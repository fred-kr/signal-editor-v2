import typing as t

import neurokit2 as nk
import numpy as np
import numpy.typing as npt
import polars as pl
import scipy.interpolate
import scipy.signal
from numba import njit

from .. import type_defs as _t


def _mad_value(sig: pl.Series | pl.Expr) -> float:
    return abs(sig - sig.median()).median()


def _scale_mad[T: (pl.Expr, pl.Series)](sig: T, constant: float = 1.4826) -> T:
    mad_val = _mad_value(sig)
    return (sig - sig.median()) / (mad_val * constant)


def _scale_z[T: (pl.Expr, pl.Series)](sig: T) -> T:
    return (sig - sig.mean()) / sig.std()


def _rolling_mad(sig: pl.Series, window_size: int, constant: float = 1.4826) -> pl.Series:
    if window_size <= 0:
        raise ValueError("Window size must be greater than 0")
    deviation = sig - sig.rolling_median(window_size, min_periods=0)
    mad = deviation.abs().rolling_median(window_size, min_periods=0) * constant

    scaled_signal = deviation / mad
    return scaled_signal.fill_nan(0)


def _rolling_z(sig: pl.Series, window_size: int) -> pl.Series:
    return (
        (sig - sig.rolling_mean(window_size, min_periods=0))
        / sig.rolling_std(window_size, min_periods=0)
    ).fill_nan(sig[0])


def scale_signal(
    sig: pl.Series | npt.NDArray[np.float64],
    robust: bool = False,
    window_size: int | None = None,
) -> pl.Series:
    """
    Scales a signal series using either Z-score or median absolute deviation (MAD) scaling. The
    function can apply scaling on a rolling window basis if a window size is provided.

    Parameters
    ----------
    sig : polars.Series
        The input signal to scale.
    robust : bool, optional
        If True, use MAD for scaling, otherwise use Z-score.
        Defaults to False.
    window_size : int | None, optional
        The size of the rolling window over which to compute the
        scaling. If None, scale the entire series. Defaults to None.

    Returns
    -------
    polars.Series
        The scaled signal series.

    Notes
    -----
    Implementation based on the
    [neurokit2.standardize](https://neuropsychology.github.io/NeuroKit/functions/stats.html#standardize)
    function.
    """
    if isinstance(sig, np.ndarray):
        sig = pl.Series("", sig)
    sig = sig.cast(pl.Float64)

    if window_size:
        return _rolling_mad(sig, window_size) if robust else _rolling_z(sig, window_size)
    else:
        return _scale_mad(sig) if robust else _scale_z(sig)


def _signal_filter_powerline(
    sig: npt.NDArray[np.float64], sampling_rate: int, powerline: int = 50
) -> npt.NDArray[np.float64]:
    b = np.ones(sampling_rate // powerline) if sampling_rate >= 100 else np.ones(2)
    a = [len(b)]
    return np.asarray(scipy.signal.filtfilt(b, a, sig, method="pad"), dtype=np.float64)


def filter_neurokit2(
    sig: npt.NDArray[np.float64], sampling_rate: int, powerline: int | float = 50
) -> npt.NDArray[np.float64]:
    clean = nk.signal_filter(
        signal=sig,
        sampling_rate=sampling_rate,
        lowcut=0.5,
        method="butterworth",
        order=5,
    )
    return _signal_filter_powerline(clean, sampling_rate, powerline)


def filter_elgendi(sig: npt.NDArray[np.float64], sampling_rate: int) -> npt.NDArray[np.float64]:
    return np.asarray(
        nk.signal_filter(
            sig,
            sampling_rate=sampling_rate,
            lowcut=0.5,
            highcut=8,
            method="butterworth",
            order=3,
        ),
        dtype=np.float64,
    )


# TODO: Look up how window size for FIR filters is calculated and replace the loop with that
def filter_signal(
    sig: npt.NDArray[np.float64],
    sampling_rate: int,
    **kwargs: t.Unpack[_t.SignalFilterParameters],
) -> tuple[npt.NDArray[np.float64], _t.SignalFilterParameters]:
    method = kwargs["method"]
    highcut = kwargs["highcut"]
    lowcut = kwargs["lowcut"]
    if highcut == 0:
        kwargs["highcut"] = None
    if lowcut == 0:
        kwargs["lowcut"] = None
    if method == "fir":
        max_attempts = 5  # Define a maximum number of attempts for FIR filtering

        for _ in range(max_attempts):
            try:
                out = nk.signal_filter(sig, sampling_rate=sampling_rate, **kwargs)
                break  # Exit the loop if filtering is successful
            except ValueError as e:
                message = str(e)
                if "which requires" not in message:
                    raise
                required_samples = int(message.split("requires")[1].split("samples")[0].strip())
                kwargs["window_size"] = required_samples
        else:
            raise RuntimeError(f"FIR filtering failed after {max_attempts} attempts")
    else:
        out = nk.signal_filter(sig, sampling_rate=sampling_rate, **kwargs)

    return np.asarray(out, dtype=np.float64), kwargs


def signal_rate(
    peaks: npt.NDArray[np.intp] | pl.Series, sampling_rate: int, desired_length: int | None = None
) -> npt.NDArray[np.float_]:
    if isinstance(peaks, pl.Series):
        peaks = peaks.to_numpy()
    period = np.ediff1d(peaks, to_begin=0) / sampling_rate
    period[0] = np.mean(period[1:10])

    if desired_length is not None:
        x_new = np.arange(desired_length, dtype=np.int32)
        period = scipy.interpolate.PchipInterpolator(peaks, period, extrapolate=True)(x_new)
        first_index = np.searchsorted(x_new, peaks[0])
        last_index = np.searchsorted(x_new, peaks[-1])
        fill_value = (
            np.repeat([period[first_index]], first_index),
            np.repeat([period[last_index]], len(x_new) - last_index - 1),
        )
        period[:first_index] = fill_value[0]
        period[last_index + 1 :] = fill_value[1]

    return 60 / period


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
        .groupby_dynamic(
            pl.col(grp_col),
            include_boundaries=True,
            every=f"{every}i",
            period=f"{period}i",
            offset=f"{offset}i",
        )
        .agg(
            pl.count().alias("n_peaks"),
            pl.mean(temperature_col).round(1).suffix("_mean"),
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
    return rr.group_by(pl.col(f"{temperature_col}_mean")).agg(pl.mean("n_peaks").suffix("_mean"))
