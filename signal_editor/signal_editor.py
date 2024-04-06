import contextlib

import superqt
from PySide6 import QtCore, QtGui, QtWidgets

from .app import type_defs as _t
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
        self.main_window.action_open_file.triggered.connect(self.select_file)
        self.main_window.action_edit_metadata.triggered.connect(self.show_metadata_dialog)
        self.main_window.settings_editor.finished.connect(self.apply_settings)
        self.main_window.btn_load_data.clicked.connect(self.read_file)
        self.main_window.metadata_dialog.sig_property_has_changed.connect(self.update_metadata)

    def _connect_data_controller_signals(self) -> None:
        self.data_controller.sig_non_ascii_in_file_name.connect(self.show_non_ascii_warning)
        self.data_controller.sig_user_input_required.connect(self.show_metadata_dialog)
        self.data_controller.sig_new_metadata.connect(self.update_metadata_read_only_tree)

    def _disconnect_data_controller_signals(self) -> None:
        self.data_controller.sig_non_ascii_in_file_name.disconnect(self.show_non_ascii_warning)
        self.data_controller.sig_user_input_required.disconnect(self.show_metadata_dialog)
        self.data_controller.sig_new_metadata.disconnect(self.update_metadata_read_only_tree)

    @QtCore.Slot(dict)
    def update_metadata(self, metadata_dict: _t.MetadataUpdateDict) -> None:
        self.data_controller.update_metadata(metadata_dict)

    @QtCore.Slot(object)
    def update_metadata_read_only_tree(self, metadata: _t.Metadata) -> None:
        self.main_window.data_tree_widget_import_metadata.setData(metadata.to_dict(), hideRoot=True)
        self.main_window.data_tree_widget_import_metadata.collapseAll()

    @QtCore.Slot(list, bool)
    def show_non_ascii_warning(
        self, non_ascii_chars: list[tuple[int, tuple[str, list[tuple[str, int]]]]], is_edf: bool
    ) -> None:
        chars = {
            c[1][0]: [nc[1][1][0][0] for nc in non_ascii_chars if nc[1][0] == c[1][0]]
            for c in non_ascii_chars
        }

        msg = (
            "Non-ASCII characters found while reading from input file.\n"
            "This may cause issues when reading the file or exporting results.\n"
            f"If possible, rename the {'Channel' if is_edf else 'Column'} (see below), and try again.\n------\n"
            f"<b>{'Channel' if is_edf else 'Column'}</b>: {non_ascii_chars[0][1][0]}, <b>Non-ASCII characters</b>: {chars[non_ascii_chars[0][1][0]]}\n------\n"
            f"Rename the {'Channels' if is_edf else 'Columns'}?"
        )
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

    @QtCore.Slot()
    def show_metadata_dialog(self) -> None:
        metadata = None
        with superqt.utils.exceptions_as_dialog(
            icon=QtWidgets.QMessageBox.Icon.Warning,
            title="Error loading metadata",
            parent=self.main_window,
        ) as ctx:
            metadata = self.data_controller.metadata
        if ctx.exception is not None or metadata is None:
            return
        required_fields = metadata.required_fields

        file_name = metadata.file_name
        file_type = metadata.file_format
        columns = metadata.column_names

        self.main_window.metadata_dialog.combo_box_signal_column.clear()
        self.main_window.metadata_dialog.combo_box_signal_column.addItems(columns)
        if len(columns) > 1:
            self.main_window.metadata_dialog.combo_box_info_column.addItems(columns)
        if "sampling_rate" not in required_fields:
            sampling_rate = metadata.sampling_rate
            self.main_window.metadata_dialog.dbl_spin_box_sampling_rate.setValue(sampling_rate)
        if "signal_column" not in required_fields:
            signal_col = metadata.signal_column
            self.main_window.metadata_dialog.combo_box_signal_column.setCurrentText(signal_col)
        if "info_column" not in required_fields:
            info_col = metadata.info_column
            self.main_window.metadata_dialog.combo_box_info_column.setCurrentText(str(info_col))
        if "additional_info" not in required_fields:
            additional_info = metadata.additional_info
            self.main_window.metadata_dialog.data_tree_widget_additional_info.setData(
                additional_info
            )

        self.main_window.metadata_dialog.line_edit_file_name.setText(file_name)
        self.main_window.metadata_dialog.line_edit_file_type.setText(file_type)

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

        self.main_window.action_close_file.setEnabled(True)
        self.main_window.action_edit_metadata.setEnabled(True)

        with contextlib.suppress(Exception):
            self._disconnect_data_controller_signals()
            self.data_controller.setParent(None)

        self.data_controller = DataController(self)
        self._connect_data_controller_signals()

        self.data_controller.select_file(file_path)
        self.main_window.table_view_import_data.setModel(self.data_controller.base_df_model)

    @QtCore.Slot()
    def read_file(self) -> None:
        self.data_controller.read_file()

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
                self.plot_controller.signal_curve.setPen(value)
            case "rate_line_color":
                self.plot_controller.rate_curve.setPen(value)
            case "section_marker_color":
                for r in self.plot_controller.regions:
                    r.setBrush(color=value)
            case "float_visual_precision":
                if isinstance(value, int):
                    self.data_controller.base_df_model.set_float_precision(value)
            case _:
                pass

    @QtCore.Slot()
    def apply_settings(self) -> None:
        self.plot_controller.apply_settings()
