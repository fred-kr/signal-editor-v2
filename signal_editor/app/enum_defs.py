import enum

from PySide6 import QtCore, QtGui


class RateComputationMethod(enum.StrEnum):
    """
    Method with which the rate is calculated after peak detection.
    """

    Instantaneous = "instantaneous"
    RollingWindow = "rolling_window"
    RollingWindowNoOverlap = "rolling_window_no_overlap"

    # def __str__(self) -> str:
    #     return self.name


class TextFileSeparator(enum.StrEnum):
    Tab = "\t"
    Space = " "
    Comma = ","
    Semicolon = ";"
    Pipe = "|"

    def qicon(self) -> QtGui.QIcon:
        pixmap = QtGui.QPixmap(16, 16)
        painter = QtGui.QPainter(pixmap)
        painter.drawText(QtCore.QRect(0, 0, 16, 16), QtCore.Qt.AlignmentFlag.AlignCenter, self.value)
        painter.end()
        return QtGui.QIcon(pixmap)


class ExportFormatCompact(enum.StrEnum):
    XLSX = ".xlsx"
    CSV = ".csv"
    TXT = ".txt"


class ExportFormatDetailed(enum.StrEnum):
    HDF5 = ".hdf5"


class FileFormat(enum.StrEnum):
    CSV = ".csv"
    TXT = ".txt"
    TSV = ".tsv"
    XLSX = ".xlsx"
    FEATHER = ".feather"
    EDF = ".edf"


class FilterMethod(enum.StrEnum):
    Butterworth = "butterworth"
    ButterworthLegacy = "butterworth_ba"
    ButterworthZI = "butterworth_zi"
    SavGol = "savgol"
    FIR = "fir"
    Bessel = "bessel"
    Powerline = "powerline"
    # NoFilter = "none"


class FilterType(enum.StrEnum):
    LowPass = "lowpass"
    HighPass = "highpass"
    BandPass = "bandpass"


class PreprocessPipeline(enum.StrEnum):
    # Custom = "custom"
    PPGElgendi = "ppg_elgendi"
    ECGNeuroKit2 = "ecg_neurokit2"
    ECGBioSPPy = "biosppy"
    ECGPanTompkins1985 = "pantompkins1985"
    ECGHamilton2002 = "hamilton2002"
    ECGElgendi2010 = "elgendi2010"
    ECGEngzeeMod2012 = "engzeemod2012"
    ECGVisibilityGraph = "vg"


class StandardizationMethod(enum.StrEnum):
    ZScore = "std"
    ZScoreRobust = "mad"
    # NoStandardization = "none"


class PeakDetectionMethod(enum.StrEnum):
    PPGElgendi = "ppg_elgendi"
    LocalMaxima = "local_maxima"
    LocalMinima = "local_minima"
    ECGNeuroKit2 = "neurokit"
    WFDBXQRS = "wfdb_xqrs"


class NK2ECGPeakDetectionMethod(enum.StrEnum):
    Default = "neurokit"
    PanTompkins1985 = "pantompkins"
    Nabian2018 = "nabian2018"
    Gamboa2008 = "gamboa2008"
    # Zong2003 = "zong2003"  # think this is the same as the method used in the `wfdb` package
    Hamilton2002 = "hamilton2002"
    Christov2004 = "christov2004"
    Engzee2012 = "engzee2012"
    Manikandan2012 = "manikandan2012"
    Elgendi2010 = "elgendi2010"
    Kalidas2017 = "kalidas2017"
    Martinez2004 = "martinez2004"
    Rodrigues2020 = "rodrigues2020"
    Emrich2023 = "emrich2023"
    # SlopeSumFunction = "ssf"
    Promac = "promac"


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


class MouseButtons(enum.StrEnum):
    LeftButton = "left"
    MiddleButton = "middle"
    RightButton = "right"
    LeftButtonWithControl = "left+control"
    RightButtonWithControl = "right+control"
    MiddleButtonWithControl = "middle+control"
    Unknown = "unknown"


