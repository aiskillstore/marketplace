---
name: contacts-at-target-accounts
description: "Turns a list of target accounts into ranked contacts per account using Leadsets search_people, then optionally enriches the kept contacts with enrich_person for current role and a verified work email. Ranks by seniority, title fit and match reasons. Use when someone says \"find contacts at these accounts\", \"who should we reach at these companies\" or \"map people to my account list\"."
license: MIT
metadata:
  title: "Contacts at target accounts"
  category: "Prospecting"
  outcome: "Find new prospects"
  tools: [get_usage, search_people, enrich_person]
  version: "1.0"
  author: Leadsets
  homepage: https://www.leadsets.ai/skills?utm_source=github&utm_medium=leadsets-skills&utm_campaign=contacts-at-target-accounts
---

# Contacts at target accounts

Takes an account list you already have and returns the best few people to contact at each one, ranked with reasons, plus verified work emails if you ask for them. Built for account-based sellers, founders and GTM engineers who know which companies they want and need the right names fast.

**Category:** Prospecting · **Outcome:** Find new prospects · **Tools:** `get_usage`, `search_people`, `enrich_person`

## Requirements

- The Leadsets MCP server connected to your agent: `https://mcp.leadsets.ai` ([setup](https://www.leadsets.ai/docs/mcp?utm_source=github&utm_medium=leadsets-skills&utm_campaign=contacts-at-target-accounts)), or a Leadsets API key for the REST API.
- A Leadsets account. The free plan includes 1,000 records, no card ([get a key](https://www.leadsets.ai/signup?utm_source=github&utm_medium=leadsets-skills&utm_campaign=contacts-at-target-accounts)).

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

- "Find 3 contacts at each of these 80 domains."
- "Who runs RevOps and sales at the accounts in this sheet?"
- "Map people to my Salesforce target accounts and add emails."
- A user has a named-account or ABM list and needs contacts, not new accounts.
- A user pastes or uploads domains and asks for decision-makers per company.

## What you give it

- **Account list**: Company domains (preferred) or names, pasted, from a CSV, a Google Sheet or a CRM account view the agent can read through its own connection. Names without domains are flagged, not guessed.
- **Target personas** (optional): Roles to find, in plain language (for example "RevOps and sales leaders, director and above"). Mapped to title, function and seniority filters. Default: revenue function, seniority vp and head.
- **Contacts per account** (optional): How many ranked contacts to keep per account. Default 3, maximum 10.
- **Enrichment** (optional): Whether to run enrich_person on kept contacts for current role and a verified work email. Default off; turn on when the list is going to outreach.
- **Where it goes** (optional): CSV, Google Sheets or written back to CRM accounts through the agent's own connection. Default CSV.

## Steps

1. **Clean the account list and confirm personas**
   Normalize domains (lowercase, strip protocol, www and paths), remove duplicates and set aside rows with no domain. Restate the persona filters (title, function, seniority) and the per-account count, and ask one question only if the personas are ambiguous.
2. **Check limits and plan the run** · `get_usage`
   Call get_usage. Estimate search records as accounts x (contacts per account + 2), and enrichment records as accounts x contacts per account if enrichment is on. If the estimate exceeds what is left in the five-hour window or the week, tell the user and either split the run into batches across windows or reduce the per-account count. Note the plan's concurrent search limit.
3. **Probe the filters** · `search_people`
   Call search_people with company_domain set to the first domain, the persona filters and limit 1. Check that the result's title and match_reasons fit the persona. If it returns nothing, loosen seniority or titles and probe again before spending on the full list.
4. **Find people at each account** · `search_people`
   Call search_people once per domain with company_domain [domain], the confirmed title, function and seniority filters, and limit set to contacts per account + 2 so there is room to rank. Run no more calls at once than the plan's concurrent searches. Send an Idempotency-Key on each call. On 429 window_full or too_many_concurrent, wait for Retry-After and retry; on weekly_limit, stop and report where to resume. Record domains that return no results.
5. **Rank and trim per account**
   Within each account, rank by seniority (c_level, vp, head, director, manager, ic), then closeness of title to the persona, then number of match_reasons. Keep the top N per account. Remove any person_id that appears under more than one account and keep it on the account matching its company domain.
6. **Enrich kept contacts (optional)** · `enrich_person`
   Only if enrichment is on, call enrich_person for each kept contact. Take current role, company and work email with its status and confidence; these emails are already verified, so do not call verify_email again. If the current company no longer matches the account, flag the contact as moved. On 404 not_found, mark no email and move on. Read the usage object as you go and pause if the enrichment window runs low.
7. **Deliver and report**
   Write the ranked table to the chosen destination through the agent's own connection, with catch-all and unknown emails on a separate tab and accounts with no matches listed. Finish with a short summary: accounts processed, contacts kept, email statuses and records used.

## Checks before returning

- Every account in the input appears in the output, either with contacts or on the no-match list with the reason (no domain, empty search).
- No person appears twice, and no account has more than the requested contacts per account.
- Verified, catch-all and unknown emails are kept in separate segments; catch-all and unknown are never presented as verified, and contacts with no email are labelled no email.
- Contacts whose enriched company differs from the account domain are flagged as moved, not silently kept.
- get_usage after the run matches the plan; any batches left for a later window are listed with where to resume.

## Output

Tab or file "Contacts": account_domain, account_name, rank, full_name, title, seniority, match_reasons, and when enrichment is on: current_company, work_email, email_status (verified), confidence, checked_at, moved_flag. Tab "Catch-all and unknown": same columns for contacts whose email is catch-all (send at lower volume) or unknown (unconfirmed, do not send without review). Tab "No match": account_domain and reason (no domain given, no people matched filters, contacts found but no email). Invalid emails are never served, so those contacts show no email. With enrichment off, the email columns are omitted.

## Example

> Here's my sheet of 60 target accounts. Find the top 3 RevOps or sales leaders at each, director and up, with verified emails. Add a tab to the same sheet.

```
✓ 60 accounts, 2 without domain set aside  ·  ✓ 412 search and 1,380 enrichment records left this window
✓ 58 accounts searched  ·  51 with matches  ·  7 no match
✓ 149 contacts kept  ·  ✓ 141 enriched  ·  118 verified  ·  15 catch-all  ·  8 no email
→ Tabs "Contacts", "Catch-all and unknown", "No match" added to "Target accounts Q1"
```

Illustrative output.

## Cost and limits

search_people uses 1 search record per person returned and 1 request per call; an empty search uses no records but still counts as a request. enrich_person uses 1 enrichment record per record returned, and its emails are already verified at no extra cost. No scrape units are used. get_usage is free. On Solo, 500 search records per five hours covers roughly 100 accounts at 3 contacts plus ranking headroom, so larger lists are split across windows; Free accounts share 1,000 one-time records across search and enrichment, and a 402 free_records_exhausted means stop and ask the user to upgrade. Concurrency stays within the plan's limit (3 Solo, 5 Pro, 8 Team and Max), and blocked 429 calls count against nothing.

## Edge cases

- **The same person appears under several accounts:** keep them once, under the account that matches their current company from `enrich_person`, and drop the other rows. Count it in the summary as a duplicate removed.
- **Report records exactly:** add up `usage.records_counted` from each response rather than estimating.

## What it doesn't do

- Find new accounts; it only works from the account list you give it (use a prospect list or lookalike skill for that).
- Guess emails or domains, or call verify_email on emails enrich_person already verified.
- Send outreach or create CRM records on its own; it writes only to the destination you choose through the agent's connection.
