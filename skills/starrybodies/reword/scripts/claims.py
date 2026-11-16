"""Bounded, inspectable relationship checks. These are heuristics, not an NLI model."""

from collections import Counter, defaultdict
import re

MONTHS = {name: index for index, name in enumerate(
    ("january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"), 1)}
MONTH = "(?:" + "|".join(MONTHS) + ")"
MONTH_FIRST = re.compile(r"\b(" + MONTH + r")\s+(\d{1,2})(?:st|nd|rd|th)?(?:,?\s+(\d{4}))?\b", re.I)
DAY_FIRST = re.compile(r"\b(\d{1,2})(?:st|nd|rd|th)?\s+(" + MONTH + r")(?:\s+(\d{4}))?\b", re.I)
WORD_NUMBERS = dict(zip("two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty".split(), range(2, 21)))
MODALS = {
    "possible": r"\b(?:may|might|could|perhaps|likely|unlikely|possibly|potentially|approximately|estimated?|suggests?|appears?|seems?)\b",
    "ability": r"\bcan\b|\bable to\b",
    "prediction": r"\bwill\b|\bgoing to\b",
    "conditional": r"\bwould\b",
    "obligation": r"\b(?:must|shall|should)\b",
    "unknown": r"\b(?:unknown|unproven|untested)\b",
}
NEGATION = re.compile(r"\b(?:no|not|never|without|cannot|\w+n't|nobody|nothing)\b", re.I)
CAUSAL = re.compile(r"\b(?:caused?|causes|led to|resulted in|because|therefore|due to)\b", re.I)
SCOPE = re.compile(r"\b(?:if|unless|until|except|only|before|after|during|simultaneously|at once|at the same time|at least|at most|more than|less than|up to)\b", re.I)
STOP = set("the a an is are was were be been being it its this that these those we our i you your they their he she his her and or but with for to from of in on at by as has have had do does did so than then can will would may might could should must shall not no never if only until unless before after during simultaneously likely possibly potentially perhaps unknown".split())


def normalize(text):
    text = text.replace("\u2019", "'")
    text = re.sub(r"\b(?:cannot|can't)\b", "can not", text, flags=re.I)
    text = re.sub(r"\bwon't\b", "will not", text, flags=re.I)
    text = MONTH_FIRST.sub("DATE", text)
    text = DAY_FIRST.sub("DATE", text)
    text = re.sub(r"\b(?:could|would|can|will)\s+you\b", "REQUEST you", text, flags=re.I)
    text = re.sub(r"\bwould (?:also |really )?like\b", "want", text, flags=re.I)
    text = re.sub(r"\b(?:not|isn't|aren't|doesn't) (?:just|merely|only)\b", "ALSO", text, flags=re.I)
    return re.sub(r"\b(\w+)'ll\b", r"\1 will", text, flags=re.I)


def modality(text):
    text = normalize(text)
    return {name for name, pattern in MODALS.items() if re.search(pattern, text, re.I)}


def scopes(text):
    aliases = {"at once": "concurrent", "at the same time": "concurrent", "simultaneously": "concurrent", "up to": "at most"}
    return Counter(aliases.get(m[0].lower(), m[0].lower()) for m in SCOPE.finditer(text))


def dates(text):
    result = Counter()
    for m in re.finditer(r"\b(\d{4})-(\d{2})-(\d{2})\b", text):
        result[f"{m[1]}-{m[2]}-{m[3]}"] += 1
    for m in MONTH_FIRST.finditer(text):
        result[f"{m[3] or '?'}-{MONTHS[m[1].lower()]:02d}-{int(m[2]):02d}"] += 1
    for m in DAY_FIRST.finditer(text):
        result[f"{m[3] or '?'}-{MONTHS[m[2].lower()]:02d}-{int(m[1]):02d}"] += 1
    return result


def speakers(text):
    # Bind literal speech to explicitly named speakers; generic descriptions need review.
    result = Counter()
    pattern = r'''\b([A-Z][\w'-]*(?:\s+[A-Z][\w'-]*){0,2})\s+(?:said|wrote|reported|stated|replied)[:,]?\s*(?:"([^"\n]+)"|\u201c([^\u201d\n]+)\u201d)'''
    for m in re.finditer(pattern, text):
        result[(m[1], m[2] or m[3])] += 1
    return result


def sentences(text):
    return [m[0].strip() for m in re.finditer(r".+?(?:[.!?](?=\s|$)|\n+|$)", text, re.S) if m[0].strip()]


def tokens(text):
    # Values must not decide which subject a sentence belongs to.
    return set(w for w in re.findall(r"[a-z]+", normalize(text).lower()) if w not in STOP and w not in WORD_NUMBERS)


