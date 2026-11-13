#!/usr/bin/env python3
"""Check a .cube LUT against a user-supplied, source-backed camera profile."""

from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import date
from pathlib import Path
from typing import Any

from validate_lut import parse_cube


PROFILE_TEMPLATE: dict[str, Any] = {
    "schema_version": 1,
    "device": "Enter manufacturer and model",
    "verified": False,
    "verification_date": None,
    "sources": [],
    "accepted_formats": [],
    "allowed_3d_sizes": [],
    "max_file_bytes": None,
    "expected_input_space": None,
    "expected_input_transfer": None,
    "supported_lumix_photo_styles": [],
    "check_full_range_domain": False,
    "card_filesystems": {},
}


def normalize(value: str) -> str:
    return "".join(character.lower() for character in value if character.isalnum())


def read_cube_metadata(path: Path) -> dict[str, str]:
    metadata: dict[str, str] = {}
    with path.open("r", encoding="utf-8-sig") as handle:
        for raw in handle:
            line = raw.strip()
            if not line.startswith("#"):
                continue
            lumix_style = line.split()
            if len(lumix_style) == 2 and lumix_style[0].upper() == "#LUMIXPHOTOSTYLE":
                metadata["lumix_photo_style"] = lumix_style[1].upper()
                continue
            if ":" not in line:
                continue
            key, value = line[1:].split(":", 1)
            if key.strip().lower() in {"source", "target"}:
                metadata[key.strip().lower()] = value.strip()
    return metadata


def read_cube_domain(path: Path) -> tuple[tuple[float, float, float], tuple[float, float, float], set[str]]:
    domain_min = (0.0, 0.0, 0.0)
    domain_max = (1.0, 1.0, 1.0)
    declared: set[str] = set()
    with path.open("r", encoding="utf-8-sig") as handle:
        for line_number, raw in enumerate(handle, 1):
            line = raw.strip()
            upper = line.upper()
            if upper.startswith("DOMAIN_MIN") or upper.startswith("DOMAIN_MAX"):
                parts = line.split()
                if len(parts) != 4:
                    raise ValueError(f"Line {line_number}: domain header needs three values.")
                try:
                    values = tuple(float(value) for value in parts[1:])
                except ValueError as exc:
                    raise ValueError(f"Line {line_number}: invalid domain value.") from exc
                if not all(math.isfinite(value) for value in values):
                    raise ValueError(f"Line {line_number}: domain contains non-finite values.")
                key = "min" if upper.startswith("DOMAIN_MIN") else "max"
                declared.add(key)
                if key == "min":
                    domain_min = values
                else:
                    domain_max = values
    return domain_min, domain_max, declared


