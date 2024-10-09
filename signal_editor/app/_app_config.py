import functools
import typing as t

import attrs
import qfluentwidgets as qfw
from PySide6 import QtCore, QtGui, QtWidgets
from pyside_config import ConfigBase, EditorWidgetInfo, config
from pyside_config.properties import ComboBoxProperties, SpinBoxProperties
from pyside_config.widgets import EnumComboBox

from ._enums import RateComputationMethod, TextFileSeparator
from .utils import app_dir_posix, search_enum

app_dir = app_dir_posix()


@config
class PlotConfig(ConfigBase):
    background_color: QtGui.QColor = attrs.field(
        default=QtGui.QColor("#000000"),
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


STYLE_SHEET_ENUM_COMBO_BOX = """
QComboBox {
    min-width: 150px;
    min-height: 31px;
    border-radius: 5px;
    padding: 5px 31px 6px 11px;
    color: rgba(0, 0, 0, 0.6063);
    background-color: rgba(255, 255, 255, 0.7);
    text-align: left;
    outline: none;
}
QComboBox:hover {
    background-color: rgba(249, 249, 249, 0.5);
}
QComboBox:pressed {
    background-color: rgba(249, 249, 249, 0.3);
    color: rgba(0, 0, 0, 0.63);
}
QComboBox:disabled {
    color: rgba(0, 0, 0, 0.36);
    background: rgba(249, 249, 249, 0.3);
    border: 1px solid rgba(0, 0, 0, 0.06);
}
QComboBox QAbstractItemView::item {
    min-height: 31px;
}
"""


@config
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


@config
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


@config
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


class Config:
    __slots__ = ("_plot", "_editing", "_data", "_internal")

    _instance: "Config | None" = None
    _groups = frozenset({"plot", "editing", "data", "internal"})

    def __new__(cls) -> "Config":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        self._plot = PlotConfig.from_qsettings()
        self._editing = EditingConfig.from_qsettings()
        self._data = DataConfig.from_qsettings()
        self._internal = InternalConfig.from_qsettings()

    @property
    def plot(self) -> PlotConfig:
        return self._plot

    @property
    def editing(self) -> EditingConfig:
        return self._editing

    @property
    def data(self) -> DataConfig:
        return self._data

    @property
    def internal(self) -> InternalConfig:
        return self._internal

    def update_value(self, group: str | None, key: str, value: t.Any) -> None:
        if group is None:
            return
        group = group.lower()
        if group not in self._groups:
            return
        if group == "plot":
            if hasattr(self._plot, key):
                setattr(self._plot, key, value)
        elif group == "editing":
            if hasattr(self._editing, key):
                setattr(self._editing, key, value)
        elif group == "data":
            if hasattr(self._data, key):
                setattr(self._data, key, value)
        elif group == "internal":
            if hasattr(self._internal, key):
                setattr(self._internal, key, value)

        self.save()

    def save(self) -> None:
        for group in self._groups:
            config: ConfigBase = getattr(self, group)
            config.to_qsettings()

    def reset(self, *, include_internal: bool = False) -> None:
        for group in self._groups:
            if not include_internal and group == "internal":
                continue
            config: ConfigBase = getattr(self, group)
            config.restore_defaults()

    def create_editor_widgets(
        self, parent: QtWidgets.QWidget | None = None, show_internal: bool = False
    ) -> QtWidgets.QDialog:
        dlg = QtWidgets.QDialog(parent)
        dlg.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose)
        dlg.setModal(True)
        dlg.setWindowTitle("Settings")

        btn_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Save | QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        btn_box.accepted.connect(dlg.accept)
        btn_box.rejected.connect(dlg.reject)

        tab_widget = QtWidgets.QTabWidget()
        tab_widget.addTab(self.plot.create_editor(), "Plot")
        tab_widget.addTab(self.editing.create_editor(), "Editing")
        tab_widget.addTab(self.data.create_editor(), "Data")

        if show_internal:
            tab_widget.addTab(self.internal.create_editor(), "Internal")

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(tab_widget)
        layout.addWidget(btn_box)
        dlg.setLayout(layout)
        dlg.resize(800, 600)

        return dlg

    def create_snapshot(self) -> dict[str, t.Any]:
        """
        Create a snapshot of the current config values.
        """
        return {
            "plot": attrs.asdict(self.plot),
            "editing": attrs.asdict(self.editing),
            "data": attrs.asdict(self.data),
            "internal": attrs.asdict(self.internal),
        }

    def restore_snapshot(self, snapshot: dict[str, t.Any]) -> None:
        for grp, grp_dict in snapshot.items():
            for key, value in grp_dict.items():
                self.update_value(grp, key, value)
