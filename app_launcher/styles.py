DARK_STYLE = """
/* General Window and Panels */
QMainWindow {
    background-color: #000000;
}

QWidget#CentralWidget {
    background-color: #000000;
}

QWidget#HeaderPanel {
    background-color: #000000;
    border-bottom: 2px solid #ffffff;
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
    background-color: #000000;
    border: 1px solid #333333;
    border-radius: 0px;
}

QFrame#LauncherCard:hover, QFrame#LauncherCard:focus {
    background-color: #121212;
    border: 2px solid #ffffff;
}

QLabel#LauncherName {
    color: #ffffff;
    font-size: 14px;
    font-weight: bold;
    background: transparent;
}

QLabel#LauncherType {
    color: #aaaaaa;
    font-size: 10px;
    font-weight: bold;
    text-transform: uppercase;
    background: transparent;
}

QLabel#LauncherIcon {
    background-color: #000000;
    border: 1px solid #333333;
    border-radius: 0px;
    padding: 5px;
}

/* Buttons */
QPushButton {
    background-color: #000000;
    color: #ffffff;
    border: 1px solid #ffffff;
    border-radius: 0px;
    padding: 8px 16px;
    font-size: 13px;
    font-weight: bold;
}

QPushButton:hover, QPushButton:focus {
    background-color: #ffffff;
    color: #000000;
}

QPushButton:pressed {
    background-color: #dddddd;
    color: #000000;
}

QPushButton#AddButton {
    background-color: #ffffff;
    color: #000000;
    border: 1px solid #ffffff;
}

QPushButton#AddButton:hover, QPushButton#AddButton:focus {
    background-color: #000000;
    color: #ffffff;
}

QPushButton#CloseButton {
    background-color: #ffffff;
    color: #000000;
    border: 1px solid #ffffff;
}

QPushButton#CloseButton:hover, QPushButton#CloseButton:focus {
    background-color: #ff3b30;
    color: #ffffff;
    border: 1px solid #ff3b30;
}

QPushButton#EditButton {
    background-color: transparent;
    color: #ffffff;
    border: 1px solid #ffffff;
    padding: 4px 8px;
    border-radius: 0px;
    font-size: 11px;
}

QPushButton#EditButton:hover {
    background-color: #ffffff;
    color: #000000;
}

QPushButton#DeleteButton {
    background-color: transparent;
    color: #ff3b30;
    border: 1px solid #ff3b30;
    padding: 4px 8px;
    border-radius: 0px;
    font-size: 11px;
}

QPushButton#DeleteButton:hover {
    background-color: #ff3b30;
    color: #ffffff;
}

/* Dialogs */
QDialog {
    background-color: #000000;
    border: 2px solid #ffffff;
    border-radius: 0px;
}

QDialog QLabel {
    color: #ffffff;
    font-size: 13px;
}

/* Input Fields & Comboboxes */
QLineEdit, QComboBox {
    background-color: #000000;
    border: 1px solid #333333;
    border-radius: 0px;
    padding: 8px;
    color: #ffffff;
}

QLineEdit:focus, QComboBox:focus {
    border: 2px solid #ffffff;
}

QComboBox::drop-down {
    border: none;
}

QComboBox QAbstractItemView {
    background-color: #000000;
    color: #ffffff;
    selection-background-color: #ffffff;
    selection-color: #000000;
}

/* Progress bar in Web view */
QProgressBar {
    background-color: #222222;
    border: none;
    height: 3px;
}

QProgressBar::chunk {
    background-color: #ffffff;
}
"""
