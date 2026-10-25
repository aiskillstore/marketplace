# Build versus buy

Per-bet sourcing decisions for step 5: what a devrel program can rent, what it must own, and the costs each option hides.

## Contents

- [The decision test](#the-decision-test)
- [Option table per capability](#option-table-per-capability)
- [Red lines - never outsourced](#red-lines--never-outsourced)
- [The documented agency pattern](#the-documented-agency-pattern)
- [Hidden costs of buying](#hidden-costs-of-buying)
- [Hidden costs of building](#hidden-costs-of-building)
- [Writing the decision into the charter](#writing-the-decision-into-the-charter)

## The decision test

Answer in this order for each bet:

1. **Judgment or volume?** Work that requires a trade-off call, a limitation admitted, or a technical opinion is judgment. Work that requires more of a known shape is volume. Buy volume.
2. **Does the output carry a person's name?** A byline, a stage, a moderation decision or an incident update is a promise from a person. Keep it.
3. **What is the latency?** Rented pipelines add weeks between decision and output. If the bet is tied to a dated event, that latency may disqualify buying.
4. **What is the setup cost before the first output?** Vendor pipelines need briefs, templates, review loops and someone to run them, paid before anything ships.
5. **Who reviews it?** Bought output still consumes in-house review time, which is usually the same bottleneck the buy was meant to relieve.
6. **What happens when the contract ends?** A surface that decays into something actively wrong (stale docs, an abandoned community, an unmaintained sample repo) is worse than one that was never started.

## Option table per capability

This table says which options are viable per capability. Which of the viable ones to pick first is ordered in step 5 of `SKILL.md`, alongside the effort, value and compliance axes - do not re-derive an order here.

| Capability                    | Build in-house                  | Contractor / freelance                     | Agency                            | Community-sourced                        | Default                                   |
| ----------------------------- | ------------------------------- | ------------------------------------------ | --------------------------------- | ---------------------------------------- | ----------------------------------------- |
| Technical blog volume         | slow, high trust                | good for niche depth                       | best throughput, needs a pipeline | write-for-us at scale stage              | buy volume, own outlines and review       |
| Reference documentation       | own it                          | technical writers work well as contractors | rare fit                          | rarely                                   | build, contract for surge                 |
| Quickstart and samples        | own it                          | possible with strict review                | no                                | no                                       | build                                     |
| Conference talks              | own it                          | no                                         | no                                | community speakers extend reach          | build                                     |
| Video production              | script in-house                 | editing and motion work well outside       | good for series                   | community screencasts                    | build the script, buy the post-production |
| Event presence                | staff booths with practitioners | contract logistics                         | full production for own events    | community-run meetups                    | mix                                       |
| Community moderation          | own the decisions               | contracted first-line triage is workable   | risky                             | volunteer moderators with a clear policy | build the policy, extend the staffing     |
| Developer support             | own escalation                  | contracted tier-one possible               | no                                | peer answers with staff backstop         | build the escalation path                 |
| Analytics and instrumentation | own the definitions             | contract the plumbing                      | no                                | no                                       | build definitions, buy tooling            |
| Swag, design, brand assets    | no                              | yes                                        | yes                               | no                                       | buy                                       |

Partner/sponsored has no column here on purpose. It buys placement and access, never output or trust; it answers a channel question rather than a sourcing one.

A sponsored slot is an ad and has to be labelled as one. Send it to `samber/developer-relations-skills@developer-event-sponsorship`.

Treat the default column as a starting point, not a rule. A three-person program with one strong writer and no designers inverts several rows legitimately.

## Red lines - never outsourced

Developers grant approval to people who visibly get it and who will recommend a competitor when it is the right answer (Leslie Hawthorn, "DevRel and the approval economy", developerrelations.com, 2018). Everything below trades on that approval and breaks when rented:

- The advocate's byline, voice and stage presence.
- Technical trade-off calls and any statement about what the product cannot do.
- Incident, outage and breaking-change communication.
- Moderation and code-of-conduct enforcement decisions.
- Answers in the community that carry the company's name.
- The relationship with named champions and design partners.

A useful test: if a developer discovering that a vendor wrote it would feel misled, it is a red line.

## The documented agency pattern

The published model that works splits ownership rather than handing over the surface (Matt Jarvis, Director of Developer Relations at Snyk, "Scaling developer content production at Snyk", developerrelations.com): "our advocate creates an outline and then works with the agency to see it fleshed out."

- Advocates keep ideation and review.
- The agency produces the body.
- Automation carries the coordination because, in his words, "we needed to industrialise this process."

The pipeline setup time and the per-piece latency from that case study are in step 5's option table, where the sourcing decision is made. Two further constants from it, useful as defaults until your own numbers exist:

- Modelled impact per piece: deeper technical pieces around 1,000 sessions, introductory pieces around 500.
- Reported failure points: underestimating outline effort, and an adjustment period for advocates moving into the new workflow.

Read it as a volume-and-compounding play. It does not hit a launch date, and it does not replace an advocate.

## Hidden costs of buying

- **Review load lands on the same bottleneck.** Output multiplies; reviewer hours do not.
- **Brief quality is the ceiling.** A vague outline returns generic content, and generic technical content is worse than none.
- **Latency compounds with revisions.** Two rounds on an eight-week pipeline miss the quarter.
- **Institutional knowledge leaves with the vendor.** Nothing accumulates in the team unless the outlines and the review notes stay in-house.
- **Sameness.** Several vendors serving the same category produce recognisably similar content, which erases differentiation.

## Hidden costs of building

- **Opportunity cost of the generalist.** At seed stage, every hour written is an hour not spent unblocking the first users.
- **Single point of failure.** One person owning docs, talks and community means all three stop when they take leave or resign.
- **Skill mismatch.** An excellent advocate is not automatically an editor, a video producer or a community moderator.
- **Slower ramp.** In-house depth compounds, but the first outputs arrive later than a vendor's.

## Writing the decision into the charter

Record one line per bet: `bet | source (in-house / contractor / agency / community) | latency | setup cost | reviewer | what happens if it stops`. A build-versus-buy line without a named reviewer is the one that fails, because the review step is where the rented output either becomes yours or becomes noise.
