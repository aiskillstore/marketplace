# FastAPI Beginner Guide

This guide covers fundamental FastAPI concepts for building basic REST APIs.

## Table of Contents

- [Project Setup](#project-setup)
- [First Application](#first-application)
- [Path Operations](#path-operations)
- [Request Parameters](#request-parameters)
- [Request Body](#request-body)
- [Response Models](#response-models)
- [Error Handling](#error-handling)

## Project Setup

### Installation

```bash
pip install "fastapi[standard]"
# or separate installations:
pip install fastapi uvicorn[standard]
```

### Minimal Project Structure

```
my-api/
├── main.py
└── requirements.txt
```

## First Application

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

**Run the application:**
```bash
uvicorn main:app --reload
```

**Access:**
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

## Path Operations

### HTTP Methods

```python
from fastapi import FastAPI

app = FastAPI()

# GET - Retrieve data
@app.get("/items")
async def list_items():
    return {"items": []}

# POST - Create data
@app.post("/items")
async def create_item():
    return {"created": True}

# PUT - Update (replace) data
@app.put("/items/{item_id}")
async def update_item(item_id: int):
    return {"updated": item_id}

# PATCH - Partial update
@app.patch("/items/{item_id}")
async def patch_item(item_id: int):
    return {"patched": item_id}

# DELETE - Remove data
@app.delete("/items/{item_id}")
async def delete_item(item_id: int):
    return {"deleted": item_id}
```

### Path Parameters

```python
@app.get("/users/{user_id}")
async def read_user(user_id: int):
    return {"user_id": user_id}

@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(user_id: int, item_id: str):
    return {"user_id": user_id, "item_id": item_id}
```

**Type validation:** FastAPI automatically validates and converts path parameters to the declared type.

### Path Order Matters

```python
# Correct order: specific before generic
@app.get("/users/me")
async def read_current_user():
    return {"user": "current"}

@app.get("/users/{user_id}")
async def read_user(user_id: int):
    return {"user_id": user_id}

# Wrong order would match "/users/me" as user_id="me"
```

## Request Parameters

### Query Parameters

```python
from typing import Optional

@app.get("/items")
async def list_items(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}

@app.get("/search")
async def search(q: Optional[str] = None, min_price: float = 0.0):
    return {"query": q, "min_price": min_price}
```

**Usage:**
- `/items` → skip=0, limit=10 (defaults)
- `/items?skip=20&limit=5` → skip=20, limit=5
- `/search?q=laptop` → q="laptop", min_price=0.0

### Required vs Optional

```python
# Required (no default value)
@app.get("/items/{item_id}")
async def get_item(item_id: int, full_details: bool):
    return {"item_id": item_id, "full_details": full_details}

# Optional (with default or Optional type)
@app.get("/users")
async def list_users(active: bool = True, role: Optional[str] = None):
    return {"active": active, "role": role}
```

### Multiple Path and Query Parameters

```python
@app.get("/users/{user_id}/orders")
async def user_orders(
    user_id: int,
    status: str = "pending",
    limit: int = 10,
    sort: str = "date"
):
    return {
        "user_id": user_id,
        "status": status,
        "limit": limit,
        "sort": sort
    }
```

## Request Body

### Pydantic Models

```python
from pydantic import BaseModel, Field
from typing import Optional

class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None

@app.post("/items")
async def create_item(item: Item):
    item_dict = item.dict()
    if item.tax:
        price_with_tax = item.price + item.tax
        item_dict["price_with_tax"] = price_with_tax
    return item_dict
```

**Request body example:**
```json
{
  "name": "Laptop",
  "description": "Gaming laptop",
  "price": 999.99,
  "tax": 99.99
}
```

### Field Validation

```python
from pydantic import BaseModel, Field, EmailStr

class User(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    age: int = Field(..., ge=0, le=120)
    bio: Optional[str] = Field(None, max_length=500)

@app.post("/users")
async def create_user(user: User):
    return user
```

### Nested Models

```python
class Image(BaseModel):
    url: str
    name: str

class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    images: list[Image] = []

@app.post("/items")
async def create_item(item: Item):
    return item
```

### Combining Parameters

```python
from fastapi import Path, Query, Body

@app.put("/items/{item_id}")
async def update_item(
    item_id: int = Path(..., ge=1),
    item: Item = Body(...),
    user_id: int = Query(...),
    importance: int = Body(...)
):
    return {
        "item_id": item_id,
        "item": item,
        "user_id": user_id,
        "importance": importance
    }
```

## Response Models

### Basic Response Model

```python
class ItemResponse(BaseModel):
    id: int
    name: str
    price: float

@app.post("/items", response_model=ItemResponse)
async def create_item(item: Item):
    # Simulate saving and returning with ID
    return {"id": 1, "name": item.name, "price": item.price}
```

### Response Model Config

```python
class UserIn(BaseModel):
    username: str
    password: str
    email: str

class UserOut(BaseModel):
    username: str
    email: str

@app.post("/users", response_model=UserOut)
async def create_user(user: UserIn):
    # Password not included in response
    return user
```

### List Responses

```python
@app.get("/items", response_model=list[ItemResponse])
async def list_items():
    return [
        {"id": 1, "name": "Item 1", "price": 10.0},
        {"id": 2, "name": "Item 2", "price": 20.0}
    ]
```

### Status Codes

```python
from fastapi import status

@app.post("/items", status_code=status.HTTP_201_CREATED)
async def create_item(item: Item):
    return item

@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int):
    return None
```

## Error Handling

### HTTPException

```python
from fastapi import HTTPException

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    if item_id not in fake_db:
        raise HTTPException(
            status_code=404,
            detail=f"Item {item_id} not found"
        )
    return fake_db[item_id]
```

### Custom Exception Handlers

```python
from fastapi import Request
from fastapi.responses import JSONResponse

class ItemNotFoundException(Exception):
    def __init__(self, item_id: int):
        self.item_id = item_id

@app.exception_handler(ItemNotFoundException)
async def item_not_found_handler(request: Request, exc: ItemNotFoundException):
    return JSONResponse(
        status_code=404,
        content={"message": f"Item {exc.item_id} not found"}
    )

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    if item_id not in fake_db:
        raise ItemNotFoundException(item_id=item_id)
    return fake_db[item_id]
```

### Validation Error Responses

FastAPI automatically returns validation errors with 422 status code:

```json
{
  "detail": [
    {
      "loc": ["body", "price"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## Common Patterns

### CRUD Operations

```python
from typing import Dict

fake_db: Dict[int, Item] = {}
next_id = 1

@app.post("/items", status_code=201)
async def create_item(item: Item):
    global next_id
    item_id = next_id
    fake_db[item_id] = item
    next_id += 1
    return {"id": item_id, **item.dict()}

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    if item_id not in fake_db:
        raise HTTPException(status_code=404, detail="Item not found")
    return fake_db[item_id]

@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    if item_id not in fake_db:
        raise HTTPException(status_code=404, detail="Item not found")
    fake_db[item_id] = item
    return item

@app.delete("/items/{item_id}", status_code=204)
async def delete_item(item_id: int):
    if item_id not in fake_db:
        raise HTTPException(status_code=404, detail="Item not found")
    del fake_db[item_id]
```

### Pagination

```python
@app.get("/items")
async def list_items(skip: int = 0, limit: int = 10):
    items = list(fake_db.values())[skip:skip + limit]
    return {
        "items": items,
        "skip": skip,
        "limit": limit,
        "total": len(fake_db)
    }
```

## Next Steps

Once comfortable with these basics, proceed to:
- **references/02-intermediate.md** for authentication, databases, and middleware
- **references/03-advanced.md** for async operations and advanced patterns
