# infrastructure/tests/test_infrastructure.py
import pytest
import testinfra

def test_required_directories_exist(host):
    """Test that all required directories exist with correct permissions"""
    required_dirs = [
        "/opt/r_pipeline",
        "/opt/r_pipeline/plugins",
        "/opt/r_pipeline/logs",
        "/opt/r_pipeline/quarantine",
    ]
    
    for dir_path in required_dirs:
        directory = host.file(dir_path)
        assert directory.exists
        assert directory.is_directory
        assert directory.user == "r_pipeline"
        assert directory.mode == 0o755

def test_firewall_rules_configured(host):
    """Test that firewall allows only necessary ports"""
    # Check that only ports 22 (SSH) and 443 (HTTPS) are open
    iptables = host.iptables.rules('INPUT')
    
    # Should allow SSH
    assert any('22' in rule for rule in iptables)
    
    # Should NOT allow random ports
    assert not any('8080' in rule for rule in iptables)

def test_opentelemetry_collector_running(host):
    """Test that OpenTelemetry collector service is active"""
    service = host.service("otel-collector")
    assert service.is_running
    assert service.is_enabled

# Run: pytest infrastructure/tests/ --hosts=localhost