#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

IMPORTANT_KEYS = [
    "id",
    "name",
    "title",
    "label",
    "username",
    "email",
    "status",
    "type",
    "created_at",
    "updated_at",
    "timestamp",
]

DISPLAY_NAME_KEYS = ("name", "title", "label", "username", "email")
DEFAULT_FALSE_OMIT_KEYS = {
    "deleted",
    "is_deleted",
    "archived",
    "is_archived",
    "disabled",
    "is_disabled",
    "removed",
    "is_removed",
    "hidden",
    "is_hidden",
}
NEGATED_BOOL_PHRASES = {
    "verified": "unverified",
    "active": "inactive",
    "enabled": "disabled",
    "public": "private",
}
PAIR_FIELDS = (
    ("email", "email_verified"),
    ("phone", "phone_verified"),
)
GENERIC_ENTITY_NAMES = {"Record", "Item", "Entry"}
INLINE_ONLY_CONTEXT_KEYS = {"profile", "settings", "metadata", "meta", "details", "attributes", "props"}
SUMMARY_PREFERRED_KEYS = {
    "status",
    "type",
    "email",
    "phone",
    "created_at",
    "updated_at",
    "timestamp",
    "profile",
}


@dataclass
class RenderOptions:
    strict: bool = False
    preserve_keys: set[str] = field(default_factory=set)
    preserve_paths: set[str] = field(default_factory=set)
    expand: set[str] = field(default_factory=set)
    show_paths: bool = False


OPTIONS = RenderOptions()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert JSON/jsonb payloads into compact readable context.",
    )
    parser.add_argument("--input", help="Input JSON file. Defaults to stdin when omitted.")
    parser.add_argument("--output", help="Optional output file. Defaults to stdout.")
    parser.add_argument("--max-samples", type=int, default=3, help="Max sample items for arrays.")
    parser.add_argument("--max-depth", type=int, default=3, help="Max nesting depth to expand.")
    parser.add_argument(
        "--max-string-len",
        type=int,
        default=72,
        help="Max visible characters before truncating long strings.",
    )
    parser.add_argument(
        "--style",
        choices=("sectioned", "flat"),
        default="sectioned",
        help="Output style. 'sectioned' groups into Summary/Details/Collections; 'flat' emits plain bullets.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Use more conservative compression and keep more explicit structure.",
    )
    parser.add_argument(
        "--preserve",
        default="",
        help="Comma-separated keys or dotted paths to always keep.",
    )
    parser.add_argument(
        "--expand",
        default="",
        help="Comma-separated sections to expand: collections, details, or all.",
    )
    parser.add_argument(
        "--show-paths",
        action="store_true",
        help="Append source path markers such as [@status] to rendered lines.",
    )
    return parser.parse_args()


def parse_csv(raw: str) -> list[str]:
    return [item.strip() for item in raw.split(",") if item.strip()]


def configure_options(args: argparse.Namespace) -> None:
    preserve_items = parse_csv(args.preserve)
    expand_items = {item.lower() for item in parse_csv(args.expand)}
    if "all" in expand_items:
        expand_items = {"collections", "details"}
    invalid_expand = expand_items - {"collections", "details"}
    if invalid_expand:
        raise SystemExit(f"Unsupported --expand values: {', '.join(sorted(invalid_expand))}")

    OPTIONS.strict = args.strict
    OPTIONS.preserve_keys = {item for item in preserve_items if "." not in item}
    OPTIONS.preserve_paths = {item for item in preserve_items if "." in item}
    OPTIONS.expand = expand_items
    OPTIONS.show_paths = args.show_paths


def path_string(path: tuple[str, ...]) -> str:
    return ".".join(path)


def is_preserved(key: str | None, path: tuple[str, ...]) -> bool:
    if key and key in OPTIONS.preserve_keys:
        return True
    if path and path_string(path) in OPTIONS.preserve_paths:
        return True
    return False


def should_expand(section: str) -> bool:
    return section in OPTIONS.expand


def format_path(path: tuple[str, ...]) -> str:
    return ".".join(path) if path else "root"


def attach_paths(text: str, *paths: tuple[str, ...]) -> str:
    if not OPTIONS.show_paths:
        return text
    unique: list[str] = []
    seen: set[str] = set()
    for path in paths:
        rendered = f"@{format_path(path)}"
        if rendered not in seen:
            seen.add(rendered)
            unique.append(rendered)
    return f"{text} [{', '.join(unique)}]"


