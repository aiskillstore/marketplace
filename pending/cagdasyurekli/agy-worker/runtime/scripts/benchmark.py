#!/usr/bin/env python3
"""Prepare, execute, and report provider-independent offline Benchmark v1.

This module never imports or invokes agy, never selects or changes a model, and
never ranks benchmark variants.  ``qa-gate`` remains the sole verdict authority.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import selectors
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
import time
from typing import Any, NoReturn

sys.dont_write_bytecode = True
SCRIPT_DIR = Path(__file__).resolve(strict=True).parent
RUNTIME = SCRIPT_DIR.parent
BENCH_ROOT = RUNTIME / "benchmarks" / "v1"
MANIFEST_PATH = BENCH_ROOT / "manifest.json"
PORTABLE_SOURCE_PATH = BENCH_ROOT / "portable-source.json"
RECEIPT_SCHEMA = RUNTIME / "schemas" / "evidence-receipt.schema.json"
PLAN_SCHEMA = RUNTIME / "schemas" / "benchmark-plan.schema.json"
RESULT_SCHEMA = RUNTIME / "schemas" / "benchmark-result.schema.json"
VERIFY_JOB = RUNTIME / "verify-job.sh"
QA_GATE = RUNTIME / "qa-gate.sh"
_REPO_CANDIDATE = RUNTIME.parents[2]
CHECKOUT_MODE = (
    (_REPO_CANDIDATE / "skills" / "agy-worker" / "runtime").is_dir()
    and Path(os.path.realpath(_REPO_CANDIDATE / "skills" / "agy-worker" / "runtime")) == RUNTIME
)
REPO_ROOT = _REPO_CANDIDATE if CHECKOUT_MODE else RUNTIME
ROOT_BENCH = REPO_ROOT / "benchmarks" / "v1" if CHECKOUT_MODE else BENCH_ROOT
MAX_JSON = 256 * 1024
MAX_VARIANT = 64 * 1024
MAX_STREAM = 128 * 1024
RUN_TIMEOUT = 30.0
SHA_RE = re.compile(r"[0-9a-f]{64}")
NAME_RE = re.compile(r"[a-z0-9](?:[a-z0-9-]{0,30}[a-z0-9])?")
PORTABLE_REVISION = "offline-benchmark-v1"
PORTABLE_FILES = (
    ("benchmark.sh", 0o755),
    ("qa-gate.sh", 0o755),
    ("verify-job.sh", 0o755),
    ("scripts/benchmark.py", 0o755),
    ("scripts/candidate_state.py", 0o755),
    ("scripts/compatibility.py", 0o755),
    ("scripts/evidence_receipt.py", 0o755),
    ("scripts/model_selection.py", 0o755),
    ("scripts/recommendation_record.py", 0o755),
    ("scripts/validate-envelope.py", 0o755),
    ("schemas/benchmark-plan.schema.json", 0o644),
    ("schemas/benchmark-result.schema.json", 0o644),
    ("schemas/evidence-receipt.schema.json", 0o644),
    ("schemas/worker-result.schema.json", 0o644),
    ("schemas/worker-result.provider.schema.json", 0o644),
)
BENCHMARK_TREE_FILES = {
    "manifest.json",
    "portable-source.json",
    "tasks/exact-edit/candidate.txt",
    "tasks/exact-edit/envelope.json",
    "tasks/exact-edit/initial.txt",
    "variants/bulk.json",
}
SIGNALS = (signal.SIGHUP, signal.SIGINT, signal.SIGTERM)
ACTIVE_PUBLICATIONS: list[tuple[Path, str, tuple[int, int]]] = []
try:
    _WAITID = ctypes.CDLL(None, use_errno=True).waitid
except (AttributeError, OSError):
    _WAITID = None

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from evidence_receipt import (  # noqa: E402
    ValidationFailure,
    canonical_bytes,
    load_schema,
    parse_json_bytes,
    read_real_file,
    validate_schema,
    validate_receipt,
)
from model_selection import (  # noqa: E402
    CallerError as SelectionError,
    validate_selection_record_shape,
)


class BenchmarkError(ValueError):
    pass


class Interrupted(BaseException):
    def __init__(self, number: int) -> None:
        self.number = number


class Parser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        del message
        self.print_usage(sys.stderr)
        self.exit(64, "benchmark: invalid arguments\n")


def fail(message: str) -> None:
    raise BenchmarkError(message)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def validate_source_contract(source: bytes) -> None:
    """Bind the fixed offline-only and one-attempt production authority."""
    required = {
        b'"attempts_per_variant_task": 1': 5,
        b'"live_execution": False': 5,
        b'"ranking": False': 6,
        b'"routing": False': 5,
        b'"recommendation": False': 5,
        b'process = subprocess.Popen(': 2,
        b'argv = [str(VERIFY_JOB),': 2,
        b'os._exit(0)': 2,
        b'rollback_publications()': 6,
        b'validate_receipt(': 3,
        b'validate_selection_record_shape(value)': 2,
        b'CallerError as SelectionError': 2,
        b'create_mask = signal.pthread_sigmask': 2,
        b'link_mask = signal.pthread_sigmask': 2,
        b'signal.pthread_sigmask(signal.SIG_BLOCK, SIGNALS)': 10,
        b'_leader_exited_unreaped(process)': 2,
        b'_close_group(process)': 4,
        b'load_portable_source()': 4,
        b'observed != BENCHMARK_TREE_FILES': 2,
        b'stat.S_IMODE(st.st_mode) != mode': 2,
    }
    if any(source.count(marker) != count for marker, count in required.items()):
        fail("benchmark runner source contract drifted")
    forbidden = (b"import " + b"requests", b"url" + b"lib", b"agy " + b"models", b"--eff" + b"ort", b"--li" + b"ve", b"shell" + b"=True", b"process." + b"poll()")
    if any(marker in source for marker in forbidden):
        fail("benchmark runner source exposes forbidden authority")


def strict_object(data: bytes, label: str) -> dict[str, Any]:
    try:
        value = parse_json_bytes(data, label)
    except ValidationFailure as exc:
        raise BenchmarkError(f"invalid {label}") from exc
    if not isinstance(value, dict):
        fail(f"{label} must be one object")
    return value


def exact_fields(value: dict[str, Any], expected: set[str], label: str) -> None:
    if set(value) != expected:
        fail(f"{label} fields are invalid")


def require_sha(value: Any, label: str) -> str:
    if not isinstance(value, str) or SHA_RE.fullmatch(value) is None:
        fail(f"{label} is not a SHA-256 digest")
    return value


def read_file(path: Path, label: str, maximum: int = MAX_JSON) -> bytes:
    try:
        return read_real_file(path, label, maximum)
    except ValidationFailure as exc:
        raise BenchmarkError(f"invalid {label}") from exc


def verify_asset(relative: str, expected: str) -> bytes:
    if relative.startswith("/") or ".." in Path(relative).parts or "\\" in relative:
        fail("manifest source is not portable")
    path = BENCH_ROOT / relative
    data = read_file(path, "benchmark asset", 64 * 1024)
    if digest(data) != expected:
        fail("benchmark asset digest drifted")
    if CHECKOUT_MODE:
        root_copy = ROOT_BENCH / relative
        if read_file(root_copy, "root benchmark asset", 64 * 1024) != data:
            fail("root and portable benchmark assets differ")
    return data


def _checked_runtime_file(relative: str, mode: int) -> bytes:
    path = RUNTIME / relative
    current = RUNTIME
    if RUNTIME.is_symlink() or Path(os.path.realpath(RUNTIME)) != RUNTIME:
        fail("portable runtime root is not canonical")
    for part in Path(relative).parts[:-1]:
        current = current / part
        st = os.lstat(current)
        if not stat.S_ISDIR(st.st_mode) or stat.S_ISLNK(st.st_mode) or st.st_uid != os.getuid() or stat.S_IMODE(st.st_mode) & 0o022:
            fail("portable runtime parent is unsafe")
    st = os.lstat(path)
    if not stat.S_ISREG(st.st_mode) or stat.S_ISLNK(st.st_mode) or st.st_uid != os.getuid() or stat.S_IMODE(st.st_mode) != mode:
        fail("portable runtime file mode or identity is invalid")
    return read_file(path, "portable runtime authority", MAX_JSON)


def _validate_benchmark_tree(root: Path) -> None:
    observed: set[str] = set()
    for directory, directories, files in os.walk(root, followlinks=False):
        parent = Path(directory)
        relative_parent = parent.relative_to(root)
        for name in directories:
            path = parent / name
            st = os.lstat(path)
            if stat.S_ISLNK(st.st_mode) or not stat.S_ISDIR(st.st_mode) or st.st_uid != os.getuid() or stat.S_IMODE(st.st_mode) & 0o022:
                fail("benchmark asset directory is unsafe")
        for name in files:
            path = parent / name
            relative = str((relative_parent / name).as_posix())
            st = os.lstat(path)
            if not stat.S_ISREG(st.st_mode) or stat.S_ISLNK(st.st_mode) or st.st_uid != os.getuid() or stat.S_IMODE(st.st_mode) != 0o644:
                fail("benchmark asset mode or identity is invalid")
            observed.add(relative)
    if observed != BENCHMARK_TREE_FILES:
        fail("benchmark asset tree has missing or extra files")


def load_portable_source() -> tuple[dict[str, Any], bytes]:
    _validate_benchmark_tree(BENCH_ROOT)
    raw = read_file(PORTABLE_SOURCE_PATH, "portable source manifest")
    value = strict_object(raw, "portable source manifest")
    exact_fields(value, {"schema_version", "kind", "source_revision", "files"}, "portable source manifest")
    if value.get("schema_version") != 1 or value.get("kind") != "agy-worker-benchmark-portable-source" or value.get("source_revision") != PORTABLE_REVISION:
        fail("portable source revision is invalid")
    files = value.get("files")
    if not isinstance(files, list) or len(files) != len(PORTABLE_FILES):
        fail("portable source file inventory is invalid")
    expected_paths = [item[0] for item in PORTABLE_FILES]
    if [item.get("path") if isinstance(item, dict) else None for item in files] != expected_paths:
        fail("portable source file ordering is invalid")
    for item, (relative, mode) in zip(files, PORTABLE_FILES):
        exact_fields(item, {"path", "mode", "sha256"}, "portable source file")
        expected_mode = "100755" if mode == 0o755 else "100644"
        if item.get("mode") != expected_mode or item.get("sha256") != digest(_checked_runtime_file(relative, mode)):
            fail("portable source file binding drifted")
    if raw != canonical_bytes(value) + b"\n":
        fail("portable source manifest is not canonical")
    if CHECKOUT_MODE:
        _validate_benchmark_tree(ROOT_BENCH)
        if read_file(ROOT_BENCH / "portable-source.json", "root portable source manifest") != raw:
            fail("root and portable source manifests differ")
    return value, raw


def validate_manifest(value: dict[str, Any]) -> dict[str, Any]:
    exact_fields(value, {"schema_version", "kind", "limits", "tasks"}, "manifest")
    if value.get("schema_version") != 1 or value.get("kind") != "agy-worker-benchmark-manifest":
        fail("manifest version is unsupported")
    limits = value.get("limits")
    if limits != {"max_file_bytes": 65536, "max_runs": 64, "max_tasks": 16, "max_variants": 8}:
        fail("manifest limits changed")
    tasks = value.get("tasks")
    if not isinstance(tasks, list) or not 1 <= len(tasks) <= 16:
        fail("manifest task count is invalid")
    seen: set[str] = set()
    for task in tasks:
        if not isinstance(task, dict):
            fail("task must be one object")
        exact_fields(task, {"id", "initial_source", "initial_sha256", "candidate_source", "candidate_sha256", "envelope_source", "envelope_sha256", "only", "expect_edits", "verifiers"}, "task")
        task_id = task.get("id")
        if not isinstance(task_id, str) or NAME_RE.fullmatch(task_id) is None or task_id in seen:
            fail("task id is invalid or duplicated")
        seen.add(task_id)
        for source_key, hash_key in (("initial_source", "initial_sha256"), ("candidate_source", "candidate_sha256"), ("envelope_source", "envelope_sha256")):
            expected = require_sha(task.get(hash_key), hash_key)
            verify_asset(task.get(source_key, ""), expected)
        if task.get("only") != ["proof.txt"] or task.get("expect_edits") is not True:
            fail("task path policy is invalid")
        if task.get("verifiers") != ["exact-content", "diff-check"]:
            fail("task verifier policy is invalid")
    return value


def load_manifest() -> tuple[dict[str, Any], bytes]:
    raw = read_file(MANIFEST_PATH, "benchmark manifest")
    if read_file(ROOT_BENCH / "manifest.json", "root benchmark manifest") != raw:
        fail("root and portable manifests differ")
    return validate_manifest(strict_object(raw, "benchmark manifest")), raw


def validate_selection(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        fail("variant selection must be one object")
    try:
        validate_selection_record_shape(value)
    except SelectionError as exc:
        raise BenchmarkError("variant selection is not a canonical G1 record") from exc
    return value


def load_variant(path: Path) -> dict[str, Any]:
    raw = read_file(path, "variant", MAX_VARIANT)
    value = strict_object(raw, "variant")
    exact_fields(value, {"schema_version", "kind", "name", "selection", "persona"}, "variant")
    if value.get("schema_version") != 1 or value.get("kind") != "agy-worker-benchmark-variant-input":
        fail("variant version is unsupported")
    name = value.get("name")
    if not isinstance(name, str) or NAME_RE.fullmatch(name) is None:
        fail("variant name is invalid")
    selection = validate_selection(value.get("selection"))
    persona = value.get("persona")
    persona_record = None
    if persona is not None:
        if not isinstance(persona, dict):
            fail("persona source must be one object")
        exact_fields(persona, {"name", "source"}, "persona source")
        persona_name = persona.get("name")
        source = persona.get("source")
        if not isinstance(persona_name, str) or NAME_RE.fullmatch(persona_name) is None:
            fail("persona name is invalid")
        if not isinstance(source, str):
            fail("persona source path is invalid")
        source_path = Path(source)
        if not source_path.is_absolute() or source_path != Path(os.path.realpath(source_path)):
            fail("persona source must be canonical and absolute")
        persona_bytes = read_file(source_path, "persona source", MAX_VARIANT)
        persona_record = {"name": persona_name, "source_sha256": digest(persona_bytes)}
    return {"name": name, "source_sha256": digest(raw), "selection": selection, "selection_sha256": digest(canonical_bytes(selection)), "persona": persona_record}


def git_env() -> dict[str, str]:
    return {"PATH": "/usr/bin:/bin", "HOME": "/var/empty", "TMPDIR": "/tmp", "LANG": "C", "LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1", "GIT_TERMINAL_PROMPT": "0", "GIT_PAGER": "cat"}


def git(args: list[str], cwd: Path, *, maximum: int = 4096) -> bytes:
    command = ["/usr/bin/git", "-c", "core.hooksPath=/dev/null", "-c", "core.fsmonitor=false", "-c", "diff.external=", *args]
    try:
        result = subprocess.run(command, cwd=cwd, env=git_env(), stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise BenchmarkError("fixed git operation failed") from exc
    if result.returncode != 0 or result.stderr or len(result.stdout) > maximum:
        fail("fixed git operation failed")
    return result.stdout


def clean_source_authority() -> dict[str, str]:
    source_manifest, source_raw = load_portable_source()
    if CHECKOUT_MODE:
        top = git(["rev-parse", "--show-toplevel"], REPO_ROOT).decode("ascii").strip()
        if top != str(REPO_ROOT):
            fail("benchmark runtime is not in its canonical checkout")
        revision = git(["rev-parse", "--verify", "HEAD^{commit}"], REPO_ROOT).decode("ascii").strip()
        if len(revision) != 40 or set(revision) - set("0123456789abcdef"):
            fail("source commit is invalid")
        if git(["status", "--porcelain=v1", "--untracked-files=all"], REPO_ROOT, maximum=MAX_STREAM):
            fail("source checkout must be clean before benchmark preparation")
        source_kind = "git-clean-commit"
    else:
        revision = source_manifest["source_revision"]
        source_kind = "portable-runtime"
    runner = read_file(Path(__file__).resolve(strict=True), "benchmark runner", MAX_JSON)
    qa = read_file(QA_GATE, "qa-gate", MAX_JSON)
    verify = read_file(VERIFY_JOB, "verify-job", MAX_JSON)
    return {"source_kind": source_kind, "source_revision": revision, "source_manifest_sha256": digest(source_raw), "benchmark_runner_sha256": digest(runner), "qa_gate_sha256": digest(qa), "verify_job_sha256": digest(verify), "plan_schema_sha256": digest(read_file(PLAN_SCHEMA, "plan schema", MAX_JSON)), "result_schema_sha256": digest(read_file(RESULT_SCHEMA, "result schema", MAX_JSON)), "receipt_schema_sha256": digest(read_file(RECEIPT_SCHEMA, "receipt schema", MAX_JSON))}


def canonical_external_root(path: Path) -> Path:
    if not path.is_absolute() or path != Path(os.path.realpath(path)) or path.is_symlink():
        fail("result root must be canonical, absolute, and real")
    try:
        st = path.stat()
    except OSError as exc:
        raise BenchmarkError("result root is unavailable") from exc
    if not stat.S_ISDIR(st.st_mode) or st.st_uid != os.getuid() or stat.S_IMODE(st.st_mode) != 0o700:
        fail("result root must be an owner-only directory")
    root_real = Path(os.path.realpath(REPO_ROOT if CHECKOUT_MODE else RUNTIME.parent))
    if path == root_real or root_real in path.parents or path in root_real.parents:
        fail("result root must be external to the repository")
    return path


def publish_new(root: Path, name: str, payload: bytes) -> tuple[Path, str]:
    if "/" in name or name in {"", ".", ".."}:
        fail("publication name is invalid")
    final = root / name
    if final.exists() or final.is_symlink():
        fail("benchmark publication never overwrites")
    fd = os.open(root, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_CLOEXEC", 0))
    temp = "." + name + "." + secrets.token_hex(12) + ".tmp"
    temp_fd = -1
    identity: tuple[int, int] | None = None
    try:
        create_mask = signal.pthread_sigmask(signal.SIG_BLOCK, SIGNALS) if hasattr(signal, "pthread_sigmask") else None
        try:
            temp_fd = os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_CLOEXEC", 0), 0o600, dir_fd=fd)
        finally:
            if create_mask is not None: signal.pthread_sigmask(signal.SIG_SETMASK, create_mask)
        os.fchmod(temp_fd, 0o600)
        view = memoryview(payload)
        while view:
            count = os.write(temp_fd, view)
            if count <= 0:
                fail("publication write failed")
            view = view[count:]
        os.fsync(temp_fd)
        st = os.fstat(temp_fd)
        identity = (st.st_dev, st.st_ino)
        os.close(temp_fd); temp_fd = -1
        link_mask = signal.pthread_sigmask(signal.SIG_BLOCK, SIGNALS) if hasattr(signal, "pthread_sigmask") else None
        try:
            os.link(temp, name, src_dir_fd=fd, dst_dir_fd=fd, follow_symlinks=False)
            current = os.stat(name, dir_fd=fd, follow_symlinks=False)
        finally:
            if link_mask is not None: signal.pthread_sigmask(signal.SIG_SETMASK, link_mask)
        if (current.st_dev, current.st_ino) != identity or stat.S_IMODE(current.st_mode) != 0o600:
            fail("publication identity changed")
        os.fsync(fd)
        os.unlink(temp, dir_fd=fd)
        os.fsync(fd)
        ACTIVE_PUBLICATIONS.append((root, name, identity))
        return final, digest(payload)
    except BaseException:
        if temp_fd >= 0:
            os.close(temp_fd)
        # A lifecycle signal may arrive after link(2) succeeds but before the
        # Python returns from the wrapper call. Inspect both names by the staged
        # inode rather than trusting post-syscall bookkeeping.
        for target in [name, temp]:
            try:
                current = os.stat(target, dir_fd=fd, follow_symlinks=False)
                if identity is None or (current.st_dev, current.st_ino) == identity:
                    os.unlink(target, dir_fd=fd)
            except FileNotFoundError:
                pass
            except OSError:
                pass
        try: os.fsync(fd)
        except OSError: pass
        raise
    finally:
        os.close(fd)


def rollback_publications() -> None:
    if hasattr(signal, "pthread_sigmask"): signal.pthread_sigmask(signal.SIG_BLOCK, SIGNALS)
    while ACTIVE_PUBLICATIONS:
        root, name, identity = ACTIVE_PUBLICATIONS.pop()
        try:
            fd = os.open(root, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_CLOEXEC", 0))
        except OSError:
            continue
        try:
            try: current = os.stat(name, dir_fd=fd, follow_symlinks=False)
            except FileNotFoundError: continue
            if stat.S_ISREG(current.st_mode) and (current.st_dev, current.st_ino) == identity:
                os.unlink(name, dir_fd=fd); os.fsync(fd)
        finally:
            os.close(fd)


def plan_value(variants: list[dict[str, Any]]) -> dict[str, Any]:
    manifest, manifest_raw = load_manifest()
    authority = clean_source_authority()
    authority["manifest_sha256"] = digest(manifest_raw)
    fixture_payload = b"".join(read_file(BENCH_ROOT / task[key], "fixture", 65536) for task in manifest["tasks"] for key in ("initial_source", "candidate_source", "envelope_source"))
    authority["fixture_set_sha256"] = digest(fixture_payload)
    tasks = [{key: task[key] for key in ("id", "initial_sha256", "candidate_sha256", "envelope_sha256", "only", "expect_edits", "verifiers")} for task in manifest["tasks"]]
    return {
        "schema_version": 1,
        "kind": "agy-worker-benchmark-plan",
        "manifest_sha256": digest(manifest_raw),
        "tool_authority": authority,
        "policy": {"mode": "offline-synthetic", "attempts_per_variant_task": 1, "gate_authority": "qa-gate", "live_execution": False, "network": False, "provider": False, "ranking": False, "routing": False, "recommendation": False, "driver_duration": "diagnostic-only-not-recorded"},
        "tasks": tasks,
        "variants": variants,
        "expected_runs": len(tasks) * len(variants),
        "integrity": {"signed": False, "tamper_evident": False},
    }


def validate_plan(value: dict[str, Any], raw: bytes) -> dict[str, Any]:
    try: validate_schema(value, load_schema(PLAN_SCHEMA))
    except ValidationFailure as exc: raise BenchmarkError("plan schema validation failed") from exc
    exact_fields(value, {"schema_version", "kind", "manifest_sha256", "tool_authority", "policy", "tasks", "variants", "expected_runs", "integrity"}, "plan")
    if value.get("schema_version") != 1 or value.get("kind") != "agy-worker-benchmark-plan":
        fail("plan version is unsupported")
    manifest, manifest_raw = load_manifest()
    if value.get("manifest_sha256") != digest(manifest_raw):
        fail("plan manifest binding drifted")
    expected_policy = {"mode": "offline-synthetic", "attempts_per_variant_task": 1, "gate_authority": "qa-gate", "live_execution": False, "network": False, "provider": False, "ranking": False, "routing": False, "recommendation": False, "driver_duration": "diagnostic-only-not-recorded"}
    if value.get("policy") != expected_policy or value.get("integrity") != {"signed": False, "tamper_evident": False}:
        fail("plan policy is invalid")
    authority = value.get("tool_authority")
    if not isinstance(authority, dict):
        fail("plan tool authority is missing")
    exact_fields(authority, {"source_kind", "source_revision", "source_manifest_sha256", "benchmark_runner_sha256", "qa_gate_sha256", "verify_job_sha256", "plan_schema_sha256", "result_schema_sha256", "receipt_schema_sha256", "manifest_sha256", "fixture_set_sha256"}, "tool authority")
    for key in authority:
        if key not in {"source_kind", "source_revision"}: require_sha(authority[key], key)
    if authority.get("source_kind") not in {"git-clean-commit", "portable-runtime"}:
        fail("plan source kind is invalid")
    revision = authority.get("source_revision")
    expected_source_kind = "git-clean-commit" if CHECKOUT_MODE else "portable-runtime"
    if authority["source_kind"] != expected_source_kind:
        fail("plan source kind does not match the runtime layout")
    if authority["source_kind"] == "git-clean-commit":
        if not isinstance(revision, str) or len(revision) != 40 or set(revision) - set("0123456789abcdef"):
            fail("plan source commit is invalid")
    elif revision != PORTABLE_REVISION:
        fail("plan portable source revision is invalid")
    _source, source_raw = load_portable_source()
    current = {
        "benchmark_runner_sha256": digest(read_file(Path(__file__).resolve(strict=True), "benchmark runner", MAX_JSON)),
        "qa_gate_sha256": digest(read_file(QA_GATE, "qa-gate", MAX_JSON)),
        "verify_job_sha256": digest(read_file(VERIFY_JOB, "verify-job", MAX_JSON)),
        "plan_schema_sha256": digest(read_file(PLAN_SCHEMA, "plan schema", MAX_JSON)),
        "result_schema_sha256": digest(read_file(RESULT_SCHEMA, "result schema", MAX_JSON)),
        "receipt_schema_sha256": digest(read_file(RECEIPT_SCHEMA, "receipt schema", MAX_JSON)),
        "source_manifest_sha256": digest(source_raw),
        "manifest_sha256": digest(manifest_raw),
    }
    if any(authority.get(key) != expected for key, expected in current.items()):
        fail("plan tool authority no longer matches")
    fixture_payload = b"".join(read_file(BENCH_ROOT / task[key], "fixture", 65536) for task in manifest["tasks"] for key in ("initial_source", "candidate_source", "envelope_source"))
    if authority.get("fixture_set_sha256") != digest(fixture_payload):
        fail("plan fixture authority no longer matches")
    tasks = value.get("tasks")
    expected_tasks = [{key: task[key] for key in ("id", "initial_sha256", "candidate_sha256", "envelope_sha256", "only", "expect_edits", "verifiers")} for task in manifest["tasks"]]
    if tasks != expected_tasks:
        fail("plan task registration is invalid")
    variants = value.get("variants")
    if not isinstance(variants, list) or not 1 <= len(variants) <= manifest["limits"]["max_variants"]:
        fail("plan variant count is invalid")
    names: set[str] = set()
    for variant in variants:
        if not isinstance(variant, dict): fail("plan variant is invalid")
        exact_fields(variant, {"name", "source_sha256", "selection", "selection_sha256", "persona"}, "plan variant")
        name = variant.get("name")
        if not isinstance(name, str) or NAME_RE.fullmatch(name) is None or name in names:
            fail("plan variant name is invalid or duplicated")
        names.add(name)
        require_sha(variant.get("source_sha256"), "variant source")
        selection = validate_selection(variant.get("selection"))
        if variant.get("selection_sha256") != digest(canonical_bytes(selection)):
            fail("plan selection binding drifted")
        persona = variant.get("persona")
        if persona is not None:
            if not isinstance(persona, dict): fail("plan persona is invalid")
            exact_fields(persona, {"name", "source_sha256"}, "plan persona")
            if not isinstance(persona.get("name"), str) or NAME_RE.fullmatch(persona["name"]) is None:
                fail("plan persona name is invalid")
            require_sha(persona.get("source_sha256"), "persona source")
    expected_runs = len(tasks) * len(variants)
    if value.get("expected_runs") != expected_runs or not 1 <= expected_runs <= manifest["limits"]["max_runs"]:
        fail("plan run count is invalid")
    if raw != canonical_bytes(value):
        fail("plan bytes are not canonical")
    return value


def load_plan(path: Path) -> tuple[dict[str, Any], bytes]:
    raw = read_file(path, "benchmark plan", MAX_JSON)
    return validate_plan(strict_object(raw, "benchmark plan"), raw), raw


def _group_exists(pid: int) -> bool:
    try: os.killpg(pid, 0)
    except ProcessLookupError: return False
    except PermissionError: return True
    return True


def _close_group(process: subprocess.Popen[bytes]) -> int:
    # Keep the leader unreaped as its PGID reservation until all group signalling ends.
    try: os.killpg(process.pid, signal.SIGTERM)
    except (ProcessLookupError, PermissionError): pass
    deadline = time.monotonic() + 0.25
    while _group_exists(process.pid) and time.monotonic() < deadline:
        time.sleep(0.01)
    if _group_exists(process.pid):
        try: os.killpg(process.pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError): pass
    return process.wait(timeout=1.0)


def _leader_exited_unreaped(process: subprocess.Popen[bytes]) -> bool:
    if _WAITID is None or not all(hasattr(os, name) for name in ("P_PID", "WEXITED", "WNOHANG", "WNOWAIT")):
        fail("non-reaping process observation is unavailable")
    information = (ctypes.c_ubyte * 256)()
    ctypes.set_errno(0)
    result = _WAITID(os.P_PID, process.pid, ctypes.byref(information), os.WEXITED | os.WNOHANG | os.WNOWAIT)
    if result != 0:
        fail("non-reaping child observation failed")
    return any(information)


def run_bounded(argv: list[str], cwd: Path, timeout: float = RUN_TIMEOUT) -> tuple[int, bytes, bytes]:
    process: subprocess.Popen[bytes] | None = None
    old = {item: signal.getsignal(item) for item in SIGNALS}
    def hit(number: int, frame: Any) -> None:
        del frame
        raise Interrupted(number)
    for item in SIGNALS: signal.signal(item, hit)
    try:
        launch_mask = signal.pthread_sigmask(signal.SIG_BLOCK, SIGNALS) if hasattr(signal, "pthread_sigmask") else None
        try:
            process = subprocess.Popen(argv, cwd=cwd, env=git_env(), stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
        except OSError as exc:
            raise BenchmarkError("benchmark gate could not start") from exc
        finally:
            if launch_mask is not None: signal.pthread_sigmask(signal.SIG_SETMASK, launch_mask)
        assert process.stdout is not None and process.stderr is not None
        stdout_fd, stderr_fd = process.stdout.fileno(), process.stderr.fileno()
        buffers = {stdout_fd: bytearray(), stderr_fd: bytearray()}
        streams = {stdout_fd: process.stdout, stderr_fd: process.stderr}
        deadline = time.monotonic() + timeout
        with selectors.DefaultSelector() as selector:
            for fd in streams:
                os.set_blocking(fd, False); selector.register(fd, selectors.EVENT_READ)
            while True:
                left = deadline - time.monotonic()
                if left <= 0: raise BenchmarkError("benchmark gate timed out")
                events = selector.select(min(0.05, left)) if selector.get_map() else ()
                for key, _ in events:
                    data = os.read(key.fd, 8192)
                    if not data:
                        selector.unregister(key.fd); streams[key.fd].close(); continue
                    buffers[key.fd].extend(data)
                    if len(buffers[key.fd]) > MAX_STREAM: raise BenchmarkError("benchmark gate output exceeded its bound")
                if _leader_exited_unreaped(process):
                    break
                if not events: time.sleep(min(0.01, left))
        wait_mask = signal.pthread_sigmask(signal.SIG_BLOCK, SIGNALS) if hasattr(signal, "pthread_sigmask") else None
        try:
            rc = _close_group(process)
            process = None
        finally:
            if wait_mask is not None: signal.pthread_sigmask(signal.SIG_SETMASK, wait_mask)
        # The closed group cannot write again. Drain only already-buffered bytes.
        for fd, stream in streams.items():
            if stream.closed: continue
            while True:
                try: data = os.read(fd, 8192)
                except BlockingIOError: break
                if not data: break
                buffers[fd].extend(data)
                if len(buffers[fd]) > MAX_STREAM: raise BenchmarkError("benchmark gate output exceeded its bound")
            stream.close()
        return rc, bytes(buffers[stdout_fd]), bytes(buffers[stderr_fd])
    except Interrupted as exc:
        if hasattr(signal, "pthread_sigmask"): signal.pthread_sigmask(signal.SIG_BLOCK, SIGNALS)
        if process is not None:
            try: _close_group(process)
            except BaseException: raise BenchmarkError("benchmark gate cleanup failed")
            process = None
        raise
    except BaseException:
        if hasattr(signal, "pthread_sigmask"): signal.pthread_sigmask(signal.SIG_BLOCK, SIGNALS)
        if process is not None:
            try: _close_group(process)
            except BaseException: pass
        raise
    finally:
        for item, handler in old.items(): signal.signal(item, handler)


def shell_quote(value: str) -> str:
    return "'" + value.replace("'", "'\"'\"'") + "'"


def init_fixture(work: Path, initial: bytes, candidate: bytes) -> tuple[Path, str]:
    repo = work / "repo"
    repo.mkdir(mode=0o700)
    git(["init", "-q", "-b", "main"], repo)
    git(["config", "user.name", "benchmark"], repo)
    git(["config", "user.email", "benchmark@example.invalid"], repo)
    (repo / "proof.txt").write_bytes(initial)
    git(["add", "--", "proof.txt"], repo)
    git(["commit", "-q", "-m", "benchmark base"], repo)
    base = git(["rev-parse", "HEAD"], repo).decode("ascii").strip()
    (repo / "proof.txt").write_bytes(candidate)
    return repo, base


def validate_result(value: dict[str, Any], raw: bytes, plan: dict[str, Any], plan_raw: bytes, root: Path) -> dict[str, Any]:
    try: validate_schema(value, load_schema(RESULT_SCHEMA))
    except ValidationFailure as exc: raise BenchmarkError("result schema validation failed") from exc
    exact_fields(value, {"schema_version", "kind", "plan_sha256", "manifest_sha256", "policy", "complete", "runs", "integrity"}, "result")
    if value.get("schema_version") != 1 or value.get("kind") != "agy-worker-benchmark-result": fail("result version is unsupported")
    if value.get("plan_sha256") != digest(plan_raw) or value.get("manifest_sha256") != plan["manifest_sha256"]: fail("result plan binding is invalid")
    if value.get("policy") != {"mode": "offline-synthetic", "attempts_per_variant_task": 1, "gate_authority": "qa-gate", "live_execution": False, "network": False, "provider": False, "ranking": False, "routing": False, "recommendation": False}: fail("result policy is invalid")
    if value.get("complete") is not True or value.get("integrity") != {"signed": False, "tamper_evident": False}: fail("result completion is invalid")
    runs = value.get("runs")
    if not isinstance(runs, list) or len(runs) != plan["expected_runs"]: fail("result is incomplete")
    expected_pairs = [(variant["name"], task["id"]) for variant in plan["variants"] for task in plan["tasks"]]
    schema = load_schema(RECEIPT_SCHEMA)
    for index, (run, pair) in enumerate(zip(runs, expected_pairs), 1):
        if not isinstance(run, dict): fail("result run is invalid")
        exact_fields(run, {"sequence", "variant", "task", "attempt", "receipt_name", "receipt_sha256", "gate_exit", "gate_outcome", "verdict", "resolved_base", "initial_candidate_state_sha256", "final_candidate_state_sha256", "selection_sha256"}, "result run")
        if (run.get("variant"), run.get("task")) != pair or run.get("sequence") != index or run.get("attempt") != 1: fail("result run ordering is invalid")
        name = run.get("receipt_name")
        if name != f"receipt-{index:03d}.json": fail("result receipt name is invalid")
        receipt_raw = read_file(root / name, "benchmark receipt", MAX_JSON)
        if digest(receipt_raw) != require_sha(run.get("receipt_sha256"), "receipt_sha256"): fail("result receipt digest drifted")
        try: receipt = validate_receipt(strict_object(receipt_raw, "benchmark receipt"), schema)
        except ValidationFailure as exc: raise BenchmarkError("benchmark receipt is invalid") from exc
        for key in ("gate_exit", "gate_outcome", "verdict", "resolved_base", "initial_candidate_state_sha256", "final_candidate_state_sha256"):
            if run.get(key) != receipt.get(key): fail("result receipt facts drifted")
        variant = plan["variants"][(index - 1) // len(plan["tasks"])]
        if receipt.get("caller_selection") != variant["selection"] or run.get("selection_sha256") != variant["selection_sha256"]: fail("result selection binding drifted")
        if receipt.get("recommendations_participated_in_acceptance") is not False: fail("recommendation affected benchmark gate")
    if raw != canonical_bytes(value): fail("result bytes are not canonical")
    return value


def command_prepare(args: argparse.Namespace) -> dict[str, Any]:
    root = canonical_external_root(Path(args.result_root))
    if not args.variant:
        fail("prepare requires at least one ordered --variant")
    variants = [load_variant(Path(item)) for item in args.variant]
    if len({item["name"] for item in variants}) != len(variants):
        fail("variant names must be unique")
    plan = plan_value(variants)
    payload = canonical_bytes(plan)
    validate_plan(plan, payload)
    _path, sha = publish_new(root, "plan.v1.json", payload)
    return {"kind": "agy-worker-benchmark-prepare", "plan_sha256": sha, "runs": plan["expected_runs"], "status": "prepared"}


def _remove_owned(path: Path) -> None:
    if path.exists() and not path.is_symlink():
        shutil.rmtree(path)


def command_run(args: argparse.Namespace) -> dict[str, Any]:
    plan_path = Path(args.plan)
    if not plan_path.is_absolute() or plan_path != Path(os.path.realpath(plan_path)):
        fail("--plan must be one canonical absolute path")
    root = canonical_external_root(plan_path.parent)
    if plan_path.name != "plan.v1.json": fail("plan name is invalid")
    plan, plan_raw = load_plan(plan_path)
    current_authority = clean_source_authority()
    if any(plan["tool_authority"].get(key) != value for key, value in current_authority.items()):
        fail("run source authority differs from the prepared plan")
    if (root / "result.v1.json").exists() or (root / "result.v1.json").is_symlink(): fail("benchmark result already exists")
    manifest, _ = load_manifest()
    task_by_id = {item["id"]: item for item in manifest["tasks"]}
    work = Path(tempfile.mkdtemp(prefix="agy-benchmark.", dir=str(root)))
    os.chmod(work, 0o700)
    created_receipts: list[Path] = []
    runs: list[dict[str, Any]] = []
    try:
        sequence = 0
        for variant in plan["variants"]:
            for planned_task in plan["tasks"]:
                sequence += 1
                task = task_by_id[planned_task["id"]]
                case = work / f"case-{sequence:03d}"
                case.mkdir(mode=0o700)
                repo, base = init_fixture(case, verify_asset(task["initial_source"], task["initial_sha256"]), verify_asset(task["candidate_source"], task["candidate_sha256"]))
                selection_path = case / "selection.json"
                selection_path.write_bytes(canonical_bytes(variant["selection"])); os.chmod(selection_path, 0o600)
                receipt_name = f"receipt-{sequence:03d}.json"
                receipt_path = root / receipt_name
                if receipt_path.exists() or receipt_path.is_symlink(): fail("benchmark receipt collision")
                created_receipts.append(receipt_path)
                candidate_path = (BENCH_ROOT / task["candidate_source"]).resolve(strict=True)
                verify_content = json.dumps([
                    "/usr/bin/python3", "-I", "-S", "-B", "-c",
                    "import pathlib,sys;sys.exit(0 if pathlib.Path(sys.argv[1]).read_bytes()==pathlib.Path(sys.argv[2]).read_bytes() else 1)",
                    str(repo / "proof.txt"), str(candidate_path),
                ], ensure_ascii=True, separators=(",", ":"))
                verify_diff = json.dumps([
                    "/usr/bin/git", "-C", str(repo), "diff", "--check", base,
                    "--", "proof.txt",
                ], ensure_ascii=True, separators=(",", ":"))
                argv = [str(VERIFY_JOB), "--receipt", str(receipt_path), "--envelope", str((BENCH_ROOT / task["envelope_source"]).resolve(strict=True)), "--repo", str(repo), "--base", base, "--only", "proof.txt", "--expect-edits", "--selection", str(selection_path), "--verify-argv", verify_content, "--verify-argv", verify_diff]
                started = time.monotonic()
                rc, stdout, stderr = run_bounded(argv, case)
                _duration_ms = int((time.monotonic() - started) * 1000)  # diagnostic only; intentionally not recorded
                if rc not in {0, 10, 11, 12, 13, 14, 15} or stdout:
                    fail("benchmark gate returned an unreceiptable result")
                if not receipt_path.is_file() or receipt_path.is_symlink():
                    fail("benchmark gate did not publish a receipt")
                # The gate owns stderr diagnostics. Do not persist or repeat them.
                del stderr
                receipt_raw = read_file(receipt_path, "benchmark receipt", MAX_JSON)
                schema = load_schema(RECEIPT_SCHEMA)
                try: receipt = validate_receipt(strict_object(receipt_raw, "benchmark receipt"), schema)
                except ValidationFailure as exc: raise BenchmarkError("benchmark receipt is invalid") from exc
                if receipt["gate_exit"] != rc or receipt.get("caller_selection") != variant["selection"]:
                    fail("benchmark receipt does not bind the gate invocation")
                runs.append({"sequence": sequence, "variant": variant["name"], "task": task["id"], "attempt": 1, "receipt_name": receipt_name, "receipt_sha256": digest(receipt_raw), "gate_exit": receipt["gate_exit"], "gate_outcome": receipt["gate_outcome"], "verdict": receipt["verdict"], "resolved_base": receipt["resolved_base"], "initial_candidate_state_sha256": receipt["initial_candidate_state_sha256"], "final_candidate_state_sha256": receipt["final_candidate_state_sha256"], "selection_sha256": variant["selection_sha256"]})
        result = {"schema_version": 1, "kind": "agy-worker-benchmark-result", "plan_sha256": digest(plan_raw), "manifest_sha256": plan["manifest_sha256"], "policy": {"mode": "offline-synthetic", "attempts_per_variant_task": 1, "gate_authority": "qa-gate", "live_execution": False, "network": False, "provider": False, "ranking": False, "routing": False, "recommendation": False}, "complete": True, "runs": runs, "integrity": {"signed": False, "tamper_evident": False}}
        payload = canonical_bytes(result)
        validate_result(result, payload, plan, plan_raw, root)
        _path, sha = publish_new(root, "result.v1.json", payload)
        return {"kind": "agy-worker-benchmark-run", "result_sha256": sha, "runs": len(runs), "status": "complete"}
    except BaseException:
        if hasattr(signal, "pthread_sigmask"): signal.pthread_sigmask(signal.SIG_BLOCK, SIGNALS)
        # A partial run is not a result. Exact receipts are rolled back by name.
        for path in created_receipts:
            try: path.unlink()
            except OSError: pass
        root_fd = -1
        try:
            root_fd = os.open(root, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
            os.fsync(root_fd)
        except OSError:
            pass
        finally:
            if root_fd >= 0: os.close(root_fd)
        raise
    finally:
        _remove_owned(work)


def command_report(args: argparse.Namespace) -> dict[str, Any]:
    plan_path = Path(args.plan); result_path = Path(args.result)
    if not plan_path.is_absolute() or plan_path != Path(os.path.realpath(plan_path)): fail("--plan must be canonical")
    if not result_path.is_absolute() or result_path != Path(os.path.realpath(result_path)): fail("--result must be canonical")
    if plan_path.parent != result_path.parent or plan_path.name != "plan.v1.json" or result_path.name != "result.v1.json": fail("report inputs must share their canonical result root")
    root = canonical_external_root(plan_path.parent)
    plan_raw = read_file(plan_path, "benchmark plan", MAX_JSON)
    plan = validate_plan(strict_object(plan_raw, "benchmark plan"), plan_raw)
    result_raw = read_file(result_path, "benchmark result", MAX_JSON)
    result = validate_result(strict_object(result_raw, "benchmark result"), result_raw, plan, plan_raw, root)
    facts = []
    for run in result["runs"]:
        facts.append({"sequence": run["sequence"], "variant": run["variant"], "task": run["task"], "attempt": 1, "gate_exit": run["gate_exit"], "gate_outcome": run["gate_outcome"], "verdict": run["verdict"]})
    return {"schema_version": 1, "kind": "agy-worker-benchmark-report", "plan_sha256": digest(plan_raw), "result_sha256": digest(result_raw), "complete": True, "expected_runs": plan["expected_runs"], "observed_runs": len(facts), "facts": facts, "ranking": False, "winner": None, "recommendation": None}


def parser() -> argparse.ArgumentParser:
    result = Parser(prog="benchmark.sh", description="provider-independent offline Benchmark v1")
    sub = result.add_subparsers(dest="command", required=True)
    prepare = sub.add_parser("prepare"); prepare.add_argument("--result-root", required=True); prepare.add_argument("--variant", action="append", default=[])
    run = sub.add_parser("run"); run.add_argument("--plan", required=True)
    report = sub.add_parser("report"); report.add_argument("--plan", required=True); report.add_argument("--result", required=True)
    return result


def main(argv: list[str]) -> int:
    try:
        args = parser().parse_args(argv)
        if args.command == "prepare": output = command_prepare(args)
        elif args.command == "run": output = command_run(args)
        else: output = command_report(args)
        sys.stdout.buffer.write(canonical_bytes(output)); sys.stdout.buffer.flush()
        return 0
    except Interrupted as exc:
        print("benchmark: interrupted", file=sys.stderr)
        return 128 + exc.number
    except (BenchmarkError, ValidationFailure, OSError, subprocess.SubprocessError):
        print("benchmark: operation rejected", file=sys.stderr)
        return 2


def cli(argv: list[str]) -> NoReturn:
    old = {item: signal.getsignal(item) for item in SIGNALS}
    def hit(number: int, frame: Any) -> None:
        del frame
        raise Interrupted(number)
    prior = signal.pthread_sigmask(signal.SIG_BLOCK, SIGNALS) if hasattr(signal, "pthread_sigmask") else None
    for item in SIGNALS: signal.signal(item, hit)
    if prior is not None: signal.pthread_sigmask(signal.SIG_SETMASK, prior)
    try:
        validate_source_contract(Path(__file__).read_bytes())
        code = main(argv)
        if code != 0:
            rollback_publications()
            os._exit(code)
        sys.stdout.flush(); sys.stderr.flush()
        # Process-owning success: handlers and publication ownership remain active
        # through termination, leaving no restore/return race after durable output.
        os._exit(0)
    except Interrupted as exc:
        rollback_publications()
        os.write(2, b"benchmark: interrupted\n")
        os._exit(128 + exc.number)
    except SystemExit as exc:
        rollback_publications()
        sys.stdout.flush(); sys.stderr.flush()
        os._exit(int(exc.code) if isinstance(exc.code, int) else 2)
    except BaseException:
        rollback_publications()
        os.write(2, b"benchmark: operation rejected\n")
        os._exit(2)
    finally:
        # Only test doubles that replace os._exit can reach this restoration.
        for item, handler in old.items(): signal.signal(item, handler)


if __name__ == "__main__":
    cli(sys.argv[1:])
