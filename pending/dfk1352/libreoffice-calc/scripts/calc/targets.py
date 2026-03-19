"""Structured target parsing and resolution for Calc spreadsheets."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from colors import resolve_color
from calc.exceptions import (
    ChartNotFoundError,
    InvalidFormattingError,
    InvalidTargetError,
    InvalidValidationError,
    NamedRangeNotFoundError,
    InvalidPayloadError,
    TargetNoMatchError,
)

CHART_TYPES = {
    "bar": "com.sun.star.chart.BarDiagram",
    "line": "com.sun.star.chart.LineDiagram",
    "pie": "com.sun.star.chart.PieDiagram",
    "scatter": "com.sun.star.chart.XYDiagram",
}

NUMBER_FORMATS = {"currency", "percentage", "date", "time"}

VALIDATION_TYPES: dict[str, str] = {
    "any": "ANY",
    "whole": "WHOLE",
    "decimal": "DECIMAL",
    "date": "DATE",
    "time": "TIME",
    "text_length": "TEXT_LEN",
    "list": "LIST",
}

CONDITION_OPERATORS: dict[str, str] = {
    "between": "BETWEEN",
    "not_between": "NOT_BETWEEN",
    "equal": "EQUAL",
    "not_equal": "NOT_EQUAL",
    "greater_than": "GREATER",
    "less_than": "LESS",
    "greater_or_equal": "GREATER_EQUAL",
    "less_or_equal": "LESS_EQUAL",
}


@dataclass(frozen=True)
class CalcTarget:
    """Canonical target description for Calc operations."""

    kind: str
    sheet: str | None = None
    sheet_index: int | None = None
    row: int | None = None
    col: int | None = None
    end_row: int | None = None
    end_col: int | None = None
    name: str | None = None
    index: int | None = None


@dataclass(frozen=True)
class CellFormatting:
    """Formatting payload for a cell or rectangular range."""

    bold: bool | None = None
    italic: bool | None = None
    font_name: str | None = None
    font_size: float | None = None
    color: str | int | None = None
    number_format: str | None = None


@dataclass(frozen=True)
class ValidationRule:
    """Structured validation payload for Calc ranges."""

    type: str
    condition: str
    value1: object | None = None
    value2: object | None = None
    show_error: bool = False
    error_message: str = ""
    show_input: bool = False
    input_title: str = ""
    input_message: str = ""
    ignore_blank: bool = True
    error_style: int = 0


@dataclass(frozen=True)
class ChartSpec:
    """Structured chart payload for Calc chart operations."""

    chart_type: str
    data_range: CalcTarget
    anchor_row: int
    anchor_col: int
    width: int
    height: int
    title: str | None = None


def parse_target(raw: dict[str, Any]) -> CalcTarget:
    """Convert raw target fields into a validated CalcTarget."""
    kind = str(raw.get("kind", "")).strip().lower()
    if not kind:
        raise InvalidTargetError("target.kind is required")

    target = CalcTarget(
        kind=kind,
        sheet=_clean_optional_string(raw.get("sheet")),
        sheet_index=_coerce_optional_int(raw.get("sheet_index"), "target.sheet_index"),
        row=_coerce_optional_int(raw.get("row"), "target.row"),
        col=_coerce_optional_int(raw.get("col"), "target.col"),
        end_row=_coerce_optional_int(raw.get("end_row"), "target.end_row"),
        end_col=_coerce_optional_int(raw.get("end_col"), "target.end_col"),
        name=_clean_optional_string(raw.get("name")),
        index=_coerce_optional_int(raw.get("index"), "target.index"),
    )
    _validate_target(target)
    return target


def resolve_sheet_target(target: CalcTarget, doc: Any) -> Any:
    """Resolve one sheet by name or zero-based index."""
    _ensure_kind(target, {"sheet", "cell", "range", "chart"})
    _require_sheet_selector(target)

    sheets = doc.Sheets
    if target.sheet is not None:
        if not sheets.hasByName(target.sheet):
            raise TargetNoMatchError(f'Sheet not found: "{target.sheet}"')
        return sheets.getByName(target.sheet)

    assert target.sheet_index is not None
    if target.sheet_index < 0 or target.sheet_index >= sheets.getCount():
        raise TargetNoMatchError(f"Sheet index out of range: {target.sheet_index}")
    return sheets.getByIndex(target.sheet_index)


def resolve_cell_target(target: CalcTarget, doc: Any) -> Any:
    """Resolve one cell object."""
    _ensure_kind(target, {"cell"})
    _validate_target(target)

    sheet = resolve_sheet_target(target, doc)
    assert target.row is not None
    assert target.col is not None
    return sheet.getCellByPosition(target.col, target.row)


def resolve_range_target(target: CalcTarget, doc: Any) -> Any:
    """Resolve one rectangular cell range."""
    _ensure_kind(target, {"range"})
    _validate_target(target)

    sheet = resolve_sheet_target(target, doc)
    assert target.row is not None
    assert target.col is not None
    assert target.end_row is not None
    assert target.end_col is not None
    return sheet.getCellRangeByPosition(
        target.col,
        target.row,
        target.end_col,
        target.end_row,
    )


def resolve_named_range_target(target: CalcTarget, doc: Any) -> Any:
    """Resolve one named range object by name."""
    _ensure_kind(target, {"named_range"})
    _validate_target(target)

    assert target.name is not None
    if not doc.NamedRanges.hasByName(target.name):
        raise NamedRangeNotFoundError(f'Named range not found: "{target.name}"')
    return doc.NamedRanges.getByName(target.name)


def resolve_chart_target(target: CalcTarget, doc: Any) -> Any:
    """Resolve one chart on one sheet by name or zero-based index."""
    _ensure_kind(target, {"chart"})
    _validate_target(target)

    sheet = resolve_sheet_target(target, doc)
    charts = sheet.Charts
    if target.name is not None:
        if not charts.hasByName(target.name):
            raise ChartNotFoundError(f'Chart not found: "{target.name}"')
        return charts.getByName(target.name)

    assert target.index is not None
    if target.index < 0 or target.index >= charts.getCount():
        raise ChartNotFoundError(f"Chart index out of range: {target.index}")
    return charts.getByIndex(target.index)


def validate_formatting(formatting: CellFormatting) -> None:
    """Ensure a Calc formatting payload is well-formed."""
    if not any(value is not None for value in formatting.__dict__.values()):
        raise InvalidFormattingError("At least one formatting field is required")
    if formatting.color is not None:
        try:
            resolve_color(formatting.color)
        except (TypeError, ValueError) as exc:
            raise InvalidFormattingError(str(exc)) from exc
    if formatting.number_format is not None:
        if formatting.number_format not in NUMBER_FORMATS:
            raise InvalidFormattingError(
                f"Unsupported number format: {formatting.number_format}"
            )


def validate_validation_rule(rule: ValidationRule) -> None:
    """Ensure a validation rule is coherent and supported."""
    if rule.type.strip().lower() not in VALIDATION_TYPES:
        raise InvalidValidationError(f"Unsupported validation type: {rule.type}")
    if rule.condition.strip().lower() not in CONDITION_OPERATORS:
        raise InvalidValidationError(
            f"Unsupported validation condition: {rule.condition}"
        )
    if isinstance(rule.error_style, bool):
        raise InvalidValidationError("error_style must be an integer")


def validate_chart_spec(spec: ChartSpec) -> None:
    """Ensure chart payload values are valid for Calc chart operations."""
    if spec.chart_type not in CHART_TYPES:
        raise InvalidPayloadError(f"Unsupported chart type: {spec.chart_type}")
    if spec.data_range.kind != "range":
        raise InvalidPayloadError("Chart data_range must be a range target")
    if spec.anchor_row < 0 or spec.anchor_col < 0:
        raise InvalidPayloadError("Chart anchor coordinates must be non-negative")
    if spec.width <= 0 or spec.height <= 0:
        raise InvalidPayloadError("Chart width and height must be positive")
    _validate_target(spec.data_range)


def normalize_validation_type(value: object, uno_module: Any) -> object:
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        key = value.strip().lower()
        if key in VALIDATION_TYPES:
            return uno_module.Enum(
                "com.sun.star.sheet.ValidationType",
                VALIDATION_TYPES[key],
            )
    raise InvalidValidationError(f"Unsupported validation type: {value}")


def normalize_validation_condition(value: object, uno_module: Any) -> object:
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        key = value.strip().lower()
        if key in CONDITION_OPERATORS:
            return uno_module.Enum(
                "com.sun.star.sheet.ConditionOperator",
                CONDITION_OPERATORS[key],
            )
    raise InvalidValidationError(f"Unsupported validation condition: {value}")


def format_validation_formula(value: object) -> str:
    if value is None:
        return ""
    return str(value)


def _validate_target(target: CalcTarget) -> None:
    if target.sheet is not None and target.sheet_index is not None:
        raise InvalidTargetError(
            "target.sheet and target.sheet_index are mutually exclusive"
        )
    if target.name is not None and target.index is not None:
        raise InvalidTargetError("target.name and target.index are mutually exclusive")

    for field_name in ("row", "col", "end_row", "end_col"):
        value = getattr(target, field_name)
        if value is not None and value < 0:
            raise InvalidTargetError(f"target.{field_name} must be >= 0")

    if target.kind == "cell":
        _require_sheet_selector(target)
        if target.row is None or target.col is None:
            raise InvalidTargetError("Cell targets require row and col")
        if any(
            value is not None
            for value in (target.end_row, target.end_col, target.name, target.index)
        ):
            raise InvalidTargetError("Cell targets only support row, col, and sheet")
        return

    if target.kind == "range":
        _require_sheet_selector(target)
        if None in (target.row, target.col, target.end_row, target.end_col):
            raise InvalidTargetError(
                "Range targets require row, col, end_row, and end_col"
            )
        assert target.row is not None
        assert target.col is not None
        assert target.end_row is not None
        assert target.end_col is not None
        if target.end_row < target.row or target.end_col < target.col:
            raise InvalidTargetError("Range targets require end coordinates >= start")
        if target.name is not None or target.index is not None:
            raise InvalidTargetError("Range targets do not support name or index")
        return

    if target.kind == "sheet":
        _require_sheet_selector(target)
        if any(
            value is not None
            for value in (
                target.row,
                target.col,
                target.end_row,
                target.end_col,
                target.name,
                target.index,
            )
        ):
            raise InvalidTargetError("Sheet targets only support sheet or sheet_index")
        return

    if target.kind == "named_range":
        if target.name is None:
            raise InvalidTargetError("Named-range targets require name")
        if any(
            value is not None
            for value in (
                target.sheet,
                target.sheet_index,
                target.row,
                target.col,
                target.end_row,
                target.end_col,
                target.index,
            )
        ):
            raise InvalidTargetError("Named-range targets only support name")
        return

    if target.kind == "chart":
        _require_sheet_selector(target)
        if target.name is None and target.index is None:
            raise InvalidTargetError("Chart targets require name or index")
        if any(
            value is not None
            for value in (target.row, target.col, target.end_row, target.end_col)
        ):
            raise InvalidTargetError("Chart targets do not support coordinate fields")
        return

    raise InvalidTargetError(f"Unsupported target kind: {target.kind}")


def _ensure_kind(target: CalcTarget, allowed: set[str]) -> None:
    if target.kind not in allowed:
        raise InvalidTargetError(
            f"Target kind '{target.kind}' is not valid here; expected {sorted(allowed)}"
        )


def _require_sheet_selector(target: CalcTarget) -> None:
    if target.sheet is None and target.sheet_index is None:
        raise InvalidTargetError("Target requires sheet or sheet_index")


def _clean_optional_string(value: Any) -> str | None:
    if value is None:
        return None
    cleaned = str(value).strip()
    return cleaned or None


def _coerce_optional_int(value: Any, field_name: str) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool):
        raise InvalidTargetError(f"{field_name} must be an integer")
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise InvalidTargetError(f"{field_name} must be an integer") from exc
