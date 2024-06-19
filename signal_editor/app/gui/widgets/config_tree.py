import enum
import typing as t

import qfluentwidgets as qfw
from PySide6 import QtCore, QtGui, QtWidgets

from ...config import Config
from ... import type_defs as _t

from ...enum_defs import RateComputationMethod

type Index = QtCore.QModelIndex | QtCore.QPersistentModelIndex

class ConfigItemDelegate(qfw.TreeItemDelegate):
    def __init__(self, parent: qfw.TreeView) -> None:
        super().__init__(parent)

    def createEditor(
        self,
        parent: QtWidgets.QWidget,
        option: QtWidgets.QStyleOptionViewItem,
        index: Index,
    ) -> QtWidgets.QWidget:
        data = index.data(QtCore.Qt.ItemDataRole.EditRole)
        item = index.data(QtCore.Qt.ItemDataRole.UserRole)

        if isinstance(data, bool):
            editor = qfw.CheckBox(parent)
        elif isinstance(data, int):
            editor = qfw.CompactSpinBox(parent)
            editor.setMinimum(0)
        elif isinstance(data, float):
            editor = qfw.CompactDoubleSpinBox(parent)
            editor.setMinimum(0)
        elif isinstance(item, RateComputationMethod):
            editor = qfw.ComboBox(parent)
            editor.addItems(list(RateComputationMethod.__members__))
        elif isinstance(data, str):
            editor = qfw.LineEdit(parent)
        elif isinstance(data, list):
            editor = qfw.ComboBox(parent)
            editor.addItems(data)
        elif isinstance(data, QtGui.QColor):
            editor = qfw.ColorPickerButton(data, index.data(QtCore.Qt.ItemDataRole.DisplayRole), parent, enableAlpha=True)
        else:
            editor = super().createEditor(parent, option, index)
        return editor

    def setEditorData(self, editor: QtWidgets.QWidget, index: Index) -> None:
        data = index.data(QtCore.Qt.ItemDataRole.EditRole)
        if isinstance(editor, qfw.CheckBox):
            editor.setChecked(data)
        elif isinstance(editor, qfw.CompactSpinBox):
            editor.setValue(data)
        elif isinstance(editor, qfw.CompactDoubleSpinBox):
            editor.setValue(data)
        elif isinstance(editor, qfw.LineEdit):
            editor.setText(data)
        elif isinstance(editor, qfw.ComboBox):
            editor.setCurrentText(data)
        elif isinstance(editor, qfw.ColorPickerButton):
            editor.setColor(data)
        else:
            super().setEditorData(editor, index)

    def setModelData(self, editor: QtWidgets.QWidget, model: QtCore.QAbstractItemModel, index: Index) -> None:
        if isinstance(editor, qfw.CheckBox):
            model.setData(index, editor.isChecked(), QtCore.Qt.ItemDataRole.EditRole)
        elif isinstance(editor, qfw.CompactSpinBox):
            model.setData(index, editor.value(), QtCore.Qt.ItemDataRole.EditRole)
        elif isinstance(editor, qfw.CompactDoubleSpinBox):
            model.setData(index, editor.value(), QtCore.Qt.ItemDataRole.EditRole)
        elif isinstance(editor, qfw.LineEdit):
            model.setData(index, editor.text(), QtCore.Qt.ItemDataRole.EditRole)
        elif isinstance(editor, qfw.ComboBox):
            model.setData(index, editor.currentText(), QtCore.Qt.ItemDataRole.EditRole)
            model.setData(index, RateComputationMethod[editor.currentText()], QtCore.Qt.ItemDataRole.UserRole)
        elif isinstance(editor, qfw.ColorPickerButton):
            model.setData(index, editor.color.name(QtGui.QColor.NameFormat.HexArgb), QtCore.Qt.ItemDataRole.EditRole)
            model.setData(index, editor.color, QtCore.Qt.ItemDataRole.UserRole | QtCore.Qt.ItemDataRole.BackgroundRole)
        else:
            super().setModelData(editor, model, index)

    def updateEditorGeometry(
        self,
        editor: QtWidgets.QWidget,
        option: QtWidgets.QStyleOptionViewItem,
        index: Index,
    ) -> None:
        super().updateEditorGeometry(editor, option, index)


