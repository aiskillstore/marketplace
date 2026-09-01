#!/usr/bin/env python3
"""Progress-aware local supervisor for one agy worker conversation.

This is a local process lifecycle, not an agy/provider status API.  The controller
owns one agy process group, consumes bounded stream-json incrementally, and publishes
only sanitized control state.  Raw streams and prompts remain in the owner-private
job directory.
"""

from __future__ import annotations

import argparse
import contextlib
import fcntl
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import selectors
import signal
import shutil
import stat
import subprocess
import sys
import time
from typing import Any, Iterator

sys.dont_write_bytecode = True

STATE_NAME = "dispatch-state.json"
COMMAND_NAME = "dispatch-command.json"
LOCK_NAME = ".dispatch.lock"
STATE_LOCK_NAME = ".dispatch-state.lock"
MAX_STATE_BYTES = 128 * 1024
MAX_COMMAND_BYTES = 512 * 1024
MAX_VERIFICATION_BYTES = 16 * 1024
MAX_CHECK_ITEMS = 32
MAX_CHECK_LABEL = 160
MAX_CHECK_SUMMARY = 512
MAX_BOUNDARY_ENTRIES = 100000
MAX_STREAM_BYTES = 32 * 1024 * 1024
MAX_EVENT_BYTES = 1024 * 1024
MAX_STATUS_WAIT = 60.0
TERM_GRACE = 1.0
CONTROL_POLL = 0.20
CONVERSATION_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}")
JOB_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,79}")
SHA_RE = re.compile(r"[0-9a-f]{64}")
COMMAND_V1_FIELDS = {
    "schema_version", "kind", "job_id", "workdir", "argv", "agy_version",
    "idle_seconds", "hard_seconds", "max_seconds", "notice_seconds",
    "stage_dir", "stage_file", "child_umask", "resume_prompt",
}
COMMAND_V2_FIELDS = COMMAND_V1_FIELDS | {"workflow", "max_cycles", "continue_prompt"}
COMMAND_V3_FIELDS = COMMAND_V2_FIELDS | {"agy_version_observed"}
COMMAND_V4_FIELDS = COMMAND_V3_FIELDS | {"selection_path", "selection_sha256", "selection_identity"}
COMMAND_V5_FIELDS = COMMAND_V4_FIELDS | {"provider_env"}
COMMAND_V6_FIELDS = COMMAND_V5_FIELDS | {
    "provider_scope_path", "provider_scope_sha256", "provider_scope_identity", "approved_transmission_sha256",
}
STATE_PROJECT_FIELDS = {
    "workflow", "max_cycles", "cycle", "phase", "assurance",
    "check_summary", "check_counts", "verification_path", "verification_sha256",
    "verification_identity", "continue_available", "last_success_path",
    "last_success_sha256", "last_success_identity",
    "project_boundary",
}
STATE_V5_FIELDS = {
    "candidate_recognized", "candidate_source", "result_available",
    "worktree_reconciliation", "worktree_changes_present",
    "worktree_changed_since_dispatch", "driver_disposition", "failure_stage",
    "last_activity", "next_action", "next_action_command", "worktree_baseline",
    "provider_schema_sha256", "provider_schema_identity",
    "canonical_schema_sha256", "canonical_schema_identity",
    "candidate_worktree_sha256", "candidate_worktree_entries",
}
STATE_V6_FIELDS = {"selection_sha256", "selection_identity"}
STATE_V8_FIELDS = {"worktree_snapshot_algorithm"}
STATE_V9_FIELDS = {"worktree_root_identity"}
STATE_V10_FIELDS = {"provider_terminal_status"}
STATE_V11_FIELDS = {
    "provider_scope_path", "provider_scope_sha256", "provider_scope_identity",
    "approved_transmission_sha256", "transmission_sha256",
    "selected_content_sha256", "selected_file_count", "selected_tree_count",
    "provider_stage_path", "provider_stage_identity",
    "provider_stage_manifest_sha256", "reconciliation_manifest_sha256",
}
PUBLIC_LAUNCHER = '"$PIPELINE/agy-worker.sh"'
CURRENT_STATE_SCHEMA = 11
WORKTREE_SNAPSHOT_LEGACY_V6 = "legacy-v6"
WORKTREE_SNAPSHOT_SEMANTIC_V1 = "semantic-v1"
CURRENT_WORKTREE_SNAPSHOT_ALGORITHM = WORKTREE_SNAPSHOT_SEMANTIC_V1
FAILURE_STAGES = {
    "framing", "outer_status", "missing_structured_output", "schema_rejection",
    "binding_failure", "selection_preflight",
}
LIFECYCLE_PHASES = {
    "dispatching", "awaiting-verification", "repairing", "completed",
    "blocked", "attempt-failed", "repair-failed",
}
TERMINAL = {"succeeded", "failed", "cancelled", "orphaned"}
REASONS = {
    "provider_timeout", "idle_timeout", "hard_deadline_exceeded",
    "authentication_failed", "provider_unavailable", "status_unavailable",
    "resume_failed", "cancelled", "agy_failed_unclassified",
    "permission_required", "empty_output", "invalid_envelope",
    "output_oversized", "interrupted", "provider_quota_exhausted",
    "provider_terminal_error", "provider_terminal_cancelled",
    "selection_preflight_failed", "resolve_undo_present",
}
EXIT_BY_REASON = {
    "empty_output": 3,
    "invalid_envelope": 4,
    "agy_failed_unclassified": 5,
    "permission_required": 6,
    "idle_timeout": 9,
    "hard_deadline_exceeded": 16,
    "provider_timeout": 17,
    "authentication_failed": 18,
    "provider_unavailable": 19,
    "status_unavailable": 20, "resolve_undo_present": 20,
    "resume_failed": 21,
    "cancelled": 22,
    "output_oversized": 23,
    "provider_quota_exhausted": 24,
    "provider_terminal_error": 25,
    "selection_preflight_failed": 26,
    "provider_terminal_cancelled": 22,
    "interrupted": 143,
}

# These are exact, version-scoped observations.  Unknown text remains unclassified;
# no broad substring or prose inference may decide auth/provider state.
# Populated only from retained, version-bound observations.  There is currently no
# reviewed 1.1.12 stderr evidence in the repository, so every provider diagnostic
# remains deliberately unclassified.
EXACT_FAILURE_LINES: dict[str, dict[bytes, str]] = {"1.1.12": {}}

# agy 1.1.13 emitted this exact provider-owned terminal error shape in three
# retained same-conversation observations. The reset duration is the only
# variable part. Do not broaden this to free-form quota/message matching or to
# another agy version without separately reviewed evidence.
QUOTA_ERROR_1_1_13_RE = re.compile(
    r"rpc error: Individual quota reached\. Contact your administrator to enable "
    r"overages\. Resets in (?P<hours>[0-9]{1,3})h"
    r"(?P<minutes>[0-9]{2})m(?P<seconds>[0-9]{2})s\."
)
QUOTA_RESULT_FIELDS = {
    "conversation_id", "status", "response", "error", "duration_seconds",
    "num_turns", "json_schema", "usage",
}
MAX_PROVIDER_RETRY_SECONDS = 30 * 24 * 3600


class DispatchError(ValueError):
    pass


class SelectionPreflightError(DispatchError):
    """A direct caller selection could not be safely reprobed for one launch."""


class WorktreeBaselineError(DispatchError):
    """The queued worktree baseline is unavailable or no longer exact."""

class ResolveUndoPresentError(WorktreeBaselineError):
    """A valid, non-empty REUC observation is present in the worktree index."""

_selection_spec = importlib.util.spec_from_file_location(
    "agy_dispatch_model_selection", Path(__file__).with_name("model_selection.py"),
)
if _selection_spec is None or _selection_spec.loader is None:  # pragma: no cover - package invariant
    raise RuntimeError("model selection runtime is unavailable")
# Loading this sibling as a module (rather than a subprocess) keeps the re-probe
# path private.  Its local compatibility dependency is package-owned too.
if str(Path(__file__).parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).parent))
MODEL_SELECTION = importlib.util.module_from_spec(_selection_spec)
_selection_spec.loader.exec_module(MODEL_SELECTION)


class Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        del message
        self.print_usage(sys.stderr)
        self.exit(64, "agy-dispatch: invalid arguments\n")


def canonical(value: Any) -> bytes:
    try:
        return json.dumps(
            value, ensure_ascii=True, sort_keys=True, separators=(",", ":")
        ).encode("ascii") + b"\n"
    except RecursionError as exc:
        raise DispatchError("JSON structure is invalid") from exc


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _parse_resolve_undo(
    raw: bytes, object_length: int,
) -> dict[tuple[bytes, int], tuple[int, bytes]] | None:
    """Strictly parse ``ls-files --resolve-undo -z`` records.

    V7 does not persist REUC records: any well-formed record makes the semantic
    snapshot unavailable.  Parsing first keeps malformed, duplicate, and
    unsupported output fail-closed instead of treating it as an empty result.
    """
    if object_length not in {40, 64}:
        return None
    if not raw:
        return {}
    if not raw.endswith(b"\0"):
        return None
    parsed: dict[tuple[bytes, int], tuple[int, bytes]] = {}
    for record in raw.split(b"\0")[:-1]:
        try:
            header, relative = record.split(b"\t", 1)
            mode_raw, oid, stage_raw = header.split(b" ")
            mode = int(mode_raw, 8)
            stage = int(stage_raw, 10)
        except (ValueError, TypeError):
            return None
        parts = relative.split(b"/")
        key = (relative, stage)
        if (
            mode not in {0o100644, 0o100755, 0o120000, 0o160000}
            or len(oid) != object_length
            or any(char not in b"0123456789abcdef" for char in oid)
            or stage not in {1, 2, 3}
            or not relative or relative.startswith(b"/")
            or any(part in {b"", b".", b".."} for part in parts)
            or parts[0] == b".git"
            or key in parsed
        ):
            return None
        parsed[key] = (mode, oid)
    return parsed


def _duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DispatchError("JSON contains duplicate fields")
        result[key] = value
    return result


def _invalid_json_constant(_value: str) -> None:
    raise DispatchError("JSON contains a non-finite number")


def parse_json(raw: bytes, label: str) -> Any:
    try:
        return json.loads(
            raw.decode("utf-8", "strict"), object_pairs_hook=_duplicates,
            parse_constant=_invalid_json_constant,
        )
    except (UnicodeError, json.JSONDecodeError, DispatchError, RecursionError) as exc:
        raise DispatchError(f"{label} is invalid") from exc


def _valid_max_cycles(workflow: str, value: Any) -> bool:
    if type(value) is not int:
        return False
    if workflow == "legacy":
        return value == 1
    if workflow in {"explore", "task"}:
        return 1 <= value <= 2
    return workflow == "project" and 1 <= value <= 5


def _identity(info: os.stat_result) -> tuple[int, int, int, int, int]:
    return (
        info.st_dev, info.st_ino, info.st_uid, info.st_gid,
        stat.S_IMODE(info.st_mode),
    )


def canonical_job(path: Path) -> Path:
    if not path.is_absolute() or Path(os.path.realpath(path)) != path:
        raise DispatchError("job directory must be one canonical absolute path")
    try:
        info = path.lstat()
    except OSError as exc:
        raise DispatchError("job directory is unavailable") from exc
    if (
        not stat.S_ISDIR(info.st_mode)
        or stat.S_ISLNK(info.st_mode)
        or info.st_uid != os.getuid()
        or stat.S_IMODE(info.st_mode) != 0o700
    ):
        raise DispatchError("job directory must be owner-private")
    return path


def _job_is_inside_worktree(job: Path, workdir: str | Path) -> bool:
    try:
        job_text = os.fsdecode(job)
        workdir_text = os.fsdecode(workdir)
        if "\0" in job_text or "\0" in workdir_text:
            return True
        resolved_job = Path(os.path.realpath(job_text))
        resolved_workdir = Path(os.path.realpath(workdir_text))
        if resolved_job == resolved_workdir:
            return True
        return os.path.commonpath([resolved_workdir, resolved_job]) == str(resolved_workdir)
    except (TypeError, UnicodeError, ValueError, OSError):
        return True


def read_regular(
    path: Path, maximum: int, label: str, *, allowed_modes: tuple[int, ...] = (0o600,),
) -> tuple[bytes, os.stat_result]:
    try:
        descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    except OSError as exc:
        raise DispatchError(f"{label} is unavailable") from exc
    try:
        info = os.fstat(descriptor)
        if (
            not stat.S_ISREG(info.st_mode)
            or info.st_uid != os.getuid()
            or stat.S_IMODE(info.st_mode) not in allowed_modes
            or info.st_nlink != 1
        ):
            raise DispatchError(f"{label} must be one owner-private regular file")
        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = os.read(descriptor, min(65536, maximum + 1 - total))
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
            if total > maximum:
                raise DispatchError(f"{label} is oversized")
        after = os.fstat(descriptor)
    finally:
        os.close(descriptor)
    try:
        named = path.lstat()
    except OSError as exc:
        raise DispatchError(f"{label} identity changed") from exc
    if _identity(info) != _identity(after) or _identity(after) != _identity(named):
        raise DispatchError(f"{label} identity changed")
    return b"".join(chunks), named


def write_atomic(job: Path, name: str, value: Any) -> tuple[bytes, str]:
    raw = canonical(value)
    temporary = job / f".{name}.{os.getpid()}.{time.monotonic_ns()}.tmp"
    descriptor = os.open(
        temporary,
        os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
        0o600,
    )
    try:
        os.fchmod(descriptor, 0o600)
        view = memoryview(raw)
        while view:
            written = os.write(descriptor, view)
            if written <= 0:
                raise DispatchError("state write failed")
            view = view[written:]
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    os.replace(temporary, job / name)
    parent = os.open(job, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        os.fsync(parent)
    finally:
        os.close(parent)
    return raw, digest(raw)


@contextlib.contextmanager
def lifecycle_lock(job: Path, *, blocking: bool) -> Iterator[int]:
    path = job / LOCK_NAME
    descriptor = os.open(
        path,
        os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0),
        0o600,
    )
    try:
        os.fchmod(descriptor, 0o600)
        operation = fcntl.LOCK_EX | (0 if blocking else fcntl.LOCK_NB)
        try:
            fcntl.flock(descriptor, operation)
        except BlockingIOError as exc:
            raise DispatchError("dispatch controller is active") from exc
        yield descriptor
    finally:
        os.close(descriptor)


@contextlib.contextmanager
def state_lock(job: Path) -> Iterator[int]:
    """Serialize short state replacements without sharing controller ownership."""

    path = job / STATE_LOCK_NAME
    descriptor = os.open(
        path,
        os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0),
        0o600,
    )
    try:
        os.fchmod(descriptor, 0o600)
        fcntl.flock(descriptor, fcntl.LOCK_EX)
        yield descriptor
    finally:
        os.close(descriptor)


@contextlib.contextmanager
def inherited_lifecycle_lock(job: Path, descriptor: int) -> Iterator[int]:
    """Adopt the spawner's already-held lock without an unlock/relock gap."""

    try:
        info = os.fstat(descriptor)
        named = (job / LOCK_NAME).lstat()
    except OSError as exc:
        raise DispatchError("inherited dispatch ownership is unavailable") from exc
    if (
        not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid()
        or stat.S_IMODE(info.st_mode) != 0o600
        or _identity(info) != _identity(named)
    ):
        raise DispatchError("inherited dispatch ownership is invalid")
    try:
        yield descriptor
    finally:
        os.close(descriptor)


def load_state(job: Path) -> tuple[dict[str, Any], bytes, str]:
    raw, _info = read_regular(job / STATE_NAME, MAX_STATE_BYTES, "dispatch state")
    value = parse_json(raw, "dispatch state")
    value = validate_state(value)
    return value, raw, digest(raw)


def read_state_snapshot(job: Path) -> tuple[dict[str, Any], bytes, str]:
    """Read one strict state snapshot without racing an approved replacement."""

    with state_lock(job):
        return load_state(job)


def load_command(job: Path) -> tuple[dict[str, Any], bytes, tuple[int, int, int, int, int]]:
    raw, info = read_regular(job / COMMAND_NAME, MAX_COMMAND_BYTES, "dispatch command")
    value = parse_json(raw, "dispatch command")
    if not isinstance(value, dict):
        raise DispatchError("dispatch command fields are invalid")
    if set(value) == COMMAND_V1_FIELDS and value.get("schema_version") == 1:
        if raw != canonical(value):
            raise DispatchError("legacy dispatch command is not canonical")
        value = dict(value)
        value.update({
            "workflow": "legacy", "max_cycles": 1,
            "continue_prompt": "legacy commands cannot continue projects",
            "agy_version_observed": False,
            "selection_path": None, "selection_sha256": None, "selection_identity": None,
            "provider_env": [],
        })
    elif set(value) == COMMAND_V2_FIELDS and value.get("schema_version") == 2:
        if raw != canonical(value):
            raise DispatchError("dispatch command is not canonical")
        value = dict(value)
        value["agy_version_observed"] = False
        value.update({
            "selection_path": None, "selection_sha256": None, "selection_identity": None,
            "provider_env": [],
        })
    elif set(value) == COMMAND_V3_FIELDS and value.get("schema_version") == 3:
        if raw != canonical(value):
            raise DispatchError("dispatch command is not canonical")
        value = dict(value)
        value.update({
            "selection_path": None, "selection_sha256": None, "selection_identity": None,
            "provider_env": [],
        })
    elif set(value) == COMMAND_V4_FIELDS and value.get("schema_version") == 4:
        if raw != canonical(value):
            raise DispatchError("dispatch command is not canonical")
        value = dict(value)
        value["provider_env"] = []
    elif set(value) == COMMAND_V5_FIELDS and value.get("schema_version") == 5:
        if raw != canonical(value):
            raise DispatchError("dispatch command is not canonical")
        value = dict(value)
        value.update({
            "provider_scope_path": None,
            "provider_scope_sha256": None,
            "provider_scope_identity": None,
            "approved_transmission_sha256": None,
        })
    elif set(value) != COMMAND_V6_FIELDS or value.get("schema_version") != 6:
        raise DispatchError("dispatch command fields are invalid")
    elif raw != canonical(value):
        raise DispatchError("dispatch command is not canonical")
    if value["kind"] != "agy-worker-dispatch-command":
        raise DispatchError("dispatch command version is invalid")
    if (
        not isinstance(value["agy_version"], str)
        or re.fullmatch(
            r"(?:0|[1-9][0-9]{0,4})\.(?:0|[1-9][0-9]{0,4})\."
            r"(?:0|[1-9][0-9]{0,4})",
            value["agy_version"],
        ) is None
    ):
        raise DispatchError("dispatch agy version is invalid")
    if not isinstance(value["job_id"], str) or JOB_RE.fullmatch(value["job_id"]) is None:
        raise DispatchError("dispatch command job ID is invalid")
    if not isinstance(value["argv"], list) or not value["argv"] or any(
        not isinstance(item, str) or "\x00" in item for item in value["argv"]
    ):
        raise DispatchError("dispatch argv is invalid")
    if value["argv"][0] != "agy" or value["argv"].count("--print") != 1:
        raise DispatchError("dispatch argv contract is invalid")
    if not isinstance(value["workdir"], str) or not Path(value["workdir"]).is_absolute():
        raise DispatchError("dispatch workdir is invalid")
    for key in ("idle_seconds", "hard_seconds", "max_seconds", "notice_seconds"):
        if type(value[key]) not in (int, float) or not (0 < value[key] <= 7 * 24 * 3600):
            raise DispatchError("dispatch duration is invalid")
    if not (value["idle_seconds"] <= value["hard_seconds"] <= value["max_seconds"]):
        raise DispatchError("dispatch duration order is invalid")
    for key in ("stage_dir", "stage_file"):
        if value[key] is not None and (
            not isinstance(value[key], str) or not Path(value[key]).is_absolute()
        ):
            raise DispatchError("dispatch stage path is invalid")
    if not isinstance(value["child_umask"], str) or re.fullmatch(r"[0-7]{3,4}", value["child_umask"]) is None:
        raise DispatchError("dispatch child umask is invalid")
    if not isinstance(value["resume_prompt"], str) or not value["resume_prompt"]:
        raise DispatchError("dispatch resume prompt is invalid")
    if not isinstance(value["continue_prompt"], str) or not value["continue_prompt"]:
        raise DispatchError("dispatch continue prompt is invalid")
    if not isinstance(value["provider_env"], list) or any(
        not isinstance(item, str) for item in value["provider_env"]
    ):
        raise DispatchError("dispatch provider environment is invalid")
    try:
        if MODEL_SELECTION.validate_child_environment_names(value["provider_env"]) != value["provider_env"]:
            raise DispatchError("dispatch provider environment is not canonical")
    except MODEL_SELECTION.EvidenceUnavailable as exc:
        raise DispatchError("dispatch provider environment is invalid") from exc
    if value["workflow"] not in {"legacy", "explore", "task", "project"}:
        raise DispatchError("dispatch workflow is invalid")
    if not _valid_max_cycles(value["workflow"], value["max_cycles"]):
        raise DispatchError("dispatch max cycles is invalid for workflow")
    if type(value["agy_version_observed"]) is not bool:
        raise DispatchError("dispatch agy version evidence is invalid")
    selection_path = value["selection_path"]
    selection_sha = value["selection_sha256"]
    selection_identity = value["selection_identity"]
    if (selection_path is None) != (selection_sha is None) or (selection_path is None) != (selection_identity is None):
        raise DispatchError("dispatch selection binding is incomplete")
    if selection_path is not None and (
        not isinstance(selection_path, str) or not Path(selection_path).is_absolute()
        or not isinstance(selection_sha, str) or SHA_RE.fullmatch(selection_sha) is None
        or not isinstance(selection_identity, list) or len(selection_identity) != 5
        or any(type(item) is not int or item < 0 for item in selection_identity)
    ):
        raise DispatchError("dispatch selection binding is invalid")
    scope_path = value.get("provider_scope_path")
    scope_sha = value.get("provider_scope_sha256")
    scope_identity = value.get("provider_scope_identity")
    approved_sha = value.get("approved_transmission_sha256")
    if (scope_path is None) != (scope_sha is None) or (scope_path is None) != (scope_identity is None) or (scope_path is None) != (approved_sha is None):
        raise DispatchError("dispatch provider scope binding is incomplete")
    if scope_path is not None and (
        not isinstance(scope_path, str) or not Path(scope_path).is_absolute()
        or not isinstance(scope_sha, str) or SHA_RE.fullmatch(scope_sha) is None
        or not isinstance(scope_identity, list) or len(scope_identity) != 5
        or any(type(item) is not int or item < 0 for item in scope_identity)
        or not isinstance(approved_sha, str) or SHA_RE.fullmatch(approved_sha) is None
    ):
        raise DispatchError("dispatch provider scope binding is invalid")
    if scope_path is not None and "--add-dir" in value["argv"]:
        raise DispatchError("narrow provider scope cannot grant an additional directory")
    return value, raw, _identity(info)


