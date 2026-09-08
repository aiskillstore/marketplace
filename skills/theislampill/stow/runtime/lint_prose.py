#!/usr/bin/env python3
"""Report-only prose linter.

This module is PACKAGED into the shipped skill. It is import-closed: it imports
only the Python standard library. Findings never change the exit code; an
invalid invocation, such as an unknown or locked profile, exits nonzero. Its
job is to point at prose patterns a human may want to reconsider, not to gate
delivery. Every finding carries ``severity="advisory"``.

The load-bearing behaviour is MASKING. Before any scan, protected regions are
blanked out (replaced with spaces, preserving line and column positions) so
their contents are never flagged:

  * fenced code blocks (``` ... ``` or ~~~ ... ~~~),
  * inline code spans (`like this`),
  * block quotes (lines beginning with ``>``),
  * things that look like a URL, a filesystem path, or a code identifier,
  * inline quoted spans, for the lexical checks (see MASK LAYERS below).

MASK LAYERS. Three layers exist because different checks need different amounts
of the text left visible:

  ``mask_protected``  fences + block quotes + inline code/URL/path/identifier.
                      The general-purpose layer. Length checks run here.
  ``mask_prose``      ``mask_protected`` plus inline quoted spans. Every LEXICAL
                      (term-table) check runs here, so a banned term that is
                      being quoted rather than used is never flagged. The
                      em-dash, semicolon, and contraction checks also use this
                      layer so attributed text remains outside their scope.
  ``mask_latin``      fences + block quotes + inline code/URL/path only. The
                      identifier mask would eat ``e.g.`` and ``i.e.``, so the
                      Latin-abbreviation check runs one layer shallower.

TERM TABLES ARE LOADED AT RUNTIME. The lexical checks read their terms from
``corpus/prose-integrity/banned-lists.md``, parsed out of that file's markdown
tables and bullet lists on each run. No term list is hard-coded here. If the
file is absent or unreadable the lexical checks silently return nothing --
report-only means a missing input is not an error.

PARTIAL CHECKS. Where only part of a contextual rule is mechanizable
(contractions, for instance, are detectable but the "no omitted words" half of
the same rule is not), the closed matcher is declared as an advisory validator.
It never upgrades the owning G1 rule to callable compliance.
"""

import argparse
import bisect
import json
import os
import re
import sys

# The profile resolver is a packaged sibling module, not a dependency. When
# this file is run as a script its directory is already first on sys.path;
# when it is loaded by path (importlib) the directory may not be, so it is
# inserted explicitly before the sibling import.
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
import profiles


# --------------------------------------------------------------------------- #
# Advisory
# --------------------------------------------------------------------------- #

class Advisory:
    """One report-only finding.

    ``rule`` is this linter's short check name and is always present.
    ``rule_id`` is the registry record id when the check maps onto one, else
    ``None`` (some term tables have no single governing record).
    """

    def __init__(self, line, col, rule, message, rule_id=None,
                 severity="advisory"):
        self.line = line
        self.col = col
        self.rule = rule
        self.message = message
        self.rule_id = rule_id
        self.severity = severity

    def as_dict(self):
        return {
            "line": self.line,
            "col": self.col,
            "rule": self.rule,
            "rule_id": self.rule_id,
            "severity": self.severity,
            "explanation": self.message,
        }

    def __repr__(self):
        return "Advisory(%d:%d [%s] %s)" % (self.line, self.col, self.rule, self.message)


# --------------------------------------------------------------------------- #
# Masking
# --------------------------------------------------------------------------- #

_FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")
_BLOCKQUOTE_RE = re.compile(r"^\s*>")

_INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
_URL_RE = re.compile(r"\b(?:https?://|ftp://|www\.)\S+", re.IGNORECASE)
# Filesystem-ish paths: posix (a/b/c, ./x, ../x, /x) and windows (C:\a\b).
_PATH_RE = re.compile(r"(?:[A-Za-z]:\\[^\s]+|(?:\.{0,2}/)[\w./\-]+|\b[\w\-]+(?:/[\w.\-]+)+)")
# Dotted / snake / underscore identifiers (module.attr, snake_case, a_b_c).
_IDENT_RE = re.compile(r"\b\w+(?:[._]\w+)+\b")
# camelCase identifiers.
_CAMEL_RE = re.compile(r"\b[a-z]+[A-Z]\w*\b")
# Inline quoted spans, straight and curly.
_QUOTE_RE = re.compile(u"\"[^\"\n]*\"|“[^”\n]*”")

