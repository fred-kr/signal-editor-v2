import datetime
import typing as t
from pathlib import Path
import sys

import attrs
import pyqtgraph as pg
from PySide6 import QtCore, QtGui, QtWidgets

from .. import type_defs as _t
from ..utils import exceptions_as_dialog


class ConfigError(Exception):
    """
    Base class for all config errors.
    """

    pass


@attrs.define
class GeneralConfig:
    app_name: str = "Signal Editor"
    app_version: str = "0.1.0"
    app_author: str = "Frederik Krämer"
    ui_theme: t.Literal["light", "dark"] = "light"


@attrs.define
class MessageConfig:
    level: t.Literal["all", "info", "warning", "error", "critial", "debug", "none"] = "all"
    include_timestamp: bool = True
    include_stack_trace: bool = False


def _set_pg_config_option[T: _t.PGColor | bool](instance: "PlotConfig", attribute: t.Any, value: T) -> T:
    if attribute.name in pg.CONFIG_OPTIONS:
        pg.setConfigOption(attribute.name, value)
    return value


@attrs.define
class PlotConfig:
    use_open_gl: bool = attrs.field(default=True, on_setattr=_set_pg_config_option)
    show_regions: bool = attrs.field(default=True)
    show_grid: bool = attrs.field(default=True)
    foreground: _t.PGColor = attrs.field(default="d", on_setattr=_set_pg_config_option)
    background: _t.PGColor = attrs.field(default="k", on_setattr=_set_pg_config_option)
    signal_color: _t.PGColor = attrs.field(default="gray")
    scatter_color: _t.PGColor = attrs.field(default="gold")
    rate_color: _t.PGColor = attrs.field(default="seagreen")
    region_color: _t.PGColor = (100, 200, 150, 40)
    signal_line_click_tolerance: int = 70
    scatter_search_radius: int = 20
    rate_type: t.Literal["instantaneous", "rolling_window"] = "instantaneous"
    min_peak_distance: int = 20


@attrs.define
class InputDataConfig:
    signal_column: str = "signal"
    index_column: str | None = "index"
    time_column: str | None = "time"
    info_column_a: str | None = "temperature"
    info_column_b: str | None = None
    sampling_rate: int = 400
    processed_signal_column_suffix: str = "processed"
    measured_date_special_value: datetime.datetime = datetime.datetime(1970, 1, 1)


def _convert_to_path(value: str | Path) -> Path:
    return Path(value).resolve()

    
@attrs.define
class DirPathConfig:
    data_dir: Path = attrs.field(default=Path("."), converter=_convert_to_path)
    export_dir: Path = attrs.field(default=Path("."), converter=_convert_to_path)


class ConfigController(QtCore.QObject):
    """
    Singleton class holding various configuration settings for the application.
    """

    _instance: "ConfigController | None" = None

    _general: GeneralConfig = GeneralConfig()
    _plot: PlotConfig = PlotConfig()
    _input_data: InputDataConfig = InputDataConfig()
    _dir_paths: DirPathConfig = DirPathConfig()
    _messages: MessageConfig = MessageConfig()
    
    sig_setting_changed = QtCore.Signal(str, object)

    def __new__(cls, parent: QtCore.QObject | None = None) -> "ConfigController":
        if cls._instance is None:
            cls._instance = super(ConfigController, cls).__new__(cls)
            # super(ConfigController, cls._instance).__init__(parent)
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

    @property
    def messages(self) -> MessageConfig:
        return self._messages

    def set_option(
        self,
        where: t.Literal["general", "plot", "input_data", "dir_paths", "messages"],
        attr_name: str,
        attr_value: t.Any,
    ) -> None:
        sub_config = getattr(self, where)
        if attr_name not in attrs.fields(sub_config):
            return
        match where:
            case "general":
                setattr(self._general, attr_name, attr_value)
            case "plot":
                setattr(self._plot, attr_name, attr_value)
            case "input_data":
                setattr(self._input_data, attr_name, attr_value)
            case "dir_paths":
                setattr(self._dir_paths, attr_name, attr_value)
            case "messages":
                setattr(self._messages, attr_name, attr_value)

        self.sig_setting_changed.emit(attr_name, attr_value)

    @exceptions_as_dialog(re_raise=False, include_traceback=False)
    def get_option(
        self,
        where: t.Literal["general", "plot", "input_data", "dir_paths", "messages"],
        attr_name: str,
    ) -> t.Any:
        sub_config = getattr(self, where)
        option = getattr(sub_config, attr_name, None)
        if option is None:
            raise ConfigError(f"Invalid config option: '{attr_name}' for '{where}'")

        match where:
            case "general":
                return getattr(self._general, attr_name)
            case "plot":
                return getattr(self._plot, attr_name)
            case "input_data":
                return getattr(self._input_data, attr_name)
            case "dir_paths":
                return getattr(self._dir_paths, attr_name)
            case "messages":
                return getattr(self._messages, attr_name)
