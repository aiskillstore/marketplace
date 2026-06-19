#!/usr/bin/env python3
"""Review Studio gate keys, scoring, and contract checks."""

from collections import Counter
from typing import Any


SCRIPT_INTERFACE = "internal-module"
SCRIPT_INTERFACE_REASON = "Imported by review_studio_gates.py for stable gate scoring and contract checks."


GATE_WEIGHTS = {
    "trigger-lab": 15,
    "output-lab": 20,
    "context-budget": 10,
    "runtime-matrix": 10,
    "trust-report": 10,
    "python-compat": 10,
    "architecture-maintainability": 10,
    "permission-gates": 10,
    "permission-runtime": 10,
    "skill-atlas": 10,
    "operations-loop": 10,
    "review-waivers": 10,
    "world-class-evidence": 10,
    "registry-audit": 10,
    "release-notes": 10,
    "intent-canvas": 10,
}
REVIEW_STUDIO_GATE_KEYS = frozenset(GATE_WEIGHTS)


def status_label(status: str) -> str:
    return {"pass": "通过", "warn": "关注", "block": "阻断"}.get(status, status)


def add_blockers_from_gate(gates: list[dict[str, str]]) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    blockers = [item for item in gates if item["status"] == "block"]
    warnings = [item for item in gates if item["status"] == "warn"]
    return blockers, warnings


def gate_contract(gates: list[dict[str, str]]) -> dict[str, Any]:
    rendered_gate_keys = [str(item.get("key", "")) for item in gates]
    rendered_gate_set = set(rendered_gate_keys)
    expected_gate_set = set(REVIEW_STUDIO_GATE_KEYS)
    duplicate_gate_keys = sorted(key for key, count in Counter(rendered_gate_keys).items() if count > 1)
    missing_gate_keys = sorted(expected_gate_set - rendered_gate_set)
    unknown_gate_keys = sorted(rendered_gate_set - expected_gate_set)
    unweighted_gate_keys = sorted(rendered_gate_set - set(GATE_WEIGHTS))
    return {
        "ok": not (missing_gate_keys or unknown_gate_keys or duplicate_gate_keys or unweighted_gate_keys),
        "expected_gate_count": len(expected_gate_set),
        "actual_gate_count": len(rendered_gate_keys),
        "expected_gate_keys": sorted(expected_gate_set),
        "rendered_gate_keys": rendered_gate_keys,
        "missing_gate_keys": missing_gate_keys,
        "unknown_gate_keys": unknown_gate_keys,
        "duplicate_gate_keys": duplicate_gate_keys,
        "unweighted_gate_keys": unweighted_gate_keys,
    }


def min_output_cases(maturity: str) -> int:
    if maturity in {"library", "governed"}:
        return 5
    if maturity == "production":
        return 3
    return 1


def weighted_score(gates: list[dict[str, str]]) -> int:
    earned = 0.0
    total = 0.0
    for item in gates:
        weight = GATE_WEIGHTS.get(item["key"], 5)
        total += weight
        if item["status"] == "pass":
            earned += weight
        elif item["status"] == "warn":
            earned += weight * 0.6
    return int(round(earned / total * 100)) if total else 0
