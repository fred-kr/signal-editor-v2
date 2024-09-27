import contextlib
import enum
import typing as t
from pathlib import Path

import numpy as np
import numpy.typing as npt
import xlsxwriter
from loguru import logger
from PySide6 import QtCore, QtWidgets

from .app import type_defs as _t
from .app.config import Config
from .app.constants import SECTION_INDEX_COL
from .app.controllers.data_controller import DataController
from .app.controllers.plot_controller import PlotController
from .app.logic.file_io import write_hdf5
from .app.logic.peak_detection import find_peaks
from .app.enum_defs import (
    PeakDetectionMethod,
    PreprocessPipeline,
    RateComputationMethod,
    StandardizationMethod,
)
from .app.gui.main_window import MainWindow
from .app.models.file_list_model import FileListModel
from .app.utils import safe_multi_disconnect

if t.TYPE_CHECKING:
    from .app.logic.section import Section
    from .app.logic.metadata import FileMetadata


class _WorkerSignals(QtCore.QObject):
    sig_success: t.ClassVar[QtCore.Signal] = QtCore.Signal()
    sig_failed: t.ClassVar[QtCore.Signal] = QtCore.Signal(Exception)
    sig_done: t.ClassVar[QtCore.Signal] = QtCore.Signal()


class PeakDetectionWorker(QtCore.QRunnable):
    def __init__(
        self,
        section: "Section",
        method: PeakDetectionMethod,
        params: _t.PeakDetectionMethodParameters,
        *,
        rr_params: _t.RollingRateKwargsDict | None = None,
    ) -> None:
        super().__init__()
        self.section = section
        self.method = method
        self.params = params
        self.rr_params = rr_params
        self.signals = _WorkerSignals()

    @QtCore.Slot()
    def run(self) -> None:
        try:
            self.section.detect_peaks(self.method, self.params, rr_params=self.rr_params)
        except Exception as e:
            self.signals.sig_failed.emit(e)
        else:
            self.signals.sig_success.emit()
        finally:
            self.signals.sig_done.emit()


class SectionResultWorker(QtCore.QRunnable):
    def __init__(self, section: "Section", *, rr_params: _t.RollingRateKwargsDict | None = None) -> None:
        super().__init__()
        self.section = section
        self.rr_params = rr_params
        self.signals = _WorkerSignals()

    @QtCore.Slot()
    def run(self) -> None:
        try:
            self.section.lock_result(rr_params=self.rr_params)
        except Exception as e:
            self.signals.sig_failed.emit(e)
        else:
            self.signals.sig_success.emit()
        finally:
            self.signals.sig_done.emit()


