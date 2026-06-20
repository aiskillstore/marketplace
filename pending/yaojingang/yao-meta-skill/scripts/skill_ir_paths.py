#!/usr/bin/env python3
"""Shared Skill IR artifact discovery helpers."""

import json
from pathlib import Path
from typing import Any


SCRIPT_INTERFACE = "internal-module"
SCRIPT_INTERFACE_REASON = "Imported by compiler, registry, conformance, and report scripts to locate canonical Skill IR artifacts."


def display_path(path: Path, root: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path.resolve())


def candidate_paths(skill_dir: Path, name: str) -> list[Path]:
    candidates = [
        skill_dir / "reports" / "skill-ir.json",
        skill_dir / "skill-ir" / "examples" / f"{name}.json",
        skill_dir / "skill-ir" / "examples" / f"{skill_dir.name}.json",
    ]
    examples_dir = skill_dir / "skill-ir" / "examples"
    if examples_dir.exists():
        for path in sorted(examples_dir.glob("*.json")):
            if path not in candidates:
                candidates.append(path)
    seen: set[Path] = set()
    unique: list[Path] = []
    for path in candidates:
        if path in seen:
            continue
        seen.add(path)
        unique.append(path)
    return unique


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def find_skill_ir_path(skill_dir: Path, name: str, *, require_schema: bool = False, fallback_source: str = "") -> str:
    for path in candidate_paths(skill_dir, name):
        payload = load_json(path)
        if not payload:
            continue
        if require_schema and not payload.get("schema_version"):
            continue
        return display_path(path, skill_dir)
    return fallback_source


def find_skill_ir(
    skill_dir: Path,
    name: str,
    *,
    require_schema: bool = False,
    fallback_source: str = "",
) -> tuple[dict[str, Any], str]:
    for path in candidate_paths(skill_dir, name):
        payload = load_json(path)
        if not payload:
            continue
        if require_schema and not payload.get("schema_version"):
            continue
        return payload, display_path(path, skill_dir)
    return {}, fallback_source
