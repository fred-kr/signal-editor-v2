import datetime
import enum
import typing as t
from collections import OrderedDict
from pathlib import Path

import attrs
import polars as pl
from PySide6 import QtCore

from .. import type_defs as _t
from ..core.file_io import read_edf
from ..core.section import Section, SectionID


class MissingDataError(Exception):
    """
    Raised if any function is called that requires data to be loaded, while no data is available.
    """

    pass


class MissingSectionError(Exception):
    """
    Raised when trying to access a section (using a valid ID) that does not exist.
    """

    pass


def _epoch_to_unknown(
    value: datetime.datetime | str | None | int | QtCore.QDateTime,
) -> datetime.datetime | t.Literal["unknown"]:
    if not value:
        return "unknown"
    if isinstance(value, datetime.datetime):
        return (
            "unknown"
            if value == datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)
            else value
        )
    if isinstance(value, QtCore.QDateTime):
        if value == QtCore.QDateTime(1970, 1, 1, 0, 0, 0, 0) or not value.isValid():
            return "unknown"
        return t.cast(datetime.datetime, value.toPython())
    if isinstance(value, int):
        if value == 0:
            return "unknown"
        return datetime.datetime.fromtimestamp(value, datetime.timezone.utc)

    try:
        return datetime.datetime.fromisoformat(value)
    except ValueError:
        return "unknown"


@attrs.define
class SelectedFileMetadata:
    file_name: str = attrs.field(on_setattr=attrs.setters.frozen)
    file_format: str = attrs.field(on_setattr=attrs.setters.frozen)
    name_signal_column: str = attrs.field(on_setattr=attrs.setters.frozen)
    sampling_rate: int = attrs.field(converter=int)
    measured_date: datetime.datetime | t.Literal["unknown"] = attrs.field(
        default="unknown", converter=_epoch_to_unknown
    )
    subject_id: str = attrs.field(
        default="unknown", converter=attrs.converters.default_if_none("unknown")
    )
    oxygen_condition: str = attrs.field(
        default="unknown", converter=attrs.converters.default_if_none("unknown")
    )

    def update_from_dict(self, metadata_dict: _t.MutableMetadataAttributes) -> None:
        for k, v in metadata_dict.items():
            setattr(self, k, v)

    def to_dict(self) -> _t.SelectedFileMetadataDict:
        return _t.SelectedFileMetadataDict(
            file_name=self.file_name,
            file_format=self.file_format,
            name_signal_column=self.name_signal_column,
            sampling_rate=self.sampling_rate,
            measured_date=self.measured_date,
            subject_id=self.subject_id,
            oxygen_condition=self.oxygen_condition,
        )


class SectionContainer(OrderedDict[SectionID, Section]):
    def __setitem__(self, key: SectionID, value: Section) -> None:
        super().__setitem__(key, value)
        self.move_to_end(key)

    def __getitem__(self, key: SectionID) -> Section:
        return super().__getitem__(key)


