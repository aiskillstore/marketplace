#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
CLI = SCRIPTS / "yao.py"
sys.path.insert(0, str(SCRIPTS))


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
        "payload": payload,
        "stderr": proc.stderr,
    }


def main() -> None:
    from skill_report_charts import render_chart_set
    from skill_report_model import build_report_model

    tmp_root = ROOT / "tests" / "tmp_skill_report_charts"
    if tmp_root.exists():
        subprocess.run(["rm", "-rf", str(tmp_root)], check=True)
    tmp_root.mkdir(parents=True, exist_ok=True)

    result = run(
        "init",
        "chart-demo-skill",
        "--description",
        "Create structured campaign briefs from interviews, keyword notes, and content constraints.",
        "--output-dir",
        str(tmp_root),
    )
    assert result["ok"], result
    created = tmp_root / "chart-demo-skill"

    model = build_report_model(created)
    charts = render_chart_set(model)
    for key in ("radar", "flow", "matrix", "layers", "risk_heatmap", "asset_donut", "timeline"):
        svg = charts.get(key, "")
        assert svg.startswith("<figure"), (key, svg[:200])
        assert "<svg" in svg and "</svg>" in svg, (key, svg[:400])
        assert "<figcaption>" in svg, (key, svg[:400])
        assert 'data-lang="zh-CN"' in svg and 'data-lang="en"' in svg, (key, svg[:600])
        assert "http://" not in svg and "https://" not in svg, (key, svg[:400])
        assert "data:image" not in svg, (key, svg[:400])
        if key in {"flow", "layers"}:
            assert 'fill="#F6F8FB"' in svg, (key, svg[:500])
    assert "Rating Radar" in charts["radar"], charts["radar"][:900]
    assert "Delivery Flow" in charts["flow"], charts["flow"][:900]
    assert "The radar chart compares" in charts["radar"], charts["radar"][-500:]

    print(json.dumps({"ok": True}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
