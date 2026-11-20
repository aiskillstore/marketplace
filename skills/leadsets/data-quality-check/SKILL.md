---
name: data-quality-check
description: "Audits an existing contact list for duplicates, stale titles and risky emails using Leadsets enrich_person and verify_email, then returns a prioritized fix list without changing the source. Use when someone says \"check this list before I use it\", \"audit my CSV\", \"find duplicates and bad emails\", \"is this list still accurate\" or \"clean up this export\"."
license: MIT
metadata:
  title: "Data quality check"
  category: "List building"
  outcome: "Keep your CRM clean"
  tools: [get_usage, enrich_person, verify_email]
  version: "1.0"
  author: Leadsets
  homepage: https://www.leadsets.ai/skills?utm_source=github&utm_medium=leadsets-skills&utm_campaign=data-quality-check
---

# Data quality check

Takes a list you already have (a CSV, a Google Sheet or a CRM export) and tells you what is wrong with it: duplicate people, titles or companies that are out of date, and emails that are catch-all, unknown or invalid. You get the original rows with status columns added plus a fix list sorted by severity. Built for GTM engineers, RevOps and agencies who inherit lists and need to know what is safe to use before anyone sends.

**Category:** List building · **Outcome:** Keep your CRM clean · **Tools:** `get_usage`, `enrich_person`, `verify_email`

## Requirements

