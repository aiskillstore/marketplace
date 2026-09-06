#!/usr/bin/env python3
"""Prepare a local, SemVer-tagged Skill Forge release.

This command is intentionally local-only. It validates the current source,
promotes CHANGELOG.md's Unreleased section, creates one commit and an
annotated tag, then prints the push command that builds a validated candidate.
Publication additionally requires the reviewed receipt and exact-tag workflow
dispatch described in references/release-receipt.md.

Usage:
    python3 -S scripts/release_skill.py patch --dry-run
    python3 -S scripts/release_skill.py minor
    python3 -S scripts/release_skill.py major
    python3 -S scripts/release_skill.py --verify-tag v1.2.3
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Iterable, Mapping, Optional, Tuple

from release_metadata import (
    ChangelogMetadataError,
    has_release_candidate,
    parse_release_entry,
    parse_unreleased_entry,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
CHANGELOG = REPO_ROOT / "CHANGELOG.md"
VERSION_RE = re.compile(
    r"^v(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$"
)
GIT_TIMEOUT_SECONDS = 30
UNSAFE_GIT_ENVIRONMENT = {
    "GIT_ALTERNATE_OBJECT_DIRECTORIES",
    "GIT_AUTHOR_DATE",
    "GIT_CEILING_DIRECTORIES",
    "GIT_COMMON_DIR",
    "GIT_COMMITTER_DATE",
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


class ReleaseError(RuntimeError):
    """Raised for a release precondition or metadata failure."""


Version = Tuple[int, int, int]


def _git_environment() -> dict[str, str]:
    environment = os.environ.copy()
    for key in list(environment):
        if key in UNSAFE_GIT_ENVIRONMENT or key.startswith("GIT_CONFIG_"):
            environment.pop(key, None)
    environment["GIT_NO_REPLACE_OBJECTS"] = "1"
    environment["GIT_OPTIONAL_LOCKS"] = "0"
    return environment


def git(
    args: Iterable[str],
    *,
    check: bool = True,
    strip: bool = True,
    environment_overrides: Optional[Mapping[str, str]] = None,
    input_text: Optional[str] = None,
) -> str:
    """Run a Git command in the source checkout and return stdout."""
    materialized_args = list(args)
    try:
        environment = _git_environment()
        if environment_overrides:
            environment.update(environment_overrides)
        result = subprocess.run(
            ["git", "--no-replace-objects", *materialized_args],
            cwd=REPO_ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            input=input_text,
            check=False,
            timeout=GIT_TIMEOUT_SECONDS,
            env=environment,
        )
    except FileNotFoundError as exc:
        raise ReleaseError("git is not available on PATH") from exc
    except subprocess.TimeoutExpired as exc:
        raise ReleaseError(
            f"git command timed out after {exc.timeout} seconds"
        ) from exc
    except OSError as exc:
        raise ReleaseError(f"could not launch git: {exc}") from exc
    if check and result.returncode:
        detail = (result.stderr or result.stdout).strip()
        raise ReleaseError(f"git {' '.join(materialized_args)} failed: {detail}")
    return result.stdout.strip() if strip else result.stdout


def parse_version(tag: str) -> Version:
    """Parse the project's strict vMAJOR.MINOR.PATCH tag format."""
    match = VERSION_RE.fullmatch(tag)
    if not match:
        raise ReleaseError(f"expected a semantic version tag like v1.2.3, got {tag!r}")
    return tuple(int(group) for group in match.groups())  # type: ignore[return-value]


def format_version(version: Version) -> str:
    return f"v{version[0]}.{version[1]}.{version[2]}"


def bump(version: Version, level: str) -> Version:
    major, minor, patch = version
    if level == "major":
        return major + 1, 0, 0
    if level == "minor":
        return major, minor + 1, 0
    if level == "patch":
        return major, minor, patch + 1
    raise ReleaseError(f"unsupported release level: {level}")


def latest_reachable_version() -> tuple[str, Version]:
    """Return the highest valid release tag reachable from HEAD."""
    candidates = []
    for tag in git(["tag", "--merged", "HEAD"]).splitlines():
        try:
            candidates.append((tag, parse_version(tag)))
        except ReleaseError:
            continue
    if not candidates:
        raise ReleaseError("no reachable vMAJOR.MINOR.PATCH tag found")
    return max(candidates, key=lambda item: item[1])


def changelog_entry(text: str, tag: str) -> tuple[str, str]:
    """Return the date and non-empty body for one exact changelog version."""
    parse_version(tag)
    try:
        entry = parse_release_entry(text, tag, required=True)
    except ChangelogMetadataError as exc:
        raise ReleaseError(str(exc)) from exc
    assert entry is not None
    return entry.date, entry.body


def unreleased_body(text: str) -> tuple[int, str, int]:
    """Locate and validate the Unreleased section before the first release."""
    try:
        entry = parse_unreleased_entry(text)
    except ChangelogMetadataError as exc:
        raise ReleaseError(str(exc)) from exc
    return entry.heading_end, entry.body, entry.body_end


