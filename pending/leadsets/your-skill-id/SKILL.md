---
name: your-skill-id
description: "What the skill does and when an agent should use it, in third person, 200 to 450 characters. End with a sentence like: Use when someone asks to ..."
license: MIT
metadata:
  title: "Your skill title"
  category: "Prospecting"
  outcome: "Find new prospects"
  tools: [search_people, enrich_person]
  version: "1.0"
  author: "Your name or GitHub handle"
  homepage: https://www.leadsets.ai/skills?utm_source=github&utm_medium=leadsets-skills&utm_campaign=template
---

# Your skill title

Two or three sentences: what it produces and who it is for.

**Category:** Prospecting · **Outcome:** Find new prospects · **Tools:** `search_people`, `enrich_person`

## Requirements

- The Leadsets MCP server connected to your agent: `https://mcp.leadsets.ai` ([setup](https://www.leadsets.ai/docs/mcp?utm_source=github&utm_medium=leadsets-skills&utm_campaign=template)), or a Leadsets API key for the REST API.
- A Leadsets account. The free plan includes 1,000 records, no card ([get a key](https://www.leadsets.ai/signup?utm_source=github&utm_medium=leadsets-skills&utm_campaign=template)).

## Rules for every run

These apply on top of the steps below.

- **Pages, not giant calls.** `search_people` and `search_companies` return at most 100 records per call (`limit` 1 to 100). Page with `next_cursor` for more.
- **Probe before spending.** Run a large search with `limit: 1` first and check the record really matches (company, title, size, country). If it doesn't, fix the filters before spending more records.
- **Rate limits.** On `429 window_full` or `too_many_concurrent`: if `Retry-After` is under 60 seconds, wait and retry the same call once. Otherwise stop, save what's done, and tell the user what's left and when the window resets (`resets_at`). On `weekly_limit`, stop and report where to resume. On `402 free_records_exhausted`, stop and ask the user to upgrade.
- **Retries never double-count.** Over MCP, just retry the same call. Over the REST API, send an `Idempotency-Key` on every paid call and reuse it on retries.
- **Only confirmed emails are verified.** Treat an email as verified only when `enrich_person` or `verify_email` returned `status: verified` for it. Search listings and old CRM values don't count. Keep catch-all, unknown and invalid separate, never rounded up.
- **No matches, no records.** Empty results and `404 not_found` cost no records. Mark them clearly and move on; don't guess.
- **Use the defaults.** When the user doesn't say, use the defaults in "What you give it" instead of asking. Ask only when an input is genuinely missing or ambiguous, and only one question at a time.

## When to use

- A request phrasing that should trigger this skill
- Another situation where it applies

## What you give it

- **Input name**: what it is, and its default.
- **Another input** (optional): what it is.

## Steps

1. **Check limits** · `get_usage`
   Confirm there are enough records left for the run before spending any.
2. **Next step** · `search_people`
   Exactly what to call, with which arguments, and what to check before moving on.

## Checks before returning

- A check the agent runs before handing back results

## Output

The exact shape of the result: columns or fields, and how catch-all, unknown and invalid emails are handled.

## Example

> A realistic request someone would type

```
✓ What happened  ·  ✓ counts
→ Where the result went
```

Illustrative output.

## Cost and limits

How records, requests and scrape units are spent, and how the skill stays inside limits.

## What it doesn't do

- Something it deliberately leaves out
