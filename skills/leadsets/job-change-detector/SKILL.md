---
name: job-change-detector
description: "Re-checks an existing contact list with Leadsets enrich_person and flags everyone who changed role or company, with the new title, new company and a labelled work email when one exists. Plans the run with get_usage so large lists stay inside limits. Use when someone says \"who on this list changed jobs\", \"check for job changes\", \"refresh my contacts\" or \"flag people who left\"."
license: MIT
metadata:
  title: "Job-change detector"
  category: "Enrichment"
  outcome: "Keep your CRM clean"
  tools: [get_usage, enrich_person]
  version: "1.0"
  author: Leadsets
  homepage: https://www.leadsets.ai/skills?utm_source=github&utm_medium=leadsets-skills&utm_campaign=job-change-detector
---

# Job-change detector

Takes a contact list you already own, re-checks every person against current Leadsets data, and returns who moved company, who changed role, and who is unchanged. Built for RevOps, founders and SDR teams who want to stop sequencing people at companies they left and to follow former contacts to their new accounts.

**Category:** Enrichment · **Outcome:** Keep your CRM clean · **Tools:** `get_usage`, `enrich_person`

## Requirements

- The Leadsets MCP server connected to your agent: `https://mcp.leadsets.ai` ([setup](https://www.leadsets.ai/docs/mcp?utm_source=github&utm_medium=leadsets-skills&utm_campaign=job-change-detector)), or a Leadsets API key for the REST API.
- A Leadsets account. The free plan includes 1,000 records, no card ([get a key](https://www.leadsets.ai/signup?utm_source=github&utm_medium=leadsets-skills&utm_campaign=job-change-detector)).

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

- "Which of these 600 HubSpot contacts changed jobs since last quarter?"
- Before loading an old list into a sequencer, to catch people who left their company
- Quarterly CRM hygiene on a contact segment such as customers, open deals or past champions
- "Re-check this CSV and tell me who has a new title or a new employer"
- After bounces start rising on a list, to see whether contacts moved

## What you give it

- **Contact list**: CSV, Google Sheet or a CRM export or view the agent can read through its own connection. Each row needs at least full name plus company domain, or a LinkedIn URL, or a work email. Stored title and company are required for comparison.
- **Fields to compare** (optional): What counts as a change. Default: company (compared by domain) and title. Optionally seniority only, so promotions are flagged separately from lateral moves.
- **Scope** (optional): How many contacts to re-check this run. Default: the whole list, split across five-hour windows if it is larger than the enrichment records left.
- **Where results go** (optional): Default: a new CSV or a new Google Sheet tab. CRM write-back is only proposed, never done without the user confirming the exact fields.

## Steps

1. **Load and clean the list**
   Read the list through the agent's own connection. Map columns to name, company domain, LinkedIn URL, work email, stored title and stored company. Remove exact duplicates by email or LinkedIn URL and drop rows with no usable identifier, counting them for the report. If the stored title or company column is missing, ask the user once which column holds it.
2. **Check limits and plan batches** · `get_usage`
   Call get_usage (free). Compare the cleaned row count with enrichment records left in the five-hour window and the week. If the list fits, run it in one pass. If not, tell the user how many contacts run now and when the window resets, and propose splitting the rest. On the free plan, remind the user that the 1,000 records are one time and shared with search.
3. **Probe with one contact** · `enrich_person`
   Call enrich_person on a single row, using the strongest identifier available (LinkedIn URL, then work email, then name plus company domain). Confirm the response maps cleanly: current role, company name and domain, work email with status and checked_at. Fix the column mapping before going further if it does not.
4. **Re-check every contact** · `enrich_person`
   Call enrich_person for each remaining row in batches sized to the plan, sending an Idempotency-Key per call so retries never count twice. Read the usage object on each response to pace the run. On 404 not_found, mark the row not found and move on. On 429 window_full, wait the Retry-After seconds and resume. On 429 weekly_limit, stop and report the resets_at time. On 402 free_records_exhausted, stop and ask the user to upgrade. Do not retry 400 or 401.
5. **Classify each contact**
   Compare returned data with stored values. Company changed: current company domain differs from the stored domain. Role changed: same company, different title or seniority (treat fuzzy equivalents like "VP Sales" and "Vice President, Sales" as unchanged). Unchanged: both match. Not found: no data returned. Record the checked_at date on every changed field so the user can see how fresh the evidence is.
6. **Label emails for movers**
   For company changes, mark the stored email at the old company as do not send. Carry the new work email from enrich_person with its status: verified goes in the main tab, catch-all in its own segment for lower-volume sending, unknown as unconfirmed. Emails from enrich_person are already verified, so do not call verify_email again. Invalid addresses are never served, so a mover with no new email is listed with an empty email and the reason.
7. **Return results and summary**
   Write the output file or tabs, then print a short run summary with counts per status and records used. If the user wants CRM updates, list the proposed field changes per record and wait for confirmation before writing anything through the agent's CRM connection.

## Checks before returning

- Every row is accounted for: changed company + changed role + unchanged + not found + skipped equals the input row count
- No email labelled catch-all or unknown appears in the verified tab, and old-company emails for movers are flagged do not send
- Company changes are decided by domain, not by company name text, so renames and formatting differences are not flagged as moves
- Records used match the usage object totals and stayed inside the five-hour and weekly enrichment limits; any unfinished rows are listed with the resume time
- Duplicates removed before enrichment so no person was enriched twice

## Output

A CSV or Google Sheet with tabs "Moved company", "Changed role", "Unchanged" and "Not found". Columns: full_name, stored_title, stored_company, stored_email, current_title, current_company, current_domain, change_type (company_change, role_change, promotion, unchanged, not_found), new_work_email, email_status (verified, catch-all, unknown, none), old_email_action (do not send, keep), checked_at, source_row. Verified new emails stay in the main tabs; catch-all rows are also copied to a "Catch-all" tab for lower-volume sending; unknown is marked unconfirmed; invalid emails never appear because Leadsets does not serve them, so those rows show an empty email. Followed by a plain-text run summary with counts and records used.

## Example

> Here's our HubSpot export of 480 contacts at customer accounts. Check who changed jobs since we last talked to them and put the results in a Google Sheet.

```
✓ 480 rows loaded  ·  6 duplicates removed  ·  ✓ 1,000 enrichment records left this window
✓ 474 re-checked  ·  451 found  ·  23 not found (no records used)
✓ 38 moved company (29 verified email, 6 catch-all, 3 none)  ·  21 changed role
→ Sheet "Job changes – Nov" created, 5 tabs  ·  CRM updates proposed, not written
```

Illustrative output.

## Cost and limits

Each enrich_person call that returns data uses 1 enrichment record and every call counts as 1 request; a not_found result uses no records. Emails returned by enrich_person are already verified, so there is no extra verify_email cost. get_usage is free and runs before the batch. On Solo the run fits 1,000 contacts per five hours and 5,000 per week; Pro 15,000 and 75,000. Free accounts share 1,000 one-time records across search and enrichment. Lists larger than the window are split across windows, and Idempotency-Keys keep retries from counting twice. No scrape units are used.

## What it doesn't do

- Write changes back to a CRM or delete records without the user approving the exact field updates
- Send outreach or enroll movers in sequences; it only flags them and supplies the new data
- Treat catch-all or unknown emails as verified, or search for new contacts beyond the people already on the list
