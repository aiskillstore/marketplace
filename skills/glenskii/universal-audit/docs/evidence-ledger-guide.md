# Evidence Ledger Guide

## Purpose

The evidence ledger is the audit's factual record. It separates what was observed from the interpretation, score, finding, and release decision that follow. Record enough detail for a qualified reviewer to locate and assess the same evidence without repeating the whole audit.

## One observation per record

Create a separate record when the location, method, control, or result changes. A single record may support more than one control only when the same observation directly proves each one. Link the records rather than copying the same text into several entries.

Each record needs:

- A stable evidence ID.
- The relevant control ID or IDs.
- The observation time and environment.
- The exact location, such as file and line, endpoint, configuration key, build identifier, or report path.
- The collection method and tool version when relevant.
- A short, sanitized excerpt or result.
- The limitation, including access or environment conditions that could affect the result.

## Write observations, not conclusions

Write `Response returned 401 without a session token` rather than `Authentication is secure`. The first statement is evidence. The second requires broader evidence and a control-level judgment.

Do not convert a missing artifact into a failed control without checking whether the control applies and whether another permitted source can verify it. When evidence is unavailable, record the gap and mark the control UNVERIFIED.

## Sanitize before saving

Do not place secrets, access tokens, personal data, session identifiers, production credentials, or working exploit payloads in the ledger. Replace sensitive values with a clear marker and preserve only the details needed to understand the observation.

Example:

```text
EVD-AUTH-014
Control: SEC-AUTH-003
Location: src/auth/session.py:42
Method: source review at commit 4f8c2d1
Observation: Session cookie is set with HttpOnly and SameSite=Lax. Secure is absent.
Limitation: Local development configuration reviewed. Production response headers were not available.
```

## Challenge the ledger before scoring

Before assigning a status, check that every PASS has affirmative evidence, every FAIL has an observable condition, and every UNVERIFIED item states what would resolve it. Remove duplicate records and reconcile contradictions. The score script calculates arithmetic only. It cannot determine whether the evidence is sufficient.
