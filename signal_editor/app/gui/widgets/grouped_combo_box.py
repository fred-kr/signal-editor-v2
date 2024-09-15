import enum
import sys
import typing as t

from PySide6 import QtCore, QtGui, QtWidgets

ItemTypeRole = QtCore.Qt.ItemDataRole.UserRole + 1


class ItemType(enum.Enum):
    SEPARATOR = enum.auto()
    PARENT = enum.auto()
    CHILD = enum.auto()


class GroupedComboBox(QtWidgets.QComboBox):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)

        self._model = QtGui.QStandardItemModel(self)
        self._view = QtWidgets.QTreeView(self)
        self._view.setHeaderHidden(True)
        self._view.setRootIsDecorated(False)

        self.setModel(self._model)
        self.setView(self._view)
        self.setItemDelegate(GroupedComboBoxDelegate(self))

    def add_separator(self) -> None:
        item = QtGui.QStandardItem()
        item.setFlags(QtCore.Qt.ItemFlag.NoItemFlags)
        item.setData(ItemType.SEPARATOR, ItemTypeRole)
        self._model.appendRow(item)

    def add_parent_item(self, text: str) -> None:
        item = QtGui.QStandardItem(text)
        flags = item.flags()
        flags &= ~QtCore.Qt.ItemFlag.ItemIsSelectable
        item.setFlags(flags)
        item.setData(ItemType.PARENT, ItemTypeRole)

        font = item.font()
        font.setBold(True)
        item.setFont(font)

        self._model.appendRow(item)

    def add_child_item(self, text: str, data: t.Any) -> None:
        item = QtGui.QStandardItem(text)
        item.setData(data, QtCore.Qt.ItemDataRole.UserRole)
        item.setData(ItemType.CHILD, ItemTypeRole)

        self._model.appendRow(item)

    def currentData(self, role: int = QtCore.Qt.ItemDataRole.UserRole) -> t.Any:
        index = self.currentIndex()
        if index >= 0:
            item = self._model.item(index)
            if item.data(ItemTypeRole) == ItemType.CHILD:
                return item.data(QtCore.Qt.ItemDataRole.UserRole)

        return None


class GroupedComboBoxDelegate(QtWidgets.QStyledItemDelegate):
    def sizeHint(
        self, option: QtWidgets.QStyleOptionViewItem, index: QtCore.QModelIndex | QtCore.QPersistentModelIndex
    ) -> QtCore.QSize:
        item_type = index.data(ItemTypeRole)
        if item_type == ItemType.SEPARATOR:
            return QtCore.QSize(0, 5)
        else:
            return super().sizeHint(option, index)

    def paint(
        self,
        painter: QtGui.QPainter,
        option: QtWidgets.QStyleOptionViewItem,
        index: QtCore.QModelIndex | QtCore.QPersistentModelIndex,
    ) -> None:
        item_type = index.data(ItemTypeRole)
        if item_type == ItemType.SEPARATOR:
            y = (option.rect.top() + option.rect.bottom()) // 2
            painter.setPen(option.palette.color(QtGui.QPalette.ColorGroup.Active, QtGui.QPalette.ColorRole.Dark))
            painter.drawLine(option.rect.left(), y, option.rect.right(), y)
        elif item_type == ItemType.PARENT:
            painter.save()
            painter.fillRect(option.rect, option.palette.midlight())
            option.font.setBold(True)
            option.state &= ~QtWidgets.QStyle.StateFlag.State_Selected
            super().paint(painter, option, index)
            painter.restore()
        elif item_type == ItemType.CHILD:
            indent = 20  # Pixels to indent child items
            option.rect.adjust(indent, 0, 0, 0)
            super().paint(painter, option, index)
        else:
            super().paint(painter, option, index)

    def editorEvent(
        self,
        event: QtCore.QEvent,
        model: QtCore.QAbstractItemModel,
        option: QtWidgets.QStyleOptionViewItem,
        index: QtCore.QModelIndex | QtCore.QPersistentModelIndex,
    ) -> bool:
        item_type = index.data(ItemTypeRole)
        if item_type != ItemType.CHILD:
            return False  # Prevent selection of non-child items

        return super().editorEvent(event, model, option, index)


class Window(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.combo = GroupedComboBox(self)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.combo)

        self.setLayout(layout)
        self.combo.clear()

        self.combo.add_parent_item("PPG")
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
    win = Window()
    win.show()
    sys.exit(app.exec())
