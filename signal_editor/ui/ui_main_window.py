# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.6.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QAbstractScrollArea, QApplication, QColumnView,
    QGridLayout, QHeaderView, QMainWindow, QMenu,
    QMenuBar, QSizePolicy, QSplitter, QStackedWidget,
    QStatusBar, QTableView, QTableWidgetItem, QToolBar,
    QWidget)

from pyqtgraph import (GraphicsLayoutWidget, TableWidget)
from pyqtgraph.widgets.MatplotlibWidget import MatplotlibWidget
from . import resources_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1659, 937)
        MainWindow.setLocale(QLocale(QLocale.English, QLocale.Germany))
        MainWindow.setDockNestingEnabled(True)
        self.action_load_file = QAction(MainWindow)
        self.action_load_file.setObjectName(u"action_load_file")
        icon = QIcon()
        icon.addFile(u":/icons/file_import", QSize(), QIcon.Normal, QIcon.Off)
        self.action_load_file.setIcon(icon)
        self.action_show_edit_page = QAction(MainWindow)
        self.action_show_edit_page.setObjectName(u"action_show_edit_page")
        icon1 = QIcon()
        icon1.addFile(u":/icons/view_plots", QSize(), QIcon.Normal, QIcon.Off)
        self.action_show_edit_page.setIcon(icon1)
        self.action_show_edit_page.setMenuRole(QAction.NoRole)
        self.action_show_import_page = QAction(MainWindow)
        self.action_show_import_page.setObjectName(u"action_show_import_page")
        icon2 = QIcon()
        icon2.addFile(u":/icons/table_import", QSize(), QIcon.Normal, QIcon.Off)
        self.action_show_import_page.setIcon(icon2)
        self.action_show_import_page.setMenuRole(QAction.NoRole)
        self.action_show_result_page = QAction(MainWindow)
        self.action_show_result_page.setObjectName(u"action_show_result_page")
        icon3 = QIcon()
        icon3.addFile(u":/icons/view_result", QSize(), QIcon.Normal, QIcon.Off)
        self.action_show_result_page.setIcon(icon3)
        self.action_show_result_page.setMenuRole(QAction.NoRole)
        self.action_show_export_page = QAction(MainWindow)
        self.action_show_export_page.setObjectName(u"action_show_export_page")
        icon4 = QIcon()
        icon4.addFile(u":/icons/table_export", QSize(), QIcon.Normal, QIcon.Off)
        self.action_show_export_page.setIcon(icon4)
        self.action_show_export_page.setMenuRole(QAction.NoRole)
        self.action_edit_undo = QAction(MainWindow)
        self.action_edit_undo.setObjectName(u"action_edit_undo")
        icon5 = QIcon()
        icon5.addFile(u":/icons/edit_undo", QSize(), QIcon.Normal, QIcon.Off)
        self.action_edit_undo.setIcon(icon5)
        self.action_edit_redo = QAction(MainWindow)
        self.action_edit_redo.setObjectName(u"action_edit_redo")
        icon6 = QIcon()
        icon6.addFile(u":/icons/edit_redo", QSize(), QIcon.Normal, QIcon.Off)
        self.action_edit_redo.setIcon(icon6)
        self.action_show_test_page = QAction(MainWindow)
        self.action_show_test_page.setObjectName(u"action_show_test_page")
        icon7 = QIcon()
        icon7.addFile(u":/icons/no_access", QSize(), QIcon.Normal, QIcon.Off)
        self.action_show_test_page.setIcon(icon7)
        self.action_show_test_page.setMenuRole(QAction.NoRole)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout_4 = QGridLayout(self.centralwidget)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.gridLayout_4.setContentsMargins(0, 0, 0, 0)
        self.stackedWidget = QStackedWidget(self.centralwidget)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.stacked_page_import = QWidget()
        self.stacked_page_import.setObjectName(u"stacked_page_import")
        self.gridLayout = QGridLayout(self.stacked_page_import)
        self.gridLayout.setObjectName(u"gridLayout")
        self.table_view_import_data = QTableView(self.stacked_page_import)
        self.table_view_import_data.setObjectName(u"table_view_import_data")
        self.table_view_import_data.horizontalHeader().setCascadingSectionResizes(True)
        self.table_view_import_data.horizontalHeader().setStretchLastSection(True)
        self.table_view_import_data.verticalHeader().setVisible(False)
        self.table_view_import_data.verticalHeader().setHighlightSections(False)

        self.gridLayout.addWidget(self.table_view_import_data, 0, 1, 1, 1)

        self.column_view_import_metadata = QColumnView(self.stacked_page_import)
        self.column_view_import_metadata.setObjectName(u"column_view_import_metadata")
        self.column_view_import_metadata.setEditTriggers(QAbstractItemView.DoubleClicked|QAbstractItemView.EditKeyPressed|QAbstractItemView.SelectedClicked)

        self.gridLayout.addWidget(self.column_view_import_metadata, 0, 0, 1, 1)

        self.stackedWidget.addWidget(self.stacked_page_import)
        self.stacked_page_edit = QWidget()
        self.stacked_page_edit.setObjectName(u"stacked_page_edit")
        self.gridLayout_2 = QGridLayout(self.stacked_page_edit)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.pg_graphics_layout_widget = GraphicsLayoutWidget(self.stacked_page_edit)
        self.pg_graphics_layout_widget.setObjectName(u"pg_graphics_layout_widget")

        self.gridLayout_2.addWidget(self.pg_graphics_layout_widget, 0, 0, 1, 1)

        self.stackedWidget.addWidget(self.stacked_page_edit)
        self.stacked_page_result = QWidget()
        self.stacked_page_result.setObjectName(u"stacked_page_result")
        self.gridLayout_5 = QGridLayout(self.stacked_page_result)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.splitter = QSplitter(self.stacked_page_result)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Horizontal)
        self.splitter.setChildrenCollapsible(False)
        self.table_widget_mpl_data = TableWidget(self.splitter)
        self.table_widget_mpl_data.setObjectName(u"table_widget_mpl_data")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.table_widget_mpl_data.sizePolicy().hasHeightForWidth())
        self.table_widget_mpl_data.setSizePolicy(sizePolicy)
        self.table_widget_mpl_data.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        self.table_widget_mpl_data.setEditTriggers(QAbstractItemView.DoubleClicked|QAbstractItemView.EditKeyPressed)
        self.table_widget_mpl_data.setSortingEnabled(True)
        self.splitter.addWidget(self.table_widget_mpl_data)
        self.table_widget_mpl_data.horizontalHeader().setCascadingSectionResizes(True)
        self.mpl_widget = MatplotlibWidget(self.splitter)
        self.mpl_widget.setObjectName(u"mpl_widget")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.mpl_widget.sizePolicy().hasHeightForWidth())
        self.mpl_widget.setSizePolicy(sizePolicy1)
        self.mpl_widget.setMinimumSize(QSize(500, 0))
        self.splitter.addWidget(self.mpl_widget)

        self.gridLayout_5.addWidget(self.splitter, 0, 0, 1, 1)

        self.stackedWidget.addWidget(self.stacked_page_result)
        self.stacked_page_export = QWidget()
        self.stacked_page_export.setObjectName(u"stacked_page_export")
        self.gridLayout_3 = QGridLayout(self.stacked_page_export)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.table_view_export_data = QTableView(self.stacked_page_export)
        self.table_view_export_data.setObjectName(u"table_view_export_data")

        self.gridLayout_3.addWidget(self.table_view_export_data, 0, 0, 1, 1)

        self.stackedWidget.addWidget(self.stacked_page_export)
        self.stacked_page_test = QWidget()
        self.stacked_page_test.setObjectName(u"stacked_page_test")
        self.gridLayout_6 = QGridLayout(self.stacked_page_test)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.stackedWidget.addWidget(self.stacked_page_test)

        self.gridLayout_4.addWidget(self.stackedWidget, 0, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1659, 22))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuEdit = QMenu(self.menubar)
        self.menuEdit.setObjectName(u"menuEdit")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.toolBarLeft = QToolBar(MainWindow)
        self.toolBarLeft.setObjectName(u"toolBarLeft")
        self.toolBarLeft.setMovable(False)
        self.toolBarLeft.setFloatable(False)
        MainWindow.addToolBar(Qt.LeftToolBarArea, self.toolBarLeft)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menuFile.addAction(self.action_load_file)
        self.menuEdit.addAction(self.action_edit_undo)
        self.menuEdit.addAction(self.action_edit_redo)
        self.toolBarLeft.addAction(self.action_show_import_page)
        self.toolBarLeft.addAction(self.action_show_edit_page)
        self.toolBarLeft.addAction(self.action_show_result_page)
        self.toolBarLeft.addAction(self.action_show_export_page)
        self.toolBarLeft.addAction(self.action_show_test_page)

        self.retranslateUi(MainWindow)

        self.stackedWidget.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Signal Editor", None))
        self.action_load_file.setText(QCoreApplication.translate("MainWindow", u"Load File", None))
        self.action_show_edit_page.setText(QCoreApplication.translate("MainWindow", u"Edit", None))