_CODEISH_MASKS = (_INLINE_CODE_RE, _URL_RE, _PATH_RE)
_NAMEISH_MASKS = (_IDENT_RE, _CAMEL_RE)
_INLINE_MASKS = _CODEISH_MASKS + _NAMEISH_MASKS


def _blank(text):
    """A run of spaces the same length as ``text`` (preserves columns)."""
    return " " * len(text)


def _sub_blank(pattern, line):
    return pattern.sub(lambda m: _blank(m.group(0)), line)


def _apply(patterns, line):
    for pattern in patterns:
        line = _sub_blank(pattern, line)
    return line


def _mask_inline(line):
    return _apply(_INLINE_MASKS, line)


def _mask_blocks(text, inline):
    """Blank fenced blocks and block quotes, then apply ``inline`` per line."""
    out = []
    in_fence = False
    fence_char = None
    for line in text.split("\n"):
        fence = _FENCE_RE.match(line)
        if in_fence:
            out.append(_blank(line))
            if fence and fence.group(1)[0] == fence_char:
                in_fence = False
                fence_char = None
            continue
        if fence:
            in_fence = True
            fence_char = fence.group(1)[0]
            out.append(_blank(line))
            continue
        if _BLOCKQUOTE_RE.match(line):
            out.append(_blank(line))
            continue
        out.append(inline(line))
    return "\n".join(out)


def mask_protected(text):
    """Return ``text`` with all protected regions blanked to spaces.

    Line count and every column offset are preserved, so advisory positions
    computed on the masked text map straight back onto the original.
    """
    return _mask_blocks(text, _mask_inline)


def mask_latin(text):
    """``mask_protected`` without the identifier mask.

    ``e.g.`` and ``i.e.`` are shaped exactly like a dotted identifier, so the
    Latin-abbreviation check needs this shallower layer. Code, URLs and paths
    are still masked, so a dotted name inside a code span stays protected.
    """
    return _mask_blocks(text, lambda line: _apply(_CODEISH_MASKS, line))


def mask_prose(text):
    """``mask_protected`` plus inline quoted spans.

    This is the layer every LEXICAL check runs on: a banned term that appears
    inside a quotation is being reported, not committed, and is never flagged.
    """
    return _mask_blocks(
        text, lambda line: _sub_blank(_QUOTE_RE, _mask_inline(line)))


def mask_generated_placeholders(text):
    """Mask examples and code-like spans but keep identifier-shaped markers."""
    return _mask_blocks(
        text,
        lambda line: _sub_blank(_QUOTE_RE, _apply(_CODEISH_MASKS, line)))


# --------------------------------------------------------------------------- #
# Term tables -- parsed from banned-lists.md at runtime
# --------------------------------------------------------------------------- #

BANNED_LISTS_RELPATH = ("corpus", "prose-integrity", "banned-lists.md")

# Normalised banned-lists.md heading -> internal bucket. Headings not named here
# (heading anti-patterns, thresholds, prose commentary) carry no term table and
# are deliberately ignored.
_HEADING_BUCKETS = (
    ("overused verbs", "verbs"),
    ("overused adjectives", "adjectives"),
    ("overused metaphorical nouns", "metaphors"),
    ("overused transitions and connectors", "transitions"),
    ("opening phrases to avoid", "filler"),
    ("transitional phrases to avoid", "transitions"),
    ("concluding phrases to avoid", "filler"),
    ("structural patterns to avoid", "structural"),
    ("inflated symbolism phrases", "filler"),
    ("filler words and empty intensifiers", "intensifiers"),
    ("academic-specific ai tells", "academic"),
    ("hedging markers", "hedge_markers"),
    ("ai hedging phrases to flag", "hedge_phrases"),
)

_HEADING_RE = re.compile(r"^\s*#{2,6}\s+(.*?)\s*$")
_BULLET_RE = re.compile(r"^\s*[-*+]\s+(.*)$")
_TABLE_ROW_RE = re.compile(r"^\s*\|(.*)\|\s*$")
_MARKER_LINE_RE = re.compile(r"^\s*\*\*(.+?)\*\*[^:]*:\s*(.+)$")
_QUOTED_SPAN_RE = re.compile(u"[\"“]([^\"”\n]+)[\"”]")
_PLACEHOLDER_TAIL_RE = re.compile(
    r"(?:\b(?:a|an|the|of|in|to|as|for|with|and|or|is|are)\b|[,:;])+\s*$",
    re.IGNORECASE)
