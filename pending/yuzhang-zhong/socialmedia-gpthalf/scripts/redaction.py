"""Redact secrets and sensitive request details from user-visible errors."""

from __future__ import annotations

import re
from typing import Iterable


SECRET_PATTERNS = (
    re.compile(r"(?i)(authorization\s*[:=]\s*(?:token|bearer)?\s*)[^\s,;]+"),
    re.compile(r"(?i)(x-api-key\s*[:=]\s*)[^\s,;]+"),
    re.compile(r"(?i)(api[_-]?key\s*[:=]\s*)[^\s,;]+"),
)


def redact_text(value: object, secrets: Iterable[str] = ()) -> str:
    """Return a bounded string with credentials removed."""

    text = str(value)
    for secret in secrets:
        if secret:
            text = text.replace(secret, "[REDACTED]")
    for pattern in SECRET_PATTERNS:
        text = pattern.sub(r"\1[REDACTED]", text)
    return text[:1000]


def safe_provider_error(provider: str, category: str, error: object, secrets: Iterable[str] = ()) -> dict:
    """Build a normalized error without raw request or response payloads."""

    return {
        "provider": provider,
        "category": category,
        "message": redact_text(error, secrets),
    }
