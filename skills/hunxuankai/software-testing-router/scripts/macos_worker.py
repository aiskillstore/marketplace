"""Process-scoped macOS Accessibility strategy. Native loading occurs only in main."""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from macos_ax import AXError, NativeAX


FIELDS = {"title": "AXTitle", "identifier": "AXIdentifier", "description": "AXDescription",
          "role": "AXRole", "subrole": "AXSubrole"}


@dataclass(frozen=True)
class WorkerOptions:
    target_pid: int
    executable: str
    window: str | None = None
    wait_seconds: float = 5
    max_nodes: int = 400
    inspect_depth: int = 0


def validate_options(options: WorkerOptions) -> None:
    if type(options.target_pid) is not int or not 1 <= options.target_pid <= 2147483647:
        raise AXError("invalid_options", "pid must be a positive 32-bit integer")
    if type(options.executable) is not str or not options.executable:
        raise AXError("invalid_options", "executable must be a nonempty path string")
    if options.window is not None and (type(options.window) is not str or not options.window):
        raise AXError("invalid_options", "window must be a nonempty string")
    if (type(options.wait_seconds) not in (int, float) or not math.isfinite(options.wait_seconds)
            or not 0.05 <= options.wait_seconds <= 60):
        raise AXError("invalid_options", "wait-seconds must be finite and between 0.05 and 60")
    for name, value, low, high in (("max-nodes", options.max_nodes, 1, 10000),
                                  ("inspect-depth", options.inspect_depth, 0, 100)):
        if type(value) is not int or not low <= value <= high:
            raise AXError("invalid_options", f"{name} must be an integer between {low} and {high}")


def _selector(value) -> None:
    if (type(value) is not dict or not value or not set(value) <= FIELDS.keys()
            or any(type(item) is not str or not item for item in value.values())):
        raise AXError("invalid_plan", "selector needs exact nonempty title/identifier/description/role/subrole strings")
    for text in value.values():
        _utf8(text)


def _utf8(text):
    try:
        text.encode("utf-8")
    except UnicodeError as error:
        raise AXError("invalid_plan", "Plan strings must be valid UTF-8") from error


