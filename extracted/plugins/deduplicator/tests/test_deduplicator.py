# plugins/deduplicator/tests/test_deduplicator.py
import pytest
import json
from deduplicator import detect_duplicate

def test_detect_new_file():
    """Test that new files are not marked as duplicates"""
    # Arrange
    input_data = {
        "file_path": "new_file.txt",
        "file_hash": "abc123",
        "trace_id": "test-trace-001"
    }
    
    # Act
    result = detect_duplicate(input_data)
    
    # Assert
    assert result["status"] == "success"
    assert result["is_duplicate"] == False
    assert result["trace_id"] == "test-trace-001"

def test_detect_duplicate_file():
    """Test that duplicate files are detected"""
    # Arrange - simulate existing file
    existing_file = {
        "file_path": "existing_file.txt",
        "file_hash": "xyz789",
        "trace_id": "test-trace-002"
    }
    
    duplicate_file = {
        "file_path": "duplicate_file.txt",
        "file_hash": "xyz789",  # Same hash!
        "trace_id": "test-trace-003"
    }
    
    # Act
    detect_duplicate(existing_file)  # Add to "database"
    result = detect_duplicate(duplicate_file)
    
    # Assert
    assert result["status"] == "success"
    assert result["is_duplicate"] == True
    assert result["duplicate_of"] == "existing_file.txt"
    assert result["recommended_action"] == "quarantine"

def test_error_handling():
    """Test that invalid input produces structured error"""
    # Arrange
    input_data = {
        "file_path": "test.txt",
        # Missing file_hash!
        "trace_id": "test-trace-004"
    }
    
    # Act
    result = detect_duplicate(input_data)
    
    # Assert
    assert result["status"] == "error"
    assert "error_message" in result

# Run: pytest plugins/deduplicator/tests/ -v
# Expected: ALL FAIL (no implementation yet)