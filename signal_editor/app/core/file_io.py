import contextlib
import datetime
import re
import typing as t
from pathlib import Path

import dateutil.parser as dt_parser
import mne.io
import polars as pl
import polars.selectors as cs

from .. import type_defs as _t
from ..controllers.config_controller import ConfigController as Config


def parse_file_name(
    file_name: str,
    date_format: str | None = None,
    id_format: str | None = None,
    oxygen_format: str | None = None,
) -> tuple[datetime.datetime, str, _t.OxygenCondition]:
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
    datetime.datetime
        The datetime retrieved via dateutil.parser.parse or the provided regex pattern. If no valid date is found, the datetime at the Unix epoch ('1970-01-01 00:00:00') is returned.
    str
        The ID parsed from the file name. If no valid ID is found, the string `unknown` is returned.
    str
        The oxygen condition parsed from the file name. If no valid oxygen condition is found, the string `unknown` is returned.

    """
    date = datetime.datetime.fromtimestamp(0)
    if date_format is None:
        with contextlib.suppress(ValueError, dt_parser.ParserError):
            date = dt_parser.parse(file_name, yearfirst=True, fuzzy=True)
    else:
        match = re.search(date_format, file_name)
        if match is not None:
            date = dt_parser.parse(match.group())
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


class MultipleValidTimeColumnsDetectedError(Exception):
    """
    Raised when the function `infer_sampling_rate` finds multiple possible time columns in the given `polars.LazyFrame`.
    """

    def __init__(self, columns: t.Sequence[str]) -> None:
        self.columns = columns

    def __str__(self) -> str:
        return f"Detected multiple columns that could be interpreted as time data: [{', '.join([f'\'{col}\'' for col in self.columns])}]. Please specify the time column manually."


class NoValidTimeColumnDetectedError(Exception):
    """
    Raised when the function `infer_sampling_rate` cannot find a suitable time column in the given `polars.LazyFrame`.
    """


class NoValidTimeUnitDetectedError(Exception):
    """
    Raised when the function `infer_sampling_rate` cannot infer the correct time unit from the time column.
    """


class TimeUnitDataTypeMismatchError(Exception):
    """
    Raised when the time column has a data type that does not match the inferred time unit.
    """

    def __init__(self, time_unit: str, time_col_dtype: pl.DataType) -> None:
        self.time_unit = time_unit
        self.time_col_dtype = time_col_dtype

    def __str__(self) -> str:
        return f"Time unit '{self.time_unit}' does not match the data type of the time column: '{self.time_col_dtype}'."


def _infer_time_column(lf: pl.LazyFrame, contains: t.Sequence[str] | None = None) -> list[str]:
    if contains is None:
        contains = ["time", "ts"]
    return lf.select(
        cs.contains(contains)
        | cs.datetime()
        | cs.duration()
        | (cs.integer() & ~cs.contains("index"))
    ).columns


def _infer_time_unit(
    time_col_dtype: pl.DataType, interpret_integers_as: t.Literal["ms", "us", "ns"]
) -> t.Literal["s", "ms", "us", "ns", "datetime"]:
    if time_col_dtype.is_float():
        return "s"
    if time_col_dtype.is_integer():
        return interpret_integers_as
    if time_col_dtype.base_type().is_(pl.Datetime):
        return "datetime"
    if time_col_dtype.is_(pl.Duration("ns")):
        return "ns"
    if time_col_dtype.is_(pl.Duration("ms")):
        return "ms"
    if time_col_dtype.is_(pl.Duration("us")):
        return "us"
    raise NoValidTimeUnitDetectedError(
        f"Could not infer valid time unit from time column with dtype: '{time_col_dtype}'."
    )


def _get_target_for_time_unit(
    time_unit: t.Literal["s", "ms", "us", "ns", "datetime"],
    time_col_dtype: pl.DataType,
    start_val: datetime.datetime | None = None,
) -> int | float | datetime.datetime:
    if time_unit == "s" and time_col_dtype.is_float():
        return 1.0
    if time_unit == "ms" and time_col_dtype in (pl.INTEGER_DTYPES | {pl.Duration("ms")}):
        return 1_000
    if time_unit == "us" and time_col_dtype in (pl.INTEGER_DTYPES | {pl.Duration("us")}):
        return 1_000_000
    if time_unit == "ns" and time_col_dtype in (pl.INTEGER_DTYPES | {pl.Duration("ns")}):
        return 1_000_000_000
    if (
        time_unit == "datetime"
        and time_col_dtype.base_type().is_(pl.Datetime)
        and start_val is not None
    ):
        return start_val + datetime.timedelta(seconds=1)
    raise TimeUnitDataTypeMismatchError(time_unit, time_col_dtype)


def detect_sampling_rate(
    lf: pl.LazyFrame,
    time_column: str | int = "auto",
    time_unit: t.Literal["auto", "s", "ms", "us", "ns", "datetime"] = "auto",
    interpret_integers_as: t.Literal["ms", "us", "ns"] = "us",
    first_column_is_time: bool = False,
) -> int:
    """
    Tries to detect the sampling rate value from a `polars.LazyFrame` containing physiological signal data.

    Parameters
    ----------
    lf : pl.LazyFrame
        The polars LazyFrame containing the data.
    time_column : str | int, optional
        The name or index of the column containing the time information. If set to `"auto"`
        (default), an attempt is made to find a suitable time column automatically. If this fails,
        a `NoValidTimeColumnDetectedError` is raised. See ``Notes`` for more information.
    time_unit : t.Literal["auto", "s", "ms", "us", "ns", "datetime"], optional
        The unit of the time column. If set to `"auto"` (default), the function will try to infer
        the correct unit automatically. Float columns are interpreted as seconds with decimal places.
    interpret_integers_as : t.Literal["ms", "us", "ns"], optional
        The unit to interpret integer values as. Default is microseconds (`"us"`).

    Returns
    -------
    int
        The sampling rate. Calculated as the number of rows in the first second of the data.

    Notes
    -----
    Possible columns when `time_column` is set to `"auto"`:
    - Columns with a name containing the substring `"time"` or `"ts"`.
    - Columns containing datetime or duration data.
    - Integer columns excluding those whose name contains the substring `"index"`.

    Raises
    ------
    NoValidTimeColumnDetectedError
        If no valid time column is found in the given `polars.LazyFrame`.
    MultipleValidTimeColumnsDetectedError
        If the function finds multiple possible time columns in the given `polars.LazyFrame`.
    NoValidTimeUnitDetectedError
        If the function cannot infer the correct time unit from the time column.
    TimeUnitDataTypeMismatchError
        If the time column has a data type that does not match the inferred time unit.
    """
    if isinstance(time_column, int):
        try:
            time_column = lf.columns[time_column]
        except IndexError:
            time_column = "auto"

    if time_column == "auto":
        possible_columns = _infer_time_column(lf)
        if not possible_columns:
            raise NoValidTimeColumnDetectedError(
                "Could not find a column containing time information."
            )
        if len(possible_columns) == 1 or first_column_is_time:
            time_column = possible_columns[0]
        else:
            raise MultipleValidTimeColumnsDetectedError(possible_columns)

    time_col_dtype = lf.schema[time_column]

    if time_unit == "auto":
        time_unit = _infer_time_unit(time_col_dtype, interpret_integers_as)

    start_val = lf.select(time_column).first().collect().item(0, time_column)

    target = _get_target_for_time_unit(time_unit, time_col_dtype, start_val)

    closed = "left" if start_val == 0 or time_unit in {"ms", "us", "ns", "datetime"} else "both"
    return lf.filter(pl.col(time_column).is_between(start_val, target, closed)).collect().height


# def read_edf_info(file_path: Path) -> _t.EDFInfoDict:
#     info = mne.io.read_raw_edf(file_path).info
#     return {
#         "sampling_rate": info["sfreq"],
#         "n_channels": info["nchan"],
#         "channel_names": info["ch_names"],
#         "measured_date": info["meas_date"],
#     }


def read_edf(
    file_path: Path,
    data_channel: str,
    temperature_channel: str,
    *,
    rename_channel_mapping: dict[str, str] | None = None,
    include_duration_column: bool = True,
    start: int = 0,
    stop: int | None = None,
) -> pl.DataFrame:
    """
    Reads data from an EDF file into a polars DataFrame.

    Parameters
    ----------
    file_path : Path
        Path to the EDF file.
    data_channel : str
        Name of the channel containing the signal data.
    temperature_channel : str
        The name of the channel containing the temperature data.
    rename_channel_mapping : dict[str, str] | None, optional
        A mapping from old channel names to new channel names. If `None` (default), the original channel names are used. Passed to `mne.io.RawEDF.
    start : int, optional
        Index of the first sample to read, by default 0
    stop : int | None, optional
        Index of the first sample not to read. Set to `None` (default) to read all samples

    Returns
    -------
    pl.DataFrame
        A polars DataFrame with the schema `{"index": pl.UInt32, "time": pl.Duration, "<name_temperature_channel>": pl.Float32, "<name_data_channel>": pl.Float64}`.

    """
    raw_edf = mne.io.read_raw_edf(file_path, include=[data_channel, temperature_channel])
    if rename_channel_mapping is None:
        rename_channel_mapping = {}
        for channel in t.cast(list[str], raw_edf.ch_names):
            if "hb" in channel.lower():
                rename_channel_mapping[channel] = "heartbeat"
                data_channel = "heartbeat"
            elif "vent" in channel.lower():
                rename_channel_mapping[channel] = "ventilation"
                data_channel = "ventilation"
            elif "temp" in channel.lower():
                rename_channel_mapping[channel] = "temperature"
                temperature_channel = "temperature"

        raw_edf.rename_channels(rename_channel_mapping)
    channel_names = t.cast(list[str], raw_edf.ch_names)
    measured_date = t.cast(datetime.datetime, raw_edf.info["meas_date"])

    sampling_rate = t.cast(float, raw_edf.info["sfreq"])

    out = pl.from_numpy(raw_edf.get_data(start=start, stop=stop), schema=channel_names).select(
        pl.col(temperature_channel).cast(pl.Float32).round(1),
        pl.col(data_channel),
    )
    if include_duration_column:
        t_end = measured_date + datetime.timedelta(seconds=raw_edf.n_times / sampling_rate)
        t_interval = datetime.timedelta(seconds=1 / sampling_rate)
        times = (
            pl.datetime_range(measured_date, t_end, interval=t_interval, closed="left", eager=True)
            - measured_date
        ).alias("time")
        out.insert_column(0, times)

    return out.filter(
        (pl.col(data_channel) != 0) & (pl.col(temperature_channel) != 0)
    ).with_row_index(offset=start)


def read_feather(
    file_path: Path,
    signal_column: str | int | t.Literal["use_config"] = "use_config",
    temperature_column: str | int = "temperature",
) -> pl.DataFrame:
    """
    Reads data from a feather file into a `polars.LazyFrame` and tries to extract some metadata
    by parsing the file name.

    Parameters
    ----------
    file_path : str | Path
        Path to the feather file.
    signal_column : str | int | t.Literal["use_config"], optional
        The name or index of the column containing the signal data. If set to `"use_config"` (default), uses the name set in the "Settings > Input Data > Signal Column Name" field.
    temperature_column : str | int, optional

    Returns
    -------

    """

    signal_column = (
        Config.instance().session.signal_column_name
        if signal_column == "use_config"
        else signal_column
    )
    col_names = pl.scan_ipc(file_path).columns
    if isinstance(signal_column, int):
        signal_column = col_names[signal_column]
    if isinstance(temperature_column, int):
        temperature_column = col_names[temperature_column]

    df = pl.read_ipc(
        file_path,
        use_pyarrow=True,
        columns=[temperature_column, signal_column],
        row_index_name="index",
    )

    if "hb" in signal_column.lower():
        new_signal_column = "heartbeat"
    elif "vent" in signal_column.lower():
        new_signal_column = "ventilation"
    else:
        new_signal_column = signal_column

    if "temp" in temperature_column.lower():
        new_temperature_column = "temperature"
    else:
        new_temperature_column = temperature_column

    return df.rename(
        {signal_column: new_signal_column, temperature_column: new_temperature_column}
    ).with_columns(pl.col(new_temperature_column).round(1))


# def unpack_dict_to_attrs(
#     data: (
#         _t.ResultIdentifierDict
#         | _t.SignalFilterParameters
#         | _t.StandardizeParameters
#         | _t.PeakDetectionParameters
#         | _t.SummaryDict
#         | dict[str, str | object]
#         | None
#     ),
#     file: tb.File,
#     node: tb.Node | str,
# ) -> None:
#     """
#     Unpacks a dictionary of attributes and sets them as node attributes in a PyTables file.

#     Parameters
#     ----------
#     data : _t.ResultIdentifierDict | _t.SignalFilterParameters | _t.StandardizeParameters | _t.PeakDetectionParameters | _t.SummaryDict | None
#         A dictionary containing the attributes to be set as node attributes. Can be one of the following types:
#         - _t.ResultIdentifierDict: A dictionary containing result identifier attributes.
#         - _t.SignalFilterParameters: A dictionary containing signal filter parameters.
#         - _t.StandardizeParameters: A dictionary containing standardize parameters.
#         - _t.PeakDetectionParameters: A dictionary containing peak detection parameters.
#         - _t.SummaryDict: A dictionary containing summary attributes.
#         - None: If data is None, the function returns without performing any action.

#     file : tb.File
#         The PyTables file object.

#     node : tb.Node | str
#         The node in the PyTables file where the attributes will be set. Can be either a PyTables Node object or a string representing the path to the node.
#     """
#     if data is None:
#         return
#     if isinstance(data, str):
#         file.set_node_attr(node, "attribute_name", data)
#         return
#     for key, value in data.items():
#         if value is None:
#             value = "unknown"
#         file.set_node_attr(node, key, value)


# def create_group_or_table(
#     parent: tb.Group | tb.File,
#     name: str,
#     description: str | None = None,
#     title: str = "title",
#     expectedrows: int = 10000,
# ) -> None:
#     if description is not None:
#         parent.create_table(
#             parent,
#             name=name,
#             description=description,
#             title=title,
#             expectedrows=expectedrows,
#         )
#     else:
#         parent.create_group(parent, name=name, title=title)


# def set_attribute(
#     parent: tb.File, attrname: str, attrvalue: int | float | str | bool | None
# ) -> None:
#     parent.set_node_attr(parent, attrname=attrname, attrvalue=attrvalue)


# def result_dict_to_hdf5(file_path: str | Path, data: _t.CompleteResultDict) -> None:
#     file_path = Path(file_path).resolve().as_posix()

#     with tb.open_file(file_path, "w", title=f"Results_{Path(file_path).stem}") as h5f:
#         unpack_dict_to_attrs(data["identifier"], h5f, h5f.root)

#         h5f.create_table(
#             h5f.root,
#             name="global_dataframe",
#             description=data["global_dataframe"],
#             title="Global DataFrame",
#             expectedrows=data["global_dataframe"].shape[0],
#         )

#         h5f.create_group(h5f.root, "focused_section_results", title="Focused Section Results")
#         for section_id, focused_result in data["focused_section_results"].items():
#             create_group_or_table(
#                 "/focused_section_results",
#                 name=f"focused_result_{section_id}",
#                 description=focused_result,
#                 title=f"Focused Result ({section_id})",
#                 expectedrows=focused_result.shape[0],
#             )

#         h5f.create_group(h5f.root, "complete_section_results", title="Complete Section Results")
#         for section_id, section_result in data["complete_section_results"].items():
#             create_group_or_table(
#                 "/complete_section_results",
#                 name=f"complete_result_{section_id}",
#                 title=f"Complete Result ({section_id})",
#             )

#             create_group_or_table(
#                 f"/complete_section_results/complete_result_{section_id}",
#                 name="section_dataframe",
#                 description=section_result["data"],
#                 title=f"DataFrame ({section_id})",
#                 expectedrows=section_result["data"].shape[0],
#             )

#             create_group_or_table(
#                 f"/complete_section_results/complete_result_{section_id}",
#                 name="peaks",
#                 title="Peaks",
#             )
#             h5f.create_array(
#                 f"/complete_section_results/complete_result_{section_id}/peaks",
#                 name="peak_indices_section",
#                 obj=section_result["peaks_section"],
#                 title="Peak indices (section)",
#             )
#             h5f.create_array(
#                 f"/complete_section_results/complete_result_{section_id}/peaks",
#                 name="peak_indices_global",
#                 obj=section_result["peaks_global"],
#                 title="Peak indices (global)",
#             )
#             h5f.create_array(
#                 f"/complete_section_results/complete_result_{section_id}/peaks",
#                 name="manually_added_peak_indices",
#                 obj=section_result["peak_edits"]["added"],
#                 title="Manually added (section)",
#             )
#             h5f.create_array(
#                 f"/complete_section_results/complete_result_{section_id}/peaks",
#                 name="manually_removed_peak_indices",
#                 obj=section_result["peak_edits"]["removed"],
#                 title="Manually removed (section)",
#             )

#             create_group_or_table(
#                 f"/complete_section_results/complete_result_{section_id}",
#                 name="rate",
#                 title="Calculated rate",
#             )
#             h5f.create_array(
#                 f"/complete_section_results/complete_result_{section_id}/rate",
#                 name="not_interpolated",
#                 obj=section_result["rate"],
#                 title="Rate (no interpolation)",
#             )
#             h5f.create_array(
#                 f"/complete_section_results/complete_result_{section_id}/rate",
#                 name="interpolated",
#                 obj=section_result["rate_interpolated"],
#                 title="Rate (interpolated to length of section)",
#             )

#             create_group_or_table(
#                 f"/complete_section_results/complete_result_{section_id}",
#                 name="processing_parameters",
#                 title=f"Processing parameters ({section_id})",
#             )
#             set_attribute(
#                 f"/complete_section_results/complete_result_{section_id}/processing_parameters",
#                 attrname="sampling_rate",
#                 attrvalue=section_result["processing_parameters"]["sampling_rate"],
#             )
#             set_attribute(
#                 f"/complete_section_results/complete_result_{section_id}/processing_parameters",
#                 attrname="pipeline",
#                 attrvalue=section_result["processing_parameters"]["pipeline"],
#             )

#             create_group_or_table(
#                 f"/complete_section_results/complete_result_{section_id}/processing_parameters",
#                 name="filter_parameters",
#                 title="Filter parameters",
#             )
#             unpack_dict_to_attrs(
#                 section_result["processing_parameters"]["filter_parameters"],
#                 h5f,
#                 f"/complete_section_results/complete_result_{section_id}/processing_parameters/filter_parameters",
#             )

#             create_group_or_table(
#                 f"/complete_section_results/complete_result_{section_id}/processing_parameters",
#                 name="standardize_parameters",
#                 title="Standardize parameters",
#             )
#             unpack_dict_to_attrs(
#                 section_result["processing_parameters"]["standardize_parameters"],
#                 h5f,
#                 f"/complete_section_results/complete_result_{section_id}/processing_parameters/standardize_parameters",
#             )

#             create_group_or_table(
#                 f"/complete_section_results/complete_result_{section_id}/processing_parameters",
#                 name="peak_detection_parameters",
#                 title="Peak detection parameters",
#             )
#             _peak_params = section_result["processing_parameters"]["peak_detection_parameters"]
#             if _peak_params is not None:
#                 _method = _peak_params["method"]
#                 _method_params = _peak_params["method_parameters"]
#                 flattened_peak_detection_parameters = {"method": _method, **_method_params}
#                 unpack_dict_to_attrs(
#                     flattened_peak_detection_parameters,
#                     h5f,
#                     f"/complete_section_results/complete_result_{section_id}/processing_parameters/peak_detection_parameters",
#                 )
