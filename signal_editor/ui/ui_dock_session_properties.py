# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'dock_session_properties.ui'
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
from PySide6.QtWidgets import (QApplication, QDockWidget, QGridLayout, QHeaderView,
    QSizePolicy, QTreeWidgetItem, QWidget)

from pyqtgraph import TreeWidget
from . import resources_rc

class Ui_DockWidgetSessionProperties(object):
    def setupUi(self, DockWidgetSessionProperties):
        if not DockWidgetSessionProperties.objectName():
            DockWidgetSessionProperties.setObjectName(u"DockWidgetSessionProperties")
        DockWidgetSessionProperties.resize(630, 623)
        DockWidgetSessionProperties.setFloating(False)
        DockWidgetSessionProperties.setFeatures(QDockWidget.DockWidgetClosable|QDockWidget.DockWidgetFloatable|QDockWidget.DockWidgetMovable)
        DockWidgetSessionProperties.setAllowedAreas(Qt.LeftDockWidgetArea|Qt.RightDockWidgetArea)
        self.dockWidgetContents = QWidget()
        self.dockWidgetContents.setObjectName(u"dockWidgetContents")
        self.gridLayout = QGridLayout(self.dockWidgetContents)
        self.gridLayout.setObjectName(u"gridLayout")
        self.tree_widget_properties = TreeWidget(self.dockWidgetContents)
        __qtreewidgetitem = QTreeWidgetItem()
        __qtreewidgetitem.setText(0, u"1");
        self.tree_widget_properties.setHeaderItem(__qtreewidgetitem)
        self.tree_widget_properties.setObjectName(u"tree_widget_properties")

        self.gridLayout.addWidget(self.tree_widget_properties, 2, 1, 1, 1)

        DockWidgetSessionProperties.setWidget(self.dockWidgetContents)

        self.retranslateUi(DockWidgetSessionProperties)

        QMetaObject.connectSlotsByName(DockWidgetSessionProperties)
    # setupUi

    def retranslateUi(self, DockWidgetSessionProperties):
        DockWidgetSessionProperties.setWindowTitle(QCoreApplication.translate("DockWidgetSessionProperties", u"Current Session - Data and Properties", None))
    # retranslateUi

