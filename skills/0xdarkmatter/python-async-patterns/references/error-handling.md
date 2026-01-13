# Async Error Handling Patterns

Error handling patterns for resilient async applications.

## Retry with Exponential Backoff

```python
import asyncio
import random
from typing import TypeVar, Callable, Awaitable

T = TypeVar("T")

async def retry_with_backoff(
    func: Callable[[], Awaitable[T]],
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: tuple = (Exception,),
) -> T:
    """
    Retry async function with exponential backoff.

    Args:
        func: Async function to retry
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries (seconds)
        max_delay: Maximum delay between retries (seconds)
        exponential_base: Base for exponential calculation
        jitter: Add randomness to prevent thundering herd
        retryable_exceptions: Exceptions that trigger retry
    """
    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            return await func()
        except retryable_exceptions as e:
            last_exception = e

            if attempt == max_retries:
                raise

            # Calculate delay with exponential backoff
            delay = min(
                base_delay * (exponential_base ** attempt),
                max_delay
            )

            # Add jitter (±25%)
            if jitter:
                delay *= 0.75 + random.random() * 0.5

            await asyncio.sleep(delay)

    raise last_exception  # Should never reach here


# Usage
async def fetch_with_retry(url: str) -> str:
    return await retry_with_backoff(
        lambda: fetch(url),
        max_retries=3,
        retryable_exceptions=(aiohttp.ClientError, asyncio.TimeoutError)
    )
```

## Retry Decorator

```python
import functools
from typing import Type

def async_retry(
    max_retries: int = 3,
    base_delay: float = 1.0,
    exceptions: tuple[Type[Exception], ...] = (Exception,)
):
    """Decorator for async retry with backoff."""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            return await retry_with_backoff(
                lambda: func(*args, **kwargs),
                max_retries=max_retries,
                base_delay=base_delay,
                retryable_exceptions=exceptions
            )
        return wrapper
    return decorator


# Usage
@async_retry(max_retries=3, exceptions=(aiohttp.ClientError,))
async def fetch_data(url: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()
```

## Circuit Breaker

```python
import asyncio
import time
from enum import Enum
from dataclasses import dataclass

class CircuitState(Enum):
    CLOSED = "closed"       # Normal operation
    OPEN = "open"           # Failing, reject calls
    HALF_OPEN = "half_open" # Testing if recovered

@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 5      # Failures before opening
    success_threshold: int = 3      # Successes to close
    timeout: float = 60.0           # Seconds before half-open
    half_open_max_calls: int = 1    # Calls allowed in half-open

class CircuitBreaker:
    """
    Circuit breaker pattern for async operations.

    States:
    - CLOSED: Normal operation, tracking failures
    - OPEN: Rejecting calls, waiting for timeout
    - HALF_OPEN: Testing with limited calls
    """

    def __init__(self, config: CircuitBreakerConfig | None = None):
        self.config = config or CircuitBreakerConfig()
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: float = 0
        self._half_open_calls = 0
        self._lock = asyncio.Lock()

    @property
    def state(self) -> CircuitState:
        return self._state

    async def call(self, func, *args, **kwargs):
        """Execute function through circuit breaker."""
        async with self._lock:
            self._check_state_transition()

            if self._state == CircuitState.OPEN:
                raise CircuitBreakerOpen(
                    f"Circuit open, retry after {self._retry_after():.1f}s"
                )

            if self._state == CircuitState.HALF_OPEN:
                if self._half_open_calls >= self.config.half_open_max_calls:
                    raise CircuitBreakerOpen("Half-open limit reached")
                self._half_open_calls += 1

        try:
            result = await func(*args, **kwargs)
            await self._record_success()
            return result
        except Exception as e:
            await self._record_failure()
            raise

    def _check_state_transition(self):
        """Check if state should transition."""
        if self._state == CircuitState.OPEN:
            if time.time() - self._last_failure_time >= self.config.timeout:
                self._state = CircuitState.HALF_OPEN
                self._half_open_calls = 0
                self._success_count = 0

    async def _record_success(self):
        async with self._lock:
            if self._state == CircuitState.HALF_OPEN:
                self._success_count += 1
                if self._success_count >= self.config.success_threshold:
                    self._state = CircuitState.CLOSED
                    self._failure_count = 0
            else:
                self._failure_count = 0

    async def _record_failure(self):
        async with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.time()

            if self._state == CircuitState.HALF_OPEN:
                self._state = CircuitState.OPEN
            elif self._failure_count >= self.config.failure_threshold:
                self._state = CircuitState.OPEN

    def _retry_after(self) -> float:
        elapsed = time.time() - self._last_failure_time
        return max(0, self.config.timeout - elapsed)

class CircuitBreakerOpen(Exception):
    """Raised when circuit breaker is open."""
    pass


# Usage
breaker = CircuitBreaker(CircuitBreakerConfig(
    failure_threshold=5,
    timeout=30.0
))

async def fetch_with_breaker(url: str):
    return await breaker.call(fetch, url)
```

## Partial Failure Handling

