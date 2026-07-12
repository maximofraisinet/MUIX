import os
import urllib.request
from urllib.parse import urlparse
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QFileDialog, QMessageBox, QFormLayout
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

        # Icon Field with Browse Button
        icon_layout = QHBoxLayout()
        self.txt_icon = QLineEdit()
        self.txt_icon.setPlaceholderText("Ruta al archivo de imagen (opcional)")
        self.btn_browse_icon = QPushButton("Buscar")
        self.btn_browse_icon.setFixedWidth(80)
        self.btn_browse_icon.clicked.connect(self.browse_icon)
        icon_layout.addWidget(self.txt_icon)
        icon_layout.addWidget(self.btn_browse_icon)
        
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
