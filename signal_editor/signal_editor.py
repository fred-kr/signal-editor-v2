import contextlib
import typing as t
from pathlib import Path

import superqt
from loguru import logger
from PySide6 import QtCore, QtGui, QtWidgets

from .app import type_defs as _t
from .app.controllers.data_controller import DataController
from .app.controllers.plot_controller import PlotController
from .app.enum_defs import PreprocessPipeline, StandardizationMethod
from .app.gui.main_window import MainWindow
from .app.utils import safe_disconnect, safe_multi_disconnect

if t.TYPE_CHECKING:
    from .app.models.metadata import QFileMetadata


class SignalEditor(QtWidgets.QApplication):
    def __init__(self, args: list[str]) -> None:
        super().__init__(args)
        self.setOrganizationName("AWI")
        self.setApplicationName("Signal Editor")
        self.main_window = MainWindow()
        self.data_controller = DataController(self)
        self.plot_controller = PlotController(self, self.main_window)

        self.connect_qt_signals()

    def connect_qt_signals(self) -> None:
        self.main_window.settings_editor.sig_setting_changed.connect(self._update_setting)
        self.main_window.action_open_file.triggered.connect(self.open_file)
        self.main_window.action_edit_metadata.triggered.connect(
            lambda: self.show_metadata_dialog([])
        )
        self.main_window.settings_editor.finished.connect(self.apply_settings)
        self.main_window.btn_load_data.clicked.connect(self.read_data)
        self.main_window.metadata_dialog.sig_property_has_changed.connect(self.update_metadata)
        self.main_window.btn_open_file.clicked.connect(self.open_file)
        self.main_window.action_close_file.triggered.connect(self.close_file)
        self.main_window.btn_close_file.clicked.connect(self.close_file)

        self.main_window.spin_box_sampling_rate_import_page.editingFinished.connect(
            self.update_sampling_rate
        )
        self.main_window.combo_box_info_column_import_page.currentTextChanged.connect(
            self.update_info_column
        )
        self.main_window.combo_box_signal_column_import_page.currentTextChanged.connect(
            self.update_signal_column
        )

        self.main_window.action_create_new_section.toggled.connect(self.maybe_new_section)
        self.main_window.action_confirm_section.triggered.connect(self.create_new_section)
        self.main_window.action_cancel_section.triggered.connect(self.cancel_new_section)
        self.main_window.action_toggle_auto_scaling.toggled.connect(
            self.plot_controller.toggle_auto_scaling
        )
        self.main_window.action_show_filter_inputs.triggered.connect(
            self.show_processing_inputs_dock
        )

        self.main_window.dock_section_list.list_view.sig_delete_current_item.connect(
            self.delete_section
        )
        self.main_window.dock_processing_inputs.sig_filter_requested.connect(
            self.filter_active_signal
        )
        self.main_window.dock_processing_inputs.sig_pipeline_requested.connect(
            self.run_preprocess_pipeline
        )
        self.main_window.dock_processing_inputs.sig_standardization_requested.connect(
            self.standardize_active_signal
        )
        self.main_window.dock_processing_inputs.sig_data_reset_requested.connect(
            self.restore_original_signal
        )

    @QtCore.Slot(dict)
    def filter_active_signal(self, filter_params: _t.SignalFilterParameters) -> None:
        self.data_controller.active_section.filter_signal(
            pipeline=PreprocessPipeline.Custom, **filter_params
        )
        self.refresh_plot_data()

    @QtCore.Slot()
    def restore_original_signal(self) -> None:
        self.data_controller.active_section.reset_signal()
        self.refresh_plot_data()

    @QtCore.Slot(object)
    def run_preprocess_pipeline(self, pipeline: PreprocessPipeline) -> None:
        if pipeline not in {PreprocessPipeline.PPGElgendi, PreprocessPipeline.ECGNeuroKit2}:
            return
        self.data_controller.active_section.filter_signal(pipeline)
        self.refresh_plot_data()

    @QtCore.Slot(dict)
    def standardize_active_signal(
        self, standardization_params: _t.StandardizationParameters
    ) -> None:
        method = standardization_params.pop("method")
        window_size = standardization_params.pop("window_size")
        robust = method == StandardizationMethod.ZScoreRobust
        self.data_controller.active_section.scale_signal(
            method=method, robust=robust, window_size=window_size
        )
        self.refresh_plot_data()

    def refresh_plot_data(self) -> None:
        self.plot_controller.set_signal_data(
            self.data_controller.active_section.processed_signal.to_numpy()
        )

    @QtCore.Slot()
    def _on_sig_new_data(self) -> None:
        self.main_window.dock_section_list.list_view.setModel(self.data_controller.sections)
        self.main_window.dock_section_list.list_view.setCurrentIndex(
            self.data_controller.base_section_index
        )
        self.update_sampling_rate()

    def _connect_data_controller_signals(self) -> None:
        self.data_controller.sig_user_input_required.connect(self.show_metadata_dialog)
        self.data_controller.sig_new_metadata.connect(self.update_metadata_widgets)
        self.data_controller.sig_new_data.connect(self._on_sig_new_data)
        self.main_window.dock_section_list.list_view.pressed.connect(
            self.data_controller.set_active_section
        )
        self.data_controller.sig_active_section_changed.connect(self._on_active_section_changed)

    def _disconnect_data_controller_signals(self) -> None:
        sender = self.data_controller
        signal_slot_pairs = [
            (sender.sig_user_input_required, self.show_metadata_dialog),
            (sender.sig_new_metadata, self.update_metadata_widgets),
            (sender.sig_new_data, self._on_sig_new_data),
            (sender.sig_active_section_changed, self._on_active_section_changed),
        ]
        safe_multi_disconnect(sender, signal_slot_pairs)
        safe_disconnect(
            self.main_window.dock_section_list.list_view,
            self.main_window.dock_section_list.list_view.pressed,
            self.data_controller.set_active_section,
        )

    @QtCore.Slot(bool)
    def maybe_new_section(self, checked: bool) -> None:
        self.main_window.toggle_section_actions(checked)
        if not checked:
            self.plot_controller.hide_region_selector()
            return
        bounds = (0, self.data_controller.base_df.height - 1)
        self.plot_controller.show_region_selector(bounds)

    @QtCore.Slot()
    def create_new_section(self) -> None:
        if self.plot_controller.region_selector is None:
            return
        if not self.plot_controller.region_selector.isVisible():
            return
        start, stop = self.plot_controller.region_selector.getRegion()
        self.data_controller.create_section(start, stop)
        self.plot_controller.hide_region_selector()
        self.main_window.toggle_section_actions(False)
        self.main_window.action_create_new_section.setChecked(False)

    @QtCore.Slot()
    def cancel_new_section(self) -> None:
        self.plot_controller.hide_region_selector()
        self.main_window.toggle_section_actions(False)
        self.main_window.action_create_new_section.setChecked(False)

    @QtCore.Slot(QtCore.QModelIndex)
    def delete_section(self, index: QtCore.QModelIndex) -> None:
        self.data_controller.delete_section(index)
        logger.success(f"Deleted section {index.row():03}")

    @QtCore.Slot(bool)
    def _on_active_section_changed(self, has_peaks: bool) -> None:
        section = self.data_controller.active_section
        is_base_section = section is self.data_controller.get_base_section()
        self.main_window.action_create_new_section.setEnabled(is_base_section)
        self.plot_controller.set_signal_data(section.processed_signal.to_numpy())
        if has_peaks:
            self.plot_controller.set_peak_data(*section.get_peak_xy())
            self.plot_controller.set_rate_data(section.rate_instantaneous_interpolated)

    @QtCore.Slot()
    def show_processing_inputs_dock(self) -> None:
        self.main_window.dock_processing_inputs.show()

    @QtCore.Slot(dict)
    def update_metadata(self, metadata_dict: _t.MetadataUpdateDict) -> None:
        sampling_rate = metadata_dict.get("sampling_rate", None)
        info_col = metadata_dict.get("info_column", None)
        signal_col = metadata_dict.get("signal_column", None)
        self.data_controller.update_metadata(sampling_rate, signal_col, info_col)

    @QtCore.Slot(object)
    def update_metadata_widgets(self, metadata: "QFileMetadata") -> None:
        metadata_dict = metadata.to_dict()
        self.main_window.data_tree_widget_import_metadata.setData(metadata_dict, hideRoot=True)
        self.main_window.data_tree_widget_import_metadata.collapseAll()
        self.main_window.spin_box_sampling_rate_import_page.setValue(metadata.sampling_rate)

    @QtCore.Slot(list)
    def show_metadata_dialog(self, required_fields: list[str]) -> None:
        metadata = None
        with superqt.utils.exceptions_as_dialog(
            icon=QtWidgets.QMessageBox.Icon.Warning,
            title="Error loading metadata",
            parent=self.main_window,
        ) as ctx:
            metadata = self.data_controller.metadata
        if ctx.exception is not None or metadata is None:
            return

        file_name = metadata.file_name
        file_type = metadata.file_format
        info_col = metadata.info_column

        self.main_window.metadata_dialog.combo_box_signal_column.setModel(metadata.columns)
        self.main_window.metadata_dialog.combo_box_info_column.setModel(metadata.columns)
        if "sampling_rate" not in required_fields:
            sampling_rate = metadata.sampling_rate
            self.main_window.metadata_dialog.spin_box_sampling_rate.setValue(sampling_rate)
            self.main_window.spin_box_sampling_rate_import_page.setValue(sampling_rate)
        if "signal_column" not in required_fields:
            signal_col = metadata.signal_column
            self.main_window.metadata_dialog.combo_box_signal_column.setCurrentText(signal_col)
            self.main_window.combo_box_signal_column_import_page.setCurrentText(signal_col)

        self.main_window.metadata_dialog.combo_box_info_column.setCurrentText(info_col)
        self.main_window.combo_box_info_column_import_page.setCurrentText(info_col)

        self.main_window.metadata_dialog.line_edit_file_name.setText(file_name)
        self.main_window.metadata_dialog.line_edit_file_type.setText(file_type)

        self.main_window.metadata_dialog.open()

    @QtCore.Slot()
    def update_sampling_rate(self) -> None:
        sampling_rate = self.main_window.spin_box_sampling_rate_import_page.value()
        self.data_controller.update_metadata(sampling_rate=sampling_rate)
        self.plot_controller.update_time_axis_scale(sampling_rate)
        self.main_window.dock_processing_inputs.update_frequency_sliders(sampling_rate)
        logger.info(f"Sampling rate set to {sampling_rate} Hz.")

    @QtCore.Slot(str)
    def update_signal_column(self, signal_column: str) -> None:
        self.data_controller.update_metadata(signal_col=signal_column)
        logger.info(f"Signal column set to '{signal_column}'.")

    @QtCore.Slot(str)
    def update_info_column(self, info_column: str) -> None:
        self.data_controller.update_metadata(info_col=info_column)
        logger.info(f"Info column set to '{info_column}'.")

    def _set_column_models(self) -> None:
        self.main_window.combo_box_info_column_import_page.setModel(
            self.data_controller.metadata.columns
        )
        self.main_window.combo_box_signal_column_import_page.setModel(
            self.data_controller.metadata.columns
        )
        self.main_window.metadata_dialog.combo_box_signal_column.setModel(
            self.data_controller.metadata.columns
        )
        self.main_window.metadata_dialog.combo_box_info_column.setModel(
            self.data_controller.metadata.columns
        )

        with contextlib.suppress(Exception):
            self.main_window.combo_box_info_column_import_page.setCurrentText(
                self.data_controller.metadata.info_column
            )
            self.main_window.combo_box_signal_column_import_page.setCurrentText(
                self.data_controller.metadata.signal_column
            )

    def _clear_column_models(self) -> None:
        with QtCore.QSignalBlocker(self.main_window.combo_box_info_column_import_page):
            self.main_window.combo_box_info_column_import_page.clear()
        with QtCore.QSignalBlocker(self.main_window.combo_box_signal_column_import_page):
            self.main_window.combo_box_signal_column_import_page.clear()
        with QtCore.QSignalBlocker(self.main_window.metadata_dialog.combo_box_info_column):
            self.main_window.metadata_dialog.combo_box_signal_column.clear()
        with QtCore.QSignalBlocker(self.main_window.metadata_dialog.combo_box_signal_column):
            self.main_window.metadata_dialog.combo_box_info_column.clear()
        self.main_window.data_tree_widget_import_metadata.clear()

    @QtCore.Slot()
    def open_file(self) -> None:
        settings = QtCore.QSettings()
        default_data_dir = str(settings.value("Misc/data_folder", self.applicationDirPath()))
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self.main_window,
            "Open File",
            default_data_dir,
            filter="Supported Files (*.csv *.txt *.tsv *.xlsx *.feather *.edf)",
        )
        if not file_path:
            return

        self.close_file()

        settings.setValue("Misc/data_folder", Path(file_path).parent.resolve().as_posix())

        self.main_window.action_close_file.setEnabled(True)
        self.main_window.action_edit_metadata.setEnabled(True)
        self.main_window.btn_close_file.setEnabled(True)
        self.main_window.btn_load_data.setEnabled(True)

        with contextlib.suppress(Exception):
            self._disconnect_data_controller_signals()
            self.data_controller.setParent(None)

        self.data_controller = DataController(self)
        self._connect_data_controller_signals()

        self.plot_controller.reset()

        self.data_controller.open_file(file_path)
        self.main_window.table_view_import_data.setModel(self.data_controller.data_model)
        self._set_column_models()

    @QtCore.Slot()
    def read_data(self) -> None:
        self.data_controller.load_data()
        for col in range(self.data_controller.base_df.width):
            self.main_window.table_view_import_data.horizontalHeader().setSectionResizeMode(
                col, QtWidgets.QHeaderView.ResizeMode.Stretch
            )

    @QtCore.Slot()
    def close_file(self) -> None:
        self.main_window.table_view_import_data.setModel(None)
        self.main_window.data_tree_widget_import_metadata.clear()
        self._clear_column_models()
        self.main_window.dock_section_list.list_view.setModel(None)

        with contextlib.suppress(Exception):
            self._disconnect_data_controller_signals()
            self.data_controller.setParent(None)

        self.data_controller = DataController(self)
        self._connect_data_controller_signals()

        self.plot_controller.reset()

        self.main_window.action_close_file.setEnabled(False)
        self.main_window.action_edit_metadata.setEnabled(False)
        self.main_window.btn_close_file.setEnabled(False)
        self.main_window.btn_load_data.setEnabled(False)

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
                if self.plot_controller.peak_scatter is not None:
                    self.plot_controller.peak_scatter.setBrush(value)
            case "signal_line_color":
                if self.plot_controller.signal_curve is not None:
                    self.plot_controller.signal_curve.setPen(value)
            case "rate_line_color":
                if self.plot_controller.rate_curve is not None:
                    self.plot_controller.rate_curve.setPen(value)
            case "section_marker_color":
                for r in self.plot_controller.regions:
                    r.setBrush(color=value)
            case "float_visual_precision":
                if isinstance(value, int):
                    self.data_controller.data_model.set_float_precision(value)
            case _:
                pass

    @QtCore.Slot()
    def apply_settings(self) -> None:
        self.plot_controller.apply_settings()
