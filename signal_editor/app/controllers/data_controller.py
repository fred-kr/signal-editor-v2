import functools
import typing as t
from pathlib import Path

import mne.io
import polars as pl
from loguru import logger
from PySide6 import QtCore

from ..config import Config
from ..constants import COLUMN_PLACEHOLDER
from ..core.file_io import detect_sampling_rate, read_edf
from ..core.section import Section
from ..enum_defs import TextFileSeparator
from ..models.df_model import DataFrameModel
from ..models.metadata import FileMetadata
from ..models.result_models import CompleteResult, SelectedFileMetadata
from ..models.section_list_model import SectionListModel


class DataController(QtCore.QObject):
    sig_non_ascii_in_file_name = QtCore.Signal(list, bool)
    sig_user_input_required = QtCore.Signal(set)
    sig_new_metadata = QtCore.Signal(object)
    sig_new_data = QtCore.Signal()
    sig_active_section_changed = QtCore.Signal(bool)
    sig_section_added = QtCore.Signal(str)
    sig_section_removed = QtCore.Signal(str)

    SUPPORTED_FILE_FORMATS = frozenset([".edf", ".feather", ".csv", ".txt", ".tsv", ".xlsx", ".hdf5"])

    def __init__(self, parent: QtCore.QObject | None = None) -> None:
        super().__init__(parent)
        self.has_data = False

        self.data_model = DataFrameModel(self)

        self._metadata: FileMetadata | None = None

        self._sections = SectionListModel(parent=self)
        self._active_section: Section | None = None
        self.active_section_model = DataFrameModel(self)
        self._base_section: Section | None = None
        self.result_model_peaks = DataFrameModel(self)
        self.result_model_rate = DataFrameModel(self)

        try:
            self._txt_separator = Config().data.TextSeparatorChar
        except Exception:
            self._txt_separator = TextFileSeparator.Tab
        self._reader_funcs = {
            ".csv": functools.partial(pl.scan_csv, separator=TextFileSeparator.Comma),
            ".txt": functools.partial(pl.scan_csv, separator=self._txt_separator),
            ".tsv": functools.partial(pl.scan_csv, separator=TextFileSeparator.Tab),
            ".feather": pl.scan_ipc,
        }

    @property
    def base_df(self) -> pl.DataFrame:
        return self.data_model.df

    @property
    def sections(self) -> SectionListModel:
        return self._sections

    @property
    def metadata(self) -> FileMetadata:
        if self._metadata is None:
            raise ValueError("No data available.")
        return self._metadata

    def get_base_section(self) -> Section:
        if self._base_section is None:
            try:
                self._base_section = Section(
                    self.base_df, signal_name=self.metadata.signal_column, info_column=self.metadata.info_column
                )
                self._base_section.set_locked(True)
            except Exception as e:
                raise ValueError("No data available. Select a valid file to load, and try again.") from e
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
            self.active_section_model.set_df(self._active_section.data)
            has_peak_data = not self._active_section.peaks_local.is_empty()
            self.sig_active_section_changed.emit(has_peak_data)

    @property
    def base_section_index(self) -> QtCore.QModelIndex:
        return self.sections.index(0)

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
        if signal_col is not None:
            self.metadata.signal_column = signal_col
        if info_col is not None:
            self.metadata.info_column = info_col

        self.sig_new_metadata.emit(self.metadata)

    @QtCore.Slot(str)
    def open_file(self, file_path: Path | str) -> None:
        file_path = Path(file_path)
        if not file_path.is_file():
            logger.error(
                f"Path: {file_path} \n\nNo file exists at the specified path. Please check the path and try again."
            )
        if file_path.suffix not in self.SUPPORTED_FILE_FORMATS:
            logger.error(
                f"Unsupported file format: {file_path.suffix}. Allowed formats: {', '.join(self.SUPPORTED_FILE_FORMATS)}"
            )

        config = Config()
        last_sampling_rate = config.internal.LastSamplingRate
        last_signal_col = config.internal.LastSignalColumn
        last_info_col = config.internal.LastInfoColumn

        other_info: dict[str, t.Any] = {}

        if file_path.suffix == ".edf":
            edf_info = mne.io.read_raw_edf(file_path, preload=False, verbose=False)
            sampling_rate = t.cast(int, edf_info.info["sfreq"])
            column_names: list[str] = edf_info.ch_names
            other_info = dict(edf_info.info)
        elif file_path.suffix in {".feather", ".csv", ".txt", ".tsv"}:
            lf = self._reader_funcs[file_path.suffix](file_path)
            column_names = lf.collect_schema().names()
            try:
                sampling_rate = detect_sampling_rate(lf)
            except Exception:
                sampling_rate = last_sampling_rate
        elif file_path.suffix == ".xlsx":
            lf = pl.read_excel(file_path).lazy()
            column_names = lf.collect_schema().names()
            try:
                sampling_rate = detect_sampling_rate(lf)
            except Exception:
                sampling_rate = last_sampling_rate
        elif file_path.suffix == ".hdf5":
            raise NotImplementedError("HDF5 file support is not yet implemented.")
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}. Please select a valid file format.")

        metadata = FileMetadata(file_path, column_names, sampling_rate)
        if last_signal_col in metadata.valid_columns:
            metadata.signal_column = last_signal_col
        if last_info_col in metadata.valid_columns:
            metadata.info_column = last_info_col

        metadata.other_info = other_info
        self._metadata = metadata
        if self.metadata.required_fields:
            self.sig_user_input_required.emit(self.metadata.required_fields)

        self.sig_new_metadata.emit(self.metadata)

    def load_data(self) -> None:
        if self._metadata is None:
            return
        suffix = self.metadata.file_format
        file_path = self.metadata.file_path
        separator = Config().data.TextSeparatorChar

        signal_col = self.metadata.signal_column
        info_col = self.metadata.info_column
        columns = [signal_col]
        if info_col != COLUMN_PLACEHOLDER:
            columns.append(info_col)
        row_index_col = "index"
        if row_index_col in columns:
            logger.exception("Column name 'index' is reserved for internal use and cannot be used as a column name.")
            return

        if suffix == ".csv":
            df = pl.read_csv(file_path, columns=columns, row_index_name=row_index_col)
        elif suffix == ".txt":
            df = pl.read_csv(file_path, columns=columns, separator=separator, row_index_name=row_index_col)
        elif suffix == ".tsv":
            df = pl.read_csv(
                file_path,
                columns=columns,
                separator=TextFileSeparator.Tab,
                row_index_name=row_index_col,
            )
        elif suffix == ".feather":
            df = pl.read_ipc(file_path, columns=columns, row_index_name=row_index_col)
        elif suffix == ".edf":
            df = read_edf(Path(file_path), signal_col, info_col)
        elif suffix == ".hdf5":
            raise NotImplementedError("HDF5 file support is not yet implemented.")
        elif suffix == ".xlsx":
            df = pl.read_excel(file_path, columns=columns)
        else:
            raise NotImplementedError(f"Can't read file type: {suffix}")

        self.data_model.set_df(df)
        self._base_section = self.get_base_section()
        self.sections.add_section(self._base_section)
        self.set_active_section(self.base_section_index)
        self.has_data = True
        self.sig_new_data.emit()

    def create_section(self, start: float | int, stop: float | int) -> None:
        if self._metadata is None:
            return
        data = self.base_df.filter(pl.col("index").is_between(start, stop))
        section = Section(data, self.metadata.signal_column, info_column=self.metadata.info_column)
        self.sections.add_section(section)
        self.sig_section_added.emit(section.section_id)

    def delete_section(self, idx: QtCore.QModelIndex) -> None:
        self.sections.remove_section(idx)
        self.set_active_section(self.base_section_index)

    def get_complete_result(self) -> CompleteResult:
        base_df = self.get_base_section().data

        section_results = {s.section_id: s.get_detailed_result() for s in self.sections.editable_sections}

        section_dfs: list[pl.DataFrame] = []
        for s in self.sections.editable_sections:
            section_df = s.data.with_columns(
                pl.col("is_peak").cast(pl.Int8),
                pl.col("is_manual").cast(pl.Int8),
            )
            section_dfs.append(section_df)

        combined_section_df = pl.concat(section_dfs)
        global_df = (
            base_df.lazy()
            .update(combined_section_df.lazy(), on=["index", self.metadata.signal_column], how="full")
            .drop("section_index")
        )

        info_col = self.metadata.info_column
        if info_col == COLUMN_PLACEHOLDER:
            info_col = None

        metadata = SelectedFileMetadata(
            file_name=self.metadata.file_name,
            file_format=str(self.metadata.file_format),
            sampling_rate=self.metadata.sampling_rate,
            name_signal_column=self.metadata.signal_column,
            name_info_column=self.metadata.info_column,
        )

        return CompleteResult(
            metadata=metadata,
            global_dataframe=global_df.collect(),
            section_results=section_results,
        )
