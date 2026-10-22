#!/usr/bin/env python3
"""Deterministic listing text audit. Reads JSON from stdin; prints JSON findings."""
import json
import re
import sys

RISK = {
    "absolute guarantee": re.compile(r"\b(guaranteed|100% guaranteed|cure|miracle)\b", re.I),
    "medical claim": re.compile(r"\b(treats|prevents|diagnoses|heals)\b", re.I),
    "superlative or comparison": re.compile(r"\b(best|#1|number one|the only)\b", re.I),
}


def audit(data):
    findings = []
    def add(level, field, message, suggestion):
        findings.append({"severity": level, "field": field, "finding": message, "suggestion": suggestion})
    title = str(data.get("title", ""))
    if not title:
        add("high", "title", "Title is missing.", "Add a specific, factual product title.")
    elif len(title) > 200:
        add("high", "title", f"Title has {len(title)} characters; limit is 200.", "Remove secondary details and retain product identity.")
    bullets = data.get("bullets", [])
    if len(bullets) != 5:
        add("medium", "bullets", f"Found {len(bullets)} bullets; this check expects 5.", "Provide five concise, distinct feature bullets.")
    backend = str(data.get("backend_terms", ""))
    byte_count = len(backend.encode("utf-8"))
    if byte_count > 249:
        add("high", "backend_terms", f"Backend terms use {byte_count} UTF-8 bytes; limit is 249.", "Remove redundant terms until within limit.")
    texts = {"title": title, "description": str(data.get("description", "")), "backend_terms": backend}
    texts.update({f"bullet_{i+1}": str(v) for i, v in enumerate(bullets)})
    for field, value in texts.items():
        words = re.findall(r"[A-Za-z0-9]+", value.lower())
        repeated = sorted({w for w in words if len(w) > 3 and words.count(w) >= 4})
        if repeated:
            add("low", field, "Repeated terms: " + ", ".join(repeated), "Keep necessary terms; remove repetition without meaning.")
        for label, pattern in RISK.items():
            for match in pattern.finditer(value):
                add("high", field, f"Potentially risky wording ({label}): {match.group(0)}.", "Verify against current policy and evidence; replace unsupported claims with facts.")
    keyword = str(data.get("main_keyword", "")).strip().lower()
    if keyword:
        for field, value in (("title", title), ("bullets", " ".join(map(str, bullets))), ("description", texts["description"])):
            if keyword not in value.lower():
                add("medium", field, f"Main keyword is not present: {keyword}.", "Add naturally where accurate; avoid awkward repetition.")
    rank = {"high": 3, "medium": 2, "low": 1}
    findings.sort(key=lambda item: (-rank[item["severity"]], item["field"], item["finding"]))
    return {"summary": {level: sum(item["severity"] == level for item in findings) for level in rank}, "findings": findings}


if __name__ == "__main__":
    try:
        print(json.dumps(audit(json.load(sys.stdin)), indent=2, ensure_ascii=False))
    except (json.JSONDecodeError, AttributeError) as exc:
        sys.exit(f"Expected a JSON object on stdin: {exc}")
