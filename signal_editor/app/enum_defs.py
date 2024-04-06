import enum


class FilterMethod(enum.StrEnum):
    Butterworth = "butterworth"
    ButterworthLegacy = "butterworth_ba"
    SavGol = "savgol"
    FIR = "fir"
    Bessel = "bessel"
    Powerline = "powerline"
    NoFilter = "none"


class PreprocessPipeline(enum.StrEnum):
    Custom = "custom"
    PPGElgendi = "ppg_elgendi"
    ECGNeuroKit2 = "ecg_neurokit2"


class StandardizationMethod(enum.StrEnum):
    ZScore = "zscore"
    MedianAbsoluteDeviation = "mad"
    MinMax = "minmax"
    NoStandardization = "none"


class PeakDetectionMethod(enum.StrEnum):
    LocalMaxima = "local_maxima"
    LocalMinima = "local_minima"
    PPGElgendi = "ppg_elgendi"
    WFDBXQRS = "wfdb_xqrs"
    PanTompkins = "pan_tompkins"
    ECGNeuroKit2 = "ecg_neurokit2"


class WFDBPeakDirection(enum.StrEnum):
    Up = "up"
    Down = "down"
    Both = "both"
    Compare = "compare"


class OxygenCondition(enum.StrEnum):
    Normoxic = "normoxic"
    Hypoxic = "hypoxic"
    Unknown = "unknown"


class PointSymbols(enum.StrEnum):
    Circle = "o"
    Square = "s"
    Diamond = "d"
    Plus = "+"
    TriangleDown = "t"
    TriangleUp = "t1"
    TriangleRight = "t2"
    TriangleLeft = "t3"
    Pentagon = "p"
    Hexagon = "h"
    Star = "star"
    Cross = "x"
    ArrowUp = "arrow_up"
    ArrowRight = "arrow_right"
    ArrowDown = "arrow_down"
    ArrowLeft = "arrow_left"
    Crosshair = "crosshair"


class SmoothingKernels(enum.StrEnum):
    BARTHANN = "barthann"
    BARTLETT = "bartlett"
    BLACKMAN = "blackman"
    BLACKMANHARRIS = "blackmanharris"
    BOHMAN = "bohman"
    BOXCAR = "boxcar"
    CHEBWIN = "chebwin"
    COSINE = "cosine"
    DPSS = "dpss"
    EXPONENTIAL = "exponential"
    FLATTOP = "flattop"
    GAUSSIAN = "gaussian"
    GENERAL_COSINE = "general_cosine"
    GENERAL_GAUSSIAN = "general_gaussian"
    GENERAL_HAMMING = "general_hamming"
    HAMMING = "hamming"
    HANN = "hann"
    KAISER = "kaiser"
    KAISER_BESSEL_DERIVED = "kaiser_bessel_derived"
    LANCZOS = "lanczos"
    NUTTALL = "nuttall"
    PARZEN = "parzen"
    TAYLOR = "taylor"
    TRIANGLE = "triangle"
    TUKEY = "tukey"
    BOXZEN = "boxzen"
    MEDIAN = "median"