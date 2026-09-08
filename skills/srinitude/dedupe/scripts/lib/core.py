"""Shared normalization and grouping for dedupe reports."""
import hashlib
import json
import unicodedata
from difflib import SequenceMatcher


def canonical_json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def key_digest(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def normalize_text(value, policy):
    if not isinstance(value, str):
        raise ValueError("text items must be strings")
    value = unicodedata.normalize(policy.get("unicode", "NFC"), value)
    if policy.get("casefold", False):
        value = value.casefold()
    whitespace = policy.get("whitespace", "preserve")
    if whitespace == "collapse":
        value = " ".join(value.split())
    elif whitespace != "preserve":
        raise ValueError("whitespace must be preserve or collapse")
    return value


def normalize_scalar(value, policy):
    if isinstance(value, str):
        return normalize_text(value, policy)
    return canonical_json(value)


def group_items(items, key_fn):
    buckets = {}
    for index, item in enumerate(items):
        key = key_fn(item)
        buckets.setdefault(key, []).append(index)
    return buckets


def find_similarity(items, adapter, normalization, threshold):
    if adapter != "text":
        return []
    if not 0 <= threshold <= 1:
        raise ValueError("similarity_threshold must be between 0 and 1")
    values = [normalize_text(item, normalization) for item in items]
    candidates = []
    for left in range(len(values)):
        for right in range(left + 1, len(values)):
            score = SequenceMatcher(None, values[left], values[right]).ratio()
            if score >= threshold and values[left] != values[right]:
                candidates.append({"indices": [left, right], "score": round(score, 6),
                                   "kind": "similarity-candidate"})
    return candidates


def record_conflicts(items, members, key_fields):
    fields = set().union(*(items[index].keys() for index in members))
    conflicts = []
    for field in sorted(fields - set(key_fields)):
        values = {canonical_json({"present": field in items[index],
                                  "value": items[index].get(field)}) for index in members}
        if len(values) > 1:
            conflicts.append(field)
    return conflicts
