import sys
from PySide6 import QtWidgets

from qtconsole.rich_jupyter_widget import RichJupyterWidget
from qtconsole.manager import QtKernelManager


USE_KERNEL = "ir"

def make_jupyter_widget_with_kernel(kernel_name: str = USE_KERNEL) -> RichJupyterWidget:
    manager = QtKernelManager(kernel_name=kernel_name)
    manager.start_kernel()

    client = manager.client()
    client.start_channels()

    jupyter_widget = RichJupyterWidget()
    jupyter_widget.kernel_manager = manager
    jupyter_widget.kernel_client = client

    return jupyter_widget

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.jupyter_widget = make_jupyter_widget_with_kernel()
        self.setCentralWidget(self.jupyter_widget)

    def shutdown_kernel(self) -> None:
        self.jupyter_widget.kernel_client.stop_channels()
        self.jupyter_widget.kernel_manager.shutdown_kernel()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.aboutToQuit.connect(window.shutdown_kernel)
    sys.exit(app.exec())