import contextlib
import os
import typing as t

import pyqtgraph as pg
from PySide6 import QtCore, QtGui, QtWidgets
from qfluentwidgets import CommandBar, MessageBox, TreeWidget, TreeItemDelegate

from ... import type_defs as _t
from ...controllers.data_controller import TextFileSeparator
from ...enum_defs import RateComputationMethod
from ...utils import get_app_dir, make_qcolor, safe_disconnect
from ..icons import FluentIcon as FI
from ._qt_type_checker import TypeChecker


class VariantDelegate(TreeItemDelegate):
    def __init__(self, type_checker: TypeChecker, parent: QtWidgets.QTreeView) -> None:
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

        super().paint(painter, option, index)

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
            value = editor.isChecked()
        elif isinstance(editor, QtWidgets.QSpinBox):
            value = editor.value()
        elif isinstance(editor, QtWidgets.QDateEdit):
            value = editor.date()
        elif isinstance(editor, QtWidgets.QTimeEdit):
            value = editor.time()
        elif isinstance(editor, QtWidgets.QDateTimeEdit):
            value = editor.dateTime()
        elif isinstance(editor, pg.ColorButton):
            value = editor.color("qcolor")
        elif isinstance(editor, QtWidgets.QLineEdit):
            value = self.value_from_lineedit(editor, model, index)

        if isinstance(value, (QtCore.QDate, QtCore.QTime, QtCore.QDateTime)):
            model.setData(index, value, QtCore.Qt.ItemDataRole.UserRole)
            model.setData(
                index,
                value.toString(QtCore.Qt.DateFormat.ISODate),
                QtCore.Qt.ItemDataRole.DisplayRole,
            )
        elif isinstance(value, QtGui.QColor):
            model.setData(index, value, QtCore.Qt.ItemDataRole.UserRole)
            model.setData(index, value.name(), QtCore.Qt.ItemDataRole.DisplayRole)
        elif isinstance(value, QtCore.QDir):
            model.setData(index, value, QtCore.Qt.ItemDataRole.UserRole)
            model.setData(index, value.canonicalPath(), QtCore.Qt.ItemDataRole.DisplayRole)
        elif value is not None:
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
                tuple,
            ),
        )

    @staticmethod
    def display_text(value: t.Any) -> str:
        if isinstance(value, str):
            if value in {" ", "\t", ";", ",", "|"}:
                return TextFileSeparator(value).name
            if value in {"instantaneous", "rolling_window", "rolling_window_no_overlap"}:
                return RateComputationMethod(value).name
            return value
        if isinstance(value, bool):
            return "True" if value else "False"
        if isinstance(value, QtCore.QByteArray):
            return "<Binary data>"
        if isinstance(value, (int, float)):
            return str(value)
        if isinstance(value, QtGui.QColor):
            return value.name()
        if isinstance(value, (QtCore.QDate, QtCore.QTime, QtCore.QDateTime)):
            return value.toString("yyyy-MM-dd HH:mm:ss.zzz")
        if isinstance(value, QtCore.QPoint):
            return f"Point(x = {value.x()}, y = {value.y()})"
        if isinstance(value, QtCore.QRect):
            x, y, w, h = t.cast(tuple[int, int, int, int], value.getRect())
            return f"Rectangle(TopLeft = ({x = }, {y = }), Width = {w}, Height = {h})"
        if isinstance(value, QtCore.QSize):
            w, h = value.width(), value.height()
            return f"QSize(Width = {w}, Height = {h})"
        if isinstance(value, list):
            return ", ".join(map(repr, value))  # type: ignore
        if isinstance(value, tuple) and len(value) == 4:  # type: ignore
            try:
                c = make_qcolor(value)  # type: ignore
                return c.name()
            except Exception:
                return f"<{value}>"
        return "<Invalid>" if value is None else f"<{value}>"


