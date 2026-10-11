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
import dataclasses
import fcntl
import hashlib
from functools import partial
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
from typing import Callable, Mapping, TypedDict, TypeVar, AbstractSet, Any, Iterator, NamedTuple, NoReturn, IO, cast

sys.dont_write_bytecode = True

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import agy_dispatch_verification as SELF_VERIFICATION  # noqa: E402 -- sibling imports follow startup isolation/path setup
import agy_dispatch_containment as CONTAINMENT  # noqa: E402 -- sibling imports follow startup isolation/path setup
import agy_dispatch_worktree as WORKTREE  # noqa: E402 -- sibling imports follow startup isolation/path setup
import candidate_state as CANDIDATE_STATE  # noqa: E402 -- shared hardened Git reads


# Compatibility names share the implementation and exception identities owned by WORKTREE.
MODEL_SELECTION = WORKTREE.MODEL_SELECTION
LAUNCH_AUTHORITY = WORKTREE.LAUNCH_AUTHORITY
DispatchError = WORKTREE.DispatchError
WorktreeBaselineError = WORKTREE.WorktreeBaselineError
ResolveUndoPresentError = WORKTREE.ResolveUndoPresentError
canonical = WORKTREE.canonical
digest = WORKTREE.digest
_identity = WORKTREE._identity
_parse_resolve_undo = WORKTREE._parse_resolve_undo
_bound_git_worktree_root = WORKTREE._bound_git_worktree_root
_bounded_git_read = WORKTREE._bounded_git_read
_build_selected_content_manifest = WORKTREE._build_selected_content_manifest
_canonical_digest = WORKTREE._canonical_digest
_cleanup_stage = WORKTREE._cleanup_stage
_compute_transmission_sha256 = WORKTREE._compute_transmission_sha256
_compute_v11_launch_approval_sha256 = WORKTREE._compute_v11_launch_approval_sha256
_confirm_safe_git_executable = WORKTREE._confirm_safe_git_executable
_fixed_git_read_argv = WORKTREE._fixed_git_read_argv
_full_stat_binding = WORKTREE._full_stat_binding
_git_boundary_identity = WORKTREE._git_boundary_identity
_manifest_digest = WORKTREE._manifest_digest
_marker_only_preflight = WORKTREE._marker_only_preflight
_materialize_stage = WORKTREE._materialize_stage
_parse_provider_scope = WORKTREE._parse_provider_scope
_project_boundary = WORKTREE._project_boundary
_read_provider_scope_file = partial(WORKTREE._read_provider_scope_file, error_type=WORKTREE.DispatchError)
_reconcile_stage_to_source = WORKTREE._reconcile_stage_to_source
_recover_reconciliation = WORKTREE._recover_reconciliation
_resolved_path_is_git_administration = WORKTREE._resolved_path_is_git_administration
_safe_git_executable = WORKTREE._safe_git_executable
_safe_git_is_outside_worktree = WORKTREE._safe_git_is_outside_worktree
_safe_git_owner_mode = WORKTREE._safe_git_owner_mode
_scan_readable_worktree = WORKTREE._scan_readable_worktree
_scan_stage_mutations = WORKTREE._scan_stage_mutations
_selected_content_digest = WORKTREE._selected_content_digest
_stable_git_authority = WORKTREE._stable_git_authority
_validate_manifest = WORKTREE._validate_manifest
_validate_scope_against_worktree = WORKTREE._validate_scope_against_worktree
_worktree_git_admin_alias_boundary = WORKTREE._worktree_git_admin_alias_boundary
_worktree_snapshot = WORKTREE._worktree_snapshot
_worktree_symlink_boundary = WORKTREE._worktree_symlink_boundary
whole_worktree_content_manifest = WORKTREE.whole_worktree_content_manifest
_MarkerPreflightLimit = WORKTREE._MarkerPreflightLimit
_FIXED_GIT_READ_ARGV = WORKTREE._FIXED_GIT_READ_ARGV

class _VerificationAPI:
    """Expose dispatcher dependencies to the optional verification adapter."""

    def __getattr__(self, name: str) -> Any:
        return globals()[name]


VERIFICATION_API = _VerificationAPI()

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
MAX_BOUNDARY_ENTRIES = WORKTREE.MAX_BOUNDARY_ENTRIES
MAX_INLINE_PROMPT_BYTES = 100000
MAX_STREAM_BYTES = WORKTREE.MAX_STREAM_BYTES
MAX_EVENT_BYTES = 1024 * 1024
MAX_STATUS_WAIT = 60.0
TERM_GRACE = WORKTREE.TERM_GRACE
CONTROL_POLL = 0.20
CONVERSATION_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}")
JOB_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,79}")
SHA_RE = re.compile(r"[0-9a-f]{64}")
COMMIT_RE = re.compile(r"[0-9a-f]{40}|[0-9a-f]{64}")
CURRENT_COMMAND_FIELDS = {
    'launch_authority',
    'launch_approval_sha256',
    'agy_version',
    'agy_version_observed',
    'allow_scoped_repair',
    'allow_self_verification',
    'approved_transmission_sha256',
    'approved_whole_worktree_sha256',
    'argv',
    'base_commit',
    'child_umask',
    'continue_prompt',
    'hard_seconds',
    'idle_seconds',
    'job_id',
    'kind',
    'max_cycles',
    'max_seconds',
    'native_grant_profile',
    'notice_seconds',
    'provider_env',
    'provider_isolation',
    'provider_scope_identity',
    'provider_scope_path',
    'provider_scope_sha256',
    'repair_authority_sha256',
    'resume_prompt',
    'schema_version',
    'selection_identity',
    'selection_path',
    'selection_sha256',
    'self_verification_manifest_identity',
    'self_verification_manifest_path',
    'self_verification_manifest_sha256',
    'stage_dir',
    'stage_file',
    'whole_worktree_content_sha256',
    'workdir',
    'workflow',
}
SCOPED_REPAIR_POLICY_TEXT = (
    "Scoped repair may transmit only controller-reconciled descendants under the "
    "unchanged initial scope, selection, workflow, provider environment, cycle, and time limits."
)
SCOPED_REPAIR_POLICY_SHA256 = hashlib.sha256(
    SCOPED_REPAIR_POLICY_TEXT.encode("utf-8")
).hexdigest()
CURRENT_STATE_FIELDS = {
    'initial_content_transmission_sha256',
    'agy_returncode',
    'allow_scoped_repair',
    'allow_self_verification',
    'approved_transmission_sha256',
    'assurance',
    'attempt',
    'attempt_base_elapsed',
    'attempt_origin',
    'cancel_requested',
    'candidate_recognized',
    'candidate_source',
    'candidate_worktree_entries',
    'candidate_worktree_path_facts',
    'candidate_worktree_sha256',
    'canonical_schema_identity',
    'canonical_schema_sha256',
    'check_counts',
    'check_summary',
    'command_identity',
    'command_sha256',
    'continue_available',
    'controller_pid',
    'conversation_id',
    'created_epoch',
    'cycle',
    'driver_disposition',
    'elapsed_seconds',
    'exit_code',
    'failure_stage',
    'finished_epoch',
    'hard_seconds',
    'idle_seconds',
    'job_id',
    'kind',
    'last_activity',
    'last_progress_epoch',
    'last_success_identity',
    'last_success_path',
    'last_success_sha256',
    'limit_kind',
    'max_cycles',
    'max_seconds',
    'native_grant_profile',
    'next_action',
    'next_action_command',
    'notice_count',
    'phase',
    'previous_state_sha256',
    'progress_count',
    'project_boundary',
    'provider_isolation',
    'provider_retry_after_seconds',
    'provider_retry_observed_epoch',
    'provider_schema_identity',
    'provider_schema_sha256',
    'provider_scope_identity',
    'provider_scope_path',
    'provider_scope_sha256',
    'provider_stage_identity',
    'provider_stage_manifest_sha256',
    'provider_stage_path',
    'provider_terminal_status',
    'reason',
    'reconciliation_manifest_sha256',
    'remote_cancel_unverified',
    'repair_authority_sha256',
    'repair_lineage_attempt',
    'repair_lineage_sha256',
    'repair_parent_result_sha256',
    'repair_parent_worktree_sha256',
    'result_available',
    'result_identity',
    'result_path',
    'result_sha256',
    'resume_available',
    'schema_version',
    'selected_content_sha256',
    'selected_file_count',
    'selected_tree_count',
    'selection_identity',
    'selection_sha256',
    'self_verification_elapsed_seconds',
    'self_verification_return_phase',
    'self_verification_run',
    'self_verification_started_epoch',
    'sequence',
    'stage_identity',
    'stage_sha256',
    'started_epoch',
    'status',
    'stderr_path',
    'stream_path',
    'transmission_sha256',
    'updated_epoch',
    'verification_identity',
    'verification_path',
    'verification_sha256',
    'whole_worktree_content_sha256',
    'workdir',
    'workflow',
    'worktree_baseline',
    'worktree_changed_since_dispatch',
    'worktree_changes_present',
    'worktree_reconciliation',
    'worktree_root_identity',
    'worktree_snapshot_algorithm',
}
PUBLIC_LAUNCHER = '"$PIPELINE/agy-worker.sh"'
CURRENT_STATE_SCHEMA = 18
CURRENT_COMMAND_SCHEMA = 16
LAST_DOCUMENTED_LEGACY_SCHEMA_RELEASE = "v0.22.0"
WORKTREE_SNAPSHOT_SEMANTIC_V1 = "semantic-v1"
CURRENT_WORKTREE_SNAPSHOT_ALGORITHM = WORKTREE_SNAPSHOT_SEMANTIC_V1
FAILURE_STAGES = {
    "framing", "outer_status", "missing_structured_output", "schema_rejection",
    "binding_failure", "selection_preflight",
}
FAILURE_STAGES.update(
    f"launch_authority_changed:{field}" for field in LAUNCH_AUTHORITY.AUTHORITY_FIELDS
)
FAILURE_STAGES.update(f"launch_authority_changed:content.{field}" for field in (
    "manifest_sha256", "policy_sha256", "selected_content_sha256", "content_manifest_sha256",
    "provider_isolation", "native_grant_profile"))
LIFECYCLE_PHASES = {
    "dispatching", "awaiting-verification", "repairing", "completed",
    "blocked", "attempt-failed", "repair-failed", "self-verifying",
}
TERMINAL = {"succeeded", "failed", "cancelled", "orphaned"}
REASONS = {
    "provider_timeout", "idle_timeout", "hard_deadline_exceeded",
    "authentication_failed", "provider_unavailable", "status_unavailable",
    "resume_failed", "cancelled", "agy_failed_unclassified",
    "permission_required", "empty_output", "invalid_envelope",
    "output_oversized", "interrupted", "provider_quota_exhausted",
    "provider_terminal_error", "provider_terminal_cancelled",
    "selection_preflight_failed", "model_selection_rejected", "resolve_undo_present",
    "native_host_sandbox_unavailable",
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
    "model_selection_rejected": 26,
    "native_host_sandbox_unavailable": 27,
    "provider_terminal_cancelled": 22,
    "interrupted": 143,
}

MODEL_SELECTION_REJECTED_MESSAGE = (
    "AGY rejected the model/effort selection. Check `agy models` and the "
    "`--model`/`--effort` pair before starting a new job."
)

MAX_PROVIDER_RETRY_SECONDS = 30 * 24 * 3600


class SelectionPreflightError(DispatchError):
    """A direct caller selection could not be safely reprobed for one launch."""


class Parser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        del message
        self.print_usage(sys.stderr)
        self.exit(64, "agy-dispatch: invalid arguments\n")


def _provider_isolation_for_command(command: dict[str, Any]) -> str:
    """Read the current command's explicit execution mode."""
    _require_supported_schema(command, label="dispatch command", supported=(CURRENT_COMMAND_SCHEMA,))
    mode = command.get("provider_isolation")
    if mode not in {"session", "native"}:
        raise DispatchError("dispatch provider isolation is invalid")
    return mode


def scoped_repair_authority_sha256(
    command: dict[str, Any], *, verification_binding_sha256: str | None = None,
) -> str | None:
    """Derive the immutable opt-in grant; future verification binds at creation."""
    if not command.get("allow_scoped_repair", False):
        return None
    if verification_binding_sha256 is not None and (
        not isinstance(verification_binding_sha256, str)
        or SHA_RE.fullmatch(verification_binding_sha256) is None
    ):
        raise DispatchError("repair verification binding is invalid")
    payload = {
        "kind": "agy-worker-scoped-repair-authority-v1",
        "policy_sha256": SCOPED_REPAIR_POLICY_SHA256,
        "initial_launch_approval_sha256": command.get("launch_approval_sha256"),
        "provider_scope_sha256": command.get("provider_scope_sha256"),
        "selection_sha256": command.get("selection_sha256"),
        "agy_version": command.get("agy_version"),
        "argv_sha256": digest(canonical(command.get("argv"))),
        "provider_env": command.get("provider_env"),
        "workflow": command.get("workflow"),
        "max_cycles": command.get("max_cycles"),
        "idle_seconds": command.get("idle_seconds"),
        "hard_seconds": command.get("hard_seconds"),
        "max_seconds": command.get("max_seconds"),
        "verification_binding_sha256": verification_binding_sha256,
    }
    payload["provider_isolation"] = command.get("provider_isolation")
    payload["native_grant_profile"] = command.get("native_grant_profile")
    return digest(canonical(payload))


def self_verification_binding_sha256(command: dict[str, Any]) -> str | None:
    """Bind the immutable private manifest fields without opening its bytes."""
    if not command.get("allow_self_verification", False):
        return None
    return digest(canonical({
        "kind": "agy-worker-self-verification-binding-v1",
        "manifest_path": command.get("self_verification_manifest_path"),
        "manifest_sha256": command.get("self_verification_manifest_sha256"),
        "manifest_identity": command.get("self_verification_manifest_identity"),
    }))


def _repair_authority_for_command(command: dict[str, Any]) -> str | None:
    """Compute repair authority with the command's optional manifest binding."""
    return scoped_repair_authority_sha256(
        command,
        verification_binding_sha256=self_verification_binding_sha256(command),
    )


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


def _bound_self_verification_manifest(
    command: dict[str, Any], job: Path | None = None,
) -> SELF_VERIFICATION.Manifest | None:
    """Reopen, bind, and parse the exact private manifest in its job."""
    if not command.get("allow_self_verification", False):
        return None
    path = Path(command["self_verification_manifest_path"])
    bound_job = path.parent if job is None else job
    try:
        canonical_path = Path(os.path.realpath(path))
    except OSError as exc:
        raise DispatchError("self-verification manifest is unavailable") from exc
    if (
        canonical_path != path
        or path.parent != bound_job
        or _job_is_inside_worktree(bound_job, command["workdir"])
    ):
        raise DispatchError("self-verification manifest path is invalid")
    raw, info = read_regular(path, MAX_COMMAND_BYTES, "self-verification manifest")
    if (
        digest(raw) != command["self_verification_manifest_sha256"]
        or list(_identity(info)) != command["self_verification_manifest_identity"]
    ):
        raise DispatchError("self-verification manifest binding changed")
    try:
        parsed = SELF_VERIFICATION.parse_manifest(raw)
        SELF_VERIFICATION.validate_runtime(parsed, Path(command["workdir"]))
        return parsed
    except SELF_VERIFICATION.VerificationError as exc:
        raise DispatchError("self-verification manifest is invalid") from exc


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
    _check_existing_dispatch_schemas(job)
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

    _check_existing_dispatch_schemas(job)
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


class UnsupportedSchemaError(DispatchError):
    """A fixed diagnostic for a record outside the supported schema boundary."""


def _require_supported_schema(
    value: Any, *, label: str, supported: tuple[int, ...],
) -> None:
    version = value.get("schema_version") if isinstance(value, dict) else None
    if type(version) is int and version in supported:
        return
    # Only bounded, retired positive integers enter a diagnostic. Never echo
    # arbitrary JSON values, strings, or unbounded/future version numbers.
    found = f"v{version}" if type(version) is int and 0 < version < max(supported) else "invalid or unsupported"
    expected = " or ".join(f"v{item}" for item in supported)
    raise UnsupportedSchemaError(
        f"{label} schema {found} is not supported by this agy-worker release; "
        f"supported: {expected}. Finish or discard the job with the "
        "release that created it."
    )


def _check_existing_command_schema(job: Path) -> None:
    """Reject retired commands before a state reader can recover or project."""
    try:
        raw, _info = read_regular(job / COMMAND_NAME, MAX_COMMAND_BYTES, "dispatch command")
        value = parse_json(raw, "dispatch command")
    except (OSError, DispatchError):
        # Preserve the existing handling of missing/corrupt command artifacts.
        # Their full binding remains owned by the ordinary command binder.
        return
    _require_supported_schema(value, label="dispatch command", supported=(CURRENT_COMMAND_SCHEMA,))


def _check_existing_dispatch_schemas(job: Path) -> None:
    """Reject decoded unsupported records before creating or chmodding locks.

    This bounded read is only an early rejection, never transition authority.
    Callers still reload and fully validate under their existing locks. Missing
    or corrupt bytes retain the ordinary reader's existing error handling.
    """
    try:
        raw, _info = read_regular(job / STATE_NAME, MAX_STATE_BYTES, "dispatch state")
        value = parse_json(raw, "dispatch state")
    except (OSError, DispatchError):
        pass
    else:
        _require_supported_schema(value, label="dispatch state", supported=(CURRENT_STATE_SCHEMA,))
    _check_existing_command_schema(job)


def load_state(job: Path) -> tuple[DispatchState, bytes, str]:
    raw, _info = read_regular(job / STATE_NAME, MAX_STATE_BYTES, "dispatch state")
    value = parse_json(raw, "dispatch state")
    value = validate_state(value)
    _check_existing_command_schema(job)
    return value, raw, digest(raw)


def read_state_snapshot(job: Path) -> tuple[DispatchState, bytes, str]:
    """Read one strict state snapshot without racing an approved replacement."""

    with state_lock(job):
        return load_state(job)


def load_command(job: Path) -> tuple[dict[str, Any], bytes, tuple[int, int, int, int, int]]:
    raw, info = read_regular(job / COMMAND_NAME, MAX_COMMAND_BYTES, "dispatch command")
    value = parse_json(raw, "dispatch command")
    _require_supported_schema(value, label="dispatch command", supported=(CURRENT_COMMAND_SCHEMA,))
    if not isinstance(value, dict):
        raise DispatchError("dispatch command fields are invalid")
    if set(value) != CURRENT_COMMAND_FIELDS:
        raise DispatchError("dispatch command fields are invalid")
    if raw != canonical(value):
        raise DispatchError("dispatch command is not canonical")
    if value["kind"] != "agy-worker-dispatch-command":
        raise DispatchError("dispatch command version is invalid")
    try:
        if (LAUNCH_AUTHORITY.approval_sha256(value["launch_authority"])
                != value["launch_approval_sha256"]
                or value["launch_approval_sha256"] != (
                    value["approved_transmission_sha256"]
                    if value["provider_scope_path"] is not None
                    else value["approved_whole_worktree_sha256"])):
            raise DispatchError("dispatch launch approval binding changed")
    except (LAUNCH_AUTHORITY.LaunchAuthorityError, TypeError, AttributeError) as exc:
        raise DispatchError("dispatch launch authority is invalid") from exc
    version = value["agy_version"]
    if (not isinstance(version, str) or not version or len(version.encode("utf-8")) > 128
            or any(ord(c) < 32 or ord(c) == 127 for c in version)):
        raise DispatchError("dispatch agy diagnostic version is invalid")
    if not isinstance(value["job_id"], str) or JOB_RE.fullmatch(value["job_id"]) is None:
        raise DispatchError("dispatch command job ID is invalid")
    if not isinstance(value["argv"], list) or not value["argv"] or any(
        not isinstance(item, str) or "\x00" in item for item in value["argv"]
    ):
        raise DispatchError("dispatch argv is invalid")
    if value["argv"][0] != "agy" or value["argv"].count("--print") != 1:
        raise DispatchError("dispatch argv contract is invalid")
    arguments = iter(value["argv"][1:])
    for argument in arguments:
        option = argument.partition("=")[0]
        if option in {
            "--agent", "--boost", "--approve-boost-risk-sha", "--persona",
            "--remote-control", "--input-format", "--project", "--new-project",
        }:
            raise DispatchError("dispatch argv contains a retired feature")
        if "=" not in argument and option in {
            "--print", "--model", "--mode", "--json-schema", "--add-dir",
            "--conversation", "--print-timeout", "--output-format",
        }:
            next(arguments, None)
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
    base_commit = value["base_commit"]
    if base_commit is not None and (
        not isinstance(base_commit, str) or COMMIT_RE.fullmatch(base_commit) is None
    ):
        raise DispatchError("dispatch base commit is invalid")
    if value["provider_scope_path"] is not None and base_commit is not None:
        raise DispatchError("scoped dispatch cannot carry a whole-worktree base")
    if (value["provider_scope_path"] is None
            and value["workflow"] in {"task", "project"} and base_commit is None):
        raise DispatchError("whole-worktree task base is missing")
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
    approved_whole_sha = value.get("approved_whole_worktree_sha256")
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
    if scope_path is None:
        if not isinstance(approved_whole_sha, str) or SHA_RE.fullmatch(approved_whole_sha) is None:
            raise DispatchError("dispatch whole-worktree approval binding is invalid")
    elif approved_whole_sha is not None:
        raise DispatchError("dispatch transmission modes conflict")
    provider_isolation = value["provider_isolation"]
    if provider_isolation not in {"session", "native"}:
        raise DispatchError("dispatch provider isolation is invalid")
    native_grant_profile = value["native_grant_profile"]
    if not isinstance(native_grant_profile, str) or native_grant_profile not in {"baseline", "A", "B", "AB"} or (
        provider_isolation == "session" and native_grant_profile != "baseline"
    ):
        raise DispatchError("dispatch native grant profile is invalid")
    whole_content_sha = value["whole_worktree_content_sha256"]
    if scope_path is None:
        if not isinstance(whole_content_sha, str) or SHA_RE.fullmatch(whole_content_sha) is None:
            raise DispatchError("dispatch whole-worktree content binding is invalid")
    elif whole_content_sha is not None:
        raise DispatchError("scoped dispatch cannot carry whole-worktree content")
    sandbox_count = value["argv"].count("--sandbox")
    if provider_isolation == "session" and sandbox_count != 0:
        raise DispatchError("session dispatch cannot request AGY sandbox")
    if provider_isolation == "native" and (
        scope_path is None or sandbox_count != 1
    ):
        raise DispatchError("native dispatch must be scoped and sandboxed")
    if scope_path is not None and "--add-dir" in value["argv"]:
        raise DispatchError("narrow provider scope cannot grant an additional directory")
    allow_self_verification = value["allow_self_verification"]
    self_verification_fields = (
        value["self_verification_manifest_path"],
        value["self_verification_manifest_sha256"],
        value["self_verification_manifest_identity"],
    )
    if type(allow_self_verification) is not bool:
        raise DispatchError("dispatch self-verification choice is invalid")
    if allow_self_verification and value["workflow"] not in {"task", "project"}:
        raise DispatchError("dispatch self-verification workflow is invalid")
    if not allow_self_verification:
        if any(item is not None for item in self_verification_fields):
            raise DispatchError("disabled self-verification cannot carry a manifest")
    elif (
        value["workflow"] not in {"task", "project"}
        or not isinstance(self_verification_fields[0], str)
        or not Path(self_verification_fields[0]).is_absolute()
        or not isinstance(self_verification_fields[1], str)
        or SHA_RE.fullmatch(self_verification_fields[1]) is None
        or not isinstance(self_verification_fields[2], list)
        or len(self_verification_fields[2]) != 5
        or any(type(item) is not int or item < 0 for item in self_verification_fields[2])
    ):
        raise DispatchError("dispatch self-verification manifest binding is invalid")
    allow_repair = value["allow_scoped_repair"]
    repair_authority = value["repair_authority_sha256"]
    if type(allow_repair) is not bool:
        raise DispatchError("dispatch scoped repair choice is invalid")
    if not allow_repair:
        if repair_authority is not None:
            raise DispatchError("disabled scoped repair cannot carry authority")
    elif (
        scope_path is None
        or value["workflow"] not in {"task", "project"}
        or value["max_cycles"] < 2
        or not isinstance(repair_authority, str)
        or SHA_RE.fullmatch(repair_authority) is None
        or repair_authority != _repair_authority_for_command(value)
    ):
        raise DispatchError("dispatch scoped repair authority is invalid")
    _bound_self_verification_manifest(value, job)
    return value, raw, _identity(info)


