"""
Main entry point for the application.
"""

if __name__ == "__main__":
    import multiprocessing

    multiprocessing.freeze_support()  # This is needed for PyInstaller to work
    import argparse
    import os
    import sys

    import pyqtgraph as pg
    from loguru import logger
    import polars as pl

    from signal_editor.signal_editor import SignalEditor

    parser = argparse.ArgumentParser(description="Signal Editor")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()

    if args.debug:
        os.environ["DEBUG"] = "1"
    else:
        logger.remove()

    pg.setConfigOptions(useOpenGL=True, enableExperimental=True, useNumba=True, useCupy=True, segmentedLineMode="on")
    pl.Config().activate_decimals(True)

    app = SignalEditor(sys.argv)
    app.main_window.show()
    sys.exit(app.exec())
