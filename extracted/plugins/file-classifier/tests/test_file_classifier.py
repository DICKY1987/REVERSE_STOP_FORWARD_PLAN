# plugins/file-classifier/tests/test_file_classifier.py
import pytest
from file_classifier import classify_file

def test_classify_python_file():
    """Test that .py files are classified as 'python_module'"""
    # Arrange
    file_path = "test_script.py"
    file_content = "def hello(): pass"
    
    # Act
    result = classify_file(file_path, file_content)
    
    # Assert
    assert result["classification"] == "python_module"
    assert result["confidence"] >= 0.9
    assert result["recommended_location"] == "modules/python/"

# Run: pytest plugins/file-classifier/tests/
# Expected: FAIL (function doesn't exist yet)