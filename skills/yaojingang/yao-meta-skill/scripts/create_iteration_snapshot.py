#!/usr/bin/env python3
import argparse
import json
import re
from datetime import date
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

CONTEXT_REPORTS = {
    "yao-meta-skill": ROOT / "reports" / "context_budget.json",
    "team-frontend-review": ROOT
    / "examples"
    / "team-frontend-review"
    / "generated-skill"
    / "reports"
    / "context_budget.json",
    "governed-incident-command": ROOT
    / "examples"
    / "governed-incident-command"
    / "generated-skill"
    / "reports"
    / "context_budget.json",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def relative(path: Path) -> str:
    return str(path.relative_to(ROOT))


def slugify(text: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", text.strip().lower())
    return value.strip("-") or "snapshot"


def summarize_target(target: dict, route_scorecard: dict, optimization_report: dict, context_report: dict) -> dict:
    route_stats = route_scorecard.get("route_stats", {}).get(target["name"], {})
    winner_summary = optimization_report.get("winner", {})
    holdout = winner_summary.get("holdout", {})
    blind = winner_summary.get("blind_holdout", {})
    judge_blind = ((target.get("judge_blind") or {}).get("winner") or {})
    adversarial = winner_summary.get("adversarial_holdout", {})
    adversarial_calibration = ((target.get("calibration") or {}).get("adversarial_holdout") or {})
    return {
        "winner_label": target["winner_label"],
        "decision": target["decision"],
        "visible_holdout_total_errors": holdout.get("false_positives", 0) + holdout.get("false_negatives", 0),
        "blind_holdout_total_errors": blind.get("false_positives", 0) + blind.get("false_negatives", 0),
        "judge_blind_total_errors": target.get("winner_judge_blind_holdout_total_errors"),
        "judge_blind_agreement": judge_blind.get("agreement_rate"),
        "adversarial_total_errors": adversarial.get("false_positives", 0) + adversarial.get("false_negatives", 0),
        "adversarial_gap": adversarial_calibration.get("score_gap"),
        "adversarial_risk_band": adversarial_calibration.get("risk_band"),
        "route_precision": route_stats.get("precision"),
        "route_recall": route_stats.get("recall"),
        "route_average_margin": route_stats.get("average_margin"),
        "context_initial_load_tokens": context_report.get("initial_load_tokens"),
        "context_budget": context_report.get("budget"),
        "quality_density": context_report.get("quality_density"),
    }


def render_markdown(snapshot: dict) -> str:
    summary = snapshot["summary"]
    lines = [
        f"# Release Snapshot: {snapshot['target']}",
        "",
        f"- label: `{snapshot['label']}`",
        f"- date: `{snapshot['date']}`",
        f"- decision: `{snapshot['decision']}`",
        f"- winner label: `{summary['winner_label']}`",
        f"- next action: {snapshot['next_action']}",
        "",
        "## Promotion Gates",
        "",
        "| Gate | Pass |",
        "| --- | --- |",
    ]
    for gate, passed in snapshot["gate_status"].items():
        lines.append(f"| `{gate}` | {passed} |")
    lines.extend(
        [
            "",
            "## Quality Summary",
            "",
            f"- visible holdout total errors: `{summary['visible_holdout_total_errors']}`",
            f"- blind holdout total errors: `{summary['blind_holdout_total_errors']}`",
            f"- judge blind total errors: `{summary['judge_blind_total_errors']}`",
            f"- judge blind agreement: `{summary['judge_blind_agreement']}`",
            f"- adversarial total errors: `{summary['adversarial_total_errors']}`",
            f"- adversarial gap: `{summary['adversarial_gap']}`",
            f"- adversarial risk band: `{summary['adversarial_risk_band']}`",
            f"- route precision: `{summary['route_precision']}`",
            f"- route recall: `{summary['route_recall']}`",
            f"- route average margin: `{summary['route_average_margin']}`",
            f"- context initial load: `{summary['context_initial_load_tokens']}/{summary['context_budget']}`",
            f"- quality density: `{summary['quality_density']}`",
            "",
            "## Cause Tags",
            "",
        ]
    )
    for cause in snapshot["cause_tags"]:
        lines.append(f"- `{cause}`")
    lines.extend(["", "## Artifact Paths", ""])
    for key, path in snapshot["artifacts"].items():
        lines.append(f"- {key}: `{path}`")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a versioned release snapshot from current promotion outputs.")
    parser.add_argument("--target", required=True)
    parser.add_argument("--label", default="manual")
    parser.add_argument("--promotion-decisions", default="reports/promotion_decisions.json")
    parser.add_argument("--route-scorecard", default="reports/route_scorecard.json")
    parser.add_argument("--output-dir", default="reports/release_snapshots")
    args = parser.parse_args()

    promotion_decisions = load_json(ROOT / args.promotion_decisions)
    route_scorecard = load_json(ROOT / args.route_scorecard)
    target = next((item for item in promotion_decisions["targets"] if item["name"] == args.target), None)
    if target is None:
        raise SystemExit(f"Unknown promotion target: {args.target}")

    optimization_report = load_json(OPTIMIZATION_REPORTS[args.target])
    context_report = load_json(CONTEXT_REPORTS[args.target])
    label = f"{date.today().isoformat()}-{slugify(args.label)}"
    output_dir = ROOT / args.output_dir / args.target
    output_dir.mkdir(parents=True, exist_ok=True)
    snapshot_json = output_dir / f"{label}.json"
    snapshot_md = output_dir / f"{label}.md"

    bundle_dir = ROOT / "reports" / "iteration_bundles" / args.target
    summary = summarize_target(target, route_scorecard, optimization_report, context_report)
    snapshot = {
        "target": args.target,
        "label": label,
        "date": date.today().isoformat(),
        "decision": target["decision"],
        "next_action": target["promotion"]["next_action"],
        "cause_tags": target["promotion"]["causes"],
        "gate_status": target["promotion"]["gate_status"],
        "summary": summary,
        "artifacts": {
            "bundle_json": relative(bundle_dir / "bundle.json"),
            "bundle_md": relative(bundle_dir / "bundle.md"),
            "review_md": relative(bundle_dir / "review.md"),
            "optimization_report": relative(OPTIMIZATION_REPORTS[args.target]),
            "promotion_decisions": relative(ROOT / args.promotion_decisions),
            "route_scorecard": relative(ROOT / args.route_scorecard),
            "context_budget": relative(CONTEXT_REPORTS[args.target]),
            "iteration_ledger": "reports/iteration_ledger.md",
        },
    }

    snapshot_json.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    snapshot_md.write_text(render_markdown(snapshot), encoding="utf-8")
    print(
        json.dumps(
            {
                "ok": True,
                "target": args.target,
                "label": label,
                "artifacts": {
                    "snapshot_json": relative(snapshot_json),
                    "snapshot_md": relative(snapshot_md),
                    "review_md": relative(bundle_dir / "review.md"),
                    "bundle_md": relative(bundle_dir / "bundle.md"),
                },
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
