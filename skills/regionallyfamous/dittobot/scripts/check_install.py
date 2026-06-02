#!/usr/bin/env python3
"""Check whether the installed Dittobot skill matches this repo."""

from __future__ import annotations

import argparse
import hashlib
import os
import shlex
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from package_files import PACKAGE_FILES


IGNORED_EXTRA_NAMES = {".DS_Store"}
IGNORED_EXTRA_SUFFIXES = {".pyc"}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def package_files_in(path: Path) -> set[str]:
    files: set[str] = set()
    for item in path.rglob("*"):
        if not item.is_file():
            continue
        rel = item.relative_to(path)
        if any(part == "__pycache__" for part in rel.parts):
            continue
        if item.name in IGNORED_EXTRA_NAMES or item.suffix in IGNORED_EXTRA_SUFFIXES:
            continue
        files.add(rel.as_posix())
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--install-dir",
        default=os.path.expanduser("~/.agents/skills/dittobot"),
        help="Installed skill directory to compare.",
    )
    args = parser.parse_args()

    repo = Path(__file__).resolve().parents[1]
    install_path = Path(args.install_dir).expanduser()
    installed = install_path.resolve()

    if not installed.exists():
        print(f"Install missing: {install_path}")
        return 1

    mismatches: list[str] = []
    missing: list[str] = []
    source_missing: list[str] = []
    unexpected: list[str] = []

    for rel in PACKAGE_FILES:
        repo_file = repo / rel
        installed_file = installed / rel
        if not repo_file.exists():
            source_missing.append(rel)
        elif not installed_file.exists():
            missing.append(rel)
        elif digest(repo_file) != digest(installed_file):
            mismatches.append(rel)

    if not install_path.is_symlink():
        expected = set(PACKAGE_FILES)
        unexpected = sorted(package_files_in(installed) - expected)

    if source_missing or missing or mismatches or unexpected:
        print(f"Installed skill differs from repo: {installed}")
        for rel in source_missing:
            print(f"  source missing: {rel}")
        for rel in missing:
            print(f"  missing: {rel}")
        for rel in mismatches:
            print(f"  mismatch: {rel}")
        for rel in unexpected:
            print(f"  unexpected: {rel}")
        print("\nPrefer a symlink install to avoid drift:")
        quoted_install_path = shlex.quote(str(install_path))
        print(f"  mv {quoted_install_path} {quoted_install_path}.backup.$(date +%s)")
        print(f"  ln -s {shlex.quote(str(repo))} {quoted_install_path}")
        return 1

    if install_path.is_symlink():
        print(f"Installed skill matches repo (symlink): {install_path} -> {installed}")
    else:
        print(f"Installed skill matches repo (copy): {installed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
