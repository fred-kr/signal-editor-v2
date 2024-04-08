import contextlib
import enum
import os
import typing as t

import pyqtgraph as pg
from PySide6 import QtCore, QtGui, QtWidgets

from ... import type_defs as _t
from ...controllers.data_controller import TextFileSeparator


def mkColor(*args: _t.PGColor) -> QtGui.QColor:
    return args[0] if isinstance(args[0], QtGui.QColor) else pg.mkColor(*args)


class RateComputationMethod(enum.StrEnum):
    Instantaneous = "instantaneous"
    RollingWindow = "rolling_window"


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

        self.directory_expr = QtCore.QRegularExpression(
            r"^([a-zA-Z]:\\)?((?:[^\\/:*?\"<>|\r\n]+\\?)*)$"
        )
        assert self.directory_expr.isValid()

    def type_from_text(
        self, text: str
    ) -> (
        t.Type[
            bool
            | int
            | QtCore.QByteArray
            | QtGui.QColor
            | QtCore.QDate
            | QtCore.QTime
            | QtCore.QDateTime
            | QtCore.QDir
        ]
        | None
    ):
        if self.bool_expr.match(text).hasMatch():
            return bool
        elif self.int_expr.match(text).hasMatch():
            return int
        elif self.byte_array_expr.match(text).hasMatch():
            return QtCore.QByteArray
        elif self.color_expr.match(text).hasMatch():
            return QtGui.QColor
        elif self.date_expr.match(text).hasMatch():
            return QtCore.QDate
        elif self.time_expr.match(text).hasMatch():
            return QtCore.QTime
        elif self.date_time_expr.match(text).hasMatch():
            return QtCore.QDateTime
        elif self.directory_expr.match(text).hasMatch():
            return QtCore.QDir

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
        if isinstance(value, QtCore.QDir):
            return QtGui.QRegularExpressionValidator(self.directory_expr, parent)
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
        if isinstance(original_value, QtCore.QDir):
            return QtCore.QDir(text)
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
                QtCore.QDir,
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
            if value in {"instantaneous", "rolling_window"}:
                return RateComputationMethod(value).name
            return value
        if isinstance(value, QtCore.QDir):
            return value.canonicalPath()
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
            return ", ".join(map(repr, value))  # pyright: ignore[reportUnknownArgumentType]
        if isinstance(value, tuple) and len(value) == 4:  # pyright: ignore[reportUnknownArgumentType]
            try:
                c = mkColor(value)  # pyright: ignore[reportUnknownArgumentType]
                return c.name()
            except Exception:
                return f"<{value}>"
        return "<Invalid>" if value is None else f"<{value}>"


def get_app_dir() -> QtCore.QDir:
    app_instance = QtWidgets.QApplication.instance()
    import sys

    if hasattr(sys, "frozen") and app_instance is not None:
        return QtCore.QDir(app_instance.applicationDirPath())
    return QtCore.QDir.current()


