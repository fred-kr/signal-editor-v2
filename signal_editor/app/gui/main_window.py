import os
import typing as t
from pathlib import Path

import pyqtgraph as pg
from loguru import logger
from PySide6 import QtCore, QtGui, QtWidgets

from signal_editor.app.enum_defs import ExportFormatCompact, ExportFormatDetailed, LogLevel
from signal_editor.app.gui.widgets.log_viewer import StatusMessageDock
from signal_editor.app.gui.widgets.peak_detection_inputs import PeakDetectionDock
from signal_editor.app.gui.widgets.processing_inputs import ProcessingInputsDock
from signal_editor.app.gui.widgets.settings_editor import SettingsEditor
from signal_editor.ui.ui_dialog_export_result import Ui_ExportDialog
from signal_editor.ui.ui_dialog_metadata import Ui_MetadataDialog
from signal_editor.ui.ui_main_window import Ui_MainWindow


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


class ExportDialog(QtWidgets.QDialog, Ui_ExportDialog):
    sig_export_confirmed: t.ClassVar[QtCore.Signal] = QtCore.Signal(dict)

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Export Results")
        self.setWindowIcon(QtGui.QIcon(":/icons/file_export"))
        self.setModal(True)

        self._initialize_widgets()
        self._connect_signals()

    def _initialize_widgets(self) -> None:
        self.collapsible_extra_metadata.setText("Additional Details")

        detail_form = QtWidgets.QFormLayout()
        detail_form.setRowWrapPolicy(QtWidgets.QFormLayout.RowWrapPolicy.WrapAllRows)
        meas_date = QtWidgets.QLineEdit()
        meas_date.setPlaceholderText("YYYY-MM-DD")
        meas_date.setInputMethodHints(QtCore.Qt.InputMethodHint.ImhDate)
        detail_form.addRow("Date of Measurement", meas_date)
        subject_id = QtWidgets.QLineEdit()
        subject_id.setPlaceholderText("Subject ID")
        detail_form.addRow("Subject ID", subject_id)
        oxy_cond = QtWidgets.QComboBox()
        oxy_cond.addItems(["-", "Normoxia", "Hypoxia"])
        detail_form.addRow("Oxygen Condition", oxy_cond)

        self.meas_date = meas_date
        self.subject_id = subject_id
        self.oxy_cond = oxy_cond

        self.collapsible_extra_metadata.content().setLayout(detail_form)

    def _connect_signals(self) -> None:
        self.combo_box_result_type.currentTextChanged.connect(self._update_export_format)
        self.btn_browse_output_dir.clicked.connect(self._browse_output_dir)

    @QtCore.Slot(str)
    def _update_export_format(self, result_type: str) -> None:
        if result_type == "Compact":
            self.enum_combo_export_format.setEnumClass(ExportFormatCompact)
        elif result_type == "Detailed":
            self.enum_combo_export_format.setEnumClass(ExportFormatDetailed)

    @QtCore.Slot()
    def _browse_output_dir(self) -> None:
        if output_dir := QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select Output Directory"
        ):
            self.line_edit_output_dir.setText(output_dir)

    @QtCore.Slot()
    def accept(self) -> None:
        output_dir = self.line_edit_output_dir.text()
        if not output_dir:
            logger.warning("No output directory selected.")
            return

        output_file = self.line_edit_output_file_name.text()
        if not output_file:
            logger.warning("No output file name specified.")
            return

        output_type = self.combo_box_result_type.currentText()
        export_format = (
            ExportFormatCompact(self.enum_combo_export_format.currentEnum())
            if output_type == "Compact"
            else ExportFormatDetailed(self.enum_combo_export_format.currentEnum())
        )
        suffix = export_format.value

        subject_id = self.subject_id.text()
        measured_date = self.meas_date.text()
        oxygen_condition = self.oxy_cond.currentText()
        if not subject_id:
            subject_id = None
        if not measured_date:
            measured_date = None
        if oxygen_condition == "-":
            oxygen_condition = None

        out_path = Path(output_dir) / Path(output_file).with_suffix(suffix)
        info = {
            "out_path": out_path,
            "subject_id": subject_id,
            "measured_date": measured_date,
            "oxygen_condition": oxygen_condition,
        }
        self.sig_export_confirmed.emit(info)
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

        confirm_cancel_btns = QtWidgets.QWidget()
        confirm_cancel_layout = QtWidgets.QHBoxLayout(confirm_cancel_btns)
        confirm_cancel_layout.setContentsMargins(0, 0, 0, 0)

        confirm_btn = QtWidgets.QPushButton()
        confirm_btn.setMinimumHeight(31)
        confirm_btn.setText("Confirm")
        confirm_btn.setIcon(QtGui.QIcon(":/icons/tick_button"))
        confirm_cancel_layout.addWidget(confirm_btn)
        self.btn_confirm = confirm_btn

        cancel_btn = QtWidgets.QPushButton()
        cancel_btn.setMinimumHeight(31)
        cancel_btn.setText("Cancel")
        cancel_btn.setIcon(QtGui.QIcon(":/icons/cross"))
        confirm_cancel_layout.addWidget(cancel_btn)
        self.btn_cancel = cancel_btn

        self.btn_container = confirm_cancel_btns
        confirm_cancel_btns.setLayout(confirm_cancel_layout)
        main_layout.addWidget(confirm_cancel_btns)

        main_layout.addWidget(self.list_view)
        self.main_layout = main_layout

        self.setWidget(main_widget)


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    sig_metadata_changed: t.ClassVar[QtCore.Signal] = QtCore.Signal(dict)
    sig_table_refresh_requested: t.ClassVar[QtCore.Signal] = QtCore.Signal()

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setupUi(self)

        self._initialize_icons()
        self._setup_docks()
        self._setup_actions()
        self._setup_toolbars()
        self._setup_menus()
        self._setup_widgets()
        self._finalize_setup()

    def _initialize_icons(self) -> None:
        self._msg_box_icons = {
            LogLevel.DEBUG: QtGui.QIcon(":/icons/app_monitor"),
            LogLevel.INFO: QtGui.QIcon(":/icons/info"),
            LogLevel.WARNING: QtGui.QIcon(":/icons/warning"),
            LogLevel.ERROR: QtGui.QIcon(":/icons/error"),
            LogLevel.CRITICAL: QtGui.QIcon(":/icons/critical"),
            LogLevel.SUCCESS: QtGui.QIcon(":/icons/success"),
        }
        self._icons = {
            "navigation": QtGui.QIcon(":/icons/navigation"),
            "whats_this": QtGui.QIcon(":/icons/whats_this"),
            "confirm": QtGui.QIcon(":/icons/tick_mark"),
            "cancel": QtGui.QIcon(":/icons/cross"),
            "refresh": QtGui.QIcon(":/icons/refresh"),
        }

    def _setup_widgets(self) -> None:
        self.dialog_meta = MetadataDialog(self)
        self.settings_editor = SettingsEditor(self)
        self.dialog_export = ExportDialog(self)

        self.table_view_import_data.horizontalHeader().setDefaultAlignment(
            QtCore.Qt.AlignmentFlag.AlignLeft
        )
        self.table_view_import_data.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeMode.Stretch
        )
        self.table_view_import_data.setContextMenuPolicy(
            QtCore.Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.table_view_import_data.customContextMenuRequested.connect(
            self.show_data_view_context_menu
        )
        data_tree_widget = pg.DataTreeWidget(self.collapsible_frame)
        data_tree_widget.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding
        )
        self.collapsible_frame.setText("File Metadata")
        self.collapsible_frame.setContent(data_tree_widget)
        self.data_tree_widget_import_metadata = data_tree_widget

        self.stackedWidget.setCurrentIndex(0)
        self.action_show_import_page.setChecked(True)

        self.search_list_widget_recent_files.filter_widget.setPlaceholderText("Search Recent Files")
        self.search_list_widget_recent_files.list_widget.setAlternatingRowColors(True)
        self.search_list_widget_recent_files.list_widget.setSelectionMode(
            QtWidgets.QAbstractItemView.SelectionMode.SingleSelection
        )
        self.search_list_widget_recent_files.list_widget.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.search_list_widget_recent_files.list_widget.setSelectionRectVisible(True)
        self.search_list_widget_recent_files.list_widget.setSpacing(2)

    def _setup_docks(self) -> None:
        dwa = QtCore.Qt.DockWidgetArea

        dock_status = StatusMessageDock()
        self.addDockWidget(dwa.BottomDockWidgetArea, dock_status)
        self.dock_status_log = dock_status

        dock_sections = SectionListDock()
        self.addDockWidget(dwa.RightDockWidgetArea, dock_sections)
        self.dock_sections = dock_sections

        dock_processing = ProcessingInputsDock()
        self.addDockWidget(dwa.RightDockWidgetArea, dock_processing)
        self.dock_processing = dock_processing

        dock_peaks = PeakDetectionDock()
        self.addDockWidget(dwa.RightDockWidgetArea, dock_peaks)
        self.dock_peaks = dock_peaks

    def _setup_actions(self) -> None:
        self.action_toggle_whats_this_mode = QtWidgets.QWhatsThis().createAction(self)
        self.action_toggle_whats_this_mode.setIcon(self._icons["whats_this"])
        self._actions = {
            "import": [self.action_open_file, self.action_edit_metadata, self.action_close_file],
            "edit": [
                self.dock_sections.toggleViewAction(),
                self.dock_processing.toggleViewAction(),
                self.dock_peaks.toggleViewAction(),
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

        navigation_action_group = QtGui.QActionGroup(self.tool_bar_navigation)
        navigation_action_group.setExclusive(True)

        navigation_action_group.addAction(self.action_show_import_page)
        navigation_action_group.addAction(self.action_show_edit_page)
        navigation_action_group.addAction(self.action_show_result_page)
        navigation_action_group.addAction(self.action_show_export_page)
        navigation_action_group.addAction(self.action_show_info_page)

        self.action_toggle_auto_scaling.setChecked(True)

    def _setup_toolbars(self) -> None:
        self.tool_bar_navigation.setWindowIcon(self._icons["navigation"])

        self.tool_bar_file_actions.addSeparator()
        self.tool_bar_file_actions.addAction(self.action_export_result)

        self.tool_bar_editing = self._setup_toolbar("tool_bar_editing", self._actions["edit"])
        self.tool_bar_editing.insertSeparator(self.action_show_section_overview)
        self.tool_bar_editing.insertSeparator(self.action_create_new_section)

        self.tool_bar_help = self._setup_toolbar("tool_bar_help", self._actions["help"])

        tb_section_list = QtWidgets.QToolBar()
        tb_section_list.setMovable(False)
        tb_section_list.setObjectName("tool_bar_section_list")
        tb_section_list.addActions(self._actions["section_list"])
        spacing = QtWidgets.QWidget()
        spacing.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred
        )
        tb_section_list.insertWidget(self.action_show_section_overview, spacing)
        self.dock_sections.main_layout.insertWidget(1, tb_section_list)
        self.tool_bar_section_list = tb_section_list

    def _setup_toolbar(
        self, name: str, actions: list[QtGui.QAction], movable: bool = False
    ) -> QtWidgets.QToolBar:
        tb = QtWidgets.QToolBar()
        tb.setObjectName(name)
        tb.setMovable(movable)
        tb.addActions(actions)
        self.addToolBar(tb)
        return tb

    def _setup_menus(self) -> None:
        self.menuView.addActions(
            [self.dock_sections.toggleViewAction(), self.dock_status_log.toggleViewAction()]
        )
        self.menuView.addSeparator()
        self.menuView.addActions(
            [
                self.dock_processing.toggleViewAction(),
                self.dock_peaks.toggleViewAction(),
            ]
        )

        self.menuEdit.insertActions(
            self.action_show_section_overview,
            [self.dock_processing.toggleViewAction(), self.dock_peaks.toggleViewAction()],
        )
        self.menuEdit.insertSeparator(self.action_show_section_overview)

        self.menuHelp.addSeparator()
        self.menuHelp.addAction(self.dock_status_log.toggleViewAction())
        self.menuHelp.insertAction(self.action_show_user_guide, self.action_toggle_whats_this_mode)

    def hide_all_docks(self) -> None:
        self.dock_status_log.hide()
        self.dock_processing.hide()
        self.dock_peaks.hide()
        self.dock_sections.hide()

    def _finalize_setup(self) -> None:
        self.read_settings()
        self._connect_signals()
        self.show_section_confirm_cancel(False)
        self.hide_all_docks()
        self._on_page_changed(0)

    def _connect_signals(self) -> None:
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
        self.action_delete_section.triggered.connect(
            self.dock_sections.list_view.emit_delete_current_request
        )

        self.dock_sections.toggleViewAction().toggled.connect(self.dock_sections.setVisible)
        self.dock_processing.toggleViewAction().toggled.connect(self.dock_processing.setVisible)
        self.dock_peaks.toggleViewAction().toggled.connect(self.dock_peaks.setVisible)
        self.dock_status_log.toggleViewAction().toggled.connect(self.dock_status_log.setVisible)

        self.stackedWidget.currentChanged.connect(self._on_page_changed)

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

        self.dock_status_log.log_text_box.sig_log_message.connect(self.maybe_show_error_dialog)
        self.dock_sections.btn_confirm.clicked.connect(self.action_confirm_section.trigger)
        self.dock_sections.btn_cancel.clicked.connect(self.action_cancel_section.trigger)

        self.action_export_result.triggered.connect(self.show_export_dialog)

    @QtCore.Slot(QtCore.QPoint)
    def show_data_view_context_menu(self, pos: QtCore.QPoint) -> None:
        menu = QtWidgets.QMenu(self.table_view_import_data)
        menu.addAction("Refresh", self.sig_table_refresh_requested.emit)
        menu.exec(self.table_view_import_data.mapToGlobal(pos))

    @QtCore.Slot(int)
    def _on_page_changed(self, index: int) -> None:
        self.show_section_confirm_cancel(False)
        if index in {0, 2, 4}:
            self.tool_bar_editing.setEnabled(False)
            self.tool_bar_section_list.setEnabled(False)
            self.dock_sections.toggleViewAction().setChecked(False)
            self.dock_processing.toggleViewAction().setChecked(False)
            self.dock_peaks.toggleViewAction().setChecked(False)
            self.action_export_result.setEnabled(False)
        elif index == 1:
            self.tool_bar_editing.setEnabled(True)
            self.tool_bar_section_list.setEnabled(True)
            self.dock_sections.toggleViewAction().setChecked(True)
            self.dock_processing.toggleViewAction().setChecked(True)
            self.dock_peaks.toggleViewAction().setChecked(True)
            self.action_export_result.setEnabled(False)
        elif index == 3:
            self.tool_bar_editing.setEnabled(False)
            self.tool_bar_section_list.setEnabled(False)
            self.dock_sections.toggleViewAction().setChecked(False)
            self.dock_processing.toggleViewAction().setChecked(False)
            self.dock_peaks.toggleViewAction().setChecked(False)
            self.action_export_result.setEnabled(True)

    def show_section_confirm_cancel(self, show: bool) -> None:
        self.dock_sections.btn_container.setVisible(show)
        self.tool_bar_navigation.setEnabled(not show)

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
