FLUENT_COMBO_BOX = """
QComboBox {
    border: 1px solid rgba(0, 0, 0, 0.073);
    border-radius: 5px;
    border-bottom: 1px solid rgba(0, 0, 0, 0.183);
    padding: 5px 31px 6px 11px;
    /* font: 14px 'Segoe UI', 'Microsoft YaHei', 'PingFang SC'; */
    color: black;
    background-color: rgba(255, 255, 255, 0.7);
    text-align: left;
    outline: none;
}

QComboBox:hover {
    background-color: rgba(249, 249, 249, 0.5);
}

QComboBox:pressed {
    background-color: rgba(249, 249, 249, 0.3);
    border-bottom: 1px solid rgba(0, 0, 0, 0.073);
    color: rgba(0, 0, 0, 0.63);
}

QComboBox:disabled {
    color: rgba(0, 0, 0, 0.36);
    background: rgba(249, 249, 249, 0.3);
    border: 1px solid rgba(0, 0, 0, 0.06);
    border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

QComboBox[isPlaceholderText=true] {
    color: rgba(0, 0, 0, 0.6063);
}
"""
