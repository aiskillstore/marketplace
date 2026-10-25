#!/usr/bin/env python3
"""Read-only Persian/English prose diagnostics. No network or third-party code."""

import argparse
from collections import defaultdict
import json
import re
import statistics
import sys

# Running the diagnostics must not create a sibling __pycache__ directory.
sys.dont_write_bytecode = True

from text_common import (WORD, finding, human_report, language, mask_spans,
                         protected_spans, read_utf8, report_order)


# Small, transparent prompts for contextual review, never a banned-word list.
TELLS = [
    ("en", r"\bit(?:'|’)s important to note that\b|\bit is important to note that\b", "Check whether this framing adds a needed qualification; otherwise state the point directly."),
    ("en", r"\bin today(?:'|’)s (?:rapidly (?:evolving|changing) |ever-changing |digital )?(?:world|landscape|age)\b", "Check whether the time-and-world framing supplies relevant context or only a generic opening."),
    ("en", r"\bdelve(?:s|d)? into\b", "Check whether this stock transition fits the speaker and subject; a direct verb may be clearer."),
    ("en", r"\ba testament to\b", "Check whether this evaluative claim is supported by the surrounding evidence."),
    ("fa", r"(?:لازم به ذکر است|لازم است (?:ذکر|گفته) شود)(?: که)?", "بررسی کنید آیا این مقدمه قید ضروری دارد یا می‌توان نکته را مستقیم بیان کرد."),
    ("fa", r"در دنیای (?:پرشتاب |پرتلاطم |امروز)", "بررسی کنید آیا این زمینه‌سازی به موضوع اطلاعات مشخصی اضافه می‌کند."),
    ("fa", r"در عصر (?:دیجیتال|حاضر|کنونی)", "بررسی کنید آیا اشاره به عصر برای استدلال لازم و مشخص است."),
    ("fa", r"نقش (?:بسزا|بی‌بدیل|بی بدیل|حیاتی) (?:ایفا می[‌ ]کند|دارد)", "این ارزیابی کلی را با شواهد و نقش مشخص آن در متن تطبیق دهید."),
]


def sentences(text):
    result = []
    start = 0
    for match in re.finditer(r"[.!?؟]+(?=\s|$)|\n[ \t]*\n", text):
        chunk = text[start:match.end()]
        words = list(WORD.finditer(chunk))
        if words:
            first = start + words[0].start()
            result.append((first, text[first:match.end()].strip(), len(words)))
        start = match.end()
    chunk = text[start:]
    words = list(WORD.finditer(chunk))
    if words:
        first = start + words[0].start()
        result.append((first, text[first:].strip(), len(words)))
    return result


def audit(text, lang="auto", profile="general"):
    protected = protected_spans(text, quotes=True)
    prose = mask_spans(text, protected)
    detected = language(prose)
    effective = detected if lang == "auto" else lang
    findings = []
    for tell_lang, pattern, message in TELLS:
        if effective not in (tell_lang, "mixed", "undetermined"):
            continue
        for match in re.finditer(pattern, prose, re.I):
            findings.append(finding(text, match.start(), "LEXICAL_REVIEW", message))
    if effective in ("fa", "mixed", "undetermined"):
        for match in re.finditer("[يك]", prose):
            findings.append(finding(text, match.start(), "FA_ARABIC_LETTER",
                                    "Review Arabic ي/ك in Persian prose; retain it if this is intentional Arabic text or a proper form."))
        # Narrow constructions only; not a Persian morphological checker.
        for match in re.finditer(r"(?<![\w‌])(?:ن?می) (?:شود|شوند|شدم|شدیم|رود|روند|کند|کنند|کنم|کنیم|دانم|دانیم|تواند|توانند|توانیم)(?![\w‌])", prose):
            findings.append(finding(text, match.start(), "FA_PREFIX_SPACING",
                                    "Review the space after می/نمی; standard Persian usually joins this prefix with a ZWNJ."))

    sentence_items = sentences(prose)
    by_sentence = defaultdict(list)
    for offset, sentence, _ in sentence_items:
        normalized = re.sub(r"\s+", " ", sentence).strip().casefold()
        by_sentence[normalized].append(offset)
    for offsets in by_sentence.values():
        if len(offsets) > 1:
            for offset in offsets[1:]:
                findings.append(finding(text, offset, "REPEATED_SENTENCE",
                                        "This sentence repeats an earlier sentence at line {}. Check whether the repetition is intentional.".format(finding(text, offsets[0], "", "")["line"])))
    paragraphs = []
    for match in re.finditer(r"\S(?:.*?\S)?(?=\n[ \t]*\n|\Z)", prose, re.S):
        words = list(WORD.finditer(match.group()))
        if words:
            paragraphs.append((match.start() + words[0].start(), [word.group().casefold() for word in words]))
    starts = defaultdict(list)
    for offset, words in paragraphs:
        if len(words) >= 3:
            starts[tuple(words[:3])].append(offset)
    for offsets in starts.values():
        if len(offsets) > 1:
            for offset in offsets[1:]:
                findings.append(finding(text, offset, "REPEATED_PARAGRAPH_START",
                                        "The first three words match a paragraph at line {}. Review rhythm or intentional parallel structure.".format(finding(text, offsets[0], "", "")["line"])))

    lengths = [item[2] for item in sentence_items]
    metrics = {
        "characters": len(text), "prose_characters": sum(not ch.isspace() for ch in prose),
        "words": len(WORD.findall(prose)), "sentences": len(sentence_items),
        "paragraphs": len(paragraphs), "protected_spans": len(protected),
        "sentence_words": {
            "min": min(lengths) if lengths else 0, "max": max(lengths) if lengths else 0,
            "mean": round(statistics.mean(lengths), 3) if lengths else 0,
            "median": statistics.median(lengths) if lengths else 0,
            "population_stdev": round(statistics.pstdev(lengths), 3) if lengths else 0,
        },
    }
    return {"schema_version": 1, "tool": "audit_text", "lang": effective,
            "detected_lang": detected, "profile": profile, "metrics": metrics,
            "scope": "Heuristic review only; no authorship determination, meaning-equivalence test or factual verification.",
            "findings": sorted(findings, key=report_order)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", help="UTF-8 text path, or - for stdin")
    parser.add_argument("--lang", choices=("auto", "fa", "en", "mixed"), default="auto")
    parser.add_argument("--profile", choices=("general", "academic", "web", "copy"), default="general",
                        help="review context recorded in output; no genre is penalized by a word blacklist")
    parser.add_argument("--json", action="store_true", help="machine-readable JSON instead of human text")
    parser.add_argument("--strict", action="store_true", help="exit 1 if any advisory findings occur")
    args = parser.parse_args(argv)
    try:
        report = audit(read_utf8(args.path), args.lang, args.profile)
    except (OSError, UnicodeError, ValueError) as error:
        parser.error(str(error))
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        human_report(report)
    return 1 if args.strict and report["findings"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
