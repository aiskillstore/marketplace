"""Driver-owned check contracts for optional worker self-verification.

The dispatcher owns file binding, candidate lineage and execution authority. This
module handles untrusted JSON and produces feedback without copying process output.
"""
from __future__ import annotations

import dataclasses
import hashlib
import json
import math
import os
from pathlib import Path
import posixpath
import re
import selectors
import signal
import stat
import subprocess
import time
from typing import Any


MAX_MANIFEST_BYTES = 64 * 1024
MAX_CHECKS = 32
CHECK_ID = re.compile(r"[A-Za-z][A-Za-z0-9_-]{0,63}")
SCRIPT_SHELLS = frozenset({"/bin/bash", "/bin/sh"})


class VerificationError(ValueError):
    """A check request cannot be executed under the frozen driver contract."""


@dataclasses.dataclass(frozen=True)
class Check:
    identifier: str
    argv: tuple[str, ...]
    required: bool
    timeout_seconds: float
    output_limit_bytes: int


@dataclasses.dataclass(frozen=True)
class Manifest:
    checks: tuple[Check, ...]
    max_seconds: float


@dataclasses.dataclass(frozen=True)
class CheckResult:
    identifier: str
    outcome: str
    exit_code: int | None
    elapsed_seconds: float
    stdout_bytes: int
    stderr_bytes: int


def run_check(check: Check, prepared: Any, *, containment: Any,
              log_directory: Path, remaining: float) -> CheckResult:
    """Run a confirmed network-free check and retain bounded private raw logs.

    The dispatcher supplies the native containment module and its prepared launch;
    neither is constructed from a worker envelope. Candidate/copy and manifest
    bindings are the dispatcher's responsibility before and after this call.
    """
    if remaining_seconds(remaining, 0, 0) == 0:
        return CheckResult(check.identifier, "not-run", None, 0.0, 0, 0)
    if (prepared.role != containment.ROLE_SELF_VERIFY
            or prepared.network_policy != containment.NETWORK_DENY_ALL
            or prepared.allow_keychain or tuple(prepared.target_argv) != check.argv):
        raise VerificationError("verification containment does not match the approved check")
    directory_info = log_directory.lstat()
    if (not stat.S_ISDIR(directory_info.st_mode) or directory_info.st_uid != os.getuid()
            or stat.S_IMODE(directory_info.st_mode) != 0o700
            or Path(os.path.realpath(log_directory)) != log_directory):
        raise VerificationError("verification log directory must be canonical and owner-private")
    descriptors: dict[str, int] = {}
    process = None
    root_identity = None
    selector = selectors.DefaultSelector()
    sizes = {"stdout": 0, "stderr": 0}
    outcome = "blocked"
    started = time.monotonic()
    try:
        for stream in sizes:
            descriptors[stream] = os.open(
                log_directory / f"{check.identifier}.{stream}",
                os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o600,
            )
        launch = containment.confirm_contained_launch(prepared)
        started = time.monotonic()
        deadline = started + min(remaining, check.timeout_seconds)
        process = subprocess.Popen(
            list(launch.argv), executable=launch.executable, cwd=launch.cwd,
            env=launch.environment, stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True,
            close_fds=True,
        )
        root_identity = containment.bind_new_process_group(process.pid)
        for name in sizes:
            pipe = getattr(process, name)
            os.set_blocking(pipe.fileno(), False)
            selector.register(pipe, selectors.EVENT_READ, name)
        while selector.get_map():
            if time.monotonic() >= deadline:
                outcome = "timeout"
                break
            for key, _events in selector.select(min(0.05, max(0, deadline - time.monotonic()))):
                chunk = os.read(key.fileobj.fileno(), min(65536, check.output_limit_bytes + 1))
                if not chunk:
                    selector.unregister(key.fileobj)
                    continue
                name = key.data
                writable = min(len(chunk), max(0, check.output_limit_bytes - sizes[name]))
                offset = 0
                while offset < writable:
                    count = os.write(descriptors[name], chunk[offset:writable])
                    if count <= 0:
                        raise VerificationError("verification log write failed")
                    offset += count
                sizes[name] += len(chunk)
                if sizes[name] > check.output_limit_bytes:
                    outcome = "output-limit"
                    break
            if outcome == "output-limit":
                break
        else:
            try:
                code = process.wait(timeout=max(0.001, deadline - time.monotonic()))
                # sandbox-exec reports EX_OSERR when the host refuses sandbox
                # activation. Its exit status is also available to the test;
                # that ambiguity needs driver attention, never provider repair.
                outcome = ("passed" if code == 0 else "blocked"
                           if code < 0 or code == 71 else "failed")
            except subprocess.TimeoutExpired:
                outcome = "timeout"
    finally:
        try:
            if process is not None:
                if root_identity is None:
                    # No unbound group signal: kill only our still-unreaped child.
                    process.kill()
                    process.wait(timeout=2)
                    raise VerificationError("verification process lineage could not be bound")
                containment.terminate_bound_process_group(root_identity, signal.SIGKILL)
                process.wait(timeout=2)
                cleanup_deadline = time.monotonic() + 2
                while containment.terminate_bound_process_group(root_identity, signal.SIGKILL):
                    if time.monotonic() >= cleanup_deadline:
                        raise VerificationError("verification descendants remain unconfirmed")
                    time.sleep(0.02)
        finally:
            selector.close()
            if process is not None:
                for stream in (process.stdout, process.stderr):
                    if stream is not None:
                        stream.close()
            for descriptor in descriptors.values():
                try:
                    os.fsync(descriptor)
                finally:
                    os.close(descriptor)
    return CheckResult(check.identifier, outcome, process.returncode if process else None,
                       time.monotonic() - started, sizes["stdout"], sizes["stderr"])


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise VerificationError("duplicate verification manifest key")
        result[key] = value
    return result


