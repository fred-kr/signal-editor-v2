import os

from loguru import logger
from PySide6 import QtCore, QtGui, QtWidgets


class TextEditLoguru(QtWidgets.QTextEdit):
    sig_log_message = QtCore.Signal(str)

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
        if "debug" in lvl_part.lower():
            html_lvl = f'<b style="color: steelblue;">{lvl_part}</b>'
        elif "info" in lvl_part.lower():
            html_lvl = f'<b style="color: lightgreen;">{lvl_part}</b>'
        elif "warning" in lvl_part.lower():
            html_lvl = f'<b style="color: goldenrod;">{lvl_part}</b>'
        elif "error" in lvl_part.lower():
            html_lvl = f'<b style="color: red;">{lvl_part}</b>'
        elif "critical" in lvl_part.lower():
            html_lvl = f'<b style="color: firebrick;">{lvl_part}</b>'
        else:
            html_lvl = f'<b style="color: gray;">{lvl_part}</b>'

        html_src = f"<i>{src_part}</i>"
        html_out = f"{html_dtm} | {html_lvl} | {html_src} - {msg_part}"
        self.sig_log_message.emit(html_out)


class StatusMessageDock(QtWidgets.QDockWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("StatusMessageDock")
        self.setWindowTitle("Status Log")
        self.setVisible(False)

        self.log_text_box = TextEditLoguru(self)
        self.setWindowIcon(QtGui.QIcon(":/icons/sys_monitor"))
        self.setWidget(self.log_text_box)

        if os.environ.get("DEBUG") == "1":
            self._test_button = QtWidgets.QPushButton("Test", self)
            self._test_button.clicked.connect(self._on_test_button_clicked)

    @QtCore.Slot()
    def _on_test_button_clicked(self) -> None:
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        logger.critical("Critical message")