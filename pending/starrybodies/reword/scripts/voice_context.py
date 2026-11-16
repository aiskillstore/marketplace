"""Destination and author style cards. Standard library only; never edits or saves text."""

from __future__ import annotations

from collections.abc import Mapping
from functools import lru_cache
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent.parent
DESTINATIONS = ("text-message", "chat", "email", "linkedin", "cover-letter", "essay", "web-copy", "general")
STYLE_CHOICES = {
    "case": ("preserve", "sentence", "lowercase"),
    "punctuation": ("preserve", "standard", "light"),
    "spelling": ("preserve", "standard", "sampled-colloquial"),
    "regional_spelling": ("preserve", "US", "UK", "CA"),
    "abbreviations": ("preserve", "familiar", "avoid"),
    "contractions": ("preserve", "natural", "avoid"),
}
TRAIT_FIELDS = ("vocabulary", "rhythm", "openings", "transitions", "emotional_register", "devices")
_ALIASES = {
    "text": "text-message", "sms": "text-message", "text-messages": "text-message",
    "messaging": "chat", "instant-message": "chat", "dm": "chat",
    "e-mail": "email", "linkedin-post": "linkedin", "coverletter": "cover-letter",
    "website-copy": "web-copy", "website": "web-copy", "webpage": "web-copy",
}
_SIGNALS = {
    "text-message": r"\b(?:text[ -]messages?|sms|imessage)\b",
    "chat": r"\b(?:chat|slack|discord|instant[ -]messag(?:e|ing)|direct[ -]message|dm)\b",
    "email": r"\be[ -]?mail\b",
    "linkedin": r"\blinkedin\b",
    "cover-letter": r"\bcover[ -]?letter\b",
    "essay": r"\bessay\b",
    "web-copy": r"\b(?:web[ -]copy|website[ -]copy|landing[ -]page|webpage)\b",
}


def _style_values(values: Mapping) -> dict:
    if not isinstance(values, Mapping) or any(key not in STYLE_CHOICES for key in values):
        raise ValueError("Style preferences accept only " + ", ".join(STYLE_CHOICES) + ".")
    checked = {}
    for key, value in values.items():
        if not isinstance(value, str) or value not in STYLE_CHOICES[key]:
            raise ValueError(f"{key} must be one of: {', '.join(STYLE_CHOICES[key])}.")
        checked[key] = value
    return checked


def validate_context_preferences(mapping: Mapping) -> dict:
    """Validate profile.contexts and return a fresh, bounded canonical mapping."""
    if not isinstance(mapping, Mapping) or any(key not in DESTINATIONS for key in mapping):
        raise ValueError("contexts must map canonical destination names to style preference objects.")
    return {key: _style_values(value) for key, value in mapping.items()}


def validate_voice_traits(mapping: Mapping) -> dict:
    """Validate optional profile.traits without interpreting it as factual material."""
    if not isinstance(mapping, Mapping) or any(key not in TRAIT_FIELDS for key in mapping):
        raise ValueError("traits accepts only " + ", ".join(TRAIT_FIELDS) + ".")
    if any(not isinstance(value, str) or not value.strip() or len(value) > 120 for value in mapping.values()):
        raise ValueError("Each voice trait must be a nonempty string of at most 120 characters.")
    return {key: value.strip() for key, value in mapping.items()}


@lru_cache(maxsize=1)
def _destinations() -> dict:
    data = json.loads((ROOT / "assets/destinations.json").read_text(encoding="utf-8"))
    if data.get("schema_version") != 1 or set(data.get("destinations", {})) != set(DESTINATIONS):
        raise ValueError("Unsupported destination policy schema.")
    result = data["destinations"]
    for value in result.values():
        if not isinstance(value.get("label"), str) or not isinstance(value.get("guidance"), str):
            raise ValueError("Destination labels and guidance must be strings.")
        if set(_style_values(value.get("style"))) != set(STYLE_CHOICES):
            raise ValueError("Destination defaults must specify every style preference.")
    return result


def _canonical(destination: str) -> str:
    normalized = re.sub(r"[\s_]+", "-", destination.strip().casefold())
    return _ALIASES.get(normalized, normalized)