def _seconds(value: Any, maximum: float) -> float:
    if type(value) not in (int, float) or not math.isfinite(value) or not 0 < value <= maximum:
        raise VerificationError("verification time limit is invalid")
    return float(value)


def requested_ids(value: Any) -> tuple[str, ...]:
    if not isinstance(value, list) or len(value) > MAX_CHECKS:
        raise VerificationError("requested check IDs must be a bounded array")
    if any(not isinstance(item, str) or CHECK_ID.fullmatch(item) is None for item in value):
        raise VerificationError("requested check ID is invalid")
    if len(set(value)) != len(value):
        raise VerificationError("requested check IDs must be unique")
    return tuple(value)


def parse_manifest(raw: bytes) -> Manifest:
    if not raw or len(raw) > MAX_MANIFEST_BYTES:
        raise VerificationError("verification manifest is empty or oversized")
    try:
        value = json.loads(raw.decode("utf-8", "strict"), object_pairs_hook=_unique_object)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise VerificationError("verification manifest is invalid JSON") from exc
    if not isinstance(value, dict) or set(value) != {"schema_version", "kind", "max_seconds", "checks"}:
        raise VerificationError("verification manifest fields are invalid")
    if type(value["schema_version"]) is not int or value["schema_version"] != 1:
        raise VerificationError("verification manifest version is invalid")
    if value["kind"] != "agy-worker-self-verification":
        raise VerificationError("verification manifest kind is invalid")
    max_seconds = _seconds(value["max_seconds"], 1800)
    items = value["checks"]
    if not isinstance(items, list) or not 1 <= len(items) <= MAX_CHECKS:
        raise VerificationError("verification manifest checks are invalid")
    checks: list[Check] = []
    for item in items:
        if not isinstance(item, dict) or set(item) != {
            "id", "argv", "required", "timeout_seconds", "output_limit_bytes",
        }:
            raise VerificationError("verification check fields are invalid")
        identifier = requested_ids([item["id"]])[0]
        if type(item["required"]) is not bool:
            raise VerificationError("verification required flag is invalid")
        argv = item["argv"]
        if not isinstance(argv, list) or not 1 <= len(argv) <= 64:
            raise VerificationError("verification argv must be a bounded array")
        if any(not isinstance(arg, str) or "\0" in arg for arg in argv):
            raise VerificationError("verification argv contains an invalid argument")
        try:
            argv_size = sum(len(arg.encode("utf-8", "strict")) for arg in argv)
        except UnicodeError as exc:
            raise VerificationError("verification argv is not UTF-8") from exc
        if argv_size > 16384 or not os.path.isabs(argv[0]):
            raise VerificationError("verification executable must be an approved absolute path")
        # Structured argv is not implicit shell authority. The lifecycle uses a
        # trusted toolchain executable and relative arguments inside the copy;
        # workers never provide command text or select the original checkout.
        if argv[0] in SCRIPT_SHELLS:
            if (len(argv) < 2 or not argv[1] or argv[1].startswith(("-", "/"))
                    or ".." in argv[1].split("/") or argv[1] in {".", ".."}
                    or posixpath.normpath(argv[1]) != argv[1]):
                raise VerificationError("shell check must name a normalized relative script without shell options")
        elif os.path.basename(argv[0]) in {"sh", "bash", "zsh", "dash", "ksh", "fish", "csh", "tcsh", "env"}:
            raise VerificationError("verification argv cannot invoke a shell or environment launcher")
        limit = item["output_limit_bytes"]
        if type(limit) is not int or not 1 <= limit <= 65536:
            raise VerificationError("verification output limit is invalid")
        checks.append(Check(identifier, tuple(argv), item["required"],
                            _seconds(item["timeout_seconds"], 300), limit))
    requested_ids([check.identifier for check in checks])
    return Manifest(tuple(checks), max_seconds)


