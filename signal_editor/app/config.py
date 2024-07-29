import functools
import typing as t
from enum import StrEnum

import attrs
import qfluentwidgets as qfw
from PySide6 import QtCore, QtGui, QtWidgets

from .gui.widgets.config_tree import ConfigItemDelegate

from . import type_defs as _t
from .enum_defs import RateComputationMethod
from .utils import get_app_dir, make_qcolor

type _Index = QtCore.QModelIndex | QtCore.QPersistentModelIndex

ItemDataRole = QtCore.Qt.ItemDataRole

@attrs.define
class _PlotConfig:
    Background: QtGui.QColor = attrs.field(
        default="black",
        converter=make_qcolor,
        metadata={"Description": "The background color of the plot."},
    )
    Foreground: QtGui.QColor = attrs.field(
        default="grey",
        converter=make_qcolor,
        metadata={"Description": "The foreground (text, axis, etc) color of the plot."},
    )
    LineColor: QtGui.QColor = attrs.field(
        default="royalblue",
        converter=make_qcolor,
        metadata={"Description": "The color of the lines in the plot."},
    )
    PointColor: QtGui.QColor = attrs.field(
        default="goldenrod",
        converter=make_qcolor,
        metadata={"Description": "The color of the points in the plot."},
    )
    SectionColor: QtGui.QColor = attrs.field(
        default="lime",
        converter=make_qcolor,
        metadata={"Description": "The color of the section markers in the plot."},
    )
    LineClickWidth: int = attrs.field(
        default=70,
        metadata={
            "Description": "The area around the signal line in pixels that is considered to be a click on the line."
        },
    )
    ClickRadius: int = attrs.field(
        default=20,
        metadata={
            "Description": "The radius of the area around the signal line in pixels that is considered to be a click on the line."
        },
    )

    def to_dict(self) -> _t.PlotConfigDict:
        return _t.PlotConfigDict(**attrs.asdict(self))

    @classmethod
    def from_qsettings(cls) -> "_PlotConfig":
        settings = QtCore.QSettings()
        settings.beginGroup("Plot")
        bg = settings.value("Background", make_qcolor("black"), type=QtGui.QColor)
        fg = settings.value("Foreground", make_qcolor("grey"), type=QtGui.QColor)
        lc = settings.value("LineColor", make_qcolor("royalblue"), type=QtGui.QColor)
        pc = settings.value("PointColor", make_qcolor("goldenrod"), type=QtGui.QColor)
        sc = settings.value("SectionColor", make_qcolor("lime"), type=QtGui.QColor)
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

    def save_to_qsettings(self) -> None:
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


@attrs.define
class _EditingConfig:
    FilterStacking: bool = attrs.field(
        default=False,
        metadata={"Description": "Whether to allow applying multiple filters to the same data."},
    )
    RateMethod: RateComputationMethod = attrs.field(
        default=RateComputationMethod.RollingWindow,
        metadata={
            "Description": "Which method to use for computing the rate displayed in the lower plot on the editing page, either 'instantaneous' or 'rolling_window'."
        },
    )

    def to_dict(self) -> _t.EditingConfigDict:
        return _t.EditingConfigDict(**attrs.asdict(self))

    @classmethod
    def from_qsettings(cls) -> "_EditingConfig":
        settings = QtCore.QSettings()
        settings.beginGroup("Editing")
        fs = settings.value("FilterStacking", False, type=bool)
        rm = RateComputationMethod(settings.value("RateMethod", RateComputationMethod.RollingWindow))
        settings.endGroup()

        return cls(
            FilterStacking=fs,  # type: ignore
            RateMethod=rm,
        )

    def save_to_qsettings(self) -> None:
        settings = QtCore.QSettings()
        settings.beginGroup("Editing")
        settings.setValue("FilterStacking", self.FilterStacking)
        settings.setValue("RateMethod", self.RateMethod)
        settings.endGroup()

        settings.sync()


