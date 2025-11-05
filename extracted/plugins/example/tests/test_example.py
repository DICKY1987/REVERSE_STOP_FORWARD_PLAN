# plugins/example/tests/test_example.py
import pytest
from unittest.mock import Mock, patch
from example import process_file

class TestProcessFile:
    """Unit tests for process_file function"""
    
    def test_valid_input_produces_valid_output(self):
        """Happy path test"""
        input_data = {
            "file_path": "test.txt",
            "content": "hello",
            "trace_id": "test-001"
        }
        
        result = process_file(input_data)
        
        assert result["status"] == "success"
        assert result["trace_id"] == "test-001"
    
    def test_missing_required_field_returns_error(self):
        """Error handling test"""
        input_data = {
            "file_path": "test.txt",
            # Missing 'content'!
            "trace_id": "test-002"
        }
        
        result = process_file(input_data)
        
        assert result["status"] == "error"
        assert "content" in result["error_message"].lower()
    
    @patch('example.external_api_call')
    def test_external_api_called_correctly(self, mock_api):
        """Test external dependencies are called correctly"""
        mock_api.return_value = {"api_status": "ok"}
        
        input_data = {
            "file_path": "test.txt",
            "content": "data",
            "trace_id": "test-003"
        }
        
        result = process_file(input_data)
        
        # Verify API was called
        mock_api.assert_called_once()
        assert result["status"] == "success"
    
    def test_timeout_handled_gracefully(self):
        """Test that timeouts don't crash the plugin"""
        with patch('example.slow_operation', side_effect=TimeoutError):
            input_data = {
                "file_path": "test.txt",
                "content": "data",
                "trace_id": "test-004"
            }
            
            result = process_file(input_data)
            
            assert result["status"] == "error"
            assert "timeout" in result["error_message"].lower()