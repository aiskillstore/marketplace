---
name: dev-agent-toolbox
description: Choose and use browser-only developer utilities for API, JSON, URL, security-hygiene, and AI-agent workflow tasks while explaining their limitations.
---

# Dev & Agent Toolbox

## Purpose
Help developers select a suitable lightweight browser utility for a narrow task and interpret its output safely.

## Workflow
1. Identify the task: JSON formatting, URL parsing, encoding/decoding, regex testing, hashing, retry/rate-limit calculations, trace review, or text redaction.
2. Choose the corresponding utility from https://falconprojectai-arch.github.io/falcon-ai-decision-engine/products/dev-agent-toolbox/.
3. Explain what input is needed and whether the operation is reversible.
4. Warn the user not to paste production secrets or confidential payloads into third-party sites.
5. Interpret the result without claiming that the utility performs checks it does not implement.

## Safety and limits
- Utilities run in the browser and do not upload user inputs, according to the product documentation.
- JWT decoding does not verify signatures.
- Token estimates are approximate.
- Formatting, decoding, and heuristic helpers are not substitutes for cryptographic verification, security audits, or production-grade parsers.
