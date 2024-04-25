import enum
import typing as t

import superqt
from PySide6 import QtCore, QtGui, QtWidgets

from ... import type_defs as _t
from ...enum_defs import FilterMethod, FilterType, PreprocessPipeline, StandardizationMethod


class ProcessingParametersDialog(QtWidgets.QDialog):
    sig_pipeline_run: t.ClassVar[QtCore.Signal] = QtCore.Signal(enum.StrEnum)
    sig_filter_applied: t.ClassVar[QtCore.Signal] = QtCore.Signal(dict)
    sig_standardization_applied: t.ClassVar[QtCore.Signal] = QtCore.Signal(dict)
    sig_restore_unfiltered: t.ClassVar[QtCore.Signal] = QtCore.Signal()

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowModality(QtCore.Qt.WindowModality.NonModal)
        self.setMinimumWidth(400)
        # self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowType.WindowContextHelpButtonHint)
        self.setWindowIcon(QtGui.QIcon(":/icons/app_wave"))
        self.setWindowTitle("Processing Parameters")

        self._layout = QtWidgets.QVBoxLayout()

        h1_font = QtGui.QFont("Segoe UI", 14, QtGui.QFont.Weight.Bold)

        main_header = QtWidgets.QLabel("Pre-processing Options")
        main_header.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed
        )
        main_header.setFont(h1_font)
        self._layout.addWidget(main_header)

        self._setup_pipeline_section()
        self._setup_custom_filter_section()
        self._setup_standardization_section()

        self.btn_reset_inputs = QtWidgets.QPushButton("Reset Inputs")
        self.btn_reset_inputs.setToolTip("Set all inputs to their default values")
        self.btn_reset_inputs.clicked.connect(self._restore_defaults)

        self.btn_reset_data = QtWidgets.QPushButton("Reset Data")
        self.btn_reset_data.setToolTip("Restore the data to its original, unfiltered state")
        self.btn_reset_data.clicked.connect(self._emit_restore_unfiltered)

        self.btn_done = QtWidgets.QPushButton("Done")
        self.btn_done.clicked.connect(self.accept)

        btn_box = QtWidgets.QDialogButtonBox()
        btn_box.addButton(self.btn_reset_inputs, QtWidgets.QDialogButtonBox.ButtonRole.ResetRole)
        btn_box.addButton(self.btn_reset_data, QtWidgets.QDialogButtonBox.ButtonRole.ResetRole)
        btn_box.addButton(self.btn_done, QtWidgets.QDialogButtonBox.ButtonRole.AcceptRole)

        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)

        self._layout.addWidget(btn_box)

        self.setLayout(self._layout)

    def _setup_pipeline_section(self) -> None:
        grp_box_pipeline = QtWidgets.QGroupBox("Filter using a pre-defined pipeline")
        grp_box_pipeline_layout = QtWidgets.QFormLayout()
        # grp_box_pipeline_layout.setRowWrapPolicy(QtWidgets.QFormLayout.RowWrapPolicy.WrapAllRows)

        combo_pipeline = superqt.QEnumComboBox(enum_class=PreprocessPipeline)
        self.combo_pipeline = combo_pipeline

        self.btn_run_pipeline = QtWidgets.QPushButton("Run")
        self.btn_run_pipeline.clicked.connect(self._emit_pipeline_run)

        grp_box_pipeline_layout.addRow("Pipeline", combo_pipeline)
        grp_box_pipeline_layout.addRow(self.btn_run_pipeline)

        grp_box_pipeline.setLayout(grp_box_pipeline_layout)

        self.grp_box_pipeline = grp_box_pipeline
        self._layout.addWidget(self.grp_box_pipeline)

    @QtCore.Slot()
    def _emit_pipeline_run(self) -> None:
        pipeline = PreprocessPipeline(self.combo_pipeline.currentEnum())
        self.sig_pipeline_run.emit(pipeline)

    def _setup_custom_filter_section(self) -> None:
        settings = QtCore.QSettings()
        sampling_rate: int = settings.value("Data/sampling_rate")  # type: ignore
        grp_box_custom = QtWidgets.QGroupBox("Define a custom filter")
        grp_box_custom_layout = QtWidgets.QFormLayout()
        grp_box_custom_layout.setRowWrapPolicy(QtWidgets.QFormLayout.RowWrapPolicy.WrapAllRows)

        combo_filter_method = superqt.QEnumComboBox(enum_class=FilterMethod)
        combo_filter_method.setCurrentEnum(FilterMethod.Butterworth)
        self.combo_filter_method = combo_filter_method
        self.combo_filter_method.currentEnumChanged.connect(self._set_filter_widget_states)

        combo_filter_type = superqt.QEnumComboBox(enum_class=FilterType)
        combo_filter_type.setCurrentEnum(FilterType.LowPass)
        self.combo_filter_type = combo_filter_type
        self.combo_filter_type.currentEnumChanged.connect(self._set_frequency_slider_states)

        slider_order = superqt.QLabeledSlider(QtCore.Qt.Orientation.Horizontal)
        slider_order.setTickPosition(QtWidgets.QSlider.TickPosition.TicksBelow)
        slider_order.setTickInterval(1)
        slider_order.setEdgeLabelMode(superqt.QLabeledSlider.EdgeLabelMode.LabelIsValue)
        slider_order.setRange(1, 10)
        slider_order.setValue(3)
        self.slider_order = slider_order

        freq_range = (0, sampling_rate // 2)
        dbl_slider_lowcut = superqt.QLabeledDoubleSlider(QtCore.Qt.Orientation.Horizontal)
        dbl_slider_lowcut.setEdgeLabelMode(superqt.QLabeledDoubleSlider.EdgeLabelMode.LabelIsValue)
        dbl_slider_lowcut.setDecimals(1)
        dbl_slider_lowcut.setRange(*freq_range)
        dbl_slider_lowcut.setValue(1)
        self.dbl_slider_lowcut = dbl_slider_lowcut

        dbl_slider_highcut = superqt.QLabeledDoubleSlider(QtCore.Qt.Orientation.Horizontal)
        dbl_slider_highcut.setEdgeLabelMode(superqt.QLabeledDoubleSlider.EdgeLabelMode.LabelIsValue)
        dbl_slider_highcut.setDecimals(1)
        dbl_slider_highcut.setRange(*freq_range)
        dbl_slider_highcut.setValue(8)
        self.dbl_slider_highcut = dbl_slider_highcut

        slider_window_size_filter = superqt.QLabeledSlider(QtCore.Qt.Orientation.Horizontal)
        slider_window_size_filter.setEdgeLabelMode(
            superqt.QLabeledSlider.EdgeLabelMode.LabelIsValue
        )
        slider_window_size_filter.setRange(5, 5_000)
        slider_window_size_filter.setValue(500)
        self.slider_window_size_filter = slider_window_size_filter

        combo_powerline = QtWidgets.QComboBox()
        combo_powerline.addItem("50 Hz")
        combo_powerline.addItem("60 Hz")
        combo_powerline.setCurrentIndex(0)
        combo_powerline.setItemData(0, 50, QtCore.Qt.ItemDataRole.UserRole)
        combo_powerline.setItemData(1, 60, QtCore.Qt.ItemDataRole.UserRole)
        self.combo_powerline = combo_powerline

        self.btn_apply_filter = QtWidgets.QPushButton("Apply Filter")
        self.btn_apply_filter.clicked.connect(self._emit_filter_applied)

        grp_box_custom_layout.addRow("Filter Method", combo_filter_method)
        grp_box_custom_layout.addRow("Filter Type", combo_filter_type)
        grp_box_custom_layout.addRow("Highcut Frequency", dbl_slider_highcut)
        grp_box_custom_layout.addRow("Lowcut Frequency", dbl_slider_lowcut)
        grp_box_custom_layout.addRow("Filter Order", slider_order)
        grp_box_custom_layout.addRow("Window Size", slider_window_size_filter)
        grp_box_custom_layout.addRow("Powerline Frequency", combo_powerline)
        grp_box_custom_layout.addRow(self.btn_apply_filter)

        grp_box_custom.setLayout(grp_box_custom_layout)
        self.grp_box_custom = grp_box_custom
        self._layout.addWidget(self.grp_box_custom)

    @QtCore.Slot()
    def _restore_defaults(self) -> None:
        self.combo_pipeline.setCurrentEnum(PreprocessPipeline.Custom)
        self.combo_filter_method.setCurrentEnum(FilterMethod.Butterworth)
        self.combo_filter_type.setCurrentEnum(FilterType.LowPass)
        self.dbl_slider_lowcut.setValue(1)
        self.dbl_slider_highcut.setValue(8)
        self.slider_order.setValue(3)
        self.slider_window_size_filter.setValue(500)
        self.combo_powerline.setCurrentIndex(0)
        self.combo_standardization.setCurrentEnum(StandardizationMethod.ZScore)
        self.checkbox_rolling.setChecked(False)
        self.slider_window_size_standardize.setValue(300)

    @QtCore.Slot(object)
    def _set_frequency_slider_states(self, filter_type_enum: FilterType) -> None:
        # Show the appropriate slider based on the filter type
        # Low-pass: Enable highcut slider, disable lowcut slider
        # High-pass: Enable lowcut slider, disable highcut slider
        # Band-pass: Enable both lowcut and highcut sliders
        if not self.combo_filter_type.isEnabled():
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
        if method_enum in [
            FilterMethod.Butterworth,
            FilterMethod.ButterworthLegacy,
            FilterMethod.Bessel,
        ]:
            self.combo_filter_type.setEnabled(True)
            self.dbl_slider_lowcut.setEnabled(True)
            self.dbl_slider_highcut.setEnabled(True)
            self.slider_order.setEnabled(True)
            self.slider_window_size_standardize.setEnabled(False)
            self.combo_powerline.setEnabled(False)
        elif method_enum == FilterMethod.SavGol:
            self.combo_filter_type.setEnabled(False)
            self.dbl_slider_lowcut.setEnabled(False)
            self.dbl_slider_highcut.setEnabled(False)
            self.slider_order.setEnabled(True)
            self.slider_window_size_standardize.setEnabled(True)
            self.combo_powerline.setEnabled(False)
        elif method_enum == FilterMethod.FIR:
            self.combo_filter_type.setEnabled(True)
            self.dbl_slider_lowcut.setEnabled(True)
            self.dbl_slider_highcut.setEnabled(True)
            self.slider_order.setEnabled(False)
            self.slider_window_size_standardize.setEnabled(True)
            self.combo_powerline.setEnabled(False)
        elif method_enum == FilterMethod.Powerline:
            self.combo_filter_type.setEnabled(False)
            self.dbl_slider_lowcut.setEnabled(False)
            self.dbl_slider_highcut.setEnabled(False)
            self.slider_order.setEnabled(False)
            self.slider_window_size_standardize.setEnabled(False)
            self.combo_powerline.setEnabled(True)
        elif method_enum == FilterMethod.NoFilter:
            self.combo_filter_type.setEnabled(False)
            self.dbl_slider_lowcut.setEnabled(False)
            self.dbl_slider_highcut.setEnabled(False)
            self.slider_order.setEnabled(False)
            self.slider_window_size_standardize.setEnabled(False)
            self.combo_powerline.setEnabled(False)

        self._set_frequency_slider_states(FilterType(self.combo_filter_type.currentEnum()))

    @QtCore.Slot()
    def _emit_filter_applied(self) -> None:
        frequency_cutoff_type: FilterType | None = self.combo_filter_type.currentEnum()
        if frequency_cutoff_type is None:
            return
        lowcut = None
        highcut = None
        if frequency_cutoff_type == FilterType.LowPass:
            highcut = self.dbl_slider_highcut.value()
        elif frequency_cutoff_type == FilterType.HighPass:
            lowcut = self.dbl_slider_lowcut.value()
        elif frequency_cutoff_type == FilterType.BandPass:
            lowcut = self.dbl_slider_lowcut.value()
            highcut = self.dbl_slider_highcut.value()

        method = FilterMethod(self.combo_filter_method.currentEnum())
        powerline = self.combo_powerline.currentData(QtCore.Qt.ItemDataRole.UserRole)

        filter_params: _t.SignalFilterParameters = {
            "lowcut": lowcut,
            "highcut": highcut,
            "method": method,
            "order": self.slider_order.value(),
            "window_size": self.slider_window_size_standardize.value(),
            "powerline": powerline,
        }

        self.sig_filter_applied.emit(filter_params)

    def _setup_standardization_section(self) -> None:
        grp_box_standardization = QtWidgets.QGroupBox("Standardization")
        standardization_layout = QtWidgets.QFormLayout()
        standardization_layout.setRowWrapPolicy(QtWidgets.QFormLayout.RowWrapPolicy.WrapAllRows)

        combo_standardization = superqt.QEnumComboBox(enum_class=StandardizationMethod)
        combo_standardization.setCurrentEnum(StandardizationMethod.ZScore)
        self.combo_standardization = combo_standardization

        checkbox_rolling = QtWidgets.QCheckBox("Use Rolling Window")
        checkbox_rolling.setChecked(False)
        self.checkbox_rolling = checkbox_rolling

        combo_standardization.currentEnumChanged.connect(self._set_rolling_window_checkbox_state)

        slider_window_size_standardize = superqt.QLabeledSlider(QtCore.Qt.Orientation.Horizontal)
        slider_window_size_standardize.setEdgeLabelMode(
            superqt.QLabeledSlider.EdgeLabelMode.LabelIsValue
        )

        slider_window_size_standardize.setRange(3, 3_333)
        slider_window_size_standardize.setValue(300)
        self.slider_window_size_standardize = slider_window_size_standardize

        self.checkbox_rolling.stateChanged.connect(self.slider_window_size_standardize.setEnabled)

        self.btn_apply_standardization = QtWidgets.QPushButton("Apply Standardization")
        self.btn_apply_standardization.clicked.connect(self._emit_standardization_applied)

        standardization_layout.addRow("Method", combo_standardization)
        standardization_layout.addRow(checkbox_rolling)
        standardization_layout.addRow("Window Size", slider_window_size_standardize)
        standardization_layout.addRow(self.btn_apply_standardization)

        grp_box_standardization.setLayout(standardization_layout)
        self.grp_box_standardization = grp_box_standardization
        self._layout.addWidget(self.grp_box_standardization)

    @QtCore.Slot(object)
    def _set_rolling_window_checkbox_state(self, method_enum: StandardizationMethod) -> None:
        if method_enum == StandardizationMethod.ZScore:
            self.checkbox_rolling.setEnabled(True)
            self.slider_window_size_standardize.setEnabled(self.checkbox_rolling.isChecked())
        else:
            self.checkbox_rolling.setChecked(False)
            self.checkbox_rolling.setEnabled(False)
            self.slider_window_size_standardize.setEnabled(False)

    @QtCore.Slot()
    def _emit_standardization_applied(self) -> None:
        method = StandardizationMethod(self.combo_standardization.currentEnum())
        window_size = self.slider_window_size_standardize.value()
        standardization_params: _t.StandardizationParameters = {
            "method": method,
            "window_size": window_size,
        }
        self.sig_standardization_applied.emit(standardization_params)

    @QtCore.Slot()
    def _emit_restore_unfiltered(self) -> None:
        self.sig_restore_unfiltered.emit()
