#!/usr/bin/env python3
"""Install Dittobot into the local Codex skills directory."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from package_files import PACKAGE_FILES


def backup_path(target: Path) -> Path:
    while True:
        candidate = target.with_name(f"{target.name}.backup.{time.time_ns()}")
        if not candidate.exists() and not candidate.is_symlink():
            return candidate


def temp_copy_path(target: Path) -> Path:
    return target.with_name(f".{target.name}.tmp.{int(time.time())}.{os.getpid()}")


def is_repo_symlink(target: Path, repo: Path) -> bool:
    return target.is_symlink() and target.resolve() == repo


def preflight_package(repo: Path) -> None:
    missing = [rel for rel in PACKAGE_FILES if not (repo / rel).exists()]
    if missing:
        raise SystemExit(
            "Cannot install: package file(s) missing: " + ", ".join(missing)
        )


def install_copy(repo: Path, target: Path) -> None:
    target.mkdir(parents=True, exist_ok=True)
    for rel in PACKAGE_FILES:
        source = repo / rel
        destination = target / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--install-dir",
        default=os.path.expanduser("~/.agents/skills/dittobot"),
        help="Destination skill directory.",
    )
    parser.add_argument(
        "--copy",
        action="store_true",
        help="Copy files instead of creating a symlink.",
    )
    args = parser.parse_args()

    repo = Path(__file__).resolve().parents[1]
    target = Path(args.install_dir).expanduser()
    target.parent.mkdir(parents=True, exist_ok=True)
    temp_target = temp_copy_path(target) if args.copy else None

    try:
        if is_repo_symlink(target, repo) and not args.copy:
            print(f"Already installed as symlink: {target}", flush=True)
        else:
            if args.copy:
                preflight_package(repo)
                assert temp_target is not None
                if temp_target.exists():
                    shutil.rmtree(temp_target)
                install_copy(repo, temp_target)

            if target.exists() or target.is_symlink():
                backup = backup_path(target)
                shutil.move(str(target), str(backup))
                print(f"Backed up existing install to: {backup}", flush=True)

            if args.copy:
                assert temp_target is not None
                shutil.move(str(temp_target), str(target))
                print(f"Installed copy: {target}", flush=True)
            else:
                target.symlink_to(repo, target_is_directory=True)
                print(f"Installed symlink: {target} -> {repo}", flush=True)
    finally:
        if temp_target is not None and temp_target.exists():
            shutil.rmtree(temp_target)

    result = subprocess.run(
        [
            sys.executable,
            str(repo / "scripts" / "check_install.py"),
            "--install-dir",
            str(target),
        ],
        check=False,
    )
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