def load_payload(input_path: str | None) -> Any:
    try:
        if input_path:
            return json.loads(Path(input_path).read_text(encoding="utf-8"))
        raw = sys.stdin.read()
        if not raw.strip():
            raise ValueError("No JSON input provided.")
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"JSON parse error: {exc.msg} at line {exc.lineno}, column {exc.colno}")
    except OSError as exc:
        raise SystemExit(f"Unable to read input: {exc}")
    except ValueError as exc:
        raise SystemExit(str(exc))


def write_output(output: str, output_path: str | None) -> None:
    if output_path:
        Path(output_path).write_text(output + "\n", encoding="utf-8")
        return
    sys.stdout.write(output + "\n")


def prune(value: Any, key: str | None = None, path: tuple[str, ...] = ()) -> Any:
    if isinstance(value, dict):
        pruned: dict[str, Any] = {}
        for child_key, child_value in value.items():
            child_path = (*path, child_key)
            cleaned = prune(child_value, child_key, child_path)
            if cleaned is _EMPTY:
                if is_preserved(child_key, child_path):
                    pruned[child_key] = child_value
                continue
            pruned[child_key] = cleaned
        return pruned if pruned else _EMPTY

    if isinstance(value, list):
        cleaned_items = [prune(item, path=path) for item in value]
        kept_items = [item for item in cleaned_items if item is not _EMPTY]
        return kept_items if kept_items else _EMPTY

    if value is None:
        if is_preserved(key, path):
            return None
        return _EMPTY

    if isinstance(value, str):
        if not value.strip():
            if is_preserved(key, path):
                return value
            return _EMPTY
        return value

    if isinstance(value, bool):
        if OPTIONS.strict:
            return value
        if value is False and key in DEFAULT_FALSE_OMIT_KEYS and not is_preserved(key, path):
            return _EMPTY
        return value

    return value


class _EmptySentinel:
    pass


_EMPTY = _EmptySentinel()


def humanize_key(key: str) -> str:
    normalized = key.replace("-", "_")
    normalized = re.sub(r"^(is_|has_)", "", normalized)
    normalized = normalized.strip("_")
    normalized = normalized.replace("_", " ")
    return normalized or "value"


def singularize(word: str) -> str:
    word = re.sub(r"[_\-\s]+", " ", word).strip()
    if not word:
        return "record"
    base = word.split()[-1]
    if base.endswith("ies") and len(base) > 3:
        return base[:-3] + "y"
    if base.endswith("ses") and len(base) > 3:
        return base[:-2]
    if base.endswith("s") and not base.endswith("ss") and len(base) > 1:
        return base[:-1]
    return base


def titleize(text: str) -> str:
    return " ".join(part.upper() if part.lower() in {"id", "api", "url", "llm"} else part.capitalize() for part in re.split(r"[\s_-]+", text) if part)


def join_naturally(items: list[str]) -> str:
    cleaned = [item for item in items if item]
    if not cleaned:
        return ""
    if len(cleaned) == 1:
        return cleaned[0]
    if len(cleaned) == 2:
        return f"{cleaned[0]} and {cleaned[1]}"
    return ", ".join(cleaned[:-1]) + f", and {cleaned[-1]}"


def pluralize(word: str, count: int) -> str:
    if count == 1:
        return singularize(word)
    lowered = singularize(word)
    if lowered.endswith("y") and len(lowered) > 1 and lowered[-2] not in "aeiou":
        return lowered[:-1] + "ies"
    if lowered.endswith("s"):
        return lowered + "es"
    return lowered + "s"


def sentence_case(text: str) -> str:
    if not text:
        return text
    return text[0].upper() + text[1:]


def strip_terminal_period(text: str) -> str:
    return text.rstrip(". ")


def looks_like_user(obj: dict[str, Any]) -> bool:
    user_hints = {"email", "username", "profile"}
    return bool(user_hints & set(obj.keys()))


def looks_like_order(obj: dict[str, Any]) -> bool:
    order_hints = {"total", "currency", "items"}
    return bool(order_hints & set(obj.keys()))


def looks_like_event(obj: dict[str, Any]) -> bool:
    return "timestamp" in obj or ("event" in obj and "status" in obj)


