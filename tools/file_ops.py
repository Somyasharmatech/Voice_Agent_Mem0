import os

OUTPUT_DIR = "output"

def file_exists(filename):
    """Check if a file already exists in the output folder."""
    filepath = os.path.join(OUTPUT_DIR, os.path.basename(filename))
    return os.path.exists(filepath)

def create_file(filename, content="", force_overwrite=False):
    """
    Creates a file inside the output directory.
    To prevent overwrite unless confirmed, it returns False if it exists and !force_overwrite.
    Returns: (bool status, str message, str file_path)
    """
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    # Prevent path traversal by only taking the basename
    safe_filename = os.path.basename(filename)
    filepath = os.path.join(OUTPUT_DIR, safe_filename)
    
    if os.path.exists(filepath) and not force_overwrite:
        return False, f"File '{safe_filename}' already exists. Please confirm overwrite.", filepath
        
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return True, f"File '{safe_filename}' created successfully.", filepath
    except Exception as e:
        return False, f"Error creating file: {str(e)}", None
