---
name: enrich-from-linkedin
description: "Enriches one LinkedIn profile URL or a batch of them with Leadsets enrich_person, returning current role, company and a work email labelled verified, catch-all or unknown, with confidence and checked dates. Checks limits first and segments uncertain emails. Use when someone says \"enrich this LinkedIn URL\", \"get the email for this profile\" or \"find work emails for these LinkedIn links\"."
license: MIT
metadata:
  title: "Enrich a contact from a LinkedIn URL"
  category: "Enrichment"
  outcome: "Get verified contact data"
  tools: [get_usage, enrich_person]
  version: "1.0"
  author: Leadsets
  homepage: https://www.leadsets.ai/skills?utm_source=github&utm_medium=leadsets-skills&utm_campaign=enrich-from-linkedin
---

# Enrich a contact from a LinkedIn URL

Turns LinkedIn profile URLs into contact records: current role, company, domain and a work email with an honest verification label. Built for founders, SDRs and GTM engineers who have a profile, or a column of profiles, and need someone they can actually email.

**Category:** Enrichment · **Outcome:** Get verified contact data · **Tools:** `get_usage`, `enrich_person`

## Requirements

- The Leadsets MCP server connected to your agent: `https://mcp.leadsets.ai` ([setup](https://www.leadsets.ai/docs/mcp?utm_source=github&utm_medium=leadsets-skills&utm_campaign=enrich-from-linkedin)), or a Leadsets API key for the REST API.
- A Leadsets account. The free plan includes 1,000 records, no card ([get a key](https://www.leadsets.ai/signup?utm_source=github&utm_medium=leadsets-skills&utm_campaign=enrich-from-linkedin)).

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

- "What's the work email for linkedin.com/in/...?"
- "Enrich these 200 LinkedIn URLs and put the results in a sheet."
- A CSV or Google Sheet has a LinkedIn URL column but no emails or current titles.
- Checking that a saved profile still works at the same company before reaching out.
- Preparing a short list of profiles from an event or a referral for a sequencer.

## What you give it

- **LinkedIn URLs**: One profile URL pasted in chat, a list, or a CSV or Google Sheet column. The skill normalises and dedupes URLs before spending anything.
- **Where results go** (optional): Default: a table in chat for up to 25 profiles, a CSV for larger batches. Google Sheets if the agent has a connection to it.
- **Email policy** (optional): Default: verified emails in the main list, catch-all in a separate segment, unknown marked unconfirmed. Ask the user only if they want catch-alls dropped.
- **Batch cap** (optional): Maximum profiles to enrich this run. Default: all unique URLs, capped at what get_usage says is left in the enrichment window.

## Steps

1. **Clean the input**
   Collect every URL, trim tracking parameters and trailing slashes, drop exact duplicates and anything that is not a personal profile URL (company pages, posts, search links). Report how many unique profile URLs remain and list the rejected ones.
2. **Check remaining limits** · `get_usage`
   Call get_usage (free). Read enrichment records left in the five-hour window and the week, or free records left on the Free plan. If the batch is larger than what is left, tell the user, enrich up to the remaining amount and note when the window resets. Do not start a run you know will stall halfway without saying so.
3. **Probe with one profile** · `enrich_person`
   Call enrich_person on the first URL only. Confirm the response has current role, company and an email status, and that the usage object decreased by one record. If it returns 401 or 403, stop and tell the user the connection or key needs fixing.
4. **Enrich the batch** · `enrich_person`
   Call enrich_person once per remaining URL, in batches sized to the remaining allowance. Over REST, send an Idempotency-Key per URL so retries never count twice. On 404 not_found, record the URL as not found and move on. On 429 window_full, wait the Retry-After seconds and resume. On 429 weekly_limit, stop and report resets_at. On 402 free_records_exhausted, stop and ask the user to upgrade. Read the usage object on each response to pace the run.
5. **Sort by email status**
   Use the status enrich_person returns; do not call verify_email again, since enrichment emails are already verified. Put verified emails in the main list, catch-all in a separate segment, unknown in an unconfirmed segment. Invalid emails are never served, so treat those people as no email. Flag anyone whose current company differs from what the user's sheet says.
6. **Write the output**
   Return a chat table for small runs, or write a CSV or Google Sheet through the agent's own connection with Verified, Catch-all, Unconfirmed and No email tabs. End with a run summary: URLs in, enriched, verified, catch-all, unknown, no email, not found, and records used.

## Checks before returning

- Every input URL appears exactly once in the output, either enriched, not found or rejected, with no duplicate people across tabs.
- No catch-all or unknown email sits in the verified list, and no email is labelled valid that Leadsets did not label verified.
- Records used matches the enriched count from the usage objects, and not-found URLs show zero records.
- If the run stopped on a limit, the summary says how many URLs are left and when the window resets.
- Each row keeps the checked_at date so stale facts can be spotted later.

## Output

One row per unique input URL with columns: linkedin_url, full_name, current_title, company_name, company_domain, work_email, email_status (verified, catch-all, unknown, none), confidence, checked_at, company_changed (yes/no if the input had a company), result (enriched, not_found, rejected_url). Tabs or sections: Verified (send), Catch-all (send at lower volume), Unconfirmed (unknown, do not send without review), No email (invalid or none found, email left blank), Not found. Invalid addresses are never written into work_email.

## Example

> Here are 60 LinkedIn URLs from the RevOps meetup last week. Get their current titles and work emails and put them in a CSV I can load into Instantly.

```
✓ 60 URLs in · 57 unique profiles · 3 rejected (company pages)
✓ 4,812 enrichment records left this window
✓ 53 enriched · 4 not found (0 records used)
✓ 41 verified · 7 catch-all · 3 unknown · 2 no email
→ "revops-meetup-enriched.csv" written, catch-all and unconfirmed in separate files
```

Illustrative output.

## Cost and limits

enrich_person uses 1 enrichment record per profile returned with data; a not-found result uses 0 records and 1 request. Emails from enrich_person are already verified, so there is no verify_email charge. get_usage is free. Free plan: 1,000 one-time records shared across search and enrichment. Solo allows 1,000 enrichment records per five hours and 5,000 per week, Pro 15,000 and 75,000. The skill checks get_usage first, caps the batch at what is left, and resumes after Retry-After on a 429; blocked calls count against nothing.

## What it doesn't do

- Scrape LinkedIn or any page behind a login; it only sends the URL to enrich_person and uses Leadsets data.
- Guess emails from name patterns or promote catch-all and unknown addresses to verified.
- Return phone numbers, which Leadsets does not offer.
