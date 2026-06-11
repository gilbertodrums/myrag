from pathlib import Path

# Add sync directory to path so we can import sync.py
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from sync import calculate_hash

def test_calculate_hash(tmp_path):
    test_file = tmp_path / "test.md"
    test_file.write_text("Hello World", encoding="utf-8")
    
    # Calculate hash using function
    file_hash = calculate_hash(test_file)
    
    # Assert hash is correct (SHA-256 of "Hello World")
    assert file_hash == "a591a6d40bf420404a011733cfb7b190d62c65bf0bcda32b57b277d9ad9f146e"

def test_calculate_hash_empty_file(tmp_path):
    test_file = tmp_path / "empty.md"
    test_file.write_text("", encoding="utf-8")
    
    file_hash = calculate_hash(test_file)
    
    # SHA-256 of empty string
    assert file_hash == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
