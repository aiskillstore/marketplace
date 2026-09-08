#!/usr/bin/env python3
"""Strict source-only changelog metadata parsing for Skill Forge releases."""

from __future__ import annotations

import datetime as dt
import re
from dataclasses import dataclass
from typing import Optional


SEMVER_TAG_PATTERN = r"v(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)"
SEMVER_TAG_RE = re.compile(rf"^{SEMVER_TAG_PATTERN}$")
RELEASE_CANDIDATE_RE = re.compile(
    rf"^## \[(?P<tag>{SEMVER_TAG_PATTERN})\](?P<suffix>.*)$"
)
EXACT_RELEASE_HEADING_RE = re.compile(
    rf"^## \[(?P<tag>{SEMVER_TAG_PATTERN})\] - (?P<date>[0-9]{{4}}-[0-9]{{2}}-[0-9]{{2}})$"
)
UNRELEASED_CANDIDATE_RE = re.compile(r"^## \[Unreleased\](?P<suffix>.*)$")
EXACT_UNRELEASED_HEADING = "## [Unreleased]"
FENCE_OPEN_RE = re.compile(r"^[ ]{0,3}(?P<fence>`{3,}|~{3,})")
RAW_HTML_TAG_RE = re.compile(
    r"^[ ]{0,3}<(?P<tag>pre|script|style|textarea)(?:[ \t>]|$)",
    re.IGNORECASE,
)
GENERIC_HTML_BLOCK_RE = re.compile(
    r"^[ ]{0,3}</?[A-Za-z][A-Za-z0-9-]*(?:[ \t/>]|$)"
)
BLOCK_HTML_TAG_RE = re.compile(
    r"^[ ]{0,3}</?(?:address|article|aside|base|basefont|blockquote|body|caption|center|"
    r"col|colgroup|dd|details|dialog|dir|div|dl|dt|fieldset|figcaption|figure|footer|"
    r"form|frame|frameset|h[1-6]|head|header|hr|html|iframe|legend|li|link|main|menu|"
    r"menuitem|nav|noframes|ol|optgroup|option|p|param|search|section|summary|table|"
    r"tbody|td|tfoot|th|thead|title|tr|track|ul)(?:[ \t/>]|$)",
    re.IGNORECASE,
)


