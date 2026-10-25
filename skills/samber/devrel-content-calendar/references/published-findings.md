# Published findings and self-set baselines

Every number and named idea this skill quotes, with its source and its limits. Read this before defending a figure to a user, and before adding a new one.

## Contents

- Throughput and lead times (case study)
- The 80/20 planning convention
- Ratios that are folklore
- This skill's own baselines
- Named ideas: kept, rejected, unattributed
- Sources

## Throughput and lead times (case study)

Source: Matt Jarvis, Director of Developer Relations at Snyk, "Scaling developer content production at Snyk", developerrelations.com case study (page undated).

| Figure                                                                                                      | Stated as                                              | Use it for                                                                                                                                   |
| ----------------------------------------------------------------------------------------------------------- | ------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------- |
| "one or maybe two blog posts per month" per developer advocate                                              | The team's output _before_ it built a scaling pipeline | Challenging an optimistic estimate. An advocate who also runs events and answers the community does not write four substantial posts a month |
| 8-9 weeks, conception to publication, when a third party writes                                             | Their measured pipeline latency                        | Booking agency or freelance work against an anchor date                                                                                      |
| ~6 months of the director's own time to industrialise the pipeline                                          | Setup cost before volume                               | Warning a user that outsourcing does not relieve this quarter                                                                                |
| ~1,000 sessions for a deeper technical piece, ~half for an introductory one, in the month after publication | Their forecasting model                                | Ranking formats by return when the goal is search-driven reach                                                                               |
| Up to 30,000 sessions for a reactive news piece, "once or twice a year"                                     | Observed, from their Log4Shell coverage                | Justifying unassigned slack. The best piece of the quarter is often unplannable                                                              |

Caveats: one company, security tooling, SEO-led programme. The traffic numbers depend entirely on that company's domain authority and say nothing about what a new project should expect.

## The 80/20 planning convention

Two widely distributed planning skills land on the same split:

- `anthropics/knowledge-work-plugins@capacity-plan`: IC/specialist target utilisation 75-80%, and "Target 80% utilization. 100% means no room for surprises."
- `anthropics/knowledge-work-plugins@campaign-plan`: "build in flexibility: leave 20% of calendar slots open for reactive or opportunistic content."

That convergence makes 80/20 a defensible default and nothing more. Both count in writer hours or campaign slots rather than reviewer passes - the constraint that actually binds a developer-content plan.

The same campaign skill publishes production timings (blog post 3-5 business days, landing page 5-7, video 2-4 weeks). Treat them as a floor for developer content: they assume no SME review and no code that has to run.

## Ratios that are folklore

An 80% evergreen / 20% trending split circulates widely in creator-economy material, adjusted to roughly 60/40-70/30 for fast-moving technical niches. The material that carries it describes it as "the widely-reported baseline among solo creators": short-form video accounts, with none of the review cost technical content carries.

Cite the mechanism instead: evergreen pieces keep earning search and support deflection after the release that prompted them, which is what makes the next quarter cheaper. Never quote the ratio as a benchmark.

## This skill's own baselines

State these as proposals, not findings, and replace them with the team's real numbers whenever those exist:

| Baseline                                                          | Why this value                                                                                                                                                                     | What would replace it                                                                  |
| ----------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| Publish rate ≥ 80%                                                | Matches the 80/20 capacity convention: if you committed 80% of capacity, you should be shipping what you committed                                                                 | Last quarter's actual published ÷ slotted                                              |
| Evergreen majority outside a launch-dominated quarter             | Follows from the compounding argument above, not from a measured optimum                                                                                                           | The team's own decay curve: how long a piece keeps earning                             |
| At least three surfaces, at least two journey stages              | A coverage floor, chosen so a single-surface plan fails the check loudly                                                                                                           | The surfaces the audience actually uses, from analytics                                |
| Announcement cap agreed per quarter                               | The defensible number is team-specific; forcing the user to name one is the point                                                                                                  | Whatever the user commits to in step 3                                                 |
| Evergreen-compounding ranked first among the three quarter shapes | Capacity judgement, not a measurement: it is the cheapest shape to run and the only one that compounds, and it ranks first partly to counter the deadline pressure that starves it | The team's own record of what actually shipped per shape, and what each shape returned |

## Named ideas: kept, rejected, unattributed

**Kept - the playground mindset.** Ashley Faus (Atlassian; author of _Human-Centered Marketing_) on her own site: "The buyer's journey is broken. It was never linear, but we need to shift to the playground mindset." Readers enter a topic at whatever depth suits them rather than walking a funnel. This is why journey-stage labels in the slot table are a coverage check, not a claim about reader order.

**Kept - demand-driven sourcing.** "Using support questions to feed your content calendar" (Matthew Revell, developerrelations.com, 2018-10-04) documents the pipeline:

- Find where developers already ask.
- Assign the monitoring.
- Categorise by product area.
- Convert repeats into content in several formats.
- Measure and repeat.

It carries Martyn Davies on the fear of covering the same ground twice - "repetition isn't a risk - it's a necessity" - because developers discover content through different channels and almost nobody sees all of them. Repeat the topic across surfaces and keep one canonical URL.

**Rejected - Hero / Hub / Help.** Google's 3H video model is frequently name-dropped in content-planning material, but it is built for a brand's video channel rather than for docs and release notes. Leave it out.

**Unattributed - the cost ladder.** Test an idea in the cheapest format first and promote only the winners up the production-cost ladder. Circulates attributed to Alex Hormozi, unverified. Use the mechanism for bet slots - a community post or a talk pitch is a cheap test before a topic earns an expensive tutorial slot - and skip the attribution.

## Sources

- Matt Jarvis / Snyk, "Scaling developer content production at Snyk", developerrelations.com case study.
- Matthew Revell, "Using support questions to feed your content calendar", developerrelations.com, 2018-10-04.
- Ashley Faus, ashleyfaus.com.
- `anthropics/knowledge-work-plugins`, skills `campaign-plan` and `capacity-plan`.
