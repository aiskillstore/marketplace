"""Minimal logger for AI Architect Lite.

Creates `.ai_context/03_ACTIVE_TASK.md` if missing and appends a four-part log entry.
Run from project root (where `.ai_context` should live).

Security: Only operates within specified project root. Validates paths to prevent traversal.

Type Annotations: Fully annotated for Python 3.8+ compatibility using PEP 484/563.
All functions have complete parameter and return type annotations.
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

TEMPLATE = """# Active Task Context

## Current Mission
- Title: (Please fill in)
- State: Drafting | Executing | Verifying | Blocked
- Owner: AI | Human
- Notes: 

## Development Log (Append Only)
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Append a log entry to .ai_context/03_ACTIVE_TASK.md")
    parser.add_argument("--root", default=".", help="Project root (default: current directory).")
    parser.add_argument("--note", required=True, help="Brief note (used when changes is empty).")
    parser.add_argument("--action", default="Memory Sync", help="Action title.")
    parser.add_argument("--changes", help="What changed in this step.")
    parser.add_argument("--outcome", help="Result or verification outcome.")
    parser.add_argument("--next", dest="next_steps", help="Next step or intent.")
    return parser.parse_args()


def ensure_active_task(ctx_root: Path) -> Path:
    """Create .ai_context directory and 03_ACTIVE_TASK.md if missing.
    
    Args:
        ctx_root: Path to .ai_context directory
        
    Returns:
        Path to 03_ACTIVE_TASK.md file
        
    Raises:
        ValueError: If ctx_root path is invalid or outside project
    """
    # Security: Validate path is within reasonable bounds
    try:
        ctx_root = ctx_root.resolve(strict=False)
    except (OSError, RuntimeError) as e:
        print(f"Error: Invalid path - {e}", file=sys.stderr)
        sys.exit(1)
    
    # Security: Prevent path traversal - ensure path doesn't contain suspicious patterns
    path_str = str(ctx_root)
    if ".." in path_str.split(ctx_root.anchor)[-1]:
        print(f"Error: Path traversal detected in {ctx_root}", file=sys.stderr)
        sys.exit(1)
        
    ctx_root.mkdir(parents=True, exist_ok=True)
    target = ctx_root / "03_ACTIVE_TASK.md"
    
    # Security: Ensure target file is within ctx_root after path resolution
    try:
        target.resolve().relative_to(ctx_root.resolve())
    except ValueError:
        print(f"Error: Target file outside context directory", file=sys.stderr)
        sys.exit(1)
    
    if not target.exists():
        target.write_text(TEMPLATE, encoding="utf-8")
        
    return target


def append_entry(target: Path, *, action: str, note: str, changes: str | None, outcome: str | None, next_steps: str | None) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [f"### [{timestamp}] Action: {action}", f"- Changes: {changes or note}"]
    lines.append(f"- Outcome: {outcome or '(Not specified)'}")
    lines.append(f"- Next: {next_steps or '(Not specified)'}")
    entry = "\n".join(lines) + "\n"

    content = target.read_text(encoding="utf-8")
    if "## Development Log (Append Only)" not in content:
        content += "\n## Development Log (Append Only)\n"
    content += entry
    target.write_text(content, encoding="utf-8")


def main() -> None:
    args = parse_args()
    ctx_root = Path(args.root).resolve() / ".ai_context"
    target = ensure_active_task(ctx_root)
    append_entry(
        target,
        action=args.action,
        note=args.note,
        changes=args.changes,
        outcome=args.outcome,
        next_steps=args.next_steps,
    )
    print(f"Appended log to {target}")


if __name__ == "__main__":
    main()
