#!/usr/bin/env python3
"""Create and validate one private, unsigned Evidence Receipt v1.

The gate remains the sole authority for its outcome.  This module binds the gate's
structured handoff to caller-owned input hashes and publishes the resulting record;
it does not reproduce acceptance logic or inspect gate prose.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import signal
import stat
import subprocess
import sys
from typing import Any

sys.dont_write_bytecode = True
RUNTIME_SCRIPTS = str(Path(__file__).resolve(strict=True).parent)
if RUNTIME_SCRIPTS not in sys.path:
    sys.path.insert(0, RUNTIME_SCRIPTS)

from model_selection import (  # noqa: E402
    CallerError as SelectionError,
    EvidenceUnavailable,
    ReviewRequired,
    child_environment,
    validate_child_environment_names,
    validate_selection_record,
    validate_selection_record_shape,
)
from recommendation_record import (  # noqa: E402
    RecommendationRecordError,
    validate_recommendation_record,
)


MAX_JSON_BYTES = 1024 * 1024
MAX_HANDOFF_BYTES = 4096
MAX_VERIFY_ENV_PAYLOAD = 256 * 1024
SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
COMMIT_RE = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})\Z")
LABEL_RE = re.compile(r"verify-[0-9]{3}\Z")
GATE_OUTCOMES = {
    0: "gate-passed",
    10: "scope-violation",
    11: "untrusted-worker-claim",
    12: "invalid-envelope",
    13: "expected-edits-missing",
    14: "driver-verification-failed",
    15: "worker-escalation",
}
VERDICTS = {
    0: "gate-passed",
    10: "rejected",
    11: "rejected",
    12: "rejected",
    13: "rejected",
    14: "rejected",
    15: "routed",
}
INTEGRITY_STATEMENT = (
    "Unsigned local record; schema-valid content can be rewritten and is not "
    "self-authenticating."
)


class UsageFailure(ValueError):
    pass


class ProtocolFailure(ValueError):
    pass


class SignalInterruption(ProtocolFailure):
    pass


class PublicationFailure(OSError):
    pass


class ValidationFailure(ValueError):
    pass


HANDLED_SIGNALS = (signal.SIGHUP, signal.SIGINT, signal.SIGTERM)


class SignalController:
    def __init__(self) -> None:
        self.previous: dict[int, Any] = {}
        self.active_group: int | None = None
        self.interrupted = False
        self.signal_number: int | None = None
        self.published_target: Path | None = None
        self.published_identity: tuple[int, int] | None = None
        self.published_descriptor = -1
        self.private_paths: set[Path] = set()

    def __enter__(self) -> "SignalController":
        for signum in HANDLED_SIGNALS:
            self.previous[signum] = signal.signal(signum, self._handle)
        return self

    def __exit__(self, _kind: Any, _value: Any, _traceback: Any) -> None:
        for signum, handler in self.previous.items():
            signal.signal(signum, handler)

    def _handle(self, signum: int, _frame: Any) -> None:
        if self.interrupted:
            return
        self.interrupted = True
        self.signal_number = signum
        if self.active_group is not None:
            try:
                os.killpg(self.active_group, signum)
            except ProcessLookupError:
                pass
        raise SignalInterruption("receipt operation interrupted")

    @contextmanager
    def blocked(self):
        previous_mask = signal.pthread_sigmask(signal.SIG_BLOCK, HANDLED_SIGNALS)
        try:
            yield
        finally:
            signal.pthread_sigmask(signal.SIG_SETMASK, previous_mask)

    def set_group(self, group: int | None) -> None:
        self.active_group = group

    def register_publication(
        self, target: Path, identity: tuple[int, int], descriptor: int
    ) -> None:
        self.published_target = target
        self.published_identity = identity
        self.published_descriptor = descriptor

    def clear_publication(self) -> None:
        if self.published_descriptor >= 0:
            os.close(self.published_descriptor)
            self.published_descriptor = -1
        self.published_target = None
        self.published_identity = None

    def register_private(self, path: Path) -> None:
        self.private_paths.add(path)

    def clear_private(self, path: Path) -> None:
        self.private_paths.discard(path)

    def remove_registered_publication(self) -> None:
        target = self.published_target
        identity = self.published_identity
        if target is None or identity is None:
            self.clear_publication()
            return
        try:
            metadata = target.lstat()
            if (metadata.st_dev, metadata.st_ino) == identity:
                target.unlink()
        except OSError:
            pass
        self.clear_publication()

    def cleanup_all(self) -> None:
        parents: set[Path] = set()
        if self.published_target is not None:
            parents.add(self.published_target.parent)
        self.remove_registered_publication()
        for path in tuple(self.private_paths):
            parents.add(path.parent)
            try:
                path.unlink()
            except OSError:
                pass
            self.clear_private(path)
        for parent in parents:
            try:
                descriptor = os.open(parent, os.O_RDONLY)
                try:
                    os.fsync(descriptor)
                finally:
                    os.close(descriptor)
            except OSError:
                pass


def interruption_checkpoint(_name: str) -> None:
    """No-op production hook monkeypatched by deterministic offline tests."""


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=True, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def published_bytes(value: Any) -> bytes:
    return canonical_bytes(value) + b"\n"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValidationFailure(f"duplicate key {key!r}")
        result[key] = value
    return result


def parse_json_bytes(payload: bytes, label: str) -> Any:
    if not payload or len(payload) > MAX_JSON_BYTES:
        raise ValidationFailure(f"{label} is empty or oversized")
    try:
        return json.loads(payload.decode("utf-8"), object_pairs_hook=reject_duplicates)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValidationFailure(f"{label} is not valid unique-key UTF-8 JSON") from exc


def read_real_file(path: Path, label: str, maximum: int = MAX_JSON_BYTES) -> bytes:
    descriptor = -1
    try:
        descriptor = os.open(
            path,
            os.O_RDONLY
            | getattr(os, "O_NOFOLLOW", 0)
            | getattr(os, "O_NONBLOCK", 0),
        )
        metadata = os.fstat(descriptor)
    except (OSError, ValueError) as exc:
        if descriptor >= 0:
            os.close(descriptor)
        raise UsageFailure(f"{label} must be one existing real file") from exc
    if not stat.S_ISREG(metadata.st_mode):
        os.close(descriptor)
        raise UsageFailure(f"{label} must be one existing real file")
    if metadata.st_size > maximum:
        os.close(descriptor)
        raise UsageFailure(f"{label} exceeds the {maximum}-byte limit")
    try:
        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = os.read(descriptor, min(1024 * 1024, maximum + 1 - total))
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
            if total > maximum:
                raise UsageFailure(f"{label} exceeds the {maximum}-byte limit")
        payload = b"".join(chunks)
    except OSError as exc:
        raise UsageFailure(f"{label} could not be read") from exc
    finally:
        os.close(descriptor)
    return payload


def require_exact_fields(value: dict[str, Any], expected: set[str], label: str) -> None:
    if set(value) != expected:
        raise ValidationFailure(f"{label} fields are inconsistent")


def require_sha(value: Any, label: str) -> str:
    if not isinstance(value, str) or SHA256_RE.fullmatch(value) is None:
        raise ValidationFailure(f"{label} must be one lowercase SHA-256")
    return value


def require_unpadded_string(value: Any, label: str, maximum: int = 4096) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value.strip() != value
        or len(value) > maximum
    ):
        raise ValidationFailure(f"{label} must be one bounded unpadded string")
    return value


SCHEMA_KEYS = {
    "$schema",
    "title",
    "type",
    "additionalProperties",
    "required",
    "properties",
    "items",
    "enum",
    "minLength",
    "maxLength",
    "minimum",
    "maximum",
    "minItems",
    "maxItems",
    "pattern",
    "oneOf",
}


def preflight_schema(schema: Any, location: str = "$") -> None:
    if not isinstance(schema, dict):
        raise ValidationFailure(f"schema node at {location} is not an object")
    unknown = set(schema) - SCHEMA_KEYS
    if unknown:
        raise ValidationFailure(f"schema has unsupported keys at {location}")
    properties = schema.get("properties", {})
    if not isinstance(properties, dict):
        raise ValidationFailure(f"schema properties at {location} are invalid")
    for key, child in properties.items():
        preflight_schema(child, f"{location}.{key}")
    if "items" in schema:
        preflight_schema(schema["items"], f"{location}[]")
    if "oneOf" in schema:
        alternatives = schema["oneOf"]
        if not isinstance(alternatives, list) or not alternatives:
            raise ValidationFailure(f"schema oneOf at {location} is invalid")
        for index, alternative in enumerate(alternatives):
            preflight_schema(alternative, f"{location}.oneOf[{index}]")


def schema_type_matches(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "boolean":
        return type(value) is bool
    if expected == "number":
        return type(value) in (int, float)
    if expected == "integer":
        return type(value) is int
    if expected == "null":
        return value is None
    raise ValidationFailure("schema contains an unknown type")


def validate_schema(value: Any, schema: dict[str, Any], location: str = "$") -> None:
    if "oneOf" in schema:
        accepted = 0
        for alternative in schema["oneOf"]:
            try:
                validate_schema(value, alternative, location)
            except ValidationFailure:
                continue
            accepted += 1
        if accepted != 1:
            raise ValidationFailure(f"{location} does not match exactly one schema alternative")
    expected_type = schema.get("type")
    if expected_type is not None and not schema_type_matches(value, expected_type):
        raise ValidationFailure(f"{location} has the wrong type")
    if "enum" in schema and value not in schema["enum"]:
        raise ValidationFailure(f"{location} has a forbidden value")
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            raise ValidationFailure(f"{location} is too short")
        if len(value) > schema.get("maxLength", len(value)):
            raise ValidationFailure(f"{location} is too long")
        pattern = schema.get("pattern")
        if pattern is not None:
            if not isinstance(pattern, str):
                raise ValidationFailure("schema pattern is invalid")
            try:
                matched = re.search(pattern, value)
            except re.error as exc:
                raise ValidationFailure("schema pattern is invalid") from exc
            if matched is None:
                raise ValidationFailure(f"{location} does not match its pattern")
    if type(value) in (int, float):
        if value < schema.get("minimum", value):
            raise ValidationFailure(f"{location} is below minimum")
        if value > schema.get("maximum", value):
            raise ValidationFailure(f"{location} is above maximum")
    if isinstance(value, list) and "items" in schema:
        if len(value) < schema.get("minItems", 0):
            raise ValidationFailure(f"{location} has too few items")
        if len(value) > schema.get("maxItems", len(value)):
            raise ValidationFailure(f"{location} has too many items")
        for index, item in enumerate(value):
            validate_schema(item, schema["items"], f"{location}[{index}]")
    if isinstance(value, dict):
        required = set(schema.get("required", []))
        if required - set(value):
            raise ValidationFailure(f"{location} is missing required fields")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False and set(value) - set(properties):
            raise ValidationFailure(f"{location} has unexpected fields")
        for key, child in properties.items():
            if key in value:
                validate_schema(value[key], child, f"{location}.{key}")


def load_schema(schema_path: Path) -> dict[str, Any]:
    schema = parse_json_bytes(read_real_file(schema_path, "receipt schema"), "receipt schema")
    if not isinstance(schema, dict):
        raise ValidationFailure("receipt schema root must be an object")
    preflight_schema(schema)
    return schema


def validate_integrity(value: Any) -> None:
    if not isinstance(value, dict):
        raise ValidationFailure("integrity must be an object")
    require_exact_fields(value, {"signed", "tamper_evident", "statement"}, "integrity")
    if value != {
        "signed": False,
        "tamper_evident": False,
        "statement": INTEGRITY_STATEMENT,
    }:
        raise ValidationFailure("integrity must state the fixed unsigned limitation")


def recommendation_argv(value: dict[str, Any]) -> list[str]:
    if value.get("stage") != "pre-dispatch":
        raise ValidationFailure("only a pre-dispatch recommendation may be bound")
    evidence = value.get("evidence")
    if not isinstance(evidence, dict) or set(evidence) != {"owner", "code", "description"}:
        raise ValidationFailure("recommendation evidence is invalid")
    code = require_unpadded_string(evidence.get("code"), "recommendation evidence code", 64)
    argv = ["--stage", "pre-dispatch"]
    tier = value.get("selected_tier")
    model = value.get("user_model")
    if (tier is None) == (model is None):
        raise ValidationFailure("recommendation must contain exactly one selection mode")
    if tier is not None:
        argv += ["--selected-tier", require_unpadded_string(tier, "selected tier", 128)]
        if "user_effort" in value:
            raise ValidationFailure("tier recommendation cannot contain effort")
    else:
        argv += ["--selected-model", require_unpadded_string(model, "user model", 128)]
        if "user_effort" in value:
            argv += [
                "--selected-effort",
                require_unpadded_string(value["user_effort"], "user effort", 16),
            ]
    argv += ["--evidence", code]
    return argv


def validate_recommendation_for_publication(
    value: Any, recommendation_script: Path
) -> dict[str, Any]:
    try:
        validate_recommendation_record(value, required_stage="pre-dispatch")
    except RecommendationRecordError as exc:
        raise ValidationFailure("pre-dispatch recommendation is invalid") from exc
    assert isinstance(value, dict)
    argv = recommendation_argv(value)
    try:
        completed = subprocess.run(
            [sys.executable, "-B", str(recommendation_script), *argv],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=False,
            timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ValidationFailure("canonical recommendation validation failed") from exc
    if completed.returncode != 0 or len(completed.stdout) > MAX_JSON_BYTES:
        raise ValidationFailure("recommendation is not canonical")
    expected = parse_json_bytes(completed.stdout, "canonical recommendation")
    if value != expected:
        raise ValidationFailure("recommendation differs from canonical policy output")
    return value


def selection_matches_recommendation(
    selection: dict[str, Any], recommendation: dict[str, Any]
) -> bool:
    if selection["selection_mode"] == "tier":
        return (
            recommendation.get("selected_tier") == selection["selected_tier"]
            and "user_model" not in recommendation
        )
    keys = [
        "user_model",
        "resolved_agy_model",
        "matrix_sha256",
        "matrix_agy_version",
        "matrix_source_revision",
    ]
    if any(recommendation.get(key) != selection.get(key) for key in keys):
        return False
    return recommendation.get("user_effort") == selection.get("user_effort")


def validate_receipt(
    value: Any,
    schema: dict[str, Any],
) -> dict[str, Any]:
    validate_schema(value, schema)
    if not isinstance(value, dict):
        raise ValidationFailure("receipt must be one object")
    if type(value.get("schema_version")) is not int or value["schema_version"] != 1:
        raise ValidationFailure("schema_version must be integer 1")
    resolved_base = value.get("resolved_base")
    if not isinstance(resolved_base, str) or COMMIT_RE.fullmatch(resolved_base) is None:
        raise ValidationFailure("resolved_base is invalid")
    for key in (
        "envelope_sha256",
        "path_policy_sha256",
        "initial_candidate_state_sha256",
        "final_candidate_state_sha256",
    ):
        require_sha(value.get(key), key)
    gate_exit = value.get("gate_exit")
    if type(gate_exit) is not int or gate_exit not in GATE_OUTCOMES:
        raise ValidationFailure("gate_exit is not a receiptable gate result")
    if value.get("gate_outcome") != GATE_OUTCOMES[gate_exit]:
        raise ValidationFailure("gate outcome and exit are inconsistent")
    if value.get("verdict") != VERDICTS[gate_exit]:
        raise ValidationFailure("receipt verdict and exit are inconsistent")
    if value.get("gate_authority") != "qa-gate":
        raise ValidationFailure("gate authority is invalid")
    if value.get("recommendations_participated_in_acceptance") is not False:
        raise ValidationFailure("recommendation cannot participate in acceptance")
    validate_integrity(value.get("integrity"))
    verifiers = value.get("verifiers")
    if not isinstance(verifiers, list) or not verifiers:
        raise ValidationFailure("receipt needs at least one verifier hash")
    for index, verifier in enumerate(verifiers, 1):
        if not isinstance(verifier, dict):
            raise ValidationFailure("verifier entry must be an object")
        require_exact_fields(verifier, {"label", "command_sha256"}, "verifier")
        if verifier.get("label") != f"verify-{index:03d}" or LABEL_RE.fullmatch(
            verifier.get("label", "")
        ) is None:
            raise ValidationFailure("verifier labels are not deterministic")
        require_sha(verifier.get("command_sha256"), "verifier command hash")
    selection = value.get("caller_selection")
    if selection is not None:
        try:
            # Semantic validation against the active G1 contract is performed on
            # publication input.  Receipt-only validation still enforces exact
            # selector shape below without re-probing agy.
            if not isinstance(selection, dict):
                raise SelectionError("selection record must be one object")
            validate_selection_record_shape(selection)
        except (SelectionError, ReviewRequired, EvidenceUnavailable) as exc:
            raise ValidationFailure("caller selection is not a valid G1 record") from exc
    recommendation = value.get("pre_dispatch_recommendation")
    if recommendation is not None:
        try:
            recommendation = validate_recommendation_record(
                recommendation, required_stage="pre-dispatch"
            )
        except RecommendationRecordError as exc:
            raise ValidationFailure("pre-dispatch recommendation is invalid") from exc
    if selection is not None and recommendation is not None:
        if not selection_matches_recommendation(selection, recommendation):
            raise ValidationFailure("selection and recommendation are inconsistent")
    return value


def load_selection(path: Path) -> dict[str, Any]:
    try:
        value = parse_json_bytes(
            read_real_file(path, "selection input"), "selection input"
        )
        if not isinstance(value, dict):
            raise SelectionError("selection record must be one object")
        validate_selection_record(value)
        return value
    except (
        SelectionError,
        ReviewRequired,
        EvidenceUnavailable,
        ValidationFailure,
    ) as exc:
        raise UsageFailure("selection input is not a current valid G1 record") from exc


def load_recommendation_record(path: Path) -> dict[str, Any]:
    try:
        value = parse_json_bytes(
            read_real_file(path, "pre-dispatch recommendation"),
            "pre-dispatch recommendation",
        )
        return validate_recommendation_record(value, required_stage="pre-dispatch")
    except (ValidationFailure, RecommendationRecordError) as exc:
        raise UsageFailure("pre-dispatch recommendation is not canonical") from exc


def load_recommendation_for_publication(
    path: Path, recommendation_script: Path
) -> dict[str, Any]:
    try:
        value = parse_json_bytes(
            read_real_file(path, "pre-dispatch recommendation"),
            "pre-dispatch recommendation",
        )
        return validate_recommendation_for_publication(value, recommendation_script)
    except ValidationFailure as exc:
        raise UsageFailure("pre-dispatch recommendation is not canonical") from exc


def validate_target(target: Path, repo: Path) -> tuple[Path, str]:
    if not target.is_absolute() or "\n" in str(target) or "\r" in str(target):
        raise UsageFailure("--receipt must be one canonical absolute path")
    if target.exists() or target.is_symlink():
        raise UsageFailure("--receipt must name a new path and never overwrites")
    try:
        parent_text = os.path.abspath(str(target.parent))
        parent = target.parent.resolve(strict=True)
        repo_resolved = repo.resolve(strict=True)
        metadata = parent.lstat()
    except OSError as exc:
        raise UsageFailure("receipt parent and repository must exist") from exc
    if str(parent) != parent_text:
        raise UsageFailure("receipt parent must be a canonical real directory")
    if (
        not stat.S_ISDIR(metadata.st_mode)
        or stat.S_ISLNK(metadata.st_mode)
        or metadata.st_uid != os.geteuid()
        or stat.S_IMODE(metadata.st_mode) & 0o077
        or stat.S_IMODE(metadata.st_mode) & 0o700 != 0o700
    ):
        raise UsageFailure("receipt parent must be an owner-private real directory")
    try:
        if os.path.commonpath((str(parent / target.name), str(repo_resolved))) == str(
            repo_resolved
        ):
            raise UsageFailure("receipt must be outside the audited repository")
    except ValueError as exc:
        raise UsageFailure("receipt and repository paths are incompatible") from exc
    return parent, target.name


def require_private_parent(parent: Path) -> None:
    try:
        metadata = parent.lstat()
        canonical = parent.resolve(strict=True)
    except OSError as exc:
        raise PublicationFailure("receipt parent became unavailable") from exc
    if (
        canonical != parent
        or not stat.S_ISDIR(metadata.st_mode)
        or stat.S_ISLNK(metadata.st_mode)
        or metadata.st_uid != os.geteuid()
        or stat.S_IMODE(metadata.st_mode) & 0o077
        or stat.S_IMODE(metadata.st_mode) & 0o700 != 0o700
    ):
        raise PublicationFailure("receipt parent is no longer owner-private")


def private_file(
    parent: Path,
    stem: str,
    payload: bytes = b"",
    controller: SignalController | None = None,
    checkpoint: str | None = None,
) -> tuple[Path, int]:
    for counter in range(100):
        path = parent / f".{stem}.{os.getpid()}.{counter}"
        descriptor = -1
        try:
            if controller is None:
                descriptor = os.open(
                    path,
                    os.O_WRONLY
                    | os.O_CREAT
                    | os.O_EXCL
                    | getattr(os, "O_NOFOLLOW", 0),
                    0o600,
                )
                os.fchmod(descriptor, 0o600)
            else:
                with controller.blocked():
                    descriptor = os.open(
                        path,
                        os.O_WRONLY
                        | os.O_CREAT
                        | os.O_EXCL
                        | getattr(os, "O_NOFOLLOW", 0),
                        0o600,
                    )
                    os.fchmod(descriptor, 0o600)
                    controller.register_private(path)
        except FileExistsError:
            continue
        except SignalInterruption:
            if descriptor >= 0:
                os.close(descriptor)
            try:
                path.unlink()
            except OSError:
                pass
            if controller is not None:
                controller.clear_private(path)
            raise
        except OSError as exc:
            if descriptor >= 0:
                os.close(descriptor)
            try:
                path.unlink()
            except OSError:
                pass
            if controller is not None:
                controller.clear_private(path)
            raise PublicationFailure("could not create a private temporary file") from exc
        try:
            if checkpoint is not None:
                interruption_checkpoint(checkpoint)
            if payload:
                view = memoryview(payload)
                while view:
                    written = os.write(descriptor, view)
                    if written <= 0:
                        raise OSError("short private-file write")
                    view = view[written:]
            return path, descriptor
        except BaseException:
            os.close(descriptor)
            try:
                path.unlink()
            except OSError:
                pass
            if controller is not None:
                controller.clear_private(path)
            raise
    raise PublicationFailure("could not create a private temporary file")


def snapshot_file(
    source: Path, parent: Path, controller: SignalController
) -> tuple[Path, str]:
    try:
        metadata = source.lstat()
    except OSError as exc:
        raise UsageFailure("envelope must be one existing real file") from exc
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode):
        raise UsageFailure("envelope must be one existing real file")
    path, descriptor = private_file(
        parent,
        "agy-receipt-envelope",
        controller=controller,
        checkpoint="snapshot-created",
    )
    source_descriptor = -1
    digest = hashlib.sha256()
    try:
        source_descriptor = os.open(
            source,
            os.O_RDONLY
            | getattr(os, "O_NOFOLLOW", 0)
            | getattr(os, "O_NONBLOCK", 0),
        )
        if not stat.S_ISREG(os.fstat(source_descriptor).st_mode):
            raise OSError("envelope snapshot source is not regular")
        while True:
            chunk = os.read(source_descriptor, 1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
            view = memoryview(chunk)
            while view:
                written = os.write(descriptor, view)
                if written <= 0:
                    raise OSError("short envelope snapshot write")
                view = view[written:]
        interruption_checkpoint("snapshot-before-fsync")
        os.fsync(descriptor)
    except (OSError, SignalInterruption) as exc:
        try:
            path.unlink()
        except OSError:
            pass
        controller.clear_private(path)
        if isinstance(exc, SignalInterruption):
            raise
        raise UsageFailure("could not snapshot envelope") from exc
    finally:
        if source_descriptor >= 0:
            os.close(source_descriptor)
        os.close(descriptor)
    return path, digest.hexdigest()


def parse_handoff(payload: bytes) -> dict[str, Any]:
    if not payload or len(payload) > MAX_HANDOFF_BYTES:
        raise ProtocolFailure("gate evidence is missing or oversized")
    if not payload.endswith(b"\n") or payload.count(b"\n") != 1:
        raise ProtocolFailure("gate evidence must be exactly one JSON line")
    try:
        value = parse_json_bytes(payload[:-1], "gate evidence")
    except ValidationFailure as exc:
        raise ProtocolFailure("gate evidence is malformed") from exc
    fields = {
        "schema_version",
        "kind",
        "resolved_base",
        "envelope_sha256",
        "initial_candidate_state_sha256",
        "final_candidate_state_sha256",
        "gate_exit",
        "gate_outcome",
    }
    if not isinstance(value, dict) or set(value) != fields:
        raise ProtocolFailure("gate evidence fields are inconsistent")
    if type(value.get("schema_version")) is not int or value["schema_version"] != 1:
        raise ProtocolFailure("gate evidence version is invalid")
    if value.get("kind") != "agy-worker-gate-evidence":
        raise ProtocolFailure("gate evidence kind is invalid")
    if not isinstance(value.get("resolved_base"), str) or COMMIT_RE.fullmatch(
        value["resolved_base"]
    ) is None:
        raise ProtocolFailure("gate evidence base is invalid")
    for key in (
        "envelope_sha256",
        "initial_candidate_state_sha256",
        "final_candidate_state_sha256",
    ):
        try:
            require_sha(value.get(key), key)
        except ValidationFailure as exc:
            raise ProtocolFailure("gate evidence digest is invalid") from exc
    gate_exit = value.get("gate_exit")
    if type(gate_exit) is not int or gate_exit not in GATE_OUTCOMES:
        raise ProtocolFailure("gate evidence exit is unknown")
    if value.get("gate_outcome") != GATE_OUTCOMES[gate_exit]:
        raise ProtocolFailure("gate evidence outcome is inconsistent")
    return value


def publish_receipt(
    target: Path,
    parent: Path,
    value: dict[str, Any],
    schema: dict[str, Any],
    _legacy_recommendation_script: Path | None = None,
    controller: SignalController | None = None,
) -> None:
    owns_controller = controller is None
    controller = controller or SignalController()
    require_private_parent(parent)
    payload = published_bytes(value)
    temporary, descriptor = private_file(
        parent,
        f"{target.name}.receipt",
        payload,
        controller=controller,
        checkpoint="publication-temp-created",
    )
    directory_fd = -1
    try:
        interruption_checkpoint("publication-before-file-fsync")
        os.fsync(descriptor)
        candidate_payload = read_real_file(temporary, "temporary receipt")
        candidate = parse_json_bytes(candidate_payload, "temporary receipt")
        validate_receipt(candidate, schema)
        if candidate != value or candidate_payload != payload:
            raise PublicationFailure("temporary receipt bytes changed")
        require_private_parent(parent)
        temporary_metadata = os.fstat(descriptor)
        published_identity = (
            temporary_metadata.st_dev,
            temporary_metadata.st_ino,
        )
        controller.register_publication(target, published_identity, descriptor)
        descriptor = -1
        interruption_checkpoint("publication-before-link")
        with controller.blocked():
            os.link(temporary, target, follow_symlinks=False)
            interruption_checkpoint("publication-after-link")
        with controller.blocked():
            directory_fd = os.open(parent, os.O_RDONLY)
        interruption_checkpoint("publication-before-first-parent-fsync")
        os.fsync(directory_fd)
        temporary.unlink()
        controller.clear_private(temporary)
        interruption_checkpoint("publication-before-second-parent-fsync")
        os.fsync(directory_fd)
        os.close(directory_fd)
        directory_fd = -1
    except (
        OSError,
        ValidationFailure,
        PublicationFailure,
        SignalInterruption,
    ) as exc:
        controller.remove_registered_publication()
        if directory_fd >= 0:
            os.close(directory_fd)
        if descriptor >= 0:
            os.close(descriptor)
        try:
            temporary.unlink()
        except OSError:
            pass
        controller.clear_private(temporary)
        try:
            cleanup_fd = os.open(parent, os.O_RDONLY)
            try:
                os.fsync(cleanup_fd)
            finally:
                os.close(cleanup_fd)
        except OSError:
            pass
        if isinstance(exc, SignalInterruption):
            raise
        raise PublicationFailure("receipt publication failed") from exc
    if owns_controller:
        controller.clear_publication()


class UsageParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        self.print_usage(sys.stderr)
        self.exit(64, f"verify-job: {message}\n")


def one(parser: UsageParser, values: list[str] | None, flag: str, required: bool) -> str | None:
    if not values:
        if required:
            parser.error(f"{flag} is required")
        return None
    if len(values) != 1:
        parser.error(f"{flag} must be provided at most once")
    return values[0]


def build_parser() -> UsageParser:
    parser = UsageParser(prog="verify-job.sh", add_help=True)
    parser.add_argument("--receipt", action="append")
    parser.add_argument("--envelope", action="append")
    parser.add_argument("--repo", action="append")
    parser.add_argument("--base", action="append")
    parser.add_argument("--allow", action="append", default=[])
    parser.add_argument("--only", action="append", default=[])
    parser.add_argument("--verify", action="append", default=[])
    parser.add_argument("--verify-env", action="append", default=[])
    parser.add_argument("--expect-edits", action="count", default=0)
    parser.add_argument("--selection", action="append")
    parser.add_argument("--pre-recommendation", action="append")
    return parser


def sanitized_gate_environment() -> dict[str, str]:
    """Build the gate baseline without verifier-only opt-in values."""

    return child_environment([])


def verifier_environment_payload(explicit_names: list[str]) -> bytes:
    """Encode present verifier-only values for the gate's private pipe."""

    records: list[bytes] = []
    for name in explicit_names:
        if name in os.environ:
            records.extend(
                (os.fsencode(name), b"\0", os.fsencode(os.environ[name]), b"\0")
            )
    payload = b"".join(records)
    if len(payload) > MAX_VERIFY_ENV_PAYLOAD:
        raise ProtocolFailure("verifier environment payload is too large")
    return payload


