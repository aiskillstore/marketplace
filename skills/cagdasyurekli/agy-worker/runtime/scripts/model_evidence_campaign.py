#!/usr/bin/env python3
"""Model Evidence Campaign: provider-independent offline incremental new-model evidence campaigns."""

from __future__ import annotations

import copy
import datetime
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import secrets
import stat
import sys
from typing import Any, Sequence

sys.dont_write_bytecode = True

MAX_JSON_BYTES = 512 * 1024
MAX_DATASET_BYTES = 512 * 1024
SHA256_RE = re.compile(r"^[0-9a-f]{64}\Z")
DATE_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}\Z")
SAFE_ID_RE = re.compile(r"^[a-zA-Z0-9._:+-]{1,100}\Z")
BINDING_KEY_RE = re.compile(r"^[a-z_]{1,50}\Z")
SOURCE_URI_RE = re.compile(r"^(?:https://[a-zA-Z0-9_./-]{1,2000}|local://[a-zA-Z0-9_./-]{1,2000})\Z")
VALID_LANES = {"vendor_declared", "measured", "observational"}
WORKFLOW_CATEGORIES = ("explore", "task", "project", "benchmark", "other")
IDENTITY_STATUSES = ("match", "mismatch", "missing", "substituted")
SUBJECT_RATIONALE_CODES = {
    "within-bounds",
    "lane-limitation",
    "identity-mismatch",
    "model-substituted",
    "observed-model-missing",
    "scenario-drift",
    "harness-drift",
    "evaluator-drift",
    "config-drift",
    "policy-drift",
    "window-drift",
    "telemetry-incompatible",
    "insufficient-coverage",
    "budget-exhausted",
    "insufficient-samples",
    "drift-exceeded",
    "error-rate-exceeded",
    "verification-failed",
    "uncertainty-exceeded",
}
RECORD_LIMITATION_CODES = {
    "identity-observation-caller-supplied",
    "observational-evidence-not-measured",
    "provider-declaration-not-measurement",
    "token-telemetry-not-billing-evidence",
}

TOKEN_DISCLAIMER = (
    "Token observations are telemetry counts only and must never be used to "
    "infer billing, quota, allowance, or general cost savings."
)

PROHIBITED_FLAGS = {
    "--send",
    "--sender",
    "--endpoint",
    "--watch",
    "--background",
    "--upload",
    "--remote",
    "--url",
    "--server",
    "--host",
    "--port",
    "--ws",
    "--daemon",
}

EVALUATION_REASON_CODES = {
    "verified-measured-evidence",
    "anchor-drift",
    "trigger-drift",
    "identity-mismatch",
    "model-substituted",
    "observed-model-missing",
    "missing-subject",
    "unexpected-subject",
    "scenario-drift",
    "harness-drift",
    "evaluator-drift",
    "config-drift",
    "policy-drift",
    "window-drift",
    "telemetry-incompatible",
    "insufficient-coverage",
    "budget-exhausted",
    "insufficient-samples",
    "drift-exceeded",
    "error-rate-exceeded",
    "verification-failed",
    "uncertainty-exceeded",
    "lane-limitation",
}


class ModelEvidenceCampaignError(Exception):
    """Model evidence campaign validation, structural, privacy, or bounds failure."""


def canonical_bytes(data: Any) -> bytes:
    return json.dumps(
        data, ensure_ascii=True, allow_nan=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _reject_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ModelEvidenceCampaignError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_nonfinite_json(value: str) -> None:
    raise ModelEvidenceCampaignError(f"non-finite JSON number is forbidden: {value}")


def _bounded_number(value: Any, label: str, minimum: float, maximum: float) -> float:
    if (
        not isinstance(value, (int, float))
        or isinstance(value, bool)
        or not math.isfinite(value)
        or not minimum <= float(value) <= maximum
    ):
        raise ModelEvidenceCampaignError(
            f"{label} must be a finite number between {minimum} and {maximum}"
        )
    return float(value)


def _workflow_category(scenario_id: str) -> str:
    """Reduce a private scenario identifier to one closed, non-identifying category."""
    tokens = {token for token in re.split(r"[._:+-]+", scenario_id.lower()) if token}
    if "benchmark" in tokens or "swebench" in tokens or {"swe", "bench"}.issubset(tokens):
        return "benchmark"
    if tokens.intersection({"explore", "exploration"}):
        return "explore"
    if "task" in tokens:
        return "task"
    if "project" in tokens:
        return "project"
    return "other"


def _scenario_version(scenario_id: str) -> str | None:
    """Expose only a terminal version token, never the scenario identifier itself."""
    match = re.search(r"(?:^|[._:+-])(v[0-9]+(?:[._-][0-9]+)*)\Z", scenario_id.lower())
    return match.group(1) if match else None


def _identity_status(record: dict[str, Any]) -> str:
    identity = record["model_identity"]
    if identity["observed_model"] is None:
        return "missing"
    if identity["substituted"] is True:
        return "substituted"
    if identity["requested_model"] != identity["observed_model"]:
        return "mismatch"
    return "match"


def _model_intelligence_module() -> Any:
    module_path = Path(__file__).resolve().with_name("model_intelligence.py")
    spec = importlib.util.spec_from_file_location("agy_model_intelligence_campaign_dependency", module_path)
    if spec is None or spec.loader is None:
        raise ModelEvidenceCampaignError("Model Intelligence validator is unavailable")
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as exc:
        raise ModelEvidenceCampaignError("Model Intelligence validator is unavailable") from exc
    return module


def parse_iso_date(date_str: Any, label: str) -> datetime.date:
    if not isinstance(date_str, str) or not DATE_RE.fullmatch(date_str):
        raise ModelEvidenceCampaignError(f"{label} is not a valid ISO date (YYYY-MM-DD): {date_str!r}")
    try:
        year, month, day = map(int, date_str.split("-"))
        return datetime.date(year, month, day)
    except (ValueError, OverflowError):
        raise ModelEvidenceCampaignError(f"{label} is an invalid calendar date: {date_str!r}") from None


def read_json_file(file_path: Path, max_bytes: int = MAX_JSON_BYTES) -> tuple[dict[str, Any], str, bytes]:
    target = Path(os.path.abspath(os.fspath(file_path)))
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
    try:
        before = os.lstat(target)
        if not stat.S_ISREG(before.st_mode) or before.st_size > max_bytes:
            raise ModelEvidenceCampaignError(f"file is not a bounded regular file: {target}")
        fd = os.open(target, flags)
        try:
            opened = os.fstat(fd)
            if (
                not stat.S_ISREG(opened.st_mode)
                or (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino)
                or opened.st_size > max_bytes
            ):
                raise ModelEvidenceCampaignError("file changed before reading")
            chunks: list[bytes] = []
            total = 0
            while True:
                chunk = os.read(fd, min(8192, max_bytes + 1 - total))
                if not chunk:
                    break
                chunks.append(chunk)
                total += len(chunk)
                if total > max_bytes:
                    raise ModelEvidenceCampaignError("file exceeded maximum byte size")
        finally:
            os.close(fd)
    except OSError as exc:
        raise ModelEvidenceCampaignError(f"cannot read file safely: {exc}") from exc

    raw = b"".join(chunks)
    digest = hashlib.sha256(raw).hexdigest()
    try:
        parsed = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_reject_duplicate_pairs,
            parse_constant=_reject_nonfinite_json,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ModelEvidenceCampaignError) as exc:
        raise ModelEvidenceCampaignError(f"file contains invalid JSON: {exc}") from exc
    if not isinstance(parsed, dict):
        raise ModelEvidenceCampaignError("JSON root must be an object")
    return parsed, digest, raw


def _directory_identity(metadata: os.stat_result) -> tuple[int, int, int, int, int]:
    return (
        metadata.st_dev,
        metadata.st_ino,
        metadata.st_uid,
        metadata.st_gid,
        metadata.st_mode,
    )


def _open_private_parent_no_follow(
    parent: Path,
) -> tuple[int, tuple[tuple[str, tuple[int, int, int, int, int]], ...]]:
    """Open an absolute parent by walking every real directory component."""
    if not parent.is_absolute() or any(part in {"", ".", ".."} for part in parent.parts[1:]):
        raise ModelEvidenceCampaignError("output parent path must be absolute and canonical")
    directory_flags = (
        os.O_RDONLY
        | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_NOFOLLOW", 0)
        | getattr(os, "O_CLOEXEC", 0)
    )
    current_fd = -1
    identities: list[tuple[str, tuple[int, int, int, int, int]]] = []
    try:
        current_fd = os.open("/", directory_flags)
        root_metadata = os.fstat(current_fd)
        if not stat.S_ISDIR(root_metadata.st_mode) or stat.S_ISLNK(root_metadata.st_mode):
            raise ModelEvidenceCampaignError("filesystem root is not one real directory")
        identities.append(("/", _directory_identity(root_metadata)))
        for component in parent.parts[1:]:
            before = os.stat(component, dir_fd=current_fd, follow_symlinks=False)
            if not stat.S_ISDIR(before.st_mode) or stat.S_ISLNK(before.st_mode):
                raise ModelEvidenceCampaignError("output parent path contains a non-directory or symlink")
            next_fd = -1
            try:
                next_fd = os.open(component, directory_flags, dir_fd=current_fd)
                opened = os.fstat(next_fd)
                if _directory_identity(opened) != _directory_identity(before):
                    raise ModelEvidenceCampaignError("output parent ancestor changed during traversal")
            except Exception:
                if next_fd >= 0:
                    os.close(next_fd)
                raise
            os.close(current_fd)
            current_fd = next_fd
            identities.append((component, _directory_identity(opened)))
        final_metadata = os.fstat(current_fd)
        if (
            final_metadata.st_uid != os.getuid()
            or stat.S_IMODE(final_metadata.st_mode) != 0o700
        ):
            raise ModelEvidenceCampaignError("output parent must be owner-controlled mode 0700")
        return current_fd, tuple(identities)
    except OSError as exc:
        if current_fd >= 0:
            os.close(current_fd)
        raise ModelEvidenceCampaignError("output parent traversal failed closed") from exc
    except Exception:
        if current_fd >= 0:
            os.close(current_fd)
        raise


def publish_file_atomically(path: Path, data: bytes) -> None:
    path = Path(os.fspath(path))
    if not path.is_absolute() or path.name in {"", ".", ".."}:
        raise ModelEvidenceCampaignError("output path must be an absolute file path")
    parent = path.parent
    parent_fd, parent_chain = _open_private_parent_no_follow(parent)
    descriptor = -1
    temporary_name = f".{path.name}.{os.getpid()}.{secrets.token_hex(8)}.tmp"
    temporary_identity: tuple[int, int] | None = None
    published_identity: tuple[int, int] | None = None
    completed = False
    try:
        try:
            os.stat(path.name, dir_fd=parent_fd, follow_symlinks=False)
        except FileNotFoundError:
            pass
        else:
            raise ModelEvidenceCampaignError(f"output path already exists: {path}")

        descriptor = os.open(
            temporary_name,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
            0o600,
            dir_fd=parent_fd,
        )
        opened_temporary = os.fstat(descriptor)
        temporary_identity = (opened_temporary.st_dev, opened_temporary.st_ino)
        os.fchmod(descriptor, 0o600)
        view = memoryview(data)
        while view:
            written = os.write(descriptor, view)
            if written <= 0:
                raise ModelEvidenceCampaignError("temporary file write failed")
            view = view[written:]
        os.fsync(descriptor)
        written_st = os.fstat(descriptor)
        if (
            not stat.S_ISREG(written_st.st_mode)
            or written_st.st_uid != os.getuid()
            or stat.S_IMODE(written_st.st_mode) != 0o600
            or written_st.st_size != len(data)
        ):
            raise ModelEvidenceCampaignError("temporary file write size mismatch")
        os.close(descriptor)
        descriptor = -1

        try:
            os.link(
                temporary_name, path.name,
                src_dir_fd=parent_fd, dst_dir_fd=parent_fd, follow_symlinks=False,
            )
        except FileExistsError as exc:
            raise ModelEvidenceCampaignError(f"output path already exists: {path}") from exc
        published_st = os.stat(path.name, dir_fd=parent_fd, follow_symlinks=False)
        published_identity = (published_st.st_dev, published_st.st_ino)
        if (
            (published_st.st_dev, published_st.st_ino) != (written_st.st_dev, written_st.st_ino)
            or published_st.st_uid != os.getuid()
            or stat.S_IMODE(published_st.st_mode) != 0o600
            or published_st.st_size != len(data)
        ):
            raise ModelEvidenceCampaignError("published output identity mismatch")
        os.unlink(temporary_name, dir_fd=parent_fd)
        os.fsync(parent_fd)
        verification_fd, verified_chain = _open_private_parent_no_follow(parent)
        try:
            if (
                verified_chain != parent_chain
                or _directory_identity(os.fstat(verification_fd))
                != _directory_identity(os.fstat(parent_fd))
            ):
                raise ModelEvidenceCampaignError("output parent changed during publication")
        finally:
            os.close(verification_fd)
        completed = True
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        if parent_fd >= 0:
            if not completed and published_identity is not None:
                try:
                    cleanup_published = os.stat(path.name, dir_fd=parent_fd, follow_symlinks=False)
                    if (cleanup_published.st_dev, cleanup_published.st_ino) == published_identity:
                        os.unlink(path.name, dir_fd=parent_fd)
                except FileNotFoundError:
                    pass
            try:
                cleanup_temporary = os.stat(
                    temporary_name, dir_fd=parent_fd, follow_symlinks=False
                )
                if temporary_identity is not None and (
                    cleanup_temporary.st_dev, cleanup_temporary.st_ino
                ) == temporary_identity:
                    os.unlink(temporary_name, dir_fd=parent_fd)
            except FileNotFoundError:
                pass
            os.close(parent_fd)


