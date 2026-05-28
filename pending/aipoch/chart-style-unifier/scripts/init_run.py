"""Initialize the running directory (chart/table style unified)

Usage:
- Run: python scripts/init_run.py

Output:
- outputs/runs/<timestamp>/config.json
- outputs/runs/<timestamp>/README.md"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

RUNS_DIR = Path("outputs/runs")

DEFAULT_CONFIG = {
    "output_dir": "outputs",
    "font_family": "Arial",
    "font_size": 9,
    "title_size": 10,
    "label_size": 9,
    "tick_size": 8,
    "line_width": 1.0,
    "marker_size": 4,
    "palette": ["#0072B2", "#D55E00", "#009E73", "#CC79A7"],
}

# Table/chart unified configuration template
TABLE_CHART_CONFIG = {
    "target_doc_path": "",  # AI fill in: full path of target document
    "font_name": "",  # AI fill in: such as "Song Dynasty" "Times New Roman"
    "font_size": None,  # AI fill in: such as 10, 12, or null (no change)
    "target_type": "table",  # AI fill in: "table" or "chart"
    "italic_numbers": False,  # AI Fill: true/false - whether to italicize numbers in tables
    "italic_chinese": False,  # AI filling: true/false - whether to italicize Chinese characters in the form
    "lowercase_letters": False,  # AI fill: true/false - whether to change the English letters in the form to lowercase
    "status": "pending",  # pending → running → done
}


def init_table_chart():
    """Initialize table/chart unified run directory"""
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = RUNS_DIR / run_id

    run_dir.mkdir(parents=True, exist_ok=True)

    # Generate configuration
    config_path = run_dir / "config.json"
    with config_path.open("w", encoding="utf-8") as handle:
        json.dump(TABLE_CHART_CONFIG, handle, ensure_ascii=False, indent=2)

    # Generate README
    readme = f"""# Run configuration - {run_id}

## fill in config.json

please AI Run after filling in the following fields：

```bash
python scripts/change_table_font.py
```

## Configuration fields

| Field | illustrate | Example |
|------|------|------|
| target_doc_path | Full path to target document | C:/Users/xxx/Desktop/xxx.docx |
| font_name | Font name | Song Dynasty / Times New Roman |
| font_size | Font size(pound) | 10 / 12 / null(Do not change) |
| target_type | Operation object | table / chart |
| italic_numbers | Table numbers italics | true / false |
| italic_chinese | Table Chinese characters italics | true / false |
"""
    (run_dir / "README.md").write_text(readme, encoding="utf-8")

    print(f"[OK] Run directory created: {run_dir}")
    print("[OK] Please edit config.json, fill in the configuration and run change_table_font.py")


def main() -> None:
    """Main entrance - supports two modes"""
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--table":
        init_table_chart()
    else:
        # Default initialization chart style configuration
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_dir = RUNS_DIR / run_id

        run_dir.mkdir(parents=True, exist_ok=True)

        config_path = run_dir / "config.json"
        with config_path.open("w", encoding="utf-8") as handle:
            json.dump(DEFAULT_CONFIG, handle, ensure_ascii=False, indent=2)

        print(f"[OK] Run directory created: {run_dir}")
        print(f"[OK] Chart style configuration has been written: {config_path}")


if __name__ == "__main__":
    main()
