#!/usr/bin/env python3
import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "render_review_annotations.py"
STUDIO = ROOT / "scripts" / "render_review_studio.py"


def run(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=check,
    )


def main() -> None:
    tmp_root = ROOT / "tests" / "tmp_review_annotations"
    if tmp_root.exists():
        shutil.rmtree(tmp_root)
    tmp_root.mkdir(parents=True, exist_ok=True)

    empty_json = tmp_root / "empty.json"
    empty_md = tmp_root / "empty.md"
    empty_proc = run(str(ROOT), "--output-json", str(empty_json), "--output-md", str(empty_md))
    empty_payload = json.loads(empty_proc.stdout)
    assert empty_payload["ok"], empty_payload
    assert empty_payload["summary"]["annotation_count"] == 0, empty_payload
    assert empty_payload["summary"]["open_blocker_count"] == 0, empty_payload
    assert "No reviewer annotations recorded yet." in empty_md.read_text(encoding="utf-8"), empty_md

    source_json = tmp_root / "review_annotations_input.json"
    template_proc = run(
        str(ROOT),
        "--annotations-json",
        str(source_json),
        "--output-json",
        str(tmp_root / "template.json"),
        "--output-md",
        str(tmp_root / "template.md"),
        "--write-template",
    )
    template_payload = json.loads(template_proc.stdout)
    assert template_payload["ok"], template_payload
    assert template_payload["template_written"], template_payload
    assert source_json.exists(), source_json

    warning_json = tmp_root / "warning.json"
    warning_md = tmp_root / "warning.md"
    add_proc = run(
        str(ROOT),
        "--annotations-json",
        str(source_json),
        "--output-json",
        str(warning_json),
        "--output-md",
        str(warning_md),
        "--add-annotation",
        "--annotation-id",
        "ann-output-1",
        "--gate-key",
        "output-lab",
        "--target-path",
        "reports/output_quality_scorecard.md",
        "--line",
        "1",
        "--severity",
        "warning",
        "--reviewer",
        "Yao QA",
        "--created-at",
        "2026-06-13",
        "--body",
        "Clarify whether the output evidence is recorded-fixture or model-executed.",
        "--suggested-action",
        "Open reports/output_execution_runs.md before release wording.",
    )
    warning_payload = json.loads(add_proc.stdout)
    assert warning_payload["ok"], warning_payload
    assert warning_payload["summary"]["annotation_count"] == 1, warning_payload
    assert warning_payload["summary"]["open_warning_count"] == 1, warning_payload
    annotation = warning_payload["annotations"][0]
    assert annotation["target_exists"], annotation
    assert annotation["source_excerpt"], annotation
    assert "ann-output-1" in warning_md.read_text(encoding="utf-8"), warning_md

    blocker_source = tmp_root / "blocker_input.json"
    blocker_source.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "annotations": [
                    {
                        "id": "ann-release-blocker",
                        "gate_key": "release-notes",
                        "target_path": "reports/skill-os-2-review.md",
                        "line": 1,
                        "severity": "blocker",
                        "status": "open",
                        "reviewer": "Yao QA",
                        "created_at": "2026-06-13",
                        "body": "Release narrative needs one reviewer pass before publish.",
                    }
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    blocker_json = ROOT / "reports" / "review_annotations.json"
    blocker_md = ROOT / "reports" / "review_annotations.md"
    original_json = blocker_json.read_text(encoding="utf-8") if blocker_json.exists() else None
    original_md = blocker_md.read_text(encoding="utf-8") if blocker_md.exists() else None
    try:
        blocker_proc = run(
            str(ROOT),
            "--annotations-json",
            str(blocker_source),
            "--output-json",
            str(blocker_json),
            "--output-md",
            str(blocker_md),
        )
        blocker_payload = json.loads(blocker_proc.stdout)
        assert blocker_payload["ok"], blocker_payload
        assert blocker_payload["summary"]["open_blocker_count"] == 1, blocker_payload

        studio_json = tmp_root / "review-studio-blocked.json"
        studio_html = tmp_root / "review-studio-blocked.html"
        studio_proc = subprocess.run(
            [
                sys.executable,
                str(STUDIO),
                str(ROOT),
                "--output-html",
                str(studio_html),
                "--output-json",
                str(studio_json),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        studio_payload = json.loads(studio_proc.stdout)
        assert studio_payload["summary"]["decision"] == "blocked", studio_payload
        assert studio_payload["summary"]["open_annotation_blocker_count"] == 1, studio_payload
        html = studio_html.read_text(encoding="utf-8")
        assert "审查批注" in html, html[:4000]
        assert "ann-release-blocker" in html, html
    finally:
        if original_json is None:
            blocker_json.unlink(missing_ok=True)
        else:
            blocker_json.write_text(original_json, encoding="utf-8")
        if original_md is None:
            blocker_md.unlink(missing_ok=True)
        else:
            blocker_md.write_text(original_md, encoding="utf-8")

    invalid_proc = run(
        str(ROOT),
        "--annotations-json",
        str(tmp_root / "invalid_input.json"),
        "--output-json",
        str(tmp_root / "invalid.json"),
        "--output-md",
        str(tmp_root / "invalid.md"),
        "--add-annotation",
        "--gate-key",
        "output-lab",
        "--target-path",
        "../outside.md",
        "--body",
        "This path must be rejected.",
        check=False,
    )
    assert invalid_proc.returncode == 2, invalid_proc.stdout
    invalid_payload = json.loads(invalid_proc.stdout)
    assert not invalid_payload["ok"], invalid_payload
    assert "escapes skill directory" in "\n".join(invalid_payload["failures"]), invalid_payload
    assert not (tmp_root / "invalid_input.json").exists(), invalid_payload

    print(json.dumps({"ok": True}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
