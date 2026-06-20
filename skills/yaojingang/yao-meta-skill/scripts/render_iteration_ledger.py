#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_snapshots(history_dir: Path) -> list[dict]:
    return [load_json(path) for path in sorted(history_dir.glob("*.json"))]


def render_markdown(
    system_snapshots: list[dict], description_snapshots: list[dict], route_scorecard: dict, promotion_decisions: dict
) -> str:
    lines = [
        "# Iteration Ledger",
        "",
        "## System Milestones",
        "",
        "| Date | Label | Trigger Cases | FP | FN | Route Accuracy | Notes |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for snapshot in system_snapshots:
        trigger_summary = snapshot["trigger_summary"]
        route_summary = snapshot.get("route_summary") or {}
        route_accuracy = route_summary.get("accuracy")
        route_display = "-" if route_accuracy is None else str(route_accuracy)
        lines.append(
            f"| {snapshot['date']} | {snapshot['label']} | {trigger_summary['total_cases']} | {trigger_summary['false_positives']} | {trigger_summary['false_negatives']} | {route_display} | {'; '.join(snapshot.get('notes', []))} |"
        )

    lines.extend(
        [
            "",
            "## Description Optimization Milestones",
            "",
            "| Date | Label | Target | Blind Errors | Judge Blind Errors | Judge Agreement | Adversarial Errors | Adversarial Gap | Adversarial Risk | Drift Note |",
            "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- |",
        ]
    )
    for snapshot in description_snapshots:
        for target in snapshot.get("targets", []):
            blind_errors = target.get("winner_blind_holdout_total_errors")
            judge_blind_errors = target.get("winner_judge_blind_holdout_total_errors")
            judge_blind = (target.get("judge_blind") or {}).get("winner") or {}
            adversarial_errors = target.get("winner_adversarial_holdout_total_errors")
            adversarial_calibration = (target.get("calibration", {}) or {}).get("adversarial_holdout") or {}
            lines.append(
                f"| {snapshot['date']} | {snapshot['label']} | `{target['name']}` | {'-' if blind_errors is None else blind_errors} | {'-' if judge_blind_errors is None else judge_blind_errors} | {judge_blind.get('agreement_rate', '-')} | {'-' if adversarial_errors is None else adversarial_errors} | {'-' if adversarial_calibration.get('score_gap') is None else adversarial_calibration.get('score_gap')} | {adversarial_calibration.get('risk_band', '-')} | {target.get('drift_note', '-')} |"
            )

    lines.extend(
        [
            "",
            "## Current Promotion Decisions",
            "",
            "| Target | Decision | Winner | Causes | Next Action |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for target in promotion_decisions.get("targets", []):
        lines.append(
            f"| `{target['name']}` | `{target['decision']}` | `{target['winner_label']}` | {', '.join(target['promotion']['causes'])} | {target['promotion']['next_action']} |"
        )

    lines.extend(
        [
            "",
            "## Current Route Scorecard",
            "",
            f"- total cases: `{route_scorecard['summary']['total_cases']}`",
            f"- accuracy: `{route_scorecard['summary']['accuracy']}`",
            f"- ambiguous cases: `{route_scorecard['summary']['ambiguous_case_count']}`",
            "",
            "| Route | Precision | Recall | Avg Margin |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for route_name, stats in route_scorecard["route_stats"].items():
        precision = "-" if stats["precision"] is None else stats["precision"]
        recall = "-" if stats["recall"] is None else stats["recall"]
        margin = "-" if stats["average_margin"] is None else stats["average_margin"]
        lines.append(f"| `{route_name}` | {precision} | {recall} | {margin} |")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Render the iteration ledger from regression and routing data.")
    parser.add_argument("--history-dir", default="evals/history")
    parser.add_argument("--description-history-dir", default="evals/history/description_optimization")
    parser.add_argument("--route-scorecard", default="reports/route_scorecard.json")
    parser.add_argument("--promotion-decisions", default="reports/promotion_decisions.json")
    parser.add_argument("--output", default="reports/iteration_ledger.md")
    args = parser.parse_args()

    system_snapshots = load_snapshots(ROOT / args.history_dir)
    description_snapshots = load_snapshots(ROOT / args.description_history_dir)
    route_scorecard = load_json(ROOT / args.route_scorecard)
    promotion_decisions = load_json(ROOT / args.promotion_decisions)

    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        render_markdown(system_snapshots, description_snapshots, route_scorecard, promotion_decisions),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
