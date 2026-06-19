from __future__ import annotations

import hashlib
from typing import Any


SCRIPT_INTERFACE = "internal-module"
SCRIPT_INTERFACE_REASON = "Imported by render_daily_skillops_report.py to score SkillOps opportunities without writing files."

ACTION_POLICY: dict[str, dict[str, str]] = {
    "language_default": {
        "action_type": "patch_existing_skill",
        "opportunity_type": "report-experience",
        "reason": "Repeated language preferences can improve existing report templates after approval.",
    },
    "report_ui": {
        "action_type": "patch_existing_skill",
        "opportunity_type": "artifact-quality",
        "reason": "Repeated report layout feedback maps to existing renderer and design doctrine changes.",
    },
    "approval_safety": {
        "action_type": "agents_update",
        "opportunity_type": "governance",
        "reason": "Repeated privacy and approval signals should tighten durable operating guidance.",
    },
    "delivery_format": {
        "action_type": "patch_existing_skill",
        "opportunity_type": "artifact-discoverability",
        "reason": "Repeated delivery-path requests can improve CLI and README artifact discoverability.",
    },
    "evidence_testing": {
        "action_type": "add_eval",
        "opportunity_type": "quality-gate",
        "reason": "Repeated verification and evidence requests should become focused checks.",
    },
}

RISK_PENALTY = {
    "low": 0,
    "medium": 8,
    "high": 18,
}


def _stable_id(pattern_id: str, target_files: list[str], title: str) -> str:
    digest = hashlib.sha1(f"{pattern_id}:{title}:{','.join(target_files)}".encode("utf-8")).hexdigest()
    return f"skillops-{digest[:10]}"


def _as_int(value: Any, default: int = 0) -> int:
    if isinstance(value, bool):
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _risk_level(proposal: dict[str, Any]) -> str:
    risk = str(proposal.get("risk_level") or "medium").lower()
    return risk if risk in RISK_PENALTY else "medium"


def _target_files(proposal: dict[str, Any]) -> list[str]:
    files = proposal.get("target_files")
    if not isinstance(files, list):
        return []
    return [str(item) for item in files if str(item).strip()]


def _verification_commands(proposal: dict[str, Any]) -> list[str]:
    commands = proposal.get("verification_commands")
    if not isinstance(commands, list):
        return []
    return [str(item) for item in commands if str(item).strip()]


def _score(pattern: dict[str, Any], proposal: dict[str, Any]) -> tuple[int, list[str]]:
    support = _as_int(pattern.get("support_count"), _as_int(proposal.get("support_count"), 0))
    confidence = pattern.get("confidence", 0.5)
    try:
        confidence_score = int(float(confidence) * 25)
    except (TypeError, ValueError):
        confidence_score = 12
    target_files = _target_files(proposal)
    verification_commands = _verification_commands(proposal)
    risk = _risk_level(proposal)
    reasons = [
        f"support_count={support}",
        f"confidence={confidence}",
        f"risk={risk}",
    ]
    score = 28
    score += min(30, support * 10)
    score += max(0, min(25, confidence_score))
    if target_files:
        score += 8
        reasons.append("target_files_present")
    else:
        reasons.append("target_files_missing")
    if verification_commands:
        score += 7
        reasons.append("verification_present")
    else:
        reasons.append("verification_missing")
    score -= RISK_PENALTY[risk]
    if proposal.get("requires_approval") is True:
        reasons.append("approval_required")
    return max(0, min(100, score)), reasons


def _decision(score: int, proposal: dict[str, Any]) -> str:
    if score >= 85:
        return "ready_for_approval_review"
    if score >= 70:
        return "proposal_review"
    if score >= 50:
        return "observe_more_evidence"
    if proposal.get("requires_approval") is True:
        return "report_only"
    return "no_action"


def _priority(score: int, risk: str) -> str:
    if score >= 85 and risk == "low":
        return "high"
    if score >= 70:
        return "medium"
    return "low"


def build_opportunities(patterns: list[dict[str, Any]], proposals: list[dict[str, Any]]) -> list[dict[str, Any]]:
    pattern_by_id = {str(item.get("pattern_id", "")): item for item in patterns if isinstance(item, dict)}
    opportunities: list[dict[str, Any]] = []
    for proposal in proposals:
        if not isinstance(proposal, dict):
            continue
        pattern_id = str(proposal.get("pattern_id") or "generic")
        pattern = pattern_by_id.get(pattern_id, {})
        policy = ACTION_POLICY.get(
            pattern_id,
            {
                "action_type": "report_only",
                "opportunity_type": "manual-review",
                "reason": "Unknown pattern family requires manual review before any durable change.",
            },
        )
        target_files = _target_files(proposal)
        verification_commands = _verification_commands(proposal)
        risk = _risk_level(proposal)
        score, score_reasons = _score(pattern, proposal)
        evidence_refs = proposal.get("evidence_refs")
        if not isinstance(evidence_refs, list):
            evidence_refs = []
        opportunities.append(
            {
                "opportunity_id": _stable_id(pattern_id, target_files, str(proposal.get("title") or "")),
                "proposal_id": proposal.get("proposal_id", ""),
                "pattern_id": pattern_id,
                "title": proposal.get("title", ""),
                "opportunity_type": policy["opportunity_type"],
                "action_type": policy["action_type"],
                "decision": _decision(score, proposal),
                "priority": _priority(score, risk),
                "score": score,
                "score_reasons": score_reasons,
                "policy_reason": policy["reason"],
                "risk_level": risk,
                "requires_approval": proposal.get("requires_approval") is True,
                "write_allowed_without_approval": False,
                "evidence_count": len(evidence_refs) or _as_int(pattern.get("support_count"), 0),
                "target_files": target_files,
                "verification_commands": verification_commands,
            }
        )
    opportunities.sort(key=lambda item: (-int(item["score"]), str(item["opportunity_id"])))
    return opportunities


def summarize_opportunities(opportunities: list[dict[str, Any]]) -> dict[str, Any]:
    by_action: dict[str, int] = {}
    by_decision: dict[str, int] = {}
    for item in opportunities:
        by_action[str(item.get("action_type", ""))] = by_action.get(str(item.get("action_type", "")), 0) + 1
        by_decision[str(item.get("decision", ""))] = by_decision.get(str(item.get("decision", "")), 0) + 1
    top_score = int(opportunities[0]["score"]) if opportunities else 0
    return {
        "opportunity_count": len(opportunities),
        "top_score": top_score,
        "ready_for_approval_review_count": by_decision.get("ready_for_approval_review", 0),
        "proposal_review_count": by_decision.get("proposal_review", 0),
        "observe_more_evidence_count": by_decision.get("observe_more_evidence", 0),
        "report_only_count": by_decision.get("report_only", 0),
        "action_type_counts": by_action,
        "decision_counts": by_decision,
    }


def decision_policy_contract() -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "contract": "skillops-opportunity-scoring",
        "score_range": [0, 100],
        "score_bands": {
            "85-100": "ready_for_approval_review",
            "70-84": "proposal_review",
            "50-69": "observe_more_evidence",
            "0-49": "report_only_or_no_action",
        },
        "action_types": sorted({item["action_type"] for item in ACTION_POLICY.values()} | {"report_only"}),
        "writes_source_files": False,
        "auto_patch_enabled": False,
        "approval_required_for_writes": True,
    }
