# Debugging Async Python

Techniques for debugging asyncio applications.

## Enable Debug Mode

```python
import asyncio

# Option 1: Environment variable
# PYTHONASYNCIODEBUG=1 python script.py

# Option 2: In code
asyncio.run(main(), debug=True)

# Option 3: On running loop
loop = asyncio.get_running_loop()
loop.set_debug(True)
```

## Debug Mode Features

When enabled:
- Slow callbacks (>100ms) are logged
- Unawaited coroutines are detected
- Resource warnings for unclosed resources
- More detailed tracebacks

## Finding Slow Callbacks

```python
import asyncio
import logging

# Enable asyncio debug logging
logging.getLogger("asyncio").setLevel(logging.DEBUG)

# Custom slow callback threshold
loop = asyncio.get_event_loop()
loop.slow_callback_duration = 0.05  # 50ms
```

## Detecting Unawaited Coroutines

```python
import warnings
warnings.filterwarnings("error", category=RuntimeWarning)

# Now this will raise instead of warn:
async def main():
    some_coroutine()  # RuntimeWarning -> Exception!
```

## Task Introspection

```python
import asyncio

async def debug_tasks():
    # Get all tasks
    all_tasks = asyncio.all_tasks()
    print(f"Total tasks: {len(all_tasks)}")

    for task in all_tasks:
        print(f"Task: {task.get_name()}")
        print(f"  Done: {task.done()}")
        print(f"  Cancelled: {task.cancelled()}")

        # Get stack
        if not task.done():
            stack = task.get_stack()
            for frame in stack:
                print(f"  {frame}")

# Get current task
current = asyncio.current_task()
```

## Tracing Coroutines

```python
import sys

def trace_coroutines(frame, event, arg):
    if event == "call" and frame.f_code.co_flags & 0x80:  # CO_COROUTINE
        print(f"Coroutine called: {frame.f_code.co_name}")
    return trace_coroutines

sys.settrace(trace_coroutines)
```

## asyncio Debug Logger

```python
import logging

# Detailed asyncio logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("asyncio")
logger.setLevel(logging.DEBUG)

# Custom handler
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
))
logger.addHandler(handler)
```

## Profiling Async Code

### With cProfile

```python
import asyncio
import cProfile
import pstats

async def main():
    await some_work()

# Profile
profiler = cProfile.Profile()
profiler.enable()
asyncio.run(main())
profiler.disable()

# Print stats
stats = pstats.Stats(profiler)
stats.sort_stats("cumtime")
stats.print_stats(20)
```

### With yappi (async-aware)

```python
import yappi
import asyncio

yappi.set_clock_type("wall")  # or "cpu"
yappi.start()

asyncio.run(main())

yappi.stop()

# Get stats for coroutines
func_stats = yappi.get_func_stats()
func_stats.print_all()

# Async-specific stats
asyncio_stats = yappi.get_func_stats(
    filter_callback=lambda x: asyncio.iscoroutinefunction(x.full_name)
)
```

## Finding Memory Leaks

```python
import asyncio
import gc
import tracemalloc

tracemalloc.start()

async def main():
    # ... your code ...
    pass

asyncio.run(main())

# Get memory snapshot
snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics("lineno")

print("Top 10 memory allocations:")
for stat in top_stats[:10]:
    print(stat)

# Find leaking tasks
gc.collect()
for obj in gc.get_objects():
    if isinstance(obj, asyncio.Task):
        print(f"Leaked task: {obj}")
```

## Common Issues and Solutions

### Issue: "Task was destroyed but it is pending"

```python
# WRONG
async def bad():
    asyncio.create_task(background_work())  # Orphaned!

# CORRECT
background_tasks = set()

async def good():
    task = asyncio.create_task(background_work())
    background_tasks.add(task)
    task.add_done_callback(background_tasks.discard)
```

### Issue: "Event loop is closed"

```python
# WRONG - reusing closed loop
loop = asyncio.get_event_loop()
loop.run_until_complete(coro1())
loop.close()
loop.run_until_complete(coro2())  # Error!

# CORRECT - use asyncio.run()
asyncio.run(coro1())
asyncio.run(coro2())  # New loop each time
```

### Issue: "Cannot schedule new futures after shutdown"

```python
# Happens when creating tasks during shutdown
async def cleanup():
    # DON'T create new tasks here
    await existing_task
```

### Issue: Hung program (blocked event loop)

```python
# Find the blocking call
import asyncio

async def debug_blocking():
    loop = asyncio.get_running_loop()
    loop.slow_callback_duration = 0.001  # 1ms threshold

    # Enable debug mode
    loop.set_debug(True)

    # Your code here
```

## Testing Async Code

```python
import pytest
import asyncio

@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result == expected

# Test timeouts
@pytest.mark.asyncio
async def test_with_timeout():
    with pytest.raises(asyncio.TimeoutError):
        async with asyncio.timeout(0.1):
            await slow_function()

# Mock async functions
from unittest.mock import AsyncMock

async def test_with_mock():
    mock = AsyncMock(return_value="mocked")
    result = await mock()
    assert result == "mocked"
```

## Visualization Tools

### aiomonitor

```python
import aiomonitor

async def main():
    with aiomonitor.start_monitor():
        # Connect via: nc localhost 50101
        # or: python -m aiomonitor.cli
        await long_running_task()
```

### aiodebug

```python
from aiodebug import log_slow_callbacks

log_slow_callbacks.enable(0.05)  # Log callbacks > 50ms
```

## Quick Debug Checklist

1. [ ] Enable debug mode: `asyncio.run(main(), debug=True)`
2. [ ] Check for unawaited coroutines: warnings -> errors
3. [ ] Look for blocking calls: time.sleep, requests, open()
4. [ ] Verify all tasks are awaited or tracked
5. [ ] Check for proper resource cleanup (sessions, connections)
6. [ ] Monitor task count: `len(asyncio.all_tasks())`
7. [ ] Profile with yappi for async-aware profiling
