from PySide6 import QtGui, QtWidgets

from ....ui.ui_overlay_widget import Ui_OverlayWidget


class OverlayWidget(QtWidgets.QWidget, Ui_OverlayWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.progress_bar.setCustomBarColor("greenyellow", "greenyellow")
        self.progress_bar.setCustomBackgroundColor(QtGui.QColor(0, 0, 0, 0), QtGui.QColor(0, 0, 0, 0))

    def set_text(self, text: str) -> None:
        self.label.setText(text)