def validate_plan(plan: Any) -> dict[str, Any]:
    if not isinstance(plan, dict):
        raise ModelEvidenceCampaignError("plan must be an object")
    allowed_keys = {
        "schema_version",
        "kind",
        "lane",
        "candidate_model_id",
        "anchor_model_ids",
        "anchors",
        "trigger",
        "scenario_id",
        "harness",
        "evaluator",
        "config_sha256",
        "measurement_window",
        "policy",
        "acceptance_rules",
        "budget",
        "drift_tolerance",
        "required_telemetry",
        "limitations",
    }
    if set(plan.keys()) != allowed_keys:
        raise ModelEvidenceCampaignError("plan keys do not match strict schema")

    if plan["schema_version"] != 1 or isinstance(plan["schema_version"], bool):
        raise ModelEvidenceCampaignError("plan schema_version must be integer 1")
    if plan["kind"] != "agy-model-evidence-campaign-plan":
        raise ModelEvidenceCampaignError("plan kind must be agy-model-evidence-campaign-plan")
    if plan["lane"] not in VALID_LANES:
        raise ModelEvidenceCampaignError(f"invalid plan lane: {plan['lane']!r}")

    if not isinstance(plan["candidate_model_id"], str) or not SAFE_ID_RE.fullmatch(plan["candidate_model_id"]):
        raise ModelEvidenceCampaignError(f"invalid candidate_model_id: {plan['candidate_model_id']!r}")

    # Anchor Model IDs
    anchor_model_ids = plan["anchor_model_ids"]
    if not isinstance(anchor_model_ids, list) or not (1 <= len(anchor_model_ids) <= 20):
        raise ModelEvidenceCampaignError("anchor_model_ids must be a non-empty list of at most 20 model IDs")
    for a in anchor_model_ids:
        if not isinstance(a, str) or not SAFE_ID_RE.fullmatch(a):
            raise ModelEvidenceCampaignError(f"invalid anchor model ID: {a!r}")
    if len(set(anchor_model_ids)) != len(anchor_model_ids):
        raise ModelEvidenceCampaignError("anchor_model_ids contains duplicate model IDs")
    if plan["candidate_model_id"] in anchor_model_ids:
        raise ModelEvidenceCampaignError("candidate_model_id cannot also be an anchor")

    # Anchors
    anchors = plan["anchors"]
    if not isinstance(anchors, dict) or set(anchors.keys()) != {
        "benchmark_review_sha256",
        "inventory_binding_sha256",
        "model_matrix_sha256",
        "dataset_sha256",
    }:
        raise ModelEvidenceCampaignError("plan anchors must strictly contain 4 SHA-256 digests")
    for key in anchors:
        if not isinstance(anchors[key], str) or not SHA256_RE.fullmatch(anchors[key]):
            raise ModelEvidenceCampaignError(f"invalid anchor digest for {key}: {anchors[key]!r}")

    # Trigger
    trigger = plan["trigger"]
    if not isinstance(trigger, dict) or set(trigger.keys()) != {
        "benchmark_review_status",
        "review_reason",
        "maintainer_disposition",
    }:
        raise ModelEvidenceCampaignError("plan trigger must strictly contain benchmark_review_status, review_reason, maintainer_disposition")
    if trigger["benchmark_review_status"] != "benchmark-review-due":
        raise ModelEvidenceCampaignError(f"plan trigger benchmark_review_status must be 'benchmark-review-due', got {trigger['benchmark_review_status']!r}")
    if trigger["review_reason"] != "inventory-added":
        raise ModelEvidenceCampaignError(f"plan trigger review_reason must be 'inventory-added', got {trigger['review_reason']!r}")
    if trigger["maintainer_disposition"] != "collect":
        raise ModelEvidenceCampaignError(f"plan trigger maintainer_disposition must be 'collect', got {trigger['maintainer_disposition']!r}")

    if not isinstance(plan["scenario_id"], str) or not SAFE_ID_RE.fullmatch(plan["scenario_id"]):
        raise ModelEvidenceCampaignError(f"invalid scenario_id: {plan['scenario_id']!r}")

    # Harness & Evaluator
    for sub in ("harness", "evaluator", "policy"):
        obj = plan[sub]
        if not isinstance(obj, dict) or set(obj.keys()) != {"id", "version"}:
            raise ModelEvidenceCampaignError(f"plan {sub} must contain strictly id and version")
        if not isinstance(obj["id"], str) or not SAFE_ID_RE.fullmatch(obj["id"]):
            raise ModelEvidenceCampaignError(f"invalid id in plan {sub}")
        if not isinstance(obj["version"], str) or not SAFE_ID_RE.fullmatch(obj["version"]):
            raise ModelEvidenceCampaignError(f"invalid version in plan {sub}")

    if not isinstance(plan["config_sha256"], str) or not SHA256_RE.fullmatch(plan["config_sha256"]):
        raise ModelEvidenceCampaignError(f"invalid config_sha256: {plan['config_sha256']!r}")

    # Measurement window
    mw = plan["measurement_window"]
    if not isinstance(mw, dict) or set(mw.keys()) != {"start_date", "end_date"}:
        raise ModelEvidenceCampaignError("plan measurement_window must contain strictly start_date and end_date")
    start_dt = parse_iso_date(mw["start_date"], "measurement_window.start_date")
    end_dt = parse_iso_date(mw["end_date"], "measurement_window.end_date")
    if start_dt > end_dt:
        raise ModelEvidenceCampaignError("measurement_window start_date cannot be after end_date")

    # Acceptance rules
    ar = plan["acceptance_rules"]
    if not isinstance(ar, dict) or not {"min_sample_size", "min_coverage", "max_error_rate", "uncertainty_rule"}.issubset(set(ar.keys())):
        raise ModelEvidenceCampaignError("plan acceptance_rules missing required keys")
    if set(ar.keys()) - {"min_sample_size", "min_coverage", "max_error_rate", "min_quality_score", "uncertainty_rule"}:
        raise ModelEvidenceCampaignError("plan acceptance_rules has extra disallowed keys")
    if not isinstance(ar["min_sample_size"], int) or isinstance(ar["min_sample_size"], bool) or not 1 <= ar["min_sample_size"] <= 10_000_000:
        raise ModelEvidenceCampaignError("min_sample_size must be an integer between 1 and 10,000,000")
    if not isinstance(ar["min_coverage"], (int, float)) or isinstance(ar["min_coverage"], bool) or not (0.0 <= ar["min_coverage"] <= 1.0):
        raise ModelEvidenceCampaignError("min_coverage must be a float between 0.0 and 1.0")
    if not isinstance(ar["max_error_rate"], (int, float)) or isinstance(ar["max_error_rate"], bool) or not (0.0 <= ar["max_error_rate"] <= 1.0):
        raise ModelEvidenceCampaignError("max_error_rate must be a float between 0.0 and 1.0")
    if "min_quality_score" in ar and ar["min_quality_score"] is not None:
        if not isinstance(ar["min_quality_score"], (int, float)) or isinstance(ar["min_quality_score"], bool) or not (0.0 <= ar["min_quality_score"] <= 100.0):
            raise ModelEvidenceCampaignError("min_quality_score must be between 0.0 and 100.0 or null")
    ur = ar["uncertainty_rule"]
    if not isinstance(ur, dict) or set(ur.keys()) != {"max_uncertainty"}:
        raise ModelEvidenceCampaignError("uncertainty_rule must contain strictly max_uncertainty")
    _bounded_number(ur["max_uncertainty"], "max_uncertainty", 0.0, 100.0)

    # Budget
    budget = plan["budget"]
    if not isinstance(budget, dict) or set(budget.keys()) != {"sample_budget", "invocation_budget"}:
        raise ModelEvidenceCampaignError("plan budget must contain strictly sample_budget and invocation_budget")
    if not isinstance(budget["sample_budget"], int) or isinstance(budget["sample_budget"], bool) or not 1 <= budget["sample_budget"] <= 10_000_000:
        raise ModelEvidenceCampaignError("sample_budget must be an integer between 1 and 10,000,000")
    if not isinstance(budget["invocation_budget"], int) or isinstance(budget["invocation_budget"], bool) or not 1 <= budget["invocation_budget"] <= 10_000_000:
        raise ModelEvidenceCampaignError("invocation_budget must be an integer between 1 and 10,000,000")

    # Drift tolerance
    dt = plan["drift_tolerance"]
    if not isinstance(dt, dict) or set(dt.keys()) != {"max_drift_fraction"}:
        raise ModelEvidenceCampaignError("drift_tolerance must contain strictly max_drift_fraction")
    if not isinstance(dt["max_drift_fraction"], (int, float)) or isinstance(dt["max_drift_fraction"], bool) or not (0.0 <= dt["max_drift_fraction"] <= 1.0):
        raise ModelEvidenceCampaignError("max_drift_fraction must be between 0.0 and 1.0")

    # Required telemetry
    rt = plan["required_telemetry"]
    if not isinstance(rt, dict) or set(rt.keys()) != {"bindings", "min_coverage"}:
        raise ModelEvidenceCampaignError("required_telemetry must contain strictly bindings and min_coverage")
    if not isinstance(rt["bindings"], list) or not (1 <= len(rt["bindings"]) <= 20):
        raise ModelEvidenceCampaignError("required_telemetry.bindings must be a list of 1 to 20 strings")
    for b in rt["bindings"]:
        if not isinstance(b, str) or not BINDING_KEY_RE.fullmatch(b):
            raise ModelEvidenceCampaignError(f"invalid telemetry binding key: {b!r}")
    if not isinstance(rt["min_coverage"], (int, float)) or isinstance(rt["min_coverage"], bool) or not (0.0 <= rt["min_coverage"] <= 1.0):
        raise ModelEvidenceCampaignError("required_telemetry.min_coverage must be between 0.0 and 1.0")

    # Limitations
    if (
        not isinstance(plan["limitations"], list)
        or not (1 <= len(plan["limitations"]) <= 20)
        or any(not isinstance(it, str) or not (1 <= len(it) <= 1000) for it in plan["limitations"])
    ):
        raise ModelEvidenceCampaignError("limitations must be a list of 1 to 20 bounded strings")

    return plan


def validate_record(record: Any) -> dict[str, Any]:
    if not isinstance(record, dict):
        raise ModelEvidenceCampaignError("record must be an object")
    allowed_keys = {
        "schema_version",
        "kind",
        "plan_sha256",
        "lane",
        "subject_role",
        "model_identity",
        "scenario_id",
        "harness",
        "evaluator",
        "config_sha256",
        "measurement_window",
        "policy",
        "measured_metadata",
        "telemetry",
        "limitations",
    }
    if set(record.keys()) != allowed_keys:
        raise ModelEvidenceCampaignError("record keys do not match strict schema")

    if record["schema_version"] != 1 or isinstance(record["schema_version"], bool):
        raise ModelEvidenceCampaignError("record schema_version must be integer 1")
    if record["kind"] != "agy-model-evidence-campaign-record":
        raise ModelEvidenceCampaignError("record kind must be agy-model-evidence-campaign-record")
    if not isinstance(record["plan_sha256"], str) or not SHA256_RE.fullmatch(record["plan_sha256"]):
        raise ModelEvidenceCampaignError(f"invalid plan_sha256: {record['plan_sha256']!r}")
    if record["lane"] not in VALID_LANES:
        raise ModelEvidenceCampaignError(f"invalid record lane: {record['lane']!r}")
    if record["subject_role"] not in {"candidate", "anchor"}:
        raise ModelEvidenceCampaignError(f"invalid subject_role: {record['subject_role']!r}")

    # Privacy check: strictly forbidden keys anywhere in the record
    forbidden_terms = {
        "prompt", "prompts", "output", "outputs", "code", "diff", "diffs",
        "command", "commands", "log", "logs", "free_text", "path", "paths",
        "endpoint", "endpoints", "sender", "user", "author", "timestamp", "timestamps"
    }
    for k in record.keys():
        if k in forbidden_terms:
            raise ModelEvidenceCampaignError(f"record contains forbidden field: {k}")

    # Model identity
    mid = record["model_identity"]
    if not isinstance(mid, dict) or set(mid.keys()) != {"requested_model", "observed_model", "substituted"}:
        raise ModelEvidenceCampaignError("model_identity must strictly contain requested_model, observed_model, substituted")
    if not isinstance(mid["requested_model"], str) or not SAFE_ID_RE.fullmatch(mid["requested_model"]):
        raise ModelEvidenceCampaignError(f"invalid requested_model: {mid['requested_model']!r}")
    if mid["observed_model"] is not None:
        if not isinstance(mid["observed_model"], str) or not SAFE_ID_RE.fullmatch(mid["observed_model"]):
            raise ModelEvidenceCampaignError(f"invalid observed_model: {mid['observed_model']!r}")
    if mid["substituted"] is not None and not isinstance(mid["substituted"], bool):
        raise ModelEvidenceCampaignError("substituted must be boolean or null")

    if not isinstance(record["scenario_id"], str) or not SAFE_ID_RE.fullmatch(record["scenario_id"]):
        raise ModelEvidenceCampaignError(f"invalid scenario_id: {record['scenario_id']!r}")

    for sub in ("harness", "evaluator", "policy"):
        obj = record[sub]
        if not isinstance(obj, dict) or set(obj.keys()) != {"id", "version"}:
            raise ModelEvidenceCampaignError(f"record {sub} must contain strictly id and version")
        if not isinstance(obj["id"], str) or not SAFE_ID_RE.fullmatch(obj["id"]):
            raise ModelEvidenceCampaignError(f"invalid id in record {sub}")
        if not isinstance(obj["version"], str) or not SAFE_ID_RE.fullmatch(obj["version"]):
            raise ModelEvidenceCampaignError(f"invalid version in record {sub}")

    if not isinstance(record["config_sha256"], str) or not SHA256_RE.fullmatch(record["config_sha256"]):
        raise ModelEvidenceCampaignError(f"invalid config_sha256: {record['config_sha256']!r}")

    measured_metadata = record["measured_metadata"]
    if record["lane"] != "measured":
        if measured_metadata is not None:
            raise ModelEvidenceCampaignError("non-measured records must set measured_metadata to null")
    else:
        measured_keys = {
            "provenance_type", "source_uri", "agy_version", "effort", "accounting",
            "tokenizer", "currency", "cost_basis", "confidence", "observed_date",
            "expiry_date",
        }
        if not isinstance(measured_metadata, dict) or set(measured_metadata) != measured_keys:
            raise ModelEvidenceCampaignError("measured records require strict measured_metadata")
        if measured_metadata["provenance_type"] not in {"independent", "local"}:
            raise ModelEvidenceCampaignError("measured provenance_type must be independent or local")
        if not isinstance(measured_metadata["source_uri"], str) or not SOURCE_URI_RE.fullmatch(measured_metadata["source_uri"]):
            raise ModelEvidenceCampaignError("measured source_uri is invalid")
        for key in ("agy_version", "accounting", "tokenizer", "currency"):
            if not isinstance(measured_metadata[key], str) or not SAFE_ID_RE.fullmatch(measured_metadata[key]):
                raise ModelEvidenceCampaignError(f"measured {key} is invalid")
        if measured_metadata["effort"] not in {"low", "medium", "high", "none", "unspecified"}:
            raise ModelEvidenceCampaignError("measured effort is invalid")
        if measured_metadata["cost_basis"] not in {"observed_billed", "version_bound_list_price"}:
            raise ModelEvidenceCampaignError("measured cost_basis is invalid")
        if measured_metadata["confidence"] not in {"high", "medium", "low"}:
            raise ModelEvidenceCampaignError("measured confidence is invalid")
        parse_iso_date(measured_metadata["observed_date"], "measured observed_date")
        parse_iso_date(measured_metadata["expiry_date"], "measured expiry_date")

    mw = record["measurement_window"]
    if not isinstance(mw, dict) or set(mw.keys()) != {"start_date", "end_date"}:
        raise ModelEvidenceCampaignError("record measurement_window must contain strictly start_date and end_date")
    start_dt = parse_iso_date(mw["start_date"], "record measurement_window.start_date")
    end_dt = parse_iso_date(mw["end_date"], "record measurement_window.end_date")
    if start_dt > end_dt:
        raise ModelEvidenceCampaignError("record measurement_window start_date cannot be after end_date")

    if isinstance(measured_metadata, dict):
        observed_date = parse_iso_date(measured_metadata["observed_date"], "measured observed_date")
        expiry_date = parse_iso_date(measured_metadata["expiry_date"], "measured expiry_date")
        if not start_dt <= observed_date <= end_dt or expiry_date < observed_date:
            raise ModelEvidenceCampaignError("measured dates are outside the frozen window or invalid")

    # Telemetry
    telem = record["telemetry"]
    if not isinstance(telem, dict):
        raise ModelEvidenceCampaignError("record telemetry must be an object")
    allowed_telem_keys = {
        "sample_count",
        "invocation_count",
        "telemetry_bindings",
        "coverage",
        "error_rate",
        "drift_fraction",
        "metrics",
        "uncertainty",
        "verification_passed",
    }
    if set(telem.keys()) != allowed_telem_keys:
        raise ModelEvidenceCampaignError("record telemetry keys do not match strict schema")

    if not isinstance(telem["sample_count"], int) or isinstance(telem["sample_count"], bool) or not 0 <= telem["sample_count"] <= 10_000_000:
        raise ModelEvidenceCampaignError("sample_count must be an integer between 0 and 10,000,000")
    if not isinstance(telem["invocation_count"], int) or isinstance(telem["invocation_count"], bool) or not 0 <= telem["invocation_count"] <= 10_000_000:
        raise ModelEvidenceCampaignError("invocation_count must be an integer between 0 and 10,000,000")

    if not isinstance(telem["telemetry_bindings"], list) or len(telem["telemetry_bindings"]) > 20:
        raise ModelEvidenceCampaignError("telemetry_bindings must be a list of at most 20 strings")
    for b in telem["telemetry_bindings"]:
        if not isinstance(b, str) or not BINDING_KEY_RE.fullmatch(b):
            raise ModelEvidenceCampaignError(f"invalid telemetry binding in record: {b!r}")

    if not isinstance(telem["coverage"], (int, float)) or isinstance(telem["coverage"], bool) or not (0.0 <= telem["coverage"] <= 1.0):
        raise ModelEvidenceCampaignError("coverage must be between 0.0 and 1.0")
    if not isinstance(telem["error_rate"], (int, float)) or isinstance(telem["error_rate"], bool) or not (0.0 <= telem["error_rate"] <= 1.0):
        raise ModelEvidenceCampaignError("error_rate must be between 0.0 and 1.0")
    if not isinstance(telem["drift_fraction"], (int, float)) or isinstance(telem["drift_fraction"], bool) or not (0.0 <= telem["drift_fraction"] <= 1.0):
        raise ModelEvidenceCampaignError("drift_fraction must be between 0.0 and 1.0")

    metrics = telem["metrics"]
    if not isinstance(metrics, dict):
        raise ModelEvidenceCampaignError("metrics must be an object")
    allowed_metric_keys = {
        "quality_score",
        "latency_p50_seconds",
        "latency_p95_seconds",
        "mean_input_tokens",
        "mean_output_tokens",
        "mean_cached_tokens",
        "mean_thinking_tokens",
        "estimated_cost_usd",
    }
    if set(metrics.keys()) - allowed_metric_keys:
        raise ModelEvidenceCampaignError("metrics contains extra disallowed keys")
    metric_maxima = {
        "quality_score": 100.0,
        "latency_p50_seconds": 1_000_000.0,
        "latency_p95_seconds": 1_000_000.0,
        "mean_input_tokens": 1_000_000_000.0,
        "mean_output_tokens": 1_000_000_000.0,
        "mean_cached_tokens": 1_000_000_000.0,
        "mean_thinking_tokens": 1_000_000_000.0,
        "estimated_cost_usd": 1_000_000.0,
    }
    for mkey, mval in metrics.items():
        if mval is not None:
            _bounded_number(mval, f"metric {mkey}", 0.0, metric_maxima[mkey])

    _bounded_number(telem["uncertainty"], "uncertainty", 0.0, 100.0)
    if not isinstance(telem["verification_passed"], bool):
        raise ModelEvidenceCampaignError("verification_passed must be a boolean")

    if (
        not isinstance(record["limitations"], list)
        or not (1 <= len(record["limitations"]) <= 4)
        or any(it not in RECORD_LIMITATION_CODES for it in record["limitations"])
        or len(set(record["limitations"])) != len(record["limitations"])
    ):
        raise ModelEvidenceCampaignError("record limitations must be unique closed limitation codes")

    return record


