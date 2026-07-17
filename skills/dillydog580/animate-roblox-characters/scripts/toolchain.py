#!/usr/bin/env python3
"""Offline inventory and safety audit for the Roblox animation toolchain."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import platform
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Any


SKILL_DIRECTORY = Path(__file__).resolve().parents[1]
MANIFEST_PATH = SKILL_DIRECTORY / "assets" / "toolchain-manifest.json"
MINIMUM_BLENDER = (4, 5, 0)
MINIMUM_PILLOW = (10, 0, 0)
MAXIMUM_PILLOW = (13, 0, 0)
NETWORK_MODULES = {"http.client", "requests", "socket", "urllib", "urllib.request"}
PROCESS_MODULES = {"subprocess"}
MAX_ARCHIVE_MEMBERS = 2048
MAX_ARCHIVE_MEMBER_SIZE = 32 * 1024 * 1024
MAX_ARCHIVE_TOTAL_SIZE = 128 * 1024 * 1024
MAX_ARCHIVE_COMPRESSION_RATIO = 200
SUPPORTED_RUNTIME_WORKFLOWS = ("r15-bootstrap",)


def load_manifest(path: str | Path = MANIFEST_PATH) -> dict[str, Any]:
    source = Path(path).expanduser().resolve()
    payload = json.loads(source.read_text(encoding="utf-8"))
    if payload.get("schema_version") != 1 or not isinstance(payload.get("components"), list):
        raise ValueError("Unsupported or malformed toolchain manifest")
    return payload


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _version_triplet(value: str) -> tuple[int, int, int]:
    parts = value.split(".")
    if len(parts) != 3 or any(not part.isdigit() for part in parts):
        raise ValueError("expected an exact major.minor.patch version")
    return tuple(int(part) for part in parts)  # type: ignore[return-value]


def audit_pillow_encoder() -> dict[str, Any]:
    """Verify Pillow in the Python environment that will encode GIF previews."""
    errors: list[str] = []
    version = None
    try:
        import PIL  # type: ignore
    except ImportError:
        errors.append("Pillow >=10,<13 is required in the external GIF-encoding Python environment")
    else:
        version = PIL.__version__
        try:
            parsed = _version_triplet(version)
        except ValueError as exc:
            errors.append(f"Could not verify Pillow version {version!r}: {exc}")
        else:
            if parsed < MINIMUM_PILLOW or parsed >= MAXIMUM_PILLOW:
                errors.append(f"Unsupported Pillow version: {version}; require >=10,<13")
    return {
        "ok": not errors,
        "pillow_available": version is not None,
        "pillow_version": version,
        "errors": errors,
    }


def audit_python_source(path: str | Path) -> dict[str, Any]:
    """Report network, process, and dynamic-code capabilities without executing source."""
    source_path = Path(path).expanduser().resolve()
    tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))
    imports = set()
    calls = set()
    aliases: dict[str, str] = {}

    def resolved_name(node: ast.expr) -> str | None:
        if isinstance(node, ast.Name):
            return aliases.get(node.id, node.id)
        if isinstance(node, ast.Attribute):
            parent = resolved_name(node.value)
            return f"{parent}.{node.attr}" if parent else None
        return None

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
                aliases[alias.asname or alias.name.split(".")[0]] = alias.name
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)
            for alias in node.names:
                aliases[alias.asname or alias.name] = f"{node.module}.{alias.name}"
        elif isinstance(node, ast.Call):
            name = resolved_name(node.func)
            if name:
                calls.add(name)
    network = sorted(
        name for name in imports if name in NETWORK_MODULES or any(name.startswith(item + ".") for item in NETWORK_MODULES)
    )
    processes = sorted(
        name for name in imports if name in PROCESS_MODULES or any(name.startswith(item + ".") for item in PROCESS_MODULES)
    )
    dynamic_calls = sorted(
        name
        for name in calls
        if name in {"eval", "exec", "compile", "builtins.eval", "builtins.exec", "builtins.compile"}
    )
    process_calls = sorted(
        name
        for name in calls
        if name in {"os.system", "os.popen"} or name.startswith(("subprocess.", "multiprocessing.", "pty."))
    )
    network_calls = sorted(
        name
        for name in calls
        if name.startswith(("requests.", "urllib.", "socket.", "http.client."))
    )
    return {
        "path": str(source_path),
        "sha256": sha256_file(source_path),
        "imports": sorted(imports),
        "network_modules": network,
        "process_modules": processes,
        "process_calls": process_calls,
        "dynamic_code_calls": dynamic_calls,
        "network_calls": network_calls,
        "review_required": bool(network or processes or process_calls or dynamic_calls or network_calls),
    }


def _archive_audit_result(
    archive_path: Path,
    archive_sha256: str | None,
    reports: list[dict[str, Any]],
    errors: list[str],
) -> dict[str, Any]:
    """Return the complete public archive-audit schema for every exit path."""
    return {
        "path": str(archive_path),
        "sha256": archive_sha256,
        "python_files": len(reports),
        "network_files": [
            item["path"] for item in reports if item["network_modules"] or item["network_calls"]
        ],
        "process_files": [
            item["path"] for item in reports if item["process_modules"] or item["process_calls"]
        ],
        "dynamic_code_files": [item["path"] for item in reports if item["dynamic_code_calls"]],
        "reports": reports,
        "errors": errors,
    }


def audit_python_archive(path: str | Path) -> dict[str, Any]:
    """Audit every Python file in a zip without importing or executing it."""
    archive_path = Path(path).expanduser().resolve()
    reports: list[dict[str, Any]] = []
    errors: list[str] = []
    try:
        archive_sha256 = sha256_file(archive_path) if archive_path.is_file() else None
    except OSError as exc:
        archive_sha256 = None
        errors.append(f"Could not hash Python archive: {exc}")
    try:
        opened_archive = zipfile.ZipFile(archive_path)
    except (OSError, zipfile.BadZipFile) as exc:
        errors.append(f"Could not open Python archive: {exc}")
        return _archive_audit_result(archive_path, archive_sha256, reports, errors)
    with tempfile.TemporaryDirectory() as directory, opened_archive as archive:
        root = Path(directory).resolve()
        members = archive.infolist()
        if len(members) > MAX_ARCHIVE_MEMBERS:
            errors.append(f"Archive contains too many members: {len(members)}")
        if sum(member.file_size for member in members) > MAX_ARCHIVE_TOTAL_SIZE:
            errors.append("Archive exceeds the maximum total uncompressed size")
        for member in members:
            target = (root / member.filename).resolve()
            if root not in target.parents and target != root:
                errors.append(f"Unsafe archive member: {member.filename}")
            if member.file_size > MAX_ARCHIVE_MEMBER_SIZE:
                errors.append(f"Archive member is too large: {member.filename}")
            if member.flag_bits & 0x1:
                errors.append(f"Encrypted archive member is not auditable: {member.filename}")
            ratio = member.file_size / max(member.compress_size, 1)
            if ratio > MAX_ARCHIVE_COMPRESSION_RATIO:
                errors.append(f"Suspicious compression ratio for archive member: {member.filename}")
            file_type = (member.external_attr >> 16) & 0o170000
            if file_type == 0o120000:
                errors.append(f"Archive symlink is not allowed: {member.filename}")
        if errors:
            return _archive_audit_result(archive_path, archive_sha256, reports, errors)
        try:
            archive.extractall(root)
        except (OSError, RuntimeError, zipfile.BadZipFile) as exc:
            errors.append(f"Could not safely extract Python archive: {exc}")
            return _archive_audit_result(archive_path, archive_sha256, reports, errors)
        for source in sorted(root.rglob("*.py")):
            try:
                report = audit_python_source(source)
            except (OSError, SyntaxError, UnicodeDecodeError) as exc:
                errors.append(f"Could not audit {source.relative_to(root)}: {exc}")
                continue
            report["path"] = str(source.relative_to(root))
            reports.append(report)
    return _archive_audit_result(archive_path, archive_sha256, reports, errors)


def _blender_executable() -> str | None:
    found = shutil.which("blender")
    if found:
        return found
    mac_path = Path("/Applications/Blender.app/Contents/MacOS/Blender")
    return str(mac_path) if mac_path.is_file() else None


def audit_repository(skill_directory: str | Path = SKILL_DIRECTORY) -> dict[str, Any]:
    root = Path(skill_directory).expanduser().resolve()
    manifest = load_manifest(root / "assets" / "toolchain-manifest.json")
    components = []
    errors = []
    warnings = []
    for component in manifest["components"]:
        item = {
            "id": component["id"],
            "bundled": bool(component.get("bundled", False)),
            "license": component.get("license", "unknown"),
            "source": component.get("source"),
            "files": [],
        }
        for relative in component.get("files", []):
            path = root / relative
            exists = path.is_file()
            record = {"path": relative, "exists": exists}
            if exists:
                record["sha256"] = sha256_file(path)
                expected = component.get("sha256") if len(component.get("files", [])) == 1 else None
                if expected:
                    record["expected_sha256"] = expected
                    record["integrity_ok"] = record["sha256"] == expected
                    if not record["integrity_ok"]:
                        errors.append(f"Bundled component failed SHA-256 verification: {relative}")
            else:
                errors.append(f"Missing bundled component file: {relative}")
            item["files"].append(record)
        license_file = component.get("license_file")
        if license_file and not (root / license_file).is_file():
            errors.append(f"Missing third-party license file: {license_file}")
        if component.get("downloads"):
            installed = []
            for download in component["downloads"]:
                path = root / "assets" / "external" / download["destination"]
                record = {"path": str(path.relative_to(root)), "exists": path.is_file()}
                if path.is_file():
                    record["sha256"] = sha256_file(path)
                    record["integrity_ok"] = (
                        record["sha256"] == download["sha256"] and path.stat().st_size == int(download["size"])
                    )
                    if not record["integrity_ok"]:
                        errors.append(f"External asset failed verification: {record['path']}")
                else:
                    warnings.append(
                        f"Pinned external asset is not installed: {record['path']}; run fetch_assets.py for {component['id']}"
                    )
                installed.append(record)
            item["downloads"] = installed
        if component["id"] == "cautioned-blender-addon" and item["files"] and item["files"][0]["exists"]:
            archive_audit = audit_python_archive(root / item["files"][0]["path"])
            item["archive_audit"] = {
                key: archive_audit[key]
                for key in ("python_files", "network_files", "process_files", "dynamic_code_files", "errors")
            }
            errors.extend(archive_audit["errors"])
        components.append(item)
    return {
        "ok": not errors,
        "skill_directory": str(root),
        "components": components,
        "errors": errors,
        "warnings": warnings,
    }


def _external_capability_status(
    available: bool | None,
    *,
    required: bool,
    default_unverified: str,
) -> str:
    if available is True:
        return "verified-by-external-discovery"
    if available is False:
        return "unavailable-by-external-discovery"
    return "required-unverified" if required else default_unverified


def audit_runtime(
    required_workflow: str | None = None,
    studio_mcp_available: bool | None = None,
    creator_plugin_available: bool | None = None,
    blender_mcp_available: bool | None = None,
    pillow_available: bool | None = None,
    pillow_version: str | None = None,
) -> dict[str, Any]:
    if required_workflow not in (None, *SUPPORTED_RUNTIME_WORKFLOWS):
        raise ValueError(
            f"Unsupported runtime workflow: {required_workflow}; "
            f"expected one of {', '.join(SUPPORTED_RUNTIME_WORKFLOWS)}"
        )
    for name, value in (
        ("blender_mcp_available", blender_mcp_available),
        ("pillow_available", pillow_available),
        ("studio_mcp_available", studio_mcp_available),
        ("creator_plugin_available", creator_plugin_available),
    ):
        if value is not None and not isinstance(value, bool):
            raise TypeError(f"{name} must be True, False, or None")
    if pillow_version is not None and not isinstance(pillow_version, str):
        raise TypeError("pillow_version must be a major.minor.patch string or None")

    r15_bootstrap_required = required_workflow == "r15-bootstrap"
    blender = _blender_executable()
    errors = []
    warnings = []
    runtime: dict[str, Any] = {
        "required_workflow": required_workflow,
        "blender_executable": blender,
        "uvx_executable": shutil.which("uvx"),
        "inside_blender": False,
        "background": None,
        "session_mode": "not-in-blender",
        "blender_version": None,
        "pillow_version": pillow_version,
        "operators": {},
        "agent_checks": {
            "blender_mcp_python_execution": _external_capability_status(
                blender_mcp_available,
                required=True,
                default_unverified="required-unverified",
            ),
            "blender_python_in_process": "unverified",
            "pillow_gif_encoder": _external_capability_status(
                pillow_available,
                required=True,
                default_unverified="required-unverified",
            ),
            "roblox_studio_mcp": _external_capability_status(
                studio_mcp_available,
                required=r15_bootstrap_required,
                default_unverified="optional-unverified",
            ),
            "creator_store_animation_plugin": _external_capability_status(
                creator_plugin_available,
                required=r15_bootstrap_required,
                default_unverified="workflow-dependent-unverified",
            ),
        },
    }
    if blender_mcp_available is not True:
        errors.append(
            "Runtime readiness requires arbitrary-Python Blender MCP capability to be verified by external "
            "capability discovery"
        )
    if pillow_available is not True:
        errors.append(
            "Runtime readiness requires Pillow in the external GIF-encoding Python environment to be verified "
            "by external capability discovery"
        )
    elif pillow_version is None:
        runtime["agent_checks"]["pillow_gif_encoder"] = "available-version-unverified"
        errors.append("Runtime readiness requires an exact externally verified Pillow version")
    else:
        try:
            parsed_pillow_version = _version_triplet(pillow_version)
        except ValueError as exc:
            runtime["agent_checks"]["pillow_gif_encoder"] = "available-invalid-version-attestation"
            errors.append(f"Could not verify externally attested Pillow version {pillow_version!r}: {exc}")
        else:
            if parsed_pillow_version < MINIMUM_PILLOW or parsed_pillow_version >= MAXIMUM_PILLOW:
                runtime["agent_checks"]["pillow_gif_encoder"] = "available-unsupported-version"
                errors.append(f"Unsupported externally attested Pillow version: {pillow_version}; require >=10,<13")
    if r15_bootstrap_required and studio_mcp_available is not True:
        errors.append(
            "The r15-bootstrap workflow requires Roblox Studio MCP to be verified by external capability discovery"
        )
    if r15_bootstrap_required and creator_plugin_available is not True:
        errors.append(
            "The r15-bootstrap workflow requires the Creator Store animation plugin to be verified by external "
            "capability discovery"
        )
    try:
        import bpy  # type: ignore
    except ImportError:
        if blender is None:
            errors.append("Blender executable was not found")
        errors.append(
            "Runtime readiness is unverified outside Blender; run this audit through the persistent Blender GUI/MCP session"
        )
    else:
        runtime["inside_blender"] = True
        runtime["agent_checks"]["blender_python_in_process"] = "verified-by-bpy-import"
        runtime["blender_version"] = list(bpy.app.version)
        runtime["background"] = bool(bpy.app.background)
        runtime["session_mode"] = "background" if bpy.app.background else "persistent-gui"
        if bpy.app.background:
            errors.append(
                "Background Blender sessions are prohibited for animation work; use one persistent "
                "interactive Blender GUI connected through Blender MCP"
            )
        if (
            platform.system().lower() == "darwin"
            and platform.machine().lower() in {"arm64", "aarch64"}
            and tuple(bpy.app.version)[:2] == (5, 1)
        ):
            warnings.append(
                "This Blender/platform combination has produced a native image-thread shutdown crash in "
                "an observed automation session; keep the GUI process open or use Blender 4.5 LTS"
            )
        for name, operator_name in (
            ("rbxanim_import", "rbxanims_importmodel"),
            ("rbxanim_rebuild", "rbxanims_genrig"),
            ("rbxanim_export", "rbxanims_bake_file"),
        ):
            try:
                operator = getattr(bpy.ops.object, operator_name)
                operator.get_rna_type()
                available = True
            except (AttributeError, KeyError, RuntimeError, TypeError):
                available = False
            runtime["operators"][name] = available
        if tuple(bpy.app.version) < MINIMUM_BLENDER:
            errors.append("Blender 4.5 or newer is required")
        if r15_bootstrap_required:
            for name in ("rbxanim_import", "rbxanim_rebuild", "rbxanim_export"):
                if not runtime["operators"].get(name):
                    errors.append(f"The r15-bootstrap workflow requires the bundled add-on operator: {name}")
        elif not runtime["operators"].get("rbxanim_export"):
            warnings.append("Motor6D export add-on is not registered in this Blender session")
    return {"ok": not errors, "runtime": runtime, "errors": errors, "warnings": warnings}


def full_audit(
    skill_directory: str | Path = SKILL_DIRECTORY,
    required_workflow: str | None = None,
    studio_mcp_available: bool | None = None,
    creator_plugin_available: bool | None = None,
    blender_mcp_available: bool | None = None,
    pillow_available: bool | None = None,
    pillow_version: str | None = None,
) -> dict[str, Any]:
    repository = audit_repository(skill_directory)
    runtime = audit_runtime(
        required_workflow=required_workflow,
        studio_mcp_available=studio_mcp_available,
        creator_plugin_available=creator_plugin_available,
        blender_mcp_available=blender_mcp_available,
        pillow_available=pillow_available,
        pillow_version=pillow_version,
    )
    return {
        "ok": repository["ok"] and runtime["ok"],
        "repository": repository,
        "runtime": runtime,
        "errors": repository["errors"] + runtime["errors"],
        "warnings": repository["warnings"] + runtime["warnings"],
    }


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill-directory", default=SKILL_DIRECTORY)
    parser.add_argument("--audit-addon", help="Statically audit a Blender Python add-on without running it")
    parser.add_argument("--audit-archive", help="Statically audit every Python file in an add-on zip")
    parser.add_argument(
        "--audit-pillow",
        action="store_true",
        help="Verify Pillow in the external Python environment used to encode GIF previews",
    )
    parser.add_argument("--repository-only", action="store_true", help="Skip host runtime checks (for CI)")
    parser.add_argument(
        "--workflow",
        choices=SUPPORTED_RUNTIME_WORKFLOWS,
        help="Require workflow-specific capabilities during the runtime audit",
    )
    parser.add_argument(
        "--blender-mcp-available",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Record whether arbitrary-Python Blender MCP was verified by external capability discovery",
    )
    parser.add_argument(
        "--studio-mcp-available",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Record whether Roblox Studio MCP was verified by external capability discovery",
    )
    parser.add_argument(
        "--creator-plugin-available",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Record whether the Creator Store animation plugin was verified by external capability discovery",
    )
    parser.add_argument(
        "--pillow-available",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Record whether Pillow was verified in the external GIF-encoding Python environment",
    )
    parser.add_argument(
        "--pillow-version",
        help="Exact externally verified Pillow major.minor.patch version",
    )
    return parser.parse_args(argv)


def main() -> int:
    args = _parse_args(sys.argv[1:])
    if args.audit_addon:
        result = audit_python_source(args.audit_addon)
    elif args.audit_archive:
        result = audit_python_archive(args.audit_archive)
        result["ok"] = not result["errors"]
    elif args.audit_pillow:
        result = audit_pillow_encoder()
    elif args.repository_only:
        result = audit_repository(args.skill_directory)
    else:
        result = full_audit(
            args.skill_directory,
            required_workflow=args.workflow,
            studio_mcp_available=args.studio_mcp_available,
            creator_plugin_available=args.creator_plugin_available,
            blender_mcp_available=args.blender_mcp_available,
            pillow_available=args.pillow_available,
            pillow_version=args.pillow_version,
        )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("ok", not result.get("review_required", False)) else 1


if __name__ == "__main__":
    raise SystemExit(main())
