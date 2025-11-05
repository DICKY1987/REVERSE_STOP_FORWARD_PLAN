"""Main pipeline runner with trace ID propagation.

This module defines a ``run_pipeline`` function used to orchestrate
R_PIPELINE executions.  It ensures that every run has a unique trace ID
and that OpenTelemetry spans are created around each lifecycle event.
Each plugin executed by the pipeline receives the same trace ID so that
operations can be correlated end‑to‑end.  A helper function
``execute_lifecycle_plugins`` is provided to iterate over plugins for
a given event; in a real implementation ``get_plugins_for_event`` would
discover and load the appropriate plugin handlers.
"""

import uuid
from opentelemetry import trace


tracer = trace.get_tracer(__name__)


def run_pipeline(file_path: str, trace_id: str | None = None) -> None:
    """Run R_PIPELINE with trace ID propagation.

    Args:
        file_path: Path to the file being processed.
        trace_id: Optional external trace ID.  If not provided, a new
            UUID‑based trace ID will be generated.

    The function prints status messages to stdout and creates nested spans
    around each lifecycle event.  At the end of the run the root span is
    marked with an OK status to indicate success.
    """
    # Generate trace ID if not provided
    if not trace_id:
        trace_id = f"trace-{uuid.uuid4()}"

    # Create root span for entire pipeline run
    with tracer.start_as_current_span(
        "pipeline_run",
        attributes={
            "trace.id": trace_id,
            "file.path": file_path,
        },
    ) as root_span:
        print(f"[{trace_id}] Starting pipeline for: {file_path}")

        # Execute lifecycle: FileDetected
        with tracer.start_as_current_span("lifecycle.file_detected") as span:
            detected_plugins = execute_lifecycle_plugins(
                "FileDetected", {"file_path": file_path, "trace_id": trace_id}
            )
            span.set_attribute("plugins.count", len(detected_plugins))

        # Execute lifecycle: PreMerge
        with tracer.start_as_current_span("lifecycle.pre_merge") as span:
            premerge_plugins = execute_lifecycle_plugins(
                "PreMerge", {"file_path": file_path, "trace_id": trace_id}
            )
            span.set_attribute("plugins.count", len(premerge_plugins))

        # Additional lifecycle events could be added here (e.g. MergeConflict, PostMerge)

        print(f"[{trace_id}] Pipeline complete")
        # Mark root span as successful
        root_span.set_status(trace.Status(trace.StatusCode.OK))


def execute_lifecycle_plugins(event: str, input_data: dict) -> list:
    """Execute all plugins registered for a lifecycle event.

    Args:
        event: Name of the lifecycle event.
        input_data: Input payload passed to each plugin.  Must include
            ``trace_id`` so that plugins can attach spans to the correct
            trace.

    Returns:
        A list of plugin execution results.  This stub uses
        ``get_plugins_for_event`` to find handlers; in an actual system
        this would load plugins from disk or a registry.
    """
    results: list = []
    for plugin in get_plugins_for_event(event):
        # Each plugin gets the same trace_id
        result = plugin.execute(input_data)
        results.append(result)
    return results


def get_plugins_for_event(event: str) -> list:
    """Placeholder for plugin discovery.

    In a real implementation this would inspect the ``plugins`` directory
    for modules whose ``plugin.spec.json`` declares the given lifecycle
    event.  Here we return an empty list to keep the example runnable.
    """
    return []