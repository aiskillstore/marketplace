# ICP for search

What an ICP is, where it lives in the search plan, which fields earn their place, how it becomes a search,
and the words every skill in this pack uses for it. Evidence labels as in `references/frameworks.md`.

Example seller everywhere below (fictional): field calibration software for water networks.

## The words

**ICP (ideal customer profile)**
- **Is:** the kind of company worth reaching. That means its trade (kind of company), its size, its place, and at most one situation a company page shows (what it runs, what it does, what it can do). One ICP is a set of companies that get about the same value from the offer and are reached the same way.
- **Is not:**
  - a person or a job title;
  - a moment (that is timing);
  - a deal's readiness (budget, authority, need, timeline: that is qualification);
  - a list of named accounts.
- **Search:** the company half of one segment of the search plan (kinds of company, size, places). Every value in it can be checked on a company page or a profile without talking to anyone.

**Segment (in the search plan)**
- **Is:** one ICP as the plan holds it, with the roles searched inside it attached (its groups). The order of the segments is the priority. In a plan edit, the field `icp` names a segment id.
- **Is not:** a test population (that is a half), or a market study.
- **Search:** each segment is searched per language and place. One segment is one ICP.

**Kind of company**
- **Is:** the trade word for what a company is (the plan's `kinds`). It is the main field of an ICP. A segment with no kind read searches every industry, and the plan says so.
- **Is not:** a persona, or a sector page's audience.

**Plan group (a role)**
- **Is:** one job searched inside one segment. It is named by its main title and carries its variant titles (spellings, languages, short forms).
- **Is not:**
  - a persona card: it has no situation and no message;
  - a batch of leads;
  - a buying group.
- **Search:** every title variant is searched. A group is the searchable half of a persona.

**Persona**
- **Is:** a role in a situation inside one ICP's companies: the person a first message is written to, and what it says. A persona card has two halves:
  - **Found by:** titles and seniority, which a profile shows. This half is searchable and copied from plan groups.
  - **The message half:** Why now, Pain, Objection, Proof, Offer, learned from the user and from replies. Nothing in it can be searched.
- One persona can cover several plan groups or segments when the first message would be the same. One title splits into two personas when the situation differs.
- **Is not:**
  - a job title alone;
  - a person with a life (age, hobbies);
  - an attitude in a deal (a champion, a blocker);
  - a kind of company.
- **Search:** only Found by reaches the search.

**Buying group, buying role**
- **Is:** the buying group is the people inside one company with a say in one purchase. A buying role is what one of them does: uses it, chooses it, signs, can veto, gets blamed.
- **Is not:** a persona each, or a fixed size (published sizes run from about 5 to over 20, depending on who counted and how).
- **Search:** never a filter. It fills the card's Who else decides, and what the reader can forward. Who to talk to inside a company is asked of the user, not read off the company's facts.

**Why now, trigger, signal, `whyNow`**

All four are timing. They order leads and give the opener. They never decide who is in an ICP or a persona.

| Term | Where it lives | What it is |
|---|---|---|
| Why now | the card | the kind of moment that makes the Pain urgent, with its window (6 months at most) |
| Trigger | the world | the event itself (a new role, a raise, a job ad, a lease ending) |
| Signal | a public page | the dated public fact that shows the trigger happened (a profile, a post, a company page, news) |
| `whyNow` | a list row | one dated reason for one person, from `bereach_add_signals` or a brief |

- **Search:** none of these is a plan field.
  - An event ask ("companies that just raised") goes to `bereach_find_signals`.
  - Dated reasons for a list already found go to `bereach_add_signals`.

**Fit, intent, timing**
- **Fit:** how well a company matches the ICP and a person matches a persona. It is stable and visible.
- **Intent:** signs a company is researching the problem. The pack's tools do not read it.
- **Timing:** whether now is the moment.
- Fit decides who is in; timing decides the order. Neither one is qualification.
- The fit check (`bereach_check_fit`) is a 0 to 100 fit score, run only when the user asks. It hides nobody.

**Qualification**
- **Is:** a judgement on one deal after a conversation (BANT, MEDDIC, SPICED): budget, authority, timeline, champion.
- **Is not:** an ICP field or a persona field.
- **Search:** never a filter. No profile shows it.

**Negative ICP, Not this persona**
- **Negative ICP:** companies left out of every search. These are current customers and open deals, the user's own company, and a size or kind of company no offer serves.
- **Not this persona:** people who look like the persona but are not it. These are students, interns, side projects, the sender's own profile and team, and a lookalike title that does not choose.
- **Search:**
  - The negative ICP leaves at the search step.
  - Not this persona sorts the leads that were found.
- **Page chips:** `hors ICP` for a company; `pas ce persona` or its specific reason (`étudiant`, `projet perso`, `votre équipe`) for a person.

**Target, cible**
- No longer used. Say ICP for companies, persona for people, or the reason something is left out.
- "Out of target" becomes "out of scope": `hors ICP` or `pas ce persona`.

**Other words**
- **Batch (lot):** leads on Who is who that share one open question. There is one rule per batch.
- **Half:** one arm of a test.
- **Card:** always "persona card" or "voice card". In French pages, "fiche" means the persona card only.

## What an ICP is and is not

Two tests make one ICP: **same value** (the companies in it get about the same value from the offer) and
**same reach** (they are found and written to the same way). If a part of the group needs a different
pitch, it is two ICPs. If it cannot be written as a search, it is a description, not an ICP.

An ICP holds only what a company page or a profile shows before anyone talks. What only a conversation
reveals (budget, urgency, who signs, how they decide) belongs to the persona card's message half or to
qualification.

| Layer | Unit | Question it answers | Changes | Known before contact |
|---|---|---|---|---|
| Market | all companies | who could ever buy | years | yes |
| ICP | a kind of company | which companies we spend on | quarters | yes, that is what defines it |
| Buying group | the people in one company, for one purchase | who has a say | per purchase | partly, ask the user |
| Buying role | one person in that group | what this person does in it | per purchase | no |
| Persona, Found by | one person | who to find (titles, seniority) | quarters | yes |
| Persona, message half | one person | what to say (Why now, Pain, Objection, Proof, Offer) | with each read of replies | partly |
| Qualification | one deal | is this deal real now | days | no |

## Where it lives

In the search plan (`bereach_plan_searches`), not in a saved memory:
- **Segments are ICPs**, in priority order: the first segment is the one the user wants reached first.
- **On each segment:** kinds of company, size and places.
- **Groups are roles** inside a segment, each with its variant titles.
- **Offered values** (roles, kinds, places the plan proposes) are not searched until the user picks them.
- **In an edit,** `icp` is a segment id.
- **The persona cards** hold the message half (linkedin-personas); their Found by copies the plan's groups.

## Fields that earn their place

A field stays only if all four hold:
1. **Observable without contact:** a company page or a profile shows it.
2. **Discriminating:** companies differ on it, and the difference tracks who buys.
3. **Actionable:** a later decision changes with its value (searched or not, which card, which message).
4. **Filterable:** it can be written as a search value, not prose.

The one-sentence test: if you cannot say what you would do differently for a company on each side of the
field, delete it.

**A label is not a capability.** An industry label is a stand-in for what a company runs or does. When
the offer depends on the capability (a utility that runs its own network, not every "utilities" company),
search the capability words, not the label. One agency reported a list rebuilt this way going from
thousands of companies to hundreds, with far more replies (Practice: keep the mechanism, not the number).

Fields that do not belong in an ICP:
- revenue band for private firms (rarely public, mostly guessed);
- budget, authority, timeline, "actively evaluating" (qualification);
- pain paragraphs (they belong on the persona card);
- psychographics;
- persona demographics (age, tenure, education);
- band edges nothing depends on (a size limit that changes no search, card or message).

## Every field narrows

A profile is a conjunction: each added value multiplies the narrowing. Chapman, Love, Milham, ElRif and
Alford (2008) drew 10,000 random descriptions over six real datasets (268 to 10,307 people): with 9 or
more attributes the description matched nobody in 5 of 6 datasets, and only one dataset had a 7-plus
description matching more than 0.3% of people (Measured; random descriptions, mostly consumer data).

So read what the whole plan returns, never what each field returns alone. The plan's count is the cost
of every field together; a field that halves it and changes no decision goes.

## From ICP to search

Work from the outside in (Bonoma and Shapiro): what a company page shows first, then what a profile
shows. What only contact reveals is never a filter.

| ICP or persona field | Where it goes in the search |
|---|---|
| Kind of company | the segment's kinds |
| Size | the segment's size |
| Place | the segment's places (and the languages written there) |
| Role | a plan group, with its title variants |
| Seniority | a loose check on the titles, not a filter on its own |

**Titles are noisy evidence of a role:**
- function and seniority shown on profiles are often guessed from the title by the platform, not given
  by the person (Vendor claim from data vendors, consistent across them);
- about 20% of established US users edited the title or description of a job they had already left
  (Bloom, Moore, Simon and Wilkie-Rogers, NBER working paper 35546, 2026, on a labour-data firm's
  profile data; Measured, not yet peer reviewed);
- titles inflate: senior-sounding words spread without the job changing (Survey and Vendor claim);
- some people choose their own titles (Grant, Berg and Cable, "Job titles as identity badges", *Academy
  of Management Journal*, 2014; Measured, field studies);
- research normalises titles through the skills that come with them (Decorte et al., JobBERT, 2021).

So one role is a set of title variants: spellings, short forms, inflated forms, in each market's
languages and in English. The persona is the job the person does; titles are only the evidence for it.

## Widening and narrowing

- **One move at a time, to the next pin** (Moore): widen to the adjacent kind of company, size or place,
  rather than every field loosened at once.
- **A small count:** ask whether it is a beachhead by choice (one tight ICP to win first) or an ICP
  narrowed by accident (a field nobody needed).
- **Picks come from the plan's offered values**, so a widening stays inside what the plan can search.
- A repeat search expects at most round 1's found minus who is already in the list (SKILL.md step 1).

## Negative ICP and Not this persona (defined in The words)

Tunguz (2017) argues companies outside the ICP carry hidden costs (a split roadmap, scattered brand,
churn). That makes exclusions a cost guard. Nothing shows they raise win rates (Practice).

## Timing is not an ICP field

A company with a fresh trigger that fails the ICP is
still outside it; a company inside the ICP with no trigger is reached later, not dropped.

- The 95:5 rule is a formula, not a measurement: share in market per quarter is about 1 divided by the
  number of quarters between purchases. A utility that renews its calibration tools every five years is
  about 1 in 20 per quarter; every two years, about 1 in 8. Ask the user how often their buyers buy.

## The circularity trap

An ICP drawn from won deals reproduces the old ICP: the wins come from the companies the old ICP chose,
so they say nothing about companies never tried (Kellogg; Mora Cortez, Clarke and Freytag 2021 call
outcome-based segments "tautological").

- A field comes before the result (kind, size, place, what they run); it is not the result (contract
  value, retention, a fit score).
- Loss reasons written in a CRM match the buyer's own account a minority of the time: one win-loss firm
  found 15% over 1,000 deals (Vendor claim, method stated). Ask non-customers about the problem.

## The buying group

Who decides is asked of the user (The words), never read off the company: six firm
characteristics predicted which buying group a firm had only 47% of the time against 27% by chance,
and three of the six were survey attitudes no outsider sees (Choffray and Lilien 1980; Measured, 118
firms, one product category; the authors call even 47% biased upward). The roles to ask about: who uses it, who
chooses, who signs, who can veto, who gets blamed. A message the reader can forward to them beats one
that only flatters the reader (Gartner 2025, n = 632: buying-group relevance makes a high-quality deal
about three times more likely; Survey, only the direction is safe to use).

## Frameworks

### The nested approach (Thomas Bonoma and Benson Shapiro, "How to Segment Industrial Markets", *Harvard Business Review*, 1984)
- What it says: five nests from the outside in: demographics (industry, size, place), operating variables (technology, what they use, capabilities), purchasing approach, situational factors (urgency, order size), personal traits of the buyer. Outer nests are cheap to see; inner ones need contact.
- On LinkedIn search or cards: nests 1 and 2 are searchable and belong to the ICP. Nests 3 to 5 are learned in conversation: they belong to the persona card's message half or to qualification.
- Example: "runs its own network of more than 500 km of pipe" (nest 2) is an ICP field; "frustrated with the last supplier" (nest 5) is not.
- Use when, not when: to decide whether a field can be a filter; not as a checklist to fill every nest.
- Evidence: Practice; never tested. Only the abstract and date were confirmed.

### Beachhead and bowling alley (Geoffrey Moore, *Crossing the Chasm*, 1991)
- What it says: win one narrow niche first, then move to the adjacent one, like bowling pins. Aim at a target customer, not a target market.
- On LinkedIn search or cards: the first segment of the plan is the beachhead; widening is the next pin, one move at a time, not a looser filter.
- Example: municipal utilities in one region first, then the same utilities in the next region, then private water operators.
- Use when, not when: a small offer with one proven use; not when the user already sells evenly across many kinds of company.
- Evidence: Practice; the criteria come from matching secondary summaries.

### Best fit from differentiated value (April Dunford, *Obviously Awesome*, 2019)
- What it says: best-fit customers are those who care a lot about what only you do. Find the value first, then the companies that care about it.
- On LinkedIn search or cards: an ICP field is a visible trait that predicts caring about the offer's difference, not a trait current customers happen to share.
- Example: utilities that calibrate in the field themselves care about on-site calibration; those that outsource maintenance do not.
- Use when, not when: when the ICP is a list of traits nobody can tie to the offer; not as a search value by itself.
- Evidence: Practice.

### ICP and segment profiles (Winning by Design, "How to Create your Ideal Customer Profile", blueprint, 2022)
- What it says: a numbers pass on firmographics against lifetime revenue, then a pass with the sellers on 5 to 10 customers; write one ICP summary and 3 to 5 segment profiles. Its own caveat: past successes may not be the customers you want next.
- On LinkedIn search or cards: the summary is the plan; the segment profiles are its segments. Its Critical Event belongs to timing (Why now), not to the ICP.
- Example: interviews reveal that utilities with several separate networks buy faster; that becomes a capability field.
- Use when, not when: when the user has customers and sellers to interview; not for a first offer with no customers.
- Evidence: Practice; the conversion rates in its figures are illustrative.

### Account tiers (Bev Burgess, ITSMA, account-based marketing, from about 2003)
- What it says: one-to-one for a few strategic accounts, one-to-few for clusters, one-to-many (programmatic) for the rest.
- On LinkedIn search or cards: a list of hundreds is one-to-many, so the ICP is written as search values, not as named accounts, and cards are written per role, not per company.
- Example: 300 utilities in France get one card per role; the three largest operators, if any, are handled by hand.
- Use when, not when: to decide whether a named-account list or an ICP fits; not for its ROI figures (no control).
- Evidence: Practice.

### The cost of non-ICP customers (Tomasz Tunguz, "ICP and disqualification", blog, 2017)
- What it says: customers outside the ICP cost more than they seem (roadmap splits, support, churn); change the ICP deliberately.
- On LinkedIn search or cards: a change of ICP is a new plan, said out loud.
- Example: private homeowners asking about leak sensors leave every search.
- Use when, not when: to justify exclusions; not as proof that exclusions raise replies.
- Evidence: Practice; no data.

### Broad reach and the 95:5 formula (Byron Sharp, *How Brands Grow*, 2010; John Dawes, Ehrenberg-Bass, 2021)
- What it says: most buyers are not in market at any moment; growth needs reaching all potential buyers, and "restrictive" targeting is warned against while "tailoring" is endorsed.
- On LinkedIn search or cards: argues against one narrow search being the only motion, not against an ICP; the formula is in Timing is not an ICP field.
- Example: renewals every five years means about 1 in 20 utilities in market per quarter: a list of 300 holds about 15.
- Use when, not when: when a user expects every lead to be ready now; not as evidence against filtering, since no outbound list was ever measured in this work.
- Evidence: Practice for the formula; the 95:5 figure itself is not measured.

### The ICP as a regression, and the trap in it (Dave Kellogg, Kellblog, 2025; Mora Cortez, Clarke and Freytag, *Journal of Business Research*, 2021)
- What it says: an ICP starts as an aspiration and becomes a regression on won accounts; segmenting by outcome is tautological.
- On LinkedIn search or cards: won deals reorder or shorten a plan, they do not invent a kind of company; a small slice outside the ICP tests whether another one works.
- Example: all wins are utilities over 100,000 people because those were the only ones called; a slice of smaller ones is tried before cutting them.
- Use when, not when: when the user wants to rebuild the ICP from their CRM; not when there are too few deals to read.
- Evidence: Practice (Kellogg); Measured literature review, 88 papers (Mora Cortez).

## Numbers not to repeat

Never repeat: "a strong ICP gives 68% higher win rates" (a self-selected survey of confidence), "a tight ICP gives 25 to 30% better ROI" (Untraced), "95% of buyers are not in market" as a measured fact (arithmetic from an assumed cycle), "a buying group of 6 to 10" (unsourced; published sizes run from about 5 to over 20), "signal-based outreach gets 25 to 40% replies" and "trigger events win 74% of the time" (Untraced).

## The honest promise

An ICP gives control over the list: who is searched, who is left out, in what order. Nothing shows that
writing one raises replies by itself; what moves replies is measured at step 6, on the user's own sends.
