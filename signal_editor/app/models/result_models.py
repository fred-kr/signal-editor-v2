import datetime
import typing as t

import attrs
import numpy as np
import numpy.typing as npt
import polars as pl

from .. import type_defs as _t

if t.TYPE_CHECKING:
    from ..core.section import ManualPeakEdits, SectionID, SectionMetadata


@attrs.define(frozen=True)
class CompactSectionResult:
    peaks_global_index: pl.Series = attrs.field()
    peaks_section_index: pl.Series = attrs.field()
    seconds_since_global_start: pl.Series = attrs.field()
    seconds_since_section_start: pl.Series = attrs.field()
    peak_intervals: pl.Series = attrs.field()
    info_values: pl.Series | None = attrs.field()
    rate_data: pl.DataFrame = attrs.field()

    def to_polars_df(self) -> pl.DataFrame:
        schema = {
            "peaks_global_index": pl.Int32,
            "peaks_section_index": pl.Int32,
            "seconds_since_global_start": pl.Float64,
            "seconds_since_section_start": pl.Float64,
            "peak_intervals": pl.Int32,
        }
        if self.info_values is not None:
            schema["info_values"] = pl.Float64

        return pl.DataFrame({k: getattr(self, k) for k in schema}, schema)

    def to_structured_array(self) -> npt.NDArray[np.void]:
        return self.to_polars_df().to_numpy(structured=True)

    def to_dict(self) -> _t.CompactSectionResultDict:
        out = _t.CompactSectionResultDict(
            peaks_global_index=self.peaks_global_index.to_numpy(),
            peaks_section_index=self.peaks_section_index.to_numpy(),
            seconds_since_global_start=self.seconds_since_global_start.to_numpy(),
            seconds_since_section_start=self.seconds_since_section_start.to_numpy(),
            peak_intervals=self.peak_intervals.to_numpy(),
            rate_data=self.rate_data.to_numpy(structured=True),
        )
        if self.info_values is not None:
            out["info_values"] = self.info_values.to_numpy()
        return out


@attrs.define(repr=True)
class SectionResult:
    peak_data: pl.DataFrame = attrs.field(factory=pl.DataFrame)
    rate_data: pl.DataFrame = attrs.field(factory=pl.DataFrame)
    is_locked: bool = attrs.field(default=False)

    def has_peak_data(self) -> bool:
        return not self.peak_data.is_empty()

    def has_rate_data(self) -> bool:
        return not self.rate_data.is_empty()
    
    def to_dict(self) -> _t.SectionResultDict:
        return _t.SectionResultDict(
            peak_data=self.peak_data.to_numpy(structured=True),
            rate_data=self.rate_data.to_numpy(structured=True),
        )


@attrs.define(frozen=True, repr=True)
class DetailedSectionResult:
    metadata: "SectionMetadata" = attrs.field()
    section_dataframe: pl.DataFrame = attrs.field()
    manual_peak_edits: "ManualPeakEdits" = attrs.field()
    compact_result: CompactSectionResult = attrs.field()
    rate_data: pl.DataFrame = attrs.field()
    rate_per_temperature: pl.DataFrame = attrs.field()

    def to_dict(self) -> _t.DetailedSectionResultDict:
        return _t.DetailedSectionResultDict(
            metadata=self.metadata.to_dict(),
            section_dataframe=self.section_dataframe.to_numpy(structured=True),
            manual_peak_edits=self.manual_peak_edits.to_dict(),
            compact_result=self.compact_result.to_structured_array(),
            rate_data=self.rate_data.to_numpy(structured=True),
            rate_per_temperature=self.rate_per_temperature.to_numpy(structured=True),
        )


@attrs.define(frozen=True, repr=True)
class SelectedFileMetadata:
    file_name: str = attrs.field()
    file_format: str = attrs.field()
    name_signal_column: str = attrs.field()
    sampling_rate: int = attrs.field()
    measured_date: str | datetime.datetime | None = attrs.field(default=None)
    subject_id: str | None = attrs.field(default=None)
    oxygen_condition: str | None = attrs.field(default=None)

    def to_dict(self) -> _t.SelectedFileMetadataDict:
        return _t.SelectedFileMetadataDict(
            file_name=self.file_name,
            file_format=self.file_format,
            name_signal_column=self.name_signal_column,
            sampling_rate=self.sampling_rate,
            measured_date=self.measured_date,
            subject_id=self.subject_id,
            oxygen_condition=self.oxygen_condition,
        )


@attrs.define(frozen=True, repr=True)
class CompleteResult:
    metadata: SelectedFileMetadata = attrs.field()
    global_dataframe: pl.DataFrame = attrs.field()
    section_results: dict["SectionID", DetailedSectionResult] = attrs.field()

    def to_dict(self) -> _t.CompleteResultDict:
        section_results = {k: v.to_dict() for k, v in self.section_results.items()}

        return _t.CompleteResultDict(
            metadata=self.metadata.to_dict(),
            global_dataframe=self.global_dataframe.to_numpy(structured=True),
            section_results=section_results,
        )
