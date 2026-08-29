#!/usr/bin/env python3
"""Pure validator and deterministic reporter for Persona Evidence Registry v1."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
from typing import Any, Callable

SCRIPT = Path(__file__).resolve(strict=True)
RUNTIME = SCRIPT.parents[1]
CHECKOUT = SCRIPT.parents[4]
CHECKOUT_MODE = (CHECKOUT / ".codex-plugin" / "plugin.json").is_file()
REGISTRY = RUNTIME / "compat" / "personas"
SCHEMA = RUNTIME / "compat" / "persona-evidence.schema.json"
MANIFEST_SCHEMA = RUNTIME / "compat" / "persona-registry.schema.json"
BENCHMARKS = RUNTIME / "benchmarks" / "v1"
RECEIPT_SCHEMA = RUNTIME / "schemas" / "evidence-receipt.schema.json"
PLAN_SCHEMA = RUNTIME / "schemas" / "benchmark-plan.schema.json"
RESULT_SCHEMA = RUNTIME / "schemas" / "benchmark-result.schema.json"
GIT = "/usr/bin/git"

PERSONAS = ("bulk-test-writer", "diff-reviewer", "repo-inventory")
MODES = {
    "bulk-test-writer": ("plan", "accept-edits"),
    "diff-reviewer": ("plan",),
    "repo-inventory": ("plan",),
}
STATES = ("offline-only", "real-escalation-observed", "accepted-real-candidate")
MAX_FILE = 65536
MAX_OUTPUT = 16384
MAX_GIT_OUTPUT = 262144
GIT_TIMEOUT = 5.0
SHA_RE = re.compile(r"[0-9a-f]{64}\Z")
COMMIT_RE = re.compile(r"[0-9a-f]{40}\Z")
NAME_RE = re.compile(r"[a-z0-9](?:[a-z0-9-]{0,30}[a-z0-9])?\Z")
VERSION_RE = re.compile(r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\Z")

ACCEPTED_VERSION_FACTS = {
    "observed": "1.1.11",
    "call_count": 1,
    "binding_sha256": "72d0bba6040b46109f6968528697579dd1dbe7fdae949e68fb22e6f058452ea2",
    "profile_sha256": "3bb5de06e4c0b8d5f540dbc6382425fc752dbb5daf96a64cb6f9cd5a77a2c69a",
    "executable_sha256": "198ff7c3f6d173daa510b0814aa70c6ce14c94035bcd4707a3c0e79fa38a7bc3",
    "source_sha256": "198ff7c3f6d173daa510b0814aa70c6ce14c94035bcd4707a3c0e79fa38a7bc3",
    "snapshot_sha256": "198ff7c3f6d173daa510b0814aa70c6ce14c94035bcd4707a3c0e79fa38a7bc3",
    "runner_sha256": "e6bd55d2d0ab6c542745fd1bb1af4f6f4b7f163abb6f8c78597a24475d501d28",
    "stdout_sha256": "75fe54d226c17e2ffce72aca63fa1e5066db0d41560e8b6dd746b2361b82574e",
    "stderr_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
}
VERSION_LIMITATIONS = {
    "binary_provenance_proven": False,
    "private_evidence_public": False,
    "private_evidence_revalidated": False,
    "signed": False,
}

EVIDENCE_FILES = (
    "benchmark-plan.json",
    "benchmark-receipt.json",
    "benchmark-result.json",
    "candidate.diff",
    "dispatch-profile.json",
    "real-receipt.json",
    "run-evidence.json",
    "selection.json",
    "tool-attestation.json",
    "verifier-001.json",
    "version-attestation.json",
)
SCHEMA_FILES = {
    "manifest": "persona-run-manifest.schema.json",
    "dispatch": "persona-dispatch.schema.json",
    "tool": "persona-tool-attestation.schema.json",
    "version": "persona-version-attestation.schema.json",
    "verifier": "persona-verifier.schema.json",
    "run": "persona-run-evidence.schema.json",
    "approval": "persona-transition-approval.schema.json",
    "review": "persona-human-review.schema.json",
}


class RegistryError(Exception):
    pass


def fail(message: str) -> None:
    raise RegistryError(message)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii") + b"\n"


def exact_fields(value: dict[str, Any], expected: set[str], label: str) -> None:
    if set(value) != expected:
        fail(f"{label} fields are invalid")


def require_sha(value: Any, label: str) -> str:
    if not isinstance(value, str) or SHA_RE.fullmatch(value) is None:
        fail(f"{label} digest is invalid")
    return value


def read_public(path: Path, label: str, maximum: int = MAX_FILE, expected_mode: int = 0o644) -> bytes:
    try:
        if path.is_symlink():
            fail(f"{label} must not be a symlink")
        info = path.stat()
        if not stat.S_ISREG(info.st_mode) or stat.S_IMODE(info.st_mode) != expected_mode:
            fail(f"{label} mode is invalid")
        data = path.read_bytes()
    except OSError as exc:
        raise RegistryError(f"{label} is unavailable") from exc
    if len(data) > maximum:
        fail(f"{label} is oversized")
    return data


def strict_object(raw: bytes, label: str) -> dict[str, Any]:
    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            if key in result:
                fail(f"{label} has duplicate keys")
            result[key] = value
        return result

    try:
        value = json.loads(raw.decode("utf-8", "strict"), object_pairs_hook=pairs)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RegistryError(f"{label} is malformed") from exc
    if not isinstance(value, dict):
        fail(f"{label} must be one object")
    return value


def load_schema(path: Path) -> dict[str, Any]:
    value = strict_object(read_public(path, "registry schema"), "registry schema")
    if value.get("$schema") != "http://json-schema.org/draft-07/schema#":
        fail("registry schema dialect is invalid")
    return value


def schema_validate(value: Any, schema: dict[str, Any]) -> None:
    scripts = str(RUNTIME / "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    from evidence_receipt import ValidationFailure, validate_schema

    try:
        validate_schema(value, schema)
    except ValidationFailure as exc:
        raise RegistryError("registry schema validation failed") from exc


def parse_frontmatter(raw: bytes, expected_name: str) -> tuple[str, tuple[str, ...]]:
    try:
        text = raw.decode("utf-8", "strict")
    except UnicodeDecodeError as exc:
        raise RegistryError("persona source is not UTF-8") from exc
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        fail("persona frontmatter is missing")
    front, body = text[4:].split("\n---\n", 1)
    if not body.strip():
        fail("persona body is empty")
    scalars: dict[str, str] = {}
    lists: dict[str, list[str]] = {"tools": [], "agyWorkerModes": []}
    seen: set[str] = set()
    section = ""
    for line in front.splitlines():
        if not line or "\t" in line or line.rstrip() != line:
            fail("persona frontmatter formatting is invalid")
        if line.startswith("    - "):
            if section not in lists or not line[6:]:
                fail("persona frontmatter list is invalid")
            lists[section].append(line[6:])
            continue
        if line.startswith(" "):
            fail("persona frontmatter indentation is invalid")
        if ":" not in line:
            fail("persona frontmatter is malformed")
        key, value = line.split(":", 1)
        if key in seen:
            fail("persona frontmatter has duplicate keys")
        seen.add(key)
        if key in lists:
            if value:
                fail("persona frontmatter list header is invalid")
            section = key
        else:
            scalars[key] = value.strip()
            section = ""
    if seen != {"name", "description", "tools", "hidden", "inheritMcp", "agyWorkerModes"}:
        fail("persona frontmatter fields are invalid")
    description = scalars["description"]
    tools = lists["tools"]
    if not description or len(description.encode("utf-8")) > 512 or not tools or len(tools) != len(set(tools)):
        fail("persona frontmatter description or tools are invalid")
    if any(NAME_RE.fullmatch(tool.replace("_", "-")) is None for tool in tools):
        fail("persona frontmatter tool name is invalid")
    name = scalars["name"]
    modes = lists["agyWorkerModes"]
    if scalars["hidden"] != "true" or scalars["inheritMcp"] != "false":
        fail("persona frontmatter flags are invalid")
    if name != expected_name or tuple(modes) != MODES[expected_name]:
        fail("persona frontmatter name or mode restriction drifted")
    return name, tuple(modes)


def validate_dispatcher_contract(raw: bytes) -> None:
    """Bind registry modes to the exact shipped Bash dispatcher authority."""

    try:
        text = raw.decode("utf-8", "strict")
    except UnicodeDecodeError as exc:
        raise RegistryError("dispatcher is not UTF-8") from exc
    markers = (
        "case \"$persona\" in\n    ''|bulk-test-writer|repo-inventory|diff-reviewer) ;;",
        "if [[ \"$mode\" != \"plan\" && ( \"$persona\" == \"repo-inventory\" || \"$persona\" == \"diff-reviewer\" ) ]]; then",
        'persona_file="$SCRIPT_DIR/agents/$persona.md"',
        'persona_text="$(awk \'BEGIN{fm=0} /^---$/{fm++; next} fm>=2\' "$persona_file")\n"',
    )
    if any(text.count(marker) != 1 for marker in markers):
        fail("dispatcher persona authority drifted")


def evidence_paths() -> dict[str, Path]:
    return {
        "benchmark_manifest": BENCHMARKS / "manifest.json",
        "benchmark_variant": BENCHMARKS / "variants" / "bulk.json",
        "benchmark_plan_schema": RUNTIME / "schemas" / "benchmark-plan.schema.json",
        "benchmark_result_schema": RUNTIME / "schemas" / "benchmark-result.schema.json",
        "receipt_schema": RUNTIME / "schemas" / "evidence-receipt.schema.json",
        "qa_gate": RUNTIME / "qa-gate.sh",
        "verify_job": RUNTIME / "verify-job.sh",
        "dispatcher": RUNTIME / "agy-worker.sh",
    }


def expected_offline_evidence() -> dict[str, Any]:
    paths = evidence_paths()
    manifest_raw = read_public(paths["benchmark_manifest"], "benchmark manifest")
    manifest = strict_object(manifest_raw, "benchmark manifest")
    tasks = manifest.get("tasks")
    if not isinstance(tasks, list) or len(tasks) != 1 or not isinstance(tasks[0], dict):
        fail("benchmark manifest task contract drifted")
    task = tasks[0]
    variant_raw = read_public(paths["benchmark_variant"], "benchmark variant")
    variant = strict_object(variant_raw, "benchmark variant")
    selection = variant.get("selection")
    if not isinstance(selection, dict):
        fail("benchmark selection is missing")
    dispatcher_raw = read_public(paths["dispatcher"], "dispatcher", 262144, 0o755)
    validate_dispatcher_contract(dispatcher_raw)
    return {
        "kind": "p1-c-public-contract",
        "benchmark_manifest_path": "benchmarks/v1/manifest.json",
        "benchmark_manifest_sha256": digest(manifest_raw),
        "benchmark_variant_path": "benchmarks/v1/variants/bulk.json",
        "benchmark_variant_sha256": digest(variant_raw),
        "selection_sha256": digest(canonical_bytes(selection)),
        "task_id": task.get("id"),
        "initial_sha256": task.get("initial_sha256"),
        "candidate_sha256": task.get("candidate_sha256"),
        "envelope_sha256": task.get("envelope_sha256"),
        "plan_schema_sha256": digest(read_public(paths["benchmark_plan_schema"], "benchmark plan schema")),
        "result_schema_sha256": digest(read_public(paths["benchmark_result_schema"], "benchmark result schema")),
        "receipt_schema_sha256": digest(read_public(paths["receipt_schema"], "receipt schema")),
        "qa_gate_sha256": digest(read_public(paths["qa_gate"], "qa gate", 262144, 0o755)),
        "verify_job_sha256": digest(read_public(paths["verify_job"], "verify job", 262144, 0o755)),
        "dispatcher_sha256": digest(dispatcher_raw),
        "gate_authority": "qa-gate",
        "persona_executed": False,
        "live_execution": False,
    }


def require_commit(value: Any, label: str) -> str:
    if not isinstance(value, str) or COMMIT_RE.fullmatch(value) is None:
        fail(f"{label} commit is invalid")
    return value


def binding(value: Any, label: str) -> dict[str, str]:
    if not isinstance(value, dict):
        fail(f"{label} binding is missing")
    exact_fields(value, {"path", "sha256", "commit"}, f"{label} binding")
    path = value.get("path")
    if not isinstance(path, str) or path.startswith("/") or ".." in Path(path).parts or "\x00" in path:
        fail(f"{label} path is invalid")
    require_sha(value.get("sha256"), label)
    require_commit(value.get("commit"), label)
    return value


def artifact_binding(value: Any, label: str) -> dict[str, str]:
    if not isinstance(value, dict):
        fail(f"{label} artifact binding is missing")
    exact_fields(value, {"path", "sha256"}, f"{label} artifact binding")
    path = value.get("path")
    if not isinstance(path, str) or path.startswith("/") or ".." in Path(path).parts or "\x00" in path:
        fail(f"{label} artifact path is invalid")
    require_sha(value.get("sha256"), label)
    return value


def source_binding(value: Any, label: str, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        fail(f"{label} source binding is missing")
    exact_fields(value, {"path", "sha256", "commit", "mode"}, f"{label} source binding")
    if value.get("path") != path or value.get("mode") != "100755":
        fail(f"{label} source path or mode is invalid")
    require_sha(value.get("sha256"), label)
    require_commit(value.get("commit"), label)
    return value


def git_env() -> dict[str, str]:
    return {
        "PATH": "/usr/bin:/bin",
        "HOME": "/var/empty",
        "LANG": "C",
        "LC_ALL": "C",
        "GIT_CONFIG_GLOBAL": "/dev/null",
        "GIT_CONFIG_SYSTEM": "/dev/null",
        "GIT_TERMINAL_PROMPT": "0",
        "GIT_PAGER": "cat",
    }


def git_read(*args: str, allowed: tuple[int, ...] = (0,)) -> tuple[int, bytes]:
    try:
        completed = subprocess.run(
            [GIT, "--no-pager", "-c", "core.hooksPath=/dev/null", "-c", "core.fsmonitor=false", "-C", str(CHECKOUT), *args],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            env=git_env(),
            timeout=GIT_TIMEOUT,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise RegistryError("immutable Git evidence is unavailable") from exc
    if completed.returncode not in allowed or len(completed.stdout) > MAX_GIT_OUTPUT:
        fail("immutable Git evidence validation failed")
    return completed.returncode, completed.stdout


class GitEvidenceStore:
    """Read exact public evidence blobs from immutable Git objects only."""

    def __init__(self, name: str, record_raw: bytes):
        if not CHECKOUT_MODE:
            fail("portable registries cannot validate upper evidence states")
        self.name = name
        self.record_path = f"compat/personas/{name}.json"
        _rc, raw = git_read("log", "-1", "--format=%H", "HEAD", "--", self.record_path)
        try:
            self.transition_commit = raw.decode("ascii", "strict").strip()
        except UnicodeDecodeError as exc:
            raise RegistryError("transition commit is malformed") from exc
        require_commit(self.transition_commit, "transition")
        if self.read_at(self.transition_commit, self.record_path, "100644") != record_raw:
            fail("upper state record is not an immutable transition blob")
        if self.read_at("HEAD", self.record_path, "100644") != record_raw:
            fail("upper state record differs from current immutable Git bytes")

    def _tree(self, commit: str, path: str) -> tuple[str, str]:
        _rc, raw = git_read("ls-tree", commit, "--", path)
        try:
            text = raw.decode("utf-8", "strict")
        except UnicodeDecodeError as exc:
            raise RegistryError("immutable Git tree entry is malformed") from exc
        lines = text.splitlines()
        if len(lines) != 1 or "\t" not in lines[0]:
            fail("immutable Git evidence path is missing or ambiguous")
        meta, actual = lines[0].split("\t", 1)
        parts = meta.split(" ")
        if actual != path or len(parts) != 3 or parts[1] != "blob" or re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", parts[2]) is None:
            fail("immutable Git evidence tree entry is invalid")
        return parts[0], parts[2]

    def read_at(self, commit: str, path: str, mode: str = "100644") -> bytes:
        if commit != "HEAD":
            require_commit(commit, "evidence")
        if path.startswith("/") or ".." in Path(path).parts or "\x00" in path:
            fail("immutable Git evidence path is invalid")
        actual_mode, oid = self._tree(commit, path)
        if actual_mode != mode:
            fail("immutable Git evidence mode is invalid")
        _rc, raw = git_read("cat-file", "blob", oid)
        if len(raw) > MAX_FILE:
            fail("immutable Git evidence is oversized")
        return raw

    def read(self, value: Any, label: str, suffix: str | None = None) -> bytes:
        item = binding(value, label)
        prefix = f"compat/personas/evidence/{self.name}/"
        if not item["path"].startswith(prefix) or (suffix is not None and item["path"] != prefix + suffix):
            fail(f"{label} path is invalid")
        raw = self.read_at(item["commit"], item["path"])
        if digest(raw) != item["sha256"]:
            fail(f"{label} immutable blob digest drifted")
        if self.read_at(self.transition_commit, item["path"]) != raw:
            fail(f"{label} blob was rewritten after its reviewed commit")
        if self.read_at("HEAD", item["path"]) != raw:
            fail(f"{label} blob differs in the current immutable tree")
        return raw

    def read_artifact(self, value: Any, commit: str, label: str, suffix: str | None = None) -> bytes:
        item = artifact_binding(value, label)
        prefix = f"compat/personas/evidence/{self.name}/"
        if not item["path"].startswith(prefix) or (suffix is not None and item["path"] != prefix + suffix):
            fail(f"{label} artifact path is invalid")
        raw = self.read_at(commit, item["path"])
        if digest(raw) != item["sha256"]:
            fail(f"{label} artifact digest drifted")
        if self.read_at(self.transition_commit, item["path"]) != raw:
            fail(f"{label} artifact was rewritten after evidence review")
        if self.read_at("HEAD", item["path"]) != raw:
            fail(f"{label} artifact differs in the current immutable tree")
        return raw

    def strict_ancestor(self, older: str, newer: str, label: str) -> None:
        require_commit(older, label)
        require_commit(newer, label)
        if older == newer:
            fail(f"{label} commits must be distinct")
        rc, _raw = git_read("merge-base", "--is-ancestor", older, newer, allowed=(0, 1))
        if rc != 0:
            fail(f"{label} commit order is invalid")

    def ancestor_or_equal(self, older: str, newer: str, label: str) -> None:
        require_commit(older, label)
        require_commit(newer, label)
        rc, _raw = git_read("merge-base", "--is-ancestor", older, newer, allowed=(0, 1))
        if rc != 0:
            fail(f"{label} commit order is invalid")

    def paths_at(self, commit: str) -> set[str]:
        prefix = f"compat/personas/evidence/{self.name}/"
        _rc, raw = git_read("ls-tree", "-r", "-z", "--name-only", commit, "--", prefix)
        try:
            return {item.decode("utf-8", "strict") for item in raw.split(b"\0") if item}
        except UnicodeDecodeError as exc:
            raise RegistryError("immutable evidence path inventory is malformed") from exc


def load_bound_json(store: GitEvidenceStore, value: Any, label: str, schema_name: str, suffix: str | None = None, commit: str | None = None) -> tuple[dict[str, Any], bytes]:
    raw = store.read(value, label, suffix) if commit is None else store.read_artifact(value, commit, label, suffix)
    parsed = strict_object(raw, label)
    if raw != canonical_bytes(parsed):
        fail(f"{label} bytes are not canonical")
    schema_validate(parsed, load_schema(RUNTIME / "schemas" / SCHEMA_FILES[schema_name]))
    return parsed, raw


def validate_receipt_bytes(raw: bytes, label: str) -> dict[str, Any]:
    scripts = str(RUNTIME / "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    from evidence_receipt import ValidationFailure, validate_receipt
    parsed = strict_object(raw, label)
    if raw != canonical_bytes(parsed):
        fail(f"{label} bytes are not canonical")
    try:
        return validate_receipt(parsed, load_schema(RECEIPT_SCHEMA))
    except ValidationFailure as exc:
        raise RegistryError(f"{label} is invalid") from exc


def validate_selection_bytes(raw: bytes) -> dict[str, Any]:
    scripts = str(RUNTIME / "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    from model_selection import CallerError, EvidenceUnavailable, ReviewRequired, validate_selection_record_shape
    parsed = strict_object(raw, "selection")
    if raw != canonical_bytes(parsed):
        fail("selection bytes are not canonical")
    try:
        validate_selection_record_shape(parsed)
    except (CallerError, EvidenceUnavailable, ReviewRequired) as exc:
        raise RegistryError("selection is invalid") from exc
    return parsed


def validate_benchmark_chain(store: GitEvidenceStore, artifacts: dict[str, Any], evidence_commit: str, record: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    plan_raw = store.read_artifact(artifacts["benchmark_plan"], evidence_commit, "benchmark plan", "benchmark-plan.json")
    result_raw = store.read_artifact(artifacts["benchmark_result"], evidence_commit, "benchmark result", "benchmark-result.json")
    receipt_raw = store.read_artifact(artifacts["benchmark_receipt"], evidence_commit, "benchmark receipt", "benchmark-receipt.json")
    plan = strict_object(plan_raw, "benchmark plan")
    result = strict_object(result_raw, "benchmark result")
    if plan_raw != canonical_bytes(plan) or result_raw != canonical_bytes(result):
        fail("benchmark evidence bytes are not canonical")
    schema_validate(plan, load_schema(PLAN_SCHEMA))
    schema_validate(result, load_schema(RESULT_SCHEMA))
    receipt = validate_receipt_bytes(receipt_raw, "benchmark receipt")
    authority = plan.get("tool_authority")
    if not isinstance(authority, dict) or authority.get("source_kind") != "git-clean-commit":
        fail("benchmark source authority is invalid")
    source_commit = require_commit(authority.get("source_revision"), "benchmark source")
    runtime_prefix = "skills/agy-worker/runtime/"
    scripts = str(RUNTIME / "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    import benchmark as benchmark_contract
    portable_raw = store.read_at(source_commit, runtime_prefix + "benchmarks/v1/portable-source.json", "100644")
    portable = strict_object(portable_raw, "benchmark portable source")
    if portable_raw != canonical_bytes(portable):
        fail("benchmark portable source bytes are not canonical")
    expected_portable = [(relative, "100755" if mode == 0o755 else "100644") for relative, mode in benchmark_contract.PORTABLE_FILES]
    files = portable.get("files")
    if portable.get("schema_version") != 1 or portable.get("kind") != "agy-worker-benchmark-portable-source" or portable.get("source_revision") != benchmark_contract.PORTABLE_REVISION or not isinstance(files, list) or len(files) != len(expected_portable):
        fail("benchmark portable source contract drifted")
    source_assets: dict[str, bytes] = {}
    for item, (relative, mode) in zip(files, expected_portable):
        if not isinstance(item, dict) or item != {"path": relative, "mode": mode, "sha256": item.get("sha256")}:
            fail("benchmark portable source entry is invalid")
        require_sha(item.get("sha256"), "benchmark portable source")
        asset = store.read_at(source_commit, runtime_prefix + relative, mode)
        if digest(asset) != item["sha256"]:
            fail("benchmark portable source blob drifted")
        source_assets[relative] = asset

    manifest_raw = store.read_at(source_commit, runtime_prefix + "benchmarks/v1/manifest.json", "100644")
    manifest = strict_object(manifest_raw, "benchmark manifest")
    if manifest_raw != canonical_bytes(manifest) or digest(manifest_raw) != record["offline_evidence"]["benchmark_manifest_sha256"]:
        fail("benchmark manifest binding drifted")
    if manifest.get("schema_version") != 1 or manifest.get("kind") != "agy-worker-benchmark-manifest" or manifest.get("limits") != {"max_file_bytes": 65536, "max_runs": 64, "max_tasks": 16, "max_variants": 8}:
        fail("benchmark manifest contract drifted")
    manifest_tasks = manifest.get("tasks")
    if not isinstance(manifest_tasks, list) or len(manifest_tasks) != 1:
        fail("benchmark task inventory drifted")
    task = manifest_tasks[0]
    if not isinstance(task, dict) or set(task) != {"id", "initial_source", "initial_sha256", "candidate_source", "candidate_sha256", "envelope_source", "envelope_sha256", "only", "expect_edits", "verifiers"}:
        fail("benchmark task contract drifted")
    fixture_parts: list[bytes] = []
    for source_key, hash_key in (("initial_source", "initial_sha256"), ("candidate_source", "candidate_sha256"), ("envelope_source", "envelope_sha256")):
        relative = task.get(source_key)
        if not isinstance(relative, str) or not relative.startswith("tasks/") or ".." in Path(relative).parts:
            fail("benchmark fixture path drifted")
        fixture = store.read_at(source_commit, runtime_prefix + "benchmarks/v1/" + relative, "100644")
        if digest(fixture) != task.get(hash_key):
            fail("benchmark fixture binding drifted")
        fixture_parts.append(fixture)
    if task.get("id") != "exact-edit" or task.get("only") != ["proof.txt"] or task.get("expect_edits") is not True or task.get("verifiers") != ["exact-content", "diff-check"]:
        fail("benchmark task policy drifted")

    variant_raw = store.read_at(source_commit, runtime_prefix + "benchmarks/v1/variants/bulk.json", "100644")
    variant_value = strict_object(variant_raw, "benchmark variant")
    if variant_raw != canonical_bytes(variant_value) or set(variant_value) != {"schema_version", "kind", "name", "selection", "persona"} or variant_value.get("schema_version") != 1 or variant_value.get("kind") != "agy-worker-benchmark-variant-input" or variant_value.get("name") != "bulk" or variant_value.get("persona") is not None:
        fail("benchmark variant contract drifted")
    selection = validate_selection_bytes(canonical_bytes(variant_value.get("selection")))
    expected_variant = {"name": "bulk", "source_sha256": digest(variant_raw), "selection": selection, "selection_sha256": digest(canonical_bytes(selection)), "persona": None}
    expected_task = {key: task[key] for key in ("id", "initial_sha256", "candidate_sha256", "envelope_sha256", "only", "expect_edits", "verifiers")}
    expected_authority = {
        "source_kind": "git-clean-commit",
        "source_revision": source_commit,
        "source_manifest_sha256": digest(portable_raw),
        "benchmark_runner_sha256": digest(source_assets["scripts/benchmark.py"]),
        "qa_gate_sha256": digest(source_assets["qa-gate.sh"]),
        "verify_job_sha256": digest(source_assets["verify-job.sh"]),
        "plan_schema_sha256": digest(source_assets["schemas/benchmark-plan.schema.json"]),
        "result_schema_sha256": digest(source_assets["schemas/benchmark-result.schema.json"]),
        "receipt_schema_sha256": digest(source_assets["schemas/evidence-receipt.schema.json"]),
        "manifest_sha256": digest(manifest_raw),
        "fixture_set_sha256": digest(b"".join(fixture_parts)),
    }
    expected_policy = {"mode": "offline-synthetic", "attempts_per_variant_task": 1, "gate_authority": "qa-gate", "live_execution": False, "network": False, "provider": False, "ranking": False, "routing": False, "recommendation": False, "driver_duration": "diagnostic-only-not-recorded"}
    expected_plan = {"schema_version": 1, "kind": "agy-worker-benchmark-plan", "manifest_sha256": digest(manifest_raw), "tool_authority": expected_authority, "policy": expected_policy, "tasks": [expected_task], "variants": [expected_variant], "expected_runs": 1, "integrity": {"signed": False, "tamper_evident": False}}
    if plan != expected_plan:
        fail("benchmark plan differs from immutable canonical P1-C assets")
    if record["offline_evidence"]["selection_sha256"] != expected_variant["selection_sha256"] or record["offline_evidence"]["qa_gate_sha256"] != expected_authority["qa_gate_sha256"] or record["offline_evidence"]["verify_job_sha256"] != expected_authority["verify_job_sha256"] or record["offline_evidence"]["receipt_schema_sha256"] != expected_authority["receipt_schema_sha256"]:
        fail("persona offline evidence differs from canonical P1-C authority")
    if receipt.get("caller_selection") != selection:
        fail("benchmark selection facts drifted")
    run = {"sequence": 1, "variant": "bulk", "task": "exact-edit", "attempt": 1, "receipt_name": "receipt-001.json", "receipt_sha256": digest(receipt_raw), "gate_exit": receipt["gate_exit"], "gate_outcome": receipt["gate_outcome"], "verdict": receipt["verdict"], "resolved_base": receipt["resolved_base"], "initial_candidate_state_sha256": receipt["initial_candidate_state_sha256"], "final_candidate_state_sha256": receipt["final_candidate_state_sha256"], "selection_sha256": expected_variant["selection_sha256"]}
    expected_result = {"schema_version": 1, "kind": "agy-worker-benchmark-result", "plan_sha256": digest(plan_raw), "manifest_sha256": digest(manifest_raw), "policy": {key: value for key, value in expected_policy.items() if key != "driver_duration"}, "complete": True, "runs": [run], "integrity": {"signed": False, "tamper_evident": False}}
    if result != expected_result:
        fail("benchmark result differs from canonical P1-C run facts")
    return plan, result, receipt


def validate_version_attestation(value: dict[str, Any], runner_sha256: str) -> dict[str, Any]:
    if runner_sha256 != ACCEPTED_VERSION_FACTS["runner_sha256"]:
        fail("accepted version runner source drifted")
    expected = {
        "schema_version": 1,
        "kind": "agy-worker-public-version-attestation",
        "claim": "maintainer-reviewed-private-version-reference",
        "status": "accepted",
        "version": ACCEPTED_VERSION_FACTS,
        "limitations": VERSION_LIMITATIONS,
    }
    if value != expected:
        fail("public version attestation facts drifted")
    return value["version"]


def validate_real_evidence(record: dict[str, Any], raw: bytes) -> None:
    status = record["status"]
    manifest_binding = record["real_evidence"]
    approval_binding = record["transition_approval"]
    review_binding = record["human_review"]
    if status == "offline-only":
        if any(item is not None for item in (manifest_binding, approval_binding, review_binding)):
            fail("offline-only records cannot carry upper-state evidence")
        return
    if any(item is None for item in (manifest_binding, approval_binding)):
        fail("upper state requires evidence and approval")
    if (status == "accepted-real-candidate") != (review_binding is not None):
        fail("human review presence does not match the upper state")
    store = GitEvidenceStore(record["name"], raw)
    manifest, _manifest_raw = load_bound_json(store, manifest_binding, "evidence manifest", "manifest", "evidence-manifest.json")
    evidence_commit = manifest_binding["commit"]
    approval_commit = approval_binding["commit"]
    if manifest.get("persona") != record["name"] or manifest.get("target_state") != status:
        fail("evidence manifest persona or state drifted")
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, dict) or set(artifacts) != {name.replace("-", "_").replace(".json", "").replace(".diff", "") for name in EVIDENCE_FILES}:
        fail("evidence manifest artifact allowlist drifted")
    for key, item in artifacts.items():
        artifact_binding(item, f"{key} artifact")
    evidence_paths = {f"compat/personas/evidence/{record['name']}/evidence-manifest.json", *(item["path"] for item in artifacts.values())}
    approval_paths = {*evidence_paths, approval_binding["path"]}
    if review_binding is not None:
        approval_paths.add(review_binding["path"])
    if store.paths_at(evidence_commit) != evidence_paths:
        fail("evidence-commit artifact allowlist drifted")
    if store.paths_at(approval_commit) != approval_paths:
        fail("approval-commit artifact allowlist drifted")
    if store.paths_at(store.transition_commit) != approval_paths or store.paths_at("HEAD") != approval_paths:
        fail("public evidence directory allowlist drifted")
    store.strict_ancestor(evidence_commit, approval_commit, "evidence-to-approval")
    store.strict_ancestor(approval_commit, store.transition_commit, "approval-to-transition")
    if review_binding is not None and review_binding["commit"] != approval_commit:
        fail("approval and human review must be immutable siblings")

    plan, _result, benchmark_receipt = validate_benchmark_chain(store, artifacts, evidence_commit, record)
    real_receipt_raw = store.read_artifact(artifacts["real_receipt"], evidence_commit, "real Receipt", "real-receipt.json")
    real_receipt = validate_receipt_bytes(real_receipt_raw, "real Receipt")
    selection_raw = store.read_artifact(artifacts["selection"], evidence_commit, "selection", "selection.json")
    selection = validate_selection_bytes(selection_raw)
    dispatch, _ = load_bound_json(store, artifacts["dispatch_profile"], "dispatch profile", "dispatch", "dispatch-profile.json", evidence_commit)
    tool, _ = load_bound_json(store, artifacts["tool_attestation"], "tool attestation", "tool", "tool-attestation.json", evidence_commit)
    version, version_raw = load_bound_json(store, artifacts["version_attestation"], "version attestation", "version", "version-attestation.json", evidence_commit)
    verifier, _ = load_bound_json(store, artifacts["verifier_001"], "verifier", "verifier", "verifier-001.json", evidence_commit)
    run, _ = load_bound_json(store, artifacts["run_evidence"], "run evidence", "run", "run-evidence.json", evidence_commit)
    diff_raw = store.read_artifact(artifacts["candidate"], evidence_commit, "candidate diff", "candidate.diff")
    approval, _ = load_bound_json(store, approval_binding, "transition approval", "approval", "transition-approval.json")
    review = None
    if review_binding is not None:
        review, _ = load_bound_json(store, review_binding, "human review", "review", "human-review.json")

    expected_exit = 15 if status == "real-escalation-observed" else 0
    expected_outcome = "worker-escalation" if expected_exit == 15 else "gate-passed"
    expected_verdict = "routed" if expected_exit == 15 else "gate-passed"
    if (real_receipt["gate_exit"], real_receipt["gate_outcome"], real_receipt["verdict"]) != (expected_exit, expected_outcome, expected_verdict):
        fail("real Receipt does not support the registry state")
    if real_receipt.get("caller_selection") != selection:
        fail("real Receipt selection differs from the public selection artifact")
    if dispatch != {"schema_version": 1, "kind": "agy-worker-persona-dispatch", "driver_owned": True, "persona": record["name"], "persona_source_sha256": record["persona"]["sha256"], "mode": dispatch.get("mode"), "dispatcher_sha256": record["offline_evidence"]["dispatcher_sha256"], "selection_sha256": digest(selection_raw), "resolved_base": real_receipt["resolved_base"]} or dispatch["mode"] not in record["modes"]:
        fail("driver-owned persona execution binding is invalid")
    source_commit = plan["tool_authority"]["source_revision"]
    require_commit(source_commit, "benchmark source")
    store.strict_ancestor(source_commit, evidence_commit, "source-to-evidence")
    if real_receipt["resolved_base"] != benchmark_receipt["resolved_base"] or real_receipt["resolved_base"] == source_commit:
        fail("target base is conflated with agy-worker source authority")
    dispatcher_binding = source_binding(tool.get("dispatcher"), "dispatcher", "skills/agy-worker/runtime/agy-worker.sh")
    if dispatcher_binding.get("sha256") != dispatch["dispatcher_sha256"]:
        fail("dispatcher tool binding is invalid")
    if dispatcher_binding.get("commit") != source_commit:
        fail("dispatcher source commit is incoherent")
    dispatcher_raw = store.read_at(source_commit, dispatcher_binding["path"], "100755")
    if digest(dispatcher_raw) != dispatcher_binding["sha256"]:
        fail("dispatcher immutable bytes drifted")
    validate_dispatcher_contract(dispatcher_raw)
    for key, path, mode in (("qa_gate", "skills/agy-worker/runtime/qa-gate.sh", "100755"), ("verify_job", "skills/agy-worker/runtime/verify-job.sh", "100755")):
        item = source_binding(tool.get(key), key, path)
        if item.get("commit") != source_commit or digest(store.read_at(source_commit, path, mode)) != item.get("sha256"):
            fail("public tool source bytes drifted")
    runner_binding = source_binding(tool.get("version_runner"), "version runner", "scripts/version_attestation_runner.py")
    if runner_binding.get("commit") != source_commit:
        fail("version runner source commit is incoherent")
    runner_raw = store.read_at(source_commit, runner_binding["path"], "100755")
    if digest(runner_raw) != runner_binding["sha256"]:
        fail("version runner immutable bytes drifted")
    source_persona_path = f"skills/agy-worker/runtime/agents/{record['name']}.md"
    source_persona_raw = store.read_at(source_commit, source_persona_path, "100644")
    parse_frontmatter(source_persona_raw, record["name"])
    if digest(source_persona_raw) != record["persona"]["sha256"] or dispatch["persona_source_sha256"] != digest(source_persona_raw):
        fail("executed persona source binding drifted")
    version_facts = validate_version_attestation(version, runner_binding["sha256"])
    if tool.get("agy_version") != version_facts["observed"] or tool.get("agy_version_binding_sha256") != version_facts["binding_sha256"] or tool.get("version_attestation_sha256") != digest(version_raw):
        fail("agy version attestation binding drifted")
    if VERSION_RE.fullmatch(version_facts["observed"]) is None:
        fail("agy version attestation syntax is invalid")
    if status == "accepted-real-candidate" and dispatch["mode"] != "accept-edits":
        fail("accepted candidate requires exact accept-edits persona execution")
    if tool.get("selection_sha256") != digest(selection_raw) or tool.get("verifier_sha256") != digest(store.read_artifact(artifacts["verifier_001"], evidence_commit, "verifier", "verifier-001.json")):
        fail("selection or verifier tool binding drifted")
    if len(real_receipt["verifiers"]) != 1 or verifier.get("label") != "verify-001" or verifier.get("command_sha256") != real_receipt["verifiers"][0]["command_sha256"] or verifier.get("driver_owned") is not True:
        fail("verifier artifact differs from the real Receipt")
    facts = {key: real_receipt[key] for key in ("resolved_base", "initial_candidate_state_sha256", "final_candidate_state_sha256", "gate_exit", "gate_outcome", "verdict")}
    expected_run = {"schema_version": 1, "kind": "agy-worker-persona-real-run", "persona": record["name"], "target_state": status, "dispatch_profile_sha256": digest(store.read_artifact(artifacts["dispatch_profile"], evidence_commit, "dispatch profile", "dispatch-profile.json")), "tool_attestation_sha256": digest(store.read_artifact(artifacts["tool_attestation"], evidence_commit, "tool attestation", "tool-attestation.json")), "selection_sha256": digest(selection_raw), "real_receipt_sha256": digest(real_receipt_raw), "benchmark_plan_sha256": digest(store.read_artifact(artifacts["benchmark_plan"], evidence_commit, "benchmark plan", "benchmark-plan.json")), "benchmark_result_sha256": digest(store.read_artifact(artifacts["benchmark_result"], evidence_commit, "benchmark result", "benchmark-result.json")), "benchmark_receipt_sha256": digest(store.read_artifact(artifacts["benchmark_receipt"], evidence_commit, "benchmark receipt", "benchmark-receipt.json")), "candidate_diff_sha256": digest(diff_raw), **facts}
    if run != expected_run:
        fail("real run evidence cross-field binding drifted")
    approval_expected = {"schema_version": 1, "kind": "agy-worker-persona-transition-approval", "persona": record["name"], "from_status": "offline-only", "to_status": status, "decision": "approved", "reviewer_role": "maintainer", "evidence_commit": evidence_commit, "evidence_manifest_sha256": manifest_binding["sha256"], "run_evidence_sha256": artifacts["run_evidence"]["sha256"], "real_receipt_sha256": artifacts["real_receipt"]["sha256"], "candidate_state_sha256": real_receipt["final_candidate_state_sha256"], "candidate_diff_sha256": artifacts["candidate"]["sha256"]}
    if approval != approval_expected:
        fail("transition approval does not bind the exact evidence")
    if status == "accepted-real-candidate":
        review_expected = {"schema_version": 1, "kind": "agy-worker-persona-human-review", "persona": record["name"], "target_state": status, "decision": "accepted", "reviewer_role": "human-maintainer", "evidence_commit": evidence_commit, "run_evidence_sha256": artifacts["run_evidence"]["sha256"], "real_receipt_sha256": artifacts["real_receipt"]["sha256"], "resolved_base": real_receipt["resolved_base"], "candidate_state_sha256": real_receipt["final_candidate_state_sha256"], "candidate_diff_sha256": artifacts["candidate"]["sha256"]}
        if review != review_expected:
            fail("human review does not bind the exact candidate and diff")
    if benchmark_receipt.get("recommendations_participated_in_acceptance") is not False or plan["variants"][0]["persona"] is not None:
        fail("P1-C evidence acquired persona trust semantics")


def validate_record(value: dict[str, Any], raw: bytes) -> dict[str, Any]:
    schema_validate(value, load_schema(SCHEMA))
    if raw != canonical_bytes(value):
        fail("persona evidence bytes are not canonical")
    name = value.get("name")
    if name not in PERSONAS or value.get("status") not in STATES:
        fail("persona name or evidence status is unsupported")
    if value.get("modes") != list(MODES[name]):
        fail("persona mode restriction does not match the runtime allowlist")
    persona = value.get("persona")
    if not isinstance(persona, dict):
        fail("persona source binding is missing")
    expected_path = f"agents/{name}.md"
    if persona.get("path") != expected_path:
        fail("persona source path is invalid")
    persona_raw = read_public(RUNTIME / expected_path, "persona source")
    parse_frontmatter(persona_raw, name)
    if persona.get("sha256") != digest(persona_raw):
        fail("persona source binding drifted")
    if value.get("offline_evidence") != expected_offline_evidence():
        fail("offline evidence binding drifted")
    if value.get("limitations") != {
        "acceptance_authority": False,
        "general_reliability": False,
        "persona_enforcement": False,
        "prompt_guidance_only": True,
    }:
        fail("persona evidence limitations are invalid")
    validate_real_evidence(value, raw)
    return value


def validate_manifest(value: dict[str, Any], raw: bytes) -> list[dict[str, Any]]:
    schema_validate(value, load_schema(MANIFEST_SCHEMA))
    if raw != canonical_bytes(value):
        fail("persona registry manifest bytes are not canonical")
    if value.get("states") != list(STATES):
        fail("persona evidence state order drifted")
    records = value.get("records")
    if not isinstance(records, list) or [item.get("name") for item in records if isinstance(item, dict)] != list(PERSONAS):
        fail("persona registry allowlist drifted")
    expected_files = {"manifest.json", *(f"{name}.json" for name in PERSONAS)}
    try:
        actual_files = {item.name for item in REGISTRY.iterdir() if item.is_file() or item.is_symlink()}
    except OSError as exc:
        raise RegistryError("persona registry is unavailable") from exc
    if actual_files != expected_files:
        fail("persona registry contains missing or dynamic records")
    loaded: list[dict[str, Any]] = []
    for item, name in zip(records, PERSONAS):
        if not isinstance(item, dict) or item.get("path") != f"{name}.json":
            fail("persona registry record path is invalid")
        record_raw = read_public(REGISTRY / item["path"], "persona evidence record")
        if item.get("sha256") != digest(record_raw):
            fail("persona registry record binding drifted")
        record = validate_record(strict_object(record_raw, "persona evidence record"), record_raw)
        if record["name"] != name:
            fail("persona registry record name drifted")
        loaded.append(record)
    return loaded


def validate_registry() -> list[dict[str, Any]]:
    manifest_raw = read_public(REGISTRY / "manifest.json", "persona registry manifest")
    records = validate_manifest(strict_object(manifest_raw, "persona registry manifest"), manifest_raw)
    if CHECKOUT_MODE:
        root_registry = CHECKOUT / "compat" / "personas"
        for name in ("manifest", *PERSONAS):
            filename = f"{name}.json"
            if read_public(REGISTRY / filename, "portable persona registry") != read_public(root_registry / filename, "root persona registry"):
                fail("root and portable persona registries differ")
    return records


def markdown(records: list[dict[str, Any]]) -> str:
    lines = [
        "| Persona | Allowed modes | Evidence status | Public evidence |",
        "|---|---|---|---|",
    ]
    for record in records:
        modes = ", ".join(f"`{mode}`" for mode in record["modes"])
        if record["status"] == "offline-only":
            evidence = "P1-C public contract; persona not executed"
        elif record["status"] == "real-escalation-observed":
            evidence = "public routed Receipt + transition approval"
        else:
            evidence = "public gate-passed Receipt + human review + transition approval"
        lines.append(f"| `{record['name']}` | {modes} | `{record['status']}` | {evidence} |")
    lines.extend([
        "",
        "Statuses are evidence levels, not trust labels or acceptance authority.",
    ])
    output = "\n".join(lines) + "\n"
    if len(output.encode("utf-8")) > MAX_OUTPUT:
        fail("persona evidence report is oversized")
    return output


def usage() -> int:
    print("usage: persona-evidence.sh validate|report", file=sys.stderr)
    return 64


def main(argv: list[str]) -> int:
    if len(argv) != 1 or argv[0] not in {"validate", "report"}:
        return usage()
    try:
        records = validate_registry()
        output = f"persona evidence registry valid: {len(records)} records\n" if argv[0] == "validate" else markdown(records)
    except Exception:
        print("persona-evidence: registry validation failed", file=sys.stderr)
        return 2
    sys.stdout.write(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
