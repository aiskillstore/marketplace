---
name: fix-sentry-issues
description: Use Sentry MCP to discover, triage, and fix production issues with root-cause analysis. Use when asked to fix Sentry issues, triage production errors, investigate error spikes, or clean up Sentry noise. Requires Sentry MCP server. Triggers on "fix sentry", "triage errors", "production bugs", "sentry issues".
---

# Fix Sentry Issues

## Philosophy

**The Sentry error is not the problem. It's a signal.**

Your goal is not to close the Sentry issue. Your goal is to discover the root cause, understand what's wrong with the application, and fix the underlying defect. Closing the Sentry issue is a side effect of doing that correctly.

Ask **"Why does this fail?"** — not **"How do I make Sentry quiet?"** Never treat log level changes as fixes. A fallback path means degraded user experience; trace why the primary path fails and fix it upstream.

## Anti-patterns (do not do these)

- **Batch-classifying as "expected" without investigation.** Seeing a fallback does NOT mean you understand the failure. Trace the full input path.
- **Treating "has a fallback" as "not a problem."** Why does the primary path fail? Can we prevent it upstream?
- **Combining multiple issues into one PR.** Each has its own root cause. Fix individually (except when investigation proves identical cause).
- **Throwing away error details.** Never remove `error` from `catch (error)` or strip status codes. That data is how you understand failures.
- **Deciding the fix during triage.** Classify as "Investigate" or "Ignore" only. You don't know the fix until investigation is complete.

**Log level downgrade is valid ONLY for genuinely expected states** (e.g., optional column missing, resource deleted) — NOT for failures with fallbacks.

## Phase 1: Discover & Triage

Use Sentry MCP (`ToolSearch` first to load tools): `find_organizations` → `find_projects` → `search_issues` with `naturalLanguageQuery: "all unresolved issues sorted by events"`.

Build a triage table. Action = **Investigate** or **Ignore** only:

| ID | Title | Events | Action | Reason |
|----|-------|--------|--------|--------|
| PROJ-A | Error in save | 14 | Investigate | User-facing save failure |
| PROJ-B | GM_register... | 3 | Ignore | Greasemonkey extension |

**Investigate:** multiple events, degraded user experience, high-volume warnings, recurring on every run.
**Ignore:** browser extension code, `ChunkLoadError` (self-resolving), single-event transients, already fixed.

Apply: `mcp__sentry__update_issue(..., status: "ignored")` or `status: "resolved"` for already-fixed.

## Phase 2: Investigate (one issue at a time)

Work through these steps **in order**. Do not skip or batch issues.

1. **Pull event-level data** — Issue summaries hide details. Use `get_issue_details` and `search_issue_events` with `naturalLanguageQuery: "all events with extra data"`. Extract: URLs, params, stack traces, status codes, timestamps.

2. **Cross-reference Axiom** — Events have `traceId`. `axiom query "['shiori-events'] | where traceId == '<traceId>'" -f json` for surrounding context (authMethod, client_version, request metadata).

3. **Read the failing code path** — Follow the stack trace. Read every file. Understand before proposing changes.

4. **Trace the input path upstream** *(most often skipped, most important)* — What data reaches the failing function? Should it have reached this path at all? Is there a missing filter? Is the input wrong (binary URL, redirect, bad format)? Can we prevent bad inputs upstream?

5. **Reproduce** — Use actual failing inputs from Sentry. Call the function with exact data. `fetch()` the URLs that timed out. Verify your understanding.

6. **Identify root cause** — Why does this input fail? Why does it reach this path? What's the right fix? (e.g., "Filter binary URLs before Firecrawl" — not "suppress the log")

| Pattern | Real Fix |
|---------|----------|
| External API fails on certain URLs | Filter/validate inputs before sending |
| Timeout | Investigate what's slow; adjust timeout or input size |
| DB "invalid json" | Sanitize before insert |
| Stale reference on cron | Detect staleness, auto-clean |

## Phase 3: Fix

One branch per issue. `git checkout main && git pull && git checkout -b fix/<descriptive-name>`

- **Tests first** — Use data from actual Sentry events. Test fails before fix, passes after.
- **Implement** — Fix the root cause, not the symptom. If the fix is primarily a log level change, STOP: did you investigate why it fails, or just suppress?
- **Verify** — Tests pass, lint passes, fix handles actual failing inputs.
- **PR** — Include **Root cause** (upstream reason) and **Fix** (what changed and why it prevents the failure). Resolve in Sentry only after merge.
