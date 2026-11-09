"""Run a process-scoped macOS Accessibility plan with a hard worker deadline."""
from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import sys
import tempfile
import time
import uuid
from datetime import datetime
from pathlib import Path

from macos_worker import AXError, FIELDS, WorkerOptions, _validate_plan, validate_options
from uia_journal import create_journal, merge_worker_result, recover_progress


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pid", type=int, required=True, help="Target application process ID")
    parser.add_argument("--executable", type=Path, required=True, help="Real executable file inside the app")
    parser.add_argument("--window", help="Exact window title; required when multiple windows match")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--inspect", action="store_true", help="List scoped raw AX attributes, excluding values")
    mode.add_argument("--probe", action="store_true", help="List windows belonging only to the verified PID")
    mode.add_argument("--steps", type=Path, help="UTF-8 JSON plan containing a steps array")
    parser.add_argument("--wait-seconds", type=float, default=5, help="Polling budget, 0.05 to 60 seconds")
    parser.add_argument("--timeout", type=float, default=30, help="Finite positive hard worker deadline")
    parser.add_argument("--max-nodes", type=int, default=400, help="Traversal budget, 1 to 10000 nodes")
    parser.add_argument("--inspect-depth", type=int, default=0, help="0 for all levels; 1 for root and children")
    parser.add_argument("--report", type=Path, help="Atomic JSON report destination")
    parser.add_argument("--journal", type=Path, help="New JSONL evidence path; existing files are preserved")
    return parser


def options_from_args(args, parser):
    options = WorkerOptions(args.pid, str(args.executable.resolve()), args.window,
                            args.wait_seconds, args.max_nodes, args.inspect_depth)
    try:
        validate_options(options)
        if not math.isfinite(args.timeout) or args.timeout <= 0:
            raise AXError("invalid_options", "timeout must be finite and positive")
    except AXError as error:
        parser.error(str(error))
    if args.report and args.journal and args.report.resolve() == args.journal.resolve():
        parser.error("report and journal must be different files")
    return options


def _worker_command(args, journal, run_id):
    command = [sys.executable, str(Path(__file__).with_name("macos_worker.py")),
               "--pid", str(args.pid), "--executable", str(args.executable.resolve()),
               "--wait-seconds", str(args.wait_seconds), "--max-nodes", str(args.max_nodes),
               "--inspect-depth", str(args.inspect_depth), "--journal", str(journal), "--run-id", run_id]
    if args.window is not None:
        command += ["--window", args.window]
    command += ["--probe"] if args.probe else ["--inspect"] if args.inspect else ["--steps", str(args.steps.resolve()), "--plan-stdin"]
    return command


def _reject_constant(value):
    raise ValueError("Non-finite JSON number")


def _timestamp(value):
    if type(value) is not str:
        return False
    try:
        return datetime.fromisoformat(value).utcoffset() is not None
    except ValueError:
        return False


def _nonnegative_number(value):
    return ((type(value) is int and value >= 0)
            or (type(value) is float and math.isfinite(value) and value >= 0))


def _valid_element(element, pid):
    return (type(element) is dict and set(element) == set(FIELDS) | {"actions", "pid"}
            and all(value is None or type(value) is str for key, value in element.items() if key in FIELDS)
            and type(element["pid"]) is int and element["pid"] == pid
            and type(element["actions"]) is list
            and all(type(action) is str and action for action in element["actions"]))


def _valid_step(record, expected, index):
    keys = {"index", "action", "selector", "elapsed_ms"}
    if expected["within"]:
        keys.add("within")
    if "window" in expected:
        keys.add("window")
    if expected["action"] == "wait":
        keys.update(("property", "observed", "observed_at"))
    if (type(record) is not dict or set(record) != keys
            or type(record["index"]) is not int or record["index"] != index
            or record["action"] != expected["action"] or record["selector"] != expected["selector"]
            or record.get("within", []) != expected["within"]
            or record.get("window") != expected.get("window")
            or not _nonnegative_number(record["elapsed_ms"])):
        return False
    return expected["action"] != "wait" or (
        record["property"] == expected["property"] and type(record["observed"]) is type(expected["equals"])
        and record["observed"] == expected["equals"] and _timestamp(record["observed_at"]))


def _validate_result(result, args, expected_steps, code):
    if (type(result) is not dict or type(result.get("ok")) is not bool
            or type(result.get("status")) is not str or type(result.get("steps")) is not list):
        raise ValueError("Invalid worker result fields")
    # json.loads also accepts escaped surrogate strings and overflowing exponents.
    json.dumps(result, ensure_ascii=False, allow_nan=False).encode("utf-8")
    records = result["steps"]
    if (len(records) > len(expected_steps)
            or any(not _valid_step(record, expected_steps[index], index) for index, record in enumerate(records))):
        raise ValueError("Worker steps do not match the submitted plan")
    if result["ok"]:
        if code != 0 or result["status"] != "ok" or len(records) != len(expected_steps):
            raise ValueError("Worker did not complete the submitted plan")
        if args.inspect or args.probe:
            key, other = ("elements", "windows") if args.inspect else ("windows", "elements")
            if (other in result or type(result.get(key)) is not list or len(result[key]) > args.max_nodes
                    or any(not _valid_element(element, args.pid) for element in result[key])
                    or (args.inspect and type(result.get("truncated")) is not bool)):
                raise ValueError("Invalid metadata for requested read-only mode")
        elif "elements" in result or "windows" in result:
            raise ValueError("Unexpected read-only metadata for action mode")


