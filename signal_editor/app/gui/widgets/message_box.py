import qfluentwidgets as qfw
from PySide6 import QtCore, QtGui, QtWidgets

from signal_editor.app.gui.widgets.data_tree_widget import DataTreeWidget

from ... import type_defs as _t
from ..icons import SignalEditorIcon as Icons


class MessageBox(qfw.MessageBoxBase):
    def __init__(
        self, title: str, text: str, icon: QtGui.QIcon | None = None, parent: QtWidgets.QWidget | None = None
    ) -> None:
        super().__init__(parent)
        upper_layout = QtWidgets.QHBoxLayout()
        self.setWindowTitle(title)

        self._detailed_text: str = "No details available"
        self.icon_widget = qfw.IconWidget(self)
        self.icon_widget.setFixedSize(24, 24)
        if icon is not None:
            self.set_icon(icon)
        self.message_label = qfw.SubtitleLabel(text, self)
        self.message_label.setWordWrap(True)
        self.message_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter)

        upper_layout.addWidget(self.icon_widget)
        upper_layout.addWidget(self.message_label)
        upper_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter)

        self.btn_show_detailed = qfw.PushButton("Show Details", parent=self)
        self.btn_show_detailed.clicked.connect(self._on_show_detailed)

        self.viewLayout.addLayout(upper_layout)
        self.viewLayout.addWidget(self.btn_show_detailed)

        self.widget.setMinimumWidth(400)

    @QtCore.Slot()
    def _on_show_detailed(self) -> None:
        qfw.Flyout.create(
            title="Details",
            content=self._detailed_text,
            icon=Icons.Info.icon(),
            isClosable=True,
            target=self.btn_show_detailed,
            parent=self,
            aniType=qfw.FlyoutAnimationType.NONE,
        )

    def set_detailed_text(self, text: str) -> None:
        self._detailed_text = text

    def set_icon(self, icon: QtGui.QIcon) -> None:
        self.icon_widget.setIcon(icon)

    def set_text(self, text: str) -> None:
        self.message_label.setText(text)

    @staticmethod
    def show_error(
        title: str = "Error", text: str = "An error occurred", parent: QtWidgets.QWidget | None = None
    ) -> None:
        MessageBox(title, text, icon=Icons.ErrorCircle.icon(), parent=parent).open()

    @staticmethod
    def show_warning(
        title: str = "Warning", text: str = "A warning occurred", parent: QtWidgets.QWidget | None = None
    ) -> None:
        MessageBox(title, text, icon=Icons.Warning.icon(), parent=parent).open()

    @staticmethod
    def show_info(title: str = "Info", text: str = "An info message", parent: QtWidgets.QWidget | None = None) -> None:
        MessageBox(title, text, icon=Icons.Info.icon(), parent=parent).open()

    @staticmethod
    def show_success(
        title: str = "Success", text: str = "A success message", parent: QtWidgets.QWidget | None = None
    ) -> None:
        MessageBox(title, text, icon=Icons.CheckmarkCircle.icon(), parent=parent).open()


class SectionSummaryBox(QtWidgets.QDialog):
    def __init__(self, title: str, summary: _t.SectionSummaryDict, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        summary_tree = DataTreeWidget()
        summary_tree.set_data(dict(summary), hide_root=True)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(summary_tree)

        self.setLayout(layout)

        self.setWindowTitle(title)

        self.adjustSize()
