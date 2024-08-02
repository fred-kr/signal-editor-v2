import os
from pathlib import Path

import pyqtgraph as pg
import qfluentwidgets as qfw
from loguru import logger
from pyqtgraph.console import ConsoleWidget
from PySide6 import QtCore, QtGui, QtWidgets
from qfluentwidgets import NavigationInterface, NavigationItemPosition, qrouter

from signal_editor.ui.ui_main_window import Ui_MainWindow

from ..config import Config
from ..enum_defs import LogLevel
from .icons import FluentIcon as FI
from .widgets import ConfigDialog, ExportDialog, MetadataDialog, SectionListDock
from .widgets.log_window import StatusMessageDock
from .widgets.parameter_inputs import ParameterInputsDock


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    sig_metadata_changed = QtCore.Signal(dict)
    sig_table_refresh_requested = QtCore.Signal()

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.new_central_widget = QtWidgets.QWidget()
        self._h_layout = QtWidgets.QHBoxLayout(self.new_central_widget)
        self.navigation_interface = NavigationInterface(self, showMenuButton=True)

        self._setup_layout()
        self.setCentralWidget(self.new_central_widget)
        self._setup_navigation()
        self._setup_window()

        self._initialize_icons()
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
        self.add_sub_interface(self.stacked_page_import, FI.ArrowImport.icon(), "Data Import")
        self.add_sub_interface(self.stacked_page_edit, FI.DesktopPulse.icon(), "View / Edit")
        self.add_sub_interface(self.stacked_page_result, FI.DataScatter.icon(), "Results")
        self.add_sub_interface(self.stacked_page_export, FI.ArrowExportLtr.icon(), "Export")

        self.navigation_interface.addSeparator()

        self.add_sub_interface(
            self.stacked_page_test,
            FI.WindowDevTools.icon(),
            "Debug",
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

    def _initialize_icons(self) -> None:
        self._msg_box_icons = {
            LogLevel.DEBUG: FI.Wrench.icon(),
            LogLevel.INFO: FI.Info.icon(),
            LogLevel.WARNING: FI.Warning.icon(),
            LogLevel.ERROR: FI.ErrorCircle.icon(),
            LogLevel.CRITICAL: FI.Important.icon(),
            LogLevel.SUCCESS: FI.CheckmarkCircle.icon(),
        }

    def _setup_widgets(self) -> None:
        self.dialog_meta = MetadataDialog(self)
        self.dialog_config = ConfigDialog(self)
        self.dialog_export = ExportDialog(self)

        self.table_view_import_data.horizontalHeader().setDefaultAlignment(
            QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter
        )
        self.table_view_import_data.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.table_view_import_data.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.table_view_import_data.customContextMenuRequested.connect(self.show_data_view_context_menu)
        data_tree_widget = pg.DataTreeWidget(self.collapsible_frame)
        data_tree_widget.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        self.collapsible_frame.setText("File Metadata")
        self.collapsible_frame.setContent(data_tree_widget)
        self.data_tree_widget_import_metadata = data_tree_widget

        self.stackedWidget.setCurrentIndex(0)
        

    def _setup_docks(self) -> None:
        dwa = QtCore.Qt.DockWidgetArea

        dock_status = StatusMessageDock()
        self.addDockWidget(dwa.BottomDockWidgetArea, dock_status)
        self.dock_status_log = dock_status

        dock_sections = SectionListDock()
        self.addDockWidget(dwa.RightDockWidgetArea, dock_sections)
        self.dock_sections = dock_sections

        dock_parameters = ParameterInputsDock()
        self.addDockWidget(dwa.RightDockWidgetArea, dock_parameters)
        self.dock_parameters = dock_parameters

    def _add_console_dock(self) -> None:
        class ConsoleDock(QtWidgets.QDockWidget):
            def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
                super().__init__(parent)
                self.setVisible(False)
                self.setObjectName("DockWidgetConsole")
                self.setFloating(True)
                self.console = ConsoleWidget(
                    self,
                    namespace={"mw": parent, "app": qApp},  # type: ignore # noqa: F821
                    editor="code-insiders --reuse-window --goto {fileName}:{lineNum}",
                )

                self.setWidget(self.console)
                self.widget().show()

        dock_console = ConsoleDock(self)
        dock_console.setVisible(False)
        self.addDockWidget(QtCore.Qt.DockWidgetArea.BottomDockWidgetArea, dock_console)
        self._actions["info"].append(dock_console.toggleViewAction())
        self.menuView.addSeparator()
        self.menuView.addAction(dock_console.toggleViewAction())
        self.dock_console = dock_console

    def _setup_actions(self) -> None:
        self.action_find_peaks_in_selection.setShortcutVisibleInContextMenu(False)
        self.action_remove_peaks_in_selection.setShortcutVisibleInContextMenu(False)
        self.action_show_settings.setShortcutVisibleInContextMenu(False)
        self.action_show_user_guide.setShortcutVisibleInContextMenu(False)
        
        self.action_toggle_whats_this_mode = QtWidgets.QWhatsThis().createAction(self)
        self.action_toggle_whats_this_mode.setIcon(FI.Question.icon())
        self._actions = {
            "import": [self.action_open_file, self.action_edit_metadata, self.action_close_file],
            "edit": [
                self.dock_sections.toggleViewAction(),
                self.dock_parameters.toggleViewAction(),
                self.action_show_section_overview,
                self.action_toggle_auto_scaling,
                self.action_create_new_section,
            ],
            "result": [],
            "export": [self.action_export_result],
            "info": [],
            "help": [
                self.action_show_user_guide,
                self.action_toggle_whats_this_mode,
                self.dock_status_log.toggleViewAction(),
            ],
            "section_list": [
                self.action_create_new_section,
                self.action_delete_section,
                self.action_show_section_overview,
            ],
        }

        self.action_toggle_auto_scaling.setChecked(True)

    def _setup_toolbars(self) -> None:
        self.tool_bar_file_actions.addSeparator()
        self.tool_bar_file_actions.addAction(self.action_export_result)

        self.tool_bar_editing = self._setup_toolbar("tool_bar_editing", self._actions["edit"])
        self.tool_bar_editing.insertSeparator(self.action_show_section_overview)
        self.tool_bar_editing.insertSeparator(self.action_create_new_section)

        self.tool_bar_help = self._setup_toolbar("tool_bar_help", self._actions["help"])

        cb_section_list = qfw.CommandBar()
        cb_section_list.setObjectName("command_bar_section_list")
        cb_section_list.addActions(self._actions["section_list"])

        cb_section_list.insertSeparator(2)
        self.dock_sections.main_layout.insertWidget(1, cb_section_list)
        self.tool_bar_section_list = cb_section_list

    def _setup_toolbar(self, name: str, actions: list[QtGui.QAction], movable: bool = False) -> QtWidgets.QToolBar:
        tb = QtWidgets.QToolBar()
        tb.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        tb.setObjectName(name)
        tb.setMovable(movable)
        tb.addActions(actions)
        self.addToolBar(tb)
        return tb

    def _setup_menus(self) -> None:
        self.menuView.addActions([self.dock_sections.toggleViewAction(), self.dock_status_log.toggleViewAction()])
        self.menuView.addSeparator()
        self.menuView.addAction(self.dock_parameters.toggleViewAction())
        
        self.menuEdit.insertAction(self.action_show_section_overview, self.dock_parameters.toggleViewAction())
        self.menuEdit.insertSeparator(self.action_show_section_overview)

        self.menuHelp.addSeparator()
        self.menuHelp.addAction(self.dock_status_log.toggleViewAction())
        self.menuHelp.insertAction(self.action_show_user_guide, self.action_toggle_whats_this_mode)

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
        self.action_delete_section.triggered.connect(self.dock_sections.list_view.emit_delete_current_request)

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

        self.action_export_result.triggered.connect(self.show_export_dialog)

    @QtCore.Slot(QtCore.QPoint)
    def show_data_view_context_menu(self, pos: QtCore.QPoint) -> None:
        menu = QtWidgets.QMenu(self)
        action = QtGui.QAction(FI.ArrowSync.icon(), "Refresh", self.table_view_import_data)
        action.triggered.connect(self.sig_table_refresh_requested.emit)
        menu.addAction(action)
        menu.exec(QtGui.QCursor.pos())

    @QtCore.Slot(int)
    def _on_page_changed(self, index: int) -> None:
        self.show_section_confirm_cancel(False)
        if index in {0, 2, 4}:
            self.tool_bar_editing.setEnabled(False)
            self.tool_bar_section_list.setEnabled(False)
            self.dock_sections.hide()
            self.dock_parameters.hide()
            self.action_export_result.setEnabled(False)
        elif index == 1:
            self.tool_bar_editing.setEnabled(True)
            self.tool_bar_section_list.setEnabled(True)
            self.dock_sections.show()
            self.dock_parameters.show()
            self.action_export_result.setEnabled(False)
        elif index == 3:
            self.tool_bar_editing.setEnabled(False)
            self.tool_bar_section_list.setEnabled(False)
            self.dock_sections.hide()
            self.dock_parameters.hide()
            self.action_export_result.setEnabled(True)

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
        # self.dialog_config.config_tree.show()

    @QtCore.Slot()
    def show_export_dialog(self) -> None:
        curr_file_name = self.line_edit_active_file.text()
        if not curr_file_name:
            return
        out_name = f"Result_{Path(curr_file_name).stem}"
        self.dialog_export.line_edit_output_file_name.setText(out_name)
        self.dialog_export.open()

    @QtCore.Slot(QtGui.QCloseEvent)
    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        self.write_settings()
        if self.dialog_config.isVisible():
            self.dialog_config.done(QtWidgets.QDialog.DialogCode.Accepted)
        self.dock_status_log.close()
        self.dock_parameters.close()
        # self.dock_processing.close()
        # self.dock_peaks.close()
        self.dock_sections.close()

        if hasattr(self, "dock_console"):
            self.dock_console.close()
        return super().closeEvent(event)

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

            msg_box = QtWidgets.QMessageBox(self)
            msg_box.setWindowIcon(self._msg_box_icons[msg_log_level])
            msg_box.setWindowTitle(f"Message: {msg_log_level.name} - {time}")
            msg_box.setIconPixmap(self._msg_box_icons[msg_log_level].pixmap(64, 64))
            msg_box.setText(text)
            msg_box.setDetailedText(plain_message)
            msg_box.open()

    def set_active_section_label(self, label_text: str) -> None:
        self.dock_sections.label_active_section.setText(f"Active Section: {label_text}")
