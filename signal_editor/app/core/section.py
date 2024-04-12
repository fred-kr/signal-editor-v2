import contextlib
import re
import typing as t

import attrs
import numpy as np
import numpy.typing as npt
import polars as pl
import polars.selectors as ps
from PySide6 import QtCore

from .. import enum_defs as _e
from .. import type_defs as _t
from ..models.result_models import CompactSectionResult
from .peak_detection import find_peaks
from .processing import filter_elgendi, filter_neurokit2, filter_signal, scale_signal, signal_rate


def _format_long_sequence(seq: t.Sequence[int | float]) -> str:
    if len(seq) > 10:
        return f"[{', '.join(map(str, seq[:5]))}, ..., {', '.join(map(str, seq[-5:]))}]"
    else:
        return str(seq)


@attrs.define
class ProcessingParameters:
    sampling_rate: int
    processing_pipeline: _e.PreprocessPipeline = _e.PreprocessPipeline.Custom
    filter_parameters: _t.SignalFilterParameters | None = None
    standardization_parameters: _t.StandardizationParameters | None = None
    peak_detection_method: _e.PeakDetectionMethod = _e.PeakDetectionMethod.PPGElgendi
    peak_detection_method_parameters: _t.PeakDetectionMethodParameters = {}

    def to_dict(self) -> _t.ProcessingParametersDict:
        return _t.ProcessingParametersDict(
            sampling_rate=self.sampling_rate,
            processing_pipeline=self.processing_pipeline,
            filter_parameters=self.filter_parameters,
            standardization_parameters=self.standardization_parameters,
            peak_detection_method=self.peak_detection_method,
            peak_detection_method_parameters=self.peak_detection_method_parameters,
        )


@attrs.define
class ManualPeakEdits:
    added: list[int] = attrs.field(factory=list)
    removed: list[int] = attrs.field(factory=list)

    def __repr__(self) -> str:
        return f"Added Peaks [{len(self.added)}]: {_format_long_sequence(self.added)}\nRemoved Peaks [{len(self.removed)}]: {_format_long_sequence(self.removed)}"

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
    def __init__(self, value: str):
        if not re.match(r"^Section_[a-zA-Z0-9]+_[0-9]{3}$", value):
            raise ValueError(
                f"SectionID must be of the form 'Section_<signal_name>_000', got '{value}'"
            )
        super().__init__()


@attrs.define
class SectionMetadata:
    signal_name: str
    section_id: SectionID
    global_bounds: tuple[int, int]
    sampling_rate: int
    processing_parameters: ProcessingParameters

    def to_dict(self) -> _t.SectionMetadataDict:
        return _t.SectionMetadataDict(
            signal_name=self.signal_name,
            section_id=self.section_id,
            global_bounds=self.global_bounds,
            sampling_rate=self.sampling_rate,
            processing_parameters=self.processing_parameters.to_dict(),
        )


