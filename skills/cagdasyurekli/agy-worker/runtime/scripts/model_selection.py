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
from typing import Any, NoReturn

sys.dont_write_bytecode = True



SHA256_RE = re.compile(r"[0-9a-f]{64}")
SOURCE_NAMES = ("cli", "environment")
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
SELECTION_SCHEMA = 5
COMMON_RECORD_FIELDS = {"schema_version", "kind", "selection_mode", "resolved_agy_model"}
PROBE_FIELDS = {"installed_agy_version", "probed_executable"}
REQUIRED_AGY_CAPABILITIES = (
    "--add-dir", "--disable-slash-commands", "--json-schema", "--mode",
    "--model", "--output-format", "--print", "--print-timeout",
)
KNOWN_AGY_CAPABILITIES = REQUIRED_AGY_CAPABILITIES + ("--sandbox", "--conversation", "--effort")
REQUIRED_CAPABILITY_VALUES = {
    "--mode": {"accept-edits", "plan"}, "--output-format": {"stream-json"},
}


class CallerError(ValueError):
    """The caller supplied an invalid or ambiguous selector."""


class EvidenceUnavailable(ValueError):
    """Required local evidence is missing, malformed, or could not be observed."""


class MissingCapabilities(EvidenceUnavailable):
    """A diagnostic made exclusively from the controller's fixed flag names."""

    def __init__(self, flags: tuple[str, ...], *, values: bool = False) -> None:
        if not flags or len(set(flags)) != len(flags) or any(flag not in KNOWN_AGY_CAPABILITIES for flag in flags):
            raise ValueError("invalid capability diagnostic")
        self.flags = tuple(sorted(flags))
        self.values = values
        super().__init__(self.diagnostic())

    def diagnostic(self) -> str:
        prefix = "agy missing required capability values: " if self.values else "agy missing required capabilities: "
        return prefix + ", ".join(self.flags)


class ProbeInterrupted(BaseException):
    """A terminal signal interrupted the bounded local version probe."""

    def __init__(self, signal_number: int) -> None:
        super().__init__(signal_number)
        self.signal_number = signal_number


class UsageParser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
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

    # Interface probes never need provider credentials. Keep their minimal
    # environment and capability descriptions in the C locale.
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
    raw = probe_command(executable, "--version", timeout=VERSION_TIMEOUT_SECONDS,
                        output_limit=VERSION_OUTPUT_LIMIT, label="version")
    try:
        line = (raw[:-1] if raw.endswith(b"\n") else raw).decode("utf-8")
    except UnicodeDecodeError as exc:
        raise EvidenceUnavailable("agy version output is malformed") from exc
    if not line or line != line.strip() or any(ord(c) < 32 or ord(c) == 127 for c in line):
        raise EvidenceUnavailable("agy version output is empty or malformed")
    return line

def required_agy_capabilities(
    *, provider_isolation: str = "session", conversation: bool = False, effort: bool = False,
) -> tuple[str, ...]:
    """Require optional flags only when the selected operation uses them."""
    if provider_isolation not in {"session", "native"}:
        raise CallerError("provider isolation must be session or native")
    return REQUIRED_AGY_CAPABILITIES + tuple(
        flag for flag, enabled in (
            ("--sandbox", provider_isolation == "native"),
            ("--conversation", conversation), ("--effort", effort),
        ) if enabled
    )


def parse_critical_help(
    raw: bytes, *, provider_isolation: str = "session", conversation: bool = False,
    effort: bool = False,
) -> None:
    """Check advertised flags and required transport values, never model policy."""
    required_flags = required_agy_capabilities(
        provider_isolation=provider_isolation, conversation=conversation, effort=effort,
    )
    if not raw or b"\x00" in raw:
        raise EvidenceUnavailable("agy capability help is malformed")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise EvidenceUnavailable("agy capability help is malformed") from exc
    found: dict[str, str] = {}
    for line in text.splitlines():
        match = re.fullmatch(r"  (--[a-z-]+) {2,}([^\r\n]+)", line)
        if match is None or match[1] not in required_flags:
            continue
        option, detail = match.groups()
        if option in found or detail != detail.strip():
            raise EvidenceUnavailable("agy capability help is ambiguous or malformed")
        found[option] = detail
    missing = sorted(set(required_flags) - set(found))
    if missing:
        raise MissingCapabilities(tuple(missing))
    for option, required in REQUIRED_CAPABILITY_VALUES.items():
        domains = [set(domain.split(", ")) for domain in re.findall(r"\(([^()]*)\)", found[option])]
        if not any(required <= domain for domain in domains):
            raise MissingCapabilities((option,), values=True)

