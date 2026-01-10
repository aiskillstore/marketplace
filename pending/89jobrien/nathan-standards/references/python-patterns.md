---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: reference
parent: nathan-standards
---

# Python Patterns for Nathan

Detailed Python patterns and conventions for the Nathan project.

## Module Template

```python
"""Module description.

Detailed explanation of what this module does and its responsibilities.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class DataModel:
    """Immutable data model with slots for memory efficiency."""

    name: str
    value: int
    optional_field: str | None = None


class ServiceClass:
    """Service class with clear responsibilities.

    Example:
        >>> service = ServiceClass()
        >>> result = service.do_something()
    """

    def __init__(self, config_path: Path | None = None) -> None:
        self.config_path = config_path or self._default_path()
        self._cache: dict[str, Any] = {}

    def _default_path(self) -> Path:
        return Path.home() / ".config" / "service.yaml"

    def do_something(self, param: str) -> dict[str, Any]:
        """Do something useful.

        Args:
            param: Description of parameter.

        Returns:
            Dictionary with result data.

        Raises:
            ValueError: If param is invalid.
        """
        if not param:
            raise ValueError("param cannot be empty")
        return {"result": param}


__all__ = ["DataModel", "ServiceClass"]
```

## Async HTTP Client Pattern

```python
"""Async HTTP client for webhook calls."""

from __future__ import annotations

from typing import Any

import httpx


async def trigger_webhook(
    *,
    url: str,
    parameters: dict[str, Any],
    timeout_s: float = 30.0,
    shared_secret: str | None = None,
    shared_secret_header: str = "X-N8N-SECRET",
) -> dict[str, Any]:
    """Execute webhook and return structured result.

    Returns a stable shape:
    - success: bool
    - data: dict (response JSON if any)
    - status_code: int | None
    - error: str | None
    """
    headers: dict[str, str] = {"Content-Type": "application/json"}
    if shared_secret:
        headers[shared_secret_header] = shared_secret

    try:
        async with httpx.AsyncClient(timeout=timeout_s) as client:
            resp = await client.post(url, json=parameters, headers=headers)
            status_code = resp.status_code
            resp.raise_for_status()

            try:
                data = resp.json()
            except ValueError:
                data = {"raw": resp.text}

            return {
                "success": True,
                "data": data,
                "status_code": status_code,
                "error": None,
            }

    except httpx.TimeoutException:
        return {
            "success": False,
            "data": {},
            "status_code": None,
            "error": f"Timeout after {timeout_s}s",
        }
    except httpx.HTTPStatusError as e:
        return {
            "success": False,
            "data": {},
            "status_code": e.response.status_code if e.response else None,
            "error": f"HTTP error: {e}",
        }
    except httpx.HTTPError as e:
        return {
            "success": False,
            "data": {},
            "status_code": None,
            "error": f"HTTP error: {e}",
        }
```

## YAML Registry Pattern

```python
"""YAML registry loader."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class RegistryError(RuntimeError):
    """Registry loading or validation error."""

    pass


@dataclass(frozen=True, slots=True)
class CommandDefinition:
    """Definition of a webhook command."""

    name: str
    endpoint: str
    method: str
    required_params: tuple[str, ...]
    optional_params: tuple[str, ...]
    description: str
    example: dict[str, Any]

    def validate_params(self, params: dict[str, Any]) -> None:
        """Validate required parameters are present."""
        missing = [k for k in self.required_params if k not in params]
        if missing:
            raise RegistryError(f"Missing required params: {missing}")


class Registry:
    """Load and manage command registry from YAML."""

    def __init__(self, config_path: Path) -> None:
        self.config_path = config_path
        self.commands: dict[str, CommandDefinition] = {}
        self._load()

    def _load(self) -> None:
        if not self.config_path.exists():
            return

        try:
            config = yaml.safe_load(self.config_path.read_text())
        except Exception as e:
            raise RegistryError(f"Failed to load YAML: {e}") from e

        if not config:
            return

        commands = config.get("commands", {})
        for name, cmd in commands.items():
            if not isinstance(cmd, dict):
                continue

            self.commands[name] = CommandDefinition(
                name=name,
                endpoint=str(cmd.get("endpoint", "")),
                method=str(cmd.get("method", "POST")),
                required_params=tuple(cmd.get("required_params", [])),
                optional_params=tuple(cmd.get("optional_params", [])),
                description=str(cmd.get("description", "")),
                example=dict(cmd.get("example", {})),
            )

    def get(self, name: str) -> CommandDefinition | None:
        return self.commands.get(name)

    def list_all(self) -> list[dict[str, Any]]:
        return [
            {
                "name": cmd.name,
                "description": cmd.description,
                "required_params": list(cmd.required_params),
                "example": cmd.example,
            }
            for cmd in sorted(self.commands.values(), key=lambda c: c.name)
        ]
```

