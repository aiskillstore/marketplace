# Advanced Generics

Deep dive into Python's generic type system.

## TypeVar Basics

```python
from typing import TypeVar

# Unconstrained TypeVar
T = TypeVar("T")

def identity(x: T) -> T:
    return x

# Usage - type is preserved
reveal_type(identity(42))      # int
reveal_type(identity("hello")) # str
```

## Bounded TypeVar

```python
from typing import TypeVar

# Upper bound - T must be subtype of bound
class Animal:
    def speak(self) -> str:
        return "..."

class Dog(Animal):
    def speak(self) -> str:
        return "woof"

A = TypeVar("A", bound=Animal)

def make_speak(animal: A) -> A:
    print(animal.speak())
    return animal

# Works with Animal or any subclass
dog = make_speak(Dog())  # Returns Dog, not Animal
```

## Constrained TypeVar

```python
from typing import TypeVar

# Constrained to specific types
StrOrBytes = TypeVar("StrOrBytes", str, bytes)

def concat(a: StrOrBytes, b: StrOrBytes) -> StrOrBytes:
    return a + b

# Must be same type
concat("a", "b")     # OK -> str
concat(b"a", b"b")   # OK -> bytes
# concat("a", b"b")  # Error: can't mix
```

## Generic Classes

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

    def peek(self) -> T | None:
        return self._items[-1] if self._items else None

# Usage
int_stack: Stack[int] = Stack()
int_stack.push(1)
int_stack.push(2)
value = int_stack.pop()  # int

str_stack: Stack[str] = Stack()
str_stack.push("hello")
```

## Multiple Type Parameters

```python
from typing import Generic, TypeVar

K = TypeVar("K")
V = TypeVar("V")

class Pair(Generic[K, V]):
    def __init__(self, key: K, value: V) -> None:
        self.key = key
        self.value = value

    def swap(self) -> "Pair[V, K]":
        return Pair(self.value, self.key)

pair: Pair[str, int] = Pair("age", 30)
swapped = pair.swap()  # Pair[int, str]
```

## Self Type (Python 3.11+)

```python
from typing import Self

class Builder:
    def __init__(self) -> None:
        self.value = ""

    def add(self, text: str) -> Self:
        self.value += text
        return self

    def build(self) -> str:
        return self.value

class HTMLBuilder(Builder):
    def tag(self, name: str) -> Self:
        self.value = f"<{name}>{self.value}</{name}>"
        return self

# Chaining works with correct types
html = HTMLBuilder().add("Hello").tag("p").build()
```

## ParamSpec (Python 3.10+)

```python
from typing import ParamSpec, TypeVar, Callable

P = ParamSpec("P")
R = TypeVar("R")

def with_logging(func: Callable[P, R]) -> Callable[P, R]:
    """Decorator that preserves function signature."""
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@with_logging
def greet(name: str, excited: bool = False) -> str:
    return f"Hello, {name}{'!' if excited else '.'}"

# Signature preserved:
greet("Alice", excited=True)  # OK
# greet(123)  # Type error
```

## TypeVarTuple (Python 3.11+)

```python
from typing import TypeVarTuple, Unpack

Ts = TypeVarTuple("Ts")

def concat_tuples(
    a: tuple[*Ts],
    b: tuple[*Ts]
) -> tuple[*Ts, *Ts]:
    return (*a, *b)

# Usage
result = concat_tuples((1, "a"), (2, "b"))
# result: tuple[int, str, int, str]
```

## Covariance and Contravariance

```python
from typing import TypeVar

# Covariant: Can use subtype
T_co = TypeVar("T_co", covariant=True)

class Reader(Generic[T_co]):
    def read(self) -> T_co:
        ...

# Contravariant: Can use supertype
T_contra = TypeVar("T_contra", contravariant=True)

class Writer(Generic[T_contra]):
    def write(self, value: T_contra) -> None:
        ...

# Invariant (default): Must be exact type
T = TypeVar("T")  # Invariant

class Container(Generic[T]):
    def get(self) -> T:
        ...
    def set(self, value: T) -> None:
        ...
```

## Generic Protocols

```python
from typing import Protocol, TypeVar

T = TypeVar("T")

class Comparable(Protocol[T]):
    def __lt__(self, other: T) -> bool:
        ...
    def __gt__(self, other: T) -> bool:
        ...

def max_value(a: T, b: T) -> T:
    return a if a > b else b

# Works with any comparable type
max_value(1, 2)        # int
max_value("a", "b")    # str
```

## Type Aliases

```python
from typing import TypeAlias

# Simple alias
Vector: TypeAlias = list[float]
Matrix: TypeAlias = list[Vector]

# Generic alias
from typing import TypeVar

T = TypeVar("T")
Result: TypeAlias = tuple[T, str | None]

def parse(data: str) -> Result[int]:
    try:
        return (int(data), None)
    except ValueError as e:
        return (0, str(e))
```

## NewType

```python
from typing import NewType

# Create distinct types for type safety
UserId = NewType("UserId", int)
OrderId = NewType("OrderId", int)

def get_user(user_id: UserId) -> dict:
    ...

def get_order(order_id: OrderId) -> dict:
    ...

user_id = UserId(42)
order_id = OrderId(42)

get_user(user_id)   # OK
# get_user(order_id)  # Type error!
# get_user(42)        # Type error!
```

## Best Practices

1. **Name TypeVars descriptively** - `T`, `K`, `V` for simple cases; `ItemT`, `KeyT` for complex
2. **Use bounds** - When you need method access on type parameter
3. **Prefer Protocol** - Over ABC for structural typing
4. **Use Self** - Instead of quoted class names in return types
5. **Covariance** - For read-only containers
6. **Contravariance** - For write-only/function parameter types
7. **Invariance** - For mutable containers (default, usually correct)
