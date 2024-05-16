# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'dialog_export_result.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QComboBox, QDialog,
    QDialogButtonBox, QFrame, QGridLayout, QLabel,
    QLineEdit, QPushButton, QSizePolicy, QWidget)

from superqt import (QCollapsible, QEnumComboBox)

class Ui_ExportDialog(object):
    def setupUi(self, ExportDialog):
        if not ExportDialog.objectName():
            ExportDialog.setObjectName(u"ExportDialog")
        ExportDialog.resize(554, 340)
        self.gridLayout = QGridLayout(ExportDialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.line_edit_output_dir = QLineEdit(ExportDialog)
        self.line_edit_output_dir.setObjectName(u"line_edit_output_dir")
        self.line_edit_output_dir.setMinimumSize(QSize(0, 31))
        self.line_edit_output_dir.setClearButtonEnabled(True)

        self.gridLayout.addWidget(self.line_edit_output_dir, 1, 1, 1, 3)

        self.label = QLabel(ExportDialog)
        self.label.setObjectName(u"label")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.label, 0, 0, 1, 2)

        self.enum_combo_export_format = QEnumComboBox(ExportDialog)
        self.enum_combo_export_format.setObjectName(u"enum_combo_export_format")
        self.enum_combo_export_format.setMinimumSize(QSize(0, 31))

        self.gridLayout.addWidget(self.enum_combo_export_format, 3, 3, 1, 1)

        self.label_2 = QLabel(ExportDialog)
        self.label_2.setObjectName(u"label_2")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy1)
        self.label_2.setMinimumSize(QSize(0, 31))

        self.gridLayout.addWidget(self.label_2, 3, 0, 1, 1)

        self.label_3 = QLabel(ExportDialog)
        self.label_3.setObjectName(u"label_3")
        sizePolicy1.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy1)
        self.label_3.setMinimumSize(QSize(0, 31))

        self.gridLayout.addWidget(self.label_3, 3, 2, 1, 1)

        self.combo_box_result_type = QComboBox(ExportDialog)
        self.combo_box_result_type.addItem("")
        self.combo_box_result_type.addItem("")
        self.combo_box_result_type.setObjectName(u"combo_box_result_type")
        self.combo_box_result_type.setMinimumSize(QSize(0, 31))

        self.gridLayout.addWidget(self.combo_box_result_type, 3, 1, 1, 1)

        self.btn_browse_output_dir = QPushButton(ExportDialog)
        self.btn_browse_output_dir.setObjectName(u"btn_browse_output_dir")
        sizePolicy.setHeightForWidth(self.btn_browse_output_dir.sizePolicy().hasHeightForWidth())
        self.btn_browse_output_dir.setSizePolicy(sizePolicy)
        self.btn_browse_output_dir.setMinimumSize(QSize(0, 31))

        self.gridLayout.addWidget(self.btn_browse_output_dir, 1, 0, 1, 1)

        self.collapsible_extra_metadata = QCollapsible(ExportDialog)
        self.collapsible_extra_metadata.setObjectName(u"collapsible_extra_metadata")
        self.collapsible_extra_metadata.setFrameShape(QFrame.Shape.StyledPanel)
        self.collapsible_extra_metadata.setFrameShadow(QFrame.Shadow.Raised)

        self.gridLayout.addWidget(self.collapsible_extra_metadata, 4, 0, 1, 4)

        self.label_4 = QLabel(ExportDialog)
        self.label_4.setObjectName(u"label_4")
        sizePolicy1.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy1)
        self.label_4.setMinimumSize(QSize(0, 31))

        self.gridLayout.addWidget(self.label_4, 2, 0, 1, 1)

        self.line_edit_output_file_name = QLineEdit(ExportDialog)
        self.line_edit_output_file_name.setObjectName(u"line_edit_output_file_name")
        self.line_edit_output_file_name.setMinimumSize(QSize(0, 31))
        self.line_edit_output_file_name.setClearButtonEnabled(True)

        self.gridLayout.addWidget(self.line_edit_output_file_name, 2, 1, 1, 3)

        self.buttonBox = QDialogButtonBox(ExportDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Save)
        self.buttonBox.setCenterButtons(False)

        self.gridLayout.addWidget(self.buttonBox, 5, 0, 1, 4)


        self.retranslateUi(ExportDialog)
        self.buttonBox.accepted.connect(ExportDialog.accept)
        self.buttonBox.rejected.connect(ExportDialog.reject)

        QMetaObject.connectSlotsByName(ExportDialog)
    # setupUi

    def retranslateUi(self, ExportDialog):
        ExportDialog.setWindowTitle(QCoreApplication.translate("ExportDialog", u"Dialog", None))
        self.line_edit_output_dir.setPlaceholderText(QCoreApplication.translate("ExportDialog", u"Select output directory for exported file", None))
        self.label.setText(QCoreApplication.translate("ExportDialog", u"<html><head/><body><p><span style=\" font-size:11pt; font-weight:700;\">Select output location:</span></p></body></html>", None))
        self.label_2.setText(QCoreApplication.translate("ExportDialog", u"Result type:", None))
        self.label_3.setText(QCoreApplication.translate("ExportDialog", u"Output format:", None))
        self.combo_box_result_type.setItemText(0, QCoreApplication.translate("ExportDialog", u"Compact", None))
        self.combo_box_result_type.setItemText(1, QCoreApplication.translate("ExportDialog", u"Detailed", None))

        self.btn_browse_output_dir.setText(QCoreApplication.translate("ExportDialog", u"Browse", None))
        self.label_4.setText(QCoreApplication.translate("ExportDialog", u"File Name:", None))
        self.line_edit_output_file_name.setPlaceholderText(QCoreApplication.translate("ExportDialog", u"Choose a name for the exported file", None))
    # retranslateUi