_BARE_VARIABLE_RE = re.compile(r"\b[XYZ]\b")


def _clean_term(raw):
    """Normalise one table cell or bullet into a matchable term, or None."""
    term = raw.strip()
    # A bracketed placeholder means the rest of the line is a template; keep
    # only the fixed prefix in front of it, then trim the dangling connective
    # the placeholder used to complete ("Whether you're a [X]" -> "Whether
    # you're"). The trim applies ONLY here: a complete term such as "prior to"
    # or "a myriad of" must keep its final word.
    truncated = "[" in term
    if truncated:
        term = term.split("[", 1)[0]
    # Drop an explanatory trailing parenthetical: `delve (into)` -> `delve`.
    term = re.sub(r"\s*\([^)]*\)\s*$", "", term).strip()
    term = term.strip(u"\"“”'‘’ \t")
    while term.endswith("."):
        term = term[:-1].rstrip()
    if truncated:
        term = _PLACEHOLDER_TAIL_RE.sub("", term).strip()
    term = term.strip(u"\"“” \t,:;")
    if not term or not re.search(r"[A-Za-z]", term):
        return None
    if _BARE_VARIABLE_RE.search(term):
        return None
    if len(term.split()) > 8:
        return None
    if truncated and len(term.split()) < 2:
        # "By [doing X], you can [achieve Y]" collapses to a bare "By". One
        # word off a template is too generic to match on.
        return None
    return term


def _bullet_term(body):
    """A bullet contributes its first quoted span, else its whole body."""
    quoted = _QUOTED_SPAN_RE.search(body)
    return _clean_term(quoted.group(1) if quoted else body)


def parse_banned_lists(text):
    """Parse banned-lists.md markdown into ``{bucket: [term, ...]}``.

    Reads the two-column ``| Avoid | Use Instead |`` tables, the bullet lists of
    banned phrases, and the bold-labelled hedging-marker lines. Three-column
    tables and prose commentary carry no term list and are skipped.
    """
    buckets = {}
    bucket = None
    for line in text.split("\n"):
        heading = _HEADING_RE.match(line)
        if heading:
            title = heading.group(1).strip().lower()
            bucket = None
            for prefix, name in _HEADING_BUCKETS:
                if title.startswith(prefix):
                    bucket = name
                    break
            continue
        if bucket is None:
            continue

        row = _TABLE_ROW_RE.match(line)
        if row:
            cells = [c.strip() for c in row.group(1).split("|")]
            if len(cells) != 2:
                continue                                   # not a term table
            head = cells[0].lower()
            if head in ("avoid", "avoid (metaphorical)", "pattern"):
                continue                                   # header row
            if not head.strip("-: "):
                continue                                   # separator row
            term = _clean_term(cells[0])
            if term:
                buckets.setdefault(bucket, []).append(term)
            continue

        marker = _MARKER_LINE_RE.match(line)
        if marker and bucket == "hedge_markers":
            for piece in marker.group(2).split(","):
                term = _clean_term(piece)
                if term:
                    buckets.setdefault(bucket, []).append(term)
            continue

        bullet = _BULLET_RE.match(line)
        if bullet:
            term = _bullet_term(bullet.group(1))
            if term:
                buckets.setdefault(bucket, []).append(term)

    # The structural-patterns bullets are mostly prose descriptions of a shape,
    # not term lists. Only the fixed-prefix opener is mechanizable.
    if "structural" in buckets:
        kept = [t for t in buckets["structural"] if t.lower().startswith("whether")]
        if kept:
            buckets["structural"] = kept
        else:
            del buckets["structural"]

    for name in buckets:
        seen = set()
        unique = []
        for term in buckets[name]:
            key = term.lower()
            if key not in seen:
                seen.add(key)
                unique.append(term)
        buckets[name] = unique
    return buckets


def default_banned_lists_path():
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(here, os.pardir, *BANNED_LISTS_RELPATH))


