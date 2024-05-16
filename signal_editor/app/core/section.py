import contextlib
import re
import typing as t
from dataclasses import dataclass, field

import numpy as np
import numpy.typing as npt
import polars as pl
import polars.selectors as ps
from loguru import logger
from polars_standardize_series import standardize
from PySide6 import QtCore

from signal_editor.app import type_defs as _t
from signal_editor.app.core.peak_detection import find_peaks
from signal_editor.app.core.processing import (
    filter_elgendi,
    filter_neurokit2,
    filter_signal,
    signal_rate,
)
from signal_editor.app.enum_defs import FilterMethod, PeakDetectionMethod, PreprocessPipeline
from signal_editor.app.models.result_models import CompactSectionResult, DetailedSectionResult
from signal_editor.app.utils import format_long_sequence


@dataclass(slots=True)
class ProcessingParameters:
    sampling_rate: int
    processing_pipeline: PreprocessPipeline = PreprocessPipeline.Custom
    filter_parameters: _t.SignalFilterParameters | None = None
    standardization_parameters: _t.StandardizationParameters | None = None
    peak_detection_method: PeakDetectionMethod = field(init=False)
    peak_detection_method_parameters: _t.PeakDetectionMethodParameters = field(init=False)

    def to_dict(self) -> _t.ProcessingParametersDict:
        return _t.ProcessingParametersDict(
            sampling_rate=self.sampling_rate,
            processing_pipeline=str(self.processing_pipeline),
            filter_parameters=self.filter_parameters,
            standardization_parameters=self.standardization_parameters,
            peak_detection_method=str(self.peak_detection_method),
            peak_detection_method_parameters=self.peak_detection_method_parameters,
        )


@dataclass(slots=True)
class ManualPeakEdits:
    added: list[int] = field(default_factory=list)
    removed: list[int] = field(default_factory=list)

    def __repr__(self) -> str:
        return f"Added Peaks [{len(self.added)}]: {format_long_sequence(self.added)}\nRemoved Peaks [{len(self.removed)}]: {format_long_sequence(self.removed)}"

    def clear(self) -> None:
        self.added.clear()
        self.removed.clear()

    def new_added(self, value: int | t.Sequence[int] | pl.Series) -> None:
        if isinstance(value, int):
            if value in self.removed:
                self.removed.remove(value)
            else:
                self.added.append(value)
        else:
            for v in value:
                if v in self.removed:
                    self.removed.remove(v)
                else:
                    self.added.append(v)

    def new_removed(self, value: int | t.Sequence[int] | pl.Series) -> None:
        if isinstance(value, int):
            if value in self.added:
                self.added.remove(value)
            else:
                self.removed.append(value)
        else:
            for v in value:
                if v in self.added:
                    self.added.remove(v)
                else:
                    self.removed.append(v)

    def sort_and_deduplicate(self) -> None:
        self.added = sorted(set(self.added))
        self.removed = sorted(set(self.removed))

    def get_joined(self) -> list[int]:
        return sorted(set(self.added + self.removed))

    def to_dict(self) -> _t.ManualPeakEditsDict:
        self.sort_and_deduplicate()
        return _t.ManualPeakEditsDict(
            added=self.added,
            removed=self.removed,
        )


class SectionID(str):
    def __init__(self, value: str) -> None:
        if not re.match(r"^Section_[a-zA-Z0-9]+_[0-9]{3}$", value):
            raise ValueError(
                f"SectionID must be of the form 'Section_<signal_name>_000', got '{value}'"
            )
        super().__init__()

    @staticmethod
    def default() -> "SectionID":
        return SectionID("Section_DEFAULT_000")

    def pretty_name(self) -> str:
        """UI friendly name for the section"""
        sig_name = self.split("_")[1]
        return f"Section {self[-3:]} ({sig_name.upper()})"


@dataclass(slots=True)
class SectionMetadata:
    signal_name: str = field()
    section_id: SectionID = field()
    global_bounds: tuple[int, int] = field()
    sampling_rate: int = field()
    processing_parameters: ProcessingParameters = field()

    def to_dict(self) -> _t.SectionMetadataDict:
        return _t.SectionMetadataDict(
            signal_name=self.signal_name,
            section_id=self.section_id,
            global_bounds=self.global_bounds,
            sampling_rate=self.sampling_rate,
            processing_parameters=self.processing_parameters.to_dict(),
        )