def validate_state(value: Any) -> dict[str, Any]:
    fields = {
        "schema_version", "kind", "sequence", "previous_state_sha256", "job_id",
        "status", "attempt", "attempt_origin", "reason", "exit_code",
        "controller_pid", "workdir", "created_epoch", "started_epoch",
        "updated_epoch", "finished_epoch", "elapsed_seconds", "progress_count",
        "last_progress_epoch", "notice_count", "hard_seconds", "max_seconds",
        "cancel_requested", "conversation_id", "resume_available",
        "remote_cancel_unverified", "result_path", "stream_path", "stderr_path",
        "agy_returncode", "limit_kind", "command_sha256", "command_identity",
        "stage_sha256", "stage_identity", "result_sha256", "result_identity",
        "idle_seconds", "attempt_base_elapsed",
        "workflow", "max_cycles", "cycle", "phase", "assurance",
        "check_summary", "check_counts", "verification_path", "verification_sha256",
        "verification_identity", "continue_available", "last_success_path",
        "last_success_sha256", "last_success_identity", "project_boundary",
        "provider_retry_after_seconds", "provider_retry_observed_epoch",
        "candidate_recognized", "candidate_source", "result_available",
        "worktree_reconciliation", "worktree_changes_present",
        "worktree_changed_since_dispatch", "driver_disposition", "failure_stage",
        "last_activity", "next_action", "next_action_command", "worktree_baseline",
        "provider_schema_sha256", "provider_schema_identity",
        "canonical_schema_sha256", "canonical_schema_identity",
        "candidate_worktree_sha256", "candidate_worktree_entries",
        "selection_sha256", "selection_identity",
        "worktree_snapshot_algorithm", "worktree_root_identity",
        "provider_terminal_status",
    }
    fields |= STATE_V11_FIELDS
    retry_fields = {"provider_retry_after_seconds", "provider_retry_observed_epoch"}
    legacy_fields = fields - STATE_PROJECT_FIELDS - retry_fields - STATE_V5_FIELDS - STATE_V6_FIELDS - STATE_V8_FIELDS - STATE_V9_FIELDS - STATE_V10_FIELDS - STATE_V11_FIELDS
    version_three_fields = fields - retry_fields - STATE_V5_FIELDS - STATE_V6_FIELDS - STATE_V8_FIELDS - STATE_V9_FIELDS - STATE_V10_FIELDS - STATE_V11_FIELDS
    version_four_fields = fields - STATE_V5_FIELDS - STATE_V6_FIELDS - STATE_V8_FIELDS - STATE_V9_FIELDS - STATE_V10_FIELDS - STATE_V11_FIELDS
    version_five_fields = fields - STATE_V6_FIELDS - STATE_V8_FIELDS - STATE_V9_FIELDS - STATE_V10_FIELDS - STATE_V11_FIELDS
    version_six_fields = fields - STATE_V8_FIELDS - STATE_V9_FIELDS - STATE_V10_FIELDS - STATE_V11_FIELDS
    version_seven_fields = fields - STATE_V8_FIELDS - STATE_V9_FIELDS - STATE_V10_FIELDS - STATE_V11_FIELDS
    version_eight_fields = fields - STATE_V9_FIELDS - STATE_V10_FIELDS - STATE_V11_FIELDS
    version_nine_fields = fields - STATE_V10_FIELDS - STATE_V11_FIELDS
    version_ten_fields = fields - STATE_V11_FIELDS
    if not isinstance(value, dict):
        raise DispatchError("dispatch state fields are invalid")
    if set(value) == legacy_fields and value.get("schema_version") == 1:
        value = dict(value)
        recognized = value["result_path"] is not None
        value.update({
            "workflow": "legacy", "max_cycles": 1, "cycle": value["attempt"],
            "phase": None, "assurance": None, "check_summary": None,
            "check_counts": {"passed": 0, "failed": 0, "advisory": 0, "missing": 0},
            "verification_path": None, "verification_sha256": None,
            "verification_identity": None, "continue_available": False,
            "last_success_path": None, "last_success_sha256": None,
            "last_success_identity": None, "project_boundary": None,
            "provider_retry_after_seconds": None,
            "provider_retry_observed_epoch": None,
            "candidate_recognized": recognized,
            "candidate_source": "provider_success" if recognized else "none",
            "result_available": recognized, "worktree_reconciliation": "not_applicable",
            "worktree_changes_present": None, "worktree_changed_since_dispatch": None,
            "driver_disposition": "unreviewed" if recognized else "not_applicable",
            "failure_stage": None, "last_activity": None,
            "next_action": "driver_review" if recognized else "none",
            "next_action_command": None,
            "worktree_baseline": None,
            "provider_schema_sha256": None, "provider_schema_identity": None,
            "canonical_schema_sha256": None, "canonical_schema_identity": None,
            "candidate_worktree_sha256": None, "candidate_worktree_entries": None,
            "selection_sha256": None, "selection_identity": None,
        })
    elif set(value) == version_three_fields and value.get("schema_version") == 3:
        value = dict(value)
        value.update({
            "provider_retry_after_seconds": None,
            "provider_retry_observed_epoch": None,
            # ``last_success_*`` was a historical compatibility pointer, not
            # proof of the outer provider outcome or a driver-reviewed
            # candidate.  Keep it distinct from the current result binding.
            "candidate_recognized": bool(value["result_path"]),
            "candidate_source": "provider_success" if value["result_path"] else "none",
            "result_available": bool(value["result_path"]),
            "worktree_reconciliation": "not_applicable",
            "worktree_changes_present": None, "worktree_changed_since_dispatch": None,
            "driver_disposition": "unreviewed" if value["result_path"] else "not_applicable",
            "failure_stage": None, "last_activity": None,
            "next_action": "driver_review" if value["result_path"] else "none",
            "next_action_command": None, "worktree_baseline": None,
            "provider_schema_sha256": None, "provider_schema_identity": None,
            "canonical_schema_sha256": None, "canonical_schema_identity": None,
            "candidate_worktree_sha256": None, "candidate_worktree_entries": None,
            "selection_sha256": None, "selection_identity": None,
        })
    elif set(value) == version_four_fields and value.get("schema_version") == 4:
        value = dict(value)
        value.update({
            "candidate_recognized": bool(value["result_path"]),
            "candidate_source": "provider_success" if value["result_path"] else "none",
            "result_available": bool(value["result_path"]),
            "worktree_reconciliation": "not_applicable",
            "worktree_changes_present": None, "worktree_changed_since_dispatch": None,
            "driver_disposition": "unreviewed" if value["result_path"] else "not_applicable",
            "failure_stage": None, "last_activity": None,
            "next_action": "driver_review" if value["result_path"] else "none",
            "next_action_command": None, "worktree_baseline": None,
            "provider_schema_sha256": None, "provider_schema_identity": None,
            "canonical_schema_sha256": None, "canonical_schema_identity": None,
            "candidate_worktree_sha256": None, "candidate_worktree_entries": None,
            "selection_sha256": None, "selection_identity": None,
        })
    elif set(value) == version_five_fields and value.get("schema_version") == 5:
        value = dict(value)
        value.update({
            "selection_sha256": None, "selection_identity": None,
        })
    elif set(value) == version_six_fields and value.get("schema_version") == 6:
        pass
    elif set(value) == version_seven_fields and value.get("schema_version") == 7:
        pass
    elif set(value) == version_eight_fields and value.get("schema_version") == 8:
        pass
    elif set(value) == version_nine_fields and value.get("schema_version") == 9:
        pass
    elif set(value) == version_ten_fields and value.get("schema_version") == 10:
        pass
    elif set(value) != fields or value.get("schema_version") != CURRENT_STATE_SCHEMA:
        raise DispatchError("dispatch state fields are invalid")
    if value["kind"] != "agy-worker-dispatch-state":
        raise DispatchError("dispatch state version is invalid")
    if value["schema_version"] in {9, 10, CURRENT_STATE_SCHEMA} and (
        value["worktree_snapshot_algorithm"] != CURRENT_WORKTREE_SNAPSHOT_ALGORITHM
    ):
        raise DispatchError("dispatch worktree snapshot algorithm is invalid")
    if value["schema_version"] in {10, CURRENT_STATE_SCHEMA} and (
        value.get("provider_terminal_status") not in {"unknown", "success", "error", "cancelled"}
    ):
        raise DispatchError("dispatch provider terminal status is invalid")
    root_identity = value.get("worktree_root_identity")
    if value["schema_version"] in {9, 10, CURRENT_STATE_SCHEMA}:
        def valid_authority(authority: Any, *, directory: bool | None = None) -> bool:
            if not isinstance(authority, dict) or set(authority) != {
                "dev", "ino", "type", "mode", "uid", "gid",
            }:
                return False
            if any(type(authority[key]) is not int or authority[key] < 0 for key in authority):
                return False
            if authority["type"] not in {stat.S_IFDIR, stat.S_IFREG}:
                return False
            return directory is None or (authority["type"] == stat.S_IFDIR) == directory

        if (
            not isinstance(root_identity, dict)
            or set(root_identity) != {
                "root", "git_marker", "git_dir", "common_dir", "object_format", "show_toplevel",
            }
            or not isinstance(root_identity["root"], dict)
            or set(root_identity["root"]) != {"realpath", "dev", "ino"}
            or not isinstance(root_identity["root"]["realpath"], str)
            or not os.path.isabs(root_identity["root"]["realpath"])
            or type(root_identity["root"]["dev"]) is not int or root_identity["root"]["dev"] < 0
            or type(root_identity["root"]["ino"]) is not int or root_identity["root"]["ino"] < 0
            or root_identity["show_toplevel"] != root_identity["root"]["realpath"]
            or root_identity["object_format"] not in {"sha1", "sha256"}
            or not isinstance(root_identity["git_marker"], dict)
            or set(root_identity["git_marker"]) != {"kind", "authority", "content_sha256"}
            or root_identity["git_marker"]["kind"] not in {"directory", "file"}
            or not valid_authority(
                root_identity["git_marker"]["authority"],
                directory=root_identity["git_marker"]["kind"] == "directory",
            )
            or (
                root_identity["git_marker"]["content_sha256"] is not None
                if root_identity["git_marker"]["kind"] == "directory" else
                not isinstance(root_identity["git_marker"]["content_sha256"], str)
                or SHA_RE.fullmatch(root_identity["git_marker"]["content_sha256"]) is None
            )
            or any(
                not isinstance(root_identity[key], dict)
                or set(root_identity[key]) != {"realpath", "authority"}
                or not isinstance(root_identity[key]["realpath"], str)
                or not os.path.isabs(root_identity[key]["realpath"])
                or not valid_authority(root_identity[key]["authority"], directory=True)
                for key in ("git_dir", "common_dir")
            )
        ):
            raise DispatchError("dispatch worktree root identity is invalid")
    if type(value["sequence"]) is not int or value["sequence"] < 1:
        raise DispatchError("dispatch sequence is invalid")
    previous = value["previous_state_sha256"]
    if previous is not None and (not isinstance(previous, str) or SHA_RE.fullmatch(previous) is None):
        raise DispatchError("dispatch history is invalid")
    if (value["sequence"] == 1) != (previous is None):
        raise DispatchError("dispatch history is inconsistent")
    if value["status"] not in {"queued", "running", "cancel-requested", *TERMINAL}:
        raise DispatchError("dispatch status is invalid")
    if value["reason"] is not None and value["reason"] not in REASONS:
        raise DispatchError("dispatch reason is invalid")
    if type(value["candidate_recognized"]) is not bool or type(value["result_available"]) is not bool:
        raise DispatchError("dispatch candidate flags are invalid")
    if value["candidate_source"] not in {"none", "provider_success", "provider_error", "provider_cancelled"}:
        raise DispatchError("dispatch candidate source is invalid")
    if (
        value["candidate_recognized"] != (value["candidate_source"] != "none")
        or (value["result_available"] and not value["candidate_recognized"])
    ):
        raise DispatchError("dispatch candidate state is inconsistent")
    if value["worktree_reconciliation"] not in {"available", "unavailable", "not_applicable"}:
        raise DispatchError("dispatch worktree reconciliation is invalid")
    for key in ("worktree_changes_present", "worktree_changed_since_dispatch"):
        if value[key] is not None and type(value[key]) is not bool:
            raise DispatchError("dispatch worktree observation is invalid")
    if value["worktree_reconciliation"] == "available" and (
        value["worktree_changes_present"] is None or value["worktree_changed_since_dispatch"] is None
    ):
        raise DispatchError("dispatch worktree reconciliation is incomplete")
    if value["worktree_reconciliation"] != "available" and (
        value["worktree_changes_present"] is not None or value["worktree_changed_since_dispatch"] is not None
    ):
        raise DispatchError("dispatch unavailable worktree reconciliation has observations")
    if value["driver_disposition"] not in {"not_applicable", "unreviewed", "verified", "partially_verified", "rejected", "blocked"}:
        raise DispatchError("dispatch driver disposition is invalid")
    if value["failure_stage"] not in {None, *FAILURE_STAGES}:
        raise DispatchError("dispatch failure stage is invalid")
    if value["last_activity"] not in {None, "provider_initialized", "progress_signal", "terminal_received"}:
        raise DispatchError("dispatch activity is invalid")
    if value["next_action"] not in {"none", "wait", "resume", "restart", "driver_review", "driver_finalize", "blocked"}:
        raise DispatchError("dispatch next action is invalid")
    if value["next_action_command"] is not None and (not isinstance(value["next_action_command"], str) or not value["next_action_command"]):
        raise DispatchError("dispatch next action command is invalid")
    baseline = value["worktree_baseline"]
    if baseline is not None and (
        not isinstance(baseline, dict) or set(baseline) != {"sha256", "entries"}
        or not isinstance(baseline["sha256"], str) or SHA_RE.fullmatch(baseline["sha256"]) is None
        or type(baseline["entries"]) is not int or not (0 <= baseline["entries"] <= MAX_BOUNDARY_ENTRIES)
    ):
        raise DispatchError("dispatch worktree baseline is invalid")
    candidate_worktree_sha = value["candidate_worktree_sha256"]
    candidate_worktree_entries = value["candidate_worktree_entries"]
    if (candidate_worktree_sha is None) != (candidate_worktree_entries is None):
        raise DispatchError("dispatch candidate worktree binding is incomplete")
    if candidate_worktree_sha is not None and (
        not isinstance(candidate_worktree_sha, str)
        or SHA_RE.fullmatch(candidate_worktree_sha) is None
        or type(candidate_worktree_entries) is not int
        or not (0 <= candidate_worktree_entries <= MAX_BOUNDARY_ENTRIES)
    ):
        raise DispatchError("dispatch candidate worktree binding is invalid")
    for digest_key, identity_key in (
        ("provider_schema_sha256", "provider_schema_identity"),
        ("canonical_schema_sha256", "canonical_schema_identity"),
    ):
        bound_digest, bound_identity = value[digest_key], value[identity_key]
        if (bound_digest is None) != (bound_identity is None):
            raise DispatchError("dispatch schema binding is incomplete")
        if bound_digest is not None and (
            not isinstance(bound_digest, str) or SHA_RE.fullmatch(bound_digest) is None
            or not isinstance(bound_identity, list) or len(bound_identity) != 5
            or any(type(item) is not int or item < 0 for item in bound_identity)
        ):
            raise DispatchError("dispatch schema binding is invalid")
    if value["attempt_origin"] not in {"initial", "conversation-resume", "fresh-restart", "conversation-continue"}:
        raise DispatchError("dispatch attempt origin is invalid")
    if type(value["attempt"]) is not int or value["attempt"] < 1:
        raise DispatchError("dispatch attempt is invalid")
    if value["workflow"] not in {"legacy", "explore", "task", "project"}:
        raise DispatchError("dispatch workflow state is invalid")
    if not _valid_max_cycles(value["workflow"], value["max_cycles"]):
        raise DispatchError("dispatch max cycles state is invalid")
    if type(value["cycle"]) is not int or value["cycle"] != value["attempt"] or (
        value["workflow"] != "legacy" and value["cycle"] > value["max_cycles"]
    ):
        raise DispatchError("dispatch cycle state is invalid")
    if not isinstance(value["job_id"], str) or JOB_RE.fullmatch(value["job_id"]) is None:
        raise DispatchError("dispatch job ID is invalid")
    conversation = value["conversation_id"]
    if conversation is not None and (
        not isinstance(conversation, str) or CONVERSATION_RE.fullmatch(conversation) is None
    ):
        raise DispatchError("dispatch conversation ID is invalid")
    for key in ("cancel_requested", "resume_available", "continue_available", "remote_cancel_unverified"):
        if type(value[key]) is not bool:
            raise DispatchError("dispatch boolean is invalid")
    for key in ("progress_count", "notice_count"):
        if type(value[key]) is not int or value[key] < 0:
            raise DispatchError("dispatch counter is invalid")
    for key in (
        "created_epoch", "updated_epoch", "elapsed_seconds", "hard_seconds",
        "max_seconds", "idle_seconds", "attempt_base_elapsed",
    ):
        if type(value[key]) not in (int, float) or value[key] < 0:
            raise DispatchError("dispatch time is invalid")
    for key in ("started_epoch", "finished_epoch", "last_progress_epoch"):
        if value[key] is not None and (type(value[key]) not in (int, float) or value[key] < 0):
            raise DispatchError("dispatch optional time is invalid")
    retry_after = value["provider_retry_after_seconds"]
    retry_observed = value["provider_retry_observed_epoch"]
    if (retry_after is None) != (retry_observed is None):
        raise DispatchError("dispatch provider retry binding is incomplete")
    if retry_after is not None and (
        type(retry_after) is not int or not (1 <= retry_after <= MAX_PROVIDER_RETRY_SECONDS)
        or type(retry_observed) not in (int, float)
        or not math.isfinite(retry_observed) or retry_observed < 0
    ):
        raise DispatchError("dispatch provider retry binding is invalid")
    if value["reason"] != "provider_quota_exhausted" and retry_after is not None:
        raise DispatchError("dispatch provider retry reason is inconsistent")
    for key in ("exit_code", "controller_pid", "agy_returncode"):
        if value[key] is not None and type(value[key]) is not int:
            raise DispatchError("dispatch integer is invalid")
    for key in ("workdir", "result_path", "stream_path", "stderr_path", "verification_path", "last_success_path"):
        if value[key] is not None and not isinstance(value[key], str):
            raise DispatchError("dispatch path is invalid")
    if value["limit_kind"] not in {None, "idle", "hard", "max-runtime"}:
        raise DispatchError("dispatch limit kind is invalid")
    for key in ("command_sha256", "stage_sha256", "result_sha256", "verification_sha256", "last_success_sha256"):
        if value[key] is not None and (
            not isinstance(value[key], str) or SHA_RE.fullmatch(value[key]) is None
        ):
            raise DispatchError("dispatch digest is invalid")
    for key in ("command_identity", "stage_identity", "result_identity", "verification_identity", "last_success_identity"):
        identity = value[key]
        if identity is not None and (
            not isinstance(identity, list) or len(identity) != 5
            or any(type(item) is not int or item < 0 for item in identity)
        ):
            raise DispatchError("dispatch identity is invalid")
    selection_sha = value["selection_sha256"]
    selection_identity = value["selection_identity"]
    if (selection_sha is None) != (selection_identity is None):
        raise DispatchError("dispatch selection state binding is incomplete")
    if selection_sha is not None and (
        not isinstance(selection_sha, str) or SHA_RE.fullmatch(selection_sha) is None
        or not isinstance(selection_identity, list) or len(selection_identity) != 5
        or any(type(item) is not int or item < 0 for item in selection_identity)
    ):
        raise DispatchError("dispatch selection state binding is invalid")
    scope_path = value.get("provider_scope_path")
    scope_sha = value.get("provider_scope_sha256")
    scope_identity = value.get("provider_scope_identity")
    approved_sha = value.get("approved_transmission_sha256")
    transmission_sha = value.get("transmission_sha256")
    selected_content_sha = value.get("selected_content_sha256")
    selected_file_count = value.get("selected_file_count")
    selected_tree_count = value.get("selected_tree_count")
    stage_path = value.get("provider_stage_path")
    stage_identity = value.get("provider_stage_identity")
    stage_manifest_sha = value.get("provider_stage_manifest_sha256")
    reconciliation_manifest_sha = value.get("reconciliation_manifest_sha256")
    if (scope_path is None) != (scope_sha is None) or (scope_path is None) != (scope_identity is None) or (scope_path is None) != (approved_sha is None) or (scope_path is None) != (transmission_sha is None) or (scope_path is None) != (selected_content_sha is None) or (scope_path is None) != (selected_file_count is None) or (scope_path is None) != (selected_tree_count is None):
        raise DispatchError("dispatch provider scope state fields are incomplete")
    stage_fields = (stage_path, stage_identity, stage_manifest_sha)
    if any(item is None for item in stage_fields) != all(item is None for item in stage_fields):
        raise DispatchError("dispatch provider stage state fields are incomplete")
    if scope_path is None and (
        any(item is not None for item in stage_fields)
        or reconciliation_manifest_sha is not None
    ):
        raise DispatchError("whole-worktree state cannot carry narrow provider evidence")
    if scope_path is not None:
        if (
            not isinstance(scope_path, str) or not Path(scope_path).is_absolute()
            or not isinstance(scope_sha, str) or SHA_RE.fullmatch(scope_sha) is None
            or not isinstance(scope_identity, list) or len(scope_identity) != 5
            or any(type(item) is not int or item < 0 for item in scope_identity)
            or not isinstance(approved_sha, str) or SHA_RE.fullmatch(approved_sha) is None
            or not isinstance(transmission_sha, str) or SHA_RE.fullmatch(transmission_sha) is None
            or not isinstance(selected_content_sha, str) or SHA_RE.fullmatch(selected_content_sha) is None
            or type(selected_file_count) is not int or selected_file_count < 0
            or type(selected_tree_count) is not int or selected_tree_count < 0
            or (stage_path is not None and (not isinstance(stage_path, str) or not Path(stage_path).is_absolute()))
            or (stage_identity is not None and (not isinstance(stage_identity, list) or len(stage_identity) != 5 or any(type(item) is not int or item < 0 for item in stage_identity)))
            or (stage_manifest_sha is not None and (not isinstance(stage_manifest_sha, str) or SHA_RE.fullmatch(stage_manifest_sha) is None))
            or (reconciliation_manifest_sha is not None and (not isinstance(reconciliation_manifest_sha, str) or SHA_RE.fullmatch(reconciliation_manifest_sha) is None))
        ):
            raise DispatchError("dispatch provider scope state fields are invalid")
    current_result = [value["result_path"], value["result_sha256"], value["result_identity"]]
    if any(item is None for item in current_result) != all(item is None for item in current_result):
        raise DispatchError("dispatch result binding is incomplete")
    if value["candidate_recognized"] != all(item is not None for item in current_result):
        raise DispatchError("dispatch candidate result binding is inconsistent")
    inaccessible_candidate = bool(
        value["candidate_recognized"] and not value["result_available"]
    )
    if value["candidate_recognized"] and value["failure_stage"] == "binding_failure" and value["result_available"]:
        raise DispatchError("dispatch binding failure cannot advertise a result")
    if inaccessible_candidate and not (
        value["failure_stage"] == "binding_failure"
        and value["status"] == "failed"
        and value["reason"] == "status_unavailable"
        and not value["resume_available"]
        and not value["continue_available"]
        and value["driver_disposition"] == "unreviewed"
        and value["next_action"] in {"blocked", "none"}
        and value["next_action_command"] is None
    ):
        raise DispatchError("dispatch inaccessible candidate state is inconsistent")
    if value["status"] in TERMINAL:
        if value["finished_epoch"] is None or value["exit_code"] is None:
            raise DispatchError("terminal dispatch state is incomplete")
    lifecycle_enabled = value["schema_version"] >= 5
    if lifecycle_enabled:
        if value["phase"] not in LIFECYCLE_PHASES:
            raise DispatchError("dispatch lifecycle phase is invalid")
        if value["assurance"] not in {"pending", "verified", "partially_verified", "rejected", "blocked"}:
            raise DispatchError("dispatch lifecycle assurance is invalid")
        if inaccessible_candidate and (
            value["phase"] != "blocked" or value["assurance"] != "blocked"
        ):
            raise DispatchError("dispatch inaccessible candidate lifecycle is invalid")
        if value["continue_available"] and not (
            value["assurance"] == "pending"
            and value["candidate_recognized"]
            and value["candidate_source"] != "provider_cancelled"
            and value["cycle"] < value["max_cycles"]
            and value["status"] in {"succeeded", "failed"}
            and value["phase"] in {"awaiting-verification", "repair-failed"}
        ):
            raise DispatchError("dispatch continuation availability is invalid")
        if value["assurance"] != "pending" and value["phase"] not in {"completed", "blocked"}:
            raise DispatchError("terminal dispatch assurance has an invalid phase")
        if value["status"] == "orphaned" and (
            value["assurance"] != "pending"
            or value["phase"] in {"completed", "blocked"}
            or value["resume_available"] or value["continue_available"]
        ):
            raise DispatchError("orphaned dispatch state must remain preserve-only")
        if value["workflow"] == "legacy":
            active = value["status"] in {"queued", "running", "cancel-requested"}
            if value["continue_available"]:
                raise DispatchError("legacy lifecycle cannot continue as repair")
            if active and (
                value["phase"] != "dispatching"
                or value["assurance"] != "pending"
                or value["driver_disposition"] != "not_applicable"
            ):
                raise DispatchError("active legacy lifecycle is invalid")
            if not active and inaccessible_candidate and (
                value["phase"] != "blocked" or value["assurance"] != "blocked"
            ):
                raise DispatchError("blocked legacy candidate lifecycle is invalid")
            if not active and value["candidate_recognized"] and not inaccessible_candidate and (
                value["phase"] != "awaiting-verification"
                or value["assurance"] != "pending"
                or value["driver_disposition"] != "unreviewed"
            ):
                raise DispatchError("legacy candidate lifecycle is invalid")
            if not active and not value["candidate_recognized"] and (
                value["phase"] != "attempt-failed" or value["assurance"] != "pending"
            ):
                raise DispatchError("failed legacy lifecycle is invalid")
    elif value["schema_version"] >= 5 and (value["phase"] is not None or value["assurance"] is not None or value["continue_available"]):
        raise DispatchError("legacy state has lifecycle status")
    elif value["schema_version"] < 5 and value["workflow"] == "project":
        if value["phase"] not in {
            "dispatching", "awaiting-verification", "repairing", "completed",
            "blocked", "provider-failed", "repair-failed",
        } or value["assurance"] not in {"pending", "verified", "partially_verified", "blocked"}:
            raise DispatchError("legacy project lifecycle state is invalid")
    elif value["schema_version"] < 5 and (
        value["phase"] is not None or value["assurance"] is not None or value["continue_available"]
    ):
        raise DispatchError("legacy non-project state has lifecycle status")
    summary = value["check_summary"]
    if summary is not None and (
        not isinstance(summary, str) or not (1 <= len(summary) <= MAX_CHECK_SUMMARY)
        or any(ch in summary for ch in "\x00\r\n")
    ):
        raise DispatchError("dispatch check summary is invalid")
    counts = value["check_counts"]
    if not isinstance(counts, dict) or set(counts) != {"passed", "failed", "advisory", "missing"} or any(
        type(item) is not int or not (0 <= item <= MAX_CHECK_ITEMS) for item in counts.values()
    ):
        raise DispatchError("dispatch check counts are invalid")
    present = [value["verification_path"], value["verification_sha256"], value["verification_identity"]]
    if any(item is None for item in present) != all(item is None for item in present):
        raise DispatchError("dispatch verification binding is incomplete")
    prior = [value["last_success_path"], value["last_success_sha256"], value["last_success_identity"]]
    if any(item is None for item in prior) != all(item is None for item in prior):
        raise DispatchError("dispatch prior result binding is incomplete")
    boundary = value["project_boundary"]
    if value["workflow"] == "project":
        if not isinstance(boundary, dict) or set(boundary) != {"kind", "identity", "sha256"}:
            raise DispatchError("project boundary binding is invalid")
        if boundary["kind"] != "file" or not isinstance(boundary["identity"], list) or len(boundary["identity"]) != 5:
            raise DispatchError("project boundary identity is invalid")
        if not isinstance(boundary["sha256"], str) or SHA_RE.fullmatch(boundary["sha256"]) is None:
            raise DispatchError("project boundary marker digest is invalid")
    elif boundary is not None:
        raise DispatchError("non-project state has a boundary binding")
    return value


def initial_state(
    command: dict[str, Any], origin: str, attempt: int, *, command_sha: str,
    command_identity: tuple[int, int, int, int, int], stage_sha: str | None,
    stage_identity: tuple[int, int, int, int, int] | None,
    project_boundary: dict[str, Any] | None = None,
    schema_bindings: dict[str, Any] | None = None,
    state_schema: int = CURRENT_STATE_SCHEMA,
    explain_worktree_rejection: bool = False,
) -> dict[str, Any]:
    if state_schema not in {6, 7, 8, 9, 10, CURRENT_STATE_SCHEMA}:
        raise DispatchError("dispatch state schema is invalid")
    now = time.time()
    workflow = command.get("workflow", "legacy")
    max_cycles = command.get("max_cycles", 1)
    try:
        worktree_baseline = _worktree_snapshot(
            command["workdir"], legacy=state_schema == 6, explain_unsupported=explain_worktree_rejection)
    except ResolveUndoPresentError:
        worktree_baseline = None
    state = {
        "schema_version": state_schema,
        "kind": "agy-worker-dispatch-state",
        "sequence": 1,
        "previous_state_sha256": None,
        "job_id": command["job_id"],
        "status": "queued",
        "attempt": attempt,
        "attempt_origin": origin,
        "reason": None,
        "exit_code": None,
        "controller_pid": None,
        "workdir": command["workdir"],
        "created_epoch": now,
        "started_epoch": None,
        "updated_epoch": now,
        "finished_epoch": None,
        "elapsed_seconds": 0.0,
        "progress_count": 0,
        "last_progress_epoch": None,
        "notice_count": 0,
        "hard_seconds": float(command["hard_seconds"]),
        "max_seconds": float(command["max_seconds"]),
        "idle_seconds": float(command["idle_seconds"]),
        "attempt_base_elapsed": 0.0,
        "cancel_requested": False,
        "conversation_id": None,
        "resume_available": False,
        "remote_cancel_unverified": False,
        "result_path": None,
        "stream_path": None,
        "stderr_path": None,
        "agy_returncode": None,
        "limit_kind": None,
        "command_sha256": command_sha,
        "command_identity": list(command_identity),
        "stage_sha256": stage_sha,
        "stage_identity": None if stage_identity is None else list(stage_identity),
        "result_sha256": None,
        "result_identity": None,
        "workflow": workflow,
        "max_cycles": max_cycles,
        "cycle": attempt,
        "phase": "dispatching",
        "assurance": "pending",
        "check_summary": None,
        "check_counts": {"passed": 0, "failed": 0, "advisory": 0, "missing": 0},
        "verification_path": None,
        "verification_sha256": None,
        "verification_identity": None,
        "continue_available": False,
        "last_success_path": None,
        "last_success_sha256": None,
        "last_success_identity": None,
        "project_boundary": (
            project_boundary if project_boundary is not None
            else _project_boundary(command["workdir"]) if workflow == "project"
            else None
        ),
        "provider_retry_after_seconds": None,
        "provider_retry_observed_epoch": None,
        "candidate_recognized": False,
        "candidate_source": "none",
        "result_available": False,
        "worktree_reconciliation": "not_applicable",
        "worktree_changes_present": None,
        "worktree_changed_since_dispatch": None,
        "driver_disposition": "not_applicable",
        "failure_stage": None,
        "last_activity": None,
        # Deprecated v5 storage only.  V7 never writes a semantic controller
        # recommendation; public aliases are derived at read time.
        "next_action": "none",
        "next_action_command": None,
        "worktree_baseline": worktree_baseline,
        "provider_schema_sha256": None if schema_bindings is None else schema_bindings["provider_schema_sha256"],
        "provider_schema_identity": None if schema_bindings is None else schema_bindings["provider_schema_identity"],
        "canonical_schema_sha256": None if schema_bindings is None else schema_bindings["canonical_schema_sha256"],
        "canonical_schema_identity": None if schema_bindings is None else schema_bindings["canonical_schema_identity"],
        "candidate_worktree_sha256": None,
        "candidate_worktree_entries": None,
        "selection_sha256": command.get("selection_sha256"),
        "selection_identity": command.get("selection_identity"),
    }
    if state_schema >= 8:
        state["worktree_snapshot_algorithm"] = CURRENT_WORKTREE_SNAPSHOT_ALGORITHM
    if state_schema >= 9:
        root_identity = _dispatch_root_identity(command["workdir"])
        if root_identity is None:
            raise DispatchError("dispatch worktree root cannot be bound")
        state["worktree_root_identity"] = root_identity
    if state_schema >= 10:
        state["provider_terminal_status"] = "unknown"
    if state_schema == CURRENT_STATE_SCHEMA:
        if command.get("provider_scope_path") is not None:
            scope_path = Path(command["provider_scope_path"])
            raw_scope, scope_info = read_regular(scope_path, MAX_COMMAND_BYTES, "provider scope")
            if digest(raw_scope) != command["provider_scope_sha256"]:
                raise DispatchError("provider scope file changed since dispatch")
            if list(_identity(scope_info)) != command["provider_scope_identity"]:
                raise DispatchError("provider scope file identity changed since dispatch")
            try:
                scope = _parse_provider_scope(raw_scope)
            except ValueError as exc:
                raise DispatchError(f"invalid provider scope: {exc}") from exc
            readable_manifest = _scan_readable_worktree(command["workdir"])
            manifest_sha = _manifest_digest(readable_manifest)
            _validate_scope_against_worktree(scope, command["workdir"], readable_manifest)
            selected_manifest = _build_selected_content_manifest(command["workdir"], scope)
            selected_sha = _selected_content_digest(selected_manifest)
            policy_sha = _canonical_digest(scope)
            transmission_sha = _compute_transmission_sha256(policy_sha, manifest_sha, selected_sha)
            if transmission_sha != command["approved_transmission_sha256"]:
                raise DispatchError("approved transmission SHA does not match current worktree scope")
            state.update({
                "provider_scope_path": command["provider_scope_path"],
                "provider_scope_sha256": command["provider_scope_sha256"],
                "provider_scope_identity": command["provider_scope_identity"],
                "approved_transmission_sha256": command["approved_transmission_sha256"],
                "transmission_sha256": transmission_sha,
                "selected_content_sha256": selected_sha,
                "selected_file_count": sum(1 for e in selected_manifest if e["kind"] == "file"),
                "selected_tree_count": sum(1 for e in selected_manifest if e["kind"] == "directory"),
                "provider_stage_path": None,
                "provider_stage_identity": None,
                "provider_stage_manifest_sha256": None,
                "reconciliation_manifest_sha256": None,
            })
        else:
            state.update({
                "provider_scope_path": None,
                "provider_scope_sha256": None,
                "provider_scope_identity": None,
                "approved_transmission_sha256": None,
                "transmission_sha256": None,
                "selected_content_sha256": None,
                "selected_file_count": None,
                "selected_tree_count": None,
                "provider_stage_path": None,
                "provider_stage_identity": None,
                "provider_stage_manifest_sha256": None,
                "reconciliation_manifest_sha256": None,
            })
    return state


