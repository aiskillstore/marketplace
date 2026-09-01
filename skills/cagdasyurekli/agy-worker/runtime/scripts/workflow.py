#!/usr/bin/env python3
"""Thin canonical workflow facade over job lifecycle, dispatch, and verification.

Commands:
  run              Obtain preview, enforce preview approval, and invoke dispatch.
  status           Strictly read-only bounded sanitized facts from bound authorities.
  verify-finalize  Delegate verification and finalization without inferring assurance.
"""

from __future__ import annotations

import argparse
import contextlib
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import stat
import subprocess
import sys
from typing import Any, Iterator

sys.dont_write_bytecode = True
SCRIPTS = Path(__file__).resolve(strict=True).parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from candidate_state import CandidateStateError, candidate_state_digest
import agy_dispatch as DISPATCH

SCHEMA_VERSION = 1
FACADE_SCHEMA_VERSION = 2
KIND_WORKFLOW_STATE = "agy-worker-workflow-state"
KIND_WORKFLOW_STATUS = "agy-worker-workflow-status"
KIND_JOB_STATE = "agy-worker-local-job-state"
FACADE_ORIGIN = "workflow-facade"
SIGNALS = (signal.SIGHUP, signal.SIGINT, signal.SIGTERM)
JOB_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,79}$")
SHA_RE = re.compile(r"^[0-9a-f]{64}$")
COMMIT_RE = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
MAX_STATE_BYTES = 128 * 1024
MAX_RECEIPT_BYTES = 1024 * 1024


class WorkflowError(ValueError):
    """Fail-closed error in workflow facade."""


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=True, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def identity(metadata: os.stat_result) -> dict[str, int]:
    return {
        "dev": metadata.st_dev,
        "ino": metadata.st_ino,
        "mode": stat.S_IMODE(metadata.st_mode),
        "uid": metadata.st_uid,
        "gid": metadata.st_gid,
    }


def job_identity(metadata: os.stat_result) -> dict[str, int]:
    return {
        "dev": metadata.st_dev,
        "ino": metadata.st_ino,
        "mode": stat.S_IMODE(metadata.st_mode),
        "uid": metadata.st_uid,
    }


def same_identity(metadata: os.stat_result, expected: dict[str, int]) -> bool:
    return identity(metadata) == expected


def real_absolute(path: Path, label: str, *, must_exist: bool = True) -> Path:
    if not path.is_absolute() or "\n" in str(path) or "\r" in str(path) or "\0" in str(path):
        raise WorkflowError(f"{label} must be one canonical absolute path")
    canonical = Path(os.path.realpath(path))
    if canonical != path:
        raise WorkflowError(f"{label} must be one canonical absolute path")
    if must_exist and not path.exists():
        raise WorkflowError(f"{label} is unavailable")
    return path


def contains(parent: Path, child: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def validate_private_parent(parent: Path) -> tuple[Path, int]:
    parent = real_absolute(parent, "state parent")
    metadata = parent.lstat()
    if (
        not stat.S_ISDIR(metadata.st_mode)
        or stat.S_ISLNK(metadata.st_mode)
        or metadata.st_uid != os.getuid()
        or stat.S_IMODE(metadata.st_mode) != 0o700
    ):
        raise WorkflowError("state parent must be one real owner-private mode-0700 directory")
    descriptor = os.open(
        parent,
        os.O_RDONLY
        | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_NOFOLLOW", 0),
    )
    opened = os.fstat(descriptor)
    if not same_identity(opened, identity(metadata)):
        os.close(descriptor)
        raise WorkflowError("state parent identity changed while opened")
    return parent, descriptor


def read_regular(path: Path, maximum: int, label: str, *, private: bool) -> tuple[bytes, os.stat_result]:
    try:
        descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    except OSError as exc:
        raise WorkflowError(f"{label} is unavailable") from exc
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode):
            raise WorkflowError(f"{label} must be one real file")
        if private and (
            metadata.st_uid != os.getuid() or stat.S_IMODE(metadata.st_mode) != 0o600
        ):
            raise WorkflowError(f"{label} must be owner-private mode 0600")
        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = os.read(descriptor, min(65536, maximum + 1 - total))
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
            if total > maximum:
                raise WorkflowError(f"{label} is oversized")
        if len(b"".join(chunks)) != metadata.st_size:
            raise WorkflowError(f"{label} changed while read")
        return b"".join(chunks), metadata
    finally:
        os.close(descriptor)


def read_regular_at(
    parent_fd: int,
    name: str,
    maximum: int,
    label: str,
    *,
    private: bool,
) -> tuple[bytes, os.stat_result]:
    try:
        descriptor = os.open(
            name,
            os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0),
            dir_fd=parent_fd,
        )
    except OSError as exc:
        raise WorkflowError(f"{label} is unavailable") from exc
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode):
            raise WorkflowError(f"{label} must be one real file")
        if private and (
            metadata.st_uid != os.getuid() or stat.S_IMODE(metadata.st_mode) != 0o600
        ):
            raise WorkflowError(f"{label} must be owner-private mode 0600")
        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = os.read(descriptor, min(65536, maximum + 1 - total))
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
            if total > maximum:
                raise WorkflowError(f"{label} is oversized")
        if total != metadata.st_size:
            raise WorkflowError(f"{label} changed while read")
        return b"".join(chunks), metadata
    finally:
        os.close(descriptor)


def _write_all(descriptor: int, data: bytes) -> None:
    view = memoryview(data)
    total = 0
    while total < len(data):
        written = os.write(descriptor, view[total:])
        if written <= 0:
            raise WorkflowError("short write during state creation")
        total += written


def parse_strict(data: bytes, label: str) -> Any:
    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise WorkflowError(f"{label} has a duplicate key")
            result[key] = value
        return result

    try:
        return json.loads(data.decode("utf-8", "strict"), object_pairs_hook=pairs)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise WorkflowError(f"{label} is invalid") from exc


