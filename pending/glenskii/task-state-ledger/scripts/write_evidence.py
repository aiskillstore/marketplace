#!/usr/bin/env python3
"""Write a reviewed local evidence record inside a task-state directory."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


NODE_ID_PATTERN = re.compile(r"^[a-z][a-z0-9_-]{0,63}$")
SENSITIVE_PATTERNS = (
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----", re.IGNORECASE),
    re.compile(r"authorization\s*:\s*bearer\s+\S+", re.IGNORECASE),
    re.compile(r"(?:api[_-]?key|access[_-]?token|refresh[_-]?token|password|secret)\s*[:=]\s*['\"]?\S+", re.IGNORECASE),
)


def normalise_summary(value: str) -> str:
    summary = " ".join(value.split())
    if not summary:
        raise ValueError("Summary must contain visible text.")
    if len(summary) > 180:
        raise ValueError("Summary must be 180 characters or fewer.")
    return summary


def validate_node_id(value: str) -> str:
    if not NODE_ID_PATTERN.fullmatch(value):
        raise ValueError(
            "Node ID must start with a lowercase letter and use only lowercase letters, numbers, hyphens, or underscores."
        )
    return value


def contains_sensitive_content(content: str) -> bool:
    return any(pattern.search(content) for pattern in SENSITIVE_PATTERNS)


def safe_target(state_dir: Path, node_id: str) -> Path:
    evidence_dir = (state_dir / "evidence").resolve()
    evidence_dir.mkdir(parents=True, exist_ok=True)
    target = (evidence_dir / f"{node_id}.md").resolve()
    if target.parent != evidence_dir:
        raise ValueError("Evidence target escaped the evidence directory.")
    return target


def build_record(node_id: str, summary: str, content: str) -> str:
    return f"# Evidence: {node_id}\n\n**Summary:** {summary}\n\n---\n\n{content}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Write reviewed evidence within a local task-state directory."
    )
    parser.add_argument("--state-dir", required=True, type=Path)
    parser.add_argument("--node-id", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--content-file", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        node_id = validate_node_id(args.node_id)
        summary = normalise_summary(args.summary)
        content = (
            args.content_file.read_text(encoding="utf-8", errors="replace")
            if args.content_file
            else sys.stdin.read()
        )
        if contains_sensitive_content(content):
            raise ValueError(
                "Evidence appears to contain sensitive material. Redact it before writing a ledger record."
            )
        target = safe_target(args.state_dir, node_id)
        target.write_text(build_record(node_id, summary, content), encoding="utf-8")
    except (OSError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1

    relative_path = Path("evidence") / target.name
    print(f"Wrote evidence record: {relative_path.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
