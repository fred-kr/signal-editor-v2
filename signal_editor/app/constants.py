import typing as t

NOT_SET_OPTION: t.Final = "<Not Set>"
INDEX_COL: t.Final = "index"
SECTION_INDEX_COL: t.Final = "section_index"
IS_PEAK_COL: t.Final = "is_peak"
IS_MANUAL_COL: t.Final = "is_manual"
RESERVED_COLUMN_NAMES: t.Final = frozenset([NOT_SET_OPTION, INDEX_COL, SECTION_INDEX_COL, IS_PEAK_COL, IS_MANUAL_COL])

STYLE_SHEET_ENUM_COMBO_BOX = """
QComboBox {
    min-width: 150px;
    min-height: 31px;
    border-radius: 5px;
    padding: 5px 31px 6px 11px;
    color: rgba(0, 0, 0, 0.6063);
    background-color: rgba(255, 255, 255, 0.7);
    text-align: left;
    outline: none;
}
QComboBox:hover {
    background-color: rgba(249, 249, 249, 0.5);
}
QComboBox:pressed {
    background-color: rgba(249, 249, 249, 0.3);
    color: rgba(0, 0, 0, 0.63);
}
QComboBox:disabled {
    color: rgba(0, 0, 0, 0.36);
    background: rgba(249, 249, 249, 0.3);
    border: 1px solid rgba(0, 0, 0, 0.06);
}
QComboBox QAbstractItemView::item {
    min-height: 31px;
}
"""

STYLE_SHEET_SPIN_BOX = """
SpinBox[requiresInput="false"] {
    border: 2px solid mediumseagreen;
    border-radius: 5px;
}
SpinBox[requiresInput="false"]:focus {
    border: 2px solid mediumseagreen;
    border-radius: 5px;
}

SpinBox[requiresInput="true"] {
    border: 2px solid red;
    border-radius: 5px;
}
SpinBox[requiresInput="true"]:focus {
    border: 2px solid red;
    border-radius: 5px;
}
"""

STYLE_SHEET_COMBO_BOX = """
ComboBox[requiresInput="false"] {
    border: 2px solid mediumseagreen;
    border-radius: 5px;
    padding: 5px 31px 6px 11px;
    /* font: 14px 'Segoe UI', 'Microsoft YaHei', 'PingFang SC'; */
    color: black;
    background-color: rgba(255, 255, 255, 0.7);
    text-align: left;
    outline: none;
}
ComboBox[requiresInput="true"] {
    border: 2px solid crimson;
    border-radius: 5px;
    padding: 5px 31px 6px 11px;
    /* font: 14px 'Segoe UI', 'Microsoft YaHei', 'PingFang SC'; */
    color: black;
    background-color: rgba(255, 255, 255, 0.7);
    text-align: left;
    outline: none;
}

ComboBox[requiresInput="false"]:hover {
    border: 2px solid mediumseagreen;
    border-radius: 5px;
    background-color: rgba(249, 249, 249, 0.5);
}
ComboBox[requiresInput="true"]:hover {
    border: 2px solid crimson;
    border-radius: 5px;
    background-color: rgba(249, 249, 249, 0.5);
}

ComboBox[requiresInput="false"]:pressed {
    border: 2px solid mediumseagreen;
    border-radius: 5px;
    background-color: rgba(249, 249, 249, 0.3);
    color: rgba(0, 0, 0, 0.63);
}
ComboBox[requiresInput="true"]:pressed {
    border: 2px solid crimson;
    border-radius: 5px;
    background-color: rgba(249, 249, 249, 0.3);
    color: rgba(0, 0, 0, 0.63);
}

ComboBox:disabled {
    color: rgba(0, 0, 0, 0.36);
    background: rgba(249, 249, 249, 0.3);
    border: 1px solid rgba(0, 0, 0, 0.06);
}

ComboBox {
    color: rgba(0, 0, 0, 0.6063);
}
"""
