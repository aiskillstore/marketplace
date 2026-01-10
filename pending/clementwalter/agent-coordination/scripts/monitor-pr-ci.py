#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
PR CI Monitor - Efficiently track CI status for a pull request.

Usage:
    monitor-pr-ci.py <pr> [--repo OWNER/REPO] [--wait] [--timeout SECONDS] [--quiet]

Examples:
    monitor-pr-ci.py 123                          # Check PR #123 in current repo
    monitor-pr-ci.py 123 --wait                   # Wait for CI to complete
    monitor-pr-ci.py 123 --wait --timeout 600    # Wait up to 10 minutes
    monitor-pr-ci.py https://github.com/org/repo/pull/123 --wait

Output is minimal unless CI fails - then shows error details.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from enum import Enum


class Status(Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILURE = "failure"
    CANCELLED = "cancelled"
    UNKNOWN = "unknown"


@dataclass
class CheckRun:
    name: str
    status: str  # queued, in_progress, completed
    conclusion: str | None  # success, failure, cancelled, skipped, etc.
    url: str

    @property
    def state(self) -> Status:
        if self.status != "completed":
            return Status.PENDING
        if self.conclusion == "success" or self.conclusion == "skipped":
            return Status.SUCCESS
        if self.conclusion == "failure":
            return Status.FAILURE
        if self.conclusion == "cancelled":
            return Status.CANCELLED
        return Status.UNKNOWN


def run_gh(args: list[str]) -> tuple[int, str, str]:
    """Run a gh CLI command."""
    try:
        result = subprocess.run(
            ["gh"] + args,
            capture_output=True,
            text=True,
            timeout=30,
        )
        return result.returncode, result.stdout, result.stderr
    except FileNotFoundError:
        return 1, "", "gh CLI not found. Install from https://cli.github.com/"
    except subprocess.TimeoutExpired:
        return 1, "", "Command timed out"


def parse_pr_arg(pr_arg: str) -> tuple[str | None, int]:
    """Parse PR argument - can be number or full URL."""
    # Full URL: https://github.com/owner/repo/pull/123
    url_match = re.match(r"https://github\.com/([^/]+/[^/]+)/pull/(\d+)", pr_arg)
    if url_match:
        return url_match.group(1), int(url_match.group(2))

    # Just a number
    if pr_arg.isdigit():
        return None, int(pr_arg)

    raise ValueError(f"Invalid PR argument: {pr_arg}. Use PR number or full URL.")


def get_check_runs(repo: str | None, pr_number: int) -> list[CheckRun]:
    """Get all check runs for a PR using gh pr checks."""
    repo_arg = ["-R", repo] if repo else []

    # Use gh pr checks - most reliable method
    code, stdout, stderr = run_gh(
        ["pr", "checks", str(pr_number), "--json", "name,state,link,workflow"]
        + repo_arg
    )
    if code != 0:
        # Check if it's just "no checks" which is not an error
        if "no checks" in stderr.lower():
            return []
        print(f"Error getting checks: {stderr}", file=sys.stderr)
        sys.exit(1)

    checks_data = json.loads(stdout) if stdout.strip() else []

    # Map gh state values to our status/conclusion model
    # gh states: SUCCESS, FAILURE, PENDING, SKIPPED, CANCELLED, etc.
    def parse_state(state: str) -> tuple[str, str | None]:
        state = state.upper()
        if state == "PENDING":
            return "in_progress", None
        elif state == "SUCCESS":
            return "completed", "success"
        elif state == "FAILURE":
            return "completed", "failure"
        elif state == "SKIPPED":
            return "completed", "skipped"
        elif state == "CANCELLED":
            return "completed", "cancelled"
        else:
            return "completed", state.lower()

    return [
        CheckRun(
            name=c.get("name", "unknown"),
            status=parse_state(c.get("state", ""))[0],
            conclusion=parse_state(c.get("state", ""))[1],
            url=c.get("link", ""),
        )
        for c in checks_data
    ]


def get_failed_job_logs(repo: str | None, check: CheckRun) -> str | None:
    """Get logs for a failed check run - just the error portion."""
    # Extract run ID from URL if possible
    # URL format: https://github.com/owner/repo/actions/runs/12345/job/67890
    run_match = re.search(r"/actions/runs/(\d+)", check.url)
    if not run_match:
        return None

    run_id = run_match.group(1)

    # Get failed job logs - gh run view shows summary with errors
    code, stdout, stderr = run_gh(
        ["run", "view", run_id, "--log-failed"] + (["-R", repo] if repo else [])
    )

    if code != 0 or not stdout.strip():
        # Try getting just the run summary
        code, stdout, stderr = run_gh(
            ["run", "view", run_id, "--json", "conclusion,jobs"]
            + (["-R", repo] if repo else [])
        )
        if code == 0:
            data = json.loads(stdout)
            failed_jobs = [
                j for j in data.get("jobs", []) if j.get("conclusion") == "failure"
            ]
            if failed_jobs:
                return f"Failed jobs: {', '.join(j.get('name', 'unknown') for j in failed_jobs)}"
        return None

    # Truncate logs if too long - keep last 100 lines (usually has the error)
    lines = stdout.strip().split("\n")
    if len(lines) > 100:
        return f"[... truncated {len(lines) - 100} lines ...]\n" + "\n".join(
            lines[-100:]
        )
    return stdout.strip()


def aggregate_status(checks: list[CheckRun]) -> Status:
    """Get overall CI status from all checks."""
    if not checks:
        return Status.UNKNOWN

    states = [c.state for c in checks]

    if Status.FAILURE in states:
        return Status.FAILURE
    if Status.CANCELLED in states:
        return Status.CANCELLED
    if Status.PENDING in states:
        return Status.PENDING
    if all(s == Status.SUCCESS for s in states):
        return Status.SUCCESS
    return Status.UNKNOWN


def print_status(checks: list[CheckRun], repo: str | None, verbose: bool = False):
    """Print CI status - minimal unless there are failures."""
    status = aggregate_status(checks)

    # Status emoji
    status_icons = {
        Status.PENDING: "⏳",
        Status.SUCCESS: "✅",
        Status.FAILURE: "❌",
        Status.CANCELLED: "🚫",
        Status.UNKNOWN: "❓",
    }

    # Count by status
    pending = sum(1 for c in checks if c.state == Status.PENDING)
    success = sum(1 for c in checks if c.state == Status.SUCCESS)
    failed = sum(1 for c in checks if c.state == Status.FAILURE)

    # One-line summary
    icon = status_icons.get(status, "❓")
    summary_parts = []
    if success:
        summary_parts.append(f"{success} passed")
    if pending:
        summary_parts.append(f"{pending} pending")
    if failed:
        summary_parts.append(f"{failed} failed")

    print(f"{icon} CI Status: {', '.join(summary_parts) or 'no checks'}")

    # If failed, show which checks failed and get logs
    if status == Status.FAILURE:
        print("\nFailed checks:")
        for check in checks:
            if check.state == Status.FAILURE:
                print(f"  ❌ {check.name}")
                if check.url:
                    print(f"     {check.url}")

                # Get error logs
                logs = get_failed_job_logs(repo, check)
                if logs:
                    print(f"\n  Error output for {check.name}:")
                    print("  " + "-" * 60)
                    for line in logs.split("\n"):
                        print(f"  {line}")
                    print("  " + "-" * 60)

    elif verbose and status == Status.PENDING:
        print("\nPending checks:")
        for check in checks:
            if check.state == Status.PENDING:
                print(f"  ⏳ {check.name}")


def main():
    parser = argparse.ArgumentParser(
        description="Monitor CI status for a GitHub PR",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("pr", help="PR number or full GitHub PR URL")
    parser.add_argument(
        "-R", "--repo", help="Repository (owner/repo), defaults to current"
    )
    parser.add_argument(
        "-w", "--wait", action="store_true", help="Wait for CI to complete"
    )
    parser.add_argument(
        "-t",
        "--timeout",
        type=int,
        default=1800,
        help="Max wait time in seconds (default: 1800)",
    )
    parser.add_argument(
        "-i",
        "--interval",
        type=int,
        default=30,
        help="Poll interval in seconds (default: 30)",
    )
    parser.add_argument(
        "-q", "--quiet", action="store_true", help="Minimal output while waiting"
    )

    args = parser.parse_args()

    try:
        repo_from_url, pr_number = parse_pr_arg(args.pr)
        repo = args.repo or repo_from_url
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    start_time = time.time()
    last_status = None

    while True:
        checks = get_check_runs(repo, pr_number)
        status = aggregate_status(checks)

        if args.wait and status == Status.PENDING:
            elapsed = time.time() - start_time
            if elapsed >= args.timeout:
                print(f"⏰ Timeout after {args.timeout}s - CI still pending")
                print_status(checks, repo, verbose=True)
                sys.exit(2)

            # Only print if status changed or first iteration
            if not args.quiet or last_status != status:
                pending_count = sum(1 for c in checks if c.state == Status.PENDING)
                print(
                    f"⏳ Waiting... {pending_count} checks pending ({int(elapsed)}s elapsed)"
                )

            last_status = status
            time.sleep(args.interval)
            continue

        # Final status
        print_status(checks, repo)

        # Exit code based on status
        if status == Status.SUCCESS:
            sys.exit(0)
        elif status == Status.FAILURE:
            sys.exit(1)
        elif status == Status.PENDING:
            sys.exit(2)
        else:
            sys.exit(3)


if __name__ == "__main__":
    main()