def _validate_plan(plan) -> list[dict]:
    if type(plan) is not dict or set(plan) != {"steps"} or type(plan["steps"]) is not list or not plan["steps"]:
        raise AXError("invalid_plan", "plan must contain a nonempty steps array")
    normalized = []
    for step in plan["steps"]:
        if type(step) is not dict or step.get("action") not in ("set", "invoke", "wait"):
            raise AXError("invalid_plan", "supported actions are set, invoke and wait")
        action = step["action"]
        allowed = {"action", "selector", "within", "window"} | (
            {"value"} if action == "set" else {"property", "equals"} if action == "wait" else set())
        if not set(step) <= allowed:
            raise AXError("invalid_plan", "unsupported step fields")
        _selector(step.get("selector"))
        if "window" in step and (type(step["window"]) is not str or not step["window"]):
            raise AXError("invalid_plan", "step window must be a nonempty string")
        if "window" in step:
            _utf8(step["window"])
        within = step.get("within", [])
        if "within" in step:
            if type(within) is dict:
                within = [within]
            if type(within) is not list or not within:
                raise AXError("invalid_plan", "within must be a selector or nonempty selector array")
            for ancestor in within:
                _selector(ancestor)
        if action == "set" and type(step.get("value")) is not str:
            raise AXError("invalid_plan", "set requires a string value")
        if action == "set":
            _utf8(step["value"])
        if action == "wait":
            prop = step.get("property")
            expected_type = bool if prop == "enabled" else str
            if prop not in ("title", "value", "enabled") or type(step.get("equals")) is not expected_type:
                raise AXError("invalid_plan", "wait requires title/value with a string, or enabled with a JSON boolean")
            if expected_type is str:
                _utf8(step["equals"])
        normalized.append({**step, "within": within})
    return normalized


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class MacWorker:
    """One verified process, exact scopes, durable events and no mutation retries."""

    def __init__(self, native, options: WorkerOptions, emit):
        self.native, self.options, self.emit = native, options, emit
        self.identity = None

    def _event(self, event, fields):
        try:
            self.emit(event, fields)
        except Exception as error:
            raise AXError("journal_error", "Could not persist progress; execution stopped") from error

    def _prepare(self):
        validate_options(self.options)
        if not Path(self.options.executable).is_file():
            raise AXError("invalid_options", "executable must name the real executable file, not an app directory")
        if self.native.trusted() is not True:
            raise AXError("permission_denied", "Accessibility permission is required for the automation host")
        self._identity()

    def _identity(self):
        current = self.native.identity(self.options.target_pid)
        if (current.get("pid") != self.options.target_pid
                or os.path.realpath(current.get("executable", "")) != os.path.realpath(self.options.executable)
                or (self.identity is not None and current != self.identity)):
            raise AXError("process_mismatch", "Target executable or process start time changed")
        if self.identity is None:
            self.identity = current

    def _pid(self, element):
        if self.native.element_pid(element) != self.options.target_pid:
            raise AXError("foreign_process", "Accessibility element is owned by another process")

    def _array(self, element, name, owned):
        values = self.native.attribute(element, name)
        if values is None:
            return []
        if type(values) is not list:
            raise AXError("invalid_data", f"{name} is not an element array")
        # Register every retained view before using any, including failures mid-array.
        owned.extend(value for value in values if callable(getattr(value, "close", None)))
        if any(not callable(getattr(value, "close", None)) for value in values):
            raise AXError("invalid_data", f"{name} contains a non-element")
        return values

    def _windows(self, owned):
        self._identity()
        app = self.native.application(self.options.target_pid)
        owned.append(app)
        self._pid(app)
        windows = self._array(app, "AXWindows", owned)
        if len(windows) > self.options.max_nodes:
            raise AXError("scope_incomplete", "Window enumeration exceeds max-nodes")
        for window in windows:
            self._pid(window)
        return windows

    def _walk(self, root, owned, *, depth=0, partial=False):
        pending = [(root, 0)]
        found = []
        while pending:
            if len(found) >= self.options.max_nodes:
                if partial:
                    return found, True
                raise AXError("scope_incomplete", "Complete selector scan exceeds max-nodes")
            element, level = pending.pop()
            self._pid(element)
            found.append(element)
            if depth == 0 or level < depth:
                children = self._array(element, "AXChildren", owned)
                pending.extend((child, level + 1) for child in reversed(children))
        return found, False

    def _unique(self, root, selector, owned):
        nodes, _ = self._walk(root, owned)
        matches = [element for element in nodes if all(
            self.native.attribute(element, FIELDS[key]) == value for key, value in selector.items())]
        if len(matches) > 1:
            raise AXError("ambiguous_selector", "Multiple controls match; refine selector or within")
        if not matches:
            raise AXError("not_found", "No control matches the exact selector", retryable=True)
        return matches[0]

    def _scope(self, step, operation):
        owned = []
        try:
            windows = self._windows(owned)
            title = step.get("window", self.options.window)
            matches = [window for window in windows if title is None or self.native.attribute(window, "AXTitle") == title]
            if len(matches) > 1:
                raise AXError("ambiguous_window", "Multiple windows match; supply an exact window title")
            if not matches:
                raise AXError("not_found", "No window matches the exact title", retryable=True)
            root = matches[0]
            for ancestor in step.get("within", []):
                root = self._unique(root, ancestor, owned)
            target = self._unique(root, step["selector"], owned) if "selector" in step else root
            return operation(target, owned)
        finally:
            for element in reversed(owned):
                element.close()

    def _password(self, element):
        return (self.native.attribute(element, "AXRole") == "AXSecureTextField"
                or self.native.attribute(element, "AXSubrole") == "AXSecureTextField")

    def _ready(self, element, action):
        self._pid(element)
        if self._password(element):
            raise AXError("protected_control", "Password controls cannot be read or modified")
        if self.native.attribute(element, "AXEnabled") is not True:
            raise AXError("disabled", "Target is not enabled", retryable=True)
        if action == "set":
            if self.native.attribute(element, "AXRole") not in ("AXTextField", "AXTextArea"):
                raise AXError("unsupported", "Only text fields and text areas support set")
            if self.native.is_settable(element, "AXValue") is not True:
                raise AXError("readonly", "AXValue is not settable")
        elif "AXPress" not in self.native.actions(element):
            raise AXError("unsupported", "Target does not expose AXPress")

    def _observe(self, element, prop):
        self._pid(element)
        if prop == "value" and self._password(element):
            raise AXError("protected_control", "Password values cannot be read")
        observed = self.native.attribute(element, {"title": "AXTitle", "value": "AXValue", "enabled": "AXEnabled"}[prop])
        observed_at = _now()
        self._identity()
        return observed, observed_at

    def _poll(self, operation):
        deadline = time.monotonic() + self.options.wait_seconds
        while True:
            try:
                return operation()
            except AXError as error:
                if not error.retryable:
                    raise
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise AXError("timeout", "Condition polling budget exhausted") from error
                time.sleep(min(0.02, remaining))

    def execute(self, plan: dict) -> dict:
        report = {"ok": False, "steps": [], "incomplete_step": None, "may_have_side_effects": False}
        pending = None
        try:
            steps = _validate_plan(plan)  # Entire plan, before any native activity.
            self._prepare()
            for index, step in enumerate(steps):
                started = time.perf_counter()
                action = step["action"]
                self._event("step_started", {"index": index, "action": action})
                pending = {"index": index, "action": action, "phase": "locating"}
                record = {"index": index, "action": action, "selector": step["selector"]}
                if step["within"]:
                    record["within"] = step["within"]
                if "window" in step:
                    record["window"] = step["window"]

                def perform(element, owned):
                    if action == "wait":
                        observed, observed_at = self._observe(element, step["property"])
                        if type(observed) is not type(step["equals"]) or observed != step["equals"]:
                            raise AXError("not_observed", "Expected state is not yet observed", retryable=True)
                        record.update(property=step["property"], observed=observed, observed_at=observed_at)
                        return
                    self._ready(element, action)
                    self._identity()
                    self._event("action_started", {"index": index, "action": action})
                    pending["phase"] = "acting"
                    report["may_have_side_effects"] = True
                    try:
                        if action == "set":
                            self.native.set_attribute(element, "AXValue", step["value"])
                        else:
                            self.native.perform_action(element, "AXPress")
                    except Exception as error:
                        # Even retryable provider failures after dispatch have unknown outcome.
                        raise AXError("action_unknown", "Native mutation failed after dispatch; do not replay automatically") from error

                self._poll(lambda: self._scope(step, perform))
                record["elapsed_ms"] = round((time.perf_counter() - started) * 1000, 2)
                self._event("step_completed", {"index": index, "record": record})
                report["steps"].append(record)
                pending = None
            self._event("run_finished", {"ok": True})
            report.update(ok=True, status="ok")
        except AXError as error:
            report.update(status=error.status, error=str(error))
        if pending:
            pending["outcome"] = "unknown" if pending["phase"] == "acting" else (
                "not_observed" if pending["action"] == "wait" else "not_started")
            report["incomplete_step"] = pending
        return report

    def _describe(self, element):
        self._pid(element)
        return {**{field: self.native.attribute(element, attribute) for field, attribute in FIELDS.items()},
                "actions": self.native.actions(element), "pid": self.options.target_pid}

    def inspect(self) -> dict:
        try:
            self._prepare()
            def describe(root, owned):
                nodes, truncated = self._walk(root, owned, depth=self.options.inspect_depth, partial=True)
                return {"ok": True, "status": "ok", "elements": [self._describe(node) for node in nodes],
                        "truncated": truncated, "steps": []}
            result = self._poll(lambda: self._scope({}, describe))
            self._event("run_finished", {"ok": True})
            return result
        except AXError as error:
            return {"ok": False, "status": error.status, "error": str(error), "steps": []}

    def probe(self) -> dict:
        owned = []
        try:
            self._prepare()
            windows = self._windows(owned)
            result = {"ok": True, "status": "ok", "windows": [self._describe(window) for window in windows], "steps": []}
            self._event("run_finished", {"ok": True})
            return result
        except AXError as error:
            return {"ok": False, "status": error.status, "error": str(error), "steps": []}
        finally:
            for element in reversed(owned):
                element.close()


