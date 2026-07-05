#!/usr/bin/env python3
"""Error log parser for debugging skill.
Extracts errors, exceptions, and stack traces from log files.
"""

import json
import re
import sys
from pathlib import Path


def extract_errors(log_content: str) -> list[dict]:
    """Extract errors and exceptions from log content."""
    errors = []

    patterns = {
        "error": re.compile(r"(?i)(error|ERROR):\s*(.+?)(?:\n|$)"),
        "exception": re.compile(r"(?i)(exception|Exception|EXCEPTION):\s*(.+?)(?:\n|$)"),
        "fatal": re.compile(r"(?i)(fatal|FATAL):\s*(.+?)(?:\n|$)"),
        "critical": re.compile(r"(?i)(critical|CRITICAL):\s*(.+?)(?:\n|$)"),
        "traceback": re.compile(r"Traceback \(most recent call last\):(.+?)(?=\n\w|\Z)", re.DOTALL),
    }

    lines = log_content.split("\n")
    for i, line in enumerate(lines):
        for error_type, pattern in patterns.items():
            match = pattern.search(line)
            if match:
                error = {
                    "type": error_type,
                    "message": (match.group(2) if len(match.groups()) > 1 else match.group(0)),
                    "line_number": i + 1,
                    "line_content": line,
                    "timestamp": extract_timestamp(line),
                }

                if error_type == "traceback":
                    error["stack_trace"] = match.group(1).strip()

                errors.append(error)

    return errors


def extract_timestamp(line: str) -> str | None:
    """Extract timestamp from log line if present."""
    timestamp_patterns = [
        r"(\d{4}-\d{2}-\d{2}[\sT]\d{2}:\d{2}:\d{2})",
        r"(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2})",
        r"\[(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\]",
    ]

    for pattern in timestamp_patterns:
        match = re.search(pattern, line)
        if match:
            return match.group(1)

    return None


def group_errors_by_type(errors: list[dict]) -> dict[str, list[dict]]:
    """Group errors by type."""
    grouped: dict[str, list[dict]] = {}
    for error in errors:
        error_type = error["type"]
        if error_type not in grouped:
            grouped[error_type] = []
        grouped[error_type].append(error)
    return grouped


def analyze_error_patterns(errors: list[dict]) -> dict:
    """Analyze error patterns and provide insights."""
    if not errors:
        return {}

    type_counts: dict[str, int] = {}
    for error in errors:
        error_type = error["type"]
        type_counts[error_type] = type_counts.get(error_type, 0) + 1

    message_counts: dict[str, int] = {}
    for error in errors:
        message = error.get("message", "")[:100]
        message_counts[message] = message_counts.get(message, 0) + 1

    most_common = sorted(message_counts.items(), key=lambda x: x[1], reverse=True)[:5]

    return {
        "total_errors": len(errors),
        "by_type": type_counts,
        "most_common_errors": [{"message": msg, "count": count} for msg, count in most_common],
    }


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: parse_logs.py <log_file>")
        sys.exit(1)

    log_file = Path(sys.argv[1])
    if not log_file.exists():
        print(f"Error: File not found: {log_file}")
        sys.exit(1)

    log_content = log_file.read_text()

    errors = extract_errors(log_content)

    analysis = analyze_error_patterns(errors)

    output = {
        "file": str(log_file),
        "errors": errors,
        "analysis": analysis,
        "grouped_by_type": group_errors_by_type(errors),
    }

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
