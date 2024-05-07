import os
import typing as t

import pyqtgraph as pg
from loguru import logger
from PySide6 import QtCore, QtGui, QtWidgets

from ...ui.ui_dialog_metadata import Ui_MetadataDialog
from ...ui.ui_main_window import Ui_MainWindow
from ..enum_defs import LogLevel
from .widgets.log_viewer import StatusMessageDock
from .widgets.peak_detection_inputs import PeakDetectionDock
from .widgets.processing_inputs import ProcessingInputsDock
from .widgets.settings_editor import SettingsEditor


class MetadataDialog(QtWidgets.QDialog, Ui_MetadataDialog):
    sig_property_has_changed = QtCore.Signal(dict)

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setupUi(self)

        self.setWindowIcon(QtGui.QIcon(":/icons/properties"))

    @QtCore.Slot()
    def accept(self) -> None:
        metadata_dict = {
            "sampling_rate": self.spin_box_sampling_rate.value(),
            "signal_column": self.combo_box_signal_column.currentText(),
            "info_column": self.combo_box_info_column.currentText(),
            "signal_column_index": self.combo_box_signal_column.currentIndex(),
            "info_column_index": self.combo_box_info_column.currentIndex(),
        }
        self.sig_property_has_changed.emit(metadata_dict)
        settings = QtCore.QSettings()
        settings.setValue(
            "Misc/last_signal_column_name", self.combo_box_signal_column.currentText()
        )
        settings.setValue("Misc/last_info_column_name", self.combo_box_info_column.currentText())
        settings.setValue("Data/sampling_rate", self.spin_box_sampling_rate.value())

        super().accept()


class SectionListView(QtWidgets.QListView):
    sig_delete_current_item: t.ClassVar[QtCore.Signal] = QtCore.Signal(QtCore.QModelIndex)

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.setSelectionRectVisible(True)
        self.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)

        self.action_delete_selected = QtGui.QAction("Delete Selected", self)
        self.action_delete_selected.triggered.connect(self.emit_delete_current_request)
        self.customContextMenuRequested.connect(self.show_context_menu)

    @QtCore.Slot(QtCore.QPoint)
    def show_context_menu(self, point: QtCore.QPoint) -> None:
        menu = QtWidgets.QMenu(self)
        selected_is_base = self.currentIndex().row() == 0
        self.action_delete_selected.setEnabled(not selected_is_base)
        menu.addAction(self.action_delete_selected)
        menu.exec(self.mapToGlobal(point))

    @QtCore.Slot()
    def emit_delete_current_request(self) -> None:
        index = self.currentIndex()
        self.sig_delete_current_item.emit(index)


