#!/usr/bin/env python3
"""Offline preflight checks for a Sent v3 integration.

Validates the things that break integrations before any network call is made:
recipient formatting, send-payload shape, channel-array intent, idempotency-key
format, batch sizing against the documented pacing budget, and the retry
classification of an error code.

Usage
-----
Run the built-in synthetic fixtures::

    python3 preflight.py --self-test

Check a send payload written to a file::

    python3 preflight.py --payload-file send.json

Classify an error code for retry behavior::

    python3 preflight.py --classify-error 409:CONFLICT_001

Exit codes: 0 all checks passed, 1 one or more findings, 3 usage error.
"""

from __future__ import annotations

import argparse
import json
import re
import sys

E164 = re.compile(r"^\+[1-9]\d{1,14}$")
IDEMPOTENCY_KEY = re.compile(r"^[A-Za-z0-9_-]{1,255}$")
VALID_CHANNELS = {"sent", "sms", "whatsapp", "rcs"}
MAX_RECIPIENTS_PER_REQUEST = 1000
STANDARD_RATE_LIMIT_PER_MINUTE = 200
SENSITIVE_RATE_LIMIT_PER_MINUTE = 10

TERMINAL_FAMILIES = {"AUTH", "VALIDATION", "RESOURCE"}
RETRYABLE_FAMILIES = {"SERVICE", "INTERNAL"}

EXIT_OK = 0
EXIT_FINDINGS = 1
EXIT_USAGE = 3


def check_recipients(recipients: object) -> list[str]:
    """Validate the `to` array."""
    findings: list[str] = []
    if not isinstance(recipients, list) or not recipients:
        return ["'to' must be a non-empty array of E.164 phone numbers"]
    for value in recipients:
        if not isinstance(value, str) or not E164.match(value):
            findings.append(f"recipient {value!r} is not E.164 (leading '+', country code, digits only)")
    if len(recipients) > MAX_RECIPIENTS_PER_REQUEST:
        findings.append(
            f"{len(recipients)} recipients exceeds the {MAX_RECIPIENTS_PER_REQUEST}-recipient per-request limit"
        )
    return findings


def check_channels(channels: object) -> list[str]:
    """Validate the `channel` array and flag broadcast intent."""
    if channels is None:
        return []
    findings: list[str] = []
    if not isinstance(channels, list):
        return ["'channel' must be an array when present"]
    for value in channels:
        if value not in VALID_CHANNELS:
            findings.append(f"channel {value!r} is invalid; allowed values are {sorted(VALID_CHANNELS)}")
    explicit = [value for value in channels if value != "sent"]
    if len(explicit) > 1:
        findings.append(
            "multiple explicit channels broadcast rather than fall back: one message and one charge is created "
            "per (recipient, channel) pair. Omit 'channel' or use ['sent'] for automatic routing with reroute"
        )
    if "sent" in channels and len(channels) > 1:
        findings.append("'sent' combined with an explicit channel is ambiguous; use one or the other")
    return findings


def check_content(payload: dict) -> list[str]:
    """Validate that exactly one content source is present."""
    has_template = isinstance(payload.get("template"), dict)
    has_text = isinstance(payload.get("text"), str) and payload["text"].strip() != ""
    if has_template and has_text:
        return ["provide either 'template' or 'text', not both"]
    if not has_template and not has_text:
        return ["provide 'template' or 'text' as the message content"]
    if has_template:
        template = payload["template"]
        if not template.get("id") and not template.get("name"):
            return ["'template' requires 'id' or 'name'"]
        if template.get("id") and template.get("name"):
            return ["'template.id' and 'template.name' are mutually exclusive"]
        parameters = template.get("parameters")
        if parameters is not None and not isinstance(parameters, dict):
            return ["'template.parameters' must be an object of string values"]
        if isinstance(parameters, dict) and any(not isinstance(value, str) for value in parameters.values()):
            return ["every 'template.parameters' value must be a string"]
    return []


def check_idempotency_key(key: object) -> list[str]:
    """Validate an Idempotency-Key header value."""
    if key is None:
        return ["no Idempotency-Key supplied; a timeout retry can produce a duplicate send"]
    if not isinstance(key, str) or not IDEMPOTENCY_KEY.match(key):
        return ["Idempotency-Key must be 1-255 characters of letters, digits, hyphens, or underscores"]
    return []