#if QT_CONFIG(tooltip)
        self.action_show_edit_page.setToolTip(QCoreApplication.translate("MainWindow", u"Apply processing and peak detection algorithms", None))
#endif // QT_CONFIG(tooltip)
        self.action_show_import_page.setText(QCoreApplication.translate("MainWindow", u"Data Import", None))
#if QT_CONFIG(tooltip)
        self.action_show_import_page.setToolTip(QCoreApplication.translate("MainWindow", u"Import data files", None))
#endif // QT_CONFIG(tooltip)
        self.action_show_result_page.setText(QCoreApplication.translate("MainWindow", u"Results", None))
#if QT_CONFIG(tooltip)
        self.action_show_result_page.setToolTip(QCoreApplication.translate("MainWindow", u"Overview of results", None))
#endif // QT_CONFIG(tooltip)
        self.action_show_export_page.setText(QCoreApplication.translate("MainWindow", u"Export", None))
#if QT_CONFIG(tooltip)
        self.action_show_export_page.setToolTip(QCoreApplication.translate("MainWindow", u"Export your results", None))
#endif // QT_CONFIG(tooltip)
        self.action_edit_undo.setText(QCoreApplication.translate("MainWindow", u"Undo", None))
        self.action_edit_redo.setText(QCoreApplication.translate("MainWindow", u"Redo", None))
        self.action_show_test_page.setText(QCoreApplication.translate("MainWindow", u"Testing OpenGL", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuEdit.setTitle(QCoreApplication.translate("MainWindow", u"Edit", None))
        self.toolBarLeft.setWindowTitle(QCoreApplication.translate("MainWindow", u"toolBarLeft", None))
    # retranslateUi

