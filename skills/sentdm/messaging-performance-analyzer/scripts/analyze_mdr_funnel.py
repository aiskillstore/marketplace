#!/usr/bin/env python3
"""Analyze Sent MDR records by channel, direction, lifecycle, and outcome.

The analyzer uses only statuses that are present in each record. A record with
only ``status=DELIVERED`` contributes one observed DELIVERED status; it does not
implicitly contribute QUEUED, ROUTED, or SENT transitions. Full ``statuses``
histories can contribute explicit transition rates.

Exit codes:
    0 - usable cohort with no threshold breach, or usable outcome-only data
    2 - bad arguments, malformed input, or no usable analysis cohort
    3 - one or more explicit delivery/engagement transitions breach threshold
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


DELIVERY_STAGES: tuple[str, ...] = ("QUEUED", "ROUTED", "SENT", "DELIVERED")
ENGAGEMENT_STAGE = "READ"
KNOWN_STATUSES = set(DELIVERY_STAGES) | {ENGAGEMENT_STAGE, "FAILED", "DEFERRED", "RECEIVED"}
OUTCOMES: tuple[str, ...] = (
    "progression",
    "terminal_failure",
    "deferred",
    "inbound",
    "malformed",
    "unknown",
)
SUPPORTED_CHANNELS = {"sms", "whatsapp", "rcs"}
READ_CHANNELS = {"whatsapp", "rcs"}
OUTBOUND_DIRECTIONS = {"outbound", "outgoing", "mt"}
INBOUND_DIRECTIONS = {"inbound", "incoming", "mo"}
_ERR_CODE_RE = re.compile(r"\bERR_[A-Z0-9_]+\b")
_STATUS_KEYS = ("status", "stage", "latest_status")


class InputError(Exception):
    """Raised for missing or structurally invalid input. Maps to exit code 2."""


@dataclass(frozen=True)
class NormalizedRecord:
    """One input row normalized without inventing lifecycle evidence."""

    index: int
    channel: str
    direction: str
    observed_statuses: tuple[str, ...]
    has_history: bool
    outcome: str
    diagnostics: tuple[str, ...]
    error_codes: tuple[str, ...]


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="analyze_mdr_funnel.py", description=__doc__)
    parser.add_argument("path", help="MDR export path (.json or .csv)")
    parser.add_argument(
        "--threshold",
        type=float,
        default=20.0,
        help="Explicit transition drop-off percentage that triggers exit 3 (default: 20)",
    )
    parser.add_argument(
        "--show-errors",
        action="store_true",
        help="Include ERR_* codes from FAILED record descriptions",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format (default: text)",
    )
    return parser.parse_args(argv)


def _load_messages(path: Path) -> list[object]:
    if not path.is_file():
        raise InputError(f"file not found: {path}")
    extension = path.suffix.lower()
    if extension == ".json":
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except OSError as exc:
            raise InputError(f"could not read {path}: {exc}") from exc
        except json.JSONDecodeError as exc:
            raise InputError(f"invalid JSON in {path}: {exc}") from exc
        if isinstance(data, dict) and "messages" in data:
            data = data["messages"]
        if not isinstance(data, list):
            raise InputError('JSON must be a list of message records or {"messages": [...]}')
        return data
    if extension == ".csv":
        try:
            with path.open("r", encoding="utf-8", newline="") as handle:
                return list(csv.DictReader(handle))
        except (OSError, csv.Error, UnicodeError) as exc:
            raise InputError(f"invalid CSV in {path}: {exc}") from exc
    raise InputError(f"unsupported file extension '{extension}'; expected .json or .csv")


def _field(record: dict[str, Any], name: str) -> Any:
    if name in record:
        return record[name]
    payload = record.get("payload")
    return payload.get(name) if isinstance(payload, dict) else None


def _normalize_channel(value: Any, diagnostics: list[str]) -> str:
    if not isinstance(value, str) or not value.strip():
        diagnostics.append("channel missing; grouped as unknown")
        return "unknown"
    channel = value.strip().lower()
    if channel not in SUPPORTED_CHANNELS:
        diagnostics.append(f"unsupported channel {value!r}; grouped as unknown")
        return "unknown"
    return channel


def _normalize_direction(value: Any, diagnostics: list[str]) -> str:
    if not isinstance(value, str) or not value.strip():
        diagnostics.append("direction missing; grouped as unknown")
        return "unknown"
    direction = value.strip().lower()
    if direction in OUTBOUND_DIRECTIONS:
        return "outbound"
    if direction in INBOUND_DIRECTIONS:
        return "inbound"
    diagnostics.append(f"unsupported direction {value!r}; grouped as unknown")
    return "unknown"


def _normalize_statuses(record: dict[str, Any], diagnostics: list[str]) -> tuple[tuple[str, ...], bool]:
    if "statuses" in record:
        history = record["statuses"]
        if not isinstance(history, list):
            diagnostics.append("statuses must be an array")
            return (), False
        statuses: list[str] = []
        for position, entry in enumerate(history, 1):
            if not isinstance(entry, dict):
                diagnostics.append(f"statuses[{position}] must be an object")
                continue
            value = next((entry.get(key) for key in _STATUS_KEYS if isinstance(entry.get(key), str)), None)
            if value is None or not value.strip():
                diagnostics.append(f"statuses[{position}] has no status/stage value")
                continue
            statuses.append(value.strip().upper())
        return tuple(statuses), True

    for key in _STATUS_KEYS:
        value = _field(record, key)
        if isinstance(value, str) and value.strip():
            return (value.strip().upper(),), False
    diagnostics.append("record has no observed status")
    return (), False


def normalize_record(record: object, index: int) -> NormalizedRecord:
    if not isinstance(record, dict):
        return NormalizedRecord(
            index=index,
            channel="unknown",
            direction="unknown",
            observed_statuses=(),
            has_history=False,
            outcome="malformed",
            diagnostics=("record must be an object",),
            error_codes=(),
        )

    diagnostics: list[str] = []
    channel = _normalize_channel(_field(record, "channel"), diagnostics)
    direction = _normalize_direction(_field(record, "direction"), diagnostics)
    statuses, has_history = _normalize_statuses(record, diagnostics)
    unknown_statuses = sorted({status for status in statuses if status not in KNOWN_STATUSES})
    if unknown_statuses:
        diagnostics.append("unknown status values: " + ", ".join(unknown_statuses))

    known = tuple(status for status in statuses if status in KNOWN_STATUSES)
    latest = known[-1] if known else None
    if direction == "inbound" or latest == "RECEIVED":
        direction = "inbound"
        outcome = "inbound"
    elif latest == "FAILED":
        outcome = "terminal_failure"
    elif latest == "DEFERRED" or latest in {"QUEUED", "ROUTED", "SENT"}:
        outcome = "deferred"
    elif latest in {"DELIVERED", "READ"}:
        outcome = "progression"
    else:
        outcome = "unknown"

    if channel == "sms" and "READ" in known:
        diagnostics.append("READ is not used for SMS delivery or engagement analysis")
    description = _field(record, "description")
    error_codes = tuple(sorted(set(_ERR_CODE_RE.findall(description)))) if isinstance(description, str) else ()
    return NormalizedRecord(
        index=index,
        channel=channel,
        direction=direction,
        observed_statuses=statuses,
        has_history=has_history,
        outcome=outcome,
        diagnostics=tuple(diagnostics),
        error_codes=error_codes,
    )


def _completed_transition(statuses: tuple[str, ...], source: str, target: str) -> bool:
    try:
        source_index = statuses.index(source)
    except ValueError:
        return False
    return target in statuses[source_index + 1 :]


def _transition(
    records: list[NormalizedRecord], source: str, target: str, threshold: float
) -> dict[str, object]:
    terminal = {"progression", "terminal_failure"}
    eligible_records = [
        record
        for record in records
        if record.has_history and record.outcome in terminal and source in record.observed_statuses
    ]
    completed = sum(
        _completed_transition(record.observed_statuses, source, target) for record in eligible_records
    )
    eligible = len(eligible_records)
    dropoff = round((eligible - completed) / eligible * 100.0, 4) if eligible else None
    return {
        "from": source,
        "to": target,
        "eligible": eligible,
        "completed": completed,
        "dropoff_pct": dropoff,
        "exceeds_threshold": dropoff is not None and dropoff > threshold,
    }


def _totals(records: Iterable[NormalizedRecord]) -> dict[str, int]:
    records = list(records)
    counts = Counter(record.outcome for record in records)
    return {
        "input": len(records),
        "usable": sum(counts[name] for name in ("progression", "terminal_failure", "deferred")),
        **{name: counts[name] for name in OUTCOMES},
    }


def _group_report(
    channel: str,
    direction: str,
    records: list[NormalizedRecord],
    threshold: float,
) -> dict[str, object]:
    delivery_statuses = {
        stage: sum(stage in record.observed_statuses for record in records) for stage in DELIVERY_STAGES
    }
    transitions = [
        _transition(records, source, target, threshold)
        for source, target in zip(DELIVERY_STAGES, DELIVERY_STAGES[1:])
    ]
    engagement: dict[str, object] | None = None
    if channel in READ_CHANNELS:
        read_transition = _transition(records, "DELIVERED", "READ", threshold)
        engagement = {
            "delivered": read_transition["eligible"],
            "read": read_transition["completed"],
            "read_rate_pct": (
                round(100.0 - float(read_transition["dropoff_pct"]), 4)
                if read_transition["dropoff_pct"] is not None
                else None
            ),
            "dropoff_pct": read_transition["dropoff_pct"],
            "exceeds_threshold": read_transition["exceeds_threshold"],
        }
    return {
        "channel": channel,
        "direction": direction,
        "totals": _totals(records),
        "progression": {"observed": delivery_statuses, "transitions": transitions},
        "engagement": engagement,
    }


def build_report(
    records: list[NormalizedRecord],
    threshold: float,
    include_errors: bool,
) -> dict[str, object]:
    grouped: dict[tuple[str, str], list[NormalizedRecord]] = defaultdict(list)
    for record in records:
        grouped[(record.channel, record.direction)].append(record)
    groups = [
        _group_report(channel, direction, grouped[(channel, direction)], threshold)
        for channel, direction in sorted(grouped)
    ]
    anomalies: list[dict[str, object]] = []
    evaluated = 0
    for group in groups:
        for transition in group["progression"]["transitions"]:
            if transition["dropoff_pct"] is not None:
                evaluated += 1
            if transition["exceeds_threshold"]:
                anomalies.append(
                    {
                        "kind": "delivery",
                        "channel": group["channel"],
                        "direction": group["direction"],
                        **transition,
                    }
                )
        engagement = group["engagement"]
        if engagement is not None:
            if engagement["dropoff_pct"] is not None:
                evaluated += 1
            if engagement["exceeds_threshold"]:
                anomalies.append(
                    {
                        "kind": "engagement",
                        "channel": group["channel"],
                        "direction": group["direction"],
                        "from": "DELIVERED",
                        "to": "READ",
                        "eligible": engagement["delivered"],
                        "completed": engagement["read"],
                        "dropoff_pct": engagement["dropoff_pct"],
                        "exceeds_threshold": True,
                    }
                )
    totals = _totals(records)
    healthy: bool | None
    if not totals["usable"] or not evaluated:
        healthy = None
    else:
        healthy = not anomalies
    diagnostics = [
        {"record": record.index, "messages": list(record.diagnostics)}
        for record in records
        if record.diagnostics
    ]
    error_codes = Counter(
        code
        for record in records
        if record.outcome == "terminal_failure"
        for code in record.error_codes
    )
    return {
        "schema_version": 1,
        "threshold_pct": threshold,
        "healthy": healthy,
        "totals": totals,
        "groups": groups,
        "anomalies": anomalies,
        "diagnostics": diagnostics,
        "error_codes": dict(sorted(error_codes.items())) if include_errors else None,
    }


def analyze(records: Iterable[object], threshold: float, include_errors: bool) -> dict[str, object]:
    normalized = [normalize_record(record, index) for index, record in enumerate(records, 1)]
    return build_report(normalized, threshold, include_errors)


def summarise_errors(messages: Iterable[dict]) -> Counter:
    """Return ERR_* code counts from records whose observed outcome is FAILED."""
    counter: Counter = Counter()
    for index, record in enumerate(messages, 1):
        normalized = normalize_record(record, index)
        if normalized.outcome == "terminal_failure":
            counter.update(normalized.error_codes)
    return counter


def _percent(value: object) -> str:
    return "N/A" if value is None else f"{float(value):.1f}%"


def render_text(report: dict[str, object]) -> str:
    totals = report["totals"]
    lines = [
        f"Records: {totals['input']} input, {totals['usable']} usable",
        "Outcomes: " + ", ".join(f"{name}={totals[name]}" for name in OUTCOMES),
    ]
    for group in report["groups"]:
        lines.extend(
            (
                "",
                f"Group: channel={group['channel']} direction={group['direction']}",
                "  Outcomes: " + ", ".join(f"{name}={group['totals'][name]}" for name in OUTCOMES),
                "  Observed: "
                + ", ".join(
                    f"{stage}={group['progression']['observed'][stage]}" for stage in DELIVERY_STAGES
                ),
                "  Delivery transitions:",
            )
        )
        for transition in group["progression"]["transitions"]:
            lines.append(
                f"    {transition['from']} -> {transition['to']}: "
                f"{_percent(transition['dropoff_pct'])} "
                f"({transition['completed']}/{transition['eligible']} completed)"
            )
        if group["engagement"] is not None:
            engagement = group["engagement"]
            lines.append("  Engagement:")
            lines.append(
                "    DELIVERED -> READ: "
                f"{_percent(engagement['dropoff_pct'])} "
                f"({engagement['read']}/{engagement['delivered']} read)"
            )
    if report["error_codes"] is not None:
        lines.append("")
        lines.append("ERR_* codes:")
        if report["error_codes"]:
            lines.extend(f"  {code}: {count}" for code, count in report["error_codes"].items())
        else:
            lines.append("  (none found)")
    if report["diagnostics"]:
        lines.append("")
        lines.append(f"Validation diagnostics: {len(report['diagnostics'])} record(s)")
        for diagnostic in report["diagnostics"]:
            lines.append(f"  record {diagnostic['record']}: " + "; ".join(diagnostic["messages"]))
    lines.append("")
    if not totals["usable"]:
        lines.append("INSUFFICIENT: no usable analysis cohort exists.")
    elif report["healthy"] is None:
        lines.append("INDETERMINATE: outcomes are usable, but no explicit transition denominator exists.")
    elif report["healthy"]:
        lines.append(f"OK: no explicit transition exceeded {report['threshold_pct']}% drop-off.")
    else:
        lines.append(
            f"FAIL: {len(report['anomalies'])} explicit transition(s) exceeded "
            f"{report['threshold_pct']}% drop-off."
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    if not 0 <= args.threshold <= 100:
        print("error: --threshold must be between 0 and 100", file=sys.stderr)
        return 2
    try:
        records = _load_messages(Path(args.path))
    except InputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    report = analyze(records, args.threshold, args.show_errors)
    if args.format == "json":
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(render_text(report))

    if report["totals"]["usable"] == 0:
        if args.format == "text":
            print("error: no usable analysis cohort exists", file=sys.stderr)
        return 2
    if report["healthy"] is False:
        if args.format == "text":
            print(f"FAIL: {len(report['anomalies'])} transition threshold breach(es)", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
