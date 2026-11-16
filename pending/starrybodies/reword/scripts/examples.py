"""Select a few relevant editorial examples locally; no model or network calls.

The asset's retrieval metadata stays on disk. Returned objects contain only id,
action (rewrite/keep), before, after, and reason. ``budget_chars`` bounds the
entire returned list under ordinary ``json.dumps`` serialization. Examples are
kept whole: a small budget can return no examples.

Pass existing lint findings to avoid another rule scan. Entries may be rule-ID
strings or mappings with a ``rule`` or ``id`` field; other fields never enter
the result. With no findings, the selector scans rules.json itself. Findings
are editorial cues, not commands to rewrite. A matching keep example can show
why a useful contrast or list should stay.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from functools import lru_cache
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
DESTINATIONS = frozenset({"general", "text-message", "chat", "email", "linkedin", "cover-letter", "essay", "web-copy"})
MODES = frozenset({"light", "rewrite", "deep"})
_DESTINATION_ALIASES = {
    "text": "text-message", "texting": "text-message", "sms": "text-message",
    "text-messages": "text-message", "message": "text-message", "whatsapp": "text-message",
    "slack": "chat", "discord": "chat", "dm": "chat", "direct-message": "chat",
    "e-mail": "email", "professional-email": "email", "warm-professional-email": "email",
    "coverletter": "cover-letter", "application": "cover-letter", "job-application": "cover-letter",
    "lyrical-essay": "essay", "personal-essay": "essay", "launch": "web-copy",
    "website": "web-copy", "web": "web-copy", "marketing": "web-copy", "technical": "general",
}
_GENRE_ALIASES = {
    "technical-note": "technical", "technical-notes": "technical", "tech": "technical",
    "lyrical": "creative", "lyrical-essay": "creative", "essay": "creative",
    "humor": "creative", "dry-humor": "creative", "literary": "creative",
    "launch": "professional", "business": "professional", "formal": "professional",
}
_STOPWORDS = frozenset("a an and are as at be before but by can could for from had has have i in is it its may my of on or our that the their them they this to was we were will with you your".split())
_PUBLIC_FIELDS = ("id", "action", "before", "after", "reason")


def _key(value: str, field: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field} must be a string.")
    return re.sub(r"[\s_]+", "-", value.strip().casefold())


def _context(destination: str, genre: str) -> tuple[str, str]:
    raw_destination, raw_genre = _key(destination, "destination"), _key(genre, "genre")
    destination = _DESTINATION_ALIASES.get(raw_destination, raw_destination)
    genre = _GENRE_ALIASES.get(raw_genre, raw_genre)
    destination = destination if destination in DESTINATIONS else "general"
    genre = genre if genre in {"general", "professional", "technical", "creative"} else "general"
    if genre == "general" and raw_destination == "technical":
        genre = "technical"
    if genre == "general" and destination == "essay":
        genre = "creative"
    if destination == "general" and raw_genre == "launch":
        destination = "web-copy"
    return destination, genre


@lru_cache(maxsize=1)
def _rules() -> tuple[tuple[str, re.Pattern, int], ...]:
    data = json.loads((ROOT / "assets/rules.json").read_text(encoding="utf-8"))
    return tuple((rule["id"], re.compile(rule["pattern"], re.IGNORECASE), rule.get("priority", 1)) for rule in data)


@lru_cache(maxsize=1)
def _corpus() -> tuple[dict, ...]:
    data = json.loads((ROOT / "assets/editorial_examples.json").read_text(encoding="utf-8"))
    return tuple({**entry, "_signals": tuple(re.compile(pattern, re.IGNORECASE) for pattern in entry.get("signals", [])),
                  "_tokens": _tokens(entry["before"])} for entry in data["examples"])


def _visible(text: str) -> str:
    """Mask literals and quotations before scoring; never use them as repair cues."""
    chars = list(text)

    def mask(start: int, end: int) -> None:
        chars[start:end] = ["\n" if c == "\n" else " " for c in text[start:end]]

    # Line-based fences preserve length and also cover a final unclosed fence.
    offset, fence = 0, None
    for line in text.splitlines(keepends=True):
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
        was_open = fence is not None
        if fence is None and marker:
            fence = (marker[1][0], len(marker[1]))
        elif fence is not None and re.fullmatch(r" {0,3}" + re.escape(fence[0]) + "{" + str(fence[1]) + r",}\s*", line):
            fence = None
        if was_open or fence is not None or marker:
            mask(offset, offset + len(line))
        offset += len(line)

    literal_patterns = (
        r"(?m)^(?: {4}|\t)\S[^\n]*",  # indented code
        r"(`+)[^`]*?\1",                # inline code
        r"\b(?:https?://|www\.)[^\s<>]+",
        r'"[^"\n]+"|“[^”\n]+”|‘[^’\n]+’',
        r"(?<!\w)'(?:[^'\n]|(?<=\w)'(?=\w))+'(?!\w)",
    )
    for pattern in literal_patterns:
        for match in re.finditer(pattern, text):
            mask(match.start(), match.end())
    return "".join(chars)


def _tokens(text: str) -> frozenset[str]:
    return frozenset(word for word in re.findall(r"[a-z][a-z0-9_'-]*", text.casefold()) if len(word) > 2 and word not in _STOPWORDS)


def _finding_ids(findings: Iterable | Mapping | str | None, visible: str) -> set[str]:
    known = {identifier for identifier, _, _ in _rules()}
    if findings is None:
        return {identifier for identifier, pattern, _ in _rules() if pattern.search(visible)}
    if isinstance(findings, (str, Mapping)):
        findings = [findings]
    try:
        entries = iter(findings)
    except TypeError as exc:
        raise ValueError("findings must contain rule IDs or finding objects.") from exc
    found = set()
    for entry in entries:
        identifier = entry if isinstance(entry, str) else entry.get("rule", entry.get("id")) if isinstance(entry, Mapping) else None
        if isinstance(identifier, str) and identifier in known:
            found.add(identifier)
    return found


def select_examples(text: str, *, destination: str = "general", genre: str = "general",
                    mode: str = "rewrite", limit: int = 2, budget_chars: int = 900,
                    findings=None) -> list[dict[str, str]]:
    """Return whole relevant examples, deterministically ranked and sparsely packed.

    Ordinary clean prose returns []. In creative/light work a recognizable
    rhythm, purposeful punctuation, or dry joke may earn one unchanged example.
    Destination aliases are accepted; unfamiliar destinations use general.
    Lowercase/texting abbreviations are cues for polishing only in formal
    destinations, not a reason to manufacture informality in other work.
    """
    if not isinstance(text, str):
        raise ValueError("text must be a string.")
    for name, value in (("limit", limit), ("budget_chars", budget_chars)):
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError(f"{name} must be a nonnegative integer.")
    mode = _key(mode, "mode")
    if mode not in MODES:
        raise ValueError("Choose light, rewrite, or deep mode.")
    destination, genre = _context(destination, genre)
    if not text.strip() or not limit or budget_chars < 2:
        return []

    visible = _visible(text)
    active = _finding_ids(findings, visible)
    weights = {identifier: 5 + 2 * priority for identifier, _, priority in _rules()}
    query_tokens = _tokens(visible)
    ranked = []
    for entry in _corpus():
        if destination not in entry["destinations"] or mode not in entry.get("modes", MODES):
            continue
        matched = active.intersection(entry["rules"])
        signals = sum(bool(pattern.search(visible)) for pattern in entry["_signals"])
        if entry.get("needs_signal") and not signals:
            continue
        creative_keep = (not active and genre == "creative" and mode == "light"
                         and entry.get("creative_light") and bool(signals))
        if entry["action"] == "keep":
            if not matched and not creative_keep:
                continue
        elif not matched and (entry["rules"] or not signals):
            continue
        score = sum(weights[identifier] for identifier in matched) + 10 * min(signals, 2)
        score += 4 if len(entry["destinations"]) == 1 else 0
        score += 3 if genre in entry["genres"] else -3
        score += 2 * min(len(query_tokens.intersection(entry["_tokens"])), 5)
        ranked.append((-score, entry["id"], entry, matched))

    result, covered_rules, families = [], set(), set()
    for _, _, entry, matched in sorted(ranked, key=lambda item: (item[0], item[1])):
        if entry["family"] in families or (matched and matched.issubset(covered_rules)):
            continue
        # Even a caller requesting many examples receives at most three.
        if len(result) >= min(limit, 3):
            break
        item = {field: entry[field] for field in _PUBLIC_FIELDS}
        if len(json.dumps([*result, item])) > budget_chars:
            continue
        result.append(item)
        covered_rules.update(matched)
        families.add(entry["family"])
        if not active:  # a keep example is reassurance, not another rulebook
            break
    return result
