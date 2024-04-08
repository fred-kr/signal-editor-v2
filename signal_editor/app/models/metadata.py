import functools
import typing as t
from abc import ABC, abstractmethod
from pathlib import Path

import mne.io
import polars as pl
from PySide6 import QtCore

from ..core.file_io import detect_sampling_rate
from ..enum_defs import FileFormat, TextFileSeparator


class FileMetadata(ABC):
    """
    Abstract base class for file metadata objects.
    """

    def __init__(self, file_path: Path | str, default_sampling_rate: int = 0) -> None:
        self.file_path = Path(file_path)
        self._sampling_rate = default_sampling_rate
        self.required_fields = []

    @property
    def file_name(self) -> str:
        """
        The name of the file, including the file extension.
        """
        return self.file_path.name

    @property
    def file_format(self) -> FileFormat:
        """
        The format of the file.
        """
        return FileFormat(self.file_path.suffix)

    @property
    def sampling_rate(self) -> int:
        """
        The sampling rate in Hz (i.e. the number of samples per second).
        """
        return int(self._sampling_rate)

    @sampling_rate.setter
    def sampling_rate(self, sampling_rate: int | float) -> None:  # TODO: remove the float type
        if "sampling_rate" in self.required_fields:
            self.required_fields.remove("sampling_rate")
        self._sampling_rate = int(sampling_rate)

    @property
    @abstractmethod
    def additional_info(self) -> t.Mapping[str, t.Any]:
        """
        Any additional information about the file. This varies depending on the file format.
        """

    @abstractmethod
    def to_dict(self) -> dict[str, t.Any]:
        """Convert the metadata object to a dictionary."""


class TextFileMetadata(FileMetadata):
    """
    Metadata information about a file containing data in a tabular text format.
    """

    def __init__(self, file_path: Path | str) -> None:
        super().__init__(file_path)
        try:
            self._txt_separator = TextFileSeparator(
                QtCore.QSettings().value("Data/txt_file_separator_character", TextFileSeparator.Tab)
            ).value
        except Exception:
            self._txt_separator = TextFileSeparator.Tab
        self._reader_funcs = {
            ".csv": functools.partial(pl.scan_csv, separator=TextFileSeparator.Comma),
            ".txt": functools.partial(pl.scan_csv, separator=self._txt_separator),
            ".tsv": functools.partial(pl.scan_csv, separator=TextFileSeparator.Tab),
        }
        lf = self._reader_funcs[self.file_path.suffix](self.file_path)
        self._schema = lf.schema
        self._columns = lf.columns
        settings = QtCore.QSettings()
        try:
            self._sampling_rate = detect_sampling_rate(lf)
        except Exception:
            self._sampling_rate = int(settings.value("Data/sampling_rate", 0))
            if self._sampling_rate == 0:
                self.required_fields.append("sampling_rate")
        self._signal_column: str | None = None
        last_signal_col = settings.value("Misc/last_signal_column_name", None)
        if last_signal_col in self._columns:
            self._signal_column = last_signal_col
        else:
            self.required_fields.append("signal_column")
        self._info_column: str | None = None
        last_info_col = settings.value("Misc/last_info_column_name", None)
        if last_info_col in self._columns:
            self._info_column = last_info_col

    @property
    def additional_info(self) -> t.OrderedDict[str, pl.DataType]:
        return self._schema

    @property
    def column_names(self) -> list[str]:
        return self._columns

    @property
    def signal_column(self) -> str:
        if self._signal_column is None:
            raise ValueError("Signal column has not been set.")
        return self._signal_column

    @signal_column.setter
    def signal_column(self, value: str) -> None:
        if "signal_column" in self.required_fields:
            self.required_fields.remove("signal_column")
        self._signal_column = value

    @property
    def info_column(self) -> str | None:
        return self._info_column

    @info_column.setter
    def info_column(self, value: str) -> None:
        self._info_column = value or None

    def to_dict(self) -> dict[str, t.Any]:
        return {
            "file_path": str(self.file_path),
            "sampling_rate": self.sampling_rate,
            "signal_column": self._signal_column,
            "info_column": self.info_column,
            "column_names": self.column_names,
            "additional_info": self.additional_info,
        }


