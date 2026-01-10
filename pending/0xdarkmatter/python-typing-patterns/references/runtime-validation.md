# Runtime Type Validation

Enforce type hints at runtime with Pydantic, typeguard, and beartype.

## Pydantic v2 Validation

```python
from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic import EmailStr, HttpUrl, PositiveInt
from datetime import datetime
from typing import Self

class User(BaseModel):
    """Model with automatic validation."""
    id: PositiveInt
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    website: HttpUrl | None = None
    created_at: datetime = Field(default_factory=datetime.now)

    @field_validator("name")
    @classmethod
    def name_must_be_title_case(cls, v: str) -> str:
        return v.title()

    @model_validator(mode="after")
    def check_consistency(self) -> Self:
        # Cross-field validation
        return self


# Usage - raises ValidationError on invalid data
user = User(id=1, name="john doe", email="john@example.com")
print(user.name)  # "John Doe" (transformed)

# From dict
user = User.model_validate({"id": 1, "name": "jane", "email": "jane@example.com"})

# Validation error
try:
    User(id=-1, name="", email="invalid")
except ValidationError as e:
    print(e.errors())
```

## Pydantic for Function Arguments

```python
from pydantic import validate_call, Field
from typing import Annotated

@validate_call
def greet(
    name: Annotated[str, Field(min_length=1)],
    count: Annotated[int, Field(ge=1, le=10)] = 1,
) -> str:
    return f"Hello, {name}!" * count


# Valid
greet("World")  # OK
greet("World", count=3)  # OK

# Invalid - raises ValidationError
greet("")  # Error: min_length
greet("World", count=100)  # Error: le
```

## typeguard (Runtime Type Checking)

```python
from typeguard import typechecked, check_type
from typing import TypeVar, Generic

# Decorator for function checking
@typechecked
def process(items: list[int], multiplier: float) -> list[float]:
    return [item * multiplier for item in items]

# Valid
process([1, 2, 3], 1.5)  # OK

# Invalid - raises TypeCheckError at runtime
process(["a", "b"], 1.5)  # Error: list[int] expected


# Check types manually
from typeguard import check_type

value = [1, 2, 3]
check_type(value, list[int])  # OK

value = [1, "two", 3]
check_type(value, list[int])  # TypeCheckError


# Class checking
@typechecked
class DataProcessor(Generic[T]):
    def __init__(self, data: list[T]):
        self.data = data

    def process(self) -> T:
        return self.data[0]
```

## beartype (Fast Runtime Checking)

```python
from beartype import beartype
from beartype.typing import List, Optional

# ~200x faster than typeguard
@beartype
def fast_process(items: List[int], factor: float) -> List[float]:
    return [i * factor for i in items]


# With optional
@beartype
def find_user(user_id: int) -> Optional[dict]:
    return None


# Class decorator
@beartype
class FastProcessor:
    def __init__(self, data: list[int]):
        self.data = data

    def sum(self) -> int:
        return sum(self.data)
```

## TypedDict Runtime Validation

```python
from typing import TypedDict, Required, NotRequired
from pydantic import TypeAdapter

class UserDict(TypedDict):
    id: Required[int]
    name: Required[str]
    email: NotRequired[str]


# Using Pydantic to validate TypedDict
adapter = TypeAdapter(UserDict)

# Valid
user = adapter.validate_python({"id": 1, "name": "John"})

# Invalid - raises ValidationError
adapter.validate_python({"id": "not-int", "name": "John"})


# JSON parsing with validation
user = adapter.validate_json('{"id": 1, "name": "John"}')
```

## dataclass Validation with Pydantic

```python
from dataclasses import dataclass
from pydantic import TypeAdapter
from typing import Annotated
from annotated_types import Gt, Lt

@dataclass
class Point:
    x: Annotated[float, Gt(-100), Lt(100)]
    y: Annotated[float, Gt(-100), Lt(100)]


# Create validator
validator = TypeAdapter(Point)

# Validate
point = validator.validate_python({"x": 10.5, "y": 20.3})

# Or with init
point = validator.validate_python(Point(x=10.5, y=20.3))
```

## Custom Validators

```python
from pydantic import BaseModel, field_validator, ValidationInfo
from pydantic_core import PydanticCustomError
import re

class Account(BaseModel):
    username: str
    password: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not re.match(r"^[a-z][a-z0-9_]{2,19}$", v):
            raise PydanticCustomError(
                "invalid_username",
                "Username must be 3-20 chars, start with letter, contain only a-z, 0-9, _"
            )
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str, info: ValidationInfo) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if info.data.get("username") and info.data["username"] in v:
            raise ValueError("Password cannot contain username")
        return v
```

## Constrained Types

```python
from pydantic import (
    BaseModel,
    PositiveInt,
    NegativeFloat,
    conint,
    constr,
    conlist,
)

class Order(BaseModel):
    quantity: PositiveInt  # > 0
    discount: NegativeFloat | None = None  # < 0

    # Custom constraints
    product_code: constr(pattern=r"^[A-Z]{3}-\d{4}$")
    priority: conint(ge=1, le=5)
    tags: conlist(str, min_length=1, max_length=10)


# Usage
order = Order(
    quantity=5,
    product_code="ABC-1234",
    priority=3,
    tags=["urgent"]
)
```

## When to Use Each

| Tool | Speed | Strictness | Use Case |
|------|-------|------------|----------|
| Pydantic | Medium | High | API validation, config |
| typeguard | Slow | Very high | Testing, debugging |
| beartype | Fast | Medium | Production code |

```python
# Development: Use typeguard for strictest checking
from typeguard import typechecked

@typechecked
def dev_function(x: list[int]) -> int:
    return sum(x)


# Production: Use beartype for minimal overhead
from beartype import beartype

@beartype
def prod_function(x: list[int]) -> int:
    return sum(x)


# API boundaries: Use Pydantic for validation + serialization
from pydantic import BaseModel

class Request(BaseModel):
    items: list[int]

def api_function(request: Request) -> int:
    return sum(request.items)
```

## Quick Reference

| Library | Decorator | Check |
|---------|-----------|-------|
| Pydantic | `@validate_call` | `Model.model_validate()` |
| typeguard | `@typechecked` | `check_type(val, Type)` |
| beartype | `@beartype` | Automatic on call |

| Pydantic Type | Constraint |
|---------------|------------|
| `PositiveInt` | `> 0` |
| `NegativeInt` | `< 0` |
| `conint(ge=0, le=100)` | `0 <= x <= 100` |
| `constr(min_length=1)` | Non-empty string |
| `EmailStr` | Valid email |
| `HttpUrl` | Valid URL |
