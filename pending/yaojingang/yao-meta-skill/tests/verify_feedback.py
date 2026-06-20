#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    tmp_root = ROOT / "tests" / "tmp_feedback"
    if tmp_root.exists():
        subprocess.run(["rm", "-rf", str(tmp_root)], check=True)
    tmp_root.mkdir(parents=True, exist_ok=True)

    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "init_skill.py"),
            "feedback-demo",
            "--description",
            "Turn repeated checklists into a reusable skill package.",
            "--output-dir",
            str(tmp_root),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    skill_dir = tmp_root / "feedback-demo"
    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "collect_feedback.py"),
            str(skill_dir),
            "--note",
            "This package needs clearer exclusions before it grows.",
            "--rating",
            "4",
            "--category",
            "boundary",
            "--recommended-action",
            "tighten-trigger",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(proc.stdout)
    assert payload["summary"]["count"] == 1, payload
    feedback_json = Path(payload["artifacts"]["json"])
    assert feedback_json.exists(), feedback_json
    stored = json.loads(feedback_json.read_text(encoding="utf-8"))
    assert stored["entries"][0]["category"] == "boundary", stored
    print(json.dumps({"ok": True}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
