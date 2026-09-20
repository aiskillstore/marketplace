#!/usr/bin/env python3
"""Resolve one explicit, reviewed model selection and record driver provenance."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import select
import shutil
import signal
import stat
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

import compatibility


RUNTIME_ROOT = Path(__file__).resolve().parents[1]
COMPAT_ROOT = RUNTIME_ROOT / "compat"
MATRIX_PATH = COMPAT_ROOT / "agy-model-effort-matrix.json"
MATRIX_SCHEMA_PATH = COMPAT_ROOT / "model-effort-matrix.schema.json"
MATRIX_SHA_PATH = COMPAT_ROOT / "agy-model-effort-matrix.sha256"
INVENTORY_BINDING_PATH = COMPAT_ROOT / "agy-models-inventory-binding.json"
INVENTORY_BINDING_SHA_PATH = COMPAT_ROOT / "agy-models-inventory-binding.sha256"
VERSION_PATH = COMPAT_ROOT / "agy-verified-version.txt"
SOURCE_PATH = COMPAT_ROOT / "agy-upstream-head.txt"
SHA256_RE = re.compile(r"[0-9a-f]{64}")
SOURCE_NAMES = ("cli", "environment")
TIER_SOURCES = ("cli", "environment", "implicit-default")
CHILD_ENV_BASE = ("HOME", "PATH", "TMPDIR", "LANG", "LANGUAGE")
CHILD_ENV_LOCALES = (
    "LC_ALL", "LC_CTYPE", "LC_NUMERIC", "LC_TIME", "LC_COLLATE",
    "LC_MONETARY", "LC_MESSAGES", "LC_PAPER", "LC_NAME", "LC_ADDRESS",
    "LC_TELEPHONE", "LC_MEASUREMENT", "LC_IDENTIFICATION",
)
ENV_NAME_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]{0,127}")
BLOCKED_ENV_NAMES = {
    "BASH_ENV", "ENV", "SHELLOPTS", "BASHOPTS", "PS4", "CDPATH",
    "GLOBIGNORE", "BASH_LOADABLES_PATH", "BASH_XTRACEFD", "BASH_COMPAT",
    "NODE_OPTIONS", "RUBYOPT", "RUBYLIB", "PERL5OPT", "PERL5LIB",
    "JAVA_TOOL_OPTIONS", "JDK_JAVA_OPTIONS", "CLASSPATH",
    "AGY_WORKER_SCHEMA",
}
BLOCKED_ENV_PREFIXES = (
    "BASH_FUNC_", "PYTHON", "LD_", "DYLD_", "GIT_", "AGY_WORKER_INTERNAL_",
)
ACTIVE_CHILD_ENV: list[str] = []
VERSION_TIMEOUT_SECONDS = 3.0
VERSION_OUTPUT_LIMIT = 128
HELP_TIMEOUT_SECONDS = 3.0
HELP_OUTPUT_LIMIT = 64 * 1024
POLICY_FILE_LIMIT = 256 * 1024
# The current agy 1.1.17 macOS executable is 177,517,056 bytes.  Keep a
# finite pre-task hashing bound while leaving enough room for a near-term
# executable growth without weakening the descriptor identity checks.
EXECUTABLE_CONTENT_LIMIT = 512 * 1024 * 1024
VERSION_RE = re.compile(r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)")
REVISION_RE = re.compile(r"[0-9a-f]{40}")
LITERAL_MODEL_RE = re.compile(r"[a-z0-9]+(?:[.-][a-z0-9]+)+")
TIER_MODEL_BY_NAME = {
    "bulk": "gemini-3.6-flash-medium",
    "cheap": "gemini-3.6-flash-low",
    "hard": "gemini-3.1-pro-high",
    "hardest": "claude-opus-4-6-thinking",
}


def validate_child_environment_names(names: list[str]) -> list[str]:
    if len(names) > 64:
        raise EvidenceUnavailable("too many explicit child environment names")
    if len(set(names)) != len(names):
        raise EvidenceUnavailable("explicit child environment names must be unique")
    for name in names:
        if (
            ENV_NAME_RE.fullmatch(name) is None
            or name in BLOCKED_ENV_NAMES
            or any(name.startswith(prefix) for prefix in BLOCKED_ENV_PREFIXES)
        ):
            raise EvidenceUnavailable("explicit child environment name is unsafe")
    return sorted(names)


def child_environment(
    explicit_names: list[str] | None = None, *, force_c_locale: bool = False,
) -> dict[str, str]:
    names = validate_child_environment_names(
        ACTIVE_CHILD_ENV if explicit_names is None else explicit_names
    )
    allowed = set(CHILD_ENV_BASE) | set(CHILD_ENV_LOCALES) | set(names)
    environment = {name: os.environ[name] for name in allowed if name in os.environ}
    if force_c_locale:
        environment["LC_ALL"] = "C"
    return environment
COMMON_RECORD_FIELDS = {"schema_version", "kind", "selection_mode"}
TIER_RECORD_FIELDS = COMMON_RECORD_FIELDS | {
    "selected_tier",
    "selected_tier_source",
    "resolved_agy_model",
}
DIRECT_V1_RECORD_FIELDS = COMMON_RECORD_FIELDS | {
    "user_model",
    "user_model_source",
    "resolved_agy_model",
    "installed_agy_version",
    "matrix_sha256",
    "matrix_agy_version",
    "matrix_source_revision",
}
EFFORT_V1_RECORD_FIELDS = DIRECT_V1_RECORD_FIELDS | {"user_effort", "user_effort_source"}
DIRECT_V2_PROBE_FIELDS = {
    "installed_agy_version",
    "matrix_sha256",
    "matrix_agy_version",
    "matrix_source_revision",
    "version_relation",
    "compatibility_status",
    "critical_interface_probe_version",
    "critical_interface_status",
    "critical_capabilities_sha256",
    "help_sha256",
    "model_availability",
    "probed_executable",
}
DIRECT_V2_RECORD_FIELDS = (COMMON_RECORD_FIELDS | {
    "user_model", "user_model_source", "resolved_agy_model",
} | DIRECT_V2_PROBE_FIELDS)
EFFORT_V2_RECORD_FIELDS = DIRECT_V2_RECORD_FIELDS | {"user_effort", "user_effort_source"}
DIRECT_V3_DECISION_FIELDS = {
    "compatibility_disposition", "approved_help_sha256", "compatibility_decision_sha256",
}
DIRECT_V3_RECORD_FIELDS = DIRECT_V2_RECORD_FIELDS | DIRECT_V3_DECISION_FIELDS
EFFORT_V3_RECORD_FIELDS = DIRECT_V3_RECORD_FIELDS | {"user_effort", "user_effort_source"}
LITERAL_RECORD_FIELDS = COMMON_RECORD_FIELDS | {
    "user_model",
    "user_model_source",
    "resolved_agy_model",
    "compatibility_status",
}


class CallerError(ValueError):
    """The caller supplied an invalid or ambiguous selector."""


class ReviewRequired(ValueError):
    """Reviewed compatibility evidence drifted and needs Codex reconciliation."""

    def __init__(self, message: str, evidence: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.evidence = evidence


class EvidenceUnavailable(ValueError):
    """Required local evidence is missing, malformed, or could not be observed."""


class ProbeInterrupted(BaseException):
    """A terminal signal interrupted the bounded local version probe."""

    def __init__(self, signal_number: int) -> None:
        super().__init__(signal_number)
        self.signal_number = signal_number


CRITICAL_OPTIONS: dict[str, tuple[str, ...]] = {
    "--sandbox": (),
    "--mode": ("accept-edits", "plan"),
    "--print-timeout": (),
    "--output-format": ("stream-json",),
    "--json-schema": (),
    "--model": (),
    "--conversation": (),
    "--add-dir": (),
    "--disable-slash-commands": (),
    "--print": (),
}
CRITICAL_ENUM_VALUES: dict[str, frozenset[str]] = {
    "--mode": frozenset({"accept-edits", "plan"}),
    "--output-format": frozenset({"text", "json", "stream-json"}),
}

class UsageParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        self.print_usage(sys.stderr)
        self.exit(64, f"model-selection: {message}\n")


def one(parser: UsageParser, values: list[str] | None, flag: str, required: bool) -> str | None:
    if not values:
        if required:
            parser.error(f"{flag} is required")
        return None
    if len(values) != 1:
        parser.error(f"{flag} must be provided exactly once")
    if values[0] == "":
        parser.error(f"{flag} must not be empty")
    return values[0]


def read_bounded(path: Path) -> bytes:
    try:
        with path.open("rb") as handle:
            data = handle.read(POLICY_FILE_LIMIT + 1)
    except OSError as exc:
        raise EvidenceUnavailable(f"cannot read {path.name}") from exc
    if len(data) > POLICY_FILE_LIMIT:
        raise EvidenceUnavailable(f"{path.name} is oversized")
    return data


def read_policy_record(path: Path, kind: str) -> str:
    try:
        return compatibility.validate_record(kind, compatibility.read_record(path))
    except compatibility.CompatibilityError as exc:
        raise EvidenceUnavailable(str(exc)) from exc


def load_policy() -> tuple[dict[str, Any], str, str, str]:
    try:
        expected_sha = compatibility.read_record(MATRIX_SHA_PATH)
    except compatibility.CompatibilityError as exc:
        raise EvidenceUnavailable(str(exc)) from exc
    if SHA256_RE.fullmatch(expected_sha) is None:
        raise EvidenceUnavailable("malformed matrix SHA-256 record")

    matrix_bytes = read_bounded(MATRIX_PATH)
    actual_sha = hashlib.sha256(matrix_bytes).hexdigest()
    if actual_sha != expected_sha:
        raise EvidenceUnavailable("matrix SHA-256 does not match the reviewed record")

    try:
        matrix = compatibility.validate_matrix_structure(MATRIX_PATH, MATRIX_SCHEMA_PATH)
    except compatibility.CompatibilityError as exc:
        raise EvidenceUnavailable(str(exc)) from exc
    if hashlib.sha256(read_bounded(MATRIX_PATH)).hexdigest() != actual_sha:
        raise EvidenceUnavailable("matrix changed while it was being validated")

    version = read_policy_record(VERSION_PATH, "version")
    revision = read_policy_record(SOURCE_PATH, "revision")
    active, reason = compatibility.matrix_binding_state(matrix, version, revision)
    if not active:
        raise ReviewRequired(reason)
    try:
        compatibility.validate_inventory_binding(
            INVENTORY_BINDING_PATH,
            INVENTORY_BINDING_SHA_PATH,
            version,
            revision,
            matrix,
        )
    except compatibility.CompatibilityError as exc:
        raise EvidenceUnavailable(str(exc)) from exc
    return matrix, actual_sha, version, revision


def resolve_model(matrix: dict[str, Any], model: str, effort: str | None) -> tuple[str, str]:
    if compatibility.MODEL_RE.fullmatch(model) is None:
        raise CallerError("--model must be one exact reviewed lowercase model name")
    if effort is not None and effort not in compatibility.EFFORTS:
        raise CallerError("--effort must be exactly low, medium, or high")

    adjustable = {row["model"]: row for row in matrix["adjustable_models"]}
    resolved_outputs = {
        slug
        for row in matrix["adjustable_models"]
        for slug in row["resolutions"].values()
    }
    fixed = {row["model_slug"] for row in matrix["fixed_models"]}

    if effort is None:
        if model in adjustable:
            raise CallerError("an adjustable base model requires one explicit effort")
        if model in resolved_outputs or model in fixed:
            return model, "exact-model"
        raise CallerError("--model is not an exact reviewed model choice")

    if model in resolved_outputs or model in fixed:
        raise CallerError("compound and fixed model slugs do not accept --effort")
    row = adjustable.get(model)
    if row is None:
        raise CallerError("--model is not a reviewed adjustable base model")
    if effort in row["unsupported_efforts"]:
        raise CallerError(f"{model} does not advertise {effort}")
    resolved = row["resolutions"].get(effort)
    if not isinstance(resolved, str) or not resolved:
        raise EvidenceUnavailable("matrix has no exact reviewed output")
    return resolved, "model-effort"


def stop_process_group(process: subprocess.Popen[bytes]) -> None:
    """Terminate the entire probe process group and reap its leader."""

    try:
        os.killpg(process.pid, signal.SIGTERM)
    except (ProcessLookupError, PermissionError):
        pass
    try:
        process.wait(timeout=0.20)
    except subprocess.TimeoutExpired:
        pass
    # Send KILL even if the leader already exited: a descendant may still hold the
    # stdout pipe and remain in the probe's process group.
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        pass
    try:
        process.wait(timeout=0.50)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()


def capture_probe_output(
    process: subprocess.Popen[bytes], *, timeout: float, output_limit: int, label: str,
    use_stderr: bool = False,
) -> bytes:
    """Read one local probe incrementally under hard byte and wall-clock bounds."""

    stream = process.stderr if use_stderr else process.stdout
    if stream is None:
        stop_process_group(process)
        raise EvidenceUnavailable(f"agy {label} probe has no output pipe")
    descriptor = stream.fileno()
    os.set_blocking(descriptor, False)
    deadline = time.monotonic() + timeout
    captured = bytearray()
    eof = False

    def read_available() -> None:
        nonlocal eof
        while not eof:
            try:
                chunk = os.read(descriptor, output_limit + 1 - len(captured))
            except BlockingIOError:
                return
            if not chunk:
                eof = True
                return
            captured.extend(chunk)
            if len(captured) > output_limit:
                raise EvidenceUnavailable(f"agy {label} probe failed or was oversized")

    try:
        while True:
            # The leader's exit establishes the probe result.  A descendant can
            # inherit the combined output pipe indefinitely, so do not make a
            # valid completed probe depend on EOF from every group member.
            if process.poll() is not None:
                read_available()
                return bytes(captured)
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise EvidenceUnavailable(f"agy {label} probe failed or was oversized")
            readable: list[int] = []
            if not eof:
                try:
                    readable, _, _ = select.select(
                        [descriptor], [], [], min(remaining, 0.10)
                    )
                except InterruptedError:
                    continue
            if readable:
                read_available()
            elif eof:
                try:
                    process.wait(timeout=min(remaining, 0.10))
                except subprocess.TimeoutExpired:
                    continue
        return bytes(captured)
    finally:
        # The leader can finish and close its pipe while a descendant remains in
        # the probe's private process group.  Every outcome owns the same bounded
        # teardown, including normal EOF and a completed nonzero leader.
        stop_process_group(process)
        stream.close()


def _lstat_record(metadata: os.stat_result) -> dict[str, int]:
    return {
        "device": metadata.st_dev,
        "inode": metadata.st_ino,
        "mode": stat.S_IMODE(metadata.st_mode),
        "uid": metadata.st_uid,
        "gid": metadata.st_gid,
        "size": metadata.st_size,
        "mtime_ns": metadata.st_mtime_ns,
        "ctime_ns": metadata.st_ctime_ns,
    }


def _canonical_executable_path(path: str) -> str:
    """Normalize only macOS's documented /var and /private/var alias."""

    if sys.platform != "darwin":
        return path
    if path == "/var":
        return "/private/var"
    if path.startswith("/var/"):
        return "/private" + path
    return path


