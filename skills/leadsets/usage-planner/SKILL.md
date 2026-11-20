---
name: usage-planner
description: "Checks remaining Leadsets limits with get_usage, estimates what a job will spend, and splits big search, enrichment, verification or scrape jobs into batches that fit the five-hour and weekly windows, so runs never stall halfway. Use when someone says \"plan this run\", \"will this fit my limits\", \"how much do I have left\" or \"split this job\", or before any large list job."
license: MIT
metadata:
  title: "Usage planner"
  category: "Usage and ops"
  outcome: "Get verified contact data"
  tools: [get_usage]
  version: "1.0"
  author: Leadsets
  homepage: https://www.leadsets.ai/skills?utm_source=github&utm_medium=leadsets-skills&utm_campaign=usage-planner
---

# Usage planner

Turns a big job, like enriching a 4,000-row CSV or searching for 2,000 prospects, into a batch plan that fits what is left in each Leadsets window and week. Built for GTM engineers and founders running large jobs through an agent who want the run to finish cleanly instead of failing on a 429 halfway through.

**Category:** Usage and ops · **Outcome:** Get verified contact data · **Tools:** `get_usage`

## Requirements

- The Leadsets MCP server connected to your agent: `https://mcp.leadsets.ai` ([setup](https://www.leadsets.ai/docs/mcp?utm_source=github&utm_medium=leadsets-skills&utm_campaign=usage-planner)), or a Leadsets API key for the REST API.
- A Leadsets account. The free plan includes 1,000 records, no card ([get a key](https://www.leadsets.ai/signup?utm_source=github&utm_medium=leadsets-skills&utm_campaign=usage-planner)).

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

- "Will enriching this 4,000-row file fit in my limits?"
- "How much Leadsets usage do I have left, and when does it reset?"
- "Split this job so it doesn't stall halfway."
- Before any other skill runs more than a few hundred search, enrichment or verification calls
- After a run hit a 429 window_full or weekly_limit error and needs to resume

## What you give it

- **The job**: What will run and how big it is, in plain language: for example 4,000 enrich_person calls from a CSV, 1,500 search_people results, 800 verify_email checks or 200 careers pages. Can be another skill's planned run.
- **Timing** (optional): When it needs to finish. Default: as soon as the windows allow, starting now.
- **Headroom** (optional): Records to leave unused in each window for ad hoc work. Default 10% of the window limit.
- **Where the plan goes** (optional): Returned in chat, or written to a markdown file, CSV or Google Sheet through the agent's own connection. Default: in chat.

## Steps

1. **Confirm the job and its meters**
   Restate the job as tool calls and counts. Map each tool to its meter: search_people and search_companies use search records; enrich_person, enrich_company and standalone verify_email use enrichment records; scrape_company and scrape_jobs use scrape units. If the job enriches with enrich_person, do not plan a second verify_email pass on those emails: they are already verified. Ask one question only if the size or tool is unclear.
2. **Read every meter** · `get_usage`
   Call get_usage. Record, for search and enrichment separately, records_5h, requests_5h and records_week as [used, limit], plus resets_at, concurrent_searches and scrape_units. Identify the plan from the limits. If the account is on Free, note the one-time 1,000 records shared across search and enrichment, and that scrape_company and scrape_jobs are not available.
3. **Estimate the spend**
   Estimate records as 1 per record returned for search and enrichment, 1 per email for standalone verify_email and 1 scrape unit per page. Treat the estimate as an upper bound: records count only when data comes back, so misses and empty searches use none, but every call still counts as a request. Check requests too; the request limit is five times the record limit, so it only matters for jobs with many retries or misses.
4. **Check hard stops**
   Before batching, stop and tell the user if: the job exceeds remaining Free records (it will end in 402 free_records_exhausted, so suggest trimming the job or upgrading); the job needs scraping and scrape_units is zero or too low; or the job exceeds the weekly records limit, in which case it must span more than one week or be submitted as an async job. Do not plan around limits with extra accounts or shared keys.
5. **Build the batch plan**
   Size batch 1 to what is left in the current five-hour window minus headroom. Size later batches to the full window limit minus headroom, scheduled at each resets_at. Keep the running total under records_week. For search, keep parallel calls at or below the plan's concurrent search limit (Solo 3, Pro 5, Team and Max 8) and page with limit up to 100 and next_cursor. For any search batch, have the runner probe with limit 1 first so a bad filter fails cheaply.
6. **Re-check between batches** · `get_usage`
   Before each batch, call get_usage again (it costs nothing) or read the usage object on the last response. If actual spend ran lower than estimated, pull the next batch forward; if higher, shrink it. Tell the runner to send an Idempotency-Key on every paid call so retries never count twice.
7. **Set the error playbook**
   Include in the plan: on 429 window_full, wait Retry-After seconds and retry with the same Idempotency-Key (REST API); on 429 too_many_concurrent, wait for a running search to finish; on 429 weekly_limit, pause until resets_at or move to an async job; on 402, 400, 401, 403 or 409, stop and report instead of retrying; on 404 not_found, skip the row and move on. Blocked calls count against nothing.
8. **Return the plan**
   Output the meter snapshot, the estimate, the batch table and any hard stops, then hand the plan to the skill or user that will run the job.

## Checks before returning

- get_usage was called within this run and the plan uses its numbers, not plan-table defaults
- Every batch fits the remaining five-hour records for its meter, and the total fits records_week
- Search batches respect the plan's concurrent search limit and each starts with a limit 1 probe
- No double verification: emails from enrich_person are not sent through verify_email again
- Free-plan and scrape-unit blockers are reported up front instead of discovered mid-run

## Output

A plan with three parts. 1) Meter snapshot: plan, and for search and enrichment the records left this window, requests left, records left this week and resets_at; scrape units left. 2) Estimate: tool, calls, maximum records or units, meter. 3) Batch table with columns batch, tool, rows or pages, max records, meter, earliest start (now or a resets_at time), notes. Hard stops and the error playbook follow the table. The planner does not label emails; it counts every verify_email check as one enrichment record whatever the result (verified, catch-all, unknown or invalid), and leaves segmenting catch-all, unknown and invalid addresses to the skill that runs the job.

## Example

> I need to enrich 4,000 contacts from a CSV on the Solo plan. Plan it so it doesn't die halfway.

```
✓ Solo plan  ·  620 enrichment records left this window (resets 14:15)  ·  4,620 left this week
✓ Job: 4,000 enrich_person calls  ·  up to 4,000 enrichment records, emails already verified
✓ 5 batches: 560 now, 3 × 900 at each reset, 740 last  ·  fits weekly limit
→ Plan returned with error playbook  ·  get_usage re-check before each batch
```

Illustrative output.

## Cost and limits

Planning spends nothing: get_usage uses no records and no requests. The plan is built around the meters the job will spend. Search and enrichment each have records per rolling five hours, requests per five hours (five times the record limit) and records per rolling week; records count only when data comes back, and every call counts as a request. Standalone verify_email counts toward enrichment; enrich_person emails are already verified at no extra cost. Scraping uses scrape units, 1 per standard page, as a paid-plan add-on, not on Free. Free accounts have 1,000 one-time records shared across search and enrichment. Over a limit the API returns 429 with Retry-After and the blocked call counts against nothing.

## What it doesn't do

- Run the job itself; it plans batches and hands them to the skill or person running the work
- Get around limits with extra accounts, shared keys or anything else the fair use policy rules out
- Upgrade the plan or buy scrape unit packs; it reports when either is needed and leaves the decision to the user
