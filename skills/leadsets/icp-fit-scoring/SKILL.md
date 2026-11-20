---
name: icp-fit-scoring
description: "Scores an account or contact list against a stated ICP using enrich_company firmographics and enrich_person roles, then explains every score with the fields behind it and sorts rows into fit tiers. Use when someone says \"score this list against our ICP\", \"which of these accounts fit\", \"rank these leads by fit\" or \"prioritize this CSV before outreach\"."
license: MIT
metadata:
  title: "ICP fit scoring"
  category: "List building"
  outcome: "Research accounts and timing"
  tools: [get_usage, enrich_company, enrich_person]
  version: "1.0"
  author: Leadsets
  homepage: https://www.leadsets.ai/skills?utm_source=github&utm_medium=leadsets-skills&utm_campaign=icp-fit-scoring
---

# ICP fit scoring

Takes a list you already have, accounts or contacts, and returns each row with a 0 to 100 ICP fit score, a tier and a plain-language reason built from sourced, dated Leadsets fields. Built for founders, RevOps and agencies who need to decide which rows deserve outreach before anyone writes a message.

**Category:** List building · **Outcome:** Research accounts and timing · **Tools:** `get_usage`, `enrich_company`, `enrich_person`

## Requirements

- The Leadsets MCP server connected to your agent: `https://mcp.leadsets.ai` ([setup](https://www.leadsets.ai/docs/mcp?utm_source=github&utm_medium=leadsets-skills&utm_campaign=icp-fit-scoring)), or a Leadsets API key for the REST API.
- A Leadsets account. The free plan includes 1,000 records, no card ([get a key](https://www.leadsets.ai/signup?utm_source=github&utm_medium=leadsets-skills&utm_campaign=icp-fit-scoring)).

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

- "Score this list of 400 domains against our ICP and tell me which ones to work first."
- "Rank these webinar sign-ups by fit, with a reason for each."
- Before loading an account or contact list into a CRM or sequencer, to cut rows that do not fit.
- When an inherited or purchased list needs to be sorted into tiers with explanations a rep can trust.
- "Why is this account a good fit?" asked across a whole sheet rather than one company.

## What you give it

- **List**: A CSV, Google Sheet or CRM view of accounts (domain or company name) or contacts (name plus company or domain, optionally LinkedIn URL or email). The agent reads it through its own connection to that system.
- **ICP**: Industry, headcount band, region, technology and, for contact lists, target functions and seniority. Plain language is fine. If you have no written ICP, the agent drafts one from your description and asks you to confirm it.
- **Weights** (optional): How much each criterion matters. Default for accounts: industry 30, headcount 25, region 20, technology 25. Default for contacts: account fit 60, role and seniority 40.
- **Tier cutoffs** (optional): Score bands for tiers. Default: A 80 and above, B 60 to 79, C 40 to 59, No fit below 40.
- **Where it goes** (optional): Write scores back to the same sheet or CRM records, or export a new CSV or Google Sheet. Default: a new Google Sheet with one tab per tier.

## Steps

1. **Confirm the ICP and rubric**
   Restate the ICP as explicit criteria with weights and tier cutoffs. Ask one question only if a criterion is ambiguous (for example "mid-market" with no headcount band). Read the list, detect whether it is an account or contact list, normalize domains, and dedupe rows by domain for accounts and by person plus domain for contacts. Note how many unique companies and people need enriching.
2. **Check limits and plan the run** · `get_usage`
   Call get_usage (free). Compare remaining enrichment records in the five-hour window and the week against unique companies plus people. On Free, remember the 1,000 records are shared and one time. If the run would cross a window, split it into batches that fit and tell the user how many batches and when the next window resets before spending anything.
3. **Probe with one company** · `enrich_company`
   Call enrich_company on a single domain from the list. Check that the response returns the fields the rubric needs (industry, headcount band, location, technology) with source and checked dates. If a criterion has no matching field, tell the user it will be scored as unknown rather than guessed, then continue.
4. **Enrich every unique account** · `enrich_company`
   Call enrich_company once per unique domain, never per row, so contacts at the same company share one company record. Send an Idempotency-Key with each call when using REST. On 404 not_found, mark the account "no data" and move on. On 429 window_full, wait the Retry-After seconds and resume. On 402 free_records_exhausted, stop and report what was scored.
5. **Enrich contacts for role fit** · `enrich_person`
   Contact lists only. Call enrich_person for each unique person to get current role and company. If the current company differs from the list, flag the row as "moved" and score against the new company (enrich that domain if not already done). Keep the work email and its status as returned; do not call verify_email, since enrich_person emails are already verified.
6. **Score and explain each row**
   Apply the rubric field by field. Award points only for criteria backed by a returned field; score missing fields as unknown with zero points and say so. Write a one-line reason naming the matched and missed criteria (for example "SaaS, 51-200, US, uses HubSpot; role is Director not VP"). Assign the tier from the cutoffs.
7. **Return the scored list**
   Write results back or export through the agent's own connection to the destination. Sort by score descending, split tabs by tier, and report counts per tier, rows with no data, moved contacts and records used.

## Checks before returning

- Every score has a reason that cites only fields Leadsets returned, and criteria with no data are labelled unknown, never inferred.
- Companies were enriched once per unique domain and duplicate rows were merged before spending records.
- Usage after the run matches the plan from get_usage, and any batch blocked by a 429 was resumed or reported as pending.
- Rows that returned 404 or no data appear in a separate "No data" group rather than silently scored as No fit.
- For contact lists, email status is carried through as returned: catch-all and unknown are flagged, invalid addresses are never shown as contact emails.

## Output

One row per input row with: input name or domain, company, domain, industry, headcount band, location, technology matched, (contacts only) current title, seniority, moved flag, work email, email status, then fit_score (0 to 100), tier (A, B, C, No fit, No data), fit_reason, and checked_at for the fields used. Default destination is a Google Sheet named "ICP fit – <list name>" with tabs A, B, C, No fit and No data, or the same columns written back to the source. Email handling: verified emails shown as is; catch-all kept with status "catch-all" and a note to send at lower volume; unknown kept with status "unknown, unconfirmed"; invalid never served, so the email cell stays blank. Email status does not change the fit score.

## Example

> Score this sheet of 250 accounts against our ICP: US or Canada B2B SaaS, 50 to 500 people, using HubSpot. Also rank the 180 contacts in the second tab, we want VP or Head of Revenue Operations or Sales.

```
✓ ICP confirmed  ·  ✓ 2,140 enrichment records left this window
✓ 231 unique domains enriched  ·  19 no data  ·  ✓ 172 contacts enriched, 11 moved
✓ Accounts: 48 A  ·  77 B  ·  61 C  ·  45 no fit
✓ Contacts: 39 A  ·  52 B  ·  81 below B  ·  8 no data
→ Sheet "ICP fit – Q1 accounts" created, 5 tabs per list
```

Illustrative output.

## Cost and limits

Uses enrichment only: enrich_company and enrich_person each use 1 enrichment record per record returned, and every call counts as one request. Empty results and 404s use no records. get_usage is free. No search records and no scrape units are spent. The skill dedupes by domain so each company costs at most one record, checks get_usage first, and splits large lists across five-hour windows (for example 1,000 enrichments per window on Solo, 15,000 on Pro). On Free, the 1,000 one-time records are shared with search, so it reports the cost before running and stops on 402.

## What it doesn't do

- Does not search for new accounts or people; it scores only the list you give it.
- Does not scrape websites or careers pages, so hiring and positioning signals are out of scope here.
- Does not guess firmographics or roles that Leadsets did not return, and does not send or sequence anyone.