def probe_critical_interface(
    executable: str, *, provider_isolation: str = "session", conversation: bool = False,
    effort: bool = False,
) -> None:
    raw = probe_command(
        executable, "--help", timeout=HELP_TIMEOUT_SECONDS,
        output_limit=HELP_OUTPUT_LIMIT, label="critical interface", help_stderr=True,
    )
    parse_critical_help(
        raw, provider_isolation=provider_isolation, conversation=conversation, effort=effort,
    )


def transport_value(value: str, label: str) -> str:
    if (not isinstance(value, str) or not value or len(value) > 128
            or value != value.strip() or value.startswith("-")
            or any(ord(c) < 33 or ord(c) == 127 for c in value)):
        raise CallerError(f"{label} must be one bounded non-empty argument")
    return value


def probe_capabilities(
    *, provider_isolation: str = "session", conversation: bool = False, effort: bool = False,
) -> tuple[str, dict[str, Any], str]:
    executable, binding = resolve_safe_executable()
    version = probe_installed_version(executable)
    probe_critical_interface(
        executable, provider_isolation=provider_isolation, conversation=conversation, effort=effort,
    )
    confirm_executable_binding(executable, binding)
    return executable, binding, version


def bind_selection(
    record: dict[str, Any], *, provider_isolation: str = "session",
) -> dict[str, Any]:
    _executable, binding, version = probe_capabilities(
        provider_isolation=provider_isolation, effort=record.get("user_effort") is not None,
    )
    return {**record, "installed_agy_version": version, "probed_executable": binding}


def resolve_selection(
    model: str, effort: str | None, model_source: str, effort_source: str | None,
    *, probe_version: bool, provider_isolation: str = "session",
) -> dict[str, Any]:
    transport_value(model, "--model")
    if model_source not in SOURCE_NAMES or (effort_source is not None and effort_source not in SOURCE_NAMES):
        raise CallerError("selector provenance must be cli or environment")
    if (effort is None) != (effort_source is None):
        raise CallerError("effort and its provenance must be supplied together")
    record: dict[str, Any] = {
        "schema_version": SELECTION_SCHEMA, "kind": "agy-worker-selection",
        "selection_mode": "exact-model" if effort is None else "model-effort",
        "user_model": model, "user_model_source": model_source, "resolved_agy_model": model,
    }
    if effort is not None:
        record.update(user_effort=transport_value(effort, "--effort"), user_effort_source=effort_source)
    return bind_selection(record, provider_isolation=provider_isolation) if probe_version else record


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
    """Require complete descriptor, content, and path authority observations."""

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
    if not isinstance(record, dict) or type(record.get("schema_version")) is not int or record["schema_version"] != SELECTION_SCHEMA:
        raise CallerError("selection record format is retired or unsupported; finish or discard the job with the release that created it")
    if record.get("kind") != "agy-worker-selection":
        raise CallerError("selection record kind is invalid")
    mode = record.get("selection_mode")
    fields = set(COMMON_RECORD_FIELDS)
    if mode == "agy-default":
        expected = {"schema_version": SELECTION_SCHEMA, "kind": "agy-worker-selection",
                    "selection_mode": "agy-default", "resolved_agy_model": None}
    elif mode in {"exact-model", "model-effort"}:
        fields |= {"user_model", "user_model_source"}
        if mode == "model-effort":
            fields |= {"user_effort", "user_effort_source"}
        expected = resolve_selection(require_string(record, "user_model"), record.get("user_effort"),
                                     require_string(record, "user_model_source"), record.get("user_effort_source"), probe_version=False)
        expected["selection_mode"] = mode
    else:
        raise CallerError("selection record mode is invalid")
    if "probed_executable" in record or "installed_agy_version" in record:
        fields |= PROBE_FIELDS
        version = require_string(record, "installed_agy_version")
        if len(version.encode("utf-8")) > VERSION_OUTPUT_LIMIT or any(ord(c) < 32 or ord(c) == 127 for c in version):
            raise CallerError("selection diagnostic version is invalid")
        validate_probed_executable(record.get("probed_executable"))
        if not has_current_probed_executable_binding(record["probed_executable"]):
            raise CallerError("selection executable binding is retired")
    require_exact_fields(record, fields)
    if any(record[key] != value for key, value in expected.items()):
        raise CallerError("selection record caller choice is inconsistent")


