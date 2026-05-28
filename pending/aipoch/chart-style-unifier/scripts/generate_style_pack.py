#!/usr/bin/env python3
"""Generate chart style package (matplotlib + plotly)

How to use:
- Run first: python scripts/init_run.py (generate running directory and configuration)
- Modify config.json in the running directory
- Run: python scripts/generate_style_pack.py

Output:
- <run directory>/outputs/style.mplstyle
- <run directory>/outputs/plotly_template.json"""

from __future__ import annotations

import json
from pathlib import Path

RUNS_DIR = Path("outputs/runs")

CONFIG: dict = {}


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
    config["output_dir"] = resolve_path(config["output_dir"], run_dir)
    return config


def write_mplstyle():
    output_dir = CONFIG["output_dir"]
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "style.mplstyle"
    lines = [
        f"font.family: {CONFIG['font_family']}",
        f"font.size: {CONFIG['font_size']}",
        f"axes.titlesize: {CONFIG['title_size']}",
        f"axes.labelsize: {CONFIG['label_size']}",
        f"xtick.labelsize: {CONFIG['tick_size']}",
        f"ytick.labelsize: {CONFIG['tick_size']}",
        f"lines.linewidth: {CONFIG['line_width']}",
        f"lines.markersize: {CONFIG['marker_size']}",
        f"axes.prop_cycle: cycler('color', {CONFIG['palette']})",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_plotly_template():
    output_dir = CONFIG["output_dir"]
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "plotly_template.json"
    template = {
        "layout": {
            "font": {"family": CONFIG["font_family"], "size": CONFIG["font_size"]},
            "title": {"font": {"size": CONFIG["title_size"]}},
            "colorway": CONFIG["palette"],
        }
    }
    with path.open("w", encoding="utf-8") as handle:
        json.dump(template, handle, ensure_ascii=False, indent=2)


def main():
    run_dir = load_run_dir()
    global CONFIG
    CONFIG = load_config(run_dir)
    write_mplstyle()
    write_plotly_template()
    print("[OK] Chart style package generated.")


if __name__ == "__main__":
    main()
