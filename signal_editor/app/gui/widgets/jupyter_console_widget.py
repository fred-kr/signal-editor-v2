import jupyter_client
import qfluentwidgets as qfw
from PySide6 import QtCore, QtGui, QtWidgets
from qframelesswindow import FramelessWindow
from qtconsole import inprocess
from rich import inspect, print

from ..icons import SignalEditorIcon as Icons


class JupyterConsoleWidget(inprocess.QtInProcessRichJupyterWidget):
    def __init__(self) -> None:
        super().__init__()
        self.set_default_style("linux")

        self.kernel_manager: inprocess.QtInProcessKernelManager = inprocess.QtInProcessKernelManager()
        self.kernel_manager.start_kernel()

        self.kernel_client: jupyter_client.blocking.client.BlockingKernelClient = self.kernel_manager.client()

        self.kernel_client.start_channels()

        app_inst = QtWidgets.QApplication.instance()
        if app_inst is not None:
            app_inst.aboutToQuit.connect(self.shutdown_kernel)

    @QtCore.Slot()
    def shutdown_kernel(self) -> None:
        self.kernel_client.stop_channels()
        self.kernel_manager.shutdown_kernel()


class ConsoleWindow(FramelessWindow):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self.toggle_view_action = qfw.Action("Show Console", self)
        self.toggle_view_action.setIcon(Icons.Code.icon())
        self.toggle_view_action.setCheckable(True)
        self.toggle_view_action.toggled.connect(self.setVisible)

        layout = QtWidgets.QVBoxLayout()

        self.console = JupyterConsoleWidget()
        layout.addWidget(self.titleBar)  # type: ignore
        layout.addWidget(self.console)  # type: ignore

        self.setLayout(layout)
        self.resize(900, 600)

        self._prepare_console()

    def _prepare_console(self) -> None:
        if self.console.kernel_manager.kernel is None:
            return
        if self.console.kernel_manager.kernel.shell is None:
            return
        self.console.kernel_manager.kernel.shell.push(
            dict(
                app=QtWidgets.QApplication.instance(),
                pp=print,
                inspect=inspect,
                qtc=QtCore,
                qtg=QtGui,
                qtw=QtWidgets,
            )
        )
        self.console.execute("whos")

    @QtCore.Slot(QtGui.QCloseEvent)
    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        with QtCore.QSignalBlocker(self.toggle_view_action):
            self.toggle_view_action.setChecked(False)
        return super().closeEvent(event)

    @QtCore.Slot(bool)
    def setVisible(self, visible: bool) -> None:
        self.toggle_view_action.setChecked(visible)
        super().setVisible(visible)
