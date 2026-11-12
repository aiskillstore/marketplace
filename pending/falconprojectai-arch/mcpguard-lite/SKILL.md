---
name: mcpguard-lite
description: Perform a local, heuristic review of MCP and AI-agent JSON configuration for potentially risky permissions, commands, downloads, and credential patterns.
---

# MCPGuard Lite

## Purpose
Help a developer inspect an MCP or agent configuration and identify patterns that deserve manual security review.

## Workflow
1. Ask for the configuration with secrets removed. Never ask for API keys, tokens, passwords, or production credentials.
2. Identify declared servers, executable commands, arguments, environment variable names, remote endpoints, transport settings, and permission scopes.
3. Flag suspicious patterns such as embedded credential-like values, shell execution, remote downloads, wildcard permissions, insecure transport hints, or unexplained environment references.
4. For each finding, quote only the relevant non-secret fragment, explain why it matters, and suggest a safer verification step.
5. Separate confirmed observations from heuristic warnings and false-positive possibilities.

## Limits and safety
- This is a heuristic checklist, not a complete security audit, malware scanner, sandbox, runtime monitor, or guarantee of safety.
- A clean result does not prove that a configuration is safe; a flagged result is not proof of malicious behavior.
- Do not execute the configuration or download/run referenced code as part of the review.
- Never reproduce secrets in the output. Recommend rotation if a real secret was exposed.
