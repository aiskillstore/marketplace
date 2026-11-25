---
name: datacircle
description: "Find the best GTM API for a job, from Datacircle's sheet of every plan of every GTM API: price per 1,000, score, rate limits, speed and the fields it returns. Use when the user asks which API to use, what an API costs, or to compare GTM APIs."
---

# Datacircle

Find the best GTM APIs. We benchmark all the GTM APIs and we put the results on our website. The `datacircle` MCP server is open to anyone, with no key, and answers from the sheet.

## Tools

- `list_apis`: lists the APIs on the sheet and the number of plans and providers for each. Call it first, and pass an API's name to `search_plans`.
- `search_plans`: the sheet's rows, one for each plan of each call, each with its provider, plan, billing, $ per 1,000 (`perThousand`), score out of 100 (`score`), rate limits, speed, the fields it returns and the pages each row was read from. What each key means: https://datacircle.dev/fields

## How to answer

- Say the plan's price per 1,000 and its score, and give the pages the row was read from.
- The best plans come first, as on the sheet. Compare a few of them, not the whole list.
- The whole sheet is one file with no sign-up: https://datacircle.dev/datacircle.json (CSV: https://datacircle.dev/datacircle.csv). Its skill is https://datacircle.dev/SKILL.md.
