import typing as t
from pathlib import Path

import polars as pl
from PySide6 import QtCore

from .. import type_defs as _t
from ..core.file_io import read_edf
from ..core.section import Section, SectionID
from ..enum_defs import TextFileSeparator
from ..models.data_table import DataTableModel
from ..models.metadata import (
    EDFFileMetadata,
    ExcelFileMetadata,
    FeatherFileMetadata,
    TextFileMetadata,
)


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


def check_string_for_non_ascii(string: str) -> tuple[bool, list[tuple[str, int]]]:
    """
    Checks a file name for possible non-ASCII characters.

    Parameters
    ----------
    string : str
        The string to check.

    Returns
    -------
    tuple[bool, list[tuple[str, int]]
        A tuple containing a boolean indicating whether non-ASCII characters were found and a list of tuples containing the detected non-ASCII characters and their positions in the input string.
    """
    non_ascii_chars = [(char, idx) for idx, char in enumerate(string) if ord(char) > 127]
    return bool(non_ascii_chars), non_ascii_chars


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

    SUPPORTED_FILE_FORMATS = frozenset([".edf", ".xlsx", ".feather", ".csv", ".txt", ".tsv"])

    def __init__(self, parent: QtCore.QObject | None = None) -> None:
        super().__init__(parent)

        settings = QtCore.QSettings()
        self._sampling_rate = int(settings.value("Data/sampling_rate"))  # type: ignore

        self._base_df: pl.DataFrame | None = None
        self.base_df_model = DataTableModel(self)
        self._working_df: pl.DataFrame | None = None
        self.working_df_model = DataTableModel(self)

        self._metadata: (
            TextFileMetadata | ExcelFileMetadata | EDFFileMetadata | FeatherFileMetadata | None
        ) = None

        self._sections: SectionContainer = SectionContainer()
        self._active_section: Section | None = None
        self._base_section: Section | None = None

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

    @property
    def metadata(
        self,
    ) -> _t.Metadata:
        if self._metadata is None:
            raise MissingDataError("No metadata available. Load a valid file to get metadata.")
        return self._metadata

    def update_metadata(self, metadata_dict: _t.MetadataUpdateDict) -> None:
        if self._metadata is None:
            return
        if metadata_dict["sampling_rate"] > 0:
            self.metadata.sampling_rate = metadata_dict["sampling_rate"]
        if metadata_dict["signal_column"] != "" and metadata_dict["signal_column_index"] != -1:
            self.metadata.signal_column = metadata_dict["signal_column"]
        self.metadata.info_column = metadata_dict["info_column"]

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

        match file_path.suffix:
            case ".edf":
                self._metadata = EDFFileMetadata(file_path)
            # case ".xlsx" | ".xls":
            # self._metadata = ExcelFileMetadata(file_path)
            case ".feather":
                self._metadata = FeatherFileMetadata(file_path)
            case ".csv" | ".txt" | ".tsv":
                self._metadata = TextFileMetadata(file_path)
            case _:
                raise ValueError(
                    f"Unsupported file format: {file_path.suffix}. Please select a valid file format."
                )

        # show_non_ascii_warning = False
        # non_ascii_characters: list[tuple[int, tuple[str, list[tuple[str, int]]]]] = []
        # for i, col in enumerate(self.metadata.column_names):
        #     has_non_ascii, non_ascii_chars = check_string_for_non_ascii(col)
        #     if has_non_ascii:
        #         show_non_ascii_warning = True
        #         col_name = self.metadata.column_names[i]

        #         non_ascii_characters.append((i, (col_name, non_ascii_chars)))

        # if show_non_ascii_warning:
        #     self.sig_non_ascii_in_file_name.emit(
        #         non_ascii_characters, self._metadata.file_format == ".edf"
        #     )

        if self.metadata.required_fields:
            self.sig_user_input_required.emit(self.metadata.required_fields)

        self.base_df_model.set_metadata(self.metadata)
        self.sig_new_metadata.emit(self.metadata)

    def read_file(self, **kwargs: t.Unpack[_t.ReadFileKwargs]) -> None:
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
        if info_col is not None:
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
            # case ".xlsx":
            # self._base_df = pl.read_excel(file_path)
            case ".feather":
                self._base_df = pl.read_ipc(file_path, columns=columns)
            case ".edf":
                if info_col is None:
                    info_col = "temperature"
                self._base_df = read_edf(
                    file_path, data_channel=signal_col, temperature_channel=info_col
                )
            case _:
                raise NotImplementedError(f"Cant read file type: {suffix}")

        self.base_df_model.set_dataframe(self._base_df, signal_col, info_col=info_col)
        self.sig_new_data.emit()
