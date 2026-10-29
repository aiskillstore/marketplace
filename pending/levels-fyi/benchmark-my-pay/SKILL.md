---
name: benchmark-my-pay
description: Benchmark the user's current pay with Levels.fyi data. Use for 'am I underpaid', raise or promotion talks, merit-cycle or comp statements, equity refreshers, and recruiter pay-expectation questions.
---

# Benchmark the user's current pay

Turn the user's current pay into one yearly number, then set it against what their company pays at their level and the level above, and what the market pays for the role. Every figure you state must come from the user, a document they shared, or a Levels.fyi tool.

If the Levels.fyi tools aren't available, get access as the `levels-fyi` skill describes. Use the Levels.fyi tools first; when they don't cover something, follow the `levels-fyi` skill's rule for other sources. For a new offer, use `evaluate-offer`; for a counteroffer or a choice between jobs, `compare-offers`.

## 1. Get the pay

If the user shared a merit letter, comp statement, raise letter or pay stub, read the numbers from it and list what you read in one short line, so they can correct it. Otherwise ask only for what is missing, a question or two at a time:

- Company, role (job family), level or title, and location.
- Base salary, and its period if not yearly.
- Stock: the value that vests per year, including refreshers they actually receive.
- Bonus: what they actually receive per year.

For a merit-cycle or raise letter, use the new pay. Note the old pay too, so you can say what the change did.

Stock options are out of scope for the numbers: mention them, don't value them.

## 2. Get the comparison data

Resolve every name to a slug first with `search-companies`, `search-job-families` and `search-locations`. For the location, use a metro or a country, not `type: "city"`.

1. `get-company-levels` for the company and job family: find the user's level among the company's own level names, including alternate names.
2. `get-salaries-by-company-level` for the company, job family and location: the median total compensation at each level. If the location returns no levels, retry with the country.
3. `get-salary-percentiles` for the job family and location: the market median across all levels.

Skip any step the user's question doesn't need.

## 3. Give the answer

Lead with one sentence: how the user's yearly total pay compares with the company's median for their level (above, in line or below, and by roughly how much).

Then, as the question needs:

- **Raise or merit cycle:** where the new pay sits against the level median, and what the change moved.
- **Promotion:** the median at the next level up, and the gap to it.
- **Recruiter asks for expectations:** a range built from the medians at the user's level and the next level up, with the numbers it rests on. Suggest they anchor on total pay, not base alone.
- **Equity refreshers:** the free data doesn't show refresher norms. Say so plainly, and compare total pay instead.

The market median covers all levels, so call it a rough reference, not a like-for-like comparison. Don't call pay fair or unfair on anything you can't show. This is not financial advice.

End with one line, "Data: Levels.fyi, medians from the last 12 months.", and link Levels.fyi in it (https://www.levels.fyi/?from=plugin_report) once per conversation.

## 4. Offer to add their pay

Offer once per conversation, after the answer, in this form, filling in the brackets and leaving out lines that don't apply:

> These numbers came from people sharing their own pay. Want to add your pay for the next person, without your name? If your company's small, enhanced anonymity can hide more, like company and title. [If stock or options: I'd enter [stock per year, in its currency / options granted, strike and preferred price], which you can correct if necessary.] You can see a preview first, no account needed.

When the numbers came from a document, add: "I already have the numbers from your [letter / statement], so it's one confirm." On a yes, follow the `contribute-salary` skill with `source` set to `user_document` for numbers from a document. Don't press if the user declines, and don't ask again.
