# Distributed Tracing with OpenTelemetry

Trace requests across services for debugging and performance analysis.

## Setup

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource

# Create resource with service info
resource = Resource.create({
    "service.name": "my-service",
    "service.version": "1.0.0",
    "deployment.environment": "production",
})

# Create and configure tracer provider
provider = TracerProvider(resource=resource)

# Export to OTLP collector (Jaeger, Tempo, etc.)
otlp_exporter = OTLPSpanExporter(
    endpoint="http://localhost:4317",
    insecure=True,
)
provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

# Set as global tracer provider
trace.set_tracer_provider(provider)

# Get tracer for your module
tracer = trace.get_tracer(__name__)
```

## FastAPI Auto-Instrumentation

```python
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor

# Instrument FastAPI
FastAPIInstrumentor.instrument_app(app)

# Instrument HTTP client
HTTPXClientInstrumentor().instrument()

# Instrument database
SQLAlchemyInstrumentor().instrument(engine=engine)

# Instrument Redis
RedisInstrumentor().instrument()
```

## Manual Instrumentation

```python
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

tracer = trace.get_tracer(__name__)

async def process_order(order_id: int):
    """Process order with detailed tracing."""
    with tracer.start_as_current_span("process_order") as span:
        # Add attributes
        span.set_attribute("order.id", order_id)
        span.set_attribute("order.type", "standard")

        # Nested spans
        with tracer.start_as_current_span("validate_order"):
            order = await validate(order_id)
            span.set_attribute("order.items", len(order.items))

        with tracer.start_as_current_span("check_inventory"):
            await check_inventory(order.items)

        with tracer.start_as_current_span("process_payment") as payment_span:
            try:
                result = await charge_payment(order)
                payment_span.set_attribute("payment.amount", float(order.total))
            except PaymentError as e:
                payment_span.set_status(Status(StatusCode.ERROR, str(e)))
                payment_span.record_exception(e)
                raise

        with tracer.start_as_current_span("send_confirmation"):
            await send_email(order.customer_email)

        span.set_status(Status(StatusCode.OK))
        return order
```

## Context Propagation

```python
from opentelemetry import trace
from opentelemetry.propagate import inject, extract
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

propagator = TraceContextTextMapPropagator()

# Inject context into outgoing HTTP headers
async def call_external_service(data: dict):
    headers = {}
    inject(headers)  # Adds traceparent header

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.example.com/process",
            json=data,
            headers=headers,
        )
    return response.json()


# Extract context from incoming request (usually handled by instrumentation)
@app.middleware("http")
async def trace_middleware(request: Request, call_next):
    # Extract trace context from headers
    ctx = extract(dict(request.headers))

    with tracer.start_as_current_span(
        f"{request.method} {request.url.path}",
        context=ctx,
    ):
        return await call_next(request)
```

## Adding Events and Exceptions

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

async def process_with_events():
    with tracer.start_as_current_span("process") as span:
        # Add event (point-in-time occurrence)
        span.add_event("processing_started", {
            "items": 10,
        })

        try:
            result = await heavy_processing()
            span.add_event("processing_completed", {
                "result_count": len(result),
            })
        except Exception as e:
            # Record exception in span
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
            raise

        return result
```

## Span Decorator

```python
from functools import wraps
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

def traced(span_name: str | None = None, attributes: dict | None = None):
    """Decorator to trace function execution."""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            name = span_name or f"{func.__module__}.{func.__name__}"
            with tracer.start_as_current_span(name) as span:
                if attributes:
                    for key, value in attributes.items():
                        span.set_attribute(key, value)
                try:
                    result = await func(*args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    return result
                except Exception as e:
                    span.record_exception(e)
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            name = span_name or f"{func.__module__}.{func.__name__}"
            with tracer.start_as_current_span(name) as span:
                if attributes:
                    for key, value in attributes.items():
                        span.set_attribute(key, value)
                try:
                    result = func(*args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    return result
                except Exception as e:
                    span.record_exception(e)
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    raise

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    return decorator


# Usage
@traced("user.create", {"component": "users"})
async def create_user(user: UserCreate):
    return await db.create(user)
```

## Linking Traces to Logs

```python
import structlog
from opentelemetry import trace

def add_trace_context(_, __, event_dict):
    """Add trace context to log entries."""
    span = trace.get_current_span()
    if span.is_recording():
        ctx = span.get_span_context()
        event_dict["trace_id"] = format(ctx.trace_id, "032x")
        event_dict["span_id"] = format(ctx.span_id, "016x")
    return event_dict


structlog.configure(
    processors=[
        add_trace_context,
        structlog.processors.JSONRenderer(),
    ],
)
```

## Sampling

```python
from opentelemetry.sdk.trace.sampling import (
    TraceIdRatioBased,
    ParentBased,
    ALWAYS_ON,
)

# Sample 10% of traces
sampler = TraceIdRatioBased(0.1)

# Respect parent's sampling decision, default to 10%
sampler = ParentBased(root=TraceIdRatioBased(0.1))

# Always sample (development)
sampler = ALWAYS_ON

provider = TracerProvider(
    resource=resource,
    sampler=sampler,
)
```

## Quick Reference

| Concept | Description |
|---------|-------------|
| Trace | Complete request journey |
| Span | Single operation within trace |
| Context | Propagated trace information |
| Attribute | Key-value metadata on span |
| Event | Point-in-time occurrence |

| Instrumentation | Package |
|-----------------|---------|
| FastAPI | `opentelemetry-instrumentation-fastapi` |
| httpx | `opentelemetry-instrumentation-httpx` |
| SQLAlchemy | `opentelemetry-instrumentation-sqlalchemy` |
| Redis | `opentelemetry-instrumentation-redis` |
| Celery | `opentelemetry-instrumentation-celery` |
