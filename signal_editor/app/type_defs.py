import datetime
import typing as t

import numpy as np
import numpy.typing as npt

if t.TYPE_CHECKING:
    from PySide6 import QtCore, QtGui

    from .controllers.config_controller2 import RateComputationMethod
    from .core.section import SectionID

type FilterMethod = t.Literal[
    "butterworth",
    "butterworth_ba",
    "savgol",
    "fir",
    "bessel",
    "powerline",
    "None",
]
type PreprocessPipeline = t.Literal["custom", "ppg_elgendi", "ecg_neurokit2"]
type StandardizeMethod = t.Literal["zscore", "mad", "minmax", "None"]
type PeakDetectionMethod = t.Literal[
    "ppg_elgendi", "local_maxima", "wfdb_xqrs", "local_minima", "ecg_neurokit2", "pan_tompkins"
]
type WFDBPeakDirection = t.Literal["up", "down", "both", "compare"]
type OxygenCondition = t.Literal["normoxic", "hypoxic", "unknown"]

type PGColor = "str | int | float | tuple[int, int, int] | tuple[int, int, int, int] | QtGui.QColor"
type PGPen = "PGColor | QtGui.QPen | PGPenKwargs | None"
type PGBrush = "PGColor | QtGui.QBrush | PGBrushKwargs | None"

type PGPointSymbols = 't.Literal["o","s","t","d","+","t1","t2","t3","p","h","star","x","arrow_up","arrow_right","arrow_down","arrow_left","crosshair"] | QtGui.QPainterPath'


type SciPySignalSmoothingKernels = t.Literal[
    "barthann",
    "bartlett",
    "blackman",
    "blackmanharris",
    "bohman",
    "boxcar",
    "chebwin",
    "cosine",
    "dpss",
    "exponential",
    "flattop",
    "gaussian",
    "general_cosine",
    "general_gaussian",
    "general_hamming",
    "hamming",
    "hann",
    "kaiser",
    "kaiser_bessel_derived",
    "lanczos",
    "nuttall",
    "parzen",
    "taylor",
    "triangle",
    "tukey",
    "boxzen",
    "median",
]

type PeakDetectionMethodParameters = (
    PeaksPPGElgendi
    | PeaksECGNeuroKit2
    | PeaksPanTompkins
    | PeaksLocalMinima
    | PeaksLocalMaxima
    | PeaksWFDBXQRS
)


class PGPenKwargs(t.TypedDict, total=False):
    color: PGColor
    width: float
    cosmetic: bool
    dash: t.Sequence[float] | None
    style: "QtCore.Qt.PenStyle | None"
    hsv: tuple[float, float, float, float]


class PGBrushKwargs(t.TypedDict, total=False):
    color: PGColor


class SignalFilterParameters(t.TypedDict, total=False):
    lowcut: float | None
    highcut: float | None
    method: FilterMethod
    order: int
    window_size: int | t.Literal["default"]
    powerline: int | float


class StandardizationParameters(t.TypedDict, total=False):
    method: StandardizeMethod
    robust: bool
    window_size: int | None


class SpotDict(t.TypedDict, total=False):
    pos: "tuple[float, float] | QtCore.QPointF"
    size: float
    pen: "QtGui.QPen | str | None"
    brush: "QtGui.QBrush | str | None"
    symbol: str