def select_checks(manifest: Manifest, requested: Any) -> tuple[Check, ...]:
    identifiers = set(requested_ids(requested))
    if identifiers - {check.identifier for check in manifest.checks if not check.required}:
        raise VerificationError("requested check is not an approved optional check")
    required = tuple(check for check in manifest.checks if check.required)
    optional = tuple(check for check in manifest.checks if not check.required and check.identifier in identifiers)
    return required + optional


def validate_runtime(manifest: Manifest, worktree: Path) -> None:
    """Reject known unsupported runtimes before spending a provider/check turn."""
    worktree = Path(os.path.realpath(worktree))
    roots = (Path("/bin"), Path("/usr/bin"), Path("/Library/Developer/CommandLineTools"))
    for check in manifest.checks:
        target = Path(os.path.realpath(check.argv[0]))
        if target.is_relative_to(worktree):
            raise VerificationError("check executable must be outside the original candidate")
        if not any(target.is_relative_to(root) for root in roots):
            raise VerificationError("self-verification runtime is outside the qualified system toolchain")


def run_checks(manifest: Manifest, requested: Any, *, containment: Any,
               job_directory: Path, copy_directory: Path,
               log_directory: Path, remaining: float) -> tuple[CheckResult, ...]:
    """Execute one frozen check batch in a fresh driver-owned verification job.

    The lifecycle caller owns the manifest/candidate binding and accounts for the
    entire action's elapsed time. Unknown IDs reject before any launch preparation.
    Neither check failure nor exhausted time causes an implicit provider call.
    The copy must come from the driver's no-hardlink verification-copy builder; native
    directory binding does not make a caller-supplied hardlinked tree safe.
    """
    selected = select_checks(manifest, requested)
    allowance = min(manifest.max_seconds, remaining_seconds(remaining, 0, 0))
    started = time.monotonic()
    if allowance == 0:
        return tuple(CheckResult(check.identifier, "not-run", None, 0.0, 0, 0) for check in selected)
    script_bindings = {check.identifier: _bind_script(copy_directory, check.argv[1])
                       for check in selected if check.argv[0] in SCRIPT_SHELLS}
    results: list[CheckResult] = []
    for attempt, check in enumerate(selected, 1):
        available = remaining_seconds(allowance, 0, time.monotonic() - started)
        if available == 0:
            results.append(CheckResult(check.identifier, "not-run", None, 0.0, 0, 0))
            continue
        if (check.identifier in script_bindings
                and _bind_script(copy_directory, check.argv[1]) != script_bindings[check.identifier]):
            raise VerificationError("approved check script changed before execution")
        prepared = containment.prepare_contained_launch(
            role=containment.ROLE_SELF_VERIFY,
            network_policy=containment.NETWORK_DENY_ALL,
            job_dir=job_directory, attempt=attempt, stage_dir=copy_directory,
            target_executable=check.argv[0], target_argv=check.argv,
            child_environment={}, allow_keychain=False,
        )
        # Executable/profile binding also spends the approved batch budget.
        available = remaining_seconds(allowance, 0, time.monotonic() - started)
        result = run_check(check, prepared, containment=containment,
                           log_directory=log_directory, remaining=available)
        if (check.identifier in script_bindings
                and _bind_script(copy_directory, check.argv[1]) != script_bindings[check.identifier]):
            raise VerificationError("approved check script changed during execution")
        results.append(result)
        if result.outcome not in {"passed", "failed", "not-run"}:
            results.extend(CheckResult(rest.identifier, "not-run", None, 0.0, 0, 0)
                           for rest in selected[attempt:])
            break
    return tuple(results)


