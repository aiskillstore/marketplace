#!/usr/bin/env python3
"""Source loading and package scanning helpers for skill overview reports."""

import json
import re
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


SCRIPT_INTERFACE = "internal-module"
SCRIPT_INTERFACE_REASON = "Imported by skill_report_model.py to load source files and scan overview package assets."


KNOWN_ENTRIES = [
    ("SKILL.md", "Skill entrypoint"),
    ("README.md", "Human-readable usage guide"),
    ("agents/interface.yaml", "Neutral interface metadata"),
    ("manifest.json", "Lifecycle and portability metadata"),
    ("references", "Extended guidance and reusable notes"),
    ("scripts", "Deterministic helpers or local tooling"),
    ("evals", "Trigger and quality checks"),
    ("reports", "Generated evidence and overview artifacts"),
]

IGNORED_PACKAGE_PARTS = {".git", "__pycache__", ".venv", "venv", "node_modules", "dist"}


def parse_frontmatter(text: str) -> tuple[dict, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text
    try:
        end_index = lines[1:].index("---") + 1
    except ValueError:
        return {}, text
    frontmatter_text = "\n".join(lines[1:end_index])
    body = "\n".join(lines[end_index + 1 :]).lstrip()
    if yaml is not None:
        data = yaml.safe_load(frontmatter_text) or {}
        return data if isinstance(data, dict) else {}, body
    data = {}
    for line in frontmatter_text.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"')
    return data, body


def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    if yaml is not None:
        payload = yaml.safe_load(text) or {}
        return payload if isinstance(payload, dict) else {}
    return {}


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def extract_title(body: str, fallback: str) -> str:
    for line in body.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def parse_sections(body: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current = "_preamble"
    sections[current] = []
    for line in body.splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            sections[current] = []
            continue
        sections[current].append(line)
    return {name: "\n".join(lines).strip() for name, lines in sections.items()}


def extract_list_items(text: str) -> list[str]:
    items = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        ordered = re.match(r"^\d+\.\s+(.*)$", stripped)
        bullet = re.match(r"^[-*]\s+(.*)$", stripped)
        match = ordered or bullet
        if match:
            items.append(match.group(1).strip())
    return items


def summarize_logic(sections: dict[str, str]) -> list[str]:
    for key in ("Compact Workflow", "Workflow", "How It Works", "Logic", "Quick Start"):
        if key in sections:
            items = extract_list_items(sections[key])
            if items:
                return items[:5]
    return extract_list_items(sections.get("_preamble", ""))[:5] or [
        "Understand the request",
        "Execute the main task",
        "Validate the result",
    ]


def summarize_usage(sections: dict[str, str], default_prompt: str, description: str) -> list[str]:
    for key in ("How To Use", "Quick Start", "Usage", "Runbook"):
        if key in sections:
            items = extract_list_items(sections[key])
            if items:
                return items[:5]
    usage = []
    if default_prompt:
        usage.append(default_prompt)
    usage.append(f"Use this skill when the request matches: {description}")
    return usage[:5]


def package_entries(skill_dir: Path) -> list[dict]:
    items = []
    for rel_path, label in KNOWN_ENTRIES:
        target = skill_dir / rel_path
        if target.exists():
            kind = "folder" if target.is_dir() else "file"
            if target.is_dir():
                count = len(
                    [
                        path
                        for path in target.rglob("*")
                        if path.is_file()
                        and not path.is_symlink()
                        and not any(part in IGNORED_PACKAGE_PARTS for part in path.relative_to(target).parts)
                        and path.suffix not in {".pyc", ".pyo"}
                    ]
                )
            else:
                count = 1
            items.append({"path": rel_path, "label": label, "kind": kind, "file_count": count})
    return items
