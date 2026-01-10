# FastAPI Advanced Guide

This guide covers WebSockets, testing, deployment, performance optimization, and production best practices.

## Table of Contents

- [WebSockets](#websockets)
- [Testing](#testing)
- [Performance Optimization](#performance-optimization)
- [API Versioning](#api-versioning)
- [Advanced Error Handling](#advanced-error-handling)
- [Logging](#logging)
- [Containerization](#containerization)
- [Deployment](#deployment)

## WebSockets

### Basic WebSocket

```python
from fastapi import WebSocket, WebSocketDisconnect

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message received: {data}")
    except WebSocketDisconnect:
        print("Client disconnected")
```

### WebSocket Connection Manager

```python
from typing import List
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")
```

### WebSocket with Authentication

```python
from fastapi import WebSocket, Query, status
from jose import JWTError, jwt

async def get_current_user_ws(websocket: WebSocket, token: str = Query(...)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return None
        return username
    except JWTError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return None

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    username = await get_current_user_ws(websocket, token)
    if username is None:
        return

    await manager.connect(websocket)
    await manager.broadcast(f"{username} joined the chat")

    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"{username}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"{username} left the chat")
```

## Testing

### Setup Test Environment

**Install dependencies:**
```bash
pip install pytest httpx
```

**Project structure:**
```
app/
├── main.py
├── routers/
│   └── items.py
└── tests/
    ├── __init__.py
    ├── test_main.py
    └── test_items.py
```

### Basic Tests

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

def test_create_item():
    response = client.post(
        "/items/",
        json={"name": "Test Item", "price": 10.5, "description": "Test"}
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Test Item"

def test_read_item():
    response = client.get("/items/1")
    assert response.status_code == 200
    assert "name" in response.json()

def test_item_not_found():
    response = client.get("/items/9999")
    assert response.status_code == 404
```

### Testing with Database

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_create_user():
    response = client.post(
        "/users/",
        json={"email": "test@example.com", "password": "testpass"}
    )
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"
```

### Testing Authentication

```python
def test_login():
    response = client.post(
        "/token",
        data={"username": "testuser", "password": "testpass"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    return response.json()["access_token"]

def test_protected_route():
    token = test_login()
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"

def test_unauthorized_access():
    response = client.get("/users/me")
    assert response.status_code == 401
```

### Async Tests

```python
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_read_items():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/items/")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_create_item():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/items/",
            json={"name": "Test", "price": 10.0}
        )
    assert response.status_code == 201
```

### Fixtures and Parametrized Tests

```python
import pytest

@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.fixture
def test_user():
    return {"username": "testuser", "email": "test@example.com"}

def test_with_fixture(test_client, test_user):
    response = test_client.post("/users/", json=test_user)
    assert response.status_code == 201

@pytest.mark.parametrize("item_id,expected_status", [
    (1, 200),
    (999, 404),
    (-1, 422),
])
def test_read_item_parametrized(test_client, item_id, expected_status):
    response = test_client.get(f"/items/{item_id}")
    assert response.status_code == expected_status
```

## Performance Optimization

### Database Query Optimization

**Use select loading to avoid N+1 queries:**
```python
from sqlalchemy.orm import selectinload

@app.get("/users-with-items/")
def get_users_with_items(db: Session = Depends(get_db)):
    users = db.query(DBUser).options(selectinload(DBUser.items)).all()
    return users
```

**Pagination for large datasets:**
```python
@app.get("/items/")
def read_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    items = db.query(DBItem).offset(skip).limit(limit).all()
    total = db.query(DBItem).count()
    return {"items": items, "total": total, "skip": skip, "limit": limit}
```

### Caching

```python
from functools import lru_cache
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from redis import asyncio as aioredis

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

@app.get("/items/{item_id}")
@cache(expire=60)  # Cache for 60 seconds
async def read_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(DBItem).filter(DBItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
```

**In-memory caching:**
```python
@lru_cache(maxsize=128)
def expensive_computation(param: str):
    # Expensive operation
    return result

@app.get("/compute/{param}")
def compute(param: str):
    result = expensive_computation(param)
    return {"result": result}
```

### Response Compression

```python
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)
```

### Database Connection Pooling

```python
from sqlalchemy import create_engine

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=20,  # Maximum number of connections
    max_overflow=10,  # Additional connections if pool is exhausted
    pool_pre_ping=True,  # Test connections before using
    pool_recycle=3600  # Recycle connections after 1 hour
)
```

## API Versioning

### URL Path Versioning

```python
from fastapi import APIRouter

v1_router = APIRouter(prefix="/v1")
v2_router = APIRouter(prefix="/v2")

@v1_router.get("/items/")
def read_items_v1():
    return {"version": "1.0", "items": []}

@v2_router.get("/items/")
def read_items_v2():
    return {"version": "2.0", "items": [], "metadata": {}}

app.include_router(v1_router)
app.include_router(v2_router)
```

### Header-Based Versioning

```python
from fastapi import Header, HTTPException

@app.get("/items/")
def read_items(api_version: str = Header(default="1.0", alias="API-Version")):
    if api_version == "1.0":
        return {"version": "1.0", "items": []}
    elif api_version == "2.0":
        return {"version": "2.0", "items": [], "metadata": {}}
    else:
        raise HTTPException(status_code=400, detail="Unsupported API version")
```

### Content Negotiation Versioning

```python
from fastapi import Request

@app.get("/items/")
def read_items(request: Request):
    accept = request.headers.get("accept", "")
    if "application/vnd.api.v1+json" in accept:
        return {"version": "1.0", "items": []}
    elif "application/vnd.api.v2+json" in accept:
        return {"version": "2.0", "items": [], "metadata": {}}
    else:
        return {"version": "1.0", "items": []}  # Default
```

## Advanced Error Handling

### Custom Exception Classes

```python
class APIException(Exception):
    def __init__(self, status_code: int, detail: str, headers: dict = None):
        self.status_code = status_code
        self.detail = detail
        self.headers = headers

class DatabaseException(APIException):
    def __init__(self, detail: str):
        super().__init__(status_code=500, detail=f"Database error: {detail}")

class ValidationException(APIException):
    def __init__(self, detail: str):
        super().__init__(status_code=422, detail=f"Validation error: {detail}")

@app.exception_handler(APIException)
async def api_exception_handler(request: Request, exc: APIException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=exc.headers
    )
```

### Global Exception Handler

```python
from fastapi.responses import JSONResponse
from fastapi import Request
import traceback

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Log the error
    logger.error(f"Unhandled exception: {exc}\n{traceback.format_exc()}")

    # Return a generic error response
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "type": type(exc).__name__
        }
    )
```

### Validation Error Customization

```python
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })

    return JSONResponse(
        status_code=422,
        content={"detail": "Validation error", "errors": errors}
    )
```

## Logging

### Structured Logging

```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data)

logger = logging.getLogger("app")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    logger.info(
        "Request processed",
        extra={
            "method": request.method,
            "url": str(request.url),
            "status_code": response.status_code,
            "duration": duration
        }
    )
    return response
```

### Request ID Tracking

```python
import uuid
from contextvars import ContextVar

request_id_var: ContextVar[str] = ContextVar("request_id", default="")

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request_id_var.set(request_id)

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response

class RequestIDFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id_var.get()
        return True

logger.addFilter(RequestIDFilter())
```

## Containerization

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY ./app /app/app

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Multi-stage Build

```dockerfile
# Build stage
FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application
COPY ./app /app/app

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/appdb
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    volumes:
      - ./app:/app/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=appdb
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

## Deployment

### Production Configuration

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Application
    app_name: str = "FastAPI App"
    debug: bool = False

    # Security
    secret_key: str
    allowed_hosts: list = ["*"]

    # Database
    database_url: str

    # Redis
    redis_url: str

    # CORS
    cors_origins: list = []

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"

settings = Settings()

# Use settings in app
app = FastAPI(
    title=settings.app_name,
    debug=settings.debug
)
```

### Gunicorn with Uvicorn Workers

**Install:**
```bash
pip install gunicorn
```

**Run:**
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

**gunicorn.conf.py:**
```python
import multiprocessing

bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
keepalive = 120
timeout = 120
accesslog = "-"
errorlog = "-"
loglevel = "info"
```

### Health Checks

```python
from sqlalchemy import text

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    try:
        # Check database connection
        db.execute(text("SELECT 1"))

        # Check Redis connection
        # await redis.ping()

        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")

@app.get("/health/ready")
async def readiness_check():
    # Check if app is ready to serve requests
    return {"status": "ready"}

@app.get("/health/live")
async def liveness_check():
    # Simple check that app is running
    return {"status": "alive"}
```

### Kubernetes Deployment

**deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: fastapi-app
  template:
    metadata:
      labels:
        app: fastapi-app
    spec:
      containers:
      - name: fastapi-app
        image: your-registry/fastapi-app:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: database-url
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: fastapi-service
spec:
  selector:
    app: fastapi-app
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

## Production Best Practices

1. **Use environment variables** for configuration
2. **Enable HTTPS** in production
3. **Set up proper CORS** policies
4. **Implement rate limiting** to prevent abuse
5. **Use connection pooling** for databases
6. **Enable response compression** for large responses
7. **Implement proper logging** with structured logs
8. **Set up monitoring** and alerting (Prometheus, Grafana)
9. **Use secrets management** (Vault, AWS Secrets Manager)
10. **Implement graceful shutdown** for zero-downtime deployments

### Graceful Shutdown

```python
import signal
import sys

def shutdown_handler(signum, frame):
    logger.info("Received shutdown signal, cleaning up...")
    # Close database connections
    # Close Redis connections
    # Wait for pending tasks
    sys.exit(0)

signal.signal(signal.SIGTERM, shutdown_handler)
signal.signal(signal.SIGINT, shutdown_handler)
```
