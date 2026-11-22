---
name: hiring-to-pain
description: "Reads open roles from company careers pages with scrape_jobs and turns each posting into the likely business pain behind the hire and a matching outreach angle, with the posting evidence attached. Needs scrape units on a paid Leadsets plan. Use when someone asks what a company's job posts say about its problems, wants hiring-based message angles, or says \"map hiring to pain\" or \"why are they hiring\"."
license: MIT
metadata:
  title: "Hiring-to-pain mapper"
  category: "Hiring signals"
  outcome: "Launch outreach"
  tools: [get_usage, scrape_jobs]
  version: "1.0"
  author: Leadsets
  homepage: https://www.leadsets.ai/skills?utm_source=github&utm_medium=leadsets-skills&utm_campaign=hiring-to-pain
---

# Hiring-to-pain mapper

Turns a list of target domains into a table of open roles, the pain each hire most likely signals, and one message angle per account, each tied to the posting it came from. Built for founders, SDRs and GTM engineers who want a true, specific reason to reach out instead of a generic opener.

**Category:** Hiring signals · **Outcome:** Launch outreach · **Tools:** `get_usage`, `scrape_jobs`

## Requirements

- The Leadsets MCP server connected to your agent: `https://mcp.leadsets.ai` ([setup](https://www.leadsets.ai/docs/mcp?utm_source=github&utm_medium=leadsets-skills&utm_campaign=hiring-to-pain)), or a Leadsets API key for the REST API.
- A Leadsets account. The free plan includes 1,000 records, no card ([get a key](https://www.leadsets.ai/signup?utm_source=github&utm_medium=leadsets-skills&utm_campaign=hiring-to-pain)).

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

- "Read the careers pages for these 20 domains and tell me what problems they're hiring to fix."
- "Northwind Analytics just posted a RevOps Manager role. What angle should I open with?"
- Turning a hiring signal list into message angles before writing a sequence
- "Why is Stackfold hiring three SDRs, and how does that connect to what we sell?"
- Preparing account notes for reps before outreach on accounts that are actively hiring

## What you give it

- **Target domains**: One or more company domains or careers page URLs, pasted in chat or read from a CSV or Google Sheet through the agent's own connection. No default; ask if missing.
- **What you sell**: One or two sentences on your product and the problem it solves, so angles map pain to your offer. If not given, ask once; without it the skill returns pains only and leaves the angle column generic.
- **Roles of interest** (optional): Functions or titles that predict need for your product, for example sales, RevOps, data engineering. Default: all open roles, ranked by relevance to what you sell.
- **Recency window** (optional): Only map roles posted within this window. Default 30 days. Roles without a posted date are kept but flagged.
- **Where it goes** (optional): Table in chat, CSV, or a Google Sheet through the agent's own connection. Default: table in chat plus CSV.

## Steps

1. **Confirm inputs and the offer**
   Restate the domain list, what you sell, the roles of interest and the recency window. Dedupe domains and normalise them (strip paths, lowercase). Ask one question if the offer or the domain list is ambiguous. Do not start scraping until the offer is clear enough to judge relevance.
2. **Check scrape units and plan the run** · `get_usage`
   Call get_usage (free) and read scrape_units. scrape_jobs costs 1 unit per page, so budget at least one unit per domain and more for careers sites with several pages. If the account is on Free or has no scrape units, stop and tell the user scraping is a paid add-on in unit packs. If units are short, propose the highest-priority subset of domains and ask before continuing.
3. **Probe with one domain** · `scrape_jobs`
   Call scrape_jobs on the first domain only. Check that roles come back with titles and dates and note whether description text, team or location are present, since that decides how much evidence each pain can cite. Confirm units used from the response. If the probe returns nothing, try the careers page URL directly before moving on.
4. **Scrape the remaining careers pages** · `scrape_jobs`
   Call scrape_jobs on each remaining domain in sequence. Record every role with title, team, location, posted date and source URL. On an empty result, mark the domain "no public roles found" and continue. On a 429, wait for Retry-After and retry the same domain. Re-check scrape units with get_usage every 25 domains and stop cleanly if they run out, reporting which domains were not read.
5. **Filter and rank roles**
   Drop roles outside the recency window, keep undated roles with a flag, and merge duplicate postings of the same title across locations into one row with a count. Rank roles by relevance to the roles of interest and what you sell. Keep at most the top 3 relevant roles per account for mapping.
6. **Map each role to a likely pain**
   For each kept role, infer the most likely pain from the evidence: the title, seniority, team, volume of similar openings and any responsibilities or tools named in the posting text. Quote or cite the exact phrase used as evidence. Grade confidence high when the posting text states the problem, medium when it is inferred from title plus team or volume, low when only the title is available. Never invent facts about the company that the posting does not support.
7. **Write one angle per account**
   Combine the mapped pains for each account into one message angle that connects the strongest pain to what you sell, in one or two plain sentences, plus a suggested opening observation that references the posting. Keep it specific and true; no claims about metrics, funding or tools the company did not publish.
8. **Return the table and report gaps**
   Return the table in chat and write the CSV or Sheet through the agent's own connection. Summarise domains read, roles found, roles mapped, domains with no public roles, and scrape units used and left.

## Checks before returning

- get_usage was called before scraping and scrape units cover the planned pages; if units ran out mid-run, the unread domains are listed by name
- Every pain row cites evidence from the posting and a source URL; rows with only a title are graded low confidence, not presented as fact
- Duplicate postings of the same role are merged, and roles outside the recency window are excluded or flagged as undated
- Domains with empty careers pages are reported as "no public roles found" rather than silently dropped
- Angles reference only what the company published and what the user sells; no invented metrics, customers or tools

## Output

One table, also saved as CSV (default file name hiring-to-pain-YYYY-MM-DD.csv) or a Google Sheet with two tabs. Tab "Roles": domain, company, role_title, team, location, posted_date, openings_count, source_url, evidence (quoted phrase or "title only"), likely_pain, confidence (high, medium, low). Tab "Angles": domain, company, top_pain, message_angle, opening_observation, roles_used. A short footer lists domains with no public roles, undated roles kept, and domains not read for lack of units. The skill returns no contacts or emails, so verified, catch-all, unknown and invalid labels do not apply here; to add verified people, hand the Angles tab to a contact-finding skill that runs search_people, enrich_person and verify_email.

## Example

> Here are 15 domains we're targeting, including northwind.co, stackfold.io and parcelry.co. We sell a pipeline forecasting tool for sales teams. Read their careers pages and give me the likely pain and an opening angle for each, roles posted in the last 30 days.

```
✓ 15 domains  ·  ✓ 1,240 scrape units left, run needs about 40
✓ 14 careers pages read  ·  1 no public roles (parcelry.co)
✓ 63 open roles  ·  29 relevant in last 30 days  ·  22 mapped (9 high, 10 medium, 3 low)
→ Northwind Analytics: RevOps Manager + 2 SDRs, pain "forecast built by hand in spreadsheets"
→ hiring-to-pain-2026-11-09.csv saved, 2 tabs, 38 units used
```

Illustrative output.

## Cost and limits

scrape_jobs costs 1 scrape unit per page read and uses no search or enrichment records. Scraping is not available on the Free plan; it is an add-on on every paid plan, sold in packs of 1,000, 5,000 or 20,000 units that do not expire while subscribed. get_usage is free and is called before the run and every 25 domains to confirm units remain. The skill probes one domain first so a bad input costs one domain, not the whole list. On a 429 it waits for Retry-After and retries; blocked calls count against nothing. Leadsets reads public careers pages only and respects robots signals, so some pages may return nothing.

## What it doesn't do

- Find, enrich or verify contacts at the accounts; it stops at pains and angles and leaves people and emails to other skills
- Write full emails or sequences, or push anything into a sequencer or CRM by itself
- Read pages behind a login or guess at company facts the postings do not state