@attrs.define
class _DataConfig:
    FloatPrecision: int = attrs.field(
        default=3,
        metadata={"Description": "The number of decimal places to show in the data table."},
    )

    def to_dict(self) -> _t.DataConfigDict:
        return _t.DataConfigDict(**attrs.asdict(self))

    @classmethod
    def from_qsettings(cls) -> "_DataConfig":
        settings = QtCore.QSettings()
        settings.beginGroup("Data")
        fp = settings.value("FloatPrecision", 3, type=int)
        settings.endGroup()

        return cls(
            FloatPrecision=fp,  # type: ignore
        )

    def save_to_qsettings(self) -> None:
        settings = QtCore.QSettings()
        settings.beginGroup("Data")
        settings.setValue("FloatPrecision", self.FloatPrecision)
        settings.endGroup()

        settings.sync()


@attrs.define
class _InternalConfig:
    InputDir: str = attrs.field(factory=functools.partial(get_app_dir, True), metadata={"allow_user_edits": True})
    OutputDir: str = attrs.field(factory=functools.partial(get_app_dir, True), metadata={"allow_user_edits": True})
    RecentFiles: list[str] = attrs.field(factory=list, metadata={"allow_user_edits": False})
    LastSignalColumn: str = attrs.field(default="", metadata={"allow_user_edits": False})
    LastInfoColumn: str = attrs.field(default="", metadata={"allow_user_edits": False})
    WindowGeometry: QtCore.QByteArray = attrs.field(factory=QtCore.QByteArray, metadata={"allow_user_edits": False})
    WindowState: QtCore.QByteArray = attrs.field(factory=QtCore.QByteArray, metadata={"allow_user_edits": False})

    def to_dict(self) -> _t.InternalConfigDict:
        return _t.InternalConfigDict(**attrs.asdict(self))

    @classmethod
    def from_qsettings(cls) -> "_InternalConfig":
        settings = QtCore.QSettings()
        settings.beginGroup("Internal")
        input_dir = settings.value("InputDir", get_app_dir(True), type=str)
        output_dir = settings.value("OutputDir", get_app_dir(True), type=str)
        recent_files = settings.value("RecentFiles", [], type=list)
        last_signal_column = settings.value("LastSignalColumn", "", type=str)
        last_info_column = settings.value("LastInfoColumn", "", type=str)
        window_geometry = settings.value("WindowGeometry", QtCore.QByteArray(), type=QtCore.QByteArray)
        window_state = settings.value("WindowState", QtCore.QByteArray(), type=QtCore.QByteArray)
        settings.endGroup()

        return cls(
            InputDir=input_dir,  # type: ignore
            OutputDir=output_dir,  # type: ignore
            RecentFiles=recent_files,  # type: ignore
            LastSignalColumn=last_signal_column,  # type: ignore
            LastInfoColumn=last_info_column,  # type: ignore
            WindowGeometry=window_geometry,  # type: ignore
            WindowState=window_state,  # type: ignore
        )

    def save_to_qsettings(self) -> None:
        settings = QtCore.QSettings()
        settings.beginGroup("Internal")
        settings.setValue("InputDir", self.InputDir)
        settings.setValue("OutputDir", self.OutputDir)
        settings.setValue("RecentFiles", self.RecentFiles)
        settings.setValue("LastSignalColumn", self.LastSignalColumn)
        settings.setValue("LastInfoColumn", self.LastInfoColumn)
        settings.setValue("WindowGeometry", self.WindowGeometry)
        settings.setValue("WindowState", self.WindowState)
        settings.endGroup()

        settings.sync()


