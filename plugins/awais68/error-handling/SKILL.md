---
name: error-handling
description: |
  Use when implementing structured error handling in backend or frontend code.
  Triggers for: try-catch patterns, custom exception classes, global error handlers,
  error logging, user-friendly error messages, or API error responses.
  NOT for: business logic validation (use domain exceptions) or unrelated error types.
---

# Error Handling Skill

Expert structured error handling for FastAPI backends and React/Next.js frontends with consistent error messages and logging.

## Quick Reference

| Pattern | Backend | Frontend |
|---------|---------|----------|
| Custom exception | `class FeeNotPaidError(AppException)` | N/A |
| Try-catch | `try: ... except SpecificError:` | `try { } catch (e) { }` |
| Global handler | `@app.exception_handler` | `ErrorBoundary` component |
| User message | `detail` field in response | Toast/Snackbar |
| Error logging | `logger.error(...)` | Console/Sentry |

## Custom Exceptions (Backend)

### Base Exception Hierarchy

```python
# backend/app/errors/exceptions.py
from fastapi import HTTPException
from typing import Any


class AppException(HTTPException):
    """Base application exception with user-friendly messages."""

    def __init__(
        self,
        status_code: int,
        detail: str,
        user_message: str,
        headers: dict[str, Any] | None = None,
    ):
        self.user_message = user_message
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class NotFoundError(AppException):
    """Resource not found (404)."""

    def __init__(self, resource: str, identifier: str):
        super().__init__(
            status_code=404,
            detail=f"{resource} with id '{identifier}' not found",
            user_message=f"{resource} not found. Please check and try again.",
        )


class ValidationError(AppException):
    """Validation failed (400)."""

    def __init__(self, field: str, reason: str):
        super().__init__(
            status_code=400,
            detail=f"Validation error for field '{field}': {reason}",
            user_message=f"Invalid value for {field}. {reason}",
        )


class UnauthorizedError(AppException):
    """Authentication required (401)."""

    def __init__(self, reason: str = "Authentication required"):
        super().__init__(
            status_code=401,
            detail=reason,
            user_message="Please log in to continue.",
            headers={"WWW-Authenticate": "Bearer"},
        )


class ForbiddenError(AppException):
    """Permission denied (403)."""

    def __init__(self, action: str):
        super().__init__(
            status_code=403,
            detail=f"Permission denied for action: {action}",
            user_message=f"You don't have permission to {action}.",
        )


class ConflictError(AppException):
    """Resource conflict (409)."""

    def __init__(self, resource: str, reason: str):
        super().__init__(
            status_code=409,
            detail=f"Conflict for {resource}: {reason}",
            user_message=f"{resource} conflict. {reason}",
        )


class RateLimitError(AppException):
    """Too many requests (429)."""

    def __init__(self, retry_after: int = 60):
        super().__init__(
            status_code=429,
            detail=f"Rate limit exceeded. Retry after {retry_after} seconds.",
            user_message="Too many requests. Please wait a moment and try again.",
            headers={"Retry-After": str(retry_after)},
        )
```

### Domain-Specific Exceptions

```python
# backend/app/errors/domains.py
from .exceptions import NotFoundError, ValidationError, ConflictError


class StudentNotFoundError(NotFoundError):
    def __init__(self, student_id: int):
        super().__init__(resource="Student", identifier=str(student_id))


class FeeNotPaidError(ConflictError):
    def __init__(self, student_id: int, amount_due: float):
        super().__init__(
            resource="Fee",
            reason=f"Student {student_id} has unpaid fee of ${amount_due:.2f}",
        )


class AttendanceAlreadyMarkedError(ConflictError):
    def __init__(self, student_id: int, date: str):
        super().__init__(
            resource="Attendance",
            reason=f"Attendance already marked for student {student_id} on {date}",
        )


class InvalidGradeError(ValidationError):
    def __init__(self, grade: str, valid_grades: list[str]):
        super().__init__(
            field="grade",
            reason=f"'{grade}' is not valid. Must be one of: {', '.join(valid_grades)}",
        )


class InsufficientBalanceError(ValidationError):
    def __init__(self, required: float, available: float):
        super().__init__(
            field="amount",
            reason=f"Insufficient balance. Required: ${required:.2f}, Available: ${available:.2f}",
        )
```

## Try-Catch Patterns

### Narrow Try Blocks