def load_banned_lists(path=None):
    """Load and parse the term tables. Returns ``{}`` if unavailable."""
    path = path or default_banned_lists_path()
    try:
        with open(path, "rb") as handle:
            text = handle.read().decode("utf-8", errors="replace")
    except OSError:
        return {}                    # report-only: a missing table is not a fail
    return parse_banned_lists(text)


def _term_pattern(term):
    """Whitespace-flexible, apostrophe-flexible, word-bounded pattern."""
    words = term.split()
    parts = []
    for word in words:
        escaped = re.escape(word)
        escaped = escaped.replace(r"\'", u"['’]").replace(u"’", u"['’]")
        parts.append(escaped)
    body = r"\s+".join(parts)
    prefix = r"\b" if term[:1].isalnum() else ""
    suffix = r"\b" if term[-1:].isalnum() else ""
    return prefix + body + suffix


def compile_terms(terms):
    """One alternation per bucket, longest term first so it wins the match."""
    if not terms:
        return None
    ordered = sorted(terms, key=lambda t: (-len(t), t.lower()))
    return re.compile("|".join(_term_pattern(t) for t in ordered), re.IGNORECASE)


# Bucket -> (check name, registry rule id or None, explanation stem).
# Registry validator names this module actually implements as callable checks.
# The enforcement-honesty gate (tests/test_enforcement_status.py) derives the
# permitted 'callable' set from THIS constant, in both directions: a registry
# record may not claim 'callable' for a validator absent here, and a validator
# listed here may not be left under-claimed. Keep it in sync with the checks
# below -- it is the contract that stops the registry asserting code that does
# not run.
IMPLEMENTED_VALIDATORS = frozenset({
    "no-em-dash",
    "no-intensifiers",
    "no-filler-phrases",
    "no-whether-youre-opener",
    "no-weasel-words",
    "no-ai-transitions",
    "no-ai-verbs",
    "no-academic-tells",
    "no-unresolved-generated-placeholders",
    "no-contractions",
    "no-semicolon",
    "no-latin-abbreviations",
    "procedural-sentence-max-20-words",
    "descriptive-sentence-max-25-words",
})


_BUCKET_CHECKS = (
    ("verbs", "action-verb-pattern", "STOW-PRO-020",
     "matched verb %r; review whether it names the exact action in context"),
    ("transitions", "transition-pattern", "STOW-PRO-020",
     "matched transition %r; review whether it serves a clear discourse function"),
    ("filler", "filler-phrase", "STOW-PRO-011",
     "matched filler phrase %r; review whether it adds information"),
    ("intensifiers", "intensifier", "STOW-PRO-009",
     "matched intensifier %r; review whether a stated fact supports it"),
    ("academic", "academic-phrase-pattern", "STOW-PRO-020",
     "matched stock phrase %r; review its function in context"),
    ("structural", "whether-youre-opener", "STOW-PRO-011",
     "matched audience opener %r; review whether the distinction changes the guidance"),
    ("hedge_phrases", "weasel-phrase", "STOW-PRO-015",
     "matched uncertainty phrase %r; review whether evidence requires it"),
)


# --------------------------------------------------------------------------- #
# Punctuation / structure patterns
# --------------------------------------------------------------------------- #

_EM_DASH_RE = re.compile(u"—")  # em dash
_SEMICOLON_RE = re.compile(";")
_LATIN_RE = re.compile(
    r"\b(?:e\.g\.|i\.e\.|etc\.|viz\.|cf\.|et\s+al\.|N\.B\.)", re.IGNORECASE)
# Unambiguous contraction suffixes, plus the closed set of pronoun+is/has forms
# (a bare 's is far more often a possessive).
_CONTRACTION_RE = re.compile(
    u"\\b\\w+n['’]t\\b"
    u"|\\b\\w+['’](?:re|ve|ll|d|m)\\b"
    u"|\\b(?:it|that|there|here|what|who|let|he|she|one|which)['’]s\\b",
    re.IGNORECASE)
_UNRESOLVED_GENERATED_PLACEHOLDER_RE = re.compile(
    r"(?<![\w./\\-])"
    r"(?:oaicite|contentReference|attributableIndex|grok_card|turn\d+(?:search|view|fetch)\d+)"
    r"(?![\w/\\-]|\.(?=[\w/\\-]))",
    re.IGNORECASE)
