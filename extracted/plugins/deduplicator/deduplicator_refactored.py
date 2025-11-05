# plugins/deduplicator/deduplicator.py (improved version)

# BEGIN AUTO SECTION

from pathlib import Path
from typing import Dict, Any, Set
import logging

# Configure logging
logger = logging.getLogger(__name__)

class DuplicateDetector:
    """Manages duplicate file detection with persistent storage"""
    
    def __init__(self, storage_path: str = "/opt/r_pipeline/data/hashes.json"):
        self.storage_path = Path(storage_path)
        self._hash_database: Dict[str, str] = {}
        self._load_database()
    
    def _load_database(self):
        """Load hash database from persistent storage"""
        if self.storage_path.exists():
            try:
                import json
                with open(self.storage_path, 'r') as f:
                    self._hash_database = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load hash database: {e}")
    
    def _save_database(self):
        """Save hash database to persistent storage"""
        try:
            import json
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.storage_path, 'w') as f:
                json.dump(self._hash_database, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save hash database: {e}")
    
    def check_duplicate(self, file_path: str, file_hash: str) -> tuple[bool, str]:
        """
        Check if file is a duplicate.
        
        Returns:
            (is_duplicate, duplicate_of_path)
        """
        if file_hash in self._hash_database:
            return (True, self._hash_database[file_hash])
        
        # Not a duplicate - register it
        self._hash_database[file_hash] = file_path
        self._save_database()
        return (False, "")

# Singleton instance
_detector = DuplicateDetector()

def detect_duplicate(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Detect if a file is a duplicate based on hash.
    
    Args:
        input_data: Dictionary with file_path, file_hash, trace_id
        
    Returns:
        Dictionary with status, is_duplicate, and other required fields
    """
    try:
        # Validate input schema
        required_fields = ["file_path", "file_hash", "trace_id"]
        missing_fields = [f for f in required_fields if f not in input_data]
        
        if missing_fields:
            return {
                "status": "error",
                "error_message": f"Missing required fields: {', '.join(missing_fields)}",
                "trace_id": input_data.get("trace_id", "unknown")
            }
        
        file_path = input_data["file_path"]
        file_hash = input_data["file_hash"]
        trace_id = input_data["trace_id"]
        
        # Log operation with trace ID
        logger.info(f"[{trace_id}] Checking duplicate for: {file_path}")
        
        # Check for duplicate
        is_duplicate, duplicate_of = _detector.check_duplicate(file_path, file_hash)
        
        result = {
            "status": "success",
            "is_duplicate": is_duplicate,
            "duplicate_of": duplicate_of,
            "recommended_action": "quarantine" if is_duplicate else "proceed",
            "trace_id": trace_id
        }
        
        logger.info(f"[{trace_id}] Result: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error in detect_duplicate: {e}", exc_info=True)
        return {
            "status": "error",
            "error_message": str(e),
            "trace_id": input_data.get("trace_id", "unknown")
        }

# END AUTO SECTION