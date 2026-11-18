---
name: positioning-snapshot
description: "Reads a company's own public pages with scrape_company and returns a short positioning snapshot: what it sells, how it prices, who it sells to and how it describes itself, with each claim tied to the page it came from. Use when someone asks what a company does, who it sells to, how it prices, or wants a positioning snapshot or quick read of a domain before outreach."
license: MIT
metadata:
  title: "Positioning snapshot"
  category: "Company research"
  outcome: "Research accounts and timing"
  tools: [get_usage, scrape_company]
  version: "1.0"
  author: Leadsets
  homepage: https://www.leadsets.ai/skills?utm_source=github&utm_medium=leadsets-skills&utm_campaign=positioning-snapshot
---

# Positioning snapshot

Turns one domain or a short list of domains into a one-screen positioning snapshot built only from the company's own pages: products, pricing model, ideal customer and positioning, with source links. Built for founders, SDRs and GTM engineers who want to understand an account before writing to it, without reading the whole site.

**Category:** Company research · **Outcome:** Research accounts and timing · **Tools:** `get_usage`, `scrape_company`

## Requirements

- The Leadsets MCP server connected to your agent: `https://mcp.leadsets.ai` ([setup](https://www.leadsets.ai/docs/mcp?utm_source=github&utm_medium=leadsets-skills&utm_campaign=positioning-snapshot)), or a Leadsets API key for the REST API.
- A Leadsets account. The free plan includes 1,000 records, no card ([get a key](https://www.leadsets.ai/signup?utm_source=github&utm_medium=leadsets-skills&utm_campaign=positioning-snapshot)).

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

- "What does stackfold.io actually sell, and who to?"
- "Give me a positioning snapshot of these 10 target accounts before I write sequences."
- "How does Parcelry price: per seat, usage or contact sales?"
- Before a discovery call or account review, when the user needs the company's own framing of its product and buyer
- When an account list needs a consistent 'sells / sells to / pricing model' column added

## What you give it

- **Domains**: One domain or a list of company domains, for example stackfold.io, parcelry.co. Plain URLs are fine; the skill normalises them to the domain.
- **Your offer** (optional): Optional one-line description of what you sell. If given, the snapshot adds one line on what this company would likely care about, clearly marked as inference. Default: omitted.
- **Where it goes** (optional): Default: returned in the chat as one snapshot per company. Can also be written as rows to a CSV or Google Sheet, or posted to a Slack channel through the agent's own connection to that system.
- **Unit budget** (optional): Optional cap on scrape units for the run. Default: no more than the units the user has left, and the skill asks before spending more than 100 units in one run.

## Steps

1. **Confirm the domains and the destination**
   Normalise every input to a bare domain, drop duplicates and obvious non-company domains (personal email providers, link shorteners). If a name was given instead of a domain and it is ambiguous, ask one question to confirm the right domain. Confirm where the snapshot goes; default to the chat.
2. **Check scrape units before spending any** · `get_usage`
   Call get_usage (it costs nothing) and read scrape_units. If scraping is not available on the account (the free plan does not include scrape_company), stop and tell the user that scraping is an add-on on paid plans billed in units, with packs from $9 for 1,000. If units left are fewer than the domain count, say how many domains fit and ask which to run first.
3. **Probe with one domain** · `scrape_company`
   Call scrape_company on the first domain only. Check that it returns products, positioning, customers named and key links, and note pages_read and units_used. Use that units_used figure to estimate the cost of the full list and tell the user before continuing if the estimate exceeds the unit budget.
4. **Scrape the remaining domains** · `scrape_company`
   Call scrape_company once per remaining domain. Read units_used on each response and stop before the budget is crossed. On a 429, wait for the Retry-After time and retry with the same Idempotency-Key (REST API). On 404 not_found or a domain that returns nothing usable, record it as 'no readable public pages' and move on; do not retry. On 403 forbidden, stop and report that the key does not allow scraping.
5. **Build the snapshot from what the pages say**
   For each company write: Sells (products in the company's own terms), Pricing model (per seat, usage-based, tiered, free tier, contact sales, or 'not stated on public pages'), Sells to (industry, size and roles the site targets), Positioning (one sentence on how it describes itself), Customers named (as listed on the site), and Key links (pricing, product, customers pages). Use only facts from the scraped pages. Never guess a price or pricing model that the pages do not show. If Your offer was given, add one 'Likely cares about' line marked as inference.
6. **Deliver and report**
   Return the snapshots in the chat, or write them as rows to the CSV or Google Sheet, or post one message per company to the Slack channel through the agent's own connection. End with a run summary: domains snapshotted, domains with no readable pages, pricing not stated, units used and units left.

## Checks before returning

- Every field in a snapshot traces to a scraped page; anything not found reads 'not stated on public pages' rather than a guess.
- Pricing model is only filled when the site shows pricing or explicitly says contact sales; inferred lines are labelled as inference.
- Units used for the run match the sum of units_used across responses and stay inside the unit budget and units left from get_usage.
- Duplicate domains are scraped once, and domains that returned nothing are listed separately, not silently dropped.
- No contact names or emails are added; the snapshot describes the company only.

## Output

One snapshot per company with these fields: domain, company, sells, pricing_model, sells_to, positioning, customers_named, key_links, likely_cares_about (only if Your offer was given, marked inference), pages_read, units_used, scraped_at. In a sheet or CSV each company is one row with those columns on a tab or file named "Positioning snapshots"; domains with no readable public pages go to a second tab or file "Not readable" with the reason. In Slack, one message per company with the same fields. The skill returns no email addresses, so there are no verified, catch-all, unknown or invalid statuses to handle; to add contacts, hand the domains to a prospecting skill.

## Example

> Give me a positioning snapshot of stackfold.io and parcelry.co: what they sell, how they price and who they sell to. We sell RevOps tooling to mid-market SaaS.

```
✓ 2 domains confirmed  ·  ✓ 320 scrape units left
✓ stackfold.io probed: 6 pages, 6 units
✓ 2 snapshots built  ·  pricing stated for 1, 'contact sales' for 1
→ Snapshots returned in chat, 12 units used, 308 left
```

Illustrative output.

## Cost and limits

scrape_company uses 1 scrape unit per standard page read and does not touch search or enrichment records. Page depth per domain is capped, so one domain costs a predictable number of units; the probe on the first domain sets the estimate for the rest. Scraping is not on the free plan; it is an add-on on every paid plan, with packs of $9 for 1,000 units, $19 for 5,000 and $49 for 20,000, which do not expire while subscribed. get_usage is free and is called first to read units left. On a 429 the skill waits for Retry-After, and blocked calls count against nothing; Idempotency-Keys keep retries from counting twice.

## What it doesn't do

- Does not read pages behind a login or paywall, or any non-public content; it uses public company pages only and respects robots signals.
- Does not invent prices, plan names or customer logos that are not on the company's own pages.
- Does not find people or emails at the company; pair it with a prospecting or decision-maker skill for contacts.