def _upgrade_legacy_state(
    state: dict[str, Any], command: dict[str, Any], *,
    migration_facts: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Prepare an eligible pre-V11 state for one atomic approved current write."""
    if state["schema_version"] >= CURRENT_STATE_SCHEMA:
        return state
    if state["schema_version"] == 1:
        # V1 has neither a lifecycle nor a bounded current-candidate contract.
        # It remains readable evidence only; do not invent task/project authority.
        raise DispatchError("legacy dispatch state has no migration authority")
    if state["schema_version"] in {3, 4} and migration_facts is None:
        # V3/V4 may be migrated only by the separate, state-SHA-approved
        # no-write proof below.  Never promote a path observation implicitly.
        raise DispatchError("legacy migration approval is required")
    value = dict(state)
    if value["phase"] == "provider-failed":
        value["phase"] = "attempt-failed"
    if value["workflow"] == "legacy":
        if value["candidate_recognized"]:
            value["phase"] = "awaiting-verification"
        elif value["status"] in TERMINAL:
            value["phase"] = "attempt-failed"
        else:
            value["phase"] = "dispatching"
        value["assurance"] = "pending"
    else:
        if value["attempt_origin"] == "conversation-continue" and value["status"] == "failed":
            value["phase"] = "repair-failed"
        elif value["candidate_recognized"]:
            value["phase"] = "awaiting-verification"
        elif value["status"] == "failed":
            value["phase"] = "attempt-failed"
        elif value["phase"] is None:
            value["phase"] = "dispatching"
        if value["assurance"] is None:
            value["assurance"] = "pending"
    # Pre-V9 state has no separate root identity.  Its persisted snapshot can
    # prove the old state once; it cannot become the new V9 baseline.  V5/V6
    # use their frozen legacy digest only for that proof, then capture a fresh
    # semantic-v1 observation in this same pending transition.  V7/V8 already
    # use semantic-v1, so their exact proved observation is safe to reuse.
    if value["schema_version"] in {3, 4}:
        assert migration_facts is not None
        snapshot = migration_facts["semantic_snapshot"]
        root_identity = migration_facts["root_identity"]
    elif value["schema_version"] == 9:
        persisted_root = value.get("worktree_root_identity")
        current_root = _dispatch_root_identity(command["workdir"])
        boundary = _git_boundary_identity(command["workdir"])
        if (
            persisted_root is None
            or current_root is None
            or persisted_root != current_root
            or persisted_root != boundary
        ):
            raise DispatchError("legacy dispatch root identity cannot be proved")
        expected_schemas = _schema_bindings(command)
        for key, val in expected_schemas.items():
            if value.get(key) != val:
                raise DispatchError("dispatch schema binding changed")
        if (
            value.get("selection_sha256") != command.get("selection_sha256")
            or value.get("selection_identity") != command.get("selection_identity")
        ):
            raise DispatchError("dispatch selection binding changed")
        expected = value.get("candidate_worktree_sha256") if value["candidate_recognized"] else None
        expected_entries = value.get("candidate_worktree_entries") if value["candidate_recognized"] else None
        if expected is None:
            baseline = value.get("worktree_baseline")
            if isinstance(baseline, dict):
                expected, expected_entries = baseline.get("sha256"), baseline.get("entries")
        observed = _state_worktree_snapshot(value, command["workdir"])
        if (
            observed is None or not isinstance(expected, str) or type(expected_entries) is not int
            or observed["sha256"] != expected or observed["entries"] != expected_entries
        ):
            raise DispatchError("legacy dispatch root identity cannot be proved")
        root_identity = persisted_root
        snapshot = observed
    else:
        expected = value.get("candidate_worktree_sha256") if value["candidate_recognized"] else None
        expected_entries = value.get("candidate_worktree_entries") if value["candidate_recognized"] else None
        if expected is None:
            baseline = value.get("worktree_baseline")
            if isinstance(baseline, dict):
                expected, expected_entries = baseline.get("sha256"), baseline.get("entries")
        observed = _state_worktree_snapshot(value, command["workdir"])
        if (
            observed is None or not isinstance(expected, str) or type(expected_entries) is not int
            or observed["sha256"] != expected or observed["entries"] != expected_entries
        ):
            raise DispatchError("legacy dispatch root identity cannot be proved")
        root_identity = _dispatch_root_identity(command["workdir"])
        if root_identity is None:
            raise DispatchError("legacy dispatch root identity cannot be proved")
        snapshot = _worktree_snapshot(command["workdir"]) if value["schema_version"] in {5, 6} else observed
    if snapshot is None:
        raise DispatchError("legacy worktree cannot be bound")
    value.update(_schema_bindings(command))
    value.update({
        "schema_version": CURRENT_STATE_SCHEMA,
        "worktree_snapshot_algorithm": CURRENT_WORKTREE_SNAPSHOT_ALGORITHM,
        "worktree_baseline": snapshot,
        "worktree_reconciliation": "available",
        "worktree_changes_present": snapshot["entries"] > 0,
        "worktree_changed_since_dispatch": False,
        "resume_available": bool(
            value["conversation_id"] and not value["candidate_recognized"]
            and value["status"] == "failed"
        ),
        "selection_sha256": command.get("selection_sha256"),
        "selection_identity": command.get("selection_identity"),
        "worktree_root_identity": root_identity,
        "provider_terminal_status": "unknown",
        "provider_scope_path": None,
        "provider_scope_sha256": None,
        "provider_scope_identity": None,
        "approved_transmission_sha256": None,
        "transmission_sha256": None,
        "selected_content_sha256": None,
        "selected_file_count": None,
        "selected_tree_count": None,
        "provider_stage_path": None,
        "provider_stage_identity": None,
        "provider_stage_manifest_sha256": None,
        "reconciliation_manifest_sha256": None,
    })
    if value["candidate_recognized"]:
        value["candidate_worktree_sha256"] = snapshot["sha256"]
        value["candidate_worktree_entries"] = snapshot["entries"]
        value["driver_disposition"] = "unreviewed"
    value["continue_available"] = bool(
        value["workflow"] != "legacy"
        and value["candidate_recognized"]
        and value["candidate_source"] != "provider_cancelled"
        and value["conversation_id"]
        and value["status"] in {"succeeded", "failed"}
        and value["phase"] in {"awaiting-verification", "repair-failed"}
        and value["attempt"] < value["max_cycles"]
        and float(value["elapsed_seconds"]) < float(value["max_seconds"])
    )
    # V3/V4's raw lifecycle fields were private compatibility data, never
    # evidence of a current controller phase or completed driver decision.
    value["assurance"] = "pending"
    value["next_action"] = "none"
    value["next_action_command"] = None
    value["phase"] = _controller_phase(value) or "attempt-failed"
    validate_state(value)
    return value


def _legacy_migration_facts(
    job: Path, state: dict[str, Any], state_sha: str,
) -> dict[str, Any]:
    """Prove a V3/V4 transition without giving a pathname lasting authority.

    The returned private facts are deliberately recomputed for status and again
    while holding the transition lock.  Their digest is an approval capability,
    not a claim that a legacy result was provider-successful or driver-verified.
    """
    if state["schema_version"] not in {3, 4}:
        raise DispatchError("legacy migration is unavailable")
    if _legacy_prior_result_is_unknown(state):
        raise DispatchError("unknown legacy result has no migration authority")
    command = _load_bound_command(job, state, stage_readonly=False)
    if _job_is_inside_worktree(job, command["workdir"]):
        raise DispatchError("legacy migration is unavailable for jobs inside the worktree")
    command, checked = _bound_lifecycle_inputs(job, state, command, read_legacy=True)
    selection = _load_bound_selection(command, checked, legacy_command_binding=True)
    schema_bindings = _schema_bindings(command)
    root_identity = _dispatch_root_identity(command["workdir"])
    snapshot = _worktree_snapshot(command["workdir"])
    if root_identity is None or snapshot is None:
        raise DispatchError("legacy dispatch root identity cannot be proved")
    artifact: dict[str, Any] | None = None
    if checked["candidate_recognized"]:
        _bound_current_candidate(job, checked)
        artifact = {
            "sha256": checked["result_sha256"],
            "identity": checked["result_identity"],
            "source": checked["candidate_source"],
        }
    facts = {
        "kind": "agy-worker-legacy-migration-v1",
        "state_sha256": state_sha,
        "legacy_schema_version": checked["schema_version"],
        "command_sha256": checked["command_sha256"],
        "command_identity": checked["command_identity"],
        "stage_sha256": checked["stage_sha256"],
        "stage_identity": checked["stage_identity"],
        "selection": {
            "sha256": command.get("selection_sha256"),
            "identity": command.get("selection_identity"),
            "schema_version": None if selection is None else selection.get("schema_version"),
        },
        "schemas": schema_bindings,
        "root_identity": root_identity,
        "semantic_snapshot": snapshot,
        "project_boundary": checked["project_boundary"],
        "workflow": checked["workflow"],
        "attempt_origin": checked["attempt_origin"],
        "status": checked["status"],
        "candidate": artifact,
        "provider_launch_authorized": _selection_launch_is_authorized(selection),
        "historical_result_provenance": (
            "unknown_bound_legacy" if _legacy_prior_result_is_unknown(checked) else None
        ),
    }
    return facts


def _legacy_migration_sha(job: Path | None, state: dict[str, Any], state_sha: str) -> str | None:
    """Return an exact, public-safe V3/V4 transition approval digest."""
    if job is None or state["schema_version"] not in {3, 4}:
        return None
    try:
        return digest(canonical(_legacy_migration_facts(job, state, state_sha)))
    except (OSError, DispatchError):
        return None


def _approved_legacy_migration(
    job: Path, state: dict[str, Any], raw: bytes, approve_migration_sha: str | None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Recompute an approved V3/V4 proof immediately before its first write."""
    if state["schema_version"] not in {3, 4}:
        command = _load_bound_command(job, state, stage_readonly=False)
        return command, state
    if not isinstance(approve_migration_sha, str) or SHA_RE.fullmatch(approve_migration_sha) is None:
        raise DispatchError("legacy migration approval is missing or invalid")
    state_sha = digest(raw)
    facts = _legacy_migration_facts(job, state, state_sha)
    if digest(canonical(facts)) != approve_migration_sha:
        raise DispatchError("legacy migration approval is stale")
    command = _load_bound_command(job, state, stage_readonly=False)
    return command, _upgrade_legacy_state(state, command, migration_facts=facts)


def _transition_locked(
    job: Path, state: dict[str, Any], prior_raw: bytes, updates: dict[str, Any], *,
    legacy_control_only: bool = False,
) -> tuple[dict[str, Any], bytes, str]:
    current, _info = read_regular(job / STATE_NAME, MAX_STATE_BYTES, "dispatch state")
    if current != prior_raw:
        raise DispatchError("dispatch state changed before transition")
    value = dict(state)
    value.update(updates)
    if value["schema_version"] < CURRENT_STATE_SCHEMA and not legacy_control_only:
        command = _load_bound_command(job, state, stage_readonly=False)
        value = _upgrade_legacy_state(value, command)
    elif legacy_control_only:
        # ``validate_state`` projects additive facts while reading old bytes.
        # A cheap active control must write the old generation's exact field
        # shape back, not accidentally persist a partial migration.
        omitted = set(STATE_V11_FIELDS)
        if value["schema_version"] < 10:
            omitted |= set(STATE_V10_FIELDS)
        if value["schema_version"] < 9:
            omitted |= set(STATE_V9_FIELDS)
        if value["schema_version"] < 8:
            omitted |= set(STATE_V8_FIELDS)
        if value["schema_version"] < 6:
            omitted |= set(STATE_V6_FIELDS)
        if value["schema_version"] < 5:
            omitted |= set(STATE_V5_FIELDS)
        if value["schema_version"] == 1:
            omitted |= set(STATE_PROJECT_FIELDS) | {
                "provider_retry_after_seconds", "provider_retry_observed_epoch",
            }
        elif value["schema_version"] == 3:
            omitted |= {"provider_retry_after_seconds", "provider_retry_observed_epoch"}
        for key in omitted:
            value.pop(key, None)
    # New V7+ writes retain these only for private legacy read compatibility.
    # A control-only legacy transition preserves its original field shape.
    if not legacy_control_only:
        value["next_action"] = "none"
        value["next_action_command"] = None
    value["sequence"] = state["sequence"] + 1
    value["previous_state_sha256"] = digest(prior_raw)
    value["updated_epoch"] = time.time()
    validate_state(value)
    raw, sha = write_atomic(job, STATE_NAME, value)
    # Return the same additive read projection that ordinary callers receive;
    # control-only V1/V3/V4 writes intentionally used their historical storage
    # shape above and must still be safe for the public status formatter.
    return validate_state(value), raw, sha


def transition(job: Path, state: dict[str, Any], prior_raw: bytes, updates: dict[str, Any]) -> tuple[dict[str, Any], bytes, str]:
    with state_lock(job):
        return _transition_locked(job, state, prior_raw, updates)


def _live_elapsed(value: dict[str, Any], now: float) -> float:
    elapsed = float(value["elapsed_seconds"])
    if value["status"] in {"running", "cancel-requested"} and value["started_epoch"] is not None:
        elapsed = max(
            elapsed,
            float(value["attempt_base_elapsed"]) + max(0.0, now - float(value["started_epoch"])),
        )
    return elapsed


def _freeze_reaped_runtime(
    job: Path, attempt: int, controller_pid: int, elapsed: float,
) -> tuple[dict[str, Any], bytes, str, str | None]:
    """Atomically stop the provider clock and classify its locked deadline.

    Reaping is the last provider-owned operation.  Everything after this
    point—envelope extraction, schema validation, and candidate worktree
    reconciliation—must observe the exact persisted value rather than accrue
    controller-local time.  Reload under the lock instead of applying a stale
    controller snapshot so a just-approved extension is included, while a
    prior freeze makes the same extension predicate ineligible.
    """
    with state_lock(job):
        current, raw, _sha = load_state(job)
        if (
            current["attempt"] != attempt
            or current["controller_pid"] != controller_pid
            or current["status"] not in {"running", "cancel-requested"}
        ):
            raise DispatchError("dispatch changed before runtime freeze")
        frozen_elapsed = max(float(elapsed), float(current["elapsed_seconds"]))
        current, raw, sha = _transition_locked(job, current, raw, {
            "elapsed_seconds": frozen_elapsed,
            "started_epoch": None,
        })
        deadline: str | None = None
        # Cancellation is an approved state fact and has priority over a
        # post-reap deadline classification.  The terminal projection still
        # handles it with the existing remote-cancel semantics.
        if not current["cancel_requested"]:
            if frozen_elapsed >= float(current["max_seconds"]):
                deadline = "max-runtime"
            elif frozen_elapsed >= float(current["hard_seconds"]):
                deadline = "hard"
        return current, raw, sha, deadline


def _is_active(value: dict[str, Any]) -> bool:
    return value["status"] in {"queued", "running", "cancel-requested"}


def _extend_is_eligible(value: dict[str, Any], now: float) -> bool:
    """One cheap state/time predicate shared by status and the lock guard."""
    elapsed = _live_elapsed(value, now)
    return bool(
        _is_active(value)
        # The lease is a provider-runtime control, never a way to extend
        # queued preflight or post-reap controller reconciliation.
        and value["started_epoch"] is not None
        and not value["cancel_requested"]
        and value["progress_count"] > 0
        and value["last_progress_epoch"] is not None
        and now - float(value["last_progress_epoch"]) < float(value["idle_seconds"])
        # ``--by`` has one-second precision.  Advertising extend with less
        # than one second before either limit would name an operation the lock
        # guard must reject.
        and elapsed + 1.0 <= float(value["hard_seconds"])
        and float(value["hard_seconds"]) + 1.0 <= float(value["max_seconds"])
    )


def _legacy_prior_result_is_unknown(value: dict[str, Any]) -> bool:
    """Recognize only the historical V3/V4 last-success pointer as unknown."""
    return bool(
        value["schema_version"] in {3, 4}
        and value["result_path"] is None
        and all(value[key] is not None for key in (
            "last_success_path", "last_success_sha256", "last_success_identity",
        ))
    )


def _resume_is_eligible(value: dict[str, Any], now: float) -> bool:
    """Mirror the strict same-conversation resume guard used before staging."""
    return bool(
        value["status"] == "failed"
        and not value["candidate_recognized"]
        and value["resume_available"]
        and isinstance(value["conversation_id"], str)
        and _restart_guard_accepts(value, elapsed_seconds=_live_elapsed(value, now))
    )


def _continue_is_eligible(value: dict[str, Any], now: float) -> bool:
    """Return the state-only half of the exact continuation guard."""
    return bool(
        value["workflow"] != "legacy"
        # A failed final direct-selection proof invalidates provider launch
        # authority for this frozen job.  Keep its bound candidate available
        # for result review/finalization, but never reuse the selection through
        # another same-conversation continuation.
        and value["reason"] != "selection_preflight_failed"
        and value["continue_available"]
        and value["candidate_recognized"]
        and value["result_available"]
        and value["candidate_source"] != "provider_cancelled"
        and value["status"] in {"succeeded", "failed"}
        and _controller_phase(value) in {"awaiting-verification", "repair-failed"}
        and isinstance(value["conversation_id"], str)
        and value["cycle"] < value["max_cycles"]
        and _live_elapsed(value, now) < float(value["max_seconds"])
    )


def _finalize_is_eligible(value: dict[str, Any]) -> bool:
    """Return the state-only half of the exact finalization guard."""
    return bool(
        value["candidate_recognized"] and value["result_available"]
        and value["result_path"] and value["workflow"] != "legacy"
        and value["driver_disposition"] == "unreviewed"
        and (value["assurance"] == "pending" or value["schema_version"] in {3, 4})
        and _controller_phase(value) in {"awaiting-verification", "repair-failed"}
    )


def _verification_copy_is_eligible(value: dict[str, Any]) -> bool:
    """Return the exact state predicate for the non-migrating copy helper.

    A V3/V4 finalization can first obtain an explicit migration capability, but
    ``verification-copy`` deliberately accepts no migration approval.  Keep it
    current-state-only so status never advertises a command the helper rejects.
    """
    return bool(
        value["schema_version"] >= 9
        and _finalize_is_eligible(value)
    )


def _controller_phase(value: dict[str, Any]) -> str | None:
    """Project controller-owned mechanics without trusting legacy raw phase."""
    if value["schema_version"] in {3, 4} and _legacy_prior_result_is_unknown(value):
        return None
    if value["driver_disposition"] in {"verified", "partially_verified", "rejected"}:
        return "completed"
    if value["driver_disposition"] == "blocked" or (
        value["candidate_recognized"] and not value["result_available"]
    ):
        return "blocked"
    if _is_active(value):
        return "repairing" if value["attempt_origin"] == "conversation-continue" else "dispatching"
    if value["candidate_recognized"]:
        if value["status"] == "failed" and value["attempt_origin"] == "conversation-continue":
            return "repair-failed"
        return "awaiting-verification"
    if value["status"] in TERMINAL:
        return "repair-failed" if value["attempt_origin"] == "conversation-continue" else "attempt-failed"
    return None


def _candidate_actions_are_bound(job: Path | None, value: dict[str, Any]) -> bool:
    """Keep public candidate actions as strict as their mutating commands."""
    if job is None:
        return False
    try:
        _bound_current_candidate(job, value)
    except (OSError, DispatchError):
        return False
    return True


def _post_candidate_selection_binding_drift(job: Path | None, value: dict[str, Any]) -> bool:
    """Identify a frozen direct-selection failure without publishing its bytes.

    The candidate action binder uses the same selection record, but can also
    reject a result/schema/worktree drift. Text recovery guidance must only
    name a fresh-job handoff for selection drift, so bind the command first and
    then probe its selection record in isolation.
    """
    if job is None or not (
        value["candidate_recognized"] and value["result_available"]
    ):
        return False
    try:
        bound_job = canonical_job(Path(job).resolve(strict=True))
        command = _load_bound_command(bound_job, value, stage_readonly=False)
    except (OSError, DispatchError):
        return False
    if command.get("selection_path") is None:
        return False
    try:
        _load_bound_selection(command, value)
    except (OSError, DispatchError):
        return True
    return False


def _lifecycle_mutation_bindings(
    job: Path | None, value: dict[str, Any],
) -> tuple[bool, bool]:
    """Return driver-write and provider-launch binding availability.

    Finalization records an exact driver decision without launching a provider.
    Recovery actions additionally require a selection record that is current
    launch authority.  Keep those facts separate so status advertises exactly
    the operations their command guards accept.
    """
    if job is None:
        return False, False
    try:
        bound_job = canonical_job(Path(job).resolve(strict=True))
        command = _load_bound_command(bound_job, value, stage_readonly=False)
        _bound_lifecycle_inputs(bound_job, value, command)
        provider_launch_bound = (
            not _job_is_inside_worktree(bound_job, command["workdir"])
            and _selection_launch_is_authorized(
                _load_bound_selection(command, value)
            )
        )
    except (OSError, DispatchError):
        return False, False
    return True, provider_launch_bound


def _selection_launch_is_authorized(record: dict[str, Any] | None) -> bool:
    """Allow exact-match V2 or explicitly approved V3 direct provenance."""
    if record is None or record.get("selection_mode") not in {
        "exact-model", "model-effort",
    }:
        return True
    if not MODEL_SELECTION.has_current_probed_executable_binding(record.get("probed_executable")):
        return False
    if record.get("schema_version") == 3:
        return True
    return (
        record.get("schema_version") == 2
        and record.get("version_relation") == "match"
        and record.get("compatibility_status") == "reviewed-version-match"
    )


def _legacy_result_action_is_bound(job: Path | None, value: dict[str, Any]) -> bool:
    """Probe an unknown-provenance legacy result with its command guard."""
    if job is None:
        return False
    try:
        _bound_legacy_unknown_result(job, value)
    except (OSError, DispatchError):
        return False
    return True


def _available_actions(
    value: dict[str, Any], sha: str, now: float, *, job: Path | None = None,
    candidate_bound: bool | None = None, legacy_result_bound: bool | None = None,
    lifecycle_mutation_bound: bool | None = None,
    provider_launch_bound: bool | None = None,
    legacy_migration_sha: str | None = None,
) -> list[dict[str, Any]]:
    """Return only state/time-applicable mechanical controller operations.

    Cancel and extend remain cheap state/time controls.  A terminal candidate is
    revalidated only when it could make a result, continue, or finalize action
    visible, and uses the same binder the command paths require.
    """
    job_id = value["job_id"]
    actions: list[dict[str, Any]] = []
    active = _is_active(value)
    if active:
        actions.append({
            "action": "wait",
            "command": f"{PUBLIC_LAUNCHER} wait --job-id {job_id} --after-state-sha {sha} --format text",
        })
    if active and not value["cancel_requested"]:
        actions.append({
            "action": "cancel",
            "command": f"{PUBLIC_LAUNCHER} cancel --job-id {job_id} --approve-state-sha {sha}",
        })
    # A terminal report with an unavailable candidate worktree is forensic
    # state only.  It must not be presented as a route to another provider
    # action, result delivery, continuation, or finalization.
    if (
        not active and value["status"] in TERMINAL
        and value["candidate_recognized"] and not value["result_available"]
        and value["worktree_reconciliation"] == "unavailable"
    ):
        return actions
    if _extend_is_eligible(value, now):
        # The state cannot choose a duration on the caller's behalf.  Keep
        # this guidance deliberately commandless: a copied command with a
        # made-up duration would not share the mutation guard's contract.
        actions.append({
            "action": "extend",
            "requires": ["--by caller-provided DURATION"],
            "guidance": "choose a positive duration that remains within the current maximum runtime",
        })
    terminal_candidate = bool(
        not active and value["status"] in TERMINAL
        and value["candidate_recognized"] and value["result_available"]
    )
    if terminal_candidate and candidate_bound is None:
        candidate_bound = _candidate_actions_are_bound(job, value)
    if terminal_candidate and candidate_bound:
        actions.append({
            "action": "result",
            "command": f"{PUBLIC_LAUNCHER} result --job-id {job_id} --format json",
        })
        if (
            _verification_copy_is_eligible(value)
            and job is not None
            and not _job_is_inside_worktree(job, value["workdir"])
        ):
            actions.append({
                "action": "verification-copy",
                "command": (
                    f"{PUBLIC_LAUNCHER} verification-copy --job-id {job_id} "
                    "--destination NEW_PRIVATE_DIRECTORY --format text"
                ),
                "requires": ["new owner-private destination outside the candidate"],
            })
    elif (
        not active and value["status"] in TERMINAL
        and _legacy_prior_result_is_unknown(value) and legacy_result_bound
    ):
        actions.append({
            "action": "result",
            "command": f"{PUBLIC_LAUNCHER} result --job-id {job_id} --format json",
        })
    # A public recovery operation is useful only when the same frozen command,
    # schemas, worktree root/boundary, and selector the command will use are
    # still present.  ``None`` keeps pure in-memory compatibility callers from
    # claiming a failed local probe; CLI status always supplies a concrete bool.
    # V1 remains result-only.  V3/V4 may advertise a lifecycle action only
    # with a fresh public migration digest which the command recomputes under
    # its transition lock.  V5-V8 retain their existing migration proof.
    lifecycle_mutation_available = bool(
        (value["schema_version"] >= 5 and lifecycle_mutation_bound is not False)
        or (value["schema_version"] in {3, 4} and legacy_migration_sha is not None)
    )
    provider_mutation_available = bool(
        lifecycle_mutation_available and provider_launch_bound is not False
    )
    if _resume_is_eligible(value, now) and provider_mutation_available:
        actions.append({
            "action": "resume",
            "command": (
                f"{PUBLIC_LAUNCHER} resume --job-id {job_id} --approve-state-sha {sha}"
                + (f" --approve-migration-sha {legacy_migration_sha}" if value["schema_version"] in {3, 4} else "")
                + " --format text"
            ),
        })
    if (
        _restart_guard_accepts(value, elapsed_seconds=_live_elapsed(value, now))
        and provider_mutation_available
    ):
        actions.append({
            "action": "restart",
            "command": (
                f"{PUBLIC_LAUNCHER} restart --job-id {job_id} --approve-state-sha {sha}"
                + (f" --approve-migration-sha {legacy_migration_sha}" if value["schema_version"] in {3, 4} else "")
                + " --format text"
            ),
        })
    if (
        terminal_candidate and candidate_bound and _continue_is_eligible(value, now)
        and provider_mutation_available
    ):
        actions.append({
            "action": "continue",
            "command": (
                f"{PUBLIC_LAUNCHER} continue --job-id {job_id} --approve-state-sha {sha} "
                + (f"--approve-migration-sha {legacy_migration_sha} " if value["schema_version"] in {3, 4} else "")
                + "< DRIVER_VERIFICATION_JSON"
            ),
            "requires": ["verification JSON"],
        })
    if (
        terminal_candidate and candidate_bound and _finalize_is_eligible(value)
        and lifecycle_mutation_available
    ):
        actions.append({
            "action": "finalize",
            "command": (
                f"{PUBLIC_LAUNCHER} finalize --job-id {job_id} --approve-state-sha {sha} "
                + (f"--approve-migration-sha {legacy_migration_sha} " if value["schema_version"] in {3, 4} else "")
                + "--assurance ASSURANCE < DRIVER_VERIFICATION_JSON"
            ),
            "requires": ["--assurance", "verification JSON"],
        })
    return actions


def _public_next_action(actions: list[dict[str, Any]]) -> tuple[str, str | None]:
    if not actions:
        return "none", None
    # `resume` and `restart` are distinct caller-owned recovery policies.  The
    # deprecated scalar alias must not turn their deterministic display order
    # into a controller recommendation.
    if {"resume", "restart"} <= {str(item.get("action")) for item in actions}:
        return "none", None
    first = actions[0]
    return str(first["action"]), first.get("command") if isinstance(first.get("command"), str) else None


def public_status(value: dict[str, Any], sha: str, *, job: Path | None = None) -> dict[str, Any]:
    now = time.time()
    elapsed = _live_elapsed(value, now)
    last_age = None
    if value["last_progress_epoch"] is not None:
        last_age = max(0.0, now - value["last_progress_epoch"])
    retry_remaining = None
    if value["provider_retry_after_seconds"] is not None:
        retry_remaining = max(
            0,
            int(math.ceil(
                value["provider_retry_after_seconds"]
                - max(0.0, now - value["provider_retry_observed_epoch"])
            )),
        )
    candidate_bound: bool | None = None
    legacy_result_bound: bool | None = None
    lifecycle_mutation_bound: bool | None = None
    provider_launch_bound: bool | None = None
    legacy_migration_sha: str | None = None
    terminal_candidate = bool(
        not _is_active(value) and value["status"] in TERMINAL
        and value["candidate_recognized"] and value["result_available"]
    )
    if terminal_candidate:
        candidate_bound = _candidate_actions_are_bound(job, value)
        # Candidate reconciliation can take meaningful bounded time.  Resample
        # the clocks so an extension that expired during that scan is omitted.
        now = time.time()
        elapsed = _live_elapsed(value, now)
    elif (
        job is not None and not _is_active(value) and value["status"] in TERMINAL
        and _legacy_prior_result_is_unknown(value)
    ):
        legacy_result_bound = _legacy_result_action_is_bound(job, value)
        # Legacy reconciliation is also a bounded terminal scan.  Do not let
        # its duration publish stale elapsed-time action eligibility.
        now = time.time()
        elapsed = _live_elapsed(value, now)
    if (
        job is not None and not _is_active(value) and value["schema_version"] in {3, 4}
        and (
            _resume_is_eligible(value, now)
            or _restart_guard_accepts(value, elapsed_seconds=_live_elapsed(value, now))
            or _continue_is_eligible(value, now)
            or _finalize_is_eligible(value)
        )
    ):
        try:
            migration_facts = _legacy_migration_facts(job, value, sha)
            legacy_migration_sha = digest(canonical(migration_facts))
            lifecycle_mutation_bound = True
            provider_launch_bound = bool(migration_facts["provider_launch_authorized"])
            if terminal_candidate:
                candidate_bound = True
        except (OSError, DispatchError):
            # A stale root, artifact, schema, selector, or boundary may not be
            # advertised as a migration route.  Terminal result readback keeps
            # its own stricter, non-mutating binder.
            legacy_migration_sha = None
    elif job is not None and (
        _resume_is_eligible(value, now)
        or _restart_guard_accepts(value, elapsed_seconds=_live_elapsed(value, now))
        or _continue_is_eligible(value, now)
        or _finalize_is_eligible(value)
    ):
        lifecycle_mutation_bound, provider_launch_bound = _lifecycle_mutation_bindings(
            job, value
        )
    available_actions = _available_actions(
        value, sha, now, job=job, candidate_bound=candidate_bound,
        legacy_result_bound=legacy_result_bound,
        lifecycle_mutation_bound=lifecycle_mutation_bound,
        provider_launch_bound=provider_launch_bound,
        legacy_migration_sha=legacy_migration_sha,
    )
    action_names = {item["action"] for item in available_actions}
    public_result_available = bool(
        value["candidate_recognized"] and "result" in action_names
    )
    # This is the canonical digest of the bound result bytes, never a worker
    # claim, path, or prose.  Do not expose it for a merely remembered or stale
    # candidate: consumers can safely use it as Verification v2 input only when
    # the same public surface makes `result` available.
    public_candidate_sha256 = (
        value["result_sha256"] if public_result_available else None
    )
    public_continue_available = "continue" in action_names
    public_failure_stage = (
        "binding_failure"
        if terminal_candidate and candidate_bound is False
        else value["failure_stage"]
    )
    next_action, next_action_command = _public_next_action(available_actions)
    public_assurance = (
        value["driver_disposition"]
        if value["driver_disposition"] in {"verified", "partially_verified", "rejected", "blocked"}
        else None
    )
    return {
        "attempt": value["attempt"],
        "attempt_origin": value["attempt_origin"],
        # Only a bound finalize records a Codex/driver decision.  Pending is
        # local lifecycle plumbing, never an assurance claim.
        "assurance": public_assurance,
        "check_counts": value["check_counts"],
        "check_summary": value["check_summary"],
        "cycle": value["cycle"],
        "elapsed_seconds": round(elapsed, 3),
        "exit_code": value["exit_code"],
        "hard_seconds": value["hard_seconds"],
        # Kept as a deprecated compatibility hint.  It says nothing about a clean
        # worktree and must not be used as an acceptance decision.
        "has_prior_candidate": bool(value["result_path"] or value["last_success_path"]),
        "candidate_recognized": value["candidate_recognized"],
        "candidate_source": value["candidate_source"],
        "candidate_sha256": public_candidate_sha256,
        "result_available": public_result_available,
        "worktree_reconciliation": value["worktree_reconciliation"],
        "worktree_changes_present": value["worktree_changes_present"],
        "worktree_changed_since_dispatch": value["worktree_changed_since_dispatch"],
        "driver_disposition": value["driver_disposition"],
        "failure_stage": public_failure_stage,
        "last_activity": value["last_activity"],
        "available_actions": available_actions,
        # Deprecated mechanical aliases retained for additive consumers.  They
        # are derived from the same live predicates as available_actions, never
        # from a controller recommendation stored in state.
        "next_action": next_action,
        "next_action_command": next_action_command,
        "job_id": value["job_id"],
        "last_progress_age_seconds": None if last_age is None else round(last_age, 3),
        "limit_kind": value["limit_kind"],
        "max_seconds": value["max_seconds"],
        "max_cycles": value["max_cycles"],
        "notice_count": value["notice_count"],
        "progress_count": value["progress_count"],
        "controller_phase": _controller_phase(value),
        "phase": value["phase"],
        "legacy_result_provenance": (
            "unknown_bound_legacy" if _legacy_prior_result_is_unknown(value) else "none"
        ),
        "migration_binding_sha256": legacy_migration_sha,
        "reason": value["reason"],
        "retry_after_seconds": retry_remaining,
        "remote_cancel_unverified": value["remote_cancel_unverified"],
        "resume_available": "resume" in action_names,
        "continue_available": public_continue_available,
        "state_sha256": sha,
        "status": value["status"],
        "workflow": value["workflow"],
    }


def print_json(value: Any) -> None:
    sys.stdout.buffer.write(canonical(value))
    sys.stdout.buffer.flush()


def print_text_status(value: dict[str, Any], sha: str, *, job: Path | None = None) -> None:
    """Print exactly three private-data-free lines for the human CLI surface."""
    counts = value["check_counts"]
    public = public_status(value, sha, job=job)
    actions = public["available_actions"]
    action_names = {item["action"] for item in actions}
    next_command = public["next_action_command"]
    result_command = next((
        item.get("command") for item in actions
        if item["action"] == "result" and isinstance(item.get("command"), str)
    ), None)
    resume_command = next((
        item.get("command") for item in actions
        if item["action"] == "resume" and isinstance(item.get("command"), str)
    ), None)
    restart_command = next((
        item.get("command") for item in actions
        if item["action"] == "restart" and isinstance(item.get("command"), str)
    ), None)
    historical_result = bool(
        result_command is not None
        and public["legacy_result_provenance"] == "unknown_bound_legacy"
    )
    finalized_result = bool(
        result_command is not None
        and value["driver_disposition"] in {
            "verified", "partially_verified", "rejected", "blocked",
        }
    )
    candidate_decision = (
        "then Codex—not the controller—chooses an eligible continue or finalize."
        if {"continue", "finalize"} <= action_names else
        "then Codex—not the controller—may choose the eligible continue action."
        if "continue" in action_names else
        "then Codex—not the controller—may choose the eligible finalize action."
        if "finalize" in action_names else
        "then no further driver decision is currently listed."
    )
    if next_command is None:
        # Continue/finalize need driver-owned bounded JSON.  This is still an
        # exact mechanical invocation, not a controller recommendation.
        action = next((item["action"] for item in actions if item["action"] in {"continue", "finalize"}), None)
        if action == "continue":
            next_command = (
                f"{PUBLIC_LAUNCHER} continue --job-id {value['job_id']} --approve-state-sha {sha} "
                "< DRIVER_VERIFICATION_JSON"
            )
        elif action == "finalize":
            next_command = (
                f"{PUBLIC_LAUNCHER} finalize --job-id {value['job_id']} --approve-state-sha {sha} "
                "--assurance ASSURANCE < DRIVER_VERIFICATION_JSON"
            )
    reason = public["reason"] if public["reason"] is not None else "none"
    failure_stage = public["failure_stage"] if public["failure_stage"] is not None else "none"
    selection_preflight_recovery_blocked = bool(
        public["reason"] == "selection_preflight_failed"
        or _post_candidate_selection_binding_drift(job, value)
    )
    cancelled_unreviewed_restart_guidance = (
        f" Available fresh restart command: {restart_command}."
        if (
            value["status"] == "cancelled"
            and value["driver_disposition"] == "unreviewed"
            and restart_command is not None
        ) else ""
    )
    ambiguous_recovery_options = {"resume", "restart"} <= action_names
    candidate_free_no_actions = bool(
        not actions
        and not value["candidate_recognized"]
    )
    candidate_free_runtime_budget_exhausted = bool(
        candidate_free_no_actions and value["limit_kind"] == "max-runtime"
    )
    candidate_free_attempt_budget_exhausted = bool(
        candidate_free_no_actions
        and not candidate_free_runtime_budget_exhausted
        and value["attempt"] >= value["max_cycles"]
    )
    lines = (
        f"Provider attempt: {value['status']}; reason: {reason}; failure stage: {failure_stage}; bound result available: {'yes' if public['result_available'] else 'no'}; driver disposition: {value['driver_disposition']}.",
        f"Driver evidence: {counts['passed']} passed, {counts['failed']} failed, {counts['advisory']} advisory, {counts['missing']} missing; cycle: {public['cycle']}/{public['max_cycles']}.",
        (
            (
                f"Next safe action: retrieve current bound result JSON with {result_command}; review it and run driver checks, then Codex—not the controller—may finalize after review. No provider-launching same-job recovery is available."
                if result_command is not None and "finalize" in action_names else
                f"Next safe action: retrieve current bound result JSON with {result_command}; no provider-launching same-job recovery is available."
                if result_command is not None else
                "Next safe action: create a fresh job using the unchanged caller selection after reviewing the current sanitized agy interface evidence. No same-job action is available."
            )
            if selection_preflight_recovery_blocked else
            f"Next safe action: retrieve historical result evidence only with {result_command}; do not use it for Verification v2, continue, or finalize."
            if historical_result else
            (
                f"Next safe action: optional finalized result JSON readback with {result_command}; driver disposition is already recorded; do not construct Verification v2, continue, or finalize. Available fresh restart command: {restart_command}."
                if restart_command is not None else
                f"Next safe action: optional finalized result JSON readback with {result_command}; driver disposition is already recorded; do not construct Verification v2, continue, or finalize."
            )
            if finalized_result else
            f"Next safe action: retrieve current bound result JSON with {result_command}; review it and run driver checks, construct Verification v2, {candidate_decision}{cancelled_unreviewed_restart_guidance}"
            if result_command is not None else
            f"Next safe actions: exact-conversation resume: {resume_command}; fresh-attempt restart: {restart_command}."
            if ambiguous_recovery_options and resume_command is not None and restart_command is not None else
            f"Next safe action: exact-conversation resume: {resume_command}."
            if resume_command is not None and "resume" in action_names else
            f"Next safe action: fresh-attempt restart: {restart_command}."
            if restart_command is not None and "restart" in action_names else
            "Next safe action: none; the current runtime budget is exhausted."
            if candidate_free_runtime_budget_exhausted else
            "Next safe action: none; the current attempt budget is exhausted."
            if candidate_free_attempt_budget_exhausted else
            f"Next safe action: {next_command}." if next_command is not None else "Next safe action: none."
        ),
    )
    sys.stdout.buffer.write(("\n".join(lines) + "\n").encode("utf-8"))
    sys.stdout.buffer.flush()


def print_control_status(
    value: dict[str, Any], sha: str, output_format: str, *, job: Path | None = None,
) -> None:
    if output_format == "text":
        print_text_status(value, sha, job=job)
    else:
        print_json(public_status(value, sha, job=job))


def _state_approval_error(state: dict[str, Any], sha: str, action: str) -> DispatchError:
    """Keep stale approval recovery useful without exposing private controller data."""
    suffix = {
        "continue": " < DRIVER_VERIFICATION_JSON",
        "finalize": " --assurance ASSURANCE < DRIVER_VERIFICATION_JSON",
        # Duration is caller-owned input.  A placeholder is deliberately not
        # an executable-looking exact duration, and never invents a value.
        "extend": " --by DURATION",
    }.get(action, "")
    return DispatchError(
        "state approval is missing or stale; rerun: "
        f"{PUBLIC_LAUNCHER} {action} --job-id {state['job_id']} --approve-state-sha {sha}{suffix}"
    )


def _missing_state_approval(job: Path, action: str) -> DispatchError:
    state, _raw, sha = read_state_snapshot(job)
    return _state_approval_error(state, sha, action)


def _attempt_paths(job: Path, attempt: int) -> tuple[Path, Path, Path]:
    if attempt == 1:
        return job / "stream.ndjson", job / "stderr.txt", job / "envelope.json"
    prefix = f"attempt-{attempt:03d}"
    return job / f"{prefix}.stream.ndjson", job / f"{prefix}.stderr.txt", job / f"{prefix}.envelope.json"


def _ensure_new_private(path: Path) -> int:
    return os.open(
        path,
        os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
        0o600,
    )


def _stage(command: dict[str, Any], readonly: bool) -> None:
    if command["stage_dir"] is None:
        return
    directory = Path(command["stage_dir"])
    source = Path(command["stage_file"])
    directory.chmod(0o555 if readonly else 0o700)
    source.chmod(0o444 if readonly else 0o600)


def _bound_stage(
    command: dict[str, Any], *, readonly: bool,
) -> tuple[str | None, tuple[int, int, int, int, int] | None]:
    if command["stage_file"] is None:
        return None, None
    path = Path(command["stage_file"])
    expected_mode = 0o444 if readonly else 0o600
    raw, info = read_regular(
        path, MAX_COMMAND_BYTES, "staged prompt", allowed_modes=(expected_mode,)
    )
    if stat.S_IMODE(info.st_mode) != expected_mode:
        raise DispatchError("staged prompt mode is invalid")
    directory = Path(command["stage_dir"])
    directory_info = directory.lstat()
    expected_directory_mode = 0o555 if readonly else 0o700
    if (
        not stat.S_ISDIR(directory_info.st_mode)
        or stat.S_ISLNK(directory_info.st_mode)
        or directory_info.st_uid != os.getuid()
        or stat.S_IMODE(directory_info.st_mode) != expected_directory_mode
    ):
        raise DispatchError("staged prompt directory is invalid")
    return digest(raw), _identity(info)


def _validate_verification(value: Any) -> dict[str, Any]:
    v1_fields = {"schema_version", "summary", "passed_checks", "failed_checks", "advisory_checks", "missing_checks"}
    v2_fields = v1_fields | {
        "candidate_sha256", "coverage", "verified_findings", "unresolved_gaps",
        "diff_review_complete",
    }
    if not isinstance(value, dict) or set(value) not in (v1_fields, v2_fields):
        raise DispatchError("verification feedback fields are invalid")
    if value["schema_version"] not in {1, 2} or (value["schema_version"] == 1) != (set(value) == v1_fields):
        raise DispatchError("verification feedback version is invalid")
    summary = value["summary"]
    if not isinstance(summary, str) or not (1 <= len(summary) <= MAX_CHECK_SUMMARY) or any(
        item in summary for item in ("\x00", "\r", "\n")
    ):
        raise DispatchError("verification feedback summary is invalid")
    for key in ("passed_checks", "failed_checks"):
        checks = value[key]
        if not isinstance(checks, list) or len(checks) > MAX_CHECK_ITEMS or any(
            not isinstance(item, str) or not (1 <= len(item) <= MAX_CHECK_LABEL)
            or any(control in item for control in ("\x00", "\r", "\n"))
            for item in checks
        ):
            raise DispatchError("verification feedback checks are invalid")
    for key in ("advisory_checks", "missing_checks"):
        if type(value[key]) is not int or not (0 <= value[key] <= MAX_CHECK_ITEMS):
            raise DispatchError("verification feedback counts are invalid")
    if value["schema_version"] == 2:
        if not isinstance(value["candidate_sha256"], str) or SHA_RE.fullmatch(value["candidate_sha256"]) is None:
            raise DispatchError("verification feedback candidate binding is invalid")
        if value["coverage"] not in {"complete", "partial", "not_assessed", "not_applicable"}:
            raise DispatchError("verification feedback coverage is invalid")
        for key in ("verified_findings", "unresolved_gaps"):
            if type(value[key]) is not int or not (0 <= value[key] <= MAX_CHECK_ITEMS):
                raise DispatchError("verification feedback evidence counts are invalid")
        if type(value["diff_review_complete"]) is not bool:
            raise DispatchError("verification feedback diff review is invalid")
    if len(canonical(value)) > MAX_VERIFICATION_BYTES:
        raise DispatchError("verification feedback canonical bytes are oversized")
    return value


def _verification_from_stdin() -> dict[str, Any]:
    raw = sys.stdin.buffer.read(MAX_VERIFICATION_BYTES + 1)
    if len(raw) > MAX_VERIFICATION_BYTES:
        raise DispatchError("verification feedback is oversized")
    return _validate_verification(parse_json(raw, "verification feedback"))


def _verification_counts(value: dict[str, Any]) -> dict[str, int]:
    return {
        "passed": len(value["passed_checks"]),
        "failed": len(value["failed_checks"]),
        "advisory": value["advisory_checks"],
        "missing": value["missing_checks"],
    }


def _verification_is_verified(value: dict[str, Any], workflow: str) -> bool:
    counts = _verification_counts(value)
    if value["schema_version"] != 2 or counts["failed"] or counts["missing"]:
        return False
    if workflow == "explore":
        return value["coverage"] == "complete" and value["unresolved_gaps"] == 0
    return counts["passed"] >= 1 and value["diff_review_complete"]


def _require_current_candidate_verification(value: dict[str, Any], state: dict[str, Any]) -> None:
    """V1 is readable for compatibility, but never authorizes a lifecycle write."""
    if value["schema_version"] != 2:
        raise DispatchError("verification v2 is required for candidate disposition")
    if (
        not state["candidate_recognized"] or not state["result_available"]
        or state["result_sha256"] is None
    ):
        raise DispatchError("verification has no current recognized candidate")
    if value["candidate_sha256"] != state["result_sha256"]:
        raise DispatchError("verification candidate binding is stale")


def _write_verification(job: Path, label: str, value: dict[str, Any]) -> tuple[Path, str, tuple[int, int, int, int, int]]:
    directory = job / "continue-staged"
    if directory.exists() or directory.is_symlink():
        info = directory.lstat()
        if (
            not stat.S_ISDIR(info.st_mode) or stat.S_ISLNK(info.st_mode)
            or info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) not in {0o700, 0o555}
        ):
            raise DispatchError("verification staging directory is invalid")
        directory.chmod(0o700)
    else:
        directory.mkdir(mode=0o700)
    path = directory / f"{label}.json"
    raw = canonical(value)
    if len(raw) > MAX_VERIFICATION_BYTES:
        raise DispatchError("verification feedback canonical bytes are oversized")
    descriptor = -1
    created_identity: tuple[int, int, int, int, int] | None = None
    try:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o600)
        created_info = os.fstat(descriptor)
        if not stat.S_ISREG(created_info.st_mode) or created_info.st_nlink != 1:
            raise DispatchError("verification feedback staging identity is invalid")
        created_identity = _identity(created_info)
    except DispatchError:
        raise
    except OSError as exc:
        raise DispatchError("verification staging path is unavailable") from exc
    try:
        os.fchmod(descriptor, 0o600)
        offset = 0
        while offset < len(raw):
            written = os.write(descriptor, raw[offset:])
            if written <= 0:
                raise DispatchError("verification feedback staging write failed")
            offset += written
        os.fsync(descriptor)
        os.close(descriptor)
        descriptor = -1
        path.chmod(0o400)
        directory.chmod(0o700)
        bound, info = read_regular(path, MAX_VERIFICATION_BYTES, "verification feedback", allowed_modes=(0o400,))
        if bound != raw:
            raise DispatchError("verification feedback changed during staging")
        return path, digest(bound), _identity(info)
    except (OSError, DispatchError):
        if descriptor >= 0:
            with contextlib.suppress(OSError):
                os.close(descriptor)
        if created_identity is None:
            with contextlib.suppress(OSError):
                fallback_info = path.lstat()
                if stat.S_ISREG(fallback_info.st_mode) and fallback_info.st_nlink == 1:
                    created_identity = _identity(fallback_info)
        _discard_new_verification(path, created_identity)
        raise


