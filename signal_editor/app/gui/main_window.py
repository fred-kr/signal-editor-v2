import typing as t

import pyqtgraph as pg
from loguru import logger
from PySide6 import QtCore, QtGui, QtWidgets

from ...ui.ui_dialog_metadata import Ui_MetadataDialog
from ...ui.ui_dock_session_properties import Ui_DockWidgetSessionProperties
from ...ui.ui_main_window import Ui_MainWindow
from .widgets.settings_editor import SettingsEditor
from .widgets.text_edit_logger import StatusMessageDock


class SessionPropertiesDock(QtWidgets.QDockWidget, Ui_DockWidgetSessionProperties):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.setVisible(False)


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


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setupUi(self)
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

        dock_session_properties = SessionPropertiesDock(self)
        self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, dock_session_properties)
        self.dock_session_properties = dock_session_properties

        dock_status_log = StatusMessageDock(self)
        self.addDockWidget(QtCore.Qt.DockWidgetArea.BottomDockWidgetArea, dock_status_log)
        self.dock_status_log = dock_status_log

        self.settings_editor = SettingsEditor(self)

        self.metadata_dialog = MetadataDialog(self)

        self.stackedWidget.setCurrentIndex(0)
        self.action_show_import_page.setChecked(True)

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
            self.metadata_dialog.spin_box_sampling_rate.setValue
        )
        self.combo_box_info_column_import_page.currentTextChanged.connect(
            self.metadata_dialog.combo_box_info_column.setCurrentText
        )
        self.combo_box_signal_column_import_page.currentTextChanged.connect(
            self.metadata_dialog.combo_box_signal_column.setCurrentText
        )
        self.metadata_dialog.spin_box_sampling_rate.valueChanged.connect(
            self.spin_box_sampling_rate_import_page.setValue
        )
        self.metadata_dialog.combo_box_info_column.currentTextChanged.connect(
            self.combo_box_info_column_import_page.setCurrentText
        )
        self.metadata_dialog.combo_box_signal_column.currentTextChanged.connect(
            self.combo_box_signal_column_import_page.setCurrentText
        )

    @QtCore.Slot(int)
    def change_context_actions(self, index: int) -> None:
        if index == 0:
            self._show_import_page_actions()
        elif index == 1:
            self._show_edit_page_actions()
        elif index == 2:
            self._show_result_page_actions()
        elif index == 3:
            self._show_export_page_actions()
        elif index == 4:
            self._show_info_page_actions()

    def _show_import_page_actions(self) -> None:
        self.tool_bar_context_actions.clear()
        self.tool_bar_context_actions.addAction(self.action_open_file)
        self.tool_bar_context_actions.addAction(self.action_edit_metadata)
        self.tool_bar_context_actions.addAction(self.action_close_file)

    def _show_edit_page_actions(self) -> None:
        self.tool_bar_context_actions.clear()
        # TODO: Add actions

    def _show_result_page_actions(self) -> None:
        self.tool_bar_context_actions.clear()
        # TODO: Add actions

    def _show_export_page_actions(self) -> None:
        self.tool_bar_context_actions.clear()
        self.tool_bar_context_actions.addAction(self.action_export_result)

    def _show_info_page_actions(self) -> None:
        self.tool_bar_context_actions.clear()
        # TODO: Add actions

    def setup_menus(self) -> None:
        action_toggle_dock_session_properties = self.dock_session_properties.toggleViewAction()
        action_toggle_dock_session_properties.setIcon(QtGui.QIcon(":/icons/properties"))
        action_toggle_dock_session_properties.setText("Show Session Properties")
        self.menuView.addAction(action_toggle_dock_session_properties)

        action_toggle_dock_status_log = self.dock_status_log.toggleViewAction()
        action_toggle_dock_status_log.setIcon(QtGui.QIcon(":/icons/processor"))
        action_toggle_dock_status_log.setText("Show Status Log")
        self.menuView.addAction(action_toggle_dock_status_log)

        action_toggle_tb_edit = self.tool_bar_context_actions.toggleViewAction()
        action_toggle_tb_edit.setIcon(QtGui.QIcon(":/icons/view_app_monitor"))
        action_toggle_tb_edit.setText("Toggle Editing Toolbar")
        self.menuView.addAction(action_toggle_tb_edit)

        action_toggle_nav_toolbar = self.tool_bar_navigation.toggleViewAction()
        action_toggle_nav_toolbar.setIcon(QtGui.QIcon(":/icons/navigation"))
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