```python
# GOOD: Specific exception, narrow scope
try:
    student = await get_student_by_id(student_id)
except StudentNotFoundError:
    raise StudentNotFoundError(student_id)

# BAD: Too broad, catches everything
try:
    student = await get_student_by_id(student_id)
    calculate_fees(student)
    send_notification(student)
    update_records(student)
except Exception:
    pass  # Swallowed!
```

### Cleanup with Finally

```python
import asyncio
from contextlib import asynccontextmanager


@asynccontextmanager
async def database_connection():
    conn = await get_db_connection()
    try:
        yield conn
    except Exception as e:
        await conn.rollback()
        raise
    finally:
        await conn.close()


async def transfer_funds(from_account: int, to_account: int, amount: float):
    async with database_connection() as conn:
        try:
            await conn.execute("UPDATE accounts SET balance = balance - ? WHERE id = ?", amount, from_account)
            await conn.execute("UPDATE accounts SET balance = balance + ? WHERE id = ?", amount, to_account)
            await conn.commit()
        except InsufficientBalanceError:
            await conn.rollback()
            raise
```

## Error Logging (Backend)

### Structured JSON Logging

```python
# backend/app/core/logger.py
import logging
import json
from datetime import datetime
from typing import Any
from contextvars import ContextVar
import traceback

# Correlation ID for request tracing
correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default="")


class StructuredLogger:
    """Structured JSON logger with correlation IDs."""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

    def _log_record(self, level: str, message: str, extra: dict[str, Any] = None):
        record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "message": message,
            "correlation_id": correlation_id_var.get(),
            **(extra or {}),
        }
        return json.dumps(record)

    def info(self, message: str, **extra):
        self.logger.info(self._log_record("INFO", message, extra))

    def warning(self, message: str, **extra):
        self.logger.warning(self._log_record("WARNING", message, extra))

    def error(self, message: str, error: Exception = None, **extra):
        log_extra = {**extra}
        if error:
            log_extra["error_type"] = type(error).__name__
            log_extra["error_message"] = str(error)
            log_extra["stack_trace"] = traceback.format_exc()
        self.logger.error(self._log_record("ERROR", message, log_extra))


logger = StructuredLogger(__name__)
```

### Using the Logger

```python
from app.core.logger import logger, correlation_id_var


async def get_student(student_id: int) -> Student:
    logger.info("Fetching student", student_id=student_id)

    try:
        student = await db.get_student(student_id)
        logger.info("Student fetched successfully", student_id=student_id, has_fees=bool(student.fees))
        return student
    except StudentNotFoundError:
        logger.warning("Student not found", student_id=student_id)
        raise
    except Exception as e:
        logger.error("Unexpected error fetching student", error=e, student_id=student_id)
        raise  # Re-raise for handler
```

## Global Error Handler (Backend)

```python
# backend/app/middleware/error_handler.py
from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
from app.errors.exceptions import AppException
from app.core.logger import logger


def setup_error_handlers(app: FastAPI):
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        logger.error(
            "App exception occurred",
            error=exc,
            status_code=exc.status_code,
            path=request.url.path,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.__class__.__name__,
                    "message": exc.user_message,
                    "internal": exc.detail,  # Only in debug mode
                }
            },
            headers=exc.headers,
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(
            "Unhandled exception",
            error=exc,
            path=request.url.path,
            method=request.method,
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Something went wrong. Please try again later.",
                }
            },
        )
```

## Frontend Error Handling

### Error Types

```typescript
// frontend/lib/errors.ts
export interface ApiError {
  error: {
    code: string;
    message: string;
    internal?: string;
  };
}

export class ApiResponseError extends Error {
  code: string;
  userMessage: string;
  internalMessage?: string;
  statusCode: number;

  constructor(error: ApiError["error"], statusCode: number) {
    super(error.message);
    this.name = "ApiResponseError";
    this.code = error.code;
    this.userMessage = error.message;
    this.internalMessage = error.internal;
    this.statusCode = statusCode;
  }
}
```

### Error Mapper

