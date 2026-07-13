import os
import urllib.request
from urllib.parse import urlparse
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QFileDialog, QMessageBox, QFormLayout,
    QListWidget, QListWidgetItem
)
from app_launcher.models import AccessItem

def fetch_favicon(url):
    try:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc or parsed_url.path.split('/')[0]
        if not domain:
            return ""
        favicon_url = f"https://www.google.com/s2/favicons?domain={domain}&sz=64"
        
        # Save path relative to root directory
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        icons_dir = os.path.join(project_root, "icons")
        os.makedirs(icons_dir, exist_ok=True)
        
        # Safe filename
        safe_domain = domain.replace(":", "_").replace("/", "_")
        local_path = os.path.join(icons_dir, f"{safe_domain}.png")
        
        req = urllib.request.Request(
            favicon_url,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=2) as response:
            with open(local_path, "wb") as f:
                f.write(response.read())
        return local_path
    except Exception as e:
        print(f"Error fetching favicon for {url}: {e}")
        return ""

class IconSearchDialog(QDialog):
    def __init__(self, initial_query="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Buscador de Iconos del Sistema")
        self.setMinimumSize(550, 450)
        self.selected_icon_path = ""

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)

        # Header instructions
        desc = QLabel("Busca iconos instalados en el sistema (por ejemplo, supertux2).")
        desc.setStyleSheet("color: #aaaaaa; font-size: 12px;")
        layout.addWidget(desc)

        # Search Bar Row
        search_layout = QHBoxLayout()
        search_layout.setSpacing(10)
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("Ej. supertux2, spotify, vlc...")
        self.txt_search.setText(initial_query)
        self.txt_search.returnPressed.connect(self.perform_search)
        
        self.btn_search = QPushButton("Buscar")
        self.btn_search.setFixedWidth(80)
        self.btn_search.clicked.connect(self.perform_search)

        search_layout.addWidget(self.txt_search)
        search_layout.addWidget(self.btn_search)
        layout.addLayout(search_layout)

        # Results Grid (ListWidget in IconMode)
        self.list_widget = QListWidget()
        self.list_widget.setViewMode(QListWidget.IconMode)
        self.list_widget.setIconSize(QSize(48, 48))
        self.list_widget.setMovement(QListWidget.Static)
        self.list_widget.setResizeMode(QListWidget.Adjust)
        self.list_widget.setSpacing(12)
        # Style QListWidget to match our theme (dark mode, white outlines)
        self.list_widget.setStyleSheet("""
            QListWidget {
                background-color: #000000;
                border: 1px solid #ffffff;
                color: #ffffff;
            }
            QListWidget::item {
                border: 1px solid transparent;
                padding: 5px;
                color: #ffffff;
            }
            QListWidget::item:hover {
                background-color: #1a1a1a;
                border: 1px solid #ffffff;
            }
            QListWidget::item:selected {
                background-color: #ffffff;
                color: #000000;
                border: 1px solid #ffffff;
            }
        """)
        self.list_widget.itemDoubleClicked.connect(self.accept_selection)
        layout.addWidget(self.list_widget)

        # Action Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.btn_cancel = QPushButton("Cancelar")
        self.btn_cancel.clicked.connect(self.reject)
        
        self.btn_accept = QPushButton("Seleccionar")
        self.btn_accept.setObjectName("AddButton")
        self.btn_accept.clicked.connect(self.accept_selection)

        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_accept)
        layout.addLayout(btn_layout)

        # Run initial search if query is provided
        if initial_query:
            self.perform_search()

    def perform_search(self):
        self.list_widget.clear()
        query = self.txt_search.text().strip()
        if not query:
            return

        results = self.find_system_icons(query)
        if not results:
            QMessageBox.information(self, "Buscador de Iconos", "No se encontraron iconos que coincidan con la búsqueda.")
            return

        for path in results:
            filename = os.path.basename(path)
            # Create list item
            item = QListWidgetItem()
            item.setIcon(QIcon(path))
            item.setText(filename)
            item.setToolTip(path)
            item.setData(Qt.UserRole, path)
            self.list_widget.addItem(item)

    def find_system_icons(self, query):
        search_dirs = [
            "/usr/share/icons",
            "/usr/share/pixmaps",
            os.path.expanduser("~/.local/share/icons")
        ]
        matches = []
        query = query.strip().lower()
        if not query:
            return matches

        for base_dir in search_dirs:
            if not os.path.exists(base_dir):
                continue
            for root, dirs, files in os.walk(base_dir):
                # Optimization: skip cursors and small icons (16x16, 22x22, etc.) for dashboard flow
                root_lower = root.lower()
                if "cursor" in root_lower or "16x16" in root_lower or "22x22" in root_lower or "24x24" in root_lower:
                    continue
                for file in files:
                    name, ext = os.path.splitext(file)
                    if ext.lower() in [".png", ".svg", ".jpg", ".jpeg", ".xpm"]:
                        if query in name.lower():
                            full_path = os.path.join(root, file)
                            if full_path not in matches:
                                matches.append(full_path)
                                # Limit results to 60 to keep performance solid
                                if len(matches) >= 60:
                                    return matches
        return matches

    def accept_selection(self):
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Buscador de Iconos", "Por favor seleccione un icono de la lista.")
            return
        self.selected_icon_path = selected_items[0].data(Qt.UserRole)
        self.accept()

