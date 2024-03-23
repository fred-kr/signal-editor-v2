import pyqtgraph as pg
from PySide6 import QtCore, QtGui, QtWidgets

from ...ui.ui_dock_session_properties import Ui_DockWidgetSessionProperties
from ...ui.ui_dock_status_log import Ui_DockWidgetLogOutput
from ...ui.ui_main_window import Ui_MainWindow
from ...ui.ui_tab_widget_settings import Ui_TabWidgetSettings


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


class SettingsEditor(QtWidgets.QTabWidget, Ui_TabWidgetSettings):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.setVisible(False)


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.tool_bar_navigation.setWindowIcon(QtGui.QIcon(":/icons/navigation"))

        dock_session_properties = SessionPropertiesDock()
        self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, dock_session_properties)
        self.dock_session_properties = dock_session_properties

        dock_status_log = StatusMessageDock()
        self.addDockWidget(QtCore.Qt.DockWidgetArea.BottomDockWidgetArea, dock_status_log)
        self.dock_status_log = dock_status_log

        self.settings_editor = SettingsEditor()

        self.stackedWidget.setCurrentIndex(0)
        self.action_show_import_page.setChecked(True)

        self.btn_plot_bg_color = pg.ColorButton()
        self.btn_plot_bg_color.setToolTip("Change the plots background color")

        self.btn_plot_fg_color = pg.ColorButton()
        self.btn_plot_fg_color.setToolTip("Change the plots foreground color")

        self.tool_bar_editing.addWidget(self.btn_plot_bg_color)
        self.tool_bar_editing.addWidget(self.btn_plot_fg_color)

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
            lambda index: self.tool_bar_editing.setVisible(index == 1)
        )
        self.action_show_settings.triggered.connect(self.settings_editor.show)

    def setup_menus(self) -> None:
        action_toggle_dock_session_properties = self.dock_session_properties.toggleViewAction()
        action_toggle_dock_session_properties.setIcon(QtGui.QIcon(":/icons/properties"))
        action_toggle_dock_session_properties.setText("Show Session Properties")
        self.menuEdit.addAction(action_toggle_dock_session_properties)

        action_toggle_dock_status_log = self.dock_status_log.toggleViewAction()
        action_toggle_dock_status_log.setIcon(QtGui.QIcon(":/icons/processor"))
        action_toggle_dock_status_log.setText("Show Status Log")
        self.menuEdit.addAction(action_toggle_dock_status_log)

        action_toggle_tb_edit = self.tool_bar_editing.toggleViewAction()
        action_toggle_tb_edit.setIcon(QtGui.QIcon(":/icons/view_app_monitor"))
        action_toggle_tb_edit.setText("Toggle Editing Toolbar")
        self.menuEdit.addAction(action_toggle_tb_edit)

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

    def read_settings(self) -> None:
        settings = QtCore.QSettings()
        settings.beginGroup("MainWindow")
        self.restoreGeometry(settings.value("geometry", QtCore.QByteArray()))
        self.restoreState(settings.value("state", QtCore.QByteArray()))
        settings.endGroup()

    @QtCore.Slot(QtGui.QCloseEvent)
    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        self.write_settings()
        return super().closeEvent(event)
