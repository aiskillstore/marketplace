---
name: api-route-design
description: |
  Use when designing RESTful API endpoints in FastAPI or Python projects.
  Triggers for: creating GET/POST/PUT/DELETE endpoints, request validation with Pydantic,
  response formatting with JSON schemas, status code selection, pagination, filtering,
  or sorting parameters.
  NOT for: GraphQL APIs, WebSocket handlers, or non-RESTful endpoints.
---

# API Route Design Skill

Expert design and implementation of RESTful APIs with proper validation, response formatting, and HTTP semantics.

## Quick Reference

| Pattern | Example | Purpose |
|---------|---------|---------|
| List resource | `@router.get("/fees/", response_model=List[FeeOut])` | Retrieve collection |
| Get by ID | `@router.get("/fees/{fee_id}")` | Retrieve single resource |
| Create | `@router.post("/fees/", response_model=FeeOut, status_code=201)` | Create new resource |
| Update | `@router.put("/fees/{fee_id}")` | Full resource update |
| Patch | `@router.patch("/fees/{fee_id}")` | Partial resource update |
| Delete | `@router.delete("/fees/{fee_id}", status_code=204)` | Remove resource |

## URL Naming Conventions

```
/v1/{resource}           # Collection endpoints
/v1/{resource}/{id}      # Single resource endpoints
/v1/{resource}/{id}/sub  # Nested resource endpoints
```

**Rules:**
- Use lowercase, hyphens for multi-word: `/student-fees` not `/studentFees`
- Use plural nouns for collections: `/users` not `/user`
- Use HTTP methods semantically: GET (read), POST (create), PUT/PATCH (update), DELETE (remove)

## HTTP Status Codes

| Code | Usage | Example |
|------|-------|---------|
| 200 | OK | Successful GET, PUT, PATCH |
| 201 | Created | Successful POST (resource created) |
| 202 | Accepted | Async operation started |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Invalid input, validation failed |
| 401 | Unauthorized | Missing or invalid auth |
| 403 | Forbidden | Authenticated but not authorized |
| 404 | Not Found | Resource doesn't exist |
| 422 | Unprocessable Entity | Validation errors (Pydantic) |
| 500 | Internal Server Error | Unexpected server error |

## Request Validation Patterns

### Path Parameters

```python
from fastapi import APIRouter, HTTPException
from typing import Annotated

router = APIRouter()

@router.get("/fees/{fee_id}")
async def get_fee(fee_id: int):
    fee = await get_fee_by_id(fee_id)
    if not fee:
        raise HTTPException(status_code=404, detail="Fee not found")
    return fee
```

### Query Parameters (Pagination, Filtering, Sorting)

```python
@router.get("/fees/", response_model=List[FeeOut])
async def list_fees(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: str | None = Query(None, pattern="^(pending|paid|overdue)$"),
    sort_by: str = Query("created_at", enum=["created_at", "amount", "due_date"]),
    sort_order: str = Query("desc", enum=["asc", "desc"]),
):
    return await paginate_fees(
        skip=skip,
        limit=limit,
        status=status,
        sort_by=sort_by,
        sort_order=sort_order,
    )
```

### Request Body (Pydantic Models)

```python
from pydantic import BaseModel
from datetime import datetime

class FeeCreate(BaseModel):
    student_id: int
    amount: float = Field(..., gt=0)
    due_date: datetime
    description: str | None = None

class FeeUpdate(BaseModel):
    amount: float | None = Field(None, gt=0)
    status: str | None = Field(None, pattern="^(pending|paid|overdue)$")
    due_date: datetime | None = None

@router.post("/fees/", response_model=FeeOut, status_code=201)
async def create_fee(fee_in: FeeCreate):
    return await create_fee_db(fee_in)

@router.patch("/fees/{fee_id}", response_model=FeeOut)
async def update_fee(fee_id: int, fee_in: FeeUpdate):
    return await update_fee_db(fee_id, fee_in)
```

## Response Models

### Standard Response Envelope

```python
class FeeOut(BaseModel):
    id: int
    student_id: int
    amount: float
    status: str
    created_at: datetime
    due_date: datetime

class PaginatedResponse(BaseModel):
    data: List[FeeOut]
    total: int
    skip: int
    limit: int
    has_more: bool
```

### Error Response

```python
class ErrorResponse(BaseModel):
    error: str
    detail: str | None = None
    code: str | None = None
```

## Complete Endpoint Example

```python
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Annotated

router = APIRouter(prefix="/v1/fees", tags=["fees"])

@router.get(
    "/",
    response_model=PaginatedResponse[FeeOut],
    summary="List fees",
    description="Retrieve a paginated list of fees with optional filtering.",
)
async def list_fees(
    skip: Annotated[int, Query(0, ge=0)] = 0,
    limit: Annotated[int, Query(100, ge=1, le=1000)] = 100,
    status: Annotated[str | None, Query(pattern="^(pending|paid|overdue)$")] = None,
    _current_user: User = Depends(get_current_user),
) -> PaginatedResponse[FeeOut]:
    fees, total = await get_fees(
        skip=skip, limit=limit, status=status, user=_current_user
    )
    return PaginatedResponse(
        data=fees,
        total=total,
        skip=skip,
        limit=limit,
        has_more=(skip + limit) < total,
    )

@router.get(
    "/{fee_id}",
    response_model=FeeOut,
    responses={404: {"model": ErrorResponse}},
)
async def get_fee(
    fee_id: int,
    _current_user: User = Depends(get_current_user),
) -> FeeOut:
    fee = await get_fee_by_id(fee_id)
    if not fee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fee not found",
        )
    return fee

@router.post(
    "/",
    response_model=FeeOut,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse}},
)
async def create_fee(
    fee_in: FeeCreate,
    _current_user: User = Depends(get_current_user),
) -> FeeOut:
    return await create_fee_db(fee_in, created_by=_current_user.id)
```

## Integration with Other Skills

| Skill | Integration Point |
|-------|-------------------|
| `@fastapi-app` | Router registration in `main.py` |
| `@sqlmodel-crud` | Database operations in endpoints |
| `@jwt-auth` | `Depends(get_current_user)` for protected routes |
| `@api-client` | Consumer of this API design |

## Quality Checklist

- [ ] **Pagination standard**: Use `skip`/`limit` with `has_more` indicator
- [ ] **Filtering**: Query params for common filter fields
- [ ] **Sorting**: `sort_by` and `sort_order` parameters
- [ ] **Status codes**: 201 for POST, 204 for DELETE, 404 for not found
- [ ] **Response models**: All endpoints use `response_model`
- [ ] **Documentation**: `summary` and `description` for OpenAPI
- [ ] **Error handling**: Consistent error response format

## Pagination Standard

```python
@router.get("/items/", response_model=PaginatedResponse[ItemOut])
async def list_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> PaginatedResponse[ItemOut]:
    items, total = await get_items(skip=skip, limit=limit)
    return PaginatedResponse(
        data=items,
        total=total,
        skip=skip,
        limit=limit,
        has_more=(skip + limit) < total,
    )
```

## Filtering & Sorting Standard

```python
@router.get("/items/")
async def list_items(
    # Filtering
    category: str | None = None,
    status: str | None = Query(None, pattern="^(active|inactive)$"),
    min_amount: float | None = Query(None, ge=0),
    # Sorting
    sort_by: str = Query("created_at", enum=["created_at", "amount", "name"]),
    sort_order: str = Query("desc", enum=["asc", "desc"]),
):
    return await get_items(
        filters={"category": category, "status": status, "min_amount": min_amount},
        order_by=f"{sort_order} {sort_by.lstrip('-')}",
    )
```
