import os
import typing as t
from types import NoneType

import attrs
from attr._make import Factory
from loguru import logger
from PySide6 import QtCore, QtGui

from . import ModelIndex, ItemDataRole
from ..config import Config
from ..enum_defs import RateComputationMethod, SVGColors, TextFileSeparator


_ConfigType = t.Union[
    QtGui.QColor, int, bool, RateComputationMethod, TextFileSeparator, str, None, list[str], QtCore.QByteArray
]


@attrs.define
class ItemData:
    """
    A data structure to store the data for a single item in the tree model.
    """

    name: str = attrs.field(default="")
    value: _ConfigType = attrs.field(
        default=None,
        validator=attrs.validators.instance_of(
            (QtGui.QColor, int, bool, RateComputationMethod, TextFileSeparator, str, NoneType, list, QtCore.QByteArray)
        ),
    )
    description: str | None = attrs.field(default=None)
    default_value: _ConfigType = attrs.field(
        default=None,
        validator=attrs.validators.instance_of(
            (
                QtGui.QColor,
                int,
                bool,
                RateComputationMethod,
                TextFileSeparator,
                str,
                NoneType,
                list,
                QtCore.QByteArray,
                Factory,
            )
        ),
    )


class ConfigItem:
    "Class representing a config item in a tree model"

    def __init__(self, data: ItemData, parent: "ConfigItem | None" = None, _allow_edits: bool | None = None) -> None:
        self.item_data = data
        self.parent_item = parent
        self.child_items: list[ConfigItem] = []
        self._allow_edits = _allow_edits

    @property
    def full_path(self) -> str:
        if self.parent_item is None:
            return self.name
        return f"{self.parent_item.full_path}.{self.name}"

    @property
    def category(self) -> str | None:
        if self.parent_item and self.parent_item.name in {
            "Plot",
            "Data",
            "Editing",
            "Internal",
        }:
            return self.parent_item.name
        return None

    @property
    def name(self) -> str:
        return self.item_data.name

    @name.setter
    def name(self, value: str) -> None:
        self.item_data.name = value

    @property
    def value(self) -> _ConfigType:
        return self.item_data.value

    @value.setter
    def value(self, value: _ConfigType) -> None:
        self.item_data.value = value

    @property
    def description(self) -> str | None:
        return self.item_data.description

    @description.setter
    def description(self, value: str | None) -> None:
        self.item_data.description = value

    @property
    def default_value(self) -> _ConfigType:
        return self.item_data.default_value

    def is_editable(self) -> bool:
        if self._allow_edits is not None:
            return self._allow_edits
        return self.value is not None and self.description != ""

    def child(self, number: int) -> "ConfigItem | None":
        if 0 <= number < len(self.child_items):
            return self.child_items[number]
        return None

    def child_count(self) -> int:
        return len(self.child_items)

    def child_number(self) -> int:
        if self.parent_item is not None:
            return self.parent_item.child_items.index(self)
        return 0

    def column_count(self) -> int:
        return 3

    def parent(self) -> "ConfigItem | None":
        return self.parent_item

    @logger.catch(message="Error setting config value")
    def set_value(self, value: _ConfigType) -> bool:
        if self.value == value:
            return False

        self.value = value
        Config().update_value(self.category, self.name, value)
        return True

    def reset_to_default(self) -> bool:
        if self.value == self.default_value:
            return False
        if isinstance(self.default_value, Factory):
            default_value = self.default_value.factory()  # type: ignore
        else:
            default_value = self.default_value

        self.value = default_value
        Config().update_value(self.category, self.name, default_value)
        return True

    def __repr__(self) -> str:
        parts = [f"<config_tree_model.TreeItem at 0x{id(self):x}>\n"]
        parts.extend(f' "{d}"' if d else " <None>" for d in [self.name, self.value, self.description])
        parts.append(f", {len(self.child_items)} children")
        return "".join(parts)


