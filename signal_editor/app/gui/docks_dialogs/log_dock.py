import enum
import typing as t

import qfluentwidgets as qfw
from loguru import logger
from PySide6 import QtCore, QtGui, QtWidgets

from ... import type_defs as _t
from ...enum_defs import LogLevel
from ..icons import SignalEditorIcons as Icons


class LoggingWindow(qfw.TextEdit):
    sig_log_message: t.ClassVar[QtCore.Signal] = QtCore.Signal(str, enum.IntEnum, dict)

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setReadOnly(True)
        self.setLineWrapMode(QtWidgets.QTextEdit.LineWrapMode.NoWrap)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setFont(QtGui.QFont("Roboto Mono", 10))
        logger.add(
            self.append_html,
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {message}",
            backtrace=True,
            diagnose=True,
        )

        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        self.sig_log_message.connect(self.append)
        self.action_clear_log = qfw.Action("Clear Log", parent=self)
        self.action_clear_log.triggered.connect(self.clear)

    @QtCore.Slot(QtCore.QPoint)
    def show_context_menu(self, pos: QtCore.QPoint) -> None:
        menu = qfw.RoundMenu(parent=self)
        menu.addAction(self.action_clear_log)
        menu.exec(self.mapToGlobal(pos))

    def append_html(self, message: str) -> None:
        record_dict: _t.LogRecordDict = message.record
        level = LogLevel[record_dict["level"].name]

        self.sig_log_message.emit(message, level, record_dict)

    @QtCore.Slot(str, int, str)
    def append(self, message: str, log_level: LogLevel, record_dict: _t.LogRecordDict) -> None:
        self.moveCursor(QtGui.QTextCursor.MoveOperation.End)
        self.textCursor().insertHtml(f"{message}<br>")
        self.moveCursor(QtGui.QTextCursor.MoveOperation.End)


class StatusMessageDock(QtWidgets.QDockWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("StatusMessageDock")
        self.setWindowTitle("Status Log")
        self.setVisible(False)
        self.toggleViewAction().setIcon(Icons.Status.icon())

        self.log_text_box = LoggingWindow(self)
        self.setWindowIcon(Icons.History.icon())
        self.setWidget(self.log_text_box)