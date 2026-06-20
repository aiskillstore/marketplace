#!/usr/bin/env python3
import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
TMP = ROOT / "tests" / "tmp_runtime_permission"
SCRIPT = ROOT / "scripts" / "probe_runtime_permissions.py"
SIMULATOR = ROOT / "scripts" / "simulate_install.py"


def run(cmd: list[str]) -> dict:
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    payload = json.loads(proc.stdout) if proc.stdout.strip() else {}
    return {
        "ok": proc.returncode == 0,
        "returncode": proc.returncode,
        "payload": payload,
        "stderr": proc.stderr,
    }


def main() -> None:
    if TMP.exists():
        shutil.rmtree(TMP)
    TMP.mkdir(parents=True, exist_ok=True)
    package_dir = TMP / "dist"

    subprocess.run([sys.executable, str(ROOT / "scripts" / "trust_check.py"), str(ROOT)], cwd=ROOT, check=True, capture_output=True, text=True)
    package = run(
        [
            sys.executable,
            str(ROOT / "scripts" / "cross_packager.py"),
            str(ROOT),
            "--platform",
            "openai",
            "--platform",
            "claude",
            "--platform",
            "generic",
            "--platform",
            "vscode",
            "--expectations",
            str(ROOT / "evals" / "packaging_expectations.json"),
            "--output-dir",
            str(package_dir),
            "--zip",
        ]
    )
    assert package["ok"], package
    install = run(
        [
            sys.executable,
            str(SIMULATOR),
            str(ROOT),
            "--package-dir",
            str(package_dir),
            "--install-root",
            str(TMP / "install-root"),
            "--output-json",
            str(TMP / "install_simulation.json"),
            "--output-md",
            str(TMP / "install_simulation.md"),
            "--generated-at",
            "2026-06-13",
        ]
    )
    assert install["ok"], install

    probe = run(
        [
            sys.executable,
            str(SCRIPT),
            str(ROOT),
            "--package-dir",
            str(package_dir),
            "--output-json",
            str(TMP / "runtime_permission_probes.json"),
            "--output-md",
            str(TMP / "runtime_permission_probes.md"),
            "--install-simulation-json",
            str(TMP / "install_simulation.json"),
        ]
    )
    assert probe["ok"], probe
    payload = probe["payload"]
    summary = payload["summary"]
    assert summary["target_count"] == 4, summary
    assert summary["pass_count"] == 4, summary
    assert summary["fail_count"] == 0, summary
    assert summary["native_enforcement_count"] == 0, summary
    assert summary["metadata_fallback_count"] == 4, summary
    assert summary["installer_enforcement_source_status"] == "present", summary
    assert summary["installer_enforcement_pass_count"] == 4, summary
    assert summary["installer_permission_enforced_count"] == 12, summary
    assert summary["installer_permission_failure_count"] == 0, summary
    assert summary["world_class_native_evidence_ready"] is False, summary
    assert summary["installer_enforcement_ready"] is True, summary
    assert summary["residual_risk_count"] == 4, summary
    assert payload["expected_capabilities"] == ["file_write", "network", "subprocess"], payload
    assert {item["assurance"] for item in payload["targets"]} == {"metadata-fallback-explicit"}, payload["targets"]
    assert all(item["installer_enforcement"]["enforced"] is True for item in payload["targets"]), payload["targets"]
    assert (TMP / "runtime_permission_probes.md").exists(), TMP

    bad_dir = TMP / "bad-dist"
    shutil.copytree(package_dir, bad_dir)
    openai_adapter = bad_dir / "targets" / "openai" / "adapter.json"
    bad_payload = json.loads(openai_adapter.read_text(encoding="utf-8"))
    bad_payload["target_permission_contract"].pop("operator_note", None)
    openai_adapter.write_text(json.dumps(bad_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    bad_probe = run(
        [
            sys.executable,
            str(SCRIPT),
            str(ROOT),
            "--package-dir",
            str(bad_dir),
            "--output-json",
            str(TMP / "bad_runtime_permission_probes.json"),
            "--output-md",
            str(TMP / "bad_runtime_permission_probes.md"),
            "--install-simulation-json",
            str(TMP / "install_simulation.json"),
        ]
    )
    assert bad_probe["returncode"] == 2, bad_probe
    assert not bad_probe["payload"]["ok"], bad_probe
    assert any("operator_note" in item for item in bad_probe["payload"]["failures"]), bad_probe["payload"]["failures"]

    print(json.dumps({"ok": True}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
