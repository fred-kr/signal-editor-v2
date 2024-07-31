import typing as t

import neurokit2 as nk
import numpy as np
import numpy.typing as npt
import wfdb.processing as wp
from loguru import logger
from scipy import ndimage, signal

from .. import type_defs as _t
from ..enum_defs import PeakDetectionMethod, SmoothingKernels, WFDBPeakDirection


def _fit_loess(
    y: npt.NDArray[np.float64],
    x: npt.NDArray[np.float64] | None = None,
    alpha: float = 0.75,
    order: int = 2,
) -> npt.NDArray[np.float64]:
    if x is None:
        x = np.linspace(0, 100, len(y))
    if order not in (1, 2):
        raise ValueError("order must be 1 or 2")
    if not 0 < alpha <= 1:
        raise ValueError("alpha must be in the range (0, 1]")
    if len(x) != len(y):
        raise ValueError("x and y must have the same length")

    n = len(x)
    span = int(np.ceil(alpha * n))
    y_predicted = np.zeros(n)

    for i, val in enumerate(x):
        distances = np.abs(x - val)
        nearest_indices = np.argsort(distances)[:span]
        nx, ny = x[nearest_indices], y[nearest_indices]
        weights = (1 - (distances[nearest_indices] / distances[nearest_indices][-1]) ** 3) ** 3

        A = np.vander(nx, N=order + 1)
        W = np.diag(weights)
        V = A.T @ W @ A
        Y = A.T @ W @ ny
        Q, R = np.linalg.qr(V)
        p = np.linalg.solve(R, Q.T @ Y)

        y_predicted[i] = np.polyval(p, val)

    return y_predicted


def _signal_smoothing_median(sig: npt.NDArray[np.float64], size: int = 5) -> npt.NDArray[np.float64]:
    if size % 2 == 0:
        size += 1
    return ndimage.median_filter(sig, size=size)


def _signal_smoothing(sig: npt.NDArray[np.float64], kernel: SmoothingKernels, size: int = 5) -> npt.NDArray[np.float64]:
    window: npt.NDArray[np.float64] = signal.get_window(kernel, size)
    w: npt.NDArray[np.float64] = window / window.sum()

    x = np.concatenate((sig[0] * np.ones(size), sig, sig[-1] * np.ones(size)))

    smoothed = np.convolve(w, x, mode="same")
    return smoothed[size:-size]


def _signal_smooth(
    sig: npt.NDArray[np.float64],
    method: t.Literal["convolution", "loess"] = "convolution",
    kernel: SmoothingKernels = SmoothingKernels.BOXZEN,
    size: int = 10,
    alpha: float = 0.1,
) -> npt.NDArray[np.float64]:
    length = sig.size

    if size > length or size < 1:
        raise ValueError(f"Size must be between 1 and {length}")

    if method == "loess":
        smoothed = _fit_loess(sig, alpha=alpha)
    elif method == "convolution":
        if kernel == SmoothingKernels.BOXCAR:
            smoothed = ndimage.uniform_filter1d(sig, size=size, mode="nearest")
        elif kernel == SmoothingKernels.BOXZEN:
            x = ndimage.uniform_filter1d(sig, size=size, mode="nearest")
            smoothed = _signal_smoothing(x, kernel=SmoothingKernels.PARZEN, size=size)
        elif kernel == SmoothingKernels.MEDIAN:
            smoothed = _signal_smoothing_median(sig, size=size)
        else:
            smoothed = _signal_smoothing(sig, kernel=kernel, size=size)

    return smoothed


