---
name: champion-tracker
description: "Re-checks a list of past champions with enrich_person, flags everyone who moved to a new company, and returns their new role, new company and verified work email so you can reach them early in the new job. Use when someone asks to track champion job changes, find former customers who switched companies, or check where past buyers work now."
license: MIT
metadata:
  title: "Champion job-change tracker"
  category: "Prospecting"
  outcome: "Find new prospects"
  tools: [get_usage, enrich_person]
  version: "1.0"
  author: Leadsets
  homepage: https://www.leadsets.ai/skills?utm_source=github&utm_medium=leadsets-skills&utm_campaign=champion-tracker
---

# Champion job-change tracker

Takes your list of past champions (happy users, buyers, power users) and finds the ones who now work somewhere else, with their new role and a verified work email. Built for founders, AEs and RevOps teams who want to reach a known fan in their first 90 days at a new company, when they are setting up their stack.

**Category:** Prospecting · **Outcome:** Find new prospects · **Tools:** `get_usage`, `enrich_person`

## Requirements

- The Leadsets MCP server connected to your agent: `https://mcp.leadsets.ai` ([setup](https://www.leadsets.ai/docs/mcp?utm_source=github&utm_medium=leadsets-skills&utm_campaign=champion-tracker)), or a Leadsets API key for the REST API.
- A Leadsets account. The free plan includes 1,000 records, no card ([get a key](https://www.leadsets.ai/signup?utm_source=github&utm_medium=leadsets-skills&utm_campaign=champion-tracker)).

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

- "Which of our past champions changed jobs?"
- "Check this list of former customers and tell me who moved to a new company."
- "Find where our old buyers work now and get their new emails."
- A monthly re-check of a closed-won contact list exported from a CRM or sheet
- Before a quarterly outbound push that starts with warm, known contacts

## What you give it

- **Champion list**: CSV, Google Sheet or a CRM view the agent can read. Each row needs a full name plus the last known company or domain; a LinkedIn URL or old work email improves matching. Optional: a note on why they were a champion.
- **Last known state** (optional): The company and title on record for each champion, used as the baseline for comparison. Defaults to the company and title columns in the list. If a previous run of this skill exists, use its output as the baseline instead.
- **Window** (optional): How long a move counts as fresh. Default 90 days from the date the move is first detected.
- **Where it goes** (optional): CSV, a new tab in the same Google Sheet, or tasks or notes in the CRM through the agent's own connection. Default: CSV.

## Steps

1. **Load and clean the champion list**
   Read the list through the agent's connection to the file, sheet or CRM. Drop exact duplicates by email or LinkedIn URL, then by name plus company. Set aside rows with no name or no company or URL and report them as skipped. Record the baseline company domain and title for each remaining row. Confirm the row count and the destination with the user, and ask one question only if the baseline columns are ambiguous.
2. **Check limits and plan batches** · `get_usage`
   Call get_usage (free). Compare the number of champions to enrichment records left in the five-hour window and the week; on Free, compare to remaining free records. If the list fits, run in one pass. If not, split it into batches that fit the current window and tell the user how many windows the run will take. Do not start a batch that would cross a limit.
3. **Probe with one champion** · `enrich_person`
   Call enrich_person for one champion with the best identifier available (LinkedIn URL if present, otherwise name plus last company). Confirm the response returns current role, company with domain, email with status, and checked dates, and that the company comparison logic works on it. Fix input mapping before going further.
4. **Enrich every champion** · `enrich_person`
   Call enrich_person for each remaining champion, batch by batch, with an Idempotency-Key per call so retries never count twice. On 404 not_found, mark the row not found and move on. On 429 window_full or too_many_concurrent, wait Retry-After seconds and retry with the same key. On 429 weekly_limit, stop and report where to resume after resets_at. On 402 free_records_exhausted or 401, stop and tell the user. Read the usage object on each response and pause before the window fills.
5. **Classify each champion**
   Compare the current company domain to the baseline domain. Label each row: moved (different company), promoted or new role (same company, different title), no change, or not found. If the domains differ only by a known rebrand or parent and you cannot tell, label it needs review rather than moved. Stamp every moved row with detected_on (today) and reach_by (detected_on plus the window). Leadsets returns checked dates, not a start date, so never state when the person actually started.
6. **Sort emails by verification status**
   For moved champions, take the work email enrich_person returned with its status. Verified goes in the main list. Catch-all goes in a separate segment marked send at lower volume. Unknown goes in its own segment as unconfirmed. If no email came back, keep the row with the new role and company and mark no email. Do not run verify_email on these: emails from enrich_person are already verified.
7. **Write results and report**
   Write the output to the chosen destination through the agent's own connection. For a CRM, add a note or task on the existing contact rather than overwriting fields, unless the user asked for updates. Return a short summary: champions checked, moved, role changes, no change, not found, emails by status, records used and any batches still pending.

## Checks before returning

- Every moved row has a new company domain that differs from the baseline, and ambiguous domain changes sit in needs review, not moved.
- No email is labelled verified unless enrich_person returned status verified; catch-all and unknown are in their own segments and no invalid email appears anywhere.
- Duplicates are removed so no champion was enriched or listed twice, and skipped rows are counted in the report.
- Records used match the usage objects returned, and any batch not run because of a five-hour or weekly limit is listed with its resume time.
- If zero champions moved, say so plainly and suggest a re-run date instead of padding the list.

## Output

A table (CSV file, Sheet tab or CRM notes) named "Champion moves - <month>" with columns: full_name, why_champion, old_company, old_domain, old_title, new_company, new_domain, new_title, change_type (moved, role change, no change, not found, needs review), work_email, email_status, email_checked_at, detected_on, reach_by, match_notes. Moved champions with verified emails are the main tab. Catch-all emails go in a "catch-all" tab, marked send at lower volume. Unknown emails go in an "unconfirmed" tab. Moved champions with no email stay in the main tab with email_status blank and a no email note. Invalid emails are never served or listed. Role changes, no change and not found go in a "no move" tab for the record.

## Example

> Here's our closed-won contacts sheet from the last two years, about 400 people. Find the champions who've changed companies and give me their new emails so we can reach them in their first 90 days.

```
✓ 400 rows · 12 duplicates removed · ✓ 1,000 enrichment records left this window
✓ 371 enriched · 17 not found
✓ 46 moved · 22 role changes at the same company · 3 need review
✓ 34 verified · 6 catch-all (separate tab) · 2 unknown · 4 no email
→ Sheet "Champion moves - Nov" created, 4 tabs, reach_by dates set
```

Illustrative output.

## Cost and limits

Each enrich_person call uses 1 enrichment record when data comes back and 1 request either way; a not_found result uses no records. Emails returned by enrich_person are already verified, so there is no extra verify_email cost. get_usage is free. On Solo that is 1,000 enrichment records per five hours and 5,000 per week; on Free the 1,000 records are one time and shared with search. The skill checks get_usage first, splits big lists into batches that fit the window, reads the usage object as it goes, waits on 429 Retry-After, and uses Idempotency-Keys so retries never count twice. No search or scrape units are used.

## What it doesn't do

- Does not send outreach, create sequences or overwrite CRM fields without asking; it returns the list and leaves sending to the user's own tools.
- Does not guess a start date at the new company; reach_by is counted from when the move was detected, not from an inferred start.
- Does not find a replacement contact at the champion's old company; use a contacts-at-target-accounts or decision-maker skill for that.
