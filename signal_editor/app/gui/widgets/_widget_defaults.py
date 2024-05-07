from ...enum_defs import WFDBPeakDirection

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
    "peak_pantompkins": {
        "correct_artifacts": False,
    },
    "peak_xqrs": {
        "search_radius": 50,
        "peak_dir": WFDBPeakDirection.Up,
    },
}
