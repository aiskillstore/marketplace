---
name: multi-client-icp-runner
description: "Runs a saved ICP for each agency client through search_people, enrich_person and verify_email, splits the work across usage windows, and delivers one deduplicated, verified list per client with catch-alls and unknowns segmented. Use when an agency asks to run client ICPs, refresh lists for all clients, build this week's lists per client, or run the multi-client batch."
license: MIT
metadata:
  title: "Multi-client ICP runner"
  category: "Agency workflows"
  outcome: "Find new prospects"
  tools: [get_usage, search_people, enrich_person, verify_email]
  version: "1.0"
  author: Leadsets
  homepage: https://www.leadsets.ai/skills?utm_source=github&utm_medium=leadsets-skills&utm_campaign=multi-client-icp-runner
---

# Multi-client ICP runner

Takes the saved ICPs for every client an agency runs outbound for and turns each one into its own clean, verified prospect list, delivered where that client's campaign lives. Built for outbound agencies and GTM engineers who rebuild lists for several clients every week and need one predictable run instead of one manual session per client.

**Category:** Agency workflows · **Outcome:** Find new prospects · **Tools:** `get_usage`, `search_people`, `enrich_person`, `verify_email`

## Requirements

- The Leadsets MCP server connected to your agent: `https://mcp.leadsets.ai` ([setup](https://www.leadsets.ai/docs/mcp?utm_source=github&utm_medium=leadsets-skills&utm_campaign=multi-client-icp-runner)), or a Leadsets API key for the REST API.
- A Leadsets account. The free plan includes 1,000 records, no card ([get a key](https://www.leadsets.ai/signup?utm_source=github&utm_medium=leadsets-skills&utm_campaign=multi-client-icp-runner)).

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

- "Run the saved ICPs for all my clients and give me a list for each."
- "Build this week's lists for Stackfold and Parcelry, 150 contacts each."
- "Refresh every client's prospect list and skip anyone we already sent to."
- A scheduled weekly or monthly agency list run across several client ICPs.
- An agency onboarding a new client next to existing ones and wanting the same process for all of them.

## What you give it

- **Client ICPs**: One saved ICP per client: client name, titles or function, seniority, industry, employee range, country, and any include or exclude notes. Accepts a file, a sheet, or filters saved by the ICP builder skill. Plain language is fine; the agent converts it to search_people filters.
- **List size per client** (optional): Target number of contacts per client. Default 100. Can be set per client, for example Stackfold 150, Parcelry 75.
- **Destination per client** (optional): Where each client's list goes: CSV, a Google Sheet, or a LinkedCamp campaign, through the agent's own connection to that system. Default is one CSV per client.
- **Exclusions per client** (optional): Optional list of emails, domains or company names to skip for each client (existing customers, past recipients, client do-not-contact list). Default is none.
- **Email policy** (optional): Which statuses count as deliverable. Default: verified in the main list, catch-all in a separate segment, unknown in its own segment, invalid never delivered.

## Steps

1. **Load and confirm every client ICP**
   Read each saved ICP and map it to search_people filters: title, seniority (c_level, vp, head, director, manager, ic), function (revenue, marketing, engineering, product, ops, finance, hr), employees range, industry slugs and country codes. Show the filter set per client in one short table. Ask one question per client only if a filter is ambiguous or missing; do not guess a country or size band. Keep each client's filters, exclusions and destination strictly separate.
2. **Check limits and plan the run** · `get_usage`
   Call get_usage (free). Read search records left in the five-hour window and week, enrichment records left in the window and week, and concurrent searches allowed. Budget roughly 1.3 times each client's list size in search records and the same in enrichment records. If the total does not fit the current window, order clients by priority, run what fits now and schedule the rest for after resets_at. On the free plan, remember the 1,000 records are shared across search and enrichment and do not refill; tell the user how many clients that covers before starting.
3. **Probe each ICP with a 1-record search** · `search_people`
   For each client call search_people with that client's filters and limit 1. Check that the result's match_reasons fit the ICP. If the search returns nothing (0 records, 1 request), loosen one filter and report the change; if it returns 400 invalid_request, fix the named filter value. Do not move a client to the full search until its probe returns a sensible match.
4. **Search people per client** · `search_people`
   Run the full search per client with limit up to 100 and page with next_cursor until the client's budget is reached. Set has_verified_email true when the user wants verified-only lists. Send an Idempotency-Key on every call. Run no more searches at once than the plan's concurrent limit (3 Solo, 5 Pro, 8 Team and Max); on 429 too_many_concurrent wait for a running search to finish. Tag every record with the client name, drop duplicates by person_id within the client, and remove anyone matching that client's exclusions.
5. **Enrich each person** · `enrich_person`
   Call enrich_person for every remaining person, client by client, with an Idempotency-Key. Keep current role, company, domain, work email, status, confidence and checked_at. Emails returned here are already verified, so do not re-verify them. On 404 not_found, mark the person no email and move on. Read the usage object after each batch and stop before the enrichment window runs out.
6. **Verify only what needs it** · `verify_email`
   Call verify_email only for addresses that arrived without a status, or that came from a client-supplied list being merged in. Standalone verification counts toward enrichment, so skip anything enrich_person already labelled. Record the returned status (verified, catch-all, unknown, invalid) and confidence.
7. **Handle limits mid-run** · `get_usage`
   On 429 window_full, wait Retry-After seconds and retry with the same Idempotency-Key (REST API). On 429 weekly_limit, stop, finish the client in progress if its records are already returned, and list the clients still pending with the resets_at time. On 402 free_records_exhausted, stop and ask the user to upgrade; do not retry. Call get_usage before starting each new client.
8. **Deliver one list per client**
   For each client, write the list to its destination through the agent's own connection to CSV, Google Sheets or LinkedCamp. Never place two clients' contacts in the same file, sheet or campaign. Then print a run summary with per-client counts: found, enriched, verified, catch-all, unknown, no email, excluded, and any client not finished.

## Checks before returning

- Every client's list contains only that client's tag, with no record copied into another client's output, and duplicates removed by person_id within each client.
- Each client's exclusion list was applied and the number of removed contacts is reported.
- Verified, catch-all and unknown are kept in separate segments, and no invalid email appears in any delivered list.
- Every client either reached its target size or the summary says why not (thin ICP, empty search, window or weekly limit) and when the rest can run.
- Usage after the run matches the plan from get_usage, and no call was retried without its original Idempotency-Key.

## Output

One deliverable per client, named "<Client> - <ICP name> - <YYYY-MM-DD>". As CSV: three files per client with suffixes _verified, _catch-all and _unknown. As Google Sheets: one sheet per client with tabs Verified, Catch-all and Unknown. As LinkedCamp: only verified contacts go to the client's campaign; catch-all and unknown are returned as CSVs for the agency to decide on. Columns: client, full_name, title, seniority, company, domain, email, email_status, confidence, checked_at, match_reasons, person_id. Catch-all rows are marked for lower-volume sending. Unknown rows are marked unconfirmed and are never mixed into Verified. Invalid emails are dropped and only counted, and people with no email are listed in the run summary, not in the deliverable.

## Example

> Run our saved ICPs for Stackfold and Parcelry. 150 contacts for Stackfold into their Google Sheet, 100 for Parcelry as CSV. Skip anyone on each client's do-not-contact list.

```
✓ 2 ICPs confirmed  ·  ✓ 13,212 enrichment and 6,840 search records left this window
✓ Stackfold: 196 found  ·  12 excluded  ·  171 enriched  ·  138 verified  ·  21 catch-all  ·  12 no email
✓ Parcelry: 131 found  ·  7 excluded  ·  117 enriched  ·  94 verified  ·  13 catch-all  ·  4 unknown  ·  6 no email
→ Sheet "Stackfold - VP Sales SaaS - 2026-11-09" created, 3 tabs  ·  3 Parcelry CSVs saved
```

Illustrative output.

## Cost and limits

search_people uses 1 search record per person returned; enrich_person uses 1 enrichment record per record returned; standalone verify_email counts toward enrichment, which is why the skill only verifies emails that arrive without a status. Empty searches and errors use no records but every call counts as one request, and the request limit is five times the record allowance. No scrape units are used. The skill calls get_usage (free) before the run and before each client, budgets about 1.3 times each list size, respects the plan's concurrent search limit, and splits clients across five-hour windows when the total does not fit. On the free plan the 1,000 one-time records are shared by search and enrichment, which usually covers one small client list; paid plans run several clients per window within their fair-use limits.

## What it doesn't do

- Does not share the agency's Leadsets key with clients or create separate accounts per client; clients receive lists, not access, in line with the fair use policy.
- Does not write outreach copy, launch sequences or send email; it hands each client's list to the tool that sends.
- Does not merge clients' lists or reuse one client's contacts for another, and does not deliver unknown or catch-all emails inside the verified list.
