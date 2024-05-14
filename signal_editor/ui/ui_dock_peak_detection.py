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

from superqt import QEnumComboBox
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
        self.algorithmLabel = QLabel(self.page_peak_neurokit2)
        self.algorithmLabel.setObjectName(u"algorithmLabel")
        self.algorithmLabel.setEnabled(False)
        self.algorithmLabel.setMinimumSize(QSize(0, 31))
        self.algorithmLabel.setFont(font1)

        self.formLayout_6.setWidget(1, QFormLayout.LabelRole, self.algorithmLabel)

        self.peak_neurokit2_algorithm_used = QEnumComboBox(self.page_peak_neurokit2)
        self.peak_neurokit2_algorithm_used.setObjectName(u"peak_neurokit2_algorithm_used")
        self.peak_neurokit2_algorithm_used.setEnabled(False)
        self.peak_neurokit2_algorithm_used.setMinimumSize(QSize(0, 31))

        self.formLayout_6.setWidget(1, QFormLayout.FieldRole, self.peak_neurokit2_algorithm_used)

        self.smoothingWindowLabel = QLabel(self.page_peak_neurokit2)
        self.smoothingWindowLabel.setObjectName(u"smoothingWindowLabel")
        self.smoothingWindowLabel.setMinimumSize(QSize(0, 31))
        self.smoothingWindowLabel.setFont(font1)

        self.formLayout_6.setWidget(2, QFormLayout.LabelRole, self.smoothingWindowLabel)

        self.peak_neurokit2_smoothwindow = QDoubleSpinBox(self.page_peak_neurokit2)
        self.peak_neurokit2_smoothwindow.setObjectName(u"peak_neurokit2_smoothwindow")
        self.peak_neurokit2_smoothwindow.setMinimumSize(QSize(0, 31))
        self.peak_neurokit2_smoothwindow.setMinimum(0.010000000000000)
        self.peak_neurokit2_smoothwindow.setMaximum(10.000000000000000)
        self.peak_neurokit2_smoothwindow.setSingleStep(0.010000000000000)

        self.formLayout_6.setWidget(2, QFormLayout.FieldRole, self.peak_neurokit2_smoothwindow)

        self.label_27 = QLabel(self.page_peak_neurokit2)
        self.label_27.setObjectName(u"label_27")
        self.label_27.setMinimumSize(QSize(0, 31))
        self.label_27.setFont(font1)

        self.formLayout_6.setWidget(3, QFormLayout.LabelRole, self.label_27)

        self.peak_neurokit2_avgwindow = QDoubleSpinBox(self.page_peak_neurokit2)
        self.peak_neurokit2_avgwindow.setObjectName(u"peak_neurokit2_avgwindow")
        self.peak_neurokit2_avgwindow.setMinimumSize(QSize(0, 31))
        self.peak_neurokit2_avgwindow.setDecimals(2)
        self.peak_neurokit2_avgwindow.setMinimum(0.010000000000000)
        self.peak_neurokit2_avgwindow.setMaximum(10.000000000000000)
        self.peak_neurokit2_avgwindow.setSingleStep(0.010000000000000)
        self.peak_neurokit2_avgwindow.setValue(0.750000000000000)

        self.formLayout_6.setWidget(3, QFormLayout.FieldRole, self.peak_neurokit2_avgwindow)

        self.label_28 = QLabel(self.page_peak_neurokit2)
        self.label_28.setObjectName(u"label_28")
        self.label_28.setMinimumSize(QSize(0, 31))
        self.label_28.setFont(font1)

        self.formLayout_6.setWidget(4, QFormLayout.LabelRole, self.label_28)

        self.peak_neurokit2_gradthreshweight = QDoubleSpinBox(self.page_peak_neurokit2)
        self.peak_neurokit2_gradthreshweight.setObjectName(u"peak_neurokit2_gradthreshweight")
        self.peak_neurokit2_gradthreshweight.setMinimumSize(QSize(0, 31))
        self.peak_neurokit2_gradthreshweight.setDecimals(1)
        self.peak_neurokit2_gradthreshweight.setMinimum(0.100000000000000)
        self.peak_neurokit2_gradthreshweight.setMaximum(10.000000000000000)
        self.peak_neurokit2_gradthreshweight.setSingleStep(0.100000000000000)
        self.peak_neurokit2_gradthreshweight.setValue(1.500000000000000)

        self.formLayout_6.setWidget(4, QFormLayout.FieldRole, self.peak_neurokit2_gradthreshweight)

        self.label_29 = QLabel(self.page_peak_neurokit2)
        self.label_29.setObjectName(u"label_29")
        self.label_29.setMinimumSize(QSize(0, 31))
        self.label_29.setFont(font1)

        self.formLayout_6.setWidget(5, QFormLayout.LabelRole, self.label_29)

        self.peak_neurokit2_minlenweight = QDoubleSpinBox(self.page_peak_neurokit2)
        self.peak_neurokit2_minlenweight.setObjectName(u"peak_neurokit2_minlenweight")
        self.peak_neurokit2_minlenweight.setMinimumSize(QSize(0, 31))
        self.peak_neurokit2_minlenweight.setDecimals(1)
        self.peak_neurokit2_minlenweight.setMinimum(0.100000000000000)
        self.peak_neurokit2_minlenweight.setMaximum(10.000000000000000)
        self.peak_neurokit2_minlenweight.setSingleStep(0.100000000000000)
        self.peak_neurokit2_minlenweight.setValue(0.400000000000000)

        self.formLayout_6.setWidget(5, QFormLayout.FieldRole, self.peak_neurokit2_minlenweight)

        self.label_30 = QLabel(self.page_peak_neurokit2)
        self.label_30.setObjectName(u"label_30")
        self.label_30.setMinimumSize(QSize(0, 31))
        self.label_30.setFont(font1)

        self.formLayout_6.setWidget(6, QFormLayout.LabelRole, self.label_30)

        self.peak_neurokit2_mindelay = QDoubleSpinBox(self.page_peak_neurokit2)
        self.peak_neurokit2_mindelay.setObjectName(u"peak_neurokit2_mindelay")
        self.peak_neurokit2_mindelay.setMinimumSize(QSize(0, 31))
        self.peak_neurokit2_mindelay.setMinimum(0.010000000000000)
        self.peak_neurokit2_mindelay.setMaximum(10.000000000000000)
        self.peak_neurokit2_mindelay.setSingleStep(0.010000000000000)
        self.peak_neurokit2_mindelay.setValue(0.300000000000000)

        self.formLayout_6.setWidget(6, QFormLayout.FieldRole, self.peak_neurokit2_mindelay)

        self.label_31 = QLabel(self.page_peak_neurokit2)
        self.label_31.setObjectName(u"label_31")
        self.label_31.setMinimumSize(QSize(0, 31))
        self.label_31.setFont(font1)

        self.formLayout_6.setWidget(7, QFormLayout.LabelRole, self.label_31)

        self.peak_neurokit2_correct_artifacts = QCheckBox(self.page_peak_neurokit2)
        self.peak_neurokit2_correct_artifacts.setObjectName(u"peak_neurokit2_correct_artifacts")
        self.peak_neurokit2_correct_artifacts.setMinimumSize(QSize(0, 31))

        self.formLayout_6.setWidget(7, QFormLayout.FieldRole, self.peak_neurokit2_correct_artifacts)

        self.peak_neurokit2_info = QTextBrowser(self.page_peak_neurokit2)
        self.peak_neurokit2_info.setObjectName(u"peak_neurokit2_info")
        sizePolicy2.setHeightForWidth(self.peak_neurokit2_info.sizePolicy().hasHeightForWidth())
        self.peak_neurokit2_info.setSizePolicy(sizePolicy2)
        self.peak_neurokit2_info.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)

        self.formLayout_6.setWidget(0, QFormLayout.SpanningRole, self.peak_neurokit2_info)

        self.stacked_peak_parameters.addWidget(self.page_peak_neurokit2)
        self.page_peak_promac = QWidget()
        self.page_peak_promac.setObjectName(u"page_peak_promac")
        self.formLayout_7 = QFormLayout(self.page_peak_promac)
        self.formLayout_7.setObjectName(u"formLayout_7")
        self.thresholdLabel = QLabel(self.page_peak_promac)
        self.thresholdLabel.setObjectName(u"thresholdLabel")
        self.thresholdLabel.setMinimumSize(QSize(0, 31))
        self.thresholdLabel.setFont(font1)

        self.formLayout_7.setWidget(1, QFormLayout.LabelRole, self.thresholdLabel)

        self.peak_promac_threshold = QDoubleSpinBox(self.page_peak_promac)
        self.peak_promac_threshold.setObjectName(u"peak_promac_threshold")
        self.peak_promac_threshold.setMinimumSize(QSize(0, 31))
        self.peak_promac_threshold.setMaximum(1.000000000000000)
        self.peak_promac_threshold.setSingleStep(0.010000000000000)
        self.peak_promac_threshold.setValue(0.330000000000000)

        self.formLayout_7.setWidget(1, QFormLayout.FieldRole, self.peak_promac_threshold)

        self.qRSComplexSizeLabel = QLabel(self.page_peak_promac)
        self.qRSComplexSizeLabel.setObjectName(u"qRSComplexSizeLabel")
        self.qRSComplexSizeLabel.setMinimumSize(QSize(0, 31))
        self.qRSComplexSizeLabel.setFont(font1)

        self.formLayout_7.setWidget(2, QFormLayout.LabelRole, self.qRSComplexSizeLabel)

        self.correctArtifactsLabel_2 = QLabel(self.page_peak_promac)
        self.correctArtifactsLabel_2.setObjectName(u"correctArtifactsLabel_2")
        self.correctArtifactsLabel_2.setMinimumSize(QSize(0, 31))
        self.correctArtifactsLabel_2.setFont(font1)

        self.formLayout_7.setWidget(3, QFormLayout.LabelRole, self.correctArtifactsLabel_2)

        self.peak_promac_correct_artifacts = QCheckBox(self.page_peak_promac)
        self.peak_promac_correct_artifacts.setObjectName(u"peak_promac_correct_artifacts")
        self.peak_promac_correct_artifacts.setMinimumSize(QSize(0, 31))

        self.formLayout_7.setWidget(3, QFormLayout.FieldRole, self.peak_promac_correct_artifacts)

        self.peak_promac_gaussian_sd = QSpinBox(self.page_peak_promac)
        self.peak_promac_gaussian_sd.setObjectName(u"peak_promac_gaussian_sd")
        self.peak_promac_gaussian_sd.setMinimumSize(QSize(0, 31))
        self.peak_promac_gaussian_sd.setMaximum(100000)
        self.peak_promac_gaussian_sd.setValue(100)

        self.formLayout_7.setWidget(2, QFormLayout.FieldRole, self.peak_promac_gaussian_sd)

        self.peak_promac_info = QTextBrowser(self.page_peak_promac)
        self.peak_promac_info.setObjectName(u"peak_promac_info")
        sizePolicy2.setHeightForWidth(self.peak_promac_info.sizePolicy().hasHeightForWidth())
        self.peak_promac_info.setSizePolicy(sizePolicy2)
        self.peak_promac_info.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)

        self.formLayout_7.setWidget(0, QFormLayout.SpanningRole, self.peak_promac_info)

        self.stacked_peak_parameters.addWidget(self.page_peak_promac)
        self.page_peak_pantompkins = QWidget()
        self.page_peak_pantompkins.setObjectName(u"page_peak_pantompkins")
        self.formLayout_8 = QFormLayout(self.page_peak_pantompkins)
        self.formLayout_8.setObjectName(u"formLayout_8")
        self.correctArtifactsLabel = QLabel(self.page_peak_pantompkins)
        self.correctArtifactsLabel.setObjectName(u"correctArtifactsLabel")
        self.correctArtifactsLabel.setMinimumSize(QSize(0, 31))
        self.correctArtifactsLabel.setFont(font1)

        self.formLayout_8.setWidget(1, QFormLayout.LabelRole, self.correctArtifactsLabel)

        self.peak_pantompkins_correct_artifacts = QCheckBox(self.page_peak_pantompkins)
        self.peak_pantompkins_correct_artifacts.setObjectName(u"peak_pantompkins_correct_artifacts")
        self.peak_pantompkins_correct_artifacts.setMinimumSize(QSize(0, 31))

        self.formLayout_8.setWidget(1, QFormLayout.FieldRole, self.peak_pantompkins_correct_artifacts)

        self.peak_pantompkins_info = QTextBrowser(self.page_peak_pantompkins)
        self.peak_pantompkins_info.setObjectName(u"peak_pantompkins_info")
        sizePolicy2.setHeightForWidth(self.peak_pantompkins_info.sizePolicy().hasHeightForWidth())
        self.peak_pantompkins_info.setSizePolicy(sizePolicy2)
        self.peak_pantompkins_info.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)

        self.formLayout_8.setWidget(0, QFormLayout.SpanningRole, self.peak_pantompkins_info)

        self.stacked_peak_parameters.addWidget(self.page_peak_pantompkins)
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

        self.stacked_peak_parameters.setCurrentIndex(0)


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
        self.thresholdLabel.setText(QCoreApplication.translate("DockWidgetPeakDetection", u"Threshold", None))
        self.qRSComplexSizeLabel.setText(QCoreApplication.translate("DockWidgetPeakDetection", u"QRS Complex Size", None))
        self.correctArtifactsLabel_2.setText(QCoreApplication.translate("DockWidgetPeakDetection", u"Correct Artifacts", None))
        self.peak_promac_gaussian_sd.setSuffix(QCoreApplication.translate("DockWidgetPeakDetection", u" ms", None))
        self.peak_promac_info.setHtml(QCoreApplication.translate("DockWidgetPeakDetection", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Finds peaks by running multiple peak detection algorithms and combining the results. Takes a while to run</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Source: <a href=\"https://github.com/neuropsychology/NeuroKit/issues/222\"><span style=\" text-decoration: underline; color:#038387;\">https://github.com/neuropsycholo"
                        "gy/NeuroKit/issues/222</span></a></p></body></html>", None))
        self.correctArtifactsLabel.setText(QCoreApplication.translate("DockWidgetPeakDetection", u"Correct Artifacts", None))
        self.peak_pantompkins_info.setHtml(QCoreApplication.translate("DockWidgetPeakDetection", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Uses the algorithm for ECG R-Peak detection by Pan &amp; Tompkins (1985)</p></body></html>", None))
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