def estimate_batches(recipient_count: int, channel_count: int = 1) -> dict[str, int]:
    """Return message and request estimates for a bulk send."""
    channel_count = max(1, channel_count)
    messages = recipient_count * channel_count
    requests = -(-recipient_count // MAX_RECIPIENTS_PER_REQUEST)
    minutes = -(-requests // STANDARD_RATE_LIMIT_PER_MINUTE)
    return {
        "messages_created": messages,
        "requests_required": requests,
        "minimum_minutes_at_rate_limit": minutes,
    }


def classify_error(status: int, code: str) -> tuple[str, str]:
    """Return (classification, guidance) for a Sent error response."""
    family = code.split("_", 1)[0].upper() if code else ""
    if status == 429:
        return "retry", "honor Retry-After, then use jittered exponential backoff; stop if the credential is locked"
    if code.upper() == "CONFLICT_001":
        return "retry-once", "a concurrent duplicate is in flight; pause, then retry the same Idempotency-Key once"
    if code.upper() == "SERVICE_001":
        return "retry", "the idempotency store was unavailable and the request was deliberately not executed"
    if family in RETRYABLE_FAMILIES or 500 <= status < 600:
        return "retry", "exponential backoff with jitter and a bounded ceiling"
    if family == "AUTH":
        return "terminal", "stop immediately; ten consecutive auth failures lock the credential with escalating lockout"
    if family in TERMINAL_FAMILIES:
        return "terminal", "fix the request or the referenced resource; retrying reproduces the same result"
    if family == "BUSINESS":
        return "conditional", (
            "an account or policy precondition; on POST /v3/messages the send is accepted with 202 and the "
            "affected messages finalize as BLOCKED or FILTERED, so resolve the condition before resending"
        )
    return "unknown", "treat as terminal until classified; log meta.request_id and inspect error.doc_url"


def check_payload(payload: dict, idempotency_key: str | None = None) -> list[str]:
    """Run every payload check and return the accumulated findings."""
    findings: list[str] = []
    findings.extend(check_recipients(payload.get("to")))
    findings.extend(check_channels(payload.get("channel")))
    findings.extend(check_content(payload))
    findings.extend(check_idempotency_key(idempotency_key))
    return findings


def _self_test() -> int:
    failures: list[str] = []

    good = {
        "to": ["+14155551234"],
        "template": {"name": "order_confirmation", "parameters": {"order_id": "12345"}},
    }
    if check_payload(good, "order-12345-confirmation"):
        failures.append("a well-formed payload with an idempotency key must produce no findings")

    if not check_recipients(["4155551234"]):
        failures.append("a non-E.164 recipient must be flagged")
    if not check_recipients([]):
        failures.append("an empty recipient list must be flagged")
    if not check_recipients(["+1415555%s" % "1" * 15]):
        failures.append("an over-long number must be flagged")

    broadcast = check_channels(["whatsapp", "sms"])
    if not any("broadcast" in finding for finding in broadcast):
        failures.append("a multi-channel array must be flagged as broadcast, not fallback")
    if check_channels(["sent"]) or check_channels(None):
        failures.append("automatic routing must produce no channel findings")
    if not check_channels(["telegram"]):
        failures.append("an unsupported channel value must be flagged")

    if not check_content({"to": ["+14155551234"]}):
        failures.append("missing content must be flagged")
    if not check_content({"template": {"id": "x", "name": "y"}}):
        failures.append("template id and name together must be flagged")
    if not check_content({"template": {"name": "t"}, "text": "hello"}):
        failures.append("template and text together must be flagged")
    if not check_content({"template": {"name": "t", "parameters": {"count": 2}}}):
        failures.append("non-string template parameter values must be flagged")

    if not check_idempotency_key(None):
        failures.append("a missing idempotency key must be flagged")
    if not check_idempotency_key("bad key!"):
        failures.append("an invalid idempotency key must be flagged")

    estimate = estimate_batches(2500, 2)
    if estimate != {"messages_created": 5000, "requests_required": 3, "minimum_minutes_at_rate_limit": 1}:
        failures.append(f"batch estimation drifted: {estimate}")

    expectations = {
        (429, "BUSINESS_009"): "retry",
        (409, "CONFLICT_001"): "retry-once",
        (503, "SERVICE_001"): "retry",
        (401, "AUTH_002"): "terminal",
        (400, "VALIDATION_004"): "terminal",
        (404, "RESOURCE_001"): "terminal",
        (500, "INTERNAL_001"): "retry",
        (402, "BUSINESS_003"): "conditional",
    }
    for (status, code), expected in expectations.items():
        actual, _ = classify_error(status, code)
        if actual != expected:
            failures.append(f"{status} {code} classified as {actual}, expected {expected}")

    if SENSITIVE_RATE_LIMIT_PER_MINUTE >= STANDARD_RATE_LIMIT_PER_MINUTE:
        failures.append("the sensitive tier must be lower than the standard tier")

    for failure in failures:
        print(f"FAIL: {failure}", file=sys.stderr)
    if failures:
        return EXIT_FINDINGS
    print("preflight self-test passed: 20 checks")
    return EXIT_OK


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Offline preflight checks for a Sent v3 integration.")
    parser.add_argument("--self-test", action="store_true", help="run synthetic fixtures and exit")
    parser.add_argument("--payload-file", help="path to a JSON send payload to check")
    parser.add_argument("--idempotency-key", help="the Idempotency-Key that will be sent with the payload")
    parser.add_argument("--estimate", type=int, metavar="RECIPIENTS", help="estimate messages, requests, and pacing")
    parser.add_argument("--channels", type=int, default=1, help="number of channels used with --estimate")
    parser.add_argument("--classify-error", metavar="STATUS:CODE", help="classify an error response for retry")
    args = parser.parse_args(argv)

    if args.self_test:
        return _self_test()

    if args.classify_error:
        try:
            status_text, _, code = args.classify_error.partition(":")
            classification, guidance = classify_error(int(status_text), code)
        except ValueError:
            print("error: --classify-error expects STATUS:CODE, for example 429:BUSINESS_009", file=sys.stderr)
            return EXIT_USAGE
        print(f"{args.classify_error} -> {classification}: {guidance}")
        return EXIT_OK

    if args.estimate is not None:
        for key, value in estimate_batches(args.estimate, args.channels).items():
            print(f"{key}: {value}")
        return EXIT_OK

    if not args.payload_file:
        parser.error("provide --payload-file, --estimate, --classify-error, or --self-test")

    try:
        with open(args.payload_file, encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: could not read payload: {exc}", file=sys.stderr)
        return EXIT_USAGE

    if not isinstance(payload, dict):
        print("error: payload must be a JSON object", file=sys.stderr)
        return EXIT_USAGE

    findings = check_payload(payload, args.idempotency_key)
    if payload.get("sandbox") is True:
        print("note: sandbox is true, so this request validates and authenticates without executing")
    if not findings:
        print("payload passed all preflight checks")
        return EXIT_OK
    for finding in findings:
        print(f"- {finding}")
    return EXIT_FINDINGS


if __name__ == "__main__":
    raise SystemExit(main())
