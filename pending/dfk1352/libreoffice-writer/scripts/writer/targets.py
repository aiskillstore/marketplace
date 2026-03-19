"""Structured target parsing and resolution for Writer documents."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from colors import resolve_color
from writer.exceptions import (
    InvalidFormattingError,
    InvalidListError,
    InvalidPayloadError,
    InvalidTableError,
    InvalidTargetError,
    TargetAmbiguousError,
    TargetNoMatchError,
)


@dataclass(frozen=True)
class WriterTarget:
    """Canonical target description for Writer operations."""

    kind: str
    text: str | None = None
    after: str | None = None
    before: str | None = None
    occurrence: int | None = None
    name: str | None = None
    index: int | None = None


@dataclass(frozen=True)
class TextFormatting:
    """Formatting payload for Writer text ranges."""

    bold: bool | None = None
    italic: bool | None = None
    underline: bool | None = None
    font_name: str | None = None
    font_size: float | None = None
    color: str | int | None = None
    align: str | None = None
    line_spacing: float | None = None
    spacing_before: int | None = None
    spacing_after: int | None = None


@dataclass(frozen=True)
class ListItem:
    """One Writer list item."""

    text: str
    level: int = 0


def parse_target(raw: dict[str, Any]) -> WriterTarget:
    """Convert raw target fields into a validated WriterTarget."""
    kind = str(raw.get("kind", "")).strip().lower()
    if not kind:
        raise InvalidTargetError("target.kind is required")

    occurrence = raw.get("occurrence")
    index = raw.get("index")
    if occurrence is not None:
        occurrence = _coerce_int(occurrence, "target.occurrence")
    if index is not None:
        index = _coerce_int(index, "target.index")

    target = WriterTarget(
        kind=kind,
        text=_clean_optional_string(raw.get("text")),
        after=_clean_optional_string(raw.get("after")),
        before=_clean_optional_string(raw.get("before")),
        occurrence=occurrence,
        name=_clean_optional_string(raw.get("name")),
        index=index,
    )
    _validate_target(target)
    return target


def resolve_text_range(target: WriterTarget, doc: Any) -> Any:
    """Resolve a text target to one UNO text range."""
    _ensure_kind(target, {"text"})
    _validate_target(target)

    bounds = _resolve_window(target, doc)
    if target.text is None:
        return _window_range(doc, bounds[0], bounds[1])

    matches = _find_text_matches(doc, target.text)
    windowed = [
        match for match in matches if _range_within_window(doc.Text, match, bounds)
    ]
    return _choose_unique_match(windowed, target, describe=target.text)


def resolve_insertion_point(target: WriterTarget | None, doc: Any) -> Any:
    """Resolve an insertion target to a UNO text cursor."""
    text_obj = doc.Text
    if target is None:
        cursor = text_obj.createTextCursor()
        cursor.gotoEnd(False)
        return cursor

    _ensure_kind(target, {"insertion"})
    _validate_target(target)

    start, end = _resolve_window(target, doc)
    if target.text is not None:
        matches = _find_text_matches(doc, target.text)
        windowed = [
            match
            for match in matches
            if _range_within_window(text_obj, match, (start, end))
        ]
        chosen = _choose_unique_match(windowed, target, describe=target.text)
        return text_obj.createTextCursorByRange(chosen.End)

    if target.before is not None and target.after is None:
        return text_obj.createTextCursorByRange(end)
    return text_obj.createTextCursorByRange(start)


def resolve_list_target(target: WriterTarget, doc: Any) -> list[Any]:
    """Resolve a target to one logical list block."""
    _ensure_kind(target, {"list"})
    _validate_target(target)

    bounds = _resolve_window(target, doc)
    groups = _collect_list_groups(doc)
    candidates = [
        group
        for group in groups
        if _paragraph_range_within_window(doc.Text, group[0], bounds)
        and _paragraph_range_within_window(doc.Text, group[-1], bounds)
    ]
    if target.text is not None:
        candidates = [
            group
            for group in candidates
            if any(paragraph.getString() == target.text for paragraph in group)
        ]
    return _choose_unique_group(candidates, target)


def resolve_table_target(target: WriterTarget, doc: Any) -> Any:
    """Resolve a target to one text table."""
    _ensure_kind(target, {"table"})
    _validate_target(target)
    if target.name is not None:
        tables = doc.getTextTables()
        names = list(tables.getElementNames())
        matches = [
            name
            for name in names
            if _normalize_name(name) == _normalize_name(target.name)
        ]
        if not matches:
            raise TargetNoMatchError(f'Table not found: "{target.name}"')
        if len(matches) > 1:
            raise TargetAmbiguousError(f'Table target is ambiguous: "{target.name}"')
        return tables.getByName(matches[0])

    if target.index is None:
        raise InvalidTargetError("Table targets require name or index")
    tables = doc.getTextTables()
    if target.index < 0 or target.index >= tables.getCount():
        raise TargetNoMatchError(f"Table index out of range: {target.index}")
    return tables.getByIndex(target.index)


def resolve_image_target(target: WriterTarget, doc: Any) -> Any:
    """Resolve a target to one image."""
    _ensure_kind(target, {"image"})
    _validate_target(target)
    graphics = doc.getGraphicObjects()
    if target.name is not None:
        names = list(graphics.getElementNames())
        matches = [
            name
            for name in names
            if _normalize_name(name) == _normalize_name(target.name)
        ]
        if not matches:
            raise TargetNoMatchError(f'Image not found: "{target.name}"')
        if len(matches) > 1:
            raise TargetAmbiguousError(f'Image target is ambiguous: "{target.name}"')
        return graphics.getByName(matches[0])

    if target.index is None:
        raise InvalidTargetError("Image targets require name or index")
    names = list(graphics.getElementNames())
    if target.index < 0 or target.index >= len(names):
        raise TargetNoMatchError(f"Image index out of range: {target.index}")
    return graphics.getByName(names[target.index])


def validate_formatting(formatting: TextFormatting) -> None:
    """Ensure a formatting payload is well-formed."""
    if not any(value is not None for value in formatting.__dict__.values()):
        raise InvalidFormattingError("At least one formatting field is required")
    if formatting.align is not None:
        align_key = str(formatting.align).strip().lower()
        if align_key not in {"left", "center", "right", "justify"}:
            raise InvalidFormattingError(f"Unknown align value: {formatting.align}")
    if formatting.color is not None:
        try:
            resolve_color(formatting.color)
        except (TypeError, ValueError) as exc:
            raise InvalidFormattingError(str(exc)) from exc


def validate_table_data(rows: int, cols: int, data: list[list[Any]] | None) -> None:
    """Validate table dimensions and optional cell data."""
    if rows < 1 or cols < 1:
        raise InvalidTableError("Rows and cols must be >= 1")
    if data is None:
        return
    if len(data) != rows:
        raise InvalidTableError(f"Data has {len(data)} rows but table needs {rows}")
    for row_index, row in enumerate(data):
        if len(row) != cols:
            raise InvalidTableError(
                f"Data row {row_index} has {len(row)} cols but table needs {cols}"
            )


def validate_image_update(
    image_path: str | None,
    width: int | None,
    height: int | None,
) -> None:
    """Validate image update payload."""
    if image_path is None and width is None and height is None:
        raise InvalidPayloadError("update_image requires image_path and/or size")


def validate_list_items(items: list[ListItem]) -> None:
    """Ensure list items are structurally valid."""
    if not items:
        raise InvalidListError("List items cannot be empty")
    previous_level = 0
    for index, item in enumerate(items):
        if item.level < 0:
            raise InvalidListError("List item levels must be >= 0")
        if index > 0 and item.level > previous_level + 1:
            raise InvalidListError("List nesting cannot skip levels")
        previous_level = item.level


def _validate_target(target: WriterTarget) -> None:
    if target.occurrence is not None and target.occurrence < 0:
        raise InvalidTargetError("target.occurrence must be >= 0")
    if target.name is not None and target.index is not None:
        raise InvalidTargetError("target.name and target.index are mutually exclusive")

    if target.kind in {"text", "insertion"}:
        if not any(
            value is not None
            for value in (target.text, target.after, target.before, target.occurrence)
        ):
            raise InvalidTargetError(
                f"Target kind '{target.kind}' needs text, after, before, or occurrence"
            )
        if target.name is not None or target.index is not None:
            raise InvalidTargetError(
                f"Target kind '{target.kind}' does not support name or index"
            )
        if (
            target.kind == "insertion"
            and target.occurrence is not None
            and target.text is None
        ):
            raise InvalidTargetError("Insertion occurrence requires target.text")
        return

    if target.kind in {"table", "image"}:
        if target.name is None and target.index is None:
            raise InvalidTargetError(
                f"Target kind '{target.kind}' requires name or index"
            )
        if any(
            value is not None
            for value in (target.text, target.after, target.before, target.occurrence)
        ):
            raise InvalidTargetError(
                f"Target kind '{target.kind}' only supports name or index"
            )
        return

    if target.kind == "list":
        if target.name is not None or target.index is not None:
            raise InvalidTargetError("List targets do not support name or index")
        if target.text is None and target.occurrence is None:
            raise InvalidTargetError("List targets require text or occurrence")
        return

    raise InvalidTargetError(f"Unsupported target kind: {target.kind}")


def _resolve_window(target: WriterTarget, doc: Any) -> tuple[Any, Any]:
    text_obj = doc.Text
    start = text_obj.getStart()
    end = text_obj.getEnd()

    if target.after is not None:
        after_match = _unique_text_match(doc, target.after, label="after")
        start = after_match.End
    if target.before is not None:
        before_match = _unique_text_match(doc, target.before, label="before")
        end = before_match.Start
    if target.after is not None and target.before is not None:
        if text_obj.compareRegionStarts(start, end) < 0:
            raise InvalidTargetError("target.after resolves after target.before")
    return start, end


def _window_range(doc: Any, start: Any, end: Any) -> Any:
    if doc.Text.compareRegionStarts(start, end) < 0:
        raise InvalidTargetError("Target window start is after end")
    cursor = doc.Text.createTextCursorByRange(start)
    cursor.gotoRange(end, True)
    return cursor


def _range_within_window(
    text_obj: Any, text_range: Any, bounds: tuple[Any, Any]
) -> bool:
    start, end = bounds
    if text_obj.compareRegionStarts(text_range.Start, start) > 0:
        return False
    if text_obj.compareRegionStarts(text_range.End, end) < 0:
        return False
    return True


def _paragraph_range_within_window(
    text_obj: Any,
    paragraph: Any,
    bounds: tuple[Any, Any],
) -> bool:
    cursor = text_obj.createTextCursorByRange(paragraph.getStart())
    cursor.gotoRange(paragraph.getEnd(), True)
    return _range_within_window(text_obj, cursor, bounds)


def _choose_unique_match(
    matches: list[Any], target: WriterTarget, describe: str
) -> Any:
    if target.occurrence is not None:
        if target.occurrence >= len(matches):
            raise TargetNoMatchError(
                f'Target occurrence {target.occurrence} out of range for "{describe}"'
            )
        return matches[target.occurrence]
    if not matches:
        raise TargetNoMatchError(f'No content matched target "{describe}"')
    if len(matches) > 1:
        raise TargetAmbiguousError(f'Target matched multiple spans: "{describe}"')
    return matches[0]


def _choose_unique_group(groups: list[list[Any]], target: WriterTarget) -> list[Any]:
    if target.occurrence is not None:
        if target.occurrence >= len(groups):
            raise TargetNoMatchError(
                f"List occurrence out of range: {target.occurrence}"
            )
        return groups[target.occurrence]
    if not groups:
        raise TargetNoMatchError("No list matched target")
    if len(groups) > 1:
        raise TargetAmbiguousError("List target matched multiple lists")
    return groups[0]


def _unique_text_match(doc: Any, needle: str, label: str) -> Any:
    matches = _find_text_matches(doc, needle)
    if not matches:
        raise TargetNoMatchError(f'No text matched target.{label}: "{needle}"')
    if len(matches) > 1:
        raise TargetAmbiguousError(f'target.{label} matched multiple spans: "{needle}"')
    return matches[0]


def _find_text_matches(doc: Any, needle: str) -> list[Any]:
    search = doc.createSearchDescriptor()
    search.SearchString = needle
    matches: list[Any] = []
    found = doc.findFirst(search)
    while found is not None:
        matches.append(found)
        found = doc.findNext(found.End, search)
    return matches


def _collect_list_groups(doc: Any) -> list[list[Any]]:
    enumeration = doc.Text.createEnumeration()
    groups: list[list[Any]] = []
    current: list[Any] = []
    while enumeration.hasMoreElements():
        paragraph = enumeration.nextElement()
        if getattr(paragraph, "NumberingStyleName", ""):
            current.append(paragraph)
            continue
        if current:
            groups.append(current)
            current = []
    if current:
        groups.append(current)
    return groups


def _ensure_kind(target: WriterTarget, allowed: set[str]) -> None:
    if target.kind not in allowed:
        raise InvalidTargetError(
            f"Target kind '{target.kind}' is not valid here; expected {sorted(allowed)}"
        )


def _normalize_name(value: str) -> str:
    return "_".join(value.split()).lower()


def _clean_optional_string(value: Any) -> str | None:
    if value is None:
        return None
    cleaned = str(value).strip()
    return cleaned or None


def _coerce_int(value: Any, field_name: str) -> int:
    if isinstance(value, bool):
        raise InvalidTargetError(f"{field_name} must be an integer")
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise InvalidTargetError(f"{field_name} must be an integer") from exc
