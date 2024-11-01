"""
Main entry point for the application.
"""

if __name__ == "__main__":
    import multiprocessing

    multiprocessing.freeze_support()  # This is needed for PyInstaller to work
    import argparse
    import os
    import sys

    parser = argparse.ArgumentParser(description="")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--no-opengl", action="store_false", help="Don't use OpenGL for rendering")
    parser.add_argument("-c", "--console", action="store_true", help="Enable Jupyter console")
    args = parser.parse_args()

    from loguru import logger

    logger.remove()

    if args.debug:
        logger.add(sys.stderr, colorize=True, backtrace=True, diagnose=True)
        logger.add("debug.log")
        org_name = "QuackTech"
        app_name = "Signal Editor - DEBUG"
    else:
        org_name = "AWI"
        app_name = "Signal Editor"

    from PySide6 import QtWidgets

    QtWidgets.QApplication.setOrganizationName(org_name)
    QtWidgets.QApplication.setApplicationName(app_name)
    use_opengl = args.no_opengl  # Default is True
    # To allow pyqtgraph to use OpenGL for plotting this needs to be set to 'opengl', otherwise the plot widgets aren't rendered correctly
    # Also, as of 2024-09-12, 'opengl' is still faster than the default (d3d11 on Windows)
    if use_opengl:
        os.environ["QSG_RHI_BACKEND"] = "opengl"

    if args.console:
        os.environ["DEV"] = "1"

    import pyqtgraph as pg

    pg.setConfigOptions(
        useOpenGL=use_opengl,
        enableExperimental=use_opengl,
        segmentedLineMode="on",
    )

    from signal_editor.se_app import SignalEditor

    app = SignalEditor(sys.argv)
    # Built-in styles: ['windows11', 'windowsvista', 'Windows', 'Fusion']
    app.mw.show()

    sys.exit(app.exec())
