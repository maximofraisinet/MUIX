import os
import shlex
import subprocess
from PySide6.QtCore import Qt, Signal, QUrl, QTimer
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QScrollArea, QMessageBox, QFrame, QStackedWidget
)
from PySide6.QtGui import QPixmap, QPainter, QColor, QFont, QKeySequence, QShortcut, QPen

from app_launcher.models import load_accesses, save_accesses, AccessItem
from app_launcher.views.settings import SettingsDialog
from app_launcher.views.web_window import WebAppWidget

class LauncherCard(QFrame):
    clicked = Signal()

    def __init__(self, item, parent=None):
        super().__init__(parent)
        self.item = item
        self.setObjectName("LauncherCard")
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(180, 160)

        # Allow keyboard focus
        self.setFocusPolicy(Qt.StrongFocus)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 12, 10, 12)
        layout.setSpacing(8)

        # Icon or Fallback
        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setFixedSize(60, 60)
        self.icon_label.setObjectName("LauncherIcon")

        if item.icon and os.path.exists(item.icon):
            pixmap = QPixmap(item.icon).scaled(56, 56, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.icon_label.setPixmap(pixmap)
        else:
            # Generate aesthetic fallback square image with name initial (dark mode)
            pixmap = QPixmap(60, 60)
            pixmap.fill(Qt.transparent)
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Pure dark background
            painter.setBrush(QColor("#1a1a1a"))
            painter.setPen(QPen(QColor("#ffffff"), 1))
            painter.drawRect(2, 2, 55, 55)
            
            # White initial text
            painter.setPen(QColor("#ffffff"))
            font = QFont("sans-serif", 18, QFont.Bold)
            painter.setFont(font)
            initial = item.name[0].upper() if item.name else "?"
            painter.drawText(2, 2, 55, 55, Qt.AlignCenter, initial)
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

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Set focus to this card when clicked
            self.setFocus()
            self.clicked.emit()
        super().mousePressEvent(event)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space):
            self.clicked.emit()
            event.accept()
        elif event.key() in (Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down):
            window = self.window()
            if event.modifiers() & Qt.ShiftModifier and event.key() in (Qt.Key_Left, Qt.Key_Right):
                if hasattr(window, "reorder_grid"):
                    window.reorder_grid(self, event.key())
                    event.accept()
                else:
                    super().keyPressEvent(event)
            else:
                if hasattr(window, "navigate_grid"):
                    window.navigate_grid(self, event.key())
                    event.accept()
                else:
                    super().keyPressEvent(event)
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

        # Global Shortcut: F5 to reload page when WebApp is active
        self.shortcut_reload = QShortcut(QKeySequence(Qt.Key_F5), self)
        self.shortcut_reload.activated.connect(self.handle_f5_reload)

        # Global Shortcut: F1 to add new access when in dashboard view
        self.shortcut_add = QShortcut(QKeySequence(Qt.Key_F1), self)
        self.shortcut_add.activated.connect(self.handle_f1_add)

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
        
        self.btn_add = QPushButton("+ Agregar (F1)")
        self.btn_add.setObjectName("AddButton")
        self.btn_add.setFocusPolicy(Qt.StrongFocus)
        self.btn_add.setFixedSize(160, 35)
        self.btn_add.clicked.connect(self.add_new_access)

        self.btn_toggle_fs = QPushButton("🗗 Ventana")
        self.btn_toggle_fs.setFocusPolicy(Qt.StrongFocus)
        self.btn_toggle_fs.setFixedSize(160, 35)
        self.btn_toggle_fs.clicked.connect(self.toggle_fullscreen)

        self.btn_exit = QPushButton("✕ Salir")
        self.btn_exit.setObjectName("CloseButton")
        self.btn_exit.setFocusPolicy(Qt.StrongFocus)
        self.btn_exit.setFixedSize(160, 35)
        self.btn_exit.clicked.connect(self.close)

        # Install event filters for arrow key navigation on header buttons
        self.btn_add.installEventFilter(self)
        self.btn_toggle_fs.installEventFilter(self)
        self.btn_exit.installEventFilter(self)

        header_layout.addWidget(lbl_title)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_add)
        header_layout.addWidget(self.btn_toggle_fs)
        header_layout.addWidget(self.btn_exit)
        page_dashboard_layout.addWidget(header)

        # Scroll Area for launchers
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setObjectName("ScrollArea")
        
        self.scroll_content = QWidget()
        self.scroll_content.setObjectName("ScrollAreaContent")
        
        # Center container horizontally and vertically
        scroll_content_layout = QHBoxLayout(self.scroll_content)
        scroll_content_layout.setContentsMargins(20, 20, 20, 20)
        scroll_content_layout.addStretch(1)
        
        center_v_widget = QWidget()
        center_v_layout = QVBoxLayout(center_v_widget)
        center_v_layout.setContentsMargins(0, 0, 0, 0)
        center_v_layout.addStretch(1)
        
        self.launcher_container = QWidget()
        self.launcher_container.setMaximumWidth(800)
        self.grid_layout = QGridLayout(self.launcher_container)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setSpacing(25)
        
        center_v_layout.addWidget(self.launcher_container)
        center_v_layout.addStretch(1)
        
        scroll_content_layout.addWidget(center_v_widget)
        scroll_content_layout.addStretch(1)
        
        scroll.setWidget(self.scroll_content)
        page_dashboard_layout.addWidget(scroll)

        # Footer Panel (Legend of shortcuts)
        footer = QWidget()
        footer.setObjectName("FooterPanel")
        footer.setFixedHeight(30)
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(10, 0, 10, 0)
        
        lbl_legend = QLabel("F1: Agregar | Enter: Abrir | E: Editar | Supr: Eliminar | Shift+Flechas: Reordenar | Esc: Volver")
        lbl_legend.setObjectName("FooterText")
        lbl_legend.setAlignment(Qt.AlignCenter)
        footer_layout.addWidget(lbl_legend)
        page_dashboard_layout.addWidget(footer)

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

    def handle_f5_reload(self):
        # Reload action via F5 shortcut
        if self.stacked_widget.currentIndex() == 1:
            self.web_widget.reload_page()

    def handle_f1_add(self):
        # Add action via F1 shortcut when in dashboard
        if self.stacked_widget.currentIndex() == 0:
            self.add_new_access()

    def show_dashboard_page(self):
        # Load blank page to stop web activities
        self.web_widget.browser.setUrl(QUrl("about:blank"))
        self.stacked_widget.setCurrentIndex(0)
        
        # Restore focus to the card that opened the WebApp
        if self.last_focused_card:
            self.last_focused_card.setFocus()
        else:
            self.focus_first_card()

    def refresh_dashboard(self, auto_focus=True):
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
            self.grid_layout.addWidget(card, row, col, Qt.AlignLeft | Qt.AlignTop)
        
        # Auto-focus the first item for instant keyboard navigation
        if auto_focus:
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

    def reorder_grid(self, current_card, key):
        item = current_card.item
        if item not in self.items:
            return

        current_idx = self.items.index(item)

        if key == Qt.Key_Left:
            if current_idx > 0:
                # Swap with previous
                self.items[current_idx], self.items[current_idx - 1] = self.items[current_idx - 1], self.items[current_idx]
                if save_accesses(self.items):
                    self.refresh_dashboard(auto_focus=False)
                    QTimer.singleShot(20, lambda: self.focus_card_by_item(item))
        elif key == Qt.Key_Right:
            if current_idx < len(self.items) - 1:
                # Swap with next
                self.items[current_idx], self.items[current_idx + 1] = self.items[current_idx + 1], self.items[current_idx]
                if save_accesses(self.items):
                    self.refresh_dashboard(auto_focus=False)
                    QTimer.singleShot(20, lambda: self.focus_card_by_item(item))

    def focus_card_by_item(self, item):
        for i in range(self.grid_layout.count()):
            widget = self.grid_layout.itemAt(i).widget()
            if isinstance(widget, LauncherCard) and widget.item.id == item.id:
                widget.setFocus()
                break

    def eventFilter(self, watched, event):
        from PySide6.QtCore import QEvent
        if event.type() == QEvent.KeyPress:
            key = event.key()
            if key in (Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down):
                if watched in (self.btn_add, self.btn_toggle_fs, self.btn_exit):
                    self.navigate_header(watched, key)
                    return True
            elif key in (Qt.Key_Return, Qt.Key_Enter):
                if watched in (self.btn_add, self.btn_toggle_fs, self.btn_exit):
                    watched.animateClick()
                    return True
        return super().eventFilter(watched, event)

    def navigate_header(self, current_btn, key):
        # Header buttons sequence
        header_btns = [self.btn_add, self.btn_toggle_fs, self.btn_exit]
        
        # Get all grid cards
        cards = []
        for i in range(self.grid_layout.count()):
            widget = self.grid_layout.itemAt(i).widget()
            if isinstance(widget, LauncherCard):
                cards.append(widget)

        idx = header_btns.index(current_btn)

        if key == Qt.Key_Left:
            new_idx = (idx - 1) % len(header_btns)
            header_btns[new_idx].setFocus()
        elif key == Qt.Key_Right:
            new_idx = (idx + 1) % len(header_btns)
            header_btns[new_idx].setFocus()
        elif key == Qt.Key_Down:
            if cards:
                # Map header button index to top row grid columns:
                # Add button (0) -> Card 0
                # Fullscreen button (1) -> Card 2 (or last card)
                # Exit button (2) -> Card 3 (or last card)
                if idx == 1:
                    target_col = min(2, len(cards) - 1)
                elif idx == 2:
                    target_col = min(3, len(cards) - 1)
                else:
                    target_col = min(0, len(cards) - 1)
                cards[target_col].setFocus()

    def navigate_grid(self, current_card, key):
        # Fetch all cards
        cards = []
        for i in range(self.grid_layout.count()):
            widget = self.grid_layout.itemAt(i).widget()
            if isinstance(widget, LauncherCard):
                cards.append(widget)

        if not cards or current_card not in cards:
            return

        current_idx = cards.index(current_card)
        cols = 4
        rows = (len(cards) + cols - 1) // cols

        r = current_idx // cols
        c = current_idx % cols

        if key == Qt.Key_Left:
            new_idx = max(0, current_idx - 1)
            cards[new_idx].setFocus()
        elif key == Qt.Key_Right:
            new_idx = min(len(cards) - 1, current_idx + 1)
            cards[new_idx].setFocus()
        elif key == Qt.Key_Up:
            if r > 0:
                new_idx = (r - 1) * cols + c
                if new_idx < len(cards):
                    cards[new_idx].setFocus()
            else:
                # Top row of cards: transition focus to header buttons
                if c in (0, 1):
                    self.btn_add.setFocus()
                elif c == 2:
                    self.btn_toggle_fs.setFocus()
                elif c == 3:
                    self.btn_exit.setFocus()
        elif key == Qt.Key_Down:
            if r < rows - 1:
                new_idx = (r + 1) * cols + c
                if new_idx < len(cards):
                    cards[new_idx].setFocus()
                else:
                    cards[-1].setFocus()

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

            header_btns = [self.btn_add, self.btn_toggle_fs, self.btn_exit]

            # If a card is focused, intercept E and Delete keys
            if isinstance(focused, LauncherCard):
                if event.key() == Qt.Key_E:
                    self.edit_item(focused.item)
                    event.accept()
                    return
                elif event.key() == Qt.Key_Delete:
                    self.delete_item(focused.item)
                    event.accept()
                    return

            if not cards:
                if focused not in header_btns:
                    self.btn_add.setFocus()
                super().keyPressEvent(event)
                return

            if focused not in cards and focused not in header_btns:
                if self.last_focused_card and self.last_focused_card in cards:
                    self.last_focused_card.setFocus()
                else:
                    cards[0].setFocus()
                event.accept()
                return

            super().keyPressEvent(event)
        else:
            super().keyPressEvent(event)
