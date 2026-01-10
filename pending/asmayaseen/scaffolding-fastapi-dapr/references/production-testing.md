# Production Testing & Logging Patterns

## Structured Logging

### Setup with structlog

```python
# app/logging.py
import structlog
import logging
from contextvars import ContextVar

request_id_ctx: ContextVar[str] = ContextVar("request_id", default="")

def configure_logging():
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

def get_logger():
    return structlog.get_logger()
```

### Request ID Middleware

```python
# app/middleware.py
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.logging import request_id_ctx, get_logger

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request_id_ctx.set(request_id)

        log = get_logger()
        log.info(
            "request_started",
            method=request.method,
            path=request.url.path,
            request_id=request_id
        )

        response = await call_next(request)

        log.info(
            "request_completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            request_id=request_id
        )

        response.headers["X-Request-ID"] = request_id
        return response
```

### Usage in Routes

```python
from app.logging import get_logger

@router.post("/tasks")
async def create_task(task: TaskCreate, session: AsyncSession = Depends(get_session)):
    log = get_logger()
    log.info("creating_task", title=task.title)

    db_task = Task.model_validate(task)
    session.add(db_task)
    await session.commit()
    await session.refresh(db_task)

    log.info("task_created", task_id=db_task.id)
    return db_task
```

## Testing Patterns

### conftest.py Setup

```python
# tests/conftest.py
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from app.main import app
from app.database import get_session

# Use test database
TEST_DATABASE_URL = "postgresql+asyncpg://test:test@localhost:5432/test_db"

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest.fixture(scope="session")
async def engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
    await engine.dispose()

@pytest.fixture
async def session(engine):
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
        await session.rollback()

@pytest.fixture
async def client(session):
    def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
```

### Test Examples

```python
# tests/test_tasks.py
import pytest
from httpx import AsyncClient

@pytest.mark.anyio
async def test_create_task(client: AsyncClient):
    response = await client.post("/tasks", json={
        "title": "Test Task",
        "status": "pending"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task"
    assert "id" in data

@pytest.mark.anyio
async def test_get_task_not_found(client: AsyncClient):
    response = await client.get("/tasks/99999")
    assert response.status_code == 404

@pytest.mark.anyio
async def test_list_tasks_pagination(client: AsyncClient):
    # Create 15 tasks
    for i in range(15):
        await client.post("/tasks", json={"title": f"Task {i}"})

    # Test pagination
    response = await client.get("/tasks?limit=10&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 10
    assert data["total"] >= 15
```

### Testing with Mocked Dependencies

```python
# tests/test_with_mocks.py
from unittest.mock import AsyncMock, patch
import pytest

@pytest.mark.anyio
async def test_external_api_call(client: AsyncClient):
    mock_response = {"status": "success", "data": {"id": 123}}

    with patch("app.services.external_api.fetch_data", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = mock_response

        response = await client.post("/sync-external")

        assert response.status_code == 200
        mock_fetch.assert_called_once()
```

## Dependency Injection Patterns

### Repository Pattern

```python
# app/repositories/task.py
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models import Task, TaskCreate, TaskUpdate

class TaskRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, task: TaskCreate) -> Task:
        db_task = Task.model_validate(task)
        self.session.add(db_task)
        await self.session.commit()
        await self.session.refresh(db_task)
        return db_task

    async def get(self, task_id: int) -> Task | None:
        return await self.session.get(Task, task_id)

    async def list(self, limit: int = 10, offset: int = 0) -> list[Task]:
        result = await self.session.exec(
            select(Task).offset(offset).limit(limit)
        )
        return result.all()
```

### Service Layer

```python
# app/services/task.py
from app.repositories.task import TaskRepository
from app.models import Task, TaskCreate
from app.logging import get_logger

class TaskService:
    def __init__(self, repo: TaskRepository):
        self.repo = repo
        self.log = get_logger()

    async def create_task(self, task: TaskCreate, user_id: str) -> Task:
        self.log.info("creating_task", user_id=user_id, title=task.title)
        db_task = await self.repo.create(task)
        # Additional business logic here
        return db_task
```

### Dependency Factory

```python
# app/dependencies.py
from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from app.database import get_session
from app.repositories.task import TaskRepository
from app.services.task import TaskService

def get_task_repository(session: AsyncSession = Depends(get_session)) -> TaskRepository:
    return TaskRepository(session)

def get_task_service(repo: TaskRepository = Depends(get_task_repository)) -> TaskService:
    return TaskService(repo)
```

### Usage in Routes

```python
# app/routers/tasks.py
from fastapi import APIRouter, Depends
from app.dependencies import get_task_service
from app.services.task import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/", response_model=TaskRead, status_code=201)
async def create_task(
    task: TaskCreate,
    service: TaskService = Depends(get_task_service),
    user: dict = Depends(get_current_user)
):
    return await service.create_task(task, user["sub"])
```

## API Versioning

### URL Prefix Versioning

```python
# app/main.py
from fastapi import FastAPI
from app.routers.v1 import tasks as tasks_v1
from app.routers.v2 import tasks as tasks_v2

app = FastAPI()

app.include_router(tasks_v1.router, prefix="/v1")
app.include_router(tasks_v2.router, prefix="/v2")
```

### Header-Based Versioning

```python
from fastapi import Header, HTTPException

async def get_api_version(x_api_version: str = Header(default="1")):
    if x_api_version not in ["1", "2"]:
        raise HTTPException(status_code=400, detail="Invalid API version")
    return x_api_version

@router.get("/tasks")
async def list_tasks(version: str = Depends(get_api_version)):
    if version == "2":
        return {"items": tasks, "total": len(tasks), "version": 2}
    return tasks  # v1 format
```

## Error Handling

### Custom Exception Handlers

```python
# app/exceptions.py
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from app.logging import get_logger

class AppException(Exception):
    def __init__(self, status_code: int, detail: str, error_code: str):
        self.status_code = status_code
        self.detail = detail
        self.error_code = error_code

async def app_exception_handler(request: Request, exc: AppException):
    log = get_logger()
    log.error(
        "app_exception",
        error_code=exc.error_code,
        detail=exc.detail,
        path=request.url.path
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.error_code,
            "detail": exc.detail
        }
    )

# In main.py
app.add_exception_handler(AppException, app_exception_handler)
```

## Production Checklist

### Logging
- [ ] Structured JSON logging configured
- [ ] Request ID middleware added
- [ ] Correlation IDs propagated to downstream services
- [ ] Sensitive data not logged (passwords, tokens)

### Testing
- [ ] pytest with anyio for async tests
- [ ] Test database with transaction rollback
- [ ] Dependency override for mocking
- [ ] Integration tests with real DB
- [ ] Coverage > 80%

### Architecture
- [ ] Repository pattern for data access
- [ ] Service layer for business logic
- [ ] Dependency injection with Depends()
- [ ] API versioning strategy defined

### Error Handling
- [ ] Custom exception classes
- [ ] Global exception handlers
- [ ] Consistent error response format
- [ ] Errors logged with context