# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'dock_status_log.ui'
##
## Created by: Qt User Interface Compiler version 6.6.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QDockWidget, QGridLayout, QPlainTextEdit,
    QSizePolicy, QWidget)

class Ui_DockWidgetLogOutput(object):
    def setupUi(self, DockWidgetLogOutput):
        if not DockWidgetLogOutput.objectName():
            DockWidgetLogOutput.setObjectName(u"DockWidgetLogOutput")
        DockWidgetLogOutput.resize(576, 300)
        DockWidgetLogOutput.setAllowedAreas(Qt.BottomDockWidgetArea|Qt.TopDockWidgetArea)
        self.dockWidgetContents = QWidget()
        self.dockWidgetContents.setObjectName(u"dockWidgetContents")
        self.gridLayout = QGridLayout(self.dockWidgetContents)
        self.gridLayout.setObjectName(u"gridLayout")
        self.plain_text_edit_logging = QPlainTextEdit(self.dockWidgetContents)
        self.plain_text_edit_logging.setObjectName(u"plain_text_edit_logging")
        self.plain_text_edit_logging.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.plain_text_edit_logging.setUndoRedoEnabled(False)
        self.plain_text_edit_logging.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.plain_text_edit_logging.setReadOnly(True)

        self.gridLayout.addWidget(self.plain_text_edit_logging, 0, 0, 1, 1)

        DockWidgetLogOutput.setWidget(self.dockWidgetContents)

        self.retranslateUi(DockWidgetLogOutput)

        QMetaObject.connectSlotsByName(DockWidgetLogOutput)
    # setupUi

    def retranslateUi(self, DockWidgetLogOutput):
        DockWidgetLogOutput.setWindowTitle(QCoreApplication.translate("DockWidgetLogOutput", u"Status Messages", None))
    # retranslateUi

