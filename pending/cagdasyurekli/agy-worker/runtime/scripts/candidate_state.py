#!/usr/bin/env python3
"""Canonical Git-visible candidate-state digest shared by gate and lifecycle."""

from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
from typing import Callable

sys.dont_write_bytecode = True

COMMIT_RE = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})")


class CandidateStateError(ValueError):
    pass


GitReader = Callable[[Path, str], bytes]


def _git(repo: Path, *arguments: str) -> bytes:
    try:
        completed = subprocess.run(
            ["git", "-C", str(repo), *arguments],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    except OSError as exc:
        raise CandidateStateError("git candidate-state probe failed") from exc
    if completed.returncode != 0:
        raise CandidateStateError("git candidate-state probe failed")
    return completed.stdout


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
) -> str:
    if validate:
        repo, base = validate_repository(repo, base, git_reader=git_reader)
    digest = hashlib.sha256()
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="candidate_state.py", add_help=False)
    parser.add_argument("--repo", action="append")
    parser.add_argument("--base", action="append")
    parsed = parser.parse_args(argv)
    if not parsed.repo or len(parsed.repo) != 1 or not parsed.base or len(parsed.base) != 1:
        return 64
    try:
        print(candidate_state_digest(Path(parsed.repo[0]), parsed.base[0]))
    except CandidateStateError:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
