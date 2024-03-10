from ..controllers.data_controller import LoadedFileMetadata
from .. import type_defs as _t
import contextlib
import datetime
import re
import typing as t
from pathlib import Path

import dateutil.parser as dt_parser
import mne.io
import polars as pl
from dataclasses import dataclass, field
from ..controllers.config_controller import ConfigController as Config

class ReadFnReturn(t.TypedDict):
    data: pl.LazyFrame
    sampling_rate: int
    animal_id: str
    measured_date: datetime.date
    oxygen_condition: str

    

def parse_file_name(
    file_name: str,
    date_format: str | None = None,
    id_format: str | None = None,
    oxygen_format: str | None = None,
) -> tuple[str, str, str]:
    """
    Parses a file name to extract the date, the ID, and the oxygen condition.

    Parameters
    ----------
    file_name : str
        The file name to parse.
    date_format : str | None, optional
        A regex pattern to match the date in the file name. If `None` (default), uses `dateutil.parser.parse` to parse the date.
    id_format : str | None, optional
        A regex pattern to match the ID in the file name. If `None` (default), uses the pattern `'(?:P[AM]|F)\\d{1,2}'`.
    oxygen_format : str | None, optional
        A regex pattern to match the oxygen condition in the file name. If `None` (default), uses the pattern `'(norm|hyp)'` (case-insensitive).

    Returns
    -------
    str
        The date as a string in ISO format (YYYY-MM-DD). If no valid date value is found in the file name, the string `unknown` is returned.
    str
        The ID parsed from the file name. If no valid ID is found, the string `unknown` is returned.
    str
        The oxygen condition parsed from the file name. If no valid oxygen condition is found, the string `unknown` is returned.

    """
    date = "unknown"
    if date_format is None:
        with contextlib.suppress(ValueError, dt_parser.ParserError):
            date = dt_parser.parse(file_name, yearfirst=True, fuzzy=True).date().isoformat()
    else:
        match = re.search(date_format, file_name)
        if match is not None:
            date = dt_parser.parse(match.group()).date().isoformat()
    animal_id = "unknown"
    if id_format is not None:
        match = re.search(id_format, file_name)
        if match is not None:
            animal_id = match.group()

    oxygen_condition = "unknown"
    if oxygen_format is not None:
        match = re.search(oxygen_format, file_name, re.IGNORECASE)
        if match is not None:
            oxygen_condition = match.group().lower()
    return date, animal_id, oxygen_condition


def infer_sampling_rate(
    lf: pl.LazyFrame, time_column: str = "auto", time_unit: t.Literal["auto", "s", "ms"] = "auto"
) -> int:
    """
    Tries to infer the sampling rate from a polars LazyFrame by looking at the first few rows.

    Parameters
    ----------
    lf : pl.LazyFrame
        The polars LazyFrame containing the data.
    time_column : str, optional
        The name of the column containing the time information. If set to `"auto"` (default), the function will try to find a column with a name containing `"time"` or the first column with a temporal data type.
    time_unit : t.Literal["auto", "s", "ms"], optional
        The unit of the time column. If set to `"auto"` (default), the function will try to infer the correct unit automatically.

    Returns
    -------
    int
        The inferred sampling rate in Hz.

    Raises
    ------
    ValueError
        If the sampling rate cannot be inferred.
    """
    if time_column == "auto":
        for col in lf.columns:
            if "time" in col or lf.select(col).dtypes[0].is_temporal():
                time_column = col
                break

    if time_unit == "auto":
        if lf.select(time_column).dtypes[0].is_float():
            time_unit = "s"
        elif lf.select(time_column).dtypes[0].is_integer():
            time_unit = "ms"
        else:
            raise ValueError("Could not infer time unit from time column.")

    lower = lf.select(time_column).first().collect().get_column(time_column)[0]
    target = 1000 if time_unit == "ms" else 1.0
    closed = "left" if lower == 0 else "both"
    return lf.filter(pl.col(time_column).is_between(lower, target, closed=closed)).collect().height


