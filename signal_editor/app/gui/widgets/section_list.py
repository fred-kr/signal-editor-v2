import typing as t

import qfluentwidgets as qfw
from PySide6 import QtCore, QtGui, QtWidgets


class SectionListView(qfw.ListView):
    sig_delete_current_item: t.ClassVar[QtCore.Signal] = QtCore.Signal(QtCore.QModelIndex)

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setUniformItemSizes(True)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.setSelectionRectVisible(True)
        self.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)

        self.action_delete_selected = QtGui.QAction("Delete Selected", self)
        self.action_delete_selected.triggered.connect(self.emit_delete_current_request)
        self.customContextMenuRequested.connect(self.show_context_menu)

    @QtCore.Slot(QtCore.QPoint)
    def show_context_menu(self, point: QtCore.QPoint) -> None:
        menu = QtWidgets.QMenu(self)
        selected_is_base = self.currentIndex().row() == 0
        self.action_delete_selected.setEnabled(not selected_is_base)
        menu.addAction(self.action_delete_selected)
        menu.exec(self.mapToGlobal(point))

    @QtCore.Slot()
    def emit_delete_current_request(self) -> None:
        index = self.currentIndex()
        self.sig_delete_current_item.emit(index)


class SectionListDock(QtWidgets.QDockWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setVisible(False)
        self.setObjectName("SectionListDock")
        self.setWindowTitle("Section List")
        self.list_view = SectionListView()
        self.toggleViewAction().setIcon(QtGui.QIcon(":/icons/list_view"))
        main_widget = QtWidgets.QWidget(self)
        main_layout = QtWidgets.QVBoxLayout(main_widget)

        label_active_section = QtWidgets.QLabel("Active Section: ", main_widget)
        label_active_section.setFont(QtGui.QFont("Segoe UI", 12, QtGui.QFont.Weight.Bold))
        main_layout.addWidget(label_active_section)
        self.label_active_section = label_active_section

        confirm_cancel_btns = QtWidgets.QWidget()
        confirm_cancel_layout = QtWidgets.QHBoxLayout(confirm_cancel_btns)
        confirm_cancel_layout.setContentsMargins(0, 0, 0, 0)

        confirm_btn = QtWidgets.QPushButton()
        confirm_btn.setMinimumHeight(31)
        confirm_btn.setText("Confirm")
        confirm_btn.setIcon(QtGui.QIcon(":/icons/tick_button"))
        confirm_cancel_layout.addWidget(confirm_btn)
        self.btn_confirm = confirm_btn

        cancel_btn = QtWidgets.QPushButton()
        cancel_btn.setMinimumHeight(31)
        cancel_btn.setText("Cancel")
        cancel_btn.setIcon(QtGui.QIcon(":/icons/cross"))
        confirm_cancel_layout.addWidget(cancel_btn)
        self.btn_cancel = cancel_btn

        self.btn_container = confirm_cancel_btns
        confirm_cancel_btns.setLayout(confirm_cancel_layout)
        main_layout.addWidget(confirm_cancel_btns)

        main_layout.addWidget(self.list_view)
        self.main_layout = main_layout

        self.setWidget(main_widget)