def aligned(source, edited):
    """Find nearby claims by shared content words; rank at most 12 candidates each."""
    target = list(dict.fromkeys(sentences(edited)))
    terms = [tokens(sentence) for sentence in target]
    index = defaultdict(set)
    for i, words in enumerate(terms):
        for word in words:
            index[word].add(i)
    for source_sentence in dict.fromkeys(sentences(source)):
        words, candidates = tokens(source_sentence), Counter()
        for word in sorted(words):
            postings = index.get(word, ())
            for i in sorted(postings):
                candidates[i] += 1 / len(postings)
        best, score = None, 0
        for i, _ in candidates.most_common(12):
            shared = words & terms[i]
            similarity = len(shared) / max(1, len(words | terms[i]))
            if similarity > score and (len(shared) >= 2 or words == terms[i]):
                best, score = i, similarity
        if best is not None and score >= 0.3:
            yield source_sentence, target[best]


def word_numbers(text):
    return Counter(WORD_NUMBERS[w] for w in re.findall(r"\b[a-z]+\b", text.lower()) if w in WORD_NUMBERS)


def relationship_risks(original, candidate, source, edited, numbers, quantities):
    if original == candidate:
        return []
    review, seen = [], set()

    def flag(kind, reason, before, after):
        key = (kind, before, after)
        if key not in seen:
            seen.add(key)
            review.append({"kind": kind, "reason": reason, "before": before[:180], "after": after[:180]})

    # Global checks cover deletions even when sentence alignment is inconclusive.
    source_modality, edited_modality = modality(source), modality(edited)
    source_negations = len(NEGATION.findall(normalize(source)))
    edited_negations = len(NEGATION.findall(normalize(edited)))
    source_word_numbers, edited_word_numbers = word_numbers(source), word_numbers(edited)
    if source_modality != edited_modality:
        flag("uncertainty", "Review changed certainty, ability, obligation, or commitment.", source, edited)
    if source_negations != edited_negations:
        flag("negation", "Review changed polarity; equivalent wording may be valid.", source, edited)
    if scopes(source) != scopes(edited):
        flag("scope", "Review changed conditions, timing, or bounds.", source, edited)
    if not CAUSAL.search(source) and CAUSAL.search(edited):
        flag("causality", "The edit introduces a causal explanation. Check its support.", source, edited)
    if source_word_numbers != edited_word_numbers:
        flag("word-number", "Review changed spelled-out counts; verify any digit conversion.", source, edited)
    weak = r"\b(?:helped|assisted|contributed|supported|co-led)\b"
    if len(re.findall(weak, source, re.I)) > len(re.findall(weak, edited, re.I)) and re.search(r"\b(?:founded|created|led|owned|built)\b", edited, re.I):
        flag("attribution", "Check whether assistance became ownership.", source, edited)

    # Totals can stay unchanged while values or qualifiers migrate to a different claim.
    global_numbers_equal = numbers(source, source) == numbers(edited, edited)
    for before, after in aligned(source, edited):
        if before == after:
            continue
        if global_numbers_equal and (numbers(before, before) != numbers(after, after) or quantities(before) != quantities(after) or (source_word_numbers == edited_word_numbers and word_numbers(before) != word_numbers(after))):
            flag("fact-binding", "Check which subject each value belongs to.", before, after)
        if source_modality == edited_modality and modality(before) != modality(after):
            flag("uncertainty-binding", "A qualifier may have moved to a different claim.", before, after)
        if source_negations == edited_negations and len(NEGATION.findall(normalize(before))) != len(NEGATION.findall(normalize(after))):
            flag("negation-binding", "Negation may have moved to a different claim.", before, after)
        names_before = re.findall(r"\b[A-Z][a-z]+\b", before)
        names_after = re.findall(r"\b[A-Z][a-z]+\b", after)
        if len(names_before) > 1 and Counter(names_before) == Counter(names_after) and names_before != names_after:
            flag("actor-order", "Check that changing name order has not reversed who acted.", before, after)
        # Detect explicit from/to reversals without objecting to paragraph reordering.
        pair = r"\bfrom\s+(.{1,45}?)\s+to\s+(.{1,45}?)(?=[,.;]|$)"
        first = re.search(pair, before, re.I)
        second = re.search(pair, after, re.I)
        down = r"\b(?:fell|dropped|declined|decreased|reduced|lowered)\b"
        up = r"\b(?:rose|grew|increased|raised)\b"
        if first and second and ((re.search(down, before, re.I) and re.search(up, after, re.I)) or (re.search(up, before, re.I) and re.search(down, after, re.I))):
            flag("direction-verb", "A rise may have become a fall, or vice versa.", before, after)
        if first and second:
            left, right = numbers(first[1], first[1]), numbers(first[2], first[2])
            if left and right and left != right and left == numbers(second[2], second[2]) and right == numbers(second[1], second[1]):
                flag("direction", "An explicit from/to change appears reversed.", before, after)
    return review
