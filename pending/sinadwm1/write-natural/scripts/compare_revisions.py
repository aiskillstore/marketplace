#!/usr/bin/env python3
"""Read-only revision integrity review; heuristic differences require human review."""

import argparse
from collections import Counter
from decimal import Decimal, InvalidOperation
import json
import re
import sys

sys.dont_write_bytecode = True

from text_common import (citation_spans, finding, human_report, language, mask_spans,
                         protected_spans, read_utf8, report_order)


DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")
# Group separators must have valid groups; a comma that fails this shape is
# punctuation, not silently coerced into a decimal or removed.
NUMBER = re.compile(r"(?<![\w.٫])(?P<sign>[+−-]?)(?P<number>\d{1,3}(?:[,٬]\d{3})+(?:[.٫]\d+)?|\d+(?:[.٫]\d+)?)(?!\d|[.٫]\d)")
UNIT_GROUPS = {
    "mg": ["mg", "milligram", "milligrams", "میلی‌گرم", "میلی گرم"],
    "g": ["g", "gram", "grams", "گرم"],
    "kg": ["kg", "kilogram", "kilograms", "کیلوگرم", "کیلو گرم"],
    "mcg": ["mcg", "µg", "μg", "microgram", "micrograms", "میکروگرم"],
    "ml": ["ml", "mL", "milliliter", "milliliters", "میلی‌لیتر", "میلی لیتر"],
    "l": ["l", "L", "liter", "liters", "litre", "litres", "لیتر"],
    "mm": ["mm", "millimeter", "millimeters", "میلی‌متر", "میلی متر"],
    "cm": ["cm", "centimeter", "centimeters", "سانتی‌متر", "سانتی متر"],
    "m": ["m", "meter", "meters", "metre", "metres", "متر"],
    "km": ["km", "kilometer", "kilometers", "کیلومتر"],
    "s": ["s", "sec", "second", "seconds", "ثانیه"],
    "min": ["min", "minute", "minutes", "دقیقه"],
    "h": ["h", "hour", "hours", "ساعت"],
    "day": ["day", "days", "روز"],
    "week": ["week", "weeks", "هفته"],
    "year": ["year", "years", "سال"],
    "USD": ["USD", "dollar", "dollars", "دلار"],
    "EUR": ["EUR", "euro", "euros", "یورو"],
    "GBP": ["GBP", "pound", "pounds"],
    "IRR": ["IRR", "ریال"], "toman": ["تومان"],
    "°C": ["°C", "° C", "درجه سانتی‌گراد", "درجه سلسیوس"],
    "°F": ["°F", "° F"],
}
UNIT_MAP = {variant.casefold(): canonical for canonical, variants in UNIT_GROUPS.items() for variant in variants}
UNIT = re.compile(r"[ \t\u00a0]*(" + "|".join(re.escape(unit) for unit in sorted(UNIT_MAP, key=len, reverse=True)) + r")(?![\w‌])", re.I)
PERCENT = re.compile(r"[ \t\u00a0]*(?:[%٪]|percent(?:age)?(?:[ \t]+points?)?\b|واحد[ \t]+درصد(?:ی)?(?![\w‌])|درصد(?:ی)?(?![\w‌]))", re.I)
RANGE = re.compile(r"[ \t\u00a0]*(?:[–—-]|to\b|through\b|تا(?![\w‌])|الی(?![\w‌]))[ \t\u00a0]*", re.I)

MARKERS = [
    ("negation", r"\b(?:not|never|neither|without|cannot|can't|isn't|aren't|wasn't|weren't|don't|doesn't|didn't|won't|wouldn't|couldn't|shouldn't|mustn't)\b"),
    ("uncertainty", r"\b(?:may|might|could|possibly|perhaps|probably|likely|unlikely|apparently|approximately|about|roughly|estimated|suggests?|appears?)\b"),
    ("qualification", r"\b(?:some|most|often|usually|sometimes|generally|typically|unless|except|subject to|at least|at most|up to|no more than|no less than)\b"),
    ("negation", r"(?<![\w‌])(?:نیست(?:ند|م)?|نبود(?:ند|م)?|نشد(?:ه|ند)?|نمی‌[^\W\d_]+|نمی [^\W\d_]+|هرگز|بدون|نه)(?![\w‌])"),
    ("uncertainty", r"(?<![\w‌])(?:ممکن است|شاید|احتمالاً|احتمالا|احتمال دارد|تقریباً|تقریبا|حدود|برآورد(?:ی| شده)?|به نظر می‌رسد)(?![\w‌])"),
    ("qualification", r"(?<![\w‌])(?:برخی|بعضی|اغلب|معمولاً|معمولا|گاهی|عموماً|عموما|مگر|به‌جز|به جز|حداقل|حداکثر|دست‌کم|دست کم)(?![\w‌])"),
]


