import json
import os
import datetime
from typing import List, Dict, Any
from utils.logger import get_logger

logger = get_logger(__name__)

MEMORY_FILE = "memory.json"

def save_memory(data: Dict[str, Any]) -> None:
    """
    Appends a new interaction (data object) to the memory file.
    Automatically adds a timestamp.

    Args:
        data (Dict[str, Any]): The interaction data to save.
    """
    history = get_memory()
    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "data": data
    }
    history.append(entry)
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=4)
        logger.info(f"Memory saved successfully. Current memory size: {len(history)} items.")
    except Exception as e:
        logger.error(f"Failed to save memory: {str(e)}", exc_info=True)

def get_memory() -> List[Dict[str, Any]]:
    """
    Retrieves the entire memory history as a list.

    Returns:
        List[Dict[str, Any]]: A list of memory entries.
    """
    if not os.path.exists(MEMORY_FILE):
        return []
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"Error reading memory file, returning empty list. Error: {str(e)}")
        return []

def clear_memory() -> None:
    """
    Clears the memory file by removing it.
    """
    if os.path.exists(MEMORY_FILE):
        try:
            os.remove(MEMORY_FILE)
            logger.info("Memory file successfully cleared.")
        except Exception as e:
            logger.error(f"Failed to clear memory: {str(e)}", exc_info=True)
