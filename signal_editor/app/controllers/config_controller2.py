import enum
import typing as t
from pathlib import Path

import attrs
import pyqtgraph as pg
from PySide6 import QtCore, QtGui, QtWidgets

from .. import type_defs as _t


@attrs.frozen
class AboutApp:
    name: str = "Signal Editor"
    version: str = "0.1.0"
    author: str = "Frederik Krämer"
    email: str = "frdrkkraemer@gmail.com"
    description: str = "Application for working with physiological signal data (ECG, PPG, etc.). Main feature is the ability to easily modify detected peaks via interaction with the plotted data."
    license: str = "MIT"
    url: str = "https://github.com/fred-kr/signal-editor"  # TODO: update link once v2 is ready


def get_app_dir() -> QtCore.QDir:
    app_instance = QtWidgets.QApplication.instance()
    import sys

    if hasattr(sys, "frozen") and app_instance is not None:
        return QtCore.QDir(app_instance.applicationDirPath())
    return QtCore.QDir.current()


def _to_qdir(path: str | Path | QtCore.QDir) -> QtCore.QDir:
    return path if isinstance(path, QtCore.QDir) else QtCore.QDir(path)


@attrs.define
class UserConfig:
    """
    Holds settings that can be modified while the app is running, with changes persisting across
    sessions. Uses `QtCore.QSettings` to store the values.
    """

    class CATEGORIES(enum.StrEnum):
        """
        Categories for the settings. Used to group the settings in the `QtCore.QSettings` object.
        """

        GENERAL = "general"
        PLOT = "plot"
        EDIT = "edit"

    class RATE_METHODS(enum.StrEnum):
        """
        Which method to use for computing the rate displayed in the lower plot on the editing page.
        """

        INSTANTANEOUS = "instantaneous"
        ROLLING_WINDOW = "rolling_window"

    _app_dir: t.ClassVar[QtCore.QDir] = get_app_dir()

    general_location_data_files: QtCore.QDir = attrs.field(default=_app_dir, converter=_to_qdir)
    general_location_export_files: QtCore.QDir = attrs.field(default=_app_dir, converter=_to_qdir)
    plot_background_color: QtGui.QColor = attrs.field(default="black", converter=pg.mkColor)
    plot_foreground_color: QtGui.QColor = attrs.field(default="lightgray", converter=pg.mkColor)
    plot_scatter_color: QtGui.QColor = attrs.field(default="gold", converter=pg.mkColor)
    plot_signal_color: QtGui.QColor = attrs.field(default="gray", converter=pg.mkColor)
    plot_rate_color: QtGui.QColor = attrs.field(default="steelblue", converter=pg.mkColor)
    plot_region_color: QtGui.QColor = attrs.field(default=(100, 200, 150, 40), converter=pg.mkColor)
    plot_signal_line_click_width: int = attrs.field(default=70, converter=int)
    plot_search_around_click_radius: int = attrs.field(default=20, converter=int)
    edit_minimum_allowed_peak_distance: int = attrs.field(default=20, converter=int)
    edit_rate_computation_method: RATE_METHODS = attrs.field(default=RATE_METHODS.INSTANTANEOUS)

    @classmethod
    def from_persisted(cls) -> "UserConfig":
        settings = QtCore.QSettings()
        user_config = cls()
        
        for category in cls.CATEGORIES:
            settings.beginGroup(category.name)
            for attr in attrs.fields(user_config.__class__):
                if attr.name.startswith(category.value):
                    stored_value = settings.value(attr.name, attr.default)
                    setattr(user_config, attr.name, stored_value)
            settings.endGroup()
        return user_config

    def write(self) -> None:
        settings = QtCore.QSettings()
        for category in self.CATEGORIES:
            settings.beginGroup(category.name)
            for attr in attrs.fields(self.__class__):
                if attr.name.startswith(category.value):
                    settings.setValue(attr.name, getattr(self, attr.name, attr.default))
            settings.endGroup()

    def to_dict(self) -> _t.UserConfigDict:
        return _t.UserConfigDict(**attrs.asdict(self))


@attrs.define
class SessionConfig:
    """
    Holds settings that are specific to a single session and are not persisted across sessions.
    """

    show_sections_in_overview_plot: bool = attrs.field(
        default=True, converter=attrs.converters.to_bool
    )


class ConfigController:
    _instance: "ConfigController | None" = None

    @classmethod
    def instance(cls) -> "ConfigController":
        if cls._instance is None:
            cls._instance = ConfigController()
        return cls._instance

    def __init__(self) -> None:
        self.about = AboutApp()
        self.user = UserConfig.from_persisted()
        self.session = SessionConfig()

    def save(self, force_sync: bool = True) -> None:
        self.user.write()
        if force_sync:
            settings = QtCore.QSettings()
            settings.sync()

    def reset(self) -> None:
        self.user = UserConfig()
        self.save()
