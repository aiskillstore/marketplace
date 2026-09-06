#!/usr/bin/env python3
"""Run source-checkout tests for release-only Skill Forge tooling.

The distributable runtime intentionally excludes this runner and the helpers it
tests. Runtime regressions live in ``run_self_tests.py`` so an extracted release
ZIP can exercise its complete shipped surface without source-only skips.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path, PureWindowsPath
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
RELEASE_TOOL = SCRIPT_DIR / "release_skill.py"
RELEASE_NOTES = SCRIPT_DIR / "generate_release_notes.py"
RELEASE_METADATA = SCRIPT_DIR / "release_metadata.py"
INDEPENDENT_EVALUATOR = SCRIPT_DIR / "verify_independent_evaluator.py"
RUNTIME_TESTS = SCRIPT_DIR / "run_self_tests.py"
RUNTIME_MANIFEST = SCRIPT_DIR / "runtime_manifest.py"
PACKAGE_TOOL = SCRIPT_DIR / "package_skill.py"
CONTRACT_VALIDATOR = SCRIPT_DIR / "validate_audit_contract.py"
SELF_TESTS_WORKFLOW = (
    SCRIPT_DIR.parent / ".github" / "workflows" / "self-tests.yml"
)
RELEASE_WORKFLOW = (
    SCRIPT_DIR.parent / ".github" / "workflows" / "release-skill.yml"
)


def load_module(path: Path, name: str) -> Any:
    """Load one source helper without relying on package installation."""

    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {path.name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def run_release_metadata_tool_case() -> dict[str, Any]:
    """Keep SemVer promotion and committed-release-note rendering stable."""

    try:
        release = load_module(RELEASE_TOOL, "skill_forge_release_tool_for_tests")
        notes = load_module(RELEASE_NOTES, "skill_forge_release_notes_for_tests")
        source = (
            "# Changelog\n\n"
            "## [Unreleased]\n\n"
            "### Fixed\n\n"
            "- Preserve the release history.\n\n"
            "## [v1.2.3] - 2026-07-14\n\n"
            "### Added\n\n"
            "- Previous release.\n"
        )
        promoted = release.promote_unreleased(
            source, "v1.2.4", dt.date(2026, 7, 15)
        )
        date, body = release.changelog_entry(promoted, "v1.2.4")
        note_entry = notes.changelog_entry(promoted, "v1.2.4")
        rendered = notes.render_committed_changelog(
            "v1.2.4", "v1.2.3", "owner/repo", note_entry
        )

        try:
            release.parse_version("v01.2.3")
        except release.ReleaseError:
            invalid_version_rejected = True
        else:
            invalid_version_rejected = False
        try:
            release.parse_version("v1\u0662.3.4")
        except release.ReleaseError:
            non_ascii_version_rejected = True
        else:
            non_ascii_version_rejected = False

        ok = (
            release.bump((1, 2, 3), "patch") == (1, 2, 4)
            and release.bump((1, 2, 3), "minor") == (1, 3, 0)
            and release.bump((1, 2, 3), "major") == (2, 0, 0)
            and date == "2026-07-15"
            and body == "### Fixed\n\n- Preserve the release history."
            and note_entry == (date, body)
            and "# skill-forge v1.2.4" in rendered
            and "Preserve the release history." in rendered
            and "https://github.com/owner/repo/compare/v1.2.3...v1.2.4" in rendered
            and invalid_version_rejected
            and non_ascii_version_rejected
        )
        reason = (
            ""
            if ok
            else f"unexpected promotion or release-note result: {promoted!r} / {rendered!r}"
        )
    except Exception as exc:
        ok = False
        reason = f"release metadata helper raised {type(exc).__name__}: {exc}"
    return {
        "name": "release tool promotes a SemVer changelog entry",
        "fixture": str(RELEASE_TOOL),
        "expected_exit": 0,
        "actual_exit": 0 if ok else 1,
        "expected_code": "release metadata",
        "result": "PASS" if ok else "FAIL",
        "reason": reason,
    }


def run_release_notes_temp_repo_case() -> dict[str, Any]:
    """Exercise Git cwd, hash width, dates, and write errors in isolation."""

    try:
        notes = load_module(
            RELEASE_NOTES, "skill_forge_release_notes_temp_repo_for_tests"
        )
        with tempfile.TemporaryDirectory(
            prefix="skill_forge_release_notes_repo_"
        ) as temp:
            repo = Path(temp) / "repo"
            repo.mkdir()

            def git(*args: str) -> str:
                proc = subprocess.run(
                    ["git", *args],
                    cwd=repo,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                    timeout=30,
                )
                if proc.returncode != 0:
                    raise RuntimeError(proc.stderr.strip() or proc.stdout.strip())
                return proc.stdout.strip()

            git("init", "--quiet")
            git(
                "config",
                "user.email",
                "skill-forge-tests@example.invalid",  # privacy-gate: allow
            )
            git("config", "user.name", "Skill Forge Tests")
            (repo / "notes.txt").write_text("base\n", encoding="utf-8")
            (repo / "CHANGELOG.md").write_text(
                "# Changelog\n\n"
                "## [Unreleased]\n\n"
                "## [v1.0.0] - 1969-12-31\n\n"
                "- Establish the release-note fixture.\n",
                encoding="utf-8",
            )
            git("add", "notes.txt", "CHANGELOG.md")
            git("commit", "--quiet", "-m", "chore: establish release-note fixture")
            git("tag", "v1.0.0")
            (repo / "notes.txt").write_text("base\nfix\n", encoding="utf-8")
            (repo / "CHANGELOG.md").write_text(
                "# Changelog\n\n"
                "## [Unreleased]\n\n"
                "## [v1.0.1] - 1970-01-01\n\n"
                "- Preserve deterministic release notes.\n\n"
                "## [v1.0.0] - 1969-12-31\n\n"
                "- Establish the release-note fixture.\n",
                encoding="utf-8",
            )
            git("add", "notes.txt", "CHANGELOG.md")
            git("commit", "--quiet", "-m", "fix: preserve deterministic release notes")
            git("tag", "v1.0.1")
            original_root = notes.REPO_ROOT
            original_changelog = notes.CHANGELOG_PATH
            original_epoch = os.environ.get("SOURCE_DATE_EPOCH")
            try:
                notes.REPO_ROOT = repo
                notes.CHANGELOG_PATH = repo / "CHANGELOG.md"
                os.environ["SOURCE_DATE_EPOCH"] = "0"
                output = repo / "release-notes.md"
                success = notes.main(
                    [
                        "--tag",
                        "v1.0.1",
                        "--previous",
                        "v1.0.0",
                        "--repo",
                        "owner/repo",
                        "--output",
                        str(output),
                    ]
                )
                rendered = output.read_text(encoding="utf-8") if output.exists() else ""
                blocked_parent = repo / "blocked-output"
                blocked_parent.write_text("not a directory\n", encoding="utf-8")
                stderr = StringIO()
                with redirect_stderr(stderr):
                    failed_write = notes.main(
                        [
                            "--tag",
                            "v1.0.1",
                            "--previous",
                            "v1.0.0",
                            "--output",
                            str(blocked_parent / "notes.md"),
                        ]
                    )
                write_error = json.loads(stderr.getvalue())
            finally:
                notes.REPO_ROOT = original_root
                notes.CHANGELOG_PATH = original_changelog
                if original_epoch is None:
                    os.environ.pop("SOURCE_DATE_EPOCH", None)
                else:
                    os.environ["SOURCE_DATE_EPOCH"] = original_epoch

        ok = (
            success == 0
            and "_Released 1970-01-01_" in rendered
            and "Preserve deterministic release notes." in rendered
            and failed_write == 1
            and write_error.get("error", {}).get("code") == "output_write_failed"
        )
        reason = (
            ""
            if ok
            else (
                f"success={success}; rendered={rendered!r}; "
                f"failed_write={failed_write}; write_error={write_error!r}"
            )
        )
    except Exception as exc:
        ok = False
        reason = (
            f"temporary release-notes repository test raised "
            f"{type(exc).__name__}: {exc}"
        )
    return {
        "name": "release notes use a temporary repository and reproducible output",
        "fixture": str(RELEASE_NOTES),
        "expected_exit": 0,
        "actual_exit": 0 if ok else 1,
        "expected_code": "deterministic release-note pipeline",
        "result": "PASS" if ok else "FAIL",
        "reason": reason,
    }


def run_release_tag_verification_case() -> dict[str, Any]:
    """Pressure-test annotated tag, committed changelog, and release gates."""

    try:
        release = load_module(RELEASE_TOOL, "skill_forge_release_tag_tests")
        notes = load_module(RELEASE_NOTES, "skill_forge_release_tag_note_tests")
        target_tag = "v1.2.3"
        release_date = "2026-07-15"
        fixed_timestamp = "2026-07-15T12:00:00+0000"
        valid_changelog = (
            "# Changelog\n\n"
            "## [Unreleased]\n\n"
            "- Future release work.\n\n"
            f"## [{target_tag}] - {release_date}\n\n"
            "- Preserve strict release evidence.\n"
        )

        def fixture_git(repo: Path, *args: str, env: Optional[dict[str, str]] = None) -> str:
            command_environment = os.environ.copy()
            if env:
                command_environment.update(env)
            proc = subprocess.run(
                ["git", *args],
                cwd=repo,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                timeout=30,
                env=command_environment,
            )
            if proc.returncode:
                raise RuntimeError(
                    f"git {' '.join(args)} failed: {proc.stderr.strip()}"
                )
            return proc.stdout.strip()

        def build_release_repo(
            parent: Path,
            *,
            changelog: str = valid_changelog,
            subject: str = f"chore(release): {target_tag}",
            annotated: bool = True,
            tagger_date: str = fixed_timestamp,
            higher_tag: bool = False,
        ) -> Path:
            repo = parent / "repo"
            repo.mkdir(parents=True)
            fixture_git(repo, "init", "--quiet")
            fixture_git(repo, "branch", "-M", "main")
            fixture_git(
                repo,
                "config",
                "user.email",
                "skill-forge-tests@example.invalid",  # privacy-gate: allow
            )
            fixture_git(repo, "config", "user.name", "Skill Forge Tests")
            (repo / "CHANGELOG.md").write_text(changelog, encoding="utf-8")
            fixture_git(repo, "add", "CHANGELOG.md")
            commit_environment = {
                "GIT_AUTHOR_DATE": fixed_timestamp,
                "GIT_COMMITTER_DATE": fixed_timestamp,
            }
            fixture_git(repo, "commit", "--quiet", "-m", subject, env=commit_environment)
            if annotated:
                fixture_git(
                    repo,
                    "tag",
                    "-a",
                    target_tag,
                    "-m",
                    target_tag,
                    env={"GIT_COMMITTER_DATE": tagger_date},
                )
            else:
                fixture_git(repo, "tag", target_tag)
            if higher_tag:
                fixture_git(
                    repo,
                    "tag",
                    "-a",
                    "v1.2.4",
                    "-m",
                    "v1.2.4",
                    env={"GIT_COMMITTER_DATE": tagger_date},
                )
            return repo

        class CRLFChangelogPath:
            """Write test changelog content as Windows-style text output."""

            def __init__(self, path: Path) -> None:
                self.path = path

            def read_text(self, *, encoding: str) -> str:
                return self.path.read_text(encoding=encoding)

            def write_text(self, text: str, *, encoding: str) -> int:
                normalized = text.replace("\r\n", "\n").replace("\n", "\r\n")
                self.path.write_bytes(normalized.encode(encoding))
                return len(text)

        original_release_root = release.REPO_ROOT
        original_release_changelog = release.CHANGELOG
        original_notes_root = notes.REPO_ROOT
        original_notes_changelog = notes.CHANGELOG_PATH
        original_release_gates = release.run_release_gates
        failures: list[str] = []

        def configure(repo: Path) -> None:
            release.REPO_ROOT = repo
            release.CHANGELOG = repo / "CHANGELOG.md"
            notes.REPO_ROOT = repo
            notes.CHANGELOG_PATH = repo / "CHANGELOG.md"

        def expect_verify_failure(repo: Path, expected: str, label: str) -> None:
            configure(repo)
            try:
                release.verify_tag(target_tag)
            except release.ReleaseError as exc:
                if expected not in str(exc):
                    failures.append(f"{label}: expected {expected!r}, got {exc!r}")
            else:
                failures.append(f"{label}: verification unexpectedly passed")

        with tempfile.TemporaryDirectory(prefix="skill_forge_release_tag_tests_") as temp:
            root = Path(temp)

            valid_repo = build_release_repo(root / "valid")
            configure(valid_repo)
            release.verify_tag(target_tag)

            lightweight_repo = build_release_repo(root / "lightweight", annotated=False)
            expect_verify_failure(
                lightweight_repo, "annotated tag object", "lightweight tag"
            )

            higher_repo = build_release_repo(root / "higher", higher_tag=True)
            expect_verify_failure(
                higher_repo, "highest reachable semantic-version tag", "lower tag"
            )

            wrong_subject_repo = build_release_repo(
                root / "subject", subject="chore: wrong release subject"
            )
            expect_verify_failure(
                wrong_subject_repo, "release commit subject must be exactly", "subject"
            )

            duplicate_changelog = (
                valid_changelog
                + f"\n## [{target_tag}] release duplicate\n\n- Duplicate.\n"
            )
            duplicate_repo = build_release_repo(
                root / "duplicate", changelog=duplicate_changelog
            )
            expect_verify_failure(
                duplicate_repo, "exactly one candidate heading", "duplicate heading"
            )
            try:
                notes.changelog_entry(duplicate_changelog, target_tag)
            except notes.ReleaseNotesError as exc:
                if exc.code != "changelog_entry_duplicate":
                    failures.append(
                        f"notes duplicate: expected changelog_entry_duplicate, got {exc.code}"
                    )
            else:
                failures.append("notes duplicate: parser unexpectedly passed")

            hidden_release_templates = (
                "<!--\n## [v1.2.3] - 2026-07-15\n\n- Hidden.\n-->\n",
                "```markdown\n## [v1.2.3] - 2026-07-15\n\n- Hidden.\n```\n",
                "~~~markdown\n## [v1.2.3] - 2026-07-15\n\n- Hidden.\n~~~\n",
                "<pre>\n## [v1.2.3] - 2026-07-15\n\n- Hidden.\n</pre>\n",
                "<script>\n## [v1.2.3] - 2026-07-15\n\n- Hidden.\n</script>\n",
                "<![CDATA[\n## [v1.2.3] - 2026-07-15\n\n- Hidden.\n]]>\n",
                "<div class=\"hidden\">\n## [v1.2.3] - 2026-07-15\n\n- Hidden.\n</div>\n",
                "<?hidden\n## [v1.2.3] - 2026-07-15\n\n- Hidden.\n?>\n",
                "<!DOCTYPE\n## [v1.2.3] - 2026-07-15\n\n- Hidden.\n>\n",
                "<div>hidden\n## [v1.2.3] - 2026-07-15\n\n- Hidden.\n</div>\n",
                "<custom/>\n## [v1.2.3] - 2026-07-15\n\n- Hidden.\n",
                "<script/>\n## [v1.2.3] - 2026-07-15\n\n- Hidden.\n",
                "<custom title=\"one > two\">\n## [v1.2.3] - 2026-07-15\n\n- Hidden.\n",
                "<div>\n\u00a0\n## [v1.2.3] - 2026-07-15\n- Hidden.\n</div>\n",
                "prefix\u2028## [v1.2.3] - 2026-07-15\n\n- Not a Markdown H2.\n",
            )
            for index, hidden_release in enumerate(hidden_release_templates):
                hidden_changelog = (
                    "# Changelog\n\n"
                    "## [Unreleased]\n\n"
                    "- Future release work.\n\n"
                    + hidden_release
                )
                hidden_repo = build_release_repo(
                    root / f"hidden-release-{index}",
                    changelog=hidden_changelog,
                )
                expect_verify_failure(
                    hidden_repo, "has no entry", f"hidden release heading {index}"
                )

            hidden_unreleased = (
                "# Changelog\n\n"
                "<!--\n## [Unreleased]\n\n- Hidden future work.\n-->\n\n"
                f"## [{target_tag}] - {release_date}\n\n"
                "- Preserve strict release evidence.\n"
            )
            try:
                release.unreleased_body(hidden_unreleased)
            except release.ReleaseError as exc:
                if "exact '## [Unreleased]'" not in str(exc):
                    failures.append(f"hidden Unreleased: unexpected error {exc!r}")
            else:
                failures.append("hidden Unreleased heading unexpectedly passed")

            missing_entry_repo = build_release_repo(
                root / "missing-entry",
                changelog=(
                    "# Changelog\n\n"
                    "## [Unreleased]\n\n"
                    "- No committed semantic release entry.\n"
                ),
            )
            configure(missing_entry_repo)
            missing_stderr = StringIO()
            with redirect_stderr(missing_stderr):
                missing_exit = notes.main(["--tag", target_tag])
            missing_error = json.loads(missing_stderr.getvalue())
            if not (
                missing_exit == 1
                and missing_error.get("error", {}).get("code")
                == "changelog_entry_missing"
            ):
                failures.append(
                    f"semantic tag fell back without a changelog entry: {missing_error!r}"
                )

            trailing_heading = valid_changelog.replace(
                f"## [{target_tag}] - {release_date}",
                f"## [{target_tag}] - {release_date} ",
            )
            trailing_repo = build_release_repo(
                root / "trailing", changelog=trailing_heading
            )
            expect_verify_failure(
                trailing_repo, "heading must be exactly", "trailing heading space"
            )

            invalid_date_changelog = valid_changelog.replace(
                release_date, "2026-02-30"
            )
            invalid_date_repo = build_release_repo(
                root / "invalid-date", changelog=invalid_date_changelog
            )
            expect_verify_failure(
                invalid_date_repo, "invalid calendar date", "invalid date"
            )

            mismatch_changelog = valid_changelog.replace(release_date, "2026-07-14")
            mismatch_repo = build_release_repo(
                root / "date-mismatch", changelog=mismatch_changelog
            )
            expect_verify_failure(
                mismatch_repo, "does not match annotated tagger date", "date mismatch"
            )

            committed_blob_repo = build_release_repo(root / "committed-blob")
            (committed_blob_repo / "CHANGELOG.md").write_text(
                "# Changed working tree\n", encoding="utf-8"
            )
            configure(committed_blob_repo)
            release.verify_tag(target_tag)
            tagged_entry = notes.load_changelog_entry(target_tag)
            if tagged_entry != (
                release_date,
                "- Preserve strict release evidence.",
            ):
                failures.append(f"tagged changelog blob was not authoritative: {tagged_entry!r}")

            replacement_repo = build_release_repo(root / "replacement")
            original_commit = fixture_git(replacement_repo, "rev-parse", "HEAD")
            tree = fixture_git(replacement_repo, "rev-parse", "HEAD^{tree}")
            replacement_commit = fixture_git(
                replacement_repo,
                "commit-tree",
                tree,
                "-m",
                "attacker replacement subject",
                env={
                    "GIT_AUTHOR_DATE": fixed_timestamp,
                    "GIT_COMMITTER_DATE": fixed_timestamp,
                },
            )
            fixture_git(replacement_repo, "replace", original_commit, replacement_commit)
            configure(replacement_repo)
            previous_git_dir = os.environ.get("GIT_DIR")
            previous_git_config = os.environ.get("GIT_CONFIG")
            os.environ["GIT_DIR"] = str(root / "poisoned-git-dir")
            os.environ["GIT_CONFIG"] = str(root / "poisoned-git-config")
            try:
                release.verify_tag(target_tag)
                loaded = notes.load_changelog_entry(target_tag)
                if loaded is None:
                    failures.append("replacement/env sanitization lost tagged changelog")
            finally:
                if previous_git_dir is None:
                    os.environ.pop("GIT_DIR", None)
                else:
                    os.environ["GIT_DIR"] = previous_git_dir
                if previous_git_config is None:
                    os.environ.pop("GIT_CONFIG", None)
                else:
                    os.environ["GIT_CONFIG"] = previous_git_config

            duplicate_unreleased = valid_changelog.replace(
                "## [Unreleased]",
                "## [Unreleased]\n\n- One.\n\n## [Unreleased]",
            )
            try:
                release.unreleased_body(duplicate_unreleased)
            except release.ReleaseError as exc:
                if "exactly one Unreleased" not in str(exc):
                    failures.append(f"duplicate Unreleased: unexpected error {exc!r}")
            else:
                failures.append("duplicate Unreleased heading unexpectedly passed")

            prepare_repo = build_release_repo(root / "prepare")
            configure(prepare_repo)
            release.run_release_gates = lambda: None
            output = StringIO()
            with redirect_stdout(output):
                release.prepare_release("patch", True)
            if "git push --atomic origin main v1.2.4" not in output.getvalue():
                failures.append("dry-run publication guidance is not atomic")

            configure(prepare_repo)

            def stage_unrelated() -> None:
                (prepare_repo / "UNRELATED.txt").write_text(
                    "unexpected gate mutation\n", encoding="utf-8"
                )
                fixture_git(prepare_repo, "add", "UNRELATED.txt")

            release.run_release_gates = stage_unrelated
            before_commit = fixture_git(prepare_repo, "rev-parse", "HEAD")
            before_changelog = (prepare_repo / "CHANGELOG.md").read_bytes()
            try:
                release.prepare_release("patch", False)
            except release.ReleaseError:
                pass
            else:
                failures.append("gate mutation unexpectedly produced a release")
            after_commit = fixture_git(prepare_repo, "rev-parse", "HEAD")
            if after_commit != before_commit:
                failures.append("gate mutation created an unexpected release commit")
            if (prepare_repo / "CHANGELOG.md").read_bytes() != before_changelog:
                failures.append("gate mutation changed CHANGELOG.md before aborting")
            if fixture_git(prepare_repo, "tag", "--list", "v1.2.4"):
                failures.append("gate mutation created an unexpected release tag")

            clean_gate_repo = build_release_repo(root / "clean-gate-mutation")
            configure(clean_gate_repo)

            def commit_during_gate() -> None:
                (clean_gate_repo / "GATE.txt").write_text(
                    "clean gate commit\n", encoding="utf-8"
                )
                fixture_git(clean_gate_repo, "add", "GATE.txt")
                fixture_git(
                    clean_gate_repo,
                    "commit",
                    "--quiet",
                    "-m",
                    "test: mutate HEAD during release gate",
                    env={
                        "GIT_AUTHOR_DATE": fixed_timestamp,
                        "GIT_COMMITTER_DATE": fixed_timestamp,
                    },
                )

            release.run_release_gates = commit_during_gate
            try:
                release.prepare_release("patch", False)
            except release.ReleaseError as exc:
                if "HEAD changed" not in str(exc):
                    failures.append(f"clean gate commit: unexpected error {exc!r}")
            else:
                failures.append("clean gate commit unexpectedly produced a release")
            if fixture_git(clean_gate_repo, "tag", "--list", "v1.2.4"):
                failures.append("clean gate commit created an unexpected release tag")

            hook_repo = build_release_repo(root / "hook-defense")
            hook = hook_repo / ".git" / "hooks" / "pre-commit"
            hook.write_text(
                "#!/bin/sh\n"
                "printf 'hook mutation\\n' > OTHER.txt\n"
                "git add OTHER.txt\n",
                encoding="utf-8",
            )
            hook.chmod(0o755)
            configure(hook_repo)
            release.run_release_gates = lambda: None
            previous_author_date = os.environ.get("GIT_AUTHOR_DATE")
            previous_committer_date = os.environ.get("GIT_COMMITTER_DATE")
            os.environ["GIT_AUTHOR_DATE"] = "1999-01-01T00:00:00+0000"
            os.environ["GIT_COMMITTER_DATE"] = "1999-01-01T00:00:00+0000"
            hook_output = StringIO()
            try:
                with redirect_stdout(hook_output):
                    release.prepare_release("patch", False)
            finally:
                if previous_author_date is None:
                    os.environ.pop("GIT_AUTHOR_DATE", None)
                else:
                    os.environ["GIT_AUTHOR_DATE"] = previous_author_date
                if previous_committer_date is None:
                    os.environ.pop("GIT_COMMITTER_DATE", None)
                else:
                    os.environ["GIT_COMMITTER_DATE"] = previous_committer_date
            hook_paths = fixture_git(
                hook_repo,
                "diff-tree",
                "--no-commit-id",
                "--name-only",
                "-r",
                "HEAD",
            ).splitlines()
            hook_tagger_date = fixture_git(
                hook_repo,
                "for-each-ref",
                "--format=%(taggerdate:short)",
                "refs/tags/v1.2.4",
            )
            if hook_paths != ["CHANGELOG.md"]:
                failures.append(f"release hook injected committed paths: {hook_paths!r}")
            if (hook_repo / "OTHER.txt").exists():
                failures.append("disabled pre-commit hook still executed")
            if hook_tagger_date != dt.date.today().isoformat():
                failures.append(
                    f"ambient tagger date poisoned the release: {hook_tagger_date!r}"
                )
            if "git push --atomic origin main v1.2.4" not in hook_output.getvalue():
                failures.append("prepared release publication guidance is not atomic")

            crlf_repo = build_release_repo(root / "crlf-clean-filter")
            fixture_git(crlf_repo, "config", "core.autocrlf", "input")
            configure(crlf_repo)
            release.CHANGELOG = CRLFChangelogPath(crlf_repo / "CHANGELOG.md")
            release.run_release_gates = lambda: None
            crlf_output = StringIO()
            try:
                with redirect_stdout(crlf_output):
                    release.prepare_release("patch", False)
            except release.ReleaseError as exc:
                failures.append(f"CRLF release preparation failed: {exc}")
            else:
                if not fixture_git(crlf_repo, "tag", "--list", "v1.2.4"):
                    failures.append("CRLF release preparation did not create its tag")

            release_workflow = (
                SCRIPT_DIR.parent / ".github" / "workflows" / "release-skill.yml"
            )
            workflow_text = release_workflow.read_text(encoding="utf-8")
            required_workflow_fragments = (
                "ref: ${{ needs.validate.outputs.commit }}",
                "fetch-depth: 0",
                "fetch-tags: true",
                "name: Restore and prove annotated release tag",
                "git fetch --force --no-tags origin",
                '"refs/tags/${RELEASE_TAG}:refs/tags/${RELEASE_TAG}"',
                'git cat-file -t "refs/tags/${RELEASE_TAG}"',
                'git rev-parse "refs/tags/${RELEASE_TAG}^{commit}"',
                'test "${tag_type}" = "tag"',
                'test "${tag_commit}" = "${head_commit}"',
                'gh release create "${RELEASE_TAG}"',
                "--verify-tag",
                "verify-publication:",
                "name: Verify published release assets",
                "name: Restore and prove published annotated tag",
                "name: Download published release assets by exact tag",
                'gh release download "${RELEASE_TAG}"',
                '--pattern "skill-forge.zip"',
                '--pattern "skill-forge.zip.sha256"',
                "cmp --silent validated/skill-forge.zip published/skill-forge.zip",
                "sha256sum --check --strict skill-forge.zip.sha256",
                "name: Source-prove published archive and canonical profiles",
                "published/skill-forge.zip",
                "--source-repo .",
            )
            missing_workflow_fragments = [
                fragment
                for fragment in required_workflow_fragments
                if fragment not in workflow_text
            ]
            if missing_workflow_fragments:
                failures.append(
                    "release workflow lost annotated-tag or publication protection: "
                    + ", ".join(missing_workflow_fragments)
                )

        ok = not failures
        reason = "; ".join(failures)
    except Exception as exc:
        ok = False
        reason = f"release-tag regression raised {type(exc).__name__}: {exc}"
    finally:
        if "original_release_root" in locals():
            release.REPO_ROOT = original_release_root
            release.CHANGELOG = original_release_changelog
            release.run_release_gates = original_release_gates
        if "original_notes_root" in locals():
            notes.REPO_ROOT = original_notes_root
            notes.CHANGELOG_PATH = original_notes_changelog

    return {
        "name": "release tags and notes require committed, unique, atomic evidence",
        "fixture": str(RELEASE_TOOL),
        "expected_exit": 0,
        "actual_exit": 0 if ok else 1,
        "expected_code": "annotated tag and committed changelog invariants",
        "result": "PASS" if ok else "FAIL",
        "reason": reason,
    }


def run_independent_evaluator_case() -> dict[str, Any]:
    """Prove scratch-only independent evaluation and failure semantics."""

    try:
        evaluator = load_module(
            INDEPENDENT_EVALUATOR, "skill_forge_independent_evaluator_tests"
        )
        failures: list[str] = []
        inspector = load_module(
            SCRIPT_DIR / "inspect_skill_package.py",
            "skill_forge_independent_evaluator_schema_tests",
        )
        if (
            evaluator.REQUIRED_INSPECTOR_SCHEMA_VERSION
            != inspector.INSPECTION_SCHEMA_VERSION
        ):
            failures.append(
                "independent evaluator schema requirement drifted from the inspector"
            )
        if not (
            evaluator.BOOTSTRAP_INSPECTOR_SCHEMA_VERSION == 5
            and evaluator.BOOTSTRAP_SCHEMA_TRANSITION == "5:6"
            and evaluator.BOOTSTRAP_RELEASE_TAG == "v2.0.0"
            and evaluator.BOOTSTRAP_TRANSITION_REUSABLE is False
        ):
            failures.append("independent evaluator bootstrap transition drifted")

        def stub_source(mode: str) -> str:
            return (
                "import json, pathlib, sys, time\n"
                "target = sys.argv[sys.argv.index('--target') + 1]\n"
                f"mode = {mode!r}\n"
                "if mode == 'write':\n"
                "    pathlib.Path(__file__).with_name('scratch-write.txt').write_text('scratch only\\n', encoding='utf-8')\n"
                "if mode == 'candidate-write':\n"
                "    pathlib.Path(sys.argv[1]).write_text('scratch candidate changed\\n', encoding='utf-8')\n"
                "if mode == 'timeout':\n"
                "    time.sleep(2)\n"
                "if mode == 'output':\n"
                "    print('X' * 5000)\n"
                "    raise SystemExit(0)\n"
                "if mode == 'nonzero':\n"
                "    raise SystemExit(7)\n"
                "if mode == 'malformed':\n"
                "    print('{')\n"
                "    raise SystemExit(0)\n"
                "if mode == 'deep-json':\n"
                "    print('{\\\"x\\\":' * 80 + '0' + '}' * 80)\n"
                "    raise SystemExit(0)\n"
                "canonical = 'portable' if mode == 'target-mismatch' else target\n"
                "coverage = False if mode == 'incomplete' else True\n"
                "report = {\n"
                "    'schema_version': 4 if mode == 'stale-schema' else 5 if mode == 'schema-5' else 6,\n"
                "    'input': sys.argv[1], 'input_exists': True, 'input_type': 'zip',\n"
                "    'manifest_verification_complete': True,\n"
                "    'requested_target': target,\n"
                "    'canonical_target': canonical,\n"
                "    'target_alias_used': False,\n"
                "    'coverage_complete': coverage,\n"
                "    'summary': {\n"
                "        'status': 'pass', 'strict_pass': True,\n"
                "        'error_count': 1 if mode == 'inconsistent-summary' else 0,\n"
                "        'warning_count': 0,\n"
                "        'finding_count': 1 if mode == 'inconsistent-summary' else 0,\n"
                "    },\n"
                "    'frontmatter': {'name': 'RAW_SCHEMA_5_FRONTMATTER_SENTINEL'},\n"
                "}\n"
                "if mode == 'opaque-input':\n"
                "    report['input'] = '[redacted-0001]'\n"
                "if mode == 'unrelated-input':\n"
                "    report['input'] = str(pathlib.Path(sys.argv[1]).with_name('unrelated.zip'))\n"
                "print(json.dumps(report, sort_keys=True))\n"
            )

        def build_stub(
            parent: Path, mode: str, *, crlf: bool = False
        ) -> tuple[Path, str]:
            suffix = "-crlf" if crlf else ""
            root = parent / f"evaluator-{mode}{suffix}"
            scripts = root / "scripts"
            scripts.mkdir(parents=True)
            inspector = scripts / "inspect_skill_package.py"
            source = stub_source(mode)
            if crlf:
                crlf_source = source.replace("\r\n", "\n").replace("\n", "\r\n")
                inspector.write_bytes(crlf_source.encode("utf-8"))
            else:
                inspector.write_text(source, encoding="utf-8")
            digest = hashlib.sha256(inspector.read_bytes()).hexdigest()
            return root, digest

        with tempfile.TemporaryDirectory(
            prefix="skill_forge_independent_evaluator_tests_"
        ) as temp:
            root = Path(temp)
            candidate = root / "candidate.zip"
            candidate.write_bytes(b"independent evaluator candidate fixture\n")
            candidate_before = hashlib.sha256(candidate.read_bytes()).hexdigest()

            def verify_stub(
                stub_root: Path,
                inspector_digest: Optional[str],
                *,
                tree_digest: Optional[str] = None,
                candidate_digest: Optional[str] = None,
                bootstrap_schema_transition: Optional[str] = None,
                bootstrap_release_tag: Optional[str] = None,
            ) -> dict[str, Any]:
                pinned_tree = (
                    tree_digest
                    if tree_digest is not None
                    else evaluator._scan_tree(stub_root).sha256
                )
                return evaluator.verify_independently(
                    stub_root,
                    candidate,
                    inspector_digest,
                    pinned_tree,
                    candidate_digest or candidate_before,
                    bootstrap_schema_transition,
                    bootstrap_release_tag,
                )

            clean_root, clean_digest = build_stub(root, "clean")
            sensitive_candidate = root / ("candidate-person" + "@example.invalid.zip")
            sensitive_candidate.write_bytes(candidate.read_bytes())
            sensitive_report = evaluator.verify_independently(
                clean_root, sensitive_candidate, clean_digest,
                evaluator._scan_tree(clean_root).sha256, candidate_before,
            )
            if sensitive_report.get("status") != "pass":
                failures.append("sensitive original candidate name broke scratch candidate binding")
            clean_report = verify_stub(clean_root, clean_digest)
            if not (
                clean_report.get("status") == "pass"
                and set(clean_report.get("profiles", {})) == set(evaluator.PROFILES)
                and all(
                    item.get("status") == "pass"
                    for item in clean_report.get("profiles", {}).values()
                )
                and clean_report.get("scratch_execution") is True
                and clean_report.get("installed_mutated") is False
                and clean_report.get("installed_integrity_verified") is True
                and clean_report.get("candidate_mutated") is False
                and clean_report.get("candidate_integrity_verified") is True
            ):
                failures.append(f"clean evaluator report was not a pass: {clean_report!r}")

            crlf_root, crlf_digest = build_stub(root, "clean", crlf=True)
            crlf_report = verify_stub(crlf_root, crlf_digest)
            if not (
                crlf_report.get("status") == "pass"
                and crlf_report.get("installed_integrity_verified") is True
                and crlf_report.get("candidate_integrity_verified") is True
            ):
                failures.append(
                    "CRLF evaluator fixture was not a pass: " + repr(crlf_report)
                )

            write_root, write_digest = build_stub(root, "write")
            write_report = verify_stub(write_root, write_digest)
            if not (
                write_report.get("status") == "fail"
                and write_report.get("installed_mutated") is False
                and write_report.get("installed_integrity_verified") is True
                and not (write_root / "scripts" / "scratch-write.txt").exists()
                and any(
                    "scratch evaluator changed" in error
                    for error in write_report.get("errors", [])
                )
            ):
                failures.append(
                    f"scratch-write evaluator escaped or passed: {write_report!r}"
                )

            candidate_write_root, candidate_write_digest = build_stub(
                root, "candidate-write"
            )
            candidate_write_report = verify_stub(
                candidate_write_root, candidate_write_digest
            )
            if not (
                candidate_write_report.get("status") == "fail"
                and candidate_write_report.get("candidate_mutated") is False
                and candidate_write_report.get("candidate_integrity_verified") is True
                and any(
                    "scratch candidate changed" in error
                    for error in candidate_write_report.get("errors", [])
                )
            ):
                failures.append(
                    "scratch candidate mutation escaped or passed: "
                    f"{candidate_write_report!r}"
                )

            mismatch_report = verify_stub(clean_root, "0" * 64)
            if not (
                mismatch_report.get("status") == "not_assessed"
                and not mismatch_report.get("profiles")
                and any(
                    "does not match" in error
                    for error in mismatch_report.get("errors", [])
                )
            ):
                failures.append(f"digest mismatch did not stop execution: {mismatch_report!r}")

            tree_mismatch_report = verify_stub(
                clean_root, clean_digest, tree_digest="f" * 64
            )
            if not (
                tree_mismatch_report.get("status") == "not_assessed"
                and not tree_mismatch_report.get("profiles")
                and any(
                    "tree SHA-256 does not match" in error
                    for error in tree_mismatch_report.get("errors", [])
                )
            ):
                failures.append(
                    f"tree digest mismatch did not stop execution: {tree_mismatch_report!r}"
                )

            candidate_mismatch_report = verify_stub(
                clean_root, clean_digest, candidate_digest="e" * 64
            )
            if not (
                candidate_mismatch_report.get("status") == "not_assessed"
                and not candidate_mismatch_report.get("profiles")
                and any(
                    "candidate SHA-256 does not match" in error
                    for error in candidate_mismatch_report.get("errors", [])
                )
            ):
                failures.append(
                    "candidate digest mismatch did not stop execution: "
                    f"{candidate_mismatch_report!r}"
                )

            stale_root, stale_digest = build_stub(root, "stale-schema")
            stale_report = verify_stub(stale_root, stale_digest)
            if not (
                stale_report.get("status") == "not_assessed"
                and all(
                    item.get("status") == "not_assessed"
                    for item in stale_report.get("profiles", {}).values()
                )
            ):
                failures.append(f"stale evaluator schema was accepted: {stale_report!r}")

            schema_5_root, schema_5_digest = build_stub(root, "schema-5")
            schema_5_default_report = verify_stub(schema_5_root, schema_5_digest)
            if not (
                schema_5_default_report.get("status") == "not_assessed"
                and all(
                    item.get("status") == "not_assessed"
                    for item in schema_5_default_report.get("profiles", {}).values()
                )
            ):
                failures.append(
                    "schema 5 evaluator passed without transition opt-in: "
                    f"{schema_5_default_report!r}"
                )

            schema_5_transition_report = verify_stub(
                schema_5_root,
                schema_5_digest,
                bootstrap_schema_transition="5:6",
                bootstrap_release_tag="v2.0.0",
            )
            serialized_transition_report = json.dumps(
                schema_5_transition_report,
                sort_keys=True,
            )
            if not (
                schema_5_transition_report.get("status") == "pass"
                and schema_5_transition_report.get("evidence_class")
                == "bootstrap_transition"
                and schema_5_transition_report.get("schema_transition", {}).get(
                    "activated"
                )
                is True
                and schema_5_transition_report.get("schema_transition", {}).get(
                    "counts_as_independent_schema_6_pass"
                )
                is False
                and schema_5_transition_report.get("schema_transition", {}).get(
                    "reusable_after_release"
                )
                is False
                and all(
                    item.get("status") == "pass"
                    and item.get("schema_version") == 5
                    and item.get("schema_compatibility") == "bootstrap_5_to_6"
                    and item.get("evidence_label")
                    == evaluator.BOOTSTRAP_EVIDENCE_LABEL
                    and item.get("raw_frontmatter_propagated") is False
                    for item in schema_5_transition_report.get(
                        "profiles", {}
                    ).values()
                )
                and "RAW_SCHEMA_5_FRONTMATTER_SENTINEL"
                not in serialized_transition_report
            ):
                failures.append(
                    "schema 5 transition evidence was unsafe or incomplete: "
                    f"{schema_5_transition_report!r}"
                )

            for transition, release_tag, label in (
                ("5:6", None, "missing release tag"),
                (None, "v2.0.0", "missing schema transition"),
                ("5:6", "v2.0.1", "post-v2 reuse"),
                ("4:6", "v2.0.0", "wrong source schema"),
            ):
                invalid_transition_report = verify_stub(
                    schema_5_root,
                    schema_5_digest,
                    bootstrap_schema_transition=transition,
                    bootstrap_release_tag=release_tag,
                )
                if not (
                    invalid_transition_report.get("status") == "not_assessed"
                    and not invalid_transition_report.get("profiles")
                    and invalid_transition_report.get("schema_transition", {}).get(
                        "activated"
                    )
                    is False
                ):
                    failures.append(
                        f"{label} transition was accepted: "
                        f"{invalid_transition_report!r}"
                    )

            schema_6_transition_report = verify_stub(
                clean_root,
                clean_digest,
                bootstrap_schema_transition="5:6",
                bootstrap_release_tag="v2.0.0",
            )
            if not (
                schema_6_transition_report.get("status") == "not_assessed"
                and all(
                    item.get("status") == "not_assessed"
                    for item in schema_6_transition_report.get(
                        "profiles", {}
                    ).values()
                )
            ):
                failures.append(
                    "schema 6 evaluator was accepted through bootstrap mode: "
                    f"{schema_6_transition_report!r}"
                )

            stale_transition_report = verify_stub(
                stale_root,
                stale_digest,
                bootstrap_schema_transition="5:6",
                bootstrap_release_tag="v2.0.0",
            )
            if not (
                stale_transition_report.get("status") == "not_assessed"
                and all(
                    item.get("status") == "not_assessed"
                    for item in stale_transition_report.get(
                        "profiles", {}
                    ).values()
                )
            ):
                failures.append(
                    "schema 4 evaluator was accepted through bootstrap mode: "
                    f"{stale_transition_report!r}"
                )

            readonly_root, readonly_digest = build_stub(root, "readonly")
            readonly_scripts = readonly_root / "scripts"
            readonly_inspector = readonly_scripts / "inspect_skill_package.py"
            readonly_inspector.chmod(0o444)
            readonly_scripts.chmod(0o555)
            try:
                readonly_report = verify_stub(readonly_root, readonly_digest)
            finally:
                readonly_scripts.chmod(0o755)
                readonly_inspector.chmod(0o644)
            if readonly_report.get("status") != "pass":
                failures.append(
                    f"read-only evaluator could not be copied safely: {readonly_report!r}"
                )

            overlap_report = evaluator.verify_independently(
                evaluator.SOURCE_REPO,
                candidate,
                None,
                "0" * 64,
                candidate_before,
            )
            if not (
                overlap_report.get("status") == "not_assessed"
                and overlap_report.get("installed_mutated") is None
                and overlap_report.get("candidate_mutated") is None
                and any(
                    "overlaps the source repository" in error
                    for error in overlap_report.get("errors", [])
                )
            ):
                failures.append(f"source-overlap evaluator was accepted: {overlap_report!r}")

            source_text = str(evaluator.SOURCE_REPO)
            case_alias_text = (
                source_text.replace("/Users/", "/users/", 1)
                if source_text.startswith("/Users/")
                else source_text
            )
            case_alias = Path(case_alias_text)
            if case_alias != evaluator.SOURCE_REPO and case_alias.exists():
                try:
                    same_source = os.path.samefile(case_alias, evaluator.SOURCE_REPO)
                except OSError:
                    same_source = False
                if same_source:
                    alias_report = evaluator.verify_independently(
                        case_alias,
                        candidate,
                        None,
                        "0" * 64,
                        candidate_before,
                    )
                    if not (
                        alias_report.get("status") == "not_assessed"
                        and any(
                            "overlaps the source repository" in error
                            for error in alias_report.get("errors", [])
                        )
                    ):
                        failures.append(
                            f"case-alias source evaluator was accepted: {alias_report!r}"
                        )

            for mode in (
                "nonzero",
                "malformed",
                "deep-json",
                "target-mismatch",
                "incomplete",
                "inconsistent-summary",
                "opaque-input",
                "unrelated-input",
            ):
                mode_root, mode_digest = build_stub(root, mode)
                report = verify_stub(mode_root, mode_digest)
                if report.get("status") != "fail":
                    failures.append(f"{mode} evaluator was not Fail: {report!r}")

            original_timeout = evaluator.PROCESS_TIMEOUT_SECONDS
            try:
                evaluator.PROCESS_TIMEOUT_SECONDS = 0.1
                timeout_root, timeout_digest = build_stub(root, "timeout")
                timeout_report = verify_stub(timeout_root, timeout_digest)
            finally:
                evaluator.PROCESS_TIMEOUT_SECONDS = original_timeout
            if not (
                timeout_report.get("status") == "not_assessed"
                and any(
                    item.get("status") == "not_assessed"
                    for item in timeout_report.get("profiles", {}).values()
                )
            ):
                failures.append(f"timeout was not Not Assessed: {timeout_report!r}")

            original_stream_limit = evaluator.MAX_STREAM_BYTES
            try:
                evaluator.MAX_STREAM_BYTES = 256
                output_root, output_digest = build_stub(root, "output")
                output_report = verify_stub(output_root, output_digest)
            finally:
                evaluator.MAX_STREAM_BYTES = original_stream_limit
            if not (
                output_report.get("status") == "not_assessed"
                and any(
                    item.get("status") == "not_assessed"
                    for item in output_report.get("profiles", {}).values()
                )
            ):
                failures.append(f"output cap was not Not Assessed: {output_report!r}")

            candidate_after = hashlib.sha256(candidate.read_bytes()).hexdigest()
            if candidate_after != candidate_before:
                failures.append("independent evaluator modified the original candidate")

        ok = not failures
        reason = "; ".join(failures)
    except Exception as exc:
        ok = False
        reason = f"independent-evaluator regression raised {type(exc).__name__}: {exc}"
    return {
        "name": "independent evaluator runs only pinned scratch copies",
        "fixture": str(INDEPENDENT_EVALUATOR),
        "expected_exit": 0,
        "actual_exit": 0 if ok else 1,
        "expected_code": "two-profile scratch evaluation with mutation proof",
        "result": "PASS" if ok else "FAIL",
        "reason": reason,
    }


def run_runtime_surface_split_case() -> dict[str, Any]:
    """Prove runtime/source boundaries stay authoritative and fail closed."""

    try:
        runtime_source = RUNTIME_TESTS.read_text(encoding="utf-8")
        runtime_manifest = load_module(
            RUNTIME_MANIFEST, "skill_forge_runtime_manifest_surface_tests"
        )
        package = load_module(PACKAGE_TOOL, "skill_forge_package_surface_tests")
        validator = load_module(
            CONTRACT_VALIDATOR, "skill_forge_runtime_boundary_contract_tests"
        )
        forbidden_runtime_symbols = (
            "RELEASE_TOOL",
            "RELEASE_NOTES",
            "source_release_helpers_available",
            "run_release_metadata_tool_case",
            "run_release_notes_temp_repo_case",
            "skip_source_only_release_case",
        )
        leaked_symbols = [
            symbol for symbol in forbidden_runtime_symbols if symbol in runtime_source
        ]
        selectors = tuple(runtime_manifest.SKILL_FORGE_RUNTIME_SELECTORS)
        source_only = tuple(runtime_manifest.SKILL_FORGE_SOURCE_ONLY_SCRIPTS)
        declaration_issues: list[str] = []
        declared = validator.source_only_declaration_paths(
            (SCRIPT_DIR.parent / "SKILL.md").read_text(encoding="utf-8"),
            declaration_issues,
        )
        clean_boundary = runtime_manifest.runtime_boundary_issues(
            selectors,
            package.FORBIDDEN_RUNTIME_PATHS,
            declared,
        )
        missing_boundary = runtime_manifest.runtime_boundary_issues(
            selectors,
            source_only[:-1],
            source_only,
        )
        extra_boundary = runtime_manifest.runtime_boundary_issues(
            selectors,
            source_only,
            (*source_only, "scripts/unexpected-source-only.py"),
        )
        misclassified_boundary = runtime_manifest.runtime_boundary_issues(
            (*selectors, source_only[0]),
            source_only,
            source_only,
        )
        ok = (
            not leaked_symbols
            and not declaration_issues
            and not clean_boundary
            and any("missing canonical paths" in item for item in missing_boundary)
            and any("non-canonical paths" in item for item in extra_boundary)
            and any(
                "runtime selectors include source-only paths" in item
                for item in misclassified_boundary
            )
        )
        reason = (
            ""
            if ok
            else (
                f"leaked_symbols={leaked_symbols!r}; declaration={declaration_issues!r}; "
                f"clean={clean_boundary!r}; missing={missing_boundary!r}; "
                f"extra={extra_boundary!r}; misclassified={misclassified_boundary!r}"
            )
        )
    except Exception as exc:
        ok = False
        reason = f"runtime/source split check raised {type(exc).__name__}: {exc}"
    return {
        "name": "runtime/source boundary stays centralized and fails closed",
        "fixture": str(RUNTIME_TESTS),
        "expected_exit": 0,
        "actual_exit": 0 if ok else 1,
        "expected_code": "runtime/source boundary drift guard",
        "result": "PASS" if ok else "FAIL",
        "reason": reason,
    }


def run_cross_platform_contract_path_case() -> dict[str, Any]:
    """Keep repository-relative contract identities portable on Windows."""

    try:
        validator = load_module(
            CONTRACT_VALIDATOR, "skill_forge_contract_path_identity_tests"
        )
        root = PureWindowsPath("D:/repo")
        reference = root / "references" / "audit-contract.json"
        actual = validator.repo_relative(reference, root)
        ok = actual == "references/audit-contract.json"
        reason = "" if ok else f"unexpected canonical reference path: {actual!r}"
    except Exception as exc:
        ok = False
        reason = f"contract path regression raised {type(exc).__name__}: {exc}"
    return {
        "name": "contract reference identities stay POSIX on Windows",
        "fixture": str(CONTRACT_VALIDATOR),
        "expected_exit": 0,
        "actual_exit": 0 if ok else 1,
        "expected_code": "cross-platform reference identity",
        "result": "PASS" if ok else "FAIL",
        "reason": reason,
    }


def run_workflow_configuration_case() -> dict[str, Any]:
    """Pin Node 24 actions and preserve CI and release event routing."""

    try:
        self_tests = SELF_TESTS_WORKFLOW.read_text(encoding="utf-8")
        release = RELEASE_WORKFLOW.read_text(encoding="utf-8")
        failures: list[str] = []

        expected_self_trigger = (
            "    branches:\n"
            '      - "**"\n'
            "  pull_request:\n"
            "  workflow_dispatch:\n"
        )
        if expected_self_trigger not in self_tests:
            failures.append("Self Tests is not restricted to branch pushes")
        if "    tags:\n" not in release or '      - "v*"\n' not in release:
            failures.append("Release Skill lost its release-tag trigger")
        expected_publication_job = (
            "  verify-publication:\n"
            "    name: Verify published release assets\n"
            "    if: github.event_name == 'workflow_dispatch'\n"
            "    needs:\n"
            "      - validate\n"
            "      - publish\n"
        )
        if expected_publication_job not in release:
            failures.append(
                "published-asset verification is not gated on tag validation "
                "and publication"
            )
        publication_marker = "  verify-publication:\n"
        publication_job = (
            release[release.index(publication_marker) :]
            if publication_marker in release
            else ""
        )
        required_publication_fragments = (
            "permissions:\n      contents: read",
            "ref: ${{ needs.validate.outputs.commit }}",
            "fetch-depth: 0",
            "fetch-tags: true",
            "name: Restore and prove published annotated tag",
            'gh release download "${RELEASE_TAG}"',
            '--repo "${GITHUB_REPOSITORY}"',
            '--pattern "skill-forge.zip"',
            '--pattern "skill-forge.zip.sha256"',
            "cmp --silent validated/skill-forge.zip published/skill-forge.zip",
            "validated/skill-forge.zip.sha256",
            "published/skill-forge.zip.sha256",
            "sha256sum --check --strict skill-forge.zip.sha256",
            "python -S scripts/package_skill.py verify",
            "published/skill-forge.zip",
            "--source-repo .",
        )
        missing_publication_fragments = [
            fragment
            for fragment in required_publication_fragments
            if fragment not in publication_job
        ]
        if missing_publication_fragments:
            failures.append(
                "published-asset verification lost required proof steps: "
                + ", ".join(missing_publication_fragments)
            )

        expected_self_actions = [
            "uses: actions/checkout@"
            "9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0 # v7.0.0",
            "uses: actions/checkout@"
            "9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0 # v7.0.0",
            "uses: actions/setup-python@"
            "ece7cb06caefa5fff74198d8649806c4678c61a1 # v6.3.0",
        ]
        expected_release_actions = [
            "uses: actions/checkout@9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0 # v7.0.0",
            "uses: actions/setup-python@ece7cb06caefa5fff74198d8649806c4678c61a1 # v6.3.0",
            "uses: actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a # v7.0.1",
            "uses: actions/checkout@9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0 # v7.0.0",
            "uses: actions/download-artifact@3e5f45b2cfb9172054b4087a40e8e0b5a5461e7c # v8.0.1",
            "uses: actions/checkout@9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0 # v7.0.0",
            "uses: actions/setup-python@ece7cb06caefa5fff74198d8649806c4678c61a1 # v6.3.0",
            "uses: actions/download-artifact@3e5f45b2cfb9172054b4087a40e8e0b5a5461e7c # v8.0.1",
        ]

        def action_lines(source: str) -> list[str]:
            return [
                line.strip()
                for line in source.splitlines()
                if line.strip().startswith("uses: actions/")
            ]

        actual_self_actions = action_lines(self_tests)
        actual_release_actions = action_lines(release)
        if actual_self_actions != expected_self_actions:
            failures.append(
                f"unexpected Self Tests action pins: {actual_self_actions!r}"
            )
        if actual_release_actions != expected_release_actions:
            failures.append(
                f"unexpected Release Skill action pins: {actual_release_actions!r}"
            )

        ok = not failures
        reason = "; ".join(failures)
    except Exception as exc:
        ok = False
        reason = f"workflow configuration check raised {type(exc).__name__}: {exc}"
    return {
        "name": "CI workflows pin Node 24 actions and preserve release routing",
        "fixture": str(SELF_TESTS_WORKFLOW),
        "expected_exit": 0,
        "actual_exit": 0 if ok else 1,
        "expected_code": "workflow trigger and immutable action pins",
        "result": "PASS" if ok else "FAIL",
        "reason": reason,
    }


def run_eval_harness_case() -> dict[str, Any]:
    """Exercise bounded fixtures and fail-closed measurement without model calls."""
    proc = subprocess.run([sys.executable, "-S", str(SCRIPT_DIR.parent / "evals/test_harness.py")],
                          capture_output=True, text=True, timeout=60, check=False)
    return dict(name="synthetic agent evaluation harness", fixture="evals/test_harness.py",
                expected_exit=0, actual_exit=proc.returncode, expected_code="trace and safety integrity",
                result="PASS" if proc.returncode == 0 else "FAIL",
                reason="" if proc.returncode == 0 else proc.stderr[-3000:])


def run_bounded_runner_case() -> dict[str, Any]:
    proc = subprocess.run([sys.executable, "-B", "-S", str(SCRIPT_DIR.parent / "evals/test_bounded_runner.py")],
                          capture_output=True, text=True, timeout=60, check=False)
    return dict(name="bounded execution controller", fixture="evals/test_bounded_runner.py",
                expected_exit=0, actual_exit=proc.returncode, expected_code="fail-closed controller boundaries",
                result="PASS" if proc.returncode == 0 else "FAIL",
                reason="" if proc.returncode == 0 else proc.stderr[-3000:])


def run_new_source_case(filename: str) -> dict[str, Any]:
    proc = subprocess.run([sys.executable, "-B", "-S", str(SCRIPT_DIR.parent / "evals" / filename)],
                          capture_output=True, text=True, encoding="utf-8", timeout=90, check=False)
    return dict(name=filename, fixture="evals/" + filename, expected_exit=0,
                actual_exit=proc.returncode, expected_code="behavioral source regression",
                result="PASS" if proc.returncode == 0 else "FAIL",
                reason="" if proc.returncode == 0 else (proc.stdout + proc.stderr)[-3000:])


def render_results(results: list[dict[str, Any]]) -> int:
    headers = ["Test", "Expected", "Actual", "Finding", "Result", "Reason"]
    rows = [
        [
            item["name"],
            str(item["expected_exit"]),
            str(item["actual_exit"]),
            item["expected_code"],
            item["result"],
            item["reason"],
        ]
        for item in results
    ]
    widths = [len(header) for header in headers]
    for row in rows:
        for index, cell in enumerate(row):
            widths[index] = max(widths[index], len(cell))

    def line(values: list[str]) -> str:
        return " | ".join(
            value.ljust(widths[index]) for index, value in enumerate(values)
        )

    print(line(headers))
    print("-+-".join("-" * width for width in widths))
    for row in rows:
        print(line(row))
    passed = sum(item["result"] == "PASS" for item in results)
    print(f"\nSource-test summary: {passed}/{len(results)} passed")
    return 0 if passed == len(results) else 1


def main() -> int:
    missing = [
        str(path)
        for path in (
            RELEASE_TOOL,
            RELEASE_NOTES,
            RELEASE_METADATA,
            INDEPENDENT_EVALUATOR,
            RUNTIME_TESTS,
            RUNTIME_MANIFEST,
            PACKAGE_TOOL,
            CONTRACT_VALIDATOR,
            SELF_TESTS_WORKFLOW,
            RELEASE_WORKFLOW,
        )
        if not path.is_file()
    ]
    if missing:
        print(
            "source-test runner requires a complete source checkout; missing: "
            + ", ".join(missing),
            file=sys.stderr,
        )
        return 1

    cases = (
        ("release metadata tool contract", run_release_metadata_tool_case),
        ("temporary release-notes repository tests", run_release_notes_temp_repo_case),
        ("strict release-tag and committed-changelog tests", run_release_tag_verification_case),
        ("independent evaluator scratch-boundary tests", run_independent_evaluator_case),
        ("runtime/source test boundary", run_runtime_surface_split_case),
        ("cross-platform contract path identity", run_cross_platform_contract_path_case),
        ("CI workflow configuration", run_workflow_configuration_case),
        ("synthetic agent evaluation harness", run_eval_harness_case),
        ("bounded execution controller", run_bounded_runner_case),
        ("transactional installation", lambda: run_new_source_case("test_install_skill.py")),
        ("measured-quality evaluation", lambda: run_new_source_case("test_measured_quality.py")),
        ("release evidence receipt", lambda: run_new_source_case("test_release_receipt.py")),
    )
    results = []
    for label, case in cases:
        print(f"Running {label}...", file=sys.stderr, flush=True)
        results.append(case())
    return render_results(results)


if __name__ == "__main__":
    raise SystemExit(main())
