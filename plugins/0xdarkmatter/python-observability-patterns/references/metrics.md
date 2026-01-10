# Prometheus Metrics Patterns

Application metrics for monitoring and alerting.

## Metric Types

```python
from prometheus_client import Counter, Histogram, Gauge, Summary, Info

# Counter - only goes up (resets on restart)
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status"]
)

# Histogram - distribution of values (latency, sizes)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

# Gauge - can go up and down (current state)
ACTIVE_CONNECTIONS = Gauge(
    "active_connections",
    "Number of active connections"
)

IN_PROGRESS_REQUESTS = Gauge(
    "in_progress_requests",
    "Number of requests currently being processed",
    ["endpoint"]
)

# Summary - like histogram but calculates quantiles client-side
RESPONSE_SIZE = Summary(
    "response_size_bytes",
    "Response size in bytes",
    ["endpoint"]
)

# Info - static labels (version, build info)
APP_INFO = Info(
    "app",
    "Application information"
)
APP_INFO.info({"version": "1.0.0", "environment": "production"})
```

## FastAPI Integration

```python
from fastapi import FastAPI, Request, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
import time

app = FastAPI()

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Record request metrics."""
    # Track in-progress requests
    endpoint = request.url.path
    IN_PROGRESS_REQUESTS.labels(endpoint=endpoint).inc()

    start = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start

    # Record metrics
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=endpoint,
        status=response.status_code
    ).inc()

    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=endpoint
    ).observe(duration)

    IN_PROGRESS_REQUESTS.labels(endpoint=endpoint).dec()

    return response


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
```

## Business Metrics

```python
from prometheus_client import Counter, Histogram

# User actions
USER_SIGNUPS = Counter(
    "user_signups_total",
    "Total user signups",
    ["source", "plan"]
)

USER_LOGINS = Counter(
    "user_logins_total",
    "Total user logins",
    ["method"]  # oauth, password, token
)

# Orders
ORDERS_CREATED = Counter(
    "orders_created_total",
    "Total orders created",
    ["payment_method"]
)

ORDER_VALUE = Histogram(
    "order_value_dollars",
    "Order value distribution",
    buckets=[10, 25, 50, 100, 250, 500, 1000, 2500, 5000]
)

# Errors by type
ERRORS = Counter(
    "errors_total",
    "Total errors by type",
    ["type", "endpoint"]
)


# Usage
async def create_order(order: OrderCreate):
    try:
        result = await process_order(order)
        ORDERS_CREATED.labels(payment_method=order.payment_method).inc()
        ORDER_VALUE.observe(float(order.total))
        return result
    except PaymentError as e:
        ERRORS.labels(type="payment", endpoint="/orders").inc()
        raise
```

## Database Metrics

```python
from prometheus_client import Histogram, Counter, Gauge
from contextlib import asynccontextmanager

DB_QUERY_DURATION = Histogram(
    "db_query_duration_seconds",
    "Database query duration",
    ["operation", "table"]
)

DB_CONNECTIONS_ACTIVE = Gauge(
    "db_connections_active",
    "Active database connections"
)

DB_CONNECTIONS_POOL = Gauge(
    "db_connections_pool",
    "Database connection pool size"
)

DB_ERRORS = Counter(
    "db_errors_total",
    "Database errors",
    ["operation", "error_type"]
)


@asynccontextmanager
async def timed_query(operation: str, table: str):
    """Context manager to time database queries."""
    start = time.perf_counter()
    try:
        yield
    except Exception as e:
        DB_ERRORS.labels(
            operation=operation,
            error_type=type(e).__name__
        ).inc()
        raise
    finally:
        duration = time.perf_counter() - start
        DB_QUERY_DURATION.labels(
            operation=operation,
            table=table
        ).observe(duration)


# Usage
async def get_user(user_id: int):
    async with timed_query("select", "users"):
        return await db.execute(select(User).where(User.id == user_id))
```

## Cache Metrics

```python
CACHE_HITS = Counter(
    "cache_hits_total",
    "Cache hits",
    ["cache_name"]
)

CACHE_MISSES = Counter(
    "cache_misses_total",
    "Cache misses",
    ["cache_name"]
)

CACHE_LATENCY = Histogram(
    "cache_operation_duration_seconds",
    "Cache operation latency",
    ["cache_name", "operation"]
)


async def cached_get(key: str, fetch_func):
    """Get from cache with metrics."""
    start = time.perf_counter()
    value = await cache.get(key)

    if value is not None:
        CACHE_HITS.labels(cache_name="redis").inc()
        CACHE_LATENCY.labels(cache_name="redis", operation="get").observe(
            time.perf_counter() - start
        )
        return value

    CACHE_MISSES.labels(cache_name="redis").inc()

    # Fetch and cache
    value = await fetch_func()
    await cache.set(key, value, ttl=300)

    return value
```

## Custom Collectors

```python
from prometheus_client import Gauge
from prometheus_client.core import GaugeMetricFamily, REGISTRY

class QueueMetricsCollector:
    """Collect queue metrics on demand."""

    def collect(self):
        # This runs when /metrics is scraped
        queue_sizes = get_queue_sizes()  # Your function

        gauge = GaugeMetricFamily(
            "queue_size",
            "Current queue size",
            labels=["queue_name"]
        )

        for name, size in queue_sizes.items():
            gauge.add_metric([name], size)

        yield gauge


# Register collector
REGISTRY.register(QueueMetricsCollector())
```

## Decorators for Metrics

```python
from functools import wraps
import time

def count_calls(counter: Counter, labels: dict | None = None):
    """Decorator to count function calls."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            counter.labels(**(labels or {})).inc()
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def time_calls(histogram: Histogram, labels: dict | None = None):
    """Decorator to time function calls."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start = time.perf_counter()
            try:
                return await func(*args, **kwargs)
            finally:
                duration = time.perf_counter() - start
                histogram.labels(**(labels or {})).observe(duration)
        return wrapper
    return decorator


# Usage
@count_calls(USER_SIGNUPS, {"source": "api", "plan": "free"})
@time_calls(REQUEST_LATENCY, {"method": "POST", "endpoint": "/users"})
async def create_user(user: UserCreate):
    return await db.create_user(user)
```

## Quick Reference

| Metric Type | Use Case | Example |
|-------------|----------|---------|
| Counter | Totals | Requests, errors, signups |
| Histogram | Distributions | Latency, request size |
| Gauge | Current state | Active connections, queue size |
| Summary | Quantiles | Response times (p50, p99) |

| Label Cardinality | Rule |
|-------------------|------|
| Good | method, endpoint, status |
| Bad | user_id, request_id |
| Limit | < 10 unique values per label |
