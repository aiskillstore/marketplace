# Worked charter and section quality

A full example charter, then weak-versus-strong versions of the sections that most often fail review. The example company is fictional; the numbers are illustrative placeholders, not benchmarks.

## Contents

- [Worked example](#worked-example)
- [Rejected charter - activity list as strategy](#rejected-charter--activity-list-as-strategy)
- [Weak vs strong sections](#weak-vs-strong-sections)
- [Second example in one paragraph - company-adoption motion](#second-example-in-one-paragraph--company-adoption-motion)

## Worked example

```markdown
# DevRel charter: Fictional Corp, H2

## Position

CORE, written after 14 user conversations and a support-ticket read.
Community: ~2,100 monthly active API keys, no venue of our own; questions land in
GitHub issues and one Discord we do not run. Engagement is transactional.
Organization: DevRel is one advocate hired three months ago, reporting into
product. Marketing owns the blog, engineering owns the docs repo. A previous
"developer marketing" push in the last fiscal year produced 30 posts and no
measurable adoption change; nobody could explain what it was for.
Relationships: two integration partners resell us into their own developer base;
our closest competitor runs a strong community and weak documentation.
Ecosystem: we are the third-known option in a category developers discover by
searching an error message, not by browsing.
Lifecycle stage: growing.

## Driver

Developer adoption. Owner: VP Product, who funds the role and will defend it.
Secondary: product input, because the roadmap for next year is still open.

## Goals

Primary: activation - 41% of new API keys never make a second successful call
(journey step: evaluation and validation).
Primary: awareness - we are absent from the error-message searches that produce
our best-converting arrivals (journey step: initial awareness).
Secondary: product - the top three friction points reach the backlog with an owner.

## Audience

Primary: individual backend developers adopting alone, in the Python and
TypeScript ecosystems, at companies under 200 people.
Not served this horizon: enterprise platform teams. We will answer their
questions but will not build procurement material for them yet.

## Pillar mix

Enablement 50%, marketing 30%, advocacy 20%, community 0%.
Community is deliberately starved: at ~2,100 monthly actives with transactional
engagement, a venue of our own would sit empty and argue against us.

## Bets

1. Rebuild the quickstart to first successful call under 10 minutes.
   Goal: activation. Owner: advocate. Signal: share of new keys reaching a second
   successful call. Review: week 8.
2. Publish troubleshooting pages for the 12 highest-volume support errors.
   Goal: activation + awareness. Owner: advocate, drafted from support data.
   Signal: organic arrivals on error pages, and tickets per 100 new keys.
   Review: week 10.
3. Ship a monthly technical series on the two integration problems developers
   already search for. Goal: awareness. Owner: advocate outlines, agency drafts.
   Signal: non-paid qualified arrivals. Review: week 12.
4. Run six friction logs on our own onboarding and route findings to product.
   Goal: product. Owner: advocate, VP Product accepts. Signal: shipped changes
   traceable to a friction log. Review: quarterly.

## Build vs buy

Bet 1: in-house. Latency 3 weeks. Reviewer: engineering lead. Red line: yes,
it is the credibility surface.
Bet 2: in-house drafting, contracted editor. Latency 4 weeks. Setup: one style
brief. Reviewer: advocate.
Bet 3: agency drafting from in-house outlines. Latency 8-9 weeks per piece,
about 6 weeks of pipeline setup first. Reviewer: advocate. If the contract ends,
the series stops cleanly; no surface decays.
Bet 4: in-house only.

## Staffing

Stage: grow, one generalist. Next capability: a technical writer, triggered when
the advocate's review queue exceeds two weeks for a second consecutive month.
Not hiring a community manager this horizon; no community to manage yet.

## Refused

- No conference sponsorship this horizon: our arrivals come from search, and a
  booth costs the equivalent of both bets 1 and 2.
- No Discord of our own until bet 1's activation number moves and question volume
  exceeds what issues can absorb.
- No swag program. The team wanted one; it serves no goal on this list.
- No enterprise procurement material until an approver-gated deal actually stalls.

## Open questions

- Is the second-call drop-off concentrated in one SDK or spread across all four?
  Nobody has cut it that way. Owner: data lead, by week 3; it decides bet 1's scope.
- Does the program budget include the advocate's salary? Finance and the VP Product
  answer differently. Owner: VP Product, before the next planning cycle.
- No named production reference has agreed to be public. Owner: account team, by
  week 6; without one, bet 3 loses its main asset.

## Exec narrative

We are funded to grow developer adoption. Four out of ten developers who sign up
never make a second successful call, and we are invisible in the searches that
bring us our best users. This half we fix the first ten minutes of the product and
own those searches, and we route what we learn into the roadmap. We are not
building a community or attending conferences yet, because neither addresses the
leak. By the end of the half you should see a higher share of new developers
reaching a working integration, and more of them arriving from search.

## Review

Re-decision at the end of the half. Early re-decision if the funding sponsor
changes, if the pricing model changes, or if bet 1's signal does not move by
week 10.
```

## Rejected charter - activity list as strategy

This is what the same company produces when it skips CORE and starts from the calendar. It is the most common failure, and it is tempting because every line is real work someone is genuinely willing to do. Recognise it and send it back.

```markdown
# DevRel plan: H2

## Goals

Build awareness, grow the community, support sales, improve docs, gather
product feedback, and strengthen our employer brand.

## Plan

- Publish two blog posts a month
- Speak at four conferences
- Launch a Discord
- Refresh the documentation
- Run a monthly livestream
- Attend two hackathons
- Ship a swag store

## Team

Hire a community manager and a developer advocate in Q3.

## Metrics

Blog views, Discord members, conference attendees, GitHub stars, social
followers.
```

Why it fails, in the order a reviewer will find it:

1. **Six goals is no goals.** Every activity below scores identically against them, so effort will follow whoever asks loudest, not the funded driver. There is no sponsor named anywhere.
2. **No position.** Nothing states what the community, organisation, relationships or ecosystem currently look like, so no reader can tell whether these are the right moves or another company's moves copied over.
3. **Activities with no drop-off behind them.** Not one line names a place developers are currently stuck. The Discord and the swag store in particular exist because they are normal, not because anything argues for them.
4. **All four pillars funded at once.** Advocacy, marketing, enablement and community all appear, at a company whose team is about to be two people - the median DevRel team size is 2-5, and this plan is shaped like a fifteen-person one.
5. **Hires with no trigger.** Two roles are named with no friction they remove and no condition that justifies them.
6. **Reach metrics only.** Views, members, attendees, stars and followers are all counts of hits, not of developer behaviour. The first exec question - "what did that change?" - has no answer.
7. **Nothing refused, nothing unknown.** With no refused list, every idea returns next quarter; with no open questions, the plan's assumptions are invisible until they break.

The repair is not to trim the list. It is to run steps 1 and 2, discover the one funded driver, and let most of these lines fall away on their own.

## Weak vs strong sections

**Driver**

- Weak: "Build awareness and community around our developer platform." Two goals, no owner, no funder's language, unfalsifiable.
- Strong: "Developer adoption. Owner: VP Product, who funds the role and will defend it." One reason, one named person, quotable in a budget review.

**Goals**

- Weak: "Increase engagement across our developer touchpoints." No journey step, no drop-off, no number.
- Strong: "Activation - 41% of new API keys never make a second successful call (journey step: evaluation and validation)." Observed behaviour, one step, correctable.

**Pillar mix**

- Weak: "Balanced investment across advocacy, marketing, enablement and community." Four pillars at 25% each is how a small program produces nothing four times.
- Strong: "Enablement 50%, marketing 30%, advocacy 20%, community 0%," plus the sentence explaining why community is starved. A starved pillar named on purpose stops the quarterly re-litigation.

**Bets**

- Weak: "Improve documentation and grow our content output." No owner, no signal, no date.
- Strong: numbered bets, each with goal, owner, signal and review date. The date is what turns a plan into something that can be wrong in public.

**Refused**

- Weak: absent, or "we will focus and say no to distractions."
- Strong: four named refusals with reasons, including one the team actively wanted. A refused list that costs nothing was not a decision.

**Exec narrative**

- Weak: "DevRel will drive developer love and community-led growth through a multi-channel engagement strategy." Jargon, no number, unrepeatable.
- Strong: five plain sentences naming the problem, the two moves, the explicit non-moves, and what the funder will see. The test is whether the funder can repeat it accurately without you in the room.

## Second example in one paragraph - company-adoption motion

A security-tooling vendor sells into platform teams; developers evaluate, a security architect approves. Driver: sales enablement, owner VP Sales. Goals: activation (proof-of-concept completion) and revenue (evaluations reaching a technical decision). Audience: platform engineers at 500-plus-employee companies; individual hobbyists explicitly not served. Pillar mix: enablement 60%, advocacy 30%, marketing 10%, community 0%. Bets: a scoped proof-of-concept kit, reference architectures for the three deployment shapes, a written security-and-licensing answer set, and two named production references. Build versus buy: everything in-house except diagram production and the case-study interviews' transcription. Refused: hobbyist content, meetup sponsorship, a public community - none of them reaches the approver who blocks the deal.
