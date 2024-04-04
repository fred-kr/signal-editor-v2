import typing as t

import numpy as np
import numpy.typing as npt
import pyqtgraph as pg
from pyqtgraph.widgets.MatplotlibWidget import MatplotlibWidget
from PySide6 import QtCore, QtGui

from .. import type_defs as _t
from ..gui.plot_items import CustomScatterPlotItem, PlotDataItem
from ..gui.plot_items.editing_view_box import EditingViewBox
from ..gui.plot_items.time_axis_item import TimeAxisItem

if t.TYPE_CHECKING:
    from pyqtgraph.GraphicsScene import mouseEvents


class PlotController(QtCore.QObject):
    sig_scatter_data_changed = QtCore.Signal(str, object)

    def __init__(
        self,
        parent: QtCore.QObject | None,
        graphics_layout_widget: pg.GraphicsLayoutWidget,
        plt_mpl: MatplotlibWidget,
    ) -> None:
        super().__init__(parent)

        self._peak_search_radius_changed = False
        self._line_click_width_changed = False
        self.regions: list[pg.LinearRegionItem] = []
        self._show_regions = False
        self.setup_plot_items(graphics_layout_widget, plt_mpl)
        self.setup_plot_data_items()

    def setup_plot_items(
        self, graphics_layout_widget: pg.GraphicsLayoutWidget, plt_mpl: MatplotlibWidget
    ) -> None:
        plt_editing = graphics_layout_widget.addPlot(
            0,
            0,
            viewBox=EditingViewBox(name="plt_editing"),
            axisItems={"top": TimeAxisItem(orientation="top")},
        )
        plt_rate = graphics_layout_widget.addPlot(
            1,
            0,
            viewBox=pg.ViewBox(name="plt_rate"),
            axisItems={"top": TimeAxisItem(orientation="top")},
        )
        editing_vb = plt_editing.getViewBox()
        rate_vb = plt_rate.getViewBox()
        for vb in (editing_vb, rate_vb):
            vb.enableAutoRange("y")
            vb.setAutoVisible(y=True)
            vb.setMouseEnabled(x=True, y=False)
        editing_vb.setXLink("plt_rate")

        for plt in (plt_editing, plt_rate):
            plt.showGrid(x=False, y=True)
            plt.setClipToView(True)
            plt.addLegend(colCount=2)
            plt.addLegend().anchor(itemPos=(0, 1), parentPos=(0, 1), offset=(5, -5))

            # ? Maybe better in main controller
            # plt.scene().sigMouseMoved.connect(self._on_mouse_moved)

        self.plt_editing = plt_editing
        self.plt_rate = plt_rate
        self.plt_mpl = plt_mpl
        settings = QtCore.QSettings()
        self._graphics_layout_widget = graphics_layout_widget
        self.set_background_color(settings.value("Plot/background_color"))
        self.set_foreground_color(settings.value("Plot/foreground_color"))

    def setup_plot_data_items(self) -> None:
        settings = QtCore.QSettings()
        self.signal_curve = self._initialize_signal_curve(
            pen_color=settings.value("Plot/signal_line_color")
        )
        self.peak_scatter = self._initialize_peak_scatter(
            brush_color=settings.value("Plot/point_color")
        )
        self.peak_scatter.setZValue(60)
        self.plt_mpl.fig.tight_layout()

        self.rate_curve = self._initialize_rate_curve(pen_color=settings.value("Plot/rate_line_color"))

        self._region_selector = pg.LinearRegionItem(
            brush=settings.value("Plot/section_marker_color"),
            pen=(255, 255, 255, 255),
            hoverBrush=(0, 200, 100, 30),
            hoverPen={"color": "gray", "width": 2},
        )
        self._region_selector.setZValue(1e3)
        for line in self._region_selector.lines:
            line.addMarker("<|>", position=0.5, size=12)

        # TODO: Find a better way to convey this information
        # self._temperature_label = pg.LabelItem("Temperature: - °C", parent=self.plt_editing)
        # self._bpm_label = pg.LabelItem("HR: - bpm", parent=self.plt_rate)

    def _initialize_signal_curve(self, pen_color: _t.PGColor = "lightgray") -> PlotDataItem:
        signal = PlotDataItem(
            pen=pen_color,
            skipFiniteCheck=True,
            autoDownsample=True,
            name="Signal",
            clickable=True,
        )
        signal.sigClicked.connect(self._on_curve_clicked)
        signal.sigPlotChanged.connect(self.set_view_limits)
        return signal

    def _initialize_peak_scatter(
        self,
        brush_color: _t.PGColor = "darkgoldenrod",
        hover_pen: _t.PGColor = "black",
        hover_brush: _t.PGColor = "red",
    ) -> CustomScatterPlotItem:
        scatter = CustomScatterPlotItem(
            pxMode=True,
            size=10,
            pen=None,
            brush=brush_color,
            useCache=True,
            name="Peaks",
            hoverable=True,
            hoverPen=hover_pen,
            hoverSymbol="x",
            hoverBrush=hover_brush,
            hoverSize=15,
            tip=None,
        )
        scatter.setZValue(60)
        scatter.sigClicked.connect(self._on_scatter_clicked)
        scatter.sigPlotChanged.connect(self._on_scatter_changed)
        return scatter

    def _initialize_rate_curve(self, pen_color: _t.PGColor = "green") -> PlotDataItem:
        return PlotDataItem(
            pen=pen_color,
            skipFiniteCheck=True,
            autoDownsample=True,
            name="Rate",
        )

    @QtCore.Slot(int)
    def reset_view_range(self, upper_bound: int) -> None:
        self.plt_editing.vb.setRange(xRange=(0, upper_bound), disableAutoRange=False)
        self.plt_rate.vb.setRange(xRange=(0, upper_bound), disableAutoRange=False)

    @QtCore.Slot(object)
    def set_view_limits(self, plt_data_item: PlotDataItem) -> None:
        if plt_data_item.xData is None or plt_data_item.xData.size == 0:
            return
        len_data = plt_data_item.xData.size
        self.plt_editing.vb.setLimits(
            xMin=-0.25 * len_data, xMax=1.25 * len_data, maxYRange=1e5, minYRange=0.1
        )
        self.plt_rate.vb.setLimits(
            xMin=-0.25 * len_data, xMax=1.25 * len_data, maxYRange=1e5, minYRange=0.1
        )
        self.reset_view_range(len_data)

    def reset(self) -> None:
        self.plt_editing.clear()
        if self.plt_editing.legend:
            self.plt_editing.legend.clear()
        self.plt_rate.clear()
        if self.plt_rate.legend:
            self.plt_rate.legend.clear()

        self.plt_mpl.fig.clear()

        self.signal_curve.clear()
        self.peak_scatter.clear()
        self.rate_curve.clear()

        if self._region_selector is not None:
            self._region_selector.setParent(None)
        self._region_selector = None

        # if self._temperature_label is not None:
        #     self._temperature_label.setParent(None)
        # self._temperature_label = None

        # if self._bpm_label is not None:
        #     self._bpm_label.setParent(None)
        # self._bpm_label = None

        self.clear_regions()
        self.setup_plot_data_items()

    @QtCore.Slot(bool)
    def toggle_regions(self, visible: bool) -> None:
        for region in self.regions:
            region.setVisible(visible)
        self._show_regions = visible

    def remove_region(
        self, region: pg.LinearRegionItem | None = None, bounds: tuple[float, float] | None = None
    ) -> None:
        if region is not None:
            self.regions.remove(region)
        if bounds is not None:
            self.regions = [r for r in self.regions if r.getRegion() != bounds]
        if self._region_selector is not None:
            self._region_selector.setParent(None)
        self._region_selector = None

    def clear_regions(self) -> None:
        for region in self.regions:
            region.setParent(None)
            if region in self.plt_editing.items:
                self.plt_editing.removeItem(region)
        self.regions = []

    def show_region_selector(self, initial_region: tuple[float, float]) -> None:
        if not self._region_selector:
            return

        self._region_selector.setRegion(initial_region)
        if self._region_selector not in self.plt_editing.items:
            self.plt_editing.addItem(self._region_selector)

        self._region_selector.setVisible(True)

    def hide_region_selector(self) -> None:
        if self._region_selector:
            self._region_selector.setVisible(False)

    @QtCore.Slot(int, int)
    def mark_region(self, x1: int, x2: int) -> None:
        r, g, b = 0, 200, 100
        marked_region = pg.LinearRegionItem(
            values=(x1, x2),
            brush=(r, g, b, 50),
            pen=pg.mkPen(color=(r, g, b, 255), width=2, style=QtCore.Qt.PenStyle.DashLine),
            movable=False,
        )
        if self._show_regions:
            marked_region.setVisible(False)
        marked_region.setZValue(10)
        self.regions.append(marked_region)
        self.plt_editing.addItem(marked_region)
        self.hide_region_selector()

    def set_signal_data(self, y_data: npt.NDArray[np.float_], clear: bool = True) -> None:
        if clear:
            self.plt_editing.clear()
            self.plt_rate.clear()

        self.signal_curve.setData(y_data)

    def set_rate_data(self, y_data: npt.NDArray[np.float_], clear: bool = True) -> None:
        if clear:
            self.plt_rate.clear()
        self.rate_curve.setData(y_data)

    def set_peak_data(
        self, x_data: npt.NDArray[np.intp | np.uintp], y_data: npt.NDArray[np.float_]
    ) -> None:
        self.peak_scatter.setData(x=x_data, y=y_data)

    @QtCore.Slot(object, object, object)
    def _on_scatter_clicked(
        self,
        sender: CustomScatterPlotItem,
        points: t.Sequence[pg.SpotItem],
        ev: "mouseEvents.MouseClickEvent",
    ) -> None:
        """
        Slot that is called when a spot item of a scatter plot item is clicked. Removes the spot
        item from the scatter plot item and updates the peak scatter plot item.

        Parameters
        ----------
        sender : CustomScatterPlotItem
            The scatter plot item that was clicked.
        points : t.Sequence[pg.SpotItem]
            An array of spot items under the cursor at the time of the click.
        ev : mouseEvents.MouseClickEvent
            The mouse click event holding information about the click and its position.
        """
        ev.accept()

        point = points[0]
        point_x = point.pos().toQPoint()
        point_index = point.index()

        scatter_data = self.peak_scatter.data
        new_x = np.delete(scatter_data["x"], point_index)
        new_y = np.delete(scatter_data["y"], point_index)
        self.peak_scatter.setData(x=new_x, y=new_y)

        self.sig_scatter_data_changed.emit("r", point_x)

    @QtCore.Slot(object, object)
    def _on_curve_clicked(
        self, sender: pg.PlotCurveItem, ev: "mouseEvents.MouseClickEvent"
    ) -> None:
        ev.accept()

        click_x = ev.pos().x()
        click_y = ev.pos().y()
        x_data = self.signal_curve.xData
        y_data = self.signal_curve.yData
        if not x_data or not y_data:
            return
        settings = QtCore.QSettings()
        scatter_search_radius = t.cast(int, settings.value("Editing/search_around_click_radius"))

        left_index = np.searchsorted(x_data, click_x - scatter_search_radius, side="left")
        right_index = np.searchsorted(x_data, click_x + scatter_search_radius, side="right")

        valid_x_values = x_data[left_index:right_index]
        valid_y_values = y_data[left_index:right_index]

        extreme_index = left_index + np.argmin(np.abs(valid_x_values - click_x))
        extreme_value = valid_y_values[np.argmin(np.abs(valid_x_values - click_x))]

        y_extreme_index = left_index + np.argmin(np.abs(valid_y_values - click_y))
        y_extreme_value = valid_y_values[np.argmin(np.abs(valid_y_values - click_y))]

        if np.abs(y_extreme_value - click_y) < np.abs(extreme_value - click_y):
            extreme_index = y_extreme_index
            extreme_value = y_extreme_value

        if extreme_index in self.peak_scatter.data["x"]:
            return

        x_new, y_new = x_data[extreme_index], extreme_value
        self.peak_scatter.addPoints(x=x_new, y=y_new)

        self.sig_scatter_data_changed.emit("a", x_new)

    @QtCore.Slot()
    def _on_remove_selection(self) -> None:
        vb = t.cast(EditingViewBox, self.plt_editing.vb)
        if vb.mapped_selection_rect is None:
            return

        r = vb.mapped_selection_rect
        rx, ry, rw, rh = r.x(), r.y(), r.width(), r.height()

        scatter_x, scatter_y = self.peak_scatter.getData()

        mask = (scatter_x < rx) | (scatter_x > rx + rw) | (scatter_y < ry) | (scatter_y > ry + rh)

        self.peak_scatter.setData(x=scatter_x[mask], y=scatter_y[mask])
        self.sig_scatter_data_changed.emit("r", scatter_x[~mask].astype(np.int32))
        vb.mapped_selection_rect = None
        vb.selection_box = None

    @QtCore.Slot(object)
    def _on_scatter_changed(self, sender: CustomScatterPlotItem) -> None:
        self.sig_scatter_data_changed.emit("n", sender)

    def get_selection_area(self) -> QtCore.QRectF | None:
        return self.plt_editing.vb.mapped_selection_rect  # pyright: ignore[reportAttributeAccessIssue, reportUnknownVariableType]

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
        subplot = self.plt_mpl.fig.add_subplot(111)
        subplot.scatter(
            x,
            y,
            color=color,
            marker=marker,
            linestyle=linestyle,
            linewidth=linewidth,
            markersize=markersize,
        )
        subplot.set_xlabel("Temperature (°C)")
        subplot.set_ylabel("HR (bpm)")
        self.plt_mpl.fig.tight_layout()
        self.plt_mpl.draw()

    @QtCore.Slot(QtGui.QColor)
    def set_background_color(self, color: QtGui.QColor) -> None:
        self._graphics_layout_widget.setBackground(color)

    @QtCore.Slot(QtGui.QColor)
    def set_foreground_color(self, color: QtGui.QColor) -> None:
        for ax in {"left", "top", "right", "bottom"}:
            edit_axis = self.plt_editing.getAxis(ax)
            rate_axis = self.plt_rate.getAxis(ax)

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
        self.peak_scatter.setBrush(color=point_color)
        self.signal_curve.setPen(color=signal_line_color)
        self.rate_curve.setPen(color=rate_line_color)
        for r in self.regions:
            r.setBrush(color=section_marker_color)
