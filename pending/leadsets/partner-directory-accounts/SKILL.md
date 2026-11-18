---
name: partner-directory-accounts
description: "Reads a public partner, integrations or marketplace directory with scrape_company, extracts every listed company and its domain, then fills industry, headcount band, location and stack with enrich_company. Returns a deduplicated, sourced account list. Use when someone says \"turn this partner page into accounts\", \"list every company in this integrations directory\" or \"who is in their app marketplace\"."
license: MIT
metadata:
  title: "Partner directory to account list"
  category: "Web scraping"
  outcome: "Find new prospects"
  tools: [get_usage, scrape_company, enrich_company]
  version: "1.0"
  author: Leadsets
  homepage: https://www.leadsets.ai/skills?utm_source=github&utm_medium=leadsets-skills&utm_campaign=partner-directory-accounts
---

# Partner directory to account list

Turns a public partner or integrations directory into a clean account list with firmographics on every row, sourced and dated. Built for GTM engineers and agencies who want to prospect an ecosystem (a platform's partners, an integrations marketplace) without copying names by hand.

**Category:** Web scraping · **Outcome:** Find new prospects · **Tools:** `get_usage`, `scrape_company`, `enrich_company`

## Requirements

- The Leadsets MCP server connected to your agent: `https://mcp.leadsets.ai` ([setup](https://www.leadsets.ai/docs/mcp?utm_source=github&utm_medium=leadsets-skills&utm_campaign=partner-directory-accounts)), or a Leadsets API key for the REST API.
- A Leadsets account. The free plan includes 1,000 records, no card ([get a key](https://www.leadsets.ai/signup?utm_source=github&utm_medium=leadsets-skills&utm_campaign=partner-directory-accounts)).

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

- "Turn stackfold.io/partners into an account list with industry and size."
- "Which companies are listed in Parcelry's integrations directory, and which fit our ICP?"
- Building a target list from a technology ecosystem or app marketplace before finding contacts.
- Mapping a competitor's or platform's partner network to find lookalike accounts.
- Refreshing an old partner list to see who is still listed and what changed.

## What you give it

- **Directory URL**: The public partner, integrations or marketplace page, for example stackfold.io/partners. Public pages only; nothing behind a login.
- **ICP filter** (optional): Optional industry, headcount band, location or technology to keep. Default: no filter, return every listed company with its firmographics.
- **Max accounts** (optional): Cap on how many partner domains to enrich. Default 200, or every partner found if fewer.
- **Where it goes** (optional): CSV (default), Google Sheets, or a CRM such as HubSpot or Attio through the agent's own connection to that system.

## Steps

1. **Confirm the directory and scope**
   Restate the directory URL, the ICP filter (if any), the cap and the destination. Ask one question only if the URL points to a login page or the filter is ambiguous. If the user is on the free plan, explain that scraping is not on Free and offer to enrich a pasted list of partner domains instead.
2. **Check limits and scrape units** · `get_usage`
   Call get_usage. Read scrape units left and enrichment records left in the five-hour window and the week. If scrape units are zero, stop and say a units pack is needed. If enrichment records left are below the planned account count, plan to split the run across windows and tell the user.
3. **Read the directory** · `scrape_company`
   Call scrape_company on the directory URL. Check pages_read and units_used against the plan, then confirm the response contains partner names and key links. If it returns only the owner's own products and no partners, report that the page structure did not expose a partner list and stop before spending more units.
4. **Build the domain list**
   From the scraped names and links, extract one domain per partner. Normalise to the root domain, drop duplicates, drop the directory owner's own domain and drop non-company links (docs, social, app store pages). Keep the partner name and any category or tier the directory shows. Apply the max accounts cap.
5. **Probe enrichment with one domain** · `enrich_company`
   Call enrich_company on the first domain. Confirm firmographics come back with source and checked dates. A 404 not_found means nothing to enrich for that input: pick another domain and probe again before moving on.
6. **Enrich every partner** · `enrich_company`
   Call enrich_company for each remaining domain with an Idempotency-Key per domain. On 404 not_found, mark the row "not found" and move on. On 429 window_full, wait Retry-After then retry with the same key. On 429 weekly_limit, stop, save progress and report the resets_at time. Read the usage object every response returns and pause before crossing the window.
7. **Filter against the ICP**
   If an ICP filter was given, mark each account fit or not fit using the enriched industry, headcount band, location and stack, with a one-line reason. Do not drop non-fit rows silently; keep them on a separate tab or section.
8. **Deliver and report**
   Write the list to the chosen destination through the agent's own connection. Report partners found, domains resolved, enriched, not found, fit and not fit, plus scrape units and enrichment records used.

## Checks before returning

- Scrape units were available before scrape_company ran, and units_used matches the page count reported.
- Every domain appears once; the directory owner's domain and non-company links are excluded.
- Rows with no enrichment are labelled "not found", never filled with guesses.
- Each enriched field keeps its source and checked date from enrich_company.
- If the directory yielded zero partners, the run stops and says so instead of returning an empty file.

## Output

One table with columns: partner_name, domain, directory_category (if shown), industry, headcount_band, location, technologies, icp_fit (fit / not fit / no filter), fit_reason, enrich_status (enriched / not found), source, checked_at, directory_url. In Google Sheets: tabs "Accounts", "Not fit" and "Not found". In CSV: one file with the icp_fit and enrich_status columns. This skill returns accounts only, no emails, so there are no catch-all, unknown or invalid addresses in the output; hand the fit accounts to a contacts skill such as Contacts at target accounts, which labels every email by verification status.

## Example

> Turn the partner directory at stackfold.io/partners into an account list. Keep US companies with 50 to 500 people and put it in a Google Sheet.

```
✓ 31 scrape units left  ·  ✓ 1,000 enrichment records left this window
✓ Directory read: 4 pages, 4 units  ·  ✓ 87 partners, 82 unique domains
✓ 76 enriched  ·  6 not found  ·  41 fit ICP, 35 not fit
→ Sheet "Stackfold partners – Nov" created, 3 tabs
```

Illustrative output.

## Cost and limits

scrape_company uses 1 scrape unit per standard page read, with capped page depth so one directory is a predictable number of units; scraping is an add-on on paid plans and not available on Free. enrich_company uses 1 enrichment record per company returned with data; a not_found result uses no records but counts as one request. The skill calls get_usage (free) before starting, reads the usage object on every response, splits runs that would cross the five-hour or weekly enrichment limit, and retries 429 window_full only after Retry-After with the same Idempotency-Key (REST API) so nothing is counted twice.

## What it doesn't do

- Read pages behind a login, paywalled member areas or private partner portals.
- Find people or emails at the partner accounts; it stops at the account list.
- Guess firmographics for domains enrich_company could not match.
