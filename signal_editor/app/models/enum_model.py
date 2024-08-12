import enum
import typing as t

from PySide6 import QtCore
from . import ModelIndex, ItemDataRole


class EnumModel(QtCore.QAbstractListModel):
    def __init__(self, enum_class: t.Type[enum.Enum] | None, parent: QtCore.QObject | None = None) -> None:
        super().__init__(parent)
        self._enum_class = enum_class

    @property
    def enum_class(self) -> t.Type[enum.Enum] | None:
        return self._enum_class

    def rowCount(self, parent: ModelIndex | None = None) -> int:
        return 0 if self._enum_class is None else len(self._enum_class)

    def data(self, index: ModelIndex, role: int = ItemDataRole.DisplayRole) -> t.Any:
        if not index.isValid():
            return None
        if self._enum_class is None:
            return None

        enum_member = list(self._enum_class.__members__.values())[index.row()]

        if role == ItemDataRole.DisplayRole:
            return enum_member.name
        elif role == ItemDataRole.ToolTipRole:
            return enum_member.value
        elif role == ItemDataRole.UserRole:
            return enum_member
        elif role == ItemDataRole.DecorationRole:
            if "qcolor" in dir(enum_member):
                return enum_member.qcolor()  # type: ignore
            elif "qicon" in dir(enum_member):
                return enum_member.qicon()  # type: ignore

        return None
