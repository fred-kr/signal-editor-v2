import datetime
import typing as t
from pathlib import Path

import numpy as np
import numpy.typing as npt

from .enum_defs import (
    FilterMethod,
    NK2ECGPeakDetectionMethod,
    PointSymbols,
    StandardizationMethod,
    WFDBPeakDirection,
    SVGColors,
    RateComputationMethod,
)

if t.TYPE_CHECKING:
    import mne
    from PySide6 import QtCore, QtGui

    from ..app.controllers.data_controller import (
        TextFileSeparator,
    )
    from ..app.core.section import SectionID


PGColor = t.Union[str, int, float, tuple[int, int, int], tuple[int, int, int, int], "QtGui.QColor", SVGColors]


class PGPenKwargs(t.TypedDict, total=False):
    color: PGColor
    width: float
    cosmetic: bool
    dash: t.Sequence[float] | None
    style: t.Union["QtCore.Qt.PenStyle", None]
    hsv: tuple[float, float, float, float]


class PGBrushKwargs(t.TypedDict, total=False):
    color: PGColor


PGPen = t.Union[PGColor, "QtGui.QPen", PGPenKwargs, None]
PGBrush = t.Union[PGColor, "QtGui.QBrush", PGBrushKwargs, None]

PGPointSymbols = t.Union[PointSymbols, "QtGui.QPainterPath"]

UpdatePeaksAction = t.Literal["add", "remove"]


class FindPeaksKwargs(t.TypedDict, total=False):
    min_peak_distance: int
    n_std: float


class MetadataUpdateDict(t.TypedDict, total=False):
    sampling_rate: int
    signal_column: str
    info_column: str
    signal_column_index: int
    info_column_index: int


class DefaultPlotSettings(t.TypedDict):
    background_color: "QtGui.QColor"
    foreground_color: "QtGui.QColor"
    point_color: "QtGui.QColor"
    signal_line_color: "QtGui.QColor"
    rate_line_color: "QtGui.QColor"
    section_marker_color: "QtGui.QColor"


class DefaultEditingSettings(t.TypedDict):
    click_width_signal_line: int
    search_around_click_radius: int
    minimum_peak_distance: int
    rate_computation_method: "RateComputationMethod"
    allow_stacking_filters: bool


class DefaultDataSettings(t.TypedDict):
    sampling_rate: float
    txt_file_separator_character: "TextFileSeparator"
    try_parse_dates: bool


class DefaultMiscSettings(t.TypedDict):
    data_folder: str
    output_folder: str
    float_visual_precision: int
    last_signal_column_name: str | None
    last_info_column_name: str | None


class DefaultAppSettings(t.TypedDict):
    Plot: DefaultPlotSettings
    Editing: DefaultEditingSettings
    Data: DefaultDataSettings
    Misc: DefaultMiscSettings


# region NewConfig
class PlotConfigDict(t.TypedDict):
    Background: "QtGui.QColor"
    Foreground: "QtGui.QColor"
    LineColor: "QtGui.QColor"
    PointColor: "QtGui.QColor"
    SectionColor: "QtGui.QColor"
    LineClickWidth: int
    ClickRadius: int


class EditingConfigDict(t.TypedDict):
    FilterStacking: bool
    RateComputationMethod: "RateComputationMethod"


class DataConfigDict(t.TypedDict):
    FloatPrecision: int
    TextSeparatorChar: "TextFileSeparator"


class InternalConfigDict(t.TypedDict):
    InputDir: str
    OutputDir: str
    RecentFiles: list[str]
    LastSignalColumn: str
    LastInfoColumn: str
    LastSamplingRate: int
    WindowGeometry: "QtCore.QByteArray"
    WindowState: "QtCore.QByteArray"


class ConfigDict(t.TypedDict):
    Plot: PlotConfigDict
    Editing: EditingConfigDict
    Data: DataConfigDict
    Internal: t.NotRequired[InternalConfigDict]


# endregion NewConfig


class ReadFileKwargs(t.TypedDict, total=False):
    columns: list[str]
    index_col: str | int | None
    try_parse_dates: bool
    separator: "TextFileSeparator"
    use_pyarrow: bool
    has_header: bool


class SignalFilterParameters(t.TypedDict, total=False):
    lowcut: float | None
    highcut: float | None
    method: str
    order: int
    window_size: int | t.Literal["default"]
    powerline: int


class StandardizationParameters(t.TypedDict, total=False):
    method: StandardizationMethod
    robust: bool
    window_size: int | None


class SpotDict(t.TypedDict):
    pos: t.Union[tuple[float, float], "QtCore.QPointF"]
    size: float
    pen: PGPen
    brush: PGBrush
    symbol: PGPointSymbols