def validate_selection_record(record: dict[str, Any]) -> None:
    validate_selection_record_shape(record)


def reprobe_selection_record(
    record: dict[str, Any], *, provider_isolation: str = "session", conversation: bool = False,
) -> tuple[str, dict[str, Any]]:
    """Probe every launch and preserve the initial executable authority binding."""
    validate_selection_record_shape(record)
    if "probed_executable" not in record:
        raise CallerError("selection record has no executable binding")
    executable, binding, _version = probe_capabilities(
        provider_isolation=provider_isolation, conversation=conversation,
        effort=record.get("user_effort") is not None,
    )
    if not frozen_executable_binding_matches(record["probed_executable"], binding):
        raise EvidenceUnavailable("agy selection executable changed")
    return executable, binding


def frozen_executable_binding_matches(before: dict[str, Any], after: dict[str, Any]) -> bool:
    """Compare the frozen target bytes and every path authority observation."""

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
    """Read strict caller provenance without provider execution."""

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
    for name in ("model", "effort", "model-source", "effort-source", "provider-isolation", "output", "validate-record", "verify-record-executable"):
        parser.add_argument("--" + name, action="append")
    observation = parser.add_mutually_exclusive_group()
    observation.add_argument("--observe-installed-version", action="store_true")
    observation.add_argument("--probe-interface", action="store_true")
    parser.add_argument("--child-env", action="append", default=[])
    return parser


def main(argv: list[str] | None = None) -> int:
    global ACTIVE_CHILD_ENV
    parser = build_parser()
    if any(arg == "--literal-model" or arg.startswith("--literal-model=") for arg in (sys.argv[1:] if argv is None else argv)):
        parser.error("--literal-model is retired; use --model")
    args = parser.parse_args(argv)
    try:
        ACTIVE_CHILD_ENV = validate_child_environment_names(args.child_env)
        values = {key: one(parser, value, "--" + key.replace("_", "-"), False)
                  for key, value in vars(args).items() if isinstance(value, list) and key != "child_env"}
        if args.observe_installed_version or args.probe_interface:
            if values:
                parser.error("interface observation is mutually exclusive with selection inputs")
            if args.probe_interface:
                _executable, _binding, version = probe_capabilities()
                print(version)
                print("required capabilities: " + " ".join(REQUIRED_AGY_CAPABILITIES))
            else:
                print(probe_installed_version())
            return 0
        def get(key: str) -> str | None:
            return values.get(key)
        for action in ("validate_record", "verify_record_executable"):
            if get(action):
                if set(values) != {action}:
                    parser.error("record operation is mutually exclusive with selection inputs")
                record = read_selection_record(Path(get(action) or ""), frozen=True)
                if action == "verify_record_executable":
                    reprobe_selection_record(record)
                return 0
        provider_isolation = get("provider_isolation") or "session"
        required_agy_capabilities(provider_isolation=provider_isolation)
        model, effort = get("model"), get("effort")
        if model is None:
            if effort is not None or get("model_source") or get("effort_source"):
                parser.error("effort and provenance require --model")
            record = bind_selection({
                "schema_version": SELECTION_SCHEMA, "kind": "agy-worker-selection",
                "selection_mode": "agy-default", "resolved_agy_model": None,
            }, provider_isolation=provider_isolation)
        else:
            record = resolve_selection(model, effort, get("model_source") or "cli",
                (get("effort_source") or "cli") if effort is not None else get("effort_source"),
                probe_version=True, provider_isolation=provider_isolation)
        if get("output"):
            publish_record(Path(get("output") or ""), record)
            print(record.get("resolved_agy_model") or "")
        else:
            print(json.dumps(record, indent=2, sort_keys=True))
        return 0
    except CallerError as exc:
        print(f"model-selection: {exc}", file=sys.stderr)
        return 64
    except EvidenceUnavailable as exc:
        print(f"model-selection: evidence-unavailable - {exc}", file=sys.stderr)
        return 8
    except ProbeInterrupted as exc:
        return 128 + exc.signal_number


if __name__ == "__main__":
    raise SystemExit(main())
