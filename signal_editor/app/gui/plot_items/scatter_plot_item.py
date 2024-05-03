import typing as t

import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt.internals import PrimitiveArray
from pyqtgraph.graphicsItems.ScatterPlotItem import SymbolAtlas
from PySide6 import QtCore, QtGui

from ...enum_defs import PointSymbols

from ... import type_defs as _t


def _mk_pen(*args: _t.PGPen, **kwargs: t.Unpack[_t.PGPenKwargs]) -> QtGui.QPen:
    if len(args) == 1 and isinstance(args[0], QtGui.QPen):
        return args[0]
    return pg.mkPen(*args, **kwargs)


def _mk_brush(*args: _t.PGBrush, **kwargs: t.Unpack[_t.PGBrushKwargs]) -> QtGui.QBrush:
    if len(args) == 1 and isinstance(args[0], QtGui.QBrush):
        return args[0]
    return pg.mkBrush(*args, **kwargs)


class CustomScatterPlotItem(pg.ScatterPlotItem):
    """
    Custom `pyqtgraph.ScatterPlotItem` subclass that fixes an issue where `num_pts` would error when
    `y` is a single point not enclosed in an object with a `__len__` attribute. Also refactors the
    code to make use of more modern Python features (3.12+).
    """

    def __init__(
        self,
        *args: list[_t.SpotDict] | t.Sequence[float],
        **kargs: t.Unpack[_t.SpotItemSetDataKwargs],
    ) -> None:
        pg.GraphicsObject.__init__(self)

        self.picture: QtGui.QPicture | None = None
        self.fragmentAtlas = SymbolAtlas()
        if screen := QtGui.QGuiApplication.primaryScreen():
            self.fragmentAtlas.setDevicePixelRatio(screen.devicePixelRatio())

        dtype = [
            ("x", np.float_),
            ("y", np.float_),
            ("size", np.float_),
            ("symbol", np.object_),
            ("pen", np.object_),
            ("brush", np.object_),
            ("visible", np.bool_),
            ("data", np.object_),
            ("hovered", np.bool_),
            ("item", np.object_),
            ("sourceRect", [("x", np.intp), ("y", np.intp), ("w", np.intp), ("h", np.intp)]),
        ]

        self.data = np.empty(0, dtype=dtype)
        self.bounds = [None, None]
        self._maxSpotWidth = 0
        self._maxSpotPxWidth = 0
        self._pixmapFragments = PrimitiveArray(QtGui.QPainter.PixmapFragment, 10)
        self.opts = {
            "pxMode": True,
            "useCache": True,  ## If useCache is False, symbols are re-drawn on every paint.
            "antialias": pg.getConfigOption("antialias"),
            "compositionMode": None,
            "name": None,
            "symbol": PointSymbols.Circle,
            "size": 7,
            "pen": pg.mkPen(pg.getConfigOption("foreground")),
            "brush": pg.mkBrush(100, 100, 150),
            "hoverable": False,
            "tip": None,
            "hoverSymbol": None,
            "hoverSize": -1,
            "hoverPen": None,
            "hoverBrush": None,
        }

        self.setData(*args, **kargs)
        self._toolTipCleared = True

    def addPoints(
        self,
        *args: list[_t.SpotDict] | t.Sequence[float],
        **kargs: t.Unpack[_t.SpotItemSetDataKwargs],
    ) -> None:
        arg_keys = ["spots", "x", "y"]
        for i, key in enumerate(arg_keys[: len(args)]):
            kargs[key] = args[i]

        pos = kargs.get("pos")
        if pos is not None:
            if isinstance(pos, np.ndarray):
                kargs["x"], kargs["y"] = pos[:, 0], pos[:, 1]
            else:
                kargs["x"] = [p.x() if isinstance(p, QtCore.QPointF) else p[0] for p in pos]
                kargs["y"] = [p.y() if isinstance(p, QtCore.QPointF) else p[1] for p in pos]

        spots = kargs.get("spots")
        x = kargs.get("x")
        y = kargs.get("y")

        # Calculate number of points
        num_pts = (
            len(spots)
            if spots is not None
            else len(y)
            if y is not None and hasattr(y, "__len__")
            else 1
            if y is not None
            else 0
        )

        # Initialize new data array
        self.data["item"][...] = None
        old_data = self.data
        self.data = np.empty(len(old_data) + num_pts, dtype=self.data.dtype)
        self.data[: len(old_data)] = old_data
        new_data = self.data[len(old_data) :]
        new_data["size"] = -1
        new_data["visible"] = True

        # Handle 'spots' parameter
        if spots is not None:
            for i, spot in enumerate(spots):
                for k in spot:
                    if k == "pos":
                        pos = spot[k]
                        if isinstance(pos, QtCore.QPointF):
                            x, y = pos.x(), pos.y()
                        else:
                            x, y = pos[0], pos[1]
                        new_data[i]["x"] = x
                        new_data[i]["y"] = y
                    elif k == "pen":
                        new_data[i][k] = _mk_pen(spot[k])
                    elif k == "brush":
                        new_data[i][k] = _mk_brush(spot[k])
                    elif k in ["x", "y", "size", "symbol", "data"]:
                        new_data[i][k] = spot[k]
                    else:
                        raise KeyError(f"Unknown spot parameter: {k}")
        # Handle 'y' parameter
        elif y is not None:
            new_data["x"] = x
            new_data["y"] = y

        if "name" in kargs:
            self.opts["name"] = kargs["name"]
        if "pxMode" in kargs:
            self.setPxMode(kargs["pxMode"])
        if "antialias" in kargs:
            self.opts["antialias"] = kargs["antialias"]
        if "hoverable" in kargs:
            self.opts["hoverable"] = bool(kargs["hoverable"])
        if "tip" in kargs:
            self.opts["tip"] = kargs["tip"]
        if "useCache" in kargs:
            self.opts["useCache"] = kargs["useCache"]
        if "pen" in kargs:
            self.setPen(kargs["pen"], update=False, dataSet=new_data, mask=kargs.get("mask", None))
        if "brush" in kargs:
            self.setBrush(
                kargs["brush"], update=False, dataSet=new_data, mask=kargs.get("mask", None)
            )
        if "symbol" in kargs:
            self.setSymbol(
                kargs["symbol"], update=False, dataSet=new_data, mask=kargs.get("mask", None)
            )
        if "size" in kargs:
            self.setSize(
                kargs["size"], update=False, dataSet=new_data, mask=kargs.get("mask", None)
            )
        if "hoverPen" in kargs:
            vh = _mk_pen(kargs["hoverPen"])
            self.opts["hoverPen"] = vh
        if "hoverBrush" in kargs:
            vh = _mk_brush(kargs["hoverBrush"])
            self.opts["hoverBrush"] = vh
        if "hoverSymbol" in kargs:
            vh = kargs["hoverSymbol"]
            self.opts["hoverSymbol"] = vh
        if "hoverSize" in kargs:
            vh = kargs["hoverSize"]
            self.opts["hoverSize"] = vh
        if "data" in kargs:
            self.setPointData(kargs["data"], dataSet=new_data)

        # Update the scatter plot item
        self.prepareGeometryChange()
        self.informViewBoundsChanged()
        self.bounds = [None, None]
        self.invalidate()
        self.updateSpots(new_data)
        self.sigPlotChanged.emit(self)
