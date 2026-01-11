# Production Async Patterns

Production-ready patterns for deploying async Python applications.

## Graceful Shutdown

```python
import asyncio
import signal
from contextlib import asynccontextmanager

class GracefulShutdown:
    """Handle graceful shutdown with signal handlers."""

    def __init__(self):
        self._shutdown = asyncio.Event()
        self._tasks: set[asyncio.Task] = set()

    @property
    def should_exit(self) -> bool:
        return self._shutdown.is_set()

    async def wait_for_shutdown(self):
        """Block until shutdown signal received."""
        await self._shutdown.wait()

    def trigger_shutdown(self):
        """Signal shutdown to all waiting coroutines."""
        self._shutdown.set()

    def register_task(self, task: asyncio.Task):
        """Track task for cleanup on shutdown."""
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)

    async def cleanup(self, timeout: float = 30.0):
        """Cancel and await all tracked tasks."""
        for task in self._tasks:
            task.cancel()

        if self._tasks:
            await asyncio.wait(
                self._tasks,
                timeout=timeout,
                return_when=asyncio.ALL_COMPLETED
            )


async def main():
    shutdown = GracefulShutdown()
    loop = asyncio.get_running_loop()

    # Register signal handlers
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, shutdown.trigger_shutdown)

    try:
        # Start background services
        worker = asyncio.create_task(background_worker(shutdown))
        shutdown.register_task(worker)

        # Run until shutdown
        await shutdown.wait_for_shutdown()
    finally:
        # Cleanup
        await shutdown.cleanup(timeout=30.0)

        # Remove signal handlers
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.remove_signal_handler(sig)


async def background_worker(shutdown: GracefulShutdown):
    """Worker that respects shutdown signals."""
    while not shutdown.should_exit:
        try:
            await process_next_item()
        except asyncio.CancelledError:
            # Finish current work before exiting
            await finish_current_work()
            raise
```

## Lifespan Context Manager

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan():
    """Application lifespan manager for startup/shutdown."""
    # Startup
    db_pool = await create_db_pool()
    redis = await create_redis_client()

    try:
        yield {"db": db_pool, "redis": redis}
    finally:
        # Shutdown (always runs)
        await redis.close()
        await db_pool.close()


# Usage with FastAPI
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    app.state.db = await create_db_pool()
    yield
    # Shutdown
    await app.state.db.close()

app = FastAPI(lifespan=lifespan)
```

## Health Check Endpoints

```python
import asyncio
from dataclasses import dataclass
from enum import Enum

class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

@dataclass
class ComponentHealth:
    name: str
    status: HealthStatus
    latency_ms: float | None = None
    error: str | None = None

async def check_database(pool) -> ComponentHealth:
    """Check database connectivity."""
    try:
        start = asyncio.get_event_loop().time()
        async with pool.acquire() as conn:
            await conn.execute("SELECT 1")
        latency = (asyncio.get_event_loop().time() - start) * 1000
        return ComponentHealth("database", HealthStatus.HEALTHY, latency)
    except Exception as e:
        return ComponentHealth("database", HealthStatus.UNHEALTHY, error=str(e))

async def check_redis(client) -> ComponentHealth:
    """Check Redis connectivity."""
    try:
        start = asyncio.get_event_loop().time()
        await client.ping()
        latency = (asyncio.get_event_loop().time() - start) * 1000
        return ComponentHealth("redis", HealthStatus.HEALTHY, latency)
    except Exception as e:
        return ComponentHealth("redis", HealthStatus.UNHEALTHY, error=str(e))

async def health_check(pool, redis) -> dict:
    """Aggregate health check for all components."""
    checks = await asyncio.gather(
        check_database(pool),
        check_redis(redis),
        return_exceptions=True
    )

    components = []
    overall = HealthStatus.HEALTHY

    for check in checks:
        if isinstance(check, Exception):
            components.append(ComponentHealth("unknown", HealthStatus.UNHEALTHY, error=str(check)))
            overall = HealthStatus.UNHEALTHY
        else:
            components.append(check)
            if check.status == HealthStatus.UNHEALTHY:
                overall = HealthStatus.UNHEALTHY
            elif check.status == HealthStatus.DEGRADED and overall == HealthStatus.HEALTHY:
                overall = HealthStatus.DEGRADED

    return {
        "status": overall.value,
        "components": [
            {"name": c.name, "status": c.status.value, "latency_ms": c.latency_ms, "error": c.error}
            for c in components
        ]
    }