def _infer(text: str, audience: str, purpose: str, context: str) -> tuple[str, str, str]:
    # Metadata names a destination; source topics and informal wording do not.
    metadata = "\n".join((audience, purpose, context))
    matches = set()
    for key, pattern in _SIGNALS.items():
        for match in re.finditer(pattern, metadata, re.I):
            clause = re.split(r"[\n.;:!?]", metadata[:match.start()])[-1][-40:]
            if not re.search(r"\b(?:not|never|avoid|without|isn['\u2019]t|don['\u2019]t|rather than)\b", clause, re.I):
                matches.add(key)
    if len(matches) == 1:
        return matches.pop(), "high", "One destination is named in task context."
    if len(matches) > 1:
        return "general", "low", "Task context names multiple destinations."
    if re.search(r"(?mi)^Subject:\s*\S", text) and re.search(r"(?mi)^(?:To|From):\s*\S", text):
        return "email", "high", "Source contains email headers."
    return "general", "low", "No unambiguous destination; preserve the source register."


def resolve_context(destination: str = "auto", *, text: str = "", audience: str = "", purpose: str = "",
                    context: str = "", preferences: Mapping | None = None) -> dict:
    """Resolve a destination and policy; do not transform prose or persist preferences.

    ``preferences`` accepts profile.contexts, a flat override map, or both together.
    Precedence: destination defaults < contexts.general < selected context < flat
    per-call overrides. Explicit destination always defeats automatic inference.
    """
    if not all(isinstance(value, str) for value in (destination, text, audience, purpose, context)):
        raise ValueError("Destination, source text and task context must be strings.")
    if preferences is None:
        preferences = {}
    if not isinstance(preferences, Mapping):
        raise ValueError("Context preferences must be an object.")
    contexts = validate_context_preferences({key: value for key, value in preferences.items() if key not in STYLE_CHOICES})
    overrides = _style_values({key: value for key, value in preferences.items() if key in STYLE_CHOICES})
    requested = _canonical(destination)
    if requested == "auto":
        selected, confidence, reason = _infer(text, audience, purpose, context)
        source = "inferred" if confidence == "high" else "fallback"
    elif requested in DESTINATIONS:
        selected, source, confidence, reason = requested, "explicit", "explicit", "Explicit destination."
    else:
        selected, source, confidence, reason = "general", "fallback", "low", "Unknown destination; use general."
    policy = _destinations()[selected]
    style = {**policy["style"], **contexts.get("general", {}), **contexts.get(selected, {}), **overrides}
    return {"destination": selected, "style": style, "source": source, "confidence": confidence,
            "reason": reason, "guidance": policy["guidance"]}


def render_style_card(resolved: Mapping) -> str:
    """Render model-facing guidance, never a mechanical capitalization filter."""
    if not isinstance(resolved, Mapping) or resolved.get("destination") not in DESTINATIONS:
        raise ValueError("Render a resolved destination context.")
    style = _style_values(resolved.get("style"))
    if set(style) != set(STYLE_CHOICES):
        raise ValueError("A resolved style must contain every style preference.")
    labels = {
        "case": {"preserve": "author's case", "sentence": "appropriate capitalization", "lowercase": "natural lowercase"},
        "punctuation": {"preserve": "author's punctuation", "standard": "standard punctuation", "light": "light punctuation"},
        "spelling": {"preserve": "author's spelling", "standard": "standard spelling", "sampled-colloquial": "colloquial spellings only if sampled"},
        "abbreviations": {"preserve": "author's abbreviations", "familiar": "familiar abbreviations if fitting", "avoid": "spell out casual abbreviations"},
        "contractions": {"preserve": "author's contractions", "natural": "natural contractions", "avoid": "avoid contractions"},
    }
    choices = "; ".join(labels[key][style[key]] for key in labels)
    regional = "Keep regional spelling" if style["regional_spelling"] == "preserve" else "Use " + style["regional_spelling"] + " spelling"
    card = (
        f"{_destinations()[resolved['destination']]['label']}: {choices}. {regional}. "
        f"{_destinations()[resolved['destination']]['guidance']} "
        "Actively match author character; explicit preferences win. "
        "Preserve proper names, acronyms, quotes, URLs/code and meaning-sensitive punctuation. "
        "Never invent typos, slang or intimacy. Adapt prose; never bulk-lowercase."
    )
    # Every component is bounded by the schema; fail visibly if policy growth breaks the budget.
    if len(card) > 600:
        raise ValueError("Destination style card exceeds the 600-character budget.")
    return card


