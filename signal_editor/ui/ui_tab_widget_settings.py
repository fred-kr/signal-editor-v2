# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'tab_widget_settings.ui'
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
from PySide6.QtWidgets import (QApplication, QGridLayout, QHeaderView, QSizePolicy,
    QTabWidget, QTreeView, QWidget)

class Ui_TabWidgetSettings(object):
    def setupUi(self, TabWidgetSettings):
        if not TabWidgetSettings.objectName():
            TabWidgetSettings.setObjectName(u"TabWidgetSettings")
        TabWidgetSettings.setWindowModality(Qt.WindowModal)
        TabWidgetSettings.resize(613, 438)
        TabWidgetSettings.setTabShape(QTabWidget.Rounded)
        self.tab_app_config = QWidget()
        self.tab_app_config.setObjectName(u"tab_app_config")
        self.gridLayout = QGridLayout(self.tab_app_config)
        self.gridLayout.setObjectName(u"gridLayout")
        self.tree_view_app_config = QTreeView(self.tab_app_config)
        self.tree_view_app_config.setObjectName(u"tree_view_app_config")

        self.gridLayout.addWidget(self.tree_view_app_config, 0, 0, 1, 1)

        TabWidgetSettings.addTab(self.tab_app_config, "")
        self.tab_session_config = QWidget()
        self.tab_session_config.setObjectName(u"tab_session_config")
        self.gridLayout_2 = QGridLayout(self.tab_session_config)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.tree_view_session_config = QTreeView(self.tab_session_config)
        self.tree_view_session_config.setObjectName(u"tree_view_session_config")

        self.gridLayout_2.addWidget(self.tree_view_session_config, 0, 0, 1, 1)

        TabWidgetSettings.addTab(self.tab_session_config, "")

        self.retranslateUi(TabWidgetSettings)

        TabWidgetSettings.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(TabWidgetSettings)
    # setupUi

    def retranslateUi(self, TabWidgetSettings):
        TabWidgetSettings.setWindowTitle(QCoreApplication.translate("TabWidgetSettings", u"Settings", None))
        TabWidgetSettings.setTabText(TabWidgetSettings.indexOf(self.tab_app_config), QCoreApplication.translate("TabWidgetSettings", u"Application", None))
        TabWidgetSettings.setTabText(TabWidgetSettings.indexOf(self.tab_session_config), QCoreApplication.translate("TabWidgetSettings", u"Session", None))
    # retranslateUi