class SectionListDock(QtWidgets.QDockWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setVisible(False)
        self.setObjectName("SectionListDock")
        self.setWindowTitle("Section List")
        self.list_view = SectionListView(self)
        main_widget = QtWidgets.QWidget(self)
        main_layout = QtWidgets.QVBoxLayout(main_widget)

        active_section_label = QtWidgets.QLabel("Active Section: ", main_widget)
        active_section_label.setFont(QtGui.QFont("Segoe UI", 12, QtGui.QFont.Weight.Bold))
        main_layout.addWidget(active_section_label)

        nav_btn_widget = QtWidgets.QWidget(self)
        nav_btn_layout = QtWidgets.QHBoxLayout(nav_btn_widget)
        self.btn_prev_section = QtWidgets.QPushButton(QtGui.QIcon(":/icons/nav_left"), "Previous")
        self.btn_next_section = QtWidgets.QPushButton(QtGui.QIcon(":/icons/nav_right"), "Next")
        nav_btn_layout.addWidget(self.btn_prev_section)
        nav_btn_layout.addStretch()
        nav_btn_layout.addWidget(self.btn_next_section)

        main_layout.addWidget(nav_btn_widget)
        main_layout.addWidget(self.list_view)

        self.setWidget(main_widget)


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    sig_metadata_changed: t.ClassVar[QtCore.Signal] = QtCore.Signal(dict)

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self._msg_box_icons = {
            LogLevel.DEBUG: QtGui.QIcon(":/icons/app_monitor"),
            LogLevel.INFO: QtGui.QIcon(":/icons/info"),
            LogLevel.WARNING: QtGui.QIcon(":/icons/warning"),
            LogLevel.ERROR: QtGui.QIcon(":/icons/error"),
            LogLevel.CRITICAL: QtGui.QIcon(":/icons/critical"),
            LogLevel.SUCCESS: QtGui.QIcon(":/icons/success"),
        }
        self._icons = {
            "properties": QtGui.QIcon(":/icons/properties"),
            "processor": QtGui.QIcon(":/icons/processor"),
            "edit": QtGui.QIcon(":/icons/view_app_monitor"),
            "navigation": QtGui.QIcon(":/icons/navigation"),
            "confirm": QtGui.QIcon(":/icons/tick_button"),
            "cancel": QtGui.QIcon(":/icons/delete"),
        }
        self.setDockNestingEnabled(True)

        self.tool_bar_navigation.setWindowIcon(QtGui.QIcon(":/icons/navigation"))

        self.table_view_import_data.horizontalHeader().setDefaultAlignment(
            QtCore.Qt.AlignmentFlag.AlignLeft
        )
        self.table_view_import_data.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeMode.Stretch
        )
        data_tree_widget = pg.DataTreeWidget(self.collapsible_frame)
        data_tree_widget.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding
        )
        self.collapsible_frame.setText("Detailed File Information")
        self.collapsible_frame.setContent(data_tree_widget)
        self.data_tree_widget_import_metadata = data_tree_widget

        dock_status_log = StatusMessageDock(self)
        self.addDockWidget(QtCore.Qt.DockWidgetArea.BottomDockWidgetArea, dock_status_log)
        self.dock_status_log = dock_status_log
        self.dock_status_log.log_text_box.sig_log_message.connect(self.maybe_show_error_dialog)

        self.settings_editor = SettingsEditor(self)

        self.dialog_meta = MetadataDialog(self)

        self.stackedWidget.setCurrentIndex(0)
        self.action_show_import_page.setChecked(True)

        self.dock_section_list = SectionListDock()
        self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, self.dock_section_list)

        self.dock_processing_inputs = ProcessingInputsDock()
        self.addDockWidget(QtCore.Qt.DockWidgetArea.LeftDockWidgetArea, self.dock_processing_inputs)

        self.dock_peaks = PeakDetectionDock()
        self.addDockWidget(QtCore.Qt.DockWidgetArea.LeftDockWidgetArea, self.dock_peaks)

        self.dialog_new_section = QtWidgets.QDialog(
            self, QtCore.Qt.WindowType.Tool | QtCore.Qt.WindowType.FramelessWindowHint
        )
        tbtn_confirm = QtWidgets.QToolButton(self.dialog_new_section)
        tbtn_confirm.setIcon(self._icons["confirm"])
        tbtn_confirm.clicked.connect(self.action_confirm_section.trigger)
        tbtn_cancel = QtWidgets.QToolButton(self.dialog_new_section)
        tbtn_cancel.setIcon(self._icons["cancel"])
        tbtn_cancel.clicked.connect(self.action_cancel_section.trigger)

        dlg_layout = QtWidgets.QHBoxLayout()
        dlg_layout.addWidget(tbtn_confirm)
        dlg_layout.addWidget(tbtn_cancel)
        self.dialog_new_section.setLayout(dlg_layout)

        self.read_settings()
        self.setup_actions()
        self.setup_menus()

    def setup_actions(self) -> None:
        navigation_action_group = QtGui.QActionGroup(self.tool_bar_navigation)
        navigation_action_group.setExclusive(True)

        navigation_action_group.addAction(self.action_show_import_page)
        navigation_action_group.addAction(self.action_show_edit_page)
        navigation_action_group.addAction(self.action_show_result_page)
        navigation_action_group.addAction(self.action_show_export_page)
        navigation_action_group.addAction(self.action_show_info_page)

        self.action_show_import_page.triggered.connect(
            lambda: self.stackedWidget.setCurrentIndex(0)
        )
        self.action_show_edit_page.triggered.connect(lambda: self.stackedWidget.setCurrentIndex(1))
        self.action_show_result_page.triggered.connect(
            lambda: self.stackedWidget.setCurrentIndex(2)
        )
        self.action_show_export_page.triggered.connect(
            lambda: self.stackedWidget.setCurrentIndex(3)
        )
        self.action_show_info_page.triggered.connect(lambda: self.stackedWidget.setCurrentIndex(4))

        self.action_show_settings.triggered.connect(self.show_settings)
        self.stackedWidget.currentChanged.connect(self.change_context_actions)

        self.spin_box_sampling_rate_import_page.valueChanged.connect(
            self.dialog_meta.spin_box_sampling_rate.setValue
        )
        self.combo_box_info_column_import_page.currentTextChanged.connect(
            self.dialog_meta.combo_box_info_column.setCurrentText
        )
        self.combo_box_signal_column_import_page.currentTextChanged.connect(
            self.dialog_meta.combo_box_signal_column.setCurrentText
        )
        self.dialog_meta.spin_box_sampling_rate.valueChanged.connect(
            self.spin_box_sampling_rate_import_page.setValue
        )
        self.dialog_meta.combo_box_info_column.currentTextChanged.connect(
            self.combo_box_info_column_import_page.setCurrentText
        )
        self.dialog_meta.combo_box_signal_column.currentTextChanged.connect(
            self.combo_box_signal_column_import_page.setCurrentText
        )
        self.stackedWidget.currentChanged.connect(
            lambda index: self.dock_section_list.setVisible(index == 1)  # type: ignore
        )
        self.action_toggle_auto_scaling.setChecked(True)
        self.action_show_section_overview.setChecked(False)

    def toggle_section_actions(self, show: bool) -> None:
        self.action_confirm_section.setEnabled(show)
        self.action_cancel_section.setEnabled(show)
        if not show:
            self.dialog_new_section.close()
        else:
            self.dialog_new_section.show()

    @QtCore.Slot(int)
    def change_context_actions(self, index: int) -> None:
        if index == 0:
            self._show_import_page()
        elif index == 1:
            self._show_edit_page()
        elif index == 2:
            self._show_result_page()
        elif index == 3:
            self._show_export_page()
        elif index == 4:
            self._show_info_page()

    def _show_import_page(self) -> None:
        self.tool_bar_context_actions.clear()
        self.tool_bar_context_actions.addAction(self.action_open_file)
        self.tool_bar_context_actions.addAction(self.action_edit_metadata)
        self.tool_bar_context_actions.addAction(self.action_close_file)

    def _show_edit_page(self) -> None:
        self.tool_bar_context_actions.clear()

        self.tool_bar_context_actions.addAction(self.action_show_processing_inputs)
        self.tool_bar_context_actions.addAction(self.action_show_peak_detection_inputs)
        self.tool_bar_context_actions.addAction(self.action_show_section_overview)
        self.tool_bar_context_actions.addAction(self.action_toggle_auto_scaling)

        self.tool_bar_context_actions.addSeparator()

        self.tool_bar_context_actions.addAction(self.action_create_new_section)

        self.tool_bar_context_actions.addSeparator()

        self.tool_bar_context_actions.addAction(self.action_confirm_section)
        self.tool_bar_context_actions.addAction(self.action_cancel_section)

        self.action_confirm_section.setEnabled(False)
        self.action_cancel_section.setEnabled(False)

    def _show_result_page(self) -> None:
        self.tool_bar_context_actions.clear()
        # TODO: Add actions

    def _show_export_page(self) -> None:
        self.tool_bar_context_actions.clear()
        self.tool_bar_context_actions.addAction(self.action_export_result)

    def _show_info_page(self) -> None:
        self.tool_bar_context_actions.clear()
        # TODO: Add actions

    def setup_menus(self) -> None:
        action_toggle_dock_status_log = self.dock_status_log.toggleViewAction()
        action_toggle_dock_status_log.setIcon(self._icons["processor"])
        action_toggle_dock_status_log.setText("Show Status Log")
        self.menuView.addAction(action_toggle_dock_status_log)

        action_toggle_tb_edit = self.tool_bar_context_actions.toggleViewAction()
        action_toggle_tb_edit.setIcon(self._icons["edit"])
        action_toggle_tb_edit.setText("Toggle Editing Toolbar")
        self.menuView.addAction(action_toggle_tb_edit)

        action_toggle_nav_toolbar = self.tool_bar_navigation.toggleViewAction()
        action_toggle_nav_toolbar.setIcon(self._icons["navigation"])
        action_toggle_nav_toolbar.setText("Toggle Navigation Toolbar")
        self.menuView.addAction(action_toggle_nav_toolbar)

    def write_settings(self) -> None:
        settings = QtCore.QSettings()
        settings.beginGroup("MainWindow")
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("state", self.saveState())
        settings.endGroup()
        settings.sync()

    def read_settings(self) -> None:
        settings = QtCore.QSettings()
        settings.beginGroup("MainWindow")
        self.restoreGeometry(
            settings.value("geometry", QtCore.QByteArray(), type=QtCore.QByteArray)  # pyright: ignore[reportArgumentType]
        )
        self.restoreState(settings.value("state", QtCore.QByteArray(), type=QtCore.QByteArray))  # pyright: ignore[reportArgumentType]
        settings.endGroup()

    @QtCore.Slot()
    def show_settings(self) -> None:
        self.settings_editor.open()
        settings = QtCore.QSettings()
        initial_setting_state = {k: settings.value(k) for k in settings.allKeys()}
        self.settings_editor.rejected.connect(lambda: self._restore_settings(initial_setting_state))
        self.settings_editor.accepted.connect(self.settings_editor.settings_tree.refresh)
        self.settings_editor.settings_tree.set_settings_object(settings)

    @QtCore.Slot(dict)
    def _restore_settings(self, initial_setting_state: dict[str, t.Any]) -> None:
        logger.info("Changes to settings weren't saved, restoring previous values.")
        settings = QtCore.QSettings()
        for k, v in initial_setting_state.items():
            if v != settings.value(k):
                settings.setValue(k, v)
        self.settings_editor.settings_tree.refresh()

    @QtCore.Slot(QtGui.QCloseEvent)
    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        self.write_settings()
        if self.settings_editor.isVisible():
            self.settings_editor.done(QtWidgets.QDialog.DialogCode.Rejected)
        return super().closeEvent(event)

    @QtCore.Slot(str, int, str)
    def maybe_show_error_dialog(
        self,
        message: str,
        msg_log_level: int,
        plain_message: str,
        threshold: LogLevel = LogLevel.ERROR,
    ) -> None:
        """
        Slot that listens for log messages and shows a QMessageBox if the message is above a certain
        log level.

        Parameters
        ----------
        message : str
            The log message to be displayed.
        msg_log_level : LogLevel, optional
            The log level of the message.
        plain_message : str
            The original log message without HTML formatting.
        threshold : LogLevel, optional
            The log level threshold for showing the message as a QMessageBox.
        """
        try:
            msg_log_level = LogLevel(msg_log_level)
        except ValueError:
            msg_log_level = LogLevel.DEBUG
            logger.debug(
                f"Invalid log level {msg_log_level} passed to maybe_show_error_dialog.\nOriginal message: {message}"
            )
        if os.environ.get("DEBUG") == "1":
            threshold = LogLevel.DEBUG

        if msg_log_level >= threshold:
            time = plain_message.split("|", 1)[0].strip().split(" ", 1)[1]
            text = message.split(" - ", 1)[1]

            msg_box = QtWidgets.QMessageBox(self)
            msg_box.setWindowIcon(self._msg_box_icons[msg_log_level])
            msg_box.setWindowTitle(f"Message: {msg_log_level.name} - {time}")
            msg_box.setIconPixmap(self._msg_box_icons[msg_log_level].pixmap(64, 64))
            msg_box.setText(text)
            msg_box.setDetailedText(plain_message)
            msg_box.open()
