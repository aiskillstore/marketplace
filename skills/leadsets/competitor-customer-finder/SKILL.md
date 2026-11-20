---
name: competitor-customer-finder
description: "Scrapes a competitor's website for the customer logos and case studies it publishes, resolves each named customer to a domain, then finds the right people at those companies with search_people and returns a ranked contact list with email status. Use when someone asks to find a competitor's customers, prospect into a rival's install base, or get contacts at companies on a competitor's logo wall."
license: MIT
metadata:
  title: "Competitor customer finder"
  category: "Company research"
  outcome: "Find new prospects"
  tools: [get_usage, scrape_company, search_people]
  version: "1.0"
  author: Leadsets
  homepage: https://www.leadsets.ai/skills?utm_source=github&utm_medium=leadsets-skills&utm_campaign=competitor-customer-finder
---

# Competitor customer finder

Turns a competitor's public customer logos and case studies into a list of named accounts and the people to contact there, each with match reasons and an honest email label. Built for founders, AEs and GTM engineers running displacement or competitive campaigns who want evidence for every account, not a guess.

**Category:** Company research · **Outcome:** Find new prospects · **Tools:** `get_usage`, `scrape_company`, `search_people`

## Requirements

- The Leadsets MCP server connected to your agent: `https://mcp.leadsets.ai` ([setup](https://www.leadsets.ai/docs/mcp?utm_source=github&utm_medium=leadsets-skills&utm_campaign=competitor-customer-finder)), or a Leadsets API key for the REST API.
- A Leadsets account. The free plan includes 1,000 records, no card ([get a key](https://www.leadsets.ai/signup?utm_source=github&utm_medium=leadsets-skills&utm_campaign=competitor-customer-finder)).

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

- "Who are Stackfold's customers, and who should I talk to there?"
- "Pull the logos off parcelry.co and find the heads of ops at each one."
- Planning a competitive displacement campaign against one or more named competitors
- Building a target account list from case studies a rival publishes
- "Find contacts at companies that use our competitor"

## What you give it

- **Competitor domain**: One or more competitor domains, for example stackfold.io. The skill reads public pages only.
- **Who to contact** (optional): Roles, function and seniority of your buyer in plain language. Default: vp, head and director in the function the user sells to; ask once if that is unclear.
- **Contacts per customer** (optional): Maximum people per customer account. Default 3.
- **Email requirement** (optional): Whether to keep only people with a verified work email (has_verified_email true). Default false, so catch-all and unconfirmed contacts are returned in separate sections.
- **Where it goes** (optional): CSV, Google Sheets, or a CRM or sequencer through the agent's own connection. Default CSV.

## Steps

1. **Confirm the brief**
   Confirm the competitor domains, buyer roles and contacts per customer. Ask one question only if the buyer persona is ambiguous. Tell the user scraping needs a paid plan with scrape units; it is not available on Free.
2. **Check limits and plan the run** · `get_usage`
   Call get_usage. Read search records left in the five-hour window and the week, concurrent searches and scrape_units. If scrape units are zero or the account is on Free, stop and explain that scrape_company needs a paid plan with a units add-on. Estimate search records as customers found times contacts per customer and warn if it would cross the window.
3. **Scrape the competitor's site** · `scrape_company`
   Call scrape_company once per competitor domain. Collect customers named, case study pages and key links. Record pages_read and units_used. Each customer must carry its evidence: logo or case study, plus the source page URL. If no customers are named, report that and stop for that competitor; do not invent accounts.
4. **Resolve customers to domains**
   Map each customer name to a company domain using links found on the scraped pages. Dedupe customers that appear on several pages or several competitors. Put any customer you cannot resolve with confidence in an Unresolved list instead of guessing a domain.
5. **Probe the people filters** · `search_people`
   Run search_people with limit 1, company_domain set to one resolved customer domain, plus the seniority, function and title filters. Check match_reasons fit the persona. An empty result costs 0 records and 1 request; loosen title or seniority once before moving on.
6. **Find contacts at each customer** · `search_people`
   Call search_people with company_domain batches of resolved domains, the confirmed filters, and has_verified_email if the user asked for it. Set limit to stay near contacts per customer times domains in the batch, page with next_cursor only when needed, and stay within the plan's concurrent search cap. Read the usage object after each call; on 429 window_full wait for Retry-After, on too_many_concurrent wait for a running search, and reuse the same Idempotency-Key on retries.
7. **Rank, segment and deliver**
   Keep the top contacts per customer by match_reasons and seniority. Segment by email status as returned: verified, catch-all, and unconfirmed (unknown or no email). Write the result to the chosen destination through the agent's own connection and report counts, units used and what could not be confirmed.

## Checks before returning

- Every account in the output has evidence from the competitor's own pages: logo or case study and the source URL.
- Customers are deduped by domain and people are deduped by person, with no more contacts per customer than requested.
- Catch-all and unknown emails are never placed in the verified section, and no invalid email appears as a contact.
- Customers with no resolvable domain or no matching people are listed, not silently dropped.
- Search records and scrape units used are reported against what get_usage showed at the start.

## Output

One table (CSV, or Google Sheet tabs) with columns: competitor, customer_company, customer_domain, evidence (logo or case study), source_url, full_name, title, seniority, email, email_status, checked_at, match_reasons. Tab or section "Verified" holds contacts with verified emails. "Catch-all" holds catch-all addresses, flagged to send at lower volume. "Unconfirmed" holds unknown status or no email, to enrich later or skip. Invalid emails are never served as contacts. A final "Unresolved customers" section lists names found on the site that could not be matched to a domain or returned no people.

## Example

> Find the customers stackfold.io shows on its site and get me up to 3 heads of RevOps or sales ops at each one. Put it in a CSV.

```
✓ 4,820 search records left this window  ·  ✓ 412 scrape units left
✓ stackfold.io scraped, 9 pages  ·  31 customers named  ·  27 domains resolved
✓ 64 contacts at 24 customers  ·  44 verified  ·  9 catch-all  ·  11 unconfirmed
→ "stackfold-customers.csv" written, 4 unresolved customers listed
```

Illustrative output.

## Cost and limits

scrape_company uses 1 scrape unit per page read, with capped page depth per domain; scraping is an add-on on paid plans (packs of 1k, 5k or 20k units) and is not available on Free. search_people uses 1 search record per person returned and 1 request per call; an empty search uses 0 records. get_usage costs nothing and runs first. The skill caps contacts per customer to keep search records predictable, probes with limit 1 before batching, respects the plan's concurrent search limit, and on a 429 waits for Retry-After instead of retrying blindly; blocked calls count against nothing.

## Edge cases

- **Customer named, but no link on the page:** don't look the domain up or guess it. Put the customer in the Unresolved list with the page it came from, and ask the user for domains only if they want those accounts included.
- **Evidence:** a customer counts only with a source URL to the page that names it (logo wall, case study or customer page). A bare homepage URL is enough only when the homepage itself shows the logo or quote.

## What it doesn't do

- Does not guess customers or domains that the competitor's public pages do not name, and never reads pages behind a login.
- Does not run enrich_person or verify_email; pass the Unconfirmed section to an enrichment or verification skill if you need more send-ready emails.
- Does not write outreach or send anything; it hands the list to your CRM, sheet or sequencer.