_CONTRACTIONS = re.compile(r"\b(?:\w+n't|(?:i|we|you|they|he|she|it|that|there|what|who|how)'(?:m|re|ve|ll|d|s))\b", re.I)
_ABBREVIATIONS = frozenset("btw fyi idk imo imho lmk np tbh rn asap omw brb afaik".split())
_COLLOQUIAL = frozenset("gonna wanna kinda sorta yep yup nope nah alright cos cuz coz dunno gotta lemme gimme outta hafta tho thru".split())


def _sample_prose(sample: str) -> str:
    # Literal material and someone else's quoted words are not author habits.
    sample = re.sub(r"(?ms)^\s*(```|~~~).*?^\s*\1\s*$", " ", sample)
    sample = re.sub(r"(?m)^(?: {4}|\t)[^\n]*(?:\n|$)", " ", sample)
    sample = re.sub(r"`+[^`\n]*`+|\b(?:https?://|www\.)[^\s<>]+", " ", sample)
    sample = re.sub(r'''"[^"\n]*"|\u201c[^\u201d\n]*\u201d|(?<!\w)'(?:[^'\n]|(?<=\w)'(?=\w))+'(?!\w)|(?<!\w)\u2018(?:[^\u2019\n]|(?<=\w)\u2019(?=\w))+\u2019(?!\w)''', " ", sample)
    return sample


_STYLE_CONTRACTIONS = re.compile(
    r"\b(?:(?:ai|are|ca|could|dare|did|does|do|had|has|have|is|might|must|need|ought|sha|should|was|were|wo|would)n['\u2019]t"
    r"|i['\u2019]m|(?:i|we|you|they)['\u2019](?:ve|ll|d)|(?:we|you|they)['\u2019]re"
    r"|(?:he|she|it|that|there|here|what|who|how|where|when|why)['\u2019](?:s|ll|d)|let['\u2019]s)\b", re.I)
_INFORMAL_ABBREVIATIONS = re.compile(r"\b(?:btw|idk|imo|imho|lmk|np|tbh|rn|omw|brb|afaik)\b")
_INFORMAL_SPELLINGS = re.compile(r"\b(?:gonna|wanna|kinda|sorta|dunno|gotta|lemme|gimme|outta|hafta|tho|cuz|coz)\b")
_LOWERCASE_I = re.compile(r"\bi(?:['\u2019](?:m|ve|ll|d))?\b")
_PRONOUN_VERB = re.compile(
    r"\s+(?:am|was|have|had|do|did|can|could|will|would|should|must|may|might|need|want|like|think|believe|know|feel|hope"
    r"|care|look|see|work|write|read|run|build|help|lead|use|try|love|hate|prefer|expect|[a-z]+ed)\b")
_LOWERCASE_START = re.compile(
    r"(?:\A[ \t]*|[.!?]\s+|\n[ \t]*\n[ \t]*|^[ \t]*(?:[-*+]|\d+[.)]|#{1,6})[ \t]+)"
    r"(?P<word>[a-z][A-Za-z]*(?:['\u2019][A-Za-z]+)?)\b", re.M)
_COMMON_OPENINGS = frozenset(
    "i we you they he she it this that these those the a an there here please thanks thank hi hello"
    " why what how where when because although however and but so if while after before".split())
_VARIABLE_PREFIX = re.compile(r"\b(?:index|variable|parameter|letter|row|column|axis|term|value|item|section|figure|appendix|coordinate|integer)\s*$", re.I)


