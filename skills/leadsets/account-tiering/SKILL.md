---
name: account-tiering
description: "Scores an account list against a user's ICP using enrich_company firmographics and, where needed, scrape_company website profiles, then sorts every account into tiers with written reasons and sourced evidence. Use when someone asks to tier, score, rank or prioritize accounts, check ICP fit for a list of domains, or decide which target accounts to work first."
license: MIT
metadata:
  title: "Account tiering"
  category: "Company research"
  outcome: "Research accounts and timing"
  tools: [get_usage, enrich_company, scrape_company]
  version: "1.0"
  author: Leadsets
  homepage: https://www.leadsets.ai/skills?utm_source=github&utm_medium=leadsets-skills&utm_campaign=account-tiering
---

# Account tiering

Takes a list of company domains and your ICP, scores each account against it, and returns Tier A, B, C or Out with the reasons and the fields behind each score. Built for founders, SDR leads and GTM engineers who have more accounts than time and want a defensible order to work them in.

**Category:** Company research · **Outcome:** Research accounts and timing · **Tools:** `get_usage`, `enrich_company`, `scrape_company`

## Requirements

- The Leadsets MCP server connected to your agent: `https://mcp.leadsets.ai` ([setup](https://www.leadsets.ai/docs/mcp?utm_source=github&utm_medium=leadsets-skills&utm_campaign=account-tiering)), or a Leadsets API key for the REST API.
- A Leadsets account. The free plan includes 1,000 records, no card ([get a key](https://www.leadsets.ai/signup?utm_source=github&utm_medium=leadsets-skills&utm_campaign=account-tiering)).

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

- "Tier these 300 accounts against our ICP before we assign them to reps."
- "Which of the domains in this sheet are actually a fit? Rank them."
- "Score our HubSpot target accounts A, B, C and tell me why."
- A user has a raw account list from an event, a partner directory or a lookalike search and needs to know where to start.
- Before running a contacts or outreach skill, when only the best-fit accounts should get spend.

## What you give it

- **Account list**: Company domains, from a pasted list, CSV, Google Sheet or a CRM view the agent can read through its own connection. Company names without domains are accepted but are flagged and only scored if a domain can be confirmed.
- **ICP**: Plain language is fine: industry, headcount band, region, technology, and what the company sells or who it sells to. The agent turns it into a weighted rubric and shows it before scoring. If an ICP builder skill already saved filters, reuse them.
- **Tier scheme** (optional): Default: Tier A, Tier B, Tier C and Out, with Out for accounts that fail a hard requirement such as region or size. The user can rename tiers, change weights or set how many accounts Tier A should hold.
- **Website research** (optional): Default: scrape_company only for borderline accounts (score within 10 points of a tier boundary) or accounts whose rubric depends on positioning or customers. Options: none, borderline only, all. Ignored on the free plan, where scraping is not available.
- **Where it goes** (optional): Default: CSV. Also Google Sheets, or a tier field in HubSpot, Salesforce, Pipedrive or Attio written through the agent's own connection to that system.

## Steps

1. **Load the list and confirm the rubric**
   Read the account list, normalize domains (lowercase, strip protocol, www and paths), and remove duplicates, keeping a count. Turn the ICP into a scoring rubric: hard requirements that send an account to Out, and weighted criteria that add up to 100. Show the rubric and tier cut-offs (default A 75+, B 50 to 74, C below 50) and ask one question only if a criterion is ambiguous.
2. **Check limits and plan the run** · `get_usage`
   Call get_usage. Read enrichment records left in the five-hour window and the week, and scrape_units. One enrich_company call per unique domain draws on enrichment; plan scrape units as up to a few pages per scraped domain. If the list exceeds what is left in the window, split it into batches that fit and tell the user when the remainder will run. If scrape_units is zero or the plan is Free, switch website research to none and say so.
3. **Probe with one account** · `enrich_company`
   Call enrich_company on one domain from the list. Confirm the fields the rubric needs (industry, headcount band, location, technology) come back with source and checked dates. If a rubric criterion has no matching field, tell the user it will need website research or will be dropped from the score before spending on the rest.
4. **Enrich every account** · `enrich_company`
   Call enrich_company for each remaining unique domain, in the batches planned in step 2, with an Idempotency-Key per call so retries never double-count. On 404 not_found, mark the account No data and move on. On 429 window_full, wait for Retry-After and resume; on 429 weekly_limit, stop and report where the run will resume. Read the usage object in each response and pause before a window fills.
5. **Research borderline accounts** · `scrape_company`
   For accounts selected by the website research setting, call scrape_company on the domain to get products, positioning, customers named and key links. Use it only to fill rubric criteria such as who the company sells to or what it sells. Track units used against the budget from step 2 and stop scraping when it is spent, noting which accounts were scored on firmographics only.
6. **Score and tier**
   Apply hard requirements first, then score each criterion from the returned fields. Write two or three short reasons per account that cite the field and its value, for example "Headcount 51-200 (enrich_company, checked 2026-11-02)" or "Sells to mid-market distributors (homepage)". Mark missing criteria as unknown rather than guessing, and lower the account's confidence instead of its score.
7. **Export and report**
   Write the table to the chosen destination through the agent's own connection. For a CRM, write only to a tier, score and reasons field the user confirmed, never over existing firmographic fields. Return a run summary: accounts in, duplicates removed, counts per tier, No data accounts, records and scrape units used.

## Checks before returning

- Every unique domain appears exactly once in the output, including No data accounts; none are silently dropped and duplicates removed are counted.
- Every tiered account has at least one reason that cites a returned field or scraped page; accounts with unknown criteria are flagged as low confidence.
- Fields with a checked date older than the source's monthly refresh, or conflicting between enrich_company and scrape_company, are noted in the reasons rather than silently used.
- Records and scrape units used match the plan from get_usage, and any batch deferred by a 429 is listed with when it will resume.
- Tier counts are sanity-checked: if more than half the list lands in Tier A or nothing does, show the distribution and offer to adjust cut-offs before exporting.

## Output

One row per unique account with columns: domain, company_name, industry, headcount_band, location, technology, score (0 to 100), tier (A, B, C, Out or No data), reasons (2 or 3 short cited lines), confidence (high or low), evidence (enrich_company, scrape_company or both), checked_at (oldest field date used). Sorted by tier, then score. In Google Sheets: tab "Tiered accounts" plus tab "No data" for domains enrich_company could not match; in CSV the same as two files; in a CRM, tier, score and reasons fields on the company record. The skill returns no contacts or emails, so verified, catch-all, unknown and invalid labels do not apply; hand Tier A to a contacts or prospect list skill for that.

## Example

> Here's a sheet of 240 domains from our event list. Our ICP is US B2B SaaS, 50 to 500 people, selling to finance or ops teams. Tier them A, B, C and add the reasons next to each one.

```
✓ 240 domains loaded  ·  6 duplicates removed  ·  ✓ 9,850 enrichment records left this window
✓ 221 enriched  ·  13 no data  ·  38 borderline scraped (112 units)
✓ Tier A 41  ·  Tier B 77  ·  Tier C 58  ·  Out 45
→ Sheet "Event accounts – tiered" updated, 2 tabs
```

Illustrative output.

## Cost and limits

enrich_company uses 1 enrichment record per account returned with data; a not_found result uses 0 records and 1 request. scrape_company uses 1 scrape unit per page read, with capped page depth per domain, and draws on no search or enrichment records. Scraping is a paid add-on and is not available on Free, so on the free plan the skill tiers on firmographics only. get_usage costs nothing and runs first. The skill dedupes domains before spending, scrapes only borderline accounts by default, splits lists that would cross the five-hour window (for example 1,000 enrichment records on Solo, 15,000 on Pro), waits on Retry-After for 429 window_full, and sends an Idempotency-Key so retries never double-count.

## What it doesn't do

- Find contacts, enrich people or return email addresses; it tiers companies only and hands Tier A to a contacts or prospect list skill.
- Guess missing firmographics or fill gaps from memory; unmatched criteria are marked unknown and unmatched domains go to No data.
- Overwrite existing CRM fields or read pages behind a login; it writes only to tier fields the user confirms and scrapes public pages only.
