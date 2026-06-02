#!/usr/bin/env python3
"""Audit an arbitrary Dittobot rewrite without calling an LLM."""

from __future__ import annotations

import argparse
import dataclasses
import json
import sys
from pathlib import Path

from failure_taxonomy import unique_failure_buckets, unique_failure_codes
from ledger import merge_ledgers, parse_fences, parse_ledger_files, split_terms, strip_fences
from regression_100 import Case, numeric_claims, validate, words


def read_value(value: str | None, file_path: str | None, label: str) -> str:
    if value and file_path:
        raise SystemExit(f"Pass either --{label} or --{label}-file, not both.")
    if file_path:
        return Path(file_path).read_text(encoding="utf-8")
    if value is not None:
        return value
    if label == "source" and not sys.stdin.isatty():
        return sys.stdin.read()
    raise SystemExit(f"Missing --{label} or --{label}-file.")


def clean_terms(values: list[str]) -> tuple[str, ...]:
    return tuple(value.strip() for value in values if value.strip())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", help="Original source text. If omitted, stdin is used.")
    parser.add_argument("--source-file", help="File containing original source text.")
    parser.add_argument("--rewrite", help="Rewritten text to audit.")
    parser.add_argument("--rewrite-file", help="File containing rewritten text.")
    parser.add_argument("--must", action="append", default=[], help="Required term or idea.")
    parser.add_argument("--protected", action="append", default=[], help="Fact or phrase that must survive.")
    parser.add_argument("--voice", action="append", default=[], help="Voice marker that must survive.")
    parser.add_argument("--forbid", action="append", default=[], help="Forbidden term or phrase.")
    parser.add_argument(
        "--ledger-file",
        action="append",
        default=[],
        help="Local .json or fence-marked .md file with protected/voice/forbid/claim terms.",
    )
    parser.add_argument("--exact-substring", action="append", default=[], help="Exact substring that must survive.")
    parser.add_argument("--line-prefix", action="append", default=[], help="Required output line prefix.")
    parser.add_argument("--ordered-term", action="append", default=[], help="Terms that must appear in this order.")
    parser.add_argument("--forbid-artifact", action="append", default=[], help="Artifact text that must not appear.")
    parser.add_argument(
        "--required-claim",
        action="append",
        default=[],
        help="Claim that must remain present.",
    )
    parser.add_argument(
        "--forbid-assertion",
        action="append",
        default=[],
        help="Assertion that must not appear.",
    )
    parser.add_argument(
        "--no-protect-source-numbers",
        action="store_true",
        help="Do not automatically protect numeric claims from the source.",
    )
    parser.add_argument("--exact-words", type=int, help="Require this exact output word count.")
    parser.add_argument("--max-words", type=int, help="Require output at or below this word count.")
    parser.add_argument("--max-ratio", type=float, default=1.35, help="Max rewrite/source word ratio.")
    parser.add_argument("--max-question-marks", type=int, help="Maximum question marks allowed.")
    parser.add_argument("--exact-paragraphs", type=int, help="Require this exact paragraph count.")
    parser.add_argument("--max-paragraphs", type=int, help="Maximum paragraph count.")
    parser.add_argument("--starts-with", help="Required output opening.")
    parser.add_argument("--ends-with", help="Required output ending.")
    parser.add_argument("--no-dash", action="store_true", help="Disallow dash characters.")
    parser.add_argument("--allow-note", action="store_true", help="Allow notes or rationale.")
    parser.add_argument("--allow-wrapper", action="store_true", help="Allow rewrite labels/wrappers.")
    parser.add_argument(
        "--allow-clarifying",
        action="store_true",
        help="Allow clarifying questions in the output.",
    )
    parser.add_argument("--allow-expand", action="store_true", help="Disable ratio-based concision check.")
    parser.add_argument(
        "--preserve-uncertainty",
        action="store_true",
        help="Require uncertainty language to survive.",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    args = parser.parse_args()

    source = read_value(args.source, args.source_file, "source").strip()
    ledger = merge_ledgers(parse_fences(source), parse_ledger_files(args.ledger_file))
    source = strip_fences(source)
    rewrite = read_value(args.rewrite, args.rewrite_file, "rewrite").strip()
    protected = ledger["protected"] + split_terms(args.protected)
    if not args.no_protect_source_numbers:
        protected.extend(sorted(numeric_claims(source)))

    case = Case(
        id="ad_hoc_audit",
        source=source,
        rewrite=rewrite,
        must=clean_terms(args.must),
        protected=clean_terms(protected),
        preserve_voice=clean_terms(ledger["voice"] + split_terms(args.voice)),
        forbid=clean_terms(ledger["forbid"] + split_terms(args.forbid)),
        required_claims=clean_terms(ledger["required_claims"] + split_terms(args.required_claim)),
        forbid_assertions=clean_terms(
            ledger["forbid_assertions"] + split_terms(args.forbid_assertion)
        ),
        exact_substrings=clean_terms(args.exact_substring),
        line_prefixes=clean_terms(args.line_prefix),
        ordered_terms=clean_terms(args.ordered_term),
        forbid_artifacts=clean_terms(args.forbid_artifact),
        exact_words=args.exact_words,
        max_words=args.max_words,
        max_ratio=args.max_ratio,
        max_question_marks=args.max_question_marks,
        exact_paragraphs=args.exact_paragraphs,
        max_paragraphs=args.max_paragraphs,
        starts_with=args.starts_with,
        ends_with=args.ends_with,
        no_dash=args.no_dash,
        allow_note=args.allow_note,
        forbid_wrappers=not args.allow_wrapper,
        forbid_clarifying=not args.allow_clarifying,
        allow_expand=args.allow_expand,
        preserve_uncertainty=args.preserve_uncertainty,
    )
    errors = validate(case)
    result = {
        "status": "PASS" if not errors else "FAIL",
        "source_words": len(words(source)),
        "rewrite_words": len(words(rewrite)),
        "protected": dataclasses.asdict(case)["protected"],
        "failure_codes": unique_failure_codes(errors),
        "failure_buckets": unique_failure_buckets(errors),
        "errors": errors,
    }

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif errors:
        print(f"FAIL | source_words={result['source_words']} rewrite_words={result['rewrite_words']}")
        if result["failure_codes"]:
            print(f"  codes: {', '.join(result['failure_codes'])}")
        if result["failure_buckets"]:
            print(f"  buckets: {', '.join(result['failure_buckets'])}")
        for error in errors:
            print(f"  - {error}")
    else:
        print(f"PASS | source_words={result['source_words']} rewrite_words={result['rewrite_words']}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
