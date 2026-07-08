#!/usr/bin/env python3
import argparse
import os
import re
import sys
from pathlib import Path
from typing import Optional
from urllib import error, parse, request


def _strip_quotes(value: str) -> str:
    value = value.strip()
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1].strip()
    return value


def _extract_project_name(text: str) -> Optional[str]:
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        for idx in range(1, len(lines)):
            if lines[idx].strip() == "---":
                for line in lines[1:idx]:
                    match = re.match(
                        r"\s*(project_name|project|name|title)\s*:\s*(.+)\s*$",
                        line,
                        re.IGNORECASE,
                    )
                    if match:
                        return _strip_quotes(match.group(2))
                break

    patterns = [
        r"^\s*Project\s*Name\s*[:：]\s*(.+?)\s*$",
        r"^\s*Project\s*[:：]\s*(.+?)\s*$",
        r"^\s*项目名称\s*[:：]\s*(.+?)\s*$",
        r"^\s*项目名\s*[:：]\s*(.+?)\s*$",
    ]
    for line in lines:
        for pattern in patterns:
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                return match.group(1).strip()

    return None


def _find_agents_file(start: Path) -> Optional[Path]:
    for candidate_root in [start] + list(start.parents):
        candidate = candidate_root / "AGENTS.md"
        if candidate.is_file():
            return candidate
    return None


def _get_project_name(cwd: Path) -> str:
    agents_path = _find_agents_file(cwd)
    if not agents_path:
        return cwd.name

    text = agents_path.read_text(encoding="utf-8", errors="ignore")
    extracted = _extract_project_name(text)
    if extracted:
        return extracted

    return agents_path.parent.name


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Send a Bark (day.app) push notification for a Codex task."
    )
    parser.add_argument("--task-title", required=True, help="Short task title.")
    parser.add_argument("--status", required=True, help="Execution status.")
    parser.add_argument("--summary", required=True, help="Result summary.")
    parser.add_argument("--project-name", help="Override project name.")
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    machine_name = os.environ.get("CODEX_MACHINE_NAME")
    bark_key = os.environ.get("CODEX_BARK_KEY")
    base_url = os.environ.get("CODEX_BARK_BASE_URL", "https://api.day.app")

    if not machine_name:
        sys.stderr.write("Missing CODEX_MACHINE_NAME.\n")
        return 1
    if not bark_key:
        sys.stderr.write("Missing CODEX_BARK_KEY.\n")
        return 1

    task_title = args.task_title.strip()
    status = args.status.strip()
    summary = args.summary.strip()
    if not task_title:
        sys.stderr.write("--task-title must be non-empty.\n")
        return 1
    if not summary:
        sys.stderr.write("--summary must be non-empty.\n")
        return 1

    project_name = args.project_name or _get_project_name(Path.cwd())

    body = "\n".join(
        [
            f"Device: {machine_name}",
            f"Project: {project_name}",
            f"Status: {status}",
            f"Summary: {summary}",
        ]
    )

    url = f"{base_url.rstrip('/')}/{parse.quote(bark_key)}"
    payload = parse.urlencode({"title": task_title, "body": body}).encode("utf-8")

    if args.dry_run:
        print("POST", url)
        print("title:", task_title)
        print("body:", body)
        return 0

    req = request.Request(url, data=payload, method="POST")
    try:
        with request.urlopen(req, timeout=args.timeout) as resp:
            response_body = resp.read().decode("utf-8", errors="ignore").strip()
    except error.HTTPError as exc:
        sys.stderr.write(f"HTTP {exc.code}: {exc.reason}\n")
        sys.stderr.write(exc.read().decode("utf-8", errors="ignore"))
        return 1
    except Exception as exc:  # pragma: no cover - network errors vary
        sys.stderr.write(f"Failed to send Bark notification: {exc}\n")
        return 1

    if response_body:
        print(response_body)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
