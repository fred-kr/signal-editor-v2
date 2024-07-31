import typing as t

import attrs
from PySide6 import QtCore, QtGui

from ..config import Config
from ..enum_defs import SVGColors

type _Index = QtCore.QModelIndex | QtCore.QPersistentModelIndex
ItemDataRole = QtCore.Qt.ItemDataRole


class TreeItem:
    def __init__(self, data: list[str | t.Any], parent: "TreeItem | None" = None) -> None:
        self.item_data = data
        self.parent_item = parent
        self.child_items: list[TreeItem] = []

    @property
    def name(self) -> str:
        return self.item_data[0]

    @property
    def value(self) -> t.Any | None:
        return self.item_data[1]

    @property
    def description(self) -> str | None:
        return self.item_data[2]

    def is_editable(self) -> bool:
        return self.value is not None and self.description != ""

    def child(self, number: int) -> "TreeItem | None":
        if 0 <= number < len(self.child_items):
            return self.child_items[number]
        return None

    def child_count(self) -> int:
        return len(self.child_items)

    def child_number(self) -> int:
        if self.parent_item is not None:
            return self.parent_item.child_items.index(self)
        return 0

    def column_count(self) -> int:
        return len(self.item_data)

    def data(self, column: int) -> t.Any:
        return self.item_data[column] if 0 <= column < len(self.item_data) else None

    def insert_children(self, position: int, count: int, columns: int) -> bool:
        if position < 0 or position > len(self.child_items):
            return False

        for _ in range(count):
            data = [None] * columns
            child = TreeItem(data.copy(), self)
            self.child_items.insert(position, child)

        return True

    def parent(self) -> "TreeItem | None":
        return self.parent_item

    def set_data(self, column: int, value: t.Any) -> bool:
        if 0 <= column < len(self.item_data):
            self.item_data[column] = value
            return True
        return False

    def __repr__(self) -> str:
        parts = [f"<config_tree_model.TreeItem at 0x{id(self):x}>\n"]
        parts.extend(f' "{d}"' if d else " <None>" for d in self.item_data)
        parts.append(f", {len(self.child_items)} children")
        return "".join(parts)


