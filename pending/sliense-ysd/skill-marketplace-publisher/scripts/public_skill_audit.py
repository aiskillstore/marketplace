#!/usr/bin/env python3
"""Audit a skill tree for obvious public-publishing risks."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


TEXT_SUFFIXES = {
    ".md",
    ".txt",
    ".json",
    ".yaml",
    ".yml",
    ".py",
    ".sh",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".toml",
    ".ini",
    ".cfg",
    ".conf",
    ".csv",
    ".env",
}

PLACEHOLDER_HINTS = ("todo", "example", "placeholder", "changeme", "your-", "xxxx", "sample")


@dataclass
class Finding:
    severity: str
    kind: str
    file: str
    line: int
    text: str


HIGH_PATTERNS = [
    ("private_key", re.compile(r"BEGIN [A-Z ]*PRIVATE KEY")),
    ("openai_key", re.compile(r"\bsk-[A-Za-z0-9]{20,}\b")),
    ("github_token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b")),
    ("aws_access_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("google_api_key", re.compile(r"\bAIza[0-9A-Za-z\-_]{20,}\b")),
    ("slack_token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
]

MEDIUM_PATTERNS = [
    ("local_path", re.compile(r"(/Users/|/home/|C:\\\\Users\\\\)")),
    ("secret_hub", re.compile(r"(ai-shared/secrets|\.secrets/|authorized_keys|id_rsa|id_ed25519)")),
    ("dotenv_secret_name", re.compile(r"\b(API[_-]?KEY|ACCESS[_-]?TOKEN|SECRET[_-]?KEY|PASSWORD|PRIVATE[_-]?KEY)\b", re.I)),
]


def looks_text(path: Path) -> bool:
    return path.suffix.lower() in TEXT_SUFFIXES or path.name in {"SKILL.md", "LICENSE", "README.md"}


def is_placeholder(line: str) -> bool:
    lowered = line.lower()
    return any(hint in lowered for hint in PLACEHOLDER_HINTS)


def is_pattern_definition(line: str) -> bool:
    return "re.compile(" in line or "HIGH_PATTERNS" in line or "MEDIUM_PATTERNS" in line


def audit_file(path: Path, root: Path) -> list[Finding]:
    findings: list[Finding] = []
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return findings

    for line_no, line in enumerate(text.splitlines(), start=1):
        for kind, pattern in HIGH_PATTERNS:
            if pattern.search(line):
                findings.append(
                    Finding(
                        severity="HIGH",
                        kind=kind,
                        file=str(path.relative_to(root)),
                        line=line_no,
                        text=line.strip()[:240],
                    )
                )

        for kind, pattern in MEDIUM_PATTERNS:
            if pattern.search(line):
                severity = "MEDIUM"
                if kind == "dotenv_secret_name" and (is_placeholder(line) or is_pattern_definition(line)):
                    severity = "INFO"
                if kind in {"local_path", "secret_hub"} and is_pattern_definition(line):
                    severity = "INFO"
                findings.append(
                    Finding(
                        severity=severity,
                        kind=kind,
                        file=str(path.relative_to(root)),
                        line=line_no,
                        text=line.strip()[:240],
                    )
                )

    return findings


def summarize(findings: list[Finding]) -> dict[str, int]:
    counts = {"HIGH": 0, "MEDIUM": 0, "INFO": 0}
    for finding in findings:
        counts[finding.severity] = counts.get(finding.severity, 0) + 1
    return counts


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit a skill tree for public publishing risks.")
    parser.add_argument("skill_path", help="Absolute or relative path to the skill directory")
    parser.add_argument("--json", action="store_true", help="Print JSON output")
    args = parser.parse_args()

    root = Path(args.skill_path).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        print(f"Skill path does not exist or is not a directory: {root}", file=sys.stderr)
        return 1

    findings: list[Finding] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in {".git", "node_modules", "__pycache__"}]
        for filename in filenames:
            path = Path(dirpath) / filename
            if looks_text(path):
                findings.extend(audit_file(path, root))

    counts = summarize(findings)
    payload = {
        "skill_path": str(root),
        "summary": counts,
        "findings": [asdict(f) for f in findings],
    }

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"Public skill audit: {root}")
        print(
            f"Summary: HIGH={counts['HIGH']} MEDIUM={counts['MEDIUM']} INFO={counts['INFO']}"
        )
        if not findings:
            print("No obvious public-publishing risks found.")
        else:
            for finding in findings:
                print(
                    f"[{finding.severity}] {finding.kind} {finding.file}:{finding.line} {finding.text}"
                )

    return 2 if counts["HIGH"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
