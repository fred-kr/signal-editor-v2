import os
import typing as t
from pathlib import Path

import qfluentwidgets as qfw
from loguru import logger
from PySide6 import QtCore, QtGui, QtWidgets
from qfluentwidgets import NavigationInterface, NavigationItemPosition, qrouter

from ...ui.ui_main_window import Ui_MainWindow

from .. import type_defs as _t
from ..config import Config
from ..enum_defs import LogLevel
from .dialogs import ConfigDialog, MetadataDialog
from .icons import SignalEditorIcon as Icons
from .widgets import (
    DataTreeWidgetContainer,
    MessageBox,
    OverlayWidget,
    ParameterInputsDock,
    SectionListDock,
    SectionSummaryBox,
    StatusMessageDock,
)
from .widgets.jupyter_console_widget import ConsoleWindow


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    sig_metadata_changed = QtCore.Signal(dict)
    sig_table_refresh_requested = QtCore.Signal()
    sig_export_requested = QtCore.Signal(str)

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self._msg_box_icons = {
            LogLevel.DEBUG: Icons.Wrench.icon(),
            LogLevel.INFO: Icons.Info.icon(),
            LogLevel.WARNING: Icons.Warning.icon(),
            LogLevel.ERROR: Icons.ErrorCircle.icon(),
            LogLevel.CRITICAL: Icons.Important.icon(),
            LogLevel.SUCCESS: Icons.CheckmarkCircle.icon(),
        }
        self.setWindowIcon(Icons.SignalEditor.icon())

        self.new_central_widget = QtWidgets.QWidget()
        self._h_layout = QtWidgets.QHBoxLayout(self.new_central_widget)
        self.navigation_interface = NavigationInterface(self, showMenuButton=True)

        self.progress_dlg: QtWidgets.QProgressDialog | None = None
        self._overlay_widget = OverlayWidget(self)
        self._overlay_widget.hide()

        self._setup_layout()
        self.setCentralWidget(self.new_central_widget)
        self._setup_navigation()
        self._setup_window()

        self._setup_docks()
        self._setup_actions()
        self._setup_toolbars()
        self._setup_menus()
        self._setup_widgets()
        self._finalize_setup()
        if os.environ.get("DEV", "0") == "1":
            self._add_console_dock()

    def _setup_window(self) -> None:
        self.setWindowTitle("Signal Editor")

        desktop = QtWidgets.QApplication.primaryScreen().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

    def _setup_layout(self) -> None:
        self._h_layout.setSpacing(0)
        self._h_layout.setContentsMargins(0, 0, 0, 0)
        self._h_layout.addWidget(self.navigation_interface)
        self._h_layout.addWidget(self.stackedWidget)
        self._h_layout.setStretchFactor(self.stackedWidget, 1)

    def _setup_navigation(self) -> None:
        self.add_sub_interface(self.stacked_page_import, Icons.DocumentArrowLeft.icon(), "Import")
        self.add_sub_interface(self.stacked_page_edit, Icons.Edit.icon(), "Editing")
        self.add_sub_interface(self.stacked_page_export, Icons.DocumentArrowRight.icon(), "Results")

        self.add_sub_interface(
            self.stacked_page_test,
            Icons.Bug.icon(),
            "Test Page",
            position=NavigationItemPosition.BOTTOM,
        )
        qrouter.setDefaultRouteKey(self.stackedWidget, self.stacked_page_import.objectName())
        self.navigation_interface.setExpandWidth(250)

        self.stackedWidget.currentChanged.connect(self._on_current_interface_changed)
        self.stackedWidget.setCurrentIndex(0)
        self.navigation_interface.setCurrentItem(self.stackedWidget.currentWidget().objectName())

    def add_sub_interface(
        self,
        widget: QtWidgets.QWidget,
        icon: QtGui.QIcon,
        text: str,
        position: NavigationItemPosition = NavigationItemPosition.TOP,
    ) -> None:
        if self.stackedWidget.indexOf(widget) == -1:
            self.stackedWidget.addWidget(widget)
        self.navigation_interface.addItem(
            routeKey=widget.objectName(),
            icon=icon,
            text=text,
            onClick=lambda: self.switch_to(widget),
            position=position,
            tooltip=text,
        )

    def switch_to(self, widget: QtWidgets.QWidget) -> None:
        self.stackedWidget.setCurrentWidget(widget)

    @QtCore.Slot(int)
    def _on_current_interface_changed(self, index: int) -> None:
        widget = self.stackedWidget.widget(index)
        self.navigation_interface.setCurrentItem(widget.objectName())
        qrouter.push(self.stackedWidget, widget.objectName())

    def _setup_widgets(self) -> None:
        self.dialog_meta = MetadataDialog(self)
        self.dialog_config = ConfigDialog(self)
        # self.dialog_export = ExportDialog(self)

        self.table_view_import_data.horizontalHeader().setDefaultAlignment(
            QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter
        )
        self.table_view_import_data.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.table_view_import_data.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.table_view_import_data.customContextMenuRequested.connect(self.show_data_view_context_menu)

        self.table_view_result_peaks.horizontalHeader().setDefaultAlignment(
            QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter
        )
        self.table_view_result_peaks.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)

        self.table_view_result_rate.horizontalHeader().setDefaultAlignment(
            QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter
        )
        self.table_view_result_rate.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)

        layout = QtWidgets.QVBoxLayout()
        data_tree_widget = DataTreeWidgetContainer()
        data_tree_widget.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        layout.addWidget(data_tree_widget)
        self.dialog_meta.container_additional_metadata.setLayout(layout)
        self.data_tree_widget_additional_metadata = data_tree_widget

        self.btn_export_all_results.setIcon(Icons.ArrowExportLtr.icon())

        self.stackedWidget.setCurrentIndex(0)

    def _setup_docks(self) -> None:  # sourcery skip: extract-duplicate-method
        dwa = QtCore.Qt.DockWidgetArea

        dock_status = StatusMessageDock()
        self.addDockWidget(dwa.BottomDockWidgetArea, dock_status)
        self.dock_status_log = dock_status

        dock_sections = SectionListDock()
        self.addDockWidget(dwa.RightDockWidgetArea, dock_sections)
        self.dock_sections = dock_sections
        self.dock_sections.setEnabled(False)

        dock_parameters = ParameterInputsDock()
        self.addDockWidget(dwa.RightDockWidgetArea, dock_parameters)
        self.dock_parameters = dock_parameters
        self.dock_parameters.setEnabled(False)

    def _add_console_dock(self) -> None:
        console_window = ConsoleWindow()
        console_window.setVisible(False)

        self.menu_view.addSeparator()
        self.menu_view.addAction(console_window.toggle_view_action)
        self.console_window = console_window

    def _setup_actions(self) -> None:
        self.action_show_section_summary = QtGui.QAction(Icons.Info.icon(), "Show Section Summary", self)

        self.action_toggle_whats_this_mode = QtWidgets.QWhatsThis().createAction(self)
        self.action_toggle_whats_this_mode.setIcon(Icons.Question.icon())

        self.action_export_to_csv = qfw.Action(Icons.ArrowExportLtr.icon(), "Export to CSV")
        self.action_export_to_xlsx = qfw.Action(Icons.ArrowExportLtr.icon(), "Export to XLSX")
        self.action_export_to_hdf5 = qfw.Action(Icons.ArrowExportLtr.icon(), "Export to HDF5")

        self.action_toggle_auto_scaling.setChecked(True)

    def _setup_toolbars(self) -> None:
        self.tool_bar_editing = self._setup_toolbar(
            "tool_bar_editing", [self.action_toggle_auto_scaling, self.action_show_section_overview]
        )

        self.tool_bar_help = self._setup_toolbar(
            "tool_bar_help", [self.action_show_user_guide, self.action_toggle_whats_this_mode]
        )

        cb_section_list = qfw.CommandBar()
        cb_section_list.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        cb_section_list.setObjectName("command_bar_section_list")
        cb_section_list.addActions(
            [self.action_create_new_section, self.action_remove_section, self.action_mark_section_done]
        )
        cb_section_list.addHiddenActions(
            [self.action_unlock_section, self.action_show_section_summary, self.action_show_section_overview]
        )

        self.dock_sections.main_layout.insertWidget(1, cb_section_list)
        self.tool_bar_section_list = cb_section_list

        self.cb_result_peak_info.addActions([self.action_export_to_csv, self.action_export_to_xlsx])
        self.cb_result_rate_info.addActions([self.action_export_to_csv, self.action_export_to_xlsx])
        self.cb_result_metadata.addActions([self.action_export_to_hdf5])

        for cb in [self.cb_result_peak_info, self.cb_result_rate_info, self.cb_result_metadata]:
            cb.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

    def _setup_toolbar(self, name: str, actions: list[QtGui.QAction], movable: bool = False) -> QtWidgets.QToolBar:
        tb = QtWidgets.QToolBar(name)
        tb.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        tb.setObjectName(name)
        tb.setMovable(movable)
        tb.addActions(actions)
        self.addToolBar(tb)
        return tb

    def _setup_menus(self) -> None:
        self.menu_view.addActions(
            [
                self.dock_sections.toggleViewAction(),
                self.dock_status_log.toggleViewAction(),
                self.dock_parameters.toggleViewAction(),
            ]
        )

        self.menu_plot.insertSeparator(self.action_show_section_overview)

        self.menu_help.addSeparator()
        self.menu_help.addAction(self.dock_status_log.toggleViewAction())
        self.menu_help.insertAction(self.action_show_user_guide, self.action_toggle_whats_this_mode)

        self.menu_export = qfw.RoundMenu()
        self.menu_export.addActions([self.action_export_to_csv, self.action_export_to_xlsx, self.action_export_to_hdf5])

    def hide_all_docks(self) -> None:
        self.dock_status_log.hide()
        self.dock_parameters.hide()
        self.dock_sections.hide()

    def _finalize_setup(self) -> None:
        self.read_settings()
        self._connect_signals()
        self.show_section_confirm_cancel(False)
        self.hide_all_docks()
        self._on_page_changed(0)

    def _connect_signals(self) -> None:
        self.action_show_settings.triggered.connect(self.show_settings_dialog)
        self.action_remove_section.triggered.connect(self.dock_sections.list_view.emit_delete_current_request)

        self.stackedWidget.currentChanged.connect(self._on_page_changed)

        self.spin_box_sampling_rate_import_page.valueChanged.connect(self.dialog_meta.spin_box_sampling_rate.setValue)
        self.combo_box_info_column_import_page.currentTextChanged.connect(
            self.dialog_meta.combo_box_info_column.setCurrentText
        )
        self.combo_box_signal_column_import_page.currentTextChanged.connect(
            self.dialog_meta.combo_box_signal_column.setCurrentText
        )
        self.dialog_meta.spin_box_sampling_rate.valueChanged.connect(self.spin_box_sampling_rate_import_page.setValue)
        self.dialog_meta.combo_box_info_column.currentTextChanged.connect(
            self.combo_box_info_column_import_page.setCurrentText
        )
        self.dialog_meta.combo_box_signal_column.currentTextChanged.connect(
            self.combo_box_signal_column_import_page.setCurrentText
        )

        self.dock_status_log.log_text_box.sig_log_message.connect(self.maybe_show_error_dialog)
        self.dock_sections.btn_confirm.clicked.connect(self.action_confirm_section.trigger)
        self.dock_sections.btn_cancel.clicked.connect(self.action_cancel_section.trigger)

        self.action_export_to_csv.triggered.connect(lambda: self.show_export_dialog("csv"))
        self.action_export_to_xlsx.triggered.connect(lambda: self.show_export_dialog("xlsx"))
        self.action_export_to_hdf5.triggered.connect(lambda: self.show_export_dialog("hdf5"))

    @QtCore.Slot(QtCore.QPoint)
    def show_data_view_context_menu(self, pos: QtCore.QPoint) -> None:
        menu = qfw.RoundMenu(parent=self.table_view_import_data)
        action = QtGui.QAction(Icons.ArrowSync.icon(), "Refresh", self.table_view_import_data)
        action.triggered.connect(self.sig_table_refresh_requested.emit)
        menu.addAction(action)
        menu.exec(self.table_view_import_data.mapToGlobal(pos))

    def show_section_summary_box(self, summary: _t.SectionSummaryDict) -> None:
        msg_box = SectionSummaryBox("Section Summary", summary, parent=self)
        msg_box.open()

    @QtCore.Slot(int)
    def _on_page_changed(self, index: int) -> None:
        self.show_section_confirm_cancel(False)
        if index in {0, 2, 3, 4}:
            self.tool_bar_editing.setEnabled(False)
            self.tool_bar_section_list.setEnabled(False)
            self.dock_parameters.hide()
        elif index == 1:
            self.tool_bar_editing.setEnabled(True)
            self.tool_bar_section_list.setEnabled(True)
            self.dock_sections.show()
            self.dock_parameters.show()

    def show_section_confirm_cancel(self, show: bool) -> None:
        self.dock_sections.btn_container.setVisible(show)

    def write_settings(self) -> None:
        config = Config()
        config.internal.WindowGeometry = self.saveGeometry()
        config.internal.WindowState = self.saveState()

        config.save()

    def read_settings(self) -> None:
        config = Config()
        self.restoreGeometry(config.internal.WindowGeometry)
        self.restoreState(config.internal.WindowState)

    @QtCore.Slot()
    def show_settings_dialog(self) -> None:
        self.dialog_config.open()

    @QtCore.Slot(str)
    def show_export_dialog(self, format: t.Literal["csv", "xlsx", "hdf5"]) -> None:
        # section = self.combo_box_result_section.currentText()
        # selected_results = self.list_view_result_selection.selectedIndexes()

        curr_file_name = self.line_edit_active_file.text()
        if not curr_file_name:
            return
        result_path = Path(Path(Config().internal.OutputDir) / f"Result_{Path(curr_file_name).stem}").with_suffix(
            f".{format}"
        )

        out_name, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, dir=result_path.as_posix(), filter=f"{format.upper()} files (*.{format})"
        )

        if not out_name:
            return

        Config().internal.OutputDir = Path(out_name).parent.as_posix()
        self.sig_export_requested.emit(out_name)

        # self.dialog_export.line_edit_output_file_name.setText(out_name)
        # self.dialog_export.open()

    def show_overlay(self, text: str = "Calculating...") -> None:
        self.centralWidget().setEnabled(False)
        self.dock_parameters.setEnabled(False)
        self.dock_sections.setEnabled(False)

        self._overlay_widget.set_text(text)
        self._overlay_widget.setGeometry(self.centralWidget().geometry())
        self._overlay_widget.btn_cancel.setEnabled(True)
        self._overlay_widget.raise_()
        self._overlay_widget.show()

    def hide_overlay(self) -> None:
        self.centralWidget().setEnabled(True)
        self.dock_parameters.setEnabled(True)
        self.dock_sections.setEnabled(True)

        self._overlay_widget.hide()

    @QtCore.Slot(QtGui.QCloseEvent)
    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        self.write_settings()
        if self.dialog_config.isVisible():
            self.dialog_config.done(QtWidgets.QDialog.DialogCode.Accepted)
        self.dock_status_log.close()
        self.dock_parameters.close()
        self.dock_sections.close()

        if hasattr(self, "console_window"):
            self.console_window.close()
        return super().closeEvent(event)

    def show_success(self, title: str, text: str) -> None:
        qfw.InfoBar.success(
            title=title,
            content=text,
            duration=3000,
            parent=self,
        )

    def show_error(self, title: str, text: str) -> None:
        qfw.InfoBar.error(
            title=title,
            content=text,
            duration=3000,
            parent=self,
        )

    @QtCore.Slot(str, int, str)
    def maybe_show_error_dialog(
        self,
        message: str,
        msg_log_level: int,
        plain_message: str,
        threshold: LogLevel = LogLevel.WARNING,
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
            # If a traceback is included, show it in the detailed text instead of the message
            traceback = plain_message
            if "Traceback" in text:
                split_text = text.split("Traceback", 1)
                text = split_text[0]
                traceback = f"Traceback: {split_text[1]}"

            title = f"Message: {msg_log_level.name} - {time}"
            icon = self._msg_box_icons[msg_log_level]
            parent = self
            if self.dialog_meta.isVisible():
                parent = self.dialog_meta
            # elif self.dialog_export.isVisible():
            # parent = self.dialog_export
            elif self.dialog_config.isVisible():
                parent = self.dialog_config

            msg_box = MessageBox(title, text, icon=icon, parent=parent)
            msg_box.set_detailed_text(traceback)

            msg_box.open()

    def set_active_section_label(self, label_text: str) -> None:
        self.dock_sections.label_active_section.setText(f"Active Section: {label_text}")
        self.label_showing_section_result.setText(label_text)
        self.label_showing_data_table.setText(f"Showing: {label_text}")