def _bind_script(root: Path, relative: str) -> tuple[Any, ...]:
    """Bind a regular check script through no-follow directory descriptors."""
    if (not relative or relative.startswith(("-", "/")) or relative in {".", ".."}
            or ".." in relative.split("/") or posixpath.normpath(relative) != relative):
        raise VerificationError("check script must be a normalized relative child path")
    descriptor = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    script_fd = None
    try:
        parts = relative.split("/")
        for part in parts[:-1]:
            next_descriptor = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                                      dir_fd=descriptor)
            os.close(descriptor)
            descriptor = next_descriptor
        named = os.stat(parts[-1], dir_fd=descriptor, follow_symlinks=False)
        if not stat.S_ISREG(named.st_mode) or named.st_nlink != 1:
            raise VerificationError("check script must be a regular unaliased file")
        script_fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW, dir_fd=descriptor)
        before = os.fstat(script_fd)
        if before != named or before.st_size > 128 * 1024 * 1024:
            raise VerificationError("check script binding is unavailable")
        digest = hashlib.sha256()
        total = 0
        while True:
            block = os.read(script_fd, 1024 * 1024)
            if not block:
                break
            total += len(block)
            if total > 128 * 1024 * 1024:
                raise VerificationError("check script exceeds its byte bound")
            digest.update(block)
        after = os.fstat(script_fd)
        current = os.stat(parts[-1], dir_fd=descriptor, follow_symlinks=False)
        # Reading may update atime; it is not a content/authority coordinate.
        def binding(info: os.stat_result) -> tuple[int, ...]:
            return (info.st_dev, info.st_ino, info.st_mode, info.st_uid, info.st_gid,
                    info.st_nlink, info.st_size, info.st_mtime_ns, info.st_ctime_ns)
        if binding(before) != binding(after) or binding(before) != binding(current):
            raise VerificationError("check script changed while binding")
        return (*binding(after), digest.hexdigest())
    finally:
        if script_fd is not None:
            os.close(script_fd)
        os.close(descriptor)