def detect_entity_type(obj: dict[str, Any], context_key: str | None = None) -> str:
    explicit_type = obj.get("type")
    if isinstance(explicit_type, str) and explicit_type.strip() and len(explicit_type) <= 32:
        return titleize(explicit_type)
    if context_key and context_key not in {"items", "data", "results", "records"}:
        return titleize(singularize(context_key))
    if looks_like_user(obj):
        return "User"
    if looks_like_order(obj):
        return "Order"
    if looks_like_event(obj):
        return "Event"
    return "Record"


def extract_identifier(obj: dict[str, Any]) -> str | None:
    if "id" in obj and is_scalar(obj["id"]):
        return format_scalar(obj["id"], 40, quote_strings=False)
    for key, value in obj.items():
        if key.endswith("_id") and is_scalar(value):
            return format_scalar(value, 40, quote_strings=False)
    return None


def extract_display_name(obj: dict[str, Any], max_string_len: int) -> str | None:
    for key in DISPLAY_NAME_KEYS:
        value = obj.get(key)
        if isinstance(value, str) and value.strip():
            return truncate_string(value, max_string_len)
    return None


def make_header(obj: dict[str, Any], context_key: str | None, max_string_len: int) -> str:
    entity_type = detect_entity_type(obj, context_key)
    identifier = extract_identifier(obj)
    display_name = extract_display_name(obj, max_string_len)
    if identifier and display_name and display_name != identifier:
        return f"{entity_type}[{identifier}]: {display_name}"
    if identifier:
        return f"{entity_type}[{identifier}]"
    if display_name:
        return f"{entity_type}: {display_name}"
    return entity_type


def is_scalar(value: Any) -> bool:
    return isinstance(value, (str, int, float, bool))


def truncate_string(value: str, max_len: int) -> str:
    if len(value) <= max_len:
        return value
    visible = max(8, max_len - 12)
    return f"{value[:visible].rstrip()}… (len={len(value)})"


def format_scalar(value: Any, max_string_len: int, quote_strings: bool = True) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        text = truncate_string(value, max_string_len)
        return f"\"{text}\"" if quote_strings and (" " in text or ":" in text) else text
    return str(value)


def bool_phrase(key: str, value: bool) -> str | None:
    label = humanize_key(key).lower()
    if value:
        return label
    simple_key = re.sub(r"^(is_|has_)", "", key)
    if simple_key in DEFAULT_FALSE_OMIT_KEYS:
        return None
    if simple_key in NEGATED_BOOL_PHRASES:
        return NEGATED_BOOL_PHRASES[simple_key]
    return f"{label}: false"


def naturalize_bool_phrase(phrase: str) -> str:
    if ": false" in phrase:
        key = phrase.split(": false", 1)[0]
        return f"{sentence_case(key)}: false."
    return f"Status: {phrase}."


def naturalize_scalar_field(key: str, value: Any, max_string_len: int) -> str:
    human_key = humanize_key(key)
    rendered = format_scalar(value, max_string_len, quote_strings=False)
    if key == "status":
        return f"Status: {rendered}."
    if key.endswith("_at") or "time" in key or "date" in key:
        return f"{sentence_case(human_key)}: {rendered}."
    return f"{sentence_case(human_key)}: {rendered}."


def shorten_header(header: str) -> str:
    return header.replace(": ", " ")


def sort_key(item: tuple[str, Any]) -> tuple[int, int, str]:
    key, value = item
    type_weight = 0 if is_scalar(value) else 1 if isinstance(value, dict) else 2
    if key in IMPORTANT_KEYS:
        return (0, IMPORTANT_KEYS.index(key), key)
    return (1, type_weight, key)


def summarize_object_inline(
    obj: dict[str, Any],
    *,
    context_key: str | None,
    depth: int,
    max_depth: int,
    max_samples: int,
    max_string_len: int,
) -> str:
    header = make_header(obj, context_key, max_string_len)
    phrases = summarize_fields(
        obj,
        path=(),
        depth=depth,
        max_depth=max_depth,
        max_samples=max_samples,
        max_string_len=max_string_len,
        inline=True,
    )
    if context_key in INLINE_ONLY_CONTEXT_KEYS and not OPTIONS.strict:
        return ", ".join(phrases[:4]) if phrases else header
    if header not in GENERIC_ENTITY_NAMES:
        if phrases:
            return f"{header} with {join_naturally(phrases[:3])}"
        return header
    if phrases:
        return join_naturally(phrases[:4])
    return header


