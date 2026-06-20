#!/usr/bin/env python3
import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "render_world_class_claim_guard.py"
TMP = ROOT / "tests" / "tmp_world_class_claim_guard"
sys.path.insert(0, str(ROOT / "scripts"))
from render_world_class_claim_guard import default_claim_surfaces, rel_path  # noqa: E402


def run_guard(*extra: str, check: bool = True, cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            str(ROOT),
            "--generated-at",
            "2026-06-14",
            *extra,
        ],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=check,
    )


def main() -> None:
    shutil.rmtree(TMP, ignore_errors=True)
    TMP.mkdir(parents=True, exist_ok=True)
    output_json = TMP / "world_class_claim_guard.json"
    output_md = TMP / "world_class_claim_guard.md"
    proc = run_guard("--output-json", str(output_json), "--output-md", str(output_md))
    payload = json.loads(proc.stdout)
    assert payload["schema_version"] == "1.0", payload
    assert payload["ok"] is True, payload
    summary = payload["summary"]
    assert summary["decision"] == "claim-guard-pass-evidence-pending", summary
    assert summary["ledger_ready_to_claim_world_class"] is False, summary
    assert summary["ledger_pending_count"] == 4, summary
    assert summary["claim_surface_count"] >= 10, summary
    assert summary["json_claim_surface_count"] >= 10, summary
    assert summary["metadata_claim_surface_count"] >= summary["json_claim_surface_count"], summary
    assert summary["package_claim_surface_count"] >= 5, summary
    assert summary["violation_count"] == 0, summary
    assert summary["overclaim_guard_active"] is True, summary
    assert any(item["path"] == "README.md" for item in payload["scanned_surfaces"]), payload["scanned_surfaces"]
    assert any(item["path"] == "manifest.json" for item in payload["scanned_surfaces"]), payload["scanned_surfaces"]
    assert any(item["path"] == "evidence/world_class/README.md" for item in payload["scanned_surfaces"]), payload[
        "scanned_surfaces"
    ]
    assert any(item["path"] == "agents/interface.yaml" for item in payload["scanned_surfaces"]), payload[
        "scanned_surfaces"
    ]
    assert any(item["path"] == "security/permission_policy.json" for item in payload["scanned_surfaces"]), payload[
        "scanned_surfaces"
    ]
    assert not any(
        item["path"].startswith("dist/install-simulation/") for item in payload["scanned_surfaces"]
    ), payload["scanned_surfaces"]
    assert any(item["path"] == "reports/world_class_evidence_ledger.json" for item in payload["scanned_surfaces"]), payload["scanned_surfaces"]

    surface_fixture = TMP / "surface-fixture"
    for rel in [
        "README.md",
        "SKILL.md",
        "manifest.json",
        "agents/interface.yaml",
        "dist/manifest.json",
        "dist/targets/openai/adapter.json",
        "dist/install-simulation/simulate-skill/SKILL.md",
        "security/permission_policy.json",
        "evidence/world_class/README.md",
        "evidence/world_class/submissions/provider-holdout.json",
    ]:
        target = surface_fixture / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("{}\n" if target.suffix == ".json" else "fixture\n", encoding="utf-8")
    fixture_surfaces = {rel_path(path, surface_fixture) for path in default_claim_surfaces(surface_fixture)}
    assert "dist/manifest.json" in fixture_surfaces, fixture_surfaces
    assert "dist/targets/openai/adapter.json" in fixture_surfaces, fixture_surfaces
    assert "dist/install-simulation/simulate-skill/SKILL.md" not in fixture_surfaces, fixture_surfaces
    assert "evidence/world_class/submissions/provider-holdout.json" not in fixture_surfaces, fixture_surfaces

    markdown = output_md.read_text(encoding="utf-8")
    assert "World-Class Claim Guard" in markdown, markdown
    assert "claim-guard-pass-evidence-pending" in markdown, markdown
    assert "world-class evidence ledger" in markdown, markdown
    assert "JSON claim surfaces scanned" in markdown, markdown
    assert "metadata claim surfaces scanned" in markdown, markdown
    assert "package/runtime claim surfaces scanned" in markdown, markdown

    safe_surface = TMP / "safe.md"
    safe_surface.write_text("ready to claim world-class: `false`\nworld-class evidence is pending.\n", encoding="utf-8")
    safe_proc = run_guard(
        "--claim-surface", str(safe_surface),
        "--output-json", str(TMP / "safe_guard.json"),
        "--output-md", str(TMP / "safe_guard.md"),
        check=True,
    )
    safe_payload = json.loads(safe_proc.stdout)
    assert safe_payload["summary"]["violation_count"] == 0, safe_payload

    unsafe_surface = TMP / "unsafe.md"
    unsafe_surface.write_text("ready to claim world-class: `true`\n世界级已完成\n", encoding="utf-8")
    unsafe_proc = run_guard(
        "--claim-surface", str(unsafe_surface),
        "--output-json", str(TMP / "unsafe_guard.json"),
        "--output-md", str(TMP / "unsafe_guard.md"),
        check=False,
    )
    assert unsafe_proc.returncode == 2, unsafe_proc.stdout
    unsafe_payload = json.loads(unsafe_proc.stdout)
    assert unsafe_payload["ok"] is False, unsafe_payload
    assert unsafe_payload["summary"]["decision"] == "claim-blocked-overclaim", unsafe_payload
    assert unsafe_payload["summary"]["violation_count"] == 2, unsafe_payload
    rules = {item["rule"] for item in unsafe_payload["violations"]}
    assert {"ready-to-claim-true", "zh-completion-phrase"} <= rules, unsafe_payload["violations"]

    relative_unsafe_surface = TMP / "relative-unsafe.md"
    relative_unsafe_surface.write_text("world-class completed\n", encoding="utf-8")
    relative_proc = run_guard(
        "--claim-surface",
        relative_unsafe_surface.relative_to(ROOT).as_posix(),
        "--output-json",
        str(TMP / "relative_unsafe_guard.json"),
        "--output-md",
        str(TMP / "relative_unsafe_guard.md"),
        check=False,
        cwd=TMP,
    )
    assert relative_proc.returncode == 2, relative_proc.stdout
    relative_payload = json.loads(relative_proc.stdout)
    assert relative_payload["summary"]["violation_count"] == 1, relative_payload
    assert relative_payload["violations"][0]["path"] == "tests/tmp_world_class_claim_guard/relative-unsafe.md", relative_payload

    unsafe_json_surface = TMP / "unsafe.json"
    unsafe_json_surface.write_text('{"world_class_ready": true}\n', encoding="utf-8")
    unsafe_json_proc = run_guard(
        "--claim-surface",
        str(unsafe_json_surface),
        "--output-json",
        str(TMP / "unsafe_json_guard.json"),
        "--output-md",
        str(TMP / "unsafe_json_guard.md"),
        check=False,
    )
    assert unsafe_json_proc.returncode == 2, unsafe_json_proc.stdout
    unsafe_json_payload = json.loads(unsafe_json_proc.stdout)
    assert unsafe_json_payload["summary"]["violation_count"] == 1, unsafe_json_payload
    assert unsafe_json_payload["violations"][0]["rule"] == "json-world-class-ready-true", unsafe_json_payload
    print(json.dumps({"ok": True}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
