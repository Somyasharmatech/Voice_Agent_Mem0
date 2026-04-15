import os
from typing import Tuple, Optional
from utils.logger import get_logger

logger = get_logger(__name__)

OUTPUT_DIR = "output"

def file_exists(filename: str) -> bool:
    """
    Check if a file already exists in the output folder.

    Args:
        filename (str): The name of the file to check.

    Returns:
        bool: True if the file exists, False otherwise.
    """
    filepath = os.path.join(OUTPUT_DIR, os.path.basename(filename))
    exists = os.path.exists(filepath)
    logger.debug(f"Checked if file '{filename}' exists: {exists}")
    return exists

def create_file(filename: str, content: str = "", force_overwrite: bool = False) -> Tuple[bool, str, Optional[str]]:
    """
    Creates a file inside the output directory.
    To prevent overwrite unless confirmed, it returns False if it exists and !force_overwrite.

    Args:
        filename (str): Name of the file.
        content (str, optional): The content to write. Defaults to "".
        force_overwrite (bool, optional): Whether to overwrite if exists. Defaults to False.

    Returns:
        Tuple[bool, str, Optional[str]]: (Success status, Result message, File path if successful else None)
    """
    logger.info(f"Attempting to create file: '{filename}' (overwrite={force_overwrite})")
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        logger.debug(f"Created missing output directory: {OUTPUT_DIR}")
        
    # Prevent path traversal by only taking the basename
    safe_filename = os.path.basename(filename)
    filepath = os.path.join(OUTPUT_DIR, safe_filename)
    
    if os.path.exists(filepath) and not force_overwrite:
        logger.warning(f"File creation aborted. '{safe_filename}' already exists and force_overwrite is False.")
        return False, f"File '{safe_filename}' already exists. Please confirm overwrite.", filepath
        
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info(f"Successfully created/written to file '{safe_filename}'.")
        return True, f"File '{safe_filename}' created successfully.", filepath
    except Exception as e:
        logger.error(f"Error creating file '{safe_filename}': {str(e)}", exc_info=True)
        return False, f"Error creating file: {str(e)}", None
