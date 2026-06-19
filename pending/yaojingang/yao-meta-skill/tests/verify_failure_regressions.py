#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FAILURES_DIR = ROOT / "failures"
TRIGGER_EVAL = ROOT / "scripts" / "trigger_eval.py"
DESCRIPTION = ROOT / "evals" / "improved_description.txt"
BASELINE = ROOT / "evals" / "baseline_description.txt"
SEMANTIC_CONFIG = ROOT / "evals" / "semantic_config.json"


def run_case(case_file: Path) -> dict:
    proc = subprocess.run(
        [
            sys.executable,
            str(TRIGGER_EVAL),
            "--description-file",
            str(DESCRIPTION),
            "--baseline-description-file",
            str(BASELINE),
            "--cases",
            str(case_file),
            "--semantic-config",
            str(SEMANTIC_CONFIG),
        ],
        capture_output=True,
        text=True,
    )
    payload = json.loads(proc.stdout)
    payload["returncode"] = proc.returncode
    payload["case_file"] = str(case_file.relative_to(ROOT))
    return payload


def main() -> None:
    case_files = sorted(FAILURES_DIR.glob("*/cases.json"))
    reports = [run_case(path) for path in case_files]
    failures = []
    for report in reports:
        if report["returncode"] != 0:
            failures.append(
                {
                    "case_file": report["case_file"],
                    "false_positives": report["false_positives"],
                    "false_negatives": report["false_negatives"],
                    "misfires": report["misfires"],
                }
            )

    output = {
        "ok": not failures,
        "case_count": len(reports),
        "families": [report["case_file"] for report in reports],
        "failures": failures,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
