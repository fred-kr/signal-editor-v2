import typing as t
from pathlib import Path

from PySide6 import QtCore

from ..config import Config
from ..utils import format_file_path
from . import ItemDataRole, ModelIndex


class FileListModel(QtCore.QAbstractListModel):
    sig_files_changed = QtCore.Signal()

    def __init__(
        self, recent_files: list[str] | None = None, max_files: int = 10, parent: QtCore.QObject | None = None
    ) -> None:
        super().__init__(parent)
        self._recent_files = recent_files or []
        self._max_files = max_files

        self.sig_files_changed.connect(self.update_config)

    def rowCount(self, parent: ModelIndex | None = None) -> int:
        return len(self._recent_files)

    def data(self, index: ModelIndex, role: int = ItemDataRole.DisplayRole) -> t.Any:
        if not index.isValid() or not self._recent_files:
            return None

        row = index.row()
        if row >= self.rowCount():
            return None

        file_path = self._recent_files[row]

        if role == ItemDataRole.DisplayRole:
            return format_file_path(file_path, max_len=70)
        elif role in [ItemDataRole.UserRole, ItemDataRole.ToolTipRole]:
            return file_path
        return None

    def headerData(
        self, section: int, orientation: QtCore.Qt.Orientation, role: int = ItemDataRole.DisplayRole
    ) -> t.Any:
        if role != ItemDataRole.DisplayRole:
            return None

        if orientation == QtCore.Qt.Orientation.Horizontal:
            return "Recent Files"

        return str(section + 1)

    def add_file(self, file_path: str) -> None:
        if not Path(file_path).is_file():
            return
        parent = QtCore.QModelIndex()

        if file_path in self._recent_files:
            file_index = self._recent_files.index(file_path)
            self.beginRemoveRows(parent, file_index, file_index)
            self._recent_files.remove(file_path)
            self.endRemoveRows()

        self.beginInsertRows(parent, 0, 0)
        self._recent_files.insert(0, file_path)
        self.endInsertRows()

        if self.rowCount() > self._max_files:
            # Remove the oldest file, i.e. the last one
            self.beginRemoveRows(parent, self.rowCount() - 1, self.rowCount() - 1)
            self._recent_files.pop()
            self.endRemoveRows()

        self.sig_files_changed.emit()

    def remove_file(self, index: ModelIndex) -> None:
        row = index.row()
        parent = self.index(0, 0)
        self.beginRemoveRows(parent, row, row)
        del self._recent_files[row]
        self.endRemoveRows()

        self.sig_files_changed.emit()

    def clear(self) -> None:
        self.beginResetModel()
        self._recent_files.clear()
        self.endResetModel()

        self.sig_files_changed.emit()

    def set_recent_files(self, recent_files: list[str]) -> None:
        self.beginResetModel()
        self._recent_files = recent_files
        self.endResetModel()

        self.sig_files_changed.emit()

    def get_recent_files(self) -> list[str]:
        return self._recent_files

    def validate_files(self) -> None:
        for i, file_path in enumerate(self._recent_files):
            if not Path(file_path).is_file():
                self.remove_file(self.index(i))

    @QtCore.Slot()
    def update_config(self) -> None:
        Config().internal.recent_files = self._recent_files
