import typing as t

import neurokit2 as nk
import numpy as np
import numpy.typing as npt
import polars as pl
from scipy import signal

from .. import type_defs as _t
from ..enum_defs import FilterMethod


def rolling_standardize(sig: pl.Series, window_size: int) -> pl.Series:
    roll_mean = sig.rolling_mean(window_size, min_periods=0)
    roll_std = sig.rolling_std(window_size, min_periods=0)
    return (sig - roll_mean) / roll_std


def calculate_mad(sig: pl.Series, constant: float = 1.4826) -> np.float64:
    sig_median = sig.median()
    mad = np.median(np.abs(sig - sig_median))
    return constant * mad


def standardize_signal(sig: pl.Series, robust: bool = False, window_size: int | None = None) -> pl.Series:
    if robust and window_size:
        raise ValueError("Windowed MAD scaling is not supported for robust scaling")
    if window_size:
        result = rolling_standardize(sig, window_size)
    elif robust:
        result = (sig - sig.median()) / calculate_mad(sig)
    else:
        result = (sig - sig.mean()) / sig.std(ddof=1)

    return result.fill_nan(None).fill_null(strategy="backward")


def ecg_clean_neurokit(
    sig: npt.NDArray[np.float64], sampling_rate: int, powerline: int = 50
) -> npt.NDArray[np.float64]:
    clean = nk.signal_filter(
        signal=sig,
        sampling_rate=sampling_rate,
        lowcut=0.5,
        method=FilterMethod.Butterworth,
        order=5,
    )
    return nk.signal_filter(clean, sampling_rate=sampling_rate, method=FilterMethod.Powerline, powerline=powerline)


def ppg_clean_elgendi(
    sig: npt.NDArray[np.float64], sampling_rate: int
) -> tuple[npt.NDArray[np.float64], _t.SignalFilterParameters]:
    return nk.signal_filter(
        sig,
        sampling_rate=sampling_rate,
        lowcut=0.5,
        highcut=8,
        method=FilterMethod.Butterworth,
        order=3,
    ), {"lowcut": 0.5, "highcut": 8, "method": FilterMethod.Butterworth, "order": 3}


def ecg_clean_biosppy(
    sig: npt.NDArray[np.float64], sampling_rate: int
) -> tuple[npt.NDArray[np.float64], _t.SignalFilterParameters]:
    order = int(1.5 * sampling_rate)
    if order % 2 == 0:
        order += 1

    frequency = [0.67, 45]

    frequency = 2 * np.array(frequency) / sampling_rate  # Normalize frequency to Nyquist Frequency

    a = np.array([1])
    b = signal.firwin(numtaps=order, cutoff=frequency, pass_zero=False)

    filtered = signal.filtfilt(b, a, sig)

    filtered -= np.mean(filtered)

    return filtered, {"lowcut": 0.67, "highcut": 45, "method": FilterMethod.FIR, "order": order}


def ecg_clean_pantompkins(
    sig: npt.NDArray[np.float64], sampling_rate: int
) -> tuple[npt.NDArray[np.float64], _t.SignalFilterParameters]:
    return nk.signal_filter(
        sig,
        sampling_rate=sampling_rate,
        lowcut=5,
        highcut=15,
        method=FilterMethod.ButterworthZI,
        order=1,
    ), {"lowcut": 5, "highcut": 15, "method": FilterMethod.ButterworthZI, "order": 1}


def ecg_clean_hamilton(
    sig: npt.NDArray[np.float64], sampling_rate: int
) -> tuple[npt.NDArray[np.float64], _t.SignalFilterParameters]:
    return nk.signal_filter(
        sig,
        sampling_rate=sampling_rate,
        lowcut=8,
        highcut=16,
        method=FilterMethod.ButterworthZI,
        order=1,
    ), {"lowcut": 8, "highcut": 16, "method": FilterMethod.ButterworthZI, "order": 1}


def ecg_clean_elgendi(
    sig: npt.NDArray[np.float64], sampling_rate: int
) -> tuple[npt.NDArray[np.float64], _t.SignalFilterParameters]:
    return nk.signal_filter(
        sig,
        sampling_rate=sampling_rate,
        lowcut=8,
        highcut=20,
        method=FilterMethod.ButterworthZI,
        order=2,
    ), {"lowcut": 8, "highcut": 20, "method": FilterMethod.ButterworthZI, "order": 2}


def ecg_clean_engzee(
    sig: npt.NDArray[np.float64], sampling_rate: int
) -> tuple[npt.NDArray[np.float64], _t.SignalFilterParameters]:
    return nk.signal_filter(
        sig,
        sampling_rate=sampling_rate,
        lowcut=52,
        highcut=48,
        method=FilterMethod.ButterworthZI,
        order=4,
    ), {"lowcut": 52, "highcut": 48, "method": FilterMethod.ButterworthZI, "order": 4}


def ecg_clean_vgraph(
    sig: npt.NDArray[np.float64], sampling_rate: int
) -> tuple[npt.NDArray[np.float64], _t.SignalFilterParameters]:
    return nk.signal_filter(
        sig,
        sampling_rate=sampling_rate,
        lowcut=4,
        method=FilterMethod.Butterworth,
        order=2,
    ), {"lowcut": 4, "method": FilterMethod.Butterworth, "order": 2}


def filter_signal(
    sig: npt.NDArray[np.float64],
    sampling_rate: int,
    **kwargs: t.Unpack[_t.SignalFilterParameters],
) -> tuple[npt.NDArray[np.float64], _t.SignalFilterParameters]:
    highcut = kwargs.get("highcut")
    lowcut = kwargs.get("lowcut")
    if highcut == 0:
        kwargs["highcut"] = None
    if lowcut == 0:
        kwargs["lowcut"] = None
    out = nk.signal_filter(sig, sampling_rate=sampling_rate, **kwargs)  # type: ignore

    return np.asarray(out, dtype=np.float64), kwargs