def _find_peaks_ppg_elgendi(
    sig: npt.NDArray[np.float64],
    sampling_rate: int,
    peakwindow: float = 0.111,
    beatwindow: float = 0.667,
    beatoffset: float = 0.02,
    mindelay: float = 0.3,
) -> npt.NDArray[np.int32]:
    """
    Finds peaks in a PPG (photoplethysmography) signal using the method described by Elgendi et al. (see Notes)

    Parameters
    ----------
    sig : NDArray[np.float64]
        The PPG signal as a 1-dimensional NumPy array.
    sampling_rate : int
        The sampling rate of the PPG signal in samples per second.
    peakwindow : float, optional
        The width of the window used for smoothing the squared PPG signal to find peaks (in seconds).
    beatwindow : float, optional
        The width of the window used for smoothing the squared PPG signal to find beats (in seconds).
    beatoffset : float, optional
        The offset added to the smoothed beat signal to determine the threshold for detecting waves.
    mindelay : float, optional
        The minimum delay between consecutive peaks (in seconds).

    Returns
    -------
    npt.NDArray[np.int32]
        An array of peak indices as a 1-dimensional NumPy array.

    Notes
    -----
    This function implements the peak detection algorithm proposed by Elgendi et al. for
    PPG signals. The algorithm involves squaring the signal, applying a moving average
    with different window sizes for peak detection, and finding the local maxima in the
    resulting signal.

    For more information, see [Elgendi et al.](https://doi.org/10.1371/journal.pone.0076585).

    The implementation is based on the `neurokit2.ppg.ppg_findpeaks` function with `method="elgendi"`. Changes
    are made to improve code readability and performance by making
    """
    sig_clipped_squared = np.clip(sig, 0, None) ** 2

    peakwindow_samples = np.rint(peakwindow * sampling_rate).astype(np.int32)
    ma_peak = _signal_smooth(sig_clipped_squared, kernel=SmoothingKernels.BOXCAR, size=peakwindow_samples)

    beatwindow_samples = np.rint(beatwindow * sampling_rate).astype(np.int32)
    ma_beat = _signal_smooth(sig_clipped_squared, kernel=SmoothingKernels.BOXCAR, size=beatwindow_samples)

    thr1 = ma_beat + beatoffset * np.mean(sig_clipped_squared)

    waves = ma_peak > thr1
    wave_changes = np.diff(waves.astype(np.int32))
    beg_waves = np.flatnonzero(wave_changes == 1)
    end_waves = np.flatnonzero(wave_changes == -1)

    if end_waves[0] < beg_waves[0]:
        end_waves = end_waves[1:]
    if end_waves[-1] < beg_waves[-1]:
        beg_waves = beg_waves[:-1]

    diff_waves = end_waves - beg_waves
    valid_waves = diff_waves >= peakwindow_samples
    beg_waves = beg_waves[valid_waves]
    end_waves = end_waves[valid_waves]

    min_delay_samples = np.rint(mindelay * sampling_rate).astype(np.int32)
    peaks: list[int] = []

    for beg, end in zip(beg_waves, end_waves, strict=False):
        data = sig[beg:end]
        locmax, props = signal.find_peaks(data, prominence=(None, None))

        if locmax.size > 0:
            peak = beg + locmax[props["prominences"].argmax()]

            if not peaks or peak - peaks[-1] > min_delay_samples:
                peaks.append(peak)

    return np.array(peaks, dtype=np.int32)


def _find_peaks_local_max(sig: npt.NDArray[np.float64], search_radius: int) -> npt.NDArray[np.int32]:
    if sig.size == 0 or np.min(sig) == np.max(sig):
        return np.array([], dtype=np.int32)

    max_vals = ndimage.maximum_filter1d(sig, size=2 * search_radius + 1, mode="constant")
    return np.flatnonzero(sig == max_vals)


def _find_peaks_local_min(sig: npt.NDArray[np.float64], search_radius: int) -> npt.NDArray[np.int32]:
    if sig.size == 0 or np.min(sig) == np.max(sig):
        return np.array([], dtype=np.int32)

    min_vals = ndimage.minimum_filter1d(sig, size=2 * search_radius + 1, mode="constant")
    return np.flatnonzero(sig == min_vals)


def find_extrema(
    sig: npt.NDArray[np.float64], search_radius: int, direction: t.Literal["up", "down"], min_peak_distance: int = 10
) -> npt.NDArray[np.int32]:
    if direction == "up":
        peaks = _find_peaks_local_max(sig, search_radius)
    else:
        peaks = _find_peaks_local_min(sig, search_radius)

    # settings = QtCore.QSettings()

    # min_dist = settings.value("Editing/minimum_peak_distance")
    peak_diffs = np.diff(peaks)
    close_peaks = np.where(peak_diffs < min_peak_distance)[0]
    while len(close_peaks) > 0:
        for i in close_peaks:
            peaks[i] = (peaks[i] + peaks[i + 1]) // 2
        peaks = np.delete(peaks, close_peaks + 1)
        peak_diffs = np.diff(peaks)
        close_peaks = np.where(peak_diffs < min_peak_distance)[0]

    return peaks


