#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from typing import Any

from render_adoption_drift_report import display_path, normalize_event, render_report, skill_defaults


def load_candidate_events(
    input_jsonl: Path,
    defaults: dict[str, str],
    default_source: str,
    default_command: str,
) -> tuple[list[dict[str, str]], list[str]]:
    events: list[dict[str, str]] = []
    failures: list[str] = []
    for index, line in enumerate(input_jsonl.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            raw = json.loads(line)
        except json.JSONDecodeError as exc:
            failures.append(f"line {index}: invalid JSONL event: {exc.msg}")
            continue
        if not isinstance(raw, dict):
            failures.append(f"line {index}: telemetry event must be a JSON object")
            continue
        raw.setdefault("source", default_source)
        raw.setdefault("command", default_command)
        event, event_failures = normalize_event(raw, defaults, f"line {index}")
        failures.extend(event_failures)
        if event:
            events.append(event)
    return events, failures


def append_events(events_jsonl: Path, events: list[dict[str, str]]) -> None:
    events_jsonl.parent.mkdir(parents=True, exist_ok=True)
    with events_jsonl.open("a", encoding="utf-8") as handle:
        for event in events:
            handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")


def import_events(
    skill_dir: Path,
    input_jsonl: Path,
    events_jsonl: Path | None = None,
    output_json: Path | None = None,
    output_md: Path | None = None,
    generated_at: str | None = None,
    default_source: str = "external",
    default_command: str = "external-client",
    dry_run: bool = False,
) -> dict[str, Any]:
    skill_dir = skill_dir.resolve()
    input_jsonl = input_jsonl.resolve()
    reports_dir = skill_dir / "reports"
    events_jsonl = (events_jsonl or reports_dir / "telemetry_events.jsonl").resolve()
    output_json = (output_json or reports_dir / "adoption_drift_report.json").resolve()
    output_md = (output_md or reports_dir / "adoption_drift_report.md").resolve()
    failures: list[str] = []
    if not input_jsonl.exists():
        failures.append(f"Input telemetry JSONL does not exist: {display_path(input_jsonl)}")
        candidate_events: list[dict[str, str]] = []
    else:
        candidate_events, load_failures = load_candidate_events(
            input_jsonl,
            skill_defaults(skill_dir),
            default_source,
            default_command,
        )
        failures.extend(load_failures)

    adoption_report: dict[str, Any] | None = None
    if not failures and not dry_run:
        append_events(events_jsonl, candidate_events)
        adoption_report = render_report(
            skill_dir,
            events_jsonl=events_jsonl,
            output_json=output_json,
            output_md=output_md,
            generated_at=generated_at,
        )

    return {
        "ok": not failures,
        "schema_version": "1.0",
        "skill_dir": display_path(skill_dir),
        "input_jsonl": display_path(input_jsonl),
        "events_jsonl": display_path(events_jsonl),
        "dry_run": dry_run,
        "imported_count": 0 if failures or dry_run else len(candidate_events),
        "candidate_count": len(candidate_events),
        "failures": failures,
        "imported_preview": candidate_events[:5],
        "artifacts": {
            "events_jsonl": display_path(events_jsonl),
            "adoption_drift_json": display_path(output_json),
            "adoption_drift_md": display_path(output_md),
        },
        "adoption_drift": {
            "summary": adoption_report.get("summary", {}) if adoption_report else {},
            "artifacts": adoption_report.get("artifacts", {}) if adoption_report else {},
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Import external metadata-only telemetry into a local skill event stream.")
    parser.add_argument("skill_dir", nargs="?", default=".")
    parser.add_argument("--input-jsonl", required=True)
    parser.add_argument("--events-jsonl")
    parser.add_argument("--output-json")
    parser.add_argument("--output-md")
    parser.add_argument("--generated-at")
    parser.add_argument("--source", choices=["external", "manual", "unknown", "yao_cli"], default="external")
    parser.add_argument("--command", default="external-client")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    report = import_events(
        Path(args.skill_dir),
        Path(args.input_jsonl),
        events_jsonl=Path(args.events_jsonl) if args.events_jsonl else None,
        output_json=Path(args.output_json) if args.output_json else None,
        output_md=Path(args.output_md) if args.output_md else None,
        generated_at=args.generated_at,
        default_source=args.source,
        default_command=args.command,
        dry_run=args.dry_run,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not report["ok"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
