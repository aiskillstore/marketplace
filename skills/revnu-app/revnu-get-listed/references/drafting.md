# Drafting submissions

Every draft starts from the target's own rules page and the facts in
`.agents/revnu-growth.md`. If a fact a form needs isn't in either, leave a
`[NEEDED: ...]` placeholder rather than filling it.

## The fact sheet (assemble once)

- Name, exactly as on the site
- One sentence: what it does, for whom (no adjectives the business can't prove)
- Category, in the buyer's words, plus 3-6 tags the target already uses
- Price: free plan or trial, starting paid price, billing period, dated
- Main use cases (2-3), main integrations
- Who it's not for (some editors appreciate this; it's honest)
- Canonical URL, pricing URL, docs URL, logo URL, screenshots
- Founded year, location, team size if public
- Proof the user has confirmed is public: customer names, numbers, quotes

## Directory form

Fill the form field by field, in a block the user can paste:

```text
Target: <directory> — <submit URL>
Rules read: <guidelines URL>
Account needed: <yes/no> · Cost: <free / price> · Review time: <if stated>

Name: <...>
Tagline (<limit> chars): <...> (<count> chars)
Short description (<limit>): <...>
Long description (<limit>): <...>
Category: <their category name>
Tags: <their existing tags>
Pricing: <their pricing options, e.g. Freemium>
URL: <canonical, with a source parameter only if the user wants one>
```

- Count characters for every limited field and show the count.
- Pick categories and tags from the directory's existing ones.
- Write the long description for that directory's readers: lead with the use
  case they browse that directory for. Two directories in the same niche
  shouldn't get identical text.

## Awesome-list pull request

Copy the list's entry format exactly from neighboring entries:

```text
Repo: <owner/list> — CONTRIBUTING: <URL> — last merged PR: <date>
Gate check: <each stated requirement and whether it's met>
Section: <section name>, position: <alphabetical after X / at the end>

Entry line:
- [<Name>](<url>) - <description in the list's style and length>

PR title: <the list's convention, e.g. "Add <Name>">
PR body: <follow the PR template; fill its checklist honestly>
```

- Description: what it is, not why it's great. Match the list's tense,
  punctuation and length; many lists want a period at the end and no
  marketing words.
- One entry per PR unless the list says otherwise.
- If the list rejects AI-generated PRs, say so to the user, give them the
  entry line and facts, and let them write and open it themselves.
- If the list requires minimum stars or age the project doesn't have, mark it
  "not eligible until <condition>" and don't draft.

## Pitch to a roundup author

Short, specific to the article, sent by the user under their own name:

```text
Subject: <Name> for your "<article title>"?

Hi <first name>,

I read your <article> (<URL>). <One sentence that shows you read it: a
specific pick or criterion they used.>

I'm the <role> at <Name>. It <one sentence: what it does, for whom>. It may
fit your "<their section or criterion>" section because <one concrete,
checkable reason: price point, a feature their criteria name, a segment they
cover>.

Facts if useful: <price, free plan, 1-2 specifics>. <Trial or demo access if
the user offers it.>

If it doesn't fit, no worries.

<User's name>
<Role>, <Name> · <URL>
```

- Use the article's own criteria. If the business doesn't meet them, don't
  pitch.
- Don't offer payment, a link swap or affiliate commission for inclusion
  unless the user decides to and the placement is disclosed as paid by the
  publisher. Paid links should carry `rel="sponsored"` or `nofollow`.
- Find the contact on the page (author bio, contact page). Don't guess email
  addresses; if none is listed, say so.
- One pitch and at most one short follow-up a week or more later. The user
  sends both.

## Review-site profile

```text
Profile: <site> — <claim or create URL> — free: <yes/no>
Fields: <field>: <text> ...
Review request (sent by the user to all customers, or a whole segment, not
only happy ones):

"Hi <name>, we're collecting honest reviews of <Name> on <site>. Good or bad,
it helps other <buyers> decide. Here's the link: <review URL>. Thanks either
way."
```

- No incentive tied to a positive review. If the user offers any incentive,
  it goes to everyone who reviews regardless of rating, and the site's own
  incentive rules apply.
- This skill never drafts reviews for founders, employees or their
  relatives to post. In the US, insider reviews must clearly disclose the
  connection, and many review sites set stricter rules of their own.

## Community reply

```text
Thread: <URL> — posted <date> — community rules on promotion: <quote or
"none found">
Reply (from <user>'s own account):

I'm the founder of <Name>, so take this with that in mind.
<Answer the actual question in 2-4 sentences, including non-<Name> options
where they fit better.>
<One sentence on where <Name> fits, with a link if the community allows
links.>
```

- Only for open threads where the product answers the question asked.
- One reply per thread. No follow-up bumps, no DMs to commenters.

## Before marking anything ready

- Every fact traces to the growth file, the live site or the user.
- No "best", "leading", "#1", "trusted by" without proof the user confirmed.
- The target's format, limits and gates are met, or the gap is stated.
- The user knows exactly what they will send, where, and at what cost.
