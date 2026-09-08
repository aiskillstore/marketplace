#!/usr/bin/env python3
"""Install a reviewed local canonical runtime ZIP without merging old files.

Run this helper from a trusted source checkout. The expected SHA-256 must come
from a separately reviewed release. No downloads or archive code execution.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import tempfile
from typing import Any, Dict, Optional
import zipfile

from package_skill import verify_archive
from runtime_manifest import MAX_CANONICAL_ARCHIVE_BYTES, PACKAGE_ROOT


class InstallError(RuntimeError):
    """Installation was refused or could not complete safely."""


def _plain_path(path: Path, directory: bool) -> Path:
    """Require an existing path without symlinks at any component."""
    path = Path(os.path.abspath(path))
    for component in [*reversed(path.parents), path]:
        mode = component.lstat().st_mode
        if stat.S_ISLNK(mode):
            raise InstallError(f"symlink path is not supported: {component}")
        expected_dir = component != path or directory
        if not (stat.S_ISDIR(mode) if expected_dir else stat.S_ISREG(mode)):
            raise InstallError(f"unexpected path type: {component}")
    return path


def _inventory(root: Path) -> Dict[str, Any]:
    """Compare the complete tree, including empty directories and file modes."""
    _plain_path(root, True)
    inventory: Dict[str, Any] = {}
    for directory, directories, files in os.walk(root, followlinks=False):
        for name in directories + files:
            path = Path(directory) / name
            if name == ".env" or name.startswith(".env."):
                raise InstallError("protected environment path refused before reading contents")
            info = path.lstat()
            relative = path.relative_to(root).as_posix()
            if stat.S_ISDIR(info.st_mode):
                inventory[relative] = ("directory",)
            elif stat.S_ISREG(info.st_mode) and info.st_nlink == 1:
                digest = hashlib.sha256()
                with path.open("rb") as handle:
                    for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                        digest.update(chunk)
                inventory[relative] = ("file", info.st_size, digest.hexdigest(),
                                       stat.S_IMODE(info.st_mode))
            else:
                raise InstallError(f"symlink, hardlink or special file refused: {path}")
    return inventory


def install_archive(archive: Path, expected_sha256: str, skills_dir: Path) -> Dict[str, Any]:
    """Verify, stage outside skills_dir, preserve the old tree, and swap.

    skills_dir must already exist, have no symlink ancestors, and be on the
    same filesystem as its parent. Do not run concurrent installers or edit
    the installation while this operation is in progress. Recoverable Python
    exceptions (including KeyboardInterrupt) roll back the swap; SIGKILL,
    power loss, and concurrent hostile filesystem mutation are not covered.
    """
    if not isinstance(expected_sha256, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", expected_sha256):
        raise InstallError("expected SHA-256 must be exactly 64 hexadecimal characters")
    archive = _plain_path(Path(archive), False)
    if archive.stat().st_size > MAX_CANONICAL_ARCHIVE_BYTES:
        raise InstallError("archive exceeds the canonical archive size limit")
    # Snapshot before verification: every subsequent check and extraction uses
    # precisely these bytes, even if the caller's archive is replaced later.
    with archive.open("rb") as handle:
        payload = handle.read(MAX_CANONICAL_ARCHIVE_BYTES + 1)
    if len(payload) > MAX_CANONICAL_ARCHIVE_BYTES:
        raise InstallError("archive exceeds the canonical archive size limit")
    digest = hashlib.sha256(payload).hexdigest()
    if digest != expected_sha256.lower():
        raise InstallError("archive SHA-256 does not match the reviewed expected digest")

    skills_dir = _plain_path(Path(skills_dir), True)
    if skills_dir.stat().st_dev != skills_dir.parent.stat().st_dev:
        raise InstallError("skills directory and external staging parent must share a filesystem")
    target = skills_dir / PACKAGE_ROOT
    present = os.path.lexists(target)
    old_inventory = _inventory(target) if present else None
    work = Path(tempfile.mkdtemp(prefix=".skill-forge-install-", dir=skills_dir.parent))
    stage = work / "staged"
    backup = work / "backup"
    keep_work = False
    try:
        reviewed = work / "reviewed.zip"
        reviewed.write_bytes(payload)
        report = verify_archive(reviewed)
        if report.get("status") != "pass":
            raise InstallError("archive verification failed: " + "; ".join(report.get("errors", [])))
        stage.mkdir()
        with zipfile.ZipFile(reviewed) as source:
            for info in source.infolist():
                relative = info.filename[len(PACKAGE_ROOT) + 1:]
                destination = stage / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(source.read(info))
                destination.chmod(stat.S_IMODE(info.external_attr >> 16))
        staged_inventory = _inventory(stage)
        # Recheck the destination immediately before swapping; never silently
        # overwrite an installation that changed during verification.
        if os.path.lexists(target) != present or (present and _inventory(target) != old_inventory):
            raise InstallError("installation changed during verification; retry after edits stop")
        if present and old_inventory == staged_inventory:
            return {"status": "unchanged", "target": str(target), "backup": None,
                    "archive_sha256": digest}
        reviewed.unlink()
        try:
            if present:
                os.rename(target, backup)
            os.rename(stage, target)
            if _inventory(target) != staged_inventory:
                raise InstallError("installed inventory differs from the verified staged tree")
        except BaseException:
            try:
                # A signal may arrive after rename completed but before Python
                # records its return; inspect filesystem state, not phase flags.
                if not os.path.lexists(stage) and os.path.lexists(target):
                    os.rename(target, stage)
                if os.path.lexists(backup):
                    os.rename(backup, target)
            except BaseException as rollback_error:
                keep_work = True
                raise InstallError(f"rollback failed; preserve recovery files at {work}: {rollback_error}") from rollback_error
            raise
        keep_work = present
        return {"status": "installed", "target": str(target),
                "backup": str(backup) if present else None, "archive_sha256": digest}
    finally:
        if not keep_work:
            shutil.rmtree(work)


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path, help="reviewed local runtime ZIP")
    parser.add_argument("--sha256", required=True, help="separately reviewed release digest")
    parser.add_argument("--skills-dir", required=True, type=Path, help="existing skills directory")
    args = parser.parse_args(argv)
    try:
        result = install_archive(args.archive, args.sha256, args.skills_dir)
    except (InstallError, OSError, ValueError, zipfile.BadZipFile) as exc:
        print(json.dumps({"status": "fail", "error": str(exc)}))
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
