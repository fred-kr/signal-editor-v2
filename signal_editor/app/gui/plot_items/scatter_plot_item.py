import typing as t

import numpy as np
import pyqtgraph as pg
from PySide6 import QtCore

from ...utils import make_qbrush, make_qpen


class CustomScatterPlotItem(pg.ScatterPlotItem):
    """
    Custom `pyqtgraph.ScatterPlotItem` subclass that fixes an issue where `num_pts` would error when
    `y` is a single point not enclosed in an object with a `__len__` attribute. Also refactors the
    code to make use of more modern Python features (3.12+).
    """

    def addPoints(self, *args: t.Any, **kargs: t.Any) -> None:
        arg_keys = ["spots", "x", "y"]
        for i, key in enumerate(arg_keys[: len(args)]):
            kargs[key] = args[i]

        pos = kargs.get("pos")
        if pos is not None:
            if isinstance(pos, np.ndarray):
                kargs["x"], kargs["y"] = pos[:, 0], pos[:, 1]
            else:
                kargs["x"], kargs["y"] = zip(
                    *((p.x(), p.y()) if isinstance(p, QtCore.QPointF) else p for p in pos), strict=True
                )

        spots = kargs.get("spots")
        x = kargs.get("x")
        y = kargs.get("y")

        # Determine how many spots we have
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
                for k, v in spot.items():
                    if k == "pos":
                        pos = v
                        if isinstance(pos, QtCore.QPointF):
                            x, y = pos.x(), pos.y()
                        else:
                            x, y = pos[0], pos[1]
                        new_data[i]["x"] = x
                        new_data[i]["y"] = y
                    elif k == "pen":
                        new_data[i][k] = make_qpen(v)
                    elif k == "brush":
                        new_data[i][k] = make_qbrush(v)
                    elif k in ("x", "y", "size", "symbol", "data"):
                        new_data[i][k] = v
                    else:
                        raise KeyError(f"Invalid key: {k}")
        # Handle 'y' parameter
        elif y is not None:
            new_data["x"] = x
            new_data["y"] = y

        for k, v in kargs.items():
            if k == "name":
                self.opts["name"] = v
            elif k == "pxMode":
                self.setPxMode(v)
            elif k == "antialias":
                self.opts["antialias"] = v
            elif k == "hoverable":
                self.opts["hoverable"] = bool(v)
            elif k == "tip":
                self.opts["tip"] = v
            elif k == "useCache":
                self.opts["useCache"] = v
            elif k in ("pen", "brush", "symbol", "size"):
                set_method = getattr(self, f"set{k.capitalize()}")
                set_method(v, update=False, dataSet=new_data, mask=kargs.get("mask", None))
            elif k in ("hoverPen", "hoverBrush", "hoverSymbol", "hoverSize"):
                vh = kargs[k]
                if k == "hoverPen":
                    vh = make_qpen(vh)
                elif k == "hoverBrush":
                    vh = make_qbrush(vh)
                self.opts[k] = vh
            elif k == "data":
                self.setPointData(kargs["data"], dataSet=new_data)

        # Update the scatter plot item
        self.prepareGeometryChange()
        self.informViewBoundsChanged()
        self.bounds = [None, None]
        self.invalidate()
        self.updateSpots(new_data)
        self.sigPlotChanged.emit(self)