def sample_scalar_list(items: list[Any], max_samples: int, max_string_len: int) -> str:
    samples = [format_scalar(item, max_string_len, quote_strings=False) for item in items[:max_samples]]
    if len(items) <= max_samples:
        return join_naturally(samples)
    return join_naturally(samples) + f", and {len(items) - max_samples} more"


def summarize_array(
    key: str,
    items: list[Any],
    *,
    depth: int,
    max_depth: int,
    max_samples: int,
    max_string_len: int,
) -> str:
    if not items:
        return "0 total."
    if all(isinstance(item, dict) for item in items):
        status_counter = Counter()
        for item in items:
            status = item.get("status")
            if isinstance(status, str) and status.strip():
                status_counter[status] += 1
        summary = f"{len(items)} total"
        if status_counter:
            top_statuses = ", ".join(f"{status} {count}" for status, count in status_counter.most_common(3))
            summary += f"; statuses: {top_statuses}"
        samples = [
            summarize_object_inline(
                item,
                context_key=singularize(key),
                depth=depth + 1,
                max_depth=max_depth,
                max_samples=max_samples,
                max_string_len=max_string_len,
            )
            for item in items[:max_samples]
        ]
        if samples:
            summary += f"; examples: {join_naturally(samples)}"
        summary += "."
        return summary

    if all(is_scalar(item) for item in items):
        sample_text = sample_scalar_list(items, max_samples, max_string_len)
        summary = f"{len(items)} total"
        if sample_text:
            summary += f"; values: {sample_text}"
        summary += "."
        return summary

    samples = [
        summarize_value_inline(
            item,
            context_key=singularize(key),
            depth=depth + 1,
            max_depth=max_depth,
            max_samples=max_samples,
            max_string_len=max_string_len,
        )
        for item in items[:max_samples]
    ]
    summary = f"{len(items)} total"
    if samples:
        summary += f"; examples: {join_naturally(samples)}"
    summary += "."
    return summary


def summarize_value_inline(
    value: Any,
    *,
    context_key: str | None,
    depth: int,
    max_depth: int,
    max_samples: int,
    max_string_len: int,
) -> str:
    if value is None:
        return "null"
    if is_scalar(value):
        return format_scalar(value, max_string_len, quote_strings=False)
    if isinstance(value, list):
        return summarize_array(
            context_key or "items",
            value,
            depth=depth,
            max_depth=max_depth,
            max_samples=max_samples,
            max_string_len=max_string_len,
        )
    if isinstance(value, dict):
        if not value:
            return "empty object"
        if depth >= max_depth:
            compact = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
            return truncate_string(compact, max_string_len)
        return summarize_object_inline(
            value,
            context_key=context_key,
            depth=depth,
            max_depth=max_depth,
            max_samples=max_samples,
            max_string_len=max_string_len,
        )
    return str(value)


