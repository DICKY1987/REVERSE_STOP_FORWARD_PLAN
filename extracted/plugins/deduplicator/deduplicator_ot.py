# plugins/deduplicator/deduplicator.py
from opentelemetry import trace
import logging

# Get tracer
tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)

def detect_duplicate(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Detect duplicates with OpenTelemetry tracing"""
    
    # Extract trace ID from input
    trace_id = input_data.get("trace_id", "unknown")
    
    # Create span for this operation
    with tracer.start_as_current_span(
        "detect_duplicate",
        attributes={
            "plugin.name": "deduplicator",
            "plugin.version": "1.0.0",
            "trace.id": trace_id,
            "file.path": input_data.get("file_path", ""),
        }
    ) as span:
        try:
            # Your plugin logic here
            logger.info(f"[{trace_id}] Starting duplicate detection")
            
            # Add events to span
            span.add_event("Checking hash database")
            
            # ... duplicate detection logic ...
            
            span.add_event("Duplicate check complete", {
                "is_duplicate": is_duplicate
            })
            
            # Set span status
            span.set_status(trace.Status(trace.StatusCode.OK))
            
            result = {
                "status": "success",
                "is_duplicate": is_duplicate,
                "trace_id": trace_id
            }
            
            # Add result to span attributes
            span.set_attributes({
                "result.status": "success",
                "result.is_duplicate": is_duplicate
            })
            
            return result
            
        except Exception as e:
            # Record exception in span
            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            
            logger.error(f"[{trace_id}] Error: {e}", exc_info=True)
            
            return {
                "status": "error",
                "error_message": str(e),
                "trace_id": trace_id
            }