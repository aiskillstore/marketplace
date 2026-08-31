#!/usr/bin/env python3
"""Privacy-safe, version-pinned Codex CLI 0.150.1 usage observation tool.

Public CLI:
    codex-usage-report.sh --task LABEL=THREAD_ID [--session LABEL=ABS_FILE]... [--account-usage] [--format json|text]

Pins Codex CLI 0.150.1 and the generated experimental app-server schema digest:
    EXPERIMENTAL_APP_SERVER_SCHEMA_SHA256 = "e9bad0a20736e7d3aba18c0f04bef59856fb212ae21049fe17d786682203cfae"

Performs bounded preflight checking:
- Runs `codex --version` and validates 0.150.1.
- Runs `codex app-server generate-json-schema --experimental --out DIR` in a private temporary directory and verifies SHA-256 digest.
- Interacts with live stdio app-server (without jsonrpc member).
- Parses exact session JSONL topology with separated protocol (64KB) and session (2MB) line limits.
- Enforces strict fail-closed privacy, process cleanup, and error sanitization (never echoes paths, userAgent, or prose).
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import pathlib
import re
import selectors
import signal
import stat
import subprocess
import sys
import tempfile
import time
from typing import Any, Optional, Sequence


PINNED_CODEX_VERSION = "0.150.1"
EXPERIMENTAL_APP_SERVER_SCHEMA_SHA256 = "e9bad0a20736e7d3aba18c0f04bef59856fb212ae21049fe17d786682203cfae"

PROTOCOL_TIMEOUT_SECONDS = 10.0
MAX_STREAM_BYTES = 1024 * 1024
MAX_PROTOCOL_LINE_BYTES = 65536
MAX_SESSION_LINE_BYTES = 2 * 1024 * 1024
MAX_SESSION_FILE_BYTES = 20 * 1024 * 1024
MAX_SCHEMA_BYTES = 32 * 1024 * 1024

LABEL_RE = re.compile(r"^[a-zA-Z0-9_-]{1,64}\Z")
THREAD_ID_RE = re.compile(r"^[a-zA-Z0-9_-]{1,128}\Z")
USER_AGENT_RE = re.compile(r"(?i)\b(?:codex|codex\s+desktop|codex-cli)/([0-9]+\.[0-9]+\.[0-9]+)\b")

ALLOWLISTED_TOOLS = frozenset({
    "exec",
    "followup_task",
    "list_agents",
    "request_user_input",
    "send_message",
    "spawn_agent",
    "wait",
    "wait_agent",
})


def _canonical(value: object) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("ascii")
        + b"\n"
    )


class UsageObservationError(ValueError):
    """Raised when usage observation encounters invalid data, drift, or violations."""
    pass


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise UsageObservationError("duplicate JSON object key")
        result[key] = value
    return result


def _json_loads_strict(data: bytes, max_bytes: int = MAX_PROTOCOL_LINE_BYTES) -> dict[str, Any]:
    if not data or len(data) > max_bytes:
        raise UsageObservationError("JSON payload exceeds size limit or is empty")
    try:
        val = json.loads(data.decode("utf-8", "strict"), object_pairs_hook=_reject_duplicate_keys)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise UsageObservationError("invalid JSON syntax or encoding") from exc
    if not isinstance(val, dict):
        raise UsageObservationError("JSON root must be an object")
    return val


def _normalize_abs_path(path_str: str) -> str:
    if not isinstance(path_str, str) or not path_str or not os.path.isabs(path_str):
        raise UsageObservationError("path must be non-empty absolute")
    norm = os.path.normpath(path_str)
    if norm != path_str:
        raise UsageObservationError("path is not normalized")
    try:
        real = os.path.realpath(path_str)
    except OSError as exc:
        raise UsageObservationError("cannot resolve real path") from exc
    if real != path_str:
        raise UsageObservationError("path contains symlinks")
    return path_str


def _close_process_group(process: subprocess.Popen[bytes], pgid: int) -> None:
    """Safely terminate child streams and process group."""
    try:
        if process.stdin and not process.stdin.closed:
            process.stdin.close()
    except Exception:
        pass
    try:
        if process.stdout and not process.stdout.closed:
            process.stdout.close()
    except Exception:
        pass
    try:
        if process.stderr and not process.stderr.closed:
            process.stderr.close()
    except Exception:
        pass

    if process.returncode is None:
        try:
            os.killpg(pgid, signal.SIGTERM)
        except (ProcessLookupError, PermissionError):
            pass
        time.sleep(0.05)
        try:
            os.killpg(pgid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass
        try:
            process.wait(timeout=0.5)
        except (subprocess.TimeoutExpired, OSError):
            pass


def _run_bounded_command(
    cmd: list[str],
    cwd: Optional[str] = None,
    timeout: float = PROTOCOL_TIMEOUT_SECONDS,
    max_bytes: int = MAX_STREAM_BYTES,
) -> bytes:
    """Run a child command safely with bounds, process group, and sanitized errors."""
    try:
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=cwd,
            start_new_session=True,
            close_fds=True,
        )
    except (FileNotFoundError, OSError) as exc:
        raise UsageObservationError("failed to spawn child process") from exc

    pgid = process.pid
    selector = selectors.DefaultSelector()
    stdout_data = bytearray()
    stderr_data = bytearray()
    try:
        if process.stdout is None or process.stderr is None:
            raise UsageObservationError("child process streams unavailable")
        for stream, sink in ((process.stdout, stdout_data), (process.stderr, stderr_data)):
            os.set_blocking(stream.fileno(), False)
            selector.register(stream.fileno(), selectors.EVENT_READ, sink)

        deadline = time.monotonic() + timeout
        while selector.get_map():
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise UsageObservationError("child process timed out")
            events = selector.select(min(remaining, 0.1))
            if not events:
                continue
            for key, _ in events:
                block = os.read(key.fd, 65536)
                if not block:
                    selector.unregister(key.fd)
                    continue
                sink = key.data
                sink.extend(block)
                if len(sink) > max_bytes:
                    raise UsageObservationError("child process output exceeded stream limit")

        try:
            return_code = process.wait(timeout=max(0.1, deadline - time.monotonic()))
        except subprocess.TimeoutExpired as exc:
            raise UsageObservationError("child process timed out") from exc
        if return_code != 0:
            raise UsageObservationError("child process exited with non-zero status")
        return bytes(stdout_data)
    finally:
        selector.close()
        _close_process_group(process, pgid)


def preflight_codex_schema(
    codex_bin: str = "codex",
    expected_version: str = PINNED_CODEX_VERSION,
    expected_digest: str = EXPERIMENTAL_APP_SERVER_SCHEMA_SHA256,
) -> str:
    """Perform preflight verification of Codex CLI version and generated schema digest."""
    ver_out = _run_bounded_command([codex_bin, "--version"])
    expected_version_line = f"codex-cli {expected_version}\n".encode("ascii")
    if ver_out != expected_version_line:
        raise UsageObservationError("Codex CLI version drift detected")

    with tempfile.TemporaryDirectory(prefix="agy-codex-schema-") as temp_dir:
        temp_path = pathlib.Path(temp_dir)
        os.chmod(str(temp_path), 0o700)

        _run_bounded_command(
            [
                codex_bin,
                "app-server",
                "generate-json-schema",
                "--experimental",
                "--out",
                str(temp_path),
            ],
            cwd=str(temp_path),
        )

        schema_path = temp_path / "codex_app_server_protocol.schemas.json"
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
        try:
            schema_fd = os.open(str(schema_path), flags)
        except OSError as exc:
            raise UsageObservationError("generated combined schema is unavailable") from exc
        try:
            schema_stat = os.fstat(schema_fd)
            if (
                not stat.S_ISREG(schema_stat.st_mode)
                or schema_stat.st_uid != os.getuid()
                or schema_stat.st_nlink != 1
                or not (1 <= schema_stat.st_size <= MAX_SCHEMA_BYTES)
            ):
                raise UsageObservationError("generated combined schema metadata is invalid")
            schema_bytes = bytearray()
            while len(schema_bytes) <= MAX_SCHEMA_BYTES:
                block = os.read(schema_fd, min(65536, MAX_SCHEMA_BYTES + 1 - len(schema_bytes)))
                if not block:
                    break
                schema_bytes.extend(block)
            if len(schema_bytes) != schema_stat.st_size or len(schema_bytes) > MAX_SCHEMA_BYTES:
                raise UsageObservationError("generated combined schema size changed or exceeded limit")
        finally:
            os.close(schema_fd)

        calculated_digest = hashlib.sha256(bytes(schema_bytes)).hexdigest()
        if calculated_digest != expected_digest:
            raise UsageObservationError("generated schema digest mismatch")

        return calculated_digest


def _get_nullable_int(data: dict[str, Any], *key_variants: str) -> Optional[int]:
    for key in key_variants:
        if key in data:
            val = data[key]
            if val is None:
                return None
            if type(val) is not int or val < 0:
                raise UsageObservationError("invalid integer counter value")
            return val
    return None


def _sum_nullable(values: list[Optional[int]]) -> Optional[int]:
    if not values or any(value is None for value in values):
        return None
    return sum(value for value in values if value is not None)


def parse_thread_usage_dict(
    raw: Any,
    expected_thread_id: Optional[str] = None,
) -> Optional[dict[str, Any]]:
    """Validate the exact Codex 0.150.1 threadUsage response without emitting its ID."""
    if raw is None:
        return None
    if not isinstance(raw, dict):
        raise UsageObservationError("threadUsage must be an object")

    thread_id = raw.get("threadId")
    if not isinstance(thread_id, str) or not thread_id:
        raise UsageObservationError("threadUsage is missing its thread binding")
    if expected_thread_id is not None and thread_id != expected_thread_id:
        raise UsageObservationError("threadUsage response does not match the requested thread")
    estimated_credits = _get_nullable_int(raw, "estimatedUsageCreditsMicros")
    if estimated_credits is None:
        raise UsageObservationError("threadUsage is missing estimated usage credits")

    groups = raw.get("groups")
    if not isinstance(groups, list):
        raise UsageObservationError("threadUsage groups are invalid")

    group_inputs: list[Optional[int]] = []
    group_cached: list[Optional[int]] = []
    group_net_new: list[Optional[int]] = []
    group_outputs: list[Optional[int]] = []
    for group in groups:
        if not isinstance(group, dict):
            raise UsageObservationError("threadUsage group is invalid")
        if _get_nullable_int(group, "estimatedUsageCreditsMicros") is None:
            raise UsageObservationError("threadUsage group is missing estimated usage credits")
        input_tokens = _get_nullable_int(group, "inputTokens")
        cached_tokens = _get_nullable_int(group, "cachedInputTokens")
        net_new_tokens = _get_nullable_int(group, "netNewInputTokens")
        output_tokens = _get_nullable_int(group, "outputTokens")
        if input_tokens is not None and cached_tokens is not None:
            if cached_tokens > input_tokens:
                raise UsageObservationError("cached input exceeds input in threadUsage group")
            if net_new_tokens is not None and net_new_tokens != input_tokens - cached_tokens:
                raise UsageObservationError("net-new input is inconsistent in threadUsage group")
        group_inputs.append(input_tokens)
        group_cached.append(cached_tokens)
        group_net_new.append(net_new_tokens)
        group_outputs.append(output_tokens)

    total_input = _sum_nullable(group_inputs)
    total_cached = _sum_nullable(group_cached)
    total_net_new = _sum_nullable(group_net_new)
    total_output = _sum_nullable(group_outputs)
    if total_net_new is None and total_input is not None and total_cached is not None:
        total_net_new = total_input - total_cached

    return {
        "status": "available",
        "input_tokens": total_input,
        "cached_input_tokens": total_cached,
        "net_new_input_tokens": total_net_new,
        "cache_write_input_tokens": None,
        "output_tokens": total_output,
        "reasoning_output_tokens": None,
        "reasoning_is_subset_of_output": True,
        "estimated_credits_micros": estimated_credits,
        "estimate_label": "provider_estimate",
    }


def _parse_window(w: Any, name: str) -> dict[str, Any]:
    if not isinstance(w, dict):
        raise UsageObservationError("rate limits window must be an object")
    win_mins = w.get("windowDurationMins")
    if win_mins is not None and (type(win_mins) is not int or win_mins <= 0):
        raise UsageObservationError("invalid windowDurationMins in rate limits")

    used_pct = w.get("usedPercent")
    if type(used_pct) is not int or not 0 <= used_pct <= 100:
        raise UsageObservationError("invalid usedPercent in rate limits")

    resets_at = w.get("resetsAt")
    if resets_at is not None and (type(resets_at) is not int or resets_at < 0):
        raise UsageObservationError("invalid resetsAt in rate limits")

    return {
        "window_duration_mins": win_mins,
        "used_percent": used_pct,
        "resets_at": resets_at,
    }


def parse_rate_limits_dict(raw: Any) -> dict[str, Any]:
    """Validate Codex 0.150.1 rate limits object (primary/secondary windowDurationMins, usedPercent, resetsAt)."""
    if not isinstance(raw, dict):
        raise UsageObservationError("rateLimits must be an object")

    primary_raw = raw.get("primary")
    if primary_raw is not None and not isinstance(primary_raw, dict):
        raise UsageObservationError("rateLimits primary window is invalid")
    primary = _parse_window(primary_raw, "primary") if primary_raw is not None else None
    res: dict[str, Any] = {"primary": primary}

    secondary_raw = raw.get("secondary")
    if secondary_raw is not None and not isinstance(secondary_raw, dict):
        raise UsageObservationError("rateLimits secondary window is invalid")
    if isinstance(secondary_raw, dict):
        res["secondary"] = _parse_window(secondary_raw, "secondary")
    else:
        res["secondary"] = None

    return res


def parse_session_file(abs_file_path: str) -> dict[str, Any]:
    """Parse one owner-private regular session file strictly using exact 0.150.1 topology."""
    norm_path = _normalize_abs_path(abs_file_path)
    no_follow = getattr(os, "O_NOFOLLOW", 0)
    cloexec = getattr(os, "O_CLOEXEC", 0)

    try:
        fd = os.open(norm_path, os.O_RDONLY | no_follow | cloexec)
    except OSError as exc:
        raise UsageObservationError("cannot open session file") from exc

    try:
        st = os.fstat(fd)
        if not stat.S_ISREG(st.st_mode):
            raise UsageObservationError("session file is not a regular file")
        if st.st_uid != os.getuid():
            raise UsageObservationError("session file is not owned by current user")
        if (stat.S_IMODE(st.st_mode) & 0o077) != 0:
            raise UsageObservationError("session file has non-private permissions")
        if st.st_nlink != 1:
            raise UsageObservationError("session file has hard links")
        if st.st_size > MAX_SESSION_FILE_BYTES:
            raise UsageObservationError("session file exceeds size bound")

        raw_buffer = bytearray()
        while len(raw_buffer) <= MAX_SESSION_FILE_BYTES:
            block = os.read(fd, min(65536, MAX_SESSION_FILE_BYTES + 1 - len(raw_buffer)))
            if not block:
                break
            raw_buffer.extend(block)
        after = os.fstat(fd)
        stable_fields = ("st_dev", "st_ino", "st_uid", "st_mode", "st_nlink", "st_size", "st_mtime_ns", "st_ctime_ns")
        if (
            len(raw_buffer) != st.st_size
            or len(raw_buffer) > MAX_SESSION_FILE_BYTES
            or any(getattr(st, field) != getattr(after, field) for field in stable_fields)
        ):
            raise UsageObservationError("session file size changed during read")
        raw_bytes = bytes(raw_buffer)

    finally:
        os.close(fd)

    lines = raw_bytes.split(b"\n")
    cli_version_observed: Optional[str] = None
    tool_counts: dict[str, int] = {}
    wait_count = 0
    seen_event_ids: set[str] = set()
    seen_ordinals: set[int] = set()
    last_ordinal: Optional[int] = None
    records_observed = 0
    token_snapshots_observed = 0
    timestamp_records_observed = 0
    first_timestamp: Optional[datetime.datetime] = None
    last_timestamp: Optional[datetime.datetime] = None

    last_input = 0
    last_cached = 0
    last_cw = 0
    last_output = 0
    last_reasoning = 0
    latest_phase: Optional[dict[str, int]] = None

    for line in lines:
        line = line.strip()
        if not line:
            continue
        obj = _json_loads_strict(line, max_bytes=MAX_SESSION_LINE_BYTES)
        records_observed += 1

        if "timestamp" in obj:
            timestamp = obj["timestamp"]
            if not isinstance(timestamp, str) or not timestamp.endswith("Z"):
                raise UsageObservationError("session timestamp is invalid")
            try:
                parsed_timestamp = datetime.datetime.fromisoformat(timestamp[:-1] + "+00:00")
            except ValueError as exc:
                raise UsageObservationError("session timestamp is invalid") from exc
            if parsed_timestamp.tzinfo is None or parsed_timestamp.utcoffset() != datetime.timedelta(0):
                raise UsageObservationError("session timestamp is invalid")
            if last_timestamp is not None and parsed_timestamp < last_timestamp:
                raise UsageObservationError("session timestamp regressed")
            if first_timestamp is None:
                first_timestamp = parsed_timestamp
            last_timestamp = parsed_timestamp
            timestamp_records_observed += 1

        if "ordinal" in obj:
            ordinal = obj["ordinal"]
            if type(ordinal) is not int or ordinal < 0:
                raise UsageObservationError("session ordinal is invalid")
            if ordinal in seen_ordinals or (last_ordinal is not None and ordinal <= last_ordinal):
                raise UsageObservationError("session ordinal is duplicate or out of order")
            seen_ordinals.add(ordinal)
            last_ordinal = ordinal

        if "id" in obj and isinstance(obj["id"], str):
            event_id = obj["id"]
            if event_id in seen_event_ids:
                raise UsageObservationError("duplicate event ID in session")
            seen_event_ids.add(event_id)

        obj_type = obj.get("type")
        payload = obj.get("payload") if isinstance(obj.get("payload"), dict) else obj

        # Check session_meta
        if obj_type == "session_meta" or "session_meta" in obj or "cli_version" in payload:
            meta = payload if ("cli_version" in payload) else (obj.get("session_meta") or {})
            if isinstance(meta, dict) and "cli_version" in meta:
                ver = meta["cli_version"]
                if not isinstance(ver, str):
                    raise UsageObservationError("session cli_version must be a string")
                if cli_version_observed is not None and cli_version_observed != ver:
                    raise UsageObservationError("conflicting cli_version in session")
                cli_version_observed = ver

        # Check tools
        tool_name = None
        if (
            obj_type == "response_item"
            and isinstance(payload, dict)
            and payload.get("type") in {"function_call", "custom_tool_call"}
        ):
            tool_name = payload.get("name")

        if tool_name is not None:
            if tool_name in ALLOWLISTED_TOOLS:
                tool_counts[tool_name] = tool_counts.get(tool_name, 0) + 1
            if tool_name in {"wait", "sleep"}:
                wait_count += 1

        # Check token counts
        tc = None
        phase_tc = None
        if obj_type == "event_msg" and isinstance(payload, dict) and payload.get("type") == "token_count":
            info = payload.get("info")
            if isinstance(info, dict):
                tc = info.get("total_token_usage")
                phase_tc = info.get("last_token_usage")

        if isinstance(tc, dict):
            token_snapshots_observed += 1
            required_total_keys = (
                "input_tokens",
                "cached_input_tokens",
                "cache_write_input_tokens",
                "output_tokens",
                "reasoning_output_tokens",
                "total_tokens",
            )
            if any(key not in tc or _get_nullable_int(tc, key) is None for key in required_total_keys):
                raise UsageObservationError("total token usage is missing a required counter")
            in_val = tc["input_tokens"]
            c_val = tc["cached_input_tokens"]
            cw_val = tc["cache_write_input_tokens"]
            out_val = tc["output_tokens"]
            res_val = tc["reasoning_output_tokens"]

            if in_val < last_input:
                raise UsageObservationError("input tokens regressed in session")
            if out_val < last_output:
                raise UsageObservationError("output tokens regressed in session")
            if c_val < last_cached:
                raise UsageObservationError("cached input tokens regressed in session")
            if cw_val < last_cw:
                raise UsageObservationError("cache-write input tokens regressed in session")
            if res_val < last_reasoning:
                raise UsageObservationError("reasoning tokens regressed in session")

            if c_val > in_val:
                raise UsageObservationError("cached tokens exceed input tokens in session")
            if res_val > out_val:
                raise UsageObservationError("reasoning tokens exceed output tokens in session")

            last_input = in_val
            last_cached = c_val
            last_cw = cw_val
            last_output = out_val
            last_reasoning = res_val

            if isinstance(phase_tc, dict):
                if any(key not in phase_tc or _get_nullable_int(phase_tc, key) is None for key in required_total_keys):
                    raise UsageObservationError("phase token usage is missing a required counter")
                phase_input = phase_tc["input_tokens"]
                phase_cached = phase_tc["cached_input_tokens"]
                phase_cw = phase_tc["cache_write_input_tokens"]
                phase_output = phase_tc["output_tokens"]
                phase_reasoning = phase_tc["reasoning_output_tokens"]
                if phase_cached > phase_input:
                    raise UsageObservationError("cached tokens exceed input tokens in phase window")
                if phase_reasoning > phase_output:
                    raise UsageObservationError("reasoning tokens exceed output tokens in phase window")
                latest_phase = {
                    "input_tokens": phase_input,
                    "cached_input_tokens": phase_cached,
                    "net_new_input_tokens": phase_input - phase_cached,
                    "cache_write_input_tokens": phase_cw,
                    "output_tokens": phase_output,
                    "reasoning_output_tokens": phase_reasoning,
                    "reasoning_is_subset_of_output": True,
                }

    if cli_version_observed is None or cli_version_observed != PINNED_CODEX_VERSION:
        raise UsageObservationError(
            f"session cli_version mismatch: expected {PINNED_CODEX_VERSION}"
        )

    net_new = last_input - last_cached
    if timestamp_records_observed not in {0, records_observed}:
        raise UsageObservationError("session timestamps are incomplete")
    duration_ms = None
    if first_timestamp is not None and last_timestamp is not None:
        duration_ms = int((last_timestamp - first_timestamp).total_seconds() * 1000)

    return {
        "status": "available",
        "cli_version": cli_version_observed,
        "tool_calls": tool_counts,
        "wait_count": wait_count,
        "token_count": {
            "input_tokens": last_input,
            "cached_input_tokens": last_cached,
            "net_new_input_tokens": net_new,
            "cache_write_input_tokens": last_cw,
            "output_tokens": last_output,
            "reasoning_output_tokens": last_reasoning,
            "reasoning_is_subset_of_output": True,
        },
        "last_phase_token_count": latest_phase,
        "measurement_window": {
            "basis": "explicit_session_records",
            "records_observed": records_observed,
            "token_snapshots_observed": token_snapshots_observed,
            "duration_ms": duration_ms,
        },
    }


def query_app_server(
    tasks: list[tuple[str, str]],
    query_account_usage: bool = False,
    app_server_cmd: Optional[list[str]] = None,
) -> dict[str, Any]:
    """Execute live interaction with Codex 0.150.1 app-server stdio (no jsonrpc member)."""
    if app_server_cmd is None:
        app_server_cmd = ["codex", "app-server"]

    try:
        process = subprocess.Popen(
            app_server_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
            close_fds=True,
        )
    except (FileNotFoundError, OSError) as exc:
        raise UsageObservationError("failed to spawn codex app-server") from exc

    pgid = process.pid
    if process.stdin is None or process.stdout is None or process.stderr is None:
        _close_process_group(process, pgid)
        raise UsageObservationError("app-server stdio streams unavailable")

    selector = selectors.DefaultSelector()
    selector.register(process.stdout.fileno(), selectors.EVENT_READ, "stdout")
    selector.register(process.stderr.fileno(), selectors.EVENT_READ, "stderr")
    os.set_blocking(process.stdout.fileno(), False)
    os.set_blocking(process.stderr.fileno(), False)

    req_id_seq = 1
    pending_requests: dict[int, str] = {}
    responses: dict[int, dict[str, Any]] = {}
    raw_buffer = bytearray()
    stderr_bytes = 0
    deadline = time.monotonic() + PROTOCOL_TIMEOUT_SECONDS

    def send_msg(msg: dict[str, Any]) -> None:
        payload = _canonical(msg)
        assert process.stdin is not None
        process.stdin.write(payload)
        process.stdin.flush()

    def read_responses() -> None:
        nonlocal raw_buffer, stderr_bytes
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise UsageObservationError("app-server protocol communication timed out")
            events = selector.select(min(remaining, 0.05))
            if not events:
                if process.poll() is not None:
                    break
                if not pending_requests:
                    break
                continue
            for key, _ in events:
                block = os.read(key.fd, 4096)
                if not block:
                    selector.unregister(key.fd)
                    continue
                if key.data == "stderr":
                    stderr_bytes += len(block)
                    if stderr_bytes > MAX_STREAM_BYTES:
                        raise UsageObservationError("app-server error output exceeded stream bound")
                    continue
                raw_buffer.extend(block)
                if len(raw_buffer) > MAX_STREAM_BYTES:
                    raise UsageObservationError("app-server output exceeded stream bound")

                while b"\n" in raw_buffer:
                    line, raw_buffer = raw_buffer.split(b"\n", 1)
                    line = line.strip()
                    if not line:
                        continue
                    msg = _json_loads_strict(line, max_bytes=MAX_PROTOCOL_LINE_BYTES)
                    if "id" in msg:
                        resp_id = msg["id"]
                        if type(resp_id) is not int:
                            raise UsageObservationError("malformed response id")
                        if resp_id in responses:
                            raise UsageObservationError("duplicate response id received")
                        if resp_id not in pending_requests:
                            raise UsageObservationError("unexpected response id received")
                        if "error" in msg and msg["error"] is not None:
                            raise UsageObservationError("app-server returned error")
                        responses[resp_id] = msg
                        pending_requests.pop(resp_id, None)

            if not pending_requests:
                break

    try:
        # Step 1: initialize (no jsonrpc member)
        init_id = req_id_seq
        req_id_seq += 1
        pending_requests[init_id] = "initialize"
        send_msg({
            "id": init_id,
            "method": "initialize",
            "params": {
                "capabilities": {"experimentalApi": True},
                "clientInfo": {"name": "codex-agy-worker", "version": "0.14.0"},
            },
        })
        read_responses()

        init_resp = responses.get(init_id)
        if init_resp is None:
            raise UsageObservationError("initialize response missing")
        result = init_resp.get("result")
        if not isinstance(result, dict):
            raise UsageObservationError("initialize result must be an object")

        user_agent = result.get("userAgent") or result.get("user_agent")
        if not isinstance(user_agent, str) or not user_agent:
            raise UsageObservationError("initialize response missing userAgent")

        m = USER_AGENT_RE.search(user_agent)
        if not m:
            raise UsageObservationError("cannot parse Codex version from userAgent")
        observed_version = m.group(1)
        if observed_version != PINNED_CODEX_VERSION:
            raise UsageObservationError(
                f"Codex server version drift: observed version != expected {PINNED_CODEX_VERSION}"
            )

        # Step 2: initialized notification
        send_msg({"method": "initialized"})

        # Step 3: per-task usage reads
        task_req_map: dict[int, str] = {}
        task_thread_ids: dict[str, str] = {}
        for label, thread_id in tasks:
            req_id = req_id_seq
            req_id_seq += 1
            task_req_map[req_id] = label
            task_thread_ids[label] = thread_id
            pending_requests[req_id] = f"usage:{label}"
            send_msg({
                "id": req_id,
                "method": "account/usage/read",
                "params": {"threadId": thread_id},
            })

        # Step 4: account usage / rate limits
        rate_limits_req_id: Optional[int] = None
        if query_account_usage:
            rate_limits_req_id = req_id_seq
            req_id_seq += 1
            pending_requests[rate_limits_req_id] = "rateLimits"
            send_msg({
                "id": rate_limits_req_id,
                "method": "account/rateLimits/read",
            })

        read_responses()

        task_results: dict[str, Any] = {}
        for req_id, label in task_req_map.items():
            resp = responses.get(req_id)
            if resp is None:
                raise UsageObservationError("missing response for task")
            res_obj = resp.get("result")
            if not isinstance(res_obj, dict):
                raise UsageObservationError("invalid result object for task")
            if "summary" not in res_obj or not isinstance(res_obj["summary"], dict):
                raise UsageObservationError("task usage response is missing summary")

            if "threadUsage" in res_obj and res_obj["threadUsage"] is None:
                raise UsageObservationError("explicit threadUsage: null fails closed")
            thread_usage_val = res_obj.get("threadUsage")
            parsed_usage = parse_thread_usage_dict(
                thread_usage_val,
                expected_thread_id=task_thread_ids[label],
            )
            if parsed_usage is None:
                task_results[label] = {
                    "status": "unavailable",
                    "reasoning_is_subset_of_output": True,
                }
            else:
                task_results[label] = parsed_usage

        rate_limits_result = None
        account_usage_result = None
        if query_account_usage:
            assert rate_limits_req_id is not None
            rl_resp = responses.get(rate_limits_req_id)
            if rl_resp is None:
                raise UsageObservationError("missing rate limits response")
            rl_result_obj = rl_resp.get("result")
            if not isinstance(rl_result_obj, dict):
                raise UsageObservationError("rate limits result must be an object")
            if "rateLimits" not in rl_result_obj:
                raise UsageObservationError("rate limits response is missing rateLimits")
            rl_data = rl_result_obj["rateLimits"]
            rate_limits_result = parse_rate_limits_dict(rl_data)
            account_usage_result = {
                "rate_limits": rate_limits_result,
            }

        return {
            "codex_version": PINNED_CODEX_VERSION,
            "tasks": task_results,
            "account_usage": account_usage_result,
        }

    finally:
        selector.close()
        _close_process_group(process, pgid)


def build_usage_report(
    tasks: list[tuple[str, str]],
    sessions: list[tuple[str, str]],
    query_account_usage: bool = False,
    app_server_cmd: Optional[list[str]] = None,
    codex_bin: str = "codex",
    skip_schema_preflight: bool = False,
) -> dict[str, Any]:
    """Combine app-server thread usage observation with session file parsing."""
    if not tasks:
        raise UsageObservationError("at least one --task LABEL=THREAD_ID is required")

    task_labels = [lbl for lbl, _ in tasks]
    if len(task_labels) != len(set(task_labels)):
        raise UsageObservationError("duplicate task labels are prohibited")
    task_thread_ids = [thread_id for _, thread_id in tasks]
    if len(task_thread_ids) != len(set(task_thread_ids)):
        raise UsageObservationError("duplicate task thread IDs are prohibited")

    session_labels = [lbl for lbl, _ in sessions]
    if len(session_labels) != len(set(session_labels)):
        raise UsageObservationError("duplicate session labels are prohibited")

    if not skip_schema_preflight:
        actual_bin = app_server_cmd[0] if (app_server_cmd and app_server_cmd[0] != sys.executable) else codex_bin
        verified_digest = preflight_codex_schema(codex_bin=actual_bin)
    else:
        verified_digest = EXPERIMENTAL_APP_SERVER_SCHEMA_SHA256

    app_server_res = query_app_server(tasks, query_account_usage, app_server_cmd)

    session_results: dict[str, Any] = {}
    for label, file_path in sessions:
        session_results[label] = parse_session_file(file_path)

    available_tasks = [t for t in app_server_res["tasks"].values() if t.get("status") == "available"]
    available_task_count = len(available_tasks)

    total_in = _sum_nullable([t.get("input_tokens") for t in available_tasks])
    total_cached = _sum_nullable([t.get("cached_input_tokens") for t in available_tasks])
    total_net_new = _sum_nullable([t.get("net_new_input_tokens") for t in available_tasks])
    total_cw = _sum_nullable([t.get("cache_write_input_tokens") for t in available_tasks])
    total_out = _sum_nullable([t.get("output_tokens") for t in available_tasks])
    total_res = _sum_nullable([t.get("reasoning_output_tokens") for t in available_tasks])

    aggregates = {
        "tasks_requested": len(tasks),
        "tasks_available": available_task_count,
        "total_input_tokens": total_in,
        "total_cached_input_tokens": total_cached,
        "total_net_new_input_tokens": total_net_new,
        "total_cache_write_input_tokens": total_cw,
        "total_output_tokens": total_out,
        "total_reasoning_output_tokens": total_res,
        "reasoning_is_subset_of_output": True,
    }

    report: dict[str, Any] = {
        "schema_digest": verified_digest,
        "codex_version": PINNED_CODEX_VERSION,
        "tasks": app_server_res["tasks"],
        "aggregates": aggregates,
        "limitations": {
            "money_inferred": False,
            "quota_inferred": False,
            "directional_only": True,
            "billing_claim": False,
        },
    }

    if sessions:
        report["sessions"] = session_results
    if query_account_usage and app_server_res.get("account_usage"):
        report["account_usage"] = app_server_res["account_usage"]

    return report


def _fmt_tok(val: Optional[int]) -> str:
    return f"{val:,}" if val is not None else "unavailable"


def format_text_report(report: dict[str, Any]) -> str:
    lines: list[str] = [
        "=== Codex Usage Observation Report ===",
        f"Codex Version: {report['codex_version']}",
        f"Schema Digest: {report['schema_digest'][:16]}...",
        "",
        "--- Tasks (Thread Usage) ---",
    ]

    for label, data in report["tasks"].items():
        if data.get("status") == "available":
            lines.extend([
                f"Task [{label}]:",
                f"  Input Tokens:      {_fmt_tok(data.get('input_tokens'))}",
                f"  Cached Input:      {_fmt_tok(data.get('cached_input_tokens'))}",
                f"  Net-New Input:     {_fmt_tok(data.get('net_new_input_tokens'))}",
                f"  Cache Write Input: {_fmt_tok(data.get('cache_write_input_tokens'))}",
                f"  Output Tokens:     {_fmt_tok(data.get('output_tokens'))}",
                f"  Reasoning Output:  {_fmt_tok(data.get('reasoning_output_tokens'))} (subset of output)",
            ])
            if data.get("estimated_credits_micros") is not None:
                lines.append(f"  Estimated Credits: {data['estimated_credits_micros']:,} micros")
        else:
            lines.append(f"Task [{label}]: unavailable")

    agg = report["aggregates"]
    lines.extend([
        "",
        "--- Aggregates ---",
        f"Tasks Available:         {agg['tasks_available']} / {agg['tasks_requested']}",
        f"Total Input Tokens:      {_fmt_tok(agg['total_input_tokens'])}",
        f"Total Cached Input:      {_fmt_tok(agg['total_cached_input_tokens'])}",
        f"Total Net-New Input:     {_fmt_tok(agg['total_net_new_input_tokens'])}",
        f"Total Cache Write Input: {_fmt_tok(agg['total_cache_write_input_tokens'])}",
        f"Total Output Tokens:     {_fmt_tok(agg['total_output_tokens'])}",
        f"Total Reasoning Output:  {_fmt_tok(agg['total_reasoning_output_tokens'])} (subset, not double-counted)",
    ])

    if "sessions" in report:
        lines.extend(["", "--- Session Structural Activity ---"])
        for label, s_data in report["sessions"].items():
            lines.append(f"Session [{label}]:")
            lines.append(f"  CLI Version: {s_data['cli_version']}")
            lines.append(f"  Wait Count:  {s_data['wait_count']}")
            tools_str = ", ".join(f"{k}={v}" for k, v in sorted(s_data["tool_calls"].items()))
            lines.append(f"  Tool Calls:  {tools_str or 'none'}")
            tc = s_data["token_count"]
            lines.append(
                f"  Total Tokens: in={tc['input_tokens']:,}, cached={tc['cached_input_tokens']:,}, out={tc['output_tokens']:,}, res={tc['reasoning_output_tokens']:,}"
            )
            phase = s_data.get("last_phase_token_count")
            if phase is not None:
                lines.append(
                    f"  Latest Phase: in={phase['input_tokens']:,}, cached={phase['cached_input_tokens']:,}, out={phase['output_tokens']:,}, res={phase['reasoning_output_tokens']:,}"
                )
            window = s_data["measurement_window"]
            lines.append(
                f"  Window: explicit records={window['records_observed']}, token snapshots={window['token_snapshots_observed']}, duration_ms={_fmt_tok(window['duration_ms'])}"
            )

    if "account_usage" in report and report["account_usage"] is not None:
        au = report["account_usage"]
        lines.extend(["", "--- Account Rate Limits ---"])
        if "rate_limits" in au and au["rate_limits"]:
            rl = au["rate_limits"]
            p = rl["primary"]
            lines.append(f"Rate Limits:")
            if p is None:
                lines.append("  Primary:   unavailable")
            else:
                reset_str = f", resets at {p['resets_at']}" if p.get('resets_at') is not None else ""
                duration_str = _fmt_tok(p.get("window_duration_mins"))
                lines.append(f"  Primary:   {p['used_percent']:.1f}% used ({duration_str}m window{reset_str})")
            if rl.get("secondary"):
                s = rl["secondary"]
                s_reset_str = f", resets at {s['resets_at']}" if s.get('resets_at') is not None else ""
                s_duration_str = _fmt_tok(s.get("window_duration_mins"))
                lines.append(f"  Secondary: {s['used_percent']:.1f}% used ({s_duration_str}m window{s_reset_str})")

    lines.extend([
        "",
        "Limitations: Token comparisons are directional only. No money, price, or quota inferred.",
    ])
    return "\n".join(lines) + "\n"


def main(argv: Optional[Sequence[str]] = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(
        prog="codex-usage-report.sh",
        description="Privacy-safe, version-pinned Codex CLI 0.150.1 usage observation tool.",
    )
    parser.add_argument(
        "--task",
        action="append",
        metavar="LABEL=THREAD_ID",
        help="Map a task label to its Codex thread ID (can be specified multiple times).",
    )
    parser.add_argument(
        "--session",
        action="append",
        metavar="LABEL=ABS_FILE",
        help="Map a session label to an owner-private regular session file (can be specified multiple times).",
    )
    parser.add_argument(
        "--account-usage",
        action="store_true",
        help="Query account-level rate limits from app-server; per-thread credit estimates remain task-bound.",
    )
    parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="text",
        help="Output format (default: text).",
    )
    parser.add_argument(
        "--codex-bin",
        default="codex",
        help="Codex executable path (default: codex).",
    )

    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return 64 if exc.code != 0 else 0

    if not args.task:
        sys.stderr.write("error: at least one --task LABEL=THREAD_ID is required\n")
        return 64

    parsed_tasks: list[tuple[str, str]] = []
    for item in args.task:
        if "=" not in item:
            sys.stderr.write("error: invalid --task format (expected LABEL=THREAD_ID)\n")
            return 64
        lbl, thread_id = item.split("=", 1)
        if not LABEL_RE.match(lbl):
            sys.stderr.write("error: invalid task label format\n")
            return 64
        if not THREAD_ID_RE.match(thread_id):
            sys.stderr.write("error: invalid thread ID format\n")
            return 64
        parsed_tasks.append((lbl, thread_id))

    parsed_sessions: list[tuple[str, str]] = []
    if args.session:
        for item in args.session:
            if "=" not in item:
                sys.stderr.write("error: invalid --session format (expected LABEL=ABS_FILE)\n")
                return 64
            lbl, abs_file = item.split("=", 1)
            if not LABEL_RE.match(lbl):
                sys.stderr.write("error: invalid session label format\n")
                return 64
            parsed_sessions.append((lbl, abs_file))

    try:
        report = build_usage_report(
            tasks=parsed_tasks,
            sessions=parsed_sessions,
            query_account_usage=args.account_usage,
            codex_bin=args.codex_bin,
        )
    except UsageObservationError as exc:
        sys.stderr.write(f"usage observation error: {exc}\n")
        return 1
    except Exception:
        sys.stderr.write("unexpected error\n")
        return 1

    if args.format == "json":
        sys.stdout.buffer.write(_canonical(report))
    else:
        sys.stdout.write(format_text_report(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