class ConfigTreeModel(QtCore.QAbstractItemModel):
    def __init__(self, parent: QtCore.QObject | None = None) -> None:
        super().__init__(parent)
        self._config = Config()
        self._headers = ["Name", "Value", "Description"]
        self.root_item = TreeItem(self._headers.copy())

        self._plot_root = TreeItem(["Plot", None, ""], self.root_item)
        self._editing_root = TreeItem(["Editing", None, ""], self.root_item)
        self._data_root = TreeItem(["Data", None, ""], self.root_item)

        self.root_item.child_items.extend([self._plot_root, self._editing_root, self._data_root])

        self.setup_model_data(include_internal=False)

    def columnCount(self, parent: _Index | None = None) -> int:
        return self.root_item.column_count()

    def data(self, index: _Index, role: int | None = None) -> t.Any:
        if not index.isValid():
            return None

        col = index.column()
        item = self.get_item(index)
        type_ = type(item.value)

        if role == ItemDataRole.DisplayRole:
            if col == 0:
                return item.name
            elif col == 1:
                val = item.value
                if isinstance(val, QtGui.QColor):
                    return SVGColors(val.name()).name
                elif isinstance(val, bool):
                    return "✓" if val else "☐"
                elif val is None:
                    return ""
                return str(val)
            elif col == 2:
                desc = item.description
                return "" if desc is None else desc
        elif role == ItemDataRole.UserRole:
            if col == 0:
                return item.name
            elif col == 1:
                return item.value
            elif col == 2:
                return item.description
        elif role == ItemDataRole.DecorationRole:
            if col == 1 and isinstance(item.value, QtGui.QColor):
                return item.value
                # pixmap = QtGui.QPixmap(16, 16)
                # pixmap.fill(item.value)
                # return pixmap
        elif role == ItemDataRole.EditRole:
            if col == 1:
                return item.value
        elif role == ItemDataRole.SizeHintRole:
            if col == 0:
                return QtCore.QSize(170, 31)
            elif col == 1:
                return QtCore.QSize(170, 31)
            elif col == 2:
                return QtCore.QSize(250, 31)

        return None

    def flags(self, index: _Index) -> QtCore.Qt.ItemFlag:
        if not index.isValid():
            return QtCore.Qt.ItemFlag.NoItemFlags
        flags = QtCore.QAbstractItemModel.flags(self, index)
        item = self.get_item(index)

        if index.column() == 1 and item.is_editable():
            flags |= QtCore.Qt.ItemFlag.ItemIsEditable

        return flags

    def get_item(self, index: _Index) -> TreeItem:
        if index.isValid():
            if item := index.internalPointer():
                return item

        return self.root_item

    def headerData(
        self, section: int, orientation: QtCore.Qt.Orientation, role: int = ItemDataRole.DisplayRole
    ) -> t.Any:
        if orientation == QtCore.Qt.Orientation.Horizontal and role == ItemDataRole.DisplayRole:
            return self._headers[section]
        return None

    def index(self, row: int, column: int, parent: _Index | None = None) -> QtCore.QModelIndex:
        if parent is None:
            parent = QtCore.QModelIndex()

        if parent.isValid() and parent.column() != 0:
            return QtCore.QModelIndex()

        if parent_item := self.get_item(parent):
            return (
                self.createIndex(row, column, child_item)
                if (child_item := parent_item.child(row))
                else QtCore.QModelIndex()
            )
        else:
            return QtCore.QModelIndex()

    def parent(self, index: _Index | None = None) -> QtCore.QModelIndex:
        if index is None:
            index = QtCore.QModelIndex()

        if not index.isValid():
            return QtCore.QModelIndex()

        if child_item := self.get_item(index):
            parent_item = child_item.parent()
        else:
            parent_item = None

        if parent_item == self.root_item or not parent_item:
            return QtCore.QModelIndex()

        return self.createIndex(parent_item.child_number(), 0, parent_item)

    def rowCount(self, parent: _Index | None = None) -> int:
        if parent is None:
            parent = QtCore.QModelIndex()

        if parent.isValid() and parent.column() > 0:
            return 0

        parent_item = self.get_item(parent)
        return parent_item.child_count() if parent_item else 0

    def setData(self, index: _Index, value: t.Any, role: int = ItemDataRole.EditRole) -> bool:
        if role not in {ItemDataRole.EditRole, ItemDataRole.UserRole} or not index.isValid() or index.column() != 1:
            return False

        item = self.get_item(index)
        # if role != ItemDataRole.CheckStateRole and isinstance(item.value, bool):
        # return False

        result = item.set_data(index.column(), value)
        if result:
            self.dataChanged.emit(index, index)

        return result

    def setup_model_data(self, include_internal: bool = False) -> None:
        # Add Plot Config items
        for field in attrs.fields(self._config.plot.__class__):
            self._plot_root.child_items.append(
                TreeItem(
                    [field.name, getattr(self._config.plot, field.name), field.metadata.get("Description", "")],
                    self._plot_root,
                )
            )

        # Add Editing Config items
        for field in attrs.fields(self._config.editing.__class__):
            self._editing_root.child_items.append(
                TreeItem(
                    [field.name, getattr(self._config.editing, field.name), field.metadata.get("Description", "")],
                    self._editing_root,
                )
            )

        # Add Data Config items
        for field in attrs.fields(self._config.data.__class__):
            self._data_root.child_items.append(
                TreeItem(
                    [field.name, getattr(self._config.data, field.name), field.metadata.get("Description", "")],
                    self._data_root,
                )
            )

        if include_internal:
            self._internal_root = TreeItem(["Internal", None, ""], self.root_item)
            self.root_item.child_items.append(self._internal_root)

            for field in attrs.fields(self._config.internal.__class__):
                self._internal_root.child_items.append(
                    TreeItem(
                        [field.name, getattr(self._config.internal, field.name), field.metadata.get("Description", "")],
                        self._internal_root,
                    )
                )

    def __repr__(self) -> str:
        return f"<config_tree_model.ConfigTreeModel at 0x{id(self):x}>"
