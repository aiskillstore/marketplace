---
name: decision-makers-at-company
description: "Turns one company domain into a ranked list of the people most likely to buy what you sell. Uses enrich_company to size and classify the account, then search_people filtered to that domain, and ranks each person by role in the deal with match reasons and email status. Use when someone asks \"who should I talk to at this company\", \"find the decision-makers at stackfold.io\" or \"map the buyers at this account\"."
license: MIT
metadata:
  title: "Find decision-makers at a company"
  category: "Prospecting"
  outcome: "Find new prospects"
  tools: [get_usage, enrich_company, search_people]
  version: "1.0"
  author: Leadsets
  homepage: https://www.leadsets.ai/skills?utm_source=github&utm_medium=leadsets-skills&utm_campaign=decision-makers-at-company
---

# Find decision-makers at a company

Give it one domain and a sentence about what you sell, and it returns a short, ranked list of the people who would sign, champion or influence the purchase, each with the reason they are on the list. Built for founders, AEs and GTM engineers working a named account who need the right three to ten people, not every employee.

**Category:** Prospecting · **Outcome:** Find new prospects · **Tools:** `get_usage`, `enrich_company`, `search_people`

## Requirements

- The Leadsets MCP server connected to your agent: `https://mcp.leadsets.ai` ([setup](https://www.leadsets.ai/docs/mcp?utm_source=github&utm_medium=leadsets-skills&utm_campaign=decision-makers-at-company)), or a Leadsets API key for the REST API.
- A Leadsets account. The free plan includes 1,000 records, no card ([get a key](https://www.leadsets.ai/signup?utm_source=github&utm_medium=leadsets-skills&utm_campaign=decision-makers-at-company)).

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

- "Who should I talk to at northwind.co about our product?"
- "Find the decision-makers at stackfold.io for a sales tooling deal."
- An inbound lead or target account arrives as a bare domain and you need the buying group before outreach.
- A rep is about to work a named account and wants the economic buyer and likely champion ranked.
- You want contacts at one company pushed to a CSV or a HubSpot company record.

## What you give it

- **Company domain**: One domain, for example parcelry.co. If the user gives a company name instead, ask for the domain rather than guessing.
- **What you sell**: One sentence on the product or the team that buys it, for example "revenue forecasting software bought by RevOps and sales leadership". Used to pick functions and seniority. If missing, ask once.
- **How many** (optional): Number of ranked people to return. Default 10, maximum 25 for a single account.
- **Where it goes** (optional): A table in chat by default. Also CSV, or HubSpot contacts associated to the company through the agent's own HubSpot connection.

## Steps

1. **Confirm the account and the buyer**
   Restate the domain and translate what the user sells into search filters: one or two function values (revenue, marketing, engineering, product, ops, finance, hr), seniority levels (c_level, vp, head, director, manager) and a few likely titles. Ask one question only if the domain or the buying team is ambiguous.
2. **Check limits** · `get_usage`
   Call get_usage. Confirm at least 1 enrichment record and enough search records for the target count plus a 1-record probe. If the free records are nearly gone or a window is full, tell the user what is left and when it resets before spending anything.
3. **Profile the company** · `enrich_company`
   Call enrich_company with the domain. Read company name, industry and headcount band. If it returns 404 not_found, stop and ask the user to check the domain. Use the headcount band to set seniority depth: under 50 people, search c_level and head; 50 to 500, add vp and director; larger, add director and manager in the buying function.
4. **Probe the filters** · `search_people`
   Call search_people with company_domain [domain], the chosen function and seniority, and limit 1. Check that the result is at the right company and that match_reasons include function or title. If it is empty (0 records used), widen seniority by one level or swap function for title before going further.
5. **Pull the buying group** · `search_people`
   Call search_people with the same filters and limit set to about 1.5 times the target count, capped at 100. Use next_cursor only if the first page is short of the target. On 429 window_full or too_many_concurrent, wait for Retry-After and retry once. Do not run a second broad search of the whole company.
6. **Rank the people**
   Assign each person a deal role: economic buyer (owns the budget for what you sell), champion (runs the team that uses it day to day) or influencer (adjacent function or more junior). Rank by deal role, then seniority, then title fit, then email status (verified above catch-all above unknown above none). Write a one-line reason per person from their match_reasons and title. Drop people clearly outside the buying function.
7. **Deliver the list**
   Return the top N as a table in chat, or write it to CSV, or create or update HubSpot contacts associated to the company through the agent's own connection after confirming with the user. Report how many were found, how many were dropped and why, and any deal role with nobody in it.

## Checks before returning

- Every person's company domain matches the input domain; remove anyone returned from a parent, subsidiary or former employer.
- No duplicates by person_id or by name plus title.
- Email status is shown exactly as returned: verified, catch-all or unknown. Nothing is rounded up to verified, and rows with no email are kept but marked.
- If no economic buyer was found, say so plainly instead of promoting a manager to fill the slot.
- Search records used stays within what get_usage reported; if the run would cross the window, stop and report.

## Output

A ranked table with columns: rank, full_name, title, seniority, function, deal_role (economic buyer, champion, influencer), why_ranked (one line), match_reasons, email, email_status, email_checked_at. A header line gives company name, domain, industry and headcount band from enrich_company. Verified emails are ready to send. Catch-all emails stay in the table with status catch-all and a note to send at lower volume. Unknown emails stay with status unknown, marked unconfirmed. Invalid emails are never served, so those people appear with email blank and status "no email". CSV output uses the same columns in a file named decision-makers-<domain>.csv. HubSpot output writes the same fields to contacts associated to the company record.

## Example

> Who are the decision-makers at northwind.co for our revenue forecasting tool? Give me the top 10 and drop them in a CSV.

```
✓ 482 search records left this window  ·  ✓ Northwind Analytics, SaaS, 51-200 people
✓ 1-record probe matched on function and seniority
✓ 16 people found  ·  10 ranked: 2 economic buyers, 4 champions, 4 influencers
✓ 6 verified  ·  2 catch-all  ·  1 unknown  ·  1 no email
→ decision-makers-northwind.co.csv created, top contact Maya Chen, VP Revenue Operations
```

Illustrative output.

## Cost and limits

enrich_company uses 1 enrichment record, counted only if company data comes back. search_people uses 1 search record per person returned, so a 1-record probe plus a 15-record pull costs 16 search records; an empty search costs 0 records and 1 request. get_usage is free. No scrape units are used, so the skill runs on the free plan's 1,000 one-time records and fits easily inside Solo's 500 search records per five hours. On 429 the blocked call counts against nothing; the skill waits for Retry-After. On 402 free_records_exhausted it stops and asks the user to upgrade.

## What it doesn't do

- Does not call enrich_person or verify_email on each contact; for full enrichment and fresh verification, hand the list to the Contacts at target accounts or Best work email for a person skill.
- Does not search beyond the one domain given or invent people for empty deal roles.
- Does not send outreach or write to a CRM without the user confirming the destination first.
