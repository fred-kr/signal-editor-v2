import typing as t

import numpy as np
import numpy.typing as npt
import pyqtgraph as pg
from pyqtgraph.widgets.MatplotlibWidget import MatplotlibWidget
from PySide6 import QtCore

from ..gui.plot_items import CustomScatterPlotItem, PlotDataItem, TimeAxisItem
from ..gui.plot_items.editing_view_box import EditingViewBox
from .config_controller import ConfigController as Config

if t.TYPE_CHECKING:
    from pyqtgraph.GraphicsScene import mouseEvents


class PlotController(QtCore.QObject):
    sig_scatter_data_changed = QtCore.Signal(str, object)

    def __init__(self, parent: QtCore.QObject | None = None) -> None:
        super().__init__(parent)

        self._regions: list[pg.LinearRegionItem] = []
        self.setup_widgets()
        self.setup_plot_items()

    def setup_widgets(self) -> None:
        editing_vb = EditingViewBox(name="main_plot")
        rate_vb = pg.ViewBox(name="rate_plot")
        for vb in (editing_vb, rate_vb):
            vb.enableAutoRange("y")
            vb.setAutoVisible(y=True)
        editing_vb.setXLink("rate_plot")

        editing_plt = pg.PlotItem(
            viewBox=editing_vb, axisItems={"top": TimeAxisItem(orientation="top")}
        )
        rate_plt = pg.PlotItem(viewBox=rate_vb, axisItems={"top": TimeAxisItem(orientation="top")})
        for plt in (editing_plt, rate_plt):
            plt.showGrid(x=False, y=True)
            plt.setClipToView(True)
            plt.addLegend(colCount=2)
            plt.addLegend().anchor(itemPos=(0, 1), parentPos=(0, 1), offset=(5, -5))

            # ? Maybe better in main controller
            # plt.scene().sigMouseMoved.connect(self._on_mouse_moved)

        self.pw_editing = pg.PlotWidget(plotItem=editing_plt)
        self.pw_rate = pg.PlotWidget(plotItem=rate_plt)
        self.pw_mpl = MatplotlibWidget()

    def setup_plot_items(self) -> None:
        self.signal_curve = self._create_signal_curve()
        self.peak_scatter = self._create_peak_scatter()
        self.peak_scatter.setZValue(60)
        self.mpl_fig = self.pw_mpl.fig
        self.mpl_fig.tight_layout()

        self.rate_curve = PlotDataItem()

        self._region_selector = pg.LinearRegionItem(
            brush=(0, 200, 100, 75),
            pen=(255, 255, 255, 255),
            hoverBrush=(0, 200, 100, 30),
            hoverPen={"color": "gray", "width": 2},
        )
        self._region_selector.setZValue(1e3)
        for line in self._region_selector.lines:
            line.addMarker("<|>", position=0.5, size=12)

        self._temperature_label = pg.LabelItem("Temperature: - °C", parent=self.pw_editing.plotItem)
        self._bpm_label = pg.LabelItem("HR: - bpm", parent=self.pw_rate.plotItem)

    def _create_signal_curve(self) -> PlotDataItem:
        pdi = PlotDataItem(
            pen="lightgray",
            skipFiniteCheck=True,
            autoDownsample=True,
            name="Signal",
            clickable=True,
        )
        pdi.sigClicked.connect(self._on_curve_clicked)
        pdi.sigPlotChanged.connect(self.set_view_limits)
        return pdi

    def _create_peak_scatter(self) -> CustomScatterPlotItem:
        spi = CustomScatterPlotItem(
            pxMode=True,
            size=10,
            pen=None,
            brush="darkgoldenrod",
            useCache=True,
            name="Peaks",
            hoverable=True,
            hoverPen="black",
            hoverSymbol="x",
            hoverBrush="red",
            hoverSize=15,
            tip=None,
        )
        spi.setZValue(60)
        spi.sigClicked.connect(self._on_scatter_clicked)
        spi.sigPlotChanged.connect(self._on_scatter_changed)
        return spi

    @QtCore.Slot(int)
    def reset_view_range(self, upper_bound: int) -> None:
        self.pw_editing.plotItem.vb.setRange(xRange=(0, upper_bound), disableAutoRange=False)
        self.pw_rate.plotItem.vb.setRange(xRange=(0, upper_bound), disableAutoRange=False)

    @QtCore.Slot(object)
    def set_view_limits(self, plt_data_item: PlotDataItem) -> None:
        if plt_data_item.xData is None or plt_data_item.xData.size == 0:
            return
        len_data = plt_data_item.xData.size
        self.pw_editing.plotItem.vb.setLimits(
            xMin=-0.25 * len_data, xMax=1.25 * len_data, maxYRange=1e5, minYRange=0.1
        )
        self.pw_rate.plotItem.vb.setLimits(
            xMin=-0.25 * len_data, xMax=1.25 * len_data, maxYRange=1e5, minYRange=0.1
        )
        self.reset_view_range(len_data)

    def reset(self) -> None:
        self.pw_editing.plotItem.clear()
        if self.pw_editing.plotItem.legend:
            self.pw_editing.plotItem.legend.clear()
        self.pw_rate.plotItem.clear()
        if self.pw_rate.plotItem.legend:
            self.pw_rate.plotItem.legend.clear()

        self.pw_mpl.fig.clear()

        self.signal_curve.clear()
        self.peak_scatter.clear()
        self.rate_curve.clear()

        if self._region_selector is not None:
            self._region_selector.setParent(None)
        self._region_selector = None

        if self._temperature_label is not None:
            self._temperature_label.setParent(None)
        self._temperature_label = None

        if self._bpm_label is not None:
            self._bpm_label.setParent(None)
        self._bpm_label = None

        self.clear_regions()
        self.setup_plot_items()

    @QtCore.Slot(bool)
    def toggle_regions(self, visible: bool) -> None:
        for region in self._regions:
            region.setVisible(visible)

    def remove_region(
        self, region: pg.LinearRegionItem | None = None, bounds: tuple[float, float] | None = None
    ) -> None:
        if region is not None:
            self._regions.remove(region)
        if bounds is not None:
            self._regions = [r for r in self._regions if r.getRegion() != bounds]
        if self._region_selector is not None:
            self._region_selector.setParent(None)
        self._region_selector = None

    def clear_regions(self) -> None:
        for region in self._regions:
            region.setParent(None)
            if region in self.pw_editing.plotItem.items:
                self.pw_editing.plotItem.removeItem(region)
        self._regions = []

    def show_region_selector(self, initial_region: tuple[float, float]) -> None:
        if not self._region_selector:
            return

        self._region_selector.setRegion(initial_region)
        if self._region_selector not in self.pw_editing.plotItem.items:
            self.pw_editing.plotItem.addItem(self._region_selector)

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
        if not Config().plot.show_regions:
            marked_region.setVisible(False)
        marked_region.setZValue(10)
        self._regions.append(marked_region)
        self.pw_editing.plotItem.addItem(marked_region)
        self.hide_region_selector()

    def draw_signal(self, y_data: npt.NDArray[np.float_], clear: bool = True) -> None:
        if clear:
            self.pw_editing.plotItem.clear()
            self.pw_rate.plotItem.clear()

        self.signal_curve.setData(y_data)

    def draw_rate(self, y_data: npt.NDArray[np.float_], clear: bool = True) -> None:
        if clear:
            self.pw_rate.plotItem.clear()
        self.rate_curve.setData(y_data)

    def draw_peaks(
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
        scatter_search_radius = Config().plot.scatter_search_radius

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
        vb: EditingViewBox = self.pw_editing.plotItem.vb
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
        return self.pw_editing.plotItem.vb.mapped_selection_rect

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
        subplot = self.mpl_fig.add_subplot(111)
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
        self.mpl_fig.tight_layout()
        self.pw_mpl.draw()
