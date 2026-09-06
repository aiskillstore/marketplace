#!/usr/bin/env python3
"""Fail-closed process-owning CLI for one explicit branch-backed worker job.

Run through job.sh. Importing or embedding main() in a host process is unsupported:
the command retains lifecycle signal handlers through flush and atomic process exit.
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
import secrets
import selectors
import shlex
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
import time
from typing import Any, Iterator

sys.dont_write_bytecode = True
SCRIPTS = Path(__file__).resolve(strict=True).parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from candidate_state import (  # noqa: E402
    CandidateStateError,
    candidate_state_digest,
)
from evidence_receipt import (  # noqa: E402
    ValidationFailure,
    load_schema,
    parse_json_bytes,
    validate_receipt,
)
from agy_dispatch import (  # noqa: E402
    DispatchError,
    LOCK_NAME as DISPATCH_LOCK_NAME,
    MAX_STATE_BYTES as MAX_DISPATCH_STATE_BYTES,
    canonical as dispatch_canonical_bytes,
    canonical_job as canonical_dispatch_job,
    parse_json as parse_dispatch_json,
    read_regular as read_dispatch_regular,
    validate_state as validate_dispatch_state,
)


SIGNALS = (signal.SIGHUP, signal.SIGINT, signal.SIGTERM)
JOB_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,79}")
SHA_RE = re.compile(r"[0-9a-f]{64}")
COMMIT_RE = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})")
STATE_FIELDS = {
    "schema_version", "kind", "sequence", "previous_state_sha256", "phase",
    "job_id", "repo_path", "repo_identity", "git_common_dir",
    "git_common_identity", "worktree_path", "worktree_parent_device",
    "worktree_identity", "branch", "branch_ref", "base", "receipt",
    "dispatch", "cleanup_step", "last_result", "failure",
}
LEGACY_STATE_FIELDS = STATE_FIELDS - {"dispatch"}
FACADE_STATE_FIELDS = STATE_FIELDS | {"origin", "dispatch_job_dir"}
FACADE_ORIGIN = "workflow-facade"
PHASES = {
    "initializing", "ready", "init-failed", "init-interrupted", "verifying",
    "verify-failed", "verify-interrupted", "verified-gate-passed",
    "verified-rejected", "verified-routed", "dispatch-failed",
    "cleanup-in-progress", "cleaned", "abort-in-progress", "aborted",
}
CLEANUP_STEPS = {"none", "worktree-removed", "branch-removed"}
RECEIPT_FIELDS = {
    "path", "sha256", "gate_exit", "verdict", "final_candidate_state_sha256"
}
DISPATCH_FIELDS = {
    "path", "sha256", "state_identity", "job_identity", "lock_identity",
    "status", "reason", "exit_code", "candidate_state_sha256",
}
MAX_STATE_BYTES = 128 * 1024
MAX_RECEIPT_BYTES = 1024 * 1024
MAX_DELETE_NODES = 100_000
MAX_GIT_OUTPUT = 32 * 1024 * 1024
MAX_ATTRIBUTE_PATH_BYTES = 16 * 1024 * 1024
GIT_TIMEOUT_SECONDS = 30.0
GIT_EXECUTABLE = "/usr/bin/git"
EMPTY_CANDIDATE_STATE_SHA256 = hashlib.sha256(b"\0" * 8).hexdigest()
UNSAFE_GIT_CONFIG_RE = re.compile(
    rb"^(?:filter\..*\.(?:clean|smudge|process|required)|core\.(?:fsmonitor|hooksPath|pager)"
    rb"|diff\.external|interactive\.diffFilter|pager\..*|include(?:If)?\..*)$",
    re.IGNORECASE,
)


class JobError(ValueError):
    pass


class GitError(OSError):
    pass


class GitOutputLimitError(GitError):
    pass


class JobSignal(BaseException):
    def __init__(self, number: int) -> None:
        self.number = number


class GitResult:
    def __init__(self, returncode: int, stdout: bytes) -> None:
        self.returncode = returncode
        self.stdout = stdout


class Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        del message
        self.print_usage(sys.stderr)
        self.exit(64, "job: invalid arguments\n")


class Once(argparse.Action):
    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: Any,
        option_string: str | None = None,
    ) -> None:
        if getattr(namespace, self.dest, None) is not None:
            parser.error(f"{option_string} must be supplied once")
        setattr(namespace, self.dest, values)


class OnceTrue(argparse.Action):
    def __init__(self, option_strings: list[str], dest: str, **kwargs: Any) -> None:
        super().__init__(option_strings, dest, nargs=0, default=None, **kwargs)

    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: Any,
        option_string: str | None = None,
    ) -> None:
        del values
        if getattr(namespace, self.dest, None) is not None:
            parser.error(f"{option_string} must be supplied once")
        setattr(namespace, self.dest, True)


class OrderedVerifier(argparse.Action):
    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: Any,
        option_string: str | None = None,
    ) -> None:
        del parser, option_string
        current = getattr(namespace, self.dest, None)
        if current is None:
            current = []
            setattr(namespace, self.dest, current)
        current.append((self.const, values))


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=True, sort_keys=True, separators=(",", ":")
    ).encode("ascii") + b"\n"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def identity(metadata: os.stat_result) -> dict[str, int]:
    return {
        "dev": metadata.st_dev,
        "ino": metadata.st_ino,
        "mode": stat.S_IMODE(metadata.st_mode),
        "uid": metadata.st_uid,
    }


def validate_identity(value: Any, label: str) -> dict[str, int]:
    if not isinstance(value, dict) or set(value) != {"dev", "ino", "mode", "uid"}:
        raise JobError(f"{label} identity is invalid")
    if any(type(value[key]) is not int or value[key] < 0 for key in value):
        raise JobError(f"{label} identity is invalid")
    return value


def same_identity(metadata: os.stat_result, expected: dict[str, int]) -> bool:
    return identity(metadata) == expected


def real_absolute(path: Path, label: str, *, must_exist: bool = True) -> Path:
    if not path.is_absolute() or "\n" in str(path) or "\r" in str(path):
        raise JobError(f"{label} must be one canonical absolute path")
    canonical = Path(os.path.realpath(path))
    if canonical != path:
        raise JobError(f"{label} must be one canonical absolute path")
    if must_exist and not path.exists():
        raise JobError(f"{label} is unavailable")
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
        raise JobError("state parent must be one real owner-private mode-0700 directory")
    descriptor = os.open(
        parent,
        os.O_RDONLY
        | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_NOFOLLOW", 0),
    )
    opened = os.fstat(descriptor)
    if not same_identity(opened, identity(metadata)):
        os.close(descriptor)
        raise JobError("state parent identity changed while opened")
    return parent, descriptor


def _read_fd(descriptor: int, maximum: int) -> bytes:
    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = os.read(descriptor, min(65536, maximum + 1 - total))
        if not chunk:
            break
        chunks.append(chunk)
        total += len(chunk)
        if total > maximum:
            raise JobError("local artifact is oversized")
    return b"".join(chunks)


def read_regular(path: Path, maximum: int, label: str, *, private: bool) -> tuple[bytes, os.stat_result]:
    try:
        descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    except OSError as exc:
        raise JobError(f"{label} is unavailable") from exc
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode):
            raise JobError(f"{label} must be one real file")
        if private and (
            metadata.st_uid != os.getuid() or stat.S_IMODE(metadata.st_mode) != 0o600
        ):
            raise JobError(f"{label} must be owner-private mode 0600")
        data = _read_fd(descriptor, maximum)
        if len(data) != metadata.st_size:
            raise JobError(f"{label} changed while read")
        return data, metadata
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
        raise JobError(f"{label} is unavailable") from exc
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode):
            raise JobError(f"{label} must be one real file")
        if private and (
            metadata.st_uid != os.getuid() or stat.S_IMODE(metadata.st_mode) != 0o600
        ):
            raise JobError(f"{label} must be owner-private mode 0600")
        data = _read_fd(descriptor, maximum)
        if len(data) != metadata.st_size:
            raise JobError(f"{label} changed while read")
        return data, metadata
    finally:
        os.close(descriptor)


def parse_strict(data: bytes, label: str) -> Any:
    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise JobError(f"{label} has a duplicate key")
            result[key] = value
        return result

    try:
        return json.loads(data.decode("utf-8", "strict"), object_pairs_hook=pairs)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise JobError(f"{label} is invalid") from exc


def canonical_branch_syntax(branch: str) -> bool:
    forbidden = set(" ~^:?*[\\")
    if (
        not branch
        or branch.startswith("-")
        or branch == "@"
        or branch.startswith("/")
        or branch.endswith(("/", "."))
        or "//" in branch
        or ".." in branch
        or "@{" in branch
        or any(ord(character) < 32 or ord(character) == 127 for character in branch)
        or any(character in forbidden for character in branch)
    ):
        return False
    return all(
        component
        and not component.startswith(".")
        and not component.endswith(".lock")
        for component in branch.split("/")
    )


def validate_state(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise JobError("state fields are invalid")
    version = value.get("schema_version")
    fields = set(value)
    if version == 1:
        if fields != STATE_FIELDS and fields != LEGACY_STATE_FIELDS:
            raise JobError("state fields are invalid")
    elif version == 2:
        if fields != FACADE_STATE_FIELDS or value.get("origin") != FACADE_ORIGIN:
            raise JobError("state fields are invalid")
        dispatch_job_dir = value.get("dispatch_job_dir")
        if (
            not isinstance(dispatch_job_dir, str)
            or not Path(dispatch_job_dir).is_absolute()
            or os.path.normpath(dispatch_job_dir) != dispatch_job_dir
            or "\n" in dispatch_job_dir
            or "\r" in dispatch_job_dir
        ):
            raise JobError("state dispatch job directory is invalid")
    else:
        raise JobError("state version is invalid")
    if value["kind"] != "agy-worker-local-job-state":
        raise JobError("state version is invalid")
    if type(value["sequence"]) is not int or value["sequence"] < 1:
        raise JobError("state sequence is invalid")
    previous = value["previous_state_sha256"]
    if previous is not None and (not isinstance(previous, str) or SHA_RE.fullmatch(previous) is None):
        raise JobError("state history binding is invalid")
    if (value["sequence"] == 1) != (previous is None):
        raise JobError("state history binding is inconsistent")
    if value["phase"] not in PHASES or value["cleanup_step"] not in CLEANUP_STEPS:
        raise JobError("state phase is invalid")
    if not isinstance(value["job_id"], str) or JOB_RE.fullmatch(value["job_id"]) is None:
        raise JobError("state job ID is invalid")
    if not isinstance(value["base"], str) or COMMIT_RE.fullmatch(value["base"]) is None:
        raise JobError("state base is invalid")
    for key in ("repo_path", "git_common_dir", "worktree_path", "branch", "branch_ref"):
        if not isinstance(value[key], str) or not value[key] or "\x00" in value[key]:
            raise JobError("state path or ref is invalid")
    for key in ("repo_path", "git_common_dir", "worktree_path"):
        candidate = value[key]
        if (
            not Path(candidate).is_absolute()
            or os.path.normpath(candidate) != candidate
            or "\n" in candidate
            or "\r" in candidate
        ):
            raise JobError("state path is not canonical")
    if not canonical_branch_syntax(value["branch"]):
        raise JobError("state branch is invalid")
    if value["branch_ref"] != f"refs/heads/{value['branch']}":
        raise JobError("state branch binding is inconsistent")
    validate_identity(value["repo_identity"], "repository")
    validate_identity(value["git_common_identity"], "Git common directory")
    if type(value["worktree_parent_device"]) is not int or value["worktree_parent_device"] < 0:
        raise JobError("worktree parent device is invalid")
    if value["worktree_identity"] is not None:
        validate_identity(value["worktree_identity"], "worktree")
    if value["last_result"] is not None and type(value["last_result"]) is not int:
        raise JobError("state result is invalid")
    if value["failure"] is not None and (
        not isinstance(value["failure"], str)
        or value["failure"] not in {
            "init-failed", "interrupted", "verify-failed", "dispatch-failed",
            "cleanup-failed",
        }
    ):
        raise JobError("state failure is invalid")
    receipt = value["receipt"]
    if receipt is not None:
        if not isinstance(receipt, dict) or set(receipt) != RECEIPT_FIELDS:
            raise JobError("state receipt binding is invalid")
        if not isinstance(receipt["path"], str) or not Path(receipt["path"]).is_absolute():
            raise JobError("state receipt path is invalid")
        for key in ("sha256", "final_candidate_state_sha256"):
            if not isinstance(receipt[key], str) or SHA_RE.fullmatch(receipt[key]) is None:
                raise JobError("state receipt digest is invalid")
        if type(receipt["gate_exit"]) is not int or receipt["verdict"] not in {
            "gate-passed", "rejected", "routed"
        }:
            raise JobError("state receipt outcome is invalid")
        receipt_path = receipt["path"]
        if os.path.normpath(receipt_path) != receipt_path or "\n" in receipt_path or "\r" in receipt_path:
            raise JobError("state receipt path is not canonical")
        expected_verdict = (
            "gate-passed" if receipt["gate_exit"] == 0
            else "routed" if receipt["gate_exit"] == 15
            else "rejected" if receipt["gate_exit"] in {10, 11, 12, 13, 14}
            else None
        )
        if receipt["verdict"] != expected_verdict:
            raise JobError("state receipt outcome is inconsistent")
    dispatch = value.get("dispatch")
    if dispatch is not None:
        if not isinstance(dispatch, dict) or set(dispatch) != DISPATCH_FIELDS:
            raise JobError("state dispatch binding is invalid")
        path = dispatch["path"]
        if (
            not isinstance(path, str)
            or not Path(path).is_absolute()
            or os.path.normpath(path) != path
            or Path(path).name != "dispatch-state.json"
            or "\n" in path
            or "\r" in path
        ):
            raise JobError("state dispatch path is invalid")
        for key in ("sha256", "candidate_state_sha256"):
            if not isinstance(dispatch[key], str) or SHA_RE.fullmatch(dispatch[key]) is None:
                raise JobError("state dispatch digest is invalid")
        for key in ("state_identity", "job_identity", "lock_identity"):
            validate_identity(dispatch[key], f"dispatch {key}")
        if dispatch["status"] not in {"failed", "cancelled"}:
            raise JobError("state dispatch status is invalid")
        if not isinstance(dispatch["reason"], str) or not dispatch["reason"]:
            raise JobError("state dispatch reason is invalid")
        if type(dispatch["exit_code"]) is not int or dispatch["exit_code"] == 0:
            raise JobError("state dispatch result is invalid")

    phase = value["phase"]
    cleanup_step = value["cleanup_step"]
    worktree_identity = value["worktree_identity"]
    last_result = value["last_result"]
    failure = value["failure"]
    if receipt is not None and dispatch is not None:
        raise JobError("receipt and dispatch bindings are mutually exclusive")
    if phase == "initializing":
        consistent = worktree_identity is None and receipt is None and dispatch is None and cleanup_step == "none" and last_result is None and failure is None
    elif phase == "ready":
        consistent = worktree_identity is not None and receipt is None and dispatch is None and cleanup_step == "none" and last_result is None and failure is None
    elif phase in {"init-failed", "init-interrupted"}:
        consistent = receipt is None and dispatch is None and cleanup_step == "none" and isinstance(last_result, int) and failure in {"init-failed", "interrupted"}
    elif phase == "verifying":
        consistent = worktree_identity is not None and receipt is None and dispatch is None and cleanup_step == "none" and last_result is None and failure is None
    elif phase in {"verify-failed", "verify-interrupted"}:
        consistent = worktree_identity is not None and receipt is None and dispatch is None and cleanup_step == "none" and isinstance(last_result, int) and failure in {"verify-failed", "interrupted"}
    elif phase in {"verified-gate-passed", "verified-rejected", "verified-routed"}:
        expected = {
            "verified-gate-passed": "gate-passed",
            "verified-rejected": "rejected",
            "verified-routed": "routed",
        }[phase]
        consistent = (
            worktree_identity is not None
            and receipt is not None
            and dispatch is None
            and receipt["verdict"] == expected
            and cleanup_step == "none"
            and last_result == receipt["gate_exit"]
            and failure is None
        )
    elif phase == "dispatch-failed":
        consistent = (
            worktree_identity is not None
            and receipt is None
            and dispatch is not None
            and cleanup_step == "none"
            and last_result == dispatch["exit_code"]
            and failure == "dispatch-failed"
        )
    elif phase == "cleanup-in-progress":
        consistent = (
            worktree_identity is not None
            and receipt is not None
            and dispatch is None
            and receipt["verdict"] == "rejected"
            and cleanup_step in {"none", "worktree-removed"}
            and (
                (last_result is None and failure is None)
                or (isinstance(last_result, int) and failure in {"interrupted", "cleanup-failed"})
            )
        )
    elif phase == "cleaned":
        consistent = (
            worktree_identity is not None
            and receipt is not None
            and dispatch is None
            and receipt["verdict"] == "rejected"
            and cleanup_step == "branch-removed"
            and last_result == 0
            and failure is None
        )
    elif phase == "abort-in-progress":
        consistent = (
            worktree_identity is not None
            and receipt is None
            and dispatch is not None
            and cleanup_step in {"none", "worktree-removed"}
            and (
                (last_result is None and failure is None)
                or (isinstance(last_result, int) and failure in {"interrupted", "cleanup-failed"})
            )
        )
    else:  # aborted
        consistent = (
            worktree_identity is not None
            and receipt is None
            and dispatch is not None
            and cleanup_step == "branch-removed"
            and last_result == 0
            and failure is None
        )
    if not consistent:
        raise JobError("state phase fields are inconsistent")
    return value


class StateStore:
    def __init__(self, path: Path, *, initial: bool = False) -> None:
        self.path = real_absolute(path, "state", must_exist=not initial)
        self.parent, self.parent_fd = validate_private_parent(self.path.parent)
        self.parent_identity = identity(os.fstat(self.parent_fd))
        try:
            fcntl.flock(self.parent_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            os.close(self.parent_fd)
            self.parent_fd = -1
            raise JobError("state parent is busy") from exc
        self.name = self.path.name
        if not self.name or self.name in {".", ".."}:
            raise JobError("state name is invalid")
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

    def load(self) -> dict[str, Any]:
        self._validate_parent_path()
        data, metadata = read_regular_at(
            self.parent_fd, self.name, MAX_STATE_BYTES, "state", private=True
        )
        value = validate_state(parse_strict(data, "state"))
        if canonical_bytes(value) != data:
            raise JobError("state bytes are not canonical")
        self.raw, self.metadata, self.sha256, self.value = (
            data, metadata, sha256_bytes(data), value
        )
        return value

    def _validate_parent_path(self) -> None:
        try:
            current = self.parent.lstat()
        except OSError as exc:
            raise JobError("state parent path changed") from exc
        if not same_identity(current, self.parent_identity):
            raise JobError("state parent path changed")

    @contextlib.contextmanager
    def _blocked(self) -> Iterator[None]:
        prior = signal.pthread_sigmask(signal.SIG_BLOCK, SIGNALS)
        try:
            yield
        finally:
            signal.pthread_sigmask(signal.SIG_SETMASK, prior)

    def create(self, value: dict[str, Any]) -> str:
        validate_state(value)
        data = canonical_bytes(value)
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

    def update(self, updates: dict[str, Any]) -> str:
        if self.value is None or self.raw is None or self.metadata is None or self.sha256 is None:
            raise JobError("state is not loaded")
        self._validate_parent_path()
        current, current_metadata = read_regular_at(
            self.parent_fd, self.name, MAX_STATE_BYTES, "state", private=True
        )
        if current != self.raw or not same_identity(current_metadata, identity(self.metadata)):
            raise JobError("state changed before transition")
        next_value = dict(self.value)
        next_value.update(updates)
        next_value["sequence"] = self.value["sequence"] + 1
        next_value["previous_state_sha256"] = self.sha256
        validate_state(next_value)
        data = canonical_bytes(next_value)
        temporary = f".{self.name}.job-state.{secrets.token_hex(12)}.tmp"
        descriptor = -1
        with self._blocked():
            try:
                self._validate_parent_path()
                descriptor = os.open(
                    temporary,
                    os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
                    0o600,
                    dir_fd=self.parent_fd,
                )
                os.fchmod(descriptor, 0o600)
                _write_all(descriptor, data)
                os.fsync(descriptor)
                temporary_metadata = os.fstat(descriptor)
                os.close(descriptor)
                descriptor = -1
                now = os.stat(self.name, dir_fd=self.parent_fd, follow_symlinks=False)
                if not same_identity(now, identity(self.metadata)):
                    raise JobError("state changed during transition")
                os.replace(temporary, self.name, src_dir_fd=self.parent_fd, dst_dir_fd=self.parent_fd)
                installed = os.stat(self.name, dir_fd=self.parent_fd, follow_symlinks=False)
                if not same_identity(installed, identity(temporary_metadata)):
                    raise JobError("state replacement identity changed")
                self.raw, self.metadata, self.sha256, self.value = (
                    data, installed, sha256_bytes(data), next_value
                )
                os.fsync(self.parent_fd)
                self._validate_parent_path()
            except BaseException:
                if descriptor >= 0:
                    os.close(descriptor)
                try:
                    os.unlink(temporary, dir_fd=self.parent_fd)
                    os.fsync(self.parent_fd)
                except FileNotFoundError:
                    pass
                raise
        assert self.sha256 is not None
        return self.sha256


def _write_all(descriptor: int, data: bytes) -> None:
    view = memoryview(data)
    while view:
        written = os.write(descriptor, view)
        if written <= 0:
            raise JobError("state write failed")
        view = view[written:]


ACTIVE_PROCESS: subprocess.Popen[bytes] | None = None
FIRST_SIGNAL: int | None = None


def _interrupt(number: int, _frame: Any) -> None:
    global FIRST_SIGNAL
    if FIRST_SIGNAL is not None:
        return
    FIRST_SIGNAL = number
    raise JobSignal(number)


def _terminate_process(process: subprocess.Popen[bytes]) -> None:
    # A non-None returncode means Popen has already reaped the leader. Never use
    # its former PID as process-group authority after that point: the PGID may
    # already have been reused by an unrelated process.
    if process.returncode is not None:
        return
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except (ProcessLookupError, PermissionError):
        pass
    time.sleep(0.25)
    # Keep the unreaped leader as the PGID reservation and send KILL before the
    # sole wait. There are deliberately no group probes or signals after wait.
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        pass
    try:
        process.wait(timeout=0.75)
    except subprocess.TimeoutExpired as exc:
        raise JobError("child cleanup failed") from exc


def _communicate_bounded(
    process: subprocess.Popen[bytes],
    input_data: bytes | None,
    maximum: int,
    timeout: float,
) -> bytes:
    if process.stdout is None or maximum < 0 or timeout <= 0:
        raise GitError("invalid bounded Git capture")
    selector = selectors.DefaultSelector()
    output = bytearray()
    pending = memoryview(input_data if input_data is not None else b"")
    deadline = time.monotonic() + timeout
    try:
        os.set_blocking(process.stdout.fileno(), False)
        selector.register(process.stdout, selectors.EVENT_READ, "stdout")
        if process.stdin is not None:
            os.set_blocking(process.stdin.fileno(), False)
            if pending:
                selector.register(process.stdin, selectors.EVENT_WRITE, "stdin")
            else:
                process.stdin.close()
        while selector.get_map():
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise subprocess.TimeoutExpired(process.args, timeout)
            events = selector.select(remaining)
            if not events:
                raise subprocess.TimeoutExpired(process.args, timeout)
            for key, _mask in events:
                if key.data == "stdout":
                    try:
                        chunk = os.read(key.fd, min(64 * 1024, maximum - len(output) + 1))
                    except BlockingIOError:
                        continue
                    if not chunk:
                        selector.unregister(key.fileobj)
                        key.fileobj.close()
                        continue
                    output.extend(chunk)
                    if len(output) > maximum:
                        raise GitOutputLimitError("Git validation output is oversized")
                else:
                    try:
                        written = os.write(key.fd, pending[:64 * 1024])
                    except BlockingIOError:
                        continue
                    except BrokenPipeError:
                        written = 0
                        pending = pending[len(pending):]
                    if written > 0:
                        pending = pending[written:]
                    if not pending:
                        selector.unregister(key.fileobj)
                        key.fileobj.close()
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise subprocess.TimeoutExpired(process.args, timeout)
        process.wait(timeout=remaining)
        return bytes(output)
    finally:
        selector.close()
        if process.stdin is not None and not process.stdin.closed:
            process.stdin.close()
        if process.stdout is not None and not process.stdout.closed:
            process.stdout.close()


def run_process(arguments: list[str], *, cwd: Path | None = None) -> int:
    global ACTIVE_PROCESS
    prior = signal.pthread_sigmask(signal.SIG_BLOCK, SIGNALS)
    try:
        ACTIVE_PROCESS = subprocess.Popen(
            arguments,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=str(cwd) if cwd is not None else None,
            start_new_session=True,
        )
    finally:
        signal.pthread_sigmask(signal.SIG_SETMASK, prior)
    try:
        return ACTIVE_PROCESS.wait()
    except JobSignal as exc:
        signal.pthread_sigmask(signal.SIG_BLOCK, SIGNALS)
        _terminate_process(ACTIVE_PROCESS)
        signal.pthread_sigmask(signal.SIG_SETMASK, prior)
        raise exc
    finally:
        ACTIVE_PROCESS = None


@contextlib.contextmanager
def _private_empty_hooks() -> Iterator[Path]:
    directory = Path(tempfile.mkdtemp(prefix="agy-worker-empty-hooks.", dir="/tmp"))
    try:
        os.chmod(directory, 0o700)
        metadata = directory.lstat()
        if (
            not stat.S_ISDIR(metadata.st_mode)
            or stat.S_ISLNK(metadata.st_mode)
            or metadata.st_uid != os.getuid()
            or stat.S_IMODE(metadata.st_mode) != 0o700
            or any(directory.iterdir())
        ):
            raise JobError("private Git policy directory is invalid")
        yield directory
    finally:
        shutil.rmtree(directory, ignore_errors=True)


def _git_environment(private_home: Path) -> dict[str, str]:
    return {
        "GIT_ASKPASS": "/usr/bin/false",
        "GIT_CONFIG_GLOBAL": "/dev/null",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_EXTERNAL_DIFF": "",
        "GIT_PAGER": "cat",
        "GIT_TERMINAL_PROMPT": "0",
        "HOME": str(private_home),
        "LANG": "C",
        "LC_ALL": "C",
        "NO_COLOR": "1",
        "PAGER": "cat",
        "PATH": "/usr/bin:/bin",
        "SSH_ASKPASS": "/usr/bin/false",
        "XDG_CONFIG_HOME": str(private_home),
    }


def _git_arguments(repo: Path | None, hooks: Path, arguments: tuple[str, ...]) -> list[str]:
    command = [
        GIT_EXECUTABLE,
        "-c", f"core.hooksPath={hooks}",
        "-c", "core.fsmonitor=false",
        "-c", "core.pager=cat",
        "-c", "pager.branch=false",
        "-c", "interactive.diffFilter=",
        "-c", "credential.helper=",
        "-c", "protocol.allow=never",
        "-c", "protocol.file.allow=never",
        "-c", "submodule.recurse=false",
        "-c", "fetch.recurseSubmodules=false",
        "-c", "color.ui=false",
    ]
    if repo is not None:
        command += ["-C", str(repo)]
    command.extend(arguments)
    return command


def git_result(
    repo: Path | None,
    *arguments: str,
    input_data: bytes | None = None,
    capture: bool = True,
) -> GitResult:
    global ACTIVE_PROCESS
    if not Path(GIT_EXECUTABLE).is_file():
        raise GitError("fixed Git executable is unavailable")
    with _private_empty_hooks() as hooks:
        command = _git_arguments(repo, hooks, arguments)
        prior = signal.pthread_sigmask(signal.SIG_BLOCK, SIGNALS)
        try:
            ACTIVE_PROCESS = subprocess.Popen(
                command,
                stdin=subprocess.PIPE if input_data is not None else subprocess.DEVNULL,
                stdout=subprocess.PIPE if capture else subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                env=_git_environment(hooks),
                start_new_session=True,
            )
        except OSError as exc:
            raise GitError("Git validation failed") from exc
        finally:
            signal.pthread_sigmask(signal.SIG_SETMASK, prior)
        try:
            try:
                if capture:
                    stdout = _communicate_bounded(
                        ACTIVE_PROCESS, input_data, MAX_GIT_OUTPUT, GIT_TIMEOUT_SECONDS
                    )
                else:
                    stdout, _stderr = ACTIVE_PROCESS.communicate(
                        input=input_data, timeout=GIT_TIMEOUT_SECONDS
                    )
            except subprocess.TimeoutExpired as exc:
                signal.pthread_sigmask(signal.SIG_BLOCK, SIGNALS)
                try:
                    _terminate_process(ACTIVE_PROCESS)
                except JobError as cleanup_exc:
                    raise GitError("Git cleanup failed") from cleanup_exc
                finally:
                    signal.pthread_sigmask(signal.SIG_SETMASK, prior)
                raise GitError("Git validation timed out") from exc
            except GitOutputLimitError:
                signal.pthread_sigmask(signal.SIG_BLOCK, SIGNALS)
                try:
                    _terminate_process(ACTIVE_PROCESS)
                except JobError as cleanup_exc:
                    raise GitError("Git cleanup failed") from cleanup_exc
                finally:
                    signal.pthread_sigmask(signal.SIG_SETMASK, prior)
                raise
            except (OSError, ValueError) as exc:
                signal.pthread_sigmask(signal.SIG_BLOCK, SIGNALS)
                try:
                    _terminate_process(ACTIVE_PROCESS)
                except JobError as cleanup_exc:
                    raise GitError("Git cleanup failed") from cleanup_exc
                finally:
                    signal.pthread_sigmask(signal.SIG_SETMASK, prior)
                raise GitError("Git validation failed") from exc
            return GitResult(ACTIVE_PROCESS.returncode, stdout if capture else b"")
        except JobSignal as exc:
            signal.pthread_sigmask(signal.SIG_BLOCK, SIGNALS)
            try:
                _terminate_process(ACTIVE_PROCESS)
            finally:
                signal.pthread_sigmask(signal.SIG_SETMASK, prior)
            raise exc
        finally:
            ACTIVE_PROCESS = None


def git(repo: Path, *arguments: str, capture: bool = True) -> bytes:
    completed = git_result(repo, *arguments, capture=capture)
    if completed.returncode != 0:
        raise GitError("Git validation failed")
    return completed.stdout if capture else b""


def run_git(repo: Path, *arguments: str) -> int:
    return git_result(repo, *arguments, capture=False).returncode


def ref_value(repo: Path, reference: str) -> str | None:
    existence = git_result(repo, "show-ref", "--verify", "--quiet", reference)
    if existence.returncode == 1:
        return None
    if existence.returncode != 0:
        raise GitError("Git ref validation failed")
    completed = git_result(repo, "show-ref", "--verify", "--hash", reference)
    if completed.returncode != 0:
        raise GitError("Git ref validation failed")
    try:
        value = completed.stdout.decode("ascii", "strict").strip()
    except UnicodeDecodeError as exc:
        raise GitError("Git ref validation failed") from exc
    if COMMIT_RE.fullmatch(value) is None:
        raise GitError("Git ref validation failed")
    return value


def _config_key(record: bytes) -> bytes:
    # `git config --null --get-regexp` separates key and value with a newline.
    return record.split(b"\n", 1)[0]


def validate_safe_git_checkout(repo: Path, base: str) -> None:
    configured = git_result(
        repo,
        "config",
        "--local",
        "--includes",
        "--null",
        "--get-regexp",
        r"^(filter\..*\.(clean|smudge|process|required)|core\.(fsmonitor|hooksPath|pager)|diff\.external|interactive\.diffFilter|pager\..*|include(If)?\..*)$",
    )
    if configured.returncode not in {0, 1}:
        raise GitError("Git configuration validation failed")
    if configured.returncode == 0:
        records = [record for record in configured.stdout.split(b"\0") if record]
        if (
            not records
            or any(
                UNSAFE_GIT_CONFIG_RE.fullmatch(_config_key(record)) is None
                for record in records
            )
        ):
            raise JobError("Git configuration validation failed")
        raise JobError("external Git configuration is not checkout-safe")

    tree = git(repo, "ls-tree", "-r", "-z", "--name-only", base)
    if len(tree) > MAX_ATTRIBUTE_PATH_BYTES:
        raise JobError("base tree path inventory is oversized")
    paths = [path for path in tree.split(b"\0") if path]
    if len(paths) > MAX_DELETE_NODES:
        raise JobError("base tree path inventory is oversized")
    if any(b"\n" in path or b"\r" in path for path in paths):
        raise JobError("base tree path inventory is invalid")
    if not paths:
        return
    attributes = git_result(
        repo,
        "check-attr",
        f"--source={base}",
        "-z",
        "--stdin",
        "filter",
        input_data=b"\0".join(paths) + b"\0",
    )
    if attributes.returncode != 0:
        raise GitError("Git attribute validation failed")
    fields = attributes.stdout.split(b"\0")
    if fields and fields[-1] == b"":
        fields.pop()
    if len(fields) != len(paths) * 3:
        raise JobError("Git attribute validation failed")
    for index, path in enumerate(paths):
        record = fields[index * 3:index * 3 + 3]
        if (
            record[0] != path
            or record[1] != b"filter"
            or record[2] not in {b"unspecified", b"unset"}
        ):
            raise JobError("external Git content filters are not checkout-safe")


def canonical_repo(path: Path) -> tuple[Path, dict[str, int], Path, dict[str, int]]:
    path = real_absolute(path, "repository")
    metadata = path.lstat()
    if not stat.S_ISDIR(metadata.st_mode) or stat.S_ISLNK(metadata.st_mode):
        raise JobError("repository must be one real directory")
    root = Path(git(path, "rev-parse", "--show-toplevel").decode("utf-8", "strict").strip())
    if root != path:
        raise JobError("repository must be the exact top-level worktree")
    common_text = git(path, "rev-parse", "--git-common-dir").decode("utf-8", "strict").strip()
    common = Path(common_text)
    if not common.is_absolute():
        common = path / common
    common = Path(os.path.realpath(common))
    common_metadata = common.lstat()
    if not stat.S_ISDIR(common_metadata.st_mode) or stat.S_ISLNK(common_metadata.st_mode):
        raise JobError("Git common directory must be real")
    return path, identity(metadata), common, identity(common_metadata)


def validate_branch(repo: Path, branch: str) -> str:
    if not canonical_branch_syntax(branch):
        raise JobError("branch is invalid")
    completed = git_result(repo, "check-ref-format", "--branch", branch)
    if completed.returncode != 0:
        raise JobError("branch is invalid")
    expected = branch.encode("utf-8", "strict") + b"\n"
    if completed.stdout != expected:
        raise JobError("branch shorthand or canonicalization is forbidden")
    return f"refs/heads/{branch}"


def validate_base(repo: Path, base: str) -> None:
    if COMMIT_RE.fullmatch(base) is None:
        raise JobError("base must be one full immutable commit ID")
    resolved = git(repo, "rev-parse", "--verify", f"{base}^{{commit}}").decode("ascii").strip()
    if resolved != base:
        raise JobError("base did not resolve exactly")


def output_state(state: dict[str, Any], digest: str) -> None:
    result: dict[str, Any] = {
        "cleanup_authorized": False,
        "job_id": state["job_id"],
        "phase": state["phase"],
        "state_sha256": digest,
    }
    if state["last_result"] is not None:
        result["last_result"] = state["last_result"]
    print(canonical_bytes(result).decode("ascii"), end="")


def initial_state(args: argparse.Namespace) -> tuple[dict[str, Any], Path, Path]:
    if JOB_RE.fullmatch(args.job_id or "") is None:
        raise JobError("job ID is invalid")
    repo, repo_id, common, common_id = canonical_repo(Path(args.repo))
    validate_base(repo, args.base)
    validate_safe_git_checkout(repo, args.base)
    branch_ref = validate_branch(repo, args.branch)
    if ref_value(repo, branch_ref) is not None:
        raise JobError("branch already exists")
    worktree = real_absolute(Path(args.worktree), "worktree", must_exist=False)
    if worktree.exists() or worktree.is_symlink():
        raise JobError("worktree path already exists")
    worktree_parent = real_absolute(worktree.parent, "worktree parent")
    if contains(repo, worktree) or contains(worktree, repo):
        raise JobError("worktree must be outside the repository")
    state_path = Path(args.state)
    if contains(repo, state_path) or contains(worktree, state_path):
        raise JobError("state must be outside repository and worktree")
    state = {
        "schema_version": 1,
        "kind": "agy-worker-local-job-state",
        "sequence": 1,
        "previous_state_sha256": None,
        "phase": "initializing",
        "job_id": args.job_id,
        "repo_path": str(repo),
        "repo_identity": repo_id,
        "git_common_dir": str(common),
        "git_common_identity": common_id,
        "worktree_path": str(worktree),
        "worktree_parent_device": worktree_parent.lstat().st_dev,
        "worktree_identity": None,
        "branch": branch_ref.removeprefix("refs/heads/"),
        "branch_ref": branch_ref,
        "base": args.base,
        "receipt": None,
        "dispatch": None,
        "cleanup_step": "none",
        "last_result": None,
        "failure": None,
    }
    if args.facade_created:
        if args.dispatch_job_dir is None:
            raise JobError("facade init requires a dispatch job directory")
        dispatch_job_dir = real_absolute(
            Path(args.dispatch_job_dir), "dispatch job directory", must_exist=False
        )
        if contains(repo, dispatch_job_dir) or contains(worktree, dispatch_job_dir):
            raise JobError("dispatch job directory must be outside repository and worktree")
        state["schema_version"] = 2
        state["origin"] = FACADE_ORIGIN
        state["dispatch_job_dir"] = str(dispatch_job_dir)
    elif args.dispatch_job_dir is not None:
        raise JobError("dispatch job directory is facade-only initialization data")
    return state, repo, worktree


def command_init(args: argparse.Namespace) -> int:
    state, repo, worktree = initial_state(args)
    store = StateStore(Path(args.state), initial=True)
    try:
        store.create(state)
        try:
            rc = run_git(
                repo,
                "worktree", "add", "-b", state["branch"], str(worktree), state["base"],
            )
            if rc != 0:
                store.update({"phase": "init-failed", "failure": "init-failed", "last_result": rc})
                output_state(store.value, store.sha256)  # type: ignore[arg-type]
                return 1
            facts = validate_ready_state(state)
            store.update({"phase": "ready", "worktree_identity": facts["worktree_identity"]})
            output_state(store.value, store.sha256)  # type: ignore[arg-type]
            return 0
        except JobSignal as exc:
            store.update({"phase": "init-interrupted", "failure": "interrupted", "last_result": 128 + exc.number})
            output_state(store.value, store.sha256)  # type: ignore[arg-type]
            return 128 + exc.number
        except (JobError, OSError):
            store.update({"phase": "init-failed", "failure": "init-failed", "last_result": 1})
            output_state(store.value, store.sha256)  # type: ignore[arg-type]
            return 1
    finally:
        store.close()


def worktree_records(repo: Path) -> list[dict[str, str]]:
    raw = git(repo, "worktree", "list", "--porcelain", "-z")
    records: list[dict[str, str]] = []
    current: dict[str, str] = {}
    for token in raw.split(b"\0"):
        if not token:
            if current:
                records.append(current)
                current = {}
            continue
        text = token.decode("utf-8", "strict")
        key, separator, value = text.partition(" ")
        current[key] = value if separator else "true"
    if current:
        records.append(current)
    return records


def validate_repo_binding(state: dict[str, Any]) -> Path:
    repo, repo_id, common, common_id = canonical_repo(Path(state["repo_path"]))
    if repo_id != state["repo_identity"] or str(common) != state["git_common_dir"] or common_id != state["git_common_identity"]:
        raise JobError("repository binding changed")
    return repo


def validate_ready_state(state: dict[str, Any]) -> dict[str, Any]:
    repo = validate_repo_binding(state)
    worktree = real_absolute(Path(state["worktree_path"]), "worktree")
    metadata = worktree.lstat()
    if not stat.S_ISDIR(metadata.st_mode) or stat.S_ISLNK(metadata.st_mode):
        raise JobError("worktree is not one real directory")
    records = [record for record in worktree_records(repo) if record.get("worktree") == str(worktree)]
    if len(records) != 1:
        raise JobError("worktree registration changed")
    record = records[0]
    if record.get("HEAD") != state["base"] or record.get("branch") != state["branch_ref"]:
        raise JobError("worktree registration changed")
    head = git(worktree, "rev-parse", "HEAD").decode("ascii").strip()
    symbolic = git(worktree, "symbolic-ref", "-q", "HEAD").decode("utf-8", "strict").strip()
    branch_value = git(repo, "rev-parse", "--verify", state["branch_ref"]).decode("ascii").strip()
    if head != state["base"] or branch_value != state["base"] or symbolic != state["branch_ref"]:
        raise JobError("branch or worktree HEAD moved")
    expected = state["worktree_identity"]
    current_identity = identity(metadata)
    if expected is not None and current_identity != expected:
        raise JobError("worktree identity changed")
    if worktree.parent.lstat().st_dev != state["worktree_parent_device"]:
        raise JobError("worktree parent device changed")
    return {"repo": repo, "worktree": worktree, "worktree_identity": current_identity}


def _receipt_binding(path: Path, expected_exit: int, base: str) -> dict[str, Any]:
    path = real_absolute(path, "receipt")
    raw, _metadata = read_regular(path, MAX_RECEIPT_BYTES, "receipt", private=True)
    scripts_root = SCRIPTS.parent
    schema = load_schema(scripts_root / "schemas/evidence-receipt.schema.json")
    try:
        receipt = validate_receipt(parse_json_bytes(raw, "receipt"), schema)
    except ValidationFailure as exc:
        raise JobError("receipt is invalid") from exc
    if receipt["gate_exit"] != expected_exit or receipt["resolved_base"] != base:
        raise JobError("receipt outcome or base is unbound")
    return {
        "path": str(path),
        "sha256": sha256_bytes(raw),
        "gate_exit": receipt["gate_exit"],
        "verdict": receipt["verdict"],
        "final_candidate_state_sha256": receipt["final_candidate_state_sha256"],
    }


def command_verify(args: argparse.Namespace) -> int:
    store = StateStore(Path(args.state))
    try:
        state = store.value
        assert state is not None
        if state["phase"] not in {"ready", "verify-failed"}:
            raise JobError("state is not eligible for verification")
        facts = validate_ready_state(state)
        receipt = real_absolute(Path(args.receipt), "receipt", must_exist=False)
        if receipt.exists() or receipt.is_symlink():
            raise JobError("receipt path already exists")
        store.update({"phase": "verifying", "failure": None, "last_result": None, "receipt": None})
        runtime = SCRIPTS.parent
        command = [
            str(runtime / "verify-job.sh"), "--receipt", str(receipt),
            "--envelope", args.envelope, "--repo", str(facts["worktree"]),
            "--base", state["base"],
        ]
        for value in args.allow:
            command += ["--allow", value]
        for value in args.only:
            command += ["--only", value]
        if args.expect_edits:
            command.append("--expect-edits")
        for flag, value in args.verifiers:
            command += [flag, value]
        for flag in (
            "legacy_shell_verification",
            "acknowledge_verifier_network",
            "acknowledge_verifier_credential_access",
        ):
            if getattr(args, flag):
                command.append("--" + flag.replace("_", "-"))
        for value in args.verify_env:
            command += ["--verify-env", value]
        for value in args.verify_credential_env:
            command += ["--verify-credential-env", value]
        if args.selection:
            command += ["--selection", args.selection]
        if args.pre_recommendation:
            command += ["--pre-recommendation", args.pre_recommendation]
        try:
            rc = run_process(command)
        except JobSignal as exc:
            store.update({"phase": "verify-interrupted", "failure": "interrupted", "last_result": 128 + exc.number})
            output_state(store.value, store.sha256)  # type: ignore[arg-type]
            return 128 + exc.number
        if rc in {0, 10, 11, 12, 13, 14, 15}:
            binding = _receipt_binding(receipt, rc, state["base"])
            current = candidate_state_digest(
                facts["worktree"], state["base"], git_reader=git
            )
            if binding["final_candidate_state_sha256"] != current:
                raise JobError("receipt does not bind the current candidate")
            phase = (
                "verified-gate-passed" if rc == 0
                else "verified-routed" if rc == 15
                else "verified-rejected"
            )
            store.update({"phase": phase, "receipt": binding, "failure": None, "last_result": rc})
        else:
            if receipt.exists() or receipt.is_symlink():
                raise JobError("failed verification left an unbound receipt")
            store.update({"phase": "verify-failed", "failure": "verify-failed", "last_result": rc})
        output_state(store.value, store.sha256)  # type: ignore[arg-type]
        return rc
    except (JobError, CandidateStateError, OSError):
        if store.value is not None and store.value["phase"] == "verifying":
            try:
                store.update({"phase": "verify-failed", "failure": "verify-failed", "last_result": 1})
            except (JobError, OSError):
                pass
        raise
    finally:
        store.close()


def validate_receipt_binding(state: dict[str, Any]) -> dict[str, Any]:
    binding = state["receipt"]
    if not isinstance(binding, dict):
        raise JobError("rejected state has no receipt binding")
    current = _receipt_binding(Path(binding["path"]), binding["gate_exit"], state["base"])
    if current != binding:
        raise JobError("receipt binding changed")
    if current["gate_exit"] not in {10, 11, 12, 13, 14} or current["verdict"] != "rejected":
        raise JobError("receipt is not cleanup-eligible")
    return current


def _acquire_dispatch_lock(
    job: Path, expected: dict[str, int] | None = None
) -> tuple[int, dict[str, int]]:
    path = job / DISPATCH_LOCK_NAME
    try:
        descriptor = os.open(
            path,
            os.O_RDWR | getattr(os, "O_NOFOLLOW", 0),
        )
    except OSError as exc:
        raise JobError("dispatch controller lock is unavailable") from exc
    try:
        metadata = os.fstat(descriptor)
        try:
            named = path.lstat()
        except OSError as exc:
            raise JobError("dispatch controller lock path changed") from exc
        current = identity(metadata)
        if (
            not stat.S_ISREG(metadata.st_mode)
            or stat.S_ISLNK(named.st_mode)
            or metadata.st_uid != os.getuid()
            or stat.S_IMODE(metadata.st_mode) != 0o600
            or metadata.st_nlink != 1
            or not same_identity(named, current)
            or (expected is not None and current != expected)
        ):
            raise JobError("dispatch controller lock binding changed")
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise JobError("dispatch controller is still active") from exc
        return descriptor, current
    except BaseException:
        os.close(descriptor)
        raise


def _closed_dispatch_lock(job: Path, expected: dict[str, int] | None = None) -> dict[str, int]:
    descriptor, current = _acquire_dispatch_lock(job, expected)
    os.close(descriptor)
    return current


@contextlib.contextmanager
def _held_dispatch_lock(
    job: Path, expected: dict[str, int] | None = None
) -> Iterator[dict[str, int]]:
    descriptor, current = _acquire_dispatch_lock(job, expected)
    try:
        yield current
    finally:
        os.close(descriptor)


def _dispatch_binding(
    state: dict[str, Any], path: Path, candidate_sha256: str
) -> dict[str, Any]:
    path = real_absolute(path, "dispatch state")
    if path.name != "dispatch-state.json":
        raise JobError("dispatch state filename is invalid")
    try:
        job = canonical_dispatch_job(path.parent)
        with _held_dispatch_lock(job) as lock_identity:
            raw, metadata = read_dispatch_regular(
                path, MAX_DISPATCH_STATE_BYTES, "dispatch state"
            )
            dispatch = parse_dispatch_json(raw, "dispatch state")
            validate_dispatch_state(dispatch)
            if dispatch_canonical_bytes(dispatch) != raw:
                raise JobError("dispatch state bytes are not canonical")
            if (
                dispatch["status"] not in {"failed", "cancelled"}
                or dispatch["reason"] is None
                or dispatch["exit_code"] in {None, 0}
                or dispatch["controller_pid"] is not None
                or dispatch["finished_epoch"] is None
                or dispatch["sequence"] < 2
                or dispatch["previous_state_sha256"] is None
            ):
                raise JobError("dispatch is not one terminal failure")
            if dispatch["job_id"] != state["job_id"]:
                raise JobError("dispatch job binding does not match lifecycle")
            if dispatch["workdir"] != state["worktree_path"]:
                raise JobError("dispatch worktree binding does not match lifecycle")
            repo = Path(state["repo_path"])
            worktree = Path(state["worktree_path"])
            if contains(repo, job) or contains(worktree, job):
                raise JobError("dispatch evidence must be outside repository and worktree")
            return {
                "path": str(path),
                "sha256": sha256_bytes(raw),
                "state_identity": identity(metadata),
                "job_identity": identity(job.lstat()),
                "lock_identity": lock_identity,
                "status": dispatch["status"],
                "reason": dispatch["reason"],
                "exit_code": dispatch["exit_code"],
                "candidate_state_sha256": candidate_sha256,
            }
    except (DispatchError, OSError) as exc:
        raise JobError("dispatch state is invalid") from exc


def validate_dispatch_binding(
    state: dict[str, Any], *, lock_is_held: bool = False
) -> dict[str, Any]:
    binding = state["dispatch"]
    if not isinstance(binding, dict):
        raise JobError("dispatch-failed state has no dispatch binding")
    path = Path(binding["path"])
    try:
        job = canonical_dispatch_job(path.parent)
        raw, metadata = read_dispatch_regular(
            path, MAX_DISPATCH_STATE_BYTES, "dispatch state"
        )
        dispatch = parse_dispatch_json(raw, "dispatch state")
        validate_dispatch_state(dispatch)
    except (DispatchError, OSError) as exc:
        raise JobError("dispatch binding changed") from exc
    if (
        identity(job.lstat()) != binding["job_identity"]
        or identity(metadata) != binding["state_identity"]
        or sha256_bytes(raw) != binding["sha256"]
        or dispatch_canonical_bytes(dispatch) != raw
        or dispatch["job_id"] != state["job_id"]
        or dispatch["workdir"] != state["worktree_path"]
        or dispatch["status"] != binding["status"]
        or dispatch["reason"] != binding["reason"]
        or dispatch["exit_code"] != binding["exit_code"]
        or dispatch["controller_pid"] is not None
    ):
        raise JobError("dispatch binding changed")
    if not lock_is_held:
        _closed_dispatch_lock(job, binding["lock_identity"])
    return binding


def command_record_dispatch_failure(args: argparse.Namespace) -> int:
    store = StateStore(Path(args.state))
    try:
        state = store.value
        assert state is not None and store.sha256 is not None
        if state["phase"] != "ready" or state["receipt"] is not None:
            raise JobError("state is not eligible for dispatch-failure recording")
        if args.approve_job != state["job_id"]:
            raise JobError("dispatch job approval does not match")
        if args.approve_state_sha != store.sha256:
            raise JobError("dispatch state approval does not match current bytes")
        if not isinstance(args.approve_candidate_sha, str) or SHA_RE.fullmatch(args.approve_candidate_sha) is None:
            raise JobError("dispatch candidate approval is invalid")
        facts = validate_ready_state(state)
        current = candidate_state_digest(
            facts["worktree"], state["base"], git_reader=git
        )
        if current != args.approve_candidate_sha:
            raise JobError("dispatch candidate approval does not match current bytes")
        binding = _dispatch_binding(state, Path(args.dispatch_state), current)
        store.update({
            "phase": "dispatch-failed",
            "dispatch": binding,
            "failure": "dispatch-failed",
            "last_result": binding["exit_code"],
        })
        output_state(store.value, store.sha256)  # type: ignore[arg-type]
        return 0
    finally:
        store.close()


def scan_deletion_domain(worktree: Path) -> None:
    root = worktree.lstat()
    root_device = root.st_dev
    seen = 0
    for directory, names, files in os.walk(worktree, topdown=True, followlinks=False):
        directory_path = Path(directory)
        metadata = directory_path.lstat()
        if not stat.S_ISDIR(metadata.st_mode) or metadata.st_dev != root_device:
            raise JobError("worktree crosses a device or mount boundary")
        for name in [*names, *files]:
            seen += 1
            if seen > MAX_DELETE_NODES:
                raise JobError("worktree deletion domain is oversized")
            path = directory_path / name
            item = path.lstat()
            relative = path.relative_to(worktree)
            if item.st_dev != root_device:
                raise JobError("worktree crosses a device or mount boundary")
            if name == ".git" and relative != Path(".git"):
                raise JobError("nested repository or initialized submodule is not disposable")
            # Candidate-state evidence binds a symlink's path, mode, and target.
            # os.walk never follows it, so removal can delete only the link node;
            # its target remains outside the proven deletion domain.
            if not (
                stat.S_ISREG(item.st_mode)
                or stat.S_ISDIR(item.st_mode)
                or stat.S_ISLNK(item.st_mode)
            ):
                raise JobError("special nodes are not cleanup-eligible")


def _cleanup_reconcile(store: StateStore) -> None:
    state = store.value
    assert state is not None
    repo = validate_repo_binding(state)
    worktree = Path(state["worktree_path"])
    registered = any(record.get("worktree") == str(worktree) for record in worktree_records(repo))
    if not registered and not worktree.exists() and state["cleanup_step"] == "none":
        store.update({"cleanup_step": "worktree-removed"})
        state = store.value
        assert state is not None
    ref_exists = ref_value(repo, state["branch_ref"]) is not None
    if not ref_exists and state["cleanup_step"] == "worktree-removed":
        terminal = "aborted" if state["phase"] == "abort-in-progress" else "cleaned"
        store.update({"cleanup_step": "branch-removed", "phase": terminal, "failure": None, "last_result": 0})


def _cleanup_checkpoint(_name: str) -> None:
    """Test-only callable; production has no CLI or environment override."""


def _rollback_dispatch_absent(path: Path) -> Path:
    path = real_absolute(path, "dispatch job directory", must_exist=False)
    try:
        path.lstat()
    except FileNotFoundError:
        return path
    except OSError as exc:
        raise JobError("dispatch job directory cannot be proven absent") from exc
    raise JobError("dispatch evidence exists")


def _delete_unchanged_state(store: StateStore) -> None:
    if (
        store.raw is None
        or store.metadata is None
        or store.sha256 is None
        or store.value is None
    ):
        raise JobError("state is not loaded")
    with store._blocked():
        store._validate_parent_path()
        current, metadata = read_regular_at(
            store.parent_fd, store.name, MAX_STATE_BYTES, "state", private=True
        )
        if current != store.raw or not same_identity(
            metadata, identity(store.metadata)
        ):
            raise JobError("state changed before rollback completion")
        os.unlink(store.name, dir_fd=store.parent_fd)
        os.fsync(store.parent_fd)
        store._validate_parent_path()
        try:
            os.stat(store.name, dir_fd=store.parent_fd, follow_symlinks=False)
        except FileNotFoundError:
            return
        raise JobError("state rollback removal was incomplete")


def command_rollback_ready(args: argparse.Namespace) -> int:
    store = StateStore(Path(args.state))
    try:
        state = store.value
        assert state is not None and store.sha256 is not None
        if (
            state["schema_version"] != 2
            or state.get("origin") != FACADE_ORIGIN
            or state["phase"] != "ready"
            or state["receipt"] is not None
            or state.get("dispatch") is not None
        ):
            raise JobError("state is not facade rollback-eligible")
        if args.approve_job != state["job_id"]:
            raise JobError("rollback job approval does not match")
        if args.approve_state_sha != store.sha256:
            raise JobError("rollback state approval does not match current bytes")
        if (
            args.repo != state["repo_path"]
            or args.worktree != state["worktree_path"]
            or args.branch != state["branch"]
            or args.base != state["base"]
            or args.dispatch_job_dir != state["dispatch_job_dir"]
        ):
            raise JobError("rollback resource binding does not match state")
        dispatch_job = _rollback_dispatch_absent(Path(args.dispatch_job_dir))
        repo = Path(state["repo_path"])
        worktree = Path(state["worktree_path"])
        if contains(repo, dispatch_job) or contains(worktree, dispatch_job):
            raise JobError("dispatch job directory must be outside repository and worktree")

        facts = validate_ready_state(state)
        scan_deletion_domain(facts["worktree"])
        if candidate_state_digest(
            facts["worktree"], state["base"], git_reader=git
        ) != EMPTY_CANDIDATE_STATE_SHA256:
            raise JobError("rollback candidate is not empty")

        _rollback_dispatch_absent(dispatch_job)
        _cleanup_checkpoint("before-rollback-worktree-remove")
        _rollback_dispatch_absent(dispatch_job)
        facts = validate_ready_state(state)
        scan_deletion_domain(facts["worktree"])
        if candidate_state_digest(
            facts["worktree"], state["base"], git_reader=git
        ) != EMPTY_CANDIDATE_STATE_SHA256:
            raise JobError("rollback candidate changed before worktree removal")
        rc = run_git(
            facts["repo"], "worktree", "remove", "--force", str(facts["worktree"])
        )
        if rc != 0:
            raise JobError("rollback worktree removal failed")
        if facts["worktree"].exists() or any(
            record.get("worktree") == str(facts["worktree"])
            for record in worktree_records(facts["repo"])
        ):
            raise JobError("rollback worktree removal was incomplete")

        _rollback_dispatch_absent(dispatch_job)
        repo = validate_repo_binding(state)
        if ref_value(repo, state["branch_ref"]) != state["base"]:
            raise JobError("branch ref moved before rollback compare-and-delete")
        _cleanup_checkpoint("before-rollback-ref-delete")
        _rollback_dispatch_absent(dispatch_job)
        rc = run_git(repo, "update-ref", "-d", state["branch_ref"], state["base"])
        if rc != 0:
            raise JobError("rollback compare-and-delete ref failed")
        if ref_value(repo, state["branch_ref"]) is not None:
            raise JobError("rolled-back branch ref still exists")

        _rollback_dispatch_absent(dispatch_job)
        _cleanup_checkpoint("before-rollback-state-delete")
        _rollback_dispatch_absent(dispatch_job)
        _delete_unchanged_state(store)
        print(canonical_bytes({
            "job_id": state["job_id"],
            "rollback_complete": True,
        }).decode("ascii"), end="")
        return 0
    finally:
        store.close()


def command_cleanup(args: argparse.Namespace) -> int:
    store = StateStore(Path(args.state))
    try:
        state = store.value
        assert state is not None and store.sha256 is not None
        if args.approve_job != state["job_id"]:
            raise JobError("cleanup job approval does not match")
        if args.approve_state_sha != store.sha256:
            raise JobError("cleanup state approval does not match current bytes")
        if not isinstance(args.approve_candidate_sha, str) or SHA_RE.fullmatch(args.approve_candidate_sha) is None:
            raise JobError("cleanup candidate approval is invalid")
        if state["phase"] not in {"verified-rejected", "cleanup-in-progress"}:
            raise JobError("state is not cleanup-eligible")
        receipt = validate_receipt_binding(state)
        if args.approve_candidate_sha != receipt["final_candidate_state_sha256"]:
            raise JobError("cleanup candidate approval does not match receipt")
        if state["phase"] == "cleanup-in-progress":
            approved_sha = store.sha256
            _cleanup_reconcile(store)
            state = store.value
            assert state is not None and store.sha256 is not None
            if state["phase"] == "cleaned":
                output_state(state, store.sha256)
                return 0
            if store.sha256 != approved_sha:
                # Reconciliation is observational only. Never spend approval for
                # old bytes on the next destructive step; print the new binding
                # and require a fresh invocation with its SHA.
                output_state(state, store.sha256)
                return 74
        facts: dict[str, Any] | None = None
        if state["cleanup_step"] == "none":
            facts = validate_ready_state(state)
            scan_deletion_domain(facts["worktree"])
            current = candidate_state_digest(
                facts["worktree"], state["base"], git_reader=git
            )
            if current != args.approve_candidate_sha:
                raise JobError("candidate changed after verification")
        if state["phase"] != "cleanup-in-progress":
            store.update({"phase": "cleanup-in-progress", "failure": None, "last_result": None})
            state = store.value
            assert state is not None
        if state["cleanup_step"] == "none":
            facts = validate_ready_state(state)
            scan_deletion_domain(facts["worktree"])
            if candidate_state_digest(
                facts["worktree"], state["base"], git_reader=git
            ) != args.approve_candidate_sha:
                raise JobError("candidate changed before cleanup")
            _cleanup_checkpoint("before-worktree-remove")
            rc = run_git(
                facts["repo"], "worktree", "remove", "--force", str(facts["worktree"])
            )
            if rc != 0:
                raise JobError("worktree removal failed")
            if facts["worktree"].exists() or any(
                record.get("worktree") == str(facts["worktree"])
                for record in worktree_records(facts["repo"])
            ):
                raise JobError("worktree removal was incomplete")
            store.update({"cleanup_step": "worktree-removed"})
            state = store.value
            assert state is not None
        if state["cleanup_step"] == "worktree-removed":
            repo = validate_repo_binding(state)
            worktree = Path(state["worktree_path"])
            if worktree.exists() or any(
                record.get("worktree") == str(worktree) for record in worktree_records(repo)
            ):
                raise JobError("removed worktree step does not match Git reality")
            if ref_value(repo, state["branch_ref"]) != state["base"]:
                raise JobError("branch ref moved before compare-and-delete")
            _cleanup_checkpoint("before-ref-delete")
            rc = run_git(
                repo, "update-ref", "-d", state["branch_ref"], state["base"]
            )
            if rc != 0:
                raise JobError("compare-and-delete ref failed")
            if ref_value(repo, state["branch_ref"]) is not None:
                raise JobError("branch ref still exists")
            store.update({"cleanup_step": "branch-removed", "phase": "cleaned", "failure": None, "last_result": 0})
        output_state(store.value, store.sha256)  # type: ignore[arg-type]
        return 0
    except JobSignal as exc:
        prior_mask = signal.pthread_sigmask(signal.SIG_BLOCK, SIGNALS)
        try:
            _cleanup_reconcile(store)
            if store.value is not None and store.value["phase"] == "cleanup-in-progress":
                store.update({"failure": "interrupted", "last_result": 128 + exc.number})
        except (JobError, OSError):
            pass
        finally:
            # The first signal is authoritative. Pending later lifecycle signals
            # are delivered to the non-raising handler after cleanup completes.
            signal.pthread_sigmask(signal.SIG_SETMASK, prior_mask)
        output_state(store.value, store.sha256)  # type: ignore[arg-type]
        return 128 + exc.number
    except GitError:
        # A fatal/transient ref observation after compare-delete is uncertainty,
        # never proof of absence. Do not retry/reconcile it into `cleaned` in the
        # same invocation; persist failure and require manual review plus a fresh
        # approval-bound invocation.
        if store.value is not None and store.value["phase"] == "cleanup-in-progress":
            try:
                store.update({"failure": "cleanup-failed", "last_result": 1})
            except (JobError, OSError):
                pass
        raise
    except (JobError, CandidateStateError, OSError):
        if store.value is not None and store.value["phase"] == "cleanup-in-progress":
            try:
                _cleanup_reconcile(store)
                if store.value is not None and store.value["phase"] == "cleanup-in-progress":
                    store.update({"failure": "cleanup-failed", "last_result": 1})
            except (JobError, OSError):
                pass
        raise
    finally:
        store.close()


def command_abort(args: argparse.Namespace) -> int:
    dispatch_lock_descriptor = -1
    store = StateStore(Path(args.state))
    try:
        state = store.value
        assert state is not None and store.sha256 is not None
        if args.approve_job != state["job_id"]:
            raise JobError("abort job approval does not match")
        if args.approve_state_sha != store.sha256:
            raise JobError("abort state approval does not match current bytes")
        if not isinstance(args.approve_candidate_sha, str) or SHA_RE.fullmatch(args.approve_candidate_sha) is None:
            raise JobError("abort candidate approval is invalid")
        if state["phase"] not in {"dispatch-failed", "abort-in-progress"}:
            raise JobError("state is not abort-eligible")
        untrusted_binding = state["dispatch"]
        if not isinstance(untrusted_binding, dict):
            raise JobError("dispatch-failed state has no dispatch binding")
        dispatch_job = canonical_dispatch_job(Path(untrusted_binding["path"]).parent)
        dispatch_lock_descriptor, _lock_identity = _acquire_dispatch_lock(
            dispatch_job, untrusted_binding["lock_identity"]
        )
        binding = validate_dispatch_binding(state, lock_is_held=True)
        if args.approve_candidate_sha != binding["candidate_state_sha256"]:
            raise JobError("abort candidate approval does not match dispatch binding")
        if (
            binding["candidate_state_sha256"] != EMPTY_CANDIDATE_STATE_SHA256
            and not args.discard_unverified
        ):
            raise JobError("changed unverified candidate needs explicit discard approval")
        if state["phase"] == "abort-in-progress":
            approved_sha = store.sha256
            _cleanup_reconcile(store)
            state = store.value
            assert state is not None and store.sha256 is not None
            if state["phase"] == "aborted":
                output_state(state, store.sha256)
                return 0
            if store.sha256 != approved_sha:
                output_state(state, store.sha256)
                return 74
        facts: dict[str, Any] | None = None
        if state["cleanup_step"] == "none":
            facts = validate_ready_state(state)
            scan_deletion_domain(facts["worktree"])
            current = candidate_state_digest(
                facts["worktree"], state["base"], git_reader=git
            )
            if current != args.approve_candidate_sha:
                raise JobError("candidate changed after dispatch failure")
        if state["phase"] != "abort-in-progress":
            store.update({
                "phase": "abort-in-progress", "failure": None,
                "last_result": None,
            })
            state = store.value
            assert state is not None
        if state["cleanup_step"] == "none":
            validate_dispatch_binding(state, lock_is_held=True)
            facts = validate_ready_state(state)
            scan_deletion_domain(facts["worktree"])
            if candidate_state_digest(
                facts["worktree"], state["base"], git_reader=git
            ) != args.approve_candidate_sha:
                raise JobError("candidate changed before abort")
            _cleanup_checkpoint("before-abort-worktree-remove")
            rc = run_git(
                facts["repo"], "worktree", "remove", "--force", str(facts["worktree"])
            )
            if rc != 0:
                raise JobError("worktree abort removal failed")
            if facts["worktree"].exists() or any(
                record.get("worktree") == str(facts["worktree"])
                for record in worktree_records(facts["repo"])
            ):
                raise JobError("worktree abort removal was incomplete")
            store.update({"cleanup_step": "worktree-removed"})
            state = store.value
            assert state is not None
        if state["cleanup_step"] == "worktree-removed":
            validate_dispatch_binding(state, lock_is_held=True)
            repo = validate_repo_binding(state)
            worktree = Path(state["worktree_path"])
            if worktree.exists() or any(
                record.get("worktree") == str(worktree)
                for record in worktree_records(repo)
            ):
                raise JobError("removed abort worktree does not match Git reality")
            if ref_value(repo, state["branch_ref"]) != state["base"]:
                raise JobError("branch ref moved before abort compare-and-delete")
            _cleanup_checkpoint("before-abort-ref-delete")
            rc = run_git(repo, "update-ref", "-d", state["branch_ref"], state["base"])
            if rc != 0:
                raise JobError("abort compare-and-delete ref failed")
            if ref_value(repo, state["branch_ref"]) is not None:
                raise JobError("aborted branch ref still exists")
            store.update({
                "cleanup_step": "branch-removed", "phase": "aborted",
                "failure": None, "last_result": 0,
            })
        output_state(store.value, store.sha256)  # type: ignore[arg-type]
        return 0
    except JobSignal as exc:
        prior_mask = signal.pthread_sigmask(signal.SIG_BLOCK, SIGNALS)
        try:
            _cleanup_reconcile(store)
            if store.value is not None and store.value["phase"] == "abort-in-progress":
                store.update({"failure": "interrupted", "last_result": 128 + exc.number})
        except (JobError, OSError):
            pass
        finally:
            signal.pthread_sigmask(signal.SIG_SETMASK, prior_mask)
        output_state(store.value, store.sha256)  # type: ignore[arg-type]
        return 128 + exc.number
    except GitError:
        if store.value is not None and store.value["phase"] == "abort-in-progress":
            try:
                store.update({"failure": "cleanup-failed", "last_result": 1})
            except (JobError, OSError):
                pass
        raise
    except (JobError, CandidateStateError, OSError):
        if store.value is not None and store.value["phase"] == "abort-in-progress":
            try:
                _cleanup_reconcile(store)
                if store.value is not None and store.value["phase"] == "abort-in-progress":
                    store.update({"failure": "cleanup-failed", "last_result": 1})
            except (JobError, OSError):
                pass
        raise
    finally:
        if dispatch_lock_descriptor >= 0:
            os.close(dispatch_lock_descriptor)
        store.close()


def status_facts(state: dict[str, Any]) -> dict[str, Any]:
    result = {
        "branch_matches": False,
        "candidate_matches_receipt": False,
        "candidate_matches_dispatch": False,
        "dispatch_bound": False,
        "dispatch_candidate_state_sha256": None,
        "receipt_candidate_state_sha256": None,
        "cleanup_authorized": False,
        "job_id": state["job_id"],
        "phase": state["phase"],
        "receipt_bound": False,
        "worktree_registered": False,
    }
    try:
        facts = validate_ready_state(state)
        result["branch_matches"] = True
        result["worktree_registered"] = True
        if state["receipt"] is not None:
            receipt = validate_receipt_binding(state)
            result["receipt_bound"] = True
            result["receipt_candidate_state_sha256"] = receipt["final_candidate_state_sha256"]
            result["candidate_matches_receipt"] = (
                candidate_state_digest(
                    facts["worktree"], state["base"], git_reader=git
                )
                == receipt["final_candidate_state_sha256"]
            )
        elif state.get("dispatch") is not None:
            dispatch = validate_dispatch_binding(state)
            result["dispatch_bound"] = True
            result["dispatch_candidate_state_sha256"] = dispatch["candidate_state_sha256"]
            result["candidate_matches_dispatch"] = (
                candidate_state_digest(
                    facts["worktree"], state["base"], git_reader=git
                )
                == dispatch["candidate_state_sha256"]
            )
    except (JobError, CandidateStateError, OSError):
        pass
    return result


def command_status(args: argparse.Namespace) -> int:
    store = StateStore(Path(args.state))
    try:
        result = status_facts(store.value)  # type: ignore[arg-type]
        result["state_sha256"] = store.sha256
        print(canonical_bytes(result).decode("ascii"), end="")
        return 0
    finally:
        store.close()


def command_preserve(args: argparse.Namespace) -> int:
    store = StateStore(Path(args.state))
    try:
        state = store.value
        assert state is not None
        if state["phase"] != "verified-gate-passed":
            raise JobError("only gate-passed work receives preserve instructions")
        validate_ready_state(state)
        worktree = shlex.quote(state["worktree_path"])
        repo = shlex.quote(state["repo_path"])
        branch = shlex.quote(state["branch"])
        print(f"git -C {worktree} status --short")
        print(f"git -C {worktree} add -- REPLACE_WITH_REVIEWED_PATHS")
        print(f"git -C {worktree} commit -m 'REPLACE_WITH_REVIEWED_MESSAGE'")
        print(f"git -C {repo} worktree remove {worktree}")
        print(f"# integrate {branch} only through your normal reviewed Git workflow")
        return 0
    finally:
        store.close()


def parser() -> argparse.ArgumentParser:
    result = Parser(prog="job.sh")
    commands = result.add_subparsers(dest="command", required=True, parser_class=Parser)
    init = commands.add_parser("init")
    for name in ("state", "repo", "worktree", "branch", "base", "job-id"):
        init.add_argument(f"--{name}", action=Once, required=True)
    init.add_argument("--facade-created", action=OnceTrue)
    init.add_argument("--dispatch-job-dir", action=Once)
    status = commands.add_parser("status")
    status.add_argument("--state", action=Once, required=True)
    verify = commands.add_parser("verify")
    verify.add_argument("--state", action=Once, required=True)
    verify.add_argument("--receipt", action=Once, required=True)
    verify.add_argument("--envelope", action=Once, required=True)
    verify.add_argument("--allow", action="append", default=[])
    verify.add_argument("--only", action="append", default=[])
    verify.add_argument("--expect-edits", action=OnceTrue)
    verify.set_defaults(verifiers=[])
    verify.add_argument(
        "--verify-argv", dest="verifiers", action=OrderedVerifier, const="--verify-argv"
    )
    verify.add_argument(
        "--verify-shell", dest="verifiers", action=OrderedVerifier, const="--verify-shell"
    )
    verify.add_argument(
        "--verify", dest="verifiers", action=OrderedVerifier, const="--verify"
    )
    verify.add_argument("--legacy-shell-verification", action=OnceTrue)
    verify.add_argument("--acknowledge-verifier-network", action=OnceTrue)
    verify.add_argument("--acknowledge-verifier-credential-access", action=OnceTrue)
    verify.add_argument("--verify-env", action="append", default=[])
    verify.add_argument("--verify-credential-env", action="append", default=[])
    verify.add_argument("--selection", action=Once)
    verify.add_argument("--pre-recommendation", action=Once)
    preserve = commands.add_parser("preserve-instructions")
    preserve.add_argument("--state", action=Once, required=True)
    cleanup = commands.add_parser("cleanup")
    cleanup.add_argument("--state", action=Once, required=True)
    cleanup.add_argument("--approve-job", action=Once, required=True)
    cleanup.add_argument("--approve-state-sha", action=Once, required=True)
    cleanup.add_argument("--approve-candidate-sha", action=Once, required=True)
    rollback = commands.add_parser("rollback-ready")
    for name in (
        "state", "approve-job", "approve-state-sha", "repo", "worktree",
        "branch", "base", "dispatch-job-dir",
    ):
        rollback.add_argument(f"--{name}", action=Once, required=True)
    record = commands.add_parser("record-dispatch-failure")
    record.add_argument("--state", action=Once, required=True)
    record.add_argument("--dispatch-state", action=Once, required=True)
    record.add_argument("--approve-job", action=Once, required=True)
    record.add_argument("--approve-state-sha", action=Once, required=True)
    record.add_argument("--approve-candidate-sha", action=Once, required=True)
    abort = commands.add_parser("abort")
    abort.add_argument("--state", action=Once, required=True)
    abort.add_argument("--approve-job", action=Once, required=True)
    abort.add_argument("--approve-state-sha", action=Once, required=True)
    abort.add_argument("--approve-candidate-sha", action=Once, required=True)
    abort.add_argument("--discard-unverified", action=OnceTrue)
    return result


def main(argv: list[str] | None = None) -> int:
    global FIRST_SIGNAL
    FIRST_SIGNAL = None
    for number in SIGNALS:
        signal.signal(number, _interrupt)
    try:
        args = parser().parse_args(argv)
        if args.command == "init":
            return command_init(args)
        if args.command == "status":
            return command_status(args)
        if args.command == "verify":
            if not args.verifiers:
                raise JobError("verify needs at least one driver command")
            return command_verify(args)
        if args.command == "preserve-instructions":
            return command_preserve(args)
        if args.command == "cleanup":
            return command_cleanup(args)
        if args.command == "rollback-ready":
            return command_rollback_ready(args)
        if args.command == "record-dispatch-failure":
            return command_record_dispatch_failure(args)
        if args.command == "abort":
            return command_abort(args)
        raise JobError("unknown command")
    except JobSignal as exc:
        print("job: interrupted", file=sys.stderr)
        return 128 + exc.number
    except JobError:
        print("job: local lifecycle validation failed", file=sys.stderr)
        return 64
    except (OSError, CandidateStateError):
        print("job: local lifecycle operation failed", file=sys.stderr)
        return 74


def process_main() -> None:
    """Own signal handling through flush and atomic process termination."""
    try:
        result = main()
        sys.stdout.flush()
        sys.stderr.flush()
    except JobSignal as exc:
        # A first signal after command return but before termination still wins.
        # _interrupt makes every later lifecycle signal non-raising.
        result = 128 + exc.number
        print("job: interrupted", file=sys.stderr)
        sys.stdout.flush()
        sys.stderr.flush()
    os._exit(result)


if __name__ == "__main__":
    process_main()
