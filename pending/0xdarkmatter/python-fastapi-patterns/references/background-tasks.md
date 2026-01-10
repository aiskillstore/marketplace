# FastAPI Background Tasks

Async background processing patterns.

## Built-in BackgroundTasks

```python
from fastapi import BackgroundTasks, FastAPI

app = FastAPI()

async def send_email(email: str, message: str):
    """Background task - runs after response sent."""
    # Simulate email sending
    await asyncio.sleep(2)
    print(f"Email sent to {email}: {message}")

@app.post("/signup")
async def signup(
    email: str,
    background_tasks: BackgroundTasks,
):
    # Create user synchronously
    user = create_user(email)

    # Queue background task
    background_tasks.add_task(send_email, email, "Welcome!")

    # Response sent immediately
    return {"message": "User created"}


# Multiple tasks
@app.post("/order")
async def create_order(
    order: OrderCreate,
    background_tasks: BackgroundTasks,
):
    db_order = save_order(order)

    # Queue multiple tasks
    background_tasks.add_task(send_confirmation, order.email)
    background_tasks.add_task(update_inventory, order.items)
    background_tasks.add_task(notify_warehouse, db_order.id)

    return {"order_id": db_order.id}
```

## Dependency Injection with Background Tasks

```python
from fastapi import Depends, BackgroundTasks
from typing import Annotated

async def audit_log(action: str, user_id: int):
    """Log user actions."""
    await db.execute(
        "INSERT INTO audit_log (action, user_id) VALUES ($1, $2)",
        action, user_id
    )

def get_auditor(background_tasks: BackgroundTasks):
    """Factory for audit logging."""
    def log(action: str, user_id: int):
        background_tasks.add_task(audit_log, action, user_id)
    return log

Auditor = Annotated[Callable, Depends(get_auditor)]

@app.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: CurrentUser,
    auditor: Auditor,
):
    await db.delete_user(user_id)
    auditor("user_deleted", current_user.id)
    return {"deleted": user_id}
```

## Longer Tasks with Celery

```python
# tasks.py
from celery import Celery

celery_app = Celery(
    "tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
)

@celery_app.task
def process_video(video_id: int):
    """Long-running task - handled by Celery worker."""
    video = get_video(video_id)
    processed = transcode(video)
    save_processed(processed)
    return {"status": "completed", "video_id": video_id}


# api.py
from fastapi import FastAPI
from tasks import process_video

app = FastAPI()

@app.post("/videos/{video_id}/process")
async def start_processing(video_id: int):
    # Queue task in Celery
    task = process_video.delay(video_id)

    return {
        "task_id": task.id,
        "status": "queued",
    }

@app.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    task = process_video.AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": task.status,
        "result": task.result if task.ready() else None,
    }
```

## Periodic Tasks with APScheduler

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI
from contextlib import asynccontextmanager

scheduler = AsyncIOScheduler()

async def cleanup_expired_sessions():
    """Run daily at midnight."""
    await db.execute("DELETE FROM sessions WHERE expires < NOW()")

async def send_daily_report():
    """Run daily at 9 AM."""
    report = await generate_report()
    await send_email("admin@example.com", report)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup - configure scheduler
    scheduler.add_job(
        cleanup_expired_sessions,
        CronTrigger(hour=0, minute=0),
        id="cleanup_sessions",
    )
    scheduler.add_job(
        send_daily_report,
        CronTrigger(hour=9, minute=0),
        id="daily_report",
    )
    scheduler.start()

    yield

    # Shutdown
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)


# Manual trigger endpoint (for testing)
@app.post("/admin/trigger/{job_id}")
async def trigger_job(job_id: str, admin: AdminUser):
    job = scheduler.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    job.modify(next_run_time=datetime.now())
    return {"message": f"Job {job_id} triggered"}
```

## Task Queues with Redis

```python
import redis.asyncio as redis
import json
from uuid import uuid4

class TaskQueue:
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)
        self.queue_name = "task_queue"

    async def enqueue(self, task_type: str, payload: dict) -> str:
        """Add task to queue."""
        task_id = str(uuid4())
        task = {
            "id": task_id,
            "type": task_type,
            "payload": payload,
            "status": "pending",
        }
        await self.redis.rpush(self.queue_name, json.dumps(task))
        await self.redis.set(f"task:{task_id}", json.dumps(task))
        return task_id

    async def get_status(self, task_id: str) -> dict | None:
        """Get task status."""
        data = await self.redis.get(f"task:{task_id}")
        return json.loads(data) if data else None


# Worker (separate process)
async def worker(queue: TaskQueue):
    """Process tasks from queue."""
    while True:
        task_data = await queue.redis.blpop(queue.queue_name, timeout=1)
        if not task_data:
            continue

        task = json.loads(task_data[1])
        task["status"] = "processing"
        await queue.redis.set(f"task:{task['id']}", json.dumps(task))

        try:
            result = await process_task(task)
            task["status"] = "completed"
            task["result"] = result
        except Exception as e:
            task["status"] = "failed"
            task["error"] = str(e)

        await queue.redis.set(f"task:{task['id']}", json.dumps(task))


# API endpoints
queue = TaskQueue("redis://localhost:6379")

@app.post("/tasks")
async def create_task(task_type: str, payload: dict):
    task_id = await queue.enqueue(task_type, payload)
    return {"task_id": task_id}

@app.get("/tasks/{task_id}")
async def get_task(task_id: str):
    task = await queue.get_status(task_id)
    if not task:
        raise HTTPException(status_code=404)
    return task
```

## Async Task Manager

```python
import asyncio
from contextlib import asynccontextmanager
from typing import Callable, Awaitable

class TaskManager:
    """Manage long-running async tasks."""

    def __init__(self):
        self._tasks: dict[str, asyncio.Task] = {}
        self._results: dict[str, Any] = {}

    async def start(self, task_id: str, coro: Awaitable):
        """Start a named task."""
        if task_id in self._tasks:
            raise ValueError(f"Task {task_id} already running")

        async def wrapper():
            try:
                result = await coro
                self._results[task_id] = {"status": "completed", "result": result}
            except Exception as e:
                self._results[task_id] = {"status": "failed", "error": str(e)}
            finally:
                self._tasks.pop(task_id, None)

        self._tasks[task_id] = asyncio.create_task(wrapper())
        return task_id

    def get_status(self, task_id: str) -> dict:
        if task_id in self._tasks:
            return {"status": "running"}
        return self._results.get(task_id, {"status": "not_found"})

    async def cancel(self, task_id: str) -> bool:
        task = self._tasks.get(task_id)
        if task:
            task.cancel()
            return True
        return False


# Global task manager
task_manager = TaskManager()

@app.post("/process")
async def start_processing(data: ProcessRequest):
    task_id = str(uuid4())
    await task_manager.start(task_id, heavy_processing(data))
    return {"task_id": task_id}

@app.get("/process/{task_id}")
async def get_processing_status(task_id: str):
    return task_manager.get_status(task_id)
```

## Quick Reference

| Method | Use Case | Runs Where |
|--------|----------|------------|
| `BackgroundTasks` | Quick async tasks | Same process |
| Celery | Heavy processing | Worker process |
| APScheduler | Periodic jobs | Same process |
| Redis queue | Distributed tasks | Worker process |
| `asyncio.Task` | In-memory async | Same process |

| Pattern | Best For |
|---------|----------|
| BackgroundTasks | Email, webhooks, logging |
| Celery | Video processing, ML, reports |
| APScheduler | Cleanup, reports, sync |
| Redis queue | Scalable task distribution |
