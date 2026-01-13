# Async Concurrency Patterns

Advanced concurrency patterns for Python asyncio.

## Producer-Consumer with Queue

```python
import asyncio

async def producer(queue: asyncio.Queue, items):
    """Produce items to queue."""
    for item in items:
        await queue.put(item)
    await queue.put(None)  # Sentinel to signal completion

async def consumer(queue: asyncio.Queue, name: str):
    """Consume items from queue."""
    while True:
        item = await queue.get()
        if item is None:
            queue.task_done()
            break
        await process(item)
        queue.task_done()

async def main():
    queue = asyncio.Queue(maxsize=100)  # Backpressure

    # Run producer and multiple consumers
    await asyncio.gather(
        producer(queue, items),
        consumer(queue, "worker-1"),
        consumer(queue, "worker-2"),
        consumer(queue, "worker-3"),
    )
```

## Sharing State with Lock

```python
import asyncio

# WRONG - race condition even in async!
counter = 0
async def increment():
    global counter
    temp = counter
    await asyncio.sleep(0)  # Context switch point!
    counter = temp + 1

# CORRECT - use Lock
lock = asyncio.Lock()

async def safe_increment():
    global counter
    async with lock:
        counter += 1
```

## Event Signaling

```python
import asyncio

async def waiter(event: asyncio.Event):
    print("Waiting for event...")
    await event.wait()
    print("Event received!")

async def setter(event: asyncio.Event):
    await asyncio.sleep(2)
    event.set()
    print("Event set!")

async def main():
    event = asyncio.Event()
    await asyncio.gather(
        waiter(event),
        setter(event),
    )
```

## Condition Variable

```python
import asyncio

async def consumer(condition: asyncio.Condition, data: list):
    async with condition:
        await condition.wait_for(lambda: len(data) > 0)
        item = data.pop(0)
        return item

async def producer(condition: asyncio.Condition, data: list):
    async with condition:
        data.append("new item")
        condition.notify()
```

## Barrier (Python 3.11+)

```python
import asyncio

async def worker(barrier: asyncio.Barrier, name: str):
    print(f"{name}: Starting work")
    await asyncio.sleep(1)
    print(f"{name}: Waiting at barrier")
    await barrier.wait()
    print(f"{name}: Continuing after barrier")

async def main():
    barrier = asyncio.Barrier(3)
    await asyncio.gather(
        worker(barrier, "A"),
        worker(barrier, "B"),
        worker(barrier, "C"),
    )
```

## Cancellation Handling

```python
async def cancellable_task():
    try:
        while True:
            await do_work()
    except asyncio.CancelledError:
        # Cleanup on cancellation
        await cleanup()
        raise  # Re-raise to propagate

# Cancel a task
task = asyncio.create_task(cancellable_task())
task.cancel()
try:
    await task
except asyncio.CancelledError:
    print("Task was cancelled")
```

## Task Completion Callbacks

```python
def on_complete(task: asyncio.Task):
    if task.exception():
        print(f"Task failed: {task.exception()}")
    else:
        print(f"Task result: {task.result()}")

task = asyncio.create_task(some_work())
task.add_done_callback(on_complete)
```

## Running Tasks in Background

```python
# Keep track of background tasks
background_tasks = set()

async def start_background_task(coro):
    task = asyncio.create_task(coro)
    background_tasks.add(task)
    task.add_done_callback(background_tasks.discard)
    return task

async def cleanup():
    for task in background_tasks:
        task.cancel()
    await asyncio.gather(*background_tasks, return_exceptions=True)
```

## Async Iterator/Generator

```python
async def async_range(n: int):
    """Async generator."""
    for i in range(n):
        await asyncio.sleep(0.1)
        yield i

# Usage
async for value in async_range(10):
    print(value)

# Async comprehension
results = [x async for x in async_range(10)]
```

## Streaming with AsyncIterator

```python
class AsyncIterator:
    def __init__(self, items):
        self.items = items
        self.index = 0

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.index >= len(self.items):
            raise StopAsyncIteration
        item = self.items[self.index]
        self.index += 1
        await asyncio.sleep(0)  # Yield control
        return item
```

## Shield from Cancellation

```python
async def critical_operation():
    # This operation must complete even if outer task is cancelled
    try:
        result = await asyncio.shield(important_work())
    except asyncio.CancelledError:
        # Shield was cancelled, but important_work continues
        result = await important_work()  # Wait for it
    return result
```

## Wait with First Completed

```python
async def first_response(urls: list[str]):
    """Return first successful response."""
    tasks = [asyncio.create_task(fetch(url)) for url in urls]

    done, pending = await asyncio.wait(
        tasks,
        return_when=asyncio.FIRST_COMPLETED
    )

    # Cancel remaining tasks
    for task in pending:
        task.cancel()

    return done.pop().result()
```

## Debounce Pattern

```python
class Debouncer:
    def __init__(self, delay: float):
        self.delay = delay
        self.task: asyncio.Task | None = None

    async def debounce(self, coro):
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass

        async def delayed():
            await asyncio.sleep(self.delay)
            await coro

        self.task = asyncio.create_task(delayed())
```

## Retry Pattern

```python
async def retry(coro_func, max_retries: int = 3, delay: float = 1.0):
    """Retry coroutine with exponential backoff."""
    for attempt in range(max_retries):
        try:
            return await coro_func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(delay * (2 ** attempt))
```
