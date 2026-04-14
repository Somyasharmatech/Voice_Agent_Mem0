import json
import os
import datetime

MEMORY_FILE = "memory.json"

def save_memory(data):
    """
    Appends a new interaction (data object) to the memory file.
    Automatically adds a timestamp.
    """
    history = get_memory()
    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "data": data
    }
    history.append(entry)
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4)

def get_memory():
    """
    Retrieves the entire memory history as a list.
    """
    if not os.path.exists(MEMORY_FILE):
        return []
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def clear_memory():
    """
    Clears the memory file.
    """
    if os.path.exists(MEMORY_FILE):
        os.remove(MEMORY_FILE)
