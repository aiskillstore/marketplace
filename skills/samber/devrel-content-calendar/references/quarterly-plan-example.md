# Worked example: one quarter, planned well and planned badly

Illustrative plan for a fictional team: three people (one writer, one advocate, one engineer who reviews at 4 hours/week) on a self-hostable job-queue product with a hosted tier. Funding driver: developer adoption, with existing-user enablement second. Audiences: individual adopters and platform teams introducing it at work.

## Contents

- Section 1: anchors
- Section 2: mix ratios
- Section 3: capacity model
- Section 4: slot table
- Section 5: review ritual and metrics
- Negative example

## Section 1: anchors

| Date | Anchor                           | Class      | Owner    | Consumes                                          |
| ---- | -------------------------------- | ---------- | -------- | ------------------------------------------------- |
| W2   | v3.0 release (breaking changes)  | release    | engineer | release notes, migration guide, upgrade docs      |
| W4   | CFP deadline, ScaleConf          | CFP        | advocate | proposal + abstract                               |
| W6   | Managed-tier pricing change      | launch     | writer   | announcement + FAQ + docs                         |
| W9   | ScaleConf talk (if accepted)     | conference | advocate | slides, demo, companion post, recording follow-up |
| W11  | Upstream runtime LTS release     | ecosystem  | engineer | compatibility note                                |
| W12  | Community office hours (monthly) | community  | advocate | promotion + Q&A write-up                          |

Freeze: W6 (pricing announcement week) - no unrelated publishing. W13: holiday coverage gap, plan nothing.

## Section 2: mix ratios

Twelve committed slots plus three slack slots.

| Axis       | Target                                                     | Rationale                                                          |
| ---------- | ---------------------------------------------------------- | ------------------------------------------------------------------ |
| Surface    | docs 35%, blog 30%, changelog 15%, video 10%, talk 10%     | Adoption driver puts docs first; video capped by editing capacity  |
| Pillar     | enablement 45%, marketing 25%, advocacy 20%, community 10% | Enablement debt from the v3 migration                              |
| Stage      | discover 20%, try 25%, adopt 40%, contribute 15%           | Existing users must survive v3 before new ones arrive              |
| Shelf life | evergreen 60%, timely 40%                                  | Release-heavy quarter; timely share accepted above the usual floor |
| Audience   | individual 50%, platform team 40%, both 10%                | Hosted tier makes the approver audience real                       |

Announcement cap: 2 slots.

## Section 3: capacity model

- Writer: 12 h/week of production time → roughly 1 substantial piece per 2 weeks plus small pieces.
- Advocate: 6 h/week outside events; W8-W9 fully consumed by the talk.
- Engineer reviewer: 4 h/week - the binding constraint. Two review-heavy pieces per month, maximum.
- Slack: 3 unassigned slots (W5, W8, W11) for incident write-ups, upstream breakage, or a slipped anchor.

Consequence recorded at planning time: the benchmark post proposed for W7 was cut, because it needs the same reviewer as the migration guide in the same fortnight.

## Section 4: slot table

| Week | Working title                                     | Surface    | Pillar     | Stage      | Shelf life | Anchor       | Owner    | Reviewer     | Evidence / hypothesis         |
| ---- | ------------------------------------------------- | ---------- | ---------- | ---------- | ---------- | ------------ | -------- | ------------ | ----------------------------- |
| W1   | v3 upgrade path: what breaks and why              | docs       | enablement | adopt      | evergreen  | v3.0         | writer   | engineer     | 14 tickets on failed upgrades |
| W2   | v3.0 release notes                                | changelog  | enablement | adopt      | timely     | v3.0         | engineer | writer       | release                       |
| W3   | Migrating a 200-worker fleet without downtime     | blog       | enablement | adopt      | evergreen  | v3.0         | writer   | engineer     | top forum thread, 40 replies  |
| W4   | ScaleConf proposal (not published)                | talk       | advocacy   | discover   | timely     | CFP          | advocate | writer       | CFP deadline                  |
| W5   | _slack_                                           | -          | -          | -          | -          | -            | -        | -            | reactive buffer               |
| W6   | Pricing change: what it means for self-hosters    | blog + FAQ | marketing  | adopt      | timely     | pricing      | writer   | founder      | announcement                  |
| W7   | "Queue stuck at retry limit" troubleshooting page | docs       | enablement | adopt      | evergreen  | -            | writer   | support lead | 31 tickets, same error string |
| W8   | _slack_ (talk preparation absorbs advocate)       | -          | -          | -          | -          | ScaleConf    | -        | -            | -                             |
| W9   | Talk companion post + slides link                 | blog       | advocacy   | discover   | timely     | ScaleConf    | advocate | writer       | talk lands same week          |
| W10  | Recording + 3 clips + Q&A write-up                | video      | advocacy   | discover   | timely     | ScaleConf    | advocate | writer       | follow-up window              |
| W11  | _slack_ / runtime LTS compatibility note          | changelog  | enablement | adopt      | timely     | ecosystem    | engineer | writer       | upstream date                 |
| W12  | Refresh: quickstart cold-run for v3               | docs       | enablement | try        | evergreen  | -            | writer   | engineer     | quickstart drifted at v3      |
| W12  | Office-hours Q&A digest                           | community  | community  | contribute | evergreen  | office hours | advocate | -            | recurring ritual              |

Repurposing tree for the ScaleConf anchor:

1. Talk.
2. Recording.
3. Clips.
4. Companion post.
5. A troubleshooting page from the audience questions.
6. A slide-derived diagram reused in the migration docs.

Validation result: evergreen 6/12 slots (60%, matches the accepted launch-heavy target), announcements 2/12 (at cap), committed capacity 12 of 15 slots (80%), every slot owned and reviewed, every anchor with preparation and follow-up. Passes.

## Section 5: review ritual and metrics

Monthly, 30 minutes, three questions: what shipped versus slotted, has the mix drifted, which pieces earned a follow-up. Kill rule: a piece whose anchor has passed or that has been re-drafted twice without converging gets cut, out loud. Defer rule: at most one deferral per piece, then it is cut.

Tracked: publish rate (target ≥ 80%), mix drift per axis, anchor coverage, and lead time from "ready for review" to published.

## Negative example

The same quarter, planned the way it usually goes wrong:

| Week | Title                    | Owner |
| ---- | ------------------------ | ----- |
| W1   | v3 is here!              | team  |
| W2   | 5 tips for faster queues | team  |
| W3   | Why we love open source  | team  |
| W4   | v3 deep dive             | team  |
| ...  | one blog post per week   | team  |

What is wrong with it, in order of damage:

1. **No owner or reviewer** - "team" means nobody; every piece stalls at review with no name attached.
2. **One surface** - a v3 with breaking changes and zero docs or migration slots pushes the whole upgrade burden into support.
3. **No anchors beyond the release** - the CFP deadline is missed and the conference talk arrives unprepared.
4. **No evidence** - "5 tips" and "why we love open source" answer no observed question and pass no novelty filter.
5. **No slack** - the first incident or upstream breakage eats a planned slot, and everything after it slides.
6. **No follow-up slots** - the talk, the launch and the release each produce material nobody scheduled.
7. **100% of capacity committed** - publish rate lands far below target, and the team concludes it is bad at writing rather than bad at estimating.
