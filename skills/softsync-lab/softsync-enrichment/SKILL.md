---
name: softsync-enrichment
description: "Look up facts about a company or person from a website, work email, LinkedIn profile or organisation number, and save them. Use when a record is missing details such as industry, size, title or contact info."
---

<!-- Generated from the SoftSync API skills. Edit them there and re-export. -->

# Enrichment

`enrich` looks a company or person up in public registers and data providers and compares the result with matching records.

## Order of operations
1. Preview first (the default). Show the user what was found and what differs from their records.
2. Save only when asked. "Fill" fills empty fields and creates missing company or contact records; "overwrite" replaces only the fields the user confirmed. Pass the preview's lookup id so nothing is looked up twice.

## Finding new companies to sell to
1. `find_leads`: how many companies match, by country, size, industry, keywords and so on. The counts are free and it adds nothing. Only ask it to show companies when the user wants to see them; each one shown costs a credit.
2. `add_leads`: adds the companies from the same search to the CRM, up to the limit asked for (at most 100), with key people and their work emails if wanted. Companies already in the CRM are left out.
3. `find_lookalike_companies`: finds up to 10 companies like ones the user already has (their records or websites) and adds them.
Run `find_leads` first so the user knows how many match, say what it will cost, and wait for a clear yes before `add_leads` or `find_lookalike_companies`.

## Rules
- A personal email address alone is not enough; ask for the website, organisation number or LinkedIn profile.
- Ask for email addresses only when the user wants them.
- Each source that finds something costs one enrichment credit. Repeating a lookup within an hour is free.
- Adding companies costs 1 credit each, 2 per person and 10 per email found. Give the number before you start.
