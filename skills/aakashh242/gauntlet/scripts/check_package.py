#!/usr/bin/env python3
"""Offline checks for this Gauntlet package; not a general Agent Skills validator."""
from __future__ import annotations
import argparse
import ast
import json
from pathlib import Path
import re
import sys


def check(root: Path) -> dict:
    errors, warnings = [], []
    required = ["SKILL.md", "README.md", "LICENSE", "agents/openai.yaml",
                "assets/gauntlet-icon-128.png", "assets/gauntlet-icon-512.png",
                "scripts/gauntlet.py", "references/tracker.md", "references/sources.md",
                "tests/test_tracker.py", "evals/cases.json", "evals/triggers.json"]
    for name in required:
        if not (root / name).is_file():
            errors.append(f"Missing {name}")
    if not (root / "SKILL.md").is_file():
        return {"ok": False, "errors": errors, "warnings": warnings}
    skill = (root / "SKILL.md").read_text(encoding="utf-8")
    match = re.match(r"\A---\n(.*?)\n---\n(.+)\Z", skill, re.S)
    if not match:
        errors.append("SKILL.md must have frontmatter and nonempty body")
    else:
        # This release deliberately uses a small, predictable YAML subset.
        meta, body = match.groups()
        name = re.search(r"^name: ([a-z0-9]+(?:-[a-z0-9]+)*)$", meta, re.M)
        if not name or len(name[1]) > 64 or name[1] != root.name:
            errors.append("Invalid name or name-directory mismatch")
        desc = re.search(r'^description: (".*")$', meta, re.M)
        try:
            description = json.loads(desc[1]) if desc else ""
            if not 1 <= len(description) <= 1024:
                errors.append("Description missing or over 1024 characters")
        except json.JSONDecodeError:
            errors.append("Description must use valid quoted-string syntax")
        if len(skill.splitlines()) >= 500:
            errors.append("Entry point exceeds the under-500-line design target")
        if len(body.split()) > 3500:
            warnings.append("Large entry point; measure tokens for the intended model")
        compatibility = re.search(r'^compatibility: (".*")$', meta, re.M)
        if compatibility and len(json.loads(compatibility[1])) > 500:
            errors.append("Compatibility over 500 characters")
    checked_links = 0
    for file in root.rglob("*.md"):
        contents = file.read_text(encoding="utf-8")
        for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", contents):
            if re.match(r"[A-Za-z][A-Za-z0-9+.-]*:", target) or target.startswith("#"):
                continue
            target = target.split("#", 1)[0]
            resolved = (file.parent / target).resolve()
            if not resolved.is_relative_to(root.resolve()):
                errors.append(f"Out-of-package link in {file.relative_to(root)}: {target}")
            elif not resolved.exists():
                errors.append(f"Broken link in {file.relative_to(root)}: {target}")
            checked_links += 1
    python_count = 0
    for file in root.rglob("*.py"):
        try:
            ast.parse(file.read_text(encoding="utf-8"), filename=str(file))
            python_count += 1
        except SyntaxError as exc:
            errors.append(f"Invalid Python in {file.relative_to(root)}: {exc}")
    for file in root.rglob("*.json"):
        try:
            json.loads(file.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"Invalid JSON in {file.relative_to(root)}: {exc}")
    for file in root.rglob("*"):
        if file.is_symlink():
            errors.append(f"Symlink not allowed in distribution: {file.relative_to(root)}")
    return {"ok": not errors, "errors": errors, "warnings": warnings,
            "skill_lines": len(skill.splitlines()), "skill_words": len(skill.split()),
            "local_links_checked": checked_links, "python_files_checked": python_count,
            "note": "Package-specific offline checks, not the official skills-ref validator"}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("directory", nargs="?", default=str(Path(__file__).resolve().parents[1]))
    args = p.parse_args()
    try:
        result = check(Path(args.directory).expanduser().absolute())
        print(json.dumps(result, indent=2))
        return 0 if result["ok"] else 1
    except (OSError, ValueError) as exc:
        print(json.dumps({"ok":False,"error":str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
