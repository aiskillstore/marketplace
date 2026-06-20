#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "render_baseline_compare.py"


def main() -> None:
    output_json = ROOT / "tests" / "tmp_baseline_compare.json"
    output_md = ROOT / "tests" / "tmp_baseline_compare.md"
    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--entry",
            f"root::{ROOT / 'reports' / 'description_optimization.json'}",
            "--entry",
            f"team-frontend-review::{ROOT / 'examples' / 'team-frontend-review' / 'optimization' / 'reports' / 'description_optimization.json'}",
            "--entry",
            f"governed-incident-command::{ROOT / 'examples' / 'governed-incident-command' / 'optimization' / 'reports' / 'description_optimization.json'}",
            "--output-json",
            str(output_json),
            "--output-md",
            str(output_md),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(proc.stdout)
    assert payload["summary"]["target_count"] == 3, payload
    assert output_json.exists(), output_json
    assert output_md.exists(), output_md
    assert "Target Breakdown" in output_md.read_text(encoding="utf-8")
    output_json.unlink(missing_ok=True)
    output_md.unlink(missing_ok=True)
    print(json.dumps({"ok": True}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
