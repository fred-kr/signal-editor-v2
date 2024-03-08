import typing as t
from dataclasses import dataclass
from pathlib import Path

from PySide6 import QtCore

from .. import type_defs as _t


@dataclass(slots=True)
class GeneralConfig:
    app_name: str = "Signal Editor"
    app_version: str = "0.1.0"
    app_author: str = "Frederik Krämer"
    ui_theme: t.Literal["light", "dark"] = "light"


@dataclass(slots=True)
class PlotConfig:
    use_open_gl: bool = True
    show_regions: bool = True
    show_grid: bool = True
    foreground: _t.ColorLike = "d"
    background: _t.ColorLike = "k"
    signal_color: _t.ColorLike = "gray"
    scatter_color: _t.ColorLike = "gold"
    rate_color: _t.ColorLike = "seagreen"
    region_color: _t.ColorLike = (100, 200, 150, 40)
    signal_line_click_tolerance: int = 70
    scatter_search_radius: int = 20
    rate_type: t.Literal["instantaneous", "rolling_window"] = "instantaneous"
    min_peak_distance: int = 20


@dataclass(slots=True)
class InputDataConfig:
    signal_column: str = "signal"
    index_column: str | None = "index"
    time_column: str | None = "time"
    info_column_a: str | None = "temperature"
    info_column_b: str | None = None
    sampling_rate: int = 400
    processed_signal_column_suffix: str = "processed"


@dataclass(slots=True)
class DirPathConfig:
    data_dir: Path = Path(".")
    export_dir: Path = Path(".")


class ConfigController(QtCore.QObject):
    """
    Singleton class holding various configuration settings for the application.
    """

    _instance: "ConfigController | None" = None
    _general: GeneralConfig = GeneralConfig()
    _plot: PlotConfig = PlotConfig()
    _input_data: InputDataConfig = InputDataConfig()
    _dir_paths: DirPathConfig = DirPathConfig()
    setting_changed = QtCore.Signal(str, object)

    def __new__(cls, parent: QtCore.QObject | None = None) -> "ConfigController":
        if cls._instance is None:
            cls._instance = super(ConfigController, cls).__new__(cls)
            super(ConfigController, cls._instance).__init__(parent)
        return cls._instance

    @property
    def general(self) -> GeneralConfig:
        return self._general

    @property
    def plot(self) -> PlotConfig:
        return self._plot

    @property
    def input_data(self) -> InputDataConfig:
        return self._input_data

    @property
    def dir_paths(self) -> DirPathConfig:
        return self._dir_paths

    def set_option(
        self,
        where: t.Literal["general", "plot", "input_data", "dir_paths"],
        attr_name: str,
        attr_value: t.Any,
    ) -> None:
        match where:
            case "general":
                setattr(self._general, attr_name, attr_value)
            case "plot":
                setattr(self._plot, attr_name, attr_value)
            case "input_data":
                setattr(self._input_data, attr_name, attr_value)
            case "dir_paths":
                setattr(self._dir_paths, attr_name, attr_value)

        self.setting_changed.emit(attr_name, attr_value)

    def get_option(
        self, where: t.Literal["general", "plot", "input_data", "dir_paths"], attr_name: str
    ) -> t.Any:
        match where:
            case "general":
                return getattr(self._general, attr_name)
            case "plot":
                return getattr(self._plot, attr_name)
            case "input_data":
                return getattr(self._input_data, attr_name)
            case "dir_paths":
                return getattr(self._dir_paths, attr_name)
