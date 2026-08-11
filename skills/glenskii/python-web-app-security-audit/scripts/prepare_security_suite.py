#!/usr/bin/env python3
"""Copy the bundled security test suite into a project without overwriting it."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


def copy_file(source: Path, destination: Path) -> None:
    if destination.exists():
        print(f"Kept existing file: {destination}")
        return
    shutil.copy2(source, destination)
    print(f"Copied: {destination}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Copy the bundled Python web application security suite."
    )
    parser.add_argument("project", type=Path, help="Existing target project directory")
    args = parser.parse_args()

    project = args.project.resolve()
    source_root = Path(__file__).resolve().parent.parent
    source_suite = source_root / "security"
    target_suite = project / "security"

    if not project.is_dir():
        parser.error(f"Target project directory does not exist: {project}")
    if target_suite.exists():
        parser.error(
            f"Refusing to overwrite existing directory: {target_suite}. "
            "Review and merge the suite manually."
        )

    shutil.copytree(source_suite, target_suite, ignore=shutil.ignore_patterns("__pycache__"))
    print(f"Copied: {target_suite}")
    copy_file(source_root / "pytest.ini", project / "pytest.ini")
    copy_file(source_root / "requirements.txt", project / "requirements-security-audit.txt")
    print("Next: copy security/.env.test.template to security/.env.test and configure it.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
