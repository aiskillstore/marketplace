#!/usr/bin/env python3
"""Render bounded, process-inert GitHub issue metadata for maintainer triage.

The stdin protocol deliberately excludes every free-text issue field.  This tool is
not a classifier, issue writer, or scheduler.  `fetch` is an explicit read-only
convenience command whose query requests metadata only and feeds the same strict
renderer.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import selectors
import signal
import shutil
import subprocess
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime
from typing import Any


SCHEMA = "agy-worker.feedback-triage.v1"
OWNER = "cagdasyurekli"
REPOSITORY = "codex-agy-worker"
REPO = f"{OWNER}/{REPOSITORY}"
ISSUE_URL = re.compile(
    rf"https://github\.com/{OWNER}/{REPOSITORY}/issues/([1-9][0-9]*)\Z"
)
TIMESTAMP = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z\Z")
DUPLICATE_KEY = re.compile(r"[0-9a-f]{64}\Z")
TYPES = ("bug", "compatibility", "feature", "other")
MAX_INPUT_BYTES = 65_536
MAX_ISSUES = 100
BURST_PER_UTC_DAY = 20
FETCH_TIMEOUT_SECONDS = 20.0
GROUP_TERM_GRACE_SECONDS = 0.25
READ_CHUNK_BYTES = 8192
OWNED_SIGNALS = (signal.SIGHUP, signal.SIGINT, signal.SIGTERM)
STATUS_BYTES = 32

# The fixed controller pins the new session/process-group identity until its parent
# closes the whole group.  It forwards only gh stdout, reports the direct gh exit on
# a private bounded descriptor, and never interprets GitHub-controlled bytes.
CONTROLLER_SOURCE = r"""
import os
import signal
import subprocess
import sys

status_fd = int(sys.argv[1])
child = subprocess.Popen(
    sys.argv[2:], stdin=subprocess.DEVNULL, stdout=sys.stdout.buffer,
    stderr=subprocess.DEVNULL, close_fds=True,
)
os.close(1)
returncode = child.wait()
os.write(status_fd, (str(returncode) + "\n").encode("ascii"))
os.close(status_fd)
while True:
    signal.pause()
