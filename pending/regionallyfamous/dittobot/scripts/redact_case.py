#!/usr/bin/env python3
"""Redact a bad rewrite report and emit public-safe fixture scaffolding."""

from __future__ import annotations

import argparse
import json
import re
import shlex
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Pattern:
    label: str
    token: str
    regex: re.Pattern[str]


PATTERNS = (
    Pattern("private_key", "PRIVATE_KEY", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.DOTALL)),
    Pattern("api_key", "API_KEY", re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b")),
    Pattern("github_token", "GITHUB_TOKEN", re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{20,}\b|\bgithub_pat_[A-Za-z0-9_]{20,}\b")),
    Pattern("slack_token", "SLACK_TOKEN", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b")),
    Pattern("aws_key", "AWS_KEY", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    Pattern("jwt", "JWT", re.compile(r"\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b")),
    Pattern("bearer_token", "TOKEN", re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]{12,}")),
    Pattern("email", "EMAIL", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")),
    Pattern("url", "URL", re.compile(r"https?://[^\s)>\"]+")),
    Pattern("phone", "PHONE", re.compile(r"\b(?:\+?1[-. ]?)?\(?\d{3}\)?[-. ]?\d{3}[-. ]?\d{4}\b")),
    Pattern("uuid", "UUID", re.compile(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b")),
    Pattern("ip_address", "IP", re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")),
    Pattern("local_path", "LOCAL_PATH", re.compile(r"(?:/Users|/home)/[^\s)>\"]+|[A-Za-z]:\\Users\\[^\s)>\"]+")),
    Pattern("long_token", "TOKEN", re.compile(r"\b[A-Fa-f0-9]{32,}\b")),
)


def read_value(value: str | None, file_path: str | None, label: str) -> str:
    if value and file_path:
        raise SystemExit(f"Pass either --{label} or --{label}-file, not both.")
    if file_path:
        return Path(file_path).read_text(encoding="utf-8").strip()
    if value is not None:
        return value.strip()
    if label == "source" and not sys.stdin.isatty():
        return sys.stdin.read().strip()
    raise SystemExit(f"Missing --{label} or --{label}-file.")


def parse_replacements(values: list[str]) -> list[tuple[str, str]]:
    replacements: list[tuple[str, str]] = []
    for value in values:
        if "=" not in value:
            raise SystemExit("--replace values must use old=new")
        old, new = value.split("=", 1)
        old = old.strip()
        new = new.strip()
        if not old or not new:
            raise SystemExit("--replace values must include both old and new text")
        replacements.append((old, new))
    return replacements


def apply_explicit_replacements(text: str, replacements: list[tuple[str, str]]) -> tuple[str, list[dict[str, str | int]]]:
    records: list[dict[str, str | int]] = []
    for old, new in replacements:
        text, count = re.subn(re.escape(old), new, text)
        if count:
            records.append({"type": "explicit", "replacement": new, "count": count})
    return text, records


def redact_patterns(text: str) -> tuple[str, list[dict[str, str | int]]]:
    records: list[dict[str, str | int]] = []
    for pattern in PATTERNS:
        seen: dict[str, str] = {}

        def replace(match: re.Match[str]) -> str:
            raw = match.group(0)
            if raw not in seen:
                seen[raw] = f"[{pattern.token}_{len(seen) + 1}]"
            return seen[raw]

        text, count = pattern.regex.subn(replace, text)
        if count:
            records.append({"type": pattern.label, "replacement": pattern.token, "count": count})
    return text, records


def redact_text(text: str, replacements: list[tuple[str, str]]) -> tuple[str, list[dict[str, str | int]]]:
    text, explicit = apply_explicit_replacements(text, replacements)
    text, automatic = redact_patterns(text)
    return text, explicit + automatic


def remaining_sensitive(text: str) -> list[str]:
    found: list[str] = []
    for pattern in PATTERNS:
        if pattern.regex.search(text):
            found.append(pattern.label)
    return sorted(set(found))


def shell_command(args: list[str]) -> str:
    return " ".join(shlex.quote(arg) for arg in args)


def add_repeated(command: list[str], flag: str, values: list[str]) -> None:
    for value in values:
        if value.strip():
            command.extend([flag, value.strip()])


def markdown_block(label: str, text: str) -> str:
    return f"## {label}\n\n```text\n{text}\n```"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case-id", required=True, help="Case id for the generated fixture command.")
    parser.add_argument("--source", help="Original failing source. If omitted, stdin is used.")
    parser.add_argument("--source-file", help="File containing original failing source.")
    parser.add_argument("--rewrite", required=True, help="Bad Dittobot output.")
    parser.add_argument("--expected", required=True, help="Desired passing rewrite or expected behavior.")
    parser.add_argument("--replace", action="append", default=[], help="Explicit redaction as old=new.")
    parser.add_argument("--must", action="append", default=[], help="Required term or idea for case_lab.")
    parser.add_argument("--protected", action="append", default=[], help="Protected fact for case_lab.")
    parser.add_argument("--voice", action="append", default=[], help="Voice marker for case_lab.")
    parser.add_argument("--forbid", action="append", default=[], help="Forbidden term for case_lab.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    parser.add_argument(
        "--fail-on-redaction",
        action="store_true",
        help="Exit nonzero when any automatic or explicit redaction was needed.",
    )
    args = parser.parse_args()

    replacements = parse_replacements(args.replace)
    fields = {
        "source": read_value(args.source, args.source_file, "source"),
        "rewrite": args.rewrite.strip(),
        "expected": args.expected.strip(),
        "must": "\n".join(args.must),
        "protected": "\n".join(args.protected),
        "voice": "\n".join(args.voice),
        "forbid": "\n".join(args.forbid),
    }
    redacted: dict[str, str] = {}
    redactions: dict[str, list[dict[str, str | int]]] = {}
    remaining: dict[str, list[str]] = {}
    for field, value in fields.items():
        redacted_value, records = redact_text(value, replacements)
        redacted[field] = redacted_value
        redactions[field] = records
        remaining[field] = remaining_sensitive(redacted_value)

    redacted_must = [value for value in redacted["must"].splitlines() if value.strip()]
    redacted_protected = [value for value in redacted["protected"].splitlines() if value.strip()]
    redacted_voice = [value for value in redacted["voice"].splitlines() if value.strip()]
    redacted_forbid = [value for value in redacted["forbid"].splitlines() if value.strip()]
    command = [
        "python3",
        "scripts/case_lab.py",
        "--case-id",
        args.case_id,
        "--source",
        redacted["source"],
        "--rewrite",
        redacted["expected"],
    ]
    add_repeated(command, "--must", redacted_must)
    add_repeated(command, "--protected", redacted_protected)
    add_repeated(command, "--voice", redacted_voice)
    add_repeated(command, "--forbid", redacted_forbid)
    command_text = shell_command(command)

    total_redactions = sum(
        int(record["count"])
        for records in redactions.values()
        for record in records
    )
    remaining_types = sorted({item for items in remaining.values() for item in items})
    result = {
        "status": "REVIEW" if remaining_types else "OK",
        "case_id": args.case_id,
        "redacted": redacted,
        "redactions": redactions,
        "remaining_sensitive_types": remaining_types,
        "case_lab_command": command_text,
    }

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("# Redacted Bad Rewrite Report")
        print()
        print(f"Status: {result['status']}")
        print(f"Redactions applied: {total_redactions}")
        if remaining_types:
            print(f"Needs review: {', '.join(remaining_types)}")
        print()
        print(markdown_block("Source", redacted["source"]))
        print()
        print(markdown_block("Bad Output", redacted["rewrite"]))
        print()
        print(markdown_block("Expected", redacted["expected"]))
        print()
        print("## case_lab Command")
        print()
        print("```bash")
        print(command_text)
        print("```")
        print()
        print("## Privacy Checklist")
        print()
        print("- [ ] No real names, companies, customers, secrets, credentials, or private drafts remain.")
        print("- [ ] The redacted text still preserves the failure shape.")
        print("- [ ] Any placeholders are boring and reusable enough for a public fixture.")

    if remaining_types or (args.fail_on_redaction and total_redactions):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
