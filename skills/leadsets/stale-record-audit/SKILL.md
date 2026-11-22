---
name: stale-record-audit
description: "Re-checks CRM or CSV contacts with enrich_person and flags everyone whose title or company no longer matches the record, so reps stop sequencing people who moved on. Reports changes with checked dates and leaves write-back for your approval. Use when someone asks to audit stale contacts, find job changes before a sequence, check whether titles are still current, or clean up outdated CRM records."
license: MIT
metadata:
  title: "Stale record audit"
  category: "CRM hygiene"
  outcome: "Keep your CRM clean"
  tools: [get_usage, enrich_person]
  version: "1.0"
  author: Leadsets
  homepage: https://www.leadsets.ai/skills?utm_source=github&utm_medium=leadsets-skills&utm_campaign=stale-record-audit
---

# Stale record audit

Takes a contact list from your CRM or a file, re-checks each person's current role and company, and returns a flagged list: still current, title changed, company changed, or could not confirm. Built for RevOps and sales teams who want to catch outdated records before a rep spends a sequence on someone who left.

**Category:** CRM hygiene · **Outcome:** Keep your CRM clean · **Tools:** `get_usage`, `enrich_person`

## Requirements

- The Leadsets MCP server connected to your agent: `https://mcp.leadsets.ai` ([setup](https://www.leadsets.ai/docs/mcp?utm_source=github&utm_medium=leadsets-skills&utm_campaign=stale-record-audit)), or a Leadsets API key for the REST API.
- A Leadsets account. The free plan includes 1,000 records, no card ([get a key](https://www.leadsets.ai/signup?utm_source=github&utm_medium=leadsets-skills&utm_campaign=stale-record-audit)).

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

- "Audit the contacts in this sequence before it launches and flag anyone who changed jobs."
- "Which of our HubSpot contacts have out-of-date titles or companies?"
- "Check this CSV of 500 contacts and tell me who is still at the same company."
- Before loading an older list into Instantly, Smartlead or LinkedCamp
- Quarterly CRM hygiene on Salesforce, Pipedrive or Attio contacts that have not been touched in months

## What you give it

- **Contact source**: HubSpot, Salesforce, Pipedrive, Attio, Google Sheets or a CSV. The agent reads it through its own connection. Each row needs a name plus company or domain; a work email or LinkedIn URL improves matching.
- **Scope** (optional): Which contacts to audit, for example a list, a sequence, an owner or records not updated in a set period. Default: contacts enrolled in or queued for active sequences, capped at 250.
- **What to do with flags** (optional): Report only, or write flags back to the source as a field, note or task. Default: report only. Write-back happens only after the user approves the change set.

## Steps

1. **Pull and dedupe the contacts**
   Read the scoped contacts from the source through the agent's own connection. Keep record ID, full name, current title, company name, company domain, work email and LinkedIn URL if present. Drop exact duplicates by record ID and by email, and set aside rows with no name or no company as 'not auditable'. Tell the user the count before spending anything.
2. **Check limits and plan batches** · `get_usage`
   Call get_usage (it costs nothing). Compare the auditable count against enrichment records left in the five-hour window and the week. On the free plan, remember the 1,000 records are one time and shared with search. If the run would cross a window, propose a batch size that fits now and say when the rest can run after resets_at. Do not start until the user accepts the plan if it needs more than one window.
3. **Probe with one contact** · `enrich_person`
   Call enrich_person on a single contact. Confirm the response maps cleanly: current_role, company name and domain, work_email with status, and checked_at dates. If the match looks wrong (different person, mismatched company), fix the input mapping, for example by sending the LinkedIn URL or domain, before continuing.
4. **Enrich the rest in batches** · `enrich_person`
   Call enrich_person for each remaining contact in the planned batch size, with an Idempotency-Key per contact so retries never count twice. Read the usage object on each response and stop before the window is exhausted. On 429 window_full or too_many_concurrent, wait the Retry-After seconds and retry with the same key. On 429 weekly_limit, stop and report where to resume. On 404 not_found, mark the contact 'could not confirm' and move on. On 402 free_records_exhausted, stop and ask the user to upgrade.
5. **Compare and classify**
   For each contact, compare the CRM company domain with the returned company domain, and the CRM title with current_role. Treat equivalent titles as unchanged (for example 'VP Sales' and 'Vice President, Sales'). Classify as: current, title changed, company changed (includes title), or could not confirm. Record the returned value and its checked_at date next to the old value so a human can see the evidence.
6. **Return the audit and handle write-back**
   Return the flagged table and a summary. Recommend pulling company-changed contacts out of sequences and reviewing title changes for fit. If the user chose write-back, show the exact change set first, then write flags as a field, note or task on each record through the agent's own CRM connection. Never overwrite the original title, company or email without explicit approval.

## Checks before returning

- Every flagged row shows the old value, the new value and a checked_at date; no flag without evidence.
- Title differences that are only wording (abbreviations, punctuation, word order) are not counted as changes.
- Contacts that returned no data are listed as 'could not confirm', never as current.
- Records used in the run match get_usage before and after, and no batch crossed the five-hour or weekly limit.
- No duplicate record IDs in the output, and the counts per category add up to the number of contacts audited.

## Output

A table (CSV, Google Sheet or CRM report) with one row per contact: record_id, full_name, crm_title, current_title, crm_company, current_company, current_domain, status (current, title_changed, company_changed, could_not_confirm), checked_at, new_work_email, email_status. For company changes, new_work_email is filled only when enrich_person returns one: verified addresses are listed as is, catch-all addresses are kept with email_status catch-all and a note to send at lower volume, and unknown addresses are marked unconfirmed and never written back as the contact email. Invalid emails are never served, so that cell stays blank. In Google Sheets, use tabs 'Changed', 'Current' and 'Could not confirm'. A short summary lists counts per status and any contacts not auditable.

## Example

> Audit the 180 contacts in our 'Q4 Expansion' HubSpot sequence. Flag anyone who changed title or company and don't change anything in HubSpot yet.

```
✓ 180 contacts pulled · 4 duplicates removed · ✓ 1,000 enrichment records left this window
✓ 176 enriched · 164 returned data · 12 could not confirm
✓ 131 current · 19 title changed · 14 company changed (9 with a new verified email, 2 catch-all)
→ Sheet "Q4 Expansion stale audit" created, 3 tabs · no HubSpot records changed
```

Illustrative output.

## Cost and limits

Each contact that comes back with data uses 1 enrichment record; contacts with no match use 0 records but still count as 1 request. get_usage is free. Emails returned by enrich_person are already verified, so there is no second charge. On Solo that means up to 1,000 contacts per five hours and 5,000 per week; Pro allows 15,000 per five hours. On the free plan the 1,000 records are one time and shared with search. The skill checks get_usage first, sizes batches to fit the current window, reads the usage object on every response, uses Idempotency-Keys so retries never double-count, and splits larger audits across windows instead of running into a 429.

## What it doesn't do

- Does not edit, pause or remove anyone from sequences, or overwrite CRM fields without the user's explicit approval.
- Does not find a replacement contact at the old company; use Contacts at target accounts or Find decision-makers at a company for that.
- Does not re-verify the old email already in the CRM; run Clean a list before sending if you need that check.
