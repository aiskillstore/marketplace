#!/usr/bin/env python3
"""Stable failure codes and buckets for Dittobot validators."""

from __future__ import annotations


RULES = (
    ("lost_voice_marker", "voice_loss", ("lost voice markers",)),
    ("missing_required_term", "fact_loss", ("missing required terms",)),
    ("lost_protected_fact", "fact_loss", ("lost protected facts",)),
    ("lost_exact_substring", "fact_loss", ("lost exact substrings",)),
    ("missing_required_claim", "claim_drift", ("missing required claims",)),
    ("forbidden_assertion", "claim_drift", ("forbidden assertions appeared",)),
    ("invented_detail", "unsupported_invention", ("invented-detail markers",)),
    ("invented_number", "unsupported_invention", ("invented numeric claims",)),
    ("lost_uncertainty", "uncertainty_drift", ("lost uncertainty marker",)),
    ("modality_drift", "uncertainty_drift", ("modality drift markers",)),
    ("causality_drift", "causality_drift", ("causality drift markers",)),
    ("generic_ai_marker", "generic_ai_tell", ("generic markers appeared",)),
    ("unexpected_note", "wrapper_or_note", ("unexpected note",)),
    ("unexpected_wrapper", "wrapper_or_note", ("unexpected rewrite wrapper",)),
    ("unexpected_markdown_fence", "wrapper_or_note", ("markdown fence",)),
    ("clarifying_question", "clarifying_question", ("unexpected clarifying question",)),
    ("line_prefix_drift", "format_drift", ("lost required line prefixes",)),
    ("ordered_terms_drift", "format_drift", (
        "ordered terms out of order",
        "missing ordered terms",
    )),
    ("unexpected_bullets", "format_drift", ("unexpected bullet list",)),
    ("paragraph_count_drift", "format_drift", ("paragraph count failed",)),
    ("opening_drift", "format_drift", ("opening failed",)),
    ("ending_drift", "format_drift", ("ending failed",)),
    ("artifact_leak", "format_drift", ("note artifacts appeared",)),
    ("diagnosis_drift", "format_drift", ("diagnosis case produced rewrite heading",)),
    ("dash_violation", "constraint_violation", ("dash constraint violated",)),
    ("question_count_violation", "constraint_violation", ("question mark count failed",)),
    ("exact_word_count_violation", "constraint_violation", ("exact word count failed",)),
    ("max_word_count_violation", "constraint_violation", ("max word count failed",)),
    ("too_long", "constraint_violation", ("too long",)),
    ("api_error", "api_error", ("API error", "HTTP ")),
)

BUCKET_RULES = (
    ("voice_loss", ("lost voice markers",)),
    ("fact_loss", ("missing required terms", "lost protected facts", "lost exact substrings")),
    ("claim_drift", ("missing required claims", "forbidden assertions appeared")),
    ("unsupported_invention", ("invented-detail markers", "invented numeric claims")),
    ("uncertainty_drift", ("lost uncertainty marker", "modality drift markers")),
    ("causality_drift", ("causality drift markers",)),
    ("generic_ai_tell", ("generic markers appeared",)),
    ("wrapper_or_note", ("unexpected note", "unexpected rewrite wrapper", "markdown fence")),
    ("clarifying_question", ("unexpected clarifying question",)),
    ("format_drift", (
        "lost required line prefixes",
        "ordered terms out of order",
        "missing ordered terms",
        "unexpected bullet list",
        "paragraph count failed",
        "opening failed",
        "ending failed",
        "note artifacts appeared",
        "diagnosis case produced rewrite heading",
    )),
    ("constraint_violation", (
        "dash constraint violated",
        "question mark count failed",
        "exact word count failed",
        "max word count failed",
        "too long",
    )),
    ("api_error", ("API error", "HTTP ")),
)


def failure_code(error: str) -> str:
    normalized = error.lower()
    for code, _bucket, needles in RULES:
        if any(needle.lower() in normalized for needle in needles):
            return code
    return "other"


def failure_bucket(error: str) -> str:
    normalized = error.lower()
    for label, needles in BUCKET_RULES:
        if any(needle.lower() in normalized for needle in needles):
            return label
    return "other"


def unique_failure_codes(errors: list[str]) -> list[str]:
    codes: list[str] = []
    for error in errors:
        code = failure_code(error)
        if code not in codes:
            codes.append(code)
    return codes


def unique_failure_buckets(errors: list[str]) -> list[str]:
    buckets: list[str] = []
    for error in errors:
        bucket = failure_bucket(error)
        if bucket not in buckets:
            buckets.append(bucket)
    return buckets


def failure_classes(errors: list[str]) -> list[str]:
    """Backward-compatible alias for previous report field name."""
    return unique_failure_buckets(errors)
