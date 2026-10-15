# Metrics, Experimentation & Business Math

> Curated, distilled wisdom from @richardrx ("Richard — Design for startups"), translated from Portuguese. Each entry is a reusable principle linked to its source post.

## Duolingo's lesson: optimize the metric that moves DAU, not the borrowed mechanic
**Principle.** Duolingo copied game mechanics twice and failed both (a Gardenscapes moves-counter: neutral; a referral program copied from Uber: +3% because the reward excluded the best users). They stopped picking mechanics and modeled which number to move: bucketing users by engagement and simulating +2%/quarter for 3 years, CURR (current-user retention rate) had ~5x the impact of the next-best metric. Then gamification worked: CURR +21% over 4 years, daily churn of best users −40%+, DAU ×4.5. Leaderboards alone +17% total learning time and tripled highly-engaged learners — because they switched to competing with users of *similar prior-week engagement* (auto opt-in = default effect, no extra tasks).
**Apply when.** Adding gamification by copying a mechanic instead of finding your CURR.
**The move.** Find the single retention metric that compounds your DAU before choosing mechanics. PBL (points, badges, leaderboards) is the free sample — there are ~290 gamification mechanics. Useful three: competition (defined start/middle/end missions), progress bars as trajectory achievement (not just onboarding), engagement-unlocked content (a forecast panel opens only after 30 real entries — blocked as a ladder, not a paywall).
**Visual.** Duolingo's DAU curve from mid-2018 to mid-2022, marked "Started working on CURR" at the inflection, with a 4.5× arrow from there to the top right — `../assets/2081714430811730162__1.jpg`
**Source.** [@richardrx · 2026-07-27](https://x.com/richardrx/status/2081714430811730162)

## Don't mistake signups for traction
**Principle.** Signups are the cheapest action a user takes, so they measure curiosity, not value — especially in freemium. Real growth is whether people come back and do the action that delivers value.
**Apply when.** A rising signup curve on the dashboard feels like proof of traction, particularly under a freemium model.
**The move.** Treat signups as top-of-funnel only — never stop reading there. Track who returns on day 2 and day 7 (D1/D7 retention) and how many complete the value-delivering action (activation). Paid media can inflate signups while real retention stays flat.
**Voice.** "The signup curve climbs with paid traffic, but usage and activation only climb with a good product."
**Source.** [@richardrx · 2026-06-11](https://x.com/richardrx/status/2065082771987394651)

## Don't bet your product on an underpowered A/B test
**Principle.** Most A/B tests in small SaaS lack the volume to prove anything, yet founders swap the whole product on the result. Testing without enough sample to conclude is the trap.
**Apply when.** You're in traction or survival stage, ran a test for a week, saw "variant B won by 12%," and want to ship it everywhere.
**The move.** Before running, compute the minimum sample size (free calculators exist); if you can't hit that floor in reasonable time, don't start. Test big things (headline, offer, pricing structure, onboarding) since large effects need less sample. Never stop a test because the number looked pretty mid-way. With no volume, decide by qualitative research — five good interviews beat an underpowered A/B test. Beware the law of small numbers and confirmation bias.
**Evidence.** ProfitWell is categorical: don't A/B test price — you'll never have the volume or context for it to mean anything.
**Source.** [@richardrx · 2026-06-01](https://x.com/richardrx/status/2061463480868229189)

## Celebrate signal quality, not list size
**Principle.** A waitlist exists to validate that a pain is one people pay to solve — not to sell. Absolute size is a vanity metric; conversion-weighted quality is the real signal.
**Apply when.** You launch a waitlist and feel tempted to celebrate raw headcount.
**The move.** Convert size to expected customers before reacting: a good waitlist converts 15–20% to paying, above 30% is excellent. 53 people at 20% = 10 customers; 1,000 people at 1% = 10 customers — same result, different perception. Until there's a transaction, there's no validated hypothesis.
**Voice.** "Founders celebrate the size of the list when they should celebrate the quality of the signal."
**Source.** [@richardrx · 2026-04-17](https://x.com/richardrx/status/2045094511106220220)

## Translate churn points into LTV, not percentages
**Principle.** Most people watch churn %, but few compute what each point costs in accumulated LTV over 12 months. Cutting churn is a cash lever that needs no price hike or new acquisition.
**Apply when.** You're staring at a churn percentage and treating it as a vanity number rather than money.
**The move.** Do the churn→LTV math: at 25% monthly churn on 1,000 users you must add 250 new users/month just to break even — kill paid traffic and the product dies in ~4 months. Then improve retention without Figma: define the Aha Moment, measure time-to-value (TTV) from signup to it, ask "how do I deliver this faster?", break it into micro-wins if you can't, then test, measure, repeat.
**Evidence.** Finance SaaS, ARPU R$120: cutting churn 5 points (25%→20%) is +R$72,000/year in cash, with no price change and no extra acquisition.
**Source.** [@richardrx · 2026-04-06](https://x.com/richardrx/status/2041184077106004289)

## Nine product metrics, each telling one thing
**Principle.** ARR = size (not necessarily health). Burn rate = risk (time until death). CAC = efficiency (but obsessing over lowering it can worsen conversion with a less-qualified cohort). DAU/MAU = engagement (<20% = bad sign). LTV = product (does the customer see value?). Churn = fit (user doesn't understand or see value → cancels). NRR = real growth (>100% = good). Gross margin = model (<70% in SaaS = problem, except AI wrappers). Runway = survival (<12 months = danger). Metrics are like a blood panel — one bad reading is critical, but all-good is real health.
**Apply when.** A founder fixates on one number or conflates what each metric diagnoses.
**The move.** Use each metric as a diagnostic for its matching layer, then read the full panel before prescribing a fix: ARR alone cannot prove health, low CAC can hide a weak cohort, and strong growth without margin or runway can still be fatal. Treat one bad result as a specific warning and the bundle as the business's health check.
**Source.** [@richardrx · 2026-01-12](https://x.com/richardrx/status/2010675817483817384)