def _require_initial_transmission_choice(command: dict[str, Any], origin: str) -> None:
    """Reject a fresh broad launch unless its exact manifest was approved."""
    if (
        origin == "initial"
        and command.get("provider_scope_path") is None
        and command.get("approved_whole_worktree_sha256") is None
    ):
        raise DispatchError("initial whole-worktree dispatch lacks explicit approval")


class FileAuthority(TypedDict):
    dev: int
    ino: int
    type: int
    mode: int
    uid: int
    gid: int


class RootIdentity(TypedDict):
    realpath: str
    dev: int
    ino: int


class GitMarkerIdentity(TypedDict):
    kind: str
    authority: FileAuthority
    content_sha256: str | None


class GitDirectoryIdentity(TypedDict):
    realpath: str
    authority: FileAuthority


class WorktreeRootIdentity(TypedDict):
    root: RootIdentity
    git_marker: GitMarkerIdentity
    git_dir: GitDirectoryIdentity
    common_dir: GitDirectoryIdentity
    object_format: str
    show_toplevel: str


class WorktreeBaseline(TypedDict):
    sha256: str
    entries: int


class CheckCounts(TypedDict):
    passed: int
    failed: int
    advisory: int
    missing: int


class ProjectBoundary(TypedDict):
    kind: str
    # Validation guarantees the list's length, but does not constrain its elements.
    identity: list[object]
    sha256: str


class DispatchState(TypedDict):
    initial_content_transmission_sha256: str | None
    """Fields proven by validate_state; optional values remain explicitly nullable."""
    schema_version: int
    kind: str
    sequence: int
    previous_state_sha256: str | None
    job_id: str
    status: str
    attempt: int
    attempt_origin: str
    reason: str | None
    exit_code: int | None
    controller_pid: int | None
    workdir: str | None
    created_epoch: float
    started_epoch: float | None
    updated_epoch: float
    finished_epoch: float | None
    elapsed_seconds: float
    progress_count: int
    last_progress_epoch: float | None
    notice_count: int
    hard_seconds: float
    max_seconds: float
    idle_seconds: float
    attempt_base_elapsed: float
    cancel_requested: bool
    conversation_id: str | None
    resume_available: bool
    remote_cancel_unverified: bool
    result_path: str | None
    stream_path: str | None
    stderr_path: str | None
    agy_returncode: int | None
    limit_kind: str | None
    command_sha256: str | None
    command_identity: list[int] | None
    stage_sha256: str | None
    stage_identity: list[int] | None
    result_sha256: str | None
    result_identity: list[int] | None
    workflow: str
    max_cycles: int
    cycle: int
    phase: str
    assurance: str
    check_summary: str | None
    check_counts: CheckCounts
    verification_path: str | None
    verification_sha256: str | None
    verification_identity: list[int] | None
    continue_available: bool
    last_success_path: str | None
    last_success_sha256: str | None
    last_success_identity: list[int] | None
    project_boundary: ProjectBoundary | None
    provider_retry_after_seconds: int | None
    provider_retry_observed_epoch: float | None
    candidate_recognized: bool
    candidate_source: str
    result_available: bool
    worktree_reconciliation: str
    worktree_changes_present: bool | None
    worktree_changed_since_dispatch: bool | None
    driver_disposition: str
    failure_stage: str | None
    last_activity: str | None
    next_action: str
    next_action_command: str | None
    worktree_baseline: WorktreeBaseline | None
    provider_schema_sha256: str | None
    provider_schema_identity: list[int] | None
    canonical_schema_sha256: str | None
    canonical_schema_identity: list[int] | None
    candidate_worktree_sha256: str | None
    candidate_worktree_entries: int | None
    candidate_worktree_path_facts: dict[str, Any] | None
    selection_sha256: str | None
    selection_identity: list[int] | None
    worktree_snapshot_algorithm: str
    worktree_root_identity: WorktreeRootIdentity
    provider_terminal_status: str
    allow_scoped_repair: bool
    repair_authority_sha256: str | None
    repair_lineage_sha256: str | None
    repair_parent_result_sha256: str | None
    repair_parent_worktree_sha256: str | None
    repair_lineage_attempt: int | None
    allow_self_verification: bool
    self_verification_elapsed_seconds: float
    self_verification_run: int
    self_verification_started_epoch: float | None
    self_verification_return_phase: str | None
    provider_isolation: str
    provider_scope_path: str | None
    provider_scope_sha256: str | None
    provider_scope_identity: list[int] | None
    approved_transmission_sha256: str | None
    transmission_sha256: str | None
    selected_content_sha256: str | None
    selected_file_count: int | None
    selected_tree_count: int | None
    provider_stage_path: str | None
    provider_stage_identity: list[int] | None
    provider_stage_manifest_sha256: str | None
    reconciliation_manifest_sha256: str | None
    whole_worktree_content_sha256: str | None
    native_grant_profile: str


def _invalid_if(invalid: bool, message: str) -> None:
    if invalid:
        raise DispatchError(message)


def _validate_worktree_observation(item: Any) -> None:
    if item is not None and type(item) is not bool:
        raise DispatchError("dispatch worktree observation is invalid")


def _validate_boolean(item: Any) -> None:
    if type(item) is not bool:
        raise DispatchError("dispatch boolean is invalid")


def _validate_counter(item: Any) -> None:
    if type(item) is not int or item < 0:
        raise DispatchError("dispatch counter is invalid")


def _validate_time(item: Any) -> None:
    if type(item) not in (int, float) or item < 0:
        raise DispatchError("dispatch time is invalid")


def _validate_optional_time(item: Any) -> None:
    if item is not None and (type(item) not in (int, float) or item < 0):
        raise DispatchError("dispatch optional time is invalid")


def _validate_optional_integer(item: Any) -> None:
    if item is not None and type(item) is not int:
        raise DispatchError("dispatch integer is invalid")


def _validate_optional_path(item: Any) -> None:
    if item is not None and not isinstance(item, str):
        raise DispatchError("dispatch path is invalid")


def _validate_optional_digest(item: Any) -> None:
    if item is not None and (
        not isinstance(item, str) or SHA_RE.fullmatch(item) is None
    ):
        raise DispatchError("dispatch digest is invalid")


def _validate_optional_identity(item: Any) -> None:
    identity = item
    if identity is not None and (
        not isinstance(identity, list) or len(identity) != 5
        or any(type(item) is not int or item < 0 for item in identity)
    ):
        raise DispatchError("dispatch identity is invalid")


def _validate_fields(value: Mapping[str, Any], validators: dict[str, Callable[[Any], None]]) -> None:
    """Run one phase's field checks in their declared first-error order."""
    for key, validate in validators.items():
        validate(value[key])


def _validate_root_identity(value: Mapping[str, Any]) -> None:
    root_identity = value.get("worktree_root_identity")
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


def _validate_scope_state(value: Mapping[str, Any]) -> None:
    candidate_worktree_sha = value["candidate_worktree_sha256"]
    scope_path = value.get("provider_scope_path")
    scope_sha = value.get("provider_scope_sha256")
    scope_identity = value.get("provider_scope_identity")
    approved_sha = value.get("approved_transmission_sha256")
    initial_content_sha = value.get("initial_content_transmission_sha256")
    if (scope_path is None) != (initial_content_sha is None) or (
            initial_content_sha is not None and (not isinstance(initial_content_sha, str)
                                                or SHA_RE.fullmatch(initial_content_sha) is None)):
        raise DispatchError("dispatch initial content transmission binding is invalid")
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
    allow_repair = value["allow_scoped_repair"]
    repair_authority = value["repair_authority_sha256"]
    lineage_sha = value["repair_lineage_sha256"]
    parent_result_sha = value["repair_parent_result_sha256"]
    parent_worktree_sha = value["repair_parent_worktree_sha256"]
    lineage_attempt = value["repair_lineage_attempt"]
    if type(allow_repair) is not bool:
        raise DispatchError("dispatch scoped repair choice is invalid")
    if not allow_repair:
        if any(item is not None for item in (
            repair_authority, lineage_sha, parent_result_sha,
            parent_worktree_sha, lineage_attempt,
        )):
            raise DispatchError("disabled scoped repair has authority")
    elif (
        scope_path is None
        or value["workflow"] not in {"task", "project"}
        or value["max_cycles"] < 2
        or not isinstance(repair_authority, str)
        or SHA_RE.fullmatch(repair_authority) is None
    ):
        raise DispatchError("dispatch scoped repair authority is invalid")
    if lineage_sha is None:
        if any(item is not None for item in (
            parent_result_sha, parent_worktree_sha, lineage_attempt,
        )):
            raise DispatchError("dispatch repair lineage is incomplete")
    elif (
        not allow_repair
        or not isinstance(lineage_sha, str) or SHA_RE.fullmatch(lineage_sha) is None
        or parent_result_sha is not None and (
            not isinstance(parent_result_sha, str) or SHA_RE.fullmatch(parent_result_sha) is None
        )
        or parent_worktree_sha is not None and (
            not isinstance(parent_worktree_sha, str) or SHA_RE.fullmatch(parent_worktree_sha) is None
        )
        or type(lineage_attempt) is not int
        or not (1 <= lineage_attempt <= value["attempt"])
        or reconciliation_manifest_sha is None
        or candidate_worktree_sha is None
        or value["result_sha256"] is None
        or lineage_sha != _compute_repair_lineage_sha256(
            authority_sha256=repair_authority,
            attempt=lineage_attempt,
            parent_result_sha256=parent_result_sha,
            parent_worktree_sha256=parent_worktree_sha,
            reconciliation_sha256=reconciliation_manifest_sha,
            result_sha256=value["result_sha256"],
            candidate_worktree_sha256=candidate_worktree_sha,
            selected_content_sha256=cast(str, selected_content_sha),
            transmission_sha256=cast(str, transmission_sha),
        )
    ):
        raise DispatchError("dispatch repair lineage is invalid")


def _validate_self_verification_state(value: Mapping[str, Any]) -> None:
    allow_self_verification = value["allow_self_verification"]
    self_verification_elapsed = value["self_verification_elapsed_seconds"]
    self_verification_run = value["self_verification_run"]
    self_verification_started = value["self_verification_started_epoch"]
    self_verification_return = value["self_verification_return_phase"]
    if type(allow_self_verification) is not bool:
        raise DispatchError("dispatch self-verification choice is invalid")
    _validate_fields(value, {
        "workflow": lambda item: _invalid_if(allow_self_verification and item not in {'task', 'project'}, 'dispatch self-verification workflow is invalid'),
        "attempt": lambda item: _invalid_if(type(self_verification_elapsed) not in (int, float) or not math.isfinite(self_verification_elapsed) or self_verification_elapsed < 0 or (type(self_verification_run) is not int) or (not 0 <= self_verification_run <= item), 'dispatch self-verification accounting is invalid'),
    })
    if self_verification_started is not None and (
        type(self_verification_started) not in (int, float)
        or not math.isfinite(self_verification_started)
        or self_verification_started < 0
    ):
        raise DispatchError("dispatch self-verification start is invalid")
    if not allow_self_verification and (
        self_verification_elapsed != 0.0
        or self_verification_run != 0
        or self_verification_started is not None
        or self_verification_return is not None
    ):
        raise DispatchError("disabled self-verification has runtime state")
    if value["phase"] == "self-verifying":
        if (
            not allow_self_verification
            or value["continue_available"]
            or value["status"] not in {"succeeded", "failed"}
            or not value["candidate_recognized"] or not value["result_available"]
            or value["driver_disposition"] != "unreviewed" or value["assurance"] != "pending"
            or self_verification_run != value["attempt"]
            or self_verification_started is None
            or self_verification_return not in {
                "awaiting-verification", "repair-failed",
            }
        ):
            raise DispatchError("active self-verification state is invalid")
    elif self_verification_started is not None or self_verification_return is not None:
        raise DispatchError("inactive self-verification has active state")


def _validate_candidate_lifecycle(value: Mapping[str, Any]) -> None:
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
    _validate_fields(value, {
        "phase": lambda item: _invalid_if(item not in LIFECYCLE_PHASES, 'dispatch lifecycle phase is invalid'),
        "assurance": lambda item: _invalid_if(item not in {'pending', 'verified', 'partially_verified', 'rejected', 'blocked'}, 'dispatch lifecycle assurance is invalid'),
    })
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


def _validate_verification_state(value: Mapping[str, Any]) -> None:
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


def _validate_worktree_state(value: Mapping[str, Any]) -> None:
    if value["worktree_reconciliation"] not in {"available", "unavailable", "not_applicable"}:
        raise DispatchError("dispatch worktree reconciliation is invalid")
    _validate_fields(value, dict.fromkeys(('worktree_changes_present', 'worktree_changed_since_dispatch'), _validate_worktree_observation))
    if value["worktree_reconciliation"] == "available" and (
        value["worktree_changes_present"] is None or value["worktree_changed_since_dispatch"] is None
    ):
        raise DispatchError("dispatch worktree reconciliation is incomplete")
    if value["worktree_reconciliation"] != "available" and (
        value["worktree_changes_present"] is not None or value["worktree_changed_since_dispatch"] is not None
    ):
        raise DispatchError("dispatch unavailable worktree reconciliation has observations")
    _validate_fields(value, {
        "driver_disposition": lambda item: _invalid_if(item not in {'not_applicable', 'unreviewed', 'verified', 'partially_verified', 'rejected', 'blocked'}, 'dispatch driver disposition is invalid'),
        "failure_stage": lambda item: _invalid_if(item not in {None, *FAILURE_STAGES}, 'dispatch failure stage is invalid'),
        "last_activity": lambda item: _invalid_if(item not in {None, 'provider_initialized', 'progress_signal', 'terminal_received'}, 'dispatch activity is invalid'),
        "next_action": lambda item: _invalid_if(item not in {'none', 'wait', 'resume', 'restart', 'driver_review', 'driver_finalize', 'blocked'}, 'dispatch next action is invalid'),
        "next_action_command": lambda item: _invalid_if(item is not None and (not isinstance(item, str) or not item), 'dispatch next action command is invalid'),
    })
    baseline = value["worktree_baseline"]
    if baseline is not None and (
        not isinstance(baseline, dict) or set(baseline) != {"sha256", "entries"}
        or not isinstance(baseline["sha256"], str) or SHA_RE.fullmatch(baseline["sha256"]) is None
        or type(baseline["entries"]) is not int or not (0 <= baseline["entries"] <= MAX_BOUNDARY_ENTRIES)
    ):
        raise DispatchError("dispatch worktree baseline is invalid")
    candidate_worktree_sha = value["candidate_worktree_sha256"]
    candidate_worktree_entries = value["candidate_worktree_entries"]
    path_facts = value["candidate_worktree_path_facts"]
    if (candidate_worktree_sha is None) != (candidate_worktree_entries is None):
        raise DispatchError("dispatch candidate worktree binding is incomplete")
    if candidate_worktree_sha is not None and (
        not isinstance(candidate_worktree_sha, str)
        or SHA_RE.fullmatch(candidate_worktree_sha) is None
        or type(candidate_worktree_entries) is not int
        or not (0 <= candidate_worktree_entries <= MAX_BOUNDARY_ENTRIES)
    ):
        raise DispatchError("dispatch candidate worktree binding is invalid")
    if path_facts is not None:
        if (
            candidate_worktree_sha is None or not isinstance(path_facts, dict)
            or set(path_facts) != {"complete", "items"}
            or type(path_facts["complete"]) is not bool
            or not isinstance(path_facts["items"], list)
            or len(path_facts["items"]) > WORKTREE.DIAGNOSTIC_MAX_PATHS
        ):
            raise DispatchError("dispatch candidate path facts are invalid")
        path_bytes = 0
        seen_paths: set[str] = set()
        for item in path_facts["items"]:
            if not isinstance(item, list) or len(item) != 4:
                raise DispatchError("dispatch candidate path fact is invalid")
            path, kind, mode, fingerprint = item
            if (
                not isinstance(path, str) or not path or "\x00" in path
                or path.startswith("/") or any(part in {"", ".", ".."} for part in path.split("/"))
                or path in seen_paths or not isinstance(kind, str)
                or kind not in {"missing", "file", "symlink", "special"}
                or ((kind == "missing") != (mode is None))
                or (mode is not None and (type(mode) is not int or not 0 <= mode <= 0o7777))
                or not isinstance(fingerprint, str) or SHA_RE.fullmatch(fingerprint) is None
            ):
                raise DispatchError("dispatch candidate path fact is invalid")
            try:
                path_bytes += len(os.fsencode(path))
            except UnicodeError as exc:
                raise DispatchError("dispatch candidate path fact is invalid") from exc
            seen_paths.add(path)
        if path_bytes > WORKTREE.DIAGNOSTIC_MAX_PATH_BYTES:
            raise DispatchError("dispatch candidate path facts exceed limit")
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


def _validate_attempt_state(value: Mapping[str, Any]) -> None:
    _validate_fields(value, {
        "attempt_origin": lambda item: _invalid_if(item not in {'initial', 'conversation-resume', 'fresh-restart', 'conversation-continue'}, 'dispatch attempt origin is invalid'),
        "attempt": lambda item: _invalid_if(type(item) is not int or item < 1, 'dispatch attempt is invalid'),
        "workflow": lambda item: _invalid_if(item not in {'legacy', 'explore', 'task', 'project'}, 'dispatch workflow state is invalid'),
    })
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
    _validate_fields(value, dict.fromkeys(('cancel_requested', 'resume_available', 'continue_available', 'remote_cancel_unverified'), _validate_boolean))
    _validate_fields(value, dict.fromkeys(('progress_count', 'notice_count'), _validate_counter))
    _validate_fields(value, dict.fromkeys(('created_epoch', 'updated_epoch', 'elapsed_seconds', 'hard_seconds', 'max_seconds', 'idle_seconds', 'attempt_base_elapsed'), _validate_time))
    _validate_fields(value, dict.fromkeys(('started_epoch', 'finished_epoch', 'last_progress_epoch'), _validate_optional_time))
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
    _validate_fields(value, dict.fromkeys(('exit_code', 'controller_pid', 'agy_returncode'), _validate_optional_integer))
    _validate_fields(value, dict.fromkeys(('workdir', 'result_path', 'stream_path', 'stderr_path', 'verification_path', 'last_success_path'), _validate_optional_path))
    if value["limit_kind"] not in {None, "idle", "hard", "max-runtime"}:
        raise DispatchError("dispatch limit kind is invalid")
    _validate_fields(value, dict.fromkeys(('command_sha256', 'stage_sha256', 'result_sha256', 'verification_sha256', 'last_success_sha256'), _validate_optional_digest))
    _validate_fields(value, dict.fromkeys(('command_identity', 'stage_identity', 'result_identity', 'verification_identity', 'last_success_identity'), _validate_optional_identity))
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


def validate_state(value: Any) -> DispatchState:
    _require_supported_schema(value, label="dispatch state", supported=(CURRENT_STATE_SCHEMA,))
    if not isinstance(value, dict) or set(value) != CURRENT_STATE_FIELDS:
        raise DispatchError("dispatch state fields are invalid")
    _validate_fields(value, {
        "kind": lambda item: _invalid_if(item != 'agy-worker-dispatch-state', 'dispatch state version is invalid'),
        "provider_isolation": lambda item: _invalid_if(item not in {'session', 'native'}, 'dispatch provider isolation state is invalid'),
    })
    if not isinstance(value.get("native_grant_profile"), str) or value.get("native_grant_profile") not in {"baseline", "A", "B", "AB"} or (
        value["provider_isolation"] == "session" and value.get("native_grant_profile") != "baseline"
    ):
        raise DispatchError("dispatch native grant profile state is invalid")
    whole_content_sha = value.get("whole_worktree_content_sha256")
    if whole_content_sha is not None and (
        not isinstance(whole_content_sha, str) or SHA_RE.fullmatch(whole_content_sha) is None
    ):
        raise DispatchError("dispatch whole-worktree content state is invalid")
    if (value["worktree_snapshot_algorithm"] != CURRENT_WORKTREE_SNAPSHOT_ALGORITHM):
        raise DispatchError("dispatch worktree snapshot algorithm is invalid")
    if (value.get("provider_terminal_status") not in {"unknown", "success", "error", "cancelled"}):
        raise DispatchError("dispatch provider terminal status is invalid")
    _validate_root_identity(value)
    if type(value["sequence"]) is not int or value["sequence"] < 1:
        raise DispatchError("dispatch sequence is invalid")
    previous = value["previous_state_sha256"]
    if previous is not None and (not isinstance(previous, str) or SHA_RE.fullmatch(previous) is None):
        raise DispatchError("dispatch history is invalid")
    _validate_fields(value, {
        "sequence": lambda item: _invalid_if((item == 1) != (previous is None), 'dispatch history is inconsistent'),
        "status": lambda item: _invalid_if(item not in {'queued', 'running', 'cancel-requested', *TERMINAL}, 'dispatch status is invalid'),
        "reason": lambda item: _invalid_if(item is not None and item not in REASONS, 'dispatch reason is invalid'),
    })
    if type(value["candidate_recognized"]) is not bool or type(value["result_available"]) is not bool:
        raise DispatchError("dispatch candidate flags are invalid")
    if value["candidate_source"] not in {"none", "provider_success", "provider_error", "provider_cancelled"}:
        raise DispatchError("dispatch candidate source is invalid")
    if (
        value["candidate_recognized"] != (value["candidate_source"] != "none")
        or (value["result_available"] and not value["candidate_recognized"])
    ):
        raise DispatchError("dispatch candidate state is inconsistent")
    _validate_worktree_state(value)
    _validate_attempt_state(value)
    _validate_scope_state(value)
    _validate_self_verification_state(value)
    _validate_candidate_lifecycle(value)
    _validate_verification_state(value)
    # Exact shape and every field/cross-field rule have passed; preserve input identity.
    return cast(DispatchState, value)


