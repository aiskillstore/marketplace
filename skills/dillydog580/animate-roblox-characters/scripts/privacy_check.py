#!/usr/bin/env python3
"""Scan repository files, binary strings, and Git metadata for private data."""

from __future__ import annotations

import argparse
import getpass
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


ALLOWED_GIT_NAMES = {"Roblox Animation Skill Contributors"}
ALLOWED_EMAILS = {"contributors@users.noreply.github.com"}
SKIP_DIRECTORIES = {".git", ".codex", "output", "outputs", "__pycache__", ".pytest_cache", ".mypy_cache"}
SKIP_SUFFIXES = {".pyc", ".pyo", ".blend1", ".blend2"}
MAX_FILE_SIZE = 64 * 1024 * 1024
MAX_HISTORY_BLOBS = 100_000


@dataclass(frozen=True)
class Finding:
    path: str
    rule: str


def _patterns() -> list[tuple[str, re.Pattern[str]]]:
    # Build path tokens in pieces so this scanner does not match its own source.
    mac_home = "/" + "Users" + r"/[^/\s\x00]{1,80}/"
    linux_home = "/" + "home" + r"/[^/\s\x00]{1,80}/"
    windows_home = r"[A-Za-z]:\\" + "Users" + r"\\[^\\\s\x00]{1,80}\\"
    return [
        ("macOS home-directory path", re.compile(mac_home)),
        ("Linux home-directory path", re.compile(linux_home)),
        ("Windows home-directory path", re.compile(windows_home, re.IGNORECASE)),
        ("file URI", re.compile(r"file://(?:/|[A-Za-z]:)")),
        ("email address", re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)),
        ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b")),
        ("OpenAI-style secret", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
        ("AWS access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
        (
            "private key material",
            re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
        ),
    ]


def _ascii_strings(data: bytes) -> str:
    return "\n".join(match.decode("ascii", errors="ignore") for match in re.findall(rb"[\x20-\x7e]{6,}", data))


def _iter_files(root: Path, tracked_paths: set[str]) -> Iterable[Path]:
    for path in sorted(root.rglob("*")):
        if not path.is_file() and not path.is_symlink():
            continue
        relative_parts = path.relative_to(root).parts
        if any(part in SKIP_DIRECTORIES for part in relative_parts):
            continue
        # Ignore ordinary fetched rig binaries, but never let this convenience
        # hide a forced-tracked publication artifact or any symlink.
        relative = path.relative_to(root).as_posix()
        if (
            ("assets", "external") in tuple(zip(relative_parts, relative_parts[1:]))
            and relative not in tracked_paths
            and not path.is_symlink()
        ):
            continue
        if path.is_symlink():
            yield path
            continue
        if path.suffix.lower() in SKIP_SUFFIXES:
            continue
        if path.stat().st_size > MAX_FILE_SIZE:
            yield path
            continue
        yield path


def _scan_text(
    text: str,
    display_path: str,
    *,
    ignored_rules: frozenset[str] = frozenset(),
) -> list[Finding]:
    findings = []
    for rule, pattern in _patterns():
        if rule in ignored_rules:
            continue
        for match in pattern.finditer(text):
            if rule == "email address" and match.group(0).lower() in ALLOWED_EMAILS:
                continue
            findings.append(Finding(display_path, rule))
            break

    local_user = getpass.getuser().strip()
    if "current local username" not in ignored_rules and local_user and len(local_user) >= 3:
        contextual = re.compile(
            rf"(?:[/\\]|user(?:name)?\s*[:=]\s*){re.escape(local_user)}(?:[/\\\s\"']|$)",
            re.IGNORECASE,
        )
        if contextual.search(text):
            findings.append(Finding(display_path, "current local username"))
    return findings


def scan_file(path: Path, root: Path) -> list[Finding]:
    display_path = path.relative_to(root).as_posix()
    if path.is_symlink():
        try:
            target = path.resolve(strict=True)
        except OSError:
            return [Finding(display_path, "broken symlink")]
        if target != root and root not in target.parents:
            return [Finding(display_path, "symlink escapes repository")]
        if not target.is_file():
            return [Finding(display_path, "symlink target is not a regular file")]
    if path.stat().st_size > MAX_FILE_SIZE:
        return [Finding(display_path, "file exceeds privacy scanner size limit")]
    data = path.read_bytes()
    if b"\x00" in data or path.suffix.lower() == ".blend":
        text = _ascii_strings(data)
    else:
        text = data.decode("utf-8", errors="replace")
    return _scan_text(text, display_path)


def _git_output(root: Path, args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def scan_git_metadata(root: Path, enforce_identity: bool = True) -> list[Finding]:
    findings = []
    if not (root / ".git").exists():
        return findings

    config = _git_output(root, ["config", "--local", "--list"])
    identity_config = []
    other_config = []
    for line in config.splitlines():
        target = identity_config if line.split("=", 1)[0].lower() in {"user.name", "user.email"} else other_config
        target.append(line)
    findings.extend(_scan_text("\n".join(other_config), ".git/config"))
    findings.extend(
        _scan_text(
            "\n".join(identity_config),
            ".git/config",
            ignored_rules=frozenset({"email address", "current local username"}),
        )
    )

    configured_name = _git_output(root, ["config", "--local", "--get", "user.name"])
    configured_email = _git_output(root, ["config", "--local", "--get", "user.email"])
    if enforce_identity:
        if configured_name and configured_name not in ALLOWED_GIT_NAMES:
            findings.append(Finding(".git/config", "non-pseudonymous local Git author name"))
        if configured_email and configured_email.lower() not in ALLOWED_EMAILS:
            findings.append(Finding(".git/config", "non-pseudonymous local Git author email"))

    history = _git_output(root, ["log", "--format=%an%x00%ae%x00%cn%x00%ce"])
    findings.extend(
        _scan_text(
            history,
            ".git/history",
            ignored_rules=frozenset({"email address", "current local username"}),
        )
    )
    if enforce_identity:
        for line in history.splitlines():
            values = line.split("\x00")
            if len(values) != 4:
                continue
            author_name, author_email, committer_name, committer_email = values
            if author_name not in ALLOWED_GIT_NAMES or committer_name not in ALLOWED_GIT_NAMES:
                findings.append(Finding(".git/history", "non-pseudonymous commit author name"))
                break
            if author_email.lower() not in ALLOWED_EMAILS or committer_email.lower() not in ALLOWED_EMAILS:
                findings.append(Finding(".git/history", "non-pseudonymous commit author email"))
                break
    messages = _git_output(root, ["log", "--format=%B%x00"])
    findings.extend(_scan_text(messages, ".git/history-messages"))
    return findings


def scan_git_history_blobs(root: Path) -> list[Finding]:
    """Scan every blob reachable from the publication branch's HEAD."""
    if not (root / ".git").exists():
        return []
    objects = subprocess.run(
        ["git", "rev-list", "--objects", "HEAD"],
        cwd=root,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    if objects.returncode != 0:
        return [Finding(".git/history-blobs", "could not enumerate reachable Git objects")]
    paths_by_oid: dict[str, str] = {}
    for line in objects.stdout.splitlines():
        oid, separator, path = line.partition(" ")
        if oid:
            paths_by_oid.setdefault(oid, path if separator else "<unnamed>")
    if len(paths_by_oid) > MAX_HISTORY_BLOBS:
        return [Finding(".git/history-blobs", "reachable Git object count exceeds scan limit")]
    if not paths_by_oid:
        return []

    batch = subprocess.run(
        ["git", "cat-file", "--batch-check=%(objectname) %(objecttype) %(objectsize)"],
        cwd=root,
        input="\n".join(paths_by_oid) + "\n",
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    if batch.returncode != 0:
        return [Finding(".git/history-blobs", "could not classify reachable Git objects")]

    findings: list[Finding] = []
    for line in batch.stdout.splitlines():
        fields = line.split()
        if len(fields) != 3:
            findings.append(Finding(".git/history-blobs", "could not classify a reachable Git object"))
            continue
        if fields[1] != "blob":
            continue
        oid, _kind, size_text = fields
        try:
            size = int(size_text)
        except ValueError:
            findings.append(Finding(".git/history-blobs", "invalid reachable blob size"))
            continue
        path = paths_by_oid.get(oid, "<unnamed>")
        label = f".git/history-blobs/{path}@{oid[:12]}"
        findings.extend(_scan_text(path, ".git/history-paths"))
        if size > MAX_FILE_SIZE:
            findings.append(Finding(label, "historical blob exceeds privacy scanner size limit"))
            continue
        blob = subprocess.run(
            ["git", "cat-file", "blob", oid],
            cwd=root,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
        if blob.returncode != 0 or len(blob.stdout) != size:
            findings.append(Finding(label, "could not read complete historical blob"))
            continue
        text = _ascii_strings(blob.stdout) if b"\x00" in blob.stdout else blob.stdout.decode("utf-8", errors="replace")
        findings.extend(_scan_text(text, label))
    return findings


def scan_repository(root: str | Path, enforce_git_identity: bool = True) -> list[Finding]:
    root_path = Path(root).expanduser().resolve()
    if not root_path.is_dir():
        raise ValueError("Repository root must be an existing directory")
    tracked_output = _git_output(root_path, ["ls-files", "-z"])
    tracked_paths = {item for item in tracked_output.split("\0") if item}
    findings = []
    for path in _iter_files(root_path, tracked_paths):
        findings.extend(scan_file(path, root_path))
    findings.extend(scan_git_metadata(root_path, enforce_identity=enforce_git_identity))
    findings.extend(scan_git_history_blobs(root_path))
    return sorted(set(findings), key=lambda finding: (finding.path, finding.rule))


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=Path(__file__).resolve().parents[2])
    parser.add_argument("--json", action="store_true", dest="json_output")
    parser.add_argument(
        "--allow-contributor-identities",
        action="store_true",
        help="Scan content, secrets, paths, remotes, and history messages without enforcing one Git author identity",
    )
    return parser.parse_args(argv)


def main() -> int:
    args = _parse_args(sys.argv[1:])
    try:
        findings = scan_repository(args.root, enforce_git_identity=not args.allow_contributor_identities)
    except (OSError, ValueError) as exc:
        print(f"Privacy check could not run: {exc}", file=sys.stderr)
        return 2
    if args.json_output:
        print(json.dumps({"ok": not findings, "findings": [asdict(item) for item in findings]}, indent=2))
    elif findings:
        print("Privacy check failed:")
        for finding in findings:
            print(f"- {finding.path}: {finding.rule}")
    else:
        print("Privacy check passed: no private paths, personal emails, local identity, or common secrets detected.")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