def _style_visible(text: str) -> str:
    """Fallback literal masking, preserving offsets; callers may supply a precise mask."""
    def blank(match: re.Match) -> str:
        return "".join("\n" if char == "\n" else " " for char in match[0])

    patterns = (
        r"(?ms)^ {0,3}(`{3,}|~{3,})[^\n]*(?:\n.*?^ {0,3}\1[ \t]*(?:\n|$)|\n.*\Z)",
        r"(?m)^(?: {4}|\t)[^\n]*(?:\n|$)",
        r"(`+)[^\n]*?\1|\b(?:https?://|www\.)[^\s<>]+|\]\([^\n)]+\)",
        r'''"[^"\n]*"|\u201c[^\u201d\n]*\u201d|(?<!\w)'(?:[^'\n]|(?<=\w)'(?=\w))+'(?!\w)|(?<!\w)\u2018(?:[^\u2019\n]|(?<=\w)\u2019(?=\w))+\u2019(?!\w)''',
    )
    for pattern in patterns:
        text = re.sub(pattern, blank, text)
    return text


def style_findings(text: str, resolved: Mapping, *, visible: str | None = None) -> list[dict]:
    """Return at most eight contextual suggestions, not grammar validation or edits.

    ``visible`` can mask protected content with spaces/newlines at original offsets.
    Names, acronyms and camelCase are not spelling or capitalization targets.
    """
    if not isinstance(text, str) or (visible is not None and (not isinstance(visible, str) or len(visible) != len(text))):
        raise ValueError("Text and any visible mask must be strings with identical lengths.")
    render_style_card(resolved)  # Validate the same bounded policy used for the request.
    style = resolved["style"]
    body = _style_visible(text) if visible is None else visible
    candidates, seen = [], set()

    def add(kind: str, start: int, end: int, reason: str) -> None:
        quote = text[start:end]
        key = (kind, quote)
        if key not in seen and sum(item[1]["kind"] == kind for item in candidates) < 8:
            seen.add(key)
            candidates.append((start, {"kind": kind, "quote": quote, "reason": reason}))

    if style["contractions"] == "avoid":
        for match in _STYLE_CONTRACTIONS.finditer(body):
            add("contraction", match.start(), match.end(), "Selected context asks to avoid contractions; consider expanding this one.")
    if style["abbreviations"] == "avoid" or style["spelling"] == "standard":
        for match in _INFORMAL_ABBREVIATIONS.finditer(body):
            add("informal-abbreviation", match.start(), match.end(), "Informal lowercase abbreviation may conflict with the selected style; consider spelling it out.")
    if style["spelling"] == "standard":
        for match in _INFORMAL_SPELLINGS.finditer(body):
            add("informal-spelling", match.start(), match.end(), "Selected context asks for standard spelling; consider the full conventional form.")
    if style["case"] == "sentence":
        for match in _LOWERCASE_I.finditer(body):
            if _VARIABLE_PREFIX.search(body[max(0, match.start() - 30):match.start()]):
                continue
            if match[0] != "i" or _PRONOUN_VERB.match(body, match.end()):
                add("capitalization", match.start(), match.end(), "Lowercase pronoun i may conflict with the selected sentence capitalization.")
        for match in _LOWERCASE_START.finditer(body):
            word = match["word"]
            stem = re.split("['\u2019]", word)[0]
            if word != word.lower() or stem not in _COMMON_OPENINGS:
                continue
            start, end = match.span("word")
            # A masked quote at the beginning can be followed by a lowercase attribution.
            prefix = text[match.start():start]
            if any(a != b and not a.isspace() for a, b in zip(prefix, body[match.start():start])):
                continue
            if re.search(r"(?:\b(?:e\.g|i\.e|etc|vs|fig|no|dr|mr|ms|mrs|prof)\.|(?:[A-Z]\.){2,})\s*$", body[:start], re.I):
                continue
            if stem == "i" and re.match(r"\s+(?:is|equals|denotes|represents)\b", body[end:]):
                continue
            add("capitalization", start, end, "Common sentence-opening word is lowercase; consider the selected sentence capitalization.")
    return [finding for _, finding in sorted(candidates, key=lambda item: item[0])[:8]]


