---
name: catch-all-segmenter
description: "Verifies a contact list with verify_email and splits catch-all domains into their own segment, grouped by domain, so they can be warmed at lower volume instead of dropped. Keeps verified, unknown and invalid separate and never counts catch-all as valid. Use when someone asks to segment catch-alls, split risky emails, handle accept-all domains or prepare a list for a slower warm-up send."
license: MIT
metadata:
  title: "Catch-all segmenter"
  category: "Email verification"
  outcome: "Get verified contact data"
  tools: [get_usage, verify_email]
  version: "1.0"
  author: Leadsets
  homepage: https://www.leadsets.ai/skills?utm_source=github&utm_medium=leadsets-skills&utm_campaign=catch-all-segmenter
---

# Catch-all segmenter

Takes a list of emails, verifies every address, and returns four clean segments with catch-all contacts grouped by domain for a separate, lower-volume send. Built for founders, SDRs and GTM engineers who want to keep reachable catch-all contacts instead of throwing them away or mixing them into the main campaign.

**Category:** Email verification · **Outcome:** Get verified contact data · **Tools:** `get_usage`, `verify_email`

## Requirements

- The Leadsets MCP server connected to your agent: `https://mcp.leadsets.ai` ([setup](https://www.leadsets.ai/docs/mcp?utm_source=github&utm_medium=leadsets-skills&utm_campaign=catch-all-segmenter)), or a Leadsets API key for the REST API.
- A Leadsets account. The free plan includes 1,000 records, no card ([get a key](https://www.leadsets.ai/signup?utm_source=github&utm_medium=leadsets-skills&utm_campaign=catch-all-segmenter)).

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

- "Separate the catch-alls in this list so I can send to them slowly."
- "Which of these emails are on accept-all domains? Don't drop them, just split them out."
- A list is about to go into a sequencer and the user wants catch-all addresses in their own campaign or tab.
- A previous verification run mixed catch-all and verified results and needs to be re-segmented by domain.
- "Group my catch-all contacts by company domain so I can warm each domain gradually."

## What you give it

- **Email list**: A CSV, Google Sheet, CRM view or pasted list with at least an email column. Name, company and domain columns are kept if present. Default: the list the user just shared or built in this conversation.
- **Re-verify existing statuses** (optional): Whether to re-check addresses that already carry a verification status and a recent checked_at date. Default: re-verify only rows with no status or a status older than 30 days.
- **Where it goes** (optional): CSV files, separate Google Sheets tabs, or segments handed to the user's sequencer (Instantly, Smartlead, LinkedCamp) through the agent's own connection. Default: one file or sheet with four tabs.

## Steps

1. **Clean and dedupe the input**
   Read the list, trim whitespace, lowercase every email and drop exact duplicates and rows with no email. Extract the domain from each address. Report the count before and after dedupe so the user knows how many verifications the run will need. Do not call any tool on duplicates.
2. **Check remaining limits and plan the run** · `get_usage`
   Call get_usage (free). verify_email counts toward enrichment, 1 per email. Compare the deduped count with enrichment records left in the five-hour window and the week, or free records left on the Free plan. If the list would cross a window, tell the user and either split it into batches that fit or, on a paid plan, submit it as an async bulk job and poll jobs/{id}.
3. **Probe with one address** · `verify_email`
   Call verify_email on a single address from the list. Confirm the response returns a status (verified, catch-all, unknown or invalid), a confidence score and checked_at. If it returns 401 or 403 stop and tell the user to check the connection; if 402 free_records_exhausted, stop and ask the user to upgrade.
4. **Verify the full list in batches** · `verify_email`
   Send the remaining addresses in batches sized to the limits from get_usage, with an Idempotency-Key on each batch so retries never double-count. Read the usage object on every response and pause before a window fills. On 429 window_full or too_many_concurrent, wait Retry-After seconds and retry with the same key; on 429 weekly_limit, stop and report how many are left and when resets_at falls.
5. **Segment by status and group catch-alls by domain**
   Split results into four segments: verified, catch-all, unknown, invalid. Never move catch-all or unknown into verified. Within catch-all, group rows by domain and count contacts per domain, sorted by count descending, so the user can warm one domain at a time. Flag any domain where some addresses came back verified and others catch-all.
6. **Write the output and report**
   Write the four segments to the chosen destination through the agent's own connection to that system (CSV files, Sheets tabs or sequencer campaigns). Keep invalid rows out of any send segment. Return a short summary with counts per status, number of catch-all domains, records used and anything that could not be verified.

## Checks before returning

- Every input email appears in exactly one segment, and the segment counts add up to the deduped total.
- No catch-all or unknown address is labelled or exported as verified, and no invalid address is in a send-ready segment.
- Duplicates were removed before verification, so no address was verified twice in the run.
- Records used match the usage objects returned, and the run stopped cleanly with a remaining count if a 429 weekly_limit or 402 was hit.
- If the list was empty after cleaning or every row failed, say so plainly instead of returning empty tabs.

## Output

Four segments, as tabs in one sheet or four CSV files named Verified, Catch-all, Unknown and Invalid. Columns on every row: email, first_name, last_name, company, domain, status, confidence, checked_at, plus any original columns. The Catch-all segment adds catch_all_domain_count and is sorted by domain, with a short domain summary (domain, contacts) at the top or in a fifth tab named Catch-all domains. Verified is send-ready. Catch-all is kept for a separate, lower-volume send. Unknown is marked unconfirmed and not added to any campaign by default. Invalid is listed for removal or suppression and never pushed to a sequencer.

## Example

> Here's my Parcelry outbound list, 640 emails. Split out the catch-alls by domain so I can warm them slowly in a separate Smartlead campaign, and give me the rest as tabs in a Google Sheet.

```
✓ 640 rows · 612 unique emails  ·  ✓ 4,380 enrichment records left this window
✓ 612 verified with verify_email
✓ 431 verified  ·  118 catch-all across 47 domains  ·  39 unknown  ·  24 invalid
→ Sheet "Parcelry list – segmented" created, 5 tabs; catch-all segment exported as CSV for Smartlead
```

Illustrative output.

## Cost and limits

Each address checked with verify_email uses 1 record from the enrichment limit (Solo 1k per 5 hours and 5k per week, Pro 15k and 75k, Team 150k and 750k, Max 225k and 1.125M), or from the 1,000 one-time free records on Free. Every call also counts as a request, but the request limit is five times the record allowance. get_usage is free and runs first. The skill dedupes before verifying, sizes batches to what is left, sends Idempotency-Keys so retries never double-count, waits out 429 Retry-After times, and on paid plans can run large lists as an async bulk job. No search records or scrape units are used.

## What it doesn't do

- Does not find replacement emails or new contacts for catch-all, unknown or invalid addresses; use an enrichment skill for that.
- Does not set send volumes, schedules or warm-up rules in the sequencer; it hands over the segments and the user decides the pace.
- Does not send email or treat a catch-all result as proof a mailbox exists.
