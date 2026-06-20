#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
from pathlib import Path


BEGIN_MARKER = "<!-- BEGIN:EVAL_RESULTS -->"
END_MARKER = "<!-- END:EVAL_RESULTS -->"


def run_eval_suite(args: argparse.Namespace) -> dict:
    proc = subprocess.run(
        [
            sys.executable,
            "scripts/run_eval_suite.py",
            "--eval-dir",
            args.eval_dir,
            "--description-file",
            args.description_file,
            "--baseline-description-file",
            args.baseline_description_file,
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(proc.stdout)


def render_readme_panel(report: dict) -> str:
    summary = report["summary"]
    suites = report["suites"]
    families = report["family_summary"]

    lines = [
        BEGIN_MARKER,
        f"- regression corpus: `{summary['total_cases']}` prompts across `{summary['family_count']}` families",
        f"- aggregate result: `{summary['false_positives']}` false positives, `{summary['false_negatives']}` false negatives, average precision `{summary['average_precision']}`, average recall `{summary['average_recall']}`",
        "- suite status:",
        "",
        "| Suite | Cases | FP | FN | Precision | Recall |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for suite_name in ("train", "dev", "holdout"):
        suite = suites[suite_name]
        cases = sum(bucket["total"] for bucket in suite["bucket_stats"].values())
        lines.append(
            f"| {suite_name} | {cases} | {suite['false_positives']} | {suite['false_negatives']} | {suite['precision']} | {suite['recall']} |"
        )

    lines.extend(
        [
            "",
            "| Family | Cases | Pass Rate |",
            "| --- | ---: | ---: |",
        ]
    )
    for family, stats in sorted(families.items()):
        lines.append(f"| `{family}` | {stats['total']} | {stats['pass_rate']} |")

    lines.extend(
        [
            "",
            "Full reports: [reports/eval_suite.json](reports/eval_suite.json) and [reports/family_summary.md](reports/family_summary.md)",
            END_MARKER,
        ]
    )
    return "\n".join(lines)


def render_family_summary(report: dict) -> str:
    summary = report["summary"]
    lines = [
        "# Eval Family Summary",
        "",
        f"- total cases: `{summary['total_cases']}`",
        f"- families: `{summary['family_count']}`",
        f"- false positives: `{summary['false_positives']}`",
        f"- false negatives: `{summary['false_negatives']}`",
        f"- average precision: `{summary['average_precision']}`",
        f"- average recall: `{summary['average_recall']}`",
        "",
        "## Family Results",
        "",
        "| Family | Cases | Passed | FP | FN | Pass Rate |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for family, stats in sorted(report["family_summary"].items()):
        lines.append(
            f"| `{family}` | {stats['total']} | {stats['passed']} | {stats['false_positives']} | {stats['false_negatives']} | {stats['pass_rate']} |"
        )
    return "\n".join(lines) + "\n"


def update_readme(readme_path: Path, panel: str) -> None:
    text = readme_path.read_text(encoding="utf-8")
    if BEGIN_MARKER not in text or END_MARKER not in text:
        raise SystemExit(f"README markers not found in {readme_path}")
    start = text.index(BEGIN_MARKER)
    end = text.index(END_MARKER) + len(END_MARKER)
    updated = text[:start] + panel + text[end:]
    readme_path.write_text(updated, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Render README-visible eval results and full family report.")
    parser.add_argument("--eval-dir", default="evals")
    parser.add_argument("--description-file", default="evals/improved_description.txt")
    parser.add_argument("--baseline-description-file", default="evals/baseline_description.txt")
    parser.add_argument("--output-dir", default="reports")
    parser.add_argument("--readme", default="README.md")
    args = parser.parse_args()

    report = run_eval_suite(args)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    (output_dir / "eval_suite.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output_dir / "family_summary.md").write_text(render_family_summary(report), encoding="utf-8")
    update_readme(Path(args.readme), render_readme_panel(report))


if __name__ == "__main__":
    main()
