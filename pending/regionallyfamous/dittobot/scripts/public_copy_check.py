#!/usr/bin/env python3
"""Check Dittobot's public-facing copy for voice and structure regressions."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"

REQUIRED_SECTIONS = (
    "## The Point",
    "## The AI Hater Case, Answered",
    "## Watch It Work",
    "## What Dittobot Is",
    "## Proof, Not Vibes",
    "## The Useful Boring Stuff",
)

REQUIRED_PHRASES = (
    "teach the tool your voice",
    "teach it taste",
    "not a ghostwriter",
    "voice-preserving editor",
    "The better move, the more hopeful move",
    "Use $skill-installer to install Dittobot",
    "A risograph-style Dittobot workshop",
)

ALWAYS_BANNED = (
    "committee paste",
    "committee pasted",
    "non-developer path",
    "non-developers",
    "nondevelopers",
    "paste committee",
    "thesaurus committee",
)

STIFF_PHRASES = (
    "at scale",
    "best-in-class",
    "cutting-edge",
    "drive meaningful impact",
    "empowers teams",
    "game-changing",
    "in today's fast-paced world",
    "in today's rapidly evolving landscape",
    "leverage ai",
    "robust platform",
    "seamless collaboration",
    "synergy",
    "unlock seamless",
    "world-class",
)

ALLOWED_CRITIQUE_MARKERS = (
    "accepting",
    "ai hater",
    "bad ai",
    "banned",
    "critique",
    "example",
    "generic",
    "hate",
    "slop",
    "source:",
    "trapped",
    "webinar",
)

OVER_INSTRUCTED_USE_PROMPTS = (
    "use $dittobot to tighten this email but keep my voice",
    "use $dittobot to make this less ai-sounding",
    "do not add facts, do not make it more formal",
    "preserve the weird phrasing where it works",
    "clean this legal-ish note",
)


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def prose_lines(markdown: str) -> list[tuple[int, str]]:
    lines: list[tuple[int, str]] = []
    in_fence = False
    for index, line in enumerate(markdown.splitlines(), start=1):
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            lines.append((index, line))
    return lines


def prose_text(markdown: str) -> str:
    return "\n".join(line for _, line in prose_lines(markdown))


def fail(message: str, errors: list[str]) -> None:
    errors.append(message)


def check_required_content(markdown: str, errors: list[str]) -> None:
    for section in REQUIRED_SECTIONS:
        if section not in markdown:
            fail(f"README is missing required public section: {section}", errors)
    normalized = normalize(markdown)
    for phrase in REQUIRED_PHRASES:
        if normalize(phrase) not in normalized:
            fail(f"README is missing required voice/thesis phrase: {phrase}", errors)


def check_heading_order(markdown: str, errors: list[str]) -> None:
    headings = [
        "# Dittobot",
        "## The Point",
        "## The AI Hater Case, Answered",
        "## Watch It Work",
        "## What Dittobot Is",
        "## Use It",
        "## Proof, Not Vibes",
    ]
    positions: list[tuple[str, int]] = []
    for heading in headings:
        position = markdown.find(heading)
        if position == -1:
            fail(f"README is missing required heading: {heading}", errors)
        else:
            positions.append((heading, position))
    for (left_heading, left_position), (right_heading, right_position) in zip(positions, positions[1:]):
        if left_position >= right_position:
            fail(f"README heading order is wrong: {left_heading} should come before {right_heading}", errors)


def check_process_examples(markdown: str, errors: list[str]) -> None:
    watch_start = markdown.find("## Watch It Work")
    next_section = markdown.find("\n## ", watch_start + 1) if watch_start != -1 else -1
    watch_section = markdown[watch_start:next_section if next_section != -1 else None]
    notice_count = watch_section.count("Dittobot notices:")
    source_count = watch_section.count("Source:")
    rewrite_count = watch_section.count("Rewrite:")
    if notice_count < 4:
        fail(f"README must show at least 4 in-process examples; found {notice_count}", errors)
    if not (source_count == notice_count == rewrite_count):
        fail(
            "README process examples must have matching Source, Dittobot notices, and Rewrite blocks; "
            f"found Source={source_count}, notices={notice_count}, Rewrite={rewrite_count}",
            errors,
        )

    blocks = watch_section.split("Dittobot notices:")[1:]
    for index, block in enumerate(blocks, start=1):
        before_rewrite = block.split("Rewrite:", 1)[0]
        bullet_count = sum(1 for line in before_rewrite.splitlines() if line.startswith("- "))
        if "Rewrite:" not in block:
            fail(f"in-process example {index} is missing a Rewrite block", errors)
        if bullet_count < 2:
            fail(f"in-process example {index} must include at least 2 Dittobot notices", errors)


def check_banned_phrases(markdown: str, errors: list[str]) -> None:
    text = normalize(markdown)
    for phrase in ALWAYS_BANNED:
        if phrase in text:
            fail(f"public copy contains awkward banned phrase: {phrase!r}", errors)

    for line_number, line in prose_lines(markdown):
        normalized_line = normalize(line)
        if not normalized_line:
            continue
        for phrase in STIFF_PHRASES:
            if phrase not in normalized_line:
                continue
            if any(marker in normalized_line for marker in ALLOWED_CRITIQUE_MARKERS):
                continue
            fail(f"stiff phrase outside critique/example context on line {line_number}: {phrase!r}", errors)


def check_use_section(markdown: str, errors: list[str]) -> None:
    normalized = normalize(markdown)
    for prompt in OVER_INSTRUCTED_USE_PROMPTS:
        if prompt in normalized:
            fail(f"README Use section reintroduced over-instructed prompt: {prompt!r}", errors)
    if "Use $dittobot on this:" not in markdown:
        fail("README must show the default drop-in usage prompt", errors)
    skill_installer_position = markdown.find("Use $skill-installer")
    curl_position = markdown.find("curl -fsSL")
    if skill_installer_position == -1:
        fail("README must lead with the streamlined $skill-installer path", errors)
    elif curl_position != -1 and curl_position < skill_installer_position:
        fail("README should show $skill-installer before the terminal fallback", errors)


def check_description(description: str | None, errors: list[str]) -> None:
    if description is None:
        return
    normalized = normalize(description)
    if len(description) > 110:
        fail("repo description should stay short and conversational", errors)
    for phrase in ALWAYS_BANNED + STIFF_PHRASES:
        if phrase in normalized:
            fail(f"repo description contains weak public-copy phrase: {phrase!r}", errors)
    if "sound like you" not in normalized:
        fail("repo description should keep the voice-preservation promise explicit", errors)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--readme", default=str(README), help="README path to check.")
    parser.add_argument("--description", help="Optional GitHub repo description to check.")
    args = parser.parse_args()

    errors: list[str] = []
    readme = Path(args.readme)
    if not readme.exists():
        fail(f"README not found: {readme}", errors)
    else:
        markdown = readme.read_text(encoding="utf-8")
        check_required_content(markdown, errors)
        check_heading_order(markdown, errors)
        check_process_examples(markdown, errors)
        check_banned_phrases(markdown, errors)
        check_use_section(markdown, errors)
    check_description(args.description, errors)

    if errors:
        print("Public copy check failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("Public copy check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
