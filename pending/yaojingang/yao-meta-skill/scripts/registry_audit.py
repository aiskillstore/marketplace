#!/usr/bin/env python3
import argparse
import json
import re
from datetime import date
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

from skill_ir_paths import find_skill_ir as find_skill_ir_document


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REGISTRY_DIR = ROOT / "registry"
REQUIRED_PACKAGE_FIELDS = [
    "name",
    "version",
    "description",
    "targets",
    "maturity",
    "owner",
    "review_cadence",
    "trust_level",
    "license",
]


def display_path(path: Path, root: Path = ROOT) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path.resolve())


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists() or yaml is None:
        return {}
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return payload if isinstance(payload, dict) else {}


def read_frontmatter(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8", errors="replace")
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    if yaml is not None:
        payload = yaml.safe_load(parts[1]) or {}
        return payload if isinstance(payload, dict) else {}
    data: dict[str, Any] = {}
    for line in parts[1].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"')
    return data


def find_skill_ir(skill_dir: Path, name: str) -> tuple[dict[str, Any], str]:
    return find_skill_ir_document(skill_dir, name, fallback_source="missing")


def license_id(skill_dir: Path) -> str:
    for name in ("LICENSE", "LICENSE.md", "LICENSE.txt"):
        path = skill_dir / name
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if re.search(r"\bMIT License\b", text, re.IGNORECASE):
            return "MIT"
        for line in text.splitlines():
            value = line.strip()
            if value:
                return value[:80]
    return ""


def compatibility_matrix(skill_dir: Path, declared_targets: list[str]) -> dict[str, str]:
    conformance = load_json(skill_dir / "reports" / "conformance_matrix.json")
    matrix = {}
    for target in conformance.get("targets", []):
        name = str(target.get("target", ""))
        if name:
            matrix[name] = str(target.get("status", "unknown"))
    if "agent-skills-compatible" in declared_targets and "agent-skills" in matrix:
        matrix["agent-skills-compatible"] = matrix["agent-skills"]
    for target in declared_targets:
        matrix.setdefault(str(target), "missing")
    return matrix


def package_hash(skill_dir: Path) -> str:
    trust = load_json(skill_dir / "reports" / "security_trust_report.json")
    return str(trust.get("summary", {}).get("package_sha256", ""))


def package_verification(skill_dir: Path) -> dict[str, Any]:
    return load_json(skill_dir / "reports" / "package_verification.json")


def install_simulation(skill_dir: Path) -> dict[str, Any]:
    return load_json(skill_dir / "reports" / "install_simulation.json")


def adoption_drift(skill_dir: Path) -> dict[str, Any]:
    return load_json(skill_dir / "reports" / "adoption_drift_report.json")


def review_waivers(skill_dir: Path) -> dict[str, Any]:
    return load_json(skill_dir / "reports" / "review_waivers.json")


def review_annotations(skill_dir: Path) -> dict[str, Any]:
    return load_json(skill_dir / "reports" / "review_annotations.json")


def compiled_targets(skill_dir: Path) -> dict[str, Any]:
    return load_json(skill_dir / "reports" / "compiled_targets.json")


def package_targets(manifest: dict[str, Any], interface_doc: dict[str, Any], ir: dict[str, Any]) -> list[str]:
    candidates = (
        manifest.get("target_platforms")
        or ir.get("targets")
        or interface_doc.get("compatibility", {}).get("adapter_targets")
        or []
    )
    targets = []
    for item in candidates:
        value = str(item).strip()
        if value and value not in targets:
            targets.append(value)
    return targets


def build_package_metadata(skill_dir: Path, generated_at: str) -> dict[str, Any]:
    frontmatter = read_frontmatter(skill_dir / "SKILL.md")
    manifest = load_json(skill_dir / "manifest.json")
    interface_doc = load_yaml(skill_dir / "agents" / "interface.yaml")
    compatibility = interface_doc.get("compatibility", {})
    trust = compatibility.get("trust", {})
    name = str(frontmatter.get("name") or manifest.get("name") or skill_dir.name)
    ir, ir_source = find_skill_ir(skill_dir, name)
    verification = package_verification(skill_dir)
    install = install_simulation(skill_dir)
    adoption = adoption_drift(skill_dir)
    waivers = review_waivers(skill_dir)
    annotations = review_annotations(skill_dir)
    compiled = compiled_targets(skill_dir)
    archive_sha = str(verification.get("summary", {}).get("archive_sha256", ""))
    checksums = {"package_sha256": package_hash(skill_dir)}
    if archive_sha:
        checksums["archive_sha256"] = archive_sha
    description = str(
        ir.get("trigger_surface", {}).get("description")
        or frontmatter.get("description")
        or manifest.get("description")
        or ""
    )
    targets = package_targets(manifest, interface_doc, ir)
    package = {
        "schema_version": "2.0",
        "name": name,
        "version": str(manifest.get("version") or frontmatter.get("version") or ""),
        "description": description,
        "targets": targets,
        "maturity": str(manifest.get("maturity_tier") or manifest.get("lifecycle_stage") or "scaffold"),
        "owner": str(manifest.get("owner") or ""),
        "review_cadence": str(manifest.get("review_cadence") or ""),
        "trust_level": str(trust.get("source_tier") or ""),
        "license": license_id(skill_dir),
        "checksums": checksums,
        "compatibility": compatibility_matrix(skill_dir, targets),
        "source": {
            "skill_dir": display_path(skill_dir),
            "skill_ir": ir_source,
            "ir_schema_version": str(ir.get("schema_version") or "missing"),
            "canonical_metadata": "agents/interface.yaml" if (skill_dir / "agents" / "interface.yaml").exists() else "missing",
        },
        "artifacts": {
            "overview_html": "reports/skill-overview.html",
            "review_studio_html": "reports/review-studio.html",
            "trust_report": "reports/security_trust_report.md",
            "conformance_matrix": "reports/conformance_matrix.md",
            "compiled_targets": "reports/compiled_targets.md" if compiled else "",
            "package_verification": "reports/package_verification.md" if verification else "",
            "install_simulation": "reports/install_simulation.md" if install else "",
            "adoption_drift": "reports/adoption_drift_report.md" if adoption else "",
            "review_waivers": "reports/review_waivers.md" if waivers else "",
            "review_annotations": "reports/review_annotations.md" if annotations else "",
            "package_metadata": f"registry/packages/{name}.json",
        },
        "distribution": {
            "archive_verified": bool(verification.get("ok")) if verification else False,
            "archive_sha256": archive_sha,
            "package_verification": "reports/package_verification.json" if verification else "",
            "install_simulated": bool(install.get("ok")) if install else False,
            "install_simulation": "reports/install_simulation.json" if install else "",
        },
        "generated_at": generated_at,
    }
    return package


def audit_package(package: dict[str, Any], skill_dir: Path) -> tuple[list[str], list[str]]:
    failures = []
    warnings = []
    for field in REQUIRED_PACKAGE_FIELDS:
        if not package.get(field):
            failures.append(f"Missing package metadata field: {field}")
    if not package.get("checksums", {}).get("package_sha256"):
        failures.append("Missing package checksum: checksums.package_sha256")
    if package.get("source", {}).get("ir_schema_version") != "2.0.0":
        failures.append("Missing valid Skill IR source for registry package")
    compatibility = package.get("compatibility", {})
    for target in package.get("targets", []):
        if compatibility.get(target) not in {"pass", "warn"}:
            failures.append(f"Compatibility is not passing for target: {target}")
    for rel in (
        "reports/skill-overview.html",
        "reports/review-studio.html",
        "reports/compiled_targets.md",
        "reports/security_trust_report.md",
        "reports/review_waivers.md",
        "reports/review_annotations.md",
    ):
        if not (skill_dir / rel).exists():
            warnings.append(f"Recommended registry evidence is missing: {rel}")
    verification = package.get("distribution", {})
    if verification.get("package_verification") and not verification.get("archive_verified"):
        failures.append("Package verification report exists but archive verification did not pass")
    if verification.get("install_simulation") and not verification.get("install_simulated"):
        failures.append("Install simulation report exists but install simulation did not pass")
    return failures, warnings


def build_index(package: dict[str, Any], generated_at: str) -> dict[str, Any]:
    return {
        "schema_version": "2.0",
        "generated_at": generated_at,
        "package_count": 1,
        "packages": [
            {
                "name": package["name"],
                "version": package["version"],
                "maturity": package["maturity"],
                "owner": package["owner"],
                "targets": package["targets"],
                "package_metadata": package["artifacts"]["package_metadata"],
                "package_sha256": package["checksums"]["package_sha256"],
            }
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    package = report["package"]
    lines = [
        "# Registry Audit",
        "",
        f"- OK: `{report['ok']}`",
        f"- Package: `{package['name']}`",
        f"- Version: `{package['version']}`",
        f"- Maturity: `{package['maturity']}`",
        f"- Owner: `{package['owner']}`",
        f"- License: `{package['license']}`",
        f"- Package SHA256: `{package['checksums']['package_sha256']}`",
        f"- Archive SHA256: `{package['checksums'].get('archive_sha256', 'n/a')}`",
        f"- Install simulated: `{package.get('distribution', {}).get('install_simulated', False)}`",
        "",
        "## Compatibility",
        "",
        "| Target | Status |",
        "| --- | --- |",
    ]
    for target, status in package["compatibility"].items():
        lines.append(f"| `{target}` | `{status}` |")
    lines.extend(["", "## Failures", ""])
    lines.extend([f"- {item}" for item in report["failures"]] or ["- None"])
    lines.extend(["", "## Warnings", ""])
    lines.extend([f"- {item}" for item in report["warnings"]] or ["- None"])
    lines.extend(["", "## Artifacts", ""])
    for key, value in report["artifacts"].items():
        lines.append(f"- {key}: `{value}`")
    return "\n".join(lines) + "\n"


def run_registry_audit(
    skill_dir: Path,
    registry_dir: Path,
    output_json: Path,
    output_md: Path,
    generated_at: str,
) -> dict[str, Any]:
    skill_dir = skill_dir.resolve()
    registry_dir = registry_dir.resolve()
    package = build_package_metadata(skill_dir, generated_at)
    failures, warnings = audit_package(package, skill_dir)
    index = build_index(package, generated_at)

    package_dir = registry_dir / "packages"
    package_path = package_dir / f"{package['name']}.json"
    index_path = registry_dir / "index.json"
    package_dir.mkdir(parents=True, exist_ok=True)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    package_path.write_text(json.dumps(package, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    report = {
        "ok": not failures,
        "schema_version": "2.0",
        "skill_dir": display_path(skill_dir),
        "registry_dir": display_path(registry_dir),
        "package": package,
        "index": index,
        "failures": failures,
        "warnings": warnings,
        "artifacts": {
            "index": display_path(index_path),
            "package": display_path(package_path),
            "json": display_path(output_json),
            "markdown": display_path(output_md),
        },
    }
    output_json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    output_md.write_text(render_markdown(report), encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Build and audit Skill OS registry package metadata.")
    parser.add_argument("skill_dir", nargs="?", default=".")
    parser.add_argument("--registry-dir", default=str(DEFAULT_REGISTRY_DIR))
    parser.add_argument("--output-json", default="reports/registry_audit.json")
    parser.add_argument("--output-md", default="reports/registry_audit.md")
    parser.add_argument("--generated-at", default=str(date.today()))
    args = parser.parse_args()

    payload = run_registry_audit(
        Path(args.skill_dir),
        Path(args.registry_dir),
        Path(args.output_json),
        Path(args.output_md),
        args.generated_at,
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    raise SystemExit(0 if payload["ok"] else 2)


if __name__ == "__main__":
    main()
