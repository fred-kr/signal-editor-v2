import typing as t
from pathlib import Path

from loguru import logger
from PySide6 import QtCore, QtGui, QtWidgets

from ...enum_defs import ExportFormatCompact, ExportFormatDetailed
from ...config import Config
from signal_editor.ui.ui_dialog_export_result import Ui_ExportDialog


class ExportDialog(QtWidgets.QDialog, Ui_ExportDialog):
    sig_export_confirmed: t.ClassVar[QtCore.Signal] = QtCore.Signal(dict)

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Export Results")
        self.setWindowIcon(QtGui.QIcon(":/icons/file_export"))
        self.setModal(True)

        self._initialize_widgets()
        self._connect_signals()
        self._update_export_format("Detailed")

    def _initialize_widgets(self) -> None:
        self.collapsible_extra_metadata.setText("Additional Details")

        widget = QtWidgets.QWidget()
        detail_form = QtWidgets.QFormLayout(widget)
        detail_form.setRowWrapPolicy(QtWidgets.QFormLayout.RowWrapPolicy.WrapAllRows)
        meas_date = QtWidgets.QLineEdit()
        meas_date.setPlaceholderText("YYYY-MM-DD")
        meas_date.setInputMethodHints(QtCore.Qt.InputMethodHint.ImhDate)
        detail_form.addRow("Date of Measurement", meas_date)
        subject_id = QtWidgets.QLineEdit()
        subject_id.setPlaceholderText("Subject ID")
        detail_form.addRow("Subject ID", subject_id)
        oxy_cond = QtWidgets.QComboBox()
        oxy_cond.addItems(["-", "Normoxia", "Hypoxia"])
        detail_form.addRow("Oxygen Condition", oxy_cond)

        self.meas_date = meas_date
        self.subject_id = subject_id
        self.oxy_cond = oxy_cond

        self.collapsible_extra_metadata.setContent(widget)

    def _connect_signals(self) -> None:
        self.combo_box_result_type.currentTextChanged.connect(self._update_export_format)
        self.btn_browse_output_dir.clicked.connect(self._browse_output_dir)

    @QtCore.Slot(str)
    def _update_export_format(self, result_type: str) -> None:
        if result_type == "Compact":
            self.enum_combo_export_format.setEnumClass(ExportFormatCompact)
            self.collapsible_extra_metadata.collapse()
            self.collapsible_extra_metadata.setLocked(True)
        elif result_type == "Detailed":
            self.enum_combo_export_format.setEnumClass(ExportFormatDetailed)
            self.collapsible_extra_metadata.setLocked(False)
            self.collapsible_extra_metadata.expand()

    @QtCore.Slot()
    def _browse_output_dir(self) -> None:
        prev_dir = Config().internal.OutputDir
        if output_dir := QtWidgets.QFileDialog.getExistingDirectory(self, "Select Output Directory", prev_dir):
            self.line_edit_output_dir.setText(output_dir)

    @QtCore.Slot()
    def accept(self) -> None:
        output_dir = self.line_edit_output_dir.text()
        if not output_dir:
            logger.warning("No output directory selected.")
            return

        output_file = self.line_edit_output_file_name.text()
        if not output_file:
            logger.warning("No output file name specified.")
            return

        output_type = self.combo_box_result_type.currentText()
        export_format = (
            ExportFormatCompact(self.enum_combo_export_format.currentEnum())
            if output_type == "Compact"
            else ExportFormatDetailed(self.enum_combo_export_format.currentEnum())
        )
        suffix = export_format.value

        subject_id = self.subject_id.text()
        measured_date = self.meas_date.text()
        oxygen_condition = self.oxy_cond.currentText()
        if not subject_id:
            subject_id = None
        if not measured_date:
            measured_date = None
        if oxygen_condition == "-":
            oxygen_condition = None

        out_path = Path(output_dir) / Path(output_file).with_suffix(suffix)
        info = {
            "out_path": out_path,
            "subject_id": subject_id,
            "measured_date": measured_date,
            "oxygen_condition": oxygen_condition,
        }
        self.sig_export_confirmed.emit(info)
        super().accept()