def create_template(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(PROFILE_TEMPLATE, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote unverified camera profile template: {path}")


def load_profile(path: Path) -> dict[str, Any]:
    try:
        profile = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid profile JSON: {exc}") from exc
    if not isinstance(profile, dict) or profile.get("schema_version") != 1:
        raise ValueError("Camera profile must be a JSON object with schema_version 1.")
    device = profile.get("device")
    if not isinstance(device, str) or not device.strip():
        raise ValueError("Camera profile needs a non-empty device name.")
    for key in ("accepted_formats", "allowed_3d_sizes", "sources", "supported_lumix_photo_styles"):
        if key in profile and not isinstance(profile[key], list):
            raise ValueError(f"Camera profile field {key} must be a list.")
    max_bytes = profile.get("max_file_bytes")
    if max_bytes is not None and (not isinstance(max_bytes, int) or max_bytes <= 0):
        raise ValueError("max_file_bytes must be a positive integer or null.")
    if not isinstance(profile.get("card_filesystems", {}), dict):
        raise ValueError("card_filesystems must be an object.")
    return profile


def field_check(name: str, result: str, detail: str) -> dict[str, str]:
    return {"check": name, "result": result, "detail": detail}


def check_lut(lut_path: Path, profile_path: Path, card_filesystem: str | None = None) -> dict[str, Any]:
    profile = load_profile(profile_path)
    checks: list[dict[str, str]] = []
    errors = False
    unresolved = False

    if lut_path.suffix.lower() != ".cube":
        checks.append(field_check("format", "FAIL", "This checker accepts .cube files only."))
        errors = True
        size = None
    else:
        try:
            size, values, _ = parse_cube(lut_path)
            if any(not math.isfinite(channel) for row in values for channel in row):
                raise ValueError("The LUT contains non-finite values.")
            checks.append(field_check("format", "PASS", "Valid 3D .cube structure, entry count, and finite values."))
        except (OSError, ValueError) as exc:
            checks.append(field_check("format", "FAIL", str(exc)))
            errors = True
            size = None

    accepted_formats = [str(value).lower() for value in profile.get("accepted_formats", [])]
    if accepted_formats:
        if ".cube" in accepted_formats:
            checks.append(field_check("device format", "PASS", ".cube appears in the profile."))
        else:
            checks.append(field_check("device format", "FAIL", "The profile does not list .cube as accepted."))
            errors = True
    else:
        checks.append(field_check("device format", "UNKNOWN", "No accepted_formats were verified in the profile."))
        unresolved = True

    allowed_sizes = profile.get("allowed_3d_sizes", [])
    if size is not None and allowed_sizes:
        try:
            normalized_sizes = {int(value) for value in allowed_sizes}
        except (TypeError, ValueError) as exc:
            raise ValueError("allowed_3d_sizes must contain integers.") from exc
        if size in normalized_sizes:
            checks.append(field_check("LUT size", "PASS", f"{size}^3 is listed as supported."))
        else:
            checks.append(field_check("LUT size", "FAIL", f"{size}^3 is not in allowed_3d_sizes."))
            errors = True
    else:
        checks.append(field_check("LUT size", "UNKNOWN", "No supported 3D sizes are configured."))
        unresolved = True

    try:
        file_size = lut_path.stat().st_size
    except OSError:
        file_size = 0
    max_bytes = profile.get("max_file_bytes")
    if max_bytes is not None:
        if file_size <= max_bytes:
            checks.append(field_check("file size", "PASS", f"{file_size} bytes is within the {max_bytes}-byte limit."))
        else:
            checks.append(field_check("file size", "FAIL", f"{file_size} bytes exceeds the {max_bytes}-byte limit."))
            errors = True
    else:
        checks.append(field_check("file size", "NOT SPECIFIED", "The profile does not document a maximum file size."))

    metadata = read_cube_metadata(lut_path) if size is not None else {}
    source = metadata.get("source", "")
    source_parts = [part.strip() for part in source.split("/", 1)] if source else []
    for field, part_index in (("expected_input_space", 0), ("expected_input_transfer", 1)):
        expected = profile.get(field)
        actual = source_parts[part_index] if len(source_parts) > part_index else ""
        if expected:
            expected_norm = normalize(str(expected))
            if not actual:
                checks.append(field_check(field, "UNKNOWN", "The LUT does not declare a matching # Source component."))
                unresolved = True
            elif expected_norm and expected_norm in normalize(actual):
                checks.append(field_check(field, "PASS", f"Declared source component contains {expected}."))
            else:
                checks.append(field_check(field, "FAIL", f"Declared source component does not match {expected}."))
                errors = True
        else:
            checks.append(field_check(field, "NOT CONFIGURED", "This device profile does not specify a single required input encoding."))

    style_options = profile.get("supported_lumix_photo_styles", [])
    if style_options:
        style = metadata.get("lumix_photo_style")
        allowed_styles = {str(value).upper() for value in style_options}
        if style:
            if style in allowed_styles:
                checks.append(field_check("LUMIX Photo Style", "PASS", f"{style} is listed in the camera profile."))
            else:
                checks.append(field_check("LUMIX Photo Style", "FAIL", f"{style} is not listed as supported in the camera profile."))
                errors = True
        elif profile.get("missing_lumix_photo_style_defaults_to"):
            fallback = str(profile["missing_lumix_photo_style_defaults_to"]).upper()
            checks.append(field_check("LUMIX Photo Style", "PASS", f"No explicit tag; camera documentation says this defaults to {fallback}."))
        else:
            checks.append(field_check("LUMIX Photo Style", "UNKNOWN", "No tag is present and the profile gives no default."))
            unresolved = True

    if profile.get("check_full_range_domain"):
        if size is not None:
            try:
                domain_min, domain_max, declared = read_cube_domain(lut_path)
                full_range = all(math.isclose(value, 0.0, abs_tol=1e-9) for value in domain_min) and all(
                    math.isclose(value, 1.0, abs_tol=1e-9) for value in domain_max
                )
                if full_range and declared == {"min", "max"}:
                    checks.append(field_check("LUT range", "PASS", "Explicit DOMAIN_MIN 0 and DOMAIN_MAX 1 are declared."))
                elif full_range:
                    checks.append(field_check("LUT range", "UNKNOWN", "The .cube default domain is 0..1, but both range headers are not explicit."))
                    unresolved = True
                else:
                    checks.append(field_check("LUT range", "WARN", "The camera profile recommends full range; a different domain may display or record incorrectly."))
                    unresolved = True
            except (OSError, ValueError) as exc:
                checks.append(field_check("LUT range", "FAIL", str(exc)))
                errors = True

    card_filesystems = profile.get("card_filesystems", {})
    if card_filesystem:
        filesystem = card_filesystem.upper()
        rule = card_filesystems.get(filesystem)
        if not isinstance(rule, dict):
            checks.append(field_check("card filename", "UNKNOWN", f"No filename rule is configured for {filesystem}."))
            unresolved = True
        else:
            stem = lut_path.stem
            full_name = lut_path.name
            valid = not rule.get("alphanumeric_stem", False) or stem.isalnum()
            limit_key = "max_stem_chars" if filesystem == "FAT32" else "max_name_chars_including_extension"
            measured = len(stem) if limit_key == "max_stem_chars" else len(full_name)
            limit = rule.get(limit_key)
            if valid and isinstance(limit, int) and measured <= limit:
                checks.append(field_check("card filename", "PASS", f"{full_name} meets the {filesystem} naming rule."))
            else:
                checks.append(field_check("card filename", "FAIL", f"Use an alphanumeric name within the documented {filesystem} limit."))
                errors = True
    elif card_filesystems:
        checks.append(field_check("card filename", "NOT CHECKED", "Specify --card-filesystem FAT32 or exFAT to check the SD card filename."))
        unresolved = True

    sources = profile.get("sources", [])
    valid_sources = [value for value in sources if isinstance(value, str) and value.strip()]
    verification_date = profile.get("verification_date")
    date_valid = False
    if isinstance(verification_date, str):
        try:
            date.fromisoformat(verification_date)
            date_valid = True
        except ValueError:
            date_valid = False
    verified = profile.get("verified") is True and bool(valid_sources) and date_valid
    profile_state = "VERIFIED" if verified else "UNVERIFIED"
    if not verified:
        unresolved = True

    if errors:
        status = "INCOMPATIBLE"
    elif verified and not unresolved:
        status = "COMPATIBLE_WITH_DECLARED_PROFILE"
    else:
        status = "UNCONFIRMED"

    return {
        "device": profile["device"],
        "profile_state": profile_state,
        "verification_date": profile.get("verification_date"),
        "profile_sources": sources,
        "lut": str(lut_path),
        "lut_size": size,
        "lut_file_bytes": file_size,
        "status": status,
        "checks": checks,
        "note": "This is a profile-based file check. It does not prove the LUT's visual quality or the accuracy of its color transform.",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check a .cube LUT against a documented camera compatibility profile.")
    parser.add_argument("--lut", help="Path to a 3D .cube LUT.")
    parser.add_argument("--profile", help="Path to a camera profile JSON.")
    parser.add_argument("--create-template", help="Write an unverified profile template JSON and exit.")
    parser.add_argument("--card-filesystem", choices=("FAT32", "exFAT"), help="Check the LUT filename for an SD card formatted with this file system.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.create_template:
        create_template(Path(args.create_template))
        return
    if not args.lut or not args.profile:
        raise SystemExit("Provide both --lut and --profile, or use --create-template.")
    try:
        report = check_lut(Path(args.lut), Path(args.profile), args.card_filesystem)
    except (OSError, ValueError) as exc:
        raise SystemExit(f"Could not check camera compatibility: {exc}") from exc
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if report["status"] == "INCOMPATIBLE":
        sys.exit(1)


if __name__ == "__main__":
    main()