_LIST_ITEM_RE = re.compile(r"^(\s*)(?:[-*+]|\d+[.)])\s+\S")
_HEADING_LINE_RE = re.compile(r"^\s*#")
_TABLE_LINE_RE = re.compile(r"^\s*\|")
_SENTENCE_SPLIT_RE = re.compile(u"(?<=[.!?])\\s+(?=[A-Z\"“(\\[])")
_PARENTHETICAL_RE = re.compile(r"\([^)]*\)")
_WORDISH_RE = re.compile(r"[A-Za-z0-9]")

PROCEDURAL_MAX_WORDS = 20
DESCRIPTIVE_MAX_WORDS = 25

CONTROLLED_TECHNICAL = "controlled-technical"


def count_words(sentence):
    """Word count under the token rules the length caps are stated in.

    A parenthetical group counts as one word and a hyphenated group counts as
    one word, so both collapse to a single token before the split.
    """
    collapsed = _PARENTHETICAL_RE.sub(" _parenthetical_ ", sentence)
    return sum(1 for token in collapsed.split() if _WORDISH_RE.search(token))


# --------------------------------------------------------------------------- #
# Region model for the length caps
# --------------------------------------------------------------------------- #

class _Unit:
    """A contiguous run of prose lines sharing one region."""

    def __init__(self, region):
        self.region = region
        self.parts = []          # (lineno, stripped text)

    def add(self, lineno, text):
        self.parts.append((lineno, text))

    def joined(self):
        """Return (text, starts, linenos) with an offset -> line index."""
        chunks = []
        starts = []
        linenos = []
        offset = 0
        for lineno, text in self.parts:
            starts.append(offset)
            linenos.append(lineno)
            chunks.append(text)
            offset += len(text) + 1
        return " ".join(chunks), starts, linenos


def _units(masked):
    """Split masked text into prose units tagged procedural or descriptive.

    A list item (bullet or numbered) opens a procedural unit; its indented
    continuation lines belong to it. Everything else is descriptive body prose.
    Headings, table rows and blank lines close the current unit and are never
    measured.
    """
    units = []
    current = None
    for lineno, line in enumerate(masked.split("\n"), start=1):
        stripped = line.strip()
        if not stripped or _HEADING_LINE_RE.match(line) or _TABLE_LINE_RE.match(line):
            current = None
            continue
        item = _LIST_ITEM_RE.match(line)
        if item:
            current = _Unit("procedural")
            units.append(current)
            current.add(lineno, stripped)
            continue
        if current is None:
            current = _Unit("descriptive")
            units.append(current)
        current.add(lineno, stripped)
    return units


def _unit_sentences(unit):
    """Yield (lineno, sentence) for every sentence in ``unit``."""
    text, starts, linenos = unit.joined()
    if not text.strip():
        return
    offset = 0
    for sentence in _SENTENCE_SPLIT_RE.split(text):
        index = text.find(sentence, offset)
        if index < 0:
            index = offset
        offset = index + len(sentence)
        slot = bisect.bisect_right(starts, index) - 1
        yield linenos[max(slot, 0)], sentence


# --------------------------------------------------------------------------- #
# Individual checks
# --------------------------------------------------------------------------- #

def _scan(pattern, masked, rule, rule_id, message):
    out = []
    if pattern is None:
        return out
    for lineno, line in enumerate(masked.split("\n"), start=1):
        for match in pattern.finditer(line):
            out.append(Advisory(lineno, match.start() + 1, rule,
                                message % match.group(0) if "%" in message
                                else message,
                                rule_id=rule_id))
    return out


def check_lexical(text, tables):
    """(a) LEXICAL -- every term table, matched on the quotation-masked layer."""
    masked = mask_prose(text)
    found = []
    for bucket, rule, rule_id, stem in _BUCKET_CHECKS:
        pattern = compile_terms(tables.get(bucket))
        if pattern is None:
            continue
        for lineno, line in enumerate(masked.split("\n"), start=1):
            for match in pattern.finditer(line):
                found.append((lineno, match.start(), len(match.group(0)),
                              Advisory(lineno, match.start() + 1, rule,
                                       stem % match.group(0), rule_id=rule_id)))
    # A term can sit in more than one table. Keep the longest match at each
    # position and drop anything overlapping an already-accepted span.
    found.sort(key=lambda f: (f[0], f[1], -f[2]))
    accepted = []
    end_by_line = {}
    for lineno, start, length, advisory in found:
        if start < end_by_line.get(lineno, -1):
            continue
        end_by_line[lineno] = start + length
        accepted.append(advisory)
    return accepted


