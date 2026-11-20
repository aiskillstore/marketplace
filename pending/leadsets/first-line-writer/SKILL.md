---
name: first-line-writer
description: "Writes one specific, true opening line per prospect from facts on their company's homepage and careers page, using Leadsets scrape_company and scrape_jobs. Scrapes each domain once, cites the fact behind every line and leaves a line blank rather than guessing. Use when someone asks for personalized first lines, icebreakers, opening lines or custom intros for a prospect list or campaign."
license: MIT
metadata:
  title: "Personalized first lines"
  category: "Company research"
  outcome: "Launch outreach"
  tools: [get_usage, scrape_company, scrape_jobs]
  version: "1.0"
  author: Leadsets
  homepage: https://www.leadsets.ai/skills?utm_source=github&utm_medium=leadsets-skills&utm_campaign=first-line-writer
---

# Personalized first lines

Takes a prospect list and returns one short opening line per person, each built from something the company actually says on its site or is actually hiring for, with the source fact next to it. Built for founders, SDRs and agencies who want personalization they can defend, not filler that could fit any company.

**Category:** Company research · **Outcome:** Launch outreach · **Tools:** `get_usage`, `scrape_company`, `scrape_jobs`

## Requirements

- The Leadsets MCP server connected to your agent: `https://mcp.leadsets.ai` ([setup](https://www.leadsets.ai/docs/mcp?utm_source=github&utm_medium=leadsets-skills&utm_campaign=first-line-writer)), or a Leadsets API key for the REST API.
- A Leadsets account. The free plan includes 1,000 records, no card ([get a key](https://www.leadsets.ai/signup?utm_source=github&utm_medium=leadsets-skills&utm_campaign=first-line-writer)).

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

- "Write a personalized first line for each prospect in this sheet."
- "Add icebreakers to my Instantly or Smartlead CSV before I load it."
- "Give me an opening line for each of these 40 accounts based on what they sell and who they're hiring."
- A verified prospect list is ready and needs a custom first-line field before it goes to LinkedCamp or a sequencer.
- Someone asks for personalization that references real company facts, such as products, customers named or open roles.

## What you give it

- **Prospect list**: CSV, Google Sheet, or an existing campaign export with at least first name, title and company domain per row. An email and email status column is passed through untouched if present.
- **What you sell**: One or two sentences on your product and the problem it solves, so lines connect the prospect's fact to a relevant angle. Asked for once if missing.
- **Line style** (optional): Tone and length. Default: one sentence, under 25 words, plain, no flattery, no questions about their week.
- **Signals to use** (optional): Which sources to draw from: site, hiring, or both. Default both, preferring a dated open role over a homepage fact when the role is relevant to what you sell.
- **Where it goes** (optional): Same file or sheet with new columns, a new CSV, or a custom field for LinkedCamp, Instantly or Smartlead. Default: new columns in the source file.

## Steps

1. **Read the list and group by domain**
   Load the prospect list through your own connection to the file, sheet or sequencer. Normalise domains (lowercase, strip www and paths), drop exact duplicate rows, and build a unique domain list. Every company is scraped once and its facts are shared by all prospects there. Confirm what the user sells and the line style if either is missing, in one question.
2. **Check scrape units before spending** · `get_usage`
   Call get_usage (free) and read scrape_units. Estimate the run: unique domains times the pages scrape_company reads per domain, plus careers pages for scrape_jobs. If units are short or the account is on Free, stop and tell the user: scraping is a paid add-on in units, packs start at $9 for 1,000. Offer to run the domains that fit first, ordered as they appear in the list.
3. **Probe with one domain** · `scrape_company`
   Call scrape_company on the first domain only. Check the result has usable fields (what they sell, who they sell to, customers named, key links) and note units_used to refine the estimate. Draft one sample line and show it to the user before scraping the rest, so style problems are caught on one unit spend, not hundreds.
4. **Scrape every company site** · `scrape_company`
   Call scrape_company for each remaining unique domain. Store sells, sells_to, customers named, positioning and key links per domain. If a domain returns nothing useful, mark it no_site_facts and move on; do not retry a page that returned empty. On 429, wait for Retry-After and resume.
5. **Read careers pages for hiring signals** · `scrape_jobs`
   If hiring is in scope, call scrape_jobs for each unique domain. Keep open roles with titles and posted dates. Prefer roles posted recently and roles related to what the user sells (for example SDR or RevOps hires for a sales tool). Mark domains with no open roles as no_hiring_signal; that is a valid result, not an error.
6. **Write one line per prospect**
   For each prospect, pick the single strongest fact for their company, weighted by relevance to their title and to what the user sells. Write one line in the chosen style that states the fact accurately and links it to a reason to talk. Use only scraped facts: no guessed metrics, funding, news or compliments. Record the fact used, its source (site or careers page) and the role's posted date. If no fact fits, leave the line blank and set the reason.
7. **Return the list and report**
   Write the new columns back through your own connection to the destination, or export a CSV. Report domains scraped, units used, lines written, blanks and why, and units left from the last usage object.

## Checks before returning

- Every written line maps to a stored fact with its source and, for hiring lines, a posted date; any line without one is deleted and left blank.
- Each domain was scraped once, prospects at the same company got different lines where more than one usable fact exists, and no two lines in the file are identical.
- Scrape units used match the estimate from get_usage within reason, and the run stopped cleanly rather than half-writing rows if units ran out.
- Blank lines are explained (no_site_facts, no_hiring_signal, no_relevant_fact, scrape_failed), never silently filled with generic text.
- Email and email status columns from the input are passed through unchanged; rows marked invalid get no line and are flagged.

## Output

The original rows plus five columns: first_line, fact_used, fact_source (homepage URL or careers page), fact_date (role posted date or scrape date), and line_status (written, no_site_facts, no_hiring_signal, no_relevant_fact, scrape_failed, skipped_invalid_email). In Google Sheets the result goes to a tab named "First lines" in the source sheet; as CSV it is <source-name>-first-lines.csv; for LinkedCamp, Instantly or Smartlead, first_line maps to a custom field. This skill does not verify emails. If the input has a status column, verified, catch-all and unknown rows keep their status as given and still get lines, so the user can segment catch-alls to lower volume and treat unknown as unconfirmed; rows marked invalid are skipped and flagged. If no status is present, the report recommends running the Pre-send campaign check or Clean a list before sending skill before launch.

## Example

> Here's my Instantly export of 120 verified ops leaders. We sell inventory forecasting software. Write a first line for each from their website and open roles, and add it as a custom field.

```
✓ 120 prospects · 74 unique domains · ✓ 1,840 scrape units available
✓ 74 sites scraped · ✓ 74 careers pages read · 41 with open roles
✓ 109 lines written · 11 blank (6 no relevant fact, 3 no site facts, 2 invalid email skipped)
→ CSV "ops-leaders-first-lines.csv" ready for Instantly, first_line custom field · 512 units used
```

Illustrative output.

## Cost and limits

scrape_company and scrape_jobs use scrape units only, 1 unit per standard page, with capped page depth so each domain costs a predictable number of units. They use no search or enrichment records. Scraping is not available on the Free plan; it is an add-on on every paid plan, with packs of $9 for 1,000, $19 for 5,000 and $49 for 20,000 units that do not expire while subscribed. The skill keeps cost down by scraping each domain once and sharing facts across prospects, probing one domain first, and checking get_usage (free) before the run. On a 429 it waits for Retry-After and resumes; blocked calls count against nothing.

## What it doesn't do

- Does not find, enrich or verify contacts; it works on a list you already have and passes email statuses through as given.
- Does not invent facts, read pages behind a login, or use news, funding or personal details that the scrape did not return.
- Does not send or schedule emails; it writes the line into your file or sequencer field and leaves sending to your own tool.
