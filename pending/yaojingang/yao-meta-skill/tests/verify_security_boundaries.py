#!/usr/bin/env python3
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parent.parent
TMP = ROOT / "tests" / "tmp_security"
CROSS_PACKAGER = ROOT / "scripts" / "cross_packager.py"
INIT_SKILL = ROOT / "scripts" / "init_skill.py"
CHECK_UPDATE = ROOT / "scripts" / "check_update.py"


def run(cmd: list[str]) -> dict:
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    payload = {}
    if proc.stdout.strip():
        payload = json.loads(proc.stdout)
    return {
        "returncode": proc.returncode,
        "ok": proc.returncode == 0,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "payload": payload,
    }


def write_skill(root: Path, *, interface_extra: str = "") -> Path:
    skill = root / "secure-demo"
    (skill / "agents").mkdir(parents=True, exist_ok=True)
    (skill / "SKILL.md").write_text(
        "---\nname: secure-demo\ndescription: Secure demo skill.\n---\n\n# Secure Demo\n",
        encoding="utf-8",
    )
    interface_text = f"""interface:
  display_name: "Secure Demo"
  short_description: "Safe package demo"
  default_prompt: "Use this demo."
compatibility:
  canonical_format: "agent-skills"
  adapter_targets:
    - "openai"
    - "generic"
  activation:
    mode: "manual"
    paths: []
  execution:
    context: "inline"
    shell: "bash"
  trust:
    source_tier: "local"
    remote_inline_execution: "forbid"
    remote_metadata_policy: "allow-metadata-only"
  degradation:
    openai: "metadata-adapter"
    generic: "neutral-source"
{interface_extra}"""
    (skill / "agents" / "interface.yaml").write_text(interface_text, encoding="utf-8")
    return skill


def test_dangerous_output_dir() -> dict:
    skill = write_skill(TMP / "dangerous-output")
    result = run(
        [
            sys.executable,
            str(CROSS_PACKAGER),
            str(skill),
            "--platform",
            "generic",
            "--output-dir",
            str(ROOT),
        ]
    )
    passed = result["returncode"] == 2 and "Refusing dangerous output directory" in result["stdout"]
    return {"name": "dangerous_output_dir_rejected", "passed": passed, **result}


def test_zip_skips_symlink() -> dict:
    case_root = TMP / "symlink-zip"
    skill = write_skill(case_root)
    outside_secret = case_root / "outside-secret.txt"
    outside_secret.write_text("SECRET_FROM_OUTSIDE", encoding="utf-8")
    (skill / "linked-secret.txt").symlink_to(outside_secret)
    out_dir = case_root / "dist"
    result = run(
        [
            sys.executable,
            str(CROSS_PACKAGER),
            str(skill),
            "--platform",
            "generic",
            "--output-dir",
            str(out_dir),
            "--zip",
        ]
    )
    zip_path = out_dir / "secure-demo.zip"
    leaked = False
    contains_link = False
    if zip_path.exists():
        with zipfile.ZipFile(zip_path) as zf:
            for name in zf.namelist():
                if name.endswith("linked-secret.txt"):
                    contains_link = True
                    leaked = zf.read(name).decode("utf-8") == "SECRET_FROM_OUTSIDE"
    passed = result["ok"] and not contains_link and not leaked
    return {"name": "zip_skips_symlink", "passed": passed, "contains_link": contains_link, "leaked": leaked, **result}


def test_output_dir_symlink_rejected() -> dict:
    case_root = TMP / "symlink-output"
    skill = write_skill(case_root)
    real_out = case_root / "real-output"
    real_out.mkdir(parents=True)
    symlink_out = case_root / "linked-output"
    symlink_out.symlink_to(real_out, target_is_directory=True)
    result = run(
        [
            sys.executable,
            str(CROSS_PACKAGER),
            str(skill),
            "--platform",
            "generic",
            "--output-dir",
            str(symlink_out),
        ]
    )
    passed = result["returncode"] == 2 and "Refusing symlink output directory" in result["stdout"]
    return {"name": "output_dir_symlink_rejected", "passed": passed, **result}


def test_init_rejects_path_traversal() -> dict:
    case_root = TMP / "init-traversal"
    output_dir = case_root / "container"
    outside = case_root / "outside-target"
    result = run(
        [
            sys.executable,
            str(INIT_SKILL),
            "../outside-target",
            "--description",
            "Traversal demo.",
            "--output-dir",
            str(output_dir),
        ]
    )
    passed = result["returncode"] == 2 and not outside.exists() and "Invalid skill name" in result["stdout"]
    return {"name": "init_rejects_path_traversal", "passed": passed, "outside_exists": outside.exists(), **result}


def test_update_rejects_file_url() -> dict:
    remote_version = TMP / "remote-version.txt"
    remote_version.write_text("9.9.9\n", encoding="utf-8")
    result = run(
        [
            sys.executable,
            str(CHECK_UPDATE),
            "--force",
            "--no-cache",
            "--version-url",
            remote_version.as_uri(),
            "--manifest-url",
            remote_version.as_uri(),
        ]
    )
    passed = result["returncode"] == 2 and "Update URL scheme is not allowed: file" in result["stdout"]
    return {"name": "update_rejects_file_url", "passed": passed, **result}


def test_openai_yaml_uses_safe_dump() -> dict:
    case_root = TMP / "safe-yaml"
    skill = write_skill(case_root)
    interface_path = skill / "agents" / "interface.yaml"
    payload = yaml.safe_load(interface_path.read_text(encoding="utf-8"))
    payload["interface"]["display_name"] = 'Quoted "Demo"\nSecond line'
    payload["interface"]["default_prompt"] = 'Use "quotes" and:\n- preserve YAML'
    interface_path.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8")
    out_dir = case_root / "dist"
    result = run(
        [
            sys.executable,
            str(CROSS_PACKAGER),
            str(skill),
            "--platform",
            "openai",
            "--output-dir",
            str(out_dir),
        ]
    )
    generated_yaml = out_dir / "targets" / "openai" / "agents" / "openai.yaml"
    parsed = yaml.safe_load(generated_yaml.read_text(encoding="utf-8")) if generated_yaml.exists() else {}
    passed = (
        result["ok"]
        and parsed.get("interface", {}).get("display_name") == payload["interface"]["display_name"]
        and parsed.get("interface", {}).get("default_prompt") == payload["interface"]["default_prompt"]
    )
    return {"name": "openai_yaml_uses_safe_dump", "passed": passed, "parsed": parsed, **result}


def main() -> None:
    if TMP.exists():
        shutil.rmtree(TMP)
    TMP.mkdir(parents=True, exist_ok=True)
    cases = [
        test_dangerous_output_dir(),
        test_zip_skips_symlink(),
        test_output_dir_symlink_rejected(),
        test_init_rejects_path_traversal(),
        test_update_rejects_file_url(),
        test_openai_yaml_uses_safe_dump(),
    ]
    report = {"ok": all(case["passed"] for case in cases), "cases": cases}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not report["ok"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