def summarize_fields(
    obj: dict[str, Any],
    *,
    path: tuple[str, ...],
    depth: int,
    max_depth: int,
    max_samples: int,
    max_string_len: int,
    inline: bool,
) -> list[str]:
    phrases: list[str] = []
    consumed: set[str] = set()
    header_name = extract_display_name(obj, max_string_len)
    if header_name is not None:
        consumed.update({key for key in DISPLAY_NAME_KEYS if obj.get(key) == header_name})
    if extract_identifier(obj) is not None:
        consumed.add("id")

    for field_key, verify_key in PAIR_FIELDS:
        value = obj.get(field_key)
        verify_value = obj.get(verify_key)
        if isinstance(value, str) and isinstance(verify_value, bool):
            if header_name is not None and field_key in DISPLAY_NAME_KEYS and value == header_name:
                consumed.update({field_key, verify_key})
                continue
            verification = "verified" if verify_value else "unverified"
            if inline:
                phrases.append(f"{humanize_key(field_key)} {truncate_string(value, max_string_len)} ({verification})")
            else:
                phrases.append(
                    attach_paths(
                        f"{sentence_case(humanize_key(field_key))}: {truncate_string(value, max_string_len)} ({verification}).",
                        (*path, field_key),
                        (*path, verify_key),
                    )
                )
            consumed.update({field_key, verify_key})

    for key, value in sorted(obj.items(), key=sort_key):
        if key in consumed:
            continue

        if value is None:
            phrases.append(
                f"{humanize_key(key)}: null"
                if inline
                else attach_paths(f"{sentence_case(humanize_key(key))}: null.", (*path, key))
            )
            continue

        if isinstance(value, bool):
            phrase = bool_phrase(key, value)
            if phrase:
                phrases.append(phrase if inline else naturalize_bool_phrase(phrase))
            continue

        if isinstance(value, str) and value == "":
            phrases.append(
                f"{humanize_key(key)}: empty string"
                if inline
                else attach_paths(f"{sentence_case(humanize_key(key))}: empty string.", (*path, key))
            )
            continue

        if is_scalar(value):
            phrases.append(
                f"{humanize_key(key)}: {format_scalar(value, max_string_len, quote_strings=False)}"
                if inline
                else attach_paths(naturalize_scalar_field(key, value, max_string_len), (*path, key))
            )
            continue

        if isinstance(value, dict):
            if not value:
                phrases.append(
                    f"{humanize_key(key)}: empty object"
                    if inline
                    else attach_paths(f"{sentence_case(humanize_key(key))}: empty object.", (*path, key))
                )
                continue
            phrase = summarize_value_inline(
                value,
                context_key=key,
                depth=depth + 1,
                max_depth=max_depth,
                max_samples=max_samples,
                max_string_len=max_string_len,
            )
            if inline:
                phrases.append(f"{humanize_key(key)}: {phrase}")
            else:
                clean_phrase = strip_terminal_period(phrase)
                key_label = sentence_case(humanize_key(key))
                if clean_phrase.startswith(f"{key_label}:") or clean_phrase.startswith(f"{key_label}["):
                    phrases.append(attach_paths(f"{clean_phrase}.", (*path, key)))
                else:
                    phrases.append(attach_paths(f"{key_label}: {clean_phrase}.", (*path, key)))
            continue

        if isinstance(value, list):
            if not value:
                phrases.append(
                    f"{humanize_key(key)}: 0 total"
                    if inline
                    else attach_paths(f"{sentence_case(humanize_key(key))}: 0 total.", (*path, key))
                )
                continue
            phrase = summarize_array(
                key,
                value,
                depth=depth + 1,
                max_depth=max_depth,
                max_samples=max_samples,
                max_string_len=max_string_len,
            )
            if inline:
                phrases.append(f"{humanize_key(key)}: {phrase}")
            else:
                phrases.append(attach_paths(f"{sentence_case(humanize_key(key))}: {strip_terminal_period(phrase)}.", (*path, key)))

    return phrases if inline else [f"- {phrase}" for phrase in phrases]


def make_expanded_detail_lines(
    key: str,
    value: dict[str, Any],
    *,
    path: tuple[str, ...],
    depth: int,
    max_depth: int,
    max_samples: int,
    max_string_len: int,
) -> list[str]:
    if depth >= max_depth or not value:
        return []
    lines: list[str] = []
    header = make_header(value, key, max_string_len)
    if header not in GENERIC_ENTITY_NAMES:
        lines.append(f"  - {attach_paths(header, (*path, key))}")
    nested = summarize_fields(
        value,
        path=(*path, key),
        depth=depth + 1,
        max_depth=max_depth,
        max_samples=max_samples,
        max_string_len=max_string_len,
        inline=False,
    )
    visible = nested[: max(2, max_samples)]
    lines.extend(f"  {line}" for line in visible)
    remaining = len(nested) - len(visible)
    if remaining > 0:
        lines.append(f"  - More details omitted: {remaining}.")
    return lines


def make_expanded_collection_lines(
    key: str,
    items: list[Any],
    *,
    path: tuple[str, ...],
    depth: int,
    max_depth: int,
    max_samples: int,
    max_string_len: int,
) -> list[str]:
    if not items:
        return []
    lines: list[str] = []
    for index, item in enumerate(items[:max_samples]):
        item_path = (*path, f"{key}[{index}]")
        if isinstance(item, dict):
            lines.append(
                f"  - {attach_paths(summarize_object_inline(item, context_key=singularize(key), depth=depth + 1, max_depth=max_depth, max_samples=max_samples, max_string_len=max_string_len) + '.', item_path)}"
            )
        elif item is None:
            lines.append(f"  - {attach_paths('null', item_path)}")
        elif is_scalar(item):
            lines.append(f"  - {attach_paths(format_scalar(item, max_string_len, quote_strings=False), item_path)}")
        else:
            lines.append(
                f"  - {attach_paths(summarize_value_inline(item, context_key=singularize(key), depth=depth + 1, max_depth=max_depth, max_samples=max_samples, max_string_len=max_string_len) + '.', item_path)}"
            )
    if len(items) > max_samples:
        lines.append(f"  - {attach_paths(f'More items omitted: {len(items) - max_samples}.', (*path, key))}")
    return lines


