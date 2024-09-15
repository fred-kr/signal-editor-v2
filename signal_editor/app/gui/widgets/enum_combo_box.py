import enum
import typing as t

from PySide6 import QtCore, QtGui, QtWidgets

type T_ModelIndex = QtCore.QModelIndex | QtCore.QPersistentModelIndex
type T_Decoration = QtGui.QColor | QtGui.QIcon | QtGui.QPixmap

ItemDataRole = QtCore.Qt.ItemDataRole


class EnumModel[T_Enum: enum.Enum](QtCore.QAbstractListModel):
    def __init__(self, enum_class: t.Type[T_Enum], parent: QtCore.QObject | None = None) -> None:
        super().__init__(parent)
        self._enum_class = enum_class
        self._enum_members = list(self._enum_class)
        self._decoration_data: t.Callable[[T_Enum], T_Decoration] | None = None

    @property
    def enum_class(self) -> t.Type[T_Enum]:
        return self._enum_class

    def set_decoration_role_getter(self, fn: t.Callable[[T_Enum], T_Decoration] | None) -> None:
        self._decoration_data = fn

    def rowCount(self, parent: T_ModelIndex | None = None) -> int:
        return len(self._enum_members)

    def data(self, index: T_ModelIndex, role: int = ItemDataRole.DisplayRole) -> t.Any:
        if not index.isValid() or not (0 <= index.row() < len(self._enum_members)):
            return None
        enum_member = self._enum_members[index.row()]

        if role == ItemDataRole.DisplayRole:
            return enum_member.name
        elif role == ItemDataRole.ToolTipRole:
            return str(enum_member.value)
        elif role == ItemDataRole.UserRole:
            return enum_member
        elif role == ItemDataRole.DecorationRole and self._decoration_data is not None:
            return self._decoration_data(enum_member)
        elif role == ItemDataRole.EditRole:
            return enum_member
        return None


class EnumComboBox[T_Enum: enum.Enum](QtWidgets.QComboBox):
    def __init__(self, enum_class: t.Type[T_Enum], parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self._enum_class = enum_class
        self._enum_model = EnumModel(enum_class)
        self.setModel(self._enum_model)

    def current_enum(self) -> T_Enum:
        return self._enum_class(self.currentData())

    def set_current_enum(self, value: T_Enum) -> None:
        index = self.findData(value, role=ItemDataRole.UserRole)

        if index >= 0:
            self.setCurrentIndex(index)

    def set_decoration_role_getter(self, fn: t.Callable[[T_Enum], T_Decoration] | None) -> None:
        self._enum_model.set_decoration_role_getter(fn)
