import typing as t

import superqt
import qfluentwidgets as qfw
from PySide6 import QtCore, QtGui, QtWidgets

from signal_editor.ui.ui_dock_processing_input import Ui_DockWidgetProcessingInputs
from ... import type_defs as _t
from ...config import Config
from ...enum_defs import FilterMethod, FilterType, PreprocessPipeline, StandardizationMethod


class ProcessingInputsDock(QtWidgets.QDockWidget, Ui_DockWidgetProcessingInputs):
    sig_pipeline_requested: t.ClassVar[QtCore.Signal] = QtCore.Signal(str)
    sig_filter_requested: t.ClassVar[QtCore.Signal] = QtCore.Signal(object)
    sig_standardization_requested: t.ClassVar[QtCore.Signal] = QtCore.Signal(object)
    sig_data_reset_requested: t.ClassVar[QtCore.Signal] = QtCore.Signal()

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.setVisible(False)
        self.toggleViewAction().setIcon(QtGui.QIcon(":/icons/filter_edit"))
        sampling_rate = Config().internal.LastSamplingRate
        if sampling_rate <= 0:
            sampling_rate = 400
        freq_range = (0, sampling_rate // 2)

        dbl_slider_lowcut = superqt.QLabeledDoubleSlider()
        dbl_slider_lowcut.setMinimumHeight(31)
        dbl_slider_lowcut.setEdgeLabelMode(superqt.QLabeledDoubleSlider.EdgeLabelMode.LabelIsValue)
        dbl_slider_lowcut.setDecimals(1)
        dbl_slider_lowcut.setRange(*freq_range)
        dbl_slider_lowcut.setValue(1)
        self.dbl_slider_lowcut = dbl_slider_lowcut
        self.v_layout_grp_box_filter_parameters.addWidget(QtWidgets.QLabel("Low-cut frequency"))
        self.v_layout_grp_box_filter_parameters.addWidget(self.dbl_slider_lowcut)

        dbl_slider_highcut = superqt.QLabeledDoubleSlider()
        dbl_slider_highcut.setEdgeLabelMode(superqt.QLabeledDoubleSlider.EdgeLabelMode.LabelIsValue)
        dbl_slider_highcut.setDecimals(1)
        dbl_slider_highcut.setRange(*freq_range)
        dbl_slider_highcut.setValue(8)
        self.dbl_slider_highcut = dbl_slider_highcut
        self.v_layout_grp_box_filter_parameters.addWidget(QtWidgets.QLabel("High-cut frequency"))
        self.v_layout_grp_box_filter_parameters.addWidget(self.dbl_slider_highcut)

        slider_window_size_filter = superqt.QLabeledSlider()
        slider_window_size_filter.setEdgeLabelMode(superqt.QLabeledSlider.EdgeLabelMode.LabelIsValue)
        slider_window_size_filter.setRange(5, 5_000)
        slider_window_size_filter.setValue(500)
        self.slider_window_size_filter = slider_window_size_filter
        self.v_layout_grp_box_filter_parameters.addWidget(QtWidgets.QLabel("Window size"))
        self.v_layout_grp_box_filter_parameters.addWidget(self.slider_window_size_filter)

        combo_powerline = QtWidgets.QComboBox()
        combo_powerline.setMinimumHeight(31)
        combo_powerline.addItem("50 Hz", userData=50)
        combo_powerline.addItem("60 Hz", userData=60)
        combo_powerline.setCurrentIndex(0)
        # combo_powerline.setItemData(0, 50, QtCore.Qt.ItemDataRole.UserRole)
        # combo_powerline.setItemData(1, 60, QtCore.Qt.ItemDataRole.UserRole)
        self.combo_powerline = combo_powerline
        self.v_layout_grp_box_filter_parameters.addWidget(QtWidgets.QLabel("Power line"))
        self.v_layout_grp_box_filter_parameters.addWidget(self.combo_powerline)

        slider_window_size_standardize = superqt.QLabeledSlider(
            QtCore.Qt.Orientation.Horizontal, self.grp_box_standardize_rolling_window
        )
        slider_window_size_standardize.setEdgeLabelMode(superqt.QLabeledSlider.EdgeLabelMode.LabelIsValue)

        slider_window_size_standardize.setRange(3, 3_333)
        slider_window_size_standardize.setValue(300)
        self.v_layout_grp_box_standardize_rolling_window.addWidget(slider_window_size_standardize)

        self.slider_window_size_standardize = slider_window_size_standardize

        self.enum_combo_pipeline.setEnumClass(PreprocessPipeline, allow_none=True)
        self.enum_combo_filter_method.setEnumClass(FilterMethod)
        self.enum_combo_filter_type.setEnumClass(FilterType)
        self.enum_combo_standardize_method.setEnumClass(StandardizationMethod)

        self._connect_qt_signals()
        self._set_filter_widget_states(self.enum_combo_filter_method.currentEnum())
        self._set_frequency_slider_states(self.enum_combo_filter_type.currentEnum())
        self._set_rolling_window_checkbox_state(self.enum_combo_standardize_method.currentEnum())
        self.update_frequency_sliders(sampling_rate)
        self._restore_defaults()

    def _connect_qt_signals(self) -> None:
        self.btn_run_pipeline.clicked.connect(self._emit_pipeline_requested)
        self.btn_apply_signal_filter.clicked.connect(self._emit_filter_requested)
        self.btn_apply_standardization.clicked.connect(self._emit_standardization_requested)
        self.btn_reset_data.clicked.connect(self._emit_data_reset_requested)
        self.btn_reset_processing_inputs.clicked.connect(self._restore_defaults)

        self.enum_combo_filter_method.currentEnumChanged.connect(self._set_filter_widget_states)
        self.enum_combo_filter_type.currentEnumChanged.connect(self._set_frequency_slider_states)

        self.enum_combo_standardize_method.currentEnumChanged.connect(self._set_rolling_window_checkbox_state)

    def update_frequency_sliders(self, sampling_rate: int) -> None:
        freq_range = (0, sampling_rate // 2)
        self.dbl_slider_lowcut.setRange(*freq_range)
        self.dbl_slider_highcut.setRange(*freq_range)

    @QtCore.Slot()
    def _restore_defaults(self) -> None:
        self.enum_combo_pipeline.setCurrentEnum(None)
        self.enum_combo_filter_method.setCurrentEnum(FilterMethod.Butterworth)
        self.enum_combo_filter_type.setCurrentEnum(FilterType.LowPass)
        self.dbl_slider_lowcut.setValue(1)
        self.dbl_slider_highcut.setValue(8)
        self.spin_box_filter_order.setValue(3)
        self.slider_window_size_filter.setValue(500)
        self.combo_powerline.setCurrentIndex(0)
        self.enum_combo_standardize_method.setCurrentEnum(StandardizationMethod.ZScore)
        self.grp_box_standardize_rolling_window.setChecked(False)
        self.slider_window_size_standardize.setValue(300)

    @QtCore.Slot(object)
    def _set_rolling_window_checkbox_state(self, method_enum: StandardizationMethod) -> None:
        if method_enum == StandardizationMethod.ZScore:
            self.grp_box_standardize_rolling_window.setEnabled(True)
        else:
            self.grp_box_standardize_rolling_window.setChecked(False)
            self.grp_box_standardize_rolling_window.setEnabled(False)

    @QtCore.Slot()
    def _emit_pipeline_requested(self) -> None:
        pipeline = self.enum_combo_pipeline.currentEnum()
        if pipeline is not None:
            pipeline = PreprocessPipeline(pipeline)
            self.sig_pipeline_requested.emit(pipeline)

    @QtCore.Slot()
    def _emit_filter_requested(self) -> None:
        freq_cutoff_type = self.enum_combo_filter_type.currentEnum()
        if freq_cutoff_type is None:
            return
        lowcut = None
        highcut = None
        if freq_cutoff_type == FilterType.LowPass:
            highcut = self.dbl_slider_highcut.value()
        elif freq_cutoff_type == FilterType.HighPass:
            lowcut = self.dbl_slider_lowcut.value()
        elif freq_cutoff_type == FilterType.BandPass:
            lowcut = self.dbl_slider_lowcut.value()
            highcut = self.dbl_slider_highcut.value()

        method = FilterMethod(self.enum_combo_filter_method.currentEnum())
        order = self.spin_box_filter_order.value()
        powerline = self.combo_powerline.currentData(QtCore.Qt.ItemDataRole.UserRole)

        filter_params: _t.SignalFilterParameters = {
            "lowcut": lowcut,
            "highcut": highcut,
            "method": method,
            "order": order,
            "window_size": self.slider_window_size_filter.value(),
            "powerline": powerline,
        }

        self.sig_filter_requested.emit(filter_params)

    @QtCore.Slot()
    def _emit_standardization_requested(self) -> None:
        method = StandardizationMethod(self.enum_combo_standardize_method.currentEnum())
        window_size = self.slider_window_size_standardize.value() if self.grp_box_standardize_rolling_window.isChecked() else None
        standardization_params: _t.StandardizationParameters = {
            "method": method,
            "window_size": window_size,
        }
        self.sig_standardization_requested.emit(standardization_params)

    @QtCore.Slot()
    def _emit_data_reset_requested(self) -> None:
        self.sig_data_reset_requested.emit()

    @QtCore.Slot(object)
    def _set_frequency_slider_states(self, filter_type_enum: FilterType) -> None:
        # Show the appropriate slider based on the filter type
        # Low-pass: Enable highcut slider, disable lowcut slider
        # High-pass: Enable lowcut slider, disable highcut slider
        # Band-pass: Enable both lowcut and highcut sliders
        if not self.enum_combo_filter_type.isEnabled():
            return
        if filter_type_enum == FilterType.LowPass:
            self.dbl_slider_lowcut.setEnabled(False)
            self.dbl_slider_highcut.setEnabled(True)
        elif filter_type_enum == FilterType.HighPass:
            self.dbl_slider_lowcut.setEnabled(True)
            self.dbl_slider_highcut.setEnabled(False)
        elif filter_type_enum == FilterType.BandPass:
            self.dbl_slider_lowcut.setEnabled(True)
            self.dbl_slider_highcut.setEnabled(True)

    @QtCore.Slot(object)
    def _set_filter_widget_states(self, method_enum: FilterMethod) -> None:
        method_enum = FilterMethod(method_enum)
        if method_enum in [
            FilterMethod.Butterworth,
            FilterMethod.ButterworthLegacy,
            FilterMethod.Bessel,
        ]:
            self.enum_combo_filter_type.setEnabled(True)
            self.dbl_slider_lowcut.setEnabled(True)
            self.dbl_slider_highcut.setEnabled(True)
            self.spin_box_filter_order.setEnabled(True)
            self.slider_window_size_filter.setEnabled(False)
            self.combo_powerline.setEnabled(False)
        elif method_enum == FilterMethod.SavGol:
            self.enum_combo_filter_type.setEnabled(False)
            self.dbl_slider_lowcut.setEnabled(False)
            self.dbl_slider_highcut.setEnabled(False)
            self.spin_box_filter_order.setEnabled(True)
            self.slider_window_size_filter.setEnabled(True)
            self.combo_powerline.setEnabled(False)
        elif method_enum == FilterMethod.FIR:
            self.enum_combo_filter_type.setEnabled(True)
            self.dbl_slider_lowcut.setEnabled(True)
            self.dbl_slider_highcut.setEnabled(True)
            self.spin_box_filter_order.setEnabled(False)
            self.slider_window_size_filter.setEnabled(True)
            self.combo_powerline.setEnabled(False)
        elif method_enum == FilterMethod.Powerline:
            self.enum_combo_filter_type.setEnabled(False)
            self.dbl_slider_lowcut.setEnabled(False)
            self.dbl_slider_highcut.setEnabled(False)
            self.spin_box_filter_order.setEnabled(False)
            self.slider_window_size_filter.setEnabled(False)
            self.combo_powerline.setEnabled(True)
        elif method_enum == FilterMethod.NoFilter:
            self.enum_combo_filter_type.setEnabled(False)
            self.dbl_slider_lowcut.setEnabled(False)
            self.dbl_slider_highcut.setEnabled(False)
            self.spin_box_filter_order.setEnabled(False)
            self.slider_window_size_filter.setEnabled(False)
            self.combo_powerline.setEnabled(False)

        self._set_frequency_slider_states(FilterType(self.enum_combo_filter_type.currentEnum()))


class FluentProcessingInputsDock(QtWidgets.QDockWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        dbl_slider_lowcut = qfw.