#!/usr/bin/env python3
"""Local Gauntlet workflow ledger. Records evidence; never executes target code.

Python 3.10+; standard library only. Use --help and references/tracker.md.
All record batches are transactional. State belongs in a private, trusted directory.
"""
from __future__ import annotations

import argparse
import copy
import datetime as dt
import json
import os
from pathlib import Path
import re
import sqlite3
import sys
from typing import Any

VERSION = "1.0.0"
SCHEMA = 1
MAX_INPUT = 1_048_576
MAX_STATE = 8_388_608
TIERS = {"focused": (2, 1), "standard": (4, 1), "critical": (6, 2)}
LENSES = {
    "core", "correctness-api", "security-privacy", "reliability-data",
    "frontend-accessibility", "performance-operations", "ai-agents",
    "specifications-research",
}
STATUSES = {"candidate", "confirmed", "patched", "verified", "dismissed", "accepted"}
TRANSITIONS = {
    "candidate": {"candidate", "confirmed", "dismissed"},
    "confirmed": {"confirmed", "patched", "dismissed", "accepted"},
    "patched": {"patched", "verified", "confirmed"},
    "verified": {"verified", "patched", "confirmed"},
    "dismissed": {"candidate"},
    "accepted": {"confirmed"},
}
FIELDS = {
    "task": {"id", "status", "evidence", "reason"},
    "add_task": {"id", "title", "lens"},
    "require_check": {"id"},
    "add_lens": {"id", "reason"},
    "finding": {
        "id", "status", "title", "severity", "location", "claim", "evidence",
        "root_cause", "fix", "regression", "verification", "reason", "approval",
    },
    "check": {"id", "kind", "result", "command", "evidence", "exit_code"},
    "target": {"revision", "reason"},
    "close_round": {"angle", "independence", "summary"},
    "next_round": {"reason"},
    "budget": {"max_rounds", "approval", "reason"},
    "note": {"text"},
}


class GauntletError(ValueError):
    """An invalid or unsupported workflow operation."""


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def text(value: Any, label: str, *, limit: int = 12_000) -> str:
    if not isinstance(value, str) or not value.strip():
        raise GauntletError(f"{label} must be a nonempty string")
    if len(value) > limit or "\x00" in value:
        raise GauntletError(f"{label} is too long or contains a NUL character")
    return value.strip()


def ident(value: Any, label: str = "id") -> str:
    value = text(value, label, limit=64)
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,63}", value):
        raise GauntletError(f"{label} must be a 1-64 character simple identifier")
    return value


def choice(value: Any, options: set[str], label: str) -> str:
    if not isinstance(value, str) or value not in options:
        raise GauntletError(f"{label} must be one of: {', '.join(sorted(options))}")
    return value


def integer(value: Any, label: str, low: int, high: int) -> int:
    if type(value) is not int or not low <= value <= high:
        raise GauntletError(f"{label} must be an integer in [{low}, {high}]")
    return value


def no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise GauntletError(f"Duplicate JSON key: {key!r}")
        result[key] = value
    return result


def decode(data: str) -> Any:
    def reject_constant(value: str) -> None:
        raise GauntletError(f"Non-finite JSON value: {value}")
    try:
        return json.loads(data, object_pairs_hook=no_duplicates, parse_constant=reject_constant)
    except (json.JSONDecodeError, RecursionError) as exc:
        raise GauntletError(f"Invalid JSON: {exc}") from exc


