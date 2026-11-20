---
name: batch-job-runner
description: "Runs large enrich_person jobs in batches sized to the remaining Leadsets limits, checkpoints progress, pauses on 429s and resumes when windows refill, then returns a segmented result file with a progress report. Use when someone says \"enrich this whole file\", \"run this overnight\", \"resume the batch\", \"don't stall on limits\" or hands over a list larger than one five-hour window."
license: MIT
metadata:
  title: "Batch job runner"
  category: "Usage and ops"
  outcome: "Get verified contact data"
  tools: [get_usage, enrich_person]
  version: "1.0"
  author: Leadsets
  homepage: https://www.leadsets.ai/skills?utm_source=github&utm_medium=leadsets-skills&utm_campaign=batch-job-runner
---

# Batch job runner

Takes a list too big for one five-hour window and works through it with enrich_person, checking get_usage before every batch, pausing cleanly on limits and picking up exactly where it stopped. Built for GTM engineers and agencies who want a large enrichment job finished without babysitting it or paying for the same record twice.

**Category:** Usage and ops · **Outcome:** Get verified contact data · **Tools:** `get_usage`, `enrich_person`

## Requirements

- The Leadsets MCP server connected to your agent: `https://mcp.leadsets.ai` ([setup](https://www.leadsets.ai/docs/mcp?utm_source=github&utm_medium=leadsets-skills&utm_campaign=batch-job-runner)), or a Leadsets API key for the REST API.
- A Leadsets account. The free plan includes 1,000 records, no card ([get a key](https://www.leadsets.ai/signup?utm_source=github&utm_medium=leadsets-skills&utm_campaign=batch-job-runner)).

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

- "Enrich all 12,000 contacts in this CSV, even if it takes a few windows."
- A previous run stopped on a 429 window_full or weekly_limit and needs to resume without redoing finished rows.
- "Run this list in the background and tell me how far along it is."
- A list's row count is larger than the enrichment records left in the current window according to get_usage.
- Any enrichment job where the user asks for progress updates or a checkpoint they can restart from.

## What you give it

- **Input list**: A CSV, Google Sheet tab or CRM export with one person per row: LinkedIn URL, or name plus company domain, or an existing work email. The agent reads it through its own connection to that system.
- **Batch size** (optional): Rows per batch. Default: the smaller of 500 or the enrichment records left in the current five-hour window minus a 10% buffer, recalculated before every batch.
- **Usage ceiling** (optional): Maximum share of the weekly enrichment allowance this job may use. Default 80%, so other work still has room.
- **Destination** (optional): Where results go: CSV (default), a Google Sheet, or write-back to the source CRM through the agent's own connection.
- **Checkpoint location** (optional): Where progress is saved so the job can resume. Default: a status column on the input file plus a small run log next to it.

## Steps

1. **Load, dedupe and checkpoint the input**
   Read the list, drop exact duplicates by LinkedIn URL, email or name plus domain, and skip rows already marked done from an earlier run. Add a status column (pending, done, not_found, error) and record the total. Report how many rows are new work.
2. **Check limits and plan the run** · `get_usage`
   Call get_usage (free). Read enrichment records_5h, records_week and resets_at. Compute how many batches fit in this window, how many windows the job needs, and whether it fits under the usage ceiling this week. If on Free, compare the job to the free records left and warn that they do not refill. Show the plan and wait for a yes on jobs that span more than one window.
3. **Probe with one record** · `enrich_person`
   Call enrich_person on the first pending row only. Confirm the input columns map correctly and the response has current role, company, work_email with status, and a usage object. If it returns 400 invalid_request, fix the mapping before going further. 404 not_found on the probe is fine; try a second row.
4. **Run batches inside the window** · `enrich_person`
   Call enrich_person for each pending row in the batch, sending an Idempotency-Key per row (e.g. run id plus row id) so retries within 24 hours never count twice. Keep concurrency within plan limits. Read the usage object after each call and stop the batch early if records left drop under the buffer. Mark each row done, not_found (404, move on) or error, and write the checkpoint after every batch.
5. **Handle limits and errors** · `get_usage`
   On 429 window_full, wait Retry-After seconds, then call get_usage before resuming. On 429 weekly_limit, save the checkpoint, report resets_at and stop until then. On 500 or 503, retry with backoff and the same Idempotency-Key. On 401, 402 free_records_exhausted or 403, stop the run and tell the user; do not retry.
6. **Report progress**
   After each batch, post one line: rows done / total, records used this window, verified so far, and the next reset time if paused. Keep the same format so the user can compare updates.
7. **Assemble and deliver results**
   When no pending rows remain, write results to the destination, segmented by email status, and finish with a summary of rows done, not found, errors and records used. If the job paused, deliver partial results and say exactly when and how it resumes.

## Checks before returning

- Every row has a final status; done + not_found + error + pending equals the input total, and pending is zero unless the job is paused.
- No duplicate rows in the output, and no row was enriched twice across resumes (idempotency keys and the checkpoint agree).
- Records used, taken from usage objects and a final get_usage, stays under the usage ceiling and matches the number of rows that returned data.
- Catch-all and unknown emails sit in their own segments and never in the verified tab; no invalid email appears as a contact email.
- If a 402, 401 or weekly_limit stopped the run, the report says so plainly with the resume time or required action.

## Output

One file or sheet named after the job, e.g. "enrich-run-2026-11-09", with tabs (or files for CSV): Verified (send-ready), Catch-all (send at lower volume), Unknown (unconfirmed, do not treat as valid), No email (enriched role and company but no work email, plus 404 not_found rows), and Run log. Columns: row_id, input fields, full_name, current_role, company_name, company_domain, work_email, email_status, confidence, checked_at, run_status. Invalid emails are never served as contact emails, so they never appear in any send tab. The Run log lists batches, records used per batch, pauses with reset times and errors with request_id.

## Example

> Enrich all 4,200 contacts in leads_q4.csv with current role and work email. I'm on Solo, so spread it over as many windows as you need and tell me where it's at.

```
✓ 4,200 rows · 37 duplicates dropped · ✓ 940 enrichment records left this window
✓ Plan: 5 windows, about 4,163 records, inside this week's 5,000
✓ Batch 1–4 done: 2,100 / 4,163 · paused on window_full, resuming 14:15Z
✓ 4,163 done · 2,988 verified · 412 catch-all · 201 unknown · 562 no email
→ Sheet "leads_q4 enriched" created, 5 tabs + run log
```

Illustrative output.

## Cost and limits

enrich_person uses 1 enrichment record per record returned and 1 request per call; 404 not_found and errors use no records but still count as requests, and the request limit is five times the record allowance. Emails from enrich_person are already verified, so the skill does not call verify_email again. get_usage and job status checks cost nothing. Enrichment limits per five hours and per week are 1k/5k on Solo, 15k/75k on Pro, 150k/750k on Team, 225k/1.125M on Max; Free is 1,000 records once, shared with search, and returns 402 when used up. The skill sizes each batch to what get_usage reports, uses Idempotency-Keys so retries never double-count, waits out Retry-After on 429 window_full, stops at weekly_limit until resets_at, and respects the user's weekly ceiling. No scrape units are used.

## What it doesn't do

- Does not search for new people or companies; it only enriches rows the user already has.
- Does not spread work across multiple accounts or keys to get around limits; it waits for windows to refill.
- Does not send emails or load contacts into a sequencer; it hands back a segmented list for another tool or skill.
