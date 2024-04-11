import functools
import typing as t
from pathlib import Path

import mne.io
import polars as pl
from PySide6 import QtCore

from .. import type_defs as _t
from ..core.file_io import detect_sampling_rate, read_edf
from ..core.section import Section, SectionID
from ..enum_defs import TextFileSeparator
from ..models.data_table import DataTableModel
from ..models.metadata import QFileMetadata


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


class SectionContainer(t.OrderedDict[SectionID, Section]):
    def __setitem__(self, key: SectionID, value: Section) -> None:
        super().__setitem__(key, value)
        self.move_to_end(key)

    def __getitem__(self, key: SectionID) -> Section:
        return super().__getitem__(key)


class DataController(QtCore.QObject):
    sig_non_ascii_in_file_name = QtCore.Signal(list, bool)
    sig_user_input_required = QtCore.Signal(list)
    sig_new_metadata = QtCore.Signal(object)
    sig_new_data = QtCore.Signal()
    sig_sampling_rate_changed = QtCore.Signal(int)
    sig_active_section_changed = QtCore.Signal(bool)
    sig_section_added = QtCore.Signal(str)
    sig_section_removed = QtCore.Signal(str)

    SUPPORTED_FILE_FORMATS = frozenset([".edf", ".feather", ".csv", ".txt", ".tsv"])

    def __init__(self, parent: QtCore.QObject | None = None) -> None:
        super().__init__(parent)

        settings = QtCore.QSettings()
        self._sampling_rate = int(settings.value("Data/sampling_rate"))  # type: ignore

        self._base_df: pl.DataFrame | None = None
        self.base_df_model = DataTableModel(self)
        self._working_df: pl.DataFrame | None = None
        self.working_df_model = DataTableModel(self)

        self.metadata: QFileMetadata | None = None

        self._sections: SectionContainer = SectionContainer()
        self._active_section: Section | None = None
        self._base_section: Section | None = None
        try:
            self._txt_separator = TextFileSeparator(
                QtCore.QSettings().value("Data/txt_file_separator_character", TextFileSeparator.Tab)
            ).value
        except Exception:
            self._txt_separator = TextFileSeparator.Tab
        self._reader_funcs = {
            ".csv": functools.partial(pl.scan_csv, separator=TextFileSeparator.Comma),
            ".txt": functools.partial(pl.scan_csv, separator=self._txt_separator),
            ".tsv": functools.partial(pl.scan_csv, separator=TextFileSeparator.Tab),
        }

    @property
    def base_df(self) -> pl.DataFrame:
        if self._base_df is None:
            raise MissingDataError("No data available. Select a valid file to load, and try again.")
        return self._base_df

    @property
    def working_df(self) -> pl.DataFrame:
        if self._working_df is None:
            raise MissingDataError("No data available. Select a valid file to load, and try again.")
        return self._working_df

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
        if self._base_df is None:
            raise MissingDataError("No data available. Select a valid file to load, and try again.")
        if self._base_section is None:
            self._base_section = Section(self._base_df)
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

    def update_metadata(self, sampling_rate: int | None = None, signal_col: str | None = None, info_col: str | None = None) -> None:
        if self.metadata is None:
            return
        
        if sampling_rate is not None:
            self.metadata.sampling_rate = sampling_rate
        if signal_col != "" and signal_col is not None:
            self.metadata.signal_column = signal_col
        if info_col is not None:
            self.metadata.info_column = info_col

        self.base_df_model.set_metadata(self.metadata)
        self.sig_new_metadata.emit(self.metadata)
        

    @QtCore.Slot(str)
    def select_file(self, file_path: Path | str) -> None:
        file_path = Path(file_path)
        if not file_path.is_file():
            raise FileNotFoundError(
                f"Path: {file_path} \n\nNo file exists at the specified path. Please check the path and try again."
            )
        if file_path.suffix not in self.SUPPORTED_FILE_FORMATS:
            raise ValueError(
                f"Unsupported file format: {file_path.suffix}. Allowed formats: {', '.join(self.SUPPORTED_FILE_FORMATS)}"
            )
        settings = QtCore.QSettings()

        last_sampling_rate = settings.value("Data/sampling_rate", 0)
        last_signal_col = settings.value("Misc/last_signal_column_name", None)
        last_info_col = settings.value("Misc/last_info_column_name", None)
        metadata = QFileMetadata(file_path, self)

        match file_path.suffix:
            case ".edf":
                edf_info = mne.io.read_raw_edf(file_path, preload=False)
                metadata.sampling_rate = edf_info.info["sfreq"]
                metadata.column_names = edf_info.ch_names
                # self._metadata = EDFFileMetadata(file_path)
            case ".feather":
                lf = pl.scan_ipc(file_path)
                metadata.column_names = lf.columns
                try:
                    metadata.sampling_rate = detect_sampling_rate(lf)
                except Exception:
                    metadata.sampling_rate = int(last_sampling_rate)

                # self._metadata = FeatherFileMetadata(file_path)
            case ".csv" | ".txt" | ".tsv":
                lf = self._reader_funcs[file_path.suffix](file_path)
                metadata.column_names = lf.columns
                try:
                    metadata.sampling_rate = detect_sampling_rate(lf)
                except Exception:
                    metadata.sampling_rate = int(last_sampling_rate)

                # self._metadata = TextFileMetadata(file_path)
            case _:
                raise ValueError(
                    f"Unsupported file format: {file_path.suffix}. Please select a valid file format."
                )

        if last_signal_col in metadata.column_names:
            metadata.signal_column = str(last_signal_col)
        if last_info_col in metadata.column_names:
            metadata.info_column = str(last_info_col)
        self.metadata = metadata
        if self.metadata.required_fields:
            self.sig_user_input_required.emit(self.metadata.required_fields)

        self.base_df_model.set_metadata(self.metadata)
        self.sig_new_metadata.emit(self.metadata)

    def read_file(self, **kwargs: t.Unpack[_t.ReadFileKwargs]) -> None:
        if self.metadata is None:
            return
        suffix = self.metadata.file_format
        file_path = self.metadata.file_path
        settings = QtCore.QSettings()
        separator = TextFileSeparator(
            settings.value("Data/txt_file_separator_character", TextFileSeparator.Tab)
        )

        signal_col = self.metadata.signal_column
        info_col = self.metadata.info_column
        other_cols = kwargs.get("columns")
        columns = [signal_col]
        if info_col:
            columns.append(info_col)
        if other_cols is not None:
            columns.extend(other_cols)

        match suffix:
            case ".csv":
                self._base_df = pl.read_csv(file_path, columns=columns)
            case ".txt":
                self._base_df = pl.read_csv(file_path, columns=columns, separator=separator)
            case ".tsv":
                self._base_df = pl.read_csv(
                    file_path,
                    columns=columns,
                    separator=TextFileSeparator.Tab,
                )
            case ".feather":
                self._base_df = pl.read_ipc(file_path, columns=columns)
            case ".edf":
                if info_col == "":
                    info_col = "temperature"
                self._base_df = read_edf(
                    Path(file_path), data_channel=signal_col, info_channel=info_col
                )
            case _:
                raise NotImplementedError(f"Cant read file type: {suffix}")

        self.base_df_model.set_dataframe(self._base_df, signal_col, info_col=info_col)
        self.sig_new_data.emit()
