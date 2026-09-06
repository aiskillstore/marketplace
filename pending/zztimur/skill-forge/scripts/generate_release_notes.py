#!/usr/bin/env python3
"""Generate release notes for a skill-forge tag from git history.

Outlines the changes between the previous tag and the target tag as grouped
markdown, suitable for a GitHub Release body. Dependency-free: standard library
only, no network access. Run it locally before tagging to preview the notes, or
let the release workflow run it and attach the output to the GitHub Release.

Usage:
    python3 scripts/generate_release_notes.py [--tag REF] [--previous REF]
                                              [--repo owner/name] [--output PATH]

Behavior:
    --tag       Target ref for the release. Defaults to the most recent tag,
                or HEAD when the repository has no tags.
    --previous  Ref that the target is compared against. Defaults to the tag
                immediately preceding --tag; when none exists, the entire
                history reachable from --tag is summarized.
    --repo      "owner/name" used to build a full-changelog compare link.
                Defaults to $GITHUB_REPOSITORY, then to the origin remote URL.
    --output    Write the notes to this path instead of stdout.

Commits are grouped by their conventional-commit type prefix
(feat, fix, docs, perf, test, ci, build, chore, refactor); anything else lands
under "Other Changes". Merge commits are skipped.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from release_metadata import (
    ChangelogMetadataError,
    SEMVER_TAG_RE,
    parse_release_entry,
)

# Record and field separators unlikely to appear in commit text.
RECORD_SEP = "\x1e"
FIELD_SEP = "\x1f"
SHORT_HASH_WIDTH = 12

# Ordered so the rendered notes read fixes-first, chores-last.
SECTIONS: List[Tuple[str, str, Tuple[str, ...]]] = [
    ("feat", "Features", ("feat", "feature")),
    ("fix", "Fixes", ("fix", "bugfix", "hotfix")),
    ("perf", "Performance", ("perf",)),
    ("refactor", "Refactoring", ("refactor",)),
    ("docs", "Documentation", ("docs", "doc")),
    ("test", "Tests", ("test", "tests")),
    ("ci", "Maintenance", ("ci", "build", "chore")),
]
OTHER_KEY = "other"
OTHER_TITLE = "Other Changes"

# Matches a leading "type" or "type(scope):" conventional-commit prefix.
PREFIX_RE = re.compile(r"^(?P<type>[a-z]+)(?:\([^)]*\))?!?:\s*(?P<rest>.*)$", re.IGNORECASE)
REPO_ROOT = Path(__file__).resolve().parents[1]
CHANGELOG_PATH = REPO_ROOT / "CHANGELOG.md"
GIT_TIMEOUT_SECONDS = 30
UNSAFE_GIT_ENVIRONMENT = {
    "GIT_ALTERNATE_OBJECT_DIRECTORIES",
    "GIT_CEILING_DIRECTORIES",
    "GIT_COMMON_DIR",
    "GIT_CONFIG",
    "GIT_DIR",
    "GIT_DISCOVERY_ACROSS_FILESYSTEM",
    "GIT_EXEC_PATH",
    "GIT_INDEX_FILE",
    "GIT_NAMESPACE",
    "GIT_OBJECT_DIRECTORY",
    "GIT_PREFIX",
    "GIT_QUARANTINE_PATH",
    "GIT_SHALLOW_FILE",
    "GIT_SUPER_PREFIX",
    "GIT_WORK_TREE",
}


class ReleaseNotesError(RuntimeError):
    """A release-note generation error with a stable machine-readable code."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def emit_error(code: str, message: str) -> None:
    """Emit a structured error without mixing it into the release-note body."""
    print(
        json.dumps({"status": "error", "error": {"code": code, "message": message}}, sort_keys=True),
        file=sys.stderr,
    )


def _git_environment() -> Dict[str, str]:
    environment = os.environ.copy()
    for key in list(environment):
        if key in UNSAFE_GIT_ENVIRONMENT or key.startswith("GIT_CONFIG_"):
            environment.pop(key, None)
    environment["GIT_NO_REPLACE_OBJECTS"] = "1"
    environment["GIT_OPTIONAL_LOCKS"] = "0"
    return environment


def run_git(args: List[str], *, strip: bool = True) -> str:
    """Run a git command and return stripped stdout, or raise with context."""
    try:
        result = subprocess.run(
            ["git", "--no-replace-objects", *args],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
            timeout=GIT_TIMEOUT_SECONDS,
            env=_git_environment(),
        )
    except FileNotFoundError:
        raise ReleaseNotesError("git_unavailable", "git is not available on PATH")
    except subprocess.TimeoutExpired as exc:
        raise ReleaseNotesError(
            "git_timeout",
            f"git command timed out after {exc.timeout} seconds",
        ) from exc
    except OSError as exc:
        raise ReleaseNotesError("git_unavailable", f"could not launch git: {exc}") from exc
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or "").strip() or "git command failed"
        raise ReleaseNotesError("git_command_failed", detail)
    return result.stdout.strip() if strip else result.stdout


