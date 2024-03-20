if __name__ == "__main__":
    import multiprocessing

    multiprocessing.freeze_support()
    import sys

    from signal_editor.signal_editor import SignalEditor

    app = SignalEditor(sys.argv)
    app.main_window.show()
    sys.exit(app.exec())
