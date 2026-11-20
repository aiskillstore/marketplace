---
name: companies-hiring-sdrs
description: "Finds companies that posted SDR or BDR roles recently, confirms each opening from the careers page with titles and post dates, and returns the sales leaders at those companies with match reasons and email status. Needs scrape units on a paid plan. Use when someone asks for companies hiring SDRs, accounts building a sales team, BDR hiring signals, or who runs sales at companies hiring reps."
license: MIT
metadata:
  title: "Companies hiring SDRs"
  category: "Hiring signals"
  outcome: "Research accounts and timing"
  tools: [get_usage, search_companies, scrape_jobs, search_people]
  version: "1.0"
  author: Leadsets
  homepage: https://www.leadsets.ai/skills?utm_source=github&utm_medium=leadsets-skills&utm_campaign=companies-hiring-sdrs
---

# Companies hiring SDRs

Produces a list of companies that are hiring SDRs or BDRs right now, with the confirmed open roles, their post dates and the sales leaders to contact at each one. Built for founders, agencies and GTM engineers selling into new or growing sales teams, where a fresh SDR posting is the reason to reach out this week.

**Category:** Hiring signals · **Outcome:** Research accounts and timing · **Tools:** `get_usage`, `search_companies`, `scrape_jobs`, `search_people`

## Requirements

