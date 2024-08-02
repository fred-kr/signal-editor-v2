# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'dialog_metadata.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QAbstractScrollArea, QApplication, QDialog,
    QFormLayout, QGridLayout, QHeaderView, QLabel,
    QScrollArea, QSizePolicy, QSpacerItem, QTreeWidgetItem,
    QVBoxLayout, QWidget)

from pyqtgraph import DataTreeWidget
from qfluentwidgets import (BodyLabel, ComboBox, LineEdit, PushButton,
    SpinBox)

class Ui_MetadataDialog(object):
    def setupUi(self, MetadataDialog):
        if not MetadataDialog.objectName():
            MetadataDialog.setObjectName(u"MetadataDialog")
        MetadataDialog.resize(653, 772)
        self.gridLayout = QGridLayout(MetadataDialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.btn_accept = PushButton(MetadataDialog)
        self.btn_accept.setObjectName(u"btn_accept")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_accept.sizePolicy().hasHeightForWidth())
        self.btn_accept.setSizePolicy(sizePolicy)
        self.btn_accept.setMinimumSize(QSize(75, 31))

        self.gridLayout.addWidget(self.btn_accept, 1, 1, 1, 1)

        self.btn_reject = PushButton(MetadataDialog)
        self.btn_reject.setObjectName(u"btn_reject")
        sizePolicy.setHeightForWidth(self.btn_reject.sizePolicy().hasHeightForWidth())
        self.btn_reject.setSizePolicy(sizePolicy)
        self.btn_reject.setMinimumSize(QSize(75, 31))

        self.gridLayout.addWidget(self.btn_reject, 1, 2, 1, 1)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer, 1, 0, 1, 1)

        self.scrollArea = QScrollArea(MetadataDialog)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 633, 715))
        self.verticalLayout_2 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label = QLabel(self.scrollAreaWidgetContents)
        self.label.setObjectName(u"label")

        self.verticalLayout.addWidget(self.label)

        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.label_2 = BodyLabel(self.scrollAreaWidgetContents)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setMinimumSize(QSize(0, 31))

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label_2)

        self.line_edit_file_name = LineEdit(self.scrollAreaWidgetContents)
        self.line_edit_file_name.setObjectName(u"line_edit_file_name")
        self.line_edit_file_name.setMinimumSize(QSize(0, 31))
        self.line_edit_file_name.setFrame(False)
        self.line_edit_file_name.setReadOnly(True)

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.line_edit_file_name)

        self.label_4 = BodyLabel(self.scrollAreaWidgetContents)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setMinimumSize(QSize(0, 31))

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label_4)

        self.line_edit_file_type = LineEdit(self.scrollAreaWidgetContents)
        self.line_edit_file_type.setObjectName(u"line_edit_file_type")
        self.line_edit_file_type.setMinimumSize(QSize(0, 31))
        self.line_edit_file_type.setFrame(False)
        self.line_edit_file_type.setReadOnly(True)

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.line_edit_file_type)

        self.label_3 = BodyLabel(self.scrollAreaWidgetContents)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setMinimumSize(QSize(0, 31))

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.label_3)

        self.spin_box_sampling_rate = SpinBox(self.scrollAreaWidgetContents)
        self.spin_box_sampling_rate.setObjectName(u"spin_box_sampling_rate")
        self.spin_box_sampling_rate.setMinimumSize(QSize(0, 31))
        self.spin_box_sampling_rate.setFrame(False)
        self.spin_box_sampling_rate.setMaximum(10000)

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.spin_box_sampling_rate)

        self.label_5 = BodyLabel(self.scrollAreaWidgetContents)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setMinimumSize(QSize(0, 31))

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.label_5)

        self.combo_box_signal_column = ComboBox(self.scrollAreaWidgetContents)
        self.combo_box_signal_column.setObjectName(u"combo_box_signal_column")
        self.combo_box_signal_column.setMinimumSize(QSize(0, 31))

        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.combo_box_signal_column)

        self.label_6 = BodyLabel(self.scrollAreaWidgetContents)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setMinimumSize(QSize(0, 31))

        self.formLayout.setWidget(4, QFormLayout.LabelRole, self.label_6)

        self.combo_box_info_column = ComboBox(self.scrollAreaWidgetContents)
        self.combo_box_info_column.setObjectName(u"combo_box_info_column")
        self.combo_box_info_column.setMinimumSize(QSize(0, 31))

        self.formLayout.setWidget(4, QFormLayout.FieldRole, self.combo_box_info_column)

        self.label_7 = BodyLabel(self.scrollAreaWidgetContents)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setMinimumSize(QSize(0, 31))

        self.formLayout.setWidget(5, QFormLayout.LabelRole, self.label_7)

        self.data_tree_widget_additional_info = DataTreeWidget(self.scrollAreaWidgetContents)
        __qtreewidgetitem = QTreeWidgetItem()
        __qtreewidgetitem.setText(2, u"3");
        __qtreewidgetitem.setText(1, u"2");
        __qtreewidgetitem.setText(0, u"1");
        self.data_tree_widget_additional_info.setHeaderItem(__qtreewidgetitem)
        self.data_tree_widget_additional_info.setObjectName(u"data_tree_widget_additional_info")
        self.data_tree_widget_additional_info.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContentsOnFirstShow)
        self.data_tree_widget_additional_info.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.data_tree_widget_additional_info.setProperty("showDropIndicator", False)
        self.data_tree_widget_additional_info.setWordWrap(True)
        self.data_tree_widget_additional_info.setHeaderHidden(True)
        self.data_tree_widget_additional_info.setExpandsOnDoubleClick(True)
        self.data_tree_widget_additional_info.setColumnCount(3)

        self.formLayout.setWidget(5, QFormLayout.FieldRole, self.data_tree_widget_additional_info)


        self.verticalLayout.addLayout(self.formLayout)

        self.label_8 = QLabel(self.scrollAreaWidgetContents)
        self.label_8.setObjectName(u"label_8")

        self.verticalLayout.addWidget(self.label_8)


        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.gridLayout.addWidget(self.scrollArea, 0, 0, 1, 3)

