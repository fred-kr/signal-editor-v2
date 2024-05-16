import enum
import typing as t

from PySide6 import QtCore, QtGui, QtWidgets

from signal_editor.app import type_defs as _t
from signal_editor.app.enum_defs import (
    NK2ECGPeakDetectionMethod,
    PeakDetectionMethod,
    WFDBPeakDirection,
)
from signal_editor.app.gui.widgets import _widget_defaults as _widget_defs
from signal_editor.ui.ui_dock_peak_detection import Ui_DockWidgetPeakDetection


class PeakDetectionDock(QtWidgets.QDockWidget, Ui_DockWidgetPeakDetection):
    sig_peak_detection_requested: t.ClassVar[QtCore.Signal] = QtCore.Signal(enum.StrEnum, dict)
    sig_clear_peaks_requested: t.ClassVar[QtCore.Signal] = QtCore.Signal()

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.setVisible(False)
        self.toggleViewAction().setIcon(QtGui.QIcon(":/icons/target_edit"))
        self.setWindowIcon(QtGui.QIcon(":/icons/search"))

        self._DEFAULT_VALUES = _widget_defs.PEAK_DETECTION
        self.collapsible_nk2_peak_inputs.setContent(self.stacked_nk2_method_parameters)
        self.collapsible_nk2_peak_inputs.setText("Tune-able Parameters")

        self.peak_neurokit2_algorithm_used.setEnumClass(NK2ECGPeakDetectionMethod)
        self.peak_neurokit2_algorithm_used.setCurrentEnum(NK2ECGPeakDetectionMethod.Default)

        self.enum_combo_peak_method.setEnumClass(PeakDetectionMethod)
        self.enum_combo_peak_method.setCurrentEnum(PeakDetectionMethod.PPGElgendi)

        self.peak_xqrs_peak_dir.setEnumClass(WFDBPeakDirection)
        self.peak_xqrs_peak_dir.setCurrentEnum(WFDBPeakDirection.Up)
        self.connect_qt_signals()
        self._show_method_parameters(PeakDetectionMethod.PPGElgendi)

    def connect_qt_signals(self) -> None:
        self.enum_combo_peak_method.currentEnumChanged.connect(self._show_method_parameters)
        self.peak_neurokit2_algorithm_used.currentEnumChanged.connect(
            self._show_nk_peak_algorithm_inputs
        )
        self.btn_run_peak_detection.clicked.connect(self._emit_peak_detection_requested)
        self.btn_reset_peak_inputs.clicked.connect(self._restore_defaults)
        self.btn_clear_peaks.clicked.connect(self.sig_clear_peaks_requested)

    @QtCore.Slot(enum.StrEnum)
    def _show_method_parameters(self, method: PeakDetectionMethod) -> None:
        if method == PeakDetectionMethod.PPGElgendi:
            self.stacked_peak_parameters.setCurrentWidget(self.page_peak_elgendi_ppg)
        elif method == PeakDetectionMethod.ECGNeuroKit2:
            self.stacked_peak_parameters.setCurrentWidget(self.page_peak_neurokit2)
            current_nk2_method = NK2ECGPeakDetectionMethod(
                self.peak_neurokit2_algorithm_used.currentEnum()
            )
            self._show_nk_peak_algorithm_inputs(current_nk2_method)
        elif method == PeakDetectionMethod.LocalMaxima:
            self.stacked_peak_parameters.setCurrentWidget(self.page_peak_local_max)
        elif method == PeakDetectionMethod.LocalMinima:
            self.stacked_peak_parameters.setCurrentWidget(self.page_peak_local_min)
        elif method == PeakDetectionMethod.WFDBXQRS:
            self.stacked_peak_parameters.setCurrentWidget(self.page_peak_xqrs)

    @QtCore.Slot(enum.StrEnum)
    def _show_nk_peak_algorithm_inputs(self, nk_algorithm: NK2ECGPeakDetectionMethod) -> None:
        if nk_algorithm == NK2ECGPeakDetectionMethod.Default:
            self.stacked_nk2_method_parameters.setCurrentWidget(self.nk2_page_neurokit)
            self.collapsible_nk2_peak_inputs.setLocked(False)
            self.collapsible_nk2_peak_inputs.expand()
        elif nk_algorithm == NK2ECGPeakDetectionMethod.All:
            self.stacked_nk2_method_parameters.setCurrentWidget(self.nk2_page_promac)
            self.collapsible_nk2_peak_inputs.setLocked(False)
            self.collapsible_nk2_peak_inputs.expand()
        elif nk_algorithm == NK2ECGPeakDetectionMethod.Gamboa2008:
            self.stacked_nk2_method_parameters.setCurrentWidget(self.nk2_page_gamboa)
            self.collapsible_nk2_peak_inputs.setLocked(False)
            self.collapsible_nk2_peak_inputs.expand()
        # elif nk_algorithm == NK2ECGPeakDetectionMethod.SlopeSumFunction:
        #     self.stacked_nk2_method_parameters.setCurrentWidget(self.nk2_page_ssf)
        #     self.collapsible_nk2_peak_inputs.setLocked(False)
        #     self.collapsible_nk2_peak_inputs.expand()
        # TODO: enable again once ts2vg package works
        # elif nk_algorithm == NK2ECGPeakDetectionMethod.Emrich2023:
        #     self.stacked_nk2_method_parameters.setCurrentWidget(self.nk2_page_emrich)
        #     self.collapsible_nk2_peak_inputs.setLocked(False)
        #     self.collapsible_nk2_peak_inputs.expand()
        else:
            self.collapsible_nk2_peak_inputs.collapse()
            self.collapsible_nk2_peak_inputs.setLocked(True)

    @QtCore.Slot()
    def _emit_peak_detection_requested(self) -> None:
        method = PeakDetectionMethod(self.enum_combo_peak_method.currentEnum())
        peak_params = self.get_peak_detection_parameters(method)
        self.sig_peak_detection_requested.emit(method, peak_params)

    def get_peak_detection_parameters(
        self, method: PeakDetectionMethod
    ) -> _t.PeakDetectionMethodParameters:
        if method == PeakDetectionMethod.PPGElgendi:
            peak_params = _t.PeaksPPGElgendi(
                peakwindow=self.peak_elgendi_ppg_peakwindow.value(),
                beatwindow=self.peak_elgendi_ppg_beatwindow.value(),
                beatoffset=self.peak_elgendi_ppg_beatoffset.value(),
                mindelay=self.peak_elgendi_ppg_mindelay.value(),
            )
        elif method == PeakDetectionMethod.ECGNeuroKit2:
            nk_method = NK2ECGPeakDetectionMethod(self.peak_neurokit2_algorithm_used.currentEnum())
            if nk_method == NK2ECGPeakDetectionMethod.Default:
                nk_params = _t.NK2PeaksNeuroKit(
                    smoothwindow=self.peak_neurokit2_smoothwindow.value(),
                    avgwindow=self.peak_neurokit2_avgwindow.value(),
                    gradthreshweight=self.peak_neurokit2_gradthreshweight.value(),
                    minlenweight=self.peak_neurokit2_minlenweight.value(),
                    mindelay=self.peak_neurokit2_mindelay.value(),
                )
            elif nk_method == NK2ECGPeakDetectionMethod.All:
                nk_params = _t.NK2PeaksPromac(
                    threshold=self.peak_promac_threshold.value(),
                    gaussian_sd=self.peak_promac_gaussian_sd.value(),
                )
            elif nk_method == NK2ECGPeakDetectionMethod.Gamboa2008:
                nk_params = _t.NK2PeaksGamboa(tol=self.peak_gamboa_tol.value())
            # elif nk_method == NK2ECGPeakDetectionMethod.SlopeSumFunction:
            #     nk_params = _t.NK2PeaksSSF(
            #         threshold=self.peak_ssf_threshold.value(),
            #         before=self.peak_ssf_before.value(),
            #         after=self.peak_ssf_after.value(),
            #     )
            # elif nk_method == NK2ECGPeakDetectionMethod.Emrich2023:
            #     nk_params = _t.NK2PeaksEmrich(
            #         window_seconds=self.peak_emrich_window_seconds.value(),
            #         window_overlap=self.peak_emrich_window_overlap.value(),
            #         accelerated=self.peak_emrich_accelerated.isChecked(),
            #     )
            else:
                nk_params = None
            peak_params = _t.PeaksECGNeuroKit2(
                method=nk_method,
                params=nk_params,
            )
        elif method == PeakDetectionMethod.LocalMaxima:
            peak_params = _t.PeaksLocalMaxima(
                search_radius=self.peak_local_max_radius.value(),
                min_distance=self.peak_local_max_min_dist.value(),
            )
        elif method == PeakDetectionMethod.LocalMinima:
            peak_params = _t.PeaksLocalMinima(
                search_radius=self.peak_local_min_radius.value(),
                min_distance=self.peak_local_min_min_dist.value(),
            )
        elif method == PeakDetectionMethod.WFDBXQRS:
            peak_dir: WFDBPeakDirection = (
                self.peak_xqrs_peak_dir.currentEnum() or WFDBPeakDirection.Up
            )
            peak_params = _t.PeaksWFDBXQRS(
                search_radius=self.peak_xqrs_search_radius.value(), peak_dir=peak_dir
            )
        else:
            raise ValueError(f"Unknown peak detection method: {method}")

        return peak_params

    @QtCore.Slot()
    def _restore_defaults(self) -> None:
        self.enum_combo_peak_method.setCurrentEnum(PeakDetectionMethod.PPGElgendi)

        for widget_name_prefix, param_map in self._DEFAULT_VALUES.items():
            for param_name, default_value in param_map.items():
                widget_name = f"{widget_name_prefix}_{param_name}"
                widget = getattr(self, widget_name)
                if isinstance(default_value, bool):
                    widget.setChecked(default_value)
                elif isinstance(default_value, (int, float)):
                    widget.setValue(default_value)
                else:
                    widget.setCurrentEnum(default_value)
