# infrastructure/tests/test_r_pipeline_infrastructure.py
import pytest
import testinfra

@pytest.fixture(scope='module')
def host(request):
    """Fixture for testinfra host"""
    return testinfra.get_host('local://')

class TestDirectoryStructure:
    """Test required directory structure"""
    
    def test_base_directory_exists(self, host):
        base_dir = host.file("/opt/r_pipeline")
        assert base_dir.exists
        assert base_dir.is_directory
        assert base_dir.user == "r_pipeline"
        assert base_dir.group == "r_pipeline"
        assert base_dir.mode == 0o755
    
    def test_plugin_directory_exists(self, host):
        plugin_dir = host.file("/opt/r_pipeline/plugins")
        assert plugin_dir.exists
        assert plugin_dir.is_directory
    
    def test_log_directory_writable(self, host):
        log_dir = host.file("/opt/r_pipeline/logs")
        assert log_dir.exists
        assert log_dir.is_directory
        assert log_dir.mode == 0o755

class TestSystemServices:
    """Test required system services"""
    
    def test_otel_collector_installed(self, host):
        otel = host.file("/usr/local/bin/otelcol")
        assert otel.exists
        assert otel.is_file
        assert otel.mode == 0o755
    
    def test_otel_service_running(self, host):
        service = host.service("otel-collector")
        assert service.is_running
        assert service.is_enabled
    
    def test_otel_listening_on_port(self, host):
        socket = host.socket("tcp://0.0.0.0:4318")
        assert socket.is_listening

class TestSecurityConfiguration:
    """Test security requirements"""
    
    def test_firewall_rules_restrictive(self, host):
        iptables = host.iptables.rules('INPUT')
        
        # Should allow SSH (22)
        assert any('dport 22' in rule for rule in iptables)
        
        # Should NOT allow unrestricted access
        assert not any('0.0.0.0/0' in rule and 'ACCEPT' in rule for rule in iptables)
    
    def test_selinux_enforcing(self, host):
        selinux = host.command("getenforce")
        assert selinux.stdout.strip() == "Enforcing"
    
    def test_ssh_password_auth_disabled(self, host):
        sshd_config = host.file("/etc/ssh/sshd_config")
        assert "PasswordAuthentication no" in sshd_config.content_string

class TestPythonEnvironment:
    """Test Python environment setup"""
    
    def test_python_version(self, host):
        python = host.command("python3 --version")
        assert python.rc == 0
        version = python.stdout.strip()
        # Ensure Python 3.10+
        assert "Python 3.1" in version
    
    def test_required_packages_installed(self, host):
        packages = [
            "pytest",
            "opentelemetry-sdk",
            "black",
            "ruff"
        ]
        for package in packages:
            pip_show = host.command(f"pip3 show {package}")
            assert pip_show.rc == 0, f"Package {package} not installed"

# Run: pytest infrastructure/tests/ -v --hosts=localhost