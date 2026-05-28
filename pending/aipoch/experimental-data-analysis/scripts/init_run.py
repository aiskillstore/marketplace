#!/usr/bin/env python3
"""Initialize the running directory (experimental data analysis)

Usage:
- Run: python scripts/init_run.py

Output:
- outputs/runs/<timestamp>/config.json
- outputs/runs/<timestamp>/data/experiment.csv"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

RUNS_DIR = Path("outputs/runs")

DEFAULT_CONFIG = {
    "input_csv": "data/experiment.csv",
    "group_col": "group",
    "value_col": "value",
    "paired": False,
    "test_type": "t_test",
    "output_json": "outputs/stat_report.json",
    "output_md": "outputs/stat_report.md",
}

SAMPLE_DATA = [
    ["group", "value"],
    ["control", 1.2],
    ["control", 1.1],
    ["control", 1.3],
    ["treatment", 1.6],
    ["treatment", 1.7],
    ["treatment", 1.5],
]


def main() -> None:
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = RUNS_DIR / run_id
    data_dir = run_dir / "data"
    outputs_dir = run_dir / "outputs"

    data_dir.mkdir(parents=True, exist_ok=True)
    outputs_dir.mkdir(parents=True, exist_ok=True)

    config_path = run_dir / "config.json"
    with config_path.open("w", encoding="utf-8") as handle:
        json.dump(DEFAULT_CONFIG, handle, ensure_ascii=False, indent=2)

    sample_path = data_dir / "experiment.csv"
    sample_path.write_text("\n".join(",".join(map(str, row)) for row in SAMPLE_DATA) + "\n", encoding="utf-8")

    print(f"[OK] Run directory created: {run_dir}")
    print(f"[OK] Configuration has been written: {config_path}")
    print(f"[OK] Sample data written: {sample_path}")


if __name__ == "__main__":
    main()
