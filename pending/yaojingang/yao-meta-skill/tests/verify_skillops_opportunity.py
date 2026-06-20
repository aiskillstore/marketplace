#!/usr/bin/env python3
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from skillops_opportunity import build_opportunities, decision_policy_contract, summarize_opportunities


def main() -> None:
    patterns = [
        {
            "pattern_id": "evidence_testing",
            "support_count": 4,
            "confidence": 0.95,
            "evidence": [{"record_id": "a"}, {"record_id": "b"}, {"record_id": "c"}],
        },
        {
            "pattern_id": "approval_safety",
            "support_count": 2,
            "confidence": 0.79,
            "evidence": [{"record_id": "d"}, {"record_id": "e"}],
        },
        {
            "pattern_id": "unknown_manual",
            "support_count": 1,
            "confidence": 0.55,
            "evidence": [{"record_id": "f"}],
        },
    ]
    proposals = [
        {
            "proposal_id": "adapt-high",
            "pattern_id": "evidence_testing",
            "title": "Attach tests and evidence refresh to each upgrade",
            "risk_level": "medium",
            "requires_approval": True,
            "target_files": ["tests/verify_adaptation_safety.py"],
            "verification_commands": ["python3 tests/verify_adaptation_safety.py"],
            "evidence_refs": [{"record_id": "a"}, {"record_id": "b"}, {"record_id": "c"}],
        },
        {
            "proposal_id": "adapt-approval",
            "pattern_id": "approval_safety",
            "title": "Keep adaptive iteration approval-gated",
            "risk_level": "low",
            "requires_approval": True,
            "target_files": ["AGENTS.md"],
            "verification_commands": ["python3 tests/verify_adaptation_safety.py"],
            "evidence_refs": [{"record_id": "d"}, {"record_id": "e"}],
        },
        {
            "proposal_id": "adapt-unknown",
            "pattern_id": "unknown_manual",
            "title": "Review repeated preference pattern",
            "risk_level": "high",
            "requires_approval": True,
            "target_files": [],
            "verification_commands": [],
            "evidence_refs": [{"record_id": "f"}],
        },
    ]
    opportunities = build_opportunities(patterns, proposals)
    assert len(opportunities) == 3, opportunities
    assert opportunities[0]["score"] >= opportunities[1]["score"] >= opportunities[2]["score"], opportunities
    by_pattern = {item["pattern_id"]: item for item in opportunities}
    assert by_pattern["evidence_testing"]["action_type"] == "add_eval", by_pattern["evidence_testing"]
    assert by_pattern["evidence_testing"]["decision"] in {"ready_for_approval_review", "proposal_review"}, by_pattern[
        "evidence_testing"
    ]
    assert by_pattern["approval_safety"]["action_type"] == "agents_update", by_pattern["approval_safety"]
    assert by_pattern["unknown_manual"]["action_type"] == "report_only", by_pattern["unknown_manual"]
    assert by_pattern["unknown_manual"]["score"] < by_pattern["evidence_testing"]["score"], by_pattern
    assert all(item["write_allowed_without_approval"] is False for item in opportunities), opportunities
    assert all(0 <= item["score"] <= 100 for item in opportunities), opportunities
    summary = summarize_opportunities(opportunities)
    assert summary["opportunity_count"] == 3, summary
    assert summary["action_type_counts"]["add_eval"] == 1, summary
    assert summary["action_type_counts"]["agents_update"] == 1, summary
    assert summary["action_type_counts"]["report_only"] == 1, summary
    assert summary["top_score"] == opportunities[0]["score"], summary
    contract = decision_policy_contract()
    assert contract["writes_source_files"] is False, contract
    assert contract["auto_patch_enabled"] is False, contract
    assert contract["approval_required_for_writes"] is True, contract
    assert contract["score_range"] == [0, 100], contract
    schema = json.loads((ROOT / "schemas" / "skillops-opportunity.schema.json").read_text(encoding="utf-8"))
    assert "score" in schema["properties"], schema
    print(json.dumps({"ok": True}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
