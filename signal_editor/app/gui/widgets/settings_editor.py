import contextlib
import typing as t

from PySide6 import QtCore, QtGui, QtWidgets


class TypeChecker:
    def __init__(self) -> None:
        self.bool_expr = QtCore.QRegularExpression("^(true)|(false)$")
        assert self.bool_expr.isValid()
        self.bool_expr.setPatternOptions(
            QtCore.QRegularExpression.PatternOption.CaseInsensitiveOption
        )

        self.byte_array_expr = QtCore.QRegularExpression(r"^[\x00-\xff]*$")
        assert self.byte_array_expr.isValid()

        self.char_expr = QtCore.QRegularExpression("^.$")
        assert self.char_expr.isValid()

        self.int_expr = QtCore.QRegularExpression(r"^[+-]?\d+$")
        assert self.int_expr.isValid()

        self.color_expr = QtCore.QRegularExpression(r"^\(([0-9]*),([0-9]*),([0-9]*),([0-9]*)\)$")
        assert self.color_expr.isValid()

        self.point_expr = QtCore.QRegularExpression(r"^\((-?[0-9]*),(-?[0-9]*)\)$")
        assert self.point_expr.isValid()

        self.rect_expr = QtCore.QRegularExpression(
            r"^\((-?[0-9]*),(-?[0-9]*),(-?[0-9]*),(-?[0-9]*)\)$"
        )
        assert self.rect_expr.isValid()

        self.size_expr = QtCore.QRegularExpression(self.point_expr)

        date_pattern = "([0-9]{,4})-([0-9]{,2})-([0-9]{,2})"
        self.date_expr = QtCore.QRegularExpression(f"^{date_pattern}$")
        assert self.date_expr.isValid()

        time_pattern = "([0-9]{,2}):([0-9]{,2}):([0-9]{,2})"
        self.time_expr = QtCore.QRegularExpression(f"^{time_pattern}$")
        assert self.time_expr.isValid()

        self.date_time_expr = QtCore.QRegularExpression(f"^{date_pattern}T{time_pattern}$")
        assert self.date_time_expr.isValid()

    def type_from_text(self, text: str) -> t.Type[bool | int] | None:
        if self.bool_expr.match(text).hasMatch():
            return bool
        elif self.int_expr.match(text).hasMatch():
            return int
        return None

    def create_validator(self, value: t.Any, parent: QtCore.QObject) -> QtGui.QValidator | None:
        if isinstance(value, bool):
            return QtGui.QRegularExpressionValidator(self.bool_expr, parent)
        if isinstance(value, float):
            return QtGui.QDoubleValidator(parent)
        if isinstance(value, int):
            return QtGui.QIntValidator(parent)
        if isinstance(value, QtCore.QByteArray):
            return QtGui.QRegularExpressionValidator(self.byte_array_expr, parent)
        if isinstance(value, QtGui.QColor):
            return QtGui.QRegularExpressionValidator(self.color_expr, parent)
        if isinstance(value, QtCore.QDate):
            return QtGui.QRegularExpressionValidator(self.date_expr, parent)
        if isinstance(value, QtCore.QTime):
            return QtGui.QRegularExpressionValidator(self.time_expr, parent)
        if isinstance(value, QtCore.QDateTime):
            return QtGui.QRegularExpressionValidator(self.date_time_expr, parent)
        if isinstance(value, QtCore.QPoint):
            return QtGui.QRegularExpressionValidator(self.point_expr, parent)
        if isinstance(value, QtCore.QRect):
            return QtGui.QRegularExpressionValidator(self.rect_expr, parent)
        if isinstance(value, QtCore.QSize):
            return QtGui.QRegularExpressionValidator(self.size_expr, parent)
        return None

    def from_string(self, text: str, original_value: t.Any) -> t.Any:
        if isinstance(original_value, QtGui.QColor):
            match = self.color_expr.match(text)
            return QtGui.QColor(
                min(int(match.captured(1)), 255),
                min(int(match.captured(2)), 255),
                min(int(match.captured(3)), 255),
                min(int(match.captured(4)), 255),
            )
        if isinstance(original_value, QtCore.QDate):
            value = QtCore.QDate.fromString(text, QtCore.Qt.DateFormat.ISODate)
            return value if value.isValid() else None
        if isinstance(original_value, QtCore.QTime):
            value = QtCore.QTime.fromString(text, QtCore.Qt.DateFormat.ISODate)
            return value if value.isValid() else None
        if isinstance(original_value, QtCore.QDateTime):
            value = QtCore.QDateTime.fromString(text, QtCore.Qt.DateFormat.ISODate)
            return value if value.isValid() else None
        if isinstance(original_value, QtCore.QPoint):
            match = self.point_expr.match(text)
            return QtCore.QPoint(int(match.captured(1)), int(match.captured(2)))
        if isinstance(original_value, QtCore.QRect):
            match = self.rect_expr.match(text)
            return QtCore.QRect(
                int(match.captured(1)),
                int(match.captured(2)),
                int(match.captured(3)),
                int(match.captured(4)),
            )
        if isinstance(original_value, QtCore.QSize):
            match = self.size_expr.match(text)
            return QtCore.QSize(int(match.captured(1)), int(match.captured(2)))
        if isinstance(original_value, list):
            return text.split(",")
        return type(original_value)(text)