def make_state(scope: str, revision: str, mode: str = "review", tier: str = "standard",
               lenses: list[str] | None = None, checks: list[str] | None = None,
               verification: str = "execution", max_rounds: int | None = None) -> dict[str, Any]:
    choice(mode, {"review", "repair"}, "mode")
    choice(tier, set(TIERS), "tier")
    choice(verification, {"execution", "inspection"}, "verification")
    maximum, clean = TIERS[tier]
    if max_rounds is not None:
        maximum = integer(max_rounds, "max_rounds", 1, 20)
    selected = sorted(set(["core", *(lenses or [])]))
    for lens in selected:
        choice(lens, LENSES, "lens")
    required = sorted(set(ident(c, "check") for c in (checks or ["baseline"])))
    return {
        "schema": SCHEMA, "version": VERSION, "created_at": now(), "updated_at": now(),
        "scope": text(scope, "scope"), "revision": text(revision, "revision", limit=500),
        "mode": mode, "tier": tier, "verification": verification,
        "max_rounds": maximum, "required_clean": clean, "required_checks": required,
        "lenses": selected, "round": 1, "closed": False, "changed_in_round": False,
        "tasks": {lens: {"title": lens, "lens": lens, "status": "pending",
                          "evidence": "", "reason": "", "revision": revision,
                          "round": 1} for lens in selected},
        "findings": {}, "checks": {}, "rounds": [], "notes": [], "budget_changes": [],
    }


def validate_state(state: Any) -> dict[str, Any]:
    """Reject corrupted/foreign state before any workflow or write operation."""
    if not isinstance(state, dict) or type(state.get("schema")) is not int or state["schema"] != SCHEMA:
        raise GauntletError("Unsupported or corrupt state schema; restore a trusted ledger")
    for key in ("scope", "revision", "created_at", "updated_at", "version"):
        text(state.get(key), key)
    for key, options in (("mode", {"review", "repair"}), ("tier", set(TIERS)),
                         ("verification", {"execution", "inspection"})):
        choice(state.get(key), options, key)
    for key in ("round", "max_rounds", "required_clean"):
        integer(state.get(key), key, 1, 20)
    if state["round"] > state["max_rounds"]:
        raise GauntletError("Corrupt state: round exceeds budget")
    for key in ("closed", "changed_in_round"):
        if type(state.get(key)) is not bool:
            raise GauntletError(f"Corrupt state: {key} is not boolean")
    for key in ("lenses", "required_checks", "rounds", "notes", "budget_changes"):
        if not isinstance(state.get(key), list):
            raise GauntletError(f"Corrupt state: {key} is not an array")
    if not state["required_checks"] or "core" not in state["lenses"]:
        raise GauntletError("Corrupt state: missing core lens or required checks")
    for lens in state["lenses"]:
        choice(lens, LENSES, "lens")
    for name in state["required_checks"]:
        ident(name)
    for key in ("tasks", "findings", "checks"):
        if not isinstance(state.get(key), dict):
            raise GauntletError(f"Corrupt state: {key} is not an object")
    if any(lens not in state["tasks"] for lens in state["lenses"]):
        raise GauntletError("Corrupt state: missing selected-lens task")
    for key, task in state["tasks"].items():
        ident(key)
        if not isinstance(task, dict):
            raise GauntletError("Corrupt task")
        text(task.get("title"), "task title")
        choice(task.get("status"), {"pending", "done", "blocked", "not_applicable"}, "task status")
        choice(task.get("lens"), LENSES, "task lens")
        integer(task.get("round"), "task round", 1, 20)
        text(task.get("revision"), "task revision")
        for field in ("evidence", "reason"):
            if not isinstance(task.get(field), str):
                raise GauntletError("Corrupt task evidence/reason")
    for key, finding in state["findings"].items():
        ident(key)
        if not isinstance(finding, dict):
            raise GauntletError("Corrupt finding")
        choice(finding.get("status"), STATUSES, "finding status")
        choice(finding.get("severity"), {"critical", "high", "medium", "low"}, "severity")
        for field in ("title", "location", "claim", "found_revision"):
            text(finding.get(field), field)
        integer(finding.get("introduced_round"), "finding round", 1, 20)
        if not isinstance(finding.get("verification"), list):
            raise GauntletError("Corrupt verification references")
        for field in ("evidence", "reason", "root_cause", "fix", "regression", "approval", "verified_revision"):
            if not isinstance(finding.get(field), str):
                raise GauntletError(f"Corrupt finding field: {field}")
    for key, check in state["checks"].items():
        ident(key)
        if not isinstance(check, dict):
            raise GauntletError("Corrupt check")
        choice(check.get("result"), {"pass", "fail", "blocked"}, "check result")
        choice(check.get("kind"), {"execution", "inspection"}, "check kind")
        text(check.get("revision"), "check revision")
        text(check.get("evidence"), "check evidence")
        integer(check.get("round"), "check round", 1, 20)
    for index, item in enumerate(state["rounds"], 1):
        if not isinstance(item, dict) or item.get("number") != index or type(item.get("clean")) is not bool:
            raise GauntletError("Corrupt round history")
        text(item.get("revision"), "round revision")
        text(item.get("angle"), "round angle")
    expected_rounds = state["round"] if state["closed"] else state["round"] - 1
    if len(state["rounds"]) != expected_rounds:
        raise GauntletError("Corrupt round count")
    return state


