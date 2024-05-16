# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'dock_peak_detection.ui'
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
from PySide6.QtWidgets import (QAbstractScrollArea, QAbstractSpinBox, QApplication, QCheckBox,
    QDockWidget, QDoubleSpinBox, QFormLayout, QFrame,
    QGridLayout, QLabel, QPushButton, QScrollArea,
    QSizePolicy, QSpinBox, QStackedWidget, QTextBrowser,
    QVBoxLayout, QWidget)

from superqt import (QCollapsible, QEnumComboBox)
from . import resources_rc

class Ui_DockWidgetPeakDetection(object):
    def setupUi(self, DockWidgetPeakDetection):
        if not DockWidgetPeakDetection.objectName():
            DockWidgetPeakDetection.setObjectName(u"DockWidgetPeakDetection")
        DockWidgetPeakDetection.resize(373, 580)
        DockWidgetPeakDetection.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea|Qt.DockWidgetArea.RightDockWidgetArea)
        self.dockWidgetContents = QWidget()
        self.dockWidgetContents.setObjectName(u"dockWidgetContents")
        self.gridLayout = QGridLayout(self.dockWidgetContents)
        self.gridLayout.setObjectName(u"gridLayout")
        self.scrollArea = QScrollArea(self.dockWidgetContents)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 353, 435))
        self.verticalLayout = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.stacked_peak_parameters = QStackedWidget(self.scrollAreaWidgetContents)
        self.stacked_peak_parameters.setObjectName(u"stacked_peak_parameters")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.stacked_peak_parameters.sizePolicy().hasHeightForWidth())
        self.stacked_peak_parameters.setSizePolicy(sizePolicy)
        self.stacked_peak_parameters.setFrameShape(QFrame.Shape.NoFrame)
        self.page_peak_elgendi_ppg = QWidget()
        self.page_peak_elgendi_ppg.setObjectName(u"page_peak_elgendi_ppg")
        self.formLayout_2 = QFormLayout(self.page_peak_elgendi_ppg)
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.peak_elgendi_ppg_info = QTextBrowser(self.page_peak_elgendi_ppg)
        self.peak_elgendi_ppg_info.setObjectName(u"peak_elgendi_ppg_info")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.peak_elgendi_ppg_info.sizePolicy().hasHeightForWidth())
        self.peak_elgendi_ppg_info.setSizePolicy(sizePolicy1)
        self.peak_elgendi_ppg_info.setMaximumSize(QSize(16777215, 100))
        self.peak_elgendi_ppg_info.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)

        self.formLayout_2.setWidget(0, QFormLayout.SpanningRole, self.peak_elgendi_ppg_info)

        self.label_peak_window = QLabel(self.page_peak_elgendi_ppg)
        self.label_peak_window.setObjectName(u"label_peak_window")
        self.label_peak_window.setMinimumSize(QSize(0, 31))
        font = QFont()
        font.setBold(True)
        font.setItalic(False)
        self.label_peak_window.setFont(font)

        self.formLayout_2.setWidget(1, QFormLayout.LabelRole, self.label_peak_window)

        self.peak_elgendi_ppg_peakwindow = QDoubleSpinBox(self.page_peak_elgendi_ppg)
        self.peak_elgendi_ppg_peakwindow.setObjectName(u"peak_elgendi_ppg_peakwindow")
        self.peak_elgendi_ppg_peakwindow.setMinimumSize(QSize(0, 31))
        self.peak_elgendi_ppg_peakwindow.setDecimals(3)
        self.peak_elgendi_ppg_peakwindow.setMinimum(0.050000000000000)
        self.peak_elgendi_ppg_peakwindow.setMaximum(5.000000000000000)
        self.peak_elgendi_ppg_peakwindow.setSingleStep(0.001000000000000)
        self.peak_elgendi_ppg_peakwindow.setValue(0.111000000000000)

        self.formLayout_2.setWidget(1, QFormLayout.FieldRole, self.peak_elgendi_ppg_peakwindow)

        self.beatWindowLabel = QLabel(self.page_peak_elgendi_ppg)
        self.beatWindowLabel.setObjectName(u"beatWindowLabel")
        self.beatWindowLabel.setMinimumSize(QSize(0, 31))
        self.beatWindowLabel.setFont(font)

        self.formLayout_2.setWidget(2, QFormLayout.LabelRole, self.beatWindowLabel)

        self.peak_elgendi_ppg_beatwindow = QDoubleSpinBox(self.page_peak_elgendi_ppg)
        self.peak_elgendi_ppg_beatwindow.setObjectName(u"peak_elgendi_ppg_beatwindow")
        self.peak_elgendi_ppg_beatwindow.setMinimumSize(QSize(0, 31))
        self.peak_elgendi_ppg_beatwindow.setDecimals(3)
        self.peak_elgendi_ppg_beatwindow.setMinimum(0.100000000000000)
        self.peak_elgendi_ppg_beatwindow.setMaximum(5.000000000000000)
        self.peak_elgendi_ppg_beatwindow.setSingleStep(0.001000000000000)
        self.peak_elgendi_ppg_beatwindow.setStepType(QAbstractSpinBox.StepType.DefaultStepType)
        self.peak_elgendi_ppg_beatwindow.setValue(0.667000000000000)

        self.formLayout_2.setWidget(2, QFormLayout.FieldRole, self.peak_elgendi_ppg_beatwindow)

        self.beatOffsetLabel = QLabel(self.page_peak_elgendi_ppg)
        self.beatOffsetLabel.setObjectName(u"beatOffsetLabel")
        self.beatOffsetLabel.setMinimumSize(QSize(0, 31))
        self.beatOffsetLabel.setFont(font)

        self.formLayout_2.setWidget(3, QFormLayout.LabelRole, self.beatOffsetLabel)

        self.peak_elgendi_ppg_beatoffset = QDoubleSpinBox(self.page_peak_elgendi_ppg)
        self.peak_elgendi_ppg_beatoffset.setObjectName(u"peak_elgendi_ppg_beatoffset")
        self.peak_elgendi_ppg_beatoffset.setMinimumSize(QSize(0, 31))
        self.peak_elgendi_ppg_beatoffset.setDecimals(2)
        self.peak_elgendi_ppg_beatoffset.setMaximum(1.000000000000000)
        self.peak_elgendi_ppg_beatoffset.setSingleStep(0.010000000000000)
        self.peak_elgendi_ppg_beatoffset.setStepType(QAbstractSpinBox.StepType.DefaultStepType)
        self.peak_elgendi_ppg_beatoffset.setValue(0.020000000000000)

        self.formLayout_2.setWidget(3, QFormLayout.FieldRole, self.peak_elgendi_ppg_beatoffset)

        self.minimumDelayLabel = QLabel(self.page_peak_elgendi_ppg)
        self.minimumDelayLabel.setObjectName(u"minimumDelayLabel")
        self.minimumDelayLabel.setMinimumSize(QSize(0, 31))
        self.minimumDelayLabel.setFont(font)

        self.formLayout_2.setWidget(4, QFormLayout.LabelRole, self.minimumDelayLabel)

        self.peak_elgendi_ppg_mindelay = QDoubleSpinBox(self.page_peak_elgendi_ppg)
        self.peak_elgendi_ppg_mindelay.setObjectName(u"peak_elgendi_ppg_mindelay")
        self.peak_elgendi_ppg_mindelay.setMinimumSize(QSize(0, 31))
        self.peak_elgendi_ppg_mindelay.setDecimals(2)
        self.peak_elgendi_ppg_mindelay.setMaximum(10.000000000000000)
        self.peak_elgendi_ppg_mindelay.setSingleStep(0.010000000000000)
        self.peak_elgendi_ppg_mindelay.setStepType(QAbstractSpinBox.StepType.DefaultStepType)
        self.peak_elgendi_ppg_mindelay.setValue(0.300000000000000)

        self.formLayout_2.setWidget(4, QFormLayout.FieldRole, self.peak_elgendi_ppg_mindelay)

        self.stacked_peak_parameters.addWidget(self.page_peak_elgendi_ppg)
        self.page_peak_local_max = QWidget()
        self.page_peak_local_max.setObjectName(u"page_peak_local_max")
        self.formLayout_5 = QFormLayout(self.page_peak_local_max)
        self.formLayout_5.setObjectName(u"formLayout_5")
        self.label_22 = QLabel(self.page_peak_local_max)
        self.label_22.setObjectName(u"label_22")
        self.label_22.setMinimumSize(QSize(0, 31))
        font1 = QFont()
        font1.setBold(True)
        self.label_22.setFont(font1)

        self.formLayout_5.setWidget(1, QFormLayout.LabelRole, self.label_22)

        self.peak_local_max_radius = QSpinBox(self.page_peak_local_max)
        self.peak_local_max_radius.setObjectName(u"peak_local_max_radius")
        self.peak_local_max_radius.setMinimumSize(QSize(0, 31))
        self.peak_local_max_radius.setAccelerated(True)
        self.peak_local_max_radius.setMinimum(5)
        self.peak_local_max_radius.setMaximum(9999)
        self.peak_local_max_radius.setStepType(QAbstractSpinBox.StepType.AdaptiveDecimalStepType)
        self.peak_local_max_radius.setValue(111)

        self.formLayout_5.setWidget(1, QFormLayout.FieldRole, self.peak_local_max_radius)

        self.peak_local_max_info = QTextBrowser(self.page_peak_local_max)
        self.peak_local_max_info.setObjectName(u"peak_local_max_info")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.peak_local_max_info.sizePolicy().hasHeightForWidth())
        self.peak_local_max_info.setSizePolicy(sizePolicy2)
        self.peak_local_max_info.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.peak_local_max_info.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)

        self.formLayout_5.setWidget(0, QFormLayout.SpanningRole, self.peak_local_max_info)

        self.minDistanceLabel = QLabel(self.page_peak_local_max)
        self.minDistanceLabel.setObjectName(u"minDistanceLabel")
        self.minDistanceLabel.setMinimumSize(QSize(0, 31))
        self.minDistanceLabel.setFont(font1)

        self.formLayout_5.setWidget(2, QFormLayout.LabelRole, self.minDistanceLabel)

        self.peak_local_max_min_dist = QSpinBox(self.page_peak_local_max)
        self.peak_local_max_min_dist.setObjectName(u"peak_local_max_min_dist")
        self.peak_local_max_min_dist.setMinimumSize(QSize(0, 31))
        self.peak_local_max_min_dist.setMinimum(0)
        self.peak_local_max_min_dist.setMaximum(1000000)
        self.peak_local_max_min_dist.setValue(15)

        self.formLayout_5.setWidget(2, QFormLayout.FieldRole, self.peak_local_max_min_dist)

        self.stacked_peak_parameters.addWidget(self.page_peak_local_max)
        self.page_peak_local_min = QWidget()
        self.page_peak_local_min.setObjectName(u"page_peak_local_min")
        self.formLayout = QFormLayout(self.page_peak_local_min)
        self.formLayout.setObjectName(u"formLayout")
        self.peak_local_min_info = QTextBrowser(self.page_peak_local_min)
        self.peak_local_min_info.setObjectName(u"peak_local_min_info")
        sizePolicy2.setHeightForWidth(self.peak_local_min_info.sizePolicy().hasHeightForWidth())
        self.peak_local_min_info.setSizePolicy(sizePolicy2)
        self.peak_local_min_info.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.peak_local_min_info.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)

        self.formLayout.setWidget(0, QFormLayout.SpanningRole, self.peak_local_min_info)

        self.label_23 = QLabel(self.page_peak_local_min)
        self.label_23.setObjectName(u"label_23")
        self.label_23.setMinimumSize(QSize(0, 31))
        self.label_23.setFont(font1)

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label_23)

        self.peak_local_min_radius = QSpinBox(self.page_peak_local_min)
        self.peak_local_min_radius.setObjectName(u"peak_local_min_radius")
        self.peak_local_min_radius.setMinimumSize(QSize(0, 31))
        self.peak_local_min_radius.setAccelerated(True)
        self.peak_local_min_radius.setMinimum(5)
        self.peak_local_min_radius.setMaximum(9999)
        self.peak_local_min_radius.setStepType(QAbstractSpinBox.StepType.AdaptiveDecimalStepType)
        self.peak_local_min_radius.setValue(111)

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.peak_local_min_radius)

        self.minDistanceLabel_2 = QLabel(self.page_peak_local_min)
        self.minDistanceLabel_2.setObjectName(u"minDistanceLabel_2")
        self.minDistanceLabel_2.setMinimumSize(QSize(0, 31))
        self.minDistanceLabel_2.setFont(font1)

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.minDistanceLabel_2)

        self.peak_local_min_min_dist = QSpinBox(self.page_peak_local_min)
        self.peak_local_min_min_dist.setObjectName(u"peak_local_min_min_dist")
        self.peak_local_min_min_dist.setMinimumSize(QSize(0, 31))
        self.peak_local_min_min_dist.setMaximum(1000000)
        self.peak_local_min_min_dist.setValue(15)

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.peak_local_min_min_dist)

        self.stacked_peak_parameters.addWidget(self.page_peak_local_min)
        self.page_peak_neurokit2 = QWidget()
        self.page_peak_neurokit2.setObjectName(u"page_peak_neurokit2")
        self.formLayout_6 = QFormLayout(self.page_peak_neurokit2)
        self.formLayout_6.setObjectName(u"formLayout_6")
        self.formLayout_6.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)
        self.peak_neurokit2_info = QTextBrowser(self.page_peak_neurokit2)
        self.peak_neurokit2_info.setObjectName(u"peak_neurokit2_info")
        sizePolicy2.setHeightForWidth(self.peak_neurokit2_info.sizePolicy().hasHeightForWidth())
        self.peak_neurokit2_info.setSizePolicy(sizePolicy2)
        self.peak_neurokit2_info.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)

        self.formLayout_6.setWidget(0, QFormLayout.SpanningRole, self.peak_neurokit2_info)

        self.algorithmLabel = QLabel(self.page_peak_neurokit2)
        self.algorithmLabel.setObjectName(u"algorithmLabel")
        self.algorithmLabel.setEnabled(False)
        self.algorithmLabel.setMinimumSize(QSize(0, 31))
        self.algorithmLabel.setFont(font1)

        self.formLayout_6.setWidget(1, QFormLayout.LabelRole, self.algorithmLabel)

        self.peak_neurokit2_algorithm_used = QEnumComboBox(self.page_peak_neurokit2)
        self.peak_neurokit2_algorithm_used.setObjectName(u"peak_neurokit2_algorithm_used")
        self.peak_neurokit2_algorithm_used.setMinimumSize(QSize(0, 31))

        self.formLayout_6.setWidget(1, QFormLayout.FieldRole, self.peak_neurokit2_algorithm_used)

        self.collapsible_nk2_peak_inputs = QCollapsible(self.page_peak_neurokit2)
        self.collapsible_nk2_peak_inputs.setObjectName(u"collapsible_nk2_peak_inputs")
        self.collapsible_nk2_peak_inputs.setFrameShape(QFrame.Shape.StyledPanel)
        self.collapsible_nk2_peak_inputs.setFrameShadow(QFrame.Shadow.Raised)
        self.stacked_nk2_method_parameters = QStackedWidget(self.collapsible_nk2_peak_inputs)
        self.stacked_nk2_method_parameters.setObjectName(u"stacked_nk2_method_parameters")
        self.stacked_nk2_method_parameters.setGeometry(QRect(10, 10, 301, 311))
        self.nk2_page_neurokit = QWidget()
        self.nk2_page_neurokit.setObjectName(u"nk2_page_neurokit")
        self.formLayout_4 = QFormLayout(self.nk2_page_neurokit)
        self.formLayout_4.setObjectName(u"formLayout_4")
        self.smoothingWindowLabel = QLabel(self.nk2_page_neurokit)
        self.smoothingWindowLabel.setObjectName(u"smoothingWindowLabel")
        self.smoothingWindowLabel.setMinimumSize(QSize(0, 31))
        self.smoothingWindowLabel.setFont(font1)

        self.formLayout_4.setWidget(0, QFormLayout.LabelRole, self.smoothingWindowLabel)

        self.peak_neurokit2_smoothwindow = QDoubleSpinBox(self.nk2_page_neurokit)
        self.peak_neurokit2_smoothwindow.setObjectName(u"peak_neurokit2_smoothwindow")
        self.peak_neurokit2_smoothwindow.setMinimumSize(QSize(0, 31))
        self.peak_neurokit2_smoothwindow.setMinimum(0.010000000000000)
        self.peak_neurokit2_smoothwindow.setMaximum(10.000000000000000)
        self.peak_neurokit2_smoothwindow.setSingleStep(0.010000000000000)

        self.formLayout_4.setWidget(0, QFormLayout.FieldRole, self.peak_neurokit2_smoothwindow)

        self.label_27 = QLabel(self.nk2_page_neurokit)
        self.label_27.setObjectName(u"label_27")
        self.label_27.setMinimumSize(QSize(0, 31))
        self.label_27.setFont(font1)

        self.formLayout_4.setWidget(1, QFormLayout.LabelRole, self.label_27)

        self.peak_neurokit2_avgwindow = QDoubleSpinBox(self.nk2_page_neurokit)
        self.peak_neurokit2_avgwindow.setObjectName(u"peak_neurokit2_avgwindow")
        self.peak_neurokit2_avgwindow.setMinimumSize(QSize(0, 31))
        self.peak_neurokit2_avgwindow.setDecimals(2)
        self.peak_neurokit2_avgwindow.setMinimum(0.010000000000000)
        self.peak_neurokit2_avgwindow.setMaximum(10.000000000000000)
        self.peak_neurokit2_avgwindow.setSingleStep(0.010000000000000)
        self.peak_neurokit2_avgwindow.setValue(0.750000000000000)

        self.formLayout_4.setWidget(1, QFormLayout.FieldRole, self.peak_neurokit2_avgwindow)

        self.label_28 = QLabel(self.nk2_page_neurokit)
        self.label_28.setObjectName(u"label_28")
        self.label_28.setMinimumSize(QSize(0, 31))
        self.label_28.setFont(font1)

        self.formLayout_4.setWidget(2, QFormLayout.LabelRole, self.label_28)

        self.peak_neurokit2_gradthreshweight = QDoubleSpinBox(self.nk2_page_neurokit)
        self.peak_neurokit2_gradthreshweight.setObjectName(u"peak_neurokit2_gradthreshweight")
        self.peak_neurokit2_gradthreshweight.setMinimumSize(QSize(0, 31))
        self.peak_neurokit2_gradthreshweight.setDecimals(1)
        self.peak_neurokit2_gradthreshweight.setMinimum(0.100000000000000)
        self.peak_neurokit2_gradthreshweight.setMaximum(10.000000000000000)
        self.peak_neurokit2_gradthreshweight.setSingleStep(0.100000000000000)
        self.peak_neurokit2_gradthreshweight.setValue(1.500000000000000)

        self.formLayout_4.setWidget(2, QFormLayout.FieldRole, self.peak_neurokit2_gradthreshweight)

        self.label_29 = QLabel(self.nk2_page_neurokit)
        self.label_29.setObjectName(u"label_29")
        self.label_29.setMinimumSize(QSize(0, 31))
        self.label_29.setFont(font1)

        self.formLayout_4.setWidget(3, QFormLayout.LabelRole, self.label_29)

        self.peak_neurokit2_minlenweight = QDoubleSpinBox(self.nk2_page_neurokit)
        self.peak_neurokit2_minlenweight.setObjectName(u"peak_neurokit2_minlenweight")
        self.peak_neurokit2_minlenweight.setMinimumSize(QSize(0, 31))
        self.peak_neurokit2_minlenweight.setDecimals(1)
        self.peak_neurokit2_minlenweight.setMinimum(0.100000000000000)
        self.peak_neurokit2_minlenweight.setMaximum(10.000000000000000)
        self.peak_neurokit2_minlenweight.setSingleStep(0.100000000000000)
        self.peak_neurokit2_minlenweight.setValue(0.400000000000000)

        self.formLayout_4.setWidget(3, QFormLayout.FieldRole, self.peak_neurokit2_minlenweight)

        self.label_30 = QLabel(self.nk2_page_neurokit)
        self.label_30.setObjectName(u"label_30")
        self.label_30.setMinimumSize(QSize(0, 31))
        self.label_30.setFont(font1)

        self.formLayout_4.setWidget(4, QFormLayout.LabelRole, self.label_30)

        self.peak_neurokit2_mindelay = QDoubleSpinBox(self.nk2_page_neurokit)
        self.peak_neurokit2_mindelay.setObjectName(u"peak_neurokit2_mindelay")
        self.peak_neurokit2_mindelay.setMinimumSize(QSize(0, 31))
        self.peak_neurokit2_mindelay.setMinimum(0.010000000000000)
        self.peak_neurokit2_mindelay.setMaximum(10.000000000000000)
        self.peak_neurokit2_mindelay.setSingleStep(0.010000000000000)
        self.peak_neurokit2_mindelay.setValue(0.300000000000000)

        self.formLayout_4.setWidget(4, QFormLayout.FieldRole, self.peak_neurokit2_mindelay)

        self.label_31 = QLabel(self.nk2_page_neurokit)
        self.label_31.setObjectName(u"label_31")
        self.label_31.setMinimumSize(QSize(0, 31))
        self.label_31.setFont(font1)

        self.formLayout_4.setWidget(5, QFormLayout.LabelRole, self.label_31)

        self.text_browser_peak_neurokit2 = QTextBrowser(self.nk2_page_neurokit)
        self.text_browser_peak_neurokit2.setObjectName(u"text_browser_peak_neurokit2")
        self.text_browser_peak_neurokit2.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)

        self.formLayout_4.setWidget(6, QFormLayout.SpanningRole, self.text_browser_peak_neurokit2)

        self.stacked_nk2_method_parameters.addWidget(self.nk2_page_neurokit)
        self.nk2_page_ssf = QWidget()
        self.nk2_page_ssf.setObjectName(u"nk2_page_ssf")
        self.formLayout_10 = QFormLayout(self.nk2_page_ssf)
        self.formLayout_10.setObjectName(u"formLayout_10")
        self.label_3 = QLabel(self.nk2_page_ssf)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setMinimumSize(QSize(0, 31))

        self.formLayout_10.setWidget(0, QFormLayout.LabelRole, self.label_3)

        self.beforeLabel = QLabel(self.nk2_page_ssf)
        self.beforeLabel.setObjectName(u"beforeLabel")
        self.beforeLabel.setMinimumSize(QSize(0, 31))

        self.formLayout_10.setWidget(1, QFormLayout.LabelRole, self.beforeLabel)

        self.peak_ssf_before = QDoubleSpinBox(self.nk2_page_ssf)
        self.peak_ssf_before.setObjectName(u"peak_ssf_before")
        self.peak_ssf_before.setMinimumSize(QSize(0, 31))
        self.peak_ssf_before.setMinimum(0.010000000000000)
        self.peak_ssf_before.setMaximum(0.100000000000000)
        self.peak_ssf_before.setSingleStep(0.010000000000000)
        self.peak_ssf_before.setValue(0.030000000000000)

        self.formLayout_10.setWidget(1, QFormLayout.FieldRole, self.peak_ssf_before)

        self.afterLabel = QLabel(self.nk2_page_ssf)
        self.afterLabel.setObjectName(u"afterLabel")
        self.afterLabel.setMinimumSize(QSize(0, 31))

        self.formLayout_10.setWidget(2, QFormLayout.LabelRole, self.afterLabel)

        self.peak_ssf_after = QDoubleSpinBox(self.nk2_page_ssf)
        self.peak_ssf_after.setObjectName(u"peak_ssf_after")
        self.peak_ssf_after.setMinimumSize(QSize(0, 31))
        self.peak_ssf_after.setDecimals(3)
        self.peak_ssf_after.setMinimum(0.005000000000000)
        self.peak_ssf_after.setMaximum(0.050000000000000)
        self.peak_ssf_after.setSingleStep(0.001000000000000)
        self.peak_ssf_after.setValue(0.010000000000000)

        self.formLayout_10.setWidget(2, QFormLayout.FieldRole, self.peak_ssf_after)

        self.peak_ssf_threshold = QSpinBox(self.nk2_page_ssf)
        self.peak_ssf_threshold.setObjectName(u"peak_ssf_threshold")
        self.peak_ssf_threshold.setMinimumSize(QSize(0, 31))
        self.peak_ssf_threshold.setMinimum(1)
        self.peak_ssf_threshold.setMaximum(150)
        self.peak_ssf_threshold.setValue(20)

        self.formLayout_10.setWidget(0, QFormLayout.FieldRole, self.peak_ssf_threshold)

        self.text_browser_peak_ssf = QTextBrowser(self.nk2_page_ssf)
        self.text_browser_peak_ssf.setObjectName(u"text_browser_peak_ssf")
        self.text_browser_peak_ssf.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)

        self.formLayout_10.setWidget(3, QFormLayout.SpanningRole, self.text_browser_peak_ssf)

        self.stacked_nk2_method_parameters.addWidget(self.nk2_page_ssf)
        self.nk2_page_gamboa = QWidget()
        self.nk2_page_gamboa.setObjectName(u"nk2_page_gamboa")
        self.formLayout_11 = QFormLayout(self.nk2_page_gamboa)
        self.formLayout_11.setObjectName(u"formLayout_11")
        self.windowLabel = QLabel(self.nk2_page_gamboa)
        self.windowLabel.setObjectName(u"windowLabel")
        self.windowLabel.setMinimumSize(QSize(0, 31))

        self.formLayout_11.setWidget(0, QFormLayout.LabelRole, self.windowLabel)

        self.peak_gamboa_tol = QDoubleSpinBox(self.nk2_page_gamboa)
        self.peak_gamboa_tol.setObjectName(u"peak_gamboa_tol")
        self.peak_gamboa_tol.setMinimumSize(QSize(0, 31))
        self.peak_gamboa_tol.setDecimals(3)
        self.peak_gamboa_tol.setMinimum(0.001000000000000)
        self.peak_gamboa_tol.setMaximum(0.010000000000000)
        self.peak_gamboa_tol.setSingleStep(0.001000000000000)
        self.peak_gamboa_tol.setValue(0.002000000000000)

        self.formLayout_11.setWidget(0, QFormLayout.FieldRole, self.peak_gamboa_tol)

        self.text_browser_peak_gamboa = QTextBrowser(self.nk2_page_gamboa)
        self.text_browser_peak_gamboa.setObjectName(u"text_browser_peak_gamboa")
        self.text_browser_peak_gamboa.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)

        self.formLayout_11.setWidget(1, QFormLayout.SpanningRole, self.text_browser_peak_gamboa)

        self.stacked_nk2_method_parameters.addWidget(self.nk2_page_gamboa)
        self.nk2_page_emrich = QWidget()
        self.nk2_page_emrich.setObjectName(u"nk2_page_emrich")
        self.formLayout_12 = QFormLayout(self.nk2_page_emrich)
        self.formLayout_12.setObjectName(u"formLayout_12")
        self.label_4 = QLabel(self.nk2_page_emrich)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setMinimumSize(QSize(0, 31))

        self.formLayout_12.setWidget(0, QFormLayout.LabelRole, self.label_4)

        self.peak_emrich_window_seconds = QDoubleSpinBox(self.nk2_page_emrich)
        self.peak_emrich_window_seconds.setObjectName(u"peak_emrich_window_seconds")
        self.peak_emrich_window_seconds.setMinimumSize(QSize(0, 31))
        self.peak_emrich_window_seconds.setDecimals(1)
        self.peak_emrich_window_seconds.setMinimum(1.000000000000000)
        self.peak_emrich_window_seconds.setSingleStep(0.100000000000000)
        self.peak_emrich_window_seconds.setValue(2.000000000000000)

        self.formLayout_12.setWidget(0, QFormLayout.FieldRole, self.peak_emrich_window_seconds)

        self.windowOverlapLabel = QLabel(self.nk2_page_emrich)
        self.windowOverlapLabel.setObjectName(u"windowOverlapLabel")
        self.windowOverlapLabel.setMinimumSize(QSize(0, 31))

        self.formLayout_12.setWidget(1, QFormLayout.LabelRole, self.windowOverlapLabel)

        self.peak_emrich_window_overlap = QDoubleSpinBox(self.nk2_page_emrich)
        self.peak_emrich_window_overlap.setObjectName(u"peak_emrich_window_overlap")
        self.peak_emrich_window_overlap.setMinimumSize(QSize(0, 31))
        self.peak_emrich_window_overlap.setDecimals(2)
        self.peak_emrich_window_overlap.setMinimum(0.010000000000000)
        self.peak_emrich_window_overlap.setMaximum(1.000000000000000)
        self.peak_emrich_window_overlap.setSingleStep(0.010000000000000)
        self.peak_emrich_window_overlap.setValue(0.500000000000000)

        self.formLayout_12.setWidget(1, QFormLayout.FieldRole, self.peak_emrich_window_overlap)

        self.acceleratedLabel = QLabel(self.nk2_page_emrich)
        self.acceleratedLabel.setObjectName(u"acceleratedLabel")
        self.acceleratedLabel.setMinimumSize(QSize(0, 31))

        self.formLayout_12.setWidget(2, QFormLayout.LabelRole, self.acceleratedLabel)

        self.peak_emrich_accelerated = QCheckBox(self.nk2_page_emrich)
        self.peak_emrich_accelerated.setObjectName(u"peak_emrich_accelerated")
        self.peak_emrich_accelerated.setMinimumSize(QSize(0, 31))
        self.peak_emrich_accelerated.setChecked(True)

        self.formLayout_12.setWidget(2, QFormLayout.FieldRole, self.peak_emrich_accelerated)

        self.text_browser_peak_emrich = QTextBrowser(self.nk2_page_emrich)
        self.text_browser_peak_emrich.setObjectName(u"text_browser_peak_emrich")
        self.text_browser_peak_emrich.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)

        self.formLayout_12.setWidget(3, QFormLayout.SpanningRole, self.text_browser_peak_emrich)

        self.stacked_nk2_method_parameters.addWidget(self.nk2_page_emrich)
        self.nk2_page_promac = QWidget()
        self.nk2_page_promac.setObjectName(u"nk2_page_promac")
        self.formLayout_13 = QFormLayout(self.nk2_page_promac)
        self.formLayout_13.setObjectName(u"formLayout_13")
        self.thresholdLabel_2 = QLabel(self.nk2_page_promac)
        self.thresholdLabel_2.setObjectName(u"thresholdLabel_2")
        self.thresholdLabel_2.setMinimumSize(QSize(0, 31))
        self.thresholdLabel_2.setFont(font1)

        self.formLayout_13.setWidget(0, QFormLayout.LabelRole, self.thresholdLabel_2)

        self.peak_promac_threshold = QDoubleSpinBox(self.nk2_page_promac)
        self.peak_promac_threshold.setObjectName(u"peak_promac_threshold")
        self.peak_promac_threshold.setMinimumSize(QSize(0, 31))
        self.peak_promac_threshold.setMaximum(1.000000000000000)
        self.peak_promac_threshold.setSingleStep(0.010000000000000)
        self.peak_promac_threshold.setValue(0.330000000000000)

        self.formLayout_13.setWidget(0, QFormLayout.FieldRole, self.peak_promac_threshold)

        self.qRSComplexSizeLabel_2 = QLabel(self.nk2_page_promac)
        self.qRSComplexSizeLabel_2.setObjectName(u"qRSComplexSizeLabel_2")
        self.qRSComplexSizeLabel_2.setMinimumSize(QSize(0, 31))
        self.qRSComplexSizeLabel_2.setFont(font1)

        self.formLayout_13.setWidget(1, QFormLayout.LabelRole, self.qRSComplexSizeLabel_2)

        self.peak_promac_gaussian_sd = QSpinBox(self.nk2_page_promac)
        self.peak_promac_gaussian_sd.setObjectName(u"peak_promac_gaussian_sd")
        self.peak_promac_gaussian_sd.setMinimumSize(QSize(0, 31))
        self.peak_promac_gaussian_sd.setMaximum(100000)
        self.peak_promac_gaussian_sd.setValue(100)

        self.formLayout_13.setWidget(1, QFormLayout.FieldRole, self.peak_promac_gaussian_sd)

        self.text_browser_peak_promac = QTextBrowser(self.nk2_page_promac)
        self.text_browser_peak_promac.setObjectName(u"text_browser_peak_promac")
        self.text_browser_peak_promac.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)

        self.formLayout_13.setWidget(2, QFormLayout.SpanningRole, self.text_browser_peak_promac)

        self.stacked_nk2_method_parameters.addWidget(self.nk2_page_promac)

        self.formLayout_6.setWidget(2, QFormLayout.SpanningRole, self.collapsible_nk2_peak_inputs)

        self.stacked_peak_parameters.addWidget(self.page_peak_neurokit2)
        self.page_peak_xqrs = QWidget()
        self.page_peak_xqrs.setObjectName(u"page_peak_xqrs")
        self.formLayout_9 = QFormLayout(self.page_peak_xqrs)
        self.formLayout_9.setObjectName(u"formLayout_9")
        self.peak_xqrs_info = QTextBrowser(self.page_peak_xqrs)
        self.peak_xqrs_info.setObjectName(u"peak_xqrs_info")
        sizePolicy2.setHeightForWidth(self.peak_xqrs_info.sizePolicy().hasHeightForWidth())
        self.peak_xqrs_info.setSizePolicy(sizePolicy2)
        self.peak_xqrs_info.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)

        self.formLayout_9.setWidget(0, QFormLayout.SpanningRole, self.peak_xqrs_info)

        self.searchRadiusLabel = QLabel(self.page_peak_xqrs)
        self.searchRadiusLabel.setObjectName(u"searchRadiusLabel")
        self.searchRadiusLabel.setMinimumSize(QSize(0, 31))
        self.searchRadiusLabel.setFont(font1)

        self.formLayout_9.setWidget(1, QFormLayout.LabelRole, self.searchRadiusLabel)

        self.peak_xqrs_search_radius = QSpinBox(self.page_peak_xqrs)
        self.peak_xqrs_search_radius.setObjectName(u"peak_xqrs_search_radius")
        self.peak_xqrs_search_radius.setMinimumSize(QSize(0, 31))
        self.peak_xqrs_search_radius.setAccelerated(True)
        self.peak_xqrs_search_radius.setCorrectionMode(QAbstractSpinBox.CorrectionMode.CorrectToNearestValue)
        self.peak_xqrs_search_radius.setMinimum(5)
        self.peak_xqrs_search_radius.setMaximum(99999)
        self.peak_xqrs_search_radius.setValue(90)

        self.formLayout_9.setWidget(1, QFormLayout.FieldRole, self.peak_xqrs_search_radius)

        self.adjustPeaksLabel = QLabel(self.page_peak_xqrs)
        self.adjustPeaksLabel.setObjectName(u"adjustPeaksLabel")
        self.adjustPeaksLabel.setMinimumSize(QSize(0, 31))
        self.adjustPeaksLabel.setFont(font1)

        self.formLayout_9.setWidget(2, QFormLayout.LabelRole, self.adjustPeaksLabel)

        self.peak_xqrs_peak_dir = QEnumComboBox(self.page_peak_xqrs)
        self.peak_xqrs_peak_dir.setObjectName(u"peak_xqrs_peak_dir")
        self.peak_xqrs_peak_dir.setMinimumSize(QSize(0, 31))

        self.formLayout_9.setWidget(2, QFormLayout.FieldRole, self.peak_xqrs_peak_dir)

        self.stacked_peak_parameters.addWidget(self.page_peak_xqrs)

        self.verticalLayout.addWidget(self.stacked_peak_parameters)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.gridLayout.addWidget(self.scrollArea, 4, 0, 1, 5)

        self.label = QLabel(self.dockWidgetContents)
        self.label.setObjectName(u"label")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy3)
        self.label.setMinimumSize(QSize(0, 31))
        self.label.setFont(font1)
        self.label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)

        self.gridLayout.addWidget(self.label, 2, 0, 1, 1)

        self.enum_combo_peak_method = QEnumComboBox(self.dockWidgetContents)
        self.enum_combo_peak_method.setObjectName(u"enum_combo_peak_method")
        self.enum_combo_peak_method.setMinimumSize(QSize(0, 31))

        self.gridLayout.addWidget(self.enum_combo_peak_method, 2, 1, 1, 4)

        self.btn_clear_peaks = QPushButton(self.dockWidgetContents)
        self.btn_clear_peaks.setObjectName(u"btn_clear_peaks")
        sizePolicy3.setHeightForWidth(self.btn_clear_peaks.sizePolicy().hasHeightForWidth())
        self.btn_clear_peaks.setSizePolicy(sizePolicy3)
        self.btn_clear_peaks.setMinimumSize(QSize(0, 31))
        icon = QIcon()
        icon.addFile(u":/icons/eraser", QSize(), QIcon.Normal, QIcon.Off)
        self.btn_clear_peaks.setIcon(icon)
        self.btn_clear_peaks.setFlat(True)

        self.gridLayout.addWidget(self.btn_clear_peaks, 1, 4, 1, 1)

        self.btn_reset_peak_inputs = QPushButton(self.dockWidgetContents)
        self.btn_reset_peak_inputs.setObjectName(u"btn_reset_peak_inputs")
        sizePolicy3.setHeightForWidth(self.btn_reset_peak_inputs.sizePolicy().hasHeightForWidth())
        self.btn_reset_peak_inputs.setSizePolicy(sizePolicy3)
        self.btn_reset_peak_inputs.setMinimumSize(QSize(0, 31))
        icon1 = QIcon()
        icon1.addFile(u":/icons/restore_defaults", QSize(), QIcon.Normal, QIcon.Off)
        self.btn_reset_peak_inputs.setIcon(icon1)
        self.btn_reset_peak_inputs.setFlat(True)

        self.gridLayout.addWidget(self.btn_reset_peak_inputs, 1, 3, 1, 1)

        self.btn_run_peak_detection = QPushButton(self.dockWidgetContents)
        self.btn_run_peak_detection.setObjectName(u"btn_run_peak_detection")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.btn_run_peak_detection.sizePolicy().hasHeightForWidth())
        self.btn_run_peak_detection.setSizePolicy(sizePolicy4)
        self.btn_run_peak_detection.setMinimumSize(QSize(0, 31))

        self.gridLayout.addWidget(self.btn_run_peak_detection, 1, 0, 1, 3)

        self.label_2 = QLabel(self.dockWidgetContents)
        self.label_2.setObjectName(u"label_2")
        sizePolicy4.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy4)

        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 5)

        DockWidgetPeakDetection.setWidget(self.dockWidgetContents)

        self.retranslateUi(DockWidgetPeakDetection)

        self.stacked_peak_parameters.setCurrentIndex(3)
        self.stacked_nk2_method_parameters.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(DockWidgetPeakDetection)
    # setupUi

    def retranslateUi(self, DockWidgetPeakDetection):
        DockWidgetPeakDetection.setWindowTitle(QCoreApplication.translate("DockWidgetPeakDetection", u"Peak Detection", None))
        self.peak_elgendi_ppg_info.setHtml(QCoreApplication.translate("DockWidgetPeakDetection", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Algorithm for detecting peaks in a PPG signal, described <a href=\"https://doi.org/10.1371/journal.pone.0076585\"><span style=\" text-decoration: underline; color:#1e3260;\">here</span></a></p></body></html>", None))
        self.label_peak_window.setText(QCoreApplication.translate("DockWidgetPeakDetection", u"Peak Window", None))
        self.peak_elgendi_ppg_peakwindow.setSuffix(QCoreApplication.translate("DockWidgetPeakDetection", u" s", None))
        self.beatWindowLabel.setText(QCoreApplication.translate("DockWidgetPeakDetection", u"Beat Window", None))
        self.peak_elgendi_ppg_beatwindow.setSuffix(QCoreApplication.translate("DockWidgetPeakDetection", u" s", None))
        self.beatOffsetLabel.setText(QCoreApplication.translate("DockWidgetPeakDetection", u"Beat Offset", None))
        self.peak_elgendi_ppg_beatoffset.setSuffix("")
        self.minimumDelayLabel.setText(QCoreApplication.translate("DockWidgetPeakDetection", u"Minimum Delay", None))
        self.peak_elgendi_ppg_mindelay.setSuffix(QCoreApplication.translate("DockWidgetPeakDetection", u" s", None))
        self.label_22.setText(QCoreApplication.translate("DockWidgetPeakDetection", u"Search Radius", None))
        self.peak_local_max_info.setHtml(QCoreApplication.translate("DockWidgetPeakDetection", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Detects peaks by finding the highest point in a window of the selected size around the current point.</p></body></html>", None))
#if QT_CONFIG(tooltip)
        self.minDistanceLabel.setToolTip(QCoreApplication.translate("DockWidgetPeakDetection", u"Minimum allowed distance between two consecutive peaks", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(whatsthis)
        self.minDistanceLabel.setWhatsThis(QCoreApplication.translate("DockWidgetPeakDetection", u"After a peak is detected, how many values to skip ahead before starting to search for the next peak", None))
#endif // QT_CONFIG(whatsthis)
        self.minDistanceLabel.setText(QCoreApplication.translate("DockWidgetPeakDetection", u"Min. Distance:", None))
        self.peak_local_min_info.setHtml(QCoreApplication.translate("DockWidgetPeakDetection", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Detects peaks by finding the lowest point in a window of the selected size around the current point.</p></body></html>", None))
        self.label_23.setText(QCoreApplication.translate("DockWidgetPeakDetection", u"Search Radius", None))
#if QT_CONFIG(tooltip)
        self.minDistanceLabel_2.setToolTip(QCoreApplication.translate("DockWidgetPeakDetection", u"Minimum allowed distance between two consecutive minima", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(whatsthis)
        self.minDistanceLabel_2.setWhatsThis(QCoreApplication.translate("DockWidgetPeakDetection", u"After a minimum is detected, how many values to skip ahead before starting to search for the next minimum", None))
#endif // QT_CONFIG(whatsthis)
        self.minDistanceLabel_2.setText(QCoreApplication.translate("DockWidgetPeakDetection", u"Min. Distance:", None))
        self.peak_neurokit2_info.setHtml(QCoreApplication.translate("DockWidgetPeakDetection", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Finds R-peaks in an ECG signal using the specified method/algorithm.</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">More Info: <a href=\"https://github.com/neuropsychology/NeuroKit/issues/476\"><span style=\" text-decoration: underline; color:#038387;\">Github Discussion</span></a></p>\n"
"<p style=\" margin-top:0px; mar"
                        "gin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Algorithms: <a href=\"https://neuropsychology.github.io/NeuroKit/functions/ecg.html#ecg-peaks\"><span style=\" text-decoration: underline; color:#038387;\">Function documentation</span></a></p></body></html>", None))
        self.algorithmLabel.setText(QCoreApplication.translate("DockWidgetPeakDetection", u"Algorithm", None))
        self.smoothingWindowLabel.setText(QCoreApplication.translate("DockWidgetPeakDetection", u"Smoothing Window", None))
        self.peak_neurokit2_smoothwindow.setSuffix(QCoreApplication.translate("DockWidgetPeakDetection", u" s", None))
        self.label_27.setText(QCoreApplication.translate("DockWidgetPeakDetection", u"Average Window", None))
        self.peak_neurokit2_avgwindow.setSuffix(QCoreApplication.translate("DockWidgetPeakDetection", u" s", None))
        self.label_28.setText(QCoreApplication.translate("DockWidgetPeakDetection", u"Grad. Thresh. Weight", None))
        self.label_29.setText(QCoreApplication.translate("DockWidgetPeakDetection", u"Min. Length Weight", None))
        self.label_30.setText(QCoreApplication.translate("DockWidgetPeakDetection", u"Minimum Delay", None))
        self.peak_neurokit2_mindelay.setSuffix(QCoreApplication.translate("DockWidgetPeakDetection", u" s", None))
        self.label_31.setText(QCoreApplication.translate("DockWidgetPeakDetection", u"Correct Artifacts", None))
        self.text_browser_peak_neurokit2.setHtml(QCoreApplication.translate("DockWidgetPeakDetection", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><a href=\"https://github.com/neuropsychology/NeuroKit/blob/master/neurokit2/ecg/ecg_findpeaks.py#L239\"><span style=\" text-decoration: underline; color:#1e3260;\">Source</span></a></p></body></html>", None))
        self.label_3.setText(QCoreApplication.translate("DockWidgetPeakDetection", u"<html><head/><body><p><span style=\" font-weight:700;\">Threshold</span></p></body></html>", None))
        self.beforeLabel.setText(QCoreApplication.translate("DockWidgetPeakDetection", u"<html><head/><body><p><span style=\" font-weight:700;\">Before</span></p></body></html>", None))
        self.peak_ssf_before.setSuffix(QCoreApplication.translate("DockWidgetPeakDetection", u" s", None))
        self.afterLabel.setText(QCoreApplication.translate("DockWidgetPeakDetection", u"<html><head/><body><p><span style=\" font-weight:700;\">After</span></p></body></html>", None))
        self.peak_ssf_after.setSuffix(QCoreApplication.translate("DockWidgetPeakDetection", u" s", None))
        self.text_browser_peak_ssf.setHtml(QCoreApplication.translate("DockWidgetPeakDetection", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:700;\">Threshold</span>: Set the minimum squared slope change to detect R-peaks in the ECG signal. Higher values reduce noise detections but may miss some peaks; lower values increase sensitivity but may include noise. The unit is (volts/sample)^2.</p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0p"
                        "x;\"><span style=\" font-weight:700;\">Before</span>: Search window size before R-peak candidate (seconds)</p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:700;\">After</span>: Search window size after R-peak candidate (seconds)</p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><a href=\"https://github.com/PIA-Group/BioSPPy/blob/e65da30f6379852ecb98f8e2e0c9b4b5175416c3/biosppy/signals/ecg.py#L448\"><span style=\" text-decoration: underline; color:#1e3260;\">Source</span></a></p></body></html>", None))
        self.windowLabel.setText(QCoreApplication.translate("DockWidgetPeakDetection", u"<html><head/><body><p><span style=\" font-weight:700;\">Tolerance</span></p></body></html>", None))
        self.text_browser_peak_gamboa.setHtml(QCoreApplication.translate("DockWidgetPeakDetection", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:700;\">Tolerance</span>: Set the threshold for detecting significant changes in the second derivative of the normalized ECG signal. Lower values increase sensitivity to minor variations, while higher values focus on more prominent features.</p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><a "
                        "href=\"https://github.com/PIA-Group/BioSPPy/blob/e65da30f6379852ecb98f8e2e0c9b4b5175416c3/biosppy/signals/ecg.py#L834\"><span style=\" text-decoration: underline; color:#1e3260;\">Source</span></a></p></body></html>", None))
        self.label_4.setText(QCoreApplication.translate("DockWidgetPeakDetection", u"<html><head/><body><p><span style=\" font-weight:700;\">Window Seconds</span></p></body></html>", None))
        self.peak_emrich_window_seconds.setSuffix(QCoreApplication.translate("DockWidgetPeakDetection", u" s", None))
        self.windowOverlapLabel.setText(QCoreApplication.translate("DockWidgetPeakDetection", u"<html><head/><body><p><span style=\" font-weight:700;\">Window Overlap</span></p></body></html>", None))
        self.acceleratedLabel.setText(QCoreApplication.translate("DockWidgetPeakDetection", u"<html><head/><body><p><span style=\" font-weight:700;\">Accelerated</span></p></body></html>", None))
        self.text_browser_peak_emrich.setHtml(QCoreApplication.translate("DockWidgetPeakDetection", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:700;\">Window Seconds</span>: Length of on data segment (in seconds!) used in the segment-wise processing of the ECG signal.</p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:700;\">Window Overlap</span>: Overlap percentage (between 0 and 1) of the data segments used"
                        " in the segment-wise computation.</p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:700;\">Accelerated</span>: Enables the data pre-processing in which the input signal is reduced only to local maxima which reduces the computation time by one order of magnitude while the performance remains comparable.</p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><a href=\"https://github.com/neuropsychology/NeuroKit/blob/master/neurokit2/ecg/ecg_findpeaks.py#L1181\"><span style=\" text-decoration: underline; color:#1e3260;\">Source</span></a></p></body></html>", None))
        self.thresholdLabel_2.setText(QCoreApplication.translate("DockWidgetPeakDetection", u"Threshold", None))
        self.qRSComplexSizeLabel_2.setText(QCoreApplication.translate("DockWidgetPeakDetection", u"Gaussian SD", None))
        self.peak_promac_gaussian_sd.setSuffix(QCoreApplication.translate("DockWidgetPeakDetection", u" ms", None))
        self.text_browser_peak_promac.setHtml(QCoreApplication.translate("DockWidgetPeakDetection", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:700;\">Threshold</span>: The tolerance for peak acceptance. This value is a percentage of the signal's maximum value. Only peaks found above this tolerance will be finally considered as actual peaks.</p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:700;\">Gaussian S"
                        "D</span>: The standard deviation of the Gaussian distribution used to represent the peak location probability. This value should be in milliseconds and is usually taken as the size of QRS complexes.</p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><a href=\"https://github.com/neuropsychology/NeuroKit/blob/master/neurokit2/ecg/ecg_findpeaks.py#L130\"><span style=\" text-decoration: underline; color:#1e3260;\">Source</span></a></p></body></html>", None))
        self.peak_xqrs_info.setHtml(QCoreApplication.translate("DockWidgetPeakDetection", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Uses XQRS detection from the 'wfdb' library, with a slightly modified peak correction step afterwards.</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Can take a while to finish when using on sections longer than 1e6 samples.</p></body></html>", None))
        self.searchRadiusLabel.setText(QCoreApplication.translate("DockWidgetPeakDetection", u"Search Radius", None))
        self.adjustPeaksLabel.setText(QCoreApplication.translate("DockWidgetPeakDetection", u"Adjust Peaks", None))
        self.label.setText(QCoreApplication.translate("DockWidgetPeakDetection", u"Detection Method:", None))
#if QT_CONFIG(tooltip)
        self.btn_clear_peaks.setToolTip(QCoreApplication.translate("DockWidgetPeakDetection", u"Clear detected peaks (for active section)", None))
#endif // QT_CONFIG(tooltip)
        self.btn_clear_peaks.setText("")
#if QT_CONFIG(tooltip)
        self.btn_reset_peak_inputs.setToolTip(QCoreApplication.translate("DockWidgetPeakDetection", u"Restore all input fields to their default values", None))
#endif // QT_CONFIG(tooltip)
        self.btn_run_peak_detection.setText(QCoreApplication.translate("DockWidgetPeakDetection", u" Run peak detection", None))
        self.label_2.setText(QCoreApplication.translate("DockWidgetPeakDetection", u"<html><head/><body><p><span style=\" font-size:12pt; font-weight:700;\">Peak Detection Parameters</span></p></body></html>", None))
    # retranslateUi

