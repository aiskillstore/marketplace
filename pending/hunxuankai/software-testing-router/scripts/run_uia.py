"""Run one process-scoped UIA plan with a hard deadline. No third-party Python packages."""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path

from uia_journal import create_journal, merge_worker_result, recover_progress


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pid", type=int, required=True, help="Target application process ID")
    parser.add_argument("--executable", type=Path, required=True, help="Expected executable path")
    parser.add_argument("--window", help="Exact top-level window name; required if multiple windows match")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--inspect", action="store_true", help="List scoped elements and supported patterns")
    mode.add_argument("--probe", action="store_true", help="Read only: resolve a verified launcher's descendant window owners")
    mode.add_argument("--steps", type=Path, help="UTF-8 JSON object containing a steps array")
    parser.add_argument("--wait-seconds", type=float, default=5, help="Condition polling budget (0.05 to 60); native calls can finish later")
    parser.add_argument("--timeout", type=float, default=30, help="Hard deadline for the whole PowerShell worker")
    parser.add_argument("--max-nodes", type=int, default=400, help="Maximum elements returned by tree inspection (1 to 10000)")
    parser.add_argument("--inspect-depth", type=int, default=0, help="Inspection depth; 0 means all levels, 1 means root and direct children")
    parser.add_argument("--report", type=Path, help="Optional JSON report destination")
    parser.add_argument("--journal", type=Path, help="New JSONL journal path; existing evidence is never overwritten")
    args = parser.parse_args()
    if args.timeout <= 0 or not 0.05 <= args.wait_seconds <= 60 or not 1 <= args.max_nodes <= 10000 or not 0 <= args.inspect_depth <= 100:
        parser.error("timeout and max-nodes must be positive; wait-seconds must be between 0.05 and 60")
    started = time.perf_counter()
    powershell = shutil.which("pwsh")
    result = None
    code = 1
    run_id = uuid.uuid4().hex
    journal = args.journal
    if journal is None:
        directory = args.report.resolve().parent if args.report else Path(tempfile.gettempdir()) / "software-testing-router"
        journal = directory / ("uia-" + run_id + ".jsonl")
    journal = journal.resolve()
    if args.report and args.report.resolve() == journal:
        parser.error("report and journal must be different files")
    journal_created = False
    if os.name != "nt" or not powershell:
        result = {"ok": False, "status": "unavailable", "error": "Windows and PowerShell 7 (pwsh) are required"}
        code = 2
    else:
        try:
            create_journal(journal, run_id, args.pid, str(args.executable.resolve()))
            journal_created = True
        except OSError as exc:
            result = {"ok": False, "status": "journal_error", "error": str(exc)}
            code = 2
        command = [powershell, "-NoLogo", "-NoProfile", "-NonInteractive", "-File",
                   str(Path(__file__).with_name("uia.ps1")), "-TargetPid", str(args.pid),
                   "-Executable", str(args.executable.resolve()),
                   "-WaitSeconds", str(args.wait_seconds), "-MaxNodes", str(args.max_nodes),
                   "-InspectDepth", str(args.inspect_depth), "-JournalPath", str(journal), "-RunId", run_id]
        if args.window:
            command += ["-WindowName", args.window]
        command += ["-Probe"] if args.probe else ["-Inspect"] if args.inspect else ["-StepsFile", str(args.steps.resolve())]
        try:
            if not journal_created:
                raise RuntimeError("Journal could not be created; target was not touched")
            completed = subprocess.run(
                command, capture_output=True, text=True, encoding="utf-8", errors="replace",
                timeout=args.timeout, creationflags=subprocess.CREATE_NO_WINDOW,
            )
            code = completed.returncode
            try:
                result = json.loads(completed.stdout)
                if not isinstance(result, dict):
                    raise ValueError("Worker result is not a JSON object")
            except ValueError:
                result = {"ok": False, "status": "worker_error",
                          "error": (completed.stderr or completed.stdout or "No JSON from worker")[:3000]}
                code = code or 1
        except subprocess.TimeoutExpired:
            # subprocess.run kills and reaps its own PowerShell worker. It never kills the target app.
            result = {"ok": False, "status": "timeout", "error": "Hard deadline exceeded; automation worker stopped"}
            code = 124
        except OSError as exc:
            result = {"ok": False, "status": "worker_error", "error": str(exc)}
        except RuntimeError:
            pass  # Preserve journal_error; the worker was not launched.
    if journal_created:
        progress = recover_progress(journal, run_id)
        result = merge_worker_result(result, progress)
        result["journal_path"] = str(journal)
        if result.get("status") == "journal_error":
            code = 1
    result["run_id"] = run_id
    result["wall_ms"] = round((time.perf_counter() - started) * 1000, 2)
    result["target_pid"] = args.pid
    if result.get("ok") is not True and code == 0:
        code = 1
    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        temporary = args.report.with_name(args.report.name + "." + run_id + ".tmp")
        temporary.write_text(output + "\n", encoding="utf-8")
        temporary.replace(args.report)
    # Preserve Chinese control names even when the caller's console uses a legacy code page.
    sys.stdout.reconfigure(encoding="utf-8")
    print(output)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
