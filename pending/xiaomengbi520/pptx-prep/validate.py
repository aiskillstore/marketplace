"""Validate a pptx-prep manifest file.

Usage: python validate.py <manifest_file>

Supports both YAML (.yml/.yaml) and JSON (.json) files.
YAML parsing is built in — no external dependencies required.
For YAML: uses full-featured pyyaml if available; otherwise falls back to
the built-in minimal parser which handles the pptx-prep manifest subset.

Exit code: 0 = valid, 1 = validation errors found.
"""

import json
import re
import sys
from pathlib import Path


VALID_STATUSES = {"ready", "placeholder"}
VALID_SOURCES = {"ai", "ai-search", "ai-generated", "user"}
VALID_CONFIDENCES = {"verified", "needs-review", "placeholder"}
VALID_TYPES = {"photo", "text", "data", "branding", "reference"}
VALID_FORMATS = {"currency_cny", "percentage", "integer", "plain_text"}
VALID_FILL_MODES = {"contain", "cover"}
VALID_WARNING_TYPES = {"overflow", "low_quality", "aspect_mismatch", "wrong_type"}


def load_manifest(path: Path) -> dict | None:
    """Load manifest from YAML or JSON file."""
    suffix = path.suffix.lower()

    if suffix in (".yml", ".yaml"):
        try:
            import yaml
            with open(path, encoding="utf-8") as f:
                return yaml.safe_load(f)
        except ImportError:
            pass

        with open(path, encoding="utf-8") as f:
            content = f.read()

        manifest = _parse_yaml(content)
        if manifest is None:
            print("Error: YAML parsing failed. Try installing pyyaml: pip install pyyaml")
        return manifest

    if suffix == ".json":
        return _load_json(path)

    print(f"Error: Unknown file extension '{suffix}'. Use .yml, .yaml, or .json.")
    return None


def _load_json(path: Path) -> dict | None:
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}")
        return None


def _parse_yaml(text: str):
    """Minimal YAML parser for pptx-prep manifest format.

    Handles: key: value, nested objects (indentation), lists (- item),
    quoted strings, integers, floats, comments (#). Does NOT handle:
    multi-line strings, anchors, tags, flow collections, complex edge cases.
    """
    lines = text.split("\n")
    return _parse_block([l for l in lines if l.strip() and not l.strip().startswith("#")])


def _parse_block(lines: list[str], indent: int = 0) -> dict | list | str | int | float | None:
    """Parse a block of YAML lines at the given indentation level."""
    if not lines:
        return None

    # Check if this is a list (first non-empty line starts with "- ")
    first_stripped = lines[0].lstrip()
    is_list = first_stripped.startswith("- ")

    if is_list:
        return _parse_list(lines, indent)

    return _parse_dict(lines, indent)


def _parse_list(lines: list[str], indent: int) -> list:
    """Parse a YAML list."""
    result = []
    i = 0

    while i < len(lines):
        stripped = lines[i].lstrip()
        line_indent = len(lines[i]) - len(stripped)

        if line_indent < indent:
            break

        if not stripped.startswith("- "):
            i += 1
            continue

        value_part = stripped[2:]

        # Check if the next lines are more indented (nested block)
        nested_lines = []
        j = i + 1
        while j < len(lines):
            ns = lines[j].lstrip()
            n_indent = len(lines[j]) - len(ns)
            if n_indent <= line_indent or (n_indent == line_indent and not ns.startswith("- ")):
                break
            nested_lines.append(lines[j])
            j += 1

        if nested_lines and nested_lines[0].lstrip().startswith("- "):
            # Sublist
            result.append(_parse_list(nested_lines, line_indent + 2))
        elif nested_lines:
            # Nested dict — combine with the "- key: value" prefix
            nested = _parse_dict(nested_lines, line_indent + 2)
            if ":" in value_part and _is_inline_dict(value_part):
                prefix = _parse_inline_dict(value_part)
                prefix.update(nested)
                result.append(prefix)
            else:
                result.append(nested)
        elif ":" in value_part and _is_inline_dict(value_part):
            # Inline key: value after "- "
            result.append(_parse_inline_dict(value_part))
        else:
            result.append(_parse_value(value_part))

        i = j
        if not nested_lines:
            i += 1

    return result