class Section:
    def __init__(self, data: pl.DataFrame, signal_name: str) -> None:
        self.signal_name = signal_name
        self.processed_signal_name = f"{self.signal_name}_processed"
        self.section_id = SectionID.default()
        self._is_filtered: bool = False
        self._is_standardized: bool = False

        if "section_index" in data.columns:
            data.drop_in_place("section_index")

        self.data = (
            data.with_row_index("section_index")
            .lazy()
            .select(ps.by_name("index", "section_index"), ~ps.by_name("index", "section_index"))
            .set_sorted(["index", "section_index"])
            .with_columns(
                pl.col(signal_name).alias(self.processed_signal_name),
                pl.lit(0, pl.Int8).alias("is_peak"),
                pl.lit(0, pl.Int8).alias("is_manual"),
                pl.lit(np.nan, pl.Float64).alias("rate_instant"),
            )
            .collect()
        )

        settings = QtCore.QSettings()

        self.sampling_rate: int = settings.value("Data/sampling_rate")  # type: ignore
        self.global_bounds: tuple[int, int] = (
            self.data.item(0, "index"),
            self.data.item(-1, "index"),
        )

        self._processing_parameters = ProcessingParameters(self.sampling_rate)
        self._manual_peak_edits = ManualPeakEdits()

    @property
    def raw_signal(self) -> pl.Series:
        return self.data.get_column(self.signal_name)

    @property
    def processed_signal(self) -> pl.Series:
        return self.data.get_column(self.processed_signal_name)

    @property
    def rate_instant(self) -> npt.NDArray[np.float64]:
        return self.data.get_column("rate_instant").to_numpy(allow_copy=False)

    @property
    def is_filtered(self) -> bool:
        return self._is_filtered

    @property
    def is_standardized(self) -> bool:
        return self._is_standardized

    # @property
    # def rate_rolling(self) -> npt.NDArray[np.float64]:
    #     return self.data.get_column("rate_rolling").to_numpy(allow_copy=False)

    @property
    def peaks_local(self) -> pl.Series:
        return (
            self.data.lazy()
            .filter(pl.col("is_peak") == 1)
            .select("section_index")
            .collect()
            .get_column("section_index")
        )

    @property
    def peaks_global(self) -> pl.Series:
        return (
            self.data.lazy()
            .filter(pl.col("is_peak") == 1)
            .select("index")
            .collect()
            .get_column("index")
        )

    @property
    def manual_peak_edits(self) -> ManualPeakEdits:
        self._manual_peak_edits.sort_and_deduplicate()
        return self._manual_peak_edits

    def update_sampling_rate(self, sampling_rate: int) -> None:
        self.sampling_rate = sampling_rate
        with contextlib.suppress(Exception):
            peaks = self.peaks_local.to_numpy(allow_copy=False)
            self.calculate_rate(peaks)
        self._processing_parameters.sampling_rate = sampling_rate

    def filter_signal(
        self, pipeline: PreprocessPipeline, **kwargs: t.Unpack[_t.SignalFilterParameters]
    ) -> None:
        settings = QtCore.QSettings()
        allow_stacking = settings.value("Editing/allow_stacking_filters", False, type=bool)
        if self.is_filtered and not allow_stacking:
            logger.warning(
                "Applying filter to raw signal. To apply to already processed signal, enable\n\n'Settings > Preferences > Editing > allow_stacking_filters'"
            )
            sig_data = self.raw_signal.to_numpy(allow_copy=False)
        else:
            sig_data = self.processed_signal.to_numpy(allow_copy=False)
        method = kwargs.get("method", FilterMethod.NoFilter)
        filtered = np.empty_like(sig_data)
        filter_params: _t.SignalFilterParameters | None = None

        if pipeline == PreprocessPipeline.Custom:
            if method == FilterMethod.NoFilter:
                filtered = sig_data
                filter_params = None
            else:
                filtered, filter_params = filter_signal(sig_data, self.sampling_rate, **kwargs)
        elif pipeline == PreprocessPipeline.PPGElgendi:
            filtered = filter_elgendi(sig_data, self.sampling_rate)
            filter_params = {
                "highcut": 8.0,
                "lowcut": 0.5,
                "method": str(FilterMethod.Butterworth),
                "order": 3,
                "window_size": "default",
                "powerline": 50,
            }
        elif pipeline == PreprocessPipeline.ECGNeuroKit2:
            pow_line = kwargs.get("powerline", 50)
            filtered = filter_neurokit2(sig_data, self.sampling_rate, powerline=pow_line)
            filter_params = {
                "highcut": None,
                "lowcut": 0.5,
                "method": str(FilterMethod.Butterworth),
                "order": 5,
                "window_size": "default",
                "powerline": pow_line,
            }

        self._processing_parameters.processing_pipeline = pipeline
        self._processing_parameters.filter_parameters = filter_params
        self.data = self.data.with_columns(pl.Series(self.processed_signal_name, filtered))
        self._is_filtered = True

    def scale_signal(self, **kwargs: t.Unpack[_t.StandardizationParameters]) -> None:
        if self._is_standardized:
            logger.warning("Signal is already standardized. No action taken.")
            return
        window_size = kwargs.get("window_size", None)
        robust = kwargs.get("robust", False)
        if robust and window_size:
            window_size = None

        self.data = self.data.with_columns(
            standardize(self.processed_signal_name, robust=robust, window_size=window_size)
            .replace([float("inf"), float("-inf")], None)
            .fill_nan(None)
            .backward_fill()
            .alias(self.processed_signal_name)
        )
        self._is_standardized = True

        self._processing_parameters.standardization_parameters = kwargs

    def detect_peaks(
        self, method: PeakDetectionMethod, method_parameters: _t.PeakDetectionMethodParameters
    ) -> None:
        peaks = find_peaks(
            self.processed_signal.to_numpy(allow_copy=False),
            self.sampling_rate,
            method,
            method_parameters,
        )

        self._processing_parameters.peak_detection_method = method
        self._processing_parameters.peak_detection_method_parameters = method_parameters

        self.set_peaks(peaks)

    def set_peaks(self, peaks: npt.NDArray[np.int32], update_rate: bool = True) -> None:
        """
        Sets the `is_peak` column in `self.data` to 1 at the indices provided in `peaks`, and to 0
        everywhere else.

        Parameters
        ----------
        peaks : ndarray
            A 1D array of integers representing the indices of the peaks in the processed signal.
        update_rate : bool
            Whether to recalculate the signal rate based on the new peaks. Defaults to True.
        """
        peaks = peaks[peaks >= 0]

        pl_peaks = pl.Series("", peaks, pl.Int32)

        self.data = self.data.with_columns(
            pl.when(pl.col("section_index").is_in(pl_peaks))
            .then(pl.lit(1))
            .otherwise(pl.lit(0))
            .alias("is_peak")
        )

        self._manual_peak_edits.clear()
        if update_rate:
            self.calculate_rate(peaks, desired_length=self.data.height)

    def update_peaks(
        self,
        action: _t.UpdatePeaksAction,
        peaks: npt.NDArray[np.int32],
        update_rate: bool = True,
    ) -> None:
        """
        Updates the `is_peak` column in `self.data` at the given indices according to the provided
        action, while keeping the rest of the column values the same.

        Parameters
        ----------
        action : {"add", "remove"}
            How the peaks should be updated:
            - "add" : Set the `is_peak` column to 1 at the indices provided in `peaks`.
            - "remove" : Set the `is_peak` column to 0 at the indices provided in `peaks`.

        peaks : ndarray
            A 1D array of integers representing the indices of the peaks in the processed signal.
        update_rate : bool
            Whether to recalculate the signal rate based on the new peaks. Defaults to True.

        """
        pl_peaks = pl.Series("peaks", peaks, pl.Int32)
        then_value = 1 if action in ["a", "add"] else 0

        updated_data = (
            self.data.lazy()
            .select(
                pl.when(pl.col("section_index").is_in(pl_peaks))
                .then(pl.lit(then_value))
                .otherwise(pl.col("is_peak"))
                .alias("is_peak")
            )
            .collect()
            .get_column("is_peak")
        )

        changed_indices = pl.arg_where(updated_data != self.data.get_column("is_peak"), eager=True)

        self.data = self.data.with_columns(is_peak=updated_data)

        if action == "add":
            self._manual_peak_edits.new_added(changed_indices)
        else:
            self._manual_peak_edits.new_removed(changed_indices)

        if update_rate and self.peaks_local.len() > 3:
            self.calculate_rate(
                self.peaks_local.to_numpy(allow_copy=False), desired_length=self.data.height
            )

    def calculate_rate(
        self, peaks: npt.NDArray[np.int32] | None = None, desired_length: int | None = None
    ) -> None:
        if peaks is None:
            peaks = self.peaks_local.to_numpy(allow_copy=False)
        if peaks.shape[0] < 2:
            logger.warning(
                "The currently selected peak detection method finds less than 2 peaks. "
                "Please change the current methods parameters (if available), or use "
                "a different method."
            )
            self.data = (
                self.data.lazy().with_columns(pl.lit(np.nan).alias("rate_instant")).collect()
            )
            return
        if desired_length is None:
            desired_length = self.data.height
        inst_rate = signal_rate(peaks, self.sampling_rate, desired_length)
        self.data = self.data.with_columns(
            pl.Series("rate_instant", inst_rate).alias("rate_instant")
        )

    def calculate_rolling_rate(
        self,
        grp_col: str = "section_index",
        sec_new_window_every: int = 10,
        sec_window_length: int = 60,
        sec_start_at: int = 0,
    ) -> pl.Series:
        sampling_rate = self.sampling_rate

        every = sec_new_window_every * sampling_rate
        period = sec_window_length * sampling_rate
        offset = sec_start_at * sampling_rate
        if grp_col not in self.data.columns:
            raise ValueError(f"Column '{grp_col}' must exist in the dataframe")
        if self.data.lazy().select(pl.col(grp_col)).dtypes[0] not in pl.INTEGER_DTYPES:
            raise ValueError(f"Column '{grp_col}' must be of integer type")

        remove_tail_count = period // every

        return (
            self.data.sort(grp_col)
            .with_columns(pl.col(grp_col).cast(pl.Int64))
            .group_by_dynamic(
                pl.col(grp_col),
                every=f"{every}i",
                period=f"{period}i",
                offset=f"{offset}i",
            )
            .agg(
                pl.len().alias("n_peaks_in_window"),
            )[:-remove_tail_count]
            .get_column("n_peaks_in_window")
        )

    def _add_manual_peak_edits_column(self) -> None:
        pl_added = pl.Series("added", self._manual_peak_edits.added, pl.Int32)
        pl_removed = pl.Series("removed", self._manual_peak_edits.removed, pl.Int32)

        self.data = (
            self.data.lazy()
            .with_columns(
                pl.when(pl.col("section_index").is_in(pl_added))
                .then(pl.lit(1))
                .when(pl.col("section_index").is_in(pl_removed))
                .then(pl.lit(-1))
                .otherwise(pl.lit(0))
                .shrink_dtype()
                .alias("is_manual")
            )
            .collect()
        )

    def get_metadata(self) -> SectionMetadata:
        return SectionMetadata(
            signal_name=self.signal_name,
            section_id=self.section_id,
            sampling_rate=self.sampling_rate,
            global_bounds=self.global_bounds,
            processing_parameters=self._processing_parameters,
        )

    def get_peak_pos(self) -> pl.DataFrame:
        return (
            self.data.lazy()
            .filter(pl.col("is_peak") == 1)
            .select(
                pl.col("section_index").alias("x"),
                pl.col(self.processed_signal_name).alias("y"),
            )
            .collect()
        )

    def get_focused_result(self, info_column: str | None = None) -> CompactSectionResult:
        section_peaks = self.peaks_local

        if section_peaks.len() < 3:
            raise RuntimeError(
                f"Need at least 3 detected peaks to create a result, got {section_peaks.len()}"
            )
        sampling_rate = self.sampling_rate

        global_peaks = self.peaks_global
        section_time = section_peaks / sampling_rate
        global_time = global_peaks / sampling_rate

        peak_intervals = section_peaks.diff().fill_null(0)
        if info_column in self.data.columns:
            info_values = self.data.get_column("temperature").gather(section_peaks)
        else:
            info_values = None

        instantaneous_rate = pl.Series(
            "instantaneous_rate",
            signal_rate(section_peaks.to_numpy(allow_copy=False), sampling_rate),
            pl.Float64,
        )
        # roll_window = self.calculate_rolling_rate("section_index")

        return CompactSectionResult(
            peaks_global_index=global_peaks,
            peaks_section_index=section_peaks,
            seconds_since_global_start=global_time,
            seconds_since_section_start=section_time,
            peak_intervals=peak_intervals,
            rate_instant=instantaneous_rate,
            info_values=info_values,
        )

    def get_detailed_result(self, info_column: str | None = None) -> DetailedSectionResult:
        metadata = self.get_metadata()
        section_df = self.data
        manual_edits = self._manual_peak_edits
        compact_result = self.get_focused_result(info_column)
        instant_rate = self.rate_instant
        rolling_rate = self.calculate_rolling_rate().to_numpy()

        return DetailedSectionResult(
            metadata=metadata,
            section_dataframe=section_df,
            manual_peak_edits=manual_edits,
            compact_result=compact_result,
            rate_instant=instant_rate,
            rate_rolling=rolling_rate,
        )

    def reset_signal(self) -> None:
        self.data = (
            self.data.lazy()
            .with_columns(
                pl.col(self.signal_name).alias(self.processed_signal_name),
                pl.lit(0, pl.Int8).alias("is_peak"),
                pl.lit(0, pl.Int8).alias("is_manual"),
                pl.lit(np.nan, pl.Float64).alias("rate_instant"),
                # pl.lit(np.nan, pl.Float64).alias("rate_rolling"),
            )
            .collect()
        )
        self._manual_peak_edits.clear()
        self._is_filtered = False
        self._is_standardized = False

    def reset_peaks(self) -> None:
        self.data = (
            self.data.lazy()
            .with_columns(
                pl.lit(0, pl.Int8).alias("is_peak"),
                pl.lit(0, pl.Int8).alias("is_manual"),
                pl.lit(np.nan, pl.Float64).alias("rate_instant"),
                # pl.lit(np.nan, pl.Float64).alias("rate_rolling"),
            )
            .collect()
        )
        self._manual_peak_edits.clear()
