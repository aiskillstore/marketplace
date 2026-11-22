---
name: n8n-inbound-enrich
description: "Enriches every new inbound form fill coming through n8n with Leadsets enrich_person and enrich_company, scores each lead against your ICP with reasons, and routes good-fit leads to sales while holding the rest for nurture. Use when someone says \"enrich our form fills in n8n\", \"route inbound leads to sales\", \"score new demo requests\" or \"add firmographics to new signups\"."
license: MIT
metadata:
  title: "n8n inbound lead enrichment"
  category: "Outreach handoff"
  outcome: "Launch outreach"
  tools: [get_usage, enrich_person, enrich_company]
  version: "1.0"
  author: Leadsets
  homepage: https://www.leadsets.ai/skills?utm_source=github&utm_medium=leadsets-skills&utm_campaign=n8n-inbound-enrich
---

# n8n inbound lead enrichment

Takes new form submissions from an n8n workflow, adds current role, a verified work email when one exists and company firmographics, then decides which leads sales should see today. Built for GTM engineers and small teams who run inbound through n8n and want reps to get only good-fit leads, each with the reasons attached.

**Category:** Outreach handoff · **Outcome:** Launch outreach · **Tools:** `get_usage`, `enrich_person`, `enrich_company`

## Requirements

- The Leadsets MCP server connected to your agent: `https://mcp.leadsets.ai` ([setup](https://www.leadsets.ai/docs/mcp?utm_source=github&utm_medium=leadsets-skills&utm_campaign=n8n-inbound-enrich)), or a Leadsets API key for the REST API.
- A Leadsets account. The free plan includes 1,000 records, no card ([get a key](https://www.leadsets.ai/signup?utm_source=github&utm_medium=leadsets-skills&utm_campaign=n8n-inbound-enrich)).

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

- Enrich every new form fill in our n8n workflow and send good-fit leads to sales.
- Score this morning's demo requests against our ICP and tell me who to route to AEs.
- Add company size, industry and title to new signups before they hit the CRM.
- Set up an n8n step that enriches inbound leads with Leadsets and posts the good ones to Slack.
- Backfill enrichment for the last week of form submissions that came through n8n.

## What you give it

- **Form fills**: New submissions from the n8n workflow: at minimum name, email and company or domain, plus the submission ID and timestamp. Default: all submissions since the last run, read through the agent's own connection to n8n or from the payload the workflow passes in.
- **Fit rules**: Your ICP in plain language: industries, headcount band, countries, and the functions and seniority that count as a buyer. Default: B2B companies with 20 to 500 people, director level and above in revenue, marketing or ops.
- **Where good-fit leads go** (optional): The sales destination, for example a CRM owner queue (HubSpot, Salesforce, Pipedrive, Attio) or a Slack channel, written through the agent's own connection to that system. Default: return a routed table and let the n8n workflow branch on the fit field.
- **Where everything else goes** (optional): Destination for maybe and no-fit leads. Default: a nurture tab in Google Sheets or a CSV, never silently dropped.

## Steps

1. **Check limits and size the batch** · `get_usage`
   Call get_usage, which costs nothing. Read enrichment records left in the five-hour window and the week. Count the batch: one enrich_person per lead plus one enrich_company per unique domain. If the batch would cross the window, process the most recent submissions first and queue the rest for the next window. On the free plan, note that the 1,000 records are shared and do not refill.
2. **Normalize and dedupe the submissions**
   Pull the new form fills through the agent's connection to n8n. Trim and lowercase emails, derive the company domain from the email or the company field, and drop exact duplicate submissions by email. Skip submissions already enriched in a previous run (match on submission ID). Build a list of unique domains so each company is enriched once.
3. **Probe with one lead** · `enrich_person`
   Call enrich_person on a single lead first. Confirm the response maps cleanly to the fields the workflow expects (current role, company, work email with status, confidence and checked_at) and that the usage object looks as planned. Fix the mapping before running the rest.
4. **Enrich each unique company** · `enrich_company`
   Call enrich_company once per unique domain. Keep industry, headcount band, location and the source and checked date on each field. If a call returns 404 not_found, mark the company as not found and move on; do not retry. When calling over REST from an n8n HTTP node, send an Idempotency-Key per domain so a retry never counts twice.
5. **Enrich each person** · `enrich_person`
   Call enrich_person for every remaining lead, using the submission ID as the Idempotency-Key on REST calls. Record current role, seniority, company and the work email with its status (verified, catch-all or unknown) and confidence. On 404 not_found, keep the lead with the submitted data only. On 429 window_full, wait the Retry-After seconds and continue; on 429 weekly_limit, stop and queue the rest until resets_at; on 402 free_records_exhausted, stop and ask the user to upgrade.
6. **Score fit with reasons**
   Score each lead against the fit rules: industry, headcount band, country, function and seniority. Label it good fit, maybe or no fit, and write the specific reasons (for example "VP, revenue function, 120 people, SaaS, US"). If key fields are missing because enrichment found nothing, label maybe, not no fit, and say what was missing.
7. **Route the leads**
   Send good-fit leads to the sales destination through the agent's own connection to the CRM or Slack, including fit reasons and email status. Send maybe and no-fit leads to the nurture destination. Hold good-fit leads with an unknown email status for rep review instead of auto-adding them to a sequence. Do not write anything until enrichment for that lead is complete.
8. **Report the run**
   Return a short summary: submissions read, duplicates skipped, people and companies enriched, not found, fit counts, email status counts, where each group went, records used and what is queued for the next window.

## Checks before returning

- Every submission is accounted for exactly once: routed to sales, sent to nurture, queued for the next window or listed as skipped with a reason.
- No duplicate leads or repeat enrichments: submissions deduped by email and submission ID, companies enriched once per domain.
- Email status is carried through as returned: catch-all and unknown are never relabelled verified, and good-fit leads with unknown status are held for review.
- Records used match the plan from get_usage, and any 429 or 402 stopped or paused the run instead of being retried blindly.
- Every good-fit lead has written fit reasons; a lead with no enrichment data is labelled maybe with the missing fields named, never auto-rejected.

## Output

One row per submission with: submission_id, submitted_at, full_name, submitted_email, title, seniority, function, company_name, domain, industry, headcount_band, company_location, work_email, email_status, email_confidence, checked_at, fit (good fit, maybe, no fit), fit_reasons, route, notes. Good-fit rows go to the sales destination; maybe and no-fit rows go to a "Nurture" tab or CSV; a "Run log" tab lists duplicates skipped, not-found lookups and leads queued for the next window. Verified emails route normally. Catch-all emails route with a "catch-all, send at lower volume" note. Unknown emails are marked unconfirmed and good-fit leads with unknown status are held for rep review. Invalid emails are never served by Leadsets, so a lead with no usable address is marked "no verified email" and keeps only the address the person submitted.

## Example

> Enrich the 60 demo requests that came through our n8n form this week. Good fit is B2B SaaS, 50 to 500 people, US or Canada, director and up in sales or RevOps. Post good fits to #inbound-sales and put the rest in the Nurture sheet.

```
✓ 1,000 free records left  ·  ✓ 60 submissions, 4 duplicates skipped
✓ 41 companies enriched  ·  ✓ 53 people enriched  ·  3 not found
✓ 19 good fit  ·  21 maybe  ·  16 no fit  ·  2 good fits held (unknown email)
→ 17 posted to #inbound-sales  ·  37 added to "Nurture" sheet
```

Illustrative output.

## Cost and limits

enrich_person and enrich_company each use 1 enrichment record per record returned and 1 request per call. Lookups that return nothing (404 not_found) use no records but still count as a request. get_usage is free. The skill enriches each domain once, dedupes submissions before calling, and probes with one lead before the batch, so records go only to new, unique leads. On Free, the 1,000 one-time records are shared across search and enrichment; on Solo the enrichment window is 1,000 records per five hours and 5,000 per week, higher on Pro, Team and Max. Over a limit, Leadsets returns 429 with Retry-After and the blocked call counts against nothing; the skill waits on window_full, queues the rest on weekly_limit and stops on 402. Idempotency keys on REST calls from n8n mean retries never double-count. No scrape units are used.

## What it doesn't do

- Does not send emails or start sequences; Leadsets feeds the CRM, Slack or sequencer and the user's own tools do the sending.
- Does not run standalone verify_email on the address the person typed into the form; use the Clean a list before sending skill for that.
- Does not search for other contacts at the lead's company; use Find decision-makers at a company or Buying committee mapper for that.
