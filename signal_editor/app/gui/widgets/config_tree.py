import enum
import typing as t

import qfluentwidgets as qfw
from PySide6 import QtCore, QtGui, QtWidgets

from ...enum_defs import RateComputationMethod, SVGColors, TextFileSeparator

type _Index = QtCore.QModelIndex | QtCore.QPersistentModelIndex

ItemDataRole = QtCore.Qt.ItemDataRole


NONE_STRING = "----"


class EnumModel(QtCore.QAbstractListModel):
    def __init__(self, enum_class: t.Type[enum.Enum] | None, parent: QtCore.QObject | None = None) -> None:
        super().__init__(parent)
        self._enum_class = enum_class

    @property
    def enum_class(self) -> t.Type[enum.Enum] | None:
        return self._enum_class

    def rowCount(self, parent: _Index | None = None) -> int:
        return 0 if self._enum_class is None else len(self._enum_class)

    def data(self, index: _Index, role: int = ItemDataRole.DisplayRole) -> t.Any:
        if not index.isValid():
            return None
        if self._enum_class is None:
            return None

        enum_member = list(self._enum_class.__members__.values())[index.row()]

        if role == ItemDataRole.DisplayRole:
            return enum_member.name
        elif role == ItemDataRole.ToolTipRole:
            return enum_member.value
        elif role == ItemDataRole.UserRole:
            return enum_member
        elif role == ItemDataRole.DecorationRole:
            if "qcolor" in dir(enum_member):
                return enum_member.qcolor()

        return None


class EnumComboBox2(QtWidgets.QComboBox):
    def __init__(self, enum_class: t.Type[enum.Enum], parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self._enum_class = enum_class
        self.setModel(EnumModel(enum_class))

    def current_enum(self) -> enum.Enum:
        return self._enum_class(self.currentData())

    def set_current_enum(self, value: enum.Enum) -> None:
        self.setCurrentText(value.name)


class EnumComboBox(qfw.ComboBox):
    sig_current_enum_changed: t.ClassVar[QtCore.Signal] = QtCore.Signal(object)

    def __init__(
        self, enum_class: enum.EnumMeta | None = None, allow_none: bool = False, parent: QtWidgets.QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self._enum_class: t.Type[enum.Enum] | None = None
        self._allow_none = allow_none
        if enum_class is not None:
            self.set_enum_class(enum_class, allow_none)
        self.currentIndexChanged.connect(self._on_current_index_changed)

    def set_enum_class(self, enum_class: enum.EnumMeta | None, allow_none: bool = False) -> None:
        self.clear()
        self._enum_class = enum_class
        self._allow_none = allow_none and enum_class is not None
        if allow_none:
            super().addItem(NONE_STRING, userData=None)
        if enum_class is not None:
            if isinstance(enum_class, SVGColors):
                for svg_color in enum_class:
                    super().addItem(svg_color.name, icon=svg_color.qicon(), userData=svg_color.value)
            else:
                for name, value in enum_class.__members__.items():
                    super().addItem(name, userData=value)

    def enum_class(self) -> t.Type[enum.Enum] | None:
        return self._enum_class

    def clear(self) -> None:
        self._enum_class = None
        self._allow_none = False
        super().clear()

    def current_enum(self) -> enum.Enum | None:
        if self._enum_class is not None:
            if self._allow_none and self.currentText() == NONE_STRING:
                return None

            return self._enum_class(self.currentData())
        return None

    def set_current_enum(self, value: enum.Enum | None) -> None:
        if self._enum_class is None:
            raise RuntimeError("Uninitialized enum class. Use `set_enum_class` before `set_current_enum`.")

        if value is None:
            if not self._allow_none:
                raise ValueError(
                    "Value cannot be None. Set `allow_none` to True when initializing the enum class to enable this."
                )

            self.setCurrentIndex(0)
            return
        if not isinstance(value, self._enum_class):
            raise TypeError(f"Expected {self._enum_class} but got {type(value)}.")

        self.setCurrentText(value.name)

    @QtCore.Slot(int)
    def _on_current_index_changed(self, index: int) -> None:
        if self._enum_class is not None:
            self.sig_current_enum_changed.emit(self.current_enum())

    def insertItems(self, *args: t.Any, **kwargs: t.Any) -> None:
        raise NotImplementedError("Not implemented for enum type.")

    def insertItem(self, *args: t.Any, **kwargs: t.Any) -> None:
        raise NotImplementedError("Not implemented for enum type.")

    def addItems(self, *args: t.Any, **kwargs: t.Any) -> None:
        raise NotImplementedError("Not implemented for enum type.")

    def addItem(self, *args: t.Any, **kwargs: t.Any) -> None:
        raise NotImplementedError("Not implemented for enum type.")

    def setInsertPolicy(self, policy: QtWidgets.QComboBox.InsertPolicy) -> None:
        raise NotImplementedError("Not implemented for enum type.")


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

        if isinstance(initial_value, (RateComputationMethod, TextFileSeparator)):
            editor = EnumComboBox2(initial_value.__class__, parent=parent)
        elif isinstance(initial_value, bool):
            editor = None
        elif isinstance(initial_value, int):
            editor = QtWidgets.QSpinBox(parent)
            editor.setMinimum(0)
        elif isinstance(initial_value, float):
            editor = QtWidgets.QDoubleSpinBox(parent)
            editor.setMinimum(0)
        elif isinstance(initial_value, QtGui.QColor):
            editor = EnumComboBox2(SVGColors, parent=parent)
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

        if isinstance(editor, EnumComboBox2):
            if isinstance(initial_value, QtGui.QColor):
                initial_value = SVGColors(initial_value.name())
            editor.set_current_enum(initial_value)
        elif isinstance(editor, (QtWidgets.QSpinBox, QtWidgets.QDoubleSpinBox)):
            editor.setValue(initial_value)
        else:
            super().setEditorData(editor, index)

    def setModelData(self, editor: QtWidgets.QWidget, model: QtCore.QAbstractItemModel, index: _Index) -> None:
        value = None
        if isinstance(editor, EnumComboBox2):
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
