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

    # from PySide6 import QtWidgets

    from signal_editor.se_app import SignalEditor

    parser = argparse.ArgumentParser(description="Signal Editor")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--no-opengl", action="store_false", help="Don't use OpenGL for rendering")
    parser.add_argument("-c", "--console", action="store_true", help="Enable Jupyter console")
    args = parser.parse_args()

    if args.debug:
        os.environ["DEBUG"] = "1"
    else:
        logger.remove()

    use_opengl = args.no_opengl

    if args.console:
        os.environ["DEV"] = "1"

    # Check if running from executable (production) or via python script (development)
    # os.environ["DEV"] = "1" if getattr(sys, "frozen", False) else "0"

    pg.setConfigOptions(
        useOpenGL=use_opengl,
        enableExperimental=use_opengl,
        useNumba=use_opengl,
        segmentedLineMode="on",
    )
    

    app = SignalEditor(sys.argv)
    # Built-in styles: ['windows11', 'windowsvista', 'Windows', 'Fusion']
    # styles = QtWidgets.QStyleFactory.keys()
    # app.setStyle("windows11")

    app.mw.show()

    sys.exit(app.exec())
