# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.7.0
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
from PySide6.QtWidgets import (QAbstractItemView, QAbstractScrollArea, QApplication, QComboBox,
    QFormLayout, QFrame, QGridLayout, QGroupBox,
    QHeaderView, QLabel, QMainWindow, QMenu,
    QMenuBar, QPushButton, QSizePolicy, QSpinBox,
    QSplitter, QStackedWidget, QStatusBar, QTableView,
    QTableWidgetItem, QToolBar, QWidget)

from pyqtgraph import TableWidget
from pyqtgraph.widgets.MatplotlibWidget import MatplotlibWidget
from superqt import QCollapsible
from . import resources_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1660, 937)
        MainWindow.setLocale(QLocale(QLocale.English, QLocale.Germany))
        MainWindow.setDockNestingEnabled(True)
        self.action_open_file = QAction(MainWindow)
        self.action_open_file.setObjectName(u"action_open_file")
        icon = QIcon()
        icon.addFile(u":/icons/folder-open", QSize(), QIcon.Normal, QIcon.Off)
        self.action_open_file.setIcon(icon)
        self.action_show_edit_page = QAction(MainWindow)
        self.action_show_edit_page.setObjectName(u"action_show_edit_page")
        self.action_show_edit_page.setCheckable(True)
        icon1 = QIcon()
        icon1.addFile(u":/icons/app_wave", QSize(), QIcon.Normal, QIcon.Off)
        self.action_show_edit_page.setIcon(icon1)
        self.action_show_edit_page.setMenuRole(QAction.MenuRole.NoRole)
        self.action_show_import_page = QAction(MainWindow)
        self.action_show_import_page.setObjectName(u"action_show_import_page")
        self.action_show_import_page.setCheckable(True)
        icon2 = QIcon()
        icon2.addFile(u":/icons/table_edit", QSize(), QIcon.Normal, QIcon.Off)
        self.action_show_import_page.setIcon(icon2)
        self.action_show_import_page.setMenuRole(QAction.MenuRole.NoRole)
        self.action_show_result_page = QAction(MainWindow)
        self.action_show_result_page.setObjectName(u"action_show_result_page")
        self.action_show_result_page.setCheckable(True)
        icon3 = QIcon()
        icon3.addFile(u":/icons/view_result", QSize(), QIcon.Normal, QIcon.Off)
        self.action_show_result_page.setIcon(icon3)
        self.action_show_result_page.setMenuRole(QAction.MenuRole.NoRole)
        self.action_show_export_page = QAction(MainWindow)
        self.action_show_export_page.setObjectName(u"action_show_export_page")
        self.action_show_export_page.setCheckable(True)
        icon4 = QIcon()
        icon4.addFile(u":/icons/table_export", QSize(), QIcon.Normal, QIcon.Off)
        self.action_show_export_page.setIcon(icon4)
        self.action_show_export_page.setMenuRole(QAction.MenuRole.NoRole)
        self.action_show_info_page = QAction(MainWindow)
        self.action_show_info_page.setObjectName(u"action_show_info_page")
        self.action_show_info_page.setCheckable(True)
        icon5 = QIcon()
        icon5.addFile(u":/icons/app_monitor", QSize(), QIcon.Normal, QIcon.Off)
        self.action_show_info_page.setIcon(icon5)
        self.action_show_info_page.setMenuRole(QAction.MenuRole.NoRole)
        self.action_show_settings = QAction(MainWindow)
        self.action_show_settings.setObjectName(u"action_show_settings")
        icon6 = QIcon()
        icon6.addFile(u":/icons/view_settings", QSize(), QIcon.Normal, QIcon.Off)
        self.action_show_settings.setIcon(icon6)
        self.action_show_settings.setMenuRole(QAction.MenuRole.PreferencesRole)
        self.action_edit_metadata = QAction(MainWindow)
        self.action_edit_metadata.setObjectName(u"action_edit_metadata")
        self.action_edit_metadata.setEnabled(False)
        icon7 = QIcon()
        icon7.addFile(u":/icons/edit", QSize(), QIcon.Normal, QIcon.Off)
        self.action_edit_metadata.setIcon(icon7)
        self.action_close_file = QAction(MainWindow)
        self.action_close_file.setObjectName(u"action_close_file")
        self.action_close_file.setEnabled(False)
        icon8 = QIcon()
        icon8.addFile(u":/icons/cross_close", QSize(), QIcon.Normal, QIcon.Off)
        self.action_close_file.setIcon(icon8)
        self.action_close_file.setMenuRole(QAction.MenuRole.NoRole)
        self.action_export_result = QAction(MainWindow)
        self.action_export_result.setObjectName(u"action_export_result")
        self.action_export_result.setIcon(icon4)
        self.action_export_result.setMenuRole(QAction.MenuRole.NoRole)
        self.action_create_new_section = QAction(MainWindow)
        self.action_create_new_section.setObjectName(u"action_create_new_section")
        self.action_create_new_section.setCheckable(True)
        icon9 = QIcon()
        icon9.addFile(u":/icons/app_plus", QSize(), QIcon.Normal, QIcon.Off)
        self.action_create_new_section.setIcon(icon9)
        self.action_create_new_section.setMenuRole(QAction.MenuRole.NoRole)
        self.action_show_filter_inputs = QAction(MainWindow)
        self.action_show_filter_inputs.setObjectName(u"action_show_filter_inputs")
        icon10 = QIcon()
        icon10.addFile(u":/icons/view_app_monitor", QSize(), QIcon.Normal, QIcon.Off)
        self.action_show_filter_inputs.setIcon(icon10)
        self.action_show_filter_inputs.setMenuRole(QAction.MenuRole.NoRole)
        self.action_toggle_auto_scaling = QAction(MainWindow)
        self.action_toggle_auto_scaling.setObjectName(u"action_toggle_auto_scaling")
        self.action_toggle_auto_scaling.setCheckable(True)
        icon11 = QIcon()
        icon11.addFile(u":/icons/toggle_autoscale", QSize(), QIcon.Normal, QIcon.Off)
        self.action_toggle_auto_scaling.setIcon(icon11)
        self.action_toggle_auto_scaling.setMenuRole(QAction.MenuRole.NoRole)
        self.action_confirm_section = QAction(MainWindow)
        self.action_confirm_section.setObjectName(u"action_confirm_section")
        icon12 = QIcon()
        icon12.addFile(u":/icons/tick_mark", QSize(), QIcon.Normal, QIcon.Off)
        self.action_confirm_section.setIcon(icon12)
        self.action_confirm_section.setMenuRole(QAction.MenuRole.NoRole)
        self.action_cancel_section = QAction(MainWindow)
        self.action_cancel_section.setObjectName(u"action_cancel_section")
        icon13 = QIcon()
        icon13.addFile(u":/icons/no_access", QSize(), QIcon.Normal, QIcon.Off)
        self.action_cancel_section.setIcon(icon13)
        self.action_cancel_section.setMenuRole(QAction.MenuRole.NoRole)
        self.action_show_section_overview = QAction(MainWindow)
        self.action_show_section_overview.setObjectName(u"action_show_section_overview")
        self.action_show_section_overview.setCheckable(True)
        self.action_show_section_overview.setChecked(True)
        icon14 = QIcon()
        icon14.addFile(u":/icons/app_ab", QSize(), QIcon.Normal, QIcon.Off)
        self.action_show_section_overview.setIcon(icon14)
        self.action_show_section_overview.setMenuRole(QAction.MenuRole.NoRole)
        self.action_remove_peaks_in_selection = QAction(MainWindow)
        self.action_remove_peaks_in_selection.setObjectName(u"action_remove_peaks_in_selection")
        icon15 = QIcon()
        icon15.addFile(u":/icons/search_minus", QSize(), QIcon.Normal, QIcon.Off)
        self.action_remove_peaks_in_selection.setIcon(icon15)
        self.action_remove_peaks_in_selection.setMenuRole(QAction.MenuRole.NoRole)
        self.action_find_peaks_in_selection = QAction(MainWindow)
        self.action_find_peaks_in_selection.setObjectName(u"action_find_peaks_in_selection")
        icon16 = QIcon()
        icon16.addFile(u":/icons/search_plus", QSize(), QIcon.Normal, QIcon.Off)
        self.action_find_peaks_in_selection.setIcon(icon16)
        self.action_find_peaks_in_selection.setMenuRole(QAction.MenuRole.NoRole)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout_4 = QGridLayout(self.centralwidget)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.gridLayout_4.setContentsMargins(0, 0, 0, 0)
        self.stackedWidget = QStackedWidget(self.centralwidget)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.stacked_page_import = QWidget()
        self.stacked_page_import.setObjectName(u"stacked_page_import")
        self.gridLayout_8 = QGridLayout(self.stacked_page_import)
        self.gridLayout_8.setObjectName(u"gridLayout_8")
        self.splitter_2 = QSplitter(self.stacked_page_import)
        self.splitter_2.setObjectName(u"splitter_2")
        self.splitter_2.setOrientation(Qt.Orientation.Horizontal)
        self.container_file_information = QWidget(self.splitter_2)
        self.container_file_information.setObjectName(u"container_file_information")
        self.gridLayout = QGridLayout(self.container_file_information)
        self.gridLayout.setObjectName(u"gridLayout")
        self.btn_load_data = QPushButton(self.container_file_information)
        self.btn_load_data.setObjectName(u"btn_load_data")
        self.btn_load_data.setEnabled(False)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_load_data.sizePolicy().hasHeightForWidth())
        self.btn_load_data.setSizePolicy(sizePolicy)
        self.btn_load_data.setMinimumSize(QSize(0, 50))
        icon17 = QIcon()
        icon17.addFile(u":/icons/table_import", QSize(), QIcon.Normal, QIcon.Off)
        self.btn_load_data.setIcon(icon17)

        self.gridLayout.addWidget(self.btn_load_data, 3, 2, 1, 1)

        self.collapsible_frame = QCollapsible(self.container_file_information)
        self.collapsible_frame.setObjectName(u"collapsible_frame")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.collapsible_frame.sizePolicy().hasHeightForWidth())
        self.collapsible_frame.setSizePolicy(sizePolicy1)
        self.collapsible_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.collapsible_frame.setFrameShadow(QFrame.Shadow.Raised)

        self.gridLayout.addWidget(self.collapsible_frame, 1, 0, 1, 3)

        self.btn_close_file = QPushButton(self.container_file_information)
        self.btn_close_file.setObjectName(u"btn_close_file")
        self.btn_close_file.setEnabled(False)
        self.btn_close_file.setMinimumSize(QSize(0, 50))
        icon18 = QIcon()
        icon18.addFile(u":/icons/delete", QSize(), QIcon.Normal, QIcon.Off)
        self.btn_close_file.setIcon(icon18)

        self.gridLayout.addWidget(self.btn_close_file, 3, 1, 1, 1)

        self.label_2 = QLabel(self.container_file_information)
        self.label_2.setObjectName(u"label_2")
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 3)

        self.btn_open_file = QPushButton(self.container_file_information)
        self.btn_open_file.setObjectName(u"btn_open_file")
        sizePolicy.setHeightForWidth(self.btn_open_file.sizePolicy().hasHeightForWidth())
        self.btn_open_file.setSizePolicy(sizePolicy)
        self.btn_open_file.setMinimumSize(QSize(0, 50))
        self.btn_open_file.setIcon(icon)

        self.gridLayout.addWidget(self.btn_open_file, 3, 0, 1, 1)

        self.groupBox = QGroupBox(self.container_file_information)
        self.groupBox.setObjectName(u"groupBox")
        self.formLayout = QFormLayout(self.groupBox)
        self.formLayout.setObjectName(u"formLayout")
        self.samplingRateLabel = QLabel(self.groupBox)
        self.samplingRateLabel.setObjectName(u"samplingRateLabel")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.samplingRateLabel)

        self.spin_box_sampling_rate_import_page = QSpinBox(self.groupBox)
        self.spin_box_sampling_rate_import_page.setObjectName(u"spin_box_sampling_rate_import_page")
        self.spin_box_sampling_rate_import_page.setMaximum(10000)
        self.spin_box_sampling_rate_import_page.setValue(0)

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.spin_box_sampling_rate_import_page)

        self.signalColumnChannelLabel = QLabel(self.groupBox)
        self.signalColumnChannelLabel.setObjectName(u"signalColumnChannelLabel")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.signalColumnChannelLabel)

        self.combo_box_signal_column_import_page = QComboBox(self.groupBox)
        self.combo_box_signal_column_import_page.setObjectName(u"combo_box_signal_column_import_page")

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.combo_box_signal_column_import_page)

        self.infoColumnChannelLabel = QLabel(self.groupBox)
        self.infoColumnChannelLabel.setObjectName(u"infoColumnChannelLabel")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.infoColumnChannelLabel)

        self.combo_box_info_column_import_page = QComboBox(self.groupBox)
        self.combo_box_info_column_import_page.setObjectName(u"combo_box_info_column_import_page")

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.combo_box_info_column_import_page)


        self.gridLayout.addWidget(self.groupBox, 2, 0, 1, 3)

        self.splitter_2.addWidget(self.container_file_information)
        self.container_loaded_data_table = QWidget(self.splitter_2)
        self.container_loaded_data_table.setObjectName(u"container_loaded_data_table")
        self.gridLayout_7 = QGridLayout(self.container_loaded_data_table)
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.label = QLabel(self.container_loaded_data_table)
        self.label.setObjectName(u"label")

        self.gridLayout_7.addWidget(self.label, 0, 0, 1, 1)

        self.table_view_import_data = QTableView(self.container_loaded_data_table)
        self.table_view_import_data.setObjectName(u"table_view_import_data")
        self.table_view_import_data.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_view_import_data.setProperty("showDropIndicator", False)
        self.table_view_import_data.setDragDropOverwriteMode(False)
        self.table_view_import_data.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_view_import_data.setCornerButtonEnabled(False)
        self.table_view_import_data.horizontalHeader().setCascadingSectionResizes(True)
        self.table_view_import_data.verticalHeader().setVisible(False)
        self.table_view_import_data.verticalHeader().setHighlightSections(False)

        self.gridLayout_7.addWidget(self.table_view_import_data, 1, 0, 1, 1)

        self.splitter_2.addWidget(self.container_loaded_data_table)

        self.gridLayout_8.addWidget(self.splitter_2, 0, 0, 1, 1)

        self.stackedWidget.addWidget(self.stacked_page_import)
        self.stacked_page_edit = QWidget()
        self.stacked_page_edit.setObjectName(u"stacked_page_edit")
        self.gridLayout_2 = QGridLayout(self.stacked_page_edit)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.plot_container = QWidget(self.stacked_page_edit)
        self.plot_container.setObjectName(u"plot_container")

        self.gridLayout_2.addWidget(self.plot_container, 0, 0, 1, 1)

        self.stackedWidget.addWidget(self.stacked_page_edit)
        self.stacked_page_result = QWidget()
        self.stacked_page_result.setObjectName(u"stacked_page_result")
        self.gridLayout_5 = QGridLayout(self.stacked_page_result)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.splitter = QSplitter(self.stacked_page_result)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Orientation.Horizontal)
        self.splitter.setChildrenCollapsible(False)
        self.table_widget_mpl_data = TableWidget(self.splitter)
        self.table_widget_mpl_data.setObjectName(u"table_widget_mpl_data")
        sizePolicy1.setHeightForWidth(self.table_widget_mpl_data.sizePolicy().hasHeightForWidth())
        self.table_widget_mpl_data.setSizePolicy(sizePolicy1)
        self.table_widget_mpl_data.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.table_widget_mpl_data.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked|QAbstractItemView.EditTrigger.EditKeyPressed)
        self.table_widget_mpl_data.setSortingEnabled(True)
        self.splitter.addWidget(self.table_widget_mpl_data)
        self.table_widget_mpl_data.horizontalHeader().setCascadingSectionResizes(True)
        self.mpl_widget = MatplotlibWidget(self.splitter)
        self.mpl_widget.setObjectName(u"mpl_widget")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.mpl_widget.sizePolicy().hasHeightForWidth())
        self.mpl_widget.setSizePolicy(sizePolicy2)
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
        self.menubar.setGeometry(QRect(0, 0, 1660, 33))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuSettings = QMenu(self.menubar)
        self.menuSettings.setObjectName(u"menuSettings")
        self.menuView = QMenu(self.menubar)
        self.menuView.setObjectName(u"menuView")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.tool_bar_navigation = QToolBar(MainWindow)
        self.tool_bar_navigation.setObjectName(u"tool_bar_navigation")
        self.tool_bar_navigation.setMovable(False)
        self.tool_bar_navigation.setAllowedAreas(Qt.ToolBarArea.LeftToolBarArea)
        self.tool_bar_navigation.setFloatable(False)
        MainWindow.addToolBar(Qt.ToolBarArea.LeftToolBarArea, self.tool_bar_navigation)
        self.tool_bar_context_actions = QToolBar(MainWindow)
        self.tool_bar_context_actions.setObjectName(u"tool_bar_context_actions")
        self.tool_bar_context_actions.setMovable(False)
        self.tool_bar_context_actions.setAllowedAreas(Qt.ToolBarArea.TopToolBarArea)
        MainWindow.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.tool_bar_context_actions)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuSettings.menuAction())
        self.menuFile.addAction(self.action_open_file)
        self.menuFile.addAction(self.action_close_file)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.action_edit_metadata)
        self.menuSettings.addAction(self.action_show_settings)
        self.tool_bar_navigation.addAction(self.action_show_import_page)
        self.tool_bar_navigation.addAction(self.action_show_edit_page)
        self.tool_bar_navigation.addAction(self.action_show_result_page)
        self.tool_bar_navigation.addAction(self.action_show_export_page)
        self.tool_bar_navigation.addAction(self.action_show_info_page)
        self.tool_bar_context_actions.addAction(self.action_open_file)
        self.tool_bar_context_actions.addAction(self.action_edit_metadata)

        self.retranslateUi(MainWindow)

        self.stackedWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Signal Editor", None))
        self.action_open_file.setText(QCoreApplication.translate("MainWindow", u"Open File", None))
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
        self.action_show_info_page.setText(QCoreApplication.translate("MainWindow", u"App Info", None))
