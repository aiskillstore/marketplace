---
name: push-to-sequencer
description: "Verifies a prospect list with Leadsets verify_email, segments it into verified, catch-all, unknown and invalid, maps custom fields, and loads the send-safe segments into an Instantly or Smartlead campaign or import-ready CSVs. Use when someone says push to Instantly, load into Smartlead, send this list to my sequencer, or import these leads into a campaign."
license: MIT
metadata:
  title: "Push to Instantly or Smartlead"
  category: "Outreach handoff"
  outcome: "Launch outreach"
  tools: [get_usage, verify_email]
  version: "1.0"
  author: Leadsets
  homepage: https://www.leadsets.ai/skills?utm_source=github&utm_medium=leadsets-skills&utm_campaign=push-to-sequencer
---

# Push to Instantly or Smartlead

Takes a prospect list you already have, verifies every address, and hands Instantly or Smartlead clean, segmented contacts with the custom fields your sequence uses. Built for founders, SDRs and agencies who want catch-alls kept apart from verified contacts and invalid addresses never loaded.

**Category:** Outreach handoff · **Outcome:** Launch outreach · **Tools:** `get_usage`, `verify_email`

## Requirements

- The Leadsets MCP server connected to your agent: `https://mcp.leadsets.ai` ([setup](https://www.leadsets.ai/docs/mcp?utm_source=github&utm_medium=leadsets-skills&utm_campaign=push-to-sequencer)), or a Leadsets API key for the REST API.
- A Leadsets account. The free plan includes 1,000 records, no card ([get a key](https://www.leadsets.ai/signup?utm_source=github&utm_medium=leadsets-skills&utm_campaign=push-to-sequencer)).

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

- "Push this list of 400 leads into my Instantly campaign."
- "Load these contacts into Smartlead with first name, company and first line as custom fields."
- "Verify this CSV and give me files I can import into my sequencer."
- A prospect list or another skill's output is ready and the next step is loading it into an email sequencer.
- "Put the verified ones in the main campaign and the catch-alls somewhere safer."

## What you give it

- **Contact list**: A CSV, Google Sheet, pasted table or the output of another skill. Needs an email column; first name, last name, company and title are strongly recommended. Any extra columns can become custom fields.
- **Sequencer and campaign**: Instantly or Smartlead, plus the campaign name. If the agent has no connection to the sequencer, the default is import-ready CSV files, one per segment.
- **Custom field mapping** (optional): Which list columns map to which sequencer variables, for example first_line to {{first_line}}. Default: first_name, last_name, company_name, title, and any non-empty extra columns passed through under their own names.
- **Catch-all handling** (optional): Default: load catch-alls into a separate campaign or tag them as catch-all so they can be sent at lower volume. Alternatives: hold them out entirely, or put them in the main campaign with a tag.
- **Suppression list** (optional): Optional list of emails or domains that must not be loaded (unsubscribes, customers, existing campaign members). Default: none beyond Leadsets invalid results.

## Steps

1. **Confirm the handoff**
   Read the list and confirm the sequencer, campaign name, field mapping and catch-all handling. Ask one question only if the email column or campaign is unclear. Count rows and note which columns are empty or missing so required variables are flagged before anything is loaded.
2. **Clean the list before spending records**
   Trim and lowercase emails, drop rows with no email or malformed syntax, remove exact duplicates by email, and remove anything matching the suppression list. If the list came from enrich_person earlier in this session with a status attached, keep that status and do not re-verify those rows, since enrich_person emails are already verified. Record every removal with a reason.
3. **Check limits and plan batches** · `get_usage`
   Call get_usage (free). verify_email uses 1 enrichment record per email. Compare the number of emails left to verify against enrichment records left in the five-hour window and the week, or free records left on the Free plan. If the run would cross a window, split it into batches that fit and tell the user when the rest will run, or on a paid plan submit the list as a bulk async verification job and poll for results.
4. **Probe with one address** · `verify_email`
   Call verify_email on a single address from the list. Confirm the response returns a status (verified, catch-all, unknown or invalid) and a confidence score, and that the usage object updates as expected. Stop and report if the call errors with 401, 402 free_records_exhausted or 403.
5. **Verify the rest** · `verify_email`
   Run verify_email on the remaining addresses in the planned batches, or as one async job on a paid plan. Store status, confidence and checked time per row. On 429 window_full wait for Retry-After and resume; on 429 weekly_limit stop and report the resets_at time. Over REST, send an Idempotency-Key per batch so retries never count twice.
6. **Segment and map fields**
   Split rows into four segments: verified (send-safe), catch-all (send at lower volume), unknown (unconfirmed, held back) and invalid (dropped, never loaded). Map columns to sequencer variables and add verification_status and verified_at as custom fields. Flag rows where a variable the sequence uses is empty instead of loading a broken merge.
7. **Load into the sequencer**
   Through the agent's own Instantly or Smartlead connection, add the verified segment to the named campaign with its custom fields, and add catch-alls to a separate campaign or with a catch-all tag per the user's choice. Do not start or schedule the campaign. If there is no connection, write one import-ready CSV per segment. Skip contacts already in the campaign.
8. **Report the run**
   Return a short summary: rows received, removed in cleaning, verified, catch-all, unknown, invalid, loaded per campaign, rows with missing variables, and records used. List any rows that could not be confirmed and why.

## Checks before returning

- No invalid address is loaded anywhere, and unknown addresses are held back unless the user explicitly asks to include them.
- Counts reconcile: rows received equals removed plus verified plus catch-all plus unknown plus invalid, and loaded counts match what the sequencer or CSVs contain.
- No duplicate emails within or across segments, and none that already exist in the target campaign or the suppression list.
- Every loaded contact has a value for each variable the sequence uses; rows with empty required fields are flagged, not silently loaded.
- If verification stopped on a limit, the report says how many rows remain unverified and when the window resets, and those rows are not loaded.

## Output

Contacts loaded into the named Instantly or Smartlead campaign, or CSV files named <campaign>_verified.csv, <campaign>_catch-all.csv, <campaign>_unknown.csv and <campaign>_removed.csv. Columns: email, first_name, last_name, company_name, title, any mapped custom fields (for example first_line), verification_status, confidence, verified_at. Verified goes to the main campaign. Catch-all goes to a separate campaign or is tagged catch-all for lower-volume sending. Unknown is held in its own file as unconfirmed and not loaded by default. Invalid, duplicate and suppressed rows go only to the removed file with a reason column and are never loaded. Plus a plain-text run summary.

## Example

> Here's my sheet of 420 heads of RevOps. Verify them and push them into my Instantly campaign "RevOps Q1" with first_line as a custom field. Keep catch-alls separate.

```
✓ 420 rows  ·  12 duplicates removed  ·  3 suppressed
✓ 2,940 enrichment records left this window  ·  405 to verify
✓ 331 verified  ·  48 catch-all  ·  17 unknown (held)  ·  9 invalid (dropped)
→ 331 loaded to "RevOps Q1"  ·  48 loaded to "RevOps Q1 – catch-all"  ·  4 flagged for empty first_line
```

Illustrative output.

## Cost and limits

verify_email uses 1 enrichment record per email and 1 request per call; it draws on enrichment limits, not search. On Free it uses the 1,000 one-time records shared across search and enrichment. Emails already returned by enrich_person are verified at no extra cost, so the skill reuses those statuses instead of re-verifying. get_usage is free and runs before any verification; the skill sizes batches to the five-hour and weekly enrichment windows, uses a bulk async job on paid plans for large lists, waits on Retry-After for 429 window_full, and uses Idempotency-Keys over REST so retries never count twice. No search records or scrape units are used.

## What it doesn't do

- Start, schedule or send the campaign; it loads contacts and stops, because Leadsets is not a sending tool.
- Find new contacts or replacement emails for invalid or unknown rows; use an enrichment or bounce recovery skill for that.
- Write email copy or first lines; it only passes through fields already in the list.
