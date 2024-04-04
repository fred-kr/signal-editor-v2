"""
Main entry point for the application.
"""

if __name__ == "__main__":
    import multiprocessing

    multiprocessing.freeze_support()
    import sys
    import os
    import argparse

    from signal_editor.signal_editor import SignalEditor

    parser = argparse.ArgumentParser(description="Signal Editor")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()

    if args.debug:
        os.environ["DEBUG"] = "1"

    app = SignalEditor(sys.argv)
    app.main_window.show()
    sys.exit(app.exec())
