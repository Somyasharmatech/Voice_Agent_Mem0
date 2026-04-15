import os
from typing import List, Tuple, Optional
from utils.logger import get_logger

logger = get_logger(__name__)

OUTPUT_DIR = "output"

def list_files() -> List[str]:
    """
    Returns a list of all files currently residing in the output folder.

    Returns:
        List[str]: A list of filenames.
    """
    if not os.path.exists(OUTPUT_DIR):
        logger.debug("Output directory does not exist. Returning empty list.")
        return []
    
    files = []
    for f in os.listdir(OUTPUT_DIR):
        if os.path.isfile(os.path.join(OUTPUT_DIR, f)):
            files.append(f)
            
    logger.info(f"Listed {len(files)} files from {OUTPUT_DIR}.")
    return files

def read_file(filename: str) -> Tuple[Optional[str], str]:
    """
    Reads and returns the content of a file located in the output folder.

    Args:
        filename (str): Name of the file to read.

    Returns:
        Tuple[Optional[str], str]: (File content if successful, Status message)
    """
    safe_filename = os.path.basename(filename)
    filepath = os.path.join(OUTPUT_DIR, safe_filename)
    
    if not os.path.exists(filepath):
        logger.warning(f"Attempted to read non-existent file: {safe_filename}")
        return None, "File does not exist."
        
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        logger.info(f"Successfully read file: {safe_filename}")
        return content, "Success"
    except Exception as e:
        logger.error(f"Error reading file '{safe_filename}': {str(e)}", exc_info=True)
        return None, f"Error reading file: {str(e)}"
