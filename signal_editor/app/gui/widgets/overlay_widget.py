from PySide6 import QtCore, QtGui, QtWidgets
import qfluentwidgets as qfw
from ...enum_defs import SVGColors


class OverlayWidget(QtWidgets.QWidget):
    def __init__(self, text: str = "Running...", parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 128);")

        self.progress_bar = qfw.IndeterminateProgressBar(self)
        self.progress_bar.setCustomBarColor(SVGColors.DarkOrange.qcolor(), SVGColors.Orange.qcolor())
        self.progress_bar.setStyleSheet("background-color: rgba(0, 0, 0, 128);")

        self.label = qfw.TitleLabel(text, self)
        self.label.setTextColor(SVGColors.LightGray.qcolor(), SVGColors.Gray.qcolor())
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        self.label.resize(self.size())
        self.progress_bar.resize(self.size())
        super().resizeEvent(event)

    def set_text(self, text: str) -> None:
        self.label.setText(text)