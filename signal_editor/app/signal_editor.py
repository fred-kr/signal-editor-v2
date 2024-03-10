from PySide6 import QtCore

from .controllers.data_controller import DataController
from .controllers.plot_controller import PlotController


class StatusUpdater(QtCore.QObject):
    sig_update_status_msg = QtCore.Signal(str)

    def __init__(self, parent: QtCore.QObject | None = None) -> None:
        super().__init__(parent)

    def update_status_msg(self, msg: str) -> None:
        self.sig_update_status_msg.emit(msg)


class SignalEditor(QtCore.QObject):
    def __init__(self, parent: QtCore.QObject | None = None) -> None:
        super().__init__(parent)
        self.data_controller = DataController(self)
        self.plot_controller = PlotController(self)
        self.main_window = ...

    def reset(self) -> None:
        self.plot_controller.reset()
        self.plot_controller.setParent(None)
        self.plot_controller = PlotController(self)

        # self.data_controller.reset()
        self.data_controller.setParent(None)
        self.data_controller = DataController(self)
