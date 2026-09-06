#!/usr/bin/env python3
"""Validate the doctor's portable compatibility records without writing files."""

from __future__ import annotations

import re
import os
import signal
import selectors
import subprocess
import sys
import time
from datetime import date
from pathlib import Path


VERSION_RE = re.compile(r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)")
REVISION_RE = re.compile(r"[0-9a-f]{40}")
REVIEW_DAYS = 30
MAX_VERSION_OUTPUT_BYTES = 128
CAPTURE_TIMEOUT_SECONDS = 5


class MetadataError(ValueError):
    """A portable compatibility record is absent or malformed."""


def read_record(path: Path) -> str:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise MetadataError("record unavailable") from exc
    if not raw.endswith(b"\n") or raw.count(b"\n") != 1:
        raise MetadataError("record must contain one line")
    try:
        value = raw[:-1].decode("ascii")
    except UnicodeDecodeError as exc:
        raise MetadataError("record must be ASCII") from exc
    if not value or value.strip() != value:
        raise MetadataError("record is empty or padded")
    return value


def version(path: Path) -> int:
    value = read_record(path)
    if VERSION_RE.fullmatch(value) is None:
        raise MetadataError("invalid version")
    print(value)
    return 0


def revision(path: Path) -> int:
    value = read_record(path)
    if REVISION_RE.fullmatch(value) is None:
        raise MetadataError("invalid revision")
    print(value)
    return 0


def agy_version_output(path: Path) -> int:
    try:
        with path.open("rb") as handle:
            raw = handle.read(MAX_VERSION_OUTPUT_BYTES + 1)
    except OSError as exc:
        raise MetadataError("version output unavailable") from exc
    if not raw or len(raw) > MAX_VERSION_OUTPUT_BYTES:
        raise MetadataError("invalid version output size")
    if raw.endswith(b"\n"):
        raw = raw[:-1]
    if not raw or b"\n" in raw or b"\r" in raw:
        raise MetadataError("invalid version output lines")
    try:
        value = raw.decode("ascii")
    except UnicodeDecodeError as exc:
        raise MetadataError("version output must be ASCII") from exc
    if value.startswith("agy "):
        value = value[4:]
    if VERSION_RE.fullmatch(value) is None:
        raise MetadataError("invalid version output")
    print(value)
    return 0


class CaptureInterrupted(Exception):
    """The doctor supervisor was interrupted while agy was active."""

    def __init__(self, signum: int):
        super().__init__(signum)
        self.signum = signum


def terminate_group(process: subprocess.Popen[bytes], signum: int) -> None:
    if process.poll() is not None:
        return
    try:
        os.killpg(process.pid, signum)
    except ProcessLookupError:
        return
    try:
        process.wait(timeout=1)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait()


def parse_agy_version_bytes(raw: bytes) -> str:
    if not raw or len(raw) > MAX_VERSION_OUTPUT_BYTES:
        raise MetadataError("invalid version output size")
    if raw.endswith(b"\n"):
        raw = raw[:-1]
    if not raw or b"\n" in raw or b"\r" in raw:
        raise MetadataError("invalid version output lines")
    try:
        value = raw.decode("ascii")
    except UnicodeDecodeError as exc:
        raise MetadataError("version output must be ASCII") from exc
    if value.startswith("agy "):
        value = value[4:]
    if VERSION_RE.fullmatch(value) is None:
        raise MetadataError("invalid version output")
    return value


def capture_agy_version() -> int:
    forwarded = (signal.SIGHUP, signal.SIGINT, signal.SIGTERM)
    process: subprocess.Popen[bytes] | None = None

    def handle_signal(signum: int, _frame: object) -> None:
        if process is not None:
            terminate_group(process, signum)
        raise CaptureInterrupted(signum)

    previous_handlers = {signum: signal.getsignal(signum) for signum in forwarded}
    for signum in forwarded:
        signal.signal(signum, handle_signal)
    if hasattr(signal, "pthread_sigmask"):
        signal.pthread_sigmask(signal.SIG_BLOCK, forwarded)
    try:
        process = subprocess.Popen(
            ["agy", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        if hasattr(signal, "pthread_sigmask"):
            signal.pthread_sigmask(signal.SIG_UNBLOCK, forwarded)
        assert process.stdout is not None
        deadline = time.monotonic() + CAPTURE_TIMEOUT_SECONDS
        chunks: list[bytes] = []
        total = 0
        with selectors.DefaultSelector() as selector:
            selector.register(process.stdout, selectors.EVENT_READ)
            while total <= MAX_VERSION_OUTPUT_BYTES:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    terminate_group(process, signal.SIGTERM)
                    raise MetadataError("version command timed out")
                if not selector.select(remaining):
                    terminate_group(process, signal.SIGTERM)
                    raise MetadataError("version command timed out")
                chunk = os.read(
                    process.stdout.fileno(),
                    MAX_VERSION_OUTPUT_BYTES + 1 - total,
                )
                if not chunk:
                    break
                chunks.append(chunk)
                total += len(chunk)
        raw = b"".join(chunks)
        if len(raw) > MAX_VERSION_OUTPUT_BYTES:
            terminate_group(process, signal.SIGTERM)
            raise MetadataError("invalid version output size")
        try:
            returncode = process.wait(timeout=max(0, deadline - time.monotonic()))
        except subprocess.TimeoutExpired as exc:
            terminate_group(process, signal.SIGTERM)
            raise MetadataError("version command timed out") from exc
        if returncode != 0:
            raise MetadataError("version command failed")
        print(parse_agy_version_bytes(raw))
        return 0
    except CaptureInterrupted as exc:
        return 128 + exc.signum
    except (MetadataError, OSError, subprocess.SubprocessError):
        if process is not None:
            terminate_group(process, signal.SIGTERM)
        return 2
    finally:
        if hasattr(signal, "pthread_sigmask"):
            signal.pthread_sigmask(signal.SIG_UNBLOCK, forwarded)
        for signum, handler in previous_handlers.items():
            signal.signal(signum, handler)


def review(path: Path) -> int:
    value = read_record(path)
    today = date.today()
    try:
        reviewed = date.fromisoformat(value)
    except ValueError as exc:
        raise MetadataError("invalid date") from exc
    if reviewed.isoformat() != value or reviewed > today:
        raise MetadataError("invalid date")
    if (today - reviewed).days >= REVIEW_DAYS:
        print("due")
        return 3
    print("fresh")
    return 0


def main(argv: list[str]) -> int:
    if len(argv) == 2 and argv[1] == "capture-agy-version":
        return capture_agy_version()
    if len(argv) != 3 or argv[1] not in {
        "version",
        "revision",
        "review",
        "agy-version-output",
    }:
        return 2
    try:
        if argv[1] == "version":
            return version(Path(argv[2]))
        if argv[1] == "revision":
            return revision(Path(argv[2]))
        if argv[1] == "agy-version-output":
            return agy_version_output(Path(argv[2]))
        return review(Path(argv[2]))
    except MetadataError:
        print("doctor metadata: invalid record", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
