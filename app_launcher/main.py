import sys
from PySide6.QtWidgets import QApplication
from app_launcher.views.dashboard import DashboardWindow
from app_launcher.styles import DARK_STYLE

def main():
    # Create Qt App
    app = QApplication(sys.argv)
    app.setApplicationName("MUIX Launcher")
    
    # Apply stylesheet
    app.setStyleSheet(DARK_STYLE)

    # Show dashboard
    window = DashboardWindow()
    window.show()

    # Start main event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
