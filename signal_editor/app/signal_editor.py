from PySide6 import QtCore


class SignalEditor(QtCore.QObject):

    def __init__(self):
        super().__init__()
        self.data_controller = ...
        self.plot_controller = ...
        self.main_window = ...