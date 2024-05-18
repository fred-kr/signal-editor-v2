import datetime
import typing as t

import numpy as np
import polars as pl
from loguru import logger
from PySide6 import QtCore

from signal_editor.app.utils import human_readable_timedelta

if t.TYPE_CHECKING:
    from .metadata import QFileMetadata


def validate_column(
    col_name: str | None, schema: t.OrderedDict[str, pl.DataType], default: str | None = None
) -> str:
    if not col_name:
        col_name = default
    if col_name not in schema and col_name != "":
        raise ValueError(
            f"Column '{col_name}' not found in data. Available columns: {", ".join(schema.keys())}"
        )
    return col_name


class DataFrameModel(QtCore.QAbstractTableModel):
    def __init__(self, parent: QtCore.QObject | None = None) -> None:
        super().__init__(parent)
        self._metadata: "QFileMetadata | None" = None
        self._df: pl.DataFrame | None = None
        self._schema: t.OrderedDict[str, pl.DataType] | None = None
        self._name_index_column: str = "index"
        self._name_signal_column: str | None = None
        self._name_info_column: str | None = None
        self._float_precision: int = QtCore.QSettings().value(  # type: ignore
            "Misc/float_visual_precision", 4, type=int
        )

    @property
    def df(self) -> pl.DataFrame:
        if self._df is None:
            raise ValueError("Data not loaded yet.")
        return self._df

    # TODO: Can probably be removed
    def set_metadata(self, metadata: "QFileMetadata") -> None:
        self._metadata = metadata
        metadata_dict = metadata.to_dict()
        self._name_signal_column = metadata_dict["signal_column"]
        self._name_info_column = metadata_dict["info_column"]

    def set_float_precision(self, precision: int) -> None:
        self._float_precision = precision
        self.set_dataframe(
            self.df, self._name_signal_column, self._name_index_column, self._name_info_column
        )

    def set_dataframe(
        self,
        data: pl.DataFrame,
        signal_col: str | None = None,
        index_col: str = "index",
        info_col: str | None = None,
    ) -> None:
        self.beginResetModel()
        self._df = data
        self._schema = data.schema

        self._name_signal_column = validate_column(
            signal_col, self._schema, default=self._name_signal_column
        )
        self._name_index_column = validate_column(index_col, self._schema, default="index")

        if not self._schema[self._name_index_column].is_integer():
            logger.info(
                f"Index column '{self._name_index_column}' is not of integer type.\nCreating new index column with name 'index'"
            )
            self._name_index_column = "index"
            if self._name_index_column in self._df.columns:
                self._df.drop_in_place(self._name_index_column)
            self._df = self._df.with_row_index(self._name_index_column)
            self._schema = self._df.schema

        if info_col:
            self._name_info_column = validate_column(info_col, self._schema)

        self.endResetModel()

    def rowCount(
        self, parent: QtCore.QModelIndex | QtCore.QPersistentModelIndex | None = None
    ) -> int:
        return self._df.height if self._df is not None else 0

    def columnCount(
        self, parent: QtCore.QModelIndex | QtCore.QPersistentModelIndex | None = None
    ) -> int:
        return self._df.width if self._df is not None else 0

    def data(
        self,
        index: QtCore.QModelIndex | QtCore.QPersistentModelIndex,
        role: int = QtCore.Qt.ItemDataRole.DisplayRole,
    ) -> t.Any:
        if not index.isValid():
            return None
        if index.row() >= self.rowCount() or index.column() >= self.columnCount():
            return None
        if self._df is None:
            return None

        col_idx = index.column()
        row_idx = index.row()

        col_name = self._df.columns[col_idx]

        value = self._df.item(row_idx, col_idx)
        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            value_type = self._df.schema[col_name]

            if value_type.is_integer():
                return f"{value:_}"
            elif value_type.is_float():
                return np.format_float_positional(
                    value, trim="0", precision=self._float_precision, fractional=True
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

        return None

    def headerData(
        self,
        section: int,
        orientation: QtCore.Qt.Orientation,
        role: int = QtCore.Qt.ItemDataRole.DisplayRole,
    ) -> str | None:
        if role != QtCore.Qt.ItemDataRole.DisplayRole or self._df is None:
            return None
        if orientation != QtCore.Qt.Orientation.Horizontal:
            return None
        name = self._df.columns[section]
        dtype = self._df.schema[name]
        return f"{name}\n---\n{dtype}"
