import typing as t

import attrs
import polars as pl

from .. import type_defs as _t

if t.TYPE_CHECKING:
    from ..core.section import ManualPeakEdits, SectionID, SectionMetadata


@attrs.define(repr=True)
class SectionResult:
    """
    Stores the detected peaks along with the computed rate data for a single section. Created for each new section.
    """
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
    """
    Class containing detailed information about a section. Created when a complete result is requested by the user.
    """
    metadata: "SectionMetadata" = attrs.field()
    section_dataframe: pl.DataFrame = attrs.field()
    manual_peak_edits: "ManualPeakEdits" = attrs.field()
    section_result: SectionResult = attrs.field()
    rate_per_temperature: pl.DataFrame = attrs.field()

    def to_dict(self) -> _t.DetailedSectionResultDict:
        return _t.DetailedSectionResultDict(
            metadata=self.metadata.to_dict(),
            section_dataframe=self.section_dataframe.to_numpy(structured=True),
            manual_peak_edits=self.manual_peak_edits.to_dict(),
            section_result=self.section_result.to_dict(),
            rate_per_temperature=self.rate_per_temperature.to_numpy(structured=True),
        )


@attrs.define(frozen=True, repr=True)
class SelectedFileMetadata:
    file_name: str = attrs.field()
    file_format: str = attrs.field()
    sampling_rate: int = attrs.field()
    name_signal_column: str = attrs.field()
    name_info_column: str | None = attrs.field(default=None)

    def to_dict(self) -> _t.SelectedFileMetadataDict:
        return _t.SelectedFileMetadataDict(
            file_name=self.file_name,
            file_format=self.file_format,
            sampling_rate=self.sampling_rate,
            name_signal_column=self.name_signal_column,
            name_info_column=self.name_info_column,
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
