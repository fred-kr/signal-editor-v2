from PySide6 import QtCore, QtGui, QtWidgets
from qfluentwidgets import CommandBar

from ...models.config_model import ConfigModel
from ..icons import SignalEditorIcon as Icons
from ..widgets.config_tree import ConfigTreeView


class ConfigDialog(QtWidgets.QDialog):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self.setWindowTitle("Settings")
        self.setWindowIcon(Icons.app_icon())
        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        self.config_tree = ConfigTreeView(self)
        self.config_tree.setModel(ConfigModel(self))

        toolbar = CommandBar(self)
        toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

        action_restore_defaults = QtGui.QAction(Icons.TabDesktopArrowClockwise.icon(), "Restore Defaults", self)
        action_restore_defaults.triggered.connect(self.config_tree.restore_defaults)

        action_reset_selected = QtGui.QAction(Icons.ArrowReset.icon(), "Reset Selected", self)
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
