import typing as t

import pyqtgraph as pg
from PySide6 import QtCore

from ... import type_defs as _t

if t.TYPE_CHECKING:
    from pyqtgraph.GraphicsScene import mouseEvents


class ClickableRegionItem(pg.LinearRegionItem):
    """
    A clickable region item for pyqtgraph plots.

    This class extends `pg.LinearRegionItem` to allow for click events on the region.

    Attributes:
        sig_clicked (QtCore.Signal): Emitted when the region is clicked.
            The signal carries an integer value representing the section ID.
    """

    sig_clicked: t.ClassVar[QtCore.Signal] = QtCore.Signal(int)

    def __init__(
        self,
        values: t.Sequence[float] = (0, 1),
        orientation: t.Literal["vertical", "horizontal"] = "vertical",
        brush: _t.PGBrush | None = None,
        pen: _t.PGPen | None = None,
        hoverBrush: _t.PGBrush | None = None,
        hoverPen: _t.PGPen | None = None,
        movable: bool = True,
        bounds: t.Sequence[float] | None = None,
        span: t.Sequence[float] = (0, 1),
        swapMode: t.Literal["block", "push", "sort"] | None = "sort",
        clipItem: pg.GraphicsObject | None = None,
    ) -> None:
        super().__init__(
            values, orientation, brush, pen, hoverBrush, hoverPen, movable, bounds, span, swapMode, clipItem
        )

        self._section_id: int = 0

    @property
    def section_id(self) -> int:
        return self._section_id

    @section_id.setter
    def section_id(self, value: int) -> None:
        self._section_id = value

    def mouseClickEvent(self, ev: "mouseEvents.MouseClickEvent") -> None:
        if ev.button() == QtCore.Qt.MouseButton.LeftButton:
            self.sig_clicked.emit(self._section_id)
            ev.accept()
        else:
            super().mouseClickEvent(ev)

    def hoverEvent(self, ev: "mouseEvents.HoverEvent") -> None:
        if (not ev.isExit()) and ev.acceptDrags(QtCore.Qt.MouseButton.LeftButton):
            self.setMouseHover(True)
        else:
            self.setMouseHover(False)
