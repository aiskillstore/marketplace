---
name: hubspot-email-backfill
description: "Finds HubSpot contacts with a missing or bounced email, runs enrich_person to get a current verified work email, re-checks reused addresses with verify_email, and writes only verified addresses back with a change log. Use when someone asks to backfill missing emails in HubSpot, fix bounced contacts, fill blank email fields, or repair CRM contacts before a sequence."
license: MIT
metadata:
  title: "HubSpot email backfill"
  category: "CRM hygiene"
  outcome: "Keep your CRM clean"
  tools: [get_usage, enrich_person, verify_email]
  version: "1.0"
  author: Leadsets
  homepage: https://www.leadsets.ai/skills?utm_source=github&utm_medium=leadsets-skills&utm_campaign=hubspot-email-backfill
---

# HubSpot email backfill

Fills blank and bounced email fields on HubSpot contacts with verified work emails from Leadsets and logs every change. Catch-alls and unknowns go to a review list. Built for RevOps and founders whose sequences keep skipping or bouncing on the same broken records.

**Category:** CRM hygiene · **Outcome:** Keep your CRM clean · **Tools:** `get_usage`, `enrich_person`, `verify_email`

## Requirements

- The Leadsets MCP server connected to your agent: `https://mcp.leadsets.ai` ([setup](https://www.leadsets.ai/docs/mcp?utm_source=github&utm_medium=leadsets-skills&utm_campaign=hubspot-email-backfill)), or a Leadsets API key for the REST API.
- A Leadsets account. The free plan includes 1,000 records, no card ([get a key](https://www.leadsets.ai/signup?utm_source=github&utm_medium=leadsets-skills&utm_campaign=hubspot-email-backfill)).

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

- "Backfill missing emails on our HubSpot contacts."
- "Find new emails for everyone who hard bounced last month."
- A HubSpot list or view has contacts with an empty email field that reps cannot sequence.
- Bounce rates went up and the user wants bounced contacts replaced with current, verified addresses.
- Before a campaign, when the target HubSpot list has gaps in its email column.

## What you give it

- **Which contacts**: A HubSpot list, view or filter. Default: contacts with an empty email field plus contacts marked as hard bounced, read through the agent's own HubSpot connection.
- **How many** (optional): Maximum contacts to process in this run. Default 200. Larger jobs are split into batches that fit the current enrichment window.
- **Write-back mode** (optional): Preview first, then write. Default: show a preview of the first 10 changes and ask for approval before writing; only verified emails go into the primary email field.
- **Catch-all handling** (optional): Default: do not write catch-all addresses to the email field; put them on a review list (or a separate HubSpot property if the user names one) so they can be sent at lower volume.

## Steps

1. **Check limits and size the run** · `get_usage`
   Call get_usage (it costs nothing). Read enrichment records left in the five-hour window and the week, or free records left on the free plan. Plan roughly one enrichment record per contact plus one per standalone verify_email. If the job is larger than what is left, tell the user how many contacts fit now and split the rest into later batches.
2. **Pull the contacts from HubSpot**
   Through the agent's own HubSpot connection, read the target contacts: record ID, first and last name, company name, company domain, LinkedIn URL if present, current email and bounce status. Drop contacts with no name or no company or domain, since they cannot be matched, and count them for the report. Remove duplicate record IDs.
3. **Probe with one contact** · `enrich_person`
   Call enrich_person on a single contact with the best identifiers the record has (LinkedIn URL if present, otherwise name plus company domain). Confirm the response shape: current role, company, work email with status, confidence and checked_at. If the person has clearly changed company, note it; the skill writes the email only when the returned company matches the HubSpot company or the user approves updating it.
4. **Enrich the rest in batches** · `enrich_person`
   Call enrich_person for each remaining contact, with an Idempotency-Key per contact over the REST API so retries never double-count. Read the usage object on each response and pause before the window runs out. On 404 not_found, mark the contact 'no match' and move on. On 429 window_full, wait for Retry-After and retry with the same key. On 402 free_records_exhausted, stop and tell the user to upgrade. Emails from enrich_person are already verified; do not re-verify them.
5. **Re-check reused bounced addresses** · `verify_email`
   If enrich_person returns the same address that previously bounced, call verify_email on it to get a current label instead of trusting either the old bounce or the match. Only do this for those cases, since standalone verification counts toward enrichment. Keep the status and confidence for the log.
6. **Sort results by label**
   Group every contact: verified (write back), catch-all (review list), unknown (do not write, treat as unconfirmed), invalid or no email (leave the field, flag), no match, company changed. Never round catch-all or unknown up to verified.
7. **Preview, then write back**
   Show the user a preview of the first 10 changes: record ID, old email, new email, status, confidence, checked_at. After approval, write verified emails to the primary email field through the agent's HubSpot connection. Preserve the old bounced address in a note or the property the user names, and never overwrite an existing email that was not empty or bounced.
8. **Report what changed and what did not**
   Return the change log and the summary counts, list catch-alls and unknowns for review, and say how many contacts were skipped for lack of identifiers or limits, with when the window resets if a batch is pending.

## Checks before returning

- Every email written to HubSpot has status verified; catch-all, unknown and invalid are never written to the primary email field.
- No contact was processed twice: record IDs are deduplicated and each paid call used an Idempotency-Key.
- Existing non-bounced emails were left untouched, and every overwrite of a bounced address has the old value preserved in the log.
- Remaining enrichment records from the last usage object cover any pending batch; if not, the report states how many contacts are left and when the window resets.
- Contacts whose enriched company differs from HubSpot are flagged as possible job changes, not silently updated.

## Output

A change log table (CSV or a Google Sheet tab named 'Email backfill – log') with columns: hubspot_record_id, full_name, company, old_email, old_status (empty or bounced), new_email, email_status, confidence, checked_at, action (written, review, skipped), reason. Verified emails are written to HubSpot. Catch-all addresses go to a 'Review – catch-all' tab with a note to send at lower volume. Unknown addresses go to 'Review – unknown' as unconfirmed and are not written. Invalid results and no-match contacts are listed in 'Not found' with the field left as it was.

## Example

> We have about 300 contacts in HubSpot with no email or a hard bounce in the 'Q4 target accounts' list. Find current emails and write the good ones back.

```
✓ 312 contacts pulled  ·  ✓ 4,860 enrichment records left this window
✓ 271 matched  ·  41 no match or missing company
✓ 214 verified and written to HubSpot  ·  33 catch-all  ·  15 unknown  ·  9 no email
✓ 18 flagged as possible job changes, not updated
→ Log sheet 'Email backfill – Nov' created, 4 tabs
```

Illustrative output.

## Cost and limits

enrich_person uses 1 enrichment record per contact that returns data; a 404 not_found uses no records but counts as a request. Emails from enrich_person are already verified at no extra cost. Standalone verify_email, used only for reused bounced addresses, counts toward the enrichment limit. No search records or scrape units are used. The skill calls get_usage first, reads the usage object on every response, and splits jobs that would cross a window (for example Solo's 1,000 enrichments per five hours and 5,000 per week). On 429 it waits for Retry-After; on 402 free_records_exhausted it stops and asks the user to upgrade. The free plan's 1,000 one-time records are enough for a trial run.

## What it doesn't do

- Write catch-all, unknown or invalid addresses into the primary email field, or overwrite emails that are not empty or bounced.
- Change titles, companies or other HubSpot fields; job changes are flagged for a human or the job-change detector skill.
- Send email or enrol contacts in sequences; Leadsets supplies the data and HubSpot is updated through the agent's own connection.