class DataController(QtCore.QObject):
    sig_new_data_file_selected = QtCore.Signal(dict)
    sig_new_data_file_loaded = QtCore.Signal()
    sig_sampling_rate_changed = QtCore.Signal(int)
    sig_active_section_changed = QtCore.Signal(bool)
    sig_section_added = QtCore.Signal(str)
    sig_section_removed = QtCore.Signal(str)

    class SupportedFileFormats(enum.StrEnum):
        CSV = ".csv"
        TXT = ".txt"
        XLSX = ".xlsx"
        FEATHER = ".feather"
        EDF = ".edf"

    def __init__(self, parent: QtCore.QObject | None = None) -> None:
        super().__init__(parent)

        settings = QtCore.QSettings()
        self._sampling_rate = t.cast(int, settings.value("Data/sampling_rate"))

        self._original_data: pl.LazyFrame | None = None
        self._working_data: pl.DataFrame | None = None

        self._metadata = SelectedFileMetadata(
            file_name="",
            file_format="",
            name_signal_column="",
            sampling_rate=self._sampling_rate,
        )

        self._sections: SectionContainer = SectionContainer()
        self._active_section: Section | None = None
        self._base_section: Section | None = None

    @property
    def sections(self) -> SectionContainer:
        return self._sections

    @property
    def sampling_rate(self) -> int:
        return self._sampling_rate

    def _set_sampling_rate(self, value: int) -> None:
        """
        This method is used whenever the sampling rate is changed programmatically, as opposed
        to when the user changes the value in the UI.
        """
        self._sampling_rate = value
        self.sig_sampling_rate_changed.emit(value)

    @QtCore.Slot(int)
    def on_sampling_rate_changed(self, value: int) -> None:
        for section in self._sections.values():
            section.update_sampling_rate(value)

    def get_base_section(self) -> Section:
        if self._original_data is None:
            raise MissingDataError("No data available. Select a valid file to load, and try again.")
        if self._base_section is None:
            self._base_section = Section(self._original_data.collect())
        return self._base_section

    @property
    def active_section(self) -> Section:
        if self._active_section is None:
            # This will raise an exception if no data is available, so no need to check for it here (i think)
            self._active_section = self.get_base_section()
        return self._active_section

    @QtCore.Slot(str)
    def set_active_section(self, section_id: SectionID) -> None:
        if section_id not in self._sections:
            raise MissingSectionError(
                f"No section found for ID: '{section_id}'. Available sections: \n\n{list(self._sections.keys())}"
            )
        self._active_section = self._sections[section_id]
        has_peak_data = not self._active_section.peaks_local.is_empty()
        self.sig_active_section_changed.emit(has_peak_data)

    @property
    def editable_section_ids(self) -> list[SectionID]:
        """
        Returns the IDs of all currently available sections, excluding the base section.
        """
        return list(self._sections.keys())[1:] if len(self._sections) > 1 else []

    @property
    def metadata(self) -> SelectedFileMetadata:
        return self._metadata

    @property
    def signal_column(self) -> str:
        return self._metadata.name_signal_column

    @QtCore.Slot(QtCore.QDateTime)
    def set_measured_date(self, value: QtCore.QDateTime) -> None:
        if not value.isValid() or value == QtCore.QDateTime(1970, 1, 1, 0, 0, 0, 0):
            self._metadata.measured_date = "unknown"
        else:
            self._metadata.measured_date = t.cast(datetime.datetime, value.toPython())

    @QtCore.Slot(str)
    def set_subject_id(self, value: str) -> None:
        self._metadata.subject_id = value

    @QtCore.Slot(str)
    def set_oxygen_condition(self, value: _t.OxygenCondition) -> None:
        self._metadata.oxygen_condition = value

    def read_file(self, file_path: Path | str, **kwargs: t.Any) -> None:
        file_path = Path(file_path)
        if not file_path.is_file():
            raise FileNotFoundError(
                f"Path: {file_path} \n\nNo file exists at the specified path. Please check the path and try again."
            )
        # TODO: Maybe find a better way of determining the file format than using the file extension
        suffix = file_path.suffix
        if suffix not in self.SupportedFileFormats:
            raise ValueError(
                f"Unsupported file format: {suffix}. Allowed formats: {', '.join(self.SupportedFileFormats._member_names_)}"
            )

        match suffix:
            case ".csv":
                self._original_data = pl.scan_csv(file_path, try_parse_dates=True)
            case ".txt":
                self._original_data = pl.scan_csv(file_path, separator="\t", try_parse_dates=True)
            case ".xlsx":
                self._original_data = pl.read_excel(file_path).lazy()
            case ".feather":
                self._original_data = pl.scan_ipc(file_path)
            case ".edf":  # FIXME: This does not work
                data_channel = kwargs.get("edf_data_channel", "hbr")
                temperature_channel = kwargs.get("edf_temperature_channel", "temperature")
                if not data_channel or not temperature_channel:
                    raise ValueError(
                        "Reading EDF files requires specifying the names for the data and temperature channels."
                    )
                edf_data = read_edf(file_path, data_channel, temperature_channel)
                self._original_data = edf_data.lazy()
            case _:
                raise NotImplementedError(f"Cant read file type: {suffix}")

        self.sig_new_data_file_loaded.emit()

        print(self._original_data.fetch(10))
