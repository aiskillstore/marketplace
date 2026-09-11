"""Canonical JSON primitives used by deterministic artifact contracts."""
from __future__ import annotations

import hashlib
import json
import math
from typing import Any


def reject_non_finite_json(value: Any) -> None:
    """Reject values JSON can encode only as non-standard numeric tokens."""

    if type(value) is float:
        if not math.isfinite(value):
            raise ValueError("canonical JSON requires finite numeric values")
        return
    if isinstance(value, dict):
        for child in value.values():
            reject_non_finite_json(child)
        return
    if isinstance(value, (list, tuple)):
        for child in value:
            reject_non_finite_json(child)


def canonical_json(value: Any) -> str:
    reject_non_finite_json(value)
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()
