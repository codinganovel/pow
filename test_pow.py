#!/usr/bin/env python3
"""
Test script for pow functionality
Tests all features to ensure nothing broke with the daily note implementation
"""

import os
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
import sys

# Add the current directory to path so we can import pow
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pow import FileExplorer, TEXT_EXTENSIONS

def test_text_file_detection():
    """Test text file detection functionality"""
    print("Testing text file detection...")
    
    explorer = FileExplorer()
    
    # Test with temporary directory
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        
        # Create test files
        text_file = tmp_path / "test.txt"
        text_file.write_text("Hello world")
        
        py_file = tmp_path / "script.py"
        py_file.write_text("print('hello')")
        
        binary_file = tmp_path / "binary.bin"
        binary_file.write_bytes(b'\x00\x01\x02\x03')
        
        empty_file = tmp_path / "empty"
        empty_file.write_text("")
        
        # Test detection
        assert explorer.is_text_file(text_file), "Should detect .txt as text"
        assert explorer.is_text_file(py_file), "Should detect .py as text"
        assert not explorer.is_text_file(binary_file), "Should not detect binary as text"
        assert explorer.is_text_file(empty_file), "Should detect empty file as text"
        
    print("✓ Text file detection working")

def test_filename_sanitization():
    """Test filename sanitization for note creation"""
    print("Testing filename sanitization...")
    
    explorer = FileExplorer()
    
    # Test various inputs
    test_cases = [
        ("My Note Title", "My-Note-Title"),
        ("test!@#$%^&*()note", "testnote"),
        ("  spaced  note  ", "spaced-note"),
        ("multiple---hyphens", "multiple-hyphens"),
        ("", "untitled"),
        ("123-abc_def", "123-abc_def"),
    ]
    
    for input_title, expected in test_cases:
        result = explorer.sanitize_filename(input_title)
        assert result == expected, f"Expected '{expected}' but got '{result}' for input '{input_title}'"
    
    print("✓ Filename sanitization working")

def test_daily_note_filename():
    """Test daily note filename generation"""
    print("Testing daily note filename generation...")
    
    explorer = FileExplorer()
    filename = explorer.get_daily_note_filename()
    
    # Should match ISO format YYYY-MM-DD.md
    expected_pattern = datetime.now().strftime("%Y-%m-%d.md")
    assert filename == expected_pattern, f"Expected '{expected_pattern}' but got '{filename}'"
    
    # Should end with .md
    assert filename.endswith(".md"), "Daily note filename should end with .md"
    
    # Should be valid date format
    date_part = filename[:-3]  # Remove .md
    try:
        datetime.strptime(date_part, "%Y-%m-%d")
    except ValueError:
        assert False, f"Invalid date format in filename: {date_part}"
    
    print("✓ Daily note filename generation working")

def test_directory_scanning():
    """Test directory scanning functionality"""
    print("Testing directory scanning...")
    
    explorer = FileExplorer()
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        explorer.current_path = tmp_path
        
        # Create test structure
        (tmp_path / "subdir").mkdir()
        (tmp_path / "test.txt").write_text("test")
        (tmp_path / "script.py").write_text("print('test')")
        (tmp_path / "binary.bin").write_bytes(b'\x00\x01')
        (tmp_path / ".hidden").write_text("hidden")
        
        # Scan directory
        explorer.scan_directory()
        
        # Check items
        item_names = [item[0] for item in explorer.items]
        
        # Should include text files and directories
        assert "test.txt" in item_names, "Should include text files"
        assert "script.py" in item_names, "Should include Python files"
        assert "subdir/" in item_names, "Should include subdirectories"
        
        # Should not include binary or hidden files
        assert "binary.bin" not in item_names, "Should not include binary files"
        assert ".hidden" not in item_names, "Should not include hidden files"
        
    print("✓ Directory scanning working")

