from functools import partial

import attrs
from PySide6 import QtCore, QtGui

from . import type_defs as _t
from .enum_defs import RateComputationMethod
from .utils import get_app_dir, make_qcolor


@attrs.define
class Config:
    PlotBackground: QtGui.QColor = attrs.field(default="black", converter=make_qcolor, metadata={"Description": "The background color of the interactive plot."})
    PlotForeground: QtGui.QColor = attrs.field(default="grey", converter=make_qcolor, metadata={"Description": "The foreground (text, axis, etc) color of the interactive plot."})
    PlotPointColor: QtGui.QColor = attrs.field(default="darkgoldenrod", converter=make_qcolor, metadata={"Description": "The color of the points in the interactive plot."})
    PlotSectionColor: QtGui.QColor = attrs.field(default="tomato", converter=make_qcolor, metadata={"Description": "The color of the section markers in the interactive plot."})
    PlotLineClickWidth: int = attrs.field(default=70, metadata={"Description": "The area around the signal line in pixels that is considered to be a click on the line."})
    PlotClickRadius: int = attrs.field(default=20, metadata={"Description": "The radius around the click in data coordinates to search for a potential peak."})

    EditFilterStacking: bool = attrs.field(default=False, metadata={"Description": "Whether to allow applying multiple filters to the same signal."})
    EditRateComputationMethod: RateComputationMethod = attrs.field(
        default=RateComputationMethod.RollingWindow, metadata={"Description": "Which method to use for computing the rate displayed in the lower plot on the editing page, either 'instantaneous' or 'rolling_window'."}
    )

    DataFloatPrecision: int = attrs.field(default=3, metadata={"Description": "The number of decimal places to show in the data table."})

    DataDir: str = attrs.field(factory=partial(get_app_dir, True))
    OutputDir: str = attrs.field(factory=partial(get_app_dir, True))
    RecentFiles: list[str] = attrs.field(factory=list)
    LastSignalColumn: str = attrs.field(default="")
    LastInfoColumn: str = attrs.field(default="")
    WindowGeometry: QtCore.QByteArray = attrs.field(factory=QtCore.QByteArray)
    WindowState: QtCore.QByteArray = attrs.field(factory=QtCore.QByteArray)

    @classmethod
    def from_settings(cls) -> "Config":
        settings = QtCore.QSettings()
        return cls(
            PlotBackground=settings.value(
                "Plot/Background", make_qcolor("black"), type=QtGui.QColor
            ),
            PlotForeground=settings.value(
                "Plot/Foreground", make_qcolor("grey"), type=QtGui.QColor
            ),
            PlotPointColor=settings.value(
                "Plot/PointColor", make_qcolor("darkgoldenrod"), type=QtGui.QColor
            ),
            PlotSectionColor=settings.value(
                "Plot/SectionColor", make_qcolor("tomato"), type=QtGui.QColor
            ),
            PlotLineClickWidth=settings.value("Plot/LineClickWidth", 70, type=int),
            PlotClickRadius=settings.value("Plot/ClickRadius", 20, type=int),
            EditFilterStacking=settings.value("Editing/FilterStacking", False, type=bool),
            EditRateComputationMethod=RateComputationMethod(
                settings.value("Editing/RateComputationMethod", RateComputationMethod.RollingWindow)
            ),
            DataFloatPrecision=settings.value("Data/FloatPrecision", 3, type=int),
            DataDir=settings.value("Internal/DataDir", get_app_dir(True), type=str),
            OutputDir=settings.value("Internal/OutputDir", get_app_dir(True), type=str),
            RecentFiles=settings.value("Internal/RecentFiles", [], type=list),
            LastSignalColumn=settings.value("Internal/LastSignalColumn", "", type=str),
            LastInfoColumn=settings.value("Internal/LastInfoColumn", "", type=str),
            WindowGeometry=settings.value(
                "Internal/WindowGeometry", QtCore.QByteArray(), type=QtCore.QByteArray
            ),
            WindowState=settings.value(
                "Internal/WindowState", QtCore.QByteArray(), type=QtCore.QByteArray
            ),
        )

    def to_dict(self, include_internal: bool = False) -> _t.ConfigDict:
        plot_settings = _t.PlotConfigDict(
            Background=self.PlotBackground,
            Foreground=self.PlotForeground,
            PointColor=self.PlotPointColor,
            SectionColor=self.PlotSectionColor,
            LineClickWidth=self.PlotLineClickWidth,
            ClickRadius=self.PlotClickRadius,
        )
        edit_settings = _t.EditConfigDict(
            FilterStacking=self.EditFilterStacking,
            RateComputationMethod=self.EditRateComputationMethod,
        )
        data_settings = _t.DataConfigDict(
            FloatPrecision=self.DataFloatPrecision,
        )
        config = _t.ConfigDict(
            Plot=plot_settings,
            Edit=edit_settings,
            Data=data_settings,
        )
        if include_internal:
            internal_settings = _t.InternalConfigDict(
                DataDir=self.DataDir,
                OutputDir=self.OutputDir,
                RecentFiles=self.RecentFiles,
                LastSignalColumn=self.LastSignalColumn,
                LastInfoColumn=self.LastInfoColumn,
                WindowGeometry=self.WindowGeometry,
                WindowState=self.WindowState,
            )
            config["Internal"] = internal_settings
        return config


