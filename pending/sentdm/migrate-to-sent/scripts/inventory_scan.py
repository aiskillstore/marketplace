#!/usr/bin/env python3
"""Scan a repository for incumbent CPaaS usage that a Sent migration must address.

Reports each finding with a migration classification so the output can be used
directly as the phase-2 rewrite list.

Usage
-----
    python3 inventory_scan.py --self-test
    python3 inventory_scan.py --path /path/to/repo
    python3 inventory_scan.py --path /path/to/repo --format json

Exit codes: 0 no findings, 1 findings reported, 3 usage error.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, asdict

EXIT_CLEAN = 0
EXIT_FINDINGS = 1
EXIT_USAGE = 3

SKIP_DIRS = {
    ".git", "node_modules", "vendor", "dist", "build", "target", ".venv", "venv",
    "__pycache__", ".next", ".gradle", ".idea", ".mypy_cache", ".pytest_cache", "coverage",
}
SCAN_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".java", ".kt", ".cs", ".php", ".rb",
    ".yml", ".yaml", ".json", ".tf", ".sh", ".md",
}
MAX_FILE_BYTES = 2_000_000


@dataclass(frozen=True)
class Rule:
    rule_id: str
    provider: str
    pattern: str
    classification: str
    guidance: str


RULES: tuple[Rule, ...] = (
    Rule(
        "ordered-channel-array", "sent",
        r"""['\"]channel['\"]\s*:\s*\[\s*['\"](?:sms|whatsapp|rcs)['\"]\s*,\s*['\"](?:sms|whatsapp|rcs)['\"]""",
        "rewrite",
        "Multiple explicit channels broadcast rather than fall back. Omit 'channel' or use ['sent'].",
    ),
    Rule(
        "twilio-sdk", "twilio", r"\b(?:from\s+twilio|require\(['\"]twilio|com\.twilio|Twilio\.Rest|twilio-go)\b",
        "rewrite", "Replace the Twilio client with a Sent SDK client reading SENT_DM_API_KEY.",
    ),
    Rule(
        "twilio-messages-endpoint", "twilio", r"api\.twilio\.com/2010-04-01/Accounts/[^/]*/Messages",
        "rewrite", "Replace with POST /v3/messages using the flat JSON body.",
    ),
    Rule(
        "twilio-signature", "twilio", r"X-Twilio-Signature|validateRequest|RequestValidator",
        "new_code", "Twilio signs HMAC-SHA1 over URL plus sorted params. Sent needs a new verifier.",
    ),
    Rule(
        "twilio-messaging-service", "twilio", r"MessagingServiceSid|messaging_service_sid",
        "rewrite", "Sender pools and sticky sender are platform routing concerns in Sent, not request fields.",
    ),
    Rule(
        "twilio-optout-code", "twilio", r"\b21610\b",
        "rewrite", "Opted-out sends are accepted with 202 and finalize as FILTERED, not as a numeric error.",
    ),
    Rule(
        "twilio-channel-prefix", "twilio", r"['\"]whatsapp:\+?",
        "rewrite", "Channel is selected by the 'channel' array in Sent, not by a recipient prefix.",
    ),
    Rule(
        "sinch-conversation", "sinch", r"conversation\.api\.sinch\.com|messages:send|sinch-webhook-signature",
        "rewrite", "Replace channel-priority ordering with Sent automatic routing.",
    ),
    Rule(
        "infobip-endpoint", "infobip", r"[a-z0-9-]+\.api\.infobip\.com|infobip-api",
        "rewrite", "Replace with POST /v3/messages; Sending Strategies have no caller-side equivalent.",
    ),
    Rule(
        "infobip-blocklist", "infobip", r"blocklist|do-not-contact|dnc",
        "rewrite", "Reconcile into Sent consent as a channel-agnostic opt_out on the contact.",
    ),
    Rule(
        "vonage-failover", "vonage", r"['\"]failover['\"]\s*[:=]\s*\[",
        "rewrite", "An ordered failover array must become Sent automatic routing.",
    ),
    Rule(
        "vonage-sdk", "vonage", r"\b(?:@vonage/|nexmo|vonage-)\b",
        "rewrite", "Replace the Vonage client; Sent authenticates with x-api-key, not a JWT bearer.",
    ),
    Rule(
        "bird-fallback", "bird", r"messagebird|bird-signature|messagebird-signature",
        "rewrite", "MessageBird signs over a body hash; the verifier is not portable to Sent.",
    ),
    Rule(
        "generic-fallback-object", "any", r"['\"](?:fallback|failover)['\"]\s*[:=]",
        "rewrite", "Caller-supplied fallback has no Sent equivalent; automatic routing performs it.",
    ),
    Rule(
        "positional-template-var", "any", r"\{\{\s*[1-9][0-9]?\s*\}\}",
        "rewrite", "Sent template parameters are a named map, not positional placeholders.",
    ),
    Rule(
        "bearer-auth-to-provider", "any", r"Authorization['\"]?\s*[:=]\s*['\"]?Bearer\s",
        "review", "Direct Sent REST calls use x-api-key; keep Bearer where an app proxy, MCP OAuth flow, or incumbent still requires it.",
    ),
    Rule(
        "provider-status-branch", "any",
        r"['\"](?:undelivered|accepted|sending)['\"]",
        "rewrite", "Map incumbent status strings onto Sent statuses, adding FILTERED, BLOCKED, and SCHEDULED.",
    ),
    Rule(
        "application-keyword-matcher", "any",
        r"(?:==|===|\.equals\(|\.includes\(|\bin\s)\s*['\"](?:STOP|UNSUBSCRIBE|CANCEL|UNSTOP)['\"]",
        "review", "Keep exact matching only to mirror local consent evidence; do not write consent to Sent a second time.",
    ),
    Rule(
        "idempotency-key-present", "sent", r"Idempotency-Key",
        "informational", "Idempotency key usage found; confirm keys are deterministic rather than random.",
    ),
)

