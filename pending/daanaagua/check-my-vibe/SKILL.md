---
name: check-my-vibe
description: Use when a user wants to review the public security posture of an AI-generated, vibe-coded, or deployed website through an authorized passive scan, especially for security headers, exposed secrets, source maps, public files, and deployment mistakes.
---

# Check My Vibe

## Overview

Use Check My Vibe for an authorized, passive review of one public website. Run the real scan at `https://checkmyvibeapp.com/`; never invent results or replace it with an unprotected API call.

## Workflow

1. Get the target URL.
2. Confirm authorization: the user must own the target or have the owner's permission. Stop if authorization is absent.
3. Open `https://checkmyvibeapp.com/` in the available browser.
4. Enter the target URL. The user must complete Turnstile; never bypass or solve it for them.
5. Start the scan and wait for a completed or failed result.
6. Read the score, coverage, limited or partial state, findings, evidence, remediation, limits, and errors.
7. Report only findings supported by the scan evidence.

If no browser is available, give the user the Check My Vibe URL and ask them to paste the resulting report. Do not simulate the scan or call the protected endpoint directly.

## Response Format

- **Summary:** Target, score, coverage, and whether the scan was partial or limited.
- **Fix now:** Critical and high findings, ordered by risk and dependencies.
- **Fix next:** Medium and low findings.
- **Manual review:** Review, not-tested, partial, or weak-evidence items.
- **Top three actions:** The highest-value next steps.
- **Coverage limits:** What this passive public-surface scan did not verify.

## Boundaries

The scan does not prove a site is secure. It does not validate authenticated areas, database authorization, private repositories, business logic, complete dependency risk, or full penetration-test coverage. It does not log in, submit target forms, exploit vulnerabilities, or recursively crawl the site.

Never request passwords, API keys, cookies, or private source code. For verification failure, rate limiting, invalid targets, or safely unreachable pages, explain the error and use the site's normal retry path without changing identity or bypassing controls.

## Common Mistakes

- Treating a public URL as permission to scan it.
- Claiming that a clean report means the site is secure.
- Guessing code locations or vulnerabilities not present in the evidence.
- Bypassing Turnstile, same-origin checks, rate limits, or URL safety rules.
