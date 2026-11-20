---
name: role-address-filter
description: "Flags role and shared inboxes such as info@, sales@ and support@ in a contact list, verifies every address with verify_email, and uses search_people to find a named person at each company behind those inboxes. Returns a cleaned list with honest email labels. Use when someone asks to remove generic inboxes, replace info@ addresses with real people, or find who sits behind sales@ before a campaign."
license: MIT
metadata:
  title: "Role-address filter"
  category: "Email verification"
  outcome: "Get verified contact data"
  tools: [get_usage, verify_email, search_people]
  version: "1.0"
  author: Leadsets
  homepage: https://www.leadsets.ai/skills?utm_source=github&utm_medium=leadsets-skills&utm_campaign=role-address-filter
---

# Role-address filter

Takes a contact list full of info@, sales@ and hello@ addresses and returns one where each shared inbox is flagged and, where possible, replaced by a named person with a verified work email. Built for founders, SDRs and GTM engineers whose lists came from form fills, scraped directories or old CRM imports and who want to reach a person instead of a queue.

**Category:** Email verification · **Outcome:** Get verified contact data · **Tools:** `get_usage`, `verify_email`, `search_people`

## Requirements

- The Leadsets MCP server connected to your agent: `https://mcp.leadsets.ai` ([setup](https://www.leadsets.ai/docs/mcp?utm_source=github&utm_medium=leadsets-skills&utm_campaign=role-address-filter)), or a Leadsets API key for the REST API.
- A Leadsets account. The free plan includes 1,000 records, no card ([get a key](https://www.leadsets.ai/signup?utm_source=github&utm_medium=leadsets-skills&utm_campaign=role-address-filter)).

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

- "Flag the info@ and sales@ addresses in this list and find a real person at each company."
- "Half my CRM contacts are generic inboxes. Who should I email instead?"
- "Clean this CSV before I load it into Instantly, and swap role addresses for named contacts."
- A list or campaign is about to launch and contains shared inboxes like support@, contact@ or team@.
- An inbound form or event export captured company inboxes instead of personal work emails.

## What you give it

- **Contact list**: A CSV, Google Sheet, CRM view or pasted list with at least an email column. Company name and domain are optional; the domain is taken from the email if missing.
- **Who to find behind each inbox** (optional): The function and seniority to look for. Default mapping: sales@ and info@, hello@, contact@ map to revenue at head or director level; marketing@ to marketing; billing@ and accounts@ to finance; hr@, jobs@ and careers@ to hr; support@ to ops. Override with your own buyer role in plain language.
- **People per company** (optional): How many named people to return per domain. Default 1, maximum 3.
- **Where it goes** (optional): Same place it came from by default (a new tab, a new CSV, or flagged fields through the agent's own CRM connection). Leadsets only supplies the data.

## Steps

1. **Parse the list and flag role addresses**
   Read the list through the agent's own connection to the file, sheet or CRM. Lowercase emails, drop exact duplicates and note them. Flag an address as a role address when the local part is a shared inbox (info, sales, hello, contact, support, team, admin, office, marketing, billing, accounts, hr, jobs, careers, enquiries, press and similar). Group flagged rows by domain so each company is searched once. Show the user the count of role addresses and the role mapping you will use, and ask one question only if the target role is unclear.
2. **Check limits and plan the run** · `get_usage`
   Call get_usage (free). verify_email counts toward enrichment at 1 per email; search_people uses 1 search record per person returned. Estimate: enrichment needed = total unique emails; search needed = flagged domains x people per company. If either exceeds what is left in the five-hour window or week, tell the user, then split the run into batches or offer to verify the role addresses only. On the free plan, remember both draw from the same 1,000 one-time records.
3. **Verify every address** · `verify_email`
   Call verify_email on all unique emails, role and personal alike, in batches. Record status (verified, catch-all, unknown, invalid), confidence and checked date per address. The first waterfall step also checks role and disposable addresses, so keep any role signal it returns alongside your own flag. For large lists on a paid plan, submit a bulk async job and poll it rather than looping single calls. On 429 window_full, wait for Retry-After and retry with the same Idempotency-Key (REST API); on 402 free_records_exhausted, stop and ask the user to upgrade.
4. **Probe the people search** · `search_people`
   Take one flagged domain and call search_people with company_domain set to that domain, the mapped function and seniority, and limit 1. Confirm the result is at the right company and that match_reasons reflect the role you asked for. If it returns nothing, widen seniority (add manager or c_level) before running the full set, and note that the empty probe used no records.
5. **Find a named person behind each inbox** · `search_people`
   For each flagged domain, call search_people with company_domain, the mapped function and seniority, has_verified_email true, and limit set to people per company. Respect concurrent search limits (3 on Solo, 5 on Pro, 8 on Team and Max); on 429 too_many_concurrent, wait for a running search to finish. Skip any person whose email is already in the list. If a domain returns no one with a verified email, retry once with has_verified_email false and keep any result only with its returned status, never upgraded.
6. **Assemble and deliver the cleaned list**
   Build the output tabs described below. For each replaced role address, keep the original row and add the named person with title, email, status, checked date and match reasons. Write results to the chosen destination through the agent's own connection. Do not delete or overwrite original CRM records; add flags or new contacts instead. Report counts and anything unconfirmed.

## Checks before returning

- Every row has exactly one verification status; no catch-all or unknown address appears in the send-ready tab, and no invalid address appears as a contact anywhere.
- Each flagged domain was searched once, and no suggested person duplicates an email already in the list.
- Each suggested person's company domain matches the role address domain, and match_reasons support the requested function and seniority.
- Domains with no named person found are listed explicitly rather than silently dropped.
- Records spent are compared against the get_usage plan, and any batch left unfinished because of a 429 or weekly limit is reported with its reset time.

## Output

Four tabs or files. 1) "Send-ready": original non-role contacts with status verified, plus the named replacements with status verified. Columns: email, first_name, last_name, title, company, domain, status, confidence, checked_at, source (original or replaces:<role address>), match_reasons. 2) "Role addresses": every flagged inbox with its status and the named person found (or "none found"). 3) "Catch-all and unknown": addresses labelled catch-all (send at lower volume) or unknown (unconfirmed), kept separate and never marked valid. 4) "Removed": invalid addresses and duplicates, with the reason. A short summary lists counts per tab and records used.

## Example

> Here's our webinar export from Google Sheets, about 400 emails. Flag the info@ and sales@ style addresses and find the head of sales or RevOps at each of those companies instead. Put the result in a new tab.

```
✓ 412 emails parsed · 9 duplicates removed · 87 role addresses on 81 domains
✓ 403 verified by verify_email: 268 verified · 41 catch-all · 22 unknown · 72 invalid
✓ 81 domains searched · 63 named people found (e.g. Maya Chen, VP Revenue Operations, Northwind Analytics)
✓ 18 domains with no named person (listed in "Role addresses")
→ Tabs "Send-ready", "Role addresses", "Catch-all and unknown", "Removed" added
```

Illustrative output.

## Cost and limits

verify_email uses 1 enrichment record per email and counts toward the enrichment five-hour and weekly limits. search_people uses 1 search record per person returned; an empty search uses no records but still counts as one request. get_usage is free. The skill calls get_usage first, searches each domain once, caps people per company (default 1), and probes with limit 1 before the full run. If a run would cross a window it splits into batches or uses a bulk async verify job on paid plans. Over a limit, Leadsets returns 429 with Retry-After and the blocked call counts against nothing; retries reuse the same Idempotency-Key so nothing is counted twice. No scrape units are used, so the skill runs on the free plan's 1,000 one-time records.

## What it doesn't do

- Guess or construct email addresses from name patterns; it only uses emails Leadsets returns, with their labels.
- Send email, delete CRM records, or load a sequencer; it hands a cleaned list to the tool you already use.
- Read team or contact pages on company sites; use the Team page to contacts skill for that.