class FeatherFileMetadata(FileMetadata):
    """
    Metadata information about a Feather file.
    """

    def __init__(self, file_path: Path | str) -> None:
        super().__init__(file_path)
        lf = pl.scan_ipc(self.file_path)
        self._schema = lf.schema
        self._columns = lf.columns
        settings = QtCore.QSettings()
        try:
            self._sampling_rate = detect_sampling_rate(lf)
        except Exception:
            self._sampling_rate = int(settings.value("Data/sampling_rate", 0))
            if self._sampling_rate == 0:
                self.required_fields.append("sampling_rate")

        self._signal_column: str | None = None
        last_signal_col = settings.value("Misc/last_signal_column_name", None)
        if last_signal_col in self._columns:
            self._signal_column = last_signal_col
        else:
            self.required_fields.append("signal_column")
        self._info_column: str | None = None
        last_info_col = settings.value("Misc/last_info_column_name", None)
        if last_info_col in self._columns:
            self._info_column = last_info_col

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
        if "signal_column" in self.required_fields:
            self.required_fields.remove("signal_column")
        self._signal_column = value

    @property
    def info_column(self) -> str | None:
        return self._info_column

    @info_column.setter
    def info_column(self, value: str) -> None:
        self._info_column = value or None

    def to_dict(self) -> dict[str, t.Any]:
        return {
            "file_path": str(self.file_path),
            "sampling_rate": self.sampling_rate,
            "signal_column": self._signal_column,
            "info_column": self.info_column,
            "column_names": self.column_names,
            "additional_info": self.additional_info,
        }


class ExcelFileMetadata(FileMetadata):
    """
    Metadata information about an Excel file.
    """

    def __init__(self, file_path: Path | str) -> None:
        super().__init__(file_path)
        self._schema: t.OrderedDict[str, pl.DataType] | None = None
        self._columns: list[str] = []
        self.required_fields.extend(["sampling_rate", "column_names", "signal_column"])
        self._signal_column: str | None = None
        self._info_column: str | None = None

    @property
    def additional_info(self) -> t.OrderedDict[str, pl.DataType]:
        return t.OrderedDict() if self._schema is None else self._schema

    @additional_info.setter
    def additional_info(self, value: t.OrderedDict[str, pl.DataType]) -> None:
        self._schema = value

    @property
    def column_names(self) -> list[str]:
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
        if "signal_column" in self.required_fields:
            self.required_fields.remove("signal_column")
        self._signal_column = value

    @property
    def info_column(self) -> str | None:
        return self._info_column

    @info_column.setter
    def info_column(self, value: str) -> None:
        self._info_column = value or None

    def to_dict(self) -> dict[str, t.Any]:
        return {
            "file_path": str(self.file_path),
            "sampling_rate": self.sampling_rate,
            "signal_column": self._signal_column,
            "info_column": self.info_column,
            "column_names": self.column_names,
            "additional_info": self._schema,
        }


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
        settings = QtCore.QSettings()
        if not self._sampling_rate:
            self._sampling_rate = int(settings.value("Misc/last_sampling_rate", 0))
            if self._sampling_rate == 0:
                self.required_fields.append("sampling_rate")
        self._signal_column: str | None = None
        last_signal_col: str | None = settings.value("Misc/last_signal_column_name", None)
        if last_signal_col in self._ch_names:
            self._signal_column = last_signal_col
        else:
            self.required_fields.append("signal_column")
        self._info_column: str | None = None
        last_info_col: str | None = settings.value("Misc/last_info_column_name", None)
        if last_info_col in self._ch_names:
            self._info_column = last_info_col

    @property
    def additional_info(self) -> mne.Info:
        return self._info

    @property
    def column_names(self) -> list[str]:
        return self._ch_names

    @property
    def signal_column(self) -> str:
        if self._signal_column is None:
            raise ValueError("Property not set")
        return self._signal_column

    @signal_column.setter
    def signal_column(self, value: str) -> None:
        if "signal_column" in self.required_fields:
            self.required_fields.remove("signal_column")
        self._signal_column = value

    @property
    def info_column(self) -> str | None:
        return self._info_column

    @info_column.setter
    def info_column(self, value: str) -> None:
        self._info_column = value or None

    def to_dict(self) -> dict[str, t.Any]:
        return {
            "file_path": str(self.file_path),
            "sampling_rate": self.sampling_rate,
            "signal_column": self._signal_column,
            "info_column": self.info_column,
            "column_names": self.column_names,
            "additional_info": self.additional_info,
        }
