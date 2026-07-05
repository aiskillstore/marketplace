---
name: gdpr-purge-log-template
description: Honest, minimal schema for memory/audits/gdpr-purges.md entries — a human-readable record of erasure requests, not an audit-grade erasure proof.
type: reference
---

# Purge Log — `memory/audits/gdpr-purges.md`

An append-only, human-readable record of every Art 17 / CCPA §1798.105 erasure request
handled by `memory-management`. It documents **what was requested and what the working tree
edit did** — it is NOT a cryptographic or audit-grade proof of complete erasure.

> **Read this first — scope honesty.** A purge edits the **working tree** only. If `memory/` is
> under version control, the subject still exists in git history; verify with
> `git log -S"<name>" -- memory/` and use `git filter-repo` for true history erasure (the user's
> responsibility, out of scope here). This log does not, and cannot, prove that the subject is gone
> everywhere. Do not present it as such to a data subject or auditor. There is no salted-fingerprint
> or reingest-blocking mechanism in the hooks; do not record fields that imply one exists.

## Entry schema

Append-only YAML list, newest at the bottom. One entry per purge. **Never store the raw subject** —
use a stable redacted label.

```yaml
- date: 2026-06-10                 # date the purge was run
  redacted_label: "Subject-A1B2"   # stable non-identifying label; NEVER the raw name
  legal_basis: art_17_request      # art_17_request | ccpa_1798.105 | proactive_minimization
  action: anonymize                # delete | anonymize
  scope:                           # working-tree files edited
    - memory/hot-cache.md
    - memory/entities/acme-corp.md
  files_modified: 9                # how many files were changed
  working_tree_only: true          # always true — git history is NOT touched by this flow
  note: "Replaced subject string with [REDACTED] across 14 lines. Advised user to run git filter-repo for history."
```

## Required fields

`date`, `redacted_label` (never raw), `legal_basis`, `action`, `scope`, `working_tree_only: true`.
Everything else is optional context. Keep `note` free of the raw subject name.

## Cross-references

- [memory-management SKILL.md §GDPR / Privacy Compliance](../SKILL.md) — purge procedure and its honest limitation
- [references/skill-contract.md](../../../references/skill-contract.md) — Write Paths table
