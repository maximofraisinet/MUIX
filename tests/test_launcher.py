import os
import json
import pytest
from app_launcher.models import AccessItem, load_accesses, save_accesses, CONFIG_PATH
from app_launcher.views.settings import SettingsDialog
from PySide6.QtWidgets import QApplication

# Setup a clean config file for testing
@pytest.fixture
def clean_config():
    # Store original configuration content if it exists
    original_exists = os.path.exists(CONFIG_PATH)
    original_content = ""
    if original_exists:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            original_content = f.read()

    # Yield back to the test
    yield CONFIG_PATH

    # Restore original configuration
    if original_exists:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            f.write(original_content)
    elif os.path.exists(CONFIG_PATH):
        os.remove(CONFIG_PATH)

def test_access_item_creation():
    item = AccessItem(name="Test YouTube", type_="webapp", path="https://youtube.com", icon="/tmp/icon.png")
    assert item.name == "Test YouTube"
    assert item.type == "webapp"
    assert item.path == "https://youtube.com"
    assert item.icon == "/tmp/icon.png"
    assert item.id is not None

def test_serialization():
    item = AccessItem(name="Test Command", type_="command", path="echo hello", icon="")
    item_dict = item.to_dict()
    
    assert item_dict["name"] == "Test Command"
    assert item_dict["type"] == "command"
    assert item_dict["path"] == "echo hello"
    assert item_dict["icon"] == ""
    assert "id" in item_dict

    restored = AccessItem.from_dict(item_dict)
    assert restored.id == item.id
    assert restored.name == item.name
    assert restored.type == item.type
    assert restored.path == item.path
    assert restored.icon == item.icon

def test_load_save_config(clean_config):
    test_items = [
        AccessItem(name="App 1", type_="webapp", path="https://test1.com"),
        AccessItem(name="App 2", type_="command", path="ls -la")
    ]
    
    # Save configuration
    save_success = save_accesses(test_items)
    assert save_success is True
    
    # Load configuration and check
    loaded = load_accesses()
    assert len(loaded) == 2
    assert loaded[0].name == "App 1"
    assert loaded[0].type == "webapp"
    assert loaded[1].name == "App 2"
    assert loaded[1].type == "command"

def test_pyside_import():
    # Ensure PySide6 compiles and packages are importable
    import PySide6
    from PySide6.QtCore import QUrl
    from PySide6.QtWidgets import QMainWindow
    from PySide6.QtWebEngineWidgets import QWebEngineView
    
    assert PySide6.__version__ is not None