#if QT_CONFIG(shortcut)
        self.label_2.setBuddy(self.line_edit_file_name)
        self.label_4.setBuddy(self.line_edit_file_type)
        self.label_3.setBuddy(self.spin_box_sampling_rate)
        self.label_7.setBuddy(self.data_tree_widget_additional_info)
#endif // QT_CONFIG(shortcut)
        QWidget.setTabOrder(self.scrollArea, self.line_edit_file_name)
        QWidget.setTabOrder(self.line_edit_file_name, self.line_edit_file_type)
        QWidget.setTabOrder(self.line_edit_file_type, self.spin_box_sampling_rate)
        QWidget.setTabOrder(self.spin_box_sampling_rate, self.combo_box_signal_column)
        QWidget.setTabOrder(self.combo_box_signal_column, self.combo_box_info_column)
        QWidget.setTabOrder(self.combo_box_info_column, self.data_tree_widget_additional_info)
        QWidget.setTabOrder(self.data_tree_widget_additional_info, self.btn_accept)
        QWidget.setTabOrder(self.btn_accept, self.btn_reject)

        self.retranslateUi(MetadataDialog)

        QMetaObject.connectSlotsByName(MetadataDialog)
    # setupUi

    def retranslateUi(self, MetadataDialog):
        MetadataDialog.setWindowTitle(QCoreApplication.translate("MetadataDialog", u"Dialog", None))
        self.btn_accept.setText(QCoreApplication.translate("MetadataDialog", u"Ok", None))
        self.btn_reject.setText(QCoreApplication.translate("MetadataDialog", u"Cancel", None))
        self.label.setText(QCoreApplication.translate("MetadataDialog", u"<html><head/><body><p><span style=\" font-size:14pt; font-weight:700;\">Metadata</span></p></body></html>", None))
        self.label_2.setText(QCoreApplication.translate("MetadataDialog", u"File Name", None))
        self.label_4.setText(QCoreApplication.translate("MetadataDialog", u"File Type", None))
        self.label_3.setText(QCoreApplication.translate("MetadataDialog", u"Sampling Rate*", None))
        self.spin_box_sampling_rate.setSuffix(QCoreApplication.translate("MetadataDialog", u" Hz", None))
        self.label_5.setText(QCoreApplication.translate("MetadataDialog", u"Signal Column / Channel*", None))
        self.combo_box_signal_column.setText("")
        self.label_6.setText(QCoreApplication.translate("MetadataDialog", u"Info Column / Channel", None))
        self.combo_box_info_column.setText("")
        self.label_7.setText(QCoreApplication.translate("MetadataDialog", u"Additional Info", None))
        self.label_8.setText(QCoreApplication.translate("MetadataDialog", u"*Field is required", None))
    # retranslateUi

