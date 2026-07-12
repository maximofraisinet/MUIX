from PySide6.QtCore import Qt, QUrl, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QProgressBar
from PySide6.QtWebEngineWidgets import QWebEngineView

class WebAppWidget(QWidget):
    back_to_dashboard = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Custom minimalist toolbar
        toolbar = QWidget()
        toolbar.setObjectName("HeaderPanel")
        toolbar.setFixedHeight(45)
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(10, 0, 10, 0)
        toolbar_layout.setSpacing(8)

        self.btn_back = QPushButton("←")
        self.btn_back.setFixedWidth(40)
        self.btn_back.clicked.connect(self.go_back)

        self.btn_forward = QPushButton("→")
        self.btn_forward.setFixedWidth(40)
        self.btn_forward.clicked.connect(self.go_forward)

        self.btn_reload = QPushButton("↻")
        self.btn_reload.setFixedWidth(40)
        self.btn_reload.clicked.connect(self.reload_page)

        self.lbl_title = QLabel("WebApp")
        self.lbl_title.setStyleSheet("color: #ffffff; font-weight: bold; font-size: 13px; margin-left: 10px;")

        self.btn_close = QPushButton("✕ Dashboard (Esc)")
        self.btn_close.setObjectName("CloseButton")
        self.btn_close.setFixedWidth(150)
        self.btn_close.clicked.connect(self.back_to_dashboard.emit)

        toolbar_layout.addWidget(self.btn_back)
        toolbar_layout.addWidget(self.btn_forward)
        toolbar_layout.addWidget(self.btn_reload)
        toolbar_layout.addWidget(self.lbl_title)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.btn_close)

        layout.addWidget(toolbar)

        # Progress bar for loading
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(3)
        self.progress_bar.setTextVisible(False)
        layout.addWidget(self.progress_bar)

        # WebEngine Browser
        self.browser = QWebEngineView()
        self.browser.loadProgress.connect(self.update_progress)
        self.browser.titleChanged.connect(self.update_title)
        self.browser.loadFinished.connect(self.update_buttons)
        layout.addWidget(self.browser)
        
        self.update_buttons()

    def load_url(self, url, title="WebApp"):
        self.lbl_title.setText(title)
        self.browser.setUrl(QUrl(url))

    def go_back(self):
        self.browser.back()

    def go_forward(self):
        self.browser.forward()

    def reload_page(self):
        self.browser.reload()

    def update_progress(self, progress):
        self.progress_bar.setValue(progress)
        if progress >= 100:
            self.progress_bar.hide()
        else:
            self.progress_bar.show()

    def update_title(self, title):
        if title.strip():
            self.lbl_title.setText(title)

    def update_buttons(self):
        history = self.browser.history()
        self.btn_back.setEnabled(history.canGoBack())
        self.btn_forward.setEnabled(history.canGoForward())

