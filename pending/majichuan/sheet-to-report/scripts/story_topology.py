from __future__ import annotations

from typing import Any


ALLOWED_STORY_ROLES = frozenset({
    "cover",
    "executive_summary",
    "baseline",
    "driver",
    "opportunity",
    "risk",
    "decision",
    "action",
    "appendix",
})

# This order only gives newly planned pages a deterministic default order.
# Validation below deliberately accepts every ordering that satisfies its edges.
CANONICAL_STORY_ROLE_ORDER = {
    "cover": 0,
    "executive_summary": 1,
    "baseline": 2,
    "driver": 3,
    "opportunity": 4,
    "risk": 5,
    "decision": 6,
    "action": 7,
    "appendix": 8,
}


def canonical_story_sort_key(page: dict[str, Any]) -> int:
    """Return the deterministic construction order for a planned page."""

    return CANONICAL_STORY_ROLE_ORDER[str(page["story_role"])]


def management_finding_sort_key(finding: dict[str, Any]) -> tuple[int, int, int, str]:
    """Order selected findings for a transactional management presentation.

    This remains separate from value-selection scoring: the selected portfolio
    stays locked in score order while its audience-facing story starts with
    outcomes and drivers and keeps data quality visible as a risk.
    """

    lens = str(finding.get("lens") or "").lower()
    signal = str(finding.get("signal_type") or "").lower()
    if lens in {"overview", "outcome", "result", "growth_driver"}:
        portfolio_rank = 0
    elif lens == "seasonality" or signal == "seasonality":
        portfolio_rank = 1
    elif signal == "opportunity":
        portfolio_rank = 2
    elif lens in {"geography", "product", "customer", "concentration"}:
        portfolio_rank = 3
    elif lens == "trend":
        portfolio_rank = 4
    elif lens == "quality":
        portfolio_rank = 6
    else:
        portfolio_rank = 5
    return (
        portfolio_rank,
        -int(finding.get("score") or 0),
        int(finding.get("source_index") or 0),
        str(finding.get("insight_id") or ""),
    )


def management_presentation_order(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return a stable presentation-only copy without mutating selection."""

    return sorted(list(findings), key=management_finding_sort_key)


def story_topology_is_valid(pages: list[dict[str, Any]]) -> bool:
    """Return the same dependency-edge verdict used by final model validation."""

    return _topology_violation(pages) is None


def validate_story_topology(pages: list[dict[str, Any]]) -> None:
    """Reject only violated story dependency edges, never independent role swaps."""

    violation = _topology_violation(pages)
    if violation:
        raise ValueError(f"story_plan_invalid: {violation}")


def _topology_violation(pages: list[dict[str, Any]]) -> str | None:
    roles = [str(page.get("story_role") or "") for page in pages]
    if not roles or any(role not in ALLOWED_STORY_ROLES for role in roles):
        return "story_role 无效"
    if roles[0] != "cover":
        return "cover 必须最先"

    appendix_indexes = [index for index, role in enumerate(roles) if role == "appendix"]
    if appendix_indexes and appendix_indexes[0] != len(roles) - len(appendix_indexes):
        return "appendix 必须位于所有主报告页之后"

    main_roles = [role for role in roles if role != "appendix"]
    if not main_roles or main_roles[-1] not in {"action", "decision"}:
        return "action 或 decision 必须是最后主报告页"

    summary_indexes = [
        index for index, role in enumerate(roles) if role == "executive_summary"
    ]
    evidence_indexes = [
        index
        for index, page in enumerate(pages)
        if roles[index] not in {"cover", "executive_summary", "appendix"}
        and bool(page.get("evidence_ids"))
    ]
    if summary_indexes and evidence_indexes and max(summary_indexes) >= min(evidence_indexes):
        return "executive_summary 必须位于证据页之前"
    return None