def _parse_dict(lines: list[str], indent: int) -> dict:
    """Parse a YAML dict."""
    result = {}
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.lstrip()
        line_indent = len(line) - len(stripped)

        if line_indent < indent or stripped.startswith("- "):
            break

        if ":" not in stripped and not stripped.startswith("#"):
            i += 1
            continue

        key_end = stripped.index(":") if ":" in stripped else len(stripped)
        key = stripped[:key_end].strip()
        value_part = stripped[key_end + 1:].lstrip()

        if value_part == "" or value_part == "|" or value_part == ">":
            # Nested block (next indented lines)
            nested_lines = []
            j = i + 1
            while j < len(lines):
                ns = lines[j].lstrip()
                n_indent = len(lines[j]) - len(ns)
                if n_indent <= line_indent:
                    break
                nested_lines.append(lines[j])
                j += 1

            if nested_lines:
                result[key] = _parse_block(nested_lines, line_indent + 2)
            i = j
        else:
            result[key] = _parse_value(value_part)
            i += 1

    return result


def _is_inline_dict(value: str) -> bool:
    """Check if a value looks like an inline dict: key1: val1, key2: val2"""
    return ":" in value and not value.startswith('"') and not value.startswith("'") and len(value) < 120


def _parse_inline_dict(value: str) -> dict:
    """Parse a simple inline dict like 'key1: val1, key2: val2'."""
    result = {}
    # Split by comma, but be careful
    parts = value.split(", ")
    for part in parts:
        if ":" in part:
            k, v = part.split(":", 1)
            result[k.strip()] = _parse_value(v.strip())
    return result


def _parse_value(value: str):
    """Parse a scalar YAML value or inline array."""
    value = value.strip()

    # Remove inline comment
    if " #" in value:
        value = value[: value.index(" #")]

    # Inline arrays: [item1, item2] or [slide-1]
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        items = []
        for item in inner.split(","):
            items.append(_parse_value(item.strip()))
        return items

    # Booleans
    if value.lower() in ("true", "yes", "on"):
        return True
    if value.lower() in ("false", "no", "off"):
        return False
    if value.lower() in ("null", "~", ""):
        return None

    # Quoted strings
    if (value.startswith('"') and value.endswith('"')) or \
       (value.startswith("'") and value.endswith("'")):
        return value[1:-1]

    # Integers
    if re.match(r"^-?\d+$", value):
        return int(value)

    # Floats
    if re.match(r"^-?\d+\.\d+$", value):
        return float(value)

    return value


