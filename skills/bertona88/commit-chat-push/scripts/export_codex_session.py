#!/usr/bin/env python3
"""Export a redacted Codex JSONL session transcript as Markdown."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shlex
import sys
from pathlib import Path
from typing import Any, Iterable


SECRET_PATTERNS = [
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.S),
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{30,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{12,}\b", re.I),
    re.compile(
        r"(?i)\b(password|passwd|pwd|secret|token|api[_-]?key|authorization|cookie)"
        r"(\s*[:=]\s*|[\"']\s*:\s*[\"'])"
        r"([^\"'\s,;}{]+)"
    ),
]


def parse_args() -> argparse.Namespace:
    default_root = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / "sessions"
    parser = argparse.ArgumentParser(
        description="Export a sanitized Markdown transcript from a Codex session JSONL file."
    )
    parser.add_argument("--repo", default=os.getcwd(), help="Repository path used to select a matching session.")
    parser.add_argument("--sessions-root", default=str(default_root), help="Root containing Codex session JSONL files.")
    parser.add_argument("--session", help="Specific Codex JSONL session to export.")
    parser.add_argument("--output-dir", default="docs/codex-sessions", help="Directory for generated transcript.")
    parser.add_argument("--output", help="Exact Markdown output path. Overrides --output-dir.")
    parser.add_argument("--title", help="Transcript title. Defaults to the Codex thread name or first user message.")
    parser.add_argument("--tool-output", choices=["none", "brief", "full"], default="none")
    parser.add_argument("--max-output-chars", type=int, default=4000, help="Per-stream limit when --tool-output=brief.")
    parser.add_argument("--include-local-paths", action="store_true", help="Include full local paths in metadata.")
    parser.add_argument("--no-redact", action="store_true", help="Disable built-in redaction.")
    return parser.parse_args()


def read_jsonl(path: Path) -> tuple[list[dict[str, Any]], int]:
    events: list[dict[str, Any]] = []
    invalid = 0
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if not line.strip():
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                invalid += 1
    return events, invalid


def first_session_meta(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            for index, line in enumerate(handle):
                if index > 100:
                    break
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if obj.get("type") == "session_meta":
                    payload = obj.get("payload")
                    return payload if isinstance(payload, dict) else {}
    except OSError:
        return {}
    return {}


def path_score(repo: Path, cwd_text: str | None) -> int:
    if not cwd_text:
        return 0
    try:
        repo_real = repo.resolve()
        cwd_real = Path(cwd_text).expanduser().resolve()
    except OSError:
        return 0
    if cwd_real == repo_real:
        return 4
    if cwd_real in repo_real.parents or repo_real in cwd_real.parents:
        return 3
    if str(cwd_real).startswith(str(repo_real)) or str(repo_real).startswith(str(cwd_real)):
        return 2
    return 0


def find_session(sessions_root: Path, repo: Path) -> tuple[Path, dict[str, Any], bool]:
    candidates: list[tuple[int, float, Path, dict[str, Any]]] = []
    for path in sessions_root.rglob("*.jsonl"):
        meta = first_session_meta(path)
        score = path_score(repo, meta.get("cwd"))
        try:
            mtime = path.stat().st_mtime
        except OSError:
            mtime = 0
        candidates.append((score, mtime, path, meta))
    if not candidates:
        raise SystemExit(f"No Codex sessions found under {sessions_root}")
    candidates.sort(key=lambda item: (item[0], item[1]), reverse=True)
    score, _, path, meta = candidates[0]
    return path, meta, score > 0


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def text_from_content(content: Any) -> str:
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""
    parts: list[str] = []
    for item in content:
        if not isinstance(item, dict):
            continue
        text = item.get("text") or item.get("content")
        if isinstance(text, str):
            parts.append(text)
    return "\n\n".join(part for part in parts if part)


def redact(text: str, *, enabled: bool = True) -> str:
    if not enabled:
        return text
    home = str(Path.home())
    if home:
        text = text.replace(home, "~")
    for pattern in SECRET_PATTERNS:
        def repl(match: re.Match[str]) -> str:
            if len(match.groups()) >= 3:
                return f"{match.group(1)}{match.group(2)}[REDACTED]"
            if match.group(0).lower().startswith("bearer "):
                return "Bearer [REDACTED]"
            return "[REDACTED]"

        text = pattern.sub(repl, text)
    return text


def truncate(text: str, limit: int) -> str:
    if limit <= 0 or len(text) <= limit:
        return text
    head = max(limit // 2, 0)
    tail = max(limit - head, 0)
    return text[:head].rstrip() + "\n\n[... truncated ...]\n\n" + text[-tail:].lstrip()


def fence(text: str, info: str = "") -> str:
    longest = max((len(match.group(0)) for match in re.finditer(r"`+", text)), default=0)
    ticks = "`" * max(3, longest + 1)
    suffix = info if info else ""
    return f"{ticks}{suffix}\n{text.rstrip()}\n{ticks}"


def slugify(text: str, fallback: str = "codex-session") -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", text.lower()).strip("-")
    slug = re.sub(r"-{2,}", "-", slug)
    return (slug[:72].strip("-") or fallback)


def iso_for_filename(value: str | None) -> str:
    if not value:
        return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    safe = value.replace(":", "-")
    safe = re.sub(r"\.\d+", "", safe)
    return safe.replace("+00-00", "Z")


def shell_command(command: Any) -> str:
    if isinstance(command, list):
        return " ".join(shlex.quote(str(part)) for part in command)
    if isinstance(command, str):
        return command
    return json.dumps(command, ensure_ascii=False)


def iter_message_records(events: Iterable[dict[str, Any]]) -> list[dict[str, str]]:
    event_messages: list[dict[str, str]] = []
    fallback_messages: list[dict[str, str]] = []
    for obj in events:
        timestamp = str(obj.get("timestamp") or "")
        payload = obj.get("payload") or {}
        if obj.get("type") == "event_msg":
            kind = payload.get("type")
            if kind == "user_message":
                message = str(payload.get("message") or "").strip()
                if message:
                    event_messages.append({"role": "User", "timestamp": timestamp, "text": message})
            elif kind == "agent_message":
                message = str(payload.get("message") or "").strip()
                if message:
                    phase = payload.get("phase")
                    role = "Assistant" + (f" ({phase})" if phase else "")
                    event_messages.append({"role": role, "timestamp": timestamp, "text": message})
        elif obj.get("type") == "response_item" and payload.get("type") == "message":
            role = payload.get("role")
            if role not in {"user", "assistant"}:
                continue
            text = text_from_content(payload.get("content")).strip()
            if not text or text.lstrip().startswith("<environment_context>"):
                continue
            fallback_messages.append({"role": role.title(), "timestamp": timestamp, "text": text})
    return event_messages or fallback_messages


def iter_activity_records(events: Iterable[dict[str, Any]], args: argparse.Namespace) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for obj in events:
        timestamp = str(obj.get("timestamp") or "")
        payload = obj.get("payload") or {}
        if obj.get("type") == "response_item" and payload.get("type") == "function_call":
            name = str(payload.get("name") or "tool")
            raw_arguments = payload.get("arguments")
            arguments = raw_arguments if isinstance(raw_arguments, str) else json.dumps(raw_arguments, indent=2)
            records.append(
                {
                    "kind": "tool_call",
                    "timestamp": timestamp,
                    "title": f"Tool Call: {name}",
                    "body": arguments or "{}",
                    "info": "json",
                }
            )
        elif obj.get("type") == "event_msg" and payload.get("type") == "exec_command_end":
            command = shell_command(payload.get("command"))
            status = str(payload.get("status") or "")
            exit_code = payload.get("exit_code")
            cwd = payload.get("cwd")
            lines = [f"status: {status}", f"exit_code: {exit_code}", ""]
            if cwd:
                lines.insert(0, f"cwd: {cwd}")
            lines.append(f"$ {command}")
            if args.tool_output != "none":
                for stream_name in ("stdout", "stderr", "aggregated_output"):
                    stream = payload.get(stream_name)
                    if not stream:
                        continue
                    stream_text = str(stream)
                    if args.tool_output == "brief":
                        stream_text = truncate(stream_text, args.max_output_chars)
                    lines.append("")
                    lines.append(f"{stream_name}:")
                    lines.append(stream_text.rstrip())
            records.append(
                {
                    "kind": "command",
                    "timestamp": timestamp,
                    "title": "Command Result",
                    "body": "\n".join(lines),
                    "info": "text",
                }
            )
    return records


def thread_name(events: Iterable[dict[str, Any]]) -> str | None:
    latest: str | None = None
    for obj in events:
        payload = obj.get("payload") or {}
        if obj.get("type") == "event_msg" and payload.get("type") == "thread_name_updated":
            name = payload.get("thread_name")
            if isinstance(name, str) and name.strip():
                latest = name.strip()
    return latest


def first_user_text(messages: Iterable[dict[str, str]]) -> str | None:
    for message in messages:
        if message.get("role", "").startswith("User"):
            text = message.get("text", "").strip()
            if text:
                return text.splitlines()[0][:120]
    return None


def render_markdown(
    *,
    events: list[dict[str, Any]],
    invalid_lines: int,
    session_path: Path,
    meta: dict[str, Any],
    matched_repo: bool,
    args: argparse.Namespace,
) -> str:
    messages = iter_message_records(events)
    activity = iter_activity_records(events, args)
    title = args.title or thread_name(events) or first_user_text(messages) or "Codex Session Transcript"
    digest = sha256_file(session_path)
    captured_at = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    redaction_enabled = not args.no_redact
    lines = [f"# {redact(title, enabled=redaction_enabled)}", ""]
    lines.extend(
        [
            "## Metadata",
            "",
            f"- Captured at: `{captured_at}`",
            f"- Session id: `{redact(str(meta.get('id') or 'unknown'), enabled=redaction_enabled)}`",
            f"- Session started: `{redact(str(meta.get('timestamp') or meta.get('started_at') or 'unknown'), enabled=redaction_enabled)}`",
            f"- Source file: `{redact(str(session_path if args.include_local_paths else session_path.name), enabled=redaction_enabled)}`",
            f"- Source SHA-256: `{digest}`",
            f"- Repository match: `{'yes' if matched_repo else 'not confirmed'}`",
        ]
    )
    if args.include_local_paths and meta.get("cwd"):
        lines.append(f"- Session cwd: `{redact(str(meta.get('cwd')), enabled=redaction_enabled)}`")
    if invalid_lines:
        lines.append(f"- Warning: `{invalid_lines}` invalid JSONL line(s) skipped, possibly from an active write.")
    lines.extend(
        [
            "",
            "> Exported by the commit-chat-push skill. Developer/system instructions, encrypted reasoning, token counts, and oversized raw logs are intentionally omitted.",
            "",
            "## Conversation",
            "",
        ]
    )
    if not messages:
        lines.extend(["_No user/assistant chat messages were found._", ""])
    for message in messages:
        heading = f"### {message['role']}"
        if message.get("timestamp"):
            heading += f" - {message['timestamp']}"
        lines.append(heading)
        lines.append("")
        lines.append(fence(redact(message.get("text", ""), enabled=redaction_enabled), "text"))
        lines.append("")

    lines.extend(["## Implementation Activity", ""])
    if not activity:
        lines.extend(["_No tool activity was found._", ""])
    for record in activity:
        heading = f"### {record['title']}"
        if record.get("timestamp"):
            heading += f" - {record['timestamp']}"
        body = redact(record.get("body", ""), enabled=redaction_enabled)
        lines.append(heading)
        lines.append("")
        lines.append(fence(body, record.get("info", "")))
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def resolve_output_path(
    args: argparse.Namespace,
    meta: dict[str, Any],
    events: list[dict[str, Any]],
    session_path: Path,
    repo: Path,
) -> Path:
    if args.output:
        output = Path(args.output).expanduser()
        return output if output.is_absolute() else repo / output
    messages = iter_message_records(events)
    title = args.title or thread_name(events) or first_user_text(messages) or "codex-session"
    started = iso_for_filename(str(meta.get("timestamp") or ""))
    short_id = str(meta.get("id") or session_path.stem)[-8:]
    filename = f"{started}-{slugify(title)}-{short_id}.md"
    output_dir = Path(args.output_dir).expanduser()
    if not output_dir.is_absolute():
        output_dir = repo / output_dir
    return output_dir / filename


def main() -> int:
    args = parse_args()
    repo = Path(args.repo).expanduser()
    if args.session:
        session_path = Path(args.session).expanduser()
        meta = first_session_meta(session_path)
        matched = path_score(repo, meta.get("cwd")) > 0
    else:
        session_path, meta, matched = find_session(Path(args.sessions_root).expanduser(), repo)
    if not session_path.exists():
        raise SystemExit(f"Session file does not exist: {session_path}")
    events, invalid = read_jsonl(session_path)
    if not meta:
        for obj in events:
            if obj.get("type") == "session_meta" and isinstance(obj.get("payload"), dict):
                meta = obj["payload"]
                break
    output_path = resolve_output_path(args, meta, events, session_path, repo)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    markdown = render_markdown(
        events=events,
        invalid_lines=invalid,
        session_path=session_path,
        meta=meta,
        matched_repo=matched,
        args=args,
    )
    output_path.write_text(markdown, encoding="utf-8")
    print(output_path)
    if not matched:
        print("warning: selected session did not clearly match the requested repo", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