def validate_evaluation(eval_dict: Any) -> dict[str, Any]:
    if not isinstance(eval_dict, dict):
        raise ModelEvidenceCampaignError("evaluation must be an object")
    allowed_keys = {
        "schema_version",
        "kind",
        "plan_sha256",
        "candidate_record_sha256",
        "anchor_record_sha256s",
        "lane",
        "candidate_model_id",
        "recommendation",
        "reason_code",
        "facts",
        "applied",
        "dispatch_authorized",
        "model_change_authorized",
        "effort_change_authorized",
        "acceptance_authorized",
        "git_authorized",
        "recommendation_only",
        "limitations",
        "token_inference_disclaimer",
    }
    if set(eval_dict.keys()) != allowed_keys:
        raise ModelEvidenceCampaignError("evaluation keys do not match strict schema")

    if eval_dict["schema_version"] != 1 or isinstance(eval_dict["schema_version"], bool):
        raise ModelEvidenceCampaignError("evaluation schema_version must be integer 1")
    if eval_dict["kind"] != "agy-model-evidence-campaign-evaluation":
        raise ModelEvidenceCampaignError("evaluation kind must be agy-model-evidence-campaign-evaluation")
    if not isinstance(eval_dict["plan_sha256"], str) or not SHA256_RE.fullmatch(eval_dict["plan_sha256"]):
        raise ModelEvidenceCampaignError("invalid plan_sha256 in evaluation")
    if not isinstance(eval_dict["candidate_record_sha256"], str) or not SHA256_RE.fullmatch(eval_dict["candidate_record_sha256"]):
        raise ModelEvidenceCampaignError("invalid candidate_record_sha256 in evaluation")
    if (
        not isinstance(eval_dict["anchor_record_sha256s"], list)
        or not (1 <= len(eval_dict["anchor_record_sha256s"]) <= 20)
        or len(set(eval_dict["anchor_record_sha256s"])) != len(eval_dict["anchor_record_sha256s"])
        or any(not isinstance(s, str) or not SHA256_RE.fullmatch(s) for s in eval_dict["anchor_record_sha256s"])
    ):
        raise ModelEvidenceCampaignError("invalid anchor_record_sha256s in evaluation")
    if eval_dict["lane"] not in VALID_LANES:
        raise ModelEvidenceCampaignError("invalid lane in evaluation")
    if not isinstance(eval_dict["candidate_model_id"], str) or not SAFE_ID_RE.fullmatch(eval_dict["candidate_model_id"]):
        raise ModelEvidenceCampaignError("invalid candidate_model_id in evaluation")

    if eval_dict["recommendation"] not in {"candidate_evidence_only", "no_recommendation"}:
        raise ModelEvidenceCampaignError(f"invalid recommendation in evaluation: {eval_dict['recommendation']!r}")
    if eval_dict["reason_code"] not in EVALUATION_REASON_CODES:
        raise ModelEvidenceCampaignError(f"invalid reason_code in evaluation: {eval_dict['reason_code']!r}")

    # Facts validation
    facts = eval_dict["facts"]
    if not isinstance(facts, dict):
        raise ModelEvidenceCampaignError("facts must be an object")
    allowed_facts = {
        "anchor_matches",
        "cohort_complete",
        "identity_matches",
        "substituted",
        "drift_detected",
        "telemetry_compatible",
        "budget_within_limits",
        "sample_count",
        "invocation_count",
        "coverage",
        "verification_passed",
        "uncertainty_acceptable",
        "anchor_count",
        "lane",
    }
    if set(facts.keys()) != allowed_facts:
        raise ModelEvidenceCampaignError("facts keys do not match strict schema")
    for fact_key in (
        "anchor_matches", "cohort_complete", "identity_matches", "substituted", "drift_detected",
        "telemetry_compatible", "budget_within_limits", "verification_passed",
        "uncertainty_acceptable",
    ):
        if not isinstance(facts[fact_key], bool):
            raise ModelEvidenceCampaignError(f"evaluation fact {fact_key} must be boolean")
    for fact_key in ("sample_count", "invocation_count"):
        if (
            not isinstance(facts[fact_key], int)
            or isinstance(facts[fact_key], bool)
            or not 0 <= facts[fact_key] <= 10_000_000
        ):
            raise ModelEvidenceCampaignError(
                f"evaluation fact {fact_key} must be an integer between 0 and 10,000,000"
            )
    if (
        not isinstance(facts["anchor_count"], int)
        or isinstance(facts["anchor_count"], bool)
        or not 0 <= facts["anchor_count"] <= 20
    ):
        raise ModelEvidenceCampaignError("evaluation fact anchor_count must be an integer between 0 and 20")
    _bounded_number(facts["coverage"], "evaluation fact coverage", 0.0, 1.0)
    if facts["lane"] not in VALID_LANES or facts["lane"] != eval_dict["lane"]:
        raise ModelEvidenceCampaignError("evaluation fact lane must match evaluation lane")

    verified_measured = (
        eval_dict["lane"] == "measured"
        and eval_dict["recommendation"] == "candidate_evidence_only"
        and eval_dict["reason_code"] == "verified-measured-evidence"
    )
    if (eval_dict["recommendation"] == "candidate_evidence_only") != verified_measured:
        raise ModelEvidenceCampaignError("candidate_evidence_only is valid only for verified measured evidence")
    if eval_dict["reason_code"] == "verified-measured-evidence" and not verified_measured:
        raise ModelEvidenceCampaignError("verified-measured-evidence requires candidate_evidence_only")
    if verified_measured and not (
        facts["anchor_matches"]
        and facts["cohort_complete"]
        and facts["identity_matches"]
        and not facts["substituted"]
        and not facts["drift_detected"]
        and facts["telemetry_compatible"]
        and facts["budget_within_limits"]
        and facts["verification_passed"]
        and facts["uncertainty_acceptable"]
    ):
        raise ModelEvidenceCampaignError("verified measured evaluation facts are inconsistent")

    for flag in (
        "applied",
        "dispatch_authorized",
        "model_change_authorized",
        "effort_change_authorized",
        "acceptance_authorized",
        "git_authorized",
    ):
        if eval_dict[flag] is not False:
            raise ModelEvidenceCampaignError(f"{flag} must be false")

    if eval_dict["recommendation_only"] is not True:
        raise ModelEvidenceCampaignError("recommendation_only must be true")

    if (
        not isinstance(eval_dict["limitations"], list)
        or not 1 <= len(eval_dict["limitations"]) <= 20
        or any(not isinstance(item, str) or not 1 <= len(item) <= 1000 for item in eval_dict["limitations"])
    ):
        raise ModelEvidenceCampaignError("evaluation limitations must be bounded non-empty strings")

    if eval_dict["token_inference_disclaimer"] != TOKEN_DISCLAIMER:
        raise ModelEvidenceCampaignError("invalid token_inference_disclaimer")

    return eval_dict


def validate_aggregate(agg: Any) -> dict[str, Any]:
    if not isinstance(agg, dict):
        raise ModelEvidenceCampaignError("aggregate must be an object")
    v1_keys = {
        "schema_version",
        "kind",
        "total_records",
        "by_lane",
        "by_status",
        "by_verification",
        "total_samples",
        "total_invocations",
    }
    version = agg.get("schema_version")
    if not isinstance(version, int) or isinstance(version, bool) or version not in {1, 2}:
        raise ModelEvidenceCampaignError("aggregate schema_version must be integer 1 or 2")
    expected_keys = v1_keys if version == 1 else v1_keys | {
        "by_workflow_category",
        "by_requested_observed_model",
        "identity_mismatch_counts",
    }
    if set(agg.keys()) != expected_keys:
        raise ModelEvidenceCampaignError("aggregate keys do not match strict schema")
    if agg["kind"] != "agy-model-evidence-campaign-aggregate":
        raise ModelEvidenceCampaignError("aggregate kind must be agy-model-evidence-campaign-aggregate")

    if not isinstance(agg["total_records"], int) or isinstance(agg["total_records"], bool) or agg["total_records"] < 0:
        raise ModelEvidenceCampaignError("total_records must be a non-negative integer")

    by_lane = agg["by_lane"]
    if not isinstance(by_lane, dict) or set(by_lane.keys()) != {"vendor_declared", "measured", "observational"}:
        raise ModelEvidenceCampaignError("by_lane must contain vendor_declared, measured, observational")
    for k in by_lane:
        if not isinstance(by_lane[k], int) or isinstance(by_lane[k], bool) or by_lane[k] < 0:
            raise ModelEvidenceCampaignError(f"by_lane {k} must be non-negative integer")

    by_status = agg["by_status"]
    if not isinstance(by_status, dict) or set(by_status.keys()) != {
        "evaluated",
        "verified_measured",
        "no_recommendation",
        "unreviewed",
    }:
        raise ModelEvidenceCampaignError("by_status must contain evaluated, verified_measured, no_recommendation, unreviewed")
    for k in by_status:
        if not isinstance(by_status[k], int) or isinstance(by_status[k], bool) or by_status[k] < 0:
            raise ModelEvidenceCampaignError(f"by_status {k} must be non-negative integer")

    by_verif = agg["by_verification"]
    if not isinstance(by_verif, dict) or set(by_verif.keys()) != {"passed", "failed"}:
        raise ModelEvidenceCampaignError("by_verification must contain passed and failed")
    for k in by_verif:
        if not isinstance(by_verif[k], int) or isinstance(by_verif[k], bool) or by_verif[k] < 0:
            raise ModelEvidenceCampaignError(f"by_verification {k} must be non-negative integer")

    if version == 2:
        by_workflow = agg["by_workflow_category"]
        if not isinstance(by_workflow, dict) or set(by_workflow.keys()) != set(WORKFLOW_CATEGORIES):
            raise ModelEvidenceCampaignError(
                "by_workflow_category must contain explore, task, project, benchmark, other"
            )
        for key, value in by_workflow.items():
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise ModelEvidenceCampaignError(
                    f"by_workflow_category {key} must be non-negative integer"
                )

        by_identity = agg["by_requested_observed_model"]
        if not isinstance(by_identity, dict) or set(by_identity.keys()) != set(IDENTITY_STATUSES):
            raise ModelEvidenceCampaignError(
                "by_requested_observed_model must contain match, mismatch, missing, substituted"
            )
        for key, value in by_identity.items():
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise ModelEvidenceCampaignError(
                    f"by_requested_observed_model {key} must be non-negative integer"
                )

        mismatch_counts = agg["identity_mismatch_counts"]
        if not isinstance(mismatch_counts, dict) or set(mismatch_counts.keys()) != {
            "candidate", "anchor", "total"
        }:
            raise ModelEvidenceCampaignError(
                "identity_mismatch_counts must contain candidate, anchor, total"
            )
        for key, value in mismatch_counts.items():
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise ModelEvidenceCampaignError(
                    f"identity_mismatch_counts {key} must be non-negative integer"
                )
        if mismatch_counts["candidate"] + mismatch_counts["anchor"] != mismatch_counts["total"]:
            raise ModelEvidenceCampaignError("identity_mismatch_counts total is inconsistent")
        if mismatch_counts["total"] != by_identity["mismatch"]:
            raise ModelEvidenceCampaignError(
                "identity_mismatch_counts must equal requested-observed mismatch count"
            )
        if sum(by_workflow.values()) != agg["total_records"]:
            raise ModelEvidenceCampaignError("workflow-category counts must equal total_records")
        if sum(by_identity.values()) != agg["total_records"]:
            raise ModelEvidenceCampaignError("requested-observed counts must equal total_records")

    if not isinstance(agg["total_samples"], int) or isinstance(agg["total_samples"], bool) or agg["total_samples"] < 0:
        raise ModelEvidenceCampaignError("total_samples must be non-negative integer")
    if not isinstance(agg["total_invocations"], int) or isinstance(agg["total_invocations"], bool) or agg["total_invocations"] < 0:
        raise ModelEvidenceCampaignError("total_invocations must be non-negative integer")

    return agg


def validate_aggregate_preview(preview: Any) -> dict[str, Any]:
    if not isinstance(preview, dict):
        raise ModelEvidenceCampaignError("preview must be an object")
    if set(preview.keys()) != {"schema_version", "kind", "preview_sha256", "payload"}:
        raise ModelEvidenceCampaignError("preview keys do not match strict schema")
    if preview["schema_version"] not in {1, 2} or isinstance(preview["schema_version"], bool):
        raise ModelEvidenceCampaignError("preview schema_version must be integer 1 or 2")
    if preview["kind"] != "agy-model-evidence-campaign-aggregate-preview":
        raise ModelEvidenceCampaignError("preview kind must be agy-model-evidence-campaign-aggregate-preview")
    if not isinstance(preview["preview_sha256"], str) or not SHA256_RE.fullmatch(preview["preview_sha256"]):
        raise ModelEvidenceCampaignError("invalid preview_sha256")
    validate_aggregate(preview["payload"])
    if preview["schema_version"] != preview["payload"]["schema_version"]:
        raise ModelEvidenceCampaignError("preview schema_version must match aggregate payload")
    return preview


def _validate_subject_summary(subject: Any, expected_role: str) -> dict[str, Any]:
    if not isinstance(subject, dict) or set(subject.keys()) != {
        "role",
        "ordinal",
        "coverage",
        "identity",
        "provenance",
        "runtime_version",
        "uncertainty",
        "drift_fraction",
        "rationale_codes",
    }:
        raise ModelEvidenceCampaignError("advisory subject keys do not match strict schema")
    if subject["role"] != expected_role:
        raise ModelEvidenceCampaignError("advisory subject role is inconsistent")
    if (
        not isinstance(subject["ordinal"], int)
        or isinstance(subject["ordinal"], bool)
        or not 0 <= subject["ordinal"] <= 20
    ):
        raise ModelEvidenceCampaignError("advisory subject ordinal is invalid")
    _bounded_number(subject["coverage"], "advisory subject coverage", 0.0, 1.0)
    _bounded_number(subject["uncertainty"], "advisory subject uncertainty", 0.0, 100.0)
    _bounded_number(subject["drift_fraction"], "advisory subject drift_fraction", 0.0, 1.0)
    if subject["identity"] not in IDENTITY_STATUSES:
        raise ModelEvidenceCampaignError("advisory subject identity is invalid")
    if subject["provenance"] not in {
        "vendor_declared", "observational", "independent", "local"
    }:
        raise ModelEvidenceCampaignError("advisory subject provenance is invalid")
    if subject["runtime_version"] is not None and (
        not isinstance(subject["runtime_version"], str)
        or not SAFE_ID_RE.fullmatch(subject["runtime_version"])
    ):
        raise ModelEvidenceCampaignError("advisory subject runtime_version is invalid")
    rationale_codes = subject["rationale_codes"]
    if (
        not isinstance(rationale_codes, list)
        or not 1 <= len(rationale_codes) <= len(SUBJECT_RATIONALE_CODES)
        or len(set(rationale_codes)) != len(rationale_codes)
        or any(code not in SUBJECT_RATIONALE_CODES for code in rationale_codes)
    ):
        raise ModelEvidenceCampaignError("advisory subject rationale_codes are invalid")
    return subject


def validate_advisory_summary(summary: Any) -> dict[str, Any]:
    if not isinstance(summary, dict) or set(summary.keys()) != {
        "schema_version",
        "kind",
        "lane",
        "scenario",
        "recommendation",
        "rationale_code",
        "candidate",
        "anchors",
        "recommendation_only",
        "applied",
        "dispatch_authorized",
        "model_change_authorized",
        "effort_change_authorized",
        "acceptance_authorized",
        "git_authorized",
        "limitations",
        "token_inference_disclaimer",
    }:
        raise ModelEvidenceCampaignError("advisory summary keys do not match strict schema")
    if summary["schema_version"] != 1 or isinstance(summary["schema_version"], bool):
        raise ModelEvidenceCampaignError("advisory summary schema_version must be integer 1")
    if summary["kind"] != "agy-model-evidence-campaign-advisory-summary":
        raise ModelEvidenceCampaignError("advisory summary kind is invalid")
    if summary["lane"] not in VALID_LANES:
        raise ModelEvidenceCampaignError("advisory summary lane is invalid")

    scenario = summary["scenario"]
    if not isinstance(scenario, dict) or set(scenario.keys()) != {
        "workflow_category",
        "scenario_version",
        "harness_version",
        "evaluator_version",
        "policy_version",
    }:
        raise ModelEvidenceCampaignError("advisory scenario keys do not match strict schema")
    if scenario["workflow_category"] not in WORKFLOW_CATEGORIES:
        raise ModelEvidenceCampaignError("advisory workflow_category is invalid")
    if scenario["scenario_version"] is not None and (
        not isinstance(scenario["scenario_version"], str)
        or not SAFE_ID_RE.fullmatch(scenario["scenario_version"])
    ):
        raise ModelEvidenceCampaignError("advisory scenario_version is invalid")
    for key in ("harness_version", "evaluator_version", "policy_version"):
        if not isinstance(scenario[key], str) or not SAFE_ID_RE.fullmatch(scenario[key]):
            raise ModelEvidenceCampaignError(f"advisory {key} is invalid")

    if summary["recommendation"] not in {"candidate_evidence_only", "no_recommendation"}:
        raise ModelEvidenceCampaignError("advisory recommendation is invalid")
    if summary["rationale_code"] not in EVALUATION_REASON_CODES:
        raise ModelEvidenceCampaignError("advisory rationale_code is invalid")
    if summary["lane"] != "measured" and summary["recommendation"] != "no_recommendation":
        raise ModelEvidenceCampaignError("non-measured advisory must fail closed")
    if summary["recommendation"] == "candidate_evidence_only" and (
        summary["lane"] != "measured"
        or summary["rationale_code"] != "verified-measured-evidence"
    ):
        raise ModelEvidenceCampaignError("candidate advisory is not verified measured evidence")

    _validate_subject_summary(summary["candidate"], "candidate")
    anchors = summary["anchors"]
    if not isinstance(anchors, list) or not 1 <= len(anchors) <= 20:
        raise ModelEvidenceCampaignError("advisory anchors must contain 1 to 20 subjects")
    for index, subject in enumerate(anchors, start=1):
        _validate_subject_summary(subject, "anchor")
        if subject["ordinal"] != index:
            raise ModelEvidenceCampaignError("advisory anchor ordinals are not contiguous")
    if summary["candidate"]["ordinal"] != 0:
        raise ModelEvidenceCampaignError("advisory candidate ordinal must be zero")

    for flag in (
        "applied",
        "dispatch_authorized",
        "model_change_authorized",
        "effort_change_authorized",
        "acceptance_authorized",
        "git_authorized",
    ):
        if summary[flag] is not False:
            raise ModelEvidenceCampaignError(f"advisory {flag} must be false")
    if summary["recommendation_only"] is not True:
        raise ModelEvidenceCampaignError("advisory recommendation_only must be true")
    if (
        not isinstance(summary["limitations"], list)
        or not 1 <= len(summary["limitations"]) <= 20
        or any(not isinstance(item, str) or not 1 <= len(item) <= 1000 for item in summary["limitations"])
    ):
        raise ModelEvidenceCampaignError("advisory limitations are invalid")
    if summary["token_inference_disclaimer"] != TOKEN_DISCLAIMER:
        raise ModelEvidenceCampaignError("invalid advisory token_inference_disclaimer")
    return summary


