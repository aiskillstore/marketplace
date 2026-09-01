#!/usr/bin/env python3
"""Validate one worker envelope against the checked-in JSON Schema subset.

The project deliberately has no third-party runtime dependencies.  This validator
implements only the Draft 7 keywords used by worker-result.schema.json and fails
closed if the schema grows an unsupported keyword.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any


SUPPORTED_KEYS = {
    "$schema", "title", "description", "type", "additionalProperties",
    "required", "properties", "items", "enum", "minLength", "maxLength",
    "minimum", "maximum",
}
MAX_JSON_BYTES = 1024 * 1024


class ValidationError(ValueError):
    pass


def load_json(path: Path) -> Any:
    def reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValidationError(f"duplicate key {key!r}")
            result[key] = value
        return result

    try:
        with path.open("rb") as handle:
            payload = handle.read(MAX_JSON_BYTES + 1)
        if not payload or len(payload) > MAX_JSON_BYTES:
            raise ValidationError("JSON input is empty or oversized")
        return json.loads(
            payload.decode("utf-8", "strict"), object_pairs_hook=reject_duplicates
        )
    except (OSError, json.JSONDecodeError, UnicodeError) as exc:
        raise ValidationError(str(exc)) from exc


def type_matches(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "boolean":
        return type(value) is bool
    if expected == "number":
        return (type(value) in (int, float)
                and not isinstance(value, bool)
                and math.isfinite(value))
    raise ValidationError(f"unsupported schema type {expected!r}")


def preflight_schema(schema: Any, location: str = "$") -> None:
    if not isinstance(schema, dict):
        raise ValidationError(f"schema node at {location} is not an object")
    unsupported = set(schema) - SUPPORTED_KEYS
    if unsupported:
        raise ValidationError(
            f"schema uses unsupported keyword(s) at {location}: {sorted(unsupported)}")
    properties = schema.get("properties", {})
    if not isinstance(properties, dict):
        raise ValidationError(f"schema properties at {location} is not an object")
    for key, child in properties.items():
        preflight_schema(child, f"{location}.properties.{key}")
    if "items" in schema:
        preflight_schema(schema["items"], f"{location}.items")


def validate(value: Any, schema: dict[str, Any], location: str = "$") -> None:
    expected_type = schema.get("type")
    if expected_type is not None and not type_matches(value, expected_type):
        raise ValidationError(f"{location}: expected {expected_type}")
    if "enum" in schema and value not in schema["enum"]:
        raise ValidationError(f"{location}: value is not in the allowed enum")

    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            raise ValidationError(f"{location}: string is too short")
        if len(value) > schema.get("maxLength", len(value)):
            raise ValidationError(f"{location}: string is too long")

    if type(value) in (int, float):
        if "minimum" in schema and value < schema["minimum"]:
            raise ValidationError(f"{location}: number is below minimum")
        if "maximum" in schema and value > schema["maximum"]:
            raise ValidationError(f"{location}: number is above maximum")

    if isinstance(value, list) and "items" in schema:
        for index, item in enumerate(value):
            validate(item, schema["items"], f"{location}[{index}]")

    if isinstance(value, dict):
        required = set(schema.get("required", []))
        missing = required - set(value)
        if missing:
            raise ValidationError(f"{location}: missing fields {sorted(missing)}")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            extra = set(value) - set(properties)
            if extra:
                raise ValidationError(f"{location}: unexpected fields {sorted(extra)}")
        for key, child_schema in properties.items():
            if key in value:
                validate(value[key], child_schema, f"{location}.{key}")


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: validate-envelope.py SCHEMA ENVELOPE", file=sys.stderr)
        return 64
    try:
        schema = load_json(Path(sys.argv[1]))
        envelope = load_json(Path(sys.argv[2]))
        if not isinstance(schema, dict):
            raise ValidationError("schema root is not an object")
        preflight_schema(schema)
        validate(envelope, schema)
    except ValidationError as exc:
        print(f"worker envelope invalid: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