def canonical_decimal(raw):
    value = Decimal(raw.translate(DIGITS).replace(",", "").replace("٬", "").replace("٫", "."))
    return format(value, "f").rstrip("0").rstrip(".") if "." in format(value, "f") else format(value, "f")


def numeric_claims(text, protected):
    prose = mask_spans(text, protected)
    claims = []
    for match in NUMBER.finditer(prose):
        raw = match.group("number")
        try:
            value = canonical_decimal(raw)
        except InvalidOperation:  # defensive; regex accepts only decimal shapes
            continue
        # A matched prefix of an invalid grouping is not a verified normalization.
        # It remains a separate numeric claim and is not joined across punctuation.
        suffix = prose[match.end():]
        percent_match = PERCENT.match(suffix)
        unit_match = UNIT.match(suffix)
        # A numeral attached to an unknown word is an identifier, not a
        # supported quantity. Known adjacent units (5mg, 5kg) remain checkable.
        if suffix and re.match(r"[\w‌]", suffix) and not (percent_match or unit_match):
            continue
        percent = None
        unit = ""
        end = match.end()
        if percent_match:
            percent = "percentage_points" if re.search(r"points?\b|واحد", percent_match.group(), re.I) else "%"
            end += percent_match.end()
        elif unit_match:
            unit = UNIT_MAP[unit_match.group(1).casefold()]
            end += unit_match.end()
        before = prose[:match.start()]
        currency = re.search(r"([+−-]?)([$€£])[ \t\u00a0]*$", before)
        if currency:
            unit = {"$": "USD", "€": "EUR", "£": "GBP"}[currency.group(2)]
        sign = {"−": "-"}.get(match.group("sign"), match.group("sign"))
        if currency and not sign:
            sign = {"−": "-"}.get(currency.group(1), currency.group(1))
        claims.append({"start": match.start(), "end": end, "value": value,
                       "sign": sign, "percent": percent, "unit": unit,
                       "text": text[match.start():end]})
    ranges = []
    for left, right in zip(claims, claims[1:]):
        between = prose[left["end"]:right["start"]]
        # In an otherwise adjacent pair, ASCII '-' can be a compact range
        # connector: 10 -20. Keep a true negative endpoint in 10--20 and
        # 10 - -20; Unicode minus (−) is always a sign, never a connector.
        if right["sign"] == "-" and prose[right["start"]] == "-" and re.fullmatch(r"[ \t\u00a0]*", between):
            between += "-"
            right["sign"] = ""
            right["start"] += 1
        if RANGE.fullmatch(between):
            # A trailing unit/percent applies to both endpoints of the range.
            if not left["unit"]:
                left["unit"] = right["unit"]
            if left["percent"] is None:
                left["percent"] = right["percent"]
            ranges.append((left, right))
    return claims, ranges


def signature(claim):
    return (claim["value"], claim["sign"], claim["percent"], claim["unit"])


def marker_spans(text, protected):
    prose = mask_spans(text, protected).replace("’", "'")
    result = []
    for category, pattern in MARKERS:
        for match in re.finditer(pattern, prose, re.I):
            result.append((match.start(), category, re.sub(r"\s+", " ", match.group().casefold())))
    return sorted(result)


