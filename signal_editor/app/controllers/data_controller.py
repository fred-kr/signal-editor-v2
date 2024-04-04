import enum
import functools
import typing as t
from abc import ABC, abstractmethod
from collections import OrderedDict
from pathlib import Path

import mne.io
import polars as pl
from PySide6 import QtCore

from .. import type_defs as _t
from ..core.file_io import detect_sampling_rate, read_edf
from ..core.section import Section, SectionID


class TextFileSeparator(enum.StrEnum):
    Tab = "\t"
    Space = " "
    Comma = ","
    Semicolon = ";"
    Pipe = "|"


class MissingDataError(Exception):
    """
    Raised if any function is called that requires data to be loaded, while no data is available.
    """

    pass


class MissingSectionError(Exception):
    """
    Raised when trying to access a section (using a valid ID) that does not exist.
    """

    pass


def check_string_for_non_ascii(string: str) -> tuple[bool, list[tuple[str, int]]]:
    """
    Checks a file name for possible non-ASCII characters.

    Parameters
    ----------
    string : str
        The string to check.

    Returns
    -------
    tuple[bool, list[tuple[str, int]]
        A tuple containing a boolean indicating whether non-ASCII characters were found and a list of tuples containing the detected non-ASCII characters and their positions in the input string.
    """
    non_ascii_chars = [(char, idx) for idx, char in enumerate(string) if ord(char) > 127]
    return bool(non_ascii_chars), non_ascii_chars


class FileMetadata(ABC):
    """
    Abstract base class for file metadata objects.
    """

    def __init__(self, file_path: Path | str) -> None:
        self.file_path = Path(file_path)
        self._sampling_rate = t.cast(float, QtCore.QSettings().value("Data/sampling_rate", 0, type=float))
        self.user_input_required = False
        self.required_fields = []

    @property
    def file_name(self) -> str:
        """
        The name of the file, including its extension.
        """
        return self.file_path.name

    @property
    def file_format(self) -> str:
        """
        The format of the file.
        """
        return self.file_path.suffix

    @property
    def sampling_rate(self) -> float:
        """
        The sampling rate of the data in the file.
        """
        return self._sampling_rate

    @sampling_rate.setter
    def sampling_rate(self, sampling_rate: float) -> None:
        self._sampling_rate = sampling_rate

    @property
    @abstractmethod
    def additional_info(self) -> t.Mapping[str, t.Any]:
        """
        Any additional information about the file. This varies depending on the file format.
        """


class TextFileMetadata(FileMetadata):
    """
    Metadata information about a file containing data in a tabular text format.
    """

    _txt_separator = t.cast(str, QtCore.QSettings().value("Data/txt_file_separator_character", " "))
    _reader_funcs = {
        ".csv": functools.partial(pl.scan_csv, separator=TextFileSeparator.Comma),
        ".txt": functools.partial(pl.scan_csv, separator=_txt_separator),
        ".tsv": functools.partial(pl.scan_csv, separator=TextFileSeparator.Tab),
    }

    def __init__(self, file_path: Path | str) -> None:
        super().__init__(file_path)
        lf = self._reader_funcs[self.file_path.suffix](self.file_path)
        self._schema = lf.schema
        self._columns = lf.columns
        try:
            self._sampling_rate = detect_sampling_rate(lf)
        except Exception:
            self.user_input_required = True
            self.required_fields.append(("sampling_rate", float))
        self._signal_column: str | None = None
        self.required_fields.append(("signal_column", str))
        self._info_column: str | None = None

    @property
    def additional_info(self) -> t.OrderedDict[str, pl.DataType]:
        return self._schema

    @property
    def column_names(self) -> list[str]:
        return self._columns

    @property
    def signal_column(self) -> str:
        if self._signal_column is None:
            raise ValueError("Property not set")
        return self._signal_column

    @signal_column.setter
    def signal_column(self, value: str) -> None:
        if value not in self.column_names:
            raise ValueError(
                f"Signal column '{value}' not found in the file. Available columns: {self.column_names}"
            )
        self._signal_column = value

    @property
    def info_column(self) -> str | None:
        return self._info_column

    @info_column.setter
    def info_column(self, value: str) -> None:
        if value not in self.column_names:
            raise ValueError(
                f"Info column '{value}' not found in the file. Available columns: {self.column_names}"
            )
        self._info_column = value


