import os
import pytest
from tools.file_ops import create_file, file_exists, OUTPUT_DIR

@pytest.fixture(autouse=True)
def setup_and_teardown_output():
    # Setup: ensure output directory exists
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    test_file = os.path.join(OUTPUT_DIR, "test_file.txt")
    if os.path.exists(test_file):
        os.remove(test_file)
        
    yield
    
    # Teardown
    if os.path.exists(test_file):
        os.remove(test_file)

def test_create_file_success():
    filename = "test_file.txt"
    content = "Hello Pytest"
    
    success, msg, filepath = create_file(filename, content)
    
    assert success is True
    assert filepath.endswith("test_file.txt")
    assert file_exists(filename)
    
    # Verify content
    with open(filepath, "r") as f:
        saved_content = f.read()
    assert saved_content == content

def test_create_file_prevent_overwrite():
    filename = "test_file.txt"
    content1 = "Content 1"
    content2 = "Content 2"
    
    # First creation should succeed
    success1, _, _ = create_file(filename, content1)
    assert success1 is True
    
    # Second creation should strictly fail if force_overwrite=False
    success2, msg, _ = create_file(filename, content2, force_overwrite=False)
    assert success2 is False
    assert "already exists" in msg
    
    # Second creation should succeed if force_overwrite=True
    success3, _, _ = create_file(filename, content2, force_overwrite=True)
    assert success3 is True
