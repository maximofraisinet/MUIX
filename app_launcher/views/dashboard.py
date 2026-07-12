import os
import shlex
import subprocess
from PySide6.QtCore import Qt, Signal, QUrl
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QScrollArea, QMessageBox, QFrame, QStackedWidget
)
from PySide6.QtGui import QPixmap, QPainter, QColor, QFont, QKeySequence, QShortcut

from app_launcher.models import load_accesses, save_accesses, AccessItem
from app_launcher.views.settings import SettingsDialog
from app_launcher.views.web_window import WebAppWidget

class LauncherCard(QFrame):
    clicked = Signal()
    edit_clicked = Signal()
    delete_clicked = Signal()

    def __init__(self, item, parent=None):
        super().__init__(parent)
        self.item = item
        self.setObjectName("LauncherCard")
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(160, 180)

        # Allow keyboard focus
        self.setFocusPolicy(Qt.StrongFocus)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 12, 10, 12)
        layout.setSpacing(8)

        # Icon or Fallback
        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setFixedSize(50, 50)
        self.icon_label.setObjectName("LauncherIcon")

        if item.icon and os.path.exists(item.icon):
            pixmap = QPixmap(item.icon).scaled(46, 46, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.icon_label.setPixmap(pixmap)
        else:
            # Generate aesthetic fallback circular image with name initial
            pixmap = QPixmap(50, 50)
            pixmap.fill(Qt.transparent)
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Choose color based on name hash to vary colors dynamically
            colors = ["#f87171", "#fb923c", "#fbbf24", "#34d399", "#2dd4bf", "#38bdf8", "#818cf8", "#c084fc", "#f472b6"]
            color_hex = colors[abs(hash(item.name)) % len(colors)]
            
            painter.setBrush(QColor(color_hex))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(2, 2, 46, 46)
            
            painter.setPen(QColor("#0d0e12"))
            font = QFont("sans-serif", 16, QFont.Bold)
            painter.setFont(font)
            initial = item.name[0].upper() if item.name else "?"
            painter.drawText(2, 2, 46, 46, Qt.AlignCenter, initial)
            painter.end()
            self.icon_label.setPixmap(pixmap)

        layout.addWidget(self.icon_label, alignment=Qt.AlignCenter)

        # Name
        self.name_label = QLabel(item.name)
        self.name_label.setObjectName("LauncherName")
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setWordWrap(True)
        layout.addWidget(self.name_label)

        # Type
        self.type_label = QLabel("WebApp" if item.type == "webapp" else "System")
        self.type_label.setObjectName("LauncherType")
        self.type_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.type_label)

        # Action Buttons Layout (edit / delete)
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(6)
        btn_layout.setContentsMargins(0, 5, 0, 0)

        self.btn_edit = QPushButton("Edit")
        self.btn_edit.setObjectName("EditButton")
        # Prevent these buttons from stealing key navigation focus from the card
        self.btn_edit.setFocusPolicy(Qt.NoFocus)
        self.btn_edit.clicked.connect(self.edit_clicked.emit)
        
        self.btn_delete = QPushButton("Del")
        self.btn_delete.setObjectName("DeleteButton")
        self.btn_delete.setFocusPolicy(Qt.NoFocus)
        self.btn_delete.clicked.connect(self.delete_clicked.emit)

        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        layout.addLayout(btn_layout)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Set focus to this card when clicked
            self.setFocus()
            child = self.childAt(event.position().toPoint())
            if child not in (self.btn_edit, self.btn_delete):
                self.clicked.emit()
        super().mousePressEvent(event)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space):
            self.clicked.emit()
            event.accept()
        else:
            super().keyPressEvent(event)


class DashboardWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MUIX Dashboard Launcher")
        self.resize(800, 600)
        self.setMinimumSize(600, 450)

        # Set default to fullscreen
        self.showFullScreen()

        self.items = []
        self.last_focused_card = None

        # Global Shortcut: Escape to exit WebApp and return to dashboard
        self.shortcut_back = QShortcut(QKeySequence(Qt.Key_Escape), self)
        self.shortcut_back.activated.connect(self.handle_escape)

        # Central Stacked Widget
        self.stacked_widget = QStackedWidget(self)
        self.setCentralWidget(self.stacked_widget)

        # ----------------------------------------------------
        # Page 0: Dashboard Grid view
        # ----------------------------------------------------
        self.page_dashboard = QWidget()
        page_dashboard_layout = QVBoxLayout(self.page_dashboard)
        page_dashboard_layout.setContentsMargins(0, 0, 0, 0)
        page_dashboard_layout.setSpacing(0)

        # Top dashboard panel
        header = QWidget()
        header.setObjectName("HeaderPanel")
        header.setFixedHeight(60)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)
        header_layout.setSpacing(10)

        lbl_title = QLabel("MUIX DASHBOARD")
        lbl_title.setStyleSheet("color: #66fcf1; font-weight: bold; font-size: 20px; font-family: monospace; letter-spacing: 2px;")
        
        btn_add = QPushButton("+ Agregar")
        btn_add.setObjectName("AddButton")
        btn_add.setFocusPolicy(Qt.NoFocus)
        btn_add.clicked.connect(self.add_new_access)

        self.btn_toggle_fs = QPushButton("🗗 Ventana")
        self.btn_toggle_fs.setFocusPolicy(Qt.NoFocus)
        self.btn_toggle_fs.clicked.connect(self.toggle_fullscreen)

        btn_exit = QPushButton("✕ Salir")
        btn_exit.setObjectName("CloseButton")
        btn_exit.setFocusPolicy(Qt.NoFocus)
        btn_exit.clicked.connect(self.close)

        header_layout.addWidget(lbl_title)
        header_layout.addStretch()
        header_layout.addWidget(btn_add)
        header_layout.addWidget(self.btn_toggle_fs)
        header_layout.addWidget(btn_exit)
        page_dashboard_layout.addWidget(header)

        # Scroll Area for launchers
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setObjectName("ScrollArea")
        
        self.scroll_content = QWidget()
        self.scroll_content.setObjectName("ScrollAreaContent")
        self.grid_layout = QGridLayout(self.scroll_content)
        self.grid_layout.setContentsMargins(20, 20, 20, 20)
        self.grid_layout.setSpacing(20)
        
        scroll.setWidget(self.scroll_content)
        page_dashboard_layout.addWidget(scroll)
        self.stacked_widget.addWidget(self.page_dashboard)

        # ----------------------------------------------------
        # Page 1: Single WebApp Widget view (embedded)
        # ----------------------------------------------------
        self.web_widget = WebAppWidget()
        self.web_widget.back_to_dashboard.connect(self.show_dashboard_page)
        self.stacked_widget.addWidget(self.web_widget)

        # Load initially saved items
        self.refresh_dashboard()

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
            self.btn_toggle_fs.setText("🗖 Pantalla Completa")
        else:
            self.showFullScreen()
            self.btn_toggle_fs.setText("🗗 Ventana")

    def handle_escape(self):
        # Back action via Escape shortcut
        if self.stacked_widget.currentIndex() == 1:
            self.show_dashboard_page()

    def show_dashboard_page(self):
        # Load blank page to stop web activities
        self.web_widget.browser.setUrl(QUrl("about:blank"))
        self.stacked_widget.setCurrentIndex(0)
        
        # Restore focus to the card that opened the WebApp
        if self.last_focused_card:
            self.last_focused_card.setFocus()
        else:
            self.focus_first_card()

    def refresh_dashboard(self):
        # Clear previous grid items
        while self.grid_layout.count():
            child = self.grid_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Load launchers from model
        self.items = load_accesses()
        
        # Grid parameters (columns depends on window width, hardcoded 4 for standard desktop layout)
        cols = 4
        for index, item in enumerate(self.items):
            row = index // cols
            col = index % cols
            card = LauncherCard(item)
            card.clicked.connect(lambda i=item: self.launch_item(i))
            card.edit_clicked.connect(lambda i=item: self.edit_item(i))
            card.delete_clicked.connect(lambda i=item: self.delete_item(i))
            self.grid_layout.addWidget(card, row, col, Qt.AlignLeft | Qt.AlignTop)
        
        # Auto-focus the first item for instant keyboard navigation
        self.focus_first_card()

    def focus_first_card(self):
        if self.grid_layout.count() > 0:
            first_item = self.grid_layout.itemAt(0).widget()
            if first_item:
                first_item.setFocus()

    def launch_item(self, item):
        # Remember last focused card
        focused = self.focusWidget()
        if isinstance(focused, LauncherCard):
            self.last_focused_card = focused

        if item.type == "webapp":
            # Load the URL and show the embedded WebApp Widget
            self.web_widget.load_url(item.path, item.name)
            self.stacked_widget.setCurrentIndex(1)
        else:
            # Launch system command in background
            try:
                args = shlex.split(item.path)
                subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo ejecutar el comando: '{item.path}'\nError: {e}")

    def add_new_access(self):
        dialog = SettingsDialog(parent=self)
        if dialog.exec():
            new_item = dialog.item
            self.items.append(new_item)
            if save_accesses(self.items):
                self.refresh_dashboard()
            else:
                QMessageBox.critical(self, "Error", "No se pudo guardar la configuración.")

    def edit_item(self, item):
        dialog = SettingsDialog(item, parent=self)
        if dialog.exec():
            if save_accesses(self.items):
                self.refresh_dashboard()
            else:
                QMessageBox.critical(self, "Error", "No se pudo actualizar la configuración.")

    def delete_item(self, item):
        reply = QMessageBox.question(
            self, "Confirmar eliminación",
            f"¿Estás seguro de que deseas eliminar '{item.name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.items = [i for i in self.items if i.id != item.id]
            if save_accesses(self.items):
                self.refresh_dashboard()
            else:
                QMessageBox.critical(self, "Error", "No se pudo guardar la configuración.")

    def keyPressEvent(self, event):
        # Active only in dashboard view
        if self.stacked_widget.currentIndex() == 0:
            focused = self.focusWidget()
            
            # Fetch all cards
            cards = []
            for i in range(self.grid_layout.count()):
                widget = self.grid_layout.itemAt(i).widget()
                if isinstance(widget, LauncherCard):
                    cards.append(widget)

            if not cards:
                super().keyPressEvent(event)
                return

            if focused not in cards:
                # If nothing focused, focus the first one
                cards[0].setFocus()
                event.accept()
                return

            current_idx = cards.index(focused)
            cols = 4
            rows = (len(cards) + cols - 1) // cols

            r = current_idx // cols
            c = current_idx % cols

            if event.key() == Qt.Key_Left:
                new_idx = max(0, current_idx - 1)
                cards[new_idx].setFocus()
                event.accept()
            elif event.key() == Qt.Key_Right:
                new_idx = min(len(cards) - 1, current_idx + 1)
                cards[new_idx].setFocus()
                event.accept()
            elif event.key() == Qt.Key_Up:
                if r > 0:
                    new_idx = (r - 1) * cols + c
                    if new_idx < len(cards):
                        cards[new_idx].setFocus()
                    event.accept()
            elif event.key() == Qt.Key_Down:
                if r < rows - 1:
                    new_idx = (r + 1) * cols + c
                    if new_idx < len(cards):
                        cards[new_idx].setFocus()
                    else:
                        cards[-1].setFocus()
                    event.accept()
            else:
                super().keyPressEvent(event)
        else:
            super().keyPressEvent(event)
