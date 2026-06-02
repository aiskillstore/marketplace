#!/usr/bin/env python3
"""Turn a private bad rewrite into a redacted, audited fixture candidate."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from case_lab import add_tuple_field, add_value_field, tuple_literal
from failure_taxonomy import unique_failure_buckets, unique_failure_codes
from ledger import merge_ledgers, parse_fences, parse_ledger_files, split_terms, strip_fences
from redact_case import parse_replacements, redact_text, remaining_sensitive
from regression_100 import Case, numeric_claims, validate


def read_value(value: str | None, file_path: str | None, label: str) -> tuple[str, bool]:
    if value and file_path:
        raise SystemExit(f"Pass either --{label} or --{label}-file, not both.")
    if file_path:
        return Path(file_path).read_text(encoding="utf-8").strip(), False
    if value is not None:
        return value.strip(), True
    if label == "source" and not sys.stdin.isatty():
        return sys.stdin.read().strip(), True
    raise SystemExit(f"Missing --{label} or --{label}-file.")


def clean_terms(values: list[str]) -> tuple[str, ...]:
    return tuple(value.strip() for value in values if value.strip())


def redact_field(value: str, replacements: list[tuple[str, str]], mode: str) -> tuple[str, list[dict[str, str | int]], list[str]]:
    if mode == "off":
        return value, [], remaining_sensitive(value)
    redacted, records = redact_text(value, replacements)
    return redacted, records, remaining_sensitive(redacted)


def make_case(
    *,
    case_id: str,
    source: str,
    rewrite: str,
    must: tuple[str, ...],
    protected: tuple[str, ...],
    voice: tuple[str, ...],
    forbid: tuple[str, ...],
    required_claims: tuple[str, ...],
    forbid_assertions: tuple[str, ...],
    preserve_uncertainty: bool,
    no_dash: bool,
    max_words: int | None,
) -> Case:
    protected_terms = list(protected)
    protected_terms.extend(sorted(numeric_claims(source)))
    return Case(
        id=case_id,
        source=source,
        rewrite=rewrite,
        must=must,
        protected=clean_terms(protected_terms),
        preserve_voice=voice,
        forbid=forbid,
        required_claims=required_claims,
        forbid_assertions=forbid_assertions,
        preserve_uncertainty=preserve_uncertainty,
        no_dash=no_dash,
        max_words=max_words,
        forbid_wrappers=True,
        forbid_clarifying=True,
    )


def audit(case: Case) -> dict[str, Any]:
    errors = validate(case)
    return {
        "status": "PASS" if not errors else "FAIL",
        "failure_codes": unique_failure_codes(errors),
        "failure_buckets": unique_failure_buckets(errors),
        "errors": errors,
    }


def case_block(case: Case) -> str:
    lines = [
        "# Review before committing: keep fixtures redacted and focused.",
        "Case(",
        f"    id={case.id!r},",
        f"    source={case.source!r},",
        f"    rewrite={case.rewrite!r},",
        f"    must={tuple_literal(case.must)},",
    ]
    add_tuple_field(lines, "protected", case.protected)
    add_tuple_field(lines, "preserve_voice", case.preserve_voice)
    add_tuple_field(lines, "forbid", case.forbid)
    add_tuple_field(lines, "required_claims", case.required_claims)
    add_tuple_field(lines, "forbid_assertions", case.forbid_assertions)
    add_value_field(lines, "preserve_uncertainty", case.preserve_uncertainty)
    add_value_field(lines, "no_dash", case.no_dash)
    add_value_field(lines, "max_words", case.max_words)
    add_value_field(lines, "forbid_wrappers", case.forbid_wrappers)
    add_value_field(lines, "forbid_clarifying", case.forbid_clarifying)
    lines.append(")")
    return "\n".join(lines)


def print_markdown(result: dict[str, Any]) -> None:
    print("# Failure Fixture Candidate")
    print()
    print(f"Status: {result['status']}")
    print(f"Redactions applied: {result['redaction']['total']}")
    if result["redaction"]["remaining_sensitive_types"]:
        print("Remaining sensitive patterns: " + ", ".join(result["redaction"]["remaining_sensitive_types"]))
    for warning in result["warnings"]:
        print(f"Warning: {warning}")
    print()
    print("## Failed Rewrite Audit")
    print(f"- Status: {result['failed_audit']['status']}")
    print(f"- Codes: {', '.join(result['failed_audit']['failure_codes']) or 'none'}")
    print()
    print("## Desired Rewrite Audit")
    print(f"- Status: {result['desired_audit']['status']}")
    print(f"- Codes: {', '.join(result['desired_audit']['failure_codes']) or 'none'}")
    print()
    print("## Case")
    print()
    print("```python")
    print(result["case"])
    print("```")
    print()
    print("## Manual Review")
    print("- Confirm no private names, customers, secrets, URLs, local paths, or private facts remain.")
    print("- Confirm the redaction still preserves the failure shape.")
    print("- Confirm the desired rewrite passes for the right reason, not because the fixture became too generic.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case-id", required=True)
    parser.add_argument("--source")
    parser.add_argument("--source-file")
    parser.add_argument("--failed-rewrite")
    parser.add_argument("--failed-rewrite-file")
    parser.add_argument("--desired-rewrite")
    parser.add_argument("--desired-rewrite-file")
    parser.add_argument("--ledger-file", action="append", default=[])
    parser.add_argument("--redact", choices=("strict", "auto", "off"), default="strict")
    parser.add_argument("--redact-term", "--replace", action="append", default=[], help="Explicit redaction as old=new.")
    parser.add_argument("--confirm-public-safe", action="store_true", help="Required when --redact off.")
    parser.add_argument("--allow-inline-private", action="store_true")
    parser.add_argument("--must", action="append", default=[])
    parser.add_argument("--protected", action="append", default=[])
    parser.add_argument("--voice", action="append", default=[])
    parser.add_argument("--forbid", action="append", default=[])
    parser.add_argument("--required-claim", action="append", default=[])
    parser.add_argument("--forbid-assertion", action="append", default=[])
    parser.add_argument("--preserve-uncertainty", action="store_true")
    parser.add_argument("--no-dash", action="store_true")
    parser.add_argument("--max-words", type=int)
    parser.add_argument("--case-only", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.redact == "off" and not args.confirm_public_safe:
        raise SystemExit("--redact off requires --confirm-public-safe")

    replacements = parse_replacements(args.redact_term)
    source, source_inline = read_value(args.source, args.source_file, "source")
    failed, failed_inline = read_value(args.failed_rewrite, args.failed_rewrite_file, "failed-rewrite")
    desired, desired_inline = read_value(args.desired_rewrite, args.desired_rewrite_file, "desired-rewrite")
    inline_used = source_inline or failed_inline or desired_inline
    warnings: list[str] = []
    if inline_used and not args.allow_inline_private:
        warnings.append("inline text can leak through shell history; prefer --*-file for private drafts")

    ledger = merge_ledgers(parse_fences(source), parse_ledger_files(args.ledger_file))
    source = strip_fences(source)
    raw_fields = {
        "source": source,
        "failed": failed,
        "desired": desired,
        "must": "\n".join(args.must),
        "protected": "\n".join(ledger["protected"] + split_terms(args.protected)),
        "voice": "\n".join(ledger["voice"] + split_terms(args.voice)),
        "forbid": "\n".join(ledger["forbid"] + split_terms(args.forbid)),
        "required_claims": "\n".join(ledger["required_claims"] + split_terms(args.required_claim)),
        "forbid_assertions": "\n".join(ledger["forbid_assertions"] + split_terms(args.forbid_assertion)),
    }
    redacted: dict[str, str] = {}
    redactions: dict[str, list[dict[str, str | int]]] = {}
    remaining: dict[str, list[str]] = {}
    for key, value in raw_fields.items():
        redacted_value, records, remaining_types = redact_field(value, replacements, args.redact)
        redacted[key] = redacted_value
        redactions[key] = records
        remaining[key] = remaining_types

    redacted_terms = {
        key: clean_terms(redacted[key].splitlines())
        for key in ("must", "protected", "voice", "forbid", "required_claims", "forbid_assertions")
    }
    failed_case = make_case(
        case_id=args.case_id + "_failed",
        source=redacted["source"],
        rewrite=redacted["failed"],
        must=redacted_terms["must"],
        protected=redacted_terms["protected"],
        voice=redacted_terms["voice"],
        forbid=redacted_terms["forbid"],
        required_claims=redacted_terms["required_claims"],
        forbid_assertions=redacted_terms["forbid_assertions"],
        preserve_uncertainty=args.preserve_uncertainty,
        no_dash=args.no_dash,
        max_words=args.max_words,
    )
    desired_case = make_case(
        case_id=args.case_id,
        source=redacted["source"],
        rewrite=redacted["desired"],
        must=redacted_terms["must"],
        protected=redacted_terms["protected"],
        voice=redacted_terms["voice"],
        forbid=redacted_terms["forbid"],
        required_claims=redacted_terms["required_claims"],
        forbid_assertions=redacted_terms["forbid_assertions"],
        preserve_uncertainty=args.preserve_uncertainty,
        no_dash=args.no_dash,
        max_words=args.max_words,
    )
    failed_audit = audit(failed_case)
    desired_audit = audit(desired_case)
    total_redactions = sum(int(record["count"]) for records in redactions.values() for record in records)
    remaining_types = sorted({item for items in remaining.values() for item in items})
    status = "READY"
    if desired_audit["status"] != "PASS":
        status = "BLOCKED"
    elif remaining_types and args.redact == "strict":
        status = "BLOCKED"
    elif remaining_types:
        status = "NEEDS_REVIEW"
    elif failed_audit["status"] != "FAIL" or warnings:
        status = "NEEDS_REVIEW"

    result = {
        "case_id": args.case_id,
        "status": status,
        "redaction": {
            "mode": args.redact,
            "total": total_redactions,
            "remaining_sensitive_types": remaining_types,
            "counts": redactions,
        },
        "warnings": warnings,
        "failed_audit": failed_audit,
        "desired_audit": desired_audit,
        "case": case_block(desired_case),
    }

    if args.case_only:
        print(result["case"])
    elif args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print_markdown(result)
    return 1 if status == "BLOCKED" else 0


if __name__ == "__main__":
    raise SystemExit(main())
