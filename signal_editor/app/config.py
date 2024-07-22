import functools
import typing as t
from enum import StrEnum

import attrs
import qfluentwidgets as qfw
from PySide6 import QtCore, QtGui, QtWidgets

from . import type_defs as _t
from .enum_defs import RateComputationMethod
from .utils import get_app_dir, make_qcolor

type Index = QtCore.QModelIndex | QtCore.QPersistentModelIndex


@attrs.define
class PlotConfig:
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
    PointColor: QtGui.QColor = attrs.field(
        default="goldenrod",
        converter=make_qcolor,
        metadata={"Description": "The color of the points in the plot."},
    )
    SectionColor: QtGui.QColor = attrs.field(
        default="tomato",
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
    def from_qsettings(cls) -> "PlotConfig":
        settings = QtCore.QSettings()
        settings.beginGroup("Plot")
        bg = settings.value("Background", make_qcolor("black"), type=QtGui.QColor)
        fg = settings.value("Foreground", make_qcolor("grey"), type=QtGui.QColor)
        pc = settings.value("PointColor", make_qcolor("goldenrod"), type=QtGui.QColor)
        sc = settings.value("SectionColor", make_qcolor("tomato"), type=QtGui.QColor)
        lcw = settings.value("LineClickWidth", 70, type=int)
        cr = settings.value("ClickRadius", 20, type=int)
        settings.endGroup()

        return cls(
            Background=bg,  # type: ignore
            Foreground=fg,  # type: ignore
            PointColor=pc,  # type: ignore
            SectionColor=sc,  # type: ignore
            LineClickWidth=lcw,  # type: ignore
            ClickRadius=cr,  # type: ignore
        )


@attrs.define
class EditingConfig:
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
    def from_qsettings(cls) -> "EditingConfig":
        settings = QtCore.QSettings()
        settings.beginGroup("Editing")
        fs = settings.value("FilterStacking", False, type=bool)
        rm = RateComputationMethod(
            settings.value("RateMethod", RateComputationMethod.RollingWindow)
        )
        settings.endGroup()

        return cls(
            FilterStacking=fs,  # type: ignore
            RateMethod=rm,
        )


@attrs.define
class DataConfig:
    FloatPrecision: int = attrs.field(
        default=3,
        metadata={"Description": "The number of decimal places to show in the data table."},
    )

    def to_dict(self) -> _t.DataConfigDict:
        return _t.DataConfigDict(**attrs.asdict(self))

    @classmethod
    def from_qsettings(cls) -> "DataConfig":
        settings = QtCore.QSettings()
        settings.beginGroup("Data")
        fp = settings.value("FloatPrecision", 3, type=int)
        settings.endGroup()

        return cls(
            FloatPrecision=fp,  # type: ignore
        )


@attrs.define
class InternalConfig:
    InputDir: str = attrs.field(
        factory=functools.partial(get_app_dir, True), metadata={"allow_user_edits": True}
    )
    OutputDir: str = attrs.field(
        factory=functools.partial(get_app_dir, True), metadata={"allow_user_edits": True}
    )
    RecentFiles: list[str] = attrs.field(factory=list, metadata={"allow_user_edits": False})
    LastSignalColumn: str = attrs.field(default="", metadata={"allow_user_edits": False})
    LastInfoColumn: str = attrs.field(default="", metadata={"allow_user_edits": False})
    WindowGeometry: QtCore.QByteArray = attrs.field(
        factory=QtCore.QByteArray, metadata={"allow_user_edits": False}
    )
    WindowState: QtCore.QByteArray = attrs.field(
        factory=QtCore.QByteArray, metadata={"allow_user_edits": False}
    )

    def to_dict(self) -> _t.InternalConfigDict:
        return _t.InternalConfigDict(**attrs.asdict(self))

    @classmethod
    def from_qsettings(cls) -> "InternalConfig":
        settings = QtCore.QSettings()
        settings.beginGroup("Internal")
        input_dir = settings.value("InputDir", get_app_dir(True), type=str)
        output_dir = settings.value("OutputDir", get_app_dir(True), type=str)
        recent_files = settings.value("RecentFiles", [], type=list)
        last_signal_column = settings.value("LastSignalColumn", "", type=str)
        last_info_column = settings.value("LastInfoColumn", "", type=str)
        window_geometry = settings.value(
            "WindowGeometry", QtCore.QByteArray(), type=QtCore.QByteArray
        )
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


@attrs.define
class Config:
    Plot: PlotConfig = attrs.field(factory=PlotConfig)
    Editing: EditingConfig = attrs.field(factory=EditingConfig)
    Data: DataConfig = attrs.field(factory=DataConfig)
    Internal: InternalConfig = attrs.field(factory=InternalConfig)

    def to_dict(self) -> _t.ConfigDict:
        return _t.ConfigDict(**attrs.asdict(self))

    @classmethod
    def from_qsettings(cls) -> "Config":
        return cls(
            Plot=PlotConfig.from_qsettings(),
            Editing=EditingConfig.from_qsettings(),
            Data=DataConfig.from_qsettings(),
            Internal=InternalConfig.from_qsettings(),
        )


class TreeItem:
    def __init__(
        self, name: str, value: t.Any | None = None, parent: "TreeItem | None" = None
    ) -> None:
        self.name = name
        self.value = value
        self.parent = parent
        self.children: list[TreeItem] = []
        self.display_widget = self._determine_editor_widget()
        self.set_value(value)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name}, value={self.value}, children={len(self.children)})"

    def __str__(self) -> str:
        return self.name

    def __iter__(self) -> t.Iterator["TreeItem"]:
        yield self
        for child in self.children:
            yield from child

    def __len__(self) -> int:
        return len(self.children)

    def __contains__(self, name: str) -> bool:
        return any(child.name == name for child in self.children)

    def _determine_editor_widget(self) -> QtWidgets.QWidget:
        if isinstance(self.value, bool):
            widget = qfw.CheckBox()
            widget.setChecked(self.value)
        elif isinstance(self.value, int):
            widget = qfw.SpinBox()
            widget.setValue(self.value)
        elif isinstance(self.value, float):
            widget = qfw.DoubleSpinBox()
            widget.setValue(self.value)
        elif isinstance(self.value, str):
            widget = qfw.LineEdit()
            widget.setText(self.value)
        elif isinstance(self.value, (list, tuple, StrEnum)):
            widget = qfw.ComboBox()
            widget.addItems([str(item) for item in self.value])
        else:
            widget = qfw.LineEdit()
            widget.setText(str(self.value))
            widget.setReadOnly(True)
        return widget
            


    def set_value(self, value: t.Any | None) -> None:
        self.value = value
        self.display_widget = self._determine_editor_widget()
    
    def add_child(self, name: str, value: t.Any | None = None) -> None:
        child = TreeItem(name, value, self)
        if child not in self.children:
            self.children.append(child)

    def remove_child(self, name: str) -> None:
        for child in self.children:
            if child.name == name:
                self.children.remove(child)
                break

    def get_child(self, name: str) -> "TreeItem | None":
        return next((child for child in self.children if child.name == name), None)