- The Leadsets MCP server connected to your agent: `https://mcp.leadsets.ai` ([setup](https://www.leadsets.ai/docs/mcp?utm_source=github&utm_medium=leadsets-skills&utm_campaign=companies-hiring-sdrs)), or a Leadsets API key for the REST API.
- A Leadsets account. The free plan includes 1,000 records, no card ([get a key](https://www.leadsets.ai/signup?utm_source=github&utm_medium=leadsets-skills&utm_campaign=companies-hiring-sdrs)).

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

- "Find US B2B SaaS companies with 20 to 200 people hiring SDRs in the last 30 days, and who runs sales there."
- "Which of these 40 domains are hiring BDRs right now?"
- You sell sales tooling, training or data and want accounts that are building an outbound team.
- You need a timing signal to prioritise a target account list before outreach.
- "Give me sales leaders at fintechs that just posted SDR roles."

## What you give it

- **Account filters**: Industry, headcount band, region and technology in plain language, or a list of domains to check. Default: US B2B companies with 20 to 200 people.
- **Recency window** (optional): How recent a posting must be to count. Default: posted in the last 30 days.
- **Roles that count** (optional): Job titles that signal the hire. Default: SDR, BDR, Sales Development Representative, Business Development Representative, and SDR or BDR team lead.
- **Who to return** (optional): The sales leaders to find at each confirmed company. Default: revenue function, seniority vp, head and director, up to 3 per company.
- **Where it goes** (optional): Table in chat, CSV or Google Sheets. Default: table in chat plus CSV.

## Steps

1. **Confirm filters and window**
   Restate the account filters, recency window, role titles and leader seniority. Ask one question only if something is ambiguous, for example a region with no country. If the user gave a domain list, skip company search and go to the usage check.
2. **Check limits and plan the run** · `get_usage`
   Call get_usage (free). Read search records and requests left in the five-hour window and week, concurrent searches, and scrape_units. If scrape units are zero or the account is on Free, stop and explain that scrape_jobs needs a scrape unit pack on a paid plan. Estimate the run: about 1 search record per company, 1 scrape unit per careers page, and up to 3 search records per confirmed company for leaders. If it would cross a window, cap the company count and tell the user.
3. **Probe the filters** · `search_companies`
   Call search_companies with the translated filters (industry, headcount band, location, technology, and the hiring filter for SDR roles where available) and limit 1. Check the one result against the ICP by its match_reasons. If it is empty or off target, adjust filters before spending records. An empty probe uses no records.
4. **Pull candidate accounts** · `search_companies`
   Run the full search with limit up to 100 per page and page with next_cursor until you reach the planned company count. Dedupe by domain. Respect the plan's concurrent search cap; on 429 too_many_concurrent or window_full, wait for Retry-After and retry with the same Idempotency-Key (REST API).
5. **Confirm SDR and BDR openings** · `scrape_jobs`
   Call scrape_jobs for each candidate domain's careers page. Keep a company only if an open role matches the role titles and its posted date falls inside the recency window. Record each matching title and date. Drop companies with no matching role or no readable careers page, and count them separately so the summary reports them.
6. **Find the sales leaders** · `search_people`
   For each confirmed company, call search_people with company_domain set to that domain, function revenue, seniority vp, head and director, limit 3. Batch domains where possible to save requests. Keep match_reasons and the email object with its status and checked_at. If the user wants send-ready contacts only, set has_verified_email to true and note who was excluded.
7. **Assemble and return**
   Build one row per leader with the company's hiring evidence attached. Sort companies by most recent SDR or BDR posting. Report counts at each stage: candidates, confirmed hiring, no careers page, leaders found, email status breakdown, and records and units used from the usage object.

## Checks before returning

- Every company in the result has at least one SDR or BDR role from scrape_jobs dated inside the recency window; companies matched only by search filters are not listed as confirmed.
- Companies are deduped by domain and leaders by person_id before output.
- Email status is shown as returned: verified, catch-all and unknown are labelled as such and never presented as valid; rows with no email are kept and marked no email.
- Search records, requests and scrape units used are within what get_usage reported; any 429 was waited out with Retry-After, and a 402 free_records_exhausted stops the run with an upgrade note rather than a retry.
- If zero companies are confirmed, say so plainly, show how many were checked, and suggest widening the window or filters instead of returning unconfirmed accounts.

## Output

A table (and CSV or Google Sheet if asked) with one row per sales leader: company name, domain, headcount band, industry, SDR/BDR role title, posted date, number of matching open roles, leader full name, title, seniority, email address, email status (verified, catch-all, unknown), email checked_at, and match_reasons. In Google Sheets use tabs "Hiring SDRs: verified" for leaders with verified emails, "Catch-all and unknown" for those labelled catch-all or unknown (catch-all can be sent at lower volume, unknown is unconfirmed), and "Companies" listing every confirmed hiring company including those with no leader found. In CSV, the same split as two files plus a companies file. Invalid emails are never served, so rows without a usable address show status "no email". The run summary lists candidates checked, confirmed hiring, leaders found and usage spent.

## Example

> Find US B2B SaaS companies with 20 to 200 people that posted SDR or BDR roles in the last 30 days, and give me their VP or Head of Sales. Put it in a Google Sheet.

```
✓ 61 search records left this window · ✓ 1,180 scrape units
✓ 86 candidate companies · ✓ 71 careers pages read · 54 hiring SDRs/BDRs (last 30 days)
✓ 112 sales leaders found · 81 verified · 19 catch-all/unknown (separate tab) · 12 no email
→ Sheet "Companies hiring SDRs – Nov" created, 3 tabs
```

Illustrative output.

## Cost and limits

search_companies and search_people use 1 search record per record returned; an empty result uses no records but still counts as 1 request. scrape_jobs uses 1 scrape unit per page and draws on no search or enrichment records; scraping is not on the Free plan and needs a unit pack on a paid plan ($9 for 1k, $19 for 5k, $49 for 20k). get_usage is free. The skill calls get_usage first, probes with limit 1, caps the company count to fit the search window (Solo has 500 search records per five hours and 2,500 per week, 3 concurrent searches), limits leaders to 3 per company, and on 429 waits for Retry-After and retries with the same Idempotency-Key (REST API) so nothing is counted twice. Large runs are split across windows rather than pushed through.

## What it doesn't do

- It does not call enrich_person or verify_email; emails and statuses come as returned by search_people. Run an enrichment or pre-send verification skill for a fully verified list.
- It does not list companies as hiring based on search filters alone; only roles confirmed by scrape_jobs inside the window count.
- It does not write outreach, send email or push contacts into a CRM or sequencer; it hands the list to the tool you already use.
