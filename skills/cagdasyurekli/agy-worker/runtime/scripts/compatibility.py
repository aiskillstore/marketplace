#!/usr/bin/env python3
"""Dependency-free compatibility metadata and model-matrix validation."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any, Iterable

sys.dont_write_bytecode = True


VERSION_RE = re.compile(r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)")
REVISION_RE = re.compile(r"[0-9a-f]{40}")
SHA256_RE = re.compile(r"[0-9a-f]{64}")
MODEL_RE = re.compile(r"[a-z0-9]+(?:[.-][a-z0-9]+)+")
EFFORTS = ("low", "medium", "high")
ADJUSTABLE_RESOLUTIONS = {
    "gemini-3.7-flash": {
        "low": "gemini-3.7-flash-low",
        "medium": "gemini-3.7-flash-medium",
        "high": "gemini-3.7-flash-high",
    },
    "gemini-3.6-flash": {
        "low": "gemini-3.6-flash-low",
        "medium": "gemini-3.6-flash-medium",
        "high": "gemini-3.6-flash-high",
    },
    "gemini-3.5-flash": {
        "low": "gemini-3.5-flash-low",
        "medium": "gemini-3.5-flash-medium",
        "high": "gemini-3.5-flash-high",
    },
    "gemini-3.1-pro": {
        "low": "gemini-3.1-pro-low",
        "high": "gemini-3.1-pro-high",
    },
}
ADJUSTABLE_MODELS = tuple(ADJUSTABLE_RESOLUTIONS)
FIXED_MODELS = {
    "claude-sonnet-4-6": "no-level",
    "claude-opus-4-6-thinking": "thinking-labelled",
    "gpt-oss-120b-medium": "effort-labelled",
}
ACTIVE_EVIDENCE = ["agy-models", "official-release", "official-source"]
CANDIDATE_EVIDENCE = ["installed-agy-models"]
ACTIVE_INVENTORY_BINDING = {
    "schema_version": 1,
    "status": "accepted-current-inventory",
    "agy_version": "1.1.22",
    "reviewed_source_revision": "556846a4bb94117222f53846896c7eb0d645307e",
    "source_sha256": "7b1317779085913d338bde0e9b39b72323d9083a879525f944fd469c8ecca906",
    "version_binding_sha256": "d9d830e65d3a5c76df6d9e07e6ea7e14e14f290ab4036bdbae8cb33502e29f2a",
    "capture_record_sha256": "626623c2c7b3b126efc2161c36554ecfa7fad3ce46e9dfcee8419c685ccaf2e3",
    "capture_stdout_sha256": "b75bd15381574af9ff1d9891dee36cc88a811c2abc86ef202c86c6b79077251c",
    "capture_response_sha256": "a7463eafad52e693c6d4890ed329f16aa60b1dfa9b058c051a13c0f0553efec1",
    "inventory_normalized_sha256": "db2a3529568b1ce4bb112d4cb9a0c31a4f3d1b32bd787728d224894ec6db133c",
    "slug_count": 14,
    "slugs": [
        "claude-opus-4-6-thinking",
        "claude-sonnet-4-6",
        "gemini-3.1-pro-high",
        "gemini-3.1-pro-low",
        "gemini-3.5-flash-high",
        "gemini-3.5-flash-low",
        "gemini-3.5-flash-medium",
        "gemini-3.6-flash-high",
        "gemini-3.6-flash-low",
        "gemini-3.6-flash-medium",
        "gemini-3.7-flash-high",
        "gemini-3.7-flash-low",
        "gemini-3.7-flash-medium",
        "gpt-oss-120b-medium",
    ],
}


class CompatibilityError(ValueError):
    """Malformed or unsupported compatibility evidence."""


class DuplicateKeyError(CompatibilityError):
    """JSON object contains a duplicate key."""


def fail(message: str, code: int = 2) -> None:
    print(f"compatibility: {message}", file=sys.stderr)
    raise SystemExit(code)


def read_record(path: Path) -> str:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise CompatibilityError(f"cannot read {path.name}: {exc.strerror}") from exc
    if not raw.endswith(b"\n") or raw.count(b"\n") != 1:
        raise CompatibilityError(f"{path.name} must be one newline-terminated line")
    try:
        value = raw[:-1].decode("ascii")
    except UnicodeDecodeError as exc:
        raise CompatibilityError(f"{path.name} must be ASCII") from exc
    if not value or value.strip() != value:
        raise CompatibilityError(f"{path.name} has an empty or padded value")
    return value


def validate_record(kind: str, value: str) -> str:
    if kind == "version":
        if VERSION_RE.fullmatch(value) is None:
            raise CompatibilityError("malformed version metadata")
    elif kind == "revision":
        if REVISION_RE.fullmatch(value) is None:
            raise CompatibilityError("malformed source revision metadata")
    elif kind == "date":
        try:
            parsed = date.fromisoformat(value)
        except ValueError as exc:
            raise CompatibilityError("malformed review date metadata") from exc
        if parsed.isoformat() != value:
            raise CompatibilityError("review date must use YYYY-MM-DD")
    else:
        raise CompatibilityError(f"unknown metadata kind: {kind}")
    return value


def command_metadata(args: argparse.Namespace) -> None:
    try:
        print(validate_record(args.kind, read_record(Path(args.file))))
    except CompatibilityError as exc:
        fail(str(exc))


def parse_semver(value: str) -> tuple[int, int, int]:
    if VERSION_RE.fullmatch(value) is None:
        raise CompatibilityError(f"malformed semantic version: {value!r}")
    return tuple(int(part) for part in value.split("."))  # type: ignore[return-value]


def command_latest_release(args: argparse.Namespace) -> None:
    versions: list[tuple[tuple[int, int, int], str]] = []
    matching_prefix_seen = False
    for raw_line in sys.stdin:
        fields = raw_line.split()
        if len(fields) != 2:
            if raw_line.strip():
                fail("malformed official release evidence")
            continue
        oid, ref = fields
        if args.tool == "agy":
            match = re.fullmatch(r"refs/tags/v?((?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*))", ref)
            matching_prefix_seen = matching_prefix_seen or ref.startswith("refs/tags/v")
        else:
            match = re.fullmatch(r"refs/tags/rust-v((?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*))", ref)
            matching_prefix_seen = matching_prefix_seen or ref.startswith("refs/tags/rust-v")
        if match is None:
            continue
        if REVISION_RE.fullmatch(oid) is None:
            fail("malformed official release revision")
        version = match.group(1)
        versions.append((parse_semver(version), version))
    if not versions:
        suffix = " (matching tags were malformed)" if matching_prefix_seen else ""
        fail(f"no stable {args.tool} release evidence{suffix}")
    print(max(versions)[1])


def command_version_output(args: argparse.Namespace) -> None:
    raw = sys.stdin.read()
    if not raw or "\x00" in raw:
        fail(f"{args.tool} version output is empty or malformed")
    lines = raw.splitlines()
    if len(lines) != 1:
        fail(f"{args.tool} version output must be one semantic line")
    line = lines[0]
    if args.tool == "agy":
        match = re.fullmatch(r"(?:agy\s+)?((?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*))", line)
    else:
        match = re.fullmatch(r"codex-cli\s+((?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*))", line)
    if match is None:
        fail(f"{args.tool} version output lacks the documented semantic content")
    print(match.group(1))


def command_review_state(args: argparse.Namespace) -> None:
    try:
        reviewed = date.fromisoformat(args.reviewed)
    except ValueError:
        fail("malformed review date metadata")
    if reviewed.isoformat() != args.reviewed or args.days != 30:
        fail("invalid fixed review policy")
    today = date.today()
    if reviewed > today:
        fail("review date is in the future")
    if (today - reviewed).days >= args.days:
        print("drift-or-review")
        raise SystemExit(3)
    print("unchanged")


def command_source_head(_: argparse.Namespace) -> None:
    rows = [line.split() for line in sys.stdin if line.strip()]
    if len(rows) != 1 or len(rows[0]) != 2:
        fail("official source HEAD evidence is missing or malformed")
    revision, ref = rows[0]
    if REVISION_RE.fullmatch(revision) is None or ref != "HEAD":
        fail("official source HEAD evidence is malformed")
    print(revision)


def no_duplicate_object(pairs: Iterable[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=no_duplicate_object)
    except (OSError, UnicodeError, json.JSONDecodeError, DuplicateKeyError) as exc:
        raise CompatibilityError(f"cannot parse {path.name}: {exc}") from exc


def exact_keys(value: Any, expected: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise CompatibilityError(f"{label} must be an object")
    keys = set(value)
    if keys != expected:
        raise CompatibilityError(
            f"{label} keys differ: expected {sorted(expected)}, got {sorted(keys)}"
        )
    return value


def canonical_schema() -> dict[str, Any]:
    """Return the complete schema contract supported by this validator."""
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://cagdasyurekli.github.io/codex-agy-worker/schemas/model-effort-matrix-v1.json",
        "title": "agy model and effort resolution matrix v1",
        "type": "object",
        "additionalProperties": False,
        "required": [
            "schema_version",
            "resolution_status",
            "inventory",
            "adjustable_models",
            "fixed_models",
        ],
        "properties": {
            "schema_version": {"const": 1},
            "resolution_status": {
                "enum": ["active", "disabled-unverified-source"]
            },
            "inventory": {"$ref": "#/$defs/inventory"},
            "adjustable_models": {
                "type": "array",
                "minItems": 4,
                "maxItems": 4,
                "items": {"$ref": "#/$defs/adjustableModel"},
            },
            "fixed_models": {
                "type": "array",
                "minItems": 3,
                "maxItems": 3,
                "items": {"$ref": "#/$defs/fixedModel"},
            },
        },
        "$defs": {
            "inventory": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "agy_version",
                    "reviewed_source_revision",
                    "evidence",
                ],
                "properties": {
                    "agy_version": {
                        "type": "string",
                        "pattern": (
                            "^(0|[1-9][0-9]*)\\.(0|[1-9][0-9]*)\\."
                            "(0|[1-9][0-9]*)$"
                        ),
                    },
                    "reviewed_source_revision": {
                        "type": ["string", "null"],
                        "pattern": "^[0-9a-f]{40}$",
                    },
                    "evidence": {
                        "type": "array",
                        "minItems": 1,
                        "maxItems": 3,
                        "items": {
                            "enum": ACTIVE_EVIDENCE + CANDIDATE_EVIDENCE
                        },
                        "uniqueItems": True,
                    },
                },
            },
            "adjustableModel": {
                "type": "object",
                "additionalProperties": False,
                "required": ["model", "resolutions", "unsupported_efforts"],
                "properties": {
                    "model": {"enum": list(ADJUSTABLE_MODELS)},
                    "resolutions": {
                        "type": "object",
                        "minProperties": 2,
                        "maxProperties": 3,
                        "propertyNames": {"enum": list(EFFORTS)},
                        "additionalProperties": {
                            "type": "string",
                            "pattern": "^[a-z0-9]+(?:[.-][a-z0-9]+)+$",
                        },
                    },
                    "unsupported_efforts": {
                        "type": "array",
                        "items": {"enum": list(EFFORTS)},
                        "uniqueItems": True,
                    },
                },
            },
            "fixedModel": {
                "type": "object",
                "additionalProperties": False,
                "required": ["model_slug", "classification"],
                "properties": {
                    "model_slug": {"enum": list(FIXED_MODELS)},
                    "classification": {
                        "enum": [
                            "no-level",
                            "thinking-labelled",
                            "effort-labelled",
                        ]
                    },
                },
            },
        },
    }


def validate_schema_document(path: Path) -> None:
    schema = load_json(path)
    if schema != canonical_schema():
        raise CompatibilityError(
            "matrix schema differs from the complete supported canonical policy"
        )


def validate_matrix_structure(matrix_path: Path, schema_path: Path) -> dict[str, Any]:
    validate_schema_document(schema_path)
    root = exact_keys(
        load_json(matrix_path),
        {"schema_version", "resolution_status", "inventory", "adjustable_models", "fixed_models"},
        "matrix",
    )
    if root["schema_version"] != 1:
        raise CompatibilityError("unsupported matrix schema_version")
    status = root["resolution_status"]
    if not isinstance(status, str) or status not in (
        "active",
        "disabled-unverified-source",
    ):
        raise CompatibilityError("unsupported matrix resolution_status")

    inventory = exact_keys(
        root["inventory"],
        {"agy_version", "reviewed_source_revision", "evidence"},
        "matrix inventory",
    )
    version = inventory["agy_version"]
    if not isinstance(version, str) or VERSION_RE.fullmatch(version) is None:
        raise CompatibilityError("matrix inventory has a malformed agy version")
    revision = inventory["reviewed_source_revision"]
    evidence = inventory["evidence"]
    if status == "active":
        if not isinstance(revision, str) or REVISION_RE.fullmatch(revision) is None:
            raise CompatibilityError("active matrix lacks an exact reviewed source revision")
        if evidence != ACTIVE_EVIDENCE:
            raise CompatibilityError("active matrix lacks the required primary evidence")
    else:
        if revision is not None:
            raise CompatibilityError("unverified candidate matrix must not claim a source revision")
        if evidence != CANDIDATE_EVIDENCE:
            raise CompatibilityError("candidate matrix evidence is unsupported")

    rows = root["adjustable_models"]
    if not isinstance(rows, list) or len(rows) != len(ADJUSTABLE_MODELS):
        raise CompatibilityError("matrix must list every reviewed adjustable model exactly once")
    seen_models: set[str] = set()
    seen_outputs: set[str] = set()
    for index, item in enumerate(rows):
        row = exact_keys(item, {"model", "resolutions", "unsupported_efforts"}, f"adjustable_models[{index}]")
        model = row["model"]
        if (
            not isinstance(model, str)
            or model not in ADJUSTABLE_MODELS
            or model in seen_models
        ):
            raise CompatibilityError(f"unknown or duplicate adjustable model: {model!r}")
        seen_models.add(model)
        resolutions = row["resolutions"]
        unsupported = row["unsupported_efforts"]
        if not isinstance(resolutions, dict) or not isinstance(unsupported, list):
            raise CompatibilityError(f"invalid effort contract for {model}")
        if any(
            not isinstance(value, str) or value not in EFFORTS
            for value in unsupported
        ) or len(set(unsupported)) != len(unsupported):
            raise CompatibilityError(f"invalid unsupported effort list for {model}")
        expected_resolutions = ADJUSTABLE_RESOLUTIONS[model]
        expected_unsupported = [
            effort for effort in EFFORTS if effort not in expected_resolutions
        ]
        if resolutions != expected_resolutions:
            raise CompatibilityError(
                f"matrix differs from the explicit reviewed mapping for {model}"
            )
        if unsupported != expected_unsupported:
            raise CompatibilityError(
                f"matrix differs from the explicit unsupported efforts for {model}"
            )
        covered = set(resolutions) | set(unsupported)
        if covered != set(EFFORTS) or set(resolutions) & set(unsupported):
            raise CompatibilityError(f"effort coverage for {model} must be exact and disjoint")
        for effort, slug in resolutions.items():
            if effort not in EFFORTS or not isinstance(slug, str) or MODEL_RE.fullmatch(slug) is None:
                raise CompatibilityError(f"invalid resolution for {model}/{effort}")
            if slug in seen_outputs:
                raise CompatibilityError(f"duplicate output slug for {model}/{effort}")
            seen_outputs.add(slug)

    fixed_rows = root["fixed_models"]
    if not isinstance(fixed_rows, list) or len(fixed_rows) != len(FIXED_MODELS):
        raise CompatibilityError("matrix must list every reviewed fixed model exactly once")
    seen_fixed: set[str] = set()
    for index, item in enumerate(fixed_rows):
        row = exact_keys(item, {"model_slug", "classification"}, f"fixed_models[{index}]")
        slug = row["model_slug"]
        if (
            not isinstance(slug, str)
            or slug not in FIXED_MODELS
            or slug in seen_fixed
        ):
            raise CompatibilityError(f"unknown or duplicate fixed model: {slug!r}")
        if row["classification"] != FIXED_MODELS[slug]:
            raise CompatibilityError(f"invalid fixed-model classification for {slug}")
        if slug in seen_outputs:
            raise CompatibilityError(f"fixed and adjustable outputs overlap: {slug}")
        seen_fixed.add(slug)
    return root


def matrix_binding_state(matrix: dict[str, Any], version: str, revision: str) -> tuple[bool, str]:
    inventory = matrix["inventory"]
    if matrix["resolution_status"] != "active":
        return False, "resolution is disabled pending official source evidence"
    if inventory["agy_version"] != version:
        return False, "matrix agy version differs from the verified baseline"
    if inventory["reviewed_source_revision"] != revision:
        return False, "matrix source revision differs from the reviewed baseline"
    return True, "active and bound"


def matrix_slugs(matrix: dict[str, Any]) -> list[str]:
    slugs = [
        slug
        for row in matrix["adjustable_models"]
        for slug in row["resolutions"].values()
    ]
    slugs.extend(row["model_slug"] for row in matrix["fixed_models"])
    return sorted(slugs)


def validate_inventory_binding(
    binding_path: Path,
    binding_sha_path: Path,
    version: str,
    revision: str,
    matrix: dict[str, Any],
) -> None:
    try:
        binding_bytes = binding_path.read_bytes()
    except OSError as exc:
        raise CompatibilityError(
            f"cannot read {binding_path.name}: {exc.strerror}"
        ) from exc
    expected_sha = read_record(binding_sha_path)
    if SHA256_RE.fullmatch(expected_sha) is None:
        raise CompatibilityError("malformed inventory binding digest")
    actual_sha = hashlib.sha256(binding_bytes).hexdigest()
    if actual_sha != expected_sha:
        raise CompatibilityError("inventory binding digest differs from accepted evidence")
    binding = load_json(binding_path)
    exact_keys(binding, set(ACTIVE_INVENTORY_BINDING), "inventory binding")
    for key, expected in ACTIVE_INVENTORY_BINDING.items():
        if binding[key] != expected:
            raise CompatibilityError("inventory binding differs from accepted evidence")
    if binding["agy_version"] != version:
        raise CompatibilityError("inventory binding agy version differs from the verified baseline")
    if binding["reviewed_source_revision"] != revision:
        raise CompatibilityError("inventory binding source differs from the reviewed baseline")
    if binding["slugs"] != matrix_slugs(matrix):
        raise CompatibilityError("inventory binding slugs differ from the active matrix")
    manifest_file = binding_path.parent / "agy-version-manifest.json"
    try:
        import version_manifest_engine
    except ImportError:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import version_manifest_engine  # type: ignore[no-redef]
    try:
        spec = version_manifest_engine.get_version_spec(version, manifest_file)
        version_manifest_engine.validate_activation_binding(binding, spec)
    except version_manifest_engine.EngineError as exc:
        raise CompatibilityError(f"version manifest error: {exc}") from exc


def load_bound_matrix(args: argparse.Namespace) -> tuple[dict[str, Any], bool, str]:
    try:
        version = validate_record("version", read_record(Path(args.verified_version_file)))
        revision = validate_record("revision", read_record(Path(args.reviewed_revision_file)))
        matrix = validate_matrix_structure(Path(args.matrix), Path(args.schema))
    except CompatibilityError as exc:
        fail(str(exc))
    active, reason = matrix_binding_state(matrix, version, revision)
    if active:
        try:
            validate_inventory_binding(
                Path(args.inventory_binding),
                Path(args.inventory_binding_sha256),
                version,
                revision,
                matrix,
            )
        except CompatibilityError as exc:
            fail(str(exc))
    return matrix, active, reason


def command_validate_matrix(args: argparse.Namespace) -> None:
    _, active, reason = load_bound_matrix(args)
    if not active:
        print(f"matrix: drift-or-review - {reason}")
        raise SystemExit(3)
    print("matrix: unchanged - active and version/source bound")


def command_resolve_matrix(args: argparse.Namespace) -> None:
    matrix, active, reason = load_bound_matrix(args)
    if not active:
        fail(f"matrix cannot resolve: {reason}", 3)
    if args.effort not in EFFORTS:
        fail("unsupported effort input", 64)
    for row in matrix["adjustable_models"]:
        if row["model"] != args.model:
            continue
        if args.effort in row["unsupported_efforts"]:
            fail(f"{args.model} does not advertise {args.effort}", 64)
        slug = row["resolutions"].get(args.effort)
        if slug is None:
            fail("matrix has no exact resolution", 64)
        print(slug)
        return
    if args.model in FIXED_MODELS:
        fail("fixed models do not accept an effort input", 64)
    fail("unknown model input", 64)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    metadata = subparsers.add_parser("metadata")
    metadata.add_argument("--kind", choices=("version", "revision", "date"), required=True)
    metadata.add_argument("--file", required=True)
    metadata.set_defaults(func=command_metadata)

    releases = subparsers.add_parser("latest-release")
    releases.add_argument("--tool", choices=("agy", "codex"), required=True)
    releases.set_defaults(func=command_latest_release)

    version_output = subparsers.add_parser("version-output")
    version_output.add_argument("--tool", choices=("agy", "codex"), required=True)
    version_output.set_defaults(func=command_version_output)

    review = subparsers.add_parser("review-state")
    review.add_argument("--reviewed", required=True)
    review.add_argument("--days", type=int, required=True)
    review.set_defaults(func=command_review_state)

    source_head = subparsers.add_parser("source-head")
    source_head.set_defaults(func=command_source_head)

    for name, func in (("validate-matrix", command_validate_matrix), ("resolve-matrix", command_resolve_matrix)):
        matrix = subparsers.add_parser(name)
        matrix.add_argument("--matrix", required=True)
        matrix.add_argument("--schema", required=True)
        matrix.add_argument("--verified-version-file", required=True)
        matrix.add_argument("--reviewed-revision-file", required=True)
        matrix.add_argument("--inventory-binding", required=True)
        matrix.add_argument("--inventory-binding-sha256", required=True)
        if name == "resolve-matrix":
            matrix.add_argument("--model", required=True)
            matrix.add_argument("--effort", required=True)
        matrix.set_defaults(func=func)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
