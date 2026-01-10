# Async Performance Optimization

Performance patterns for high-throughput async applications.

## uvloop - Drop-in Event Loop Replacement

```python
# Install: pip install uvloop

# Option 1: Install as default (before any asyncio calls)
import uvloop
uvloop.install()

# Then use asyncio normally
import asyncio

async def main():
    # Now using uvloop
    pass

asyncio.run(main())


# Option 2: Use explicitly
import asyncio
import uvloop

async def main():
    pass

with asyncio.Runner(loop_factory=uvloop.new_event_loop) as runner:
    runner.run(main())


# Option 3: Check if available
def get_event_loop_policy():
    try:
        import uvloop
        return uvloop.EventLoopPolicy()
    except ImportError:
        return asyncio.DefaultEventLoopPolicy()

asyncio.set_event_loop_policy(get_event_loop_policy())
```

**Performance gains:**
- 2-4x faster than default asyncio event loop
- Significant improvement for I/O-bound workloads
- Based on libuv (same as Node.js)

## Connection Pool Tuning

```python
import aiohttp

# Optimal connector settings
connector = aiohttp.TCPConnector(
    limit=100,              # Total connection limit
    limit_per_host=30,      # Per-host limit (prevents overwhelming one server)
    ttl_dns_cache=300,      # DNS cache TTL (seconds)
    use_dns_cache=True,     # Enable DNS caching
    keepalive_timeout=30,   # Keep connections alive (seconds)
    enable_cleanup_closed=True,  # Clean up closed connections
)

async with aiohttp.ClientSession(connector=connector) as session:
    # Use session
    pass


# Database connection pool (asyncpg)
import asyncpg

pool = await asyncpg.create_pool(
    dsn="postgresql://user:pass@localhost/db",
    min_size=5,        # Minimum connections to keep
    max_size=20,       # Maximum connections allowed
    max_inactive_connection_lifetime=300.0,  # Close idle connections
    command_timeout=60.0,  # Query timeout
)


# Redis connection pool (aioredis/redis-py)
import redis.asyncio as redis

pool = redis.ConnectionPool.from_url(
    "redis://localhost",
    max_connections=50,
    decode_responses=True,
)
client = redis.Redis(connection_pool=pool)
```

### Pool Sizing Guidelines

| Service Type | Min Size | Max Size | Notes |
|--------------|----------|----------|-------|
| Database (heavy) | 10 | 50 | Match CPU cores × 2-4 |
| Database (light) | 5 | 20 | Standard web apps |
| HTTP external API | N/A | 100 | Limited by rate limits |
| HTTP per-host | N/A | 30 | Prevent overwhelming |
| Redis | 10 | 50 | Very fast, less critical |

## Buffer Sizing

```python
# aiohttp response reading
async def fetch_large(session, url):
    async with session.get(url) as response:
        # Default: reads entire response into memory
        data = await response.read()

        # For large responses, stream:
        chunks = []
        async for chunk in response.content.iter_chunked(8192):
            chunks.append(chunk)


# Custom buffer sizes for TCP
import asyncio

async def create_connection():
    reader, writer = await asyncio.open_connection(
        "localhost", 8888,
        limit=2**20,  # 1MB read buffer (default is 64KB)
    )
    return reader, writer


# aiohttp server with custom limits
from aiohttp import web

app = web.Application(
    client_max_size=1024 * 1024 * 100,  # 100MB max request body
)
```

## Batching Requests

```python
import asyncio
from collections import defaultdict
from typing import TypeVar, Callable

T = TypeVar("T")

class BatchProcessor:
    """Batch multiple requests into single operations."""

    def __init__(
        self,
        batch_func: Callable[[list[str]], dict[str, T]],
        max_batch_size: int = 100,
        max_delay: float = 0.01  # 10ms
    ):
        self._batch_func = batch_func
        self._max_batch_size = max_batch_size
        self._max_delay = max_delay
        self._pending: dict[str, asyncio.Future] = {}
        self._batch: list[str] = []
        self._lock = asyncio.Lock()
        self._timer: asyncio.Task | None = None

    async def get(self, key: str) -> T:
        """Get single item (batched with other requests)."""
        async with self._lock:
            if key in self._pending:
                return await self._pending[key]

            future = asyncio.get_event_loop().create_future()
            self._pending[key] = future
            self._batch.append(key)

            if len(self._batch) >= self._max_batch_size:
                await self._flush()
            elif not self._timer:
                self._timer = asyncio.create_task(self._delayed_flush())

        return await future

    async def _delayed_flush(self):
        await asyncio.sleep(self._max_delay)
        async with self._lock:
            await self._flush()

    async def _flush(self):
        if not self._batch:
            return

        batch = self._batch
        pending = self._pending
        self._batch = []
        self._pending = {}
        self._timer = None

        try:
            results = await self._batch_func(batch)
            for key in batch:
                if key in results:
                    pending[key].set_result(results[key])
                else:
                    pending[key].set_exception(KeyError(key))
        except Exception as e:
            for key in batch:
                pending[key].set_exception(e)


# Usage
async def batch_fetch_users(user_ids: list[str]) -> dict[str, User]:
    # Single database query for multiple users
    return {u.id: u for u in await db.fetch_users(user_ids)}

user_batcher = BatchProcessor(batch_fetch_users, max_batch_size=50)

# These will be batched together:
user1 = await user_batcher.get("user-1")
user2 = await user_batcher.get("user-2")
```

