import typing as t
from pathlib import Path

from PySide6 import QtCore

from .. import _type_defs as _t
from .._app_config import Config
from .._constants import COMBO_BOX_NO_SELECTION, RESERVED_COLUMN_NAMES
from .._enums import InputFileFormat


class FileMetadata:
    __slots__ = (
        "required_fields",
        "file_info",
        "_sampling_rate",
        "_columns",
        "_signal_column",
        "_info_column",
        "other_info",
    )

    def __init__(self, file_path: Path | str, columns: list[str], sampling_rate: int) -> None:
        self.required_fields: list[str] = []
        self.file_info = QtCore.QFileInfo(file_path)
        self._sampling_rate = sampling_rate
        if self._sampling_rate == 0:
            self.required_fields.append("sampling_rate")

        self._columns = columns
        signal_col = Config.internal.last_signal_column
        if signal_col not in self._columns or signal_col in RESERVED_COLUMN_NAMES:
            self.required_fields.append("signal_column")
            signal_col = self._columns[0]
        self._signal_column = signal_col

        info_col = Config.internal.last_info_column
        if info_col not in self._columns:
            info_col = COMBO_BOX_NO_SELECTION
        self._info_column = info_col

        self.other_info: dict[str, t.Any] = {}

    @property
    def file_name(self) -> str:
        return self.file_info.fileName()

    @property
    def file_path(self) -> str:
        return self.file_info.canonicalFilePath()

    @property
    def file_format(self) -> InputFileFormat:
        return InputFileFormat(f".{self.file_info.suffix()}")

    @property
    def column_names(self) -> list[str]:
        return [COMBO_BOX_NO_SELECTION] + self._columns

    @column_names.setter
    def column_names(self, value: list[str]) -> None:
        self._columns = value

    @property
    def valid_columns(self) -> list[str]:
        return self._columns

    @property
    def sampling_rate(self) -> int:
        return self._sampling_rate

    @sampling_rate.setter
    def sampling_rate(self, value: int) -> None:
        if "sampling_rate" in self.required_fields and value > 0:
            self.required_fields.remove("sampling_rate")
        elif value == 0 and "sampling_rate" not in self.required_fields:
            self.required_fields.append("sampling_rate")
        self._sampling_rate = value

    @property
    def signal_column(self) -> str:
        return self._signal_column

    @signal_column.setter
    def signal_column(self, value: str) -> None:
        if value in RESERVED_COLUMN_NAMES:
            self.required_fields.append("signal_column")
        elif "signal_column" in self.required_fields:
            self.required_fields.remove("signal_column")
        self._signal_column = value

    @property
    def info_column(self) -> str:
        return self._info_column

    @info_column.setter
    def info_column(self, value: str | None) -> None:
        if value is None:
            value = COMBO_BOX_NO_SELECTION
        self._info_column = value

    def to_dict(self) -> _t.MetadataDict:
        return {
            "file_path": self.file_path,
            "sampling_rate": self.sampling_rate,
            "signal_column": self.signal_column,
            "info_column": self.info_column,
            "column_names": self.column_names,
        }
