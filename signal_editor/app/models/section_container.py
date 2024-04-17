from PySide6 import QtCore

from ..core.section import Section, SectionID


class SectionListModel(QtCore.QAbstractListModel):
    def __init__(
        self,
        sections: list[Section] | None = None,
        parent: QtCore.QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._sections = sections or []

    @property
    def editable_sections(self) -> list[Section]:
        return self._sections

    @property
    def editable_section_ids(self) -> list[SectionID]:
        return [section.section_id for section in self._sections]

    def rowCount(
        self, parent: QtCore.QModelIndex | QtCore.QPersistentModelIndex | None = None
    ) -> int:
        return len(self._sections)

    def data(
        self,
        index: QtCore.QModelIndex | QtCore.QPersistentModelIndex,
        role: int = QtCore.Qt.ItemDataRole.DisplayRole,
    ) -> Section | SectionID | None:
        if not index.isValid():
            return None
        if index.row() >= self.rowCount():
            return None
        section = self._sections[index.row()]

        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            return section.section_id
        return section if role == QtCore.Qt.ItemDataRole.UserRole else None

    def headerData(
        self,
        section: int,
        orientation: QtCore.Qt.Orientation,
        role: int = QtCore.Qt.ItemDataRole.DisplayRole,
    ) -> str | None:
        if role != QtCore.Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == QtCore.Qt.Orientation.Vertical:
            return str(section)
        else:
            return f"Sections ({self.rowCount()})"

    def add_section(self, section: Section) -> None:
        parent = self.index(0, 0)
        self.beginInsertRows(parent, self.rowCount(), self.rowCount())
        self._sections.append(section)
        self.endInsertRows()

    def remove_section(self, section_id: SectionID) -> None:
        for i, section in enumerate(self._sections):
            if section.section_id == section_id:
                self.beginRemoveRows(QtCore.QModelIndex(), i, i)
                self._sections.remove(section)
                self.endRemoveRows()
                break

    def remove_section_by_index(self, index: QtCore.QModelIndex) -> None:
        row = index.row()
        parent = self.index(0, 0)
        self.beginRemoveRows(parent, row, row)
        self._sections.remove(self._sections[row])
        self.endRemoveRows()

    def get_section(self, section_id: SectionID) -> Section | None:
        return next(
            (section for section in self._sections if section.section_id == section_id),
            None,
        )

    def clear(self) -> None:
        self.beginResetModel()
        self._sections.clear()
        self.endResetModel()

    def update_sampling_rate(self, sampling_rate: int) -> None:
        for section in self._sections:
            section.update_sampling_rate(sampling_rate)
