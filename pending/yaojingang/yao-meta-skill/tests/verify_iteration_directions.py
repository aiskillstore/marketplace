#!/usr/bin/env python3
import json
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
        check=True,
    )
    return json.loads(proc.stdout)


def main() -> None:
    tmp_root = ROOT / "tests" / "tmp_iteration_directions"
    if tmp_root.exists():
        subprocess.run(["rm", "-rf", str(tmp_root)], check=True)
    tmp_root.mkdir(parents=True, exist_ok=True)

    init_payload = run(
        "init",
        "iteration-demo-skill",
        "--description",
        "Turn a repeated release checklist into a reusable reusable skill package.",
        "--output-dir",
        str(tmp_root),
    )
    created = Path(init_payload["root"])
    report = run("iteration-directions", str(created))
    assert report["summary"]["selection_rule"], report
    assert report["summary"]["recommended_now"], report
    assert report["summary"]["defer_for_now"], report
    assert len(report["directions"]) == 3, report
    titles = {item["title"] for item in report["directions"]}
    assert "Tighten trigger and exclusions" in titles or "Add the first execution asset" in titles, titles
    print(json.dumps({"ok": True}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
