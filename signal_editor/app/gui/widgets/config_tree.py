import qfluentwidgets as qfw
from PySide6 import QtCore, QtGui, QtWidgets

from ...enum_defs import RateComputationMethod

type _Index = QtCore.QModelIndex | QtCore.QPersistentModelIndex


class ConfigItemDelegate(qfw.TreeItemDelegate):
    def __init__(self, parent: qfw.TreeView | qfw.TreeWidget) -> None:
        super().__init__(parent)

    def createEditor(
        self, parent: QtWidgets.QWidget, option: QtWidgets.QStyleOptionViewItem, index: _Index
    ) -> QtWidgets.QWidget:
        if index.column() != 2:
            return super().createEditor(parent, option, index)

        value = index.data(QtCore.Qt.ItemDataRole.UserRole)

        if isinstance(value, bool):
            editor = qfw.CheckBox(parent)
            editor.setChecked(value)
        elif isinstance(value, RateComputationMethod):
            editor = qfw.ComboBox(parent)
            editor.addItems([str(m) for m in RateComputationMethod])
            editor.setCurrentText(str(value))
        elif isinstance(value, int):
            editor = qfw.SpinBox(parent)
            editor.setValue(value)
            editor.setMinimum(0)
        elif isinstance(value, float):
            editor = qfw.DoubleSpinBox(parent)
            editor.setValue(value)
            editor.setMinimum(0)
        elif isinstance(value, QtGui.QColor):
            editor = qfw.ColorPickerButton(color=value, title="Choose Color", parent=parent)
        else:
            editor = super().createEditor(parent, option, index)

        return editor

    def setEditorData(self, editor: QtWidgets.QWidget, index: _Index) -> None:
        if index.column() != 2:
            return super().setEditorData(editor, index)

        value = index.data(QtCore.Qt.ItemDataRole.UserRole)

        if isinstance(value, bool):
            assert isinstance(editor, qfw.CheckBox)
            editor.setChecked(value)
        elif isinstance(value, RateComputationMethod):
            assert isinstance(editor, qfw.ComboBox)
            editor.setCurrentText(str(value))
        elif isinstance(value, int):
            assert isinstance(editor, qfw.SpinBox)
            editor.setValue(value)
        elif isinstance(value, float):
            assert isinstance(editor, qfw.DoubleSpinBox)
            editor.setValue(value)
        elif isinstance(value, QtGui.QColor):
            assert isinstance(editor, qfw.ColorPickerButton)
            editor.setColor(value)
        else:
            super().setEditorData(editor, index)

    def setModelData(self, editor: QtWidgets.QWidget, model: QtCore.QAbstractItemModel, index: _Index) -> None:
        if index.column() != 2:
            return super().setModelData(editor, model, index)

        value = index.data(QtCore.Qt.ItemDataRole.UserRole)

        if isinstance(value, bool):
            assert isinstance(editor, qfw.CheckBox)
            model.setData(index, editor.isChecked(), QtCore.Qt.ItemDataRole.EditRole)
        elif isinstance(value, RateComputationMethod):
            assert isinstance(editor, qfw.ComboBox)
            model.setData(index, RateComputationMethod[editor.currentText()], QtCore.Qt.ItemDataRole.EditRole)
        elif isinstance(value, int):
            assert isinstance(editor, qfw.SpinBox)
            model.setData(index, editor.value(), QtCore.Qt.ItemDataRole.EditRole)
        elif isinstance(value, float):
            assert isinstance(editor, qfw.DoubleSpinBox)
            model.setData(index, editor.value(), QtCore.Qt.ItemDataRole.EditRole)
        elif isinstance(value, QtGui.QColor):
            assert isinstance(editor, qfw.ColorPickerButton)
            model.setData(index, editor.color, QtCore.Qt.ItemDataRole.EditRole)
        else:
            super().setModelData(editor, model, index)


class ConfigTreeView(qfw.TreeView):
    def __init__(self, parent: QtWidgets.QWidget) -> None:
        super().__init__(parent)

        self.setItemDelegate(ConfigItemDelegate(self))
