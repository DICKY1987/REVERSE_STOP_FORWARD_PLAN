#!/usr/bin/env python3
"""
Unit tests for the file similarity comparison script.
"""

import tempfile
from pathlib import Path
from compare_file_similarity import calculate_similarity, is_text_file


def test_identical_files():
    """Test that identical files have 100% similarity."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file1 = Path(tmpdir) / "file1.txt"
        file2 = Path(tmpdir) / "file2.txt"
        
        content = "This is a test file with some content.\nIt has multiple lines.\n"
        file1.write_text(content)
        file2.write_text(content)
        
        similarity = calculate_similarity(file1, file2)
        assert similarity == 1.0, f"Expected 1.0, got {similarity}"
        print("✓ Identical files test passed")


def test_completely_different_files():
    """Test that completely different files have low similarity."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file1 = Path(tmpdir) / "file1.txt"
        file2 = Path(tmpdir) / "file2.txt"
        
        file1.write_text("AAAAAAAAAAAAAAAAAAAA")
        file2.write_text("BBBBBBBBBBBBBBBBBBBB")
        
        similarity = calculate_similarity(file1, file2)
        assert similarity < 0.1, f"Expected < 0.1, got {similarity}"
        print("✓ Completely different files test passed")


def test_similar_files():
    """Test that similar files have high similarity."""
    with tempfile.TemporaryDirectory() as tmpdir:
        file1 = Path(tmpdir) / "file1.txt"
        file2 = Path(tmpdir) / "file2.txt"
        
        # Files with 90% same content
        content1 = "Line 1\nLine 2\nLine 3\nLine 4\nLine 5\nLine 6\nLine 7\nLine 8\nLine 9\nLine 10\n"
        content2 = "Line 1\nLine 2\nLine 3\nLine 4\nLine 5\nLine 6\nLine 7\nLine 8\nLine 9\nDifferent\n"
        
        file1.write_text(content1)
        file2.write_text(content2)
        
        similarity = calculate_similarity(file1, file2)
        assert similarity > 0.85, f"Expected > 0.85, got {similarity}"
        print(f"✓ Similar files test passed (similarity: {similarity:.2%})")


def test_is_text_file_detection():
    """Test text file detection."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Python file
        py_file = Path(tmpdir) / "test.py"
        py_file.write_text("print('hello')")
        assert is_text_file(py_file), "Python file should be detected as text"
        print("✓ Python file detection passed")
        
        # Text file
        txt_file = Path(tmpdir) / "test.txt"
        txt_file.write_text("hello world")
        assert is_text_file(txt_file), "Text file should be detected as text"
        print("✓ Text file detection passed")
        
        # JSON file
        json_file = Path(tmpdir) / "test.json"
        json_file.write_text('{"key": "value"}')
        assert is_text_file(json_file), "JSON file should be detected as text"
        print("✓ JSON file detection passed")


def main():
    """Run all tests."""
    print("Running unit tests for compare_file_similarity.py")
    print("=" * 60)
    
    try:
        test_identical_files()
        test_completely_different_files()
        test_similar_files()
        test_is_text_file_detection()
        
        print("=" * 60)
        print("All tests passed! ✓")
        return 0
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
