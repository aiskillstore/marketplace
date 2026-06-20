#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
from pathlib import Path


def run_case(script: Path, description: Path, baseline: Path, cases: Path) -> dict:
    proc = subprocess.run(
        [
            sys.executable,
            str(script),
            "--description-file",
            str(description),
            "--baseline-description-file",
            str(baseline),
            "--cases",
            str(cases),
            "--semantic-config",
            str(Path("evals/semantic_config.json").resolve()),
        ],
        capture_output=True,
        text=True,
    )
    payload = json.loads(proc.stdout)
    payload["returncode"] = proc.returncode
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Run semantic trigger evaluation across train/dev/holdout suites.")
    parser.add_argument("--eval-dir", default="evals", help="Root eval directory")
    parser.add_argument("--description-file", default="evals/improved_description.txt")
    parser.add_argument("--baseline-description-file", default="evals/baseline_description.txt")
    parser.add_argument("--output-file", help="Optional path to write the combined JSON report")
    args = parser.parse_args()

    root = Path(args.eval_dir).resolve()
    script = Path("scripts/trigger_eval.py").resolve()
    description = Path(args.description_file).resolve()
    baseline = Path(args.baseline_description_file).resolve()

    suites = {}
    aggregate = {"false_positives": 0, "false_negatives": 0, "precision": [], "recall": []}
    family_summary: dict[str, dict] = {}
    for name in ("train", "dev", "holdout"):
        report = run_case(script, description, baseline, root / name / "trigger_cases.json")
        suites[name] = report
        aggregate["false_positives"] += report["false_positives"]
        aggregate["false_negatives"] += report["false_negatives"]
        if report["precision"] is not None:
            aggregate["precision"].append(report["precision"])
        if report["recall"] is not None:
            aggregate["recall"].append(report["recall"])
        for family, stats in report.get("family_stats", {}).items():
            slot = family_summary.setdefault(
                family,
                {"total": 0, "passed": 0, "false_positives": 0, "false_negatives": 0},
            )
            slot["total"] += stats["total"]
            slot["passed"] += stats["passed"]
            slot["false_positives"] += stats["false_positives"]
            slot["false_negatives"] += stats["false_negatives"]

    for family, stats in family_summary.items():
        stats["pass_rate"] = round(stats["passed"] / stats["total"], 3) if stats["total"] else None

    total_cases = sum(stats["total"] for stats in family_summary.values())
    summary = {
        "suite_count": len(suites),
        "total_cases": total_cases,
        "family_count": len(family_summary),
        "false_positives": aggregate["false_positives"],
        "false_negatives": aggregate["false_negatives"],
        "average_precision": round(sum(aggregate["precision"]) / len(aggregate["precision"]), 3) if aggregate["precision"] else None,
        "average_recall": round(sum(aggregate["recall"]) / len(aggregate["recall"]), 3) if aggregate["recall"] else None,
    }
    output = {"summary": summary, "family_summary": family_summary, "suites": suites}
    rendered = json.dumps(output, ensure_ascii=False, indent=2)
    if args.output_file:
        Path(args.output_file).write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    if summary["false_positives"] > 0 or summary["false_negatives"] > 0:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
