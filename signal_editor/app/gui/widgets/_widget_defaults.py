"""
Default values for input widgets.
"""

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
        # "peak_dir": 0,  # Index
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
    # "combo_peak_method": 0,  # Index
    # "peak_neurokit2_algorithm_used": 0,  # Index
}


PROCESSING = {
    "dbl_sb_powerline": 50,
    "dbl_sb_lower_cutoff": 0,
    "dbl_sb_upper_cutoff": 0,
    "sb_filter_order": 3,
    "sb_filter_window_size": 333,
    "sb_standardize_window_size": 333,
    # "combo_pipeline": 0,  # Index
    "switch_btn_standardize_rolling_window": False,
    # "combo_filter_method": 0,  # Index
}