class VariantDelegate(QtWidgets.QItemDelegate):
    def __init__(self, type_checker: TypeChecker, parent: QtCore.QObject | None = None) -> None:
        super().__init__(parent)
        self._type_checker = type_checker

    def paint(
        self,
        painter: QtGui.QPainter,
        option: QtWidgets.QStyleOptionViewItem,
        index: QtCore.QModelIndex | QtCore.QPersistentModelIndex,
    ) -> None:
        if index.column() == 2:
            value = index.model().data(index, QtCore.Qt.ItemDataRole.UserRole)
            if not self.is_supported_type(value):
                my_option = QtWidgets.QStyleOptionViewItem(option)
                my_option.state &= ~QtWidgets.QStyle.StateFlag.State_Enabled  # pyright: ignore[reportAttributeAccessIssue]
                super(VariantDelegate, self).paint(painter, my_option, index)
                return

        super(VariantDelegate, self).paint(painter, option, index)

    def createEditor(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        parent: QtWidgets.QWidget,
        option: QtWidgets.QStyleOptionViewItem,
        index: QtCore.QModelIndex | QtCore.QPersistentModelIndex,
    ) -> QtWidgets.QWidget | None:
        if index.column() != 2:
            return None

        original_value = index.model().data(index, QtCore.Qt.ItemDataRole.UserRole)
        if not self.is_supported_type(original_value):
            return None

        editor = None
        if isinstance(original_value, bool):
            editor = QtWidgets.QCheckBox(parent)
        if isinstance(original_value, int):
            editor = QtWidgets.QSpinBox(parent)
            editor.setRange(-32767, 32767)
        else:
            editor = QtWidgets.QLineEdit(parent)
            editor.setFrame(False)
            if validator := self._type_checker.create_validator(original_value, editor):
                editor.setValidator(validator)
        return editor

    def setEditorData(
        self, editor: QtWidgets.QWidget, index: QtCore.QModelIndex | QtCore.QPersistentModelIndex
    ) -> None:
        if not editor:
            return

        value = index.model().data(index, QtCore.Qt.ItemDataRole.UserRole)
        if isinstance(editor, QtWidgets.QCheckBox):
            editor.setCheckState(
                QtCore.Qt.CheckState.Checked if value else QtCore.Qt.CheckState.Unchecked
            )
        elif isinstance(editor, QtWidgets.QSpinBox):
            editor.setValue(value)
        elif isinstance(editor, QtWidgets.QLineEdit):
            editor.setText(self.display_text(value))
        else:
            raise ValueError(f"Unsupported editor type: {type(editor)}")

    def value_from_lineedit(
        self,
        lineedit: QtWidgets.QLineEdit,
        model: QtCore.QAbstractItemModel,
        index: QtCore.QModelIndex | QtCore.QPersistentModelIndex,
    ) -> t.Any:
        if not lineedit.isModified():
            return None
        text = lineedit.text()
        validator = lineedit.validator()

        if validator is not None:  # pyright: ignore[reportUnnecessaryComparison]
            state, text, _ = validator.validate(text, 0)  # pyright: ignore[reportGeneralTypeIssues, reportUnknownVariableType]
            if state != QtGui.QValidator.State.Acceptable:
                return None

        original_value = index.model().data(index, QtCore.Qt.ItemDataRole.UserRole)
        return self._type_checker.from_string(text, original_value)  # pyright: ignore[reportUnknownArgumentType]

    def setModelData(
        self,
        editor: QtWidgets.QWidget,
        model: QtCore.QAbstractItemModel,
        index: QtCore.QModelIndex | QtCore.QPersistentModelIndex,
    ) -> None:
        value = None
        if isinstance(editor, QtWidgets.QCheckBox):
            value = editor.checkState() == QtCore.Qt.CheckState.Checked
        elif isinstance(editor, QtWidgets.QSpinBox):
            value = editor.value()
        elif isinstance(editor, QtWidgets.QLineEdit):
            value = self.value_from_lineedit(editor, model, index)
        else:
            raise ValueError(f"Unsupported editor type: {type(editor)}")

        if value is not None:
            model.setData(index, value, QtCore.Qt.ItemDataRole.UserRole)
            model.setData(index, self.display_text(value), QtCore.Qt.ItemDataRole.DisplayRole)

    @staticmethod
    def is_supported_type(value: t.Any) -> bool:
        return isinstance(
            value,
            (
                bool,
                int,
                float,
                str,
                QtCore.QByteArray,
                QtGui.QColor,
                QtCore.QDate,
                QtCore.QTime,
                QtCore.QDateTime,
                QtCore.QPoint,
                QtCore.QRect,
                QtCore.QSize,
                list,
            ),
        )

    @staticmethod
    def display_text(value: t.Any) -> str:
        if isinstance(value, str):
            return value
        if isinstance(value, bool):
            return "✓" if value else "☐"
        if isinstance(value, (int, float, QtCore.QByteArray)):
            return str(value)
        if isinstance(value, QtGui.QColor):
            (r, g, b, a) = (value.red(), value.green(), value.blue(), value.alpha())
            return f"({r},{g},{b},{a})"
        if isinstance(value, (QtCore.QDate, QtCore.QTime, QtCore.QDateTime)):
            return value.toString(QtCore.Qt.DateFormat.ISODate)
        if isinstance(value, QtCore.QPoint):
            x, y = value.x(), value.y()
            return f"({x},{y})"
        if isinstance(value, QtCore.QRect):
            x, y, w, h = value.x(), value.y(), value.width(), value.height()
            return f"({x},{y},{w},{h})"
        if isinstance(value, QtCore.QSize):
            w, h = value.width(), value.height()
            return f"({w},{h})"
        if isinstance(value, list):
            return ", ".join(map(repr, value))  # pyright: ignore[reportUnknownArgumentType]
        return "<Invalid>" if value is None else f"<{value}>"


