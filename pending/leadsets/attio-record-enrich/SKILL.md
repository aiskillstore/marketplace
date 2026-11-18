---
name: attio-record-enrich
description: "Fills empty fields on Attio people and company records using Leadsets enrich_person and enrich_company, writing only sourced, dated values and never overwriting data without approval. Checks limits first and labels email status honestly. Use when someone says \"enrich my Attio records\", \"fill missing fields in Attio\", \"backfill emails in Attio\" or \"update Attio companies with firmographics\"."
license: MIT
metadata:
  title: "Attio record enrichment"
  category: "CRM hygiene"
  outcome: "Keep your CRM clean"
  tools: [get_usage, enrich_company, enrich_person]
  version: "1.0"
  author: Leadsets
  homepage: https://www.leadsets.ai/skills?utm_source=github&utm_medium=leadsets-skills&utm_campaign=attio-record-enrich
---

# Attio record enrichment

Reads people and company records from Attio, enriches the ones with gaps, and writes back current role, verified work email and firmographics, each with its source and last-checked date. Built for founders and GTM engineers who run Attio as their CRM and want filled records they can trust, not guesses pasted into empty fields.

**Category:** CRM hygiene · **Outcome:** Keep your CRM clean · **Tools:** `get_usage`, `enrich_company`, `enrich_person`

## Requirements

- The Leadsets MCP server connected to your agent: `https://mcp.leadsets.ai` ([setup](https://www.leadsets.ai/docs/mcp?utm_source=github&utm_medium=leadsets-skills&utm_campaign=attio-record-enrich)), or a Leadsets API key for the REST API.
- A Leadsets account. The free plan includes 1,000 records, no card ([get a key](https://www.leadsets.ai/signup?utm_source=github&utm_medium=leadsets-skills&utm_campaign=attio-record-enrich)).

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

- "Enrich the people and companies in my Attio workspace that are missing data."
- "Fill in industry, headcount and location for every company in this Attio list."
- "Find work emails and current titles for Attio contacts that have none."
- New records were imported into Attio from a form, event or spreadsheet and arrived half empty.
- Before a campaign, when reps need Attio records with current roles and verified emails.

## What you give it

- **Which records**: An Attio list, view or filter to work from, for example "Companies in the Q1 target list" or "People added in the last 30 days". Default: records in the chosen object with at least one empty target field.
- **Objects** (optional): People, companies or both. Default: both, companies first so people can be linked to enriched companies.
- **Fields to fill** (optional): Person: current role, company, work email. Company: industry, headcount band, location. Default: all of these, empty fields only.
- **Overwrite policy** (optional): Empty only, or propose changes for fields that already have a value. Default: fill empty fields only and list differing values as proposed changes for the user to approve.
- **Batch size** (optional): How many records to enrich in this run. Default: everything in scope that fits in the remaining enrichment window; the rest is queued for the next window.

## Steps

1. **Read the Attio scope**
   Through your own Attio connection, pull the records in the chosen list, view or filter. For each, note the record ID, the identifiers you can enrich from (person: email, LinkedIn URL, or name plus company domain; company: domain) and which target fields are empty. Drop records with no usable identifier into a skipped list. Confirm the counts with the user and ask one question if the scope or overwrite policy is unclear.
2. **Check limits and plan the run** · `get_usage`
   Call get_usage (free). Read enrichment records left in the five-hour window and the week. Plan one enrichment record per company and per person in scope. If the run would exceed the window, enrich what fits now, tell the user how many records remain and when the window resets. On the free plan, remember the 1,000 records are one time and shared with search.
3. **Probe with one record** · `enrich_company`
   Enrich one company domain (or one person with enrich_person if only people are in scope). Check that the returned fields map cleanly to the Attio attributes, that source and checked_at come back on each field, and that the company match is the right one. Fix the mapping before moving on.
4. **Enrich companies** · `enrich_company`
   Call enrich_company for each company domain in scope. Keep industry, headcount band, location and the source and last-checked date for every field. On 404 not_found, mark the record as no data and move on. On 429 window_full, wait for Retry-After and resume; on weekly_limit, stop and report resets_at. Read the usage object on responses to pace the run.
5. **Enrich people** · `enrich_person`
   Call enrich_person for each person in scope, using the strongest identifier available. Keep current role, company, work email and its status (verified, catch-all, unknown), confidence and checked_at. Flag people whose returned company differs from the Attio company as possible job changes rather than silently moving them. Emails from enrich_person are already verified, so do not call verify_email on them.
6. **Write back to Attio**
   Through your Attio connection, write values only into empty fields, per the overwrite policy. Write verified emails to the email attribute. Do not write catch-all or unknown emails to the primary email attribute; record them in a note or a separate attribute with their label. Store the Leadsets source and checked_at date with each written field, for example in a note or dedicated attributes. Collect fields with differing existing values as proposed changes, not writes.
7. **Report the run**
   Return a summary: records read, enriched, fields filled per object, verified emails written, catch-all and unknown held back, possible job changes, no-data and skipped records, proposed changes awaiting approval, and records queued for the next window with the reset time.

## Checks before returning

- Every value written to Attio carries a Leadsets source and last-checked date, and no existing value was overwritten without approval.
- Only verified emails went into the primary email attribute; catch-all and unknown are labelled separately and invalid never appears.
- Each Attio record was enriched once in this run: deduplicate by record ID, domain and email before calling the tools.
- Usage after the run matches the plan from get_usage, and any records left over are listed with the window reset time.
- Records returning 404 not_found or lacking an identifier are reported, not retried in a loop.

## Output

Updated Attio records plus a run report with four sections: Filled (record ID, object, field, new value, source, checked_at), Proposed changes (record ID, field, current Attio value, Leadsets value, checked_at), Email held back (record ID, email, status catch-all or unknown, confidence; catch-all can be sent at lower volume, unknown is unconfirmed), and Not enriched (record ID, reason: no identifier, not_found, possible job change, or queued for next window). Invalid emails are never returned by Leadsets as contact emails and are never written. Optionally export the report as CSV.

## Example

> Fill in the empty fields on everyone in my Attio "Q1 targets" list, people and companies. Don't overwrite anything that's already there.

```
✓ 412 people · 96 companies read  ·  ✓ 4,880 enrichment records left this window
✓ 91 companies enriched  ·  ✓ 377 people enriched  ·  35 not found
✓ 288 verified emails written  ·  41 catch-all, 12 unknown held back  ·  19 possible job changes
→ Attio updated: 1,146 fields filled with source and date, 23 proposed changes awaiting approval
```

Illustrative output.

## Cost and limits

enrich_person and enrich_company use 1 enrichment record per record returned; a 404 not_found or other empty result uses no records but still counts as one request. Emails from enrich_person are already verified at no extra cost, so the skill does not call verify_email. Enrichment limits per five hours are 1k on Solo, 15k on Pro, 150k on Team and 225k on Max, with weekly caps of 5k, 75k, 750k and 1.125M; free accounts have 1,000 one-time records shared with search. The skill calls get_usage first (free), sizes the run to what is left, reads the usage object as it goes, waits out 429 window_full with Retry-After, and queues the remainder for the next window instead of stalling halfway. No scrape units are used.

## What it doesn't do

- Overwrite existing Attio values, merge records or delete anything without the user's approval.
- Write catch-all or unknown emails as if they were verified, or add phone numbers (Leadsets does not offer them).
- Search for new people or companies to add to Attio; it only enriches records that already exist.
