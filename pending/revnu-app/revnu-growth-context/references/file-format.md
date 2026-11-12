# `.agents/revnu-growth.md` format

Every `revnu-*` skill reads this file and some append to it. Keep the headings
exactly as below so they can find what they need. Leave a section with
`Unknown. <what would answer it>` rather than deleting it.

```markdown
# Growth context: <Business name>

Updated: <YYYY-MM-DD> · Version: <n>
Site: <https://...> · Also read: <imported file and date, or "none">

## The business in one paragraph
<What it is, for whom, and the outcome they get, in the user's words. 3-4
sentences, each tagged.>

## Who buys
- Buyer: <role> at <company type, size, stage, or consumer segment> [tag]
- What makes them look now: <the trigger: a hire, a deadline, a tool breaking,
  a new rule> [tag]
- Who has bought or used it so far: <names only if confirmed, else counts or
  "none yet"> [user, date]
- Not for: <who should not buy, and why> [tag]

## The problem, in their words
- "<exact quote>" (<where: support email, review on G2, sales call, Reddit
  thread URL>) [tag]
<If no real quotes exist yet: "None collected yet." Never paraphrase into a
fake quote.>

## What we sell and what it costs
- Offer: <product, plans> [site: /pricing, date]
- Price: <amounts, billing period, free plan or trial terms> [site: /pricing, date]
- How people start: <signup, demo, waitlist, install command> [tag]

## Alternatives buyers compare us with
- <Name or approach> — chosen when <situation>; we're chosen when <situation> [tag]
<Include "do nothing" or "a spreadsheet" if that's the real competitor.>

## Proof we can use
- <Customer, quote or number> — permission: <public / ask first / internal
  only> [tag]
- Claims on site not yet confirmed: <list> [site: page, date]

## How we sound
- <3 rules read from copy the user likes or wrote, each with a real example
  line and its source>
- Never say: <words, claims, comparisons> [user, date]

## Facts AI answers and listings should get right
- Name: <exact, including capitalization>; also known as: <old names>
- Not to be confused with: <namesakes, with their domains>
- Category: <the shelf buyers look on, in their words>
- URL: <canonical> · Pricing page: <URL> · Docs: <URL>
- Founded: <year> · Based in: <city/country or "remote"> · Status: <beta, GA>
- Official profiles: <GitHub, LinkedIn, G2, Crunchbase, app store, npm ...>
<Each with a source. revnu-fix-ai-claims and revnu-get-listed use this block
as the truth.>

## Goal and channels
- Goal now: <e.g. first 10 paying customers by <date>> [user, date]
- The action that counts: <signup, demo booked, install, purchase> [tag]
- Channels in use: <channel — since when — who runs it> [tag]

## Open questions
1. <Question> — <why it matters, which skill needs it>

## Tried and learned
| Date | Skill or person | What we did | Result | Next check | Status |
|---|---|---|---|---|---|
| <YYYY-MM-DD> | <revnu-get-listed / founder> | <one line> | <number, n, window, or "none yet"> | <date or condition> | <open / keep / retest / dropped> |

### Older
- <date> <one-line summary of a closed or dropped row>

## Changes
- <YYYY-MM-DD> v<n>: <sections changed and why>
```

## Notes on filling it

- **One fact per bullet, one tag per fact.** If two sources disagree, keep both
  bullets and add an open question.
- **Prices change.** Always date the pricing line. Skills that write public
  copy re-check the live pricing page if the date is older than 30 days.
- **Quotes stay verbatim**, including typos. Remove only personal data.
- **Proof needs permission.** A logo on the site is not permission to name the
  customer in an outreach email; ask.
- **"Not for" is about fit, not refusal.** Write who the product serves badly,
  not tasks the agent must refuse. If the user later asks for work outside it,
  the request wins.
- **Keep it under about 200 lines.** Past that, other skills skim it. Move
  history to `### Older` and drop superseded bullets after noting them in
  `## Changes`.
