#!/usr/bin/env python3
"""Delegation-First Coordinator Policy evaluator."""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import sys
from typing import Any, Sequence

sys.dont_write_bytecode = True

TOKEN_DISCLAIMER = "Token observations are not billing, quota, or general savings evidence."
FIXED_OVERHEAD_WARNING = (
    "Small tasks incur fixed initialization overhead (prompt staging, sandbox setup, "
    "provider round-trip); token observations are not billing, quota, or cost-savings evidence."
)

MODEL_SLUG_RE = re.compile(r"^[a-zA-Z0-9._:-]{1,100}\Z")
EFFORT_SET = {"low", "medium", "high", "none", "unspecified"}

VALID_INPUT_KEYS = {
    "schema_version",
    "kind",
    "policy",
    "intent",
    "user_opt_in",
    "transmission_approved",
    "scope_path_approved",
    "preflight_passed",
    "provider_state",
    "hard_stop_triggered",
    "hard_stop_reasons",
    "cycle_budget_exhausted",
    "attempt_count",
    "max_cycles",
    "prior_candidate_available",
    "caller_model",
    "caller_effort",
}


class DelegationPolicyError(Exception):
    """Delegation policy validation or evaluation failure."""


def validate_input(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise DelegationPolicyError("policy input must be a JSON object")

    extra_keys = set(data) - VALID_INPUT_KEYS
    if extra_keys:
        raise DelegationPolicyError(f"unrecognized input keys: {sorted(extra_keys)!r}")

    schema_version = data.get("schema_version", 1)
    if schema_version != 1:
        raise DelegationPolicyError(f"unsupported schema_version {schema_version!r}")

    kind = data.get("kind", "agy-delegation-policy-input")
    if kind != "agy-delegation-policy-input":
        raise DelegationPolicyError(f"unsupported kind {kind!r}")

    policy = data.get("policy")
    if policy not in {"delegation-first", "direct-codex", "second-eye"}:
        raise DelegationPolicyError(f"invalid policy {policy!r}")

    intent = data.get("intent")
    if intent not in {"explore", "task", "project"}:
        raise DelegationPolicyError(f"invalid intent {intent!r}")

    if "user_opt_in" in data and not isinstance(data["user_opt_in"], bool):
        raise DelegationPolicyError("user_opt_in must be a boolean")

    for bool_field in (
        "transmission_approved", "scope_path_approved", "preflight_passed",
        "hard_stop_triggered", "cycle_budget_exhausted",
    ):
        if not isinstance(data.get(bool_field), bool):
            raise DelegationPolicyError(f"field {bool_field} must be a boolean")

    if "prior_candidate_available" in data and not isinstance(data["prior_candidate_available"], bool):
        raise DelegationPolicyError("prior_candidate_available must be a boolean")

    provider_state = data.get("provider_state")
    if provider_state not in {"available", "unavailable", "quota_exhausted", "rate_limited", "unverified"}:
        raise DelegationPolicyError(f"invalid provider_state {provider_state!r}")

    hard_stop_reasons = data.get("hard_stop_reasons", [])
    if not isinstance(hard_stop_reasons, list) or not all(isinstance(x, str) for x in hard_stop_reasons):
        raise DelegationPolicyError("hard_stop_reasons must be a list of strings")

    attempt_count = data.get("attempt_count", 0)
    if type(attempt_count) is not int or attempt_count < 0:
        raise DelegationPolicyError("attempt_count must be a non-negative integer")

    max_cycles = data.get("max_cycles", 1)
    if type(max_cycles) is not int or max_cycles < 1:
        raise DelegationPolicyError("max_cycles must be a positive integer")

    caller_model = data.get("caller_model")
    if caller_model is not None:
        if not isinstance(caller_model, str) or not MODEL_SLUG_RE.fullmatch(caller_model):
            raise DelegationPolicyError(f"caller_model must be a bounded valid string: {caller_model!r}")

    caller_effort = data.get("caller_effort")
    if caller_effort is not None:
        if not isinstance(caller_effort, str) or caller_effort not in EFFORT_SET:
            raise DelegationPolicyError(f"caller_effort must be a bounded effort enum: {caller_effort!r}")

    return data


def evaluate_policy(data: dict[str, Any]) -> dict[str, Any]:
    validate_input(data)

    policy = data["policy"]
    intent = data["intent"]
    user_opt_in = data.get("user_opt_in")
    transmission_approved = data["transmission_approved"]
    scope_path_approved = data["scope_path_approved"]
    preflight_passed = data["preflight_passed"]
    provider_state = data["provider_state"]
    hard_stop_triggered = data["hard_stop_triggered"]
    cycle_budget_exhausted = data["cycle_budget_exhausted"] or (data.get("attempt_count", 0) >= data.get("max_cycles", 1))
    prior_candidate_available = data.get("prior_candidate_available", False)
    caller_model = data.get("caller_model")
    caller_effort = data.get("caller_effort")

    # Base response
    decision_record: dict[str, Any] = {
        "schema_version": 1,
        "kind": "agy-delegation-policy-decision",
        "policy": policy,
        "intent": intent,
        "decision": "blocked",
        "first_substantive_actor": "none",
        "required_pre_steps": [],
        "reason_code": "hard-stop-active",
        "caller_model": caller_model,
        "caller_effort": caller_effort,
        "silent_fallback_authorized": False,
        "direct_codex_authorized": False,
        "git_authorized": False,
        "acceptance_authorized": False,
        "fixed_overhead_warning": FIXED_OVERHEAD_WARNING,
        "token_disclaimer": TOKEN_DISCLAIMER,
        "rationale": "",
    }

    # 1. Check hard stops and scope approval first
    if hard_stop_triggered:
        decision_record["decision"] = "blocked"
        decision_record["reason_code"] = "hard-stop-active"
        decision_record["rationale"] = "A hard stop condition was triggered; execution is halted."
        return decision_record

    if not scope_path_approved:
        decision_record["decision"] = "blocked"
        decision_record["reason_code"] = "missing-scope-approval"
        decision_record["rationale"] = "Repository or path scope has not been approved by the user."
        return decision_record

    # 2. Direct-Codex Override (Needs no provider transmission, preflight, or provider availability)
    if policy == "direct-codex":
        decision_record.update({
            "decision": "direct-codex",
            "first_substantive_actor": "codex",
            "required_pre_steps": ["scope_privacy_approval", "disposable_worktree_setup", "verification_planning"],
            "reason_code": "direct-codex-override",
            "direct_codex_authorized": True,
            "rationale": "Direct Codex implementation explicitly selected by caller policy override; provider transmission is not required.",
        })
        return decision_record

    # 3. Explicit User Opt-In for Delegation-First (must be present and literal True)
    if policy == "delegation-first" and (user_opt_in is not True or "user_opt_in" not in data):
        decision_record.update({
            "decision": "blocked",
            "first_substantive_actor": "none",
            "reason_code": "missing-user-opt-in",
            "direct_codex_authorized": False,
            "rationale": "Explicit user opt-in (user_opt_in: true) is required to enable delegation-first coordinator policy.",
        })
        return decision_record

    # 4. Provider-dependent paths (second-eye and delegation-first) require transmission approval
    if not transmission_approved:
        decision_record["decision"] = "blocked"
        decision_record["reason_code"] = "missing-transmission-approval"
        decision_record["rationale"] = "External provider transmission has not been approved by the user."
        return decision_record

    # 5. Preflight check for provider-dependent paths
    if not preflight_passed:
        decision_record.update({
            "decision": "blocked",
            "first_substantive_actor": "none",
            "reason_code": "preflight-failed",
            "direct_codex_authorized": False,
            "rationale": "AGY preflight checks failed; silent fallback to Codex is prohibited.",
        })
        return decision_record

    # 6. Provider availability check
    if provider_state == "quota_exhausted":
        decision_record.update({
            "decision": "blocked",
            "first_substantive_actor": "none",
            "reason_code": "provider-quota-exhausted",
            "direct_codex_authorized": False,
            "rationale": "Provider quota is exhausted; silent fallback to Codex is prohibited.",
        })
        return decision_record

    if provider_state != "available":
        decision_record.update({
            "decision": "blocked",
            "first_substantive_actor": "none",
            "reason_code": "provider-unavailable",
            "direct_codex_authorized": False,
            "rationale": f"Provider state is {provider_state!r}; silent fallback to Codex is prohibited.",
        })
        return decision_record

    # 7. Second-Eye Policy (Codex implements candidate, AGY reviews/verifies)
    if policy == "second-eye":
        decision_record.update({
            "decision": "second-eye",
            "first_substantive_actor": "codex",
            "required_pre_steps": [
                "scope_privacy_approval", "disposable_worktree_setup",
                "direct_codex_implementation", "verification_planning", "post_implementation_review",
            ],
            "reason_code": "second-eye-override",
            "direct_codex_authorized": True,
            "rationale": "Second-eye policy active: Codex implements candidate, AGY reviews/verifies.",
        })
        return decision_record

    # 8. Delegation-First Policy Cycle Budget Evaluation
    assert policy == "delegation-first"

    if cycle_budget_exhausted:
        if prior_candidate_available:
            decision_record.update({
                "decision": "partially_verified",
                "first_substantive_actor": "none",
                "reason_code": "cycle-budget-exhausted",
                "direct_codex_authorized": False,
                "rationale": "Cycle budget exhausted with prior candidate; delivering current candidate outcome without silent fallback.",
            })
        else:
            decision_record.update({
                "decision": "blocked",
                "first_substantive_actor": "none",
                "reason_code": "no-candidate-exhausted",
                "direct_codex_authorized": False,
                "rationale": "Cycle budget exhausted with no candidate produced; execution is blocked without silent fallback.",
            })
        return decision_record

    # Happy path: delegate to AGY
    decision_record.update({
        "decision": "delegate-agy",
        "first_substantive_actor": "agy",
        "required_pre_steps": [
            "instruction_discovery", "scope_privacy_approval",
            "disposable_worktree_setup", "verification_planning",
        ],
        "reason_code": "delegation-first-active",
        "direct_codex_authorized": False,
        "rationale": "Delegation-first policy active: AGY is the first substantive repository actor.",
    })
    return decision_record


def main(argv: Sequence[str]) -> int:
    input_path: Path | None = None
    out_path: Path | None = None
    seen: set[str] = set()

    idx = 1
    # Check if first arg is 'eval' subcommand
    if len(argv) > 1 and argv[1] == "eval":
        idx = 2

    while idx < len(argv):
        arg = argv[idx]
        if arg == "--input" and idx + 1 < len(argv):
            if "input" in seen:
                sys.stderr.write("delegation-policy: duplicate input option\n")
                return 2
            seen.add("input")
            input_path = Path(argv[idx + 1])
            idx += 2
        elif arg.startswith("--input="):
            if "input" in seen:
                sys.stderr.write("delegation-policy: duplicate input option\n")
                return 2
            seen.add("input")
            input_path = Path(arg.partition("=")[2])
            idx += 1
        elif arg == "--out" and idx + 1 < len(argv):
            if "out" in seen:
                sys.stderr.write("delegation-policy: duplicate out option\n")
                return 2
            seen.add("out")
            out_path = Path(argv[idx + 1])
            idx += 2
        elif arg.startswith("--out="):
            if "out" in seen:
                sys.stderr.write("delegation-policy: duplicate out option\n")
                return 2
            seen.add("out")
            out_path = Path(arg.partition("=")[2])
            idx += 1
        else:
            sys.stderr.write(f"delegation-policy: rejected argument {arg}\n")
            return 2

    try:
        if input_path is not None:
            raw = input_path.read_text(encoding="utf-8")
        else:
            raw = sys.stdin.read()
        parsed = json.loads(raw)
        result = evaluate_policy(parsed)
        formatted = json.dumps(result, indent=2) + "\n"
        if out_path is not None:
            out_path.write_text(formatted, encoding="utf-8")
        else:
            sys.stdout.write(formatted)
        return 0
    except (DelegationPolicyError, json.JSONDecodeError, OSError) as exc:
        sys.stderr.write(f"delegation-policy error: {exc}\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
