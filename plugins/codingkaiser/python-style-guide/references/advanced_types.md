# Advanced Type Annotations Reference

This document provides detailed guidance on advanced type annotation patterns in Python.

## Union Types

Use `|` (union operator) for Python 3.10+ or `Union` for earlier versions:

```python
# Python 3.10+
def process(value: int | str) -> None:
    ...

# Python 3.9 and earlier
from typing import Union
def process(value: Union[int, str]) -> None:
    ...
```

## Optional Types

`Optional[X]` is shorthand for `X | None`:

```python
from typing import Optional

# These are equivalent:
def foo(x: Optional[int]) -> None: ...
def foo(x: int | None) -> None: ...  # Preferred in Python 3.10+
```

## Callable Types

For function types, use `Callable`:

```python
from collections.abc import Callable

def apply_func(func: Callable[[int, int], int], x: int, y: int) -> int:
    return func(x, y)

# Callable[[arg1_type, arg2_type], return_type]
```

For functions with variable arguments:

```python
# Use ... for variable arguments
def accepts_any_callable(func: Callable[..., int]) -> None:
    ...
```

## Sequence, Mapping, and Iterable

Use abstract types from `collections.abc` when you don't need specific container features:

```python
from collections.abc import Sequence, Mapping, Iterable

def process_items(items: Sequence[str]) -> None:
    """Works with lists, tuples, or any sequence."""
    ...

def process_mapping(data: Mapping[str, int]) -> None:
    """Works with dicts or any mapping."""
    ...

def sum_numbers(nums: Iterable[int]) -> int:
    """Works with any iterable."""
    return sum(nums)
```

## Protocol and Structural Subtyping

Define structural types using `Protocol`:

```python
from typing import Protocol

class Drawable(Protocol):
    def draw(self) -> None:
        ...

def render(obj: Drawable) -> None:
    obj.draw()  # Any object with a draw() method works
```

## TypedDict for Structured Dictionaries

Use `TypedDict` for dictionaries with known keys:

```python
from typing import TypedDict

class Employee(TypedDict):
    name: str
    id: int
    department: str

def process_employee(emp: Employee) -> None:
    print(emp["name"])  # Type checker knows this key exists
```

Optional fields:

```python
from typing import TypedDict, NotRequired

class Employee(TypedDict):
    name: str
    id: int
    department: NotRequired[str]  # Optional field
```

## Literal Types

Use `Literal` for specific values:

```python
from typing import Literal

def set_mode(mode: Literal["read", "write", "append"]) -> None:
    ...

# Type checker ensures only these values are passed
set_mode("read")  # OK
set_mode("delete")  # Error
```

## Generic Classes

Create generic classes with `Generic`:

```python
from typing import Generic, TypeVar

T = TypeVar("T")

class Stack(Generic[T]):
    def __init__(self) -> None:
        self._items: list[T] = []
    
    def push(self, item: T) -> None:
        self._items.append(item)
    
    def pop(self) -> T:
        return self._items.pop()

# Usage
int_stack: Stack[int] = Stack()
int_stack.push(42)
```

## ParamSpec for Higher-Order Functions

Use `ParamSpec` to preserve function signatures:

```python
from typing import ParamSpec, TypeVar, Callable

P = ParamSpec("P")
R = TypeVar("R")

def log_calls(func: Callable[P, R]) -> Callable[P, R]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@log_calls
def greet(name: str, excited: bool = False) -> str:
    return f"Hello, {name}{'!' if excited else '.'}"

# Type checker preserves the signature of greet
```

## TypeGuard for Type Narrowing

Use `TypeGuard` for custom type checking functions:

```python
from typing import TypeGuard

def is_str_list(val: list[object]) -> TypeGuard[list[str]]:
    return all(isinstance(x, str) for x in val)

def process(items: list[object]) -> None:
    if is_str_list(items):
        # Type checker knows items is list[str] here
        print(", ".join(items))
```

## Annotating *args and **kwargs

```python
def foo(*args: int, **kwargs: str) -> None:
    # args is tuple[int, ...]
    # kwargs is dict[str, str]
    ...
```

## Overload for Multiple Signatures

Use `@overload` for functions with different return types based on arguments:

```python
from typing import overload

@overload
def process(x: int) -> int: ...

@overload
def process(x: str) -> str: ...

def process(x: int | str) -> int | str:
    if isinstance(x, int):
        return x * 2
    return x.upper()
```

## Self Type (Python 3.11+)

Use `Self` for methods that return the instance:

```python
from typing import Self

class Builder:
    def add_item(self, item: str) -> Self:
        self.items.append(item)
        return self  # Return type is automatically the class type
    
    def build(self) -> dict:
        return {"items": self.items}
```

For Python < 3.11, use TypeVar:

```python
from typing import TypeVar

TBuilder = TypeVar("TBuilder", bound="Builder")

class Builder:
    def add_item(self: TBuilder, item: str) -> TBuilder:
        self.items.append(item)
        return self
```

## Best Practices

1. Use the most general type that works (e.g., `Sequence` over `list`)
2. Use `Protocol` for duck typing
3. Use `TypedDict` for structured dictionaries
4. Use `Literal` to restrict to specific values
5. Use `TypeGuard` for custom type narrowing
6. Always annotate public APIs
7. Use `Any` sparingly and explicitly when needed
8. Prefer built-in generic types (`list`, `dict`) over `typing` equivalents (Python 3.9+)
