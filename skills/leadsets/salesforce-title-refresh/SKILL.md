---
name: salesforce-title-refresh
description: "Refreshes job titles and seniority on Salesforce contacts with Leadsets enrich_person, writes back only confirmed same-company changes, flags people who moved companies, and logs every old and new value with its checked date. Use when someone asks to refresh Salesforce titles, fix stale job titles, update contact seniority, or audit titles before a sequence."
license: MIT
metadata:
  title: "Salesforce title refresh"
  category: "CRM hygiene"
  outcome: "Keep your CRM clean"
  tools: [get_usage, enrich_person]
  version: "1.0"
  author: Leadsets
  homepage: https://www.leadsets.ai/skills?utm_source=github&utm_medium=leadsets-skills&utm_campaign=salesforce-title-refresh
---

# Salesforce title refresh

Re-checks the current title of your Salesforce contacts, updates Title and seniority where they changed, and produces a change log with the old value, new value and the date Leadsets last checked it. Built for RevOps and sales ops teams who want accurate titles for routing, scoring and personalization without hand-editing records.

**Category:** CRM hygiene · **Outcome:** Keep your CRM clean · **Tools:** `get_usage`, `enrich_person`

## Requirements

- The Leadsets MCP server connected to your agent: `https://mcp.leadsets.ai` ([setup](https://www.leadsets.ai/docs/mcp?utm_source=github&utm_medium=leadsets-skills&utm_campaign=salesforce-title-refresh)), or a Leadsets API key for the REST API.
- A Leadsets account. The free plan includes 1,000 records, no card ([get a key](https://www.leadsets.ai/signup?utm_source=github&utm_medium=leadsets-skills&utm_campaign=salesforce-title-refresh)).

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

- "Refresh the titles on our Salesforce contacts."
- "Half our contact titles are out of date, fix them before the Q1 sequence."
- "Update seniority on contacts at our top 200 accounts and log what changed."
- Before routing or scoring rules that depend on title or seniority are run against Salesforce contacts
- After a stale record audit flags contacts with outdated roles

## What you give it

- **Which contacts**: A Salesforce report, list view or plain-language filter (for example "contacts at open opportunity accounts"). Default: contacts whose Title has not been modified in the last 180 days. Each contact needs a work email, a LinkedIn URL, or name plus company.
- **How many** (optional): Maximum contacts to check in this run. Default 500, capped by what get_usage says is left in the enrichment window.
- **Fields to update** (optional): Default: the standard Title field, plus a seniority picklist if the org has one (for example a custom Seniority__c). The user names the field; the skill does not create fields.
- **Write mode** (optional): Default "review first": build the change log, show it, and write only after the user approves. "Auto-write" updates Salesforce directly for confirmed same-company changes.
- **Where the log goes** (optional): Default a CSV named title-refresh-YYYY-MM-DD.csv. Alternatively a Google Sheet. Optionally also stamp a "Title last verified" date field on each updated contact if one exists.

## Steps

1. **Check limits and plan the run** · `get_usage`
   Call get_usage and read enrich records_5h, records_week and resets_at. One contact uses at most one enrichment record. If the contact count exceeds what is left in the five-hour window, plan batches that fit and tell the user how many will run now and when the rest can resume. On the free plan, note that the 1,000 records are one time and shared with search.
2. **Pull and dedupe contacts from Salesforce**
   Through the agent's own Salesforce connection, read Id, FirstName, LastName, Email, Account name and domain, Title, the seniority field if named, and any LinkedIn URL for the contacts in scope. Drop duplicates by Salesforce Id and by email. Set aside contacts with no email, no LinkedIn URL and no company as "insufficient input" without calling Leadsets.
3. **Probe with one contact** · `enrich_person`
   Call enrich_person for a single contact and confirm the response includes current_role with checked_at and the company name and domain. If identifiers are being matched wrongly (wrong person or company), fix the input mapping before spending more records.
4. **Enrich in batches** · `enrich_person`
   Call enrich_person for each remaining contact, with an Idempotency-Key per contact over the REST API so retries never double-count. Read the usage object on each response and stop before the window runs out. On 429 window_full wait for Retry-After and resume; on 429 weekly_limit stop and report resets_at; on 404 not_found record "not found" and move on; on 402 free_records_exhausted stop and ask the user to upgrade.
5. **Classify each result**
   Compare the returned company domain to the Salesforce account domain. Same company and a materially different title: title_change. Treat formatting-only differences ("VP Sales" vs "Vice President, Sales") as no_change. Map the new title to a seniority level (c_level, vp, head, director, manager, ic) and mark seniority_change when it differs. Different company: company_change, which is flagged and never written as a title update. Keep the returned checked_at and confidence on every row.
6. **Write approved changes to Salesforce**
   In review-first mode, show counts and the title_change and seniority_change rows, then wait for approval. Through the agent's Salesforce connection, update only Title and the named seniority field on approved rows. Do not touch Email, Account, owner or any other field. Stamp the "Title last verified" field if the user asked for it.
7. **Write the change log and report**
   Write every contact checked to the log, including no_change, not_found and insufficient input rows, with the action taken. Report totals, records used, anything left for a later window, and the list of company_change contacts so the user can run a job-change or email backfill workflow on them.

## Checks before returning

- No contact whose returned company differs from the Salesforce account had its title overwritten; all of them are flagged as company_change.
- Every written change has a matching log row with the old value, new value, checked_at and Salesforce Id, and the number of Salesforce updates equals the number of updated rows in the log.
- Formatting-only title differences were classified as no_change and not written.
- Enrichment records used stayed inside the window reported by get_usage, and any unprocessed contacts are listed with the time they can resume.
- not_found and insufficient-input contacts are counted and reported, not silently dropped.

## Output

A change log (CSV title-refresh-YYYY-MM-DD.csv, or a Google Sheet with tabs "Updated", "Company changed", "No change" and "Not found") with columns: salesforce_contact_id, full_name, account_name, account_domain, returned_company_domain, old_title, new_title, old_seniority, new_seniority, change_type (title_change, seniority_change, company_change, no_change, not_found, insufficient_input), checked_at, confidence, action (updated, flagged, skipped, pending_approval). Salesforce contacts get updated Title and seniority only for approved same-company changes. The skill does not write emails: any email enrich_person returns is left out of Salesforce, and verified, catch-all, unknown or invalid statuses are not acted on here. Company_change contacts are listed for a separate email backfill or job-change workflow.

## Example

> Refresh titles and seniority on Salesforce contacts at our Tier 1 accounts that haven't been touched since spring. Show me the changes before you write anything.

```
✓ 4,870 enrichment records left this window  ·  ✓ 412 contacts pulled, 9 duplicates removed
✓ 391 enriched  ·  12 not found  ·  0 errors
✓ 63 title changes  ·  21 seniority changes  ·  27 moved companies (flagged, not written)
→ 63 contacts updated in Salesforce after approval  ·  log "title-refresh-2026-11-09.csv" saved
```

Illustrative output.

## Cost and limits

enrich_person uses 1 enrichment record per contact that comes back with data; a not_found result uses no records but still counts as one request. The skill does not call search or scrape tools, so it uses no search records and no scrape units, and get_usage is free. It sizes batches to the rolling five-hour enrichment window (for example 1,000 records on Solo, 15,000 on Pro) and the weekly limit (5,000 on Solo), reads the usage object on every response, waits out 429 window_full using Retry-After, and uses Idempotency-Keys so retries never count twice. On the free plan it draws from the one-time 1,000 records shared with search.

## Edge cases

- **The change log is always saved,** in review-first mode too. It isn't a Salesforce write: save `title-refresh-YYYY-MM-DD.csv` (or the sheet the user names) with every contact checked, before asking for approval to write anything to Salesforce.
- **No seniority field in the read:** use the default `Seniority__c` if the org has it; if the field truly doesn't exist, fill new_seniority in the log only and say the field is missing. Don't stop to ask.

## What it doesn't do

- Overwrite titles for contacts who moved to a different company; it flags them instead of editing the Account or creating new contacts.
- Change, add or verify email addresses, phone numbers or any field other than Title and the named seniority field.
- Create Salesforce fields, reassign owners or start sequences.