# XQRS related functions
def _shift_peaks(
    sig: npt.NDArray[np.float64], peaks: npt.NDArray[np.int32], radius: int, dir_is_up: bool
) -> npt.NDArray[np.int32]:
    start_indices = np.maximum(peaks - radius, 0)
    end_indices = np.minimum(peaks + radius, sig.size)

    shifted_peaks = np.zeros_like(peaks)

    for i, (start, end) in enumerate(zip(start_indices, end_indices, strict=False)):
        local_sig = sig[start:end]
        if dir_is_up:
            shifted_peaks[i] = np.subtract(np.argmax(local_sig), radius)
        else:
            shifted_peaks[i] = np.subtract(np.argmin(local_sig), radius)

    peaks += shifted_peaks
    return peaks


def _adjust_peak_positions(
    sig: npt.NDArray[np.float64],
    peaks: npt.NDArray[np.int32],
    radius: int,
    direction: WFDBPeakDirection,
) -> npt.NDArray[np.int32]:
    if direction == WFDBPeakDirection.Up:
        return _shift_peaks(sig, peaks, radius, dir_is_up=True)
    elif direction == WFDBPeakDirection.Down:
        return _shift_peaks(sig, peaks, radius, dir_is_up=False)
    elif direction == WFDBPeakDirection.Both:
        return _shift_peaks(np.abs(sig), peaks, radius, dir_is_up=True)
    elif direction == WFDBPeakDirection.Compare:
        shifted_up = _shift_peaks(sig, peaks, radius, dir_is_up=True)
        shifted_down = _shift_peaks(sig, peaks, radius, dir_is_up=False)

        up_dist = np.mean(np.abs(sig[shifted_up]))
        down_dist = np.mean(np.abs(sig[shifted_down]))

        return shifted_up if np.greater_equal(up_dist, down_dist) else shifted_down


def _get_comparison_func(find_peak_func: t.Callable[..., np.intp]) -> t.Callable[..., np.bool_]:
    if find_peak_func == np.argmax:
        return np.less_equal
    elif find_peak_func == np.argmin:
        return np.greater_equal
    else:
        raise ValueError("find_peak_func must be np.argmax or np.argmin")


def _remove_outliers(
    sig: npt.NDArray[np.float64],
    qrs_locations: npt.NDArray[np.int32],
    n_std: float,
    find_peak_func: t.Callable[..., np.intp],
) -> npt.NDArray[np.int32]:
    comparison_ops = {np.argmax: (np.less_equal, -1), np.argmin: (np.greater_equal, 1)}

    if find_peak_func not in comparison_ops:
        raise ValueError("find_peak_func must be np.argmax or np.argmin")

    comparison_func, direction = comparison_ops[find_peak_func]
    outliers_mask = np.zeros_like(qrs_locations, dtype=np.bool_)

    for i, peak in enumerate(qrs_locations):
        start_ind = max(0, i - 2)
        end_ind = min(len(qrs_locations), i + 3)

        surrounding_peaks = qrs_locations[start_ind:end_ind]
        surrounding_values = sig[surrounding_peaks]
        local_mean = np.mean(surrounding_values)
        local_std = np.std(surrounding_values)
        threshold = local_mean + direction * n_std * local_std

        if comparison_func(sig[peak], threshold):
            outliers_mask[i] = True

    qrs_locations = qrs_locations[~outliers_mask]
    return qrs_locations


def _handle_close_peaks(
    sig: npt.NDArray[np.float64],
    qrs_locations: npt.NDArray[np.int32],
    n_std: float,
    find_peak_func: t.Callable[..., np.intp],
    min_peak_distance: int = 10,
) -> npt.NDArray[np.int32]:
    qrs_diffs = np.diff(qrs_locations)
    # settings = QtCore.QSettings()
    # min_dist = settings.value("Editing/minimum_peak_distance")
    close_indices = np.where(qrs_diffs <= min_peak_distance)[0]

    if not close_indices.size:
        return qrs_locations

    comparison_func = _get_comparison_func(find_peak_func)
    to_remove = [
        i if comparison_func(sig[qrs_locations[i]], sig[qrs_locations[i + 1]]) else i + 1 for i in close_indices
    ]

    qrs_locations = np.delete(qrs_locations, to_remove)
    return _remove_outliers(sig, qrs_locations, n_std, find_peak_func)


