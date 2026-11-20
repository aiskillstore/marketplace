---
name: search-b2b-prospects
description: "Finds B2B people by title, function, seniority, country, company size and industry with the Leadsets search_people tool, and returns a ranked table that shows why each person matched. It plans the run against search limits and probes the filters first. Use when someone asks to search prospects, find people matching a persona, pull a list of VPs or heads of a function, or see who fits an ICP before enriching."
license: MIT
metadata:
  title: "Search B2B prospects"
  category: "Prospecting"
  outcome: "Find new prospects"
  tools: [get_usage, search_people]
  version: "1.0"
  author: Leadsets
  homepage: https://www.leadsets.ai/skills?utm_source=github&utm_medium=leadsets-skills&utm_campaign=search-b2b-prospects
---

# Search B2B prospects

Turns a plain-language persona into Leadsets people filters and returns a ranked table of matching people, each with the reasons they matched. Built for founders, SDRs and GTM engineers who want to see who fits before they spend enrichment on anyone.

**Category:** Prospecting · **Outcome:** Find new prospects · **Tools:** `get_usage`, `search_people`

## Requirements

- The Leadsets MCP server connected to your agent: `https://mcp.leadsets.ai` ([setup](https://www.leadsets.ai/docs/mcp?utm_source=github&utm_medium=leadsets-skills&utm_campaign=search-b2b-prospects)), or a Leadsets API key for the REST API.
- A Leadsets account. The free plan includes 1,000 records, no card ([get a key](https://www.leadsets.ai/signup?utm_source=github&utm_medium=leadsets-skills&utm_campaign=search-b2b-prospects)).

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

- "Find VPs of Sales at US SaaS companies with 50 to 200 people."
- "Who are the heads of RevOps at fintechs in the UK?"
- "Search for marketing directors in healthcare, 200 to 1,000 employees, and show me why each one matched."
- Sizing a persona before deciding whether to enrich or build a full outbound list
- "Only show people with a verified work email" as a quick search, without a separate enrichment pass

## What you give it

- **Persona**: Titles, function and seniority in plain language, for example "VP or Head of Sales". Mapped to title (fuzzy-matched), function (revenue, marketing, engineering, product, ops, finance, hr) and seniority (c_level, vp, head, director, manager, ic).
- **Company filters** (optional): Country, company size range and industry, for example US, 50-200, SaaS. Mapped to country (ISO 3166-1 alpha-2), employees (a range such as "50-200") and industry slugs. Default: no restriction beyond what the user states.
- **How many** (optional): Target number of people. Default 100. Capped by the search records left in the current five-hour window.
- **Verified email only** (optional): Whether to set has_verified_email to true so only people with a verified work email come back. Default off, so the user sees the full market first.
- **Where it goes** (optional): A table in the chat (default) or a CSV file. Any other destination is written through the agent's own connection to that system.

## Steps

1. **Turn the request into filters**
   Map the persona to title, function and seniority, and the company description to country, employees and industry. If one thing is ambiguous (for example "Europe" with no countries, or "mid-market" with no headcount), ask one question, then restate the final filters in one line before spending anything.
2. **Check limits and plan the run** · `get_usage`
   Call get_usage (it costs nothing). Read search records left in the five-hour window and the week, and concurrent searches allowed. If the target count exceeds what is left, tell the user the number you can return now and when the window resets, and lower the target rather than running into a 429. On the free plan, note that the 1,000 free records are shared with enrichment.
3. **Probe the filters with one record** · `search_people`
   Call search_people with the planned filters and limit 1. Check the returned person against the intent: title, seniority, company size, country and the match_reasons. If the result is wrong, adjust filters and probe again. If it is empty, it used no records; loosen one filter at a time (title variants first, then industry, then size) and report each change.
4. **Run the search and page through results** · `search_people`
   Call search_people with the confirmed filters and limit up to 100 per call (default is 25). Pass next_cursor as cursor for the next page until the target count is reached or next_cursor is empty. Run pages one after another, staying under the plan's concurrent search cap. Send an Idempotency-Key on each call so a retry never counts records twice. Read the usage object on every response and stop early if the window is nearly full.
5. **Handle errors without wasting records**
   On 429 window_full or too_many_concurrent, wait the Retry-After seconds and retry with the same Idempotency-Key (REST API). On 429 weekly_limit, stop and report resets_at. On 400 invalid_request, fix the named filter. On 402 free_records_exhausted, stop and tell the user the free records are used up. Do not retry 401 or 403.
6. **Clean and rank the results**
   Remove duplicates by person_id. Rank by match_score where present, then by how many filters appear in match_reasons. Keep each email exactly as labelled by Leadsets (verified, catch-all, unknown) with its checked_at date, and never upgrade a label.
7. **Return the table and a short summary**
   Show the table in the chat or write the CSV. Report total found, how many carry a verified email, how many have no email or a non-verified label, records used and records left. Offer next steps: enrich the top rows or build a full verified outbound list.

## Checks before returning

- The 1-record probe matched the intended title, seniority, size and country before any larger search ran.
- No duplicate person_id in the output, and the row count does not exceed the target or the records left in the window.
- Every email keeps its Leadsets status and checked_at; catch-all and unknown are labelled as such and never shown as verified.
- Empty searches and loosened filters are reported, so the user knows exactly which filters produced the list.
- The final usage object or a get_usage call confirms records used and what is left this window and week.

## Output

One table (chat) or one CSV file named after the persona and month, for example "vp-sales-us-saas-nov.csv", with columns: full_name, title, company_name, company_domain, email, email_status, email_checked_at, match_reasons, match_score, person_id. Rows with a verified email are listed first. Catch-all and unknown emails stay in the table with their label in email_status and are counted separately in the summary; they are not treated as send-ready. Rows with no email have an empty email column and email_status "none". Invalid emails are never served by Leadsets, so none appear. A short summary above the table states filters used, counts by email status, records used and records left.

## Example

> Find 100 VPs and Heads of Sales at US SaaS companies with 50 to 200 employees. Show me why each one matched and save it as a CSV.

```
✓ Filters: title VP Sales, Head of Sales · seniority vp, head · US · saas · 50-200
✓ 1-record probe matched (Maya Chen, VP Sales, Northwind Analytics) · 412 search records left this window
✓ 100 people found across 1 page · 0 duplicates
✓ 71 with verified email · 9 catch-all · 4 unknown · 16 no email
→ vp-sales-us-saas-nov.csv saved, 100 rows · 101 search records used
```

Illustrative output.

## Cost and limits

search_people uses 1 search record per person returned and 1 request per call; an empty result uses 0 records and 1 request, and get_usage costs nothing. Search records draw on the search meters only: Solo 500 per five hours and 2,500 per week, Pro 7,500 and 37,500, Team 75,000 and 375,000, Max 112,500 and 562,500. On Free, the 1,000 one-time records are shared with enrichment and do not refill. Concurrent searches are capped at 3 on Solo, 5 on Pro and 8 on Team and Max. The skill checks get_usage first, probes with limit 1, pages with cursors, reads the usage object on each response, and uses Idempotency-Keys so retries after a 429 never count records twice. It uses no enrichment records and no scrape units.

## What it doesn't do

- It does not call enrich_person or verify_email; emails are shown only as search returns them, with their existing labels. Use the outbound prospect list skill for a fully enriched and verified list.
- It does not write to a CRM or push to a sequencer; any destination beyond chat or CSV goes through the agent's own connection to that system.
- It does not return phone numbers or personal home addresses, which Leadsets does not provide.
