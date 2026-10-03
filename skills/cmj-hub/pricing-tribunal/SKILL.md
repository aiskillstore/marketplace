---
name: pricing-tribunal
description: The capstone workflow for high-stakes pricing decisions. Four stages — Hypothesize, Test, Adjudicate, Audit — that make material pricing changes safe to ship at speed. Loaded by the main pricing skill when the operator faces a decision material to ARR (new tiers, value-metric switch, raise-the-base, outcome guarantee, kill a tier, change discount policy). Outputs a tribunal-defensible pricing plan + verdict matrix + 30/60/90 audit cadence.
user-invocable: false
allowed-tools: Read
  - Write
license: MIT

---

# Pricing Tribunal — sub-skill

The high-stakes pricing decision workflow. When the change is
material to ARR (>5% revenue impact OR affects >20% of customers
OR touches the value metric), route through the tribunal — not
through "let's just try it and see."

## Activation

The main `pricing` skill routes here when:

- The operator describes a change material to ARR
- `pricing-audit` or `pricing-diagnostic` recommends "tribunal"
- The operator explicitly asks "I'm thinking about [change]"
- The change touches: value metric, base price, top tier elimination,
  outcome guarantee structure, or discount policy

## The four stages

```
Hypothesize  →  Test  →  Adjudicate  →  Audit
  (week 0)     (1-6)     (week 7)     (30/60/90)
```

### Stage 1 — Hypothesize (week 0)

Name the pricing hypothesis SPECIFICALLY. Format:

> **If** [the change], **then** [expected outcome with magnitude + direction],
> **because** [the mechanism]. **Downside risk** [where it concentrates +
> magnitude]. **Test predicts** [observable that would falsify].

Example:

> **If** we shift from $299 flat to $0.05 per API call with a $99 minimum,
> **then** mid-market ACV +25% and free-tier conversion +15% in Q1,
> **because** the value metric finally tracks customer success and the
> $99 minimum eliminates the friction of the previous flat tier.
> **Downside risk** concentrated in low-volume customers (~5% of base,
> ~2% of ARR) who may churn at the new minimum.
> **Test predicts** new-logo ACV in the per-API cohort lifts ≥15% within
> 60 days while free-tier conversion holds or rises.

Hypothesis quality checklist:

- [ ] Names the change concretely (no "improve pricing")
- [ ] States expected magnitude + direction
- [ ] Cites the mechanism (which JMC principle applies)
- [ ] Names where downside risk concentrates
- [ ] States what observable would falsify

### Stage 2 — Test (weeks 1-6)

Controlled tests WITHOUT public damage. Test options:

| Test | When to use | Risk profile |
|---|---|---|
| **Private beta** | Net-new logos, hidden URL or invite-only | Lowest risk |
| **Grandfather-clause** | Existing customers stay on old pricing, only new logos see new price | Low risk |
| **Sales-led pilot** | Sales reps offer new price to 10-20 selected prospects | Low-medium |
| **Geographic/segment cohort** | One geo or PSP segment gets the new price | Medium |
| **Ramp** | 10% of new sign-ups → 30% → 100% over 4-6 weeks | Medium-high |
| **Live test on a single tier** | Decoy or anchor change, target tier unchanged | Medium-high |
| **Full cutover** | NOT a test — only if hypothesis is high-confidence + reversible | Highest risk |

Test design rules:

1. **Run to statistical significance** OR document the test as
   inconclusive. Never decide on vibes.
2. **Predict the lift direction + magnitude UP FRONT.** Post-hoc
   rationalization is forbidden.
3. **Document every input change** (price, copy, layout) — if you
   change two things you can't attribute the result.
4. **Set a kill-switch threshold.** "If close-rate drops below X
   in week 2, pull the test."

### Stage 3 — Adjudicate (week 7)

The verdict matrix:

| Question | Pass | Fail |
|---|---|---|
| Did the test reach the predicted direction? | Yes (sign matches) | No |
| Did the test reach the predicted magnitude (±20%)? | Yes | No |
| Were side effects within prediction? | Yes | No |
| Is the downside risk concentration matching predicted? | Yes | No |
| Does product + sales + finance sign off in writing? | Yes | No |

Verdict outcomes:

- **All Pass** → ROLL OUT (with the documented rollout plan)
- **Direction + Magnitude Pass, side effects Fail** → ITERATE (refine,
  retest, re-tribunal)
- **Direction Pass, Magnitude Fail (lift smaller than predicted)** → 
  ITERATE or ABANDON (depending on cost of switching back)
- **Direction Fail** → ABANDON + update the diagnostic framework
  (the test exposed a wrong assumption — capture it)

### Stage 4 — Audit (30 / 60 / 90 days post-rollout)

At each interval, re-run the verdict matrix against actuals:

- Did the LIVE result match the test result?
- Are side effects emerging that the test didn't surface?
- Is the downside concentration as expected?

If actuals diverge from test predictions in 30-day audit, the
divergence reason gets documented in the failed-test registry. The
discipline is what compounds — not any single win.

## Decision routing

When operator describes a change, classify risk tier:

| Risk tier | Definition | Workflow |
|---|---|---|
| **Routine** | <2% ARR impact, <5% of customers affected, reversible in <30 days | Skip tribunal; route to `pricing-pocket-waterfall` or `pricing-contrast-set` |
| **Material** | 2-10% ARR impact, 5-20% of customers, reversibility in 30-90 days | Full tribunal, 6-week test window minimum |
| **Strategic** | >10% ARR impact, >20% of customers, or value-metric change, or hard to reverse | Full tribunal + executive review + 8-12 week test window + grandfather-clause mandatory |

## Workflow

### 1. Classify the change

Ask the operator the 3 risk-tier questions. Route accordingly.

### 2. Hypothesize

Walk the operator through the hypothesis template. Refuse to proceed
without all 5 fields populated.

### 3. Design the test

Pick a test from the table based on risk tier. Document:

- Test type
- Cohort size + selection method
- Duration
- Kill-switch threshold
- Sign-off owners

### 4. Output the tribunal plan

```
Pricing Tribunal Plan — {change name}
─────────────────────────────────────────────────────────────────

RISK TIER: {Routine / Material / Strategic}

HYPOTHESIS:
{full hypothesis with all 5 fields}

TEST DESIGN:
- Type: {private beta / grandfather / pilot / ramp / cohort}
- Cohort: {size + selection criteria}
- Duration: {N weeks}
- Kill-switch: {threshold + condition}
- Sign-offs: {product, sales, finance, exec}

ADJUDICATION DATE: {date}
30-DAY AUDIT: {date}
60-DAY AUDIT: {date}
90-DAY AUDIT: {date}

PREDICTED LIFT: {direction + magnitude}
FALSIFICATION CONDITION: {what would prove the hypothesis wrong}
```

### 5. Sign-off + calendar

Confirm with the operator:

- Calendar holds set for adjudication + 30/60/90 audits
- Sign-off requests sent to listed owners
- Kill-switch threshold tracked in monitoring

## Self-check

- [ ] Risk tier classified correctly (don't tribunal routine changes; don't skip on strategic)
- [ ] Hypothesis has all 5 fields including falsification condition
- [ ] Test type matches risk tier
- [ ] Kill-switch + threshold documented
- [ ] All audit dates calendared
- [ ] Sign-off owners named

## Reference

- `../../pricing/references/pricing-framework.md` — the tribunal frame in context
- `../pricing-audit/SKILL.md` — what feeds into the tribunal
- `../pricing-pocket-waterfall/SKILL.md` — for routine discount-policy changes