def validate_advisory_preview(preview: Any) -> dict[str, Any]:
    if not isinstance(preview, dict) or set(preview.keys()) != {
        "schema_version", "kind", "preview_sha256", "payload"
    }:
        raise ModelEvidenceCampaignError("advisory preview keys do not match strict schema")
    if preview["schema_version"] != 1 or isinstance(preview["schema_version"], bool):
        raise ModelEvidenceCampaignError("advisory preview schema_version must be integer 1")
    if preview["kind"] != "agy-model-evidence-campaign-advisory-preview":
        raise ModelEvidenceCampaignError("advisory preview kind is invalid")
    if not isinstance(preview["preview_sha256"], str) or not SHA256_RE.fullmatch(
        preview["preview_sha256"]
    ):
        raise ModelEvidenceCampaignError("invalid advisory preview_sha256")
    validate_advisory_summary(preview["payload"])
    return preview


def validate_campaign_artifacts(
    plan: dict[str, Any],
    review: dict[str, Any],
    review_sha: str,
    inventory: dict[str, Any],
    inventory_sha: str,
    matrix: dict[str, Any],
    matrix_sha: str,
    dataset: dict[str, Any],
    dataset_sha: str,
) -> dict[str, str]:
    """Validate the exact #106 review and current artifact chain bound by a plan."""
    validate_plan(plan)
    expected = plan["anchors"]
    observed = {
        "benchmark_review_sha256": review_sha,
        "inventory_binding_sha256": inventory_sha,
        "model_matrix_sha256": matrix_sha,
        "dataset_sha256": dataset_sha,
    }
    if observed != expected:
        raise ModelEvidenceCampaignError("current campaign artifact digests differ from plan anchors")

    model_intelligence = _model_intelligence_module()
    try:
        model_intelligence.validate_benchmark_review_output(review)
        model_intelligence.validate_dataset(dataset)
        inventory_slugs, _, inventory_kind, inventory_meta = model_intelligence._extract_model_inventory(
            inventory, "campaign_inventory"
        )
        matrix_slugs, _, matrix_kind, matrix_meta = model_intelligence._extract_model_inventory(
            matrix, "campaign_matrix"
        )
    except Exception as exc:
        raise ModelEvidenceCampaignError("current campaign artifact validation failed") from exc

    if inventory_kind != "inventory_binding" or matrix_kind != "model_matrix":
        raise ModelEvidenceCampaignError("campaign inventory or matrix has the wrong artifact kind")
    if inventory.get("status") != "accepted-current-inventory":
        raise ModelEvidenceCampaignError("campaign inventory is not accepted current evidence")
    if matrix.get("resolution_status") != "active":
        raise ModelEvidenceCampaignError("campaign matrix is not active")
    inventory_version = inventory_meta.get("agy_version")
    matrix_inventory = matrix_meta.get("inventory")
    matrix_version = matrix_inventory.get("agy_version") if isinstance(matrix_inventory, dict) else None
    if (
        not isinstance(inventory_version, str)
        or not SAFE_ID_RE.fullmatch(inventory_version)
        or matrix_version != inventory_version
    ):
        raise ModelEvidenceCampaignError("campaign inventory and matrix version bindings differ")
    if review["evidence_dataset_sha256"] != dataset_sha:
        raise ModelEvidenceCampaignError("#106 review is not bound to the current dataset")
    if (
        review["status"] != "benchmark-review-due"
        or review["maintainer_disposition"] != "collect"
    ):
        raise ModelEvidenceCampaignError("#106 review does not authorize collection")
    matching = [
        item for item in review["reviews_due"]
        if item["model_id"] == plan["candidate_model_id"]
        and item["evidence_state"] == "inventory-added"
    ]
    if len(matching) != 1:
        raise ModelEvidenceCampaignError("#106 review lacks one exact inventory-added candidate trigger")
    candidate = plan["candidate_model_id"]
    if candidate not in inventory_slugs or candidate not in matrix_slugs:
        raise ModelEvidenceCampaignError("campaign candidate is absent from current inventory or matrix")
    for anchor_id in plan["anchor_model_ids"]:
        if anchor_id not in inventory_slugs or anchor_id not in matrix_slugs:
            raise ModelEvidenceCampaignError(f"campaign anchor {anchor_id} is absent from current inventory or matrix")
    return {"agy_version": inventory_version}


