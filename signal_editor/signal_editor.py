import contextlib
import enum
import typing as t
from pathlib import Path

import numpy as np
import superqt
from loguru import logger
from PySide6 import QtCore, QtGui, QtWidgets

from .app import type_defs as _t
from .app.controllers.data_controller import DataController
from .app.controllers.plot_controller import PlotController
from .app.core.peak_detection import find_extrema
from .app.enum_defs import PeakDetectionMethod, PreprocessPipeline, StandardizationMethod
from .app.gui.main_window import MainWindow
from .app.utils import safe_disconnect, safe_multi_disconnect

if t.TYPE_CHECKING:
    from .app.models.metadata import QFileMetadata


class SignalEditor(QtWidgets.QApplication):
    def __init__(self, args: list[str]) -> None:
        super().__init__(args)
        self.setOrganizationName("AWI")
        self.setApplicationName("Signal Editor")
        self.mw = MainWindow()
        self.data_c = DataController(self)
        self.plot_c = PlotController(self, self.mw)

        self.connect_qt_signals()

    def connect_qt_signals(self) -> None:
        self.mw.settings_editor.sig_setting_changed.connect(self._update_setting)
        self.mw.action_open_file.triggered.connect(self.open_file)
        self.mw.action_edit_metadata.triggered.connect(lambda: self.show_metadata_dialog([]))
        self.mw.settings_editor.finished.connect(self.apply_settings)
        self.mw.btn_load_data.clicked.connect(self.read_data)
        self.mw.dialog_meta.sig_property_has_changed.connect(self.update_metadata)
        self.mw.btn_open_file.clicked.connect(self.open_file)
        self.mw.action_close_file.triggered.connect(self.close_file)
        self.mw.btn_close_file.clicked.connect(self.close_file)

        self.mw.spin_box_sampling_rate_import_page.editingFinished.connect(
            self.update_sampling_rate
        )
        self.mw.combo_box_info_column_import_page.currentTextChanged.connect(
            self.update_info_column
        )
        self.mw.combo_box_signal_column_import_page.currentTextChanged.connect(
            self.update_signal_column
        )

        # Section actions
        self.mw.action_create_new_section.toggled.connect(self.maybe_new_section)
        self.mw.action_confirm_section.triggered.connect(self.create_new_section)
        self.mw.action_cancel_section.triggered.connect(self.cancel_new_section)
        self.mw.action_show_section_overview.toggled.connect(self.plot_c.toggle_regions)

        self.mw.action_toggle_auto_scaling.toggled.connect(self.plot_c.toggle_auto_scaling)
        self.mw.action_show_processing_inputs.toggled.connect(self.mw.dock_processing.setVisible)
        self.mw.action_show_peak_detection_inputs.toggled.connect(self.mw.dock_peaks.setVisible)

        self.mw.dock_sections.list_view.sig_delete_current_item.connect(self.delete_section)
        self.mw.dock_processing.sig_filter_requested.connect(self.filter_active_signal)
        self.mw.dock_processing.sig_pipeline_requested.connect(self.run_preprocess_pipeline)
        self.mw.dock_processing.sig_standardization_requested.connect(
            self.standardize_active_signal
        )
        self.mw.dock_processing.sig_data_reset_requested.connect(self.restore_original_signal)

        self.mw.dock_peaks.sig_peak_detection_requested.connect(self.run_peak_detection)

        self.mw.action_find_peaks_in_selection.triggered.connect(self.find_peaks_in_selection)
        self.mw.action_remove_peaks_in_selection.triggered.connect(
            self.plot_c.remove_peaks_in_selection
        )

    @QtCore.Slot()
    def find_peaks_in_selection(self) -> None:
        rect = self.plot_c.get_selection_area()
        if rect is None:
            return
        active_section = self.data_c.active_section
        left, right, top, bottom = int(rect.left()), int(rect.right()), rect.top(), rect.bottom()
        self.plot_c.remove_selection_rect()
        # TODO: Replace with values from widgets
        win_size = 50
        edge_buffer = 10
        peak_type = "auto"
        b_left, b_right = left + edge_buffer, right - edge_buffer
        b_left = np.maximum(b_left, 0)
        b_right = np.minimum(b_right, active_section.processed_signal.len())
        data = active_section.processed_signal[b_left:b_right].to_numpy()
        if peak_type != "auto":
            raise NotImplementedError
        data_mean = np.mean(data)
        peaks = (
            find_extrema(data, search_radius=win_size, direction="up")
            if abs(top - data_mean) < abs(bottom - data_mean)
            else find_extrema(data, search_radius=win_size, direction="down")
        )
        peaks = peaks + b_left
        active_section.update_peaks("add", peaks)
        self.plot_c.set_peak_data(*active_section.get_peak_xy())
        self.plot_c.set_rate_data(active_section.rate_instantaneous_interpolated)

    @QtCore.Slot(dict)
    def filter_active_signal(self, filter_params: _t.SignalFilterParameters) -> None:
        self.data_c.active_section.filter_signal(
            pipeline=PreprocessPipeline.Custom, **filter_params
        )
        self.refresh_plot_data()

    @QtCore.Slot()
    def restore_original_signal(self) -> None:
        self.data_c.active_section.reset_signal()
        self.refresh_plot_data()

    @QtCore.Slot(object)
    def run_preprocess_pipeline(self, pipeline: PreprocessPipeline) -> None:
        if pipeline not in {PreprocessPipeline.PPGElgendi, PreprocessPipeline.ECGNeuroKit2}:
            return
        self.data_c.active_section.filter_signal(pipeline)
        self.refresh_plot_data()

    @QtCore.Slot(dict)
    def standardize_active_signal(
        self, standardization_params: _t.StandardizationParameters
    ) -> None:
        method = standardization_params.pop("method")
        window_size = standardization_params.pop("window_size")
        robust = method == StandardizationMethod.ZScoreRobust
        self.data_c.active_section.scale_signal(
            method=method, robust=robust, window_size=window_size
        )
        self.refresh_plot_data()

    def refresh_plot_data(self) -> None:
        self.plot_c.set_signal_data(self.data_c.active_section.processed_signal.to_numpy())

    @QtCore.Slot(enum.StrEnum, dict)
    def run_peak_detection(
        self, method: PeakDetectionMethod, params: _t.PeakDetectionMethodParameters
    ) -> None:
        self.data_c.active_section.detect_peaks(method, params)
        self.plot_c.set_peak_data(*self.data_c.active_section.get_peak_xy())
        self.plot_c.set_rate_data(self.data_c.active_section.rate_instantaneous_interpolated)

    @QtCore.Slot()
    def _on_sig_new_data(self) -> None:
        self.mw.dock_sections.list_view.setModel(self.data_c.sections)
        self.mw.dock_sections.list_view.setCurrentIndex(self.data_c.base_section_index)
        self.update_sampling_rate()

    def _connect_data_controller_signals(self) -> None:
        self.data_c.sig_user_input_required.connect(self.show_metadata_dialog)
        self.data_c.sig_new_metadata.connect(self.update_metadata_widgets)
        self.data_c.sig_new_data.connect(self._on_sig_new_data)
        self.mw.dock_sections.list_view.pressed.connect(self.data_c.set_active_section)
        self.data_c.sig_active_section_changed.connect(self._on_active_section_changed)

    def _disconnect_data_controller_signals(self) -> None:
        sender = self.data_c
        signal_slot_pairs = [
            (sender.sig_user_input_required, self.show_metadata_dialog),
            (sender.sig_new_metadata, self.update_metadata_widgets),
            (sender.sig_new_data, self._on_sig_new_data),
            (sender.sig_active_section_changed, self._on_active_section_changed),
        ]
        safe_multi_disconnect(sender, signal_slot_pairs)
        safe_disconnect(
            self.mw.dock_sections.list_view,
            self.mw.dock_sections.list_view.pressed,
            self.data_c.set_active_section,
        )

    @QtCore.Slot(bool)
    def maybe_new_section(self, checked: bool) -> None:
        self.mw.toggle_section_actions(checked)
        if not checked:
            self.plot_c.hide_region_selector()
            return
        bounds = (0, self.data_c.base_df.height - 1)
        self.plot_c.show_region_selector(bounds)

    @QtCore.Slot()
    def create_new_section(self) -> None:
        if self.plot_c.region_selector is None:
            return
        if not self.plot_c.region_selector.isVisible():
            return
        start, stop = self.plot_c.region_selector.getRegion()
        self.data_c.create_section(start, stop)
        self.plot_c.hide_region_selector()
        self.mw.toggle_section_actions(False)
        self.mw.action_create_new_section.setChecked(False)
        self.plot_c.mark_region(start, stop)

    @QtCore.Slot()
    def cancel_new_section(self) -> None:
        self.plot_c.hide_region_selector()
        self.mw.toggle_section_actions(False)
        self.mw.action_create_new_section.setChecked(False)

    @QtCore.Slot(QtCore.QModelIndex)
    def delete_section(self, index: QtCore.QModelIndex) -> None:
        s = self.data_c.sections.get_section(index)
        if s is not None:
            bounds = s.global_bounds
            self.plot_c.remove_region(bounds=bounds)
        self.data_c.delete_section(index)
        logger.success(f"Deleted section {index.row():03}")

    @QtCore.Slot(bool)
    def _on_active_section_changed(self, has_peaks: bool) -> None:
        section = self.data_c.active_section
        is_base_section = section is self.data_c.get_base_section()
        self.mw.action_create_new_section.setEnabled(is_base_section)
        self.plot_c.set_signal_data(section.processed_signal.to_numpy())
        self.plot_c.clear_peaks()
        self.plot_c.clear_rate()
        if has_peaks:
            self.plot_c.set_peak_data(*section.get_peak_xy())
            self.plot_c.set_rate_data(section.rate_instantaneous_interpolated)

    @QtCore.Slot(dict)
    def update_metadata(self, metadata_dict: _t.MetadataUpdateDict) -> None:
        sampling_rate = metadata_dict.get("sampling_rate", None)
        info_col = metadata_dict.get("info_column", None)
        signal_col = metadata_dict.get("signal_column", None)
        self.data_c.update_metadata(sampling_rate, signal_col, info_col)

    @QtCore.Slot(object)
    def update_metadata_widgets(self, metadata: "QFileMetadata") -> None:
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
            metadata = self.data_c.metadata
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
        self.data_c.update_metadata(sampling_rate=sampling_rate)
        self.plot_c.update_time_axis_scale(sampling_rate)
        self.mw.dock_processing.update_frequency_sliders(sampling_rate)
        logger.info(f"Sampling rate set to {sampling_rate} Hz.")

    @QtCore.Slot(str)
    def update_signal_column(self, signal_column: str) -> None:
        self.data_c.update_metadata(signal_col=signal_column)
        logger.info(f"Signal column set to '{signal_column}'.")

    @QtCore.Slot(str)
    def update_info_column(self, info_column: str) -> None:
        self.data_c.update_metadata(info_col=info_column)
        logger.info(f"Info column set to '{info_column}'.")

    def _set_column_models(self) -> None:
        self.mw.combo_box_info_column_import_page.setModel(self.data_c.metadata.columns)
        self.mw.combo_box_signal_column_import_page.setModel(self.data_c.metadata.columns)
        self.mw.dialog_meta.combo_box_signal_column.setModel(self.data_c.metadata.columns)
        self.mw.dialog_meta.combo_box_info_column.setModel(self.data_c.metadata.columns)

        with contextlib.suppress(Exception):
            self.mw.combo_box_info_column_import_page.setCurrentText(
                self.data_c.metadata.info_column
            )
            self.mw.combo_box_signal_column_import_page.setCurrentText(
                self.data_c.metadata.signal_column
            )

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
        settings = QtCore.QSettings()
        default_data_dir = str(settings.value("Misc/data_folder", self.applicationDirPath()))
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self.mw,
            "Open File",
            default_data_dir,
            filter="Supported Files (*.csv *.txt *.tsv *.xlsx *.feather *.edf)",
        )
        if not file_path:
            return

        self.close_file()

        settings.setValue("Misc/data_folder", Path(file_path).parent.resolve().as_posix())

        self.mw.action_close_file.setEnabled(True)
        self.mw.action_edit_metadata.setEnabled(True)
        self.mw.btn_close_file.setEnabled(True)
        self.mw.btn_load_data.setEnabled(True)

        # with contextlib.suppress(Exception):
        #     self._disconnect_data_controller_signals()
        #     self.data_controller.setParent(None)

        # self.data_controller = DataController(self)
        # self._connect_data_controller_signals()

        # self.plot_controller.reset()

        self.data_c.open_file(file_path)
        self.mw.table_view_import_data.setModel(self.data_c.data_model)
        self._set_column_models()

    @QtCore.Slot()
    def read_data(self) -> None:
        self.data_c.load_data()
        for col in range(self.data_c.base_df.width):
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
            self.data_c.setParent(None)

        self.data_c = DataController(self)
        self._connect_data_controller_signals()

        self.plot_c.reset()

        self.mw.action_close_file.setEnabled(False)
        self.mw.action_edit_metadata.setEnabled(False)
        self.mw.btn_close_file.setEnabled(False)
        self.mw.btn_load_data.setEnabled(False)

    @QtCore.Slot(str, object)
    def _update_setting(self, name: str, value: QtGui.QColor | str | int | float | None) -> None:
        if value is None:
            return
        match name:
            case "background_color":
                self.plot_c.set_background_color(value)
            case "foreground_color":
                self.plot_c.set_foreground_color(value)
            case "point_color":
                if self.plot_c.peak_scatter is not None:
                    self.plot_c.peak_scatter.setBrush(value)
            case "signal_line_color":
                if self.plot_c.signal_curve is not None:
                    self.plot_c.signal_curve.setPen(value)
            case "rate_line_color":
                if self.plot_c.rate_curve is not None:
                    self.plot_c.rate_curve.setPen(value)
            case "section_marker_color":
                for r in self.plot_c.regions:
                    r.setBrush(color=value)
            case "float_visual_precision":
                if isinstance(value, int):
                    self.data_c.data_model.set_float_precision(value)
            case _:
                pass

    @QtCore.Slot()
    def apply_settings(self) -> None:
        self.plot_c.apply_settings()
