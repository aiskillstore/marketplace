# Protocol Patterns

Structural typing with Protocol for flexible, decoupled code.

## Basic Protocol

```python
from typing import Protocol

class Drawable(Protocol):
    def draw(self) -> None:
        ...

class Circle:
    def draw(self) -> None:
        print("Drawing circle")

class Square:
    def draw(self) -> None:
        print("Drawing square")

def render(shape: Drawable) -> None:
    shape.draw()

# Both work - no inheritance needed
render(Circle())
render(Square())
```

## Protocol with Attributes

```python
from typing import Protocol

class Named(Protocol):
    name: str

class HasId(Protocol):
    id: int
    name: str

class User:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name

def greet(entity: Named) -> str:
    return f"Hello, {entity.name}"

# Works with any object having 'name' attribute
greet(User(1, "Alice"))
```

## Protocol with Methods

```python
from typing import Protocol

class Closeable(Protocol):
    def close(self) -> None:
        ...

class Flushable(Protocol):
    def flush(self) -> None:
        ...

class CloseableAndFlushable(Closeable, Flushable, Protocol):
    """Combined protocol."""
    pass

def cleanup(resource: CloseableAndFlushable) -> None:
    resource.flush()
    resource.close()
```

## Callable Protocol

```python
from typing import Protocol

class Comparator(Protocol):
    def __call__(self, a: int, b: int) -> int:
        """Return negative, zero, or positive."""
        ...

def sort_with(items: list[int], cmp: Comparator) -> list[int]:
    return sorted(items, key=lambda x: cmp(x, 0))

# Lambda works
sort_with([3, 1, 2], lambda a, b: a - b)

# Function works
def compare(a: int, b: int) -> int:
    return a - b

sort_with([3, 1, 2], compare)
```

## Generic Protocol

```python
from typing import Protocol, TypeVar

T = TypeVar("T")

class Container(Protocol[T]):
    def get(self) -> T:
        ...

    def set(self, value: T) -> None:
        ...

class Box:
    def __init__(self, value: int):
        self._value = value

    def get(self) -> int:
        return self._value

    def set(self, value: int) -> None:
        self._value = value

def process(container: Container[int]) -> int:
    value = container.get()
    container.set(value * 2)
    return container.get()

process(Box(5))  # Returns 10
```

## Runtime Checkable Protocol

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Sized(Protocol):
    def __len__(self) -> int:
        ...

# Now isinstance() works
def process(obj: object) -> int:
    if isinstance(obj, Sized):
        return len(obj)
    return 0

process([1, 2, 3])  # 3
process("hello")     # 5
process(42)          # 0
```

## Protocol vs ABC

```python
from abc import ABC, abstractmethod
from typing import Protocol

# ABC - Requires explicit inheritance
class AbstractReader(ABC):
    @abstractmethod
    def read(self) -> str:
        pass

class FileReader(AbstractReader):  # Must inherit
    def read(self) -> str:
        return "content"

# Protocol - Structural (duck typing)
class ReaderProtocol(Protocol):
    def read(self) -> str:
        ...

class AnyReader:  # No inheritance needed
    def read(self) -> str:
        return "content"

def process(reader: ReaderProtocol) -> str:
    return reader.read()

process(AnyReader())  # Works!
process(FileReader())  # Also works!
```

## Common Protocols

### Supports Protocols

```python
from typing import SupportsInt, SupportsFloat, SupportsBytes, SupportsAbs

def to_int(value: SupportsInt) -> int:
    return int(value)

to_int(3.14)   # OK - float supports __int__
to_int("42")   # Error - str doesn't support __int__
```

### Iterator Protocol

```python
from typing import Protocol, TypeVar

T = TypeVar("T", covariant=True)

class Iterator(Protocol[T]):
    def __next__(self) -> T:
        ...

class Iterable(Protocol[T]):
    def __iter__(self) -> Iterator[T]:
        ...
```

### Context Manager Protocol

```python
from typing import Protocol, TypeVar

T = TypeVar("T")

class ContextManager(Protocol[T]):
    def __enter__(self) -> T:
        ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object | None,
    ) -> bool | None:
        ...
```

## Real-World Patterns

### Repository Pattern

```python
from typing import Protocol, TypeVar

T = TypeVar("T")

class Repository(Protocol[T]):
    def get(self, id: int) -> T | None:
        ...

    def save(self, entity: T) -> None:
        ...

    def delete(self, id: int) -> bool:
        ...

class User:
    id: int
    name: str

class InMemoryUserRepo:
    def __init__(self):
        self._data: dict[int, User] = {}

    def get(self, id: int) -> User | None:
        return self._data.get(id)

    def save(self, entity: User) -> None:
        self._data[entity.id] = entity

    def delete(self, id: int) -> bool:
        return self._data.pop(id, None) is not None

def process_users(repo: Repository[User]) -> None:
    user = repo.get(1)
    if user:
        repo.delete(user.id)
```

### Event Handler

```python
from typing import Protocol

class Event:
    pass

class UserCreated(Event):
    def __init__(self, user_id: int):
        self.user_id = user_id

class EventHandler(Protocol):
    def can_handle(self, event: Event) -> bool:
        ...

    def handle(self, event: Event) -> None:
        ...

class UserCreatedHandler:
    def can_handle(self, event: Event) -> bool:
        return isinstance(event, UserCreated)

    def handle(self, event: Event) -> None:
        if isinstance(event, UserCreated):
            print(f"User {event.user_id} created")

def dispatch(event: Event, handlers: list[EventHandler]) -> None:
    for handler in handlers:
        if handler.can_handle(event):
            handler.handle(event)
```

## Best Practices

1. **Prefer Protocol over ABC** - For external interfaces
2. **Use @runtime_checkable sparingly** - Has performance cost
3. **Keep protocols minimal** - Single responsibility
4. **Document expected behavior** - Protocols only define shape, not behavior
5. **Combine protocols** - For complex requirements
6. **Use Generic protocols** - For type-safe containers