def _path_sha256(path: str) -> str:
    return hashlib.sha256(os.fsencode(_canonical_executable_path(path))).hexdigest()


def _read_bound_executable_sha256(path: Path, expected: os.stat_result) -> str:
    """Hash one safe executable through a no-follow descriptor race guard."""

    nofollow = getattr(os, "O_NOFOLLOW", 0)
    nonblock = getattr(os, "O_NONBLOCK", 0)
    if nofollow == 0 or nonblock == 0:
        raise EvidenceUnavailable("agy executable identity is unavailable")
    # O_NONBLOCK is harmless for regular files and prevents a regular pathname
    # replaced by a FIFO between lstat and open from hanging this pre-task gate.
    # A platform without the flag must fail closed rather than retry a blocking
    # open against an untrusted pathname.
    flags = os.O_RDONLY | nofollow | nonblock | getattr(os, "O_CLOEXEC", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise EvidenceUnavailable("agy executable identity is unavailable") from exc
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode):
            raise EvidenceUnavailable("agy executable identity is unavailable")
        if (
            not _safe_owner_mode(before, directory=False)
            or not (stat.S_IMODE(before.st_mode) & 0o111)
            or _lstat_record(before) != _lstat_record(expected)
            or before.st_size > EXECUTABLE_CONTENT_LIMIT
        ):
            raise EvidenceUnavailable("agy executable identity is unavailable")
        digest = hashlib.sha256()
        remaining = before.st_size
        while remaining:
            chunk = os.read(descriptor, min(64 * 1024, remaining))
            if not chunk:
                raise EvidenceUnavailable("agy executable identity is unavailable")
            digest.update(chunk)
            remaining -= len(chunk)
        if os.read(descriptor, 1):
            raise EvidenceUnavailable("agy executable identity is unavailable")
        after = os.fstat(descriptor)
        if _lstat_record(before) != _lstat_record(after):
            raise EvidenceUnavailable("agy executable identity is unavailable")
        return digest.hexdigest()
    except OSError as exc:
        raise EvidenceUnavailable("agy executable identity is unavailable") from exc
    finally:
        os.close(descriptor)


