"""Quality gates for R_PIPELINE plugins.

This module defines a framework for applying a series of automated
checks (quality gates) to plugin code before it can be accepted for
deployment.  Each gate implements a ``check`` method that returns a
boolean indicating pass/fail and an explanatory message.  The
``run_quality_gates`` function orchestrates running these gates on a
specified plugin directory and prints coloured output to stdout to
indicate status.  Gates include test coverage enforcement, security
scanning via Bandit and contract compliance checking.
"""

from __future__ import annotations

import json
import subprocess
from typing import Dict, List, Tuple


class QualityGate:
    """Base class for all quality gates."""

    def check(self, plugin_path: str) -> Tuple[bool, str]:
        """Check whether the gate passes.

        Args:
            plugin_path: Path to the plugin directory.

        Returns:
            A tuple of (passed, message).
        """
        raise NotImplementedError


class TestCoverageGate(QualityGate):
    """Enforce a minimum test coverage percentage."""

    def __init__(self, minimum_coverage: int = 80) -> None:
        self.minimum_coverage = minimum_coverage

    def check(self, plugin_path: str) -> Tuple[bool, str]:
        # Run pytest with coverage and output JSON report
        subprocess.run([
            "pytest",
            f"{plugin_path}/tests/",
            "--cov",
            plugin_path,
            "--cov-report=json",
        ], capture_output=True, text=True)

        # Read coverage data from generated file
        with open("coverage.json") as f:
            coverage_data = json.load(f)

        total_coverage = coverage_data["totals"]["percent_covered"]
        if total_coverage >= self.minimum_coverage:
            return True, f"Coverage: {total_coverage:.1f}%"
        else:
            return False, f"Coverage {total_coverage:.1f}% < {self.minimum_coverage}%"


class SecurityScanGate(QualityGate):
    """Scan plugin for common security issues using Bandit."""

    def check(self, plugin_path: str) -> Tuple[bool, str]:
        result = subprocess.run(
            ["bandit", "-r", plugin_path, "-f", "json"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return True, "No security issues found"
        else:
            issues = json.loads(result.stdout)
            return False, f"Found {len(issues['results'])} security issues"


class ContractComplianceGate(QualityGate):
    """Verify plugin specification compliance with the operating contract."""

    def check(self, plugin_path: str) -> Tuple[bool, str]:
        with open(f"{plugin_path}/plugin.spec.json") as f:
            spec = json.load(f)

        required = [
            "plugin_name",
            "version",
            "lifecycle_event",
            "input_schema",
            "output_schema",
        ]
        missing = [f for f in required if f not in spec]
        if missing:
            return False, f"Missing fields: {', '.join(missing)}"

        # Check trace_id in schemas
        if "trace_id" not in spec["input_schema"].get("required", []):
            return False, "Input schema must require trace_id"
        if "trace_id" not in spec["output_schema"].get("required", []):
            return False, "Output schema must require trace_id"

        return True, "Contract compliant"


def run_quality_gates(plugin_path: str) -> bool:
    """Run all configured quality gates and return overall result.

    Args:
        plugin_path: Path to the plugin directory under ``plugins``.

    Returns:
        True if all gates pass, False otherwise.  The function prints
        coloured status markers for each gate.
    """
    gates = [
        TestCoverageGate(minimum_coverage=80),
        SecurityScanGate(),
        ContractComplianceGate(),
    ]

    print(f"\n=== Running Quality Gates for {plugin_path} ===\n")
    all_passed = True
    for gate in gates:
        gate_name = gate.__class__.__name__
        passed, message = gate.check(plugin_path)
        status = "✓" if passed else "✗"
        color = "\033[92m" if passed else "\033[91m"
        print(f"{color}{status} {gate_name}: {message}\033[0m")
        if not passed:
            all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("\033[92m✓ ALL QUALITY GATES PASSED\033[0m")
    else:
        print("\033[91m✗ SOME QUALITY GATES FAILED\033[0m")
    return all_passed