class FeatherFileMetadata(FileMetadata):
    """
    Metadata information about a Feather file.
    """

    def __init__(self, file_path: Path | str) -> None:
        super().__init__(file_path)
        lf = pl.scan_ipc(self.file_path)
        self._schema = lf.schema
        self._columns = lf.columns
        try:
            self._sampling_rate = detect_sampling_rate(lf)
        except Exception:
            self.user_input_required = True
            self.required_fields.append(("sampling_rate", float))
        self._signal_column: str | None = None
        self.required_fields.append(("signal_column", str))
        self._info_column: str | None = None

    @property
    def additional_info(self) -> t.OrderedDict[str, pl.DataType]:
        return self._schema

    @property
    def column_names(self) -> list[str]:
        return self._columns

    @property
    def signal_column(self) -> str:
        if self._signal_column is None:
            raise ValueError("Property not set")
        return self._signal_column

    @signal_column.setter
    def signal_column(self, value: str) -> None:
        if value not in self.column_names:
            raise ValueError(
                f"Signal column '{value}' not found in the file. Available columns: {self.column_names}"
            )
        self._signal_column = value

    @property
    def info_column(self) -> str | None:
        return self._info_column

    @info_column.setter
    def info_column(self, value: str) -> None:
        if value not in self.column_names:
            raise ValueError(
                f"Info column '{value}' not found in the file. Available columns: {self.column_names}"
            )
        self._info_column = value


class ExcelFileMetadata(FileMetadata):
    """
    Metadata information about an Excel file.
    """

    def __init__(self, file_path: Path | str) -> None:
        super().__init__(file_path)
        self.user_input_required = True
        self._schema: t.OrderedDict[str, pl.DataType] | None = None
        self._columns: list[str] | None = None
        self.required_fields.extend([("sampling_rate", float), ("column_names", list[str])])
        self._signal_column: str | None = None
        self._info_column: str | None = None

    @property
    def additional_info(self) -> t.OrderedDict[str, pl.DataType]:
        if self._schema is None:
            raise ValueError("Property not set")
        return self._schema

    @additional_info.setter
    def additional_info(self, value: t.OrderedDict[str, pl.DataType]) -> None:
        self._schema = value

    @property
    def column_names(self) -> list[str]:
        if self._columns is None:
            raise ValueError("Property not set")
        return self._columns

    @column_names.setter
    def column_names(self, value: list[str]) -> None:
        self._columns = value

    @property
    def signal_column(self) -> str:
        if self._signal_column is None:
            raise ValueError("Property not set")
        return self._signal_column

    @signal_column.setter
    def signal_column(self, value: str) -> None:
        if value not in self.column_names:
            raise ValueError(
                f"Signal column '{value}' not found in the file. Available columns: {self.column_names}"
            )
        self._signal_column = value

    @property
    def info_column(self) -> str | None:
        return self._info_column

    @info_column.setter
    def info_column(self, value: str) -> None:
        if value not in self.column_names:
            raise ValueError(
                f"Info column '{value}' not found in the file. Available columns: {self.column_names}"
            )
        self._info_column = value


