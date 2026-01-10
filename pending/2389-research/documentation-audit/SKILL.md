---
name: documentation-audit
description: This skill should be used when verifying documentation claims against codebase reality. Triggers on "audit docs", "verify documentation", "check docs", "docs accurate", "documentation drift", "before release", "after refactor", "docs don't match". Uses two-pass extraction with pattern expansion for comprehensive detection.
context: fork
agent: Plan
---

<!-- ABOUTME: Documentation audit skill for verifying claims against codebase -->
<!-- ABOUTME: Uses two-pass extraction with pattern expansion for comprehensive detection -->

# Documentation Audit

Systematically verify claims in documentation against the actual codebase using a two-pass approach.

## Overview

**Core principle:** Low recall is worse than false positives—missed claims stay invisible.

**Two-pass process:**
1. **Pass 1:** Extract and verify claims directly from docs
2. **Pass 2A:** Expand patterns from false claims to find similar issues
3. **Pass 2B:** Compare codebase inventory vs documented items (gap detection)

## Quick Start

1. Identify target docs (user-facing only, skip `plans/`, `audits/`)
2. Note current git commit for report header
3. Run Pass 1 extraction using parallel agents (one per doc)
4. Analyze false claims for patterns
5. Run Pass 2 expansion searches
6. Generate `docs/audits/AUDIT_REPORT_YYYY-MM-DD.md`

## Claim Types

| Type | Example | Verification |
|------|---------|--------------|
| `file_ref` | `scripts/foo.py` | File exists? |
| `config_default` | "defaults to 'AI Radio'" | Check schema/code |
| `env_var` | `STATION_NAME` | In .env.example + code? |
| `cli_command` | `--normalize` flag | Script supports it? |
| `behavior` | "runs every 2 minutes" | Check timers/code |

**Verification confidence:**
- **Tier 1 (auto):** file_ref, config_default, env_var, cli_command
- **Tier 2 (semi-auto):** symbol_ref, version_req
- **Tier 3 (human review):** behavior, constraint

## Pass 2 Pattern Expansion

After Pass 1, analyze false claims and search for similar patterns:

```
Dead script found: diagnose_track_selection.py
  → Search: all script references → Found 8 more dead scripts

Wrong interval: "every 10 seconds"
  → Search: "every \d+ (seconds?|minutes?)" → Found 3 more

Wrong service name: ai-radio-break-gen.service
  → Search: service/timer names → Found naming inconsistencies
```

**Common patterns to always check:**
- Dead scripts: `scripts/*.py` references
- Timer intervals: `every \d+ (seconds?|minutes?)`
- Service names: `ai-radio-*.service`, `*.timer`
- Config vars: `RADIO_*` environment variables
- CLI flags: `--flag` patterns in bash blocks

## Output Format

Generate `docs/audits/AUDIT_REPORT_YYYY-MM-DD.md`:

```markdown
# Documentation Audit Report
Generated: YYYY-MM-DD | Commit: abc123

## Executive Summary
| Metric | Count |
|--------|-------|
| Documents scanned | 12 |
| Claims verified | ~180 |
| Verified TRUE | ~145 (81%) |
| **Verified FALSE** | **31 (17%)** |

## False Claims Requiring Fixes
### CONFIGURATION.md
| Line | Claim | Reality | Fix |
|------|-------|---------|-----|
| 135 | `claude-sonnet-4-5` | Actual: `claude-3-5-sonnet-latest` | Update |

## Pattern Summary
| Pattern | Count | Root Cause |
|---------|-------|------------|
| Dead scripts | 9 | Scripts deleted, docs not updated |

## Human Review Queue
- [ ] Line 436: behavior claim needs verification
```

## Detailed References

For execution checklist and anti-patterns: [checklist.md](checklist.md)
For claim extraction patterns: [extraction-patterns.md](extraction-patterns.md)
