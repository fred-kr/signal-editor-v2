"""
Main entry point for the application.
"""

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
    parser.add_argument("--no-opengl", action="store_false", help="Don't use OpenGL for rendering")
    args = parser.parse_args()

    # os.environ["QT_LOGGING_RULES"] = "qt.pyside.libpyside.warning=true"
    if args.debug:
        os.environ["DEBUG"] = "1"
    else:
        logger.remove()

    use_opengl = args.no_opengl

    pg.setConfigOptions(
        useOpenGL=use_opengl,
        enableExperimental=use_opengl,
        useNumba=use_opengl,
        segmentedLineMode="on",
    )
    pl.Config().activate_decimals(True)

    app = SignalEditor(sys.argv)
    # app.setStyleSheet(qdarkstyle.load_stylesheet())
    # Built-in styles: ['windows11', 'windowsvista', 'Windows', 'Fusion']
    app.setStyle("windows11")
    app.mw.show()
    sys.exit(app.exec())
