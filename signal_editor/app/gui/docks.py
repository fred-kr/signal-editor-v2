import enum
import typing as t

import qfluentwidgets as qfw
from loguru import logger
from PySide6 import QtCore, QtGui, QtWidgets

from ...ui.ui_parameter_inputs import Ui_ParameterInputs
from .. import _type_defs as _t
from .._constants import COMBO_BOX_NO_SELECTION
from .._enums import (
    FilterMethod,
    IncompleteWindowMethod,
    LogLevel,
    NK2ECGPeakDetectionMethod,
    PeakDetectionMethod,
    PreprocessPipeline,
    StandardizationMethod,
    WFDBPeakDirection,
)
from ._widget_defaults import PEAK_DETECTION, PROCESSING
from .icons import AppIcons


class LoggingWindow(qfw.TextEdit):
    sig_log_message: t.ClassVar[QtCore.Signal] = QtCore.Signal(str, enum.IntEnum, dict)

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setReadOnly(True)
        self.setLineWrapMode(QtWidgets.QTextEdit.LineWrapMode.NoWrap)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setFont(QtGui.QFont("Roboto Mono", 10))
        logger.add(
            self.append_html,
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {message}",
            backtrace=True,
            diagnose=True,
        )

        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.sig_log_message.connect(self.append)
        self.action_clear_log = qfw.Action("Clear Log", parent=self)
        self.action_clear_log.triggered.connect(self.clear)

    @QtCore.Slot(QtCore.QPoint)
    def show_context_menu(self, pos: QtCore.QPoint) -> None:
        menu = qfw.RoundMenu(parent=self)
        menu.addAction(self.action_clear_log)
        menu.exec(self.mapToGlobal(pos))

    def append_html(self, message: str) -> None:
        record_dict: _t.LogRecordDict = message.record  # type: ignore
        level = LogLevel[record_dict["level"].name]

        self.sig_log_message.emit(message, level, record_dict)

    @QtCore.Slot(str, int, str)
    def append(self, message: str, log_level: LogLevel, record_dict: _t.LogRecordDict) -> None:
        self.moveCursor(QtGui.QTextCursor.MoveOperation.End)
        self.textCursor().insertHtml(f"{message}<br>")
        self.moveCursor(QtGui.QTextCursor.MoveOperation.End)


