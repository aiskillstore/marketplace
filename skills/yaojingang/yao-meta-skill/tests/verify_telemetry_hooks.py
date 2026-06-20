#!/usr/bin/env python3
import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
TMP = ROOT / "tests" / "tmp_telemetry_hooks"
HOOKS = ROOT / "scripts" / "render_telemetry_hook_recipes.py"
YAO = ROOT / "scripts" / "yao.py"
SENSITIVE_FLAGS = {
    "--prompt",
    "--content",
    "--input",
    "--inputs",
    "--output",
    "--outputs",
    "--transcript",
    "--message",
    "--messages",
    "--note",
    "--raw",
    "--text",
}


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


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def assert_metadata_only(argv: list[str]) -> None:
    lowered = {item.lower() for item in argv}
    assert not (lowered & SENSITIVE_FLAGS), argv


def main() -> None:
    shutil.rmtree(TMP, ignore_errors=True)
    TMP.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "init_skill.py"),
            "telemetry-hooks-demo",
            "--description",
            "Render local telemetry client hook recipes without collecting raw content.",
            "--output-dir",
            str(TMP),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    skill_dir = TMP / "telemetry-hooks-demo"
    output_json = TMP / "telemetry_hook_recipes.json"
    output_md = TMP / "telemetry_hook_recipes.md"
    spool = TMP / "client-spool.jsonl"
    rendered = run(
        [
            sys.executable,
            str(HOOKS),
            str(skill_dir),
            "--output-json",
            str(output_json),
            "--output-md",
            str(output_md),
            "--output-jsonl",
            str(spool),
        ]
    )
    assert rendered["ok"], rendered
    payload = rendered["payload"]
    assert payload["summary"]["recipe_count"] == 5, payload
    assert payload["summary"]["native_auto_capture_count"] == 0, payload
    assert payload["summary"]["metadata_only_recipe_count"] == 5, payload
    assert payload["privacy_contract"]["raw_content_allowed"] is False, payload
    assert {"browser-extension", "chrome-extension", "vscode-extension", "cli-wrapper", "provider-adapter"} == {
        item["id"] for item in payload["recipes"]
    }, payload
    assert output_json.exists(), output_json
    assert output_md.exists(), output_md
    markdown = output_md.read_text(encoding="utf-8")
    assert "Telemetry Hook Recipes" in markdown, markdown
    assert "not proof that a host client is already natively integrated" in markdown, markdown

    for recipe in payload["recipes"]:
        assert recipe["metadata_only"] is True, recipe
        assert recipe["source"] == "external", recipe
        assert recipe["integration_status"] == "client-hook-recipe", recipe
        assert recipe["emit_argv"][:3] == ["python3", "scripts/yao.py", "telemetry-emit"], recipe
        assert recipe["dry_run_argv"][-1] == "--dry-run", recipe
        assert "--command" in recipe["emit_argv"], recipe
        assert_metadata_only(recipe["emit_argv"])
        assert_metadata_only(recipe["dry_run_argv"])
        dry_run = run(recipe["dry_run_argv"])
        assert dry_run["ok"], dry_run
        assert dry_run["payload"]["dry_run"] is True, dry_run
        assert dry_run["payload"]["emitted"] is False, dry_run
    assert read_jsonl(spool) == [], spool

    browser = next(item for item in payload["recipes"] if item["id"] == "browser-extension")
    emitted = run(browser["emit_argv"])
    assert emitted["ok"], emitted
    assert emitted["payload"]["emitted"] is True, emitted
    events = read_jsonl(spool)
    assert len(events) == 1, events
    assert events[0]["command"] == "browser-extension", events
    assert events[0]["event"] == "skill_activation", events

    imported = run(payload["artifacts"]["import_argv"])
    assert imported["ok"], imported
    assert imported["payload"]["imported_count"] == 1, imported
    assert imported["payload"]["adoption_drift"]["summary"]["source_types"]["external"] == 1, imported
    assert imported["payload"]["adoption_drift"]["summary"]["command_counts"]["browser-extension"] == 1, imported

    cli_output_json = TMP / "cli_telemetry_hook_recipes.json"
    cli = run(
        [
            sys.executable,
            str(YAO),
            "telemetry-hooks",
            str(skill_dir),
            "--output-json",
            str(cli_output_json),
            "--output-jsonl",
            str(spool),
        ]
    )
    assert cli["ok"], cli
    assert cli["payload"]["summary"]["recipe_count"] == 5, cli
    assert cli_output_json.exists(), cli_output_json

    print(json.dumps({"ok": True}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
