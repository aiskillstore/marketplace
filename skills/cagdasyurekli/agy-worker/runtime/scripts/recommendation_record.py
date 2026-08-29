#!/usr/bin/env python3
"""Side-effect-free validation for recommendation-only record version 1."""

from __future__ import annotations

import re
from typing import Any


NAMED_TIERS = ("cheap", "bulk", "hard", "hardest")
PRE_DISPATCH_EVIDENCE = {
    "bounded-routine": (
        "cheap",
        "The driver classified the task as bounded and routine.",
    ),
    "batched-mechanical": (
        "bulk",
        "The driver identified a bounded batch of mechanical work.",
    ),
    "cross-file-bounded": (
        "hard",
        "The driver identified bounded cross-file reasoning with fixed acceptance criteria.",
    ),
    "high-complexity-bounded": (
        "hardest",
        "The driver identified a bounded high-complexity task with fixed acceptance criteria.",
    ),
}
POST_GATE_EVIDENCE = {
    "gate-accepted": (
        False,
        "The driver-owned gate accepted the independently observed repository state.",
        "Acceptance supplies no reason to recommend a more expensive tier.",
    ),
    "driver-verification-failed": (
        True,
        "A driver-authored verification command failed against the candidate.",
        "A bounded verification failure may benefit from one higher named tier.",
    ),
    "driver-quality-review-failed": (
        True,
        "Independent driver review found a bounded quality gap in the candidate.",
        "A bounded quality gap may benefit from one higher named tier.",
    ),
    "expected-edits-missing": (
        True,
        "The gate independently found no edits for a job that required edits.",
        "A bounded failure to produce the requested edit may benefit from one higher named tier.",
    ),
    "permission-failed": (
        False,
        "The driver classified the outcome as a permission failure.",
        "A model change cannot grant permission; resolve the permission boundary instead.",
    ),
    "authentication-failed": (
        False,
        "The driver classified the outcome as an authentication failure.",
        "A model change cannot authenticate the tool; resolve authentication instead.",
    ),
    "scope-policy-failed": (
        False,
        "The gate independently found a scope-policy violation.",
        "A stronger model must not be used to bypass the driver-owned scope policy.",
    ),
    "human-required": (
        False,
        "The gate routed the outcome to a human decision.",
        "A model change cannot supply authorization or make the required human decision.",
    ),
    "noncompleted-worker-outcome": (
        False,
        "The gate routed a partial, failed, or blocked worker outcome without accepting it.",
        "An untrusted noncompleted status is not driver-owned evidence that more model spend would help.",
    ),
    "untrusted-worker-claim": (
        False,
        "The gate rejected untrusted command or test claims from the worker envelope.",
        "A tier change does not turn worker claims into driver-owned evidence.",
    ),
    "invalid-envelope": (
        False,
        "The checked-in validator rejected the worker envelope contract.",
        "Repair the contract or prompt boundary without inferring that more model spend is justified.",
    ),
}

