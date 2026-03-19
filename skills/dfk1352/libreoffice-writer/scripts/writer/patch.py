"""Patch parsing and application for Writer documents."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Literal

from writer.exceptions import PatchSyntaxError
from writer.targets import ListItem, TextFormatting, WriterTarget, parse_target

PatchApplyMode = Literal["atomic", "best_effort"]

_OPERATION_TYPES = {
    "insert_text",
    "replace_text",
    "delete_text",
    "format_text",
    "insert_table",
    "update_table",
    "delete_table",
    "insert_image",
    "update_image",
    "delete_image",
    "insert_list",
    "replace_list",
    "delete_list",
}

_INT_KEYS = {"rows", "cols", "width", "height"}
_BOOL_KEYS = {"list.ordered", "format.bold", "format.italic", "format.underline"}
_TARGET_INT_KEYS = {"occurrence", "index"}


@dataclass(frozen=True)
class PatchOperation:
    """Parsed patch operation."""

    operation_type: str
    target: WriterTarget | None
    payload: dict[str, Any]


@dataclass
class PatchOperationResult:
    """Result for one patch operation."""

    operation_type: str
    target: WriterTarget | None
    status: str
    error: str | None
    mutated: bool


@dataclass
class PatchApplyResult:
    """Aggregate patch application result."""

    mode: PatchApplyMode
    overall_status: str
    operations: list[PatchOperationResult]
    document_persisted: bool


def parse_patch(patch_text: str) -> list[PatchOperation]:
    """Parse Writer patch text into ordered operations."""
    blocks = _parse_blocks(patch_text)
    operations: list[PatchOperation] = []
    for block in blocks:
        operation_type = block.get("type")
        if operation_type is None:
            raise PatchSyntaxError("Operation block is missing type")
        if operation_type not in _OPERATION_TYPES:
            raise PatchSyntaxError(f"Unknown operation type: {operation_type}")

        target_fields = {
            key.split(".", 1)[1]: _coerce_target_value(key.split(".", 1)[1], value)
            for key, value in block.items()
            if key.startswith("target.")
        }
        target = parse_target(target_fields) if target_fields else None
        payload = _parse_payload(operation_type, block)
        _validate_operation_shape(operation_type, target, payload)
        operations.append(
            PatchOperation(
                operation_type=operation_type,
                target=target,
                payload=payload,
            )
        )
    return operations


def apply_operations(
    session, patch_text: str, mode: PatchApplyMode
) -> PatchApplyResult:
    """Apply patch operations to an already-open Writer session."""
    operations = parse_patch(patch_text)
    results: list[PatchOperationResult] = []

    if mode not in ("atomic", "best_effort"):
        raise PatchSyntaxError(f"Unsupported patch mode: {mode}")

    for index, operation in enumerate(operations):
        try:
            _dispatch_operation(session, operation)
            results.append(
                PatchOperationResult(
                    operation_type=operation.operation_type,
                    target=operation.target,
                    status="ok",
                    error=None,
                    mutated=True,
                )
            )
        except Exception as exc:
            results.append(
                PatchOperationResult(
                    operation_type=operation.operation_type,
                    target=operation.target,
                    status="failed",
                    error=str(exc),
                    mutated=False,
                )
            )
            if mode == "atomic":
                for skipped in operations[index + 1 :]:
                    results.append(
                        PatchOperationResult(
                            operation_type=skipped.operation_type,
                            target=skipped.target,
                            status="skipped",
                            error="Skipped because an earlier atomic operation failed",
                            mutated=False,
                        )
                    )
                session.reset()
                return PatchApplyResult(
                    mode=mode,
                    overall_status="failed",
                    operations=results,
                    document_persisted=False,
                )

    overall_status = "ok"
    if any(result.status == "failed" for result in results):
        overall_status = "partial"
    document_persisted = overall_status != "failed" and any(
        result.mutated for result in results
    )
    return PatchApplyResult(
        mode=mode,
        overall_status=overall_status,
        operations=results,
        document_persisted=document_persisted,
    )


def patch(
    path: str, patch_text: str, mode: PatchApplyMode = "atomic"
) -> PatchApplyResult:
    """Open a session, apply a patch, and persist if appropriate."""
    from writer.session import open_writer_session

    session = open_writer_session(path)
    try:
        result = apply_operations(session, patch_text, mode)
        should_save = result.overall_status != "failed" and any(
            operation.mutated for operation in result.operations
        )
        session.close(save=should_save)
        result.document_persisted = should_save
        return result
    finally:
        if not session._closed:
            session.close(save=False)


def _parse_blocks(patch_text: str) -> list[dict[str, str]]:
    lines = patch_text.splitlines()
    current: dict[str, str] | None = None
    blocks: list[dict[str, str]] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            index += 1
            continue
        if stripped == "[operation]":
            if current is not None:
                blocks.append(current)
            current = {}
            index += 1
            continue
        if current is None:
            raise PatchSyntaxError("Patch content must be inside [operation] blocks")
        if "<<" in stripped:
            key, marker = stripped.split("<<", 1)
            value_lines: list[str] = []
            end_marker = marker.strip()
            index += 1
            while index < len(lines) and lines[index].strip() != end_marker:
                value_lines.append(lines[index])
                index += 1
            if index >= len(lines):
                raise PatchSyntaxError(f"Unterminated heredoc for key: {key.strip()}")
            current[key.strip()] = "\n".join(value_lines)
            index += 1
            continue
        if "=" not in stripped:
            raise PatchSyntaxError(f"Invalid patch line: {line}")
        key, value = stripped.split("=", 1)
        current[key.strip()] = value.strip()
        index += 1

    if current is not None:
        blocks.append(current)
    return blocks


def _parse_payload(operation_type: str, block: dict[str, str]) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for key, raw_value in block.items():
        if key == "type" or key.startswith("target."):
            continue
        if key in _INT_KEYS:
            payload[key] = _coerce_int(raw_value, key)
            continue
        if key in _BOOL_KEYS:
            payload[key] = _coerce_bool(raw_value, key)
            continue
        if key in {"data", "items"}:
            payload[key] = _coerce_json(raw_value, key)
            continue
        payload[key] = raw_value

    if operation_type == "format_text":
        payload = {"formatting": _build_formatting(payload)}
    elif operation_type in {"insert_list", "replace_list"}:
        payload = {
            "ordered": payload.get("list.ordered"),
            "items": _build_list_items(payload.get("items")),
        }
    else:
        payload.pop("list.ordered", None)
    return payload


def _validate_operation_shape(
    operation_type: str,
    target: WriterTarget | None,
    payload: dict[str, Any],
) -> None:
    has_target = target is not None
    if operation_type == "insert_text":
        _require_payload_keys(operation_type, payload, {"text"})
        return
    if operation_type == "replace_text":
        _require_target(operation_type, has_target)
        _require_payload_keys(operation_type, payload, {"new_text"})
        return
    if operation_type == "delete_text":
        _require_target(operation_type, has_target)
        return
    if operation_type == "format_text":
        _require_target(operation_type, has_target)
        _require_payload_keys(operation_type, payload, {"formatting"})
        return
    if operation_type == "insert_table":
        _require_payload_keys(operation_type, payload, {"rows", "cols"})
        return
    if operation_type == "update_table":
        _require_target(operation_type, has_target)
        _require_payload_keys(operation_type, payload, {"data"})
        return
    if operation_type == "delete_table":
        _require_target(operation_type, has_target)
        return
    if operation_type == "insert_image":
        _require_payload_keys(operation_type, payload, {"image_path"})
        return
    if operation_type == "update_image":
        _require_target(operation_type, has_target)
        if not any(key in payload for key in {"image_path", "width", "height"}):
            raise PatchSyntaxError(
                "Operation update_image is missing required keys: image_path, width, or height"
            )
        return
    if operation_type == "delete_image":
        _require_target(operation_type, has_target)
        return
    if operation_type == "insert_list":
        _require_payload_keys(operation_type, payload, {"ordered", "items"})
        return
    if operation_type == "replace_list":
        _require_target(operation_type, has_target)
        _require_payload_keys(operation_type, payload, {"items"})
        return
    if operation_type == "delete_list":
        _require_target(operation_type, has_target)
        return


def _dispatch_operation(session, operation: PatchOperation) -> None:
    if operation.operation_type == "insert_text":
        session.insert_text(operation.payload["text"], operation.target)
        return
    if operation.operation_type == "replace_text":
        session.replace_text(operation.target, operation.payload["new_text"])
        return
    if operation.operation_type == "delete_text":
        session.delete_text(operation.target)
        return
    if operation.operation_type == "format_text":
        session.format_text(operation.target, operation.payload["formatting"])
        return
    if operation.operation_type == "insert_table":
        session.insert_table(
            operation.payload["rows"],
            operation.payload["cols"],
            operation.payload.get("data"),
            operation.payload.get("name"),
            operation.target,
        )
        return
    if operation.operation_type == "update_table":
        session.update_table(operation.target, operation.payload["data"])
        return
    if operation.operation_type == "delete_table":
        session.delete_table(operation.target)
        return
    if operation.operation_type == "insert_image":
        session.insert_image(
            operation.payload["image_path"],
            operation.payload.get("width"),
            operation.payload.get("height"),
            operation.payload.get("name"),
            operation.target,
        )
        return
    if operation.operation_type == "update_image":
        session.update_image(
            operation.target,
            image_path=operation.payload.get("image_path"),
            width=operation.payload.get("width"),
            height=operation.payload.get("height"),
        )
        return
    if operation.operation_type == "delete_image":
        session.delete_image(operation.target)
        return
    if operation.operation_type == "insert_list":
        session.insert_list(
            operation.payload["items"],
            ordered=operation.payload["ordered"],
            target=operation.target,
        )
        return
    if operation.operation_type == "replace_list":
        session.replace_list(
            operation.target,
            operation.payload["items"],
            ordered=operation.payload.get("ordered"),
        )
        return
    if operation.operation_type == "delete_list":
        session.delete_list(operation.target)
        return
    raise PatchSyntaxError(f"Unsupported operation type: {operation.operation_type}")


def _build_formatting(payload: dict[str, Any]) -> TextFormatting:
    return TextFormatting(
        bold=payload.get("format.bold"),
        italic=payload.get("format.italic"),
        underline=payload.get("format.underline"),
        font_name=payload.get("format.font_name"),
        font_size=payload.get("format.font_size"),
        color=payload.get("format.color"),
        align=payload.get("format.align"),
        line_spacing=payload.get("format.line_spacing"),
        spacing_before=payload.get("format.spacing_before"),
        spacing_after=payload.get("format.spacing_after"),
    )


def _build_list_items(value: Any) -> list[ListItem]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise PatchSyntaxError("items must be a JSON array")
    items: list[ListItem] = []
    for entry in value:
        if not isinstance(entry, dict) or "text" not in entry:
            raise PatchSyntaxError("Each list item must be an object with text")
        level = entry.get("level", 0)
        try:
            level_int = int(level)
        except (TypeError, ValueError) as exc:
            raise PatchSyntaxError("List item level must be an integer") from exc
        items.append(ListItem(text=str(entry["text"]), level=level_int))
    return items


def _coerce_target_value(field: str, value: str) -> Any:
    if field in _TARGET_INT_KEYS:
        try:
            return int(value)
        except ValueError as exc:
            raise PatchSyntaxError(f"target.{field} must be an integer") from exc
    return value


def _coerce_int(value: str, key: str) -> int:
    try:
        return int(value)
    except ValueError as exc:
        raise PatchSyntaxError(f"{key} must be an integer") from exc


def _coerce_bool(value: str, key: str) -> bool:
    lowered = value.strip().lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    raise PatchSyntaxError(f"{key} must be true or false")


def _coerce_json(value: str, key: str) -> Any:
    try:
        return json.loads(value)
    except json.JSONDecodeError as exc:
        raise PatchSyntaxError(f"{key} must be valid JSON") from exc


def _require_target(operation_type: str, has_target: bool) -> None:
    if not has_target:
        raise PatchSyntaxError(f"Operation {operation_type} requires target.* fields")


def _require_payload_keys(
    operation_type: str,
    payload: dict[str, Any],
    keys: set[str],
) -> None:
    missing = [
        key for key in sorted(keys) if key not in payload or payload[key] is None
    ]
    if missing:
        raise PatchSyntaxError(
            f"Operation {operation_type} is missing required keys: {', '.join(missing)}"
        )
