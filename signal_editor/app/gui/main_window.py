import os
import typing as t

import pyqtgraph as pg
from loguru import logger
from PySide6 import QtCore, QtGui, QtWidgets

from signal_editor.ui.ui_dialog_metadata import Ui_MetadataDialog
from signal_editor.ui.ui_main_window import Ui_MainWindow
from signal_editor.app.enum_defs import LogLevel
from signal_editor.app.gui.widgets.log_viewer import StatusMessageDock
from signal_editor.app.gui.widgets.peak_detection_inputs import PeakDetectionDock
from signal_editor.app.gui.widgets.processing_inputs import ProcessingInputsDock
from signal_editor.app.gui.widgets.settings_editor import SettingsEditor


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
        self.setUniformItemSizes(True)
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
        self.toggleViewAction().setIcon(QtGui.QIcon(":/icons/list_view"))
        main_widget = QtWidgets.QWidget(self)
        main_layout = QtWidgets.QVBoxLayout(main_widget)

        label_active_section = QtWidgets.QLabel("Active Section: ", main_widget)
        label_active_section.setFont(QtGui.QFont("Segoe UI", 12, QtGui.QFont.Weight.Bold))
        main_layout.addWidget(label_active_section)
        self.label_active_section = label_active_section

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

        self.tool_bar_navigation.setWindowIcon(QtGui.QIcon(":/icons/navigation"))
        cc_tb = QtWidgets.QToolBar()
        cc_tb.setObjectName("tool_bar_confirm_cancel")
        cc_tb.addActions([self.action_confirm_section, self.action_cancel_section])
        self.addToolBar(QtCore.Qt.ToolBarArea.TopToolBarArea, cc_tb)
        self.tool_bar_cc = cc_tb
        self.tool_bar_cc.setVisible(False)

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

        self.dock_sections = SectionListDock()
        self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, self.dock_sections)

        self.dock_processing = ProcessingInputsDock()
        self.addDockWidget(QtCore.Qt.DockWidgetArea.LeftDockWidgetArea, self.dock_processing)

        self.dock_peaks = PeakDetectionDock()
        self.addDockWidget(QtCore.Qt.DockWidgetArea.LeftDockWidgetArea, self.dock_peaks)

        self._context_actions = {
            "import": [self.action_open_file, self.action_edit_metadata, self.action_close_file],
            "edit": [
                self.dock_processing.toggleViewAction(),
                self.dock_peaks.toggleViewAction(),
                self.action_show_section_overview,
                self.action_toggle_auto_scaling,
                self.action_create_new_section,
            ],
            "result": [],
            "export": [self.action_export_result],
            "info": [],
        }

        self.menuView.addActions(
            [self.dock_sections.toggleViewAction(), self.dock_status_log.toggleViewAction()]
        )
        self.menuView.addSeparator()
        self.menuView.addActions(
            [self.dock_processing.toggleViewAction(), self.dock_peaks.toggleViewAction()]
        )
        self.menuEdit.insertActions(
            self.action_show_section_overview,
            [self.dock_processing.toggleViewAction(), self.dock_peaks.toggleViewAction()],
        )
        self.menuEdit.insertSeparator(self.action_show_section_overview)

        self.read_settings()
        self.setup_actions()
        self.connect_qt_signals()
        self.dock_status_log.hide()
        self.dock_processing.hide()
        self.dock_peaks.hide()
        self.dock_sections.hide()
        self.change_context_actions(0)

    def setup_actions(self) -> None:
        navigation_action_group = QtGui.QActionGroup(self.tool_bar_navigation)
        navigation_action_group.setExclusive(True)

        navigation_action_group.addAction(self.action_show_import_page)
        navigation_action_group.addAction(self.action_show_edit_page)
        navigation_action_group.addAction(self.action_show_result_page)
        navigation_action_group.addAction(self.action_show_export_page)
        navigation_action_group.addAction(self.action_show_info_page)

        self.action_toggle_auto_scaling.setChecked(True)
        self.action_show_section_overview.setChecked(False)

        for action_list in self._context_actions.values():
            self.tool_bar_context_actions.addActions(action_list)

    def connect_qt_signals(self) -> None:
        self.action_show_import_page.triggered.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.stacked_page_import)
        )
        self.action_show_edit_page.triggered.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.stacked_page_edit)
        )
        self.action_show_result_page.triggered.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.stacked_page_result)
        )
        self.action_show_export_page.triggered.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.stacked_page_export)
        )
        self.action_show_info_page.triggered.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.stacked_page_test)
        )

        self.action_show_settings.triggered.connect(self.show_settings)

        self.dock_sections.toggleViewAction().toggled.connect(self.dock_sections.setVisible)
        self.dock_processing.toggleViewAction().toggled.connect(self.dock_processing.setVisible)
        self.dock_peaks.toggleViewAction().toggled.connect(self.dock_peaks.setVisible)
        self.dock_status_log.toggleViewAction().toggled.connect(self.dock_status_log.setVisible)

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

    @QtCore.Slot(int)
    def change_context_actions(self, index: int) -> None:
        self.tool_bar_context_actions.clear()
        self.tool_bar_cc.setVisible(False)
        if index == 0:
            self.tool_bar_context_actions.addActions(self._context_actions["import"])
        elif index == 1:
            self.tool_bar_context_actions.addActions(self._context_actions["edit"])
            self.tool_bar_context_actions.insertSeparator(self.action_show_section_overview)
            self.tool_bar_context_actions.insertSeparator(self.action_create_new_section)
            self.dock_sections.toggleViewAction().setChecked(True)
        elif index == 2:
            self.tool_bar_context_actions.addActions(self._context_actions["result"])
        elif index == 3:
            self.tool_bar_context_actions.addActions(self._context_actions["export"])
        elif index == 4:
            self.tool_bar_context_actions.addActions(self._context_actions["info"])

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
            settings.value("geometry", QtCore.QByteArray(), type=QtCore.QByteArray)  # type: ignore
        )
        self.restoreState(settings.value("state", QtCore.QByteArray(), type=QtCore.QByteArray))  # type: ignore
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
        self.dock_status_log.close()
        self.dock_processing.close()
        self.dock_peaks.close()
        self.dock_sections.close()
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

    def set_active_section_label(self, label_text: str) -> None:
        self.dock_sections.label_active_section.setText(f"Active Section: {label_text}")
