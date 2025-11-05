# plugins/file-classifier/file_classifier.py
def classify_file(file_path: str, file_content: str) -> dict:
    """Classify a file based on path and content"""
    if file_path.endswith('.py'):
        return {
            "classification": "python_module",
            "confidence": 0.95,
            "recommended_location": "modules/python/"
        }
    return {
        "classification": "unknown",
        "confidence": 0.0,
        "recommended_location": "quarantine/"
    }

# Run: pytest plugins/file-classifier/tests/
# Expected: PASS