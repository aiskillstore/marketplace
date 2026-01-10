# Type Narrowing

Techniques for narrowing types in conditional branches.

## isinstance Narrowing

```python
def process(value: str | int | list[str]) -> str:
    if isinstance(value, str):
        # value is str here
        return value.upper()
    elif isinstance(value, int):
        # value is int here
        return str(value * 2)
    else:
        # value is list[str] here
        return ", ".join(value)
```

## None Checks

```python
def greet(name: str | None) -> str:
    if name is None:
        return "Hello, stranger"
    # name is str here (not None)
    return f"Hello, {name}"

# Also works with truthiness
def greet_truthy(name: str | None) -> str:
    if name:
        # name is str here
        return f"Hello, {name}"
    return "Hello, stranger"
```

## Assertion Narrowing

```python
def process(data: dict | None) -> str:
    assert data is not None
    # data is dict here
    return str(data.get("key"))

def validate(value: int | str) -> int:
    assert isinstance(value, int), "Must be int"
    # value is int here
    return value * 2
```

## Type Guards

```python
from typing import TypeGuard

def is_string_list(val: list[object]) -> TypeGuard[list[str]]:
    """Check if all elements are strings."""
    return all(isinstance(x, str) for x in val)

def process(items: list[object]) -> str:
    if is_string_list(items):
        # items is list[str] here
        return ", ".join(items)
    return "Not all strings"

# With TypeVar
from typing import TypeVar

T = TypeVar("T")

def is_not_none(val: T | None) -> TypeGuard[T]:
    return val is not None

def process_optional(value: str | None) -> str:
    if is_not_none(value):
        # value is str here
        return value.upper()
    return "default"
```

## TypeIs (Python 3.13+)

```python
from typing import TypeIs

# TypeIs narrows more aggressively than TypeGuard
def is_str(val: object) -> TypeIs[str]:
    return isinstance(val, str)

def process(value: object) -> str:
    if is_str(value):
        # value is str here
        return value.upper()
    return "not a string"
```

## Discriminated Unions

```python
from typing import Literal, TypedDict

class SuccessResult(TypedDict):
    status: Literal["success"]
    data: dict

class ErrorResult(TypedDict):
    status: Literal["error"]
    message: str

Result = SuccessResult | ErrorResult

def handle_result(result: Result) -> str:
    if result["status"] == "success":
        # result is SuccessResult
        return str(result["data"])
    else:
        # result is ErrorResult
        return f"Error: {result['message']}"
```

## Match Statement (Python 3.10+)

```python
def describe(value: int | str | list[int]) -> str:
    match value:
        case int(n):
            return f"Integer: {n}"
        case str(s):
            return f"String: {s}"
        case [first, *rest]:
            return f"List starting with {first}"
        case _:
            return "Unknown"
```

## hasattr Narrowing

```python
from typing import Protocol

class HasName(Protocol):
    name: str

def greet(obj: object) -> str:
    if hasattr(obj, "name") and isinstance(obj.name, str):
        # Type checkers may not narrow here
        # Use Protocol + isinstance instead
        return f"Hello, {obj.name}"
    return "Hello"
```

## Callable Narrowing

```python
from collections.abc import Callable

def execute(func_or_value: Callable[[], int] | int) -> int:
    if callable(func_or_value):
        # func_or_value is Callable[[], int]
        return func_or_value()
    else:
        # func_or_value is int
        return func_or_value
```

## Exhaustiveness Checking

```python
from typing import Literal, Never

def assert_never(value: Never) -> Never:
    raise AssertionError(f"Unexpected value: {value}")

Status = Literal["pending", "active", "closed"]

def handle_status(status: Status) -> str:
    if status == "pending":
        return "Waiting..."
    elif status == "active":
        return "In progress"
    elif status == "closed":
        return "Done"
    else:
        # If we add a new status, type checker will error here
        assert_never(status)
```

## Narrowing in Loops

```python
from typing import TypeGuard

def is_valid(item: str | None) -> TypeGuard[str]:
    return item is not None

def process_items(items: list[str | None]) -> list[str]:
    result: list[str] = []
    for item in items:
        if is_valid(item):
            # item is str here
            result.append(item.upper())
    return result

# Or use filter with type guard
def process_items_functional(items: list[str | None]) -> list[str]:
    valid_items = filter(is_valid, items)
    return [item.upper() for item in valid_items]
```

## Class Type Narrowing

```python
class Animal:
    pass

class Dog(Animal):
    def bark(self) -> str:
        return "Woof!"

class Cat(Animal):
    def meow(self) -> str:
        return "Meow!"

def make_sound(animal: Animal) -> str:
    if isinstance(animal, Dog):
        return animal.bark()  # animal is Dog
    elif isinstance(animal, Cat):
        return animal.meow()  # animal is Cat
    return "..."
```

## Common Patterns

### Optional Unwrapping

```python
def unwrap_or_default(value: T | None, default: T) -> T:
    if value is not None:
        return value
    return default

# With early return
def process(data: dict | None) -> dict:
    if data is None:
        return {}
    # data is dict for rest of function
    return {k: v.upper() for k, v in data.items()}
```

### Safe Dictionary Access

```python
def get_nested(data: dict, *keys: str) -> object | None:
    result: object = data
    for key in keys:
        if not isinstance(result, dict):
            return None
        result = result.get(key)
        if result is None:
            return None
    return result
```

## Best Practices

1. **Prefer isinstance** - Most reliable for type narrowing
2. **Use TypeGuard** - For complex conditions
3. **Check None explicitly** - `is None` or `is not None`
4. **Use exhaustiveness checks** - Catch missing cases
5. **Avoid hasattr** - Type checkers struggle with it
6. **Match statements** - Clean pattern matching (3.10+)