def read_edf(
    file_path: Path,
    start: int = 0,
    stop: int | None = None,
) -> tuple[pl.LazyFrame, _t.LoadedFileMetadataDict]:
    """
    Reads data from an EDF file into a polars DataFrame.

    Parameters
    ----------
    file_path : str
        Path to the EDF file.
    start : int, optional
        Index of the first sample to read, by default 0
    stop : int | None, optional
        Index of the last sample to read. Set to `None` (default) to read all samples

    Returns
    -------


    """
    raw_edf = mne.io.read_raw_edf(file_path)
    channel_names = t.cast(list[str], raw_edf.info.ch_names)
    measured_date = t.cast(datetime.datetime, raw_edf.info["meas_date"])
    sampling_rate = int(raw_edf.info["sfreq"])  # type: ignore
    _, animal_id, oxygen_condition = parse_file_name(file_path.name)

    rename_map = {
        "temp": "temperature",
        "hb": "hbr",
        "vent": "ventilation",
    }
    column_names = [
        next(
            (rename_map[key] for key in rename_map if key in name.lower()),
            f"channel_{i}",
        )
        for i, name in enumerate(channel_names)
    ]
    data, times = raw_edf.get_data(start=start, stop=stop, return_times=True)  # type: ignore
    lf = (
        pl.from_numpy(data.transpose(), schema={name: pl.Float64 for name in column_names})  # type: ignore
        .lazy()
        .with_row_index(offset=start)
        .with_columns(
            pl.Series("time_s", times, dtype=pl.Decimal),
            pl.col("temperature").round(1),
        )
        .filter((pl.col("temperature") != 0) & (pl.col("hbr") != 0) & (pl.col("ventilation") != 0))
        .select("index", "time_s", *column_names)
    )
    return lf, {"file_name": file_path.name, "file_format": file_path.suffix, "sampling_rate": sampling_rate, }


def read_feather(
    file_path: Path,
    sampling_rate: int | t.Literal["use_config"] | None = None,
    time_column: str = "auto",
    time_unit: t.Literal["auto", "s", "ms"] = "auto",
    date_format: str | None = None,
    id_format: str | None = None,
    oxygen_format: str | None = None,
) -> tuple[pl.LazyFrame, _t.LoadedFileMetadataDict]:
    """
    Reads data from a feather file into a polars DataFrame.

    Parameters
    ----------
    file_path : str | Path
        Path to the feather file.
    sampling_rate : int | None, optional
        If `None` (default), the function will try to infer the sampling rate by looking at the first few rows of the feather file. If the sampling rate cannot be inferred, a `ValueError` is raised.
    time_column : str, optional
        The name of the column containing the time information. If set to `"auto"` (default), the function will try to find a column with a name containing `"time"` or the first column with a temporal data type.
    time_unit : t.Literal["auto", "s", "ms"], optional
        The unit of the time column. If set to `"auto"` (default), the function will try to infer the correct unit automatically.
    date_format : str | None, optional
        A regex pattern to match the date in the file name. If `None` (default), uses `dateutil.parser.parse` to parse the date.
    id_format : str | None, optional
        A regex pattern to match the ID in the file name. If `None` (default), uses the pattern `'(?:P[AM]|F)\\d{1,2}'`.
    oxygen_format : str | None, optional
        A regex pattern to match the oxygen condition in the file name. If `None` (default), uses the pattern `'(norm|hyp)'` (case-insensitive).

    Returns
    -------
    ReadFnReturn
        A dictionary containing the data, the sampling rate, the animal ID, the date measured, and the oxygen condition.

    """
    lf = pl.scan_ipc(file_path)
    if sampling_rate is None:
        try:
            sampling_rate = infer_sampling_rate(lf, time_column, time_unit)
        except ValueError:
            sampling_rate = "use_config"
    if sampling_rate == "use_config":
        sampling_rate = Config().input_data.sampling_rate
        
    date, animal_id, oxygen_condition = parse_file_name(
        str(file_path), date_format, id_format, oxygen_format
    )
    metadata = {}
    for param in {sampling_rate, date, animal_id, oxygen_condition}:
        if param != 
            metadata[str(param)] = param
        
        
    return lf, {}