class ConfigModel(QtCore.QAbstractItemModel):
    def __init__(self, parent: QtCore.QObject | None = None) -> None:
        super().__init__(parent)
        self._config = Config()
        self._headers = ["Name", "Value", "Description"]
        self.root_item = ConfigItem(ItemData("Name", "Value", "Description"))

        self._plot_root = ConfigItem(ItemData("Plot", None, None), self.root_item)
        self._editing_root = ConfigItem(ItemData("Editing", None, None), self.root_item)
        self._data_root = ConfigItem(ItemData("Data", None, None), self.root_item)

        self.root_item.child_items.extend([self._plot_root, self._editing_root, self._data_root])

        include_internal = os.environ.get("DEBUG", "0") == "1"
        self.setup_model_data(include_internal=include_internal)

    def columnCount(self, parent: ModelIndex | None = None) -> int:
        return self.root_item.column_count()

    def data(self, index: ModelIndex, role: int | None = None) -> t.Any:
        if not index.isValid():
            return None

        col = index.column()
        item = self.get_item(index)

        if role == ItemDataRole.DisplayRole:
            if col == 0:
                return item.name
            elif col == 1:
                if isinstance(item.value, QtGui.QColor):
                    return SVGColors(item.value.name()).name
                elif isinstance(item.value, (TextFileSeparator, RateComputationMethod)):
                    return item.value.name
                elif isinstance(item.value, bool) or item.value is None:
                    return ""
                elif isinstance(item.value, QtCore.QByteArray):
                    return "<Binary data>"
                elif isinstance(item.value, list):
                    return ", ".join(str(v) for v in item.value)

                return str(item.value)
            elif col == 2:
                desc = item.description
                return "" if desc is None else desc
        elif role == ItemDataRole.UserRole:
            if col == 0:
                return item.name
            elif col == 1:
                return item.value
            elif col == 2:
                return item.description
        elif role == ItemDataRole.DecorationRole:
            if col == 1 and isinstance(item.value, QtGui.QColor):
                return item.value
        elif role == ItemDataRole.EditRole:
            if col == 1:
                return item.value
        elif role == ItemDataRole.CheckStateRole:
            if col == 1 and isinstance(item.value, bool):
                return QtCore.Qt.CheckState.Checked if item.value else QtCore.Qt.CheckState.Unchecked
        elif role == ItemDataRole.SizeHintRole:
            if col == 0:
                return QtCore.QSize(150, 31)
            elif col == 1:
                return QtCore.QSize(180, 31)
            elif col == 2:
                return QtCore.QSize(250, 31)
        elif role == QtCore.Qt.ItemDataRole.ToolTipRole:
            if isinstance(item.value, QtCore.QByteArray):
                return str(item.value)
            elif isinstance(item.value, list):
                return "\n".join(str(v) for v in item.value)
            else:
                return item.description or ""

        return None

    def setData(self, index: ModelIndex, value: _ConfigType, role: int = ItemDataRole.EditRole) -> bool:
        if (
            role not in {ItemDataRole.EditRole, ItemDataRole.UserRole, ItemDataRole.CheckStateRole}
            or not index.isValid()
        ):
            return False

        col = index.column()
        if col != 1:
            return False

        item = self.get_item(index)

        if isinstance(value, QtCore.Qt.CheckState):
            value = value == QtCore.Qt.CheckState.Checked

        result = item.set_value(value)
        if result:
            self.dataChanged.emit(index, index)

        return result

    def flags(self, index: ModelIndex) -> QtCore.Qt.ItemFlag:
        if not index.isValid():
            return QtCore.Qt.ItemFlag.NoItemFlags
        flags = QtCore.QAbstractItemModel.flags(self, index)

        if index.column() == 1:
            item = self.get_item(index)
            if item.is_editable():
                flags |= QtCore.Qt.ItemFlag.ItemIsEditable
            if isinstance(item.value, bool):
                flags |= QtCore.Qt.ItemFlag.ItemIsUserCheckable

        return flags

    def get_item(self, index: ModelIndex) -> ConfigItem:
        if index.isValid():
            if item := index.internalPointer():
                return item

        return self.root_item

    def headerData(
        self, section: int, orientation: QtCore.Qt.Orientation, role: int = ItemDataRole.DisplayRole
    ) -> t.Any:
        if orientation == QtCore.Qt.Orientation.Horizontal and role == ItemDataRole.DisplayRole:
            return self._headers[section]
        return None

    def index(self, row: int, column: int, parent: ModelIndex | None = None) -> QtCore.QModelIndex:
        if parent is None:
            parent = QtCore.QModelIndex()

        if parent.isValid() and parent.column() != 0:
            return QtCore.QModelIndex()

        if parent_item := self.get_item(parent):
            return (
                self.createIndex(row, column, child_item)
                if (child_item := parent_item.child(row))
                else QtCore.QModelIndex()
            )
        else:
            return QtCore.QModelIndex()

    def parent(self, index: ModelIndex | None = None) -> QtCore.QModelIndex:  # type: ignore
        if index is None:
            index = QtCore.QModelIndex()

        if not index.isValid():
            return QtCore.QModelIndex()

        if child_item := self.get_item(index):
            parent_item = child_item.parent()
        else:
            parent_item = None

        if parent_item == self.root_item or not parent_item:
            return QtCore.QModelIndex()

        return self.createIndex(parent_item.child_number(), 0, parent_item)

    def rowCount(self, parent: ModelIndex | None = None) -> int:
        if parent is None:
            parent = QtCore.QModelIndex()

        if parent.isValid() and parent.column() > 0:
            return 0

        parent_item = self.get_item(parent)
        return parent_item.child_count() if parent_item else 0

    def setup_model_data(self, include_internal: bool = False) -> None:
        for field in attrs.fields(self._config.plot.__class__):
            self._plot_root.child_items.append(
                ConfigItem(
                    ItemData(
                        field.name,
                        getattr(self._config.plot, field.name),
                        field.metadata.get("Description", None),
                        field.default,
                    ),
                    self._plot_root,
                )
            )

        for field in attrs.fields(self._config.editing.__class__):
            self._editing_root.child_items.append(
                ConfigItem(
                    ItemData(
                        field.name,
                        getattr(self._config.editing, field.name),
                        field.metadata.get("Description", None),
                        field.default,
                    ),
                    self._editing_root,
                )
            )

        for field in attrs.fields(self._config.data.__class__):
            self._data_root.child_items.append(
                ConfigItem(
                    ItemData(
                        field.name,
                        getattr(self._config.data, field.name),
                        field.metadata.get("Description", None),
                        field.default,
                    ),
                    self._data_root,
                )
            )

        if include_internal:
            self._internal_root = ConfigItem(ItemData("Internal", None, None), self.root_item)
            self.root_item.child_items.append(self._internal_root)

            for field in attrs.fields(self._config.internal.__class__):
                self._internal_root.child_items.append(
                    ConfigItem(
                        ItemData(
                            field.name,
                            getattr(self._config.internal, field.name),
                            field.metadata.get("Description", None),
                            field.default,
                        ),
                        self._internal_root,
                        field.metadata.get("allow_user_edits", False),
                    )
                )

    def __repr__(self) -> str:
        return f"<config_tree_model.ConfigTreeModel at 0x{id(self):x}>"

    def restore_defaults(self) -> None:
        self.beginResetModel()
        for item in self._plot_root.child_items:
            item.reset_to_default()
        for item in self._editing_root.child_items:
            item.reset_to_default()
        for item in self._data_root.child_items:
            item.reset_to_default()
        if hasattr(self, "_internal_root"):
            for item in self._internal_root.child_items:
                item.reset_to_default()
        self.endResetModel()

    def reset_item(self, index: ModelIndex) -> bool:
        item = self.get_item(index)
        result = item.reset_to_default()
        if result:
            self.dataChanged.emit(index, index)

        return result
