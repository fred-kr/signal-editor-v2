"""
Taken from the PySide6 'Settings Editor Example', see:
https://doc.qt.io/qtforpython-6/examples/example_corelib_settingseditor.html
"""

import typing as t

from PySide6 import QtCore, QtGui


class TypeChecker:
    """
    A class that provides type checking and conversion functionality for various data types.
    """

    def __init__(self) -> None:
        self.bool_expr = QtCore.QRegularExpression("^(true)|(false)$")
        assert self.bool_expr.isValid()
        self.bool_expr.setPatternOptions(
            QtCore.QRegularExpression.PatternOption.CaseInsensitiveOption
        )

        self.byte_array_expr = QtCore.QRegularExpression(r"^[\x00-\xff]*$")
        assert self.byte_array_expr.isValid()

        self.char_expr = QtCore.QRegularExpression("^.$")
        assert self.char_expr.isValid()

        self.int_expr = QtCore.QRegularExpression(r"^[+-]?\d+$")
        assert self.int_expr.isValid()

        self.color_expr = QtCore.QRegularExpression(r"^\(([0-9]*),([0-9]*),([0-9]*),([0-9]*)\)$")
        assert self.color_expr.isValid()

        self.point_expr = QtCore.QRegularExpression(r"^\((-?[0-9]*),(-?[0-9]*)\)$")
        assert self.point_expr.isValid()

        self.rect_expr = QtCore.QRegularExpression(
            r"^\((-?[0-9]*),(-?[0-9]*),(-?[0-9]*),(-?[0-9]*)\)$"
        )
        assert self.rect_expr.isValid()

        self.size_expr = QtCore.QRegularExpression(self.point_expr)

        date_pattern = "([0-9]{,4})-([0-9]{,2})-([0-9]{,2})"
        self.date_expr = QtCore.QRegularExpression(f"^{date_pattern}$")
        assert self.date_expr.isValid()

        time_pattern = "([0-9]{,2}):([0-9]{,2}):([0-9]{,2})"
        self.time_expr = QtCore.QRegularExpression(f"^{time_pattern}$")
        assert self.time_expr.isValid()

        self.date_time_expr = QtCore.QRegularExpression(f"^{date_pattern}T{time_pattern}$")
        assert self.date_time_expr.isValid()

    def type_from_text(
        self, text: str
    ) -> (
        t.Type[
            bool
            | int
            | QtCore.QByteArray
            | QtGui.QColor
            | QtCore.QDate
            | QtCore.QTime
            | QtCore.QDateTime
        ]
        | None
    ):
        """
        Determines the data type based on the given text.

        Parameters
        ----------
        text : str
            The text to check the data type for.

        Returns
        -------
        Type[bool | int | QtCore.QByteArray | QtGui.QColor | QtCore.QDate | QtCore.QTime | QtCore.QDateTime] | None
            The determined data type or None if the type cannot be determined.
        """
        if self.bool_expr.match(text).hasMatch():
            return bool
        elif self.int_expr.match(text).hasMatch():
            return int
        elif self.byte_array_expr.match(text).hasMatch():
            return QtCore.QByteArray
        elif self.color_expr.match(text).hasMatch():
            return QtGui.QColor
        elif self.date_expr.match(text).hasMatch():
            return QtCore.QDate
        elif self.time_expr.match(text).hasMatch():
            return QtCore.QTime
        elif self.date_time_expr.match(text).hasMatch():
            return QtCore.QDateTime

        return None

    def create_validator(self, value: t.Any, parent: QtCore.QObject) -> QtGui.QValidator | None:
        """
        Creates a validator for the given value.

        Parameters
        ----------
        value : Any
            The value to create a validator for.
        parent : QtCore.QObject
            The parent object for the validator.

        Returns
        -------
        QtGui.QValidator | None
            The created validator or None if a validator cannot be created.
        """
        if isinstance(value, bool):
            return QtGui.QRegularExpressionValidator(self.bool_expr, parent)
        if isinstance(value, float):
            return QtGui.QDoubleValidator(parent)
        if isinstance(value, int):
            return QtGui.QIntValidator(parent)
        if isinstance(value, QtCore.QByteArray):
            return QtGui.QRegularExpressionValidator(self.byte_array_expr, parent)
        if isinstance(value, QtGui.QColor):
            return QtGui.QRegularExpressionValidator(self.color_expr, parent)
        if isinstance(value, QtCore.QDate):
            return QtGui.QRegularExpressionValidator(self.date_expr, parent)
        if isinstance(value, QtCore.QTime):
            return QtGui.QRegularExpressionValidator(self.time_expr, parent)
        if isinstance(value, QtCore.QDateTime):
            return QtGui.QRegularExpressionValidator(self.date_time_expr, parent)
        if isinstance(value, QtCore.QPoint):
            return QtGui.QRegularExpressionValidator(self.point_expr, parent)
        if isinstance(value, QtCore.QRect):
            return QtGui.QRegularExpressionValidator(self.rect_expr, parent)
        if isinstance(value, QtCore.QSize):
            return QtGui.QRegularExpressionValidator(self.size_expr, parent)
        return None

    def from_string(self, text: str, original_value: t.Any) -> t.Any:
        """
        Converts the given text to the original data type.

        Parameters
        ----------
        text : str
            The text to convert.
        original_value : Any
            The original value to determine the data type.

        Returns
        -------
        Any
            The converted value.
        """
        if isinstance(original_value, QtGui.QColor):
            match = self.color_expr.match(text)
            return QtGui.QColor(
                min(int(match.captured(1)), 255),
                min(int(match.captured(2)), 255),
                min(int(match.captured(3)), 255),
                min(int(match.captured(4)), 255),
            )
        if isinstance(original_value, QtCore.QDate):
            value = QtCore.QDate.fromString(text, QtCore.Qt.DateFormat.ISODate)
            return value if value.isValid() else None
        if isinstance(original_value, QtCore.QTime):
            value = QtCore.QTime.fromString(text, QtCore.Qt.DateFormat.ISODate)
            return value if value.isValid() else None
        if isinstance(original_value, QtCore.QDateTime):
            value = QtCore.QDateTime.fromString(text, QtCore.Qt.DateFormat.ISODate)
            return value if value.isValid() else None
        if isinstance(original_value, QtCore.QPoint):
            match = self.point_expr.match(text)
            return QtCore.QPoint(int(match.captured(1)), int(match.captured(2)))
        if isinstance(original_value, QtCore.QRect):
            match = self.rect_expr.match(text)
            return QtCore.QRect(
                int(match.captured(1)),
                int(match.captured(2)),
                int(match.captured(3)),
                int(match.captured(4)),
            )
        if isinstance(original_value, QtCore.QSize):
            match = self.size_expr.match(text)
            return QtCore.QSize(int(match.captured(1)), int(match.captured(2)))
        if isinstance(original_value, list):
            return text.split(",")
        return type(original_value)(text)
