---
name: python-typing-patterns
description: "Python type hints and type safety patterns. Triggers on: type hints, typing, TypeVar, Generic, Protocol, mypy, pyright, type annotation, overload, TypedDict."
compatibility: "Python 3.10+ (uses union syntax X | Y). Some patterns require 3.11+ (Self, TypeVarTuple)."
allowed-tools: "Read Write"
depends-on: []
related-skills: [python-pytest-patterns]
---

# Python Typing Patterns

Modern type hints for safe, documented Python code.

## Basic Annotations

```python
# Variables
name: str = "Alice"
count: int = 42
items: list[str] = ["a", "b"]
mapping: dict[str, int] = {"key": 1}

# Function signatures
def greet(name: str, times: int = 1) -> str:
    return f"Hello, {name}!" * times

# None handling
def find(id: int) -> str | None:
    return db.get(id)  # May return None
```

## Collections

```python
from collections.abc import Sequence, Mapping, Iterable

# Use collection ABCs for flexibility
def process(items: Sequence[str]) -> list[str]:
    """Accepts list, tuple, or any sequence."""
    return [item.upper() for item in items]

def lookup(data: Mapping[str, int], key: str) -> int:
    """Accepts dict or any mapping."""
    return data.get(key, 0)

# Nested types
Matrix = list[list[float]]
Config = dict[str, str | int | bool]
```

## Optional and Union

```python
# Modern syntax (3.10+)
def find(id: int) -> User | None:
    pass

def parse(value: str | int | float) -> str:
    pass

# With default None
def fetch(url: str, timeout: float | None = None) -> bytes:
    pass
```

## TypedDict

```python
from typing import TypedDict, Required, NotRequired

class UserDict(TypedDict):
    id: int
    name: str
    email: str | None

class ConfigDict(TypedDict, total=False):  # All optional
    debug: bool
    log_level: str

class APIResponse(TypedDict):
    data: Required[list[dict]]
    error: NotRequired[str]

def process_user(user: UserDict) -> str:
    return user["name"]  # Type-safe key access
```

## Callable

```python
from collections.abc import Callable

# Function type
Handler = Callable[[str, int], bool]

def register(callback: Callable[[str], None]) -> None:
    pass

# With keyword args (use Protocol instead)
from typing import Protocol

class Processor(Protocol):
    def __call__(self, data: str, *, verbose: bool = False) -> int:
        ...
```

## Generics

```python
from typing import TypeVar

T = TypeVar("T")

def first(items: list[T]) -> T | None:
    return items[0] if items else None

# Bounded TypeVar
from typing import SupportsFloat

N = TypeVar("N", bound=SupportsFloat)

def average(values: list[N]) -> float:
    return sum(float(v) for v in values) / len(values)
```

## Protocol (Structural Typing)

```python
from typing import Protocol

class Readable(Protocol):
    def read(self, n: int = -1) -> bytes:
        ...

def load(source: Readable) -> dict:
    """Accepts any object with read() method."""
    data = source.read()
    return json.loads(data)

# Works with file, BytesIO, custom classes
load(open("data.json", "rb"))
load(io.BytesIO(b"{}"))
```

## Type Guards

```python
from typing import TypeGuard

def is_string_list(val: list[object]) -> TypeGuard[list[str]]:
    return all(isinstance(x, str) for x in val)

def process(items: list[object]) -> None:
    if is_string_list(items):
        # items is now list[str]
        print(", ".join(items))
```

## Literal and Final

```python
from typing import Literal, Final

Mode = Literal["read", "write", "append"]

def open_file(path: str, mode: Mode) -> None:
    pass

# Constants
MAX_SIZE: Final = 1024
API_VERSION: Final[str] = "v2"
```

## Quick Reference

| Type | Use Case |
|------|----------|
| `X \| None` | Optional value |
| `list[T]` | Homogeneous list |
| `dict[K, V]` | Dictionary |
| `Callable[[Args], Ret]` | Function type |
| `TypeVar("T")` | Generic parameter |
| `Protocol` | Structural typing |
| `TypedDict` | Dict with fixed keys |
| `Literal["a", "b"]` | Specific values only |
| `Final` | Cannot be reassigned |

## Type Checker Commands

```bash
# mypy
mypy src/ --strict

# pyright
pyright src/

# In pyproject.toml
[tool.mypy]
strict = true
python_version = "3.11"
```

## Additional Resources

- `./references/generics-advanced.md` - TypeVar, ParamSpec, TypeVarTuple
- `./references/protocols-patterns.md` - Structural typing, runtime protocols
- `./references/type-narrowing.md` - Guards, isinstance, assert
- `./references/mypy-config.md` - mypy/pyright configuration
- `./references/runtime-validation.md` - Pydantic v2, typeguard, beartype
- `./references/overloads.md` - @overload decorator patterns

## Scripts

- `./scripts/check-types.sh` - Run type checkers with common options

## Assets

- `./assets/pyproject-typing.toml` - Recommended mypy/pyright config

---

## See Also

This is a **foundation skill** with no prerequisites.

**Related Skills:**
- `python-pytest-patterns` - Type-safe fixtures and mocking

**Build on this skill:**
- `python-async-patterns` - Async type annotations
- `python-fastapi-patterns` - Pydantic models and validation
- `python-database-patterns` - SQLAlchemy type annotations
