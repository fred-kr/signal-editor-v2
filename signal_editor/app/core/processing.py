import typing as t

import neurokit2 as nk
import numpy as np
import numpy.typing as npt
import polars as pl
import scipy.interpolate
import scipy.signal
import scipy.stats

from .. import type_defs as _t
from ..enum_defs import FilterMethod


def rolling_standardize[T: (pl.Expr | pl.Series)](sig: T, window_size: int) -> T:
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


def filter_neurokit2(sig: npt.NDArray[np.float64], sampling_rate: int, powerline: int = 50) -> npt.NDArray[np.float64]:
    clean = nk.signal_filter(
        signal=sig,
        sampling_rate=sampling_rate,
        lowcut=0.5,
        method=FilterMethod.Butterworth,
        order=5,
    )
    return nk.signal_filter(clean, sampling_rate=sampling_rate, method=FilterMethod.Powerline, powerline=powerline)


def filter_elgendi(sig: npt.NDArray[np.float64], sampling_rate: int) -> npt.NDArray[np.float64]:
    return nk.signal_filter(
        sig,
        sampling_rate=sampling_rate,
        lowcut=0.5,
        highcut=8,
        method=FilterMethod.Butterworth,
        order=3,
    )


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


def signal_rate(
    peaks: npt.NDArray[np.int32],
    sampling_rate: int,
    desired_length: int | None = None,
) -> npt.NDArray[np.float64]:
    period = np.ediff1d(peaks, to_begin=0) / sampling_rate
    # For the first period, use the mean of the first 10 periods
    period[0] = np.mean(period[1:10])

    if desired_length is not None:
        # Create a new set of indexes for the desired length
        x_new = np.arange(desired_length, dtype=np.int32)
        # Interpolate the period values to the new length
        period = scipy.interpolate.PchipInterpolator(peaks, period, extrapolate=True)(x_new)
        # Find the index of the first and last peaks in the new indexes
        first_index = np.searchsorted(x_new, peaks[0])
        last_index = np.searchsorted(x_new, peaks[-1])
        # Fill the beginning and end of the array with the first and last period values
        fill_value = (
            np.repeat([period[first_index]], first_index),
            np.repeat([period[last_index]], len(x_new) - last_index - 1),
        )
        period[:first_index] = fill_value[0]
        period[last_index + 1 :] = fill_value[1]

    return np.divide(60, period)


def rolling_rate(
    df: pl.DataFrame,
    grp_col: str,
    temperature_col: str,
    sampling_rate: int,
    sec_new_window_every: int = 10,
    sec_window_length: int = 60,
    sec_start_at: int = 0,
) -> pl.DataFrame:
    every = sec_new_window_every * sampling_rate
    period = sec_window_length * sampling_rate
    offset = sec_start_at * sampling_rate
    remove_row_count = period // every

    if grp_col not in df.columns or temperature_col not in df.columns:
        raise ValueError(f"Columns '{grp_col}' and '{temperature_col}' must exist in the dataframe")
    if df.get_column(grp_col).dtype not in pl.INTEGER_DTYPES:
        raise ValueError(f"Column '{grp_col}' must be of integer type")
    return (
        df.sort(grp_col)
        .with_columns(pl.col(grp_col).cast(pl.Int64))
        .group_by_dynamic(
            pl.col(grp_col),
            include_boundaries=True,
            every=f"{every}i",
            period=f"{period}i",
            offset=f"{offset}i",
        )
        .agg(
            pl.count().alias("n_peaks"),
            pl.mean(temperature_col).round(1).name.suffix("_mean"),
        )[:-remove_row_count]
    )


def mean_bpm_per_temperature(
    df: pl.DataFrame,
    grp_col: str,
    temperature_col: str,
    sampling_rate: int,
    sec_new_window_every: int = 10,
    sec_window_length: int = 60,
    sec_start_at: int = 0,
) -> pl.DataFrame:
    rr = rolling_rate(
        df,
        grp_col,
        temperature_col,
        sampling_rate,
        sec_new_window_every,
        sec_window_length,
        sec_start_at,
    )
    return rr.group_by(pl.col(f"{temperature_col}_mean")).agg(pl.mean("n_peaks").name.suffix("_mean"))