COMPILED = tuple((rule, re.compile(rule.pattern, re.IGNORECASE)) for rule in RULES)


@dataclass
class Finding:
    path: str
    line: int
    rule_id: str
    provider: str
    classification: str
    guidance: str
    excerpt: str


def redact_excerpt(line: str) -> str:
    """Mask credential-like literals before reporting a matched source line."""
    line = re.sub(
        r"(?i)(authorization[^\n]{0,24}bearer\s+)([^\s'\",;}]+)",
        r"\1<redacted>",
        line,
    )
    line = re.sub(
        r"(?i)\b(api[_-]?key|auth[_-]?token|access[_-]?token|secret|password)(\s*[:=]\s*)([^\s,;}]+)",
        r"\1\2<redacted>",
        line,
    )
    return line


def scan_text(text: str, path: str = "<memory>") -> list[Finding]:
    """Scan a blob of text and return findings."""
    findings: list[Finding] = []
    for number, line in enumerate(text.splitlines(), start=1):
        if len(line) > 2000:
            line = line[:2000]
        for rule, regex in COMPILED:
            if regex.search(line):
                findings.append(
                    Finding(
                        path=path,
                        line=number,
                        rule_id=rule.rule_id,
                        provider=rule.provider,
                        classification=rule.classification,
                        guidance=rule.guidance,
                        excerpt=redact_excerpt(line.strip())[:200],
                    )
                )
    return findings


