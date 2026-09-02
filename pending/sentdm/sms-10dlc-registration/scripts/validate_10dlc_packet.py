#!/usr/bin/env python3
"""Validate the internal 10DLC evidence packet schema.

This packet is readiness evidence, not the Sent campaign API request. Its
snake_case fields are namespaced by an explicit schema version so they cannot
be mistaken for Sent's camelCase contract.

Exit codes:
    0 - valid evidence packet
    1 - invalid packet or unreadable/malformed input
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "sent-10dlc-evidence/v1"
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
URL_RE = re.compile(r"^https://[^\s]+$", re.IGNORECASE)
EIN_RE = re.compile(r"^\d{2}-?\d{7}$")
PHONE_RE = re.compile(r"^\+\d{1,15}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
REQUIRED = {
    "schema_version",
    "legal_business_name",
    "ein",
    "business_address",
    "business_phone",
    "contact_email",
    "website",
    "privacy_policy_url",
    "terms_and_conditions_url",
    "opt_in_evidence",
    "message_flow",
    "autoresponses",
    "use_cases",
}


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate(packet: Any, path: str = "<packet>") -> list[str]:
    issues: list[str] = []

    def issue(field: str, reason: str) -> None:
        issues.append(f"{path}: {field}: {reason}")

    if not isinstance(packet, dict):
        issue("<root>", "must be a JSON object")
        return issues
    for key in sorted(REQUIRED - set(packet)):
        issue(key, "missing required field")
    if packet.get("schema_version") != SCHEMA_VERSION:
        issue("schema_version", f"must equal {SCHEMA_VERSION!r}")
    for key in ("legal_business_name", "business_address", "message_flow"):
        if key in packet and not _text(packet[key]):
            issue(key, "must be a non-empty string")
    if _text(packet.get("ein")) and not EIN_RE.fullmatch(packet["ein"]):
        issue("ein", "must contain nine digits, optionally formatted NN-NNNNNNN")
    if _text(packet.get("business_phone")) and not PHONE_RE.fullmatch(packet["business_phone"]):
        issue("business_phone", "must be E.164")
    if _text(packet.get("contact_email")) and not EMAIL_RE.fullmatch(packet["contact_email"]):
        issue("contact_email", "must be a valid email")
    for key in ("website", "privacy_policy_url", "terms_and_conditions_url"):
        if key in packet and (not _text(packet[key]) or not URL_RE.fullmatch(packet[key])):
            issue(key, "must be a public HTTPS URL")

    opt_in = packet.get("opt_in_evidence")
    if not isinstance(opt_in, dict):
        issue("opt_in_evidence", "must be an object")
    else:
        for key in ("method", "description", "proof_url"):
            if not _text(opt_in.get(key)):
                issue(f"opt_in_evidence.{key}", "must be a non-empty string")
        proof = opt_in.get("proof_url")
        if _text(proof) and not URL_RE.fullmatch(proof):
            issue("opt_in_evidence.proof_url", "must be a public HTTPS URL")

    autoresponses = packet.get("autoresponses")
    if not isinstance(autoresponses, dict):
        issue("autoresponses", "must be an object")
    else:
        for key in ("optinMessage", "optoutMessage", "helpMessage", "optinKeywords", "optoutKeywords", "helpKeywords"):
            if not _text(autoresponses.get(key)):
                issue(f"autoresponses.{key}", "must be a non-empty string")
        if "STOP" not in str(autoresponses.get("optoutKeywords", "")).upper().split(","):
            issue("autoresponses.optoutKeywords", "must include STOP")
        if "HELP" not in str(autoresponses.get("helpKeywords", "")).upper().split(","):
            issue("autoresponses.helpKeywords", "must include HELP")

    use_cases = packet.get("use_cases")
    if not isinstance(use_cases, list) or not use_cases:
        issue("use_cases", "must be a non-empty array")
    else:
        for index, use_case in enumerate(use_cases):
            field = f"use_cases[{index}]"
            if not isinstance(use_case, dict):
                issue(field, "must be an object")
                continue
            if use_case.get("messaging_use_case_us") not in USE_CASES:
                issue(f"{field}.messaging_use_case_us", f"must be one of {sorted(USE_CASES)}")
            samples = use_case.get("sample_messages")
            if not isinstance(samples, list) or not 1 <= len(samples) <= 5:
                issue(f"{field}.sample_messages", "must contain 1–5 samples")
            elif any(not _text(sample) or len(sample) > 1024 for sample in samples):
                issue(f"{field}.sample_messages", "samples must be non-empty strings of at most 1,024 characters")
    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", type=Path)
    args = parser.parse_args(argv)
    try:
        packet = json.loads(args.packet.read_text(encoding="utf-8"))
    except OSError as exc:
        print(f"{args.packet}: <file>: {exc}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"{args.packet}: <file>: invalid JSON ({exc})", file=sys.stderr)
        return 1
    issues = validate(packet, str(args.packet))
    if issues:
        print("\n".join(issues), file=sys.stderr)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
