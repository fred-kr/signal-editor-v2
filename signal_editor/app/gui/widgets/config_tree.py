import enum
import typing as t

import qfluentwidgets as qfw
from PySide6 import QtCore, QtGui, QtWidgets

from ...enum_defs import RateComputationMethod, SVGColors, TextFileSeparator
from ...models import EnumModel, ItemDataRole, ModelIndex


class EnumComboBox(QtWidgets.QComboBox):
    def __init__(self, enum_class: t.Type[enum.Enum], parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self._enum_class = enum_class
        self.setModel(EnumModel(enum_class))

    def current_enum(self) -> enum.Enum:
        return self._enum_class(self.currentData())

    def set_current_enum(self, value: enum.Enum) -> None:
        self.setCurrentText(value.name)


class ConfigItemDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent: QtWidgets.QTreeView | None = None) -> None:
        super().__init__(parent)
        self._editable_types = (bool, int, float, QtGui.QColor, RateComputationMethod, TextFileSeparator, str)

    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionViewItem, index: ModelIndex) -> None:
        value = index.model().data(index, ItemDataRole.UserRole)
        if value is not None and not isinstance(value, self._editable_types):
            # If the value is not editable, we disable the item.
            my_option = QtWidgets.QStyleOptionViewItem(option)
            my_option.state &= ~QtWidgets.QStyle.StateFlag.State_Enabled  # pyright: ignore[reportAttributeAccessIssue]
            super().paint(painter, my_option, index)
            return

        super().paint(painter, option, index)

    def createEditor(  # type: ignore
        self, parent: QtWidgets.QWidget, option: QtWidgets.QStyleOptionViewItem, index: ModelIndex
    ) -> QtWidgets.QWidget | None:
        initial_value = index.model().data(index, ItemDataRole.EditRole)
        if type(initial_value) not in self._editable_types:
            return None

        if isinstance(initial_value, (RateComputationMethod, TextFileSeparator)):
            editor = EnumComboBox(initial_value.__class__, parent=parent)
        elif isinstance(initial_value, bool):
            editor = None
        elif isinstance(initial_value, int):
            editor = QtWidgets.QSpinBox(parent)
            editor.setMinimum(0)
        elif isinstance(initial_value, float):
            editor = QtWidgets.QDoubleSpinBox(parent)
            editor.setMinimum(0)
        elif isinstance(initial_value, QtGui.QColor):
            editor = EnumComboBox(SVGColors, parent=parent)
        else:
            editor = super().createEditor(parent, option, index)

        return editor

    def editorEvent(
        self,
        event: QtCore.QEvent,
        model: QtCore.QAbstractItemModel,
        option: QtWidgets.QStyleOptionViewItem,
        index: ModelIndex,
    ) -> bool:
        initial_value = index.model().data(index, ItemDataRole.EditRole)

        if (
            event.type() == QtCore.QEvent.Type.MouseButtonRelease
            and isinstance(initial_value, bool)
            and index.flags() & QtCore.Qt.ItemFlag.ItemIsEditable
        ):
            current_state = index.model().data(index, ItemDataRole.CheckStateRole)
            new_state = (
                QtCore.Qt.CheckState.Checked
                if current_state == QtCore.Qt.CheckState.Unchecked
                else QtCore.Qt.CheckState.Unchecked
            )
            model.setData(index, new_state, ItemDataRole.CheckStateRole)
            return True

        return super().editorEvent(event, model, option, index)

    def setEditorData(self, editor: QtWidgets.QWidget, index: ModelIndex) -> None:
        initial_value = index.model().data(index, ItemDataRole.EditRole)

        if isinstance(editor, EnumComboBox):
            if isinstance(initial_value, QtGui.QColor):
                initial_value = SVGColors(initial_value.name())
            editor.set_current_enum(initial_value)
        elif isinstance(editor, (QtWidgets.QSpinBox, QtWidgets.QDoubleSpinBox)):
            editor.setValue(initial_value)
        else:
            super().setEditorData(editor, index)

    def setModelData(self, editor: QtWidgets.QWidget, model: QtCore.QAbstractItemModel, index: ModelIndex) -> None:
        value = None
        if isinstance(editor, EnumComboBox):
            value = editor.current_enum()
            if isinstance(value, SVGColors):
                value = value.qcolor()
        elif isinstance(editor, (QtWidgets.QSpinBox, QtWidgets.QDoubleSpinBox)):
            value = editor.value()

        if isinstance(value, (RateComputationMethod, TextFileSeparator, int, float, QtGui.QColor)):
            model.setData(index, value, ItemDataRole.EditRole)
        else:
            super().setModelData(editor, model, index)


class ConfigTreeView(QtWidgets.QTreeView):
    def __init__(self, parent: QtWidgets.QWidget) -> None:
        super().__init__(parent)

        self.setItemDelegateForColumn(1, ConfigItemDelegate(self))
        self.header().setSizeAdjustPolicy(QtWidgets.QHeaderView.SizeAdjustPolicy.AdjustToContents)
        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def sizeHint(self) -> QtCore.QSize:
        return QtCore.QSize(800, 600)

    @QtCore.Slot()
    def restore_defaults(self) -> None:
        msg_box = qfw.MessageBox(
            title="Restore default settings?",
            content="Are you sure you want to restore all settings to their default values?",
            parent=self,
        )

        if msg_box.exec():
            self.model().restore_defaults()  # type: ignore

    @QtCore.Slot()
    def reset_current_item(self) -> None:
        self.model().reset_item(self.currentIndex())  # type: ignore

    @QtCore.Slot(QtCore.QPoint)
    def show_context_menu(self, pos: QtCore.QPoint) -> None:
        menu = QtWidgets.QMenu(self)
        menu.addAction("Restore Defaults", self.restore_defaults)
        menu.addAction("Reset Selected", self.reset_current_item)
        menu.exec(self.mapToGlobal(pos))