def _discard_new_verification(path: Path | None, identity: tuple[int, int, int, int, int] | None) -> None:
    if path is None or identity is None:
        return
    try:
        parent = path.parent
        parent_info = parent.lstat()
        if (
            not stat.S_ISDIR(parent_info.st_mode) or stat.S_ISLNK(parent_info.st_mode)
            or parent_info.st_uid != os.getuid() or stat.S_IMODE(parent_info.st_mode) not in {0o700, 0o555}
        ):
            return
        # A prior runtime used 0555 for this directory.  Recover that exact
        # owner-private directory, but publish new staging in cleanup-friendly
        # 0700 mode.
        parent.chmod(0o700)
        info = path.lstat()
        if stat.S_ISREG(info.st_mode) and _identity(info) == identity and info.st_nlink == 1:
            path.unlink()
            descriptor = os.open(parent, os.O_RDONLY)
            try:
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
    except OSError:
        pass


def _bound_verification(job: Path, state: dict[str, Any]) -> Path | None:
    path_text = state["verification_path"]
    if path_text is None:
        return None
    path = Path(path_text)
    expected = job / "continue-staged" / f"cycle-{state['cycle']:03d}.json"
    if state["attempt_origin"] != "conversation-continue" or path != expected:
        raise DispatchError("verification feedback path is not bound to this continuation")
    raw, info = read_regular(path, MAX_VERIFICATION_BYTES, "verification feedback", allowed_modes=(0o400,))
    if digest(raw) != state["verification_sha256"] or list(_identity(info)) != state["verification_identity"]:
        raise DispatchError("verification feedback binding changed")
    _require_current_candidate_verification(
        _validate_verification(parse_json(raw, "verification feedback")), state,
    )
    parent = path.parent.lstat()
    if (
        not stat.S_ISDIR(parent.st_mode) or stat.S_ISLNK(parent.st_mode)
        or parent.st_uid != os.getuid() or stat.S_IMODE(parent.st_mode) != 0o700
    ):
        raise DispatchError("verification staging directory changed")
    return path


# Worktree/Git snapshot implementation is path-pinned to the sibling helper.
# Each façade call supplies this module's current globals so test and controller
# monkeypatches remain observable while the portable runtime has no package import.
_worktree_helper_path = Path(__file__).with_name("agy_dispatch_worktree.py")
_worktree_helper_spec = importlib.util.spec_from_file_location(
    "agy_dispatch_worktree", _worktree_helper_path,
)
if _worktree_helper_spec is None or _worktree_helper_spec.loader is None:  # pragma: no cover - bundle invariant
    raise RuntimeError("dispatch worktree helper is unavailable")
_WORKTREE_HELPER = importlib.util.module_from_spec(_worktree_helper_spec)
exec(
    compile(_worktree_helper_path.read_bytes(), str(_worktree_helper_path), "exec"),
    _WORKTREE_HELPER.__dict__,
)


class _MarkerPreflightLimit(Exception):
    """The marker-only scan hit its documented bounded entry cap."""


_FIXED_GIT_READ_ARGV = _WORKTREE_HELPER._FIXED_GIT_READ_ARGV
_WORKTREE_FACADE_DEFAULTS: dict[str, Any] = {}


def _worktree_call(name: str, *args: Any, **kwargs: Any) -> Any:
    dependencies = dict(globals())
    for dependency in _WORKTREE_HELPER._IMPLEMENTATION_FUNCTIONS:
        if dependencies.get(dependency) is _WORKTREE_FACADE_DEFAULTS.get(dependency):
            dependencies[dependency] = _WORKTREE_HELPER._IMPLEMENTATION_DEFAULTS[dependency]
    return _WORKTREE_HELPER.call(name, dependencies, *args, **kwargs)


def _marker_only_preflight(root_fd: int, *, deadline: float | None = None) -> bool:
    return _worktree_call("_marker_only_preflight", root_fd, deadline=deadline)


def _resolved_path_is_git_administration(root: str, resolved: str) -> bool:
    return _worktree_call("_resolved_path_is_git_administration", root, resolved)


def _worktree_symlink_boundary(workdir: str) -> bool:
    return _worktree_call("_worktree_symlink_boundary", workdir)


def _worktree_git_admin_alias_boundary(workdir: str) -> bool:
    return _worktree_call("_worktree_git_admin_alias_boundary", workdir)


def _project_boundary(workdir: str) -> dict[str, Any]:
    return _worktree_call("_project_boundary", workdir)


def _safe_git_owner_mode(metadata: os.stat_result, *, directory: bool) -> bool:
    return _worktree_call("_safe_git_owner_mode", metadata, directory=directory)


def _safe_git_executable() -> tuple[str, dict[str, Any]] | None:
    return _worktree_call("_safe_git_executable")