class SpotItemSetDataKwargs(t.TypedDict, total=False):
    spots: list[SpotDict]
    x: npt.NDArray[np.float64 | np.intp | np.uintp] | t.Sequence[float | int]
    y: npt.NDArray[np.float64 | np.intp | np.uintp] | t.Sequence[float | int]
    pos: npt.NDArray[np.float64 | np.intp] | list[tuple[float, float]]
    pxMode: bool
    symbol: PGPointSymbols
    pen: PGPen
    brush: PGBrush
    size: float
    data: npt.NDArray[np.void]
    hoverable: bool
    tip: str | None
    hoverSymbol: PGPointSymbols
    hoverSize: float
    hoverPen: PGPen
    hoverBrush: PGBrush
    useCache: bool
    antialias: bool
    compositionMode: "QtGui.QPainter.CompositionMode | None"
    name: str | None


class PGConfigOptions(t.TypedDict):
    useOpenGL: bool
    leftButtonPan: bool
    foreground: PGColor
    background: PGColor
    antialias: bool
    editorCommand: str | None
    exitCleanup: bool
    enableExperimental: bool
    crashWarning: bool
    mouseRateLimit: int
    imageAxisOrder: t.Literal["row-major", "col-major"]
    useCupy: bool
    useNumba: bool
    segmentedLineMode: t.Literal["auto", "on", "off"]


class PlotDataItemKwargs(t.TypedDict, total=False):
    x: npt.NDArray[np.float64 | np.intp | np.uintp]
    y: npt.NDArray[np.float64 | np.intp | np.uintp]
    connect: t.Literal["all", "pairs", "finite", "auto"] | npt.NDArray[np.int32]
    pen: PGPen | None
    shadowPen: PGPen | None
    fillLevel: float | None
    fillOutline: bool
    fillBrush: PGBrush | None
    stepMode: t.Literal["center", "left", "right"] | None
    symbol: PGPointSymbols | list[PGPointSymbols] | None
    symbolPen: t.Union[PGPen, list["QtGui.QPen"], None]
    symbolBrush: t.Union[PGBrush, list["QtGui.QBrush"], None]
    symbolSize: float | list[float]
    pxMode: bool
    useCache: bool
    antialias: bool
    downsample: int
    downsampleMethod: t.Literal["subsample", "mean", "peak"]
    autoDownsample: bool
    clipToView: bool
    dynamicRangeLimit: float | None
    dynamicRangeHyst: float
    skipFiniteCheck: bool
    name: str
    clickable: bool


class PlotDataItemOpts(t.TypedDict):
    connect: t.Literal["all", "pairs", "finite", "auto"] | npt.NDArray[np.int32]
    skipFiniteCheck: bool
    fftMode: bool
    logMode: list[bool]
    derivativeMode: bool
    phasemapMode: bool
    alphaHint: float
    alphaMode: bool
    pen: PGPen | None
    shadowPen: PGPen | None
    fillLevel: float | None
    fillOutline: bool
    fillBrush: PGBrush | None
    stepMode: t.Literal["center", "left", "right"] | None
    symbol: PGPointSymbols | list[PGPointSymbols] | None
    symbolPen: t.Union[PGPen, list["QtGui.QPen"], None]
    symbolBrush: t.Union[PGBrush, list["QtGui.QBrush"], None]
    symbolSize: float | list[float]
    pxMode: bool
    antialias: bool
    pointMode: t.Any | None
    useCache: bool
    downsample: int
    autoDownsample: bool
    downsampleMethod: t.Literal["subsample", "mean", "peak"]
    autoDownsampleFactor: float
    clipToView: bool
    dynamicRangeLimit: float | None
    dynamicRangeHyst: float
    data: t.Any | None  # Not used?
    name: t.NotRequired[str]


class NKSignalFilterParams(t.TypedDict, total=False):
    lowcut: float | None
    highcut: float | None
    method: FilterMethod
    order: int
    window_size: int | t.Literal["default"]
    powerline: int | float


class PeaksPPGElgendi(t.TypedDict):
    peakwindow: float
    beatwindow: float
    beatoffset: float
    mindelay: float


class PeaksLocalMaxima(t.TypedDict):
    search_radius: int
    min_distance: int


class PeaksLocalMinima(t.TypedDict):
    search_radius: int
    min_distance: int


class PeaksWFDBXQRS(t.TypedDict):
    search_radius: int
    peak_dir: WFDBPeakDirection


class NK2PeaksNeuroKit(t.TypedDict):
    smoothwindow: float
    avgwindow: float
    gradthreshweight: float
    minlenweight: float
    mindelay: float


