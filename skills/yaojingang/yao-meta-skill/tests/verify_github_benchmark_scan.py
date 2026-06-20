#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "github_benchmark_scan.py"
FIXTURE_DIR = ROOT / "tests" / "fixtures" / "github_benchmark_scan"


def main() -> None:
    tmp_root = ROOT / "tests" / "tmp_github_benchmark_scan"
    if tmp_root.exists():
        subprocess.run(["rm", "-rf", str(tmp_root)], check=True)
    skill_dir = tmp_root / "benchmark-scan-demo"
    (skill_dir / "reports").mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(
        "---\nname: benchmark-scan-demo\ndescription: Turn rough release notes into a reusable governed skill.\n---\n\n# Benchmark Scan Demo\n",
        encoding="utf-8",
    )

    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            str(skill_dir),
            "--query",
            "release workflow evaluation portability",
            "--fixture-dir",
            str(FIXTURE_DIR),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(proc.stdout)
    assert payload["ok"], payload
    assert payload["source"] == "fixture", payload
    assert len(payload["repositories"]) == 3, payload
    assert len(payload["external_references"]) == 3, payload
    assert payload["borrow_prompt"], payload

    markdown = Path(payload["artifacts"]["markdown"]).read_text(encoding="utf-8")
    assert "## Top 3 Benchmark Repositories" in markdown, markdown[:400]
    assert "anthropics/skills" in markdown, markdown[:800]
    assert "Cross-Repo Borrow Recommendations" in markdown, markdown[:1400]

    empty_fixture = tmp_root / "empty_fixture"
    empty_fixture.mkdir(parents=True, exist_ok=True)
    (empty_fixture / "bundle.json").write_text(
        json.dumps({"search_items": [], "readmes": {}}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    empty_skill_dir = tmp_root / "benchmark-empty-demo"
    (empty_skill_dir / "reports").mkdir(parents=True, exist_ok=True)
    (empty_skill_dir / "SKILL.md").write_text(
        "---\nname: benchmark-empty-demo\ndescription: Turn a vague idea into a reusable skill.\n---\n\n# Empty Benchmark Demo\n",
        encoding="utf-8",
    )
    empty_proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            str(empty_skill_dir),
            "--query",
            "unlikely benchmark query",
            "--fixture-dir",
            str(empty_fixture),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    empty_payload = json.loads(empty_proc.stdout)
    assert empty_payload["ok"], empty_payload
    assert empty_payload["repositories"] == [], empty_payload
    assert empty_payload["cross_repo"]["borrow"] == [], empty_payload
    assert empty_payload["external_references"] == [], empty_payload
    assert empty_payload["borrow_prompt"].startswith("No benchmark suggestions"), empty_payload
    empty_markdown = Path(empty_payload["artifacts"]["markdown"]).read_text(encoding="utf-8")
    assert "No benchmark repositories were collected." in empty_markdown, empty_markdown[:600]
    assert "Review the three benchmark objects" not in empty_markdown, empty_markdown[:600]

    print(json.dumps({"ok": True}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
