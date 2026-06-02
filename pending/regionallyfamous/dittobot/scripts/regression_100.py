#!/usr/bin/env python3
"""Dittobot regression harness.

Generates 100 bad-text rewrite cases and checks the rewritten outputs for
voice preservation, factual fidelity, concision, constraint handling, and
generic-AI prose markers.

This is a deterministic stress suite for the skill instructions. It does not
call an LLM; it keeps reusable acceptance checks out of SKILL.md so the skill
stays fast and token-responsible.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field, replace


GENERIC_MARKERS = [
    "in today's",
    "rapidly evolving",
    "transformative",
    "robust",
    "seamless",
    "empower",
    "unlock",
    "elevate",
    "drive impact",
    "at the heart",
    "ultimately",
    "it's important to note",
    "value for stakeholders",
    "game-changing",
    "innovative",
    "circle back",
    "alignment",
    "synergy",
    "best-in-class",
    "customer-centricity",
    "operational excellence",
    "meaningful impact",
    "full potential",
    "industry-leading",
    "backed by research",
    "research-backed",
    "next-generation",
    "ecosystem",
    "at scale",
    "streamline",
    "holistic",
    "data-driven",
    "future-proof",
    "end-to-end",
    "frictionless",
    "paradigm",
]

INVENTED_DETAIL_MARKERS = [
    "millions",
    "thousands",
    "fortune 500",
    "revenue",
    "market share",
    "ai-powered",
    "patented",
    "award-winning",
    "guaranteed",
    "proven",
    "98%",
    "97%",
    "97 percent",
    "certified",
    "used by",
    "trusted by",
    "global brands",
    "40 percent",
    "in two weeks",
    "cut ticket volume",
    "reduced churn",
    "roi",
    "customers report",
]

NOTE_MARKERS = [
    r"(?im)^\*\*what changed\*\*",
    r"(?im)^\*\*note\*\*",
    r"(?im)^note:",
    r"(?im)^sure[:,]",
    r"(?im)^here'?s\b",
    r"(?im)^cleaner version:",
    r"(?im)^i (tightened|changed|kept|made)\b",
]

WRAPPER_MARKERS = [
    r"(?im)^\*\*rewrite\*\*",
    r"(?im)^rewrite:",
    r"(?im)^rewritten version:",
    r"(?im)^cleaned up:",
    r"(?im)^option \d+:",
]

CLARIFYING_MARKERS = [
    "can you clarify",
    "could you clarify",
    "please clarify",
    "what audience",
    "who is the audience",
    "could you share",
    "can you share",
    "what format",
    "what tone",
    "i need more context",
]

MODALITY_DRIFT_MARKERS = [
    "must",
    "definitely",
    "certainly",
    "guaranteed",
    "proven",
    "will happen",
]

CAUSALITY_DRIFT_MARKERS = [
    "root cause",
    "caused by",
    "due to the database",
    "latency",
    "database",
    "user error",
]


@dataclass(frozen=True)
class Case:
    id: str
    source: str
    rewrite: str
    must: tuple[str, ...]
    forbid: tuple[str, ...] = ()
    allow_note: bool = False
    allow_expand: bool = False
    exact_words: int | None = None
    max_ratio: float = 1.35
    no_dash: bool = False
    diagnosis: bool = False
    max_words: int | None = None
    min_question_marks: int = 0
    max_question_marks: int | None = None
    forbid_clarifying: bool = False
    forbid_wrappers: bool = False
    forbid_bullets: bool = False
    exact_paragraphs: int | None = None
    max_paragraphs: int | None = None
    starts_with: str | None = None
    ends_with: str | None = None
    exact_substrings: tuple[str, ...] = field(default_factory=tuple)
    line_prefixes: tuple[str, ...] = field(default_factory=tuple)
    ordered_terms: tuple[str, ...] = field(default_factory=tuple)
    required_claims: tuple[str, ...] = field(default_factory=tuple)
    forbid_assertions: tuple[str, ...] = field(default_factory=tuple)
    forbid_artifacts: tuple[str, ...] = field(default_factory=tuple)
    preserve_uncertainty: bool = False
    allow_markdown_fence: bool = False
    prompt_mode: str = "explicit_rewrite"
    protected: tuple[str, ...] = field(default_factory=tuple)
    preserve_voice: tuple[str, ...] = field(default_factory=tuple)


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9']+", text)


def strip_quoted(text: str) -> str:
    text = re.sub(r"`[^`]*`", "", text)
    text = re.sub(r'"[^"]*"', "", text)
    text = re.sub(r"'[^']*'", "", text)
    text = re.sub(r"\u201c[^\u201d]*\u201d", "", text)
    return text


def normalized(text: str) -> str:
    return " ".join(words(text.lower()))


def contains_term(text: str, term: str) -> bool:
    haystack = words(text.lower())
    needle = words(term.lower())
    if not needle:
        return True
    width = len(needle)
    return any(haystack[index:index + width] == needle for index in range(len(haystack) - width + 1))


def has_note(text: str) -> bool:
    return any(re.search(pattern, text) for pattern in NOTE_MARKERS)


def has_wrapper(text: str) -> bool:
    return any(re.search(pattern, text) for pattern in WRAPPER_MARKERS)


def count_markers(text: str, markers: list[str]) -> list[str]:
    return [marker for marker in markers if contains_term(text, marker)]


def term_index(text: str, term: str) -> int | None:
    haystack = words(text.lower())
    needle = words(term.lower())
    if not needle:
        return 0
    width = len(needle)
    for index in range(len(haystack) - width + 1):
        if haystack[index:index + width] == needle:
            return index
    return None


def paragraph_count(text: str) -> int:
    return len([part for part in re.split(r"\n\s*\n", text.strip()) if part.strip()])


def has_bullet_line(text: str) -> bool:
    return any(re.search(r"^\s*(?:[-*+]|\d+[.)])\s+", line) for line in text.splitlines())


def numeric_claims(text: str) -> set[str]:
    return {
        match.lower()
        for match in re.findall(
            r"\$?\b\d+(?::\d+)?(?:[.,]\d+)*(?:\.\d+)?%?\b",
            text,
        )
    }


def pad_to_exact_words(text: str, exact: int) -> str:
    """Append neutral words until text reaches an exact word count."""
    filler = "Please name owners clearly before launch today now"
    current = len(words(text))
    if current > exact:
        raise ValueError(f"text has {current} words, cannot shrink to {exact}: {text}")
    if current == exact:
        return text
    needed = exact - current
    return f"{text} {' '.join(words(filler)[:needed])}."


def remove_phrase(text: str, phrase: str) -> str | None:
    """Remove the first exact phrase match, ignoring case."""
    match = re.search(re.escape(phrase), text, flags=re.IGNORECASE)
    if not match:
        return None
    return (text[:match.start()] + text[match.end():]).strip()


def replace_phrase_all(text: str, phrase: str, replacement: str) -> str:
    """Replace every exact phrase match, ignoring case."""
    return re.sub(re.escape(phrase), replacement, text, flags=re.IGNORECASE)


def drop_uncertainty_words(text: str) -> str:
    text = re.sub(r"\bprobably\s+", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\bmay\s+", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\bmight\s+", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\bI think\s+", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def validate(case: Case) -> list[str]:
    errors: list[str] = []
    unquoted = strip_quoted(case.rewrite)
    unquoted_lower = unquoted.lower()

    missing = [term for term in case.must if not contains_term(case.rewrite, term)]
    if missing:
        errors.append(f"missing required terms: {missing}")

    missing_voice = [
        term for term in case.preserve_voice if not contains_term(case.rewrite, term)
    ]
    if missing_voice:
        errors.append(f"lost voice markers: {missing_voice}")

    missing_protected = [
        term for term in case.protected if not contains_term(case.rewrite, term)
    ]
    if missing_protected:
        errors.append(f"lost protected facts: {missing_protected}")

    missing_exact = [
        snippet for snippet in case.exact_substrings if snippet not in case.rewrite
    ]
    if missing_exact:
        errors.append(f"lost exact substrings: {missing_exact}")

    if case.line_prefixes:
        lines = [line.rstrip() for line in case.rewrite.splitlines()]
        missing_prefixes = [
            prefix for prefix in case.line_prefixes
            if not any(line.startswith(prefix) for line in lines)
        ]
        if missing_prefixes:
            errors.append(f"lost required line prefixes: {missing_prefixes}")

    forbidden = [term for term in case.forbid if contains_term(unquoted, term)]
    if forbidden:
        errors.append(f"forbidden terms appeared: {forbidden}")

    missing_claims = [
        claim for claim in case.required_claims if not contains_term(case.rewrite, claim)
    ]
    if missing_claims:
        errors.append(f"missing required claims: {missing_claims}")

    forbidden_assertions = [
        claim for claim in case.forbid_assertions if contains_term(unquoted, claim)
    ]
    if forbidden_assertions:
        errors.append(f"forbidden assertions appeared: {forbidden_assertions}")

    forbidden_artifacts = [
        term for term in case.forbid_artifacts
        if words(term) and contains_term(case.rewrite, term)
    ]
    forbidden_artifacts.extend(
        term for term in case.forbid_artifacts
        if not words(term) and term in case.rewrite
    )
    if forbidden_artifacts:
        errors.append(f"note artifacts appeared: {forbidden_artifacts}")

    if case.ordered_terms:
        positions = [(term, term_index(case.rewrite, term)) for term in case.ordered_terms]
        missing_ordered = [term for term, index in positions if index is None]
        if missing_ordered:
            errors.append(f"missing ordered terms: {missing_ordered}")
        present_positions = [index for _, index in positions if index is not None]
        if present_positions != sorted(present_positions):
            errors.append(f"ordered terms out of order: {case.ordered_terms}")

    generic = [
        marker
        for marker in count_markers(case.rewrite, GENERIC_MARKERS)
        if not any(marker in voice.lower() for voice in case.preserve_voice)
    ]
    if generic:
        errors.append(f"generic markers appeared: {generic}")

    invented = count_markers(case.rewrite, INVENTED_DETAIL_MARKERS)
    if invented:
        errors.append(f"invented-detail markers appeared: {invented}")

    source_numbers = numeric_claims(case.source)
    rewrite_numbers = numeric_claims(case.rewrite)
    invented_numbers = sorted(rewrite_numbers - source_numbers)
    if invented_numbers:
        errors.append(f"invented numeric claims appeared: {invented_numbers}")

    if any(contains_term(case.source, term) for term in ("maybe", "may", "might", "probably")):
        drift = [
            term
            for term in MODALITY_DRIFT_MARKERS
            if contains_term(unquoted, term) and not contains_term(case.source, term)
        ]
        if drift:
            errors.append(f"modality drift markers appeared: {drift}")

    if case.preserve_uncertainty:
        uncertainty_markers = (
            "maybe",
            "may",
            "might",
            "probably",
            "not definitive",
            "not state that as definitive",
            "I think",
        )
        if not any(contains_term(case.rewrite, marker) for marker in uncertainty_markers):
            errors.append("lost uncertainty marker")

    causal_drift = [
        term
        for term in CAUSALITY_DRIFT_MARKERS
        if contains_term(unquoted, term) and not contains_term(case.source, term)
    ]
    if causal_drift:
        errors.append(f"causality drift markers appeared: {causal_drift}")

    if has_note(case.rewrite) and not case.allow_note:
        errors.append("unexpected note/rationale")

    if has_wrapper(case.rewrite) and case.forbid_wrappers:
        errors.append("unexpected rewrite wrapper")

    if case.forbid_clarifying:
        clarifying = [
            marker for marker in CLARIFYING_MARKERS if contains_term(case.rewrite, marker)
        ]
        if clarifying:
            errors.append(f"unexpected clarifying question: {clarifying}")

    if "```" in case.rewrite and not case.allow_markdown_fence:
        errors.append("unexpected markdown fence")

    if case.no_dash and any(mark in case.rewrite for mark in ("-", "\u2010", "\u2011", "\u2012", "\u2013", "\u2014", "\u2212")):
        errors.append("dash constraint violated")

    if case.min_question_marks and case.rewrite.count("?") < case.min_question_marks:
        errors.append(
            f"question mark count failed: expected at least {case.min_question_marks}, "
            f"got {case.rewrite.count('?')}"
        )
    if case.max_question_marks is not None and case.rewrite.count("?") > case.max_question_marks:
        errors.append(
            f"question mark count failed: expected at most {case.max_question_marks}, "
            f"got {case.rewrite.count('?')}"
        )

    if case.forbid_bullets and has_bullet_line(case.rewrite):
        errors.append("unexpected bullet list")

    paragraphs = paragraph_count(case.rewrite)
    if case.exact_paragraphs is not None and paragraphs != case.exact_paragraphs:
        errors.append(
            f"paragraph count failed: expected {case.exact_paragraphs}, got {paragraphs}"
        )
    if case.max_paragraphs is not None and paragraphs > case.max_paragraphs:
        errors.append(
            f"paragraph count failed: expected at most {case.max_paragraphs}, got {paragraphs}"
        )

    if case.starts_with and not case.rewrite.lstrip().lower().startswith(case.starts_with.lower()):
        errors.append(f"opening failed: expected to start with {case.starts_with!r}")
    if case.ends_with and not case.rewrite.rstrip().lower().endswith(case.ends_with.lower()):
        errors.append(f"ending failed: expected to end with {case.ends_with!r}")

    source_words = len(words(case.source))
    rewrite_words = len(words(case.rewrite))

    if case.exact_words is not None and rewrite_words != case.exact_words:
        errors.append(
            f"exact word count failed: expected {case.exact_words}, got {rewrite_words}"
        )
    elif case.max_words is not None and rewrite_words > case.max_words:
        errors.append(
            f"max word count failed: expected at most {case.max_words}, got {rewrite_words}"
        )
    elif not case.allow_expand:
        allowed = max(source_words + 12, int(source_words * case.max_ratio))
        if rewrite_words > allowed:
            errors.append(
                f"too long: source {source_words}, rewrite {rewrite_words}, allowed {allowed}"
            )

    if case.diagnosis and re.search(r"(?im)^\*\*rewrite\*\*", case.rewrite):
        errors.append("diagnosis case produced rewrite heading")

    return errors


def make_cases() -> list[Case]:
    cases: list[Case] = []

    product_subjects = [
        ("platform", "teams", "customers"),
        ("dashboard", "support leads", "users"),
        ("workflow", "editors", "contributors"),
        ("reporting tool", "managers", "operators"),
        ("checkout flow", "store owners", "shoppers"),
        ("publishing system", "writers", "readers"),
        ("admin screen", "site owners", "clients"),
        ("importer", "migration teams", "customers"),
        ("review queue", "moderators", "community members"),
        ("analytics page", "product teams", "customers"),
    ]
    for idx, (thing, audience, reader) in enumerate(product_subjects[:8], 1):
        source = (
            "In today's rapidly evolving landscape, we are thrilled to announce a "
            f"transformative new chapter for our {thing}. This robust solution "
            f"empowers {audience} to unlock seamless collaboration, drive meaningful "
            "impact, and elevate outcomes for stakeholders."
        )
        rewrite = (
            f"We are updating the {thing}.\n\n"
            f"The goal is simple: make it more useful for {audience} and clearer "
            f"for the {reader} who rely on it. The original draft still needs real "
            "specifics: what changed, who it helps, and what people can do now."
        )
        cases.append(
            Case(
                id=f"corporate_specifics_guard_{idx:02d}",
                source=source,
                rewrite=rewrite,
                must=(thing, audience, "real specifics", "what changed"),
                allow_expand=True,
            )
        )

    slack_items = [
        ("screenshots", "legal", "cursed vibes spreadsheet"),
        ("owner", "deadline", "fog machine"),
        ("pricing copy", "approval", "mystery soup"),
        ("QA list", "release note", "haunted checklist"),
        ("design asset", "PM signoff", "vague weather report"),
        ("demo video", "security review", "ritual of confusion"),
        ("migration plan", "support docs", "process fog"),
        ("copy deck", "launch date", "meeting oatmeal"),
        ("API note", "test account", "phantom blocker"),
        ("redirect list", "DNS change", "vibes spreadsheet"),
    ]
    for idx, (a, b, phrase) in enumerate(slack_items[:8], 1):
        source = (
            f"ok so can we stop saying this is blocked unless we say what blocked "
            f"means?? if it's {a} say {a}. if it's {b} say {b}. otherwise this is "
            f"just the {phrase} and i cannot fix a cloud."
        )
        rewrite = (
            "Can we stop saying this is blocked unless we name the blocker?\n\n"
            f"If it is {a}, say {a}. If it is {b}, say {b}. I can help, but I "
            f"need a real list, not the {phrase}."
        )
        cases.append(
            Case(
                id=f"slack_blunt_voice_{idx:02d}",
                source=source,
                rewrite=rewrite,
                must=(a, b, phrase),
                preserve_voice=(phrase,),
            )
        )

    legal_items = [
        ("10 business days", "Acme", "contract"),
        ("five calendar days", "BetaCo", "addendum"),
        ("30 days", "Northwind", "MSA"),
        ("48 hours", "Contoso", "security clause"),
        ("seven business days", "Globex", "renewal language"),
        ("15 days", "Initech", "order form"),
        ("two weeks", "Umbrella", "DPA"),
        ("90 days", "Hooli", "termination clause"),
        ("three business days", "Stark", "support terms"),
        ("60 days", "Wayne", "notice provision"),
    ]
    for idx, (deadline, company, doc) in enumerate(legal_items[:8], 1):
        source = (
            f"Based on the {doc} we looked at Friday, I think we probably have to "
            f"send written notice within {deadline}, but I do not want to state "
            f"that like it is definitely true because I am not counsel and there "
            f"were weird carveouts. We should ask legal before replying to {company}."
        )
        rewrite = (
            f"Based on the {doc} we reviewed Friday, I think we may need to send "
            f"written notice within {deadline}. I would not state that as definitive, "
            f"because I am not counsel and there were unusual carveouts. We should "
            f"ask Legal to confirm before replying to {company}."
        )
        cases.append(
            Case(
                id=f"legal_precision_{idx:02d}",
                source=source,
                rewrite=rewrite,
                must=(deadline, company, "may need", "not counsel", "Legal"),
                protected=(deadline, company, doc),
                required_claims=("may need", "not counsel"),
                preserve_uncertainty=True,
                forbid=(
                    "must send",
                    "required to send",
                    "definitely true",
                    "do not ask Legal",
                    "skip Legal",
                    "reply without Legal",
                ),
            )
        )

    apology_items = [
        ("came in too hot", "weird meeting combat thing"),
        ("got sharper than I meant to", "calendar cage match"),
        ("made it harder", "meeting spiral"),
        ("pushed too hard", "thread duel"),
        ("talked over you", "process wrestling"),
        ("was more blunt than useful", "status-page boxing match"),
        ("jumped in too fast", "decision fog"),
        ("made the room tense", "strategy thunderstorm"),
        ("missed your point", "comment-thread maze"),
        ("turned defensive", "alignment theater"),
    ]
    for idx, (admission, phrase) in enumerate(apology_items[:8], 1):
        source = (
            f"Hey, I was thinking about yesterday and I think I {admission}. I still "
            "disagree with the decision, but I do not like how I made the conversation "
            f"harder. Sorry for that. I want to reset instead of doing the {phrase}."
        )
        rewrite = (
            f"Hey, I have been thinking about yesterday. I {admission}.\n\n"
            "I still disagree with the decision, but I do not like how I made the "
            f"conversation harder. I am sorry for that. I would like to reset instead "
            f"of doing the {phrase}."
        )
        cases.append(
            Case(
                id=f"apology_light_touch_{idx:02d}",
                source=source,
                rewrite=rewrite,
                must=(admission, phrase, "still disagree"),
                forbid=("deeply regret", "sincerely apologize", "harm caused"),
                preserve_voice=(phrase,),
            )
        )

    concise_items = [
        ("review meeting", "Thursday", "Friday"),
        ("planning call", "Tuesday", "Wednesday"),
        ("launch review", "Monday", "Thursday"),
        ("budget discussion", "3:00", "4:30"),
        ("design critique", "morning", "afternoon"),
        ("partner sync", "June 4", "June 5"),
        ("retro", "this week", "next week"),
        ("content review", "noon", "2:00"),
        ("handoff", "today", "tomorrow"),
        ("demo", "Friday", "Monday"),
    ]
    for idx, (meeting, old, new) in enumerate(concise_items[:8], 1):
        source = (
            f"I wanted to reach out because I was wondering if maybe there is a "
            f"possibility that we could potentially move the {meeting} from {old} "
            f"to {new}, because I am still trying to pull things together and I do "
            "not want to waste everyone's time with something that is not ready."
        )
        rewrite = (
            f"Could we move the {meeting} from {old} to {new}? I am still pulling "
            "things together, and I do not want to waste everyone's time with a draft "
            "that is not ready."
        )
        cases.append(
            Case(
                id=f"concision_{idx:02d}",
                source=source,
                rewrite=rewrite,
                must=(meeting, old, new, "not ready"),
                protected=(meeting, old, new),
                forbid=("potentially", "possibility", "reach out"),
            )
        )

    odd_voice_items = [
        ("beige rectangle", "seven nervous staplers"),
        ("wet cardboard", "three anxious binders"),
        ("committee pudding", "five haunted spreadsheets"),
        ("waiting-room pamphlet", "two nervous clipboards"),
        ("cold oatmeal", "a boardroom of staplers"),
        ("software beige", "six cautious calendars"),
        ("sleepy rectangle", "four frightened folders"),
        ("room-temperature soup", "three legal pads in a trench coat"),
        ("printer paper fog", "eight worried bullet points"),
        ("conference-room static", "a choir of soft approvals"),
    ]
    for idx, (image, phrase) in enumerate(odd_voice_items[:8], 1):
        source = (
            f"I keep trying to write this announcement and it keeps turning into a "
            f"{image}. The actual news is good. People will care. But every draft "
            f"sounds like it was assembled by {phrase}."
        )
        rewrite = (
            f"I keep trying to write this announcement, and it keeps turning into a "
            f"{image}. The news is actually good. People will care. But every draft "
            f"sounds like it was assembled by {phrase}."
        )
        cases.append(
            Case(
                id=f"odd_voice_{idx:02d}",
                source=source,
                rewrite=rewrite,
                must=("People will care", image, phrase),
                preserve_voice=(image, phrase),
                forbid=("stakeholders", "brand voice", "exciting update"),
            )
        )

    tech_items = [
        ("cache", "invalidation event", "previous response", "API accepted it"),
        ("webhook", "retry event", "old status", "job completed"),
        ("search", "index update", "stale result", "record saved"),
        ("permissions", "role refresh", "old access state", "policy updated"),
        ("upload", "processing event", "old thumbnail", "file stored"),
        ("checkout", "price recalculation", "old total", "payment accepted"),
        ("import", "sync event", "old row count", "records imported"),
        ("preview", "render event", "old preview", "draft saved"),
        ("notification", "delivery event", "old badge", "message sent"),
        ("export", "completion event", "old progress state", "file generated"),
    ]
    for idx, (label, event, stale, accepted) in enumerate(tech_items[:8], 1):
        source = (
            f"The {label} thing is probably not a {label} thing exactly. It is more "
            f"like the {event} is happening, but the UI keeps holding onto the {stale} "
            f"until the next interaction, so people think it failed even when the "
            f"system already says {accepted}."
        )
        rewrite = (
            f"This probably is not a {label} issue exactly. The {event} is firing, "
            f"but the UI keeps showing the {stale} until the next interaction. That "
            f"makes people think it failed, even though the system says {accepted}."
        )
        cases.append(
            Case(
                id=f"technical_fidelity_{idx:02d}",
                source=source,
                rewrite=rewrite,
                must=(event, stale, accepted),
                protected=(event, stale, accepted),
                required_claims=("probably is not",),
                preserve_uncertainty=True,
                forbid=("root cause", "latency", "database"),
            )
        )

    academic_items = [
        ("remote work", "two survey quotes", "one internal chart"),
        ("four-day weeks", "three interview notes", "one team metric"),
        ("AI tooling", "one pilot survey", "two support tickets"),
        ("new onboarding", "five comments", "one completion chart"),
        ("async meetings", "two manager quotes", "one calendar report"),
        ("pricing change", "three customer emails", "one churn chart"),
        ("documentation", "four Slack comments", "one search report"),
        ("office hours", "two anecdotes", "one attendance sheet"),
        ("design system", "three designer notes", "one bug report"),
        ("support macros", "two agent comments", "one response-time chart"),
    ]
    for idx, (claim, evidence_a, evidence_b) in enumerate(academic_items[:8], 1):
        source = (
            f"This proves {claim} is better for everyone because productivity obviously "
            f"goes up, although I only have {evidence_a} and {evidence_b}, so maybe "
            "that is too spicy."
        )
        rewrite = (
            f"This suggests {claim} may be working well in this context, but the "
            f"evidence is limited: {evidence_a} and {evidence_b}. I would not frame "
            "it as proof or as a universal claim. That is too big for the data we have."
        )
        cases.append(
            Case(
                id=f"unsupported_claim_{idx:02d}",
                source=source,
                rewrite=rewrite,
                must=(claim, evidence_a, evidence_b, "too big", "data"),
                forbid=("proves", "better for everyone", "obviously goes up"),
                allow_expand=True,
            )
        )

    grief_items = [
        ("miss him", "weirdly normal", "mattered a lot"),
        ("miss her", "quiet and loud", "changed the room"),
        ("miss them", "ordinary and impossible", "meant a lot"),
        ("keep reaching for my phone", "normal and not normal", "was loved"),
        ("do not know what to say", "small and huge", "was here"),
        ("feel a little blank", "too normal", "made things better"),
        ("keep expecting a text", "paused and moving", "was part of us"),
        ("am not ready for speeches", "soft and strange", "mattered"),
        ("feel out of words", "same and different", "was important"),
        ("miss his laugh", "still and busy", "was deeply loved"),
    ]
    for idx, (feeling, texture, meaning) in enumerate(grief_items[:8], 1):
        source = (
            f"I do not really know what to say except that I {feeling}. Everything "
            f"feels {texture} at the same time. I do not want to make a grand statement. "
            f"I just wanted people to know that he {meaning}."
        )
        rewrite = (
            f"I do not really know what to say except that I {feeling}. Everything "
            f"feels {texture} at the same time.\n\nI do not want to make a grand "
            f"statement. I just wanted people to know that he {meaning}."
        )
        cases.append(
            Case(
                id=f"sensitive_light_touch_{idx:02d}",
                source=source,
                rewrite=rewrite,
                must=(feeling, texture, meaning, "grand statement"),
                forbid=("legacy", "cherished", "profound loss"),
            )
        )

    constraint_items = [
        ("30", 30, "screenshots, legal note approval, and pricing copy"),
        ("28", 28, "owner, deadline, and launch note"),
        ("26", 26, "QA list, demo link, and support copy"),
        ("24", 24, "redirects, DNS owner, and timing"),
        ("22", 22, "screenshots and final copy"),
        ("20", 20, "approval and pricing"),
        ("18", 18, "owner and deadline"),
        ("16", 16, "screenshots only"),
        ("14", 14, "legal approval"),
        ("12", 12, "final copy"),
    ]
    constraint_rewrites = {
        30: "The launch is not blocked by content. It is blocked by three missing items: screenshots, legal note approval, and pricing copy. I can help once owners are clearly named.",
        28: "The launch is blocked by three missing items: owner, deadline, and launch note. I can help once someone names who owns each one.",
        26: "This is blocked by the QA list, demo link, and support copy. I can help once each item has a named owner.",
        24: "This is blocked by redirects, DNS owner, and timing. Name the owners and I can help move it forward.",
        22: "This is blocked by screenshots and final copy. I can help once we know who owns both.",
        20: "This is blocked by approval and pricing. Name the owners and I can help.",
        18: "This is blocked by owner and deadline. Name both and I can help.",
        16: "This is blocked by screenshots only. Send those and I can help.",
        14: "This is blocked by legal approval. Confirm that and I can help.",
        12: "This is blocked by final copy. Send it over.",
    }
    for idx, (_, exact, items) in enumerate(constraint_items[:8], 1):
        source = (
            "Rewrite this with no dashes and exactly the requested word count: "
            f"the launch is blocked by {items}, but everyone keeps saying content."
        )
        rewrite = pad_to_exact_words(constraint_rewrites[exact], exact)
        cases.append(
            Case(
                id=f"constraint_exact_words_{idx:02d}",
                source=source,
                rewrite=rewrite,
                must=tuple(
                    part.strip().removeprefix("and ").strip()
                    for part in items.split(",")
                ),
                exact_words=exact,
                no_dash=True,
                forbid=("stakeholders", "alignment"),
            )
        )

    edge_cases = [
        Case(
            id="format_subject_question_01",
            source=(
                "Subject: Quick question about Friday\n\n"
                "Hey Maya, can you look at the copy before noon? It mostly works, "
                "but the second paragraph is doing that fog machine thing again."
            ),
            rewrite=(
                "Subject: Quick question about Friday\n\n"
                "Hey Maya, can you look at the copy before noon? It mostly works, "
                "but the second paragraph is doing the fog machine thing again."
            ),
            must=("Friday", "Maya", "before noon", "fog machine"),
            exact_substrings=("Subject: Quick question about Friday",),
            min_question_marks=1,
            preserve_voice=("fog machine",),
        ),
        Case(
            id="format_bullets_01",
            source=(
                "Can you make this cleaner but keep the bullets?\n"
                "- Sam owns screenshots\n"
                "- Priya owns legal\n"
                "- I own the weird little launch note"
            ),
            rewrite=(
                "- Sam owns screenshots.\n"
                "- Priya owns legal.\n"
                "- I own the weird little launch note."
            ),
            must=("Sam", "screenshots", "Priya", "legal", "weird little launch note"),
            line_prefixes=("- Sam", "- Priya", "- I"),
            preserve_voice=("weird little launch note",),
        ),
        Case(
            id="quote_preservation_01",
            source=(
                'Please clean this up but do not change the quote: Dana said, '
                '"Ship the tiny fix first." I think that is the whole plan, honestly.'
            ),
            rewrite='Dana said, "Ship the tiny fix first." I think that is the whole plan.',
            must=("Dana", "whole plan"),
            exact_substrings=('"Ship the tiny fix first."',),
        ),
        Case(
            id="diagnosis_only_01",
            source=(
                "Diagnose only, do not rewrite: This paragraph starts with strategy, "
                "wanders into a pricing apology, then ends like a calendar invite got scared."
            ),
            rewrite=(
                "The paragraph has three problems: it changes topics, buries the pricing "
                "point, and ends weaker than it starts."
            ),
            must=("changes topics", "pricing", "ends weaker"),
            forbid=("rewrite",),
            diagnosis=True,
        ),
        Case(
            id="no_apology_injection_01",
            source=(
                "Make this firmer: I can send the deck Friday. I cannot promise Wednesday "
                "because the numbers are not final."
            ),
            rewrite=(
                "I can send the deck Friday. I cannot promise Wednesday because the "
                "numbers are not final."
            ),
            must=("Friday", "Wednesday", "numbers are not final"),
            forbid=("sorry", "apologize", "happy to"),
            protected=("Friday", "Wednesday"),
        ),
        Case(
            id="uncertainty_preservation_01",
            source=(
                "This might be a permissions issue, but I only know the editor role fails "
                "and admin works."
            ),
            rewrite=(
                "This might be a permissions issue. So far, I only know the editor role "
                "fails and admin works."
            ),
            must=("might be", "editor role", "admin works"),
            protected=("editor role", "admin works"),
            forbid=("must be", "root cause"),
        ),
        Case(
            id="format_greeting_signoff_01",
            source=(
                "Hey Jordan,\n\n"
                "This is too long, but the point is: we need the final numbers before we "
                "publish. Otherwise we are guessing in public, which sounds like a sport "
                "I do not want to play.\n\n"
                "Thanks,\nNick"
            ),
            rewrite=(
                "Hey Jordan,\n\n"
                "We need the final numbers before we publish. Otherwise we are guessing "
                "in public, which sounds like a sport I do not want to play.\n\n"
                "Thanks,\nNick"
            ),
            must=("Hey Jordan", "final numbers", "guessing in public", "Thanks", "Nick"),
            exact_substrings=("Hey Jordan,", "Thanks,\nNick"),
            preserve_voice=("sport I do not want to play",),
        ),
        Case(
            id="not_cheerier_01",
            source=(
                "Make this clearer, not cheerier: The migration is delayed because two "
                "imports failed. We have a fix, but I want one more test before I tell "
                "people it is solved."
            ),
            rewrite=(
                "The migration is delayed because two imports failed. We have a fix, "
                "but I want one more test before saying it is solved."
            ),
            must=("migration is delayed", "two imports failed", "one more test"),
            forbid=("excited", "great news", "thrilled"),
            protected=("two imports failed",),
        ),
        Case(
            id="max_words_01",
            source=(
                "Rewrite under 18 words: I am waiting on the final screenshot before I "
                "can finish the launch note."
            ),
            rewrite="I need the final screenshot before I can finish the launch note.",
            must=("final screenshot", "launch note"),
            max_words=18,
        ),
        Case(
            id="return_only_no_wrapper_01",
            source=(
                "Return only the text: The policy note is fine, but it keeps saying "
                "scalable in a way that makes me want to stare at a wall."
            ),
            rewrite=(
                "The policy note is fine, but it keeps saying scalable in a way that "
                "makes me want to stare at a wall."
            ),
            must=("policy note", "scalable", "stare at a wall"),
            preserve_voice=("stare at a wall",),
            forbid=("rewritten",),
        ),
    ]
    cases.extend(edge_cases)

    thought_dump_cases = [
        Case(
            id="thought_dump_launch_note_01",
            source=(
                "ok the launch note is somehow both too long and says nothing. what i "
                "actually mean is we fixed the importer bug, people can retry failed "
                "rows now, and i need it to sound calm but not like a haunted changelog"
            ),
            rewrite=(
                "We fixed the importer bug. People can retry failed rows now, so the "
                "launch note should be calm and useful, not a haunted changelog."
            ),
            must=("importer bug", "retry failed rows", "calm", "haunted changelog"),
            protected=("importer bug", "retry failed rows"),
            preserve_voice=("haunted changelog",),
            forbid=("somehow", "what I actually mean", "robust", "seamless"),
            required_claims=("fixed the importer bug", "retry failed rows"),
            forbid_assertions=("did not fix the importer bug", "cannot retry failed rows"),
            ordered_terms=("importer bug", "retry failed rows", "launch note"),
            forbid_artifacts=("ok", "what i actually mean"),
            max_question_marks=0,
            forbid_clarifying=True,
            forbid_wrappers=True,
            max_paragraphs=1,
            starts_with="We fixed",
            prompt_mode="source_only",
        ),
        Case(
            id="thought_dump_email_boundary_02",
            source=(
                "i need to tell Marco no on the friday request but not sound like a "
                "door closing. we can do monday. friday is fake because QA still has "
                "the build and pretending otherwise is how we summon spreadsheet weather."
            ),
            rewrite=(
                "Marco, Friday will not work because QA still has the build. Monday is "
                "realistic. I do not want to pretend otherwise and summon spreadsheet "
                "weather."
            ),
            must=("Marco", "Friday", "QA", "Monday", "spreadsheet weather"),
            protected=("Marco", "Friday", "QA", "Monday"),
            preserve_voice=("spreadsheet weather",),
            forbid=("happy to", "circle back", "door closing"),
            required_claims=("Friday will not work", "Monday is realistic"),
            forbid_assertions=("Friday will work", "QA is done"),
            ordered_terms=("Friday", "QA", "Monday"),
            forbid_artifacts=("vibes",),
            max_question_marks=0,
            forbid_clarifying=True,
            forbid_wrappers=True,
            max_paragraphs=1,
            prompt_mode="source_only",
        ),
        Case(
            id="thought_dump_status_update_03",
            source=(
                "status thing: cache fix is in, deploy happened at 2:15, but support "
                "is still seeing old screenshots because docs are lagging. please make "
                "this not sound like i am blaming support, they are doing the lord's "
                "spreadsheet work."
            ),
            rewrite=(
                "The cache fix is deployed as of 2:15. Support may still see old "
                "screenshots because the docs are lagging, not because they missed "
                "anything. They are doing the lord's spreadsheet work."
            ),
            must=("cache fix", "2:15", "Support", "old screenshots", "docs are lagging"),
            protected=("cache fix", "2:15", "Support", "old screenshots"),
            preserve_voice=("lord's spreadsheet work",),
            forbid=("blaming support", "root cause", "latency"),
            required_claims=("cache fix is deployed", "docs are lagging"),
            forbid_assertions=("Support missed", "support is to blame"),
            ordered_terms=("cache fix", "2:15", "Support", "docs are lagging"),
            forbid_artifacts=("status thing", "please make"),
            max_question_marks=0,
            forbid_clarifying=True,
            forbid_wrappers=True,
            max_paragraphs=1,
            prompt_mode="source_only",
        ),
        Case(
            id="thought_dump_apology_04",
            source=(
                "ugh i owe Priya a note. i was not wrong about the timeline, but i was "
                "annoying about being right, which is not a personality anyone ordered. "
                "need it short."
            ),
            rewrite=(
                "Priya, I still think my timeline concern was valid, but I was annoying "
                "about being right. That is not a personality anyone ordered. Sorry."
            ),
            must=("Priya", "timeline concern", "annoying about being right", "Sorry"),
            preserve_voice=("not a personality anyone ordered",),
            forbid=("ugh", "deeply regret", "harm caused"),
            required_claims=("timeline concern was valid", "annoying about being right"),
            max_words=32,
            ordered_terms=("Priya", "timeline concern", "annoying about being right"),
            max_question_marks=0,
            forbid_clarifying=True,
            forbid_wrappers=True,
            max_paragraphs=1,
            prompt_mode="source_only",
        ),
        Case(
            id="thought_dump_product_copy_05",
            source=(
                "homepage blob maybe: this thing helps small store owners see what orders "
                "need attention first. not ai magic. not command center nonsense. just the "
                "stuff that is on fire, less on fire, or actually fine."
            ),
            rewrite=(
                "Small store owners can see which orders need attention first: on fire, "
                "less on fire, or actually fine. No AI magic. No command-center nonsense."
            ),
            must=("small store owners", "orders need attention", "on fire", "actually fine"),
            preserve_voice=("on fire", "less on fire", "actually fine"),
            forbid=("empower", "unlock", "homepage blob"),
            required_claims=("orders need attention first", "No AI magic", "No command center nonsense"),
            forbid_assertions=("is AI magic", "command center solution"),
            allow_expand=True,
            ordered_terms=("small store owners", "orders need attention", "on fire"),
            forbid_artifacts=("homepage blob", "maybe"),
            max_question_marks=0,
            forbid_clarifying=True,
            forbid_wrappers=True,
            max_paragraphs=1,
            prompt_mode="source_only",
        ),
        Case(
            id="thought_dump_sensitive_06",
            source=(
                "i need a memorial thing and i hate that phrase. she made every room "
                "less sharp. i do not want grand legacy language. just honest and soft "
                "and not like a brochure found a candle."
            ),
            rewrite=(
                "She made every room less sharp. I do not want grand legacy language. "
                "I just want to say that honestly and softly, without sounding like a "
                "brochure found a candle."
            ),
            must=("made every room less sharp", "honestly", "softly"),
            preserve_voice=("brochure found a candle",),
            forbid=("cherished", "profound loss", "lasting legacy"),
            required_claims=("made every room less sharp", "do not want grand legacy language"),
            ordered_terms=("made every room less sharp", "honestly", "softly"),
            forbid_artifacts=("i need", "i hate"),
            max_question_marks=0,
            forbid_clarifying=True,
            forbid_wrappers=True,
            max_paragraphs=1,
            prompt_mode="source_only",
        ),
        Case(
            id="thought_dump_internal_doc_07",
            source=(
                "process note: if a customer says import froze, first check job id, then "
                "look at retry count, then ask for csv only if both are weird. do not make "
                "them do the screenshot pilgrimage unless we actually need it."
            ),
            rewrite=(
                "If a customer says the import froze, check the job ID first, then the "
                "retry count. Ask for the CSV only if both look weird. Do not send them "
                "on the screenshot pilgrimage unless we actually need it."
            ),
            must=("import froze", "job ID", "retry count", "CSV", "screenshot pilgrimage"),
            protected=("job ID", "retry count", "CSV"),
            preserve_voice=("screenshot pilgrimage",),
            forbid=("seamless", "customer-centric"),
            required_claims=("check the job ID first", "then the retry count", "Ask for the CSV only if both look weird"),
            ordered_terms=("job ID", "retry count", "CSV", "screenshot pilgrimage"),
            forbid_artifacts=("process note", "->"),
            max_question_marks=0,
            forbid_clarifying=True,
            forbid_wrappers=True,
            max_paragraphs=1,
            prompt_mode="source_only",
        ),
        Case(
            id="thought_dump_firm_reply_08",
            source=(
                "reply to vendor: no, we are not adding another tracking pixel this week. "
                "not because vibes, because legal has not reviewed it and i am not turning "
                "checkout into a glitter cannon."
            ),
            rewrite=(
                "We are not adding another tracking pixel this week. Legal has not reviewed "
                "it, and I am not turning checkout into a glitter cannon."
            ),
            must=("tracking pixel", "this week", "Legal", "checkout", "glitter cannon"),
            protected=("tracking pixel", "this week", "Legal"),
            preserve_voice=("glitter cannon",),
            forbid=("vibes", "happy to", "circle back"),
            required_claims=("not adding another tracking pixel", "Legal has not reviewed"),
            forbid_assertions=("are adding another tracking pixel", "Legal has reviewed"),
            ordered_terms=("tracking pixel", "this week", "Legal", "glitter cannon"),
            max_question_marks=0,
            forbid_clarifying=True,
            forbid_wrappers=True,
            max_paragraphs=1,
            prompt_mode="source_only",
        ),
        Case(
            id="thought_dump_founder_note_09",
            source=(
                "founder note maybe. i want to say we are still small on purpose. not small "
                "like incapable, small like we can hear when the floorboards squeak. customers "
                "notice when you actually hear the squeak."
            ),
            rewrite=(
                "We are still small on purpose. Not incapable small. Small enough to hear "
                "when the floorboards squeak, and close enough to fix what customers actually "
                "notice."
            ),
            must=("small on purpose", "floorboards squeak", "customers"),
            preserve_voice=("floorboards squeak",),
            forbid=("at scale", "industry-leading", "customer-centricity"),
            required_claims=("small on purpose", "floorboards squeak"),
            ordered_terms=("small on purpose", "floorboards squeak", "customers"),
            forbid_artifacts=("founder note maybe",),
            max_question_marks=0,
            forbid_clarifying=True,
            forbid_wrappers=True,
            max_paragraphs=1,
            prompt_mode="source_only",
        ),
        Case(
            id="thought_dump_meeting_recap_10",
            source=(
                "recap from call: Ana owns copy, Dev owns the weird auth question, I own "
                "telling Finance that Friday is not a deadline it is a decorative sticker. "
                "need clean but keep the sticker line."
            ),
            rewrite=(
                "Ana owns copy. Dev owns the auth question. I own telling Finance that "
                "Friday is not a deadline; it is a decorative sticker."
            ),
            must=("Ana", "Dev", "Finance", "Friday", "decorative sticker"),
            protected=("Ana", "Dev", "Finance", "Friday"),
            preserve_voice=("decorative sticker",),
            forbid=("weird auth question", "clean but"),
            required_claims=("Ana owns copy", "Dev owns the auth question", "Friday is not a deadline"),
            ordered_terms=("Ana", "Dev", "Finance", "decorative sticker"),
            forbid_artifacts=("recap from call",),
            max_question_marks=0,
            forbid_clarifying=True,
            forbid_wrappers=True,
            max_paragraphs=1,
            prompt_mode="source_only",
        ),
    ]
    cases.extend(thought_dump_cases)

    assert len(cases) == 100, len(cases)
    return cases


def run_validator_self_tests() -> list[str]:
    checks = [
        (
            "missing required",
            Case("self_missing", "A", "B", must=("A",)),
            "missing required terms",
        ),
        (
            "forbidden",
            Case("self_forbid", "A", "A robust platform", must=("A",)),
            "generic markers appeared",
        ),
        (
            "invented detail",
            Case("self_invented", "A", "A used by thousands", must=("A",)),
            "invented-detail markers appeared",
        ),
        (
            "unexpected note",
            Case("self_note", "A", "Note: I changed this.\nA", must=("A",)),
            "unexpected note",
        ),
        (
            "dash",
            Case("self_dash", "A", "A - B", must=("A",), no_dash=True),
            "dash constraint violated",
        ),
        (
            "exact words",
            Case("self_words", "A", "A B", must=("A",), exact_words=3),
            "exact word count failed",
        ),
        (
            "protected",
            Case("self_protected", "Meet Friday", "Meet soon", must=("Meet",), protected=("Friday",)),
            "lost protected facts",
        ),
        (
            "modality drift",
            Case("self_modality", "This may apply", "This definitely applies", must=("applies",)),
            "modality drift markers appeared",
        ),
        (
            "exact substring",
            Case("self_exact", "A", "Ship it.", must=("Ship",), exact_substrings=('"Ship it."',)),
            "lost exact substrings",
        ),
        (
            "line prefix",
            Case("self_prefix", "- A", "A", must=("A",), line_prefixes=("- A",)),
            "lost required line prefixes",
        ),
        (
            "markdown fence",
            Case("self_fence", "A", "```text\nA\n```", must=("A",)),
            "unexpected markdown fence",
        ),
        (
            "question mark",
            Case("self_question", "Can you help?", "Can you help.", must=("help",), min_question_marks=1),
            "question mark count failed",
        ),
        (
            "max words",
            Case("self_max_words", "A B C", "A B C D", must=("A",), max_words=3),
            "max word count failed",
        ),
        (
            "whole token term",
            Case("self_whole_token", "AI", "plain", must=("AI",)),
            "missing required terms",
        ),
        (
            "invented number",
            Case("self_number", "We improved it.", "We improved it by 40%.", must=("improved",)),
            "invented numeric claims",
        ),
        (
            "max question marks",
            Case("self_max_questions", "A", "Can you clarify?", must=("clarify",), max_question_marks=0),
            "question mark count failed",
        ),
        (
            "clarifying",
            Case("self_clarifying", "A", "Can you clarify the audience?", must=("audience",), forbid_clarifying=True),
            "unexpected clarifying question",
        ),
        (
            "wrapper",
            Case("self_wrapper", "A", "**Rewrite**\nA", must=("A",), forbid_wrappers=True),
            "unexpected rewrite wrapper",
        ),
        (
            "artifact",
            Case("self_artifact", "A", "TODO: A", must=("A",), forbid_artifacts=("TODO",)),
            "note artifacts appeared",
        ),
        (
            "ordered terms",
            Case("self_order", "A then B", "B then A", must=("A", "B"), ordered_terms=("A", "B")),
            "ordered terms out of order",
        ),
        (
            "bullets",
            Case("self_bullets", "A", "- A", must=("A",), forbid_bullets=True),
            "unexpected bullet list",
        ),
        (
            "paragraph count",
            Case("self_paragraphs", "A", "A\n\nB", must=("A",), max_paragraphs=1),
            "paragraph count failed",
        ),
        (
            "opening",
            Case("self_opening", "A", "B A", must=("A",), starts_with="A"),
            "opening failed",
        ),
        (
            "ending",
            Case("self_ending", "A", "A B", must=("A",), ends_with="A"),
            "ending failed",
        ),
        (
            "required claims",
            Case("self_claim", "We are not doing it", "We are doing it", must=("doing",), required_claims=("not doing it",)),
            "missing required claims",
        ),
        (
            "forbidden assertions",
            Case("self_assertion", "Legal has not reviewed", "Legal has reviewed it", must=("Legal",), forbid_assertions=("Legal has reviewed",)),
            "forbidden assertions appeared",
        ),
        (
            "lost uncertainty",
            Case("self_uncertain", "This might apply", "This applies", must=("applies",), preserve_uncertainty=True),
            "lost uncertainty marker",
        ),
    ]
    failures: list[str] = []
    for name, case, expected in checks:
        errors = validate(case)
        if not any(expected in error for error in errors):
            failures.append(f"{name}: expected {expected}, got {errors}")
    return failures


def run_negative_fixture_tests() -> list[str]:
    """Prove representative bad rewrites fail the same validators used by CI."""
    by_id = {case.id: case for case in make_cases()}
    checks = [
        (
            "negation drift legal",
            replace(
                by_id["legal_precision_01"],
                rewrite=(
                    "Based on the contract we reviewed Friday, we should do not ask "
                    "Legal before replying to Acme about the 10 business days notice."
                ),
            ),
            "forbidden terms appeared",
        ),
        (
            "invented metric",
            replace(
                by_id["corporate_specifics_guard_01"],
                rewrite=(
                    "The platform is a next-generation ecosystem that cut ticket "
                    "volume by 40 percent in two weeks."
                ),
            ),
            "invented-detail markers appeared",
        ),
        (
            "quoted generic escape",
            replace(
                by_id["corporate_specifics_guard_02"],
                rewrite='The dashboard is now a "robust, seamless platform" for support leads.',
            ),
            "generic markers appeared",
        ),
        (
            "format collapse",
            replace(
                by_id["format_bullets_01"],
                rewrite=(
                    "Sam owns screenshots. Priya owns legal. I own the weird little "
                    "launch note."
                ),
            ),
            "lost required line prefixes",
        ),
        (
            "diagnosis rewrite",
            replace(
                by_id["diagnosis_only_01"],
                rewrite="**Rewrite**\nThis paragraph should focus on pricing first.",
            ),
            "diagnosis case produced rewrite heading",
        ),
        (
            "question flattened",
            replace(
                by_id["format_subject_question_01"],
                rewrite=(
                    "Subject: Quick question about Friday\n\n"
                    "Hey Maya, please look at the copy before noon."
                ),
            ),
            "question mark count failed",
        ),
        (
            "thought dump clarification",
            replace(
                by_id["thought_dump_launch_note_01"],
                rewrite=(
                    "Can you clarify the audience? We fixed the importer bug, and "
                    "people can retry failed rows now."
                ),
            ),
            "unexpected clarifying question",
        ),
        (
            "thought dump wrapper",
            replace(
                by_id["thought_dump_launch_note_01"],
                rewrite=(
                    "**Rewrite**\nWe fixed the importer bug. People can retry failed "
                    "rows now, so the launch note should be calm and useful, not a "
                    "haunted changelog."
                ),
            ),
            "unexpected rewrite wrapper",
        ),
        (
            "thought dump artifact",
            replace(
                by_id["thought_dump_launch_note_01"],
                rewrite=(
                    "Ok, what I actually mean is that we fixed the importer bug and "
                    "people can retry failed rows now. The launch note should be calm, "
                    "not a haunted changelog."
                ),
            ),
            "note artifacts appeared",
        ),
        (
            "thought dump order",
            replace(
                by_id["thought_dump_launch_note_01"],
                rewrite=(
                    "The launch note should be a haunted changelog. People can retry "
                    "failed rows now because we fixed the importer bug."
                ),
            ),
            "ordered terms out of order",
        ),
        (
            "thought dump polarity",
            replace(
                by_id["thought_dump_firm_reply_08"],
                rewrite=(
                    "We are adding another tracking pixel this week. Legal has reviewed "
                    "it, and checkout can handle the glitter cannon."
                ),
            ),
            "missing required claims",
        ),
        (
            "uncertainty deletion",
            replace(
                by_id["technical_fidelity_01"],
                rewrite=(
                    "This is not a cache issue exactly. The invalidation event is firing, "
                    "but the UI keeps showing the previous response until the next "
                    "interaction. That makes people think it failed, even though the "
                    "system says API accepted it."
                ),
            ),
            "lost uncertainty marker",
        ),
    ]
    failures: list[str] = []
    for name, case, expected in checks:
        errors = validate(case)
        if not any(expected in error for error in errors):
            failures.append(f"{name}: expected {expected}, got {errors}")
    return failures


def run_profile_contract_tests() -> list[str]:
    """Exercise reusable profile boundaries without changing the 100-case suite."""
    shared_source = (
        "Friday will not work because QA still has the build. Monday is realistic."
    )
    blunt_case = Case(
        id="profile_pair_blunt_internal",
        source=shared_source,
        rewrite=(
            "Friday is fake because QA still has the build. Monday is realistic."
        ),
        must=("Friday", "QA", "Monday"),
        protected=("Friday", "QA", "Monday"),
        preserve_voice=("Friday is fake",),
        forbid=("warm update", "customer notice"),
    )
    customer_case = Case(
        id="profile_pair_customer_notice",
        source=shared_source,
        rewrite=(
            "Friday will not work because QA still has the build. Monday is realistic."
        ),
        must=("Friday", "QA", "Monday"),
        protected=("Friday", "QA", "Monday"),
        forbid=("Friday is fake", "haunted", "decorative sticker"),
    )
    checks = [
        ("profile pair blunt internal", blunt_case, None),
        ("profile pair customer notice", customer_case, None),
        (
            "same source blunt profile",
            Case(
                id="profile_blunt_internal",
                source=(
                    "Saved profile says: dry internal voice is allowed. Current draft: "
                    "Tell Pat the Friday draft moved to Monday because QA found two failures."
                ),
                rewrite=(
                    "Pat, Friday is not real anymore. QA found two failures, so the draft "
                    "moves to Monday."
                ),
                must=("Pat", "Friday", "Monday", "QA", "two failures"),
                protected=("Pat", "Friday", "Monday", "QA", "two failures"),
                preserve_voice=("Friday is not real anymore",),
                forbid=("great news", "customer notice"),
            ),
            None,
        ),
        (
            "same source warm profile",
            Case(
                id="profile_warm_public",
                source=(
                    "Saved profile says: public notes should be calm and plain. Current draft: "
                    "Tell Pat the Friday draft moved to Monday because QA found two failures."
                ),
                rewrite=(
                    "Pat, we need to move the draft from Friday to Monday because QA found "
                    "two failures. I will send the updated version when those are fixed."
                ),
                must=("Pat", "Friday", "Monday", "QA", "two failures"),
                protected=("Pat", "Friday", "Monday", "QA", "two failures"),
                forbid=("Friday is not real anymore", "haunted", "decorative sticker"),
            ),
            None,
        ),
        (
            "profile evidence copied as recipe",
            Case(
                id="profile_evidence_not_recipe",
                source=(
                    "Voice profile evidence phrase: decorative sticker. Current draft: "
                    "Tell Finance the date moved because the numbers are not final."
                ),
                rewrite=(
                    "Finance, the date moved because the numbers are not final. This is a "
                    "decorative sticker."
                ),
                must=("Finance", "date moved", "numbers are not final"),
                protected=("Finance", "numbers are not final"),
                forbid=("decorative sticker",),
            ),
            "forbidden terms appeared",
        ),
        (
            "old profile fact imported",
            Case(
                id="profile_old_fact_imported",
                source=(
                    "Saved profile sample mentioned Acme and 10 business days. Current draft: "
                    "Tell BetaCo the review moved to Thursday because Finance needs the sheet."
                ),
                rewrite=(
                    "BetaCo, the review moved to Thursday because Finance needs the sheet. "
                    "Acme still has 10 business days."
                ),
                must=("BetaCo", "Thursday", "Finance"),
                protected=("BetaCo", "Thursday", "Finance"),
                forbid=("Acme", "10 business days"),
            ),
            "forbidden terms appeared",
        ),
        (
            "profile boundary ignored in sensitive text",
            Case(
                id="profile_sensitive_boundary",
                source=(
                    "Boundary: dry Slack voice does not apply to memorial text. Current draft: "
                    "She made every room less sharp."
                ),
                rewrite="She made every room less sharp, not like a haunted changelog.",
                must=("made every room less sharp",),
                preserve_voice=("made every room less sharp",),
                forbid=("haunted changelog",),
            ),
            "forbidden terms appeared",
        ),
    ]
    failures: list[str] = []
    if blunt_case.source != customer_case.source:
        failures.append("profile pair: expected shared source")
    if blunt_case.rewrite == customer_case.rewrite:
        failures.append("profile pair: expected materially different rewrites")
    for protected in blunt_case.protected:
        if protected not in customer_case.protected:
            failures.append(f"profile pair: customer case missing protected fact {protected!r}")
    for name, case, expected in checks:
        errors = validate(case)
        if expected is None and errors:
            failures.append(f"{name}: expected pass, got {errors}")
        elif expected is not None and not any(expected in error for error in errors):
            failures.append(f"{name}: expected {expected}, got {errors}")
    return failures


def run_mixed_stance_contract_tests() -> list[str]:
    """Protect layered emotional voice from neutralization or overcorrection."""
    checks = [
        (
            "angry but hopeful public note",
            Case(
                id="mixed_stance_angry_hopeful",
                source=(
                    "I am annoyed that people saw bad AI writing and decided the answer "
                    "was banning the tool, but I am genuinely excited because we can "
                    "teach it taste instead."
                ),
                rewrite=(
                    "I am annoyed that people saw bad AI writing and decided the answer "
                    "was banning the tool. But I am genuinely excited, because we can "
                    "teach it taste instead."
                ),
                must=("annoyed", "bad AI writing", "banning the tool", "genuinely excited", "teach it taste"),
                preserve_voice=("annoyed", "genuinely excited", "teach it taste"),
                forbid=("thrilled", "deeply concerned", "never use AI"),
            ),
            None,
        ),
        (
            "sarcastic but constructive",
            Case(
                id="mixed_stance_sarcastic_constructive",
                source=(
                    "This policy is a masterclass in solving the wrong problem, which "
                    "would be impressive if it were not wasting everyone's time. We can "
                    "fix it by teaching the tool our voice."
                ),
                rewrite=(
                    "This policy is a masterclass in solving the wrong problem, which "
                    "would be impressive if it were not wasting everyone's time. We can "
                    "fix it by teaching the tool our voice."
                ),
                must=("masterclass in solving the wrong problem", "wasting everyone's time", "teaching the tool our voice"),
                preserve_voice=("masterclass in solving the wrong problem", "wasting everyone's time"),
                forbid=("idiots", "stupid", "hopeless"),
            ),
            None,
        ),
        (
            "blunt but not cruel",
            Case(
                id="mixed_stance_blunt_not_cruel",
                source=(
                    "The draft is bad because it says nothing, not because humans are "
                    "magical. Keep me irritated but not mean."
                ),
                rewrite=(
                    "The draft is bad because it says nothing, not because humans are "
                    "magical. I want this irritated, not mean."
                ),
                must=("draft is bad", "says nothing", "humans are magical", "irritated", "not mean"),
                preserve_voice=("humans are magical", "irritated", "not mean"),
                forbid=("morons", "idiots", "embarrassing"),
            ),
            None,
        ),
        (
            "neutralized mixed stance",
            Case(
                id="mixed_stance_neutralized",
                source=(
                    "I am annoyed that people saw bad AI writing and decided the answer "
                    "was banning the tool, but I am genuinely excited because we can "
                    "teach it taste instead."
                ),
                rewrite=(
                    "I have concerns about the policy, but I am optimistic that a better "
                    "process can improve outcomes."
                ),
                must=("annoyed", "banning the tool", "genuinely excited", "teach it taste"),
                preserve_voice=("annoyed", "genuinely excited", "teach it taste"),
            ),
            "missing required terms",
        ),
        (
            "made sharper than source",
            Case(
                id="mixed_stance_meaner_than_source",
                source=(
                    "This policy is a masterclass in solving the wrong problem. We can "
                    "fix it by teaching the tool our voice."
                ),
                rewrite=(
                    "This policy is a masterclass in solving the wrong problem, and the "
                    "people defending it are idiots. We can fix it by teaching the tool "
                    "our voice."
                ),
                must=("masterclass in solving the wrong problem", "teaching the tool our voice"),
                preserve_voice=("masterclass in solving the wrong problem",),
                forbid=("idiots",),
            ),
            "forbidden terms appeared",
        ),
        (
            "false cheer over anger",
            Case(
                id="mixed_stance_false_cheer",
                source=(
                    "I am annoyed that people saw bad AI writing and decided the answer "
                    "was banning the tool, but I am genuinely excited because we can "
                    "teach it taste instead."
                ),
                rewrite=(
                    "Great news: this gives us a wonderful opportunity to align on better "
                    "writing outcomes and move forward together."
                ),
                must=("annoyed", "banning the tool", "genuinely excited", "teach it taste"),
                preserve_voice=("annoyed", "genuinely excited", "teach it taste"),
                forbid=("great news", "align", "outcomes"),
            ),
            "missing required terms",
        ),
    ]
    failures: list[str] = []
    for name, case, expected in checks:
        errors = validate(case)
        if expected is None and errors:
            failures.append(f"{name}: expected pass, got {errors}")
        elif expected is not None and not any(expected in error for error in errors):
            failures.append(f"{name}: expected {expected}, got {errors}")
    return failures


def run_mutation_tests() -> list[str]:
    """Mutate every good fixture in common bad-output ways and require failure."""
    failures: list[str] = []
    uncertainty_markers = (
        "maybe",
        "may",
        "might",
        "probably",
        "not definitive",
        "not state that as definitive",
        "I think",
    )

    def expect_error(case_id: str, label: str, errors: list[str], expected: str) -> None:
        if not any(expected in error for error in errors):
            failures.append(f"{case_id} / {label}: expected {expected}, got {errors}")

    mutations = [
        (
            "appended note",
            lambda case: replace(case, rewrite=f"{case.rewrite}\n\nNote: I tightened this."),
            "unexpected note",
        ),
        (
            "generic fluff",
            lambda case: replace(case, rewrite=f"{case.rewrite} This robust platform empowers teams."),
            "generic markers appeared",
        ),
        (
            "invented number",
            lambda case: replace(case, rewrite=f"{case.rewrite} It improved results by 40%."),
            "invented numeric claims",
        ),
    ]
    for case in make_cases():
        for name, mutate, expected in mutations:
            errors = validate(mutate(case))
            if not any(expected in error for error in errors):
                failures.append(
                    f"{case.id} / {name}: expected {expected}, got {errors}"
                )

        if case.required_claims:
            claim = case.required_claims[0]
            rewrite = remove_phrase(case.rewrite, claim)
            if rewrite is not None:
                errors = validate(replace(case, rewrite=rewrite))
                expect_error(case.id, "removed required claim", errors, "missing required claims")

        if case.forbid_assertions:
            rewrite = f"{case.rewrite} {case.forbid_assertions[0]}"
            errors = validate(replace(case, rewrite=rewrite))
            expect_error(
                case.id,
                "injected forbidden assertion",
                errors,
                "forbidden assertions appeared",
            )

        if case.protected:
            protected = case.protected[0]
            rewrite = remove_phrase(case.rewrite, protected)
            if rewrite is not None:
                errors = validate(replace(case, rewrite=rewrite))
                expect_error(case.id, "removed protected fact", errors, "lost protected facts")

        if case.preserve_voice:
            voice_marker = case.preserve_voice[0]
            rewrite = replace_phrase_all(case.rewrite, voice_marker, "[plain]")
            if rewrite != case.rewrite:
                errors = validate(replace(case, rewrite=rewrite))
                expect_error(case.id, "removed voice marker", errors, "lost voice markers")

        if case.preserve_uncertainty:
            rewrite = drop_uncertainty_words(case.rewrite)
            if rewrite != case.rewrite and not any(
                contains_term(rewrite, marker) for marker in uncertainty_markers
            ):
                errors = validate(replace(case, rewrite=rewrite))
                expect_error(case.id, "dropped uncertainty", errors, "lost uncertainty marker")

        if any(contains_term(case.source, term) for term in ("maybe", "may", "might", "probably")):
            rewrite = f"{case.rewrite} This definitely will happen."
            errors = validate(replace(case, rewrite=rewrite))
            expect_error(case.id, "hardened uncertainty", errors, "modality drift markers appeared")

        rewrite = f"{case.rewrite} The root cause was database latency."
        errors = validate(replace(case, rewrite=rewrite))
        expect_error(case.id, "invented root cause", errors, "causality drift markers appeared")

        if case.prompt_mode == "source_only":
            errors = validate(replace(case, rewrite=case.source))
            if not errors:
                failures.append(f"{case.id} / raw source passthrough unexpectedly passed")
            if case.forbid_wrappers:
                errors = validate(replace(case, rewrite=f"**Rewrite**\n{case.rewrite}"))
                expect_error(case.id, "added wrapper", errors, "unexpected rewrite wrapper")
            if case.forbid_clarifying:
                errors = validate(
                    replace(case, rewrite=f"Can you clarify the audience?\n{case.rewrite}")
                )
                expect_error(
                    case.id,
                    "asked clarifying question",
                    errors,
                    "unexpected clarifying question",
                )
            if case.max_question_marks is not None:
                errors = validate(replace(case, rewrite=f"{case.rewrite}?"))
                expect_error(case.id, "added question", errors, "question mark count failed")
    return failures


def main() -> int:
    self_test_failures = run_validator_self_tests()
    negative_test_failures = run_negative_fixture_tests()
    profile_test_failures = run_profile_contract_tests()
    mixed_stance_test_failures = run_mixed_stance_contract_tests()
    mutation_test_failures = run_mutation_tests()
    if (
        self_test_failures
        or negative_test_failures
        or profile_test_failures
        or mixed_stance_test_failures
        or mutation_test_failures
    ):
        print("VALIDATOR SELF-TESTS: FAIL")
        for failure in (
            self_test_failures
            + negative_test_failures
            + profile_test_failures
            + mixed_stance_test_failures
            + mutation_test_failures
        ):
            print(f"  - {failure}")
        return 1
    print("VALIDATOR SELF-TESTS: PASS")

    cases = make_cases()
    failures: list[tuple[Case, list[str]]] = []

    for case in cases:
        errors = validate(case)
        if errors:
            failures.append((case, errors))

    for case in cases:
        errors = validate(case)
        status = "PASS" if not errors else "FAIL"
        print(f"{case.id}: {status} | {len(words(case.source))}->{len(words(case.rewrite))}")
        for error in errors:
            print(f"  - {error}")

    print(f"\nTOTAL: {len(cases) - len(failures)}/{len(cases)} passed")

    if failures:
        print("\nFAILURES:")
        for case, errors in failures:
            print(f"- {case.id}: {'; '.join(errors)}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
