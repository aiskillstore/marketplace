#!/usr/bin/env python3
"""Path-pinned worktree and Git snapshot implementation for agy_dispatch.

This module deliberately does not import agy_dispatch.  Its caller passes the
current dispatcher globals for each invocation, preserving the dispatcher's
exception identity and its mutable test seams when two copied runtimes coexist.
"""
from __future__ import annotations

import contextlib
import hashlib
import json
import os
from pathlib import Path
import posixpath
import selectors
import shutil
import signal
import stat
import subprocess
import sys
import time
import unicodedata
from typing import Any, Mapping


READABLE_MANIFEST_MAX_ENTRIES = 100000
READABLE_MANIFEST_MAX_BYTES = 32 * 1024 * 1024
READABLE_MANIFEST_MAX_DEPTH = 128
READABLE_MANIFEST_SCAN_SECONDS = 5.0
READABLE_MANIFEST_KIND = "agy-worker-readable-path-manifest"
READABLE_MANIFEST_ALGORITHM = "agy-worker-readable-path-manifest-v1"
READABLE_MANIFEST_GIT = "/usr/bin/git"
READABLE_MANIFEST_GIT_BYTES = 1024 * 1024
READABLE_MANIFEST_GIT_SECONDS = 3.0
SELECTED_CONTENT_MAX_ENTRIES = 100000
SELECTED_CONTENT_MAX_FILE_BYTES = 128 * 1024 * 1024
SELECTED_CONTENT_MAX_TOTAL_BYTES = 512 * 1024 * 1024
SELECTED_CONTENT_SCAN_SECONDS = 30.0
RECONCILIATION_MAX_OPERATIONS = 100000


class ReadableManifestError(ValueError):
    """The provider-readable path boundary could not be observed completely."""


# Standalone preview/parser imports do not have the dispatcher dependency map.
# ``call`` replaces this binding with the dispatcher's exact exception class.
DispatchError = ReadableManifestError


