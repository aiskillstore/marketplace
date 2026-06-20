#!/usr/bin/env python3
import argparse
import json
import re
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
BUMP_RANK = {"none": 0, "patch": 1, "minor": 2, "major": 3}
COMPAT_RANK = {"missing": 0, "unknown": 0, "fail": 0, "warn": 1, "pass": 2}


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


def package_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    package = payload.get("package")
    if isinstance(package, dict):
        return package
    return payload


def parse_version(value: str) -> tuple[int, int, int] | None:
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)(?:[-+].*)?$", str(value or ""))
    if not match:
        return None
    return tuple(int(part) for part in match.groups())


def declared_bump(previous: str, current: str) -> str:
    old = parse_version(previous)
    new = parse_version(current)
    if old is None or new is None:
        return "invalid"
    if new < old:
        return "downgrade"
    if new == old:
        return "none"
    if new[0] > old[0]:
        return "major"
    if new[1] > old[1]:
        return "minor"
    return "patch"


def compare_sets(previous: list[Any], current: list[Any]) -> tuple[list[str], list[str]]:
    old = {str(item) for item in previous}
    new = {str(item) for item in current}
    return sorted(new - old), sorted(old - new)


def compatibility_changes(previous: dict[str, Any], current: dict[str, Any]) -> list[dict[str, str]]:
    targets = sorted(set(previous) | set(current))
    changes = []
    for target in targets:
        old = str(previous.get(target, "missing"))
        new = str(current.get(target, "missing"))
        if old != new:
            direction = "regressed" if COMPAT_RANK.get(new, 0) < COMPAT_RANK.get(old, 0) else "improved"
            changes.append({"target": target, "from": old, "to": new, "direction": direction})
    return changes


def metadata_changes(previous: dict[str, Any], current: dict[str, Any]) -> list[dict[str, str]]:
    fields = ["description", "maturity", "owner", "review_cadence", "trust_level", "license"]
    changes = []
    for field in fields:
        old = str(previous.get(field, ""))
        new = str(current.get(field, ""))
        if old != new:
            changes.append({"field": field, "from": old, "to": new})
    return changes


def checksum_changes(previous: dict[str, Any], current: dict[str, Any]) -> list[dict[str, str]]:
    old_checksums = previous.get("checksums", {}) if isinstance(previous.get("checksums"), dict) else {}
    new_checksums = current.get("checksums", {}) if isinstance(current.get("checksums"), dict) else {}
    changes = []
    for key in sorted(set(old_checksums) | set(new_checksums)):
        old = str(old_checksums.get(key, ""))
        new = str(new_checksums.get(key, ""))
        if old != new:
            changes.append({"field": key, "from": old, "to": new})
    return changes


def required_bump(
    *,
    name_changed: bool,
    removed_targets: list[str],
    added_targets: list[str],
    compat: list[dict[str, str]],
    metadata: list[dict[str, str]],
    checksums: list[dict[str, str]],
) -> str:
    if name_changed or removed_targets or any(item["direction"] == "regressed" for item in compat):
        return "major"
    if added_targets or any(item["field"] in {"description", "maturity", "trust_level"} for item in metadata):
        return "minor"
    if metadata or checksums or compat:
        return "patch"
    return "none"


def build_release_notes(diff: dict[str, Any], recommended: str, current: dict[str, Any]) -> list[str]:
    notes = [f"Recommended version bump: {recommended}."]
    if diff["removed_targets"]:
        notes.append(f"Breaking target removals: {', '.join(diff['removed_targets'])}.")
    if diff["added_targets"]:
        notes.append(f"Added targets: {', '.join(diff['added_targets'])}.")
    regressions = [item for item in diff["compatibility_changes"] if item["direction"] == "regressed"]
    if regressions:
        notes.append("Compatibility regressions: " + ", ".join(f"{item['target']} {item['from']}->{item['to']}" for item in regressions) + ".")
    if diff["checksum_changes"]:
        notes.append("Package or archive checksum changed; reviewers should verify package artifacts before release.")
    if current.get("artifacts", {}).get("package_verification"):
        notes.append(f"Package verification evidence: {current['artifacts']['package_verification']}.")
    return notes