```typescript
// frontend/lib/errorMapper.ts
import { ApiResponseError } from "./errors";

export function getUserMessage(error: unknown): string {
  if (error instanceof ApiResponseError) {
    return error.userMessage;
  }

  if (error instanceof Error) {
    // Network errors
    if (error.name === "TypeError" && error.message.includes("fetch")) {
      return "Unable to connect to server. Please check your internet connection.";
    }

    // Unexpected errors
    return "An unexpected error occurred. Please try again.";
  }

  return "An unknown error occurred.";
}

export function getErrorTitle(error: unknown): string {
  if (error instanceof ApiResponseError) {
    switch (error.statusCode) {
      case 401:
        return "Authentication Required";
      case 403:
        return "Access Denied";
      case 404:
        return "Not Found";
      case 409:
        return "Conflict";
      case 422:
        return "Validation Error";
      case 429:
        return "Rate Limited";
      case 500:
        return "Server Error";
      default:
        return "Error";
    }
  }

  return "Error";
}
```

### API Client with Error Handling

```typescript
// frontend/lib/api.ts
import { ApiResponseError } from "./errors";
import { getUserMessage } from "./errorMapper";

interface RequestOptions extends RequestInit {
  params?: Record<string, string>;
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = "/api/v1") {
    this.baseUrl = baseUrl;
  }

  async request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
    const url = new URL(`${this.baseUrl}${endpoint}`, window.location.origin);

    if (options.params) {
      Object.entries(options.params).forEach(([key, value]) => {
        url.searchParams.append(key, value);
      });
    }

    const response = await fetch(url.toString(), {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));

      throw new ApiResponseError(
        {
          code: errorData.error?.code || "HTTP_ERROR",
          message: errorData.error?.message || response.statusText,
          internal: errorData.error?.internal,
        },
        response.status
      );
    }

    if (response.status === 204) {
      return undefined as T;
    }

    return response.json() as Promise<T>;
  }

  get<T>(endpoint: string, params?: Record<string, string>): Promise<T> {
    return this.request<T>(endpoint, { method: "GET", params });
  }

  post<T>(endpoint: string, body: unknown): Promise<T> {
    return this.request<T>(endpoint, { method: "POST", body: JSON.stringify(body) });
  }

  put<T>(endpoint: string, body: unknown): Promise<T> {
    return this.request<T>(endpoint, { method: "PUT", body: JSON.stringify(body) });
  }

  delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: "DELETE" });
  }
}

export const api = new ApiClient();
```

### React Query with Error Handling

```typescript
// frontend/hooks/useApi.ts
import { useQuery, useMutation, UseQueryOptions } from "@tanstack/react-query";
import { api } from "../lib/api";
import { ApiResponseError } from "../lib/errors";
import { toast } from "sonner";

export function useFetch<T>(
  key: string[],
  endpoint: string,
  options?: Partial<UseQueryOptions<T>>
) {
  return useQuery({
    queryKey: key,
    queryFn: () => api.get<T>(endpoint),
    ...options,
    onError: (error: unknown) => {
      if (error instanceof ApiResponseError) {
        toast.error(error.userMessage);
      } else {
        toast.error("Failed to fetch data");
      }
    },
  });
}

export function useMutationWithError<T, V>(
  mutationFn: (variables: V) => Promise<T>,
  successMessage: string,
  onSuccess?: (data: T) => void
) {
  return useMutation({
    mutationFn,
    onSuccess: (data) => {
      toast.success(successMessage);
      onSuccess?.(data);
    },
    onError: (error: unknown) => {
      if (error instanceof ApiResponseError) {
        toast.error(error.userMessage);
      } else {
        toast.error("An error occurred. Please try again.");
      }
    },
  });
}
```

## Quality Checklist

- [ ] **No swallowed errors**: Every exception is either logged or surfaced to user
- [ ] **Internal vs user message separation**: Technical details in `detail`, user-friendly in `user_message`
- [ ] **4xx vs 5xx correctly mapped**: Client errors (4xx) vs server errors (5xx)
- [ ] **No PII in logs**: Never log passwords, tokens, personal data
- [ ] **Correlation IDs**: Track errors across services with request IDs
- [ ] **Consistent error format**: Same structure for all API errors

## Error Response Format

```json
{
  "error": {
    "code": "STUDENT_NOT_FOUND",
    "message": "Student not found. Please check and try again.",
    "internal": "Student with id '12345' not found"
  }
}
```

## Integration Points

| Skill | Integration |
|-------|-------------|
| `@fastapi-app` | Global exception handlers in main.py |
| `@api-route-design` | Proper status codes in responses |
| `@jwt-auth` | UnauthorizedError for auth failures |
| `@db-migration` | Handle migration errors gracefully |
| `@env-config` | Configuration validation errors |