def evaluate_campaign(
    plan: dict[str, Any],
    plan_sha: str,
    candidate_record: dict[str, Any] | None = None,
    candidate_record_sha: str | None = None,
    anchor_records: Sequence[tuple[dict[str, Any], str]] | None = None,
    records: Sequence[tuple[dict[str, Any], str]] | None = None,
    review: dict[str, Any] | None = None,
    review_sha: str | None = None,
    dataset_sha: str | None = None,
    inventory_sha: str | None = None,
    matrix_sha: str | None = None,
    # Backward compat kwargs
    record: dict[str, Any] | None = None,
    record_sha: str | None = None,
) -> dict[str, Any]:
    """Pure and deterministic evaluation of candidate + anchor campaign records against a frozen plan."""
    validate_plan(plan)

    # Collect and normalize all records into candidate and anchor sets
    cand_records: list[tuple[dict[str, Any], str]] = []
    anc_records: list[tuple[dict[str, Any], str]] = []

    if records is not None:
        for rec, r_sha in records:
            validate_record(rec)
            if rec["subject_role"] == "candidate":
                cand_records.append((rec, r_sha))
            elif rec["subject_role"] == "anchor":
                anc_records.append((rec, r_sha))
    else:
        if candidate_record is not None:
            validate_record(candidate_record)
            cand_records.append((candidate_record, candidate_record_sha or "0"*64))
        elif record is not None:
            validate_record(record)
            if record["subject_role"] == "candidate":
                cand_records.append((record, record_sha or "0"*64))
            elif record["subject_role"] == "anchor":
                anc_records.append((record, record_sha or "0"*64))
        if anchor_records is not None:
            for anc, a_sha in anchor_records:
                validate_record(anc)
                anc_records.append((anc, a_sha))

    declared_anchors = plan["anchor_model_ids"]
    declared_candidate = plan["candidate_model_id"]

    # Hash chain binding and lane check across all provided records
    for rec, _ in cand_records + anc_records:
        if rec["plan_sha256"] != plan_sha:
            raise ModelEvidenceCampaignError("record plan_sha256 does not match plan digest")
        if rec["lane"] != plan["lane"]:
            raise ModelEvidenceCampaignError(
                f"record lane {rec['lane']!r} does not match plan lane {plan['lane']!r}"
            )

    # Check cohort structure
    has_candidate = (len(cand_records) == 1 and cand_records[0][0]["subject_role"] == "candidate")
    candidate_rec = cand_records[0][0] if len(cand_records) == 1 else None
    cand_sha = cand_records[0][1] if len(cand_records) == 1 else "0" * 64

    anchors_by_model: dict[str, list[tuple[dict[str, Any], str]]] = {}
    unexpected_subjects: list[str] = []
    for anc, a_sha in anc_records:
        req = anc["model_identity"]["requested_model"]
        if anc["subject_role"] != "anchor" or req not in declared_anchors:
            unexpected_subjects.append(req)
        else:
            anchors_by_model.setdefault(req, []).append((anc, a_sha))

    if len(cand_records) > 1:
        unexpected_subjects.append("extra-candidate")

    missing_anchors = [a for a in declared_anchors if a not in anchors_by_model or len(anchors_by_model[a]) == 0]
    duplicate_anchors = [a for a in declared_anchors if a in anchors_by_model and len(anchors_by_model[a]) > 1]

    cohort_complete = bool(has_candidate and not missing_anchors and not duplicate_anchors and not unexpected_subjects)

    # Initialize tracking facts
    anchor_matches = True
    identity_matches = True
    substituted = False
    drift_detected = False
    telemetry_compatible = True
    budget_within_limits = True
    uncertainty_acceptable = True
    all_verification_passed = True

    # 1. Trigger / anchor drift.
    if (
        plan["trigger"]["benchmark_review_status"] != "benchmark-review-due"
        or plan["trigger"]["review_reason"] != "inventory-added"
        or plan["trigger"]["maintainer_disposition"] != "collect"
    ):
        anchor_matches = False
        drift_detected = True

    if (
        not isinstance(review, dict)
        or review_sha is None
        or dataset_sha is None
        or inventory_sha is None
        or matrix_sha is None
    ):
        anchor_matches = False
        drift_detected = True
    else:
        if review_sha != plan["anchors"]["benchmark_review_sha256"]:
            anchor_matches = False
            drift_detected = True
        if review.get("status") != "benchmark-review-due":
            anchor_matches = False
            drift_detected = True
        if review.get("maintainer_disposition") != "collect":
            anchor_matches = False
            drift_detected = True
        reviews_due = review.get("reviews_due", [])
        matching_due = [
            it for it in reviews_due
            if isinstance(it, dict)
            and it.get("model_id") == plan["candidate_model_id"]
            and it.get("evidence_state") == "inventory-added"
        ]
        if not matching_due:
            anchor_matches = False
            drift_detected = True

    if dataset_sha != plan["anchors"]["dataset_sha256"]:
        anchor_matches = False
        drift_detected = True
    if inventory_sha != plan["anchors"]["inventory_binding_sha256"]:
        anchor_matches = False
        drift_detected = True
    if matrix_sha != plan["anchors"]["model_matrix_sha256"]:
        anchor_matches = False
        drift_detected = True

    # Build cohort record list
    all_cohort_records: list[dict[str, Any]] = []
    if candidate_rec is not None:
        all_cohort_records.append(candidate_rec)
    for a in declared_anchors:
        if a in anchors_by_model and len(anchors_by_model[a]) > 0:
            all_cohort_records.append(anchors_by_model[a][0][0])

    anchor_sha_list = [
        anchors_by_model[a][0][1] if (a in anchors_by_model and len(anchors_by_model[a]) > 0) else "0" * 64
        for a in declared_anchors
    ]

    # If anchor artifacts drift
    if not anchor_matches:
        return _make_evaluation_result(
            plan_sha, cand_sha, anchor_sha_list, plan["lane"], plan["candidate_model_id"],
            recommendation="no_recommendation",
            reason_code="anchor-drift",
            facts={
                "anchor_matches": False,
                "cohort_complete": cohort_complete,
                "identity_matches": identity_matches,
                "substituted": substituted,
                "drift_detected": True,
                "telemetry_compatible": telemetry_compatible,
                "budget_within_limits": budget_within_limits,
                "sample_count": sum(r["telemetry"]["sample_count"] for r in all_cohort_records),
                "invocation_count": sum(r["telemetry"]["invocation_count"] for r in all_cohort_records),
                "coverage": min((r["telemetry"]["coverage"] for r in all_cohort_records), default=0.0),
                "verification_passed": all_verification_passed,
                "uncertainty_acceptable": uncertainty_acceptable,
                "anchor_count": len(declared_anchors),
                "lane": plan["lane"],
            },
        )

    # 2. Missing or unexpected subjects in cohort
    if not cohort_complete:
        reason = "missing-subject" if (not has_candidate or missing_anchors) else "unexpected-subject"
        return _make_evaluation_result(
            plan_sha, cand_sha, anchor_sha_list, plan["lane"], plan["candidate_model_id"],
            recommendation="no_recommendation",
            reason_code=reason,
            facts={
                "anchor_matches": True,
                "cohort_complete": False,
                "identity_matches": identity_matches,
                "substituted": substituted,
                "drift_detected": False,
                "telemetry_compatible": telemetry_compatible,
                "budget_within_limits": budget_within_limits,
                "sample_count": sum(r["telemetry"]["sample_count"] for r in all_cohort_records),
                "invocation_count": sum(r["telemetry"]["invocation_count"] for r in all_cohort_records),
                "coverage": min((r["telemetry"]["coverage"] for r in all_cohort_records), default=0.0),
                "verification_passed": all_verification_passed,
                "uncertainty_acceptable": uncertainty_acceptable,
                "anchor_count": len(declared_anchors),
                "lane": plan["lane"],
            },
        )

    # 3. Identity and substitution checks across cohort
    # Candidate identity check
    assert candidate_rec is not None
    cand_mid = candidate_rec["model_identity"]
    if cand_mid["requested_model"] != declared_candidate:
        identity_matches = False
        return _make_evaluation_result(
            plan_sha, cand_sha, anchor_sha_list, plan["lane"], plan["candidate_model_id"],
            recommendation="no_recommendation",
            reason_code="identity-mismatch",
            facts={
                "anchor_matches": True,
                "cohort_complete": True,
                "identity_matches": False,
                "substituted": substituted,
                "drift_detected": False,
                "telemetry_compatible": telemetry_compatible,
                "budget_within_limits": budget_within_limits,
                "sample_count": sum(r["telemetry"]["sample_count"] for r in all_cohort_records),
                "invocation_count": sum(r["telemetry"]["invocation_count"] for r in all_cohort_records),
                "coverage": min((r["telemetry"]["coverage"] for r in all_cohort_records), default=0.0),
                "verification_passed": all_verification_passed,
                "uncertainty_acceptable": uncertainty_acceptable,
                "anchor_count": len(declared_anchors),
                "lane": plan["lane"],
            },
        )

    if cand_mid["observed_model"] is None:
        return _make_evaluation_result(
            plan_sha, cand_sha, anchor_sha_list, plan["lane"], plan["candidate_model_id"],
            recommendation="no_recommendation",
            reason_code="observed-model-missing",
            facts={
                "anchor_matches": True,
                "cohort_complete": True,
                "identity_matches": True,
                "substituted": substituted,
                "drift_detected": False,
                "telemetry_compatible": telemetry_compatible,
                "budget_within_limits": budget_within_limits,
                "sample_count": sum(r["telemetry"]["sample_count"] for r in all_cohort_records),
                "invocation_count": sum(r["telemetry"]["invocation_count"] for r in all_cohort_records),
                "coverage": min((r["telemetry"]["coverage"] for r in all_cohort_records), default=0.0),
                "verification_passed": all_verification_passed,
                "uncertainty_acceptable": uncertainty_acceptable,
                "anchor_count": len(declared_anchors),
                "lane": plan["lane"],
            },
        )

    if cand_mid["substituted"] is True or cand_mid["observed_model"] != cand_mid["requested_model"]:
        return _make_evaluation_result(
            plan_sha, cand_sha, anchor_sha_list, plan["lane"], plan["candidate_model_id"],
            recommendation="no_recommendation",
            reason_code="model-substituted",
            facts={
                "anchor_matches": True,
                "cohort_complete": True,
                "identity_matches": True,
                "substituted": True,
                "drift_detected": False,
                "telemetry_compatible": telemetry_compatible,
                "budget_within_limits": budget_within_limits,
                "sample_count": sum(r["telemetry"]["sample_count"] for r in all_cohort_records),
                "invocation_count": sum(r["telemetry"]["invocation_count"] for r in all_cohort_records),
                "coverage": min((r["telemetry"]["coverage"] for r in all_cohort_records), default=0.0),
                "verification_passed": all_verification_passed,
                "uncertainty_acceptable": uncertainty_acceptable,
                "anchor_count": len(declared_anchors),
                "lane": plan["lane"],
            },
        )

    # Anchor identity checks
    for a in declared_anchors:
        anc_r = anchors_by_model[a][0][0]
        anc_mid = anc_r["model_identity"]
        if anc_mid["requested_model"] != a:
            return _make_evaluation_result(
                plan_sha, cand_sha, anchor_sha_list, plan["lane"], plan["candidate_model_id"],
                recommendation="no_recommendation",
                reason_code="identity-mismatch",
                facts={
                    "anchor_matches": True,
                    "cohort_complete": True,
                    "identity_matches": False,
                    "substituted": substituted,
                    "drift_detected": False,
                    "telemetry_compatible": telemetry_compatible,
                    "budget_within_limits": budget_within_limits,
                    "sample_count": sum(r["telemetry"]["sample_count"] for r in all_cohort_records),
                    "invocation_count": sum(r["telemetry"]["invocation_count"] for r in all_cohort_records),
                    "coverage": min((r["telemetry"]["coverage"] for r in all_cohort_records), default=0.0),
                    "verification_passed": all_verification_passed,
                    "uncertainty_acceptable": uncertainty_acceptable,
                    "anchor_count": len(declared_anchors),
                    "lane": plan["lane"],
                },
            )
        if anc_mid["observed_model"] is None:
            return _make_evaluation_result(
                plan_sha, cand_sha, anchor_sha_list, plan["lane"], plan["candidate_model_id"],
                recommendation="no_recommendation",
                reason_code="observed-model-missing",
                facts={
                    "anchor_matches": True,
                    "cohort_complete": True,
                    "identity_matches": True,
                    "substituted": substituted,
                    "drift_detected": False,
                    "telemetry_compatible": telemetry_compatible,
                    "budget_within_limits": budget_within_limits,
                    "sample_count": sum(r["telemetry"]["sample_count"] for r in all_cohort_records),
                    "invocation_count": sum(r["telemetry"]["invocation_count"] for r in all_cohort_records),
                    "coverage": min((r["telemetry"]["coverage"] for r in all_cohort_records), default=0.0),
                    "verification_passed": all_verification_passed,
                    "uncertainty_acceptable": uncertainty_acceptable,
                    "anchor_count": len(declared_anchors),
                    "lane": plan["lane"],
                },
            )
        if anc_mid["substituted"] is True or anc_mid["observed_model"] != anc_mid["requested_model"]:
            return _make_evaluation_result(
                plan_sha, cand_sha, anchor_sha_list, plan["lane"], plan["candidate_model_id"],
                recommendation="no_recommendation",
                reason_code="model-substituted",
                facts={
                    "anchor_matches": True,
                    "cohort_complete": True,
                    "identity_matches": True,
                    "substituted": True,
                    "drift_detected": False,
                    "telemetry_compatible": telemetry_compatible,
                    "budget_within_limits": budget_within_limits,
                    "sample_count": sum(r["telemetry"]["sample_count"] for r in all_cohort_records),
                    "invocation_count": sum(r["telemetry"]["invocation_count"] for r in all_cohort_records),
                    "coverage": min((r["telemetry"]["coverage"] for r in all_cohort_records), default=0.0),
                    "verification_passed": all_verification_passed,
                    "uncertainty_acceptable": uncertainty_acceptable,
                    "anchor_count": len(declared_anchors),
                    "lane": plan["lane"],
                },
            )

    # 4. Cross-record scenario, harness, evaluator, config, window, and policy drift
    for rec in all_cohort_records:
        if rec["scenario_id"] != plan["scenario_id"]:
            return _make_evaluation_result(
                plan_sha, cand_sha, anchor_sha_list, plan["lane"], plan["candidate_model_id"],
                recommendation="no_recommendation",
                reason_code="scenario-drift",
                facts={
                    "anchor_matches": True,
                    "cohort_complete": True,
                    "identity_matches": True,
                    "substituted": False,
                    "drift_detected": True,
                    "telemetry_compatible": telemetry_compatible,
                    "budget_within_limits": budget_within_limits,
                    "sample_count": sum(r["telemetry"]["sample_count"] for r in all_cohort_records),
                    "invocation_count": sum(r["telemetry"]["invocation_count"] for r in all_cohort_records),
                    "coverage": min((r["telemetry"]["coverage"] for r in all_cohort_records), default=0.0),
                    "verification_passed": all_verification_passed,
                    "uncertainty_acceptable": uncertainty_acceptable,
                    "anchor_count": len(declared_anchors),
                    "lane": plan["lane"],
                },
            )
        if rec["harness"] != plan["harness"]:
            return _make_evaluation_result(
                plan_sha, cand_sha, anchor_sha_list, plan["lane"], plan["candidate_model_id"],
                recommendation="no_recommendation",
                reason_code="harness-drift",
                facts={
                    "anchor_matches": True,
                    "cohort_complete": True,
                    "identity_matches": True,
                    "substituted": False,
                    "drift_detected": True,
                    "telemetry_compatible": telemetry_compatible,
                    "budget_within_limits": budget_within_limits,
                    "sample_count": sum(r["telemetry"]["sample_count"] for r in all_cohort_records),
                    "invocation_count": sum(r["telemetry"]["invocation_count"] for r in all_cohort_records),
                    "coverage": min((r["telemetry"]["coverage"] for r in all_cohort_records), default=0.0),
                    "verification_passed": all_verification_passed,
                    "uncertainty_acceptable": uncertainty_acceptable,
                    "anchor_count": len(declared_anchors),
                    "lane": plan["lane"],
                },
            )
        if rec["evaluator"] != plan["evaluator"]:
            return _make_evaluation_result(
                plan_sha, cand_sha, anchor_sha_list, plan["lane"], plan["candidate_model_id"],
                recommendation="no_recommendation",
                reason_code="evaluator-drift",
                facts={
                    "anchor_matches": True,
                    "cohort_complete": True,
                    "identity_matches": True,
                    "substituted": False,
                    "drift_detected": True,
                    "telemetry_compatible": telemetry_compatible,
                    "budget_within_limits": budget_within_limits,
                    "sample_count": sum(r["telemetry"]["sample_count"] for r in all_cohort_records),
                    "invocation_count": sum(r["telemetry"]["invocation_count"] for r in all_cohort_records),
                    "coverage": min((r["telemetry"]["coverage"] for r in all_cohort_records), default=0.0),
                    "verification_passed": all_verification_passed,
                    "uncertainty_acceptable": uncertainty_acceptable,
                    "anchor_count": len(declared_anchors),
                    "lane": plan["lane"],
                },
            )
        if rec["config_sha256"] != plan["config_sha256"]:
            return _make_evaluation_result(
                plan_sha, cand_sha, anchor_sha_list, plan["lane"], plan["candidate_model_id"],
                recommendation="no_recommendation",
                reason_code="config-drift",
                facts={
                    "anchor_matches": True,
                    "cohort_complete": True,
                    "identity_matches": True,
                    "substituted": False,
                    "drift_detected": True,
                    "telemetry_compatible": telemetry_compatible,
                    "budget_within_limits": budget_within_limits,
                    "sample_count": sum(r["telemetry"]["sample_count"] for r in all_cohort_records),
                    "invocation_count": sum(r["telemetry"]["invocation_count"] for r in all_cohort_records),
                    "coverage": min((r["telemetry"]["coverage"] for r in all_cohort_records), default=0.0),
                    "verification_passed": all_verification_passed,
                    "uncertainty_acceptable": uncertainty_acceptable,
                    "anchor_count": len(declared_anchors),
                    "lane": plan["lane"],
                },
            )
        if rec["measurement_window"] != plan["measurement_window"]:
            return _make_evaluation_result(
                plan_sha, cand_sha, anchor_sha_list, plan["lane"], plan["candidate_model_id"],
                recommendation="no_recommendation",
                reason_code="window-drift",
                facts={
                    "anchor_matches": True,
                    "cohort_complete": True,
                    "identity_matches": True,
                    "substituted": False,
                    "drift_detected": True,
                    "telemetry_compatible": telemetry_compatible,
                    "budget_within_limits": budget_within_limits,
                    "sample_count": sum(r["telemetry"]["sample_count"] for r in all_cohort_records),
                    "invocation_count": sum(r["telemetry"]["invocation_count"] for r in all_cohort_records),
                    "coverage": min((r["telemetry"]["coverage"] for r in all_cohort_records), default=0.0),
                    "verification_passed": all_verification_passed,
                    "uncertainty_acceptable": uncertainty_acceptable,
                    "anchor_count": len(declared_anchors),
                    "lane": plan["lane"],
                },
            )
        if rec["policy"] != plan["policy"]:
            return _make_evaluation_result(
                plan_sha, cand_sha, anchor_sha_list, plan["lane"], plan["candidate_model_id"],
                recommendation="no_recommendation",
                reason_code="policy-drift",
                facts={
                    "anchor_matches": True,
                    "cohort_complete": True,
                    "identity_matches": True,
                    "substituted": False,
                    "drift_detected": True,
                    "telemetry_compatible": telemetry_compatible,
                    "budget_within_limits": budget_within_limits,
                    "sample_count": sum(r["telemetry"]["sample_count"] for r in all_cohort_records),
                    "invocation_count": sum(r["telemetry"]["invocation_count"] for r in all_cohort_records),
                    "coverage": min((r["telemetry"]["coverage"] for r in all_cohort_records), default=0.0),
                    "verification_passed": all_verification_passed,
                    "uncertainty_acceptable": uncertainty_acceptable,
                    "anchor_count": len(declared_anchors),
                    "lane": plan["lane"],
                },
            )

    # In measured lane: check comparability basis across candidate and all anchors
    if plan["lane"] == "measured":
        cand_meta = candidate_rec["measured_metadata"]
        assert isinstance(cand_meta, dict)
        for a in declared_anchors:
            anc_meta = anchors_by_model[a][0][0]["measured_metadata"]
            assert isinstance(anc_meta, dict)
            if (
                anc_meta["agy_version"] != cand_meta["agy_version"]
                or anc_meta["accounting"] != cand_meta["accounting"]
                or anc_meta["tokenizer"] != cand_meta["tokenizer"]
                or anc_meta["currency"] != cand_meta["currency"]
                or anc_meta["cost_basis"] != cand_meta["cost_basis"]
            ):
                return _make_evaluation_result(
                    plan_sha, cand_sha, anchor_sha_list, plan["lane"], plan["candidate_model_id"],
                    recommendation="no_recommendation",
                    reason_code="telemetry-incompatible",
                    facts={
                        "anchor_matches": True,
                        "cohort_complete": True,
                        "identity_matches": True,
                        "substituted": False,
                        "drift_detected": False,
                        "telemetry_compatible": False,
                        "budget_within_limits": budget_within_limits,
                        "sample_count": sum(r["telemetry"]["sample_count"] for r in all_cohort_records),
                        "invocation_count": sum(r["telemetry"]["invocation_count"] for r in all_cohort_records),
                        "coverage": min((r["telemetry"]["coverage"] for r in all_cohort_records), default=0.0),
                        "verification_passed": all_verification_passed,
                        "uncertainty_acceptable": uncertainty_acceptable,
                        "anchor_count": len(declared_anchors),
                        "lane": plan["lane"],
                    },
                )

    # 5. Telemetry bindings and coverage across cohort
    required_bindings = set(plan["required_telemetry"]["bindings"])
    for rec in all_cohort_records:
        provided_bindings = set(rec["telemetry"]["telemetry_bindings"])
        if not required_bindings.issubset(provided_bindings):
            return _make_evaluation_result(
                plan_sha, cand_sha, anchor_sha_list, plan["lane"], plan["candidate_model_id"],
                recommendation="no_recommendation",
                reason_code="telemetry-incompatible",
                facts={
                    "anchor_matches": True,
                    "cohort_complete": True,
                    "identity_matches": True,
                    "substituted": False,
                    "drift_detected": False,
                    "telemetry_compatible": False,
                    "budget_within_limits": budget_within_limits,
                    "sample_count": sum(r["telemetry"]["sample_count"] for r in all_cohort_records),
                    "invocation_count": sum(r["telemetry"]["invocation_count"] for r in all_cohort_records),
                    "coverage": min((r["telemetry"]["coverage"] for r in all_cohort_records), default=0.0),
                    "verification_passed": all_verification_passed,
                    "uncertainty_acceptable": uncertainty_acceptable,
                    "anchor_count": len(declared_anchors),
                    "lane": plan["lane"],
                },
            )

    for rec in all_cohort_records:
        if rec["telemetry"]["coverage"] < plan["required_telemetry"]["min_coverage"] or rec["telemetry"]["coverage"] < plan["acceptance_rules"]["min_coverage"]:
            return _make_evaluation_result(
                plan_sha, cand_sha, anchor_sha_list, plan["lane"], plan["candidate_model_id"],
                recommendation="no_recommendation",
                reason_code="insufficient-coverage",
                facts={
                    "anchor_matches": True,
                    "cohort_complete": True,
                    "identity_matches": True,
                    "substituted": False,
                    "drift_detected": False,
                    "telemetry_compatible": True,
                    "budget_within_limits": budget_within_limits,
                    "sample_count": sum(r["telemetry"]["sample_count"] for r in all_cohort_records),
                    "invocation_count": sum(r["telemetry"]["invocation_count"] for r in all_cohort_records),
                    "coverage": min((r["telemetry"]["coverage"] for r in all_cohort_records), default=0.0),
                    "verification_passed": all_verification_passed,
                    "uncertainty_acceptable": uncertainty_acceptable,
                    "anchor_count": len(declared_anchors),
                    "lane": plan["lane"],
                },
            )

    # 6. Budget constraints across cohort
    for rec in all_cohort_records:
        if (
            rec["telemetry"]["invocation_count"] > plan["budget"]["invocation_budget"]
            or rec["telemetry"]["sample_count"] > plan["budget"]["sample_budget"]
        ):
            return _make_evaluation_result(
                plan_sha, cand_sha, anchor_sha_list, plan["lane"], plan["candidate_model_id"],
                recommendation="no_recommendation",
                reason_code="budget-exhausted",
                facts={
                    "anchor_matches": True,
                    "cohort_complete": True,
                    "identity_matches": True,
                    "substituted": False,
                    "drift_detected": False,
                    "telemetry_compatible": True,
                    "budget_within_limits": False,
                    "sample_count": sum(r["telemetry"]["sample_count"] for r in all_cohort_records),
                    "invocation_count": sum(r["telemetry"]["invocation_count"] for r in all_cohort_records),
                    "coverage": min((r["telemetry"]["coverage"] for r in all_cohort_records), default=0.0),
                    "verification_passed": all_verification_passed,
                    "uncertainty_acceptable": uncertainty_acceptable,
                    "anchor_count": len(declared_anchors),
                    "lane": plan["lane"],
                },
            )

    # 7. Minimum sample size across cohort
    for rec in all_cohort_records:
        if rec["telemetry"]["sample_count"] < plan["acceptance_rules"]["min_sample_size"]:
            return _make_evaluation_result(
                plan_sha, cand_sha, anchor_sha_list, plan["lane"], plan["candidate_model_id"],
                recommendation="no_recommendation",
                reason_code="insufficient-samples",
                facts={
                    "anchor_matches": True,
                    "cohort_complete": True,
                    "identity_matches": True,
                    "substituted": False,
                    "drift_detected": False,
                    "telemetry_compatible": True,
                    "budget_within_limits": True,
                    "sample_count": sum(r["telemetry"]["sample_count"] for r in all_cohort_records),
                    "invocation_count": sum(r["telemetry"]["invocation_count"] for r in all_cohort_records),
                    "coverage": min((r["telemetry"]["coverage"] for r in all_cohort_records), default=0.0),
                    "verification_passed": all_verification_passed,
                    "uncertainty_acceptable": uncertainty_acceptable,
                    "anchor_count": len(declared_anchors),
                    "lane": plan["lane"],
                },
            )

    # 8. Drift tolerance and error rate across cohort
    for rec in all_cohort_records:
        if rec["telemetry"]["drift_fraction"] > plan["drift_tolerance"]["max_drift_fraction"]:
            return _make_evaluation_result(
                plan_sha, cand_sha, anchor_sha_list, plan["lane"], plan["candidate_model_id"],
                recommendation="no_recommendation",
                reason_code="drift-exceeded",
                facts={
                    "anchor_matches": True,
                    "cohort_complete": True,
                    "identity_matches": True,
                    "substituted": False,
                    "drift_detected": True,
                    "telemetry_compatible": True,
                    "budget_within_limits": True,
                    "sample_count": sum(r["telemetry"]["sample_count"] for r in all_cohort_records),
                    "invocation_count": sum(r["telemetry"]["invocation_count"] for r in all_cohort_records),
                    "coverage": min((r["telemetry"]["coverage"] for r in all_cohort_records), default=0.0),
                    "verification_passed": all_verification_passed,
                    "uncertainty_acceptable": uncertainty_acceptable,
                    "anchor_count": len(declared_anchors),
                    "lane": plan["lane"],
                },
            )

    for rec in all_cohort_records:
        if rec["telemetry"]["error_rate"] > plan["acceptance_rules"]["max_error_rate"]:
            return _make_evaluation_result(
                plan_sha, cand_sha, anchor_sha_list, plan["lane"], plan["candidate_model_id"],
                recommendation="no_recommendation",
                reason_code="error-rate-exceeded",
                facts={
                    "anchor_matches": True,
                    "cohort_complete": True,
                    "identity_matches": True,
                    "substituted": False,
                    "drift_detected": False,
                    "telemetry_compatible": True,
                    "budget_within_limits": True,
                    "sample_count": sum(r["telemetry"]["sample_count"] for r in all_cohort_records),
                    "invocation_count": sum(r["telemetry"]["invocation_count"] for r in all_cohort_records),
                    "coverage": min((r["telemetry"]["coverage"] for r in all_cohort_records), default=0.0),
                    "verification_passed": False,
                    "uncertainty_acceptable": uncertainty_acceptable,
                    "anchor_count": len(declared_anchors),
                    "lane": plan["lane"],
                },
            )

    # 9. Verification passed and quality score across cohort
    min_qual = plan["acceptance_rules"].get("min_quality_score")
    for rec in all_cohort_records:
        qual_val = rec["telemetry"]["metrics"].get("quality_score")
        qual_failed = (min_qual is not None and (qual_val is None or qual_val < min_qual))
        if not rec["telemetry"]["verification_passed"] or qual_failed:
            return _make_evaluation_result(
                plan_sha, cand_sha, anchor_sha_list, plan["lane"], plan["candidate_model_id"],
                recommendation="no_recommendation",
                reason_code="verification-failed",
                facts={
                    "anchor_matches": True,
                    "cohort_complete": True,
                    "identity_matches": True,
                    "substituted": False,
                    "drift_detected": False,
                    "telemetry_compatible": True,
                    "budget_within_limits": True,
                    "sample_count": sum(r["telemetry"]["sample_count"] for r in all_cohort_records),
                    "invocation_count": sum(r["telemetry"]["invocation_count"] for r in all_cohort_records),
                    "coverage": min((r["telemetry"]["coverage"] for r in all_cohort_records), default=0.0),
                    "verification_passed": False,
                    "uncertainty_acceptable": uncertainty_acceptable,
                    "anchor_count": len(declared_anchors),
                    "lane": plan["lane"],
                },
            )

    # 10. Uncertainty across cohort
    max_unc = plan["acceptance_rules"]["uncertainty_rule"]["max_uncertainty"]
    for rec in all_cohort_records:
        if rec["telemetry"]["uncertainty"] > max_unc:
            return _make_evaluation_result(
                plan_sha, cand_sha, anchor_sha_list, plan["lane"], plan["candidate_model_id"],
                recommendation="no_recommendation",
                reason_code="uncertainty-exceeded",
                facts={
                    "anchor_matches": True,
                    "cohort_complete": True,
                    "identity_matches": True,
                    "substituted": False,
                    "drift_detected": False,
                    "telemetry_compatible": True,
                    "budget_within_limits": True,
                    "sample_count": sum(r["telemetry"]["sample_count"] for r in all_cohort_records),
                    "invocation_count": sum(r["telemetry"]["invocation_count"] for r in all_cohort_records),
                    "coverage": min((r["telemetry"]["coverage"] for r in all_cohort_records), default=0.0),
                    "verification_passed": True,
                    "uncertainty_acceptable": False,
                    "anchor_count": len(declared_anchors),
                    "lane": plan["lane"],
                },
            )

    # 11. Lane limitation
    if plan["lane"] in ("vendor_declared", "observational"):
        return _make_evaluation_result(
            plan_sha, cand_sha, anchor_sha_list, plan["lane"], plan["candidate_model_id"],
            recommendation="no_recommendation",
            reason_code="lane-limitation",
            facts={
                "anchor_matches": True,
                "cohort_complete": True,
                "identity_matches": True,
                "substituted": False,
                "drift_detected": False,
                "telemetry_compatible": True,
                "budget_within_limits": True,
                "sample_count": sum(r["telemetry"]["sample_count"] for r in all_cohort_records),
                "invocation_count": sum(r["telemetry"]["invocation_count"] for r in all_cohort_records),
                "coverage": min((r["telemetry"]["coverage"] for r in all_cohort_records), default=0.0),
                "verification_passed": True,
                "uncertainty_acceptable": True,
                "anchor_count": len(declared_anchors),
                "lane": plan["lane"],
            },
        )

    # 12. Verified measured cohort evidence
    return _make_evaluation_result(
        plan_sha, cand_sha, anchor_sha_list, "measured", plan["candidate_model_id"],
        recommendation="candidate_evidence_only",
        reason_code="verified-measured-evidence",
        facts={
            "anchor_matches": True,
            "cohort_complete": True,
            "identity_matches": True,
            "substituted": False,
            "drift_detected": False,
            "telemetry_compatible": True,
            "budget_within_limits": True,
            "sample_count": sum(r["telemetry"]["sample_count"] for r in all_cohort_records),
            "invocation_count": sum(r["telemetry"]["invocation_count"] for r in all_cohort_records),
            "coverage": min((r["telemetry"]["coverage"] for r in all_cohort_records), default=0.0),
            "verification_passed": True,
            "uncertainty_acceptable": True,
            "anchor_count": len(declared_anchors),
            "lane": "measured",
        },
    )