class NK2PeaksGamboa(t.TypedDict):
    tol: float


# NOTE: Needs `ts2vg` package which currently doesnt work (py=3.12.3, windows)
# class NK2PeaksEmrich(t.TypedDict):
#     window_seconds: float  # seconds
#     window_overlap: float  # percentage (0-1)
#     accelerated: bool


class NK2PeaksPromac(t.TypedDict):
    threshold: float
    gaussian_sd: int  # milliseconds


NK2PeakMethodParams = t.Union[NK2PeaksNeuroKit, NK2PeaksGamboa, NK2PeaksPromac]


class PeaksECGNeuroKit2(t.TypedDict):
    method: NK2ECGPeakDetectionMethod
    params: t.Union[NK2PeakMethodParams, None]


class PeaksPanTompkins(t.TypedDict):
    correct_artifacts: bool


PeakDetectionMethodParameters = t.Union[
    PeaksPPGElgendi,
    PeaksECGNeuroKit2,
    PeaksPanTompkins,
    PeaksLocalMinima,
    PeaksLocalMaxima,
    PeaksWFDBXQRS,
]


class SelectedFileMetadataDict(t.TypedDict):
    file_name: str
    file_format: str
    name_signal_column: str
    sampling_rate: int
    measured_date: t.NotRequired[str | datetime.datetime | None]
    subject_id: t.NotRequired[str | None]
    oxygen_condition: t.NotRequired[str | None]


class MutableMetadataAttributes(t.TypedDict, total=False):
    measured_date: str | datetime.datetime | None
    subject_id: str | None
    oxygen_condition: str | None


class ProcessingParametersDict(t.TypedDict):
    sampling_rate: int
    processing_pipeline: str
    filter_parameters: SignalFilterParameters | None
    standardization_parameters: StandardizationParameters | None
    peak_detection_method: str
    peak_detection_method_parameters: PeakDetectionMethodParameters


class ManualPeakEditsDict(t.TypedDict):
    added: list[int]
    removed: list[int]


class SectionMetadataDict(t.TypedDict):
    signal_name: str
    section_id: "SectionID"
    global_bounds: tuple[int, int]
    sampling_rate: int
    processing_parameters: ProcessingParametersDict


class CompactSectionResultDict(t.TypedDict):
    peaks_global_index: npt.NDArray[np.int32]
    peaks_section_index: npt.NDArray[np.int32]
    seconds_since_global_start: npt.NDArray[np.float64]
    seconds_since_section_start: npt.NDArray[np.float64]
    peak_intervals: npt.NDArray[np.int32]
    rate_data: npt.NDArray[np.void]
    info_values: t.NotRequired[npt.NDArray[np.float64]]


class DetailedSectionResultDict(t.TypedDict):
    metadata: SectionMetadataDict
    section_dataframe: npt.NDArray[np.void]
    manual_peak_edits: ManualPeakEditsDict
    compact_result: npt.NDArray[np.void]
    rate_data: npt.NDArray[np.void]
    rate_per_temperature: npt.NDArray[np.void]


class ExportInfoDict(t.TypedDict):
    out_path: Path
    subject_id: str | None
    measured_date: str | None
    oxygen_condition: str | None


##### Types for EDF files read with MNE-Python #####
class EDFSubjectInfoDict(t.TypedDict, total=False):
    id: int
    his_id: str
    last_name: str
    first_name: str
    middle_name: str
    birthday: tuple[int]
    sex: t.Literal[0, 1, 2]  # 0 = unknown, 1 = male, 2 = female
    hand: t.Literal[1, 2, 3]  # 1 = right, 2 = left, 3 = ambidextrous
    weight: float  # in kg
    height: float  # in m


class EDFChannelDict(t.TypedDict, total=False):
    cal: float
    logno: int
    scanno: int
    range: float
    unit_mul: int
    ch_name: str
    unit: int
    coord_frame: int
    coil_type: int
    kind: int
    loc: npt.NDArray[np.float64]  # shape (12,)


class EDFInfoDict(t.TypedDict, total=False):
    highpass: float
    lowpass: float
    meas_date: datetime.datetime
    subject_info: dict[str, str]
    bads: list[str]
    chs: list[EDFChannelDict]
    custom_ref_applied: int
    sfreq: float
    dev_head_t: "mne.transforms.Transform"
    ch_names: list[str]
    nchan: int


class CompleteResultDict(t.TypedDict):
    metadata: SelectedFileMetadataDict
    global_dataframe: npt.NDArray[np.void]
    section_results: dict["SectionID", DetailedSectionResultDict]