def _sample_habits(samples: list[str], style: Mapping) -> list[str]:
    """Describe observable surface habits without extracting sample events or facts."""
    if not samples:
        return []
    samples = [_sample_prose(sample).strip() for sample in samples]
    samples = [sample for sample in samples if sample]
    if not samples:
        return []
    joined = "\n".join(samples).replace("\u2019", "'")
    words = re.findall(r"\b[a-z]+\b", joined.casefold())
    lowercase_words = set(re.findall(r"\b[a-z]+\b", joined))
    habits = []
    if style["contractions"] != "avoid" and _CONTRACTIONS.search(joined):
        habits.append("Use natural contractions, as the samples do.")
    if style["case"] != "sentence":
        starts = re.findall(r"(?:^|[.!?]\s+)([A-Za-z]+)", joined, re.M)
        if len(starts) >= 2 and all(word[0].islower() for word in starts):
            habits.append("The samples favor natural lowercase; use it where this destination permits.")
    if style["punctuation"] != "standard" and len(words) >= 8 and all(
            not sample.rstrip().endswith((".", "!", "?")) for sample in samples):
        habits.append("Keep the samples' light end punctuation when the meaning stays clear.")
    if style["abbreviations"] == "familiar":
        observed = sorted(lowercase_words & _ABBREVIATIONS)
        if observed:
            habits.append("Familiar abbreviations seen in samples: " + ", ".join(observed[:4]) + "; use only if fitting.")
    if style["spelling"] == "sampled-colloquial":
        observed = sorted(lowercase_words & _COLLOQUIAL)
        if observed:
            habits.append("Colloquial spellings seen in samples: " + ", ".join(observed[:4]) + "; do not invent others.")
    # Rhythm observations are deliberately broad, not quotas or invented personality.
    clauses = [part for part in re.split(r"[.!?]+(?:\s+|$)|\n", joined) if part.strip()]
    lengths = [len(re.findall(r"\b[\w']+\b", part)) for part in clauses]
    if len(lengths) >= 3:
        if max(lengths) <= 12:
            habits.append("Favor the samples' compact phrasing without imposing a sentence quota.")
        elif min(lengths) <= 8 and max(lengths) >= 20:
            habits.append("Vary sentence length as the samples do; retain their longer turns where useful.")
    if joined.count("?") >= 2:
        habits.append("The samples use direct questions; retain that movement where it serves the purpose.")
    return habits


def compact_voice(profile: Mapping | None, destination: str | Mapping = "general") -> dict:
    """Distill an author card without new facts, raw sample events, I/O or learning.

    Pass the resolved context as ``destination`` to honor per-call style overrides;
    a destination string instead uses that profile's context preferences.
    """
    if profile is None:
        return {}
    if not isinstance(profile, Mapping):
        raise ValueError("A voice profile must be an object.")
    fields = {}
    for key, count, size in (("preferences", 8, 180), ("avoid", 8, 100), ("samples", 2, 500)):
        values = profile.get(key, [])
        if not isinstance(values, list) or len(values) > count or any(
                not isinstance(value, str) or not value.strip() or len(value) > size for value in values):
            raise ValueError(f"{key} must contain at most {count} nonempty strings of at most {size} characters.")
        fields[key] = list(dict.fromkeys(value.strip() for value in values))
    traits = validate_voice_traits(profile.get("traits", {}))
    contexts = validate_context_preferences(profile.get("contexts", {}))
    resolved = destination if isinstance(destination, Mapping) else resolve_context(destination, preferences=contexts)
    # Validate caller-supplied resolved data even if the profile has no samples.
    render_style_card(resolved)
    result = {key: fields[key] for key in ("preferences", "avoid") if fields[key]}
    if traits:
        result["traits"] = traits
    habits = _sample_habits(fields["samples"], resolved["style"])
    if habits:
        result["sample_habits"] = habits
    if fields["samples"]:
        result["sample_scope"] = "Observed style only; sample facts, feelings and experiences never transfer."
        if not traits:
            result["needs_sample_context"] = True
            result["sample_guidance"] = "Use the supplied samples as style data for vocabulary, rhythm, openings and transitions; surface habits alone do not capture a voice."
    if result:
        result["apply"] = "Actively use these habits in word choice, rhythm and transitions; fit the destination and preserve meaning."
    return result