SAFE_LABEL = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:+/-]*\Z")
SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
VERSION_RE = re.compile(r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\Z")
REVISION_RE = re.compile(r"[0-9a-f]{40}\Z")
COMMON_FIELDS = {
    "schema_version",
    "kind",
    "stage",
    "recommendation_only",
    "applied",
    "decision",
    "recommended_tier",
    "rationale",
    "cost_impact",
    "evidence",
}
DIRECT_FIELDS = {
    "user_model",
    "resolved_agy_model",
    "matrix_sha256",
    "matrix_agy_version",
    "matrix_source_revision",
}


class RecommendationRecordError(ValueError):
    """A recommendation record is not internally valid version-1 evidence."""


def _fail(message: str) -> None:
    raise RecommendationRecordError(message)


def _string(value: Any, label: str, limit: int) -> str:
    if not isinstance(value, str) or not value or value.strip() != value:
        _fail(f"{label} must be one non-empty unpadded string")
    if len(value) > limit or any(ord(character) < 32 or ord(character) == 127 for character in value):
        _fail(f"{label} is invalid")
    return value


def _exact(value: dict[str, Any], expected: set[str]) -> None:
    if set(value) != expected:
        _fail("recommendation fields are invalid")


def _no_change(reason: str) -> tuple[str, None, str, dict[str, Any]]:
    return (
        "no-escalation",
        None,
        reason,
        {
            "direction": "none",
            "relative_tier_steps": 0,
            "summary": "No tier change is recommended; no incremental model cost is proposed.",
        },
    )


def _higher(selected: str, recommended: str, reason: str) -> tuple[str, str, str, dict[str, Any]]:
    steps = NAMED_TIERS.index(recommended) - NAMED_TIERS.index(selected)
    suffix = "s" if steps != 1 else ""
    return (
        "consider-higher-tier",
        recommended,
        reason,
        {
            "direction": "increase",
            "relative_tier_steps": steps,
            "summary": (
                f"The recommendation is {steps} named tier step{suffix} higher; "
                "exact provider cost is not inferred."
            ),
        },
    )


def _tier_expectation(stage: str, tier: str, code: str) -> tuple[str, str, tuple[Any, ...]]:
    if stage == "pre-dispatch":
        if code not in PRE_DISPATCH_EVIDENCE:
            _fail("pre-dispatch evidence code is invalid")
        target, description = PRE_DISPATCH_EVIDENCE[code]
        if tier not in NAMED_TIERS:
            expected = _no_change(
                "The selected tier is default or a custom model label, so its relative position cannot be inferred safely."
            )
        elif NAMED_TIERS.index(tier) >= NAMED_TIERS.index(target):
            expected = _no_change(
                f"The selected tier already meets or exceeds the driver-evidenced {target} task profile."
            )
        else:
            expected = _higher(
                tier,
                target,
                f"The driver-evidenced task profile maps to the named {target} tier.",
            )
        return code, description, expected

    if code not in POST_GATE_EVIDENCE:
        _fail("post-gate evidence code is invalid")
    escalatable, description, rationale = POST_GATE_EVIDENCE[code]
    if not escalatable:
        expected = _no_change(rationale)
    elif tier not in NAMED_TIERS:
        expected = _no_change(
            "The selected tier is default or a custom model label, so a higher tier cannot be inferred safely."
        )
    elif tier == NAMED_TIERS[-1]:
        expected = _no_change(
            "The caller already selected the highest named tier; no higher named tier exists."
        )
    else:
        expected = _higher(tier, NAMED_TIERS[NAMED_TIERS.index(tier) + 1], rationale)
    return code, description, expected


def validate_recommendation_record(value: Any, *, required_stage: str | None = None) -> dict[str, Any]:
    """Validate and return one exact side-effect-free v1 recommendation record."""

    if not isinstance(value, dict):
        _fail("recommendation must be one object")
    if type(value.get("schema_version")) is not int or value.get("schema_version") != 1:
        _fail("recommendation schema_version must be integer 1")
    if value.get("kind") != "model-tier-recommendation":
        _fail("recommendation kind is invalid")
    stage = value.get("stage")
    if stage not in ("pre-dispatch", "post-gate") or (
        required_stage is not None and stage != required_stage
    ):
        _fail("recommendation stage is invalid")
    if value.get("recommendation_only") is not True or value.get("applied") is not False:
        _fail("recommendation must remain advisory and unapplied")

    has_tier = "selected_tier" in value
    has_model = "user_model" in value
    if has_tier == has_model:
        _fail("recommendation must contain exactly one selection mode")
    if has_tier:
        _exact(value, COMMON_FIELDS | {"selected_tier"})
        selected = _string(value["selected_tier"], "selected tier", 128)
        if SAFE_LABEL.fullmatch(selected) is None:
            _fail("selected tier is invalid")
    else:
        fields = COMMON_FIELDS | DIRECT_FIELDS
        if "user_effort" in value:
            fields |= {"user_effort"}
        _exact(value, fields)
        selected = _string(value["resolved_agy_model"], "resolved model", 128)
        for key in ("user_model", "resolved_agy_model"):
            if SAFE_LABEL.fullmatch(_string(value[key], key.replace("_", " "), 128)) is None:
                _fail(f"{key.replace('_', ' ')} is invalid")
        if "user_effort" in value and value["user_effort"] not in ("low", "medium", "high"):
            _fail("user effort is invalid")
        if "user_effort" not in value and value["resolved_agy_model"] != value["user_model"]:
            _fail("exact model recommendation resolution is inconsistent")
        if SHA256_RE.fullmatch(_string(value["matrix_sha256"], "matrix SHA-256", 64)) is None:
            _fail("matrix SHA-256 is invalid")
        if VERSION_RE.fullmatch(_string(value["matrix_agy_version"], "matrix version", 32)) is None:
            _fail("matrix version is invalid")
        if REVISION_RE.fullmatch(_string(value["matrix_source_revision"], "matrix revision", 40)) is None:
            _fail("matrix revision is invalid")

    evidence = value.get("evidence")
    if not isinstance(evidence, dict) or set(evidence) != {"owner", "code", "description"}:
        _fail("recommendation evidence is invalid")
    if evidence.get("owner") != "driver":
        _fail("recommendation evidence owner is invalid")
    code = _string(evidence.get("code"), "evidence code", 64)
    expected_code, expected_description, expected = _tier_expectation(stage, selected, code)
    if evidence != {
        "owner": "driver",
        "code": expected_code,
        "description": expected_description,
    }:
        _fail("recommendation evidence differs from v1 policy")
    if not has_tier:
        expected = _no_change(
            "An explicit model/effort selection is caller-owned and unranked; this advisory cannot change or redispatch it."
        )
    actual = (
        value.get("decision"),
        value.get("recommended_tier"),
        value.get("rationale"),
        value.get("cost_impact"),
    )
    if actual != expected:
        _fail("recommendation decision differs from v1 policy")
    return value