def command_self_verify(api: Any, job: Path, approve_sha: str, output_format: str,
                        *, containment: Any) -> int:
    """Run one advisory action under the existing dispatcher's locks and bindings.

    ``api`` is the trusted dispatch module adapter, never worker-supplied data.
    A candidate attempt spends its one self-verification action even if execution
    is interrupted. The dispatcher owns recovery of a persisted running phase.
    """
    if not isinstance(approve_sha, str) or re.fullmatch(r"[0-9a-f]{64}", approve_sha) is None:
        raise api.DispatchError("self-verification requires the current state SHA")
    if any(signal.getitimer(signal.ITIMER_REAL)):
        raise api.DispatchError("self-verification cannot replace an existing process timer")
    with api.lifecycle_lock(job, blocking=False):
        started = time.monotonic()
        with api.state_lock(job):
            state, raw, sha = api.load_state(job)
            if sha != approve_sha:
                raise api.DispatchError("dispatch state changed before self-verification")
            if (state["schema_version"] not in {12, 13}
                    or not state["allow_self_verification"]
                    or state["phase"] not in {"awaiting-verification", "repair-failed"}
                    or state["self_verification_run"] >= state["attempt"]):
                raise api.DispatchError("self-verification is unavailable")
            command, candidate_raw = api._bound_current_candidate(job, state)
            if ((state["schema_version"], command["schema_version"])
                    not in {(12, 9), (13, 9), (13, 10)}
                    or not command["allow_self_verification"]
                    or command["workflow"] not in {"task", "project"} or command["boost"]):
                raise api.DispatchError("self-verification was not enabled for this job")
            if api._job_is_inside_worktree(job, command["workdir"]):
                raise api.DispatchError("self-verification job must be outside the candidate")
            manifest = api._bound_self_verification_manifest(command, job)
            worktree = Path(os.path.realpath(command["workdir"]))
            try:
                validate_runtime(manifest, worktree)
            except VerificationError as exc:
                raise api.DispatchError(str(exc)) from None
            requested = json.loads(candidate_raw).get("requested_check_ids", [])
            selected_checks = select_checks(manifest, requested)
            try:
                containment.require_supported_host()
            except containment.ContainmentError as exc:
                raise api.DispatchError(str(exc)) from None
            shell_checks = [check for check in selected_checks if check.argv[0] in SCRIPT_SHELLS]
            if shell_checks and command["provider_scope_path"] is not None:
                _scope, selected_content = _selected_candidate(api, command, state)
                files = {item["path"] for item in selected_content if item["kind"] == "file"}
                if any(check.argv[1] not in files for check in shell_checks):
                    raise api.DispatchError("check script is outside the approved readable scope")
            script_hashes = {check.identifier: _bind_script(worktree, check.argv[1])[-1]
                             for check in shell_checks}
            remaining = remaining_seconds(
                state["max_seconds"], state["elapsed_seconds"],
                state["self_verification_elapsed_seconds"])
            if remaining == 0:
                raise api.DispatchError("dispatch max runtime is exhausted")
            return_phase = state["phase"]
            state, raw, sha = api._transition_locked(job, state, raw, {
                "phase": "self-verifying",
                "continue_available": False,
                "self_verification_run": state["attempt"],
                "self_verification_started_epoch": time.time() - (time.monotonic() - started),
                "self_verification_return_phase": return_phase,
            })
        interrupted = None
        previous_signals = {}
        feedback = None
        status = "blocked"
        blocked_summary = "Self-verification blocked; driver review required."
        previous_timer = None

        def stop(number: int, _frame: Any) -> None:
            nonlocal interrupted
            if interrupted is None:
                interrupted = number
                raise VerificationError("self-verification interrupted")

        def expire(_number: int, _frame: Any) -> None:
            nonlocal blocked_summary
            blocked_summary = "Self-verification time limit reached; driver review required."
            raise VerificationError("self-verification time limit reached")

        try:
            for number in (signal.SIGHUP, signal.SIGINT, signal.SIGTERM):
                previous_signals[number] = signal.getsignal(number)
                signal.signal(number, stop)
            previous_signals[signal.SIGALRM] = signal.getsignal(signal.SIGALRM)
            signal.signal(signal.SIGALRM, expire)
            previous_timer = signal.setitimer(
                signal.ITIMER_REAL, max(0.000001, remaining - (time.monotonic() - started)))
            directory = job / f"self-verify-run-{state['attempt']:03d}"
            directory.mkdir(mode=0o700)
            logs = directory / "logs"
            logs.mkdir(mode=0o700)
            copy = directory / "copy"
            copy, parent_identity = api._verification_copy_destination(copy, Path(command["workdir"]))
            _copy_candidate(api, job, command, state, copy)
            copy_identity = api._identity(copy.lstat())
            if api._identity(directory.lstat()) != parent_identity:
                raise VerificationError("verification copy parent changed")
            if any(_bind_script(copy, check.argv[1])[-1] != script_hashes[check.identifier]
                   for check in shell_checks):
                raise VerificationError("check script copy changed")
            api._bound_current_candidate(job, state)
            if api._bound_self_verification_manifest(command, job) != manifest:
                raise VerificationError("self-verification manifest changed")
            available = remaining_seconds(remaining, 0, time.monotonic() - started)
            if (api._identity(copy.lstat()) != copy_identity
                    or api._identity(directory.lstat()) != parent_identity):
                raise VerificationError("verification copy identity changed")
            results = run_checks(manifest, requested, containment=containment,
                                 job_directory=directory, copy_directory=copy,
                                 log_directory=logs, remaining=available)
            if (api._identity(copy.lstat()) != copy_identity
                    or api._identity(directory.lstat()) != parent_identity):
                raise VerificationError("verification copy identity changed")
            api._bound_current_candidate(job, state)
            if api._bound_self_verification_manifest(command, job) != manifest:
                raise VerificationError("self-verification manifest changed")
            uncertain = next((item for item in results
                              if item.outcome not in {"passed", "failed", "not-run"}), None)
            if uncertain is not None:
                blocked_summary = (f"Self-verification blocked: {uncertain.identifier} "
                                   f"({uncertain.outcome}); driver review required.")
            feedback = advisory_feedback(state["result_sha256"],
                                         [(item.identifier, item.outcome) for item in results])
            status = "completed"
        except (Exception, KeyboardInterrupt):
            # Logs stay local. Binding, execution and containment failures never
            # become model-readable test failures or implicit repair authority.
            feedback = None
        finally:
            if previous_timer is not None:
                signal.setitimer(signal.ITIMER_REAL, 0)
            for number, handler in previous_signals.items():
                signal.signal(number, handler)
            if previous_timer is not None and previous_timer[0] > 0:
                signal.setitimer(signal.ITIMER_REAL, *previous_timer)
        with api.state_lock(job):
            current, current_raw, _current_sha = api.load_state(job)
            if (current_raw != raw or current["phase"] != "self-verifying"
                    or current["self_verification_run"] != state["attempt"]):
                raise api.DispatchError("dispatch state changed during self-verification")
            updates = {
                "phase": return_phase,
                "self_verification_started_epoch": None,
                "self_verification_return_phase": None,
                "check_summary": blocked_summary,
                "verification_path": None, "verification_sha256": None,
                "verification_identity": None,
                "check_counts": api._verification_counts(advisory_feedback(state["result_sha256"], [])),
            }
            path = None
            identity = None
            if feedback is not None:
                # Rebind after reacquiring the state lock before publishing any
                # feedback for this candidate. The raw logs are never embedded.
                api._bound_current_candidate(job, current)
                if api._bound_self_verification_manifest(command, job) != manifest:
                    raise api.DispatchError("self-verification manifest changed before publication")
                path, verification_sha, identity = api._write_verification(
                    job, f"self-verify-{state['attempt']:03d}", feedback)
                updates.update({
                    "verification_path": str(path), "verification_sha256": verification_sha,
                    "verification_identity": list(identity), "check_summary": feedback["summary"],
                    "check_counts": api._verification_counts(feedback),
                })
            updates["self_verification_elapsed_seconds"] = (
                state["self_verification_elapsed_seconds"] + min(
                    time.monotonic() - started,
                    remaining_seconds(state["max_seconds"], state["elapsed_seconds"],
                                      state["self_verification_elapsed_seconds"])))
            updates["continue_available"] = api._continue_from_facts(
                {**current, **updates}, time.time())
            try:
                state, _raw, sha = api._transition_locked(job, current, current_raw, updates)
            except BaseException:
                api._discard_new_verification(path, identity)
                raise
        api.print_control_status(state, sha, output_format, job=job)
        if interrupted is not None:
            return 128 + interrupted
        return 0 if status == "completed" else 20


