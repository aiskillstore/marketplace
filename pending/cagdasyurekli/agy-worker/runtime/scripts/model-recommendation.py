#!/usr/bin/env python3
"""Render a driver-evidence-based, recommendation-only model-tier decision."""

import argparse
import json
import re
import sys

sys.dont_write_bytecode = True

from model_selection import CallerError, EvidenceUnavailable, ReviewRequired, resolve_selection
from recommendation_record import (
    NAMED_TIERS,
    POST_GATE_EVIDENCE,
    PRE_DISPATCH_EVIDENCE,
    RecommendationRecordError,
    validate_recommendation_record,
)

SAFE_TIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:+/-]*\Z")


class UsageErrorParser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        self.exit(64, f"model-recommendation: {message}\n")


def one(parser, values, flag):
    if not values:
        parser.error(f"{flag} is required")
    if len(values) != 1:
        parser.error(f"{flag} must be provided exactly once")
    return values[0]


def no_change(reason):
    return {
        "decision": "no-escalation",
        "recommended_tier": None,
        "rationale": reason,
        "cost_impact": {
            "direction": "none",
            "relative_tier_steps": 0,
            "summary": "No tier change is recommended; no incremental model cost is proposed.",
        },
    }


def higher_tier(selected_tier, recommended_tier, reason):
    selected_index = NAMED_TIERS.index(selected_tier)
    recommended_index = NAMED_TIERS.index(recommended_tier)
    steps = recommended_index - selected_index
    return {
        "decision": "consider-higher-tier",
        "recommended_tier": recommended_tier,
        "rationale": reason,
        "cost_impact": {
            "direction": "increase",
            "relative_tier_steps": steps,
            "summary": (
                f"The recommendation is {steps} named tier step"
                f"{'s' if steps != 1 else ''} higher; exact provider cost is not inferred."
            ),
        },
    }


def pre_dispatch(selected_tier, evidence_code):
    target_tier, evidence_description = PRE_DISPATCH_EVIDENCE[evidence_code]
    if selected_tier not in NAMED_TIERS:
        decision = no_change(
            "The selected tier is default or a custom model label, so its relative position cannot be inferred safely."
        )
    elif NAMED_TIERS.index(selected_tier) >= NAMED_TIERS.index(target_tier):
        decision = no_change(
            f"The selected tier already meets or exceeds the driver-evidenced {target_tier} task profile."
        )
    else:
        decision = higher_tier(
            selected_tier,
            target_tier,
            f"The driver-evidenced task profile maps to the named {target_tier} tier.",
        )
    return evidence_description, decision


def post_gate(selected_tier, evidence_code):
    escalatable, evidence_description, rationale = POST_GATE_EVIDENCE[evidence_code]
    if not escalatable:
        return evidence_description, no_change(rationale)
    if selected_tier not in NAMED_TIERS:
        return evidence_description, no_change(
            "The selected tier is default or a custom model label, so a higher tier cannot be inferred safely."
        )
    selected_index = NAMED_TIERS.index(selected_tier)
    if selected_index == len(NAMED_TIERS) - 1:
        return evidence_description, no_change(
            "The caller already selected the highest named tier; no higher named tier exists."
        )
    return evidence_description, higher_tier(
        selected_tier,
        NAMED_TIERS[selected_index + 1],
        rationale,
    )


def main(argv=None):
    parser = UsageErrorParser(
        prog="model-recommendation.sh",
        description="Print a recommendation-only model-tier decision as JSON.",
    )
    parser.add_argument(
        "--stage",
        action="append",
        choices=("pre-dispatch", "post-gate"),
        help="recommendation point",
    )
    parser.add_argument(
        "--selected-tier",
        action="append",
        metavar="TIER",
        help="the caller-selected named tier, default, or explicit model label",
    )
    parser.add_argument(
        "--selected-model",
        action="append",
        metavar="MODEL",
        help="one explicit reviewed model or adjustable base model",
    )
    parser.add_argument(
        "--selected-effort",
        action="append",
        metavar="EFFORT",
        help="explicit effort paired with --selected-model",
    )
    parser.add_argument(
        "--evidence",
        action="append",
        metavar="CODE",
        help="one controlled driver-owned evidence code",
    )
    args = parser.parse_args(argv)

    stage = one(parser, args.stage, "--stage")
    selected_tier = args.selected_tier
    selected_model = args.selected_model
    selected_effort = args.selected_effort
    if bool(selected_tier) == bool(selected_model):
        parser.error("exactly one of --selected-tier or --selected-model is required")
    if selected_tier:
        selected_tier_value = one(parser, selected_tier, "--selected-tier")
        if selected_effort:
            parser.error("--selected-effort requires --selected-model")
        selection = None
    else:
        selected_tier_value = ""
        model_value = one(parser, selected_model, "--selected-model")
        effort_value = None
        if selected_effort:
            effort_value = one(parser, selected_effort, "--selected-effort")
        try:
            selection = resolve_selection(
                model_value, effort_value, "cli", "cli" if effort_value else None,
                probe_version=False,
            )
        except CallerError as exc:
            parser.error(str(exc))
        except ReviewRequired as exc:
            parser.error(f"compatibility review required: {exc}")
        except EvidenceUnavailable as exc:
            parser.error(f"compatibility evidence unavailable: {exc}")
    evidence_code = one(parser, args.evidence, "--evidence")

    if selection is None and not SAFE_TIER.fullmatch(selected_tier_value):
        parser.error("--selected-tier must be a non-empty tier or model label without whitespace")

    evidence_set = PRE_DISPATCH_EVIDENCE if stage == "pre-dispatch" else POST_GATE_EVIDENCE
    if evidence_code not in evidence_set:
        allowed = ", ".join(sorted(evidence_set))
        parser.error(f"--evidence is not valid for {stage}; choose one of: {allowed}")

    ranking_input = selected_tier_value if selection is None else selection["resolved_agy_model"]
    if stage == "pre-dispatch":
        evidence_description, decision = pre_dispatch(ranking_input, evidence_code)
    else:
        evidence_description, decision = post_gate(ranking_input, evidence_code)

    if selection is not None:
        decision = no_change(
            "An explicit model/effort selection is caller-owned and unranked; this advisory cannot change or redispatch it."
        )

    result = {
        "schema_version": 1,
        "kind": "model-tier-recommendation",
        "stage": stage,
        "recommendation_only": True,
        "applied": False,
        **decision,
        "evidence": {
            "owner": "driver",
            "code": evidence_code,
            "description": evidence_description,
        },
    }
    if selection is None:
        result["selected_tier"] = selected_tier_value
    else:
        result["user_model"] = selection["user_model"]
        if "user_effort" in selection:
            result["user_effort"] = selection["user_effort"]
        result["resolved_agy_model"] = selection["resolved_agy_model"]
        result["matrix_sha256"] = selection["matrix_sha256"]
        result["matrix_agy_version"] = selection["matrix_agy_version"]
        result["matrix_source_revision"] = selection["matrix_source_revision"]
    try:
        validate_recommendation_record(result)
    except RecommendationRecordError as exc:
        parser.error(f"internal recommendation record validation failed: {exc}")
    json.dump(result, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
