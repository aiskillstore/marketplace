---
name: account-research-brief
description: "Reads a company's public website with scrape_company and adds firmographics with enrich_company, then writes a one-page account brief: what the company sells, who it sells to, proof points and grounded angles to open with. Every claim traces back to a scraped or enriched field. Use when someone asks to research an account, prep for a call, write a company brief or find an angle for a domain."
license: MIT
metadata:
  title: "Account research brief"
  category: "Company research"
  outcome: "Research accounts and timing"
  tools: [get_usage, scrape_company, enrich_company]
  version: "1.0"
  author: Leadsets
  homepage: https://www.leadsets.ai/skills?utm_source=github&utm_medium=leadsets-skills&utm_campaign=account-research-brief
---

# Account research brief

Turns a company domain into a one-page brief covering what they sell, who they sell to, who they name as customers and two or three angles worth opening with. Built for founders, SDRs and GTM engineers who want account research grounded in the company's own pages, not a guess dressed up as insight.

**Category:** Company research · **Outcome:** Research accounts and timing · **Tools:** `get_usage`, `scrape_company`, `enrich_company`

## Requirements

- The Leadsets MCP server connected to your agent: `https://mcp.leadsets.ai` ([setup](https://www.leadsets.ai/docs/mcp?utm_source=github&utm_medium=leadsets-skills&utm_campaign=account-research-brief)), or a Leadsets API key for the REST API.
- A Leadsets account. The free plan includes 1,000 records, no card ([get a key](https://www.leadsets.ai/signup?utm_source=github&utm_medium=leadsets-skills&utm_campaign=account-research-brief)).

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

- Research northwind.co before my call tomorrow
- Read stackfold.io and tell me who they sell to and what they'd care about
- Give me a one-page brief and opening angles for each of these 10 target accounts
- What does Parcelry actually sell, and how should I open with them?
- Prep account notes for a deal review from a list of domains

## What you give it

- **Company domains**: One domain or a list, for example northwind.co. Duplicates and protocol prefixes are stripped. Default cap 10 domains per run; ask before going higher.
- **What you sell** (optional): One or two sentences on your product and buyer, used to shape the angles. If missing, the brief still runs and the angles are kept generic and labelled as such.
- **Where it goes** (optional): Default: returned in chat as one brief per domain. Optional: a Google Sheet or CSV with one row per domain, written through the agent's own connection to that system.

## Steps

1. **Confirm domains and offer**
   Normalise the domain list (lowercase, strip https:// and paths, remove duplicates). Confirm what the user sells. If the offer is unclear, ask one question; otherwise move on.
2. **Check limits and plan the run** · `get_usage`
   Call get_usage (costs nothing). Read scrape_units and enrichment records left in this window and this week. scrape_company needs scrape units, which are an add-on on paid plans and not available on Free. If no units are available, tell the user and offer an enrich_company-only brief, clearly marked as partial with no products, positioning or customers named.
3. **Probe with one domain** · `scrape_company`
   Call scrape_company on the first domain only. Check that sells, sells_to and key links came back, and note pages_read and units_used. Multiply units_used by the number of domains to estimate the run. If the estimate exceeds remaining units, tell the user and either trim the list or stop for confirmation.
4. **Scrape the remaining domains** · `scrape_company`
   Call scrape_company for each remaining domain. If a domain returns nothing useful (no public homepage, robots signals, empty profile), record it as 'site not readable' and move on. On 429, wait for Retry-After and retry; do not retry 400 or 403.
5. **Add firmographics** · `enrich_company`
   Call enrich_company for each domain to get industry, headcount band, location and stack, keeping the source and last-checked date for every field. On 404 not_found, note 'no firmographics' and move on. Use the same Idempotency-Key on any retry so records are never counted twice.
6. **Write the brief**
   For each domain write: one-line summary, what they sell, who they sell to, customers named on the site, firmographics, and two or three opening angles that connect a specific fact to the user's offer. Tag each angle with the field it rests on. Mark anything inferred as inference. Do not invent customers, pricing or metrics the scrape did not return.
7. **Deliver and report**
   Return the briefs in chat, or write one row per domain to the requested Sheet or CSV. Finish with a run summary: briefs written, domains not readable, units and enrichment records used, and what is left from the usage object.

## Checks before returning

- Every fact in a brief maps to a scrape_company or enrich_company field; anything else is labelled inference or removed.
- Domains that returned empty scrapes or 404 on enrichment are listed separately, not padded with guesses.
- Units used match the probe estimate, and the run stopped before exceeding the scrape units or enrichment records reported by get_usage.
- No duplicate domains, and firmographic fields older than their last-checked date flagged as possibly stale are noted.
- Angles are specific to the account; if two briefs share the same angle wording, rewrite or flag them.

## Output

Per domain, a one-page brief with these fields: Company, Domain, Summary (one line), What they sell, Who they sell to, Customers named, Industry, Headcount band, Location, Stack, Key links, Angles (2 to 3, each with the source field), Inferences, Sources and last-checked dates, Status (complete, partial: firmographics only, or site not readable). In a Sheet or CSV this is one row per domain on a tab named 'Account briefs', with a second tab 'Not readable' for failed domains. The brief contains no contact emails, so verified, catch-all, unknown and invalid statuses do not apply; hand off to a contact skill for people and emails.

## Example

> Research northwind.co, stackfold.io and parcelry.co. We sell a pipeline forecasting tool to RevOps teams. Give me a brief and opening angles for each.

```
✓ 3 domains confirmed  ·  ✓ 320 scrape units and 13,212 enrichment records left
✓ Probe: northwind.co read 6 pages, 6 units  ·  est. 18 units for the run
✓ 3 sites scraped (17 units)  ·  ✓ 3 companies enriched
✓ 3 briefs, 8 angles  ·  0 sites not readable
→ Briefs returned in chat, sources and checked dates under each
```

Illustrative output.

## Cost and limits

scrape_company uses 1 scrape unit per page read, with capped page depth so one domain is a predictable number of units. Scrape units are an add-on on paid plans (packs of 1,000, 5,000 or 20,000) and scraping is not on the Free plan. enrich_company uses 1 enrichment record per record returned; an empty result uses no records but still counts as one request. get_usage is free and runs first, and the one-domain probe sets the unit estimate before the batch. On 429 the skill waits for Retry-After, and blocked calls count against nothing.

## What it doesn't do

- Find contacts or emails at the account; pair it with a decision-makers or contacts skill for that.
- Read pages behind a login, paywalled content or anything other than public company pages.
- Invent customers, pricing, revenue or pain points the scraped and enriched fields do not support.
