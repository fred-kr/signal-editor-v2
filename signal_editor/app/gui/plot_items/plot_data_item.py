import bisect
import enum
import math
import typing as t

import numpy as np
import numpy.typing as npt
import pyqtgraph as pg
from pyqtgraph.graphicsItems.GraphicsObject import GraphicsObject
from pyqtgraph.graphicsItems.PlotCurveItem import PlotCurveItem
from pyqtgraph.graphicsItems.PlotDataItem import PlotDataset
from PySide6 import QtCore, QtGui

from ... import type_defs as _t
from ...enum_defs import PointSymbols
from .scatter_plot_item import CustomScatterPlotItem

if t.TYPE_CHECKING:
    from pyqtgraph.GraphicsScene import mouseEvents

    from .editing_view_box import EditingViewBox

    
class PlotDataItem(GraphicsObject):
    sigPlotChanged: t.ClassVar[QtCore.Signal] = QtCore.Signal(object)
    sigClicked: t.ClassVar[QtCore.Signal] = QtCore.Signal(object, object)
    sigPointsClicked: t.ClassVar[QtCore.Signal] = QtCore.Signal(object, object, object)
    sigPointsHovered: t.ClassVar[QtCore.Signal] = QtCore.Signal(object, object, object)

    def __init__(
        self,
        *args: npt.NDArray[np.float_ | np.intp | np.uintp],
        **kwargs: t.Unpack[_t.PlotDataItemKwargs],
    ) -> None:
        GraphicsObject.__init__(self)
        self.setFlag(self.GraphicsItemFlag.ItemHasNoContents)

        self._dataset: PlotDataset | None = None
        self._datasetMapped: PlotDataset | None = None
        self._datasetDisplay: PlotDataset | None = None

        self.curve = PlotCurveItem()
        self.scatter = CustomScatterPlotItem()
        self.curve.setParentItem(self)
        self.scatter.setParentItem(self)

        self.curve.sigClicked.connect(self.curveClicked)
        self.scatter.sigClicked.connect(self.scatterClicked)
        self.scatter.sigHovered.connect(self.scatterHovered)

        self.setProperty("xViewRangeWasChanged", False)
        self.setProperty("yViewRangeWasChanged", False)
        self.setProperty("styleWasChanged", True)

        self._drlLastClip = (0.0, 0.0)

        self.opts: _t.PlotDataItemOpts = {
            "connect": "auto",
            "skipFiniteCheck": False,
            "fftMode": False,
            "logMode": [False, False],
            "derivativeMode": False,
            "phasemapMode": False,
            "alphaHint": 1.0,
            "alphaMode": False,
            "pen": (200, 200, 200),
            "shadowPen": None,
            "fillLevel": None,
            "fillOutline": False,
            "fillBrush": None,
            "stepMode": None,
            "symbol": None,
            "symbolSize": 10,
            "symbolPen": (200, 200, 200),
            "symbolBrush": (50, 50, 150),
            "pxMode": True,
            "antialias": pg.getConfigOption("antialias"),
            "pointMode": None,
            "useCache": True,
            "downsample": 1,
            "autoDownsample": False,
            "downsampleMethod": "peak",
            "autoDownsampleFactor": 5.0,  # draw ~5 samples per pixel
            "clipToView": False,
            "dynamicRangeLimit": 1e6,
            "dynamicRangeHyst": 3.0,
            "data": None,
        }
        self.setCurveClickable(kwargs.get("clickable", False))
        self.setData(*args, **kwargs)

    @property
    def xData(self) -> npt.NDArray[np.float_ | np.intp | np.uintp] | None:
        return None if self._dataset is None else self._dataset.x

    @property
    def yData(self) -> npt.NDArray[np.float_ | np.intp | np.uintp] | None:
        return None if self._dataset is None else self._dataset.y

    def implements(self, interface: str | None = None) -> bool | list[str]:
        ints = ["plotData"]
        return ints if interface is None else interface in ints

    def name(self) -> str | None:
        """
        Returns the name of this item used in the legend.
        """
        return self.opts.get("name", None)

    def setCurveClickable(self, state: bool, width: int | None = None) -> None:
        """
        Set the curve to be clickable, with a tolerance margin represented by `width`.
        """
        self.curve.setClickable(state, width)

    def curveClickable(self) -> bool:
        """
        Returns `True` if the curve is set to be clickable.
        """
        return self.curve.clickable

    def boundingRect(self) -> QtCore.QRectF:
        return QtCore.QRectF()

    def setPos(self, x: float, y: float) -> None:
        GraphicsObject.setPos(self, x, y)
        self.viewTransformChanged()
        self.viewRangeChanged()

    def setAlpha(self, alpha: float, auto: bool) -> None:
        if self.opts["alphaHint"] == alpha and self.opts["alphaMode"] == auto:
            return
        self.opts["alphaHint"] = alpha
        self.opts["alphaMode"] = auto
        self.setOpacity(alpha)

    def setFftMode(self, state: bool) -> None:
        """
        Setting `state = True` enables mapping the data by a fast Fourier transform. If the `x`
        values are not equidistant, the data set is resampled at equal intervals.
        """
        if self.opts["fftMode"] == state:
            return
        self.opts["fftMode"] = state
        self._datasetMapped = None
        self._datasetDisplay = None
        self.updateItems(styleUpdate=False)
        self.informViewBoundsChanged()

    def setLogMode(self, xState: bool, yState: bool) -> None:
        """
        When log mode is enabled for the respective axis by setting `xState` or `yState` to `True`,
        a mapping according to `mapped = np.log10(value)` is applied to the data. For negative or
        zero values, this results in a `NaN` value.
        """
        if self.opts["logMode"] == [xState, yState]:
            return
        self.opts["logMode"] = [xState, yState]
        self._datasetMapped = None
        self._datasetDisplay = None
        self._adsLastValue = 1
        self.updateItems(styleUpdate=False)
        self.informViewBoundsChanged()

    def setDerivativeMode(self, state: bool) -> None:
        """
        Enable / disable derivative mode.

        Setting `state = True` enables derivative mode, where a mapping according to
        `y_mapped = dy / dx` is applied, with `dx` and `dy` representing the differences between
        adjacent `x` and `y` values.
        """
        if self.opts["derivativeMode"] == state:
            return
        self.opts["derivativeMode"] = state
        self._datasetMapped = None
        self._datasetDisplay = None
        self._adsLastValue = 1
        self.updateItems(styleUpdate=False)
        self.informViewBoundsChanged()

    def setPhasemapMode(self, state: bool) -> None:
        """
        Enable / disable phase map mode.

        Setting `state = True` enables phase map mode, where a mapping
        according to `x_mappped = y` and `y_mapped = dy / dx`
        is applied, plotting the numerical derivative of the data over the
        original `y` values.
        """
        if self.opts["phasemapMode"] == state:
            return
        self.opts["phasemapMode"] = state
        self._datasetMapped = None
        self._datasetDisplay = None
        self._adsLastValue = 1
        self.updateItems(styleUpdate=False)
        self.informViewBoundsChanged()

    def setPen(self, *args: _t.PGPen, **kwargs: t.Unpack[_t.PGPenKwargs]) -> None:
        """
        Set the pen used to draw lines between points.
        """
        pen = pg.mkPen(*args, **kwargs)
        self.opts["pen"] = pen
        self.updateItems(styleUpdate=True)

    def setShadowPen(self, *args: _t.PGPen, **kwargs: t.Unpack[_t.PGPenKwargs]) -> None:
        """
        Set the shadow pen used to draw lines between points (this is for enhancing contrast or
        emphasizing data). This line is drawn behind the primary pen and should generally be assigned
        greater width than the primary pen.
        """
        pen = None if args and args[0] is None else pg.mkPen(*args, **kwargs)
        self.opts["shadowPen"] = pen
        self.updateItems(styleUpdate=True)

    def setFillBrush(self, *args: _t.PGBrush, **kwargs: t.Unpack[_t.PGBrushKwargs]) -> None:
        """
        Sets the `QtGui.QBrush` used to fill the area under the curve.
        """
        brush = None if args and args[0] is None else pg.mkBrush(*args, **kwargs)
        self.opts["fillBrush"] = brush
        self.updateItems(styleUpdate=True)

    def setBrush(self, *args: _t.PGBrush, **kwargs: t.Unpack[_t.PGBrushKwargs]) -> None:
        """
        Alias for `setFillBrush()`.
        """
        self.setFillBrush(*args, **kwargs)

    def setFillLevel(self, level: float | None) -> None:
        """
        Enables filling the area under the curve towards the value specified by
        `level`. `None` disables the filling.
        """
        if self.opts["fillLevel"] == level:
            return
        self.opts["fillLevel"] = level
        self.updateItems(styleUpdate=True)

    def setSymbol(self, symbol: PointSymbols | QtGui.QPainterPath | list[PointSymbols | QtGui.QPainterPath] | None) -> None:
        if self.opts["symbol"] == symbol:
            return
        self.opts["symbol"] = symbol
        self.updateItems(styleUpdate=True)

    def setSymbolPen(self, *args: _t.PGPen, **kwargs: t.Unpack[_t.PGPenKwargs]) -> None:
        """
        Sets the pen used to draw symbols.
        """
        pen = pg.mkPen(*args, **kwargs)
        if self.opts["symbolPen"] == pen:
            return
        self.opts["symbolPen"] = pen
        self.updateItems(styleUpdate=True)

    def setSymbolBrush(self, *args: _t.PGBrush, **kwargs: t.Unpack[_t.PGBrushKwargs]) -> None:
        """
        Sets the brush used to fill symbols.
        """
        brush = pg.mkBrush(*args, **kwargs)
        if self.opts["symbolBrush"] == brush:
            return
        self.opts["symbolBrush"] = brush
        self.updateItems(styleUpdate=True)

    def setSymbolSize(self, size: float) -> None:
        """
        Sets the size of the symbols used for the data points.
        """
        if self.opts["symbolSize"] == size:
            return
        self.opts["symbolSize"] = size
        self.updateItems(styleUpdate=True)

    def setDownsampling(
        self,
        ds: int | None = None,
        auto: bool | None = None,
        method: t.Literal["subsample", "mean", "peak"] | None = None,
    ) -> None:
        changed = False
        if ds is not None and self.opts["downsample"] != ds:
            changed = True
            self.opts["downsample"] = ds

        if auto is not None and self.opts["autoDownsample"] != auto:
            self.opts["autoDownsample"] = auto
            changed = True

        if method is not None and self.opts["downsampleMethod"] != method:
            changed = True
            self.opts["downsampleMethod"] = method

        if changed:
            self._datasetMapped = None
            self._datasetDisplay = None
            self._adsLastValue = 1
            self.updateItems(styleUpdate=False)

    def setClipToView(self, state: bool) -> None:
        if self.opts["clipToView"] == state:
            return
        self.opts["clipToView"] = state
        self._datasetDisplay = None
        self.updateItems(styleUpdate=False)

    def setDynamicRangeLimit(self, limit: float = 1e6, hysteresis: float = 3.0) -> None:
        hysteresis = max(hysteresis, 1.0)
        self.opts["dynamicRangeHyst"] = hysteresis

        if limit == self.opts["dynamicRangeLimit"]:
            return
        self.opts["dynamicRangeLimit"] = limit
        self._datasetDisplay = None

        self.updateItems(styleUpdate=False)

    def setSkipFiniteCheck(self, skipFiniteCheck: bool) -> None:
        self.opts["skipFiniteCheck"] = skipFiniteCheck

    def setData(
        self,
        *args: npt.NDArray[np.float_ | np.intp | np.uintp] | None,
        **kwargs: t.Unpack[_t.PlotDataItemKwargs],
    ) -> None:
        x = None
        y = None
        
        if args and len(args) == 1:
            data = args[0]
            if data is None:
                pass
            elif data.ndim == 1:
                x = None
                y = data
            else:
                x = data[:, 0]
                y = data[:, 1]
        elif len(args) == 2:
            x = args[0]
            y = args[1]

        if "x" in kwargs:
            x = kwargs["x"]
        if "y" in kwargs:
            y = kwargs["y"]

        yData = None if y is None or len(y) == 0 else y.view(np.ndarray)
        xData = None if x is None or len(x) == 0 else x.view(np.ndarray)

        if "name" in kwargs:
            self.opts["name"] = kwargs["name"]
            self.setProperty("styleWasChanged", True)

        if "connect" in kwargs:
            self.opts["connect"] = kwargs["connect"]
            self.setProperty("styleWasChanged", True)

        if "skipFiniteCheck" in kwargs:
            self.opts["skipFiniteCheck"] = kwargs["skipFiniteCheck"]

        if (
            "symbol" not in kwargs
            and ("symbolPen" in kwargs or "symbolBrush" in kwargs or "symbolSize" in kwargs)
            and self.opts["symbol"] is None
        ):
            kwargs["symbol"] = "o"

        if "brush" in kwargs:
            kwargs["fillBrush"] = kwargs["brush"]

        for k in list(self.opts.keys()):
            if k in kwargs:
                self.opts[k] = kwargs[k]
                self.setProperty("styleWasChanged", True)

        if xData is None or yData is None:
            self._dataset = None
        else:
            self._dataset = PlotDataset(xData, yData)

        self._datasetMapped = None
        self._datasetDisplay = None
        self._adsLastValue = 1

        self.updateItems(styleUpdate=self.property("styleWasChanged"))
        self.setProperty("styleWasChanged", False)

        self.informViewBoundsChanged()

        self.sigPlotChanged.emit(self)

    def updateItems(self, styleUpdate: bool = True) -> None:
        curveArgs = {
            v: self.opts[k]
            for k, v in [
                ("pen", "pen"),
                ("shadowPen", "shadowPen"),
                ("fillLevel", "fillLevel"),
                ("fillOutline", "fillOutline"),
                ("fillBrush", "brush"),
                ("antialias", "antialias"),
                ("connect", "connect"),
                ("stepMode", "stepMode"),
                ("skipFiniteCheck", "skipFiniteCheck"),
            ]
            if k in self.opts
        }

        scatterArgs = {
            v: self.opts[k]
            for k, v in [
                ("symbolPen", "pen"),
                ("symbolBrush", "brush"),
                ("symbol", "symbol"),
                ("symbolSize", "size"),
                ("data", "data"),
                ("pxMode", "pxMode"),
                ("antialias", "antialias"),
                ("useCache", "useCache"),
            ]
            if k in self.opts
        }

        dataset = self._getDisplayDataset()
        if dataset is None:
            self.curve.hide()
            self.scatter.hide()
            return

        x = dataset.x
        y = dataset.y

        curveArgs["connect"] = curveArgs.get("connect", "auto")
        if curveArgs["connect"] == "auto":
            curveArgs["connect"] = "finite" if dataset.containsNonfinite else "all"
            curveArgs["skipFiniteCheck"] = not dataset.containsNonfinite

        if curveArgs.get("pen") is not None or (
            curveArgs.get("brush") is not None and curveArgs.get("fillLevel") is not None
        ):
            self.curve.setData(x=x, y=y, **curveArgs)
            self.curve.show()
        else:
            self.curve.hide()

        if self.opts.get("symbol") is not None:
            if self.opts.get("stepMode", False) in ("center", True):
                x = 0.5 * (x[:-1] + x[1:])
            self.scatter.setData(x=x, y=y, **scatterArgs)

    def getOriginalDataset(
        self,
    ) -> (
        tuple[
            npt.NDArray[np.float_ | np.intp | np.uintp], npt.NDArray[np.float_ | np.intp | np.uintp]
        ]
        | tuple[None, None]
    ):
        dataset = self._dataset
        return (None, None) if dataset is None else (dataset.x, dataset.y)

    def _getDisplayDataset(self) -> PlotDataset | None:
        if self._dataset is None:
            return None

        if (
            self._datasetDisplay is not None
            and not (self.property("xViewRangeWasChanged") and self.opts["clipToView"])
            and not (self.property("xViewRangeWasChanged") and self.opts["autoDownsample"])
            and not (
                self.property("yViewRangeWasChanged") and self.opts["dynamicRangeLimit"] is not None
            )
        ):
            return self._datasetDisplay

        if self._datasetMapped is None:
            x = self._dataset.x
            y = self._dataset.y
            if y.dtype == bool:
                y = y.astype(np.uint8)
            if x.dtype == bool:
                x = x.astype(np.uint8)

            if self.opts["fftMode"]:
                x, y = self._fourierTransform(x, y)
                # Ignore the first bin for fft data if we have a logx scale
                if self.opts["logMode"][0]:
                    x = x[1:]
                    y = y[1:]

            if self.opts["derivativeMode"]:
                y = np.diff(self._dataset.y) / np.diff(self._dataset.x)
                x = x[:-1]

            if self.opts["phasemapMode"]:
                x = self._dataset.y[:-1]
                y = np.diff(self._dataset.y) / np.diff(self._dataset.x)

            dataset = PlotDataset(x, y, self._dataset.xAllFinite, self._dataset.yAllFinite)

            if True in self.opts["logMode"]:
                dataset.applyLogMapping(self.opts["logMode"])

            self._datasetMapped = dataset

        x = self._datasetMapped.x
        y = self._datasetMapped.y
        xAllFinite = self._datasetMapped.xAllFinite
        yAllFinite = self._datasetMapped.yAllFinite

        view = self.getViewBox()
        view_range = None if view is None else view.viewRect()
        if view_range is None:
            view_range = self.viewRect()

        ds = self.opts["downsample"]

        if self.opts["autoDownsample"]:
            finite_x = x if xAllFinite else x[np.isfinite(x)]
            if view_range is not None and len(finite_x) > 1:
                dx = float(finite_x[-1] - finite_x[0]) / (len(finite_x) - 1)
                if dx != 0.0:
                    width = self.getViewBox().width()
                    if width != 0.0:
                        ds_float = max(
                            1.0,
                            abs(
                                view_range.width()
                                / dx
                                / (width * self.opts["autoDownsampleFactor"])
                            ),
                        )
                        if math.isfinite(ds_float):
                            ds = int(ds_float)

            if math.isclose(ds, self._adsLastValue, rel_tol=0.01):
                ds = self._adsLastValue
            self._adsLastValue = ds

        if (
            view is not None
            and not view.autoRangeEnabled()[0]
            and (view_range is not None and len(x) > 1)
            and self.opts["clipToView"]
        ):
            x0 = bisect.bisect_left(x, view_range.left()) - ds
            x0 = pg.clip_scalar(x0, 0, len(x))

            x1 = bisect.bisect_left(x, view_range.right()) + ds
            x1 = pg.clip_scalar(x1, 0, len(x))

            x = x[x0:x1]
            y = y[x0:x1]

        if ds > 1:
            if self.opts["downsampleMethod"] == "subsample":
                x = x[::ds]
                y = y[::ds]
            elif self.opts["downsampleMethod"] == "mean":
                n = len(x) // ds
                stx = ds // 2
                x = x[stx : stx + n * ds : ds]
                y = y[: n * ds].reshape(n, ds).mean(axis=1)
            elif self.opts["downsampleMethod"] == "peak":
                n = len(x) // ds
                x1 = np.empty((n, 2))
                stx = ds // 2
                x1[:] = x[stx : stx + n * ds : ds, np.newaxis]
                x = x1.reshape(n * 2)
                y1 = np.empty((n, 2))
                y2 = y[: n * ds].reshape((n, ds))
                y1[:, 0] = y2.max(axis=1)
                y1[:, 1] = y2.min(axis=1)
                y = y1.reshape(n * 2)

        if self.opts["dynamicRangeLimit"] is not None and view_range is not None:
            data_range = self._datasetMapped.dataRect()
            if data_range is not None:
                view_height = view_range.height()
                limit = self.opts["dynamicRangeLimit"]
                hyst = self.opts["dynamicRangeHyst"]

                if (
                    view_height > 0
                    and not data_range.bottom() < view_range.top()
                    and not data_range.top() > view_range.bottom()
                    and data_range.height() > 2 * hyst * limit * view_height
                ):
                    cache_is_good = False
                    if self._datasetDisplay is not None:
                        top_exc = -(self._drlLastClip[0] - view_range.bottom()) / view_height
                        bot_exc = (self._drlLastClip[1] - view_range.top()) / view_height

                        if (
                            top_exc >= limit / hyst
                            and top_exc <= limit * hyst
                            and bot_exc >= limit / hyst
                            and bot_exc <= limit * hyst
                        ):
                            x = self._datasetDisplay.x
                            y = self._datasetDisplay.y
                            cache_is_good = True

                    if not cache_is_good:
                        min_val = view_range.bottom() - limit * view_height
                        max_val = view_range.top() + limit * view_height
                        y = pg.clip_array(y, min_val, max_val)
                        self._drlLastClip = (min_val, max_val)

        self._datasetDisplay = PlotDataset(x, y, xAllFinite, yAllFinite)
        self.setProperty("xViewRangeWasChanged", False)
        self.setProperty("yViewRangeWasChanged", False)

        return self._datasetDisplay

    def getData(
        self,
    ) -> (
        tuple[
            npt.NDArray[np.float_ | np.intp | np.uintp], npt.NDArray[np.float_ | np.intp | np.uintp]
        ]
        | tuple[None, None]
    ):
        dataset = self._getDisplayDataset()
        return (None, None) if dataset is None else (dataset.x, dataset.y)

    def dataRect(self) -> QtCore.QRectF | None:
        return None if self._dataset is None else self._dataset.dataRect()

    def dataBounds(
        self,
        ax: t.Literal[0, 1],
        frac: float = 1.0,
        orthoRange: tuple[float, float] | list[float] | None = None,
    ) -> tuple[float, float] | list[float | None] | list[None]:
        bounds = [None, None]
        if self.curve.isVisible():
            bounds = self.curve.dataBounds(ax, frac, orthoRange)
        elif self.scatter.isVisible():
            r2 = self.scatter.dataBounds(ax, frac, orthoRange)
            bounds = [
                r2[0]
                if bounds[0] is None
                else (bounds[0] if r2[0] is None else min(r2[0], bounds[0])),
                r2[1]
                if bounds[1] is None
                else (bounds[1] if r2[1] is None else min(r2[1], bounds[1])),
            ]
        return bounds

    def pixelPadding(self) -> float:
        pad = 0
        if self.curve.isVisible():
            pad = max(pad, self.curve.pixelPadding())
        elif self.scatter.isVisible():
            pad = max(pad, self.scatter.pixelPadding())
        return pad

    def clear(self) -> None:
        self._dataset = None
        self._datasetMapped = None
        self._datasetDisplay = None
        self.curve.clear()
        self.scatter.clear()

    def appendData(self, *args: t.Any, **kargs: t.Any) -> None: ...

    @QtCore.Slot(object, object)
    def curveClicked(self, curve: PlotCurveItem, ev: "mouseEvents.MouseClickEvent") -> None:
        self.sigClicked.emit(self, ev)

    @QtCore.Slot(object, object, object)
    def scatterClicked(
        self, plt: t.Self, points: t.Iterable[pg.SpotItem], ev: "mouseEvents.MouseClickEvent"
    ) -> None:
        self.sigClicked.emit(self, ev)
        self.sigPointsClicked.emit(self, points, ev)

    @QtCore.Slot(object, object, object)
    def scatterHovered(
        self, plt: t.Self, points: t.Iterable[pg.SpotItem], ev: "mouseEvents.MouseClickEvent"
    ) -> None:
        self.sigPointsHovered.emit(self, points, ev)

    def viewRangeChanged(
        self,
        vb: "pg.ViewBox | EditingViewBox | None" = None,
        ranges: list[list[float]] | None = None,
        changed: list[bool] | None = None,
    ) -> None:
        update_needed = False
        if changed is None or changed[0]:
            self.setProperty("xViewRangeWasChanged", True)
            if self.opts["clipToView"] or self.opts["autoDownsample"]:
                self._datasetDisplay = None
                update_needed = True

        if changed is None or changed[1]:
            self.setProperty("yViewRangeWasChanged", True)
            if self.opts["dynamicRangeLimit"] is not None:
                update_needed = True

        if update_needed:
            self.updateItems(styleUpdate=False)

    def _fourierTransform(
        self, x: npt.NDArray[np.float_], y: npt.NDArray[np.float_]
    ) -> tuple[npt.NDArray[np.float_], npt.NDArray[np.float_]]:
        dx = np.diff(x)
        uniform = not np.any(np.abs(dx - dx[0]) > (abs(dx[0]) / 1000.0))
        if not uniform:
            x2 = np.linspace(x[0], x[-1], len(x), dtype=x.dtype)
            y = np.interp(x2, x, y)
            x = x2

        n = y.size
        f = np.fft.rfft(y) / n
        d = float(x[-1] - x[0]) / (len(x) - 1)
        x = np.fft.rfftfreq(n, d)
        y = np.abs(f)
        return x, y
