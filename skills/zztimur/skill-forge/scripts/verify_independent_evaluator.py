#!/usr/bin/env python3
"""Run a release candidate through an independently installed Skill Forge.

The installed evaluator is treated as pre-trusted, read-only provenance. Its
complete tree and inspector are pinned, copied into a temporary directory, and
only the copy is executed. The candidate receives the same treatment. A pass
means both originals matched their pre-execution content and identity snapshots
afterward; this helper is process-isolated but is not an operating-system
filesystem or network sandbox.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import signal
import stat
import subprocess
import sys
import tempfile
import threading
import time
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple


SCHEMA_VERSION = 2
REQUIRED_INSPECTOR_SCHEMA_VERSION = 6
BOOTSTRAP_INSPECTOR_SCHEMA_VERSION = 5
BOOTSTRAP_SCHEMA_TRANSITION = "5:6"
BOOTSTRAP_RELEASE_TAG = "v2.0.0"
BOOTSTRAP_EVIDENCE_LABEL = "bootstrap transition evidence"
BOOTSTRAP_TRANSITION_REUSABLE = False
SOURCE_REPO = Path(__file__).resolve().parents[1]
INSPECTOR_RELATIVE_PATH = "scripts/inspect_skill_package.py"
PROFILES = ("portable", "openai")
TREE_HASH_DOMAIN = b"skill-forge-independent-evaluator-tree-v1\0"
TREE_INTEGRITY_DOMAIN = b"skill-forge-independent-evaluator-integrity-v1\0"
HASH_CHUNK_BYTES = 1024 * 1024
MAX_EVALUATOR_ENTRIES = 20_000
MAX_EVALUATOR_FILE_BYTES = 50 * 1024 * 1024
MAX_EVALUATOR_TOTAL_BYTES = 250 * 1024 * 1024
MAX_CANDIDATE_BYTES = 64 * 1024 * 1024
MAX_STREAM_BYTES = 2 * 1024 * 1024
MAX_JSON_DEPTH = 64
MAX_JSON_NODES = 100_000
PROCESS_TIMEOUT_SECONDS = 60.0
PROCESS_POLL_SECONDS = 0.02
PROCESS_SHUTDOWN_SECONDS = 5.0


class VerificationError(RuntimeError):
    """Raised when independent evaluation cannot be completed safely."""


@dataclass(frozen=True)
class DirectoryRecord:
    relative_path: str
    mode: int
    device: int
    inode: int
    mtime_ns: int


@dataclass(frozen=True)
class FileRecord:
    relative_path: str
    size: int
    sha256: str
    mode: Optional[int] = None
    device: Optional[int] = None
    inode: Optional[int] = None
    mtime_ns: Optional[int] = None


@dataclass(frozen=True)
class RegularFileSnapshot:
    sha256: str
    size: int
    mode: int
    device: int
    inode: int
    mtime_ns: int


@dataclass(frozen=True)
class TreeSnapshot:
    sha256: str
    integrity_sha256: str
    root_mode: int
    directories: Tuple[DirectoryRecord, ...]
    files: Tuple[FileRecord, ...]
    total_bytes: int

    def file_map(self) -> Dict[str, FileRecord]:
        return {record.relative_path: record for record in self.files}


@dataclass(frozen=True)
class ProcessResult:
    launched: bool
    returncode: Optional[int]
    stdout: bytes
    stderr: bytes
    stdout_bytes: int
    stderr_bytes: int
    timed_out: bool
    output_limit_exceeded: bool
    launch_error: Optional[str]


def _is_filesystem_ancestor(ancestor: Path, path: Path) -> bool:
    """Compare ancestry by filesystem identity, not case-sensitive spelling."""

    current = path
    while True:
        try:
            if os.path.samefile(str(ancestor), str(current)):
                return True
        except OSError as exc:
            raise VerificationError(
                f"cannot compare filesystem identities: {ancestor} / {current}: {exc}"
            ) from exc
        parent = current.parent
        if parent == current:
            return False
        current = parent


def _is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdefABCDEF" for character in value)
    )


def _stat_identity(value: os.stat_result) -> Tuple[int, int, int, int, int]:
    return (
        value.st_dev,
        value.st_ino,
        value.st_mode,
        value.st_size,
        value.st_mtime_ns,
    )


def _open_regular_file(path: Path) -> Tuple[int, os.stat_result]:
    """Open a regular file without following a final symlink when supported."""
    flags = os.O_RDONLY
    flags |= getattr(os, "O_BINARY", 0)
    flags |= getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(str(path), flags)
    except OSError as exc:
        raise VerificationError(f"cannot open a required regular file: {path}: {exc}") from exc
    try:
        opened_stat = os.fstat(descriptor)
        if not stat.S_ISREG(opened_stat.st_mode):
            raise VerificationError(f"path is not a regular file: {path}")
        try:
            path_stat = path.lstat()
        except OSError as exc:
            raise VerificationError(f"cannot re-check opened file identity: {path}: {exc}") from exc
        if stat.S_ISLNK(path_stat.st_mode) or _stat_identity(path_stat) != _stat_identity(opened_stat):
            raise VerificationError(f"file identity changed while it was opened: {path}")
        return descriptor, opened_stat
    except Exception:
        os.close(descriptor)
        raise


def _hash_regular_file(path: Path, maximum_bytes: int) -> RegularFileSnapshot:
    descriptor, opened_stat = _open_regular_file(path)
    digest = hashlib.sha256()
    size = 0
    try:
        with os.fdopen(descriptor, "rb", closefd=True) as handle:
            while True:
                chunk = handle.read(HASH_CHUNK_BYTES)
                if not chunk:
                    break
                size += len(chunk)
                if size > maximum_bytes:
                    raise VerificationError(f"file exceeds the safe read limit: {path}")
                digest.update(chunk)
            final_stat = os.fstat(handle.fileno())
    except VerificationError:
        raise
    except OSError as exc:
        raise VerificationError(f"cannot hash file: {path}: {exc}") from exc
    if size != opened_stat.st_size or _stat_identity(final_stat) != _stat_identity(opened_stat):
        raise VerificationError(f"file changed while it was hashed: {path}")
    return RegularFileSnapshot(
        sha256=digest.hexdigest(),
        size=size,
        mode=stat.S_IMODE(final_stat.st_mode),
        device=final_stat.st_dev,
        inode=final_stat.st_ino,
        mtime_ns=final_stat.st_mtime_ns,
    )


def _utf8_name(name: str, path: Path) -> bytes:
    try:
        return name.encode("utf-8", errors="strict")
    except UnicodeEncodeError as exc:
        raise VerificationError(f"tree path is not valid UTF-8: {path}") from exc


def _scan_tree(root: Path) -> TreeSnapshot:
    try:
        root_stat = root.lstat()
    except OSError as exc:
        raise VerificationError(f"cannot inspect evaluator root: {root}: {exc}") from exc
    if stat.S_ISLNK(root_stat.st_mode) or not stat.S_ISDIR(root_stat.st_mode):
        raise VerificationError(f"evaluator root must resolve to a real directory: {root}")

    directories: List[DirectoryRecord] = []
    files: List[FileRecord] = []
    total_bytes = 0
    entry_count = 0
    pending: List[Tuple[Path, PurePosixPath]] = [(root, PurePosixPath())]

    while pending:
        directory, relative_directory = pending.pop()
        try:
            with os.scandir(str(directory)) as iterator:
                entries = []
                for entry in iterator:
                    if entry_count + len(entries) + 1 > MAX_EVALUATOR_ENTRIES:
                        raise VerificationError(
                            "evaluator tree exceeds the safe entry limit"
                        )
                    entries.append(entry)
        except OSError as exc:
            raise VerificationError(f"cannot enumerate evaluator directory: {directory}: {exc}") from exc
        entries.sort(key=lambda entry: _utf8_name(entry.name, Path(entry.path)))
        child_directories: List[Tuple[Path, PurePosixPath]] = []
        for entry in entries:
            entry_count += 1
            if entry_count > MAX_EVALUATOR_ENTRIES:
                raise VerificationError("evaluator tree exceeds the safe entry limit")
            relative = relative_directory / entry.name
            relative_text = relative.as_posix()
            path = Path(entry.path)
            try:
                entry_stat = entry.stat(follow_symlinks=False)
            except OSError as exc:
                raise VerificationError(f"cannot inspect evaluator entry: {path}: {exc}") from exc
            if stat.S_ISLNK(entry_stat.st_mode):
                raise VerificationError(f"evaluator tree contains a symlink: {relative_text}")
            if stat.S_ISDIR(entry_stat.st_mode):
                directories.append(
                    DirectoryRecord(
                        relative_path=relative_text,
                        mode=stat.S_IMODE(entry_stat.st_mode),
                        device=entry_stat.st_dev,
                        inode=entry_stat.st_ino,
                        mtime_ns=entry_stat.st_mtime_ns,
                    )
                )
                child_directories.append((path, relative))
                continue
            if not stat.S_ISREG(entry_stat.st_mode):
                raise VerificationError(f"evaluator tree contains an unsupported entry: {relative_text}")
            try:
                before_hash_stat = path.lstat()
            except OSError as exc:
                raise VerificationError(f"cannot re-check evaluator entry: {path}: {exc}") from exc
            if stat.S_ISLNK(before_hash_stat.st_mode) or not stat.S_ISREG(before_hash_stat.st_mode):
                raise VerificationError(f"evaluator entry changed during tree scan: {relative_text}")
            file_snapshot = _hash_regular_file(path, MAX_EVALUATOR_FILE_BYTES)
            try:
                after_hash_stat = path.lstat()
            except OSError as exc:
                raise VerificationError(f"cannot re-check evaluator entry: {path}: {exc}") from exc
            if _stat_identity(before_hash_stat) != _stat_identity(after_hash_stat):
                raise VerificationError(f"evaluator entry changed during tree scan: {relative_text}")
            total_bytes += file_snapshot.size
            if total_bytes > MAX_EVALUATOR_TOTAL_BYTES:
                raise VerificationError("evaluator tree exceeds the safe total byte limit")
            files.append(
                FileRecord(
                    relative_text,
                    file_snapshot.size,
                    file_snapshot.sha256,
                    file_snapshot.mode,
                    file_snapshot.device,
                    file_snapshot.inode,
                    file_snapshot.mtime_ns,
                )
            )
        # Stack insertion is reversed so traversal order itself is deterministic.
        pending.extend(reversed(child_directories))

    try:
        final_root_stat = root.lstat()
    except OSError as exc:
        raise VerificationError(f"cannot re-check evaluator root: {root}: {exc}") from exc
    if _stat_identity(final_root_stat) != _stat_identity(root_stat):
        raise VerificationError("evaluator root changed during tree scan")

    directories.sort(key=lambda value: value.relative_path.encode("utf-8"))
    files.sort(key=lambda record: record.relative_path.encode("utf-8"))
    digest = hashlib.sha256()
    digest.update(TREE_HASH_DOMAIN)
    _update_tree_digest(
        digest,
        b"root",
        b"",
        str(stat.S_IMODE(root_stat.st_mode)).encode("ascii"),
    )
    for directory_record in directories:
        _update_tree_digest(
            digest,
            b"directory",
            directory_record.relative_path.encode("utf-8"),
            str(directory_record.mode).encode("ascii"),
        )
    for record in files:
        payload = f"{record.size}:{record.sha256}:{record.mode}".encode("ascii")
        _update_tree_digest(digest, b"file", record.relative_path.encode("utf-8"), payload)

    integrity_digest = hashlib.sha256()
    integrity_digest.update(TREE_INTEGRITY_DOMAIN)
    _update_tree_digest(
        integrity_digest,
        b"root",
        b"",
        (
            f"{root_stat.st_dev}:{root_stat.st_ino}:{root_stat.st_mode}:"
            f"{root_stat.st_mtime_ns}"
        ).encode("ascii"),
    )
    for directory_record in directories:
        payload = (
            f"{directory_record.device}:{directory_record.inode}:"
            f"{directory_record.mode}:{directory_record.mtime_ns}"
        ).encode("ascii")
        _update_tree_digest(
            integrity_digest,
            b"directory",
            directory_record.relative_path.encode("utf-8"),
            payload,
        )
    for record in files:
        payload = (
            f"{record.device}:{record.inode}:{record.mode}:{record.mtime_ns}:"
            f"{record.size}:{record.sha256}"
        ).encode("ascii")
        _update_tree_digest(
            integrity_digest,
            b"file",
            record.relative_path.encode("utf-8"),
            payload,
        )
    return TreeSnapshot(
        sha256=digest.hexdigest(),
        integrity_sha256=integrity_digest.hexdigest(),
        root_mode=stat.S_IMODE(root_stat.st_mode),
        directories=tuple(directories),
        files=tuple(files),
        total_bytes=total_bytes,
    )


def _update_tree_digest(
    digest: "hashlib._Hash", entry_type: bytes, relative_path: bytes, payload: bytes
) -> None:
    for value in (entry_type, relative_path, payload):
        digest.update(len(value).to_bytes(8, byteorder="big", signed=False))
        digest.update(value)


def _path_from_relative(root: Path, relative_path: str) -> Path:
    return root.joinpath(*PurePosixPath(relative_path).parts)


def _copy_verified_file(source: Path, destination: Path, expected: FileRecord) -> None:
    descriptor, opened_stat = _open_regular_file(source)
    if (
        expected.mode is not None
        and stat.S_IMODE(opened_stat.st_mode) != expected.mode
    ):
        os.close(descriptor)
        raise VerificationError(f"source mode changed before copying: {source}")
    digest = hashlib.sha256()
    copied_bytes = 0
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        with os.fdopen(descriptor, "rb", closefd=True) as source_handle:
            with destination.open("xb") as destination_handle:
                while True:
                    chunk = source_handle.read(HASH_CHUNK_BYTES)
                    if not chunk:
                        break
                    copied_bytes += len(chunk)
                    if copied_bytes > expected.size:
                        raise VerificationError(f"source grew while copying: {source}")
                    digest.update(chunk)
                    destination_handle.write(chunk)
                final_stat = os.fstat(source_handle.fileno())
        if expected.mode is not None:
            os.chmod(destination, expected.mode)
    except VerificationError:
        raise
    except OSError as exc:
        raise VerificationError(f"cannot copy required file into scratch space: {source}: {exc}") from exc
    if _stat_identity(final_stat) != _stat_identity(opened_stat):
        raise VerificationError(f"source changed while copying: {source}")
    if copied_bytes != expected.size or digest.hexdigest() != expected.sha256:
        raise VerificationError(f"copied file does not match its original digest: {source}")


def _copy_tree(source_root: Path, destination_root: Path, snapshot: TreeSnapshot) -> None:
    destination_root.mkdir(parents=True, exist_ok=False)
    ordered_directories = sorted(
        snapshot.directories,
        key=lambda value: (
            len(PurePosixPath(value.relative_path).parts),
            value.relative_path.encode("utf-8"),
        ),
    )
    for directory_record in ordered_directories:
        _path_from_relative(
            destination_root, directory_record.relative_path
        ).mkdir(exist_ok=False)
    for record in snapshot.files:
        _copy_verified_file(
            _path_from_relative(source_root, record.relative_path),
            _path_from_relative(destination_root, record.relative_path),
            record,
        )
    # Apply restrictive modes only after descendants have been copied.
    for directory_record in reversed(ordered_directories):
        os.chmod(
            _path_from_relative(destination_root, directory_record.relative_path),
            directory_record.mode,
        )
    os.chmod(destination_root, snapshot.root_mode)


def _copy_candidate(source: Path, destination: Path, sha256: str, size: int) -> None:
    _copy_verified_file(source, destination, FileRecord(destination.name, size, sha256))


def _safe_environment(scratch_root: Path) -> Dict[str, str]:
    """Construct a small environment with no inherited credential variables."""
    environment: Dict[str, str] = {}
    for name in ("PATH", "SystemRoot", "WINDIR", "COMSPEC", "PATHEXT", "LANG", "LC_ALL", "LC_CTYPE"):
        value = os.environ.get(name)
        if value:
            environment[name] = value
    home = scratch_root / "home"
    temporary = scratch_root / "tmp"
    home.mkdir()
    temporary.mkdir()
    environment.update(
        {
            "HOME": str(home),
            "USERPROFILE": str(home),
            "TMPDIR": str(temporary),
            "TEMP": str(temporary),
            "TMP": str(temporary),
            "NO_COLOR": "1",
        }
    )
    return environment


def _kill_process_tree(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is not None:
        return
    try:
        if os.name == "posix":
            os.killpg(process.pid, signal.SIGKILL)
        else:
            process.kill()
    except (OSError, ProcessLookupError):
        try:
            process.kill()
        except OSError:
            pass


def _run_bounded(command: Sequence[str], cwd: Path, environment: Mapping[str, str]) -> ProcessResult:
    popen_kwargs: Dict[str, Any] = {
        "cwd": str(cwd),
        "env": dict(environment),
        "stdin": subprocess.DEVNULL,
        "stdout": subprocess.PIPE,
        "stderr": subprocess.PIPE,
        "shell": False,
        "close_fds": True,
    }
    if os.name == "posix":
        popen_kwargs["start_new_session"] = True
    elif hasattr(subprocess, "CREATE_NEW_PROCESS_GROUP"):
        popen_kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    try:
        process = subprocess.Popen(list(command), **popen_kwargs)
    except OSError as exc:
        return ProcessResult(False, None, b"", b"", 0, 0, False, False, str(exc))

    assert process.stdout is not None
    assert process.stderr is not None
    retained: Dict[str, bytearray] = {"stdout": bytearray(), "stderr": bytearray()}
    totals: Dict[str, int] = {"stdout": 0, "stderr": 0}
    output_limit = threading.Event()

    def drain(name: str, stream: Any) -> None:
        try:
            while True:
                chunk = stream.read(64 * 1024)
                if not chunk:
                    return
                totals[name] += len(chunk)
                available = MAX_STREAM_BYTES - len(retained[name])
                if available > 0:
                    retained[name].extend(chunk[:available])
                if totals[name] > MAX_STREAM_BYTES:
                    output_limit.set()
        except (OSError, ValueError):
            return

    threads = [
        threading.Thread(target=drain, args=("stdout", process.stdout), daemon=True),
        threading.Thread(target=drain, args=("stderr", process.stderr), daemon=True),
    ]
    for thread in threads:
        thread.start()

    timed_out = False
    deadline = time.monotonic() + PROCESS_TIMEOUT_SECONDS
    while process.poll() is None:
        if output_limit.is_set():
            _kill_process_tree(process)
            break
        if time.monotonic() >= deadline:
            timed_out = True
            _kill_process_tree(process)
            break
        time.sleep(PROCESS_POLL_SECONDS)
    try:
        process.wait(timeout=PROCESS_SHUTDOWN_SECONDS)
    except subprocess.TimeoutExpired:
        timed_out = True
        _kill_process_tree(process)
        try:
            process.wait(timeout=PROCESS_SHUTDOWN_SECONDS)
        except subprocess.TimeoutExpired:
            pass
    for thread in threads:
        thread.join(timeout=PROCESS_SHUTDOWN_SECONDS)
    try:
        process.stdout.close()
        process.stderr.close()
    except OSError:
        pass
    return ProcessResult(
        True,
        process.returncode,
        bytes(retained["stdout"]),
        bytes(retained["stderr"]),
        totals["stdout"],
        totals["stderr"],
        timed_out,
        output_limit.is_set(),
        None,
    )


def _load_strict_json(payload: bytes) -> Any:
    def reject_constant(value: str) -> None:
        raise ValueError(f"non-standard JSON constant: {value}")

    def unique_object(pairs: Iterable[Tuple[str, Any]]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result

    text = payload.decode("utf-8", errors="strict")
    value = json.loads(text, parse_constant=reject_constant, object_pairs_hook=unique_object)
    stack: List[Tuple[Any, int]] = [(value, 1)]
    nodes = 0
    while stack:
        current, depth = stack.pop()
        nodes += 1
        if nodes > MAX_JSON_NODES:
            raise ValueError("JSON exceeds the bounded node limit")
        if depth > MAX_JSON_DEPTH:
            raise ValueError("JSON exceeds the bounded nesting depth")
        if isinstance(current, dict):
            stack.extend((item, depth + 1) for item in current.values())
        elif isinstance(current, list):
            stack.extend((item, depth + 1) for item in current)
    return value


def _profile_result(
    profile: str,
    process: ProcessResult,
    expected_input: Path,
    bootstrap_transition: bool = False,
) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "status": "fail",
        "exit_code": process.returncode,
        "timed_out": process.timed_out,
        "output_limit_exceeded": process.output_limit_exceeded,
        "stdout_bytes": process.stdout_bytes,
        "stderr_bytes": process.stderr_bytes,
        "schema_version": None,
        "schema_compatibility": None,
        "evidence_label": None,
        "raw_frontmatter_propagated": False,
        "input": None,
        "input_type": None,
        "manifest_verification_complete": None,
        "requested_target": None,
        "canonical_target": None,
        "target_alias_used": None,
        "coverage_complete": None,
        "summary": None,
        "errors": [],
    }
    errors: List[str] = result["errors"]
    if not process.launched:
        result["status"] = "not_assessed"
        errors.append(f"scratch inspector could not start: {process.launch_error or 'unknown launch error'}")
        return result
    if process.timed_out:
        result["status"] = "not_assessed"
        errors.append(f"scratch inspector exceeded the {int(PROCESS_TIMEOUT_SECONDS)} second timeout")
    if process.output_limit_exceeded:
        result["status"] = "not_assessed"
        errors.append(f"scratch inspector exceeded the {MAX_STREAM_BYTES} byte stdout/stderr limit")
    if errors:
        return result
    try:
        data = _load_strict_json(process.stdout)
    except (UnicodeDecodeError, ValueError, json.JSONDecodeError, RecursionError) as exc:
        errors.append(f"scratch inspector did not return valid strict JSON: {exc}")
        return result
    if not isinstance(data, dict):
        errors.append("scratch inspector JSON root is not an object")
        return result

    inspector_schema = data.get("schema_version")
    if isinstance(inspector_schema, bool) or not isinstance(inspector_schema, int):
        result["status"] = "not_assessed"
        errors.append(
            "scratch inspector schema is incompatible: expected an integer schema version"
        )
        return result
    result["schema_version"] = inspector_schema
    expected_schema = (
        BOOTSTRAP_INSPECTOR_SCHEMA_VERSION
        if bootstrap_transition
        else REQUIRED_INSPECTOR_SCHEMA_VERSION
    )
    if inspector_schema != expected_schema:
        result["status"] = "not_assessed"
        errors.append(
            "scratch inspector schema is incompatible: expected "
            f"{expected_schema}, received {inspector_schema}"
        )
        return result
    result["schema_compatibility"] = (
        "bootstrap_5_to_6" if bootstrap_transition else "exact"
    )
    result["evidence_label"] = (
        BOOTSTRAP_EVIDENCE_LABEL
        if bootstrap_transition
        else "independent strict-inspection evidence"
    )

    requested = data.get("requested_target")
    canonical = data.get("canonical_target")
    alias_used = data.get("target_alias_used")
    coverage_complete = data.get("coverage_complete")
    summary = data.get("summary")
    input_path = data.get("input")
    input_type = data.get("input_type")
    manifest_complete = data.get("manifest_verification_complete")
    result.update(
        {
            "requested_target": requested,
            "canonical_target": canonical,
            "target_alias_used": alias_used,
            "coverage_complete": coverage_complete,
            "input": input_path,
            "input_type": input_type,
            "manifest_verification_complete": manifest_complete,
        }
    )
    if isinstance(summary, dict):
        result["summary"] = {
            "status": summary.get("status"),
            "strict_pass": summary.get("strict_pass"),
            "error_count": summary.get("error_count"),
            "warning_count": summary.get("warning_count"),
            "finding_count": summary.get("finding_count"),
        }
    else:
        errors.append("scratch inspector JSON omitted its summary object")

    if process.returncode != 0:
        errors.append(f"scratch inspector exited with status {process.returncode}")
    if input_path != str(expected_input):
        errors.append(
            "inspected input mismatch; display identifiers do not establish candidate identity"
        )
    if data.get("input_exists") is not True:
        errors.append("input_exists must be true")
    if input_type != "zip":
        errors.append(f"input_type must be 'zip', received {input_type!r}")
    if manifest_complete is not True:
        errors.append("manifest_verification_complete must be true")
    if requested != profile:
        errors.append(f"requested target mismatch: expected {profile!r}, received {requested!r}")
    if canonical != profile:
        errors.append(f"canonical target mismatch: expected {profile!r}, received {canonical!r}")
    if alias_used is not False:
        errors.append("target_alias_used must be false for a canonical profile")
    if coverage_complete is not True:
        errors.append("coverage_complete must be true")
    if not isinstance(summary, dict) or summary.get("strict_pass") is not True:
        errors.append("summary.strict_pass must be true")
    if isinstance(summary, dict) and summary.get("status") != "pass":
        errors.append("summary.status must be pass")
    if isinstance(summary, dict):
        counts = [
            summary.get("error_count"),
            summary.get("warning_count"),
            summary.get("finding_count"),
        ]
        if any(
            isinstance(value, bool) or not isinstance(value, int) or value < 0
            for value in counts
        ):
            errors.append("summary finding counts must be non-negative integers")
        else:
            if counts[0] != 0:
                errors.append("summary.error_count must be zero for a passing profile")
            if counts[2] < counts[0] + counts[1]:
                errors.append("summary finding_count is smaller than error plus warning counts")
    if not errors:
        result["status"] = "pass"
    return result


RUNNER_CODE = (
    "import os,runpy,sys;"
    "script=os.path.abspath(sys.argv[1]);"
    "sys.path.insert(0,os.path.dirname(script));"
    "sys.argv=[script]+sys.argv[2:];"
    "runpy.run_path(script,run_name='__main__')"
)


def _base_report(
    evaluator_root: Path,
    archive: Path,
    expected_inspector: Optional[str],
    expected_tree: Optional[str],
    expected_candidate: Optional[str],
    bootstrap_schema_transition: Optional[str],
    bootstrap_release_tag: Optional[str],
) -> Dict[str, Any]:
    transition_requested = (
        bootstrap_schema_transition is not None or bootstrap_release_tag is not None
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "not_assessed",
        "evidence_class": (
            "bootstrap_transition"
            if transition_requested
            else "independent_schema_match"
        ),
        "schema_transition": {
            "requested": transition_requested,
            "activated": False,
            "requested_transition": bootstrap_schema_transition,
            "requested_release_tag": bootstrap_release_tag,
            "allowed_transition": BOOTSTRAP_SCHEMA_TRANSITION,
            "allowed_release_tag": BOOTSTRAP_RELEASE_TAG,
            "from_schema_version": BOOTSTRAP_INSPECTOR_SCHEMA_VERSION,
            "to_schema_version": REQUIRED_INSPECTOR_SCHEMA_VERSION,
            "evidence_label": BOOTSTRAP_EVIDENCE_LABEL,
            "counts_as_independent_schema_6_pass": False,
            "raw_frontmatter_report_output": "forbidden",
            "reusable_after_release": BOOTSTRAP_TRANSITION_REUSABLE,
        },
        "evaluator_provenance": {
            "label": "independently-installed-local-skill",
            "path": str(evaluator_root),
            "tree_sha256": None,
            "tree_sha256_after": None,
            "tree_integrity_sha256": None,
            "tree_integrity_sha256_after": None,
            "tree_copy_sha256": None,
            "inspector_path": INSPECTOR_RELATIVE_PATH,
            "inspector_sha256": None,
            "inspector_sha256_after": None,
            "inspector_copy_sha256": None,
            "expected_inspector_sha256": (
                expected_inspector.lower()
                if _is_sha256(expected_inspector)
                else expected_inspector
            ),
            "expected_tree_sha256": (
                expected_tree.lower() if _is_sha256(expected_tree) else expected_tree
            ),
        },
        "candidate": {
            "path": str(archive),
            "sha256": None,
            "sha256_after": None,
            "copy_sha256": None,
            "expected_sha256": (
                expected_candidate.lower()
                if _is_sha256(expected_candidate)
                else expected_candidate
            ),
            "size": None,
            "mode": None,
            "mode_after": None,
            "mtime_ns": None,
            "mtime_ns_after": None,
            "device": None,
            "device_after": None,
            "inode": None,
            "inode_after": None,
        },
        "profiles": {},
        "scratch_execution": False,
        "credential_environment_removed": False,
        "installed_mutated": None,
        "installed_integrity_verified": False,
        "candidate_mutated": None,
        "candidate_integrity_verified": False,
        "execution_isolation": {
            "pretrusted_evaluator_required": True,
            "whole_tree_pin_required": True,
            "scratch_copy_only": True,
            "isolated_python": True,
            "credential_environment_removed": False,
            "os_filesystem_sandbox": False,
            "network_sandbox": False,
            "continuous_immutability_claimed": False,
        },
        "errors": [],
    }


def verify_independently(
    evaluator_root_argument: Path,
    archive_argument: Path,
    expected_inspector_sha256: Optional[str] = None,
    expected_evaluator_tree_sha256: Optional[str] = None,
    expected_candidate_sha256: Optional[str] = None,
    bootstrap_schema_transition: Optional[str] = None,
    bootstrap_release_tag: Optional[str] = None,
) -> Dict[str, Any]:
    report = _base_report(
        evaluator_root_argument,
        archive_argument,
        expected_inspector_sha256,
        expected_evaluator_tree_sha256,
        expected_candidate_sha256,
        bootstrap_schema_transition,
        bootstrap_release_tag,
    )
    errors: List[str] = report["errors"]
    evaluator_root: Optional[Path] = None
    archive: Optional[Path] = None
    evaluator_before: Optional[TreeSnapshot] = None
    candidate_before: Optional[RegularFileSnapshot] = None
    bootstrap_transition = False

    try:
        transition_requested = (
            bootstrap_schema_transition is not None
            or bootstrap_release_tag is not None
        )
        if transition_requested:
            if (
                bootstrap_schema_transition != BOOTSTRAP_SCHEMA_TRANSITION
                or bootstrap_release_tag != BOOTSTRAP_RELEASE_TAG
            ):
                raise VerificationError(
                    "bootstrap transition requires both "
                    f"--bootstrap-schema-transition {BOOTSTRAP_SCHEMA_TRANSITION} and "
                    f"--bootstrap-release-tag {BOOTSTRAP_RELEASE_TAG}"
                )
            bootstrap_transition = True
            report["schema_transition"]["activated"] = True
        if expected_inspector_sha256 is not None and not _is_sha256(expected_inspector_sha256):
            raise VerificationError("--expected-inspector-sha256 must be exactly 64 hexadecimal characters")
        if not _is_sha256(expected_evaluator_tree_sha256):
            raise VerificationError(
                "--expected-evaluator-tree-sha256 is required and must be exactly 64 hexadecimal characters"
            )
        if not _is_sha256(expected_candidate_sha256):
            raise VerificationError(
                "--expected-candidate-sha256 is required and must be exactly 64 hexadecimal characters"
            )
        try:
            evaluator_root = evaluator_root_argument.expanduser().resolve(strict=True)
        except OSError as exc:
            raise VerificationError(f"evaluator root cannot be resolved: {exc}") from exc
        report["evaluator_provenance"]["path"] = str(evaluator_root)
        if _is_filesystem_ancestor(SOURCE_REPO, evaluator_root) or _is_filesystem_ancestor(
            evaluator_root, SOURCE_REPO
        ):
            raise VerificationError(
                f"evaluator root overlaps the source repository and is not independent: {evaluator_root}"
            )

        try:
            archive = archive_argument.expanduser().resolve(strict=True)
        except OSError as exc:
            raise VerificationError(f"candidate archive cannot be resolved: {exc}") from exc
        report["candidate"]["path"] = str(archive)
        if _is_filesystem_ancestor(evaluator_root, archive):
            raise VerificationError(
                "candidate archive must not live inside the independent evaluator tree"
            )
        archive_lstat = archive.lstat()
        if stat.S_ISLNK(archive_lstat.st_mode) or not stat.S_ISREG(archive_lstat.st_mode):
            raise VerificationError("candidate archive must resolve to a regular non-symlink file")

        evaluator_before = _scan_tree(evaluator_root)
        report["evaluator_provenance"]["tree_sha256"] = evaluator_before.sha256
        report["evaluator_provenance"][
            "tree_integrity_sha256"
        ] = evaluator_before.integrity_sha256
        if evaluator_before.sha256 != expected_evaluator_tree_sha256.lower():
            raise VerificationError(
                "installed evaluator tree SHA-256 does not match "
                "--expected-evaluator-tree-sha256"
            )
        inspector_record = evaluator_before.file_map().get(INSPECTOR_RELATIVE_PATH)
        if inspector_record is None:
            raise VerificationError(f"evaluator does not contain {INSPECTOR_RELATIVE_PATH}")
        report["evaluator_provenance"]["inspector_sha256"] = inspector_record.sha256

        candidate_before = _hash_regular_file(archive, MAX_CANDIDATE_BYTES)
        report["candidate"].update(
            {
                "sha256": candidate_before.sha256,
                "size": candidate_before.size,
                "mode": candidate_before.mode,
                "mtime_ns": candidate_before.mtime_ns,
                "device": candidate_before.device,
                "inode": candidate_before.inode,
            }
        )
        if candidate_before.sha256 != expected_candidate_sha256.lower():
            raise VerificationError(
                "candidate SHA-256 does not match --expected-candidate-sha256"
            )
        if any(
            record.device == candidate_before.device
            and record.inode == candidate_before.inode
            for record in evaluator_before.files
        ):
            raise VerificationError(
                "candidate archive aliases a file inside the independent evaluator tree"
            )
        if expected_inspector_sha256 is not None and inspector_record.sha256 != expected_inspector_sha256.lower():
            raise VerificationError(
                "installed inspector SHA-256 does not match --expected-inspector-sha256"
            )

        with tempfile.TemporaryDirectory(prefix="skill-forge-independent-") as temporary_name:
            scratch_root = Path(temporary_name)
            evaluator_copy = scratch_root / "evaluator"
            archive_copy = scratch_root / "candidate.zip"
            work_directory = scratch_root / "work"
            work_directory.mkdir()
            _copy_tree(evaluator_root, evaluator_copy, evaluator_before)
            evaluator_copy_before = _scan_tree(evaluator_copy)
            report["evaluator_provenance"]["tree_copy_sha256"] = evaluator_copy_before.sha256
            if evaluator_copy_before.sha256 != evaluator_before.sha256:
                raise VerificationError("scratch evaluator tree does not match the installed evaluator digest")
            copied_inspector_record = evaluator_copy_before.file_map().get(INSPECTOR_RELATIVE_PATH)
            if copied_inspector_record is None or copied_inspector_record.sha256 != inspector_record.sha256:
                raise VerificationError("scratch inspector does not match the installed inspector digest")
            report["evaluator_provenance"]["inspector_copy_sha256"] = copied_inspector_record.sha256

            _copy_candidate(
                archive,
                archive_copy,
                candidate_before.sha256,
                candidate_before.size,
            )
            candidate_copy_before = _hash_regular_file(
                archive_copy, MAX_CANDIDATE_BYTES
            )
            report["candidate"]["copy_sha256"] = candidate_copy_before.sha256
            if (
                candidate_copy_before.sha256 != candidate_before.sha256
                or candidate_copy_before.size != candidate_before.size
            ):
                raise VerificationError("scratch candidate does not match the original candidate digest")

            environment = _safe_environment(scratch_root)
            report["credential_environment_removed"] = True
            report["execution_isolation"]["credential_environment_removed"] = True
            copied_inspector = _path_from_relative(evaluator_copy, INSPECTOR_RELATIVE_PATH)
            profile_failed = False
            profile_not_assessed = False
            for profile in PROFILES:
                command = [
                    sys.executable,
                    "-I",
                    "-S",
                    "-B",
                    "-c",
                    RUNNER_CODE,
                    str(copied_inspector),
                    str(archive_copy),
                    "--json",
                    "--strict",
                    "--target",
                    profile,
                ]
                process = _run_bounded(command, work_directory, environment)
                if process.launched:
                    report["scratch_execution"] = True
                profile_report = _profile_result(
                    profile,
                    process,
                    archive_copy,
                    bootstrap_transition=bootstrap_transition,
                )
                report["profiles"][profile] = profile_report
                if profile_report["status"] == "not_assessed":
                    profile_not_assessed = True
                    errors.extend(f"{profile}: {message}" for message in profile_report["errors"])
                elif profile_report["status"] != "pass":
                    profile_failed = True
                    errors.extend(f"{profile}: {message}" for message in profile_report["errors"])

            evaluator_copy_after = _scan_tree(evaluator_copy)
            candidate_copy_after = _hash_regular_file(
                archive_copy, MAX_CANDIDATE_BYTES
            )
            if (
                evaluator_copy_after.sha256 != evaluator_copy_before.sha256
                or evaluator_copy_after.integrity_sha256
                != evaluator_copy_before.integrity_sha256
            ):
                errors.append("scratch evaluator changed during execution")
                profile_failed = True
            if candidate_copy_after != candidate_copy_before:
                errors.append("scratch candidate changed during execution")
                profile_failed = True
            if not report["scratch_execution"]:
                errors.append("scratch inspector was never executed")
                profile_failed = True
            report["status"] = (
                "fail"
                if profile_failed
                else "not_assessed"
                if profile_not_assessed
                else "pass"
            )
    except VerificationError as exc:
        errors.append(str(exc))
        report["status"] = "fail" if report["scratch_execution"] else "not_assessed"
    except (OSError, ValueError) as exc:
        errors.append(f"independent evaluation failed safely: {exc}")
        report["status"] = "fail" if report["scratch_execution"] else "not_assessed"
    finally:
        if evaluator_root is not None and evaluator_before is not None:
            try:
                evaluator_after = _scan_tree(evaluator_root)
                report["evaluator_provenance"]["tree_sha256_after"] = evaluator_after.sha256
                report["evaluator_provenance"][
                    "tree_integrity_sha256_after"
                ] = evaluator_after.integrity_sha256
                after_inspector = evaluator_after.file_map().get(INSPECTOR_RELATIVE_PATH)
                if after_inspector is not None:
                    report["evaluator_provenance"]["inspector_sha256_after"] = after_inspector.sha256
                report["installed_mutated"] = (
                    evaluator_after.sha256 != evaluator_before.sha256
                    or evaluator_after.integrity_sha256
                    != evaluator_before.integrity_sha256
                )
                report["installed_integrity_verified"] = not report["installed_mutated"]
                if report["installed_mutated"]:
                    errors.append("installed evaluator changed during independent evaluation")
                    report["status"] = "fail"
            except VerificationError as exc:
                errors.append(f"could not prove installed evaluator remained unchanged: {exc}")
                report["installed_integrity_verified"] = False
                if report["scratch_execution"]:
                    report["status"] = "fail"

        if archive is not None and candidate_before is not None:
            try:
                candidate_after = _hash_regular_file(archive, MAX_CANDIDATE_BYTES)
                report["candidate"]["sha256_after"] = candidate_after.sha256
                report["candidate"]["mode_after"] = candidate_after.mode
                report["candidate"]["mtime_ns_after"] = candidate_after.mtime_ns
                report["candidate"]["device_after"] = candidate_after.device
                report["candidate"]["inode_after"] = candidate_after.inode
                report["candidate_mutated"] = candidate_after != candidate_before
                report["candidate_integrity_verified"] = not report["candidate_mutated"]
                if report["candidate_mutated"]:
                    errors.append("original candidate changed during independent evaluation")
                    report["status"] = "fail"
            except VerificationError as exc:
                errors.append(f"could not prove original candidate remained unchanged: {exc}")
                report["candidate_integrity_verified"] = False
                if report["scratch_execution"]:
                    report["status"] = "fail"

    if report["status"] == "pass" and (
        not report["installed_integrity_verified"]
        or not report["candidate_integrity_verified"]
        or len(report["profiles"]) != len(PROFILES)
        or any(item.get("status") != "pass" for item in report["profiles"].values())
    ):
        errors.append("pass invariants were not completely proven")
        report["status"] = "fail"
    return report


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify a candidate with an independently installed, read-only Skill Forge evaluator."
    )
    parser.add_argument("--evaluator-root", required=True, type=Path, help="independent Skill Forge root")
    parser.add_argument("--archive", required=True, type=Path, help="candidate Skill ZIP to inspect")
    parser.add_argument("--json", action="store_true", help="emit the complete machine-readable report")
    parser.add_argument(
        "--expected-inspector-sha256",
        help="optional pinned SHA-256 for scripts/inspect_skill_package.py",
    )
    parser.add_argument(
        "--expected-evaluator-tree-sha256",
        required=True,
        help="required pre-trusted SHA-256 for the complete evaluator tree",
    )
    parser.add_argument(
        "--expected-candidate-sha256",
        required=True,
        help="required expected SHA-256 for the candidate archive",
    )
    parser.add_argument(
        "--bootstrap-schema-transition",
        help=(
            "one-time schema transition; only '5:6' is accepted and it must be "
            "paired with --bootstrap-release-tag v2.0.0"
        ),
    )
    parser.add_argument(
        "--bootstrap-release-tag",
        help=(
            "candidate release identity for the one-time schema transition; "
            "only v2.0.0 is accepted"
        ),
    )
    return parser.parse_args(argv)


def render_report(report: Mapping[str, Any]) -> str:
    evaluator = report.get("evaluator_provenance", {})
    candidate = report.get("candidate", {})
    lines = [
        f"Independent evaluator verification: {report.get('status')}",
        f"Evaluator: {evaluator.get('path')}",
        f"Evaluator tree SHA-256: {evaluator.get('tree_sha256') or 'Not Assessed'}",
        f"Inspector SHA-256: {evaluator.get('inspector_sha256') or 'Not Assessed'}",
        f"Candidate SHA-256: {candidate.get('sha256') or 'Not Assessed'}",
        f"Evidence class: {report.get('evidence_class')}",
    ]
    transition = report.get("schema_transition", {})
    if transition.get("requested"):
        lines.append(
            "Schema transition: "
            f"{transition.get('requested_transition')} for "
            f"{transition.get('requested_release_tag')} "
            f"(activated: {transition.get('activated')})"
        )
    for profile in PROFILES:
        profile_report = report.get("profiles", {}).get(profile)
        if profile_report is not None:
            lines.append(f"{profile}: {profile_report.get('status')}")
    lines.append(f"Installed evaluator mutated: {report.get('installed_mutated')}")
    for error in report.get("errors", []):
        lines.append(f"ERROR: {error}")
    return "\n".join(lines)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    report = verify_independently(
        args.evaluator_root,
        args.archive,
        args.expected_inspector_sha256,
        args.expected_evaluator_tree_sha256,
        args.expected_candidate_sha256,
        args.bootstrap_schema_transition,
        args.bootstrap_release_tag,
    )
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True, allow_nan=False))
    else:
        print(render_report(report))
    return {"pass": 0, "fail": 2, "not_assessed": 3}.get(report.get("status"), 2)


if __name__ == "__main__":
    sys.exit(main())
