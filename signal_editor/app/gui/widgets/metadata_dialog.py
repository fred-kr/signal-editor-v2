from PySide6 import QtCore, QtWidgets

from signal_editor.ui.ui_dialog_metadata import Ui_MetadataDialog

from ..icons import FluentIcon
from ...config import Config


class MetadataDialog(QtWidgets.QDialog, Ui_MetadataDialog):
    sig_property_has_changed = QtCore.Signal(dict)

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setupUi(self)

        self.setWindowIcon(FluentIcon.BookInformation.icon())
        self.btn_accept.clicked.connect(self.accept)
        self.btn_reject.clicked.connect(self.reject)
        
    @QtCore.Slot()
    def accept(self) -> None:
        metadata_dict = {
            "sampling_rate": self.spin_box_sampling_rate.value(),
            "signal_column": self.combo_box_signal_column.currentText(),
            "info_column": self.combo_box_info_column.currentText(),
            "signal_column_index": self.combo_box_signal_column.currentIndex(),
            "info_column_index": self.combo_box_info_column.currentIndex(),
        }
        self.sig_property_has_changed.emit(metadata_dict)
        config = Config()
        config.internal.LastSignalColumn = self.combo_box_signal_column.currentText()
        config.internal.LastInfoColumn = self.combo_box_info_column.currentText()
        config.internal.LastSamplingRate = self.spin_box_sampling_rate.value()
        config.save()

        super().accept()
