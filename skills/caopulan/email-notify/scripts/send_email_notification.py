#!/usr/bin/env python3
import argparse
import os
import re
import smtplib
import sys
from email.message import EmailMessage
from pathlib import Path
from typing import List, Optional


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
        r"^\s*Project\s*Name\s*:\s*(.+?)\s*$",
        r"^\s*Project\s*:\s*(.+?)\s*$",
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


def _parse_bool_env(name: str, default: bool) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized in ("1", "true", "yes", "on"):
        return True
    if normalized in ("0", "false", "no", "off"):
        return False
    raise ValueError(f"Invalid {name} value: {value}")


def _split_recipients(value: str) -> List[str]:
    parts = re.split(r"[;,]", value)
    return [part.strip() for part in parts if part.strip()]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Send an SMTP email notification for a Codex task."
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
    smtp_host = os.environ.get("CODEX_EMAIL_SMTP_HOST")
    smtp_port_raw = os.environ.get("CODEX_EMAIL_SMTP_PORT", "587")
    smtp_user = os.environ.get("CODEX_EMAIL_USERNAME")
    smtp_password = os.environ.get("CODEX_EMAIL_PASSWORD")
    smtp_from = os.environ.get("CODEX_EMAIL_FROM")
    smtp_to_raw = os.environ.get("CODEX_EMAIL_TO")

    if not machine_name:
        sys.stderr.write("Missing CODEX_MACHINE_NAME.\n")
        return 1
    if not smtp_host:
        sys.stderr.write("Missing CODEX_EMAIL_SMTP_HOST.\n")
        return 1
    if not smtp_from:
        sys.stderr.write("Missing CODEX_EMAIL_FROM.\n")
        return 1
    if not smtp_to_raw:
        sys.stderr.write("Missing CODEX_EMAIL_TO.\n")
        return 1
    if smtp_user and not smtp_password:
        sys.stderr.write("Missing CODEX_EMAIL_PASSWORD.\n")
        return 1
    if smtp_password and not smtp_user:
        sys.stderr.write("Missing CODEX_EMAIL_USERNAME.\n")
        return 1

    try:
        smtp_port = int(smtp_port_raw)
    except ValueError:
        sys.stderr.write("CODEX_EMAIL_SMTP_PORT must be an integer.\n")
        return 1

    try:
        use_tls = _parse_bool_env("CODEX_EMAIL_USE_TLS", True)
        use_ssl = _parse_bool_env("CODEX_EMAIL_USE_SSL", False)
    except ValueError as exc:
        sys.stderr.write(f"{exc}\n")
        return 1
    if use_tls and use_ssl:
        sys.stderr.write("Set only one of CODEX_EMAIL_USE_TLS or CODEX_EMAIL_USE_SSL.\n")
        return 1

    recipients = _split_recipients(smtp_to_raw)
    if not recipients:
        sys.stderr.write("CODEX_EMAIL_TO must contain at least one recipient.\n")
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

    msg = EmailMessage()
    msg["Subject"] = task_title
    msg["From"] = smtp_from
    msg["To"] = ", ".join(recipients)
    msg.set_content(body)

    if args.dry_run:
        print("SMTP host:", smtp_host)
        print("SMTP port:", smtp_port)
        print("use TLS:", use_tls)
        print("use SSL:", use_ssl)
        print("from:", smtp_from)
        print("to:", ", ".join(recipients))
        print("subject:", task_title)
        print("body:", body)
        return 0

    try:
        if use_ssl:
            client: smtplib.SMTP = smtplib.SMTP_SSL(
                smtp_host, smtp_port, timeout=args.timeout
            )
        else:
            client = smtplib.SMTP(smtp_host, smtp_port, timeout=args.timeout)
        with client:
            client.ehlo()
            if use_tls:
                client.starttls()
                client.ehlo()
            if smtp_user:
                client.login(smtp_user, smtp_password)
            client.send_message(msg)
    except smtplib.SMTPException as exc:
        sys.stderr.write(f"Failed to send email notification: {exc}\n")
        return 1
    except Exception as exc:  # pragma: no cover - network errors vary
        sys.stderr.write(f"Failed to send email notification: {exc}\n")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