def initial_state(
    command: dict[str, Any], origin: str, attempt: int, *, command_sha: str,
    command_identity: tuple[int, int, int, int, int], stage_sha: str | None,
    stage_identity: tuple[int, int, int, int, int] | None,
    project_boundary: Mapping[str, Any] | None = None,
    schema_bindings: dict[str, Any] | None = None,
    explain_worktree_rejection: bool = False,
    repair_authority_state: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    now = time.time()
    workflow = command.get("workflow", "legacy")
    max_cycles = command.get("max_cycles", 1)
    try:
        worktree_baseline = WORKTREE._worktree_snapshot(
            command["workdir"], explain_unsupported=explain_worktree_rejection)
    except ResolveUndoPresentError:
        worktree_baseline = None
    if worktree_baseline is not None:
        worktree_baseline = {key: worktree_baseline[key] for key in ("sha256", "entries")}
    state = {
        "schema_version": CURRENT_STATE_SCHEMA,
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
            else WORKTREE._project_boundary(command["workdir"]) if workflow == "project"
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
        "candidate_worktree_path_facts": None,
        "selection_sha256": command.get("selection_sha256"),
        "selection_identity": command.get("selection_identity"),
    }
    state["worktree_snapshot_algorithm"] = CURRENT_WORKTREE_SNAPSHOT_ALGORITHM
    root_identity = _dispatch_root_identity(command["workdir"])
    if root_identity is None:
        raise DispatchError("dispatch worktree root cannot be bound")
    state["worktree_root_identity"] = root_identity
    state["provider_terminal_status"] = "unknown"
    state.update({
        "allow_scoped_repair": command.get("allow_scoped_repair", False),
        "repair_authority_sha256": command.get("repair_authority_sha256"),
        "repair_lineage_sha256": None,
        "repair_parent_result_sha256": None,
        "repair_parent_worktree_sha256": None,
        "repair_lineage_attempt": None,
        "allow_self_verification": command.get("allow_self_verification", False),
        "self_verification_elapsed_seconds": 0.0,
        "self_verification_run": 0,
        "self_verification_started_epoch": None,
        "self_verification_return_phase": None,
    })
    state["provider_isolation"] = _provider_isolation_for_command(command)
    if command.get("provider_scope_path") is not None:
        _scope_path, raw_scope, scope_info = _read_provider_scope_file(
            command["provider_scope_path"], MAX_COMMAND_BYTES,
        )
        if digest(raw_scope) != command["provider_scope_sha256"]:
            raise DispatchError("provider scope file changed since dispatch")
        if list(_identity(scope_info)) != command["provider_scope_identity"]:
            raise DispatchError("provider scope file identity changed since dispatch")
        try:
            scope = WORKTREE._parse_provider_scope(raw_scope)
        except ValueError as exc:
            raise DispatchError(f"invalid provider scope: {exc}") from exc
        readable_manifest = WORKTREE._scan_readable_worktree(command["workdir"])
        manifest_sha = WORKTREE._manifest_digest(readable_manifest)
        WORKTREE._validate_scope_against_worktree(scope, command["workdir"], readable_manifest)
        selected_manifest = WORKTREE._build_selected_content_manifest(command["workdir"], scope)
        selected_sha = WORKTREE._selected_content_digest(selected_manifest)
        policy_sha = WORKTREE._canonical_digest(scope)
        transmission_sha = _bound_transmission_sha256(
            command, policy_sha, manifest_sha, selected_sha,
        )
        _require_scoped_transmission_authority(
            command,
            state if repair_authority_state is None else repair_authority_state,
            selected_content_sha256=selected_sha,
            transmission_sha256=transmission_sha,
            provider_origin=origin,
        )
        state.update({
            "provider_scope_path": command["provider_scope_path"],
            "provider_scope_sha256": command["provider_scope_sha256"],
            "provider_scope_identity": command["provider_scope_identity"],
            "approved_transmission_sha256": command["approved_transmission_sha256"],
            "transmission_sha256": transmission_sha,
            "initial_content_transmission_sha256": _initial_content_transmission(command),
            "selected_content_sha256": selected_sha,
            "selected_file_count": sum(1 for e in selected_manifest if e["kind"] == "file"),
            "selected_tree_count": sum(1 for e in selected_manifest if e["kind"] == "directory"),
            "provider_stage_path": None,
            "provider_stage_identity": None,
            "provider_stage_manifest_sha256": None,
            "reconciliation_manifest_sha256": None,
        })
    else:
        approved_whole_sha = command.get("approved_whole_worktree_sha256")
        if approved_whole_sha is not None and origin == "initial":
            content = WORKTREE.whole_worktree_content_manifest(command["workdir"])
            content_sha = content["manifest_sha256"]
            readable_manifest = WORKTREE._scan_readable_worktree(command["workdir"])
            if content_sha != command["whole_worktree_content_sha256"]:
                raise DispatchError("whole-worktree content binding changed")
            if WORKTREE._manifest_digest(readable_manifest) != command["launch_authority"]["content"]["manifest_sha256"]:
                raise DispatchError(
                    "approved whole-worktree manifest does not match current worktree"
                )
        state.update({
            "provider_scope_path": None,
            "provider_scope_sha256": None,
            "provider_scope_identity": None,
            "approved_transmission_sha256": None,
            "initial_content_transmission_sha256": None,
            "transmission_sha256": None,
            "selected_content_sha256": None,
            "selected_file_count": None,
            "selected_tree_count": None,
            "provider_stage_path": None,
            "provider_stage_identity": None,
            "provider_stage_manifest_sha256": None,
            "reconciliation_manifest_sha256": None,
        })
    state["whole_worktree_content_sha256"] = command.get("whole_worktree_content_sha256")
    state["native_grant_profile"] = command.get("native_grant_profile", "baseline")
    return state


def _transition_locked(
    job: Path, state: Mapping[str, Any], prior_raw: bytes, updates: dict[str, Any],
) -> tuple[DispatchState, bytes, str]:
    current, _info = read_regular(job / STATE_NAME, MAX_STATE_BYTES, "dispatch state")
    if current != prior_raw:
        raise DispatchError("dispatch state changed before transition")
    value = dict(state)
    value.update(updates)
    value["next_action"] = "none"
    value["next_action_command"] = None
    value["sequence"] = state["sequence"] + 1
    value["previous_state_sha256"] = digest(prior_raw)
    value["updated_epoch"] = time.time()
    validate_state(value)
    raw, sha = write_atomic(job, STATE_NAME, value)
    return validate_state(value), raw, sha


def transition(job: Path, state: Mapping[str, Any], prior_raw: bytes, updates: dict[str, Any]) -> tuple[DispatchState, bytes, str]:
    with state_lock(job):
        return _transition_locked(job, state, prior_raw, updates)


def _live_elapsed(value: Mapping[str, Any], now: float) -> float:
    elapsed = float(value["elapsed_seconds"])
    if value["status"] in {"running", "cancel-requested"} and value["started_epoch"] is not None:
        elapsed = max(
            elapsed,
            float(value["attempt_base_elapsed"]) + max(0.0, now - float(value["started_epoch"])),
        )
    return elapsed


def _verification_live_elapsed(value: Mapping[str, Any], now: float) -> float:
    elapsed = float(value.get("self_verification_elapsed_seconds", 0.0))
    started = value.get("self_verification_started_epoch")
    if value.get("phase") == "self-verifying" and started is not None:
        elapsed += max(0.0, now - float(started))
    return elapsed


def _total_live_elapsed(value: Mapping[str, Any], now: float) -> float:
    return _live_elapsed(value, now) + _verification_live_elapsed(value, now)


def _provider_max_seconds(value: Mapping[str, Any]) -> float:
    """Keep provider hard/idle clocks separate from the shared job allowance."""
    return max(0.0, float(value["max_seconds"])
               - float(value.get("self_verification_elapsed_seconds", 0.0)))


def _freeze_reaped_runtime(
    job: Path, attempt: int, controller_pid: int, elapsed: float,
) -> tuple[DispatchState, bytes, str, str | None]:
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
            if frozen_elapsed >= _provider_max_seconds(current):
                deadline = "max-runtime"
            elif frozen_elapsed >= float(current["hard_seconds"]):
                deadline = "hard"
        return current, raw, sha, deadline


def _is_active(value: Mapping[str, Any]) -> bool:
    return value["status"] in {"queued", "running", "cancel-requested"}


def _extend_is_eligible(value: Mapping[str, Any], now: float) -> bool:
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
        and float(value["hard_seconds"]) + 1.0 <= _provider_max_seconds(value)
    )


def _resume_is_eligible(value: Mapping[str, Any], now: float) -> bool:
    """Mirror the strict same-conversation resume guard used before staging."""
    return bool(
        value["status"] == "failed"
        and not value["candidate_recognized"]
        and value.get("reason") not in {"selection_preflight_failed", "model_selection_rejected", "permission_required"}
        and value["resume_available"]
        and isinstance(value["conversation_id"], str)
        and _restart_guard_accepts(value, elapsed_seconds=_live_elapsed(value, now))
    )


def _continue_is_eligible(value: Mapping[str, Any], now: float) -> bool:
    """Return the state-only half of the exact continuation guard."""
    return bool(value["continue_available"] and _continue_from_facts(value, now))


def _continue_from_facts(value: Mapping[str, Any], now: float) -> bool:
    """Recompute eligibility after verification without a circular stored flag."""
    return bool(
        value["workflow"] != "legacy"
        # A failed final direct-selection proof invalidates provider launch
        # authority for this frozen job.  Keep its bound candidate available
        # for result review/finalization, but never reuse the selection through
        # another same-conversation continuation.
        # A provider-reported permission denial likewise preserves the candidate
        # for review, but is not authority for an automatic continuation.
        and value["reason"] not in {"selection_preflight_failed", "model_selection_rejected", "permission_required"}
        and value["candidate_recognized"]
        and value["result_available"]
        and value["candidate_source"] != "provider_cancelled"
        and value["status"] in {"succeeded", "failed"}
        and _controller_phase(value) in {"awaiting-verification", "repair-failed"}
        and isinstance(value["conversation_id"], str)
        and value["cycle"] < value["max_cycles"]
        and _total_live_elapsed(value, now) < float(value["max_seconds"])
        and (
            value.get("provider_scope_path") is None
            or value.get("transmission_sha256") == value.get("initial_content_transmission_sha256")
            or (
                value.get("allow_scoped_repair", False)
                and value.get("repair_lineage_sha256") is not None
                and value.get("repair_lineage_attempt") == value["attempt"]
            )
        )
    )


def _finalize_is_eligible(value: Mapping[str, Any]) -> bool:
    """Return the state-only half of the exact finalization guard."""
    return bool(
        value["candidate_recognized"] and value["result_available"]
        and value["result_path"] and value["workflow"] != "legacy"
        and value["driver_disposition"] == "unreviewed"
        and (value["assurance"] == "pending")
        and _controller_phase(value) in {"awaiting-verification", "repair-failed"}
    )


def _verification_copy_is_eligible(value: Mapping[str, Any]) -> bool:
    """Return the exact state predicate for the current candidate copy helper."""
    return bool(
        _finalize_is_eligible(value)
    )


def _controller_phase(value: Mapping[str, Any]) -> str | None:
    """Project controller-owned mechanics from the current bound state."""
    if value.get("phase") == "self-verifying":
        return "self-verifying"
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


def _candidate_actions_are_bound(job: Path | None, value: Mapping[str, Any]) -> bool:
    """Keep public candidate actions as strict as their mutating commands."""
    if job is None:
        return False
    try:
        _bound_current_candidate(job, value)
    except UnsupportedSchemaError:
        raise
    except (OSError, DispatchError):
        return False
    return True


def _post_candidate_selection_binding_drift(job: Path | None, value: Mapping[str, Any]) -> bool:
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
    except UnsupportedSchemaError:
        raise
    except (OSError, DispatchError):
        return False
    if command.get("selection_path") is None:
        return False
    try:
        _load_bound_selection(command, value)
    except UnsupportedSchemaError:
        raise
    except (OSError, DispatchError):
        return True
    return False