class SVGColors(enum.StrEnum):
    AliceBlue = "#f0f8ff"
    AntiqueWhite = "#faebd7"
    Aqua = "#00ffff"
    Aquamarine = "#7fffd4"
    Azure = "#f0ffff"
    Beige = "#f5f5dc"
    Bisque = "#ffe4c4"
    Black = "#000000"
    BlanchedAlmond = "#ffebcd"
    Blue = "#0000ff"
    BlueViolet = "#8a2be2"
    Brown = "#a52a2a"
    BurlyWood = "#deb887"
    CadetBlue = "#5f9ea0"
    Chartreuse = "#7fff00"
    Chocolate = "#d2691e"
    Coral = "#ff7f50"
    CornflowerBlue = "#6495ed"
    Cornsilk = "#fff8dc"
    Crimson = "#dc143c"
    Cyan = "#00ffff"
    DarkBlue = "#00008b"
    DarkCyan = "#008b8b"
    DarkGoldenRod = "#b8860b"
    DarkGray = "#a9a9a9"
    DarkGreen = "#006400"
    DarkGrey = "#a9a9a9"
    DarkKhaki = "#bdb76b"
    DarkMagenta = "#8b008b"
    DarkOliveGreen = "#556b2f"
    DarkOrange = "#ff8c00"
    DarkOrchid = "#9932cc"
    DarkRed = "#8b0000"
    DarkSalmon = "#e9967a"
    DarkSeaGreen = "#8fbc8f"
    DarkSlateBlue = "#483d8b"
    DarkSlateGray = "#2f4f4f"
    DarkSlateGrey = "#2f4f4f"
    DarkTurquoise = "#00ced1"
    DarkViolet = "#9400d3"
    DeepPink = "#ff1493"
    DeepSkyBlue = "#00bfff"
    DimGray = "#696969"
    DimGrey = "#696969"
    DodgerBlue = "#1e90ff"
    FireBrick = "#b22222"
    FloralWhite = "#fffaf0"
    ForestGreen = "#228b22"
    Fuchsia = "#ff00ff"
    Gainsboro = "#dcdcdc"
    GhostWhite = "#f8f8ff"
    Gold = "#ffd700"
    GoldenRod = "#daa520"
    Gray = "#808080"
    Green = "#008000"
    GreenYellow = "#adff2f"
    Grey = "#808080"
    HoneyDew = "#f0fff0"
    HotPink = "#ff69b4"
    IndianRed = "#cd5c5c"
    Indigo = "#4b0082"
    Ivory = "#fffff0"
    Khaki = "#f0e68c"
    Lavender = "#e6e6fa"
    LavenderBlush = "#fff0f5"
    LawnGreen = "#7cfc00"
    LemonChiffon = "#fffacd"
    LightBlue = "#add8e6"
    LightCoral = "#f08080"
    LightCyan = "#e0ffff"
    LightGoldenRodYellow = "#fafad2"
    LightGray = "#d3d3d3"
    LightGreen = "#90ee90"
    LightGrey = "#d3d3d3"
    LightPink = "#ffb6c1"
    LightSalmon = "#ffa07a"
    LightSeaGreen = "#20b2aa"
    LightSkyBlue = "#87cefa"
    LightSlateGray = "#778899"
    LightSlateGrey = "#778899"
    LightSteelBlue = "#b0c4de"
    LightYellow = "#ffffe0"
    Lime = "#00ff00"
    LimeGreen = "#32cd32"
    Linen = "#faf0e6"
    Magenta = "#ff00ff"
    Maroon = "#800000"
    MediumAquaMarine = "#66cdaa"
    MediumBlue = "#0000cd"
    MediumOrchid = "#ba55d3"
    MediumPurple = "#9370db"
    MediumSeaGreen = "#3cb371"
    MediumSlateBlue = "#7b68ee"
    MediumSpringGreen = "#00fa9a"
    MediumTurquoise = "#48d1cc"
    MediumVioletRed = "#c71585"
    MidnightBlue = "#191970"
    MintCream = "#f5fffa"
    MistyRose = "#ffe4e1"
    Moccasin = "#ffe4b5"
    NavajoWhite = "#ffdead"
    Navy = "#000080"
    OldLace = "#fdf5e6"
    Olive = "#808000"
    OliveDrab = "#6b8e23"
    Orange = "#ffa500"
    OrangeRed = "#ff4500"
    Orchid = "#da70d6"
    PaleGoldenRod = "#eee8aa"
    PaleGreen = "#98fb98"
    PaleTurquoise = "#afeeee"
    PaleVioletRed = "#db7093"
    PapayaWhip = "#ffefd5"
    PeachPuff = "#ffdab9"
    Peru = "#cd853f"
    Pink = "#ffc0cb"
    Plum = "#dda0dd"
    PowderBlue = "#b0e0e6"
    Purple = "#800080"
    Red = "#ff0000"
    RosyBrown = "#bc8f8f"
    RoyalBlue = "#4169e1"
    SaddleBrown = "#8b4513"
    Salmon = "#fa8072"
    SandyBrown = "#f4a460"
    SeaGreen = "#2e8b57"
    SeaShell = "#fff5ee"
    Sienna = "#a0522d"
    Silver = "#c0c0c0"
    SkyBlue = "#87ceeb"
    SlateBlue = "#6a5acd"
    SlateGray = "#708090"
    SlateGrey = "#708090"
    Snow = "#fffafa"
    SpringGreen = "#00ff7f"
    SteelBlue = "#4682b4"
    Tan = "#d2b48c"
    Teal = "#008080"
    Thistle = "#d8bfd8"
    Tomato = "#ff6347"
    Turquoise = "#40e0d0"
    Violet = "#ee82ee"
    Wheat = "#f5deb3"
    White = "#ffffff"
    WhiteSmoke = "#f5f5f5"
    Yellow = "#ffff00"
    YellowGreen = "#9acd32"

    def qcolor(self) -> QtGui.QColor:
        return QtGui.QColor(self.value)

    def qicon(self) -> QtGui.QIcon:
        pixmap = QtGui.QPixmap(16, 16)
        pixmap.fill(QtGui.QColor(self.value))
        return QtGui.QIcon(pixmap)


class LogLevel(enum.IntEnum):
    TRACE = 5
    DEBUG = 10
    INFO = 20
    SUCCESS = 25
    WARNING = 30
    ERROR = 40
    CRITICAL = 50
