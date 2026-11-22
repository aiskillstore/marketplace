---
name: pre-send-check
description: "Runs a final verify_email pass on every contact in a loaded Instantly, Smartlead or LinkedCamp campaign, labels each address verified, catch-all, unknown or invalid, and pauses risky contacts before launch. Use when someone says \"check this campaign before I send\", \"pre-send check\", \"verify my sequence list\" or \"pause bad emails before launch\"."
license: MIT
metadata:
  title: "Pre-send campaign check"
  category: "Email verification"
  outcome: "Launch outreach"
  tools: [get_usage, verify_email]
  version: "1.0"
  author: Leadsets
  homepage: https://www.leadsets.ai/skills?utm_source=github&utm_medium=leadsets-skills&utm_campaign=pre-send-check
---

# Pre-send campaign check

Takes a campaign that is already loaded in your sequencer, re-verifies every address with Leadsets, and pauses the contacts most likely to bounce before the first email goes out. Built for founders, SDRs and agencies who want to protect their sending domain at the last step, not after the bounce report.

**Category:** Email verification · **Outcome:** Launch outreach · **Tools:** `get_usage`, `verify_email`

## Requirements

- The Leadsets MCP server connected to your agent: `https://mcp.leadsets.ai` ([setup](https://www.leadsets.ai/docs/mcp?utm_source=github&utm_medium=leadsets-skills&utm_campaign=pre-send-check)), or a Leadsets API key for the REST API.
- A Leadsets account. The free plan includes 1,000 records, no card ([get a key](https://www.leadsets.ai/signup?utm_source=github&utm_medium=leadsets-skills&utm_campaign=pre-send-check)).

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

- "Check my Instantly campaign before I launch it tomorrow."
- "Run a pre-send check on the Q4 RevOps sequence in Smartlead and pause anything risky."
- A list was built or imported weeks ago and is about to be sent for the first time.
- "Verify the leads in my LinkedCamp campaign and tell me what's safe to send."
- A previous send had a high bounce rate and the next campaign needs checking first.

## What you give it

- **Campaign**: The sequencer (Instantly, Smartlead, LinkedCamp or another tool) and the campaign name or ID. The agent reads contacts through its own connection to that tool, or from a CSV export if there is no connection.
- **Catch-all handling** (optional): What to do with catch-all addresses: move to a separate lower-volume segment, pause, or leave active. Default: move to a separate low-volume segment and leave them out of the main send.
- **Action mode** (optional): Report only, or report and pause. Default: report first, then pause invalid and unknown contacts after the user confirms.
- **Scope** (optional): Which contacts to check: all contacts, or only those not yet sent to. Default: only contacts with no step sent yet.

## Steps

1. **Read the campaign and dedupe**
   Pull the in-scope contacts from the campaign through the agent's connection to the sequencer (or the CSV the user provides). Keep email, name, company and the sequencer's contact ID. Lowercase and trim emails, drop exact duplicates, and note blank email fields. Report the count to check before spending anything.
2. **Check remaining limits and plan batches** · `get_usage`
   Call get_usage (it costs nothing). Each verify_email counts toward the enrichment meter, so compare the contact count with enrichment records left in this five-hour window and this week, or free records left on the free plan. If the count exceeds what is left, tell the user, propose splitting across windows, and verify the contacts scheduled to send first.
3. **Probe with one address** · `verify_email`
   Call verify_email on a single address from the campaign. Confirm the response returns a status (verified, catch-all, unknown or invalid), a confidence score and a usage object. If it fails with 401 or 403, stop and report the connection problem.
4. **Verify the rest in batches** · `verify_email`
   Verify remaining addresses in batches sized to the window planned in step 2. Over REST, send an Idempotency-Key on each call so retries never count twice; for large lists on a paid plan, submit a bulk async job and poll its status. Read the usage object after each batch. On 429 window_full or too_many_concurrent, wait for Retry-After and retry. On 429 weekly_limit, stop and report where to resume. On 402 free_records_exhausted, stop and ask the user to upgrade.
5. **Segment results**
   Group every contact by status: verified (send), catch-all (apply the catch-all setting), unknown (treat as unconfirmed, pause), invalid (pause, never send). Never move a catch-all or unknown into the verified group. Keep confidence and the check time on each row.
6. **Pause risky contacts**
   Show the user the counts per segment and the list of contacts to pause. After confirmation (or immediately if action mode is report and pause with pre-approval), pause invalid and unknown contacts, and apply the catch-all choice, through the agent's own connection to the sequencer. Where the tool supports tags or custom fields, write the verification status and check date. If there is no connection, produce the pause list as a CSV for the user to apply.
7. **Report**
   Return a short summary: contacts checked, verified, catch-all, unknown, invalid, duplicates removed, contacts paused, and any contacts not checked because of limits, with when to resume.

## Checks before returning

- Every in-scope contact has exactly one status from verify_email, or is listed as not checked with the reason (limit reached, blank email, error).
- No catch-all or unknown address is counted or labelled as verified, and no invalid address is left active in the campaign.
- Duplicate emails were removed before verification so no address was verified or sent twice.
- The number of paused contacts in the sequencer matches the pause list in the report; any mismatch is reported.
- Records used match the usage object, and remaining enrichment records for the window and week are stated in the summary.

## Output

A run summary plus a table (CSV or a sheet) with one row per contact: email, full name, company, sequencer contact ID, status, confidence, checked date, action taken (kept, moved to low-volume, paused, not checked). Segments or tabs: "Send" (verified), "Catch-all" (separate low-volume segment by default), "Paused - unknown" (unconfirmed, held back), "Paused - invalid" (never sent). Contacts not checked because of limits or errors are listed separately with the reason.

## Example

> My Instantly campaign "Northwind lookalikes - Nov" launches tomorrow with about 600 contacts. Run a pre-send check and pause anything that might bounce. Keep catch-alls but put them in their own lower-volume segment.

```
✓ 612 contacts read · 9 duplicates removed · ✓ 4,210 enrichment records left this window
✓ 603 verified with verify_email
✓ 521 verified · 47 catch-all (low-volume segment) · 22 unknown · 13 invalid
→ 35 contacts paused in "Northwind lookalikes - Nov", report saved as pre-send-check.csv
```

Illustrative output.

## Cost and limits

Each address checked with verify_email counts toward the enrichment limit (1 per email), and every call counts as one request, hit or miss; the request limit is five times the record allowance, so normal retries do not hit it. The skill calls get_usage first (free), probes with one address, then sizes batches to what is left: for example Solo allows 1,000 enrichment records per five hours and 5,000 per week, so a larger campaign is split across windows with the earliest-sending contacts first. On the free plan checks draw on the 1,000 one-time records shared with search. Over a limit the API returns 429 with Retry-After and the blocked call counts against nothing. Bulk async verification jobs are available on paid plans. No search records or scrape units are used.

## What it doesn't do

- Send, launch or schedule the campaign; Leadsets is not a sending tool and the skill only pauses contacts through the agent's connection to the sequencer.
- Find replacement emails for paused contacts; use a skill such as Bounce recovery or Best work email for a person for that.
- Delete contacts or round catch-all and unknown results up to verified.