class ChangelogMetadataError(RuntimeError):
    """A strict changelog metadata failure with a stable error code."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class ReleaseEntry:
    tag: str
    date: str
    body: str


@dataclass(frozen=True)
class UnreleasedEntry:
    heading_start: int
    heading_end: int
    body: str
    body_end: int


@dataclass(frozen=True)
class HeadingCandidate:
    start: int
    end: int
    line: str
    tag: Optional[str]


def _advance_html_comment_state(line: str, in_comment: bool) -> bool:
    """Track block comments well enough to exclude hidden heading lines."""

    position = 0
    while position < len(line):
        if in_comment:
            end = line.find("-->", position)
            if end < 0:
                return True
            in_comment = False
            position = end + 3
        else:
            start = line.find("<!--", position)
            if start < 0:
                return False
            in_comment = True
            position = start + 4
    return in_comment


def _visible_heading_candidates(
    text: str,
) -> tuple[list[HeadingCandidate], list[HeadingCandidate]]:
    """Return release/Unreleased headings outside comments and code fences."""

    releases: list[HeadingCandidate] = []
    unreleased: list[HeadingCandidate] = []
    in_comment = False
    fence_character: Optional[str] = None
    fence_length = 0
    raw_html_end: Optional[str] = None
    raw_html_until_blank = False
    offset = 0
    # CommonMark line endings are LF and CRLF. ``str.splitlines`` would also
    # treat Unicode separators as line breaks and could invent a hidden H2.
    line_segments = text.split("\n")
    for index, segment in enumerate(line_segments):
        raw_line = segment + ("\n" if index < len(line_segments) - 1 else "")
        line = segment[:-1] if segment.endswith("\r") else segment
        line_end = offset + len(line)
        if raw_html_end is not None:
            if raw_html_end.lower() in line.lower():
                raw_html_end = None
            offset += len(raw_line)
            continue
        if raw_html_until_blank:
            # CommonMark blank lines contain only ASCII spaces or tabs.
            # ``str.strip`` would also consume NBSP, VT, FF, NEL, and other
            # Unicode whitespace, ending the raw HTML block too early.
            if re.fullmatch(r"[ \t]*", line) is not None:
                raw_html_until_blank = False
            offset += len(raw_line)
            continue
        if fence_character is not None:
            closing = re.fullmatch(
                rf"[ ]{{0,3}}{re.escape(fence_character)}{{{fence_length},}}[ \t]*",
                line,
            )
            if closing is not None:
                fence_character = None
                fence_length = 0
            offset += len(raw_line)
            continue

        if not in_comment:
            stripped = line.lstrip(" ") if len(line) - len(line.lstrip(" ")) <= 3 else line
            lowered = stripped.lower()
            raw_tag = RAW_HTML_TAG_RE.match(line)
            if raw_tag is not None:
                closing = f"</{raw_tag.group('tag')}>"
                if closing.lower() not in lowered:
                    raw_html_end = closing
                offset += len(raw_line)
                continue
            if stripped.startswith("<![CDATA["):
                if "]]>" not in stripped[len("<![CDATA["):]:
                    raw_html_end = "]]>"
                offset += len(raw_line)
                continue
            if stripped.startswith("<?"):
                if "?>" not in stripped[2:]:
                    raw_html_end = "?>"
                offset += len(raw_line)
                continue
            if re.match(r"^<![A-Z]", stripped) is not None:
                if ">" not in stripped[2:]:
                    raw_html_end = ">"
                offset += len(raw_line)
                continue
            if (
                BLOCK_HTML_TAG_RE.match(line) is not None
                # Treat any line that starts like an HTML tag as raw HTML
                # until a blank line. This deliberately over-filters in the
                # strict release gate: quoted attributes, custom elements,
                # and self-closing tags must never expose a hidden heading.
                or GENERIC_HTML_BLOCK_RE.match(line) is not None
            ):
                raw_html_until_blank = True
                offset += len(raw_line)
                continue
            fence = FENCE_OPEN_RE.match(line)
            if fence is not None:
                marker = fence.group("fence")
                fence_character = marker[0]
                fence_length = len(marker)
                offset += len(raw_line)
                continue

            release_match = RELEASE_CANDIDATE_RE.fullmatch(line)
            if release_match is not None:
                releases.append(
                    HeadingCandidate(
                        start=offset,
                        end=line_end,
                        line=line,
                        tag=release_match.group("tag"),
                    )
                )
            unreleased_match = UNRELEASED_CANDIDATE_RE.fullmatch(line)
            if unreleased_match is not None:
                unreleased.append(
                    HeadingCandidate(
                        start=offset,
                        end=line_end,
                        line=line,
                        tag=None,
                    )
                )
        in_comment = _advance_html_comment_state(line, in_comment)
        offset += len(raw_line)

    # ``splitlines`` returns no row for an empty string; all real headings have
    # already been visited whether or not the final line ended in a newline.
    return releases, unreleased


def parse_release_entry(
    text: str,
    tag: str,
    *,
    required: bool = True,
) -> Optional[ReleaseEntry]:
    """Return one unique, exact, calendar-valid release entry."""

    if not SEMVER_TAG_RE.fullmatch(tag):
        raise ChangelogMetadataError(
            "release_tag_invalid", f"expected a semantic version tag, got {tag!r}"
        )
    all_candidates, _unreleased_candidates = _visible_heading_candidates(text)
    candidates = [candidate for candidate in all_candidates if candidate.tag == tag]
    if not candidates:
        if required:
            raise ChangelogMetadataError(
                "changelog_entry_missing", f"CHANGELOG.md has no entry for {tag}"
            )
        return None
    if len(candidates) != 1:
        raise ChangelogMetadataError(
            "changelog_entry_duplicate",
            f"CHANGELOG.md must contain exactly one candidate heading for {tag}",
        )

    candidate = candidates[0]
    exact = EXACT_RELEASE_HEADING_RE.fullmatch(candidate.line)
    if exact is None or exact.group("tag") != tag:
        raise ChangelogMetadataError(
            "changelog_heading_invalid",
            f"CHANGELOG.md heading must be exactly '## [{tag}] - YYYY-MM-DD'",
        )
    date_text = exact.group("date")
    try:
        parsed_date = dt.date.fromisoformat(date_text)
    except ValueError as exc:
        raise ChangelogMetadataError(
            "changelog_date_invalid",
            f"CHANGELOG.md entry for {tag} has an invalid calendar date: {date_text}",
        ) from exc
    if parsed_date.isoformat() != date_text:
        raise ChangelogMetadataError(
            "changelog_date_invalid",
            f"CHANGELOG.md entry for {tag} has a non-canonical date: {date_text}",
        )

    next_candidates = [
        match for match in all_candidates if match.start > candidate.start
    ]
    body_end = next_candidates[0].start if next_candidates else len(text)
    body = text[candidate.end:body_end].strip()
    if not body:
        raise ChangelogMetadataError(
            "changelog_entry_empty", f"CHANGELOG.md entry for {tag} is empty"
        )
    return ReleaseEntry(tag=tag, date=date_text, body=body)


def parse_unreleased_entry(text: str) -> UnreleasedEntry:
    """Return the one exact, non-empty Unreleased section."""

    all_release_candidates, candidates = _visible_heading_candidates(text)
    if not candidates:
        raise ChangelogMetadataError(
            "changelog_unreleased_missing",
            "CHANGELOG.md must contain an exact '## [Unreleased]' heading",
        )
    if len(candidates) != 1:
        raise ChangelogMetadataError(
            "changelog_unreleased_duplicate",
            "CHANGELOG.md must contain exactly one Unreleased heading",
        )
    candidate = candidates[0]
    if candidate.line != EXACT_UNRELEASED_HEADING:
        raise ChangelogMetadataError(
            "changelog_unreleased_heading_invalid",
            "CHANGELOG.md heading must be exactly '## [Unreleased]'",
        )
    next_releases = [
        release for release in all_release_candidates if release.start > candidate.start
    ]
    body_end = next_releases[0].start if next_releases else len(text)
    body = text[candidate.end:body_end].strip()
    if not body:
        raise ChangelogMetadataError(
            "changelog_unreleased_empty",
            "CHANGELOG.md Unreleased section is empty; add the changes being released",
        )
    return UnreleasedEntry(
        heading_start=candidate.start,
        heading_end=candidate.end,
        body=body,
        body_end=body_end,
    )


def has_release_candidate(text: str, tag: str) -> bool:
    """Return whether any release-like heading names ``tag``."""

    releases, _unreleased = _visible_heading_candidates(text)
    return any(candidate.tag == tag for candidate in releases)