def _safe_owner_mode(metadata: os.stat_result, *, directory: bool) -> bool:
    """Permit the local owner or root, never group/world-writable objects.

    A root-owned sticky ancestor such as /tmp is the conventional exception: its
    sticky bit keeps one user from replacing another user's private descendant.
    The executable and every non-sticky component remain non-writable by group or
    world.
    """

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


def resolve_safe_executable() -> tuple[str, dict[str, Any]]:
    """Resolve `agy` once and return only a private executable path to callers.

    The persisted record deliberately contains hashes and lstat observations, not
    a local executable path.  Each final-path symlink is bounded and recorded so
    a historical record remains auditable without becoming a launch instruction.
    """

    candidate = shutil.which("agy")
    if not candidate:
        raise EvidenceUnavailable("agy is unavailable on PATH")
    candidate = os.path.abspath(candidate)
    parts = list(Path(candidate).parts[1:])
    current = Path(os.sep)
    chain: list[dict[str, Any]] = []
    components: list[dict[str, Any]] = []
    seen: set[tuple[int, int]] = set()
    for _ in range(128):
        if not parts:
            break
        part = parts.pop(0)
        if part in {"", ".", ".."}:
            raise EvidenceUnavailable("agy executable identity is unavailable")
        current /= part
        try:
            metadata = os.lstat(current)
        except OSError as exc:
            raise EvidenceUnavailable("agy executable identity is unavailable") from exc
        if stat.S_ISLNK(metadata.st_mode):
            # Symlink permission bits are not access controls on POSIX; ownership
            # plus the already-checked containing directory is the meaningful
            # boundary here.
            if metadata.st_uid not in {os.geteuid(), 0}:
                raise EvidenceUnavailable("agy executable identity is unavailable")
            identity = (metadata.st_dev, metadata.st_ino)
            if identity in seen or len(chain) >= 16:
                raise EvidenceUnavailable("agy executable identity is unavailable")
            seen.add(identity)
            try:
                target = os.readlink(current)
            except OSError as exc:
                raise EvidenceUnavailable("agy executable identity is unavailable") from exc
            chain.append({
                "path_sha256": _path_sha256(str(current)),
                "lstat": _lstat_record(metadata),
                "target_sha256": hashlib.sha256(os.fsencode(target)).hexdigest(),
            })
            target_path = Path(target if os.path.isabs(target) else current.parent / target)
            target_path = Path(os.path.normpath(str(target_path)))
            if not target_path.is_absolute():
                raise EvidenceUnavailable("agy executable identity is unavailable")
            parts = list(target_path.parts[1:]) + parts
            current = Path(os.sep)
            continue
        if parts:
            if not stat.S_ISDIR(metadata.st_mode) or not _safe_owner_mode(metadata, directory=True):
                raise EvidenceUnavailable("agy executable identity is unavailable")
            components.append({
                "path_sha256": _path_sha256(str(current)),
                "lstat": _lstat_record(metadata),
            })
            if len(components) > 128:
                raise EvidenceUnavailable("agy executable identity is unavailable")
            continue
        if not stat.S_ISREG(metadata.st_mode) or not _safe_owner_mode(metadata, directory=False):
            raise EvidenceUnavailable("agy executable identity is unavailable")
        if not (stat.S_IMODE(metadata.st_mode) & 0o111):
            raise EvidenceUnavailable("agy executable identity is unavailable")
        return str(current), {
            "path_sha256": _path_sha256(candidate),
            "target_lstat": _lstat_record(metadata),
            "content_sha256": _read_bound_executable_sha256(current, metadata),
            "symlink_chain": chain,
            "components": components,
        }
    raise EvidenceUnavailable("agy executable identity is unavailable")


