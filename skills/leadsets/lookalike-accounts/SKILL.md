---
name: lookalike-accounts
description: "Starts from a short list of your best customers, enriches each domain with enrich_company, turns their shared firmographics into filters, and finds new companies that look like them with search_companies. Returns a ranked account list with match reasons, existing customers removed. Use when someone asks for lookalike accounts, companies like our best customers, more accounts like these, or an account list from customer domains."
license: MIT
metadata:
  title: "Lookalike accounts"
  category: "Prospecting"
  outcome: "Find new prospects"
  tools: [get_usage, enrich_company, search_companies]
  version: "1.0"
  author: Leadsets
  homepage: https://www.leadsets.ai/skills?utm_source=github&utm_medium=leadsets-skills&utm_campaign=lookalike-accounts
---

# Lookalike accounts

Turns the domains of your best customers into a ranked list of new accounts with the same industry, headcount band, technology and location profile. Built for founders, GTM engineers and agencies who want a target account list grounded in who already buys, not a guessed ICP.

**Category:** Prospecting · **Outcome:** Find new prospects · **Tools:** `get_usage`, `enrich_company`, `search_companies`

## Requirements

- The Leadsets MCP server connected to your agent: `https://mcp.leadsets.ai` ([setup](https://www.leadsets.ai/docs/mcp?utm_source=github&utm_medium=leadsets-skills&utm_campaign=lookalike-accounts)), or a Leadsets API key for the REST API.
- A Leadsets account. The free plan includes 1,000 records, no card ([get a key](https://www.leadsets.ai/signup?utm_source=github&utm_medium=leadsets-skills&utm_campaign=lookalike-accounts)).

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

- "Find 200 companies that look like our top 10 customers."
- "Here are our best accounts: northwind.co, stackfold.io, parcelry.co. Who else looks like them?"
- Building a target account list before running a contacts or prospect list skill
- Expanding into a new region with the same customer profile that works at home
- Refreshing an account list when the current one is worked out

## What you give it

- **Seed customers**: 3 to 20 domains of your best customers, pasted, from a CSV or Google Sheet, or read from your CRM through the agent's own connection. At least 3 are needed to find shared traits.
- **How many accounts** (optional): Target list size. Default 100.
- **Exclusions** (optional): Domains to leave out: current customers, open deals, competitors. Defaults to excluding the seed domains only.
- **Overrides** (optional): Any trait to fix or relax, such as region or headcount band. Default: take everything from the seeds.
- **Where it goes** (optional): CSV, Google Sheets or a CRM through the agent's own connection. Default CSV.

## Steps

1. **Check limits and plan the run** · `get_usage`
   Call get_usage. Confirm enrichment records cover one per seed domain and search records cover the target list size plus about 30% for exclusions and duplicates. If the free plan is close to its 1,000 records or a window would be crossed, tell the user the plan and offer a smaller list or a split run.
2. **Enrich the seed customers** · `enrich_company`
   Call enrich_company once per seed domain. Record industry, headcount band, location and technology, with the source and checked date on each field. If a domain returns 404 not_found, note it and move on. Stop and ask for more seeds if fewer than 3 enrich.
3. **Derive the lookalike profile**
   Find the traits most seeds share: the most common industries, the headcount band range that covers most seeds, shared technologies and locations. Drop traits shared by only one seed. Show the profile to the user in one short block and ask one question only if something is ambiguous, such as seeds split across two industries.
4. **Probe the filters** · `search_companies`
   Call search_companies with the derived industry, headcount band, technology and location filters and limit 1. Check the result matches the profile and read its match reasons. If it returns nothing, relax the narrowest filter (usually technology) and probe again. Empty probes use no records.
5. **Pull the accounts** · `search_companies`
   Run the full search, paging with the cursor until you reach the target size plus headroom. Respect plan concurrency (3 searches on Solo, 5 on Pro, 8 on Team and Max). On 429 window_full wait for Retry-After and retry with the same Idempotency-Key (REST API); on 429 weekly_limit stop and report where to resume.
6. **Exclude, dedupe and rank**
   Remove seed domains, user exclusions and duplicate domains. Score each account by how many profile traits it matches, using the returned match reasons, and note which seeds it most resembles. Trim to the target size, highest score first.
7. **Deliver the list**
   Write the ranked list to the chosen destination through the agent's own connection, with the derived profile on a separate tab or in a header note. Report counts: seeds enriched, accounts found, excluded, returned.

## Checks before returning

- Every seed customer and every exclusion domain is absent from the final list
- No duplicate domains, and each account has at least one match reason
- The derived profile is shown, and any relaxed filter is named in the summary
- Seeds that could not be enriched and any shortfall against the target size are reported, not hidden
- Records spent match get_usage before and after, and no 429 left a page silently missing

## Output

One table, one row per account: rank, company name, domain, industry, headcount band, location, technology, match reasons, traits matched (for example 3 of 4), most similar seed. A second tab or section holds the lookalike profile and the enriched seed customers with source and checked date. File or tab names follow "Lookalikes - <month>". The skill returns accounts only, no contacts or emails, so verified, catch-all, unknown and invalid statuses do not apply here; they are handled when the list is passed to a contacts or prospect list skill.

## Example

> Our best customers are northwind.co, stackfold.io, parcelry.co and four others in this sheet. Find 100 companies that look like them, skip anyone already in our customer list, and put it in a Google Sheet.

```
✓ 13,212 enrichment and 6,940 search records left this window
✓ 7 of 7 seeds enriched  ·  profile: B2B SaaS, 50-200 people, US, shared stack
✓ 141 accounts found  ·  23 existing customers removed  ·  18 lower fit trimmed
→ Sheet "Lookalikes - Nov" created: 100 ranked accounts, profile tab
```

Illustrative output.

## Cost and limits

enrich_company uses 1 enrichment record per seed returned with data; search_companies uses 1 search record per account returned. Empty probes and errors use no records, though every call counts as one request, and the request limit is five times the record allowance. No scrape units are used, so the skill runs on the free plan's 1,000 one-time records. It calls get_usage first (free), probes with limit 1 before paging, pulls only modest headroom over the target, and splits the run or waits on Retry-After if a five-hour or weekly window would be crossed.

## What it doesn't do

- Find people or emails at the accounts; hand the list to the contacts at target accounts or outbound prospect list skill for that
- Scrape company websites or careers pages; it uses firmographics from enrich_company and search_companies only
- Write to a CRM or sequencer unless the user names a destination, and never overwrites existing records