def _make_evaluation_result(
    plan_sha: str,
    candidate_record_sha: str,
    anchor_record_sha256s: list[str],
    lane: str,
    candidate_model_id: str,
    recommendation: str,
    reason_code: str,
    facts: dict[str, Any],
) -> dict[str, Any]:
    eval_dict = {
        "schema_version": 1,
        "kind": "agy-model-evidence-campaign-evaluation",
        "plan_sha256": plan_sha,
        "candidate_record_sha256": candidate_record_sha,
        "anchor_record_sha256s": anchor_record_sha256s,
        "lane": lane,
        "candidate_model_id": candidate_model_id,
        "recommendation": recommendation,
        "reason_code": reason_code,
        "facts": facts,
        "applied": False,
        "dispatch_authorized": False,
        "model_change_authorized": False,
        "effort_change_authorized": False,
        "acceptance_authorized": False,
        "git_authorized": False,
        "recommendation_only": True,
        "limitations": [
            "Deterministic offline campaign evaluation; no execution, dispatch, model-change, or git authority.",
            TOKEN_DISCLAIMER,
        ],
        "token_inference_disclaimer": TOKEN_DISCLAIMER,
    }
    return validate_evaluation(eval_dict)


def _subject_rationale_codes(
    plan: dict[str, Any], record: dict[str, Any]
) -> list[str]:
    codes: list[str] = []
    identity_status = _identity_status(record)
    if identity_status == "missing":
        codes.append("observed-model-missing")
    elif identity_status == "substituted":
        codes.append("model-substituted")
    elif identity_status == "mismatch":
        codes.append("identity-mismatch")

    if record["scenario_id"] != plan["scenario_id"]:
        codes.append("scenario-drift")
    if record["harness"] != plan["harness"]:
        codes.append("harness-drift")
    if record["evaluator"] != plan["evaluator"]:
        codes.append("evaluator-drift")
    if record["config_sha256"] != plan["config_sha256"]:
        codes.append("config-drift")
    if record["policy"] != plan["policy"]:
        codes.append("policy-drift")
    if record["measurement_window"] != plan["measurement_window"]:
        codes.append("window-drift")

    telemetry = record["telemetry"]
    required_bindings = set(plan["required_telemetry"]["bindings"])
    if not required_bindings.issubset(set(telemetry["telemetry_bindings"])):
        codes.append("telemetry-incompatible")
    required_coverage = max(
        float(plan["acceptance_rules"]["min_coverage"]),
        float(plan["required_telemetry"]["min_coverage"]),
    )
    if float(telemetry["coverage"]) < required_coverage:
        codes.append("insufficient-coverage")
    if telemetry["sample_count"] < plan["acceptance_rules"]["min_sample_size"]:
        codes.append("insufficient-samples")
    if (
        telemetry["sample_count"] > plan["budget"]["sample_budget"]
        or telemetry["invocation_count"] > plan["budget"]["invocation_budget"]
    ):
        codes.append("budget-exhausted")
    if float(telemetry["drift_fraction"]) > float(plan["drift_tolerance"]["max_drift_fraction"]):
        codes.append("drift-exceeded")
    if float(telemetry["error_rate"]) > float(plan["acceptance_rules"]["max_error_rate"]):
        codes.append("error-rate-exceeded")
    if telemetry["verification_passed"] is not True:
        codes.append("verification-failed")
    if float(telemetry["uncertainty"]) > float(
        plan["acceptance_rules"]["uncertainty_rule"]["max_uncertainty"]
    ):
        codes.append("uncertainty-exceeded")
    if plan["lane"] != "measured":
        codes.append("lane-limitation")
    return codes or ["within-bounds"]


def _subject_summary(
    plan: dict[str, Any], record: dict[str, Any], role: str, ordinal: int
) -> dict[str, Any]:
    measured = record["measured_metadata"]
    if plan["lane"] == "vendor_declared":
        provenance = "vendor_declared"
    elif plan["lane"] == "observational":
        provenance = "observational"
    else:
        assert isinstance(measured, dict)
        provenance = measured["provenance_type"]
    summary = {
        "role": role,
        "ordinal": ordinal,
        "coverage": record["telemetry"]["coverage"],
        "identity": _identity_status(record),
        "provenance": provenance,
        "runtime_version": measured["agy_version"] if isinstance(measured, dict) else None,
        "uncertainty": record["telemetry"]["uncertainty"],
        "drift_fraction": record["telemetry"]["drift_fraction"],
        "rationale_codes": _subject_rationale_codes(plan, record),
    }
    return _validate_subject_summary(summary, role)


def compute_advisory_summary(
    plan: dict[str, Any],
    plan_sha: str,
    records: Sequence[tuple[dict[str, Any], str]],
    evaluation: dict[str, Any],
    review: dict[str, Any],
    review_sha: str,
    dataset: dict[str, Any],
    dataset_sha: str,
    inventory: dict[str, Any],
    inventory_sha: str,
    matrix: dict[str, Any],
    matrix_sha: str,
) -> dict[str, Any]:
    """Render a privacy-bounded advisory from one exact plan/cohort/evaluation chain."""
    validate_plan(plan)
    validate_evaluation(evaluation)
    if not isinstance(plan_sha, str) or not SHA256_RE.fullmatch(plan_sha):
        raise ModelEvidenceCampaignError("advisory plan digest is invalid")
    if evaluation["plan_sha256"] != plan_sha or evaluation["lane"] != plan["lane"]:
        raise ModelEvidenceCampaignError("advisory evaluation does not bind the plan")
    if evaluation["candidate_model_id"] != plan["candidate_model_id"]:
        raise ModelEvidenceCampaignError("advisory evaluation candidate does not bind the plan")
    validate_campaign_artifacts(
        plan, review, review_sha, inventory, inventory_sha, matrix, matrix_sha,
        dataset, dataset_sha,
    )

    candidate_entries: list[tuple[dict[str, Any], str]] = []
    anchor_by_sha: dict[str, dict[str, Any]] = {}
    seen_record_shas: set[str] = set()
    for record, record_sha in records:
        validate_record(record)
        if not isinstance(record_sha, str) or not SHA256_RE.fullmatch(record_sha):
            raise ModelEvidenceCampaignError("advisory record digest is invalid")
        if record_sha in seen_record_shas:
            raise ModelEvidenceCampaignError("advisory record digest is duplicated")
        seen_record_shas.add(record_sha)
        if record["plan_sha256"] != plan_sha or record["lane"] != plan["lane"]:
            raise ModelEvidenceCampaignError("advisory record does not bind the plan and lane")
        if record["subject_role"] == "candidate":
            candidate_entries.append((record, record_sha))
        else:
            anchor_by_sha[record_sha] = record

    if len(candidate_entries) != 1:
        raise ModelEvidenceCampaignError("advisory requires exactly one candidate record")
    candidate_record, candidate_sha = candidate_entries[0]
    if candidate_sha != evaluation["candidate_record_sha256"]:
        raise ModelEvidenceCampaignError("advisory candidate record does not bind the evaluation")
    if candidate_record["model_identity"]["requested_model"] != plan["candidate_model_id"]:
        raise ModelEvidenceCampaignError("advisory candidate record is unexpected")

    evaluation_anchor_shas = evaluation["anchor_record_sha256s"]
    if set(anchor_by_sha) != set(evaluation_anchor_shas):
        raise ModelEvidenceCampaignError("advisory anchor records do not bind the evaluation")
    if len(evaluation_anchor_shas) != len(plan["anchor_model_ids"]):
        raise ModelEvidenceCampaignError("advisory requires the complete anchor cohort")
    ordered_anchors: list[dict[str, Any]] = []
    ordered_anchor_records: list[tuple[dict[str, Any], str]] = []
    for ordinal, (expected_model, anchor_sha) in enumerate(
        zip(plan["anchor_model_ids"], evaluation_anchor_shas), start=1
    ):
        anchor_record = anchor_by_sha[anchor_sha]
        if anchor_record["model_identity"]["requested_model"] != expected_model:
            raise ModelEvidenceCampaignError("advisory anchor order does not bind the plan")
        ordered_anchor_records.append((anchor_record, anchor_sha))
        ordered_anchors.append(_subject_summary(plan, anchor_record, "anchor", ordinal))

    recomputed_evaluation = evaluate_campaign(
        plan,
        plan_sha,
        candidate_record=candidate_record,
        candidate_record_sha=candidate_sha,
        anchor_records=ordered_anchor_records,
        review=review,
        review_sha=review_sha,
        dataset_sha=dataset_sha,
        inventory_sha=inventory_sha,
        matrix_sha=matrix_sha,
    )
    if canonical_bytes(recomputed_evaluation) != canonical_bytes(evaluation):
        raise ModelEvidenceCampaignError(
            "advisory evaluation differs from deterministic cohort recomputation"
        )

    candidate_summary = _subject_summary(plan, candidate_record, "candidate", 0)

    summary = {
        "schema_version": 1,
        "kind": "agy-model-evidence-campaign-advisory-summary",
        "lane": plan["lane"],
        "scenario": {
            "workflow_category": _workflow_category(plan["scenario_id"]),
            "scenario_version": _scenario_version(plan["scenario_id"]),
            "harness_version": plan["harness"]["version"],
            "evaluator_version": plan["evaluator"]["version"],
            "policy_version": plan["policy"]["version"],
        },
        "recommendation": evaluation["recommendation"],
        "rationale_code": evaluation["reason_code"],
        "candidate": candidate_summary,
        "anchors": ordered_anchors,
        "recommendation_only": True,
        "applied": False,
        "dispatch_authorized": False,
        "model_change_authorized": False,
        "effort_change_authorized": False,
        "acceptance_authorized": False,
        "git_authorized": False,
        "limitations": [
            "Privacy-bounded local advisory; excludes prompts, paths, identifiers, and raw evidence.",
            "Scenario identifiers are reduced to a closed workflow category and terminal version token.",
            TOKEN_DISCLAIMER,
        ],
        "token_inference_disclaimer": TOKEN_DISCLAIMER,
    }
    return validate_advisory_summary(summary)


def compute_aggregate(
    records: Sequence[tuple[dict[str, Any], str]],
    evaluations: Sequence[dict[str, Any]],
) -> dict[str, Any]:
    """Pure aggregation over record digests and optional bound evaluations."""
    total_records = len(records)
    by_lane = {"vendor_declared": 0, "measured": 0, "observational": 0}
    by_status = {"evaluated": 0, "verified_measured": 0, "no_recommendation": 0, "unreviewed": 0}
    by_verification = {"passed": 0, "failed": 0}
    by_workflow_category = {category: 0 for category in WORKFLOW_CATEGORIES}
    by_requested_observed_model = {status: 0 for status in IDENTITY_STATUSES}
    identity_mismatch_counts = {"candidate": 0, "anchor": 0, "total": 0}
    total_samples = 0
    total_invocations = 0

    evaluation_by_candidate: dict[str, dict[str, Any]] = {}
    for evaluation in evaluations:
        validate_evaluation(evaluation)
        cand_sha = evaluation["candidate_record_sha256"]
        if cand_sha in evaluation_by_candidate:
            raise ModelEvidenceCampaignError(
                "aggregate evaluation set contains duplicate candidate record bindings"
            )
        evaluation_by_candidate[cand_sha] = evaluation

    seen_record_shas: set[str] = set()
    for rec, record_sha in records:
        validate_record(rec)
        if not isinstance(record_sha, str) or not SHA256_RE.fullmatch(record_sha):
            raise ModelEvidenceCampaignError("aggregate record digest is invalid")
        if record_sha in seen_record_shas:
            raise ModelEvidenceCampaignError("aggregate record digest is duplicated")
        seen_record_shas.add(record_sha)
        lane = rec["lane"]
        if lane in by_lane:
            by_lane[lane] += 1
        by_workflow_category[_workflow_category(rec["scenario_id"])] += 1
        identity_status = _identity_status(rec)
        by_requested_observed_model[identity_status] += 1
        if identity_status == "mismatch":
            identity_mismatch_counts[rec["subject_role"]] += 1
            identity_mismatch_counts["total"] += 1

        telem = rec["telemetry"]
        total_samples += telem["sample_count"]
        total_invocations += telem["invocation_count"]

        # Find evaluation binding this record (either as candidate or anchor)
        matching_eval = None
        for ev in evaluations:
            if ev["candidate_record_sha256"] == record_sha or record_sha in ev["anchor_record_sha256s"]:
                matching_eval = ev
                break

        if (
            matching_eval is None
            or matching_eval["plan_sha256"] != rec["plan_sha256"]
            or matching_eval["lane"] != lane
            or matching_eval["facts"]["lane"] != lane
        ):
            by_status["unreviewed"] += 1
            continue

        by_status["evaluated"] += 1
        if rec["telemetry"]["verification_passed"]:
            by_verification["passed"] += 1
        else:
            by_verification["failed"] += 1
        if (
            lane == "measured"
            and matching_eval["recommendation"] == "candidate_evidence_only"
            and matching_eval["reason_code"] == "verified-measured-evidence"
        ):
            by_status["verified_measured"] += 1
        else:
            by_status["no_recommendation"] += 1

    agg = {
        "schema_version": 2,
        "kind": "agy-model-evidence-campaign-aggregate",
        "total_records": total_records,
        "by_lane": by_lane,
        "by_status": by_status,
        "by_verification": by_verification,
        "by_workflow_category": by_workflow_category,
        "by_requested_observed_model": by_requested_observed_model,
        "identity_mismatch_counts": identity_mismatch_counts,
        "total_samples": total_samples,
        "total_invocations": total_invocations,
    }
    return validate_aggregate(agg)


