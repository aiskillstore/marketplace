#!/usr/bin/env python3
import json
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
TMP = ROOT / "tests" / "tmp_install_simulation"
PACKAGER = ROOT / "scripts" / "cross_packager.py"
SIMULATOR = ROOT / "scripts" / "simulate_install.py"
EXPECTATIONS = ROOT / "evals" / "packaging_expectations.json"


def run(cmd: list[str]) -> dict:
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    payload = {}
    if proc.stdout.strip():
        payload = json.loads(proc.stdout)
    return {
        "ok": proc.returncode == 0,
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "payload": payload,
    }


def build_package(out_dir: Path, skill_root: Path = ROOT) -> dict:
    return run(
        [
            sys.executable,
            str(PACKAGER),
            str(skill_root),
            "--platform",
            "openai",
            "--platform",
            "claude",
            "--platform",
            "generic",
            "--platform",
            "vscode",
            "--expectations",
            str(EXPECTATIONS),
            "--output-dir",
            str(out_dir),
            "--zip",
        ]
    )


def simulate(package_dir: Path, output_json: Path, output_md: Path, skill_root: Path = ROOT) -> dict:
    return run(
        [
            sys.executable,
            str(SIMULATOR),
            str(skill_root),
            "--package-dir",
            str(package_dir),
            "--install-root",
            str(TMP / "install-root"),
            "--output-json",
            str(output_json),
            "--output-md",
            str(output_md),
            "--generated-at",
            "2026-06-13",
        ]
    )


def rewrite_archive_json(package_dir: Path, relative_path: str, transform) -> None:
    archive_path = package_dir / "yao-meta-skill.zip"
    rewritten_path = package_dir / "yao-meta-skill.rewritten.zip"
    archive_member = f"yao-meta-skill/{relative_path}"
    replaced = False
    with zipfile.ZipFile(archive_path) as archive_in, zipfile.ZipFile(rewritten_path, "w", compression=zipfile.ZIP_DEFLATED) as archive_out:
        for info in archive_in.infolist():
            data = archive_in.read(info.filename)
            if info.filename == archive_member:
                payload = json.loads(data.decode("utf-8"))
                data = (json.dumps(transform(payload), ensure_ascii=False, indent=2) + "\n").encode("utf-8")
                replaced = True
            archive_out.writestr(info, data)
    assert replaced, archive_member
    rewritten_path.replace(archive_path)


def main() -> None:
    if TMP.exists():
        shutil.rmtree(TMP)
    TMP.mkdir(parents=True, exist_ok=True)

    valid_dir = TMP / "dist"
    build = build_package(valid_dir)
    assert build["ok"], build
    valid = simulate(valid_dir, TMP / "install_simulation.json", TMP / "install_simulation.md")
    payload = valid["payload"]
    assert valid["ok"], valid
    assert payload["ok"], payload
    assert payload["summary"]["archive_extracted"], payload
    assert payload["summary"]["entrypoint_loaded"], payload
    assert payload["summary"]["manifest_loaded"], payload
    assert payload["summary"]["interface_loaded"], payload
    assert payload["summary"]["adapter_count"] == 4, payload
    assert payload["summary"]["installer_permission_enforced_count"] == 12, payload
    assert payload["summary"]["installer_permission_failure_count"] == 0, payload
    assert payload["summary"]["permission_target_count"] == 4, payload
    assert payload["summary"]["permission_capability_count"] == 3, payload
    assert not payload["failures"], payload
    valid_markdown = (TMP / "install_simulation.md").read_text(encoding="utf-8")
    assert "Install Simulation" in valid_markdown
    assert "Installer permissions enforced" in valid_markdown

    with tempfile.TemporaryDirectory(prefix="renamed-install-root-") as temp_root:
        renamed_root = Path(temp_root) / "checkout-alias"
        shutil.copytree(
            ROOT,
            renamed_root,
            ignore=shutil.ignore_patterns(".git", ".previews", "dist", "__pycache__", ".pytest_cache", "tmp*"),
        )
        renamed_dir = TMP / "renamed-dist"
        renamed_build = build_package(renamed_dir, renamed_root)
        assert renamed_build["ok"], renamed_build
        assert (renamed_dir / "yao-meta-skill.zip").exists(), renamed_build
        renamed_valid = simulate(renamed_dir, TMP / "renamed_install_simulation.json", TMP / "renamed_install_simulation.md", renamed_root)
        assert renamed_valid["ok"], renamed_valid
        assert renamed_valid["payload"]["summary"]["archive_extracted"], renamed_valid
        assert renamed_valid["payload"]["installed_skill_dir"].endswith("simulate-yao-meta-skill/yao-meta-skill"), renamed_valid

    policy_gap_dir = TMP / "policy-gap-dist"
    shutil.copytree(valid_dir, policy_gap_dir)

    def remove_vscode_network_enforcement(payload: dict) -> dict:
        payload["capabilities"]["network"]["target_enforcement"].pop("vscode", None)
        return payload

    rewrite_archive_json(policy_gap_dir, "security/permission_policy.json", remove_vscode_network_enforcement)
    policy_gap = simulate(policy_gap_dir, TMP / "policy_gap.json", TMP / "policy_gap.md")
    policy_gap_payload = policy_gap["payload"]
    assert policy_gap["returncode"] == 2, policy_gap
    assert not policy_gap_payload["ok"], policy_gap_payload
    assert policy_gap_payload["summary"]["installer_permission_enforced_count"] == 11, policy_gap_payload
    assert policy_gap_payload["summary"]["installer_permission_failure_count"] >= 1, policy_gap_payload
    assert any("vscode capability network has target enforcement note" in item for item in policy_gap_payload["failures"]), policy_gap_payload

    unsafe_dir = TMP / "unsafe-dist"
    shutil.copytree(valid_dir, unsafe_dir)
    with zipfile.ZipFile(unsafe_dir / "yao-meta-skill.zip", "a", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("../evil.txt", "bad")
    unsafe = simulate(unsafe_dir, TMP / "unsafe.json", TMP / "unsafe.md")
    unsafe_payload = unsafe["payload"]
    assert unsafe["returncode"] == 2, unsafe
    assert not unsafe_payload["ok"], unsafe_payload
    assert any("Archive has no absolute or parent-traversal entries" in item for item in unsafe_payload["failures"]), unsafe_payload

    print(json.dumps({"ok": True}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