class StatusMessageDock(QtWidgets.QDockWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("StatusMessageDock")
        self.setWindowTitle("Status Log")
        self.setVisible(False)
        self.toggleViewAction().setIcon(AppIcons.Status.icon())

        self.log_text_box = LoggingWindow(self)
        self.setWindowIcon(AppIcons.History.icon())
        self.setWidget(self.log_text_box)


def _fill_combo_box_with_enum(combo_box: qfw.ComboBox, enum_class: t.Type[enum.Enum], allow_none: bool = False) -> None:
    combo_box.clear()
    for enum_value in enum_class:
        combo_box.addItem(enum_value.name, userData=enum_value.value)

    if allow_none:
        combo_box.insertItem(0, COMBO_BOX_NO_SELECTION, userData=None)


def _reset_widget(widget: QtWidgets.QWidget | QtCore.QObject) -> None:
    if isinstance(widget, (qfw.ComboBox, QtWidgets.QComboBox)):
        widget.setCurrentIndex(0)
        return
    if not hasattr(widget, "default_value"):
        return
    if isinstance(widget, (qfw.CheckBox, QtWidgets.QCheckBox, qfw.SwitchButton)):
        widget.setChecked(widget.default_value)  # type: ignore
    else:
        widget.setValue(widget.default_value)  # type: ignore


class ParameterInputs(QtWidgets.QWidget, Ui_ParameterInputs):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setupUi(self)


class ParameterInputsDock(QtWidgets.QDockWidget):
    sig_pipeline_requested: t.ClassVar[QtCore.Signal] = QtCore.Signal(enum.StrEnum)  # PreprocessPipeline
    sig_filter_requested: t.ClassVar[QtCore.Signal] = QtCore.Signal(dict)  # _t.SignalFilterParameters
    sig_standardization_requested: t.ClassVar[QtCore.Signal] = QtCore.Signal(dict)  # _t.StandardizationParameters
    sig_data_reset_requested: t.ClassVar[QtCore.Signal] = QtCore.Signal()

    sig_peak_detection_requested: t.ClassVar[QtCore.Signal] = QtCore.Signal(enum.StrEnum, dict)
    sig_clear_peaks_requested: t.ClassVar[QtCore.Signal] = QtCore.Signal()

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setVisible(False)
        self.setObjectName("DockWidgetParameterInputs")
        self.setWindowTitle("Parameter Inputs")
        self.toggleViewAction().setIcon(AppIcons.Options.icon())
        self.setWindowIcon(AppIcons.Options.icon())
        self.setAllowedAreas(QtCore.Qt.DockWidgetArea.AllDockWidgetAreas)

        self.ui = ParameterInputs()
        self.setWidget(self.ui)

        self._peak_defaults = PEAK_DETECTION
        self._processing_defaults = PROCESSING
        self._assign_defaults()

        self._setup_enum_combo_boxes()
        self._setup_command_bars()
        self._setup_status_indicators()
        self._setup_actions()

        self._on_filter_method_changed()
        self._on_pipeline_changed()
        self._on_peak_detection_method_changed(self.ui.combo_peak_method.currentData())

    @property
    def filter_inputs(self) -> list[QtWidgets.QWidget]:
        return [
            self.ui.dbl_sb_lower_cutoff,
            self.ui.dbl_sb_upper_cutoff,
            self.ui.sb_filter_order,
            self.ui.sb_filter_window_size,
            self.ui.dbl_sb_powerline,
        ]

    @property
    def standardization_inputs(self) -> list[QtWidgets.QWidget]:
        return [
            self.ui.switch_btn_standardize_rolling_window,
            self.ui.sb_standardize_window_size,
        ]

    def _setup_status_indicators(self) -> None:
        self.ui.icon_pipeline_status.setFixedSize(20, 20)
        self.ui.icon_filter_status.setFixedSize(20, 20)
        self.ui.icon_standardize_status.setFixedSize(20, 20)
        self.reset_status_indicators()

    def set_pipeline_status(self, status: bool) -> None:
        self.ui.icon_pipeline_status.setIcon(AppIcons.CheckmarkCircle.icon() if status else AppIcons.Circle.icon())

    def set_filter_status(self, status: bool, times_filtered: int) -> None:
        self.ui.icon_filter_status.setIcon(AppIcons.CheckmarkCircle.icon() if status else AppIcons.Circle.icon())
        self.ui.icon_filter_status.setToolTip(f"Filtered {times_filtered} times")

    def set_standardization_status(self, status: bool) -> None:
        self.ui.icon_standardize_status.setIcon(AppIcons.CheckmarkCircle.icon() if status else AppIcons.Circle.icon())

    def reset_status_indicators(self, status: bool = False) -> None:
        self.ui.icon_pipeline_status.setIcon(AppIcons.CheckmarkCircle.icon() if status else AppIcons.Circle.icon())
        self.ui.icon_filter_status.setIcon(AppIcons.CheckmarkCircle.icon() if status else AppIcons.Circle.icon())
        self.ui.icon_standardize_status.setIcon(AppIcons.CheckmarkCircle.icon() if status else AppIcons.Circle.icon())

    def _assign_defaults(self) -> None:
        # Peak Detection
        for name_prefix, param_map in self._peak_defaults.items():
            for name_suffix, default_value in param_map.items():
                name = f"{name_prefix}_{name_suffix}"
                widget = getattr(self.ui, name)
                widget.default_value = default_value

        # Processing
        for name, default_value in self._processing_defaults.items():
            widget = getattr(self.ui, name)
            widget.default_value = default_value

    def _setup_enum_combo_boxes(self) -> None:
        _fill_combo_box_with_enum(self.ui.combo_pipeline, PreprocessPipeline, allow_none=True)
        _fill_combo_box_with_enum(self.ui.combo_filter_method, FilterMethod, allow_none=True)
        _fill_combo_box_with_enum(self.ui.combo_peak_method, PeakDetectionMethod)
        _fill_combo_box_with_enum(self.ui.combo_standardize_method, StandardizationMethod, allow_none=True)
        _fill_combo_box_with_enum(self.ui.peak_neurokit2_algorithm_used, NK2ECGPeakDetectionMethod)
        _fill_combo_box_with_enum(self.ui.peak_xqrs_peak_dir, WFDBPeakDirection)
        _fill_combo_box_with_enum(self.ui.combo_incomplete_window_method, IncompleteWindowMethod)

    def _setup_actions(self) -> None:
        # Peak Detection
        # Actions
        self.ui.action_clear_peaks.triggered.connect(self.sig_clear_peaks_requested)
        self.ui.action_run_peak_detection.triggered.connect(self._on_run_peak_detection)
        self.ui.action_restore_defaults_peak_detection.triggered.connect(self._on_restore_defaults_peak_detection)
        # Widgets
        self.ui.combo_peak_method.currentIndexChanged.connect(
            lambda: self._on_peak_detection_method_changed(self.ui.combo_peak_method.currentData())
        )
        self.ui.peak_neurokit2_algorithm_used.currentIndexChanged.connect(
            lambda: self._show_nk_peak_algorithm_inputs(self.ui.peak_neurokit2_algorithm_used.currentData())
        )

        # Processing
        # Actions
        self.ui.action_run_processing.triggered.connect(self._on_run_processing)
        self.ui.action_restore_defaults_processing.triggered.connect(self._on_restore_defaults_processing)
        self.ui.action_restore_original_values.triggered.connect(self.sig_data_reset_requested)
        # Widgets
        self.ui.combo_pipeline.currentIndexChanged.connect(lambda: self._on_pipeline_changed())
        self.ui.combo_filter_method.currentIndexChanged.connect(lambda: self._on_filter_method_changed())
        self.ui.combo_standardize_method.currentIndexChanged.connect(lambda: self._on_standardize_method_changed())
        self.ui.switch_btn_standardize_rolling_window.checkedChanged.connect(self._on_switch_toggled)

    @QtCore.Slot(bool)
    def _on_switch_toggled(self, checked: bool) -> None:
        self.ui.container_standardize_rolling_window.setEnabled(checked)
        self.ui.sb_standardize_window_size.setEnabled(checked)

    def _setup_command_bars(self) -> None:
        # Peak Detection
        self.ui.command_bar_peak_detection.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.ui.command_bar_peak_detection.addActions(
            [
                self.ui.action_run_peak_detection,
                self.ui.action_clear_peaks,
                self.ui.action_restore_defaults_peak_detection,
            ]
        )

        # Processing
        self.ui.command_bar_processing.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.ui.command_bar_processing.addActions(
            [
                self.ui.action_run_processing,
                self.ui.action_restore_original_values,
                self.ui.action_restore_defaults_processing,
            ]
        )

    @QtCore.Slot()
    def _on_pipeline_changed(self) -> None:
        pipeline = self.ui.combo_pipeline.currentData()
        if pipeline is None:
            self.ui.combo_filter_method.setEnabled(True)
            self.ui.combo_standardize_method.setEnabled(True)
        else:
            self.ui.combo_filter_method.setCurrentIndex(0)
            self.ui.combo_standardize_method.setCurrentIndex(0)
            self.ui.combo_filter_method.setEnabled(False)
            self.ui.combo_standardize_method.setEnabled(False)

    @QtCore.Slot()
    def _on_filter_method_changed(self) -> None:
        filter_method = self.ui.combo_filter_method.currentData()
        if filter_method is None:
            for widget in self.filter_inputs:
                widget.setEnabled(False)
                _reset_widget(widget)
        elif filter_method in [FilterMethod.Butterworth, FilterMethod.ButterworthLegacy, FilterMethod.Bessel]:
            self.ui.dbl_sb_lower_cutoff.setEnabled(True)
            self.ui.dbl_sb_upper_cutoff.setEnabled(True)
            self.ui.sb_filter_order.setEnabled(True)
            self.ui.sb_filter_window_size.setEnabled(False)
            self.ui.dbl_sb_powerline.setEnabled(False)
        elif filter_method == FilterMethod.SavGol:
            self.ui.dbl_sb_lower_cutoff.setEnabled(False)
            self.ui.dbl_sb_upper_cutoff.setEnabled(False)
            self.ui.sb_filter_order.setEnabled(True)
            self.ui.sb_filter_window_size.setEnabled(True)
            self.ui.dbl_sb_powerline.setEnabled(False)
        elif filter_method == FilterMethod.FIR:
            self.ui.dbl_sb_lower_cutoff.setEnabled(True)
            self.ui.dbl_sb_upper_cutoff.setEnabled(True)
            self.ui.sb_filter_order.setEnabled(False)
            self.ui.sb_filter_window_size.setEnabled(True)
            self.ui.dbl_sb_powerline.setEnabled(False)
        elif filter_method == FilterMethod.Powerline:
            self.ui.dbl_sb_lower_cutoff.setEnabled(False)
            self.ui.dbl_sb_upper_cutoff.setEnabled(False)
            self.ui.sb_filter_order.setEnabled(False)
            self.ui.sb_filter_window_size.setEnabled(False)
            self.ui.dbl_sb_powerline.setEnabled(True)

    @QtCore.Slot()
    def _on_standardize_method_changed(self) -> None:
        standardize_method = self.ui.combo_standardize_method.currentData()
        if standardize_method is None:
            for widget in self.standardization_inputs:
                widget.setEnabled(False)
                _reset_widget(widget)
        elif standardize_method == StandardizationMethod.ZScore:
            self.ui.switch_btn_standardize_rolling_window.setEnabled(True)
        else:
            self.ui.switch_btn_standardize_rolling_window.setChecked(False)
            self.ui.switch_btn_standardize_rolling_window.setEnabled(False)

    @QtCore.Slot()
    def _on_run_processing(self) -> None:
        pipeline = self.ui.combo_pipeline.currentData()
        # logger.debug(f"Pipeline: {pipeline}")
        if pipeline is not None:
            pipeline = PreprocessPipeline(pipeline)
            self.sig_pipeline_requested.emit(pipeline)
        else:
            filter_method = self.ui.combo_filter_method.currentData()
            if filter_method is not None:
                filter_method = FilterMethod(filter_method)
                filter_params = self._get_filter_params(filter_method)
                self.sig_filter_requested.emit(filter_params)
            standardize_method = self.ui.combo_standardize_method.currentData()
            if standardize_method is not None:
                standardize_method = StandardizationMethod(standardize_method)
                standardize_params = self._get_standardize_params(standardize_method)
                self.sig_standardization_requested.emit(standardize_params)

    def _get_filter_params(self, method: FilterMethod) -> _t.SignalFilterParameters:
        window = self.ui.sb_filter_window_size
        if window.value() == window.minimum():
            window_size = "default"
        else:
            window_size = window.value()
        return {
            "lowcut": self.ui.dbl_sb_lower_cutoff.value(),
            "highcut": self.ui.dbl_sb_upper_cutoff.value(),
            "method": method,
            "order": self.ui.sb_filter_order.value(),
            "window_size": window_size,
            "powerline": self.ui.dbl_sb_powerline.value(),
        }

    def _get_standardize_params(self, method: StandardizationMethod) -> _t.StandardizationParameters:
        return {
            "method": method,
            "window_size": self.ui.sb_standardize_window_size.value()
            if self.ui.switch_btn_standardize_rolling_window.isChecked()
            else None,
        }

    @QtCore.Slot()
    def _on_run_peak_detection(self) -> None:
        peak_method = PeakDetectionMethod(self.ui.combo_peak_method.currentData())
        peak_params = self.get_peak_detection_params(peak_method)
        self.sig_peak_detection_requested.emit(peak_method, peak_params)

    @QtCore.Slot(str)
    def _on_peak_detection_method_changed(self, method: str) -> None:
        peak_method = PeakDetectionMethod(method)
        if peak_method == PeakDetectionMethod.PPGElgendi:
            self.ui.stacked_peak_parameters.setCurrentWidget(self.ui.page_peak_elgendi_ppg)
        elif peak_method == PeakDetectionMethod.ECGNeuroKit2:
            self.ui.stacked_peak_parameters.setCurrentWidget(self.ui.page_peak_neurokit2)
            self._show_nk_peak_algorithm_inputs(self.ui.peak_neurokit2_algorithm_used.currentData())
        elif peak_method == PeakDetectionMethod.LocalMaxima:
            self.ui.stacked_peak_parameters.setCurrentWidget(self.ui.page_peak_local_max)
        elif peak_method == PeakDetectionMethod.LocalMinima:
            self.ui.stacked_peak_parameters.setCurrentWidget(self.ui.page_peak_local_min)
        elif peak_method == PeakDetectionMethod.WFDBXQRS:
            self.ui.stacked_peak_parameters.setCurrentWidget(self.ui.page_peak_xqrs)

    @QtCore.Slot(str)
    def _show_nk_peak_algorithm_inputs(self, method: str) -> None:
        method = NK2ECGPeakDetectionMethod(method)
        if method == NK2ECGPeakDetectionMethod.Default:
            self.ui.stacked_nk2_method_parameters.setCurrentWidget(self.ui.nk2_page_neurokit)
        elif method == NK2ECGPeakDetectionMethod.Promac:
            self.ui.stacked_nk2_method_parameters.setCurrentWidget(self.ui.nk2_page_promac)
        elif method == NK2ECGPeakDetectionMethod.Gamboa2008:
            self.ui.stacked_nk2_method_parameters.setCurrentWidget(self.ui.nk2_page_gamboa)
        elif method == NK2ECGPeakDetectionMethod.Emrich2023:
            self.ui.stacked_nk2_method_parameters.setCurrentWidget(self.ui.nk2_page_emrich)
        else:
            self.ui.stacked_nk2_method_parameters.setCurrentWidget(self.ui.nk2_page_no_params)

    def get_peak_detection_params(self, method: PeakDetectionMethod) -> _t.PeakDetectionMethodParameters:
        if method == PeakDetectionMethod.PPGElgendi:
            peak_params = _t.PeaksPPGElgendi(
                peakwindow=self.ui.peak_elgendi_ppg_peakwindow.value(),
                beatwindow=self.ui.peak_elgendi_ppg_beatwindow.value(),
                beatoffset=self.ui.peak_elgendi_ppg_beatoffset.value(),
                mindelay=self.ui.peak_elgendi_ppg_mindelay.value(),
            )
        elif method == PeakDetectionMethod.ECGNeuroKit2:
            nk_algorithm = NK2ECGPeakDetectionMethod(self.ui.peak_neurokit2_algorithm_used.currentData())
            if nk_algorithm == NK2ECGPeakDetectionMethod.Default:
                nk_params = _t.NK2PeaksNeuroKit(
                    smoothwindow=self.ui.peak_neurokit2_smoothwindow.value(),
                    avgwindow=self.ui.peak_neurokit2_avgwindow.value(),
                    gradthreshweight=self.ui.peak_neurokit2_gradthreshweight.value(),
                    minlenweight=self.ui.peak_neurokit2_minlenweight.value(),
                    mindelay=self.ui.peak_neurokit2_mindelay.value(),
                )
            elif nk_algorithm == NK2ECGPeakDetectionMethod.Promac:
                nk_params = _t.NK2PeaksPromac(
                    threshold=self.ui.peak_promac_threshold.value(),
                    gaussian_sd=self.ui.peak_promac_gaussian_sd.value(),
                )
            elif nk_algorithm == NK2ECGPeakDetectionMethod.Gamboa2008:
                nk_params = _t.NK2PeaksGamboa(tol=self.ui.peak_gamboa_tol.value())
            elif nk_algorithm == NK2ECGPeakDetectionMethod.Emrich2023:
                nk_params = _t.NK2PeaksEmrich(
                    window_seconds=self.ui.peak_emrich_window_seconds.value(),
                    window_overlap=self.ui.peak_emrich_window_overlap.value(),
                    accelerated=self.ui.peak_emrich_accelerated.isChecked(),
                )
            else:
                nk_params = None

            peak_params = _t.PeaksECGNeuroKit2(method=nk_algorithm, params=nk_params)

        elif method == PeakDetectionMethod.LocalMaxima:
            peak_params = _t.PeaksLocalMaxima(
                search_radius=self.ui.peak_local_max_radius.value(),
                min_distance=self.ui.peak_local_max_min_dist.value(),
            )

        elif method == PeakDetectionMethod.LocalMinima:
            peak_params = _t.PeaksLocalMinima(
                search_radius=self.ui.peak_local_min_radius.value(),
                min_distance=self.ui.peak_local_min_min_dist.value(),
            )

        elif method == PeakDetectionMethod.WFDBXQRS:
            peak_params = _t.PeaksWFDBXQRS(
                search_radius=self.ui.peak_xqrs_search_radius.value(),
                peak_dir=WFDBPeakDirection(self.ui.peak_xqrs_peak_dir.currentData()),
                min_peak_distance=self.ui.peak_xqrs_min_peak_distance.value(),
            )

        return peak_params

    def get_rate_calculation_params(self) -> _t.RollingRateKwargsDict:
        new_window_every = self.ui.sb_every_seconds.value()
        window_length = self.ui.sb_period_seconds.value()
        incomplete_window_method = IncompleteWindowMethod(self.ui.combo_incomplete_window_method.currentData())

        return {
            "sec_new_window_every": new_window_every,
            "sec_window_length": window_length,
            "incomplete_window_method": incomplete_window_method,
        }

    @QtCore.Slot()
    def _on_restore_defaults_peak_detection(self) -> None:
        current_input_page = self.ui.stacked_peak_parameters.currentWidget()
        for child in current_input_page.children():
            _reset_widget(child)

        if current_input_page == self.ui.page_peak_neurokit2:
            for child in self.ui.stacked_nk2_method_parameters.currentWidget().children():
                _reset_widget(child)

    @QtCore.Slot()
    def _on_restore_defaults_processing(self) -> None:
        for cb in [self.ui.combo_pipeline, self.ui.combo_filter_method, self.ui.combo_standardize_method]:
            cb.setCurrentIndex(0)

        for widget_name, default_value in self._processing_defaults.items():
            widget = getattr(self.ui, widget_name)
            if isinstance(default_value, bool):
                widget.setChecked(default_value)
            else:
                widget.setValue(default_value)


class SectionListView(qfw.ListView):
    sig_delete_current_item: t.ClassVar[QtCore.Signal] = QtCore.Signal(QtCore.QModelIndex)
    sig_show_summary: t.ClassVar[QtCore.Signal] = QtCore.Signal(QtCore.QModelIndex)

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setSelectRightClickedRow(True)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.setSelectionRectVisible(True)
        self.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)

    @QtCore.Slot()
    def emit_delete_current_request(self) -> None:
        index = self.currentIndex()
        self.sig_delete_current_item.emit(index)

    @QtCore.Slot()
    def emit_show_summary_request(self) -> None:
        index = self.currentIndex()
        self.sig_show_summary.emit(index)


