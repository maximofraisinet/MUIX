DARK_STYLE = """
/* General Window and Panels */
QMainWindow {
    background-color: #0b0c10;
}

QWidget#CentralWidget {
    background-color: #0b0c10;
}

QWidget#HeaderPanel {
    background-color: #1f2833;
    border-bottom: 2px solid #0b0c10;
}

/* Scroll Area styling */
QScrollArea {
    border: none;
    background-color: transparent;
}

QWidget#ScrollAreaContent {
    background-color: transparent;
}

/* Card design for Grid Items */
QFrame#LauncherCard {
    background-color: #1f2833;
    border: 1px solid #2d3748;
    border-radius: 12px;
}

QFrame#LauncherCard:hover, QFrame#LauncherCard:focus {
    background-color: #2b3a4a;
    border: 2px solid #66fcf1;
}

QLabel#LauncherName {
    color: #ffffff;
    font-size: 15px;
    font-weight: bold;
    background: transparent;
}

QLabel#LauncherType {
    color: #66fcf1;
    font-size: 11px;
    font-weight: 500;
    text-transform: uppercase;
    background: transparent;
}

QLabel#LauncherIcon {
    background-color: #0b0c10;
    border: 1px solid #2d3748;
    border-radius: 20px;
    padding: 5px;
}

/* Buttons */
QPushButton {
    background-color: #1f2833;
    color: #c5c6c7;
    border: 1px solid #45f3ff;
    border-radius: 6px;
    padding: 8px 16px;
    font-size: 13px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #45f3ff;
    color: #0b0c10;
}

QPushButton:pressed {
    background-color: #1f2833;
    color: #45f3ff;
}

QPushButton#AddButton {
    background-color: #0b0c10;
    color: #66fcf1;
    border: 2px solid #66fcf1;
    font-size: 14px;
}

QPushButton#AddButton:hover {
    background-color: #66fcf1;
    color: #0b0c10;
}

QPushButton#CloseButton {
    background-color: #e53e3e;
    color: white;
    border: none;
}

QPushButton#CloseButton:hover {
    background-color: #c53030;
}

QPushButton#EditButton {
    background-color: transparent;
    color: #66fcf1;
    border: 1px solid #66fcf1;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 11px;
}

QPushButton#EditButton:hover {
    background-color: #66fcf1;
    color: #0b0c10;
}

QPushButton#DeleteButton {
    background-color: transparent;
    color: #ff4d4d;
    border: 1px solid #ff4d4d;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 11px;
}

QPushButton#DeleteButton:hover {
    background-color: #ff4d4d;
    color: #0b0c10;
}

/* Dialogs */
QDialog {
    background-color: #1f2833;
    border: 2px solid #66fcf1;
    border-radius: 8px;
}

QDialog QLabel {
    color: #c5c6c7;
    font-size: 13px;
}

/* Input Fields & Comboboxes */
QLineEdit, QComboBox {
    background-color: #0b0c10;
    border: 1px solid #45f3ff;
    border-radius: 6px;
    padding: 8px;
    color: #ffffff;
}

QLineEdit:focus, QComboBox:focus {
    border: 2px solid #66fcf1;
}

QComboBox::drop-down {
    border: none;
}

QComboBox QAbstractItemView {
    background-color: #0b0c10;
    color: #ffffff;
    selection-background-color: #66fcf1;
    selection-color: #0b0c10;
}

/* Progress bar in Web view */
QProgressBar {
    background-color: #1f2833;
    border: none;
    height: 3px;
}

QProgressBar::chunk {
    background-color: #66fcf1;
}
"""
