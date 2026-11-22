---
name: icp-builder
description: "Interviews the user for about five minutes about their offer, best customers and buyers, turns the answers into company and people filters, tests them with small search_companies probes, and saves the ICP as a reusable filter file other Leadsets skills can run. Use when someone says \"define my ICP\", \"who should we target\", \"turn my ideal customer into filters\" or \"save my ICP\"."
license: MIT
metadata:
  title: "ICP builder"
  category: "List building"
  outcome: "Find new prospects"
  tools: [get_usage, search_companies]
  version: "1.0"
  author: Leadsets
  homepage: https://www.leadsets.ai/skills?utm_source=github&utm_medium=leadsets-skills&utm_campaign=icp-builder
---

# ICP builder

Turns a plain-language description of your best customers into tested, reusable Leadsets filters, saved as one file you can hand to any prospecting skill. Built for founders, agencies and GTM engineers who want every future list to start from the same, checked definition instead of a fresh guess.

**Category:** List building · **Outcome:** Find new prospects · **Tools:** `get_usage`, `search_companies`

## Requirements

- The Leadsets MCP server connected to your agent: `https://mcp.leadsets.ai` ([setup](https://www.leadsets.ai/docs/mcp?utm_source=github&utm_medium=leadsets-skills&utm_campaign=icp-builder)), or a Leadsets API key for the REST API.
- A Leadsets account. The free plan includes 1,000 records, no card ([get a key](https://www.leadsets.ai/signup?utm_source=github&utm_medium=leadsets-skills&utm_campaign=icp-builder)).

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

- "Help me define my ICP before we build any lists."
- "Turn 'RevOps leads at 50 to 200 person fintechs' into filters I can reuse."
- "Our best customers are northwind.co, stackfold.io and parcelry.co. Who else looks like them?" (as a first step, before searching people)
- An agency onboarding a new client that needs a saved ICP per client
- A prospect-list run returned off-target accounts and the filters need to be rebuilt

## What you give it

- **Your offer and best customers**: What you sell and, if you have them, 2 to 5 customer domains you would clone. Plain language is fine.
- **Market constraints** (optional): Industry, headcount band, countries, technology used, and anything to exclude. Defaults: no exclusions, country taken from your answer or asked once.
- **Buyer roles** (optional): Who signs or champions the deal: titles, function and seniority. Default: ask, then suggest function and seniority values from your offer.
- **ICP name and save location** (optional): A short name such as "revops-saas-us". Default: a file named icp-<name>.json in the working folder, or a tab in a Google Sheet the agent can already write to.
- **Probe budget** (optional): Maximum search records the probes may spend. Default 25.

## Steps

1. **Run the five-minute interview**
   Ask no more than seven short questions, one at a time: what you sell and the problem it solves; 2 to 5 best customers by domain; industry; headcount band; countries; technology or other signals that matter; who buys (titles, function, seniority) and what to exclude. Skip any question the user already answered. If an answer is vague ("mid-market"), propose a concrete value ("employees 200-1000?") and let the user confirm.
2. **Check limits before spending records** · `get_usage`
   Call get_usage, which costs nothing. Read search records left in the five-hour window and the week, and free records left on the Free plan. If fewer records remain than the probe budget, lower the budget and tell the user. Do not start probes if the search window is full; report the reset time instead.
3. **Translate answers into filters**
   Build two filter sets. Company filters for search_companies: industry, headcount band, location, technology. People filters for later search_people runs, using only documented values: title (string list, fuzzy-matched), function (revenue, marketing, engineering, product, ops, finance, hr), seniority (c_level, vp, head, director, manager, ic), employees as a range like "50-200", industry slugs like "saas", country as ISO 3166-1 alpha-2 codes, and has_verified_email if the user only wants sendable contacts. Write each filter next to the interview answer it came from.
4. **Probe with one record** · `search_companies`
   Call search_companies with the company filters and limit 1. On 400 invalid_request, fix the filter the message names and probe again; do not retry unchanged. On an empty result (0 records, 1 request), loosen one filter at a time, starting with the narrowest, and say which one you changed. On 429, wait for Retry-After before retrying.
5. **Show a small sample and tune** · `search_companies`
   Call search_companies with limit 10 and show each account with its domain and match_reasons. Ask the user to mark any account that does not fit and why, then tighten or add exclusions. Re-run at most two more tuning rounds, keeping total probe spend within the budget. If the user gave customer domains, check whether they would pass the filters and point out any that would not.
6. **Save the ICP as reusable filters**
   Write the confirmed ICP to the save location through the agent's own file or Google Sheets access. Include the name, date, a one-line summary, company_filters, people_filters, exclusions, the interview answers each filter came from, and the sample accounts that passed. Keep it in the exact argument shape search_companies and search_people accept so other skills can load it without edits.
7. **Report the run**
   Return a short summary: filters saved, where, records spent, sample size, anything still uncertain, and the next skill to run (for example Build an outbound prospect list or Lookalike accounts).

## Checks before returning

- Every people filter value is one of the documented enums or formats (seniority, function, ISO country codes, employees as a range); nothing invented.
- The final company filters returned at least one account on the last probe; an ICP that returns zero is not saved without telling the user.
- The user confirmed the sample accounts fit, and any customer domains they gave were checked against the filters with mismatches reported.
- Total probe spend stayed within the probe budget and the remaining search records reported by the usage object.
- The saved file has no duplicate or contradictory filters (for example two different headcount bands) and loads as valid JSON.

## Output

One file, icp-<name>.json (or a tab named "ICP - <name>" in the chosen Google Sheet), with fields: name, created (date), summary, company_filters {industry, employees, country, technology}, people_filters {title, function, seniority, employees, industry, country, has_verified_email}, exclusions, rationale (filter to interview answer), sample_accounts (name, domain, match_reasons), records_spent. The skill does not collect people or emails, so no verification statuses appear; if has_verified_email is set, downstream skills return only verified contacts, and those skills are responsible for segmenting catch-all, unknown and invalid emails.

## Example

> Help me nail down our ICP. We sell a revenue forecasting tool; our best customers are northwind.co and stackfold.io. Save it so I can reuse it for prospect lists.

```
✓ Interview done (6 questions)  ·  ✓ 486 search records left this window
✓ Probe: 1 match  ·  ✓ Sample: 10 accounts, 8 confirmed, 2 excluded (agencies)
✓ Filters: B2B SaaS · employees 50-200 · US · function revenue · seniority vp, head
→ Saved icp-revops-saas-us.json · 12 search records used
```

Illustrative output.

## Cost and limits

get_usage is free. search_companies uses 1 search record per record returned and 1 request per call; an empty probe uses 0 records. A typical run spends 11 to 25 search records (one 1-record probe plus up to three 10-record samples), well inside Solo's 500 search records per five hours; on Free they come out of the 1,000 one-time records shared by search and enrichment. Probes run one at a time, so the plan's concurrent-search limit is never reached. On 429 the skill waits for Retry-After, and the blocked call counts against nothing.

## What it doesn't do

- Search for people, enrich contacts or verify emails; it only defines and tests the filters that later skills use.
- Write to a CRM or sequencer, or store the ICP inside Leadsets; the filter file lives wherever the agent saves it.
- Scrape company websites or careers pages, so it spends no scrape units.
