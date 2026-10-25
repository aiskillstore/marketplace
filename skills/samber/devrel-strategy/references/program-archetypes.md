# Program archetypes

Candidate whole-program shapes to brainstorm from in step 3. Each one over-invests in one or two of the four pillars - developer advocacy, developer marketing, developer enablement, developer community. It starves the rest on purpose.

Pick by funding driver and stage, then adapt; never present only one.

## Contents

- [How to use these](#how-to-use-these)
- [Archetype 1 - Enablement-first](#archetype-1--enablement-first)
- [Archetype 2 - Product-feedback](#archetype-2--product-feedback)
- [Archetype 3 - Evaluation-support](#archetype-3--evaluation-support)
- [Archetype 4 - Reach-first](#archetype-4--reach-first)
- [Archetype 5 - Community-first](#archetype-5--community-first)
- [Archetype 6 - Contributor-first](#archetype-6--contributor-first)
- [Stage overlay](#stage-overlay)
- [Adoption-path overlay](#adoption-path-overlay)
- [Breaking a tie between two survivors](#breaking-a-tie-between-two-survivors)

## How to use these

Match the funding driver to a starting archetype, then check it against the stage overlay and the adoption-path overlay. Change the bets, not the shape: a program that funds three archetypes at once is the failure mode these exist to prevent.

They are listed here in the same efficiency order step 3 applies - `enablement-first > product-feedback > evaluation-support > reach-first > community-first > contributor-first`. Read top-down. The value and effort axes, the ties and the conditions that override the order live in step 3 of `SKILL.md`, where the choice is actually made.

## Archetype 1 - Enablement-first

- **Fits drivers:** developer enablement, developer adoption after a signup spike that does not convert.
- **Pillar mix:** enablement heavy, advocacy light, marketing and community token.
- **Goals it serves:** activation, retention.
- **First bets:** time-to-first-success quickstart, error and troubleshooting coverage for the top support signals, tested code samples in the two languages that actually matter, an agent-readable documentation surface.
- **Effort:** about a quarter of one person's writing time, then near-zero maintenance; no coordination beyond whoever owns the docs; fully reversible, because the artefacts outlive the program.
- **Starves:** events, social presence, community venue.
- **Fastest signal:** share of new signups reaching first success, and support tickets per hundred new developers.
- **Wrong pick when:** nobody arrives at all. Fixing activation for a trickle produces a very efficient trickle.

## Archetype 2 - Product-feedback

- **Fits drivers:** product input before or around product-market fit.
- **Pillar mix:** advocacy heavy, enablement medium, marketing and community token.
- **Goals it serves:** product, activation.
- **First bets:** friction logs on the real onboarding path, structured design-partner conversations, a route that gets developer pain into the product backlog with a named owner, public follow-through on what shipped because of it.
- **Effort:** about an hour a week of friction logging, plus standing attention from one product owner; reversible the day the roadmap closes.
- **Starves:** scale content, events, community programs.
- **Fastest signal:** product changes traceable to developer feedback per quarter.
- **Wrong pick when:** the roadmap is already fixed for a year. Collected feedback that changes nothing burns credibility with both developers and the product team.

## Archetype 3 - Evaluation-support

- **Fits drivers:** sales enablement, ecosystem and partnerships in an enterprise motion.
- **Pillar mix:** enablement heavy, advocacy medium (pre-sales facing), marketing light, community light.
- **Goals it serves:** activation, revenue.
- **First bets:** reference architectures, proof-of-concept kits with a scoped success definition, security/licensing/compliance answers written once, migration guides from the incumbent, named production references.
- **Effort:** about a quarter of one person's writing time, plus standing coordination with sales; reversible, since the artefacts outlive the program.
- **Starves:** hobbyist content, broad awareness plays.
- **Fastest signal:** evaluations that reach a technical decision, and time from first contact to a working proof of concept.
- **Wrong pick when:** the product is bought bottom-up by individuals. Approver material nobody reads is expensive.

## Archetype 4 - Reach-first

- **Fits drivers:** developer adoption at the awareness stage, employer brand.
- **Pillar mix:** marketing heavy, advocacy medium, enablement maintenance-only, community none.
- **Goals it serves:** awareness, acquisition.
- **First bets:** a search-durable content line on the problems developers already search for, one or two conference stages that match the ecosystem, a repeatable launch beat, presence where the ecosystem already gathers.
- **Effort:** a standing job - the cadence is the product. Unwinding it is cheap, but everything it compounded stops compounding.
- **Starves:** community venue, champions, certification.
- **Fastest signal:** qualified arrivals from non-paid sources, and whether new arrivals reach first success at the same rate as existing ones.
- **Wrong pick when:** onboarding leaks. Reach into a broken activation path burns the audience once and teaches it the product does not work.

## Archetype 5 - Community-first

- **Fits drivers:** contributor community, developer adoption in a peer-learning ecosystem, retention of an installed base.
- **Pillar mix:** community heavy, advocacy medium, enablement medium, marketing light.
- **Goals it serves:** retention, referral.
- **First bets:** a single venue chosen against where the audience already is, a founding cohort seeded by hand, answer-time discipline, recognition for the first peer answers, a champions pipeline once density allows.
- **Effort:** a standing job with daily answer-time discipline; the hardest shape to unwind, because closing a venue is public evidence against the program.
- **Starves:** paid reach, conference booths, gated content.
- **Fastest signal:** questions answered by someone other than staff, and week-four return rate of the founding cohort.
- **Wrong pick when:** the user base is too small or too asynchronous to reach conversational density. An empty venue is worse evidence than no venue.

## Archetype 6 - Contributor-first

- **Fits drivers:** contributor community around a company-owned or sponsored open-source project.
- **Pillar mix:** community heavy, enablement heavy (contributor-facing), advocacy light, marketing light.
- **Goals it serves:** product, referral.
- **First bets:** a first-contribution path, curated starter issues with real mentoring, a reproducible dev environment, published triage and review response targets, governance clarity about who decides.
- **Effort:** a standing job spent on maintainer hours nobody can backfill; barely reversible, since an abandoned starter-issue queue damages the project itself.
- **Starves:** paid reach, event sponsorship.
- **Fastest signal:** first-response time on issues and pull requests, and repeat contributors in the following quarter.
- **Wrong pick when:** the codebase cannot absorb outside changes, or maintainers have no review capacity. Recruiting contributors into a review backlog damages the project's reputation.

## Stage overlay

| Stage                             | Realistic shape                                                          | Do not                                                      |
| --------------------------------- | ------------------------------------------------------------------------ | ----------------------------------------------------------- |
| Seed (nobody or a part-time hat)  | one archetype, one bet, finished before a second starts                  | run two archetypes, build a community venue, sponsor events |
| Grow (small team, specialising)   | one primary archetype plus a maintenance line on the previous one        | let every new hire start a new pillar                       |
| Scale (several specialised teams) | primary archetype plus leverage programs that multiply output per person | grow headcount linearly and call it scaling                 |

## Adoption-path overlay

- **Individual-developer adoption** pushes toward enablement-first, reach-first and community-first. The developer decides alone, so friction and peer proof dominate.
- **Company adoption** pushes toward evaluation-support and, later, community-first for the installed base. The developer's enthusiasm still starts it, but the approver's checklist finishes it.
- Artefacts serving both: quickstart, reference documentation, changelog and migration guides, honest limitations. Build these once and count them in both columns.
- Artefacts serving one only: hobbyist tutorials and swag reach individuals; security questionnaires, procurement-ready licensing and named references reach companies.

## Breaking a tie between two survivors

Two rules settle what the efficiency order leaves level:

- **Fix the leak before opening the tap.** An activation problem beats an awareness problem whatever the ratio says, because reach into a leaking funnel spends audience that does not come back.
- **Choose the one whose signal appears soonest, when still tied.** An unfalsifiable strategy cannot be corrected mid-horizon.
