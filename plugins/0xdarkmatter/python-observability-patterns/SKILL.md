---
name: python-observability-patterns
description: "Observability patterns for Python applications. Triggers on: logging, metrics, tracing, opentelemetry, prometheus, observability, monitoring, structlog, correlation id."
compatibility: "Python 3.10+. Requires structlog, opentelemetry-api, prometheus-client."
allowed-tools: "Read Write"
depends-on: [python-async-patterns]
related-skills: [python-fastapi-patterns, python-cli-patterns]
---

# Python Observability Patterns

Logging, metrics, and tracing for production applications.

## Structured Logging with structlog

```python
import structlog

# Configure structlog
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
)

logger = structlog.get_logger()

# Usage
logger.info("user_created", user_id=123, email="test@example.com")
# Output: {"event": "user_created", "user_id": 123, "email": "test@example.com", "level": "info", "timestamp": "2024-01-15T10:00:00Z"}
```

## Request Context Propagation

```python
import structlog
from contextvars import ContextVar
from uuid import uuid4

request_id_var: ContextVar[str] = ContextVar("request_id", default="")

def bind_request_context(request_id: str | None = None):
    """Bind request ID to logging context."""
    rid = request_id or str(uuid4())
    request_id_var.set(rid)
    structlog.contextvars.bind_contextvars(request_id=rid)
    return rid

# FastAPI middleware
@app.middleware("http")
async def request_context_middleware(request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid4())
    bind_request_context(request_id)
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    structlog.contextvars.clear_contextvars()
    return response
```

## Prometheus Metrics

```python
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import FastAPI, Response

# Define metrics
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    ["method", "endpoint"],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 5.0]
)

ACTIVE_CONNECTIONS = Gauge(
    "active_connections",
    "Number of active connections"
)

# Middleware to record metrics
@app.middleware("http")
async def metrics_middleware(request, call_next):
    ACTIVE_CONNECTIONS.inc()
    start = time.perf_counter()

    response = await call_next(request)

    duration = time.perf_counter() - start
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)
    ACTIVE_CONNECTIONS.dec()

    return response

# Metrics endpoint
@app.get("/metrics")
async def metrics():
    return Response(
        content=generate_latest(),
        media_type="text/plain"
    )
```

## OpenTelemetry Tracing

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# Setup
provider = TracerProvider()
processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="localhost:4317"))
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

tracer = trace.get_tracer(__name__)

# Manual instrumentation
async def process_order(order_id: int):
    with tracer.start_as_current_span("process_order") as span:
        span.set_attribute("order_id", order_id)

        with tracer.start_as_current_span("validate_order"):
            await validate(order_id)

        with tracer.start_as_current_span("charge_payment"):
            await charge(order_id)
```

## Quick Reference

| Library | Purpose |
|---------|---------|
| structlog | Structured logging |
| prometheus-client | Metrics collection |
| opentelemetry | Distributed tracing |

| Metric Type | Use Case |
|-------------|----------|
| Counter | Total requests, errors |
| Histogram | Latencies, sizes |
| Gauge | Current connections, queue size |

## Additional Resources

- `./references/structured-logging.md` - structlog configuration, formatters
- `./references/metrics.md` - Prometheus patterns, custom metrics
- `./references/tracing.md` - OpenTelemetry, distributed tracing

## Assets

- `./assets/logging-config.py` - Production logging configuration

---

## See Also

**Prerequisites:**
- `python-async-patterns` - Async context propagation

**Related Skills:**
- `python-fastapi-patterns` - API middleware for metrics/tracing
- `python-cli-patterns` - CLI logging patterns

**Integration Skills:**
- `python-database-patterns` - Database query tracing
