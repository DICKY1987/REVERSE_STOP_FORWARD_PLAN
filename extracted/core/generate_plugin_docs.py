"""Generate plugin documentation from a specification.

This module provides utility functions to convert a ``plugin.spec.json``
into a suite of documentation artifacts.  The generator reads the
specification, then writes out a manifest, policy snapshot, ledger
contract, README, and healthcheck file.  All generated files live in
the same directory as the specification.  Dates and times are
expressed in ISO 8601 format to ensure determinism and to simplify
comparison in tests.
"""

import json
import datetime
from pathlib import Path
from typing import Dict


def generate_plugin_documentation(spec_path: Path) -> None:
    """Generate all documentation artifacts from ``plugin.spec.json``.

    Args:
        spec_path: Path to the ``plugin.spec.json`` file.

    The function loads the specification, then delegates to helper
    functions to create each artifact.  It prints a summary to stdout
    upon completion.
    """
    # Load spec
    with open(spec_path) as f:
        spec = json.load(f)

    plugin_dir = spec_path.parent

    # Generate each artifact
    generate_manifest(spec, plugin_dir)
    generate_policy_snapshot(spec, plugin_dir)
    generate_ledger_contract(spec, plugin_dir)
    generate_readme(spec, plugin_dir)
    generate_healthcheck(spec, plugin_dir)

    print(f"✓ Generated all documentation for {spec['plugin_name']}")


def generate_manifest(spec: Dict, plugin_dir: Path) -> None:
    """Generate ``manifest.json`` from the specification."""
    manifest = {
        "plugin_name": spec["plugin_name"],
        "version": spec["version"],
        "author": spec["author"],
        "lifecycle_event": spec["lifecycle_event"],
        "entry_point": spec["entry_point"],
        "enabled": spec["enabled"],
        "generated_at": datetime.datetime.utcnow().isoformat(),
        "contract_version": "1.0.0",
    }
    with open(plugin_dir / "manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)


def generate_policy_snapshot(spec: Dict, plugin_dir: Path) -> None:
    """Generate a placeholder ``policy_snapshot.json``.

    In a full implementation this would capture allowed and forbidden
    actions along with the active policy version.  Here we mirror the
    input specification for demonstration purposes.
    """
    snapshot = {
        "plugin_name": spec["plugin_name"],
        "policy_version": "1.0.0",
        "allowed_actions": spec.get("allowed_actions", []),
        "forbidden_actions": spec.get("forbidden_actions", []),
    }
    with open(plugin_dir / "policy_snapshot.json", "w") as f:
        json.dump(snapshot, f, indent=2)


def generate_ledger_contract(spec: Dict, plugin_dir: Path) -> None:
    """Generate ``ledger_contract.json``.

    This contract defines the fields that must be recorded in the
    append‑only ledger for each plugin execution.  The example includes
    core fields plus any fields declared in the output schema.
    """
    required_fields = ["timestamp", "trace_id"] + spec["output_schema"].get(
        "required", []
    )
    contract = {
        "plugin_name": spec["plugin_name"],
        "required_fields": list(dict.fromkeys(required_fields)),
    }
    with open(plugin_dir / "ledger_contract.json", "w") as f:
        json.dump(contract, f, indent=2)


def generate_readme(spec: Dict, plugin_dir: Path) -> None:
    """Generate ``README_PLUGIN.md`` describing the plugin."""
    readme = f"""# {spec['plugin_name']}

> Version: {spec['version']}  
> Lifecycle Event: {spec['lifecycle_event']}  
> Author: {spec['author']}

## Description

{spec['description']}

## Input Schema

```json
{json.dumps(spec['input_schema'], indent=2)}
```

## Output Schema

```json
{json.dumps(spec['output_schema'], indent=2)}
```

## Dependencies

### Python Packages
{chr(10).join(f"- {pkg}" for pkg in spec['dependencies'].get('python_packages', []))}

### PowerShell Modules
{chr(10).join(f"- {mod}" for mod in spec['dependencies'].get('powershell_modules', []))}

## Configuration

- **Timeout**: {spec['timeout_seconds']} seconds
- **Risk Level**: {spec['risk_level']}
- **Rollback Supported**: {'Yes' if spec['rollback_supported'] else 'No'}

## Usage

This plugin is automatically invoked during the `{spec['lifecycle_event']}` lifecycle event.

## Testing

```bash
pytest plugins/{spec['plugin_name']}/tests/ -v
```

## Validation

```bash
./core/Validate-Plugin.ps1 -PluginPath "plugins/{spec['plugin_name']}"
```

---

*This document was auto‑generated from plugin.spec.json on {datetime.datetime.utcnow().isoformat()}*"""
    with open(plugin_dir / "README_PLUGIN.md", "w") as f:
        f.write(readme)


def generate_healthcheck(spec: Dict, plugin_dir: Path) -> None:
    """Generate ``healthcheck.md`` to aid monitoring the plugin."""
    healthcheck = f"""# Healthcheck: {spec['plugin_name']}

## Monitoring Guidelines

### Expected Behavior

- **Execution Time**: Should complete within {spec['timeout_seconds']} seconds
- **Success Rate**: Should maintain >99% success rate
- **Error Patterns**: Structured errors with trace IDs

### Metrics to Monitor

```
r_pipeline_plugin_execution_duration_seconds{{plugin="{spec['plugin_name']}"}}
r_pipeline_plugin_execution_total{{plugin="{spec['plugin_name']}", status="success"}}
r_pipeline_plugin_execution_total{{plugin="{spec['plugin_name']}", status="error"}}
```

### Alerting Thresholds

| Metric | Threshold | Action |
|--------|-----------|--------|
| Execution Duration | > {spec['timeout_seconds']}s | Investigate slow performance |
| Error Rate | > 1% | Check recent code changes |
| Not Executed | > 1 hour | Verify plugin is enabled |

### Manual Health Check

```bash
# Test plugin in isolation
python plugins/{spec['plugin_name']}/{spec['entry_point']} << 'EOF'
{{
  "file_path": "test.txt",
  "trace_id": "health-check-001"
}}
EOF
```

Expected output: `{{"status": "success", ...}}`

### Common Issues

1. **Timeout Errors**
   - Check for slow external API calls
   - Verify database connection pools

2. **Missing Dependencies**
   - Ensure all packages installed: `pip install -r requirements.txt`

3. **Permission Errors**
   - Verify plugin runs as `r_pipeline` user

---

*Auto‑generated healthcheck documentation*
"""
    with open(plugin_dir / "healthcheck.md", "w") as f:
        f.write(healthcheck)
