import numpy as np
import numpy.typing as npt
import contextlib
import datetime
import re
import typing as t
from pathlib import Path

import dateutil.parser as dt_parser
import mne.io
import polars as pl

from .. import type_defs as _t
from ..controllers.config_controller import ConfigController as Config
from ..controllers.data_controller import LoadedFileMetadata


def parse_file_name(
    file_name: str,
    date_format: str | None = None,
    id_format: str | None = None,
    oxygen_format: str | None = None,
) -> tuple[str, str, _t.OxygenCondition]:
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
    if oxygen_condition not in {"normoxic", "hypoxic", "unknown"}:
        oxygen_condition = "unknown"

    return date, animal_id, t.cast(_t.OxygenCondition, oxygen_condition)


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


def read_edf_header(file_path: Path) -> _t.EDFHeaderDataDict:
    info = mne.io.read_raw_edf(file_path).info
    return {
        "sampling_rate": info["sfreq"],
        "n_channels": info["nchan"],
        "channel_names": info["ch_names"],
        "measured_date": info["meas_date"],
    }


def read_edf(
    file_path: Path,
    included_channels: list[str] | None = None,
    *,
    rename_channel_mapping: dict[str, str] | None = None,
    times_from_file: bool = False,
    start: int = 0,
    stop: int | None = None,
) -> tuple[pl.LazyFrame, LoadedFileMetadata]:
    """
    Reads data from an EDF file into a polars DataFrame.

    Parameters
    ----------
    file_path : Path
        Path to the EDF file.
    included_channels : list[str] | None, optional
        The names of the channels to include when reading the file. If `None` (default), all channels are loaded. Passed to `mne.io.read_raw_edf`.
    rename_channel_mapping : dict[str, str] | None, optional
        A mapping from old channel names to new channel names. If `None` (default), the original channel names are used. Passed to `mne.io.RawEDF.
    start : int, optional
        Index of the first sample to read, by default 0
    stop : int | None, optional
        Index of the first sample not to read. Set to `None` (default) to read all samples

    Returns
    -------


    """
    raw_edf = mne.io.read_raw_edf(file_path, include=included_channels)
    if rename_channel_mapping is not None:
        raw_edf.info.rename_channels(rename_channel_mapping)
    channel_names = t.cast(list[str], raw_edf.info.ch_names)
    measured_date: datetime.datetime | str = raw_edf.info.get("meas_date", "unknown")
    if isinstance(measured_date, datetime.datetime):
        measured_date = measured_date.date().isoformat()

    _, animal_id, oxygen_condition = parse_file_name(file_path.name)
    sampling_rate = float(raw_edf.info["sfreq"])

    if len(channel_names) == 1:
        signal_column = channel_names[0]
    else:
        signal_column = channel_names[-1]

    data = raw_edf.get_data(start=start, stop=stop, return_times=times_from_file)
    if times_from_file:
        data: npt.NDArray[np.float64] = data[0]
        times: npt.NDArray[np.float64] = data[1]
    else:
        times = pl.int_range(start, stop, step=1, dtype=pl.Int32)
    lf = (
        pl.from_numpy(data.transpose(), schema={name: pl.Float64 for name in channel_names})
        .lazy()
        .with_row_index(name=index_column, offset=start)
        .with_columns(
            pl.Series("", times, dtype=pl.Decimal(10, 4)).alias("time_s"),
            pl.col(name_temperature_column).round(1),
        )
        .filter(
            (pl.col(name_temperature_column) != 0)
            & (pl.col("hbr") != 0)
            & (pl.col("ventilation") != 0)
        )
        .select("index", "time_s", *column_names)
    )
    return lf, LoadedFileMetadata(
        file_name=file_path.name,
        file_format=file_path.suffix,
        name_signal_column=signal_column,
        sampling_rate=sampling_rate,
        measured_date=measured_date,
        subject_id=animal_id,
        oxygen_condition=oxygen_condition,
    )