def _create_native():
    return NativeAX()


def main(argv=None) -> int:
    from run_macos import build_parser, options_from_args

    parser = build_parser()
    parser.add_argument("--run-id", required=True, help=argparse.SUPPRESS)
    parser.add_argument("--plan-stdin", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if not args.journal:
        parser.error("worker requires a pre-created journal")
    if args.plan_stdin and not args.steps:
        parser.error("worker plan input requires steps mode")

    def emit(event, fields):
        record = {"schema_version": 1, "run_id": args.run_id, "event": event, "time": _now(), **fields}
        # The parent creates the journal exclusively; never create missing evidence here.
        with args.journal.open("r+", encoding="utf-8", newline="\n") as stream:
            stream.seek(0, os.SEEK_END)
            stream.write(json.dumps(record, ensure_ascii=False) + "\n")
            stream.flush()
            os.fsync(stream.fileno())

    try:
        options = options_from_args(args, parser)
        plan = None
        if args.steps:
            plan_text = (sys.stdin.buffer.read().decode("utf-8", errors="strict") if args.plan_stdin
                         else args.steps.read_text(encoding="utf-8-sig"))
            plan = json.loads(plan_text)
        if args.steps is not None:
            _validate_plan(plan)
        worker = MacWorker(_create_native(), options, emit)
        result = worker.probe() if args.probe else worker.inspect() if args.inspect else worker.execute(plan)
    except AXError as error:
        result = {"ok": False, "status": error.status, "error": str(error), "steps": []}
    except (OSError, ValueError) as error:
        result = {"ok": False, "status": "invalid_plan", "error": str(error), "steps": []}
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
