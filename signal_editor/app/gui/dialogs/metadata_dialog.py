from PySide6 import QtCore, QtWidgets

from signal_editor.ui.ui_dialog_metadata import Ui_MetadataDialog

from ...config import Config
from ..icons import SignalEditorIcons as Icons

STYLE_SHEET = """
SpinBox[requiresInput="false"] {
    border: 2px solid mediumseagreen;
    border-radius: 5px;
}
SpinBox[requiresInput="false"]:focus {
    border: 2px solid mediumseagreen;
    border-radius: 5px;
}

SpinBox[requiresInput="true"] {
    border: 2px solid red;
    border-radius: 5px;
}
SpinBox[requiresInput="true"]:focus {
    border: 2px solid red;
    border-radius: 5px;
}
"""

CB_STYLE_SHEET = """
ComboBox[requiresInput="false"] {
    border: 2px solid mediumseagreen;
    border-radius: 5px;
    padding: 5px 31px 6px 11px;
    /* font: 14px 'Segoe UI', 'Microsoft YaHei', 'PingFang SC'; */
    color: black;
    background-color: rgba(255, 255, 255, 0.7);
    text-align: left;
    outline: none;
}
ComboBox[requiresInput="true"] {
    border: 2px solid crimson;
    border-radius: 5px;
    padding: 5px 31px 6px 11px;
    /* font: 14px 'Segoe UI', 'Microsoft YaHei', 'PingFang SC'; */
    color: black;
    background-color: rgba(255, 255, 255, 0.7);
    text-align: left;
    outline: none;
}

ComboBox[requiresInput="false"]:hover {
    border: 2px solid mediumseagreen;
    border-radius: 5px;
    background-color: rgba(249, 249, 249, 0.5);
}
ComboBox[requiresInput="true"]:hover {
    border: 2px solid crimson;
    border-radius: 5px;
    background-color: rgba(249, 249, 249, 0.5);
}

ComboBox[requiresInput="false"]:pressed {
    border: 2px solid mediumseagreen;
    border-radius: 5px;
    background-color: rgba(249, 249, 249, 0.3);
    color: rgba(0, 0, 0, 0.63);
}
ComboBox[requiresInput="true"]:pressed {
    border: 2px solid crimson;
    border-radius: 5px;
    background-color: rgba(249, 249, 249, 0.3);
    color: rgba(0, 0, 0, 0.63);
}

ComboBox:disabled {
    color: rgba(0, 0, 0, 0.36);
    background: rgba(249, 249, 249, 0.3);
    border: 1px solid rgba(0, 0, 0, 0.06);
}

ComboBox {
    color: rgba(0, 0, 0, 0.6063);
}
"""


class MetadataDialog(QtWidgets.QDialog, Ui_MetadataDialog):
    sig_property_has_changed = QtCore.Signal(dict)

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self.setupUi(self)

        self.combo_box_signal_column.setStyleSheet(CB_STYLE_SHEET)
        self.spin_box_sampling_rate.setStyleSheet(STYLE_SHEET)
        self.setWindowIcon(Icons.SignalEditor.icon())
        self.btn_accept.clicked.connect(self.accept)
        self.btn_reject.clicked.connect(self.reject)

    @QtCore.Slot()
    def accept(self) -> None:
        metadata_dict: dict[str, int | str] = {
            "sampling_rate": self.spin_box_sampling_rate.value(),
            "signal_column": self.combo_box_signal_column.currentText(),
            "info_column": self.combo_box_info_column.currentText(),
        }
        self.sig_property_has_changed.emit(metadata_dict)
        config = Config()
        config.internal.last_signal_column = self.combo_box_signal_column.currentText()
        config.internal.last_info_column = self.combo_box_info_column.currentText()
        config.internal.last_sampling_rate = self.spin_box_sampling_rate.value()

        super().accept()