def read_feather(
    file_path: Path,
    signal_column: str | int | t.Literal["use_config"] = "use_config",
    sampling_rate: int | t.Literal["use_config"] | None = None,
    time_column: str = "auto",
    time_unit: t.Literal["auto", "s", "ms"] = "auto",
    date_format: str | None = None,
    id_format: str | None = None,
    oxygen_format: str | None = None,
) -> tuple[pl.LazyFrame, LoadedFileMetadata]:
    """
    Reads data from a feather file into a `polars.LazyFrame` and tries to extract some metadata
    by parsing the file name.

    Parameters
    ----------
    file_path : str | Path
        Path to the feather file.
    signal_column : str | int | t.Literal["use_config"], optional
        The name or index of the column containing the signal data. If set to `"use_config"` (default), uses the name set in the "Settings > Input Data > Signal Column Name" field.
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

    """
    lf = pl.scan_ipc(file_path)
    if sampling_rate is None:
        try:
            sampling_rate = infer_sampling_rate(lf, time_column, time_unit)
        except ValueError:
            sampling_rate = "use_config"
    if sampling_rate == "use_config":
        sampling_rate = Config().input_data.sampling_rate

    date, subject_id, oxygen_condition = parse_file_name(
        str(file_path), date_format, id_format, oxygen_format
    )
    signal_column = (
        Config().input_data.signal_column if signal_column == "use_config" else signal_column
    )
    if isinstance(signal_column, int):
        signal_column = lf.columns[signal_column]

    return lf, LoadedFileMetadata(
        file_name=file_path.name,
        file_format=file_path.suffix,
        name_signal_column=signal_column,
        sampling_rate=sampling_rate,
        measured_date=date,
        subject_id=subject_id,
        oxygen_condition=oxygen_condition,
    )


def unpack_dict_to_attrs(
    data: (
        _t.ResultIdentifierDict
        | _t.SignalFilterParameters
        | _t.StandardizeParameters
        | _t.PeakDetectionParameters
        | _t.SummaryDict
        | dict[str, str | object]
        | None
    ),
    file: tb.File,
    node: tb.Node | str,
) -> None:
    """
    Unpacks a dictionary of attributes and sets them as node attributes in a PyTables file.

    Parameters
    ----------
    data : _t.ResultIdentifierDict | _t.SignalFilterParameters | _t.StandardizeParameters | _t.PeakDetectionParameters | _t.SummaryDict | None
        A dictionary containing the attributes to be set as node attributes. Can be one of the following types:
        - _t.ResultIdentifierDict: A dictionary containing result identifier attributes.
        - _t.SignalFilterParameters: A dictionary containing signal filter parameters.
        - _t.StandardizeParameters: A dictionary containing standardize parameters.
        - _t.PeakDetectionParameters: A dictionary containing peak detection parameters.
        - _t.SummaryDict: A dictionary containing summary attributes.
        - None: If data is None, the function returns without performing any action.

    file : tb.File
        The PyTables file object.

    node : tb.Node | str
        The node in the PyTables file where the attributes will be set. Can be either a PyTables Node object or a string representing the path to the node.
    """
    if data is None:
        return
    if isinstance(data, str):
        file.set_node_attr(node, "attribute_name", data)
        return
    for key, value in data.items():
        if value is None:
            value = "unknown"
        file.set_node_attr(node, key, value)


def create_group_or_table(
    parent: tb.Group | tb.File,
    name: str,
    description: str | None = None,
    title: str = "title",
    expectedrows: int = 10000,
) -> None:
    if description is not None:
        parent.create_table(
            parent,
            name=name,
            description=description,
            title=title,
            expectedrows=expectedrows,
        )
    else:
        parent.create_group(parent, name=name, title=title)


def set_attribute(
    parent: tb.File, attrname: str, attrvalue: int | float | str | bool | None
) -> None:
    parent.set_node_attr(parent, attrname=attrname, attrvalue=attrvalue)


