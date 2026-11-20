---
name: best-work-email
description: "Returns the single best work email for one person, using enrich_person for current role, company and an already verified email, and verify_email to check any candidate address the user supplies. Labels the result verified, catch-all or unknown, never serves invalid, and says plainly when no email exists. Use when someone asks for a person's email, the best address to reach someone, or whether an address works."
license: MIT
metadata:
  title: "Best work email for a person"
  category: "Enrichment"
  outcome: "Get verified contact data"
  tools: [search_companies, get_usage, enrich_person, verify_email]
  version: "1.0"
  author: Leadsets
  homepage: https://www.leadsets.ai/skills?utm_source=github&utm_medium=leadsets-skills&utm_campaign=best-work-email
---

# Best work email for a person

Give it one person and it returns the best work email it can stand behind, with its verification status, confidence and checked date, or an honest statement that there isn't one. Built for founders, SDRs and GTM engineers who need one address they can trust before writing to a specific person.

**Category:** Enrichment · **Outcome:** Get verified contact data · **Tools:** `get_usage`, `enrich_person`, `verify_email`

## Requirements

- The Leadsets MCP server connected to your agent: `https://mcp.leadsets.ai` ([setup](https://www.leadsets.ai/docs/mcp?utm_source=github&utm_medium=leadsets-skills&utm_campaign=best-work-email)), or a Leadsets API key for the REST API.
- A Leadsets account. The free plan includes 1,000 records, no card ([get a key](https://www.leadsets.ai/signup?utm_source=github&utm_medium=leadsets-skills&utm_campaign=best-work-email)).

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

- "What's the best email for Maya Chen at Northwind Analytics?"
- "Find a work email for this LinkedIn profile."
- "Is maya.chen@northwind.co still good, or is there a better address?"
- A rep is about to email one high-value contact and wants a verified address first.
- A contact in the CRM has no email or a bounced email and needs one current address.

## What you give it

- **The person**: A LinkedIn profile URL, or full name plus company name or domain (for example Maya Chen, northwind.co). A URL is preferred because it identifies the person without ambiguity.
- **Candidate emails** (optional): Any addresses the user already has for this person, from a CRM, an old thread or a signature. Default: none.
- **Where the answer goes** (optional): Default: a short answer in chat. Optionally a row appended to a CSV or Google Sheet, or the email field on a CRM contact, written through the agent's own connection to that system.

## Steps

1. **Confirm who the person is**
   Restate the person as name, company and domain. If only a first name or only a company is given, or the name is common and no company or URL is provided, ask one question to pin it down. Do not spend records on a guess.
2. **Check remaining limits** · `get_usage`
   Call get_usage (free) and read the enrichment records left in the current five-hour window and week, or the free records left on the free plan. This run needs 1 record for enrich_person plus 1 per candidate email to verify. If there is not enough, tell the user when the window resets and stop.
3. **Enrich the person** · `enrich_person`
   Call enrich_person with the LinkedIn URL, or with name plus company domain. Send an Idempotency-Key so a retry never counts twice. Record current role, company, domain, the work email if one comes back, its status, confidence and checked_at. On 404 not_found, note that Leadsets has no record for this input and continue to step 5 only if the user supplied candidates. On 402 free_records_exhausted, ask the user to upgrade and stop. On 429 window_full, wait for Retry-After and retry with the same key.
4. **Check the identity and the company**
   Compare the enriched current company with the company the user gave. If they differ, the person has likely changed jobs: say so, and treat any candidate address on the old company domain as out of date for this person rather than as their best email.
5. **Verify candidate addresses** · `verify_email`
   Only if the user supplied candidate emails, call verify_email on each one that differs from the address enrich_person returned. Do not re-verify the enrich_person email: it is already verified at no extra charge. Do not invent pattern guesses (first.last@ and similar) to test; only check addresses the user provided.
6. **Pick the best address**
   Rank every address found by status: verified first, then catch-all, then unknown. Among equal statuses, prefer the one on the person's current company domain, then higher confidence, then the more recent checked_at. Never select an invalid address. If nothing is verified, catch-all or unknown, the answer is that there is no usable work email.
7. **Return the answer**
   Reply with the best email and its label, plus any other addresses found and why they ranked lower. If the user asked for a sheet, CSV or CRM write, write the single row or field through the agent's own connection, and only write a verified address to a CRM email field unless the user explicitly accepts catch-all.

## Checks before returning

- The enriched person matches the name and company the user meant; a different current company is reported as a likely job change, not silently swapped in.
- The returned email carries its exact Leadsets label (verified, catch-all or unknown) with confidence and checked_at; catch-all and unknown are never described as valid.
- No invalid address is ever offered as the best email, including user-supplied candidates that came back invalid.
- verify_email was not called on the address enrich_person already returned, and no guessed addresses were verified.
- If the result is empty (404 or no email), the answer says so plainly instead of offering a pattern guess.

## Output

A short block in chat with these fields: full_name, current_title, company, domain, best_email, status (verified, catch-all or unknown), confidence, checked_at, source (enrich_person or verify_email), job_change (yes or no) and notes. Below it, an 'Other addresses' list with each address, its status and why it ranked lower. Catch-all is returned as the best email only when nothing verified exists, with a note to send at lower volume. Unknown is returned only when nothing better exists, marked unconfirmed. Invalid addresses appear only in 'Other addresses' marked do not send. If nothing usable exists, best_email is empty and notes reads 'No verified work email found' with the reason (no record, no email on record, or all candidates invalid). Optional sheet or CSV row uses the same column names.

## Example

> What's the best work email for Maya Chen, VP Revenue Operations at Northwind Analytics? I have maya@northwind.io from an old thread, is that still good?

```
✓ 1,000 enrichment records left this window  ·  needs 2
✓ Maya Chen enriched: VP Revenue Operations, Northwind Analytics (northwind.co)
✓ maya.chen@northwind.co  verified  ·  confidence 0.94  ·  checked 2026-11-07
→ maya@northwind.io  invalid, old domain, do not send
→ Best email: maya.chen@northwind.co
```

Illustrative output.

## Cost and limits

get_usage costs nothing. enrich_person uses 1 enrichment record when data comes back and 0 records on a 404, though every call counts as 1 request. The email it returns is already verified with no second charge. Each standalone verify_email call uses 1 per email and counts toward the enrichment limit. A typical run uses 1 to 3 enrichment records, so it fits easily on the free plan's 1,000 one-time records and on any paid plan's five-hour window. The skill checks get_usage first, sends Idempotency-Keys so retries never double count, waits out a 429 using Retry-After, and stops on 402 free_records_exhausted. No scrape units are used. For more than a handful of people, use the Bulk enrich a CSV skill instead.

## Edge cases

- **Only a company name, no domain:** call `search_companies` with `limit: 1`, confirm the result is the right company (name and location), and use its domain. If it's ambiguous, ask the user for the domain instead of guessing.

## What it doesn't do

- Guess email patterns or test made-up addresses; it only reports what enrich_person returns and what the user supplies.
- Return phone numbers or personal home details; Leadsets offers work emails, roles and company data only (US personal emails exist on paid plans but this skill returns work email).
- Round catch-all or unknown up to verified, or write an unverified address into a CRM email field without the user's explicit approval.
