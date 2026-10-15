# Product Strategy & Feature Discipline

> Curated, distilled wisdom from @richardrx ("Richard — Design for startups"), translated from Portuguese. Each entry is a reusable principle linked to its source post.

## Feature requests from cancellations don't buy features
**Principle.** Three auto shops canceled RepareCar over missing boleto (bank-slip) issuance — request logged in Linear with name and date, 20+ in the same queue, oldest since June. But cancellation doesn't buy a feature: the ICP profile is defined, and boleto sits in a deliberately-not-doing package. Support is semi-automated (AI triages, human on novel questions, both open Linear tickets; a daily Claude task prioritizes). Bugs jump the queue; anything new defaults to parking lot.
**Apply when.** Cancelling customers' feature requests pressure the roadmap.
**The move.** Log each request with the customer and date, aggregate demand, then prioritize by bug severity, ICP fit, and strategy — not by the latest cancellation. Default net-new work to the parking lot. When asked for timing, communicate the real queue ("20 requests are ahead of yours") instead of making a false promise.
**Source.** [@richardrx · 2026-08-10](https://x.com/richardrx/status/2086931878251057479)

## Building is the comfort zone; distribution is the game
**Principle.** Founders choose to build because selling hurts — Richard spent 90% of his time perfecting a delivery product one year before iFood existed; it died beautiful. Humane raised ~US$240M, ex-Apple founders, gorgeous hardware; returns outpaced sales by summer 2024 and HP took the assets for US$116M. In survival phase you do both jobs and almost always pick building — your comfort zone — pretending the next feature will make selling easier. Exercise: how many months of runway does your next feature cost?
**Apply when.** Roadmap keeps growing while distribution is untested.
**The move.** Before every roadmap item in the survival phase, ask the post's question — how many months of runway does this feature cost? — and whether it actually makes selling easier or just postpones selling. If the honest answer is "it's the comfortable thing to build," spend that time on the job that hurts: selling.
**Source.** [@richardrx · 2026-07-21](https://x.com/richardrx/status/2079575881115226453)

## 94% of features are filler — Pendo's data and what to do about it
**Principle.** Pendo's analysis across ~2,500 companies' apps found roughly 6% feature adoption in the average product; even top-10% products reached only 15.6%. That leaves about 94% rarely or never used in the average product (84.4% even in the top decile), creating low activation, churn, a larger attack surface, and higher sustaining cost/complexity. Some features sell without being used, but that doesn't explain the gap.
**Apply when.** Auditing a bloated roadmap or justifying a feature purge.
**The move.** Classify every feature by usage correlation: A. Core (the 6% carrying the product; 15% if you're top-10%), B. Strategic (contributes to sales), C. Discard. Then shrink the product based on use and/or cash generation.
**Source.** [@richardrx · 2026-07-17](https://x.com/richardrx/status/2078079228717764886)

## PMF is step 8 in a 10-step sequence — founders start there too early
**Principle.** Sequence: (1) Define the ICP — does it really exist, or is it who you wish it were? (2) Surface the ICP's pains and desires — real? verified where, with how many? (3) Understand awareness level — knows the pain? the solution? yours? (4) Slice niche/sub-niche — their particularities, do they exclude each other? (5) Size TAM of niche and sub — enough market, and does enough remain after niching? (6) Actively decide who the solution serves — can you stand out there? (7) Validate the thesis — the ICP's pain solved in a way that pays; are they paying? (8) Reach PMF — does the product stick? do users recommend it unprompted? does the business sustain itself without you pushing? (9) Fix inefficiencies in acquisition, activation, retention — always leaks; measured where? (10) Scale.
**Apply when.** A founder says they "want PMF" without the groundwork.
**The move.** Work the sequence in order and require evidence at each gate: a verified ICP and pain, a viable niche/TAM, paying thesis validation, then PMF. Only after measuring and fixing acquisition, activation, and retention leaks should you scale.
**Source.** [@richardrx · 2026-07-09](https://x.com/richardrx/status/2075192130184630688)

## Feature creep ("fiturite") is a business cost, not just a UX one
**Principle.** The Homer Simpson car problem: every unsatisfied user request implemented as a feature eventually makes the product hard to operate, steepens the learning curve, and worsens experience through cognitive overload and choice paradox. It's bad for the business too — you spend more on dev for features serving few users, more on maintenance, eventually whole teams for barely-needed areas. Prune based on: who are our most strategic users, what are they using, what's unused that I can abstract, what aligns with the vision.
**Apply when.** A product keeps growing features without a subtraction ritual.
**The move.** Treat pruning like a cost line: grass grows by itself, you have to mow. Look for low-usage features serving low-paying/high-churn subniches and cut them to serve better those who pay more and stay longer.
**Source.** [@richardrx · 2025-11-03](https://x.com/richardrx/status/1985329704312709254) and [@richardrx · 2026-07-06](https://x.com/richardrx/status/2074118439321350163)

## Maturing the product means doing the same thing better, not adding power-user features
**Principle.** Technical founders keep densifying the product for heavy users, making it expensive, complex, and hard for the average user — a Boeing 747 cockpit. Maturing means doing better what the product already does: smoother flows, bug fixes, attention direction. Hidden risk: a power-user product has a smaller top of funnel, so you must charge more — you changed markets (TAM/SAM changed) and price must follow. The founder then reads "product is bad" when really ICP isn't adjusted. Adjust copy (more executive, less tool-like), visuals (show the result, less product internals), and detail care (high-paying ICP tolerates AI-slop design less).
**Apply when.** The product keeps getting denser and conversion falls.
**The move.** Stop adding depth by default; smooth the core flows, fix bugs, and direct attention first. If the product is deliberately moving upmarket, recalculate TAM/SAM and price, then align the ICP, copy, visuals, and detail quality with that smaller, higher-value market.
**Evidence.** Christoph Janz's five paths to $100M — from the elephant (few customers paying a lot) to the fly (millions paying little) — all work; the problem is becoming an elephant without noticing and still charging mouse prices.
**Source.** [@richardrx · 2026-07-02](https://x.com/richardrx/status/2072718071060447691)

## Run every feature through a two-layer "Swiss Knife filter" before building
**Principle.** A feature you ship stays forever and charges rent forever, so the right question isn't "is this good?" but "does it deserve the permanent cost it imposes on the product?"
**Apply when.** A roadmap item feels appealing but nobody applied a filter before committing to build.
**The move.** Layer 1 — does it deserve to exist? Pass all four: (1) cognitive load (more surface = more to learn + Hick's law decision time); (2) ICP specificity (a CRM for facial-aesthetics clinics charges 5x a generic one); (3) operational cost (maintain/support/document, not build); (4) reinforces the core claim. Layer 2 — build now? Two axes: easily rejectable (clear "no"?) and easily implementable (cost to the validating version, not the dream version). Build the no-brainers first; fail any of the four, kill it guilt-free. To rank survivors, score (New Users + New Revenue + Impact Level) / Effort.
**Visual.** Prioritization scoring table: (New Users + New Revenue + Impact Level) / Effort = Score — `../assets/2059236567533650119__1.jpg`
**Voice.** "Every feature that gets in, stays. And it charges rent forever."
**Source.** [@richardrx · 2026-05-26](https://x.com/richardrx/status/2059236567533650119)

## Feature adoption is a design problem, not a communication problem
**Principle.** Shipping a feature doesn't make it discovered; users move through their habitual path and never see what they aren't looking for.
**Apply when.** Three weeks post-launch only ~9% of active users opened the feature and ~4% used it twice, despite changelog, email, and "new" badges.
**The move.** Stop treating adoption as announcement. The killers are inattentional blindness (users don't see what they aren't seeking) plus status-quo bias (re-learning cost outweighs perceived benefit even when the new way is better). Instead: directional empty states that surface the feature where it'd be used; triggered onboarding fired by the behavior that signals need (CRM user hits the sales page → introduce the objection-busting AI); and a feature adoption rate metric measuring habit/appropriate frequency, not clicks. Anything below an adoption threshold goes back into review.
**Voice.** "Launching a feature is easy; getting it used is a whole other thing."
**Source.** [@richardrx · 2026-05-20](https://x.com/richardrx/status/2057162392048476345)

## Compute your Swiss Knife Index to expose feature creep
**Principle.** A product's worth is measured by features actually used, not features shipped; a bloated product is expensive to sustain and hard to sell, not rich.
**Apply when.** The roadmap has become a user wishlist and every new feature feels like progress (especially with AI making building cheap).
**The move.** Swiss Knife Index (SKI) = (features used by >40% of active users in a 30-day window) ÷ (total features). Below 0.3, you own a clumsy Swiss army knife. Fix it with: quarterly audits on real usage data (not team opinion); hide, don't delete (push rarely-used features into advanced settings — reachable for the 3%, gone for the 97%); and a gate on every new feature — "which existing feature do I kill to make cognitive room?" Litmus test: which feature would you show first with 30 seconds to sell? The rest stays invisible until needed. See the academic grounding (2034248739557159293) and the curve (2033880553607364684).
**Visual.** SKI curve — perceived utility rises then declines past the optimal point as complexity keeps climbing — `../assets/2057124008445796659__1.jpg`
**Voice.** "Which feature would I show first if I had 30 seconds to sell the product?"
**Source.** [@richardrx · 2026-05-20](https://x.com/richardrx/status/2057124008445796659)

## Design the attention hierarchy to direct behavior, not just organize info
**Principle.** A product that organizes delivers access; a product that directs delivers activation — and the visual hierarchy decides which the user gets.
**Apply when.** "My interface looks good, but people don't use the main features" — and the key feature is buried behind three clicks the user will never make.
**The move.** Recognize that attention hierarchy is the structure deciding what users see first, find with effort, or never discover. Built without intent, the product sabotages itself: users use what's most salient, which is rarely what retains. Plan the hierarchy to influence behavior — make the value-driving, retention-driving feature the most prominent thing — instead of merely arranging information neatly.
**Visual.** A typographic demo (huge headline "YOU WILL READ THIS FIRST") proving the eye follows visual weight, not reading order — `../assets/2039399756452057159__1.jpg`
**Voice.** "A well-designed attention hierarchy makes the user use what retains; a bad one makes them use what's most salient."
**Source.** [@richardrx · 2026-04-01](https://x.com/richardrx/status/2039399756452057159)

## Ground feature discipline in the academic feature-fatigue research
**Principle.** Past a cognitive-load threshold, the subjective evaluation of a product doesn't stay neutral — it declines into frustration, confusion, and task abandonment, directly hitting CAC and LTV.
**Apply when.** You need the evidence behind cutting features, and want to separate pre-purchase appeal from post-purchase utility.
**The move.** Apply the SKI as a decision criterion grounded in feature fatigue. More features help pre-purchase comparison via distinction bias but hurt the decision via analysis paralysis (more options = longer decisions and more no-decisions; no decision, no conversion). Each extra feature steepens the learning curve — measurable B2B productivity loss — and when value comes slowly, users silently churn before the trial ends, blaming themselves, not the product. This complements the index (2057124008445796659) and the curve (2033880553607364684).
**Evidence.** Thompson, Hamilton & Rust (2005), "Feature Fatigue," JMR 42(4); distinction bias (Hsee & Zhang 2004); analysis paralysis (Iyengar & Lepper 2000).
**Voice.** "A product that grows without criteria doesn't get rich — it gets expensive to sustain and hard to sell."
**Source.** [@richardrx · 2026-03-18](https://x.com/richardrx/status/2034248739557159293)

## Past the optimal feature count, a technically bigger product becomes functionally worse
**Principle.** The relationship between feature count and perceived utility is non-linear: there's an optimal point, after which each added feature reduces perceived utility while raising sustaining cost and the learning curve.
**Apply when.** You hear "my interface looks good, but people don't use the main features" — a sign you've passed the optimal point.
**The move.** Read the SKI curve: utility climbs to a peak (~10 features in the example) then falls as complexity keeps rising. The fix isn't more visibility — it's reducing the product's cognitive load so the rest becomes visible again. Criterion: any feature used by under 10% of the active base must justify its existence or leave. There's no universal ideal count — only the ideal for your ICP, context, and device.
**Visual.** SKI graph: green perceived-utility curve peaks at the optimal point (10.3 features, 97), red complexity curve rises monotonically and overtakes utility in the "decline zone" — `../assets/2033880553607364684__1.jpg`
**Voice.** "A bloated product isn't a rich product — it's a product actively destroying the conversion and retention you paid dearly to win."
**Source.** [@richardrx · 2026-03-17](https://x.com/richardrx/status/2033880553607364684)

## Focus on your core; trying to be "all-in-one" dilutes your value proposition
**Principle.** Chasing a bigger TAM by going generic destroys retention of your heavy users without converting new ones — the same roadmap mistake in cars and in software.
**Apply when.** The product is tempted to "embrace the world" and become a do-everything tool, abandoning the specific ICP that made it loved.
**The move.** Remember who your ICP actually is and build for them, even at the expense of broad appeal. In software, when UI/UX tries to cover everything, the value proposition dilutes: you wreck heavy-user retention and fail to convert newcomers because you've gone generic. Focus relentlessly on the core.
**Evidence.** Porsche chased China's TAM with generic EVs, abandoning its ICP (visceral flat-six machines); ~€3.9B in losses to reverse the roadmap — operating profit fell from €4,000M (2022) to €40M (9M 2025), margin 18% → 0.2%. [Porsche figures from the quoted post; treat as illustrative.]
**Voice.** "Focus on your damn core."
**Source.** [@richardrx · 2026-03-11](https://x.com/richardrx/status/2031722047080960265)
