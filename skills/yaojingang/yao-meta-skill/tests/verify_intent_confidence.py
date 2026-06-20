#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "render_intent_confidence.py"


def main() -> None:
    tmp_root = ROOT / "tests" / "tmp_intent_confidence"
    if tmp_root.exists():
        subprocess.run(["rm", "-rf", str(tmp_root)], check=True)
    skill_dir = tmp_root / "intent-confidence-demo"
    (skill_dir / "reports").mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(
        "---\nname: intent-confidence-demo\ndescription: Turn repeated incident notes into a reusable incident packet.\n---\n\n# Intent Confidence Demo\n",
        encoding="utf-8",
    )
    context_path = skill_dir / "reports" / "context.json"
    context_path.write_text(
        json.dumps(
            {
                "job": "Turn repeated incident notes into a reusable incident packet.",
                "real_inputs": ["incident notes", "chat timeline"],
                "primary_output": "A reusable incident command packet.",
                "description": "Turn repeated incident notes into a reusable incident packet. Primary output: A reusable incident command packet.",
                "exclusions": ["Do not draft external PR statements."],
                "constraints": ["auditability", "portability"],
                "standards": ["consistency"],
                "correction": "",
                "user_references": ["A trusted incident workflow"],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            str(skill_dir),
            "--context-json",
            str(context_path),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(proc.stdout)
    assert payload["summary"]["gate_passed"], payload
    assert payload["summary"]["score"] >= 70, payload
    markdown = Path(payload["artifacts"]["markdown"]).read_text(encoding="utf-8")
    assert "Intent Confidence" in markdown, markdown[:200]
    assert "Follow-Up Questions" in markdown, markdown[:500]
    print(json.dumps({"ok": True}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