def _canonical_json(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=True, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _canonical_digest(value: Any) -> str:
    """Hash the repository's newline-terminated canonical JSON encoding."""
    return hashlib.sha256(_canonical_json(value) + b"\n").hexdigest()


def _decode_manifest_path(raw: bytes) -> str:
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ReadableManifestError("path is not UTF-8") from exc


def _manifest_binding(info: os.stat_result) -> tuple[int, ...]:
    return (
        info.st_dev,
        info.st_ino,
        info.st_mode,
        info.st_nlink,
        info.st_uid,
        info.st_gid,
        info.st_size,
        info.st_mtime_ns,
        info.st_ctime_ns,
    )


def _read_bound_control_file(path: str, limit: int = 4096) -> tuple[bytes, tuple[int, ...]]:
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    before = os.lstat(path)
    if not stat.S_ISREG(before.st_mode):
        raise ReadableManifestError("control marker is not regular")
    descriptor = os.open(path, os.O_RDONLY | nofollow)
    try:
        opened = os.fstat(descriptor)
        if _manifest_binding(opened) != _manifest_binding(before):
            raise ReadableManifestError("control marker changed")
        payload = os.read(descriptor, limit + 1)
        if len(payload) > limit or os.read(descriptor, 1):
            raise ReadableManifestError("control marker is oversized")
        if _manifest_binding(os.fstat(descriptor)) != _manifest_binding(before):
            raise ReadableManifestError("control marker changed")
        return payload, _manifest_binding(before)
    finally:
        os.close(descriptor)


def _linked_worktree_authority(root: str) -> tuple[Any, ...]:
    marker_path = os.path.join(root, ".git")
    marker, marker_binding = _read_bound_control_file(marker_path)
    try:
        marker_text = marker.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ReadableManifestError("control marker is not UTF-8") from exc
    if not marker_text.endswith("\n") or marker_text.count("\n") != 1:
        raise ReadableManifestError("control marker is malformed")
    prefix = "gitdir: "
    if not marker_text.startswith(prefix):
        raise ReadableManifestError("control marker is malformed")
    gitdir = marker_text[len(prefix):-1]
    if (
        not gitdir
        or "\0" in gitdir
        or not os.path.isabs(gitdir)
        or gitdir != os.path.realpath(gitdir)
        or not os.path.isdir(gitdir)
        or os.path.islink(gitdir)
    ):
        raise ReadableManifestError("linked worktree administration is invalid")
    backpointer, backpointer_binding = _read_bound_control_file(
        os.path.join(gitdir, "gitdir")
    )
    try:
        backpointer_text = backpointer.decode("utf-8").rstrip("\n")
    except UnicodeDecodeError as exc:
        raise ReadableManifestError("linked worktree backpointer is invalid") from exc
    if backpointer_text != marker_path:
        raise ReadableManifestError("linked worktree backpointer differs")
    head, head_binding = _read_bound_control_file(os.path.join(gitdir, "HEAD"))
    try:
        head_text = head.decode("ascii").rstrip("\n")
    except UnicodeDecodeError as exc:
        raise ReadableManifestError("linked worktree HEAD is invalid") from exc
    if not head_text.startswith("ref: refs/heads/") or len(head_text) <= len("ref: refs/heads/"):
        raise ReadableManifestError("worktree is not branch-backed")
    return (
        marker_binding,
        gitdir,
        backpointer_binding,
        head_binding,
        head_text,
    )


def _stop_preview_child(child: subprocess.Popen[bytes]) -> None:
    if child.poll() is None:
        try:
            os.killpg(child.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    try:
        child.wait(timeout=1)
    except (OSError, subprocess.TimeoutExpired):
        pass


def _bounded_git_worktree_list(root: str) -> bytes:
    """Read fixed local Git registration data without prompts, hooks, or network."""

    command = [
        READABLE_MANIFEST_GIT,
        "-c", "core.hooksPath=/dev/null",
        "-c", "protocol.file.allow=never",
        "-c", "core.fsmonitor=false",
        "-C", root,
        "worktree", "list", "--porcelain", "-z",
    ]
    environment = {
        "GIT_CONFIG_GLOBAL": "/dev/null",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_OPTIONAL_LOCKS": "0",
        "GIT_PAGER": "",
        "GIT_TERMINAL_PROMPT": "0",
        "GIT_ASKPASS": "/usr/bin/false",
        "SSH_ASKPASS": "/usr/bin/false",
        "LC_ALL": "C",
    }
    child: subprocess.Popen[bytes] | None = None
    selector = selectors.DefaultSelector()
    chunks: list[bytes] = []
    observed = 0
    deadline = time.monotonic() + READABLE_MANIFEST_GIT_SECONDS
    try:
        child = subprocess.Popen(
            command,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            close_fds=True,
            env=environment,
            start_new_session=True,
        )
        if child.stdout is None:
            raise ReadableManifestError("Git registration output is unavailable")
        descriptor = child.stdout.fileno()
        os.set_blocking(descriptor, False)
        selector.register(descriptor, selectors.EVENT_READ)
        reached_eof = False
        while not reached_eof:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise ReadableManifestError("Git registration deadline exceeded")
            events = selector.select(remaining)
            if not events:
                raise ReadableManifestError("Git registration deadline exceeded")
            for key, _mask in events:
                chunk = os.read(key.fd, 65536)
                if not chunk:
                    selector.unregister(key.fd)
                    reached_eof = True
                    break
                observed += len(chunk)
                if observed > READABLE_MANIFEST_GIT_BYTES:
                    raise ReadableManifestError("Git registration output is oversized")
                chunks.append(chunk)
        remaining = deadline - time.monotonic()
        if remaining <= 0 or child.wait(timeout=remaining) != 0:
            raise ReadableManifestError("Git registration check failed")
        return b"".join(chunks)
    except (OSError, subprocess.SubprocessError) as exc:
        raise ReadableManifestError("Git registration check failed") from exc
    finally:
        selector.close()
        if child is not None:
            _stop_preview_child(child)


def _registered_worktree_authority(root: str, head_text: str) -> tuple[str, str]:
    raw = _bounded_git_worktree_list(root)
    target_records: list[dict[bytes, bytes | None]] = []
    for record_raw in raw.split(b"\0\0"):
        if not record_raw:
            continue
        fields: dict[bytes, bytes | None] = {}
        for field in record_raw.split(b"\0"):
            if not field:
                continue
            key, separator, value = field.partition(b" ")
            if key in fields:
                raise ReadableManifestError("Git registration record is ambiguous")
            fields[key] = value if separator else None
        path_raw = fields.get(b"worktree")
        if path_raw is None:
            raise ReadableManifestError("Git registration record is malformed")
        try:
            path = path_raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ReadableManifestError("Git registration path is not UTF-8") from exc
        if path == root:
            target_records.append(fields)
    if len(target_records) != 1:
        raise ReadableManifestError("worktree is not uniquely registered")
    record = target_records[0]
    head_raw = record.get(b"HEAD")
    branch_raw = record.get(b"branch")
    if (
        not isinstance(head_raw, bytes)
        or len(head_raw) not in (40, 64)
        or any(byte not in b"0123456789abcdef" for byte in head_raw)
        or not isinstance(branch_raw, bytes)
        or b"detached" in record
        or b"bare" in record
        or b"prunable" in record
    ):
        raise ReadableManifestError("worktree registration is not branch-backed")
    try:
        branch = branch_raw.decode("utf-8")
        head = head_raw.decode("ascii")
    except UnicodeDecodeError as exc:
        raise ReadableManifestError("worktree registration is invalid") from exc
    if not branch.startswith("refs/heads/") or head_text != f"ref: {branch}":
        raise ReadableManifestError("worktree registration differs from control data")
    return head, branch


def _preview_worktree_authority(root: str) -> tuple[Any, ...]:
    control = _linked_worktree_authority(root)
    registration = _registered_worktree_authority(root, control[-1])
    return control, registration


def _scan_readable_paths(root: str) -> tuple[list[dict[str, str]], tuple[Any, ...]]:
    deadline = time.monotonic() + READABLE_MANIFEST_SCAN_SECONDS
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    directory_flag = getattr(os, "O_DIRECTORY", 0)
    root_fd = os.open(root, os.O_RDONLY | directory_flag | nofollow)
    entries: list[tuple[bytes, str, str]] = []
    observations: list[tuple[Any, ...]] = []
    enumerated_count = 0

    def ensure_time() -> None:
        if time.monotonic() > deadline:
            raise ReadableManifestError("scan deadline exceeded")

    def add_entry(kind: str, relative_bytes: bytes) -> None:
        if len(entries) >= READABLE_MANIFEST_MAX_ENTRIES:
            raise ReadableManifestError("entry limit exceeded")
        if relative_bytes.count(b"/") + 1 > READABLE_MANIFEST_MAX_DEPTH:
            raise ReadableManifestError("depth limit exceeded")
        relative = _decode_manifest_path(relative_bytes)
        entries.append((relative_bytes, kind, relative))

    def walk(parent_fd: int, parent_path: str, prefix: bytes, depth: int) -> None:
        nonlocal enumerated_count
        ensure_time()
        if depth > READABLE_MANIFEST_MAX_DEPTH:
            raise ReadableManifestError("depth limit exceeded")
        before = os.fstat(parent_fd)
        if not stat.S_ISDIR(before.st_mode):
            raise ReadableManifestError("directory changed type")
        scan_fd = os.dup(parent_fd)
        try:
            with os.scandir(scan_fd) as scanned:
                children: list[tuple[bytes, str]] = []
                for entry in scanned:
                    ensure_time()
                    name = os.fsencode(entry.name)
                    if not name or b"\0" in name:
                        raise ReadableManifestError("invalid path")
                    _decode_manifest_path(name)
                    if name.lower() == b".git":
                        if not prefix and name == b".git":
                            continue
                        raise ReadableManifestError("nested Git marker")
                    enumerated_count += 1
                    if enumerated_count > READABLE_MANIFEST_MAX_ENTRIES:
                        raise ReadableManifestError("entry limit exceeded")
                    children.append((name, entry.name))
        finally:
            os.close(scan_fd)
        children.sort(key=lambda item: item[0])
        listing: list[bytes] = []
        for name, entry_name in children:
            ensure_time()
            relative = name if not prefix else prefix + b"/" + name
            listing.append(name)
            info = os.stat(entry_name, dir_fd=parent_fd, follow_symlinks=False)
            binding = _manifest_binding(info)
            full_path = os.path.join(parent_path, entry_name)
            if stat.S_ISDIR(info.st_mode):
                add_entry("directory", relative)
                child_fd = os.open(
                    entry_name,
                    os.O_RDONLY | directory_flag | nofollow,
                    dir_fd=parent_fd,
                )
                try:
                    if _manifest_binding(os.fstat(child_fd)) != binding:
                        raise ReadableManifestError("directory changed")
                    walk(child_fd, full_path, relative, depth + 1)
                    if _manifest_binding(os.fstat(child_fd)) != binding:
                        raise ReadableManifestError("directory changed")
                finally:
                    os.close(child_fd)
                observations.append((relative, "directory", binding))
            elif stat.S_ISREG(info.st_mode):
                add_entry("file", relative)
                file_fd = os.open(entry_name, os.O_RDONLY | nofollow, dir_fd=parent_fd)
                try:
                    if _manifest_binding(os.fstat(file_fd)) != binding:
                        raise ReadableManifestError("file changed")
                finally:
                    os.close(file_fd)
                if _manifest_binding(
                    os.stat(entry_name, dir_fd=parent_fd, follow_symlinks=False)
                ) != binding:
                    raise ReadableManifestError("file changed")
                observations.append((relative, "file", binding))
            elif stat.S_ISLNK(info.st_mode):
                add_entry("symlink", relative)
                target = os.readlink(entry_name, dir_fd=parent_fd)
                if not isinstance(target, str):
                    target = os.fsdecode(target)
                target.encode("utf-8")
                resolved = os.path.realpath(full_path)
                try:
                    contained = os.path.commonpath([root, resolved]) == root
                except ValueError:
                    contained = False
                if (
                    not contained
                    or not os.path.exists(resolved)
                    or any(part.casefold() == ".git" for part in Path(os.path.relpath(resolved, root)).parts)
                ):
                    raise ReadableManifestError("symlink boundary violation")
                if _manifest_binding(
                    os.stat(entry_name, dir_fd=parent_fd, follow_symlinks=False)
                ) != binding:
                    raise ReadableManifestError("symlink changed")
                observations.append((relative, "symlink", binding, target))
            else:
                raise ReadableManifestError("special node")
        after = os.fstat(parent_fd)
        if _manifest_binding(after) != _manifest_binding(before):
            raise ReadableManifestError("directory changed")
        observations.append((prefix, "listing", tuple(listing), _manifest_binding(before)))

    try:
        root_before = _manifest_binding(os.fstat(root_fd))
        walk(root_fd, root, b"", 0)
        root_after = _manifest_binding(os.fstat(root_fd))
        if root_after != root_before:
            raise ReadableManifestError("root changed")
    finally:
        os.close(root_fd)
    entries.sort(key=lambda item: item[0])
    public_entries = [{"kind": kind, "path": path} for _raw, kind, path in entries]
    return public_entries, tuple(observations)


def readable_path_manifest(workdir: str) -> dict[str, Any]:
    """Return a stable content-free provider-readable path manifest preview."""

    if (
        not workdir
        or "\0" in workdir
        or not os.path.isabs(workdir)
        or os.path.normpath(workdir) != workdir
        or os.path.realpath(workdir) != workdir
        or os.path.islink(workdir)
    ):
        raise ReadableManifestError("worktree path is not canonical")
    root_info = os.lstat(workdir)
    if not stat.S_ISDIR(root_info.st_mode):
        raise ReadableManifestError("worktree root is not a directory")
    authority_before = _preview_worktree_authority(workdir)
    first_entries, first_observation = _scan_readable_paths(workdir)
    second_entries, second_observation = _scan_readable_paths(workdir)
    authority_after = _preview_worktree_authority(workdir)
    if (
        first_entries != second_entries
        or first_observation != second_observation
        or authority_before != authority_after
        or os.path.realpath(workdir) != workdir
        or _manifest_binding(os.lstat(workdir)) != _manifest_binding(root_info)
    ):
        raise ReadableManifestError("worktree changed during preview")
    manifest = {
        "algorithm": READABLE_MANIFEST_ALGORITHM,
        "entries": first_entries,
        "entry_count": len(first_entries),
        "kind": READABLE_MANIFEST_KIND,
        "schema_version": 1,
    }
    manifest_bytes = _canonical_json(manifest)
    if len(manifest_bytes) > READABLE_MANIFEST_MAX_BYTES:
        raise ReadableManifestError("manifest byte limit exceeded")
    return {
        "bounds": {
            "max_canonical_bytes": READABLE_MANIFEST_MAX_BYTES,
            "max_depth": READABLE_MANIFEST_MAX_DEPTH,
            "max_entries": READABLE_MANIFEST_MAX_ENTRIES,
            "scan_deadline_seconds": int(READABLE_MANIFEST_SCAN_SECONDS),
        },
        "contents_read": False,
        "manifest": manifest,
        "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        "network_used": False,
        "provider_launched": False,
        "resolved_root": workdir,
    }


def _scan_readable_worktree(worktree: str | Path) -> list[dict[str, str]]:
    """Return the canonical readable manifest entries for lifecycle binding."""

    return readable_path_manifest(str(worktree))["manifest"]["entries"]


def _validate_manifest(manifest: Any) -> list[dict[str, str]]:
    """Validate and normalize a canonical readable-path entry list."""

    if not isinstance(manifest, list):
        raise ReadableManifestError("manifest entries are invalid")
    validated: list[dict[str, str]] = []
    previous: bytes | None = None
    for entry in manifest:
        if (
            not isinstance(entry, dict)
            or set(entry) != {"kind", "path"}
            or entry.get("kind") not in {"directory", "file", "symlink"}
            or not isinstance(entry.get("path"), str)
            or not entry["path"]
        ):
            raise ReadableManifestError("manifest entry is invalid")
        path = entry["path"]
        raw = path.encode("utf-8", "strict")
        if (
            b"\0" in raw
            or path.startswith("/")
            or path.endswith("/")
            or posixpath.normpath(path) != path
            or any(part.casefold() == ".git" for part in path.split("/"))
            or (previous is not None and raw <= previous)
        ):
            raise ReadableManifestError("manifest path is invalid")
        previous = raw
        validated.append({"kind": entry["kind"], "path": path})
    return validated


def _manifest_digest(manifest: Any) -> str:
    """Return the unchanged readable-manifest v1 digest."""

    entries = _validate_manifest(manifest)
    value = {
        "algorithm": READABLE_MANIFEST_ALGORITHM,
        "entries": entries,
        "entry_count": len(entries),
        "kind": READABLE_MANIFEST_KIND,
        "schema_version": 1,
    }
    raw = _canonical_json(value)
    if len(raw) > READABLE_MANIFEST_MAX_BYTES:
        raise ReadableManifestError("manifest byte limit exceeded")
    return hashlib.sha256(raw).hexdigest()


def _preview_main(argv: list[str]) -> int:
    workdir: str | None = None
    scope_path: str | None = None
    format_opt = "json"
    idx = 0
    while idx < len(argv):
        arg = argv[idx]
        if arg in ("--workdir", "--worktree"):
            if idx + 1 >= len(argv) or workdir is not None:
                print("agy-worker.sh: transmission preview unavailable", file=sys.stderr)
                return 64
            workdir = argv[idx + 1]
            idx += 2
        elif arg == "--provider-scope":
            if idx + 1 >= len(argv) or scope_path is not None:
                print("agy-worker.sh: transmission preview unavailable", file=sys.stderr)
                return 64
            scope_path = argv[idx + 1]
            idx += 2
        elif arg == "--format":
            if idx + 1 >= len(argv) or argv[idx + 1] != "json":
                print("agy-worker.sh: transmission preview unavailable", file=sys.stderr)
                return 64
            format_opt = argv[idx + 1]
            idx += 2
        else:
            print("agy-worker.sh: transmission preview unavailable", file=sys.stderr)
            return 64
    if workdir is None:
        print("agy-worker.sh: transmission preview unavailable", file=sys.stderr)
        return 64
    try:
        result = readable_path_manifest(workdir)
        if scope_path is not None:
            resolved_scope = os.path.realpath(scope_path)
            if not os.path.isabs(resolved_scope) or os.path.islink(scope_path):
                raise ReadableManifestError("provider scope path is invalid")
            descriptor = os.open(
                resolved_scope, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0),
            )
            try:
                before = os.fstat(descriptor)
                if (
                    not stat.S_ISREG(before.st_mode)
                    or before.st_uid != os.geteuid()
                    or before.st_nlink != 1
                ):
                    raise ReadableManifestError("provider scope authority is invalid")
                chunks: list[bytes] = []
                total = 0
                while total <= 512 * 1024:
                    chunk = os.read(descriptor, min(65536, 512 * 1024 + 1 - total))
                    if not chunk:
                        break
                    chunks.append(chunk)
                    total += len(chunk)
                after = os.fstat(descriptor)
            finally:
                os.close(descriptor)
            named = os.lstat(resolved_scope)
            if (
                total > 512 * 1024
                or _manifest_binding(before) != _manifest_binding(after)
                or _manifest_binding(after) != _manifest_binding(named)
            ):
                raise ReadableManifestError("provider scope changed during preview")
            raw_scope = b"".join(chunks)
            scope = _parse_provider_scope(raw_scope)
            _validate_scope_against_worktree(scope, workdir, result["manifest"]["entries"])
            selected_manifest = _build_selected_content_manifest(workdir, scope)
            selected_sha = _selected_content_digest(selected_manifest)
            policy_sha = _canonical_digest(scope)
            manifest_sha = result["manifest_sha256"]
            transmission_sha = _compute_transmission_sha256(policy_sha, manifest_sha, selected_sha)
            result["provider_scope"] = scope
            result["contents_read"] = True
            result["policy_sha256"] = policy_sha
            result["selected_content_manifest"] = selected_manifest
            result["selected_content_sha256"] = selected_sha
            result["transmission_sha256"] = transmission_sha
    except (OSError, UnicodeError, ValueError, OverflowError, RecursionError):
        print("agy-worker.sh: transmission preview unavailable", file=sys.stderr)
        return 20
    sys.stdout.buffer.write(_canonical_json(result) + b"\n")
    return 0


def call(name: str, dependencies: Mapping[str, Any], *args: Any, **kwargs: Any) -> Any:
    """Run one façade target with its caller's current dependency bindings."""
    for key, value in dependencies.items():
        # Keep the invoked implementation local so a façade cannot recurse
        # into itself. Other implementation names are dependencies: callers
        # intentionally monkeypatch them in controller and regression tests.
        if not key.startswith("__") and key != name:
            globals()[key] = value
    return _IMPLEMENTATION_DEFAULTS[name](*args, **kwargs)


class _MarkerPreflightLimit(Exception):
    """The marker-only scan hit its documented bounded entry cap."""


class _UnsupportedWorktreeError(ValueError):
    """A known repository form cannot produce an accepted snapshot."""


class _ResolveUndoPresentError(_UnsupportedWorktreeError):
    """A valid, non-empty REUC observation is present in the worktree index."""


def _marker_only_preflight(root_fd: int, *, deadline: float | None = None) -> bool:
    """Reject root aliases and nested Git markers without opening their contents.

    Filesystems such as the usual macOS volume can resolve ``.GIT`` through a
    lookup for ``.git``.  Authority checks must use the directory entry's
    actual bytes, rather than a later pathname lookup.  This intentionally
    walks only no-follow directory descriptors and returns before reading,
    opening, or resolving a marker itself.  The later complete boundary or
    manifest scan remains the timing-consistency observation.
    """
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    directory = getattr(os, "O_DIRECTORY", 0)
    entries_seen = 0

    def binding(info: os.stat_result) -> tuple[int, ...]:
        return (
            info.st_dev, info.st_ino, info.st_mode, info.st_nlink,
            info.st_uid, info.st_gid, info.st_size, info.st_mtime_ns, info.st_ctime_ns,
        )

    def walk(parent_fd: int, *, is_root: bool = False) -> bool:
        nonlocal entries_seen
        if deadline is not None and time.monotonic() >= deadline:
            return False
        try:
            before_directory = os.fstat(parent_fd)
            if not stat.S_ISDIR(before_directory.st_mode):
                return False
        except OSError:
            return False
        scan_fd = -1
        try:
            # Keep ownership of a duplicate: the traversal must not depend on
            # a pathname after its parent was bound.
            scan_fd = os.dup(parent_fd)
            with os.scandir(scan_fd) as scanned:
                for entry in scanned:
                    if deadline is not None and time.monotonic() >= deadline:
                        return False
                    raw_name = os.fsencode(entry.name)
                    if not raw_name or b"\0" in raw_name:
                        return False
                    if raw_name.lower() == b".git":
                        # An exact root spelling is the only marker permitted;
                        # its normal directory or linked-worktree file binding
                        # is performed by the caller after this preflight.
                        if is_root and raw_name == b".git":
                            continue
                        return False
                    entries_seen += 1
                    if entries_seen > MAX_BOUNDARY_ENTRIES:
                        raise _MarkerPreflightLimit
                    try:
                        info = os.stat(entry.name, dir_fd=parent_fd, follow_symlinks=False)
                    except OSError:
                        return False
                    if not stat.S_ISDIR(info.st_mode):
                        continue
                    try:
                        child_fd = os.open(
                            entry.name, os.O_RDONLY | directory | nofollow, dir_fd=parent_fd,
                        )
                    except OSError:
                        return False
                    try:
                        if binding(os.fstat(child_fd)) != binding(info) or not walk(child_fd):
                            return False
                        if binding(os.fstat(child_fd)) != binding(info):
                            return False
                    except OSError:
                        return False
                    finally:
                        os.close(child_fd)
        except OSError:
            return False
        finally:
            if scan_fd >= 0:
                os.close(scan_fd)
        try:
            return binding(os.fstat(parent_fd)) == binding(before_directory)
        except OSError:
            return False

    return walk(root_fd, is_root=True)


def _resolved_path_is_git_administration(root: str, resolved: str) -> bool:
    """Return whether a contained resolved path enters a Git admin boundary."""
    try:
        if os.path.commonpath([root, resolved]) != root:
            return False
    except ValueError:
        return False
    relative = os.path.relpath(resolved, root)
    return any(part.lower() == ".git" for part in relative.split(os.sep))


def _worktree_symlink_boundary(workdir: str) -> bool:
    """Boundedly reject a link whose resolved target leaves ``workdir``.

    This is intentionally a no-follow directory walk, not a worktree snapshot:
    link targets are resolved only to check containment and link directories are
    never traversed.  The controller invokes it for every provider workflow.
    """
    root = os.path.realpath(workdir)
    pending = [root]
    count = 0
    try:
        while pending:
            current = pending.pop()
            with os.scandir(current) as entries:
                for entry in entries:
                    raw_name = os.fsencode(entry.name)
                    if raw_name.lower() == b".git":
                        # The root marker is controller metadata, not worktree
                        # content.  Nested Git administration is handled by
                        # the existing marker preflight.
                        if current == root and raw_name == b".git":
                            continue
                        return False
                    count += 1
                    if count > MAX_BOUNDARY_ENTRIES:
                        return False
                    if entry.is_symlink():
                        # `mktemp` commonly returns /var/... on macOS while
                        # realpath canonicalizes the worktree to /private/var.
                        # Resolve before containment so an internal link is not
                        # falsely treated as an escape; chained escapes remain
                        # outside the canonical root.
                        resolved = os.path.realpath(entry.path)
                        try:
                            contained = os.path.commonpath([root, resolved]) == root
                        except ValueError:
                            contained = False
                        if not contained or not os.path.exists(resolved):
                            return False
                        if _resolved_path_is_git_administration(root, resolved):
                            # A contained alias into the root marker or a
                            # nested Git administration area still changes
                            # repository authority; containment alone is not
                            # sufficient for lifecycle/provider safety.
                            return False
                    elif entry.is_dir(follow_symlinks=False):
                        pending.append(entry.path)
    except OSError:
        return False
    return True


def _worktree_git_admin_alias_boundary(workdir: str) -> bool:
    """Reject only contained symlink aliases into a Git admin boundary.

    Snapshotting intentionally hashes outward symlink target bytes rather than
    following them, so it cannot reuse the provider/lifecycle scope boundary.
    This narrower scan preserves that evidence behavior while refusing a link
    that aliases the worktree's own Git administration.
    """
    root = os.path.realpath(workdir)
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    directory = getattr(os, "O_DIRECTORY", 0)
    entries_seen = 0

    def binding(info: os.stat_result) -> tuple[int, ...]:
        return (
            info.st_dev, info.st_ino, info.st_mode, info.st_nlink,
            info.st_uid, info.st_gid, info.st_size, info.st_mtime_ns, info.st_ctime_ns,
        )

    def walk(parent_fd: int, parent_path: str, *, is_root: bool = False) -> bool:
        nonlocal entries_seen
        try:
            before_directory = os.fstat(parent_fd)
            if not stat.S_ISDIR(before_directory.st_mode):
                return False
        except OSError:
            return False
        scan_fd = -1
        try:
            # Retain the directory descriptor across enumeration so fixture and
            # runtime behavior cannot depend on a mutable pathname.
            scan_fd = os.dup(parent_fd)
            with os.scandir(scan_fd) as entries:
                for entry in entries:
                    raw_name = os.fsencode(entry.name)
                    if not raw_name or b"\0" in raw_name:
                        return False
                    if raw_name.lower() == b".git":
                        if is_root and raw_name == b".git":
                            continue
                        return False
                    entries_seen += 1
                    if entries_seen > MAX_BOUNDARY_ENTRIES:
                        return False
                    try:
                        info = os.stat(
                            entry.name, dir_fd=parent_fd, follow_symlinks=False,
                        )
                    except OSError:
                        return False
                    if stat.S_ISLNK(info.st_mode):
                        try:
                            resolved = os.path.realpath(
                                os.path.join(parent_path, entry.name),
                            )
                            after_link = os.stat(
                                entry.name, dir_fd=parent_fd, follow_symlinks=False,
                            )
                        except OSError:
                            return False
                        if binding(info) != binding(after_link):
                            return False
                        if _resolved_path_is_git_administration(root, resolved):
                            return False
                        continue
                    if not stat.S_ISDIR(info.st_mode):
                        continue
                    try:
                        child_fd = os.open(
                            entry.name, os.O_RDONLY | directory | nofollow, dir_fd=parent_fd,
                        )
                    except OSError:
                        return False
                    try:
                        if (
                            binding(os.fstat(child_fd)) != binding(info)
                            or not walk(child_fd, os.path.join(parent_path, entry.name))
                            or binding(os.fstat(child_fd)) != binding(info)
                        ):
                            return False
                    except OSError:
                        return False
                    finally:
                        os.close(child_fd)
        except OSError:
            return False
        finally:
            if scan_fd >= 0:
                os.close(scan_fd)
        try:
            return binding(os.fstat(parent_fd)) == binding(before_directory)
        except OSError:
            return False

    root_fd = -1
    try:
        root_fd = os.open(root, os.O_RDONLY | directory | nofollow)
        root_info = os.fstat(root_fd)
        if (
            not stat.S_ISDIR(root_info.st_mode)
            or binding(os.lstat(root)) != binding(root_info)
        ):
            return False
        return walk(root_fd, root, is_root=True)
    except OSError:
        return False
    finally:
        if root_fd >= 0:
            os.close(root_fd)


def _project_boundary(workdir: str) -> dict[str, Any]:
    root = os.path.realpath(workdir)
    if root != workdir:
        raise DispatchError("project worktree is no longer canonical")
    root_fd = -1
    try:
        root_fd = os.open(
            root, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0),
        )
        root_info = os.fstat(root_fd)
        if (
            not stat.S_ISDIR(root_info.st_mode)
            or _identity(os.lstat(root)) != _identity(root_info)
        ):
            raise DispatchError("project worktree cannot be inspected")
        try:
            marker_preflight = _marker_only_preflight(root_fd)
        except _MarkerPreflightLimit as exc:
            raise DispatchError("project worktree boundary scan is too large") from exc
        if not marker_preflight:
            raise DispatchError("project worktree has nested Git administration")
    except DispatchError:
        raise
    except OSError as exc:
        raise DispatchError("project worktree cannot be inspected") from exc
    finally:
        if root_fd >= 0:
            os.close(root_fd)
    marker = Path(root) / ".git"
    descriptor = -1
    try:
        descriptor = os.open(marker, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    except OSError as exc:
        raise DispatchError("project worktree has no Git marker") from exc
    try:
        marker_info = os.fstat(descriptor)
        if (
            not stat.S_ISREG(marker_info.st_mode)
            or marker_info.st_uid != os.getuid()
            or marker_info.st_nlink != 1
        ):
            raise DispatchError("project Git marker must be one owner-owned linked-worktree file")
        if marker_info.st_size > 4096:
            raise DispatchError("project Git marker is oversized")
        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = os.read(descriptor, 4097 - total)
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
            if total > 4096:
                raise DispatchError("project Git marker is oversized")
        after = os.fstat(descriptor)
        if after.st_size > 4096:
            raise DispatchError("project Git marker is oversized")
    except DispatchError:
        raise
    except OSError as exc:
        raise DispatchError("project Git marker is unavailable") from exc
    finally:
        os.close(descriptor)
    try:
        named = marker.lstat()
    except OSError as exc:
        raise DispatchError("project Git marker identity changed") from exc
    raw = b"".join(chunks)
    if (
        not stat.S_ISREG(after.st_mode)
        or after.st_uid != os.getuid()
        or after.st_nlink != 1
        or not stat.S_ISREG(named.st_mode)
        or named.st_uid != os.getuid()
        or named.st_nlink != 1
        or _identity(marker_info) != _identity(after)
        or _identity(after) != _identity(named)
        or marker_info.st_size != after.st_size
        or after.st_size != named.st_size
        or len(raw) != after.st_size
        or marker_info.st_mtime_ns != after.st_mtime_ns
        or marker_info.st_ctime_ns != after.st_ctime_ns
        or after.st_mtime_ns != named.st_mtime_ns
        or after.st_ctime_ns != named.st_ctime_ns
    ):
        raise DispatchError("project Git marker identity changed")
    marker_record: dict[str, Any] = {
        "kind": "file", "identity": list(_identity(after)), "sha256": digest(raw),
    }
    if not _worktree_symlink_boundary(root):
        raise DispatchError("project worktree has an outward symlink")
    return marker_record


def _safe_git_owner_mode(metadata: os.stat_result, *, directory: bool) -> bool:
    """Keep snapshot plumbing inside the documented local-owner/root TCB."""
    mode = stat.S_IMODE(metadata.st_mode)
    if metadata.st_uid not in {os.geteuid(), 0}:
        return False
    if not directory and metadata.st_mode & (stat.S_ISUID | stat.S_ISGID):
        return False
    if not (mode & 0o022):
        return True
    return bool(
        directory and metadata.st_uid == 0 and (mode & stat.S_ISVTX)
        and (mode & 0o022) == 0o022
    )


def _safe_git_executable() -> tuple[str, dict[str, Any]] | None:
    """Resolve Git through a bounded safe ownership and symlink-chain check."""
    candidate = shutil.which("git")
    if not candidate:
        return None

    def authority(info: os.stat_result) -> tuple[int, int, int, int, int]:
        return info.st_dev, info.st_ino, info.st_mode, info.st_uid, info.st_gid

    def target_binding(info: os.stat_result) -> tuple[int, ...]:
        return (
            info.st_dev, info.st_ino, info.st_mode, info.st_nlink,
            info.st_uid, info.st_gid, info.st_size, info.st_mtime_ns, info.st_ctime_ns,
        )

    def bind(selected: str) -> tuple[str, dict[str, Any]] | None:
        """Bind one exact executable spelling without relaxing path authority."""
        selected = os.path.abspath(selected)
        parts = list(Path(selected).parts[1:])
        current = Path(os.sep)
        chain: list[tuple[tuple[int, int, int, int, int], str]] = []
        components: list[tuple[int, int, int, int, int]] = []
        seen: set[tuple[int, int]] = set()
        try:
            for _ in range(128):
                if not parts:
                    break
                part = parts.pop(0)
                if part in {"", ".", ".."}:
                    return None
                current /= part
                metadata = os.lstat(current)
                if stat.S_ISLNK(metadata.st_mode):
                    if metadata.st_uid not in {os.geteuid(), 0}:
                        return None
                    identity = (metadata.st_dev, metadata.st_ino)
                    if identity in seen or len(chain) >= 16:
                        return None
                    seen.add(identity)
                    target = os.readlink(current)
                    chain.append((authority(metadata), digest(os.fsencode(target))))
                    target_path = Path(target if os.path.isabs(target) else current.parent / target)
                    target_path = Path(os.path.normpath(str(target_path)))
                    if not target_path.is_absolute():
                        return None
                    parts = list(target_path.parts[1:]) + parts
                    current = Path(os.sep)
                    continue
                if parts:
                    if not stat.S_ISDIR(metadata.st_mode) or not _safe_git_owner_mode(metadata, directory=True):
                        return None
                    components.append(authority(metadata))
                    if len(components) > 128:
                        return None
                    continue
                if (
                    not stat.S_ISREG(metadata.st_mode)
                    or not _safe_git_owner_mode(metadata, directory=False)
                    or not (stat.S_IMODE(metadata.st_mode) & 0o111)
                ):
                    return None
                return str(current), {
                    "candidate": selected,
                    "target": target_binding(metadata),
                    "chain": tuple(chain),
                    "components": tuple(components),
                }
        except OSError:
            return None
        return None

    selected = os.path.abspath(candidate)
    bound = bind(selected)
    if bound is not None:
        return bound
    # GitHub's Apple-Silicon image can expose a group-writable Homebrew
    # launcher before the root-owned system Git.  Do not widen Homebrew's
    # authority: when that exact launcher fails the existing no-follow bind,
    # use only the fixed platform Git path and bind it by the same rules.
    if sys.platform == "darwin" and selected == "/opt/homebrew/bin/git":
        return bind("/usr/bin/git")
    return None


def _confirm_safe_git_executable(
    executable: str, expected: dict[str, Any],
) -> bool:
    current = _safe_git_executable()
    return current is not None and current[0] == executable and current[1] == expected


def _safe_git_is_outside_worktree(executable: str, worktree_root: str) -> bool:
    """Keep Git probes outside a repository-controlled executable boundary."""
    try:
        root = os.path.realpath(worktree_root)
        target = os.path.realpath(executable)
        if not os.path.isabs(root) or not os.path.isabs(target):
            return False
        return os.path.commonpath((root, target)) != root
    except (OSError, ValueError):
        # Containment is an authority decision; an unavailable or incomparable
        # path must not surface its spelling or authorize a Git subprocess.
        return False


def _stable_git_authority(info: os.stat_result) -> dict[str, int]:
    """Serialize only durable no-follow authority facts for V9 state.

    Callers may use fuller observations while holding descriptors to catch a
    race.  Persisting timestamps, sizes, or link counts would make ordinary
    Git maintenance and worktree activity look like a boundary replacement.
    """
    return {
        "dev": info.st_dev,
        "ino": info.st_ino,
        "type": stat.S_IFMT(info.st_mode),
        "mode": stat.S_IMODE(info.st_mode),
        "uid": info.st_uid,
        "gid": info.st_gid,
    }


def _full_stat_binding(info: os.stat_result) -> tuple[int, ...]:
    """Keep transient scan consistency separate from persisted authority."""
    return (
        info.st_dev, info.st_ino, info.st_mode, info.st_nlink,
        info.st_uid, info.st_gid, info.st_size, info.st_mtime_ns,
        info.st_ctime_ns,
    )


def _bound_git_worktree_root(
    raw: bytes, canonical_root: str, root_binding: tuple[int, ...],
) -> bool:
    """Accept only Git's exact bound-root spelling or macOS's /var alias.

    Git may report the documented ``/var`` spelling while Python canonicalizes
    the same macOS directory as ``/private/var``.  The alias is accepted only
    after strict UTF-8 framing and a no-follow full-stat binding prove that the
    final named directory is the held root.  This is deliberately narrower
    than ``realpath``: arbitrary symlink aliases and lexical path variations
    remain a failed boundary.
    """
    if (
        type(raw) is not bytes
        or type(canonical_root) is not str
        or type(root_binding) is not tuple
        or len(root_binding) != 9
        or any(type(value) is not int for value in root_binding)
        or not raw.endswith(b"\n")
        or raw.count(b"\n") != 1
        or b"\0" in raw
    ):
        return False
    try:
        path_text = raw[:-1].decode("utf-8", "strict")
    except UnicodeDecodeError:
        return False
    if not path_text or not os.path.isabs(path_text) or "\0" in path_text:
        return False
    try:
        if MODEL_SELECTION._canonical_executable_path(path_text) != (
            MODEL_SELECTION._canonical_executable_path(canonical_root)
        ):
            return False
        named = os.lstat(os.fsencode(path_text))
        if not stat.S_ISDIR(named.st_mode) or stat.S_ISLNK(named.st_mode):
            return False
        descriptor = os.open(
            os.fsencode(path_text), os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
            | getattr(os, "O_NOFOLLOW", 0),
        )
        try:
            opened = os.fstat(descriptor)
        finally:
            os.close(descriptor)
        after = os.lstat(os.fsencode(path_text))
    except OSError:
        return False
    return (
        _full_stat_binding(named) == root_binding
        and _full_stat_binding(opened) == root_binding
        and _full_stat_binding(after) == root_binding
    )


_FIXED_GIT_READ_ARGV = {
    ("rev-parse", "--is-inside-work-tree"),
    ("rev-parse", "--show-toplevel"),
    ("rev-parse", "--show-object-format"),
    ("rev-parse", "--absolute-git-dir"),
    ("rev-parse", "--git-common-dir"),
    ("rev-parse", "--git-path", "index"),
    ("rev-parse", "--verify", "-q", "HEAD^{tree}"),
    (
        "config", "--local", "--no-includes", "--get-regexp",
        "^(extensions\\.partialclone|remote\\..*\\.promisor)$",
    ),
    ("config", "--bool", "--get", "core.sparseCheckout"),
    ("ls-files", "-v", "-z"),
    ("ls-files", "--stage", "-z"),
    ("ls-files", "--debug", "-z"),
    ("ls-files", "--resolve-undo", "-z"),
    ("ls-files", "-z", "--others", "--exclude-standard"),
    ("ls-files", "-z", "--others", "--ignored", "--exclude-standard"),
    ("cat-file", "--batch"),
}


def _fixed_git_read_argv(arguments: list[str]) -> bool:
    """Accept only the read-only plumbing shapes owned by this module."""
    value = tuple(arguments)
    if value in _FIXED_GIT_READ_ARGV:
        return True
    return bool(
        len(value) == 4 and value[:3] == ("ls-tree", "-r", "-z")
        and re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", value[3]) is not None
    )


def _bound_git_directory(path: str, expected_binding: tuple[int, ...]) -> bool:
    """Revalidate one no-follow Git-directory authority before a pinned read."""
    if (
        type(path) is not str
        or not path
        or not os.path.isabs(path)
        or "\0" in path
        or type(expected_binding) is not tuple
        or len(expected_binding) != 9
        or any(type(value) is not int for value in expected_binding)
    ):
        return False
    named_path = os.path.abspath(path)
    try:
        named = os.lstat(os.fsencode(named_path))
        if not stat.S_ISDIR(named.st_mode) or stat.S_ISLNK(named.st_mode):
            return False
        canonical_path = os.path.realpath(named_path)
        if MODEL_SELECTION._canonical_executable_path(canonical_path) != (
            MODEL_SELECTION._canonical_executable_path(named_path)
        ):
            return False
        descriptor = os.open(
            os.fsencode(named_path), os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
            | getattr(os, "O_NOFOLLOW", 0),
        )
        try:
            opened = os.fstat(descriptor)
        finally:
            os.close(descriptor)
        after = os.lstat(os.fsencode(named_path))
    except OSError:
        return False
    return (
        _full_stat_binding(named) == expected_binding
        and _full_stat_binding(opened) == expected_binding
        and _full_stat_binding(after) == expected_binding
    )


class _BoundGitReadArguments(list[str]):
    """Fixed Git arguments paired with the snapshot's private directory proof."""

    def __init__(self, arguments: list[str], git_directory: tuple[str, tuple[int, ...]]) -> None:
        super().__init__(arguments)
        self.git_directory = git_directory


def _bounded_git_read(
    executable: str, executable_authority: dict[str, Any], root: str,
    arguments: list[str], *, deadline: float, payload: bytes = b"",
    allowed: tuple[int, ...] = (0,), stdout_limit: int | None = None,
) -> tuple[int, bytes] | None:
    """Run one allowlisted Git read under a bounded, owned process group.

    A private supervisor remains the session leader after Git exits, so the
    group identity is still signalable while a Git descendant holds stdout or
    stderr open.  Both streams are consumed incrementally with hard caps; all
    exits kill the group before a bounded reap and close every parent pipe.
    """
    if (
        not _fixed_git_read_argv(arguments)
        or not isinstance(payload, bytes)
        or len(payload) > MAX_STREAM_BYTES
        or not allowed
        or any(type(code) is not int or not (0 <= code <= 255) for code in allowed)
    ):
        return None
    output_limit = MAX_STREAM_BYTES if stdout_limit is None else stdout_limit
    if type(output_limit) is not int or not (0 <= output_limit <= MAX_STREAM_BYTES):
        return None
    git_directory = None
    if type(arguments) is _BoundGitReadArguments:
        git_directory = arguments.git_directory
        if (
            type(git_directory) is not tuple
            or len(git_directory) != 2
        ):
            return None
    git_options = () if git_directory is None else (
        f"--git-dir={git_directory[0]}", f"--work-tree={root}",
    )
    target_binding = tuple(executable_authority.get("target", ()))
    if len(target_binding) != 9:
        return None

    def executable_is_bound() -> bool:
        try:
            return bool(
                _confirm_safe_git_executable(executable, executable_authority)
                and _full_stat_binding(os.lstat(executable)) == target_binding
            )
        except OSError:
            return False

    def git_directory_is_bound() -> bool:
        return git_directory is None or _bound_git_directory(*git_directory)

    if not executable_is_bound() or time.monotonic() >= deadline:
        return None
    environment = os.environ.copy()
    for key in tuple(environment):
        if key.startswith("GIT_"):
            environment.pop(key)
    environment.update({
        "GIT_OPTIONAL_LOCKS": "0",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_NO_LAZY_FETCH": "1",
        "GIT_NO_REPLACE_OBJECTS": "1",
        "GIT_TERMINAL_PROMPT": "0",
        "GIT_PAGER": "cat",
        "GIT_EXTERNAL_DIFF": "",
    })

    status_read = status_write = control_read = control_write = -1
    payload_read = payload_write = -1
    process: subprocess.Popen[bytes] | None = None
    launched = False
    try:
        status_read, status_write = os.pipe()
        control_read, control_write = os.pipe()
        payload_read, payload_write = os.pipe()
        # The supervisor owns the process group and deliberately outlives its
        # Git child.  Closing its copies of both output streams means any open
        # pipe after Git exits belongs to a descendant that the group kill must
        # close, rather than to the supervisor itself.
        supervisor = (
            'status_fd=$1; control_fd=$2; payload_fd=$3; shift 3; '
            '"$@" <&"$payload_fd" & child=$!; exec 1>&- 2>&-; '
            'wait "$child"; code=$?; printf "%s\\n" "$code" >&"$status_fd"; '
            'IFS= read -r _ <&"$control_fd"; exit "$code"'
        )
        if not executable_is_bound() or not git_directory_is_bound() or time.monotonic() >= deadline:
            return None
        process = subprocess.Popen(
            [
                "/bin/sh", "-c", supervisor, "bounded-git-supervisor",
                str(status_write), str(control_read), str(payload_read),
                executable, "-C", root, "-c", "core.fsmonitor=false",
                "-c", "core.hooksPath=/dev/null", *git_options, *arguments,
            ],
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, env=environment,
            pass_fds=(status_write, control_read, payload_read),
            start_new_session=True,
        )
        launched = True
    except OSError:
        return None
    finally:
        for descriptor in (status_write, control_read, payload_read):
            if descriptor >= 0:
                os.close(descriptor)
        if not launched:
            for descriptor in (status_read, control_write, payload_write):
                if descriptor >= 0:
                    os.close(descriptor)
            status_read = control_write = payload_write = -1

    selector = selectors.DefaultSelector()
    output = bytearray()
    diagnostic_bytes = 0
    status = bytearray()
    sent = 0
    group_terminated = False
    reaped = False
    status_code: int | None = None
    try:
        assert process is not None
        assert process.stdout is not None and process.stderr is not None
        for stream in (process.stdout, process.stderr):
            os.set_blocking(stream.fileno(), False)
            selector.register(stream, selectors.EVENT_READ)
        os.set_blocking(status_read, False)
        selector.register(status_read, selectors.EVENT_READ)
        if payload:
            os.set_blocking(payload_write, False)
            selector.register(payload_write, selectors.EVENT_WRITE)
        else:
            os.close(payload_write)
            payload_write = -1
        while selector.get_map():
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return None
            ready = selector.select(remaining)
            if not ready:
                return None
            for key, events in ready:
                if events & selectors.EVENT_READ:
                    if key.fileobj == status_read:
                        piece = os.read(status_read, 33 - len(status))
                        if not piece:
                            return None
                        status.extend(piece)
                        if len(status) > 32 or b"\n" not in status:
                            continue
                        if (
                            status.count(b"\n") != 1 or not status.endswith(b"\n")
                            or not status[:-1].isdigit()
                        ):
                            return None
                        status_code = int(status[:-1])
                        selector.unregister(status_read)
                        os.close(status_read)
                        status_read = -1
                    elif key.fileobj is process.stdout:
                        amount = min(65536, output_limit + 1 - len(output))
                        piece = os.read(process.stdout.fileno(), amount)
                        if not piece:
                            selector.unregister(process.stdout)
                        else:
                            output.extend(piece)
                            if len(output) > output_limit:
                                return None
                    else:
                        amount = min(65536, MAX_STREAM_BYTES + 1 - diagnostic_bytes)
                        piece = os.read(process.stderr.fileno(), amount)
                        if not piece:
                            selector.unregister(process.stderr)
                        else:
                            diagnostic_bytes += len(piece)
                            if diagnostic_bytes > MAX_STREAM_BYTES:
                                return None
                if events & selectors.EVENT_WRITE:
                    if sent == len(payload):
                        selector.unregister(key.fileobj)
                        os.close(payload_write)
                        payload_write = -1
                    else:
                        sent += os.write(payload_write, payload[sent:])
        if status_code is None or not executable_is_bound():
            return None
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            return None
        group_terminated = True
        process.wait(timeout=TERM_GRACE)
        reaped = True
        if status_code not in allowed or not executable_is_bound():
            return None
        return status_code, bytes(output)
    except (OSError, subprocess.SubprocessError):
        return None
    finally:
        selector.close()
        if control_write >= 0:
            # Unblock an intact supervisor before the final group/reap guard.
            os.close(control_write)
            control_write = -1
        if payload_write >= 0:
            os.close(payload_write)
            payload_write = -1
        if process is not None and not group_terminated:
            with contextlib.suppress(ProcessLookupError, PermissionError):
                os.killpg(process.pid, signal.SIGKILL)
        try:
            if process is not None and not reaped:
                process.wait(timeout=TERM_GRACE)
        except subprocess.SubprocessError:
            pass
        if status_read >= 0:
            os.close(status_read)
        if process is not None:
            for stream in (process.stdout, process.stderr):
                if stream is not None and not stream.closed:
                    stream.close()


def _git_boundary_identity(workdir: str) -> dict[str, Any] | None:
    """Return the V9 no-follow Git administration boundary for ``workdir``.

    This intentionally records repository *authority*, not repository state:
    no index, HEAD, ref, object, worktree-file, timestamp, directory-size, or
    link-count data reaches the returned mapping.  It is shared by the root
    binder and the candidate/worktree scanner, so those paths use one stable
    definition of a repository boundary.
    """
    root_fd = -1
    try:
        if not os.path.isabs(workdir):
            return None
        root = os.path.realpath(workdir)
        if MODEL_SELECTION._canonical_executable_path(root) != (
            MODEL_SELECTION._canonical_executable_path(workdir)
        ):
            return None
        named_root = os.lstat(workdir)
        if not stat.S_ISDIR(named_root.st_mode) or stat.S_ISLNK(named_root.st_mode):
            return None
        root_fd = os.open(
            os.fsencode(workdir),
            os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0),
        )
        opened_root = os.fstat(root_fd)
        root_binding = _full_stat_binding(opened_root)
        if _full_stat_binding(named_root) != root_binding:
            return None
        deadline = time.monotonic() + 5.0
        try:
            if not _marker_only_preflight(root_fd, deadline=deadline):
                return None
        except _MarkerPreflightLimit:
            return None

        def marker() -> dict[str, Any] | None:
            """Open the exact root marker once, never following it."""
            descriptor = -1
            try:
                before = os.stat(".git", dir_fd=root_fd, follow_symlinks=False)
                if stat.S_ISDIR(before.st_mode):
                    kind = "directory"
                    descriptor = os.open(
                        ".git", os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
                        | getattr(os, "O_NOFOLLOW", 0), dir_fd=root_fd,
                    )
                    payload_sha = None
                    payload_size = 0
                elif stat.S_ISREG(before.st_mode) and before.st_size <= 8192:
                    kind = "file"
                    descriptor = os.open(
                        ".git", os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0), dir_fd=root_fd,
                    )
                    chunks: list[bytes] = []
                    total = 0
                    while True:
                        piece = os.read(descriptor, min(8193 - total, 8192))
                        if not piece:
                            break
                        chunks.append(piece)
                        total += len(piece)
                        if total > 8192:
                            return None
                    payload_sha = digest(b"".join(chunks))
                    payload_size = total
                else:
                    return None
                opened = os.fstat(descriptor)
                after = os.stat(".git", dir_fd=root_fd, follow_symlinks=False)
            except OSError:
                return None
            finally:
                if descriptor >= 0:
                    os.close(descriptor)
            if (
                _full_stat_binding(before) != _full_stat_binding(opened)
                or _full_stat_binding(opened) != _full_stat_binding(after)
                or (kind == "directory" and not stat.S_ISDIR(opened.st_mode))
                or (kind == "file" and (
                    not stat.S_ISREG(opened.st_mode)
                    or payload_sha is None
                    or opened.st_size != payload_size
                ))
            ):
                return None
            return {
                "kind": kind,
                "authority": _stable_git_authority(opened),
                "content_sha256": payload_sha,
            }

        initial_marker = marker()
        if initial_marker is None:
            return None
        safe_git = _safe_git_executable()
        if safe_git is None:
            return None
        executable, executable_authority = safe_git
        if not _safe_git_is_outside_worktree(executable, root):
            # Repository-controlled programs are outside the read-only probe
            # authority even when their mode and parent ownership look safe.
            return None

        def read_plumbing(arguments: list[str]) -> bytes | None:
            """Use fixed read-only plumbing with the snapshot's Git guards."""
            completed = _bounded_git_read(
                executable, executable_authority, root, arguments,
                deadline=deadline,
            )
            return None if completed is None else completed[1]

        def one_line(raw: bytes) -> str | None:
            if not raw.endswith(b"\n") or raw.count(b"\n") != 1 or b"\0" in raw:
                return None
            try:
                text = os.fsdecode(raw[:-1])
            except UnicodeError:
                return None
            return text if text else None

        def directory(
            path_text: str, *, allow_root_relative: bool = False,
        ) -> tuple[str, dict[str, int]] | None:
            """Bind a direct Git authority, allowing only macOS's /var alias."""
            if not os.path.isabs(path_text) and not allow_root_relative:
                return None
            named_path = os.path.abspath(
                path_text if os.path.isabs(path_text) else os.path.join(root, path_text)
            )
            try:
                named = os.lstat(os.fsencode(named_path))
                if not stat.S_ISDIR(named.st_mode) or stat.S_ISLNK(named.st_mode):
                    return None
                resolved_path = os.path.realpath(named_path)
                # ``realpath`` may change only macOS's documented /var
                # spelling.  An arbitrary outward symlink remains a boundary
                # failure even if its target happens to be a Git directory.
                if MODEL_SELECTION._canonical_executable_path(resolved_path) != (
                    MODEL_SELECTION._canonical_executable_path(named_path)
                ):
                    return None
                descriptor = os.open(
                    os.fsencode(named_path), os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
                    | getattr(os, "O_NOFOLLOW", 0),
                )
                try:
                    opened = os.fstat(descriptor)
                finally:
                    os.close(descriptor)
                after = os.lstat(os.fsencode(named_path))
            except OSError:
                return None
            if (
                _full_stat_binding(named) != _full_stat_binding(opened)
                or _full_stat_binding(opened) != _full_stat_binding(after)
            ):
                return None
            return resolved_path, _stable_git_authority(opened)

        inside = read_plumbing(["rev-parse", "--is-inside-work-tree"])
        top_level = read_plumbing(["rev-parse", "--show-toplevel"])
        object_format = read_plumbing(["rev-parse", "--show-object-format"])
        git_dir_raw = read_plumbing(["rev-parse", "--absolute-git-dir"])
        common_dir_raw = read_plumbing(["rev-parse", "--git-common-dir"])
        if (
            inside != b"true\n"
            or not _bound_git_worktree_root(top_level, root, root_binding)
            or object_format not in {b"sha1\n", b"sha256\n"}
            or git_dir_raw is None or common_dir_raw is None
        ):
            return None
        git_dir_text = one_line(git_dir_raw)
        common_dir_text = one_line(common_dir_raw)
        if git_dir_text is None or common_dir_text is None:
            return None
        git_dir = directory(git_dir_text)
        common_dir = directory(common_dir_text, allow_root_relative=True)
        if git_dir is None or common_dir is None:
            return None
        final_marker = marker()
        if (
            final_marker != initial_marker
            or _full_stat_binding(os.fstat(root_fd)) != root_binding
            or _full_stat_binding(os.lstat(workdir)) != root_binding
            or (final_top_level := read_plumbing(["rev-parse", "--show-toplevel"])) != top_level
            or not _bound_git_worktree_root(final_top_level, root, root_binding)
            or read_plumbing(["rev-parse", "--show-object-format"]) != object_format
            or read_plumbing(["rev-parse", "--absolute-git-dir"]) != git_dir_raw
            or read_plumbing(["rev-parse", "--git-common-dir"]) != common_dir_raw
            or directory(git_dir_text) != git_dir
            or directory(common_dir_text, allow_root_relative=True) != common_dir
        ):
            return None
        return {
            "root": {"realpath": root, "dev": opened_root.st_dev, "ino": opened_root.st_ino},
            "git_marker": initial_marker,
            "git_dir": {"realpath": git_dir[0], "authority": git_dir[1]},
            "common_dir": {"realpath": common_dir[0], "authority": common_dir[1]},
            "object_format": object_format[:-1].decode("ascii"),
            "show_toplevel": root,
        }
    except (OSError, UnicodeError, ValueError, OverflowError):
        return None
    finally:
        if root_fd >= 0:
            os.close(root_fd)