def materialize_measured_dataset(
    plan: dict[str, Any],
    plan_sha: str,
    candidate_record: dict[str, Any] | None = None,
    candidate_record_sha: str | None = None,
    anchor_records: Sequence[tuple[dict[str, Any], str]] | None = None,
    evaluation: dict[str, Any] | None = None,
    evaluation_sha: str | None = None,
    dataset: dict[str, Any] | None = None,
    dataset_sha: str | None = None,
    review: dict[str, Any] | None = None,
    review_sha: str | None = None,
    inventory: dict[str, Any] | None = None,
    inventory_sha: str | None = None,
    matrix: dict[str, Any] | None = None,
    matrix_sha: str | None = None,
    # Backward compat
    record: dict[str, Any] | None = None,
    record_sha: str | None = None,
    eval_sha: str | None = None,
) -> dict[str, Any]:
    """Explicit measured-only command to materialize a candidate evidence item into a new dataset."""
    if candidate_record is None and record is not None:
        candidate_record = record
        candidate_record_sha = record_sha
    if evaluation_sha is None and eval_sha is not None:
        evaluation_sha = eval_sha

    if candidate_record is None or candidate_record_sha is None:
        raise ModelEvidenceCampaignError("materialize-measured requires candidate record")
    if anchor_records is None:
        anchor_records = []
    if evaluation is None or evaluation_sha is None:
        raise ModelEvidenceCampaignError("materialize-measured requires evaluation artifact")
    if dataset is None or dataset_sha is None:
        raise ModelEvidenceCampaignError("materialize-measured requires dataset")
    if review is None or review_sha is None:
        raise ModelEvidenceCampaignError("materialize-measured requires review")
    if inventory is None or inventory_sha is None:
        raise ModelEvidenceCampaignError("materialize-measured requires inventory")
    if matrix is None or matrix_sha is None:
        raise ModelEvidenceCampaignError("materialize-measured requires matrix")

    validate_plan(plan)
    validate_record(candidate_record)
    for anc_r, _ in anchor_records:
        validate_record(anc_r)
    validate_evaluation(evaluation)

    artifact_facts = validate_campaign_artifacts(
        plan, review, review_sha, inventory, inventory_sha, matrix, matrix_sha, dataset, dataset_sha
    )

    # 1. Exact hash bindings and deterministic evaluation recomputation.
    if not isinstance(evaluation_sha, str) or not SHA256_RE.fullmatch(evaluation_sha):
        raise ModelEvidenceCampaignError("invalid evaluation artifact digest")
    if evaluation["plan_sha256"] != plan_sha:
        raise ModelEvidenceCampaignError("evaluation plan_sha256 mismatch")
    if evaluation["candidate_record_sha256"] != candidate_record_sha:
        raise ModelEvidenceCampaignError("evaluation candidate_record_sha256 mismatch")

    anchor_by_id = {
        r["model_identity"]["requested_model"]: r_sha
        for r, r_sha in anchor_records
        if r["subject_role"] == "anchor"
    }
    expected_anchor_shas: list[str] = []
    for a in plan["anchor_model_ids"]:
        if a not in anchor_by_id:
            raise ModelEvidenceCampaignError("missing anchor record for declared anchor in materialization")
        expected_anchor_shas.append(anchor_by_id[a])
    if evaluation["anchor_record_sha256s"] != expected_anchor_shas:
        raise ModelEvidenceCampaignError("evaluation anchor_record_sha256s mismatch")

    if candidate_record["plan_sha256"] != plan_sha:
        raise ModelEvidenceCampaignError("record plan_sha256 mismatch")
    for anc_r, _ in anchor_records:
        if anc_r["plan_sha256"] != plan_sha:
            raise ModelEvidenceCampaignError("anchor record plan_sha256 mismatch")
    if plan["anchors"]["dataset_sha256"] != dataset_sha:
        raise ModelEvidenceCampaignError("plan dataset anchor does not match target dataset digest")

    expected_evaluation = evaluate_campaign(
        plan, plan_sha,
        candidate_record=candidate_record, candidate_record_sha=candidate_record_sha,
        anchor_records=anchor_records,
        review=review, review_sha=review_sha,
        dataset_sha=dataset_sha, inventory_sha=inventory_sha, matrix_sha=matrix_sha,
    )
    if evaluation != expected_evaluation:
        raise ModelEvidenceCampaignError("evaluation does not match deterministic recomputation")

    # 2. Evaluation state and all lane/candidate facts must agree.
    if plan["lane"] != "measured" or candidate_record["lane"] != "measured" or evaluation["lane"] != "measured":
        raise ModelEvidenceCampaignError("materialize-measured requires a measured lane campaign")
    for anc_r, _ in anchor_records:
        if anc_r["lane"] != "measured":
            raise ModelEvidenceCampaignError("materialize-measured requires a measured lane campaign")
    if evaluation["candidate_model_id"] != plan["candidate_model_id"]:
        raise ModelEvidenceCampaignError("materialize-measured candidate identity mismatch")
    if evaluation["recommendation"] != "candidate_evidence_only":
        raise ModelEvidenceCampaignError("materialize-measured requires candidate_evidence_only recommendation")
    if evaluation["reason_code"] != "verified-measured-evidence":
        raise ModelEvidenceCampaignError("materialize-measured requires verified-measured-evidence reason code")

    # Construct new evidence item
    mid = candidate_record["model_identity"]
    telem = candidate_record["telemetry"]
    metrics = telem["metrics"]
    measured = candidate_record["measured_metadata"]
    assert isinstance(measured, dict)
    if measured["agy_version"] != artifact_facts["agy_version"]:
        raise ModelEvidenceCampaignError("measured agy_version differs from current inventory and matrix")

    safe_item_id = f"{plan['candidate_model_id'].replace(':', '-').replace('/', '-')}-{candidate_record_sha[:8]}".lower()
    if not re.match(r"^[a-z0-9._-]+$", safe_item_id):
        safe_item_id = f"item-{candidate_record_sha[:16]}"

    new_item = {
        "id": safe_item_id,
        "provenance_type": measured["provenance_type"],
        "source_uri": measured["source_uri"],
        "observed_date": measured["observed_date"],
        "expiry_date": measured["expiry_date"],
        "harness": plan["harness"]["id"],
        "harness_version": plan["harness"]["version"],
        "agy_version": measured["agy_version"],
        "requested_model": plan["candidate_model_id"],
        "observed_model": mid["observed_model"],
        "substituted": False,
        "effort": measured["effort"],
        "task_taxonomy": plan["scenario_id"],
        "sample_size": telem["sample_count"],
        "calibration_only": False,
        "metrics": {
            "quality_score": metrics.get("quality_score"),
            "latency_p50_seconds": metrics.get("latency_p50_seconds"),
            "latency_p95_seconds": metrics.get("latency_p95_seconds"),
            "mean_input_tokens": metrics.get("mean_input_tokens"),
            "mean_output_tokens": metrics.get("mean_output_tokens"),
            "mean_cached_tokens": metrics.get("mean_cached_tokens"),
            "mean_thinking_tokens": metrics.get("mean_thinking_tokens"),
        },
        "telemetry_bindings": {
            "accounting": measured["accounting"],
            "tokenizer": measured["tokenizer"],
            "currency": measured["currency"],
            "cost_basis": measured["cost_basis"],
            "estimated_cost_per_task": metrics.get("estimated_cost_usd"),
        },
        "confidence": measured["confidence"],
        "limitations": [
            "Evidence materialized from verified offline measured campaign.",
            TOKEN_DISCLAIMER,
        ],
    }

    new_dataset = copy.deepcopy(dataset)
    new_dataset["items"].append(new_item)
    model_intelligence = _model_intelligence_module()
    try:
        model_intelligence.validate_dataset(new_dataset)
    except Exception as exc:
        raise ModelEvidenceCampaignError("materialized Model Intelligence dataset is invalid") from exc
    return new_dataset


def collect_record_files(args: Sequence[str]) -> list[tuple[dict[str, Any], str]]:
    records: list[tuple[dict[str, Any], str]] = []
    idx = 0
    while idx < len(args):
        arg = args[idx]
        if arg in {"--record", "--candidate-record", "--anchor-record"} and idx + 1 < len(args):
            path = Path(args[idx + 1])
            rec, rec_sha, _ = read_json_file(path)
            validate_record(rec)
            records.append((rec, rec_sha))
            idx += 2
        elif arg.startswith(("--record=", "--candidate-record=", "--anchor-record=")):
            path = Path(arg.partition("=")[2])
            rec, rec_sha, _ = read_json_file(path)
            validate_record(rec)
            records.append((rec, rec_sha))
            idx += 1
        elif arg == "--records-dir" and idx + 1 < len(args):
            dir_path = Path(args[idx + 1])
            if not dir_path.is_dir():
                raise ModelEvidenceCampaignError(f"--records-dir is not a directory: {dir_path}")
            for p in sorted(dir_path.glob("*.json")):
                rec, rec_sha, _ = read_json_file(p)
                validate_record(rec)
                records.append((rec, rec_sha))
            idx += 2
        elif arg.startswith("--records-dir="):
            dir_path = Path(arg.partition("=")[2])
            if not dir_path.is_dir():
                raise ModelEvidenceCampaignError(f"--records-dir is not a directory: {dir_path}")
            for p in sorted(dir_path.glob("*.json")):
                rec, rec_sha, _ = read_json_file(p)
                validate_record(rec)
                records.append((rec, rec_sha))
            idx += 1
        elif arg in {"--record", "--candidate-record", "--anchor-record", "--records-dir"}:
            raise ModelEvidenceCampaignError(f"missing value for {arg}")
        elif not arg.startswith("--"):
            # Positional record file
            path = Path(arg)
            rec, rec_sha, _ = read_json_file(path)
            validate_record(rec)
            records.append((rec, rec_sha))
            idx += 1
        else:
            raise ModelEvidenceCampaignError(f"rejected aggregate argument: {arg}")
    return records


def collect_aggregate_inputs(
    args: Sequence[str],
) -> tuple[list[tuple[dict[str, Any], str]], list[dict[str, Any]]]:
    if args.count("--local-opt-in") != 1:
        raise ModelEvidenceCampaignError("aggregate commands require one explicit --local-opt-in")
    record_args: list[str] = []
    evaluation_paths: list[Path] = []
    idx = 0
    while idx < len(args):
        arg = args[idx]
        if arg == "--local-opt-in":
            idx += 1
        elif arg == "--evaluation" and idx + 1 < len(args):
            evaluation_paths.append(Path(args[idx + 1])); idx += 2
        elif arg.startswith("--evaluation="):
            evaluation_paths.append(Path(arg.partition("=")[2])); idx += 1
        elif arg == "--evaluations-dir" and idx + 1 < len(args):
            directory = Path(args[idx + 1])
            if not directory.is_dir():
                raise ModelEvidenceCampaignError(f"--evaluations-dir is not a directory: {directory}")
            evaluation_paths.extend(sorted(directory.glob("*.json"))); idx += 2
        elif arg.startswith("--evaluations-dir="):
            directory = Path(arg.partition("=")[2])
            if not directory.is_dir():
                raise ModelEvidenceCampaignError(f"--evaluations-dir is not a directory: {directory}")
            evaluation_paths.extend(sorted(directory.glob("*.json"))); idx += 1
        else:
            record_args.append(arg)
            if arg in {"--record", "--candidate-record", "--anchor-record", "--records-dir"} and idx + 1 < len(args):
                record_args.append(args[idx + 1]); idx += 1
            idx += 1

    evaluations: list[dict[str, Any]] = []
    seen_evaluation_paths: set[Path] = set()
    for evaluation_path in evaluation_paths:
        if evaluation_path in seen_evaluation_paths:
            raise ModelEvidenceCampaignError("aggregate evaluation path is duplicated")
        seen_evaluation_paths.add(evaluation_path)
        evaluation, _, _ = read_json_file(evaluation_path)
        validate_evaluation(evaluation)
        evaluations.append(evaluation)
    return collect_record_files(record_args), evaluations


def collect_advisory_inputs(
    args: Sequence[str],
) -> tuple[
    dict[str, Any], str, list[tuple[dict[str, Any], str]], dict[str, Any], dict[str, Any]
]:
    if args.count("--local-opt-in") != 1:
        raise ModelEvidenceCampaignError("advisory commands require one explicit --local-opt-in")
    required_paths: dict[str, Path | None] = {
        "plan": None,
        "evaluation": None,
        "review": None,
        "dataset": None,
        "inventory": None,
        "matrix": None,
    }
    record_args: list[str] = []
    idx = 0
    while idx < len(args):
        arg = args[idx]
        if arg == "--local-opt-in":
            idx += 1
        elif arg.lstrip("-") in required_paths and idx + 1 < len(args):
            key = arg.lstrip("-")
            if required_paths[key] is not None:
                raise ModelEvidenceCampaignError(f"advisory {key} path is duplicated")
            required_paths[key] = Path(args[idx + 1]); idx += 2
        elif arg.startswith("--") and arg.partition("=")[0].lstrip("-") in required_paths and "=" in arg:
            key = arg.partition("=")[0].lstrip("-")
            if required_paths[key] is not None:
                raise ModelEvidenceCampaignError(f"advisory {key} path is duplicated")
            required_paths[key] = Path(arg.partition("=")[2]); idx += 1
        elif arg in {"--record", "--candidate-record", "--anchor-record", "--records-dir"}:
            if idx + 1 >= len(args):
                raise ModelEvidenceCampaignError(f"missing value for {arg}")
            record_args.extend((arg, args[idx + 1])); idx += 2
        elif arg.startswith(("--record=", "--candidate-record=", "--anchor-record=", "--records-dir=")):
            record_args.append(arg); idx += 1
        elif not arg.startswith("--"):
            record_args.append(arg); idx += 1
        else:
            raise ModelEvidenceCampaignError(f"rejected advisory argument: {arg}")
    if any(path is None for path in required_paths.values()) or not record_args:
        raise ModelEvidenceCampaignError(
            "advisory commands require --plan, records, --evaluation, --review, "
            "--dataset, --inventory, and --matrix"
        )
    plan_path = required_paths["plan"]
    evaluation_path = required_paths["evaluation"]
    assert plan_path is not None and evaluation_path is not None
    plan, plan_sha, _ = read_json_file(plan_path)
    validate_plan(plan)
    evaluation, _, _ = read_json_file(evaluation_path)
    validate_evaluation(evaluation)
    review_path = required_paths["review"]
    dataset_path = required_paths["dataset"]
    inventory_path = required_paths["inventory"]
    matrix_path = required_paths["matrix"]
    assert review_path is not None and dataset_path is not None
    assert inventory_path is not None and matrix_path is not None
    review, review_sha, _ = read_json_file(review_path)
    dataset, dataset_sha, _ = read_json_file(dataset_path, max_bytes=MAX_DATASET_BYTES)
    inventory, inventory_sha, _ = read_json_file(inventory_path)
    matrix, matrix_sha, _ = read_json_file(matrix_path)
    artifacts = {
        "review": review,
        "review_sha": review_sha,
        "dataset": dataset,
        "dataset_sha": dataset_sha,
        "inventory": inventory,
        "inventory_sha": inventory_sha,
        "matrix": matrix,
        "matrix_sha": matrix_sha,
    }
    return plan, plan_sha, collect_record_files(record_args), evaluation, artifacts


