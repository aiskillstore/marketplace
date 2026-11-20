---
name: hiring-signal-finder
description: "Reads careers pages with scrape_jobs to find companies hiring for roles that signal they need what you sell, then uses search_people to find the right buyers at each hiring account, ranked by signal strength and recency. Use when someone asks \"who is hiring SDRs\", \"find companies hiring RevOps\", \"which of these accounts are hiring\" or wants hiring signals and contacts for timely outreach."
license: MIT
metadata:
  title: "Hiring signal finder"
  category: "Hiring signals"
  outcome: "Research accounts and timing"
  tools: [get_usage, scrape_jobs, search_people]
  version: "1.0"
  author: Leadsets
  homepage: https://www.leadsets.ai/skills?utm_source=github&utm_medium=leadsets-skills&utm_campaign=hiring-signal-finder
---

# Hiring signal finder

Turns a list of target domains into the accounts that are hiring right now for roles that predict a need for your product, with the open roles, posting dates and the people to contact. Built for founders, SDRs and GTM engineers who want a reason to reach out this week, not a static account list.

**Category:** Hiring signals · **Outcome:** Research accounts and timing · **Tools:** `get_usage`, `scrape_jobs`, `search_people`

## Requirements

- The Leadsets MCP server connected to your agent: `https://mcp.leadsets.ai` ([setup](https://www.leadsets.ai/docs/mcp?utm_source=github&utm_medium=leadsets-skills&utm_campaign=hiring-signal-finder)), or a Leadsets API key for the REST API.
- A Leadsets account. The free plan includes 1,000 records, no card ([get a key](https://www.leadsets.ai/signup?utm_source=github&utm_medium=leadsets-skills&utm_campaign=hiring-signal-finder)).

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

- "Which of these 40 domains are hiring SDRs right now? Who runs sales there?"
- "Find accounts in my target list that posted RevOps or sales ops roles in the last 30 days."
- You sell a tool for a specific team and want companies that are building that team, plus the leader to contact.
- You have a tiered account list and want to know which accounts to work first based on hiring.
- "Give me hiring signals on my target accounts and the decision-makers behind them."

## What you give it

- **Target accounts**: A list of company domains (pasted, CSV or Google Sheet). If you only have an ICP, the agent can build a domain list first with search_companies by industry, headcount band and location. No default; one of the two is required.
- **Signal roles**: The job titles that predict a need for what you sell, for example SDR, BDR, RevOps Manager. If not given, the agent derives them from a one-line description of your product and confirms them with you.
- **Lookback window** (optional): How recent a posting must be to count as a signal. Default 30 days.
- **Who to contact** (optional): Buyer persona at each hiring account, as function and seniority (for example revenue, vp and head). Default: the leader of the team that is hiring, up to 3 people per account.
- **Where it goes** (optional): CSV, Google Sheets or a reply in chat. Default: a table in chat plus a CSV.

## Steps

1. **Confirm signal roles and buyers**
   Restate the signal roles, the lookback window and the buyer persona in one short list. Map each signal role to the team leader who would own the purchase (for example SDR postings map to function revenue, seniority vp or head). Ask one question only if the mapping is ambiguous. Dedupe and normalise the domain list (lowercase, strip protocol and paths).
2. **Check limits and scrape units** · `get_usage`
   Call get_usage. Read scrape_units, search records left in the five-hour window and this week, and concurrent searches. scrape_jobs is not available on the free plan: if no scrape units are available, stop and tell the user that scraping is a paid add-on in units before spending any search records. Estimate the run as roughly one scrape unit per careers page plus up to 3 search records per hiring account. If the estimate exceeds what is left, process the domains that fit now and report the rest as queued for the next window.
3. **Probe one careers page** · `scrape_jobs`
   Call scrape_jobs on the first domain only. Check that roles come back with titles and dates, and that your title matching catches the signal roles (fuzzy variants such as "Sales Development Representative" for SDR). Adjust the matching before moving on. If the probe returns no careers data, try the next domain rather than assuming the tool failed.
4. **Scrape careers pages for hiring signals** · `scrape_jobs`
   Call scrape_jobs for each remaining domain. Keep only roles whose title matches a signal role and whose posting date falls inside the lookback window. For each account record the matching titles, posting dates and count. Mark accounts with no careers page, no open roles or only older postings as no signal; do not drop them silently. On 429, wait for Retry-After and retry.
5. **Probe the people search** · `search_people`
   For the first signal account, call search_people with company_domain set to that domain, the buyer function and seniority, and limit 1. Confirm the match_reasons fit the persona and the company domain matches. Widen titles or seniority if the result is empty; an empty search uses no records.
6. **Find who to contact at each hiring account** · `search_people`
   Call search_people for the signal accounts, passing their domains in company_domain with the confirmed function and seniority and limit set to about 3 per account. Stay within the plan's concurrent search limit (3 on Solo, 5 on Pro, 8 on Team and Max); on 429 too_many_concurrent wait for a running search to finish. Keep match_reasons and any email with its status and checked_at as returned. Use has_verified_email true only if the user asked for verified contacts only.
7. **Rank and return**
   Rank signal accounts by number of matching roles, then by most recent posting date. Build the output table, separate no-signal accounts, and call get_usage again to report scrape units and search records used. Write to the chosen destination through the agent's own connection to Google Sheets or as a CSV.

## Checks before returning

- Every signal row has a matching role title and a posting date inside the lookback window; postings without a date are flagged as undated, not counted as recent.
- No duplicate domains and no duplicate people; each contact's company domain matches the hiring account.
- Accounts with no careers data or no matching roles appear in a separate no-signal list with the reason, and empty people searches are reported as no contact found.
- Emails are shown with the status Leadsets returned (verified, catch-all, unknown); catch-all and unknown are labelled, never presented as verified, and invalid addresses are never listed.
- Scrape units and search records used match the plan from get_usage, and any domains deferred to the next window are listed.

## Output

One table, "Hiring signals", one row per contact at a signal account, with columns: rank, company, domain, signal_roles (titles), signal_count, latest_posted, contact_name, title, seniority, match_reasons, email, email_status, checked_at. Accounts with a signal but no contact found get one row with contact fields empty. A second tab or section, "No signal", lists domains with the reason (no careers data, no matching roles, postings older than the window). email_status is copied as returned: verified rows are send-ready, catch-all and unknown rows are labelled and left for a verification skill, and invalid emails never appear. In Google Sheets the tabs are named "Hiring signals" and "No signal"; as CSV, two files with the same names.

## Example

> Here are 40 domains from my target list. Which ones are hiring SDRs or BDRs in the last 30 days, and who runs sales there? Put it in a Google Sheet.

```
✓ 40 domains · ✓ 412 scrape units and 470 search records left
✓ 40 careers pages read · 14 hiring SDR/BDR in last 30 days · 26 no signal
✓ 31 sales leaders found at 13 accounts · 1 account no contact
✓ 19 verified · 7 catch-all · 5 no email (labelled)
→ Sheet "SDR hiring signals – Nov" created, 2 tabs
```

Illustrative output.

## Cost and limits

scrape_jobs uses 1 scrape unit per page read; scraping is an add-on on paid plans (packs of 1k, 5k or 20k units) and is not available on Free, so the skill checks scrape units with get_usage before anything else. search_people uses 1 search record per person returned and 1 request per call; empty searches use no records. get_usage is free and is called at the start and end. The skill probes with one domain and a limit 1 search before scaling, caps contacts per account, respects concurrent search limits, and on 429 waits for Retry-After (blocked calls count against nothing). If a run would cross the five-hour or weekly window, it finishes the domains that fit and lists the rest for the next window.

## What it doesn't do

- Does not enrich or verify contacts: it reports email status as search_people returns it and leaves enrich_person and verify_email to a follow-up skill such as Build an outbound prospect list.
- Does not send messages or write to a CRM or sequencer on its own; it hands the table to the destination you choose through your own connection.
- Does not read pages behind a login or guess at hiring from anything other than public careers pages.