- The Leadsets MCP server connected to your agent: `https://mcp.leadsets.ai` ([setup](https://www.leadsets.ai/docs/mcp?utm_source=github&utm_medium=leadsets-skills&utm_campaign=data-quality-check)), or a Leadsets API key for the REST API.
- A Leadsets account. The free plan includes 1,000 records, no card ([get a key](https://www.leadsets.ai/signup?utm_source=github&utm_medium=leadsets-skills&utm_campaign=data-quality-check)).

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

- "Audit this list of 600 contacts for duplicates, stale titles and bad emails before we load it."
- A purchased, inherited or event list needs a quality check before it goes into a CRM or sequencer.
- "How much of this CSV is still accurate?" or "Which of these people have moved?"
- A campaign bounced more than expected and the user wants to know which rows caused it.
- Before merging several lists, to see what overlaps and what is broken in each.

## What you give it

- **The list**: A CSV, Excel file, Google Sheet or CRM export reached through the agent's own connection. Needs at least name plus company or domain per row; email, title and LinkedIn URL improve matching.
- **Column mapping** (optional): Which columns hold name, company, domain, title and email. Default: the agent infers them from headers and confirms the mapping once before spending records.
- **Checks to run** (optional): Any of duplicates, stale titles, risky emails. Default: all three. Duplicates alone spends no records.
- **Stale rule** (optional): What counts as stale. Default: current company differs from the list (moved), or current title differs in function or seniority (changed role). Minor wording differences are ignored.
- **Where results go** (optional): Default: same format as the input, written as a new file or new tabs. The source list is never overwritten.

## Steps

1. **Load the list and find duplicates locally**
   Read the list, confirm the column mapping, and normalize names, domains and emails (lowercase, trim, strip mailbox tags). Group rows that share an email, a LinkedIn URL, or the same normalized name plus domain. Assign a dup_group ID and pick a keeper per group (most complete row, most recent date if one exists). Count unique people; only unique people are sent to Leadsets in later steps. If the user only asked for duplicates, skip to the final step.
2. **Check limits and plan the run** · `get_usage`
   Call get_usage (free). Compare enrichment records left in the five-hour window and the week against the planned spend: up to 1 enrich_person record per unique person plus 1 verify_email per address that enrichment does not already cover. On Free, remember the 1,000 records are shared across search and enrichment and do not refill. If the run would cross a window, tell the user, then either split it into batches across windows or narrow the scope (for example only rows going into the next campaign).
3. **Probe with one record** · `enrich_person`
   Call enrich_person on one unique person from the list to confirm the mapping produces a match (right person, right company). If it returns 404 not_found, check the input fields before continuing rather than running the whole list. Read the usage object in the response to confirm what was counted.
4. **Enrich unique people for current role and email** · `enrich_person`
   Run enrich_person on every remaining unique person in batches sized to the remaining window, with an Idempotency-Key per call so retries never double count. For each person record current_role, company, work_email with status and confidence, and checked_at. Compare against the list: mark title_status as current, title_changed, moved (company differs) or not_found. A 404 not_found uses no records; mark the row not_found and move on. On 429 window_full wait for Retry-After and resume; on 429 weekly_limit stop and report where it paused; on 402 free_records_exhausted stop and ask the user to upgrade.
5. **Verify list emails that enrichment did not cover** · `verify_email`
   Emails returned by enrich_person are already verified, so do not re-verify them. Call verify_email only on list emails that enrichment did not return or that differ from the enriched email. Each standalone check counts toward enrichment. Record status (verified, catch-all, unknown, invalid), confidence and checked_at for the email that is actually in the list. For very large lists on a paid plan, submit the batch as an async job and pull results when ready.
6. **Build the fix list**
   For every row assign one action: keep, merge (duplicate, not the keeper), update_title, moved_review (person left the company), replace_email (list email invalid but enrichment returned a verified one), remove_email (invalid with no replacement), send_low_volume (catch-all), hold (unknown), or not_found. Sort the fix list by severity: invalid emails first, then moved, unknown, duplicates, title updates, catch-alls.
7. **Return results and report**
   Write the annotated list and the separate tabs or files described in the output section through the agent's connection to Sheets, CSV or the CRM export location. Do not write changes back into a CRM unless the user approves the fix list. Report counts per check, records spent from the usage object, and anything that could not be confirmed.

## Checks before returning

- Every email in the output carries one of verified, catch-all, unknown or invalid; catch-all and unknown are never reported or counted as verified.
- Duplicate groups each have exactly one keeper, and the row count of the annotated file equals the input row count (nothing silently dropped).
- Records spent match the usage objects returned, and the run stayed inside the limits shown by get_usage; any paused batch is reported with where it stopped.
- Moved and title_changed flags are based on enrich_person results with a checked_at date, not on guesses; not_found rows are labelled as unconfirmed, not as stale.
- If the list is empty after mapping or no rows match, say so and stop before spending records.

## Output

The original list with added columns: dup_group, is_keeper, current_title, current_company, title_status (current, title_changed, moved, not_found), email_status (verified, catch-all, unknown, invalid), email_confidence, suggested_email (only when enrichment found a verified replacement), checked_at, action. Tabs or files: "Annotated" (all rows), "Fix list" (rows needing action, sorted by severity), "Duplicates" (grouped, keeper first), "Catch-all" (kept but flagged to send at lower volume). Invalid emails are marked remove_email or replace_email and never left as contact emails. Unknown emails are marked hold and treated as unconfirmed. A summary line reports counts per check and records used.

## Example

> Here's our webinar list from last spring, about 640 rows in a Google Sheet. Check it for duplicates, people who changed jobs and bad emails before we import it into HubSpot.

```
✓ 640 rows · 41 duplicates in 18 groups · 599 unique people
✓ 2,940 enrichment records left this window · 573 enriched · 26 not found
✓ 62 moved · 47 title changes · 412 verified · 58 catch-all · 31 unknown · 44 invalid (19 with verified replacement)
→ Sheet "Webinar list audit" created: Annotated, Fix list (283 rows), Duplicates, Catch-all
```

Illustrative output.

## Cost and limits

Finding duplicates is done by the agent and spends nothing. enrich_person uses 1 enrichment record per person returned; a not_found result uses no records but still counts as a request. Standalone verify_email uses 1 per email and counts toward the enrichment limit, so the skill skips it for emails enrich_person already verified. Only unique people are enriched, which keeps spend at or below the deduplicated row count. get_usage is free and runs before the run; the usage object in each response is read between batches. Five-hour and weekly windows (for example Solo 1,000 enrichments per five hours and 5,000 per week) decide batch size; over a limit the API returns 429 with Retry-After and the blocked call counts against nothing. Free accounts draw on 1,000 one-time records shared with search. No scrape units are used.

## What it doesn't do

- Write changes into a CRM or delete rows from the source list without the user approving the fix list.
- Find new contacts or replacements for people who moved; that belongs to skills like Job-change detector, Bounce recovery or Contacts at target accounts.
- Mark catch-all or unknown addresses as safe, or add phone numbers (Leadsets does not offer them).
