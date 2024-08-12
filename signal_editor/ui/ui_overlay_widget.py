# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'overlay_widget.ui'
##
## Created by: Qt User Interface Compiler version 6.7.2
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
from PySide6.QtWidgets import (QApplication, QSizePolicy, QVBoxLayout, QWidget)

from qfluentwidgets import (IndeterminateProgressRing, TitleLabel)
from . import resources_rc

class Ui_OverlayWidget(object):
    def setupUi(self, OverlayWidget):
        if not OverlayWidget.objectName():
            OverlayWidget.setObjectName(u"OverlayWidget")
        OverlayWidget.resize(561, 341)
        self.verticalLayout = QVBoxLayout(OverlayWidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(-1, 0, 0, 0)
        self.gridWidget = QWidget(OverlayWidget)
        self.gridWidget.setObjectName(u"gridWidget")
        self.gridWidget.setStyleSheet(u"background-color: rgba(0, 0, 0, 128);")
        self.verticalLayout_2 = QVBoxLayout(self.gridWidget)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.widget = QWidget(self.gridWidget)
        self.widget.setObjectName(u"widget")
        self.widget.setStyleSheet(u"background: rgba(0,0,0,0);")
        self.verticalLayout_3 = QVBoxLayout(self.widget)
        self.verticalLayout_3.setSpacing(12)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.label = TitleLabel(self.widget)
        self.label.setObjectName(u"label")
        self.label.setMinimumSize(QSize(0, 31))
        self.label.setStyleSheet(u"background: transparent;\n"
"color: white;")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_3.addWidget(self.label, 0, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignTop)

        self.progress_bar = IndeterminateProgressRing(self.widget)
        self.progress_bar.setObjectName(u"progress_bar")

        self.verticalLayout_3.addWidget(self.progress_bar, 0, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)


        self.verticalLayout_2.addWidget(self.widget, 0, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)


        self.verticalLayout.addWidget(self.gridWidget)


        self.retranslateUi(OverlayWidget)

        QMetaObject.connectSlotsByName(OverlayWidget)
    # setupUi

    def retranslateUi(self, OverlayWidget):
        OverlayWidget.setWindowTitle(QCoreApplication.translate("OverlayWidget", u"Form", None))
        self.label.setText(QCoreApplication.translate("OverlayWidget", u"Calculating...", None))
    # retranslateUi

