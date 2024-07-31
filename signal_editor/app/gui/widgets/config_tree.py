import contextlib
import typing as t
import qfluentwidgets as qfw
from PySide6 import QtCore, QtGui, QtWidgets
import enum

from ...enum_defs import RateComputationMethod, SVGColors

type _Index = QtCore.QModelIndex | QtCore.QPersistentModelIndex

ItemDataRole = QtCore.Qt.ItemDataRole


class SVGColorListModel(QtCore.QAbstractListModel):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self._colors = SVGColors

    @property
    def hex_codes(self) -> list[str]:
        return [c.value for c in self._colors]

    def rowCount(self, parent: _Index | None = None) -> int:
        return len(self._colors)

    def data(self, index: _Index, role: int = ItemDataRole.DisplayRole) -> t.Any:
        if not index.isValid():
            return None

        svg_color = self._colors(self.hex_codes[index.row()])
        
        if role == ItemDataRole.DisplayRole:
            return svg_color.name
        elif role == ItemDataRole.UserRole:
            return svg_color
        elif role == ItemDataRole.DecorationRole:
            pixmap = QtGui.QPixmap(16, 16)
            pixmap.fill(QtGui.QColor(svg_color.value))
            return QtGui.QIcon(pixmap)

        return None


class ColorComboBox(QtWidgets.QComboBox):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setMinimumHeight(21)
        self.setModel(SVGColorListModel())

    def current_color(self) -> QtGui.QColor:
        return QtGui.QColor(self.currentData())

    def set_color(self, color: SVGColors) -> None:
        self.setCurrentText(color.name)


class RateMethodComboBox(QtWidgets.QComboBox):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setMinimumHeight(21)
        for rm in RateComputationMethod:
            name = rm.name
            value = rm.value

            self.addItem(name, userData=value)

    def current_method(self) -> RateComputationMethod:
        return RateComputationMethod(self.currentData())

    def set_method(self, method: RateComputationMethod) -> None:
        self.setCurrentText(method.name)

class EnumComboBox(QtWidgets.QComboBox):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setMinimumHeight(21)

        self._enum_class: t.Type[enum.Enum] | None = None

    def set_enum(self, enum_class: t.Type[enum.Enum]) -> None:
        self._enum_class = enum_class
        self.clear()

        for enum_member in self._enum_class:
            name = enum_member.name
            value = enum_member.value

            self.addItem(name, userData=value)

    def current_enum(self) -> enum.Enum | None:
        if self._enum_class is None:
            return None
        return self._enum_class[self.currentText()]

    def current_name(self) -> str:
        current_enum = self.current_enum()
        return "" if current_enum is None else current_enum.name

    def current_value(self) -> t.Any | None:
        current_enum = self.current_enum()
        return None if current_enum is None else current_enum.value

    def currentData(self, role: int = ItemDataRole.UserRole) -> t.Any | None:
        return self.current_value()



class ConfigItemDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent: QtWidgets.QTreeView | None = None) -> None:
        super().__init__(parent)
        
    def createEditor(
        self, parent: QtWidgets.QWidget, option: QtWidgets.QStyleOptionViewItem, index: _Index
    ) -> QtWidgets.QWidget:

        initial_value = index.data(ItemDataRole.EditRole)

        if isinstance(initial_value, RateComputationMethod):
            editor = RateMethodComboBox(parent)
        elif isinstance(initial_value, int):
            editor = QtWidgets.QSpinBox(parent)
            editor.setMinimum(0)
        elif isinstance(initial_value, float):
            editor = QtWidgets.QDoubleSpinBox(parent)
            editor.setMinimum(0)
        elif isinstance(initial_value, bool):
            editor = QtWidgets.QCheckBox(parent)
        elif isinstance(initial_value, QtGui.QColor):
            editor = ColorComboBox(parent)
        else:
            editor = QtWidgets.QStyledItemDelegate.createEditor(self, parent, option, index)

        editor.setMinimumHeight(21)
        
        with contextlib.suppress(Exception):
            if hasattr(editor, "setFrame"):
                editor.setFrame(False)
            
        return editor

    def setEditorData(self, editor: QtWidgets.QWidget, index: _Index) -> None:

        initial_value = index.data(ItemDataRole.EditRole)

        if isinstance(initial_value, RateComputationMethod):
            assert isinstance(editor, RateMethodComboBox), f"Editor for value {initial_value} is not a combobox: {type(editor)}"
            editor.set_method(initial_value)
        elif isinstance(initial_value, bool):
            assert isinstance(editor, QtWidgets.QCheckBox), f"Editor for value {initial_value} is not a checkbox: {type(editor)}"
            editor.setCheckState(QtCore.Qt.CheckState.Checked if initial_value else QtCore.Qt.CheckState.Unchecked)
        elif isinstance(initial_value, int):
            assert isinstance(editor, QtWidgets.QSpinBox), f"Editor for value {initial_value} is not a spinbox: {type(editor)}"
            editor.setValue(initial_value)
        elif isinstance(initial_value, float):
            assert isinstance(editor, QtWidgets.QDoubleSpinBox), f"Editor for value {initial_value} is not a double spinbox: {type(editor)}"
            editor.setValue(initial_value)
        elif isinstance(initial_value, QtGui.QColor):
            assert isinstance(editor, ColorComboBox), f"Editor for value {initial_value} is not a color combobox: {type(editor)}"
            editor.set_color(SVGColors(initial_value.name()))
        else:
            QtWidgets.QStyledItemDelegate.setEditorData(self, editor, index)

    def setModelData(self, editor: QtWidgets.QWidget, model: QtCore.QAbstractItemModel, index: _Index) -> None:

        value = None
        if isinstance(editor, EnumComboBox):
            value = editor.current_enum()
        elif isinstance(editor, ColorComboBox):
            value = editor.current_color()
        elif isinstance(editor, QtWidgets.QComboBox):
            value = editor.currentText()
        elif isinstance(editor, (QtWidgets.QSpinBox, QtWidgets.QDoubleSpinBox, qfw.SpinBox, qfw.CompactSpinBox, qfw.DoubleSpinBox, qfw.CompactDoubleSpinBox)):
            value = editor.value()
        elif isinstance(editor, (QtWidgets.QCheckBox, qfw.CheckBox)):
            value = editor.isChecked()

        if isinstance(value, (RateComputationMethod, int, float, bool, QtGui.QColor)):
            model.setData(index, value, ItemDataRole.EditRole)
        # elif isinstance(value, SVGColors):
        #     model.setData(index, QtGui.QColor(value.value), ItemDataRole.EditRole)
        else:
            QtWidgets.QStyledItemDelegate.setModelData(self, editor, model, index)

class ConfigTreeView(QtWidgets.QTreeView):
    def __init__(self, parent: QtWidgets.QWidget) -> None:
        super().__init__(parent)

        self.setItemDelegateForColumn(1, ConfigItemDelegate(self))
        # self.setSizeAdjustPolicy(QtWidgets.QAbstractItemView.SizeAdjustPolicy.AdjustToContentsOnFirstShow)
        # self.header().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        self.header().setSizeAdjustPolicy(QtWidgets.QHeaderView.SizeAdjustPolicy.AdjustToContents)
        # self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        # self.setUniformRowHeights(True)
        # self.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        # self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectItems)
        # self.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.SelectedClicked | QtWidgets.QAbstractItemView.EditTrigger.DoubleClicked | QtWidgets.QAbstractItemView.EditTrigger.EditKeyPressed)
        # self.setAnimated(True)

    def sizeHint(self) -> QtCore.QSize:
        return QtCore.QSize(800, 600)

def test_config_tree() -> None:
    import sys
    from signal_editor.app.models.config_tree_model import ConfigTreeModel

    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QWidget()
    window.setWindowTitle("Config Tree View")
    layout = QtWidgets.QVBoxLayout(window)

    tree = ConfigTreeView(window)
    model = ConfigTreeModel(window)
    tree.setModel(model)
    tree.expandAll()
    for column in range(model.columnCount()):
        tree.resizeColumnToContents(column)

    tree.adjustSize()

    layout.addWidget(tree)
    window.show()
    sys.exit(app.exec())
    
    
