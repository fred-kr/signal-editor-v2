# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'dialog_metadata.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QAbstractItemView, QApplication, QComboBox,
    QDialog, QDialogButtonBox, QDoubleSpinBox, QFormLayout,
    QGridLayout, QHeaderView, QLabel, QLineEdit,
    QScrollArea, QSizePolicy, QTreeWidgetItem, QVBoxLayout,
    QWidget)

from pyqtgraph import DataTreeWidget

class Ui_MetadataDialog(object):
    def setupUi(self, MetadataDialog):
        if not MetadataDialog.objectName():
            MetadataDialog.setObjectName(u"MetadataDialog")
        MetadataDialog.resize(653, 772)
        self.gridLayout = QGridLayout(MetadataDialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.scrollArea = QScrollArea(MetadataDialog)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 633, 722))
        self.verticalLayout_2 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label = QLabel(self.scrollAreaWidgetContents)
        self.label.setObjectName(u"label")

        self.verticalLayout.addWidget(self.label)

        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.label_2 = QLabel(self.scrollAreaWidgetContents)
        self.label_2.setObjectName(u"label_2")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label_2)

        self.line_edit_file_name = QLineEdit(self.scrollAreaWidgetContents)
        self.line_edit_file_name.setObjectName(u"line_edit_file_name")
        self.line_edit_file_name.setReadOnly(True)

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.line_edit_file_name)

        self.label_4 = QLabel(self.scrollAreaWidgetContents)
        self.label_4.setObjectName(u"label_4")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label_4)

        self.line_edit_file_type = QLineEdit(self.scrollAreaWidgetContents)
        self.line_edit_file_type.setObjectName(u"line_edit_file_type")
        self.line_edit_file_type.setReadOnly(True)

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.line_edit_file_type)

        self.label_3 = QLabel(self.scrollAreaWidgetContents)
        self.label_3.setObjectName(u"label_3")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.label_3)

        self.dbl_spin_box_sampling_rate = QDoubleSpinBox(self.scrollAreaWidgetContents)
        self.dbl_spin_box_sampling_rate.setObjectName(u"dbl_spin_box_sampling_rate")
        self.dbl_spin_box_sampling_rate.setDecimals(1)
        self.dbl_spin_box_sampling_rate.setMaximum(100000.000000000000000)

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.dbl_spin_box_sampling_rate)

        self.label_5 = QLabel(self.scrollAreaWidgetContents)
        self.label_5.setObjectName(u"label_5")

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.label_5)

        self.combo_box_signal_column = QComboBox(self.scrollAreaWidgetContents)
        self.combo_box_signal_column.setObjectName(u"combo_box_signal_column")

        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.combo_box_signal_column)

        self.label_6 = QLabel(self.scrollAreaWidgetContents)
        self.label_6.setObjectName(u"label_6")

        self.formLayout.setWidget(4, QFormLayout.LabelRole, self.label_6)

        self.combo_box_info_column = QComboBox(self.scrollAreaWidgetContents)
        self.combo_box_info_column.setObjectName(u"combo_box_info_column")

        self.formLayout.setWidget(4, QFormLayout.FieldRole, self.combo_box_info_column)

        self.label_7 = QLabel(self.scrollAreaWidgetContents)
        self.label_7.setObjectName(u"label_7")

        self.formLayout.setWidget(5, QFormLayout.LabelRole, self.label_7)

        self.data_tree_widget_additional_info = DataTreeWidget(self.scrollAreaWidgetContents)
        __qtreewidgetitem = QTreeWidgetItem()
        __qtreewidgetitem.setText(0, u"1");
        self.data_tree_widget_additional_info.setHeaderItem(__qtreewidgetitem)
        self.data_tree_widget_additional_info.setObjectName(u"data_tree_widget_additional_info")
        self.data_tree_widget_additional_info.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.data_tree_widget_additional_info.setProperty("showDropIndicator", False)

        self.formLayout.setWidget(5, QFormLayout.FieldRole, self.data_tree_widget_additional_info)


        self.verticalLayout.addLayout(self.formLayout)

        self.label_8 = QLabel(self.scrollAreaWidgetContents)
        self.label_8.setObjectName(u"label_8")

        self.verticalLayout.addWidget(self.label_8)


        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.gridLayout.addWidget(self.scrollArea, 0, 0, 1, 1)

        self.buttonBox = QDialogButtonBox(MetadataDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)

#if QT_CONFIG(shortcut)
        self.label_2.setBuddy(self.line_edit_file_name)
        self.label_4.setBuddy(self.line_edit_file_type)
        self.label_3.setBuddy(self.dbl_spin_box_sampling_rate)
        self.label_5.setBuddy(self.combo_box_signal_column)
        self.label_6.setBuddy(self.combo_box_info_column)
        self.label_7.setBuddy(self.data_tree_widget_additional_info)
#endif // QT_CONFIG(shortcut)
        QWidget.setTabOrder(self.line_edit_file_name, self.line_edit_file_type)
        QWidget.setTabOrder(self.line_edit_file_type, self.dbl_spin_box_sampling_rate)
        QWidget.setTabOrder(self.dbl_spin_box_sampling_rate, self.combo_box_signal_column)
        QWidget.setTabOrder(self.combo_box_signal_column, self.combo_box_info_column)
        QWidget.setTabOrder(self.combo_box_info_column, self.data_tree_widget_additional_info)

        self.retranslateUi(MetadataDialog)
        self.buttonBox.accepted.connect(MetadataDialog.accept)
        self.buttonBox.rejected.connect(MetadataDialog.reject)

        QMetaObject.connectSlotsByName(MetadataDialog)
    # setupUi

    def retranslateUi(self, MetadataDialog):
        MetadataDialog.setWindowTitle(QCoreApplication.translate("MetadataDialog", u"Dialog", None))
        self.label.setText(QCoreApplication.translate("MetadataDialog", u"<html><head/><body><p><span style=\" font-size:14pt; font-weight:700;\">Metadata</span></p></body></html>", None))
        self.label_2.setText(QCoreApplication.translate("MetadataDialog", u"File Name", None))
        self.label_4.setText(QCoreApplication.translate("MetadataDialog", u"File Type", None))
        self.label_3.setText(QCoreApplication.translate("MetadataDialog", u"Sampling Rate*", None))
        self.dbl_spin_box_sampling_rate.setSuffix(QCoreApplication.translate("MetadataDialog", u" Hz", None))
        self.label_5.setText(QCoreApplication.translate("MetadataDialog", u"Signal Column / Channel*", None))
        self.label_6.setText(QCoreApplication.translate("MetadataDialog", u"Info Column / Channel", None))
        self.combo_box_info_column.setPlaceholderText(QCoreApplication.translate("MetadataDialog", u"None", None))
        self.label_7.setText(QCoreApplication.translate("MetadataDialog", u"Additional Info", None))
        self.label_8.setText(QCoreApplication.translate("MetadataDialog", u"*Field is required", None))
    # retranslateUi

