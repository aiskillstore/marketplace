#!/usr/bin/env python3
"""Experimental data statistical analysis script (CSV)

How to use:
- Run first: python scripts/init_run.py (generate running directory and configuration)
- Modify config.json in the running directory
- Run: python scripts/analyze_experiment.py

Description:
- Depends on pandas, numpy, scipy
- Output JSON and Markdown summary"""

from __future__ import annotations

import json
from pathlib import Path

RUNS_DIR = Path("outputs/runs")

CONFIG: dict = {}


def require_packages():
    try:
        import numpy as np  # noqa: F401
        import pandas as pd  # noqa: F401
        from scipy import stats  # noqa: F401
    except Exception as exc:  # pragma: no cover
        print("[ERROR] Missing dependency package: pandas/numpy/scipy. Please install it first and then run it.")
        raise SystemExit(1) from exc


def load_run_dir():
    if not RUNS_DIR.exists():
        print("[ERROR] The running directory was not found, please run scripts/init_run.py first.")
        raise SystemExit(1)
    candidates = [path for path in RUNS_DIR.iterdir() if path.is_dir()]
    if not candidates:
        print("[ERROR] No available run directory found, please run scripts/init_run.py first.")
        raise SystemExit(1)
    run_dir = max(candidates, key=lambda path: path.stat().st_mtime).resolve()
    return run_dir


def ensure_within_run(path: Path, run_dir: Path) -> Path:
    run_dir_resolved = run_dir.resolve()
    path_resolved = path.resolve()
    try:
        path_resolved.relative_to(run_dir_resolved)
    except ValueError:
        print(f"[ERROR] The path exceeds the scope of the running directory: {path_resolved}")
        raise SystemExit(1)
    return path_resolved


def resolve_path(value: str, run_dir: Path) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = run_dir / path
    return ensure_within_run(path, run_dir)


def load_config(run_dir: Path):
    config_path = run_dir / "config.json"
    if not config_path.exists():
        print(f"[ERROR] Configuration file not found: {config_path}")
        raise SystemExit(1)
    with config_path.open("r", encoding="utf-8") as handle:
        config = json.load(handle)
    config["input_csv"] = resolve_path(config["input_csv"], run_dir)
    config["output_json"] = resolve_path(config["output_json"], run_dir)
    config["output_md"] = resolve_path(config["output_md"], run_dir)
    return config


def load_data():
    import pandas as pd

    path = CONFIG["input_csv"]
    if not path.exists():
        print(f"[ERROR] Input file not found: {path}")
        raise SystemExit(1)
    return pd.read_csv(path, encoding="utf-8")


def compute_descriptive(df):
    group_col = CONFIG["group_col"]
    value_col = CONFIG["value_col"]
    if group_col not in df.columns or value_col not in df.columns:
        print("[ERROR] The input data is missing the specified column.")
        raise SystemExit(1)
    grouped = df.groupby(group_col)[value_col]
    summary = grouped.agg(["count", "mean", "std"]).reset_index()
    summary["sem"] = summary["std"] / summary["count"].pow(0.5)
    return summary


def run_t_test(df):
    from scipy import stats

    group_col = CONFIG["group_col"]
    value_col = CONFIG["value_col"]
    groups = [g for g in df[group_col].dropna().unique()]
    if len(groups) != 2:
        print("[ERROR] The t-test requires exactly two sets of data.")
        raise SystemExit(1)
    g1 = df[df[group_col] == groups[0]][value_col].dropna()
    g2 = df[df[group_col] == groups[1]][value_col].dropna()
    if CONFIG["paired"]:
        stat, p = stats.ttest_rel(g1, g2, nan_policy="omit")
        test_name = "paired_t_test"
    else:
        stat, p = stats.ttest_ind(g1, g2, nan_policy="omit", equal_var=False)
        test_name = "welch_t_test"
    return {
        "test": test_name,
        "groups": groups,
        "statistic": float(stat),
        "p_value": float(p),
    }


def run_anova(df):
    from scipy import stats

    group_col = CONFIG["group_col"]
    value_col = CONFIG["value_col"]
    groups = [g for g in df[group_col].dropna().unique()]
    if len(groups) < 2:
        print("[ERROR] ANOVA requires at least two sets of data.")
        raise SystemExit(1)
    samples = [
        df[df[group_col] == group][value_col].dropna() for group in groups
    ]
    stat, p = stats.f_oneway(*samples)
    return {
        "test": "anova_oneway",
        "groups": groups,
        "statistic": float(stat),
        "p_value": float(p),
    }


def write_outputs(summary, test_result):
    output_json = CONFIG["output_json"]
    output_md = CONFIG["output_md"]
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)

    report = {
        "summary": summary.to_dict(orient="records"),
        "test": test_result,
    }
    with output_json.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)

    lines = [
        "# Statistical analysis report",
        "",
        "## Descriptive Statistics",
        "",
    ]
    lines.append(summary.to_markdown(index=False))
    lines.extend(
        [
            "",
            "## Test results",
            "",
            f"- method：{test_result['test']}",
            f"- Statistics：{test_result['statistic']:.6f}",
            f"- p value：{test_result['p_value']:.6f}",
        ]
    )
    output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    require_packages()
    run_dir = load_run_dir()
    global CONFIG
    CONFIG = load_config(run_dir)
    df = load_data()
    summary = compute_descriptive(df)
    test_type = CONFIG["test_type"].lower()
    if test_type == "t_test":
        test_result = run_t_test(df)
    elif test_type == "anova":
        test_result = run_anova(df)
    else:
        print("[ERROR] test_type only supports t_test or anova.")
        raise SystemExit(1)
    write_outputs(summary, test_result)
    print("[OK] Statistical analysis report has been generated.")


if __name__ == "__main__":
    main()