def promote_unreleased(text: str, tag: str, date: dt.date) -> str:
    """Promote Unreleased content into a dated release while retaining its header."""
    parse_version(tag)
    if has_release_candidate(text, tag):
        raise ReleaseError(f"CHANGELOG.md already contains {tag}")
    heading_end, body, body_end = unreleased_body(text)
    release = f"## [{tag}] - {date.isoformat()}\n\n{body}\n\n"
    return text[:heading_end] + "\n\n" + release + text[body_end:].lstrip("\n")


def require_clean_main() -> None:
    branch = git(["branch", "--show-current"])
    if branch != "main":
        raise ReleaseError(f"release from main only; current branch is {branch or 'detached HEAD'}")
    changes = git(["status", "--porcelain"])
    if changes:
        raise ReleaseError("working tree must be clean before preparing a release")


def run_gate(command: list[str], label: str) -> None:
    print(f"Running {label}...", flush=True)
    result = subprocess.run(command, cwd=REPO_ROOT, check=False)
    if result.returncode:
        raise ReleaseError(f"{label} failed with exit {result.returncode}")


def run_release_gates() -> None:
    """Run the same deterministic checks that protect the GitHub release."""
    python = sys.executable
    run_gate([python, "-S", "scripts/validate_audit_contract.py"], "audit contract validation")
    run_gate([python, "-S", "scripts/run_source_tests.py"], "source-only release tests")
    with tempfile.TemporaryDirectory(prefix="skill_forge_release_") as temp:
        archive = Path(temp) / "skill-forge.zip"
        extracted = Path(temp) / "extracted"
        run_gate(
            [python, "-S", "scripts/package_skill.py", "build", "--revision", "HEAD", "--output", str(archive)],
            "release package build",
        )
        run_gate(
            [
                python,
                "-S",
                "scripts/package_skill.py",
                "verify",
                str(archive),
                "--json",
                "--source-repo",
                str(REPO_ROOT),
            ],
            "release package verification",
        )
        run_gate(
            [python, "-S", "-m", "zipfile", "-e", str(archive), str(extracted)],
            "verified package extraction",
        )
        run_gate(
            [
                python,
                "-S",
                str(extracted / "skill-forge" / "scripts" / "run_self_tests.py"),
            ],
            "extracted runtime regression suite",
        )


def verify_tag(tag: str) -> None:
    """Validate the complete committed release/tag metadata contract."""
    parse_version(tag)
    exact_ref = f"refs/tags/{tag}"
    object_type = git(["cat-file", "-t", exact_ref])
    if object_type != "tag":
        raise ReleaseError(f"{tag} must be an annotated tag object")

    tag_commit = git(["rev-parse", f"{exact_ref}^{{commit}}"])
    head_commit = git(["rev-parse", "HEAD"])
    if tag_commit != head_commit:
        raise ReleaseError(f"{tag} must point at the checked-out release commit")
    highest_tag, _highest_version = latest_reachable_version()
    if highest_tag != tag:
        raise ReleaseError(
            f"{tag} is not the highest reachable semantic-version tag "
            f"(highest: {highest_tag})"
        )

    subject = git(["show", "-s", "--format=%s", tag_commit])
    expected_subject = f"chore(release): {tag}"
    if subject != expected_subject:
        raise ReleaseError(
            f"release commit subject must be exactly {expected_subject!r}"
        )

    committed_changelog = git(
        ["show", f"{tag_commit}:CHANGELOG.md"], strip=False
    )
    changelog_date, _body = changelog_entry(committed_changelog, tag)
    tagger_date = git(
        ["for-each-ref", "--format=%(taggerdate:short)", exact_ref]
    )
    try:
        parsed_tagger_date = dt.date.fromisoformat(tagger_date)
    except ValueError as exc:
        raise ReleaseError(
            f"annotated tag {tag} has an invalid tagger date: {tagger_date!r}"
        ) from exc
    if parsed_tagger_date.isoformat() != tagger_date:
        raise ReleaseError(
            f"annotated tag {tag} has a non-canonical tagger date: {tagger_date!r}"
        )
    if changelog_date != tagger_date:
        raise ReleaseError(
            f"CHANGELOG.md date {changelog_date} does not match annotated tagger date "
            f"{tagger_date} for {tag}"
        )
    print(f"Release metadata: PASS ({tag})")


