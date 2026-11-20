---
name: enrich-company-domains
description: "Enriches a list of company domains with firmographics from Leadsets enrich_company: industry, headcount band, location and technology stack, each with its source and last-checked date. Dedupes and normalizes domains, plans the run against remaining limits and reports domains it could not match. Use when someone says \"enrich these domains\", \"add industry and size to my account list\" or \"fill in company data for this CSV\"."
license: MIT
metadata:
  title: "Enrich companies from domains"
  category: "Enrichment"
  outcome: "Get verified contact data"
  tools: [get_usage, enrich_company]
  version: "1.0"
  author: Leadsets
  homepage: https://www.leadsets.ai/skills?utm_source=github&utm_medium=leadsets-skills&utm_campaign=enrich-company-domains
---

# Enrich companies from domains

Takes a list of domains and returns one row per company with industry, headcount band, location and stack, plus the source and checked date for every field. Built for GTM engineers, RevOps and founders who have an account list with nothing but URLs and need it segmentable before anyone prospects into it.

**Category:** Enrichment · **Outcome:** Get verified contact data · **Tools:** `get_usage`, `enrich_company`

## Requirements

- The Leadsets MCP server connected to your agent: `https://mcp.leadsets.ai` ([setup](https://www.leadsets.ai/docs/mcp?utm_source=github&utm_medium=leadsets-skills&utm_campaign=enrich-company-domains)), or a Leadsets API key for the REST API.
- A Leadsets account. The free plan includes 1,000 records, no card ([get a key](https://www.leadsets.ai/signup?utm_source=github&utm_medium=leadsets-skills&utm_campaign=enrich-company-domains)).

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

- "Enrich these 300 domains with industry, size and location."
- "I have a CSV of company websites, add headcount band and tech stack."
- Preparing an account list for tiering, ICP fit scoring or a people search that needs firmographic filters.
- Filling empty company fields in a Google Sheet or Attio before a campaign.
- "Which of these domains are SaaS companies with 50 to 200 people?"

## What you give it

- **Domains**: A list of company domains or website URLs, pasted, in a CSV or Google Sheet column, or read from Attio through the agent's own connection. Full URLs are fine; the skill strips them to the bare domain.
- **Fields** (optional): Which firmographics to keep. Default: industry, headcount band, location and technology stack, each with source and checked date.
- **Where it goes** (optional): CSV, a Google Sheet, or write-back to Attio. Default: a CSV with the original row order preserved.
- **Overwrite policy** (optional): Whether to replace values already present in the source list or CRM. Default: fill empty fields only and report any conflicts instead of overwriting.

## Steps

1. **Normalize and dedupe the domains**
   Strip protocol, paths, query strings and a leading www. from every entry, lowercase it, and drop exact duplicates. Set aside anything that is not a domain (blank cells, emails, free-text company names) in a skipped list with the reason. Report the count of unique domains before spending anything.
2. **Check remaining limits and plan the run** · `get_usage`
   Call get_usage (it costs nothing). Read enrichment records left in the five-hour window and the week, or free records left on the Free plan. If the unique domain count exceeds what is left, tell the user and either split the run across windows or enrich the first batch now and resume after resets_at. Do not start a run that will stall halfway without saying so.
3. **Probe with one domain** · `enrich_company`
   Call enrich_company on a single domain from the list. Confirm the response contains the requested fields with source and checked dates and that the company matches the domain. If it returns 404 not_found, try one more domain before concluding anything. Stop on 401 or 403 and report the key or access problem.
4. **Enrich the rest in batches** · `enrich_company`
   Call enrich_company for each remaining domain in batches sized to the window left. Read the usage object on every response and pause before the window fills. On 404 not_found, record the domain as no match and move on without retrying. On 429 window_full or too_many_concurrent, wait Retry-After seconds and retry; on 429 weekly_limit, stop and report resets_at. On 402 free_records_exhausted, stop and ask the user to upgrade. Over REST, send an Idempotency-Key per domain so retries never count twice.
5. **Merge results onto the original list**
   Join each enriched record back to every source row that shared its normalized domain, keeping original row order. Apply the overwrite policy: fill empty fields, and list any field where the existing value differs from the Leadsets value as a conflict rather than replacing it, unless the user asked to overwrite.
6. **Write the output and report**
   Write the table to the chosen destination through the agent's own connection (CSV file, Google Sheet, or Attio company records). Then report counts: unique domains, enriched, no match, skipped, conflicts, and records used against what remains.

## Checks before returning

- Every input row is accounted for exactly once: enriched, no match, skipped as not a domain, or duplicate of another row.
- No domain was enriched twice in the run; duplicates were collapsed before any call.
- Each enriched field carries its source and checked date; flag fields with an old checked date rather than presenting them as current.
- Records used matches the enriched count, and the run stopped cleanly with a resume point if a five-hour or weekly limit was reached.
- If more than a small share of domains returned no match, say so and show examples so the user can check for typos, parked domains or subsidiaries.

## Output

One table, original row order, with columns: input_value, domain, company_name, industry, headcount_band, location, tech_stack, source, checked_at, status (enriched, no_match, skipped, duplicate), notes. In Google Sheets this is tab "Enriched" plus tab "Needs review" holding no_match, skipped and conflict rows; in CSV the same split is two files. In Attio, only empty fields are written unless overwrite was requested, and conflicts are returned as a list. This skill returns company data only, so there are no email addresses and no verified, catch-all, unknown or invalid labels in the output; pair it with a people skill for contacts.

## Example

> Here's a sheet of 240 target account websites from our event list. Add industry, headcount band, HQ location and tech stack, and flag anything you couldn't match.

```
✓ 240 rows · 226 unique domains · 6 skipped (not a domain)
✓ 13,880 enrichment records left this window
✓ 211 enriched · 15 no match (no records used)
→ Sheet "Event accounts – enriched" updated, 2 tabs: Enriched, Needs review
```

Illustrative output.

## Cost and limits

enrich_company uses 1 enrichment record per company returned; a 404 or empty result uses no records but still counts as one request. Requests are capped at five times the record allowance, so normal retries do not hit them. On Free, records come from the one-time 1,000 shared across search and enrichment. On paid plans the run draws on the enrichment window (Solo 1k per five hours and 5k per week, Pro 15k and 75k, Team 150k and 750k, Max 225k and 1.125M). The skill calls get_usage first at no cost, dedupes before calling so no record is spent twice, reads the usage object on each response, and splits large lists across windows. No scrape units are used.

## What it doesn't do

- Find people or emails at the companies; use a people search or contacts-at-target-accounts skill for that.
- Scrape company websites or careers pages for products, positioning or hiring signals; that needs scrape_company or scrape_jobs and scrape units.
- Overwrite existing CRM or sheet values by default; conflicts are reported for a human to decide.
