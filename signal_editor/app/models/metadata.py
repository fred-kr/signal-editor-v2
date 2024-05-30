import typing as t
from pathlib import Path

from loguru import logger
from PySide6 import QtCore

from ..enum_defs import FileFormat


class FileMetadata(QtCore.QObject):
    def __init__(self, file_path: Path | str, parent: QtCore.QObject | None = None) -> None:
        super().__init__(parent)
        self.required_fields = []
        self.file_info = QtCore.QFileInfo(file_path)
        settings = QtCore.QSettings()
        self._sampling_rate: int = settings.value("Data/sampling_rate", 0, int)  # type: ignore
        if self._sampling_rate == 0:
            self.required_fields.append("sampling_rate")

        self.columns = QtCore.QStringListModel(self)
        self._signal_column: str | None = None
        self.required_fields.append("signal_column")
        self._info_column: str = ""

    @property
    def file_name(self) -> str:
        return self.file_info.fileName()

    @property
    def file_path(self) -> str:
        return self.file_info.canonicalFilePath()

    @property
    def file_format(self) -> FileFormat:
        return FileFormat(f".{self.file_info.suffix()}")

    @property
    def column_names(self) -> list[str]:
        return self.columns.stringList()

    @column_names.setter
    def column_names(self, value: list[str]) -> None:
        if value[0] != "":
            value.insert(0, "")
        self.columns.setStringList(value)

    @property
    def sampling_rate(self) -> int:
        return self._sampling_rate

    @sampling_rate.setter
    def sampling_rate(self, value: int) -> None:
        if "sampling_rate" in self.required_fields and value > 0:
            self.required_fields.remove("sampling_rate")
        elif value == 0 and "sampling_rate" not in self.required_fields:
            self.required_fields.append("sampling_rate")
        settings = QtCore.QSettings()
        settings.setValue("Data/sampling_rate", value)
        self._sampling_rate = value

    @property
    def signal_column(self) -> str:
        if self._signal_column is None:
            logger.error("No signal column set.")
            raise ValueError("Property not set")
        return self._signal_column

    @signal_column.setter
    def signal_column(self, value: str) -> None:
        if "signal_column" in self.required_fields:
            self.required_fields.remove("signal_column")

        settings = QtCore.QSettings()
        settings.setValue("Misc/last_signal_column_name", value)
        self._signal_column = value

    @property
    def info_column(self) -> str:
        return self._info_column

    @info_column.setter
    def info_column(self, value: str | None) -> None:
        if value is None:
            value = ""
        settings = QtCore.QSettings()
        settings.setValue("Misc/last_info_column_name", value)
        self._info_column = value

    def all_fields_set(self) -> bool:
        return not self.required_fields

    def to_dict(self) -> dict[str, t.Any]:
        return {
            "file_path": self.file_path,
            "sampling_rate": self.sampling_rate,
            "signal_column": self._signal_column,
            "info_column": self.info_column,
            "column_names": self.column_names,
        }
