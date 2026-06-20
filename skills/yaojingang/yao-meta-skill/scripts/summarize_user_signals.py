#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
SCRIPT_INTERFACE = "cli"
SCRIPT_INTERFACE_REASON = "Scans an explicit local source file and summarizes redacted repeated user preference signals."

TEXT_FIELDS = ("text", "message", "content", "excerpt", "prompt", "note", "body")
HISTORY_FILENAMES = {".zsh_history", ".bash_history", ".fish_history", "History"}
SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_-]{12,}"),
    re.compile(r"AKIA[0-9A-Z]{12,}"),
    re.compile(r"(?i)\b(api[_-]?key|token|password|secret)\b\s*[:=]\s*[^\s,;]+"),
]
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
LOCAL_PATH_RE = re.compile(r"/Users/[^\s'\"<>]+")

PATTERN_RULES = [
    {
        "pattern_id": "language_default",
        "label": "Default language preference",
        "signal_type": "report-language",
        "keywords": ["中文", "简体", "默认中文", "英文", "双语", "language", "bilingual", "chinese", "english"],
        "recommended_action": "Keep generated reports Chinese-first with an English switch where user-facing.",
    },
    {
        "pattern_id": "report_ui",
        "label": "Report UI and visualization preference",
        "signal_type": "artifact-design",
        "keywords": ["报告", "html", "图表", "排版", "ui", "kami", "白底", "模块", "导航", "report", "chart", "layout"],
        "recommended_action": "Prioritize white-background Kami-style reports with readable charts and stable navigation.",
    },
    {
        "pattern_id": "approval_safety",
        "label": "Approval and privacy boundary",
        "signal_type": "governance",
        "keywords": ["审批", "授权", "不要扫描", "隐私", "私人", "日志", "明确路径", "回滚", "提案", "批准", "approval", "privacy", "private", "proposal", "rollback"],
        "recommended_action": "Keep adaptive work proposal-only until a reviewer approves an allowlisted patch path.",
    },
    {
        "pattern_id": "delivery_format",
        "label": "Delivery format preference",
        "signal_type": "artifact-format",
        "keywords": ["markdown", "pdf", "word", "docx", "html", "地址", "路径", "打开", "输出", "交付"],
        "recommended_action": "Surface stable artifact paths and formats in CLI output and generated summaries.",
    },
    {
        "pattern_id": "evidence_testing",
        "label": "Evidence and testing preference",
        "signal_type": "quality-gate",
        "keywords": ["测试", "验证", "ci", "证据", "覆盖", "github", "push", "evidence", "review"],
        "recommended_action": "Attach focused tests and refreshed evidence reports to every non-trivial skill upgrade.",
    },
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def display_path(path: Path, skill_dir: Path) -> str:
    try:
        return str(path.resolve().relative_to(skill_dir.resolve()))
    except ValueError:
        return f"[external-explicit-source]/{path.name}"


def resolve_output(skill_dir: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else skill_dir / path


def source_fingerprint(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def redact_text(text: str) -> str:
    redacted = text
    for pattern in SECRET_PATTERNS:
        redacted = pattern.sub("[REDACTED_SECRET]", redacted)
    redacted = EMAIL_RE.sub("[REDACTED_EMAIL]", redacted)
    redacted = LOCAL_PATH_RE.sub("[LOCAL_PATH]", redacted)
    redacted = re.sub(r"\s+", " ", redacted).strip()
    if len(redacted) > 240:
        return redacted[:237].rstrip() + "..."
    return redacted


def extract_text(raw: Any) -> str:
    if isinstance(raw, str):
        return raw
    if not isinstance(raw, dict):
        return ""
    for field in TEXT_FIELDS:
        value = raw.get(field)
        if isinstance(value, str) and value.strip():
            return value
    messages = raw.get("messages")
    if isinstance(messages, list):
        parts = []
        for item in messages:
            if isinstance(item, dict):
                content = item.get("content")
                if isinstance(content, str):
                    parts.append(content)
            elif isinstance(item, str):
                parts.append(item)
        return "\n".join(parts)
    return ""


def load_records(source: Path) -> tuple[list[dict[str, str]], list[str]]:
    records: list[dict[str, str]] = []
    failures: list[str] = []
    text = source.read_text(encoding="utf-8", errors="replace")
    if source.suffix.lower() == ".jsonl":
        for index, line in enumerate(text.splitlines(), start=1):
            if not line.strip():
                continue
            try:
                raw = json.loads(line)
            except json.JSONDecodeError as exc:
                failures.append(f"line {index}: invalid JSONL source: {exc.msg}")
                continue
            extracted = extract_text(raw)
            if not extracted.strip():
                failures.append(f"line {index}: no supported text field found")
                continue
            records.append({"record_id": f"line-{index}", "excerpt": redact_text(extracted)})
    else:
        for index, line in enumerate(text.splitlines(), start=1):
            if line.strip():
                records.append({"record_id": f"line-{index}", "excerpt": redact_text(line)})
    return records, failures


def classify_patterns(records: list[dict[str, str]], min_support: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    patterns: list[dict[str, Any]] = []
    discarded: list[dict[str, Any]] = []
    for rule in PATTERN_RULES:
        matches = []
        for record in records:
            lowered = record["excerpt"].lower()
            if any(keyword.lower() in lowered for keyword in rule["keywords"]):
                matches.append(record)
        if not matches:
            continue
        item = {
            "pattern_id": rule["pattern_id"],
            "label": rule["label"],
            "signal_type": rule["signal_type"],
            "support_count": len(matches),
            "confidence": min(0.95, round(0.55 + (0.12 * len(matches)), 2)),
            "reason": f"{len(matches)} redacted records matched repeated {rule['signal_type']} signals.",
            "recommended_action": rule["recommended_action"],
            "evidence": matches[:3],
        }
        if len(matches) >= min_support:
            patterns.append(item)
        else:
            discarded.append({**item, "discard_reason": f"support_count below min_support {min_support}"})
    return patterns, discarded


def build_report(
    skill_dir: Path,
    source: Path,
    min_support: int,
    generated_at: str,
    allow_history_source: bool,
) -> dict[str, Any]:
    skill_dir = skill_dir.resolve()
    source = source.resolve()
    failures: list[str] = []
    records: list[dict[str, str]] = []
    fingerprint = ""
    if not source.exists():
        failures.append(f"Explicit source does not exist: {display_path(source, skill_dir)}")
    elif not source.is_file():
        failures.append(f"Explicit source must be a file: {display_path(source, skill_dir)}")
    elif source.name in HISTORY_FILENAMES and not allow_history_source:
        failures.append(f"Refusing private history source by default: {source.name}")
    else:
        fingerprint = source_fingerprint(source)
        records, load_failures = load_records(source)
        failures.extend(load_failures)
    patterns, discarded = classify_patterns(records, min_support) if not failures else ([], [])
    return {
        "ok": not failures,
        "schema_version": "1.0",
        "generated_at": generated_at,
        "skill_dir": display_path(skill_dir, skill_dir),
        "source": {
            "label": source.name,
            "path": display_path(source, skill_dir),
            "fingerprint_sha256": fingerprint,
            "explicit_source": True,
            "record_count": len(records),
        },
        "privacy_contract": {
            "local_only": True,
            "explicit_source_required": True,
            "implicit_private_log_scan": False,
            "raw_content_stored": False,
            "redacted_excerpts_only": True,
            "redacted_excerpt_limit": 240,
            "writes_repository_files": False,
        },
        "summary": {
            "record_count": len(records),
            "pattern_count": len(patterns),
            "discarded_signal_count": len(discarded),
            "min_support": min_support,
            "failure_count": len(failures),
        },
        "patterns": patterns,
        "discarded_signals": discarded,
        "failures": failures,
        "artifacts": {
            "json": "reports/user_patterns.json",
            "markdown": "reports/user_patterns.md",
        },
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# User Pattern Summary",
        "",
        f"- Generated at: `{report['generated_at']}`",
        f"- Local only: `{str(report['privacy_contract']['local_only']).lower()}`",
        f"- Explicit source: `{report['source']['path']}`",
        f"- Records: `{report['summary']['record_count']}`",
        f"- Patterns: `{report['summary']['pattern_count']}`",
        f"- Discarded signals: `{report['summary']['discarded_signal_count']}`",
        "",
        "## Privacy Contract",
        "",
        "- No implicit private log scan.",
        "- No unredacted raw content stored.",
        "- Scan and proposal stages do not write source files.",
        "",
        "## Patterns",
        "",
    ]
    if not report["patterns"]:
        lines.append("- No repeated pattern met the support threshold.")
    for pattern in report["patterns"]:
        lines.extend(
            [
                f"### {pattern['label']}",
                "",
                f"- Pattern: `{pattern['pattern_id']}`",
                f"- Support: `{pattern['support_count']}`",
                f"- Confidence: `{pattern['confidence']}`",
                f"- Reason: {pattern['reason']}",
                f"- Recommended action: {pattern['recommended_action']}",
                "- Redacted evidence:",
            ]
        )
        for item in pattern["evidence"]:
            lines.append(f"  - `{item['record_id']}`: {item['excerpt']}")
        lines.append("")
    if report["discarded_signals"]:
        lines.extend(["## Discarded Signals", ""])
        for item in report["discarded_signals"]:
            lines.append(f"- `{item['pattern_id']}`: {item['discard_reason']}")
    if report["failures"]:
        lines.extend(["", "## Failures", ""])
        lines.extend(f"- {failure}" for failure in report["failures"])
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize repeated user preference signals from one explicit local source file.")
    parser.add_argument("skill_dir", nargs="?", default=".")
    parser.add_argument("--source", required=True)
    parser.add_argument("--output-json", default="reports/user_patterns.json")
    parser.add_argument("--output-md", default="reports/user_patterns.md")
    parser.add_argument("--min-support", type=int, default=2)
    parser.add_argument("--generated-at", default=utc_now())
    parser.add_argument("--allow-history-source", action="store_true")
    args = parser.parse_args()

    skill_dir = Path(args.skill_dir).resolve()
    report = build_report(
        skill_dir,
        Path(args.source),
        min_support=max(2, args.min_support),
        generated_at=args.generated_at,
        allow_history_source=args.allow_history_source,
    )
    if report["ok"]:
        output_json = resolve_output(skill_dir, args.output_json)
        output_md = resolve_output(skill_dir, args.output_md)
        output_json.parent.mkdir(parents=True, exist_ok=True)
        output_md.parent.mkdir(parents=True, exist_ok=True)
        report["artifacts"] = {
            "json": display_path(output_json, skill_dir),
            "markdown": display_path(output_md, skill_dir),
        }
        output_json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        output_md.write_text(render_markdown(report), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not report["ok"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
