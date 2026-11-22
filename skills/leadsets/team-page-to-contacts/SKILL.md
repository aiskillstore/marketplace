---
name: team-page-to-contacts
description: "Reads a public company team or about page with scrape_company, pulls out the people listed, enriches each one with enrich_person and checks every email's status, returning a contact list segmented by verification label. Use when someone says \"get contacts from this team page\", \"who works at parcelry.co and what are their emails\", or \"turn this about page into a list\"."
license: MIT
metadata:
  title: "Team page to contacts"
  category: "Web scraping"
  outcome: "Get verified contact data"
  tools: [get_usage, scrape_company, enrich_person, verify_email]
  version: "1.0"
  author: Leadsets
  homepage: https://www.leadsets.ai/skills?utm_source=github&utm_medium=leadsets-skills&utm_campaign=team-page-to-contacts
---

# Team page to contacts

Turns the people named on a company's public team page into a contact list with current roles and labelled work emails. Built for founders, SDRs and GTM engineers working small target accounts where the team page is the fastest map of who is there.

**Category:** Web scraping · **Outcome:** Get verified contact data · **Tools:** `get_usage`, `scrape_company`, `enrich_person`, `verify_email`

## Requirements

- The Leadsets MCP server connected to your agent: `https://mcp.leadsets.ai` ([setup](https://www.leadsets.ai/docs/mcp?utm_source=github&utm_medium=leadsets-skills&utm_campaign=team-page-to-contacts)), or a Leadsets API key for the REST API.
- A Leadsets account. The free plan includes 1,000 records, no card ([get a key](https://www.leadsets.ai/signup?utm_source=github&utm_medium=leadsets-skills&utm_campaign=team-page-to-contacts)).

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

- The user pastes a team, about or leadership page URL and asks for the people on it with emails.
- "Who's on the Stackfold team and how do I reach them?"
- An account has no clear decision-maker in search results, but its website lists the team.
- The user wants to check whether people named on a company site still work there before reaching out.
- A handful of target domains need a named-contact list built from their own sites.

## What you give it

- **Company domain or team page URL**: A domain like parcelry.co or the direct URL of a public team, about or leadership page. One domain per run unless the user lists several.
- **Roles to keep** (optional): Which people to enrich, for example founders, sales, RevOps or anyone at director level and up. Default: everyone listed on the page.
- **Where it goes** (optional): CSV, Google Sheets, or a CRM or sequencer the agent is already connected to. Default: CSV.

## Steps

1. **Confirm the target and the role filter**
   Restate the domain or URL and which roles to keep. Ask one question only if the page or filter is ambiguous, for example when a domain has several regional sites. Confirm the page is public; never ask for logins or paywalled pages.
2. **Check limits and scrape units** · `get_usage`
   Call get_usage, which costs nothing. Read scrape_units and the enrichment meters (records per 5 hours and per week). Scraping is not on the Free plan; if scrape units are zero or the account is on Free, stop and tell the user scraping needs a paid plan with a scrape unit pack. If the expected number of people exceeds enrichment records left in this window, plan to split the run.
3. **Read the team page** · `scrape_company`
   Call scrape_company on the team page URL or domain. Read pages_read and units_used from the response and report them. Extract every person named with the title shown on the page, plus any email addresses printed on it. If no people are found, say so and stop rather than guessing from other pages.
4. **Clean and filter the names**
   Remove duplicates (same person on several pages), drop entries that are not people (advisors' firms, investor logos, role inboxes like info@ or careers@), and apply the role filter. Keep the page URL as the source for each person.
5. **Probe one enrichment, then enrich the rest** · `enrich_person`
   Call enrich_person for the first person using their name and the company domain, and check the returned company matches the target domain before continuing. Then enrich the remaining people, pacing against the usage object in each response. A 404 not_found means nothing to enrich: record it and move on, it uses no records. On 429 window_full, wait for Retry-After and retry with the same Idempotency-Key (REST API); on weekly_limit, stop and report where to resume.
6. **Verify emails that did not come from enrichment** · `verify_email`
   Emails returned by enrich_person are already verified, so do not re-check them. Call verify_email only on addresses printed on the team page or supplied by the user that enrichment did not return. Record each status: verified, catch-all, unknown or invalid, with its confidence.
7. **Segment and deliver**
   Build the table, split it into verified, catch-all and unconfirmed segments, write it to the chosen destination through the agent's own connection to that system, and report counts, units used and anything it could not confirm.

## Checks before returning

- Every enriched person's current company matches the target domain; anyone whose current role is elsewhere is flagged as possibly moved on, not listed as a contact there.
- No duplicate people across pages, and no role inboxes in the contact rows.
- Invalid emails are excluded from all contact segments; catch-all and unknown are never labelled verified.
- Scrape units used and enrichment records spent match the run plan, and any person skipped for limits is listed for a later run.
- An empty page or zero matches is reported plainly instead of padded with search results.

## Output

A table with one row per person: full_name, title_on_page, current_role, company, domain, work_email, email_status, confidence, checked_at, source_url, notes. Three segments (tabs in Sheets, separate files for CSV): "Verified" for verified emails; "Catch-all" for catch-all addresses, to send at lower volume; "Unconfirmed" for unknown emails, people with no email found and people who appear to have left. Invalid emails are never written as contacts; they are counted in the summary. The summary also lists pages read, scrape units used and enrichment records used.

## Example

> Pull everyone on parcelry.co's team page who works in sales, ops or leadership, find their work emails and give me a CSV.

```
✓ Team page read · 6 scrape units used · ✓ 4,820 enrichment records left this window
✓ 24 people listed · 19 kept after role filter
✓ 15 enriched · 12 verified · 2 catch-all · 1 unknown · 4 not found
→ parcelry-team.csv created, 3 segments (1 person flagged as moved on)
```

Illustrative output.

## Cost and limits

scrape_company uses 1 scrape unit per standard page with capped page depth, so one domain costs a predictable number of units; scraping is an add-on on paid plans and not available on Free. enrich_person uses 1 enrichment record per person returned with data, and its emails are already verified at no extra cost. Standalone verify_email counts toward the enrichment limit, so it runs only on emails enrichment did not supply. Not-found and empty results use no records but count as requests. The skill calls get_usage first, reads the usage object as it goes, splits runs that would cross a five-hour window, and honours Retry-After on 429.

## What it doesn't do

- Read pages behind a login, paywalled content or anything other than public company pages.
- Guess or construct email addresses from name patterns; it only returns what enrichment or verification confirms.
- Send outreach or write to a CRM by itself; Leadsets supplies the data and the agent's own connection handles delivery.
