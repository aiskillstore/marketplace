#!/usr/bin/env python3
"""Explain deterministic rewrite risks without calling an LLM."""

from __future__ import annotations

import argparse
import dataclasses
import json
import sys
from pathlib import Path

from failure_taxonomy import unique_failure_buckets, unique_failure_codes
from ledger import merge_ledgers, parse_fences, parse_ledger_files, split_terms, strip_fences
from regression_100 import (
    Case,
    GENERIC_MARKERS,
    INVENTED_DETAIL_MARKERS,
    contains_term,
    count_markers,
    numeric_claims,
    validate,
    words,
)


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


def term_status(text: str, terms: list[str]) -> list[dict[str, str | bool]]:
    return [
        {
            "term": term,
            "kept": contains_term(text, term),
        }
        for term in terms
    ]


def print_section(title: str, rows: list[dict[str, str | bool]]) -> None:
    print(title)
    if not rows:
        print("- none")
        return
    for row in rows:
        mark = "kept" if row["kept"] else "missing"
        print(f"- {row['term']}: {mark}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", help="Original source text. If omitted, stdin is used.")
    parser.add_argument("--source-file", help="File containing original source text.")
    parser.add_argument("--rewrite", help="Rewritten text to report on.")
    parser.add_argument("--rewrite-file", help="File containing rewritten text.")
    parser.add_argument("--protected", action="append", default=[], help="Fact or phrase that must survive.")
    parser.add_argument("--voice", action="append", default=[], help="Voice marker that should survive.")
    parser.add_argument("--forbid", action="append", default=[], help="Forbidden term or phrase.")
    parser.add_argument(
        "--ledger-file",
        action="append",
        default=[],
        help="Local .json or fence-marked .md file with protected/voice/forbid/claim terms.",
    )
    parser.add_argument(
        "--no-protect-source-numbers",
        action="store_true",
        help="Do not automatically track numeric claims from the source.",
    )
    parser.add_argument("--exact-words", type=int, help="Require this exact output word count.")
    parser.add_argument("--max-words", type=int, help="Require output at or below this word count.")
    parser.add_argument("--max-ratio", type=float, default=1.35, help="Max rewrite/source word ratio.")
    parser.add_argument("--no-dash", action="store_true", help="Disallow dash characters.")
    parser.add_argument(
        "--preserve-uncertainty",
        action="store_true",
        help="Require uncertainty language to survive.",
    )
    parser.add_argument("--allow-note", action="store_true", help="Allow notes or rationale.")
    parser.add_argument("--allow-wrapper", action="store_true", help="Allow rewrite labels/wrappers.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    args = parser.parse_args()

    source = read_value(args.source, args.source_file, "source").strip()
    ledger = merge_ledgers(parse_fences(source), parse_ledger_files(args.ledger_file))
    source = strip_fences(source)
    rewrite = read_value(args.rewrite, args.rewrite_file, "rewrite").strip()

    source_numbers = sorted(numeric_claims(source))
    rewrite_numbers = sorted(numeric_claims(rewrite))
    protected = ledger["protected"] + split_terms(args.protected)
    if not args.no_protect_source_numbers:
        protected.extend(source_numbers)

    case = Case(
        id="rewrite_report",
        source=source,
        rewrite=rewrite,
        must=(),
        protected=clean_terms(protected),
        preserve_voice=clean_terms(ledger["voice"] + split_terms(args.voice)),
        forbid=clean_terms(ledger["forbid"] + split_terms(args.forbid)),
        required_claims=clean_terms(ledger["required_claims"]),
        forbid_assertions=clean_terms(ledger["forbid_assertions"]),
        exact_words=args.exact_words,
        max_words=args.max_words,
        max_ratio=args.max_ratio,
        no_dash=args.no_dash,
        allow_note=args.allow_note,
        forbid_wrappers=not args.allow_wrapper,
        preserve_uncertainty=args.preserve_uncertainty,
    )
    errors = validate(case)
    source_word_count = len(words(source))
    rewrite_word_count = len(words(rewrite))
    ratio = rewrite_word_count / source_word_count if source_word_count else 0
    generic_markers = count_markers(rewrite, GENERIC_MARKERS)
    invented_detail_markers = count_markers(rewrite, INVENTED_DETAIL_MARKERS)
    added_numbers = sorted(set(rewrite_numbers) - set(source_numbers))
    result = {
        "status": "PASS" if not errors else "FAIL",
        "source_words": source_word_count,
        "rewrite_words": rewrite_word_count,
        "ratio": round(ratio, 3),
        "protected": term_status(rewrite, list(dataclasses.asdict(case)["protected"])),
        "voice": term_status(rewrite, list(dataclasses.asdict(case)["preserve_voice"])),
        "source_numbers": source_numbers,
        "rewrite_numbers": rewrite_numbers,
        "added_numbers": added_numbers,
        "generic_markers": generic_markers,
        "invented_detail_markers": invented_detail_markers,
        "failure_codes": unique_failure_codes(errors),
        "failure_buckets": unique_failure_buckets(errors),
        "errors": errors,
    }

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("# Rewrite Report")
        print(f"Status: {result['status']}")
        print(f"Words: {source_word_count} -> {rewrite_word_count} ({ratio:.2f}x)")
        if result["failure_codes"]:
            print(f"Failure codes: {', '.join(result['failure_codes'])}")
        if result["failure_buckets"]:
            print(f"Failure buckets: {', '.join(result['failure_buckets'])}")
        print_section("Protected facts", result["protected"])
        print_section("Voice markers", result["voice"])
        print("Added numeric claims")
        print("- " + ", ".join(added_numbers) if added_numbers else "- none")
        print("Generic AI markers")
        print("- " + ", ".join(generic_markers) if generic_markers else "- none")
        print("Invented-detail markers")
        print("- " + ", ".join(invented_detail_markers) if invented_detail_markers else "- none")
        if errors:
            print("Audit notes")
            for error in errors:
                print(f"- {error}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
