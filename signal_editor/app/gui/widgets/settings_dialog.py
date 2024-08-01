from PySide6 import QtGui, QtWidgets
from qfluentwidgets import CommandBar

from ...models.config_tree_model import ConfigTreeModel
from ..icons import FluentIcon as FI
from .config_tree import ConfigTreeView


class ConfigDialog(QtWidgets.QDialog):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self.setWindowTitle("Settings")
        self.setWindowIcon(FI.Settings.icon())
        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        self.config_tree = ConfigTreeView(self)
        self.config_tree.setModel(ConfigTreeModel(self))

        toolbar = CommandBar(self)

        action_restore_defaults = QtGui.QAction(FI.TabDesktopArrowClockwise.icon(), "Restore Defaults", self)
        action_restore_defaults.triggered.connect(self.config_tree.restore_defaults)

        action_reset_selected = QtGui.QAction(FI.ArrowReset.icon(), "Reset Selected", self)
        action_reset_selected.triggered.connect(self.config_tree.reset_current_item)

        toolbar.addAction(action_restore_defaults)
        toolbar.addAction(action_reset_selected)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(self.config_tree)
        layout.addWidget(buttons)

        self.setLayout(layout)

        self.config_tree.expandAll()

        for col in range(self.config_tree.model().columnCount()):
            self.config_tree.resizeColumnToContents(col)
