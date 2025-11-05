import json
import subprocess
from pathlib import Path


class TestPluginIntegration:
    """Integration tests for plugin execution in R_PIPELINE"""

    def test_deduplicator_integration(self):
        """Test deduplicator plugin in full pipeline"""
        # Create test file
        test_file = Path("/tmp/test_dup.txt")
        test_file.write_text("duplicate content")

        # Run pipeline with deduplicator plugin
        result = subprocess.run(
            ["python3", "core/runner.py", "--file", str(test_file)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0

        # Parse output
        output = json.loads(result.stdout)

        # Verify deduplicator was invoked
        assert "deduplicator" in output["plugins_executed"]
        assert output["status"] == "success"

    def test_multi_plugin_execution_order(self):
        """Test that plugins execute in correct lifecycle order"""
        # This would test:
        # 1. FileDetected plugins run first
        # 2. PreMerge plugins run before merge
        # 3. PostMerge plugins run after merge
        pass