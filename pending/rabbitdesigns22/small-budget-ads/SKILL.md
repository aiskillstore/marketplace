---
name: small-budget-ads
description: >-
  Load before recommending to turn off, change, duplicate or add ads or ad sets in Meta Ads (Facebook/Instagram) when budgets are small (about 1-5 USD a day per ad set), typically click-to-WhatsApp or Messenger "conversations" campaigns for local businesses, often one ad set per product or service and accounts in different currencies. Also when the user asks "what should I turn off?", "who is doing badly?", "should I duplicate this?". Generic ads skills assume big budgets and statistical tests; this one gives safe decision rules for small accounts: enough data first, compare each ad set only with itself, and never break the learning phase for nothing.
license: MIT
---

# Small-budget ad decisions (Meta Ads)

Most ad advice assumes thousands per month and clean A/B tests. Small local businesses run 1-5 USD a day per ad set, one ad set per product, with conversations to WhatsApp as the result. With so little data, the usual rules ("kill anything above target CPA after 3 days") turn off good ads and reset the learning phase for nothing. These rules keep decisions safe.

## 0. Permission

- Look only, by default. Turning ads on or off, editing, duplicating, changing budgets or publishing happens only with the account owner's explicit yes, change by change ("Turn off ad 1, 2 and 3?").
- After any change, read it back in Ads Manager and show it.

## 1. Is there enough data?

- Minimum window: 7 full days since the last significant edit. With fewer days, only flag what is clearly broken and say "too few days".
- Today's data is for spotting breakage (0 impressions, rejection, payment failure), not for turning things off. One bad day is not a trend.
- The **benchmark** of each ad set is its own normal cost per conversation: its last 30 days before the period you judge (if it is new, the period itself). Never another ad set's benchmark, and never only the bad period: if the whole ad set dropped, its current average hides the problem.
- An ad can be called "bad" only after spending at least **2x the benchmark**. Below that, zero conversations means nothing.
- Example: an ad set normally costs 10 per conversation. An ad at 14 is 1.4x: keep it. An ad that spent 30 with 0 conversations is 3x: turn it off.
- Always read the account currency, and check that ads add up to the ad set and ad sets add up to the campaign.

## 2. Compare like with like

- Each ad against the average of its own ad set. Each ad set against itself (its past weeks) or against ad sets of the same product.
- Never one product against another (roof repair vs general services, preschool vs high school). Don't recommend moving money from one product's ad set to another just because it is cheaper, and don't remove ad sets the business wants to keep even if they cost more.

## 2b. How the account is built (the technique)

Small budget, and new ads always competing. Structure that works:
- **One ad set = one product or service**, each with its own small daily budget.
- **Different goals never share a campaign.** For example, a "recruit new resellers" campaign (videos about the opportunity) and a "sell the product" campaign stay apart. If a client can only afford one ad set, it carries whatever is working best.
- **A local service business with one star service** can run two campaigns for that service (it wants many of those jobs) and one for everything else.
- **Only matching pieces go in each ad set.** Before adding a piece, open its preview and confirm it is about that ad set's product or service. A roof photo never goes in "general services"; a recruitment video never goes in "sales".

## 2c. "Not tested" is not "lost"

Meta gives almost all of an ad set's spend to its current winner. In real small accounts, over 7 days the winning ad took about 95-99% of its ad set's budget. So:
- A new ad that spent less than 2x the ad set's benchmark is **not tested**, not a loser. Don't turn it off for being "bad".
- If it still gets no spend after two review cycles (for example two weeks), replace it with another piece of the same product: there should always be new ads competing.
- **Judge by spend, not by week.** With minimum budgets an ad set gets anywhere from 1 to 50 conversations a week; the 2x-benchmark rule decides.
- **Add new ads together, on a fixed day of the week**, right after turning off the losers. Never one per day.
- **Duplicate the ad inside the ad set, not the ad set.** A duplicated ad set restarts learning and often costs far more per conversation than the original.
- **Use posts that already exist on the page** ("Use existing post") so ads keep their likes and comments as social proof. First this week's posts, then ones that worked before; organic posts count too.

## 3. What to recommend (in this order)

| What you see (with enough data) | Recommendation |
|---|---|
| Ad spent ≥ 2x its ad set's benchmark with 0 conversations, or costs ≥ 2x the benchmark | Turn off that ad |
| Turning it off would leave fewer than 2 active ads | Don't just turn it off: replace it with a new piece for the same product (Meta recommends 2-3 ads per ad set) |
| Whole ad set ≥ 2x its own benchmark | Add 1-2 genuinely new pieces to the same ad set (a different idea, not the same photo with new text) |
| High frequency (≈5+) and cost rising week over week | New piece; first rule out budget changes, payments, edits and seasonality |
| Ad "Active" with 0 impressions for 48 h+ | Not the creative: check the Ad Library (is it really running?), billing (balance, card, limit), account quality, then the ad set settings |
| New ad that spent less than 2x the benchmark (Meta barely gave it money) | Don't turn it off: "not tested". If nothing changes after two review cycles, replace it with another piece of the same product |
| Cheap ad with volume | Don't touch it. Make variations of that idea for other ad sets of the same product |

## 4. What NOT to recommend

- Duplicating ad sets or campaigns to "fix" them: duplicates restart learning from zero.
- Leaving a single ad in an ad set.
- Editing the creative or the audience of an ad that works or is in review: it goes back to review and learning. Budget changes don't send it to review, but big jumps can reset learning: raise 20-30% every 3-5 days.
- Adding new ads one per day: adding ads is also a significant edit. Batch them and add them once.
- Cost caps or bid limits in ad sets with fewer than 50 conversations.
- Criticizing repeated ad names ("1 - Copy 9"): they are often different pieces. Open the preview to know which piece it is.

## 5. New pieces

Brief whoever makes creatives with: the product (ad set), the winning piece and why (preview opened), the losing piece, and 2-3 different ideas. With small budgets a creative test is a screening test, not a statistically significant test: say so.

Respect ad policies: no misleading before-and-after, no health promises, no personal attributes of the viewer, no third-party brands.

## 6. How to report

One short answer: what to do first, then one line of why per item, and close with the permission question ("Turn off 1 and 2?"). Amounts in the account's currency. Anything you could not see: say "I couldn't see it".
