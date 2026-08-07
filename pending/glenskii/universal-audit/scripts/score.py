#!/usr/bin/env python3
# =============================================================================
# score.py - Deterministic scoring engine for the Universal Software
# Engineering Audit Specification v2.2 (Sections 13, 14, Appendix A.0).
#
# Usage:
#   python score.py selected-controls.json --profile P4 --tier standard \
#       --out score-sheet.json
#
# Input: selected-controls.json - see references/schemas/selected-controls.schema.json
# Output: score-sheet.json plus a human-readable console summary.
#
# This script is the single source of scoring arithmetic for an audit.
# It never decides the final verdict alone: qualitative gates (critical-workflow
# verification, interim-control ownership) remain the auditor's responsibility.
# =============================================================================

import argparse
import json
import sys

SPEC_VERSION = "2.2"
SCHEMA_VERSION = "1.0"

# -----------------------------------------------------------------------------
# Section 13.1 - Base category weights (percent)
# -----------------------------------------------------------------------------
CATEGORIES = {
    "security_privacy":        {"label": "Security and privacy",                  "weight": 20},
    "reliability_operations":  {"label": "Reliability, recovery, and operations", "weight": 18},
    "architecture_data":       {"label": "Architecture and data integrity",       "weight": 14},
    "quality_correctness":     {"label": "Quality engineering and correctness",   "weight": 12},
    "deployment_supply_chain": {"label": "Deployment and supply chain",           "weight": 10},
    "maintainability_docs":    {"label": "Maintainability and documentation",     "weight": 8},
    "performance_cost":        {"label": "Performance, capacity, and cost",       "weight": 7},
    "ux_product_fitness":      {"label": "UX and product fitness",                "weight": 6},
    "accessibility":           {"label": "Accessibility",                         "weight": 5},
}

# -----------------------------------------------------------------------------
# Section 13.0 - Risk profiles and their critical categories
# -----------------------------------------------------------------------------
PROFILES = {
    "P1": ["security_privacy", "reliability_operations", "ux_product_fitness", "accessibility"],
    "P2": ["security_privacy", "architecture_data", "quality_correctness", "reliability_operations"],
    "P3": ["security_privacy", "architecture_data", "reliability_operations", "deployment_supply_chain"],
    "P4": ["quality_correctness", "architecture_data", "deployment_supply_chain", "reliability_operations"],
    "P5": ["security_privacy", "reliability_operations", "architecture_data", "performance_cost"],
    "P6": ["security_privacy", "quality_correctness", "architecture_data", "reliability_operations"],
}

# -----------------------------------------------------------------------------
# Section 13.4 - Points per control result. Key: (status, severity_or_None)
# -----------------------------------------------------------------------------
POINTS = {
    ("PASS", None): 10,
    ("NOTE", None): 9,
    ("WARN", "Low"): 8,
    ("WARN", "Medium"): 6,
    ("WARN", "High"): 4,
    ("FAIL", "Low"): 5,
    ("FAIL", "Medium"): 3,
    ("FAIL", "High"): 1,
    ("FAIL", "Critical"): 0,
}

CRIT_WEIGHT = {"C1": 1, "C2": 2, "C3": 3}

# -----------------------------------------------------------------------------
# Appendix A.0 - Control-to-category mapping.
# Named exceptions first, then prefix rules (order matters).
# Gate controls score in no category.
# -----------------------------------------------------------------------------
GATE_CONTROLS = {"GOV-SCOPE-001", "GOV-ROE-001"}

EXCEPTION_MAP = {
    "GOV-THREAT-001": "security_privacy",
    "GOV-RISK-001": "reliability_operations",
    "GOV-REQ-001": "ux_product_fitness",
    "GOV-TRACE-001": "ux_product_fitness",
    "ARC-CPLX-001": "maintainability_docs",
    "INF-IAM-001": "security_privacy",
    "INF-NET-001": "security_privacy",
    "INF-TLS-001": "security_privacy",
    "INF-ENV-001": "security_privacy",
    "INF-IAC-001": "deployment_supply_chain",
    "INF-PATCH-001": "deployment_supply_chain",
    "DESK-LOCAL-001": "security_privacy",
    "DESK-INSTALL-001": "deployment_supply_chain",
    "DESK-UPDATE-001": "deployment_supply_chain",
    "MOB-PERM-001": "security_privacy",
    "MOB-LIFE-001": "quality_correctness",
    "MOD-BOUND-001": "security_privacy",
    "MOD-INJECT-001": "security_privacy",
    "MOD-DATA-001": "security_privacy",
    "MOD-EVAL-001": "quality_correctness",
    "MOD-FAIL-001": "reliability_operations",
}

