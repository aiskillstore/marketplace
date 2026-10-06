#!/usr/bin/env python3
"""Canonical Git-visible candidate-state digest shared by gate and lifecycle."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import select
import stat
import subprocess
import sys
import time
from typing import Callable, TypedDict

sys.dont_write_bytecode = True

# Shared with lifecycle: caller PATH must not select the candidate authority.
GIT_EXECUTABLE = "/usr/bin/git"

COMMIT_RE = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})")


class CandidateStateError(ValueError):
    pass


class CandidateStateLimitError(CandidateStateError):
    """A bounded proof could not complete; callers must preserve the candidate."""


class GitCommitState(TypedDict):
    branch: str
    head: str
    entries: list[list[str]]


GitReader = Callable[[Path, str], bytes]


def _checked_git_reader(repo: Path) -> Callable[..., bytes]:
    # Caller Git variables can redirect even `git -C`; local configuration can
    # execute helpers or make a dirty worktree appear clean. A reader belongs
    # to one invocation only; never carry it across driver verification.
    environment = {key: value for key, value in os.environ.items()
                   if not key.startswith("GIT_")}
    environment.update({
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_TERMINAL_PROMPT": "0",
        "GIT_NO_LAZY_FETCH": "1",
        "GIT_NO_REPLACE_OBJECTS": "1",
    })
    command = [
        GIT_EXECUTABLE, "--no-pager", "-C", str(repo),
        "-c", "core.fsmonitor=false",
        "-c", f"core.hooksPath={os.devnull}",
        "-c", "core.untrackedCache=false",
        "-c", "color.ui=false",
        "-c", "core.pager=cat",
        "-c", "credential.helper=",
        "-c", "protocol.allow=never",
        "-c", "submodule.recurse=false",
        "-c", "fetch.recurseSubmodules=false",
    ]

    def run(args: tuple[str, ...]) -> subprocess.CompletedProcess[bytes]:
        try:
            return subprocess.run(
                [*command, *args], env=environment,
                stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL, check=False,
            )
        except OSError as exc:
            raise CandidateStateError("git candidate-state probe failed") from exc

    # --includes follows effective include/includeIf and worktree configuration.
    # Ask only for names: values may contain commands or private material. Any
    # definition is unsafe here, including empty clean/process or required=false.
    filters = run(("config", "--includes", "--name-only", "--get-regexp",
                   r"^filter\..*\.(clean|process|required)$"))
    if filters.returncode == 0:
        raise CandidateStateError(
            "repository content-filter configuration is unsupported by the gate; "
            "remove effective filter.*.clean/process/required definitions from "
            "the review worktree configuration (including includes) before retrying"
        )
    if filters.returncode != 1:
        raise CandidateStateError("cannot inspect repository content-filter configuration")
    def read(
        _repo: Path, *arguments: str,
        max_output_bytes: int | None = None,
        timeout_seconds: float | None = None,
    ) -> bytes:
        if _repo != repo:
            raise CandidateStateError("git reader repository mismatch")
        if arguments and arguments[0] == "diff":
            arguments = ("diff", "--no-ext-diff", "--no-textconv", *arguments[1:])
        if max_output_bytes is None:
            completed = run(arguments)
            if completed.returncode != 0:
                raise CandidateStateError("git candidate-state probe failed")
            return completed.stdout
        assert timeout_seconds is not None and max_output_bytes > 0
        try:
            process = subprocess.Popen(
                [*command, *arguments], env=environment, stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            )
            assert process.stdout is not None
            deadline = time.monotonic() + timeout_seconds
            chunks: list[bytes] = []
            size = 0
            try:
                while True:
                    remaining = deadline - time.monotonic()
                    if remaining <= 0 or not select.select([process.stdout], [], [], remaining)[0]:
                        raise CandidateStateLimitError("Git index probe timed out")
                    chunk = os.read(process.stdout.fileno(), min(65536, max_output_bytes - size + 1))
                    if not chunk:
                        break
                    size += len(chunk)
                    if size > max_output_bytes:
                        raise CandidateStateLimitError("Git index listing exceeds bounded limit")
                    chunks.append(chunk)
                if process.wait(timeout=max(0.01, deadline - time.monotonic())) != 0:
                    raise CandidateStateError("git candidate-state probe failed")
                return b"".join(chunks)
            finally:
                if process.poll() is None:
                    process.kill()
                    process.wait()
                process.stdout.close()
        except subprocess.TimeoutExpired as exc:
            raise CandidateStateLimitError("Git index probe timed out") from exc
        except OSError as exc:
            raise CandidateStateError("Git index probe failed") from exc

    return read


def _git(repo: Path, *arguments: str) -> bytes:
    # Standalone reads retain their own effective-filter check.
    return _checked_git_reader(repo)(repo, *arguments)


def _read_git(
    repo: Path,
    arguments: tuple[str, ...],
    git_reader: Callable[..., bytes] | None,
) -> bytes:
    return _git(repo, *arguments) if git_reader is None else git_reader(repo, *arguments)


def _paths(
    repo: Path,
    *arguments: str,
    git_reader: Callable[..., bytes] | None = None,
) -> list[bytes]:
    return sorted(
        part
        for part in _read_git(repo, arguments, git_reader).split(b"\0")
        if part
    )


def validate_repository(
    repo: Path,
    base: str,
    *,
    git_reader: Callable[..., bytes] | None = None,
) -> tuple[Path, str]:
    if not repo.is_absolute() or Path(os.path.realpath(repo)) != repo:
        raise CandidateStateError("repository must be one canonical absolute path")
    try:
        metadata = repo.lstat()
    except OSError as exc:
        raise CandidateStateError("repository is unavailable") from exc
    if not stat.S_ISDIR(metadata.st_mode) or stat.S_ISLNK(metadata.st_mode):
        raise CandidateStateError("repository must be one real directory")
    if COMMIT_RE.fullmatch(base) is None:
        raise CandidateStateError("base must be one full immutable commit ID")
    root = _read_git(
        repo, ("rev-parse", "--show-toplevel"), git_reader
    ).rstrip(b"\n")
    try:
        decoded_root = Path(root.decode("utf-8", "strict"))
    except UnicodeDecodeError as exc:
        raise CandidateStateError("repository root is not canonical UTF-8") from exc
    if decoded_root != repo:
        raise CandidateStateError("repository must be the exact worktree root")
    resolved = _read_git(
        repo, ("rev-parse", "--verify", f"{base}^{{commit}}"), git_reader
    ).rstrip(b"\n")
    try:
        resolved_text = resolved.decode("ascii", "strict")
    except UnicodeDecodeError as exc:
        raise CandidateStateError("base resolution is invalid") from exc
    if resolved_text != base:
        raise CandidateStateError("base did not resolve exactly")
    return repo, base


def candidate_state_digest(
    repo: Path,
    base: str,
    *,
    validate: bool = True,
    git_reader: Callable[..., bytes] | None = None,
    commit_state: GitCommitState | None = None,
) -> str:
    owned_reader = git_reader is None
    if git_reader is None:
        git_reader = _checked_git_reader(repo)
    if validate:
        repo, base = validate_repository(repo, base, git_reader=git_reader)
    digest = hashlib.sha256()
    if commit_state is None:
        # Lifecycle's Git reader has a different call shape; its index probe
        # gets a fresh bounded reader, while our own reader is reused.
        commit_state = git_commit_state(repo, git_reader=git_reader if owned_reader else None)
    digest.update(json.dumps(commit_state, sort_keys=True, separators=(",", ":")).encode())
    tracked_diff = _read_git(
        repo,
        (
            "diff",
            "--binary",
            "--no-ext-diff",
            "--no-textconv",
            "--submodule=short",
            base,
            "--",
        ),
        git_reader,
    )
    digest.update(len(tracked_diff).to_bytes(8, "big"))
    digest.update(tracked_diff)
    paths = set(
        _paths(
            repo,
            "ls-files",
            "--others",
            "--exclude-standard",
            "-z",
            "--",
            git_reader=git_reader,
        )
    )
    paths.update(
        _paths(
            repo,
            "ls-files",
            "--others",
            "--ignored",
            "--exclude-standard",
            "-z",
            "--",
            git_reader=git_reader,
        )
    )
    for raw_path in sorted(paths):
        try:
            relative = raw_path.decode("utf-8", "surrogateescape")
        except UnicodeDecodeError as exc:  # pragma: no cover - surrogateescape is total
            raise CandidateStateError("candidate path is invalid") from exc
        full_path = os.path.join(repo, relative)
        digest.update(len(raw_path).to_bytes(8, "big"))
        digest.update(raw_path)
        try:
            metadata = os.lstat(full_path)
        except FileNotFoundError:
            digest.update(b"deleted")
            continue
        digest.update(str(stat.S_IFMT(metadata.st_mode)).encode("ascii"))
        digest.update(str(stat.S_IMODE(metadata.st_mode)).encode("ascii"))
        if stat.S_ISLNK(metadata.st_mode):
            digest.update(os.readlink(full_path).encode("utf-8", "surrogateescape"))
        elif stat.S_ISREG(metadata.st_mode):
            with open(full_path, "rb") as handle:
                for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                    digest.update(chunk)
        else:
            digest.update(b"non-regular")
    return digest.hexdigest()


def git_commit_state(
    repo: Path, *, git_reader: Callable[..., bytes] | None = None,
) -> GitCommitState:
    """Bound semantic index entries and current plain-commit target."""
    if git_reader is None:
        git_reader = _checked_git_reader(repo)
    staged = git_reader(repo, "ls-files", "--stage", "-z",
                        max_output_bytes=8 * 1024 * 1024, timeout_seconds=2.0)
    if staged and not staged.endswith(b"\0"):
        raise CandidateStateError("Git index listing is incomplete")
    flags = git_reader(repo, "ls-files", "-v", "-z",
                       max_output_bytes=8 * 1024 * 1024, timeout_seconds=2.0)
    if flags and not flags.endswith(b"\0"):
        raise CandidateStateError("Git index flags listing is incomplete")
    for record in flags.split(b"\0"):
        if record and not record.startswith(b"H "):
            # Lowercase tags hide working-tree checks (assume-unchanged); S
            # hides sparse paths (skip-worktree). Neither permits safe cleanup.
            raise CandidateStateError("unsupported Git index flags in candidate")
    entries: list[list[str]] = []
    for record in staged.split(b"\0"):
        if not record:
            continue
        try:
            header, path = record.split(b"\t", 1)
            relative = path.decode("utf-8", "surrogateescape")
        except (ValueError, UnicodeError) as exc:
            raise CandidateStateError("Git index listing is invalid") from exc
        entries.append([relative, header.decode("ascii", "strict")])
    branch = git_reader(repo, "rev-parse", "--symbolic-full-name", "HEAD").decode("utf-8", "strict").strip()
    head = git_reader(repo, "rev-parse", "--verify", "HEAD^{commit}").decode("ascii", "strict").strip()
    if not branch or COMMIT_RE.fullmatch(head) is None:
        raise CandidateStateError("Git commit target is invalid")
    return {"branch": branch, "head": head, "entries": entries}


def candidate_state_is_empty(repo: Path, base: str) -> bool:
    """Check that neither the index nor working tree adds a committable change."""
    try:
        return _candidate_state_is_empty(repo, base)
    except CandidateStateLimitError:
        return False


def _candidate_state_is_empty(repo: Path, base: str) -> bool:
    reader = _checked_git_reader(repo)
    validate_repository(repo, base, git_reader=reader)
    state = git_commit_state(repo, git_reader=reader)
    if state["head"] != base:
        return False
    tree = reader(repo, "ls-tree", "-r", "-z", base,
                  max_output_bytes=8 * 1024 * 1024, timeout_seconds=2.0)
    if tree and not tree.endswith(b"\0"):
        raise CandidateStateError("Git tree listing is incomplete")
    expected_entries: list[list[str]] = []
    for record in tree.split(b"\0"):
        if not record:
            continue
        try:
            header, path = record.split(b"\t", 1)
            mode, _kind, oid = header.decode("ascii", "strict").split(" ")
            expected_entries.append([path.decode("utf-8", "surrogateescape"),
                                     f"{mode} {oid} 0"])
        except (ValueError, UnicodeError) as exc:
            raise CandidateStateError("Git tree listing is invalid") from exc
    if sorted(state["entries"]) != sorted(expected_entries):
        return False
    # Override repository stat shortcuts. Git reports paths whose index stat
    # data differs; only those need direct byte hashing, including restored mtime.
    suspect_paths = set(reader(
        repo, "-c", "core.trustctime=true", "-c", "core.checkStat=default",
        "-c", "core.ignoreStat=false", "-c", "core.filemode=true",
        "-c", "core.symlinks=true", "diff-files", "--no-ext-diff",
        "--no-textconv", "--name-only", "-z", "--",
        max_output_bytes=8 * 1024 * 1024, timeout_seconds=2.0,
    ).split(b"\0"))
    suspect_entries = [entry for entry in expected_entries
                       if os.fsencode(entry[0]) in suspect_paths]
    if not _tracked_bytes_match_tree(repo, suspect_entries):
        return False
    clean_digest = hashlib.sha256()
    clean_digest.update(json.dumps(state, sort_keys=True, separators=(",", ":")).encode())
    clean_digest.update((0).to_bytes(8, "big"))
    return candidate_state_digest(repo, base, git_reader=reader,
                                  commit_state=state) == clean_digest.hexdigest()


def _tracked_bytes_match_tree(repo: Path, entries: list[list[str]]) -> bool:
    """Hash stat-suspect tracked paths without following symlink parents."""
    deadline = time.monotonic() + 3.0
    total_bytes = 0
    root_fd = os.open(repo, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for relative, header in entries:
            if time.monotonic() > deadline:
                return False
            mode, oid, stage = header.split(" ")
            if stage != "0" or len(oid) not in (40, 64):
                raise CandidateStateError("Git tree entry is unsupported")
            parts = os.fsencode(relative).split(b"/")
            if any(part in (b"", b".", b"..") for part in parts):
                raise CandidateStateError("Git tree path is invalid")
            parent_fd = os.dup(root_fd)
            try:
                for part in parts[:-1]:
                    child_fd = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                                       dir_fd=parent_fd)
                    os.close(parent_fd)
                    parent_fd = child_fd
                before = os.stat(parts[-1], dir_fd=parent_fd, follow_symlinks=False)
                if mode == "120000" and stat.S_ISLNK(before.st_mode):
                    payload = os.readlink(parts[-1], dir_fd=parent_fd)
                    payload_bytes = os.fsencode(payload)
                    after = os.stat(parts[-1], dir_fd=parent_fd, follow_symlinks=False)
                elif mode in ("100644", "100755") and stat.S_ISREG(before.st_mode):
                    if bool(before.st_mode & 0o111) != (mode == "100755"):
                        return False
                    handle = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW |
                                     os.O_NONBLOCK | os.O_CLOEXEC,
                                     dir_fd=parent_fd)
                    try:
                        opened = os.fstat(handle)
                        if not stat.S_ISREG(opened.st_mode) or (
                                opened.st_dev, opened.st_ino, opened.st_mode,
                                opened.st_size, opened.st_mtime_ns, opened.st_ctime_ns) != (
                                before.st_dev, before.st_ino, before.st_mode,
                                before.st_size, before.st_mtime_ns, before.st_ctime_ns):
                            return False
                        if total_bytes + opened.st_size > 64 * 1024 * 1024:
                            return False
                        chunks: list[bytes] = []
                        while chunk := os.read(handle, 1024 * 1024):
                            total_bytes += len(chunk)
                            if total_bytes > 64 * 1024 * 1024 or time.monotonic() > deadline:
                                return False
                            chunks.append(chunk)
                        payload_bytes = b"".join(chunks)
                        read_back = os.fstat(handle)
                        if (read_back.st_dev, read_back.st_ino, read_back.st_mode,
                                read_back.st_size, read_back.st_mtime_ns,
                                read_back.st_ctime_ns) != (
                                before.st_dev, before.st_ino, before.st_mode,
                                before.st_size, before.st_mtime_ns, before.st_ctime_ns):
                            return False
                    finally:
                        os.close(handle)
                    after = os.stat(parts[-1], dir_fd=parent_fd, follow_symlinks=False)
                else:
                    return False
                if (before.st_dev, before.st_ino, before.st_mode, before.st_size,
                        before.st_mtime_ns, before.st_ctime_ns) != (
                        after.st_dev, after.st_ino, after.st_mode, after.st_size,
                        after.st_mtime_ns, after.st_ctime_ns):
                    return False
                digest = hashlib.sha1() if len(oid) == 40 else hashlib.sha256()
                digest.update(f"blob {len(payload_bytes)}\0".encode("ascii"))
                digest.update(payload_bytes)
                if digest.hexdigest() != oid:
                    return False
            except (FileNotFoundError, NotADirectoryError, OSError):
                return False
            finally:
                os.close(parent_fd)
    finally:
        os.close(root_fd)
    return True


def _diagnostic_facts(repo: Path) -> dict[str, object]:
    """Collect bounded no-follow clues; incomplete scans give generic diagnostics."""
    items: list[list[object]] = []
    path_bytes = 0
    content_bytes = 0
    # The wall-clock cap protects diagnostics on slow filesystems; allow normal
    # scheduler delays so a small safe tree still gets useful path detail.
    deadline = time.monotonic() + 0.5
    try:
        root_fd = os.open(repo, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    except OSError:
        return {"complete": False, "items": []}

    def binding(info: os.stat_result) -> tuple[int, ...]:
        # Reads may advance atime; it is not evidence of a path replacement.
        return (info.st_dev, info.st_ino, info.st_mode, info.st_nlink,
                info.st_uid, info.st_gid, info.st_size, info.st_mtime_ns,
                info.st_ctime_ns)

    def scan(directory_fd: int, prefix: bytes) -> bool:
        nonlocal path_bytes, content_bytes
        with os.scandir(directory_fd) as entries:
            for entry in entries:
                name = os.fsencode(entry.name)
                if not prefix and name == b".git":
                    continue
                path = prefix + name
                if (time.monotonic() > deadline or len(items) >= 64
                        or path_bytes + len(path) > 8192):
                    return False
                path_bytes += len(path)
                metadata = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
                mode = stat.S_IMODE(metadata.st_mode)
                fingerprint = hashlib.sha256(str(mode).encode("ascii") + b"\0")
                if stat.S_ISDIR(metadata.st_mode):
                    kind = "dir"
                elif stat.S_ISLNK(metadata.st_mode):
                    kind = "symlink"
                    fingerprint.update(os.readlink(name, dir_fd=directory_fd))
                elif stat.S_ISREG(metadata.st_mode):
                    kind = "file"
                    descriptor = os.open(name, os.O_RDONLY | os.O_NOFOLLOW,
                                         dir_fd=directory_fd)
                    try:
                        if binding(os.fstat(descriptor)) != binding(metadata):
                            return False
                        while chunk := os.read(descriptor, 1024 * 1024):
                            content_bytes += len(chunk)
                            if content_bytes > 8 * 1024 * 1024 or time.monotonic() > deadline:
                                return False
                            fingerprint.update(chunk)
                        if (binding(os.fstat(descriptor)) != binding(metadata)
                                or binding(os.stat(name, dir_fd=directory_fd,
                                                    follow_symlinks=False)) != binding(metadata)):
                            return False
                    finally:
                        os.close(descriptor)
                else:
                    kind = "special"
                fingerprint.update(kind.encode("ascii"))
                items.append([os.fsdecode(path), kind, mode, fingerprint.hexdigest()])
                if kind == "dir":
                    child_fd = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                                       dir_fd=directory_fd)
                    try:
                        if (binding(os.fstat(child_fd)) != binding(metadata)
                                or not scan(child_fd, path + b"/")):
                            return False
                    finally:
                        os.close(child_fd)
                    if (binding(os.stat(name, dir_fd=directory_fd, follow_symlinks=False))
                            != binding(metadata)):
                        return False
        return True

    try:
        original = os.fstat(root_fd)
        complete = scan(root_fd, b"") and binding(os.fstat(root_fd)) == binding(original)
    except (OSError, UnicodeError, RecursionError):
        complete = False
    finally:
        os.close(root_fd)
    if not complete:
        return {"complete": False, "items": []}
    items.sort(key=lambda item: str(item[0]))
    return {"complete": True, "items": items}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="candidate_state.py", add_help=False)
    parser.add_argument("--repo", action="append")
    parser.add_argument("--base", action="append")
    parser.add_argument("--git", nargs=argparse.REMAINDER)
    parser.add_argument("--verify-base", action="store_true")
    parser.add_argument("--digest-facts", action="store_true")
    parser.add_argument("--digest-git-state", action="store_true")
    parser.add_argument("--facts", action="store_true")
    parser.add_argument("--compare-git-states", action="store_true")
    parser.add_argument("--diagnostic-facts", action="store_true")
    parser.add_argument("--compare-diagnostics", nargs=2)
    parsed = parser.parse_args(argv)
    if parsed.compare_git_states:
        if parsed.repo or parsed.base or parsed.git is not None:
            return 64
        try:
            before = json.loads(sys.stdin.readline())
            after = json.loads(sys.stdin.readline())
            if not isinstance(before, dict) or not isinstance(after, dict):
                return 64
            if before.get("branch") != after.get("branch") or before.get("head") != after.get("head"):
                print("verifier changed Git HEAD or the current branch; inspect the branch and restore the reviewed target")
            elif before.get("entries") != after.get("entries"):
                old = before["entries"]
                new = after["entries"]
                if not isinstance(old, list) or not isinstance(new, list):
                    return 64
                old_entries = {tuple(item) for item in old}
                new_entries = {tuple(item) for item in new}
                changed = next((item[0] for item in sorted(old_entries ^ new_entries)), None)
                if changed is None:
                    return 64
                print(f"verifier changed the Git index for {json.dumps(changed, ensure_ascii=True)}; inspect staged bytes and restore the reviewed index")
            else:
                return 64
        except (KeyError, TypeError, ValueError):
            return 64
        return 0
    if parsed.compare_diagnostics is not None:
        if (parsed.repo or parsed.base or parsed.git is not None or parsed.diagnostic_facts
                or parsed.verify_base or parsed.digest_facts or parsed.facts):
            return 64
        if any(len(raw) > 65536 for raw in parsed.compare_diagnostics):
            return 64
        try:
            sys.path.insert(0, str(Path(__file__).resolve().parent))
            import agy_dispatch_worktree as worktree

            before, after = (json.loads(raw) for raw in parsed.compare_diagnostics)
            if not isinstance(before, dict) or not isinstance(after, dict):
                return 64
            print(worktree._snapshot_drift_details(before, after))
        except (ImportError, KeyError, TypeError, ValueError, IndexError):
            return 64
        return 0
    if parsed.diagnostic_facts:
        if (not parsed.repo or len(parsed.repo) != 1 or parsed.base or parsed.git is not None
                or parsed.verify_base or parsed.digest_facts or parsed.facts):
            return 64
        try:
            sys.path.insert(0, str(Path(__file__).resolve().parent))
            import agy_dispatch_worktree as worktree

            # Diagnostics must not select an executable from the caller's PATH.
            os.environ["PATH"] = os.path.dirname(GIT_EXECUTABLE)
            snapshot = worktree._worktree_snapshot(parsed.repo[0])
            if snapshot is None:
                return 1
            print(json.dumps(snapshot["path_facts"], ensure_ascii=True, separators=(",", ":")))
        except (ImportError, ValueError):
            return 1
        return 0
    if parsed.verify_base:
        if (not parsed.repo or len(parsed.repo) != 1 or not parsed.base
                or len(parsed.base) != 1 or parsed.git is not None
                or parsed.digest_facts or parsed.facts):
            return 64
        try:
            repo = Path(parsed.repo[0])
            reader = _checked_git_reader(repo)
            if reader(repo, "rev-parse", "--is-inside-work-tree") != b"true\n":
                raise CandidateStateError("cannot establish trusted Git worktree")
            resolved = reader(repo, "rev-parse", "--verify", f"{parsed.base[0]}^{{commit}}")
            if resolved != (parsed.base[0] + "\n").encode("ascii"):
                raise CandidateStateError("base did not resolve to the exact supplied commit")
        except CandidateStateError as exc:
            print(f"candidate-state: {exc}", file=sys.stderr)
            return 1
        print(parsed.base[0])
        return 0
    if parsed.git is not None:
        if (not parsed.repo or len(parsed.repo) != 1 or not parsed.git or parsed.base
                or parsed.digest_facts or parsed.facts):
            return 64
        try:
            sys.stdout.buffer.write(_git(Path(parsed.repo[0]), *parsed.git))
        except CandidateStateError as exc:
            print(f"candidate-state: {exc}", file=sys.stderr)
            return 1
        return 0
    if parsed.facts:
        if not parsed.repo or len(parsed.repo) != 1 or parsed.base or parsed.digest_facts:
            return 64
        repo = Path(parsed.repo[0])
        print(json.dumps(_diagnostic_facts(repo),
                         ensure_ascii=True, separators=(",", ":")))
        return 0
    if not parsed.repo or len(parsed.repo) != 1 or not parsed.base or len(parsed.base) != 1:
        return 64
    try:
        repo = Path(parsed.repo[0])
        digest_reader = _checked_git_reader(repo) if (parsed.digest_facts or parsed.digest_git_state) else None
        commit_state = git_commit_state(repo, git_reader=digest_reader) if digest_reader else None
        digest = candidate_state_digest(repo, parsed.base[0], git_reader=digest_reader,
                                        commit_state=commit_state)
        print(digest)
        if parsed.digest_facts:
            assert digest_reader is not None
            print(json.dumps(_diagnostic_facts(repo), ensure_ascii=True,
                             separators=(",", ":")))
        if parsed.digest_facts or parsed.digest_git_state:
            print(json.dumps(commit_state, ensure_ascii=True, sort_keys=True,
                             separators=(",", ":")))
    except CandidateStateError as exc:
        print(f"candidate-state: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
