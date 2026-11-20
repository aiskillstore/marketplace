---
name: dedupe-merge
description: "Merges several prospect or contact lists into one clean list, resolving duplicates by person and by company. Matches on email, profile URL and name plus domain, then uses enrich_person only on ambiguous rows to confirm current role and company. Use when someone says merge these lists, dedupe my CSVs, combine event and CRM exports, or remove duplicates before sending."
license: MIT
metadata:
  title: "Dedupe and merge lists"
  category: "List building"
  outcome: "Keep your CRM clean"
  tools: [get_usage, enrich_person]
  version: "1.0"
  author: Leadsets
  homepage: https://www.leadsets.ai/skills?utm_source=github&utm_medium=leadsets-skills&utm_campaign=dedupe-merge
---

# Dedupe and merge lists

Takes two or more lists (CSVs, sheet tabs or CRM exports), collapses duplicate people and companies into single rows, and keeps a record of which source each row came from. Built for GTM engineers, agencies and founders who pull contacts from several places and need one list without double-sends or conflicting titles.

**Category:** List building · **Outcome:** Keep your CRM clean · **Tools:** `get_usage`, `enrich_person`

## Requirements

- The Leadsets MCP server connected to your agent: `https://mcp.leadsets.ai` ([setup](https://www.leadsets.ai/docs/mcp?utm_source=github&utm_medium=leadsets-skills&utm_campaign=dedupe-merge)), or a Leadsets API key for the REST API.
- A Leadsets account. The free plan includes 1,000 records, no card ([get a key](https://www.leadsets.ai/signup?utm_source=github&utm_medium=leadsets-skills&utm_campaign=dedupe-merge)).

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

- "Merge these three CSVs into one list and remove duplicates."
- Combining webinar sign-ups, event attendees and a CRM export before a campaign.
- An agency consolidating lists built for the same client across several runs.
- "Some of these people appear twice with different titles. Which one is right?"
- Before pushing a list to a sequencer, to make sure no one is contacted twice.

## What you give it

- **Lists to merge**: Two or more CSV files, Google Sheets tabs or CRM exports. Columns can differ; the skill maps them. Each row keeps a source tag naming the list it came from.
- **Match rules** (optional): How duplicates are detected. Default order: exact work email, then profile URL, then normalized full name plus company domain. Companies match on root domain. The user can add or drop rules.
- **Resolve ambiguous rows** (optional): Whether to call enrich_person on rows that cannot be resolved locally (same name at different companies, conflicting titles, missing email). Default yes, capped at 200 rows per run unless the user raises it.
- **Where it goes** (optional): CSV, Google Sheets or a CRM the agent is connected to. Default: one CSV plus a review file.

## Steps

1. **Load and normalize every list**
   Read each list through the agent's own file, sheet or CRM connection. Map columns to a common shape: full_name, title, company_name, company_domain, work_email, profile_url, source_list. Lowercase and trim emails, reduce company websites to root domains (northwind.co, not www.northwind.co/about), strip honorifics and extra whitespace from names. Report row counts per list before moving on.
2. **Dedupe locally first**
   Apply the match rules in order: exact email, then profile URL, then normalized name plus company domain. Group matching rows into clusters and merge clusters that share any key. Group companies by root domain. This step spends nothing. Set aside as ambiguous: clusters with conflicting titles or companies, same name at different domains, and rows with no email and no profile URL.
3. **Check limits and plan enrichment** · `get_usage`
   Call get_usage. Compare the number of ambiguous rows (capped by the input default) with enrichment records left in the five-hour window and the week. On the free plan, remember the 1,000 records are shared and do not refill. If the batch would cross a window, tell the user and either split it across windows or resolve the highest-value rows first.
4. **Probe with one record** · `enrich_person`
   Call enrich_person on a single ambiguous row. Confirm the response returns current role, company and an email status, and that the fields line up with the column mapping. If the input format is wrong for the tool, fix the mapping before running the batch.
5. **Resolve ambiguous rows** · `enrich_person`
   Call enrich_person for each remaining ambiguous row, sending an Idempotency-Key on every call. Use the returned current role and company to decide whether two rows are the same person (one moved jobs) or two different people. On 404 not_found, keep the row unresolved and move on. On 429 window_full or weekly_limit, wait for Retry-After or stop and report progress. On 402 free_records_exhausted, stop and ask the user to upgrade. Do not retry 400 errors as is.
6. **Pick survivor values**
   For each merged person, keep one row. Prefer values returned by enrich_person (they carry checked_at dates) over unsourced input values, then the most recently updated source. Never silently overwrite: when titles, companies or emails disagree, keep the losing values in a conflicts column. Keep every source_list tag joined in one field so the user can see where the person appeared.
7. **Write the merged list and report**
   Write the output to the chosen destination through the agent's own connection. Return a short summary: rows in, unique people out, unique companies, duplicates merged, rows resolved by enrichment, rows left for review.

## Checks before returning

- Row accounting adds up: rows in equals unique rows out plus rows merged away, with nothing dropped silently.
- No email address appears on more than one row in the merged list, and no person appears twice under different emails without a flag.
- Email statuses from enrich_person are carried through as returned; catch-all and unknown are never relabelled verified, and invalid addresses are never kept as the contact email.
- Enrichment stayed within the planned cap and the limits reported by get_usage; any rows skipped for limits are listed, not dropped.
- If no duplicates were found, say so plainly and still return the normalized merged list.

## Output

Main file or tab "Merged": one row per person with full_name, title, company_name, company_domain, work_email, email_status, profile_url, source_lists, merged_from_count, resolved_by (local or enrich_person), checked_at, conflicts. A second file or tab "Companies": one row per root domain with company_name, contact_count and source_lists. A third "Review": ambiguous rows that could not be resolved, with the reason. email_status uses the Leadsets label when enrich_person returned one: verified stays in Merged; catch-all and unknown stay in Merged but are labelled as such so they can be sent at lower volume or treated as unconfirmed; invalid is moved to the conflicts column and the email field is left empty. Input emails that were never checked are labelled unchecked, not verified.

## Example

> Merge my webinar sign-ups, the SaaStr attendee list and our HubSpot export into one sheet. Lots of people show up twice. Keep track of where each came from.

```
✓ 3 lists loaded · 2,140 rows · ✓ 1,190 enrichment records left this window
✓ 1,612 unique people · 528 duplicates merged · 741 companies
✓ 164 ambiguous rows sent to enrich_person · 151 resolved · 13 to review
→ Sheet "Merged contacts – Nov" created, 3 tabs (Merged, Companies, Review)
```

Illustrative output.

## Cost and limits

Loading, normalizing and local dedupe spend nothing. get_usage is free. Only enrich_person spends: 1 enrichment record per record returned, counted only when data comes back, so a 404 not_found uses no records but still counts as one request. The request limit is five times the record allowance, so retries do not hit it, and an Idempotency-Key keeps retries from counting twice. On Solo that is 1,000 enrichment records per five hours and 5,000 per week; free accounts share 1,000 one-time records across search and enrichment. The skill caps enrichment at 200 rows by default, checks get_usage before the batch, and splits the run across windows when it would not fit. It uses no search records and no scrape units.

## What it doesn't do

- Does not verify or re-verify emails already in the lists; hand the merged list to the Clean a list before sending skill for that.
- Does not search for new people or fill gaps beyond the ambiguous rows it needs to resolve.
- Does not delete or overwrite records in your CRM; it writes a merged list and leaves CRM changes to you.