class ConfigTreeWidget(QtWidgets.QTreeWidget):
    def __init__(
        self, config: Config | None = None, parent: QtWidgets.QWidget | None = None
    ) -> None:
        super().__init__(parent)
        if config is None:
            config = Config()
        self._config = config
        self._headers = ("Name", "Value")
        self._plot_children = [
            QtWidgets.QTreeWidgetItem([pk, str(pv)])
            for pk, pv in self._config.Plot.to_dict().items()
        ]
        self._editing_children = [
            QtWidgets.QTreeWidgetItem([ek, str(ev)])
            for ek, ev in self._config.Editing.to_dict().items()
        ]
        self._data_children = [
            QtWidgets.QTreeWidgetItem([dk, str(dv)])
            for dk, dv in self._config.Data.to_dict().items()
        ]

        self.setColumnCount(len(self._headers))
        self.setHeaderLabels(self._headers)

        self.add_item_group("Plot", self._plot_children)
        self.add_item_group("Editing", self._editing_children)
        self.add_item_group("Data", self._data_children)

    def add_item_group(self, name: str, children: list[QtWidgets.QTreeWidgetItem]) -> None:
        item = QtWidgets.QTreeWidgetItem([name])
        item.addChildren(children)
        self.addTopLevelItem(item)


def test_config() -> None:
    cw = ConfigTreeWidget()
    dlg = QtWidgets.QDialog(qApp.mw)  # type: ignore  # noqa: F821
    layout = QtWidgets.QVBoxLayout()
    layout.addWidget(cw)
    dlg.setLayout(layout)
    dlg.exec()
