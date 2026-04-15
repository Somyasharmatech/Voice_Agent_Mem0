import os
import json
import pytest
from memory import save_memory, get_memory, clear_memory, MEMORY_FILE

@pytest.fixture(autouse=True)
def setup_and_teardown_memory():
    # Setup: Clear any existing memory before the test
    clear_memory()
    yield
    # Teardown: Clean up after the test
    clear_memory()

def test_save_and_get_memory():
    sample_data = {"type": "chat", "message": "hello world"}
    
    # Initially memory should be empty
    assert get_memory() == []
    
    # Save memory
    save_memory(sample_data)
    
    # Memory should have 1 item
    history = get_memory()
    assert len(history) == 1
    assert "timestamp" in history[0]
    assert history[0]["data"] == sample_data

def test_clear_memory():
    sample_data = {"test": "data"}
    save_memory(sample_data)
    
    assert os.path.exists(MEMORY_FILE)
    
    clear_memory()
    
    assert not os.path.exists(MEMORY_FILE)
    assert get_memory() == []
