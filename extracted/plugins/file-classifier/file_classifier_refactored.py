# plugins/file-classifier/file_classifier.py
from pathlib import Path
from typing import Dict

def classify_file(file_path: str, file_content: str) -> Dict[str, any]:
    """
    Classify a file based on path and content.
    
    Args:
        file_path: Path to the file
        file_content: Content of the file
        
    Returns:
        Classification result with confidence and recommended location
    """
    extension = Path(file_path).suffix.lower()
    
    classifiers = {
        '.py': ('python_module', 'modules/python/', 0.95),
        '.ps1': ('powershell_script', 'modules/powershell/', 0.95),
        '.md': ('documentation', 'docs/', 0.90),
    }
    
    if extension in classifiers:
        classification, location, confidence = classifiers[extension]
        return {
            "classification": classification,
            "confidence": confidence,
            "recommended_location": location
        }
    
    return {
        "classification": "unknown",
        "confidence": 0.0,
        "recommended_location": "quarantine/"
    }

# Run: pytest plugins/file-classifier/tests/
# Expected: PASS (still works after refactor)