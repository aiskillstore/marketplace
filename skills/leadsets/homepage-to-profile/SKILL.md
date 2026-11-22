---
name: homepage-to-profile
description: "Turns one or more company homepages into structured profiles: what the company sells, who it sells to, positioning, customers named on the site and key links, using Leadsets scrape_company. Checks scrape units first and probes one domain before a batch. Use when someone asks to profile a company website, summarize what a domain sells, or turn a list of homepages into a research sheet."
license: MIT
metadata:
  title: "Homepage to company profile"
  category: "Web scraping"
  outcome: "Research accounts and timing"
  tools: [get_usage, scrape_company]
  version: "1.0"
  author: Leadsets
  homepage: https://www.leadsets.ai/skills?utm_source=github&utm_medium=leadsets-skills&utm_campaign=homepage-to-profile
---

# Homepage to company profile

Gives you a clean, structured profile of any company from its own public homepage: products, audience, proof points such as named customers, and the links worth reading next. Built for founders, SDRs and GTM engineers who want account context in a table instead of ten open browser tabs.

**Category:** Web scraping · **Outcome:** Research accounts and timing · **Tools:** `get_usage`, `scrape_company`

## Requirements

- The Leadsets MCP server connected to your agent: `https://mcp.leadsets.ai` ([setup](https://www.leadsets.ai/docs/mcp?utm_source=github&utm_medium=leadsets-skills&utm_campaign=homepage-to-profile)), or a Leadsets API key for the REST API.
- A Leadsets account. The free plan includes 1,000 records, no card ([get a key](https://www.leadsets.ai/signup?utm_source=github&utm_medium=leadsets-skills&utm_campaign=homepage-to-profile)).

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

- "Read stackfold.io and tell me what they sell and who they sell to."
- "Profile these 30 domains from their homepages and put it in a sheet."
- "Which customers does parcelry.co name on its site?"
- Before writing outreach or tiering accounts, when you need what a company says about itself in a structured form
- When a CRM has company records with domains but no description of products or audience

## What you give it

- **Domains**: One domain or a list (pasted, CSV or Google Sheet column). Bare domains or full URLs are fine; the skill normalizes them to the homepage.
- **Fields to keep** (optional): Default: products, sells_to, positioning, customers named, key links. Narrow it if you only need one thing, such as customers named.
- **Where it goes** (optional): Chat summary for 1 to 3 domains, otherwise CSV or Google Sheets. Default: CSV.
- **Unit budget** (optional): Maximum scrape units to spend on this run. Default: stop if remaining units would drop below what the full list needs and ask before continuing.

## Steps

1. **Confirm the domains and the output**
   Normalize every input to a bare domain, drop duplicates and obvious non-company domains, and confirm the count and destination with the user. Ask one question only if the list is ambiguous, for example a subdomain versus the main site.
2. **Check scrape units and plan the run** · `get_usage`
   Call get_usage (it costs nothing) and read scrape_units. If the account is on the free plan or has no scrape units, stop and explain that scrape_company is a paid add-on in units (packs from $9 for 1,000) rather than calling the tool. Otherwise estimate the run at a few pages per domain, since scrape_company caps page depth per domain, and compare against remaining units and the user's budget.
3. **Probe with one domain** · `scrape_company`
   Call scrape_company on the first domain only. Check that it returns sells, sells_to and key links, and note pages_read and units_used. Use units_used from this probe to re-estimate the full run before moving on; if the estimate exceeds remaining units or budget, tell the user and offer to run a subset.
4. **Profile the remaining domains** · `scrape_company`
   Call scrape_company for each remaining domain in small batches. After each batch, read units_used and stop before the budget is crossed. On a 429, wait for the Retry-After time and retry; the blocked call counts against nothing. If a domain returns nothing usable, mark it no data and move on rather than retrying.
5. **Assemble the profiles**
   For each domain, map the result to: products, sells_to, positioning (one line in the company's own terms), customers named, and key links (pricing, customers or case studies, careers, docs where present). Keep only what the page states. Leave a field empty and flag it rather than guessing an audience or customer the site does not name.
6. **Deliver and report**
   Return a chat summary for up to 3 domains, otherwise write the table to the chosen CSV or Google Sheet through the agent's own connection. End with a run summary: domains profiled, domains with no data, units used and units left.

## Checks before returning

- get_usage was called before any scrape and the run stayed inside remaining scrape units and the user's budget
- Every domain appears once; duplicates and redirects to the same site were merged
- Each profile field comes from the scraped page; empty fields are flagged, not filled with guesses
- Domains with no usable result are listed separately with the reason (no data, blocked or unreachable) instead of silently dropped
- Units used per domain and in total are reported, so the user can plan the next batch

## Output

One row per domain with columns: domain, company, products, sells_to, positioning, customers_named, key_links, pages_read, units_used, status (profiled or no data). For CSV or Google Sheets, write a "Profiles" tab and a "No data" tab listing domains that returned nothing usable and why. For 1 to 3 domains, return the same fields as a short profile per company in chat. This skill returns no contact data, so no email statuses apply; if the user wants people or verified emails, hand the domains to a prospecting or enrichment skill.

## Example

> Profile these 25 domains from their homepages: what they sell, who they sell to and which customers they name. Put it in a Google Sheet.

```
✓ 25 domains, 24 unique  ·  ✓ 1,840 scrape units left
✓ Probe on stackfold.io: 6 pages, 6 units
✓ 22 profiled  ·  2 no data (separate tab)  ·  131 units used
→ Sheet "Homepage profiles – Nov" created, 2 tabs
```

Illustrative output.

## Cost and limits

scrape_company uses 1 scrape unit per standard page read and does not touch search or enrichment records. Page depth is capped per domain, so each domain costs a predictable number of units, reported as units_used. Scraping is a units add-on on paid plans (packs of 1,000 for $9, 5,000 for $19, 20,000 for $49) and is not available on the free plan. The skill calls get_usage first at no cost, probes one domain to measure units per domain, and stops before crossing the user's budget or remaining units. Over a limit, Leadsets returns a 429 with a Retry-After time and the blocked call counts against nothing.

## What it doesn't do

- Find people or emails at the company; use a prospecting or enrichment skill for contacts and verified emails
- Read anything behind a login, paywall or outside the public homepage pages scrape_company reads
- Invent firmographics, audience or customers the site does not state; it does not call enrich_company for headcount or industry