def section_priority(key: str, value: Any) -> str:
    if isinstance(value, list):
        return "Collections"
    if isinstance(value, bool):
        return "Summary"
    if key in SUMMARY_PREFERRED_KEYS:
        return "Summary"
    if is_scalar(value) and key in IMPORTANT_KEYS:
        return "Summary"
    return "Details"


def summarize_sections(
    obj: dict[str, Any],
    *,
    path: tuple[str, ...],
    depth: int,
    max_depth: int,
    max_samples: int,
    max_string_len: int,
) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {"Summary": [], "Details": [], "Collections": []}
    consumed: set[str] = set()
    header_name = extract_display_name(obj, max_string_len)
    if header_name is not None:
        consumed.update({key for key in DISPLAY_NAME_KEYS if obj.get(key) == header_name})
    if extract_identifier(obj) is not None:
        consumed.add("id")

    for field_key, verify_key in PAIR_FIELDS:
        value = obj.get(field_key)
        verify_value = obj.get(verify_key)
        if isinstance(value, str) and isinstance(verify_value, bool):
            verification = "verified" if verify_value else "unverified"
            sections["Summary"].append(
                f"- {attach_paths(f'{sentence_case(humanize_key(field_key))}: {truncate_string(value, max_string_len)} ({verification}).', (*path, field_key), (*path, verify_key))}"
            )
            consumed.update({field_key, verify_key})

    for key, value in sorted(obj.items(), key=sort_key):
        if key in consumed:
            continue

        bucket = section_priority(key, value)

        if isinstance(value, bool):
            phrase = bool_phrase(key, value)
            if phrase:
                sections[bucket].append(f"- {attach_paths(naturalize_bool_phrase(phrase), (*path, key))}")
            continue

        if is_scalar(value):
            sections[bucket].append(f"- {attach_paths(naturalize_scalar_field(key, value, max_string_len), (*path, key))}")
            continue

        if isinstance(value, dict):
            phrase = summarize_value_inline(
                value,
                context_key=key,
                depth=depth + 1,
                max_depth=max_depth,
                max_samples=max_samples,
                max_string_len=max_string_len,
            )
            clean_phrase = strip_terminal_period(phrase)
            key_label = sentence_case(humanize_key(key))
            if clean_phrase.startswith(f"{key_label}:") or clean_phrase.startswith(f"{key_label}["):
                sections[bucket].append(f"- {attach_paths(f'{clean_phrase}.', (*path, key))}")
            else:
                sections[bucket].append(f"- {attach_paths(f'{key_label}: {clean_phrase}.', (*path, key))}")
            if bucket == "Details" and should_expand("details"):
                sections[bucket].extend(
                    make_expanded_detail_lines(
                        key,
                        value,
                        path=path,
                        depth=depth,
                        max_depth=max_depth,
                        max_samples=max_samples,
                        max_string_len=max_string_len,
                    )
                )
            continue

        if isinstance(value, list):
            phrase = summarize_array(
                key,
                value,
                depth=depth + 1,
                max_depth=max_depth,
                max_samples=max_samples,
                max_string_len=max_string_len,
            )
            sections[bucket].append(f"- {attach_paths(f'{sentence_case(humanize_key(key))}: {strip_terminal_period(phrase)}.', (*path, key))}")
            if bucket == "Collections" and should_expand("collections"):
                sections[bucket].extend(
                    make_expanded_collection_lines(
                        key,
                        value,
                        path=path,
                        depth=depth,
                        max_depth=max_depth,
                        max_samples=max_samples,
                        max_string_len=max_string_len,
                    )
                )

    return {name: lines for name, lines in sections.items() if lines}


def render_sections(sections: dict[str, list[str]]) -> list[str]:
    lines: list[str] = []
    for section_name in ("Summary", "Details", "Collections"):
        section_lines = sections.get(section_name)
        if not section_lines:
            continue
        if lines:
            lines.append("")
        lines.append(section_name)
        lines.extend(section_lines)
    return lines


