import polars as pl
from PySide6 import QtCore
import datetime

from .config_controller import ConfigController as Config
from .. import type_defs as _t
from dataclasses import dataclass, field

@dataclass(slots=True)
class InputFileMetadata:
    file_name: str
    file_format: str
    name_signal_column: str
    sampling_rate: int 
    measured_date: str = "unknown"
    subject_id: str = "unknown"
    oxygen_condition: _t.OxygenCondition = "unknown"

    def to_dict(self) -> _t.InputFileMetadataDict:
        return _t.InputFileMetadataDict(
            file_name=self.file_name,
            file_format=self.file_format,
            name_signal_column=self.name_signal_column,
            sampling_rate=self.sampling_rate,
            measured_date=self.measured_date,
            subject_id=self.subject_id,
            oxygen_condition=self.oxygen_condition,
        )

class DataController(QtCore.QObject):
    sig_new_data = QtCore.Signal()
    sig_sampling_rate_changed = QtCore.Signal(int)
    sig_active_section_changed = QtCore.Signal(bool)
    sig_section_added = QtCore.Signal(str)
    sig_section_removed = QtCore.Signal(str)

    def __init__(self, parent: QtCore.QObject | None = None) -> None:
        super().__init__(parent)

        self._sampling_rate: int = 0

        self._original_data: pl.LazyFrame | None = None
        self._working_data: pl.DataFrame | None = None
        self._metadata = InputFileMetadata(
            file_name="",
            file_format="",
            name_signal_column="",
            sampling_rate=self._sampling_rate,
            measured_date="unknown",
            subject_id="unknown",
            oxygen_condition="unknown",
        )
