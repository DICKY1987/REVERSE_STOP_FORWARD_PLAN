"""OpenTelemetry configuration for R_PIPELINE

This module sets up a global tracer for the R_PIPELINE system.  It
defines a helper function that configures a `TracerProvider` with a
resource describing the service, attaches a batch span processor with
an OTLP exporter, and registers the provider with the global OpenTelemetry
API.  The exported tracer can be imported by other modules to create
spans.  All configuration values, such as the OTLP endpoint and
deployment environment, are read from environment variables to keep
the code deterministic and side‑effect free.
"""

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
import os


def setup_opentelemetry():
    """Initialize OpenTelemetry for R_PIPELINE.

    Creates a `TracerProvider` configured with a service name, version and
    deployment environment.  A batch span processor sends spans to an
    OTLP endpoint, which defaults to ``http://localhost:4318/v1/traces`` but
    can be overridden via the ``OTEL_EXPORTER_OTLP_ENDPOINT`` environment
    variable.  Once configured, the provider is registered as the global
    tracer provider and a tracer for this module is returned.

    Returns:
        A tracer instance bound to this module.
    """
    # Create resource with service information
    resource = Resource.create({
        "service.name": "r_pipeline",
        "service.version": "1.0.0",
        "deployment.environment": os.getenv("R_PIPELINE_ENV", "development"),
    })

    # Create tracer provider
    provider = TracerProvider(resource=resource)

    # Configure OTLP exporter
    otlp_exporter = OTLPSpanExporter(
        endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318/v1/traces")
    )

    # Add span processor
    provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

    # Set global tracer provider
    trace.set_tracer_provider(provider)

    return trace.get_tracer(__name__)


# Global tracer initialized at import time
tracer = setup_opentelemetry()