## Task Prioritization

```python
import asyncio
import heapq
from dataclasses import dataclass, field
from typing import Any

@dataclass(order=True)
class PrioritizedTask:
    priority: int
    item: Any = field(compare=False)

class PriorityQueue:
    """Async priority queue for task ordering."""

    def __init__(self):
        self._queue: list[PrioritizedTask] = []
        self._condition = asyncio.Condition()

    async def put(self, priority: int, item: Any):
        async with self._condition:
            heapq.heappush(self._queue, PrioritizedTask(priority, item))
            self._condition.notify()

    async def get(self) -> Any:
        async with self._condition:
            while not self._queue:
                await self._condition.wait()
            return heapq.heappop(self._queue).item


# Usage
queue = PriorityQueue()

# Lower number = higher priority
await queue.put(1, "critical task")
await queue.put(10, "low priority task")
await queue.put(5, "normal task")
```

## Memory Optimization

```python
import asyncio
from weakref import WeakValueDictionary

# Use weak references for caches
class AsyncCache:
    """Memory-efficient async cache using weak references."""

    def __init__(self, fetch_func):
        self._cache = WeakValueDictionary()
        self._fetch_func = fetch_func
        self._locks: dict[str, asyncio.Lock] = {}

    async def get(self, key: str):
        if key in self._cache:
            return self._cache[key]

        if key not in self._locks:
            self._locks[key] = asyncio.Lock()

        async with self._locks[key]:
            if key in self._cache:
                return self._cache[key]

            value = await self._fetch_func(key)
            self._cache[key] = value
            return value


# Limit concurrent operations to prevent memory spikes
async def process_large_dataset(items: list, concurrency: int = 10):
    """Process items with limited concurrency."""
    semaphore = asyncio.Semaphore(concurrency)

    async def process_one(item):
        async with semaphore:
            result = await heavy_processing(item)
            return result

    # Process in chunks to avoid memory issues with huge lists
    chunk_size = 1000
    all_results = []

    for i in range(0, len(items), chunk_size):
        chunk = items[i:i + chunk_size]
        results = await asyncio.gather(*[process_one(item) for item in chunk])
        all_results.extend(results)

    return all_results
```

## Profiling Async Code

```python
import asyncio
import time
from contextlib import asynccontextmanager

@asynccontextmanager
async def async_timer(name: str):
    """Context manager to time async operations."""
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        print(f"{name}: {elapsed:.3f}s")


# Usage
async with async_timer("fetch_all"):
    results = await fetch_all(urls)


# Detailed profiling
class AsyncProfiler:
    def __init__(self):
        self.timings: dict[str, list[float]] = {}

    @asynccontextmanager
    async def profile(self, name: str):
        start = time.perf_counter()
        try:
            yield
        finally:
            elapsed = time.perf_counter() - start
            if name not in self.timings:
                self.timings[name] = []
            self.timings[name].append(elapsed)

    def report(self):
        for name, times in self.timings.items():
            avg = sum(times) / len(times)
            total = sum(times)
            print(f"{name}: avg={avg:.3f}s, total={total:.3f}s, count={len(times)}")


# Use yappi for comprehensive profiling
# pip install yappi
import yappi

yappi.set_clock_type("wall")  # For async code
yappi.start()

asyncio.run(main())

yappi.stop()
yappi.get_func_stats().print_all()
```

## Quick Reference

| Optimization | Impact | When to Use |
|--------------|--------|-------------|
| uvloop | 2-4x throughput | Always (production) |
| Connection pooling | Reduce latency | Any external service |
| Request batching | N requests → 1 | Database, APIs |
| Semaphore limiting | Memory control | Large datasets |
| Streaming | Memory efficiency | Large responses |
| Priority queue | Latency SLAs | Mixed workloads |

## Performance Checklist

```markdown
- [ ] uvloop installed and configured
- [ ] Connection pools properly sized
- [ ] Timeouts on all external calls
- [ ] Semaphores limiting concurrency
- [ ] Large responses streamed
- [ ] DNS caching enabled
- [ ] Connection keep-alive configured
- [ ] Profiling in place for hot paths
```
