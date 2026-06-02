#!/usr/bin/env python3
"""Extract local, observable voice signals from writing samples."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


STOPWORDS = {
    "a",
    "about",
    "and",
    "are",
    "as",
    "at",
    "be",
    "but",
    "by",
    "for",
    "from",
    "had",
    "has",
    "have",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "this",
    "to",
    "was",
    "we",
    "with",
    "you",
}


def read_samples(paths: list[str], inline: list[str]) -> list[str]:
    samples = [text.strip() for text in inline if text.strip()]
    for raw_path in paths:
        path = Path(raw_path)
        if not path.exists():
            raise SystemExit(f"Sample not found: {path}")
        samples.append(path.read_text(encoding="utf-8").strip())
    if not samples and not sys.stdin.isatty():
        text = sys.stdin.read().strip()
        if text:
            samples.append(text)
    if not samples:
        raise SystemExit("Provide --sample, sample files, or stdin.")
    return samples


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9']+", text)


def sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [part.strip() for part in parts if words(part)]


def bucket_sentence_lengths(lengths: list[int]) -> dict[str, int]:
    return {
        "short_1_8": sum(1 for length in lengths if length <= 8),
        "medium_9_20": sum(1 for length in lengths if 9 <= length <= 20),
        "long_21_plus": sum(1 for length in lengths if length >= 21),
    }


def punctuation_counts(text: str) -> dict[str, int]:
    return {
        "comma": text.count(","),
        "colon": text.count(":"),
        "semicolon": text.count(";"),
        "question_mark": text.count("?"),
        "exclamation": text.count("!"),
        "ellipsis": text.count("..."),
        "dash": len(re.findall(r"--|[-\u2013\u2014]", text)),
        "parentheses": text.count("(") + text.count(")"),
    }


def ngram_candidates(all_words: list[str], n: int, limit: int) -> list[dict[str, Any]]:
    counts = Counter()
    for index in range(len(all_words) - n + 1):
        gram = all_words[index:index + n]
        if all(word in STOPWORDS for word in gram):
            continue
        if gram[0] in STOPWORDS and gram[-1] in STOPWORDS:
            continue
        counts[" ".join(gram)] += 1
    return [
        {"phrase": phrase, "count": count}
        for phrase, count in counts.most_common(limit)
        if count > 1
    ]


def contractions(text: str) -> list[str]:
    return re.findall(r"\b[A-Za-z]+'[A-Za-z]+\b", text)


def summarize(samples: list[str], phrase_limit: int) -> dict[str, Any]:
    joined = "\n\n".join(samples)
    sample_words = [words(sample) for sample in samples]
    flat_words = [word.lower() for sample in sample_words for word in sample]
    sample_sentences = [sentence for sample in samples for sentence in sentences(sample)]
    sentence_lengths = [len(words(sentence)) for sentence in sample_sentences]
    contraction_list = contractions(joined)
    first_person = sum(1 for word in flat_words if word in {"i", "i'm", "me", "my", "we", "our", "us"})

    return {
        "samples": len(samples),
        "words": len(flat_words),
        "sentences": len(sample_sentences),
        "avg_sentence_words": round(
            sum(sentence_lengths) / len(sentence_lengths), 2
        ) if sentence_lengths else 0,
        "sentence_length_buckets": bucket_sentence_lengths(sentence_lengths),
        "punctuation": punctuation_counts(joined),
        "contractions": {
            "count": len(contraction_list),
            "examples": sorted(set(contraction_list))[:10],
        },
        "first_person_words": first_person,
        "candidate_phrases": {
            "bigrams": ngram_candidates(flat_words, 2, phrase_limit),
            "trigrams": ngram_candidates(flat_words, 3, phrase_limit),
        },
    }


def write_markdown(summary: dict[str, Any]) -> None:
    print("# Voice Probe")
    print()
    print(f"- Samples: {summary['samples']}")
    print(f"- Words: {summary['words']}")
    print(f"- Sentences: {summary['sentences']}")
    print(f"- Average sentence length: {summary['avg_sentence_words']} words")
    print(f"- First-person words: {summary['first_person_words']}")
    print()
    print("## Sentence Lengths")
    for label, count in summary["sentence_length_buckets"].items():
        print(f"- {label}: {count}")
    print()
    print("## Punctuation")
    for label, count in summary["punctuation"].items():
        print(f"- {label}: {count}")
    print()
    print("## Contractions")
    examples = ", ".join(summary["contractions"]["examples"]) or "none"
    print(f"- Count: {summary['contractions']['count']}")
    print(f"- Examples: {examples}")
    print()
    print("## Candidate Evidence Phrases")
    for label in ("bigrams", "trigrams"):
        print(f"- {label}:")
        rows = summary["candidate_phrases"][label]
        if not rows:
            print("  - none repeated")
            continue
        for row in rows:
            print(f"  - {row['phrase']} ({row['count']})")
    print()
    print("Use these as evidence, not a recipe. A voice profile still needs judgment.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="*", help="Sample files to inspect.")
    parser.add_argument("--sample", action="append", default=[], help="Inline writing sample.")
    parser.add_argument("--phrase-limit", type=int, default=8)
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    args = parser.parse_args()

    if args.phrase_limit < 0:
        raise SystemExit("--phrase-limit cannot be negative.")

    summary = summarize(read_samples(args.files, args.sample), args.phrase_limit)
    if args.json:
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    else:
        write_markdown(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
