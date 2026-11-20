---
name: pipedrive-lead-enrich
description: "Enriches new Pipedrive leads with current role, company firmographics and a verified work email using Leadsets enrich_person and enrich_company, then writes the results back through the agent's Pipedrive connection with status labels. Use when someone says \"enrich my new Pipedrive leads\", \"fill missing emails in Pipedrive\" or \"add titles and company data to Pipedrive leads\"."
license: MIT
metadata:
  title: "Pipedrive lead enrichment"
  category: "CRM hygiene"
  outcome: "Keep your CRM clean"
  tools: [get_usage, enrich_person, enrich_company]
  version: "1.0"
  author: Leadsets
  homepage: https://www.leadsets.ai/skills?utm_source=github&utm_medium=leadsets-skills&utm_campaign=pipedrive-lead-enrich
---

# Pipedrive lead enrichment

Takes the leads that landed in Pipedrive with thin data and fills in current role, company firmographics and a verified work email, with the source and checked date on every field. Built for founders and RevOps people who want new leads ready to work without copying data in by hand.

**Category:** CRM hygiene · **Outcome:** Keep your CRM clean · **Tools:** `get_usage`, `enrich_person`, `enrich_company`

## Requirements

- The Leadsets MCP server connected to your agent: `https://mcp.leadsets.ai` ([setup](https://www.leadsets.ai/docs/mcp?utm_source=github&utm_medium=leadsets-skills&utm_campaign=pipedrive-lead-enrich)), or a Leadsets API key for the REST API.
- A Leadsets account. The free plan includes 1,000 records, no card ([get a key](https://www.leadsets.ai/signup?utm_source=github&utm_medium=leadsets-skills&utm_campaign=pipedrive-lead-enrich)).

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

- "Enrich the leads we added to Pipedrive this week."
- "Our Pipedrive leads are missing emails and titles. Fill them in."
- "Add industry, headcount and location to the organizations behind our new leads."
- New inbound or event leads were imported into Pipedrive with only a name and company.
- Before a rep starts a sequence on Pipedrive leads that have never been checked.

## What you give it

- **Which leads** (optional): A Pipedrive filter, view, label or date range. Default: leads created in the last 7 days that are missing an email, a job title or organization details.
- **Overwrite policy** (optional): Whether to replace existing values or only fill empty fields. Default: fill empty fields only, and list any conflicting values for review instead of overwriting.
- **Field mapping** (optional): Which Pipedrive fields receive title, email, email status, industry, headcount band and location. Default: standard person and organization fields, plus custom fields for email status and last-checked date if they exist; otherwise the details go in a note.
- **Catch-all handling** (optional): Whether catch-all emails are written to the lead. Default: write them with an email status of catch-all so reps send at lower volume; never mark them verified.

## Steps

1. **Pull the leads and plan the work**
   Read the selected leads through the agent's own Pipedrive connection. For each lead collect name, organization name, organization domain, any profile URL and any existing email or title. Skip leads that already have every target field filled. Deduplicate people by email or name plus domain, and build a list of unique organization domains so each company is enriched once. If no lead has a usable name plus company or domain, stop and say so.
2. **Check remaining limits** · `get_usage`
   Call get_usage (free). Needed enrichment records are at most the number of leads to enrich plus the number of unique domains. Compare that with enrichment records left in the five-hour window and the week. If the run would cross a window, tell the user, process what fits now and queue the rest for after resets_at. If the account is on Free, note that the 1,000 one-time records are shared with search and do not refill.
3. **Probe with one lead** · `enrich_person`
   Call enrich_person for a single lead with the richest input (profile URL if present, otherwise name plus company domain). Confirm the returned person is the same person and the company matches the Pipedrive organization before running the batch. If the match looks wrong, adjust which inputs are sent and probe again rather than spending records on the whole list.
4. **Enrich each person** · `enrich_person`
   Call enrich_person for each remaining lead, sending an Idempotency-Key per lead so retries never count twice. Keep current role, company, work email, email status, confidence and checked dates. On 404 not_found, mark the lead no match and move on. On 429 window_full, wait for Retry-After and retry with the same key. On 402 free_records_exhausted, stop and ask the user to upgrade. Read the usage object on each response and pause before a window fills.
5. **Enrich each organization once** · `enrich_company`
   Call enrich_company once per unique domain, including domains from the company enrich_person returned when the Pipedrive organization had none. Keep industry, headcount band, location and the source and freshness of each field. Handle 404 and 429 the same way as the person step.
6. **Reconcile before writing**
   Compare returned data with what Pipedrive holds. If enrich_person shows the person now works at a different company, flag the lead as a possible job change instead of writing the new company over the old one. Apply email rules: verified is written as the email; catch-all is written only with its catch-all status; unknown is not written as the email and is listed as unconfirmed; invalid is never served and the lead is marked no email. Under the default policy, collect conflicts with existing values into a review list.
7. **Write back to Pipedrive and report**
   Through the agent's Pipedrive connection, update the person and organization fields per the mapping, set email status, and add a note with the Leadsets source and checked date for each written field. Do not create new leads, deals or organizations unless the user asked. Return a run summary with counts by outcome and the review list.

## Checks before returning

- Every written email carries its status; no catch-all or unknown address is labelled verified, and no invalid address is written.
- Each organization domain was enriched once, and no lead was enriched twice in the run.
- No existing Pipedrive value was overwritten without the user's permission; conflicts and possible job changes are listed for review.
- Records used match the get_usage plan, and any leads left over from a full window are queued with the reset time rather than silently dropped.
- Leads with no match or no email are reported by name, not hidden from the summary.

## Output

Updated Pipedrive leads plus a run summary. Per lead: name, Pipedrive lead link, title (current role), organization, domain, work email, email status (verified, catch-all, unknown or invalid), confidence, industry, headcount band, location, last-checked date, and outcome (updated, partly updated, no match, no email, possible job change, conflict). Verified emails are written as the email. Catch-all emails are written with a catch-all status so reps send at lower volume. Unknown emails are not written as the email and are listed as unconfirmed. Invalid emails are never written; those leads are marked no email. A review list covers conflicts with existing values and possible job changes. If the user asks, the same table is also exported as CSV.

## Example

> Enrich the 60 leads we added to Pipedrive this week. Fill in title, verified email and company details, but don't overwrite anything a rep already entered.

```
✓ 60 leads pulled  ·  ✓ 2,840 enrichment records left this window
✓ 54 people enriched  ·  ✓ 41 organizations enriched  ·  6 no match
✓ 44 verified  ·  6 catch-all (labelled)  ·  4 unknown or no email
→ 54 Pipedrive leads updated  ·  3 possible job changes and 5 conflicts in review list
```

Illustrative output.

## Cost and limits

Each enrich_person call that returns data uses 1 enrichment record, and each enrich_company call that returns data uses 1 enrichment record. Emails from enrich_person are already verified, so there is no separate verify_email charge. No match (404) and empty results use no records but count as one request; the request limit is five times the record allowance, so normal retries are safe. The skill uses no search records and no scrape units. On Solo that is 1,000 enrichment records per five hours and 5,000 per week; Free has 1,000 one-time records shared with search. The skill calls get_usage first, enriches each organization only once, sends Idempotency-Keys so retries never double-count, waits on 429 Retry-After, and splits runs that would cross a window.

## What it doesn't do

- Create or delete Pipedrive leads, deals or organizations, or overwrite rep-entered values without permission.
- Send email or add leads to sequences; it only fills data for the tools that send.
- Return phone numbers, which Leadsets does not offer.