class SpotItemSetDataKwargs(t.TypedDict, total=False):
    spots: list[SpotDict]
    x: npt.ArrayLike
    y: npt.ArrayLike
    pos: npt.ArrayLike | list[tuple[float, float]]
    pxMode: bool
    symbol: str
    pen: "QtGui.QPen | str | None"
    brush: "QtGui.QBrush | str | None"
    size: float
    data: npt.NDArray[np.void] | list[t.Any]
    hoverable: bool
    tip: str | None
    hoverSymbol: str
    hoverSize: float
    hoverPen: "QtGui.QPen | str | None"
    hoverBrush: "QtGui.QBrush | str | None"
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
    x: npt.NDArray[np.float_ | np.intp | np.uintp]
    y: npt.NDArray[np.float_ | np.intp | np.uintp]
    connect: t.Literal["all", "pairs", "finite", "auto"] | npt.NDArray[np.int32]
    pen: "PGPen | QtGui.QPen | None"
    shadowPen: "PGPen | QtGui.QPen | None"
    fillLevel: float | None
    fillOutline: bool
    fillBrush: "PGBrush | QtGui.QBrush | None"
    stepMode: t.Literal["center", "left", "right"] | None
    symbol: PGPointSymbols | list[PGPointSymbols] | None
    symbolPen: "PGPen | QtGui.QPen | list[QtGui.QPen] | None"
    symbolBrush: "PGBrush | QtGui.QBrush | list[QtGui.QBrush] | None"
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
    pen: "PGPen | QtGui.QPen | None"
    shadowPen: "PGPen | QtGui.QPen | None"
    fillLevel: float | None
    fillOutline: bool
    fillBrush: "PGBrush | QtGui.QBrush | None"
    stepMode: t.Literal["center", "left", "right"] | None
    symbol: PGPointSymbols | list[PGPointSymbols] | None
    symbolPen: "PGPen | QtGui.QPen | list[QtGui.QPen] | None"
    symbolBrush: "PGBrush | QtGui.QBrush | list[QtGui.QBrush] | None"
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


class PeaksPPGElgendi(t.TypedDict, total=False):
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
    peak_dir: t.NotRequired[WFDBPeakDirection]


class PeaksECGNeuroKit2(t.TypedDict, total=False):
    smoothwindow: float
    avgwindow: float
    gradthreshweight: float
    minlenweight: float
    mindelay: float
    correct_artifacts: bool


class PeaksPanTompkins(t.TypedDict, total=False):
    correct_artifacts: bool


class SelectedFileMetadataDict(t.TypedDict, total=False):
    file_name: str
    file_format: str
    name_signal_column: str
    sampling_rate: int
    measured_date: str | datetime.datetime
    subject_id: str
    oxygen_condition: str


class MutableMetadataAttributes(t.TypedDict, total=False):
    sampling_rate: int
    measured_date: str | datetime.datetime
    subject_id: str
    oxygen_condition: str


class ProcessingParametersDict(t.TypedDict):
    sampling_rate: int
    processing_pipeline: PreprocessPipeline
    filter_parameters: SignalFilterParameters | None
    standardization_parameters: StandardizationParameters | None
    peak_detection_method: PeakDetectionMethod
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
    temperature: npt.NDArray[np.float64]
    instantaneous_rate: npt.NDArray[np.float64]
    rolling_rate: npt.NDArray[np.float64]


class DetailedSectionResultDict(t.TypedDict):
    metadata: SectionMetadataDict
    section_dataframe: npt.NDArray[np.void]
    manual_peak_edits: ManualPeakEditsDict
    compact_result: CompactSectionResultDict
    rate_instantaneous: npt.NDArray[np.float64]
    rate_rolling_window: npt.NDArray[np.float64]


class CompleteResultDict(t.TypedDict):
    metadata: SelectedFileMetadataDict
    global_dataframe: npt.NDArray[np.void]
    section_results: dict["SectionID", DetailedSectionResultDict]


class UserConfigDict(t.TypedDict):
    plot_background_color: "QtGui.QColor"
    plot_foreground_color: "QtGui.QColor"
    plot_scatter_color: "QtGui.QColor"
    plot_signal_color: "QtGui.QColor"
    plot_rate_color: "QtGui.QColor"
    plot_region_color: "QtGui.QColor"
    plot_signal_line_click_width: int
    plot_search_around_click_radius: int
    edit_minimum_allowed_peak_distance: int
    edit_rate_computation_method: "RateComputationMethod"
