# FastAPI Middleware Patterns

Request/response processing, CORS, security, and error handling.

## Basic Middleware

```python
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
import time

app = FastAPI()

# Function-based middleware
@app.middleware("http")
async def add_timing_header(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start
    response.headers["X-Process-Time"] = f"{duration:.4f}"
    return response


# Class-based middleware
class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        duration = time.perf_counter() - start
        response.headers["X-Process-Time"] = f"{duration:.4f}"
        return response

app.add_middleware(TimingMiddleware)
```

## CORS Configuration

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://myapp.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Or specific: ["GET", "POST"]
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
    max_age=600,  # Cache preflight for 10 minutes
)

# Development: allow all origins
if settings.debug:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
```

## Security Headers

```python
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # CSP - customize for your app
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'"
        )

        # HSTS (only in production with HTTPS)
        if not request.url.scheme == "http":
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )

        return response

app.add_middleware(SecurityHeadersMiddleware)
```

## Request ID Tracking

```python
from uuid import uuid4
from contextvars import ContextVar

request_id_ctx: ContextVar[str] = ContextVar("request_id", default="")

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Use existing or generate new
        request_id = request.headers.get("X-Request-ID") or str(uuid4())

        # Store in context for logging
        request_id_ctx.set(request_id)
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        return response

app.add_middleware(RequestIDMiddleware)


# Access in endpoints
@app.get("/trace")
async def trace(request: Request):
    return {"request_id": request.state.request_id}
```

## Logging Middleware

```python
import logging
import time
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()

        # Log request
        logger.info(
            "Request started",
            extra={
                "method": request.method,
                "path": request.url.path,
                "client": request.client.host if request.client else None,
            }
        )

        response = await call_next(request)

        # Log response
        duration = time.perf_counter() - start
        logger.info(
            "Request completed",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "duration": f"{duration:.3f}s",
            }
        )

        return response

app.add_middleware(LoggingMiddleware)
```

## Error Handling Middleware

```python
from fastapi import Request
from fastapi.responses import JSONResponse
import traceback

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as exc:
            # Log the full traceback
            logger.exception(
                "Unhandled exception",
                extra={
                    "path": request.url.path,
                    "method": request.method,
                    "traceback": traceback.format_exc(),
                }
            )

            # Return generic error (hide details in production)
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Internal server error",
                    "request_id": getattr(request.state, "request_id", None),
                },
            )

app.add_middleware(ErrorHandlingMiddleware)
```

## Rate Limiting

```python
from collections import defaultdict
from datetime import datetime, timedelta
import asyncio

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests: int = 100, window: int = 60):
        super().__init__(app)
        self.requests = requests
        self.window = window
        self.clients: dict[str, list[datetime]] = defaultdict(list)
        self.lock = asyncio.Lock()

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        now = datetime.now()
        window_start = now - timedelta(seconds=self.window)

        async with self.lock:
            # Remove old requests
            self.clients[client_ip] = [
                t for t in self.clients[client_ip]
                if t > window_start
            ]

            if len(self.clients[client_ip]) >= self.requests:
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Rate limit exceeded"},
                    headers={
                        "Retry-After": str(self.window),
                        "X-RateLimit-Limit": str(self.requests),
                        "X-RateLimit-Remaining": "0",
                    },
                )

            self.clients[client_ip].append(now)
            remaining = self.requests - len(self.clients[client_ip])

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response

app.add_middleware(RateLimitMiddleware, requests=100, window=60)
```

## GZip Compression

```python
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(
    GZipMiddleware,
    minimum_size=1000,  # Only compress responses > 1KB
)
```

## Trusted Host Validation

```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["example.com", "*.example.com"],
)
```

## Middleware Order

```python
# Middleware executes in REVERSE order of addition
# Last added = First to process request, Last to process response

app = FastAPI()

# 1. Error handling (outermost - catches all errors)
app.add_middleware(ErrorHandlingMiddleware)

# 2. Logging (log after error handling)
app.add_middleware(LoggingMiddleware)

# 3. Request ID (needed for logging)
app.add_middleware(RequestIDMiddleware)

# 4. Security (before business logic)
app.add_middleware(SecurityHeadersMiddleware)

# 5. CORS (needs to be early for preflight)
app.add_middleware(CORSMiddleware, ...)

# 6. GZip (compress final response)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Request flow: GZip → CORS → Security → RequestID → Logging → Error → App
# Response flow: App → Error → Logging → RequestID → Security → CORS → GZip
```

## Quick Reference

| Middleware | Purpose |
|------------|---------|
| `CORSMiddleware` | Cross-origin requests |
| `GZipMiddleware` | Response compression |
| `TrustedHostMiddleware` | Host validation |
| `BaseHTTPMiddleware` | Custom middleware base |
| `@app.middleware("http")` | Simple function middleware |

| Order Position | Middleware Type |
|----------------|-----------------|
| First (outer) | Error handling |
| Early | Logging, tracing |
| Middle | Auth, rate limiting |
| Late | CORS, compression |