def _copy_candidate(api: Any, job: Path, command: dict[str, Any],
                    state: dict[str, Any], destination: Path) -> None:
    """Reuse the existing selected copier so checks cannot read omitted files."""
    if command["provider_scope_path"] is None:
        api._copy_bound_candidate(Path(command["workdir"]), destination)
        return
    scope, selected = _selected_candidate(api, command, state)
    identity, observed = api._materialize_stage(command["workdir"], destination, scope, selected)
    info = destination.lstat()
    if (observed != state["selected_content_sha256"] or identity != (
            info.st_dev, info.st_ino, info.st_uid, info.st_gid, info.st_mode)):
        raise VerificationError("self-verification copy does not match the selected candidate")
    api._bound_current_candidate(job, state)


def _selected_candidate(api: Any, command: dict[str, Any], state: dict[str, Any]) -> tuple[Any, Any]:
    _path, raw_scope, info = api._read_provider_scope_file(
        command["provider_scope_path"], api.MAX_COMMAND_BYTES)
    if (api.digest(raw_scope) != command["provider_scope_sha256"]
            or list(api._identity(info)) != command["provider_scope_identity"]):
        raise VerificationError("self-verification provider scope changed")
    scope = api._parse_provider_scope(raw_scope)
    selected = api._build_selected_content_manifest(command["workdir"], scope)
    expected = state["selected_content_sha256"]
    if (api._selected_content_digest(selected) != expected
            or sum(item["kind"] == "file" for item in selected) != state["selected_file_count"]
            or sum(item["kind"] == "directory" for item in selected) != state["selected_tree_count"]):
        raise VerificationError("self-verification selected candidate changed")
    return scope, selected


