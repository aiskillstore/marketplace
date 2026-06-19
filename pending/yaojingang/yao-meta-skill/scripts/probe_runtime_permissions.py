#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


DEFAULT_TARGETS = ["openai", "claude", "generic", "vscode"]


def display_path(path: Path, root: Path) -> str:
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
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        return {}
    return payload if isinstance(payload, dict) else {}


def expected_capabilities(skill_dir: Path) -> list[str]:
    trust = load_json(skill_dir / "reports" / "security_trust_report.json")
    governance = trust.get("permission_governance", {}) if isinstance(trust.get("permission_governance"), dict) else {}
    required = governance.get("required_capabilities", [])
    if isinstance(required, list) and required:
        return sorted(str(item) for item in required)
    summary = trust.get("summary", {}) if isinstance(trust.get("summary"), dict) else {}
    candidates = []
    if int(summary.get("network_script_count", 0) or 0):
        candidates.append("network")
    if int(summary.get("file_write_script_count", 0) or 0):
        candidates.append("file_write")
    if any(item.get("uses_subprocess") for item in trust.get("scripts", []) if isinstance(item, dict)):
        candidates.append("subprocess")
    if int(summary.get("interactive_script_count", 0) or 0):
        candidates.append("interactive")
    return sorted(candidates)


def add_check(checks: list[dict[str, Any]], failures: list[str], key: str, condition: bool, detail: str) -> None:
    checks.append({"key": key, "passed": condition, "detail": detail})
    if not condition:
        failures.append(detail)


def sorted_strings(value: Any) -> list[str]:
    return sorted(str(item) for item in value) if isinstance(value, list) else []


def check_index(checks: list[Any]) -> dict[str, str]:
    indexed: dict[str, str] = {}
    for item in checks:
        if not isinstance(item, dict):
            continue
        check_id = str(item.get("id") or item.get("key") or "").strip()
        status = str(item.get("status") or ("pass" if item.get("passed") is True else "")).strip()
        if check_id:
            indexed[check_id] = status
    return indexed


def installer_enforcement_source(
    skill_dir: Path,
    package_dir: Path,
    targets: list[str],
    expected: list[str],
    install_simulation_path: Path | None,
) -> dict[str, Any]:
    path = install_simulation_path or skill_dir / "reports" / "install_simulation.json"
    report = load_json(path)
    source_display = display_path(path, skill_dir)
    if not path.exists() or not report:
        return {
            "source": source_display,
            "source_status": "missing",
            "package_dir_matches": False,
            "summary": {},
            "targets": {
                target: {
                    "target": target,
                    "source_status": "missing",
                    "enforced": False,
                    "enforced_capabilities": [],
                    "missing_capabilities": expected,
                    "failure_details": ["install simulation report is missing"],
                }
                for target in targets
            },
        }

    expected_package_dir = display_path(package_dir, skill_dir)
    observed_package_dir = str(report.get("package_dir", "")).strip()
    package_matches = observed_package_dir in {expected_package_dir, str(package_dir)}
    summary = report.get("summary", {}) if isinstance(report.get("summary"), dict) else {}
    if not package_matches:
        source_status = "package-mismatch"
    else:
        source_status = "present"

    indexed = check_index(report.get("checks", []) if isinstance(report.get("checks"), list) else [])
    target_results: dict[str, Any] = {}
    for target in targets:
        enforced_capabilities = []
        missing_capabilities = []
        failure_details = []
        for capability in expected:
            approval_id = f"permission-{target}-{capability}-approved"
            enforcement_id = f"permission-{target}-{capability}-target-enforcement"
            approval_ok = indexed.get(approval_id) == "pass"
            enforcement_ok = indexed.get(enforcement_id) == "pass"
            if source_status == "present" and approval_ok and enforcement_ok:
                enforced_capabilities.append(capability)
            else:
                missing_capabilities.append(capability)
                if source_status == "present" and not approval_ok:
                    failure_details.append(f"{approval_id} did not pass")
                if source_status == "present" and not enforcement_ok:
                    failure_details.append(f"{enforcement_id} did not pass")
        if source_status == "package-mismatch":
            failure_details.append(
                f"install simulation package_dir {observed_package_dir or 'missing'} does not match probed package_dir {expected_package_dir}"
            )
        target_results[target] = {
            "target": target,
            "source_status": source_status,
            "enforced": bool(expected) and source_status == "present" and not missing_capabilities,
            "enforced_capabilities": enforced_capabilities,
            "missing_capabilities": missing_capabilities,
            "failure_details": failure_details,
        }

    return {
        "source": source_display,
        "source_status": source_status,
        "package_dir_matches": package_matches,
        "summary": {
            "installer_permission_enforced_count": int(summary.get("installer_permission_enforced_count", 0) or 0),
            "installer_permission_failure_count": int(summary.get("installer_permission_failure_count", 0) or 0),
            "permission_target_count": int(summary.get("permission_target_count", 0) or 0),
            "permission_capability_count": int(summary.get("permission_capability_count", 0) or 0),
            "failure_count": int(summary.get("failure_count", 0) or 0),
        },
        "targets": target_results,
    }