def _completed_journal(journal, run_id, args, expected_steps):
    """Additional Mac completion proof; original progress recovery stays intact."""
    try:
        events = [json.loads(line, parse_constant=_reject_constant) for line in journal.read_bytes().splitlines()]
    except (OSError, ValueError):
        return False
    if len(events) < 2:
        return False
    kinds = {"run_started", "step_started", "action_started", "step_completed", "run_finished"}
    for index, event in enumerate(events):
        if (type(event) is not dict or type(event.get("schema_version")) is not int
                or event["schema_version"] != 1 or event.get("run_id") != run_id
                or type(event.get("event")) is not str or event["event"] not in kinds
                or not _timestamp(event.get("time"))):
            return False
        if ((event["event"] == "run_started") != (index == 0)
                or (event["event"] == "run_finished") != (index == len(events) - 1)):
            return False
    first, last = events[0], events[-1]
    cursor = 1
    for index, step in enumerate(expected_steps):
        sequence = ("step_started", "step_completed") if step["action"] == "wait" else (
            "step_started", "action_started", "step_completed")
        for kind in sequence:
            if cursor >= len(events) - 1:
                return False
            event = events[cursor]
            cursor += 1
            if event["event"] != kind or type(event.get("index")) is not int or event["index"] != index:
                return False
            if kind == "step_completed":
                if not _valid_step(event.get("record"), step, index):
                    return False
            elif event.get("action") != step["action"]:
                return False
    return (type(first.get("target_pid")) is int and first["target_pid"] == args.pid
            and first.get("executable") == str(args.executable.resolve()) and last.get("ok") is True
            and cursor == len(events) - 1)


def _mutation_evidence(report):
    """Keep possible effects even when a malformed journal cannot prove success."""
    if type(report) is not dict:
        return False, set()
    possible = report.get("may_have_side_effects") is True
    records = list(report["steps"]) if type(report.get("steps")) is list else []
    pending = report.get("incomplete_step")
    if type(pending) is dict and (pending.get("phase") == "acting" or pending.get("outcome") == "unknown"):
        records.append(pending)
    mutations = set()
    for record in records:
        if type(record) is dict and record.get("action") in ("set", "invoke"):
            possible = True
            if type(record.get("index")) is int and record["index"] >= 0:
                mutations.add((record["index"], record["action"]))
    return possible, mutations


def _finish(result, args, run_id, started, code):
    result.update(run_id=run_id, target_pid=args.pid, wall_ms=round((time.perf_counter() - started) * 1000, 2))
    if result.get("ok") is not True and code == 0:
        code = 1
    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.report:
        temporary = args.report.with_name(args.report.name + "." + run_id + ".tmp")
        temporary_created = False
        try:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            with temporary.open("x", encoding="utf-8", newline="\n") as stream:
                temporary_created = True
                stream.write(output + "\n")
                stream.flush()
                os.fsync(stream.fileno())
            temporary.replace(args.report)
        except OSError as error:
            result.update(ok=False, status="report_error", error=str(error))
            output = json.dumps(result, ensure_ascii=False, indent=2)
            code = 1
        finally:
            if temporary_created and temporary.exists():
                temporary.unlink()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(output)
    return code


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    options_from_args(args, parser)
    started, run_id = time.perf_counter(), uuid.uuid4().hex
    expected_steps, plan_text = [], None
    if args.steps:
        try:
            plan = json.loads(args.steps.read_text(encoding="utf-8-sig"), parse_constant=_reject_constant)
            expected_steps = _validate_plan(plan)
            # Feed the exact validated document to the worker, not a later file read.
            plan_text = json.dumps(plan, ensure_ascii=False, allow_nan=False)
        except (AXError, OSError, ValueError) as error:
            return _finish({"ok": False, "status": "invalid_plan", "error": str(error), "steps": []},
                           args, run_id, started, 2)
    directory = args.report.resolve().parent if args.report else Path(tempfile.gettempdir()) / "software-testing-router"
    journal = (args.journal or directory / ("macos-" + run_id + ".jsonl")).resolve()
    try:
        create_journal(journal, run_id, args.pid, str(args.executable.resolve()))
    except OSError as error:
        return _finish({"ok": False, "status": "journal_error", "error": str(error)}, args, run_id, started, 2)
    code = 1
    received_effects, received_mutations = False, set()
    try:
        completed = subprocess.run(_worker_command(args, journal, run_id), capture_output=True,
                                   input=plan_text, text=True, encoding="utf-8", errors="replace", timeout=args.timeout,
                                   creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
        code = completed.returncode
        try:
            result = json.loads(completed.stdout, parse_constant=_reject_constant)
            received_effects, received_mutations = _mutation_evidence(result)
            _validate_result(result, args, expected_steps, code)
        except ValueError:
            result = {"ok": False, "status": "worker_error",
                      "error": (completed.stderr or completed.stdout or "No valid JSON from worker")[:3000]}
            code = code or 1
    except subprocess.TimeoutExpired:
        # run() kills and reaps only the worker it created, never the application PID.
        result = {"ok": False, "status": "timeout", "error": "Hard deadline exceeded; automation worker stopped"}
        code = 124
    except OSError as error:
        result = {"ok": False, "status": "worker_error", "error": str(error)}
    progress = recover_progress(journal, run_id)
    progress_effects, _ = _mutation_evidence(progress)
    result = merge_worker_result(result, progress)
    result["may_have_side_effects"] = received_effects or progress_effects
    pending = result.get("incomplete_step")
    if pending and (pending["index"], pending["action"]) in received_mutations:
        result["incomplete_step"] = {**pending, "phase": "acting", "outcome": "unknown"}
    if result.get("ok") is True and not _completed_journal(journal, run_id, args, expected_steps):
        result.update(ok=False, status="journal_error", journal_incomplete=True,
                      error="Durable journal does not prove complete ordered execution for this run")
    result["journal_path"] = str(journal)
    return _finish(result, args, run_id, started, code)


if __name__ == "__main__":
    raise SystemExit(main())
