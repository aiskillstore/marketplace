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


def assert_metric(metric: dict) -> None:
    assert isinstance(metric.get("score"), int), metric
    assert 0 <= metric["score"] <= 100, metric
    assert metric.get("label"), metric
    assert metric.get("reasons"), metric
    assert all(isinstance(reason, str) and reason for reason in metric["reasons"]), metric


def main() -> None:
    from skill_report_metrics import calculate_scorecard

    tmp_root = ROOT / "tests" / "tmp_skill_report_metrics"
    if tmp_root.exists():
        subprocess.run(["rm", "-rf", str(tmp_root)], check=True)
    tmp_root.mkdir(parents=True, exist_ok=True)

    result = run(
        "init",
        "metric-demo-skill",
        "--description",
        "Turn customer research notes into a reusable strategy brief skill.",
        "--output-dir",
        str(tmp_root),
    )
    assert result["ok"], result
    created = tmp_root / "metric-demo-skill"

    scorecard = calculate_scorecard(created)
    expected_keys = {
        "completeness_score",
        "trigger_score",
        "evidence_score",
        "maintainability_score",
        "portability_score",
        "context_cost",
    }
    assert expected_keys.issubset(scorecard.keys()), scorecard
    for key in expected_keys:
        assert_metric(scorecard[key])

    assert scorecard["completeness_score"]["score"] >= 70, scorecard
    assert scorecard["trigger_score"]["score"] >= 50, scorecard
    assert any("SKILL.md" in reason for reason in scorecard["completeness_score"]["reasons"]), scorecard

    sparse_root = tmp_root / "sparse-skill"
    sparse_root.mkdir()
    (sparse_root / "SKILL.md").write_text(
        "---\nname: sparse-skill\ndescription: Sparse demo.\n---\n\n# Sparse Skill\n",
        encoding="utf-8",
    )
    sparse_scorecard = calculate_scorecard(sparse_root)
    assert sparse_scorecard["evidence_score"]["score"] < scorecard["evidence_score"]["score"], sparse_scorecard
    assert any("证据不足" in reason for reason in sparse_scorecard["evidence_score"]["reasons"]), sparse_scorecard

    print(json.dumps({"ok": True}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
