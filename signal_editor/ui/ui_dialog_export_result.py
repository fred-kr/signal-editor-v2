# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'dialog_export_result.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QFrame, QGridLayout,
    QSizePolicy, QSpacerItem, QWidget)

from qfluentwidgets import (BodyLabel, ComboBox, LineEdit, PushButton,
    SubtitleLabel)
from ..app.gui.widgets.collapsible_frame import CollapsibleFrame
from . import resources_rc

class Ui_ExportDialog(object):
    def setupUi(self, ExportDialog):
        if not ExportDialog.objectName():
            ExportDialog.setObjectName(u"ExportDialog")
        ExportDialog.resize(553, 340)
        icon = QIcon()
        icon.addFile(u":/icons/app_icon.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        ExportDialog.setWindowIcon(icon)
        self.gridLayout = QGridLayout(ExportDialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.label_5 = SubtitleLabel(ExportDialog)
        self.label_5.setObjectName(u"label_5")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.label_5, 0, 0, 1, 6)

        self.btn_browse_output_dir = PushButton(ExportDialog)
        self.btn_browse_output_dir.setObjectName(u"btn_browse_output_dir")
        sizePolicy.setHeightForWidth(self.btn_browse_output_dir.sizePolicy().hasHeightForWidth())
        self.btn_browse_output_dir.setSizePolicy(sizePolicy)
        self.btn_browse_output_dir.setMinimumSize(QSize(0, 31))

        self.gridLayout.addWidget(self.btn_browse_output_dir, 1, 0, 1, 1)

        self.line_edit_output_dir = LineEdit(ExportDialog)
        self.line_edit_output_dir.setObjectName(u"line_edit_output_dir")
        self.line_edit_output_dir.setMinimumSize(QSize(0, 31))
        self.line_edit_output_dir.setFrame(False)
        self.line_edit_output_dir.setClearButtonEnabled(True)

        self.gridLayout.addWidget(self.line_edit_output_dir, 1, 1, 1, 5)

        self.label_4 = BodyLabel(ExportDialog)
        self.label_4.setObjectName(u"label_4")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy1)
        self.label_4.setMinimumSize(QSize(0, 31))

        self.gridLayout.addWidget(self.label_4, 2, 0, 1, 1)

        self.line_edit_output_file_name = LineEdit(ExportDialog)
        self.line_edit_output_file_name.setObjectName(u"line_edit_output_file_name")
        self.line_edit_output_file_name.setMinimumSize(QSize(0, 31))
        self.line_edit_output_file_name.setFrame(False)
        self.line_edit_output_file_name.setClearButtonEnabled(True)

        self.gridLayout.addWidget(self.line_edit_output_file_name, 2, 1, 1, 5)

        self.label_2 = BodyLabel(ExportDialog)
        self.label_2.setObjectName(u"label_2")
        sizePolicy1.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy1)
        self.label_2.setMinimumSize(QSize(0, 31))

        self.gridLayout.addWidget(self.label_2, 3, 0, 1, 1)

        self.collapsible_extra_metadata = CollapsibleFrame(ExportDialog)
        self.collapsible_extra_metadata.setObjectName(u"collapsible_extra_metadata")
        self.collapsible_extra_metadata.setFrameShape(QFrame.Shape.StyledPanel)
        self.collapsible_extra_metadata.setFrameShadow(QFrame.Shadow.Raised)

        self.gridLayout.addWidget(self.collapsible_extra_metadata, 4, 0, 1, 6)

        self.horizontalSpacer = QSpacerItem(348, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer, 5, 0, 1, 4)

        self.btn_accept = PushButton(ExportDialog)
        self.btn_accept.setObjectName(u"btn_accept")

        self.gridLayout.addWidget(self.btn_accept, 5, 4, 1, 1)

        self.btn_reject = PushButton(ExportDialog)
        self.btn_reject.setObjectName(u"btn_reject")

        self.gridLayout.addWidget(self.btn_reject, 5, 5, 1, 1)

        self.combo_box_export_format = ComboBox(ExportDialog)
        self.combo_box_export_format.setObjectName(u"combo_box_export_format")
        self.combo_box_export_format.setMinimumSize(QSize(0, 31))

        self.gridLayout.addWidget(self.combo_box_export_format, 3, 4, 1, 2)

        self.label_3 = BodyLabel(ExportDialog)
        self.label_3.setObjectName(u"label_3")
        sizePolicy1.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy1)
        self.label_3.setMinimumSize(QSize(0, 31))

        self.gridLayout.addWidget(self.label_3, 3, 3, 1, 1)

        self.combo_box_result_type = ComboBox(ExportDialog)
        self.combo_box_result_type.setObjectName(u"combo_box_result_type")
        self.combo_box_result_type.setMinimumSize(QSize(0, 31))

        self.gridLayout.addWidget(self.combo_box_result_type, 3, 1, 1, 2)


        self.retranslateUi(ExportDialog)

        QMetaObject.connectSlotsByName(ExportDialog)
    # setupUi

    def retranslateUi(self, ExportDialog):
        ExportDialog.setWindowTitle(QCoreApplication.translate("ExportDialog", u"Export Results", None))
        self.label_5.setText(QCoreApplication.translate("ExportDialog", u"Export Results", None))
        self.btn_browse_output_dir.setText(QCoreApplication.translate("ExportDialog", u"Browse", None))
        self.line_edit_output_dir.setPlaceholderText(QCoreApplication.translate("ExportDialog", u"Select output directory for exported file", None))
        self.label_4.setText(QCoreApplication.translate("ExportDialog", u"File Name:", None))
        self.line_edit_output_file_name.setPlaceholderText(QCoreApplication.translate("ExportDialog", u"Choose a name for the exported file", None))
        self.label_2.setText(QCoreApplication.translate("ExportDialog", u"Result type:", None))
        self.btn_accept.setText(QCoreApplication.translate("ExportDialog", u"Save", None))
        self.btn_reject.setText(QCoreApplication.translate("ExportDialog", u"Cancel", None))
        self.combo_box_export_format.setText("")
        self.label_3.setText(QCoreApplication.translate("ExportDialog", u"Output format:", None))
        self.combo_box_result_type.setText("")
    # retranslateUi

