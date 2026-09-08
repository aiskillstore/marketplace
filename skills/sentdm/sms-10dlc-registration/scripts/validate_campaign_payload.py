#!/usr/bin/env python3
"""Validate the exact Sent campaign request used by profile campaign endpoints.

Exit codes:
    0 - valid campaign payload
    1 - invalid payload or unreadable/malformed input
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


USE_CASES = {
    "MARKETING",
    "ACCOUNT_NOTIFICATION",
    "CUSTOMER_CARE",
    "FRAUD_ALERT",
    "TWO_FA",
    "DELIVERY_NOTIFICATION",
    "SECURITY_ALERT",
    "M2M",
    "MIXED",
    "HIGHER_EDUCATION",
    "POLLING_VOTING",
    "PUBLIC_SERVICE_ANNOUNCEMENT",
    "LOW_VOLUME",
}
POLICY_TWO_SAMPLE_CASES = {"MARKETING", "MIXED", "LOW_VOLUME"}
CAMPAIGN_REQUIRED = {"name", "description", "type", "useCases"}
CAMPAIGN_OPTIONAL = {
    "volume",
    "messageFlow",
    "privacyPolicyLink",
    "termsAndConditionsLink",
    "optinMessage",
    "optoutMessage",
    "helpMessage",
    "optinKeywords",
    "optoutKeywords",
    "helpKeywords",
}
URL_RE = re.compile(r"^https://[^\s]+$", re.IGNORECASE)
VOLUME_RE = re.compile(r"^\d+$")


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate(payload: Any, path: str = "<payload>") -> list[str]:
    issues: list[str] = []

    def issue(field: str, reason: str) -> None:
        issues.append(f"{path}: {field}: {reason}")

    if not isinstance(payload, dict):
        issue("<root>", "must be a JSON object")
        return issues
    for key in sorted(set(payload) - {"campaign", "sandbox"}):
        issue(key, "unsupported top-level field")
    if "sandbox" in payload and not isinstance(payload["sandbox"], bool):
        issue("sandbox", "must be boolean")
    campaign = payload.get("campaign")
    if not isinstance(campaign, dict):
        issue("campaign", "required and must be an object")
        return issues
    allowed = CAMPAIGN_REQUIRED | CAMPAIGN_OPTIONAL
    for key in sorted(set(campaign) - allowed):
        issue(f"campaign.{key}", "unsupported field; use the exact camelCase Sent contract")
    for key in sorted(CAMPAIGN_REQUIRED - set(campaign)):
        issue(f"campaign.{key}", "missing required field")
    for key in ("name", "description", "type"):
        if key in campaign and not _text(campaign[key]):
            issue(f"campaign.{key}", "must be a non-empty string")
    volume = campaign.get("volume")
    if volume is not None and (not isinstance(volume, str) or not VOLUME_RE.fullmatch(volume)):
        issue("campaign.volume", "must be a numeric string such as '1999' or '2000'")
    for key in ("privacyPolicyLink", "termsAndConditionsLink"):
        value = campaign.get(key)
        if value is not None and (not _text(value) or not URL_RE.fullmatch(value)):
            issue(f"campaign.{key}", "must be a public HTTPS URL or null")
    for key in ("optinKeywords", "optoutKeywords", "helpKeywords"):
        value = campaign.get(key)
        if value is not None and (not _text(value) or len(value) > 255):
            issue(f"campaign.{key}", "must be a non-empty string of at most 255 characters or null")

    use_cases = campaign.get("useCases")
    if not isinstance(use_cases, list) or not use_cases:
        issue("campaign.useCases", "must be a non-empty array")
        return issues
    for index, use_case in enumerate(use_cases):
        field = f"campaign.useCases[{index}]"
        if not isinstance(use_case, dict):
            issue(field, "must be an object")
            continue
        for key in sorted(set(use_case) - {"messagingUseCaseUs", "sampleMessages"}):
            issue(f"{field}.{key}", "unsupported field")
        selected = use_case.get("messagingUseCaseUs")
        if selected not in USE_CASES:
            issue(f"{field}.messagingUseCaseUs", f"must be one of {sorted(USE_CASES)}")
        samples = use_case.get("sampleMessages")
        if not isinstance(samples, list) or not 1 <= len(samples) <= 5:
            issue(f"{field}.sampleMessages", "must contain 1–5 samples")
            continue
        for sample_index, sample in enumerate(samples):
            if not _text(sample):
                issue(f"{field}.sampleMessages[{sample_index}]", "must be a non-empty string")
            elif len(sample) > 1024:
                issue(f"{field}.sampleMessages[{sample_index}]", "must be at most 1,024 characters")
        if selected in POLICY_TWO_SAMPLE_CASES and len(samples) < 2:
            issue(
                f"{field}.sampleMessages",
                f"{selected} requires at least two samples under the compliance policy layer",
            )
    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("payload", type=Path)
    args = parser.parse_args(argv)
    try:
        payload = json.loads(args.payload.read_text(encoding="utf-8"))
    except OSError as exc:
        print(f"{args.payload}: <file>: {exc}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"{args.payload}: <file>: invalid JSON ({exc})", file=sys.stderr)
        return 1
    issues = validate(payload, str(args.payload))
    if issues:
        print("\n".join(issues), file=sys.stderr)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
