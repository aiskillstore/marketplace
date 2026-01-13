# Function Overloads

Type-safe function signatures with @overload.

## Basic Overloads

```python
from typing import overload, Literal

# Overload signatures (no implementation)
@overload
def process(data: str) -> str: ...

@overload
def process(data: bytes) -> bytes: ...

@overload
def process(data: int) -> int: ...

# Actual implementation
def process(data: str | bytes | int) -> str | bytes | int:
    if isinstance(data, str):
        return data.upper()
    elif isinstance(data, bytes):
        return data.upper()
    else:
        return data * 2


# Type checker knows the return type
result = process("hello")  # str
result = process(b"hello")  # bytes
result = process(42)  # int
```

## Overloads with Literal

```python
from typing import overload, Literal

@overload
def fetch(url: str, format: Literal["json"]) -> dict: ...

@overload
def fetch(url: str, format: Literal["text"]) -> str: ...

@overload
def fetch(url: str, format: Literal["bytes"]) -> bytes: ...

def fetch(url: str, format: str) -> dict | str | bytes:
    response = requests.get(url)
    if format == "json":
        return response.json()
    elif format == "text":
        return response.text
    else:
        return response.content


# Usage - return type is known
data = fetch("https://api.example.com", "json")  # dict
text = fetch("https://api.example.com", "text")  # str
```

## Overloads with Optional Parameters

```python
from typing import overload

@overload
def get_user(user_id: int) -> User: ...

@overload
def get_user(user_id: int, include_posts: Literal[True]) -> UserWithPosts: ...

@overload
def get_user(user_id: int, include_posts: Literal[False]) -> User: ...

def get_user(user_id: int, include_posts: bool = False) -> User | UserWithPosts:
    user = db.get_user(user_id)
    if include_posts:
        user.posts = db.get_posts(user_id)
        return UserWithPosts(**user.__dict__)
    return user


# Type-safe usage
user = get_user(1)  # User
user_with_posts = get_user(1, include_posts=True)  # UserWithPosts
```

## Overloads with None Returns

```python
from typing import overload

@overload
def find(items: list[T], predicate: Callable[[T], bool]) -> T | None: ...

@overload
def find(items: list[T], predicate: Callable[[T], bool], default: T) -> T: ...

def find(
    items: list[T],
    predicate: Callable[[T], bool],
    default: T | None = None
) -> T | None:
    for item in items:
        if predicate(item):
            return item
    return default


# Without default - might be None
result = find([1, 2, 3], lambda x: x > 5)  # int | None

# With default - never None
result = find([1, 2, 3], lambda x: x > 5, default=0)  # int
```

## Class Method Overloads

```python
from typing import overload, Self
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float

    @overload
    @classmethod
    def from_tuple(cls, coords: tuple[float, float]) -> Self: ...

    @overload
    @classmethod
    def from_tuple(cls, coords: tuple[float, float, float]) -> "Point3D": ...

    @classmethod
    def from_tuple(cls, coords: tuple[float, ...]) -> "Point | Point3D":
        if len(coords) == 2:
            return cls(coords[0], coords[1])
        elif len(coords) == 3:
            return Point3D(coords[0], coords[1], coords[2])
        raise ValueError("Expected 2 or 3 coordinates")
```

## Overloads with Generics

```python
from typing import overload, TypeVar, Sequence

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")

@overload
def first(items: Sequence[T]) -> T | None: ...

@overload
def first(items: Sequence[T], default: T) -> T: ...

def first(items: Sequence[T], default: T | None = None) -> T | None:
    return items[0] if items else default


@overload
def get(d: dict[K, V], key: K) -> V | None: ...

@overload
def get(d: dict[K, V], key: K, default: V) -> V: ...

def get(d: dict[K, V], key: K, default: V | None = None) -> V | None:
    return d.get(key, default)
```

## Async Overloads

```python
from typing import overload

@overload
async def fetch_data(url: str, as_json: Literal[True]) -> dict: ...

@overload
async def fetch_data(url: str, as_json: Literal[False] = False) -> str: ...

async def fetch_data(url: str, as_json: bool = False) -> dict | str:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if as_json:
                return await response.json()
            return await response.text()
```

## Property Overloads (Getter/Setter)

```python
from typing import overload

class Temperature:
    def __init__(self, celsius: float):
        self._celsius = celsius

    @property
    def value(self) -> float:
        return self._celsius

    @overload
    def convert(self, unit: Literal["C"]) -> float: ...

    @overload
    def convert(self, unit: Literal["F"]) -> float: ...

    @overload
    def convert(self, unit: Literal["K"]) -> float: ...

    def convert(self, unit: str) -> float:
        if unit == "C":
            return self._celsius
        elif unit == "F":
            return self._celsius * 9/5 + 32
        elif unit == "K":
            return self._celsius + 273.15
        raise ValueError(f"Unknown unit: {unit}")
```

## Common Patterns

```python
from typing import overload, Literal, TypeVar

T = TypeVar("T")

# Pattern 1: Return type based on flag
@overload
def parse(data: str, strict: Literal[True]) -> Result: ...
@overload
def parse(data: str, strict: Literal[False] = False) -> Result | None: ...

# Pattern 2: Different return for different input types
@overload
def normalize(value: str) -> str: ...
@overload
def normalize(value: list[str]) -> list[str]: ...
@overload
def normalize(value: dict[str, str]) -> dict[str, str]: ...

# Pattern 3: Optional vs required parameter
@overload
def create(name: str) -> Item: ...
@overload
def create(name: str, *, template: str) -> Item: ...
```

## Quick Reference

| Pattern | Use Case |
|---------|----------|
| `@overload` | Define signature (no body) |
| `Literal["value"]` | Specific string/int values |
| `T \| None` vs `T` | Optional default changes return |
| Implementation | Must handle all overload cases |

| Rule | Description |
|------|-------------|
| No body in overloads | Use `...` (ellipsis) |
| Implementation last | After all overloads |
| Cover all cases | Implementation must accept all overload inputs |
| Static only | Overloads are for type checkers, not runtime |
