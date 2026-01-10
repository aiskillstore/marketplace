# Pydantic v2 Validation & Serialization

Modern validation patterns for FastAPI with Pydantic v2.

## Basic Models

```python
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Annotated

class UserCreate(BaseModel):
    """Request model with field validation."""
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    age: int = Field(..., ge=0, le=150)
    bio: str | None = Field(default=None, max_length=500)

class UserResponse(BaseModel):
    """Response model with ORM support."""
    id: int
    name: str
    email: EmailStr
    created_at: datetime

    model_config = {"from_attributes": True}
```

## Custom Validators

```python
from pydantic import BaseModel, field_validator, model_validator
from typing import Self

class UserCreate(BaseModel):
    username: str
    password: str
    password_confirm: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate single field."""
        if not v.isalnum():
            raise ValueError("Username must be alphanumeric")
        return v.lower()

    @model_validator(mode="after")
    def validate_passwords(self) -> Self:
        """Validate across multiple fields."""
        if self.password != self.password_confirm:
            raise ValueError("Passwords don't match")
        return self


# Before validation (raw input)
class Config(BaseModel):
    port: int

    @field_validator("port", mode="before")
    @classmethod
    def parse_port(cls, v):
        """Convert string to int before validation."""
        if isinstance(v, str):
            return int(v)
        return v
```

## Computed Fields

```python
from pydantic import BaseModel, computed_field
from datetime import datetime

class User(BaseModel):
    first_name: str
    last_name: str
    birth_date: datetime

    @computed_field
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @computed_field
    @property
    def age(self) -> int:
        today = datetime.now()
        return today.year - self.birth_date.year
```

## Field Serialization

```python
from pydantic import BaseModel, field_serializer
from datetime import datetime
from decimal import Decimal

class Order(BaseModel):
    id: int
    total: Decimal
    created_at: datetime

    @field_serializer("total")
    def serialize_total(self, value: Decimal) -> str:
        """Serialize Decimal as formatted string."""
        return f"${value:.2f}"

    @field_serializer("created_at")
    def serialize_date(self, value: datetime) -> str:
        """Serialize datetime as ISO string."""
        return value.isoformat()


# Or use Annotated with serialization
from pydantic import PlainSerializer

FormattedDecimal = Annotated[
    Decimal,
    PlainSerializer(lambda v: f"${v:.2f}", return_type=str)
]

class Order(BaseModel):
    total: FormattedDecimal
```

## Custom Types

```python
from pydantic import BaseModel, GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema
from typing import Any

class PhoneNumber(str):
    """Custom phone number type with validation."""

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls._validate,
            core_schema.str_schema(),
        )

    @classmethod
    def _validate(cls, v: str) -> "PhoneNumber":
        # Remove non-digits
        digits = "".join(c for c in v if c.isdigit())
        if len(digits) != 10:
            raise ValueError("Phone must be 10 digits")
        return cls(f"({digits[:3]}) {digits[3:6]}-{digits[6:]}")


class Contact(BaseModel):
    name: str
    phone: PhoneNumber

# Usage
contact = Contact(name="John", phone="1234567890")
print(contact.phone)  # (123) 456-7890
```

## Nested Models

```python
from pydantic import BaseModel
from datetime import datetime

class Address(BaseModel):
    street: str
    city: str
    country: str = "USA"

class Company(BaseModel):
    name: str
    address: Address

class UserResponse(BaseModel):
    id: int
    name: str
    company: Company | None = None
    addresses: list[Address] = []

    model_config = {"from_attributes": True}
```

## Discriminated Unions

```python
from pydantic import BaseModel, Field
from typing import Literal, Union
from typing_extensions import Annotated

class Dog(BaseModel):
    pet_type: Literal["dog"]
    name: str
    breed: str

class Cat(BaseModel):
    pet_type: Literal["cat"]
    name: str
    indoor: bool = True

# Use discriminator for efficient parsing
Pet = Annotated[
    Union[Dog, Cat],
    Field(discriminator="pet_type")
]

class Owner(BaseModel):
    name: str
    pets: list[Pet]

# FastAPI automatically validates
@app.post("/owners")
async def create_owner(owner: Owner):
    return owner
```

## Model Inheritance

```python
from pydantic import BaseModel
from datetime import datetime

class BaseResponse(BaseModel):
    """Base for all responses."""
    model_config = {"from_attributes": True}

class TimestampMixin(BaseModel):
    """Mixin for timestamp fields."""
    created_at: datetime
    updated_at: datetime

class UserBase(BaseModel):
    name: str
    email: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase, TimestampMixin, BaseResponse):
    id: int
```

## Partial Updates (PATCH)

```python
from pydantic import BaseModel
from typing import Any

class UserUpdate(BaseModel):
    """All fields optional for partial updates."""
    name: str | None = None
    email: str | None = None
    bio: str | None = None

@app.patch("/users/{user_id}")
async def update_user(user_id: int, updates: UserUpdate):
    # Only get set fields
    update_data = updates.model_dump(exclude_unset=True)

    # Apply to existing user
    user = await get_user(user_id)
    for field, value in update_data.items():
        setattr(user, field, value)

    return user
```

## Validation Error Handling

```python
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    """Custom validation error response."""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"],
        })

    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error",
            "errors": errors,
        },
    )
```

## Quick Reference

| Feature | Pydantic v2 |
|---------|-------------|
| ORM mode | `model_config = {"from_attributes": True}` |
| Field validator | `@field_validator("field")` |
| Model validator | `@model_validator(mode="after")` |
| Serializer | `@field_serializer("field")` |
| Computed | `@computed_field` + `@property` |
| Exclude unset | `model_dump(exclude_unset=True)` |
| Discriminator | `Field(discriminator="type")` |

| Validation | Usage |
|------------|-------|
| Required | `name: str` |
| Optional | `name: str \| None = None` |
| Default | `name: str = "default"` |
| Constraints | `Field(min_length=1, max_length=100)` |
| Custom | `@field_validator` |
