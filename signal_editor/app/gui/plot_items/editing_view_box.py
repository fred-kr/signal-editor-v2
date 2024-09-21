import typing as t

import numpy as np
import numpy.typing as npt
import pyqtgraph as pg
from pyqtgraph.Point import Point
from PySide6 import QtCore, QtGui, QtWidgets

from ...enum_defs import MouseButtons

if t.TYPE_CHECKING:
    from pyqtgraph.GraphicsScene import mouseEvents


def _get_button_type(ev: "mouseEvents.MouseDragEvent") -> MouseButtons:
    if ev.button() == QtCore.Qt.MouseButton.MiddleButton:
        return MouseButtons.MiddleButton
    elif ev.button() == QtCore.Qt.MouseButton.LeftButton:
        if ev.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier:
            return MouseButtons.LeftButtonWithControl
        else:
            return MouseButtons.LeftButton
    elif ev.button() == QtCore.Qt.MouseButton.RightButton:
        return MouseButtons.RightButton
    else:
        return MouseButtons.Unknown


class EditingViewBox(pg.ViewBox):
    """
    Custom `pyqtgraph.ViewBox` subclass that adds some features for enhanced editing.
    """

    def __init__(self, *args: t.Any, **kargs: t.Any) -> None:
        super().__init__(*args, **kargs)
        self._selection_box: QtWidgets.QGraphicsRectItem | None = None
        self.mapped_selection_rect: QtCore.QRectF | None = None

    @property
    def selection_box(self) -> QtWidgets.QGraphicsRectItem:
        if self._selection_box is None:
            selection_box = QtWidgets.QGraphicsRectItem(0, 0, 1, 1)
            selection_box.setPen(pg.mkPen(color=(255, 165, 0, 255)))
            selection_box.setBrush(pg.mkBrush((255, 165, 0, 100)))
            selection_box.setZValue(1e9)
            selection_box.hide()
            self._selection_box = selection_box
            self.addItem(selection_box, ignoreBounds=True)
        return self._selection_box

    @selection_box.setter
    def selection_box(self, selection_box: QtWidgets.QGraphicsRectItem | None) -> None:
        if self._selection_box is not None:
            self.removeItem(self._selection_box)
        self._selection_box = selection_box
        if selection_box is None:
            return
        selection_box.setZValue(1e9)
        selection_box.hide()
        self.addItem(selection_box, ignoreBounds=True)
        return

    def mouseDragEvent(self, ev: "mouseEvents.MouseDragEvent", axis: int | float | None = None) -> None:
        ev.accept()

        pos = ev.pos()
        last_pos = ev.lastPos()
        dif: Point = (pos - last_pos) * np.array([-1, -1])

        mouse_enabled = np.array(self.state["mouseEnabled"], dtype=np.float64)
        mask = mouse_enabled.copy()
        if axis is not None:
            mask[1 - axis] = 0.0

        button_type = _get_button_type(ev)

        if button_type in {MouseButtons.MiddleButton, MouseButtons.LeftButtonWithControl}:
            if ev.isFinish():
                r = QtCore.QRectF(ev.pos(), ev.buttonDownPos())
                self.mapped_selection_rect = self.mapToView(r).boundingRect()
            else:
                self.updateSelectionBox(ev.pos(), ev.buttonDownPos())
                self.mapped_selection_rect = None
        elif button_type == MouseButtons.LeftButton:
            if self.state["mouseMode"] == pg.ViewBox.RectMode and axis is None:
                if ev.isFinish():
                    self._on_left_mouse_drag_finished(ev, pos)
                else:
                    self.updateScaleBox(ev.buttonDownPos(), ev.pos())
            else:
                self._on_left_mouse_drag(dif, mask)
        elif button_type == MouseButtons.RightButton:
            self._on_right_mouse_drag(mask, ev, mouse_enabled)

    def _on_right_mouse_drag(
        self,
        mask: npt.NDArray[np.float64],
        ev: "mouseEvents.MouseDragEvent",
        mouse_enabled: npt.NDArray[np.float64],
    ) -> None:
        if self.state["aspectLocked"] is not False:
            mask[0] = 0

        dif = np.array(
            [
                -(ev.screenPos().x() - ev.lastScreenPos().x()),
                ev.screenPos().y() - ev.lastScreenPos().y(),
            ]
        )
        s = ((mask * 0.02) + 1) ** dif

        tr = pg.invertQTransform(self.childGroup.transform())

        x = s[0] if mouse_enabled[0] == 1 else None
        y = s[1] if mouse_enabled[1] == 1 else None

        center = Point(tr.map(ev.buttonDownPos(QtCore.Qt.MouseButton.RightButton)))
        self._resetTarget()
        self.scaleBy(x=x, y=y, center=center)
        self.sigRangeChangedManually.emit(self.state["mouseEnabled"])

    def _on_left_mouse_drag(self, dif: Point, mask: npt.NDArray[np.float64]) -> None:
        tr = pg.invertQTransform(self.childGroup.transform())
        tr = tr.map(dif * mask) - tr.map(Point(0, 0))

        x = tr.x() if mask[0] == 1 else None
        y = tr.y() if mask[1] == 1 else None

        self._resetTarget()
        if x is not None or y is not None:
            self.translateBy(x=x, y=y)
        self.sigRangeChangedManually.emit(self.state["mouseEnabled"])

    def _on_left_mouse_drag_finished(self, ev: "mouseEvents.MouseDragEvent", pos: Point) -> None:
        self.rbScaleBox.hide()
        ax = QtCore.QRectF(Point(ev.buttonDownPos(ev.button())), Point(pos))
        ax = self.childGroup.mapRectFromParent(ax)
        self.showAxRect(ax)
        self.axHistoryPointer += 1
        self.axHistory = self.axHistory[: self.axHistoryPointer] + [ax]

    def updateSelectionBox(self, pos1: Point, pos2: Point) -> None:
        rect = QtCore.QRectF(pos1, pos2)
        rect = self.childGroup.mapRectFromParent(rect)
        self.selection_box.setPos(rect.topLeft())
        tr = QtGui.QTransform.fromScale(rect.width(), rect.height())
        self.selection_box.setTransform(tr)
        self.selection_box.show()
