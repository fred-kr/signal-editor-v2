import typing as t

import superqt
from loguru import logger
from PySide6 import QtCore, QtGui, QtWidgets

from ... import type_defs as _t
from ...enum_defs import FilterMethod, FilterType, PreprocessPipeline, StandardizationMethod


class ProcessingParametersDialog(QtWidgets.QDialog):
    sig_pipeline_run: t.ClassVar[QtCore.Signal] = QtCore.Signal(object)
    sig_filter_applied: t.ClassVar[QtCore.Signal] = QtCore.Signal(dict)
    sig_standardization_applied: t.ClassVar[QtCore.Signal] = QtCore.Signal(dict)

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setMinimumSize(500, 300)
        self.setMaximumSize(800, 600)
        self.setWindowFlag(QtCore.Qt.WindowType.WindowContextHelpButtonHint, True)
        self.setWindowIcon(QtGui.QIcon(":/icons/app_wave"))
        self.setWindowTitle("Processing Parameters")

        # self.setModal(True)

        scroll_area = QtWidgets.QScrollArea(self)
        self.scroll_area_layout = QtWidgets.QVBoxLayout()
        h1_font = QtGui.QFont("Segoe UI", 14, QtGui.QFont.Weight.Bold)

        main_header = QtWidgets.QLabel("Pre-processing Options")
        main_header.setFont(h1_font)
        self.scroll_area_layout.addWidget(main_header)

        self._setup_pipeline_section()
        self._setup_custom_filter_section()
        self._setup_standardization_section()

        scroll_area.setLayout(self.scroll_area_layout)
        

    def _setup_pipeline_section(self) -> None:
        grp_box_pipeline = QtWidgets.QGroupBox("Use a pre-configured pipeline")
        grp_box_pipeline_layout = QtWidgets.QFormLayout()

        pipeline_combo = superqt.QEnumComboBox(enum_class=PreprocessPipeline)
        self.pipeline_combo = pipeline_combo

        self.btn_run_pipeline = QtWidgets.QPushButton("Run")
        self.btn_run_pipeline.clicked.connect(self._emit_pipeline_run)

        grp_box_pipeline_layout.addRow("Pipeline", pipeline_combo)
        grp_box_pipeline_layout.addRow(self.btn_run_pipeline)

        grp_box_pipeline.setLayout(grp_box_pipeline_layout)

        self.grp_box_pipeline = grp_box_pipeline
        self.scroll_area_layout.addWidget(self.grp_box_pipeline)

    @QtCore.Slot()
    def _emit_pipeline_run(self) -> None:
        pipeline = PreprocessPipeline(self.pipeline_combo.currentEnum())
        logger.debug(f"About to emit pipeline run signal with pipeline: {pipeline}")
        self.sig_pipeline_run.emit(pipeline)

    def _setup_custom_filter_section(self) -> None:
        settings = QtCore.QSettings()
        sampling_rate: int = settings.value("Data/sampling_rate")
        grp_box_custom = QtWidgets.QGroupBox("Use a custom filter")
        grp_box_custom_layout = QtWidgets.QFormLayout()
        grp_box_custom_layout.setRowWrapPolicy(QtWidgets.QFormLayout.RowWrapPolicy.WrapAllRows)

        combo_filter_method = superqt.QEnumComboBox(enum_class=FilterMethod)
        combo_filter_method.setCurrentEnum(FilterMethod.Butterworth)
        self.combo_filter_method = combo_filter_method
        self.combo_filter_method.currentEnumChanged.connect(self._set_filter_widget_states)

        combo_filter_type = superqt.QEnumComboBox(enum_class=FilterType)
        combo_filter_type.setCurrentEnum(FilterType.LowPass)
        self.combo_filter_type = combo_filter_type

        slider_order = superqt.QLabeledSlider(QtCore.Qt.Orientation.Horizontal, grp_box_custom)
        slider_order.setEdgeLabelMode(
            superqt.QLabeledSlider.EdgeLabelMode.LabelIsValue
            | superqt.QLabeledSlider.EdgeLabelMode.LabelIsRange
        )
        slider_order.setRange(1, 10)
        slider_order.setValue(3)
        self.slider_order = slider_order

        dbl_slider_lowcut = superqt.QLabeledDoubleSlider(
            QtCore.Qt.Orientation.Horizontal, grp_box_custom
        )
        dbl_slider_lowcut.setEdgeLabelMode(
            superqt.QLabeledSlider.EdgeLabelMode.LabelIsValue
            | superqt.QLabeledSlider.EdgeLabelMode.LabelIsRange
        )
        dbl_slider_lowcut.setDecimals(1)
        dbl_slider_lowcut.setRange(0, sampling_rate / 2)
        dbl_slider_lowcut.setValue(0.5)
        self.dbl_slider_lowcut = dbl_slider_lowcut

        dbl_slider_highcut = superqt.QLabeledDoubleSlider(
            QtCore.Qt.Orientation.Horizontal, grp_box_custom
        )
        dbl_slider_highcut.setEdgeLabelMode(
            superqt.QLabeledSlider.EdgeLabelMode.LabelIsValue
            | superqt.QLabeledSlider.EdgeLabelMode.LabelIsRange
        )
        dbl_slider_highcut.setDecimals(1)
        dbl_slider_highcut.setRange(0, sampling_rate / 2)
        dbl_slider_highcut.setValue(8)
        self.dbl_slider_highcut = dbl_slider_highcut

        dbl_range_slider_passband = superqt.QLabeledDoubleRangeSlider(
            QtCore.Qt.Orientation.Horizontal, grp_box_custom
        )
        dbl_range_slider_passband.setEdgeLabelMode(
            superqt.QLabeledSlider.EdgeLabelMode.LabelIsValue
            | superqt.QLabeledSlider.EdgeLabelMode.LabelIsRange
        )
        dbl_range_slider_passband.setDecimals(1)
        dbl_range_slider_passband.setRange(0, sampling_rate / 2)
        dbl_range_slider_passband.setValue((0.5, 8.0))
        self.dbl_range_slider_passband = dbl_range_slider_passband

        # dbl_range_slider_stopband = superqt.QLabeledDoubleRangeSlider(QtCore.Qt.Orientation.Horizontal)
        # dbl_range_slider_stopband.setDecimals(1)
        # dbl_range_slider_stopband.setRange(0, sampling_rate // 2)
        # dbl_range_slider_stopband.setValue((8.0, 12.0))
        # self.dbl_range_slider_stopband = dbl_range_slider_stopband

        stacked_widget_sliders = QtWidgets.QStackedWidget(grp_box_custom)
        stacked_widget_sliders.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred
        )
        stacked_widget_sliders.addWidget(dbl_slider_lowcut)
        stacked_widget_sliders.addWidget(dbl_slider_highcut)
        stacked_widget_sliders.addWidget(dbl_range_slider_passband)
        # stacked_widget_sliders.addWidget(dbl_range_slider_stopband)
        self.stacked_widget_sliders = stacked_widget_sliders

        self.combo_filter_type.currentIndexChanged.connect(
            self.stacked_widget_sliders.setCurrentIndex
        )

        slider_window_size = superqt.QLabeledSlider(
            QtCore.Qt.Orientation.Horizontal, grp_box_custom
        )
        slider_window_size.setRange(5, 5_000)
        slider_window_size.setValue(500)
        self.slider_window_size = slider_window_size

        slider_powerline = superqt.QLabeledSlider(QtCore.Qt.Orientation.Horizontal, grp_box_custom)
        slider_powerline.setRange(50, 60)
        slider_powerline.setValue(50)
        self.slider_powerline = slider_powerline

        self.btn_apply_filter = QtWidgets.QPushButton("Apply Filter")
        self.btn_apply_filter.clicked.connect(self._emit_filter_applied)

        grp_box_custom_layout.addRow("Filter Method", combo_filter_method)
        grp_box_custom_layout.addRow("Filter Type", combo_filter_type)
        grp_box_custom_layout.addRow("Filter Cutoffs", stacked_widget_sliders)
        grp_box_custom_layout.addRow("Filter Order", slider_order)
        grp_box_custom_layout.addRow("Window Size", slider_window_size)
        grp_box_custom_layout.addRow("Powerline Frequency", slider_powerline)
        grp_box_custom_layout.addRow(self.btn_apply_filter)

        grp_box_custom.setLayout(grp_box_custom_layout)
        self.grp_box_custom = grp_box_custom
        self.scroll_area_layout.addWidget(self.grp_box_custom)

    @QtCore.Slot(object)
    def _set_filter_widget_states(self, method_enum: FilterMethod) -> None:
        match method_enum:
            case FilterMethod.Butterworth | FilterMethod.ButterworthLegacy | FilterMethod.Bessel:
                self.combo_filter_type.setVisible(True)
                self.stacked_widget_sliders.setVisible(True)
                self.slider_order.setVisible(True)
                self.slider_window_size.setVisible(False)
                self.slider_powerline.setVisible(False)
            case FilterMethod.SavGol:
                self.combo_filter_type.setVisible(False)
                self.stacked_widget_sliders.setVisible(False)
                self.slider_order.setVisible(True)
                self.slider_window_size.setVisible(True)
                self.slider_powerline.setVisible(False)
            case FilterMethod.FIR:
                self.combo_filter_type.setVisible(True)
                self.stacked_widget_sliders.setVisible(True)
                self.slider_order.setVisible(False)
                self.slider_window_size.setVisible(True)
                self.slider_powerline.setVisible(False)
            case FilterMethod.Powerline:
                self.combo_filter_type.setVisible(False)
                self.stacked_widget_sliders.setVisible(False)
                self.slider_order.setVisible(False)
                self.slider_window_size.setVisible(False)
                self.slider_powerline.setVisible(True)
            case FilterMethod.NoFilter:
                self.combo_filter_type.setVisible(False)
                self.stacked_widget_sliders.setVisible(False)
                self.slider_order.setVisible(False)
                self.slider_window_size.setVisible(False)
                self.slider_powerline.setVisible(False)

    @QtCore.Slot()
    def _emit_filter_applied(self) -> None:
        frequency_cutoff_type: FilterType | None = self.combo_filter_type.currentEnum()
        if frequency_cutoff_type is None:
            return
        lowcut = None
        highcut = None
        match frequency_cutoff_type:
            case FilterType.LowPass:
                highcut = self.dbl_slider_lowcut.value()
            case FilterType.HighPass:
                lowcut = self.dbl_slider_highcut.value()
            case FilterType.BandPass:
                lowcut, highcut = self.dbl_range_slider_passband.value()

        method = FilterMethod(self.combo_filter_method.currentEnum())

        filter_params: _t.SignalFilterParameters = {
            "lowcut": lowcut,
            "highcut": highcut,
            "method": method,
            "order": self.slider_order.value(),
            "window_size": self.slider_window_size.value(),
            "powerline": self.slider_powerline.value(),
        }

        logger.debug(f"About to emit filter applied signal with params: \n{filter_params}")
        self.sig_filter_applied.emit(filter_params)

    def _setup_standardization_section(self) -> None:
        grp_box_standardization = QtWidgets.QGroupBox("Standardization")
        grp_box_standardization_layout = QtWidgets.QHBoxLayout()

        combo_standardization = superqt.QEnumComboBox(enum_class=StandardizationMethod)
        combo_standardization.setCurrentEnum(StandardizationMethod.ZScore)
        self.combo_standardization = combo_standardization

        slider_window_size = superqt.QLabeledSlider(QtCore.Qt.Orientation.Horizontal)
        slider_window_size.setRange(5, 5_000)
        slider_window_size.setValue(300)
        self.slider_window_size = slider_window_size

        self.btn_apply_standardization = QtWidgets.QPushButton("Apply Standardization")
        self.btn_apply_standardization.clicked.connect(self._emit_standardization_applied)

        grp_box_standardization_layout.addWidget(combo_standardization)
        grp_box_standardization_layout.addWidget(slider_window_size)
        grp_box_standardization_layout.addWidget(self.btn_apply_standardization)

        grp_box_standardization.setLayout(grp_box_standardization_layout)
        self.grp_box_standardization = grp_box_standardization
        self.scroll_area_layout.addWidget(self.grp_box_standardization)

    @QtCore.Slot()
    def _emit_standardization_applied(self) -> None:
        method = StandardizationMethod(self.combo_standardization.currentEnum())
        window_size = self.slider_window_size.value()
        standardization_params: _t.StandardizationParameters = {
            "method": method,
            "window_size": window_size,
        }
        logger.debug(
            f"About to emit standardization applied signal with params: \n{standardization_params}"
        )
        self.sig_standardization_applied.emit(standardization_params)
