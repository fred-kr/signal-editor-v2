from pyqtgraph import AxisItem


class TimeAxisItem(AxisItem):
    """
    Custom `pyqtgraph.AxisItem` subclass for displaying millisecond timestamps in a human readable format.
    """

    def tickStrings(self, values: list[float], scale: float, spacing: float) -> list[str]:
        strings: list[str] = []
        for v in values:
            vs = v * scale
            minutes, seconds = divmod(int(vs), 60)
            hours, minutes = divmod(minutes, 60)
            vstr = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            strings.append(vstr)
        return strings
