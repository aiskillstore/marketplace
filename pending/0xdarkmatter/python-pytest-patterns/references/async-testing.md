# Async Testing Patterns

Testing asyncio code with pytest-asyncio.

## Setup

```bash
pip install pytest-asyncio
```

```ini
# pytest.ini or pyproject.toml
[pytest]
asyncio_mode = auto  # Recommended for pytest-asyncio 0.21+
```

## Basic Async Tests

```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    result = await async_fetch_data()
    assert result["status"] == "ok"

@pytest.mark.asyncio
async def test_async_context_manager():
    async with AsyncResource() as resource:
        result = await resource.get()
        assert result is not None
```

## Async Fixtures

```python
import pytest
import aiohttp

@pytest.fixture
async def async_client():
    """Async fixture with cleanup."""
    async with aiohttp.ClientSession() as session:
        yield session
    # Session closed automatically

@pytest.fixture
async def database():
    """Async database fixture."""
    conn = await create_async_connection()
    await conn.execute("BEGIN")
    yield conn
    await conn.execute("ROLLBACK")
    await conn.close()

@pytest.mark.asyncio
async def test_with_async_fixture(async_client):
    async with async_client.get("https://httpbin.org/json") as resp:
        data = await resp.json()
        assert "slideshow" in data
```

## Fixture Scopes

```python
@pytest.fixture(scope="session")
async def app():
    """Session-scoped async fixture."""
    app = await create_app()
    yield app
    await app.shutdown()

@pytest.fixture(scope="module")
async def db_pool():
    """Module-scoped connection pool."""
    pool = await asyncpg.create_pool(DATABASE_URL)
    yield pool
    await pool.close()
```

## Testing Timeouts

```python
import asyncio

@pytest.mark.asyncio
async def test_timeout():
    with pytest.raises(asyncio.TimeoutError):
        async with asyncio.timeout(0.1):
            await asyncio.sleep(1.0)

@pytest.mark.asyncio
async def test_wait_for():
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(slow_operation(), timeout=0.1)
```

## Testing Cancellation

```python
@pytest.mark.asyncio
async def test_task_cancellation():
    task = asyncio.create_task(long_running_task())
    await asyncio.sleep(0.01)
    task.cancel()

    with pytest.raises(asyncio.CancelledError):
        await task

@pytest.mark.asyncio
async def test_graceful_cancellation():
    """Test that cleanup runs on cancellation."""
    cleanup_ran = False

    async def task_with_cleanup():
        nonlocal cleanup_ran
        try:
            await asyncio.sleep(10)
        except asyncio.CancelledError:
            cleanup_ran = True
            raise

    task = asyncio.create_task(task_with_cleanup())
    await asyncio.sleep(0.01)
    task.cancel()

    with pytest.raises(asyncio.CancelledError):
        await task

    assert cleanup_ran
```

## Testing gather

```python
@pytest.mark.asyncio
async def test_gather_success():
    results = await asyncio.gather(
        async_op_1(),
        async_op_2(),
        async_op_3(),
    )
    assert len(results) == 3

@pytest.mark.asyncio
async def test_gather_with_exceptions():
    results = await asyncio.gather(
        async_op_1(),
        async_op_that_fails(),
        async_op_3(),
        return_exceptions=True
    )
    assert isinstance(results[1], Exception)
```

## Testing TaskGroup (Python 3.11+)

```python
@pytest.mark.asyncio
async def test_task_group():
    results = []

    async with asyncio.TaskGroup() as tg:
        tg.create_task(append_result(results, 1))
        tg.create_task(append_result(results, 2))
        tg.create_task(append_result(results, 3))

    assert sorted(results) == [1, 2, 3]

@pytest.mark.asyncio
async def test_task_group_exception():
    with pytest.raises(ExceptionGroup):
        async with asyncio.TaskGroup() as tg:
            tg.create_task(successful_task())
            tg.create_task(failing_task())
```

## Mocking Async Functions

```python
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_mock_async_function(mocker):
    mock = mocker.patch("mymodule.async_api_call", new_callable=AsyncMock)
    mock.return_value = {"data": "mocked"}

    result = await mymodule.fetch_data()

    assert result == {"data": "mocked"}
    mock.assert_awaited_once()

@pytest.mark.asyncio
async def test_async_side_effect(mocker):
    mock = AsyncMock()
    mock.side_effect = [
        {"page": 1},
        {"page": 2},
        ValueError("No more pages"),
    ]

    assert await mock() == {"page": 1}
    assert await mock() == {"page": 2}
    with pytest.raises(ValueError):
        await mock()
```

## Testing aiohttp

```python
import aiohttp
from aiohttp import web
import pytest

@pytest.fixture
async def app():
    """Create aiohttp app."""
    app = web.Application()
    app.router.add_get("/", home_handler)
    return app

@pytest.fixture
async def client(aiohttp_client, app):
    """Create test client."""
    return await aiohttp_client(app)

@pytest.mark.asyncio
async def test_endpoint(client):
    resp = await client.get("/")
    assert resp.status == 200
    data = await resp.json()
    assert "message" in data
```

## Testing WebSockets

```python
@pytest.mark.asyncio
async def test_websocket(aiohttp_client, app):
    client = await aiohttp_client(app)

    async with client.ws_connect("/ws") as ws:
        await ws.send_str("Hello")
        msg = await ws.receive()
        assert msg.type == aiohttp.WSMsgType.TEXT
        assert msg.data == "Hello back"
```

## Event Loop Fixtures

```python
import pytest

@pytest.fixture(scope="session")
def event_loop_policy():
    """Custom event loop policy."""
    return asyncio.DefaultEventLoopPolicy()

# For uvloop
@pytest.fixture(scope="session")
def event_loop_policy():
    import uvloop
    return uvloop.EventLoopPolicy()
```

## Testing Queues

```python
@pytest.mark.asyncio
async def test_queue_producer_consumer():
    queue = asyncio.Queue()
    results = []

    async def producer():
        for i in range(3):
            await queue.put(i)
        await queue.put(None)  # Sentinel

    async def consumer():
        while True:
            item = await queue.get()
            if item is None:
                break
            results.append(item)

    await asyncio.gather(producer(), consumer())
    assert results == [0, 1, 2]
```

## Best Practices

1. **Use `asyncio_mode = auto`** - Simplifies test marking
2. **Scope fixtures appropriately** - Session for expensive resources
3. **Use AsyncMock** - For mocking coroutines
4. **Test cancellation** - Ensure cleanup happens
5. **Test timeouts** - Verify timeout behavior
6. **Avoid blocking calls** - Use `run_in_executor` if needed
7. **Close resources** - Use async context managers