def _lifecycle_mutation_bindings(
    job: Path | None, value: Mapping[str, Any],
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
    except UnsupportedSchemaError:
        raise
    except (OSError, DispatchError):
        return False, False
    try:
        _bound_lifecycle_inputs(bound_job, value, command)
        provider_launch_bound = (
            not _job_is_inside_worktree(bound_job, command["workdir"])
            and _selection_launch_is_authorized(
                _load_bound_selection(command, value)
            )
        )
    except UnsupportedSchemaError:
        raise
    except (OSError, DispatchError):
        # A changed current scoped candidate is valid driver evidence, but
        # transmitting those new bytes again requires a fresh exact approval
        # that the continuation interface cannot collect. Keep result/finalize
        # available while declining to advertise provider continuation.
        if not (
            value['candidate_recognized'] and value['status'] in TERMINAL
        ):
            return False, False
        try:
            _bound_current_candidate(bound_job, value)
        except UnsupportedSchemaError:
            raise
        except (OSError, DispatchError):
            return False, False
        return True, False
    return True, provider_launch_bound


def _selection_launch_is_authorized(record: dict[str, Any] | None) -> bool:
    return record is None or (
        record.get("schema_version") == MODEL_SELECTION.SELECTION_SCHEMA
        and MODEL_SELECTION.has_current_probed_executable_binding(record.get("probed_executable"))
    )


def _available_actions(
    value: Mapping[str, Any], sha: str, now: float, *, job: Path | None = None,
    candidate_bound: bool | None = None,
    lifecycle_mutation_bound: bool | None = None,
    provider_launch_bound: bool | None = None,
) -> list[dict[str, Any]]:
    """Return only state/time-applicable mechanical controller operations.

    Cancel and extend remain cheap state/time controls.  A terminal candidate is
    revalidated only when it could make a result, continue, or finalize action
    visible, and uses the same binder the command paths require.
    """
    job_id = value["job_id"]
    actions: list[dict[str, Any]] = []
    if value.get("phase") == "self-verifying":
        return [{
            "action": "wait",
            "command": f"{PUBLIC_LAUNCHER} wait --job-id {job_id} --after-state-sha {sha} --format text",
        }]
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
        try:
            CONTAINMENT.require_supported_host()
            self_verification_host_supported = True
        except CONTAINMENT.ContainmentError:
            self_verification_host_supported = False
        if (
            value.get("allow_self_verification")
            and self_verification_host_supported
            and value.get("self_verification_run", 0) < value["attempt"]
            and value.get("phase") in {"awaiting-verification", "repair-failed"}
            and _total_live_elapsed(value, now) < value["max_seconds"]
            and job is not None
            and not _job_is_inside_worktree(job, value["workdir"])
            and lifecycle_mutation_bound is True
        ):
            actions.append({
                "action": "self-verify",
                "command": f"{PUBLIC_LAUNCHER} self-verify --job-id {job_id} --approve-state-sha {sha} --format text",
            })
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
                    "--destination NEW_DIRECTORY_IN_0700_PARENT --format text"
                ),
                "requires": ["new owner-private destination outside the candidate"],
            })
    # A public recovery operation is useful only when the same frozen command,
    # schemas, worktree root/boundary, and selector the command will use are
    # still present.  ``None`` keeps pure in-memory compatibility callers from
    # claiming a failed local probe; CLI status always supplies a concrete bool.
    lifecycle_mutation_available = bool(
        lifecycle_mutation_bound is not False
    )
    provider_mutation_available = bool(
        lifecycle_mutation_available and provider_launch_bound is not False
    )
    if _resume_is_eligible(value, now) and provider_mutation_available:
        actions.append({
            "action": "resume",
            "command": (
                f"{PUBLIC_LAUNCHER} resume --job-id {job_id} --approve-state-sha {sha}"
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
                + " --format text"
            ),
        })
    if (
        terminal_candidate and candidate_bound and _continue_is_eligible(value, now)
        and provider_mutation_available
    ):
        stored_feedback = False
        if job is not None and value.get("allow_self_verification"):
            try:
                _bound_self_verification_feedback(job, value)
                stored_feedback = True
            except UnsupportedSchemaError:
                raise
            except (DispatchError, OSError):
                pass
        actions.append({
            "action": "continue",
            "command": (
                f"{PUBLIC_LAUNCHER} continue --job-id {job_id} --approve-state-sha {sha} "
                + ("--use-self-verification" if stored_feedback else "< DRIVER_VERIFICATION_JSON")
            ),
            "requires": [] if stored_feedback else ["verification JSON"],
        })
    if (
        terminal_candidate and candidate_bound and _finalize_is_eligible(value)
        and lifecycle_mutation_available
    ):
        actions.append({
            "action": "finalize",
            "command": (
                f"{PUBLIC_LAUNCHER} finalize --job-id {job_id} --approve-state-sha {sha} "
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


def _cycle_budget_explanation(value: Mapping[str, Any]) -> str | None:
    if value["status"] == "cancelled" and value["reason"] == "interrupted" and not value["candidate_recognized"]:
        return "The interrupted attempt consumed one cycle even though it produced no candidate; a fresh restart consumes another cycle."
    return None


def _provider_execution_from_bound_command(command: dict[str, Any]) -> dict[str, Any]:
    """Describe the current bound launch mechanics."""

    provider_isolation = _provider_isolation_for_command(command)
    scoped = command.get("provider_scope_path") is not None
    sandboxed = "--sandbox" in command["argv"]
    return {
        "legacy": False,
        "scope": "provider-scope" if scoped else "whole-worktree",
        "agy_sandbox": sandboxed,
        "native_containment": provider_isolation == "native",
    }


def bound_provider_execution(job: Path, state: Mapping[str, Any]) -> dict[str, Any]:
    """Bind execution facts to the command, not the state projection."""

    command = _load_bound_command(job, state, stage_readonly=False)
    return _provider_execution_from_bound_command(command)


def public_status(value: Mapping[str, Any], sha: str, *, job: Path | None = None) -> dict[str, Any]:
    _require_supported_schema(value, label="dispatch state", supported=(CURRENT_STATE_SCHEMA,))
    if job is not None:
        _check_existing_command_schema(job)
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
    lifecycle_mutation_bound: bool | None = None
    provider_launch_bound: bool | None = None
    terminal_candidate = bool(
        not _is_active(value) and value.get("phase") != "self-verifying" and value["status"] in TERMINAL
        and value["candidate_recognized"] and value["result_available"]
    )
    if terminal_candidate:
        candidate_bound = _candidate_actions_are_bound(job, value)
        # Candidate reconciliation can take meaningful bounded time.  Resample
        # the clocks so an extension that expired during that scan is omitted.
        now = time.time()
        elapsed = _live_elapsed(value, now)
    if job is not None and (
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
        lifecycle_mutation_bound=lifecycle_mutation_bound,
        provider_launch_bound=provider_launch_bound,
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
    provider_execution = None
    if job is not None:
        try:
            provider_execution = bound_provider_execution(job, value)
        except UnsupportedSchemaError:
            raise
        except (OSError, DispatchError):
            provider_execution = None
    public_provider_isolation = (
        value["provider_isolation"]
        if job is None else
        None
        if provider_execution is None or provider_execution["legacy"] else
        value["provider_isolation"]
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
        "self_verification_elapsed_seconds": round(_verification_live_elapsed(value, now), 3),
        "total_elapsed_seconds": round(_total_live_elapsed(value, now), 3),
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
        "cycle_budget_explanation": _cycle_budget_explanation(value),
        "notice_count": value["notice_count"],
        "progress_count": value["progress_count"],
        "provider_isolation": public_provider_isolation,
        "provider_execution": provider_execution,
        "controller_phase": _controller_phase(value),
        "phase": value["phase"],
        "legacy_result_provenance": (
            "none"
        ),
        "migration_binding_sha256": None,
        "reason": value["reason"],
        "reason_message": (
            MODEL_SELECTION_REJECTED_MESSAGE
            if value["reason"] == "model_selection_rejected" else None
        ),
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


def print_text_status(value: Mapping[str, Any], sha: str, *, job: Path | None = None) -> None:
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
    finalized_result = bool(
        result_command is not None
        and value["driver_disposition"] in {
            "verified", "partially_verified", "rejected", "blocked",
        }
    )
    candidate_decision = (
        "then the driver chooses an eligible continue or finalize."
        if {"continue", "finalize"} <= action_names else
        "then the driver may choose the eligible continue action."
        if "continue" in action_names else
        "then the driver may choose the eligible finalize action."
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
        f"Provider attempt: {value['status']}; reason: {reason}; failure stage: {failure_stage}; bound result available: {'yes' if public['result_available'] else 'no'}; driver disposition: {value['driver_disposition']}."
        + (f" {public['reason_message']}" if public["reason_message"] else "")
        + (" macOS denied native sandbox_apply; this can occur when the driver host is already sandboxed. Use a compatible driver host with the same approved native mode." if reason == "native_host_sandbox_unavailable" else ""),
        f"Driver evidence: {counts['passed']} passed, {counts['failed']} failed, {counts['advisory']} advisory, {counts['missing']} missing; cycle: {public['cycle']}/{public['max_cycles']}."
        + (f" {public['cycle_budget_explanation']}" if public['cycle_budget_explanation'] else ""),
        (
            (
                f"Next safe action: retrieve current bound result JSON with {result_command}; review it and run driver checks, then the driver may finalize after review. No provider-launching same-job recovery is available."
                if result_command is not None and "finalize" in action_names else
                f"Next safe action: retrieve current bound result JSON with {result_command}; no provider-launching same-job recovery is available."
                if result_command is not None else
                "Next safe action: create a fresh job using the unchanged caller selection after reviewing the current sanitized agy interface evidence. No same-job action is available."
            )
            if selection_preflight_recovery_blocked else
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
    value: Mapping[str, Any], sha: str, output_format: str, *, job: Path | None = None,
) -> None:
    if output_format == "text":
        print_text_status(value, sha, job=job)
    else:
        print_json(public_status(value, sha, job=job))


def _state_approval_error(state: Mapping[str, Any], sha: str, action: str) -> DispatchError:
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


def _bound_whole_worktree_base(workdir: str, expected: str | None, workflow: str) -> str | None:
    """Bind the gate's Git reference to HEAD before the first worker launch."""
    if expected is not None and COMMIT_RE.fullmatch(expected) is None:
        raise DispatchError("base commit is invalid")
    try:
        actual = CANDIDATE_STATE._git(
            Path(workdir), "rev-parse", "--verify", "HEAD^{commit}",
        ).decode("ascii", "strict").strip()
    except (CANDIDATE_STATE.CandidateStateError, UnicodeError):
        if expected is not None or workflow in {"task", "project"}:
            raise DispatchError("Git base is unavailable") from None
        return None
    if COMMIT_RE.fullmatch(actual) is None or (expected is not None and expected != actual):
        raise DispatchError("Git HEAD differs from the immutable base commit")
    return actual


def _whole_worktree_change_hint(workdir: Path, base: str) -> str:
    """Show preexisting and prior-cycle changes without making worker claims evidence."""
    try:
        raw = CANDIDATE_STATE._git(
            workdir, "diff", "--name-status", "--no-renames", "-z", base, "--",
        )
        parts = [part for part in raw.split(b"\0") if part]
        if len(parts) % 2:
            raise DispatchError("Git change summary is invalid")
        changes = [
            {"path": parts[index + 1].decode("utf-8", "surrogateescape"),
             "change": {b"A": "created", b"D": "deleted"}.get(parts[index], "modified")}
            for index in range(0, len(parts), 2)
        ]
        untracked = CANDIDATE_STATE._git(
            workdir, "ls-files", "--others", "--exclude-standard", "-z", "--",
        )
        changes.extend(
            {"path": path.decode("utf-8", "surrogateescape"), "change": "created"}
            for path in untracked.split(b"\0") if path
        )
        ignored = CANDIDATE_STATE._git(
            workdir, "ls-files", "--others", "--ignored", "--exclude-standard", "-z", "--",
        )
        changes.extend(
            {"path": path.decode("utf-8", "surrogateescape"), "change": "created"}
            for path in ignored.split(b"\0") if path
        )
    except CANDIDATE_STATE.CandidateStateError as exc:
        raise DispatchError("Git change summary is unavailable") from exc
    if len(changes) > 64:
        return (f"Driver currently observes {len(changes)} changed paths against the base; "
                "the list is too long for this prompt. Report all net changes you can establish; "
                "the gate will reject omissions.")
    changes.sort(key=lambda item: item["path"])
    encoded = json.dumps(changes, ensure_ascii=True, separators=(",", ":"))
    if len(encoded.encode("utf-8")) > 8192:
        return (f"Driver currently observes {len(changes)} changed paths against the base; "
                "the list is too long for this prompt. Report all net changes you can establish; "
                "the gate will reject omissions.")
    return "Driver currently observes these net changes against the base: " + encoded


def _bind_workspace_prompt(
    argv: list[str], workspace_root: Path, *, scoped: bool,
    provider_isolation: str, base_commit: str | None = None,
) -> str:
    """Bind every worker's file tools to the exact provider launch cwd."""
    if argv.count("--print") != 1:
        raise DispatchError("dispatch argv contract is invalid")
    print_index = argv.index("--print")
    if print_index + 1 >= len(argv):
        raise DispatchError("dispatch argv contract is invalid")
    prompt = argv[print_index + 1]
    if provider_isolation not in {"session", "native"}:
        raise DispatchError("dispatch provider isolation is invalid")
    hint = _whole_worktree_change_hint(workspace_root, base_commit) if not scoped and base_commit else ""
    prefix = LAUNCH_AUTHORITY.workspace_prefix(
        workspace_root, scoped=scoped, provider_isolation=provider_isolation,
        base_commit=base_commit, change_hint=hint)
    expected = prefix + prompt
    argv[print_index + 1] = expected
    return expected


def _init_cwd_matches_launch(init_value: dict[str, Any], launch_cwd: str) -> bool:
    """Bind a provider-reported cwd only when the stream protocol supplies one."""
    reported = init_value.get("cwd")
    if reported is None:
        return True
    if not isinstance(reported, str) or not reported or "\x00" in reported:
        return False
    try:
        return (
            os.path.isabs(reported)
            and reported == os.path.realpath(reported)
            and reported == os.path.realpath(launch_cwd)
        )
    except OSError:
        return False


def _provider_environment(command: dict[str, Any]) -> dict[str, str]:
    """Use the existing curated child environment for both launch modes."""

    if _provider_isolation_for_command(command) in {"session", "native"}:
        return MODEL_SELECTION.child_environment(command["provider_env"])
    raise DispatchError("dispatch provider isolation is invalid")


def _stage_relative_declared_path(path: str, stage_dir: Path) -> str | None:
    """Accept a canonical absolute report only when it names this exact stage."""
    if not path or "\x00" in path:
        return None
    if os.path.isabs(path):
        root = str(stage_dir)
        if (
            not os.path.isabs(root)
            or os.path.normpath(root) != root
            or not path.startswith(root + os.sep)
        ):
            return None
        path = path[len(root) + 1:]
    if (
        not path
        or os.path.normpath(path) != path
        or any(part in {"", ".", ".."} for part in path.split(os.sep))
    ):
        return None
    return path


def _canonicalize_scoped_report_paths(value: dict[str, Any], stage_dir: Path) -> dict[str, Any]:
    """Canonicalize only exact stage-child claims before envelope binding."""
    declared = value.get("files_changed")
    if not isinstance(declared, list):
        return value
    normalized: list[Any] = []
    for item in declared:
        if not isinstance(item, dict):
            normalized.append(item)
            continue
        rewritten = dict(item)
        path = rewritten.get("path")
        if isinstance(path, str) and os.path.isabs(path):
            relative_path = _stage_relative_declared_path(path, stage_dir)
            if relative_path is not None:
                rewritten["path"] = relative_path
        normalized.append(rewritten)
    return {**value, "files_changed": normalized}


def _declared_scoped_mutations_match(
    envelope: Path, binding: tuple[str, tuple[int, int, int, int, int]],
    operations: list[dict[str, Any]], stage_dir: Path,
) -> bool:
    """Require an envelope to declare exactly the staged operations to reconcile."""
    try:
        raw, info = read_regular(envelope, 1024 * 1024, "dispatch result")
        if digest(raw) != binding[0] or _identity(info) != binding[1]:
            return False
        value = parse_json(raw, "dispatch result")
        declared = value.get("files_changed") if isinstance(value, dict) else None
    except (DispatchError, OSError):
        return False
    if not isinstance(declared, list):
        return False
    mapping = {"create": "created", "replace": "modified", "delete": "deleted"}
    expected: set[tuple[str, str]] = set()
    for operation in operations:
        # The public envelope contract declares files, while reconciliation
        # carries directory scaffolding so nested file operations can be
        # applied descriptor-safely. Directory operations are not reportable
        # through ``files_changed`` and therefore cannot be part of this exact
        # file declaration comparison.
        if operation.get("kind") != "file":
            continue
        path, op = operation.get("path"), operation.get("op")
        change = mapping.get(op) if isinstance(op, str) else None
        if not isinstance(path, str) or change is None:
            return False
        item = (path, change)
        if item in expected:
            return False
        expected.add(item)
    observed: set[tuple[str, str]] = set()
    for item in declared:
        if not isinstance(item, dict):
            return False
        path, change = item.get("path"), item.get("change")
        if not isinstance(path, str) or not isinstance(change, str):
            return False
        relative_path = _stage_relative_declared_path(path, stage_dir)
        if relative_path is None:
            return False
        key = (relative_path, change)
        if key in observed:
            return False
        observed.add(key)
    return observed == expected


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


def _require_current_candidate_verification(value: Mapping[str, Any], state: Mapping[str, Any]) -> None:
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


def _bound_verification(job: Path, state: Mapping[str, Any]) -> Path | None:
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


def _bound_transmission_sha256(
    command: dict[str, Any], policy_sha256: str,
    readable_manifest_sha256: str, selected_content_sha256: str,
) -> str:
    """Bind current mode and content authority without changing approval bytes."""

    base = WORKTREE._compute_transmission_sha256(
        policy_sha256, readable_manifest_sha256, selected_content_sha256,
    )
    return WORKTREE._compute_v11_launch_approval_sha256(
        _provider_isolation_for_command(command), command["native_grant_profile"],
        transmission_sha256=base,
    )


def _compute_repair_lineage_sha256(
    *, authority_sha256: str, attempt: int,
    parent_result_sha256: str | None, parent_worktree_sha256: str | None,
    reconciliation_sha256: str, result_sha256: str,
    candidate_worktree_sha256: str, selected_content_sha256: str,
    transmission_sha256: str,
) -> str:
    return digest(canonical({
        "kind": "agy-worker-scoped-repair-lineage-v1",
        "authority_sha256": authority_sha256,
        "attempt": attempt,
        "parent_result_sha256": parent_result_sha256,
        "parent_worktree_sha256": parent_worktree_sha256,
        "reconciliation_sha256": reconciliation_sha256,
        "result_sha256": result_sha256,
        "candidate_worktree_sha256": candidate_worktree_sha256,
        "selected_content_sha256": selected_content_sha256,
        "transmission_sha256": transmission_sha256,
    }))


def _initial_content_transmission(command: dict[str, Any]) -> str:
    content = command["launch_authority"]["content"]
    return _bound_transmission_sha256(
        command, content["policy_sha256"], content["manifest_sha256"],
        content["selected_content_sha256"])


def _require_scoped_transmission_authority(
    command: dict[str, Any], state: Mapping[str, Any], *,
    selected_content_sha256: str, transmission_sha256: str,
    provider_origin: str | None = None,
) -> None:
    """Apply the one exact rule used at every scoped transmission check."""
    initial_transmission_sha = _initial_content_transmission(command)
    if transmission_sha256 == initial_transmission_sha:
        if state.get("transmission_sha256") not in {None, transmission_sha256} or (
            state.get("selected_content_sha256") not in {None, selected_content_sha256}
        ):
            raise DispatchError("worktree scope transmission binding changed")
        return
    if provider_origin not in {None, "conversation-continue"}:
        raise DispatchError("approved transmission SHA does not match current worktree scope")
    if (
        not command.get("allow_scoped_repair", False)
        or not state.get("allow_scoped_repair", False)
        or command.get("repair_authority_sha256") != state.get("repair_authority_sha256")
        or command.get("repair_authority_sha256") != _repair_authority_for_command(command)
        or state.get("repair_lineage_sha256") is None
        or state.get("repair_lineage_attempt") not in {
            state.get("attempt"), state.get("attempt", 0) - 1,
        }
        or not state.get("candidate_recognized", False)
        or not state.get("result_available", False)
        or state.get("worktree_reconciliation") != "available"
        or state.get("reconciliation_manifest_sha256") is None
        or state.get("candidate_worktree_sha256") is None
        or state.get("selected_content_sha256") != selected_content_sha256
        or state.get("transmission_sha256") != transmission_sha256
    ):
        raise DispatchError("scoped repair transmission lineage is unavailable")


def _dispatch_root_identity(workdir: str) -> dict[str, Any] | None:
    """Return V9's stable root/Git-administration authority record.

    Unlike the semantic candidate snapshot, this extractor is intentionally
    unchanged by ordinary tracked/untracked worktree edits, index refreshes,
    HEAD/ref moves, and object maintenance.  Those remain candidate-binding
    facts; this record detects a substituted repository boundary.
    """
    return WORKTREE._git_boundary_identity(workdir)


def _state_worktree_snapshot(state: Mapping[str, Any], workdir: str) -> dict[str, Any] | None:
    """Use the one persisted semantic algorithm without changing its digest."""
    if state.get("schema_version") is not None:
        _require_supported_schema(state, label="dispatch state", supported=(CURRENT_STATE_SCHEMA,))
        if state.get("worktree_snapshot_algorithm") != CURRENT_WORKTREE_SNAPSHOT_ALGORITHM:
            raise DispatchError("dispatch worktree snapshot algorithm is unavailable")
    return WORKTREE._worktree_snapshot(workdir)


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
    workdir: str, baseline: dict[str, Any] | None, *, state: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    current = WORKTREE._worktree_snapshot(workdir) if state is None else _state_worktree_snapshot(state, workdir)
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


def _bound_schemas(command: dict[str, Any], state: Mapping[str, Any]) -> tuple[Path, Path]:
    paths = _schema_paths(command)
    if paths is None:
        raise DispatchError("dispatch schema argument is unavailable")
    expected = _schema_bindings(command)
    for key, value in expected.items():
        if state[key] != value:
            raise DispatchError("dispatch schema binding changed")
    return paths


def _bound_candidate_worktree(state: Mapping[str, Any], command: dict[str, Any]) -> None:
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
    if (WORKTREE._git_boundary_identity(command["workdir"])
        != state.get("worktree_root_identity")):
        raise DispatchError("dispatch worktree root binding changed")
    expected_sha = state["candidate_worktree_sha256"]
    expected_entries = state["candidate_worktree_entries"]
    current = _state_worktree_snapshot(state, command["workdir"])
    if current is None or expected_sha is None or expected_entries is None:
        raise DispatchError("candidate worktree reconciliation is unavailable")
    if current["sha256"] != expected_sha or current["entries"] != expected_entries:
        drift = "entry count and snapshot digest" if current["entries"] != expected_entries else "snapshot digest"
        details = WORKTREE._snapshot_drift_details(
            state["candidate_worktree_path_facts"], current.get("path_facts"),
        )
        raise DispatchError(
            f"candidate worktree binding changed ({drift})"
            + (f": {details}" if details else "")
            + "; inspect candidate drift and request repair in the same worker "
            "conversation; do not edit the bound candidate by hand"
        )


def _bound_current_candidate(job: Path, state: Mapping[str, Any]) -> tuple[dict[str, Any], bytes]:
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
    result_path = Path(state["result_path"])
    try:
        result_parent = result_path.parent.resolve(strict=True)
    except OSError as exc:
        raise DispatchError("dispatch result path is unavailable") from exc
    if not result_path.is_absolute() or result_parent != bound_job:
        raise DispatchError("dispatch result path is outside this job")
    command = _load_bound_command(bound_job, state, stage_readonly=False)
    command, state = _bound_lifecycle_inputs(
        bound_job, state, command,
        bind_terminal_candidate=True,
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
    _bound_lifecycle_inputs(
        bound_job, state, command,
        bind_terminal_candidate=True,
    )
    # Project jobs created before the external-log-root boundary can place their
    # own controller state inside the candidate worktree. Every state write then
    # changes the semantic snapshot, so that stored snapshot is self-invalidating.
    # Keep exact command/schema/root/result bindings for readback and a driver-only
    # final disposition; provider recovery is denied by the inside-worktree guard.
    if not _job_is_inside_worktree(bound_job, command["workdir"]):
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
        raise DispatchError("verification copy destination immediate parent must be current-user mode 0700")
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
            # Validate that the source still supports reading its symlink target.
            os.readlink(source)
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
            or WORKTREE._resolved_path_is_git_administration(str(root), resolved)
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
        command, state = _bound_lifecycle_inputs(
            job, state, command, bind_terminal_candidate=True,
        )
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


def _bound_worktree_baseline(state: Mapping[str, Any], command: dict[str, Any]) -> None:
    """Require the queued worktree fact set immediately before provider launch."""
    expected = state["worktree_baseline"]
    current = _state_worktree_snapshot(state, command["workdir"])
    if expected is None or current is None:
        WORKTREE._worktree_snapshot(command["workdir"], explain_unsupported=True)
        raise WorktreeBaselineError("queued worktree baseline is unavailable")
    if (
        current["sha256"] != expected["sha256"]
        or current["entries"] != expected["entries"]
    ):
        raise WorktreeBaselineError("queued worktree baseline changed")


def _restart_guard_accepts(
    state: Mapping[str, Any], *, status: str | None = None,
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
        and elapsed < _provider_max_seconds(state)
        and state.get("phase") != "self-verifying"
        and (
            state["workflow"] == "legacy"
            or state["attempt"] < state["max_cycles"]
        )
    )


def _load_bound_command(
    job: Path, state: Mapping[str, Any], *, stage_readonly: bool,
) -> dict[str, Any]:
    command, raw, identity = load_command(job)
    if digest(raw) != state["command_sha256"] or list(identity) != state["command_identity"]:
        raise DispatchError("dispatch command binding changed")
    expected_content = _initial_content_transmission(command) if command["provider_scope_path"] else None
    if state["initial_content_transmission_sha256"] != expected_content:
        raise DispatchError("dispatch initial content transmission binding changed")
    stage_sha, stage_identity = _bound_stage(command, readonly=stage_readonly)
    if stage_sha != state["stage_sha256"] or (
        stage_identity is not None and list(stage_identity[:4]) != state["stage_identity"][:4]
    ) or (stage_identity is None) != (state["stage_identity"] is None):
        raise DispatchError("staged prompt binding changed")
    return command


def _load_bound_selection(
    command: dict[str, Any], state: Mapping[str, Any],
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
    if (state["selection_sha256"] != command["selection_sha256"]
        or state["selection_identity"] != command["selection_identity"]):
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
        # not reopen or substitute the caller selection here.
        record = MODEL_SELECTION.decode_selection_record(raw, frozen=True)
    except (MODEL_SELECTION.CallerError, MODEL_SELECTION.EvidenceUnavailable) as exc:
        raise DispatchError("dispatch selection is invalid") from exc
    return record


StateMapping = TypeVar("StateMapping", bound=Mapping[str, Any])


def _bound_lifecycle_inputs(
    job: Path, state: StateMapping, command: dict[str, Any] | None = None,
    *, bind_terminal_candidate: bool = False,
) -> tuple[dict[str, Any], StateMapping]:
    """Bind non-provider recovery/finalization inputs before any state write.

    This never writes state or launches a provider, but it does perform the
    bounded local root, selection, schema, and boundary probes shared by status
    projection and the mutating create/finalize/result paths.  Provider launch
    still repeats its final executable and worktree probes.
    """
    if command is None:
        command = _load_bound_command(job, state, stage_readonly=False)
    checked = state
    if checked["workdir"] != command["workdir"]:
        raise DispatchError("dispatch worktree root binding changed")
    if (checked["provider_isolation"] != _provider_isolation_for_command(command)):
        raise DispatchError("dispatch provider isolation binding changed")
    if (checked["native_grant_profile"]
        != command.get("native_grant_profile", "baseline")
        or checked["whole_worktree_content_sha256"]
        != command.get("whole_worktree_content_sha256")):
        raise DispatchError("dispatch authority binding changed")
    root = Path(command["workdir"])
    try:
        root_info = root.lstat()
    except OSError as exc:
        raise DispatchError("dispatch worktree root is unavailable") from exc
    root_identity = _dispatch_root_identity(command["workdir"])
    if (
        root_identity is None
        or root_identity != checked["worktree_root_identity"]
    ):
        raise DispatchError("dispatch worktree root binding changed")
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
    if not WORKTREE._worktree_symlink_boundary(command["workdir"]):
        raise DispatchError("dispatch worktree symlink boundary changed")
    _load_bound_selection(
        command, checked,
    )
    _bound_schemas(command, checked)
    if checked["workflow"] == "project" and (
        WORKTREE._project_boundary(command["workdir"]) != checked["project_boundary"]
    ):
        raise DispatchError("project worktree boundary changed")
    if (checked["allow_scoped_repair"] != command.get("allow_scoped_repair", False)
        or checked["repair_authority_sha256"] != command.get("repair_authority_sha256")
        or command.get("repair_authority_sha256") != _repair_authority_for_command(command)):
        raise DispatchError("dispatch scoped repair authority changed")
    if checked["allow_self_verification"] != command.get(
        "allow_self_verification", False
    ):
        raise DispatchError("dispatch self-verification authority changed")
    _bound_self_verification_manifest(command, job)
    if checked.get("provider_scope_path") is not None:
        _scope_path, raw_scope, scope_info = _read_provider_scope_file(
            checked["provider_scope_path"], MAX_COMMAND_BYTES,
        )
        if digest(raw_scope) != checked["provider_scope_sha256"]:
            raise DispatchError("provider scope file changed since dispatch")
        if list(_identity(scope_info)) != checked["provider_scope_identity"]:
            raise DispatchError("provider scope file identity changed since dispatch")
        try:
            scope = WORKTREE._parse_provider_scope(raw_scope)
        except ValueError as exc:
            raise DispatchError(f"invalid provider scope: {exc}") from exc
        if bind_terminal_candidate:
            if not (
                checked["candidate_recognized"]
                and (
                    checked["status"] in TERMINAL
                    or (
                        checked["status"] == "queued"
                        and checked["attempt_origin"] == "conversation-continue"
                        and checked["controller_pid"] in {None, os.getpid()}
                    )
                )
            ):
                raise DispatchError("terminal candidate binding is unavailable")
        else:
            readable_manifest = WORKTREE._scan_readable_worktree(command["workdir"])
            manifest_sha = WORKTREE._manifest_digest(readable_manifest)
            WORKTREE._validate_scope_against_worktree(scope, command["workdir"], readable_manifest)
            selected_manifest = WORKTREE._build_selected_content_manifest(command["workdir"], scope)
            selected_sha = WORKTREE._selected_content_digest(selected_manifest)
            policy_sha = WORKTREE._canonical_digest(scope)
            transmission_sha = _bound_transmission_sha256(
                command, policy_sha, manifest_sha, selected_sha,
            )
            _require_scoped_transmission_authority(
                command, checked,
                selected_content_sha256=selected_sha,
                transmission_sha256=transmission_sha,
                provider_origin=(
                    checked["attempt_origin"]
                    if checked["status"] in {"queued", "running", "cancel-requested"}
                    else None
                ),
            )
    return command, checked


def _reprobe_direct_selection(
    command: dict[str, Any], state: Mapping[str, Any], argv: list[str],
) -> tuple[str, dict[str, Any]]:
    """Probe every provider launch and bind exact caller model/effort arguments."""
    record = _load_bound_selection(command, state)
    if record is not None:
        if not _selection_launch_is_authorized(record):
            raise DispatchError("dispatch selection has no current executable binding")
        for flag, key in (("--model", "resolved_agy_model"), ("--effort", "user_effort")):
            expected = record.get(key)
            if expected is None:
                if flag in argv:
                    raise DispatchError("dispatch selection argument drifted: " + flag)
            elif argv.count(flag) != 1 or argv.index(flag) + 1 >= len(argv) or argv[argv.index(flag) + 1] != expected:
                raise DispatchError("dispatch selection argument drifted: " + flag)
    try:
        provider_isolation = _provider_isolation_for_command(command)
        conversation = "--conversation" in argv
        if record is not None:
            return MODEL_SELECTION.reprobe_selection_record(
                record, provider_isolation=provider_isolation, conversation=conversation,
            )
        executable, binding, _version = MODEL_SELECTION.probe_capabilities(
            provider_isolation=provider_isolation, conversation=conversation,
            effort="--effort" in argv,
        )
        return executable, binding
    except (MODEL_SELECTION.CallerError, MODEL_SELECTION.EvidenceUnavailable) as exc:
        raise SelectionPreflightError("dispatch capability preflight failed") from exc


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


def _revalidate_scoped_provider_stage(
    stage_dir: Path,
    scope: dict[str, Any],
    selected_manifest: list[dict[str, Any]],
    stage_identity: tuple[int, int, int, int, int],
    stage_manifest_sha: str,
) -> None:
    """Rebind the complete fresh stage immediately before native launch."""
    try:
        current = stage_dir.lstat()
    except OSError as exc:
        raise DispatchError("provider stage is unavailable before launch") from exc
    identity = (
        current.st_dev, current.st_ino, current.st_uid,
        current.st_gid, current.st_mode,
    )
    if (
        identity != stage_identity
        or not stat.S_ISDIR(current.st_mode)
        or stat.S_ISLNK(current.st_mode)
        or current.st_uid != os.getuid()
        or stat.S_IMODE(current.st_mode) != 0o700
        or WORKTREE._selected_content_digest(selected_manifest) != stage_manifest_sha
    ):
        raise DispatchError("provider stage binding changed before launch")
    mutations, _operation_sha = WORKTREE._scan_stage_mutations(
        stage_dir, scope, selected_manifest,
    )
    if mutations:
        raise DispatchError("provider stage changed before launch")


def _terminate_provider_process(
    process: subprocess.Popen[bytes],
    contained_root: CONTAINMENT.ProcessIdentity | None,
    *,
    contained: bool,
) -> int:
    """Reap a provider group, using kernel-bound identity when contained."""
    if not contained:
        return _terminate(process)
    if contained_root is None:
        raise DispatchError("contained provider process identity is unavailable")
    try:
        # Reap an already-exited leader before libproc enumeration. Darwin can
        # report the zombie PID in its group while proc_pidinfo no longer has
        # a bindable identity for it. The recorded start identity still makes
        # a subsequently reused leader PID a hard failure.
        process.poll()
        CONTAINMENT.terminate_bound_process_group(contained_root, signal.SIGTERM)
        with contextlib.suppress(subprocess.TimeoutExpired):
            process.wait(timeout=TERM_GRACE)
        deadline = time.monotonic() + TERM_GRACE
        while (
            not CONTAINMENT.process_group_is_quiescent(contained_root)
            and time.monotonic() < deadline
        ):
            time.sleep(0.02)
        if not CONTAINMENT.process_group_is_quiescent(contained_root):
            CONTAINMENT.terminate_bound_process_group(contained_root, signal.SIGKILL)
        if process.poll() is None:
            process.wait(timeout=1.0)
        deadline = time.monotonic() + 1.0
        while (
            not CONTAINMENT.process_group_is_quiescent(contained_root)
            and time.monotonic() < deadline
        ):
            time.sleep(0.02)
        if not CONTAINMENT.process_group_is_quiescent(contained_root):
            raise DispatchError("contained provider process group cleanup is uncertain")
        return int(process.returncode)
    except (CONTAINMENT.ContainmentError, OSError, subprocess.SubprocessError) as exc:
        raise DispatchError("contained provider process group cleanup is uncertain") from exc


def _event(line: bytes) -> tuple[bool, str | None, str | None]:
    if not line or len(line) > MAX_EVENT_BYTES:
        return False, None, None
    try:
        value = json.loads(
            line.decode("utf-8", "strict"), object_pairs_hook=_duplicates,
            parse_constant=_invalid_json_constant,
        )
    except (UnicodeError, json.JSONDecodeError, ValueError, OverflowError, DispatchError, RecursionError):
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


def _reviewed_provider_timeout_lines(version: str, seconds: object) -> set[bytes]:
    """Build only the exact 1.2.2/1.2.6/1.2.7 timeout lines bound to this job's limit.

    The installed binary exposes a ``%s`` duration slot but its unavailable
    source does not establish whether that slot retains the integer-seconds
    flag spelling or uses Go's canonical whole-second duration spelling.  The
    wrapper always supplies a positive integer number of seconds.  Accept only
    those two equivalent spellings for that exact bound value.
    """
    if type(seconds) not in (int, float):
        return set()
    # The exact-type guard above excludes bool and all non-numeric objects.
    seconds = cast("int | float", seconds)
    if not math.isfinite(seconds) or seconds <= 0 or seconds != int(seconds):
        return set()
    total = int(seconds)
    if total > 7 * 24 * 3600:
        return set()
    raw = f"{total}s"
    if total < 60:
        canonical = raw
    elif total < 3600:
        minutes, remainder = divmod(total, 60)
        canonical = f"{minutes}m{remainder}s"
    else:
        hours, remainder = divmod(total, 3600)
        minutes, remainder = divmod(remainder, 60)
        canonical = f"{hours}h{minutes}m{remainder}s"
    prefix = "[agy] print timeout after "
    suffix = " with turn in progress; returning partial output"
    return {
        f"{prefix}{duration}{suffix}".encode("ascii")
        for duration in {raw, canonical}
    }


def _has_reviewed_provider_timeout(
    path: Path, version: str, seconds: object,
) -> bool:
    expected = _reviewed_provider_timeout_lines(version, seconds)
    if not expected:
        return False
    try:
        raw = path.read_bytes()
    except OSError:
        return False
    return bool(expected.intersection(raw.splitlines()))


def _classify_stderr(
    path: Path, version: str, returncode: int, provider_timeout_seconds: object = None,
    *, native: bool = False,
) -> str:
    try:
        raw = path.read_bytes()
    except OSError:
        return "agy_failed_unclassified"

    raw_lines = raw.splitlines()

    # 1. Any AGY_ERROR marker lines must be evaluated strictly
    agy_lines = [line for line in raw_lines if b"AGY_ERROR" in line]
    if agy_lines:
        if len(agy_lines) != 1:
            return "agy_failed_unclassified"
        m_line = agy_lines[0]
        if len(m_line) > MAX_EVENT_BYTES:
            return "agy_failed_unclassified"
        if not m_line.startswith(b"AGY_ERROR: "):
            return "agy_failed_unclassified"
        if returncode != 3:
            return "agy_failed_unclassified"
        payload = parse_agy_error(m_line)
        if payload is None:
            return "agy_failed_unclassified"
        expected_timeout = _reviewed_provider_timeout_lines(version, provider_timeout_seconds)
        if expected_timeout and bool(expected_timeout.intersection(raw_lines)):
            return "agy_failed_unclassified"
        if any(b"permission that headless mode cannot prompt for" in line for line in raw_lines):
            return "agy_failed_unclassified"
        return "provider_terminal_error"

    # 2. No AGY_ERROR marker: reviewed timeout wins first
    expected_timeout = _reviewed_provider_timeout_lines(version, provider_timeout_seconds)
    if expected_timeout and bool(expected_timeout.intersection(raw_lines)):
        return "provider_timeout"

    # 3. rc0 returns empty_output
    if returncode == 0:
        return "empty_output"

    native_host_denials = {
        b"sandbox_apply: Operation not permitted",
        b"sandbox-exec: sandbox_apply: Operation not permitted",
    }
    if native and any(line.strip() in native_host_denials for line in raw_lines):
        return "native_host_sandbox_unavailable"

    # Preserve the existing nonzero headless-permission restriction.
    if any(b"permission that headless mode cannot prompt for" in line for line in raw_lines):
        return "permission_required"

    return "agy_failed_unclassified"


def _selection_rejection_result(line: bytes) -> bool:
    """Recognize only a strict diagnostic frame, never a worker envelope."""
    if not line or len(line) > MAX_EVENT_BYTES:
        return False
    try:
        frame = json.loads(
            line.decode("utf-8", "strict"), object_pairs_hook=_duplicates,
            parse_constant=_invalid_json_constant,
        )
    except (UnicodeError, ValueError, OverflowError, DispatchError, RecursionError):
        return False
    result = frame.get("result") if isinstance(frame, dict) else None
    return bool(
        isinstance(frame, dict) and frame.get("event") == "result"
        and isinstance(result, dict) and result.get("status") == "ERROR"
        and type(result.get("num_turns")) is int and result["num_turns"] == 0
    )


def _model_selection_rejected(
    stream: Path, stderr: Path, returncode: int, version: str,
    provider_timeout_seconds: object, *, native: bool,
) -> bool:
    """Require the complete bounded evidence and actual reaped exit code."""
    if returncode != 1:
        return False
    try:
        with stderr.open("rb") as handle:
            diagnostic = handle.read(MAX_STREAM_BYTES + 1)
        with stream.open("rb") as handle:
            output = handle.read(MAX_EVENT_BYTES + 2)
    except OSError:
        return False
    lines = diagnostic.splitlines()
    if (
        len(diagnostic) > MAX_STREAM_BYTES
        or b"AGY_ERROR" in diagnostic
        or sum(line.startswith(b"error: invalid model selection (") for line in lines) != 1
        or any(line.strip() in {
            b"sandbox_apply: Operation not permitted",
            b"sandbox-exec: sandbox_apply: Operation not permitted",
        } for line in lines)
        or _classify_stderr(stderr, version, returncode, provider_timeout_seconds, native=native)
        != "agy_failed_unclassified"
    ):
        return False
    return not output or bool(
        output.endswith(b"\n") and output.count(b"\n") == 1
        and _selection_rejection_result(output[:-1])
    )


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
                except (UnicodeError, json.JSONDecodeError, ValueError, OverflowError, DispatchError, RecursionError):
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


def _has_denied_actions(stream: Path) -> bool:
    """Opaque denial-key presence restricts reuse only after strict framing."""
    result = _terminal_result(stream, strict=True)
    return isinstance(result, dict) and isinstance(result.get("status"), str) and result["status"] in {"SUCCESS", "ERROR", "CANCELLED", "CANCELED"} and "denied_actions" in result


AGY_ERROR_PAYLOAD_FIELDS = {
    "short_error", "status", "error_code", "code_kind", "retryable", "error_id",
}


class AgyErrorPayload(NamedTuple):
    short_error: str | None
    status: str | None = None
    error_code: int | None = None
    code_kind: str | None = None
    retryable: bool | None = None
    error_id: str | None = None


def parse_agy_error(raw: str | bytes) -> AgyErrorPayload | None:
    """Closed offline parser for static printmode.agentErrorPayload metadata.

    Static analysis of the approved 1.2.6/1.2.7 Go binary recovered:
      short_error *string (no omitempty)
      status *string omitempty
      error_code *uint32 omitempty
      code_kind *string omitempty
      retryable *bool (no omitempty)
      error_id *string omitempty
      Exact fallback literal: {"short_error":%q}

    Accepts only a single column-zero line starting with exact "AGY_ERROR: ".
    Raw JSON, leading whitespace, missing space after colon, duplicate keys,
    invalid constants, numeric overflow, or schema mismatch fail closed (return None).
    """
    if isinstance(raw, bytes):
        if len(raw) > MAX_EVENT_BYTES:
            return None
        try:
            text = raw.decode("utf-8", "strict")
        except UnicodeDecodeError:
            return None
    elif isinstance(raw, str):
        if len(raw) > MAX_EVENT_BYTES:
            return None
        text = raw
    else:
        return None

    if text.endswith("\r\n"):
        line = text[:-2]
    elif text.endswith("\n"):
        line = text[:-1]
    else:
        line = text
    if "\r" in line or "\n" in line:
        return None
    prefix = "AGY_ERROR: "
    if not line.startswith(prefix):
        return None
    json_part = line[len(prefix):].strip()
    if not (json_part.startswith("{") and json_part.endswith("}")):
        return None

    try:
        data = json.loads(
            json_part,
            object_pairs_hook=_duplicates,
            parse_constant=_invalid_json_constant,
        )
    except (json.JSONDecodeError, ValueError, OverflowError, DispatchError, RecursionError):
        return None

    if not isinstance(data, dict):
        return None

    # Fallback literal shape: exact field set {"short_error"}, string value (empty string allowed)
    if set(data.keys()) == {"short_error"}:
        short_error = data["short_error"]
        if not isinstance(short_error, str):
            return None
        return AgyErrorPayload(
            short_error=short_error,
            status=None,
            error_code=None,
            code_kind=None,
            retryable=None,
            error_id=None,
        )

    # Normal shape: requires short_error and retryable
    # short_error can be str | None (string or null, empty allowed)
    # retryable can be bool | None (bool or null)
    # Optional keys: status, error_code, code_kind, error_id only.
    # Optional string-pointer fields are strings (empty allowed).
    # error_code must be non-bool uint32 (0 <= error_code <= 0xFFFFFFFF, type(val) is int).
    if "short_error" not in data or "retryable" not in data:
        return None
    if not set(data.keys()).issubset(AGY_ERROR_PAYLOAD_FIELDS):
        return None

    short_error = data["short_error"]
    if short_error is not None and not isinstance(short_error, str):
        return None

    retryable = data["retryable"]
    if retryable is not None and type(retryable) is not bool:
        return None

    status = data.get("status")
    if "status" in data and not isinstance(status, str):
        return None

    code_kind = data.get("code_kind")
    if "code_kind" in data and not isinstance(code_kind, str):
        return None

    error_id = data.get("error_id")
    if "error_id" in data and not isinstance(error_id, str):
        return None

    error_code = data.get("error_code")
    if "error_code" in data and (type(error_code) is not int or isinstance(error_code, bool) or not (0 <= error_code <= 0xFFFFFFFF)):
        return None

    return AgyErrorPayload(
        short_error=short_error,
        status=status,
        error_code=error_code,
        code_kind=code_kind,
        retryable=retryable,
        error_id=error_id,
    )


def _validate_terminal_envelope(
    stream: Path, envelope: Path, provider_schema: Path, canonical_schema: Path, *,
    stage_dir: Path | None = None,
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
    if stage_dir is not None:
        value = _canonicalize_scoped_report_paths(value, stage_dir)
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


@dataclasses.dataclass
class _ControllerBinding:
    state: Mapping[str, Any] = dataclasses.field(default_factory=dict)
    prior_raw: bytes = b""
    command: dict[str, Any] = dataclasses.field(default_factory=dict)
    feedback: Path | None = None
    schema_paths: tuple[Path, Path] | None = None


@dataclasses.dataclass
class _ProviderExecution:
    stop_signal: int | None = None
    process: subprocess.Popen[bytes] | None = None
    started_mono: float | None = None
    runtime_end_mono: float | None = None
    runtime_frozen: bool = False
    idle_timeout_with_exited_provider: bool = False
    elapsed: float = 0.0
    heartbeat_mono: float = 0.0
    next_notice: float = 0.0
    returncode: int = 0


@dataclasses.dataclass
class _ControllerStreams:
    stream_path: Path
    stderr_path: Path
    envelope_path: Path
    stdout_fd: int = -1
    stderr_fd: int = -1
    selector: selectors.BaseSelector | None = None
    buffers: dict[str, bytearray] = dataclasses.field(
        default_factory=lambda: {"stdout": bytearray(), "stderr": bytearray()},
    )
    sizes: dict[str, int] = dataclasses.field(
        default_factory=lambda: {"stdout": 0, "stderr": 0},
    )


@dataclasses.dataclass
class _ScopedLaunch:
    argv: list[str] = dataclasses.field(default_factory=list)
    expected_print: str | None = None
    launch_cwd: str = ""
    executable_binding: tuple[str, dict[str, Any]] | None = None
    stage_dir: Path | None = None
    scope: dict[str, Any] | None = None
    selected_manifest: list[dict[str, Any]] | None = None
    stage_manifest_sha: str | None = None
    stage_identity: tuple[int, int, int, int, int] | None = None
    narrow_source_snapshot: dict[str, Any] | None = None
    scoped_executable: str | None = None
    prepared_containment: CONTAINMENT.PreparedContainedLaunch | None = None
    contained_root: CONTAINMENT.ProcessIdentity | None = None


@dataclasses.dataclass
class _ControllerOutcome:
    reason: str | None = None
    limit_kind: str | None = None
    failure_stage: str | None = None
    saw_init: bool = False
    saw_terminal: bool = False
    provisional_orphan_result: bool = False
    result_binding: tuple[str, tuple[int, int, int, int, int]] | None = None
    outer_status: str | None = None
    provider_retry_after: int | None = None
    provider_retry_observed: float | None = None
    boundary_failed: bool = False
    cleanup_failed: bool = False
    final_status: str = "failed"
    exit_code: int = 0
    result_path: str | None = None


@dataclasses.dataclass
class _CandidateReconciliation:
    candidate_worktree: dict[str, Any] | None = None
    reconciliation: dict[str, Any] = dataclasses.field(default_factory=dict)
    reconciliation_manifest_sha: str | None = None
    derived_selected_sha: str | None = None
    derived_selected_files: int | None = None
    derived_selected_trees: int | None = None
    derived_transmission_sha: str | None = None


def _controller_monitor_limit(
    state: Mapping[str, Any], stop_signal: int | None, elapsed: float,
    now_mono: float, heartbeat_mono: float, *, float_hard: bool,
) -> tuple[str, str | None] | None:
    """Classify a sample without evaluating limits after a winning control."""
    if state["cancel_requested"] or stop_signal is not None:
        return ("cancelled" if stop_signal is None else "interrupted"), None
    if elapsed >= _provider_max_seconds(state):
        return "hard_deadline_exceeded", "max-runtime"
    hard_seconds = float(state["hard_seconds"]) if float_hard else state["hard_seconds"]
    if elapsed >= hard_seconds:
        return "hard_deadline_exceeded", "hard"
    if now_mono - heartbeat_mono >= float(state["idle_seconds"]):
        return "idle_timeout", "idle"
    return None


def _controller_wait_seconds(
    state: Mapping[str, Any], started_mono: float, heartbeat_mono: float,
    next_notice: float, now_mono: float,
) -> float:
    """Bound a selector wait by the first controller-owned clock."""
    wait_until = min(
        started_mono + max(0.0, _provider_max_seconds(state) - float(state["attempt_base_elapsed"])),
        started_mono + max(0.0, float(state["hard_seconds"]) - float(state["attempt_base_elapsed"])),
        heartbeat_mono + float(state["idle_seconds"]),
        next_notice,
    )
    return min(CONTROL_POLL, max(0.0, wait_until - now_mono))


def _controller_terminal_status(
    reason: str | None, stop_signal: int | None,
) -> tuple[str, int]:
    if reason is None:
        return "succeeded", 0
    status = "cancelled" if reason in {
        "cancelled", "interrupted", "provider_terminal_cancelled",
    } else "failed"
    return status, 128 + stop_signal if stop_signal is not None else EXIT_BY_REASON[reason]


def _controller_completion_signal(
    watched: tuple[int, ...], pending: AbstractSet[int], stop_signal: int | None,
) -> int | None:
    for candidate in watched:
        if candidate in pending or candidate == stop_signal:
            return candidate
    return stop_signal


def _latch_controller_signal(execution: _ProviderExecution, number: int) -> None:
    if execution.stop_signal is None:
        execution.stop_signal = number


@dataclasses.dataclass
class _CandidateDisposition:
    preserve_candidate_forensics: bool = False
    terminal_snapshot_unavailable: bool = False
    candidate_recognized: bool = False
    candidate_unavailable: bool = False
    candidate_source: str = "none"
    provider_terminal_status: str = "unknown"
    preserved_path: str | None = None
    preserved_sha: str | None = None
    preserved_identity: list[int] | None = None


def _claim_controller_attempt(
    job: Path,
    binding: _ControllerBinding,
) -> int | None:
    # Claim the queued attempt under one state lock.  A cancel can land
    # between process spawn and this point, but never between this exact
    # queued observation and controller ownership publication.
    cancelled_before_claim = False
    with state_lock(job):
        binding.state, binding.prior_raw, _sha = load_state(job)
        if binding.state["status"] == "cancel-requested" and binding.state["cancel_requested"]:
            cancelled_before_claim = True
        elif binding.state["status"] != "queued" or binding.state["cancel_requested"]:
            raise DispatchError("dispatch is not queued")
        else:
            # A queued state with this exact PID is the startup handshake; it
            # means the private controller is alive, not that a provider
            # process exists or that provider runtime has started.
            binding.state, binding.prior_raw, _sha = _transition_locked(job, binding.state, binding.prior_raw, {
                "controller_pid": os.getpid(),
            })
    if cancelled_before_claim:
        _terminalize_owned(
            job, binding.state, status="cancelled", reason="cancelled",
            exit_code=EXIT_BY_REASON["cancelled"], expected_controller_pid=None,
        )
        return EXIT_BY_REASON["cancelled"]
    return None


def _bind_controller_inputs(
    job: Path,
    binding: _ControllerBinding,
) -> int | None:
    binding.feedback = None
    binding.schema_paths = None
    try:
        binding.command = _load_bound_command(job, binding.state, stage_readonly=False)
        MODEL_SELECTION.ACTIVE_CHILD_ENV = list(binding.command["provider_env"])
        _load_bound_selection(binding.command, binding.state)
        binding.schema_paths = _bound_schemas(binding.command, binding.state)
        if not WORKTREE._worktree_symlink_boundary(binding.command["workdir"]):
            raise DispatchError("dispatch worktree symlink boundary changed")
        if binding.state["workflow"] == "project":
            if WORKTREE._project_boundary(binding.command["workdir"]) != binding.state["project_boundary"]:
                raise DispatchError("project worktree boundary changed")
        if binding.state["attempt_origin"] == "conversation-continue":
            binding.feedback = _bound_verification(job, binding.state)
            if binding.feedback is None:
                raise DispatchError("project continuation has no verification feedback")
            binding.command, _candidate_raw = _bound_current_candidate(job, binding.state)
    except (OSError, DispatchError):
        terminal, _raw, _sha = _terminalize_owned(
            job, binding.state, status="failed", reason="status_unavailable",
            exit_code=EXIT_BY_REASON["status_unavailable"],
            failure_stage="binding_failure", expected_controller_pid=os.getpid(),
        )
        # Terminal validation guarantees an integer exit code.
        assert terminal["exit_code"] is not None
        return int(terminal["exit_code"])
    return None


def _open_controller_artifacts(
    job: Path,
    binding: _ControllerBinding,
    execution: _ProviderExecution,
    streams: _ControllerStreams,
) -> int | None:
    # ``elapsed_seconds`` is provider execution time.  The strict local
    # command/root/schema/worktree proofs below happen before a provider
    # process exists, so they cannot consume the provider hard, maximum,
    # or idle budgets.  This is especially important when a safe platform
    # Git fallback makes those bounded probes materially slower.
    execution.elapsed = float(binding.state["attempt_base_elapsed"])
    try:
        streams.stdout_fd = _ensure_new_private(streams.stream_path)
        streams.stderr_fd = _ensure_new_private(streams.stderr_path)
        _stage(binding.command, True)
        _load_bound_command(job, binding.state, stage_readonly=True)
        _load_bound_selection(binding.command, binding.state)
        binding.schema_paths = _bound_schemas(binding.command, binding.state)
    except (OSError, DispatchError):
        if streams.stdout_fd >= 0: os.close(streams.stdout_fd)
        if streams.stderr_fd >= 0: os.close(streams.stderr_fd)
        with contextlib.suppress(OSError): _stage(binding.command, False)
        terminal, _raw, _sha = _terminalize_owned(
            job, binding.state, status="failed", reason="status_unavailable",
            exit_code=EXIT_BY_REASON["status_unavailable"],
            failure_stage="binding_failure", expected_controller_pid=os.getpid(),
        )
        # Terminal validation guarantees an integer exit code.
        assert terminal["exit_code"] is not None
        return int(terminal["exit_code"])
    return None


def _build_controller_argv(
    binding: _ControllerBinding,
    launch: _ScopedLaunch,
) -> None:
    launch.argv = list(binding.command["argv"])
    if binding.state["attempt_origin"] in {"conversation-resume", "conversation-continue"}:
        conversation = binding.state["conversation_id"]
        if not isinstance(conversation, str):
            raise DispatchError("resume has no conversation")
        print_index = launch.argv.index("--print")
        prefix = ["--conversation", conversation]
        prompt = binding.command["resume_prompt"]
        if binding.state["attempt_origin"] == "conversation-continue":
            if binding.feedback is None:
                raise DispatchError("project continuation feedback was not prevalidated")
            if binding.state.get("provider_scope_path") is None:
                prefix.extend(["--add-dir", str(binding.feedback.parent)])
                prompt = binding.command["continue_prompt"] + f" Feedback file: '{binding.feedback}'."
            else:
                feedback_raw, _feedback_info = read_regular(
                    binding.feedback, MAX_VERIFICATION_BYTES, "verification feedback",
                    allowed_modes=(0o400,),
                )
                prompt = (
                    binding.command["continue_prompt"]
                    + " Driver verification JSON follows inline:\n"
                    + feedback_raw.decode("utf-8", "strict")
                )
        launch.argv[print_index + 1] = prompt
        launch.argv[print_index:print_index] = prefix


def _controller_transition(
    job: Path,
    binding: _ControllerBinding,
    updates: dict[str, Any],
) -> bool:
    """Do not turn a concurrent approved control into a controller crash."""
    try:
        binding.state, binding.prior_raw, _sha = transition(job, binding.state, binding.prior_raw, updates)
        return True
    except DispatchError as exc:
        if str(exc) != "dispatch state changed before transition":
            raise
        current, current_raw, _current_sha = read_state_snapshot(job)
        if current["attempt"] != binding.state["attempt"]:
            raise DispatchError("dispatch attempt changed during control")  # noqa: B904 -- preserve existing exception context and public diagnostics
        binding.state, binding.prior_raw = current, current_raw
        return False


def _refresh_control_snapshot(
    job: Path,
    binding: _ControllerBinding,
) -> None:
    """Reload an approved control transition before using live limits."""
    current, current_raw, _current_sha = read_state_snapshot(job)
    if current_raw == binding.prior_raw:
        return
    if (
        current["previous_state_sha256"] != digest(binding.prior_raw)
        or current["sequence"] != binding.state["sequence"] + 1
        or current["attempt"] != binding.state["attempt"]
    ):
        raise DispatchError("dispatch changed during provider control")
    binding.state, binding.prior_raw = current, current_raw


def _drain_reaped_streams(
    streams: _ControllerStreams,
    outcome: _ControllerOutcome,
) -> None:
    """Bind bytes emitted before reap without treating them as activity."""
    for key in list(cast(selectors.BaseSelector, streams.selector).get_map().values()):
        name = key.data
        while True:
            try:
                chunk = os.read(key.fd, 65536)
            except BlockingIOError:
                break
            except OSError:
                outcome.reason = "status_unavailable"
                outcome.failure_stage = "binding_failure"
                return
            if not chunk:
                try:
                    cast(selectors.BaseSelector, streams.selector).unregister(key.fileobj)
                    cast(IO[bytes], key.fileobj).close()
                except OSError:
                    outcome.reason = "status_unavailable"
                    outcome.failure_stage = "binding_failure"
                break
            streams.sizes[name] += len(chunk)
            if streams.sizes[name] > MAX_STREAM_BYTES:
                outcome.reason = "output_oversized"
                return
            try:
                os.write(streams.stdout_fd if name == "stdout" else streams.stderr_fd, chunk)
            except OSError:
                outcome.reason = "status_unavailable"
                outcome.failure_stage = "binding_failure"
                return


def _prepare_scoped_controller_launch(
    job: Path,
    binding: _ControllerBinding,
    launch: _ScopedLaunch,
) -> None:
    _scope_path, raw_scope, scope_info = _read_provider_scope_file(
        binding.state["provider_scope_path"], MAX_COMMAND_BYTES,
    )
    if digest(raw_scope) != binding.state["provider_scope_sha256"]:
        raise DispatchError("provider scope file changed since dispatch")
    if list(_identity(scope_info)) != binding.state["provider_scope_identity"]:
        raise DispatchError("provider scope file identity changed since dispatch")
    launch.scope = WORKTREE._parse_provider_scope(raw_scope)
    readable_manifest = WORKTREE._scan_readable_worktree(binding.command["workdir"])
    manifest_sha = WORKTREE._manifest_digest(readable_manifest)
    WORKTREE._validate_scope_against_worktree(launch.scope, binding.command["workdir"], readable_manifest)
    launch.selected_manifest = WORKTREE._build_selected_content_manifest(binding.command["workdir"], launch.scope)
    selected_sha = WORKTREE._selected_content_digest(launch.selected_manifest)
    policy_sha = WORKTREE._canonical_digest(launch.scope)
    transmission_sha = _bound_transmission_sha256(
        binding.command, policy_sha, manifest_sha, selected_sha,
    )
    _require_scoped_transmission_authority(
        binding.command, binding.state,
        selected_content_sha256=selected_sha,
        transmission_sha256=transmission_sha,
        provider_origin=binding.state["attempt_origin"],
    )
    launch.narrow_source_snapshot = WORKTREE._worktree_snapshot(binding.command["workdir"])
    launch.stage_dir = job / f"stage-{binding.state['attempt']:03d}"
    launch.stage_identity, launch.stage_manifest_sha = WORKTREE._materialize_stage(binding.command["workdir"], launch.stage_dir, launch.scope, launch.selected_manifest)
    launch.launch_cwd = str(launch.stage_dir)
    if launch.executable_binding is None:
        try:
            launch.executable_binding = MODEL_SELECTION.resolve_safe_executable()
        except MODEL_SELECTION.EvidenceUnavailable as exc:
            raise SelectionPreflightError(
                "scoped dispatch executable binding is unavailable",
            ) from exc
    launch.scoped_executable = launch.executable_binding[0]


def _confirm_whole_controller_approval(
    binding: _ControllerBinding,
) -> None:
    approved_whole_sha = binding.command.get("approved_whole_worktree_sha256")
    if (
        approved_whole_sha is not None
        and (
            binding.state["attempt_origin"] == "initial"
            or (
                binding.state.get("conversation_id") is None
            )
        )
    ):
        readable_manifest = WORKTREE._scan_readable_worktree(binding.command["workdir"])
        content = WORKTREE.whole_worktree_content_manifest(binding.command["workdir"])
        content_sha = content["manifest_sha256"]
        if content_sha != binding.command["whole_worktree_content_sha256"]:
            raise DispatchError("whole-worktree content binding changed")
        if WORKTREE._manifest_digest(readable_manifest) != binding.command["launch_authority"]["content"]["manifest_sha256"]:
            raise DispatchError("whole-worktree transmission binding changed")


def _prepare_native_controller_launch(
    job: Path,
    binding: _ControllerBinding,
    launch: _ScopedLaunch,
) -> None:
    if launch.stage_dir is None:
        raise DispatchError("scoped provider stage is unavailable")
    contained_argv = [cast(str, launch.scoped_executable), *launch.argv[1:]]
    if contained_argv.count("--json-schema") != 1:
        raise DispatchError("scoped provider schema argument is invalid")
    schema_index = contained_argv.index("--json-schema") + 1
    if schema_index >= len(contained_argv):
        raise DispatchError("scoped provider schema argument is invalid")
    # The native binder canonicalizes the exact file. Use the
    # same spelling in argv so /var -> /private/var aliases do
    # not make the provider's approved schema unreadable.
    contained_argv[schema_index] = os.path.realpath(cast(tuple[Path, Path], binding.schema_paths)[0])
    launch.prepared_containment = CONTAINMENT.prepare_contained_launch(
        role=CONTAINMENT.ROLE_PROVIDER,
        network_policy=CONTAINMENT.NETWORK_PROVIDER_TLS,
        job_dir=job,
        attempt=binding.state['attempt'],
        stage_dir=launch.stage_dir,
        target_executable=cast(str, launch.scoped_executable),
        target_argv=contained_argv,
        child_environment=MODEL_SELECTION.child_environment(
            binding.command["provider_env"],
        ),
        allow_keychain=True,
        read_only_inputs=(contained_argv[schema_index],),
        provider_max_cycles=binding.command["max_cycles"],
        provider_write_selectors=cast(dict[str, Any], launch.scope)["write"],
        grant_profile=binding.command["native_grant_profile"],
    )


def _spawn_controller_provider(
    job: Path,
    binding: _ControllerBinding,
    execution: _ProviderExecution,
    streams: _ControllerStreams,
    launch: _ScopedLaunch,
    outcome: _ControllerOutcome,
) -> None:
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
    if execution.stop_signal is not None:
        outcome.reason = "interrupted"
        execution.returncode = 128 + execution.stop_signal
    elif execution.elapsed >= _provider_max_seconds(binding.state):
        outcome.reason, outcome.limit_kind = "hard_deadline_exceeded", "max-runtime"
        execution.returncode = EXIT_BY_REASON[outcome.reason]
    elif execution.elapsed >= float(binding.state["hard_seconds"]):
        outcome.reason, outcome.limit_kind = "hard_deadline_exceeded", "hard"
        execution.returncode = EXIT_BY_REASON[outcome.reason]
    else:
        # Linearize cancellation against the provider-causing
        # operation.  The final executable confirmation and Popen
        # stay in this same short critical section: cancellation
        # before it wins without a provider; cancellation after
        # it is necessarily a post-launch request.
        with state_lock(job):
            current, current_raw, _current_sha = load_state(job)
            if (
                current["attempt"] != binding.state["attempt"]
                or current["controller_pid"] != os.getpid()
                or current["status"] in TERMINAL
            ):
                raise DispatchError("dispatch changed before provider launch")
            binding.state, binding.prior_raw = current, current_raw
            if binding.state["cancel_requested"]:
                outcome.reason = "cancelled"
                execution.returncode = EXIT_BY_REASON[outcome.reason]
            else:
                running_updates = {
                    "status": "running", "controller_pid": os.getpid(),
                    "started_epoch": None, "last_progress_epoch": None,
                    "stream_path": str(streams.stream_path), "stderr_path": str(streams.stderr_path),
                    "next_action": "wait",
                }
                if launch.stage_dir is not None:
                    running_updates.update({
                        "provider_stage_path": str(launch.stage_dir),
                        "provider_stage_identity": list(launch.stage_identity) if launch.stage_identity is not None else None,
                        "provider_stage_manifest_sha256": launch.stage_manifest_sha,
                    })
                binding.state, binding.prior_raw, _sha = _transition_locked(job, binding.state, binding.prior_raw, running_updates)
                exact_executable = None
                if launch.executable_binding is not None:
                    try:
                        exact_executable = MODEL_SELECTION.confirm_executable_binding(
                            *launch.executable_binding,
                        )
                    except MODEL_SELECTION.EvidenceUnavailable as exc:
                        raise SelectionPreflightError(
                            "dispatch direct selection launch binding changed",
                        ) from exc
                provider_argv: list[str] | tuple[str, ...] = launch.argv
                provider_cwd = launch.launch_cwd
                provider_environment = _provider_environment(binding.command)
                if launch.prepared_containment is not None:
                    if (
                        launch.stage_dir is None
                        or launch.scope is None
                        or launch.selected_manifest is None
                        or launch.stage_identity is None
                        or launch.stage_manifest_sha is None
                    ):
                        raise DispatchError("scoped provider launch binding is incomplete")
                    _revalidate_scoped_provider_stage(
                        launch.stage_dir, launch.scope, launch.selected_manifest,
                        launch.stage_identity, launch.stage_manifest_sha,
                    )
                    confirmed_containment = CONTAINMENT.confirm_contained_launch(
                        launch.prepared_containment,
                    )
                    provider_argv = confirmed_containment.argv
                    exact_executable = confirmed_containment.executable
                    provider_cwd = confirmed_containment.cwd
                    provider_environment = confirmed_containment.environment
                if (launch.expected_print is None or provider_argv.count("--print") != 1
                        or provider_argv[provider_argv.index("--print") + 1] != launch.expected_print):
                    raise DispatchError("dispatch final transport prompt changed")
                launch_mono = time.monotonic()
                execution.process = subprocess.Popen(
                    provider_argv,
                    executable=exact_executable,
                    cwd=provider_cwd,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env=provider_environment,
                    start_new_session=True,
                    close_fds=True,
                    preexec_fn=lambda: os.umask(int(binding.command["child_umask"], 8)),
                )
                execution.started_mono = launch_mono
                execution.heartbeat_mono = execution.started_mono
                execution.next_notice = execution.started_mono + float(binding.command["notice_seconds"])
                if launch.prepared_containment is not None:
                    launch.contained_root = CONTAINMENT.bind_new_process_group(
                        execution.process.pid,
                    )
                binding.state, binding.prior_raw, _sha = _transition_locked(
                    job, binding.state, binding.prior_raw, {"started_epoch": time.time()},
                )


def _confirm_launch_authority(job: Path, command: dict[str, Any], state: Mapping[str, Any]) -> None:
    """Recompute caller authority from actual immutable inputs before spawning."""
    try:
        task_raw = LAUNCH_AUTHORITY.read_bound_file(
            job / "task.txt", LAUNCH_AUTHORITY.MAX_TASK_BYTES, private=True, label="initial task")
        task, _text = LAUNCH_AUTHORITY.normalize_task(task_raw)
        if digest(task) != command["launch_authority"]["task_sha256"]:
            raise DispatchError("launch authority changed: task_sha256")
        argv = command["argv"]

        def option(name: str) -> str | None:
            positions = [index for index, item in enumerate(argv) if item == name]
            if len(positions) > 1 or (positions and positions[0] + 1 >= len(argv)):
                raise DispatchError("dispatch launch argument is invalid")
            return argv[positions[0] + 1] if positions else None

        if option("--print-timeout") != f'{command["max_seconds"]}s':
            raise DispatchError("launch authority changed: max_seconds")
        if option("--output-format") != "stream-json":
            raise DispatchError("dispatch launch output format is invalid")
        _load_bound_selection(command, state)
        mode = option("--mode")
        if mode not in {"plan", "accept-edits"}:
            raise DispatchError("dispatch launch mode is invalid")
        if mode != command["launch_authority"]["mode"]:
            raise DispatchError("launch authority changed: mode")
        block = ""
        manifest_sha = None
        if command["self_verification_manifest_path"] is not None:
            raw = LAUNCH_AUTHORITY.read_bound_file(
                Path(command["self_verification_manifest_path"]), SELF_VERIFICATION.MAX_MANIFEST_BYTES,
                private=True, label="verification manifest")
            manifest = SELF_VERIFICATION.parse_manifest(raw)
            block = LAUNCH_AUTHORITY.verification_request_block(
                [check.identifier for check in manifest.checks if check.required],
                [check.identifier for check in manifest.checks if not check.required])
            manifest_sha = digest(raw)
        prompt = LAUNCH_AUTHORITY.full_prompt(
            task, mode=mode, provider_isolation=command["provider_isolation"], verification_block=block)
        retained_prompt = LAUNCH_AUTHORITY.read_bound_file(
            job / "full-prompt.txt", LAUNCH_AUTHORITY.MAX_TASK_BYTES + 65536,
            private=True, label="initial prompt")
        if prompt != retained_prompt:
            raise DispatchError("launch authority changed: full_prompt_sha256")
        initial_prompt = option("--print")
        if command["stage_file"] is not None:
            initial_expected = LAUNCH_AUTHORITY.STAGED_INSTRUCTION.format(stage_file=command["stage_file"])
            staged, _info = read_regular(Path(command["stage_file"]), MAX_COMMAND_BYTES,
                                        "staged prompt", allowed_modes=(0o600, 0o444))
            if staged != prompt:
                raise DispatchError("launch authority changed: full_prompt_sha256")
        else:
            initial_expected = prompt.decode("utf-8")
        if initial_prompt != initial_expected:
            raise DispatchError("launch authority changed: full_prompt_sha256")
        schema = option("--json-schema")
        if schema is None:
            raise DispatchError("dispatch launch schema is missing")
        schema_raw = LAUNCH_AUTHORITY.read_bound_file(Path(schema), 512 * 1024,
                                                     private=False, label="provider schema")
        root = Path(command["workdir"]).resolve()
        add_dirs = []
        for index, argument in enumerate(argv):
            if argument == "--add-dir":
                path = Path(argv[index + 1]).resolve(strict=True)
                if command["stage_dir"] is not None and path == Path(command["stage_dir"]).resolve():
                    continue
                add_dirs.append(path.relative_to(root).as_posix())
        actual = LAUNCH_AUTHORITY.build_authority(
            content=command["launch_authority"]["content"], task=task, prompt=prompt,
            workflow=command["workflow"], mode=mode, max_cycles=command["max_cycles"],
            idle_seconds=command["idle_seconds"], hard_seconds=command["hard_seconds"],
            max_seconds=command["max_seconds"], notice_seconds=command["notice_seconds"],
            model=option("--model"), effort=option("--effort"),
            allow_scoped_repair=command["allow_scoped_repair"],
            self_verification_manifest_sha256=manifest_sha,
            provider_env_names=command["provider_env"],
            allow_slash_commands=mode == "accept-edits" and "--disable-slash-commands" not in argv,
            add_dirs=sorted(set(add_dirs)), provider_schema_sha256=digest(schema_raw),
            base_commit=command["base_commit"], workdir=str(root))
        field = LAUNCH_AUTHORITY.changed_field(command["launch_authority"], actual)
        if field:
            raise DispatchError(f"launch authority changed: {field}")
        if LAUNCH_AUTHORITY.approval_sha256(actual) != command["launch_approval_sha256"]:
            raise DispatchError("dispatch launch approval digest changed")
    except DispatchError:
        raise
    except (LAUNCH_AUTHORITY.LaunchAuthorityError, ValueError, IndexError) as exc:
        raise DispatchError("dispatch launch authority is unavailable") from exc


def _launch_controller_provider(
    job: Path,
    binding: _ControllerBinding,
    execution: _ProviderExecution,
    streams: _ControllerStreams,
    launch: _ScopedLaunch,
    outcome: _ControllerOutcome,
) -> None:
    try:
        # Re-read the frozen record and re-probe *after* all controller
        # mutations and immediately before the provider-causing launch.
        # argv[0] stays the portable public spelling while executable=
        # pins the safe, freshly-probed target for this one process.
        launch.executable_binding = _reprobe_direct_selection(binding.command, binding.state, launch.argv)
        _bound_worktree_baseline(binding.state, binding.command)
        if not WORKTREE._worktree_symlink_boundary(binding.command["workdir"]):
            raise DispatchError("dispatch worktree symlink boundary changed")
        launch.launch_cwd = binding.command["workdir"]
        if binding.state.get("provider_scope_path") is not None:
            _prepare_scoped_controller_launch(job, binding, launch)
        else:
            _confirm_whole_controller_approval(binding)
            if binding.command["base_commit"] is not None:
                _bound_whole_worktree_base(
                    binding.command["workdir"], binding.command["base_commit"],
                    binding.command["workflow"],
                )
        _confirm_launch_authority(job, binding.command, binding.state)
        launch.expected_print = _bind_workspace_prompt(
            launch.argv, Path(os.path.realpath(launch.launch_cwd)),
            scoped=launch.scope is not None,
            provider_isolation=_provider_isolation_for_command(binding.command),
            base_commit=binding.command["base_commit"],
        )
        if launch.scoped_executable is not None and _provider_isolation_for_command(binding.command) == "native":
            _prepare_native_controller_launch(job, binding, launch)
        _spawn_controller_provider(job, binding, execution, streams, launch, outcome)
    except MODEL_SELECTION.ProbeInterrupted as exc:
        # model_selection owns and reaps its short-lived probe group;
        # the controller owns the terminal dispatch projection.
        execution.stop_signal = exc.signal_number
        outcome.reason = "interrupted"
        execution.returncode = 128 + exc.signal_number
    except SelectionPreflightError as exc:
        outcome.reason = "selection_preflight_failed"
        outcome.failure_stage = "selection_preflight"
        cause = exc.__cause__
        if isinstance(cause, MODEL_SELECTION.MissingCapabilities):
            diagnostic = (cause.diagnostic() + "\n").encode("ascii")
            try:
                if os.write(streams.stderr_fd, diagnostic) != len(diagnostic):
                    raise OSError("short capability diagnostic write")
            except OSError:
                outcome.reason = "status_unavailable"
                outcome.failure_stage = "binding_failure"
        execution.returncode = EXIT_BY_REASON[outcome.reason]
    except WorktreeBaselineError as exc:
        outcome.reason = "resolve_undo_present" if isinstance(exc, ResolveUndoPresentError) else "status_unavailable"
        outcome.failure_stage = "binding_failure"
        execution.returncode = EXIT_BY_REASON[outcome.reason]
    except (DispatchError, CONTAINMENT.ContainmentError) as exc:
        message = str(exc)
        if re.fullmatch(r"launch authority changed: [a-z0-9_]+(?:\.[a-z0-9_]+)?", message):
            outcome.failure_stage = "launch_authority_changed:" + message.removeprefix("launch authority changed: ")
            with contextlib.suppress(OSError):
                os.write(streams.stderr_fd, (message + "\n").encode("ascii"))
        outcome.reason = "status_unavailable"
        execution.returncode = EXIT_BY_REASON["status_unavailable"]
    except OSError:
        # A selection reaches this point even when agy is
        # absent.  Publish a terminal, sanitized dispatch failure rather
        # than leaking an interpreter traceback or leaving a queued job.
        outcome.reason = "agy_failed_unclassified"
        execution.returncode = 127
    else:
        if execution.process is not None:
            try:
                assert execution.process.stdout is not None and execution.process.stderr is not None
                for name, pipe in (("stdout", execution.process.stdout), ("stderr", execution.process.stderr)):
                    os.set_blocking(pipe.fileno(), False)
                    cast(selectors.BaseSelector, streams.selector).register(pipe, selectors.EVENT_READ, name)
            except (OSError, DispatchError):
                outcome.reason = "status_unavailable"
                outcome.failure_stage = "binding_failure"


def _consume_controller_events(
    job: Path,
    binding: _ControllerBinding,
    execution: _ProviderExecution,
    streams: _ControllerStreams,
    launch: _ScopedLaunch,
    outcome: _ControllerOutcome,
    events: list[tuple[selectors.SelectorKey, int]],
) -> None:
    for key, _mask in events:
        name = key.data
        try:
            chunk = os.read(key.fd, 65536)
        except BlockingIOError:
            continue
        except OSError:
            outcome.reason = "status_unavailable"
            outcome.failure_stage = "binding_failure"
            break
        if not chunk:
            try:
                cast(selectors.BaseSelector, streams.selector).unregister(key.fileobj)
                cast(IO[bytes], key.fileobj).close()
            except OSError:
                outcome.reason = "status_unavailable"
                outcome.failure_stage = "binding_failure"
                break
            continue
        streams.sizes[name] += len(chunk)
        if streams.sizes[name] > MAX_STREAM_BYTES:
            outcome.reason = "output_oversized"
            break
        try:
            os.write(streams.stdout_fd if name == "stdout" else streams.stderr_fd, chunk)
        except OSError:
            outcome.reason = "status_unavailable"
            outcome.failure_stage = "binding_failure"
            break
        if name == "stdout" and outcome.reason is None:
            streams.buffers[name].extend(chunk)
            while b"\n" in streams.buffers[name]:
                line, _, remainder = streams.buffers[name].partition(b"\n")
                streams.buffers[name] = bytearray(remainder)
                if len(line) > MAX_EVENT_BYTES:
                    outcome.reason = "output_oversized"
                    break
                if outcome.provisional_orphan_result:
                    # Keep subsequent bytes as evidence only. No progress,
                    # conversation binding, or heartbeat credit is authorized.
                    continue
                valid, conversation, event_kind = _event(line)
                if valid:
                    if outcome.saw_terminal or (event_kind == "init" and outcome.saw_init) or (
                        event_kind != "init" and not outcome.saw_init
                    ):
                        if (
                            not outcome.saw_init and not outcome.saw_terminal
                            and streams.sizes[name] - len(remainder) == len(line) + 1
                            and _selection_rejection_result(line)
                        ):
                            # Preserve framing as a provisional fallback while
                            # the existing bounded monitor observes EOF/reap.
                            outcome.provisional_orphan_result = True
                            continue
                        outcome.reason = "invalid_envelope"
                        outcome.failure_stage = "framing"
                        break
                    if event_kind == "init":
                        try:
                            init_frame = json.loads(
                                line.decode("utf-8", "strict"),
                                object_pairs_hook=_duplicates,
                            )
                        except (UnicodeError, json.JSONDecodeError, ValueError, OverflowError, DispatchError):
                            init_frame = None
                        init_value = init_frame.get("init") if isinstance(init_frame, dict) else None
                        if not isinstance(init_value, dict) or not _init_cwd_matches_launch(init_value, launch.launch_cwd):
                            outcome.reason = "status_unavailable"
                            outcome.failure_stage = "binding_failure"
                            break
                        outcome.saw_init = True
                    elif event_kind == "result":
                        outcome.saw_terminal = True
                    execution.heartbeat_mono = time.monotonic()
                    updates: dict[str, Any] = {
                        "progress_count": binding.state["progress_count"] + 1,
                        "last_progress_epoch": time.time(),
                        "elapsed_seconds": float(binding.state["attempt_base_elapsed"]) + execution.heartbeat_mono - cast(float, execution.started_mono),
                        "last_activity": (
                            "provider_initialized" if event_kind == "init"
                            else "progress_signal" if event_kind == "step_update"
                            else "terminal_received"
                        ),
                    }
                    if conversation is not None:
                        if binding.state["conversation_id"] not in {None, conversation}:
                            outcome.reason = "status_unavailable"
                            break
                        updates["conversation_id"] = conversation
                        updates["resume_available"] = True
                    try:
                        _controller_transition(job, binding, updates)
                    except DispatchError:
                        outcome.reason = "status_unavailable"
                        outcome.failure_stage = "binding_failure"
                        break
            if len(streams.buffers[name]) > MAX_EVENT_BYTES:
                # A newline-free oversized frame cannot be safely
                # resynchronized.  It is neither a heartbeat nor a
                # candidate terminal result.
                outcome.reason = "output_oversized"
        if outcome.reason is not None:
            break


def _monitor_controller_provider(
    job: Path,
    binding: _ControllerBinding,
    execution: _ProviderExecution,
    streams: _ControllerStreams,
    launch: _ScopedLaunch,
    outcome: _ControllerOutcome,
) -> None:
    # Pipe EOF is the completion observation.  Do not poll/reap the leader
    # before process-group closure; its PID reserves the group identifier.
    while execution.process is not None and cast(selectors.BaseSelector, streams.selector).get_map() and outcome.reason is None:
        now_mono = time.monotonic()
        execution.elapsed = float(binding.state["attempt_base_elapsed"]) + now_mono - cast(float, execution.started_mono)
        try:
            _refresh_control_snapshot(job, binding)
        except DispatchError:
            outcome.reason = "status_unavailable"
            break
        decision = _controller_monitor_limit(binding.state, execution.stop_signal, execution.elapsed, now_mono, execution.heartbeat_mono, float_hard=False)
        if decision is not None:
            outcome.reason, outcome.limit_kind = decision
            break
        if now_mono >= execution.next_notice:
            try:
                _controller_transition(job, binding, {
                    "notice_count": binding.state["notice_count"] + 1,
                    "elapsed_seconds": execution.elapsed,
                })
            except DispatchError:
                outcome.reason = "status_unavailable"
                outcome.failure_stage = "binding_failure"
                break
            execution.next_notice += float(binding.command["notice_seconds"])
            if sys.stderr.isatty():
                print(
                    f"agy-worker: still running; elapsed={int(execution.elapsed)}s "
                    f"progress={binding.state['progress_count']}", file=sys.stderr, flush=True,
                )
        try:
            # A fixed poll can return after a nearer hard, maximum,
            # idle, or notice boundary.  Bound the kernel wait to the
            # first controller-owned clock, then reload any extension
            # and classify the resampled time before consuming ready
            # bytes as semantic progress.
            wait_seconds = _controller_wait_seconds(binding.state, cast(float, execution.started_mono), execution.heartbeat_mono, execution.next_notice, now_mono)
            events = cast(selectors.BaseSelector, streams.selector).select(wait_seconds)
        except OSError:
            outcome.reason = "status_unavailable"
            outcome.failure_stage = "binding_failure"
            break
        post_wait_mono = time.monotonic()
        try:
            _refresh_control_snapshot(job, binding)
        except DispatchError:
            outcome.reason = "status_unavailable"
            outcome.failure_stage = "binding_failure"
            break
        execution.elapsed = (
            float(binding.state["attempt_base_elapsed"])
            + post_wait_mono - cast(float, execution.started_mono)
        )
        decision = _controller_monitor_limit(binding.state, execution.stop_signal, execution.elapsed, post_wait_mono, execution.heartbeat_mono, float_hard=True)
        if decision is not None:
            outcome.reason, outcome.limit_kind = decision
            break
        _consume_controller_events(job, binding, execution, streams, launch, outcome, events)
        if outcome.reason is not None:
            break


def _reap_controller_provider(
    job: Path,
    binding: _ControllerBinding,
    execution: _ProviderExecution,
    streams: _ControllerStreams,
    launch: _ScopedLaunch,
    outcome: _ControllerOutcome,
) -> None:
    if execution.process is not None:
        # The candidate worktree binding below is taken only after the
        # provider process group has been terminated and reaped.  The
        # controller-owned stream artifacts are flushed afterward.
        # Freeze first: fsync, envelope parsing, and reconciliation
        # are controller-local work and must not keep the provider
        # clock or extension window alive.
        execution.returncode = _terminate_provider_process(
            execution.process, launch.contained_root,
            contained=launch.prepared_containment is not None,
        )
        execution.idle_timeout_with_exited_provider = bool(
            outcome.reason == "idle_timeout" and execution.returncode == 0
        )
        execution.process = None
        execution.runtime_end_mono = time.monotonic()
        # A hard/max boundary stops semantic event processing, but a
        # complete terminal frame already present in the reaped pipes
        # remains bounded provider evidence.  Drain it without
        # incrementing progress or moving the heartbeat.
        _drain_reaped_streams(streams, outcome)
        assert execution.started_mono is not None
        execution.elapsed = float(binding.state["attempt_base_elapsed"]) + max(
            0.0, execution.runtime_end_mono - execution.started_mono,
        )
        binding.state, binding.prior_raw, _sha, frozen_limit = _freeze_reaped_runtime(
            job, binding.state["attempt"], os.getpid(), execution.elapsed,
        )
        execution.runtime_frozen = True
        if outcome.reason == "hard_deadline_exceeded":
            # A valid extension may have landed after this controller
            # observed its old limit but before the reaped-runtime CAS.
            # The frozen locked limit is authoritative in either
            # direction; do not retain a stale timeout projection.
            if frozen_limit is None:
                outcome.reason, outcome.limit_kind = None, None
            else:
                outcome.reason, outcome.limit_kind = "hard_deadline_exceeded", frozen_limit
        elif outcome.reason is None and frozen_limit is not None:
            outcome.reason, outcome.limit_kind = "hard_deadline_exceeded", frozen_limit


def _observe_controller_terminal(
    binding: _ControllerBinding,
    execution: _ProviderExecution,
    streams: _ControllerStreams,
    launch: _ScopedLaunch,
    outcome: _ControllerOutcome,
) -> None:
    try:
        os.fsync(streams.stdout_fd)
        os.fsync(streams.stderr_fd)
    except OSError:
        outcome.reason = "status_unavailable"
        outcome.failure_stage = "binding_failure"
    outcome.result_binding = None
    outcome.outer_status = None
    outcome.provider_retry_after = None
    outcome.provider_retry_observed = None
    if outcome.provisional_orphan_result and outcome.reason in {
        None, "idle_timeout", "hard_deadline_exceeded",
    }:
        # These limits still stopped and reaped the child. Deferral alone
        # exposed them; retain the orphan's original framing diagnosis.
        if outcome.reason is None and _model_selection_rejected(
            streams.stream_path, streams.stderr_path, execution.returncode,
            binding.command["agy_version"] if binding.command["agy_version_observed"] else "",
            binding.command["max_seconds"],
            native=binding.command["provider_isolation"] == "native",
        ):
            outcome.reason = "model_selection_rejected"
            outcome.failure_stage = None
        else:
            outcome.reason = "invalid_envelope"
            outcome.failure_stage = "framing"
    if outcome.reason is None and streams.sizes["stdout"] == 0 and _model_selection_rejected(
        streams.stream_path, streams.stderr_path, execution.returncode,
        binding.command["agy_version"] if binding.command["agy_version_observed"] else "",
        binding.command["max_seconds"],
        native=binding.command["provider_isolation"] == "native",
    ):
        outcome.reason = "model_selection_rejected"
    reviewed_idle_partial = bool(
        not outcome.provisional_orphan_result
        and execution.idle_timeout_with_exited_provider
        and _has_reviewed_provider_timeout(
            streams.stderr_path,
            binding.command["agy_version"] if binding.command["agy_version_observed"] else "",
            binding.command["max_seconds"],
        )
    )
    # A deadline is a controller fact, not a reason to discard a
    # terminal report already emitted by the bounded provider.  Parse
    # that report for candidate/provenance evidence, but never let its
    # outer SUCCESS/ERROR/CANCELLED disposition publish past the
    # frozen deadline.  Cancellation and binding failures retain their
    # existing fail-closed precedence and do not enter this path.
    if outcome.reason in {None, "hard_deadline_exceeded"} or reviewed_idle_partial:
        if outcome.reason in {None, "hard_deadline_exceeded"} and streams.sizes["stdout"] == 0:
            if outcome.reason is None:
                outcome.reason = (
                    _classify_stderr(
                        streams.stderr_path,
                        binding.command["agy_version"] if binding.command["agy_version_observed"] else "",
                        execution.returncode,
                        binding.command["max_seconds"],
                        native=binding.command["provider_isolation"] == "native",
                    )
                )
        elif outcome.reason in {None, "hard_deadline_exceeded"} or reviewed_idle_partial:
            try:
                if binding.schema_paths is None:
                    raise DispatchError("dispatch schema binding is unavailable")
                binding.schema_paths = _bound_schemas(binding.command, binding.state)
                outcome.result_binding, outcome.outer_status, outcome.failure_stage = _validate_terminal_envelope(
                    streams.stream_path, streams.envelope_path, binding.schema_paths[0], binding.schema_paths[1],
                    stage_dir=launch.stage_dir,
                )
                if outcome.failure_stage == "binding_failure":
                    outcome.reason = "status_unavailable"
                    outcome.result_binding = None
                elif _has_denied_actions(streams.stream_path):
                    # Keep hard-limit diagnostics and persist the reuse prohibition.
                    outcome.reason = "permission_required"
                    if outcome.limit_kind not in {"hard", "max-runtime"}:
                        outcome.limit_kind = None
                elif outcome.result_binding is None and outcome.reason is None:
                    outcome.reason = "invalid_envelope"
                elif (
                    outcome.result_binding is not None
                    and outcome.reason != "hard_deadline_exceeded"
                    and _has_reviewed_provider_timeout(
                        streams.stderr_path, binding.command["agy_version"], binding.command["max_seconds"],
                    )
                ):
                    outcome.reason, outcome.limit_kind = "provider_timeout", None
                elif outcome.reason is None and outcome.outer_status == "ERROR":
                    outcome.reason = "provider_terminal_error"
                elif outcome.reason is None and outcome.outer_status == "CANCELLED":
                    outcome.reason = "provider_terminal_cancelled"
                elif outcome.reason is None and execution.returncode != 0:
                    outcome.reason = "agy_failed_unclassified"
            except DispatchError:
                # A binding/schema failure is security-relevant even
                # when a deadline was observed.  Do not preserve a
                # candidate whose terminal bytes could not be bound.
                outcome.reason = "status_unavailable"
                outcome.result_binding = None
                outcome.failure_stage = "binding_failure"
    outcome.boundary_failed = False
    if binding.command["workflow"] == "project":
        try:
            if WORKTREE._project_boundary(binding.command["workdir"]) != binding.state["project_boundary"]:
                raise DispatchError("project worktree boundary changed")
        except DispatchError:
            outcome.boundary_failed = True
            outcome.reason = "status_unavailable"
            outcome.result_binding = None
            outcome.failure_stage = "binding_failure"


def _begin_controller_completion(
    execution: _ProviderExecution,
    streams: _ControllerStreams,
    outcome: _ControllerOutcome,
    candidate_data: _CandidateReconciliation,
    prior_handlers: dict[signal.Signals, Any],
) -> None:
    # One blocked completion snapshot linearizes terminal state against
    # late HUP/INT/TERM just as the foreground result publisher does.
    watched = tuple(prior_handlers)
    signal.pthread_sigmask(signal.SIG_BLOCK, watched)
    pending = signal.sigpending()
    completion_signal = _controller_completion_signal(watched, pending, execution.stop_signal)
    if completion_signal is not None:
        execution.stop_signal = completion_signal
        outcome.reason = "interrupted"
        outcome.result_binding = None
        outcome.failure_stage = None
    outcome.final_status, outcome.exit_code = _controller_terminal_status(outcome.reason, execution.stop_signal)
    outcome.result_path = str(streams.envelope_path) if outcome.reason is None or outcome.result_binding is not None else None
    outcome.cleanup_failed = False
    candidate_data.reconciliation_manifest_sha = None
    candidate_data.derived_selected_sha = None
    candidate_data.derived_selected_files = None
    candidate_data.derived_selected_trees = None
    candidate_data.derived_transmission_sha = None


def _cleanup_controller_stage(
    job: Path,
    binding: _ControllerBinding,
    streams: _ControllerStreams,
    launch: _ScopedLaunch,
    outcome: _ControllerOutcome,
    candidate_data: _CandidateReconciliation,
) -> None:
    if launch.stage_dir is not None and launch.stage_dir.exists():
        try:
            if (
                launch.narrow_source_snapshot is None
                or WORKTREE._worktree_snapshot(binding.command["workdir"]) != launch.narrow_source_snapshot
            ):
                raise DispatchError(
                    "source worktree changed while the narrow provider stage was active"
                )
            mutations, op_manifest = WORKTREE._scan_stage_mutations(launch.stage_dir, cast(dict[str, Any], launch.scope), cast(list[dict[str, Any]], launch.selected_manifest))
            if outcome.result_binding is not None and not _declared_scoped_mutations_match(
                streams.envelope_path, outcome.result_binding, mutations, launch.stage_dir,
            ):
                raise DispatchError(
                    "worker files_changed does not match scoped stage mutations"
                )
            if outcome.result_binding is not None and outcome.outer_status in {
                "SUCCESS", "ERROR", "CANCELLED",
            }:
                candidate_data.reconciliation_manifest_sha = WORKTREE._reconcile_stage_to_source(
                    binding.command["workdir"], launch.stage_dir, mutations, job,
                )
                if WORKTREE._build_selected_content_manifest(
                    binding.command["workdir"], cast(dict[str, Any], launch.scope),
                ) != WORKTREE._build_selected_content_manifest(
                    launch.stage_dir, cast(dict[str, Any], launch.scope), is_stage=True,
                ):
                    raise DispatchError(
                        "source reconciliation does not match the provider stage"
                    )
            else:
                candidate_data.reconciliation_manifest_sha = WORKTREE._selected_content_digest([])
        except Exception:
            outcome.cleanup_failed = True
        finally:
            try:
                if launch.stage_identity is None:
                    raise DispatchError("stage cleanup identity is unavailable")
                WORKTREE._cleanup_stage(launch.stage_dir, launch.stage_identity)
            except (OSError, DispatchError):
                outcome.cleanup_failed = True
    try:
        cast(selectors.BaseSelector, streams.selector).close()
        os.close(streams.stdout_fd); streams.stdout_fd = -1
        os.close(streams.stderr_fd); streams.stderr_fd = -1
        _stage(binding.command, False)
        _load_bound_command(job, binding.state, stage_readonly=False)
        _bound_schemas(binding.command, binding.state)
        if binding.state["attempt_origin"] == "conversation-continue":
            _bound_verification(job, binding.state)
    except (OSError, DispatchError):
        outcome.cleanup_failed = True
    if outcome.cleanup_failed:
        outcome.reason, outcome.final_status = "status_unavailable", "failed"
        outcome.exit_code = EXIT_BY_REASON["status_unavailable"]
        outcome.result_path = None
        outcome.result_binding = None
        outcome.failure_stage = "binding_failure"


def _observe_controller_cancel(
    job: Path,
    binding: _ControllerBinding,
    outcome: _ControllerOutcome,
) -> None:
    # A SHA-approved cancellation may arrive after the last pipe-loop
    # observation (or after reaping) and before candidate work begins.
    # Observe it under the short ownership lock before selecting the
    # expensive reconciliation path.  The final transition reloads
    # again, but that later check is too late to keep a cheap cancel
    # from being delayed by a repository-controlled Git probe.
    with state_lock(job):
        current, current_raw, _current_sha = load_state(job)
        if (
            current["attempt"] != binding.state["attempt"]
            or current["controller_pid"] != os.getpid()
            or current["status"] in TERMINAL
        ):
            raise DispatchError("dispatch changed before terminal reconciliation")
        binding.state, binding.prior_raw = current, current_raw
        if current["cancel_requested"]:
            outcome.reason, outcome.final_status = "cancelled", "cancelled"
            outcome.exit_code = EXIT_BY_REASON["cancelled"]
            outcome.result_path = None
            outcome.result_binding = None
            outcome.failure_stage = None


def _reconcile_controller_candidate(
    binding: _ControllerBinding,
    launch: _ScopedLaunch,
    outcome: _ControllerOutcome,
    candidate_data: _CandidateReconciliation,
) -> None:
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
        outcome.reason in {"cancelled", "interrupted"}
        and outcome.result_binding is None
    )
    if skip_cancel_reconciliation:
        candidate_data.candidate_worktree = None
        candidate_data.reconciliation = {
            "worktree_reconciliation": "unavailable",
            "worktree_changes_present": None,
            "worktree_changed_since_dispatch": None,
        }
    else:
        candidate_data.candidate_worktree = (
            _state_worktree_snapshot(binding.state, binding.command["workdir"])
            if outcome.result_binding is not None else None
        )
        candidate_data.reconciliation = (
            _reconciliation_from_snapshot(
                candidate_data.candidate_worktree, binding.state["worktree_baseline"],
            )
            if outcome.result_binding is not None else _reconcile_worktree(
                binding.command["workdir"], binding.state["worktree_baseline"], state=binding.state,
            )
        )
    if (
        outcome.result_binding is not None
        and candidate_data.candidate_worktree is not None
        and candidate_data.reconciliation_manifest_sha is not None
        and launch.scope is not None
    ):
        try:
            derived_readable = WORKTREE._scan_readable_worktree(binding.command["workdir"])
            WORKTREE._validate_scope_against_worktree(
                launch.scope, binding.command["workdir"], derived_readable,
            )
            derived_selected = WORKTREE._build_selected_content_manifest(
                binding.command["workdir"], launch.scope,
            )
            candidate_data.derived_selected_sha = WORKTREE._selected_content_digest(derived_selected)
            candidate_data.derived_selected_files = sum(
                1 for item in derived_selected if item["kind"] == "file"
            )
            candidate_data.derived_selected_trees = sum(
                1 for item in derived_selected if item["kind"] == "directory"
            )
            candidate_data.derived_transmission_sha = _bound_transmission_sha256(
                binding.command, WORKTREE._canonical_digest(launch.scope),
                WORKTREE._manifest_digest(derived_readable), candidate_data.derived_selected_sha,
            )
        except Exception:
            candidate_data.derived_selected_sha = None
            candidate_data.derived_selected_files = None
            candidate_data.derived_selected_trees = None
            candidate_data.derived_transmission_sha = None


def _classify_controller_candidate(
    outcome: _ControllerOutcome,
    candidate_data: _CandidateReconciliation,
    current: Mapping[str, Any],
) -> tuple[_ControllerOutcome, _CandidateDisposition]:
    outcome = dataclasses.replace(outcome)
    disposition = _CandidateDisposition()
    if current["cancel_requested"]:
        outcome.reason, outcome.final_status, outcome.exit_code = "cancelled", "cancelled", EXIT_BY_REASON["cancelled"]
        outcome.result_path = None
        outcome.result_binding = None
        outcome.failure_stage = None
    if outcome.reason != "provider_quota_exhausted":
        outcome.provider_retry_after = None
        outcome.provider_retry_observed = None
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
    disposition.preserve_candidate_forensics = bool(
        outcome.result_binding is None and prior_candidate_exists
    )
    disposition.terminal_snapshot_unavailable = bool(
        outcome.result_binding is not None
        and outcome.outer_status in {"SUCCESS", "ERROR", "CANCELLED"}
        and candidate_data.candidate_worktree is None
    )
    if disposition.terminal_snapshot_unavailable:
        # Keep the exact terminal report binding and its outer
        # provenance for forensics, but it is not a reviewable
        # candidate without a worktree binding.
        outcome.reason, outcome.final_status = "status_unavailable", "failed"
        outcome.exit_code = EXIT_BY_REASON["status_unavailable"]
        outcome.failure_stage = "binding_failure"
    if disposition.preserve_candidate_forensics and not prior_candidate_is_bound:
        outcome.reason, outcome.final_status = "status_unavailable", "failed"
        outcome.exit_code = EXIT_BY_REASON["status_unavailable"]
        outcome.failure_stage = "binding_failure"
    disposition.candidate_recognized = outcome.result_binding is not None or disposition.preserve_candidate_forensics
    disposition.candidate_unavailable = bool(
        disposition.candidate_recognized and outcome.failure_stage == "binding_failure"
    )
    disposition.candidate_source = (
        "provider_success" if outcome.result_binding is not None and outcome.outer_status == "SUCCESS"
        else "provider_error" if outcome.result_binding is not None and outcome.outer_status == "ERROR"
        else "provider_cancelled" if outcome.result_binding is not None and outcome.outer_status == "CANCELLED"
        else current["candidate_source"] if disposition.preserve_candidate_forensics
        else "none"
    )
    if outcome.failure_stage in {"schema_rejection", "binding_failure", "framing", "outer_status", "invalid_envelope"}:
        disposition.provider_terminal_status = "unknown"
    else:
        disposition.provider_terminal_status = (
            "success" if outcome.outer_status == "SUCCESS"
            else "error" if outcome.outer_status == "ERROR"
            else "cancelled" if outcome.outer_status in {"CANCELLED", "CANCELED"}
            else "unknown"
        )
    disposition.preserved_path = current["result_path"] if disposition.preserve_candidate_forensics else None
    disposition.preserved_sha = current["result_sha256"] if disposition.preserve_candidate_forensics else None
    disposition.preserved_identity = current["result_identity"] if disposition.preserve_candidate_forensics else None
    return outcome, disposition


def _controller_repair_lineage(
    outcome: _ControllerOutcome,
    candidate_data: _CandidateReconciliation,
    current: Mapping[str, Any],
) -> dict[str, Any]:
    repair_lineage_updates: dict[str, Any] = {}
    if (outcome.result_binding is not None):
        repair_lineage_updates = {
            "repair_lineage_sha256": None,
            "repair_parent_result_sha256": None,
            "repair_parent_worktree_sha256": None,
            "repair_lineage_attempt": None,
        }
        if (
            candidate_data.derived_selected_sha is not None
            and candidate_data.derived_selected_files is not None
            and candidate_data.derived_selected_trees is not None
            and candidate_data.derived_transmission_sha is not None
        ):
            repair_lineage_updates.update({
                "selected_content_sha256": candidate_data.derived_selected_sha,
                "selected_file_count": candidate_data.derived_selected_files,
                "selected_tree_count": candidate_data.derived_selected_trees,
                "transmission_sha256": candidate_data.derived_transmission_sha,
            })
        if (
            current["allow_scoped_repair"]
            and candidate_data.candidate_worktree is not None
            and candidate_data.reconciliation_manifest_sha is not None
            and candidate_data.derived_selected_sha is not None
            and candidate_data.derived_selected_files is not None
            and candidate_data.derived_selected_trees is not None
            and candidate_data.derived_transmission_sha is not None
        ):
            parent_result_sha = (
                current["result_sha256"]
                if current["attempt_origin"] == "conversation-continue"
                else None
            )
            parent_worktree_sha = (
                current["candidate_worktree_sha256"]
                if current["attempt_origin"] == "conversation-continue"
                else current["worktree_baseline"]["sha256"]
            )
            repair_lineage_updates = {
                **repair_lineage_updates,
                "repair_parent_result_sha256": parent_result_sha,
                "repair_parent_worktree_sha256": parent_worktree_sha,
                "repair_lineage_attempt": current["attempt"],
                "repair_lineage_sha256": _compute_repair_lineage_sha256(
                    authority_sha256=current["repair_authority_sha256"],
                    attempt=current["attempt"],
                    parent_result_sha256=parent_result_sha,
                    parent_worktree_sha256=parent_worktree_sha,
                    reconciliation_sha256=candidate_data.reconciliation_manifest_sha,
                    result_sha256=outcome.result_binding[0],
                    candidate_worktree_sha256=candidate_data.candidate_worktree["sha256"],
                    selected_content_sha256=candidate_data.derived_selected_sha,
                    transmission_sha256=candidate_data.derived_transmission_sha,
                ),
            }
    return repair_lineage_updates


def _controller_terminal_updates(
    execution: _ProviderExecution,
    streams: _ControllerStreams,
    outcome: _ControllerOutcome,
    candidate_data: _CandidateReconciliation,
    disposition: _CandidateDisposition,
    current: Mapping[str, Any],
    repair_lineage_updates: dict[str, Any],
) -> dict[str, Any]:
    updates = {
        "status": outcome.final_status,
        "reason": outcome.reason,
        "exit_code": outcome.exit_code,
        "controller_pid": None,
        "finished_epoch": time.time(),
        "elapsed_seconds": execution.elapsed,
        "agy_returncode": execution.returncode,
        "result_path": str(streams.envelope_path) if outcome.result_binding is not None else disposition.preserved_path,
        "result_sha256": outcome.result_binding[0] if outcome.result_binding is not None else disposition.preserved_sha,
        "result_identity": list(outcome.result_binding[1]) if outcome.result_binding is not None else disposition.preserved_identity,
        "candidate_recognized": disposition.candidate_recognized,
        "candidate_source": disposition.candidate_source,
        "provider_terminal_status": disposition.provider_terminal_status,
        # Preserve an exact old candidate after a binding failure for
        # forensics, but never claim it can still be read or reviewed.
        "result_available": disposition.candidate_recognized and not disposition.candidate_unavailable,
        "candidate_worktree_sha256": (
            candidate_data.candidate_worktree["sha256"] if candidate_data.candidate_worktree is not None
            else current["candidate_worktree_sha256"] if disposition.preserve_candidate_forensics else None
        ),
        "candidate_worktree_entries": (
            candidate_data.candidate_worktree["entries"] if candidate_data.candidate_worktree is not None
            else current["candidate_worktree_entries"] if disposition.preserve_candidate_forensics else None
        ),
        "candidate_worktree_path_facts": (
            candidate_data.candidate_worktree.get("path_facts") if candidate_data.candidate_worktree is not None
            else current["candidate_worktree_path_facts"] if disposition.preserve_candidate_forensics else None
        ),
        "driver_disposition": "unreviewed" if disposition.candidate_recognized else "not_applicable",
        "failure_stage": outcome.failure_stage,
        "last_activity": "terminal_received" if outcome.saw_terminal else current["last_activity"],
        "next_action": (
            "blocked" if disposition.candidate_unavailable else "driver_review"
        ) if disposition.candidate_recognized else (
            "none" if outcome.reason in {"selection_preflight_failed", "model_selection_rejected", "permission_required"} else
            "resume" if current["conversation_id"] else "blocked"
        ),
        "next_action_command": None,
        **(
            {
                "worktree_reconciliation": "unavailable",
                "worktree_changes_present": None,
                "worktree_changed_since_dispatch": None,
            }
            if disposition.terminal_snapshot_unavailable else candidate_data.reconciliation
        ),
        "resume_available": bool(
            current["conversation_id"] and not disposition.candidate_recognized
            and outcome.final_status == "failed"
            and outcome.reason not in {"selection_preflight_failed", "model_selection_rejected", "permission_required"}
        ),
        "continue_available": False,
        "remote_cancel_unverified": outcome.reason in {"cancelled", "interrupted"},
        "limit_kind": outcome.limit_kind,
        "provider_retry_after_seconds": outcome.provider_retry_after,
        "provider_retry_observed_epoch": outcome.provider_retry_observed,
        **repair_lineage_updates,
    }
    if current.get("provider_scope_path") is not None:
        updates["reconciliation_manifest_sha256"] = (
            current["reconciliation_manifest_sha256"] if disposition.preserve_candidate_forensics
            else candidate_data.reconciliation_manifest_sha
        )
    if outcome.result_binding is not None:
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
    if outcome.boundary_failed or disposition.candidate_unavailable:
        updates.update({"phase": "blocked", "assurance": "blocked"})
    elif disposition.candidate_recognized:
        updates.update({
            "phase": (
                "repair-failed"
                if outcome.final_status == "failed" and current["attempt_origin"] == "conversation-continue"
                else "awaiting-verification"
            ),
            "assurance": "pending",
            "continue_available": bool(
                outcome.final_status in {"succeeded", "failed"}
                and outcome.reason not in {"selection_preflight_failed", "model_selection_rejected", "permission_required"}
                and disposition.candidate_source != "provider_cancelled"
                and current["conversation_id"]
                and current["attempt"] < current["max_cycles"]
                and execution.elapsed < _provider_max_seconds(current)
                and (
                    current.get("provider_scope_path") is None
                    or candidate_data.derived_transmission_sha
                    == current.get("initial_content_transmission_sha256")
                    or repair_lineage_updates.get(
                        "repair_lineage_sha256"
                    ) is not None
                    or (
                        outcome.result_binding is None
                        and (
                            current.get("transmission_sha256")
                            == current.get("initial_content_transmission_sha256")
                            or current.get("repair_lineage_sha256") is not None
                        )
                    )
                )
            ),
        })
    else:
        updates.update({
            "phase": (
                "repair-failed"
                if outcome.final_status == "failed" and current["attempt_origin"] == "conversation-continue"
                else "attempt-failed"
            ),
            "assurance": "pending",
            "continue_available": False,
        })
    return updates


def _publish_controller_terminal(
    job: Path,
    binding: _ControllerBinding,
    execution: _ProviderExecution,
    streams: _ControllerStreams,
    outcome: _ControllerOutcome,
    candidate_data: _CandidateReconciliation,
) -> int:
    # An approved control may land after the last loop observation.  Bind
    # finalization to the current state under the same short transition lock.
    with state_lock(job):
        current, current_raw, _current_sha = load_state(job)
        if (
            current["attempt"] != binding.state["attempt"]
            or current["controller_pid"] != os.getpid()
            or current["status"] in TERMINAL
        ):
            raise DispatchError("dispatch changed before terminalization")
        # Persist the provider runtime measured before local terminal
        # parsing/reconciliation.  Those controller-local checks must
        # not silently consume a later repair/recovery budget.
        execution.elapsed = max(
            execution.elapsed,
            float(current["elapsed_seconds"]),
        )
        outcome, disposition = _classify_controller_candidate(outcome, candidate_data, current)
        repair_lineage_updates = _controller_repair_lineage(outcome, candidate_data, current)
        updates = _controller_terminal_updates(execution, streams, outcome, candidate_data, disposition, current, repair_lineage_updates)
        binding.state, binding.prior_raw, _sha = _transition_locked(job, current, current_raw, updates)
    return outcome.exit_code


def _cleanup_controller_resources(
    binding: _ControllerBinding,
    execution: _ProviderExecution,
    streams: _ControllerStreams,
    launch: _ScopedLaunch,
) -> None:
    if execution.process is not None:
        # If an exception is leaving the provider loop, transfer
        # ownership to the outer recovery only after this exact group
        # termination/reap has succeeded.  It then freezes elapsed
        # time from this reap boundary.  If termination itself raises,
        # keep ``process`` live so the outer recovery retains the one
        # retry opportunity instead of assuming the group is gone.
        _terminate_provider_process(
            execution.process, launch.contained_root,
            contained=launch.prepared_containment is not None,
        )
        execution.runtime_end_mono = time.monotonic()
        execution.process = None
    with contextlib.suppress(Exception):
        cast(selectors.BaseSelector, streams.selector).close()
    if streams.stdout_fd >= 0:
        os.close(streams.stdout_fd)
    if streams.stderr_fd >= 0:
        os.close(streams.stderr_fd)
    with contextlib.suppress(OSError):
        _stage(binding.command, False)


def _recover_controller_failure(
    job: Path,
    binding: _ControllerBinding,
    execution: _ProviderExecution,
    launch: _ScopedLaunch,
) -> int:
    # Once Popen succeeds, no ordinary controller exception may be left to
    # the cleanup-only finally path.  Reap first, freeze if the state still
    # belongs to this controller, then publish one fail-closed terminal
    # projection.  Pre-launch errors retain their narrower existing paths.
    if execution.process is not None:
        with contextlib.suppress(Exception):
            _terminate_provider_process(
                execution.process, launch.contained_root,
                contained=launch.prepared_containment is not None,
            )
        execution.process = None
        execution.runtime_end_mono = time.monotonic()
    frozen_elapsed = float(binding.state["elapsed_seconds"])
    if not execution.runtime_frozen:
        frozen_elapsed = float(binding.state["attempt_base_elapsed"])
        if execution.started_mono is not None:
            end = execution.runtime_end_mono if execution.runtime_end_mono is not None else time.monotonic()
            frozen_elapsed += max(0.0, end - execution.started_mono)
        try:
            binding.state, binding.prior_raw, _sha, _limit = _freeze_reaped_runtime(
                job, binding.state["attempt"], os.getpid(), frozen_elapsed,
            )
            execution.runtime_frozen = True
        except Exception:
            # The final state write below still clears an active controller
            # record; preserve the largest local elapsed observation if the
            # dedicated freeze CAS itself could not complete.
            pass
    try:
        terminal, _raw, _sha = _terminalize_owned(
            job, binding.state, status="failed", reason="status_unavailable",
            exit_code=EXIT_BY_REASON["status_unavailable"],
            failure_stage="binding_failure", expected_controller_pid=os.getpid(),
            elapsed_seconds=frozen_elapsed, postlaunch_cancel=True,
        )
        # Terminal validation guarantees an integer exit code.
        assert terminal["exit_code"] is not None
        return int(terminal["exit_code"])
    except Exception:
        # A failed final write is still not allowed to disguise the
        # controller exception; the strict helper has already attempted
        # its unavailable fallback without holding a scan under the lock.
        return EXIT_BY_REASON["status_unavailable"]


def controller(job: Path, ownership_fd: int) -> int:
    binding = _ControllerBinding()
    execution = _ProviderExecution()
    launch = _ScopedLaunch()

    def interrupted(number: int, _frame: Any) -> None:
        _latch_controller_signal(execution, number)

    prior_handlers = {
        number: signal.getsignal(number)
        for number in (signal.SIGHUP, signal.SIGINT, signal.SIGTERM)
    }
    for number in prior_handlers:
        signal.signal(number, interrupted)
    try:
        with inherited_lifecycle_lock(job, ownership_fd):
            early_exit = _claim_controller_attempt(job, binding)
            if early_exit is not None:
                return early_exit
            early_exit = _bind_controller_inputs(job, binding)
            if early_exit is not None:
                return early_exit
            streams = _ControllerStreams(*_attempt_paths(job, binding.state["attempt"]))
            early_exit = _open_controller_artifacts(job, binding, execution, streams)
            if early_exit is not None:
                return early_exit
            _build_controller_argv(binding, launch)
            streams.selector = selectors.DefaultSelector()
            outcome = _ControllerOutcome()
            candidate_data = _CandidateReconciliation()
            try:
                _launch_controller_provider(job, binding, execution, streams, launch, outcome)
                _monitor_controller_provider(job, binding, execution, streams, launch, outcome)
                _reap_controller_provider(job, binding, execution, streams, launch, outcome)
                _observe_controller_terminal(binding, execution, streams, launch, outcome)
                _begin_controller_completion(execution, streams, outcome, candidate_data, prior_handlers)
                _cleanup_controller_stage(job, binding, streams, launch, outcome, candidate_data)
                _observe_controller_cancel(job, binding, outcome)
                _reconcile_controller_candidate(binding, launch, outcome, candidate_data)
                return _publish_controller_terminal(job, binding, execution, streams, outcome, candidate_data)
            finally:
                _cleanup_controller_resources(binding, execution, streams, launch)
    except Exception:
        if execution.process is None and execution.started_mono is None:
            raise
        return _recover_controller_failure(job, binding, execution, launch)
    finally:
        for number, handler in prior_handlers.items():
            signal.signal(number, handler)


def create_state(
    job: Path, origin: str, *, resume: bool, approve_sha: str | None = None,
    verification: dict[str, Any] | None = None,
    require_initial_choice: bool = False,
) -> tuple[DispatchState, str]:
    command, command_raw, command_info = load_command(job)
    if require_initial_choice:
        _require_initial_transmission_choice(command, origin)
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
            command = _load_bound_command(job, state, stage_readonly=False)
            if _job_is_inside_worktree(job, command["workdir"]):
                raise DispatchError("dispatch job directory cannot be inside the target workdir")
            command, state = _bound_lifecycle_inputs(job, state, command)
            if not _selection_launch_is_authorized(_load_bound_selection(command, state)):
                raise DispatchError("dispatch selection has no current executable binding")
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
            if float(state["elapsed_seconds"]) >= _provider_max_seconds(state):
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
                    explain_worktree_rejection=True,
                    repair_authority_state=(
                        state if origin == "conversation-continue" else None
                    ),
                )
                next_state["sequence"] = state["sequence"] + 1
                next_state["previous_state_sha256"] = sha
                next_state["conversation_id"] = conversation
                next_state["resume_available"] = conversation is not None
                next_state["attempt_base_elapsed"] = float(state["elapsed_seconds"])
                next_state["elapsed_seconds"] = float(state["elapsed_seconds"])
                next_state["hard_seconds"] = min(
                    _provider_max_seconds(state),
                    float(state["elapsed_seconds"]) + float(command["hard_seconds"]),
                )
                next_state["max_seconds"] = float(state["max_seconds"])
                next_state["self_verification_elapsed_seconds"] = float(
                    state["self_verification_elapsed_seconds"]
                )
                next_state["self_verification_run"] = state[
                    "self_verification_run"
                ]
                if state["workflow"] != "legacy":
                    next_state["phase"] = "repairing" if origin == "conversation-continue" else "dispatching"
                    next_state["check_summary"] = state["check_summary"]
                    next_state["check_counts"] = state["check_counts"]
                    next_state["last_success_path"] = state["result_path"] or state["last_success_path"]
                    next_state["last_success_sha256"] = state["result_sha256"] or state["last_success_sha256"]
                    next_state["last_success_identity"] = state["result_identity"] or state["last_success_identity"]
                    if origin == "conversation-continue":
                        state_fields: Mapping[str, object] = state
                        for key in (
                            "result_path", "result_sha256", "result_identity",
                            "candidate_recognized", "candidate_source", "result_available",
                            "candidate_worktree_sha256", "candidate_worktree_entries",
                            "candidate_worktree_path_facts",
                            "driver_disposition", "worktree_reconciliation",
                            "worktree_changes_present",
                            "worktree_changed_since_dispatch",
                        ):
                            next_state[key] = state_fields[key]
                        for key in (
                            "repair_lineage_sha256",
                            "repair_parent_result_sha256",
                            "repair_parent_worktree_sha256",
                            "repair_lineage_attempt",
                            "reconciliation_manifest_sha256",
                        ):
                            next_state[key] = state_fields[key]
                if verification_path is not None:
                    next_state.update({
                        "verification_path": str(verification_path),
                        "verification_sha256": verification_sha,
                        "verification_identity": list(cast(tuple[int, int, int, int, int], verification_identity)),
                        "check_summary": cast(dict[str, Any], verification)["summary"],
                        "check_counts": _verification_counts(cast(dict[str, Any], verification)),
                    })
                validated_next = validate_state(next_state)
                current, _info = read_regular(path, MAX_STATE_BYTES, "dispatch state")
                if current != raw:
                    raise DispatchError("dispatch state changed before continuation")
                _new_raw, new_sha = write_atomic(job, STATE_NAME, next_state)
                return validated_next, new_sha
            except Exception:
                _discard_new_verification(verification_path, verification_identity)
                raise
        if path.exists() or path.is_symlink():
            raise DispatchError("dispatch state already exists")
        if command.get("workflow") == "project" and _job_is_inside_worktree(job, command["workdir"]):
            raise DispatchError("dispatch job directory cannot be inside the target workdir")
        initial = initial_state(
            command, origin, 1, command_sha=digest(command_raw),
            command_identity=command_info, stage_sha=stage_sha, stage_identity=stage_info,
            schema_bindings=schema_bindings,
            explain_worktree_rejection=True,
        )
        state = validate_state(initial)
        _raw, sha = write_atomic(job, STATE_NAME, state)
        return state, sha


def spawn(
    job: Path, origin: str, *, resume: bool, foreground: bool,
    approve_sha: str | None = None, verification: dict[str, Any] | None = None,
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
                verification=verification,
                require_initial_choice=True,
            )
            if parent_signal is not None:
                _terminalize_queued_signal(job, parent_signal)
                return 128 + parent_signal
            bound_command = _load_bound_command(job, state, stage_readonly=False)
            controller_environment = _provider_environment(bound_command)
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
    state: Mapping[str, Any], *, status: str, reason: str, exit_code: int,
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
        and float(state["elapsed_seconds"]) < _provider_max_seconds(state)
        and status == "failed"
        and reason not in {"permission_required", "selection_preflight_failed", "model_selection_rejected"}
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
            and reason not in {"permission_required", "selection_preflight_failed", "model_selection_rejected"}
            and state["attempt_origin"] != "conversation-continue"
        )
        updates.update({
            "resume_available": resume_eligible,
            "driver_disposition": "not_applicable",
            "next_action": "resume" if resume_eligible else "blocked",
            "next_action_command": None,
        })
    updates.update({
        "phase": "blocked" if candidate_unavailable else ("awaiting-verification" if candidate else "attempt-failed"),
        "assurance": "blocked" if candidate_unavailable else "pending",
    })
    return updates


def _terminalize_owned(
    job: Path, state: Mapping[str, Any], *, status: str, reason: str, exit_code: int,
    failure_stage: str | None = None, expected_controller_pid: int | None = None,
    elapsed_seconds: float | None = None, postlaunch_cancel: bool = False,
) -> tuple[DispatchState, bytes, str]:
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
            current_fields: Mapping[str, object] = current
            prior_candidate_is_bound = bool(
                current["attempt_origin"] == "conversation-continue"
                and current["candidate_recognized"]
                and current["candidate_source"] != "none"
                and current["result_available"]
                and current["failure_stage"] is None
                and all(current_fields[key] is not None for key in (
                    "result_path", "result_sha256", "result_identity",
                    "candidate_worktree_sha256", "candidate_worktree_entries",
                ))
            )
            candidate = bool(current["candidate_recognized"])
            # An ordinary post-launch cancellation has no candidate to
            # protect, so it remains cancelled.  Only an *incomplete* prior
            # candidate takes fail-closed precedence over cancellation: that
            # combination cannot truthfully expose a readable result.
            was_cancelled = bool(
                current["cancel_requested"]
                and (not candidate or prior_candidate_is_bound)
            )
            candidate_unavailable = bool(candidate and not prior_candidate_is_bound)
            updates = {
                "status": "cancelled" if was_cancelled else "failed",
                "reason": "cancelled" if was_cancelled else "status_unavailable",
                "exit_code": (
                    EXIT_BY_REASON["cancelled"] if was_cancelled
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
                "failure_stage": None if (was_cancelled or prior_candidate_is_bound) else "binding_failure",
                "remote_cancel_unverified": bool(was_cancelled and postlaunch_cancel),
                "provider_terminal_status": current.get("provider_terminal_status", "unknown"),
            }
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


def _recover_interrupted_self_verification(job: Path) -> tuple[DispatchState, bytes, str]:
    """Recover only while holding the lifecycle lock; never rerun a check."""
    with state_lock(job):
        state, raw, sha = load_state(job)
        if state.get("phase") != "self-verifying":
            return state, raw, sha
        remaining = SELF_VERIFICATION.remaining_seconds(
            state["max_seconds"], state["elapsed_seconds"],
            state["self_verification_elapsed_seconds"],
        )
        started = state["self_verification_started_epoch"]
        result_sha = state["result_sha256"]
        # validate_state proves both bindings for the self-verifying phase above.
        assert started is not None and result_sha is not None
        charge = min(remaining, max(0.0, time.time() - started))
        updates = {
            "phase": state["self_verification_return_phase"],
            "self_verification_started_epoch": None,
            "self_verification_return_phase": None,
            "self_verification_elapsed_seconds": state["self_verification_elapsed_seconds"] + charge,
            "verification_path": None, "verification_sha256": None,
            "verification_identity": None,
            "check_counts": _verification_counts(SELF_VERIFICATION.advisory_feedback(result_sha, [])),
            "check_summary": "Self-verification was interrupted; wall-clock time was conservatively charged.",
        }
        updates["continue_available"] = _continue_from_facts({**state, **updates}, time.time())
        return _transition_locked(job, state, raw, updates)


def command_status(job: Path, output_format: str = "json") -> int:
    state, _raw, sha = read_state_snapshot(job)
    if state.get("phase") == "self-verifying":
        try:
            with lifecycle_lock(job, blocking=False):
                state, _raw, sha = _recover_interrupted_self_verification(job)
        except DispatchError as exc:
            if str(exc) != "dispatch controller is active":
                raise
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
        if state.get("phase") == "self-verifying":
            try:
                with lifecycle_lock(job, blocking=False):
                    state, _raw, sha = _recover_interrupted_self_verification(job)
            except DispatchError as exc:
                if str(exc) != "dispatch controller is active":
                    raise
        if sha != after or (state["status"] in TERMINAL and state.get("phase") != "self-verifying"):
            print_control_status(state, sha, output_format, job=job)
            return 0
        if time.monotonic() >= deadline:
            print_control_status(state, sha, output_format, job=job)
            return 0
        time.sleep(min(0.20, max(0.0, deadline - time.monotonic())))


def command_result(job: Path, output_format: str = "json") -> int:
    state, _raw, sha = read_state_snapshot(job)
    if state["candidate_recognized"]:
        if _is_active(state) or state.get("phase") == "self-verifying":
            raise DispatchError("dispatch result is unavailable while a repair is active")
        _command, candidate_raw = _bound_current_candidate(job, state)
        if output_format == "text":
            print_text_status(state, sha, job=job)
        else:
            sys.stdout.buffer.write(candidate_raw)
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


def _bound_self_verification_feedback(job: Path, state: Mapping[str, Any]) -> dict[str, Any]:
    """Read only the advisory artifact published for this candidate attempt."""
    expected = job / "continue-staged" / f"self-verify-{state['attempt']:03d}.json"
    if (
        not state.get("allow_self_verification")
        or state.get("self_verification_run") != state["attempt"]
        or state.get("phase") not in {"awaiting-verification", "repair-failed"}
        or state["verification_path"] != str(expected)
    ):
        raise DispatchError("current self-verification feedback is unavailable")
    raw, info = read_regular(expected, MAX_VERIFICATION_BYTES, "self-verification feedback", allowed_modes=(0o400,))
    if digest(raw) != state["verification_sha256"] or list(_identity(info)) != state["verification_identity"]:
        raise DispatchError("self-verification feedback binding changed")
    parent = expected.parent.lstat()
    if (not stat.S_ISDIR(parent.st_mode) or stat.S_ISLNK(parent.st_mode)
            or parent.st_uid != os.getuid() or stat.S_IMODE(parent.st_mode) != 0o700):
        raise DispatchError("verification staging directory changed")
    feedback = _validate_verification(parse_json(raw, "self-verification feedback"))
    _require_current_candidate_verification(feedback, state)
    if feedback["coverage"] != "partial" or feedback["diff_review_complete"]:
        raise DispatchError("self-verification feedback is not advisory")
    return feedback


def command_continue(
    job: Path, approve_sha: str,
    output_format: str = "json",
    use_self_verification: bool = False,
) -> int:
    if use_self_verification:
        with state_lock(job):
            state, _raw, sha = load_state(job)
            if sha != approve_sha:
                raise _state_approval_error(state, sha, "continue")
            verification = _bound_self_verification_feedback(job, state)
    else:
        verification = _verification_from_stdin()
    return spawn(
        job, "conversation-continue", resume=True, foreground=False,
        approve_sha=approve_sha,
        verification=verification, output_format=output_format,
    )


def command_finalize(
    job: Path, approve_sha: str,
    assurance: str, output_format: str = "json",
) -> int:
    if assurance not in {"verified", "partially_verified", "rejected", "blocked"}:
        raise DispatchError("project assurance is invalid")
    verification = _verification_from_stdin()
    with state_lock(job):
        state, raw, sha = load_state(job)
        if sha != approve_sha:
            raise _state_approval_error(state, sha, "finalize")
        command = _load_bound_command(job, state, stage_readonly=False)
        command, state = _bound_lifecycle_inputs(
            job, state, command, bind_terminal_candidate=True,
        )
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
            if seconds <= 0 or state["hard_seconds"] + seconds > _provider_max_seconds(state):
                raise DispatchError("deadline extension exceeds max runtime")
            updates = {"hard_seconds": state["hard_seconds"] + seconds}
        state, _raw, sha = _transition_locked(
            job, state, raw, updates,
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
    for name in ("run", "start", "resume", "restart", "continue", "status", "result", "verification-copy", "self-verify", "controller"):
        item = commands.add_parser(name)
        item.add_argument("--job-dir", required=True)
        if name == "controller":
            item.add_argument("--ownership-fd", required=True, type=int)
        if name in {"resume", "restart", "continue"}:
            item.add_argument("--approve-state-sha", required=name != "resume")
        if name in {"resume", "restart", "continue", "status", "result", "verification-copy"}:
            item.add_argument("--format", choices=("json", "text"), default="json")
        if name == "verification-copy":
            item.add_argument("--destination", required=True)
        if name == "continue":
            item.add_argument("--use-self-verification", action="store_true")
        if name == "self-verify":
            item.add_argument("--approve-state-sha", required=True)
            item.add_argument("--format", choices=("json", "text"), default="json")
    finalize = commands.add_parser("finalize")
    finalize.add_argument("--job-dir", required=True)
    finalize.add_argument("--approve-state-sha", required=True)
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
    arguments = list(sys.argv[1:] if argv is None else argv)
    if any(arg.partition("=")[0] == "--approve-migration-sha" for arg in arguments):
        raise DispatchError(
            f"--approve-migration-sha was removed after {LAST_DOCUMENTED_LEGACY_SCHEMA_RELEASE}; "
            "finish or discard the old job with the release that created it."
        )
    args = parser().parse_args(arguments)
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
            output_format=args.format,
        )
    if args.command == "restart":
        return spawn(
            job, "fresh-restart", resume=True, foreground=False,
            approve_sha=args.approve_state_sha,
            output_format=args.format,
        )
    if args.command == "continue":
        return command_continue(
            job, args.approve_state_sha, args.format,
            use_self_verification=args.use_self_verification,
        )
    if args.command == "status":
        return command_status(job, args.format)
    if args.command == "wait":
        return command_wait(job, args.after_state_sha, args.timeout, args.format)
    if args.command == "result":
        return command_result(job, args.format)
    if args.command == "verification-copy":
        return command_verification_copy(job, Path(args.destination), args.format)
    if args.command == "self-verify":
        try:
            return SELF_VERIFICATION.command_self_verify(
                VERIFICATION_API, job, args.approve_state_sha, args.format, containment=CONTAINMENT,
            )
        except (SELF_VERIFICATION.VerificationError, OSError) as exc:
            raise DispatchError("self-verification could not bind or execute the approved checks") from exc
    if args.command == "finalize":
        return command_finalize(
            job, args.approve_state_sha,
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
            raise SystemExit(EXIT_BY_REASON["resume_failed"])  # noqa: B904 -- preserve existing exception context and public diagnostics
        if command_name in {"status", "wait", "result", "verification-copy", "self-verify"}:
            raise SystemExit(EXIT_BY_REASON["status_unavailable"])  # noqa: B904 -- preserve existing exception context and public diagnostics
        raise SystemExit(64)  # noqa: B904 -- preserve existing exception context and public diagnostics
