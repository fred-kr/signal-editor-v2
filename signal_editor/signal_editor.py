from PySide6 import QtCore, QtWidgets

from .app.controllers.data_controller import DataController
from .app.controllers.plot_controller import PlotController
from .app.gui.main_window import MainWindow
from .app.controllers.config_controller2 import ConfigController as Config

class StatusUpdater(QtCore.QObject):
    sig_update_status_msg = QtCore.Signal(str)

    def __init__(self, parent: QtCore.QObject | None = None) -> None:
        super().__init__(parent)

    def update_status_msg(self, msg: str) -> None:
        self.sig_update_status_msg.emit(msg)


class SignalEditor(QtWidgets.QApplication):
    def __init__(self, args: list[str]) -> None:
        super().__init__(args)
        self.setOrganizationName("AWI")
        self.setApplicationName("Signal Editor")
        self.main_window = MainWindow()
        self.data_controller = DataController(self)
        self.plot_controller = PlotController(
            self,
            self.main_window.pg_graphics_layout_widget,
            self.main_window.mpl_widget,
        )
        self.config_controller = Config.instance()
        self.connect_qt_signals()
    
    def connect_qt_signals(self) -> None:
        self.main_window.btn_plot_bg_color.sigColorChanging.connect(self.plot_controller.change_plot_bg_color)
        self.main_window.btn_plot_fg_color.sigColorChanging.connect(self.plot_controller.change_plot_fg_color)
        
    def reset(self) -> None:
        self.plot_controller.reset()
        self.plot_controller.setParent(None)
        self.plot_controller = PlotController(
            self,
            self.main_window.pg_graphics_layout_widget,
            self.main_window.mpl_widget,
        )

        # self.data_controller.reset()
        self.data_controller.setParent(None)
        self.data_controller = DataController(self)