def task_and_check_gaps(state: dict[str, Any]) -> list[str]:
    gaps = []
    for name, task in state["tasks"].items():
        if task["status"] not in {"done", "not_applicable"}:
            gaps.append(f"task {name}: {task['status']}")
        elif task["revision"] != state["revision"] or task["round"] != state["round"]:
            gaps.append(f"task {name}: stale evidence")
        elif task["status"] == "done" and not task["evidence"].strip():
            gaps.append(f"task {name}: missing evidence")
        elif task["status"] == "not_applicable" and (name == "core" or not task["reason"].strip()):
            gaps.append(f"task {name}: invalid exclusion")
    for name in state["required_checks"]:
        check = state["checks"].get(name)
        if not check:
            gaps.append(f"required check {name}: missing")
        elif check["result"] != "pass":
            gaps.append(f"required check {name}: {check['result']}")
        elif check["revision"] != state["revision"] or check["round"] != state["round"]:
            gaps.append(f"required check {name}: stale evidence")
        elif state["verification"] == "execution" and check["kind"] != "execution":
            gaps.append(f"required check {name}: execution was required")
    for name, check in state["checks"].items():
        if check["revision"] == state["revision"] and check["result"] != "pass" and name not in state["required_checks"]:
            gaps.append(f"additional check {name}: {check['result']}")
    return gaps


def finding_gaps(state: dict[str, Any]) -> list[str]:
    gaps = []
    for name, finding in state["findings"].items():
        status = finding["status"]
        if status == "candidate" or (state["mode"] == "repair" and status in {"confirmed", "patched"}):
            gaps.append(f"finding {name}: {status}")
        if status == "verified":
            if finding["verified_revision"] != state["revision"]:
                gaps.append(f"finding {name}: stale verification")
            if not finding["verification"]:
                gaps.append(f"finding {name}: missing verification references")
            for check_id in finding["verification"]:
                check = state["checks"].get(check_id)
                if not check or check["result"] != "pass" or check["revision"] != state["revision"]:
                    gaps.append(f"finding {name}: invalidated verification check {check_id}")
                elif state["verification"] == "execution" and check["kind"] != "execution":
                    gaps.append(f"finding {name}: verification check {check_id} is no longer execution-backed")
        if status == "accepted" and (finding["severity"] in {"critical", "high"} or not finding["approval"].strip()):
            gaps.append(f"finding {name}: invalid acceptance")
    return gaps


def clean_count(state: dict[str, Any]) -> int:
    count, angles = 0, set()
    for item in reversed(state["rounds"]):
        if not item["clean"] or item["revision"] != state["revision"]:
            break
        angle = " ".join(item["angle"].lower().split())
        if angle in angles:
            break
        angles.add(angle)
        count += 1
    return count


