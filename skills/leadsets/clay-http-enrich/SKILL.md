---
name: clay-http-enrich
description: "Sets up a Clay HTTP API column that calls the Leadsets REST enrich endpoint to fill current role, company and verified work email for every row in a Clay table, tested on one row and paced against enrichment limits. Use when someone says \"enrich my Clay table with Leadsets\", \"add Leadsets to Clay\", \"fill emails in Clay\" or \"Clay HTTP column for emails\"."
license: MIT
metadata:
  title: "Clay table enrichment"
  category: "Outreach handoff"
  outcome: "Get verified contact data"
  tools: [get_usage, enrich_person]
  version: "1.0"
  author: Leadsets
  homepage: https://www.leadsets.ai/skills?utm_source=github&utm_medium=leadsets-skills&utm_campaign=clay-http-enrich
---

# Clay table enrichment

Wires Leadsets into a Clay table through an HTTP API column so each row gets a current role, company and a work email with an honest verification label. Built for GTM engineers and agencies who already run their lists in Clay and want one enrichment source that says what it could and could not confirm.

**Category:** Outreach handoff · **Outcome:** Get verified contact data · **Tools:** `get_usage`, `enrich_person`

## Requirements

- The Leadsets MCP server connected to your agent: `https://mcp.leadsets.ai` ([setup](https://www.leadsets.ai/docs/mcp?utm_source=github&utm_medium=leadsets-skills&utm_campaign=clay-http-enrich)), or a Leadsets API key for the REST API.
- A Leadsets account. The free plan includes 1,000 records, no card ([get a key](https://www.leadsets.ai/signup?utm_source=github&utm_medium=leadsets-skills&utm_campaign=clay-http-enrich)).

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

- "Add a Leadsets column to my Clay table so it fills emails and titles."
- "Set up a Clay HTTP column that calls Leadsets enrich for every row."
- A Clay table of people has missing or stale emails and roles and the user wants them filled without leaving Clay.
- "Replace my Clay email waterfall step with Leadsets and keep catch-alls separate."

## What you give it

- **Clay table**: The table name and which columns identify each person (for example LinkedIn URL, or full name plus company domain). The agent asks which column to trust if several exist.
- **Leadsets API key**: A key starting with ls_live_, stored in Clay as a secret or auth header, never pasted into a visible cell. The free key works for small tables.
- **Rows to run** (optional): How many rows to enrich. Default: all rows where the email column is empty. Rows that already have a verified email are skipped.
- **Output columns** (optional): Which fields to write back. Default: role, company, work email, email status, confidence, checked date and request ID.

## Steps

1. **Check limits and size the run** · `get_usage`
   Call get_usage and read enrich records_5h, records_week and their reset times (or the free records left). Count the rows to run. If the row count exceeds what is left in the five-hour window, plan batches that fit and tell the user how many rows will run now and when the rest can run.
2. **Probe one real row** · `enrich_person`
   Take one row from the table and call enrich_person with its identifiers through MCP. Confirm the response shape: current_role, company name and domain, work_email with status and confidence, checked_at and match_reasons. If it returns 404 not_found, try a second row before concluding the identifier column is wrong. This costs at most one enrichment record.
3. **Build the Clay HTTP API column**
   Through the agent's own access to Clay (or by giving the user exact settings to paste), add an HTTP API column: method POST, URL https://api.leadsets.ai/v1/people/enrich, header Authorization: Bearer <stored key>, and an Idempotency-Key header built from the row ID so reruns never count records twice. Map the identifier columns into the request body as documented in the Leadsets API reference. Do not invent extra body fields.
4. **Add parsed output columns**
   Add columns that extract from the response: ls_role, ls_company, ls_company_domain, ls_work_email, ls_email_status, ls_email_confidence, ls_checked_at and request_id. Add one formula column ls_send_ready that is true only when ls_email_status is verified.
5. **Run a 10-row test batch**
   Run the column on 10 rows. Check that statuses parse, that 404 rows show as no match rather than an error, and that no row shows an email marked invalid as a contact email. Fix the mapping before going further.
6. **Run the rest in batches inside the window** · `get_usage`
   Run the remaining rows in batches sized to the enrichment records left. Call get_usage between batches. On 429 window_full, stop and rerun the failed rows after Retry-After; on 429 weekly_limit, resume after resets_at. On 402 free_records_exhausted or 401, stop and tell the user. Never rerun 400 or 404 rows unchanged.
7. **Report results**
   Summarise rows enriched, verified, catch-all, unknown, no match and skipped, plus records used and what is left. Point the user to a Clay view filtered on ls_send_ready for sending and a separate view for catch-all rows.

## Checks before returning

- The one-row probe and the 10-row test both returned parseable status values before the full run started.
- Every row with an email has one of verified, catch-all or unknown in ls_email_status; no row presents an invalid address as a contact email.
- Rows that already had a verified email, and duplicate rows for the same person, were skipped rather than enriched again.
- Enrichment records used plus records remaining match the get_usage reading, and any rows blocked by a 429 are listed for a later rerun.
- Rows returning 404 not_found are marked no match, not left blank or retried in a loop.

## Output

The same Clay table with added columns: ls_role, ls_company, ls_company_domain, ls_work_email, ls_email_status, ls_email_confidence, ls_checked_at, request_id and ls_send_ready. Verified emails set ls_send_ready to true. Catch-all emails are kept with their label and grouped in a separate view for lower-volume sending. Unknown emails are kept as unconfirmed and excluded from the send-ready view. Invalid addresses are never written as contact emails, and rows with nothing to enrich show "no match". A short run summary is returned in chat.

## Example

> My Clay table "Q4 fintech VPs" has 400 people with LinkedIn URLs but half the emails are missing. Add a Leadsets column to fill emails and current titles, and keep catch-alls out of the send list.

```
✓ 1 row probed  ·  ✓ 13,840 enrichment records left this window
✓ HTTP column "Leadsets enrich" added  ·  ✓ 10-row test passed
✓ 212 rows enriched  ·  171 verified  ·  23 catch-all  ·  9 unknown  ·  9 no match
→ View "Send ready" (171) and view "Catch-all, low volume" (23) created
```

Illustrative output.

## Cost and limits

Each enriched row uses 1 enrichment record, counted only when data comes back; rows that return no match use no records but still count as one request. Emails from enrich_person are already verified, so no separate verify_email call or second bill is needed. get_usage is free and is called before and between batches. Batches are sized to the five-hour enrichment window (for example 1,000 on Solo, 15,000 on Pro) and the weekly limit, and the Idempotency-Key header means Clay reruns never double-count. On the free plan, the 1,000 one-time records are shared with search, so the skill tells the user up front how many rows the remaining records cover.

## What it doesn't do

- Does not send emails or push rows into a sequencer; it only fills the Clay table.
- Does not search for new people to add to the table; it enriches the rows that are already there.
- Does not mark catch-all or unknown emails as send-ready, and does not return phone numbers.
