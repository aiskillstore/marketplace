#!/usr/bin/env python3
"""Compile, validate, and render compact Dittobot voice profile contracts."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from regression_100 import GENERIC_MARKERS, contains_term, words
from voice_probe import read_samples, summarize


SCHEMA_VERSION = 1
SECTION_KEYS = (
    "use",
    "avoid",
    "rhythm_diction",
    "protected_quirks",
    "evidence_phrases",
    "when_not_to_apply",
    "editing_rules",
)
SECTION_LABELS = {
    "use": "Use",
    "avoid": "Avoid",
    "rhythm_diction": "Rhythm/Diction",
    "protected_quirks": "Protected quirks",
    "evidence_phrases": "Evidence phrases",
    "when_not_to_apply": "When not to apply",
    "editing_rules": "Editing rules",
}
SENSITIVE_BOUNDARY_TERMS = (
    "legal",
    "medical",
    "financial",
    "academic",
    "hr",
    "crisis",
    "customer-facing",
    "precision-sensitive",
)
SUSPECT_FACT_RE = re.compile(
    r"https?://|[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}|\b\d{2,}\b|"
    r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\b|"
    r"\b(?:Inc|LLC|Corp|Corporation|Ltd|contract|clause|deadline|invoice|revenue)\b",
    re.IGNORECASE,
)
RECIPE_RE = re.compile(r"\b(always|copy|reuse|repeat|say exactly|use exactly)\b", re.IGNORECASE)


def phrase_rows(summary: dict[str, Any], limit: int) -> list[str]:
    phrases: list[str] = []
    for key in ("trigrams", "bigrams"):
        for row in summary["candidate_phrases"][key]:
            phrase = row["phrase"]
            if phrase not in phrases:
                phrases.append(phrase)
            if len(phrases) >= limit:
                return phrases
    return phrases


def rhythm_line(summary: dict[str, Any]) -> str:
    buckets = summary["sentence_length_buckets"]
    avg = summary["avg_sentence_words"]
    dominant = max(buckets, key=buckets.get)
    if dominant == "short_1_8":
        base = "Mostly short sentences with a quick, plainspoken cadence."
    elif dominant == "long_21_plus":
        base = "Comfortable with longer sentences when the thought needs room."
    else:
        base = "Mostly medium sentences with room for short punch lines."
    punctuation = summary["punctuation"]
    extras: list[str] = []
    if punctuation["question_mark"]:
        extras.append("questions are part of the rhythm")
    if punctuation["dash"]:
        extras.append("dashes appear in the source, but should not become a reflex")
    if summary["contractions"]["count"]:
        extras.append("contractions are natural here")
    suffix = " " + "; ".join(extras) + "." if extras else ""
    return f"{base} Average sentence length: {avg} words.{suffix}"


def profile_sections(summary: dict[str, Any], max_evidence_phrases: int) -> dict[str, list[str]]:
    evidence = phrase_rows(summary, max_evidence_phrases)
    return {
        "use": [
            "Plain words, source-backed specificity, and the writer's actual emotional temperature.",
            "Light edits when the draft already has a pulse; stronger rewrites only when structure blocks the point.",
        ],
        "avoid": [
            "Corporate fog, tidy triples, forced cheer, fake casualness, and generic AI polish.",
            "Importing old facts, names, claims, dates, or opinions from the samples into new drafts.",
        ],
        "rhythm_diction": [rhythm_line(summary)],
        "protected_quirks": [
            "Keep odd phrasing, dry contrast, bluntness, or asymmetry when it carries the point.",
            "Treat repeated phrases as evidence of taste, not slogans to paste into every rewrite.",
        ],
        "evidence_phrases": evidence or ["No repeated evidence phrases detected."],
        "when_not_to_apply": [
            "Legal, medical, financial, HR, crisis, customer-facing, or precision-sensitive text where facts and risk beat style.",
            "Any draft whose current audience, constraints, or emotional stance conflicts with the profile.",
        ],
        "editing_rules": [
            "Preserve current draft facts and explicit constraints before applying profile habits.",
            "If the profile would make the draft more certain, formal, cheerful, or complete than the source supports, ignore the profile.",
        ],
    }


def card_word_count(contract: dict[str, Any]) -> int:
    text = "\n".join(
        line for key in SECTION_KEYS for line in contract.get(key, [])
    )
    return len(words(text))


def compile_contract(args: argparse.Namespace) -> dict[str, Any]:
    summary = summarize(read_samples(args.files, args.sample), args.phrase_limit)
    sections = profile_sections(summary, args.max_evidence_phrases)
    contract: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "profile_id": args.profile_id,
        "profile_type": "voice_taste",
        "token_budget": {
            "max_card_words": args.max_card_words,
            "max_evidence_phrases": args.max_evidence_phrases,
        },
        **sections,
        "forbidden_imports": [
            "old facts",
            "old names",
            "old dates",
            "old claims",
            "old opinions",
        ],
        "probe": summary,
        "warnings": [],
    }
    warnings, errors = validate_contract(contract, strict=False)
    contract["warnings"] = warnings + errors
    return contract


def validate_contract(contract: dict[str, Any], strict: bool) -> tuple[list[str], list[str]]:
    warnings: list[str] = []
    errors: list[str] = []
    if contract.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    if contract.get("profile_type") != "voice_taste":
        errors.append("profile_type must be voice_taste")
    for key in SECTION_KEYS:
        value = contract.get(key)
        if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
            errors.append(f"{key} must be a non-empty array of strings")
    budget = contract.get("token_budget", {})
    max_card_words = int(budget.get("max_card_words", 220)) if isinstance(budget, dict) else 220
    max_evidence = int(budget.get("max_evidence_phrases", 5)) if isinstance(budget, dict) else 5
    if card_word_count(contract) > max_card_words:
        errors.append(f"profile card exceeds {max_card_words} words")
    evidence = contract.get("evidence_phrases", [])
    if isinstance(evidence, list):
        if len(evidence) > max_evidence:
            errors.append(f"too many evidence phrases: {len(evidence)} > {max_evidence}")
        for phrase in evidence:
            if len(words(str(phrase))) > 8:
                errors.append(f"evidence phrase is too long: {phrase}")
            if SUSPECT_FACT_RE.search(str(phrase)):
                warnings.append(f"possible private fact in evidence phrase: {phrase}")
    joined = "\n".join(
        line for key in SECTION_KEYS for line in contract.get(key, []) if isinstance(line, str)
    )
    if not any(term in joined.lower() for term in SENSITIVE_BOUNDARY_TERMS):
        errors.append("profile needs a sensitive/precision boundary")
    if RECIPE_RE.search(joined):
        warnings.append("profile may treat evidence phrases as a recipe; keep phrases as evidence only")
    generic = [marker for marker in GENERIC_MARKERS if contains_term(joined, marker)]
    if generic:
        warnings.append(f"profile contains generic AI markers: {generic}")
    if strict:
        errors.extend(warnings)
        warnings = []
    return warnings, errors


def render_card(contract: dict[str, Any], *, prompt: bool = False) -> str:
    lines: list[str] = []
    if prompt:
        lines.extend(
            [
                "Use this as editing taste only. Current draft facts, constraints, audience, and risk beat this profile.",
                "",
            ]
        )
    for key in SECTION_KEYS:
        lines.append(f"## {SECTION_LABELS[key]}")
        for item in contract.get(key, []):
            text = str(item)
            if key == "evidence_phrases" and text and not text.startswith('"') and text != "No repeated evidence phrases detected.":
                text = f'"{text}"'
            lines.append(f"- {text}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_contract(path: str | None, payload: str) -> None:
    if path:
        Path(path).write_text(payload, encoding="utf-8")
    else:
        sys.stdout.write(payload)


def load_contract(path: str) -> dict[str, Any]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise SystemExit(f"{path}: expected a JSON object")
    return raw


def command_compile(args: argparse.Namespace) -> int:
    contract = compile_contract(args)
    if args.out:
        Path(args.out).write_text(json.dumps(contract, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.card_out:
        Path(args.card_out).write_text(render_card(contract), encoding="utf-8")
    if args.json:
        print(json.dumps(contract, indent=2, ensure_ascii=False))
    elif not args.out and not args.card_out:
        sys.stdout.write(render_card(contract))
    return 0


def command_validate(args: argparse.Namespace) -> int:
    contract = load_contract(args.profile)
    warnings, errors = validate_contract(contract, args.strict)
    result = {
        "status": "PASS" if not errors else "FAIL",
        "warnings": warnings,
        "errors": errors,
        "card_words": card_word_count(contract),
    }
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"Status: {result['status']}")
        print(f"Card words: {result['card_words']}")
        for warning in warnings:
            print(f"WARNING: {warning}")
        for error in errors:
            print(f"ERROR: {error}")
    return 1 if errors else 0


def command_render(args: argparse.Namespace) -> int:
    contract = load_contract(args.profile)
    if args.format == "json":
        print(json.dumps(contract, indent=2, ensure_ascii=False))
    else:
        sys.stdout.write(render_card(contract, prompt=args.format == "prompt-md"))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    compile_parser = sub.add_parser("compile", help="Compile samples into a profile contract.")
    compile_parser.add_argument("files", nargs="*", help="Sample files to inspect.")
    compile_parser.add_argument("--sample", action="append", default=[], help="Inline writing sample.")
    compile_parser.add_argument("--profile-id", default="dittobot-profile")
    compile_parser.add_argument("--phrase-limit", type=int, default=8)
    compile_parser.add_argument("--max-card-words", type=int, default=220)
    compile_parser.add_argument("--max-evidence-phrases", type=int, default=5)
    compile_parser.add_argument("--out", help="Write JSON contract to this path.")
    compile_parser.add_argument("--card-out", help="Write Markdown card to this path.")
    compile_parser.add_argument("--json", action="store_true", help="Print JSON contract.")
    compile_parser.set_defaults(func=command_compile)

    validate_parser = sub.add_parser("validate", help="Validate a profile contract.")
    validate_parser.add_argument("profile", help="Profile contract JSON file.")
    validate_parser.add_argument("--strict", action="store_true", help="Treat warnings as errors.")
    validate_parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    validate_parser.set_defaults(func=command_validate)

    render_parser = sub.add_parser("render", help="Render a profile contract.")
    render_parser.add_argument("profile", help="Profile contract JSON file.")
    render_parser.add_argument("--format", choices=("card-md", "prompt-md", "json"), default="card-md")
    render_parser.set_defaults(func=command_render)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if getattr(args, "phrase_limit", 0) < 0:
        raise SystemExit("--phrase-limit cannot be negative.")
    if getattr(args, "max_evidence_phrases", 0) < 0:
        raise SystemExit("--max-evidence-phrases cannot be negative.")
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
