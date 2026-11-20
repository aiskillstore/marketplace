---
name: outbound-prospect-list
description: "Turns a plain-language ICP into a send-ready B2B prospect list. Confirms the ICP, checks Leadsets limits, finds matching accounts and people with match reasons, enriches each person, verifies emails, and exports verified, catch-all and unconfirmed contacts as separate segments. Use when someone asks to build a prospect list, find leads matching an ICP, or get N contacts with verified emails."
license: MIT
metadata:
  title: "Build an outbound prospect list"
  category: "Prospecting"
  outcome: "Find new prospects"
  tools: [get_usage, search_companies, search_people, enrich_person, verify_email]
  version: "1.0"
  author: Leadsets
  homepage: https://www.leadsets.ai/skills?utm_source=github&utm_medium=leadsets-skills&utm_campaign=outbound-prospect-list
---

# Build an outbound prospect list

This skill takes your ICP in plain language and returns a list of the right people at matching companies, each with a current role, a work email and an honest verification label. It is built for founders and GTM engineers who want a list they can send to today, not a dashboard export to clean up.

**Category:** Prospecting · **Outcome:** Find new prospects · **Tools:** `get_usage`, `search_companies`, `search_people`, `enrich_person`, `verify_email`

## Requirements

- The Leadsets MCP server connected to your agent: `https://mcp.leadsets.ai` ([setup](https://www.leadsets.ai/docs/mcp?utm_source=github&utm_medium=leadsets-skills&utm_campaign=outbound-prospect-list)), or a Leadsets API key for the REST API.
- A Leadsets account. The free plan includes 1,000 records, no card ([get a key](https://www.leadsets.ai/signup?utm_source=github&utm_medium=leadsets-skills&utm_campaign=outbound-prospect-list)).

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

- "Build me a list of 100 heads of RevOps at US B2B SaaS companies with 50 to 200 people."
- "Find VP Sales leads at Series A fintechs in New York with verified emails and put them in a Google Sheet."
- "I need my next 50 prospects matching our ICP, ready to load into LinkedCamp."
- Someone describes an ideal customer and wants named contacts with send-safe emails, not just a company list.
- An agency needs a fresh, verified list for one client ICP as a CSV for their sequencer.

## What you give it

- **ICP**: Industry, company size, region and target roles or seniority, in plain language. Example: RevOps leaders at US B2B SaaS companies with 50 to 200 people. No default; the skill asks if a core element is missing.
- **List size** (optional): How many send-ready contacts to aim for. Default 100. The skill caps the target at what remaining limits allow and says so before starting.
- **Destination** (optional): CSV, Google Sheets or a LinkedCamp campaign, written through the agent's own connection to that system. Default CSV.
- **Exclusions** (optional): Domains or emails to skip, such as current customers, open deals or a do-not-contact list. Default none.
- **Contacts per company** (optional): Maximum people to keep per account so one company does not dominate the list. Default 2.

## Steps

1. **Confirm the ICP**
   Restate the ICP as filters: industry slug, employees range (for example "50-200"), country as ISO codes, seniority (c_level, vp, head, director, manager, ic), function (revenue, marketing, engineering, product, ops, finance, hr) and titles. If one element is ambiguous, such as region or seniority, ask one question and wait. Do not ask more than one question; fill the rest with sensible defaults and state them.
2. **Check limits and plan the run** · `get_usage`
   Call get_usage (free). Read search records left in the five-hour window and the week, enrichment records left, and concurrent searches allowed. Plan roughly 1.3 to 1.5 people searched per contact wanted, plus one enrichment per person. If the plan does not fit the current window, tell the user the size you can deliver now and offer to finish the rest after resets_at. On the free plan, remember the 1,000 records are shared across search and enrichment and do not refill.
3. **Probe the filters** · `search_companies`
   Call search_companies with the ICP filters (industry, headcount band, location, technology if given) and limit 1. Check that the single result actually fits the ICP and read its match_reasons. If it returns nothing (0 records, 1 request), loosen one filter at a time and probe again. If it returns a poor fit, tighten the filters before any large call.
4. **Find matching accounts** · `search_companies`
   Run search_companies with the confirmed filters, paging with next_cursor until you have enough accounts for the target (target divided by contacts per company, plus a margin). Drop any domain in the exclusions list. Stay within the plan's concurrent search limit; on 429 too_many_concurrent, wait for a running search to finish and retry.
5. **Find the right people** · `search_people`
   Call search_people with company_domain set to batches of matching domains, plus seniority, function and title filters from the ICP. Use limit up to 100 and page with cursor. Keep match_reasons on every person. Keep at most the configured number of contacts per company, preferring the closest title match. Stop paging once you have about 1.3 to 1.5 times the target list size. Before going further, run a 1-record search_people probe if the role filters changed from the confirmed ICP.
6. **Enrich each person** · `enrich_person`
   Call enrich_person for each kept person to confirm current role and company and get a work email. Emails returned by enrich_person already carry a verification status, confidence and checked_at, at no extra cost. On 404 not_found, mark the person as no email and move on. Re-read the usage object every batch; if a 429 window_full arrives, wait Retry-After seconds and resume; on weekly_limit, stop and report progress; on 402 free_records_exhausted, stop and ask the user to upgrade.
7. **Verify only what needs it** · `verify_email`
   Call verify_email only for addresses that have no status yet, such as emails supplied by the user, or where the user asks for a fresh pre-send check. Each standalone check counts toward enrichment, so do not re-verify emails that enrich_person already labelled. Record the returned status (verified, catch-all, unknown, invalid) and confidence. Drop invalid addresses from the contact list and count them in the report.
8. **Export and report**
   Dedupe by email and by person plus company. Write the Verified, Catch-all and Not confirmed segments to the chosen destination through the agent's own connection to CSV, Google Sheets or LinkedCamp. Push only the Verified segment to LinkedCamp unless the user says otherwise. Finish with a short run summary: people found, enriched, counts per status, records used, and anything you could not confirm.

## Checks before returning

- Every row in the Verified segment has status verified; catch-all and unknown are never relabelled or mixed in, and invalid addresses never appear as contact emails.
- No duplicate people or emails across segments, no excluded domains, and no company above the per-company cap.
- The probe result and a sample of final rows actually match the ICP, judged from match_reasons, title and company size.
- Remaining limits were re-read from the usage object during the run, and any shortfall against the target list size is stated with the reason (filters too narrow, limit reached, no email found).
- Empty searches and 404s are reported as such rather than silently dropped, so the user knows what the list does not cover.

## Output

Three segments, as tabs in Google Sheets or as three CSV files (prospects_verified.csv, prospects_catch_all.csv, prospects_not_confirmed.csv): Verified, Catch-all, Not confirmed. Columns: full_name, title, seniority, company_name, company_domain, work_email, email_status, email_confidence, email_checked_at, match_reasons, person_id. Verified holds only verified emails and is the send-ready list. Catch-all holds catch-all addresses, to send at lower volume. Not confirmed holds unknown emails and people with no email found, for review or later re-checks. Invalid emails are removed and only counted in the summary. For LinkedCamp, the Verified segment is pushed as campaign leads and the other segments are returned as files.

## Example

> Build a list of 100 heads of RevOps at US B2B SaaS companies with 50 to 200 people. Put it in a Google Sheet.

```
✓ ICP confirmed  ·  ✓ 412 search records, 13,212 enrichment records left this window
✓ 1-record probe: Northwind Analytics (northwind.co) matches on industry, size, country
✓ 138 matching people at 81 accounts  ·  ✓ 121 enriched
✓ 97 verified  ·  15 catch-all (separate tab)  ·  9 unknown or no email
→ Sheet "RevOps leads - Nov" created, 3 tabs
```

Illustrative output.

## Cost and limits

get_usage costs nothing and runs first. search_companies and search_people use 1 search record per record returned; the 1-record probe uses at most 1, and an empty search uses 0 records but 1 request. enrich_person uses 1 enrichment record per record returned, and its emails are already verified with no second charge. Standalone verify_email counts toward enrichment, so the skill only calls it for addresses without a status. A 100-contact list typically needs a few hundred search records and around 130 to 150 enrichments, which fits one five-hour window on Solo (500 search, 1,000 enrichment) and above. On the free plan the 1,000 one-time records are shared across search and enrichment. Every request counts toward the request limit, which is five times the record allowance. On 429 window_full the skill waits Retry-After and resumes; blocked calls use no records. On weekly_limit it stops and reports progress. No scrape units are used.

## What it doesn't do

- Send emails or start sequences; it hands the list to the CSV, sheet or LinkedCamp campaign you choose, and Leadsets is not a sending tool.
- Round catch-all or unknown emails up to verified, or return phone numbers, which Leadsets does not offer.
- Scrape websites or careers pages for hiring signals; use the hiring signal skills for that, which need scrape units on a paid plan.