def probe_openai_yaml(package_dir: Path, expected: list[str]) -> tuple[list[dict[str, Any]], list[str]]:
    checks: list[dict[str, Any]] = []
    failures: list[str] = []
    path = package_dir / "targets" / "openai" / "agents" / "openai.yaml"
    payload = load_yaml(path)
    permission_contract = payload.get("compatibility", {}).get("permission_contract", {}) if payload else {}
    add_check(checks, failures, "openai-yaml-present", bool(payload), "OpenAI permission metadata YAML is readable")
    add_check(
        checks,
        failures,
        "openai-yaml-permissions",
        sorted_strings(permission_contract.get("declared_capabilities")) == expected,
        "OpenAI YAML permission contract mirrors expected capabilities",
    )
    add_check(
        checks,
        failures,
        "openai-yaml-native-flag",
        isinstance(permission_contract.get("native_enforcement"), bool),
        "OpenAI YAML declares native_enforcement as a boolean",
    )
    return checks, failures


def probe_target(
    skill_dir: Path,
    package_dir: Path,
    target: str,
    expected: list[str],
    installer_targets: dict[str, Any],
) -> dict[str, Any]:
    adapter_path = package_dir / "targets" / target / "adapter.json"
    checks: list[dict[str, Any]] = []
    failures: list[str] = []
    adapter = load_json(adapter_path)
    add_check(checks, failures, "adapter-present", bool(adapter), f"{target} adapter.json is readable")

    permission_contract = adapter.get("permission_contract", {}) if adapter else {}
    target_contract = adapter.get("target_permission_contract", {}) if adapter else {}
    add_check(checks, failures, "permission-contract-present", bool(permission_contract), f"{target} adapter includes permission_contract")
    add_check(checks, failures, "target-contract-present", bool(target_contract), f"{target} adapter includes target_permission_contract")
    add_check(
        checks,
        failures,
        "source-available",
        permission_contract.get("source_available") is True,
        f"{target} permission_contract links to an available trust report",
    )
    add_check(
        checks,
        failures,
        "declared-capabilities-match",
        sorted_strings(target_contract.get("declared_capabilities")) == expected,
        f"{target} target_permission_contract mirrors expected capabilities",
    )
    add_check(
        checks,
        failures,
        "capability-counts-present",
        isinstance(target_contract.get("capability_counts"), dict),
        f"{target} target_permission_contract includes capability_counts",
    )
    add_check(
        checks,
        failures,
        "native-enforcement-boolean",
        isinstance(target_contract.get("native_enforcement"), bool),
        f"{target} target_permission_contract declares native_enforcement as a boolean",
    )
    add_check(
        checks,
        failures,
        "representation-present",
        bool(str(target_contract.get("representation", "")).strip()),
        f"{target} target_permission_contract declares where permission metadata is represented",
    )
    add_check(
        checks,
        failures,
        "operator-note-present",
        bool(str(target_contract.get("operator_note", "")).strip()),
        f"{target} target_permission_contract includes an operator_note",
    )
    add_check(
        checks,
        failures,
        "review-required-matches",
        bool(target_contract.get("review_required")) == bool(expected),
        f"{target} review_required matches whether capabilities are required",
    )

    yaml_checks: list[dict[str, Any]] = []
    yaml_failures: list[str] = []
    if target == "openai":
        yaml_checks, yaml_failures = probe_openai_yaml(package_dir, expected)
        checks.extend(yaml_checks)
        failures.extend(yaml_failures)

    native = target_contract.get("native_enforcement")
    metadata_fallback = native is False and bool(target_contract.get("representation")) and bool(target_contract.get("operator_note"))
    assurance = "native-enforced" if native is True else ("metadata-fallback-explicit" if metadata_fallback else "missing")
    residual_risks = []
    if native is False:
        residual_risks.append("Client-native permission enforcement is not provided by this target; installer or operator must honor metadata.")
    installer_enforcement = installer_targets.get(
        target,
        {
            "target": target,
            "source_status": "missing",
            "enforced": False,
            "enforced_capabilities": [],
            "missing_capabilities": expected,
            "failure_details": ["install simulation report is missing"],
        },
    )
    return {
        "target": target,
        "status": "pass" if not failures else "fail",
        "adapter": display_path(adapter_path, skill_dir),
        "permission_model": str(target_contract.get("permission_model", "")),
        "native_enforcement": bool(native) if isinstance(native, bool) else None,
        "metadata_fallback_explicit": metadata_fallback,
        "installer_enforcement": installer_enforcement,
        "assurance": assurance,
        "declared_capabilities": sorted_strings(target_contract.get("declared_capabilities")),
        "checks": checks,
        "failures": failures,
        "residual_risks": residual_risks,
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    installer = report.get("installer_enforcement", {})
    lines = [
        "# Runtime Permission Probes",
        "",
        "Runtime permission probes verify that generated target adapters expose high-permission capabilities, make native-enforcement limits explicit, and link installer enforcement evidence when available.",
        "",
        "## Summary",
        "",
        f"- OK: `{report['ok']}`",
        f"- Targets probed: `{summary['target_count']}`",
        f"- Passed: `{summary['pass_count']}`",
        f"- Failed: `{summary['fail_count']}`",
        f"- Native enforcement targets: `{summary['native_enforcement_count']}`",
        f"- Explicit metadata fallbacks: `{summary['metadata_fallback_count']}`",
        f"- Installer enforcement source: `{summary['installer_enforcement_source_status']}`",
        f"- Installer-enforced targets: `{summary['installer_enforcement_pass_count']}`",
        f"- Installer permission failures: `{summary['installer_permission_failure_count']}`",
        f"- World-class native evidence ready: `{summary['world_class_native_evidence_ready']}`",
        f"- Required capabilities: `{', '.join(report['expected_capabilities']) or 'none'}`",
        "",
        "| Target | Status | Assurance | Native Enforcement | Metadata Fallback | Installer Enforcement | Residual Risk |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for target in report["targets"]:
        residual = "<br>".join(target["residual_risks"]) if target["residual_risks"] else "None"
        installer_status = target.get("installer_enforcement", {})
        installer_label = "pass" if installer_status.get("enforced") else installer_status.get("source_status", "missing")
        lines.append(
            f"| `{target['target']}` | `{target['status']}` | `{target['assurance']}` | "
            f"`{target['native_enforcement']}` | `{target['metadata_fallback_explicit']}` | `{installer_label}` | {residual} |"
        )
    lines.extend(
        [
            "",
            "## Installer Enforcement",
            "",
            f"- Source: `{installer.get('source', '')}`",
            f"- Source status: `{installer.get('source_status', 'missing')}`",
            f"- Package dir matches probe: `{installer.get('package_dir_matches', False)}`",
            "",
            "Installer enforcement means the package install simulation blocks missing capability approvals or target enforcement notes. It is supporting local distribution evidence, not proof of target-client native enforcement.",
        ]
    )
    lines.extend(["", "## Failures", ""])
    lines.extend([f"- {item}" for item in report["failures"]] or ["- None"])
    lines.extend(
        [
            "",
            "## Reviewer Note",
            "",
            "A passing probe means the target contract is explicit and auditable. It does not claim that a host client enforces permissions natively.",
        ]
    )
    return "\n".join(lines).strip() + "\n"


def probe_runtime_permissions(
    skill_dir: Path,
    package_dir: Path,
    targets: list[str],
    output_json: Path,
    output_md: Path,
    install_simulation_json: Path | None = None,
) -> dict[str, Any]:
    skill_dir = skill_dir.resolve()
    package_dir = package_dir.resolve()
    expected = expected_capabilities(skill_dir)
    installer = installer_enforcement_source(skill_dir, package_dir, targets, expected, install_simulation_json)
    installer_targets = installer.get("targets", {}) if isinstance(installer.get("targets"), dict) else {}
    target_results = [probe_target(skill_dir, package_dir, target, expected, installer_targets) for target in targets]
    failures = [failure for target in target_results for failure in target["failures"]]
    installer_summary = installer.get("summary", {}) if isinstance(installer.get("summary"), dict) else {}
    installer_pass_count = sum(
        1
        for item in installer_targets.values()
        if isinstance(item, dict) and item.get("enforced") is True
    )
    summary = {
        "target_count": len(target_results),
        "pass_count": sum(1 for item in target_results if item["status"] == "pass"),
        "fail_count": sum(1 for item in target_results if item["status"] == "fail"),
        "native_enforcement_count": sum(1 for item in target_results if item["native_enforcement"] is True),
        "metadata_fallback_count": sum(1 for item in target_results if item["metadata_fallback_explicit"]),
        "residual_risk_count": sum(len(item["residual_risks"]) for item in target_results),
        "required_capability_count": len(expected),
        "failure_count": len(failures),
        "installer_enforcement_source_status": installer.get("source_status", "missing"),
        "installer_enforcement_target_count": len(installer_targets),
        "installer_enforcement_pass_count": installer_pass_count,
        "installer_permission_enforced_count": int(installer_summary.get("installer_permission_enforced_count", 0) or 0),
        "installer_permission_failure_count": int(installer_summary.get("installer_permission_failure_count", 0) or 0),
        "installer_permission_capability_count": int(installer_summary.get("permission_capability_count", 0) or 0),
        "world_class_native_evidence_ready": sum(1 for item in target_results if item["native_enforcement"] is True) > 0 and not failures,
        "installer_enforcement_ready": (
            installer.get("source_status") == "present"
            and installer_pass_count == len(target_results)
            and bool(expected)
            and int(installer_summary.get("failure_count", 0) or 0) == 0
            and int(installer_summary.get("installer_permission_failure_count", 0) or 0) == 0
        ),
    }
    report = {
        "schema_version": "1.0",
        "ok": not failures,
        "skill_dir": display_path(skill_dir, skill_dir),
        "package_dir": display_path(package_dir, skill_dir),
        "expected_capabilities": expected,
        "summary": summary,
        "installer_enforcement": {
            "source": installer.get("source", ""),
            "source_status": installer.get("source_status", "missing"),
            "package_dir_matches": installer.get("package_dir_matches", False),
            "summary": installer_summary,
        },
        "targets": target_results,
        "failures": failures,
        "artifacts": {
            "json": display_path(output_json, skill_dir),
            "markdown": display_path(output_md, skill_dir),
        },
    }
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    output_md.write_text(render_markdown(report), encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Probe generated target adapters for runtime permission enforcement metadata.")
    parser.add_argument("skill_dir", nargs="?", default=".")
    parser.add_argument("--package-dir", default="dist")
    parser.add_argument("--target", action="append", choices=DEFAULT_TARGETS)
    parser.add_argument("--output-json")
    parser.add_argument("--output-md")
    parser.add_argument("--install-simulation-json")
    args = parser.parse_args()

    skill_dir = Path(args.skill_dir).resolve()
    report = probe_runtime_permissions(
        skill_dir,
        Path(args.package_dir).resolve(),
        args.target or DEFAULT_TARGETS,
        Path(args.output_json).resolve() if args.output_json else skill_dir / "reports" / "runtime_permission_probes.json",
        Path(args.output_md).resolve() if args.output_md else skill_dir / "reports" / "runtime_permission_probes.md",
        Path(args.install_simulation_json).resolve() if args.install_simulation_json else None,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if report["ok"] else 2)


if __name__ == "__main__":
    main()
