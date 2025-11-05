"""Utility script to extract governance document versions.

This script scans the YAML front matter of specified Markdown files
and extracts the semantic version (semver) for each.  It can be used
in pipeline startup to record the active policy versions into a ledger
entry.  The functions here mirror the examples found in the
Versioning Operating Contract.
"""

from __future__ import annotations

import re
import json
import subprocess
from pathlib import Path
from datetime import datetime


def get_doc_semver(path: str) -> str | None:
    """Extract semver from document front matter.

    Args:
        path: Path to the Markdown document.

    Returns:
        The semantic version as a string if found, otherwise ``None``.
    """
    content = Path(path).read_text(encoding="utf-8")
    match = re.search(r"---\s*(.*?)---", content, re.DOTALL)
    if match:
        yaml_content = match.group(1)
        semver_match = re.search(
            r"^\s*semver:\s*([0-9]+\.[0-9]+\.[0-9]+)", yaml_content, re.MULTILINE
        )
        if semver_match:
            return semver_match.group(1)
    return None


def get_active_policy_versions() -> dict:
    """Get current versions of all policy documents.

    Returns a mapping of document keys to their current semantic
    versions by reading the front matter of the appropriate files.  The
    paths here should be adjusted if your repository layout differs.
    """
    return {
        "OC_CORE": get_doc_semver("docs/standards/OC_CORE.md"),
        "PIPELINE_POLICY": get_doc_semver("docs/standards/PIPELINE_POLICY.md"),
        "R_PIPELINE_PHASE_01": get_doc_semver(
            "plans/R_PIPELINE/PHASE_01_EXECUTION_CONTRACT.md"
        ),
    }


if __name__ == "__main__":
    run_ledger = {
        "run_id": "2025-11-01T12-00-00Z_ULID...",
        "repo_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True
        ).strip(),
        "policy_versions": get_active_policy_versions(),
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    # Serialize to ledger
    ledger_path = Path("ledger") / f"{run_ledger['run_id']}.json"
    ledger_path.parent.mkdir(exist_ok=True)
    ledger_path.write_text(json.dumps(run_ledger, indent=2))