import datetime
import typing as t

import numpy as np
import polars as pl
from PySide6 import QtCore

from . import ModelIndex
from ..config import Config
from ..utils import human_readable_timedelta


class DataFrameModel(QtCore.QAbstractTableModel):
    def __init__(self, parent: QtCore.QObject | None = None) -> None:
        super().__init__(parent)
        self.df = pl.DataFrame()
        self._float_precision = Config().data.FloatPrecision

    def set_df(self, df: pl.DataFrame) -> None:
        self.beginResetModel()
        self._float_precision = Config().data.FloatPrecision
        self.df = df
        self.endResetModel()

    def rowCount(self, parent: ModelIndex | None = None) -> int:
        return self.df.height

    def columnCount(self, parent: ModelIndex | None = None) -> int:
        return self.df.width

    def data(
        self,
        index: ModelIndex,
        role: int = QtCore.Qt.ItemDataRole.DisplayRole,
    ) -> t.Any:
        if not index.isValid():
            return None
        if index.row() >= self.rowCount() or index.column() >= self.columnCount():
            return None
        if self.df.is_empty():
            return None

        col_idx = index.column()
        row_idx = index.row()

        col_name = self.df.columns[col_idx]

        value = self.df.item(row_idx, col_idx)
        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            value_type = self.df.schema[col_name]

            if value_type.is_integer():
                return f"{value:_}"
            elif value_type.is_float():
                return np.format_float_positional(value, trim="0", precision=self._float_precision, fractional=True)
            elif value_type.is_temporal():
                if isinstance(value, datetime.timedelta):
                    return human_readable_timedelta(value)
                else:
                    return str(value)
            elif value is None:
                return ""
            elif isinstance(value, str) and value.lower() == "nan":
                return "NaN"
            else:
                return str(value)
        elif role == QtCore.Qt.ItemDataRole.UserRole:
            return value
        elif role == QtCore.Qt.ItemDataRole.ToolTipRole:
            return repr(value)

        return None

    def headerData(
        self,
        section: int,
        orientation: QtCore.Qt.Orientation,
        role: int = QtCore.Qt.ItemDataRole.DisplayRole,
    ) -> str | None:
        if self.df.is_empty():
            return None
        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            if orientation == QtCore.Qt.Orientation.Horizontal:
                return self.df.columns[section]
        elif role == QtCore.Qt.ItemDataRole.ToolTipRole:
            if orientation == QtCore.Qt.Orientation.Horizontal:
                return str(self.df.schema[self.df.columns[section]])
        return None