def gate(state: dict[str, Any]) -> dict[str, Any]:
    gaps = task_and_check_gaps(state) + finding_gaps(state)
    count = clean_count(state)
    if not state["closed"]:
        gaps.append("current round is not closed")
    if not gaps and state["mode"] == "review":
        outcome = "REVIEW_COMPLETE"
    elif not gaps and count >= state["required_clean"]:
        outcome = "PASS_WITH_EXCEPTIONS" if any(f["status"] == "accepted" for f in state["findings"].values()) else "PASS_WITHIN_SCOPE"
    else:
        if state["mode"] == "repair" and count < state["required_clean"]:
            gaps.append(f"clean re-attacks: {count}/{state['required_clean']}")
        outcome = "BUDGET_EXHAUSTED" if state["closed"] and state["round"] >= state["max_rounds"] else "BLOCKED"
    return {"outcome": outcome, "reasons": gaps, "round": state["round"],
            "max_rounds": state["max_rounds"], "clean_re_attacks": count,
            "required_clean": state["required_clean"], "revision": state["revision"],
            "mode": state["mode"], "recorded_evidence_only": True}


def apply_event(state: dict[str, Any], event: Any) -> None:
    if not isinstance(event, dict):
        raise GauntletError("Each event must be a JSON object")
    kind = choice(event.get("type"), set(FIELDS), "event type")
    unknown = set(event) - FIELDS[kind] - {"type"}
    if unknown:
        raise GauntletError(f"Unknown {kind} fields: {', '.join(sorted(unknown))}")
    if state["closed"] and kind not in {"next_round", "note", "budget"}:
        raise GauntletError("Round is closed; record next_round before more work")

    if kind == "task":
        name = ident(event.get("id"))
        if name not in state["tasks"]:
            raise GauntletError(f"Unknown task: {name}")
        status = choice(event.get("status"), {"pending", "done", "blocked", "not_applicable"}, "task status")
        evidence = text(event.get("evidence"), "evidence") if status == "done" else ""
        reason = text(event.get("reason"), "reason") if status in {"blocked", "not_applicable"} else ""
        if name == "core" and status == "not_applicable":
            raise GauntletError("The core review cannot be excluded")
        state["tasks"][name].update(status=status, evidence=evidence, reason=reason,
                                    revision=state["revision"], round=state["round"])
    elif kind == "add_task":
        name = ident(event.get("id"))
        if name in state["tasks"]:
            raise GauntletError(f"Task already exists: {name}")
        lens = choice(event.get("lens"), set(state["lenses"]), "selected lens")
        state["tasks"][name] = {"title": text(event.get("title"), "title"), "lens": lens,
                                 "status": "pending", "evidence": "", "reason": "",
                                 "revision": state["revision"], "round": state["round"]}
        state["changed_in_round"] = True
    elif kind == "add_lens":
        lens = choice(event.get("id"), LENSES, "lens")
        reason = text(event.get("reason"), "lens expansion reason")
        if lens in state["lenses"]:
            raise GauntletError("Lens is already selected")
        state["lenses"].append(lens)
        state["tasks"][lens] = {"title": lens, "lens": lens, "status": "pending",
                                "evidence": "", "reason": "", "revision": state["revision"],
                                "round": state["round"]}
        state["changed_in_round"] = True
        state["notes"].append({"round": state["round"], "at": now(), "text": reason})
    elif kind == "require_check":
        name = ident(event.get("id"))
        if name not in state["required_checks"]:
            state["required_checks"].append(name)
            state["changed_in_round"] = True
    elif kind == "check":
        name = ident(event.get("id"))
        check_kind = choice(event.get("kind"), {"execution", "inspection"}, "check kind")
        result = choice(event.get("result"), {"pass", "fail", "blocked"}, "check result")
        evidence = text(event.get("evidence"), "check evidence")
        command = text(event.get("command"), "command/procedure")
        exit_code = event.get("exit_code")
        if check_kind == "execution" and result != "blocked":
            integer(exit_code, "exit_code", -255, 255)
            if result == "pass" and exit_code != 0:
                raise GauntletError("An execution pass requires exit_code 0")
        elif exit_code is not None:
            raise GauntletError("Inspection/blocked checks must omit exit_code")
        state["checks"][name] = {"kind": check_kind, "result": result, "evidence": evidence,
                                 "command": command, "exit_code": exit_code,
                                 "revision": state["revision"], "round": state["round"], "at": now()}
    elif kind == "finding":
        name = ident(event.get("id"))
        old = state["findings"].get(name)
        status = choice(event.get("status"), STATUSES, "finding status")
        if old is None:
            if status not in {"candidate", "confirmed"}:
                raise GauntletError("New findings must start as candidate or confirmed")
            finding = {field: "" for field in ("evidence", "root_cause", "fix", "regression", "reason", "approval", "verified_revision")}
            finding.update(verification=[], introduced_round=state["round"], found_revision=state["revision"])
            for field in ("title", "location", "claim"):
                finding[field] = text(event.get(field), field)
            finding["severity"] = choice(event.get("severity"), {"critical", "high", "medium", "low"}, "severity")
        else:
            if status not in TRANSITIONS[old["status"]]:
                raise GauntletError(f"Invalid transition: {old['status']} -> {status}")
            finding = copy.deepcopy(old)
            if old["status"] in {"dismissed", "accepted"}:
                text(event.get("reason"), "reopening reason")
                finding["introduced_round"] = state["round"]
            if "severity" in event and event["severity"] != old["severity"]:
                text(event.get("reason"), "severity-change reason")
        for field in FIELDS["finding"] - {"id", "status", "verification", "severity"}:
            if field in event:
                finding[field] = text(event[field], field)
        if "severity" in event:
            finding["severity"] = choice(event["severity"], {"critical", "high", "medium", "low"}, "severity")
        if "verification" in event:
            if not isinstance(event["verification"], list):
                raise GauntletError("verification must be an array of check IDs")
            finding["verification"] = [ident(item, "verification check") for item in event["verification"]]
        if status != "candidate":
            text(finding.get("evidence"), "finding evidence")
        if status in {"patched", "verified"}:
            if state["mode"] != "repair":
                raise GauntletError("Review-only mode does not authorize a repair record")
            for field in ("root_cause", "fix", "regression"):
                text(finding.get(field), field)
            if state["revision"] == finding["found_revision"]:
                raise GauntletError("Record the changed target revision before claiming a repair")
        if status == "verified":
            if not finding["verification"]:
                raise GauntletError("Verified fixes require named passing verification checks")
            for check_id in finding["verification"]:
                check = state["checks"].get(check_id)
                if not check or check["result"] != "pass" or check["revision"] != state["revision"] or check["round"] != state["round"]:
                    raise GauntletError(f"Verification check missing, stale, or not passing: {check_id}")
                if state["verification"] == "execution" and check["kind"] != "execution":
                    raise GauntletError("Fix verification requires execution-backed checks")
            finding["verified_revision"] = state["revision"]
        if status == "dismissed":
            text(event.get("reason"), "dismissal reason")
        if status == "accepted":
            if finding["severity"] in {"critical", "high"}:
                raise GauntletError("Critical/high findings cannot be waived in this tracker")
            text(event.get("approval"), "external approval reference")
            text(event.get("reason"), "acceptance rationale")
        finding["status"] = status
        finding["updated_at"] = now()
        state["findings"][name] = finding
    elif kind == "target":
        revision = text(event.get("revision"), "revision", limit=500)
        reason = text(event.get("reason"), "revision change reason")
        if revision == state["revision"]:
            raise GauntletError("New revision must differ; include actual uncommitted changes")
        state["revision"] = revision
        state["changed_in_round"] = True
        state["checks"] = {}
        for task in state["tasks"].values():
            task.update(status="pending", evidence="", reason="", revision=revision, round=state["round"])
        for finding in state["findings"].values():
            if finding["status"] == "verified":
                finding.update(status="patched", verified_revision="", verification=[])
            elif finding["status"] == "accepted":
                finding.update(status="confirmed", approval="", reason="Target changed; reassess residual risk and obtain fresh approval")
            elif state["mode"] == "review" and finding["status"] == "confirmed":
                finding.update(status="candidate", reason="Target changed; substantiate against the new snapshot")
        state["notes"].append({"round": state["round"], "at": now(), "text": f"Target changed: {reason}"})
    elif kind == "close_round":
        angle = text(event.get("angle"), "fresh attack angle")
        independence = choice(event.get("independence"), {"subagent", "solo-role-pass", "human"}, "independence")
        summary = text(event.get("summary"), "round summary")
        gaps = task_and_check_gaps(state) + finding_gaps(state)
        discoveries = [name for name, f in state["findings"].items()
                       if f["introduced_round"] == state["round"] and f["status"] != "dismissed"]
        if state["changed_in_round"]:
            gaps.append("target or review contract changed during this round")
        if discoveries:
            gaps.append("new non-dismissed findings: " + ", ".join(discoveries))
        state["rounds"].append({"number": state["round"], "revision": state["revision"],
                                "clean": not gaps, "gaps": gaps, "angle": angle,
                                "independence": independence, "summary": summary, "at": now()})
        state["closed"] = True
    elif kind == "next_round":
        if not state["closed"]:
            raise GauntletError("Close the current round before opening another")
        reason = text(event.get("reason"), "new strategy / next-round reason")
        if state["round"] >= state["max_rounds"]:
            raise GauntletError("Budget exhausted; stop or record an explicitly approved extension")
        state["round"] += 1
        state["closed"] = False
        state["changed_in_round"] = False
        for task in state["tasks"].values():
            task.update(status="pending", evidence="", reason="", revision=state["revision"], round=state["round"])
        state["notes"].append({"round": state["round"], "at": now(), "text": reason})
    elif kind == "budget":
        maximum = integer(event.get("max_rounds"), "max_rounds", 1, 20)
        if maximum <= state["max_rounds"]:
            raise GauntletError("Budget extension must increase the maximum")
        approval = text(event.get("approval"), "external approval reference")
        reason = text(event.get("reason"), "extension reason")
        state["budget_changes"].append({"from": state["max_rounds"], "to": maximum,
                                        "approval": approval, "reason": reason, "at": now()})
        state["max_rounds"] = maximum
    elif kind == "note":
        state["notes"].append({"round": state["round"], "at": now(), "text": text(event.get("text"), "note")})
    state["updated_at"] = now()


