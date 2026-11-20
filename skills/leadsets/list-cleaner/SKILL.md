---
name: list-cleaner
description: "Verifies every address on an email list with Leadsets verify_email and returns four segments: send-safe (verified), catch-all, unknown and invalid, each with a confidence score and checked date. Dedupes first and plans the run against limits. Use when someone says \"clean this list before I send\", \"verify these emails\", \"check this CSV for bounces\" or \"flag catch-alls separately\"."
license: MIT
metadata:
  title: "Clean a list before sending"
  category: "Email verification"
  outcome: "Get verified contact data"
  tools: [get_usage, verify_email]
  version: "1.0"
  author: Leadsets
  homepage: https://www.leadsets.ai/skills?utm_source=github&utm_medium=leadsets-skills&utm_campaign=list-cleaner
---

# Clean a list before sending

Takes a list of email addresses from a CSV, a Google Sheet or a pasted column and verifies every one through the Leadsets verification waterfall. It returns the list split into send-safe, catch-all, unknown and invalid segments, so founders, SDRs and GTM engineers can protect their sending domain before a campaign goes out.

**Category:** Email verification · **Outcome:** Get verified contact data · **Tools:** `get_usage`, `verify_email`

## Requirements

- The Leadsets MCP server connected to your agent: `https://mcp.leadsets.ai` ([setup](https://www.leadsets.ai/docs/mcp?utm_source=github&utm_medium=leadsets-skills&utm_campaign=list-cleaner)), or a Leadsets API key for the REST API.
- A Leadsets account. The free plan includes 1,000 records, no card ([get a key](https://www.leadsets.ai/signup?utm_source=github&utm_medium=leadsets-skills&utm_campaign=list-cleaner)).

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

- "Clean this list of 800 emails before I send. Flag catch-alls separately."
- Before loading a purchased, event or older list into Instantly, Smartlead, LinkedCamp or any sequencer
- A list has started bouncing and the user wants to know which addresses are still good
- "Verify the emails in this Google Sheet and tell me which ones are safe to send to."
- Someone hands over a CSV of contacts with no verification status or with statuses that are months old

## What you give it

- **The list**: A CSV or Excel file, a Google Sheet, or pasted addresses. The agent finds the email column; if there are several, it asks which one to verify.
- **Where results go** (optional): Default: the same format the list arrived in, with one tab or file per segment. Also CSV, Google Sheets, or a summary in chat for short lists.
- **Catch-all policy** (optional): Default: keep catch-alls in their own segment to send at lower volume. The user can ask to exclude them entirely instead.
- **Keep original columns** (optional): Default: yes. Every original column is carried through next to the verification fields, so the list can be re-imported without remapping.

## Steps

1. **Read and prepare the list**
   Load the list through your connection to the file or sheet. Trim whitespace and lowercase each address, remove exact duplicates, and set aside rows with an empty email cell or a value with no @ sign. Count unique addresses to verify and report the count of duplicates and unusable rows before spending anything.
2. **Check limits and plan the run** · `get_usage`
   Call get_usage (free). Standalone verify_email counts toward the enrichment meter, 1 per email. Compare unique addresses against enrichment records left in this five-hour window and this week, or free records left on the Free plan. If the list fits, run it in one pass. If not, tell the user how many fit now, split the rest into batches per window, and ask before continuing. On Free, if the list exceeds the remaining free records, say so and offer to verify a subset.
3. **Probe with one address** · `verify_email`
   Call verify_email on a single address from the list. Confirm the response returns a status (verified, catch-all, unknown or invalid), a confidence score and a checked date, and that the usage object updated as expected. If you get 401 or 403, stop and tell the user the connection or key needs attention. If you get 402 free_records_exhausted, stop and tell the user free records are gone and a paid plan is needed.
4. **Verify every address** · `verify_email`
   Verify the remaining addresses. On a paid plan, submit large lists as a bulk job (upload or POST the list, get an async job ID, pull results when ready). Otherwise call verify_email in batches and read the usage object after each batch. On 429 window_full or too_many_concurrent, wait for Retry-After and retry; on 429 weekly_limit, pause and report when it resets. When calling REST, send an Idempotency-Key on each batch so a retry never counts twice. Retry 500 and 503 with backoff; do not retry 400.
5. **Segment the results**
   Join results back to the original rows by email. Put verified in send-safe, catch-all in its own segment marked send at lower volume, unknown in its own segment marked unconfirmed, and invalid in a do-not-send segment. Never move unknown or catch-all into send-safe. Put duplicate and unusable rows in a skipped segment with the reason.
6. **Deliver and report**
   Write the segments through your connection to the destination (separate tabs in a sheet, or separate CSV files). Report counts per segment, records used, anything left unverified because of limits, and when the remainder can run. If the user plans to send, note that catch-alls should go out at lower volume and unknowns should be held or re-checked later.

## Checks before returning

- Every unique address has exactly one status from verified, catch-all, unknown or invalid, or is listed as not yet verified with the reason
- No catch-all, unknown or invalid address appears in the send-safe segment
- Segment counts plus skipped rows add up to the original row count
- Duplicates were removed before verifying, so no address was paid for twice
- If limits stopped the run, the report says how many remain and when the window resets, rather than implying the list is complete

## Output

One tab or file per segment, named "<list name> – send-safe", "– catch-all", "– unknown", "– invalid" and "– skipped". Each row keeps all original columns plus email_status, confidence and checked_at. Send-safe holds verified addresses only. Catch-all holds addresses on domains that accept everything, marked to send at lower volume. Unknown holds addresses where the server gave no clear answer, marked unconfirmed and not for sending yet. Invalid holds addresses that bounce, marked do not send. Skipped holds duplicates and rows with no usable email, with a reason column. A short summary with counts and records used is returned in chat.

## Example

> Here's our webinar sign-up export, about 800 emails. Clean it before I load it into Instantly and put catch-alls on a separate tab.

```
✓ 812 rows read  ·  27 duplicates  ·  6 no email  ·  779 to verify
✓ 13,212 enrichment records left this window, run fits in one pass
✓ 604 verified  ·  91 catch-all  ·  38 unknown  ·  46 invalid
→ Sheet "Webinar list – cleaned" created, 5 tabs (send-safe, catch-all, unknown, invalid, skipped)
```

Illustrative output.

## Cost and limits

Each standalone verify_email uses 1 record per email and counts toward the enrichment limit (Solo 1k per five hours and 5k per week, Pro 15k and 75k, Team 150k and 750k, Max 225k and 1.125M). On Free it draws from the 1,000 one-time records shared across search and enrichment. Every call counts as one request, but the request limit is five times the record allowance, so retries do not hit it. Errors and blocked 429 calls use no records. get_usage is free and runs first, and deduping before verifying avoids paying twice for the same address. Lists larger than the remaining window are split across windows or submitted as a bulk async job on paid plans. No scrape units are used.

## What it doesn't do

- Find replacement emails for invalid or unknown addresses; use the Bounce recovery or Best work email skills for that
- Send email or push contacts into a sequencer; it hands back segmented lists for the user's own tools
- Report catch-all or unknown addresses as valid, or delete any rows from the user's original file
