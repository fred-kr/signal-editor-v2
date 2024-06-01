from PySide6 import QtCore, QtWidgets

from signal_editor.ui.ui_dialog_metadata import Ui_MetadataDialog

from ..icons import FluentIcon


class MetadataDialog(QtWidgets.QDialog, Ui_MetadataDialog):
    sig_property_has_changed = QtCore.Signal(dict)

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setupUi(self)

        self.setWindowIcon(FluentIcon.BookInformation.icon())

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
        settings = QtCore.QSettings()
        settings.setValue(
            "Misc/last_signal_column_name", self.combo_box_signal_column.currentText()
        )
        settings.setValue("Misc/last_info_column_name", self.combo_box_info_column.currentText())
        settings.setValue("Data/sampling_rate", self.spin_box_sampling_rate.value())

        super().accept()