class Section:
    _id_counter: t.ClassVar[int] = 0
    _base_created: t.ClassVar[bool] = False

    @classmethod
    def _get_next_id(cls) -> int:
        cls._id_counter += 1
        return cls._id_counter

    @classmethod
    def reset_id_counter(cls) -> None:
        cls._id_counter = 0
        cls._base_created = False

    @classmethod
    def get_id_counter(cls) -> int:
        return cls._id_counter

    def __init__(self, data: pl.DataFrame, signal_name: str) -> None:
        self.signal_name = signal_name
        self.processed_signal_name = f"{self.signal_name}_processed"

        if not self.__class__._base_created:
            self.section_id = SectionID(f"Section_{self.signal_name}_000")
            self.__class__._base_created = True
        else:
            self.section_id = self._generate_id()

        if "section_index" in data.columns:
            data.drop_in_place("section_index")

        self.data = (
            data.with_row_index("section_index")
            .lazy()
            .select(ps.by_name("index", "section_index"), ~ps.by_name("index", "section_index"))
            .set_sorted(["index", "section_index"])
            .with_columns(pl.col(signal_name).alias(self.processed_signal_name), pl.lit(0).alias("is_peak"), pl.lit(0).alias("is_manual"))
            .collect()
        )

        settings = QtCore.QSettings()

        self.sampling_rate: int = settings.value("Data/sampling_rate")  # type: ignore
        self.global_bounds: tuple[int, int] = (
            self.data.item(0, "index"),
            self.data.item(-1, "index"),
        )
        self.rate_instantaneous = np.empty(0, dtype=np.float64)
        self.rate_instantaneous_interpolated = np.empty(self.data.height, dtype=np.float64)
        self.rate_rolling_window = pl.Series("rate_rolling_window", [], pl.Float64)

        self._processing_parameters = ProcessingParameters(self.sampling_rate)  # type: ignore
        self._manual_peak_edits = ManualPeakEdits()

    def _generate_id(self) -> SectionID:
        prefix = f"Section_{self.signal_name}"
        number = self._get_next_id()
        return SectionID(f"{prefix}_{number:03}")

    @property
    def raw_signal(self) -> pl.Series:
        return self.data.get_column(self.signal_name)

    @property
    def processed_signal(self) -> pl.Series:
        return self.data.get_column(self.processed_signal_name)

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
            peaks = self.peaks_local.to_numpy(zero_copy_only=True)
            self.calculate_rate(peaks)

    def filter_signal(
        self, pipeline: _e.PreprocessPipeline, **kwargs: t.Unpack[_t.SignalFilterParameters]
    ) -> None:
        method = kwargs.get("method", _e.FilterMethod.NoFilter)
        raw_data = self.raw_signal.to_numpy(zero_copy_only=True)
        filtered = np.empty_like(raw_data)
        filter_params: _t.SignalFilterParameters | None = None

        match pipeline:
            case _e.PreprocessPipeline.Custom:
                if method == _e.FilterMethod.NoFilter:
                    filtered = raw_data
                    filter_params = None
                else:
                    filtered, filter_params = filter_signal(raw_data, self.sampling_rate, **kwargs)
            case _e.PreprocessPipeline.PPGElgendi:
                filtered = filter_elgendi(raw_data, self.sampling_rate)
                filter_params = {
                    "highcut": 8.0,
                    "lowcut": 0.5,
                    "method": _e.FilterMethod.Butterworth,
                    "order": 3,
                    "window_size": "default",
                    "powerline": 50,
                }
            case _e.PreprocessPipeline.ECGNeuroKit2:
                pow_line = kwargs.get("powerline", 50)
                filtered = filter_neurokit2(raw_data, self.sampling_rate, powerline=pow_line)
                filter_params = {
                    "highcut": None,
                    "lowcut": 0.5,
                    "method": _e.FilterMethod.Butterworth,
                    "order": 5,
                    "window_size": "default",
                    "powerline": pow_line,
                }

        self._processing_parameters.processing_pipeline = pipeline
        self._processing_parameters.filter_parameters = filter_params
        self.data = self.data.with_columns(
            pl.Series(self.processed_signal_name, filtered, dtype=pl.Float64)
        )

    def scale_signal(self, **kwargs: t.Unpack[_t.StandardizationParameters]) -> None:
        robust = kwargs.get("robust", False)
        window_size = kwargs.get("window_size", None)

        scaled = scale_signal(self.processed_signal, robust, window_size)

        self._processing_parameters.standardization_parameters = {**kwargs}
        self.data = self.data.with_columns(scaled.alias(self.processed_signal_name))

    def detect_peaks(
        self, method: _e.PeakDetectionMethod, method_parameters: _t.PeakDetectionMethodParameters
    ) -> None:
        peaks = find_peaks(
            self.processed_signal.to_numpy(zero_copy_only=True),
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
        peaks : npt.NDArray[np.int32]
            A 1D array of integers representing the indices of the peaks in the processed signal.
        """
        # Remove any negative peak indices
        peaks = peaks[peaks >= 0]

        pl_peaks = pl.Series("peaks", peaks, pl.Int32)

        self.data = self.data.with_columns(
            pl.when(pl.col("section_index").is_in(pl_peaks))
            .then(pl.lit(1))
            .otherwise(pl.lit(0))
            .shrink_dtype()
            .alias("is_peak")
        )

        self._manual_peak_edits.clear()
        if update_rate:
            self.calculate_rate(peaks)

    def update_peaks(
        self,
        action: t.Literal["a", "r", "add", "remove"],
        peaks: t.Sequence[int] | npt.NDArray[np.int32],
    ) -> None:
        """
        Updates the `is_peak` column in `self.data` at the given indices according to the provided
        action, while keeping the rest of the column values the same.

        Parameters
        ----------
        action : t.Literal["a", "r", "add", "remove"]
            The action to perform. Must be one of "a"/"add" for adding peaks or "r"/"remove" for
            removing peaks.
        peaks : t.Sequence[int] | npt.NDArray[np.int32]
            A 1D array of integers representing the indices of the peaks in the processed signal.
        """
        pl_peaks = pl.Series("peaks", peaks, pl.Int32)
        then_value = 1 if action == "add" else 0

        updated_data = (
            self.data.lazy()
            .select(
                pl.when(pl.col("section_index").is_in(pl_peaks))
                .then(pl.lit(then_value))
                .otherwise(pl.col("is_peak"))
                .shrink_dtype()
                .alias("is_peak")
            )
            .collect()
            .get_column("is_peak")
        )

        changed_indices = pl.arg_where(updated_data != self.data.get_column("is_peak"), eager=True)

        self.data.replace("is_peak", updated_data)

        if action == "add":
            self._manual_peak_edits.new_added(changed_indices)
        else:
            self._manual_peak_edits.new_removed(changed_indices)

    def calculate_rate(
        self, peaks: npt.NDArray[np.int32], desired_length: int | None = None
    ) -> None:
        self.rate_instantaneous_interpolated = signal_rate(
            peaks, self.sampling_rate, desired_length
        )

    def calculate_rolling_rate(
        self,
        grp_col: str,
        sec_new_window_every: int = 10,
        sec_window_length: int = 60,
        sec_start_at: int = 0,
    ) -> None:
        sampling_rate = self.sampling_rate

        every = sec_new_window_every * sampling_rate
        period = sec_window_length * sampling_rate
        offset = sec_start_at * sampling_rate
        if grp_col not in self.data.columns:
            raise ValueError(f"Column '{grp_col}' must exist in the dataframe")
        if self.data.lazy().select(pl.col(grp_col)).dtypes[0] not in pl.INTEGER_DTYPES:
            raise ValueError(f"Column '{grp_col}' must be of integer type")

        remove_tail_count = period // every

        self.rate_rolling_window = (
            self.data.sort(grp_col)
            .with_columns(pl.col(grp_col).cast(pl.Int64))
            .groupby_dynamic(
                pl.col(grp_col),
                include_boundaries=True,
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

    def get_section_metadata(self) -> SectionMetadata:
        return SectionMetadata(
            signal_name=self.signal_name,
            section_id=self.section_id,
            sampling_rate=self.sampling_rate,
            global_bounds=self.global_bounds,
            processing_parameters=self._processing_parameters,
        )

    def get_peak_xy(self) -> tuple[npt.NDArray[np.int32], npt.NDArray[np.float64]]:
        peaks = self.peaks_local.to_numpy(zero_copy_only=True)

        return peaks, self.processed_signal.gather(peaks).to_numpy(zero_copy_only=True)

    def get_focused_result(self) -> CompactSectionResult:
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
        temperature = self.data.get_column("temperature").gather(section_peaks)

        instantaneous_rate = pl.Series(
            "instantaneous_rate", signal_rate(section_peaks, sampling_rate), pl.Float64
        )
        self.calculate_rolling_rate("section_index")

        return CompactSectionResult(
            peaks_global_index=global_peaks,
            peaks_section_index=section_peaks,
            seconds_since_global_start=global_time,
            seconds_since_section_start=section_time,
            peak_intervals=peak_intervals,
            instantaneous_rate=instantaneous_rate,
            rolling_rate=self.rate_rolling_window,
            temperature=temperature,
        )