PREFIX_MAP = [
    ("SEC-", "security_privacy"),
    ("PRIV-", "security_privacy"),
    ("ADM-", "security_privacy"),
    ("RET-", "security_privacy"),
    ("REL-", "reliability_operations"),
    ("OPS-", "reliability_operations"),
    ("BAK-", "reliability_operations"),
    ("DR-", "reliability_operations"),
    ("ARC-", "architecture_data"),
    ("DATA-", "architecture_data"),
    ("CODE-", "quality_correctness"),
    ("QA-", "quality_correctness"),
    ("SUP-", "deployment_supply_chain"),
    ("CICD-", "deployment_supply_chain"),
    ("DOC-", "maintainability_docs"),
    ("PERF-", "performance_cost"),
    ("COST-", "performance_cost"),
    ("UX-", "ux_product_fitness"),
    ("I18N-", "ux_product_fitness"),
    ("A11Y-", "accessibility"),
]

VALID_STATUSES = {"PASS", "FAIL", "WARN", "NOTE", "UNVERIFIED", "NOT_APPLICABLE"}
COVERED_STATUSES = {"PASS", "FAIL", "WARN", "NOTE"}


def map_category(control):
    """Resolve a control's scoring category per spec A.0."""
    cid = control["control_id"]
    if cid in GATE_CONTROLS:
        return None
    if control.get("category"):
        return control["category"]
    if cid in EXCEPTION_MAP:
        return EXCEPTION_MAP[cid]
    for prefix, cat in PREFIX_MAP:
        if cid.startswith(prefix):
            return cat
    raise ValueError(
        f"{cid}: no category assignment. Spec A.0 requires every scored control "
        f"to map to exactly one category. Add an explicit 'category' field."
    )


def control_points(control):
    """Points per spec 13.4. WARN may not be Critical."""
    status = control["status"]
    if status in ("PASS", "NOTE"):
        return POINTS[(status, None)]
    severity = control.get("severity")
    if status == "WARN" and severity == "Critical":
        raise ValueError(
            f"{control['control_id']}: WARN may not carry Critical severity "
            f"(spec 13.4) - a credible Critical impact is a FAIL by definition."
        )
    key = (status, severity)
    if key not in POINTS:
        raise ValueError(
            f"{control['control_id']}: {status} requires a severity of "
            f"Low/Medium/High" + ("/Critical" if status == "FAIL" else "")
        )
    return POINTS[key]


def score_category(controls, systemic_flags):
    """Score one category: weighted mean, caps, coverage. Spec 13.3–13.4."""
    applicable = [c for c in controls if c["status"] != "NOT_APPLICABLE"]
    covered = [c for c in applicable if c["status"] in COVERED_STATUSES]
    coverage = (len(covered) / len(applicable) * 100) if applicable else None

    num = den = 0
    for c in covered:
        w = CRIT_WEIGHT[c.get("criticality", "C2")]
        num += control_points(c) * w
        den += w
    provisional = (num / den) if den else None

    caps, capped = [], provisional
    def apply_cap(value, reason):
        nonlocal capped
        if capped is not None and capped > value:
            capped = value
        caps.append(reason)

    if any(c["status"] == "FAIL" and c.get("severity") == "Critical" for c in covered):
        apply_cap(2.9, "Unresolved Critical FAIL caps category at 2.9")
    if any(c["status"] == "FAIL" and c.get("severity") == "High" for c in covered):
        apply_cap(4.9, "Unresolved High FAIL caps category at 4.9")
    if systemic_flags:
        apply_cap(6.9, "Verified systemic risk (spec 13.5) caps category at 6.9")
    if any(c["status"] == "FAIL" and c.get("criticality") == "C3" for c in covered):
        apply_cap(6.9, "C3 control failure caps category at 6.9")
    if coverage is not None and coverage < 70 and capped is not None:
        apply_cap(7.9, "Coverage below 70% caps category at 7.9 for release decisions")

    return {
        "provisional_score": round(provisional, 1) if provisional is not None else None,
        "score": round(capped, 1) if capped is not None else None,
        "caps_applied": caps,
        "coverage_pct": round(coverage, 1) if coverage is not None else None,
        "insufficient_evidence": coverage is not None and coverage < 50,
        "counts": {s: sum(1 for c in applicable if c["status"] == s)
                   for s in ("PASS", "FAIL", "WARN", "NOTE", "UNVERIFIED")},
        "applicable_controls": len(applicable),
    }