def probe_command(
    executable: str, argument: str, *, timeout: float, output_limit: int, label: str,
    help_stderr: bool = False,
) -> bytes:
    """Run one bounded, group-owned local interface probe with no provider input."""

    process: subprocess.Popen[bytes] | None = None
    watched_signals = (signal.SIGHUP, signal.SIGINT, signal.SIGTERM)
    previous_handlers = {
        signal_number: signal.getsignal(signal_number)
        for signal_number in watched_signals
    }

    def interrupt_probe(signal_number: int, _frame: Any) -> None:
        raise ProbeInterrupted(signal_number)

    # Interface probes never need provider credentials. The public approval
    # recipe hashes C-locale help bytes, so bind the minimal probe environment
    # to that locale as well.
    probe_environment = child_environment(force_c_locale=True)
    try:
        for signal_number in watched_signals:
            signal.signal(signal_number, interrupt_probe)
        try:
            process = subprocess.Popen(
                [executable, argument], stdin=subprocess.DEVNULL,
                # Help is not consistently assigned to one stream by CLI
                # implementations.  A combined, bounded pipe avoids accepting
                # only the convenient half while retaining one teardown path.
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT if help_stderr else subprocess.DEVNULL,
                env=probe_environment,
                start_new_session=True,
            )
        except OSError as exc:
            raise EvidenceUnavailable(f"agy {label} probe could not start") from exc
        raw = capture_probe_output(
            process, timeout=timeout, output_limit=output_limit, label=label,
            # Help stderr is redirected into stdout above, so one combined pipe
            # remains bounded and has the same group teardown behavior.
            use_stderr=False,
        )
    except ProbeInterrupted:
        if process is not None:
            stop_process_group(process)
        raise
    finally:
        for signal_number, previous_handler in previous_handlers.items():
            signal.signal(signal_number, previous_handler)
    assert process is not None
    if process.returncode != 0:
        raise EvidenceUnavailable(f"agy {label} probe failed or was oversized")
    return raw


def probe_installed_version(executable: str | None = None) -> str:
    executable = executable or resolve_safe_executable()[0]
    raw = probe_command(
        executable, "--version", timeout=VERSION_TIMEOUT_SECONDS,
        output_limit=VERSION_OUTPUT_LIMIT, label="version",
    )

    if not raw.endswith(b"\n") or raw.count(b"\n") != 1 or b"\x00" in raw:
        raise EvidenceUnavailable("agy version output is empty or malformed")
    try:
        line = raw[:-1].decode("ascii")
    except UnicodeDecodeError as exc:
        raise EvidenceUnavailable("agy version output is not ASCII") from exc
    match = re.fullmatch(rf"(?:agy\s+)?({VERSION_RE.pattern})", line)
    if match is None:
        raise EvidenceUnavailable("agy version output lacks documented semantic content")
    return match.group(1)


def parse_critical_help(raw: bytes) -> tuple[str, str]:
    """Strictly bind the supported CLI surface without treating prose as evidence."""

    if b"\x00" in raw:
        raise EvidenceUnavailable("agy critical interface output is malformed")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise EvidenceUnavailable("agy critical interface output is malformed") from exc
    found: dict[str, str] = {}
    for line in text.splitlines():
        # Help currently uses exactly two indentation spaces then a long option and
        # at least two separating spaces.  Do not accept reflowed prose or aliases.
        match = re.fullmatch(r"  (--[a-z-]+) {2,}([^\r\n]+)", line)
        if match is None:
            continue
        option, detail = match.groups()
        if option not in CRITICAL_OPTIONS:
            continue
        if option in found:
            raise EvidenceUnavailable("agy critical interface output is ambiguous")
        if not detail or detail != detail.strip():
            raise EvidenceUnavailable("agy critical interface output is malformed")
        found[option] = detail
    if set(found) != set(CRITICAL_OPTIONS):
        raise EvidenceUnavailable("agy critical interface output is incompatible")
    semantic: dict[str, Any] = {}
    for option, required_values in CRITICAL_OPTIONS.items():
        detail = found[option]
        if not required_values:
            semantic[option] = True
            continue
        domains = re.findall(r"\(([^()]*)\)", detail)
        selected: set[str] | None = None
        for domain in domains:
            tokens = domain.split(", ")
            if not tokens or any(re.fullmatch(r"[a-z][a-z-]*", token) is None for token in tokens):
                continue
            values = set(tokens)
            if not set(required_values).issubset(values):
                continue
            allowed = CRITICAL_ENUM_VALUES[option]
            if not values.issubset(allowed) or selected is not None:
                raise EvidenceUnavailable("agy critical interface output is incompatible")
            selected = values
        if selected is None:
            raise EvidenceUnavailable("agy critical interface output is incompatible")
        semantic[option] = sorted(selected)
    normalized = json.dumps(
        {option: semantic[option] for option in sorted(semantic)},
        ensure_ascii=True, sort_keys=True, separators=(",", ":"),
    ).encode("ascii")
    return hashlib.sha256(normalized).hexdigest(), hashlib.sha256(raw).hexdigest()


def probe_critical_interface(executable: str) -> tuple[str, str]:
    raw = probe_command(
        executable, "--help", timeout=HELP_TIMEOUT_SECONDS,
        output_limit=HELP_OUTPUT_LIMIT, label="critical interface", help_stderr=True,
    )
    return parse_critical_help(raw)


def compatibility_review_evidence(
    *, installed: str, matrix_version: str, capability_sha: str, help_sha: str,
    relation: str, user_model: str, user_model_source: str, resolved_model: str,
    user_effort: str | None, user_effort_source: str | None,
    compatibility_disposition: str | None, approve_help_sha: str | None,
) -> dict[str, Any]:
    retry_arguments, retry_environment = [], {}
    selectors = [(user_model_source, "--model", user_model, "AGY_WORKER_MODEL")]
    if user_effort is not None:
        selectors.append((user_effort_source, "--effort", user_effort, "AGY_WORKER_EFFORT"))
    for source, flag, value, environment_name in selectors:
        if source == "cli":
            retry_arguments.extend((flag, value))
        else:
            retry_environment[environment_name] = value
    retry_arguments += ["--compatibility-disposition", "proceed", "--approve-help-sha", help_sha]
    evidence = {
        "schema_version": 1,
        "kind": "agy-worker-compatibility-review-evidence",
        "installed_agy_version": installed,
        "matrix_agy_version": matrix_version,
        "version_relation": relation,
        "compatibility_status": "direct-selection-review-required",
        "critical_interface_status": "compatible",
        "critical_capabilities_sha256": capability_sha,
        "raw_help_sha256": help_sha,
        "user_model": user_model,
        "user_model_source": user_model_source,
        "resolved_agy_model": resolved_model,
        "retry_selection_arguments": retry_arguments,
        "retry_selection_environment": retry_environment,
        "approval": {"compatibility_disposition": compatibility_disposition, "approve_help_sha256": approve_help_sha},
    }
    if user_effort is not None:
        evidence.update(user_effort=user_effort, user_effort_source=user_effort_source)
    return evidence


