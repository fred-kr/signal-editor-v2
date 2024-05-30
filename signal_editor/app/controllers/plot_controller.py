import typing as t

import numpy as np
import numpy.typing as npt
import pyqtgraph as pg
from PySide6 import QtCore, QtGui, QtWidgets

from .. import type_defs as _t
from ..enum_defs import PointSymbols
from ..gui.plot_items import CustomScatterPlotItem
from ..gui.plot_items.editing_view_box import EditingViewBox
from ..gui.plot_items.time_axis_item import TimeAxisItem

if t.TYPE_CHECKING:
    from pyqtgraph.GraphicsScene import mouseEvents

    from ..gui.main_window import MainWindow


class PlotController(QtCore.QObject):
    sig_scatter_data_changed = QtCore.Signal(str, object)

    def __init__(
        self,
        parent: QtCore.QObject | None,
        main_window: "MainWindow",
    ) -> None:
        super().__init__(parent)

        self._mw_ref = main_window
        self.regions: list[pg.LinearRegionItem] = []
        self._show_regions = False
        self._setup_plot_widgets()
        self._setup_plot_items()
        self._setup_plot_data_items()

        settings = QtCore.QSettings()
        self.search_around_click_radius: int = settings.value(
            "Editing/search_around_click_radius", 20, type=int
        )  # type: ignore

    def _setup_plot_widgets(self) -> None:
        widget_layout = QtWidgets.QVBoxLayout()
        widget_layout.setContentsMargins(0, 0, 0, 0)
        widget_layout.setSpacing(2)
        main_plot_widget = pg.PlotWidget(viewBox=EditingViewBox(name="main_plot"))
        rate_plot_widget = pg.PlotWidget(viewBox=pg.ViewBox(name="rate_plot"))

        widget_layout.addWidget(main_plot_widget)
        widget_layout.addWidget(rate_plot_widget)
        self._mw_ref.plot_container.setLayout(widget_layout)
        self.pw_main = main_plot_widget
        self.pw_rate = rate_plot_widget
        self.mpw_result = self._mw_ref.mpl_widget

    def _setup_plot_items(self) -> None:
        for plt_item in (self.pw_main.getPlotItem(), self.pw_rate.getPlotItem()):
            vb = plt_item.getViewBox()
            plt_item.setAxisItems({"top": TimeAxisItem(orientation="top")})
            plt_item.showGrid(x=False, y=True)
            plt_item.setDownsampling(auto=True)
            plt_item.setClipToView(True)
            plt_item.addLegend(colCount=2)
            plt_item.addLegend().anchor(itemPos=(0, 1), parentPos=(0, 1), offset=(5, -5))
            plt_item.setMouseEnabled(x=True, y=False)
            vb.enableAutoRange("y", enable=0.99)
            vb.setAutoVisible(y=False)

        self.pw_main.getPlotItem().getViewBox().setXLink("rate_plot")

        settings = QtCore.QSettings()
        self.set_background_color(settings.value("Plot/background_color"))
        self.set_foreground_color(settings.value("Plot/foreground_color"))

    def _setup_region_selector(self) -> None:
        settings = QtCore.QSettings()
        brush_col: QtGui.QColor = settings.value("Plot/section_marker_color", type=QtGui.QColor)  # type: ignore
        hover_brush_col = brush_col
        hover_brush_col.setAlpha(30)
        self.region_selector = pg.LinearRegionItem(
            brush=brush_col,
            pen=(255, 255, 255, 255),
            hoverBrush=hover_brush_col,
            hoverPen={"color": "gray", "width": 2},
        )
        self.region_selector.setVisible(False)
        self.region_selector.setZValue(1e3)
        for line in self.region_selector.lines:
            line.addMarker("<|>", position=0.5, size=12)

        self.pw_main.addItem(self.region_selector)

    def remove_region_selector(self) -> None:
        """
        Remove the region selector from the main plot widget.
        """        
        if self.region_selector:
            self.pw_main.removeItem(self.region_selector)
            self.region_selector.setParent(None)
            self.region_selector = None

    def _setup_plot_data_items(self) -> None:
        self.initialize_signal_curve()
        self.initialize_peak_scatter()
        self.initialize_rate_curve()
        self._setup_region_selector()

    def initialize_signal_curve(self, pen_color: _t.PGColor | None = None) -> None:
        """
        Create the PlotDataItem representing the signal curve.

        Parameters
        ----------
        pen_color : 
            The color of the pen used to draw the signal curve, by default None
        """        
        settings = QtCore.QSettings()

        if pen_color is None:
            pen_color = settings.value(  # type: ignore
                "Plot/signal_line_color", "tomato", type=QtGui.QColor
            )
        click_width = settings.value("Editing/click_width_signal_line", 20, type=int)
        signal = pg.PlotDataItem(
            pen=pen_color,
            skipFiniteCheck=True,
            autoDownsample=True,
            name="Signal",
        )
        signal.setCurveClickable(True, width=click_width)  # type: ignore
        signal.sigClicked.connect(self._on_curve_clicked)
        signal.sigPlotChanged.connect(self.set_view_limits)
        self.signal_curve = signal
        self.pw_main.addItem(self.signal_curve)

    def remove_signal_curve(self) -> None:
        if self.signal_curve is None:
            return
        self.signal_curve.sigClicked.disconnect(self._on_curve_clicked)
        self.signal_curve.sigPlotChanged.disconnect(self.set_view_limits)
        self.pw_main.removeItem(self.signal_curve)
        self.signal_curve.setParent(None)
        self.signal_curve = None

    def initialize_peak_scatter(
        self,
        brush_color: _t.PGColor | None = None,
        hover_pen: _t.PGColor = "black",
        hover_brush: _t.PGColor = "red",
    ) -> None:
        if brush_color is None:
            brush_color = QtCore.QSettings().value(  # type: ignore
                "Plot/point_color", "darkgoldenrod", type=QtGui.QColor
            )
        scatter = CustomScatterPlotItem(
            pxMode=True,
            size=10,
            pen=None,
            brush=brush_color,
            useCache=True,
            name="Peaks",
            hoverable=True,
            hoverPen=hover_pen,
            hoverSymbol=PointSymbols.Cross,
            hoverBrush=hover_brush,
            hoverSize=15,
            tip=None,
        )
        scatter.setZValue(60)
        scatter.sigClicked.connect(self._on_scatter_clicked)
        self.peak_scatter = scatter
        self.pw_main.addItem(self.peak_scatter)

    def remove_peak_scatter(self) -> None:
        if self.peak_scatter is None:
            return
        self.peak_scatter.sigClicked.disconnect(self._on_scatter_clicked)
        self.pw_main.removeItem(self.peak_scatter)
        self.peak_scatter.setParent(None)
        self.peak_scatter = None

    def initialize_rate_curve(self, pen_color: _t.PGColor | None = None) -> None:
        if pen_color is None:
            pen_color = QtCore.QSettings().value(  # type: ignore
                "Plot/rate_line_color", "lightgreen", type=QtGui.QColor
            )
        rate_curve = pg.PlotDataItem(
            pen=pen_color,
            skipFiniteCheck=True,
            autoDownsample=True,
            name="Rate",
        )
        self.rate_curve = rate_curve
        self.pw_rate.addItem(self.rate_curve)

    def remove_rate_curve(self) -> None:
        if self.rate_curve is None:
            return
        self.pw_rate.removeItem(self.rate_curve)
        self.rate_curve.setParent(None)
        self.rate_curve = None

    def remove_plot_data_items(self) -> None:
        self.remove_signal_curve()
        self.remove_peak_scatter()
        self.remove_rate_curve()
        self.remove_region_selector()

    @QtCore.Slot(int)
    def update_time_axis_scale(self, sampling_rate: int) -> None:
        if sampling_rate == 0:
            return
        for plt_item in (self.pw_main.getPlotItem(), self.pw_rate.getPlotItem()):
            plt_item.getAxis("top").setScale(1 / sampling_rate)

    @QtCore.Slot(int)
    def reset_view_range(self, upper_bound: int) -> None:
        self.pw_main.plotItem.vb.setRange(xRange=(0, upper_bound), disableAutoRange=False)
        self.pw_rate.plotItem.vb.setRange(xRange=(0, upper_bound), disableAutoRange=False)

    @QtCore.Slot(object)
    def set_view_limits(self, plt_data_item: pg.PlotDataItem) -> None:
        if plt_data_item.xData is None or plt_data_item.xData.size == 0:
            return
        len_data = plt_data_item.xData.size
        self.pw_main.plotItem.vb.setLimits(
            xMin=-0.25 * len_data, xMax=1.25 * len_data, maxYRange=1e5, minYRange=0.1
        )
        self.pw_rate.plotItem.vb.setLimits(
            xMin=-0.25 * len_data, xMax=1.25 * len_data, maxYRange=1e5, minYRange=0.1
        )
        self.reset_view_range(len_data)

    def reset(self) -> None:
        self.pw_main.clear()
        if self.pw_main.plotItem.legend:
            self.pw_main.plotItem.legend.clear()
        self.pw_rate.clear()
        if self.pw_rate.plotItem.legend:
            self.pw_rate.plotItem.legend.clear()

        self.mpw_result.fig.clear()

        self.remove_plot_data_items()
        self.clear_regions()
        self._setup_plot_data_items()

    @QtCore.Slot(bool)
    def toggle_regions(self, visible: bool) -> None:
        for i, region in enumerate(self.regions):
            region.setToolTip(f"Section {i + 1:03}")
            region.setVisible(visible)
        self._show_regions = visible

    def remove_region(
        self, region: pg.LinearRegionItem | None = None, bounds: tuple[float, float] | None = None
    ) -> None:
        if region is not None:
            self.regions.remove(region)
        if bounds is not None:
            for region in self.regions:
                reg_bounds = region.getRegion()
                if np.allclose(bounds, reg_bounds):
                    self.regions.remove(region)
                    self.pw_main.removeItem(region)
                    break

    def clear_regions(self) -> None:
        for region in self.regions:
            region.setParent(None)
            if region in self.pw_main.plotItem.items:
                self.pw_main.removeItem(region)
        self.regions.clear()

    def show_region_selector(self, bounds: tuple[float, float]) -> None:
        if not self.region_selector:
            return

        self.region_selector.setBounds(bounds)
        view_range = self.pw_main.plotItem.vb.viewRange()[0]
        span = view_range[1] - view_range[0]
        initial_region = (view_range[0], view_range[0] + 0.33 * span)
        self.region_selector.setRegion(initial_region)
        if self.region_selector not in self.pw_main.plotItem.items:
            self.pw_main.addItem(self.region_selector)

        self.region_selector.setVisible(True)

    def hide_region_selector(self) -> None:
        if self.region_selector:
            self.region_selector.setVisible(False)

    @QtCore.Slot(int, int)
    def mark_region(self, x1: int, x2: int) -> None:
        r, g, b = 0, 200, 100
        marked_region = pg.LinearRegionItem(
            values=(x1, x2),
            brush=(r, g, b, 50),
            pen=pg.mkPen(color=(r, g, b, 255), width=2, style=QtCore.Qt.PenStyle.DashLine),
            movable=False,
        )
        marked_region.setVisible(self._show_regions)
        marked_region.setZValue(10)
        self.regions.append(marked_region)
        self.pw_main.addItem(marked_region)
        self.hide_region_selector()

    def set_signal_data(self, y_data: npt.NDArray[np.float64], clear: bool = False) -> None:
        if self.signal_curve is None:
            return
        if clear:
            self.signal_curve.clear()
            self.clear_peaks()

        self.signal_curve.setData(y_data)

    def set_rate_data(self, y_data: npt.NDArray[np.float64 | np.intp], x_data: npt.NDArray[np.intp] | None = None, clear: bool = False) -> None:
        if self.rate_curve is None:
            return
        if clear:
            self.rate_curve.clear()

        if x_data is not None:
            self.rate_curve.setData(x_data, y_data)
        else:
            self.rate_curve.setData(y_data)

    def set_peak_data(
        self, x_data: npt.NDArray[np.intp | np.uintp], y_data: npt.NDArray[np.float64]
    ) -> None:
        if self.peak_scatter is None:
            return
        self.peak_scatter.setData(x=x_data, y=y_data)

    @QtCore.Slot()
    def clear_peaks(self) -> None:
        if self.peak_scatter is None:
            return
        self.peak_scatter.clear()
        if self.rate_curve is not None:
            self.rate_curve.clear()
        # ? Unclear if this is a good way of forcing a redraw
        self.pw_main.invalidateScene()
        self.pw_rate.invalidateScene()

    def remove_selection_rect(self) -> None:
        vb: EditingViewBox = self.pw_main.plotItem.vb  # type: ignore
        vb.selection_box = None
        vb.mapped_selection_rect = None

    @QtCore.Slot(object, object, object)
    def _on_scatter_clicked(
        self,
        sender: CustomScatterPlotItem,
        points: t.Sequence[pg.SpotItem],
        ev: "mouseEvents.MouseClickEvent",
    ) -> None:
        ev.accept()
        if not self.peak_scatter or len(points) == 0:
            return

        point = points[0]
        point_x = int(point.pos().x())
        point_index = point.index()

        scatter_data = self.peak_scatter.data
        new_x = np.delete(scatter_data["x"], point_index)
        new_y = np.delete(scatter_data["y"], point_index)
        self.peak_scatter.setData(x=new_x, y=new_y)

        self.sig_scatter_data_changed.emit("remove", np.array([point_x], dtype=np.int32))

    @QtCore.Slot(object, object)
    def _on_curve_clicked(
        self, sender: pg.PlotCurveItem, ev: "mouseEvents.MouseClickEvent"
    ) -> None:
        ev.accept()
        if self.signal_curve is None or self.peak_scatter is None:
            return

        click_x = int(ev.pos().x())
        click_y = ev.pos().y()
        x_data = self.signal_curve.xData
        y_data = self.signal_curve.yData
        if x_data is None or y_data is None:
            return

        scatter_search_radius = self.search_around_click_radius

        left_index = np.searchsorted(x_data, click_x - scatter_search_radius, side="left")
        right_index = np.searchsorted(x_data, click_x + scatter_search_radius, side="right")

        valid_x = x_data[left_index:right_index]
        valid_y = y_data[left_index:right_index]

        # Find the index of the nearest extreme point to the click position
        extreme_index = left_index + np.argmin(np.abs(valid_x - click_x))
        extreme_value = valid_y[np.argmin(np.abs(valid_x - click_x))]

        # Find the index of the nearest extreme point to the click position in the y direction
        extreme_index_y = left_index + np.argmin(np.abs(valid_y - click_y))
        extreme_value_y = valid_y[np.argmin(np.abs(valid_y - click_y))]

        # Use the index of the nearest extreme point in the y direction if it is closer to the click position
        if np.abs(extreme_value_y - click_y) < np.abs(extreme_value - click_y):
            extreme_index = extreme_index_y
            extreme_value = extreme_value_y

        if extreme_index in self.peak_scatter.data["x"]:
            return

        x_new, y_new = x_data[extreme_index], extreme_value
        self.peak_scatter.addPoints(x=x_new, y=y_new)
        self.sig_scatter_data_changed.emit("add", np.array([x_new], dtype=np.int32))

    @QtCore.Slot()
    def remove_peaks_in_selection(self) -> None:
        vb: EditingViewBox = self.pw_main.plotItem.vb  # type: ignore
        if vb.mapped_selection_rect is None or self.peak_scatter is None:
            return

        r = vb.mapped_selection_rect
        rx, ry, rw, rh = r.x(), r.y(), r.width(), r.height()

        scatter_x, scatter_y = self.peak_scatter.getData()

        mask = (scatter_x < rx) | (scatter_x > rx + rw) | (scatter_y < ry) | (scatter_y > ry + rh)

        self.peak_scatter.setData(x=scatter_x[mask], y=scatter_y[mask])
        self.sig_scatter_data_changed.emit("remove", scatter_x[~mask].astype(np.int32))
        vb.mapped_selection_rect = None
        vb.selection_box = None

    def get_selection_area(self) -> QtCore.QRectF | None:
        return self.pw_main.plotItem.vb.mapped_selection_rect  # type: ignore

    def draw_rolling_rate(
        self,
        x: npt.NDArray[np.float_],
        y: npt.NDArray[np.float_],
        color: str = "green",
        marker: str = "o",
        linestyle: str | None = None,
        linewidth: int = 2,
        markersize: int = 12,
    ) -> None:
        subplot = self.mpw_result.fig.add_subplot(111)
        subplot.scatter(
            x,
            y,
            color=color,
            marker=marker,  # type: ignore
            linestyle=linestyle,
            linewidth=linewidth,
            markersize=markersize,
        )
        subplot.set_xlabel("Temperature (°C)")
        subplot.set_ylabel("HR (bpm)")
        self.mpw_result.fig.tight_layout()
        self.mpw_result.draw()

    @QtCore.Slot(QtGui.QColor)
    def set_background_color(self, color: QtGui.QColor) -> None:
        self.pw_main.setBackground(color)
        self.pw_rate.setBackground(color)

    @QtCore.Slot(QtGui.QColor)
    def set_foreground_color(self, color: QtGui.QColor) -> None:
        for ax in {"left", "top", "right", "bottom"}:
            edit_axis = self.pw_main.plotItem.getAxis(ax)
            rate_axis = self.pw_rate.plotItem.getAxis(ax)

            if edit_axis.isVisible():
                edit_axis.setPen(color)
                edit_axis.setTextPen(color)
            if rate_axis.isVisible():
                rate_axis.setPen(color)
                rate_axis.setTextPen(color)

    def apply_settings(self) -> None:
        settings = QtCore.QSettings()
        settings.beginGroup("Plot")
        bg_color = settings.value("background_color", type=QtGui.QColor)
        fg_color = settings.value("foreground_color", type=QtGui.QColor)
        point_color = settings.value("point_color", type=QtGui.QColor)
        signal_line_color = settings.value("signal_line_color", type=QtGui.QColor)
        rate_line_color = settings.value("rate_line_color", type=QtGui.QColor)
        section_marker_color = settings.value("section_marker_color", type=QtGui.QColor)
        settings.endGroup()

        self.set_background_color(bg_color)
        self.set_foreground_color(fg_color)
        if self.peak_scatter is not None and isinstance(point_color, QtGui.QColor):
            self.peak_scatter.setBrush(point_color)
        if self.signal_curve is not None and isinstance(signal_line_color, QtGui.QColor):
            self.signal_curve.setPen(color=signal_line_color)
        if self.rate_curve is not None and isinstance(rate_line_color, QtGui.QColor):
            self.rate_curve.setPen(color=rate_line_color)
        for r in self.regions:
            if isinstance(section_marker_color, QtGui.QColor):
                r.setBrush(color=section_marker_color)

    @QtCore.Slot(bool)
    def toggle_auto_scaling(self, state: bool) -> None:
        self.pw_main.enableAutoRange(y=state)
        self.pw_rate.enableAutoRange(y=state)