## Pydantic Model Pattern

```python
"""Pydantic models for validation."""

from __future__ import annotations

from pydantic import BaseModel, Field


class NodeDefinition(BaseModel):
    """n8n node definition."""

    id: str = Field(..., description="Unique node identifier")
    name: str = Field(..., description="Display name")
    type: str = Field(..., description="Node type e.g. n8n-nodes-base.webhook")
    typeVersion: int = Field(default=1, ge=1)
    position: tuple[int, int] = Field(default=(0, 0))
    parameters: dict[str, object] = Field(default_factory=dict)
    webhookId: str | None = None
    credentials: dict[str, object] | None = None


class ConnectionDefinition(BaseModel):
    """Connection between nodes."""

    from_node: str = Field(..., alias="from")
    to_node: str = Field(..., alias="to")
    from_output: str = Field(default="main")
    from_index: int = Field(default=0, ge=0)
    to_input: str = Field(default="main")
    to_index: int = Field(default=0, ge=0)

    class Config:
        populate_by_name = True
```

## Test Pattern

```python
"""Test module for component."""

from __future__ import annotations

from pathlib import Path

import pytest

from nathan.module import Component


@pytest.fixture
def sample_data() -> dict[str, object]:
    """Provide sample test data."""
    return {"key": "value", "count": 42}


@pytest.fixture
def temp_config(tmp_path: Path) -> Path:
    """Create temporary config file."""
    config = tmp_path / "config.yaml"
    config.write_text("key: value\n")
    return config


class TestComponent:
    """Tests for Component class."""

    def test_init_default(self) -> None:
        """Test default initialization."""
        comp = Component()
        assert comp is not None

    def test_init_with_config(self, temp_config: Path) -> None:
        """Test initialization with config."""
        comp = Component(config_path=temp_config)
        assert comp.config_path == temp_config

    def test_process_valid_input(self, sample_data: dict[str, object]) -> None:
        """Test processing with valid input."""
        comp = Component()
        result = comp.process(sample_data)
        assert result["success"] is True

    def test_process_invalid_input(self) -> None:
        """Test processing with invalid input raises error."""
        comp = Component()
        with pytest.raises(ValueError, match="cannot be empty"):
            comp.process({})


@pytest.mark.asyncio
async def test_async_operation() -> None:
    """Test async operation."""
    result = await some_async_function()
    assert result is not None
```

## Logging Pattern

```python
"""Structured logging setup."""

from __future__ import annotations

import logging
import sys

def setup_logging(level: int = logging.INFO) -> None:
    """Configure structured logging."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stderr)],
    )

# In modules, use module-level logger
logger = logging.getLogger(__name__)

# Log with context
logger.info("Processing item", extra={"item_id": item.id, "status": "started"})
logger.error("Operation failed", extra={"error": str(e)}, exc_info=True)
```

## Type Hints Quick Reference

| Pattern | Use |
|---------|-----|
| `str \| None` | Optional string (not `Optional[str]`) |
| `list[str]` | List of strings (not `List[str]`) |
| `dict[str, Any]` | Dict with string keys (not `Dict`) |
| `tuple[int, int]` | Fixed-size tuple |
| `tuple[str, ...]` | Variable-length tuple |
| `Path` | Always use pathlib.Path |
| `-> None` | Explicit None return |
