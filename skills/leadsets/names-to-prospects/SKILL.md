---
name: names-to-prospects
description: "Turns a list of names and companies, such as event attendees, webinar sign-ups or booth scans, into matched and enriched contacts with current role, company and a verified work email when one exists. Flags ambiguous, missing and moved people instead of guessing. Use when someone says \"enrich these attendees\", \"turn this sign-up list into contacts\" or \"find emails for these names\"."
license: MIT
metadata:
  title: "Names to prospects"
  category: "Prospecting"
  outcome: "Find new prospects"
  tools: [get_usage, search_people, enrich_person]
  version: "1.0"
  author: Leadsets
  homepage: https://www.leadsets.ai/skills?utm_source=github&utm_medium=leadsets-skills&utm_campaign=names-to-prospects
---

# Names to prospects

Takes a raw list of names and company names and returns the same people as enriched contacts: current title, company, domain and a verified work email when one exists. Built for marketers and founders who come back from an event or webinar with a spreadsheet of names and want a list they can follow up with, not a pile of guesses.

**Category:** Prospecting · **Outcome:** Find new prospects · **Tools:** `get_usage`, `search_people`, `enrich_person`

## Requirements

- The Leadsets MCP server connected to your agent: `https://mcp.leadsets.ai` ([setup](https://www.leadsets.ai/docs/mcp?utm_source=github&utm_medium=leadsets-skills&utm_campaign=names-to-prospects)), or a Leadsets API key for the REST API.
- A Leadsets account. The free plan includes 1,000 records, no card ([get a key](https://www.leadsets.ai/signup?utm_source=github&utm_medium=leadsets-skills&utm_campaign=names-to-prospects)).

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

- The user has a list of event attendees, webinar registrants or booth scans with names and companies but no emails
- "Find work emails for these 200 names from the conference"
- "Turn this webinar sign-up export into contacts I can send to"
- A list has names and company names only, with no LinkedIn URLs
- The user wants to know which people on an old list are still at the company they listed

## What you give it

- **Name list**: CSV, Google Sheet or pasted rows with at least full name and company name. Optional columns: company domain, title, country. Extra columns are kept and passed through.
- **Event context** (optional): Where the list came from (for example "SaaStr booth scans, Nov"). Used to name the output and the source column. Default: the file name.
- **Email statuses to keep** (optional): Which labels go in the main list. Default: verified only in the main tab, catch-all in its own tab, everything else in a review tab.
- **Where it goes** (optional): CSV or Google Sheets, written through the agent's own connection. Default: CSV in the same folder as the input.

## Steps

1. **Read and clean the list**
   Load the rows, trim whitespace, split full names into first and last, and drop exact duplicates (same name and company). Resolve each company name to a domain: use the domain column if present, otherwise infer the obvious domain (Northwind Analytics → northwind.co). If a company name could map to more than one domain, list those rows and ask the user one question before spending anything. Report row count, duplicates removed and rows with no company.
2. **Check limits and plan the run** · `get_usage`
   Call get_usage (free). Estimate search records as rows × the per-row search limit you will use (default 10) and enrichment records as one per matched person. If the estimate exceeds what is left in the five-hour search or enrichment window, or the free plan's remaining records, tell the user and split the run into batches that fit, or process the highest-priority rows first.
3. **Probe with one row** · `search_people`
   Take the first row with a domain and call search_people with company_domain set to that domain, title set to the row's title if the list has one, and limit 1. Confirm the call returns people at the right company and the response usage object counts as expected. If it returns 400 invalid_request, fix the filter named in the message before continuing.
4. **Find each person at their company** · `search_people`
   For each row, call search_people with company_domain [domain], plus title or country when the list provides them, limit 10, and an Idempotency-Key per row. Match full_name in the results against the input name, allowing for nicknames and middle initials (Maya Chen matches Maya L. Chen). Mark each row matched (one clear match), ambiguous (two or more plausible matches), or not_found (no match or empty result, which uses no records). Respect concurrent search limits; on 429 too_many_concurrent or window_full, wait for Retry-After and retry with the same key. Do not page with cursor beyond the first page unless the user asks.
5. **Enrich matched people** · `enrich_person`
   Call enrich_person for every matched row only. Record current role, company, domain, work email, its status (verified, catch-all, unknown), confidence and checked_at. If the current company differs from the company on the input list, mark the row moved and keep both companies. On 404 not_found, mark the row no_data and move on without retrying. Read the usage object after each batch and pause before the enrichment window would be crossed.
6. **Segment and export**
   Write the output through the agent's own CSV or Google Sheets connection. Verified emails go to the main tab, catch-all to a separate tab, and ambiguous, not_found, moved, no_data and unknown-email rows to a review tab with the reason. Never place an unknown or catch-all address in the main tab. Finish with a short run summary: rows in, matched, enriched, verified, catch-all, needs review, and records used.

## Checks before returning

- Every row in the main tab has email_status verified; catch-all and unknown are never relabelled as valid, and no invalid address appears anywhere as a contact email
- Each input row appears exactly once across the three tabs, and the row counts add up to the cleaned input count
- Ambiguous name matches were not resolved by guessing; they sit in the review tab with the candidate names listed
- Rows where the person now works somewhere else are marked moved, with both the listed and current company shown
- Records used match the get_usage plan; if the run stopped on 402 free_records_exhausted or a weekly_limit 429, the summary says which rows were not processed

## Output

One CSV per tab or one Google Sheet named "<event context> contacts" with three tabs: "Verified", "Catch-all" and "Needs review". Columns: input_name, input_company, full_name, title, company, domain, work_email, email_status, confidence, checked_at, match_status (matched, moved, ambiguous, not_found, no_data), match_reasons, source (event context), plus any original columns passed through. Verified holds verified emails only. Catch-all holds catch-all emails, to be sent at lower volume. Needs review holds unknown-email rows (treated as unconfirmed), rows with no email, ambiguous matches with candidate names, and not_found rows. Invalid emails are never returned as contact emails.

## Example

> Here are 180 people who registered for our pipeline webinar, just names and companies. Find their current roles and work emails and put it in a Google Sheet.

```
✓ 180 rows · 6 duplicates removed · ✓ 1,000 enrichment records left this window
✓ 151 matched · 9 ambiguous · 14 not found
✓ 143 enriched · 117 verified · 18 catch-all (separate tab) · 8 no email · 11 moved companies
→ Sheet "Pipeline webinar contacts" created, 3 tabs
```

Illustrative output.

## Cost and limits

search_people uses 1 search record per person returned, so each row costs up to the per-row limit (default 10); adding title or country filters keeps results and records down, and empty results use no records. enrich_person uses 1 enrichment record per person returned, and its emails are already verified with no second charge. Every call counts as one request, hits and misses, but the request limit is five times the record allowance. get_usage is free and runs before the run and between batches. On the free plan the 1,000 one-time records are shared across search and enrichment, so a 180-row list can use most of them; the skill estimates first and asks before exceeding what is left. On a 429 it waits for Retry-After and retries with the same Idempotency-Key (REST API), which never double-counts. No scrape units are used.

## What it doesn't do

- Guess an email from a name pattern or pick between ambiguous matches; unresolved rows go to review instead
- Send emails, add people to a sequencer or write to a CRM; it hands back a list for the user's own tools
- Find people who were not on the input list or return phone numbers or home addresses