def try_git(args: List[str]) -> Optional[str]:
    """Run a git command, returning None instead of raising on failure."""
    try:
        return run_git(args)
    except ReleaseNotesError:
        return None


def _semver_value(tag: str) -> Optional[Tuple[int, int, int]]:
    if not SEMVER_TAG_RE.fullmatch(tag):
        return None
    return tuple(int(part) for part in tag[1:].split("."))  # type: ignore[return-value]


def _validate_ref(ref: str) -> None:
    if not isinstance(ref, str) or not ref or ref.startswith("-"):
        raise ReleaseNotesError(
            "git_ref_invalid", "git refs must be non-empty and must not start with '-'"
        )
    if any(character in ref for character in ("\x00", "\n", "\r")):
        raise ReleaseNotesError(
            "git_ref_invalid", "git refs must not contain control characters"
        )


def _git_ref(ref: str) -> str:
    _validate_ref(ref)
    return f"refs/tags/{ref}" if _semver_value(ref) is not None else ref


def _reachable_versions(ref: str) -> List[Tuple[str, Tuple[int, int, int]]]:
    versions: List[Tuple[str, Tuple[int, int, int]]] = []
    for tag in run_git(["tag", "--merged", _git_ref(ref)]).splitlines():
        version = _semver_value(tag)
        if version is not None:
            versions.append((tag, version))
    return versions


def resolve_target(tag: Optional[str]) -> str:
    if tag:
        return tag
    candidates = _reachable_versions("HEAD")
    return max(candidates, key=lambda item: item[1])[0] if candidates else "HEAD"


def resolve_previous(target: str, previous: Optional[str]) -> Optional[str]:
    if previous:
        return previous
    candidates = [item for item in _reachable_versions(target) if item[0] != target]
    target_version = _semver_value(target)
    if target_version is not None:
        candidates = [item for item in candidates if item[1] < target_version]
    return max(candidates, key=lambda item: item[1])[0] if candidates else None


def resolve_repo(repo: Optional[str]) -> Optional[str]:
    if repo:
        return repo
    env_repo = os.environ.get("GITHUB_REPOSITORY")
    if env_repo:
        return env_repo
    url = try_git(["remote", "get-url", "origin"])
    if not url:
        return None
    match = re.search(r"github\.com[:/](?P<slug>[^/]+/[^/]+?)(?:\.git)?/?$", url)
    return match.group("slug") if match else None


def collect_commits(target: str, previous: Optional[str]) -> List[Tuple[str, str]]:
    """Return (short_sha, subject) pairs in the range, newest first."""
    target_ref = _git_ref(target)
    previous_ref = _git_ref(previous) if previous else None
    revs = f"{previous_ref}..{target_ref}" if previous_ref else target_ref
    pretty = f"--pretty=format:%H{FIELD_SEP}%s{RECORD_SEP}"
    raw = run_git(["log", revs, "--no-merges", pretty])
    commits: List[Tuple[str, str]] = []
    for record in raw.split(RECORD_SEP):
        if not record:
            continue
        full_sha, _, subject = record.partition(FIELD_SEP)
        subject = subject.strip()
        if subject:
            full_sha = full_sha.strip()
            if not re.fullmatch(r"[0-9a-f]{40,}", full_sha):
                raise ReleaseNotesError("git_hash_invalid", f"git returned an invalid commit hash: {full_sha!r}")
            commits.append((full_sha[:SHORT_HASH_WIDTH], subject))
    return commits


def categorize(subject: str) -> Tuple[str, str]:
    """Return (section_key, cleaned_subject) for a commit subject."""
    match = PREFIX_RE.match(subject)
    if match:
        commit_type = match.group("type").lower()
        rest = match.group("rest").strip() or subject
        for key, _title, aliases in SECTIONS:
            if commit_type in aliases:
                return key, rest
    return OTHER_KEY, subject


def group_commits(commits: List[Tuple[str, str]]) -> Dict[str, List[str]]:
    grouped: Dict[str, List[str]] = {}
    for short_sha, subject in commits:
        key, cleaned = categorize(subject)
        grouped.setdefault(key, []).append(f"- {cleaned} ({short_sha})")
    return grouped


def changelog_entry(text: str, tag: str) -> Optional[Tuple[str, str]]:
    """Return a dated committed changelog entry for one exact tag, if present."""
    try:
        entry = parse_release_entry(text, tag, required=False)
    except ChangelogMetadataError as exc:
        raise ReleaseNotesError(exc.code, str(exc)) from exc
    return (entry.date, entry.body) if entry is not None else None