def resolve_selection(
    model: str,
    effort: str | None,
    model_source: str,
    effort_source: str | None,
    *,
    probe_version: bool,
    compatibility_disposition: str | None = None,
    approve_help_sha: str | None = None,
) -> dict[str, Any]:
    if not model or model.strip() != model:
        raise CallerError("--model must be non-empty and unpadded")
    if effort is not None and (not effort or effort.strip() != effort):
        raise CallerError("--effort must be non-empty and unpadded")
    if model_source not in SOURCE_NAMES or (effort_source is not None and effort_source not in SOURCE_NAMES):
        raise CallerError("selector provenance must be cli or environment")
    if effort is None and effort_source is not None:
        raise CallerError("effort provenance was supplied without an effort")
    if effort is not None and effort_source is None:
        raise CallerError("effort provenance is required with an effort")
    if (compatibility_disposition is None) != (approve_help_sha is None):
        # The pair is checked again after the local version probe so an
        # omitted approval produces review-required rather than usage.
        if compatibility_disposition is not None and compatibility_disposition != "proceed":
            raise CallerError("--compatibility-disposition must be exactly proceed")
        if approve_help_sha is not None and SHA256_RE.fullmatch(approve_help_sha) is None:
            raise CallerError("--approve-help-sha must be one lowercase SHA-256")
    elif compatibility_disposition is not None:
        if compatibility_disposition != "proceed":
            raise CallerError("--compatibility-disposition must be exactly proceed")
        if SHA256_RE.fullmatch(approve_help_sha or "") is None:
            raise CallerError("--approve-help-sha must be one lowercase SHA-256")

    matrix, matrix_sha, matrix_version, matrix_revision = load_policy()
    resolved, mode = resolve_model(matrix, model, effort)
    executable, executable_record = resolve_safe_executable() if probe_version else (None, None)
    installed = probe_installed_version(executable) if executable else None
    capability_sha = help_sha = None
    if executable:
        capability_sha, help_sha = probe_critical_interface(executable)
    result: dict[str, Any] = {
        "schema_version": 2 if installed is not None else 1,
        "kind": "agy-worker-selection",
        "selection_mode": mode,
        "user_model": model,
        "user_model_source": model_source,
        "resolved_agy_model": resolved,
        "matrix_sha256": matrix_sha,
        "matrix_agy_version": matrix_version,
        "matrix_source_revision": matrix_revision,
    }
    if installed is not None:
        relation = "match" if installed == matrix_version else "drift"
        evidence = compatibility_review_evidence(
            installed=installed, matrix_version=matrix_version, relation=relation,
            capability_sha=capability_sha or "", help_sha=help_sha or "",
            user_model=model, user_model_source=model_source, resolved_model=resolved,
            user_effort=effort, user_effort_source=effort_source,
            compatibility_disposition=compatibility_disposition,
            approve_help_sha=approve_help_sha,
        )
        if relation == "match":
            if compatibility_disposition is not None or approve_help_sha is not None:
                raise CallerError("compatibility approval is reserved for version drift")
        elif compatibility_disposition is None or approve_help_sha is None:
            raise ReviewRequired(
                "version drift needs --compatibility-disposition proceed and --approve-help-sha SHA256",
                evidence,
            )
        if relation == "drift" and approve_help_sha != help_sha:
            raise ReviewRequired("approved help SHA-256 does not match the structural probe", evidence)
        result.update({
            "schema_version": 3 if relation == "drift" else 2,
            "installed_agy_version": installed,
            "version_relation": relation,
            "compatibility_status": (
                "reviewed-version-match" if relation == "match"
                else "critical-interface-compatible-version-drift"
            ),
            "critical_interface_probe_version": 1,
            "critical_interface_status": "compatible",
            "critical_capabilities_sha256": capability_sha,
            "help_sha256": help_sha,
            "model_availability": "not_assessed",
            "probed_executable": executable_record,
        })
    if effort is not None:
        result["user_effort"] = effort
        result["user_effort_source"] = effort_source
    if installed is not None and relation == "drift":
        result.update({
            "compatibility_disposition": "proceed",
            "approved_help_sha256": approve_help_sha,
        })
        result["compatibility_decision_sha256"] = compatibility_decision_sha256(result)
    return result