def result_dict_to_hdf5(file_path: str | Path, data: _t.CompleteResultDict) -> None:
    file_path = Path(file_path).resolve().as_posix()

    with tb.open_file(file_path, "w", title=f"Results_{Path(file_path).stem}") as h5f:
        unpack_dict_to_attrs(data["identifier"], h5f, h5f.root)

        h5f.create_table(
            h5f.root,
            name="global_dataframe",
            description=data["global_dataframe"],
            title="Global DataFrame",
            expectedrows=data["global_dataframe"].shape[0],
        )

        h5f.create_group(h5f.root, "focused_section_results", title="Focused Section Results")
        for section_id, focused_result in data["focused_section_results"].items():
            create_group_or_table(
                "/focused_section_results",
                name=f"focused_result_{section_id}",
                description=focused_result,
                title=f"Focused Result ({section_id})",
                expectedrows=focused_result.shape[0],
            )

        h5f.create_group(h5f.root, "complete_section_results", title="Complete Section Results")
        for section_id, section_result in data["complete_section_results"].items():
            create_group_or_table(
                "/complete_section_results",
                name=f"complete_result_{section_id}",
                title=f"Complete Result ({section_id})",
            )

            create_group_or_table(
                f"/complete_section_results/complete_result_{section_id}",
                name="section_dataframe",
                description=section_result["data"],
                title=f"DataFrame ({section_id})",
                expectedrows=section_result["data"].shape[0],
            )

            create_group_or_table(
                f"/complete_section_results/complete_result_{section_id}",
                name="peaks",
                title="Peaks",
            )
            h5f.create_array(
                f"/complete_section_results/complete_result_{section_id}/peaks",
                name="peak_indices_section",
                obj=section_result["peaks_section"],
                title="Peak indices (section)",
            )
            h5f.create_array(
                f"/complete_section_results/complete_result_{section_id}/peaks",
                name="peak_indices_global",
                obj=section_result["peaks_global"],
                title="Peak indices (global)",
            )
            h5f.create_array(
                f"/complete_section_results/complete_result_{section_id}/peaks",
                name="manually_added_peak_indices",
                obj=section_result["peak_edits"]["added"],
                title="Manually added (section)",
            )
            h5f.create_array(
                f"/complete_section_results/complete_result_{section_id}/peaks",
                name="manually_removed_peak_indices",
                obj=section_result["peak_edits"]["removed"],
                title="Manually removed (section)",
            )

            create_group_or_table(
                f"/complete_section_results/complete_result_{section_id}",
                name="rate",
                title="Calculated rate",
            )
            h5f.create_array(
                f"/complete_section_results/complete_result_{section_id}/rate",
                name="not_interpolated",
                obj=section_result["rate"],
                title="Rate (no interpolation)",
            )
            h5f.create_array(
                f"/complete_section_results/complete_result_{section_id}/rate",
                name="interpolated",
                obj=section_result["rate_interpolated"],
                title="Rate (interpolated to length of section)",
            )

            create_group_or_table(
                f"/complete_section_results/complete_result_{section_id}",
                name="processing_parameters",
                title=f"Processing parameters ({section_id})",
            )
            set_attribute(
                f"/complete_section_results/complete_result_{section_id}/processing_parameters",
                attrname="sampling_rate",
                attrvalue=section_result["processing_parameters"]["sampling_rate"],
            )
            set_attribute(
                f"/complete_section_results/complete_result_{section_id}/processing_parameters",
                attrname="pipeline",
                attrvalue=section_result["processing_parameters"]["pipeline"],
            )

            create_group_or_table(
                f"/complete_section_results/complete_result_{section_id}/processing_parameters",
                name="filter_parameters",
                title="Filter parameters",
            )
            unpack_dict_to_attrs(
                section_result["processing_parameters"]["filter_parameters"],
                h5f,
                f"/complete_section_results/complete_result_{section_id}/processing_parameters/filter_parameters",
            )

            create_group_or_table(
                f"/complete_section_results/complete_result_{section_id}/processing_parameters",
                name="standardize_parameters",
                title="Standardize parameters",
            )
            unpack_dict_to_attrs(
                section_result["processing_parameters"]["standardize_parameters"],
                h5f,
                f"/complete_section_results/complete_result_{section_id}/processing_parameters/standardize_parameters",
            )

            create_group_or_table(
                f"/complete_section_results/complete_result_{section_id}/processing_parameters",
                name="peak_detection_parameters",
                title="Peak detection parameters",
            )
            _peak_params = section_result["processing_parameters"]["peak_detection_parameters"]
            if _peak_params is not None:
                _method = _peak_params["method"]
                _method_params = _peak_params["method_parameters"]
                flattened_peak_detection_parameters = {"method": _method, **_method_params}
                unpack_dict_to_attrs(
                    flattened_peak_detection_parameters,
                    h5f,
                    f"/complete_section_results/complete_result_{section_id}/processing_parameters/peak_detection_parameters",
                )
