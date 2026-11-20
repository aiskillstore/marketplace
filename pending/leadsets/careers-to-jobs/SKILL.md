---
name: careers-to-jobs
description: "Reads public careers pages with scrape_jobs and returns every open role as a structured row: title, team, location and posted date, per company. Checks scrape units first, probes one domain, then batches the rest. Use when someone says \"what roles is this company hiring for\", \"turn these careers pages into a table\", \"list open jobs at these domains\" or \"pull job postings for my accounts\"."
license: MIT
metadata:
  title: "Careers page to structured jobs"
  category: "Web scraping"
  outcome: "Research accounts and timing"
  tools: [get_usage, scrape_jobs]
  version: "1.0"
  author: Leadsets
  homepage: https://www.leadsets.ai/skills?utm_source=github&utm_medium=leadsets-skills&utm_campaign=careers-to-jobs
---

# Careers page to structured jobs

Turns one careers page or a list of company domains into a clean table of open roles, with title, team, location and posted date for each. Built for GTM engineers, founders and agencies who want hiring data they can filter, sort and feed into other workflows, not a pile of copied job ads.

**Category:** Web scraping · **Outcome:** Research accounts and timing · **Tools:** `get_usage`, `scrape_jobs`

## Requirements

- The Leadsets MCP server connected to your agent: `https://mcp.leadsets.ai` ([setup](https://www.leadsets.ai/docs/mcp?utm_source=github&utm_medium=leadsets-skills&utm_campaign=careers-to-jobs)), or a Leadsets API key for the REST API.
- A Leadsets account. The free plan includes 1,000 records, no card ([get a key](https://www.leadsets.ai/signup?utm_source=github&utm_medium=leadsets-skills&utm_campaign=careers-to-jobs)).

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

- "What is northwind.co hiring for right now?"
- "Turn these 30 careers pages into one spreadsheet of open roles."
- "List every open role at Stackfold and Parcelry, with team and location."
- You need structured job data as input for a hiring signal, account research or first-line workflow.
- "Which of my target accounts posted new roles in the last 30 days?"

## What you give it

- **Companies**: One or more company domains or careers page URLs, pasted in chat or read from a CSV or Google Sheet column. Domains are fine; the skill looks for the careers page.
- **Role filter** (optional): Optional keywords, teams or locations to keep (for example "sales, RevOps, US"). Default: keep every open role.
- **Recency** (optional): Optional posted-within window in days. Default: no cutoff, but roles are sorted newest first.
- **Where it goes** (optional): CSV, Google Sheets or a table in chat. Default: CSV for more than 25 roles, a chat table otherwise.

## Steps

1. **Confirm the company list and filters**
   Normalize every input to a domain or careers URL, remove duplicates and blank rows, and restate the role filter and recency window. Ask one question only if the filter is ambiguous, for example whether "sales" includes customer success.
2. **Check scrape units and plan the run** · `get_usage`
   Call get_usage and read scrape_units. Scraping is not on the Free plan; if the account has no scrape units, stop and tell the user scrape_jobs needs a paid plan with a scrape unit pack. Estimate cost as at least one unit per careers page and, if the remaining units cannot cover the list, ask whether to run a subset or stop.
3. **Probe with one company** · `scrape_jobs`
   Call scrape_jobs on the first domain only. Check that it returns open roles with titles and dates, note the units used, and confirm the fields map cleanly to title, team, location and posted date. If it returns nothing, check the URL before scaling up.
4. **Scrape the remaining careers pages** · `scrape_jobs`
   Call scrape_jobs for each remaining domain in batches of about 20. Read units used after each batch and re-check with get_usage before the next one. On a 429, wait for Retry-After and retry the same call; on 400 or 404, record the company as not readable and move on. Never retry 401, 402 or 403.
5. **Structure and filter the roles**
   Build one row per open role. Keep the title exactly as posted, fill team and location only when the page states them, and store dates as YYYY-MM-DD. Apply the role filter and recency window, drop exact duplicate postings within a company, and sort by company, then newest first.
6. **Deliver the table and report gaps**
   Write the rows to the chosen destination through the agent's own connection (CSV file, Google Sheet, or chat table). Add a second tab or section listing companies with no open roles found and companies whose careers page could not be read, with the reason. Finish with a short run summary and units used.

## Checks before returning

- Every row has a company, domain, title and source URL; team, location and posted date are blank rather than guessed when the page does not state them.
- Scrape units used match the get_usage reading before and after the run, and the run stopped before exceeding what the user approved.
- No duplicate postings within a company: same title, team and location appear once.
- Companies with zero roles are reported separately from companies whose page could not be read, so "not hiring" and "no data" are never confused.
- The role filter and recency window were applied and the summary states how many roles were removed by them.

## Output

A table named "Open roles" with one row per role and columns: company, domain, title, team, location, posted_date (YYYY-MM-DD), source_url, scraped_at. A second tab or section named "Not found" lists each company with status no_open_roles or page_unreadable and a short reason. In Google Sheets these are two tabs; as CSV they are two files (open_roles.csv, not_found.csv). This skill returns no contacts or emails, so there are no verified, catch-all, unknown or invalid labels; hand the company list to a people or verification skill if contacts are needed.

## Example

> Here are 40 target account domains in my Sheet. Pull every open role from their careers pages, keep sales and RevOps roles posted in the last 60 days, and add them as a new tab.

```
✓ 40 domains, 38 unique  ·  ✓ 2,140 scrape units left
✓ Probe northwind.co: 6 roles, 6 units
✓ 31 careers pages read  ·  412 open roles  ·  57 match sales/RevOps, last 60 days
7 no open roles  ·  0 unreadable  ·  194 units used
→ Tab "Open roles – sales & RevOps" added, plus "Not found"
```

Illustrative output.

## Cost and limits

scrape_jobs uses scrape units, not search or enrichment records: one unit per standard page read, with capped page depth so one domain costs a predictable number of units. Scraping is not available on the Free plan; it is an add-on on every paid plan, with packs of $9 for 1,000, $19 for 5,000 and $49 for 20,000 units that do not expire while subscribed. get_usage is free, so the skill calls it before the run and between batches, probes one domain before scaling, and asks before spending beyond what the remaining units cover. A 429 returns a Retry-After time and the blocked call counts against nothing.

## What it doesn't do

- Find people, enrich contacts or verify emails; pair it with a people search or hiring signal skill for who to contact.
- Read pages behind a login, paywalled job boards or anything that blocks robots; it only reads public company careers pages.
- Infer team, location or posting date when the page does not state them, or decide which roles count as a buying signal for you.
