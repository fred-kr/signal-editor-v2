# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'dock_processing_inputs.ui'
##
## Created by: Qt User Interface Compiler version 6.7.0
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
from PySide6.QtWidgets import (QApplication, QDockWidget, QFormLayout, QFrame,
    QGridLayout, QGroupBox, QLabel, QPushButton,
    QSizePolicy, QSpinBox, QStackedWidget, QTabWidget,
    QTextBrowser, QVBoxLayout, QWidget)

from superqt import QEnumComboBox
from . import resources_rc

class Ui_DockWidgetProcessingInputs(object):
    def setupUi(self, DockWidgetProcessingInputs):
        if not DockWidgetProcessingInputs.objectName():
            DockWidgetProcessingInputs.setObjectName(u"DockWidgetProcessingInputs")
        DockWidgetProcessingInputs.resize(365, 493)
        self.dockWidgetContents = QWidget()
        self.dockWidgetContents.setObjectName(u"dockWidgetContents")
        self.gridLayout = QGridLayout(self.dockWidgetContents)
        self.gridLayout.setObjectName(u"gridLayout")
        self.tab_widget_processing_inputs = QTabWidget(self.dockWidgetContents)
        self.tab_widget_processing_inputs.setObjectName(u"tab_widget_processing_inputs")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tab_widget_processing_inputs.sizePolicy().hasHeightForWidth())
        self.tab_widget_processing_inputs.setSizePolicy(sizePolicy)
        self.tab_processing_pipeline = QWidget()
        self.tab_processing_pipeline.setObjectName(u"tab_processing_pipeline")
        self.gridLayout_3 = QGridLayout(self.tab_processing_pipeline)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.text_browser_pipeline_info = QTextBrowser(self.tab_processing_pipeline)
        self.text_browser_pipeline_info.setObjectName(u"text_browser_pipeline_info")

        self.gridLayout_3.addWidget(self.text_browser_pipeline_info, 7, 0, 1, 2)

        self.line = QFrame(self.tab_processing_pipeline)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_3.addWidget(self.line, 2, 0, 1, 2)

        self.label_5 = QLabel(self.tab_processing_pipeline)
        self.label_5.setObjectName(u"label_5")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy1)

        self.gridLayout_3.addWidget(self.label_5, 4, 0, 1, 1)

        self.label_3 = QLabel(self.tab_processing_pipeline)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout_3.addWidget(self.label_3, 1, 0, 1, 2)

        self.enum_combo_pipeline = QEnumComboBox(self.tab_processing_pipeline)
        self.enum_combo_pipeline.setObjectName(u"enum_combo_pipeline")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.enum_combo_pipeline.sizePolicy().hasHeightForWidth())
        self.enum_combo_pipeline.setSizePolicy(sizePolicy2)
        self.enum_combo_pipeline.setMinimumSize(QSize(0, 31))

        self.gridLayout_3.addWidget(self.enum_combo_pipeline, 4, 1, 1, 1)

        self.label_2 = QLabel(self.tab_processing_pipeline)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout_3.addWidget(self.label_2, 6, 0, 1, 1)

        self.tab_widget_processing_inputs.addTab(self.tab_processing_pipeline, "")
        self.tab_processing_filter = QWidget()
        self.tab_processing_filter.setObjectName(u"tab_processing_filter")
        self.gridLayout_4 = QGridLayout(self.tab_processing_filter)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.label_6 = QLabel(self.tab_processing_filter)
        self.label_6.setObjectName(u"label_6")
        sizePolicy1.setHeightForWidth(self.label_6.sizePolicy().hasHeightForWidth())
        self.label_6.setSizePolicy(sizePolicy1)

        self.gridLayout_4.addWidget(self.label_6, 2, 0, 1, 1)

        self.grp_box_filter_parameters = QGroupBox(self.tab_processing_filter)
        self.grp_box_filter_parameters.setObjectName(u"grp_box_filter_parameters")
        self.form_layout_grp_box_filter_parameters = QFormLayout(self.grp_box_filter_parameters)
        self.form_layout_grp_box_filter_parameters.setObjectName(u"form_layout_grp_box_filter_parameters")
        self.form_layout_grp_box_filter_parameters.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)
        self.label_9 = QLabel(self.grp_box_filter_parameters)
        self.label_9.setObjectName(u"label_9")

        self.form_layout_grp_box_filter_parameters.setWidget(0, QFormLayout.LabelRole, self.label_9)

        self.enum_combo_filter_type = QEnumComboBox(self.grp_box_filter_parameters)
        self.enum_combo_filter_type.setObjectName(u"enum_combo_filter_type")
        sizePolicy2.setHeightForWidth(self.enum_combo_filter_type.sizePolicy().hasHeightForWidth())
        self.enum_combo_filter_type.setSizePolicy(sizePolicy2)
        self.enum_combo_filter_type.setMinimumSize(QSize(0, 31))

        self.form_layout_grp_box_filter_parameters.setWidget(0, QFormLayout.FieldRole, self.enum_combo_filter_type)

        self.label_10 = QLabel(self.grp_box_filter_parameters)
        self.label_10.setObjectName(u"label_10")

        self.form_layout_grp_box_filter_parameters.setWidget(1, QFormLayout.LabelRole, self.label_10)

        self.spin_box_filter_order = QSpinBox(self.grp_box_filter_parameters)
        self.spin_box_filter_order.setObjectName(u"spin_box_filter_order")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.spin_box_filter_order.sizePolicy().hasHeightForWidth())
        self.spin_box_filter_order.setSizePolicy(sizePolicy3)
        self.spin_box_filter_order.setMinimumSize(QSize(0, 31))

        self.form_layout_grp_box_filter_parameters.setWidget(1, QFormLayout.FieldRole, self.spin_box_filter_order)


        self.gridLayout_4.addWidget(self.grp_box_filter_parameters, 3, 0, 1, 2)

        self.line_2 = QFrame(self.tab_processing_filter)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.Shape.HLine)
        self.line_2.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_4.addWidget(self.line_2, 1, 0, 1, 2)

        self.enum_combo_filter_method = QEnumComboBox(self.tab_processing_filter)
        self.enum_combo_filter_method.setObjectName(u"enum_combo_filter_method")
        self.enum_combo_filter_method.setMinimumSize(QSize(0, 31))

        self.gridLayout_4.addWidget(self.enum_combo_filter_method, 2, 1, 1, 1)

        self.label_4 = QLabel(self.tab_processing_filter)
        self.label_4.setObjectName(u"label_4")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy4)

        self.gridLayout_4.addWidget(self.label_4, 0, 0, 1, 2)

        self.tab_widget_processing_inputs.addTab(self.tab_processing_filter, "")
        self.tab_processing_standardize = QWidget()
        self.tab_processing_standardize.setObjectName(u"tab_processing_standardize")
        self.gridLayout_5 = QGridLayout(self.tab_processing_standardize)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.line_3 = QFrame(self.tab_processing_standardize)
        self.line_3.setObjectName(u"line_3")
        self.line_3.setFrameShape(QFrame.Shape.HLine)
        self.line_3.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_5.addWidget(self.line_3, 1, 0, 1, 2)

        self.text_browser_standardize_info = QTextBrowser(self.tab_processing_standardize)
        self.text_browser_standardize_info.setObjectName(u"text_browser_standardize_info")

        self.gridLayout_5.addWidget(self.text_browser_standardize_info, 4, 0, 1, 2)

        self.label_7 = QLabel(self.tab_processing_standardize)
        self.label_7.setObjectName(u"label_7")

        self.gridLayout_5.addWidget(self.label_7, 0, 0, 1, 2)

        self.label_8 = QLabel(self.tab_processing_standardize)
        self.label_8.setObjectName(u"label_8")
        sizePolicy1.setHeightForWidth(self.label_8.sizePolicy().hasHeightForWidth())
        self.label_8.setSizePolicy(sizePolicy1)

        self.gridLayout_5.addWidget(self.label_8, 2, 0, 1, 1)

        self.grp_box_standardize_rolling_window = QGroupBox(self.tab_processing_standardize)
        self.grp_box_standardize_rolling_window.setObjectName(u"grp_box_standardize_rolling_window")
        sizePolicy5 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.grp_box_standardize_rolling_window.sizePolicy().hasHeightForWidth())
        self.grp_box_standardize_rolling_window.setSizePolicy(sizePolicy5)
        self.grp_box_standardize_rolling_window.setFlat(True)
        self.grp_box_standardize_rolling_window.setCheckable(True)
        self.grp_box_standardize_rolling_window.setChecked(False)
        self.form_layout_standardize_roll_window = QFormLayout(self.grp_box_standardize_rolling_window)
        self.form_layout_standardize_roll_window.setObjectName(u"form_layout_standardize_roll_window")
        self.label_11 = QLabel(self.grp_box_standardize_rolling_window)
        self.label_11.setObjectName(u"label_11")

        self.form_layout_standardize_roll_window.setWidget(0, QFormLayout.LabelRole, self.label_11)


        self.gridLayout_5.addWidget(self.grp_box_standardize_rolling_window, 3, 0, 1, 2)

        self.enum_combo_standardize_method = QEnumComboBox(self.tab_processing_standardize)
        self.enum_combo_standardize_method.setObjectName(u"enum_combo_standardize_method")
        self.enum_combo_standardize_method.setMinimumSize(QSize(0, 31))

        self.gridLayout_5.addWidget(self.enum_combo_standardize_method, 2, 1, 1, 1)

        self.tab_widget_processing_inputs.addTab(self.tab_processing_standardize, "")

        self.gridLayout.addWidget(self.tab_widget_processing_inputs, 2, 0, 1, 4)

        self.btn_reset_data = QPushButton(self.dockWidgetContents)
        self.btn_reset_data.setObjectName(u"btn_reset_data")
        sizePolicy6 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy6.setHorizontalStretch(0)
        sizePolicy6.setVerticalStretch(0)
        sizePolicy6.setHeightForWidth(self.btn_reset_data.sizePolicy().hasHeightForWidth())
        self.btn_reset_data.setSizePolicy(sizePolicy6)
        self.btn_reset_data.setMinimumSize(QSize(0, 31))
        icon = QIcon()
        icon.addFile(u":/icons/reset_all", QSize(), QIcon.Normal, QIcon.Off)
        self.btn_reset_data.setIcon(icon)
        self.btn_reset_data.setFlat(True)

        self.gridLayout.addWidget(self.btn_reset_data, 0, 3, 1, 1)

        self.btn_reset_processing_inputs = QPushButton(self.dockWidgetContents)
        self.btn_reset_processing_inputs.setObjectName(u"btn_reset_processing_inputs")
        sizePolicy6.setHeightForWidth(self.btn_reset_processing_inputs.sizePolicy().hasHeightForWidth())
        self.btn_reset_processing_inputs.setSizePolicy(sizePolicy6)
        self.btn_reset_processing_inputs.setMinimumSize(QSize(0, 31))
        icon1 = QIcon()
        icon1.addFile(u":/icons/restore_defaults", QSize(), QIcon.Normal, QIcon.Off)
        self.btn_reset_processing_inputs.setIcon(icon1)
        self.btn_reset_processing_inputs.setFlat(True)

        self.gridLayout.addWidget(self.btn_reset_processing_inputs, 0, 2, 1, 1)

        self.label = QLabel(self.dockWidgetContents)
        self.label.setObjectName(u"label")
        sizePolicy6.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy6)
        self.label.setMinimumSize(QSize(0, 31))

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.stacked_apply_btns = QStackedWidget(self.dockWidgetContents)
        self.stacked_apply_btns.setObjectName(u"stacked_apply_btns")
        sizePolicy4.setHeightForWidth(self.stacked_apply_btns.sizePolicy().hasHeightForWidth())
        self.stacked_apply_btns.setSizePolicy(sizePolicy4)
        self.page_pipeline = QWidget()
        self.page_pipeline.setObjectName(u"page_pipeline")
        self.verticalLayout_2 = QVBoxLayout(self.page_pipeline)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(-1, 0, -1, 0)
        self.btn_run_pipeline = QPushButton(self.page_pipeline)
        self.btn_run_pipeline.setObjectName(u"btn_run_pipeline")
        self.btn_run_pipeline.setMinimumSize(QSize(0, 31))

        self.verticalLayout_2.addWidget(self.btn_run_pipeline)

        self.stacked_apply_btns.addWidget(self.page_pipeline)
        self.page_filter = QWidget()
        self.page_filter.setObjectName(u"page_filter")
        self.verticalLayout_3 = QVBoxLayout(self.page_filter)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(-1, 0, -1, 0)
        self.btn_apply_signal_filter = QPushButton(self.page_filter)
        self.btn_apply_signal_filter.setObjectName(u"btn_apply_signal_filter")
        self.btn_apply_signal_filter.setMinimumSize(QSize(0, 31))

        self.verticalLayout_3.addWidget(self.btn_apply_signal_filter)

        self.stacked_apply_btns.addWidget(self.page_filter)
        self.page_standardize = QWidget()
        self.page_standardize.setObjectName(u"page_standardize")
        self.verticalLayout_4 = QVBoxLayout(self.page_standardize)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(-1, 0, -1, 0)
        self.btn_apply_standardization = QPushButton(self.page_standardize)
        self.btn_apply_standardization.setObjectName(u"btn_apply_standardization")
        self.btn_apply_standardization.setMinimumSize(QSize(0, 31))

        self.verticalLayout_4.addWidget(self.btn_apply_standardization)

        self.stacked_apply_btns.addWidget(self.page_standardize)

        self.gridLayout.addWidget(self.stacked_apply_btns, 1, 0, 1, 4)

        DockWidgetProcessingInputs.setWidget(self.dockWidgetContents)

        self.retranslateUi(DockWidgetProcessingInputs)
        self.tab_widget_processing_inputs.currentChanged.connect(self.stacked_apply_btns.setCurrentIndex)

        self.tab_widget_processing_inputs.setCurrentIndex(0)
        self.stacked_apply_btns.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(DockWidgetProcessingInputs)
    # setupUi

    def retranslateUi(self, DockWidgetProcessingInputs):
        DockWidgetProcessingInputs.setWindowTitle(QCoreApplication.translate("DockWidgetProcessingInputs", u"Signal Pre-Processing", None))
        self.label_5.setText(QCoreApplication.translate("DockWidgetProcessingInputs", u"Name:", None))
        self.label_3.setText(QCoreApplication.translate("DockWidgetProcessingInputs", u"<html><head/><body><p><span style=\" font-size:10pt;\">Process your signal using one of the available pipelines</span></p></body></html>", None))
        self.label_2.setText(QCoreApplication.translate("DockWidgetProcessingInputs", u"<html><head/><body><p><span style=\" font-size:10pt; font-weight:700;\">Description</span></p></body></html>", None))
        self.tab_widget_processing_inputs.setTabText(self.tab_widget_processing_inputs.indexOf(self.tab_processing_pipeline), QCoreApplication.translate("DockWidgetProcessingInputs", u"Pipeline", None))
        self.label_6.setText(QCoreApplication.translate("DockWidgetProcessingInputs", u"Filter Method:", None))
        self.grp_box_filter_parameters.setTitle(QCoreApplication.translate("DockWidgetProcessingInputs", u"Method Parameters", None))
        self.label_9.setText(QCoreApplication.translate("DockWidgetProcessingInputs", u"Filter Type:", None))
        self.label_10.setText(QCoreApplication.translate("DockWidgetProcessingInputs", u"Filter Order", None))
        self.label_4.setText(QCoreApplication.translate("DockWidgetProcessingInputs", u"<html><head/><body><p><span style=\" font-size:10pt;\">Filter your signal using one of the listed methods</span></p></body></html>", None))
        self.tab_widget_processing_inputs.setTabText(self.tab_widget_processing_inputs.indexOf(self.tab_processing_filter), QCoreApplication.translate("DockWidgetProcessingInputs", u"Custom Filters", None))
        self.text_browser_standardize_info.setHtml(QCoreApplication.translate("DockWidgetProcessingInputs", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Performs a standardization of data (Z-scoring), i.e., centering and scaling, so that the data is expressed in terms of standard deviation (i.e., mean = 0, SD = 1) or Median Absolute Deviance (median = 0, MAD = 1). The latter is more robust to outliers.</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">The rolling version of"
                        " this standardization is available only for the standard deviation approach, since calculating rolling median's for signals with over 100k samples will take way too long.</p></body></html>", None))
        self.label_7.setText(QCoreApplication.translate("DockWidgetProcessingInputs", u"<html><head/><body><p><span style=\" font-size:10pt;\">Standardize the current signal values via Z-Scoring</span></p></body></html>", None))
        self.label_8.setText(QCoreApplication.translate("DockWidgetProcessingInputs", u"Standardize using:", None))
        self.grp_box_standardize_rolling_window.setTitle(QCoreApplication.translate("DockWidgetProcessingInputs", u"Rolling Standardization ", None))
        self.label_11.setText(QCoreApplication.translate("DockWidgetProcessingInputs", u"Window Size:", None))
        self.tab_widget_processing_inputs.setTabText(self.tab_widget_processing_inputs.indexOf(self.tab_processing_standardize), QCoreApplication.translate("DockWidgetProcessingInputs", u"Standardization", None))
#if QT_CONFIG(tooltip)
        self.btn_reset_data.setToolTip(QCoreApplication.translate("DockWidgetProcessingInputs", u"Discard currently applied processing and restore original signal values (for the current section)", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.btn_reset_processing_inputs.setToolTip(QCoreApplication.translate("DockWidgetProcessingInputs", u"Restore all input fields to their default values", None))
#endif // QT_CONFIG(tooltip)
        self.label.setText(QCoreApplication.translate("DockWidgetProcessingInputs", u"<html><head/><body><p><span style=\" font-size:12pt; font-weight:700;\">Pre-Processing Parameters</span></p></body></html>", None))
        self.btn_run_pipeline.setText(QCoreApplication.translate("DockWidgetProcessingInputs", u"Run Pipeline", None))
        self.btn_apply_signal_filter.setText(QCoreApplication.translate("DockWidgetProcessingInputs", u"Apply Filter", None))
        self.btn_apply_standardization.setText(QCoreApplication.translate("DockWidgetProcessingInputs", u"Apply Standardization", None))
    # retranslateUi