def scan_path(root: str) -> list[Finding]:
    """Walk a directory tree and scan eligible files."""
    findings: list[Finding] = []
    for directory, subdirs, files in os.walk(root):
        subdirs[:] = [name for name in subdirs if name not in SKIP_DIRS and not name.startswith(".")]
        for filename in files:
            if filename.startswith(".env"):
                continue
            extension = os.path.splitext(filename)[1].lower()
            if extension not in SCAN_EXTENSIONS:
                continue
            full = os.path.join(directory, filename)
            try:
                if os.path.getsize(full) > MAX_FILE_BYTES:
                    continue
                with open(full, encoding="utf-8", errors="replace") as handle:
                    text = handle.read()
            except OSError:
                continue
            findings.extend(scan_text(text, os.path.relpath(full, root)))
    return findings


def summarize(findings: list[Finding]) -> dict[str, int]:
    """Count findings per classification."""
    counts: dict[str, int] = {}
    for finding in findings:
        counts[finding.classification] = counts.get(finding.classification, 0) + 1
    return counts


def _self_test() -> int:
    failures: list[str] = []

    sample = """
    const client = require('twilio')(sid, token);
    await client.messages.create({ to, from, body });
    if (status === 'undelivered') retry();
    if (error.code === 21610) suppress();
    payload = {"channel": ["whatsapp", "sms"], "to": ["+14155551234"]}
    body = {"failover": [{"channel": "sms"}]}
    template = "Hello {{1}}, your order {{2}} shipped"
    headers = {"Authorization": "Bearer " + token}
    if (text.trim().toUpperCase() === 'STOP') { optOut(); }
    """
    found = {finding.rule_id for finding in scan_text(sample)}
    expected = {
        "twilio-sdk",
        "provider-status-branch",
        "twilio-optout-code",
        "ordered-channel-array",
        "vonage-failover",
        "generic-fallback-object",
        "positional-template-var",
        "bearer-auth-to-provider",
        "application-keyword-matcher",
    }
    missing = expected - found
    if missing:
        failures.append(f"rules failed to fire: {sorted(missing)}")

    clean = 'payload = {"to": ["+14155551234"], "template": {"name": "t", "parameters": {"a": "b"}}}\n'
    if scan_text(clean):
        failures.append("a correct Sent payload must produce no findings")

    single = 'payload = {"channel": ["sms"]}\n'
    if any(f.rule_id == "ordered-channel-array" for f in scan_text(single)):
        failures.append("a single-channel array must not be flagged as broadcast")

    counts = summarize(scan_text(sample))
    if counts.get("rewrite", 0) < 5 or counts.get("review", 0) != 2:
        failures.append(f"classification summary drifted: {counts}")

    for failure in failures:
        print(f"FAIL: {failure}", file=sys.stderr)
    if failures:
        return EXIT_FINDINGS
    print("inventory_scan self-test passed: 4 checks")
    return EXIT_CLEAN


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scan a repository for incumbent CPaaS usage.")
    parser.add_argument("--self-test", action="store_true", help="run synthetic fixtures and exit")
    parser.add_argument("--path", help="repository root to scan")
    parser.add_argument("--format", choices=("text", "json"), default="text", help="output format")
    args = parser.parse_args(argv)

    if args.self_test:
        return _self_test()
    if not args.path:
        parser.error("provide --path or --self-test")
    if not os.path.isdir(args.path):
        print(f"error: {args.path} is not a directory", file=sys.stderr)
        return EXIT_USAGE

    findings = scan_path(args.path)

    if args.format == "json":
        print(json.dumps({"summary": summarize(findings), "findings": [asdict(f) for f in findings]}, indent=2))
    else:
        if not findings:
            print("no incumbent CPaaS usage detected")
        for finding in findings:
            print(f"{finding.path}:{finding.line} [{finding.classification}/{finding.provider}] {finding.rule_id}")
            print(f"    {finding.excerpt}")
            print(f"    -> {finding.guidance}")
        if findings:
            print("\nsummary: " + ", ".join(f"{k}={v}" for k, v in sorted(summarize(findings).items())))

    return EXIT_FINDINGS if findings else EXIT_CLEAN


if __name__ == "__main__":
    raise SystemExit(main())
