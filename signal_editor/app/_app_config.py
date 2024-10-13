import functools
import typing as t

import attrs
import qfluentwidgets as qfw
from PySide6 import QtCore, QtGui
from pyside_config import ComboBoxProperties, ConfigBase, EditorWidgetInfo, SpinBoxProperties, config, define_config
from pyside_widgets.enum_combo_box import EnumComboBox

from ._enums import RateComputationMethod, TextFileSeparator
from .utils import app_dir_posix, make_qcolor, search_enum

app_dir = app_dir_posix()


@define_config
class PlotConfig(ConfigBase):
    background_color: QtGui.QColor = attrs.field(
        default=QtGui.QColor("#000000"),
        converter=make_qcolor,
        metadata={
            "editor": EditorWidgetInfo(
                label="Background Color",
                widget_factory=functools.partial(qfw.ColorPickerButton, color=QtGui.QColor("#000000"), title=""),
                sig_value_changed="colorChanged",
                set_value_method="setColor",
            ),
            "description": "Plot background color.",
        },
    )
    foreground_color: QtGui.QColor = attrs.field(
        default=QtGui.QColor("#969696"),
        converter=make_qcolor,
        metadata={
            "editor": EditorWidgetInfo(
                label="Foreground Color",
                widget_factory=functools.partial(qfw.ColorPickerButton, color=QtGui.QColor("#969696"), title=""),
                sig_value_changed="colorChanged",
                set_value_method="setColor",
            ),
            "description": "Plot foreground color.",
        },
    )
    line_click_width: int = attrs.field(
        default=70,
        converter=int,
        metadata={
            "editor": EditorWidgetInfo(
                label="Line click width",
                widget_factory=qfw.SpinBox,
                sig_value_changed="valueChanged",
                set_value_method="setValue",
                widget_properties=SpinBoxProperties(
                    minimum=0,
                    maximum=10_000,
                    singleStep=10,
                    suffix=" px",
                    hasFrame=False,
                ),
            ),
            "description": "Area in pixels around the line in which a click will be counted as a click on the line.",
        },
    )
    click_radius: int = attrs.field(
        default=20,
        converter=int,
        metadata={
            "editor": EditorWidgetInfo(
                label="Click radius",
                widget_factory=qfw.SpinBox,
                sig_value_changed="valueChanged",
                set_value_method="setValue",
                widget_properties=SpinBoxProperties(
                    minimum=0,
                    maximum=1_000,
                    singleStep=1,
                    hasFrame=False,
                    suffix=" samples",
                ),
            ),
            "description": "Area in pixels around a click on the line that will be considered a click on the line.",
        },
    )


config.update_name("PlotConfig", "plot")
plot: PlotConfig = config.get("plot")
del PlotConfig


STYLE_SHEET_ENUM_COMBO_BOX = """
EnumComboBox {
    border-radius: 5px;
    padding: 5px 31px 6px 11px;
    color: rgba(0, 0, 0, 0.6063);
    background-color: rgba(255, 255, 255, 0.7);
    text-align: left;
    outline: none;
}
EnumComboBox:hover {
    background-color: rgba(249, 249, 249, 0.5);
}
EnumComboBox:pressed {
    background-color: rgba(249, 249, 249, 0.3);
    color: rgba(0, 0, 0, 0.63);
}
EnumComboBox:disabled {
    color: rgba(0, 0, 0, 0.36);
    background: rgba(249, 249, 249, 0.3);
    border: 1px solid rgba(0, 0, 0, 0.06);
}
EnumComboBox QAbstractItemView::item {
    min-height: 31px;
}
"""