def check_hedging(text, tables):
    """Hedging markers, reported only as a cluster.

    Single markers (may, might, could) are ordinary technical English. The term
    table itself sets a density threshold rather than banning the words, so this
    fires only when two or more land on the same line.
    """
    pattern = compile_terms(tables.get("hedge_markers"))
    if pattern is None:
        return []
    masked = mask_prose(text)
    out = []
    for lineno, line in enumerate(masked.split("\n"), start=1):
        hits = list(pattern.finditer(line))
        if len(hits) >= 2:
            words = ", ".join(sorted({h.group(0).lower() for h in hits}))
            out.append(Advisory(
                lineno, hits[0].start() + 1, "hedging",
                "uncertainty cluster (%s); review whether each qualifier is evidence-grounded"
                % words, rule_id="STOW-PRO-015"))
    return out


def check_generated_placeholders(text):
    """Report a closed set of unresolved generated-artifact markers.

    The scan is advisory and uses the quotation-masked prose layer. Literal
    examples, code, configuration, quotations, identifiers, and other protected
    regions remain untouched. A host may block only under its own explicit
    output contract and final-candidate custody.
    """
    return _scan(
        _UNRESOLVED_GENERATED_PLACEHOLDER_RE,
        mask_generated_placeholders(text),
        "unresolved-generated-placeholder",
        "STOW-PRO-020",
        "unresolved generated placeholder %r; resolve it or preserve it only as a literal example")


def check_punctuation(text, profile_record):
    """(b) PUNCTUATION / STRUCTURE.

    ``profile_record`` is a resolved profile record; each profile-gated check
    asks the resolver whether it is active. The em-dash detector is a
    profile-independent advisory.
    """
    prose = mask_prose(text)
    out = []

    out.extend(_scan(
        _EM_DASH_RE, prose, "em-dash", "STOW-PRO-001",
        "em-dash (U+2014); review punctuation against the applicable style contract"))

    if profiles.check_active("semicolon", profile_record):
        out.extend(_scan(
            _SEMICOLON_RE, prose, "semicolon", "STOW-PCT-001",
            "semicolon; write two separate sentences instead"))

    if profiles.check_active("latin-abbreviation", profile_record):
        out.extend(_scan(
            _LATIN_RE, mask_latin(text), "latin-abbreviation", "STOW-GEN-006",
            "Latin abbreviation %r; use the English words"))

    if profiles.check_active("contraction", profile_record):
        out.extend(_scan(
            _CONTRACTION_RE, prose, "contraction", "STOW-SEN-002",
            "contraction %r; write both words in full "
            "(partial check: the omitted-word half of this rule is not mechanized)"))

    return out


def check_lengths(text, profile_record):
    """(c) LENGTH CAPS, each applied only to its own region.

    The two sentence caps are profile-gated.
    """
    masked = mask_protected(text)
    out = []
    caps_active = {
        "procedural": profiles.check_active(
            "procedural-sentence-length", profile_record),
        "descriptive": profiles.check_active(
            "descriptive-sentence-length", profile_record),
    }
    for unit in _units(masked):
        if not caps_active[unit.region]:
            continue
        limit = (PROCEDURAL_MAX_WORDS if unit.region == "procedural"
                 else DESCRIPTIVE_MAX_WORDS)
        rule_id = ("STOW-PRC-001" if unit.region == "procedural"
                   else "STOW-DSC-003")
        rule = "%s-sentence-length" % unit.region
        for lineno, sentence in _unit_sentences(unit):
            words = count_words(sentence)
            if words > limit:
                out.append(Advisory(
                    lineno, 1, rule, rule_id=rule_id,
                    message="%s sentence runs %d words (cap %d); split it"
                            % (unit.region, words, limit)))

    return out


# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #

# File extensions treated as structured artifacts: prose checks do not apply.
STRUCTURED_EXTENSIONS = (".json", ".jsonl", ".yaml", ".yml")