#if QT_CONFIG(tooltip)
        self.action_show_info_page.setToolTip(QCoreApplication.translate("MainWindow", u"Status Information", None))
#endif // QT_CONFIG(tooltip)
        self.action_show_settings.setText(QCoreApplication.translate("MainWindow", u"Settings", None))
#if QT_CONFIG(tooltip)
        self.action_show_settings.setToolTip(QCoreApplication.translate("MainWindow", u"Modify various settings", None))
#endif // QT_CONFIG(tooltip)
        self.action_edit_metadata.setText(QCoreApplication.translate("MainWindow", u"Edit Metadata", None))
        self.action_close_file.setText(QCoreApplication.translate("MainWindow", u"Close File", None))
#if QT_CONFIG(tooltip)
        self.action_close_file.setToolTip(QCoreApplication.translate("MainWindow", u"Closes the currently loaded file and refreshes the app state. Any changes made to the file will be lost, so make sure to export any results first.", None))
#endif // QT_CONFIG(tooltip)
        self.action_export_result.setText(QCoreApplication.translate("MainWindow", u"Export Result", None))
#if QT_CONFIG(tooltip)
        self.action_export_result.setToolTip(QCoreApplication.translate("MainWindow", u"Export results to the chosen file format", None))
#endif // QT_CONFIG(tooltip)
        self.action_create_new_section.setText(QCoreApplication.translate("MainWindow", u"New Section", None))
