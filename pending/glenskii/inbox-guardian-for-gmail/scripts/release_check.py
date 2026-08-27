#!/usr/bin/env python3
"""Validate the public release contract without reading mailbox data."""

from __future__ import annotations

import re
import sys
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
REQUIRED_FILES = (
    "SKILL.md",
    "README.md",
    "LICENSE",
    "SECURITY.md",
    "guardian.py",
    "guardian_storage.py",
    "requirements.txt",
    "docs/google-oauth-setup.md",
    "docs/safety-model.md",
    "docs/scheduled-runs.md",
    "references/operating-model.md",
)
PRIVATE_ARTIFACTS = (
    "credentials.json",
    "token.json",
    "config.json",
    "guardian.log",
    "guardian_stats.json",
    "sender_reputation.db",
    "guardian_review_*.json",
    "guardian_review.key",
    "guardian_unsubscribe_review_*.json",
    "dashboard.html",
)


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def read(relative_path: str) -> str:
    return (SKILL_DIR / relative_path).read_text(encoding="utf-8")


def main() -> None:
    for relative_path in REQUIRED_FILES:
        if not (SKILL_DIR / relative_path).is_file():
            fail(f"missing required file: {relative_path}")

    skill_text = read("SKILL.md")
    readme = read("README.md")
    guardian = read("guardian.py")
    ignored = read(".gitignore")
    license_text = read("LICENSE")

    skill_version = re.search(r"^\s+version:\s*([0-9]+\.[0-9]+\.[0-9]+)\s*$", skill_text, re.M)
    code_version = re.search(r'^__version__\s*=\s*"([0-9]+\.[0-9]+\.[0-9]+)"', guardian, re.M)
    if not skill_version or not code_version:
        fail("semantic version is missing from SKILL.md or guardian.py")
    version = code_version.group(1)
    if skill_version.group(1) != version or f"v{version}" not in readme:
        fail("semantic version differs across SKILL.md, guardian.py, and README.md")

    if "license: MIT" not in skill_text or not license_text.startswith("MIT License"):
        fail("MIT license metadata and LICENSE file must agree")

    for artifact in PRIVATE_ARTIFACTS:
        if artifact not in ignored:
            fail(f"private artifact is not ignored: {artifact}")

    for unsupported in ("--install-scheduler", "--uninstall-scheduler", "--hard-delete", "--confirm-destructive", ".messages().delete("):
        if unsupported in readme:
            fail(f"README advertises unsupported command: {unsupported}")

    if ".messages().delete(" in guardian:
        fail("guardian.py must not contain irreversible Gmail deletion")

    for relative_path in ("SKILL.md", "README.md", "SECURITY.md", "docs/google-oauth-setup.md"):
        if "—" in read(relative_path):
            fail(f"em dash found in {relative_path}")

    print(f"PASS: Inbox Guardian for Gmail v{version} release contract is valid.")


if __name__ == "__main__":
    main()