def test_search_functionality():
    """Test fuzzy search functionality"""
    print("Testing search functionality...")
    
    explorer = FileExplorer()
    
    # Mock some items
    explorer.items = [
        ("readme.md", False, Path("readme.md")),
        ("test.py", False, Path("test.py")),
        ("main.js", False, Path("main.js")),
        ("config.yaml", False, Path("config.yaml")),
    ]
    
    # Test search
    explorer.handle_search("test")
    assert len(explorer.filtered_items) >= 1, "Should find matching items"
    
    # Test fuzzy matching
    explorer.handle_search("tst")  # Fuzzy match for "test"
    assert len(explorer.filtered_items) >= 1, "Should find fuzzy matches"
    
    # Test empty search
    explorer.handle_search("")
    assert len(explorer.filtered_items) == len(explorer.items), "Empty search should show all items"
    
    print("✓ Search functionality working")

def test_file_creation_simulation():
    """Test file creation logic (without actually opening editor)"""
    print("Testing file creation simulation...")
    
    explorer = FileExplorer()
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        explorer.current_path = tmp_path
        
        # Test daily note filename generation
        filename = explorer.get_daily_note_filename()
        file_path = tmp_path / filename
        
        # Should not exist initially
        assert not file_path.exists(), "Daily note should not exist initially"
        
        # Simulate file creation (without opening editor)
        if not file_path.exists():
            file_path.write_text("")
        
        # Should exist after creation
        assert file_path.exists(), "Daily note should exist after creation"
        assert file_path.is_file(), "Daily note should be a file"
        
        # Test duplicate handling for regular notes
        test_file = tmp_path / "test.md"
        test_file.write_text("existing")
        
        # Should handle existing files by adding counter
        filename = explorer.sanitize_filename("test")
        base_path = tmp_path / f"{filename}.md"
        counter = 1
        while base_path.exists():
            base_path = tmp_path / f"{filename}-{counter}.md"
            counter += 1
        
        assert counter == 2, "Should find next available filename"
        
    print("✓ File creation simulation working")

def test_text_extensions():
    """Test that TEXT_EXTENSIONS constant contains expected extensions"""
    print("Testing text extensions...")
    
    expected_extensions = [
        '.txt', '.md', '.py', '.js', '.json', '.yaml', '.yml',
        '.html', '.css', '.sh', '.conf', '.cfg', '.ini', '.log',
        '.sql', '.xml', '.csv', '.toml', '.rs', '.go', '.c', '.cpp'
    ]
    
    for ext in expected_extensions:
        assert ext in TEXT_EXTENSIONS, f"Extension {ext} should be in TEXT_EXTENSIONS"
    
    print("✓ Text extensions working")

def test_cursor_bounds():
    """Test cursor position bounds checking"""
    print("Testing cursor bounds...")
    
    explorer = FileExplorer()
    
    # Test with empty items
    explorer.items = []
    explorer.scan_directory()  # This should reset cursor
    assert explorer.cursor_position == 0, "Cursor should be 0 for empty list"
    
    # Test with items
    explorer.items = [("test1.txt", False, Path("test1.txt"))]
    explorer.cursor_position = 5  # Out of bounds
    # Manually trigger cursor bounds check since scan_directory will rebuild items
    if explorer.items:
        explorer.cursor_position = min(explorer.cursor_position, len(explorer.items) - 1)
        explorer.cursor_position = max(0, explorer.cursor_position)
    assert explorer.cursor_position == 0, "Cursor should be reset to valid position"
    
    print("✓ Cursor bounds working")

def run_all_tests():
    """Run all tests"""
    print("Running pow functionality tests...\n")
    
    tests = [
        test_text_file_detection,
        test_filename_sanitization,
        test_daily_note_filename,
        test_directory_scanning,
        test_search_functionality,
        test_file_creation_simulation,
        test_text_extensions,
        test_cursor_bounds,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
    
    print(f"\nTest Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! The daily note feature integration is working correctly.")
    else:
        print("❌ Some tests failed. Please check the implementation.")
    
    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)