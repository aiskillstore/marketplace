#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def parse_entry(value: str) -> tuple[str, Path]:
    if "::" not in value:
        raise ValueError("Entry must use label::path format.")
    label, raw_path = value.split("::", 1)
    return label.strip() or "target", Path(raw_path).resolve()


def load_report(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Unexpected payload in {path}")
    return payload


def metric_snapshot(report: dict, prefix: str) -> dict:
    summary = report.get("summary", {})
    return {
        "tokens": summary.get(f"{prefix}_tokens", 0),
        "dev_errors": summary.get(f"{prefix}_dev_total_errors", 0),
        "holdout_errors": summary.get(f"{prefix}_holdout_total_errors", 0),
        "blind_errors": summary.get(f"{prefix}_blind_holdout_total_errors", 0),
        "judge_blind_errors": summary.get(f"{prefix}_judge_blind_holdout_total_errors", 0),
        "adversarial_errors": summary.get(f"{prefix}_adversarial_holdout_total_errors", 0),
    }


def total_errors(snapshot: dict) -> int:
    return (
        snapshot["dev_errors"]
        + snapshot["holdout_errors"]
        + snapshot["blind_errors"]
        + snapshot["judge_blind_errors"]
        + snapshot["adversarial_errors"]
    )


def compare_target(label: str, report: dict) -> dict:
    baseline = metric_snapshot(report, "baseline")
    current = metric_snapshot(report, "current")
    winner = metric_snapshot(report, "winner")
    return {
        "label": label,
        "winner_label": report.get("summary", {}).get("winner_label", report.get("winner", {}).get("label", "winner")),
        "baseline": baseline,
        "current": current,
        "winner": winner,
        "delta": {
            "current_vs_baseline": total_errors(baseline) - total_errors(current),
            "winner_vs_baseline": total_errors(baseline) - total_errors(winner),
            "winner_vs_current": total_errors(current) - total_errors(winner),
        },
    }


def build_summary(comparisons: list[dict]) -> dict:
    baseline_total = sum(total_errors(item["baseline"]) for item in comparisons)
    current_total = sum(total_errors(item["current"]) for item in comparisons)
    winner_total = sum(total_errors(item["winner"]) for item in comparisons)
    return {
        "target_count": len(comparisons),
        "baseline_total_errors": baseline_total,
        "current_total_errors": current_total,
        "winner_total_errors": winner_total,
        "winner_vs_baseline_gain": baseline_total - winner_total,
        "winner_vs_current_gain": current_total - winner_total,
    }


def render_markdown(payload: dict) -> str:
    lines = [
        "# Baseline Compare",
        "",
        "A lightweight with-skill vs baseline comparison across tracked optimization targets.",
        "",
        f"- Targets: `{payload['summary']['target_count']}`",
        f"- Baseline total errors: `{payload['summary']['baseline_total_errors']}`",
        f"- Current total errors: `{payload['summary']['current_total_errors']}`",
        f"- Winner total errors: `{payload['summary']['winner_total_errors']}`",
        f"- Winner vs baseline gain: `{payload['summary']['winner_vs_baseline_gain']}`",
        f"- Winner vs current gain: `{payload['summary']['winner_vs_current_gain']}`",
        "",
        "## Target Breakdown",
        "",
        "| Target | Baseline Errors | Current Errors | Winner Errors | Winner Label |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    for item in payload["comparisons"]:
        lines.append(
            f"| {item['label']} | {total_errors(item['baseline'])} | {total_errors(item['current'])} | {total_errors(item['winner'])} | {item['winner_label']} |"
        )
    return "\n".join(lines).strip() + "\n"


def render_baseline_compare(entries: list[tuple[str, Path]], output_json: Path | None = None, output_md: Path | None = None) -> dict:
    comparisons = [compare_target(label, load_report(path)) for label, path in entries]
    payload = {
        "summary": build_summary(comparisons),
        "comparisons": comparisons,
    }
    if output_json:
        output_json.parent.mkdir(parents=True, exist_ok=True)
        output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    if output_md:
        output_md.parent.mkdir(parents=True, exist_ok=True)
        output_md.write_text(render_markdown(payload), encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a baseline comparison report from description optimization artifacts.")
    parser.add_argument("--entry", action="append", required=True, help="Format: label::/absolute/path/to/description_optimization.json")
    parser.add_argument("--output-json")
    parser.add_argument("--output-md")
    args = parser.parse_args()
    entries = [parse_entry(value) for value in args.entry]
    payload = render_baseline_compare(
        entries,
        output_json=Path(args.output_json).resolve() if args.output_json else None,
        output_md=Path(args.output_md).resolve() if args.output_md else None,
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
