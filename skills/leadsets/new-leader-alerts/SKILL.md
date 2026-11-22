---
name: new-leader-alerts
description: "Watches a list of target accounts for new VP and C-level leaders by comparing each run against a saved snapshot, confirms every new name with enrich_person and returns alerts with verified emails. Use when someone asks to track new executives, spot leadership changes, find new VPs at target accounts, or watch accounts for a new buyer."
license: MIT
metadata:
  title: "New leader alerts"
  category: "Hiring signals"
  outcome: "Research accounts and timing"
  tools: [get_usage, search_people, enrich_person]
  version: "1.0"
  author: Leadsets
  homepage: https://www.leadsets.ai/skills?utm_source=github&utm_medium=leadsets-skills&utm_campaign=new-leader-alerts
---

# New leader alerts

Turns a target account list into a recurring alert of new VP and C-level leaders, each confirmed against current role data and paired with an honestly labelled work email. Built for founders, AEs and GTM engineers who want to reach a new leader early, while they are still choosing tools and vendors.

**Category:** Hiring signals · **Outcome:** Research accounts and timing · **Tools:** `get_usage`, `search_people`, `enrich_person`

## Requirements

- The Leadsets MCP server connected to your agent: `https://mcp.leadsets.ai` ([setup](https://www.leadsets.ai/docs/mcp?utm_source=github&utm_medium=leadsets-skills&utm_campaign=new-leader-alerts)), or a Leadsets API key for the REST API.
- A Leadsets account. The free plan includes 1,000 records, no card ([get a key](https://www.leadsets.ai/signup?utm_source=github&utm_medium=leadsets-skills&utm_campaign=new-leader-alerts)).

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

- Tell me when any of my 50 target accounts gets a new VP or C-level hire.
- Watch these domains for new sales or revenue leaders and alert me in Slack.
- Who are the new executives at my tier 1 accounts since last month?
- Run a weekly leadership-change check on my named account list.
- Compare today's VP+ people at these companies with my last snapshot and show what changed.

## What you give it

- **Target accounts**: A list of company domains from a CSV, a Google Sheet or a CRM view, for example northwind.co, stackfold.io, parcelry.co. Domains, not company names. Up to a few hundred per run on Solo.
- **Roles to watch** (optional): Seniority and function to track. Default: seniority vp and c_level across all functions. Narrow with function (revenue, marketing, engineering, product, ops, finance, hr) or titles if you only care about your buyer.
- **Previous snapshot** (optional): The leaders file saved by the last run (person_id, name, title, domain, date first seen). Default: none, in which case this run builds the baseline and sends no alerts.
- **Where alerts go** (optional): CSV, a Google Sheet tab, a Slack channel or a CRM note or task. Default: CSV plus a summary in chat. Written through the agent's own connection to that system.

## Steps

1. **Plan the run against remaining limits** · `get_usage`
   Call get_usage and read search records left in the five-hour window and the week, and enrichment records left. Estimate search cost as accounts x about 5 leaders per account, and enrichment as the expected number of new names (usually under 10 percent of the snapshot). If search would cross the window, split the account list into batches and tell the user how many windows the run needs. On the free plan, warn that a recurring watch draws down the 1,000 one-time records each run.
2. **Load the snapshot and confirm scope**
   Read the previous snapshot if one exists and check it has person_id and company domain on every row. Confirm roles to watch. If no snapshot exists, tell the user this run creates the baseline and will report current leaders, not new ones. Ask one question only if the account list or roles are ambiguous.
3. **Probe the filters on one account** · `search_people`
   Call search_people with company_domain set to one target domain, seniority ["vp","c_level"], any function filter, and limit 1. Check the result's match_reasons reflect seniority and company. If it returns 0 for a domain you expect to have leaders, check the domain spelling and filters before spending on the full run. An empty result uses no records.
4. **Pull current leaders at every account** · `search_people`
   Call search_people with company_domain set to a batch of target domains, the same seniority and function filters, and limit 100. Page with next_cursor until it is empty. Keep concurrent calls within the plan (3 Solo, 5 Pro, 8 Team and Max). On 429 window_full wait for Retry-After and retry with the same Idempotency-Key (REST API); on 429 weekly_limit stop, save progress and report the resets_at time. Record person_id, full_name, title, company domain and match_reasons for each result.
5. **Diff against the snapshot**
   Match on person_id, then on name plus domain as a fallback. Flag as candidate new leaders: people not in the snapshot, and people already in the snapshot whose title moved up to VP or C-level. Note people in the snapshot who no longer appear as possible departures, but do not alert on them. Dedupe people returned under more than one domain.
6. **Confirm each new leader and get a contact** · `enrich_person`
   Call enrich_person only on candidate new leaders, never on the whole snapshot. Keep a candidate only if current_role and company match the target account; drop anyone whose current company differs. Read the work_email status and the checked_at date on the role. A 404 not_found means nothing to enrich: keep the alert without an email and move on. Emails from enrich_person are already verified, so do not call verify_email again.
7. **Deliver alerts and save the new snapshot**
   Write the alert rows to the chosen destination and post a short summary. Save the full current leader list as the new snapshot with a first_seen date for each new person, so the next run diffs against it. Report counts for accounts checked, leaders found, new leaders confirmed, dropped candidates and accounts with no results.

## Checks before returning

- On a baseline run, no person is labelled new; the output says the baseline was created.
- Every alert has enrich_person data showing the person's current role at the target account, with its checked_at date; mismatches are dropped and counted.
- No duplicates across accounts or against the previous snapshot, matched on person_id first.
- Emails keep their Leadsets label: verified, catch-all or unknown are shown as such and never rounded up; invalid emails never appear as contacts.
- Accounts that returned zero leaders and any batches stopped by a 429 are listed so the user knows what was not checked.

## Output

A table named "New leaders" (CSV file, Sheet tab or Slack message rows) with columns: company, domain, full_name, title, seniority, change (new person or promoted), first_seen (this run's date), role_checked_at, work_email, email_status, confidence, match_reasons. Verified emails are ready to use. Catch-all emails stay in the table with status catch-all and a note to send at lower volume. Unknown emails stay with status unknown and are marked unconfirmed. Invalid emails are never served, so those rows show no email. A second tab or file, "Leader snapshot", holds the full current list for the next run, plus a short list of possible departures and accounts with no results.

## Example

> Here are my 60 target accounts in the "Tier 1" sheet. Every Monday, tell me which ones got a new VP or C-level leader, with emails, and post it to #new-leaders in Slack.

```
✓ 14,820 search records left this window  ·  ✓ snapshot from last Monday loaded (318 leaders)
✓ 60 accounts checked  ·  326 current VP+ leaders  ·  2 accounts returned none
✓ 11 candidates  ·  9 confirmed new leaders  ·  2 dropped (different current company)
✓ 7 verified  ·  1 catch-all  ·  1 no email
→ 9 alerts posted to #new-leaders, snapshot updated
```

Illustrative output.

## Cost and limits

search_people uses 1 search record per leader returned, so each run costs roughly the size of the leader snapshot; empty results use no records but still count as requests. enrich_person uses 1 enrichment record per confirmed result and runs only on new candidates, which keeps enrichment small. No verify_email calls are needed because enrich_person emails are already verified, and no scrape units are used. get_usage is free and runs first; large account lists are split across five-hour windows (Solo allows 500 search records per five hours and 2,500 per week). On 429 the skill waits for Retry-After or stops at a weekly limit, using Idempotency-Keys so retries never double-count. The free plan's 1,000 one-time records are shared across search and enrichment and do not refill, so a recurring watch needs a paid plan.

## What it doesn't do

- It does not claim an official start date: first_seen is when the change was detected by this skill, and role_checked_at is when Leadsets last checked the role.
- It does not write or send outreach; it hands confirmed leaders to your sequencer, CRM or Slack.
- It does not read press releases, careers pages or news, so it uses no scrape units and catches changes only once they appear in Leadsets data.