def run_upgrade_check(previous: dict[str, Any], current: dict[str, Any], generated_at: str) -> dict[str, Any]:
    failures = []
    warnings = []
    previous_version = str(previous.get("version", ""))
    current_version = str(current.get("version", ""))
    bump = declared_bump(previous_version, current_version)
    if bump == "invalid":
        failures.append("Version comparison requires semver-like previous and current versions")
    if bump == "downgrade":
        failures.append("Current version is lower than previous version")

    added_targets, removed_targets = compare_sets(previous.get("targets", []), current.get("targets", []))
    compat = compatibility_changes(previous.get("compatibility", {}), current.get("compatibility", {}))
    metadata = metadata_changes(previous, current)
    checksums = checksum_changes(previous, current)
    name_changed = str(previous.get("name", "")) != str(current.get("name", ""))
    recommended = required_bump(
        name_changed=name_changed,
        removed_targets=removed_targets,
        added_targets=added_targets,
        compat=compat,
        metadata=metadata,
        checksums=checksums,
    )
    if bump in BUMP_RANK and BUMP_RANK[bump] < BUMP_RANK[recommended]:
        failures.append(f"Version bump is insufficient: declared {bump}, recommended {recommended}")
    if name_changed:
        failures.append("Package name changed; publish as a new package or use a major version bump")
    if not checksums:
        warnings.append("No checksum changes detected; confirm the previous package is the intended comparison baseline")

    diff = {
        "name_changed": name_changed,
        "added_targets": added_targets,
        "removed_targets": removed_targets,
        "compatibility_changes": compat,
        "metadata_changes": metadata,
        "checksum_changes": checksums,
    }
    return {
        "ok": not failures,
        "schema_version": "2.0",
        "generated_at": generated_at,
        "previous": {
            "name": previous.get("name", ""),
            "version": previous_version,
            "targets": previous.get("targets", []),
        },
        "current": {
            "name": current.get("name", ""),
            "version": current_version,
            "targets": current.get("targets", []),
        },
        "summary": {
            "declared_bump": bump,
            "recommended_bump": recommended,
            "breaking_change_count": int(name_changed) + len(removed_targets) + sum(1 for item in compat if item["direction"] == "regressed"),
            "added_target_count": len(added_targets),
            "metadata_change_count": len(metadata),
            "checksum_change_count": len(checksums),
            "failure_count": len(failures),
            "warning_count": len(warnings),
        },
        "upgrade_diff": diff,
        "release_notes": build_release_notes(diff, recommended, current),
        "failures": failures,
        "warnings": warnings,
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Upgrade Check",
        "",
        f"- OK: `{report['ok']}`",
        f"- Previous: `{report['previous']['name']} {report['previous']['version']}`",
        f"- Current: `{report['current']['name']} {report['current']['version']}`",
        f"- Declared bump: `{report['summary']['declared_bump']}`",
        f"- Recommended bump: `{report['summary']['recommended_bump']}`",
        f"- Breaking changes: `{report['summary']['breaking_change_count']}`",
        "",
        "## Upgrade Diff",
        "",
        f"- Added targets: `{', '.join(report['upgrade_diff']['added_targets']) or 'none'}`",
        f"- Removed targets: `{', '.join(report['upgrade_diff']['removed_targets']) or 'none'}`",
        f"- Compatibility changes: `{len(report['upgrade_diff']['compatibility_changes'])}`",
        f"- Metadata changes: `{len(report['upgrade_diff']['metadata_changes'])}`",
        f"- Checksum changes: `{len(report['upgrade_diff']['checksum_changes'])}`",
        "",
        "## Release Notes",
        "",
    ]
    lines.extend(f"- {item}" for item in report["release_notes"])
    lines.extend(["", "## Failures", ""])
    lines.extend([f"- {item}" for item in report["failures"]] or ["- None"])
    lines.extend(["", "## Warnings", ""])
    lines.extend([f"- {item}" for item in report["warnings"]] or ["- None"])
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare current and previous registry package metadata for upgrade readiness.")
    parser.add_argument("skill_dir", nargs="?", default=".")
    parser.add_argument("--previous-package-json", required=True)
    parser.add_argument("--current-package-json", default="reports/registry_audit.json")
    parser.add_argument("--output-json", default="reports/upgrade_check.json")
    parser.add_argument("--output-md", default="reports/upgrade_check.md")
    parser.add_argument("--generated-at", default=str(date.today()))
    args = parser.parse_args()

    previous = package_from_payload(load_json(Path(args.previous_package_json)))
    current = package_from_payload(load_json(Path(args.current_package_json)))
    report = run_upgrade_check(previous, current, args.generated_at)
    report["artifacts"] = {
        "previous_package": display_path(Path(args.previous_package_json)),
        "current_package": display_path(Path(args.current_package_json)),
    }
    output_json = Path(args.output_json)
    output_md = Path(args.output_md)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    output_md.write_text(render_markdown(report), encoding="utf-8")
    report["artifacts"]["json"] = display_path(output_json)
    report["artifacts"]["markdown"] = display_path(output_md)
    output_json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if report["ok"] else 2)


if __name__ == "__main__":
    main()
