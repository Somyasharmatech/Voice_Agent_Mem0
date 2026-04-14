import os

OUTPUT_DIR = "output"

def list_files():
    """
    Returns a list of all files currently residing in the output folder.
    """
    if not os.path.exists(OUTPUT_DIR):
        return []
    
    files = []
    for f in os.listdir(OUTPUT_DIR):
        if os.path.isfile(os.path.join(OUTPUT_DIR, f)):
            files.append(f)
    return files

def read_file(filename):
    """
    Reads and returns the content of a file located in the output folder.
    """
    filepath = os.path.join(OUTPUT_DIR, os.path.basename(filename))
    
    if not os.path.exists(filepath):
        return None, "File does not exist."
        
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        return content, "Success"
    except Exception as e:
        return None, f"Error reading file: {str(e)}"
