import typing as t

from PySide6 import QtCore

from ..core.section import SectionID
from ..gui.icons import SignalEditorIcons as Icons
from . import ItemDataRole, ModelIndex

if t.TYPE_CHECKING:
    from ..core.section import Section


class SectionListModel(QtCore.QAbstractListModel):
    def __init__(
        self,
        sections: list["Section"] | None = None,
        parent: QtCore.QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._sections = sections or []

    @property
    def editable_sections(self) -> list["Section"]:
        return list(self._sections)[1:]

    def rowCount(self, parent: ModelIndex | None = None) -> int:
        return len(self._sections)

    def data(
        self,
        index: ModelIndex,
        role: int = ItemDataRole.DisplayRole,
    ) -> t.Any:
        if not index.isValid() or not self._sections:
            return None
        row = index.row()
        if row >= self.rowCount():
            return None

        section = self._sections[row]

        if role == ItemDataRole.DisplayRole:
            return section.section_id.pretty_name()
        elif role == ItemDataRole.SizeHintRole:
            return QtCore.QSize(100, 31)
        elif role == ItemDataRole.UserRole:
            return section
        elif role == ItemDataRole.ToolTipRole:
            return repr(section)
        elif role == ItemDataRole.DecorationRole:
            return Icons.LockClosed.icon() if section.is_locked else Icons.LockOpen.icon()
        return None

    def add_section(self, section: "Section") -> None:
        parent = self.index(0, 0)
        self.beginInsertRows(parent, self.rowCount(), self.rowCount())
        self._sections.append(section)
        self.refresh_section_ids()
        self.endInsertRows()

    def remove_section(self, index: QtCore.QModelIndex) -> None:
        row = index.row()
        parent = self.index(0, 0)
        self.beginRemoveRows(parent, row, row)
        self._sections.remove(self._sections[row])
        self.refresh_section_ids()
        self.endRemoveRows()

    def get_section(self, index: QtCore.QModelIndex) -> "Section | None":
        return self._sections[index.row()] if index.isValid() else None

    def get_base_section(self) -> "Section | None":
        return self._sections[0] if self._sections else None

    def clear(self) -> None:
        self.beginResetModel()
        self._sections.clear()
        self.endResetModel()

    def update_sampling_rate(self, sampling_rate: int) -> None:
        for section in self._sections:
            section.update_sampling_rate(sampling_rate)

    def refresh_section_ids(self) -> None:
        for i, section in enumerate(self._sections):
            section.section_id = SectionID(f"Section_{section.signal_name}_{i:03}")