def load_changelog_entry(tag: str) -> Optional[Tuple[str, str]]:
    if _semver_value(tag) is None:
        return None
    exact_ref = _git_ref(tag)
    try:
        commit = run_git(["rev-parse", f"{exact_ref}^{{commit}}"])
        text = run_git(["show", f"{commit}:{CHANGELOG_PATH.name}"], strip=False)
    except ReleaseNotesError as exc:
        raise ReleaseNotesError(
            "changelog_blob_unavailable",
            f"could not read committed CHANGELOG.md for {tag}: {exc}",
        ) from exc
    entry = changelog_entry(text, tag)
    if entry is None:
        raise ReleaseNotesError(
            "changelog_entry_missing",
            f"committed CHANGELOG.md has no entry for semantic release {tag}",
        )
    return entry


def render_committed_changelog(
    target: str,
    previous: Optional[str],
    repo: Optional[str],
    entry: Tuple[str, str],
) -> str:
    """Render the matching committed entry as the GitHub Release body."""
    date, body = entry
    lines = [f"# skill-forge {target}", "", f"_Released {date}_", "", body, ""]
    if previous:
        if repo:
            lines.append(f"**Full changelog:** https://github.com/{repo}/compare/{previous}...{target}")
        else:
            lines.append(f"**Full changelog:** {previous}...{target}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def release_date(target: str) -> dt.date:
    """Return a reproducible date from SOURCE_DATE_EPOCH or the target commit."""
    source_date_epoch = os.environ.get("SOURCE_DATE_EPOCH")
    if source_date_epoch is not None:
        try:
            epoch = int(source_date_epoch)
        except ValueError as exc:
            raise ReleaseNotesError(
                "source_date_epoch_invalid",
                "SOURCE_DATE_EPOCH must be an integer number of UTC seconds",
            ) from exc
        try:
            return dt.datetime.fromtimestamp(epoch, tz=dt.timezone.utc).date()
        except (OverflowError, OSError, ValueError) as exc:
            raise ReleaseNotesError(
                "source_date_epoch_invalid",
                "SOURCE_DATE_EPOCH is outside the supported UTC date range",
            ) from exc

    timestamp = run_git(["show", "-s", "--format=%cI", _git_ref(target)])
    try:
        return dt.datetime.fromisoformat(timestamp.replace("Z", "+00:00")).date()
    except ValueError as exc:
        raise ReleaseNotesError(
            "git_timestamp_invalid",
            f"could not parse committed timestamp for {target}: {timestamp!r}",
        ) from exc


def render(
    target: str,
    previous: Optional[str],
    repo: Optional[str],
    commits: List[Tuple[str, str]],
    today: dt.date,
) -> str:
    heading_ref = target if target != "HEAD" else "unreleased"
    lines: List[str] = [f"# skill-forge {heading_ref}", "", f"_Released {today.isoformat()}_", ""]

    if not commits:
        lines.append("No changes recorded for this range.")
        return "\n".join(lines) + "\n"

    grouped = group_commits(commits)
    for key, title, _aliases in SECTIONS:
        entries = grouped.get(key)
        if entries:
            lines.append(f"## {title}")
            lines.extend(entries)
            lines.append("")
    if grouped.get(OTHER_KEY):
        lines.append(f"## {OTHER_TITLE}")
        lines.extend(grouped[OTHER_KEY])
        lines.append("")

    if previous:
        if repo:
            lines.append(
                f"**Full changelog:** https://github.com/{repo}/compare/{previous}...{target}"
            )
        else:
            lines.append(f"**Full changelog:** {previous}...{target}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate skill-forge release notes.")
    parser.add_argument("--tag", help="Target ref (default: latest tag or HEAD).")
    parser.add_argument("--previous", help="Compare against this ref (default: preceding tag).")
    parser.add_argument("--repo", help='"owner/name" for the compare link (default: origin).')
    parser.add_argument("--output", help="Write notes to this path instead of stdout.")
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    try:
        target = resolve_target(args.tag)
        previous = resolve_previous(target, args.previous)
        repo = resolve_repo(args.repo)
        entry = load_changelog_entry(target)
        commits = [] if entry else collect_commits(target, previous)
    except ReleaseNotesError as exc:
        emit_error(exc.code, str(exc))
        return 1

    try:
        notes = (
            render_committed_changelog(target, previous, repo, entry)
            if entry
            else render(target, previous, repo, commits, release_date(target))
        )
    except ReleaseNotesError as exc:
        emit_error(exc.code, str(exc))
        return 1

    if args.output:
        try:
            Path(args.output).write_text(notes, encoding="utf-8")
        except OSError as exc:
            emit_error("output_write_failed", f"could not write {args.output}: {exc}")
            return 1
    else:
        sys.stdout.write(notes)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