```python
async def fetch_all_with_partial_failure(
    urls: list[str],
    max_failures: int | None = None
) -> tuple[list[str], list[Exception]]:
    """
    Fetch all URLs, collecting both successes and failures.

    Args:
        urls: URLs to fetch
        max_failures: If set, abort after this many failures

    Returns:
        Tuple of (successful_results, exceptions)
    """
    results = await asyncio.gather(
        *[fetch(url) for url in urls],
        return_exceptions=True
    )

    successes = []
    failures = []

    for result in results:
        if isinstance(result, Exception):
            failures.append(result)
            if max_failures and len(failures) >= max_failures:
                # Cancel remaining work if too many failures
                break
        else:
            successes.append(result)

    return successes, failures


# With structured handling
@dataclass
class FetchResult:
    url: str
    data: str | None = None
    error: Exception | None = None

    @property
    def success(self) -> bool:
        return self.error is None

async def fetch_with_result(url: str) -> FetchResult:
    """Wrap fetch in result object."""
    try:
        data = await fetch(url)
        return FetchResult(url=url, data=data)
    except Exception as e:
        return FetchResult(url=url, error=e)

async def fetch_all_structured(urls: list[str]) -> list[FetchResult]:
    """Fetch all URLs with structured results."""
    return await asyncio.gather(*[fetch_with_result(url) for url in urls])
```

## Exception Groups (Python 3.11+)

```python
async def process_with_exception_groups():
    """Handle multiple exceptions from TaskGroup."""
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(task1())
            tg.create_task(task2())
            tg.create_task(task3())
    except* ValueError as eg:
        # Handle all ValueError instances
        for exc in eg.exceptions:
            logger.error(f"ValueError: {exc}")
    except* TypeError as eg:
        # Handle all TypeError instances
        for exc in eg.exceptions:
            logger.error(f"TypeError: {exc}")


# Filtering exception groups
def handle_exception_group(eg: ExceptionGroup):
    """Process exception group by type."""
    critical = []
    recoverable = []

    for exc in eg.exceptions:
        if isinstance(exc, (ConnectionError, TimeoutError)):
            recoverable.append(exc)
        else:
            critical.append(exc)

    # Retry recoverable errors
    for exc in recoverable:
        logger.warning(f"Recoverable error: {exc}")

    # Raise critical errors
    if critical:
        raise ExceptionGroup("Critical errors", critical)
```

## Fallback Pattern

```python
async def with_fallback(
    primary: Callable[[], Awaitable[T]],
    fallback: Callable[[], Awaitable[T]],
    exceptions: tuple = (Exception,)
) -> T:
    """Try primary, fall back on failure."""
    try:
        return await primary()
    except exceptions as e:
        logger.warning(f"Primary failed, using fallback: {e}")
        return await fallback()


# With multiple fallbacks
async def with_fallback_chain(
    *funcs: Callable[[], Awaitable[T]]
) -> T:
    """Try functions in order until one succeeds."""
    last_error = None

    for func in funcs:
        try:
            return await func()
        except Exception as e:
            last_error = e
            continue

    raise last_error or RuntimeError("No fallbacks provided")


# Usage
result = await with_fallback_chain(
    lambda: fetch_from_primary_api(),
    lambda: fetch_from_secondary_api(),
    lambda: fetch_from_cache(),
)
```

## Bulkhead Pattern

```python
class Bulkhead:
    """
    Bulkhead pattern to isolate failures.
    Limits concurrent calls to protect resources.
    """

    def __init__(
        self,
        max_concurrent: int,
        max_waiting: int = 0,
        timeout: float | None = None
    ):
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._max_waiting = max_waiting
        self._waiting = 0
        self._timeout = timeout
        self._lock = asyncio.Lock()

    async def call(self, func, *args, **kwargs):
        """Execute function within bulkhead."""
        async with self._lock:
            if self._waiting >= self._max_waiting:
                raise BulkheadFull("Bulkhead queue full")
            self._waiting += 1

        try:
            if self._timeout:
                async with asyncio.timeout(self._timeout):
                    async with self._semaphore:
                        return await func(*args, **kwargs)
            else:
                async with self._semaphore:
                    return await func(*args, **kwargs)
        finally:
            async with self._lock:
                self._waiting -= 1

class BulkheadFull(Exception):
    """Raised when bulkhead cannot accept more calls."""
    pass


# Usage - isolate external service calls
external_api_bulkhead = Bulkhead(
    max_concurrent=10,  # Max 10 concurrent calls
    max_waiting=50,     # Max 50 in queue
    timeout=30.0        # 30s timeout
)

async def call_external_api(data):
    return await external_api_bulkhead.call(
        lambda: http_client.post("/api", json=data)
    )
```

## Quick Reference

| Pattern | Use Case | Behavior |
|---------|----------|----------|
| Retry + backoff | Transient failures | Retry with increasing delays |
| Circuit breaker | Cascading failures | Fast-fail when service down |
| Fallback | Degraded operation | Use backup on failure |
| Bulkhead | Resource isolation | Limit concurrent access |
| Exception groups | Multiple failures | Handle 3.11+ TaskGroup errors |
| Partial failure | Best-effort batch | Collect successes and failures |
