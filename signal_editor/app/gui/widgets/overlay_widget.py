from PySide6 import QtGui, QtWidgets

from ....ui.ui_overlay_widget import Ui_OverlayWidget


class OverlayWidget(QtWidgets.QWidget, Ui_OverlayWidget):
    def __init__(self, parent: QtWidgets.QWidget) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.progress_bar.setCustomBarColor("greenyellow", "greenyellow")
        self.progress_bar.setCustomBackgroundColor(QtGui.QColor(0, 0, 0, 0), QtGui.QColor(0, 0, 0, 0))

        # self._target = parent

    def set_text(self, text: str) -> None:
        self.label.setText(text)

    # def show(self) -> None:
    #     self._target.setEnabled(False)
    #     self.setGeometry(self._target.geometry())
    #     self.raise_()
    #     super().show()

    # def hide(self) -> None:
    #     self._target.setEnabled(True)
    #     super().hide()