class ConfigTree(qfw.TreeView):
    sig_restore_defaults = QtCore.Signal(bool)
    sig_reset_current = QtCore.Signal(QtCore.QModelIndex)
    
    def __init__(self, parent: QtWidgets.QWidget) -> None:
        super().__init__(parent)
        self.setItemDelegate(ConfigItemDelegate(self))

        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)


    def show_context_menu(self, pos: QtCore.QPoint) -> None:
        menu = QtWidgets.QMenu(self)

        menu.addAction("Reset Selected", self.emit_reset_current)
        menu.addAction("Restore Defaults", self.emit_restore_defaults)
        menu.exec(self.mapToGlobal(pos))

    def emit_reset_current(self) -> None:
        self.sig_reset_current.emit(self.currentIndex())

    def emit_restore_defaults(self, include_internal: bool = False) -> None:
        self.sig_restore_defaults.emit(include_internal)


class TreeItem:
    def __init__(self, data: list[t.Any], parent: 'TreeItem | None' = None) -> None:
        self.item_data = data
        self.parent_item = parent
        self.child_items: list[TreeItem] = []

    def child(self, number: int) -> 'TreeItem | None':
        if number < 0 or number >= len(self.child_items):
            return None
        return self.child_items[number]

    def last_child(self):
        return self.child_items[-1] if self.child_items else None

    def child_count(self) -> int:
        return len(self.child_items)

    def child_number(self) -> int:
        return self.parent_item.child_items.index(self) if self.parent_item else 0

    def column_count(self) -> int:
        return len(self.item_data)

    def data(self, column: int):
        if column < 0 or column >= len(self.item_data):
            return None
        return self.item_data[column]

    def insert_children(self, position: int, count: int, columns: int) -> bool:
        if position < 0 or position > len(self.child_items):
            return False

        for _ in range(count):
            data = [None] * columns
            item = TreeItem(data.copy(), self)
            self.child_items.insert(position, item)

        return True

    def insert_columns(self, position: int, columns: int) -> bool:
        if position < 0 or position > len(self.item_data):
            return False

        for _ in range(columns):
            self.item_data.insert(position, None)

        for child in self.child_items:
            child.insert_columns(position, columns)

        return True

    def parent(self):
        return self.parent_item

    def remove_children(self, position: int, count: int) -> bool:
        if position < 0 or position + count > len(self.child_items):
            return False

        for _ in range(count):
            self.child_items.pop(position)

        return True

    def remove_columns(self, position: int, columns: int) -> bool:
        if position < 0 or position + columns > len(self.item_data):
            return False

        for _ in range(columns):
            self.item_data.pop(position)

        for child in self.child_items:
            child.remove_columns(position, columns)

        return True

    def set_data(self, column: int, value: t.Any) -> bool:
        if column < 0 or column >= len(self.item_data):
            return False

        self.item_data[column] = value
        return True

    def __repr__(self) -> str:
        result = f"<treeitem.TreeItem at 0x{id(self):x}"
        for d in self.item_data:
            result += f' "{d}"' if d else " <None>"
        result += f", {len(self.child_items)} children>"
        return result

    
class ConfigTreeModel(QtCore.QAbstractItemModel):
    def __init__(self, parent: QtCore.QObject) -> None:
        super().__init__(parent)

        self._config = Config.from_settings()
        self._root = self.createIndex(0, 0)
        self._columns = ("Name", "Value", "Description")

    def columnCount(self, parent: Index | None = None) -> int:
        return 3

    def rowCount(self, parent: Index | None = None) -> int:
        if parent is None:
            parent = QtCore.QModelIndex()

        if parent.column() > 0:
            return 0

        parent_item = parent.internalPointer() if parent.isValid() else self._root
        return parent_item.childCount()

    def data(self, index: Index, role: int = QtCore.Qt.ItemDataRole.DisplayRole) -> t.Any:
        if not index.isValid():
            return None

        item = index.internalPointer()

        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            