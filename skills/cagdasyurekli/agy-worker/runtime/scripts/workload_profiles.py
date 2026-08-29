#!/usr/bin/env python3
"""Render fixed data-only workload profiles without dispatch or policy authority."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import stat
import sys
from typing import Any


MAX_FILE_BYTES = 16 * 1024
MANIFEST_FIELDS = {"kind", "profiles", "schema_version", "source_revision"}
ENTRY_FIELDS = {"file", "name", "sha256"}
PROFILE_FIELDS = {
    "authority", "caller_required", "kind", "name", "non_executable",
    "path_policy_shape", "schema_version", "summary", "suggested_mode",
    "suggested_persona",
}
REQUIRED_INPUTS = [
    "approval", "exact-repository", "path-policy", "selected-tier",
    "verification-commands",
]
NO_AUTHORITY = {
    "acceptance": False,
    "authorization": False,
    "dispatch": False,
    "routing": False,
}
EXPECTED = {
    "bounded-test-backfill": {
        "file": "bounded-test-backfill.json",
        "mode": "accept-edits",
        "path_policy_shape": "caller-declared-repo-relative-subtrees",
        "persona": "bulk-test-writer",
        "sha256": "cf7cb8b95bac318da6c60a49fc388e7bf8723f648e8ac4dc3b3396d57bc4bc75",
        "summary": "Prepare a bounded test backfill only inside caller-declared repository subtrees.",
    },
    "diff-review": {
        "file": "diff-review.json",
        "mode": "plan",
        "path_policy_shape": "caller-declared-repo-relative-paths",
        "persona": "diff-reviewer",
        "sha256": "5774915afe58fb4eddb0f44dddad8d777169133195cb0f1e5a05070bd331120a",
        "summary": "Review only caller-declared repository paths with the maintained read-only diff persona.",
    },
    "repository-inventory": {
        "file": "repository-inventory.json",
        "mode": "plan",
        "path_policy_shape": "caller-declared-repo-relative-subtrees",
        "persona": "repo-inventory",
        "sha256": "354889901d6e47b95f4dac8316758999262f11fd713bd7f23214177cc54da8e2",
        "summary": "Inspect only caller-declared repository subtrees with the maintained read-only inventory persona.",
    },
}
SCHEMA_SHA256 = "4bab51bd97158a53fce0cd08cfd8949405106236e94e54ede9371239510afbdf"


class ProfileError(ValueError):
    pass


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=True, sort_keys=True, separators=(",", ":")
    ).encode("ascii") + b"\n"


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ProfileError("duplicate JSON key")
        result[key] = value
    return result


def parse_canonical(data: bytes) -> Any:
    try:
        value = json.loads(data.decode("utf-8", "strict"), object_pairs_hook=_pairs)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProfileError("invalid JSON") from exc
    if canonical_bytes(value) != data:
        raise ProfileError("non-canonical JSON")
    return value


def _real_directory(path: Path, label: str) -> Path:
    try:
        metadata = path.lstat()
    except OSError as exc:
        raise ProfileError(f"{label} is unavailable") from exc
    if not stat.S_ISDIR(metadata.st_mode) or stat.S_ISLNK(metadata.st_mode):
        raise ProfileError(f"{label} is invalid")
    if stat.S_IMODE(metadata.st_mode) & 0o022:
        raise ProfileError(f"{label} is writable")
    if Path(os.path.realpath(path)) != path:
        raise ProfileError(f"{label} is not canonical")
    return path


def _read_data(path: Path, label: str) -> bytes:
    try:
        descriptor = os.open(
            path,
            os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0),
        )
    except OSError as exc:
        raise ProfileError(f"{label} is unavailable") from exc
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode):
            raise ProfileError(f"{label} is not a regular file")
        if stat.S_IMODE(metadata.st_mode) != 0o644:
            raise ProfileError(f"{label} mode is invalid")
        if metadata.st_size > MAX_FILE_BYTES:
            raise ProfileError(f"{label} is oversized")
        data = os.read(descriptor, MAX_FILE_BYTES + 1)
        if len(data) != metadata.st_size or os.read(descriptor, 1) != b"":
            raise ProfileError(f"{label} changed while read")
        return data
    finally:
        os.close(descriptor)


def _validate_profile(value: Any, name: str) -> dict[str, Any]:
    expected = EXPECTED[name]
    if not isinstance(value, dict) or set(value) != PROFILE_FIELDS:
        raise ProfileError("profile shape is invalid")
    if (
        value["schema_version"] != 1
        or value["kind"] != "agy-worker-workload-profile"
        or value["name"] != name
        or value["summary"] != expected["summary"]
        or value["suggested_mode"] != expected["mode"]
        or value["suggested_persona"] != expected["persona"]
        or value["path_policy_shape"] != expected["path_policy_shape"]
        or value["caller_required"] != REQUIRED_INPUTS
        or value["non_executable"] is not True
        or value["authority"] != NO_AUTHORITY
    ):
        raise ProfileError("profile policy is invalid")
    return value


def load_profiles(runtime: Path | None = None) -> dict[str, dict[str, Any]]:
    if runtime is None:
        runtime = Path(__file__).resolve(strict=True).parent.parent
    runtime = _real_directory(runtime, "runtime")
    profiles_parent = _real_directory(runtime / "profiles", "profiles parent")
    version_root = _real_directory(profiles_parent / "v1", "profiles version")
    schema_parent = _real_directory(runtime / "schemas", "schemas parent")
    schema = _read_data(schema_parent / "workload-profile.schema.json", "profile schema")
    if hashlib.sha256(schema).hexdigest() != SCHEMA_SHA256:
        raise ProfileError("profile schema digest is invalid")

    allowed = {"manifest.json"} | {entry["file"] for entry in EXPECTED.values()}
    try:
        actual = set(os.listdir(version_root))
    except OSError as exc:
        raise ProfileError("profile inventory is unavailable") from exc
    if actual != allowed:
        raise ProfileError("profile inventory is invalid")

    manifest_data = _read_data(version_root / "manifest.json", "profile manifest")
    manifest = parse_canonical(manifest_data)
    if (
        not isinstance(manifest, dict)
        or set(manifest) != MANIFEST_FIELDS
        or manifest["schema_version"] != 1
        or manifest["kind"] != "agy-worker-workload-profile-manifest"
        or manifest["source_revision"] != "workload-profiles-v1"
        or not isinstance(manifest["profiles"], list)
        or len(manifest["profiles"]) != len(EXPECTED)
    ):
        raise ProfileError("profile manifest is invalid")

    records: dict[str, dict[str, Any]] = {}
    names: list[str] = []
    for entry in manifest["profiles"]:
        if not isinstance(entry, dict) or set(entry) != ENTRY_FIELDS:
            raise ProfileError("profile manifest entry is invalid")
        name = entry.get("name")
        if not isinstance(name, str) or name not in EXPECTED or name in records:
            raise ProfileError("profile manifest name is invalid")
        expected = EXPECTED[name]
        if entry != {
            "file": expected["file"], "name": name, "sha256": expected["sha256"]
        }:
            raise ProfileError("profile manifest binding is invalid")
        data = _read_data(version_root / expected["file"], "profile data")
        if hashlib.sha256(data).hexdigest() != expected["sha256"]:
            raise ProfileError("profile digest is invalid")
        records[name] = _validate_profile(parse_canonical(data), name)
        names.append(name)
    if names != sorted(EXPECTED):
        raise ProfileError("profile order is invalid")
    return records


def main(argv: list[str]) -> int:
    if argv == ["list"]:
        records = load_profiles()
        value = {
            "kind": "agy-worker-workload-profile-list",
            "profiles": [
                {"name": name, "summary": records[name]["summary"]}
                for name in sorted(records)
            ],
            "schema_version": 1,
        }
    elif len(argv) == 2 and argv[0] == "show" and argv[1] in EXPECTED:
        value = load_profiles()[argv[1]]
    else:
        sys.stderr.write("profile: invalid arguments\n")
        return 64
    sys.stdout.buffer.write(canonical_bytes(value))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except ProfileError:
        sys.stderr.write("profile: bundled profiles are invalid\n")
        raise SystemExit(2)
