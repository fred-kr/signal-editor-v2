import typing as t

from PySide6 import QtCore, QtGui, QtWidgets

from ...ui.ui_dialog_metadata import Ui_MetadataDialog
from ...ui.ui_dock_session_properties import Ui_DockWidgetSessionProperties
from ...ui.ui_dock_status_log import Ui_DockWidgetLogOutput
from ...ui.ui_main_window import Ui_MainWindow
from .widgets.settings_editor import SettingsEditor


class SessionPropertiesDock(QtWidgets.QDockWidget, Ui_DockWidgetSessionProperties):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.setVisible(False)


class StatusMessageDock(QtWidgets.QDockWidget, Ui_DockWidgetLogOutput):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.setVisible(False)

        self.setWindowIcon(QtGui.QIcon(":/icons/sys_monitor"))


class MetadataDialog(QtWidgets.QDialog, Ui_MetadataDialog):
    sig_property_has_changed = QtCore.Signal(dict)

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setupUi(self)

        self.setWindowIcon(QtGui.QIcon(":/icons/properties"))

    @QtCore.Slot()
    def accept(self) -> None:
        metadata_dict = {
            "sampling_rate": self.dbl_spin_box_sampling_rate.value(),
            "signal_column": self.combo_box_signal_column.currentText(),
            "info_column": self.combo_box_info_column.currentText(),
            "signal_column_index": self.combo_box_signal_column.currentIndex(),
            "info_column_index": self.combo_box_info_column.currentIndex(),
        }
        self.sig_property_has_changed.emit(metadata_dict)

        super().accept()


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.tool_bar_navigation.setWindowIcon(QtGui.QIcon(":/icons/navigation"))

        dock_session_properties = SessionPropertiesDock(self)
        self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, dock_session_properties)
        self.dock_session_properties = dock_session_properties

        dock_status_log = StatusMessageDock(self)
        self.addDockWidget(QtCore.Qt.DockWidgetArea.BottomDockWidgetArea, dock_status_log)
        self.dock_status_log = dock_status_log
        self.text_status_log = dock_status_log.plain_text_edit_logging

        self.settings_editor = SettingsEditor(self)

        self.metadata_dialog = MetadataDialog(self)

        self.stackedWidget.setCurrentIndex(0)
        self.action_show_import_page.setChecked(True)

        self.tool_bar_editing.setVisible(False)

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

        self.stackedWidget.currentChanged.connect(
            lambda index: self.tool_bar_editing.setVisible(index == 1)  # pyright: ignore[reportUnknownArgumentType, reportUnknownLambdaType]
        )

        self.action_show_settings.triggered.connect(self.show_settings)

    def setup_menus(self) -> None:
        action_toggle_dock_session_properties = self.dock_session_properties.toggleViewAction()
        action_toggle_dock_session_properties.setIcon(QtGui.QIcon(":/icons/properties"))
        action_toggle_dock_session_properties.setText("Show Session Properties")
        self.menuView.addAction(action_toggle_dock_session_properties)

        action_toggle_dock_status_log = self.dock_status_log.toggleViewAction()
        action_toggle_dock_status_log.setIcon(QtGui.QIcon(":/icons/processor"))
        action_toggle_dock_status_log.setText("Show Status Log")
        self.menuView.addAction(action_toggle_dock_status_log)

        action_toggle_tb_edit = self.tool_bar_editing.toggleViewAction()
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

    @QtCore.Slot(object)
    def _restore_settings(self, initial_setting_state: dict[str, t.Any]) -> None:
        settings = QtCore.QSettings()
        for k, v in initial_setting_state.items():
            if v != settings.value(k):
                settings.setValue(k, v)
        self.settings_editor.settings_tree.refresh()

    @QtCore.Slot(QtGui.QCloseEvent)
    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        self.write_settings()
        self.settings_editor.done(QtWidgets.QDialog.DialogCode.Rejected)
        return super().closeEvent(event)