"""

# This is intentionally static: callers cannot change the repository, host, fields,
# pagination, or query shape.  It asks GitHub for metadata only, including the
# one-bit truncation signal necessary to keep a one-page result honest.
FETCH_QUERY = """query($owner:String!, $name:String!, $first:Int!) {
  repository(owner:$owner, name:$name) {
    issues(first:$first, states:OPEN, orderBy:{field:UPDATED_AT, direction:DESC}) {
      nodes { number url createdAt updatedAt }
      pageInfo { hasNextPage }
    }
  }
}"""


class TriageError(ValueError):
    pass


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise TriageError("duplicate JSON object key")
        result[key] = value
    return result


def load_bounded_json(raw: bytes) -> Any:
    if len(raw) > MAX_INPUT_BYTES:
        raise TriageError("input exceeds byte limit")
    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=reject_duplicate_keys)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise TriageError("input is not valid JSON") from exc


def exact_keys(value: dict[str, Any], allowed: set[str], what: str) -> None:
    if set(value) != allowed:
        raise TriageError(f"{what} fields are invalid")


def valid_timestamp(value: Any) -> str:
    if not isinstance(value, str) or not TIMESTAMP.fullmatch(value):
        raise TriageError("timestamp is invalid")
    try:
        datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError as exc:
        raise TriageError("timestamp is invalid") from exc
    return value


def validate_input(value: Any) -> tuple[list[dict[str, Any]], bool]:
    if not isinstance(value, dict):
        raise TriageError("input root is invalid")
    exact_keys(value, {"issues", "overflow"}, "input root")
    issues = value["issues"]
    overflow = value["overflow"]
    if not isinstance(issues, list) or len(issues) > MAX_ISSUES or type(overflow) is not bool:
        raise TriageError("input bounds are invalid")
    result: list[dict[str, Any]] = []
    numbers: set[int] = set()
    for issue in issues:
        if not isinstance(issue, dict):
            raise TriageError("issue metadata is invalid")
        exact_keys(issue, {"number", "url", "type", "created_at", "updated_at", "duplicate_key"}, "issue")
        number = issue["number"]
        url = issue["url"]
        issue_type = issue["type"]
        duplicate_key = issue["duplicate_key"]
        if type(number) is not int or number < 1 or number in numbers:
            raise TriageError("issue number is invalid")
        if not isinstance(url, str) or (match := ISSUE_URL.fullmatch(url)) is None or int(match.group(1)) != number:
            raise TriageError("issue URL is invalid")
        if issue_type not in TYPES:
            raise TriageError("issue type is invalid")
        if duplicate_key is not None and (not isinstance(duplicate_key, str) or not DUPLICATE_KEY.fullmatch(duplicate_key)):
            raise TriageError("duplicate key is invalid")
        result.append({
            "number": number,
            "url": url,
            "type": issue_type,
            "created_at": valid_timestamp(issue["created_at"]),
            "updated_at": valid_timestamp(issue["updated_at"]),
            "duplicate_key": duplicate_key,
        })
        numbers.add(number)
    return result, overflow


def canonical_summary(value: Any) -> dict[str, Any]:
    issues, overflow = validate_input(value)
    created_months: Counter[str] = Counter()
    updated_months: Counter[str] = Counter()
    created_days: Counter[str] = Counter()
    types: Counter[str] = Counter()
    duplicates: defaultdict[str, list[int]] = defaultdict(list)
    ordered = sorted(issues, key=lambda issue: issue["number"])
    for issue in ordered:
        created_months[issue["created_at"][:7]] += 1
        updated_months[issue["updated_at"][:7]] += 1
        created_days[issue["created_at"][:10]] += 1
        types[issue["type"]] += 1
        if issue["duplicate_key"] is not None:
            duplicates[issue["duplicate_key"]].append(issue["number"])
    duplicate_groups = sorted(
        (numbers for numbers in duplicates.values() if len(numbers) > 1),
        key=lambda numbers: (numbers[0], numbers),
    )
    return {
        "schema": SCHEMA,
        "issue_count": len(ordered),
        "issue_numbers": [issue["number"] for issue in ordered],
        "issue_urls": [issue["url"] for issue in ordered],
        "type_counts": {issue_type: types[issue_type] for issue_type in TYPES},
        "created_month_counts": dict(sorted(created_months.items())),
        "updated_month_counts": dict(sorted(updated_months.items())),
        "duplicate_groups": duplicate_groups,
        "burst": any(count >= BURST_PER_UTC_DAY for count in created_days.values()),
        "overflow": overflow,
    }


def print_summary(value: Any) -> None:
    print(json.dumps(canonical_summary(value), sort_keys=True, separators=(",", ":")))


def summarize_command(_: argparse.Namespace) -> int:
    # One extra byte distinguishes an exact MAX_INPUT_BYTES stream from an overflow.
    raw = sys.stdin.buffer.read(MAX_INPUT_BYTES + 1)
    print_summary(load_bounded_json(raw))
    return 0


def project_github_response(value: Any) -> dict[str, Any]:
    """Drop all GitHub fields except the four explicit metadata fields."""
    try:
        issues = value["data"]["repository"]["issues"]
        nodes = issues["nodes"]
        overflow = issues["pageInfo"]["hasNextPage"]
    except (KeyError, TypeError) as exc:
        raise TriageError("GitHub response shape is invalid") from exc
    if not isinstance(nodes, list) or type(overflow) is not bool:
        raise TriageError("GitHub response shape is invalid")
    metadata = []
    for node in nodes:
        if not isinstance(node, dict):
            raise TriageError("GitHub response shape is invalid")
        # GitHub field names are mapped here rather than forwarding a node; title,
        # body, author, labels, comments, and any future fields cannot cross this seam.
        try:
            metadata.append({
                "number": node["number"], "url": node["url"], "type": "other",
                "created_at": node["createdAt"], "updated_at": node["updatedAt"],
                "duplicate_key": None,
            })
        except KeyError as exc:
            raise TriageError("GitHub response shape is invalid") from exc
    return {"issues": metadata, "overflow": overflow}


def close_process_group(process: subprocess.Popen[bytes]) -> None:
    """Close the exact child group, then reap the direct child once."""
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except (ProcessLookupError, PermissionError):
        pass
    time.sleep(GROUP_TERM_GRACE_SECONDS)
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        pass
    if process.stdout is not None:
        process.stdout.close()
    process.wait()


def bounded_fetch(command: list[str], environment: dict[str, str]) -> bytes:
    """Run one fixed gh read with bounded incremental stdout and group cleanup."""
    interrupted: list[int] = []
    originals: dict[int, Any] = {}

    def latch(signum: int, _frame: Any) -> None:
        if not interrupted:
            interrupted.append(signum)

    def restore_handlers() -> None:
        for signum, original in list(originals.items()):
            signal.signal(signum, original)
            del originals[signum]

    for signum in OWNED_SIGNALS:
        originals[signum] = signal.getsignal(signum)
        signal.signal(signum, latch)

    process: subprocess.Popen[bytes] | None = None
    selector = selectors.DefaultSelector()
    status_read = -1
    status_write = -1
    reaped = False
    try:
        status_read, status_write = os.pipe()
        process = subprocess.Popen(
            [sys.executable, "-I", "-S", "-B", "-c", CONTROLLER_SOURCE,
             str(status_write), *command],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            env=environment,
            start_new_session=True,
            close_fds=True,
            pass_fds=(status_write,),
        )
        os.close(status_write)
        status_write = -1
        if process.stdout is None:
            raise TriageError("GitHub metadata read failed")
        os.set_blocking(process.stdout.fileno(), False)
        os.set_blocking(status_read, False)
        selector.register(process.stdout, selectors.EVENT_READ, "stdout")
        selector.register(status_read, selectors.EVENT_READ, "status")
        deadline = time.monotonic() + FETCH_TIMEOUT_SECONDS
        output = bytearray()
        status = bytearray()
        output_eof = False
        status_eof = False
        while not (output_eof and status_eof):
            if interrupted:
                close_process_group(process)
                reaped = True
                raise TriageError("GitHub metadata read interrupted")
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                close_process_group(process)
                reaped = True
                raise TriageError("GitHub metadata read timed out")
            events = selector.select(min(0.1, remaining))
            for key, _mask in events:
                if key.data == "stdout":
                    allowance = MAX_INPUT_BYTES + 1 - len(output)
                    chunk = os.read(key.fileobj.fileno(), min(READ_CHUNK_BYTES, allowance))
                    if not chunk:
                        selector.unregister(key.fileobj)
                        output_eof = True
                        continue
                    output.extend(chunk)
                    if len(output) > MAX_INPUT_BYTES:
                        close_process_group(process)
                        reaped = True
                        raise TriageError("GitHub metadata read exceeds byte limit")
                else:
                    chunk = os.read(status_read, STATUS_BYTES + 1 - len(status))
                    if not chunk:
                        selector.unregister(status_read)
                        os.close(status_read)
                        status_read = -1
                        status_eof = True
                        continue
                    status.extend(chunk)
                    if len(status) > STATUS_BYTES:
                        close_process_group(process)
                        reaped = True
                        raise TriageError("GitHub metadata read failed")

        if re.fullmatch(rb"-?[0-9]+\n", status) is None:
            close_process_group(process)
            reaped = True
            raise TriageError("GitHub metadata read failed")
        returncode = int(status)
        close_process_group(process)
        reaped = True
        restore_handlers()
        if interrupted:
            raise TriageError("GitHub metadata read interrupted")
        if returncode != 0:
            raise TriageError("GitHub metadata read failed")
        return bytes(output)
    except OSError as exc:
        if process is not None and not reaped:
            close_process_group(process)
            reaped = True
        raise TriageError("GitHub metadata read failed") from exc
    finally:
        selector.close()
        if status_read >= 0:
            os.close(status_read)
        if status_write >= 0:
            os.close(status_write)
        restore_handlers()


def fetch_command(_: argparse.Namespace) -> int:
    gh = shutil.which("gh")
    if gh is None:
        raise TriageError("gh is not installed")
    environment = os.environ.copy()
    for name in (
        "GH_HOST", "GH_REPO", "GH_FORCE_TTY", "GITHUB_API_URL",
        "GITHUB_GRAPHQL_URL", "GITHUB_SERVER_URL", "GITHUB_REPOSITORY",
    ):
        environment.pop(name, None)
    environment["GH_PROMPT_DISABLED"] = "1"
    command = [
        gh, "api", "graphql", "--hostname", "github.com",
        "-f", f"query={FETCH_QUERY}", "-f", f"owner={OWNER}",
        "-f", f"name={REPOSITORY}", "-F", f"first={MAX_ISSUES}",
    ]
    raw = bounded_fetch(command, environment)
    print_summary(project_github_response(load_bounded_json(raw)))
    return 0


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="Render bounded safe feedback metadata")
    commands = root.add_subparsers(dest="command", required=True)
    summarize = commands.add_parser("summarize")
    summarize.set_defaults(handler=summarize_command)
    fetch = commands.add_parser("fetch")
    fetch.set_defaults(handler=fetch_command)
    return root


def main() -> int:
    try:
        arguments = parser().parse_args()
        return arguments.handler(arguments)
    except TriageError as exc:
        print(f"feedback-triage: {exc}", file=sys.stderr)
        return 65


if __name__ == "__main__":
    raise SystemExit(main())
