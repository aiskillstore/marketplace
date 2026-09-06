#!/usr/bin/env python3
"""Build and verify Skill Forge runtime manifests from committed Git blobs.

The embedded manifest proves that a canonical runtime ZIP is internally
consistent. ``verify_source_proof`` is deliberately separate: archive
integrity alone does not prove that the bytes came from the declared Git
revision.
"""

from __future__ import annotations

import hashlib
import json
import os
import stat
import subprocess
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from portable_zip_paths import validate_portable_zip_members


REPO_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_NAME = "skill-forge"
PACKAGE_ROOT = "skill-forge"
SCHEMA_ID = "skill-forge.runtime-manifest.v1"
CANONICAL_ZIP_POLICY = "skill-forge.zip.v1"
HASH_ALGORITHM = "sha256"
MANIFEST_PATH = "runtime-manifest.json"
MANIFEST_SELF_HASH_POLICY = "excluded"
SELECTION_POLICY = "skill-forge.runtime-paths.v1"
SKILL_FORGE_RUNTIME_STATIC_SELECTORS = (
    "SKILL.md",
    "README.md",
    "LICENSE",
    "agents",
    "references",
)
SKILL_FORGE_RUNTIME_SCRIPT_PATHS = (
    "scripts/inspect_skill_package.py",
    "scripts/package_skill.py",
    "scripts/portable_zip_paths.py",
    "scripts/run_self_tests.py",
    "scripts/run_bounded_tests.py",
    "scripts/score_audit.py",
    "scripts/runtime_manifest.py",
    "scripts/validate_audit_contract.py",
)
# Repository-maintenance helpers are intentionally excluded from the runtime
# ZIP. Keep this list authoritative; the source contract checks the matching
# SKILL.md declaration and package verifier boundary.
SKILL_FORGE_SOURCE_ONLY_SCRIPTS = (
    "scripts/generate_release_notes.py",
    "scripts/release_metadata.py",
    "scripts/release_skill.py",
    "scripts/run_source_tests.py",
    "scripts/verify_independent_evaluator.py",
    "scripts/install_skill.py",
    "scripts/verify_release_receipt.py",
)
SKILL_FORGE_RUNTIME_SELECTORS = (
    *SKILL_FORGE_RUNTIME_STATIC_SELECTORS,
    *SKILL_FORGE_RUNTIME_SCRIPT_PATHS,
)
CANONICAL_ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)
CANONICAL_ZIP_COMPRESSION = zipfile.ZIP_STORED
MAX_MANIFEST_BYTES = 1_000_000
MAX_RUNTIME_FILES = 5000
MAX_RUNTIME_FILE_BYTES = 25 * 1024 * 1024
MAX_RUNTIME_TOTAL_BYTES = 100 * 1024 * 1024
MAX_CANONICAL_ARCHIVE_BYTES = 110 * 1024 * 1024
MAX_GIT_TREE_OUTPUT_BYTES = 2 * 1024 * 1024
GIT_TIMEOUT_SECONDS = 30

TOP_LEVEL_KEYS = {
    "schema",
    "package",
    "source",
    "selection",
    "canonical_zip",
    "hash_algorithm",
    "manifest",
    "files",
}
PACKAGE_KEYS = {"name", "root"}
SOURCE_KEYS = {"object_format", "commit", "tree"}
SELECTION_KEYS = {"policy", "selectors"}
MANIFEST_KEYS = {"path", "self_hash_policy"}
FILE_KEYS = {"path", "size", "sha256", "git_mode"}
REGULAR_GIT_MODES = {"100644", "100755"}


class RuntimeManifestError(RuntimeError):
    """Raised when manifest construction or verification cannot continue."""


class GitEvidenceUnavailableError(RuntimeManifestError):
    """Raised when trusted Git evidence cannot currently be obtained."""


def _boundary_set_issues(label: str, actual: set[str], expected: set[str]) -> List[str]:
    """Describe deterministic missing/extra path drift for one boundary view."""
    issues: List[str] = []
    missing = sorted(expected - actual)
    unexpected = sorted(actual - expected)
    if missing:
        issues.append(f"{label} missing canonical paths: {', '.join(missing)}")
    if unexpected:
        issues.append(f"{label} has non-canonical paths: {', '.join(unexpected)}")
    return issues


def runtime_boundary_issues(
    runtime_selectors: Iterable[str] = SKILL_FORGE_RUNTIME_SELECTORS,
    forbidden_runtime_paths: Iterable[str] = SKILL_FORGE_SOURCE_ONLY_SCRIPTS,
    declared_source_only_paths: Iterable[str] = SKILL_FORGE_SOURCE_ONLY_SCRIPTS,
) -> List[str]:
    """Return source/runtime boundary drift without mutating package state.

    ``SKILL_FORGE_RUNTIME_SCRIPT_PATHS`` and
    ``SKILL_FORGE_SOURCE_ONLY_SCRIPTS`` are the authoritative classifications.
    Callers supply the manifest selectors, package exclusions, and SKILL.md
    declaration so this function can detect missing, extra, and misclassified
    paths across the three independent representations.
    """
    selectors = set(runtime_selectors)
    runtime_scripts = {path for path in selectors if path.startswith("scripts/")}
    forbidden = set(forbidden_runtime_paths)
    declared = set(declared_source_only_paths)
    expected_runtime = set(SKILL_FORGE_RUNTIME_SCRIPT_PATHS)
    expected_source_only = set(SKILL_FORGE_SOURCE_ONLY_SCRIPTS)
    issues = _boundary_set_issues("runtime selectors", runtime_scripts, expected_runtime)
    issues.extend(
        _boundary_set_issues(
            "package forbidden runtime paths", forbidden, expected_source_only
        )
    )
    issues.extend(
        _boundary_set_issues(
            "SKILL.md source-only declaration", declared, expected_source_only
        )
    )
    selected_source_only = sorted(runtime_scripts & expected_source_only)
    if selected_source_only:
        issues.append(
            "runtime selectors include source-only paths: "
            + ", ".join(selected_source_only)
        )
    forbidden_runtime = sorted(forbidden & expected_runtime)
    if forbidden_runtime:
        issues.append(
            "package forbidden runtime paths misclassify runtime paths: "
            + ", ".join(forbidden_runtime)
        )
    declared_runtime = sorted(declared & expected_runtime)
    if declared_runtime:
        issues.append(
            "SKILL.md source-only declaration misclassifies runtime paths: "
            + ", ".join(declared_runtime)
        )
    return issues


