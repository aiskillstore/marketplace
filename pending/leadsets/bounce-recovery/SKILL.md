---
name: bounce-recovery
description: "Takes a list of bounced contacts, re-checks the original addresses, finds who changed role or company with enrich_person, and returns a current, verified work email for the ones who moved, with catch-all and unresolved contacts kept separate. Use when someone says \"recover my bounces\", \"find new emails for bounced contacts\", \"who moved after this campaign bounced\" or \"fix hard bounces\"."
license: MIT
metadata:
  title: "Bounce recovery"
  category: "Email verification"
  outcome: "Get verified contact data"
  tools: [get_usage, verify_email, enrich_person]
  version: "1.0"
  author: Leadsets
  homepage: https://www.leadsets.ai/skills?utm_source=github&utm_medium=leadsets-skills&utm_campaign=bounce-recovery
---

# Bounce recovery

Turns a pile of bounced contacts into three clear groups: people with a new verified email, people worth a lower-volume retry, and people it could not confirm. Built for founders, SDR leads and GTM engineers who want to win back contacts lost to job changes instead of deleting them.

**Category:** Email verification · **Outcome:** Get verified contact data · **Tools:** `get_usage`, `verify_email`, `enrich_person`

## Requirements

- The Leadsets MCP server connected to your agent: `https://mcp.leadsets.ai` ([setup](https://www.leadsets.ai/docs/mcp?utm_source=github&utm_medium=leadsets-skills&utm_campaign=bounce-recovery)), or a Leadsets API key for the REST API.
- A Leadsets account. The free plan includes 1,000 records, no card ([get a key](https://www.leadsets.ai/signup?utm_source=github&utm_medium=leadsets-skills&utm_campaign=bounce-recovery)).

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

- A campaign came back with hard bounces and the user wants current emails for those contacts
- "These 200 contacts bounced, find out who moved and where they went"
- A sequencer or CRM export of bounced or invalid addresses needs a recovery pass before the next send
- "Recover my bounces from last week's Instantly campaign"
- Cleaning up after a list aged badly and many emails now bounce

## What you give it

- **Bounced contacts**: CSV, Google Sheet, CRM view or sequencer export. Needs full name and the bounced email at minimum; company name, domain, title and LinkedIn URL improve matching. The agent reads it through its own connection to that system.
- **Recheck original addresses** (optional): Whether to run verify_email on the bounced addresses first to catch soft or temporary bounces. Default yes. Each check counts toward the enrichment limit.
- **Where it goes** (optional): CSV, Google Sheets, or written back to the CRM or sequencer the list came from. Default: a CSV or Sheet with separate tabs, nothing written back without the user's confirmation.
- **Max contacts this run** (optional): Cap on how many contacts to process. Default: all, split across windows if the enrichment limit would be crossed.

## Steps

1. **Load and dedupe the bounced list**
   Read the list through the agent's own connection to the source. Normalise emails to lowercase, drop exact duplicates by email and by name plus company, and drop rows with no name. Count what is left and tell the user the number before spending anything.
2. **Check remaining limits and plan the run** · `get_usage`
   Call get_usage (it costs nothing). Estimate the spend: one enrichment record per verify_email check plus up to one per enrich_person call that returns data. If the estimate exceeds what is left in the five-hour enrichment window or the week, tell the user and split the run into batches that fit, resuming after resets_at. On the free plan, remember the 1,000 records are shared with search and do not refill.
3. **Recheck the original addresses** · `verify_email`
   If recheck is on, call verify_email on the bounced addresses in batches. Read the usage object after each batch. Any address that now comes back verified is likely a soft or temporary bounce: move it to a 'Still deliverable' group and skip enrichment for it. Keep invalid, unknown and catch-all results in the recovery queue.
4. **Probe enrichment on one contact** · `enrich_person`
   Call enrich_person for a single contact from the queue, passing the strongest identifier available (LinkedIn URL, or name plus company or domain). Confirm the response returns current role, company and an email status before running the rest. If the input shape is rejected (400 invalid_request), fix the fields instead of retrying.
5. **Enrich the recovery queue** · `enrich_person`
   Call enrich_person for each remaining contact. Compare the returned current company and role with the original row: a different company means the person moved; same company with a different email means the address changed. Use the email status that comes back; emails from enrich_person are already verified, so do not call verify_email on them again. On 404 not_found, mark the contact unresolved and move on. On 429 window_full or weekly_limit, wait for Retry-After or resets_at and resume. On 402 free_records_exhausted, stop and ask the user to upgrade.
6. **Segment and export**
   Split results into Recovered (new verified email), Catch-all (new address on a catch-all domain), Still deliverable (original address now verifies), and Unresolved (unknown, no email found, not found, or same company with the same bounced address). Write them to the chosen destination through the agent's own connection. Ask before overwriting any field in a CRM or sequencer.
7. **Report the run**
   Summarise counts per group, how many contacts moved company, records used, and anything that needs a decision, such as unresolved contacts the user may want to drop or suppress.

## Checks before returning

- Every recovered email carries status verified from the response; catch-all and unknown addresses are never placed in the Recovered group, and invalid addresses never appear as a contact email.
- No new email equals the original bounced address unless the recheck labelled it verified; if enrichment returns the same bounced address, the contact goes to Unresolved.
- Duplicates are removed before spending records, and no contact is enriched twice in the same run.
- Records used match the plan from get_usage, and any batch that hit a 429 was resumed rather than silently dropped.
- If no contacts were recovered, the report says so plainly and lists why (not found, no email, unknown) instead of returning an empty file.

## Output

One file or Sheet named like "Bounce recovery – <date>" with four tabs (or four CSVs): Recovered, Catch-all, Still deliverable, Unresolved. Columns: full_name, original_email, original_company, current_title, current_company, current_domain, new_email, email_status, confidence, checked_at, moved (yes/no), note. Recovered holds only verified addresses and is send-ready. Catch-all holds new addresses on catch-all domains, flagged to send at lower volume. Still deliverable holds originals that now verify, likely soft bounces. Unresolved holds unknown results (treated as unconfirmed), contacts with no email found, and 404 not_found rows; invalid addresses are listed only as the original_email, never as a contact email.

## Example

> Here's a CSV of 240 contacts that hard-bounced from our October campaign. Find out who moved and get me working emails for them. Put the results in a Google Sheet.

```
✓ 240 rows loaded · 228 after dedupe · ✓ 13,850 enrichment records left this window
✓ 228 originals rechecked · 11 now verify (likely soft bounce)
✓ 217 enriched · 134 moved company · 102 new verified · 19 catch-all · 96 unresolved
→ Sheet "Bounce recovery – Nov" created, 4 tabs
```

Illustrative output.

## Cost and limits

verify_email uses 1 enrichment record per email checked, and enrich_person uses 1 enrichment record per record returned; emails from enrich_person are already verified, so there is no second charge for them. Empty results and errors such as 404 not_found use no records but still count as one request. The skill calls get_usage first (free), reads the usage object after each batch, and splits the job across five-hour windows when needed (for example Solo allows 1,000 enrichment records per five hours and 5,000 per week). On a 429 it waits for Retry-After or resets_at; on the free plan it stops at 402 free_records_exhausted and asks the user to upgrade. Turning off the recheck step saves one record per contact. No scrape units are used.

## What it doesn't do

- Send emails, restart sequences or remove anyone from a sequencer's suppression list; it only supplies data to the tools that send.
- Guess email patterns or promote catch-all and unknown addresses to verified.
- Recontact people who unsubscribed or opted out; suppressed records are never served, and honouring the user's own suppression list stays with the user.
