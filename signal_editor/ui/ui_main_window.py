# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.7.2
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
from PySide6.QtWidgets import (QAbstractItemView, QAbstractScrollArea, QApplication, QFormLayout,
    QFrame, QGridLayout, QGroupBox, QHBoxLayout,
    QHeaderView, QLabel, QListWidgetItem, QMainWindow,
    QMenuBar, QSizePolicy, QStackedWidget, QTabWidget,
    QToolBar, QVBoxLayout, QWidget)

from pyqtgraph.widgets.MatplotlibWidget import MatplotlibWidget
from qfluentwidgets import (BodyLabel, ComboBox, LineEdit, ListWidget,
    PushButton, RoundMenu, SpinBox, StrongBodyLabel,
    SubtitleLabel, TableView)
from superqt import QCollapsible
from . import resources_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1660, 937)
        MainWindow.setDockNestingEnabled(True)
        MainWindow.setDockOptions(QMainWindow.DockOption.AllowNestedDocks|QMainWindow.DockOption.AllowTabbedDocks|QMainWindow.DockOption.AnimatedDocks|QMainWindow.DockOption.VerticalTabs)
        self.action_open_file = QAction(MainWindow)
        self.action_open_file.setObjectName(u"action_open_file")
        icon = QIcon()
        icon.addFile(u":/icons/fluent-icons/FolderOpen.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.action_open_file.setIcon(icon)
        self.action_open_file.setIconVisibleInMenu(False)
        self.action_show_settings = QAction(MainWindow)
        self.action_show_settings.setObjectName(u"action_show_settings")
        icon1 = QIcon()
        icon1.addFile(u":/icons/fluent-icons/Settings.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.action_show_settings.setIcon(icon1)
        self.action_show_settings.setMenuRole(QAction.MenuRole.PreferencesRole)
        self.action_edit_metadata = QAction(MainWindow)
        self.action_edit_metadata.setObjectName(u"action_edit_metadata")
        self.action_edit_metadata.setEnabled(False)
        icon2 = QIcon()
        icon2.addFile(u":/icons/fluent-icons/DocumentToolbox.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.action_edit_metadata.setIcon(icon2)
        self.action_edit_metadata.setIconVisibleInMenu(False)
        self.action_close_file = QAction(MainWindow)
        self.action_close_file.setObjectName(u"action_close_file")
        self.action_close_file.setEnabled(False)
        icon3 = QIcon()
        icon3.addFile(u":/icons/fluent-icons/DocumentDismiss.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.action_close_file.setIcon(icon3)
        self.action_close_file.setMenuRole(QAction.MenuRole.NoRole)
        self.action_close_file.setIconVisibleInMenu(False)
        self.action_export_result = QAction(MainWindow)
        self.action_export_result.setObjectName(u"action_export_result")
        icon4 = QIcon()
        icon4.addFile(u":/icons/fluent-icons/ArrowExportLtr.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.action_export_result.setIcon(icon4)
        self.action_export_result.setMenuRole(QAction.MenuRole.NoRole)
        self.action_create_new_section = QAction(MainWindow)
        self.action_create_new_section.setObjectName(u"action_create_new_section")
        self.action_create_new_section.setCheckable(True)
        icon5 = QIcon()
        icon5.addFile(u":/icons/fluent-icons/Add.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.action_create_new_section.setIcon(icon5)
        self.action_create_new_section.setMenuRole(QAction.MenuRole.NoRole)
        self.action_toggle_auto_scaling = QAction(MainWindow)
        self.action_toggle_auto_scaling.setObjectName(u"action_toggle_auto_scaling")
        self.action_toggle_auto_scaling.setCheckable(True)
        icon6 = QIcon()
        icon6.addFile(u":/icons/fluent-icons/AutoFitHeight.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.action_toggle_auto_scaling.setIcon(icon6)
        self.action_toggle_auto_scaling.setMenuRole(QAction.MenuRole.NoRole)
        self.action_confirm_section = QAction(MainWindow)
        self.action_confirm_section.setObjectName(u"action_confirm_section")
        icon7 = QIcon()
        icon7.addFile(u":/icons/fluent-icons/Checkmark.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.action_confirm_section.setIcon(icon7)
        self.action_confirm_section.setMenuRole(QAction.MenuRole.NoRole)
        self.action_cancel_section = QAction(MainWindow)
        self.action_cancel_section.setObjectName(u"action_cancel_section")
        icon8 = QIcon()
        icon8.addFile(u":/icons/fluent-icons/Dismiss.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.action_cancel_section.setIcon(icon8)
        self.action_cancel_section.setMenuRole(QAction.MenuRole.NoRole)
        self.action_show_section_overview = QAction(MainWindow)
        self.action_show_section_overview.setObjectName(u"action_show_section_overview")
        self.action_show_section_overview.setCheckable(True)
        self.action_show_section_overview.setChecked(False)
        icon9 = QIcon()
        icon9.addFile(u":/icons/fluent-icons/EyeHide.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        icon9.addFile(u":/icons/fluent-icons/EyeShow.svg", QSize(), QIcon.Mode.Normal, QIcon.State.On)
        self.action_show_section_overview.setIcon(icon9)
        self.action_show_section_overview.setMenuRole(QAction.MenuRole.NoRole)
        self.action_remove_peaks_in_selection = QAction(MainWindow)
        self.action_remove_peaks_in_selection.setObjectName(u"action_remove_peaks_in_selection")
        icon10 = QIcon()
        icon10.addFile(u":/icons/fluent-icons/Eraser.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.action_remove_peaks_in_selection.setIcon(icon10)
        self.action_remove_peaks_in_selection.setMenuRole(QAction.MenuRole.NoRole)
        self.action_find_peaks_in_selection = QAction(MainWindow)
        self.action_find_peaks_in_selection.setObjectName(u"action_find_peaks_in_selection")
        icon11 = QIcon()
        icon11.addFile(u":/icons/fluent-icons/SearchSquare.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.action_find_peaks_in_selection.setIcon(icon11)
        self.action_find_peaks_in_selection.setMenuRole(QAction.MenuRole.NoRole)
        self.action_show_user_guide = QAction(MainWindow)
        self.action_show_user_guide.setObjectName(u"action_show_user_guide")
        icon12 = QIcon()
        icon12.addFile(u":/icons/fluent-icons/BookQuestionMark.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.action_show_user_guide.setIcon(icon12)
        self.action_show_user_guide.setMenuRole(QAction.MenuRole.NoRole)
        self.action_about_qt = QAction(MainWindow)
        self.action_about_qt.setObjectName(u"action_about_qt")
        self.action_about_qt.setMenuRole(QAction.MenuRole.AboutQtRole)
        self.action_about_app = QAction(MainWindow)
        self.action_about_app.setObjectName(u"action_about_app")
        icon13 = QIcon()
        icon13.addFile(u":/icons/fluent-icons/Info.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.action_about_app.setIcon(icon13)
        self.action_about_app.setMenuRole(QAction.MenuRole.AboutRole)
        self.action_delete_section = QAction(MainWindow)
        self.action_delete_section.setObjectName(u"action_delete_section")
        icon14 = QIcon()
        icon14.addFile(u":/icons/fluent-icons/Delete.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.action_delete_section.setIcon(icon14)
        self.action_delete_section.setMenuRole(QAction.MenuRole.NoRole)
        self.action_clear_recent_files = QAction(MainWindow)
        self.action_clear_recent_files.setObjectName(u"action_clear_recent_files")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.h_layout_centralwidget = QHBoxLayout(self.centralwidget)
        self.h_layout_centralwidget.setObjectName(u"h_layout_centralwidget")
        self.h_layout_centralwidget.setContentsMargins(0, 0, 0, 0)
        self.stackedWidget = QStackedWidget(self.centralwidget)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.stacked_page_import = QWidget()
        self.stacked_page_import.setObjectName(u"stacked_page_import")
        self.horizontalLayout = QHBoxLayout(self.stacked_page_import)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.container_file_information = QWidget(self.stacked_page_import)
        self.container_file_information.setObjectName(u"container_file_information")
        self.gridLayout = QGridLayout(self.container_file_information)
        self.gridLayout.setObjectName(u"gridLayout")
        self.btn_load_data = PushButton(self.container_file_information)
        self.btn_load_data.setObjectName(u"btn_load_data")
        self.btn_load_data.setEnabled(False)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_load_data.sizePolicy().hasHeightForWidth())
        self.btn_load_data.setSizePolicy(sizePolicy)
        self.btn_load_data.setMinimumSize(QSize(0, 41))
        icon15 = QIcon()
        icon15.addFile(u":/icons/fluent-icons/DocumentArrowRight.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.btn_load_data.setIcon(icon15)

        self.gridLayout.addWidget(self.btn_load_data, 3, 0, 1, 2)

        self.grp_box_required_info = QGroupBox(self.container_file_information)
        self.grp_box_required_info.setObjectName(u"grp_box_required_info")
        sizePolicy.setHeightForWidth(self.grp_box_required_info.sizePolicy().hasHeightForWidth())
        self.grp_box_required_info.setSizePolicy(sizePolicy)
        self.grp_box_required_info.setFlat(True)
        self.formLayout = QFormLayout(self.grp_box_required_info)
        self.formLayout.setObjectName(u"formLayout")
        self.samplingRateLabel = BodyLabel(self.grp_box_required_info)
        self.samplingRateLabel.setObjectName(u"samplingRateLabel")
        self.samplingRateLabel.setMinimumSize(QSize(0, 31))

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.samplingRateLabel)

        self.spin_box_sampling_rate_import_page = SpinBox(self.grp_box_required_info)
        self.spin_box_sampling_rate_import_page.setObjectName(u"spin_box_sampling_rate_import_page")
        self.spin_box_sampling_rate_import_page.setMinimumSize(QSize(0, 31))
        self.spin_box_sampling_rate_import_page.setFrame(False)
        self.spin_box_sampling_rate_import_page.setMaximum(10000)
        self.spin_box_sampling_rate_import_page.setValue(0)

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.spin_box_sampling_rate_import_page)

        self.signalColumnChannelLabel = BodyLabel(self.grp_box_required_info)
        self.signalColumnChannelLabel.setObjectName(u"signalColumnChannelLabel")
        self.signalColumnChannelLabel.setMinimumSize(QSize(0, 31))

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.signalColumnChannelLabel)

        self.combo_box_signal_column_import_page = ComboBox(self.grp_box_required_info)
        self.combo_box_signal_column_import_page.setObjectName(u"combo_box_signal_column_import_page")
        self.combo_box_signal_column_import_page.setMinimumSize(QSize(0, 31))

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.combo_box_signal_column_import_page)

        self.combo_box_info_column_import_page = ComboBox(self.grp_box_required_info)
        self.combo_box_info_column_import_page.setObjectName(u"combo_box_info_column_import_page")
        self.combo_box_info_column_import_page.setMinimumSize(QSize(0, 31))

        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.combo_box_info_column_import_page)

        self.infoColumnChannelLabel = BodyLabel(self.grp_box_required_info)
        self.infoColumnChannelLabel.setObjectName(u"infoColumnChannelLabel")
        self.infoColumnChannelLabel.setMinimumSize(QSize(0, 31))

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.infoColumnChannelLabel)

        self.line = QFrame(self.grp_box_required_info)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.formLayout.setWidget(2, QFormLayout.SpanningRole, self.line)

        self.label_5 = QLabel(self.grp_box_required_info)
        self.label_5.setObjectName(u"label_5")

        self.formLayout.setWidget(4, QFormLayout.SpanningRole, self.label_5)


        self.gridLayout.addWidget(self.grp_box_required_info, 2, 0, 1, 3)

        self.line_edit_active_file = LineEdit(self.container_file_information)
        self.line_edit_active_file.setObjectName(u"line_edit_active_file")
        self.line_edit_active_file.setMinimumSize(QSize(0, 31))
        self.line_edit_active_file.setFrame(False)
        self.line_edit_active_file.setReadOnly(True)

        self.gridLayout.addWidget(self.line_edit_active_file, 1, 1, 1, 2)

        self.tab_widget_files_properties = QTabWidget(self.container_file_information)
        self.tab_widget_files_properties.setObjectName(u"tab_widget_files_properties")
        self.tab_recent_files = QWidget()
        self.tab_recent_files.setObjectName(u"tab_recent_files")
        self.verticalLayout_3 = QVBoxLayout(self.tab_recent_files)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.list_widget_recent_files = ListWidget(self.tab_recent_files)
        self.list_widget_recent_files.setObjectName(u"list_widget_recent_files")

        self.verticalLayout_3.addWidget(self.list_widget_recent_files)

        self.tab_widget_files_properties.addTab(self.tab_recent_files, "")
        self.tab_file_metadata = QWidget()
        self.tab_file_metadata.setObjectName(u"tab_file_metadata")
        self.verticalLayout_4 = QVBoxLayout(self.tab_file_metadata)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.collapsible_frame = QCollapsible(self.tab_file_metadata)
        self.collapsible_frame.setObjectName(u"collapsible_frame")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.collapsible_frame.sizePolicy().hasHeightForWidth())
        self.collapsible_frame.setSizePolicy(sizePolicy1)
        self.collapsible_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.collapsible_frame.setFrameShadow(QFrame.Shadow.Raised)

        self.verticalLayout_4.addWidget(self.collapsible_frame)

        self.tab_widget_files_properties.addTab(self.tab_file_metadata, "")

        self.gridLayout.addWidget(self.tab_widget_files_properties, 4, 0, 1, 3)

        self.btn_open_file = PushButton(self.container_file_information)
        self.btn_open_file.setObjectName(u"btn_open_file")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.btn_open_file.sizePolicy().hasHeightForWidth())
        self.btn_open_file.setSizePolicy(sizePolicy2)
        self.btn_open_file.setMinimumSize(QSize(0, 41))
        self.btn_open_file.setIcon(icon)

        self.gridLayout.addWidget(self.btn_open_file, 1, 0, 1, 1)

        self.btn_close_file = PushButton(self.container_file_information)
        self.btn_close_file.setObjectName(u"btn_close_file")
        self.btn_close_file.setEnabled(False)
        sizePolicy2.setHeightForWidth(self.btn_close_file.sizePolicy().hasHeightForWidth())
        self.btn_close_file.setSizePolicy(sizePolicy2)
        self.btn_close_file.setMinimumSize(QSize(0, 41))
        self.btn_close_file.setIcon(icon3)

        self.gridLayout.addWidget(self.btn_close_file, 3, 2, 1, 1)

        self.label_2 = SubtitleLabel(self.container_file_information)
        self.label_2.setObjectName(u"label_2")
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 3)


        self.horizontalLayout.addWidget(self.container_file_information)

        self.container_loaded_data_table = QWidget(self.stacked_page_import)
        self.container_loaded_data_table.setObjectName(u"container_loaded_data_table")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.container_loaded_data_table.sizePolicy().hasHeightForWidth())
        self.container_loaded_data_table.setSizePolicy(sizePolicy3)
        self.gridLayout_7 = QGridLayout(self.container_loaded_data_table)
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.label = SubtitleLabel(self.container_loaded_data_table)
        self.label.setObjectName(u"label")

        self.gridLayout_7.addWidget(self.label, 0, 0, 1, 1)

        self.label_showing_data_table = StrongBodyLabel(self.container_loaded_data_table)
        self.label_showing_data_table.setObjectName(u"label_showing_data_table")
        self.label_showing_data_table.setAlignment(Qt.AlignmentFlag.AlignBottom|Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing)

        self.gridLayout_7.addWidget(self.label_showing_data_table, 0, 1, 1, 1)

        self.table_view_import_data = TableView(self.container_loaded_data_table)
        self.table_view_import_data.setObjectName(u"table_view_import_data")
        self.table_view_import_data.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_view_import_data.setProperty("showDropIndicator", False)
        self.table_view_import_data.setDragDropOverwriteMode(False)
        self.table_view_import_data.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_view_import_data.setCornerButtonEnabled(False)
        self.table_view_import_data.horizontalHeader().setCascadingSectionResizes(True)
        self.table_view_import_data.verticalHeader().setVisible(False)
        self.table_view_import_data.verticalHeader().setHighlightSections(False)

        self.gridLayout_7.addWidget(self.table_view_import_data, 1, 0, 1, 2)


        self.horizontalLayout.addWidget(self.container_loaded_data_table)

        self.horizontalLayout.setStretch(0, 4)
        self.horizontalLayout.setStretch(1, 6)
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
        self.h_layout_result_page = QHBoxLayout(self.stacked_page_result)
        self.h_layout_result_page.setObjectName(u"h_layout_result_page")
        self.table_widget_mpl_data = TableView(self.stacked_page_result)
        self.table_widget_mpl_data.setObjectName(u"table_widget_mpl_data")
        sizePolicy1.setHeightForWidth(self.table_widget_mpl_data.sizePolicy().hasHeightForWidth())
        self.table_widget_mpl_data.setSizePolicy(sizePolicy1)
        self.table_widget_mpl_data.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.table_widget_mpl_data.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked|QAbstractItemView.EditTrigger.EditKeyPressed)
        self.table_widget_mpl_data.setSortingEnabled(True)
        self.table_widget_mpl_data.horizontalHeader().setHighlightSections(True)

        self.h_layout_result_page.addWidget(self.table_widget_mpl_data)

        self.mpl_widget = MatplotlibWidget(self.stacked_page_result)
        self.mpl_widget.setObjectName(u"mpl_widget")
        sizePolicy3.setHeightForWidth(self.mpl_widget.sizePolicy().hasHeightForWidth())
        self.mpl_widget.setSizePolicy(sizePolicy3)
        self.mpl_widget.setMinimumSize(QSize(500, 0))

        self.h_layout_result_page.addWidget(self.mpl_widget)

        self.h_layout_result_page.setStretch(0, 4)
        self.h_layout_result_page.setStretch(1, 6)
        self.stackedWidget.addWidget(self.stacked_page_result)
        self.stacked_page_export = QWidget()
        self.stacked_page_export.setObjectName(u"stacked_page_export")
        self.gridLayout_3 = QGridLayout(self.stacked_page_export)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.table_view_export_data = TableView(self.stacked_page_export)
        self.table_view_export_data.setObjectName(u"table_view_export_data")

        self.gridLayout_3.addWidget(self.table_view_export_data, 0, 0, 1, 1)

        self.stackedWidget.addWidget(self.stacked_page_export)
        self.stacked_page_test = QWidget()
        self.stacked_page_test.setObjectName(u"stacked_page_test")
        self.gridLayout_6 = QGridLayout(self.stacked_page_test)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.stackedWidget.addWidget(self.stacked_page_test)

        self.h_layout_centralwidget.addWidget(self.stackedWidget)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1660, 33))
        self.menuFile = RoundMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuOpen_Recent = RoundMenu(self.menuFile)
        self.menuOpen_Recent.setObjectName(u"menuOpen_Recent")
        self.menuSettings = RoundMenu(self.menubar)
        self.menuSettings.setObjectName(u"menuSettings")
        self.menuView = RoundMenu(self.menubar)
        self.menuView.setObjectName(u"menuView")
        self.menuEdit = RoundMenu(self.menubar)
        self.menuEdit.setObjectName(u"menuEdit")
        self.menuHelp = RoundMenu(self.menubar)
        self.menuHelp.setObjectName(u"menuHelp")
        MainWindow.setMenuBar(self.menubar)
        self.tool_bar_file_actions = QToolBar(MainWindow)
        self.tool_bar_file_actions.setObjectName(u"tool_bar_file_actions")
        self.tool_bar_file_actions.setMovable(False)
        self.tool_bar_file_actions.setAllowedAreas(Qt.ToolBarArea.TopToolBarArea)
        self.tool_bar_file_actions.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        MainWindow.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.tool_bar_file_actions)
        QWidget.setTabOrder(self.btn_open_file, self.line_edit_active_file)
        QWidget.setTabOrder(self.line_edit_active_file, self.spin_box_sampling_rate_import_page)
        QWidget.setTabOrder(self.spin_box_sampling_rate_import_page, self.combo_box_signal_column_import_page)
        QWidget.setTabOrder(self.combo_box_signal_column_import_page, self.combo_box_info_column_import_page)
        QWidget.setTabOrder(self.combo_box_info_column_import_page, self.btn_load_data)
        QWidget.setTabOrder(self.btn_load_data, self.btn_close_file)
        QWidget.setTabOrder(self.btn_close_file, self.tab_widget_files_properties)
        QWidget.setTabOrder(self.tab_widget_files_properties, self.list_widget_recent_files)
        QWidget.setTabOrder(self.list_widget_recent_files, self.table_view_import_data)
        QWidget.setTabOrder(self.table_view_import_data, self.table_widget_mpl_data)
        QWidget.setTabOrder(self.table_widget_mpl_data, self.table_view_export_data)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuSettings.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menuFile.addAction(self.action_open_file)
        self.menuFile.addAction(self.menuOpen_Recent.menuAction())
        self.menuFile.addAction(self.action_close_file)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.action_edit_metadata)
        self.menuOpen_Recent.addSeparator()
        self.menuOpen_Recent.addAction(self.action_clear_recent_files)
        self.menuSettings.addAction(self.action_show_settings)
        self.menuEdit.addAction(self.action_remove_peaks_in_selection)
        self.menuEdit.addAction(self.action_find_peaks_in_selection)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.action_show_section_overview)
        self.menuEdit.addAction(self.action_toggle_auto_scaling)
        self.menuHelp.addAction(self.action_show_user_guide)
        self.menuHelp.addSeparator()
        self.menuHelp.addAction(self.action_about_app)
        self.menuHelp.addAction(self.action_about_qt)
        self.tool_bar_file_actions.addAction(self.action_open_file)
        self.tool_bar_file_actions.addAction(self.action_edit_metadata)
        self.tool_bar_file_actions.addAction(self.action_close_file)

        self.retranslateUi(MainWindow)
        self.line_edit_active_file.textChanged.connect(MainWindow.setWindowTitle)

        self.stackedWidget.setCurrentIndex(0)
        self.tab_widget_files_properties.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Signal Editor", None))
        self.action_open_file.setText(QCoreApplication.translate("MainWindow", u"Open File", None))
        self.action_show_settings.setText(QCoreApplication.translate("MainWindow", u"Preferences", None))