class SectionListWidget(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout()

        self.list_view = SectionListView()

        label_active_section = qfw.StrongBodyLabel("Active Section: ", self)
        layout.addWidget(label_active_section)
        self.label_active_section = label_active_section

        command_bar = qfw.CommandBar()
        command_bar.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        command_bar.setObjectName("command_bar_section_list")
        layout.addWidget(command_bar)
        self.command_bar = command_bar

        confirm_cancel_btns = QtWidgets.QWidget()
        confirm_cancel_layout = QtWidgets.QHBoxLayout(confirm_cancel_btns)
        confirm_cancel_layout.setContentsMargins(0, 0, 0, 0)

        confirm_btn = qfw.PushButton(icon=AppIcons.CheckmarkCircle.icon(), text="Confirm")
        confirm_cancel_layout.addWidget(confirm_btn)
        self.btn_confirm = confirm_btn

        cancel_btn = qfw.PushButton(icon=AppIcons.DismissCircle.icon(), text="Cancel")
        confirm_cancel_layout.addWidget(cancel_btn)
        self.btn_cancel = cancel_btn

        self.btn_container = confirm_cancel_btns
        confirm_cancel_btns.setLayout(confirm_cancel_layout)
        layout.addWidget(confirm_cancel_btns)

        layout.addWidget(self.list_view)
        self.main_layout = layout
        self.setLayout(layout)


class SectionListDock(QtWidgets.QDockWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setVisible(False)
        self.setObjectName("SectionListDock")
        self.setWindowTitle("Section List")
        self.setWindowIcon(AppIcons.SignalEditor.icon())

        self._widget = SectionListWidget()
        self.list_view = self._widget.list_view
        self.command_bar = self._widget.command_bar
        self.label_active_section = self._widget.label_active_section
        self.btn_confirm = self._widget.btn_confirm
        self.btn_cancel = self._widget.btn_cancel
        self.btn_container = self._widget.btn_container

        self.setWidget(self._widget)