def main(argv: Sequence[str]) -> int:
    if len(argv) < 2:
        sys.stderr.write(
            "usage: model-evidence-campaign <validate-plan|evaluate|materialize-measured|advisory-preview|advisory-export|aggregate-status|aggregate-preview|aggregate-export> [options]\n"
        )
        return 2

    # Global check: reject any prohibited flags or background/watcher arguments
    for a in argv:
        for p in PROHIBITED_FLAGS:
            if a == p or a.startswith(f"{p}="):
                sys.stderr.write(f"model-evidence-campaign: rejected prohibited argument {a}\n")
                return 2

    subcmd = argv[1]
    subcmd_args = argv[2:]

    if subcmd == "validate-plan":
        plan_path: Path | None = None
        review_path: Path | None = None
        inventory_path: Path | None = None
        matrix_path: Path | None = None
        dataset_path: Path | None = None

        idx = 0
        while idx < len(subcmd_args):
            arg = subcmd_args[idx]
            if arg == "--plan" and idx + 1 < len(subcmd_args):
                plan_path = Path(subcmd_args[idx + 1])
                idx += 2
            elif arg.startswith("--plan="):
                plan_path = Path(arg.partition("=")[2])
                idx += 1
            elif arg == "--review" and idx + 1 < len(subcmd_args):
                review_path = Path(subcmd_args[idx + 1])
                idx += 2
            elif arg.startswith("--review="):
                review_path = Path(arg.partition("=")[2])
                idx += 1
            elif arg == "--inventory" and idx + 1 < len(subcmd_args):
                inventory_path = Path(subcmd_args[idx + 1])
                idx += 2
            elif arg.startswith("--inventory="):
                inventory_path = Path(arg.partition("=")[2])
                idx += 1
            elif arg == "--matrix" and idx + 1 < len(subcmd_args):
                matrix_path = Path(subcmd_args[idx + 1])
                idx += 2
            elif arg.startswith("--matrix="):
                matrix_path = Path(arg.partition("=")[2])
                idx += 1
            elif arg == "--dataset" and idx + 1 < len(subcmd_args):
                dataset_path = Path(subcmd_args[idx + 1])
                idx += 2
            elif arg.startswith("--dataset="):
                dataset_path = Path(arg.partition("=")[2])
                idx += 1
            else:
                sys.stderr.write(f"model-evidence-campaign validate-plan: rejected argument {arg}\n")
                return 2

        if any(path is None for path in (plan_path, review_path, inventory_path, matrix_path, dataset_path)):
            sys.stderr.write(
                "model-evidence-campaign validate-plan: missing required --plan, --review, --inventory, --matrix, or --dataset\n"
            )
            return 2

        try:
            plan, _, _ = read_json_file(plan_path)
            validate_plan(plan)

            assert review_path is not None and inventory_path is not None
            assert matrix_path is not None and dataset_path is not None
            rev, rev_sha, _ = read_json_file(review_path)
            inventory, inv_sha, _ = read_json_file(inventory_path)
            matrix, mat_sha, _ = read_json_file(matrix_path)
            dataset, ds_sha, _ = read_json_file(dataset_path, max_bytes=MAX_DATASET_BYTES)
            validate_campaign_artifacts(
                plan, rev, rev_sha, inventory, inv_sha, matrix, mat_sha, dataset, ds_sha
            )

            sys.stdout.write(json.dumps(plan, indent=2) + "\n")
            return 0
        except Exception as exc:
            sys.stderr.write(f"model-evidence-campaign validate-plan error: {exc}\n")
            return 2

    elif subcmd == "evaluate":
        plan_path = None
        review_path = None
        dataset_path = None
        inventory_path = None
        matrix_path = None
        out_path: Path | None = None
        record_args: list[str] = []

        idx = 0
        while idx < len(subcmd_args):
            arg = subcmd_args[idx]
            if arg == "--plan" and idx + 1 < len(subcmd_args):
                plan_path = Path(subcmd_args[idx + 1]); idx += 2
            elif arg.startswith("--plan="):
                plan_path = Path(arg.partition("=")[2]); idx += 1
            elif arg in {"--record", "--candidate-record", "--anchor-record", "--records-dir"} and idx + 1 < len(subcmd_args):
                record_args.extend([arg, subcmd_args[idx + 1]]); idx += 2
            elif arg.startswith(("--record=", "--candidate-record=", "--anchor-record=", "--records-dir=")):
                record_args.append(arg); idx += 1
            elif arg == "--review" and idx + 1 < len(subcmd_args):
                review_path = Path(subcmd_args[idx + 1]); idx += 2
            elif arg.startswith("--review="):
                review_path = Path(arg.partition("=")[2]); idx += 1
            elif arg == "--dataset" and idx + 1 < len(subcmd_args):
                dataset_path = Path(subcmd_args[idx + 1]); idx += 2
            elif arg.startswith("--dataset="):
                dataset_path = Path(arg.partition("=")[2]); idx += 1
            elif arg == "--inventory" and idx + 1 < len(subcmd_args):
                inventory_path = Path(subcmd_args[idx + 1]); idx += 2
            elif arg.startswith("--inventory="):
                inventory_path = Path(arg.partition("=")[2]); idx += 1
            elif arg == "--matrix" and idx + 1 < len(subcmd_args):
                matrix_path = Path(subcmd_args[idx + 1]); idx += 2
            elif arg.startswith("--matrix="):
                matrix_path = Path(arg.partition("=")[2]); idx += 1
            elif arg == "--out" and idx + 1 < len(subcmd_args):
                out_path = Path(subcmd_args[idx + 1]); idx += 2
            elif arg.startswith("--out="):
                out_path = Path(arg.partition("=")[2]); idx += 1
            elif not arg.startswith("--"):
                record_args.append(arg); idx += 1
            else:
                sys.stderr.write(f"model-evidence-campaign evaluate: rejected argument {arg}\n")
                return 2

        if any(path is None for path in (plan_path, review_path, inventory_path, matrix_path, dataset_path)) or not record_args:
            sys.stderr.write(
                "model-evidence-campaign evaluate: missing required --plan, records, --review, --inventory, --matrix, or --dataset\n"
            )
            return 2

        try:
            plan, plan_sha, _ = read_json_file(plan_path)
            records = collect_record_files(record_args)

            assert review_path is not None and dataset_path is not None
            assert inventory_path is not None and matrix_path is not None
            rev, rev_sha, _ = read_json_file(review_path)
            dataset, ds_sha, _ = read_json_file(dataset_path, max_bytes=MAX_DATASET_BYTES)
            inventory, inv_sha, _ = read_json_file(inventory_path)
            matrix, mat_sha, _ = read_json_file(matrix_path)
            validate_campaign_artifacts(
                plan, rev, rev_sha, inventory, inv_sha, matrix, mat_sha, dataset, ds_sha
            )

            evaluation = evaluate_campaign(
                plan, plan_sha, records=records,
                review=rev, review_sha=rev_sha,
                dataset_sha=ds_sha, inventory_sha=inv_sha, matrix_sha=mat_sha,
            )

            formatted = json.dumps(evaluation, indent=2) + "\n"
            if out_path is not None:
                publish_file_atomically(out_path, formatted.encode("utf-8"))
            sys.stdout.write(formatted)
            return 0
        except Exception as exc:
            sys.stderr.write(f"model-evidence-campaign evaluate error: {exc}\n")
            return 2

    elif subcmd == "materialize-measured":
        plan_path = None
        evaluation_path = None
        dataset_path = None
        review_path = None
        inventory_path = None
        matrix_path = None
        out_path = None
        record_args: list[str] = []

        idx = 0
        while idx < len(subcmd_args):
            arg = subcmd_args[idx]
            if arg == "--plan" and idx + 1 < len(subcmd_args):
                plan_path = Path(subcmd_args[idx + 1]); idx += 2
            elif arg.startswith("--plan="):
                plan_path = Path(arg.partition("=")[2]); idx += 1
            elif arg in {"--record", "--candidate-record", "--anchor-record", "--records-dir"} and idx + 1 < len(subcmd_args):
                record_args.extend([arg, subcmd_args[idx + 1]]); idx += 2
            elif arg.startswith(("--record=", "--candidate-record=", "--anchor-record=", "--records-dir=")):
                record_args.append(arg); idx += 1
            elif arg == "--evaluation" and idx + 1 < len(subcmd_args):
                evaluation_path = Path(subcmd_args[idx + 1]); idx += 2
            elif arg.startswith("--evaluation="):
                evaluation_path = Path(arg.partition("=")[2]); idx += 1
            elif arg == "--dataset" and idx + 1 < len(subcmd_args):
                dataset_path = Path(subcmd_args[idx + 1]); idx += 2
            elif arg.startswith("--dataset="):
                dataset_path = Path(arg.partition("=")[2]); idx += 1
            elif arg == "--review" and idx + 1 < len(subcmd_args):
                review_path = Path(subcmd_args[idx + 1]); idx += 2
            elif arg.startswith("--review="):
                review_path = Path(arg.partition("=")[2]); idx += 1
            elif arg == "--inventory" and idx + 1 < len(subcmd_args):
                inventory_path = Path(subcmd_args[idx + 1]); idx += 2
            elif arg.startswith("--inventory="):
                inventory_path = Path(arg.partition("=")[2]); idx += 1
            elif arg == "--matrix" and idx + 1 < len(subcmd_args):
                matrix_path = Path(subcmd_args[idx + 1]); idx += 2
            elif arg.startswith("--matrix="):
                matrix_path = Path(arg.partition("=")[2]); idx += 1
            elif arg == "--out" and idx + 1 < len(subcmd_args):
                out_path = Path(subcmd_args[idx + 1]); idx += 2
            elif arg.startswith("--out="):
                out_path = Path(arg.partition("=")[2]); idx += 1
            elif not arg.startswith("--"):
                record_args.append(arg); idx += 1
            else:
                sys.stderr.write(f"model-evidence-campaign materialize-measured: rejected argument {arg}\n")
                return 2

        if any(path is None for path in (
            plan_path, evaluation_path, review_path,
            inventory_path, matrix_path, dataset_path, out_path,
        )) or not record_args:
            sys.stderr.write("model-evidence-campaign materialize-measured: missing required --plan, records, --evaluation, --review, --inventory, --matrix, --dataset, or --out\n")
            return 2

        try:
            plan, plan_sha, _ = read_json_file(plan_path)
            records = collect_record_files(record_args)
            cand_records = [(r, r_sha) for r, r_sha in records if r["subject_role"] == "candidate"]
            anc_records = [(r, r_sha) for r, r_sha in records if r["subject_role"] == "anchor"]
            if len(cand_records) != 1:
                raise ModelEvidenceCampaignError("materialize-measured requires exactly one candidate record")
            candidate_record, candidate_record_sha = cand_records[0]

            eval_dict, eval_sha, _ = read_json_file(evaluation_path)
            dataset, ds_sha, _ = read_json_file(dataset_path, max_bytes=MAX_DATASET_BYTES)
            assert review_path is not None and inventory_path is not None and matrix_path is not None
            review, review_sha, _ = read_json_file(review_path)
            inventory, inventory_sha, _ = read_json_file(inventory_path)
            matrix, matrix_sha, _ = read_json_file(matrix_path)

            new_dataset = materialize_measured_dataset(
                plan, plan_sha,
                candidate_record=candidate_record,
                candidate_record_sha=candidate_record_sha,
                anchor_records=anc_records,
                evaluation=eval_dict, evaluation_sha=eval_sha,
                dataset=dataset, dataset_sha=ds_sha,
                review=review, review_sha=review_sha,
                inventory=inventory, inventory_sha=inventory_sha,
                matrix=matrix, matrix_sha=matrix_sha,
            )
            formatted = json.dumps(new_dataset, indent=2) + "\n"
            publish_file_atomically(out_path, formatted.encode("utf-8"))
            sys.stdout.write(formatted)
            return 0
        except Exception as exc:
            sys.stderr.write(f"model-evidence-campaign materialize-measured error: {exc}\n")
            return 2

    elif subcmd == "advisory-preview":
        try:
            plan, plan_sha, records, evaluation, artifacts = collect_advisory_inputs(subcmd_args)
            summary = compute_advisory_summary(
                plan, plan_sha, records, evaluation, **artifacts
            )
            preview_sha = hashlib.sha256(canonical_bytes(summary)).hexdigest()
            preview = {
                "schema_version": 1,
                "kind": "agy-model-evidence-campaign-advisory-preview",
                "preview_sha256": preview_sha,
                "payload": summary,
            }
            validate_advisory_preview(preview)
            sys.stdout.write(json.dumps(preview, indent=2) + "\n")
            return 0
        except Exception as exc:
            sys.stderr.write(f"model-evidence-campaign {subcmd} error: {exc}\n")
            return 2

    elif subcmd == "advisory-export":
        approve_sha: str | None = None
        out_path: Path | None = None
        advisory_args: list[str] = []
        idx = 0
        while idx < len(subcmd_args):
            arg = subcmd_args[idx]
            if arg == "--approve-preview-sha" and idx + 1 < len(subcmd_args):
                approve_sha = subcmd_args[idx + 1]; idx += 2
            elif arg.startswith("--approve-preview-sha="):
                approve_sha = arg.partition("=")[2]; idx += 1
            elif arg == "--out" and idx + 1 < len(subcmd_args):
                out_path = Path(subcmd_args[idx + 1]); idx += 2
            elif arg.startswith("--out="):
                out_path = Path(arg.partition("=")[2]); idx += 1
            else:
                advisory_args.append(arg)
                if arg in {
                    "--plan", "--evaluation", "--record", "--candidate-record",
                    "--anchor-record", "--records-dir", "--review", "--dataset",
                    "--inventory", "--matrix",
                } and idx + 1 < len(subcmd_args):
                    advisory_args.append(subcmd_args[idx + 1]); idx += 1
                idx += 1
        if approve_sha is None or out_path is None:
            sys.stderr.write(
                "model-evidence-campaign advisory-export: missing required --approve-preview-sha or --out\n"
            )
            return 2
        try:
            plan, plan_sha, records, evaluation, artifacts = collect_advisory_inputs(advisory_args)
            summary = compute_advisory_summary(
                plan, plan_sha, records, evaluation, **artifacts
            )
            computed_sha = hashlib.sha256(canonical_bytes(summary)).hexdigest()
            if computed_sha != approve_sha:
                sys.stderr.write(
                    "model-evidence-campaign advisory-export error: preview SHA mismatch "
                    f"(approved {approve_sha}, computed {computed_sha})\n"
                )
                return 2
            formatted = json.dumps(summary, indent=2) + "\n"
            publish_file_atomically(out_path, formatted.encode("utf-8"))
            sys.stdout.write(formatted)
            return 0
        except Exception as exc:
            sys.stderr.write(f"model-evidence-campaign advisory-export error: {exc}\n")
            return 2

    elif subcmd == "aggregate-status":
        try:
            records, evaluations = collect_aggregate_inputs(subcmd_args)
            agg = compute_aggregate(records, evaluations)
            sys.stdout.write(json.dumps(agg, indent=2) + "\n")
            return 0
        except Exception as exc:
            sys.stderr.write(f"model-evidence-campaign aggregate-status error: {exc}\n")
            return 2

    elif subcmd == "aggregate-preview":
        try:
            records, evaluations = collect_aggregate_inputs(subcmd_args)
            agg = compute_aggregate(records, evaluations)
            preview_bytes = canonical_bytes(agg)
            preview_sha = hashlib.sha256(preview_bytes).hexdigest()
            preview = {
                "schema_version": agg["schema_version"],
                "kind": "agy-model-evidence-campaign-aggregate-preview",
                "preview_sha256": preview_sha,
                "payload": agg,
            }
            validate_aggregate_preview(preview)
            sys.stdout.write(json.dumps(preview, indent=2) + "\n")
            return 0
        except Exception as exc:
            sys.stderr.write(f"model-evidence-campaign aggregate-preview error: {exc}\n")
            return 2

    elif subcmd == "aggregate-export":
        approve_sha: str | None = None
        out_path = None

        idx = 0
        aggregate_args: list[str] = []
        while idx < len(subcmd_args):
            arg = subcmd_args[idx]
            if arg == "--approve-preview-sha" and idx + 1 < len(subcmd_args):
                approve_sha = subcmd_args[idx + 1]
                idx += 2
            elif arg.startswith("--approve-preview-sha="):
                approve_sha = arg.partition("=")[2]
                idx += 1
            elif arg == "--out" and idx + 1 < len(subcmd_args):
                out_path = Path(subcmd_args[idx + 1])
                idx += 2
            elif arg.startswith("--out="):
                out_path = Path(arg.partition("=")[2])
                idx += 1
            elif arg in ("--record", "--candidate-record", "--anchor-record", "--records-dir", "--evaluation", "--evaluations-dir"):
                if idx + 1 >= len(subcmd_args):
                    sys.stderr.write(f"model-evidence-campaign aggregate-export: missing value for {arg}\n")
                    return 2
                aggregate_args.extend((arg, subcmd_args[idx + 1]))
                idx += 2
            elif (
                arg == "--local-opt-in"
                or arg.startswith(("--record=", "--candidate-record=", "--anchor-record=", "--records-dir=", "--evaluation=", "--evaluations-dir="))
                or not arg.startswith("--")
            ):
                aggregate_args.append(arg)
                idx += 1
            else:
                sys.stderr.write(f"model-evidence-campaign aggregate-export: rejected argument {arg}\n")
                return 2

        if approve_sha is None or out_path is None:
            sys.stderr.write("model-evidence-campaign aggregate-export: missing required --approve-preview-sha or --out\n")
            return 2

        try:
            records, evaluations = collect_aggregate_inputs(aggregate_args)
            agg = compute_aggregate(records, evaluations)
            preview_bytes = canonical_bytes(agg)
            computed_sha = hashlib.sha256(preview_bytes).hexdigest()

            if computed_sha != approve_sha:
                sys.stderr.write(
                    f"model-evidence-campaign aggregate-export error: preview SHA mismatch (approved {approve_sha}, computed {computed_sha})\n"
                )
                return 2

            formatted = json.dumps(agg, indent=2) + "\n"
            publish_file_atomically(out_path, formatted.encode("utf-8"))
            sys.stdout.write(formatted)
            return 0
        except Exception as exc:
            sys.stderr.write(f"model-evidence-campaign aggregate-export error: {exc}\n")
            return 2

    else:
        sys.stderr.write(f"model-evidence-campaign: unknown subcommand {subcmd}\n")
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