@dataclass(frozen=True)
class SourceIdentity:
    """Resolved identity for one committed Git tree."""

    object_format: str
    commit: str
    tree: str


SYNTHETIC_SOURCE = SourceIdentity(
    object_format="sha1",
    commit="0" * 40,
    tree="0" * 40,
)


@dataclass(frozen=True)
class CommittedFile:
    """One regular file read directly from a Git blob."""

    path: str
    data: bytes
    git_mode: str


@dataclass(frozen=True)
class RuntimeManifestBuild:
    """Canonical manifest plus the committed bytes it describes."""

    source: SourceIdentity
    files: Tuple[CommittedFile, ...]
    manifest: Dict[str, Any]
    manifest_bytes: bytes

    def file_bytes(self) -> Dict[str, bytes]:
        """Return runtime paths mapped to their committed blob bytes."""

        return {item.path: item.data for item in self.files}


def _run_git(
    args: Sequence[str],
    repo_root: Path,
    *,
    text: bool = False,
    max_stdout_bytes: Optional[int] = None,
) -> subprocess.CompletedProcess[Any]:
    """Run a bounded read-only Git command and return captured output."""

    # Replacement refs are local, mutable aliases. Source proof must resolve
    # the repository's real object graph, never refs/replace overlays.
    command = ["git", "--no-replace-objects", *args]
    environment = os.environ.copy()
    unsafe_git_environment = {
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
    for key in list(environment):
        if key in unsafe_git_environment or key.startswith("GIT_CONFIG_"):
            environment.pop(key, None)
    environment["GIT_NO_REPLACE_OBJECTS"] = "1"
    environment["GIT_OPTIONAL_LOCKS"] = "0"
    stdout_file = tempfile.TemporaryFile() if max_stdout_bytes is not None else None
    try:
        proc = subprocess.run(
            command,
            cwd=repo_root,
            stdout=stdout_file if stdout_file is not None else subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=text,
            env=environment,
            check=False,
            timeout=GIT_TIMEOUT_SECONDS,
        )
    except FileNotFoundError as exc:
        if stdout_file is not None:
            stdout_file.close()
        if not Path(repo_root).is_dir():
            raise GitEvidenceUnavailableError(
                f"source repository is unavailable: {repo_root}"
            ) from exc
        raise GitEvidenceUnavailableError("git is not available on PATH") from exc
    except subprocess.TimeoutExpired as exc:
        if stdout_file is not None:
            stdout_file.close()
        raise GitEvidenceUnavailableError(
            f"git command timed out after {exc.timeout} seconds: {' '.join(command)}"
        ) from exc
    except OSError as exc:
        if stdout_file is not None:
            stdout_file.close()
        raise GitEvidenceUnavailableError(f"could not launch Git command: {exc}") from exc
    finally:
        if stdout_file is not None and not stdout_file.closed:
            stdout_file.flush()
    if stdout_file is not None:
        stdout_size = stdout_file.tell()
        if stdout_size > int(max_stdout_bytes):
            stdout_file.close()
            raise RuntimeManifestError("git command output exceeded its bounded capture limit")
        stdout_file.seek(0)
        stdout_bytes = stdout_file.read()
        stdout_file.close()
        proc = subprocess.CompletedProcess(
            proc.args,
            proc.returncode,
            stdout_bytes.decode("utf-8", errors="strict") if text else stdout_bytes,
            proc.stderr,
        )
    if proc.returncode != 0:
        stderr = proc.stderr if text else proc.stderr.decode("utf-8", errors="replace")
        detail = stderr.strip()
        raise GitEvidenceUnavailableError(
            f"git command failed ({proc.returncode}): {' '.join(command)}: {detail}"
        )
    return proc


def _validate_revision(revision: str) -> None:
    if not isinstance(revision, str) or not revision or revision.startswith("-"):
        raise RuntimeManifestError("revision must be a non-empty, non-option Git revision")
    if "\x00" in revision or "\n" in revision or "\r" in revision:
        raise RuntimeManifestError("revision contains a forbidden control character")


def _object_format(repo_root: Path) -> str:
    proc = _run_git(["rev-parse", "--show-object-format=storage"], repo_root, text=True)
    object_format = proc.stdout.strip()
    if object_format not in {"sha1", "sha256"}:
        raise RuntimeManifestError(f"unsupported Git object format: {object_format!r}")
    return object_format


def resolve_source_identity(
    revision: str = "HEAD",
    repo_root: Path = REPO_ROOT,
) -> SourceIdentity:
    """Resolve ``revision`` once to an immutable commit and tree identity."""

    _validate_revision(revision)
    root = Path(repo_root).resolve()
    commit_proc = _run_git(
        ["rev-parse", "--verify", "--end-of-options", f"{revision}^{{commit}}"],
        root,
        text=True,
    )
    commit = commit_proc.stdout.strip()
    tree_proc = _run_git(
        ["rev-parse", "--verify", "--end-of-options", f"{commit}^{{tree}}"],
        root,
        text=True,
    )
    return SourceIdentity(
        object_format=_object_format(root),
        commit=commit,
        tree=tree_proc.stdout.strip(),
    )


def _validate_runtime_path(path: str) -> None:
    if not isinstance(path, str) or not path:
        raise RuntimeManifestError("runtime paths must be non-empty strings")
    if "\x00" in path or "\\" in path or path.startswith("/") or path.endswith("/"):
        raise RuntimeManifestError(f"runtime path is not canonical POSIX-relative: {path!r}")
    parts = path.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise RuntimeManifestError(f"runtime path is not canonical POSIX-relative: {path!r}")
    try:
        path.encode("utf-8", errors="strict")
    except UnicodeEncodeError as exc:
        raise RuntimeManifestError(f"runtime path is not valid UTF-8 text: {path!r}") from exc


def _validate_runtime_selectors(runtime_paths: Iterable[str]) -> Tuple[str, ...]:
    materialized = tuple(runtime_paths)
    if not materialized:
        raise RuntimeManifestError("at least one runtime path must be selected")
    seen = set()
    for path in materialized:
        _validate_runtime_path(path)
        if path == MANIFEST_PATH:
            raise RuntimeManifestError(
                f"{MANIFEST_PATH} is generated and must not be selected from Git"
            )
        if path in seen:
            raise RuntimeManifestError(f"duplicate runtime selector: {path}")
        seen.add(path)
    return materialized


def _git_blob(repo_root: Path, object_id: str) -> bytes:
    size_proc = _run_git(["cat-file", "-s", object_id], repo_root, text=True)
    try:
        size = int(size_proc.stdout.strip())
    except ValueError as exc:
        raise RuntimeManifestError("git cat-file returned an invalid blob size") from exc
    if size > MAX_RUNTIME_FILE_BYTES:
        raise RuntimeManifestError("runtime Git blob exceeds file limit")
    proc = _run_git(["cat-file", "blob", object_id], repo_root)
    if len(proc.stdout) != size:
        raise RuntimeManifestError("git blob size changed during bounded collection")
    return proc.stdout


def collect_committed_files(
    revision: str,
    runtime_paths: Iterable[str],
    repo_root: Path = REPO_ROOT,
) -> Tuple[SourceIdentity, Tuple[CommittedFile, ...]]:
    """Read selected regular files from committed Git blobs.

    Selectors may name files or directories. Every selector must match at
    least one committed regular file; symlinks, submodules, and other Git
    object types fail closed.
    """

    selectors = _validate_runtime_selectors(runtime_paths)
    root = Path(repo_root).resolve()
    source = resolve_source_identity(revision, root)
    literal_pathspecs = [f":(literal){path}" for path in selectors]
    proc = _run_git(
        [
            "ls-tree",
            "-r",
            "-z",
            "--full-tree",
            source.commit,
            "--",
            *literal_pathspecs,
        ],
        root,
        max_stdout_bytes=MAX_GIT_TREE_OUTPUT_BYTES,
    )

    matched = {selector: False for selector in selectors}
    committed_files: List[CommittedFile] = []
    seen_paths = set()
    total_bytes = 0
    for raw_entry in proc.stdout.split(b"\x00"):
        if not raw_entry:
            continue
        try:
            raw_metadata, raw_path = raw_entry.split(b"\t", 1)
            raw_mode, raw_type, raw_object_id = raw_metadata.split(b" ", 2)
            path = raw_path.decode("utf-8", errors="strict")
            mode = raw_mode.decode("ascii", errors="strict")
            object_type = raw_type.decode("ascii", errors="strict")
            object_id = raw_object_id.decode("ascii", errors="strict")
        except (UnicodeDecodeError, ValueError) as exc:
            raise RuntimeManifestError("git ls-tree returned an unsupported entry") from exc

        _validate_runtime_path(path)
        if path == MANIFEST_PATH:
            raise RuntimeManifestError(
                f"committed runtime selection unexpectedly includes {MANIFEST_PATH}"
            )
        if object_type != "blob" or mode not in REGULAR_GIT_MODES:
            raise RuntimeManifestError(
                f"runtime path is not a regular Git file: {path} ({mode} {object_type})"
            )
        if path in seen_paths:
            raise RuntimeManifestError(f"Git returned duplicate runtime path: {path}")
        seen_paths.add(path)
        for selector in selectors:
            if path == selector or path.startswith(f"{selector}/"):
                matched[selector] = True
        data = _git_blob(root, object_id)
        if len(data) > MAX_RUNTIME_FILE_BYTES:
            raise RuntimeManifestError(f"runtime Git blob exceeds file limit: {path}")
        total_bytes += len(data)
        if total_bytes > MAX_RUNTIME_TOTAL_BYTES:
            raise RuntimeManifestError("selected runtime Git blobs exceed total-byte limit")
        committed_files.append(CommittedFile(path=path, data=data, git_mode=mode))
        if len(committed_files) > MAX_RUNTIME_FILES:
            raise RuntimeManifestError("selected runtime tree exceeds file-count limit")

    missing = [selector for selector, was_matched in matched.items() if not was_matched]
    if missing:
        raise RuntimeManifestError(
            f"runtime selectors did not match committed regular files: {', '.join(missing)}"
        )
    committed_files.sort(key=lambda item: item.path.encode("utf-8"))
    return source, tuple(committed_files)


def _file_record(item: CommittedFile) -> Dict[str, Any]:
    return {
        "path": item.path,
        "size": len(item.data),
        "sha256": hashlib.sha256(item.data).hexdigest(),
        "git_mode": item.git_mode,
    }


def create_manifest(
    source: SourceIdentity,
    files: Iterable[CommittedFile],
    selectors: Iterable[str] = SKILL_FORGE_RUNTIME_SELECTORS,
) -> Dict[str, Any]:
    """Create the v1 manifest object for already-materialized Git blobs."""

    materialized = tuple(files)
    materialized_selectors = _validate_runtime_selectors(selectors)
    records = [_file_record(item) for item in materialized]
    records.sort(key=lambda item: item["path"].encode("utf-8"))
    manifest: Dict[str, Any] = {
        "schema": SCHEMA_ID,
        "package": {"name": PACKAGE_NAME, "root": PACKAGE_ROOT},
        "source": {
            "object_format": source.object_format,
            "commit": source.commit,
            "tree": source.tree,
        },
        "selection": {
            "policy": SELECTION_POLICY,
            "selectors": list(materialized_selectors),
        },
        "canonical_zip": CANONICAL_ZIP_POLICY,
        "hash_algorithm": HASH_ALGORITHM,
        "manifest": {
            "path": MANIFEST_PATH,
            "self_hash_policy": MANIFEST_SELF_HASH_POLICY,
        },
        "files": records,
    }
    errors = validate_manifest(manifest)
    if errors:
        raise RuntimeManifestError("invalid generated runtime manifest: " + "; ".join(errors))
    return manifest


def canonical_json_bytes(manifest: Mapping[str, Any]) -> bytes:
    """Return canonical UTF-8 JSON: sorted keys, compact separators, no newline."""

    try:
        rendered = json.dumps(
            manifest,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    except (TypeError, ValueError) as exc:
        raise RuntimeManifestError(f"manifest cannot be encoded as canonical JSON: {exc}") from exc
    return rendered.encode("utf-8")


def build_runtime_manifest(
    revision: str,
    runtime_paths: Iterable[str],
    repo_root: Path = REPO_ROOT,
) -> RuntimeManifestBuild:
    """Build a canonical manifest from one resolved committed revision."""

    selectors = tuple(runtime_paths)
    source, files = collect_committed_files(revision, selectors, repo_root)
    manifest = create_manifest(source, files, selectors)
    return RuntimeManifestBuild(
        source=source,
        files=files,
        manifest=manifest,
        manifest_bytes=canonical_json_bytes(manifest),
    )


def build_synthetic_manifest(
    file_bytes: Mapping[str, bytes],
    git_modes: Optional[Mapping[str, str]] = None,
    source: SourceIdentity = SYNTHETIC_SOURCE,
    selectors: Iterable[str] = SKILL_FORGE_RUNTIME_SELECTORS,
) -> RuntimeManifestBuild:
    """Build a valid manifest without Git for focused archive self-tests."""

    if not isinstance(file_bytes, Mapping) or not file_bytes:
        raise RuntimeManifestError("synthetic file_bytes must be a non-empty mapping")
    modes = git_modes or {}
    unknown_modes = sorted(set(modes) - set(file_bytes))
    if unknown_modes:
        raise RuntimeManifestError(
            f"synthetic git modes name unknown paths: {', '.join(unknown_modes)}"
        )
    files: List[CommittedFile] = []
    for path, data in file_bytes.items():
        _validate_runtime_path(path)
        if path == MANIFEST_PATH:
            raise RuntimeManifestError(
                f"synthetic files must exclude generated {MANIFEST_PATH}"
            )
        if not isinstance(data, bytes):
            raise RuntimeManifestError(f"synthetic file data must be bytes: {path}")
        git_mode = modes.get(path, "100644")
        if git_mode not in REGULAR_GIT_MODES:
            raise RuntimeManifestError(f"unsupported synthetic Git mode for {path}: {git_mode}")
        files.append(CommittedFile(path=path, data=data, git_mode=git_mode))
    files.sort(key=lambda item: item.path.encode("utf-8"))
    materialized = tuple(files)
    manifest = create_manifest(source, materialized, selectors)
    return RuntimeManifestBuild(
        source=source,
        files=materialized,
        manifest=manifest,
        manifest_bytes=canonical_json_bytes(manifest),
    )


def _exact_keys(value: Any, expected: set[str], label: str, errors: List[str]) -> bool:
    if not isinstance(value, dict):
        errors.append(f"{label} must be an object")
        return False
    actual = set(value)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        if missing:
            errors.append(f"{label} is missing keys: {', '.join(missing)}")
        if extra:
            errors.append(f"{label} has unknown keys: {', '.join(extra)}")
        return False
    return True


def _valid_hex_digest(value: Any, length: int) -> bool:
    return (
        isinstance(value, str)
        and len(value) == length
        and all(character in "0123456789abcdef" for character in value)
    )


def validate_manifest(manifest: Any) -> List[str]:
    """Validate exact v1 schema, constants, records, ordering, and uniqueness."""

    errors: List[str] = []
    if not _exact_keys(manifest, TOP_LEVEL_KEYS, "manifest", errors):
        if not isinstance(manifest, dict):
            return errors

    if manifest.get("schema") != SCHEMA_ID:
        errors.append(f"schema must equal {SCHEMA_ID!r}")
    if manifest.get("canonical_zip") != CANONICAL_ZIP_POLICY:
        errors.append(f"canonical_zip must equal {CANONICAL_ZIP_POLICY!r}")
    if manifest.get("hash_algorithm") != HASH_ALGORITHM:
        errors.append(f"hash_algorithm must equal {HASH_ALGORITHM!r}")

    package = manifest.get("package")
    if _exact_keys(package, PACKAGE_KEYS, "package", errors):
        if package.get("name") != PACKAGE_NAME:
            errors.append(f"package.name must equal {PACKAGE_NAME!r}")
        if package.get("root") != PACKAGE_ROOT:
            errors.append(f"package.root must equal {PACKAGE_ROOT!r}")

    source = manifest.get("source")
    if _exact_keys(source, SOURCE_KEYS, "source", errors):
        object_format = source.get("object_format")
        if object_format not in {"sha1", "sha256"}:
            errors.append("source.object_format must be 'sha1' or 'sha256'")
        else:
            digest_length = 40 if object_format == "sha1" else 64
            if not _valid_hex_digest(source.get("commit"), digest_length):
                errors.append("source.commit is not a canonical object ID")
            if not _valid_hex_digest(source.get("tree"), digest_length):
                errors.append("source.tree is not a canonical object ID")

    selection = manifest.get("selection")
    if _exact_keys(selection, SELECTION_KEYS, "selection", errors):
        if selection.get("policy") != SELECTION_POLICY:
            errors.append(f"selection.policy must equal {SELECTION_POLICY!r}")
        if selection.get("selectors") != list(SKILL_FORGE_RUNTIME_SELECTORS):
            errors.append("selection.selectors must match the authoritative Skill Forge runtime policy")

    manifest_metadata = manifest.get("manifest")
    if _exact_keys(manifest_metadata, MANIFEST_KEYS, "manifest metadata", errors):
        if manifest_metadata.get("path") != MANIFEST_PATH:
            errors.append(f"manifest.path must equal {MANIFEST_PATH!r}")
        if manifest_metadata.get("self_hash_policy") != MANIFEST_SELF_HASH_POLICY:
            errors.append(
                f"manifest.self_hash_policy must equal {MANIFEST_SELF_HASH_POLICY!r}"
            )

    records = manifest.get("files")
    if not isinstance(records, list):
        errors.append("files must be an array")
        return errors
    if not records:
        errors.append("files must contain at least one runtime file")
    if len(records) > MAX_RUNTIME_FILES:
        errors.append(f"files exceeds the runtime manifest limit of {MAX_RUNTIME_FILES}")
        return errors

    paths: List[str] = []
    total_size = 0
    for index, record in enumerate(records):
        label = f"files[{index}]"
        if not _exact_keys(record, FILE_KEYS, label, errors):
            continue
        path = record.get("path")
        try:
            _validate_runtime_path(path)
        except RuntimeManifestError as exc:
            errors.append(f"{label}.path is invalid: {exc}")
        else:
            if path == MANIFEST_PATH:
                errors.append(f"{label}.path must exclude the generated manifest itself")
            paths.append(path)
        size = record.get("size")
        if isinstance(size, bool) or not isinstance(size, int) or size < 0:
            errors.append(f"{label}.size must be a non-negative integer")
        else:
            total_size += size
            if size > MAX_RUNTIME_FILE_BYTES:
                errors.append(f"{label}.size exceeds the runtime file limit")
        if not _valid_hex_digest(record.get("sha256"), 64):
            errors.append(f"{label}.sha256 is not a canonical SHA-256 digest")
        if record.get("git_mode") not in REGULAR_GIT_MODES:
            errors.append(f"{label}.git_mode must be 100644 or 100755")

    if len(paths) != len(set(paths)):
        errors.append("files contains duplicate paths")
    if paths != sorted(paths, key=lambda item: item.encode("utf-8")):
        errors.append("files must be sorted by UTF-8 path bytes")
    if total_size > MAX_RUNTIME_TOTAL_BYTES:
        errors.append("files exceed the runtime manifest total-byte limit")
    _portable_records, path_issues = validate_portable_zip_members(
        (f"{PACKAGE_ROOT}/{path}", False) for path in paths
    )
    for issue in path_issues:
        errors.append(f"files path is not portable: {issue.code}: {issue.raw_name}")
    for selector in SKILL_FORGE_RUNTIME_SELECTORS:
        if not any(path == selector or path.startswith(f"{selector}/") for path in paths):
            errors.append(f"files do not cover authoritative runtime selector: {selector}")
    for path in paths:
        if not any(
            path == selector or path.startswith(f"{selector}/")
            for selector in SKILL_FORGE_RUNTIME_SELECTORS
        ):
            errors.append(f"files path is outside authoritative runtime selectors: {path}")
    return errors


class _DuplicateJSONKey(ValueError):
    pass


def _reject_duplicate_keys(pairs: List[Tuple[str, Any]]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateJSONKey(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _load_manifest_bytes(raw: bytes) -> Dict[str, Any]:
    try:
        text = raw.decode("utf-8", errors="strict")
        parsed = json.loads(text, object_pairs_hook=_reject_duplicate_keys)
    except (UnicodeDecodeError, json.JSONDecodeError, _DuplicateJSONKey) as exc:
        raise RuntimeManifestError(f"runtime manifest is not canonical JSON: {exc}") from exc
    if not isinstance(parsed, dict):
        raise RuntimeManifestError("runtime manifest root must be an object")
    return parsed


def _expected_unix_mode(git_mode: str) -> int:
    return 0o755 if git_mode == "100755" else 0o644


def _expected_flag_bits(filename: str) -> int:
    try:
        filename.encode("ascii")
    except UnicodeEncodeError:
        return 0x800
    return 0


def canonical_zip_info(member_name: str, git_mode: str) -> zipfile.ZipInfo:
    """Create the exact ZIP metadata required by canonical policy v1."""

    if not isinstance(member_name, str) or not member_name:
        raise RuntimeManifestError("canonical ZIP member name must be non-empty")
    if git_mode not in REGULAR_GIT_MODES:
        raise RuntimeManifestError(f"unsupported canonical ZIP Git mode: {git_mode}")
    info = zipfile.ZipInfo(member_name, CANONICAL_ZIP_TIMESTAMP)
    info.compress_type = CANONICAL_ZIP_COMPRESSION
    info.create_system = 3
    info.create_version = 20
    info.extract_version = 20
    info.flag_bits = _expected_flag_bits(member_name)
    info.internal_attr = 0
    info.volume = 0
    info.external_attr = (stat.S_IFREG | _expected_unix_mode(git_mode)) << 16
    info.extra = b""
    info.comment = b""
    return info


def canonical_zip_member_names(manifest: Mapping[str, Any]) -> Tuple[str, ...]:
    """Return the only valid member sequence for canonical ZIP policy v1."""

    errors = validate_manifest(manifest)
    if errors:
        raise RuntimeManifestError(
            "cannot derive ZIP member order from an invalid manifest: " + "; ".join(errors)
        )
    names = [
        f"{PACKAGE_ROOT}/{MANIFEST_PATH}",
        *(f"{PACKAGE_ROOT}/{record['path']}" for record in manifest["files"]),
    ]
    names.sort(key=lambda item: item.encode("utf-8"))
    return tuple(names)


def _write_canonical_payload_archive(
    output: Path,
    manifest: Mapping[str, Any],
    manifest_bytes: bytes,
    payloads: Mapping[str, Tuple[bytes, str]],
) -> None:
    """Write the exact v1 ZIP byte layout for already-validated payloads."""

    output_path = Path(output)
    member_names = canonical_zip_member_names(manifest)
    expected_payload_names = set(member_names) - {f"{PACKAGE_ROOT}/{MANIFEST_PATH}"}
    if set(payloads) != expected_payload_names:
        raise RuntimeManifestError("canonical ZIP payload set does not match manifest members")
    with zipfile.ZipFile(output_path, "w", allowZip64=True) as archive:
        for member_name in member_names:
            if member_name == f"{PACKAGE_ROOT}/{MANIFEST_PATH}":
                data = manifest_bytes
                git_mode = "100644"
            else:
                data, git_mode = payloads[member_name]
            archive.writestr(canonical_zip_info(member_name, git_mode), data)
        archive.comment = b""


def write_canonical_archive(build: RuntimeManifestBuild, output: Path) -> None:
    """Write a deterministic v1 runtime ZIP from one manifest build."""

    manifest_errors = validate_manifest(build.manifest)
    if manifest_errors:
        raise RuntimeManifestError(
            "cannot write an invalid runtime manifest: " + "; ".join(manifest_errors)
        )
    if build.manifest_bytes != canonical_json_bytes(build.manifest):
        raise RuntimeManifestError("runtime manifest bytes are not canonical")
    records = {record["path"]: record for record in build.manifest["files"]}
    files = {item.path: item for item in build.files}
    if set(records) != set(files):
        raise RuntimeManifestError("runtime build files do not match manifest records")

    payloads: Dict[str, Tuple[bytes, str]] = {}
    for path, record in records.items():
        item = files[path]
        if item.git_mode != record["git_mode"]:
            raise RuntimeManifestError(f"runtime Git mode does not match manifest: {path}")
        if len(item.data) != record["size"]:
            raise RuntimeManifestError(f"runtime file size does not match manifest: {path}")
        if hashlib.sha256(item.data).hexdigest() != record["sha256"]:
            raise RuntimeManifestError(f"runtime file hash does not match manifest: {path}")
        payloads[f"{PACKAGE_ROOT}/{path}"] = (item.data, item.git_mode)
    _write_canonical_payload_archive(
        Path(output), build.manifest, build.manifest_bytes, payloads
    )


def _files_equal(left: Path, right: Path) -> bool:
    """Compare two regular files exactly without loading either whole file."""

    if left.stat().st_size != right.stat().st_size:
        return False
    with left.open("rb") as left_handle, right.open("rb") as right_handle:
        while True:
            left_chunk = left_handle.read(1024 * 1024)
            right_chunk = right_handle.read(1024 * 1024)
            if left_chunk != right_chunk:
                return False
            if not left_chunk:
                return True


def _zip_policy_errors(info: zipfile.ZipInfo, git_mode: str) -> List[str]:
    errors: List[str] = []
    if info.compress_type != CANONICAL_ZIP_COMPRESSION:
        errors.append(f"ZIP member is not stored without compression: {info.filename}")
    if info.date_time != CANONICAL_ZIP_TIMESTAMP:
        errors.append(f"ZIP member has a non-canonical timestamp: {info.filename}")
    if info.create_system != 3:
        errors.append(f"ZIP member does not declare Unix metadata: {info.filename}")
    if info.create_version != 20 or info.extract_version != 20:
        errors.append(f"ZIP member has non-canonical version metadata: {info.filename}")
    if (
        info.flag_bits != _expected_flag_bits(info.filename)
        or info.internal_attr != 0
        or info.volume != 0
    ):
        errors.append(f"ZIP member has non-canonical header flags: {info.filename}")
    expected_external_attr = (stat.S_IFREG | _expected_unix_mode(git_mode)) << 16
    if info.external_attr != expected_external_attr:
        errors.append(f"ZIP member has non-canonical external attributes: {info.filename}")
    if info.extra:
        errors.append(f"ZIP member has non-canonical extra fields: {info.filename}")
    if info.comment:
        errors.append(f"ZIP member has a non-canonical comment: {info.filename}")
    return errors


def _zip_framing_errors(archive_path: Path) -> List[str]:
    """Reject self-extracting prefixes and bytes outside the final EOCD."""
    errors: List[str] = []
    try:
        size = archive_path.stat().st_size
        if size < 22:
            return ["ZIP archive is too short to contain a canonical end record"]
        with archive_path.open("rb") as handle:
            first_signature = handle.read(4)
            tail_size = min(size, 65_557)
            handle.seek(size - tail_size)
            tail = handle.read(tail_size)
    except OSError as exc:
        return [f"could not inspect ZIP framing: {exc}"]
    if first_signature != b"PK\x03\x04":
        errors.append("ZIP archive has a non-canonical prefix before its first local header")
    end_index = tail.rfind(b"PK\x05\x06")
    if end_index < 0 or end_index + 22 > len(tail):
        errors.append("ZIP archive lacks a canonical end-of-central-directory record")
        return errors
    comment_length = int.from_bytes(tail[end_index + 20:end_index + 22], "little")
    absolute_end = size - tail_size + end_index + 22 + comment_length
    if comment_length != 0:
        errors.append("ZIP archive has a non-canonical end-record comment")
    if absolute_end != size:
        errors.append("ZIP archive has trailing bytes outside its final end record")
    return errors


def verify_zip_manifest(archive_path: Path) -> Dict[str, Any]:
    """Verify embedded-manifest integrity without claiming Git provenance."""

    report: Dict[str, Any] = {
        "status": "fail",
        "archive": str(archive_path),
        "manifest_path": f"{PACKAGE_ROOT}/{MANIFEST_PATH}",
        "member_count": 0,
        "manifest": None,
        "manifest_sha256": None,
        "archive_sha256": None,
        "errors": [],
    }
    errors: List[str] = report["errors"]
    archive = Path(archive_path)
    if not archive.is_file():
        errors.append("archive does not exist or is not a regular file")
        return report
    try:
        archive_size = archive.stat().st_size
    except OSError as exc:
        errors.append(f"could not stat archive: {exc}")
        return report
    if archive_size > MAX_CANONICAL_ARCHIVE_BYTES:
        errors.append("ZIP archive exceeds the canonical runtime byte limit")
        return report

    errors.extend(_zip_framing_errors(archive))
    if errors:
        return report

    try:
        with zipfile.ZipFile(archive, "r") as zip_file:
            infos = zip_file.infolist()
            report["member_count"] = len(infos)
            if len(infos) > MAX_RUNTIME_FILES + 1:
                errors.append("ZIP archive exceeds the canonical runtime member limit")
                return report
            if zip_file.comment:
                errors.append("ZIP archive has a non-canonical comment")
            names = [info.filename for info in infos]
            if len(names) != len(set(names)):
                errors.append("ZIP archive contains duplicate member names")

            manifest_member = report["manifest_path"]
            try:
                manifest_info = zip_file.getinfo(manifest_member)
            except KeyError:
                errors.append(f"ZIP archive is missing {manifest_member}")
                return report
            if manifest_info.is_dir() or manifest_info.file_size > MAX_MANIFEST_BYTES:
                errors.append("embedded runtime manifest is not a bounded regular file")
                return report
            # Enforce stored/canonical metadata before reading attacker-chosen
            # bytes so the manifest itself cannot be a decompression bomb.
            errors.extend(_zip_policy_errors(manifest_info, "100644"))
            if manifest_info.compress_size != manifest_info.file_size:
                errors.append("embedded runtime manifest has inconsistent stored size metadata")
            if errors:
                return report
            raw_manifest = zip_file.read(manifest_info)
            report["manifest_sha256"] = hashlib.sha256(raw_manifest).hexdigest()
            parsed = _load_manifest_bytes(raw_manifest)
            report["manifest"] = parsed
            errors.extend(validate_manifest(parsed))
            if raw_manifest != canonical_json_bytes(parsed):
                errors.append("embedded runtime manifest bytes are not canonical")
            if errors:
                return report

            expected_records = {record["path"]: record for record in parsed["files"]}
            canonical_names = canonical_zip_member_names(parsed)
            expected_names = set(canonical_names)
            actual_names = set(names)
            missing = sorted(expected_names - actual_names)
            extra = sorted(actual_names - expected_names)
            if missing:
                errors.append(f"ZIP archive is missing declared members: {', '.join(missing)}")
            if extra:
                errors.append(f"ZIP archive has undeclared members: {', '.join(extra)}")
            if names != list(canonical_names):
                errors.append("ZIP archive members are not in canonical UTF-8 byte order")
            if errors:
                return report

            # Validate every runtime member's bounded, stored metadata before
            # opening any runtime payload. This prevents a contradictory
            # compressed member from becoming a decompression-work gate.
            runtime_infos: Dict[str, zipfile.ZipInfo] = {}
            actual_runtime_bytes = 0
            for path, record in expected_records.items():
                member_name = f"{PACKAGE_ROOT}/{path}"
                info = zip_file.getinfo(member_name)
                runtime_infos[path] = info
                if info.file_size != record["size"]:
                    errors.append(f"ZIP member size does not match manifest: {member_name}")
                if info.compress_size != info.file_size:
                    errors.append(
                        f"ZIP member has inconsistent stored size metadata: {member_name}"
                    )
                errors.extend(_zip_policy_errors(info, record["git_mode"]))
                actual_runtime_bytes += info.file_size
            if actual_runtime_bytes > MAX_RUNTIME_TOTAL_BYTES:
                errors.append("ZIP runtime members exceed the total-byte limit")
            if errors:
                return report

            # Metadata now proves each read is bounded by the corresponding
            # manifest record. Retain the verified bytes for reconstruction.
            payloads: Dict[str, Tuple[bytes, str]] = {}
            for path, record in expected_records.items():
                member_name = f"{PACKAGE_ROOT}/{path}"
                data = zip_file.read(runtime_infos[path])
                if len(data) != record["size"]:
                    errors.append(f"ZIP member read size does not match manifest: {member_name}")
                    continue
                if hashlib.sha256(data).hexdigest() != record["sha256"]:
                    errors.append(f"ZIP member hash does not match manifest: {member_name}")
                    continue
                payloads[member_name] = (data, record["git_mode"])
            if errors:
                return report

            # Central-directory metadata alone cannot prove local headers or
            # byte layout. Rebuild with the canonical writer and compare the
            # entire artifact, catching hidden gaps and obsolete directories.
            canonical_path: Optional[Path] = None
            try:
                with tempfile.NamedTemporaryFile(
                    prefix="skill-forge-canonical-",
                    suffix=".zip",
                    delete=False,
                ) as canonical_handle:
                    canonical_path = Path(canonical_handle.name)
                _write_canonical_payload_archive(
                    canonical_path,
                    parsed,
                    raw_manifest,
                    payloads,
                )
                if not _files_equal(archive, canonical_path):
                    errors.append("ZIP archive bytes do not match canonical policy")
            finally:
                if canonical_path is not None:
                    try:
                        canonical_path.unlink(missing_ok=True)
                    except OSError:
                        pass
    except (OSError, EOFError, RuntimeError, ValueError, zipfile.BadZipFile) as exc:
        errors.append(f"ZIP manifest verification failed: {exc}")

    if not errors:
        digest = hashlib.sha256()
        try:
            with archive.open("rb") as handle:
                for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                    digest.update(chunk)
        except OSError as exc:
            errors.append(f"could not hash canonical archive: {exc}")
        else:
            report["archive_sha256"] = digest.hexdigest()
    report["status"] = "pass" if not errors else "fail"
    return report


def verify_source_proof(
    manifest: Mapping[str, Any],
    repo_root: Path = REPO_ROOT,
    revision: Optional[str] = None,
) -> Dict[str, Any]:
    """Prove manifest records against Git, separately from ZIP verification.

    When ``revision`` is provided it must resolve to the embedded commit. When
    omitted, the embedded commit itself is resolved in the local repository.
    """

    report: Dict[str, Any] = {
        "status": "fail",
        "revision": revision,
        "source": dict(manifest.get("source", {})) if isinstance(manifest, dict) else {},
        "manifest_sha256": None,
        "errors": [],
    }
    errors: List[str] = report["errors"]
    errors.extend(validate_manifest(manifest))
    if errors:
        return report
    report["manifest_sha256"] = hashlib.sha256(canonical_json_bytes(manifest)).hexdigest()

    embedded_source = manifest["source"]
    requested_revision = revision if revision is not None else embedded_source["commit"]
    report["revision"] = requested_revision
    try:
        resolved = resolve_source_identity(requested_revision, Path(repo_root))
    except GitEvidenceUnavailableError as exc:
        errors.append(str(exc))
        report["status"] = "not_assessed"
        return report
    except RuntimeManifestError as exc:
        errors.append(str(exc))
        return report

    if resolved.object_format != embedded_source["object_format"]:
        errors.append("Git object format does not match embedded source proof")
    if resolved.commit != embedded_source["commit"]:
        errors.append("resolved commit does not match embedded source proof")
    if resolved.tree != embedded_source["tree"]:
        errors.append("resolved tree does not match embedded source proof")
    if errors:
        return report

    try:
        selectors = manifest["selection"]["selectors"]
        collected_source, committed_files = collect_committed_files(
            resolved.commit,
            selectors,
            Path(repo_root),
        )
        rebuilt = create_manifest(collected_source, committed_files, selectors)
        if rebuilt != manifest:
            expected_records = {record["path"]: record for record in manifest["files"]}
            actual_records = {record["path"]: record for record in rebuilt["files"]}
            missing = sorted(set(expected_records) - set(actual_records))
            extra = sorted(set(actual_records) - set(expected_records))
            changed = sorted(
                path
                for path in set(expected_records) & set(actual_records)
                if expected_records[path] != actual_records[path]
            )
            if missing:
                errors.append(f"source proof is missing manifest paths: {', '.join(missing)}")
            if extra:
                errors.append(f"source proof has extra selected paths: {', '.join(extra)}")
            if changed:
                errors.append(f"source proof differs for manifest paths: {', '.join(changed)}")
            if not missing and not extra and not changed:
                errors.append("source proof metadata does not reproduce the embedded manifest")
    except GitEvidenceUnavailableError as exc:
        errors.append(str(exc))
        report["status"] = "not_assessed"
        return report
    except RuntimeManifestError as exc:
        errors.append(str(exc))
        # The requested commit and tree were resolved successfully. Failure to
        # reproduce the authoritative runtime selection is contradictory
        # source evidence, not an unavailable-evidence condition.
        report["status"] = "fail"
        return report

    report["status"] = "pass" if not errors else "fail"
    return report