def evaluate_gates(cat_results, overall_coverage, critical_categories, all_controls):
    """Release-gate preconditions the script can verify mechanically (spec 14)."""
    fails = [c for c in all_controls
             if c["status"] == "FAIL" and c.get("severity") in ("Critical", "High")]
    critical_open = [c["control_id"] for c in fails if c["severity"] == "Critical"]
    high_open = [c["control_id"] for c in fails if c["severity"] == "High"]

    low_critical_cov = [
        k for k in critical_categories
        if cat_results.get(k, {}).get("coverage_pct") is not None
        and cat_results[k]["coverage_pct"] < 80
    ]
    blockers = []
    if critical_open:
        blockers.append(f"Unresolved Critical FAIL: {', '.join(critical_open)}")
    if high_open:
        blockers.append(f"Unresolved High FAIL: {', '.join(high_open)}")
    if overall_coverage is not None and overall_coverage < 85:
        blockers.append(f"Overall coverage {overall_coverage:.1f}% is below the 85% approval gate")
    if low_critical_cov:
        blockers.append(f"Critical categories below 80% coverage: {', '.join(low_critical_cov)}")

    if critical_open:
        recommendation = "DO_NOT_SHIP"
    elif high_open:
        recommendation = "REQUIRES_REWORK"
    elif blockers:
        recommendation = "APPROVED_WITH_CONDITIONS_AT_BEST"
    else:
        recommendation = "APPROVED_ELIGIBLE"
    return {"mechanical_blockers": blockers, "gate_recommendation": recommendation,
            "note": ("Qualitative gates (critical-workflow verification, ownership of "
                     "remaining work, interim controls) must still be confirmed by the "
                     "auditor before selecting the final verdict.")}