class Config:
    _instance: "Config | None" = None

    def __new__(cls, use_qsettings: bool = True) -> "Config":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, use_qsettings: bool = True) -> None:
        if use_qsettings:
            self._plot_config = _PlotConfig.from_qsettings()
            self._editing_config = _EditingConfig.from_qsettings()
            self._data_config = _DataConfig.from_qsettings()
            self._internal_config = _InternalConfig.from_qsettings()
        else:
            self._plot_config = _PlotConfig()
            self._editing_config = _EditingConfig()
            self._data_config = _DataConfig()
            self._internal_config = _InternalConfig()

    def __repr__(self) -> str:
        out = self.to_dict()
        return str(out)
        
    @property
    def plot(self) -> _PlotConfig:
        return self._plot_config

    @property
    def editing(self) -> _EditingConfig:
        return self._editing_config

    @property
    def data(self) -> _DataConfig:
        return self._data_config

    @property
    def internal(self) -> _InternalConfig:
        return self._internal_config

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

    def save_to_qsettings(self) -> None:
        self.plot.save_to_qsettings()
        self.editing.save_to_qsettings()
        self.data.save_to_qsettings()
        self.internal.save_to_qsettings()



# class ConfigModel(QtCore.QAbstractItemModel):
#     def __init__(self, config: Config | None = None, parent: QtCore.QObject | None = None) -> None:
#         super().__init__(parent)
        
#         self._config = Config().to_dict()
#         self._headers = ("Setting", "Value", "Description")

#     def columnCount(self, parent: _Index | None = None) -> int:
#         return len(self._headers)

#     def data(self, index: _Index, role: int = ItemDataRole.DisplayRole) -> t.Any:
#         if not index or not index.isValid():
#             return None

#         if role not in [
#             QtCore.Qt.ItemDataRole.DisplayRole,
#             QtCore.Qt.ItemDataRole.UserRole,
#         ]:
#             return None

#         row = index.row()
#         col = index.column()

#         if col != 2:
#             return None


def test_config() -> None:
    import sys
    
    class MW(QtWidgets.QMainWindow):
        def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
            super().__init__(parent)

            self.config = Config()
            self._standard_model = QtGui.QStandardItemModel(self)
            self._tree_view = qfw.TreeView(self)
            # self._tree_view.setItemDelegate(ConfigItemDelegate(self._tree_view))
            self.setCentralWidget(self._tree_view)
            root = self._standard_model.invisibleRootItem()

            # Prepare Plot config rows
            plot_config = self.config.plot
            plot_root = QtGui.QStandardItem("Plot")
            root.appendRow(plot_root)
            for field in attrs.fields(plot_config.__class__):
                name = field.name
                value = getattr(plot_config, name)
                description = field.metadata.get("Description", "")
                row = self.prepare_item_row(name, value, description)
                plot_root.appendRow(row)

            # Prepare Editing config rows
            editing_config = self.config.editing
            editing_root = QtGui.QStandardItem("Editing")
            root.appendRow(editing_root)
            for field in attrs.fields(editing_config.__class__):
                name = field.name
                value = getattr(editing_config, name)
                description = field.metadata.get("Description", "")
                row = self.prepare_item_row(name, value, description)
                editing_root.appendRow(row)

            # Prepare Data config rows
            data_config = self.config.data
            data_root = QtGui.QStandardItem("Data")
            root.appendRow(data_root)
            for field in attrs.fields(data_config.__class__):
                name = field.name
                value = getattr(data_config, name)
                description = field.metadata.get("Description", "")
                row = self.prepare_item_row(name, value, description)
                data_root.appendRow(row)

            self._tree_view.setModel(self._standard_model)
            self._tree_view.expandAll()

        def prepare_item_row(self, name: str, value: t.Any, description: str) -> list[QtGui.QStandardItem]:
            item_name = QtGui.QStandardItem(name)
            item_value = QtGui.QStandardItem(str(value))
            item_description = QtGui.QStandardItem(description)

            return [item_name, item_value, item_description]

    app = QtWidgets.QApplication(sys.argv)
    mw = MW()
    mw.show()
    sys.exit(app.exec())