def _sanitize_qrs_locations(
    sig: npt.NDArray[np.float64],
    qrs_locations: npt.NDArray[np.int32],
    min_peak_distance: int,
    n_std: float = 4.0,
) -> npt.NDArray[np.int32]:
    find_peak_func = np.argmax if np.mean(sig) < np.mean(sig[qrs_locations]) else np.argmin

    peak_indices = _handle_close_peaks(sig, qrs_locations, n_std, find_peak_func, min_peak_distance)
    sorted_peak_indices = np.argsort(peak_indices)

    return peak_indices[
        sorted_peak_indices[(peak_indices[sorted_peak_indices] > 0) & (peak_indices[sorted_peak_indices] < sig.size)]
    ]


def _find_peaks_xqrs(
    sig: npt.NDArray[np.float64],
    sampling_rate: int,
    radius: int,
    min_peak_distance: int,
    peak_dir: WFDBPeakDirection = WFDBPeakDirection.Up,
) -> npt.NDArray[np.int32]:
    xqrs_out = wp.XQRS(sig, sampling_rate)
    xqrs_out.detect()
    qrs_locations = np.array(xqrs_out.qrs_inds, dtype=np.int32)
    peak_indices = _adjust_peak_positions(sig, peaks=qrs_locations, radius=radius, direction=peak_dir)

    return _sanitize_qrs_locations(sig, peak_indices, min_peak_distance)


def find_peaks(
    sig: npt.NDArray[np.float64],
    sampling_rate: int,
    method: PeakDetectionMethod,
    method_parameters: _t.PeakDetectionMethodParameters,
    **kwargs: t.Unpack[_t.FindPeaksKwargs],
) -> npt.NDArray[np.int32]:
    if method == PeakDetectionMethod.LocalMaxima:
        return find_extrema(
            sig,
            search_radius=method_parameters.get("search_radius", sampling_rate // 2),
            direction="up",
        )
    elif method == PeakDetectionMethod.LocalMinima:
        return find_extrema(
            sig,
            search_radius=method_parameters.get("search_radius", sampling_rate // 2),
            direction="down",
        )
    elif method == PeakDetectionMethod.PPGElgendi:
        return _find_peaks_ppg_elgendi(
            sig,
            sampling_rate,
            peakwindow=method_parameters.get("peakwindow", 0.111),
            beatwindow=method_parameters.get("beatwindow", 0.667),
            beatoffset=method_parameters.get("beatoffset", 0.02),
            mindelay=method_parameters.get("mindelay", 0.3),
        )
    elif method == PeakDetectionMethod.WFDBXQRS:
        return _find_peaks_xqrs(
            sig,
            sampling_rate,
            radius=method_parameters.get("search_radius", sampling_rate // 2),
            min_peak_distance=kwargs.get("min_peak_distance", 20),
            peak_dir=method_parameters.get("peak_dir", WFDBPeakDirection.Up),
        )
    elif method == PeakDetectionMethod.ECGNeuroKit2:
        assert "method" in method_parameters, "NeuroKit2 ECG peak detection method not specified"
        return _find_peaks_nk_ecg(method_parameters, sig, sampling_rate)
    else:
        raise ValueError(f"Unsupported peak detection method: {method}")


def _find_peaks_nk_ecg(
    method_parameters: _t.PeaksECGNeuroKit2, sig: npt.NDArray[np.float64], sampling_rate: int
) -> npt.NDArray[np.int32]:
    nk_method = method_parameters["method"]
    logger.info(f"Using NeuroKit2 ECG peak detection method: {nk_method}")
    params = method_parameters["params"]
    if params is None:
        params = {}

    return nk.ecg_findpeaks(
        ecg_cleaned=sig,
        sampling_rate=sampling_rate,
        method=nk_method,
        show=False,
        **params,
    )["ECG_R_Peaks"]  # type: ignore