class SettingsTree(QtWidgets.QTreeWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self._type_checker = TypeChecker()
        self.setItemDelegate(VariantDelegate(self._type_checker, self))

        self.setColumnCount(4)
        self.setHeaderLabels(("Setting", "Type", "Value", "Description"))
        self.header().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.header().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.header().setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeMode.Stretch)

        self.settings: QtCore.QSettings | None = None
        self.refresh_timer = QtCore.QTimer()
        self.refresh_timer.setInterval(2000)
        self.auto_refresh = False

        self.group_icon = QtGui.QIcon()
        style = self.style()
        self.group_icon.addPixmap(
            style.standardPixmap(QtWidgets.QStyle.StandardPixmap.SP_DirClosedIcon),
            QtGui.QIcon.Mode.Normal,
            QtGui.QIcon.State.Off,
        )
        self.group_icon.addPixmap(
            style.standardPixmap(QtWidgets.QStyle.StandardPixmap.SP_DirOpenIcon),
            QtGui.QIcon.Mode.Normal,
            QtGui.QIcon.State.On,
        )
        self.key_icon = QtGui.QIcon()
        self.key_icon.addPixmap(style.standardPixmap(QtWidgets.QStyle.StandardPixmap.SP_FileIcon))

        self.refresh_timer.timeout.connect(self.maybe_refresh)

    def set_settings_object(self, settings: QtCore.QSettings | None) -> None:
        self.settings = settings
        self.clear()

        if self.settings is not None:
            self.settings.setParent(self)
            self.refresh()
            if self.auto_refresh:
                self.refresh_timer.start()
        else:
            self.refresh_timer.stop()

    def sizeHint(self) -> QtCore.QSize:
        return QtCore.QSize(800, 600)

    @QtCore.Slot(bool)
    def set_auto_refresh(self, auto_refresh: bool) -> None:
        self.auto_refresh = auto_refresh

        if self.settings is not None:
            if self.auto_refresh:
                self.maybe_refresh()
                self.refresh_timer.start()
            else:
                self.refresh_timer.stop()

    @QtCore.Slot()
    def maybe_refresh(self) -> None:
        if self.state() != QtWidgets.QAbstractItemView.State.EditingState:
            self.refresh()

    @QtCore.Slot()
    def refresh(self) -> None:
        if self.settings is None:
            return

        with contextlib.suppress(Exception):
            self.itemChanged.disconnect(self.update_setting)

        self.settings.sync()
        self.update_child_items(None)

        self.itemChanged.connect(self.update_setting)

    def event(self, e: QtCore.QEvent) -> bool:
        if e.type() == QtCore.QEvent.Type.WindowActivate and (
            self.isActiveWindow() and self.auto_refresh
        ):
            self.maybe_refresh()

        return super(SettingsTree, self).event(e)

    def update_setting(self, item: QtWidgets.QTreeWidgetItem) -> None:
        key = item.text(0)
        ancestor = item.parent()

        while ancestor:
            key = f"{ancestor.text(0)}/{key}"
            ancestor = ancestor.parent()

        if self.settings is not None:
            self.settings.setValue(key, item.data(2, QtCore.Qt.ItemDataRole.UserRole))

        if self.auto_refresh:
            self.refresh()

    def update_child_items(self, parent: QtWidgets.QTreeWidgetItem | None) -> None:
        divider_index = 0
        if self.settings is None:
            return

        for group in self.settings.childGroups():
            child_index = self.find_child(parent, group, divider_index)
            if child_index != -1:
                child = self.child_at(parent, child_index)
                child.setText(1, "")
                child.setText(2, "")
                child.setText(3, "")
                child.setData(2, QtCore.Qt.ItemDataRole.UserRole, None)
                self.move_item_forward(parent, child_index, divider_index)
            else:
                child = self.create_item(group, parent, divider_index)

            child.setIcon(0, self.group_icon)
            divider_index += 1

            self.settings.beginGroup(group)
            self.update_child_items(child)
            self.settings.endGroup()

        for key in self.settings.childKeys():
            child_index = self.find_child(parent, key, 0)
            if child_index == -1:
                child = self.create_item(key, parent, divider_index)
                child.setIcon(0, self.key_icon)
                divider_index += 1
            elif child_index >= divider_index:
                child = self.child_at(parent, child_index)
                for i in range(child.childCount()):
                    self.delete_item(child, i)
                self.move_item_forward(parent, child_index, divider_index)
                child.setIcon(0, self.key_icon)
                divider_index += 1
            else:
                child = self.child_at(parent, child_index)

            value = self.settings.value(key)
            if value is None:
                child.setText(1, "Invalid")
            else:
                # Try to convert to type unless a QByteArray is received
                if isinstance(value, str):
                    if value_type := self._type_checker.type_from_text(value):
                        value = self.settings.value(key, type=value_type)
                child.setText(1, value.__class__.__name__)
            child.setText(2, VariantDelegate.display_text(value))
            child.setData(2, QtCore.Qt.ItemDataRole.UserRole, value)

        while divider_index < self.child_count(parent):
            self.delete_item(parent, divider_index)

    def create_item(
        self, text: str, parent: QtWidgets.QTreeWidgetItem | None, index: int
    ) -> QtWidgets.QTreeWidgetItem:
        after = self.child_at(parent, index - 1) if index != 0 else None
        if parent is not None:
            item = QtWidgets.QTreeWidgetItem(parent, after)  # pyright: ignore[reportCallIssue, reportArgumentType]
        else:
            item = QtWidgets.QTreeWidgetItem(self, after)  # pyright: ignore[reportCallIssue, reportArgumentType]

        item.setText(0, text)
        item.setFlags(item.flags() | QtCore.Qt.ItemFlag.ItemIsEditable)
        return item

    def delete_item(self, parent: QtWidgets.QTreeWidgetItem | None, index: int) -> None:
        if parent is not None:
            item = parent.takeChild(index)
        else:
            item = self.takeTopLevelItem(index)
        del item

    def child_at(
        self, parent: QtWidgets.QTreeWidgetItem | None, index: int
    ) -> QtWidgets.QTreeWidgetItem:
        return parent.child(index) if parent is not None else self.topLevelItem(index)

    def child_count(self, parent: QtWidgets.QTreeWidgetItem | None) -> int:
        return parent.childCount() if parent is not None else self.topLevelItemCount()

    def find_child(
        self, parent: QtWidgets.QTreeWidgetItem | None, text: str, start_index: int
    ) -> int:
        return next(
            (
                i
                for i in range(self.child_count(parent))
                if self.child_at(parent, i).text(0) == text
            ),
            -1,
        )

    def move_item_forward(
        self, parent: QtWidgets.QTreeWidgetItem | None, old_index: int, new_index: int
    ) -> None:
        for _ in range(old_index - new_index):
            self.delete_item(parent, new_index)


class SettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self.setWindowTitle("Settings")
        self.setMinimumSize(800, 600)

        self.settings_tree = SettingsTree(self)
        # Populate the settings tree with the application settings
        self.settings_tree.set_settings_object(QtCore.QSettings())
        self.settings_tree.set_auto_refresh(True)

        # self.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)

        toolbar = QtWidgets.QToolBar()

        toolbar.addAction(QtGui.QIcon(":/icons/refresh"), "Refresh", self.settings_tree.refresh)

        auto_refresh_action = QtGui.QAction(
            QtGui.QIcon(":/icons/auto_refresh"), "Auto Refresh", toolbar
        )
        auto_refresh_action.setCheckable(True)
        auto_refresh_action.toggled.connect(self.settings_tree.set_auto_refresh)
        toolbar.addAction(auto_refresh_action)

        toolbar.addAction(QtGui.QIcon(":/icons/delete"), "Delete", self.settings_tree.delete_item)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(toolbar)
        layout.addWidget(self.settings_tree)