def lint(text, profile=None, tables=None, banned_lists_path=None,
         artifact_type=None):
    """Return the list of :class:`Advisory` for ``text``.

    ``profile`` is a profile id or alias from ``rules/profiles.json``; ``None``
    resolves to the default profile. Profile-gated checks run only where their
    owning profile activates them. ``artifact_type`` of ``"structured"`` or
    ``"raw"`` suppresses every prose check (structured data is a protected
    region; use validate.py on it).

    Raises :class:`profiles.ProfileError` on an unknown or locked profile —
    profile identity is a contract input, not a finding.
    """
    if artifact_type in ("structured", "raw"):
        return []
    profile_record = profiles.resolve(profile)
    if tables is None:
        tables = load_banned_lists(banned_lists_path)
    advisories = []
    advisories.extend(check_punctuation(text, profile_record))
    advisories.extend(check_lexical(text, tables))
    advisories.extend(check_hedging(text, tables))
    advisories.extend(check_generated_placeholders(text))
    advisories.extend(check_lengths(text, profile_record))
    advisories.sort(key=lambda a: (a.line, a.col, a.rule))
    return advisories


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def _profile_choices():
    data = profiles.load_profiles()
    names = []
    for record in data["profiles"]:
        names.append(record["id"])
        names.extend(record.get("aliases", []))
    return names


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Report (never fail on) advisory prose patterns. "
                    "Findings never change the exit code; only an invalid "
                    "invocation (unknown or locked profile) exits nonzero.")
    parser.add_argument("file", help="path to the prose file to lint")
    parser.add_argument("--profile", choices=_profile_choices(), default=None,
                        help="profile id or alias from rules/profiles.json "
                             "(default: stow-default)")
    parser.add_argument("--artifact-type",
                        choices=["prose", "structured", "raw"], default=None,
                        help="override artifact detection; 'prose' forces "
                             "prose checks on a structured-looking file")
    parser.add_argument("--banned-lists", default=None,
                        help="override the path to the term tables")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args(argv)

    try:
        profile_record = profiles.resolve(args.profile)
    except profiles.LockedProfileError as exc:
        print("lint_prose: %s" % exc, file=sys.stderr)
        return 2
    except profiles.UnknownProfileError as exc:
        print("lint_prose: %s" % exc, file=sys.stderr)
        return 2

    try:
        with open(args.file, "rb") as handle:
            text = handle.read().decode("utf-8", errors="replace")
    except OSError as exc:
        # Report-only: even an unreadable file is not a failure of the linter.
        print("lint_prose: cannot read %s: %s" % (args.file, exc))
        return 0

    artifact_type = args.artifact_type
    note = None
    if artifact_type is None and args.file.lower().endswith(STRUCTURED_EXTENSIONS):
        artifact_type = "structured"
    if artifact_type in ("structured", "raw"):
        try:
            json.loads(text)
            parse_state = "parses as JSON"
        except ValueError:
            parse_state = ("structured extension but does not parse as JSON; "
                           "pass --artifact-type prose to lint it as prose")
        note = ("structured artifact (%s): prose checks do not apply; "
                "use validate.py" % parse_state)

    advisories = lint(text, profile=args.profile,
                      banned_lists_path=args.banned_lists,
                      artifact_type=artifact_type)

    if args.format == "json":
        print(json.dumps({
            "tool": "lint_prose",
            "file": args.file,
            "report_only": True,
            "profile": profile_record["id"],
            "profile_source": "cli" if args.profile else "default",
            "guidance_active": profile_record.get("guidance_rules", []),
            "artifact_type": artifact_type or "prose",
            "note": note,
            "findings": [a.as_dict() for a in advisories],
        }, indent=2, sort_keys=True))
        return 0

    if note:
        print("lint_prose: %s: %s" % (args.file, note))
        return 0
    if not advisories:
        print("lint_prose: no advisories for %s (profile %s)"
              % (args.file, profile_record["id"]))
    else:
        print("lint_prose: %d advisory(ies) for %s (profile %s; report only, "
              "exit 0)" % (len(advisories), args.file, profile_record["id"]))
        for adv in advisories:
            print("  %d:%d [%s] %s%s: %s"
                  % (adv.line, adv.col, adv.rule,
                     adv.rule_id + " " if adv.rule_id else "",
                     adv.severity, adv.message))
    if profile_record.get("guidance_rules"):
        print("lint_prose: guidance-active (review-level, no mechanical "
              "check): %s" % ", ".join(profile_record["guidance_rules"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
