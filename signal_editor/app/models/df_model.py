import datetime
import typing as t

import numpy as np
import polars as pl
from PySide6 import QtCore, QtWidgets

from ..config import Config
from ..utils import human_readable_timedelta
from . import ModelIndex


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


class LazyDataFrameModel(QtCore.QAbstractTableModel):
    sig_number_populated: t.ClassVar[QtCore.Signal] = QtCore.Signal(int, int, int)

    def __init__(self, batch_size: int = 100, parent: QtCore.QObject | None = None) -> None:
        super().__init__(parent)
        self._df: pl.DataFrame | None = None
        self._rows_loaded: int = 0
        self._batch_size = batch_size

    def rowCount(self, parent: ModelIndex | None = None) -> int:
        return self._rows_loaded if self._df is not None else 0

    def columnCount(self, parent: ModelIndex | None = None) -> int:
        return self._df.width if self._df is not None else 0

    def data(
        self,
        index: ModelIndex,
        role: int = QtCore.Qt.ItemDataRole.DisplayRole,
    ) -> t.Any:
        if not index.isValid() or self._df is None:
            return None

        row, col = index.row(), index.column()
        if row >= self._rows_loaded or row < 0 or col >= self._df.width or col < 0:
            return None

        value = self._df.item(row, col)
        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            col_name = self._df.columns[col]
            value_type = self._df.schema[col_name]

            if value_type.is_integer():
                return f"{value:_}"
            elif value_type.is_float():
                return np.format_float_positional(
                    value, trim="0", precision=Config().data.FloatPrecision, fractional=True
                )
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
        elif role == QtCore.Qt.ItemDataRole.BackgroundRole:
            batch = row // self._batch_size
            palette = QtWidgets.QApplication.palette()
            return palette.base() if batch % 2 == 0 else palette.alternateBase()

        return None

    def headerData(
        self,
        section: int,
        orientation: QtCore.Qt.Orientation,
        role: int = QtCore.Qt.ItemDataRole.DisplayRole,
    ) -> str | None:
        if role != QtCore.Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == QtCore.Qt.Orientation.Horizontal and self._df is not None:
            return self._df.columns[section]
        return str(section + 1)

    def canFetchMore(self, parent: ModelIndex) -> bool:
        return False if self._df is None else self._rows_loaded < self._df.height

    def fetchMore(self, parent: ModelIndex) -> None:
        if self._df is None:
            return
        start = self._rows_loaded
        total = self._df.height
        remainder = total - start
        rows_to_fetch = min(self._batch_size, remainder)

        self.beginInsertRows(QtCore.QModelIndex(), start, start + rows_to_fetch - 1)
        self._rows_loaded += rows_to_fetch
        self.endInsertRows()
        self.sig_number_populated.emit(start, rows_to_fetch, total)

    @QtCore.Slot(object)
    def set_df(self, df: pl.DataFrame) -> None:
        self.beginResetModel()
        self._df = df
        self._rows_loaded = 0
        self.endResetModel()