def load_contract(path):
    """A small explicit schema; rejecting typos avoids silently missing checks."""
    def unique_keys(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate invariants key: {}".format(key))
            result[key] = value
        return result

    value = json.loads(read_utf8(path), object_pairs_hook=unique_keys)
    if not isinstance(value, dict) or set(value) - {"protected_strings", "required_terms"}:
        raise ValueError("invariants must be an object with only protected_strings and/or required_terms")
    for key, items in value.items():
        if not isinstance(items, list) or any(not isinstance(item, str) or not item.strip() for item in items):
            raise ValueError("invariants.{} must be a list of nonempty strings".format(key))
        if len(items) != len(set(items)):
            raise ValueError("invariants.{} contains duplicate strings".format(key))
    return value


def term_present(text, value):
    """Match exact case-sensitive terms, avoiding cat inside concatenate."""
    left = r"(?<![\w‌])" if re.match(r"[\w‌]", value[0]) else ""
    right = r"(?![\w‌])" if re.match(r"[\w‌]", value[-1]) else ""
    return re.search(left + re.escape(value) + right, text) is not None


def compare(original, revised, invariants=None):
    findings = []
    original_protected = protected_spans(original, quotes=True)
    revised_protected = protected_spans(revised, quotes=True)
    original_citations = citation_spans(original, original_protected)
    revised_citations = citation_spans(revised, revised_protected)

    def original_finding(offset, code, message, **extra):
        findings.append(finding(original, offset, code, message, source="original", **extra))

    def revised_finding(offset, code, message, **extra):
        findings.append(finding(revised, offset, code, message, source="revised", **extra))

    remaining = Counter((span.kind, span.text) for span in revised_protected + revised_citations)
    for span in original_protected + original_citations:
        key = (span.kind, span.text)
        if remaining[key]:
            remaining[key] -= 1
        else:
            original_finding(span.start, "PROTECTED_SPAN_REVIEW",
                             "An exact {} span was removed, changed, or changed protection context. Review the source before accepting.".format(span.kind),
                             kind=span.kind, original=span.text)
    remaining = Counter((span.kind, span.text) for span in original_protected + original_citations)
    for span in revised_protected + revised_citations:
        key = (span.kind, span.text)
        if remaining[key]:
            remaining[key] -= 1
        else:
            revised_finding(span.start, "PROTECTED_SPAN_ADDED_REVIEW",
                            "A new exact {} span or protection context appears in the revision. Verify its source and purpose.".format(span.kind),
                            kind=span.kind, revised=span.text)
    # Numeric claims in protected material are reviewed by the exact check above.
    original_claims, original_ranges = numeric_claims(original, original_protected + original_citations)
    revised_claims, revised_ranges = numeric_claims(revised, revised_protected + revised_citations)
    revised_counts = Counter(signature(claim) for claim in revised_claims)
    removed = []
    for claim in original_claims:
        key = signature(claim)
        if revised_counts[key]:
            revised_counts[key] -= 1
        else:
            removed.append(claim)
    original_counts = Counter(signature(claim) for claim in original_claims)
    added = []
    for claim in revised_claims:
        key = signature(claim)
        if original_counts[key]:
            original_counts[key] -= 1
        else:
            added.append(claim)
    # Pair same-value changes first so units, percentages and signs are explicit.
    used_added = set()
    for old in removed:
        same_value = next((index for index, new in enumerate(added) if index not in used_added and new["value"] == old["value"]), None)
        if same_value is not None:
            new = added[same_value]
            used_added.add(same_value)
            changed = [key for key in ("sign", "percent", "unit") if old[key] != new[key]]
            original_finding(old["start"], "NUMERIC_ATTRIBUTE_REVIEW",
                             "The same numeric magnitude has changed {}. This is a semantic review prompt, not proof of meaning.".format(", ".join(changed)),
                             before={key: old[key] for key in ("value", "sign", "percent", "unit")},
                             after={key: new[key] for key in ("value", "sign", "percent", "unit")})
        else:
            original_finding(old["start"], "NUMERIC_CLAIM_REMOVED_REVIEW",
                             "This normalized numeric claim has no matching occurrence in the revision; check value, scope and context.",
                             claim={key: old[key] for key in ("value", "sign", "percent", "unit")})
    for index, new in enumerate(added):
        if index not in used_added:
            revised_finding(new["start"], "NUMERIC_CLAIM_ADDED_REVIEW",
                            "This normalized numeric claim has no matching occurrence in the original; verify its source and context.",
                            claim={key: new[key] for key in ("value", "sign", "percent", "unit")})
    revised_range_counts = Counter((signature(left), signature(right)) for left, right in revised_ranges)
    for left, right in original_ranges:
        key = (signature(left), signature(right))
        if revised_range_counts[key]:
            revised_range_counts[key] -= 1
        else:
            original_finding(left["start"], "RANGE_REVIEW",
                             "A numeric range no longer has a matching endpoint-and-range pattern. Review the bounds, connector and shared unit.")
    original_range_counts = Counter((signature(left), signature(right)) for left, right in original_ranges)
    for left, right in revised_ranges:
        key = (signature(left), signature(right))
        if original_range_counts[key]:
            original_range_counts[key] -= 1
        else:
            revised_finding(left["start"], "RANGE_ADDED_REVIEW",
                            "A numeric range has no matching endpoint-and-range pattern in the original. Verify its bounds and source.")

    old_markers = marker_spans(original, original_protected + original_citations)
    new_markers = marker_spans(revised, revised_protected + revised_citations)
    revised_markers = Counter((category, marker) for _, category, marker in new_markers)
    for offset, category, marker in old_markers:
        key = (category, marker)
        if revised_markers[key]:
            revised_markers[key] -= 1
        else:
            original_finding(offset, "{}_REMOVAL_REVIEW".format(category.upper()),
                             "The marker {!r} has fewer exact occurrences. Review possible changes to negation, certainty or scope; paraphrases can be equivalent.".format(marker),
                             marker=marker)
    original_markers = Counter((category, marker) for _, category, marker in old_markers)
    for offset, category, marker in new_markers:
        key = (category, marker)
        if original_markers[key]:
            original_markers[key] -= 1
        else:
            revised_finding(offset, "{}_ADDITION_REVIEW".format(category.upper()),
                            "The marker {!r} has more exact occurrences. Review possible changes to negation, certainty or scope; paraphrases can be equivalent.".format(marker),
                            marker=marker)

    invariants = invariants or {}
    for value in invariants.get("protected_strings", []):
        count = original.count(value)
        if not count:
            original_finding(0, "INVARIANT_BASELINE_REVIEW", "An exact protected string from the contract is absent from the original.", invariant=value)
        if revised.count(value) < max(1, count):
            revised_finding(revised.find(value) if value in revised else 0, "INVARIANT_PROTECTED_REVIEW",
                            "The revision contains fewer exact protected-string occurrences than the contract requires.", invariant=value)
    for value in invariants.get("required_terms", []):
        if not term_present(revised, value):
            revised_finding(0, "INVARIANT_REQUIRED_REVIEW", "A required exact term is absent from the revision.", invariant=value)

    return {"schema_version": 1, "tool": "compare_revisions",
            "scope": "Heuristic review only; no authorship determination, meaning-equivalence test or factual verification.",
            "lang": {"original": language(mask_spans(original, original_protected)),
                     "revised": language(mask_spans(revised, revised_protected))},
            "metrics": {"original_numeric_claims": len(original_claims), "revised_numeric_claims": len(revised_claims),
                        "original_ranges": len(original_ranges), "revised_ranges": len(revised_ranges),
                        "original_protected_spans": len(original_protected) + len(original_citations),
                        "revised_protected_spans": len(revised_protected) + len(revised_citations)},
            "findings": sorted(findings, key=report_order)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("original", help="original UTF-8 text path")
    parser.add_argument("revised", help="revised UTF-8 text path")
    parser.add_argument("--invariants", help="UTF-8 JSON contract with protected_strings and required_terms")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true", help="exit 1 if any advisory findings occur")
    args = parser.parse_args(argv)
    if args.original == "-" or args.revised == "-" or args.invariants == "-":
        parser.error("comparison requires file paths; stdin is supported by audit_text.py")
    try:
        contract = load_contract(args.invariants) if args.invariants else None
        report = compare(read_utf8(args.original), read_utf8(args.revised), contract)
    except (OSError, UnicodeError, ValueError, InvalidOperation) as error:
        parser.error(str(error))
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        human_report(report)
    return 1 if args.strict and report["findings"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
