#!/usr/bin/env python3
"""Generate a regression Case skeleton from a redacted rewrite failure."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ledger import merge_ledgers, parse_fences, parse_ledger_files, split_terms, strip_fences


PROMPT_MODES = ("explicit_rewrite", "source_only")


def read_value(value: str | None, file_path: str | None, label: str) -> str:
    if value and file_path:
        raise SystemExit(f"Pass either --{label} or --{label}-file, not both.")
    if file_path:
        return Path(file_path).read_text(encoding="utf-8").strip()
    if value is not None:
        return value.strip()
    raise SystemExit(f"Missing --{label} or --{label}-file.")


def clean_terms(values: list[str]) -> tuple[str, ...]:
    return tuple(value.strip() for value in values if value.strip())


def tuple_literal(values: tuple[str, ...]) -> str:
    if not values:
        return "()"
    if len(values) == 1:
        return f"({values[0]!r},)"
    return "(" + ", ".join(repr(value) for value in values) + ")"


def add_tuple_field(lines: list[str], name: str, values: tuple[str, ...]) -> None:
    if values:
        lines.append(f"    {name}={tuple_literal(values)},")


def add_value_field(lines: list[str], name: str, value) -> None:
    if value is not None and value is not False:
        lines.append(f"    {name}={value!r},")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case-id", required=True, help="New deterministic case id.")
    parser.add_argument("--source", help="Redacted source text.")
    parser.add_argument("--source-file", help="File containing redacted source text.")
    parser.add_argument("--rewrite", help="Desired passing rewrite.")
    parser.add_argument("--rewrite-file", help="File containing desired passing rewrite.")
    parser.add_argument("--must", action="append", default=[], help="Required term or idea.")
    parser.add_argument("--protected", action="append", default=[], help="Fact or phrase to protect.")
    parser.add_argument("--voice", action="append", default=[], help="Voice marker to preserve.")
    parser.add_argument("--forbid", action="append", default=[], help="Forbidden term or phrase.")
    parser.add_argument(
        "--ledger-file",
        action="append",
        default=[],
        help="Local .json or fence-marked .md file with protected/voice/forbid/claim terms.",
    )
    parser.add_argument("--exact-substring", action="append", default=[], help="Exact substring to preserve.")
    parser.add_argument("--line-prefix", action="append", default=[], help="Required output line prefix.")
    parser.add_argument("--ordered-term", action="append", default=[], help="Terms that must appear in order.")
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
    parser.add_argument("--exact-words", type=int)
    parser.add_argument("--max-words", type=int)
    parser.add_argument("--max-ratio", type=float)
    parser.add_argument("--max-question-marks", type=int)
    parser.add_argument("--max-paragraphs", type=int)
    parser.add_argument("--starts-with")
    parser.add_argument("--ends-with")
    parser.add_argument("--no-dash", action="store_true")
    parser.add_argument("--allow-note", action="store_true")
    parser.add_argument("--allow-expand", action="store_true")
    parser.add_argument("--forbid-wrapper", action="store_true")
    parser.add_argument("--forbid-clarifying", action="store_true")
    parser.add_argument("--forbid-bullets", action="store_true")
    parser.add_argument("--preserve-uncertainty", action="store_true")
    parser.add_argument("--prompt-mode", choices=PROMPT_MODES, default="explicit_rewrite")
    args = parser.parse_args()

    source = read_value(args.source, args.source_file, "source")
    ledger = merge_ledgers(parse_fences(source), parse_ledger_files(args.ledger_file))
    source = strip_fences(source)
    rewrite = read_value(args.rewrite, args.rewrite_file, "rewrite")
    must = clean_terms(args.must)

    lines = [
        "# Review before committing: keep fixtures redacted and focused.",
        "Case(",
        f"    id={args.case_id!r},",
        f"    source={source!r},",
        f"    rewrite={rewrite!r},",
        f"    must={tuple_literal(must)},",
    ]
    add_tuple_field(lines, "protected", clean_terms(ledger["protected"] + split_terms(args.protected)))
    add_tuple_field(lines, "preserve_voice", clean_terms(ledger["voice"] + split_terms(args.voice)))
    add_tuple_field(lines, "forbid", clean_terms(ledger["forbid"] + split_terms(args.forbid)))
    add_tuple_field(
        lines,
        "required_claims",
        clean_terms(ledger["required_claims"] + split_terms(args.required_claim)),
    )
    add_tuple_field(
        lines,
        "forbid_assertions",
        clean_terms(ledger["forbid_assertions"] + split_terms(args.forbid_assertion)),
    )
    add_tuple_field(lines, "exact_substrings", clean_terms(args.exact_substring))
    add_tuple_field(lines, "line_prefixes", clean_terms(args.line_prefix))
    add_tuple_field(lines, "ordered_terms", clean_terms(args.ordered_term))
    add_tuple_field(lines, "forbid_artifacts", clean_terms(args.forbid_artifact))
    add_value_field(lines, "exact_words", args.exact_words)
    add_value_field(lines, "max_words", args.max_words)
    add_value_field(lines, "max_ratio", args.max_ratio)
    add_value_field(lines, "max_question_marks", args.max_question_marks)
    add_value_field(lines, "max_paragraphs", args.max_paragraphs)
    add_value_field(lines, "starts_with", args.starts_with)
    add_value_field(lines, "ends_with", args.ends_with)
    add_value_field(lines, "no_dash", args.no_dash)
    add_value_field(lines, "allow_note", args.allow_note)
    add_value_field(lines, "allow_expand", args.allow_expand)
    add_value_field(lines, "forbid_wrappers", args.forbid_wrapper)
    add_value_field(lines, "forbid_clarifying", args.forbid_clarifying)
    add_value_field(lines, "forbid_bullets", args.forbid_bullets)
    add_value_field(lines, "preserve_uncertainty", args.preserve_uncertainty)
    if args.prompt_mode != "explicit_rewrite":
        add_value_field(lines, "prompt_mode", args.prompt_mode)
    lines.append(")")
    sys.stdout.write("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
