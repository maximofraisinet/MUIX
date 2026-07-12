import json
import os
import uuid

# Configuration path is always relative to the workspace root where the script resides
CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "accesos.json")

class AccessItem:
    def __init__(self, name, type_, path, icon="", id_=None):
        self.id = id_ or str(uuid.uuid4())
        self.name = name
        self.type = type_  # "webapp" or "command"
        self.path = path
        self.icon = icon

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "path": self.path,
            "icon": self.icon
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data.get("name", ""),
            type_=data.get("type", "webapp"),
            path=data.get("path", ""),
            icon=data.get("icon", ""),
            id_=data.get("id")
        )

def load_accesses():
    if not os.path.exists(CONFIG_PATH):
        # Create empty configuration if not exists
        save_accesses([])
        return []
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [AccessItem.from_dict(item) for item in data]
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return []

def save_accesses(items):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump([item.to_dict() for item in items], f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving configuration: {e}")
        return False