def render_flat_object(
    obj: dict[str, Any],
    *,
    max_depth: int,
    max_samples: int,
    max_string_len: int,
) -> list[str]:
    lines = summarize_fields(
        obj,
        path=(),
        depth=0,
        max_depth=max_depth,
        max_samples=max_samples,
        max_string_len=max_string_len,
        inline=False,
    )
    if not OPTIONS.expand:
        return lines

    expanded_lines: list[str] = []
    for key, value in sorted(obj.items(), key=sort_key):
        if isinstance(value, dict) and should_expand("details"):
            expanded_lines.extend(
                make_expanded_detail_lines(
                    key,
                    value,
                    path=(),
                    depth=0,
                    max_depth=max_depth,
                    max_samples=max_samples,
                    max_string_len=max_string_len,
                )
            )
        elif isinstance(value, list) and should_expand("collections"):
            expanded_lines.extend(
                make_expanded_collection_lines(
                    key,
                    value,
                    path=(),
                    depth=0,
                    max_depth=max_depth,
                    max_samples=max_samples,
                    max_string_len=max_string_len,
                )
            )
    return lines + expanded_lines


def summarize_root(
    data: Any,
    *,
    style: str,
    max_depth: int,
    max_samples: int,
    max_string_len: int,
) -> str:
    cleaned = prune(data)
    if cleaned is _EMPTY:
        return "No meaningful content."

    if isinstance(cleaned, dict):
        header = make_header(cleaned, None, max_string_len)
        if header in GENERIC_ENTITY_NAMES:
            header = "Context"
        lines = [attach_paths(header, ())]
        if style == "flat":
            lines.extend(
                render_flat_object(
                    cleaned,
                    max_depth=max_depth,
                    max_samples=max_samples,
                    max_string_len=max_string_len,
                )
            )
        else:
            sections = summarize_sections(
                cleaned,
                path=(),
                depth=0,
                max_depth=max_depth,
                max_samples=max_samples,
                max_string_len=max_string_len,
            )
            lines.extend(render_sections(sections))
        return "\n".join(lines)

    if isinstance(cleaned, list):
        if not cleaned:
            if style == "flat":
                return "\n".join([attach_paths("Items", ()), f"- {attach_paths('Count: 0 total.', ())}"])
            return "\n".join([attach_paths("Items", ()), "", "Summary", f"- {attach_paths('Count: 0 total.', ())}"])
        if all(isinstance(item, dict) for item in cleaned):
            entity_type = detect_entity_type(cleaned[0], "items")
            header = titleize(pluralize(entity_type, len(cleaned)))
            summary_line = summarize_array(
                entity_type.lower(),
                cleaned,
                depth=0,
                max_depth=max_depth,
                max_samples=max_samples,
                max_string_len=max_string_len,
            )
            if style == "flat":
                lines = [
                    attach_paths(header, ()),
                    f"- {attach_paths(f'Count: {len(cleaned)} total.', ())}",
                    f"- {attach_paths(f'{header}: {strip_terminal_period(summary_line)}.', ())}",
                ]
            else:
                lines = [attach_paths(header, ()), "", "Summary", f"- {attach_paths(f'Count: {len(cleaned)} total.', ())}"]
                lines.extend(["", "Collections", f"- {attach_paths(f'{header}: {strip_terminal_period(summary_line)}.', ())}"])
            if len(cleaned) > max_samples:
                lines.append(f"- {attach_paths(f'More omitted: {len(cleaned) - max_samples}.', ())}")
            return "\n".join(lines)

        summary = summarize_array(
            "items",
            cleaned,
            depth=0,
            max_depth=max_depth,
            max_samples=max_samples,
            max_string_len=max_string_len,
        )
        if style == "flat":
            return "\n".join([attach_paths("Items", ()), f"- {attach_paths(f'{strip_terminal_period(summary)}.', ())}"])
        return "\n".join([attach_paths("Items", ()), "", "Summary", f"- {attach_paths(f'{strip_terminal_period(summary)}.', ())}"])

    return format_scalar(cleaned, max_string_len, quote_strings=False)


def main() -> None:
    args = parse_args()
    configure_options(args)
    payload = load_payload(args.input)
    output = summarize_root(
        payload,
        style=args.style,
        max_depth=max(1, args.max_depth),
        max_samples=max(1, args.max_samples),
        max_string_len=max(16, args.max_string_len),
    )
    write_output(output, args.output)


if __name__ == "__main__":
    main()
