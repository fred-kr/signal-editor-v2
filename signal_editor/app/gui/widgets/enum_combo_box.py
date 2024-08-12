import enum
import typing as t

from PySide6 import QtWidgets

from ...models import EnumModel


class EnumComboBox(QtWidgets.QComboBox):
    def __init__(self, enum_class: t.Type[enum.Enum], parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self._enum_class = enum_class
        self.setModel(EnumModel(enum_class))

    def current_enum(self) -> enum.Enum:
        return self._enum_class(self.currentData())

    def set_current_enum(self, value: enum.Enum) -> None:
        self.setCurrentText(value.name)
