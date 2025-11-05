# noxfile.py (project root)
import nox

@nox.session(python=["3.10", "3.11"])
def test_plugin(session):
    """Run plugin tests in isolated environment"""
    session.install("-r", "requirements.txt")
    session.run("pytest", "plugins/deduplicator/tests/", "-v", "--cov")

@nox.session
def lint_plugin(session):
    """Run linters on plugin"""
    session.install("ruff", "pylint", "mypy")
    session.run("ruff", "check", "plugins/deduplicator/")
    session.run("pylint", "plugins/deduplicator/deduplicator.py")
    session.run("mypy", "plugins/deduplicator/deduplicator.py")