def compatibility_decision_sha256(record: dict[str, Any]) -> str:
    """Hash the exact Codex disposition and every fact it is allowed to approve."""

    fields = (
        "compatibility_disposition", "approved_help_sha256", "help_sha256",
        "critical_capabilities_sha256", "installed_agy_version", "matrix_agy_version",
        "matrix_sha256", "matrix_source_revision", "selection_mode",
        "user_model", "user_model_source", "resolved_agy_model", "probed_executable",
    )
    decision = {key: record[key] for key in fields}
    if record["selection_mode"] == "model-effort":
        decision["user_effort"] = record["user_effort"]
        decision["user_effort_source"] = record["user_effort_source"]
    raw = json.dumps(decision, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def resolve_tier_selection(tier: str, source: str) -> dict[str, Any]:
    if not tier:
        raise CallerError("--tier must not be empty")
    if source not in TIER_SOURCES:
        raise CallerError("tier provenance must be cli, environment, or implicit-default")
    record: dict[str, Any] = {
        "schema_version": 1,
        "kind": "agy-worker-selection",
        "selection_mode": "tier",
        "selected_tier": tier,
        "selected_tier_source": source,
        "resolved_agy_model": None,
    }
    if tier != "default":
        record["resolved_agy_model"] = TIER_MODEL_BY_NAME.get(tier, tier)
    return record


def resolve_literal_selection(model: str) -> dict[str, Any]:
    """Record one caller-owned literal without consulting compatibility policy."""

    if not isinstance(model, str) or len(model) > 128 or LITERAL_MODEL_RE.fullmatch(model) is None:
        raise CallerError("--literal-model must be one exact lowercase model slug")
    return {
        "schema_version": 1,
        "kind": "agy-worker-selection",
        "selection_mode": "literal-model",
        "user_model": model,
        "user_model_source": "cli",
        "resolved_agy_model": model,
        "compatibility_status": "unreconciled-pass-through",
    }


def require_exact_fields(record: dict[str, Any], expected: set[str]) -> None:
    actual = set(record)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        detail = []
        if missing:
            detail.append(f"missing={','.join(missing)}")
        if extra:
            detail.append(f"extra={','.join(extra)}")
        raise CallerError(f"selection record has invalid fields ({'; '.join(detail)})")


def require_string(record: dict[str, Any], key: str) -> str:
    value = record.get(key)
    if not isinstance(value, str) or not value or value.strip() != value:
        raise CallerError(f"selection record {key} must be a non-empty unpadded string")
    return value


def validate_lstat_record(value: Any) -> None:
    current = {"device", "inode", "mode", "uid", "gid", "size", "mtime_ns", "ctime_ns"}
    legacy = current - {"ctime_ns"}
    if not isinstance(value, dict) or (set(value) != current and set(value) != legacy):
        raise CallerError("selection record executable binding is invalid")
    for key in value:
        if type(value.get(key)) is not int or value[key] < 0:
            raise CallerError("selection record executable binding is invalid")
    if value["device"] == 0 or value["inode"] == 0 or value["mode"] == 0:
        raise CallerError("selection record executable binding is invalid")


def validate_probed_executable(value: Any) -> None:
    current_fields = {"path_sha256", "target_lstat", "content_sha256", "symlink_chain", "components"}
    legacy_fields = current_fields - {"content_sha256"}
    if not isinstance(value, dict) or (set(value) != current_fields and set(value) != legacy_fields):
        raise CallerError("selection record executable binding is invalid")
    if SHA256_RE.fullmatch(value.get("path_sha256", "")) is None:
        raise CallerError("selection record executable binding is invalid")
    if "content_sha256" in value and SHA256_RE.fullmatch(value["content_sha256"]) is None:
        raise CallerError("selection record executable binding is invalid")
    validate_lstat_record(value.get("target_lstat"))
    target = value["target_lstat"]
    if target["uid"] not in {os.geteuid(), 0} or target["mode"] & 0o022:
        raise CallerError("selection record executable binding is invalid")
    chain = value.get("symlink_chain")
    components = value.get("components")
    if not isinstance(chain, list) or not isinstance(components, list) or len(chain) > 16 or len(components) > 128:
        raise CallerError("selection record executable binding is invalid")
    for item in chain:
        if not isinstance(item, dict) or set(item) != {"path_sha256", "lstat", "target_sha256"}:
            raise CallerError("selection record executable binding is invalid")
        if SHA256_RE.fullmatch(item.get("path_sha256", "")) is None or SHA256_RE.fullmatch(item.get("target_sha256", "")) is None:
            raise CallerError("selection record executable binding is invalid")
        validate_lstat_record(item.get("lstat"))
    for item in components:
        if not isinstance(item, dict) or set(item) != {"path_sha256", "lstat"} or SHA256_RE.fullmatch(item.get("path_sha256", "")) is None:
            raise CallerError("selection record executable binding is invalid")
        validate_lstat_record(item.get("lstat"))


def has_current_probed_executable_binding(value: Any) -> bool:
    """Whether a decoded binding contains every field required to launch now.

    V2 artifacts written before content digests and ctime observations existed
    remain readable evidence.  They are deliberately not equivalent to a
    current launch binding, even if their relation says ``match``.
    """

    current_lstat = {
        "device", "inode", "mode", "uid", "gid", "size", "mtime_ns", "ctime_ns",
    }
    current_fields = {
        "path_sha256", "target_lstat", "content_sha256", "symlink_chain", "components",
    }
    if not isinstance(value, dict) or set(value) != current_fields:
        return False
    if not isinstance(value.get("target_lstat"), dict) or set(value["target_lstat"]) != current_lstat:
        return False
    chain = value.get("symlink_chain")
    components = value.get("components")
    if not isinstance(chain, list) or not isinstance(components, list):
        return False
    return all(
        isinstance(item, dict)
        and isinstance(item.get("lstat"), dict)
        and set(item["lstat"]) == current_lstat
        for item in [*chain, *components]
    )


def validate_selection_record_shape(record: dict[str, Any]) -> None:
    """Validate strict v1/v2 selection-record shape and provenance without probing."""

    if not isinstance(record, dict):
        raise CallerError("selection record must be one JSON object")
    schema_version = record.get("schema_version")
    if type(schema_version) is not int or schema_version not in (1, 2, 3):
        raise CallerError("selection record schema_version must be 1, 2, or 3")
    if record.get("kind") != "agy-worker-selection":
        raise CallerError("selection record kind is invalid")
    mode = record.get("selection_mode")
    if mode == "tier":
        if schema_version != 1:
            raise CallerError("selection record tier schema_version is invalid")
        require_exact_fields(record, TIER_RECORD_FIELDS)
        tier = require_string(record, "selected_tier")
        source = record.get("selected_tier_source")
        if source not in TIER_SOURCES:
            raise CallerError("selection record tier source is invalid")
        if source == "implicit-default" and tier != "default":
            raise CallerError("implicit-default provenance is reserved for the agy-owned default")
        expected = None if tier == "default" else TIER_MODEL_BY_NAME.get(tier, tier)
        if record.get("resolved_agy_model") != expected:
            raise CallerError("selection record tier resolution is inconsistent")
        return

    if mode == "literal-model":
        if schema_version != 1:
            raise CallerError("selection record literal schema_version is invalid")
        require_exact_fields(record, LITERAL_RECORD_FIELDS)
        user_model = require_string(record, "user_model")
        if len(user_model) > 128 or LITERAL_MODEL_RE.fullmatch(user_model) is None:
            raise CallerError("selection record literal model is invalid")
        if record.get("user_model_source") != "cli":
            raise CallerError("selection record literal source is invalid")
        if record.get("resolved_agy_model") != user_model:
            raise CallerError("selection record literal resolution is inconsistent")
        if record.get("compatibility_status") != "unreconciled-pass-through":
            raise CallerError("selection record literal compatibility status is invalid")
        return

    if mode not in ("exact-model", "model-effort"):
        raise CallerError("selection record mode is invalid")
    if schema_version == 1:
        expected_fields = EFFORT_V1_RECORD_FIELDS if mode == "model-effort" else DIRECT_V1_RECORD_FIELDS
    elif schema_version == 2:
        expected_fields = EFFORT_V2_RECORD_FIELDS if mode == "model-effort" else DIRECT_V2_RECORD_FIELDS
    else:
        expected_fields = EFFORT_V3_RECORD_FIELDS if mode == "model-effort" else DIRECT_V3_RECORD_FIELDS
    require_exact_fields(
        record, expected_fields,
    )
    user_model = require_string(record, "user_model")
    resolved_model = require_string(record, "resolved_agy_model")
    if schema_version == 3:
        for key, value in (("user_model", user_model), ("resolved_agy_model", resolved_model)):
            if len(value) > 128 or LITERAL_MODEL_RE.fullmatch(value) is None:
                raise CallerError(f"selection record {key} is invalid")
    if record.get("user_model_source") not in SOURCE_NAMES:
        raise CallerError("selection record model source is invalid")
    installed = require_string(record, "installed_agy_version")
    matrix_version = require_string(record, "matrix_agy_version")
    if VERSION_RE.fullmatch(installed) is None:
        raise CallerError("selection record installed version is invalid")
    if VERSION_RE.fullmatch(matrix_version) is None:
        raise CallerError("selection record matrix version is invalid")
    matrix_sha = require_string(record, "matrix_sha256")
    revision = require_string(record, "matrix_source_revision")
    if SHA256_RE.fullmatch(matrix_sha) is None:
        raise CallerError("selection record matrix SHA-256 is invalid")
    if REVISION_RE.fullmatch(revision) is None:
        raise CallerError("selection record source revision is invalid")
    if schema_version == 1:
        if installed != matrix_version:
            raise CallerError("selection record installed version is invalid")
    else:
        relation = record.get("version_relation")
        status = record.get("compatibility_status")
        expected_relation = "match" if installed == matrix_version else "drift"
        expected_status = (
            "reviewed-version-match"
            if expected_relation == "match"
            else "critical-interface-compatible-version-drift"
        )
        if relation != expected_relation or status != expected_status:
            raise CallerError("selection record version relation is invalid")
        if schema_version == 3 and expected_relation != "drift":
            raise CallerError("selection record version relation is invalid")
        if record.get("critical_interface_probe_version") != 1:
            raise CallerError("selection record critical interface version is invalid")
        if record.get("critical_interface_status") != "compatible":
            raise CallerError("selection record critical interface status is invalid")
        for key in ("critical_capabilities_sha256", "help_sha256"):
            if SHA256_RE.fullmatch(require_string(record, key)) is None:
                raise CallerError("selection record critical interface digest is invalid")
        if record.get("model_availability") != "not_assessed":
            raise CallerError("selection record model availability is invalid")
        if schema_version == 3:
            if record.get("approved_help_sha256") != record["help_sha256"]:
                raise CallerError("selection record approved help binding is invalid")
        validate_probed_executable(record.get("probed_executable"))
        if schema_version == 3:
            if not has_current_probed_executable_binding(record["probed_executable"]):
                raise CallerError("selection record executable binding is legacy-only")
            if record.get("compatibility_disposition") != "proceed":
                raise CallerError("selection record compatibility disposition is invalid")
            if record.get("approved_help_sha256") != record.get("help_sha256"):
                raise CallerError("selection record approved help SHA-256 is invalid")
            decision = record.get("compatibility_decision_sha256")
            if not isinstance(decision, str) or SHA256_RE.fullmatch(decision) is None:
                raise CallerError("selection record compatibility decision is invalid")
            if decision != compatibility_decision_sha256(record):
                raise CallerError("selection record compatibility decision is invalid")
    effort = None
    if mode == "model-effort":
        effort = require_string(record, "user_effort")
        if effort not in compatibility.EFFORTS:
            raise CallerError("selection record effort is invalid")
        if record.get("user_effort_source") not in SOURCE_NAMES:
            raise CallerError("selection record effort source is invalid")
    elif resolved_model != user_model:
        raise CallerError("selection record exact model resolution is inconsistent")


def validate_selection_record(record: dict[str, Any]) -> None:
    """Validate the exact semantic artifact contract against reviewed policy."""

    validate_selection_record_shape(record)
    mode = record["selection_mode"]
    if mode in ("tier", "literal-model"):
        return
    user_model = record["user_model"]
    resolved_model = record["resolved_agy_model"]
    matrix_sha = record["matrix_sha256"]
    matrix_version = record["matrix_agy_version"]
    revision = record["matrix_source_revision"]
    effort = record.get("user_effort")
    matrix, current_sha, current_version, current_revision = load_policy()
    if (matrix_sha, matrix_version, revision) != (
        current_sha,
        current_version,
        current_revision,
    ):
        raise ReviewRequired("selection record compatibility provenance drifted")
    expected_model, expected_mode = resolve_model(matrix, user_model, effort)
    if mode != expected_mode or resolved_model != expected_model:
        raise CallerError("selection record direct resolution is inconsistent")


def reprobe_selection_record(record: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    """Re-resolve and prove a frozen direct selection immediately before launch.

    This is intentionally the sole API which returns the local executable path;
    command-line modes never print it.  Version and inode changes are acceptable
    only before a fresh safe-target, version, and critical-interface probe.  The
    target and its content-related lstat binding must then remain exact through a
    final re-resolution immediately before the controller launch boundary.
    """

    # This is a controller launch path, not a new caller choice.  The dispatch
    # command passes the record decoded from the exact bytes it SHA/identity-
    # bound, so this probe must not reopen a mutable record path.  Its shape
    # still authenticates the record's own matrix identity and direct-interface
    # evidence before the fresh executable probe.
    validate_selection_record_shape(record)
    schema_version = record.get("schema_version")
    if record.get("selection_mode") not in ("exact-model", "model-effort") or schema_version not in (2, 3):
        raise CallerError("selection record has no direct executable binding")
    if not has_current_probed_executable_binding(record["probed_executable"]):
        raise CallerError("selection record executable binding is legacy-only")
    executable, binding = resolve_safe_executable()
    installed = probe_installed_version(executable)
    capabilities, help_sha = probe_critical_interface(executable)
    if (
        installed != record["installed_agy_version"]
        or capabilities != record["critical_capabilities_sha256"]
        or help_sha != record["help_sha256"]
        or not frozen_executable_binding_matches(record["probed_executable"], binding)
    ):
        raise EvidenceUnavailable("agy direct-selection compatibility facts changed")
    final_executable, final_binding = resolve_safe_executable()
    if final_executable != executable or not executable_bindings_match(binding, final_binding):
        raise EvidenceUnavailable("agy executable changed during final interface probe")
    return final_executable, final_binding


def frozen_executable_binding_matches(before: dict[str, Any], after: dict[str, Any]) -> bool:
    """Compare target bytes plus all path identity and authority observations.

    Path digests are normalized only when written through the documented macOS
    ``/var`` -> ``/private/var`` alias.  A legacy V2/V3 record can still be
    decoded, but cannot authorize a current direct-selection launch because it
    lacks the required descriptor-bound content digest.
    """

    return executable_bindings_match(before, after)


def executable_bindings_match(before: dict[str, Any], after: dict[str, Any]) -> bool:
    """Compare the target bytes and every resolved path-authority observation."""

    if before.get("path_sha256") != after.get("path_sha256"):
        return False
    if before.get("target_lstat") != after.get("target_lstat"):
        return False
    if before.get("content_sha256") != after.get("content_sha256"):
        return False
    if before.get("symlink_chain") != after.get("symlink_chain"):
        return False
    before_components = before.get("components")
    after_components = after.get("components")
    if not isinstance(before_components, list) or not isinstance(after_components, list):
        return False
    if len(before_components) != len(after_components):
        return False
    authority_fields = ("device", "inode", "mode", "uid", "gid")
    for old, new in zip(before_components, after_components):
        if old.get("path_sha256") != new.get("path_sha256"):
            return False
        old_lstat = old.get("lstat", {})
        new_lstat = new.get("lstat", {})
        if any(old_lstat.get(key) != new_lstat.get(key) for key in authority_fields):
            return False
    return True


def confirm_executable_binding(executable: str, binding: dict[str, Any]) -> str:
    """Consume a re-probe binding at the controller's immediate launch boundary."""

    current_executable, current_binding = resolve_safe_executable()
    if current_executable != executable or not executable_bindings_match(binding, current_binding):
        raise EvidenceUnavailable("agy executable changed before provider launch")
    return current_executable


def decode_selection_record(payload: bytes, *, frozen: bool = False) -> dict[str, Any]:
    """Strictly decode and validate the exact supplied selection-record bytes."""

    def reject_constant(_value: str) -> Any:
        raise CallerError("selection record input is not bounded valid JSON")

    def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise CallerError("selection record input has duplicate keys")
            result[key] = value
        return result

    try:
        record = json.loads(
            payload.decode("utf-8"),
            parse_constant=reject_constant,
            object_pairs_hook=reject_duplicate_keys,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError) as exc:
        raise CallerError("selection record input is not bounded valid JSON") from exc
    if frozen:
        validate_selection_record_shape(record)
    else:
        validate_selection_record(record)
    return record


def read_selection_record(path: Path, *, frozen: bool = False) -> dict[str, Any]:
    """Read one record, with live policy validation only for a new selection.

    A controller consumes immutable bytes that its dispatch command and state
    have already bound cryptographically.  Those bytes retain their own matrix
    SHA/version/revision and interface-evidence fields, which are checked by
    ``validate_selection_record_shape``.  Consulting the mutable current
    matrix here would turn unrelated policy drift into a change to the caller's
    already-approved model choice.
    """

    if path.is_symlink() or not path.is_file():
        raise CallerError("selection record input must be one real file")
    try:
        payload = read_bounded(path)
    except OSError as exc:
        raise CallerError("selection record input is not bounded valid JSON") from exc
    return decode_selection_record(payload, frozen=frozen)


def publish_record(path: Path, record: dict[str, Any]) -> None:
    if path.exists() or path.is_symlink() or not path.parent.is_dir():
        raise CallerError("selection output must be a new file in an existing directory")
    payload = (json.dumps(record, indent=2, sort_keys=True) + "\n").encode("utf-8")
    temporary = path.parent / f".{path.name}.{os.getpid()}"
    descriptor = -1
    try:
        descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "wb") as handle:
            descriptor = -1
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        # Validate the exact bytes that will be published. The temporary remains
        # private and the destination does not exist until this check succeeds.
        candidate = read_selection_record(temporary)
        if candidate != record:
            raise CallerError("selection record changed before publication")
        os.replace(temporary, path)
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def build_parser() -> UsageParser:
    parser = UsageParser(prog="model-selection.sh")
    parser.add_argument("--tier", action="append")
    parser.add_argument("--tier-source", action="append", choices=TIER_SOURCES)
    parser.add_argument("--model", action="append")
    parser.add_argument("--literal-model", action="append")
    parser.add_argument("--effort", action="append")
    parser.add_argument("--model-source", action="append", choices=SOURCE_NAMES)
    parser.add_argument("--effort-source", action="append", choices=SOURCE_NAMES)
    parser.add_argument("--compatibility-disposition", action="append")
    parser.add_argument("--approve-help-sha", action="append")
    parser.add_argument("--output", action="append")
    parser.add_argument("--validate-record", action="append")
    parser.add_argument("--verify-record-executable", action="append")
    parser.add_argument("--observe-installed-version", action="store_true")
    parser.add_argument("--child-env", action="append", default=[])
    return parser


def main(argv: list[str] | None = None) -> int:
    global ACTIVE_CHILD_ENV
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        ACTIVE_CHILD_ENV = validate_child_environment_names(args.child_env)
    except EvidenceUnavailable as exc:
        parser.error(str(exc))
    tier = one(parser, args.tier, "--tier", False)
    tier_source = one(parser, args.tier_source, "--tier-source", False)
    model = one(parser, args.model, "--model", False)
    literal_model = one(parser, args.literal_model, "--literal-model", False)
    effort = one(parser, args.effort, "--effort", False)
    model_source = one(parser, args.model_source, "--model-source", False) or "cli"
    effort_source = one(parser, args.effort_source, "--effort-source", False)
    compatibility_disposition = one(parser, args.compatibility_disposition, "--compatibility-disposition", False)
    approve_help_sha = one(parser, args.approve_help_sha, "--approve-help-sha", False)
    output = one(parser, args.output, "--output", False)
    validate_record = one(parser, args.validate_record, "--validate-record", False)
    verify_record_executable = one(
        parser, args.verify_record_executable, "--verify-record-executable", False,
    )
    if args.observe_installed_version:
        if any(
            value is not None
            for value in (
                args.tier, args.tier_source, args.model, args.literal_model,
                args.effort, args.model_source, args.effort_source,
                args.compatibility_disposition, args.approve_help_sha, args.output,
                args.validate_record, args.verify_record_executable,
            )
        ):
            parser.error("--observe-installed-version is mutually exclusive with selection inputs")
        try:
            print(probe_installed_version())
        except EvidenceUnavailable as exc:
            print(f"model-selection: evidence-unavailable - {exc}", file=sys.stderr)
            return 8
        except ProbeInterrupted as exc:
            return 128 + exc.signal_number
        return 0
    if validate_record is not None:
        if any(
            value is not None
            for value in (
                args.tier,
                args.tier_source,
                args.model,
                args.literal_model,
                args.effort,
                args.model_source,
                args.effort_source,
                args.compatibility_disposition,
                args.approve_help_sha,
                args.output,
                args.verify_record_executable,
            )
        ):
            parser.error("--validate-record is mutually exclusive with selection inputs")
        try:
            read_selection_record(Path(validate_record))
        except CallerError as exc:
            print(f"model-selection: {exc}", file=sys.stderr)
            return 64
        except ReviewRequired as exc:
            print_review_required(exc)
            return 7
        except EvidenceUnavailable as exc:
            print(f"model-selection: evidence-unavailable - {exc}", file=sys.stderr)
            return 8
        return 0
    if verify_record_executable is not None:
        if any(
            value is not None
            for value in (
                args.tier, args.tier_source, args.model, args.literal_model,
                args.effort, args.model_source, args.effort_source,
                args.compatibility_disposition, args.approve_help_sha, args.output,
                args.validate_record,
            )
        ):
            parser.error("--verify-record-executable is mutually exclusive with selection inputs")
        try:
            # This compatibility flag proves the record but deliberately does
            # not make an executable path a public CLI output.
            record = read_selection_record(Path(verify_record_executable), frozen=True)
            reprobe_selection_record(record)
        except CallerError as exc:
            print(f"model-selection: {exc}", file=sys.stderr)
            return 64
        except ReviewRequired as exc:
            print_review_required(exc)
            return 7
        except EvidenceUnavailable as exc:
            print(f"model-selection: evidence-unavailable - {exc}", file=sys.stderr)
            return 8
        return 0
    if sum(value is not None for value in (tier, model, literal_model)) != 1:
        parser.error("exactly one of --tier, --model, or --literal-model is required")
    if tier is not None and (
        effort is not None or args.model_source is not None or effort_source is not None
    ):
        parser.error("--tier is mutually exclusive with model and effort inputs")
    if literal_model is not None and (
        effort is not None
        or args.model_source is not None
        or effort_source is not None
        or tier_source is not None
    ):
        parser.error("--literal-model is CLI-only and mutually exclusive with tier/model/effort provenance")
    if (compatibility_disposition is not None or approve_help_sha is not None) and model is None:
        parser.error("compatibility approval requires --model")
    if tier is None and tier_source is not None:
        parser.error("--tier-source requires --tier")
    if tier is not None and tier_source is None:
        tier_source = "cli"
    if effort is not None and effort_source is None:
        effort_source = "cli"
    if effort is None and effort_source is not None:
        parser.error("--effort-source requires --effort")
    try:
        if tier is not None:
            record = resolve_tier_selection(tier, tier_source or "cli")
        elif literal_model is not None:
            record = resolve_literal_selection(literal_model)
        else:
            record = resolve_selection(
                model or "", effort, model_source, effort_source, probe_version=True,
                compatibility_disposition=compatibility_disposition,
                approve_help_sha=approve_help_sha,
            )
        if output is None:
            json.dump(record, sys.stdout, indent=2, sort_keys=True)
            sys.stdout.write("\n")
        else:
            publish_record(Path(output), record)
            print(record.get("resolved_agy_model") or "")
    except CallerError as exc:
        print(f"model-selection: {exc}", file=sys.stderr)
        return 64
    except ReviewRequired as exc:
        print_review_required(exc)
        return 7
    except EvidenceUnavailable as exc:
        print(f"model-selection: evidence-unavailable - {exc}", file=sys.stderr)
        return 8
    except ProbeInterrupted as exc:
        return 128 + exc.signal_number
    return 0


def print_review_required(exc: ReviewRequired) -> None:
    """Emit the bounded public evidence shape without changing success stdout."""
    if exc.evidence is None:
        print(f"model-selection: review-required - {exc}", file=sys.stderr)
        return
    raw = json.dumps(exc.evidence, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
    print(f"model-selection: review-required {raw}", file=sys.stderr)


if __name__ == "__main__":
    raise SystemExit(main())
