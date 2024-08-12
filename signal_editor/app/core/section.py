import contextlib
import pprint
import re
import typing as t

import attrs
import numpy as np
import numpy.typing as npt
import polars as pl
import polars.selectors as ps
from loguru import logger

from .. import type_defs as _t
from ..config import Config
from ..enum_defs import FilterMethod, PeakDetectionMethod, PreprocessPipeline, RateComputationMethod
from ..models.result_models import CompactSectionResult, DetailedSectionResult, SectionResult
from ..utils import format_long_sequence
from .peak_detection import find_peaks
from .processing import (
    filter_elgendi,
    filter_neurokit2,
    filter_signal,
    signal_rate,
    standardize_signal,
)


@attrs.define
class ProcessingParameters:
    sampling_rate: int = attrs.field()
    processing_pipeline: PreprocessPipeline | None = attrs.field(default=None)
    filter_parameters: list[_t.SignalFilterParameters] = attrs.field(factory=list)
    standardization_parameters: _t.StandardizationParameters | None = attrs.field(default=None)
    peak_detection_method: PeakDetectionMethod | None = attrs.field(default=None)
    peak_detection_method_parameters: _t.PeakDetectionMethodParameters | None = attrs.field(default=None)
    rate_computation_method: RateComputationMethod = attrs.field(default=Config().editing.RateMethod)

    def to_dict(self) -> _t.ProcessingParametersDict:
        return {
            "sampling_rate": self.sampling_rate,
            "processing_pipeline": str(self.processing_pipeline),
            "filter_parameters": self.filter_parameters,
            "standardization_parameters": self.standardization_parameters,
            "peak_detection_method": str(self.peak_detection_method),
            "peak_detection_method_parameters": self.peak_detection_method_parameters,
            "rate_computation_method": str(self.rate_computation_method),
        }

    def reset(self, peaks_only: bool = False) -> None:
        if peaks_only:
            self.peak_detection_method = None
            self.peak_detection_method_parameters = None
            return
        self.processing_pipeline = None
        self.filter_parameters = []
        self.standardization_parameters = None
        self.peak_detection_method = None
        self.peak_detection_method_parameters = None
        self.rate_computation_method = Config().editing.RateMethod

    def __repr__(self) -> str:
        return pprint.pformat(self.to_dict(), indent=2, width=120, underscore_numbers=True)


@attrs.define
class ManualPeakEdits:
    added: list[int] = attrs.field(factory=list)
    removed: list[int] = attrs.field(factory=list)

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
        return sorted(set(self.added) | set(self.removed))

    def to_dict(self) -> _t.ManualPeakEditsDict:
        self.sort_and_deduplicate()
        return _t.ManualPeakEditsDict(
            added=self.added,
            removed=self.removed,
        )


class SectionID(str):
    def __init__(self, value: str) -> None:
        if not re.match(r"^Section_[a-zA-Z0-9]+_[0-9]{3}$", value):
            raise ValueError(f"SectionID must be of the form 'Section_<signal_name>_000', got '{value}'")
        super().__init__()

    @staticmethod
    def default() -> "SectionID":
        return SectionID("Section_DEFAULT_000")

    def pretty_name(self) -> str:
        """UI friendly name for the section"""
        sig_name = self.split("_")[1]
        return f"Section {self[-3:]} ({sig_name.upper()})"


@attrs.define
class SectionMetadata:
    signal_name: str = attrs.field()
    section_id: SectionID = attrs.field()
    global_bounds: tuple[int, int] = attrs.field()
    sampling_rate: int = attrs.field()
    processing_parameters: ProcessingParameters = attrs.field()

    def to_dict(self) -> _t.SectionMetadataDict:
        return _t.SectionMetadataDict(
            signal_name=self.signal_name,
            section_id=self.section_id,
            global_bounds=self.global_bounds,
            sampling_rate=self.sampling_rate,
            processing_parameters=self.processing_parameters.to_dict(),
        )

    def __repr__(self) -> str:
        return pprint.pformat(self.to_dict(), indent=2, width=120, underscore_numbers=True)


