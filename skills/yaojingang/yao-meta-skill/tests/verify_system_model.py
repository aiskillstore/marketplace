#!/usr/bin/env python3
import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CLI = ROOT / "scripts" / "yao.py"


def run(*args: str) -> dict:
    proc = subprocess.run(
        [sys.executable, str(CLI), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    payload = json.loads(proc.stdout)
    return {
        "ok": proc.returncode == 0,
        "returncode": proc.returncode,
        "payload": payload,
        "stderr": proc.stderr,
    }


def main() -> None:
    tmp_root = ROOT / "tests" / "tmp_system_model"
    if tmp_root.exists():
        shutil.rmtree(tmp_root)
    tmp_root.mkdir(parents=True, exist_ok=True)

    init_result = run(
        "init",
        "system-model-demo",
        "--description",
        "Turn repeated customer research notes into a reusable insight brief skill.",
        "--output-dir",
        str(tmp_root),
        "--mode",
        "production",
        "--archetype",
        "production",
        "--intent-job",
        "Turn repeated customer research notes into reusable insight briefs.",
        "--intent-real-input",
        "interview notes",
        "--intent-real-input",
        "support tickets",
        "--intent-primary-output",
        "a concise insight brief with risks and next actions",
        "--intent-exclusion",
        "do not invent customer quotes",
        "--intent-constraint",
        "protect private customer details",
        "--intent-standard",
        "specificity over generic summary",
    )
    assert init_result["ok"], init_result
    created = Path(init_result["payload"]["root"])
    assert (created / "reports" / "system-model.md").exists(), created
    assert (created / "reports" / "system-model.json").exists(), created
    assert init_result["payload"]["artifacts"]["system_model_md"].endswith("reports/system-model.md"), init_result
    assert init_result["payload"]["system_model"]["stability"]["score"] >= 75, init_result

    payload = json.loads((created / "reports" / "system-model.json").read_text(encoding="utf-8"))
    assert payload["boundary_map"]["owned_job"].startswith("Turn repeated customer research"), payload
    assert "interview notes" in payload["boundary_map"]["input_boundary"], payload
    assert payload["feedback_loops"], payload
    assert payload["drift_watch"], payload
    assert payload["failure_pattern_map"], payload
    assert payload["leverage_points"], payload

    markdown = (created / "reports" / "system-model.md").read_text(encoding="utf-8")
    assert "System Boundary Map" in markdown, markdown[:400]
    assert "Feedback Loops" in markdown, markdown[:800]
    assert "Delay And Drift Watch" in markdown, markdown[:1200]
    assert "Highest Leverage Moves" in markdown, markdown[:1800]

    overview_html = (created / "reports" / "skill-overview.html").read_text(encoding="utf-8")
    assert "原理结构" in overview_html, overview_html[:2400]
    assert "质量评估" in overview_html, overview_html[:2600]
    assert 'aria-label="Skill principle flow"' in overview_html, overview_html[:3000]

    rerender_result = run("system-model", str(created))
    assert rerender_result["ok"], rerender_result
    assert rerender_result["payload"]["artifacts"]["markdown"].endswith("reports/system-model.md"), rerender_result
    assert rerender_result["payload"]["summary"]["leverage_points"], rerender_result

    print(json.dumps({"ok": True}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
