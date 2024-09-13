import typing as t
import sys
from PySide6 import QtCore, QtGui, QtWidgets


class TreeComboBox(QtWidgets.QComboBox):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self._model = QtGui.QStandardItemModel(self)
        self._view = QtWidgets.QTreeView(self)
        self._view.setHeaderHidden(True)
        self._view.setRootIsDecorated(False)
        
        self.setModel(self._model)
        self.setView(self._view)
        self.setItemDelegate(ComboBoxDelegate(self))

    def add_separator(self) -> None:
        self.insertSeparator(self.count())
        
    def add_parent_item(self, text: str) -> None:
        item = QtGui.QStandardItem(text)
        item.setFlags(item.flags() & ~(QtCore.Qt.ItemFlag.ItemIsEnabled | QtCore.Qt.ItemFlag.ItemIsSelectable))
        item.setData("parent", QtCore.Qt.ItemDataRole.AccessibleDescriptionRole)

        font = item.font()
        font.setBold(True)
        item.setFont(font)

        self._model.appendRow(item)

    def add_child_item(self, text: str, data: t.Any) -> None:
        item = QtGui.QStandardItem(f"  {text}")
        item.setData(data, QtCore.Qt.ItemDataRole.UserRole)
        item.setData("child", QtCore.Qt.ItemDataRole.AccessibleDescriptionRole)

        self._model.appendRow(item)

class ComboBoxDelegate(QtWidgets.QStyledItemDelegate):
    def sizeHint(self, option: QtWidgets.QStyleOptionViewItem, index: QtCore.QModelIndex | QtCore.QPersistentModelIndex) -> QtCore.QSize:
        typ_ = str(index.data(QtCore.Qt.ItemDataRole.AccessibleDescriptionRole))
        if typ_ == "separator":
            return QtCore.QSize(5, 5)
        return super().sizeHint(option, index)

    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionViewItem, index: QtCore.QModelIndex | QtCore.QPersistentModelIndex) -> None:
        typ_ = str(index.data(QtCore.Qt.ItemDataRole.AccessibleDescriptionRole))
        # option = QtWidgets.QStyleOptionViewItem(option)
        if typ_ == "separator":
            super().paint(painter, option, index)
            y = (option.rect.top() + option.rect.bottom()) // 2
            painter.setPen(option.palette.color(QtGui.QPalette.ColorGroup.Active, QtGui.QPalette.ColorRole.Dark))
            painter.drawLine(option.rect.left(), y, option.rect.right(), y)
        elif typ_ == "parent":
            parent_option = option
            parent_option.state |= QtWidgets.QStyle.StateFlag.State_Enabled
            super().paint(painter, parent_option, index)
        elif typ_ == "child":
            child_option = option
            indent = QtGui.QFontMetrics("    ").maxWidth()
            child_option.rect.adjust(indent, 0, 0, 0)
            child_option.textElideMode = QtCore.Qt.TextElideMode.ElideNone
            super().paint(painter, child_option, index)
        else:
            super().paint(painter, option, index)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.combo = TreeComboBox(self)
        self.setCentralWidget(self.combo)
        self.combo.clear()

        self.combo.add_parent_item("Parent 1")
        self.combo.add_child_item("Child 1", "data1")
        self.combo.add_child_item("Child 2", "data2")
        self.combo.add_separator()
        self.combo.add_parent_item("Parent 2")
        self.combo.add_child_item("Child 3", "data3")
        self.combo.add_child_item("Child 4", "data4")
        self.combo.add_separator()
        self.combo.add_parent_item("Parent 3")
        self.combo.add_child_item("Child 5", "data5")
        self.combo.add_child_item("Child 6", "data6")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
    