def prepare_release(level: str, dry_run: bool) -> None:
    require_clean_main()
    initial_head = git(["rev-parse", "HEAD"])
    previous_tag, previous_version = latest_reachable_version()
    next_tag = format_version(bump(previous_version, level))
    changelog = CHANGELOG.read_text(encoding="utf-8")
    # Validate the section before expensive gates, but choose the release date
    # only after them so a midnight rollover cannot stale the tag metadata.
    unreleased_body(changelog)
    if has_release_candidate(changelog, next_tag):
        raise ReleaseError(f"CHANGELOG.md already contains {next_tag}")

    print(f"Preparing {next_tag} from {previous_tag} ({level} release).")
    run_release_gates()
    require_clean_main()
    if git(["rev-parse", "HEAD"]) != initial_head:
        raise ReleaseError("HEAD changed while release gates were running")
    current_tag, current_version = latest_reachable_version()
    if (current_tag, current_version) != (previous_tag, previous_version):
        raise ReleaseError("reachable semantic-version tags changed during release gates")
    if CHANGELOG.read_text(encoding="utf-8") != changelog:
        raise ReleaseError("CHANGELOG.md changed during release gates")

    release_timestamp = dt.datetime.now().astimezone()
    release_date = release_timestamp.date()
    updated_changelog = promote_unreleased(changelog, next_tag, release_date)

    if dry_run:
        print(f"Dry run passed. Would commit CHANGELOG.md, create annotated tag {next_tag}, then build a validated candidate with:")
        print(f"  git push --atomic origin main {next_tag}")
        print("Publication requires a reviewed receipt and exact-tag Release Skill dispatch; see references/release-receipt.md.")
        return

    CHANGELOG.write_text(updated_changelog, encoding="utf-8")
    expected_changelog_blob = git(
        ["hash-object", "--path=CHANGELOG.md", "--stdin"],
        input_text=updated_changelog,
    )
    git(["add", "--", "CHANGELOG.md"])
    staged_paths = git(["diff", "--cached", "--name-only", "--"]).splitlines()
    if staged_paths != ["CHANGELOG.md"]:
        raise ReleaseError(
            "release staging must contain exactly CHANGELOG.md; found: "
            + (", ".join(staged_paths) or "nothing")
        )
    unstaged_paths = git(["diff", "--name-only", "--"]).splitlines()
    untracked_paths = git(
        ["ls-files", "--others", "--exclude-standard"]
    ).splitlines()
    if unstaged_paths or untracked_paths:
        unexpected = sorted(set(unstaged_paths + untracked_paths))
        raise ReleaseError(
            "working tree changed during release preparation: "
            + ", ".join(unexpected)
        )
    staged_changelog_blob = git(["rev-parse", ":CHANGELOG.md"])
    if staged_changelog_blob != expected_changelog_blob:
        raise ReleaseError(
            "the staged CHANGELOG.md blob differs from the generated changelog "
            "after Git clean filters"
        )

    timestamp_text = release_timestamp.isoformat()
    expected_subject = f"chore(release): {next_tag}"
    with tempfile.TemporaryDirectory(prefix="skill_forge_empty_hooks_") as hooks_dir:
        git(
            [
                "-c",
                f"core.hooksPath={hooks_dir}",
                "-c",
                "commit.gpgSign=false",
                "commit",
                "--no-verify",
                "--only",
                "-m",
                expected_subject,
                "--",
                "CHANGELOG.md",
            ],
            environment_overrides={
                "GIT_AUTHOR_DATE": timestamp_text,
                "GIT_COMMITTER_DATE": timestamp_text,
            },
        )

    release_commit = git(["rev-parse", "HEAD"])
    parents = git(["rev-list", "--parents", "-n", "1", release_commit]).split()
    if parents != [release_commit, initial_head]:
        raise ReleaseError("release commit does not have exactly the expected parent")
    changed_paths = git(
        ["diff-tree", "--no-commit-id", "--name-only", "-r", release_commit]
    ).splitlines()
    if changed_paths != ["CHANGELOG.md"]:
        raise ReleaseError(
            "release commit changed paths other than CHANGELOG.md: "
            + ", ".join(changed_paths)
        )
    if git(["rev-parse", f"{release_commit}:CHANGELOG.md"]) != expected_changelog_blob:
        raise ReleaseError("release commit does not contain the generated CHANGELOG.md blob")
    if git(["show", "-s", "--format=%s", release_commit]) != expected_subject:
        raise ReleaseError("release commit subject changed during commit creation")
    require_clean_main()

    git(
        ["-c", "tag.gpgSign=false", "tag", "-a", next_tag, "-m", next_tag],
        environment_overrides={"GIT_COMMITTER_DATE": timestamp_text},
    )
    verify_tag(next_tag)
    print(f"Prepared local release {next_tag}. Build its validated candidate with:")
    print(f"  git push --atomic origin main {next_tag}")
    print("Publication requires a reviewed receipt and exact-tag Release Skill dispatch; see references/release-receipt.md.")


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare or verify a local Skill Forge release.")
    parser.add_argument("level", nargs="?", choices=("patch", "minor", "major"), help="semantic version increment to prepare")
    parser.add_argument("--dry-run", action="store_true", help="run every gate without editing, committing, or tagging")
    parser.add_argument("--verify-tag", metavar="TAG", help="validate a checked-out release tag and matching changelog entry")
    args = parser.parse_args(argv)
    if bool(args.level) == bool(args.verify_tag):
        parser.error("provide exactly one release level or --verify-tag TAG")
    if args.dry_run and not args.level:
        parser.error("--dry-run is valid only with patch, minor, or major")
    return args


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    try:
        if args.verify_tag:
            verify_tag(args.verify_tag)
        else:
            prepare_release(args.level, args.dry_run)
    except (OSError, ReleaseError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