def validate_workflow_state(state: dict[str, Any]) -> dict[str, Any]:
    base_keys = {
        "schema_version", "kind", "job_id", "repo_path", "repo_identity",
        "worktree_path", "worktree_identity", "branch", "branch_ref", "base",
        "preview_manifest_sha256", "dispatch_job_dir", "job_state_path",
        "receipt_path",
    }
    facade_keys = base_keys | {"origin", "job_state_sha256"}
    expected_keys = base_keys if state.get("schema_version") == SCHEMA_VERSION else facade_keys
    if set(state.keys()) != expected_keys:
        raise WorkflowError("workflow state fields mismatch")
    if state["schema_version"] not in {SCHEMA_VERSION, FACADE_SCHEMA_VERSION}:
        raise WorkflowError("workflow state schema_version is invalid")
    if state["kind"] != KIND_WORKFLOW_STATE:
        raise WorkflowError("workflow state kind is invalid")
    if not isinstance(state["job_id"], str) or JOB_RE.fullmatch(state["job_id"]) is None:
        raise WorkflowError("workflow state job_id is invalid")
    if not isinstance(state["base"], str) or COMMIT_RE.fullmatch(state["base"]) is None:
        raise WorkflowError("workflow state base is invalid")
    if not isinstance(state["preview_manifest_sha256"], str) or SHA_RE.fullmatch(state["preview_manifest_sha256"]) is None:
        raise WorkflowError("workflow state preview_manifest_sha256 is invalid")
    for label in ("repo_identity", "worktree_identity"):
        value = state[label]
        if not isinstance(value, dict) or set(value) != {"dev", "ino", "mode", "uid", "gid"}:
            raise WorkflowError(f"workflow state {label} is invalid")
        if any(type(item) is not int or item < 0 for item in value.values()):
            raise WorkflowError(f"workflow state {label} is invalid")
    for label in ("repo_path", "worktree_path"):
        value = state[label]
        if (
            not isinstance(value, str)
            or not Path(value).is_absolute()
            or "\n" in value
            or "\r" in value
            or "\0" in value
        ):
            raise WorkflowError(f"workflow state {label} is invalid")
    if (
        not isinstance(state["branch"], str)
        or not state["branch"]
        or "\n" in state["branch"]
        or "\r" in state["branch"]
        or state["branch_ref"] != f"refs/heads/{state['branch']}"
    ):
        raise WorkflowError("workflow state branch binding is invalid")
    for label in ("dispatch_job_dir", "job_state_path", "receipt_path"):
        value = state[label]
        if value is not None and (
            not isinstance(value, str)
            or not Path(value).is_absolute()
            or "\n" in value
            or "\r" in value
            or "\0" in value
        ):
            raise WorkflowError(f"workflow state {label} is invalid")
    if state["schema_version"] == FACADE_SCHEMA_VERSION:
        if state["origin"] != FACADE_ORIGIN:
            raise WorkflowError("workflow state origin is invalid")
        if state["job_state_path"] is None:
            raise WorkflowError("workflow state job_state_path is required")
        if (
            not isinstance(state["job_state_sha256"], str)
            or SHA_RE.fullmatch(state["job_state_sha256"]) is None
        ):
            raise WorkflowError("workflow state job_state_sha256 is invalid")
    return state


