"""Structured target parsing and resolution for Impress presentations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from colors import resolve_color
from impress.exceptions import (
    InvalidFormattingError,
    InvalidListError,
    InvalidPayloadError,
    InvalidSlideIndexError,
    InvalidTargetError,
    MasterNotFoundError,
    TargetAmbiguousError,
    TargetNoMatchError,
)

_SUPPORTED_KINDS = {
    "slide",
    "shape",
    "text",
    "table",
    "chart",
    "media",
    "image",
    "notes",
    "master_page",
    "list",
    "insertion",
}
_TEXTUAL_KINDS = {"text", "notes", "list", "insertion"}
_SHAPE_SELECTOR_KINDS = {
    "shape",
    "text",
    "table",
    "chart",
    "media",
    "image",
    "list",
    "insertion",
}
_ALIGNMENT_MAP = {"left": 0, "right": 1, "justify": 2, "center": 3}


@dataclass(frozen=True)
class ImpressTarget:
    """Canonical target description for Impress operations."""

    kind: str
    slide_index: int | None = None
    shape_name: str | None = None
    shape_index: int | None = None
    shape_type: str | None = None
    placeholder: str | None = None
    text: str | None = None
    after: str | None = None
    before: str | None = None
    occurrence: int | None = None
    master_name: str | None = None


@dataclass(frozen=True)
class TextFormatting:
    """Formatting payload for Impress text ranges."""

    bold: bool | None = None
    italic: bool | None = None
    underline: bool | None = None
    font_name: str | None = None
    font_size: float | None = None
    color: str | int | None = None
    align: str | None = None


@dataclass(frozen=True)
class ListItem:
    """One Impress list item."""

    text: str
    level: int = 0


@dataclass(frozen=True)
class ShapePlacement:
    """Position and size for a slide shape in centimetres."""

    x_cm: float
    y_cm: float
    width_cm: float
    height_cm: float


def parse_target(raw: dict[str, Any]) -> ImpressTarget:
    """Convert raw target fields into a validated ImpressTarget."""
    kind = str(raw.get("kind", "")).strip().lower()
    if not kind:
        raise InvalidTargetError("target.kind is required")

    target = ImpressTarget(
        kind=kind,
        slide_index=_coerce_optional_int(raw.get("slide_index"), "target.slide_index"),
        shape_name=_clean_optional_string(raw.get("shape_name")),
        shape_index=_coerce_optional_int(raw.get("shape_index"), "target.shape_index"),
        shape_type=_clean_optional_string(raw.get("shape_type")),
        placeholder=_clean_optional_string(raw.get("placeholder")),
        text=_clean_optional_string(raw.get("text")),
        after=_clean_optional_string(raw.get("after")),
        before=_clean_optional_string(raw.get("before")),
        occurrence=_coerce_optional_int(raw.get("occurrence"), "target.occurrence"),
        master_name=_clean_optional_string(raw.get("master_name")),
    )
    _validate_target(target)
    return target


def resolve_slide_target(target: ImpressTarget, doc: Any) -> Any:
    """Resolve one zero-based slide."""
    _validate_target(target)
    if target.kind == "master_page":
        raise InvalidTargetError("Master-page targets do not resolve to slides")
    if target.slide_index is None:
        raise InvalidTargetError("Slide-scoped targets require slide_index")

    pages = doc.DrawPages
    if target.slide_index < 0 or target.slide_index >= pages.Count:
        raise InvalidSlideIndexError(f"Slide index out of range: {target.slide_index}")
    return pages.getByIndex(target.slide_index)


def resolve_shape_target(target: ImpressTarget, doc: Any) -> Any:
    """Resolve one shape on one slide by placeholder, name, or index."""
    _validate_target(target)
    if target.kind == "notes":
        notes_shape = _find_notes_text_shape(
            resolve_slide_target(target, doc).getNotesPage()
        )
        if notes_shape is None:
            raise TargetNoMatchError("Notes text shape not found")
        return notes_shape
    if target.kind not in _SHAPE_SELECTOR_KINDS | {"shape"}:
        raise InvalidTargetError(
            f"Target kind '{target.kind}' does not resolve to a shape"
        )

    slide = resolve_slide_target(target, doc)
    if target.placeholder is not None:
        shape = _resolve_placeholder_shape(slide, target.placeholder)
        if shape is None:
            raise TargetNoMatchError(
                f'No placeholder matched "{target.placeholder}" on slide {target.slide_index}'
            )
        return shape

    if target.shape_name is not None:
        normalized_target = _normalize_name(target.shape_name)
        exact_matches = [
            slide.getByIndex(index)
            for index in range(slide.Count)
            if _normalize_name(_shape_name(slide.getByIndex(index)))
            == normalized_target
        ]
        matches = exact_matches
        if not matches:
            matches = [
                slide.getByIndex(index)
                for index in range(slide.Count)
                if _matches_uno_duplicate_name(
                    _normalize_name(_shape_name(slide.getByIndex(index))),
                    normalized_target,
                )
            ]
        if not matches:
            raise TargetNoMatchError(f'Shape not found: "{target.shape_name}"')
        if len(matches) > 1:
            raise TargetAmbiguousError(
                f'Shape target is ambiguous: "{target.shape_name}"'
            )
        return matches[0]

    if target.shape_index is not None:
        if target.shape_index < 0 or target.shape_index >= slide.Count:
            raise TargetNoMatchError(f"Shape index out of range: {target.shape_index}")
        return slide.getByIndex(target.shape_index)

    if target.shape_type is not None:
        matches = [
            slide.getByIndex(index)
            for index in range(slide.Count)
            if target.shape_type.lower()
            in str(slide.getByIndex(index).ShapeType).lower()
        ]
        if not matches:
            raise TargetNoMatchError(f'Shape type not found: "{target.shape_type}"')
        if len(matches) > 1:
            raise TargetAmbiguousError(
                f'Shape type target is ambiguous: "{target.shape_type}"'
            )
        return matches[0]

    raise InvalidTargetError(
        "Shape-scoped targets require placeholder, shape_name, shape_index, or shape_type"
    )


def resolve_text_range(target: ImpressTarget, doc: Any) -> Any:
    """Resolve a text target to one UNO text range."""
    _validate_target(target)
    if target.kind not in _TEXTUAL_KINDS:
        raise InvalidTargetError(
            f"Target kind '{target.kind}' does not resolve to text"
        )

    shape = _resolve_text_shape(target, doc)
    text_obj = shape.getText()
    full_text = shape.getString()
    window_start, window_end = _resolve_text_window(full_text, target)

    if target.kind == "insertion":
        cursor = text_obj.createTextCursor()
        cursor.gotoStart(False)
        cursor.goRight(window_start, False)
        return cursor

    if target.text is None:
        return _cursor_for_span(text_obj, window_start, window_end)

    start_positions = _find_substring_positions(
        full_text[window_start:window_end],
        target.text,
    )
    if not start_positions:
        raise TargetNoMatchError(f'No content matched target "{target.text}"')

    actual_positions = [window_start + position for position in start_positions]
    if target.occurrence is not None:
        if target.occurrence >= len(actual_positions):
            raise TargetNoMatchError(
                f'Target occurrence {target.occurrence} out of range for "{target.text}"'
            )
        chosen_start = actual_positions[target.occurrence]
    else:
        if len(actual_positions) > 1:
            raise TargetAmbiguousError(
                f'Target matched multiple spans: "{target.text}"'
            )
        chosen_start = actual_positions[0]
    return _cursor_for_span(text_obj, chosen_start, chosen_start + len(target.text))


def resolve_insertion_point(target: ImpressTarget | None, doc: Any) -> Any:
    """Resolve an insertion target to a UNO text cursor."""
    if target is None:
        slide = doc.DrawPages.getByIndex(doc.DrawPages.Count - 1)
        shape = _find_first_text_shape(slide)
        if shape is None:
            raise TargetNoMatchError("No text shape available for insertion")
        cursor = shape.getText().createTextCursor()
        cursor.gotoEnd(False)
        return cursor

    _validate_target(target)
    if target.kind != "insertion":
        raise InvalidTargetError("Insertion points require target.kind = insertion")

    shape = _resolve_text_shape(target, doc)
    text_obj = shape.getText()
    full_text = shape.getString()
    window_start, window_end = _resolve_text_window(full_text, target)

    if target.text is not None:
        matches = _find_substring_positions(
            full_text[window_start:window_end], target.text
        )
        if not matches:
            raise TargetNoMatchError(f'No content matched target "{target.text}"')
        actual_positions = [window_start + position for position in matches]
        if target.occurrence is not None:
            if target.occurrence >= len(actual_positions):
                raise TargetNoMatchError(
                    f'Target occurrence {target.occurrence} out of range for "{target.text}"'
                )
            index = target.occurrence
        else:
            if len(actual_positions) > 1:
                raise TargetAmbiguousError(
                    f'Target matched multiple spans: "{target.text}"'
                )
            index = 0
        cursor = text_obj.createTextCursor()
        cursor.gotoStart(False)
        cursor.goRight(actual_positions[index] + len(target.text), False)
        return cursor

    cursor = text_obj.createTextCursor()
    cursor.gotoStart(False)
    cursor.goRight(window_start, False)
    return cursor


def resolve_list_target(target: ImpressTarget, doc: Any) -> list[Any]:
    """Resolve one structural list block within slide or notes text."""
    _validate_target(target)
    if target.kind != "list":
        raise InvalidTargetError("List resolution requires target.kind = list")

    shape = _resolve_text_shape(target, doc)
    text_obj = shape.getText()
    full_text = shape.getString()
    window_start, window_end = _resolve_text_window(full_text, target)
    groups = _collect_list_groups(text_obj)
    candidates = [
        group
        for group in groups
        if _group_within_window(text_obj, group, window_start, window_end)
    ]
    if target.text is not None:
        candidates = [
            group
            for group in candidates
            if any(
                _normalize_list_item_text(paragraph.getString()) == target.text
                for paragraph in group
            )
        ]
    if target.occurrence is not None:
        if target.occurrence >= len(candidates):
            raise TargetNoMatchError(
                f"List occurrence out of range: {target.occurrence}"
            )
        return candidates[target.occurrence]
    if not candidates:
        raise TargetNoMatchError("No list matched target")
    if len(candidates) > 1:
        raise TargetAmbiguousError("List target matched multiple lists")
    return candidates[0]


def resolve_master_page_target(target: ImpressTarget, doc: Any) -> Any:
    """Resolve one master page by name."""
    _validate_target(target)
    if target.kind != "master_page":
        raise InvalidTargetError(
            "Master-page resolution requires target.kind = master_page"
        )
    assert target.master_name is not None
    masters = doc.MasterPages
    for index in range(masters.Count):
        master = masters.getByIndex(index)
        if str(master.Name) == target.master_name:
            return master
    raise MasterNotFoundError(f'Master page not found: "{target.master_name}"')


def validate_formatting(formatting: TextFormatting) -> None:
    """Ensure an Impress formatting payload is well formed."""
    if not any(value is not None for value in formatting.__dict__.values()):
        raise InvalidFormattingError("At least one formatting field is required")
    if formatting.align is not None:
        key = str(formatting.align).strip().lower()
        if key not in _ALIGNMENT_MAP:
            raise InvalidFormattingError(f"Unknown align value: {formatting.align}")
    if formatting.color is not None:
        try:
            resolve_color(formatting.color)
        except (TypeError, ValueError) as exc:
            raise InvalidFormattingError(str(exc)) from exc


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


def validate_placement(placement: ShapePlacement) -> None:
    """Ensure shape placement values are valid centimetre measurements."""
    if placement.x_cm < 0 or placement.y_cm < 0:
        raise InvalidPayloadError("Placement coordinates must be non-negative")
    if placement.width_cm <= 0 or placement.height_cm <= 0:
        raise InvalidPayloadError("Placement width and height must be positive")


def alignment_code(value: str) -> int:
    """Return the UNO alignment code for a public alignment string."""
    key = value.strip().lower()
    if key not in _ALIGNMENT_MAP:
        raise InvalidFormattingError(f"Unknown align value: {value}")
    return _ALIGNMENT_MAP[key]


def _validate_target(target: ImpressTarget) -> None:
    if target.kind not in _SUPPORTED_KINDS:
        raise InvalidTargetError(f"Unsupported target kind: {target.kind}")
    if target.slide_index is not None and target.slide_index < 0:
        raise InvalidTargetError("target.slide_index must be >= 0")
    if target.shape_index is not None and target.shape_index < 0:
        raise InvalidTargetError("target.shape_index must be >= 0")
    if target.occurrence is not None and target.occurrence < 0:
        raise InvalidTargetError("target.occurrence must be >= 0")
    if target.shape_name is not None and target.shape_index is not None:
        raise InvalidTargetError(
            "target.shape_name and target.shape_index are mutually exclusive"
        )
    if target.placeholder is not None and (
        target.shape_name is not None or target.shape_index is not None
    ):
        raise InvalidTargetError(
            "target.placeholder is mutually exclusive with shape_name and shape_index"
        )
    if target.kind == "master_page":
        if target.master_name is None:
            raise InvalidTargetError("Master-page targets require master_name")
        if any(
            value is not None
            for value in (
                target.slide_index,
                target.shape_name,
                target.shape_index,
                target.shape_type,
                target.placeholder,
                target.text,
                target.after,
                target.before,
                target.occurrence,
            )
        ):
            raise InvalidTargetError("Master-page targets only support master_name")
        return
    if target.slide_index is None:
        raise InvalidTargetError("Slide-scoped targets require slide_index")
    if target.kind == "slide":
        if any(
            value is not None
            for value in (
                target.shape_name,
                target.shape_index,
                target.shape_type,
                target.placeholder,
                target.text,
                target.after,
                target.before,
                target.occurrence,
                target.master_name,
            )
        ):
            raise InvalidTargetError("Slide targets only support slide_index")
        return
    if target.kind == "notes":
        if any(
            value is not None
            for value in (
                target.shape_name,
                target.shape_index,
                target.shape_type,
                target.placeholder,
                target.master_name,
            )
        ):
            raise InvalidTargetError("Notes targets do not support shape selectors")
        return
    if target.kind in _SHAPE_SELECTOR_KINDS | {"shape"}:
        if (
            target.placeholder is None
            and target.shape_name is None
            and target.shape_index is None
            and target.shape_type is None
            and target.kind not in {"list", "insertion"}
        ):
            raise InvalidTargetError(
                "Shape-scoped targets require placeholder, shape_name, shape_index, or shape_type"
            )
    if target.kind == "list" and target.text is None and target.occurrence is None:
        raise InvalidTargetError("List targets require text or occurrence")


def _resolve_text_shape(target: ImpressTarget, doc: Any) -> Any:
    shape = resolve_shape_target(target, doc)
    try:
        shape.getText()
        shape.getString()
        return shape
    except Exception:
        pass
    raise InvalidTargetError("Target does not resolve to a text-bearing shape")


def _resolve_placeholder_shape(slide: Any, placeholder: str) -> Any | None:
    key = placeholder.strip().lower()
    if key not in {"title", "subtitle", "body"}:
        raise InvalidTargetError(f"Unsupported placeholder: {placeholder}")
    for index in range(slide.Count):
        shape = slide.getByIndex(index)
        if key == "title" and _is_title_shape(shape):
            return shape
        if key == "subtitle" and _is_subtitle_shape(shape):
            return shape
        if key == "body" and _is_body_placeholder(shape):
            return shape
    return None


def _resolve_text_window(full_text: str, target: ImpressTarget) -> tuple[int, int]:
    start = 0
    end = len(full_text)
    if target.after is not None:
        after_positions = _find_substring_positions(full_text, target.after)
        if len(after_positions) != 1:
            if not after_positions:
                raise TargetNoMatchError(
                    f'No text matched target.after: "{target.after}"'
                )
            raise TargetAmbiguousError(
                f'target.after matched multiple spans: "{target.after}"'
            )
        start = after_positions[0] + len(target.after)
    if target.before is not None:
        before_positions = _find_substring_positions(full_text, target.before)
        if len(before_positions) != 1:
            if not before_positions:
                raise TargetNoMatchError(
                    f'No text matched target.before: "{target.before}"'
                )
            raise TargetAmbiguousError(
                f'target.before matched multiple spans: "{target.before}"'
            )
        end = before_positions[0]
    if start > end:
        raise InvalidTargetError("target.after resolves after target.before")
    return start, end


def _cursor_for_span(text_obj: Any, start: int, end: int) -> Any:
    cursor = text_obj.createTextCursor()
    cursor.gotoStart(False)
    if start:
        cursor.goRight(start, False)
    if end > start:
        cursor.goRight(end - start, True)
    return cursor


def _find_substring_positions(haystack: str, needle: str) -> list[int]:
    positions: list[int] = []
    start = 0
    while True:
        index = haystack.find(needle, start)
        if index == -1:
            return positions
        positions.append(index)
        start = index + 1


def _collect_list_groups(text_obj: Any) -> list[list[Any]]:
    enumeration = text_obj.createEnumeration()
    groups: list[list[Any]] = []
    current: list[Any] = []
    while enumeration.hasMoreElements():
        paragraph = enumeration.nextElement()
        if _paragraph_is_list_item(paragraph):
            current.append(paragraph)
            continue
        if current:
            groups.append(current)
            current = []
    if current:
        groups.append(current)
    return groups


def _group_within_window(text_obj: Any, group: list[Any], start: int, end: int) -> bool:
    first = _cursor_index(text_obj, group[0].getStart())
    last = _cursor_index(text_obj, group[-1].getEnd())
    return first >= start and last <= end


def _cursor_index(text_obj: Any, position: Any) -> int:
    cursor = text_obj.createTextCursor()
    cursor.gotoStart(False)
    cursor.gotoRange(position, True)
    return len(cursor.getString())


def _find_notes_text_shape(notes_page: Any) -> Any | None:
    for index in range(notes_page.Count):
        shape = notes_page.getByIndex(index)
        try:
            shape.getText()
            shape.getString()
            return shape
        except Exception:
            continue
    return None


def _find_first_text_shape(slide: Any) -> Any | None:
    for index in range(slide.Count):
        shape = slide.getByIndex(index)
        try:
            shape.getText()
            shape.getString()
            return shape
        except Exception:
            continue
    return None


def _is_title_shape(shape: Any) -> bool:
    try:
        return bool(shape.supportsService("com.sun.star.presentation.TitleTextShape"))
    except Exception:
        return False


def _is_subtitle_shape(shape: Any) -> bool:
    try:
        return bool(
            shape.supportsService("com.sun.star.presentation.SubtitleTextShape")
        )
    except Exception:
        return False


def _is_body_placeholder(shape: Any) -> bool:
    try:
        shape.getText()
        shape.getString()
    except Exception:
        return False
    if not bool(getattr(shape, "IsPresentationObject", False)):
        return False
    return not _is_title_shape(shape) and not _is_subtitle_shape(shape)


def _shape_name(shape: Any) -> str:
    if hasattr(shape, "getName"):
        try:
            return str(shape.getName())
        except Exception:
            pass
    return str(getattr(shape, "Name", ""))


def _normalize_name(value: str) -> str:
    return "_".join(value.split()).lower()


def _matches_uno_duplicate_name(actual: str, expected: str) -> bool:
    if not actual.startswith(expected):
        return False
    suffix = actual[len(expected) :]
    if not suffix:
        return False
    return suffix.startswith("_") and suffix[1:].isdigit()


def _paragraph_cursor(paragraph: Any) -> Any:
    text_obj = paragraph.getText()
    cursor = text_obj.createTextCursorByRange(paragraph.getStart())
    cursor.gotoRange(paragraph.getEnd(), True)
    return cursor


def _paragraph_property(paragraph: Any, name: str, default: Any = None) -> Any:
    try:
        return getattr(paragraph, name)
    except Exception:
        try:
            return getattr(_paragraph_cursor(paragraph), name)
        except Exception:
            return default


def _paragraph_is_list_item(paragraph: Any) -> bool:
    value = _paragraph_property(paragraph, "NumberingLevel", None)
    if value is None:
        return False
    try:
        return int(value) >= 0
    except Exception:
        return False


def _clean_optional_string(value: Any) -> str | None:
    if value is None:
        return None
    cleaned = str(value).strip()
    return cleaned or None


def _normalize_list_item_text(text: str) -> str:
    return text.strip()


def _coerce_optional_int(value: Any, field_name: str) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool):
        raise InvalidTargetError(f"{field_name} must be an integer")
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise InvalidTargetError(f"{field_name} must be an integer") from exc
