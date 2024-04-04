from PySide6 import QtCore, QtGui, QtWidgets

from .app.controllers.data_controller import DataController
from .app.controllers.plot_controller import PlotController
from .app.gui.main_window import MainWindow


class StatusUpdater(QtCore.QObject):
    sig_update_status_msg = QtCore.Signal(str)

    def __init__(self, parent: QtCore.QObject | None = None) -> None:
        super().__init__(parent)
        self.message_box = QtWidgets.QMessageBox()

    def update_status_msg(self, msg: str) -> None:
        self.sig_update_status_msg.emit(msg)


def check_string_for_non_ascii(string: str) -> tuple[bool, list[tuple[str, int]]]:
    """
    Checks a file name for possible non-ASCII characters.

    Parameters
    ----------
    string : str
        The string to check.

    Returns
    -------
    tuple[bool, list[tuple[str, int]]
        A tuple containing a boolean indicating whether non-ASCII characters were found and a list of tuples containing the detected non-ASCII characters and their positions in the input string.
    """
    non_ascii_chars = [(char, idx) for idx, char in enumerate(string) if ord(char) > 127]
    return bool(non_ascii_chars), non_ascii_chars


class SignalEditor(QtWidgets.QApplication):
    sig_open_rename_dialog = QtCore.Signal(list, bool)

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
        self.main_window.action_load_file.triggered.connect(self.select_file)
        self.main_window.settings_editor.finished.connect(self.apply_settings)
        # self.data_controller.sig_new_data_file_loaded.connect()
        self.data_controller.sig_non_ascii_in_file_name.connect(self.show_non_ascii_warning)
        self.data_controller.sig_user_input_required.connect(self.show_metadata_dialog)

    @QtCore.Slot(list, bool)
    def show_non_ascii_warning(
        self, non_ascii_chars: list[tuple[int, tuple[str, list[tuple[str, int]]]]], is_edf: bool
    ) -> None:
        chars = {
            c[1][0]: [nc[1][1][0][0] for nc in non_ascii_chars if nc[1][0] == c[1][0]]
            for c in non_ascii_chars
        }

        msg = f"""
        Non-ASCII characters found while reading from input file. This may cause issues when reading the file or exporting results. If possible, rename the {"Channel" if is_edf else "Column"}s (see below), and try again.:

        {'\n'.join([f'{"Channel" if is_edf else "Column"}: {col}, letters: {chars[col]}' for col in chars])}

        Rename the {"Channels" if is_edf else "Columns"}?
        """
        
        btn = QtWidgets.QMessageBox.warning(
            self.main_window,
            "Non-ASCII characters found",
            msg,
            QtWidgets.QMessageBox.StandardButton.Yes
            | QtWidgets.QMessageBox.StandardButton.No
            | QtWidgets.QMessageBox.StandardButton.Cancel,
        )
        if btn == QtWidgets.QMessageBox.StandardButton.Yes:
            self.sig_open_rename_dialog.emit([c[1][0] for c in non_ascii_chars], is_edf)

    @QtCore.Slot(list)
    def show_metadata_dialog(self, required_fields: list[str]) -> None:
        metadata = self.data_controller.metadata
        file_name = metadata.file_name
        file_type = metadata.file_format
        sampling_rate = metadata.sampling_rate
        signal_col = metadata.signal_column
        info_col = metadata.info_column
        additional_info = metadata.additional_info

        self.main_window.metadata_dialog.line_edit_file_name.setText(file_name)
        self.main_window.metadata_dialog.line_edit_file_type.setText(file_type)
        self.main_window.metadata_dialog.dbl_spin_box_sampling_rate.setValue(sampling_rate)
        self.main_window.metadata_dialog.combo_box_signal_column.setCurrentText(signal_col)
        self.main_window.metadata_dialog.combo_box_info_column.setCurrentText(str(info_col))
        self.main_window.metadata_dialog.data_tree_widget_additional_info.setData(additional_info)
        
        self.main_window.metadata_dialog.open()
        
        

    @QtCore.Slot()
    def select_file(self) -> None:
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self.main_window,
            "Open File",
            filter="Supported Files (*.csv *.txt *.xlsx *.feather *.edf)",
        )
        if not file_path:
            return

        self.data_controller.select_file(file_path)

    @QtCore.Slot(str, object)
    def _update_setting(self, name: str, value: QtGui.QColor | str | int | float | None) -> None:
        if value is None:
            return
        match name:
            case "background_color":
                self.plot_controller.set_background_color(value)
            case "foreground_color":
                self.plot_controller.set_foreground_color(value)
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

    @QtCore.Slot()
    def apply_settings(self) -> None:
        self.plot_controller.apply_settings()
