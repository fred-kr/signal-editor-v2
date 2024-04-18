"""
Main entry point for the application.
"""

from PySide6 import QtWidgets

if __name__ == "__main__":
    import multiprocessing

    multiprocessing.freeze_support()  # This is needed for PyInstaller to work
    import argparse
    import os
    import sys

    import polars as pl
    import pyqtgraph as pg

    # import qdarkstyle
    from loguru import logger

    from signal_editor.signal_editor import SignalEditor

    parser = argparse.ArgumentParser(description="Signal Editor")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()

    if args.debug:
        os.environ["DEBUG"] = "1"
    else:
        logger.remove()

    pg.setConfigOptions(
        useOpenGL=True, enableExperimental=True, useNumba=True, useCupy=True, segmentedLineMode="on"
    )
    pl.Config().activate_decimals(True)

    app = SignalEditor(sys.argv)
    # app.setStyleSheet(qdarkstyle.load_stylesheet(qdarkstyle.DarkPalette))
    # Built-in styles: ['windows11', 'windowsvista', 'Windows', 'Fusion']
    app.setStyle(QtWidgets.QStyleFactory.create("windows11"))
    app.main_window.show()
    sys.exit(app.exec())
