import typing as t

from loguru import logger
from PySide6 import QtCore, QtGui, QtWidgets

from ..icons import FluentIcon as FI


class LoggingWindow(QtWidgets.QTextEdit):
    sig_log_message: t.ClassVar[QtCore.Signal] = QtCore.Signal(str, int, str)

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setReadOnly(True)
        self.setLineWrapMode(QtWidgets.QTextEdit.LineWrapMode.NoWrap)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        logger.add(self.append_html)

        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.sig_log_message.connect(self.append)

    @QtCore.Slot(QtCore.QPoint)
    def show_context_menu(self, pos: QtCore.QPoint) -> None:
        menu = QtWidgets.QMenu(self)
        menu.addAction(QtGui.QIcon(":/icons/reset_all"), "Clear Messages", self.clear)
        menu.exec(self.mapToGlobal(pos))

    def append_html(self, message: str) -> None:
        dtm_part, lvl_part, src_and_msg_part = message.split("|", 2)
        src_part, msg_part = src_and_msg_part.split(" - ", 1)

        # Format the message using HTML
        html_dtm = f'<b style="color: gray;">{dtm_part}</b>'
        if "success" in lvl_part.lower():
            html_lvl = f'<b style="color: lightgreen;">{lvl_part}</b>'
            log_level = 60
        elif "debug" in lvl_part.lower():
            html_lvl = f'<b style="color: teal;">{lvl_part}</b>'
            log_level = 10
        elif "info" in lvl_part.lower():
            html_lvl = f'<b style="color: lightgray;">{lvl_part}</b>'
            log_level = 20
        elif "warning" in lvl_part.lower():
            html_lvl = f'<b style="color: goldenrod;">{lvl_part}</b>'
            log_level = 30
        elif "error" in lvl_part.lower():
            html_lvl = f'<b style="color: firebrick;">{lvl_part}</b>'
            log_level = 40
        elif "critical" in lvl_part.lower():
            html_lvl = f'<b style="color: crimson;">{lvl_part}</b>'
            log_level = 50
        else:
            html_lvl = f'<b style="color: lightgray;">{lvl_part}</b>'
            log_level = 20

        html_src = f"<i>{src_part}</i>"
        html_out = f"{html_dtm} | {html_lvl} | {html_src} - {msg_part}"
        self.sig_log_message.emit(html_out, log_level, message)

    @QtCore.Slot(str, int, str)
    def append(self, message: str, log_level: int, original_message: str) -> None:
        super().append(message)


class StatusMessageDock(QtWidgets.QDockWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("StatusMessageDock")
        self.setWindowTitle("Status Log")
        self.setVisible(False)
        self.toggleViewAction().setIcon(FI.Status.icon())

        self.log_text_box = LoggingWindow(self)
        self.setWindowIcon(FI.Status.icon())
        self.setWidget(self.log_text_box)

    #     if os.environ.get("DEBUG") == "1":
    #         self._test_button = QtWidgets.QPushButton("Test", self)
    #         self._test_button.clicked.connect(self._on_test_button_clicked)

    # @QtCore.Slot()
    # def _on_test_button_clicked(self) -> None:
    #     logger.debug("Debug message")
    #     logger.info("Info message")
    #     logger.warning("Warning message")
    #     logger.error("Error message")
    #     logger.critical("Critical message")