class EDFFileMetadata(FileMetadata):
    """
    Holds metadata information about an EDF file.
    """

    def __init__(self, file_path: Path | str) -> None:
        super().__init__(file_path)
        self._raw_edf = mne.io.read_raw_edf(self.file_path, preload=False)
        self._info: mne.Info = self._raw_edf.info
        self._ch_names: list[str] = self._info["ch_names"]
        self._sampling_rate: float = self._info["sfreq"]
        if not self._ch_names:
            self.user_input_required = True
            self.required_fields.append("column_names")
        if not self._sampling_rate:
            self.user_input_required = True
            self.required_fields.append("sampling_rate")
        self._signal_channel: str | None = None
        self._info_channel: str | None = None

    @property
    def additional_info(self) -> mne.Info:
        return self._info

    @property
    def column_names(self) -> list[str]:
        return self._ch_names

    @property
    def signal_column(self) -> str:
        if self._signal_channel is None:
            raise ValueError("Property not set")
        return self._signal_channel

    @signal_column.setter
    def signal_column(self, value: str) -> None:
        if value not in self._ch_names:
            raise ValueError(
                f"Channel '{value}' does not exist in the file. Available channels: {self._ch_names}"
            )
        self._signal_channel = value

    @property
    def info_column(self) -> str | None:
        return self._info_channel

    @info_column.setter
    def info_column(self, value: str) -> None:
        if value not in self._ch_names:
            raise ValueError(
                f"Channel '{value}' does not exist in the file. Available channels: {self._ch_names}"
            )
        self._info_channel = value


class SectionContainer(OrderedDict[SectionID, Section]):
    def __setitem__(self, key: SectionID, value: Section) -> None:
        super().__setitem__(key, value)
        self.move_to_end(key)

    def __getitem__(self, key: SectionID) -> Section:
        return super().__getitem__(key)