#if QT_CONFIG(tooltip)
        self.action_show_settings.setToolTip(QCoreApplication.translate("MainWindow", u"Modify various settings", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(shortcut)
        self.action_show_settings.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+,", None))
#endif // QT_CONFIG(shortcut)
        self.action_edit_metadata.setText(QCoreApplication.translate("MainWindow", u"File Metadata", None))
#if QT_CONFIG(tooltip)
        self.action_edit_metadata.setToolTip(QCoreApplication.translate("MainWindow", u"View or edit metadata of the opened file", None))
#endif // QT_CONFIG(tooltip)
        self.action_close_file.setText(QCoreApplication.translate("MainWindow", u"Close File", None))
#if QT_CONFIG(tooltip)
        self.action_close_file.setToolTip(QCoreApplication.translate("MainWindow", u"Closes the currently loaded file and refreshes the app state. Make sure to export any existing results first, as they will be lost on refresh.", None))
#endif // QT_CONFIG(tooltip)
        self.action_export_result.setText(QCoreApplication.translate("MainWindow", u"Export Result", None))
#if QT_CONFIG(tooltip)
        self.action_export_result.setToolTip(QCoreApplication.translate("MainWindow", u"Open the export dialog", None))
#endif // QT_CONFIG(tooltip)
        self.action_create_new_section.setText(QCoreApplication.translate("MainWindow", u"New Section", None))
#if QT_CONFIG(tooltip)
        self.action_create_new_section.setToolTip(QCoreApplication.translate("MainWindow", u"Create a new section", None))
#endif // QT_CONFIG(tooltip)
        self.action_toggle_auto_scaling.setText(QCoreApplication.translate("MainWindow", u"Auto-Scaling", None))
#if QT_CONFIG(tooltip)
        self.action_toggle_auto_scaling.setToolTip(QCoreApplication.translate("MainWindow", u"Automatically adjust the y-axis limits to the visible data range", None))
#endif // QT_CONFIG(tooltip)
        self.action_confirm_section.setText(QCoreApplication.translate("MainWindow", u"Confirm Section", None))
#if QT_CONFIG(tooltip)
        self.action_confirm_section.setToolTip(QCoreApplication.translate("MainWindow", u"Create a new section with the data of the selected region", None))
#endif // QT_CONFIG(tooltip)
        self.action_cancel_section.setText(QCoreApplication.translate("MainWindow", u"Cancel Section", None))
#if QT_CONFIG(tooltip)
        self.action_cancel_section.setToolTip(QCoreApplication.translate("MainWindow", u"Cancel the section creation process", None))
#endif // QT_CONFIG(tooltip)
        self.action_show_section_overview.setText(QCoreApplication.translate("MainWindow", u"Section Overview", None))
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
        self.action_show_user_guide.setText(QCoreApplication.translate("MainWindow", u"User Guide", None))
#if QT_CONFIG(tooltip)
        self.action_show_user_guide.setToolTip(QCoreApplication.translate("MainWindow", u"User Guide", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(shortcut)
        self.action_show_user_guide.setShortcut(QCoreApplication.translate("MainWindow", u"F1", None))
#endif // QT_CONFIG(shortcut)
        self.action_about_qt.setText(QCoreApplication.translate("MainWindow", u"About Qt", None))
        self.action_about_app.setText(QCoreApplication.translate("MainWindow", u"About App", None))
#if QT_CONFIG(tooltip)
        self.action_about_app.setToolTip(QCoreApplication.translate("MainWindow", u"About this Application", None))
#endif // QT_CONFIG(tooltip)
        self.action_delete_section.setText(QCoreApplication.translate("MainWindow", u"Delete Section", None))
#if QT_CONFIG(tooltip)
        self.action_delete_section.setToolTip(QCoreApplication.translate("MainWindow", u"Delete the selected section", None))
#endif // QT_CONFIG(tooltip)
        self.action_clear_recent_files.setText(QCoreApplication.translate("MainWindow", u"Clear Recent Files", None))
#if QT_CONFIG(tooltip)
        self.btn_load_data.setToolTip(QCoreApplication.translate("MainWindow", u"Load data from the selected file using the settings shown above", None))
#endif // QT_CONFIG(tooltip)
        self.btn_load_data.setText(QCoreApplication.translate("MainWindow", u"Load Data", None))
        self.grp_box_required_info.setTitle(QCoreApplication.translate("MainWindow", u"Required Information ", None))
#if QT_CONFIG(tooltip)
        self.samplingRateLabel.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>The sampling rate of the signal values in the file</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.samplingRateLabel.setText(QCoreApplication.translate("MainWindow", u"Sampling Rate", None))
#if QT_CONFIG(tooltip)
        self.spin_box_sampling_rate_import_page.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>The sampling rate of the signal values in the file</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.spin_box_sampling_rate_import_page.setSuffix(QCoreApplication.translate("MainWindow", u" Hz", None))
#if QT_CONFIG(tooltip)
        self.signalColumnChannelLabel.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>The column / channel in the file containing the signal values</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.signalColumnChannelLabel.setText(QCoreApplication.translate("MainWindow", u"Data Source", None))
#if QT_CONFIG(tooltip)
        self.combo_box_signal_column_import_page.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>The column / channel in the file containing the signal values</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.combo_box_info_column_import_page.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>A column / channel in the file containing supplementary data, e.g. temperature or O2-saturation recordings</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.infoColumnChannelLabel.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>A column / channel in the file containing supplementary data, e.g. temperature or O2-saturation recordings</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.infoColumnChannelLabel.setText(QCoreApplication.translate("MainWindow", u"*Info Source", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:7pt;\">*optional data source from the file to be displayed alongside the signal data (e.g. temperature, O2-saturation, etc)</span></p></body></html>", None))
        self.tab_widget_files_properties.setTabText(self.tab_widget_files_properties.indexOf(self.tab_recent_files), QCoreApplication.translate("MainWindow", u"Recent Files", None))
        self.tab_widget_files_properties.setTabText(self.tab_widget_files_properties.indexOf(self.tab_file_metadata), QCoreApplication.translate("MainWindow", u"File Metadata", None))
        self.btn_open_file.setText(QCoreApplication.translate("MainWindow", u"Select File", None))
        self.btn_close_file.setText(QCoreApplication.translate("MainWindow", u"Close File", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Data Import", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Data View", None))
        self.label_showing_data_table.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:10pt;\">Showing</span><span style=\" font-size:10pt;\">: -</span></p></body></html>", None))
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuOpen_Recent.setTitle(QCoreApplication.translate("MainWindow", u"Open Recent", None))
        self.menuSettings.setTitle(QCoreApplication.translate("MainWindow", u"Settings", None))
        self.menuView.setTitle(QCoreApplication.translate("MainWindow", u"View", None))
        self.menuEdit.setTitle(QCoreApplication.translate("MainWindow", u"Edit", None))
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", u"Help", None))
        self.tool_bar_file_actions.setWindowTitle(QCoreApplication.translate("MainWindow", u"Editing Toolbar", None))
    # retranslateUi