def validate(manifest: dict) -> list[str]:
    """Validate manifest structure. Returns list of error messages (empty = valid)."""
    errors = []

    # Top-level required keys
    for key in ("manifest_version", "project", "materials", "summary"):
        if key not in manifest:
            errors.append(f"Missing required top-level key: '{key}'")

    if "manifest_version" in manifest and manifest["manifest_version"] != "1.0":
        errors.append(f"Unknown manifest_version: '{manifest['manifest_version']}'. Expected '1.0'.")

    # Project
    project = manifest.get("project", {})
    if not isinstance(project, dict):
        errors.append("'project' must be an object.")
    else:
        if "title" not in project:
            errors.append("Missing 'project.title'.")
        if "slide_count" not in project:
            errors.append("Missing 'project.slide_count'.")
        elif not isinstance(project["slide_count"], int) or project["slide_count"] < 1:
            errors.append(f"'project.slide_count' must be a positive integer, got: {project['slide_count']}")

    # Materials
    materials = manifest.get("materials", [])
    if not isinstance(materials, list):
        errors.append("'materials' must be an array.")
    else:
        seen_fields = set()
        for i, mat in enumerate(materials):
            prefix = f"materials[{i}]"
            if not isinstance(mat, dict):
                errors.append(f"{prefix}: must be an object.")
                continue

            for key in ("field", "type", "description", "used_in", "status", "source", "confidence"):
                if key not in mat:
                    errors.append(f"{prefix}: missing required key '{key}'.")

            field = mat.get("field", "")
            if field in seen_fields:
                errors.append(f"{prefix}: duplicate 'field' value '{field}'.")
            seen_fields.add(field)

            if mat.get("type") not in VALID_TYPES:
                errors.append(f"{prefix}: invalid type '{mat.get('type')}'. Must be one of: {VALID_TYPES}")

            if mat.get("status") not in VALID_STATUSES:
                errors.append(f"{prefix}: invalid status '{mat.get('status')}'. Must be one of: {VALID_STATUSES}")

            if mat.get("source") not in VALID_SOURCES:
                errors.append(f"{prefix}: invalid source '{mat.get('source')}'. Must be one of: {VALID_SOURCES}")

            if mat.get("confidence") not in VALID_CONFIDENCES:
                errors.append(f"{prefix}: invalid confidence '{mat.get('confidence')}'. Must be one of: {VALID_CONFIDENCES}")

            used_in = mat.get("used_in", [])
            if isinstance(used_in, list):
                for j, slide_ref in enumerate(used_in):
                    if not isinstance(slide_ref, str) or not slide_ref.startswith("slide-"):
                        errors.append(f"{prefix}.used_in[{j}]: must be 'slide-N' format, got '{slide_ref}'.")
            else:
                errors.append(f"{prefix}: 'used_in' must be an array.")

            if mat.get("status") == "ready" and mat.get("type") == "photo" and "path" not in mat:
                errors.append(f"{prefix}: status is 'ready' and type is 'photo' but no 'path' provided.")

            slot = mat.get("slot")
            if slot and isinstance(slot, dict):
                fm = slot.get("fill_mode")
                if fm and fm not in VALID_FILL_MODES:
                    errors.append(f"{prefix}.slot.fill_mode: must be 'contain' or 'cover', got '{fm}'.")

                capacity = slot.get("estimated_capacity")
                if capacity is not None and (not isinstance(capacity, int) or capacity < 0):
                    errors.append(f"{prefix}.slot.estimated_capacity: must be a non-negative integer, got '{capacity}'.")

            fmt = mat.get("format")
            if fmt and fmt not in VALID_FORMATS:
                errors.append(f"{prefix}: invalid format '{fmt}'. Must be one of: {VALID_FORMATS}")

            warnings = mat.get("warnings")
            if warnings:
                if not isinstance(warnings, list):
                    errors.append(f"{prefix}: 'warnings' must be an array.")
                else:
                    for j, w in enumerate(warnings):
                        if isinstance(w, dict) and w.get("type") not in VALID_WARNING_TYPES:
                            errors.append(f"{prefix}.warnings[{j}]: invalid warning type '{w.get('type')}'.")

    # Summary
    summary = manifest.get("summary", {})
    if not isinstance(summary, dict):
        errors.append("'summary' must be an object.")
    else:
        for key in ("total", "ready", "placeholder", "needs_review"):
            if key not in summary:
                errors.append(f"Missing 'summary.{key}'.")
            elif not isinstance(summary[key], int):
                errors.append(f"'summary.{key}' must be an integer, got: {summary[key]}")

        # Cross-validate summary vs materials
        if materials and all(isinstance(m, dict) for m in materials):
            actual = {
                "total": len(materials),
                "ready": sum(1 for m in materials if m.get("status") == "ready"),
                "placeholder": sum(1 for m in materials if m.get("status") == "placeholder"),
                "needs_review": sum(1 for m in materials if m.get("confidence") == "needs-review"),
            }
            for k, expected in actual.items():
                reported = summary.get(k)
                if reported is not None and reported != expected:
                    errors.append(f"summary.{k}: reported {reported}, but materials count is {expected}.")

    return errors


def main():
    if len(sys.argv) != 2:
        print("Usage: python validate.py <manifest_file>")
        print("  manifest_file: .yml, .yaml, or .json")
        sys.exit(1)

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"Error: File not found: {path}")
        sys.exit(1)

    manifest = load_manifest(path)
    if manifest is None:
        sys.exit(1)

    errors = validate(manifest)

    if errors:
        print(f"\nValidation FAILED — {len(errors)} error(s):\n")
        for e in errors:
            print(f"  - {e}")
        print()
        sys.exit(1)
    else:
        print(f"\nValidation PASSED — {len(manifest.get('materials', []))} materials, all checks passed.\n")
        sys.exit(0)


if __name__ == "__main__":
    main()