class SettingsTree(TreeWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self.DEFAULT_VALUES: t.Final[_t.DefaultAppSettings] = _t.DefaultAppSettings(
            Plot=_t.DefaultPlotSettings(
                background_color=pg.mkColor("black"),
                foreground_color=pg.mkColor("lightgray"),
                point_color=pg.mkColor("darkgoldenrod"),
                signal_line_color=pg.mkColor("tomato"),
                rate_line_color=pg.mkColor("lightgreen"),
                section_marker_color=pg.mkColor((100, 200, 150, 40)),
            ),
            Editing=_t.DefaultEditingSettings(
                click_width_signal_line=70,
                search_around_click_radius=20,
                minimum_peak_distance=20,
                rate_computation_method=RateComputationMethod.RollingWindow,
                allow_stacking_filters=False,
            ),
            Data=_t.DefaultDataSettings(
                sampling_rate=400,
                txt_file_separator_character=TextFileSeparator.Tab,
                try_parse_dates=False,
            ),
            Misc=_t.DefaultMiscSettings(
                data_folder=get_app_dir(False).canonicalPath(),
                output_folder=get_app_dir(False).canonicalPath(),
                float_visual_precision=3,
                last_signal_column_name=None,
                last_info_column_name=None,
            ),
        )
        self.DESCRIPTIONS: t.Final[dict[str, str]] = {
            # "Plot": "Settings related to the interactive plots",
            "background_color": "The background color for the interactive plots",
            "foreground_color": "The foreground (text, axis, etc) color for the interactive plots",
            "point_color": "The fill color for the peak points in the upper plot",
            "signal_line_color": "The color for the signal line in the upper plot",
            "rate_line_color": "The color for the rate line in the lower plot",
            "section_marker_color": "The color used to highlight the created sections in the upper plot",
            # "Editing": "Settings related to the editing features",
            "click_width_signal_line": "The area around the signal line in pixels that is considered to be a click on the line",
            "search_around_click_radius": "The radius around the click in data coordinates to search for a potential peak",
            "minimum_peak_distance": "Sets the minimum allowed distance between two peaks when using any of the peak detection algorithms",
            "rate_computation_method": "Which method to use for computing the rate displayed in the lower plot on the editing page, either 'instantaneous' or 'rolling_window'",
            "allow_stacking_filters": "Whether to allow applying multiple filters to the same signal",
            # "Data": "Settings related to input data",
            "sampling_rate": "The default sampling rate (in Hz) to use in cases where it can't be inferred or is not provided in the data itself (for example, EDF files usually have the sampling rate in the file header)",
            "txt_file_separator_character": "The character used to separate columns if reading from a '.txt' file",
            "try_parse_dates": "Whether to try parsing dates in the data if reading from a '.txt', '.csv', or '.xlsx' file",
            # "Misc": "Settings that don't fit into any other category",
            "data_folder": "Which folder to open when selecting a data file",
            "output_folder": "Which folder to save the output files to",
            "float_visual_precision": "How many digits to use for displaying floating point (decimal) values",
            "last_signal_column_name": "The name of the signal column in the last loaded data file. If a new data file is loaded that has a column with this name, the signal column will be automatically selected",
            "last_info_column_name": "The name of the info column in the last loaded data file. If a new data file is loaded that has a column with this name, the info column will be automatically selected",
        }
        self.setBorderVisible(True)
        self.header().setDefaultAlignment(
            QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter
        )
        self.setUniformRowHeights(True)
        self.setTextElideMode(QtCore.Qt.TextElideMode.ElideRight)
        self.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self._type_checker = TypeChecker()
        self.setItemDelegate(VariantDelegate(self._type_checker, self))

        self.setColumnCount(4)
        self.setHeaderLabels(("Setting", "Type", "Value", "Description"))
        self.setEditTriggers(QtWidgets.QTreeWidget.EditTrigger.NoEditTriggers)
        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)

        self.settings: QtCore.QSettings | None = None
        self.refresh_timer = QtCore.QTimer()
        self.refresh_timer.setInterval(2000)
        self.auto_refresh = False

        self.refresh_timer.timeout.connect(self.maybe_refresh)
        self.itemExpanded.connect(self._resize_columns)

    @QtCore.Slot(QtWidgets.QTreeWidgetItem)
    def _resize_columns(self, item: QtWidgets.QTreeWidgetItem) -> None:
        self.resizeColumnToContents(0)
        self.resizeColumnToContents(1)
        self.setColumnWidth(2, 200)

    def set_settings_object(self, settings: QtCore.QSettings | None) -> None:
        self.settings = settings
        self.clear()

        if self.settings is not None:
            # Check if all default values exist in the settings, if not add the missing ones
            for group, default_values in self.DEFAULT_VALUES.items():
                for setting_key, default_value in default_values.items():  # type: ignore
                    setting_key = f"{group}/{setting_key}"
                    if not self.settings.contains(setting_key):
                        self.settings.setValue(setting_key, default_value)
            self.settings.setParent(self)
            self.refresh()
            if self.auto_refresh:
                self.refresh_timer.start()

        else:
            self.refresh_timer.stop()

    def sizeHint(self) -> QtCore.QSize:
        return QtCore.QSize(600, 400)

    @QtCore.Slot()
    def restore_defaults(self) -> None:
        if self.settings is None:
            return

        msg_box = MessageBox(
            "Restore default settings?",
            "Are you sure you want to restore all settings to their default values?",
            parent=self.parent(),
        )
        sure = msg_box.exec()
        if not sure:
            return

        for grp, kvs in self.DEFAULT_VALUES.items():
            self.settings.remove(grp)
            self.settings.beginGroup(grp)
            for k, v in kvs.items():  # type: ignore
                if isinstance(v, QtCore.QDir):
                    v = v.canonicalPath()
                self.settings.setValue(k, v)  # type: ignore
            self.settings.endGroup()

        self.refresh()

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
        if self.state() != TreeWidget.State.EditingState:
            self.refresh()

    @QtCore.Slot()
    def refresh(self) -> None:
        if self.settings is None:
            return

        safe_disconnect(self, self.itemChanged, self.update_setting)

        self.settings.sync()
        self.update_child_items(None)

        self.itemChanged.connect(self.update_setting)

    def event(self, e: QtCore.QEvent) -> bool:
        if e.type() == QtCore.QEvent.Type.WindowActivate and (
            self.isActiveWindow() and self.auto_refresh
        ):
            self.maybe_refresh()

        return super().event(e)

    @QtCore.Slot(QtWidgets.QTreeWidgetItem)
    def update_setting(self, item: QtWidgets.QTreeWidgetItem) -> None:
        key = item.text(0)
        ancestor = item.parent()

        while ancestor:
            key = f"{ancestor.text(0)}/{key}"
            ancestor = ancestor.parent()

        if self.settings is not None:
            data = item.data(2, QtCore.Qt.ItemDataRole.UserRole)
            if isinstance(data, QtCore.QDir):
                data = data.canonicalPath()
            self.settings.setValue(key, data)

        if self.auto_refresh:
            self.refresh()

    def adjust_colors(self, child: QtWidgets.QTreeWidgetItem, value: _t.PGColor) -> None:
        color = make_qcolor(value)
        child.setBackground(2, color)
        if color.lightnessF() < 0.5:
            child.setForeground(2, QtGui.QBrush(QtGui.QColor(255, 255, 255)))
        else:
            child.setForeground(2, QtGui.QBrush(QtGui.QColor(0, 0, 0)))

    def update_child_items(self, parent: QtWidgets.QTreeWidgetItem | None) -> None:
        divider_index = 0
        if self.settings is None:
            return

        for group in self.settings.childGroups():
            if group == "Internal":
                continue
            child_index = self.find_child(parent, group, divider_index)
            if child_index != -1:
                child = self.child_at(parent, child_index)
                child.setText(1, "")
                child.setText(2, "")
                child.setData(2, QtCore.Qt.ItemDataRole.UserRole, None)
                self.move_item_forward(parent, child_index, divider_index)
            else:
                child = self.create_item(group, parent, divider_index)

            # child.setIcon(0, self.group_icon)
            divider_index += 1

            self.settings.beginGroup(group)
            self.update_child_items(child)
            self.settings.endGroup()

        for key in self.settings.childKeys():
            child_index = self.find_child(parent, key, 0)
            if child_index == -1:
                child = self.create_item(key, parent, divider_index)
                # child.setIcon(0, self.determine_icon(key))
                divider_index += 1
            elif child_index >= divider_index:
                child = self.child_at(parent, child_index)
                for i in range(child.childCount()):
                    self.delete_item(child, i)
                self.move_item_forward(parent, child_index, divider_index)
                # child.setIcon(0, self.determine_icon(key))
                divider_index += 1
            else:
                child = self.child_at(parent, child_index)

            value = self.settings.value(key)
            if value is None:
                child.setText(1, "Invalid")
            else:
                # Try to convert to type unless a QByteArray is received
                if isinstance(value, str) and (
                    value_type := self._type_checker.type_from_text(value)
                ):
                    value = self.settings.value(key, type=value_type)
                child.setText(1, value.__class__.__name__)
            child.setText(2, VariantDelegate.display_text(value))
            child.setData(2, QtCore.Qt.ItemDataRole.UserRole, value)
            child.setText(3, self.DESCRIPTIONS.get(key, ""))
            if "color" in key or isinstance(value, QtGui.QColor):
                with contextlib.suppress(Exception):
                    self.adjust_colors(child, value)  # type: ignore

        while divider_index < self.child_count(parent):
            self.delete_item(parent, divider_index)

    def create_item(
        self,
        text: str,
        parent: QtWidgets.QTreeWidgetItem | None = None,
        index: int = 0,
        description: str | None = None,
    ) -> QtWidgets.QTreeWidgetItem:
        after = self.child_at(parent, index - 1) if index != 0 else None
        target = parent if parent is not None else self
        item = (
            QtWidgets.QTreeWidgetItem(target, after)
            if after is not None
            else QtWidgets.QTreeWidgetItem(target)
        )

        item.setText(0, text)
        if description is not None:
            item.setText(3, description)
        return item

    def delete_item(self, parent: QtWidgets.QTreeWidgetItem | None, index: int) -> None:
        if parent is not None:
            item = parent.takeChild(index)
            if self.settings is not None:
                self.settings.remove(f"{parent.text(0)}/{item.text(0)}")
        else:
            item = self.takeTopLevelItem(index)
            if self.settings is not None:
                self.settings.remove(item.text(0))
        del item

    @QtCore.Slot()
    def delete_current_item(self) -> None:
        msg_box = MessageBox(
            "Delete?", "Are you sure you want to delete this item?", parent=self.parent()
        )
        sure = msg_box.exec()

        if not sure:
            return

        item = self.currentItem()
        if item.parent():
            self.delete_item(item.parent(), item.parent().indexOfChild(item))
        else:
            self.delete_item(None, self.indexOfTopLevelItem(item))

    @QtCore.Slot()
    def reset_current_item(self) -> None:
        item = self.currentItem()
        key = item.text(0)
        if not item.parent():
            return

        default_value = self.DEFAULT_VALUES[item.parent().text(0)][key]  # type: ignore
        if isinstance(default_value, QtCore.QDir):
            default_value = default_value.canonicalPath()
        item.setData(2, QtCore.Qt.ItemDataRole.UserRole, default_value)
        item.setText(2, VariantDelegate.display_text(default_value))
        self.update_setting(item)

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
    sig_setting_changed = QtCore.Signal(str, object)

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self._type_handlers: dict[
            str, t.Callable[[QtWidgets.QTreeWidgetItem], QtGui.QColor | str | int | float | None]
        ] = {
            "QColor": self._handle_qcolor,
            "str": self._handle_str,
            "int": self._handle_int,
            "float": self._handle_float,
            "bool": self._handle_bool,
        }
        # self.setVisible(False)

        # self.setTitleBar(StandardTitleBar(self))
        self.setWindowTitle("Settings")
        self.setWindowIcon(FI.Settings.icon())
        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok
            | QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        self.settings_tree = SettingsTree(self)
        # Populate the settings tree with the application settings
        settings = QtCore.QSettings()
        self.settings_tree.set_settings_object(settings)

        toolbar = CommandBar(self)

        action_reset_selected_item = QtGui.QAction(FI.ArrowReset.icon(), "Reset Selected", self)
        action_reset_selected_item.triggered.connect(self.settings_tree.reset_current_item)

        if os.environ.get("DEBUG", "0") == "1":
            action_delete_selected_item = QtGui.QAction(FI.Delete.icon(), "Delete Selected", self)
            action_delete_selected_item.triggered.connect(self.settings_tree.delete_current_item)
            toolbar.addAction(action_delete_selected_item)

        action_restore_defaults = QtGui.QAction(
            FI.TabDesktopArrowClockwise.icon(), "Restore Original Values", self
        )
        action_restore_defaults.triggered.connect(self.settings_tree.restore_defaults)

        action_edit_selected_item_value = QtGui.QAction(
            FI.EditSettings.icon(), "Edit Selected Item Value", self
        )
        action_edit_selected_item_value.triggered.connect(
            lambda: self._on_edit_selected_item_value(self.settings_tree.currentItem())
        )
        action_refresh_settings = QtGui.QAction(FI.ArrowSync.icon(), "Refresh", self)
        action_refresh_settings.triggered.connect(self.settings_tree.refresh)

        toolbar.addAction(action_reset_selected_item)
        toolbar.addAction(action_restore_defaults)
        toolbar.addAction(action_refresh_settings)
        toolbar.addAction(action_edit_selected_item_value)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(self.settings_tree)
        layout.addWidget(buttons)

        self.setLayout(layout)
        self.connect_signals()

    def connect_signals(self) -> None:
        self.settings_tree.itemDoubleClicked.connect(self._on_edit_selected_item_value)
        self.settings_tree.customContextMenuRequested.connect(self.show_context_menu)

    @QtCore.Slot(QtCore.QPoint)
    def show_context_menu(self, pos: QtCore.QPoint) -> None:
        menu = QtWidgets.QMenu(self)
        menu.addAction("Reset Selected", self.settings_tree.reset_current_item)
        menu.addAction("Restore Defaults", self.settings_tree.restore_defaults)
        if os.environ.get("DEBUG", "0") == "1":
            menu.addAction("Delete Selected", self.settings_tree.delete_current_item)
        menu.addAction("Refresh", self.settings_tree.refresh)
        menu.exec(self.settings_tree.mapToGlobal(pos))

    @QtCore.Slot()
    def accept(self) -> None:
        self.settings_tree.refresh()
        super().accept()

    def get_color(self, initial: QtGui.QColor) -> QtGui.QColor | None:
        val = QtWidgets.QColorDialog.getColor(
            initial, self, "Select Color", QtWidgets.QColorDialog.ColorDialogOption.ShowAlphaChannel
        )
        return val if val.isValid() else None

    def get_directory(self, initial: str) -> str | None:
        val, _ = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory", initial)
        return val or None

    def get_text(self, initial: str) -> str:
        val, ok = QtWidgets.QInputDialog.getText(
            self,
            "Edit Setting",
            "Enter new value:",
            QtWidgets.QLineEdit.EchoMode.Normal,
            initial,
        )
        return val if ok else initial

    def get_int(
        self, initial: int, min_allowed: int = -10_000_000, max_allowed: int = 10_000_000
    ) -> int:
        val, ok = QtWidgets.QInputDialog.getInt(
            self,
            "Edit Setting",
            "Enter new value:",
            initial,
            min_allowed,
            max_allowed,
        )
        return val if ok else initial

    def get_float(
        self, initial: float, min_allowed: float = -10e6, max_allowed: float = 10e6
    ) -> float:
        val, ok = QtWidgets.QInputDialog.getDouble(
            self,
            "Edit Setting",
            "Enter new value:",
            initial,
            min_allowed,
            max_allowed,
        )
        return val if ok else initial

    @QtCore.Slot(QtWidgets.QTreeWidgetItem)
    def _on_edit_selected_item_value(self, item: QtWidgets.QTreeWidgetItem) -> None:
        handler = self._type_handlers.get(item.text(1), self._handle_default)
        new_value = handler(item)
        if new_value is not None:
            self.sig_setting_changed.emit(item.text(0), new_value)
            self.settings_tree.refresh()

    def _handle_qcolor(self, item: QtWidgets.QTreeWidgetItem) -> QtGui.QColor:
        new_value = self.get_color(item.data(2, QtCore.Qt.ItemDataRole.UserRole))
        if new_value is not None:
            item.setData(2, QtCore.Qt.ItemDataRole.UserRole, new_value)
            item.setText(2, new_value.name())
            item.setBackground(2, new_value)

        return new_value or item.data(2, QtCore.Qt.ItemDataRole.UserRole)

    def _handle_str(self, item: QtWidgets.QTreeWidgetItem) -> str:
        setting_name = item.text(0)
        if setting_name in {"data_folder", "output_folder"}:
            if new_value := QtWidgets.QFileDialog.getExistingDirectory(
                self, "Select Directory", item.data(2, QtCore.Qt.ItemDataRole.UserRole)
            ):
                item.setData(2, QtCore.Qt.ItemDataRole.UserRole, new_value)
                item.setText(2, new_value)
        elif setting_name == "rate_computation_method":
            items = [RateComputationMethod(c).value for c in RateComputationMethod]
            current_value = item.data(2, QtCore.Qt.ItemDataRole.UserRole)
            new_value, ok = QtWidgets.QInputDialog.getItem(
                self,
                "Edit Setting",
                "Select Method",
                items,
                items.index(current_value),
                False,
            )
            if ok and new_value:
                item.setData(2, QtCore.Qt.ItemDataRole.UserRole, new_value)
                item.setText(2, new_value)
        elif setting_name == "txt_file_separator_character":
            items = [TextFileSeparator(c).name for c in TextFileSeparator]
            current_value = TextFileSeparator(item.data(2, QtCore.Qt.ItemDataRole.UserRole)).name
            new_value, ok = QtWidgets.QInputDialog.getItem(
                self,
                "Edit Setting",
                "Select Character",
                items,
                items.index(current_value),
                False,
            )
            if ok and new_value:
                item.setData(2, QtCore.Qt.ItemDataRole.UserRole, TextFileSeparator[new_value].value)
                item.setText(2, new_value)
        else:
            new_value = self.get_text(item.data(2, QtCore.Qt.ItemDataRole.UserRole))
            item.setData(2, QtCore.Qt.ItemDataRole.UserRole, new_value)
            item.setText(2, new_value)

        return new_value

    def _handle_int(self, item: QtWidgets.QTreeWidgetItem) -> int:
        setting_name = item.text(0)
        if setting_name in {
            "click_width_signal_line",
            "search_around_click_radius",
            "minimum_peak_distance",
        }:
            new_value = self.get_int(item.data(2, QtCore.Qt.ItemDataRole.UserRole), 5, 10_000)
        else:
            new_value = self.get_int(item.data(2, QtCore.Qt.ItemDataRole.UserRole))
        item.setData(2, QtCore.Qt.ItemDataRole.UserRole, new_value)
        item.setText(2, str(new_value))

        return new_value

    def _handle_float(self, item: QtWidgets.QTreeWidgetItem) -> float:
        setting_name = item.text(0)
        if setting_name == "sampling_rate":
            new_value = self.get_float(item.data(2, QtCore.Qt.ItemDataRole.UserRole), 1, 100_000)
        else:
            new_value = self.get_float(item.data(2, QtCore.Qt.ItemDataRole.UserRole))

        item.setData(2, QtCore.Qt.ItemDataRole.UserRole, new_value)
        item.setText(2, str(new_value))

        return new_value

    def _handle_bool(self, item: QtWidgets.QTreeWidgetItem) -> bool:
        options = ("True", "False")
        new_value, ok = QtWidgets.QInputDialog.getItem(
            self,
            "Edit Setting",
            "Select new value:",
            options,
            options.index(str(item.data(2, QtCore.Qt.ItemDataRole.UserRole))),
            False,
        )
        if ok and new_value:
            item.setData(2, QtCore.Qt.ItemDataRole.UserRole, bool(new_value))
            item.setText(2, new_value)

        return bool(new_value)

    def _handle_default(self, item: QtWidgets.QTreeWidgetItem) -> None:
        QtWidgets.QMessageBox.warning(
            self,
            "Cannot Edit Directly",
            "This item cannot be edited directly.",
        )
