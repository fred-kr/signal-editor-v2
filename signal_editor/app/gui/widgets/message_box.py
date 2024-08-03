import qfluentwidgets as qfw
from PySide6 import QtGui, QtWidgets, QtCore

from ..icons import FluentIcon as FI


class MessageBox(qfw.MessageBoxBase):
    def __init__(
        self, title: str, text: str, icon: QtGui.QIcon | None = None, parent: QtWidgets.QWidget | None = None
    ) -> None:
        super().__init__(parent)
        upper_layout = QtWidgets.QHBoxLayout()
        self.setWindowTitle(title)

        self.detailed_text: str | None = None
        self.icon = qfw.IconWidget(self)
        self.icon.setFixedSize(24, 24)
        if icon is not None:
            self.set_icon(icon)
        self.text = qfw.SubtitleLabel(text, self)
        self.text.setWordWrap(True)

        upper_layout.addWidget(self.icon)
        upper_layout.addWidget(self.text)
        upper_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)

        self.btn_show_detailed = qfw.PushButton("Show Details", parent=self)
        self.btn_show_detailed.clicked.connect(self._on_show_detailed)

        self.viewLayout.addLayout(upper_layout)
        self.viewLayout.addWidget(self.btn_show_detailed)

        self.widget.setMinimumWidth(400)

    @QtCore.Slot()
    def _on_show_detailed(self) -> None:
        if self.detailed_text is not None:
            qfw.Flyout.create(
                title="Details",
                content=self.detailed_text,
                icon=FI.Info.icon(),
                isClosable=True,
                target=self.btn_show_detailed,
                parent=self,
                aniType=qfw.FlyoutAnimationType.FADE_IN
            )
        else:
            qfw.Flyout.create(
                title="Details",
                content="No details available",
                icon=FI.Info.icon(),
                isClosable=True,
                target=self.btn_show_detailed,
                parent=self,
                aniType=qfw.FlyoutAnimationType.FADE_IN
            )
            
    def set_detailed_text(self, text: str) -> None:
        self.detailed_text = text

    def set_icon(self, icon: QtGui.QIcon) -> None:
        self.icon.setIcon(icon)
        self.setWindowIcon(icon)

    def set_text(self, text: str) -> None:
        self.text.setText(text)

    @staticmethod
    def show_error(
        title: str = "Error", text: str = "An error occurred", parent: QtWidgets.QWidget | None = None
    ) -> None:
        MessageBox(title, text, icon=FI.ErrorCircle.icon(), parent=parent).open()

    @staticmethod
    def show_warning(
        title: str = "Warning", text: str = "A warning occurred", parent: QtWidgets.QWidget | None = None
    ) -> None:
        MessageBox(title, text, icon=FI.Warning.icon(), parent=parent).open()

    @staticmethod
    def show_info(title: str = "Info", text: str = "An info message", parent: QtWidgets.QWidget | None = None) -> None:
        MessageBox(title, text, icon=FI.Info.icon(), parent=parent).open()

    @staticmethod
    def show_success(
        title: str = "Success", text: str = "A success message", parent: QtWidgets.QWidget | None = None
    ) -> None:
        MessageBox(title, text, icon=FI.CheckmarkCircle.icon(), parent=parent).open()
