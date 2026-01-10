# Structured Logging with structlog

Production logging patterns for Python applications.

## Basic Setup

```python
import logging
import structlog
import sys

def configure_logging(json_output: bool = True, log_level: str = "INFO"):
    """Configure structlog for production."""

    # Shared processors for both stdlib and structlog
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    if json_output:
        # Production: JSON output
        renderer = structlog.processors.JSONRenderer()
    else:
        # Development: colored console output
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=shared_processors + [
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure standard library logging
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    ))

    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level)


# Usage
configure_logging(json_output=True, log_level="INFO")
logger = structlog.get_logger()
```

## Context Variables

```python
import structlog
from contextvars import ContextVar
from uuid import uuid4

# Request context
request_id_var: ContextVar[str] = ContextVar("request_id", default="")
user_id_var: ContextVar[int | None] = ContextVar("user_id", default=None)

def bind_request_context(request_id: str | None = None, user_id: int | None = None):
    """Bind context that will be included in all log messages."""
    rid = request_id or str(uuid4())
    request_id_var.set(rid)

    context = {"request_id": rid}
    if user_id:
        user_id_var.set(user_id)
        context["user_id"] = user_id

    structlog.contextvars.bind_contextvars(**context)
    return rid

def clear_request_context():
    """Clear context at end of request."""
    structlog.contextvars.clear_contextvars()


# FastAPI middleware
from fastapi import Request

@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    # Extract or generate request ID
    request_id = request.headers.get("X-Request-ID", str(uuid4()))
    bind_request_context(request_id=request_id)

    # Log request
    logger.info(
        "request_started",
        method=request.method,
        path=request.url.path,
        client=request.client.host if request.client else None,
    )

    try:
        response = await call_next(request)
        logger.info(
            "request_completed",
            status_code=response.status_code,
        )
        response.headers["X-Request-ID"] = request_id
        return response
    except Exception as e:
        logger.exception("request_failed", error=str(e))
        raise
    finally:
        clear_request_context()
```

## Exception Logging

```python
import structlog

logger = structlog.get_logger()

# Log exception with context
try:
    result = risky_operation()
except ValueError as e:
    logger.error(
        "operation_failed",
        error=str(e),
        error_type=type(e).__name__,
    )
    raise

# Log with full traceback
try:
    result = another_operation()
except Exception:
    logger.exception("unexpected_error")  # Includes full traceback
    raise


# Custom exception with context
class OrderError(Exception):
    def __init__(self, message: str, order_id: int, **context):
        super().__init__(message)
        self.order_id = order_id
        self.context = context

try:
    process_order(order_id=123)
except OrderError as e:
    logger.error(
        "order_processing_failed",
        order_id=e.order_id,
        **e.context,
    )
```

## Filtering Sensitive Data

```python
import structlog
import re

def filter_sensitive_data(_, __, event_dict):
    """Remove sensitive data from logs."""
    sensitive_keys = {"password", "token", "secret", "api_key", "authorization"}

    def redact(data):
        if isinstance(data, dict):
            return {
                k: "[REDACTED]" if k.lower() in sensitive_keys else redact(v)
                for k, v in data.items()
            }
        elif isinstance(data, list):
            return [redact(item) for item in data]
        elif isinstance(data, str):
            # Redact emails
            return re.sub(
                r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
                '[EMAIL]',
                data
            )
        return data

    return redact(event_dict)


structlog.configure(
    processors=[
        filter_sensitive_data,
        structlog.processors.JSONRenderer(),
    ],
)
```

## Log Levels and Events

```python
logger = structlog.get_logger()

# Use semantic event names
logger.debug("cache_lookup", key="user:123", hit=True)
logger.info("user_created", user_id=123, email="user@example.com")
logger.warning("rate_limit_approaching", current=95, limit=100)
logger.error("payment_failed", order_id=456, reason="insufficient_funds")
logger.critical("database_connection_lost", host="db.example.com")

# Business events
logger.info("order_placed", order_id=789, total=99.99, items=3)
logger.info("order_shipped", order_id=789, carrier="ups", tracking="1Z...")
logger.info("user_login", user_id=123, method="oauth", provider="google")
```

## Integration with Third-Party Loggers

```python
import structlog
import logging

# Capture logs from libraries
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

# Create a structlog-wrapped stdlib logger for compatibility
def get_stdlib_logger(name: str):
    """Get a structlog logger that works with libraries expecting stdlib."""
    return structlog.wrap_logger(
        logging.getLogger(name),
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ]
    )
```

## Performance Logging

```python
import structlog
import time
from contextlib import contextmanager

logger = structlog.get_logger()

@contextmanager
def log_duration(event: str, **context):
    """Context manager to log operation duration."""
    start = time.perf_counter()
    try:
        yield
        duration = time.perf_counter() - start
        logger.info(
            event,
            duration_ms=round(duration * 1000, 2),
            status="success",
            **context,
        )
    except Exception as e:
        duration = time.perf_counter() - start
        logger.error(
            event,
            duration_ms=round(duration * 1000, 2),
            status="error",
            error=str(e),
            **context,
        )
        raise


# Usage
with log_duration("database_query", table="users"):
    users = await db.fetch_users()
```

## Quick Reference

| Function | Purpose |
|----------|---------|
| `structlog.get_logger()` | Get logger instance |
| `bind_contextvars()` | Add context to all logs |
| `clear_contextvars()` | Clear request context |
| `logger.exception()` | Log with traceback |

| Processor | Purpose |
|-----------|---------|
| `TimeStamper(fmt="iso")` | Add timestamp |
| `add_log_level` | Add level field |
| `JSONRenderer()` | Output as JSON |
| `ConsoleRenderer()` | Pretty console output |
