---
name: push-to-linkedcamp
description: "Builds or takes a prospect list, confirms each person's current role and verified work email with Leadsets search_people and enrich_person, and loads the send-ready leads into a LinkedCamp campaign with catch-alls held apart. Use when someone asks to push leads to LinkedCamp, load a list into a LinkedCamp campaign, or send prospects to LinkedCamp."
license: MIT
metadata:
  title: "Push a list to LinkedCamp"
  category: "Outreach handoff"
  outcome: "Launch outreach"
  tools: [get_usage, search_people, enrich_person]
  version: "1.0"
  author: Leadsets
  homepage: https://www.leadsets.ai/skills?utm_source=github&utm_medium=leadsets-skills&utm_campaign=push-to-linkedcamp
---

# Push a list to LinkedCamp

Takes an ICP or an existing list of people, confirms each one is still in the role with a verified work email, and loads them into a LinkedCamp campaign as leads. Built for founders and outbound teams who run LinkedIn and email sequences in LinkedCamp and want only checked contacts going in.

**Category:** Outreach handoff · **Outcome:** Launch outreach · **Tools:** `get_usage`, `search_people`, `enrich_person`

## Requirements

- The Leadsets MCP server connected to your agent: `https://mcp.leadsets.ai` ([setup](https://www.leadsets.ai/docs/mcp?utm_source=github&utm_medium=leadsets-skills&utm_campaign=push-to-linkedcamp)), or a Leadsets API key for the REST API.
- A Leadsets account. The free plan includes 1,000 records, no card ([get a key](https://www.leadsets.ai/signup?utm_source=github&utm_medium=leadsets-skills&utm_campaign=push-to-linkedcamp)).

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

- Push these 80 prospects into my LinkedCamp campaign "Q1 RevOps".
- Find heads of RevOps at US SaaS companies with 50 to 200 people and load them into LinkedCamp.
- Send this CSV of leads to LinkedCamp, but only the ones with verified emails.
- Refill my LinkedCamp campaign with 50 more VPs of Sales at fintechs.
- A prospect list was just built and the next step is starting a LinkedCamp sequence.

## What you give it

- **Lead source**: Either an ICP in plain language (industry, size, region, roles) or an existing list of people with name plus company domain or LinkedIn URL. Default: ask which one if neither is given.
- **LinkedCamp campaign**: Name of an existing LinkedCamp campaign, or a name for a new one. The agent uses its own LinkedCamp connection to write leads.
- **How many** (optional): Target number of leads to push when starting from an ICP. Default 50. Ignored when a list is supplied.
- **Catch-all handling** (optional): Push catch-all emails to a separate lower-volume campaign, export them to CSV, or hold them back. Default: hold back and list them in a CSV.

## Steps

1. **Confirm the source and the campaign**
   Restate the ICP or list, the target count and the LinkedCamp campaign name. Confirm the agent can reach LinkedCamp through its own connection and read the campaign's current leads. Ask one question only if the roles, region or campaign are ambiguous.
2. **Check limits and plan the run** · `get_usage`
   Call get_usage (free). Read search records left in the 5-hour window and week, enrichment records left, and reset times. Plan roughly 1 search record and 1 enrichment record per lead. If the run would cross a window or the free records, tell the user and either shrink the batch or split it across windows. Skip the search budget if a list was supplied.
3. **Probe the filters with one record** · `search_people`
   Only when starting from an ICP. Call search_people with the mapped filters (title, seniority, function, employees, industry, country) and limit 1. Check that the returned person and match_reasons fit the ICP. If the result is empty or off-target, adjust the filters and probe again before spending more records.
4. **Find the people** · `search_people`
   Call search_people with the confirmed filters, limit up to 100 per page, paging with next_cursor until about 1.3x the target count is reached to allow for drop-off. Set has_verified_email to true when the user wants verified-only leads. Respect the plan's concurrent search cap; on 429 too_many_concurrent or window_full, wait for Retry-After and retry with the same Idempotency-Key (REST API). For a supplied list, use search_people with title and company_domain only to locate people that lack a LinkedIn URL.
5. **Enrich each person** · `enrich_person`
   Call enrich_person for every person, with an Idempotency-Key per person. Keep current role, company, domain, work_email with status and confidence, and checked_at. Emails from enrich_person are already verified, so no separate verify_email call is needed. On 404 not_found record the person as no match and move on; on 402 free_records_exhausted stop and ask the user to upgrade; on 429 weekly_limit stop and report what is left to do.
6. **Segment and dedupe**
   Split results by email status: verified goes to the push set; catch-all goes to the catch-all set; unknown and no email go to a report and are not pushed. Invalid emails are never served, so treat them as no email. Drop people whose current role or company no longer matches the ICP. Remove duplicates by email and by person, then remove anyone already in the target LinkedCamp campaign.
7. **Push leads to LinkedCamp**
   Using the agent's LinkedCamp connection, add the verified set to the named campaign as leads with first name, last name, title, company, domain, work email and LinkedIn URL where available. Handle the catch-all set per the user's choice (separate campaign, CSV or held back). Do not start or schedule sending. Read the campaign back to confirm the lead count matches what was pushed.
8. **Report the run**
   Return the summary: people found, enriched, verified, catch-all, unknown or no email, duplicates skipped, leads pushed, records used, and a CSV of everything not pushed with the reason for each row.

## Checks before returning

- Only leads with status verified are pushed to the main campaign; catch-all, unknown and no-email contacts are never mixed in.
- No lead is pushed twice: duplicates within the run and people already in the campaign are removed first.
- Each pushed lead's current role and company came from enrich_person in this run, not from an old list.
- get_usage was called first and the run stayed inside the 5-hour and weekly windows; any stop on 429 or 402 is reported with what is left.
- If the search returned nothing or fewer people than requested, the report says so plainly instead of loosening the ICP silently.

## Output

A LinkedCamp campaign (the one the user named) with verified leads added, each carrying first_name, last_name, title, company, domain, work_email, linkedin_url and email_status=verified. Catch-all contacts go to a separate campaign named "<campaign> - catch-all" only if the user asked for it, otherwise to a CSV "<campaign>-catch-all.csv" with the same columns plus confidence. A CSV "<campaign>-not-pushed.csv" lists unknown, no email, not found, role changed and duplicate rows with a reason column. Invalid emails are never returned by Leadsets and never pushed. A short run summary is printed in chat.

## Example

> Find 50 VPs of Sales at US B2B SaaS companies with 50 to 200 people and push them into my LinkedCamp campaign "Sales leaders - Dec". Keep catch-alls out.

```
✓ 4,880 search · 13,950 enrichment records left this window
✓ 66 matching people  ·  ✓ 61 enriched  ·  3 role changed
✓ 49 verified  ·  6 catch-all (CSV)  ·  3 no email  ·  2 already in campaign
→ 47 leads added to LinkedCamp "Sales leaders - Dec"; not sending yet
```

Illustrative output.

## Cost and limits

search_people uses 1 search record per person returned and enrich_person 1 enrichment record per person returned; the email it returns is already verified at no extra cost. Empty results and errors use no records, but every call counts as a request. The probe costs at most 1 search record and get_usage costs nothing. On the free plan the 1,000 one-time records are shared by search and enrichment, so a 50-lead run uses about 130. On paid plans the skill checks get_usage first, stays under the plan's concurrent search cap, retries 429 window_full after Retry-After with the same Idempotency-Key (REST API) so nothing is counted twice, and splits large lists across windows. No scrape units are used.

## What it doesn't do

- Start, schedule or send the LinkedCamp campaign, or write message copy; it only loads leads.
- Push catch-all, unknown or unverified emails into the main campaign.
- Add phone numbers, which Leadsets does not provide.