def remaining_seconds(max_seconds: float, provider_elapsed: float, verification_elapsed: float) -> float:
    for value in (max_seconds, provider_elapsed, verification_elapsed):
        if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
            raise VerificationError("verification runtime budget is invalid")
    return max(0.0, max_seconds - provider_elapsed - verification_elapsed)


def advisory_feedback(candidate_sha256: str, results: list[tuple[str, str]]) -> dict[str, Any]:
    if not isinstance(candidate_sha256, str) or re.fullmatch(r"[0-9a-f]{64}", candidate_sha256) is None:
        raise VerificationError("verification candidate binding is invalid")
    requested_ids([identifier for identifier, _outcome in results])
    if any(outcome not in {"passed", "failed", "not-run"} for _identifier, outcome in results):
        # Containment, timeout and other runner failures must return to the
        # driver rather than masquerade as a test failure for provider repair.
        raise VerificationError("verification execution needs driver attention")
    passed = [identifier for identifier, outcome in results if outcome == "passed"]
    failed = [identifier for identifier, outcome in results if outcome == "failed"]
    missing = sum(outcome == "not-run" for _identifier, outcome in results)
    return {
        "schema_version": 2,
        "candidate_sha256": candidate_sha256,
        "summary": f"Advisory self-verification: {len(passed)} passed, {len(failed)} failed, {missing} not run.",
        "passed_checks": passed,
        "failed_checks": failed,
        "advisory_checks": len(results),
        "missing_checks": missing,
        "coverage": "partial",
        "verified_findings": 0,
        "unresolved_gaps": missing,
        "diff_review_complete": False,
    }
