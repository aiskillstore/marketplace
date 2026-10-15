# Distillation spec — how to turn a new @richardrx post into a skill principle

You are distilling a curated X/Twitter post by **Richard (@richardrx, "Design for
startups")** — a product designer focused on conversion-rate optimization, churn
reduction, and applied behavioral science — into ONE reusable principle for the
Revenue-Centric Design agent skill. The skill is in **ENGLISH**; posts are usually
in Portuguese — translate faithfully into clear, natural English.

## Output format (use EXACTLY this shape)

```
## <short imperative principle title, English>
**Principle.** <1–3 sentences: the core reusable heuristic, generalized, in English.>
**Apply when.** <the trigger/situation where it matters.>
**The move.** <the concrete action/how-to; include framework steps, key numbers, and any NAMED bias/model/framework — KEEP the names (e.g., decoy effect, Zeigarnik effect, Swiss Knife Index, GBB, Eugene Schwartz's 5 awareness levels, loss aversion, peak-end rule, Hick's law).>
**Evidence.** <ONLY if the post cites a study/stat/named case — one tight line. Else omit this line.>
**Visual.** <one line: what an informational image shows> — `../assets/<filename>` <ONLY if the post has an image that carries information (chart, diagram, framework, good/bad UI); for decorative/analogy-only images (e.g. a car photo), omit.>
**Voice.** "<one memorable line, translated, preserving the author's framing>" <ONLY if the post has a punchy line; else omit.>
**Source.** [@richardrx · <YYYY-MM-DD>](<post url>)
```

## Rules

- **Principle-only.** Do NOT include a full translation of the post — distill the reusable idea.
- Keep each entry ~60–110 words. For a long-form [article] post, one comprehensive but skimmable entry with a compact bulleted framework — never a wall of text.
- Preserve the **named mechanism** (the cognitive bias / framework / law) — that naming is the value.
- Be concrete and evidence-led: if the post cites a study, stat, or case, keep the citation attached.
- `[QUOTE]` posts: distill RICHARD's point; use the quoted tweet only as context.
- Images bundled for the skill live in `assets/`; reference them as `../assets/<filename>` (that's the path from inside `references/`).

## Usage boundary (carry forward)

Do not produce a principle that promotes betting, casino, or gambling products. If a
new post is about gambling/betting/casino work, skip it — the skill's reuse permission
excludes that domain.

## Theme routing

Assign the finished entry to exactly ONE theme, then append it (newest-first by date)
to `references/<slug>.md`:

| slug | covers |
|---|---|
| conversion-and-landing-pages | hero/copy, CTAs, social proof, awareness levels, CRO |
| checkout-and-forms | checkout, signup/lead forms, cart abandonment, field friction, trust signals |
| onboarding-and-activation | empty states, aha moment, TTV, activation, trials |
| revenue-centric-design | design philosophy, the RCD principles, process & method |
| pricing-and-monetization | decoy/anchoring, GBB, trial-with-card, upgrades |
| churn-and-retention | cancellation UX, expectation debt, NRR, jobs-to-be-done |
| dashboards-and-data-viz | dashboards, KPIs, data visualization, actionable panels, F-pattern |
| behavioral-science-toolkit | the cross-cutting cognitive biases & persuasion levers |
| product-strategy-and-features | Swiss Knife Index, feature adoption, attention hierarchy |
| positioning-icp-and-gtm | ICP, niche, TAM/SAM/SOM, PLG, Bullseye, first customers, distribution |
| ai-era-differentiation | moats, commoditization, vibe-coding pitfalls |
| metrics-and-experimentation | A/B rigor, vanity metrics, churn→LTV math |

## Worked example (the bar to hit)

```
## Design owns the flow, not the final coat of paint
**Principle.** What decides whether a user converts or churns — information order, when you ask for the card, what appears at moments of doubt, when value is first felt — is set and coded long before a "finished" product reaches design.
**Apply when.** Design is scoped as "make it pretty before launch"; product/eng/requirements own the flow.
**The move.** Pull design upstream to own the flow. To win the argument, show it: Richard built the same app twice (requirements-led vs UX-led) and the side-by-side won him project leadership.
**Voice.** "If I got a buck every time I heard 'design comes in when the product's almost ready,' I'd buy a GT3 RS."
**Source.** [@richardrx · 2026-06-09](https://x.com/richardrx/status/2064327349894553855)
```
