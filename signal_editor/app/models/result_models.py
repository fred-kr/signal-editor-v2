import typing as t
from dataclasses import dataclass, field

import numpy as np
import numpy.typing as npt
import polars as pl

from .. import type_defs as _t

if t.TYPE_CHECKING:
    from ..controllers.data_controller import LoadedFileMetadata
    from ..core.section import ManualPeakEdits, SectionID, SectionMetadata


@dataclass(slots=True, frozen=True)
class CompactSectionResult:
    peaks_global_index: pl.Series = field()
    peaks_section_index: pl.Series = field()
    seconds_since_global_start: pl.Series = field()
    seconds_since_section_start: pl.Series = field()
    peak_intervals: pl.Series = field()
    temperature: pl.Series = field()
    instantaneous_rate: pl.Series = field()
    rolling_rate: pl.Series = field()

    def to_polars_df(self) -> pl.DataFrame:
        schema = {
            "peaks_global_index": pl.Int32,
            "peaks_section_index": pl.Int32,
            "seconds_since_global_start": pl.Float64,
            "seconds_since_section_start": pl.Float64,
            "peak_intervals": pl.Int32,
            "temperature": pl.Float64,
            "instantaneous_rate": pl.Float64,
            "rolling_rate": pl.Float64,
        }
        return pl.DataFrame({k: getattr(self, k) for k in schema}, schema)

    def to_structured_array(self) -> npt.NDArray[np.void]:
        return self.to_polars_df().to_numpy(structured=True)

    def to_dict(self) -> _t.CompactSectionResultDict:
        return _t.CompactSectionResultDict(
            peaks_global_index=self.peaks_global_index.to_numpy(),
            peaks_section_index=self.peaks_section_index.to_numpy(),
            seconds_since_global_start=self.seconds_since_global_start.to_numpy(),
            seconds_since_section_start=self.seconds_since_section_start.to_numpy(),
            peak_intervals=self.peak_intervals.to_numpy(),
            temperature=self.temperature.to_numpy(),
            instantaneous_rate=self.instantaneous_rate.to_numpy(),
            rolling_rate=self.rolling_rate.to_numpy(),
        )


@dataclass(slots=True, frozen=True, repr=True)
class DetailedSectionResult:
    metadata: "SectionMetadata" = field()
    section_dataframe: pl.DataFrame = field()
    manual_peak_edits: "ManualPeakEdits" = field()
    compact_result: CompactSectionResult = field()
    rate_instantaneous: npt.NDArray[np.float64] = field()
    rate_rolling_window: npt.NDArray[np.float64] = field()

    def to_dict(self) -> _t.DetailedSectionResultDict:
        return _t.DetailedSectionResultDict(
            metadata=self.metadata.to_dict(),
            section_dataframe=self.section_dataframe.to_numpy(structured=True),
            manual_peak_edits=self.manual_peak_edits.to_dict(),
            compact_result=self.compact_result.to_dict(),
            rate_instantaneous=self.rate_instantaneous,
            rate_rolling_window=self.rate_rolling_window,
        )


@dataclass(slots=True, frozen=True, repr=True)
class CompleteResult:
    metadata: "LoadedFileMetadata" = field()
    global_dataframe: pl.DataFrame = field()
    section_results: dict["SectionID", DetailedSectionResult] = field()

    def to_dict(self) -> _t.CompleteResultDict:
        section_results = {k: v.to_dict() for k, v in self.section_results.items()}

        return _t.CompleteResultDict(
            metadata=self.metadata.to_dict(),
            global_dataframe=self.global_dataframe.to_numpy(structured=True),
            section_results=section_results,
        )