class SignalEditor(QtWidgets.QApplication):
    sig_peaks_updated: t.ClassVar[QtCore.Signal] = QtCore.Signal()

    def __init__(self, args: list[str]) -> None:
        super().__init__(args)
        self.setOrganizationName("AWI")
        self.setApplicationName("Signal Editor")
        self.mw = MainWindow()
        self.data = DataController(self)
        self.plot = PlotController(self, self.mw)

        self.thread_pool = QtCore.QThreadPool.globalInstance()

        self.recent_files_model = FileListModel(Config().internal.recent_files, max_files=10, parent=self)
        self.recent_files_model.validate_files()

        self.mw.list_view_recent_files.setModel(self.recent_files_model)

        self._connect_signals()

    def _connect_signals(self) -> None:
        self.sig_peaks_updated.connect(self.refresh_peak_data)

        self.mw.action_show_settings.triggered.connect(self._on_action_show_settings)
        self.mw.action_open_file.triggered.connect(self.open_file)
        self.mw.action_edit_metadata.triggered.connect(lambda: self.show_metadata_dialog([]))
        self.mw.action_about_qt.triggered.connect(self.aboutQt)
        self.mw.action_close_file.triggered.connect(self.close_file)

        self.mw.dialog_meta.sig_property_has_changed.connect(self.update_metadata)

        self.mw.btn_load_data.clicked.connect(self.read_data)
        self.mw.btn_open_file.clicked.connect(self.open_file)
        self.mw.btn_close_file.clicked.connect(self.close_file)

        self.mw.combo_box_signal_column_import_page.currentTextChanged.connect(self.update_signal_column)
        self.mw.combo_box_info_column_import_page.currentTextChanged.connect(self.update_info_column)

        self.mw.spin_box_sampling_rate_import_page.editingFinished.connect(self.update_sampling_rate)

        self.mw.list_view_recent_files.doubleClicked.connect(self._open_recent_file)

        self.mw.sig_table_refresh_requested.connect(self.refresh_data_view)
        self.mw.sig_export_requested.connect(self.export_result)

        # Section actions
        self.mw.action_create_new_section.toggled.connect(self.maybe_new_section)
        self.mw.action_confirm_section.triggered.connect(self._on_confirm_new_section)
        self.mw.action_cancel_section.triggered.connect(self._on_cancel_new_section)
        self.mw.action_show_section_overview.toggled.connect(self.plot.toggle_regions)

        self.mw.action_toggle_auto_scaling.toggled.connect(self.plot.toggle_auto_scaling)

        self.mw.dock_sections.list_view.sig_delete_current_item.connect(self.delete_section)
        self.mw.dock_sections.list_view.sig_show_summary.connect(self.show_section_summary)
        self.mw.action_mark_section_done.triggered.connect(self._lock_section)
        self.mw.action_unlock_section.triggered.connect(self._unlock_section)

        self.mw.dock_parameters.sig_filter_requested.connect(self.filter_active_signal)
        self.mw.dock_parameters.sig_pipeline_requested.connect(self.run_preprocess_pipeline)
        self.mw.dock_parameters.sig_standardization_requested.connect(self.standardize_active_signal)
        self.mw.dock_parameters.sig_data_reset_requested.connect(self.restore_original_signal)
        self.mw.dock_parameters.sig_peak_detection_requested.connect(self.run_peak_detection_worker)
        self.mw.dock_parameters.sig_clear_peaks_requested.connect(self.clear_peaks)

        self.mw.action_find_peaks_in_selection.triggered.connect(self.find_peaks_in_selection)
        self.mw.action_remove_peaks_in_selection.triggered.connect(self.plot.remove_peaks_in_selection)

        self.plot.sig_scatter_data_changed.connect(self.handle_peak_edit)
        self.plot.sig_section_clicked.connect(self.set_active_section_from_int)

    @QtCore.Slot()
    def _on_action_show_settings(self) -> None:
        snapshot = Config().get_snapshot()

        settings_dlg = Config().create_editor_widgets(self.mw)
        settings_dlg.accepted.connect(self.apply_settings)
        settings_dlg.rejected.connect(lambda: Config().restore_snapshot(snapshot))
        settings_dlg.open()

    @QtCore.Slot()
    def clear_peaks(self) -> None:
        self.plot.clear_peaks()
        self.data.active_section.reset_peaks()

    @QtCore.Slot()
    def find_peaks_in_selection(self) -> None:
        rect = self.plot.get_selection_area()
        if rect is None or self.plot.block_clicks:
            self.plot.remove_selection_rect()
            return

        active_section = self.data.active_section
        left, right = int(rect.left()), int(rect.right())
        self.plot.remove_selection_rect()

        peak_method = PeakDetectionMethod(self.mw.dock_parameters.ui.combo_peak_method.currentData())
        param_dock = self.mw.dock_parameters
        peak_params = param_dock.get_peak_detection_params(peak_method)
        rolling_rate_params = param_dock.get_rate_calculation_params()

        edge_buffer = 10
        b_left = max(left + edge_buffer, 0)
        b_right = min(right - edge_buffer, active_section.processed_signal.len())
        b_length = b_right - b_left
        data = active_section.processed_signal.slice(b_left, b_length).to_numpy(allow_copy=False)
        peaks = find_peaks(
            data,
            sampling_rate=active_section.sampling_rate,
            method=peak_method,
            method_parameters=peak_params,
        )
        peaks = peaks + b_left
        active_section.update_peaks("add", peaks, rr_params=rolling_rate_params)
        self.sig_peaks_updated.emit()

    @QtCore.Slot(str, object)
    def handle_peak_edit(self, action: _t.UpdatePeaksAction, indices: npt.NDArray[np.int32]) -> None:
        rolling_rate_kwargs = self.mw.dock_parameters.get_rate_calculation_params()
        self.data.active_section.update_peaks(action, indices, rr_params=rolling_rate_kwargs)
        self.sig_peaks_updated.emit()

    @QtCore.Slot()
    def refresh_peak_data(self) -> None:
        cas = self.data.active_section
        pos = cas.get_peak_pos()
        self.plot.set_peak_data(pos.get_column(SECTION_INDEX_COL), pos.get_column(cas.processed_signal_name))
        if Config().editing.rate_computation_method == RateComputationMethod.RollingWindow:
            rolling_rate_kwargs = self.mw.dock_parameters.get_rate_calculation_params()
            cas.update_rate_data(rr_params=rolling_rate_kwargs)
        else:
            cas.update_rate_data()
        rate_data = cas.rate_data.select(SECTION_INDEX_COL, "rate_bpm")
        self.plot.set_rate_data(x_data=rate_data.get_column(SECTION_INDEX_COL), y_data=rate_data.get_column("rate_bpm"))

    def update_status_indicators(self) -> None:
        self.mw.dock_parameters.set_filter_status(
            self.data.active_section.is_filtered, self.data.active_section.n_filters
        )
        self.mw.dock_parameters.set_pipeline_status(self.data.active_section.is_processed)
        self.mw.dock_parameters.set_standardization_status(self.data.active_section.is_standardized)

    @QtCore.Slot(dict)
    def filter_active_signal(self, filter_params: _t.SignalFilterParameters) -> None:
        self.data.active_section.filter_signal(pipeline=None, **filter_params)
        self.refresh_plot_data()

    @QtCore.Slot()
    def restore_original_signal(self) -> None:
        self.data.active_section.reset_signal()
        self.refresh_plot_data()
        self.plot.clear_peaks()

    @QtCore.Slot(object)
    def run_preprocess_pipeline(self, pipeline: PreprocessPipeline) -> None:
        if pipeline not in PreprocessPipeline:
            return
        self.data.active_section.filter_signal(pipeline)
        self.refresh_plot_data()

    @QtCore.Slot(dict)
    def standardize_active_signal(self, standardization_params: _t.StandardizationParameters) -> None:
        method = standardization_params.pop("method")
        window_size = standardization_params.pop("window_size")
        robust = method == StandardizationMethod.ZScoreRobust
        self.data.active_section.standardize_signal(method=method, robust=robust, window_size=window_size)
        self.refresh_plot_data()

    def refresh_plot_data(self) -> None:
        self.plot.set_signal_data(self.data.active_section.processed_signal)
        self.update_status_indicators()

    @QtCore.Slot(enum.StrEnum, dict)
    def run_peak_detection_worker(self, method: PeakDetectionMethod, params: _t.PeakDetectionMethodParameters) -> None:
        rolling_rate_kwargs = self.mw.dock_parameters.get_rate_calculation_params()
        worker = PeakDetectionWorker(self.data.active_section, method, params, rr_params=rolling_rate_kwargs)
        worker.signals.sig_success.connect(self.refresh_peak_data)
        worker.signals.sig_done.connect(self._on_worker_finished)
        # worker.signals.sig_failed.connect(self.mw.sb_progress.error)
        self._on_worker_started("Detecting peaks...")
        self.thread_pool.start(worker)

    def _on_worker_started(self, overlay_text: str = "Calculating...") -> None:
        self.mw.overlay_widget.show_overlay(overlay_text)

    @QtCore.Slot()
    def _on_worker_finished(self) -> None:
        self.mw.overlay_widget.hide_overlay()
        is_locked = self.data.active_section.is_locked
        self.mw.dock_parameters.setEnabled(not is_locked)
        self.mw.action_remove_section.setEnabled(not is_locked)
        self.mw.action_mark_section_done.setEnabled(not is_locked)
        self.mw.action_unlock_section.setEnabled(is_locked)
        self.plot.block_clicks = is_locked

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
        self.plot.remove_region(index)
        self.data.delete_section(index)
        self.mw.dock_sections.list_view.setCurrentIndex(self.data.base_section_index)
        logger.info(f"Deleted section {index.row():03}")

    @QtCore.Slot(QtCore.QModelIndex)
    def show_section_summary(self, index: QtCore.QModelIndex) -> None:
        s = self.data.sections.get_section(index)
        if s is None:
            return
        summary = s.get_summary()
        self.mw.show_section_summary_box(summary)

    @QtCore.Slot(bool)
    def _on_active_section_changed(self, has_peaks: bool) -> None:
        section = self.data.active_section
        is_base_section = section is self.data.get_base_section()
        is_locked = section.is_locked
        is_locked_or_base = is_locked or is_base_section

        self.mw.action_create_new_section.setEnabled(is_base_section)
        self.mw.action_remove_section.setEnabled(not is_base_section and not is_locked)
        self.mw.action_mark_section_done.setEnabled(not is_base_section and not is_locked)
        self.mw.action_unlock_section.setEnabled(not is_base_section and is_locked)
        self.mw.action_show_section_overview.setEnabled(is_base_section)
        self.mw.action_show_section_overview.setChecked(is_base_section)
        self.mw.dock_parameters.setEnabled(not is_base_section and not is_locked)

        self.mw.set_active_section_label(section.section_id.pretty_name())

        self.plot.block_clicks = is_locked_or_base
        self.plot.set_signal_data(section.processed_signal)
        self.plot.clear_peaks()

        if has_peaks:
            self.sig_peaks_updated.emit()

        # Update the table view to show the current sections' data
        self.mw.table_view_import_data.setModel(self.data.active_section_model)
        if is_locked_or_base:
            self.update_result_views()

    @QtCore.Slot(int)
    def set_active_section_from_int(self, index: int) -> None:
        self.data.set_active_section(self.data.sections.index(index))
        self.mw.dock_sections.list_view.setCurrentIndex(self.data.sections.index(index))

    @QtCore.Slot()
    def refresh_data_view(self) -> None:
        # TODO: Make this generic so any table view can be connected to this slot
        self.data.active_section_model.set_df(self.data.active_section.data)

    @QtCore.Slot(dict)
    def update_metadata(self, metadata_dict: _t.MetadataDict) -> None:
        sampling_rate = metadata_dict.get("sampling_rate", None)
        info_col = metadata_dict.get("info_column", None)
        signal_col = metadata_dict.get("signal_column", None)
        self.data.update_metadata(sampling_rate, signal_col, info_col)

    @QtCore.Slot(object)
    def update_metadata_widgets(self, metadata: "FileMetadata") -> None:
        self.mw.data_tree_widget_additional_metadata.set_data(metadata.other_info, hide_root=True)
        self.mw.data_tree_widget_additional_metadata.collapseAll()
        self.mw.spin_box_sampling_rate_import_page.setValue(metadata.sampling_rate)
        self.mw.combo_box_signal_column_import_page.setCurrentText(metadata.signal_column)
        self.mw.combo_box_info_column_import_page.setCurrentText(metadata.info_column)

    @QtCore.Slot(set)
    def show_metadata_dialog(self, required_fields: set[str]) -> None:
        metadata = self.data.metadata

        file_name = metadata.file_name
        file_type = metadata.file_format
        info_col = metadata.info_column

        if "sampling_rate" not in required_fields:
            sampling_rate = metadata.sampling_rate
            self.mw.dialog_meta.spin_box_sampling_rate.setValue(sampling_rate)
            self.mw.spin_box_sampling_rate_import_page.setValue(sampling_rate)
            self.mw.dialog_meta.spin_box_sampling_rate.setProperty("requiresInput", False)
        else:
            self.mw.dialog_meta.spin_box_sampling_rate.setProperty("requiresInput", True)

        self.mw.dialog_meta.spin_box_sampling_rate.style().unpolish(self.mw.dialog_meta.spin_box_sampling_rate)
        self.mw.dialog_meta.spin_box_sampling_rate.style().polish(self.mw.dialog_meta.spin_box_sampling_rate)
        self.mw.dialog_meta.spin_box_sampling_rate.update()

        if "signal_column" not in required_fields:
            signal_col = metadata.signal_column
            self.mw.dialog_meta.combo_box_signal_column.setCurrentText(signal_col)
            self.mw.combo_box_signal_column_import_page.setCurrentText(signal_col)
            self.mw.dialog_meta.combo_box_signal_column.setProperty("requiresInput", False)
        else:
            self.mw.dialog_meta.combo_box_signal_column.setProperty("requiresInput", True)

        self.mw.dialog_meta.combo_box_signal_column.style().unpolish(self.mw.dialog_meta.combo_box_signal_column)
        self.mw.dialog_meta.combo_box_signal_column.style().polish(self.mw.dialog_meta.combo_box_signal_column)
        self.mw.dialog_meta.combo_box_signal_column.update()

        self.mw.dialog_meta.combo_box_info_column.setCurrentText(info_col)
        self.mw.combo_box_info_column_import_page.setCurrentText(info_col)

        self.mw.dialog_meta.line_edit_file_name.setText(file_name)
        self.mw.dialog_meta.line_edit_file_type.setText(file_type)

        self.mw.data_tree_widget_additional_metadata.set_data(metadata.other_info, hide_root=True)

        self.mw.dialog_meta.open()

    @QtCore.Slot()
    def update_sampling_rate(self) -> None:
        sampling_rate = self.mw.spin_box_sampling_rate_import_page.value()
        self.data.update_metadata(sampling_rate=sampling_rate)
        self.plot.update_time_axis_scale(sampling_rate)
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
        with QtCore.QSignalBlocker(self.mw.combo_box_signal_column_import_page):
            self.mw.combo_box_signal_column_import_page.addItems(self.data.metadata.valid_columns)
            self.mw.combo_box_signal_column_import_page.setCurrentText(self.data.metadata.signal_column)
        with QtCore.QSignalBlocker(self.mw.combo_box_info_column_import_page):
            self.mw.combo_box_info_column_import_page.addItems(self.data.metadata.column_names)
            self.mw.combo_box_info_column_import_page.setCurrentText(self.data.metadata.info_column)
        with QtCore.QSignalBlocker(self.mw.dialog_meta.combo_box_signal_column):
            self.mw.dialog_meta.combo_box_signal_column.addItems(self.data.metadata.valid_columns)
            self.mw.dialog_meta.combo_box_signal_column.setCurrentText(self.data.metadata.signal_column)
        with QtCore.QSignalBlocker(self.mw.dialog_meta.combo_box_info_column):
            self.mw.dialog_meta.combo_box_info_column.addItems(self.data.metadata.column_names)
            self.mw.dialog_meta.combo_box_info_column.setCurrentText(self.data.metadata.info_column)

    def _clear_column_models(self) -> None:
        with QtCore.QSignalBlocker(self.mw.combo_box_info_column_import_page):
            self.mw.combo_box_info_column_import_page.clear()
        with QtCore.QSignalBlocker(self.mw.combo_box_signal_column_import_page):
            self.mw.combo_box_signal_column_import_page.clear()
        with QtCore.QSignalBlocker(self.mw.dialog_meta.combo_box_info_column):
            self.mw.dialog_meta.combo_box_signal_column.clear()
        with QtCore.QSignalBlocker(self.mw.dialog_meta.combo_box_signal_column):
            self.mw.dialog_meta.combo_box_info_column.clear()
        self.mw.data_tree_widget_additional_metadata.clear()

    @QtCore.Slot()
    def open_file(self) -> None:
        default_data_dir = Config().internal.last_input_dir
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self.mw,
            "Open File",
            default_data_dir,
            filter="Supported Files (*.csv *.txt *.tsv *.xlsx *.feather *.edf)",
        )
        if not file_path:
            return

        self.close_file()

        Config().internal.last_input_dir = Path(file_path).parent.resolve().as_posix()
        self._on_file_opened(file_path)

    def _on_file_opened(self, file_path: str) -> None:
        self.mw.line_edit_active_file.setText(Path(file_path).name)

        self.mw.action_close_file.setEnabled(True)
        self.mw.action_edit_metadata.setEnabled(True)
        self.mw.btn_close_file.setEnabled(True)
        self.mw.btn_load_data.setEnabled(True)

        self.data.open_file(file_path)
        self.mw.table_view_import_data.setModel(self.data.data_model)
        self.mw.table_view_result_peaks.setModel(self.data.result_model_peaks)
        self.mw.table_view_result_rate.setModel(self.data.result_model_rate)

        self._set_column_models()
        self.recent_files_model.add_file(file_path)
        self.mw.switch_to(self.mw.stacked_page_import)

        logger.info(f"Opened file: {file_path}")

    @QtCore.Slot(QtCore.QModelIndex)
    def _open_recent_file(self, index: QtCore.QModelIndex) -> None:
        file_path = self.recent_files_model.data(index, QtCore.Qt.ItemDataRole.UserRole)
        self.close_file()
        self._on_file_opened(file_path)

    @QtCore.Slot()
    def read_data(self) -> None:
        if self.data.has_data:
            loaded_file = self.data.metadata.file_path
            self.close_file()
            self._on_file_opened(loaded_file)

        self.data.load_data()
        self.mw.table_view_import_data.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)

        self.mw.dock_sections.setEnabled(True)

        self.mw.spin_box_sampling_rate_import_page.setEnabled(False)
        self.mw.combo_box_signal_column_import_page.setEnabled(False)
        self.mw.combo_box_info_column_import_page.setEnabled(False)
        self.mw.dialog_meta.spin_box_sampling_rate.setEnabled(False)
        self.mw.dialog_meta.combo_box_signal_column.setEnabled(False)
        self.mw.dialog_meta.combo_box_info_column.setEnabled(False)

        Config().internal.last_signal_column = self.data.metadata.signal_column
        Config().internal.last_info_column = self.data.metadata.info_column
        Config().internal.last_sampling_rate = self.data.metadata.sampling_rate

    @QtCore.Slot()
    def close_file(self) -> None:
        self.mw.table_view_import_data.setModel(None)
        self.mw.table_view_result_peaks.setModel(None)
        self.mw.table_view_result_rate.setModel(None)
        self.mw.data_tree_widget_additional_metadata.clear()
        self._clear_column_models()
        self.mw.dock_sections.list_view.setModel(None)
        self.mw.dock_parameters.setEnabled(False)
        self.mw.dock_sections.setEnabled(False)

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

        self.mw.set_active_section_label("-")
        self.mw.line_edit_active_file.clear()

        self.mw.spin_box_sampling_rate_import_page.setEnabled(True)
        self.mw.combo_box_signal_column_import_page.setEnabled(True)
        self.mw.combo_box_info_column_import_page.setEnabled(True)
        self.mw.dialog_meta.spin_box_sampling_rate.setEnabled(True)
        self.mw.dialog_meta.combo_box_signal_column.setEnabled(True)
        self.mw.dialog_meta.combo_box_info_column.setEnabled(True)

    @QtCore.Slot()
    def apply_settings(self) -> None:
        self.plot.apply_settings()

    @QtCore.Slot()
    def update_result_views(self) -> None:
        self.data.result_model_peaks.set_df(self.data.active_section.peak_data)
        self.data.result_model_rate.set_df(self.data.active_section.rate_data)

    @QtCore.Slot()
    def _lock_section(self) -> None:
        rate_params = self.mw.dock_parameters.get_rate_calculation_params()

        worker = SectionResultWorker(self.data.active_section, rr_params=rate_params)
        worker.signals.sig_success.connect(self.update_result_views)
        worker.signals.sig_done.connect(self._on_worker_finished)

        self._on_worker_started("Creating section result...")
        self.thread_pool.start(worker)

    @QtCore.Slot()
    def _unlock_section(self) -> None:
        self.data.active_section.set_locked(False)
        self._on_worker_finished()

    @QtCore.Slot(str)
    def export_result(self, format: str) -> None:
        dir_path = (
            Path(Config().internal.last_output_dir)
            / f"Result_{self.data.active_section.signal_name.title()}_{Path(self.data.metadata.file_path).stem}"
        )
        out_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self.mw,
            f"Export {format.upper()}",
            dir_path.as_posix(),
            filter=f"{format.upper()} files (*.{format})",
        )
        if not out_path:
            return
        Config().internal.last_output_dir = Path(out_path).parent.resolve().as_posix()

        if format == "csv":
            if self.mw.tab_widget_result_views.currentIndex() == 0:
                df = self.data.active_section.peak_data
            elif self.mw.tab_widget_result_views.currentIndex() == 1:
                df = self.data.active_section.rate_data
            else:
                raise NotImplementedError

            df.write_csv(out_path)

        elif format == "hdf5":
            result = self.data.get_complete_result()
            write_hdf5(Path(out_path), result.to_dict())

        elif format == "xlsx":
            df_peaks = self.data.active_section.peak_data
            df_rate = self.data.active_section.rate_data

            with xlsxwriter.Workbook(out_path) as wb:
                df_peaks.write_excel(
                    workbook=wb,
                    worksheet="Detected Peaks",
                )
                df_rate.write_excel(
                    workbook=wb,
                    worksheet="Rate Data",
                )

        else:
            raise NotImplementedError

        self.mw.show_success("Success!", f"Saved to '{out_path}'")
