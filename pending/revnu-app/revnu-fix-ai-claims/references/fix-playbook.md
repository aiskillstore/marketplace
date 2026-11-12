# Fix playbook

Fix the source a claim came from, in this order: pages the user owns, then
profiles they control, then other people's pages. Engine feedback buttons come
last and are optional.

## Own site

**Put each fact on one page that owns it.** Price on the pricing page, plan
limits on the pricing page or a plan comparison, integrations on an
integrations page, company facts on the about page. Other pages link there
instead of restating numbers that will drift.

**Write the fact the way the question is asked.** If the wrong answer is "no
free plan", the pricing page should say in a sentence near the top: "<Name>
has a free plan: <limits>. Paid plans start at <price>/month." A price inside
an image or only in a toggle widget is harder for any reader to quote.

**Make it readable without JavaScript.** Check the fact is in the HTML the
server returns (`curl -s <url> | grep -i "<fact>"`). If it only appears after
client-side rendering, move it into server-rendered or static output.

**Date the facts that change.** "Prices updated <Month YYYY>" on pricing and
plan pages, and a dated changelog entry for removals and renames.

**Retire old versions.** An old pricing page, a launch post with launch-day
prices, docs for a removed plan:

- Update the page with a dated note, or
- 301-redirect it to the current page, or
- mark it `noindex` if it must stay up for existing users.

Don't leave two live pages that disagree. If two URLs show the same content,
set a canonical.

**Keep structured data matching the page.** Organization JSON-LD on the home
or about page: `name`, `alternateName` (old names), `url`, `logo`,
`description`, `sameAs` (the official profiles from the growth file),
`foundingDate` if public. Google uses Organization data for disambiguation
and the logo; it doesn't require any property, and it can read JSON-LD
added by JavaScript, though server-rendered is simpler to verify. Never put a
fact in markup that the page doesn't show.

**Help crawlers notice.** Update `lastmod` in the sitemap for changed pages.
In Google Search Console, URL Inspection can request recrawl of a few
changed URLs (quota applies; crawling can take days to weeks). IndexNow
notifies Bing and the other participating engines of changed URLs; Bing
Webmaster Tools' AI Performance report shows when Copilot and Bing AI
summaries cite your pages, which makes Bing worth notifying. None of these
guarantee indexing or an answer change.

**Renames.** Keep the old name visible once on the about page ("<New>,
formerly <Old>") and in `alternateName`, so both names resolve to one entity.

## Profiles the business controls

Draft each change as field: new text, for the user to paste after logging in:

- **G2**: claiming is free; product details, description and pricing are
  edited in the vendor portal; names should match the website. Some fields
  need a change request. Reviews can't be edited by the vendor.
- **Google Business Profile** (if listed): owners edit name, category,
  hours, website and description; Google reviews changes before they go live.
- **Google knowledge panel** (if one shows): the entity can claim it, then
  suggest corrections through Feedback with supporting links. Anyone can
  send feedback; verified owners get priority review.
- **Crunchbase, LinkedIn, Product Hunt, GitHub, package registries, app
  stores, partner marketplaces**: update description, website, pricing
  mention and logo to match the growth file. Check each platform's own
  editing rules before promising what can be changed.

## Pages the business doesn't control

A correction request is short and checkable:

```text
Subject: Correction for "<article title>": <Name> pricing

Hi <name>,

Your <article> (<URL>) says <Name> "<the wrong line>". That changed on
<date>: <correct fact>. Source: <link to the current page>.

Would you update that line? Happy to answer anything else about <Name>.

<User's name>, <role> at <Name>
```

- One fact per request where possible; editors act on small, sourced asks.
- State the sender's role. Never pose as a reader or customer.
- Ask for factual corrections, not removal of fair opinions or bad reviews.
- Never offer payment or a link swap for the change.
- Find the contact from the page itself (author bio, contact or corrections
  page). Don't guess email addresses.

**Wikipedia**: someone with a company connection is strongly discouraged from
editing the article directly. Draft a talk-page edit request (the
`{{edit COI}}` template), disclose the connection, cite independent sources,
and accept that editors may decline.

**Wikidata**: creating an item about your own organization is discouraged as
self-promotion and notability needs independent reliable sources. On an
existing item, fixing a clear factual error is accepted; otherwise use an
edit request on the item's talk page.

**Forums and Reddit**: a reply in an existing thread is allowed only where the
user participates there, the community's rules allow it, and the reply opens
by stating the connection ("I work on <Name>"). Draft it; the user posts it
under their own account. No new accounts, no second accounts, no asking others
to upvote.

## Engine feedback

Google knowledge panels take suggested edits through Feedback. Where an
engine's interface offers feedback on an individual answer, the user can
report an identity mix-up there too. Treat both as a supplement: they don't
fix the page the next answer will read.

## What not to do

- Don't publish pages written to "train" engines with claims about
  competitors or unsourced superlatives.
- Don't create profiles, reviews or posts that pretend to be independent.
- Don't promise when or whether any answer will change.
