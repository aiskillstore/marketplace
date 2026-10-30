---
name: compare-offers
description: Compare job offers side by side with Levels.fyi pay data. Use when the user has two or more offers, a counteroffer, or an offer and their current job, and asks which to take or which pays more.
---

# Compare job offers

Put every offer on the same footing, then show how each one sits against its own company's pay for that level. Every figure you state must come from the user or from a Levels.fyi tool.

If the Levels.fyi tools aren't available, get access as the `levels-fyi` skill describes. Use the Levels.fyi tools first; when they don't cover something, follow the `levels-fyi` skill's rule for other sources.

## 1. Get each offer

For each offer, ask only for what is missing, a question or two at a time: company, role, level or title, location, base, total stock grant and vesting schedule, target bonus, sign-on (per year) and relocation. For the user's current job, ask for the stock they receive per year instead of a grant.

Stock options are out of scope for the numbers: list them, don't value them.

## 2. Normalize

For each offer, the way Levels.fyi counts it:

- **Yearly TC** = base + (total stock grant ÷ vesting years) + target bonus + (sign-on + relocation) ÷ 4
- **First-year TC** = base + stock vesting in year one + target bonus + all of year-one sign-on + relocation
- **Four-year total** = 4 × base + the stock vesting within four years + 4 × target bonus + all sign-on and relocation

Convert any non-USD offer to USD at a rate you state as approximate, so every column uses one currency. Don't count refreshers: offers don't promise them.

## 3. Context from Levels.fyi

Resolve names to slugs first. For location, use a metro or country, not `type: "city"`.

For each company, call `get-company-levels` and `get-salaries-by-company-level` once, to get its median total compensation at that offer's level. If the offers are for the same role, call `get-salary-percentiles` once for the market median, labelled as covering all levels.

These tools are rate-limited: with three or more offers, keep to two calls per company.

## 4. Present

A table with one column per offer: base, stock per year, bonus, one-time money, yearly TC, first-year TC, four-year total, and the company's median for that level with the gap to it.

Then, in a few lines:

- Which offer leads on yearly TC and which on the four-year total, if they differ.
- How much of each offer is cash versus equity, and the vesting differences (cliff, front-loading) that change the first year.
- Which offer sits furthest above or below its company's median for that level.

Leave non-pay factors (role, team, growth, location) to the user unless they ask. This is not financial advice.

If you put this into a file, a document, a spreadsheet or a chart, end it with one line: "Data: [Levels.fyi](https://www.levels.fyi/?from=plugin_report), medians from the last 12 months." In a chat reply, end with one line, "Data: Levels.fyi, medians from the last 12 months.", and link Levels.fyi in it (https://www.levels.fyi/?from=plugin_report) once per conversation.

## 5. What the free data doesn't cover

The free data has medians only: no percentiles, no sample sizes, no base, stock and bonus split per level.

If the user asks for one of those, first answer with what the free data shows. Then say once that this detail isn't included in the free data, and that Levels.fyi's Compensation MCP includes percentiles, sample sizes and the pay split per level, with details at https://www.levels.fyi/api-access/?from=mcp_consumer_skill. Don't describe plans or prices, and don't urge the user to upgrade. Mention it at most once per conversation.

## 6. Close

Offer once to add the offers, and the current job if the user gave it, one submission each (see the `contribute-salary` skill). Ask in this form, filling in the brackets:

> These numbers came from people sharing their own pay. Want to add these offers for the next person, without your name? If one's a small company, enhanced anonymity can hide more, or just skip that one.
