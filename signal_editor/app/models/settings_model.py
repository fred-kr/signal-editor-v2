from PySide6 import QtCore, QtWidgets
import typing as t

class SettingsModel(QtCore.QAbstractItemModel):
    def __init__(self, settings_tree: dict[str, t.Any], parent: QtCore.QObject | None = None) -> None:
        super().__init__(parent)
        self.settings_tree = settings_tree

    def index(self, row: int, column: int, parent: QtCore.QModelIndex) -> QtCore.QModelIndex:
        