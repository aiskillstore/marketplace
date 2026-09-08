#!/usr/bin/env python3
"""Build and verify the distributable skill-forge ZIP.

Builds from a committed Git revision, includes only the runtime skill surface,
and verifies the resulting archive across every canonical validation profile.

Usage:
    python3 -S scripts/package_skill.py build --output /tmp/skill-forge.zip
    python3 -S scripts/package_skill.py verify /tmp/skill-forge.zip --json
"""

from __future__ import annotations

import argparse
import json
import os
import stat
import subprocess
import sys
import tempfile
import zipfile
import zlib
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from inspect_skill_package import InspectionLimits, target_profile, validate_zip_archive
from portable_zip_paths import validate_portable_zip_members
from runtime_manifest import (
    MANIFEST_PATH,
    RuntimeManifestBuild,
    RuntimeManifestError,
    SKILL_FORGE_SOURCE_ONLY_SCRIPTS,
    SKILL_FORGE_RUNTIME_SELECTORS,
    build_runtime_manifest,
    canonical_zip_member_names,
    verify_source_proof,
    verify_zip_manifest,
    write_canonical_archive as write_runtime_archive,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
INSPECTOR = Path(__file__).with_name("inspect_skill_package.py")
PACKAGE_ROOT = "skill-forge"
PACKAGE_PATHS = SKILL_FORGE_RUNTIME_SELECTORS
REQUIRED_MEMBERS = {
    "SKILL.md",
    "README.md",
    "LICENSE",
    "agents/openai.yaml",
    "runtime-manifest.json",
    "scripts/inspect_skill_package.py",
    "scripts/package_skill.py",
    "scripts/portable_zip_paths.py",
    "scripts/run_self_tests.py",
    "scripts/score_audit.py",
    "scripts/run_bounded_tests.py",
    "scripts/runtime_manifest.py",
    "scripts/validate_audit_contract.py",
}
REQUIRED_DIRECTORIES = ("agents", "references", "scripts")
FORBIDDEN_COMPONENTS = {".git", ".github", "build", "dist", "__pycache__"}
# Runtime exclusions share the runtime-manifest authority; the audit-contract
# validator separately proves the matching SKILL.md declaration.
FORBIDDEN_RUNTIME_PATHS = frozenset(SKILL_FORGE_SOURCE_ONLY_SCRIPTS)
# Keep aliases out of release verification: they intentionally produce the
# same findings as their canonical profile and add no independent evidence.
TARGETS = ("portable", "openai")


class PackageError(RuntimeError):
    """Raised when a release package cannot be built or verified."""


def _is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


ARCHIVE_VERIFICATION_EXCEPTIONS = (
    OSError,
    EOFError,
    RuntimeError,
    ValueError,
    NotImplementedError,
    zlib.error,
    zipfile.BadZipFile,
    zipfile.LargeZipFile,
)


def preflight_archive_errors(archive_path: Path) -> List[str]:
    """Return bounded inspector preflight errors before CRC decompression."""
    findings = validate_zip_archive(
        archive_path,
        InspectionLimits(),
        target_profile("portable"),
    )
    return [
        f"{item.get('code', 'archive_preflight_error')}: {item.get('message', 'archive preflight failed')}"
        for item in findings
        if item.get("severity") == "error"
    ]


def write_canonical_archive(build: RuntimeManifestBuild, output: Path) -> None:
    """Atomically write one deterministic ZIP from committed manifest bytes."""
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    member_names = canonical_zip_member_names(build.manifest)
    _members, path_issues = validate_portable_zip_members(
        (member_name, False) for member_name in member_names
    )
    if path_issues:
        issue = path_issues[0]
        raise PackageError(f"runtime path is not portable: {issue.code}: {issue.raw_name}")

    temporary_path: Optional[Path] = None
    try:
        with tempfile.NamedTemporaryFile(
            dir=output.parent,
            prefix=f".{output.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temporary_path = Path(handle.name)
        write_runtime_archive(build, temporary_path)

        integrity = verify_zip_manifest(temporary_path)
        if integrity.get("status") != "pass":
            raise PackageError(
                "canonical runtime ZIP failed its embedded-manifest check: "
                + "; ".join(integrity.get("errors", []))
            )
        os.replace(temporary_path, output)
        temporary_path = None
    finally:
        if temporary_path is not None:
            try:
                temporary_path.unlink(missing_ok=True)
            except OSError:
                pass


def build_archive(revision: str, output: Path) -> RuntimeManifestBuild:
    """Build a deterministic runtime ZIP from one committed Git revision."""
    try:
        build = build_runtime_manifest(revision, PACKAGE_PATHS, REPO_ROOT)
        write_canonical_archive(build, output)
    except (RuntimeManifestError, OSError, zipfile.BadZipFile) as exc:
        raise PackageError(str(exc)) from exc
    return build


def archive_path_errors(infos: Iterable[zipfile.ZipInfo]) -> List[str]:
    """Return structural errors specific to the distributable package shape."""
    errors: List[str] = []
    materialized_infos = list(infos)
    _, path_issues = validate_portable_zip_members(
        (info.filename, info.is_dir()) for info in materialized_infos
    )
    for issue in path_issues:
        errors.append(f"{issue.code}: {issue.message}: {issue.raw_name}")

    package_prefix = f"{PACKAGE_ROOT}/"
    for info in materialized_infos:
        name = info.filename
        if not name.startswith(package_prefix):
            errors.append(f"ZIP member is outside {package_prefix}: {name}")
            continue
        relative_parts = name.split("/")[1:]
        if any(part in FORBIDDEN_COMPONENTS for part in relative_parts):
            errors.append(f"ZIP member includes a forbidden repo-only path: {name}")
        relative_name = "/".join(relative_parts).rstrip("/")
        if relative_name in FORBIDDEN_RUNTIME_PATHS:
            errors.append(f"ZIP member includes a forbidden repo-only runtime path: {name}")
        mode = info.external_attr >> 16
        if stat.S_IFMT(mode) == stat.S_IFLNK:
            errors.append(f"ZIP member is a symlink: {name}")
    return errors


def verify_archive(archive_path: Path, source_repo: Optional[Path] = None) -> Dict[str, Any]:
    """Verify package shape, contents, and strict inspector results."""
    source_proof_initial: Dict[str, Any] = {
        "status": "Not Assessed",
        "manifest_sha256": None,
    }
    if source_repo is None:
        source_proof_initial["reason"] = "no source repository requested"
    else:
        source_proof_initial.update(
            {
                "repository": str(source_repo),
                "reason": "archive integrity did not permit source proof",
            }
        )
    report: Dict[str, Any] = {
        "archive": str(archive_path),
        "member_count": 0,
        "profile_summaries": {},
        "archive_integrity": {
            "status": "Not Assessed",
            "manifest_sha256": None,
            "archive_sha256": None,
        },
        "source_proof": source_proof_initial,
        "evidence_binding": {
            "status": "Not Assessed",
            "reason": "source proof has not produced a matching manifest digest",
        },
        "errors": [],
    }
    errors: List[str] = report["errors"]

    if not archive_path.is_file():
        errors.append("archive does not exist or is not a regular file")
        report["status"] = "fail"
        return report
    if not INSPECTOR.is_file():
        errors.append(f"bundled inspector is unavailable: {INSPECTOR}")
        report["status"] = "fail"
        return report

    try:
        errors.extend(preflight_archive_errors(archive_path))
    except ARCHIVE_VERIFICATION_EXCEPTIONS as exc:
        errors.append(f"archive preflight failed: {exc}")
    if errors:
        report["status"] = "fail"
        return report

    try:
        with zipfile.ZipFile(archive_path) as archive:
            infos = archive.infolist()
            report["member_count"] = len(infos)
            if not infos:
                errors.append("archive is empty")
            errors.extend(archive_path_errors(infos))
            if errors:
                report["status"] = "fail"
                return report
            members = {info.filename.rstrip("/") for info in infos if not info.is_dir()}
    except ARCHIVE_VERIFICATION_EXCEPTIONS as exc:
        errors.append(f"archive could not be read: {exc}")
        report["status"] = "fail"
        return report

    integrity = verify_zip_manifest(archive_path)
    manifest = integrity.get("manifest")
    report["archive_integrity"] = {
        "status": "Pass" if integrity.get("status") == "pass" else "Fail",
        "manifest_path": integrity.get("manifest_path"),
        "manifest_sha256": integrity.get("manifest_sha256"),
        "archive_sha256": integrity.get("archive_sha256"),
        "source": manifest.get("source") if isinstance(manifest, dict) else None,
        "errors": integrity.get("errors", []),
    }
    if integrity.get("status") != "pass":
        errors.extend(
            f"runtime manifest: {error}" for error in integrity.get("errors", [])
        )
        report["status"] = "fail"
        return report
    if not _is_sha256(integrity.get("manifest_sha256")):
        report["archive_integrity"]["status"] = "Fail"
        errors.append("runtime manifest verification omitted a canonical manifest SHA-256")
    if not _is_sha256(integrity.get("archive_sha256")):
        report["archive_integrity"]["status"] = "Fail"
        errors.append("runtime manifest verification omitted a canonical archive SHA-256")
    if errors:
        report["status"] = "fail"
        return report

    if source_repo is not None and isinstance(manifest, dict):
        source_report = verify_source_proof(manifest, Path(source_repo))
        raw_source_status = source_report.get("status")
        source_status = {
            "pass": "Pass",
            "fail": "Fail",
            "not_assessed": "Not Assessed",
        }.get(raw_source_status, "Fail")
        report["source_proof"] = {
            "status": source_status,
            "manifest_sha256": source_report.get("manifest_sha256"),
            "source": source_report.get("source"),
            "revision": source_report.get("revision"),
            "errors": source_report.get("errors", []),
        }
        if raw_source_status not in {"pass", "fail", "not_assessed"}:
            errors.append(f"source proof returned an unknown status: {raw_source_status!r}")
        archive_manifest_digest = integrity.get("manifest_sha256")
        source_manifest_digest = source_report.get("manifest_sha256")
        if raw_source_status == "pass":
            if not _is_sha256(source_manifest_digest):
                report["source_proof"]["status"] = "Fail"
                report["evidence_binding"] = {
                    "status": "Fail",
                    "reason": "source proof omitted a canonical manifest SHA-256",
                }
                errors.append("source proof omitted a canonical manifest SHA-256")
            elif archive_manifest_digest != source_manifest_digest:
                report["source_proof"]["status"] = "Fail"
                report["evidence_binding"] = {
                    "status": "Fail",
                    "archive_manifest_sha256": archive_manifest_digest,
                    "source_manifest_sha256": source_manifest_digest,
                    "reason": "archive and source proof bind different runtime manifests",
                }
                errors.append(
                    "source proof manifest digest does not match archive integrity manifest digest"
                )
            else:
                report["evidence_binding"] = {
                    "status": "Pass",
                    "manifest_sha256": archive_manifest_digest,
                }
        else:
            report["evidence_binding"] = {
                "status": "Not Assessed",
                "reason": "source proof did not pass",
            }
        if raw_source_status != "pass":
            errors.extend(
                f"source proof: {error}" for error in source_report.get("errors", [])
            )
            report["status"] = "fail"
            return report
        if errors:
            report["status"] = "fail"
            return report

    prefix = f"{PACKAGE_ROOT}/"
    missing = sorted(f"{prefix}{member}" for member in REQUIRED_MEMBERS if f"{prefix}{member}" not in members)
    if missing:
        errors.append(f"required package members are missing: {', '.join(missing)}")
    for directory in REQUIRED_DIRECTORIES:
        if not any(member.startswith(f"{prefix}{directory}/") for member in members):
            errors.append(f"required package directory is empty or missing: {directory}/")

    if errors:
        report["status"] = "fail"
        return report

    for target in TARGETS:
        command = [
            sys.executable,
            "-S",
            str(INSPECTOR),
            str(archive_path),
            "--json",
            "--strict",
            "--target",
            target,
        ]
        try:
            proc = subprocess.run(
                command,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                timeout=60,
            )
        except subprocess.TimeoutExpired as exc:
            errors.append(f"{target} inspection timed out after {exc.timeout} seconds")
            continue
        try:
            data = json.loads(proc.stdout)
        except json.JSONDecodeError:
            errors.append(f"{target} inspection did not return valid JSON: {proc.stderr.strip()}")
            continue

        summary = data.get("summary", {})
        report["profile_summaries"][target] = summary
        if proc.returncode != 0 or not summary.get("strict_pass"):
            errors.append(
                f"{target} strict inspection failed (exit {proc.returncode}): {summary}"
            )
        if data.get("dangerous_command_findings"):
            errors.append(f"{target} inspection found a dangerous bundled command")

    report["status"] = "pass" if not errors else "fail"
    return report


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build or verify the skill-forge release package.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    build = subparsers.add_parser("build", help="build a runtime-only ZIP from a committed revision")
    build.add_argument("--revision", default="HEAD", help="Git revision to package (default: HEAD)")
    build.add_argument("--output", required=True, type=Path, help="destination ZIP path")

    verify = subparsers.add_parser("verify", help="verify a built ZIP across all supported targets")
    verify.add_argument("archive", type=Path, help="ZIP archive to verify")
    verify.add_argument("--json", action="store_true", help="emit a machine-readable verification report")
    verify.add_argument(
        "--source-repo",
        type=Path,
        help="also prove the embedded commit, tree, and blobs against this Git repository",
    )
    return parser.parse_args(argv)


def render_report(report: Dict[str, Any]) -> str:
    lines = [
        f"Package verification: {report['status']}",
        f"Archive: {report['archive']}",
        f"Members: {report['member_count']}",
    ]
    for target, summary in report["profile_summaries"].items():
        lines.append(f"{target}: {summary}")
    lines.append(f"Archive integrity: {report['archive_integrity'].get('status')}")
    lines.append(
        f"Archive SHA-256: {report['archive_integrity'].get('archive_sha256') or 'Not Assessed'}"
    )
    lines.append(
        "Archive manifest SHA-256: "
        f"{report['archive_integrity'].get('manifest_sha256') or 'Not Assessed'}"
    )
    lines.append(f"Source proof: {report['source_proof'].get('status')}")
    lines.append(
        "Source manifest SHA-256: "
        f"{report['source_proof'].get('manifest_sha256') or 'Not Assessed'}"
    )
    lines.append(f"Evidence binding: {report['evidence_binding'].get('status')}")
    for error in report["errors"]:
        lines.append(f"error: {error}")
    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    if args.command == "build":
        try:
            build = build_archive(args.revision, args.output)
        except PackageError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        print(
            f"Built {args.output} from {build.source.commit} with manifest "
            f"{MANIFEST_PATH} and runtime paths: {', '.join(PACKAGE_PATHS)}"
        )
        return 0

    try:
        report = verify_archive(args.archive, args.source_repo)
    except ARCHIVE_VERIFICATION_EXCEPTIONS as exc:
        report = {
            "archive": str(args.archive),
            "member_count": 0,
            "profile_summaries": {},
            "archive_integrity": {"status": "Fail"},
            "source_proof": {"status": "Not Assessed"},
            "evidence_binding": {"status": "Not Assessed"},
            "errors": [f"archive verification failed: {exc}"],
            "status": "fail",
        }
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True, allow_nan=False))
    else:
        print(render_report(report))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