def _worktree_snapshot(
    workdir: str, *, legacy: bool = False, explain_unsupported: bool = False,
) -> dict[str, Any] | None:
    """Hash a bounded worktree fact set without executing repository programs.

    This deliberately avoids ``status``, diff, attributes' clean/textconv
    filters, hooks, and external commands.  Read-only index/object plumbing
    provides the tracked baseline; files are opened relative to a no-follow
    root descriptor, so symlinks contribute their own target bytes only.  The
    persisted v7 form deliberately excludes volatile inode/timestamp/cache
    details; the complete bindings below remain in this one scan to detect
    replacement and TOCTOU races.  ``legacy`` retains the exact v6 digest
    algorithm for already-persisted v6 state only.
    """
    root_fd = -1
    try:
        if not os.path.isabs(workdir):
            return None
        root = os.path.realpath(workdir)
        root_fd = os.open(
            os.fsencode(workdir),
            os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0),
        )
        root_info = os.fstat(root_fd)
        if not stat.S_ISDIR(root_info.st_mode):
            return None

        def binding(info: os.stat_result) -> tuple[int, ...]:
            return (
                info.st_dev, info.st_ino, info.st_mode, info.st_nlink,
                info.st_uid, info.st_gid, info.st_size, info.st_mtime_ns, info.st_ctime_ns,
            )

        def authority(value: tuple[int, ...]) -> tuple[int, int, int, int, int]:
            """Project stable identity out of a full in-call race binding."""
            return value[0], value[1], value[4], value[5], stat.S_IMODE(value[2])

        def persistent_metadata(value: tuple[int, ...]) -> tuple[int, ...]:
            """Persist semantic file shape while retaining full race bindings."""
            if not value:
                return value
            if legacy:
                return value
            return stat.S_IFMT(value[2]), stat.S_IMODE(value[2])

        root_binding = binding(root_info)
        if binding(os.lstat(workdir)) != root_binding:
            return None
        # Do not start Git plumbing until a no-follow, marker-only traversal
        # established that the sole marker has the exact root spelling.  The
        # complete directory manifest below repeats the check as its later
        # bounded timing-consistency observation.
        deadline = time.monotonic() + 5.0
        try:
            marker_preflight = _marker_only_preflight(root_fd, deadline=deadline)
        except _MarkerPreflightLimit:
            return None
        if not marker_preflight:
            return None
        if not _worktree_git_admin_alias_boundary(root):
            return None

        def git_marker_binding() -> tuple[bytes, tuple[int, ...], bytes] | None:
            """Bind the root .git marker without following it or its contents."""
            try:
                before = os.stat(".git", dir_fd=root_fd, follow_symlinks=False)
                if stat.S_ISDIR(before.st_mode):
                    descriptor = os.open(
                        ".git", os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
                        | getattr(os, "O_NOFOLLOW", 0), dir_fd=root_fd,
                    )
                    kind = b"directory"
                    payload = b""
                elif stat.S_ISREG(before.st_mode) and before.st_size <= 8192:
                    descriptor = os.open(
                        ".git", os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0), dir_fd=root_fd,
                    )
                    kind = b"file"
                else:
                    return None
                try:
                    if kind == b"file":
                        chunks: list[bytes] = []
                        size = 0
                        while True:
                            piece = os.read(descriptor, min(8193 - size, 8192))
                            if not piece:
                                break
                            chunks.append(piece); size += len(piece)
                            if size > 8192:
                                return None
                        payload = b"".join(chunks)
                    opened = os.fstat(descriptor)
                finally:
                    os.close(descriptor)
                named = os.stat(".git", dir_fd=root_fd, follow_symlinks=False)
            except OSError:
                return None
            if (
                binding(before) != binding(opened) or binding(opened) != binding(named)
                or (kind == b"directory" and not stat.S_ISDIR(opened.st_mode))
                or (kind == b"file" and (not stat.S_ISREG(opened.st_mode) or len(payload) != opened.st_size))
            ):
                return None
            return kind, binding(opened), hashlib.sha256(payload).digest()

        root_git_marker = git_marker_binding()
        if root_git_marker is None:
            return None
        safe_git = _safe_git_executable()
        if safe_git is None:
            return None
        target, target_authority = safe_git
        if not _safe_git_is_outside_worktree(target, root):
            return None
        target_binding = tuple(target_authority["target"])
        total = 0

        def git_read(
            arguments: list[str], payload: bytes = b"", *, allowed: tuple[int, ...] = (0,),
        ) -> tuple[int, bytes] | None:
            """Read fixed Git plumbing with no filters, hooks, fetches, or locks."""
            nonlocal total
            completed = _bounded_git_read(
                target, target_authority, root, arguments, payload=payload,
                allowed=allowed, deadline=deadline,
                stdout_limit=MAX_STREAM_BYTES - total,
            )
            if completed is None:
                return None
            total += len(completed[1])
            return completed

        def one_path(raw: bytes, *, resolve: bool = True) -> str | None:
            if not raw.endswith(b"\n") or raw.count(b"\n") != 1 or b"\0" in raw:
                return None
            value = os.fsdecode(raw[:-1])
            if not value:
                return None
            path = value if os.path.isabs(value) else os.path.join(root, value)
            return os.path.realpath(path) if resolve else os.path.abspath(path)

        def directory_boundary(path: str) -> tuple[str, tuple[int, ...]] | None:
            """Bind a direct Git directory without accepting arbitrary aliases."""
            if not os.path.isabs(path):
                return None
            named_path = os.path.abspath(path)
            try:
                named = os.lstat(os.fsencode(named_path))
                if not stat.S_ISDIR(named.st_mode) or stat.S_ISLNK(named.st_mode):
                    return None
                canonical_path = os.path.realpath(named_path)
                if MODEL_SELECTION._canonical_executable_path(canonical_path) != (
                    MODEL_SELECTION._canonical_executable_path(named_path)
                ):
                    return None
                descriptor = os.open(
                    os.fsencode(named_path), os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
                    | getattr(os, "O_NOFOLLOW", 0),
                )
                try:
                    opened = os.fstat(descriptor)
                finally:
                    os.close(descriptor)
                after = os.lstat(os.fsencode(named_path))
            except OSError:
                return None
            if (
                binding(named) != binding(opened)
                or binding(opened) != binding(after)
            ):
                return None
            return canonical_path, binding(opened)

        def index_binding(path: str) -> tuple[bytes | None, tuple[int, ...] | None] | None:
            try:
                descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
            except FileNotFoundError:
                return (None, None)
            except OSError:
                return None
            try:
                before = os.fstat(descriptor)
                if not stat.S_ISREG(before.st_mode) or stat.S_ISLNK(before.st_mode) or before.st_size > MAX_STREAM_BYTES:
                    return None
                chunks: list[bytes] = []
                total_bytes = 0
                while True:
                    piece = os.read(descriptor, min(65536, MAX_STREAM_BYTES + 1 - total_bytes))
                    if not piece:
                        break
                    chunks.append(piece)
                    total_bytes += len(piece)
                    if total_bytes > MAX_STREAM_BYTES:
                        return None
                after = os.fstat(descriptor)
            finally:
                os.close(descriptor)
            try:
                named = os.lstat(path)
            except OSError:
                return None
            if binding(before) != binding(after) or binding(after) != binding(named):
                return None
            return b"".join(chunks), binding(after)

        def bound_git_worktree() -> bool:
            """Require Git's configured worktree to remain this held root.

            ``-C`` only chooses Git's process directory: a local
            ``core.worktree`` can otherwise redirect plumbing enumeration.  The
            initial and final fixed rev-parse facts therefore bind the context
            before it is passed directly to every enumeration below.
            """
            inside = git_read(["rev-parse", "--is-inside-work-tree"])
            top_level = git_read(["rev-parse", "--show-toplevel"])
            return (
                inside is not None and inside[1] == b"true\n"
                and top_level is not None
                and _bound_git_worktree_root(top_level[1], root, root_binding)
            )

        def bound_git_read(
            arguments: list[str], payload: bytes = b"", *, allowed: tuple[int, ...] = (0,),
        ) -> tuple[int, bytes] | None:
            """Use the no-follow-bound Git directory and held worktree root.

            The initial bare root proof rejects a configured redirected
            worktree.  The bounded reader then derives command-line global
            options from this exact Git-directory authority and held root;
            arbitrary argument lists cannot override either.  The final bare
            proof fails closed if repository configuration drifts during the
            scan.
            """
            return git_read(
                _BoundGitReadArguments(arguments, git_dir_boundary), payload, allowed=allowed,
            )

        if not bound_git_worktree():
            return None

        format_result = git_read(["rev-parse", "--show-object-format"])
        if format_result is None or format_result[1] not in {b"sha1\n", b"sha256\n"}:
            return None
        object_length = 40 if format_result[1] == b"sha1\n" else 64
        git_dir_result = git_read(["rev-parse", "--absolute-git-dir"])
        if git_dir_result is None:
            return None
        git_dir_path = one_path(git_dir_result[1], resolve=False)
        if git_dir_path is None:
            return None
        git_dir_boundary = directory_boundary(git_dir_path)
        if git_dir_boundary is None:
            return None
        index_path_result = git_read(["rev-parse", "--git-path", "index"])
        if index_path_result is None:
            return None
        index_path = one_path(index_path_result[1], resolve=False)
        if index_path is None:
            return None
        before_index = index_binding(index_path)
        if before_index is None:
            return None
        common_path_result = git_read(["rev-parse", "--git-common-dir"])
        if common_path_result is None:
            return None
        common_path = one_path(common_path_result[1], resolve=False)
        if common_path is None:
            return None
        common_dir_boundary = directory_boundary(common_path)
        if common_dir_boundary is None:
            return None
        for alternate_name in ("alternates", "http-alternates"):
            try:
                os.lstat(os.path.join(common_path, "objects", "info", alternate_name))
                return None
            except FileNotFoundError:
                pass
            except OSError:
                return None
        promisor = bound_git_read(
            ["config", "--local", "--no-includes", "--get-regexp", "^(extensions\\.partialclone|remote\\..*\\.promisor)$"],
            allowed=(0, 1),
        )
        sparse = bound_git_read(["config", "--bool", "--get", "core.sparseCheckout"], allowed=(0, 1))
        if promisor is None or sparse is None:
            return None
        if promisor[0] == 0 and promisor[1]:
            if explain_unsupported:
                raise _UnsupportedWorktreeError(
                    "partial/promisor Git clones are unsupported; use a full clone"
                )
            return None
        if (promisor[0] == 1 and promisor[1]) or (sparse[0] == 0 and sparse[1] != b"false\n") or (sparse[0] == 1 and sparse[1]):
            return None
        skip = bound_git_read(["ls-files", "-v", "-z"])
        if skip is None or (skip[1] and not skip[1].endswith(b"\0")):
            return None
        if any(
            len(record) < 3 or record[1:2] != b" " or record.startswith(b"S ") or record[:1].islower()
            for record in skip[1].split(b"\0")[:-1]
        ):
            return None

        def listings() -> tuple[bytes, bytes, bytes, bytes, bytes, bytes] | None:
            head_id = bound_git_read(["rev-parse", "--verify", "-q", "HEAD^{tree}"], allowed=(0, 1))
            staged = bound_git_read(["ls-files", "--stage", "-z"])
            debug = None if legacy else bound_git_read(["ls-files", "--debug", "-z"])
            resolve_undo = None if legacy else bound_git_read(["ls-files", "--resolve-undo", "-z"])
            other = bound_git_read(["ls-files", "-z", "--others", "--exclude-standard"])
            ignored = bound_git_read(["ls-files", "-z", "--others", "--ignored", "--exclude-standard"])
            if (
                head_id is None or staged is None or (not legacy and debug is None)
                or (not legacy and resolve_undo is None) or other is None or ignored is None
            ):
                return None
            if not legacy:
                parsed_resolve_undo = _parse_resolve_undo(resolve_undo[1], object_length)  # type: ignore[index]
                if parsed_resolve_undo is None or parsed_resolve_undo:
                    if explain_unsupported and parsed_resolve_undo:
                        second_resolve_undo = bound_git_read(["ls-files", "--resolve-undo", "-z"])
                        if (
                            second_resolve_undo is not None
                            and second_resolve_undo[1] == resolve_undo[1]
                            and index_binding(index_path) == before_index
                            and _parse_resolve_undo(second_resolve_undo[1], object_length) == parsed_resolve_undo
                        ):
                            raise _ResolveUndoPresentError("resolve_undo_present")
                    return None
            if head_id[0] == 1:
                if head_id[1]:
                    return None
                head = b""
            elif len(head_id[1]) == object_length + 1 and head_id[1].endswith(b"\n"):
                oid = head_id[1][:-1]
                if any(char not in b"0123456789abcdef" for char in oid):
                    return None
                tree = bound_git_read(["ls-tree", "-r", "-z", oid.decode("ascii")])
                if tree is None:
                    return None
                head = tree[1]
            else:
                return None
            values = (head, staged[1], other[1], ignored[1])
            if any(raw and not raw.endswith(b"\0") for raw in values):
                return None
            return values[0], values[1], b"" if debug is None else debug[1], values[2], values[3], head_id[1]

        first = listings()
        if first is None:
            return None
        head_raw, staged_raw, debug_raw, other_raw, ignored_raw, head_id_raw = first

        def valid_oid(value: bytes) -> bool:
            return len(value) == object_length and not any(char not in b"0123456789abcdef" for char in value)

        def parse_tree(raw: bytes) -> dict[bytes, tuple[int, bytes]] | None:
            parsed: dict[bytes, tuple[int, bytes]] = {}
            for record in raw.split(b"\0")[:-1]:
                try:
                    header, relative = record.split(b"\t", 1)
                    mode_raw, kind, oid = header.split(b" ")
                    mode = int(mode_raw, 8)
                except (ValueError, TypeError):
                    return None
                if kind != b"blob" or mode not in {0o100644, 0o100755, 0o120000} or not valid_oid(oid) or relative in parsed:
                    return None
                parsed[relative] = (mode, oid)
            return parsed

        def parse_index(raw: bytes) -> dict[bytes, tuple[int, bytes]] | None:
            parsed: dict[bytes, tuple[int, bytes]] = {}
            for record in raw.split(b"\0")[:-1]:
                try:
                    header, relative = record.split(b"\t", 1)
                    mode_raw, oid, stage_raw = header.split(b" ")
                    mode = int(mode_raw, 8)
                except (ValueError, TypeError):
                    return None
                if stage_raw != b"0" or mode not in {0o100644, 0o100755, 0o120000} or not valid_oid(oid) or relative in parsed:
                    return None
                parsed[relative] = (mode, oid)
            return parsed

        def debug_index_flags(raw: bytes) -> dict[bytes, int] | None:
            """Read documented ls-files debug flags, ignoring volatile stat cache.

            The debug record's pathname is NUL-delimited; its preceding stat
            cache lines are intentionally only shape-checked.  Flags are the
            semantic portion: unsupported nonzero values, including
            CE_INTENT_TO_ADD, reject rather than silently sharing an OID/mode
            digest with a different index meaning.
            """
            parsed: dict[bytes, int] = {}
            position = 0
            while position < len(raw):
                separator = raw.find(b"\0", position)
                if separator < position:
                    return None
                relative = raw[position:separator]
                position = separator + 1
                lines: list[bytes] = []
                for _ in range(5):
                    ending = raw.find(b"\n", position)
                    if ending < position:
                        return None
                    lines.append(raw[position:ending + 1])
                    position = ending + 1
                if not relative or relative in parsed or any(
                    re.fullmatch(shape, line) is None
                    for shape, line in zip((
                        br"  ctime: [0-9]+:[0-9]+\n",
                        br"  mtime: [0-9]+:[0-9]+\n",
                        br"  dev: [0-9]+\tino: [0-9]+\n",
                        br"  uid: [0-9]+\tgid: [0-9]+\n",
                    ), lines[:4])
                ):
                    return None
                flags = re.fullmatch(br"  size: [0-9]+\tflags: ([0-9a-f]+)\n", lines[4])
                if flags is None:
                    return None
                try:
                    parsed[relative] = int(flags.group(1), 16)
                except ValueError:
                    return None
            return parsed

        head = parse_tree(head_raw)
        staged = parse_index(staged_raw)
        flags = {} if legacy else debug_index_flags(debug_raw)
        if head is None or staged is None or flags is None:
            return None
        if not legacy and (set(flags) != set(staged) or any(value != 0 for value in flags.values())):
            return None
        other = set(other_raw.split(b"\0")[:-1])
        ignored = set(ignored_raw.split(b"\0")[:-1])
        if other & ignored or len(head) + len(staged) + len(other) + len(ignored) > MAX_BOUNDARY_ENTRIES:
            return None
        object_ids = sorted({oid for _mode, oid in staged.values()})
        objects_raw = bound_git_read(["cat-file", "--batch"], b"".join(item + b"\n" for item in object_ids))
        if objects_raw is None:
            return None
        objects: dict[bytes, bytes] = {}
        position = 0
        while position < len(objects_raw[1]):
            end = objects_raw[1].find(b"\n", position)
            if end < 0:
                return None
            fields = objects_raw[1][position:end].split(b" ")
            if len(fields) != 3 or fields[0] not in object_ids or fields[1] != b"blob":
                return None
            try:
                size = int(fields[2])
            except ValueError:
                return None
            start = end + 1
            finish = start + size
            if size < 0 or finish >= len(objects_raw[1]) or objects_raw[1][finish:finish + 1] != b"\n" or fields[0] in objects:
                return None
            objects[fields[0]] = objects_raw[1][start:finish]
            position = finish + 1
        if len(objects) != len(object_ids):
            return None

        nofollow = getattr(os, "O_NOFOLLOW", 0)
        directory = getattr(os, "O_DIRECTORY", 0)

        def directory_manifest() -> tuple[bytes, int] | None:
            """Bind bounded topology and count otherwise-unlisted empty directories."""
            manifest_bytes = 0
            manifest_entries = 0
            empty_directories = 0

            def walk(parent_fd: int, *, is_root: bool = False) -> bytes | None:
                nonlocal manifest_bytes, manifest_entries, empty_directories
                if time.monotonic() >= deadline:
                    return None
                before_directory = os.fstat(parent_fd)
                if not stat.S_ISDIR(before_directory.st_mode):
                    return None
                records: list[tuple[bytes, bytes, tuple[int, ...], bytes]] = []
                scan_fd = -1
                try:
                    # scandir does not own a caller-supplied descriptor on the
                    # supported runtimes, so retain and close this duplicate in
                    # our own finally path even if scandir rejects it.
                    scan_fd = os.dup(parent_fd)
                    with os.scandir(scan_fd) as scanned:
                        for entry in scanned:
                            if time.monotonic() >= deadline:
                                return None
                            name = entry.name
                            raw_name = os.fsencode(name)
                            if not raw_name or b"\0" in raw_name:
                                continue
                            if raw_name.lower() == b".git":
                                # Only the root marker was bound separately.
                                # Do not open or traverse a nested marker.
                                if is_root and raw_name == b".git":
                                    continue
                                return None
                            manifest_entries += 1
                            if manifest_entries > MAX_BOUNDARY_ENTRIES:
                                return None
                            try:
                                info = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
                            except OSError:
                                return None
                            metadata = binding(info)
                            if stat.S_ISDIR(info.st_mode):
                                try:
                                    child_fd = os.open(name, os.O_RDONLY | directory | nofollow, dir_fd=parent_fd)
                                except OSError:
                                    return None
                                try:
                                    if binding(os.fstat(child_fd)) != metadata:
                                        return None
                                    payload = walk(child_fd)
                                    if payload is None or binding(os.fstat(child_fd)) != metadata:
                                        return None
                                finally:
                                    os.close(child_fd)
                                kind = b"directory"
                            elif stat.S_ISLNK(info.st_mode):
                                try:
                                    target_raw = os.fsencode(os.readlink(name, dir_fd=parent_fd))
                                    named = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
                                except OSError:
                                    return None
                                manifest_bytes += len(target_raw)
                                if manifest_bytes > MAX_STREAM_BYTES or binding(named) != metadata:
                                    return None
                                payload = hashlib.sha256(target_raw).digest()
                                kind = b"symlink"
                            elif stat.S_ISREG(info.st_mode):
                                # Regular bytes and metadata are bound by the
                                # primary listed-path observation and its final
                                # revalidation.  This second pass is topology
                                # only, so it never re-reads file contents.
                                metadata = ()
                                payload = b""
                                kind = b"file"
                            else:
                                metadata = ()
                                payload = b""
                                kind = b"special"
                            records.append((raw_name, kind, persistent_metadata(metadata), payload))
                except OSError:
                    return None
                finally:
                    if scan_fd >= 0:
                        os.close(scan_fd)
                try:
                    if binding(os.fstat(parent_fd)) != binding(before_directory):
                        return None
                except OSError:
                    return None
                result = hashlib.sha256()
                result.update(b"agy-worker-directory-manifest-v1\0")
                for raw_name, kind, metadata, payload in sorted(records):
                    result.update(len(raw_name).to_bytes(8, "big")); result.update(raw_name)
                    result.update(len(kind).to_bytes(8, "big")); result.update(kind)
                    metadata_raw = canonical(list(metadata))
                    result.update(len(metadata_raw).to_bytes(8, "big")); result.update(metadata_raw)
                    result.update(len(payload).to_bytes(8, "big")); result.update(payload)
                if not is_root and not records:
                    empty_directories += 1
                return result.digest()

            manifest = walk(root_fd, is_root=True)
            if manifest is None:
                return None
            return manifest, empty_directories

        observation = hashlib.sha256()
        observation.update(b"agy-worker-worktree-v5\0" if legacy else b"agy-worker-worktree-v7\0")
        canonical_root = os.fsencode(root)
        observation.update(len(canonical_root).to_bytes(8, "big")); observation.update(canonical_root)
        observation.update(canonical([root_info.st_dev, root_info.st_ino]))
        observation.update(canonical([
            os.fsdecode(root_git_marker[0]), list(authority(root_git_marker[1])),
            root_git_marker[2].hex(),
        ]))
        observation.update(canonical([
            git_dir_boundary[0], list(authority(git_dir_boundary[1])),
            common_dir_boundary[0], list(authority(common_dir_boundary[1])),
            os.path.realpath(index_path) if legacy else None,
            None if before_index[0] is None else hashlib.sha256(before_index[0]).hexdigest() if legacy else None,
            None if before_index[1] is None else list(authority(before_index[1])) if legacy else None,
        ]))
        content_bytes = 0
        changed = 0
        observed_paths: dict[bytes, tuple[Any, ...]] = {}
        for relative in sorted(set(head) | set(staged) | other | ignored):
            parts = relative.split(b"/")
            if not relative or relative.startswith(b"/") or any(part in {b"", b".", b".."} for part in parts) or parts[0] == b".git":
                return None
            observation.update(len(relative).to_bytes(8, "big")); observation.update(relative)
            indexed = staged.get(relative)
            head_entry = head.get(relative)
            for label, entry in ((b"head", head_entry), (b"index", indexed)):
                observation.update(label + b"\0")
                if entry is None:
                    observation.update(b"missing\0")
                else:
                    observation.update(f"{entry[0]:o}".encode("ascii") + b"\0")
                    observation.update(entry[1])
            index_changed = indexed != head_entry
            is_other = relative in other or relative in ignored
            parent_fd = os.dup(root_fd)
            try:
                for component in parts[:-1]:
                    next_fd = os.open(component, os.O_RDONLY | directory | nofollow, dir_fd=parent_fd)
                    os.close(parent_fd); parent_fd = next_fd
                name = parts[-1]
                try:
                    before = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
                except FileNotFoundError:
                    observation.update(b"missing\0")
                    observed_paths[relative] = (b"missing",)
                    differs = indexed is not None
                else:
                    metadata = binding(before); observation.update(canonical(list(persistent_metadata(metadata))))
                    if stat.S_ISLNK(before.st_mode):
                        target_raw = os.fsencode(os.readlink(name, dir_fd=parent_fd))
                        content_bytes += len(target_raw)
                        if content_bytes > MAX_STREAM_BYTES or binding(os.stat(name, dir_fd=parent_fd, follow_symlinks=False)) != metadata:
                            return None
                        observation.update(b"symlink\0"); observation.update(len(target_raw).to_bytes(8, "big")); observation.update(target_raw)
                        observed_paths[relative] = (b"symlink", metadata, target_raw)
                        differs = indexed is None or indexed[0] != 0o120000 or target_raw != objects[indexed[1]]
                    elif stat.S_ISREG(before.st_mode):
                        descriptor = os.open(name, os.O_RDONLY | nofollow, dir_fd=parent_fd)
                        try:
                            opened = os.fstat(descriptor)
                            if (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino):
                                return None
                            content = hashlib.sha256()
                            while True:
                                piece = os.read(descriptor, 65536)
                                if not piece:
                                    break
                                content_bytes += len(piece)
                                if content_bytes > MAX_STREAM_BYTES:
                                    return None
                                content.update(piece)
                            after = os.fstat(descriptor)
                        finally:
                            os.close(descriptor)
                        if binding(after) != metadata or binding(os.stat(name, dir_fd=parent_fd, follow_symlinks=False)) != metadata:
                            return None
                        content_digest = content.digest()
                        observation.update(b"file\0"); observation.update(content_digest)
                        observed_paths[relative] = (b"file", metadata, content_digest)
                        differs = indexed is None or indexed[0] not in {0o100644, 0o100755} or bool(before.st_mode & 0o111) != bool(indexed[0] & 0o111) or before.st_size != len(objects[indexed[1]]) or content_digest != hashlib.sha256(objects[indexed[1]]).digest()
                    else:
                        observation.update(b"special\0")
                        observed_paths[relative] = (b"special", metadata)
                        differs = True
                if is_other or index_changed or differs:
                    changed += 1
            finally:
                os.close(parent_fd)
        initial_directory_observation = directory_manifest()
        if initial_directory_observation is None:
            return None
        initial_directory_manifest, initial_empty_directories = initial_directory_observation
        second = listings()
        if second is None or second != first or index_binding(index_path) != before_index:
            return None

        revalidated_bytes = 0
        for relative, expected in observed_paths.items():
            parts = relative.split(b"/")
            parent_fd = os.dup(root_fd)
            try:
                for component in parts[:-1]:
                    next_fd = os.open(component, os.O_RDONLY | directory | nofollow, dir_fd=parent_fd)
                    os.close(parent_fd); parent_fd = next_fd
                name = parts[-1]
                try:
                    before = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
                except FileNotFoundError:
                    current: tuple[Any, ...] = (b"missing",)
                else:
                    metadata = binding(before)
                    if stat.S_ISLNK(before.st_mode):
                        target_raw = os.fsencode(os.readlink(name, dir_fd=parent_fd))
                        revalidated_bytes += len(target_raw)
                        if (
                            revalidated_bytes > MAX_STREAM_BYTES
                            or binding(os.stat(name, dir_fd=parent_fd, follow_symlinks=False)) != metadata
                        ):
                            return None
                        current = (b"symlink", metadata, target_raw)
                    elif stat.S_ISREG(before.st_mode):
                        descriptor = os.open(name, os.O_RDONLY | nofollow, dir_fd=parent_fd)
                        try:
                            opened = os.fstat(descriptor)
                            if (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino):
                                return None
                            content = hashlib.sha256()
                            while True:
                                piece = os.read(descriptor, 65536)
                                if not piece:
                                    break
                                revalidated_bytes += len(piece)
                                if revalidated_bytes > MAX_STREAM_BYTES:
                                    return None
                                content.update(piece)
                            after = os.fstat(descriptor)
                        finally:
                            os.close(descriptor)
                        if (
                            binding(after) != metadata
                            or binding(os.stat(name, dir_fd=parent_fd, follow_symlinks=False)) != metadata
                        ):
                            return None
                        current = (b"file", metadata, content.digest())
                    else:
                        current = (b"special", metadata)
                if current != expected:
                    return None
            finally:
                os.close(parent_fd)
        third = listings()
        if (
            third is None
            or third != first
            or index_binding(index_path) != before_index
        ):
            return None
        # The second complete manifest is the bounded linearization point: all
        # Git/listing operations completed before it begins and it must equal
        # the first manifest. A same-UID mutation after an entry's final read
        # remains outside this finite observation and is a controller-TCB
        # residual, not a reason to alternate scans indefinitely.
        final_directory_observation = directory_manifest()
        if final_directory_observation is None:
            return None
        final_directory_manifest, final_empty_directories = final_directory_observation
        if (
            final_directory_manifest != initial_directory_manifest
            or final_empty_directories != initial_empty_directories
            or index_binding(index_path) != before_index
        ):
            return None
        if (
            os.path.realpath(workdir) != root
            or binding(os.fstat(root_fd)) != root_binding
            or binding(os.lstat(workdir)) != root_binding
            or git_marker_binding() != root_git_marker
            or directory_boundary(git_dir_path) != git_dir_boundary
            or directory_boundary(common_path) != common_dir_boundary
            or index_binding(index_path) != before_index
            or binding(os.lstat(target)) != target_binding
            or not bound_git_worktree()
        ):
            return None
        observation.update(b"directory-manifest-v1\0")
        observation.update(initial_directory_manifest)
        observation.update(initial_empty_directories.to_bytes(8, "big"))
        return {"sha256": observation.hexdigest(), "entries": changed + initial_empty_directories}
    except _UnsupportedWorktreeError:
        raise
    except (OSError, subprocess.TimeoutExpired, OverflowError, ValueError, RecursionError):
        return None
    finally:
        if root_fd >= 0:
            os.close(root_fd)


