# Mix and capacity model

Reference for steps 2-5 of the workflow: what the mix axes are, how the funding driver sets the ratios, what each format costs, and where topics come from.

## Contents

- Mix axes
- Ratios by funding driver
- Format cost bands
- Demand signals and bets
- Routing a topic to the right surface

## Mix axes

| Axis          | Values                                                                                                                                                                   | Unbalanced result                                              |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------- |
| Surface       | docs page, quickstart, tutorial, reference update, blog post, changelog/release notes, video/screencast, conference talk, community post or AMA, newsletter, sample repo | Blog-only plan: adoption blocked in docs nobody planned        |
| Pillar        | advocacy, marketing, enablement, community                                                                                                                               | Everything lands in marketing; enablement debt grows unnoticed |
| Journey stage | discover, try, adopt, contribute, advocate                                                                                                                               | Discover-only plan: traffic without activation                 |
| Shelf life    | evergreen (survives the next release), timely (release/event/news-bound)                                                                                                 | Timely-only plan resets to zero each quarter                   |
| Audience      | individual adopter, buying organisation, ecosystem segment, new vs. existing user                                                                                        | One blended voice answers neither audience                     |

Write the ratios as percentages of slots, not of hours - hours hide the fact that one talk costs six blog posts.

## Ratios by funding driver

The mix follows the reason the program is funded. Use this as a starting point, then adjust with the user; never present it as a fixed standard.

| Driver                                                    | Weight toward                                                                 | Typical anchor of the quarter       |
| --------------------------------------------------------- | ----------------------------------------------------------------------------- | ----------------------------------- |
| Developer adoption (developers are the buyers)            | enablement + try/adopt stage, self-serve paths                                | product releases                    |
| Sales enablement (developers evaluate, someone else buys) | evaluation material for approvers: security, licence, cadence, migration cost | proof points and comparison content |
| Enablement of existing users                              | docs, troubleshooting, migration guides, tutorials                            | version releases and deprecations   |
| Product feedback                                          | community-facing formats that generate conversation                           | previews, RFCs, office hours        |
| Ecosystem and partners                                    | integration guides, sample repos, partner co-content                          | partner launches                    |
| Contributor community                                     | contributor onboarding, governance posts, roadmap transparency                | release cycles and community events |
| Employer branding                                         | engineering deep dives, architecture and incident write-ups                   | conferences                         |

Sanity checks apply to every driver:

- Majority of slots evergreen, unless the quarter is deliberately launch-dominated.
- A capped share for announcements.
- At least one slot serving each audience the user named.

The evergreen-majority rule is this skill's working baseline rather than a measured optimum - present it that way, and drop it the moment the team has its own decay data.

## Format cost bands

Estimate in passes, not drafting hours. A pass is one of:

- Research.
- Drafting.
- Writing code that must run.
- Technical review by someone who can dispute the claims.
- Assets (diagrams, screenshots, recordings).
- Publishing.
- The post-publication reply load.

| Format                                                | Distinguishing cost                                               | Usual bottleneck                                                     |
| ----------------------------------------------------- | ----------------------------------------------------------------- | -------------------------------------------------------------------- |
| Changelog entry / release note                        | Small, but tied to the release date                               | Release engineering                                                  |
| Short community post or AMA                           | Low production, high reply load                                   | Author availability after publishing                                 |
| Docs page or troubleshooting page                     | Correctness review, canonical placement                           | Docs review queue                                                    |
| Quickstart                                            | Cold-run verification on a clean machine                          | Test environment                                                     |
| Engineering blog post                                 | Claim-to-evidence checking                                        | Technical reviewer                                                   |
| Tutorial                                              | Working code plus checkpoint verification at every step           | Reviewer plus environment                                            |
| Benchmark or migration guide                          | Reproducible measurements, honest limitations                     | Engineering time, and it fails late                                  |
| Video/screencast                                      | Recording, editing, re-record cost after any product change       | Editing capacity                                                     |
| Conference talk                                       | Deadline is external, preparation compresses into the final weeks | Speaker's calendar                                                   |
| Anything written outside the team (agency, freelance) | Outline and review still cost internal passes                     | Round-trip latency, eight to nine weeks in the one published account |

Two lead times are systematically underestimated:

- Review by people who do not report to the content owner.
- Anything requiring code that must actually run.

A per-person reality check before committing the plan: the only published devrel figure puts an advocate at one to two blog posts a month before any production pipeline exists. An estimate far above that needs an explanation - a dedicated writer, an agency, or smaller formats.

## Demand signals and bets

Demand-sourced slots (evidence required):

- Repeated support tickets and their resolution notes.
- Questions asked more than twice in the community channel or public Q&A.
- Issues filed against the same confusion; docs-site searches returning nothing.
- Error telemetry - the only signal showing failures nobody reported.

The volume sets the label:

- A question asked three times is a missing page.
- A question asked thirty times is a docs or product defect; say which in the slot.

Bet slots (hypothesis required) must pass a novelty filter. An idea passing none of the criteria below produces an accurate, unread piece:

- Counter-intuitive.
- Counter-narrative.
- Surprising.
- An elegant articulation of something readers already feel.

Deliberate repetition across surfaces is coverage, not waste - developers discover content through different channels and almost nobody sees all of them. Keep one canonical URL per topic so search authority is not split.

## Routing a topic to the right surface

| Signal                                       | Surface                          |
| -------------------------------------------- | -------------------------------- |
| A step in the product is broken or unclear   | Docs fix                         |
| A specific error string                      | Troubleshooting page             |
| "How do I do X end to end"                   | Tutorial                         |
| "How do I get started at all"                | Quickstart                       |
| "Why is it built this way" / trade-off story | Engineering blog post            |
| Version-specific change                      | Release notes or migration guide |
| Decision-stage comparison for an approver    | Evaluation page, not a blog post |

Choosing the surface at planning time is what stops the blog from becoming the dumping ground for content that belongs in the docs.
