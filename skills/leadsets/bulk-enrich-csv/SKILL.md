---
name: bulk-enrich-csv
description: "Enriches every row of a CSV, Excel or Google Sheets file with current role, company and a verified work email using enrich_person, calling get_usage before each batch so the run never stalls on a limit. It splits large files across windows and segments results by email status. Use when someone says \"enrich this CSV\", \"fill in emails for this file\", \"bulk enrich my list\" or \"add roles and emails to this spreadsheet\"."
license: MIT
metadata:
  title: "Bulk enrich a CSV"
  category: "Enrichment"
  outcome: "Get verified contact data"
  tools: [get_usage, enrich_person]
  version: "1.0"
  author: Leadsets
  homepage: https://www.leadsets.ai/skills?utm_source=github&utm_medium=leadsets-skills&utm_campaign=bulk-enrich-csv
---

# Bulk enrich a CSV

Takes a whole file of contacts and returns the same file with current role, company and a verified work email added to every row it can match, plus an honest status on the rows it cannot. Built for GTM engineers, agencies and founders who have a list from an event, an export or an old CRM and want it usable without babysitting the run.

**Category:** Enrichment · **Outcome:** Get verified contact data · **Tools:** `get_usage`, `enrich_person`

## Requirements

- The Leadsets MCP server connected to your agent: `https://mcp.leadsets.ai` ([setup](https://www.leadsets.ai/docs/mcp?utm_source=github&utm_medium=leadsets-skills&utm_campaign=bulk-enrich-csv)), or a Leadsets API key for the REST API.
- A Leadsets account. The free plan includes 1,000 records, no card ([get a key](https://www.leadsets.ai/signup?utm_source=github&utm_medium=leadsets-skills&utm_campaign=bulk-enrich-csv)).

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

- "Enrich this CSV of 2,000 contacts with work emails and current titles."
- "Here's a Google Sheet of LinkedIn URLs. Fill in role, company and email for each."
- A file is too large to enrich in one five-hour window and needs to be split into batches that resume cleanly.
- "Add emails to this webinar export, but only give me the ones I can actually send to."
- Someone uploads an Excel file and asks to fill in the missing columns before importing it into a CRM or sequencer.

## What you give it

- **The file**: A CSV, Excel file or Google Sheet the agent can read through its own connection. Each row needs at least one identifier: a LinkedIn profile URL, or full name plus company name or domain. A work email column is also accepted for refreshing role and company.
- **Column mapping** (optional): Which columns hold the identifiers. Default: the agent infers the mapping from headers and confirms it with the user in one question before spending anything.
- **Rows to enrich** (optional): All rows, or a filter such as "only rows with no email" or "first 500". Default: every row that has a usable identifier and is not a duplicate.
- **Where it goes** (optional): A new CSV, a new Google Sheet or new tabs in the same Sheet. Default: a copy of the original file with enrichment columns appended, plus separate catch-all and review segments. The original file is never overwritten.

## Steps

1. **Read the file and plan the rows**
   Open the file, confirm the column mapping with the user if headers are ambiguous, and assign each row a stable row_id. Drop exact duplicates (same LinkedIn URL, or same name plus domain) and mark them skipped_duplicate. Mark rows with no usable identifier as skipped_no_identifier. Report the count of enrichable rows before moving on.
2. **Check limits and size the batches** · `get_usage`
   Call get_usage and read enrichment records left in the five-hour window and in the week (on the free plan, the remaining free records, shared with search). Set batch size to the smaller of 100 rows and what is left in the window. If the file needs more records than the window or week allows, tell the user how many rows fit now, how many will run after the reset time get_usage returned, and whether to split across windows or submit the remaining rows as an async job. Do not start until the user accepts the plan when the file will not fit in the current window.
3. **Probe with one row** · `enrich_person`
   Call enrich_person on the first enrichable row only. Confirm the mapping worked: the returned name and company should match the input, and the work_email should carry a status. If it returns 404 not_found, try one more row before concluding the mapping is wrong. If it returns 400 invalid_request, fix the field mapping named in the message and probe again. Do not continue until one row comes back correctly.
4. **Enrich in batches, checking limits before each one** · `enrich_person`
   For each batch, call get_usage first, then call enrich_person once per row, sending an Idempotency-Key derived from the row_id so a retry never counts the record twice. Read the usage object on each response to pace the run. On 404 not_found, mark the row not_found and move on. On 429 window_full or too_many_concurrent, wait the Retry-After seconds and retry with the same key. On 429 weekly_limit, stop and record where to resume after resets_at, or submit the remaining rows as an async job and poll its status with the jobs/{id} route. On 402 free_records_exhausted or 401 unauthorized, stop the run and tell the user. Save progress after every batch so the run can resume from the last completed row_id.
5. **Segment by email status**
   Emails returned by enrich_person are already verified, so do not call verify_email again. Sort rows into: verified (send-ready), catch-all (send at lower volume), unknown (unconfirmed, do not send without review), and no email (not found, or no address served because invalid emails are never returned as contacts). Flag rows where the enriched company or domain differs from the input as possible job changes.
6. **Write the output and report**
   Through the agent's own connection to Google Sheets or the file system, write the enriched copy and the segments described in the output section. Then report counts per status, rows skipped and why, records used, and any rows still pending a window reset with the time they can resume.

## Checks before returning

- Every input row appears exactly once in the output with an enrich_status, and enriched + not_found + skipped + pending equals the original row count.
- No catch-all or unknown address sits in the send-ready segment, and no row is labelled verified unless enrich_person returned status verified.
- Records used matches the usage objects returned during the run and stays inside the enrichment window and weekly limit reported by get_usage; nothing was retried without its original Idempotency-Key.
- Duplicates were enriched once, not once per copy, and rows whose returned company differs from the input are flagged rather than silently overwritten.
- If the run paused on a limit, the report names the exact resume point (last row_id) and the reset time, and no partial batch is left unrecorded.

## Output

A copy of the input named "<original name> – enriched" with all original columns untouched and these columns appended: row_id, enrich_status (enriched, not_found, skipped_duplicate, skipped_no_identifier, pending), full_name, current_title, company_name, company_domain, work_email, email_status, email_confidence, checked_at, company_changed (yes/no). In Google Sheets this is four tabs: "Send-ready" (email_status verified), "Catch-all" (send at lower volume), "Review" (unknown emails, not_found rows, company_changed rows) and "All rows". For CSV output the same segments are separate files with those suffixes. Unknown emails are kept but never marked send-ready. Invalid emails are never served, so those rows show no work_email and land in Review.

## Example

> Here's our trade show scan export, 1,840 rows with names and company domains. Enrich it with titles and work emails and put the results back in the same Google Sheet.

```
✓ 1,840 rows read  ·  1,792 enrichable  ·  48 duplicates skipped
✓ 1,000 enrichment records left this window → 2 windows planned, batches of 100
✓ 1,511 enriched  ·  281 not found (no records used)
✓ 1,204 verified  ·  187 catch-all  ·  64 unknown  ·  56 no email  ·  73 company changed
→ Sheet "Trade show scans" updated, 4 new tabs
```

Illustrative output.

## Cost and limits

Each row that comes back with data uses 1 enrichment record; rows that return nothing use no records but still count as 1 request, and the request limit is five times the record allowance, so normal retries never hit it. Emails from enrich_person are already verified, so there is no second verify_email charge. get_usage costs nothing and runs before every batch. On Solo the window is 1,000 enrichment records per five hours and 5,000 per week (Pro 15k and 75k, Team 150k and 750k, Max 225k and 1.125M); on Free the 1,000 one-time records are shared with search and do not refill. When a file is bigger than what is left, the skill splits it across rolling windows or submits the rest as an async job, and Idempotency-Keys on every call mean a retried row is never counted twice. A 429 blocked call counts against nothing.

## What it doesn't do

- Does not run a separate verify_email pass on enriched addresses or verify emails already in the file; use the clean-a-list skill for that.
- Does not overwrite the original file or write back to a CRM; it produces an enriched copy and leaves syncing to the CRM to a separate step.
- Does not return phone numbers or home addresses, and does not guess an email when Leadsets has none.