def run_gate(
    gate: Path,
    args: list[str],
    verify_environment: list[str],
    evidence_fd: int,
    controller: SignalController,
) -> int:
    child: subprocess.Popen[bytes] | None = None
    verify_read_fd = -1
    verify_write_fd = -1
    try:
        gate_environment = sanitized_gate_environment()
        evidence_token = secrets.token_hex(32)
        gate_environment["AGY_WORKER_INTERNAL_EVIDENCE_TOKEN"] = evidence_token
        gate_environment["AGY_WORKER_INTERNAL_PYTHON"] = str(
            Path(sys.executable).resolve(strict=True)
        )
        payload = verifier_environment_payload(verify_environment)
        verify_read_fd, verify_write_fd = os.pipe()
        child = subprocess.Popen(
            [
                "/bin/bash",
                str(gate),
                *args,
                "--evidence-fd",
                str(evidence_fd),
                "--evidence-token",
                evidence_token,
                "--verify-env-fd",
                str(verify_read_fd),
            ],
            stdin=subprocess.DEVNULL,
            pass_fds=(evidence_fd, verify_read_fd),
            start_new_session=True,
            env=gate_environment,
        )
        controller.set_group(child.pid)
        os.close(verify_read_fd)
        verify_read_fd = -1
        while payload:
            written = os.write(verify_write_fd, payload)
            payload = payload[written:]
        os.close(verify_write_fd)
        verify_write_fd = -1
        gate_exit = child.wait()
        return gate_exit
    except SignalInterruption:
        if child is not None:
            try:
                os.killpg(child.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            try:
                child.wait(timeout=5)
            except (subprocess.TimeoutExpired, OSError):
                pass
        raise
    except OSError as exc:
        if child is not None:
            try:
                os.killpg(child.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            try:
                child.wait(timeout=5)
            except (subprocess.TimeoutExpired, OSError):
                pass
        raise ProtocolFailure("gate could not start") from exc
    finally:
        for descriptor in (verify_read_fd, verify_write_fd):
            if descriptor >= 0:
                try:
                    os.close(descriptor)
                except OSError:
                    pass
        controller.set_group(None)


def verify_main(
    argv: list[str], runtime_root: Path, controller: SignalController
) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    receipt_text = one(parser, args.receipt, "--receipt", True)
    envelope_text = one(parser, args.envelope, "--envelope", True)
    repo_text = one(parser, args.repo, "--repo", True)
    base = one(parser, args.base, "--base", True)
    selection_text = one(parser, args.selection, "--selection", False)
    recommendation_text = one(
        parser, args.pre_recommendation, "--pre-recommendation", False
    )
    if args.expect_edits > 1:
        parser.error("--expect-edits must be provided at most once")
    if not args.verify or any(not value.strip() for value in args.verify):
        parser.error("at least one non-empty --verify command is required")
    if len(args.verify) > 999:
        parser.error("at most 999 verifier commands are supported")
    try:
        verify_environment = validate_child_environment_names(args.verify_env)
    except EvidenceUnavailable as exc:
        parser.error(str(exc))
    assert receipt_text and envelope_text and repo_text and base

    target = Path(receipt_text)
    repo = Path(repo_text)
    parent, _name = validate_target(target, repo)
    schema_path = runtime_root / "schemas/evidence-receipt.schema.json"
    recommendation_script = runtime_root / "scripts/model-recommendation.py"
    schema = load_schema(schema_path)
    selection = load_selection(Path(selection_text)) if selection_text else None
    recommendation = (
        load_recommendation_for_publication(
            Path(recommendation_text), recommendation_script
        )
        if recommendation_text
        else None
    )
    if selection is not None and recommendation is not None:
        if not selection_matches_recommendation(selection, recommendation):
            raise UsageFailure("selection and recommendation inputs do not match")

    envelope_snapshot: Path | None = None
    handoff_path: Path | None = None
    write_fd = -1
    result: int | None = None
    try:
        envelope_snapshot, envelope_sha256 = snapshot_file(
            Path(envelope_text), parent, controller
        )
        handoff_path, write_fd = private_file(
            parent,
            "agy-receipt-handoff",
            controller=controller,
            checkpoint="handoff-created",
        )
        gate_args = [
            "--envelope",
            str(envelope_snapshot),
            "--repo",
            repo_text,
            "--base",
            base,
        ]
        for value in args.allow:
            gate_args += ["--allow", value]
        for value in args.only:
            gate_args += ["--only", value]
        if args.expect_edits:
            gate_args.append("--expect-edits")
        for value in args.verify:
            gate_args += ["--verify", value]
        for value in verify_environment:
            gate_args += ["--verify-env", value]

        try:
            gate_rc = run_gate(
                runtime_root / "qa-gate.sh", gate_args, verify_environment,
                write_fd, controller
            )
        finally:
            if write_fd >= 0:
                os.close(write_fd)
                write_fd = -1
        if gate_rc == 64:
            result = 64
            return result
        if gate_rc not in GATE_OUTCOMES:
            raise ProtocolFailure("gate returned an internal or interrupted result")
        try:
            handoff_payload = read_real_file(
                handoff_path, "gate evidence", MAX_HANDOFF_BYTES
            )
        except UsageFailure as exc:
            raise ProtocolFailure("gate evidence is unavailable") from exc
        handoff = parse_handoff(handoff_payload)
        if handoff["gate_exit"] != gate_rc:
            raise ProtocolFailure("gate process exit and evidence exit differ")
        if handoff["resolved_base"] != base:
            raise ProtocolFailure("gate resolved a different base")
        if handoff["envelope_sha256"] != envelope_sha256:
            raise ProtocolFailure("gate validated a different envelope snapshot")

        policy = {
            "allow": args.allow,
            "only": args.only,
            "expect_edits": bool(args.expect_edits),
            "verify_environment": verify_environment,
        }
        receipt: dict[str, Any] = {
            "schema_version": 1,
            "kind": "agy-worker-evidence-receipt",
            "gate_authority": "qa-gate",
            "resolved_base": handoff["resolved_base"],
            "envelope_sha256": handoff["envelope_sha256"],
            "path_policy_sha256": sha256_bytes(canonical_bytes(policy)),
            "verifiers": [
                {
                    "label": f"verify-{index:03d}",
                    "command_sha256": sha256_bytes(command.encode("utf-8")),
                }
                for index, command in enumerate(args.verify, 1)
            ],
            "initial_candidate_state_sha256": handoff[
                "initial_candidate_state_sha256"
            ],
            "final_candidate_state_sha256": handoff[
                "final_candidate_state_sha256"
            ],
            "gate_exit": gate_rc,
            "gate_outcome": handoff["gate_outcome"],
            "verdict": VERDICTS[gate_rc],
            "recommendations_participated_in_acceptance": False,
            "integrity": {
                "signed": False,
                "tamper_evident": False,
                "statement": INTEGRITY_STATEMENT,
            },
        }
        if selection is not None:
            receipt["caller_selection"] = selection
        if recommendation is not None:
            receipt["pre_dispatch_recommendation"] = recommendation
        validate_receipt(receipt, schema)
        publish_receipt(
            target,
            parent,
            receipt,
            schema,
            None,
            controller,
        )
        result = gate_rc
    except SignalInterruption:
        controller.remove_registered_publication()
        raise
    finally:
        interruption_checkpoint("wrapper-cleanup-start")
        if write_fd >= 0:
            os.close(write_fd)
        for private_path in (envelope_snapshot, handoff_path):
            if private_path is not None:
                try:
                    private_path.unlink(missing_ok=True)
                except OSError:
                    pass
                controller.clear_private(private_path)
        try:
            cleanup_fd = os.open(parent, os.O_RDONLY)
            try:
                interruption_checkpoint("wrapper-cleanup-parent-fsync")
                os.fsync(cleanup_fd)
            finally:
                os.close(cleanup_fd)
        except OSError:
            pass
    if result is None:
        raise ProtocolFailure("gate result was not established")
    controller.clear_publication()
    return result


def validate_main(argv: list[str], runtime_root: Path) -> int:
    parser = UsageParser(prog="evidence-receipt-validator")
    parser.add_argument("--receipt", action="append")
    parser.add_argument("--envelope", action="append")
    parser.add_argument("--selection", action="append")
    parser.add_argument("--pre-recommendation", action="append")
    parser.add_argument("--initial-state-digest", action="append")
    parser.add_argument("--final-state-digest", action="append")
    parsed = parser.parse_args(argv)
    receipt_text = one(parser, parsed.receipt, "--receipt", True)
    envelope_text = one(parser, parsed.envelope, "--envelope", False)
    selection_text = one(parser, parsed.selection, "--selection", False)
    recommendation_text = one(
        parser, parsed.pre_recommendation, "--pre-recommendation", False
    )
    initial_digest = one(
        parser, parsed.initial_state_digest, "--initial-state-digest", False
    )
    final_digest = one(
        parser, parsed.final_state_digest, "--final-state-digest", False
    )
    assert receipt_text
    schema = load_schema(runtime_root / "schemas/evidence-receipt.schema.json")
    value = parse_json_bytes(
        read_real_file(Path(receipt_text), "receipt"), "receipt"
    )
    receipt = validate_receipt(value, schema)
    if envelope_text:
        payload = read_real_file(Path(envelope_text), "bound envelope")
        if sha256_bytes(payload) != receipt["envelope_sha256"]:
            raise ValidationFailure("bound envelope digest does not match receipt")
    if selection_text:
        selection = load_selection(Path(selection_text))
        if receipt.get("caller_selection") != selection:
            raise ValidationFailure("bound selection does not match receipt")
    if recommendation_text:
        recommendation = load_recommendation_record(Path(recommendation_text))
        if receipt.get("pre_dispatch_recommendation") != recommendation:
            raise ValidationFailure("bound recommendation does not match receipt")
    if initial_digest:
        require_sha(initial_digest, "bound initial state digest")
        if receipt["initial_candidate_state_sha256"] != initial_digest:
            raise ValidationFailure("bound initial state digest does not match receipt")
    if final_digest:
        require_sha(final_digest, "bound final state digest")
        if receipt["final_candidate_state_sha256"] != final_digest:
            raise ValidationFailure("bound final state digest does not match receipt")
    return 0


def main(argv: list[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    runtime_root = Path(__file__).resolve().parent.parent
    if not arguments or arguments[0] not in ("verify", "validate"):
        print("usage: evidence_receipt.py verify|validate ...", file=sys.stderr)
        return 64
    command = arguments.pop(0)
    try:
        if command == "verify":
            with SignalController() as controller:
                try:
                    return verify_main(arguments, runtime_root, controller)
                except SignalInterruption:
                    controller.cleanup_all()
                    raise
        return validate_main(arguments, runtime_root)
    except UsageFailure as exc:
        print(f"verify-job: invalid input - {exc}", file=sys.stderr)
        return 64
    except ProtocolFailure:
        print("verify-job: gate evidence protocol failed", file=sys.stderr)
        return 70
    except ValidationFailure as exc:
        if command == "validate":
            print(f"evidence receipt invalid: {exc}", file=sys.stderr)
            return 1
        print("verify-job: receipt publication failed", file=sys.stderr)
        return 74
    except PublicationFailure:
        print("verify-job: receipt publication failed", file=sys.stderr)
        return 74


if __name__ == "__main__":
    raise SystemExit(main())
