from PySide6 import QtCore, QtGui, QtWidgets

from .app.controllers.data_controller import DataController
from .app.controllers.plot_controller import PlotController
from .app.gui.main_window import MainWindow


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

        self.connect_qt_signals()

    def connect_qt_signals(self) -> None:
        self.main_window.settings_editor.sig_setting_changed.connect(self._update_setting)
        self.main_window.action_load_file.triggered.connect(self.read_file)

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

    @QtCore.Slot()
    def read_file(self) -> None:
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self.main_window,
            "Open File",
            filter="Supported Files (*.csv *.txt *.xlsx *.feather *.edf)",
        )
        if not file_path:
            return
        self.data_controller.read_file(file_path)
    @QtCore.Slot(str, object)
    def _update_setting(self, name: str, value: QtGui.QColor | str | int | float | None) -> None:
        if value is None:
            return
        match name:
            case "background_color":
                self.plot_controller.change_plot_bg_color(value)
            case "foreground_color":
                self.plot_controller.change_plot_fg_color(value)
            case "point_color":
                self.plot_controller.peak_scatter.setBrush(color=value)
            case "signal_line_color":
                self.plot_controller.signal_curve.setPen(color=value)
            case "rate_line_color":
                self.plot_controller.rate_curve.setPen(color=value)
            case "section_marker_color":
                for r in self.plot_controller.regions:
                    r.setBrush(color=value)
            case _:
                pass
