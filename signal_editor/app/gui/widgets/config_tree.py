import typing as t

from PySide6 import QtCore, QtGui, QtWidgets
import qfluentwidgets as qfw

from ...enum_defs import RateComputationMethod, SVGColors, TextFileSeparator

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


# TODO: Combine the following three classes into a single class that can handle all three types of enums.
class ColorComboBox(QtWidgets.QComboBox):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setModel(SVGColorListModel())

    def current_color(self) -> QtGui.QColor:
        return QtGui.QColor(self.currentData())

    def set_color(self, color: SVGColors) -> None:
        self.setCurrentText(color.name)


class RateMethodComboBox(QtWidgets.QComboBox):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        for rm in RateComputationMethod:
            name = rm.name
            value = rm.value

            self.addItem(name, userData=value)

    def current_method(self) -> RateComputationMethod:
        return RateComputationMethod(self.currentData())

    def set_method(self, method: RateComputationMethod) -> None:
        self.setCurrentText(method.name)


class TextFileSeparatorComboBox(QtWidgets.QComboBox):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        for separator in TextFileSeparator:
            name = separator.name
            value = separator.value

            self.addItem(name, userData=value)

    def current_separator(self) -> TextFileSeparator:
        return TextFileSeparator(self.currentData())

    def set_separator(self, separator: TextFileSeparator) -> None:
        self.setCurrentText(separator.name)


class ConfigItemDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent: QtWidgets.QTreeView | None = None) -> None:
        super().__init__(parent)
        self._editable_types = (bool, int, float, QtGui.QColor, RateComputationMethod, TextFileSeparator, str)

    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionViewItem, index: _Index) -> None:
        value = index.model().data(index, ItemDataRole.UserRole)
        if value is not None and not isinstance(value, self._editable_types):
            # If the value is not editable, we disable the item.
            my_option = QtWidgets.QStyleOptionViewItem(option)
            my_option.state &= ~QtWidgets.QStyle.StateFlag.State_Enabled  # pyright: ignore[reportAttributeAccessIssue]
            super().paint(painter, my_option, index)
            return

        super().paint(painter, option, index)

    def createEditor(
        self, parent: QtWidgets.QWidget, option: QtWidgets.QStyleOptionViewItem, index: _Index
    ) -> QtWidgets.QWidget | None:
        initial_value = index.model().data(index, ItemDataRole.EditRole)
        if type(initial_value) not in self._editable_types:
            return None

        if isinstance(initial_value, RateComputationMethod):
            editor = RateMethodComboBox(parent)
        elif isinstance(initial_value, TextFileSeparator):
            editor = TextFileSeparatorComboBox(parent)
        elif isinstance(initial_value, bool):
            editor = None
        elif isinstance(initial_value, int):
            editor = QtWidgets.QSpinBox(parent)
            editor.setMinimum(0)
        elif isinstance(initial_value, float):
            editor = QtWidgets.QDoubleSpinBox(parent)
            editor.setMinimum(0)
        elif isinstance(initial_value, QtGui.QColor):
            editor = ColorComboBox(parent)
        else:
            editor = super().createEditor(parent, option, index)

        return editor

    def editorEvent(
        self,
        event: QtCore.QEvent,
        model: QtCore.QAbstractItemModel,
        option: QtWidgets.QStyleOptionViewItem,
        index: _Index,
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

    def setEditorData(self, editor: QtWidgets.QWidget, index: _Index) -> None:
        initial_value = index.model().data(index, ItemDataRole.EditRole)

        if isinstance(editor, RateMethodComboBox):
            editor.set_method(initial_value)
        elif isinstance(editor, TextFileSeparatorComboBox):
            editor.set_separator(initial_value)
        elif isinstance(editor, (QtWidgets.QSpinBox, QtWidgets.QDoubleSpinBox)):
            editor.setValue(initial_value)
        elif isinstance(editor, ColorComboBox):
            editor.set_color(SVGColors(initial_value.name()))
        else:
            super().setEditorData(editor, index)

    def setModelData(self, editor: QtWidgets.QWidget, model: QtCore.QAbstractItemModel, index: _Index) -> None:
        value = None
        if isinstance(editor, RateMethodComboBox):
            value = editor.current_method()
        elif isinstance(editor, TextFileSeparatorComboBox):
            value = editor.current_separator()
        elif isinstance(editor, ColorComboBox):
            value = editor.current_color()
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

        # msg_box = QtWidgets.QMessageBox(
        # QtWidgets.QMessageBox.Icon.Warning,
        # "Restore default settings?",
        # "Are you sure you want to restore all settings to their default values?",
        # parent=self,
        # )
        if sure := msg_box.exec():
            # self.model() returns a ConfigTreeModel
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
