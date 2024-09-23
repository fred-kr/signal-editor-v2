from PySide6 import QtWidgets

from ... import type_defs as _t
from . import DataTreeWidgetContainer


class SectionSummaryBox(QtWidgets.QDialog):
    def __init__(self, title: str, summary: _t.SectionSummaryDict, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        summary_tree = DataTreeWidgetContainer(allow_edit=False)
        summary_tree.set_data(dict(summary), hide_root=True)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(summary_tree)

        self.setLayout(layout)

        self.setWindowTitle(title)

        self.resize(600, 400)