def main():
    ap = argparse.ArgumentParser(description="Universal Audit deterministic scorer (spec v2.2)")
    ap.add_argument("controls_file", help="Path to selected-controls.json")
    ap.add_argument("--profile", choices=sorted(PROFILES), required=True)
    ap.add_argument("--tier", choices=["rapid", "standard", "deep"], required=True)
    ap.add_argument("--weights", help="Optional JSON file with adjusted category weights "
                                      "(each within ±5 of base, sum 100)")
    ap.add_argument("--out", help="Write score-sheet.json to this path")
    args = ap.parse_args()

    with open(args.controls_file, encoding="utf-8") as f:
        data = json.load(f)
    controls = data["controls"]

    # ---- Validation --------------------------------------------------------
    for c in controls:
        if c["status"] not in VALID_STATUSES:
            sys.exit(f"ERROR: {c['control_id']}: invalid status '{c['status']}'")
        if c["status"] == "NOT_APPLICABLE" and not c.get("na_justification"):
            sys.exit(f"ERROR: {c['control_id']}: NOT_APPLICABLE requires na_justification")

    # ---- Weights (base or adjusted within profile limits) ------------------
    weights = {k: v["weight"] for k, v in CATEGORIES.items()}
    if args.weights:
        with open(args.weights, encoding="utf-8") as f:
            adjusted = json.load(f)
        for k, v in adjusted.items():
            if k not in weights:
                sys.exit(f"ERROR: unknown category in weights file: {k}")
            if abs(v - weights[k]) > 5:
                sys.exit(f"ERROR: {k}: adjustment exceeds ±5 percentage points (spec 13.0)")
        if round(sum(adjusted.values()), 6) != 100:
            sys.exit("ERROR: adjusted weights must sum to 100")
        weights = adjusted

    # ---- Categorize --------------------------------------------------------
    by_cat = {k: [] for k in CATEGORIES}
    gates = []
    try:
        for c in controls:
            cat = map_category(c)
            (gates if cat is None else by_cat[cat]).append(c)
    except (ValueError, KeyError) as e:
        sys.exit(f"ERROR: {e}")

    systemic = set(data.get("systemic_risk_categories", []))
    cat_results = {}
    try:
        for k, items in by_cat.items():
            cat_results[k] = score_category(items, k in systemic)
    except ValueError as e:
        sys.exit(f"ERROR: {e}")

    # ---- NA-category weight redistribution (spec 13.1) ---------------------
    active = {k for k, r in cat_results.items() if r["applicable_controls"] > 0}
    active_weight = sum(weights[k] for k in active)
    eff_weights = {k: (weights[k] / active_weight * 100 if k in active else 0) for k in weights}

    # ---- Overall score and coverage ----------------------------------------
    # UNVERIFIED controls reduce coverage, not quality (spec 13.3-13.4).
    # Renormalize the overall-score denominator across categories that have a
    # quality score so an entirely unverified category is not silently scored
    # as zero. The unverified category still blocks approval through coverage.
    scored = [(k, r) for k, r in cat_results.items() if r["score"] is not None]
    scored_weight = sum(eff_weights[k] for k, _ in scored)
    overall = (
        round(sum(r["score"] * eff_weights[k] for k, r in scored) / scored_weight, 1)
        if scored and scored_weight
        else None
    )

    scored_controls = [c for c in controls if map_category(c) is not None]
    applicable = [c for c in scored_controls if c["status"] != "NOT_APPLICABLE"]
    covered = [c for c in applicable if c["status"] in COVERED_STATUSES]
    overall_coverage = round(len(covered) / len(applicable) * 100, 1) if applicable else None

    # ---- Rapid audits also report the Standard-tier denominator (spec 13.3) ----
    std_denominator_coverage = None
    if args.tier == "rapid":
        std_total = data.get("standard_tier_denominator")
        if std_total:
            std_denominator_coverage = round(len(covered) / std_total * 100, 1)

    gate_eval = evaluate_gates(cat_results, overall_coverage, PROFILES[args.profile], applicable)
    gate_fail = [g["control_id"] for g in gates if g["status"] != "PASS"]
    if gate_fail:
        gate_eval["mechanical_blockers"].insert(
            0, f"Gate control not passed: {', '.join(gate_fail)} - advisory status only, "
               f"no approval verdict may be issued")
        gate_eval["gate_recommendation"] = "ADVISORY_ONLY"

    sheet = {
        "schema_version": SCHEMA_VERSION,
        "spec_version": SPEC_VERSION,
        "audit_id": data.get("audit_id"),
        "profile": args.profile,
        "tier": args.tier,
        "weights_used": eff_weights,
        "categories": {k: {**{"label": CATEGORIES[k]["label"]}, **r}
                       for k, r in cat_results.items()},
        "overall_score": overall,
        "overall_coverage_pct": overall_coverage,
        "standard_denominator_coverage_pct": std_denominator_coverage,
        "gate_controls": {g["control_id"]: g["status"] for g in gates},
        "gate_evaluation": gate_eval,
    }

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(sheet, f, indent=2, ensure_ascii=False)

    # ---- Console summary ----------------------------------------------------
    print(f"Audit {sheet['audit_id']}  |  profile {args.profile}  |  tier {args.tier}")
    print("-" * 78)
    for k, r in cat_results.items():
        if r["applicable_controls"] == 0:
            continue
        flag = "  INSUFFICIENT EVIDENCE" if r["insufficient_evidence"] else ""
        score = "n/a " if r["score"] is None else f"{r['score']:>4}"
        print(f"{CATEGORIES[k]['label']:<42} {score}/10  "
              f"cov {r['coverage_pct'] or 0:>5.1f}%  w {eff_weights[k]:>4.1f}%{flag}")
        for cap in r["caps_applied"]:
            print(f"    CAP: {cap}")
    print("-" * 78)
    cov_line = f"{overall_coverage}%"
    if std_denominator_coverage is not None:
        cov_line += f" (rapid denominator), {std_denominator_coverage}% (standard denominator)"
    print(f"OVERALL: {overall}/10   coverage {cov_line}")
    print(f"GATE RECOMMENDATION: {gate_eval['gate_recommendation']}")
    for b in gate_eval["mechanical_blockers"]:
        print(f"  BLOCKER: {b}")
    print(f"  NOTE: {gate_eval['note']}")


if __name__ == "__main__":
    main()
