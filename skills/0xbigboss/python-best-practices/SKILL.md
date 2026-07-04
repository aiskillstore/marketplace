---
name: python-best-practices
description: Use when reading or writing Python files (.py, pyproject.toml, requirements.txt).
---

# Python Best Practices

Follows type-first, functional, and error handling patterns from CLAUDE.md. This skill covers language-specific idioms only.

## Make Illegal States Unrepresentable

Use Python's type system to prevent invalid states at type-check time.

**Frozen dataclasses for immutable domain models:**
```python
from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class User:
    id: str
    email: str
    name: str
    created_at: datetime

# Frozen dataclasses are immutable — no accidental mutation
```

**Discriminated unions with Literal:**
```python
from dataclasses import dataclass
from typing import Literal

@dataclass
class Success:
    status: Literal["success"] = "success"
    data: str

@dataclass
class Failure:
    status: Literal["error"] = "error"
    error: Exception

RequestState = Success | Failure

def handle_state(state: RequestState) -> None:
    match state:
        case Success(data=data):
            render(data)
        case Failure(error=err):
            show_error(err)
```

**NewType for domain primitives:**
```python
from typing import NewType

UserId = NewType("UserId", str)
OrderId = NewType("OrderId", str)

def get_user(user_id: UserId) -> User:
    # Type checker prevents passing OrderId here
    ...
```

**Protocol for structural typing:**
```python
from typing import Protocol

class Readable(Protocol):
    def read(self, n: int = -1) -> bytes: ...

def process_input(source: Readable) -> bytes:
    # Accepts any object with a read() method — no inheritance required
    return source.read()
```

## Python-Specific Error Handling

Chain exceptions with `from err` to preserve the original traceback:
```python
try:
    data = json.loads(raw)
except json.JSONDecodeError as err:
    raise ValueError(f"invalid JSON payload: {err}") from err
```

## Structured Logging

Use a module-level logger with `%s` formatting (deferred string interpolation):
```python
import logging

logger = logging.getLogger("myapp.widgets")

def create_widget(name: str) -> Widget:
    logger.debug("creating widget: %s", name)
    widget = Widget(name=name)
    logger.debug("created widget id=%s", widget.id)
    return widget
```

## Optional: ty

For fast type checking, consider [ty](https://docs.astral.sh/ty/) from Astral (creators of ruff and uv). Written in Rust, significantly faster than mypy or pyright.

```bash
uvx ty check          # run directly, no install needed
uvx ty check src/     # check specific path
```

```toml
# pyproject.toml
[tool.ty]
python-version = "3.12"
```

When to choose:
- `ty` — fastest, good for CI and large codebases (early stage, rapidly evolving)
- `pyright` — most complete type inference, VS Code integration
- `mypy` — mature, extensive plugin ecosystem
