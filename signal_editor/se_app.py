import contextlib
import enum
import typing as t
from pathlib import Path

import numpy as np
import numpy.typing as npt
import superqt
from loguru import logger
from PySide6 import QtCore, QtWidgets

from .app import type_defs as _t
from .app.config import Config
from .app.controllers.data_controller import DataController
from .app.controllers.plot_controller import PlotController
from .app.core.file_io import write_hdf5
from .app.core.peak_detection import find_peaks
from .app.enum_defs import (
    PeakDetectionMethod,
    PreprocessPipeline,
    StandardizationMethod,
)
from .app.gui.main_window import MainWindow
from .app.utils import safe_multi_disconnect

if t.TYPE_CHECKING:
    from .app.models.metadata import FileMetadata


class SignalEditor(QtWidgets.QApplication):
    sig_peaks_updated: t.ClassVar[QtCore.Signal] = QtCore.Signal()

    def __init__(self, args: list[str]) -> None:
        super().__init__(args)
        self.setOrganizationName("AWI")
        self.setApplicationName("Signal Editor")
        self.mw = MainWindow()
        self.data = DataController(self)
        self.plot = PlotController(self, self.mw)
        self.config = Config()

        self.recent_files = self._retrieve_recent_files()

        self._connect_signals()

    def _connect_signals(self) -> None:
        self.sig_peaks_updated.connect(self.refresh_peak_data)

        # self.mw.dialog_settings.sig_setting_changed.connect(self._update_setting)
        self.mw.action_open_file.triggered.connect(self.open_file)
        self.mw.action_edit_metadata.triggered.connect(lambda: self.show_metadata_dialog([]))
        self.mw.dialog_config.finished.connect(self.apply_settings)
        self.mw.btn_load_data.clicked.connect(self.read_data)
        self.mw.dialog_meta.sig_property_has_changed.connect(self.update_metadata)
        self.mw.btn_open_file.clicked.connect(self.open_file)
        self.mw.action_close_file.triggered.connect(self.close_file)
        self.mw.btn_close_file.clicked.connect(self.close_file)
        self.mw.action_about_qt.triggered.connect(self.aboutQt)
        self.mw.dialog_export.sig_export_confirmed.connect(self.export_result)
        self.mw.list_widget_recent_files.itemDoubleClicked.connect(self._open_recent_file)
        self.mw.sig_table_refresh_requested.connect(self.refresh_data_view)

        self.mw.spin_box_sampling_rate_import_page.editingFinished.connect(self.update_sampling_rate)
        self.mw.combo_box_info_column_import_page.currentTextChanged.connect(self.update_info_column)
        self.mw.combo_box_signal_column_import_page.currentTextChanged.connect(self.update_signal_column)

        # Section actions
        self.mw.action_create_new_section.toggled.connect(self.maybe_new_section)
        self.mw.action_confirm_section.triggered.connect(self._on_confirm_new_section)
        self.mw.action_cancel_section.triggered.connect(self._on_cancel_new_section)
        self.mw.action_show_section_overview.toggled.connect(self.plot.toggle_regions)

        self.mw.action_toggle_auto_scaling.toggled.connect(self.plot.toggle_auto_scaling)

        self.mw.dock_sections.list_view.sig_delete_current_item.connect(self.delete_section)
        self.mw.dock_processing.sig_filter_requested.connect(self.filter_active_signal)
        self.mw.dock_processing.sig_pipeline_requested.connect(self.run_preprocess_pipeline)
        self.mw.dock_processing.sig_standardization_requested.connect(self.standardize_active_signal)
        self.mw.dock_processing.sig_data_reset_requested.connect(self.restore_original_signal)

        self.mw.dock_peaks.sig_peak_detection_requested.connect(self.run_peak_detection)
        self.mw.dock_peaks.sig_clear_peaks_requested.connect(self.clear_peaks)

        self.mw.action_find_peaks_in_selection.triggered.connect(self.find_peaks_in_selection)
        self.mw.action_remove_peaks_in_selection.triggered.connect(self.plot.remove_peaks_in_selection)
        self.plot.sig_scatter_data_changed.connect(self.handle_peak_edit)

    def _retrieve_recent_files(self) -> list[str]:
        # settings = QtCore.QSettings()
        # recent_files: list[str] | None = settings.value("Internal/recent_files", None)  # type: ignore
        recent_files = self.config.internal.RecentFiles
        # if recent_files is None:
        #     recent_files = []
        self.mw.list_widget_recent_files.clear()
        self.mw.list_widget_recent_files.addItems(recent_files)
        return recent_files

    @QtCore.Slot()
    def clear_peaks(self) -> None:
        self.plot.clear_peaks()
        self.data.active_section.reset_peaks()

    @QtCore.Slot()
    def find_peaks_in_selection(self) -> None:
        rect = self.plot.get_selection_area()
        if rect is None:
            return

        active_section = self.data.active_section
        left, right = int(rect.left()), int(rect.right())
        self.plot.remove_selection_rect()

        peak_method = PeakDetectionMethod(self.mw.dock_peaks.enum_combo_peak_method.currentEnum())
        peak_params = self.mw.dock_peaks.get_peak_detection_parameters(peak_method)

        edge_buffer = 10
        b_left, b_right = left + edge_buffer, right - edge_buffer
        b_left = np.maximum(b_left, 0)
        b_right = np.minimum(b_right, active_section.processed_signal.len())
        data = active_section.processed_signal[b_left:b_right].to_numpy()
        peaks = find_peaks(
            data,
            sampling_rate=active_section.sampling_rate,
            method=peak_method,
            method_parameters=peak_params,
        )
        peaks = peaks + b_left
        active_section.update_peaks("add", peaks)
        self.sig_peaks_updated.emit()

    @QtCore.Slot(str, object)
    def handle_peak_edit(self, action: _t.UpdatePeaksAction, indices: npt.NDArray[np.int32]) -> None:
        self.data.active_section.update_peaks(action, indices)
        self.sig_peaks_updated.emit()

    @QtCore.Slot()
    def refresh_peak_data(self) -> None:
        pos = self.data.active_section.get_peak_pos().to_numpy(structured=True)
        self.plot.set_peak_data(pos["x"], pos["y"])
        rate_data = self.data.active_section.get_rate_data().to_numpy(structured=True)
        self.plot.set_rate_data(x_data=rate_data["x"], y_data=rate_data["y"])

    @QtCore.Slot(dict)
    def filter_active_signal(self, filter_params: _t.SignalFilterParameters) -> None:
        self.data.active_section.filter_signal(pipeline=PreprocessPipeline.PPGElgendi, **filter_params)
        self.refresh_plot_data()

    @QtCore.Slot()
    def restore_original_signal(self) -> None:
        self.data.active_section.reset_signal()
        self.refresh_plot_data()
        self.plot.clear_peaks()

    @QtCore.Slot(object)
    def run_preprocess_pipeline(self, pipeline: PreprocessPipeline) -> None:
        if pipeline not in {PreprocessPipeline.PPGElgendi, PreprocessPipeline.ECGNeuroKit2}:
            return
        self.data.active_section.filter_signal(pipeline)
        self.refresh_plot_data()

    @QtCore.Slot(dict)
    def standardize_active_signal(self, standardization_params: _t.StandardizationParameters) -> None:
        method = standardization_params.pop("method")
        window_size = standardization_params.pop("window_size")
        robust = method == StandardizationMethod.ZScoreRobust
        self.data.active_section.scale_signal(method=method, robust=robust, window_size=window_size)
        self.refresh_plot_data()

    def refresh_plot_data(self) -> None:
        self.plot.set_signal_data(self.data.active_section.processed_signal.to_numpy())

    @QtCore.Slot(enum.StrEnum, dict)
    def run_peak_detection(self, method: PeakDetectionMethod, params: _t.PeakDetectionMethodParameters) -> None:
        self.data.active_section.detect_peaks(method, params)
        self.sig_peaks_updated.emit()

    @QtCore.Slot()
    def _on_sig_new_data(self) -> None:
        self.mw.dock_sections.list_view.setModel(self.data.sections)
        self.mw.dock_sections.list_view.setCurrentIndex(self.data.base_section_index)
        self.update_sampling_rate()

    def _connect_data_controller_signals(self) -> None:
        self.data.sig_user_input_required.connect(self.show_metadata_dialog)
        self.data.sig_new_metadata.connect(self.update_metadata_widgets)
        self.data.sig_new_data.connect(self._on_sig_new_data)
        self.mw.dock_sections.list_view.pressed.connect(self.data.set_active_section)
        self.data.sig_active_section_changed.connect(self._on_active_section_changed)

    def _disconnect_data_controller_signals(self) -> None:
        sender = self.data
        signal_slot_pairs = [
            (sender.sig_user_input_required, self.show_metadata_dialog),
            (sender.sig_new_metadata, self.update_metadata_widgets),
            (sender.sig_new_data, self._on_sig_new_data),
            (sender.sig_active_section_changed, self._on_active_section_changed),
            (self.mw.dock_sections.list_view.pressed, sender.set_active_section),
        ]
        safe_multi_disconnect(sender, signal_slot_pairs)

    @QtCore.Slot(bool)
    def maybe_new_section(self, checked: bool) -> None:
        self.mw.show_section_confirm_cancel(checked)
        if not checked:
            self.plot.hide_region_selector()
            return
        bounds = (0, self.data.base_df.height - 1)
        self.plot.show_region_selector(bounds)

    @QtCore.Slot()
    def _on_confirm_new_section(self) -> None:
        if self.plot.region_selector is None:
            return
        if not self.plot.region_selector.isVisible():
            return
        start, stop = self.plot.region_selector.getRegion()
        self.data.create_section(start, stop)
        self.plot.hide_region_selector()
        self.mw.show_section_confirm_cancel(False)
        self.mw.action_create_new_section.setChecked(False)
        self.plot.mark_region(start, stop)

    @QtCore.Slot()
    def _on_cancel_new_section(self) -> None:
        self.plot.hide_region_selector()
        self.mw.show_section_confirm_cancel(False)
        self.mw.action_create_new_section.setChecked(False)

    @QtCore.Slot(QtCore.QModelIndex)
    def delete_section(self, index: QtCore.QModelIndex) -> None:
        s = self.data.sections.get_section(index)
        if s is not None:
            bounds = s.global_bounds
            self.plot.remove_region(bounds=bounds)
        self.data.delete_section(index)
        self.mw.dock_sections.list_view.setCurrentIndex(self.data.base_section_index)
        logger.info(f"Deleted section {index.row():03}")

    @QtCore.Slot(bool)
    def _on_active_section_changed(self, has_peaks: bool) -> None:
        section = self.data.active_section
        is_base_section = section is self.data.get_base_section()
        has_results = not section.result_data.is_empty()

        self.mw.action_create_new_section.setEnabled(is_base_section)
        self.mw.action_delete_section.setEnabled(not is_base_section)
        self.mw.action_show_section_overview.setEnabled(is_base_section)
        self.mw.action_show_section_overview.setChecked(False)
        self.mw.dock_processing.setEnabled(not is_base_section)
        self.mw.dock_peaks.setEnabled(not is_base_section)
        self.mw.set_active_section_label(section.section_id.pretty_name())
        self.plot.set_signal_data(section.processed_signal.to_numpy())
        self.plot.clear_peaks()
        if has_peaks:
            self.sig_peaks_updated.emit()
        if has_results:
            result = section.result_data.to_numpy(structured=True)
            self.plot.draw_rolling_rate(result["x"], result["y"])
        # Update the table view to show the current sections' data
        self.mw.table_view_import_data.setModel(self.data.active_section_model)
        self.mw.label_showing_data_table.setText(f"Showing: {section.section_id.pretty_name()}")

    @QtCore.Slot()
    def refresh_data_view(self) -> None:
        self.data.active_section_model.set_dataframe(self.data.active_section.data)

    @QtCore.Slot(dict)
    def update_metadata(self, metadata_dict: _t.MetadataUpdateDict) -> None:
        sampling_rate = metadata_dict.get("sampling_rate", None)
        info_col = metadata_dict.get("info_column", None)
        signal_col = metadata_dict.get("signal_column", None)
        self.data.update_metadata(sampling_rate, signal_col, info_col)

    @QtCore.Slot(object)
    def update_metadata_widgets(self, metadata: "FileMetadata") -> None:
        metadata_dict = metadata.to_dict()
        self.mw.data_tree_widget_import_metadata.setData(metadata_dict, hideRoot=True)
        self.mw.data_tree_widget_import_metadata.collapseAll()
        self.mw.spin_box_sampling_rate_import_page.setValue(metadata.sampling_rate)

    @QtCore.Slot(list)
    def show_metadata_dialog(self, required_fields: list[str]) -> None:
        metadata = None
        with superqt.utils.exceptions_as_dialog(
            icon=QtWidgets.QMessageBox.Icon.Warning,
            title="Error loading metadata",
            parent=self.mw,
        ) as ctx:
            metadata = self.data.metadata
        if ctx.exception is not None or metadata is None:
            return

        file_name = metadata.file_name
        file_type = metadata.file_format
        info_col = metadata.info_column

        self.mw.dialog_meta.combo_box_signal_column.setModel(metadata.columns)
        self.mw.dialog_meta.combo_box_info_column.setModel(metadata.columns)
        if "sampling_rate" not in required_fields:
            sampling_rate = metadata.sampling_rate
            self.mw.dialog_meta.spin_box_sampling_rate.setValue(sampling_rate)
            self.mw.spin_box_sampling_rate_import_page.setValue(sampling_rate)
        if "signal_column" not in required_fields:
            signal_col = metadata.signal_column
            self.mw.dialog_meta.combo_box_signal_column.setCurrentText(signal_col)
            self.mw.combo_box_signal_column_import_page.setCurrentText(signal_col)

        self.mw.dialog_meta.combo_box_info_column.setCurrentText(info_col)
        self.mw.combo_box_info_column_import_page.setCurrentText(info_col)

        self.mw.dialog_meta.line_edit_file_name.setText(file_name)
        self.mw.dialog_meta.line_edit_file_type.setText(file_type)

        self.mw.dialog_meta.open()

    @QtCore.Slot()
    def update_sampling_rate(self) -> None:
        sampling_rate = self.mw.spin_box_sampling_rate_import_page.value()
        self.data.update_metadata(sampling_rate=sampling_rate)
        self.plot.update_time_axis_scale(sampling_rate)
        self.mw.dock_processing.update_frequency_sliders(sampling_rate)
        logger.info(f"Sampling rate set to {sampling_rate} Hz.")

    @QtCore.Slot(str)
    def update_signal_column(self, signal_column: str) -> None:
        self.data.update_metadata(signal_col=signal_column)
        logger.info(f"Signal column set to '{signal_column}'.")

    @QtCore.Slot(str)
    def update_info_column(self, info_column: str) -> None:
        self.data.update_metadata(info_col=info_column)
        logger.info(f"Info column set to '{info_column}'.")

    def _set_column_models(self) -> None:
        self.mw.combo_box_info_column_import_page.addItems(self.data.metadata.columns.stringList())
        self.mw.combo_box_signal_column_import_page.addItems(self.data.metadata.columns.stringList())
        self.mw.dialog_meta.combo_box_signal_column.setModel(self.data.metadata.columns)
        self.mw.dialog_meta.combo_box_info_column.setModel(self.data.metadata.columns)

        with contextlib.suppress(Exception):
            self.mw.combo_box_info_column_import_page.setCurrentText(self.data.metadata.info_column)
            self.mw.combo_box_signal_column_import_page.setCurrentText(self.data.metadata.signal_column)

    def _clear_column_models(self) -> None:
        with QtCore.QSignalBlocker(self.mw.combo_box_info_column_import_page):
            self.mw.combo_box_info_column_import_page.clear()
        with QtCore.QSignalBlocker(self.mw.combo_box_signal_column_import_page):
            self.mw.combo_box_signal_column_import_page.clear()
        with QtCore.QSignalBlocker(self.mw.dialog_meta.combo_box_info_column):
            self.mw.dialog_meta.combo_box_signal_column.clear()
        with QtCore.QSignalBlocker(self.mw.dialog_meta.combo_box_signal_column):
            self.mw.dialog_meta.combo_box_info_column.clear()
        self.mw.data_tree_widget_import_metadata.clear()

    @QtCore.Slot()
    def open_file(self) -> None:
        # settings = QtCore.QSettings()
        # default_data_dir = str(settings.value("Misc/data_folder", self.applicationDirPath()))
        default_data_dir = self.config.internal.InputDir
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self.mw,
            "Open File",
            default_data_dir,
            filter="Supported Files (*.csv *.txt *.tsv *.xlsx *.feather *.edf)",
        )
        if not file_path:
            return

        self.close_file()

        self.config.internal.InputDir = Path(file_path).parent.resolve().as_posix()
        self.config.save()
        # settings.setValue("Misc/data_folder", Path(file_path).parent.resolve().as_posix())
        self._on_file_opened(file_path)

    def update_recent_files(self, file_path: str) -> None:
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        self.recent_files.insert(0, file_path)
        self.recent_files = self.recent_files[:10]
        self.config.internal.RecentFiles = self.recent_files
        self.config.save()
        # settings = QtCore.QSettings()
        # settings.setValue("Internal/recent_files", self.recent_files)
        self.mw.list_widget_recent_files.clear()
        self.mw.list_widget_recent_files.addItems(self.recent_files)

    def _on_file_opened(self, file_path: str) -> None:
        self.mw.line_edit_active_file.setText(file_path)

        self.mw.action_close_file.setEnabled(True)
        self.mw.action_edit_metadata.setEnabled(True)
        self.mw.btn_close_file.setEnabled(True)
        self.mw.btn_load_data.setEnabled(True)

        self.data.open_file(file_path)
        self.mw.table_view_import_data.setModel(self.data.data_model)
        self._set_column_models()
        self.update_recent_files(file_path)

    def _open_recent_file(self, item: QtWidgets.QListWidgetItem) -> None:
        file_path = item.text()
        self.close_file()
        self._on_file_opened(file_path)

    @QtCore.Slot()
    def read_data(self) -> None:
        if self.data.has_data:
            loaded_file = self.mw.line_edit_active_file.text()
            self.close_file()
            self._on_file_opened(loaded_file)

        self.data.load_data()
        for col in range(self.data.base_df.width):
            self.mw.table_view_import_data.horizontalHeader().setSectionResizeMode(
                col, QtWidgets.QHeaderView.ResizeMode.Stretch
            )

    @QtCore.Slot()
    def close_file(self) -> None:
        self.mw.table_view_import_data.setModel(None)
        self.mw.data_tree_widget_import_metadata.clear()
        self._clear_column_models()
        self.mw.dock_sections.list_view.setModel(None)

        with contextlib.suppress(Exception):
            self._disconnect_data_controller_signals()
            self.data.setParent(None)

        self.data = DataController(self)
        self._connect_data_controller_signals()

        self.plot.reset()

        self.mw.action_close_file.setEnabled(False)
        self.mw.action_edit_metadata.setEnabled(False)
        self.mw.btn_close_file.setEnabled(False)
        self.mw.btn_load_data.setEnabled(False)

        self.mw.label_showing_data_table.setText("Showing: -")
        self.mw.set_active_section_label("-")
        self.mw.line_edit_active_file.clear()

    # @QtCore.Slot(str, object)
    # def _update_setting(self, name: str, value: QtGui.QColor | str | int | float | None) -> None:
    #     if value is None:
    #         return
    #     logger.info(f"Setting changed: {name} -> {value}")
    #     if name == "background_color":
    #         self.plot.set_background_color(value)
    #     elif name == "foreground_color":
    #         self.plot.set_foreground_color(value)
    #     elif name == "point_color":
    #         if self.plot.peak_scatter is not None:
    #             self.plot.peak_scatter.setBrush(value)
    #     elif name == "signal_line_color":
    #         if self.plot.signal_curve is not None:
    #             self.plot.signal_curve.setPen(value)
    #     elif name == "rate_line_color":
    #         if self.plot.rate_curve is not None:
    #             self.plot.rate_curve.setPen(value)
    #     elif name == "section_marker_color":
    #         for r in self.plot.regions:
    #             r.setBrush(color=value)
    #     elif name == "float_visual_precision":
    #         if isinstance(value, int):
    #             self.data.data_model.set_float_precision(value)
    #     elif name == "click_width_signal_line":
    #         if isinstance(value, int) and self.plot.signal_curve is not None:
    #             self.plot.signal_curve.setCurveClickable(True, width=value)
    #     elif name == "search_around_click_radius":
    #         if isinstance(value, int):
    #             self.plot.search_around_click_radius = value
    #     # elif name == "rate_computation_method":
    #     #     if isinstance(value, RateComputationMethod):
    #     #         self.

    @QtCore.Slot()
    def apply_settings(self) -> None:
        self.plot.apply_settings()

    @QtCore.Slot(dict)
    def export_result(self, info_dict: _t.ExportInfoDict) -> None:
        path = info_dict["out_path"]

        result = self.data.get_complete_result(
            measured_date=info_dict["measured_date"],
            subject_id=info_dict["subject_id"],
            oxygen_condition=info_dict["oxygen_condition"],
        )
        try:
            write_hdf5(path, result)
        except Exception as e:
            logger.error(f"Error writing HDF5 file: {e}")
            return
        else:
            logger.success(f"Result exported to {path}.")