class SettingsDialog(QDialog):
    def __init__(self, item=None, parent=None):
        super().__init__(parent)
        self.item = item
        self.setWindowTitle("Configurar Acceso")
        self.setMinimumWidth(450)
        self.resize(500, 300)

        # Form Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title = QLabel("Configurar Acceso" if not item else "Editar Acceso")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #66fcf1; margin-bottom: 10px;")
        layout.addWidget(title)

        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        form_layout.setLabelAlignment(Qt.AlignRight)

        # Name Field
        self.txt_name = QLineEdit()
        self.txt_name.setPlaceholderText("Nombre del acceso (ej. YouTube, Stremio)")
        form_layout.addRow("Nombre:", self.txt_name)

        # Type Field
        self.combo_type = QComboBox()
        self.combo_type.addItems(["WebApp (Enlace Web)", "Comando del sistema"])
        self.combo_type.currentIndexChanged.connect(self.on_type_changed)
        form_layout.addRow("Tipo:", self.combo_type)

        # Path / URL Field
        self.txt_path = QLineEdit()
        self.txt_path.setPlaceholderText("https://... o comando del sistema")
        form_layout.addRow("Ruta / URL:", self.txt_path)

        # Icon Field with Browse and Search System Buttons
        icon_layout = QHBoxLayout()
        self.txt_icon = QLineEdit()
        self.txt_icon.setPlaceholderText("Ruta al archivo de imagen (opcional)")
        
        self.btn_browse_icon = QPushButton("Buscar")
        self.btn_browse_icon.setFixedWidth(80)
        self.btn_browse_icon.clicked.connect(self.browse_icon)
        
        self.btn_search_system_icon = QPushButton("Buscar Sistema")
        self.btn_search_system_icon.setFixedWidth(120)
        self.btn_search_system_icon.clicked.connect(self.search_system_icon)
        
        icon_layout.addWidget(self.txt_icon)
        icon_layout.addWidget(self.btn_browse_icon)
        icon_layout.addWidget(self.btn_search_system_icon)
        
        form_layout.addRow("Icono:", icon_layout)
        layout.addLayout(form_layout)

        # Action Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_cancel = QPushButton("Cancelar")
        self.btn_cancel.clicked.connect(self.reject)
        
        self.btn_save = QPushButton("Guardar")
        self.btn_save.setObjectName("AddButton")
        self.btn_save.clicked.connect(self.save)

        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_save)
        layout.addLayout(btn_layout)

        # Populate if editing
        if self.item:
            self.txt_name.setText(self.item.name)
            if self.item.type == "webapp":
                self.combo_type.setCurrentIndex(0)
            else:
                self.combo_type.setCurrentIndex(1)
            self.txt_path.setText(self.item.path)
            self.txt_icon.setText(self.item.icon)

        self.on_type_changed()

    def on_type_changed(self):
        # Update placeholder based on type
        if self.combo_type.currentIndex() == 0:
            self.txt_path.setPlaceholderText("https://www.youtube.com")
        else:
            self.txt_path.setPlaceholderText("flatpak run com.spotify.Client o connman-gtk")

    def browse_icon(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Icono", "", "Imágenes (*.png *.jpg *.jpeg *.svg *.ico);;Todos los archivos (*)"
        )
        if file_path:
            self.txt_icon.setText(file_path)

    def search_system_icon(self):
        initial_query = self.txt_name.text().strip()
        dialog = IconSearchDialog(initial_query, self)
        if dialog.exec() == QDialog.Accepted:
            if dialog.selected_icon_path:
                self.txt_icon.setText(dialog.selected_icon_path)

    def save(self):
        name = self.txt_name.text().strip()
        path = self.txt_path.text().strip()
        icon = self.txt_icon.text().strip()
        type_ = "webapp" if self.combo_type.currentIndex() == 0 else "command"

        if not name:
            QMessageBox.warning(self, "Error", "El nombre es obligatorio.")
            return
        if not path:
            QMessageBox.warning(self, "Error", "La Ruta o URL es obligatoria.")
            return

        # Simple validation for WebApp
        if type_ == "webapp":
            if not (path.startswith("http://") or path.startswith("https://")):
                # Automatically prepend https:// if missing
                if not path.startswith("www."):
                    path = "https://" + path
                else:
                    path = "https://" + path

            # Automatically fetch favicon if no icon is specified
            if not icon:
                fetched_icon = fetch_favicon(path)
                if fetched_icon:
                    icon = fetched_icon

        if not self.item:
            # Create new access item
            self.item = AccessItem(name=name, type_=type_, path=path, icon=icon)
        else:
            # Update existing
            self.item.name = name
            self.item.type = type_
            self.item.path = path
            self.item.icon = icon

        self.accept()
