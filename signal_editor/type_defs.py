import typing as t

type FilterMethod = t.Literal[
    "butterworth",
    "butterworth_ba",
    "savgol",
    "fir",
    "bessel",
    "powerline",
    "None",
]

class SignalFilterParameters(t.TypedDict):
    lowcut: float | None
    highcut: float | None
    method: FilterMethod
    order: int
    window_size: int | t.Literal["default"]
    powerline: int | float