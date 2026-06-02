#!/usr/bin/env python3
"""Summarize local Dittobot live-eval JSONL transcripts."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from failure_taxonomy import failure_bucket, failure_code, unique_failure_buckets, unique_failure_codes


def derived_family(case_id: str) -> str:
    return re.sub(r"_\d+$", "", case_id)


def error_kind(error: str) -> str:
    return error.split(":", 1)[0].strip()


def usage_value(usage: dict[str, Any], key: str) -> int:
    value = usage.get(key)
    return value if isinstance(value, int) else 0


def read_records(paths: list[str]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for raw_path in paths:
        path = Path(raw_path)
        if not path.exists():
            raise SystemExit(f"Transcript not found: {path}")
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise SystemExit(f"{path}:{line_number}: invalid JSON: {exc}") from exc
            if not isinstance(record, dict):
                raise SystemExit(f"{path}:{line_number}: expected object record")
            records.append(record)
    return records


def filtered_records(
    records: list[dict[str, Any]],
    model: str | None,
    prompt_mode: str | None,
    skill_sha256: str | None,
) -> list[dict[str, Any]]:
    if model:
        records = [record for record in records if record.get("model") == model]
    if prompt_mode:
        records = [record for record in records if record.get("prompt_mode") == prompt_mode]
    if skill_sha256:
        records = [
            record for record in records
            if str(record.get("skill_sha256", "")).startswith(skill_sha256)
        ]
    return records


def pass_rate(passed: int, total: int) -> float:
    return passed / total if total else 0.0


def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    by_model: dict[str, Counter[str]] = defaultdict(Counter)
    by_prompt_mode: dict[str, Counter[str]] = defaultdict(Counter)
    by_family: dict[str, Counter[str]] = defaultdict(Counter)
    failures = Counter()
    failure_codes = Counter()
    failure_buckets = Counter()
    failed_cases: list[dict[str, Any]] = []
    skill_hashes = Counter()
    input_tokens = 0
    output_tokens = 0
    total_tokens = 0
    passed = 0

    for record in records:
        errors = record.get("errors")
        if not isinstance(errors, list):
            errors = []
        status = "passed" if not errors else "failed"
        if status == "passed":
            passed += 1

        case_id = str(record.get("case", "unknown"))
        case_family = str(record.get("family") or derived_family(case_id))
        model = str(record.get("model", "unknown"))
        prompt_mode = str(record.get("prompt_mode", "unknown"))
        by_model[model][status] += 1
        by_prompt_mode[prompt_mode][status] += 1
        by_family[case_family][status] += 1
        codes = (
            record.get("failure_codes")
            if isinstance(record.get("failure_codes"), list)
            else unique_failure_codes([str(error) for error in errors])
        )
        buckets = (
            record.get("failure_buckets")
            if isinstance(record.get("failure_buckets"), list)
            else unique_failure_buckets([str(error) for error in errors])
        )
        if errors:
            failed_cases.append(
                {
                    "case": case_id,
                    "family": case_family,
                    "model": model,
                    "prompt_mode": prompt_mode,
                    "failure_codes": codes,
                    "failure_buckets": buckets,
                    "errors": [str(error) for error in errors],
                }
            )
        for error in errors:
            text = str(error)
            failures[error_kind(text)] += 1
            failure_codes[failure_code(text)] += 1
            failure_buckets[failure_bucket(text)] += 1

        skill_sha256 = str(record.get("skill_sha256", ""))
        if skill_sha256:
            skill_hashes[skill_sha256[:12]] += 1

        usage = record.get("usage")
        if isinstance(usage, dict):
            usage_input = usage_value(usage, "input_tokens")
            usage_output = usage_value(usage, "output_tokens")
            usage_total = usage_value(usage, "total_tokens") or usage_input + usage_output
            input_tokens += usage_input
            output_tokens += usage_output
            total_tokens += usage_total

    return {
        "records": len(records),
        "passed": passed,
        "failed": len(records) - passed,
        "pass_rate": pass_rate(passed, len(records)),
        "usage": {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
        },
        "skill_hashes": dict(skill_hashes),
        "by_model": {key: dict(value) for key, value in sorted(by_model.items())},
        "by_prompt_mode": {key: dict(value) for key, value in sorted(by_prompt_mode.items())},
        "by_family": {key: dict(value) for key, value in sorted(by_family.items())},
        "failure_types": dict(failures.most_common()),
        "failure_codes": dict(failure_codes.most_common()),
        "failure_buckets": dict(failure_buckets.most_common()),
        "failed_cases": failed_cases,
    }


def write_counter_section(title: str, rows: dict[str, dict[str, int]]) -> None:
    print(title)
    if not rows:
        print("  none")
        return
    for name, counts in rows.items():
        passed = counts.get("passed", 0)
        failed = counts.get("failed", 0)
        total = passed + failed
        print(f"  {name}: {passed}/{total} passed ({pass_rate(passed, total):.1%})")


def write_text_report(summary: dict[str, Any], top_failures: int) -> None:
    total = int(summary["records"])
    passed = int(summary["passed"])
    failed = int(summary["failed"])
    usage = summary["usage"]

    print("LIVE EVAL REPORT")
    print(f"records: {total}")
    print(f"passed: {passed}/{total} ({summary['pass_rate']:.1%})")
    print(f"failed: {failed}")
    if usage["total_tokens"]:
        print(
            "usage: "
            f"input={usage['input_tokens']} output={usage['output_tokens']} "
            f"total={usage['total_tokens']}"
        )
    if summary["skill_hashes"]:
        hashes = ", ".join(
            f"{key} ({value})" for key, value in summary["skill_hashes"].items()
        )
        print(f"skill hashes: {hashes}")
    print()
    write_counter_section("by model:", summary["by_model"])
    print()
    write_counter_section("by prompt mode:", summary["by_prompt_mode"])
    print()
    write_counter_section("by case family:", summary["by_family"])
    print()
    print("failure types:")
    if summary["failure_types"]:
        for name, count in summary["failure_types"].items():
            print(f"  {name}: {count}")
    else:
        print("  none")
    print()
    print("failure codes:")
    if summary["failure_codes"]:
        for name, count in summary["failure_codes"].items():
            print(f"  {name}: {count}")
    else:
        print("  none")
    print()
    print("failure buckets:")
    if summary["failure_buckets"]:
        for name, count in summary["failure_buckets"].items():
            print(f"  {name}: {count}")
    else:
        print("  none")
    print()
    print("top failed cases:")
    for record in summary["failed_cases"][:top_failures]:
        codes = ", ".join(record["failure_codes"]) or "none"
        print(
            f"  {record['case']} [{record['model']} / {record['prompt_mode']}]: "
            f"{codes}"
        )
    if not summary["failed_cases"]:
        print("  none")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("transcripts", nargs="+", help="One or more *.local.jsonl transcript files.")
    parser.add_argument("--model", help="Only include this model.")
    parser.add_argument("--prompt-mode", help="Only include this prompt mode.")
    parser.add_argument("--skill-sha256", help="Only include skill hashes with this prefix.")
    parser.add_argument("--top-failures", type=int, default=10, help="Failed cases to show.")
    parser.add_argument(
        "--fail-under",
        type=float,
        help="Exit nonzero if pass rate is below this decimal threshold, e.g. 0.95.",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    args = parser.parse_args()

    if args.fail_under is not None and not 0 <= args.fail_under <= 1:
        raise SystemExit("--fail-under must be between 0 and 1.")
    if args.top_failures < 0:
        raise SystemExit("--top-failures cannot be negative.")

    records = filtered_records(
        read_records(args.transcripts),
        model=args.model,
        prompt_mode=args.prompt_mode,
        skill_sha256=args.skill_sha256,
    )
    if not records:
        raise SystemExit("No transcript records matched.")

    summary = summarize(records)
    if args.json:
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    else:
        write_text_report(summary, args.top_failures)

    if args.fail_under is not None and summary["pass_rate"] < args.fail_under:
        print(
            f"Pass rate {summary['pass_rate']:.1%} is below threshold {args.fail_under:.1%}.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
