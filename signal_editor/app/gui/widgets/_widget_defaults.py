from signal_editor.app.enum_defs import WFDBPeakDirection

PEAK_DETECTION = {
    "peak_elgendi_ppg": {
        "peakwindow": 0.111,
        "beatwindow": 0.667,
        "beatoffset": 0.02,
        "mindelay": 0.3,
    },
    "peak_neurokit2": {
        "smoothwindow": 0.1,
        "avgwindow": 0.75,
        "gradthreshweight": 1.5,
        "minlenweight": 0.4,
        "mindelay": 0.3,
    },
    "peak_local_max": {
        "radius": 100,
        "min_dist": 15,
    },
    "peak_local_min": {
        "radius": 100,
        "min_dist": 15,
    },
    "peak_xqrs": {
        "search_radius": 50,
        "peak_dir": WFDBPeakDirection.Up,
    },
    "peak_promac": {
        "threshold": 0.33,
        "gaussian_sd": 100,
    },
    "peak_gamboa": {
        "tol": 0.002,
    },
    "peak_ssf": {
        "threshold": 20,
        "before": 0.03,
        "after": 0.01,
    },
    "peak_emrich": {
        "window_seconds": 2,
        "window_overlap": 0.5,
        "accelerated": True,
    },
}