#if QT_CONFIG(tooltip)
        self.action_create_new_section.setToolTip(QCoreApplication.translate("MainWindow", u"Select a section of the data for processing", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(shortcut)
        self.action_create_new_section.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+N", None))
#endif // QT_CONFIG(shortcut)
        self.action_show_filter_inputs.setText(QCoreApplication.translate("MainWindow", u"Signal Filtering", None))
#if QT_CONFIG(tooltip)
        self.action_show_filter_inputs.setToolTip(QCoreApplication.translate("MainWindow", u"Show signal pre-processing options", None))
#endif // QT_CONFIG(tooltip)
        self.action_toggle_auto_scaling.setText(QCoreApplication.translate("MainWindow", u"Toggle Auto-Scaling", None))
#if QT_CONFIG(tooltip)
        self.action_toggle_auto_scaling.setToolTip(QCoreApplication.translate("MainWindow", u"Enable / Disable automatic y-axis scaling", None))
#endif // QT_CONFIG(tooltip)
        self.action_confirm_section.setText(QCoreApplication.translate("MainWindow", u"Confirm Section", None))
#if QT_CONFIG(tooltip)
        self.action_confirm_section.setToolTip(QCoreApplication.translate("MainWindow", u"Create a new section with the data of the selected region", None))
#endif // QT_CONFIG(tooltip)
        self.action_cancel_section.setText(QCoreApplication.translate("MainWindow", u"Cancel Section", None))
#if QT_CONFIG(tooltip)
        self.action_cancel_section.setToolTip(QCoreApplication.translate("MainWindow", u"Cancel the section creation process", None))
#endif // QT_CONFIG(tooltip)
        self.action_show_section_overview.setText(QCoreApplication.translate("MainWindow", u"Show Section Overview", None))
#if QT_CONFIG(tooltip)
        self.action_show_section_overview.setToolTip(QCoreApplication.translate("MainWindow", u"Shows the current sections as colored regions in the plot", None))
#endif // QT_CONFIG(tooltip)
        self.action_remove_peaks_in_selection.setText(QCoreApplication.translate("MainWindow", u"Remove Peaks in Selection", None))
#if QT_CONFIG(tooltip)
        self.action_remove_peaks_in_selection.setToolTip(QCoreApplication.translate("MainWindow", u"Deletes all peaks inside the selected area", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(shortcut)
        self.action_remove_peaks_in_selection.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+D", None))
#endif // QT_CONFIG(shortcut)
        self.action_find_peaks_in_selection.setText(QCoreApplication.translate("MainWindow", u"Find Peaks in Selection", None))
#if QT_CONFIG(tooltip)
        self.action_find_peaks_in_selection.setToolTip(QCoreApplication.translate("MainWindow", u"Detect peaks in just the selected area instead of the entire signal", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(shortcut)
        self.action_find_peaks_in_selection.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+F", None))
#endif // QT_CONFIG(shortcut)
#if QT_CONFIG(tooltip)
        self.btn_load_data.setToolTip(QCoreApplication.translate("MainWindow", u"Load data from the selected file using the settings shown above", None))
#endif // QT_CONFIG(tooltip)
        self.btn_load_data.setText(QCoreApplication.translate("MainWindow", u" Load Data", None))
        self.btn_close_file.setText(QCoreApplication.translate("MainWindow", u" Close File", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:14pt; font-weight:700;\">File Information</span></p></body></html>", None))
        self.btn_open_file.setText(QCoreApplication.translate("MainWindow", u" Open File", None))
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"Required Information", None))
        self.samplingRateLabel.setText(QCoreApplication.translate("MainWindow", u"Sampling Rate", None))
        self.spin_box_sampling_rate_import_page.setSuffix(QCoreApplication.translate("MainWindow", u" Hz", None))
        self.signalColumnChannelLabel.setText(QCoreApplication.translate("MainWindow", u"Signal Column / Channel", None))
        self.infoColumnChannelLabel.setText(QCoreApplication.translate("MainWindow", u"Info Column / Channel", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:14pt; font-weight:700;\">Loaded Data</span></p></body></html>", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuSettings.setTitle(QCoreApplication.translate("MainWindow", u"Settings", None))
        self.menuView.setTitle(QCoreApplication.translate("MainWindow", u"View", None))
        self.tool_bar_navigation.setWindowTitle(QCoreApplication.translate("MainWindow", u"Navigation Toolbar", None))
        self.tool_bar_context_actions.setWindowTitle(QCoreApplication.translate("MainWindow", u"Editing Toolbar", None))
    # retranslateUi

