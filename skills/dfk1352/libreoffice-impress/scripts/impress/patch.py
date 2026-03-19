"""Patch parsing and application for Impress presentations."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Literal

from impress.exceptions import PatchSyntaxError
from impress.targets import (
    ImpressTarget,
    ListItem,
    ShapePlacement,
    TextFormatting,
    parse_target,
)

PatchApplyMode = Literal["atomic", "best_effort"]

_OPERATION_TYPES = {
    "add_slide",
    "delete_slide",
    "move_slide",
    "duplicate_slide",
    "insert_text",
    "replace_text",
    "format_text",
    "insert_list",
    "replace_list",
    "insert_text_box",
    "insert_shape",
    "delete_item",
    "insert_image",
    "replace_image",
    "insert_table",
    "update_table",
    "insert_chart",
    "update_chart",
    "insert_media",
    "replace_media",
    "set_notes",
    "apply_master_page",
    "set_master_background",
}
_TARGET_INT_KEYS = {"slide_index", "shape_index", "occurrence"}
_INT_KEYS = {"index", "to_index", "rows", "cols"}
_BOOL_KEYS = {
    "list.ordered",
    "format.bold",
    "format.italic",
    "format.underline",
}
_FLOAT_KEYS = {
    "placement.x_cm",
    "placement.y_cm",
    "placement.width_cm",
    "placement.height_cm",
    "format.font_size",
}


@dataclass(frozen=True)
class PatchOperation:
    """Parsed Impress patch operation."""

    operation_type: str
    target: ImpressTarget | None
    payload: dict[str, Any]


@dataclass
class PatchOperationResult:
    """Result for one patch operation."""

    operation_type: str
    target: ImpressTarget | None
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
    """Parse Impress patch text into ordered operations."""
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
    """Apply patch operations to an already-open Impress session."""
    operations = parse_patch(patch_text)
    results: list[PatchOperationResult] = []
    atomic_snapshot = session._path.read_bytes() if mode == "atomic" else None

    if mode not in {"atomic", "best_effort"}:
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
                assert atomic_snapshot is not None
                session.restore_snapshot(atomic_snapshot)
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
    from impress.session import open_impress_session

    session = open_impress_session(path)
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


def _dispatch_operation(session, operation: PatchOperation) -> None:
    op = operation.operation_type
    if op == "add_slide":
        session.add_slide(
            index=operation.payload.get("index"),
            layout=operation.payload.get("layout", "BLANK"),
        )
        return
    if op == "delete_slide":
        session.delete_slide(operation.target)
        return
    if op == "move_slide":
        session.move_slide(operation.target, operation.payload["to_index"])
        return
    if op == "duplicate_slide":
        session.duplicate_slide(operation.target)
        return
    if op == "insert_text":
        session.insert_text(operation.payload["text"], operation.target)
        return
    if op == "replace_text":
        session.replace_text(operation.target, operation.payload["new_text"])
        return
    if op == "format_text":
        session.format_text(operation.target, operation.payload["formatting"])
        return
    if op == "insert_list":
        session.insert_list(
            operation.payload["items"],
            ordered=operation.payload["ordered"],
            target=operation.target,
        )
        return
    if op == "replace_list":
        session.replace_list(
            operation.target,
            operation.payload["items"],
            ordered=operation.payload.get("ordered"),
        )
        return
    if op == "insert_text_box":
        session.insert_text_box(
            operation.target,
            operation.payload["text"],
            operation.payload["placement"],
            name=operation.payload.get("name"),
        )
        return
    if op == "insert_shape":
        session.insert_shape(
            operation.target,
            operation.payload["shape_type"],
            operation.payload["placement"],
            fill_color=operation.payload.get("fill_color"),
            line_color=operation.payload.get("line_color"),
            name=operation.payload.get("name"),
        )
        return
    if op == "delete_item":
        session.delete_item(operation.target)
        return
    if op == "insert_image":
        session.insert_image(
            operation.target,
            operation.payload["image_path"],
            operation.payload["placement"],
            name=operation.payload.get("name"),
        )
        return
    if op == "replace_image":
        session.replace_image(
            operation.target,
            image_path=operation.payload.get("image_path"),
            placement=operation.payload.get("placement"),
        )
        return
    if op == "insert_table":
        session.insert_table(
            operation.target,
            operation.payload["rows"],
            operation.payload["cols"],
            operation.payload["placement"],
            data=operation.payload.get("data"),
            name=operation.payload.get("name"),
        )
        return
    if op == "update_table":
        session.update_table(operation.target, operation.payload["data"])
        return
    if op == "insert_chart":
        session.insert_chart(
            operation.target,
            operation.payload["chart_type"],
            operation.payload["data"],
            operation.payload["placement"],
            title=operation.payload.get("title"),
            name=operation.payload.get("name"),
        )
        return
    if op == "update_chart":
        session.update_chart(
            operation.target,
            chart_type=operation.payload.get("chart_type"),
            data=operation.payload.get("data"),
            placement=operation.payload.get("placement"),
            title=operation.payload.get("title"),
        )
        return
    if op == "insert_media":
        session.insert_media(
            operation.target,
            operation.payload["media_path"],
            operation.payload["placement"],
            name=operation.payload.get("name"),
        )
        return
    if op == "replace_media":
        session.replace_media(
            operation.target,
            media_path=operation.payload.get("media_path"),
            placement=operation.payload.get("placement"),
        )
        return
    if op == "set_notes":
        session.set_notes(operation.target, operation.payload["text"])
        return
    if op == "apply_master_page":
        session.apply_master_page(operation.target, operation.payload["master_target"])
        return
    if op == "set_master_background":
        session.set_master_background(operation.target, operation.payload["color"])
        return
    raise PatchSyntaxError(f"Unsupported operation type: {op}")


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
            end_marker = marker.strip()
            value_lines: list[str] = []
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
        if key in _FLOAT_KEYS:
            payload[key] = _coerce_float(raw_value, key)
            continue
        if key in {"items", "data"}:
            payload[key] = _coerce_json(raw_value, key)
            continue
        payload[key] = raw_value

    if any(key.startswith("format.") for key in payload):
        payload["formatting"] = TextFormatting(
            bold=payload.get("format.bold"),
            italic=payload.get("format.italic"),
            underline=payload.get("format.underline"),
            font_name=payload.get("format.font_name"),
            font_size=payload.get("format.font_size"),
            color=payload.get("format.color"),
            align=payload.get("format.align"),
        )
    if any(key.startswith("placement.") for key in payload):
        payload["placement"] = ShapePlacement(
            x_cm=_require_float_payload(payload, "placement.x_cm"),
            y_cm=_require_float_payload(payload, "placement.y_cm"),
            width_cm=_require_float_payload(payload, "placement.width_cm"),
            height_cm=_require_float_payload(payload, "placement.height_cm"),
        )
    if operation_type in {"insert_list", "replace_list"}:
        payload["items"] = _build_list_items(payload.get("items"))
        if operation_type == "insert_list":
            payload["ordered"] = payload.get("list.ordered")
        else:
            payload["ordered"] = payload.get("list.ordered")
    if any(key.startswith("master.") for key in block):
        master_fields = {
            key.split(".", 1)[1]: _coerce_target_value(key.split(".", 1)[1], value)
            for key, value in block.items()
            if key.startswith("master.")
        }
        payload["master_target"] = parse_target(master_fields)
    return payload


def _validate_operation_shape(
    operation_type: str,
    target: ImpressTarget | None,
    payload: dict[str, Any],
) -> None:
    has_target = target is not None
    if operation_type == "add_slide":
        return
    if operation_type in {
        "delete_slide",
        "duplicate_slide",
        "delete_item",
    }:
        _require_target(operation_type, has_target)
        return
    if operation_type == "move_slide":
        _require_target(operation_type, has_target)
        _require_payload_keys(operation_type, payload, {"to_index"})
        return
    if operation_type == "insert_text":
        _require_payload_keys(operation_type, payload, {"text"})
        return
    if operation_type == "replace_text":
        _require_target(operation_type, has_target)
        _require_payload_keys(operation_type, payload, {"new_text"})
        return
    if operation_type == "format_text":
        _require_target(operation_type, has_target)
        _require_payload_keys(operation_type, payload, {"formatting"})
        return
    if operation_type == "insert_list":
        _require_payload_keys(operation_type, payload, {"ordered", "items"})
        return
    if operation_type == "replace_list":
        _require_target(operation_type, has_target)
        _require_payload_keys(operation_type, payload, {"items"})
        return
    if operation_type == "insert_text_box":
        _require_target(operation_type, has_target)
        _require_payload_keys(operation_type, payload, {"text", "placement"})
        return
    if operation_type == "insert_shape":
        _require_target(operation_type, has_target)
        _require_payload_keys(operation_type, payload, {"shape_type", "placement"})
        return
    if operation_type == "insert_image":
        _require_target(operation_type, has_target)
        _require_payload_keys(operation_type, payload, {"image_path", "placement"})
        return
    if operation_type == "replace_image":
        _require_target(operation_type, has_target)
        if "image_path" not in payload and "placement" not in payload:
            raise PatchSyntaxError(
                "Operation replace_image is missing required keys: image_path or placement"
            )
        return
    if operation_type == "insert_table":
        _require_target(operation_type, has_target)
        _require_payload_keys(operation_type, payload, {"rows", "cols", "placement"})
        return
    if operation_type == "update_table":
        _require_target(operation_type, has_target)
        _require_payload_keys(operation_type, payload, {"data"})
        return
    if operation_type == "insert_chart":
        _require_target(operation_type, has_target)
        _require_payload_keys(
            operation_type, payload, {"chart_type", "data", "placement"}
        )
        return
    if operation_type == "update_chart":
        _require_target(operation_type, has_target)
        if not any(
            key in payload for key in {"chart_type", "data", "placement", "title"}
        ):
            raise PatchSyntaxError(
                "Operation update_chart is missing required keys: chart_type, data, placement, or title"
            )
        return
    if operation_type == "insert_media":
        _require_target(operation_type, has_target)
        _require_payload_keys(operation_type, payload, {"media_path", "placement"})
        return
    if operation_type == "replace_media":
        _require_target(operation_type, has_target)
        if "media_path" not in payload and "placement" not in payload:
            raise PatchSyntaxError(
                "Operation replace_media is missing required keys: media_path or placement"
            )
        return
    if operation_type == "set_notes":
        _require_target(operation_type, has_target)
        _require_payload_keys(operation_type, payload, {"text"})
        return
    if operation_type == "apply_master_page":
        _require_target(operation_type, has_target)
        _require_payload_keys(operation_type, payload, {"master_target"})
        return
    if operation_type == "set_master_background":
        _require_target(operation_type, has_target)
        _require_payload_keys(operation_type, payload, {"color"})
        return


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
            level_value = int(level)
        except (TypeError, ValueError) as exc:
            raise PatchSyntaxError("List item level must be an integer") from exc
        items.append(ListItem(text=str(entry["text"]), level=level_value))
    return items


def _coerce_target_value(field: str, value: str) -> Any:
    if field in _TARGET_INT_KEYS:
        return _coerce_int(value, f"target.{field}")
    return value


def _coerce_int(value: str, key: str) -> int:
    try:
        return int(value)
    except ValueError as exc:
        raise PatchSyntaxError(f"{key} must be an integer") from exc


def _coerce_float(value: str, key: str) -> float:
    try:
        return float(value)
    except ValueError as exc:
        raise PatchSyntaxError(f"{key} must be a number") from exc


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
    operation_type: str, payload: dict[str, Any], keys: set[str]
) -> None:
    missing = [
        key for key in sorted(keys) if key not in payload or payload[key] is None
    ]
    if missing:
        raise PatchSyntaxError(
            f"Operation {operation_type} is missing required keys: {', '.join(missing)}"
        )


def _require_float_payload(payload: dict[str, Any], key: str) -> float:
    value = payload.get(key)
    if not isinstance(value, (int, float)):
        raise PatchSyntaxError(f"{key} must be a number")
    return float(value)
