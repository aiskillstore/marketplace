"""Patch parsing and application for Calc spreadsheets."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Literal

from calc.exceptions import PatchSyntaxError
from calc.targets import (
    CalcTarget,
    CellFormatting,
    ChartSpec,
    ValidationRule,
    parse_target,
)

PatchApplyMode = Literal["atomic", "best_effort"]

_OPERATION_TYPES = {
    "write_cell",
    "write_range",
    "format_range",
    "add_sheet",
    "rename_sheet",
    "delete_sheet",
    "define_named_range",
    "delete_named_range",
    "set_validation",
    "clear_validation",
    "create_chart",
    "update_chart",
    "delete_chart",
    "recalculate",
}
_TARGET_INT_KEYS = {"sheet_index", "row", "col", "end_row", "end_col", "index"}
_FORMAT_BOOL_KEYS = {"format.bold", "format.italic"}
_RULE_BOOL_KEYS = {"rule.show_error", "rule.show_input", "rule.ignore_blank"}
_RULE_INT_KEYS = {"rule.error_style"}
_CHART_INT_KEYS = {
    "chart.anchor_row",
    "chart.anchor_col",
    "chart.width",
    "chart.height",
}
_CHART_RANGE_INT_KEYS = {"row", "col", "end_row", "end_col", "sheet_index", "index"}


@dataclass(frozen=True)
class PatchOperation:
    """Parsed Calc patch operation."""

    operation_type: str
    target: CalcTarget | None
    payload: dict[str, Any]


@dataclass
class PatchOperationResult:
    """Result for one patch operation."""

    operation_type: str
    target: CalcTarget | None
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
    """Parse Calc patch text into ordered operations."""
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
    """Apply patch operations to an already-open Calc session."""
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
    from calc.session import open_calc_session

    session = open_calc_session(path)
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
    if operation.operation_type == "write_cell":
        session.write_cell(
            operation.target,
            operation.payload["value"],
            value_type=operation.payload.get("value_type", "auto"),
        )
        return
    if operation.operation_type == "write_range":
        session.write_range(operation.target, operation.payload["data"])
        return
    if operation.operation_type == "format_range":
        session.format_range(operation.target, operation.payload["formatting"])
        return
    if operation.operation_type == "add_sheet":
        session.add_sheet(
            operation.payload["name"], index=operation.payload.get("index")
        )
        return
    if operation.operation_type == "rename_sheet":
        session.rename_sheet(operation.target, operation.payload["new_name"])
        return
    if operation.operation_type == "delete_sheet":
        session.delete_sheet(operation.target)
        return
    if operation.operation_type == "define_named_range":
        session.define_named_range(operation.payload["name"], operation.target)
        return
    if operation.operation_type == "delete_named_range":
        session.delete_named_range(operation.target)
        return
    if operation.operation_type == "set_validation":
        session.set_validation(operation.target, operation.payload["rule"])
        return
    if operation.operation_type == "clear_validation":
        session.clear_validation(operation.target)
        return
    if operation.operation_type == "create_chart":
        session.create_chart(operation.target, operation.payload["spec"])
        return
    if operation.operation_type == "update_chart":
        session.update_chart(operation.target, operation.payload["spec"])
        return
    if operation.operation_type == "delete_chart":
        session.delete_chart(operation.target)
        return
    if operation.operation_type == "recalculate":
        session.recalculate()
        return
    raise PatchSyntaxError(f"Unsupported operation type: {operation.operation_type}")


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
        if key == "data":
            payload[key] = _coerce_json(raw_value, key)
            continue
        if key == "index":
            payload[key] = _coerce_int(raw_value, key)
            continue
        if key.startswith("format."):
            payload[key] = _coerce_format_value(key, raw_value)
            continue
        if key.startswith("rule."):
            payload[key] = _coerce_rule_value(key, raw_value)
            continue
        if key.startswith("chart."):
            payload[key] = _coerce_chart_value(key, raw_value)
            continue
        if key == "value":
            payload[key] = _coerce_scalar(raw_value)
            continue
        payload[key] = raw_value

    if operation_type == "format_range":
        payload = {"formatting": _build_formatting(payload)}
    elif operation_type == "set_validation":
        payload = {"rule": _build_validation_rule(payload)}
    elif operation_type in {"create_chart", "update_chart"}:
        payload = {"spec": _build_chart_spec(payload)}
    return payload


def _validate_operation_shape(
    operation_type: str,
    target: CalcTarget | None,
    payload: dict[str, Any],
) -> None:
    has_target = target is not None
    if operation_type == "write_cell":
        _require_target(operation_type, has_target)
        _require_payload_keys(operation_type, payload, {"value"})
        return
    if operation_type == "write_range":
        _require_target(operation_type, has_target)
        _require_payload_keys(operation_type, payload, {"data"})
        return
    if operation_type == "format_range":
        _require_target(operation_type, has_target)
        _require_payload_keys(operation_type, payload, {"formatting"})
        return
    if operation_type == "add_sheet":
        _require_payload_keys(operation_type, payload, {"name"})
        return
    if operation_type == "rename_sheet":
        _require_target(operation_type, has_target)
        _require_payload_keys(operation_type, payload, {"new_name"})
        return
    if operation_type in {
        "delete_sheet",
        "delete_named_range",
        "clear_validation",
        "delete_chart",
    }:
        _require_target(operation_type, has_target)
        return
    if operation_type == "define_named_range":
        _require_target(operation_type, has_target)
        _require_payload_keys(operation_type, payload, {"name"})
        return
    if operation_type == "set_validation":
        _require_target(operation_type, has_target)
        _require_payload_keys(operation_type, payload, {"rule"})
        return
    if operation_type in {"create_chart", "update_chart"}:
        _require_target(operation_type, has_target)
        _require_payload_keys(operation_type, payload, {"spec"})
        return


def _build_formatting(payload: dict[str, Any]) -> CellFormatting:
    return CellFormatting(
        bold=payload.get("format.bold"),
        italic=payload.get("format.italic"),
        font_name=payload.get("format.font_name"),
        font_size=payload.get("format.font_size"),
        color=payload.get("format.color"),
        number_format=payload.get("format.number_format"),
    )


def _build_validation_rule(payload: dict[str, Any]) -> ValidationRule:
    rule_type = payload.get("rule.type")
    condition = payload.get("rule.condition")
    if rule_type is None or condition is None:
        missing = []
        if rule_type is None:
            missing.append("rule.type")
        if condition is None:
            missing.append("rule.condition")
        raise PatchSyntaxError(
            f"Operation set_validation is missing required keys: {', '.join(missing)}"
        )
    return ValidationRule(
        type=str(rule_type),
        condition=str(condition),
        value1=payload.get("rule.value1"),
        value2=payload.get("rule.value2"),
        show_error=payload.get("rule.show_error", False),
        error_message=str(payload.get("rule.error_message", "")),
        show_input=payload.get("rule.show_input", False),
        input_title=str(payload.get("rule.input_title", "")),
        input_message=str(payload.get("rule.input_message", "")),
        ignore_blank=payload.get("rule.ignore_blank", True),
        error_style=payload.get("rule.error_style", 0),
    )


def _build_chart_spec(payload: dict[str, Any]) -> ChartSpec:
    data_range_fields = {
        key.split(".", 2)[2]: value
        for key, value in payload.items()
        if key.startswith("chart.data_range.")
    }
    if not data_range_fields:
        raise PatchSyntaxError("Chart operations require chart.data_range.* fields")

    return ChartSpec(
        chart_type=str(payload.get("chart.chart_type", "")),
        data_range=parse_target(data_range_fields),
        anchor_row=_require_int_payload(payload, "chart.anchor_row"),
        anchor_col=_require_int_payload(payload, "chart.anchor_col"),
        width=_require_int_payload(payload, "chart.width"),
        height=_require_int_payload(payload, "chart.height"),
        title=_optional_string(payload.get("chart.title")),
    )


def _coerce_target_value(field: str, value: str) -> Any:
    if field in _TARGET_INT_KEYS:
        return _coerce_int(value, f"target.{field}")
    return value


def _coerce_format_value(key: str, value: str) -> Any:
    if key in _FORMAT_BOOL_KEYS:
        return _coerce_bool(value, key)
    if key == "format.font_size":
        return _coerce_float(value, key)
    return value


def _coerce_rule_value(key: str, value: str) -> Any:
    if key in _RULE_BOOL_KEYS:
        return _coerce_bool(value, key)
    if key in _RULE_INT_KEYS:
        return _coerce_int(value, key)
    return _coerce_scalar(value)


def _coerce_chart_value(key: str, value: str) -> Any:
    if key in _CHART_INT_KEYS:
        return _coerce_int(value, key)
    if key.startswith("chart.data_range."):
        field = key.split(".", 2)[2]
        if field in _CHART_RANGE_INT_KEYS:
            return _coerce_int(value, key)
    return value


def _coerce_scalar(value: str) -> Any:
    lowered = value.strip().lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
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


def _require_int_payload(payload: dict[str, Any], key: str) -> int:
    value = payload.get(key)
    if not isinstance(value, int):
        raise PatchSyntaxError(f"{key} must be an integer")
    return value


def _optional_string(value: Any) -> str | None:
    if value is None:
        return None
    cleaned = str(value).strip()
    return cleaned or None