class SettingsTree(QtWidgets.QTreeWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self._DEFAULT_VALUES = _t.DefaultAppSettings(
            Plot=_t.DefaultPlotSettings(
                background_color=pg.mkColor("black"),
                foreground_color=pg.mkColor("lightgray"),
                point_color=pg.mkColor("gold"),
                signal_line_color=pg.mkColor("coral"),
                rate_line_color=pg.mkColor("lightgreen"),
                section_marker_color=pg.mkColor((100, 200, 150, 40)),
            ),
            Editing=_t.DefaultEditingSettings(
                click_width_signal_line=70,
                search_around_click_radius=20,
                minimum_peak_distance=20,
                rate_computation_method=RateComputationMethod.Instantaneous,
            ),
            Data=_t.DefaultDataSettings(
                sampling_rate=400,
                txt_file_separator_character=TextFileSeparator.Tab,
                try_parse_dates=False,
            ),
            Misc=_t.DefaultMiscSettings(
                data_folder=get_app_dir().canonicalPath(),
                output_folder=get_app_dir().canonicalPath(),
                float_visual_precision=3,
                last_signal_column_name=None,
                last_info_column_name=None,
            ),
        )
        self._DESCRIPTIONS = {
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
        self._type_checker = TypeChecker()
        self.setItemDelegate(VariantDelegate(self._type_checker, self))

        self.setColumnCount(4)
        self.setHeaderLabels(("Setting", "Type", "Value", "Description"))
        self.header().setMinimumSectionSize(50)
        self.header().setStretchLastSection(True)
        self.header().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Interactive)
        self.setEditTriggers(QtWidgets.QTreeWidget.EditTrigger.NoEditTriggers)
        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)

        self.settings: QtCore.QSettings | None = None
        self.refresh_timer = QtCore.QTimer()
        self.refresh_timer.setInterval(2000)
        self.auto_refresh = False

        self.group_icon = QtGui.QIcon()
        self.group_icon.addPixmap(
            QtGui.QPixmap(":/icons/expand_plus"),
            QtGui.QIcon.Mode.Normal,
            QtGui.QIcon.State.Off,
        )
        self.group_icon.addPixmap(
            QtGui.QPixmap(":/icons/expand_minus"),
            QtGui.QIcon.Mode.Normal,
            QtGui.QIcon.State.On,
        )
        self.key_icon = QtGui.QIcon(":/icons/category_item")
        self.color_icon = QtGui.QIcon(":/icons/color")
        self.folder_import_icon = QtGui.QIcon(":/icons/folder_import")
        self.folder_export_icon = QtGui.QIcon(":/icons/folder_export")

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
            for group, default_values in self._DEFAULT_VALUES.items():
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

        sure = QtWidgets.QMessageBox.question(
            self,
            "Restore Defaults",
            "Are you sure you want to restore the default settings?\nThis will overwrite any changes you've made.",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
        )
        if sure != QtWidgets.QMessageBox.StandardButton.Yes:
            return

        for grp, kvs in self._DEFAULT_VALUES.items():
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

        return super().event(e)

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
                if "color" in key:
                    child.setIcon(0, self.color_icon)
                elif key == "data_folder":
                    child.setIcon(0, self.folder_import_icon)
                elif key == "output_folder":
                    child.setIcon(0, self.folder_export_icon)
                else:
                    child.setIcon(0, self.key_icon)
                divider_index += 1
            elif child_index >= divider_index:
                child = self.child_at(parent, child_index)
                for i in range(child.childCount()):
                    self.delete_item(child, i)
                self.move_item_forward(parent, child_index, divider_index)
                if "color" in key:
                    child.setIcon(0, self.color_icon)
                elif key == "data_folder":
                    child.setIcon(0, self.folder_import_icon)
                elif key == "output_folder":
                    child.setIcon(0, self.folder_export_icon)
                else:
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
            child.setText(3, self._DESCRIPTIONS.get(key, ""))
            if "color" in key or isinstance(value, QtGui.QColor):
                with contextlib.suppress(Exception):
                    color = mkColor(value)  # pyright: ignore[reportArgumentType]
                    child.setBackground(2, color)
                    # Adjust foreground color to be readable
                    if color.lightnessF() < 0.5:
                        child.setForeground(2, QtGui.QBrush(QtGui.QColor(255, 255, 255)))
                    else:
                        child.setForeground(2, QtGui.QBrush(QtGui.QColor(0, 0, 0)))

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

        if parent is not None:
            item = QtWidgets.QTreeWidgetItem(parent, after)  # type: ignore
        else:
            item = QtWidgets.QTreeWidgetItem(self, after)  # type: ignore

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
        sure = QtWidgets.QMessageBox.question(
            self,
            "Delete?",
            "Are you sure you want to delete this item?",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
        )
        if sure != QtWidgets.QMessageBox.StandardButton.Yes:
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

        default_value = self._DEFAULT_VALUES[item.parent().text(0)][key]  # type: ignore
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


