# Mixing Sync and Async

Patterns for bridging synchronous and asynchronous Python code.

## Running Sync Code from Async

### run_in_executor

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def run_blocking():
    """Run blocking I/O in thread pool."""
    loop = asyncio.get_running_loop()

    # Using default executor (ThreadPoolExecutor)
    result = await loop.run_in_executor(
        None,  # Default executor
        blocking_function,
        arg1, arg2
    )
    return result

# With custom executor
executor = ThreadPoolExecutor(max_workers=4)

async def run_with_custom_executor():
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        executor,
        blocking_function,
        arg1
    )
    return result
```

### CPU-bound with ProcessPoolExecutor

```python
from concurrent.futures import ProcessPoolExecutor

executor = ProcessPoolExecutor(max_workers=4)

async def run_cpu_bound():
    """Run CPU-bound code in process pool."""
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        executor,
        cpu_intensive_function,
        data
    )
    return result
```

### Decorator Pattern

```python
import asyncio
import functools

def run_in_executor(func):
    """Decorator to run sync function in executor."""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None,
            functools.partial(func, *args, **kwargs)
        )
    return wrapper

@run_in_executor
def blocking_io_operation(path):
    with open(path) as f:
        return f.read()

# Usage
async def main():
    content = await blocking_io_operation("file.txt")
```

## Running Async Code from Sync

### asyncio.run()

```python
import asyncio

async def async_function():
    await asyncio.sleep(1)
    return "done"

# From sync code
def sync_wrapper():
    return asyncio.run(async_function())
```

### Nested Event Loops (nest_asyncio)

```python
# For Jupyter notebooks or nested contexts
import nest_asyncio
nest_asyncio.apply()

# Now asyncio.run() works even if event loop is running
```

### Thread with Event Loop

```python
import asyncio
import threading

def run_in_new_thread(coro):
    """Run coroutine in a new thread with its own event loop."""
    result = None
    exception = None

    def runner():
        nonlocal result, exception
        try:
            result = asyncio.run(coro)
        except Exception as e:
            exception = e

    thread = threading.Thread(target=runner)
    thread.start()
    thread.join()

    if exception:
        raise exception
    return result
```

## Common Pitfalls

### DON'T: Call asyncio.run() from async

```python
# WRONG - nested asyncio.run()
async def bad():
    result = asyncio.run(other_async())  # RuntimeError!

# CORRECT - just await
async def good():
    result = await other_async()
```

### DON'T: Use time.sleep() in async

```python
# WRONG - blocks event loop
async def bad():
    time.sleep(5)  # Blocks entire event loop!

# CORRECT
async def good():
    await asyncio.sleep(5)
```

### DON'T: Use blocking I/O directly

```python
# WRONG - blocks event loop
async def bad():
    with open("file.txt") as f:  # Blocking!
        return f.read()

# CORRECT - use executor
async def good():
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, read_file, "file.txt")

# OR use async file library
import aiofiles
async def better():
    async with aiofiles.open("file.txt") as f:
        return await f.read()
```

## Synchronization Primitives

### Threading Lock vs asyncio Lock

```python
import threading
import asyncio

# For sync code
sync_lock = threading.Lock()

# For async code
async_lock = asyncio.Lock()

# DON'T mix them!
# threading.Lock() in async code blocks event loop
# asyncio.Lock() in sync code doesn't work
```

### Thread-Safe Queue for Sync/Async Bridge

```python
import asyncio
import queue
import threading

def sync_producer(q: queue.Queue):
    """Sync code putting items."""
    for i in range(10):
        q.put(i)
    q.put(None)  # Sentinel

async def async_consumer(q: queue.Queue):
    """Async code getting items from sync queue."""
    loop = asyncio.get_running_loop()
    while True:
        # Non-blocking get in executor
        item = await loop.run_in_executor(None, q.get)
        if item is None:
            break
        await process(item)

async def main():
    q = queue.Queue()

    # Start sync producer in thread
    thread = threading.Thread(target=sync_producer, args=(q,))
    thread.start()

    # Consume async
    await async_consumer(q)
    thread.join()
```

## Async-First Database Access

```python
# Instead of sync database drivers, use async versions

# SQLite
import aiosqlite
async def query_db():
    async with aiosqlite.connect("db.sqlite") as db:
        async with db.execute("SELECT * FROM users") as cursor:
            return await cursor.fetchall()

# PostgreSQL
import asyncpg
async def query_postgres():
    conn = await asyncpg.connect("postgresql://...")
    rows = await conn.fetch("SELECT * FROM users")
    await conn.close()
    return rows

# HTTP
import aiohttp
async def fetch_api():
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()
```

## Best Practices

1. **Prefer async libraries** - Use aiohttp, aiosqlite, asyncpg over sync versions
2. **Use run_in_executor for blocking** - Never block the event loop
3. **Keep sync/async boundaries clean** - Don't mix unnecessarily
4. **Use ProcessPoolExecutor for CPU-bound** - ThreadPool for I/O
5. **Don't nest event loops** - Use a single asyncio.run() entry point
6. **Profile before threading** - Async is often enough
