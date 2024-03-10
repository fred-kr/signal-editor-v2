from pathlib import Path
import typing as t
from dataclasses import dataclass, field

import polars as pl
from PySide6 import QtCore

from ..core.file_readers import LoadedFileData, read_edf

from .. import type_defs as _t
from ..core.section import Section, SectionID
from ..utils import exceptions_as_dialog
from .config_controller import ConfigController as Config

if t.TYPE_CHECKING:
    from .config_controller import InputDataConfig


class MissingDataError(Exception):
    """
    Raised if any function is called that requires data to be loaded, while no data is available.
    """

    pass


class SectionNotFoundError(Exception):
    """
    Raised when trying to access a section (using a valid ID) that does not exist.
    """

    pass

class UnsupportedFileTypeError(Exception):
    """
    Raised when trying to load a file of an unsupported format.
    """
    pass

@dataclass(slots=True)
class LoadedFileMetadata:
    file_name: str = field()
    file_format: str = field()
    name_signal_column: str = field()
    sampling_rate: int = field()
    measured_date: str = field(default="unknown")
    subject_id: str = field(default="unknown")
    oxygen_condition: _t.OxygenCondition = field(default="unknown")

    def update_from_dict(self, metadata_dict: _t.LoadedFileMetadataDict) -> None:
        for k, v in metadata_dict.items():
            setattr(self, k, v)
            
    def to_dict(self) -> _t.LoadedFileMetadataDict:
        return _t.LoadedFileMetadataDict(
            file_name=self.file_name,
            file_format=self.file_format,
            name_signal_column=self.name_signal_column,
            sampling_rate=self.sampling_rate,
            measured_date=self.measured_date,
            subject_id=self.subject_id,
            oxygen_condition=self.oxygen_condition,
        )


class SectionContainer(t.OrderedDict[SectionID, Section]):
    def __setitem__(self, key: SectionID, value: Section) -> None:
        super().__setitem__(key, value)
        self.move_to_end(key)

    def __getitem__(self, key: SectionID) -> Section:
        return super().__getitem__(key)


class DataController(QtCore.QObject):
    sig_new_file_loaded = QtCore.Signal()
    sig_sampling_rate_changed = QtCore.Signal(int)
    sig_active_section_changed = QtCore.Signal(bool)
    sig_section_added = QtCore.Signal(str)
    sig_section_removed = QtCore.Signal(str)

    def __init__(self, parent: QtCore.QObject | None = None) -> None:
        super().__init__(parent)

        data_config: "InputDataConfig" = Config().input_data
        self._sampling_rate: int = data_config.sampling_rate
        self._supported_file_extensions = {".csv", ".txt", ".xlsx", ".feather", ".edf"}

        self._original_data: pl.LazyFrame | None = None
        self._working_data: pl.DataFrame | None = None

        self._metadata = LoadedFileMetadata(
            file_name="",
            file_format="",
            name_signal_column=data_config.signal_column,
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

    @exceptions_as_dialog(
        re_raise=True, include_traceback=False, additional_msg="Failed to get base section"
    )
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

    @exceptions_as_dialog(
        re_raise=True, include_traceback=False, additional_msg="Failed to set active section"
    )
    @QtCore.Slot(str)
    def set_active_section(self, section_id: SectionID) -> None:
        if section_id not in self._sections:
            raise SectionNotFoundError(
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
    def metadata(self) -> LoadedFileMetadata:
        return self._metadata

    @property
    def signal_column(self) -> str:
        return self._metadata.name_signal_column

    @QtCore.Slot(QtCore.QDate)
    def set_measured_date(self, value: QtCore.QDate) -> None:
        if not value.isValid() or value == Config().input_data.measured_date_special_value:
            self._metadata.measured_date = "unknown"
        else:
            self._metadata.measured_date = value.toString("yyyy-MM-dd")
            
    @QtCore.Slot(str)
    def set_subject_id(self, value: str) -> None:
        self._metadata.subject_id = value

    @QtCore.Slot(str)
    def set_oxygen_condition(self, value: _t.OxygenCondition) -> None:
        self._metadata.oxygen_condition = value

    @exceptions_as_dialog(re_raise=False)
    def read_file(self, file_path: Path) -> None:
        if not file_path.is_file():
            raise FileNotFoundError(f"Path: {file_path} \n\nNo file exists at the specified path. Please check the path and try again.")
        # TODO: Maybe find a better way of determining the file format than using the file extension
        suffix = file_path.suffix
        if suffix not in self._supported_file_extensions:
            raise UnsupportedFileTypeError(f"File type '{suffix}' is not supported. Please select a file with one of the following extensions: {', '.join(self._supported_file_extensions)}")

        data_config = Config().input_data
        
        match suffix:
            case ".csv":
                self._original_data = pl.scan_csv(file_path, try_parse_dates=True)
            case ".txt":
                self._original_data = pl.scan_csv(file_path, separator="\t", try_parse_dates=True)
            case ".xlsx":
                self._original_data = pl.read_excel(file_path).lazy()
            case ".feather":
                self._original_data = pl.scan_ipc(file_path)
            case ".edf":
                edf_data = read_edf(file_path)
                self._original_data = edf_data.data
                
                
                