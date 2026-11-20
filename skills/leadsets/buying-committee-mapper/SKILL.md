---
name: buying-committee-mapper
description: "Maps the buying committee on an open deal: compares the contacts already on the deal with the roles that usually sign off, finds the missing stakeholders at the account with search_people, enriches them with enrich_person, and adds them to the account in the CRM. Use when someone says \"who else should be on this deal\", \"map the buying committee\", \"we're single-threaded\" or \"find the other stakeholders at this account\"."
license: MIT
metadata:
  title: "Buying committee mapper"
  category: "Prospecting"
  outcome: "Find new prospects"
  tools: [get_usage, search_people, enrich_person]
  version: "1.0"
  author: Leadsets
  homepage: https://www.leadsets.ai/skills?utm_source=github&utm_medium=leadsets-skills&utm_campaign=buying-committee-mapper
---

# Buying committee mapper

Takes one open deal, works out which stakeholders are missing from it, and returns those people with current roles and verified work emails, ready to add to the account. Built for AEs, founders and RevOps teams who are single-threaded on a deal and need the economic buyer, the champion's boss or the technical evaluator before the deal stalls.

**Category:** Prospecting · **Outcome:** Find new prospects · **Tools:** `get_usage`, `search_people`, `enrich_person`

## Requirements

- The Leadsets MCP server connected to your agent: `https://mcp.leadsets.ai` ([setup](https://www.leadsets.ai/docs/mcp?utm_source=github&utm_medium=leadsets-skills&utm_campaign=buying-committee-mapper)), or a Leadsets API key for the REST API.
- A Leadsets account. The free plan includes 1,000 records, no card ([get a key](https://www.leadsets.ai/signup?utm_source=github&utm_medium=leadsets-skills&utm_campaign=buying-committee-mapper)).

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

- "Who else should we be talking to on the Northwind Analytics deal?"
- "We're single-threaded on this opportunity. Map the buying committee."
- "Find the finance and IT stakeholders at stackfold.io and add them to the account in HubSpot."
- A deal moves to a late stage with only one or two contacts attached
- Before a pricing or security review where approvers outside the current thread will weigh in

## What you give it

- **Deal or account**: The open deal name or the company domain (for example northwind.co). If given a deal name, read the account domain and attached contacts from the CRM through the agent's own connection.
- **Existing contacts** (optional): People already on the deal, with titles. Read from the CRM by default; the user can also paste them. Used to avoid duplicates and to infer which roles are covered.
- **Committee roles** (optional): The roles that usually take part in buying what you sell, as functions and seniority (for example economic buyer: finance or revenue, vp or c_level; technical evaluator: engineering or ops, director or head). Default: economic buyer, champion's manager, technical evaluator, end-user lead and procurement or finance approver, inferred from the deal and confirmed with the user.
- **Max people to add** (optional): Cap on new stakeholders per account. Default 6, so the committee stays focused and the run stays small.
- **Where it goes** (optional): Add to the account in HubSpot, Salesforce, Pipedrive or Attio through the agent's own CRM connection, or return a CSV or Google Sheet for review. Default: return a review table first and write to the CRM only after the user approves.

## Steps

1. **Confirm the deal and the committee**
   Resolve the account domain and list the contacts already on the deal with their titles. Map each existing contact to a committee role, list the uncovered roles, and show the plan to the user. Ask one question only if the product, the account domain or the roles to look for are ambiguous.
2. **Check remaining limits** · `get_usage`
   Call get_usage (costs nothing). Expect up to about 25 search records per role and one enrichment record per stakeholder you keep. If the search or enrichment window cannot cover the run, say so and reduce roles or the per-role limit before spending anything. On the free plan, note how many of the 1,000 one-time records remain.
3. **Probe the account** · `search_people`
   Call search_people with company_domain set to the account domain and limit 1. If it returns nothing, the domain may be wrong or not covered: confirm the domain with the user instead of widening filters blindly. An empty result uses no records.
4. **Search each missing role** · `search_people`
   For each uncovered role, call search_people with company_domain, the role's function and seniority enums (c_level, vp, head, director, manager, ic) and optional title strings, limit 10 to 25. Respect the plan's concurrent search limit (3 on Solo, 5 on Pro); on 429 too_many_concurrent or window_full, wait for Retry-After and retry with the same Idempotency-Key (REST API). Keep match_reasons for every result.
5. **Pick and rank stakeholders**
   Drop anyone already on the deal (match by name and email). For each role keep the one or two best fits by seniority, function and match_reasons, up to the max people to add. Prefer people who sit in the same function as or above the current champion. Flag gaps where no one matched.
6. **Enrich the shortlist** · `enrich_person`
   Call enrich_person on each kept person to confirm current role and company and get a work email. Emails from enrich_person are already verified, so do not call verify_email again. If a person's current company is no longer the account, drop them and note it. A 404 not_found means nothing to enrich: move on without retrying.
7. **Review and add to the account**
   Show the review table. After the user approves, create or update each contact through the agent's own CRM connection, associate it with the account and the deal, and record the committee role. Write only verified emails into the email field; put catch-all and unknown addresses in a note, not the primary email. Otherwise export CSV or a Google Sheet.

## Checks before returning

- Every new stakeholder is confirmed by enrich_person as currently at the account domain; anyone who moved is dropped and listed separately.
- No duplicates: nobody already on the deal or account is added again, matched on name and email.
- Email statuses are reported as returned: verified, catch-all and unknown are labelled separately and nothing uncertain is presented as verified; invalid addresses are never written.
- Uncovered roles with zero matches are reported as gaps, not filled with weak matches from the wrong function.
- Usage after the run is within the window shown by get_usage, and any 429 was retried after Retry-After rather than skipped silently.

## Output

A review table, one row per new stakeholder: committee_role, full_name, title, seniority, function, company_domain, work_email, email_status (verified, catch-all or unknown), match_reasons, checked_at, action (add or skip). Below it: the roles already covered and by whom, roles with no match, and people dropped because they changed company. On approval, contacts are added to the CRM account and associated with the deal; only verified emails go in the primary email field, catch-all and unknown go in a note marked unconfirmed, people with no email are added without one and flagged. CSV or Sheet export uses the same columns, with a second tab named "Gaps".

## Example

> We're single-threaded with Maya Chen, VP Revenue Operations, on the Northwind Analytics deal (northwind.co). Find who else should be in the buying committee and add them to the account in HubSpot.

```
✓ Deal found · 1 contact on it (champion) · 4 roles missing  ·  ✓ 412 search records left this window
✓ 31 people found at northwind.co across 4 roles  ·  ✓ 5 shortlisted and enriched
✓ 3 verified  ·  1 catch-all (noted, not primary)  ·  1 moved company (dropped)  ·  procurement: no match
→ 4 contacts added to Northwind Analytics in HubSpot and linked to the deal
```

Illustrative output.

## Cost and limits

search_people uses 1 search record per person returned and enrich_person 1 enrichment record per person returned; empty results and errors use no records, but every call counts as one request. Emails from enrich_person are already verified, so there is no second verification charge. The skill calls get_usage first for free, probes with a limit 1 search, keeps per-role limits at 25 or fewer, and enriches only the shortlist, so a typical account uses well under 100 search records and under 10 enrichment records. It works on the free plan's 1,000 one-time records; if they run out the API returns 402 free_records_exhausted and the skill stops and asks the user to upgrade. It stays within the plan's concurrent search limit and waits out 429s using Retry-After. No scraping, so no scrape units.

## What it doesn't do

- Does not write to the CRM before the user approves the review table, and never overwrites existing contacts or deal fields.
- Does not send outreach or enroll anyone in a sequence; Leadsets is not a sending tool, so handing off is a separate step.
- Does not return phone numbers, which Leadsets does not offer, or search beyond the account's own domain.