class DataController(QtCore.QObject):
    sig_non_ascii_in_file_name = QtCore.Signal(list, bool)
    sig_user_input_required = QtCore.Signal(list)
    sig_new_data_file_selected = QtCore.Signal(dict)
    sig_new_data_file_loaded = QtCore.Signal()
    sig_sampling_rate_changed = QtCore.Signal(int)
    sig_active_section_changed = QtCore.Signal(bool)
    sig_section_added = QtCore.Signal(str)
    sig_section_removed = QtCore.Signal(str)

    SUPPORTED_FILE_FORMATS = frozenset(
        [".edf", ".xlsx", ".xls", ".feather", ".csv", ".txt", ".tsv"]
    )

    def __init__(self, parent: QtCore.QObject | None = None) -> None:
        super().__init__(parent)

        settings = QtCore.QSettings()
        self._sampling_rate = t.cast(int, settings.value("Data/sampling_rate"))

        self._base_df: pl.DataFrame | None = None
        self._working_df: pl.DataFrame | None = None

        self._metadata: (
            TextFileMetadata | ExcelFileMetadata | EDFFileMetadata | FeatherFileMetadata | None
        ) = None

        self._sections: SectionContainer = SectionContainer()
        self._active_section: Section | None = None
        self._base_section: Section | None = None

    @property
    def sections(self) -> SectionContainer:
        return self._sections

    @property
    def sampling_rate(self) -> int:
        return self._sampling_rate

    def _set_sampling_rate(self, value: int) -> None:
        """
        This method is used whenever the sampling rate is changed programmatically, as opposed
        to when the user changes the value in the UI.
        """
        self._sampling_rate = value
        self.sig_sampling_rate_changed.emit(value)

    @QtCore.Slot(int)
    def on_sampling_rate_changed(self, value: int) -> None:
        for section in self._sections.values():
            section.update_sampling_rate(value)

    def get_base_section(self) -> Section:
        if self._base_df is None:
            raise MissingDataError("No data available. Select a valid file to load, and try again.")
        if self._base_section is None:
            self._base_section = Section(self._base_df)
        return self._base_section

    @property
    def active_section(self) -> Section:
        if self._active_section is None:
            # This will raise an exception if no data is available, so no need to check for it here (i think)
            self._active_section = self.get_base_section()
        return self._active_section

    @QtCore.Slot(str)
    def set_active_section(self, section_id: SectionID) -> None:
        if section_id not in self._sections:
            raise MissingSectionError(
                f"No section found for ID: '{section_id}'. Available sections: \n\n{list(self._sections.keys())}"
            )
        self._active_section = self._sections[section_id]
        has_peak_data = not self._active_section.peaks_local.is_empty()
        self.sig_active_section_changed.emit(has_peak_data)

    @property
    def editable_section_ids(self) -> list[SectionID]:
        """
        Returns the IDs of all currently available sections, excluding the base section.
        """
        return list(self._sections.keys())[1:] if len(self._sections) > 1 else []

    @property
    def metadata(
        self,
    ) -> TextFileMetadata | ExcelFileMetadata | EDFFileMetadata | FeatherFileMetadata:
        if self._metadata is None:
            raise MissingDataError("No metadata available. Load a valid file to get metadata.")
        return self._metadata

    @QtCore.Slot(str)
    def select_file(self, file_path: Path | str) -> None:
        file_path = Path(file_path)
        if not file_path.is_file():
            raise FileNotFoundError(
                f"Path: {file_path} \n\nNo file exists at the specified path. Please check the path and try again."
            )
        if file_path.suffix not in self.SUPPORTED_FILE_FORMATS:
            raise ValueError(
                f"Unsupported file format: {file_path.suffix}. Allowed formats: {', '.join(self.SUPPORTED_FILE_FORMATS)}"
            )

        match file_path.suffix:
            case ".edf":
                self._metadata = EDFFileMetadata(file_path)
            case ".xlsx" | ".xls":
                self._metadata = ExcelFileMetadata(file_path)
            case ".feather":
                self._metadata = FeatherFileMetadata(file_path)
            case ".csv" | ".txt" | ".tsv":
                self._metadata = TextFileMetadata(file_path)
            case _:
                raise ValueError(
                    f"Unsupported file format: {file_path.suffix}. Please select a valid file format."
                )

        show_non_ascii_warning = False
        non_ascii_characters: list[tuple[int, tuple[str, list[tuple[str, int]]]]] = []
        for i, col in enumerate(self.metadata.column_names):
            has_non_ascii, non_ascii_chars = check_string_for_non_ascii(col)
            if has_non_ascii:
                show_non_ascii_warning = True
                col_name = self.metadata.column_names[i]

                non_ascii_characters.append((i, (col_name, non_ascii_chars)))

        if show_non_ascii_warning:
            self.sig_non_ascii_in_file_name.emit(non_ascii_characters, self._metadata.file_format == ".edf")

        if self.metadata.user_input_required:
            self.sig_user_input_required.emit(self.metadata.required_fields)
        

    def read_file(self, **kwargs: t.Unpack[_t.ReadFileKwargs]) -> None:
        suffix = self.metadata.file_format
        file_path = self.metadata.file_path
        try_parse_dates = kwargs.get("try_parse_dates", False)
        separator = kwargs.get("separator")
        if separator is None:
            settings = QtCore.QSettings()
            separator = t.cast(
                TextFileSeparator,
                settings.value("Data/txt_file_separator_character", TextFileSeparator.Tab),
            )
        signal_col = self.metadata.signal_column
        info_col = self.metadata.info_column
        other_cols = kwargs.get("columns")
        columns = [signal_col]
        if info_col is not None:
            columns.append(info_col)
        if other_cols is not None:
            columns.extend(other_cols)

        match suffix:
            case ".csv":
                self._base_df = pl.read_csv(
                    file_path, columns=columns, try_parse_dates=try_parse_dates
                )
            case ".txt":
                self._base_df = pl.read_csv(
                    file_path, columns=columns, separator=separator, try_parse_dates=try_parse_dates
                )
            case ".tsv":
                self._base_df = pl.read_csv(
                    file_path,
                    columns=columns,
                    separator=TextFileSeparator.Tab,
                    try_parse_dates=try_parse_dates,
                )
            case ".xlsx":
                self._base_df = pl.read_excel(file_path)
            case ".feather":
                self._base_df = pl.read_ipc(
                    file_path, columns=columns, use_pyarrow=kwargs.get("use_pyarrow", False)
                )
            case ".edf":  # FIXME: This does not work
                if info_col is None:
                    info_col = "temperature"
                self._base_df = read_edf(
                    file_path, data_channel=signal_col, temperature_channel=info_col
                )
            case _:
                raise NotImplementedError(f"Cant read file type: {suffix}")

        self.sig_new_data_file_loaded.emit()
        print(self._base_df.head(10))
