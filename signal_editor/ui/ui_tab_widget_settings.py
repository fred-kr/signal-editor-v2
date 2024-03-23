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
    QTabWidget, QTreeWidgetItem, QWidget)

from pyqtgraph import TreeWidget

class Ui_TabWidgetSettings(object):
    def setupUi(self, TabWidgetSettings):
        if not TabWidgetSettings.objectName():
            TabWidgetSettings.setObjectName(u"TabWidgetSettings")
        TabWidgetSettings.setWindowModality(Qt.WindowModal)
        TabWidgetSettings.resize(472, 438)
        TabWidgetSettings.setTabShape(QTabWidget.Rounded)
        self.tab_general = QWidget()
        self.tab_general.setObjectName(u"tab_general")
        self.gridLayout = QGridLayout(self.tab_general)
        self.gridLayout.setObjectName(u"gridLayout")
        self.tree_widget_general = TreeWidget(self.tab_general)
        self.tree_widget_general.setObjectName(u"tree_widget_general")

        self.gridLayout.addWidget(self.tree_widget_general, 0, 0, 1, 1)

        TabWidgetSettings.addTab(self.tab_general, "")
        self.tab_plots = QWidget()
        self.tab_plots.setObjectName(u"tab_plots")
        self.gridLayout_2 = QGridLayout(self.tab_plots)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.tree_widget_plots = TreeWidget(self.tab_plots)
        self.tree_widget_plots.setObjectName(u"tree_widget_plots")

        self.gridLayout_2.addWidget(self.tree_widget_plots, 0, 0, 1, 1)

        TabWidgetSettings.addTab(self.tab_plots, "")
        self.tab_files_dirs = QWidget()
        self.tab_files_dirs.setObjectName(u"tab_files_dirs")
        self.gridLayout_3 = QGridLayout(self.tab_files_dirs)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.tree_widget_files_dirs = TreeWidget(self.tab_files_dirs)
        self.tree_widget_files_dirs.setObjectName(u"tree_widget_files_dirs")

        self.gridLayout_3.addWidget(self.tree_widget_files_dirs, 0, 0, 1, 1)

        TabWidgetSettings.addTab(self.tab_files_dirs, "")

        self.retranslateUi(TabWidgetSettings)

        TabWidgetSettings.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(TabWidgetSettings)
    # setupUi

    def retranslateUi(self, TabWidgetSettings):
        TabWidgetSettings.setWindowTitle(QCoreApplication.translate("TabWidgetSettings", u"TabWidget", None))
        ___qtreewidgetitem = self.tree_widget_general.headerItem()
        ___qtreewidgetitem.setText(3, QCoreApplication.translate("TabWidgetSettings", u"Info", None));
        ___qtreewidgetitem.setText(2, QCoreApplication.translate("TabWidgetSettings", u"Value", None));
        ___qtreewidgetitem.setText(1, QCoreApplication.translate("TabWidgetSettings", u"Type", None));
        ___qtreewidgetitem.setText(0, QCoreApplication.translate("TabWidgetSettings", u"Setting", None));
        TabWidgetSettings.setTabText(TabWidgetSettings.indexOf(self.tab_general), QCoreApplication.translate("TabWidgetSettings", u"General", None))
        ___qtreewidgetitem1 = self.tree_widget_plots.headerItem()
        ___qtreewidgetitem1.setText(3, QCoreApplication.translate("TabWidgetSettings", u"Info", None));
        ___qtreewidgetitem1.setText(2, QCoreApplication.translate("TabWidgetSettings", u"Value", None));
        ___qtreewidgetitem1.setText(1, QCoreApplication.translate("TabWidgetSettings", u"Type", None));
        ___qtreewidgetitem1.setText(0, QCoreApplication.translate("TabWidgetSettings", u"Setting", None));
        TabWidgetSettings.setTabText(TabWidgetSettings.indexOf(self.tab_plots), QCoreApplication.translate("TabWidgetSettings", u"Plots", None))
        ___qtreewidgetitem2 = self.tree_widget_files_dirs.headerItem()
        ___qtreewidgetitem2.setText(3, QCoreApplication.translate("TabWidgetSettings", u"Info", None));
        ___qtreewidgetitem2.setText(2, QCoreApplication.translate("TabWidgetSettings", u"Value", None));
        ___qtreewidgetitem2.setText(1, QCoreApplication.translate("TabWidgetSettings", u"Type", None));
        ___qtreewidgetitem2.setText(0, QCoreApplication.translate("TabWidgetSettings", u"Setting", None));
        TabWidgetSettings.setTabText(TabWidgetSettings.indexOf(self.tab_files_dirs), QCoreApplication.translate("TabWidgetSettings", u"Files && Directories", None))
    # retranslateUi

