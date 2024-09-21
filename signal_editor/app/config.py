import functools
import typing as t

import attrs
import qfluentwidgets as qfw
from PySide6 import QtCore, QtGui
from pyside_config import ConfigBase
from pyside_config.properties import EditorWidgetInfo, SpinBoxProperties
from pyside_config.utils import sync
from pyside_config.widgets import EnumComboBox

from . import type_defs as _t
from .enum_defs import RateComputationMethod, SVGColors, TextFileSeparator
from .utils import app_dir_posix, make_qcolor, search_enum

type _Index = QtCore.QModelIndex | QtCore.QPersistentModelIndex

ItemDataRole = QtCore.Qt.ItemDataRole

app_dir = app_dir_posix()


@attrs.define(on_setattr=sync)
class PlotConfig(ConfigBase):
    background_color: QtGui.QColor = attrs.field(
        default=SVGColors.Black.qcolor(),
        metadata={
            "editor": EditorWidgetInfo(
                label="Background color",
                widget_factory=functools.partial(qfw.ColorPickerButton, color=SVGColors.Black.qcolor(), title=""),
                change_signal_name="colorChanged",
                set_value_name="setColor",
            ),
            "description": "The background color of the plot.",
        },
    )
    foreground_color: QtGui.QColor = attrs.field(
        default=SVGColors.Grey.qcolor(),
        metadata={
            "editor": EditorWidgetInfo(
                label="Foreground color",
                widget_factory=functools.partial(qfw.ColorPickerButton, color=SVGColors.Grey.qcolor(), title=""),
                change_signal_name="colorChanged",
                set_value_name="setColor",
            ),
            "description": "The foreground color of the plot.",
        },
    )
    line_click_width: int = attrs.field(
        default=70,
        converter=int,
        metadata={
            "editor": EditorWidgetInfo(
                label="Line click width",
                widget_factory=qfw.SpinBox,
                change_signal_name="valueChanged",
                set_value_name="setValue",
                widget_properties=SpinBoxProperties(
                    minimum=0,
                    maximum=10_000,
                    singleStep=10,
                    frame=False,
                    suffix=" px",
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
                change_signal_name="valueChanged",
                set_value_name="setValue",
                widget_properties=SpinBoxProperties(
                    minimum=0,
                    maximum=1_000,
                    singleStep=1,
                    frame=False,
                    suffix=" samples",
                ),
            ),
            "description": "Area in pixels around a click on the line that will be considered a click on the line.",
        },
    )


@attrs.define(on_setattr=sync)
class EditingConfig(ConfigBase):
    filter_stacking: bool = attrs.field(
        default=False,
        converter=attrs.converters.to_bool,
        metadata={
            "editor": EditorWidgetInfo(
                label="Filter stacking",
                widget_factory=qfw.SwitchButton,
                change_signal_name="checkedChanged",
                set_value_name="setChecked",
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
                change_signal_name="sig_current_enum_changed",
                set_value_name="set_current_enum",
            ),
            "description": "How to compute the signal rate from the detected peaks.",
        },
    )


@attrs.define(on_setattr=sync)
class DataConfig(ConfigBase):
    float_precision: int = attrs.field(
        default=3,
        converter=int,
        metadata={
            "editor": EditorWidgetInfo(
                label="Float precision",
                widget_factory=qfw.SpinBox,
                change_signal_name="valueChanged",
                set_value_name="setValue",
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
                change_signal_name="sig_current_enum_changed",
                set_value_name="set_current_enum",
            ),
            "description": "Character used to separate fields when reading from a text (.txt) file.",
        },
    )


@attrs.define(on_setattr=sync)
class InternalConfig(ConfigBase):
    last_input_dir: str = attrs.field(
        default=app_dir,
        metadata={
            "editor": EditorWidgetInfo(
                label="Last input directory",
                widget_factory=qfw.LineEdit,
                change_signal_name="textEdited",
                set_value_name="setText",
            ),
            "description": "The directory from which the last file was loaded.",
        },
    )
    last_output_dir: str = attrs.field(
        default=app_dir,
        metadata={
            "editor": EditorWidgetInfo(
                label="Last output directory",
                widget_factory=qfw.LineEdit,
                change_signal_name="textEdited",
                set_value_name="setText",
            ),
            "description": "The directory to which the last file was saved.",
        },
    )
    last_sampling_rate: int = attrs.field(
        default=0,
        converter=int,
        metadata={
            "editor": EditorWidgetInfo(
                label="Last sampling rate",
                widget_factory=qfw.SpinBox,
                change_signal_name="valueChanged",
                set_value_name="setValue",
            ),
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


# def sync[T](inst: attrs.AttrsInstance, attr: t.Any, value: T) -> T:
#     path = attr.metadata.get("path", None)
#     settings = QtCore.QSettings()
#     if path and path in settings.allKeys():
#         settings.setValue(path, value)
#         settings.sync()
#     return value


@attrs.define(on_setattr=sync)
class _PlotConfig:
    Background: QtGui.QColor = attrs.field(
        default=QtGui.QColor(SVGColors.Black),
        converter=make_qcolor,
        metadata={"path": "Plot/Background", "Description": "The background color of the plot."},
    )
    Foreground: QtGui.QColor = attrs.field(
        default=QtGui.QColor(SVGColors.Grey),
        converter=make_qcolor,
        metadata={"path": "Plot/Foreground", "Description": "The foreground (text, axis, etc) color of the plot."},
    )
    LineColor: QtGui.QColor = attrs.field(
        default=QtGui.QColor(SVGColors.RoyalBlue),
        converter=make_qcolor,
        metadata={"path": "Plot/LineColor", "Description": "The color of the lines in the plot."},
    )
    PointColor: QtGui.QColor = attrs.field(
        default=QtGui.QColor(SVGColors.GoldenRod),
        converter=make_qcolor,
        metadata={"path": "Plot/PointColor", "Description": "The color of the points in the plot."},
    )
    SectionColor: QtGui.QColor = attrs.field(
        default=QtGui.QColor(SVGColors.Lime),
        converter=make_qcolor,
        metadata={"path": "Plot/SectionColor", "Description": "The color of the section markers in the plot."},
    )
    LineClickWidth: int = attrs.field(
        default=70,
        metadata={
            "path": "Plot/LineClickWidth",
            "Description": "The area around the signal line in pixels that is considered to be a click on the line.",
        },
    )
    ClickRadius: int = attrs.field(
        default=20,
        metadata={
            "path": "Plot/ClickRadius",
            "Description": "The radius in data points around a click in which to search for a maximum or minimum value.",
        },
    )

    def to_dict(self) -> _t.PlotConfigDict:
        return _t.PlotConfigDict(**attrs.asdict(self))

    @classmethod
    def from_qsettings(cls) -> "_PlotConfig":
        settings = QtCore.QSettings()
        settings.beginGroup("Plot")
        bg = settings.value("Background", make_qcolor(SVGColors.Black), type=QtGui.QColor)
        fg = settings.value("Foreground", make_qcolor(SVGColors.Grey), type=QtGui.QColor)
        lc = settings.value("LineColor", make_qcolor(SVGColors.RoyalBlue), type=QtGui.QColor)
        pc = settings.value("PointColor", make_qcolor(SVGColors.GoldenRod), type=QtGui.QColor)
        sc = settings.value("SectionColor", make_qcolor(SVGColors.Lime), type=QtGui.QColor)
        lcw = settings.value("LineClickWidth", 70, type=int)
        cr = settings.value("ClickRadius", 20, type=int)
        settings.endGroup()

        return cls(
            Background=bg,  # type: ignore
            Foreground=fg,  # type: ignore
            LineColor=lc,  # type: ignore
            PointColor=pc,  # type: ignore
            SectionColor=sc,  # type: ignore
            LineClickWidth=lcw,  # type: ignore
            ClickRadius=cr,  # type: ignore
        )

    def save_all(self) -> None:
        settings = QtCore.QSettings()
        settings.beginGroup("Plot")
        settings.setValue("Background", self.Background)
        settings.setValue("Foreground", self.Foreground)
        settings.setValue("LineColor", self.LineColor)
        settings.setValue("PointColor", self.PointColor)
        settings.setValue("SectionColor", self.SectionColor)
        settings.setValue("LineClickWidth", self.LineClickWidth)
        settings.setValue("ClickRadius", self.ClickRadius)
        settings.endGroup()

        settings.sync()


@attrs.define(on_setattr=sync)
class _EditingConfig:
    FilterStacking: bool = attrs.field(
        default=False,
        metadata={
            "path": "Editing/FilterStacking",
            "Description": "Whether to allow applying multiple filters to the same data.",
        },
    )
    RateMethod: RateComputationMethod = attrs.field(
        default=RateComputationMethod.RollingWindow,
        converter=functools.partial(search_enum, enum_class=RateComputationMethod),
        metadata={
            "path": "Editing/RateMethod",
            "Description": "Which method to use for computing the rate displayed in the lower plot on the editing page, either 'instantaneous' or 'rolling_window'.",
        },
    )

    def to_dict(self) -> _t.EditingConfigDict:
        return _t.EditingConfigDict(**attrs.asdict(self))

    @classmethod
    def from_qsettings(cls) -> "_EditingConfig":
        settings = QtCore.QSettings()
        settings.beginGroup("Editing")
        fs = settings.value("FilterStacking", False, type=bool)
        rm = settings.value("RateMethod", RateComputationMethod.RollingWindow)
        settings.endGroup()

        return cls(
            FilterStacking=fs,  # type: ignore
            RateMethod=rm,
        )

    def save_all(self) -> None:
        settings = QtCore.QSettings()
        settings.beginGroup("Editing")
        settings.setValue("FilterStacking", self.FilterStacking)
        settings.setValue("RateMethod", str(self.RateMethod))
        settings.endGroup()

        settings.sync()


@attrs.define(on_setattr=sync)
class _DataConfig:
    FloatPrecision: int = attrs.field(
        default=3,
        metadata={
            "path": "Data/FloatPrecision",
            "Description": "The number of decimal places to show in the data table.",
        },
    )
    TextSeparatorChar: TextFileSeparator = attrs.field(
        default=TextFileSeparator.Tab,
        converter=functools.partial(search_enum, enum_class=TextFileSeparator),
        metadata={
            "path": "Data/TextSeparatorChar",
            "Description": "Character used to separate fields when reading from a text (.txt) file.",
        },
    )

    def to_dict(self) -> _t.DataConfigDict:
        return _t.DataConfigDict(**attrs.asdict(self))

    @classmethod
    def from_qsettings(cls) -> "_DataConfig":
        settings = QtCore.QSettings()
        settings.beginGroup("Data")
        fp = settings.value("FloatPrecision", 3, type=int)
        tfs = settings.value("TextSeparatorChar", TextFileSeparator.Tab)
        settings.endGroup()

        return cls(
            FloatPrecision=fp,  # type: ignore
            TextSeparatorChar=tfs,
        )

    def save_all(self) -> None:
        settings = QtCore.QSettings()
        settings.beginGroup("Data")
        settings.setValue("FloatPrecision", self.FloatPrecision)
        settings.setValue("TextSeparatorChar", str(self.TextSeparatorChar))
        settings.endGroup()

        settings.sync()


@attrs.define(on_setattr=sync)
class _InternalConfig:
    InputDir: str = attrs.field(factory=app_dir_posix, metadata={"path": "Internal/InputDir", "allow_user_edits": True})
    OutputDir: str = attrs.field(
        factory=app_dir_posix, metadata={"path": "Internal/OutputDir", "allow_user_edits": True}
    )
    LastSamplingRate: int = attrs.field(
        default=0, metadata={"path": "Internal/LastSamplingRate", "allow_user_edits": True}
    )
    RecentFiles: list[str] = attrs.field(
        factory=list, metadata={"path": "Internal/RecentFiles", "allow_user_edits": False}
    )
    LastSignalColumn: str = attrs.field(
        default="", metadata={"path": "Internal/LastSignalColumn", "allow_user_edits": False}
    )
    LastInfoColumn: str = attrs.field(
        default="", metadata={"path": "Internal/LastInfoColumn", "allow_user_edits": False}
    )
    WindowGeometry: QtCore.QByteArray = attrs.field(
        factory=QtCore.QByteArray, metadata={"path": "Internal/WindowGeometry", "allow_user_edits": False}
    )
    WindowState: QtCore.QByteArray = attrs.field(
        factory=QtCore.QByteArray, metadata={"path": "Internal/WindowState", "allow_user_edits": False}
    )

    def to_dict(self) -> _t.InternalConfigDict:
        return _t.InternalConfigDict(**attrs.asdict(self))

    @classmethod
    def from_qsettings(cls) -> "_InternalConfig":
        settings = QtCore.QSettings()
        settings.beginGroup("Internal")
        input_dir = settings.value("InputDir", app_dir_posix(), type=str)
        output_dir = settings.value("OutputDir", app_dir_posix(), type=str)
        last_sampling_rate = settings.value("LastSamplingRate", 0, type=int)
        recent_files = settings.value("RecentFiles", [], type=list)
        last_signal_column = settings.value("LastSignalColumn", "", type=str)
        last_info_column = settings.value("LastInfoColumn", "", type=str)
        window_geometry = settings.value("WindowGeometry", QtCore.QByteArray(), type=QtCore.QByteArray)
        window_state = settings.value("WindowState", QtCore.QByteArray(), type=QtCore.QByteArray)
        settings.endGroup()

        return cls(
            InputDir=input_dir,  # type: ignore
            OutputDir=output_dir,  # type: ignore
            LastSamplingRate=last_sampling_rate,  # type: ignore
            RecentFiles=recent_files,  # type: ignore
            LastSignalColumn=last_signal_column,  # type: ignore
            LastInfoColumn=last_info_column,  # type: ignore
            WindowGeometry=window_geometry,  # type: ignore
            WindowState=window_state,  # type: ignore
        )

    def save_all(self) -> None:
        settings = QtCore.QSettings()
        settings.beginGroup("Internal")
        settings.setValue("InputDir", self.InputDir)
        settings.setValue("OutputDir", self.OutputDir)
        settings.setValue("LastSamplingRate", self.LastSamplingRate)
        settings.setValue("RecentFiles", self.RecentFiles)
        settings.setValue("LastSignalColumn", self.LastSignalColumn)
        settings.setValue("LastInfoColumn", self.LastInfoColumn)
        settings.setValue("WindowGeometry", self.WindowGeometry)
        settings.setValue("WindowState", self.WindowState)
        settings.endGroup()

        settings.sync()


class Config:
    __slots__ = ("_plot_config", "_editing_config", "_data_config", "_internal_config")

    _instance: "Config | None" = None

    def __new__(cls, use_qsettings: bool = True) -> "Config":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, use_qsettings: bool = True) -> None:
        if use_qsettings:
            self._plot_config = PlotConfig.from_qsettings()
            # self._editing_config = _EditingConfig.from_qsettings()
            self._editing_config = EditingConfig.from_qsettings()
            self._data_config = DataConfig.from_qsettings()
            self._internal_config = InternalConfig.from_qsettings()
        else:
            self._plot_config = PlotConfig()
            # self._editing_config = _EditingConfig()
            self._editing_config = EditingConfig()
            self._data_config = DataConfig()
            self._internal_config = InternalConfig()

    def __repr__(self) -> str:
        out = self.to_dict()
        return str(out)

    @property
    def plot(self) -> PlotConfig:
        return self._plot_config

    @property
    def editing(self) -> EditingConfig:
        return self._editing_config

    @property
    def data(self) -> DataConfig:
        return self._data_config

    @property
    def internal(self) -> InternalConfig:
        return self._internal_config

    def update_value(self, group: str | None, key: str, value: t.Any) -> None:
        if group is None:
            return
        group = group.lower()
        if group not in {"plot", "editing", "data", "internal"}:
            raise ValueError(f"Unknown config group: {group}")

        if group == "plot":
            if hasattr(self._plot_config, key):
                setattr(self._plot_config, key, value)
            else:
                raise ValueError(f"Unknown plot config key: {key}")
        elif group == "editing":
            if hasattr(self._editing_config, key):
                setattr(self._editing_config, key, value)
            else:
                raise ValueError(f"Unknown editing config key: {key}")
        elif group == "data":
            if hasattr(self._data_config, key):
                setattr(self._data_config, key, value)
            else:
                raise ValueError(f"Unknown data config key: {key}")
        elif group == "internal":
            if hasattr(self._internal_config, key):
                setattr(self._internal_config, key, value)
            else:
                raise ValueError(f"Unknown internal config key: {key}")

        self.save()

    def to_dict(self) -> _t.ConfigDict:
        plot_dict = self.plot.to_dict()
        editing_dict = self.editing.to_dict()
        data_dict = self.data.to_dict()
        internal_dict = self.internal.to_dict()

        return _t.ConfigDict(
            Plot=plot_dict,
            Editing=editing_dict,
            Data=data_dict,
            Internal=internal_dict,
        )

    def save(self) -> None:
        self.plot.save_all()
        self.editing.to_qsettings()
        self.data.save_all()
        self.internal.save_all()

    def reset(self) -> None:
        self._plot_config = _PlotConfig()
        self._editing_config = EditingConfig()
        self._data_config = _DataConfig()
        self._internal_config = _InternalConfig()
        self.save()