@define_config
class EditingConfig(ConfigBase):
    filter_stacking: bool = attrs.field(
        default=False,
        converter=attrs.converters.to_bool,
        metadata={
            "editor": EditorWidgetInfo(
                label="Filter stacking",
                widget_factory=qfw.SwitchButton,
                sig_value_changed="checkedChanged",
                set_value_method="setChecked",
            ),
            "description": "Whether to allow applying multiple filters to the same data.",
        },
    )
    rate_computation_method: RateComputationMethod = attrs.field(
        default=RateComputationMethod.RollingWindow,
        converter=functools.partial(search_enum, enum_class=RateComputationMethod),
        metadata={
            "editor": EditorWidgetInfo(
                label="Rate computation method",
                widget_factory=functools.partial(EnumComboBox[RateComputationMethod], enum_class=RateComputationMethod),
                sig_value_changed="sig_current_enum_changed",
                set_value_method="set_current_enum",
                widget_properties=ComboBoxProperties(
                    styleSheet=STYLE_SHEET_ENUM_COMBO_BOX,
                    hasFrame=False,
                ),
            ),
            "description": "How to compute the signal rate from the detected peaks.",
        },
    )


config.update_name("EditingConfig", "editing")
editing: EditingConfig = config.get("editing")
del EditingConfig


@define_config
class DataConfig(ConfigBase):
    float_precision: int = attrs.field(
        default=3,
        converter=int,
        metadata={
            "editor": EditorWidgetInfo(
                label="Float precision",
                widget_factory=qfw.SpinBox,
                sig_value_changed="valueChanged",
                set_value_method="setValue",
                widget_properties=SpinBoxProperties(
                    minimum=0,
                    maximum=10,
                    singleStep=1,
                    hasFrame=False,
                ),
            ),
            "description": "Amount of decimal places to display when displaying data in tables.",
        },
    )
    text_file_separator: TextFileSeparator = attrs.field(
        default=TextFileSeparator.Tab,
        converter=functools.partial(search_enum, enum_class=TextFileSeparator),
        metadata={
            "editor": EditorWidgetInfo(
                label="Text file separator",
                widget_factory=functools.partial(EnumComboBox[TextFileSeparator], enum_class=TextFileSeparator),
                sig_value_changed="sig_current_enum_changed",
                set_value_method="set_current_enum",
                widget_properties=ComboBoxProperties(
                    styleSheet=STYLE_SHEET_ENUM_COMBO_BOX,
                    hasFrame=False,
                ),
            ),
            "description": "Character used to separate fields when reading from a text (.txt) file.",
        },
    )


config.update_name("DataConfig", "data")
data: DataConfig = config.get("data")
del DataConfig


@define_config
class InternalConfig(ConfigBase):
    last_input_dir: str = attrs.field(
        default=app_dir,
        metadata={
            "editor": None,
            "description": "The directory from which the last file was loaded.",
        },
    )
    last_output_dir: str = attrs.field(
        default=app_dir,
        metadata={
            "editor": None,
            "description": "The directory to which the last file was saved.",
        },
    )
    last_sampling_rate: int = attrs.field(
        default=0,
        converter=int,
        metadata={
            "editor": None,
            "description": "The sampling rate from which the last file was loaded.",
        },
    )
    recent_files: list[str] = attrs.field(
        factory=list,
        metadata={
            "editor": None,
            "description": "List of recently opened files.",
        },
    )
    last_signal_column: str = attrs.field(
        default="",
        metadata={
            "editor": None,
            "description": "The name of the signal column in the last file.",
        },
    )
    last_info_column: str = attrs.field(
        default="",
        metadata={
            "editor": None,
            "description": "The name of the info column in the last file.",
        },
    )
    window_geometry: QtCore.QByteArray = attrs.field(
        factory=QtCore.QByteArray,
        metadata={
            "editor": None,
            "description": "Geometry of the main window.",
        },
    )
    window_state: QtCore.QByteArray = attrs.field(
        factory=QtCore.QByteArray,
        metadata={
            "editor": None,
            "description": "State of the main window.",
        },
    )


config.update_name("InternalConfig", "internal")
internal: InternalConfig = config.get("internal")
del InternalConfig


class Config(t.NamedTuple):
    plot = plot
    editing = editing
    data = data
    internal = internal
