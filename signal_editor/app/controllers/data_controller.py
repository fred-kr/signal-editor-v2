import functools
from pathlib import Path

import mne.io
import polars as pl
from PySide6 import QtCore

from ..core.file_io import detect_sampling_rate, read_edf
from ..core.section import Section, SectionID
from ..enum_defs import TextFileSeparator
from ..models.data_table import DataTableModel
from ..models.metadata import QFileMetadata
from ..models.section_container import SectionListModel


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
        Section.reset_id_counter()

        settings = QtCore.QSettings()
        self._sampling_rate = int(settings.value("Data/sampling_rate"))  # type: ignore

        self.data_model = DataTableModel(self)

        self._metadata: QFileMetadata | None = None

        self._sections = SectionListModel(parent=self)
        self._active_section: Section | None = None
        self.active_section_model = DataTableModel(self)
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
        return self.data_model.df

    @property
    def sections(self) -> SectionListModel:
        return self._sections

    @property
    def sampling_rate(self) -> int:
        return self._sampling_rate

    @property
    def metadata(self) -> QFileMetadata:
        if self._metadata is None:
            raise MissingDataError("No data available.")
        return self._metadata

    def _set_sampling_rate(self, value: int) -> None:
        """
        This method is used whenever the sampling rate is changed programmatically, as opposed
        to when the user changes the value in the UI.
        """
        self._sampling_rate = value
        self.sig_sampling_rate_changed.emit(value)

    @QtCore.Slot(int)
    def on_sampling_rate_changed(self, value: int) -> None:
        self.sections.update_sampling_rate(value)

    def get_base_section(self) -> Section:
        if self._base_section is None:
            try:
                self._base_section = Section(self.base_df, self.metadata.signal_column)
            except Exception as e:
                raise MissingDataError(
                    "No data available. Select a valid file to load, and try again."
                ) from e
        return self._base_section

    @property
    def active_section(self) -> Section:
        if self._active_section is None:
            self._active_section = self.get_base_section()
        return self._active_section

    @QtCore.Slot(QtCore.QModelIndex)
    def set_active_section(self, model_index: QtCore.QModelIndex) -> None:
        section = self.sections.data(model_index, QtCore.Qt.ItemDataRole.UserRole)
        if isinstance(section, Section):
            self._active_section = section
            self.active_section_model.set_metadata(self.metadata)
            self.active_section_model.set_dataframe(self._active_section.data)
            has_peak_data = not self._active_section.peaks_local.is_empty()
            self.sig_active_section_changed.emit(has_peak_data)

    @property
    def editable_section_ids(self) -> list[SectionID]:
        """
        Returns the IDs of all currently available sections, excluding the base section.
        """
        return self.sections.editable_section_ids

    def update_metadata(
        self,
        sampling_rate: int | None = None,
        signal_col: str | None = None,
        info_col: str | None = None,
    ) -> None:
        if self._metadata is None:
            return

        if sampling_rate is not None:
            self.metadata.sampling_rate = sampling_rate
        if signal_col != "" and signal_col is not None:
            self.metadata.signal_column = signal_col
        if info_col is not None:
            self.metadata.info_column = info_col

        self.data_model.set_metadata(self.metadata)
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

        last_sampling_rate: int = settings.value("Data/sampling_rate", 0)  # type: ignore
        last_signal_col = settings.value("Misc/last_signal_column_name", None)
        last_info_col = settings.value("Misc/last_info_column_name", None)
        metadata = QFileMetadata(file_path, self)

        match file_path.suffix:
            case ".edf":
                edf_info = mne.io.read_raw_edf(file_path, preload=False)
                metadata.sampling_rate = edf_info.info["sfreq"]
                metadata.column_names = edf_info.ch_names
            case ".feather":
                lf = pl.scan_ipc(file_path)
                metadata.column_names = lf.columns
                try:
                    metadata.sampling_rate = detect_sampling_rate(lf)
                except Exception:
                    metadata.sampling_rate = last_sampling_rate

            case ".csv" | ".txt" | ".tsv":
                lf = self._reader_funcs[file_path.suffix](file_path)
                metadata.column_names = lf.columns
                try:
                    metadata.sampling_rate = detect_sampling_rate(lf)
                except Exception:
                    metadata.sampling_rate = last_sampling_rate

            case _:
                raise ValueError(
                    f"Unsupported file format: {file_path.suffix}. Please select a valid file format."
                )

        if last_signal_col in metadata.column_names:
            metadata.signal_column = str(last_signal_col)
        if last_info_col in metadata.column_names:
            metadata.info_column = str(last_info_col)
        self._metadata = metadata
        if self.metadata.required_fields:
            self.sig_user_input_required.emit(self.metadata.required_fields)

        self.data_model.set_metadata(self.metadata)
        self.sig_new_metadata.emit(self.metadata)

    def read_file(self) -> None:
        if self._metadata is None:
            return
        suffix = self.metadata.file_format
        file_path = self.metadata.file_path
        settings = QtCore.QSettings()
        separator = TextFileSeparator(
            settings.value("Data/txt_file_separator_character", TextFileSeparator.Tab)
        )

        signal_col = self.metadata.signal_column
        info_col = self.metadata.info_column
        columns = [signal_col]
        if info_col:
            columns.append(info_col)
        row_index_col = "index" if "index" not in columns else None

        match suffix:
            case ".csv":
                df = pl.read_csv(file_path, columns=columns, row_index_name=row_index_col)
            case ".txt":
                df = pl.read_csv(
                    file_path, columns=columns, separator=separator, row_index_name=row_index_col
                )
            case ".tsv":
                df = pl.read_csv(
                    file_path,
                    columns=columns,
                    separator=TextFileSeparator.Tab,
                    row_index_name=row_index_col,
                )
            case ".feather":
                df = pl.read_ipc(file_path, columns=columns, row_index_name=row_index_col)
            case ".edf":
                if info_col == "":
                    info_col = "temperature"
                df = read_edf(Path(file_path), data_channel=signal_col, info_channel=info_col)
            case _:
                raise NotImplementedError(f"Cant read file type: {suffix}")

        self.data_model.set_dataframe(df, signal_col, info_col=info_col)
        self._base_section = Section(df, self.metadata.signal_column)
        self.sections.add_section(self._base_section)
        self.sig_new_data.emit()

    def create_new_section(self, start: float | int, stop: float | int) -> None:
        if self._metadata is None:
            return
        data = self.base_df.filter(pl.col("index").is_between(start, stop))
        section = Section(data, self.metadata.signal_column)
        self.sections.add_section(section)
        self.sig_section_added.emit(section.section_id)

    def delete_section(self, idx: QtCore.QModelIndex | SectionID) -> None:
        if isinstance(idx, SectionID):
            self.sections.remove_section(idx)
        else:
            self.sections.remove_section_by_index(idx)
