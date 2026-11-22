---
name: signal-slack-alerts
description: "Watches a list of target accounts for new hiring and leadership signals and posts a short, deduplicated alert for each one to a Slack channel. Reads careers pages with scrape_jobs and re-checks tracked leaders with enrich_person. Use when someone asks to get Slack alerts for hiring signals, watch target accounts, or flag new leaders and job changes at named accounts."
license: MIT
metadata:
  title: "Signal alerts to Slack"
  category: "Outreach handoff"
  outcome: "Research accounts and timing"
  tools: [get_usage, scrape_jobs, enrich_person]
  version: "1.0"
  author: Leadsets
  homepage: https://www.leadsets.ai/skills?utm_source=github&utm_medium=leadsets-skills&utm_campaign=signal-slack-alerts
---

# Signal alerts to Slack

Turns a target account list into a running feed of timing signals in Slack: new open roles that predict a need for what you sell, and leaders at those accounts who changed title or company. Built for founders, SDR teams and GTM engineers who want reps to see why now is the moment without opening another dashboard.

**Category:** Outreach handoff · **Outcome:** Research accounts and timing · **Tools:** `get_usage`, `scrape_jobs`, `enrich_person`

## Requirements

- The Leadsets MCP server connected to your agent: `https://mcp.leadsets.ai` ([setup](https://www.leadsets.ai/docs/mcp?utm_source=github&utm_medium=leadsets-skills&utm_campaign=signal-slack-alerts)), or a Leadsets API key for the REST API.
- A Leadsets account. The free plan includes 1,000 records, no card ([get a key](https://www.leadsets.ai/signup?utm_source=github&utm_medium=leadsets-skills&utm_campaign=signal-slack-alerts)).

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

- Post new hiring signals on my target accounts to #signals in Slack.
- Tell me in Slack when any of these 40 accounts starts hiring SDRs or RevOps.
- Watch our tier 1 accounts and alert the channel when a VP or C-level contact changes role.
- Run a weekly signal check on this account list and post what changed.
- Set up timing alerts for the accounts in this sheet before reps start sequencing.

## What you give it

- **Target accounts**: Company domains, from a CSV, a Google Sheet or a CRM list the agent can read. Careers page URLs are optional; if missing, the agent uses the careers link found on the company site. Keep the first run to 50 accounts or fewer.
- **Signals to watch**: Role keywords that predict a need for what you sell (for example SDR, BDR, RevOps, Head of Sales) and seniority for leadership changes. Default: sales and revenue roles, plus VP and C-level leaders.
- **Tracked leaders** (optional): Optional list of known contacts at those accounts (name and company, or a LinkedIn URL) to re-check for role or company changes. If none is given, the skill runs hiring signals only.
- **Slack channel and lookback**: The channel to post to through the agent's own Slack connection, and how far back a posting counts as new. Default lookback: 14 days, or since the last run if a previous snapshot exists.

## Steps

1. **Check remaining scrape units and enrichment records** · `get_usage`
   Call get_usage. It costs nothing. Read scrape_units and the enrichment records left in the five-hour window and the week. scrape_jobs is not on the Free plan; if there are no scrape units, stop and tell the user scraping is an add-on on paid plans, then offer to run leadership checks only. Estimate one unit per careers page and one enrichment record per tracked leader, and split the account list across windows if it would not fit.
2. **Load the watchlist and the last snapshot**
   Read the target accounts, role keywords and tracked leaders from the user's file, sheet or CRM through the agent's own connection. Load the previous run's snapshot if one exists (open roles per domain, last known title and company per leader, and alert IDs already posted). Dedupe domains and contacts before spending anything.
3. **Probe one careers page** · `scrape_jobs`
   Call scrape_jobs on a single account's careers page first. Confirm it returns open roles with titles and dates and that the role keywords match the way that company titles its jobs. If titles do not match, adjust the keywords with the user before scraping the full list.
4. **Scrape careers pages for hiring signals** · `scrape_jobs`
   Call scrape_jobs for each remaining account. Keep a role only if its title matches a watched keyword and its posted date is inside the lookback window or it is absent from the last snapshot. Record title, posted date and source URL for each match. On 429, wait for Retry-After and retry; stop and report if scrape units run out mid-run.
5. **Re-check tracked leaders for leadership signals** · `enrich_person`
   Call enrich_person for each tracked leader. Compare current role and company with the snapshot. Flag a signal when the title changed into a watched seniority (new VP or C-level) or when the person moved to a new company. On 404 not_found, mark the contact as not found and move on without retrying. Read the usage object on each response and pause before the enrichment window fills.
6. **Build alerts and drop duplicates**
   Group signals by account. Build one alert per account with the company, signal type, role title or new title, posted or checked date and source. Skip any signal already posted in a previous run. Include a contact email only when its status is verified; label catch-all addresses as catch-all; never include unknown or invalid addresses.
7. **Post to Slack and save the snapshot**
   Post the alerts to the chosen channel through the agent's own Slack connection, one message per account, newest signals first. Then write the new snapshot (roles, leader titles, posted alert IDs) back to the user's file or sheet so the next run only reports what changed. Return a short run summary to the user.

## Checks before returning

- Every hiring alert has a role title, a posted date inside the lookback window and a source careers page; roles without a date are labelled date unknown, not presented as new.
- No signal is posted twice: compare against alert IDs from the previous snapshot before posting.
- Emails shown in Slack are verified, or clearly labelled catch-all; unknown and invalid addresses are never posted.
- Accounts where scrape_jobs returned no roles and leaders who returned 404 are listed in the run summary, not silently dropped.
- Remaining scrape units and enrichment records are reported, and any accounts deferred to the next window are named.

## Output

One Slack message per account with signals, in this shape: Company (domain) · Signal type (Hiring or Leadership) · Detail (role title and posted date, or old title → new title) · Contact (name, title, email with status) · Source link · Checked date. Email handling: verified emails are shown as is, catch-all emails are shown with a catch-all label and a note to send at lower volume, unknown emails are omitted and noted as unconfirmed, invalid emails are never shown. Alongside the Slack posts, the agent saves a snapshot tab or file named "signals-snapshot" with columns domain, role_title, posted_date, leader_name, last_title, last_company, alert_id, checked_at, and returns a plain-text run summary to the user.

## Example

> Check these 40 target accounts for new SDR, BDR and RevOps openings in the last 14 days, and flag any VP or C-level contact on my list who changed roles. Post it to #sales-signals.

```
✓ 3,980 scrape units left  ·  ✓ 912 enrichment records left this window
✓ 40 careers pages read  ·  11 accounts hiring for watched roles (17 roles)
✓ 62 leaders re-checked  ·  4 new titles  ·  2 moved company  ·  3 not found
✓ 2 contacts verified  ·  1 catch-all (labelled)  ·  3 already posted, skipped
→ 15 alerts posted to #sales-signals, snapshot saved
```

Illustrative output.

## Cost and limits

scrape_jobs uses 1 scrape unit per page and does not touch search or enrichment records; scraping is an add-on on every paid plan, sold in packs of 1,000, 5,000 or 20,000 units, and is not available on Free. enrich_person uses 1 enrichment record per record returned, and the email it returns is already verified at no extra cost; a 404 not_found or empty result uses no records but still counts as one request. get_usage is free and runs first so the skill can size the run. Enrichment has a rolling five-hour window and a weekly limit per plan (for example 1,000 per five hours and 5,000 per week on Solo); if the leader list would cross a window, the skill checks the most important accounts first and defers the rest. On a 429 it waits for Retry-After, and blocked calls count against nothing.

## What it doesn't do

- Does not send emails or messages to prospects; it only posts internal alerts to Slack and leaves outreach to your sequencer or reps.
- Does not scrape pages behind a login or anything other than public careers pages, and does not post unknown or invalid emails into the channel.
- Does not find new leaders it was not given; leadership signals come only from re-checking the tracked contacts you supply.