class Section:
    __slots__ = (
        "signal_name",
        "processed_signal_name",
        "info_name",
        "section_id",
        "_is_filtered",
        "_is_standardized",
        "_is_processed",
        "data",
        "sampling_rate",
        "global_bounds",
        "_result_data",
        "_rate_is_synced",
        "_processing_parameters",
        "_manual_peak_edits",
    )

    def __init__(self, data: pl.DataFrame, signal_name: str, info_column: str | None = None) -> None:
        self.signal_name = signal_name
        self.processed_signal_name = f"{self.signal_name}_processed"
        self.info_name = info_column
        self.section_id = SectionID.default()
        self._is_filtered: bool = False
        self._is_standardized: bool = False
        self._is_processed: bool = False  # flag to indicate if the section has been processed using a pipeline

        if "section_index" in data.columns:
            data.drop_in_place("section_index")

        self.data = (
            data.with_row_index("section_index")
            .lazy()
            .select(ps.by_name("index", "section_index"), ~ps.by_name("index", "section_index"))
            .set_sorted("index")
            .set_sorted("section_index")
            .with_columns(
                pl.col(signal_name).alias(self.processed_signal_name),
                pl.lit(0, pl.Int8).alias("is_peak"),
                pl.lit(0, pl.Int8).alias("is_manual"),
            )
            .collect()
        )

        self.sampling_rate = Config().internal.LastSamplingRate
        self.global_bounds: tuple[int, int] = (
            self.data.item(0, "index"),
            self.data.item(-1, "index"),
        )

        self._rate_is_synced = False

        self._result_data = SectionResult()

        self._processing_parameters = ProcessingParameters(self.sampling_rate)
        self._manual_peak_edits = ManualPeakEdits()

    @property
    def rate_data(self) -> pl.DataFrame:
        return self._result_data.rate_data

    @rate_data.setter
    def rate_data(self, value: pl.DataFrame) -> None:
        if self._result_data.is_locked:
            logger.warning(
                "Unable to update rate data because the section is locked. Please unlock the section and try again."
            )
            return
        self._result_data.rate_data = value

    @property
    def peak_data(self) -> pl.DataFrame:
        return self._result_data.peak_data

    @peak_data.setter
    def peak_data(self, value: pl.DataFrame) -> None:
        if self._result_data.is_locked:
            logger.warning(
                "Unable to update peak data because the section is locked. Please unlock the section and try again."
            )
            return
        self._result_data.peak_data = value

    @property
    def is_locked(self) -> bool:
        return self._result_data.is_locked

    def set_locked(self, value: bool) -> None:
        self._result_data.is_locked = value

    @property
    def n_filters(self) -> int:
        return len(self._processing_parameters.filter_parameters)

    @property
    def raw_signal(self) -> pl.Series:
        """The raw (unprocessed) signal data for the section."""
        return self.data.get_column(self.signal_name)

    @property
    def processed_signal(self) -> pl.Series:
        """The processed (filtered, standardized, etc) signal data for the section."""
        return self.data.get_column(self.processed_signal_name)

    @property
    def is_filtered(self) -> bool:
        """Flag indicating if the section values were processed using a custom filter."""
        return self._is_filtered

    @property
    def is_standardized(self) -> bool:
        """Flag indicating if the section values were standardized."""
        return self._is_standardized

    @property
    def is_processed(self) -> bool:
        """Flag indicating if the section values were processed using a pipeline."""
        return self._is_processed

    @property
    def peaks_local(self) -> pl.Series:
        """Returns the indices of the peaks in the processed signal."""
        return (
            self.data.lazy()
            .filter(pl.col("is_peak") == 1)
            .select("section_index")
            .collect()
            .get_column("section_index")
        )

    @property
    def peaks_global(self) -> pl.Series:
        """Returns the indices of the peaks relative to the entire signal."""
        return self.data.lazy().filter(pl.col("is_peak") == 1).select("index").collect().get_column("index")

    @property
    def manual_peak_edits(self) -> ManualPeakEdits:
        """Object holding information about manually added/removed peaks."""
        self._manual_peak_edits.sort_and_deduplicate()
        return self._manual_peak_edits

    def update_sampling_rate(self, sampling_rate: int) -> None:
        self.sampling_rate = sampling_rate
        with contextlib.suppress(Exception):
            self.update_rate_data()
        self._processing_parameters.sampling_rate = sampling_rate

    def filter_signal(
        self,
        pipeline: PreprocessPipeline | None = None,
        **kwargs: t.Unpack[_t.SignalFilterParameters],
    ) -> None:
        """
        Filter this section's signal using the specified pipeline / custom filter parameters.

        Parameters
        ----------
        pipeline : PreprocessPipeline | None, optional
            The filter pipeline to apply, by default None

        The keyword arguments are used to apply a custom filter to the signal if pipeline is None:

        lowcut : float | None
            The lower cutoff frequency for the filter, by default None
        highcut : float | None
            The upper cutoff frequency for the filter, by default None
        method : str
            Which filter method to use, see `neurokit2.signal_filter` for more information
        order : int
            The filter order to use
        window_size : int | "default"
            The window size to use for FIR filters
        powerline : int | float
            The powerline frequency to use, only used with method="powerline"
        """
        allow_stacking = Config().editing.FilterStacking
        if self.is_filtered and not allow_stacking:
            logger.warning(
                "Applying filter to raw signal. To apply to already processed signal, enable\n\n'Settings > Preferences > Editing > FilterStacking'."
            )
            sig_data = self.raw_signal.to_numpy(allow_copy=False)
        else:
            sig_data = self.processed_signal.to_numpy(allow_copy=False)
        method = kwargs.get("method", None)
        # filtered = np.empty_like(sig_data)
        # filtered = sig_data.clear(n=len(sig_data))
        filter_params: _t.SignalFilterParameters = {}
        additional_params: _t.SignalFilterParameters | None = None

        if pipeline is None:
            self._processing_parameters.processing_pipeline = pipeline
            if method is None:
                filtered = sig_data

            else:
                filtered, filter_params = filter_signal(sig_data, self.sampling_rate, **kwargs)
                self._is_filtered = True
        elif pipeline == PreprocessPipeline.PPGElgendi:
            filtered = filter_elgendi(sig_data, self.sampling_rate)
            filter_params = {
                "highcut": 8.0,
                "lowcut": 0.5,
                "method": str(FilterMethod.Butterworth),
                "order": 3,
            }
            self._is_processed = True
        elif pipeline == PreprocessPipeline.ECGNeuroKit2:
            pow_line = kwargs.get("powerline", 50)
            filtered = filter_neurokit2(sig_data, self.sampling_rate, powerline=int(pow_line))
            # Applies two filters to the signal: first a highpass butterworth, then a powerline filter
            filter_params = {
                "lowcut": 0.5,
                "method": str(FilterMethod.Butterworth),
                "order": 5,
            }
            additional_params = {
                "method": str(FilterMethod.Powerline),
                "powerline": pow_line,
            }
            self._is_processed = True

        self._processing_parameters.processing_pipeline = pipeline
        self._processing_parameters.filter_parameters.append(filter_params)
        if additional_params is not None:
            self._processing_parameters.filter_parameters.append(additional_params)

        self.data = self.data.with_columns(pl.Series(self.processed_signal_name, filtered))

    def scale_signal(self, **kwargs: t.Unpack[_t.StandardizationParameters]) -> None:
        """
        Standardize this section's signal using the specified parameters. Based on `neurokit2.standardize`.

        Parameters
        ----------
        robust : bool
            If True, uses median absolute deviation (MAD) instead of standard deviation
        window_size : int
            If using rolling standardization, the window size to use
        """
        if self._is_standardized:
            logger.warning("Signal is already standardized. Skipping standardization.")
            return
        window_size = kwargs.get("window_size", None)
        robust = kwargs.get("robust", False)
        if robust and window_size:
            window_size = None

        standardized = standardize_signal(self.processed_signal, robust=robust, window_size=window_size)

        self.data = self.data.with_columns(
            standardized.replace([float("inf"), float("-inf")], None)
            .fill_nan(None)
            .fill_null(strategy="backward")
            .alias(self.processed_signal_name)
        )
        self._is_standardized = True

        self._processing_parameters.standardization_parameters = kwargs

    @logger.catch(message="Peak detection failed. Please check the parameters and try again.")
    def detect_peaks(self, method: PeakDetectionMethod, method_parameters: _t.PeakDetectionMethodParameters) -> None:
        """
        Find peaks in the processed signal using the specified method and parameters.

        Parameters
        ----------
        method : PeakDetectionMethod
            The method to use for peak detection
        method_parameters : PeakDetectionMethodParameters
            The parameters to use for the peak detection method
        """
        peaks = find_peaks(
            self.processed_signal.to_numpy(allow_copy=False),
            self.sampling_rate,
            method,
            method_parameters,
        )

        self._processing_parameters.peak_detection_method = method
        self._processing_parameters.peak_detection_method_parameters = method_parameters

        self.set_peaks(peaks)

    def set_peaks(
        self,
        peaks: npt.NDArray[np.int32],
        update_rate: bool = True,
    ) -> None:
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
            .cast(pl.Int8)
            .alias("is_peak")
        )

        self._manual_peak_edits.clear()
        self._rate_is_synced = False
        if update_rate:
            self.update_rate_data()

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
                .cast(pl.Int8)
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

        self._rate_is_synced = False
        if update_rate and self.peaks_local.len() > 3:
            self.update_rate_data()

    def update_rate_data(self, full_info: bool = False, force: bool = False) -> None:
        """
        Recalculates the signal rate based on the current peaks.

        Parameters
        ----------
        full_info : bool, optional
            If True, calculates summary statistics in addition to the rate, by default False
        force : bool, optional
            If True, recalculates the rate even if the `_rate_is_synced` flag is True, by default False

        """
        if (not force and self._rate_is_synced) or self.is_locked:
            return

        method = Config().editing.RateMethod
        if method == RateComputationMethod.RollingWindow:
            self._calc_rate_rolling(full_info=full_info)
        elif method == RateComputationMethod.RollingWindowNoOverlap:
            self._calc_rate_rolling(sec_new_window_every=60, full_info=full_info)
        elif method == RateComputationMethod.Instantaneous:
            self._calc_rate_instant()
        else:
            raise ValueError(f"Invalid rate computation method: {method}")

        self._rate_is_synced = True

    def _calc_rate_instant(self, peaks: npt.NDArray[np.int32] | pl.Series | None = None, desired_length: int | None = None) -> None:
        if peaks is None:
            peaks = self.peaks_local
        if peaks.shape[0] < 2:
            logger.warning(
                "The currently selected peak detection method finds less than 2 peaks. "
                "Please change the current methods parameters (if available), or use "
                "a different method."
            )
            return
        if desired_length is None:
            desired_length = self.data.height
        inst_rate = signal_rate(peaks, self.sampling_rate, desired_length)

        self.rate_data = pl.DataFrame({"x": pl.int_range(inst_rate.size, dtype=pl.Int32, eager=True), "y": inst_rate})

    def _calc_rate_rolling(
        self,
        grp_col: str = "section_index",
        sec_new_window_every: int = 10,
        sec_window_length: int = 60,
        sec_start_at: int = 0,
        full_info: bool = False,
    ) -> None:
        sampling_rate = self.sampling_rate

        every = sec_new_window_every * sampling_rate
        period = sec_window_length * sampling_rate
        offset = sec_start_at * sampling_rate
        if grp_col not in self.data.columns:
            raise ValueError(f"Column '{grp_col}' must exist in the dataframe")
        if self.data.lazy().select(pl.col(grp_col)).collect_schema().dtypes()[0] not in pl.INTEGER_DTYPES:
            raise ValueError(f"Column '{grp_col}' must be of integer type")
        n_incomplete_windows = period // every

        rr_df = (
            self.data.lazy()
            .sort(grp_col)
            .with_columns(pl.col(grp_col).cast(pl.Int64))
            .group_by_dynamic(
                pl.col(grp_col),
                every=f"{every}i",
                period=f"{period}i",
                offset=f"{offset}i",
            )
        )
        if (self.info_name in self.data.columns) and full_info:
            info_col = self.info_name
            rr_df = rr_df.agg(
                pl.sum("is_peak").alias("y"),
                pl.mean(info_col).name.suffix("_mean"),
                pl.median(info_col).name.suffix("_median"),
                pl.std(info_col).name.suffix("_std"),
                pl.min(info_col).name.suffix("_min"),
                pl.max(info_col).name.suffix("_max"),
                pl.var(info_col).name.suffix("_var"),
            ).collect()[:-n_incomplete_windows]
        else:
            rr_df = rr_df.agg(
                pl.sum("is_peak").alias("y"),
            ).collect()[:-n_incomplete_windows]

        rr_df = rr_df.rename({"section_index": "x"})

        self.rate_data = rr_df.with_columns(pl.col("x").shrink_dtype(), pl.col("y").shrink_dtype()).shrink_to_fit()

    def get_mean_rate_per_temperature(self) -> pl.DataFrame:
        info_col = self.info_name
        return (
            self.rate_data.group_by(pl.col(f"{info_col}_mean"))
            .agg(
                pl.mean("y").alias("rate_mean"),
                pl.median("y").alias("rate_median"),
                pl.std("y").alias("rate_std"),
                pl.min("y").alias("rate_min"),
                pl.max("y").alias("rate_max"),
            )
            .sort(f"{info_col}_mean")
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
            raise RuntimeError(f"Need at least 3 detected peaks to create a result, got {section_peaks.len()}")
        sampling_rate = self.sampling_rate

        global_peaks = self.peaks_global
        section_time = section_peaks / sampling_rate
        global_time = global_peaks / sampling_rate

        peak_intervals = section_peaks.diff().fill_null(0)
        if info_column in self.data.columns:
            info_values = self.data.get_column(info_column).gather(section_peaks)
        else:
            info_values = None

        self.update_rate_data(full_info=True, force=True)

        return CompactSectionResult(
            peaks_global_index=global_peaks,
            peaks_section_index=section_peaks,
            seconds_since_global_start=global_time,
            seconds_since_section_start=section_time,
            peak_intervals=peak_intervals,
            info_values=info_values,
            rate_data=self.rate_data,
        )

    def lock_result(self) -> None:
        self.update_peak_data(include_global=True, include_times=True, include_intervals=True, include_info=True)
        self.update_rate_data(full_info=True, force=True)
        self._result_data.is_locked = True

    def get_detailed_result(self, info_column: str | None = None) -> DetailedSectionResult:
        metadata = self.get_metadata()
        section_df = self.data
        manual_edits = self._manual_peak_edits
        compact_result = self.get_focused_result(info_column)
        rate = self.rate_data
        rate_per_temperature = self.get_mean_rate_per_temperature()

        return DetailedSectionResult(
            metadata=metadata,
            section_dataframe=section_df,
            manual_peak_edits=manual_edits,
            compact_result=compact_result,
            rate_data=rate,
            rate_per_temperature=rate_per_temperature,
        )

    def update_peak_data(
        self,
        include_global: bool = False,
        include_times: bool = False,
        include_intervals: bool = False,
        include_info: bool = False,
    ) -> None:
        section_peaks = self.peaks_local

        if section_peaks.len() < 3:
            raise RuntimeError(f"Need at least 3 detected peaks to create a result, got {section_peaks.len()}")

        peak_df = self.get_peak_pos().rename({"x": "section_index", "y": self.processed_signal_name})

        if include_global:
            peak_df = peak_df.with_columns(self.peaks_global.alias("global_index"))
        if include_times:
            peak_df = peak_df.with_columns(
                (pl.col("section_index") / self.sampling_rate).alias("seconds_since_section_start")
            )
        if include_intervals:
            peak_df = peak_df.with_columns(section_peaks.diff().fill_null(0).alias("peak_intervals"))

        if self.info_name in self.data.columns and include_info:
            peak_df = peak_df.with_columns(
                self.data.get_column(self.info_name).gather(section_peaks).alias(self.info_name)
            )

        self.peak_data = peak_df

    def reset_signal(self) -> None:
        self.data = (
            self.data.lazy()
            .with_columns(
                pl.col(self.signal_name).alias(self.processed_signal_name),
                pl.lit(0, pl.Int8).alias("is_peak"),
                pl.lit(0, pl.Int8).alias("is_manual"),
            )
            .collect()
        )
        self._manual_peak_edits.clear()
        self._is_filtered = False
        self._is_standardized = False
        self._is_processed = False
        self._processing_parameters.reset()

    def reset_peaks(self) -> None:
        self.data = (
            self.data.lazy()
            .with_columns(
                pl.lit(0, pl.Int8).alias("is_peak"),
                pl.lit(0, pl.Int8).alias("is_manual"),
            )
            .collect()
        )
        self._manual_peak_edits.clear()
        self._processing_parameters.reset(peaks_only=True)

    def get_summary(self) -> _t.SectionSummaryDict:
        return {
            "name": self.section_id.pretty_name(),
            "size": self.data.height,
            "sampling_rate": self.sampling_rate,
            "start_index": self.global_bounds[0],
            "end_index": self.global_bounds[1],
            "peak_count": self.peaks_local.len(),
            "processing_parameters": self._processing_parameters.to_dict(),
        }

    def __repr__(self) -> str:
        # Section stats
        metadata = self.get_metadata()
        size = self.data.height
        processing_history: dict[str, str] = {
            f"Run {i}": repr(hist) for i, hist in enumerate(self._processing_parameters.filter_parameters, start=1)
        }
        stat_dict = {
            "Name": self.section_id.pretty_name(),
            "Size": f"{size} samples",
            "Sampling rate": f"{metadata.sampling_rate} Hz",
            "Start Index": str(metadata.global_bounds[0]),
            "End Index": str(metadata.global_bounds[1]),
            "Peak Count": str(self.peaks_local.len()),
            "Processing History": pprint.pformat(processing_history),
        }

        return pprint.pformat(stat_dict, indent=2, width=120, underscore_numbers=True)
