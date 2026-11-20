---
name: hubspot-company-enrich
description: "Finds HubSpot companies with empty industry, size or location fields, looks up each company domain with Leadsets enrich_company, and writes back only the missing values with source and checked date. Never overwrites existing data. Use when someone asks to fill blank company fields in HubSpot, backfill firmographics, fix missing industry or headcount, or clean up company records before routing or reporting."
license: MIT
metadata:
  title: "HubSpot company enrichment"
  category: "CRM hygiene"
  outcome: "Keep your CRM clean"
  tools: [get_usage, enrich_company]
  version: "1.0"
  author: Leadsets
  homepage: https://www.leadsets.ai/skills?utm_source=github&utm_medium=leadsets-skills&utm_campaign=hubspot-company-enrich
---

# HubSpot company enrichment

Fills the empty industry, size and location fields on your HubSpot companies from their domains, and leaves every field you already have alone. Built for RevOps and GTM engineers who need clean company records for routing, segmentation and reporting without a manual research sprint.

**Category:** CRM hygiene · **Outcome:** Keep your CRM clean · **Tools:** `get_usage`, `enrich_company`

## Requirements

- The Leadsets MCP server connected to your agent: `https://mcp.leadsets.ai` ([setup](https://www.leadsets.ai/docs/mcp?utm_source=github&utm_medium=leadsets-skills&utm_campaign=hubspot-company-enrich)), or a Leadsets API key for the REST API.
- A Leadsets account. The free plan includes 1,000 records, no card ([get a key](https://www.leadsets.ai/signup?utm_source=github&utm_medium=leadsets-skills&utm_campaign=hubspot-company-enrich)).

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

- "Fill in the missing industry and employee count on our HubSpot companies."
- "Half our HubSpot accounts have no location. Can you backfill it?"
- Before building territories, lead routing or ICP reports that depend on company firmographics
- After a list import or form-fill surge left company records with a domain and little else
- "Enrich HubSpot companies created this quarter that are missing size."

## What you give it

- **Which companies** (optional): A HubSpot view, list or filter to work from. Default: every company that has a domain and at least one empty field among industry, size and location.
- **Fields to fill** (optional): Any of industry, size (headcount band) and location (city, state, country). Default: all three. The user can name the HubSpot property for each, including custom properties.
- **Max companies this run** (optional): Upper limit on companies to enrich. Default: 500, or fewer if get_usage shows less enrichment left in the current window.
- **Write mode** (optional): Preview first (default) shows a change table and waits for approval; direct mode writes to HubSpot after the probe passes. Either way, only empty fields are written.

## Steps

1. **Check limits and plan the run** · `get_usage`
   Call get_usage. Read enrichment records left in this five-hour window and this week. If the target count exceeds what is left, cap this run at the remaining window, tell the user how many will wait for the reset, and give the reset time. On the free plan, remind the user the 1,000 records are one time and shared with search.
2. **Pull companies and build the domain queue**
   Through the agent's own HubSpot connection, read the selected companies with id, name, domain and the target properties. Skip companies with no domain and count them. Normalize domains (lowercase, strip protocol, www and paths). Drop companies where all target fields are already filled. Deduplicate by domain so several HubSpot records sharing a domain are enriched once and updated together.
3. **Probe with one company** · `enrich_company`
   Call enrich_company for one domain from the queue. Confirm the response has industry, headcount band and location fields with source and checked date, and that they map cleanly to the HubSpot properties. If the user's size property is numeric and only a band comes back, do not invent a number: propose a text or dropdown property for the band, or skip size and report it. Do not continue until the mapping is agreed.
4. **Enrich the queue in batches** · `enrich_company`
   Call enrich_company for each remaining domain, sending an Idempotency-Key per domain so retries never count twice. Read the usage object on each response and stop before the window fills. On 404 not_found, mark the domain as no data and move on. On 429 window_full, wait Retry-After seconds and resume. On 429 weekly_limit, stop and report resets_at. On 402 free_records_exhausted, stop and ask the user to upgrade.
5. **Build the change set**
   For each company, keep only values for fields that are empty in HubSpot. Never replace an existing value; if Leadsets returns a different value for a filled field, log it as a conflict for review instead. Record the source and checked date for every value written.
6. **Preview and write back**
   In preview mode, show the change table (company, domain, field, new value, checked date) plus counts, and wait for approval. Then update the companies through the agent's HubSpot connection in small batches. Optionally set a note or custom property such as last enriched date so the next run can skip them.
7. **Report results**
   Return counts: companies scanned, skipped with no domain, enriched, fields filled per property, no data found, conflicts left untouched, and any companies deferred to the next window with the reset time.

## Checks before returning

- Every written field was empty in HubSpot before the run; no existing value was overwritten, and conflicts are listed separately.
- Domains were normalized and deduplicated, so no domain was enriched twice and shared-domain records got the same values.
- Companies with no domain or a not_found result are reported, not silently dropped or filled with guesses.
- Enrichment usage stayed inside the five-hour window and weekly limit shown by get_usage, with any deferred companies and the reset time stated.
- Size values match the HubSpot property type; headcount bands were never converted into made-up exact employee counts.

## Output

HubSpot company records updated in place for empty fields only. A run report with: totals (scanned, enriched, fields filled by property, no domain, no data, conflicts, deferred). A change log table with columns company_id, company_name, domain, field, old_value (empty), new_value, source, checked_at. A conflicts table with company_id, domain, field, hubspot_value, leadsets_value for human review. Optionally exported as CSV or a Google Sheet with tabs "Changes", "Conflicts" and "No data". This skill writes company firmographics only and does not touch emails, so verified, catch-all, unknown and invalid labels do not apply; use the HubSpot email backfill skill for contacts.

## Example

> Fill in missing industry, size and country on our HubSpot companies created since January. Don't touch anything that's already filled in. Show me the changes before you write.

```
✓ 8,420 enrichment records left this window  ·  612 companies with empty fields
✓ 574 unique domains  ·  38 skipped (no domain)
✓ 531 enriched  ·  43 no data  ·  1,204 fields filled  ·  17 conflicts left as-is
→ Preview approved, 531 HubSpot companies updated, change log in Sheet "Company backfill – Nov"
```

Illustrative output.

## Cost and limits

Each enrich_company call that returns data uses 1 enrichment record; a not_found result uses no records but still counts as 1 request. get_usage is free. HubSpot reads and writes go through the agent's own connection and use no Leadsets records. Deduplicating domains keeps spend to one record per unique company. On Solo that is up to 1,000 enrichments per five hours and 5,000 per week; Pro 15,000 and 75,000; free accounts have 1,000 one-time records shared with search. The skill checks get_usage first, reads the usage object as it goes, waits on 429 window_full using Retry-After, stops on weekly_limit, and sends Idempotency-Keys so retries never double-count.

## What it doesn't do

- Overwrite any company field that already has a value, or change records without logging the source and checked date.
- Create new companies or contacts in HubSpot, or enrich contact emails and roles.
- Scrape company websites or careers pages; it uses enrich_company only and spends no scrape units.
