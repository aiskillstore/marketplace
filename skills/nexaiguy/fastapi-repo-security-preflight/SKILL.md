---
name: fastapi-repo-security-preflight
description: 'Automated security scanner for FastAPI repos to detect secrets, SQLi, insecure CORS, and unverified webhooks. Use when: Identify hardcoded credentials and committed .env files before deployment; Catch SQL injection vulnerabilities in raw database queries; Enforce signature verification on all FastAPI webhook endpoints.'
license: MIT
metadata:
  author: Nex AI
  version: '1.0'
  agensi-slug: fastapi-repo-security-preflight
compatibility: Compatible with SKILL.md-compatible agents including Claude Code, Cursor, and Aider.
---

# FastAPI Repo Security Preflight

> Free skill by [Nex AI](https://nex-ai.be). This file is the public guide from [Agensi](https://www.agensi.io/skills/fastapi-repo-security-preflight). Scripts, extension source, and templates from the original package are not in this folder.

## The problem

Manual security audits for FastAPI applications are slow and error-prone. Developers frequently ship code with hardcoded secrets, insecure CORS headers, or unverified webhooks that lead to production vulnerabilities.

## What it does

- Scans code for hardcoded API keys, tokens, and database credentials using AST analysis.
- Detects insecure FastAPI configurations including debug mode, permissive CORS, and broad network binds.
- Identifies SQL injection risks in f-strings and unparameterized execute calls.
- Validates webhook implementations for missing HMAC or signature verification.
- Audits route handlers to ensure Pydantic models are used instead of raw JSON requests.

## Frameworks & tools

FastAPI, Python 3.11+, Pydantic, Uvicorn, and SQL databases using SQLAlchemy or raw SQL drivers.

## Why this beats prompting it yourself

General LLM prompts often miss subtle context-specific vulnerabilities or produce hallucinations. This skill uses deterministic AST scanning to ensure 100% coverage of your codebase without the token costs or privacy risks of sending your entire repo to an external API.

## Use cases

- Running pre-deployment checks to block insecure code from hitting production.
- Auditing legacy FastAPI repositories for hidden secrets or raw SQL injections.
- Integrating into CI/CD pipelines to enforce security standards automatically.
- Ensuring webhook endpoints are properly protected by signature verification.

## Known limitations

Requires Python 3.11 or higher. Scans are limited to static analysis and may not catch vulnerabilities hidden in dynamic string evaluations.

## Example

**Request**

Run a security preflight audit on my FastAPI project in the /backend folder and fail if any high-severity issues are found.

**Result**

Scan complete for /backend. Findings:
- CRITICAL: Hardcoded Postgres URL found in config.py
- HIGH: Webhook at /api/v1/stripe missing signature verification
- HIGH: CORS allow_origins=["*"] with allow_credentials=True
Result: Failed (3 high/critical issues).

## Questions

### What specific security vulnerabilities does this scanner detect?

This skill uses deterministic AST analysis to scan for hardcoded secrets, SQL injection risks in f-strings, insecure CORS policies, and unverified webhook signatures specifically within FastAPI applications.

### What are the technical requirements for running this security preflight?

The skill is designed for Python 3.11+ environments and is optimized for repositories using FastAPI, Pydantic, and SQLAlchemy or raw SQL drivers.

### How does this compare to just asking a general AI model to review my code?

Unlike general LLMs that may hallucinate or miss context, this skill uses static analysis to provide 100% code coverage without the privacy risks or token costs associated with sending your entire codebase to an external API.

### Can I integrate this scanner into my existing CI/CD workflow?

Yes, the skill is built for automation and can be integrated into your CI/CD pipeline to act as a quality gate, blocking insecure code from being deployed to production.

### What is included in the purchase of this skill?

You will receive the full skill package including the scanner logic, integration instructions, and documentation on how to interpret the security reports.

### Are there any known limitations to the scanning process?

Static analysis may not detect vulnerabilities hidden in complex dynamic string evaluations, so we recommend using this as a primary shield alongside standard runtime testing.

---

Built by [Nex AI](https://nex-ai.be). More skills, including the paid catalog: https://www.agensi.io/creators/ch1n4-g3nd4x