class WorkflowStateStore:
    def __init__(self, path: Path, *, initial: bool = False) -> None:
        self.path = real_absolute(path, "workflow state", must_exist=not initial)
        self.parent, self.parent_fd = validate_private_parent(self.path.parent)
        self.parent_identity = identity(os.fstat(self.parent_fd))
        try:
            fcntl.flock(self.parent_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            os.close(self.parent_fd)
            self.parent_fd = -1
            raise WorkflowError("state parent is busy") from exc
        self.name = self.path.name
        if not self.name or self.name in {".", ".."}:
            raise WorkflowError("state name is invalid")
        self.raw: bytes | None = None
        self.metadata: os.stat_result | None = None
        self.sha256: str | None = None
        self.value: dict[str, Any] | None = None
        if not initial:
            self.load()

    def close(self) -> None:
        if self.parent_fd >= 0:
            os.close(self.parent_fd)
            self.parent_fd = -1

    def _validate_parent_path(self) -> None:
        try:
            current = self.parent.lstat()
        except OSError as exc:
            raise WorkflowError("state parent path changed") from exc
        if not same_identity(current, self.parent_identity):
            raise WorkflowError("state parent path changed")

    @contextlib.contextmanager
    def _blocked(self) -> Iterator[None]:
        prior = signal.pthread_sigmask(signal.SIG_BLOCK, SIGNALS)
        try:
            yield
        finally:
            signal.pthread_sigmask(signal.SIG_SETMASK, prior)

    def load(self) -> dict[str, Any]:
        self._validate_parent_path()
        data, metadata = read_regular_at(
            self.parent_fd, self.name, MAX_STATE_BYTES, "workflow state", private=True
        )
        value = validate_workflow_state(parse_strict(data, "workflow state"))
        if canonical_json(value) + b"\n" != data and canonical_json(value) != data:
            raise WorkflowError("workflow state bytes are not canonical")
        self.raw, self.metadata, self.sha256, self.value = (
            data, metadata, sha256_bytes(data), value
        )
        return value

    def create(self, value: dict[str, Any]) -> str:
        validate_workflow_state(value)
        data = canonical_json(value) + b"\n"
        with self._blocked():
            self._validate_parent_path()
            descriptor = os.open(
                self.name,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
                0o600,
                dir_fd=self.parent_fd,
            )
            try:
                os.fchmod(descriptor, 0o600)
                _write_all(descriptor, data)
                os.fsync(descriptor)
                metadata = os.fstat(descriptor)
            finally:
                os.close(descriptor)
            self.raw, self.metadata, self.sha256, self.value = (
                data, metadata, sha256_bytes(data), value
            )
            os.fsync(self.parent_fd)
            self._validate_parent_path()
        assert self.sha256 is not None
        return self.sha256

    def update(self, changes: dict[str, Any]) -> str:
        if self.value is None or self.metadata is None:
            raise WorkflowError("state must be loaded before update")
        updated = dict(self.value)
        updated.update(changes)
        validate_workflow_state(updated)
        data = canonical_json(updated) + b"\n"
        with self._blocked():
            self._validate_parent_path()
            temp_name = f".tmp-{self.name}-{os.getpid()}"
            descriptor = os.open(
                temp_name,
                os.O_WRONLY | os.O_CREAT | os.O_TRUNC | getattr(os, "O_NOFOLLOW", 0),
                0o600,
                dir_fd=self.parent_fd,
            )
            try:
                os.fchmod(descriptor, 0o600)
                _write_all(descriptor, data)
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
            try:
                os.replace(self.parent / temp_name, self.path)
            except OSError as exc:
                try:
                    os.unlink(self.parent / temp_name)
                except OSError:
                    pass
                raise WorkflowError("state update replace failed") from exc
            os.fsync(self.parent_fd)
            self._validate_parent_path()
            current_data, current_meta = read_regular_at(
                self.parent_fd, self.name, MAX_STATE_BYTES, "workflow state", private=True
            )
            self.raw, self.metadata, self.sha256, self.value = (
                current_data, current_meta, sha256_bytes(current_data), updated
            )
        assert self.sha256 is not None
        return self.sha256

    def discard_exact(self, expected_sha: str, expected_identity: dict[str, int]) -> None:
        """Remove only the unchanged state file created by this invocation."""

        with self._blocked():
            self._validate_parent_path()
            current_data, current_meta = read_regular_at(
                self.parent_fd, self.name, MAX_STATE_BYTES, "workflow state", private=True
            )
            if (
                sha256_bytes(current_data) != expected_sha
                or not same_identity(current_meta, expected_identity)
            ):
                raise WorkflowError("workflow state changed before pre-dispatch rollback")
            try:
                os.unlink(self.name, dir_fd=self.parent_fd)
            except OSError as exc:
                raise WorkflowError("workflow state rollback failed") from exc
            os.fsync(self.parent_fd)
            self._validate_parent_path()


def validate_worktree_registration(repo: Path, worktree: Path) -> None:
    try:
        proc = subprocess.run(
            ["/usr/bin/git", "-C", str(repo), "worktree", "list", "--porcelain", "-z"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5.0,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise WorkflowError("failed to query git worktree list") from exc
    if proc.returncode != 0:
        raise WorkflowError("git worktree list failed")

    raw = proc.stdout
    registered_paths: set[str] = set()
    for item in raw.split(b"\0"):
        if item.startswith(b"worktree "):
            raw_path = item[len(b"worktree "):].decode("utf-8", errors="replace")
            try:
                registered_paths.add(str(Path(os.path.realpath(raw_path))))
            except Exception:
                registered_paths.add(raw_path)

    canonical_worktree = str(Path(os.path.realpath(worktree)))
    if canonical_worktree not in registered_paths and str(worktree) not in registered_paths:
        raise WorkflowError("worktree is not registered in repository worktree list")


def validate_branch_backed_worktree(worktree: Path, branch: str) -> None:
    git_marker = worktree / ".git"
    if not git_marker.exists() or git_marker.is_symlink() or not git_marker.is_file():
        raise WorkflowError("worktree .git control marker is missing or not a file")
    content = git_marker.read_text(encoding="utf-8").strip()
    if not content.startswith("gitdir: "):
        raise WorkflowError("worktree .git control marker is malformed")
    gitdir = Path(content[len("gitdir: "):])
    if not gitdir.is_absolute() or not gitdir.exists() or gitdir.is_symlink():
        raise WorkflowError("worktree gitdir is invalid")
    head_file = gitdir / "HEAD"
    if not head_file.exists() or head_file.is_symlink() or not head_file.is_file():
        raise WorkflowError("worktree HEAD file is invalid")
    head_content = head_file.read_text(encoding="utf-8").strip()
    expected_ref = f"ref: refs/heads/{branch}"
    if head_content != expected_ref:
        raise WorkflowError(f"worktree HEAD is not branch-backed on {branch}")


def validate_base_commit(repo: Path, base: str) -> None:
    if COMMIT_RE.fullmatch(base) is None:
        raise WorkflowError("base commit format is invalid")
    try:
        proc = subprocess.run(
            ["/usr/bin/git", "-C", str(repo), "cat-file", "-e", f"{base}^{{commit}}"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5.0,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise WorkflowError("failed to verify base commit") from exc
    if proc.returncode != 0:
        raise WorkflowError("base commit does not exist in repository")


def canonical_transmission_preview(worktree: Path) -> tuple[bytes, dict[str, Any]]:
    """Delegate preview generation to the canonical public runtime command."""

    preview_command = SCRIPTS.parent / "agy-worker.sh"
    try:
        proc = subprocess.run(
            [
                str(preview_command),
                "transmission-preview",
                "--workdir",
                str(worktree),
            ],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=15.0,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise WorkflowError("transmission preview unavailable") from exc
    if proc.returncode != 0:
        raise WorkflowError("transmission preview unavailable")
    value = parse_strict(proc.stdout, "transmission preview")
    if not isinstance(value, dict):
        raise WorkflowError("transmission preview contract is invalid")
    manifest_sha = value.get("manifest_sha256")
    manifest = value.get("manifest")
    if (
        not isinstance(manifest_sha, str)
        or SHA_RE.fullmatch(manifest_sha) is None
        or not isinstance(manifest, dict)
        or canonical_json(value) + b"\n" != proc.stdout
    ):
        raise WorkflowError("transmission preview contract is invalid")
    return proc.stdout, value


def _owner_directory(path: Path, label: str, *, private: bool) -> Path:
    path = real_absolute(path, label)
    metadata = path.lstat()
    if (
        not stat.S_ISDIR(metadata.st_mode)
        or stat.S_ISLNK(metadata.st_mode)
        or metadata.st_uid != os.getuid()
        or (private and stat.S_IMODE(metadata.st_mode) != 0o700)
        or (not private and stat.S_IMODE(metadata.st_mode) & 0o022 != 0)
    ):
        requirement = "owner-private mode-0700" if private else "owner-controlled"
        raise WorkflowError(f"{label} must be one real {requirement} directory")
    return path


def _ensure_private_child(parent: Path, name: str, label: str) -> Path:
    _owner_directory(parent, f"{label} parent", private=False)
    child = parent / name
    if child.exists() or child.is_symlink():
        return _owner_directory(child, label, private=True)
    try:
        os.mkdir(child, 0o700)
    except OSError as exc:
        raise WorkflowError(f"failed to create {label}") from exc
    return _owner_directory(child, label, private=True)


def _ensure_owner_child(parent: Path, name: str, label: str) -> Path:
    _owner_directory(parent, f"{label} parent", private=False)
    child = parent / name
    if child.exists() or child.is_symlink():
        return _owner_directory(child, label, private=False)
    try:
        os.mkdir(child, 0o700)
    except OSError as exc:
        raise WorkflowError(f"failed to create {label}") from exc
    return _owner_directory(child, label, private=False)


def _state_home() -> Path:
    configured = os.environ.get("XDG_STATE_HOME")
    if configured:
        path = Path(configured)
        if not path.is_absolute():
            raise WorkflowError("XDG_STATE_HOME must be one absolute path")
        return _owner_directory(path, "XDG_STATE_HOME", private=False)

    home_text = os.environ.get("HOME")
    if not home_text or not Path(home_text).is_absolute():
        raise WorkflowError("HOME must be one absolute path")
    home = _owner_directory(Path(home_text), "HOME", private=False)
    local = _ensure_owner_child(home, ".local", "HOME state parent")
    return _ensure_owner_child(local, "state", "HOME state directory")


def _derived_bindings(repo: Path, job_id: str) -> dict[str, Path | str]:
    if JOB_RE.fullmatch(job_id or "") is None:
        raise WorkflowError("job ID is invalid")
    state_home = _state_home()
    prospective = state_home / "agy-worker" / "workflows"
    if contains(repo, prospective) or contains(prospective, repo):
        raise WorkflowError("workflow state root must be outside the repository")
    root = _ensure_private_child(state_home, "agy-worker", "agy-worker state root")
    workflows = _ensure_private_child(root, "workflows", "workflow state root")
    repo_key = sha256_bytes(str(repo).encode("utf-8"))[:24]
    repo_root = _ensure_private_child(workflows, repo_key, "repository workflow root")
    job_root = _ensure_private_child(repo_root, job_id, "job workflow root")
    logs = _ensure_private_child(job_root, "logs", "job log root")
    branch_key = sha256_bytes(f"{repo_key}\0{job_id}".encode("utf-8"))[:20]
    return {
        "state": job_root / "workflow.json",
        "job_state": job_root / "job.json",
        "worktree": job_root / "worktree",
        "dispatch_job_dir": logs / job_id,
        "branch": f"agy/workflow-{branch_key}",
    }


def _git_head(repo: Path) -> str:
    environment = dict(os.environ)
    for name in tuple(environment):
        if name.startswith("GIT_"):
            environment.pop(name, None)
    environment.update(
        {
            "GIT_CONFIG_GLOBAL": "/dev/null",
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_TERMINAL_PROMPT": "0",
        }
    )
    try:
        proc = subprocess.run(
            ["/usr/bin/git", "-C", str(repo), "rev-parse", "--verify", "HEAD^{commit}"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=environment,
            timeout=5.0,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise WorkflowError("failed to resolve repository HEAD") from exc
    try:
        value = proc.stdout.decode("ascii", "strict").strip()
    except UnicodeDecodeError as exc:
        raise WorkflowError("repository HEAD is invalid") from exc
    if proc.returncode != 0 or COMMIT_RE.fullmatch(value) is None:
        raise WorkflowError("repository HEAD is unavailable")
    return value


def _run_lifecycle(*arguments: str) -> subprocess.CompletedProcess[bytes]:
    try:
        return subprocess.run(
            [str(SCRIPTS.parent / "job.sh"), *arguments],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=60.0,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise WorkflowError("job lifecycle command unavailable") from exc


def _job_state_snapshot(path: Path) -> tuple[dict[str, Any], str]:
    data, _metadata = read_regular(path, MAX_STATE_BYTES, "job state", private=True)
    value = parse_strict(data, "job state")
    if not isinstance(value, dict) or value.get("kind") != KIND_JOB_STATE:
        raise WorkflowError("job state contract is invalid")
    return value, sha256_bytes(data)


def _validate_facade_job_state(
    value: dict[str, Any], *, repo: Path, worktree: Path, branch: str,
    base: str, job_id: str,
) -> None:
    expected = {
        "schema_version": FACADE_SCHEMA_VERSION,
        "origin": FACADE_ORIGIN,
        "phase": "ready",
        "job_id": job_id,
        "repo_path": str(repo),
        "worktree_path": str(worktree),
        "branch": branch,
        "branch_ref": f"refs/heads/{branch}",
        "base": base,
        "receipt": None,
        "dispatch": None,
        "dispatch_job_dir": str(
            worktree.parent / "logs" / job_id
        ),
        "repo_identity": job_identity(repo.lstat()),
        "worktree_identity": job_identity(worktree.lstat()),
    }
    mismatched = [
        key for key, expected_value in expected.items()
        if value.get(key) != expected_value
    ]
    if mismatched:
        raise WorkflowError(
            "facade job state binding is unavailable or changed: "
            + ",".join(mismatched)
        )


def _rollback_facade_ready(
    *, state_path: Path, workflow_state_path: Path | None,
    workflow_sha: str | None, workflow_identity: dict[str, int] | None,
    repo: Path, worktree: Path, branch: str, base: str, job_id: str,
    dispatch_job_dir: Path,
) -> None:
    job_value, job_sha = _job_state_snapshot(state_path)
    _validate_facade_job_state(
        job_value, repo=repo, worktree=worktree, branch=branch,
        base=base, job_id=job_id,
    )
    proc = _run_lifecycle(
        "rollback-ready", "--state", str(state_path),
        "--approve-job", job_id, "--approve-state-sha", job_sha,
        "--repo", str(repo), "--worktree", str(worktree),
        "--branch", branch, "--base", base,
        "--dispatch-job-dir", str(dispatch_job_dir),
    )
    if proc.returncode != 0:
        raise WorkflowError("facade-created resources require advanced recovery")
    if (
        workflow_state_path is not None
        and workflow_sha is not None
        and workflow_identity is not None
    ):
        workflow_store = WorkflowStateStore(workflow_state_path, initial=False)
        try:
            workflow_store.discard_exact(workflow_sha, workflow_identity)
        finally:
            workflow_store.close()


class OrderedVerifier(argparse.Action):
    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: Any,
        option_string: str | None = None,
    ) -> None:
        items = getattr(namespace, self.dest, None)
        if items is None:
            items = []
            setattr(namespace, self.dest, items)
        items.append((self.const or option_string, values))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="workflow.sh",
        description="Canonical workflow facade over job lifecycle, dispatch, and verification.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 1. run
    run_parser = subparsers.add_parser("run", help="Obtain preview, verify approval, and dispatch.")
    run_parser.add_argument("--state", help="Advanced: explicit workflow state file.")
    run_parser.add_argument("--repo", required=True, help="Path to target repository.")
    run_parser.add_argument("--worktree", "--workdir", dest="worktree", help="Advanced: explicit branch-backed disposable worktree.")
    run_parser.add_argument("--branch", help="Advanced: explicit branch name.")
    run_parser.add_argument("--base", help="Immutable base commit SHA; defaults to current HEAD in ordinary mode.")
    run_parser.add_argument("--job-id", "--workflow-id", dest="job_id", required=True, help="Workflow job ID.")
    run_parser.add_argument("--approve-preview-sha", help="Approved transmission-preview manifest SHA-256.")
    run_parser.add_argument("--preview", action="store_true", help="Run transmission preview only.")
    run_parser.add_argument("--job-dir", help="Explicit dispatch job directory.")
    run_parser.add_argument("--job-state", help="Optional path to job.sh state file.")
    run_parser.add_argument("--workflow", choices=("explore", "task", "project"), default="task")
    run_parser.add_argument("--mode", choices=("plan", "accept-edits"), default="accept-edits")
    run_parser.add_argument("--tier")
    run_parser.add_argument("--model")
    run_parser.add_argument("--effort")
    run_parser.add_argument("--max-cycles", type=int)
    run_parser.add_argument("--idle-timeout")
    run_parser.add_argument("--hard-timeout")
    run_parser.add_argument("--max-runtime")
    run_parser.add_argument("--notice-interval")
    run_parser.add_argument("--provider-env", action="append", default=[])
    run_parser.add_argument("--task", "--prompt", dest="task")
    run_parser.add_argument("--format", choices=("json", "text"), default="json")

    # 2. status
    status_parser = subparsers.add_parser("status", help="Read-only bounded sanitized facts.")
    status_sources = status_parser.add_mutually_exclusive_group(required=True)
    status_sources.add_argument("--state", help="Workflow or existing low-level job state file.")
    status_sources.add_argument("--job-state", help="Existing low-level job state file.")
    status_sources.add_argument("--dispatch-state", help="Existing dispatcher state file.")
    status_sources.add_argument("--job-id", dest="dispatcher_job_id", help="Existing dispatcher job ID.")
    status_parser.add_argument("--format", choices=("json", "text"), default="json")

    # 3. verify-finalize
    vf_parser = subparsers.add_parser("verify-finalize", help="Run verification and finalization.")
    vf_parser.add_argument("--state", required=True, help="Path to workflow state file.")
    vf_parser.add_argument("--receipt", required=True, help="Path to write Evidence Receipt v1.")
    vf_parser.add_argument("--envelope", required=True, help="Path to worker result envelope JSON.")
    vf_parser.add_argument("--base", help="Optional immutable base commit SHA to recheck.")
    vf_parser.add_argument("--candidate-sha", help="Optional exact candidate state SHA to recheck.")
    vf_parser.add_argument("--allow", action="append", default=[])
    vf_parser.add_argument("--only", action="append", default=[])
    vf_parser.add_argument("--expect-edits", action="store_true")
    vf_parser.set_defaults(verifiers=[])
    vf_parser.add_argument("--verify-argv", dest="verifiers", action=OrderedVerifier, const="--verify-argv")
    vf_parser.add_argument("--verify-shell", dest="verifiers", action=OrderedVerifier, const="--verify-shell")
    vf_parser.add_argument("--verify", dest="verifiers", action=OrderedVerifier, const="--verify")
    vf_parser.add_argument("--legacy-shell-verification", action="store_true")
    vf_parser.add_argument("--acknowledge-verifier-network", action="store_true")
    vf_parser.add_argument("--acknowledge-verifier-credential-access", action="store_true")
    vf_parser.add_argument("--verify-env", action="append", default=[])
    vf_parser.add_argument("--verify-credential-env", action="append", default=[])
    vf_parser.add_argument("--selection")
    vf_parser.add_argument("--pre-recommendation")
    vf_parser.add_argument("--assurance", required=True, choices=("verified", "partially_verified", "rejected", "blocked"))
    approval_group = vf_parser.add_mutually_exclusive_group()
    approval_group.add_argument(
        "--approve-dispatch-sha",
        help="Exact dispatch-state SHA copied from workflow status before verification.",
    )
    approval_group.add_argument(
        "--approve-state-sha",
        help="Deprecated compatibility alias for --approve-dispatch-sha.",
    )
    vf_parser.add_argument("--verification-json")
    vf_parser.add_argument("--format", choices=("json", "text"), default="json")

    return parser


def _dispatch_run(
    args: argparse.Namespace, *, worktree: Path, dispatch_job_dir: Path,
) -> int:
    runtime = SCRIPTS.parent
    cmd = [
        str(runtime / "agy-worker.sh"),
        "--workdir", str(worktree),
        "--add-dir", str(worktree),
        "--workflow", args.workflow,
        "--mode", args.mode,
    ]
    if args.tier:
        cmd += ["--tier", args.tier]
    if args.model:
        cmd += ["--model", args.model]
    if args.effort:
        cmd += ["--effort", args.effort]
    if args.max_cycles:
        cmd += ["--max-cycles", str(args.max_cycles)]
    if args.idle_timeout:
        cmd += ["--idle-timeout", args.idle_timeout]
    if args.hard_timeout:
        cmd += ["--hard-timeout", args.hard_timeout]
    if args.max_runtime:
        cmd += ["--max-runtime", args.max_runtime]
    if args.notice_interval:
        cmd += ["--notice-interval", args.notice_interval]
    for env_opt in args.provider_env:
        cmd += ["--provider-env", env_opt]

    env = dict(os.environ)
    env["AGY_WORKER_JOB_ID"] = args.job_id
    env["AGY_WORKER_LOG_DIR"] = str(dispatch_job_dir.parent)
    task_input = args.task.encode("utf-8") if args.task else b""
    if not task_input and not sys.stdin.isatty():
        task_input = sys.stdin.buffer.read()
    proc = subprocess.run(
        cmd,
        input=task_input if task_input else None,
        cwd=str(worktree),
        env=env,
        check=False,
    )
    return proc.returncode


def _explicit_run(args: argparse.Namespace, repo: Path) -> int:
    if not all((args.state, args.worktree, args.branch, args.base)):
        raise WorkflowError(
            "advanced mode requires --state, --worktree, --branch, and --base together"
        )
    state_path = Path(args.state)
    worktree = real_absolute(Path(args.worktree), "worktree")
    if contains(repo, worktree) or contains(worktree, repo):
        raise WorkflowError("worktree must be outside the repository")
    if contains(repo, state_path) or contains(worktree, state_path):
        raise WorkflowError("state must be outside repository and worktree")
    validate_base_commit(repo, args.base)
    validate_worktree_registration(repo, worktree)
    validate_branch_backed_worktree(worktree, args.branch)

    store = WorkflowStateStore(state_path, initial=not state_path.exists())
    created_state_sha: str | None = None
    created_state_identity: dict[str, int] | None = None
    try:
        preview_raw, preview_data = canonical_transmission_preview(worktree)
        manifest_sha = preview_data["manifest_sha256"]
        if args.preview:
            sys.stdout.buffer.write(preview_raw)
            return 0
        if not args.approve_preview_sha:
            sys.stdout.buffer.write(preview_raw)
            sys.stderr.write(
                f"workflow: provider-transmission approval required. Re-run with --approve-preview-sha {manifest_sha}\n"
            )
            return 20
        if args.approve_preview_sha != manifest_sha:
            raise WorkflowError("transmission preview approval is stale or mismatched")
        if store.value is not None:
            raise WorkflowError(
                "workflow state already exists; use status or the advanced recovery commands"
            )
        if args.job_dir:
            dispatch_job_dir = real_absolute(
                Path(args.job_dir), "dispatch job directory", must_exist=False
            )
        else:
            log_root = Path(
                os.environ.get("AGY_WORKER_LOG_DIR") or (state_path.parent / "logs")
            )
            dispatch_job_dir = real_absolute(
                log_root / args.job_id, "dispatch job directory", must_exist=False
            )
        created_state_sha = store.create(
            {
                "schema_version": SCHEMA_VERSION,
                "kind": KIND_WORKFLOW_STATE,
                "job_id": args.job_id,
                "repo_path": str(repo),
                "repo_identity": identity(repo.lstat()),
                "worktree_path": str(worktree),
                "worktree_identity": identity(worktree.lstat()),
                "branch": args.branch,
                "branch_ref": f"refs/heads/{args.branch}",
                "base": args.base,
                "preview_manifest_sha256": manifest_sha,
                "dispatch_job_dir": str(dispatch_job_dir),
                "job_state_path": args.job_state,
                "receipt_path": None,
            }
        )
        assert store.metadata is not None
        created_state_identity = identity(store.metadata)
    finally:
        store.close()

    result = _dispatch_run(args, worktree=worktree, dispatch_job_dir=dispatch_job_dir)
    if (
        result != 0 and created_state_sha is not None
        and created_state_identity is not None
        and not dispatch_job_dir.exists() and not dispatch_job_dir.is_symlink()
    ):
        rollback_store = WorkflowStateStore(state_path, initial=False)
        try:
            if dispatch_job_dir.exists() or dispatch_job_dir.is_symlink():
                raise WorkflowError("dispatch artifacts appeared before pre-dispatch rollback")
            rollback_store.discard_exact(created_state_sha, created_state_identity)
        finally:
            rollback_store.close()
    return result


def _ordinary_run(args: argparse.Namespace, repo: Path) -> int:
    if args.job_dir or args.job_state:
        raise WorkflowError("--job-dir and --job-state require advanced mode")
    derived = _derived_bindings(repo, args.job_id)
    state_path = Path(derived["state"])
    job_state_path = Path(derived["job_state"])
    worktree = Path(derived["worktree"])
    branch = str(derived["branch"])
    dispatch_job_dir = Path(derived["dispatch_job_dir"])
    if args.base:
        base = args.base
    elif state_path.exists() and not state_path.is_symlink():
        existing_data, _metadata = read_regular(
            state_path, MAX_STATE_BYTES, "workflow state", private=True
        )
        existing = validate_workflow_state(
            parse_strict(existing_data, "workflow state")
        )
        base = existing["base"]
    elif job_state_path.exists() and not job_state_path.is_symlink():
        existing_job, _job_sha = _job_state_snapshot(job_state_path)
        existing_base = existing_job.get("base")
        if not isinstance(existing_base, str):
            raise WorkflowError("facade job state base is invalid")
        base = existing_base
    else:
        base = _git_head(repo)
    validate_base_commit(repo, base)
    if contains(repo, worktree) or contains(worktree, repo):
        raise WorkflowError("derived worktree must be outside the repository")
    if contains(repo, state_path) or contains(worktree, state_path):
        raise WorkflowError("derived state must be outside repository and worktree")

    initialized_here = False
    if not job_state_path.exists() and not job_state_path.is_symlink():
        if state_path.exists() or state_path.is_symlink():
            raise WorkflowError("workflow state exists without its lifecycle state")
        if worktree.exists() or worktree.is_symlink():
            raise WorkflowError("derived worktree path already exists")
        init = _run_lifecycle(
            "init", "--facade-created", "--state", str(job_state_path),
            "--repo", str(repo), "--worktree", str(worktree),
            "--branch", branch, "--base", base, "--job-id", args.job_id,
            "--dispatch-job-dir", str(dispatch_job_dir),
        )
        if init.returncode != 0:
            raise WorkflowError("facade lifecycle initialization failed")
        initialized_here = True
    job_value, job_sha = _job_state_snapshot(job_state_path)
    _validate_facade_job_state(
        job_value, repo=repo, worktree=worktree, branch=branch,
        base=base, job_id=args.job_id,
    )
    validate_worktree_registration(repo, worktree)
    validate_branch_backed_worktree(worktree, branch)

    store = WorkflowStateStore(state_path, initial=not state_path.exists())
    state_sha: str | None = None
    state_identity: dict[str, int] | None = None
    try:
        try:
            preview_raw, preview_data = canonical_transmission_preview(worktree)
        except BaseException:
            if initialized_here:
                _rollback_facade_ready(
                    state_path=job_state_path, workflow_state_path=None,
                    workflow_sha=None, workflow_identity=None,
                    repo=repo, worktree=worktree, branch=branch, base=base,
                    job_id=args.job_id, dispatch_job_dir=dispatch_job_dir,
                )
            raise
        manifest_sha = preview_data["manifest_sha256"]
        if store.value is None:
            state_sha = store.create(
                {
                    "schema_version": FACADE_SCHEMA_VERSION,
                    "kind": KIND_WORKFLOW_STATE,
                    "origin": FACADE_ORIGIN,
                    "job_id": args.job_id,
                    "repo_path": str(repo),
                    "repo_identity": identity(repo.lstat()),
                    "worktree_path": str(worktree),
                    "worktree_identity": identity(worktree.lstat()),
                    "branch": branch,
                    "branch_ref": f"refs/heads/{branch}",
                    "base": base,
                    "preview_manifest_sha256": manifest_sha,
                    "dispatch_job_dir": str(dispatch_job_dir),
                    "job_state_path": str(job_state_path),
                    "job_state_sha256": job_sha,
                    "receipt_path": None,
                }
            )
        else:
            state = store.value
            expected = {
                "schema_version": FACADE_SCHEMA_VERSION,
                "origin": FACADE_ORIGIN,
                "job_id": args.job_id,
                "repo_path": str(repo),
                "repo_identity": identity(repo.lstat()),
                "worktree_path": str(worktree),
                "worktree_identity": identity(worktree.lstat()),
                "branch": branch,
                "base": base,
                "dispatch_job_dir": str(dispatch_job_dir),
                "job_state_path": str(job_state_path),
                "job_state_sha256": job_sha,
                "preview_manifest_sha256": manifest_sha,
            }
            if any(state.get(key) != value for key, value in expected.items()):
                raise WorkflowError("facade workflow binding or preview changed")
            state_sha = store.sha256
        assert store.metadata is not None and state_sha is not None
        state_identity = identity(store.metadata)

        if args.preview:
            sys.stdout.buffer.write(preview_raw)
            return 0
        if not args.approve_preview_sha:
            sys.stdout.buffer.write(preview_raw)
            sys.stderr.write(
                f"workflow: provider-transmission approval required. Re-run with --approve-preview-sha {manifest_sha}\n"
            )
            return 20
        if args.approve_preview_sha != manifest_sha:
            raise WorkflowError("transmission preview approval is stale or mismatched")
    finally:
        store.close()

    result = _dispatch_run(args, worktree=worktree, dispatch_job_dir=dispatch_job_dir)
    if (
        result != 0 and initialized_here
        and not dispatch_job_dir.exists() and not dispatch_job_dir.is_symlink()
    ):
        _rollback_facade_ready(
            state_path=job_state_path, workflow_state_path=state_path,
            workflow_sha=state_sha, workflow_identity=state_identity,
            repo=repo, worktree=worktree, branch=branch, base=base,
            job_id=args.job_id, dispatch_job_dir=dispatch_job_dir,
        )
    return result


def command_run(args: argparse.Namespace) -> int:
    repo = real_absolute(Path(args.repo), "repository")
    explicit = any((args.state, args.worktree, args.branch))
    if explicit:
        return _explicit_run(args, repo)
    return _ordinary_run(args, repo)


def _workflow_status(args: argparse.Namespace) -> int:
    state_path = Path(args.state)
    store = WorkflowStateStore(state_path, initial=False)
    try:
        state = store.value
        assert state is not None
        job_id = state["job_id"]
        repo_path = state["repo_path"]
        worktree_path = state["worktree_path"]
        branch = state["branch"]
        base = state["base"]
        manifest_sha = state["preview_manifest_sha256"]

        dispatch_facts: dict[str, Any] | None = None
        # Check if dispatch state exists
        if state.get("dispatch_job_dir"):
            dispatch_dir = Path(state["dispatch_job_dir"])
            dispatch_state_file = dispatch_dir / "dispatch-state.json"
            if dispatch_state_file.exists():
                try:
                    d_data, _ = read_regular(dispatch_state_file, MAX_STATE_BYTES, "dispatch state", private=True)
                    d_val = parse_strict(d_data, "dispatch state")
                    dispatch_facts = {
                        "state_sha256": sha256_bytes(d_data),
                        "job_id": d_val.get("job_id"),
                        "phase": d_val.get("phase"),
                        "controller_phase": d_val.get("controller_phase"),
                        "available_actions": d_val.get("available_actions", []),
                        "status": d_val.get("status"),
                        "reason": d_val.get("reason"),
                        "exit_code": d_val.get("exit_code"),
                        "candidate_state_sha256": d_val.get("candidate_state_sha256"),
                        "candidate_recognized": d_val.get("candidate_recognized"),
                        "result_available": d_val.get("result_available"),
                        "failure_stage": d_val.get("failure_stage"),
                        "provider_terminal_status": d_val.get("provider_terminal_status"),
                        "assurance": d_val.get("assurance"),
                        "driver_disposition": d_val.get("driver_disposition"),
                        "next_action": d_val.get("next_action"),
                    }
                except Exception:
                    dispatch_facts = None

        verification_facts: dict[str, Any] | None = None
        if state.get("receipt_path"):
            receipt_file = Path(state["receipt_path"])
            if receipt_file.exists():
                try:
                    r_data, _ = read_regular(receipt_file, MAX_RECEIPT_BYTES, "receipt", private=True)
                    r_val = parse_strict(r_data, "receipt")
                    verification_facts = {
                        "path": str(receipt_file),
                        "sha256": sha256_bytes(r_data),
                        "verdict": r_val.get("verdict"),
                        "gate_exit": r_val.get("gate_exit"),
                        "final_candidate_state_sha256": r_val.get("final_candidate_state_sha256"),
                    }
                except Exception:
                    verification_facts = None

        status_result = {
            "schema_version": SCHEMA_VERSION,
            "kind": KIND_WORKFLOW_STATUS,
            "source_kind": "workflow_facade",
            "job_id": job_id,
            "repo_path": repo_path,
            "worktree_path": worktree_path,
            "branch": branch,
            "base": base,
            "preview_manifest_sha256": manifest_sha,
            "dispatch_job_dir": state.get("dispatch_job_dir"),
            "dispatch": dispatch_facts,
            "verification": verification_facts,
            "phase": dispatch_facts.get("phase") if dispatch_facts else "ready",
            "controller_phase": (
                dispatch_facts.get("controller_phase") if dispatch_facts else None
            ),
            "available_actions": (
                dispatch_facts.get("available_actions", []) if dispatch_facts else []
            ),
            "advanced_recovery": (
                "Use workflow verify-finalize for driver-owned verification; "
                "use job.sh or agy-worker.sh directly only for advanced recovery."
            ),
        }

        if args.format == "json":
            sys.stdout.buffer.write(canonical_json(status_result) + b"\n")
        else:
            line1 = f"workflow: job={job_id} branch={branch} base={base[:12]}"
            disp = dispatch_facts.get("status", "none") if dispatch_facts else "none"
            phase = dispatch_facts.get("phase", "none") if dispatch_facts else "none"
            cand = dispatch_facts.get("candidate_state_sha256", "none") if dispatch_facts else "none"
            dispatch_sha = dispatch_facts.get("state_sha256", "none") if dispatch_facts else "none"
            line2 = f"dispatch: status={disp} phase={phase} state={dispatch_sha[:12] if dispatch_sha != 'none' else 'none'} candidate={cand[:12] if cand != 'none' else 'none'}"
            verdict = verification_facts.get("verdict", "unverified") if verification_facts else "unverified"
            assurance = dispatch_facts.get("assurance") if dispatch_facts else "none"
            line3 = f"verification: verdict={verdict} assurance={assurance or 'none'}"
            sys.stdout.write(f"{line1}\n{line2}\n{line3}\n")
        return 0
    finally:
        store.close()


def _low_level_status(args: argparse.Namespace, state_path: Path) -> int:
    data, _metadata = read_regular(state_path, MAX_STATE_BYTES, "job state", private=True)
    value = parse_strict(data, "job state")
    if not isinstance(value, dict) or value.get("kind") != KIND_JOB_STATE:
        raise WorkflowError("job state contract is invalid")
    proc = _run_lifecycle("status", "--state", str(state_path))
    if proc.returncode != 0:
        raise WorkflowError("job lifecycle status unavailable")
    facts = parse_strict(proc.stdout, "job lifecycle status")
    if not isinstance(facts, dict):
        raise WorkflowError("job lifecycle status contract is invalid")
    phase = facts.get("phase")
    actions = ["status"]
    if phase == "ready":
        actions.append("verify")
    elif phase == "verified-gate-passed":
        actions.append("preserve-instructions")
    elif phase == "verified-rejected":
        actions.append("cleanup")
    elif phase == "dispatch-failed":
        actions.append("abort")
    result = {
        "schema_version": SCHEMA_VERSION,
        "kind": KIND_WORKFLOW_STATUS,
        "source_kind": "job_lifecycle",
        "job_id": facts.get("job_id"),
        "phase": phase,
        "controller_phase": phase,
        "available_actions": actions,
        "state_sha256": facts.get("state_sha256"),
        "advanced_recovery": (
            "This is an existing low-level lifecycle state. Mutations remain with job.sh."
        ),
    }
    if args.format == "json":
        sys.stdout.buffer.write(canonical_json(result) + b"\n")
    else:
        sys.stdout.write(
            f"source: job_lifecycle job={result['job_id']}\n"
            f"phase: {phase}\n"
            f"advanced-recovery: actions={','.join(actions)} via job.sh\n"
        )
    return 0


def _dispatcher_status(
    args: argparse.Namespace, *, job_id: str, state_path: Path | None = None,
) -> int:
    if state_path is not None:
        if state_path.name != DISPATCH.STATE_NAME or state_path.parent.name != job_id:
            raise WorkflowError("dispatch state path is not canonically job-bound")
        job = DISPATCH.canonical_job(state_path.parent)
    else:
        log_root = Path(
            os.environ.get("AGY_WORKER_LOG_DIR") or (SCRIPTS.parent / "logs")
        )
        log_root = _owner_directory(log_root, "dispatch log root", private=True)
        job = DISPATCH.canonical_job(log_root / job_id)
    try:
        value, raw, state_sha = DISPATCH.load_state(job)
        if value.get("job_id") != job_id:
            raise WorkflowError("dispatch state job binding is invalid")
        facts = DISPATCH.public_status(value, state_sha, job=job)
        _after, after_raw, after_sha = DISPATCH.load_state(job)
    except (OSError, DISPATCH.DispatchError) as exc:
        raise WorkflowError("dispatcher status unavailable") from exc
    if raw != after_raw or state_sha != after_sha:
        raise WorkflowError("dispatch state changed during read-only projection")
    if not isinstance(facts, dict) or facts.get("job_id") != job_id:
        raise WorkflowError("dispatcher status contract is invalid")
    result = {
        "schema_version": SCHEMA_VERSION,
        "kind": KIND_WORKFLOW_STATUS,
        "source_kind": "dispatcher",
        "job_id": job_id,
        "phase": facts.get("phase"),
        "controller_phase": facts.get("controller_phase"),
        "available_actions": facts.get("available_actions", []),
        "state_sha256": facts.get("state_sha256"),
        "advanced_recovery": (
            "This is an existing dispatcher job. Mutations remain with agy-worker.sh."
        ),
    }
    if args.format == "json":
        sys.stdout.buffer.write(canonical_json(result) + b"\n")
    else:
        action_names = [
            item.get("action", "unknown") if isinstance(item, dict) else str(item)
            for item in result["available_actions"]
        ]
        sys.stdout.write(
            f"source: dispatcher job={job_id}\n"
            f"phase: {result['controller_phase'] or result['phase']}\n"
            f"advanced-recovery: actions={','.join(action_names)} via agy-worker.sh\n"
        )
    return 0


def command_status(args: argparse.Namespace) -> int:
    if args.job_state:
        return _low_level_status(args, real_absolute(Path(args.job_state), "job state"))
    if args.dispatch_state:
        state_path = real_absolute(Path(args.dispatch_state), "dispatch state")
        data, _metadata = read_regular(
            state_path, MAX_STATE_BYTES, "dispatch state", private=True
        )
        value = parse_strict(data, "dispatch state")
        job_id = value.get("job_id") if isinstance(value, dict) else None
        if not isinstance(job_id, str) or JOB_RE.fullmatch(job_id) is None:
            raise WorkflowError("dispatch state job ID is invalid")
        return _dispatcher_status(args, job_id=job_id, state_path=state_path)
    if args.dispatcher_job_id:
        if JOB_RE.fullmatch(args.dispatcher_job_id) is None:
            raise WorkflowError("dispatcher job ID is invalid")
        return _dispatcher_status(args, job_id=args.dispatcher_job_id)

    state_path = real_absolute(Path(args.state), "state")
    data, _metadata = read_regular(state_path, MAX_STATE_BYTES, "state", private=True)
    value = parse_strict(data, "state")
    if not isinstance(value, dict):
        raise WorkflowError("state contract is invalid")
    if value.get("kind") == KIND_JOB_STATE:
        return _low_level_status(args, state_path)
    if value.get("kind") != KIND_WORKFLOW_STATE:
        raise WorkflowError("state kind is unsupported")
    return _workflow_status(args)


def command_verify_finalize(args: argparse.Namespace) -> int:
    state_path = Path(args.state)
    store = WorkflowStateStore(state_path, initial=False)
    try:
        state = store.value
        assert state is not None
        worktree = real_absolute(Path(state["worktree_path"]), "worktree")
        repo = real_absolute(Path(state["repo_path"]), "repository")

        if not same_identity(repo.lstat(), state["repo_identity"]):
            raise WorkflowError("repository identity changed since workflow run")
        if not same_identity(worktree.lstat(), state["worktree_identity"]):
            raise WorkflowError("worktree identity changed since workflow run")
        validate_worktree_registration(repo, worktree)
        validate_branch_backed_worktree(worktree, state["branch"])
        validate_base_commit(repo, state["base"])

        if args.base and args.base != state["base"]:
            raise WorkflowError("base commit mismatch with workflow state")

        try:
            initial_candidate = candidate_state_digest(worktree, state["base"])
        except (CandidateStateError, OSError, ValueError) as exc:
            raise WorkflowError("candidate state is unavailable") from exc
        if args.candidate_sha:
            if SHA_RE.fullmatch(args.candidate_sha) is None:
                raise WorkflowError("candidate state SHA is invalid")
            if args.candidate_sha != initial_candidate:
                raise WorkflowError("candidate state SHA mismatch")

        dispatch_dir: Path | None = None
        dispatch_state_file: Path | None = None
        verification_payload: dict[str, Any] | None = None
        dispatch_approve_sha: str | None = None
        if state.get("dispatch_job_dir"):
            dispatch_dir = Path(state["dispatch_job_dir"])
            possible_dispatch_state = dispatch_dir / "dispatch-state.json"
            if possible_dispatch_state.exists():
                dispatch_state_file = possible_dispatch_state
                dispatch_approve_sha = (
                    args.approve_dispatch_sha or args.approve_state_sha
                )
                if dispatch_approve_sha is None:
                    raise WorkflowError(
                        "--approve-dispatch-sha from workflow status is required "
                        "to finalize a dispatch"
                    )
                if SHA_RE.fullmatch(dispatch_approve_sha) is None:
                    raise WorkflowError("dispatch state approval SHA is invalid")
                initial_dispatch_data, _ = read_regular(
                    dispatch_state_file,
                    MAX_STATE_BYTES,
                    "dispatch state",
                    private=True,
                )
                if sha256_bytes(initial_dispatch_data) != dispatch_approve_sha:
                    raise WorkflowError("dispatch state approval is stale or mismatched")
                if not args.verification_json:
                    raise WorkflowError(
                        "driver-authored --verification-json is required to finalize a dispatch"
                    )
                verification_path = real_absolute(
                    Path(args.verification_json), "verification json"
                )
                verification_data, _ = read_regular(
                    verification_path,
                    MAX_STATE_BYTES,
                    "verification json",
                    private=True,
                )
                parsed_verification = parse_strict(
                    verification_data, "verification json"
                )
                if not isinstance(parsed_verification, dict):
                    raise WorkflowError("verification json must be one object")
                verification_payload = parsed_verification
        elif args.verification_json:
            raise WorkflowError("verification json requires a bound dispatch state")

        receipt_path = real_absolute(Path(args.receipt), "receipt", must_exist=False)
        if receipt_path.exists() or receipt_path.is_symlink():
            raise WorkflowError("receipt path already exists")

        envelope_path = real_absolute(Path(args.envelope), "envelope")

        if not args.verifiers:
            raise WorkflowError("at least one verifier is required")

        # Check shell verifier acknowledgements
        for kind, _val in args.verifiers:
            if kind == "--verify-shell":
                if not (args.acknowledge_verifier_network and args.acknowledge_verifier_credential_access):
                    raise WorkflowError("--verify-shell requires network and credential access acknowledgements")
            elif kind == "--verify":
                if not (args.legacy_shell_verification and args.acknowledge_verifier_network and args.acknowledge_verifier_credential_access):
                    raise WorkflowError("--verify requires legacy shell verification and acknowledgements")

        runtime = SCRIPTS.parent
        verify_cmd = [
            str(runtime / "verify-job.sh"),
            "--receipt", str(receipt_path),
            "--envelope", str(envelope_path),
            "--repo", str(worktree),
            "--base", state["base"],
        ]
        for val in args.allow:
            verify_cmd += ["--allow", val]
        for val in args.only:
            verify_cmd += ["--only", val]
        if args.expect_edits:
            verify_cmd.append("--expect-edits")
        for flag, val in args.verifiers:
            verify_cmd += [flag, val]
        if args.legacy_shell_verification:
            verify_cmd.append("--legacy-shell-verification")
        if args.acknowledge_verifier_network:
            verify_cmd.append("--acknowledge-verifier-network")
        if args.acknowledge_verifier_credential_access:
            verify_cmd.append("--acknowledge-verifier-credential-access")
        for val in args.verify_env:
            verify_cmd += ["--verify-env", val]
        for val in args.verify_credential_env:
            verify_cmd += ["--verify-credential-env", val]
        if args.selection:
            verify_cmd += ["--selection", args.selection]
        if args.pre_recommendation:
            verify_cmd += ["--pre-recommendation", args.pre_recommendation]

        proc = subprocess.run(verify_cmd, check=False)
        rc = proc.returncode

        if rc in {0, 10, 11, 12, 13, 14, 15}:
            if not receipt_path.exists():
                raise WorkflowError("verification completed without creating receipt")
            r_data, _ = read_regular(receipt_path, MAX_RECEIPT_BYTES, "receipt", private=True)
            receipt_json = parse_strict(r_data, "receipt")
            try:
                current_cand = candidate_state_digest(worktree, state["base"])
            except (CandidateStateError, OSError, ValueError) as exc:
                raise WorkflowError("candidate state is unavailable") from exc
            if current_cand != initial_candidate:
                raise WorkflowError("candidate state changed during verification")
            if receipt_json.get("final_candidate_state_sha256") != current_cand:
                raise WorkflowError("receipt does not bind current candidate state")

            # The receipt is useful bounded evidence even when later controller
            # finalization rejects a stale approval or another binding.
            store.update({"receipt_path": str(receipt_path)})

            # Rejected/routed gate outcomes remain useful bounded receipts, but
            # they can never authorize a lifecycle assurance transition.
            if rc != 0:
                return rc

            # Delegate to existing finalize authority if dispatch job directory is present
            if dispatch_dir is not None and dispatch_state_file is not None:
                d_data, _ = read_regular(
                    dispatch_state_file,
                    MAX_STATE_BYTES,
                    "dispatch state",
                    private=True,
                )
                d_sha = sha256_bytes(d_data)
                assert dispatch_approve_sha is not None
                if d_sha != dispatch_approve_sha:
                    raise WorkflowError("dispatch state changed during verification")
                assert verification_payload is not None

                fin_proc = subprocess.run(
                    [
                        str(runtime / "agy-worker.sh"),
                        "finalize",
                        "--job-dir", str(dispatch_dir),
                        "--approve-state-sha", dispatch_approve_sha,
                        "--assurance", args.assurance,
                        "--format", args.format,
                    ],
                    input=canonical_json(verification_payload),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                )
                sys.stdout.buffer.write(fin_proc.stdout)
                sys.stderr.buffer.write(fin_proc.stderr)
                if fin_proc.returncode != 0:
                    return fin_proc.returncode
        else:
            if receipt_path.exists() or receipt_path.is_symlink():
                raise WorkflowError("failed verification left an unbound receipt")

        return rc
    finally:
        store.close()


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "run":
            return command_run(args)
        elif args.command == "status":
            return command_status(args)
        elif args.command == "verify-finalize":
            return command_verify_finalize(args)
        else:
            sys.stderr.write(f"workflow: unknown command {args.command}\n")
            return 64
    except WorkflowError as exc:
        sys.stderr.write(f"workflow error: {exc}\n")
        return 20
    except Exception as exc:
        sys.stderr.write(f"workflow fatal error: {exc}\n")
        return 70


if __name__ == "__main__":
    raise SystemExit(main())