def db_path(value: str) -> Path:
    path = Path(value).expanduser().absolute()
    if path.is_symlink():
        raise GauntletError("Refusing a symlink as the database file")
    return path


def connect(path: Path, *, writable: bool) -> sqlite3.Connection:
    if not path.is_file() or path.is_symlink():
        raise GauntletError("Database is missing or not a regular file; run init first")
    connection = sqlite3.connect(path.as_uri() + ("?mode=rw" if writable else "?mode=ro"),
                                 uri=True, timeout=5, isolation_level=None)
    connection.execute("PRAGMA busy_timeout = 5000")
    connection.execute("PRAGMA trusted_schema = OFF")
    if writable:
        connection.execute("PRAGMA synchronous = FULL")
    return connection


def initialize(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    try:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise GauntletError("Database already exists; refusing to overwrite it") from exc
    os.close(descriptor)
    # If initialization fails, leave the newly created file for inspection; no destructive cleanup.
    conn = connect(path, writable=True)
    try:
        conn.execute("BEGIN IMMEDIATE")
        conn.execute("CREATE TABLE gauntlet_state (id INTEGER PRIMARY KEY CHECK(id=1), payload TEXT NOT NULL)")
        conn.execute("CREATE TABLE gauntlet_events (seq INTEGER PRIMARY KEY AUTOINCREMENT, at TEXT NOT NULL, payload TEXT NOT NULL)")
        conn.execute("INSERT INTO gauntlet_state VALUES (1, ?)", (json.dumps(state, ensure_ascii=True),))
        conn.execute("INSERT INTO gauntlet_events(at,payload) VALUES (?,?)", (now(), json.dumps({"type": "init", "scope": state["scope"]})))
        conn.execute("COMMIT")
    except Exception:
        if conn.in_transaction:
            conn.execute("ROLLBACK")
        raise
    finally:
        conn.close()


def load(conn: sqlite3.Connection) -> dict[str, Any]:
    row = conn.execute("SELECT payload FROM gauntlet_state WHERE id=1").fetchone()
    if row is None or not isinstance(row[0], str) or len(row[0].encode("utf-8")) > MAX_STATE:
        raise GauntletError("Missing or oversized state; restore a trusted ledger")
    return validate_state(decode(row[0]))


def record(path: Path, payload: Any) -> dict[str, Any]:
    events = payload if isinstance(payload, list) else [payload]
    if not 1 <= len(events) <= 100:
        raise GauntletError("A batch must contain 1-100 events")
    conn = connect(path, writable=True)
    try:
        conn.execute("BEGIN IMMEDIATE")
        state = load(conn)
        for event in events:
            apply_event(state, event)
            validate_state(state)
            conn.execute("INSERT INTO gauntlet_events(at,payload) VALUES (?,?)", (now(), json.dumps(event, ensure_ascii=True)))
        encoded = json.dumps(state, ensure_ascii=True, allow_nan=False)
        if len(encoded.encode("utf-8")) > MAX_STATE:
            raise GauntletError("State exceeds 8 MiB; preserve the ledger and narrow the run")
        conn.execute("UPDATE gauntlet_state SET payload=? WHERE id=1", (encoded,))
        conn.execute("COMMIT")
        return state
    except Exception:
        if conn.in_transaction:
            conn.execute("ROLLBACK")
        raise
    finally:
        conn.close()


def read_state(path: Path) -> dict[str, Any]:
    conn = connect(path, writable=False)
    try:
        return load(conn)
    finally:
        conn.close()


def summary(state: dict[str, Any]) -> dict[str, Any]:
    return {**gate(state), "scope": state["scope"], "tier": state["tier"],
            "tasks": {name: task["status"] for name, task in state["tasks"].items()},
            "findings": {name: {"status": f["status"], "severity": f["severity"], "title": f["title"]}
                         for name, f in state["findings"].items()},
            "checks": {name: {"result": c["result"], "kind": c["kind"], "round": c["round"]}
                       for name, c in state["checks"].items()}}


def safe_md(value: Any) -> str:
    value = str(value)
    value = "".join(c for c in value if c in "\n\t" or ord(c) >= 32)
    return value.replace("<", "&lt;").replace(">", "&gt;").replace("|", "\\|")


def report(state: dict[str, Any]) -> str:
    verdict = gate(state)
    lines = ["# Gauntlet report", "", f"**Outcome:** {verdict['outcome']}",
             f"**Mode:** {state['mode']} | **Tier:** {state['tier']} | **Rounds:** {state['round']}/{state['max_rounds']}",
             f"**Scope:** {safe_md(state['scope'])}", f"**Revision:** {safe_md(state['revision'])}", "",
             "This report summarizes recorded attestations; the tracker does not execute or authenticate checks.",
             "A scoped pass is not a guarantee that all defects are absent.", "", "## Gate", ""]
    lines += [f"- {safe_md(reason)}" for reason in verdict["reasons"]] or ["Declared workflow gates are satisfied."]
    lines += ["", "## Findings", ""]
    if not state["findings"]:
        lines.append("No findings recorded; see coverage and check evidence below.")
    for name, finding in state["findings"].items():
        lines += [f"### {name}: {safe_md(finding['title'])}",
                  f"{finding['severity']} / {finding['status']}"]
        for field in ("location", "claim", "evidence", "root_cause", "fix", "regression", "verification", "approval", "reason"):
            if finding.get(field):
                lines.append(f"**{field}:** {safe_md(finding[field])}")
        lines.append("")
    lines += ["## Task coverage", ""]
    for name, task in state["tasks"].items():
        lines.append(f"- **{name}: {task['status']}** — {safe_md(task['evidence'] or task['reason'])}")
    lines += ["", "## Recorded checks", ""]
    for name, check in state["checks"].items():
        lines += [f"### {name}: {check['result']} ({check['kind']})",
                  f"Snapshot: {safe_md(check['revision'])}; round: {check['round']}",
                  f"Command/procedure: {safe_md(check['command'])}",
                  f"Evidence: {safe_md(check['evidence'])}", ""]
    lines += ["## Rounds", ""]
    for item in state["rounds"]:
        lines.append(f"- Round {item['number']}: clean={item['clean']}; {safe_md(item['independence'])}; {safe_md(item['angle'])}. {safe_md(item['summary'])}")
    lines += ["", "## Notes and limitations", ""]
    lines += [f"- {safe_md(note['text'])}" for note in state["notes"]]
    lines += ["", "Review the recorded evidence, unexamined surfaces, and actual deployment state before a release decision."]
    return "\n".join(lines) + "\n"


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--version", action="version", version=VERSION)
    commands = p.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init", help="Create a new ledger; never overwrite")
    init.add_argument("--db", required=True)
    init.add_argument("--scope", required=True)
    init.add_argument("--revision", required=True)
    init.add_argument("--mode", choices=["review", "repair"], default="review")
    init.add_argument("--tier", choices=sorted(TIERS), default="standard")
    init.add_argument("--lenses", default="", help="Comma-separated additional lenses; core is always included")
    init.add_argument("--checks", default="baseline", help="Comma-separated required check IDs")
    init.add_argument("--verification", choices=["execution", "inspection"], default="execution")
    init.add_argument("--max-rounds", type=int)
    rec = commands.add_parser("record", help="Apply one JSON event or an atomic array of events")
    rec.add_argument("--db", required=True)
    sources = rec.add_mutually_exclusive_group(required=True)
    sources.add_argument("--input", help="UTF-8 JSON file; use - for stdin, maximum 1 MiB")
    sources.add_argument("--event", help="Inline JSON event (be careful with shell quoting)")
    for name, help_text in (("status", "Compact JSON summary"), ("snapshot", "Full state JSON, without event history"),
                            ("gate", "Exit 0 for completion, 3 for blocked, 4 for budget exhaustion"),
                            ("report", "Markdown report to stdout; no automatic file writes")):
        sub = commands.add_parser(name, help=help_text)
        sub.add_argument("--db", required=True)
    return p


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        path = db_path(args.db)
        if args.command == "init":
            split = lambda value: [part.strip() for part in value.split(",") if part.strip()]
            state = make_state(args.scope, args.revision, args.mode, args.tier,
                               split(args.lenses), split(args.checks), args.verification, args.max_rounds)
            initialize(path, state)
        elif args.command == "record":
            if args.event is not None:
                raw = args.event.encode("utf-8")
            elif args.input == "-":
                raw = sys.stdin.buffer.read(MAX_INPUT + 1)
            else:
                with open(args.input, "rb") as handle:
                    raw = handle.read(MAX_INPUT + 1)
            if len(raw) > MAX_INPUT:
                raise GauntletError("Event input exceeds 1 MiB")
            state = record(path, decode(raw.decode("utf-8")))
        else:
            state = read_state(path)
        if args.command == "report":
            sys.stdout.write(report(state))
        else:
            result = state if args.command == "snapshot" else gate(state) if args.command == "gate" else summary(state)
            print(json.dumps(result, ensure_ascii=True, indent=2, allow_nan=False))
        if args.command == "gate":
            outcome = gate(state)["outcome"]
            return 4 if outcome == "BUDGET_EXHAUSTED" else 3 if outcome == "BLOCKED" else 0
        return 0
    except (GauntletError, OSError, UnicodeError, sqlite3.Error, KeyError, TypeError, RecursionError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:
        # Suppress a second flush error when output is piped to a short-lived reader.
        try:
            sys.stdout.close()
        except BrokenPipeError:
            pass
        raise SystemExit(0)
