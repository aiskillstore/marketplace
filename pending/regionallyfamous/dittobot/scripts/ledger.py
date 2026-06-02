#!/usr/bin/env python3
"""Parse local Dittobot profile/fact-fence ledgers."""

from __future__ import annotations

import json
import re
from collections.abc import Iterable
from pathlib import Path
from typing import Any


LEDGER_KEYS = (
    "protected",
    "voice",
    "forbid",
    "required_claims",
    "forbid_assertions",
    "boundary",
)
FENCE_TO_KEY = {
    "keep": "protected",
    "protected": "protected",
    "fact": "protected",
    "claim": "required_claims",
    "required_claim": "required_claims",
    "voice": "voice",
    "avoid": "forbid",
    "forbid": "forbid",
    "forbid_assertion": "forbid_assertions",
    "boundary": "boundary",
}
FENCE_PATTERN = re.compile(r"\[\[\s*([A-Za-z_ -]+)\s*:\s*(.*?)\s*\]\]", re.DOTALL)


def empty_ledger() -> dict[str, list[str]]:
    return {key: [] for key in LEDGER_KEYS}


def split_terms(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        parts = re.split(r"[,;\n]", value)
    elif isinstance(value, Iterable):
        parts = []
        for item in value:
            parts.extend(split_terms(item))
    else:
        parts = [str(value)]
    return [part.strip() for part in parts if part and part.strip()]


def merge_ledgers(*ledgers: dict[str, list[str]]) -> dict[str, list[str]]:
    merged = empty_ledger()
    for ledger in ledgers:
        for key in LEDGER_KEYS:
            for value in ledger.get(key, []):
                if value not in merged[key]:
                    merged[key].append(value)
    return merged


def parse_fences(text: str) -> dict[str, list[str]]:
    ledger = empty_ledger()
    for raw_key, raw_value in FENCE_PATTERN.findall(text):
        key = FENCE_TO_KEY.get(raw_key.strip().lower().replace(" ", "_").replace("-", "_"))
        if key:
            ledger[key].extend(split_terms(raw_value))
    return ledger


def strip_fences(text: str) -> str:
    text = FENCE_PATTERN.sub("", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def parse_json_ledger(path: Path) -> dict[str, list[str]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise SystemExit(f"{path}: expected a JSON object")
    ledger = empty_ledger()
    aliases = {
        "keep": "protected",
        "protected": "protected",
        "facts": "protected",
        "voice": "voice",
        "preserve_voice": "voice",
        "avoid": "forbid",
        "forbid": "forbid",
        "claims": "required_claims",
        "required_claims": "required_claims",
        "forbid_assertions": "forbid_assertions",
        "boundary": "boundary",
        "when_not_to_apply": "boundary",
    }
    for raw_key, value in raw.items():
        key = aliases.get(str(raw_key))
        if key:
            ledger[key].extend(split_terms(value))
    return ledger


def parse_ledger_file(path: str) -> dict[str, list[str]]:
    target = Path(path)
    if not target.exists():
        raise SystemExit(f"Ledger file not found: {target}")
    if target.suffix.lower() == ".json":
        return parse_json_ledger(target)
    return parse_fences(target.read_text(encoding="utf-8"))


def parse_ledger_files(paths: list[str]) -> dict[str, list[str]]:
    return merge_ledgers(*(parse_ledger_file(path) for path in paths))
