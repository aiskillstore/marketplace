---
name: security-quick-review
description: Quick security pass over a change or module covering secrets, injection, auth and access checks, unsafe deserialization, dependency and config risks, with evidence. Use before merging code that handles input, auth, files or money.
license: MIT
metadata:
  author: AgentKit Co
  version: "1.0"
---

# Quick security review

This is a fast triage by an AI assistant, not a security audit or penetration test. Say so in the report. Goal: find the likely problems in the code in scope and show evidence for each.

## Scope

State what you reviewed (a diff, a directory, an endpoint) and what you did not. Review the diff plus the code it calls into; a change in one place often breaks assumptions elsewhere.

## Checklist (look at each, report "nothing found" if clean)

1. **Secrets**: keys, tokens, passwords, private keys, connection strings in code, config, tests, fixtures, logs, CI files. Check `git diff` and `git log -p` for the scope too. Never repeat a secret value in the report; give file and line only.
2. **Untrusted input**: every place data comes from a user, a request, a file, a webhook, an environment, a database field that a user can write.
3. **Injection**: SQL built by string concatenation, shell commands with interpolated input, template or HTML output without escaping, path joins with user input (path traversal), regex built from input, SSRF through user-supplied URLs.
4. **Authentication and authorization**: is every new route or action checked for who may call it? Can a user reach another user's data by changing an ID? Are admin paths separate and checked server-side?
5. **Data exposure**: logs or errors that include tokens or personal data, overly broad API responses, debug flags, permissive CORS.
6. **Unsafe operations**: deserialization of untrusted data, `eval`/`exec`, disabled TLS verification, weak randomness for tokens, home-made crypto, unbounded file uploads or request sizes.
7. **Dependencies and config**: new packages (do they exist, are they maintained, is the name suspiciously close to a popular one), pinned versions, lockfile changes, new permissions in CI or cloud config.
8. **Failure behavior**: what happens on error, timeout or malformed input? Does it fail closed?

## Report

```
Scope: <reviewed / not reviewed>
HIGH: <file:line> <issue>. Exploit sketch: <how it could be abused, one or two sentences>. Fix: <specific>
MEDIUM: ...
LOW / hardening: ...
Checked, nothing found: <categories>
Could not verify: <things needing runtime, infra or secrets access>
Limits: automated triage; not an audit; get a human review for anything handling money, health or identity data.
```

## Rules

- Every finding needs file, line and a concrete explanation. No generic OWASP lists.
- Do not attempt to exploit anything against live systems. Reading code and running local tests is fine.
- Rate by realistic impact, not by how scary the category sounds.
- If you find a real secret, tell the user to rotate it; removing it from the code does not remove it from git history.
