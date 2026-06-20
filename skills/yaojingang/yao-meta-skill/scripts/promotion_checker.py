#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent

OPTIMIZATION_REPORTS = {
    "yao-meta-skill": ROOT / "reports" / "description_optimization.json",
    "team-frontend-review": ROOT / "examples" / "team-frontend-review" / "optimization" / "reports" / "description_optimization.json",
    "governed-incident-command": ROOT
    / "examples"
    / "governed-incident-command"
    / "optimization"
    / "reports"
    / "description_optimization.json",
}

SKILL_PATHS = {
    "yao-meta-skill": ROOT / "SKILL.md",
    "team-frontend-review": ROOT / "examples" / "team-frontend-review" / "generated-skill" / "SKILL.md",
    "governed-incident-command": ROOT / "examples" / "governed-incident-command" / "generated-skill" / "SKILL.md",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def error_total(prefix: str, target: dict) -> int:
    return int(target.get(f"{prefix}_fp", 0)) + int(target.get(f"{prefix}_fn", 0))


def family_clean(summary: dict | None) -> bool:
    if not summary:
        return False
    return summary.get("clean_family_count", 0) == summary.get("family_count", 0)


def relative(path: Path) -> str:
    return str(path.relative_to(ROOT))


def classify_target(target: dict, route_scorecard: dict) -> dict:
    route_summary = route_scorecard["summary"]
    route_stats = route_scorecard["route_stats"].get(target["name"], {})
    winner_changed = target["winner_label"] != "Current"
    visible_ok = error_total("winner_holdout", target) <= error_total("current_holdout", target) and error_total(
        "winner_holdout", target
    ) <= error_total("baseline_holdout", target)
    blind_ok = error_total("winner_blind_holdout", target) <= error_total(
        "current_blind_holdout", target
    ) and error_total("winner_blind_holdout", target) <= error_total("baseline_blind_holdout", target)
    judge_ok = error_total("winner_judge_blind_holdout", target) <= error_total(
        "current_judge_blind_holdout", target
    ) and error_total("winner_judge_blind_holdout", target) <= error_total("baseline_judge_blind_holdout", target)
    judge_agreement = ((target.get("judge_blind") or {}).get("winner") or {}).get("agreement_rate")
    judge_agreement_ok = judge_agreement is not None and judge_agreement >= 0.95
    adversarial_ok = error_total("winner_adversarial_holdout", target) <= error_total(
        "current_adversarial_holdout", target
    ) and error_total("winner_adversarial_holdout", target) <= error_total("baseline_adversarial_holdout", target)
    holdout_calibration = (target.get("calibration") or {}).get("holdout") or {}
    adversarial_calibration = (target.get("calibration") or {}).get("adversarial_holdout") or {}
    adversarial_risk = adversarial_calibration.get("risk_band")
    adversarial_risk_ok = adversarial_risk not in {"overlap", None}
    route_clean = (
        route_summary.get("misroute_count", 0) == 0
        and route_summary.get("ambiguous_case_count", 0) == 0
        and route_stats.get("precision") == 1.0
        and route_stats.get("recall") == 1.0
    )
    family_ok = all(
        family_clean((target.get("family_health") or {}).get(gate))
        for gate in ("blind_holdout", "judge_blind_holdout", "adversarial_holdout")
    )

    causes = []
    if not winner_changed:
        causes.append("no_candidate_outperformed_current")
    if not visible_ok:
        causes.append("visible_holdout_regression")
    if not blind_ok:
        causes.append("blind_holdout_regression")
    if error_total("winner_holdout", target) > 0:
        causes.append("current_holdout_gap_present")
    if holdout_calibration.get("risk_band") in {"overlap", "watch", "tight"}:
        causes.append("current_holdout_risk")
    if not judge_ok:
        causes.append("judge_blind_regression")
    if not judge_agreement_ok:
        causes.append("judge_blind_low_agreement")
    if not adversarial_ok:
        causes.append("adversarial_regression")
    if adversarial_risk == "overlap":
        causes.append("adversarial_overlap_risk")
    elif adversarial_risk in {"watch", "tight"}:
        causes.append("adversarial_watch_risk")
    if not family_ok:
        causes.append("family_instability")
    if route_summary.get("misroute_count", 0):
        causes.append("route_confusion")
    if route_summary.get("ambiguous_case_count", 0):
        causes.append("route_ambiguity")
    if target["winner_tokens"] > target["current_tokens"] and not winner_changed:
        causes.append("longer_without_gain")

    severe = (
        route_summary.get("misroute_count", 0) > 0
        or route_summary.get("ambiguous_case_count", 0) > 0
        or adversarial_risk == "overlap"
        or not judge_agreement_ok
    )

    all_gates_pass = all(
        [visible_ok, blind_ok, judge_ok, judge_agreement_ok, adversarial_ok, adversarial_risk_ok, route_clean, family_ok]
    )

    if winner_changed and all_gates_pass:
        decision = "promote"
    elif severe:
        decision = "blocked"
    else:
        decision = "keep_current"

    if decision == "promote" and "promotion_ready" not in causes:
        causes.append("promotion_ready")

    next_action = {
        "promote": "Review the promoted candidate, update the skill description, and snapshot the release.",
        "keep_current": "Keep the current description and open a new candidate only when fresh route evidence appears.",
        "blocked": "Do not promote. Investigate failing gates, route collisions, or calibration risk before generating new candidates.",
    }[decision]

    return {
        "decision": decision,
        "winner_changed": winner_changed,
        "all_gates_pass": all_gates_pass,
        "route_clean": route_clean,
        "judge_agreement_ok": judge_agreement_ok,
        "causes": causes,
        "next_action": next_action,
        "gate_status": {
            "visible_holdout_non_regression": visible_ok,
            "blind_holdout_non_regression": blind_ok,
            "judge_blind_non_regression": judge_ok,
            "judge_blind_agreement": judge_agreement_ok,
            "adversarial_non_regression": adversarial_ok,
            "adversarial_risk_ok": adversarial_risk_ok,
            "route_confusion_clean": route_clean,
            "family_stability": family_ok,
        },
        "route_metrics": {
            "precision": route_stats.get("precision"),
            "recall": route_stats.get("recall"),
            "average_margin": route_stats.get("average_margin"),
            "misroute_count": route_summary.get("misroute_count"),
            "ambiguous_case_count": route_summary.get("ambiguous_case_count"),
        },
    }


def build_candidate_entries(target_name: str, target_summary: dict, decision: str) -> list[dict]:
    report = load_json(OPTIMIZATION_REPORTS[target_name])
    winner_description = report["winner"]["description"]
    winner_dev_errors = report["winner"]["dev"]["false_positives"] + report["winner"]["dev"]["false_negatives"]
    entries = [
        {
            "name": target_name,
            "role": "baseline",
            "label": "Baseline",
            "ranking_state": "reference",
            "promotion_state": "reference",
            "description": report["baseline"]["description"] if report.get("baseline") else None,
            "tokens": report["baseline"]["estimated_tokens"] if report.get("baseline") else None,
            "dev_errors": (
                report["baseline"]["dev"]["false_positives"] + report["baseline"]["dev"]["false_negatives"]
                if report.get("baseline")
                else None
            ),
            "holdout_errors": (
                report["baseline"]["holdout"]["false_positives"] + report["baseline"]["holdout"]["false_negatives"]
                if report.get("baseline") and report["baseline"].get("holdout")
                else None
            ),
        }
    ]

    for candidate in report["candidates"]:
        selected = candidate["description"] == winner_description
        role = "current" if candidate["id"] == "current" else "candidate"
        if selected and decision == "promote":
            promotion_state = "promoted"
        elif selected and role == "current":
            promotion_state = "kept_current"
        elif selected:
            promotion_state = "blocked"
        else:
            promotion_state = "blocked"

        reason_tags = []
        candidate_dev_errors = candidate["dev"]["false_positives"] + candidate["dev"]["false_negatives"]
        if candidate_dev_errors > winner_dev_errors:
            reason_tags.append("weaker_dev_fit")
        holdout = candidate.get("holdout") or {}
        holdout_errors = holdout.get("false_positives", 0) + holdout.get("false_negatives", 0) if holdout else None
        if holdout_errors is not None and holdout_errors > error_total("current_holdout", target_summary):
            reason_tags.append("visible_holdout_regression")
        if candidate["estimated_tokens"] > target_summary["current_tokens"] and not selected:
            reason_tags.append("longer_without_gain")
        if not reason_tags and not selected:
            reason_tags.append("not_selected_by_dev_ranking")

        entries.append(
            {
                "name": target_name,
                "role": role,
                "label": candidate["label"],
                "ranking_state": "selected_by_dev" if selected else "not_selected",
                "promotion_state": promotion_state,
                "description": candidate["description"],
                "tokens": candidate["estimated_tokens"],
                "dev_errors": candidate_dev_errors,
                "holdout_errors": holdout_errors,
                "reason_tags": reason_tags,
            }
        )
    return entries


def render_candidate_registry_md(targets: list[dict]) -> str:
    lines = [
        "# Candidate Registry",
        "",
        "| Target | Role | Label | Ranking State | Promotion State | Tokens | Dev Errors | Holdout Errors | Reason Tags |",
        "| --- | --- | --- | --- | --- | ---: | ---: | ---: | --- |",
    ]
    for target in targets:
        for entry in target["registry"]:
            lines.append(
                f"| `{target['name']}` | {entry['role']} | `{entry['label']}` | {entry['ranking_state']} | {entry['promotion_state']} | {'-' if entry['tokens'] is None else entry['tokens']} | {'-' if entry['dev_errors'] is None else entry['dev_errors']} | {'-' if entry['holdout_errors'] is None else entry['holdout_errors']} | {', '.join(entry.get('reason_tags', [])) or '-'} |"
            )
    return "\n".join(lines) + "\n"


def render_promotion_md(targets: list[dict]) -> str:
    lines = [
        "# Promotion Decisions",
        "",
        "| Target | Decision | Winner | Route Clean | Judge Agreement | Adv Risk | Causes | Next Action |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for target in targets:
        decision = target["decision"]
        judge_summary = ((target.get("judge_blind") or {}).get("winner") or {}).get("agreement_rate")
        adv_risk = ((target.get("calibration") or {}).get("adversarial_holdout") or {}).get("risk_band")
        lines.append(
            f"| `{target['name']}` | `{decision}` | `{target['winner_label']}` | {target['promotion']['route_clean']} | {judge_summary if judge_summary is not None else '-'} | {adv_risk or '-'} | {', '.join(target['promotion']['causes'])} | {target['promotion']['next_action']} |"
        )
    return "\n".join(lines) + "\n"


def render_bundle_md(bundle: dict) -> str:
    review = bundle["review_template"]
    lines = [
        f"# Iteration Bundle: {bundle['target']}",
        "",
        f"- decision: `{bundle['decision']}`",
        f"- winner label: `{bundle['winner_label']}`",
        f"- winner changed: `{bundle['winner_changed']}`",
        f"- next action: {bundle['next_action']}",
        "",
        "## Cause Tags",
        "",
    ]
    for cause in bundle["cause_tags"]:
        lines.append(f"- `{cause}`")
    lines.extend(
        [
            "",
            "## Gate Status",
            "",
            "| Gate | Pass |",
            "| --- | --- |",
        ]
    )
    for gate, passed in bundle["gate_status"].items():
        lines.append(f"| `{gate}` | {passed} |")
    lines.extend(
        [
            "",
            "## Candidate Registry",
            "",
            "| Role | Label | Ranking State | Promotion State | Tokens | Dev Errors | Holdout Errors |",
            "| --- | --- | --- | --- | ---: | ---: | ---: |",
        ]
    )
    for entry in bundle["candidate_registry"]:
        lines.append(
            f"| {entry['role']} | `{entry['label']}` | {entry['ranking_state']} | {entry['promotion_state']} | {'-' if entry['tokens'] is None else entry['tokens']} | {'-' if entry['dev_errors'] is None else entry['dev_errors']} | {'-' if entry['holdout_errors'] is None else entry['holdout_errors']} |"
        )
    lines.extend(
        [
            "",
            "## Human Review Stub",
            "",
            f"- target: {review['target']}",
            f"- current description: {review['current_description']}",
            f"- candidate description: {review['candidate_description']}",
            f"- review focus: {', '.join(review['focus'])}",
            "",
            "## Artifact Paths",
            "",
        ]
    )
    for label, path in bundle["artifacts"].items():
        lines.append(f"- {label}: `{path}`")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply promotion policy and build iteration bundles.")
    parser.add_argument("--optimization-suite", default="reports/description_optimization_suite.json")
    parser.add_argument("--route-scorecard", default="reports/route_scorecard.json")
    parser.add_argument("--output-json", default="reports/promotion_decisions.json")
    parser.add_argument("--output-md", default="reports/promotion_decisions.md")
    parser.add_argument("--candidate-registry-json", default="reports/candidate_registry.json")
    parser.add_argument("--candidate-registry-md", default="reports/candidate_registry.md")
    parser.add_argument("--bundle-dir", default="reports/iteration_bundles")
    args = parser.parse_args()

    suite = load_json(ROOT / args.optimization_suite)
    route_scorecard = load_json(ROOT / args.route_scorecard)
    bundle_dir = ROOT / args.bundle_dir
    bundle_dir.mkdir(parents=True, exist_ok=True)

    targets = []
    decisions = []
    for target in suite["targets"]:
        promotion = classify_target(target, route_scorecard)
        registry = build_candidate_entries(target["name"], target, promotion["decision"])
        target["promotion"] = promotion
        target["registry"] = registry
        target["decision"] = promotion["decision"]
        targets.append(target)
        decisions.append(promotion["decision"])

        bundle = {
            "target": target["name"],
            "decision": promotion["decision"],
            "winner_label": target["winner_label"],
            "winner_changed": promotion["winner_changed"],
            "next_action": promotion["next_action"],
            "cause_tags": promotion["causes"],
            "gate_status": promotion["gate_status"],
            "candidate_registry": registry,
            "review_template": {
                "target": target["name"],
                "current_description": target["winner_description"] if target["winner_label"] == "Current" else load_json(OPTIMIZATION_REPORTS[target["name"]])["current_description"],
                "candidate_description": target["winner_description"],
                "focus": promotion["causes"][:3] or ["promotion_ready"],
            },
            "artifacts": {
                "skill": relative(SKILL_PATHS[target["name"]]),
                "optimization_report": relative(OPTIMIZATION_REPORTS[target["name"]]),
                "promotion_decisions": relative(ROOT / args.output_json),
                "candidate_registry": relative(ROOT / args.candidate_registry_json),
                "regression_cause_taxonomy": "references/regression-cause-taxonomy.md",
                "human_review_template": "references/human-review-template.md",
            },
        }
        target_dir = bundle_dir / target["name"]
        target_dir.mkdir(parents=True, exist_ok=True)
        (target_dir / "bundle.json").write_text(json.dumps(bundle, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (target_dir / "bundle.md").write_text(render_bundle_md(bundle), encoding="utf-8")
        (target_dir / "review.md").write_text(
            "\n".join(
                [
                    "# Human Review",
                    "",
                    f"- target: {bundle['review_template']['target']}",
                    f"- current description: {bundle['review_template']['current_description']}",
                    f"- candidate description: {bundle['review_template']['candidate_description']}",
                    f"- suggested focus: {', '.join(bundle['review_template']['focus'])}",
                    "",
                    "Use the shared template in `references/human-review-template.md` to complete the final decision.",
                    "",
                ]
            ),
            encoding="utf-8",
        )

    summary = {
        "ok": "blocked" not in decisions,
        "summary": {
            "promote": sum(1 for d in decisions if d == "promote"),
            "keep_current": sum(1 for d in decisions if d == "keep_current"),
            "blocked": sum(1 for d in decisions if d == "blocked"),
        },
        "targets": targets,
    }

    output_json = ROOT / args.output_json
    output_md = ROOT / args.output_md
    candidate_json = ROOT / args.candidate_registry_json
    candidate_md = ROOT / args.candidate_registry_md
    output_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    output_md.write_text(render_promotion_md(targets), encoding="utf-8")
    candidate_json.write_text(json.dumps({"targets": targets}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    candidate_md.write_text(render_candidate_registry_md(targets), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if not summary["ok"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