class SettingsEditor(QtWidgets.QDialog):
    sig_setting_changed = QtCore.Signal(str, object)

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setVisible(False)

        self.setWindowTitle("Settings")
        self.setWindowIcon(QtGui.QIcon(":/icons/view_settings"))
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

        toolbar = QtWidgets.QToolBar("Toolbar Settings", self)

        action_reset_selected_item = QtGui.QAction(
            QtGui.QIcon(":/icons/restore_defaults"), "Reset Selected", self
        )
        action_reset_selected_item.triggered.connect(self.settings_tree.reset_current_item)

        if os.environ.get("DEBUG", "0") == "1":
            action_delete_selected_item = QtGui.QAction(
                QtGui.QIcon(":/icons/delete"), "Delete Selected", self
            )
            action_delete_selected_item.triggered.connect(self.settings_tree.delete_current_item)
            toolbar.addAction(action_delete_selected_item)

        action_restore_defaults = QtGui.QAction(
            QtGui.QIcon(":/icons/reset_all"), "Restore Original Values", self
        )
        action_restore_defaults.triggered.connect(self.settings_tree.restore_defaults)

        action_edit_selected_item_value = QtGui.QAction(
            QtGui.QIcon(":/icons/edit"), "Edit Selected Item Value", self
        )
        action_edit_selected_item_value.triggered.connect(
            lambda: self._on_edit_selected_item_value(self.settings_tree.currentItem())
        )
        action_refresh_settings = QtGui.QAction(QtGui.QIcon(":/icons/refresh"), "Refresh", self)
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
        settings = QtCore.QSettings()
        settings.sync()
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
            "Edit Item Value",
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
            "Edit Item Value",
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
            "Edit Item Value",
            "Enter new value:",
            initial,
            min_allowed,
            max_allowed,
        )
        return val if ok else initial

    @QtCore.Slot(QtWidgets.QTreeWidgetItem)
    def _on_edit_selected_item_value(self, item: QtWidgets.QTreeWidgetItem) -> None:
        new_value = None
        match item.text(1):
            case "QColor":
                new_value = self.get_color(item.data(2, QtCore.Qt.ItemDataRole.UserRole))
                if new_value is not None:
                    item.setData(2, QtCore.Qt.ItemDataRole.UserRole, new_value)
                    item.setText(2, new_value.name())
                    item.setBackground(2, new_value)

            case "str":
                if item.text(0) in {"data_folder", "output_folder"}:
                    if new_value := QtWidgets.QFileDialog.getExistingDirectory(
                        self,
                        "Select Directory",
                        item.data(2, QtCore.Qt.ItemDataRole.UserRole),
                    ):
                        item.setData(2, QtCore.Qt.ItemDataRole.UserRole, new_value)
                        item.setText(2, new_value)

                elif item.text(0) == "rate_computation_method":
                    items = ("instantaneous", "rolling_window")
                    current_value = item.data(2, QtCore.Qt.ItemDataRole.UserRole)
                    new_value, ok = QtWidgets.QInputDialog.getItem(
                        self,
                        "Edit Item Value",
                        "Select Method",
                        items,
                        items.index(current_value),
                        False,
                    )
                    if ok and new_value:
                        item.setData(2, QtCore.Qt.ItemDataRole.UserRole, new_value)
                        item.setText(2, new_value)
                elif item.text(0) == "txt_file_separator_character":
                    items = [TextFileSeparator(c).name for c in TextFileSeparator]
                    current_value = TextFileSeparator(
                        item.data(2, QtCore.Qt.ItemDataRole.UserRole)
                    ).name
                    new_value, ok = QtWidgets.QInputDialog.getItem(
                        self,
                        "Edit Item Value",
                        "Select Character",
                        items,
                        items.index(current_value),
                        False,
                    )
                    if ok and new_value:
                        item.setData(
                            2, QtCore.Qt.ItemDataRole.UserRole, TextFileSeparator[new_value].value
                        )
                        item.setText(2, new_value)
                else:
                    new_value = self.get_text(item.data(2, QtCore.Qt.ItemDataRole.UserRole))
                    item.setData(2, QtCore.Qt.ItemDataRole.UserRole, new_value)
                    item.setText(2, new_value)
            case "int":
                if item.text(0) in {
                    "click_width_signal_line",
                    "search_around_click_radius",
                    "minimum_peak_distance",
                }:
                    new_value = self.get_int(
                        item.data(2, QtCore.Qt.ItemDataRole.UserRole), 5, 10_000
                    )
                else:
                    new_value = self.get_int(item.data(2, QtCore.Qt.ItemDataRole.UserRole))
                item.setData(2, QtCore.Qt.ItemDataRole.UserRole, new_value)
                item.setText(2, str(new_value))
            case "float":
                if item.text(0) == "sampling_rate":
                    new_value = self.get_float(
                        item.data(2, QtCore.Qt.ItemDataRole.UserRole), 1, 100_000
                    )
                else:
                    new_value = self.get_float(item.data(2, QtCore.Qt.ItemDataRole.UserRole))

                item.setData(2, QtCore.Qt.ItemDataRole.UserRole, new_value)
                item.setText(2, str(new_value))
            case "bool":
                options = ["True", "False"]
                new_value, ok = QtWidgets.QInputDialog.getItem(
                    self,
                    "Edit Item Value",
                    "Select new value:",
                    options,
                    options.index(str(item.data(2, QtCore.Qt.ItemDataRole.UserRole))),
                    False,
                )
                if ok and new_value:
                    item.setData(2, QtCore.Qt.ItemDataRole.UserRole, bool(new_value))
                    item.setText(2, new_value)
            case _:
                QtWidgets.QMessageBox.warning(
                    self,
                    "Cannot Edit Directly",
                    "This item cannot be edited directly.",
                )
        if new_value is not None:
            self.sig_setting_changed.emit(item.text(0), new_value)
