#!/usr/bin/env python3
"""Validate this repository as a release-ready Agent Skill."""

from __future__ import annotations

import json
import py_compile
import re
import sys
from pathlib import Path


REQUIRED_FILES = [
    "SKILL.md",
    "README.md",
    "LICENSE",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "CHANGELOG.md",
    "references/quality-checklist.md",
    "scripts/pdf_guardrails.py",
    "evals/evals.json",
]

FORBIDDEN_RELEASE_PATHS = [
    "output",
    "outputs",
    "uploads",
    "tmp",
    ".env",
]


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def parse_frontmatter(skill_md: Path) -> dict[str, str]:
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        fail("SKILL.md must start with YAML frontmatter")
    try:
        _, raw, _ = text.split("---", 2)
    except ValueError:
        fail("SKILL.md frontmatter is not closed")

    data: dict[str, str] = {}
    for line in raw.splitlines():
        if not line.strip():
            continue
        if ":" not in line:
            fail(f"Unsupported frontmatter line: {line!r}")
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"')
    return data


def has_files(path: Path) -> bool:
    if path.is_file():
        return True
    if not path.is_dir():
        return False
    return any(child.is_file() for child in path.rglob("*"))


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    if not root.exists():
        fail(f"Path does not exist: {root}")

    for rel in REQUIRED_FILES:
        if not (root / rel).is_file():
            fail(f"Missing required release file: {rel}")

    frontmatter = parse_frontmatter(root / "SKILL.md")
    name = frontmatter.get("name", "")
    description = frontmatter.get("description", "")

    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", name):
        fail("Skill name must be lowercase kebab-case, max 64 chars")
    if root.name != name:
        fail(f"Directory name {root.name!r} must match SKILL.md name {name!r}")
    if not description:
        fail("Skill description is required")
    if len(description) > 1024:
        fail("Skill description must be 1024 characters or fewer")
    if len(description) > 200:
        print("WARN: description exceeds 200 chars; Claude.ai uploads may reject it")

    evals_path = root / "evals/evals.json"
    try:
        evals = json.loads(evals_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"evals/evals.json is invalid JSON: {exc}")
    if evals.get("skill_name") != name:
        fail("evals/evals.json skill_name must match SKILL.md name")
    if not isinstance(evals.get("evals"), list) or not evals["evals"]:
        fail("evals/evals.json must include at least one eval")

    for rel in FORBIDDEN_RELEASE_PATHS:
        path = root / rel
        if has_files(path):
            fail(f"Release tree contains generated/private path with files: {rel}")

    for script in sorted((root / "scripts").glob("*.py")):
        py_compile.compile(str(script), doraise=True)

    print("Skill repository is release-ready.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