def _confirm_safe_git_executable(executable: str, expected: dict[str, Any]) -> bool:
    return _worktree_call("_confirm_safe_git_executable", executable, expected)


def _safe_git_is_outside_worktree(executable: str, worktree_root: str) -> bool:
    return _worktree_call("_safe_git_is_outside_worktree", executable, worktree_root)


def _stable_git_authority(info: os.stat_result) -> dict[str, int]:
    return _worktree_call("_stable_git_authority", info)


def _full_stat_binding(info: os.stat_result) -> tuple[int, ...]:
    return _worktree_call("_full_stat_binding", info)


def _bound_git_worktree_root(
    raw: bytes, canonical_root: str, root_binding: tuple[int, ...],
) -> bool:
    return _worktree_call("_bound_git_worktree_root", raw, canonical_root, root_binding)


def _fixed_git_read_argv(arguments: list[str]) -> bool:
    return _worktree_call("_fixed_git_read_argv", arguments)


def _bounded_git_read(
    executable: str, executable_authority: dict[str, Any], root: str,
    arguments: list[str], *, deadline: float, payload: bytes = b"",
    allowed: tuple[int, ...] = (0,), stdout_limit: int | None = None,
) -> tuple[int, bytes] | None:
    return _worktree_call(
        "_bounded_git_read", executable, executable_authority, root, arguments,
        deadline=deadline, payload=payload, allowed=allowed, stdout_limit=stdout_limit,
    )


def _git_boundary_identity(workdir: str) -> dict[str, Any] | None:
    return _worktree_call("_git_boundary_identity", workdir)


def _worktree_snapshot(
    workdir: str, *, legacy: bool = False, explain_unsupported: bool = False,
) -> dict[str, Any] | None:
    try:
        return _worktree_call(
            "_worktree_snapshot", workdir, legacy=legacy,
            explain_unsupported=explain_unsupported,
        )
    except _WORKTREE_HELPER._ResolveUndoPresentError as exc:
        raise ResolveUndoPresentError(str(exc)) from None
    except _WORKTREE_HELPER._UnsupportedWorktreeError as exc:
        raise WorktreeBaselineError(str(exc)) from None

def _scan_readable_worktree(worktree: str | Path) -> list[dict[str, str]]:
    return _worktree_call("_scan_readable_worktree", worktree)


def _validate_manifest(manifest: Any) -> list[dict[str, str]]:
    return _worktree_call("_validate_manifest", manifest)


def _manifest_digest(manifest: list[dict[str, str]]) -> str:
    return _worktree_call("_manifest_digest", manifest)


def _parse_provider_scope(raw_bytes: bytes) -> dict[str, Any]:
    return _worktree_call("_parse_provider_scope", raw_bytes)


def _validate_scope_against_worktree(
    scope: dict[str, Any], worktree_root: str | Path, readable_manifest: list[dict[str, str]],
) -> None:
    return _worktree_call("_validate_scope_against_worktree", scope, worktree_root, readable_manifest)


def _build_selected_content_manifest(
    root_dir: str | Path, scope: dict[str, Any], *, is_stage: bool = False,
) -> list[dict[str, Any]]:
    return _worktree_call("_build_selected_content_manifest", root_dir, scope, is_stage=is_stage)


def _selected_content_digest(manifest: list[dict[str, Any]]) -> str:
    return _worktree_call("_selected_content_digest", manifest)


def _canonical_digest(value: Any) -> str:
    return _worktree_call("_canonical_digest", value)


def _compute_transmission_sha256(
    policy_sha256: str, readable_manifest_sha256: str, selected_content_sha256: str,
) -> str:
    return _worktree_call(
        "_compute_transmission_sha256", policy_sha256, readable_manifest_sha256, selected_content_sha256,
    )


def _materialize_stage(
    source_root: str | Path, stage_dir: str | Path, scope: dict[str, Any],
    selected_manifest: list[dict[str, Any]],
) -> tuple[tuple[int, int, int, int, int], str]:
    return _worktree_call(
        "_materialize_stage", source_root, stage_dir, scope, selected_manifest,
    )


def _scan_stage_mutations(
    stage_dir: str | Path, scope: dict[str, Any], pre_launch_manifest: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], str]:
    return _worktree_call(
        "_scan_stage_mutations", stage_dir, scope, pre_launch_manifest,
    )


def _reconcile_stage_to_source(
    source_root: str | Path, stage_dir: str | Path, operation_manifest: list[dict[str, Any]],
    job_dir: Path,
) -> str:
    return _worktree_call(
        "_reconcile_stage_to_source", source_root, stage_dir, operation_manifest, job_dir,
    )


def _recover_reconciliation(source_root: str | Path, job_dir: Path) -> bool:
    return _worktree_call("_recover_reconciliation", source_root, job_dir)


def _cleanup_stage(stage_dir: str | Path, recorded_identity: tuple[int, int, int, int, int]) -> None:
    return _worktree_call("_cleanup_stage", stage_dir, recorded_identity)


_WORKTREE_FACADE_DEFAULTS = {
    name: globals()[name] for name in _WORKTREE_HELPER._IMPLEMENTATION_FUNCTIONS
}


def _dispatch_root_identity(workdir: str) -> dict[str, Any] | None:
    """Return V9's stable root/Git-administration authority record.

    Unlike the semantic candidate snapshot, this extractor is intentionally
    unchanged by ordinary tracked/untracked worktree edits, index refreshes,
    HEAD/ref moves, and object maintenance.  Those remain candidate-binding
    facts; this record detects a substituted repository boundary.
    """
    return _git_boundary_identity(workdir)


def _state_worktree_snapshot(state: dict[str, Any], workdir: str) -> dict[str, Any] | None:
    """Use a persisted algorithm identity; historical snapshots stay exact."""
    if state.get("schema_version") in {5, 6}:
        algorithm = WORKTREE_SNAPSHOT_LEGACY_V6
    elif state.get("schema_version") == 7:
        # V7 predates the explicit field but its semantic digest is frozen.
        algorithm = WORKTREE_SNAPSHOT_SEMANTIC_V1
    elif state.get("schema_version") is None:
        # This private helper also accepts a baseline-only test/launch probe;
        # it is never a validated persisted state.
        algorithm = WORKTREE_SNAPSHOT_SEMANTIC_V1
    else:
        algorithm = state.get("worktree_snapshot_algorithm")
    if algorithm == WORKTREE_SNAPSHOT_LEGACY_V6:
        return _worktree_snapshot(workdir, legacy=True)
    if algorithm == WORKTREE_SNAPSHOT_SEMANTIC_V1:
        return _worktree_snapshot(workdir)
    raise DispatchError("dispatch worktree snapshot algorithm is unavailable")


def _reconciliation_from_snapshot(
    current: dict[str, Any] | None, baseline: dict[str, Any] | None,
) -> dict[str, Any]:
    """Project reconciliation from one already-linearized worktree fact."""
    if current is None or baseline is None:
        return {
            "worktree_reconciliation": "unavailable",
            "worktree_changes_present": None,
            "worktree_changed_since_dispatch": None,
        }
    return {
        "worktree_reconciliation": "available",
        "worktree_changes_present": current["entries"] > 0,
        "worktree_changed_since_dispatch": current["sha256"] != baseline["sha256"],
    }


def _reconcile_worktree(
    workdir: str, baseline: dict[str, Any] | None, *, state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    current = _worktree_snapshot(workdir) if state is None else _state_worktree_snapshot(state, workdir)
    return _reconciliation_from_snapshot(current, baseline)


def _schema_binding(path: Path) -> tuple[str, tuple[int, int, int, int, int]]:
    """Bind a schema as dispatch input without accepting a symlink swap."""
    try:
        descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    except OSError as exc:
        raise DispatchError("dispatch schema is unavailable") from exc
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode) or stat.S_ISLNK(before.st_mode) or before.st_size > 1024 * 1024:
            raise DispatchError("dispatch schema is invalid")
        raw = b""
        while len(raw) <= 1024 * 1024:
            piece = os.read(descriptor, 65536)
            if not piece:
                break
            raw += piece
        after = os.fstat(descriptor)
    finally:
        os.close(descriptor)
    try:
        named = path.lstat()
    except OSError as exc:
        raise DispatchError("dispatch schema identity changed") from exc
    if len(raw) > 1024 * 1024 or _identity(before) != _identity(after) or _identity(after) != _identity(named):
        raise DispatchError("dispatch schema identity changed")
    return digest(raw), _identity(after)


def _schema_paths(command: dict[str, Any]) -> tuple[Path, Path] | None:
    argv = command["argv"]
    if "--json-schema" not in argv:
        return None
    if argv.count("--json-schema") != 1:
        raise DispatchError("dispatch schema argument is invalid")
    index = argv.index("--json-schema")
    if index + 1 >= len(argv):
        raise DispatchError("dispatch schema argument is invalid")
    return Path(argv[index + 1]), Path(__file__).parent.parent / "schemas" / "worker-result.schema.json"


def _schema_bindings(command: dict[str, Any]) -> dict[str, Any]:
    paths = _schema_paths(command)
    if paths is None:
        return {
            "provider_schema_sha256": None, "provider_schema_identity": None,
            "canonical_schema_sha256": None, "canonical_schema_identity": None,
        }
    provider_sha, provider_identity = _schema_binding(paths[0])
    canonical_sha, canonical_identity = _schema_binding(paths[1])
    return {
        "provider_schema_sha256": provider_sha, "provider_schema_identity": list(provider_identity),
        "canonical_schema_sha256": canonical_sha, "canonical_schema_identity": list(canonical_identity),
    }


def _bound_schemas(command: dict[str, Any], state: dict[str, Any]) -> tuple[Path, Path]:
    paths = _schema_paths(command)
    if paths is None:
        raise DispatchError("dispatch schema argument is unavailable")
    expected = _schema_bindings(command)
    for key, value in expected.items():
        if state[key] != value:
            raise DispatchError("dispatch schema binding changed")
    return paths


def _bound_candidate_worktree(state: dict[str, Any], command: dict[str, Any]) -> None:
    """Reject post-review worktree drift before a continuation or final disposition."""
    quiescent = (
        state["status"] in TERMINAL and state["controller_pid"] is None
    ) or (
        state["status"] == "queued"
        and state["attempt_origin"] == "conversation-continue"
        # The owning controller publishes its PID while provider-free local
        # preflight is in progress.  No other process may treat that active
        # queued candidate as quiescent.
        and state["controller_pid"] in {None, os.getpid()}
    )
    if not quiescent:
        raise DispatchError("candidate worktree is not quiescent")
    # Candidate content and repository authority are separate checks.  The
    # same V9 extractor used by lifecycle recovery is repeated here so a
    # direct candidate-binding caller cannot turn a substituted Git boundary
    # into a content-only comparison.
    if state.get("schema_version") in {9, 10, CURRENT_STATE_SCHEMA} and (
        _git_boundary_identity(command["workdir"])
        != state.get("worktree_root_identity")
    ):
        raise DispatchError("dispatch worktree root binding changed")
    expected_sha = state["candidate_worktree_sha256"]
    expected_entries = state["candidate_worktree_entries"]
    current = _state_worktree_snapshot(state, command["workdir"])
    if current is None or expected_sha is None or expected_entries is None:
        raise DispatchError("candidate worktree reconciliation is unavailable")
    if current["sha256"] != expected_sha or current["entries"] != expected_entries:
        raise DispatchError("candidate worktree binding changed")


def _bound_current_candidate(job: Path, state: dict[str, Any]) -> tuple[dict[str, Any], bytes]:
    """Reopen every current-candidate authority before exposing or mutating it.

    This is intentionally one bounded no-follow binding sequence, reused by
    status action projection, continuation staging/launch, result delivery, and
    finalization.  It binds the private command, state worktree/root, both
    schemas, current canonical artifact, and post-provider worktree fact set.
    """

    if not (
        state["candidate_recognized"] and state["result_available"]
        and isinstance(state["result_path"], str)
        and isinstance(state["result_sha256"], str)
        and isinstance(state["result_identity"], list)
    ):
        raise DispatchError("dispatch has no current recognized candidate")
    try:
        bound_job = canonical_job(Path(job).resolve(strict=True))
    except OSError as exc:
        raise DispatchError("job directory is unavailable") from exc
    # Old snapshots are readable evidence only.  Do not synthesize a V9 root
    # identity during a result/status read: that would make a replacement root
    # look approved before an explicit, provable transition.
    legacy_read = state["schema_version"] < 9
    result_path = Path(state["result_path"])
    try:
        result_parent = result_path.parent.resolve(strict=True)
    except OSError as exc:
        raise DispatchError("dispatch result path is unavailable") from exc
    if not result_path.is_absolute() or result_parent != bound_job:
        raise DispatchError("dispatch result path is outside this job")
    command = _load_bound_command(bound_job, state, stage_readonly=False)
    command, state = _bound_lifecycle_inputs(
        bound_job, state, command, read_legacy=legacy_read,
    )
    schema_paths = _schema_paths(command)
    if schema_paths is None:
        raise DispatchError("dispatch schema argument is unavailable")
    raw, info = read_regular(result_path, 1024 * 1024, "dispatch result")
    if digest(raw) != state["result_sha256"] or list(_identity(info)) != state["result_identity"]:
        raise DispatchError("dispatch result binding changed")
    validator = Path(__file__).with_name("validate-envelope.py")
    checked = [
        subprocess.run(
            [sys.executable, "-I", "-S", "-B", str(validator), str(schema), str(result_path)],
            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            check=False,
        )
        for schema in schema_paths
    ]
    if any(item.returncode != 0 for item in checked):
        raise DispatchError("dispatch result is no longer valid")
    rebound, rebound_info = read_regular(result_path, 1024 * 1024, "dispatch result")
    if rebound != raw or _identity(rebound_info) != _identity(info):
        raise DispatchError("dispatch result binding changed")
    # The validator opened both schema pathnames; bind them and the project
    # marker again before accepting its answer.
    _bound_lifecycle_inputs(bound_job, state, command, read_legacy=legacy_read)
    # Project jobs created before the external-log-root boundary can place their
    # own controller state inside the candidate worktree. Every state write then
    # changes the semantic snapshot, so that stored snapshot is self-invalidating.
    # Keep exact command/schema/root/result bindings for readback and a driver-only
    # final disposition; provider recovery is denied by the inside-worktree guard.
    if not legacy_read and not _job_is_inside_worktree(bound_job, command["workdir"]):
        _bound_candidate_worktree(state, command)
    return command, raw


def _verification_copy_destination(destination: Path, worktree: Path) -> tuple[Path, tuple[int, int, int, int, int]]:
    """Accept one new private directory outside the bound candidate.

    The copy is a driver convenience, not controller state or acceptance evidence.
    Keeping the destination caller-selected avoids exposing a local path through the
    public status surface, while the private-parent rule keeps accidental sharing and
    symlink traversal out of the helper's scope.
    """
    if not destination.is_absolute() or destination.name in {"", ".", ".."}:
        raise DispatchError("verification copy destination is invalid")
    parent = destination.parent
    if Path(os.path.realpath(parent)) != parent:
        raise DispatchError("verification copy destination parent is not canonical")
    try:
        metadata = parent.lstat()
    except OSError as exc:
        raise DispatchError("verification copy destination parent is unavailable") from exc
    if (
        not stat.S_ISDIR(metadata.st_mode)
        or stat.S_ISLNK(metadata.st_mode)
        or metadata.st_uid != os.getuid()
        or stat.S_IMODE(metadata.st_mode) != 0o700
    ):
        raise DispatchError("verification copy destination parent must be owner-private")
    if destination.exists() or destination.is_symlink():
        raise DispatchError("verification copy destination must be new")
    try:
        if os.path.commonpath((str(worktree), str(destination))) == str(worktree):
            raise DispatchError("verification copy destination is inside the candidate")
    except ValueError as exc:
        raise DispatchError("verification copy destination is invalid") from exc
    return destination, _identity(metadata)


def _discard_verification_copy(destination: Path) -> None:
    """Best-effort removal of a failed new verifier workspace without following links."""
    try:
        info = destination.lstat()
    except FileNotFoundError:
        return
    except OSError:
        return
    try:
        if stat.S_ISDIR(info.st_mode) and not stat.S_ISLNK(info.st_mode):
            # Copied source metadata may make nested directories read-only.
            # Restore write/search permission only on lstat-proven directories
            # below this disposable copy; link nodes are never traversed or
            # chmodded before rmtree unlinks them.
            pending = [destination]
            while pending:
                current = pending.pop()
                current_info = current.lstat()
                if not stat.S_ISDIR(current_info.st_mode) or stat.S_ISLNK(current_info.st_mode):
                    continue
                os.chmod(current, 0o700)
                with os.scandir(current) as entries:
                    for entry in entries:
                        child = Path(entry.path)
                        child_info = child.lstat()
                        if stat.S_ISDIR(child_info.st_mode) and not stat.S_ISLNK(child_info.st_mode):
                            pending.append(child)
            shutil.rmtree(destination)
        elif stat.S_ISLNK(info.st_mode):
            destination.unlink()
    except OSError:
        # The owner-private parent and the current local user are in the
        # documented TCB.  A same-UID replacement can still make cleanup
        # uncertain; never turn that into a successful copy result.
        pass


def _copy_bound_candidate(worktree: Path, destination: Path) -> None:
    """Copy a candidate without following source links or copying Git metadata.

    Every contained source link becomes a relative link to the corresponding
    object under ``destination``.  Preserving either an absolute target or a
    location-dependent relative spelling can resolve back into the candidate
    after relocation, so ``copytree(symlinks=True)`` cannot provide this
    isolation.
    """
    root = Path(os.path.realpath(worktree))

    def require_contained_link(source: Path, target: Path) -> str:
        before = source.lstat()
        if not stat.S_ISLNK(before.st_mode):
            raise DispatchError("verification copy source link changed")
        try:
            target_text = os.readlink(source)
            resolved = os.path.realpath(source)
            after = source.lstat()
        except OSError as exc:
            raise DispatchError("verification copy source link is unavailable") from exc
        if _identity(before) != _identity(after):
            raise DispatchError("verification copy source link changed")
        try:
            contained = os.path.commonpath([str(root), resolved]) == str(root)
        except ValueError:
            contained = False
        if (
            not contained or not os.path.exists(resolved)
            or _resolved_path_is_git_administration(str(root), resolved)
        ):
            raise DispatchError("verification copy source link is unsafe")
        # A relative source spelling can still escape a sibling copy (for
        # example ``../source/target``).  Rebase every contained link from its
        # resolved source object to the mirrored destination object instead of
        # preserving raw target text.
        mirrored = destination / os.path.relpath(resolved, root)
        return os.path.relpath(mirrored, target.parent)

    def copy_entry(source: Path, target: Path, *, is_root: bool = False) -> None:
        try:
            before = source.lstat()
        except OSError as exc:
            raise DispatchError("verification copy source is unavailable") from exc
        if stat.S_ISLNK(before.st_mode):
            target_text = require_contained_link(source, target)
            try:
                os.symlink(target_text, target)
                shutil.copystat(source, target, follow_symlinks=False)
            except OSError as exc:
                raise DispatchError("verification copy failed") from exc
            return
        if stat.S_ISREG(before.st_mode):
            try:
                shutil.copy2(source, target, follow_symlinks=False)
                copied = target.lstat()
                after = source.lstat()
            except OSError as exc:
                raise DispatchError("verification copy failed") from exc
            if (
                _identity(before) != _identity(after)
                or not stat.S_ISREG(copied.st_mode)
            ):
                raise DispatchError("verification copy source changed")
            return
        if not stat.S_ISDIR(before.st_mode):
            raise DispatchError("verification copy source has unsupported entry")
        try:
            # Child entries must be created before source metadata is restored:
            # an otherwise valid read-only source directory would reject them.
            os.mkdir(target, 0o700)
            entries = list(os.scandir(source))
        except OSError as exc:
            raise DispatchError("verification copy failed") from exc
        markers = [entry.name for entry in entries if entry.name.lower() == ".git"]
        if is_root:
            if any(name != ".git" for name in markers):
                raise DispatchError("verification copy source has ambiguous Git administration")
        elif markers:
            raise DispatchError("verification copy source has nested Git administration")
        for entry in entries:
            if is_root and entry.name == ".git":
                continue
            copy_entry(Path(entry.path), target / entry.name)
        try:
            after = source.lstat()
            if _identity(before) != _identity(after):
                raise DispatchError("verification copy source changed")
            shutil.copystat(source, target, follow_symlinks=False)
        except OSError as exc:
            raise DispatchError("verification copy failed") from exc

    try:
        copy_entry(root, destination, is_root=True)
        os.chmod(destination, 0o700)
        copied = destination.lstat()
    except (OSError, shutil.Error, DispatchError):
        _discard_verification_copy(destination)
        raise
    if (
        not stat.S_ISDIR(copied.st_mode)
        or stat.S_ISLNK(copied.st_mode)
        or copied.st_uid != os.getuid()
        or stat.S_IMODE(copied.st_mode) != 0o700
        or (destination / ".git").exists()
        or (destination / ".git").is_symlink()
    ):
        _discard_verification_copy(destination)
        raise DispatchError("verification copy binding changed")


def command_verification_copy(job: Path, destination: Path, output_format: str) -> int:
    """Create an isolated verifier workspace after exact candidate revalidation."""
    with state_lock(job):
        state, _raw, _sha = load_state(job)
        if not _verification_copy_is_eligible(state):
            raise DispatchError("verification copy is unavailable")
        command = _load_bound_command(job, state, stage_readonly=False)
        command, state = _bound_lifecycle_inputs(job, state, command)
        if _job_is_inside_worktree(job, command["workdir"]):
            raise DispatchError("verification copy is unavailable for jobs inside the worktree")
        command, _candidate_raw = _bound_current_candidate(job, state)
        worktree = Path(command["workdir"])
        destination, parent_identity = _verification_copy_destination(destination, worktree)
        _copy_bound_candidate(worktree, destination)
        try:
            if _identity(destination.parent.lstat()) != parent_identity:
                raise DispatchError("verification copy destination parent changed")
            # The source candidate is still the final authority.  A verifier
            # copy never reconciles ignored drift into that candidate.
            _bound_current_candidate(job, state)
        except (OSError, DispatchError):
            _discard_verification_copy(destination)
            raise DispatchError("candidate changed while creating verification copy") from None
    result = {
        "candidate_sha256": state["result_sha256"],
        "verification_copy": "created",
    }
    if output_format == "text":
        sys.stdout.buffer.write(
            b"Driver verification copy created; no candidate acceptance was recorded.\n"
        )
        sys.stdout.buffer.flush()
    else:
        print_json(result)
    return 0


def _bound_legacy_unknown_result(job: Path, state: dict[str, Any]) -> bytes:
    """Revalidate a V3/V4 historical result without promoting its provenance."""
    if not _legacy_prior_result_is_unknown(state):
        raise DispatchError("dispatch has no unknown legacy result")
    try:
        bound_job = canonical_job(Path(job).resolve(strict=True))
    except OSError as exc:
        raise DispatchError("job directory is unavailable") from exc
    result_path = Path(state["last_success_path"])
    try:
        result_parent = result_path.parent.resolve(strict=True)
    except OSError as exc:
        raise DispatchError("legacy dispatch result path is unavailable") from exc
    if not result_path.is_absolute() or result_parent != bound_job:
        raise DispatchError("legacy dispatch result path is outside this job")
    command = _load_bound_command(bound_job, state, stage_readonly=False)
    command, state = _bound_lifecycle_inputs(bound_job, state, command, read_legacy=True)
    if state["workflow"] != "project" or (
        _project_boundary(command["workdir"]) != state["project_boundary"]
    ):
        raise DispatchError("legacy dispatch result boundary is unavailable")
    schema_paths = _schema_paths(command)
    if schema_paths is None:
        raise DispatchError("dispatch result schema is unavailable")
    raw, info = read_regular(result_path, 1024 * 1024, "dispatch result")
    if digest(raw) != state["last_success_sha256"] or list(_identity(info)) != state["last_success_identity"]:
        raise DispatchError("dispatch result binding changed")
    validator = Path(__file__).with_name("validate-envelope.py")
    checked = [
        subprocess.run(
            [sys.executable, "-I", "-S", "-B", str(validator), str(schema), str(result_path)],
            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            check=False,
        )
        for schema in schema_paths
    ]
    if any(item.returncode != 0 for item in checked):
        raise DispatchError("dispatch result is no longer valid")
    rebound, rebound_info = read_regular(result_path, 1024 * 1024, "dispatch result")
    if rebound != raw or _identity(rebound_info) != _identity(info):
        raise DispatchError("dispatch result binding changed")
    _bound_lifecycle_inputs(bound_job, state, command, read_legacy=True)
    return raw

def _bound_worktree_baseline(state: dict[str, Any], command: dict[str, Any]) -> None:
    """Require the queued worktree fact set immediately before provider launch."""
    expected = state["worktree_baseline"]
    current = _state_worktree_snapshot(state, command["workdir"])
    if expected is None or current is None:
        if state.get("schema_version", CURRENT_STATE_SCHEMA) >= 7:
            _worktree_snapshot(command["workdir"], explain_unsupported=True)
        raise WorktreeBaselineError("queued worktree baseline is unavailable")
    if (
        current["sha256"] != expected["sha256"]
        or current["entries"] != expected["entries"]
    ):
        raise WorktreeBaselineError("queued worktree baseline changed")


def _restart_guard_accepts(
    state: dict[str, Any], *, status: str | None = None,
    elapsed_seconds: float | None = None,
) -> bool:
    """Share the state-only fresh-restart guard with public recovery projection."""
    current_status = state["status"] if status is None else status
    elapsed = float(state["elapsed_seconds"]) if elapsed_seconds is None else elapsed_seconds
    return bool(
        current_status in TERMINAL
        and current_status != "orphaned"
        # A frozen direct-selection record which just failed its final
        # executable/version/help proof cannot become launch authority by
        # creating another attempt.  Keep that local evidence for Codex, but
        # reject recovery before it can stage or mutate the job.
        and state["reason"] != "selection_preflight_failed"
        and elapsed < float(state["max_seconds"])
        and (
            state["workflow"] == "legacy"
            or state["attempt"] < state["max_cycles"]
        )
    )


def _load_bound_command(
    job: Path, state: dict[str, Any], *, stage_readonly: bool,
) -> dict[str, Any]:
    command, raw, identity = load_command(job)
    if digest(raw) != state["command_sha256"] or list(identity) != state["command_identity"]:
        raise DispatchError("dispatch command binding changed")
    stage_sha, stage_identity = _bound_stage(command, readonly=stage_readonly)
    if stage_sha != state["stage_sha256"] or (
        stage_identity is not None and list(stage_identity[:4]) != state["stage_identity"][:4]
    ) or (stage_identity is None) != (state["stage_identity"] is None):
        raise DispatchError("staged prompt binding changed")
    return command


def _load_bound_selection(
    command: dict[str, Any], state: dict[str, Any], *,
    legacy_command_binding: bool = False,
) -> dict[str, Any] | None:
    """Read the frozen selection bytes and bind them to command and state.

    The record is private job state.  Its public JSON contains no executable
    pathname, and a controller never turns it back into an argv[0] string.
    """

    path_value = command["selection_path"]
    if path_value is None:
        if state["selection_sha256"] is not None or state["selection_identity"] is not None:
            raise DispatchError("dispatch selection state binding changed")
        return None
    # V1-V5 predate the duplicate state-level selection fields.  Their bound
    # command still freezes the selection path, digest, and identity, which is
    # sufficient for a read-only result revalidation.  Provider-causing and
    # V6+ paths retain the stricter duplicate state binding.
    if not (
        legacy_command_binding and state["schema_version"] < 6
    ) and (
        state["selection_sha256"] != command["selection_sha256"]
        or state["selection_identity"] != command["selection_identity"]
    ):
        raise DispatchError("dispatch selection state binding changed")
    try:
        raw, info = read_regular(Path(path_value), MAX_COMMAND_BYTES, "dispatch selection")
    except DispatchError:
        raise
    if digest(raw) != command["selection_sha256"] or list(_identity(info)) != command["selection_identity"]:
        raise DispatchError("dispatch selection binding changed")
    try:
        # A direct selection is an immutable dispatch input.  Its raw bytes and
        # identity have just been compared to the command/state bindings; do
        # not reapply a mutable current compatibility matrix to it here.
        record = MODEL_SELECTION.decode_selection_record(raw, frozen=True)
    except (MODEL_SELECTION.CallerError, MODEL_SELECTION.ReviewRequired, MODEL_SELECTION.EvidenceUnavailable) as exc:
        raise DispatchError("dispatch selection is invalid") from exc
    return record