def _parse_provider_scope(raw_bytes: bytes) -> dict[str, Any]:
    """Parse and validate a closed agy-worker-provider-scope JSON object."""
    if not isinstance(raw_bytes, (bytes, bytearray)):
        raise DispatchError("provider scope must be raw bytes")
    try:
        text = raw_bytes.decode("utf-8", "strict")
    except UnicodeError as exc:
        raise DispatchError("provider scope is not valid UTF-8") from exc
    if "\x00" in text:
        raise DispatchError("provider scope contains NUL character")

    def _reject_dup(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, val in pairs:
            if key in result:
                raise DispatchError(f"duplicate key in scope JSON: {key!r}")
            result[key] = val
        return result

    try:
        value = json.loads(text, object_pairs_hook=_reject_dup)
    except (json.JSONDecodeError, ValueError) as exc:
        raise DispatchError(f"provider scope JSON is invalid: {exc}") from exc

    if not isinstance(value, dict):
        raise DispatchError("provider scope must be a JSON object")
    if set(value.keys()) != {"schema_version", "kind", "read", "write"}:
        raise DispatchError("provider scope keys must be exactly schema_version, kind, read, write")
    if value.get("schema_version") != 1:
        raise DispatchError("provider scope schema_version must be 1")
    if value.get("kind") != "agy-worker-provider-scope":
        raise DispatchError("provider scope kind must be agy-worker-provider-scope")
    if not isinstance(value.get("read"), list) or not isinstance(value.get("write"), list):
        raise DispatchError("provider scope read and write must be lists")

    def validate_entries(entries: list[Any], section: str) -> list[dict[str, str]]:
        result: list[dict[str, str]] = []
        last_path: str | None = None
        tree_paths: list[str] = []
        for index, entry in enumerate(entries):
            if not isinstance(entry, dict):
                raise DispatchError(f"{section} entry {index} must be an object")
            if set(entry.keys()) != {"path", "kind"}:
                raise DispatchError(f"{section} entry {index} keys must be exactly path and kind")
            path = entry.get("path")
            kind = entry.get("kind")
            if not isinstance(path, str) or not path:
                raise DispatchError(f"{section} entry {index} path is invalid")
            if not isinstance(kind, str) or kind not in {"file", "tree"}:
                raise DispatchError(f"{section} entry {index} kind must be 'file' or 'tree'")
            if "\x00" in path or "\r" in path or "\n" in path:
                raise DispatchError(f"{section} entry {index} path contains forbidden control characters")
            if path.startswith("/") or path.endswith("/"):
                raise DispatchError(f"{section} entry {index} path cannot have leading or trailing slashes")
            norm = posixpath.normpath(path)
            if norm != path or norm in ("", ".", "..") or norm.startswith("../") or posixpath.isabs(norm):
                raise DispatchError(f"{section} entry {index} path is not normalized: {path!r}")
            parts = norm.split("/")
            for part in parts:
                if part.lower() in {".git", ".agy-worker-control"}:
                    raise DispatchError(f"{section} entry {index} path contains reserved component: {part!r}")
            if last_path is not None:
                if path == last_path:
                    raise DispatchError(f"duplicate path in {section}: {path!r}")
                if path < last_path:
                    raise DispatchError(f"{section} entries must be strictly sorted: {path!r} after {last_path!r}")
            last_path = path
            # Nonredundancy check against previous tree entries
            for tree_p in tree_paths:
                if path.startswith(tree_p + "/"):
                    raise DispatchError(f"redundant entry in {section}: {path!r} is covered by tree {tree_p!r}")
            if kind == "tree":
                tree_paths.append(path)
            result.append({"kind": kind, "path": path})
        return result

    validated_read = validate_entries(value["read"], "read")
    validated_write = validate_entries(value["write"], "write")

    def covered_by_read(entry: dict[str, str]) -> bool:
        for readable in validated_read:
            if readable["path"] == entry["path"]:
                return readable["kind"] == entry["kind"] or readable["kind"] == "tree"
            if readable["kind"] == "tree" and entry["path"].startswith(
                readable["path"] + "/"
            ):
                return True
        return False

    for entry in validated_write:
        if not covered_by_read(entry):
            raise DispatchError(
                f"write entry is not covered by read scope: {entry['path']!r}"
            )

    canonical_obj = {
        "kind": "agy-worker-provider-scope",
        "read": validated_read,
        "schema_version": 1,
        "write": validated_write,
    }
    return canonical_obj


def _validate_scope_against_worktree(
    scope: dict[str, Any], worktree_root: str, readable_manifest: list[dict[str, str]],
) -> None:
    """Validate provider scope against the worktree readable manifest and invariants."""
    manifest_files = {e["path"] for e in readable_manifest if e["kind"] == "file"}
    manifest_dirs = {e["path"] for e in readable_manifest if e["kind"] == "directory"}
    manifest_symlinks = {e["path"] for e in readable_manifest if e["kind"] == "symlink"}

    if manifest_symlinks:
        raise DispatchError("narrow provider scope requires a symlink-free worktree; symlinks rejected")

    directory_flag = getattr(os, "O_DIRECTORY", 0)
    nofollow = getattr(os, "O_NOFOLLOW", 0)

    # Reject hardlinks (nlink != 1) on all regular files using descriptor-relative O_NOFOLLOW stat
    root_fd = os.open(worktree_root, os.O_RDONLY | directory_flag | nofollow)
    try:
        for rel_path in manifest_files:
            parts = rel_path.split("/")
            parent_fd = os.dup(root_fd)
            try:
                for comp in parts[:-1]:
                    next_fd = os.open(comp, os.O_RDONLY | directory_flag | nofollow, dir_fd=parent_fd)
                    os.close(parent_fd)
                    parent_fd = next_fd
                st = os.stat(parts[-1], dir_fd=parent_fd, follow_symlinks=False)
                if not stat.S_ISREG(st.st_mode) or st.st_nlink != 1:
                    raise DispatchError(f"narrow provider scope requires hardlink-free regular files; nlink={st.st_nlink} on {rel_path}")
            finally:
                os.close(parent_fd)
    finally:
        os.close(root_fd)

    # Path alias collision detection (casefold, NFC, NFD)
    all_paths = [e["path"] for e in readable_manifest]
    casefold_seen: set[str] = set()
    nfc_seen: set[str] = set()
    nfd_seen: set[str] = set()
    for p in all_paths:
        cf = p.casefold()
        if cf in casefold_seen:
            raise DispatchError(f"worktree contains casefold path alias collision: {p}")
        casefold_seen.add(cf)

        nfc = unicodedata.normalize("NFC", p)
        if nfc in nfc_seen:
            raise DispatchError(f"worktree contains Unicode NFC path alias collision: {p}")
        nfc_seen.add(nfc)

        nfd = unicodedata.normalize("NFD", p)
        if nfd in nfd_seen:
            raise DispatchError(f"worktree contains Unicode NFD path alias collision: {p}")
        nfd_seen.add(nfd)

    # Validate read entries exist
    for r in scope["read"]:
        if r["kind"] == "file":
            if r["path"] not in manifest_files:
                raise DispatchError(f"read file does not exist in worktree: {r['path']}")
        elif r["kind"] == "tree":
            if r["path"] not in manifest_dirs:
                raise DispatchError(f"read tree does not exist in worktree: {r['path']}")

    def is_covered_by_read(p: str, kind: str) -> bool:
        for r in scope["read"]:
            if r["kind"] == kind and r["path"] == p:
                return True
            if r["kind"] == "tree" and (p == r["path"] or p.startswith(r["path"] + "/")):
                return True
        return False

    for w in scope["write"]:
        w_path = w["path"]
        if w_path in manifest_files:
            if not is_covered_by_read(w_path, "file"):
                raise DispatchError(f"existing write file is not covered by read scope: {w_path}")
        elif w_path in manifest_dirs:
            if not is_covered_by_read(w_path, "tree"):
                raise DispatchError(f"existing write tree is not covered by read scope: {w_path}")
        else:
            if w["kind"] == "tree":
                if not is_covered_by_read(w_path, "tree"):
                    raise DispatchError(f"new write tree is not covered by read tree: {w_path}")
            elif w["kind"] == "file":
                parent = posixpath.dirname(w_path)
                if parent and parent != ".":
                    if parent not in manifest_dirs and not is_covered_by_read(parent, "tree"):
                        raise DispatchError(f"new write file parent is not covered by read tree: {w_path}")


def _build_selected_content_manifest(
    root_dir: str | Path, scope: dict[str, Any], *, is_stage: bool = False,
) -> list[dict[str, Any]]:
    """Build canonical selected-content manifest using descriptor-relative O_NOFOLLOW operations."""
    directory_flag = getattr(os, "O_DIRECTORY", 0)
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    deadline = time.monotonic() + SELECTED_CONTENT_SCAN_SECONDS
    total_bytes = 0

    def check_bounds(*, add_bytes: int = 0) -> None:
        nonlocal total_bytes
        if time.monotonic() > deadline:
            raise DispatchError("selected content scan deadline exceeded")
        total_bytes += add_bytes
        if total_bytes > SELECTED_CONTENT_MAX_TOTAL_BYTES:
            raise DispatchError("selected content byte limit exceeded")

    def is_selected_path(p: str) -> tuple[bool, str | None]:
        for r in scope["read"]:
            if r["kind"] == "file" and r["path"] == p:
                return True, "file"
            if r["kind"] == "tree":
                if r["path"] == p or p.startswith(r["path"] + "/"):
                    return True, None
        for r in scope["read"]:
            if r["path"].startswith(p + "/"):
                return True, "directory"
        return False, None

    manifest: list[dict[str, Any]] = []
    empty_sha = hashlib.sha256(b"").hexdigest()

    def walk_descriptor(parent_fd: int, rel_prefix: str) -> None:
        check_bounds()
        scan_fd = os.dup(parent_fd)
        try:
            with os.scandir(scan_fd) as scanned:
                children = [(entry.name.encode("utf-8"), entry.name) for entry in scanned]
        finally:
            os.close(scan_fd)
        children.sort(key=lambda x: x[0])
        for _name_b, name_str in children:
            check_bounds()
            rel = posixpath.normpath(posixpath.join(rel_prefix, name_str)) if rel_prefix else name_str
            if name_str in {".git", ".gitmodules"} and not is_stage:
                continue
            st = os.stat(name_str, dir_fd=parent_fd, follow_symlinks=False)
            if stat.S_ISLNK(st.st_mode):
                raise DispatchError(f"symlink rejected in selected content scan: {rel}")
            if not (stat.S_ISDIR(st.st_mode) or stat.S_ISREG(st.st_mode)):
                raise DispatchError(f"special node rejected in selected content scan: {rel}")
            selected, _ = is_selected_path(rel)
            if not selected:
                continue
            if stat.S_ISDIR(st.st_mode):
                if len(manifest) >= SELECTED_CONTENT_MAX_ENTRIES:
                    raise DispatchError("selected content entry limit exceeded")
                manifest.append({
                    "executable": False,
                    "kind": "directory",
                    "path": rel,
                    "sha256": empty_sha,
                    "size": 0,
                })
                child_fd = os.open(name_str, os.O_RDONLY | directory_flag | nofollow, dir_fd=parent_fd)
                try:
                    walk_descriptor(child_fd, rel)
                finally:
                    os.close(child_fd)
            elif stat.S_ISREG(st.st_mode):
                if st.st_nlink != 1:
                    raise DispatchError(f"hardlink rejected in selected content scan: {rel}")
                file_fd = os.open(name_str, os.O_RDONLY | nofollow, dir_fd=parent_fd)
                try:
                    opened = os.fstat(file_fd)
                    if _manifest_binding(opened) != _manifest_binding(st):
                        raise DispatchError(f"selected file changed before read: {rel}")
                    hasher = hashlib.sha256()
                    total_size = 0
                    while True:
                        check_bounds()
                        chunk = os.read(file_fd, 65536)
                        if not chunk:
                            break
                        total_size += len(chunk)
                        if total_size > SELECTED_CONTENT_MAX_FILE_BYTES:
                            raise DispatchError(f"selected file byte limit exceeded: {rel}")
                        check_bounds(add_bytes=len(chunk))
                        hasher.update(chunk)
                    file_sha = hasher.hexdigest()
                    after = os.fstat(file_fd)
                finally:
                    os.close(file_fd)
                named = os.stat(name_str, dir_fd=parent_fd, follow_symlinks=False)
                if (
                    _manifest_binding(opened) != _manifest_binding(after)
                    or _manifest_binding(after) != _manifest_binding(named)
                ):
                    raise DispatchError(f"selected file changed during read: {rel}")
                if len(manifest) >= SELECTED_CONTENT_MAX_ENTRIES:
                    raise DispatchError("selected content entry limit exceeded")
                manifest.append({
                    "executable": bool(st.st_mode & 0o111),
                    "kind": "file",
                    "path": rel,
                    "sha256": file_sha,
                    "size": total_size,
                })

    root_fd = os.open(str(root_dir), os.O_RDONLY | directory_flag | nofollow)
    try:
        walk_descriptor(root_fd, "")
    finally:
        os.close(root_fd)

    manifest.sort(key=lambda it: it["path"])
    return manifest


def _selected_content_digest(selected_manifest: list[dict[str, Any]]) -> str:
    """Compute deterministic SHA-256 digest of canonical selected-content manifest."""
    raw = json.dumps(selected_manifest, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("ascii") + b"\n"
    return hashlib.sha256(raw).hexdigest()


def _compute_transmission_sha256(
    policy_sha256: str, readable_manifest_sha256: str, selected_content_sha256: str,
) -> str:
    """Compute deterministic combined transmission SHA-256."""
    payload = {
        "manifest_sha256": readable_manifest_sha256,
        "policy_sha256": policy_sha256,
        "selected_content_sha256": selected_content_sha256,
    }
    raw = json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("ascii") + b"\n"
    return hashlib.sha256(raw).hexdigest()


def _materialize_stage(
    source_root: str | Path, stage_dir: str | Path, scope: dict[str, Any], selected_manifest: list[dict[str, Any]],
) -> tuple[tuple[int, int, int, int, int], str]:
    """Materialize 0700 Git-less stage with descriptor-relative safe copies."""
    directory_flag = getattr(os, "O_DIRECTORY", 0)
    nofollow = getattr(os, "O_NOFOLLOW", 0)

    stage_str = str(stage_dir)
    source_str = str(source_root)
    deadline = time.monotonic() + SELECTED_CONTENT_SCAN_SECONDS
    copied_bytes = 0

    if len(selected_manifest) > SELECTED_CONTENT_MAX_ENTRIES:
        raise DispatchError("selected content entry limit exceeded")
    src_root_fd = -1
    stage_root_fd = -1
    stage_identity: tuple[int, int, int, int, int] | None = None
    os.mkdir(stage_str, mode=0o700)
    try:
        stage_root_fd = os.open(stage_str, os.O_RDONLY | directory_flag | nofollow)
        created_st = os.fstat(stage_root_fd)
        if not stat.S_ISDIR(created_st.st_mode) or created_st.st_uid != os.getuid():
            raise DispatchError("stage directory authority is invalid")
        stage_identity = (
            created_st.st_dev, created_st.st_ino, created_st.st_uid,
            created_st.st_gid, created_st.st_mode,
        )
        os.fchmod(stage_root_fd, 0o700)
        normalized_st = os.fstat(stage_root_fd)
        normalized_identity = (
            normalized_st.st_dev, normalized_st.st_ino, normalized_st.st_uid,
            normalized_st.st_gid, normalized_st.st_mode,
        )
        if (
            normalized_identity[:4] != stage_identity[:4]
            or not stat.S_ISDIR(normalized_st.st_mode)
            or stat.S_IMODE(normalized_st.st_mode) != 0o700
        ):
            raise DispatchError("stage directory identity changed before materialization")
        stage_identity = normalized_identity
        path_st = os.lstat(stage_str)
        if (path_st.st_dev, path_st.st_ino, path_st.st_uid, path_st.st_gid, path_st.st_mode) != stage_identity:
            raise DispatchError("stage directory identity changed before materialization")
        src_root_fd = os.open(source_str, os.O_RDONLY | directory_flag | nofollow)

        for entry in selected_manifest:
            if time.monotonic() > deadline:
                raise DispatchError("stage materialization deadline exceeded")
            rel = entry["path"]
            parts = rel.split("/")
            if entry["kind"] == "directory":
                curr_fd = os.dup(stage_root_fd)
                try:
                    for comp in parts:
                        try:
                            next_fd = os.open(comp, os.O_RDONLY | directory_flag | nofollow, dir_fd=curr_fd)
                        except FileNotFoundError:
                            os.mkdir(comp, 0o700, dir_fd=curr_fd)
                            next_fd = os.open(comp, os.O_RDONLY | directory_flag | nofollow, dir_fd=curr_fd)
                        os.fchmod(next_fd, 0o700)
                        os.close(curr_fd)
                        curr_fd = next_fd
                finally:
                    os.close(curr_fd)
            elif entry["kind"] == "file":
                curr_src = os.dup(src_root_fd)
                try:
                    for comp in parts[:-1]:
                        next_src = os.open(comp, os.O_RDONLY | directory_flag | nofollow, dir_fd=curr_src)
                        os.close(curr_src)
                        curr_src = next_src
                    src_fd = os.open(parts[-1], os.O_RDONLY | nofollow, dir_fd=curr_src)
                finally:
                    os.close(curr_src)

                try:
                    src_st = os.fstat(src_fd)
                    if not stat.S_ISREG(src_st.st_mode) or src_st.st_nlink != 1:
                        raise DispatchError(f"source file {rel} is not a valid regular file")
                    source_hasher = hashlib.sha256()
                    source_size = 0

                    curr_dst = os.dup(stage_root_fd)
                    try:
                        for comp in parts[:-1]:
                            try:
                                next_dst = os.open(comp, os.O_RDONLY | directory_flag | nofollow, dir_fd=curr_dst)
                            except FileNotFoundError:
                                os.mkdir(comp, 0o700, dir_fd=curr_dst)
                                next_dst = os.open(comp, os.O_RDONLY | directory_flag | nofollow, dir_fd=curr_dst)
                            os.fchmod(next_dst, 0o700)
                            os.close(curr_dst)
                            curr_dst = next_dst

                        dst_mode = 0o700 if entry["executable"] else 0o600
                        dst_fd = os.open(
                            parts[-1],
                            os.O_WRONLY | os.O_CREAT | os.O_EXCL | nofollow,
                            dst_mode,
                            dir_fd=curr_dst,
                        )
                        try:
                            while True:
                                if time.monotonic() > deadline:
                                    raise DispatchError("stage materialization deadline exceeded")
                                chunk = os.read(src_fd, 65536)
                                if not chunk:
                                    break
                                source_size += len(chunk)
                                copied_bytes += len(chunk)
                                if (
                                    source_size > SELECTED_CONTENT_MAX_FILE_BYTES
                                    or copied_bytes > SELECTED_CONTENT_MAX_TOTAL_BYTES
                                ):
                                    raise DispatchError("stage materialization byte limit exceeded")
                                source_hasher.update(chunk)
                                view = memoryview(chunk)
                                while view:
                                    written = os.write(dst_fd, view)
                                    if written <= 0:
                                        raise DispatchError("stage materialization write failed")
                                    view = view[written:]
                            os.fsync(dst_fd)
                            os.fchmod(dst_fd, dst_mode)
                        finally:
                            os.close(dst_fd)
                    finally:
                        os.close(curr_dst)
                    source_after = os.fstat(src_fd)
                    if (
                        _manifest_binding(source_after) != _manifest_binding(src_st)
                        or source_size != entry["size"]
                        or source_hasher.hexdigest() != entry["sha256"]
                    ):
                        raise DispatchError(f"source file changed during stage copy: {rel}")
                finally:
                    os.close(src_fd)

        rescan = _build_selected_content_manifest(stage_str, scope, is_stage=True)
        if rescan != selected_manifest:
            raise DispatchError("materialized stage content does not match source selected content")

        stage_stat = os.fstat(stage_root_fd)
        identity = (stage_stat.st_dev, stage_stat.st_ino, stage_stat.st_uid, stage_stat.st_gid, stage_stat.st_mode)
        if identity != stage_identity:
            raise DispatchError("stage directory identity changed during materialization")
        return identity, _selected_content_digest(selected_manifest)
    except Exception as materialization_exc:
        if src_root_fd >= 0:
            os.close(src_root_fd)
            src_root_fd = -1
        if stage_root_fd >= 0:
            if stage_identity is not None:
                try:
                    cleanup_st = os.fstat(stage_root_fd)
                    cleanup_identity = (
                        cleanup_st.st_dev, cleanup_st.st_ino, cleanup_st.st_uid,
                        cleanup_st.st_gid, cleanup_st.st_mode,
                    )
                    if (
                        cleanup_identity[:2] == stage_identity[:2]
                        and stat.S_ISDIR(cleanup_st.st_mode)
                        and cleanup_st.st_uid == os.getuid()
                    ):
                        stage_identity = cleanup_identity
                    else:
                        stage_identity = None
                except OSError:
                    stage_identity = None
            os.close(stage_root_fd)
            stage_root_fd = -1
        if stage_identity is None:
            raise DispatchError(
                "stage materialization failed before identity-safe cleanup; cleanup is uncertain"
            ) from materialization_exc
        try:
            _cleanup_stage(stage_str, stage_identity)
        except Exception as cleanup_exc:
            raise DispatchError(
                "stage materialization failed and cleanup is uncertain"
            ) from cleanup_exc
        raise
    finally:
        if src_root_fd >= 0:
            os.close(src_root_fd)
        if stage_root_fd >= 0:
            os.close(stage_root_fd)


def _scan_stage_mutations(
    stage_dir: str | Path, scope: dict[str, Any], pre_launch_manifest: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], str]:
    """Rescan stage, detect mutations, and authorize against scope write policy."""
    directory_flag = getattr(os, "O_DIRECTORY", 0)
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    empty_sha = hashlib.sha256(b"").hexdigest()
    deadline = time.monotonic() + SELECTED_CONTENT_SCAN_SECONDS
    total_bytes = 0

    current_entries: dict[str, dict[str, Any]] = {}

    def scan_all_descriptor(parent_fd: int, rel_prefix: str) -> None:
        nonlocal total_bytes
        if time.monotonic() > deadline:
            raise DispatchError("stage mutation scan deadline exceeded")
        scan_fd = os.dup(parent_fd)
        try:
            with os.scandir(scan_fd) as scanned:
                items = [(entry.name.encode("utf-8"), entry.name) for entry in scanned]
        finally:
            os.close(scan_fd)
        items.sort(key=lambda it: it[0])

        for _name_b, name_str in items:
            if time.monotonic() > deadline:
                raise DispatchError("stage mutation scan deadline exceeded")
            if len(current_entries) >= SELECTED_CONTENT_MAX_ENTRIES:
                raise DispatchError("stage mutation entry limit exceeded")
            rel = posixpath.normpath(posixpath.join(rel_prefix, name_str)) if rel_prefix else name_str
            st = os.stat(name_str, dir_fd=parent_fd, follow_symlinks=False)
            if stat.S_ISLNK(st.st_mode):
                raise DispatchError(f"symlink mutation rejected in stage: {rel}")
            if name_str.lower() in {".git", ".gitmodules"}:
                raise DispatchError(f"git administration mutation rejected in stage: {rel}")
            if name_str.lower() == ".agy-worker-control":
                raise DispatchError(f"control file mutation rejected in stage: {rel}")

            if stat.S_ISDIR(st.st_mode):
                current_entries[rel] = {
                    "executable": False,
                    "kind": "directory",
                    "path": rel,
                    "sha256": empty_sha,
                    "size": 0,
                }
                child_fd = os.open(name_str, os.O_RDONLY | directory_flag | nofollow, dir_fd=parent_fd)
                try:
                    scan_all_descriptor(child_fd, rel)
                finally:
                    os.close(child_fd)
            elif stat.S_ISREG(st.st_mode):
                if st.st_nlink != 1 or st.st_uid != os.getuid():
                    raise DispatchError(f"file metadata mutation rejected in stage: {rel}")
                file_fd = os.open(name_str, os.O_RDONLY | nofollow, dir_fd=parent_fd)
                try:
                    opened = os.fstat(file_fd)
                    if _manifest_binding(opened) != _manifest_binding(st):
                        raise DispatchError(f"stage file changed before read: {rel}")
                    hasher = hashlib.sha256()
                    total_size = 0
                    while True:
                        if time.monotonic() > deadline:
                            raise DispatchError("stage mutation scan deadline exceeded")
                        chunk = os.read(file_fd, 65536)
                        if not chunk:
                            break
                        total_size += len(chunk)
                        total_bytes += len(chunk)
                        if (
                            total_size > SELECTED_CONTENT_MAX_FILE_BYTES
                            or total_bytes > SELECTED_CONTENT_MAX_TOTAL_BYTES
                        ):
                            raise DispatchError("stage mutation byte limit exceeded")
                        hasher.update(chunk)
                    file_sha = hasher.hexdigest()
                    after = os.fstat(file_fd)
                finally:
                    os.close(file_fd)
                named = os.stat(name_str, dir_fd=parent_fd, follow_symlinks=False)
                if (
                    _manifest_binding(opened) != _manifest_binding(after)
                    or _manifest_binding(after) != _manifest_binding(named)
                ):
                    raise DispatchError(f"stage file changed during read: {rel}")
                current_entries[rel] = {
                    "executable": bool(st.st_mode & 0o111),
                    "kind": "file",
                    "path": rel,
                    "sha256": file_sha,
                    "size": total_size,
                }
            else:
                raise DispatchError(f"special node mutation rejected in stage: {rel}")

    root_fd = os.open(str(stage_dir), os.O_RDONLY | directory_flag | nofollow)
    try:
        scan_all_descriptor(root_fd, "")
    finally:
        os.close(root_fd)

    pre_by_path = {e["path"]: e for e in pre_launch_manifest}

    created_paths = sorted(set(current_entries) - set(pre_by_path))
    deleted_paths = sorted(set(pre_by_path) - set(current_entries))
    modified_paths = sorted(
        p for p in (set(current_entries) & set(pre_by_path))
        if current_entries[p]["sha256"] != pre_by_path[p]["sha256"]
        or current_entries[p]["executable"] != pre_by_path[p]["executable"]
        or current_entries[p]["kind"] != pre_by_path[p]["kind"]
    )
    for path in modified_paths:
        if current_entries[path]["kind"] != pre_by_path[path]["kind"]:
            raise DispatchError(f"stage path kind change rejected: {path}")

    def is_authorized_write(p: str, kind: str) -> bool:
        for w in scope["write"]:
            if w["kind"] == kind and w["path"] == p:
                return True
            if w["kind"] == "tree" and (p == w["path"] or p.startswith(w["path"] + "/")):
                return True
        return False

    for p in modified_paths:
        if not is_authorized_write(p, current_entries[p]["kind"]):
            raise DispatchError(f"unauthorized modification of path: {p}")

    for p in created_paths:
        if not is_authorized_write(p, current_entries[p]["kind"]):
            raise DispatchError(f"unauthorized creation of path: {p}")

    for p in deleted_paths:
        if not is_authorized_write(p, pre_by_path[p]["kind"]):
            raise DispatchError(f"unauthorized deletion of path: {p}")

    operations: list[dict[str, Any]] = []

    created_dirs = sorted([p for p in created_paths if current_entries[p]["kind"] == "directory"], key=lambda p: p.count("/"))
    for p in created_dirs:
        operations.append({
            "executable": False,
            "kind": "directory",
            "op": "create",
            "path": p,
            "post_identity": None,
            "prior_identity": None,
            "post_sha256": empty_sha,
            "prior_sha256": None,
            "sha256": empty_sha,
            "size": 0,
        })

    created_files = sorted([p for p in created_paths if current_entries[p]["kind"] == "file"])
    for p in created_files:
        operations.append({
            "executable": current_entries[p]["executable"],
            "kind": "file",
            "op": "create",
            "path": p,
            "post_identity": None,
            "prior_identity": None,
            "post_sha256": current_entries[p]["sha256"],
            "prior_sha256": None,
            "sha256": current_entries[p]["sha256"],
            "size": current_entries[p]["size"],
        })

    for p in modified_paths:
        operations.append({
            "executable": current_entries[p]["executable"],
            "kind": "file",
            "op": "replace",
            "path": p,
            "post_identity": None,
            "prior_identity": None,
            "post_sha256": current_entries[p]["sha256"],
            "prior_sha256": pre_by_path[p]["sha256"],
            "sha256": current_entries[p]["sha256"],
            "size": current_entries[p]["size"],
        })

    deleted_files = sorted([p for p in deleted_paths if pre_by_path[p]["kind"] == "file"])
    for p in deleted_files:
        operations.append({
            "executable": pre_by_path[p]["executable"],
            "kind": "file",
            "op": "delete",
            "path": p,
            "post_identity": None,
            "prior_identity": None,
            "post_sha256": None,
            "prior_sha256": pre_by_path[p]["sha256"],
            "sha256": pre_by_path[p]["sha256"],
            "size": pre_by_path[p]["size"],
        })

    deleted_dirs = sorted([p for p in deleted_paths if pre_by_path[p]["kind"] == "directory"], key=lambda p: -p.count("/"))
    for p in deleted_dirs:
        operations.append({
            "executable": False,
            "kind": "directory",
            "op": "delete",
            "path": p,
            "post_identity": None,
            "prior_identity": None,
            "post_sha256": None,
            "prior_sha256": empty_sha,
            "sha256": empty_sha,
            "size": 0,
        })

    if len(operations) > RECONCILIATION_MAX_OPERATIONS:
        raise DispatchError("reconciliation operation limit exceeded")

    raw_manifest = json.dumps(operations, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("ascii") + b"\n"
    op_sha = hashlib.sha256(raw_manifest).hexdigest()
    return operations, op_sha


def _reconciliation_write_all(descriptor: int, payload: bytes) -> None:
    view = memoryview(payload)
    while view:
        written = os.write(descriptor, view)
        if written <= 0:
            raise DispatchError("reconciliation durable write failed")
        view = view[written:]


def _persist_reconciliation_ledger(job_fd: int, ledger: dict[str, Any]) -> None:
    """Durably replace the owner-private recovery marker."""
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    raw = _canonical_json(ledger) + b"\n"
    if len(raw) > READABLE_MANIFEST_MAX_BYTES:
        raise DispatchError("reconciliation ledger is oversized")
    tmp = f"reconciliation-marker.{os.getpid()}.{time.time_ns()}.tmp"
    descriptor = os.open(
        tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | nofollow,
        0o600, dir_fd=job_fd,
    )
    try:
        _reconciliation_write_all(descriptor, raw)
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    os.replace(
        tmp, "reconciliation-in-progress.json",
        src_dir_fd=job_fd, dst_dir_fd=job_fd,
    )
    os.fsync(job_fd)


def _reconciliation_parts(value: Any) -> list[str]:
    if not isinstance(value, str) or not value or value.startswith("/"):
        raise DispatchError("reconciliation ledger path is invalid")
    parts = value.split("/")
    if (
        posixpath.normpath(value) != value
        or any(part in {"", ".", ".."} for part in parts)
        or any(part.casefold() in {".git", ".gitmodules", ".agy-worker-control"} for part in parts)
    ):
        raise DispatchError("reconciliation ledger path is invalid")
    return parts


def _reconciliation_root_identity(info: os.stat_result) -> list[int]:
    return [info.st_dev, info.st_ino, info.st_uid, info.st_gid, info.st_mode]


def _reconciliation_parent(root_fd: int, parts: list[str]) -> int:
    directory_flag = getattr(os, "O_DIRECTORY", 0)
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    current = os.dup(root_fd)
    try:
        for component in parts[:-1]:
            child = os.open(
                component, os.O_RDONLY | directory_flag | nofollow, dir_fd=current,
            )
            os.close(current)
            current = child
        return current
    except Exception:
        os.close(current)
        raise


def _reconciliation_stat(root_fd: int, parts: list[str]) -> os.stat_result | None:
    parent = _reconciliation_parent(root_fd, parts)
    try:
        try:
            return os.stat(parts[-1], dir_fd=parent, follow_symlinks=False)
        except FileNotFoundError:
            return None
    finally:
        os.close(parent)


def _reconciliation_file_digest(root_fd: int, parts: list[str]) -> tuple[str, int]:
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    parent = _reconciliation_parent(root_fd, parts)
    try:
        descriptor = os.open(parts[-1], os.O_RDONLY | nofollow, dir_fd=parent)
    finally:
        os.close(parent)
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
            raise DispatchError("reconciliation file authority is invalid")
        hasher = hashlib.sha256()
        total = 0
        while True:
            chunk = os.read(descriptor, 65536)
            if not chunk:
                break
            total += len(chunk)
            if total > SELECTED_CONTENT_MAX_FILE_BYTES:
                raise DispatchError("reconciliation file is oversized")
            hasher.update(chunk)
        return hasher.hexdigest(), stat.S_IMODE(metadata.st_mode)
    finally:
        os.close(descriptor)


def _finish_reconciliation_recovery(
    job_fd: int, recovery_fd: int, ledger: dict[str, Any],
) -> None:
    """Remove only the exact backup artifacts named by a verified ledger."""
    expected = {
        record["name"] for record in ledger["backups"].values()
        if isinstance(record, dict) and isinstance(record.get("name"), str)
    }
    scan_fd = os.dup(recovery_fd)
    try:
        with os.scandir(scan_fd) as entries:
            actual = {entry.name for entry in entries}
    finally:
        os.close(scan_fd)
    if not actual <= expected:
        raise DispatchError("reconciliation backup directory contents changed")
    for name in sorted(actual):
        os.unlink(name, dir_fd=recovery_fd)
    os.fsync(recovery_fd)
    os.rmdir("reconciliation-backups", dir_fd=job_fd)
    os.unlink("reconciliation-in-progress.json", dir_fd=job_fd)
    os.fsync(job_fd)


def _restore_reconciliation_prior(
    src_root_fd: int, recovery_fd: int, job_fd: int, ledger: dict[str, Any],
) -> None:
    """Restore and verify the ledger's exact pre-reconciliation path state."""
    directory_flag = getattr(os, "O_DIRECTORY", 0)
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    operations = ledger["operation_manifest"]
    backups = ledger["backups"]
    directory_backups = ledger["directory_backups"]
    active = ledger.get("active_operation")

    ledger["status"] = "rollback-restoring"
    _persist_reconciliation_ledger(job_fd, ledger)

    # Remove only entries created by this transaction and bound after creation.
    for index in range(len(operations) - 1, -1, -1):
        operation = operations[index]
        if operation["op"] != "create":
            continue
        parts = _reconciliation_parts(operation["path"])
        current = _reconciliation_stat(src_root_fd, parts)
        if current is None:
            continue
        if (
            operation.get("post_identity") is None
            or list(_manifest_binding(current)) != operation["post_identity"]
        ):
            raise DispatchError("reconciliation created target identity is uncertain")
        parent = _reconciliation_parent(src_root_fd, parts)
        try:
            if operation["kind"] == "file":
                os.unlink(parts[-1], dir_fd=parent)
            else:
                os.rmdir(parts[-1], dir_fd=parent)
            os.fsync(parent)
        finally:
            os.close(parent)

    # Restore deleted empty directories shallow-first, preserving their mode.
    for rel in sorted(directory_backups, key=lambda item: (item.count("/"), item)):
        record = directory_backups[rel]
        if (
            not isinstance(record, dict)
            or type(record.get("mode")) is not int
            or not isinstance(record.get("prior_identity"), list)
            or len(record["prior_identity"]) != 5
        ):
            raise DispatchError("reconciliation directory backup is invalid")
        parts = _reconciliation_parts(rel)
        current = _reconciliation_stat(src_root_fd, parts)
        if current is None:
            record["recreate_pending"] = True
            _persist_reconciliation_ledger(job_fd, ledger)
            parent = _reconciliation_parent(src_root_fd, parts)
            try:
                os.mkdir(parts[-1], record["mode"], dir_fd=parent)
                child = os.open(
                    parts[-1], os.O_RDONLY | directory_flag | nofollow, dir_fd=parent,
                )
                try:
                    os.fchmod(child, record["mode"])
                    os.fsync(child)
                    restored = os.fstat(child)
                finally:
                    os.close(child)
                os.fsync(parent)
            finally:
                os.close(parent)
            record["rollback_identity"] = _reconciliation_root_identity(restored)
            record.pop("recreate_pending", None)
            _persist_reconciliation_ledger(job_fd, ledger)
        else:
            current_identity = _reconciliation_root_identity(current)
            pending_recreation = bool(record.get("recreate_pending"))
            if pending_recreation:
                scan_parent = _reconciliation_parent(src_root_fd, parts)
                try:
                    child = os.open(
                        parts[-1], os.O_RDONLY | directory_flag | nofollow,
                        dir_fd=scan_parent,
                    )
                finally:
                    os.close(scan_parent)
                try:
                    scan_fd = os.dup(child)
                    try:
                        with os.scandir(scan_fd) as entries:
                            is_empty = next(entries, None) is None
                    finally:
                        os.close(scan_fd)
                finally:
                    os.close(child)
                if not is_empty:
                    raise DispatchError("reconciliation pending directory is not empty")
            if (
                not stat.S_ISDIR(current.st_mode)
                or stat.S_IMODE(current.st_mode) != record["mode"]
                or current_identity not in (
                    record["prior_identity"], record.get("rollback_identity"),
                )
                and not pending_recreation
            ):
                raise DispatchError("reconciliation directory restoration is uncertain")
            if pending_recreation:
                record["rollback_identity"] = current_identity
                record.pop("recreate_pending", None)
                _persist_reconciliation_ledger(job_fd, ledger)

    # Restore every replaced/deleted file from its owner-private durable backup.
    for rel, record in backups.items():
        if (
            not isinstance(record, dict)
            or type(record.get("mode")) is not int
            or not isinstance(record.get("name"), str)
            or not isinstance(record.get("prior_identity"), list)
            or not isinstance(record.get("prior_sha256"), str)
        ):
            raise DispatchError("reconciliation file backup is invalid")
        parts = _reconciliation_parts(rel)
        backup_fd = os.open(record["name"], os.O_RDONLY | nofollow, dir_fd=recovery_fd)
        try:
            metadata = os.fstat(backup_fd)
            if (
                not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1
                or metadata.st_uid != os.getuid()
            ):
                raise DispatchError("reconciliation backup authority is invalid")
            content = bytearray()
            hasher = hashlib.sha256()
            while True:
                chunk = os.read(backup_fd, 65536)
                if not chunk:
                    break
                content.extend(chunk)
                if len(content) > SELECTED_CONTENT_MAX_FILE_BYTES:
                    raise DispatchError("reconciliation backup is oversized")
                hasher.update(chunk)
            if hasher.hexdigest() != record["prior_sha256"]:
                raise DispatchError("reconciliation backup content changed")
        finally:
            os.close(backup_fd)
        current = _reconciliation_stat(src_root_fd, parts)
        operation_index = next(
            (index for index, item in enumerate(operations) if item["path"] == rel), None,
        )
        operation = operations[operation_index] if operation_index is not None else None
        allowed = current is None
        if current is not None and operation is not None:
            identity = list(_manifest_binding(current))
            allowed = identity in (
                record["prior_identity"], operation.get("post_identity"),
                record.get("rollback_identity"),
            )
            if not allowed and active == operation_index and stat.S_ISREG(current.st_mode):
                current_sha, _current_mode = _reconciliation_file_digest(src_root_fd, parts)
                allowed = current_sha in {record["prior_sha256"], operation.get("post_sha256")}
            if not allowed and record.get("restore_pending") and stat.S_ISREG(current.st_mode):
                current_sha, current_mode = _reconciliation_file_digest(src_root_fd, parts)
                allowed = current_sha == record["prior_sha256"] and current_mode == record["mode"]
        if not allowed:
            raise DispatchError("reconciliation file restoration identity is uncertain")
        record["restore_pending"] = True
        _persist_reconciliation_ledger(job_fd, ledger)
        parent = _reconciliation_parent(src_root_fd, parts)
        try:
            tmp = f".tmp.rollback.{os.getpid()}.{time.time_ns()}"
            tmp_fd = os.open(
                tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | nofollow,
                record["mode"], dir_fd=parent,
            )
            try:
                _reconciliation_write_all(tmp_fd, content)
                os.fchmod(tmp_fd, record["mode"])
                os.fsync(tmp_fd)
            finally:
                os.close(tmp_fd)
            os.replace(tmp, parts[-1], src_dir_fd=parent, dst_dir_fd=parent)
            os.fsync(parent)
            restored = os.stat(parts[-1], dir_fd=parent, follow_symlinks=False)
        finally:
            os.close(parent)
        record["rollback_identity"] = list(_manifest_binding(restored))
        record.pop("restore_pending", None)
        _persist_reconciliation_ledger(job_fd, ledger)

    # Do not clear evidence until every manifest path exactly matches its prior state.
    for operation in operations:
        parts = _reconciliation_parts(operation["path"])
        current = _reconciliation_stat(src_root_fd, parts)
        if operation["op"] == "create":
            if current is not None:
                raise DispatchError("reconciliation rollback left a created target")
        elif operation["kind"] == "directory":
            record = directory_backups[operation["path"]]
            if (
                current is None or not stat.S_ISDIR(current.st_mode)
                or stat.S_IMODE(current.st_mode) != record["mode"]
                or _reconciliation_root_identity(current) not in (
                    record["prior_identity"], record.get("rollback_identity"),
                )
            ):
                raise DispatchError("reconciliation directory rollback verification failed")
        else:
            record = backups[operation["path"]]
            if current is None or not stat.S_ISREG(current.st_mode):
                raise DispatchError("reconciliation file rollback verification failed")
            current_sha, current_mode = _reconciliation_file_digest(src_root_fd, parts)
            if current_sha != record["prior_sha256"] or current_mode != record["mode"]:
                raise DispatchError("reconciliation file rollback verification failed")

    ledger["status"] = "rolled-back-verified"
    ledger.pop("active_operation", None)
    _persist_reconciliation_ledger(job_fd, ledger)


def _recover_reconciliation(source_root: str | Path, job_dir: Path) -> bool:
    """Recover a durable transaction; a second call is an idempotent no-op."""
    directory_flag = getattr(os, "O_DIRECTORY", 0)
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    src_root_fd = os.open(str(source_root), os.O_RDONLY | directory_flag | nofollow)
    job_fd = os.open(str(job_dir), os.O_RDONLY | directory_flag | nofollow)
    recovery_fd = -1
    try:
        try:
            marker_fd = os.open(
                "reconciliation-in-progress.json", os.O_RDONLY | nofollow, dir_fd=job_fd,
            )
        except FileNotFoundError:
            return False
        try:
            metadata = os.fstat(marker_fd)
            if (
                not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1
                or metadata.st_uid != os.getuid() or stat.S_IMODE(metadata.st_mode) & 0o077
                or metadata.st_size > READABLE_MANIFEST_MAX_BYTES
            ):
                raise DispatchError("reconciliation ledger authority is invalid")
            raw = bytearray()
            while True:
                chunk = os.read(marker_fd, 65536)
                if not chunk:
                    break
                raw.extend(chunk)
                if len(raw) > READABLE_MANIFEST_MAX_BYTES:
                    raise DispatchError("reconciliation ledger is oversized")
        finally:
            os.close(marker_fd)
        try:
            ledger = json.loads(bytes(raw))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise DispatchError("reconciliation ledger is invalid") from exc
        if (
            not isinstance(ledger, dict) or bytes(raw) != _canonical_json(ledger) + b"\n"
            or ledger.get("schema_version") != 1
            or ledger.get("source_root") != str(source_root)
            or not isinstance(ledger.get("operation_manifest"), list)
            or len(ledger["operation_manifest"]) > RECONCILIATION_MAX_OPERATIONS
            or not isinstance(ledger.get("backups"), dict)
            or not isinstance(ledger.get("directory_backups"), dict)
        ):
            raise DispatchError("reconciliation ledger is invalid")
        if _reconciliation_root_identity(os.fstat(src_root_fd)) != ledger.get("source_root_identity"):
            raise DispatchError("reconciliation source root identity changed")
        for operation in ledger["operation_manifest"]:
            if (
                not isinstance(operation, dict)
                or operation.get("op") not in {"create", "replace", "delete"}
                or operation.get("kind") not in {"file", "directory"}
            ):
                raise DispatchError("reconciliation ledger operation is invalid")
            _reconciliation_parts(operation.get("path"))
        active = ledger.get("active_operation")
        if active is not None and (
            type(active) is not int or not 0 <= active < len(ledger["operation_manifest"])
        ):
            raise DispatchError("reconciliation active operation is invalid")
        recovery_fd = os.open(
            "reconciliation-backups", os.O_RDONLY | directory_flag | nofollow, dir_fd=job_fd,
        )
        recovery_metadata = os.fstat(recovery_fd)
        if (
            _reconciliation_root_identity(recovery_metadata) != ledger.get("backup_dir_identity")
            or recovery_metadata.st_uid != os.getuid()
            or stat.S_IMODE(recovery_metadata.st_mode) != 0o700
        ):
            raise DispatchError("reconciliation backup directory identity changed")
        if ledger.get("status") not in {"committed", "rolled-back-verified"}:
            _restore_reconciliation_prior(src_root_fd, recovery_fd, job_fd, ledger)
        _finish_reconciliation_recovery(job_fd, recovery_fd, ledger)
        os.close(recovery_fd)
        recovery_fd = -1
        return True
    except DispatchError:
        raise
    except (OSError, TypeError, ValueError) as exc:
        raise DispatchError("reconciliation recovery is uncertain") from exc
    finally:
        if recovery_fd >= 0:
            os.close(recovery_fd)
        os.close(src_root_fd)
        os.close(job_fd)


def _reconcile_stage_to_source(
    source_root: str | Path, stage_dir: str | Path, operation_manifest: list[dict[str, Any]], job_dir: Path,
) -> str:
    """Apply operation manifest descriptor-relative to source with durable rollback."""
    _recover_reconciliation(source_root, job_dir)
    if not operation_manifest:
        return _selected_content_digest([])
    if len(operation_manifest) > RECONCILIATION_MAX_OPERATIONS:
        raise DispatchError("reconciliation operation limit exceeded")
    directory_flag = getattr(os, "O_DIRECTORY", 0)
    nofollow = getattr(os, "O_NOFOLLOW", 0)

    src_root_fd = os.open(str(source_root), os.O_RDONLY | directory_flag | nofollow)
    stage_root_fd = os.open(str(stage_dir), os.O_RDONLY | directory_flag | nofollow)
    job_fd = os.open(str(job_dir), os.O_RDONLY | directory_flag | nofollow)

    marker_name = "reconciliation-in-progress.json"
    backup_dir_name = "reconciliation-backups"
    recovery_fd = -1

    ledger: dict[str, Any] = {
        "schema_version": 1,
        "applied_operations": 0,
        "backups": {},
        "directory_backups": {},
        "operation_manifest": operation_manifest,
        "source_root": str(source_root),
        "source_root_identity": _reconciliation_root_identity(os.fstat(src_root_fd)),
        "stage_dir": str(stage_dir),
        "status": "preparing",
    }

    def persist_ledger() -> None:
        _persist_reconciliation_ledger(job_fd, ledger)

    try:
        try:
            os.stat(marker_name, dir_fd=job_fd, follow_symlinks=False)
        except FileNotFoundError:
            pass
        else:
            raise DispatchError("unfinished reconciliation requires recovery")
        os.mkdir(backup_dir_name, 0o700, dir_fd=job_fd)
        recovery_fd = os.open(
            backup_dir_name, os.O_RDONLY | directory_flag | nofollow, dir_fd=job_fd,
        )
        ledger["backup_dir_identity"] = _reconciliation_root_identity(os.fstat(recovery_fd))

        backups: dict[str, dict[str, Any]] = {}
        directory_backups: dict[str, dict[str, Any]] = {}
        for index, op in enumerate(operation_manifest):
            parts = _reconciliation_parts(op["path"])
            curr_src = os.dup(src_root_fd)
            try:
                for comp in parts[:-1]:
                    next_src = os.open(
                        comp, os.O_RDONLY | directory_flag | nofollow, dir_fd=curr_src,
                    )
                    os.close(curr_src)
                    curr_src = next_src
                try:
                    prior = os.stat(parts[-1], dir_fd=curr_src, follow_symlinks=False)
                except FileNotFoundError:
                    prior = None
            finally:
                os.close(curr_src)
            if op["op"] == "create":
                if prior is not None:
                    raise DispatchError("reconciliation create target already exists")
                op["prior_identity"] = None
            else:
                if prior is None or stat.S_ISLNK(prior.st_mode):
                    raise DispatchError("reconciliation prior target is unavailable")
                if (op["kind"] == "file") != stat.S_ISREG(prior.st_mode):
                    raise DispatchError("reconciliation prior target changed kind")
                if op["kind"] == "directory" and not stat.S_ISDIR(prior.st_mode):
                    raise DispatchError("reconciliation prior target changed kind")
                op["prior_identity"] = list(_manifest_binding(prior))
                if op["op"] == "delete" and op["kind"] == "directory":
                    directory_backups[op["path"]] = {
                        "mode": stat.S_IMODE(prior.st_mode),
                        "prior_identity": _reconciliation_root_identity(prior),
                    }
            if op["op"] in {"replace", "delete"} and op["kind"] == "file":
                curr_src = os.dup(src_root_fd)
                try:
                    for comp in parts[:-1]:
                        next_src = os.open(comp, os.O_RDONLY | directory_flag | nofollow, dir_fd=curr_src)
                        os.close(curr_src)
                        curr_src = next_src
                    try:
                        f_fd = os.open(parts[-1], os.O_RDONLY | nofollow, dir_fd=curr_src)
                    except FileNotFoundError:
                        f_fd = -1
                finally:
                    os.close(curr_src)
                if f_fd >= 0:
                    try:
                        st = os.fstat(f_fd)
                        backup_name = f"{index:06d}.backup"
                        backup_fd = os.open(
                            backup_name,
                            os.O_WRONLY | os.O_CREAT | os.O_EXCL | nofollow,
                            0o600, dir_fd=recovery_fd,
                        )
                        try:
                            hasher = hashlib.sha256()
                            total = 0
                            while True:
                                chunk = os.read(f_fd, 65536)
                                if not chunk:
                                    break
                                total += len(chunk)
                                if total > SELECTED_CONTENT_MAX_FILE_BYTES:
                                    raise DispatchError("reconciliation backup byte limit exceeded")
                                hasher.update(chunk)
                                _reconciliation_write_all(backup_fd, chunk)
                            os.fsync(backup_fd)
                        finally:
                            os.close(backup_fd)
                        if hasher.hexdigest() != op["prior_sha256"]:
                            raise DispatchError("reconciliation prior content changed")
                        backups[op["path"]] = {
                            "mode": stat.S_IMODE(st.st_mode),
                            "name": backup_name,
                            "prior_identity": op["prior_identity"],
                            "prior_sha256": op["prior_sha256"],
                        }
                    finally:
                        os.close(f_fd)

        os.fsync(recovery_fd)
        ledger["backups"] = backups
        ledger["directory_backups"] = directory_backups
        ledger["status"] = "prepared"
        persist_ledger()

        try:
            for operation_index, op in enumerate(operation_manifest):
                rel = op["path"]
                parts = rel.split("/")
                ledger["status"] = "applying"
                ledger["active_operation"] = operation_index
                persist_ledger()

                check_fd = os.dup(src_root_fd)
                try:
                    for comp in parts[:-1]:
                        next_fd = os.open(
                            comp, os.O_RDONLY | directory_flag | nofollow,
                            dir_fd=check_fd,
                        )
                        os.close(check_fd)
                        check_fd = next_fd
                    try:
                        current_prior = os.stat(
                            parts[-1], dir_fd=check_fd, follow_symlinks=False,
                        )
                    except FileNotFoundError:
                        current_prior = None
                finally:
                    os.close(check_fd)
                if op["op"] == "create":
                    if current_prior is not None:
                        raise DispatchError("reconciliation create target drifted")
                elif (
                    current_prior is None
                    or list(_manifest_binding(current_prior)) != op["prior_identity"]
                ):
                    raise DispatchError("reconciliation prior target identity drifted")

                if op["op"] == "create" and op["kind"] == "directory":
                    curr_fd = os.dup(src_root_fd)
                    try:
                        for comp in parts:
                            try:
                                next_fd = os.open(comp, os.O_RDONLY | directory_flag | nofollow, dir_fd=curr_fd)
                            except FileNotFoundError:
                                os.mkdir(comp, 0o700, dir_fd=curr_fd)
                                next_fd = os.open(comp, os.O_RDONLY | directory_flag | nofollow, dir_fd=curr_fd)
                            os.fchmod(next_fd, 0o700)
                            os.fsync(curr_fd)
                            os.close(curr_fd)
                            curr_fd = next_fd
                    finally:
                        os.close(curr_fd)
                elif op["op"] in {"create", "replace"} and op["kind"] == "file":
                    curr_stg = os.dup(stage_root_fd)
                    try:
                        for comp in parts[:-1]:
                            next_stg = os.open(comp, os.O_RDONLY | directory_flag | nofollow, dir_fd=curr_stg)
                            os.close(curr_stg)
                            curr_stg = next_stg
                        stg_fd = os.open(parts[-1], os.O_RDONLY | nofollow, dir_fd=curr_stg)
                    finally:
                        os.close(curr_stg)
                    try:
                        content = bytearray()
                        while True:
                            chunk = os.read(stg_fd, 65536)
                            if not chunk:
                                break
                            content.extend(chunk)
                    finally:
                        os.close(stg_fd)

                    curr_src = os.dup(src_root_fd)
                    try:
                        for comp in parts[:-1]:
                            try:
                                next_src = os.open(comp, os.O_RDONLY | directory_flag | nofollow, dir_fd=curr_src)
                            except FileNotFoundError:
                                os.mkdir(comp, 0o700, dir_fd=curr_src)
                                next_src = os.open(comp, os.O_RDONLY | directory_flag | nofollow, dir_fd=curr_src)
                            os.fchmod(next_src, 0o700)
                            os.close(curr_src)
                            curr_src = next_src

                        tmp_name = f".tmp.reconcile.{os.getpid()}.{time.time_ns()}"
                        mode = 0o700 if op["executable"] else 0o600
                        tmp_fd = os.open(tmp_name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | nofollow, mode, dir_fd=curr_src)
                        try:
                            _reconciliation_write_all(tmp_fd, content)
                            os.fsync(tmp_fd)
                            os.fchmod(tmp_fd, mode)
                        finally:
                            os.close(tmp_fd)
                        os.replace(tmp_name, parts[-1], src_dir_fd=curr_src, dst_dir_fd=curr_src)
                        os.fsync(curr_src)
                    finally:
                        os.close(curr_src)
                elif op["op"] == "delete" and op["kind"] == "file":
                    curr_src = os.dup(src_root_fd)
                    try:
                        for comp in parts[:-1]:
                            next_src = os.open(comp, os.O_RDONLY | directory_flag | nofollow, dir_fd=curr_src)
                            os.close(curr_src)
                            curr_src = next_src
                        with contextlib.suppress(FileNotFoundError):
                            os.unlink(parts[-1], dir_fd=curr_src)
                            os.fsync(curr_src)
                    finally:
                        os.close(curr_src)
                elif op["op"] == "delete" and op["kind"] == "directory":
                    curr_src = os.dup(src_root_fd)
                    try:
                        for comp in parts[:-1]:
                            next_src = os.open(comp, os.O_RDONLY | directory_flag | nofollow, dir_fd=curr_src)
                            os.close(curr_src)
                            curr_src = next_src
                        with contextlib.suppress(FileNotFoundError):
                            os.rmdir(parts[-1], dir_fd=curr_src)
                            os.fsync(curr_src)
                    finally:
                        os.close(curr_src)

                post_fd = os.dup(src_root_fd)
                try:
                    for comp in parts[:-1]:
                        next_fd = os.open(
                            comp, os.O_RDONLY | directory_flag | nofollow,
                            dir_fd=post_fd,
                        )
                        os.close(post_fd)
                        post_fd = next_fd
                    try:
                        post = os.stat(
                            parts[-1], dir_fd=post_fd, follow_symlinks=False,
                        )
                    except FileNotFoundError:
                        post = None
                finally:
                    os.close(post_fd)
                if op["op"] == "delete":
                    if post is not None:
                        raise DispatchError("reconciliation delete target remains")
                    op["post_identity"] = None
                else:
                    if post is None or stat.S_ISLNK(post.st_mode):
                        raise DispatchError("reconciliation post target is unavailable")
                    op["post_identity"] = list(_manifest_binding(post))
                ledger["applied_operations"] = operation_index + 1
                ledger.pop("active_operation", None)
                persist_ledger()
        except Exception as exc:
            ledger["status"] = "rollback-required"
            try:
                persist_ledger()
                os.close(recovery_fd)
                recovery_fd = -1
                _recover_reconciliation(source_root, job_dir)
            except Exception as recovery_exc:
                raise DispatchError(
                    "reconciliation rollback failed; recovery uncertain"
                ) from recovery_exc
            raise DispatchError(f"reconciliation failed and was rolled back: {exc}") from exc

        ledger["status"] = "committed"
        ledger.pop("active_operation", None)
        persist_ledger()
        final_manifest_sha = hashlib.sha256(
            json.dumps(
                operation_manifest, ensure_ascii=True, sort_keys=True,
                separators=(",", ":"),
            ).encode("ascii") + b"\n"
        ).hexdigest()
        _finish_reconciliation_recovery(job_fd, recovery_fd, ledger)
        os.close(recovery_fd)
        recovery_fd = -1
        return final_manifest_sha
    finally:
        if recovery_fd >= 0:
            os.close(recovery_fd)
        os.close(src_root_fd)
        os.close(stage_root_fd)
        os.close(job_fd)


def _cleanup_stage(stage_dir: str | Path, recorded_identity: tuple[int, int, int, int, int]) -> None:
    """Safely and boundly clean up a materialized stage directory."""
    directory_flag = getattr(os, "O_DIRECTORY", 0)
    nofollow = getattr(os, "O_NOFOLLOW", 0)

    stg_str = str(stage_dir)
    stage_root_fd = os.open(stg_str, os.O_RDONLY | directory_flag | nofollow)
    try:
        st = os.fstat(stage_root_fd)
        current_id = (st.st_dev, st.st_ino, st.st_uid, st.st_gid, st.st_mode)
        if current_id != recorded_identity:
            raise DispatchError("stage directory identity changed; cleanup refused")

        def remove_dir_contents(parent_fd: int) -> None:
            scan_fd = os.dup(parent_fd)
            try:
                with os.scandir(scan_fd) as scanned:
                    items = [(entry.name.encode("utf-8"), entry.name) for entry in scanned]
            finally:
                os.close(scan_fd)
            for _name_b, name_str in items:
                child_st = os.stat(name_str, dir_fd=parent_fd, follow_symlinks=False)
                if stat.S_ISLNK(child_st.st_mode):
                    raise DispatchError(f"symlink mutation inside stage refused in cleanup: {name_str}")
                if stat.S_ISDIR(child_st.st_mode):
                    child_fd = os.open(name_str, os.O_RDONLY | directory_flag | nofollow, dir_fd=parent_fd)
                    try:
                        remove_dir_contents(child_fd)
                    finally:
                        os.close(child_fd)
                    os.rmdir(name_str, dir_fd=parent_fd)
                else:
                    os.unlink(name_str, dir_fd=parent_fd)

        remove_dir_contents(stage_root_fd)
    finally:
        os.close(stage_root_fd)

    os.rmdir(stg_str)


_IMPLEMENTATION_FUNCTIONS = frozenset({
    "_marker_only_preflight",
    "_resolved_path_is_git_administration",
    "_worktree_symlink_boundary",
    "_worktree_git_admin_alias_boundary",
    "_project_boundary",
    "_safe_git_owner_mode",
    "_safe_git_executable",
    "_confirm_safe_git_executable",
    "_safe_git_is_outside_worktree",
    "_stable_git_authority",
    "_full_stat_binding",
    "_bound_git_worktree_root",
    "_fixed_git_read_argv",
    "_bounded_git_read",
    "_git_boundary_identity",
    "_worktree_snapshot",
    "_scan_readable_worktree",
    "_validate_manifest",
    "_manifest_digest",
    "_parse_provider_scope",
    "_validate_scope_against_worktree",
    "_build_selected_content_manifest",
    "_canonical_digest",
    "_selected_content_digest",
    "_compute_transmission_sha256",
    "_materialize_stage",
    "_scan_stage_mutations",
    "_recover_reconciliation",
    "_reconcile_stage_to_source",
    "_cleanup_stage",
})
_IMPLEMENTATION_DEFAULTS = {
    name: globals()[name] for name in _IMPLEMENTATION_FUNCTIONS
}


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "transmission-preview":
        raise SystemExit(_preview_main(sys.argv[2:]))
    print("agy-worker.sh: transmission preview unavailable", file=sys.stderr)
    raise SystemExit(64)