```

## Liveness vs Readiness Probes

```python
class HealthProbes:
    """Kubernetes-style health probes."""

    def __init__(self):
        self._ready = asyncio.Event()
        self._alive = True

    def set_ready(self):
        """Mark application as ready to receive traffic."""
        self._ready.set()

    def set_not_ready(self):
        """Mark application as not ready (drain traffic)."""
        self._ready.clear()

    def set_not_alive(self):
        """Mark application as dead (trigger restart)."""
        self._alive = False

    async def liveness(self) -> bool:
        """
        Liveness probe - is the process healthy?
        Failing this triggers a container restart.
        """
        return self._alive

    async def readiness(self) -> bool:
        """
        Readiness probe - can the app handle traffic?
        Failing this removes the pod from service.
        """
        return self._ready.is_set()

    async def startup(self) -> bool:
        """
        Startup probe - has the app finished initializing?
        Prevents liveness checks during slow startup.
        """
        return self._ready.is_set()


# Usage
probes = HealthProbes()

async def startup():
    await initialize_db()
    await warm_caches()
    probes.set_ready()  # Now accept traffic

async def shutdown():
    probes.set_not_ready()  # Stop accepting new requests
    await drain_connections()  # Finish in-flight requests
```

## Resource Cleanup on Cancellation

```python
async def process_with_cleanup():
    """Ensure cleanup even when cancelled."""
    resource = await acquire_resource()
    try:
        await do_work(resource)
    except asyncio.CancelledError:
        # Perform essential cleanup before re-raising
        await resource.flush()
        raise
    finally:
        # Always close resource
        await resource.close()


async def shielded_cleanup():
    """Protect critical cleanup from cancellation."""
    resource = await acquire_resource()
    try:
        await do_work(resource)
    finally:
        # Shield cleanup from cancellation
        await asyncio.shield(resource.close())
```

## Background Task Management

```python
class BackgroundTaskManager:
    """Manage long-running background tasks."""

    def __init__(self):
        self._tasks: dict[str, asyncio.Task] = {}
        self._shutdown = asyncio.Event()

    def start(self, name: str, coro):
        """Start a named background task."""
        if name in self._tasks:
            raise ValueError(f"Task {name} already running")

        task = asyncio.create_task(coro, name=name)
        task.add_done_callback(lambda t: self._task_done(name, t))
        self._tasks[name] = task
        return task

    def _task_done(self, name: str, task: asyncio.Task):
        """Handle task completion."""
        self._tasks.pop(name, None)

        if not task.cancelled():
            exc = task.exception()
            if exc:
                # Log error, potentially restart
                logger.error(f"Task {name} failed: {exc}")

    async def stop(self, name: str, timeout: float = 10.0):
        """Stop a specific task."""
        if task := self._tasks.get(name):
            task.cancel()
            try:
                await asyncio.wait_for(task, timeout=timeout)
            except (asyncio.CancelledError, asyncio.TimeoutError):
                pass

    async def shutdown(self, timeout: float = 30.0):
        """Stop all background tasks."""
        self._shutdown.set()

        for task in self._tasks.values():
            task.cancel()

        if self._tasks:
            await asyncio.wait(
                self._tasks.values(),
                timeout=timeout,
                return_when=asyncio.ALL_COMPLETED
            )
```

## Periodic Tasks

```python
async def periodic_task(
    interval: float,
    coro_func,
    shutdown_event: asyncio.Event | None = None
):
    """Run a coroutine periodically."""
    while True:
        if shutdown_event and shutdown_event.is_set():
            break

        try:
            await coro_func()
        except asyncio.CancelledError:
            raise
        except Exception as e:
            logger.error(f"Periodic task error: {e}")

        # Wait for interval or shutdown
        if shutdown_event:
            try:
                await asyncio.wait_for(
                    shutdown_event.wait(),
                    timeout=interval
                )
                break  # Shutdown signaled
            except asyncio.TimeoutError:
                pass  # Continue loop
        else:
            await asyncio.sleep(interval)
```

## Quick Reference

| Pattern | Use Case |
|---------|----------|
| `GracefulShutdown` | SIGTERM/SIGINT handling |
| `lifespan` context | Startup/shutdown resources |
| `HealthProbes` | Kubernetes health checks |
| `asyncio.shield()` | Protect critical cleanup |
| `BackgroundTaskManager` | Long-running task lifecycle |
| `periodic_task` | Scheduled background work |
