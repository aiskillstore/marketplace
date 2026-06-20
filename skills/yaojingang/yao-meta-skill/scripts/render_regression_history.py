#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def load_snapshots(history_dir: Path) -> list[dict]:
    snapshots = []
    for path in sorted(history_dir.glob("*.json")):
        snapshots.append(json.loads(path.read_text(encoding="utf-8")))
    return snapshots


def render_markdown(snapshots: list[dict]) -> str:
    lines = [
        "# Regression History",
        "",
        "| Date | Label | Cases | Families | FP | FN | Route Accuracy | Governance | Governed Examples | Notes |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for snapshot in snapshots:
        summary = snapshot["trigger_summary"]
        notes = "; ".join(snapshot.get("notes", []))
        score = snapshot.get("governance_score")
        score_display = "-" if score is None else str(score)
        route_summary = snapshot.get("route_summary") or {}
        route_accuracy = route_summary.get("accuracy")
        route_display = "-" if route_accuracy is None else str(route_accuracy)
        lines.append(
            f"| {snapshot['date']} | {snapshot['label']} | {summary['total_cases']} | {summary['family_count']} | {summary['false_positives']} | {summary['false_negatives']} | {route_display} | {score_display} | {snapshot.get('governed_examples', 0)} | {notes} |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Render regression history from milestone snapshots.")
    parser.add_argument("--history-dir", default="evals/history")
    parser.add_argument("--output", default="reports/regression_history.md")
    args = parser.parse_args()

    history_dir = Path(args.history_dir)
    snapshots = load_snapshots(history_dir)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_markdown(snapshots), encoding="utf-8")


if __name__ == "__main__":
    main()
