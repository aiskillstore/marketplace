#!/usr/bin/env python3
import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
TMP = ROOT / "tests" / "tmp_telemetry_import"
IMPORTER = ROOT / "scripts" / "import_telemetry_events.py"
YAO = ROOT / "scripts" / "yao.py"


def run(cmd: list[str]) -> dict:
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    payload = json.loads(proc.stdout) if proc.stdout.strip() else {}
    return {
        "ok": proc.returncode == 0,
        "returncode": proc.returncode,
        "payload": payload,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n", encoding="utf-8")


def main() -> None:
    if TMP.exists():
        shutil.rmtree(TMP)
    TMP.mkdir(parents=True, exist_ok=True)

    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "init_skill.py"),
            "external-telemetry-demo",
            "--description",
            "Import external client telemetry into a reusable metadata-only drift loop.",
            "--output-dir",
            str(TMP),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    skill_dir = TMP / "external-telemetry-demo"
    input_jsonl = TMP / "external-events.jsonl"
    write_jsonl(
        input_jsonl,
        [
            {
                "event": "skill_activation",
                "activation_type": "explicit",
                "outcome": "accepted",
                "failure_type": "none",
                "timestamp": "2026-06-13T11:00:00Z",
            },
            {
                "event": "script_run",
                "activation_type": "manual",
                "outcome": "failed",
                "failure_type": "script_error",
                "timestamp": "2026-06-13T11:01:00Z",
            },
        ],
    )

    dry_run = run(
        [
            sys.executable,
            str(IMPORTER),
            str(skill_dir),
            "--input-jsonl",
            str(input_jsonl),
            "--command",
            "chrome-extension",
            "--dry-run",
        ]
    )
    assert dry_run["ok"], dry_run
    assert dry_run["payload"]["dry_run"] is True, dry_run
    assert dry_run["payload"]["candidate_count"] == 2, dry_run
    assert dry_run["payload"]["imported_count"] == 0, dry_run
    assert not (skill_dir / "reports" / "telemetry_events.jsonl").exists(), dry_run

    imported = run(
        [
            sys.executable,
            str(IMPORTER),
            str(skill_dir),
            "--input-jsonl",
            str(input_jsonl),
            "--command",
            "chrome-extension",
            "--generated-at",
            "2026-06-13T11:02:00Z",
        ]
    )
    assert imported["ok"], imported
    assert imported["payload"]["imported_count"] == 2, imported
    assert imported["payload"]["adoption_drift"]["summary"]["event_count"] == 2, imported
    assert imported["payload"]["adoption_drift"]["summary"]["source_types"]["external"] == 2, imported
    assert imported["payload"]["adoption_drift"]["summary"]["command_counts"]["chrome-extension"] == 2, imported
    events = [
        json.loads(line)
        for line in (skill_dir / "reports" / "telemetry_events.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert len(events) == 2, events
    assert {event["source"] for event in events} == {"external"}, events
    assert {event["command"] for event in events} == {"chrome-extension"}, events
    markdown = (skill_dir / "reports" / "adoption_drift_report.md").read_text(encoding="utf-8")
    assert "source=`external` command=`chrome-extension`" in markdown, markdown

    unsafe_jsonl = TMP / "unsafe-events.jsonl"
    write_jsonl(
        unsafe_jsonl,
        [
            {
                "event": "skill_activation",
                "activation_type": "explicit",
                "outcome": "accepted",
                "failure_type": "none",
                "timestamp": "2026-06-13T11:03:00Z",
            },
            {
                "event": "skill_activation",
                "activation_type": "explicit",
                "outcome": "accepted",
                "failure_type": "none",
                "prompt": "raw user prompt must never be imported",
                "timestamp": "2026-06-13T11:04:00Z",
            },
        ],
    )
    unsafe = run([sys.executable, str(IMPORTER), str(skill_dir), "--input-jsonl", str(unsafe_jsonl)])
    assert unsafe["returncode"] == 2, unsafe
    assert not unsafe["payload"]["ok"], unsafe
    assert "raw content fields" in "\n".join(unsafe["payload"]["failures"]), unsafe
    events_after_failure = (skill_dir / "reports" / "telemetry_events.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(events_after_failure) == 2, events_after_failure

    cli_input_jsonl = TMP / "cli-external-events.jsonl"
    write_jsonl(
        cli_input_jsonl,
        [
            {
                "event": "skill_output",
                "activation_type": "manual",
                "outcome": "edited",
                "failure_type": "none",
                "timestamp": "2026-06-13T11:05:00Z",
            }
        ],
    )
    cli = run(
        [
            sys.executable,
            str(YAO),
            "telemetry-import",
            str(skill_dir),
            "--input-jsonl",
            str(cli_input_jsonl),
            "--command",
            "browser-plugin",
            "--generated-at",
            "2026-06-13T11:06:00Z",
        ]
    )
    assert cli["ok"], cli
    assert cli["payload"]["imported_count"] == 1, cli
    assert cli["payload"]["adoption_drift"]["summary"]["event_count"] == 3, cli
    assert cli["payload"]["adoption_drift"]["summary"]["source_types"]["external"] == 3, cli
    assert cli["payload"]["adoption_drift"]["summary"]["command_counts"]["browser-plugin"] == 1, cli

    print(json.dumps({"ok": True}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