def _bound_lifecycle_inputs(
    job: Path, state: dict[str, Any], command: dict[str, Any] | None = None,
    *, read_legacy: bool = False,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Bind non-provider recovery/finalization inputs before any state write.

    This never writes state or launches a provider, but it does perform the
    bounded local root, selection, schema, and boundary probes shared by status
    projection and the mutating create/finalize/result paths.  Provider launch
    still repeats its final executable and worktree probes.
    """
    if command is None:
        command = _load_bound_command(job, state, stage_readonly=False)
    checked = state
    if checked["schema_version"] < CURRENT_STATE_SCHEMA and not read_legacy:
        checked = _upgrade_legacy_state(checked, command)
    # V3/V4 still carry their own lifecycle copy.  Before those historical
    # bytes can produce a migration approval (or be upgraded under one), bind
    # every immutable overlap to the frozen command.  ``hard_seconds`` is not
    # included: an approved local extend is allowed to change that one limit.
    # V1 has no comparable workflow contract and remains result-only.
    if checked["schema_version"] in {3, 4}:
        for key in ("job_id", "workflow", "max_cycles"):
            if checked[key] != command[key]:
                raise DispatchError("dispatch immutable lifecycle binding changed")
        for key in ("idle_seconds", "max_seconds"):
            if float(checked[key]) != float(command[key]):
                raise DispatchError("dispatch immutable lifecycle binding changed")
    if checked["workdir"] != command["workdir"]:
        raise DispatchError("dispatch worktree root binding changed")
    root = Path(command["workdir"])
    try:
        root_info = root.lstat()
    except OSError as exc:
        raise DispatchError("dispatch worktree root is unavailable") from exc
    if checked["schema_version"] in {9, 10, CURRENT_STATE_SCHEMA}:
        root_identity = _dispatch_root_identity(command["workdir"])
        if (
            root_identity is None
            or root_identity != checked["worktree_root_identity"]
        ):
            raise DispatchError("dispatch worktree root binding changed")
    elif not read_legacy:
        raise DispatchError("legacy dispatch root identity cannot be proved")
    if not stat.S_ISDIR(root_info.st_mode) or stat.S_ISLNK(root_info.st_mode):
        raise DispatchError("dispatch worktree root binding changed")
    try:
        # macOS exposes /var through its documented /private/var alias.  A
        # no-symlink root can legitimately stringify through that alias; all
        # other resolution changes remain a fail-closed boundary drift.
        if MODEL_SELECTION._canonical_executable_path(os.path.realpath(root)) != (
            MODEL_SELECTION._canonical_executable_path(command["workdir"])
        ):
            raise DispatchError("dispatch worktree root binding changed")
    except OSError as exc:
        raise DispatchError("dispatch worktree root is unavailable") from exc
    if not _worktree_symlink_boundary(command["workdir"]):
        raise DispatchError("dispatch worktree symlink boundary changed")
    _load_bound_selection(
        command, checked, legacy_command_binding=read_legacy,
    )
    if checked["schema_version"] in {9, 10, CURRENT_STATE_SCHEMA}:
        _bound_schemas(command, checked)
    elif not read_legacy or _schema_paths(command) is None:
        raise DispatchError("legacy dispatch schema binding cannot be proved")
    if checked["workflow"] == "project" and (
        _project_boundary(command["workdir"]) != checked["project_boundary"]
    ):
        raise DispatchError("project worktree boundary changed")
    if checked.get("provider_scope_path") is not None:
        scope_path = Path(checked["provider_scope_path"])
        raw_scope, scope_info = read_regular(scope_path, MAX_COMMAND_BYTES, "provider scope")
        if digest(raw_scope) != checked["provider_scope_sha256"]:
            raise DispatchError("provider scope file changed since dispatch")
        if list(_identity(scope_info)) != checked["provider_scope_identity"]:
            raise DispatchError("provider scope file identity changed since dispatch")
        try:
            scope = _parse_provider_scope(raw_scope)
        except ValueError as exc:
            raise DispatchError(f"invalid provider scope: {exc}") from exc
        readable_manifest = _scan_readable_worktree(command["workdir"])
        manifest_sha = _manifest_digest(readable_manifest)
        _validate_scope_against_worktree(scope, command["workdir"], readable_manifest)
        selected_manifest = _build_selected_content_manifest(command["workdir"], scope)
        selected_sha = _selected_content_digest(selected_manifest)
        policy_sha = _canonical_digest(scope)
        transmission_sha = _compute_transmission_sha256(policy_sha, manifest_sha, selected_sha)
        if transmission_sha != checked["transmission_sha256"]:
            raise DispatchError("worktree scope transmission binding changed")
    return command, checked


def _reprobe_direct_selection(
    command: dict[str, Any], state: dict[str, Any], argv: list[str],
) -> tuple[str, dict[str, Any]] | None:
    """Prove direct selection compatibility immediately before provider launch."""

    record = _load_bound_selection(command, state)
    if record is None:
        return None
    mode = record["selection_mode"]
    if mode not in {"exact-model", "model-effort"}:
        return None
    if not _selection_launch_is_authorized(record):
        # A current exact-version V2 record is mechanically sufficient.  V2
        # drift remains historical evidence only; drift needs a bound V3 Codex
        # disposition before any provider-causing lifecycle.
        raise DispatchError("dispatch direct selection lacks approved compatibility disposition")
    if argv.count("--model") != 1:
        raise DispatchError("dispatch direct selection model argument is invalid")
    model_index = argv.index("--model")
    if model_index + 1 >= len(argv) or argv[model_index + 1] != record["resolved_agy_model"]:
        raise DispatchError("dispatch direct selection model argument drifted")
    # The worker does not support an effort flag; selection resolves effort into
    # one immutable compound model slug.  A new one would be a fallback surface.
    if "--effort" in argv:
        raise DispatchError("dispatch direct selection effort fallback is invalid")
    try:
        # Keep both facts through the subsequent bounded worktree scan.  The
        # final confirmation belongs after that scan, immediately before the
        # provider process is created; otherwise an A->B replacement can make
        # a successfully probed A authorize an unprobed B.
        return MODEL_SELECTION.reprobe_selection_record(record)
    except (MODEL_SELECTION.CallerError, MODEL_SELECTION.ReviewRequired, MODEL_SELECTION.EvidenceUnavailable) as exc:
        raise SelectionPreflightError("dispatch direct selection reprobe failed") from exc


def _terminate(process: subprocess.Popen[bytes]) -> int:
    # The leader can exit while a descendant still owns the stream or performs a
    # late side effect.  Signal the recorded session even in that case.
    signalled = False
    try:
        os.killpg(process.pid, signal.SIGTERM)
        signalled = True
    except (ProcessLookupError, PermissionError):
        pass
    if signalled:
        deadline = time.monotonic() + TERM_GRACE
        while time.monotonic() < deadline:
            try:
                os.killpg(process.pid, 0)
            except ProcessLookupError:
                break
            except PermissionError:
                pass
            time.sleep(0.02)
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        pass
    try:
        process.wait(timeout=1.0)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()
    return process.returncode


def _event(line: bytes) -> tuple[bool, str | None, str | None]:
    if not line or len(line) > MAX_EVENT_BYTES:
        return False, None, None
    try:
        value = json.loads(
            line.decode("utf-8", "strict"), object_pairs_hook=_duplicates,
            parse_constant=_invalid_json_constant,
        )
    except (UnicodeError, json.JSONDecodeError, DispatchError, RecursionError):
        return False, None, None
    if not isinstance(value, dict):
        return False, None, None
    event = value.get("event")
    if event not in {"init", "step_update", "result"}:
        return False, None, None
    if event == "init" and not isinstance(value.get("init"), dict):
        return False, None, None
    if event == "step_update" and not isinstance(value.get("step_update"), dict):
        return False, None, None
    if event == "result" and not isinstance(value.get("result"), dict):
        return False, None, None
    conversation = value.get("conversation_id")
    if conversation is None and event == "result":
        conversation = value["result"].get("conversation_id")
    if conversation is not None and (
        not isinstance(conversation, str) or CONVERSATION_RE.fullmatch(conversation) is None
    ):
        conversation = None
    return True, conversation, event


def _classify_stderr(path: Path, version: str, returncode: int) -> str:
    if returncode == 0:
        return "empty_output"
    try:
        raw = path.read_bytes()
    except OSError:
        return "agy_failed_unclassified"
    lines = {line.strip() for line in raw.splitlines() if line.strip()}
    if any(b"permission that headless mode cannot prompt for" in line for line in lines):
        return "permission_required"
    signatures = EXACT_FAILURE_LINES.get(version, {})
    matches = {reason for signature, reason in signatures.items() if signature in lines}
    return matches.pop() if len(matches) == 1 else "agy_failed_unclassified"


def _terminal_result(stream: Path, *, strict: bool = False) -> dict[str, Any] | None:
    result: dict[str, Any] | None = None
    init_conversation: str | None = None
    saw_init = False
    saw_terminal = False
    try:
        with stream.open("rb") as handle:
            for raw in handle:
                if len(raw) > MAX_EVENT_BYTES or not raw.endswith(b"\n"):
                    return None
                try:
                    event = json.loads(
                        raw.decode("utf-8", "strict"), object_pairs_hook=_duplicates,
                        parse_constant=_invalid_json_constant,
                    )
                except (UnicodeError, json.JSONDecodeError, DispatchError, RecursionError):
                    if strict:
                        return None
                    continue
                if not isinstance(event, dict):
                    if strict:
                        return None
                    continue
                kind = event.get("event")
                structurally_valid = (
                    (kind == "init" and isinstance(event.get("init"), dict))
                    or (kind == "step_update" and isinstance(event.get("step_update"), dict))
                    or (kind == "result" and isinstance(event.get("result"), dict))
                )
                if not structurally_valid:
                    if strict:
                        return None
                    continue
                if saw_terminal:
                    return None
                if kind == "init":
                    if saw_init:
                        return None
                    init_conversation = event.get("conversation_id")
                    if strict and init_conversation is not None and (
                        not isinstance(init_conversation, str)
                        or CONVERSATION_RE.fullmatch(init_conversation) is None
                    ):
                        return None
                    saw_init = True
                elif not saw_init:
                    return None
                if kind == "result":
                    result_conversation = event["result"].get("conversation_id")
                    if strict and result_conversation is not None and (
                        not isinstance(result_conversation, str)
                        or CONVERSATION_RE.fullmatch(result_conversation) is None
                    ):
                        return None
                    if strict and init_conversation is not None and result_conversation is not None and result_conversation != init_conversation:
                        return None
                    saw_terminal = True
                    result = event["result"]
    except OSError:
        return None
    if not saw_terminal or not isinstance(result, dict):
        return None
    return result


def _quota_terminal_failure(stream: Path, version: str) -> tuple[str, int | None] | None:
    if version != "1.1.13":
        return None
    result = _terminal_result(stream, strict=True)
    if result is None or set(result) != QUOTA_RESULT_FIELDS:
        return None
    if result.get("status") != "ERROR" or result.get("response") != "":
        return None
    conversation = result.get("conversation_id")
    if not isinstance(conversation, str) or CONVERSATION_RE.fullmatch(conversation) is None:
        return None
    if (
        type(result.get("duration_seconds")) not in (int, float)
        or not math.isfinite(result["duration_seconds"])
        or result["duration_seconds"] < 0
    ):
        return None
    if type(result.get("num_turns")) is not int or result["num_turns"] < 0:
        return None
    if not isinstance(result.get("usage"), dict) or not isinstance(result.get("json_schema"), dict):
        return None
    error = result.get("error")
    if not isinstance(error, str) or len(error) > 256:
        return None
    match = QUOTA_ERROR_1_1_13_RE.fullmatch(error)
    if match is None:
        return None
    hours = int(match.group("hours") or 0)
    minutes = int(match.group("minutes") or 0)
    seconds = int(match.group("seconds") or 0)
    retry = hours * 3600 + minutes * 60 + seconds
    if minutes >= 60 or seconds >= 60 or not (1 <= retry <= MAX_PROVIDER_RETRY_SECONDS):
        retry = None
    return "provider_quota_exhausted", retry


def _validate_terminal_envelope(
    stream: Path, envelope: Path, provider_schema: Path, canonical_schema: Path,
) -> tuple[tuple[str, tuple[int, int, int, int, int]] | None, str | None, str | None]:
    """Keep framing, provider status, extraction, and canonical validation distinct."""
    result = _terminal_result(stream, strict=True)
    if result is None:
        return None, None, "framing"
    outer_status = result.get("status")
    if not isinstance(outer_status, str) or outer_status not in {"SUCCESS", "ERROR", "CANCELED", "CANCELLED"}:
        return None, None, "outer_status"
    outer_status = "CANCELLED" if outer_status in {"CANCELED", "CANCELLED"} else outer_status
    value = result.get("structured_output")
    if not isinstance(value, dict):
        return None, outer_status, "missing_structured_output"
    # The provider may omit exactly these ergonomic report-only arrays.  Every
    # other required field and every extra field remain schema failures.
    value = dict(value)
    for field in ("commands_run", "tests_run"):
        value.setdefault(field, [])
    raw = json.dumps(value, ensure_ascii=True, indent=2).encode("ascii") + b"\n"
    if len(raw) > 1024 * 1024:
        return None, outer_status, "schema_rejection"
    descriptor = _ensure_new_private(envelope)
    try:
        os.write(descriptor, raw)
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    validator = Path(__file__).with_name("validate-envelope.py")
    provider_checked = subprocess.run(
        [sys.executable, "-I", "-S", "-B", str(validator), str(provider_schema), str(envelope)],
        stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        check=False,
    )
    canonical_checked = subprocess.run(
        [sys.executable, "-I", "-S", "-B", str(validator), str(canonical_schema), str(envelope)],
        stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        check=False,
    )
    if provider_checked.returncode != 0 or canonical_checked.returncode != 0:
        with contextlib.suppress(OSError):
            envelope.unlink()
        return None, outer_status, "schema_rejection"
    try:
        rebound, info = read_regular(envelope, 1024 * 1024, "dispatch result")
    except DispatchError:
        return None, outer_status, "binding_failure"
    if rebound != raw:
        return None, outer_status, "binding_failure"
    return (digest(raw), _identity(info)), outer_status, None


def controller(job: Path, ownership_fd: int) -> int:
    stop_signal: int | None = None
    process: subprocess.Popen[bytes] | None = None
    started_mono: float | None = None
    runtime_end_mono: float | None = None
    runtime_frozen = False

    def interrupted(number: int, _frame: Any) -> None:
        nonlocal stop_signal
        if stop_signal is None:
            stop_signal = number

    prior_handlers = {
        number: signal.getsignal(number)
        for number in (signal.SIGHUP, signal.SIGINT, signal.SIGTERM)
    }
    for number in prior_handlers:
        signal.signal(number, interrupted)
    try:
      with inherited_lifecycle_lock(job, ownership_fd):
        # Claim the queued attempt under one state lock.  A cancel can land
        # between process spawn and this point, but never between this exact
        # queued observation and controller ownership publication.
        cancelled_before_claim = False
        with state_lock(job):
            state, prior_raw, _sha = load_state(job)
            if state["status"] == "cancel-requested" and state["cancel_requested"]:
                cancelled_before_claim = True
            elif state["status"] != "queued" or state["cancel_requested"]:
                raise DispatchError("dispatch is not queued")
            else:
                # A queued state with this exact PID is the startup handshake; it
                # means the private controller is alive, not that a provider
                # process exists or that provider runtime has started.
                state, prior_raw, _sha = _transition_locked(job, state, prior_raw, {
                    "controller_pid": os.getpid(),
                })
        if cancelled_before_claim:
            _terminalize_owned(
                job, state, status="cancelled", reason="cancelled",
                exit_code=EXIT_BY_REASON["cancelled"], expected_controller_pid=None,
            )
            return EXIT_BY_REASON["cancelled"]
        feedback: Path | None = None
        schema_paths: tuple[Path, Path] | None = None
        try:
            command = _load_bound_command(job, state, stage_readonly=False)
            MODEL_SELECTION.ACTIVE_CHILD_ENV = list(command["provider_env"])
            _load_bound_selection(command, state)
            schema_paths = _bound_schemas(command, state)
            if not _worktree_symlink_boundary(command["workdir"]):
                raise DispatchError("dispatch worktree symlink boundary changed")
            if state["workflow"] == "project":
                if _project_boundary(command["workdir"]) != state["project_boundary"]:
                    raise DispatchError("project worktree boundary changed")
            if state["attempt_origin"] == "conversation-continue":
                feedback = _bound_verification(job, state)
                if feedback is None:
                    raise DispatchError("project continuation has no verification feedback")
                command, _candidate_raw = _bound_current_candidate(job, state)
        except (OSError, DispatchError):
            terminal, _raw, _sha = _terminalize_owned(
                job, state, status="failed", reason="status_unavailable",
                exit_code=EXIT_BY_REASON["status_unavailable"],
                failure_stage="binding_failure", expected_controller_pid=os.getpid(),
            )
            return int(terminal["exit_code"])
        attempt = state["attempt"]
        stream_path, stderr_path, envelope_path = _attempt_paths(job, attempt)
        stdout_fd = -1; stderr_fd = -1
        # ``elapsed_seconds`` is provider execution time.  The strict local
        # command/root/schema/worktree proofs below happen before a provider
        # process exists, so they cannot consume the provider hard, maximum,
        # or idle budgets.  This is especially important when a safe platform
        # Git fallback makes those bounded probes materially slower.
        elapsed = float(state["attempt_base_elapsed"])
        try:
            stdout_fd = _ensure_new_private(stream_path)
            stderr_fd = _ensure_new_private(stderr_path)
            _stage(command, True)
            _load_bound_command(job, state, stage_readonly=True)
            _load_bound_selection(command, state)
            schema_paths = _bound_schemas(command, state)
        except (OSError, DispatchError):
            if stdout_fd >= 0: os.close(stdout_fd)
            if stderr_fd >= 0: os.close(stderr_fd)
            with contextlib.suppress(OSError): _stage(command, False)
            terminal, _raw, _sha = _terminalize_owned(
                job, state, status="failed", reason="status_unavailable",
                exit_code=EXIT_BY_REASON["status_unavailable"],
                failure_stage="binding_failure", expected_controller_pid=os.getpid(),
            )
            return int(terminal["exit_code"])
        argv = list(command["argv"])
        if state["attempt_origin"] in {"conversation-resume", "conversation-continue"}:
            conversation = state["conversation_id"]
            if not isinstance(conversation, str):
                raise DispatchError("resume has no conversation")
            print_index = argv.index("--print")
            prefix = ["--conversation", conversation]
            prompt = command["resume_prompt"]
            if state["attempt_origin"] == "conversation-continue":
                if feedback is None:
                    raise DispatchError("project continuation feedback was not prevalidated")
                if state.get("provider_scope_path") is None:
                    prefix.extend(["--add-dir", str(feedback.parent)])
                    prompt = command["continue_prompt"] + f" Feedback file: '{feedback}'."
                else:
                    feedback_raw, _feedback_info = read_regular(
                        feedback, MAX_VERIFICATION_BYTES, "verification feedback",
                        allowed_modes=(0o400,),
                    )
                    prompt = (
                        command["continue_prompt"]
                        + " Driver verification JSON follows inline:\n"
                        + feedback_raw.decode("utf-8", "strict")
                    )
            argv[print_index + 1] = prompt
            argv[print_index:print_index] = prefix
        selector = selectors.DefaultSelector()
        buffers = {"stdout": bytearray(), "stderr": bytearray()}
        sizes = {"stdout": 0, "stderr": 0}
        next_notice = 0.0
        reason: str | None = None
        limit_kind: str | None = None
        failure_stage: str | None = None
        saw_init = False
        saw_terminal = False
        stage_dir: Path | None = None
        scope: dict[str, Any] | None = None
        selected_manifest: list[dict[str, Any]] | None = None
        stage_manifest_sha: str | None = None
        stage_identity: tuple[int, int, int, int, int] | None = None
        narrow_source_snapshot: dict[str, Any] | None = None

        def controller_transition(updates: dict[str, Any]) -> bool:
            """Do not turn a concurrent approved control into a controller crash."""
            nonlocal state, prior_raw
            try:
                state, prior_raw, _sha = transition(job, state, prior_raw, updates)
                return True
            except DispatchError as exc:
                if str(exc) != "dispatch state changed before transition":
                    raise
                current, current_raw, _current_sha = read_state_snapshot(job)
                if current["attempt"] != state["attempt"]:
                    raise DispatchError("dispatch attempt changed during control")
                state, prior_raw = current, current_raw
                return False

        def refresh_control_snapshot() -> None:
            """Reload an approved control transition before using live limits."""
            nonlocal state, prior_raw
            current, current_raw, _current_sha = read_state_snapshot(job)
            if current_raw == prior_raw:
                return
            if (
                current["previous_state_sha256"] != digest(prior_raw)
                or current["sequence"] != state["sequence"] + 1
                or current["attempt"] != state["attempt"]
            ):
                raise DispatchError("dispatch changed during provider control")
            state, prior_raw = current, current_raw

        def drain_reaped_streams() -> None:
            """Bind bytes emitted before reap without treating them as activity."""
            nonlocal reason, failure_stage
            for key in list(selector.get_map().values()):
                name = key.data
                while True:
                    try:
                        chunk = os.read(key.fd, 65536)
                    except BlockingIOError:
                        break
                    except OSError:
                        reason = "status_unavailable"
                        failure_stage = "binding_failure"
                        return
                    if not chunk:
                        try:
                            selector.unregister(key.fileobj)
                            key.fileobj.close()
                        except OSError:
                            reason = "status_unavailable"
                            failure_stage = "binding_failure"
                        break
                    sizes[name] += len(chunk)
                    if sizes[name] > MAX_STREAM_BYTES:
                        reason = "output_oversized"
                        return
                    try:
                        os.write(stdout_fd if name == "stdout" else stderr_fd, chunk)
                    except OSError:
                        reason = "status_unavailable"
                        failure_stage = "binding_failure"
                        return
        try:
            try:
                # Re-read the frozen record and re-probe *after* all controller
                # mutations and immediately before the provider-causing launch.
                # argv[0] stays the portable public spelling while executable=
                # pins the safe, freshly-probed target for this one process.
                executable_binding = _reprobe_direct_selection(command, state, argv)
                _bound_worktree_baseline(state, command)
                if not _worktree_symlink_boundary(command["workdir"]):
                    raise DispatchError("dispatch worktree symlink boundary changed")
                launch_cwd = command["workdir"]
                if state.get("provider_scope_path") is not None:
                    scope_path = Path(state["provider_scope_path"])
                    raw_scope, scope_info = read_regular(scope_path, MAX_COMMAND_BYTES, "provider scope")
                    if digest(raw_scope) != state["provider_scope_sha256"]:
                        raise DispatchError("provider scope file changed since dispatch")
                    if list(_identity(scope_info)) != state["provider_scope_identity"]:
                        raise DispatchError("provider scope file identity changed since dispatch")
                    scope = _parse_provider_scope(raw_scope)
                    readable_manifest = _scan_readable_worktree(command["workdir"])
                    manifest_sha = _manifest_digest(readable_manifest)
                    _validate_scope_against_worktree(scope, command["workdir"], readable_manifest)
                    selected_manifest = _build_selected_content_manifest(command["workdir"], scope)
                    selected_sha = _selected_content_digest(selected_manifest)
                    policy_sha = _canonical_digest(scope)
                    transmission_sha = _compute_transmission_sha256(policy_sha, manifest_sha, selected_sha)
                    if transmission_sha != state["transmission_sha256"]:
                        raise DispatchError("worktree scope transmission binding changed")
                    narrow_source_snapshot = _worktree_snapshot(command["workdir"])
                    stage_dir = job / f"stage-{attempt:03d}"
                    stage_identity, stage_manifest_sha = _materialize_stage(command["workdir"], stage_dir, scope, selected_manifest)
                    launch_cwd = str(stage_dir)
                # The prior attempt budget is still a hard stop, but bounded
                # controller-local proofs do not become a provider timeout.
                # Commit the running state/CAS boundary after slow preflight.
                # The provider hard/runtime lease starts at the invocation
                # boundary, immediately before Popen.  The value is committed
                # only after Popen succeeds, so failed local creation still
                # has no provider runtime.  This leaves no post-Popen window
                # in which a child can schedule work beyond the hard limit.
                # The final executable confirmation remains immediately
                # adjacent to the provider-causing call.
                if stop_signal is not None:
                    reason = "interrupted"
                    returncode = 128 + stop_signal
                elif elapsed >= float(state["max_seconds"]):
                    reason, limit_kind = "hard_deadline_exceeded", "max-runtime"
                    returncode = EXIT_BY_REASON[reason]
                elif elapsed >= float(state["hard_seconds"]):
                    reason, limit_kind = "hard_deadline_exceeded", "hard"
                    returncode = EXIT_BY_REASON[reason]
                else:
                    # Linearize cancellation against the provider-causing
                    # operation.  The final executable confirmation and Popen
                    # stay in this same short critical section: cancellation
                    # before it wins without a provider; cancellation after
                    # it is necessarily a post-launch request.
                    with state_lock(job):
                        current, current_raw, _current_sha = load_state(job)
                        if (
                            current["attempt"] != state["attempt"]
                            or current["controller_pid"] != os.getpid()
                            or current["status"] in TERMINAL
                        ):
                            raise DispatchError("dispatch changed before provider launch")
                        state, prior_raw = current, current_raw
                        if state["cancel_requested"]:
                            reason = "cancelled"
                            returncode = EXIT_BY_REASON[reason]
                        else:
                            running_updates = {
                                "status": "running", "controller_pid": os.getpid(),
                                "started_epoch": None, "last_progress_epoch": None,
                                "stream_path": str(stream_path), "stderr_path": str(stderr_path),
                                "next_action": "wait",
                            }
                            if stage_dir is not None:
                                running_updates.update({
                                    "provider_stage_path": str(stage_dir),
                                    "provider_stage_identity": list(stage_identity) if stage_identity is not None else None,
                                    "provider_stage_manifest_sha256": stage_manifest_sha,
                                })
                            state, prior_raw, _sha = _transition_locked(job, state, prior_raw, running_updates)
                            exact_executable = None
                            if executable_binding is not None:
                                try:
                                    exact_executable = MODEL_SELECTION.confirm_executable_binding(
                                        *executable_binding,
                                    )
                                except MODEL_SELECTION.EvidenceUnavailable as exc:
                                    raise SelectionPreflightError(
                                        "dispatch direct selection launch binding changed",
                                    ) from exc
                            launch_mono = time.monotonic()
                            process = subprocess.Popen(
                                argv,
                                executable=exact_executable,
                                cwd=launch_cwd,
                                stdin=subprocess.DEVNULL,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                env=MODEL_SELECTION.child_environment(command["provider_env"]),
                                start_new_session=True,
                                preexec_fn=lambda: os.umask(int(command["child_umask"], 8)),
                            )
                            started_mono = launch_mono
                            heartbeat_mono = started_mono
                            next_notice = started_mono + float(command["notice_seconds"])
                            state, prior_raw, _sha = _transition_locked(
                                job, state, prior_raw, {"started_epoch": time.time()},
                            )
            except MODEL_SELECTION.ProbeInterrupted as exc:
                # model_selection owns and reaps its short-lived probe group;
                # the controller owns the terminal dispatch projection.
                stop_signal = exc.signal_number
                reason = "interrupted"
                returncode = 128 + exc.signal_number
            except SelectionPreflightError:
                reason = "selection_preflight_failed"
                failure_stage = "selection_preflight"
                returncode = EXIT_BY_REASON[reason]
            except WorktreeBaselineError as exc:
                reason = "resolve_undo_present" if isinstance(exc, ResolveUndoPresentError) else "status_unavailable"
                failure_stage = "binding_failure"
                returncode = EXIT_BY_REASON[reason]
            except DispatchError:
                reason = "status_unavailable"
                returncode = EXIT_BY_REASON["status_unavailable"]
            except OSError:
                # A legacy tier deliberately reaches this point even when agy is
                # absent.  Publish a terminal, sanitized dispatch failure rather
                # than leaking an interpreter traceback or leaving a queued job.
                reason = "agy_failed_unclassified"
                returncode = 127
            else:
                if process is not None:
                    try:
                        assert process.stdout is not None and process.stderr is not None
                        for name, pipe in (("stdout", process.stdout), ("stderr", process.stderr)):
                            os.set_blocking(pipe.fileno(), False)
                            selector.register(pipe, selectors.EVENT_READ, name)
                    except (OSError, DispatchError):
                        reason = "status_unavailable"
                        failure_stage = "binding_failure"
            # Pipe EOF is the completion observation.  Do not poll/reap the leader
            # before process-group closure; its PID reserves the group identifier.
            while process is not None and selector.get_map() and reason is None:
                now_mono = time.monotonic()
                elapsed = float(state["attempt_base_elapsed"]) + now_mono - started_mono
                try:
                    refresh_control_snapshot()
                except DispatchError:
                    reason = "status_unavailable"
                    break
                if state["cancel_requested"] or stop_signal is not None:
                    reason = "cancelled" if stop_signal is None else "interrupted"
                    break
                if elapsed >= state["max_seconds"]:
                    reason, limit_kind = "hard_deadline_exceeded", "max-runtime"
                    break
                if elapsed >= state["hard_seconds"]:
                    reason, limit_kind = "hard_deadline_exceeded", "hard"
                    break
                if now_mono - heartbeat_mono >= float(state["idle_seconds"]):
                    reason, limit_kind = "idle_timeout", "idle"
                    break
                if now_mono >= next_notice:
                    try:
                        controller_transition({
                            "notice_count": state["notice_count"] + 1,
                            "elapsed_seconds": elapsed,
                        })
                    except DispatchError:
                        reason = "status_unavailable"
                        failure_stage = "binding_failure"
                        break
                    next_notice += float(command["notice_seconds"])
                    if sys.stderr.isatty():
                        print(
                            f"agy-worker: still running; elapsed={int(elapsed)}s "
                            f"progress={state['progress_count']}", file=sys.stderr, flush=True,
                        )
                try:
                    # A fixed poll can return after a nearer hard, maximum,
                    # idle, or notice boundary.  Bound the kernel wait to the
                    # first controller-owned clock, then reload any extension
                    # and classify the resampled time before consuming ready
                    # bytes as semantic progress.
                    wait_until = min(
                        started_mono
                        + max(0.0, float(state["max_seconds"]) - float(state["attempt_base_elapsed"])),
                        started_mono
                        + max(0.0, float(state["hard_seconds"]) - float(state["attempt_base_elapsed"])),
                        heartbeat_mono + float(state["idle_seconds"]),
                        next_notice,
                    )
                    wait_seconds = min(CONTROL_POLL, max(0.0, wait_until - now_mono))
                    events = selector.select(wait_seconds)
                except OSError:
                    reason = "status_unavailable"
                    failure_stage = "binding_failure"
                    break
                post_wait_mono = time.monotonic()
                try:
                    refresh_control_snapshot()
                except DispatchError:
                    reason = "status_unavailable"
                    failure_stage = "binding_failure"
                    break
                elapsed = (
                    float(state["attempt_base_elapsed"])
                    + post_wait_mono - started_mono
                )
                if state["cancel_requested"] or stop_signal is not None:
                    reason = "cancelled" if stop_signal is None else "interrupted"
                    break
                if elapsed >= float(state["max_seconds"]):
                    reason, limit_kind = "hard_deadline_exceeded", "max-runtime"
                    break
                if elapsed >= float(state["hard_seconds"]):
                    reason, limit_kind = "hard_deadline_exceeded", "hard"
                    break
                if post_wait_mono - heartbeat_mono >= float(state["idle_seconds"]):
                    reason, limit_kind = "idle_timeout", "idle"
                    break
                for key, _mask in events:
                    name = key.data
                    try:
                        chunk = os.read(key.fd, 65536)
                    except BlockingIOError:
                        continue
                    except OSError:
                        reason = "status_unavailable"
                        failure_stage = "binding_failure"
                        break
                    if not chunk:
                        try:
                            selector.unregister(key.fileobj)
                            key.fileobj.close()
                        except OSError:
                            reason = "status_unavailable"
                            failure_stage = "binding_failure"
                            break
                        continue
                    sizes[name] += len(chunk)
                    if sizes[name] > MAX_STREAM_BYTES:
                        reason = "output_oversized"
                        break
                    try:
                        os.write(stdout_fd if name == "stdout" else stderr_fd, chunk)
                    except OSError:
                        reason = "status_unavailable"
                        failure_stage = "binding_failure"
                        break
                    if name == "stdout" and reason is None:
                        buffers[name].extend(chunk)
                        while b"\n" in buffers[name]:
                            line, _, remainder = buffers[name].partition(b"\n")
                            buffers[name] = bytearray(remainder)
                            if len(line) > MAX_EVENT_BYTES:
                                reason = "output_oversized"
                                break
                            valid, conversation, event_kind = _event(line)
                            if valid:
                                if saw_terminal or (event_kind == "init" and saw_init) or (
                                    event_kind != "init" and not saw_init
                                ):
                                    reason = "invalid_envelope"
                                    failure_stage = "framing"
                                    break
                                if event_kind == "init":
                                    saw_init = True
                                elif event_kind == "result":
                                    saw_terminal = True
                                heartbeat_mono = time.monotonic()
                                updates: dict[str, Any] = {
                                    "progress_count": state["progress_count"] + 1,
                                    "last_progress_epoch": time.time(),
                                    "elapsed_seconds": float(state["attempt_base_elapsed"]) + heartbeat_mono - started_mono,
                                    "last_activity": (
                                        "provider_initialized" if event_kind == "init"
                                        else "progress_signal" if event_kind == "step_update"
                                        else "terminal_received"
                                    ),
                                }
                                if conversation is not None:
                                    if state["conversation_id"] not in {None, conversation}:
                                        reason = "status_unavailable"
                                        break
                                    updates["conversation_id"] = conversation
                                    updates["resume_available"] = True
                                try:
                                    controller_transition(updates)
                                except DispatchError:
                                    reason = "status_unavailable"
                                    failure_stage = "binding_failure"
                                    break
                        if len(buffers[name]) > MAX_EVENT_BYTES:
                            # A newline-free oversized frame cannot be safely
                            # resynchronized.  It is neither a heartbeat nor a
                            # candidate terminal result.
                            reason = "output_oversized"
                    if reason is not None:
                        break
                if reason is not None:
                    break
            if process is not None:
                # The candidate worktree binding below is taken only after the
                # provider process group has been terminated and reaped.  The
                # controller-owned stream artifacts are flushed afterward.
                # Freeze first: fsync, envelope parsing, and reconciliation
                # are controller-local work and must not keep the provider
                # clock or extension window alive.
                returncode = _terminate(process)
                process = None
                runtime_end_mono = time.monotonic()
                # A hard/max boundary stops semantic event processing, but a
                # complete terminal frame already present in the reaped pipes
                # remains bounded provider evidence.  Drain it without
                # incrementing progress or moving the heartbeat.
                drain_reaped_streams()
                assert started_mono is not None
                elapsed = float(state["attempt_base_elapsed"]) + max(
                    0.0, runtime_end_mono - started_mono,
                )
                state, prior_raw, _sha, frozen_limit = _freeze_reaped_runtime(
                    job, state["attempt"], os.getpid(), elapsed,
                )
                runtime_frozen = True
                if reason == "hard_deadline_exceeded":
                    # A valid extension may have landed after this controller
                    # observed its old limit but before the reaped-runtime CAS.
                    # The frozen locked limit is authoritative in either
                    # direction; do not retain a stale timeout projection.
                    if frozen_limit is None:
                        reason, limit_kind = None, None
                    else:
                        reason, limit_kind = "hard_deadline_exceeded", frozen_limit
                elif reason is None and frozen_limit is not None:
                    reason, limit_kind = "hard_deadline_exceeded", frozen_limit
            try:
                os.fsync(stdout_fd)
                os.fsync(stderr_fd)
            except OSError:
                reason = "status_unavailable"
                failure_stage = "binding_failure"
            result_binding: tuple[str, tuple[int, int, int, int, int]] | None = None
            outer_status: str | None = None
            provider_retry_after: int | None = None
            provider_retry_observed: float | None = None
            # A deadline is a controller fact, not a reason to discard a
            # terminal report already emitted by the bounded provider.  Parse
            # that report for candidate/provenance evidence, but never let its
            # outer SUCCESS/ERROR/CANCELLED disposition publish past the
            # frozen deadline.  Cancellation and binding failures retain their
            # existing fail-closed precedence and do not enter this path.
            if reason in {None, "hard_deadline_exceeded"}:
                if reason is None:
                    terminal_failure = _quota_terminal_failure(
                        stream_path,
                        command["agy_version"] if command["agy_version_observed"] else "",
                    )
                    if terminal_failure is not None:
                        reason, provider_retry_after = terminal_failure
                        outer_status = "ERROR"
                        # The exact 1.1.13 quota terminal has a valid outer ERROR
                        # fact but intentionally carries no structured report.
                        # Preserve both facts without treating quota as a report.
                        failure_stage = "missing_structured_output"
                        if provider_retry_after is not None:
                            provider_retry_observed = time.time()
                if reason in {None, "hard_deadline_exceeded"} and sizes["stdout"] == 0:
                    if reason is None:
                        reason = (
                            _classify_stderr(stderr_path, command["agy_version"], returncode)
                            if returncode != 0 else "empty_output"
                        )
                elif reason in {None, "hard_deadline_exceeded"}:
                    try:
                        if schema_paths is None:
                            raise DispatchError("dispatch schema binding is unavailable")
                        schema_paths = _bound_schemas(command, state)
                        result_binding, outer_status, failure_stage = _validate_terminal_envelope(
                            stream_path, envelope_path, schema_paths[0], schema_paths[1],
                        )
                        if result_binding is None and reason is None:
                            reason = "invalid_envelope"
                        elif reason is None and outer_status == "ERROR":
                            reason = "provider_terminal_error"
                        elif reason is None and outer_status == "CANCELLED":
                            reason = "provider_terminal_cancelled"
                    except DispatchError:
                        # A binding/schema failure is security-relevant even
                        # when a deadline was observed.  Do not preserve a
                        # candidate whose terminal bytes could not be bound.
                        reason = "status_unavailable"
                        result_binding = None
                        failure_stage = "binding_failure"
            boundary_failed = False
            if command["workflow"] == "project":
                try:
                    if _project_boundary(command["workdir"]) != state["project_boundary"]:
                        raise DispatchError("project worktree boundary changed")
                except DispatchError:
                    boundary_failed = True
                    reason = "status_unavailable"
                    result_binding = None
                    failure_stage = "binding_failure"
            # One blocked completion snapshot linearizes terminal state against
            # late HUP/INT/TERM just as the foreground result publisher does.
            watched = tuple(prior_handlers)
            signal.pthread_sigmask(signal.SIG_BLOCK, watched)
            pending = signal.sigpending()
            completion_signal = stop_signal
            for candidate in watched:
                if candidate in pending or candidate == stop_signal:
                    completion_signal = candidate
                    break
            if completion_signal is not None:
                stop_signal = completion_signal
                reason = "interrupted"
                result_binding = None
                failure_stage = None
            if reason is None:
                final_status, exit_code = "succeeded", 0
                result_path: str | None = str(envelope_path)
            else:
                final_status = "cancelled" if reason in {"cancelled", "interrupted"} else "failed"
                if reason == "provider_terminal_cancelled":
                    final_status = "cancelled"
                exit_code = 128 + stop_signal if stop_signal is not None else EXIT_BY_REASON[reason]
                result_path = str(envelope_path) if result_binding is not None else None
            cleanup_failed = False
            reconciliation_manifest_sha: str | None = None
            if stage_dir is not None and stage_dir.exists():
                try:
                    if (
                        narrow_source_snapshot is None
                        or _worktree_snapshot(command["workdir"]) != narrow_source_snapshot
                    ):
                        raise DispatchError(
                            "source worktree changed while the narrow provider stage was active"
                        )
                    mutations, op_manifest = _scan_stage_mutations(stage_dir, scope, selected_manifest)
                    if result_binding is not None and outer_status in {
                        "SUCCESS", "ERROR", "CANCELLED",
                    }:
                        reconciliation_manifest_sha = _reconcile_stage_to_source(
                            command["workdir"], stage_dir, mutations, job,
                        )
                        if _build_selected_content_manifest(
                            command["workdir"], scope,
                        ) != _build_selected_content_manifest(
                            stage_dir, scope, is_stage=True,
                        ):
                            raise DispatchError(
                                "source reconciliation does not match the provider stage"
                            )
                    else:
                        reconciliation_manifest_sha = _selected_content_digest([])
                except Exception:
                    cleanup_failed = True
                finally:
                    try:
                        if stage_identity is None:
                            raise DispatchError("stage cleanup identity is unavailable")
                        _cleanup_stage(stage_dir, stage_identity)
                    except (OSError, DispatchError):
                        cleanup_failed = True
            try:
                selector.close()
                os.close(stdout_fd); stdout_fd = -1
                os.close(stderr_fd); stderr_fd = -1
                _stage(command, False)
                _load_bound_command(job, state, stage_readonly=False)
                _bound_schemas(command, state)
                if state["attempt_origin"] == "conversation-continue":
                    _bound_verification(job, state)
            except (OSError, DispatchError):
                cleanup_failed = True
            if cleanup_failed:
                reason, final_status = "status_unavailable", "failed"
                exit_code = EXIT_BY_REASON["status_unavailable"]
                result_path = None
                result_binding = None
                failure_stage = "binding_failure"
            # A SHA-approved cancellation may arrive after the last pipe-loop
            # observation (or after reaping) and before candidate work begins.
            # Observe it under the short ownership lock before selecting the
            # expensive reconciliation path.  The final transition reloads
            # again, but that later check is too late to keep a cheap cancel
            # from being delayed by a repository-controlled Git probe.
            with state_lock(job):
                current, current_raw, _current_sha = load_state(job)
                if (
                    current["attempt"] != state["attempt"]
                    or current["controller_pid"] != os.getpid()
                    or current["status"] in TERMINAL
                ):
                    raise DispatchError("dispatch changed before terminal reconciliation")
                state, prior_raw = current, current_raw
                if current["cancel_requested"]:
                    reason, final_status = "cancelled", "cancelled"
                    exit_code = EXIT_BY_REASON["cancelled"]
                    result_path = None
                    result_binding = None
                    failure_stage = None
            # This may use a bounded Git fallback.  The provider clock was
            # already frozen above, so keep this outside the final short state
            # lock: status/control readers can observe the frozen record and
            # reject stale extensions while reconciliation is in progress.
            # A local cancellation/interruption with no current terminal
            # report has no new worktree fact to reconcile.  Do not make the
            # cheap control wait for a candidate/worktree Git scan after the
            # provider group is already reaped.  A continuation's prior
            # candidate remains exact-bound and unreviewed; result/finalize
            # rebind it before use.  A provider-CANCELLED report still has a
            # current result_binding and retains the reconciliation path.
            skip_cancel_reconciliation = bool(
                reason in {"cancelled", "interrupted"}
                and result_binding is None
            )
            if skip_cancel_reconciliation:
                candidate_worktree = None
                reconciliation = {
                    "worktree_reconciliation": "unavailable",
                    "worktree_changes_present": None,
                    "worktree_changed_since_dispatch": None,
                }
            else:
                candidate_worktree = (
                    _state_worktree_snapshot(state, command["workdir"])
                    if result_binding is not None else None
                )
                reconciliation = (
                    _reconciliation_from_snapshot(
                        candidate_worktree, state["worktree_baseline"],
                    )
                    if result_binding is not None else _reconcile_worktree(
                        command["workdir"], state["worktree_baseline"], state=state,
                    )
                )
            # An approved control may land after the last loop observation.  Bind
            # finalization to the current state under the same short transition lock.
            with state_lock(job):
                current, current_raw, _current_sha = load_state(job)
                if (
                    current["attempt"] != state["attempt"]
                    or current["controller_pid"] != os.getpid()
                    or current["status"] in TERMINAL
                ):
                    raise DispatchError("dispatch changed before terminalization")
                # Persist the provider runtime measured before local terminal
                # parsing/reconciliation.  Those controller-local checks must
                # not silently consume a later repair/recovery budget.
                elapsed = max(
                    elapsed,
                    float(current["elapsed_seconds"]),
                )
                if current["cancel_requested"]:
                    reason, final_status, exit_code = "cancelled", "cancelled", EXIT_BY_REASON["cancelled"]
                    result_path = None
                    result_binding = None
                    failure_stage = None
                if reason != "provider_quota_exhausted":
                    provider_retry_after = None
                    provider_retry_observed = None
                prior_candidate_exists = bool(
                    current["attempt_origin"] == "conversation-continue"
                    and current["candidate_recognized"]
                )
                prior_candidate_is_bound = bool(
                    prior_candidate_exists
                    and current["candidate_source"] != "none"
                    and current["result_available"]
                    and current["failure_stage"] is None
                    and all(current[key] is not None for key in (
                        "result_path", "result_sha256", "result_identity",
                        "candidate_worktree_sha256", "candidate_worktree_entries",
                    ))
                )
                # An old continuation candidate remains readable only when all
                # of its exact report/worktree bindings are still complete.
                # Keep an incomplete one as inaccessible forensic state and
                # fail closed; do not let a concurrent local cancel convert it
                # into an apparently usable candidate.
                preserve_candidate = bool(
                    result_binding is None and prior_candidate_is_bound
                )
                preserve_candidate_forensics = bool(
                    result_binding is None and prior_candidate_exists
                )
                terminal_snapshot_unavailable = bool(
                    result_binding is not None
                    and outer_status in {"SUCCESS", "ERROR", "CANCELLED"}
                    and candidate_worktree is None
                )
                if terminal_snapshot_unavailable:
                    # Keep the exact terminal report binding and its outer
                    # provenance for forensics, but it is not a reviewable
                    # candidate without a worktree binding.
                    reason, final_status = "status_unavailable", "failed"
                    exit_code = EXIT_BY_REASON["status_unavailable"]
                    failure_stage = "binding_failure"
                if preserve_candidate_forensics and not prior_candidate_is_bound:
                    reason, final_status = "status_unavailable", "failed"
                    exit_code = EXIT_BY_REASON["status_unavailable"]
                    failure_stage = "binding_failure"
                candidate_recognized = result_binding is not None or preserve_candidate_forensics
                candidate_unavailable = bool(
                    candidate_recognized and failure_stage == "binding_failure"
                )
                candidate_source = (
                    "provider_success" if result_binding is not None and outer_status == "SUCCESS"
                    else "provider_error" if result_binding is not None and outer_status == "ERROR"
                    else "provider_cancelled" if result_binding is not None and outer_status == "CANCELLED"
                    else current["candidate_source"] if preserve_candidate_forensics
                    else "none"
                )
                if failure_stage in {"schema_rejection", "binding_failure", "framing", "outer_status", "invalid_envelope"}:
                    provider_terminal_status = "unknown"
                else:
                    provider_terminal_status = (
                        "success" if outer_status == "SUCCESS"
                        else "error" if outer_status == "ERROR"
                        else "cancelled" if outer_status in {"CANCELLED", "CANCELED"}
                        else "unknown"
                    )
                preserved_path = current["result_path"] if preserve_candidate_forensics else None
                preserved_sha = current["result_sha256"] if preserve_candidate_forensics else None
                preserved_identity = current["result_identity"] if preserve_candidate_forensics else None
                updates = {
                    "status": final_status,
                    "reason": reason,
                    "exit_code": exit_code,
                    "controller_pid": None,
                    "finished_epoch": time.time(),
                    "elapsed_seconds": elapsed,
                    "agy_returncode": returncode,
                    "result_path": str(envelope_path) if result_binding is not None else preserved_path,
                    "result_sha256": result_binding[0] if result_binding is not None else preserved_sha,
                    "result_identity": list(result_binding[1]) if result_binding is not None else preserved_identity,
                    "candidate_recognized": candidate_recognized,
                    "candidate_source": candidate_source,
                    "provider_terminal_status": provider_terminal_status,
                    # Preserve an exact old candidate after a binding failure for
                    # forensics, but never claim it can still be read or reviewed.
                    "result_available": candidate_recognized and not candidate_unavailable,
                    "candidate_worktree_sha256": (
                        candidate_worktree["sha256"] if candidate_worktree is not None
                        else current["candidate_worktree_sha256"] if preserve_candidate_forensics else None
                    ),
                    "candidate_worktree_entries": (
                        candidate_worktree["entries"] if candidate_worktree is not None
                        else current["candidate_worktree_entries"] if preserve_candidate_forensics else None
                    ),
                    "driver_disposition": "unreviewed" if candidate_recognized else "not_applicable",
                    "failure_stage": failure_stage,
                    "last_activity": "terminal_received" if saw_terminal else current["last_activity"],
                    "next_action": (
                        "blocked" if candidate_unavailable else "driver_review"
                    ) if candidate_recognized else (
                        "none" if reason == "selection_preflight_failed" else
                        "resume" if current["conversation_id"] else "blocked"
                    ),
                    "next_action_command": None,
                    **(
                        {
                            "worktree_reconciliation": "unavailable",
                            "worktree_changes_present": None,
                            "worktree_changed_since_dispatch": None,
                        }
                        if terminal_snapshot_unavailable else reconciliation
                    ),
                    "resume_available": bool(
                        current["conversation_id"] and not candidate_recognized
                        and final_status == "failed"
                        and reason != "selection_preflight_failed"
                    ),
                    "continue_available": False,
                    "remote_cancel_unverified": reason in {"cancelled", "interrupted"},
                    "limit_kind": limit_kind,
                    "provider_retry_after_seconds": provider_retry_after,
                    "provider_retry_observed_epoch": provider_retry_observed,
                }
                if current.get("provider_scope_path") is not None:
                    updates["reconciliation_manifest_sha256"] = reconciliation_manifest_sha
                if result_binding is not None:
                    # Continuation feedback remains bound audit evidence for
                    # the prior candidate. A newly returned candidate starts
                    # unreviewed, so it cannot inherit prior check evidence.
                    updates.update({
                        "check_summary": None,
                        "check_counts": {
                            "passed": 0, "failed": 0,
                            "advisory": 0, "missing": 0,
                        },
                    })
                if current["schema_version"] >= 5:
                    if boundary_failed or candidate_unavailable:
                        updates.update({"phase": "blocked", "assurance": "blocked"})
                    elif candidate_recognized:
                        updates.update({
                            "phase": (
                                "repair-failed"
                                if final_status == "failed" and current["attempt_origin"] == "conversation-continue"
                                else "awaiting-verification"
                            ),
                            "assurance": "pending",
                            "continue_available": bool(
                                final_status in {"succeeded", "failed"}
                                and reason != "selection_preflight_failed"
                                and candidate_source != "provider_cancelled"
                                and current["conversation_id"]
                                and current["attempt"] < current["max_cycles"]
                                and elapsed < current["max_seconds"]
                            ),
                        })
                    else:
                        updates.update({
                            "phase": (
                                "repair-failed"
                                if final_status == "failed" and current["attempt_origin"] == "conversation-continue"
                                else "attempt-failed"
                            ),
                            "assurance": "pending",
                            "continue_available": False,
                        })
                state, prior_raw, _sha = _transition_locked(job, current, current_raw, updates)
            return exit_code
        finally:
            if process is not None:
                # If an exception is leaving the provider loop, transfer
                # ownership to the outer recovery only after this exact group
                # termination/reap has succeeded.  It then freezes elapsed
                # time from this reap boundary.  If termination itself raises,
                # keep ``process`` live so the outer recovery retains the one
                # retry opportunity instead of assuming the group is gone.
                _terminate(process)
                runtime_end_mono = time.monotonic()
                process = None
            with contextlib.suppress(Exception):
                selector.close()
            if stdout_fd >= 0:
                os.close(stdout_fd)
            if stderr_fd >= 0:
                os.close(stderr_fd)
            with contextlib.suppress(OSError):
                _stage(command, False)
    except Exception:
        # Once Popen succeeds, no ordinary controller exception may be left to
        # the cleanup-only finally path.  Reap first, freeze if the state still
        # belongs to this controller, then publish one fail-closed terminal
        # projection.  Pre-launch errors retain their narrower existing paths.
        if process is None and started_mono is None:
            raise
        if process is not None:
            with contextlib.suppress(Exception):
                _terminate(process)
            process = None
            runtime_end_mono = time.monotonic()
        frozen_elapsed = float(state["elapsed_seconds"])
        if not runtime_frozen:
            frozen_elapsed = float(state["attempt_base_elapsed"])
            if started_mono is not None:
                end = runtime_end_mono if runtime_end_mono is not None else time.monotonic()
                frozen_elapsed += max(0.0, end - started_mono)
            try:
                state, prior_raw, _sha, _limit = _freeze_reaped_runtime(
                    job, state["attempt"], os.getpid(), frozen_elapsed,
                )
                runtime_frozen = True
            except Exception:
                # The final state write below still clears an active controller
                # record; preserve the largest local elapsed observation if the
                # dedicated freeze CAS itself could not complete.
                pass
        try:
            terminal, _raw, _sha = _terminalize_owned(
                job, state, status="failed", reason="status_unavailable",
                exit_code=EXIT_BY_REASON["status_unavailable"],
                failure_stage="binding_failure", expected_controller_pid=os.getpid(),
                elapsed_seconds=frozen_elapsed, postlaunch_cancel=True,
            )
            return int(terminal["exit_code"])
        except Exception:
            # A failed final write is still not allowed to disguise the
            # controller exception; the strict helper has already attempted
            # its unavailable fallback without holding a scan under the lock.
            return EXIT_BY_REASON["status_unavailable"]
    finally:
        for number, handler in prior_handlers.items():
            signal.signal(number, handler)


def create_state(
    job: Path, origin: str, *, resume: bool, approve_sha: str | None = None,
    approve_migration_sha: str | None = None, verification: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], str]:
    command, command_raw, command_info = load_command(job)
    stage_sha, stage_info = _bound_stage(command, readonly=False)
    schema_bindings = _schema_bindings(command)
    path = job / STATE_NAME
    with state_lock(job):
        if resume:
            state, raw, sha = load_state(job)
            if approve_sha != sha:
                action = {
                    "conversation-resume": "resume",
                    "fresh-restart": "restart",
                    "conversation-continue": "continue",
                }[origin]
                raise _state_approval_error(state, sha, action)
            # Reject a semantically unavailable recovery before probing its
            # launch inputs.  This keeps an approved stale-state diagnostic
            # actionable without treating the diagnostic itself as authority
            # to rebind a root for a recovery that cannot run.
            if origin != "conversation-continue":
                if state["status"] not in TERMINAL or state["status"] == "orphaned":
                    raise DispatchError("only a terminal unsuccessful dispatch can continue")
                if origin == "fresh-restart" and not _restart_guard_accepts(state):
                    raise DispatchError("dispatch fresh restart is unavailable")
                if origin == "conversation-resume" and not _resume_is_eligible(state, time.time()):
                    raise DispatchError("dispatch is not resume-eligible")
            if state["schema_version"] in {3, 4}:
                command, state = _approved_legacy_migration(
                    job, state, raw, approve_migration_sha,
                )
            else:
                command = _load_bound_command(job, state, stage_readonly=False)
            if _job_is_inside_worktree(job, command["workdir"]):
                raise DispatchError("dispatch job directory cannot be inside the target workdir")
            command, state = _bound_lifecycle_inputs(job, state, command)
            if not _selection_launch_is_authorized(_load_bound_selection(command, state)):
                raise DispatchError("dispatch direct selection lacks approved compatibility disposition")
            if origin == "conversation-continue":
                if (
                    verification is None
                    or not _continue_is_eligible(state, time.time())
                ):
                    raise DispatchError("dispatch continuation is unavailable")
                _require_current_candidate_verification(verification, state)
                command, _candidate_raw = _bound_current_candidate(job, state)
            else:
                # The terminal/recovery predicates were checked above before
                # any launch-input probe; preserve that linearization here.
                pass
            if float(state["elapsed_seconds"]) >= float(state["max_seconds"]):
                raise DispatchError("dispatch max runtime is exhausted")
            if state["workflow"] != "legacy" and state["attempt"] >= state["max_cycles"]:
                raise DispatchError("dispatch max cycles is exhausted")
            conversation = state["conversation_id"] if origin == "conversation-resume" else None
            if origin == "conversation-continue":
                conversation = state["conversation_id"]
            verification_path: Path | None = None
            verification_sha: str | None = None
            verification_identity: tuple[int, int, int, int, int] | None = None
            if verification is not None:
                verification_path, verification_sha, verification_identity = _write_verification(
                    job, f"cycle-{state['attempt'] + 1:03d}", verification,
                )
            try:
                next_state = initial_state(
                    command, origin, state["attempt"] + 1,
                    command_sha=digest(command_raw), command_identity=command_info,
                    stage_sha=stage_sha, stage_identity=stage_info,
                    project_boundary=state["project_boundary"],
                    schema_bindings=schema_bindings,
                    state_schema=state["schema_version"],
                    explain_worktree_rejection=True,
                )
                next_state["sequence"] = state["sequence"] + 1
                next_state["previous_state_sha256"] = sha
                next_state["conversation_id"] = conversation
                next_state["resume_available"] = conversation is not None
                next_state["attempt_base_elapsed"] = float(state["elapsed_seconds"])
                next_state["elapsed_seconds"] = float(state["elapsed_seconds"])
                next_state["hard_seconds"] = min(
                    float(state["max_seconds"]),
                    float(state["elapsed_seconds"]) + float(command["hard_seconds"]),
                )
                next_state["max_seconds"] = float(state["max_seconds"])
                if state["workflow"] != "legacy":
                    next_state["phase"] = "repairing" if origin == "conversation-continue" else "dispatching"
                    next_state["check_summary"] = state["check_summary"]
                    next_state["check_counts"] = state["check_counts"]
                    next_state["last_success_path"] = state["result_path"] or state["last_success_path"]
                    next_state["last_success_sha256"] = state["result_sha256"] or state["last_success_sha256"]
                    next_state["last_success_identity"] = state["result_identity"] or state["last_success_identity"]
                    if origin == "conversation-continue":
                        for key in (
                            "result_path", "result_sha256", "result_identity",
                            "candidate_recognized", "candidate_source", "result_available",
                            "candidate_worktree_sha256", "candidate_worktree_entries",
                            "driver_disposition",
                        ):
                            next_state[key] = state[key]
                if verification_path is not None:
                    next_state.update({
                        "verification_path": str(verification_path),
                        "verification_sha256": verification_sha,
                        "verification_identity": list(verification_identity),
                        "check_summary": verification["summary"],
                        "check_counts": _verification_counts(verification),
                    })
                validate_state(next_state)
                current, _info = read_regular(path, MAX_STATE_BYTES, "dispatch state")
                if current != raw:
                    raise DispatchError("dispatch state changed before continuation")
                _new_raw, new_sha = write_atomic(job, STATE_NAME, next_state)
                return next_state, new_sha
            except Exception:
                _discard_new_verification(verification_path, verification_identity)
                raise
        if path.exists() or path.is_symlink():
            raise DispatchError("dispatch state already exists")
        if command.get("workflow") == "project" and _job_is_inside_worktree(job, command["workdir"]):
            raise DispatchError("dispatch job directory cannot be inside the target workdir")
        state = initial_state(
            command, origin, 1, command_sha=digest(command_raw),
            command_identity=command_info, stage_sha=stage_sha, stage_identity=stage_info,
            schema_bindings=schema_bindings,
            explain_worktree_rejection=True,
        )
        validate_state(state)
        _raw, sha = write_atomic(job, STATE_NAME, state)
        return state, sha


def spawn(
    job: Path, origin: str, *, resume: bool, foreground: bool,
    approve_sha: str | None = None, verification: dict[str, Any] | None = None,
    approve_migration_sha: str | None = None,
    output_format: str = "json",
) -> int:
    parent_signal: int | None = None
    completion_blocked = False

    def latch(number: int, _frame: Any) -> None:
        nonlocal parent_signal
        if parent_signal is None:
            parent_signal = number

    watched = (signal.SIGHUP, signal.SIGINT, signal.SIGTERM)
    previous = {number: signal.getsignal(number) for number in watched}
    for number in watched:
        signal.signal(number, latch)
    controller_process: subprocess.Popen[bytes] | None = None
    try:
      with lifecycle_lock(job, blocking=False) as ownership_fd:
        state, _sha = create_state(
            job, origin, resume=resume, approve_sha=approve_sha,
            approve_migration_sha=approve_migration_sha, verification=verification,
        )
        if parent_signal is not None:
            _terminalize_queued_signal(job, parent_signal)
            return 128 + parent_signal
        bound_command = _load_bound_command(job, state, stage_readonly=False)
        controller_environment = MODEL_SELECTION.child_environment(bound_command["provider_env"])
        controller_argv = [
            sys.executable, "-I", "-S", "-B", str(Path(__file__).resolve()),
            "controller", "--job-dir", str(job), "--ownership-fd", str(ownership_fd),
        ]
        controller_process = subprocess.Popen(
            controller_argv, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL, start_new_session=True, close_fds=True,
            pass_fds=(ownership_fd,),
            env=controller_environment,
        )
      deadline = time.monotonic() + 5.0
      forwarded = False
      while time.monotonic() < deadline:
        current, _raw, sha = read_state_snapshot(job)
        if parent_signal is not None and not forwarded:
            with contextlib.suppress(ProcessLookupError, PermissionError):
                os.killpg(controller_process.pid, parent_signal)
            forwarded = True
        if current["status"] in TERMINAL:
            break
        if controller_process.poll() is not None:
            _terminalize_start_failure(job)
            raise DispatchError("controller exited before startup handshake")
        if (
            current["status"] in {"queued", "running", "cancel-requested"}
            and current["controller_pid"] == controller_process.pid
        ):
            break
        time.sleep(0.02)
      else:
        _terminate(controller_process)
        controller_process = None
        _terminalize_start_failure(job)
        raise DispatchError("controller startup handshake timed out")
      if parent_signal is not None and not foreground:
        try:
            controller_process.wait(timeout=5.0)
        except subprocess.TimeoutExpired:
            _terminate(controller_process)
        return 128 + parent_signal
      if not foreground:
        print_control_status(current, sha, output_format, job=job)
        return 0
      while controller_process.poll() is None:
        if parent_signal is not None and not forwarded:
            with contextlib.suppress(ProcessLookupError, PermissionError):
                os.killpg(controller_process.pid, parent_signal)
            forwarded = True
        time.sleep(0.02)
      result_code = controller_process.returncode
      # Linearize foreground completion: after this snapshot lifecycle signals stay
      # blocked until process exit, so success bytes cannot race a late cancellation.
      signal.pthread_sigmask(signal.SIG_BLOCK, watched)
      completion_blocked = True
      pending = signal.sigpending()
      completion_signal = parent_signal
      for candidate in watched:
        if candidate in pending or candidate == parent_signal:
            completion_signal = candidate
            break
      if completion_signal is not None:
        result_code = 128 + completion_signal
      final, _raw, sha = read_state_snapshot(job)
      if completion_signal is None and final["status"] == "succeeded" and final["result_path"] is not None:
        command_result(job)
      else:
        sys.stderr.buffer.write(canonical(public_status(final, sha, job=job)))
        sys.stderr.buffer.flush()
      return result_code
    finally:
      if not completion_blocked:
        for number, handler in previous.items():
            signal.signal(number, handler)


def _terminal_projection(
    state: dict[str, Any], *, status: str, reason: str, exit_code: int,
    failure_stage: str | None = None, remote_cancel_unverified: bool = False,
    allow_continue: bool = True,
) -> dict[str, Any]:
    """Project a local terminal side path without dropping a bound candidate.

    These paths run before normal provider terminalization, so they must not leave
    the transient dispatching/repairing UI fields behind.  A queued continuation
    already contains an exact, driver-owned candidate binding; returning that
    candidate to review is safer than treating a local controller failure as a
    provider repair result.
    """
    candidate = bool(state["candidate_recognized"])
    candidate_unavailable = bool(candidate and failure_stage == "binding_failure")
    continuation = candidate and state["attempt_origin"] == "conversation-continue"
    can_continue = bool(
        continuation
        and state["candidate_source"] != "provider_cancelled"
        and state["conversation_id"]
        and state["attempt"] < state["max_cycles"]
        and float(state["elapsed_seconds"]) < float(state["max_seconds"])
        and status == "failed"
        and allow_continue
        and not candidate_unavailable
    )
    updates: dict[str, Any] = {
        "status": status,
        "reason": reason,
        "exit_code": exit_code,
        "controller_pid": None,
        "finished_epoch": time.time(),
        "failure_stage": failure_stage,
        "provider_terminal_status": state.get("provider_terminal_status", "unknown"),
        # A local process signal is not evidence that the provider observed a
        # cancellation.  Startup/binding failures make no remote-cancel claim.
        "remote_cancel_unverified": remote_cancel_unverified,
        "continue_available": can_continue,
        "result_available": candidate and not candidate_unavailable,
        **_reconcile_worktree(state["workdir"], state["worktree_baseline"], state=state),
    }
    if candidate:
        updates.update({
            "resume_available": False,
            "driver_disposition": "unreviewed",
            "next_action": "blocked" if candidate_unavailable else "driver_review",
            "next_action_command": None,
        })
    else:
        resume_eligible = bool(
            status == "failed" and state["conversation_id"]
            and state["attempt_origin"] != "conversation-continue"
        )
        updates.update({
            "resume_available": resume_eligible,
            "driver_disposition": "not_applicable",
            "next_action": "resume" if resume_eligible else "blocked",
            "next_action_command": None,
        })
    if state["schema_version"] >= 5:
        updates.update({
            "phase": "blocked" if candidate_unavailable else ("awaiting-verification" if candidate else "attempt-failed"),
            "assurance": "blocked" if candidate_unavailable else "pending",
        })
    return updates


def _terminalize_owned(
    job: Path, state: dict[str, Any], *, status: str, reason: str, exit_code: int,
    failure_stage: str | None = None, expected_controller_pid: int | None = None,
    elapsed_seconds: float | None = None, postlaunch_cancel: bool = False,
) -> tuple[dict[str, Any], bytes, str]:
    """Publish one owned terminal state without holding a lock across scans."""
    projection_unavailable = False
    try:
        primary = _terminal_projection(
            state, status=status, reason=reason, exit_code=exit_code,
            failure_stage=failure_stage, allow_continue=False,
        )
        cancelled = _terminal_projection(
            state, status="cancelled", reason="cancelled",
            exit_code=EXIT_BY_REASON["cancelled"],
            remote_cancel_unverified=postlaunch_cancel,
        )
    except Exception:
        # The no-scan fallback is deliberately built under the final state
        # lock below.  A continuation can have a previously bound candidate;
        # a failed reconciliation of this new attempt is not evidence that
        # the old binding disappeared.  Conversely, an incomplete/unavailable
        # prior binding must fail closed as status_unavailable rather than
        # combine ``cancelled`` with a schema-invalid inaccessible candidate.
        projection_unavailable = True
    with state_lock(job):
        current, raw, _sha = load_state(job)
        if current["status"] in TERMINAL:
            return current, raw, digest(raw)
        if (
            current["attempt"] != state["attempt"]
            or current["controller_pid"] != expected_controller_pid
        ):
            raise DispatchError("dispatch changed before terminalization")
        if projection_unavailable:
            # Do not re-run any candidate/worktree probe here: this is the
            # recovery path for a probe that has already failed.  The exact
            # old candidate is safe to preserve only when its stored bindings
            # are internally complete and still advertised as available.  Its
            # command paths will independently bind it again before result,
            # continue, or finalize is allowed.
            prior_candidate_is_bound = bool(
                current["attempt_origin"] == "conversation-continue"
                and current["candidate_recognized"]
                and current["candidate_source"] != "none"
                and current["result_available"]
                and current["failure_stage"] is None
                and all(current[key] is not None for key in (
                    "result_path", "result_sha256", "result_identity",
                    "candidate_worktree_sha256", "candidate_worktree_entries",
                ))
            )
            candidate = bool(current["candidate_recognized"])
            # An ordinary post-launch cancellation has no candidate to
            # protect, so it remains cancelled.  Only an *incomplete* prior
            # candidate takes fail-closed precedence over cancellation: that
            # combination cannot truthfully expose a readable result.
            cancelled = bool(
                current["cancel_requested"]
                and (not candidate or prior_candidate_is_bound)
            )
            candidate_unavailable = bool(candidate and not prior_candidate_is_bound)
            updates = {
                "status": "cancelled" if cancelled else "failed",
                "reason": "cancelled" if cancelled else "status_unavailable",
                "exit_code": (
                    EXIT_BY_REASON["cancelled"] if cancelled
                    else EXIT_BY_REASON["status_unavailable"]
                ),
                "controller_pid": None,
                "finished_epoch": time.time(),
                "continue_available": False,
                "result_available": bool(prior_candidate_is_bound),
                "worktree_reconciliation": "unavailable",
                "worktree_changes_present": None,
                "worktree_changed_since_dispatch": None,
                "next_action": "blocked" if candidate_unavailable else "none",
                "next_action_command": None,
                "resume_available": False,
                "driver_disposition": "unreviewed" if candidate else "not_applicable",
                # A successful local cancellation has no failed binding to
                # report.  An unbound/incomplete prior candidate is the one
                # case that must retain binding_failure fail-closed.
                "failure_stage": None if (cancelled or prior_candidate_is_bound) else "binding_failure",
                "remote_cancel_unverified": bool(cancelled and postlaunch_cancel),
                "provider_terminal_status": current.get("provider_terminal_status", "unknown"),
            }
            if current["schema_version"] >= 5:
                updates.update({
                    "phase": "blocked" if candidate_unavailable else (
                        "awaiting-verification" if candidate else "attempt-failed"
                    ),
                    "assurance": "blocked" if candidate_unavailable else "pending",
                })
        else:
            updates = dict(cancelled if current["cancel_requested"] else primary)
        if elapsed_seconds is not None:
            updates.update({
                "elapsed_seconds": max(elapsed_seconds, float(current["elapsed_seconds"])),
                "started_epoch": None,
            })
        return _transition_locked(job, current, raw, updates)


def _terminalize_start_failure(job: Path) -> None:
    with lifecycle_lock(job, blocking=True):
        with state_lock(job):
            state, raw, _sha = load_state(job)
            if state["status"] in TERMINAL:
                return
            _transition_locked(job, state, raw, _terminal_projection(
                state, status="failed", reason="status_unavailable",
                exit_code=EXIT_BY_REASON["status_unavailable"],
            ))


def _terminalize_queued_signal(job: Path, number: int) -> None:
    with state_lock(job):
        state, raw, _sha = load_state(job)
        if state["status"] != "queued":
            raise DispatchError("dispatch changed before queued cancellation")
        # A signal before a continuation controller starts must preserve the
        # prior candidate and send it back to driver review.  Its local terminal
        # state is failed (not provider-CANCELED), so a strict same-conversation
        # continue remains possible when its original budget still permits it.
        continuation = bool(
            state["candidate_recognized"]
            and state["attempt_origin"] == "conversation-continue"
        )
        _transition_locked(job, state, raw, _terminal_projection(
            state,
            status="failed" if continuation else "cancelled",
            reason="interrupted",
            exit_code=128 + number,
            remote_cancel_unverified=True,
        ))


def command_status(job: Path, output_format: str = "json") -> int:
    state, _raw, sha = read_state_snapshot(job)
    if state["status"] in {"queued", "running", "cancel-requested"}:
        try:
            with lifecycle_lock(job, blocking=False):
                state, raw, sha = read_state_snapshot(job)
                if state["status"] in {"queued", "running", "cancel-requested"}:
                    state, raw, sha = transition(job, state, raw, _terminal_projection(
                        state, status="orphaned", reason="status_unavailable",
                        exit_code=EXIT_BY_REASON["status_unavailable"],
                    ))
        except DispatchError as exc:
            if str(exc) != "dispatch controller is active":
                raise
    print_control_status(state, sha, output_format, job=job)
    return 0


def command_wait(job: Path, after: str, timeout: float, output_format: str = "json") -> int:
    if SHA_RE.fullmatch(after) is None or not (0 <= timeout <= MAX_STATUS_WAIT):
        raise DispatchError("wait arguments are invalid")
    deadline = time.monotonic() + timeout
    while True:
        state, _raw, sha = read_state_snapshot(job)
        if sha != after or state["status"] in TERMINAL:
            print_control_status(state, sha, output_format, job=job)
            return 0
        if time.monotonic() >= deadline:
            print_control_status(state, sha, output_format, job=job)
            return 0
        time.sleep(min(0.20, max(0.0, deadline - time.monotonic())))


def command_result(job: Path, output_format: str = "json") -> int:
    state, _raw, sha = read_state_snapshot(job)
    if state["candidate_recognized"]:
        if _is_active(state):
            raise DispatchError("dispatch result is unavailable while a repair is active")
        _command, candidate_raw = _bound_current_candidate(job, state)
        if output_format == "text":
            print_text_status(state, sha, job=job)
        else:
            sys.stdout.buffer.write(candidate_raw)
            sys.stdout.buffer.flush()
        return 0
    if _legacy_prior_result_is_unknown(state):
        legacy_raw = _bound_legacy_unknown_result(job, state)
        if output_format == "text":
            print_text_status(state, sha, job=job)
        else:
            sys.stdout.buffer.write(legacy_raw)
            sys.stdout.buffer.flush()
        return 0
    result_path = state["result_path"]
    result_sha = state["result_sha256"]
    result_identity = state["result_identity"]
    if (
        state["workflow"] == "project" and state["status"] in {"failed", "cancelled"}
        and state["phase"] == "completed" and state["assurance"] == "partially_verified"
        and result_path is None
    ):
        result_path = state["last_success_path"]
        result_sha = state["last_success_sha256"]
        result_identity = state["last_success_identity"]
    elif not state["result_available"]:
        raise DispatchError("dispatch result is unavailable")
    if result_path is None:
        raise DispatchError("dispatch has no preserved result")
    raw, info = read_regular(Path(result_path), 1024 * 1024, "dispatch result")
    if digest(raw) != result_sha or list(_identity(info)) != result_identity:
        raise DispatchError("dispatch result binding changed")
    command = _load_bound_command(job, state, stage_readonly=False)
    schema_paths = _schema_paths(command)
    if schema_paths is None:
        raise DispatchError("dispatch result schema is unavailable")
    if state["schema_version"] >= 5:
        schema_paths = _bound_schemas(command, state)
    validator = Path(__file__).with_name("validate-envelope.py")
    checked = [
        subprocess.run(
            [sys.executable, "-I", "-S", "-B", str(validator), str(schema), str(result_path)],
            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            check=False,
        )
        for schema in schema_paths
    ]
    if any(item.returncode != 0 for item in checked):
        raise DispatchError("dispatch result is no longer valid")
    if output_format == "text":
        print_text_status(state, sha, job=job)
    else:
        sys.stdout.buffer.write(raw)
        sys.stdout.buffer.flush()
    return 0


def command_continue(
    job: Path, approve_sha: str, approve_migration_sha: str | None,
    output_format: str = "json",
) -> int:
    verification = _verification_from_stdin()
    return spawn(
        job, "conversation-continue", resume=True, foreground=False,
        approve_sha=approve_sha, approve_migration_sha=approve_migration_sha,
        verification=verification, output_format=output_format,
    )


def command_finalize(
    job: Path, approve_sha: str, approve_migration_sha: str | None,
    assurance: str, output_format: str = "json",
) -> int:
    if assurance not in {"verified", "partially_verified", "rejected", "blocked"}:
        raise DispatchError("project assurance is invalid")
    verification = _verification_from_stdin()
    with state_lock(job):
        state, raw, sha = load_state(job)
        if sha != approve_sha:
            raise _state_approval_error(state, sha, "finalize")
        if state["schema_version"] in {3, 4}:
            command, state = _approved_legacy_migration(
                job, state, raw, approve_migration_sha,
            )
        else:
            command = _load_bound_command(job, state, stage_readonly=False)
        command, state = _bound_lifecycle_inputs(job, state, command)
        if not _finalize_is_eligible(state):
            raise DispatchError("dispatch finalization is stale or unavailable")
        if assurance == "verified" and _job_is_inside_worktree(job, command["workdir"]):
            raise DispatchError("verified finalization is unavailable for jobs inside the worktree")
        _require_current_candidate_verification(verification, state)
        if assurance == "verified" and not _verification_is_verified(verification, state["workflow"]):
            raise DispatchError("verified finalization requires complete driver evidence")
        command, _candidate_raw = _bound_current_candidate(job, state)
        counts = _verification_counts(verification)
        path: Path | None = None
        identity: tuple[int, int, int, int, int] | None = None
        try:
            path, verification_sha, identity = _write_verification(
                job, f"final-{state['cycle']:03d}", verification,
            )
            phase = "blocked" if assurance == "blocked" else "completed"
            state, _raw, sha = _transition_locked(job, state, raw, {
                "phase": phase,
                "assurance": assurance,
                "continue_available": False,
                "check_summary": verification["summary"],
                "check_counts": counts,
                "verification_path": str(path),
                "verification_sha256": verification_sha,
                "verification_identity": list(identity),
                "driver_disposition": assurance,
                "next_action": "none",
                "next_action_command": None,
            })
        except Exception:
            _discard_new_verification(path, identity)
            raise
    print_control_status(state, sha, output_format, job=job)
    return 0


def command_control(job: Path, action: str, approve_sha: str, seconds: float | None) -> int:
    if SHA_RE.fullmatch(approve_sha) is None:
        raise DispatchError("state approval is invalid")
    with state_lock(job):
        state, raw, sha = load_state(job)
        if sha != approve_sha:
            raise _state_approval_error(state, sha, action)
        now = time.time()
        if state["status"] not in {"queued", "running", "cancel-requested"}:
            raise DispatchError("state approval is stale or dispatch is terminal")
        if action == "cancel":
            if state["cancel_requested"]:
                raise DispatchError("cancel is already requested")
            updates = {"cancel_requested": True, "status": "cancel-requested"}
        else:
            assert seconds is not None
            if not _extend_is_eligible(state, now):
                raise DispatchError("deadline extension requires fresh progress before the hard deadline")
            if seconds <= 0 or state["hard_seconds"] + seconds > state["max_seconds"]:
                raise DispatchError("deadline extension exceeds max runtime")
            updates = {"hard_seconds": state["hard_seconds"] + seconds}
        state, _raw, sha = _transition_locked(
            job, state, raw, updates,
            # Cancel/extend are cheap active-process controls.  They must not
            # trigger a candidate/root migration scan or turn an active V3/V4
            # record into a different lifecycle state.
            legacy_control_only=state["schema_version"] in {1, 3, 4},
        )
    print_json(public_status(state, sha, job=job))
    return 0


def duration(text: str) -> float:
    match = re.fullmatch(r"([1-9][0-9]*)(s|m|h)", text)
    if match is None:
        raise argparse.ArgumentTypeError("duration must be a positive integer plus s, m, or h")
    factor = {"s": 1, "m": 60, "h": 3600}[match.group(2)]
    value = int(match.group(1)) * factor
    if value > 7 * 24 * 3600:
        raise argparse.ArgumentTypeError("duration is too large")
    return float(value)


def parser() -> Parser:
    result = Parser(prog="agy-dispatch")
    commands = result.add_subparsers(dest="command", required=True, parser_class=Parser)
    for name in ("run", "start", "resume", "restart", "continue", "status", "result", "verification-copy", "controller"):
        item = commands.add_parser(name)
        item.add_argument("--job-dir", required=True)
        if name == "controller":
            item.add_argument("--ownership-fd", required=True, type=int)
        if name in {"resume", "restart", "continue"}:
            item.add_argument("--approve-state-sha", required=name != "resume")
            item.add_argument("--approve-migration-sha")
        if name in {"resume", "restart", "continue", "status", "result", "verification-copy"}:
            item.add_argument("--format", choices=("json", "text"), default="json")
        if name == "verification-copy":
            item.add_argument("--destination", required=True)
    finalize = commands.add_parser("finalize")
    finalize.add_argument("--job-dir", required=True)
    finalize.add_argument("--approve-state-sha", required=True)
    finalize.add_argument("--approve-migration-sha")
    finalize.add_argument("--assurance", required=True)
    finalize.add_argument("--format", choices=("json", "text"), default="json")
    wait = commands.add_parser("wait")
    wait.add_argument("--job-dir", required=True)
    wait.add_argument("--after-state-sha", required=True)
    wait.add_argument("--timeout", type=duration, default=60.0)
    wait.add_argument("--format", choices=("json", "text"), default="json")
    for name in ("cancel", "extend"):
        item = commands.add_parser(name)
        item.add_argument("--job-dir", required=True)
        item.add_argument("--approve-state-sha", required=True)
        if name == "extend":
            item.add_argument("--by", type=duration, required=True)
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    job = canonical_job(Path(args.job_dir))
    if args.command == "controller":
        if args.ownership_fd < 3:
            raise DispatchError("controller ownership descriptor is invalid")
        return controller(job, args.ownership_fd)
    if args.command == "run":
        return spawn(job, "initial", resume=False, foreground=True)
    if args.command == "start":
        return spawn(job, "initial", resume=False, foreground=False)
    if args.command == "resume":
        if args.approve_state_sha is None:
            raise _missing_state_approval(job, "resume")
        return spawn(
            job, "conversation-resume", resume=True, foreground=False,
            approve_sha=args.approve_state_sha,
            approve_migration_sha=args.approve_migration_sha, output_format=args.format,
        )
    if args.command == "restart":
        return spawn(
            job, "fresh-restart", resume=True, foreground=False,
            approve_sha=args.approve_state_sha,
            approve_migration_sha=args.approve_migration_sha, output_format=args.format,
        )
    if args.command == "continue":
        return command_continue(
            job, args.approve_state_sha, args.approve_migration_sha, args.format,
        )
    if args.command == "status":
        return command_status(job, args.format)
    if args.command == "wait":
        return command_wait(job, args.after_state_sha, args.timeout, args.format)
    if args.command == "result":
        return command_result(job, args.format)
    if args.command == "verification-copy":
        return command_verification_copy(job, Path(args.destination), args.format)
    if args.command == "finalize":
        return command_finalize(
            job, args.approve_state_sha, args.approve_migration_sha,
            args.assurance, args.format,
        )
    if args.command in {"cancel", "extend"}:
        return command_control(
            job, args.command, args.approve_state_sha,
            getattr(args, "by", None),
        )
    raise DispatchError("unknown command")


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except DispatchError as exc:
        print(f"agy-dispatch: {exc}", file=sys.stderr)
        command_name = sys.argv[1] if len(sys.argv) > 1 else ""
        if command_name == "resume":
            raise SystemExit(EXIT_BY_REASON["resume_failed"])
        if command_name in {"status", "wait", "result", "verification-copy"}:
            raise SystemExit(EXIT_BY_REASON["status_unavailable"])
        raise SystemExit(64)
