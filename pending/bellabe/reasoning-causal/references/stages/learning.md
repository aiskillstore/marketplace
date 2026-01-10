
# Stage 7: Learning (Validation)

You are an expert at evidence-based learning and systematic knowledge capture. Your role is to close the feedback loop by documenting results, validating hypotheses, and automatically updating the Canvas.

## Purpose

Complete the causal flow by:
- Documenting actual results vs expected outcomes
- Validating or invalidating hypotheses from Stage 2
- Identifying surprises (positive and negative)
- Automatically updating Canvas with validated evidence
- Generating new threads from discovered opportunities
- Calculating accuracy of predictions

## Core Principle

**Every thread must produce validated learning that updates the Canvas. Otherwise, it was just activity, not progress.**

## When to Use

- After Stage 5 (Actions) complete and results are observed
- Documenting outcomes from completed initiatives
- Quarterly Canvas validation reviews
- Closing threads with lessons learned

## Learning Document Structure

Create: `threads/operations/{thread-name}/6-learning.md`

### Template

```markdown
---
thread: {thread-name}
stage: 6-learning
date: {YYYY-MM-DD}
owner: ai-agent
canvas_updates: [section-ids that will be updated]
validation_result: success | partial | failure
---

# Learning: {Title}

## Results Summary

**Expected:** {Summary from Stage 4 - what we predicted}
**Actual:** {What actually happened}
**Variance:** {Difference between expected and actual}

**Overall Assessment:** {success | partial | failure}

---

## Outcome Metrics

### Primary Metrics
| Metric | Target | Actual | Variance | Status |
|--------|--------|--------|----------|--------|
| {Metric 1} | {Target} | {Actual} | {+/-X%} | ✅ ❌ ⚠️ |
| {Metric 2} | {Target} | {Actual} | {+/-X%} | ✅ ❌ ⚠️ |
| {Metric 3} | {Target} | {Actual} | {+/-X%} | ✅ ❌ ⚠️ |

**Legend:**
- ✅ Met or exceeded target
- ⚠️ Within 20% of target
- ❌ Missed by >20%

### Secondary Metrics
| Metric | Target | Actual | Variance |
|--------|--------|--------|----------|
| {Metric 1} | {Target} | {Actual} | {+/-X%} |
| {Metric 2} | {Target} | {Actual} | {+/-X%} |

---

## Hypothesis Validation

### Hypothesis {ID}: "{Hypothesis text}"
**Original Status:** {From Stage 2: challenged/validated/new}
**Original Confidence:** {X%}
**Final Status:** ✅ VALIDATED | ❌ INVALIDATED | ⚠️ INCONCLUSIVE
**Final Confidence:** {Y%}

**Evidence:**
- {Data point 1 from results}
- {Data point 2 from results}
- {Pattern observed}

**Analysis:**
{2-3 sentences explaining why hypothesis was validated/invalidated}

**Canvas Impact:**
- Update `canvas/{section}.md` → {Specific change}

---

### Hypothesis {ID}: "{Hypothesis text}"
**Original Status:** {From Stage 2}
**Original Confidence:** {X%}
**Final Status:** ✅ VALIDATED | ❌ INVALIDATED | ⚠️ INCONCLUSIVE
**Final Confidence:** {Y%}

**Evidence:**
- {Data point}

**Analysis:**
{Explanation}

**Canvas Impact:**
- Update `canvas/{section}.md` → {Specific change}

---

## Surprises

### Positive Surprises
**Surprise 1:** {What happened that we didn't expect}
- **Impact:** {How this helps}
- **Opportunity:** {New thread or action to pursue}
- **New Hypothesis:** {If this reveals new pattern}

**Surprise 2:** {Unexpected positive outcome}
- **Impact:** {How this helps}
- **Opportunity:** {What to do about it}

### Negative Surprises
**Surprise 1:** {What went wrong unexpectedly}
- **Impact:** {How this hurts}
- **Root cause:** {Why it happened}
- **Mitigation:** {How to prevent in future}
- **New Risk:** {Add to risk register}

**Surprise 2:** {Unexpected negative outcome}
- **Impact:** {Consequences}
- **Root cause:** {Analysis}
- **Mitigation:** {Prevention}

---

## Canvas Updates Required

### 04.segments.md
**Change:** {What needs updating}
**Rationale:** {Why based on evidence}
**Confidence:** {X%}

### 12.revenu.md
**Change:** {What needs updating}
**Rationale:** {Why based on evidence}
**Confidence:** {X%}

### 10.assumptions.md
**Update A{ID}:** {Assumption text}
- Status: {Before} → {After}
- Confidence: {X%} → {Y%}
- Evidence: {Link to this learning doc}

**Update A{ID}:** {Assumption text}
- Status: {Before} → {After}
- Confidence: {X%} → {Y%}
- Evidence: {Link to this learning doc}

**Add H{ID}:** {New hypothesis}
- Status: NEW
- Confidence: {X%}
- Test: {How to validate}

---

## Prediction Accuracy

**Decision Stage Predictions (from 4-decision.md):**

### 3-Month Predictions
| Prediction | Actual | Accuracy |
|------------|--------|----------|
| {Prediction 1} | {What happened} | {%} |
| {Prediction 2} | {What happened} | {%} |

### 6-Month Predictions
| Prediction | Actual | Accuracy |
|------------|--------|----------|
| {Prediction 1} | {What happened} | {%} |

### Overall Prediction Accuracy
**Average accuracy:** {X%}
**Best prediction:** {Which one}
**Worst prediction:** {Which one}

**Lessons:**
- {What to improve in future predictions}

---

## What Worked Well

1. **{What went right}**
   - Why: {Root cause of success}
   - Replicate: {How to repeat this}

2. **{What went right}**
   - Why: {Root cause}
   - Replicate: {How to repeat}

---

## What Didn't Work

1. **{What went wrong}**
   - Why: {Root cause of failure}
   - Fix: {How to prevent in future}
   - Impact: {Cost/delay caused}

2. **{What went wrong}**
   - Why: {Root cause}
   - Fix: {Prevention}

---

## Next Actions

### Canvas Updates (Automated)
- [x] Update assumption A{ID} status and confidence
- [x] Update section {X} with validated evidence
- [x] Add new hypothesis H{ID}
- [x] Flag strategic changes in ops/today.md

### New Threads Generated
- [ ] **business/{new-thread}:** {Opportunity discovered}
  - Trigger: {What triggered this}
  - Expected impact: {Revenue/strategic value}

- [ ] **business/{new-thread}:** {Follow-up needed}
  - Trigger: {What triggered this}
  - Expected impact: {Value}

### Human Review
- [ ] Quarterly Canvas validation review: {Date}
- [ ] Strategic pivot review (if flagged): {Date}

---

## Related Threads

**Upstream:**
- Input: {Link to 1-input.md}
- Hypothesis: {Link to 2-hypothesis.md}
- Implication: {Link to 3-implication.md}
- Decision: {Link to 4-decision.md}
- Actions: {Links to 5-actions/*.md}

**Downstream:**
- {Related thread 1}: {How they relate}
- {Related thread 2}: {How they relate}

---

## Thread Status

**Status:** completed
**Completed date:** {YYYY-MM-DD}
**Archive date:** {YYYY-MM-DD + 90 days}

**Final Assessment:** {success | partial | failure}
- Success: Met primary metrics, validated key hypotheses
- Partial: Met some metrics, mixed hypothesis validation
- Failure: Missed most metrics, invalidated hypotheses

---

## Appendix: Evidence

**Data sources:**
- {Link to analytics dashboard}
- {Link to customer feedback}
- {Link to financial reports}
- {Link to meeting notes}

**Artifacts:**
- {Link to deliverables}
- {Link to code repositories}
- {Link to documentation}
```

### Example: Enterprise Solution Tier

```markdown
---
thread: enterprise-solution-tier
stage: 6-learning
date: 2025-12-15
owner: ai-agent
canvas_updates: [5-customer-segments, 8-revenue-streams, 13-assumptions]
validation_result: success
---

# Learning: Premium Tier Success

## Results Summary

**Expected:** $850K ARR by month 3 ({Customer} + {Customer-2}), >40% close rate, >60 NPS

**Actual:** $1.1M ARR by month 3 ({Customer} + {Customer-2} + {Customer-3}), 60% close rate, 72 NPS

**Variance:**
- ARR: +29% ($1.1M vs $850K) ✅
- Close rate: +50% (60% vs 40%) ✅
- NPS: +20% (72 vs 60) ✅

**Overall Assessment:** Exceeded expectations across all primary metrics. Validation: success.

---

## Outcome Metrics

### Primary Metrics
| Metric | Target | Actual | Variance | Status |
|--------|--------|--------|----------|--------|
| Enterprise ARR (premium tier) | $850K | $1.1M | +29% | ✅ |
| Premium tier close rate | >40% | 60% (3/5) | +50% | ✅ |
| Premium tier NPS | >60 | 72 | +20% | ✅ |

**Legend:**
- ✅ All primary metrics exceeded targets

### Secondary Metrics
| Metric | Target | Actual | Variance |
|--------|--------|--------|----------|
| Gross margin | >85% | 91% | +7% |
| Support hours/client | <2 hrs/week | 1.5 hrs/week | +25% better |
| Deployment time | <1 hour | 42 min | +30% better |
| Contract negotiation | <30 days | 38 days avg | -27% worse |

**Analysis:**
All metrics met or exceeded except contract negotiation (38 days vs 30 day target).
Legal review took 2 weeks instead of 1 week as estimated. Mitigation: streamline
legal template, reduce custom terms negotiation.

---

## Hypothesis Validation

### Hypothesis A4: "Solution approach preference correlates with segment"
**Original Status:** CHALLENGED (70% → 30% confidence)
**Original Confidence:** 60% (Stage 2)
**Final Status:** ✅ VALIDATED
**Final Confidence:** 95%

**Evidence:**
- 100% of premium segment customers (3/3) chose {solution approach}: {Customer}, {Customer-2}, {Customer-3}
- 100% of standard segment leads (2/2) chose alternative approach: {Lead-1}, {Lead-2}
- Clear segment split confirmed across 5 data points
- NPS for premium tier clients: 72 (high satisfaction)

**Analysis:**
Original assumption "enterprises prefer alternative approach" was wrong. Evidence now
conclusively shows solution preference correlates with customer segment:
- {Premium Segment}: {Solution approach} ({priority} priority)
- {Standard Segment}: Alternative approach (trust signal priority)

Pattern holds across 5 enterprise conversations with 100% consistency.

**Canvas Impact:**
- Update `strategy/canvas/04.segments.md` → Split enterprise segment into:
  - {Premium Segment} (premium tier positioning)
  - {Standard Segment} (standard tier positioning)
- Update `strategy/canvas/10.assumptions.md` → Mark A4 as VALIDATED (95% confidence)

---

### Hypothesis A2: "Enterprise willingness to pay $300K+ per year"
**Original Status:** VALIDATED (60% → 85% confidence in Stage 2)
**Original Confidence:** 85% (Stage 2)
**Final Status:** ✅ VALIDATED
**Final Confidence:** 95%

**Evidence:**
- {Customer}: $400K/year (signed contract)
- {Customer-2}: $450K/year (signed contract)
- {Customer-3}: $500K/year (signed contract)
- Average: $450K/year (50% above original $300K hypothesis)
- 100% of closed deals exceeded $300K threshold

**Analysis:**
Enterprise pricing hypothesis thoroughly validated. All 3 clients paid 33-67%
above minimum threshold. No price resistance at $400K-500K range for premium
segment.

**Canvas Impact:**
- Update `strategy/canvas/12.revenu.md` → Set premium tier pricing at $400K-600K/year
- Update `strategy/canvas/10.assumptions.md` → Mark A2 as VALIDATED (95% confidence)

---

### Hypothesis A9: "Enterprise sales cycle 30-60 days"
**Original Status:** VALIDATED (50% → 70% confidence in Stage 2)
**Original Confidence:** 70% (Stage 2)
**Final Status:** ⚠️ PARTIALLY VALIDATED
**Final Confidence:** 80%

**Evidence:**
- {Customer}: 45 days (first contact → contract signed)
- {Customer-2}: 38 days
- {Customer-3}: 52 days
- Average: 45 days (within 30-60 day range)
- However: Legal review added 7-10 days to each (not anticipated)

**Analysis:**
Sales cycle mostly within predicted range, but legal contract negotiation took
longer than expected (2 weeks vs 1 week). Sales-to-contract was fast (30-40
days), but legal review extended total cycle.

**Canvas Impact:**
- Update `strategy/canvas/10.assumptions.md` → Adjust A9 to "45-60 days" (account for legal)
- Update confidence to 80% (validated with caveat)

---

### Hypothesis H12: "{Premium Segment} values {priority} > social proof"
**Original Status:** NEW (Stage 2)
**Original Confidence:** 65% (Stage 2)
**Final Status:** ✅ VALIDATED
**Final Confidence:** 90%

**Evidence:**
- All 3 premium segment clients cited "{priority}" as primary reason for solution choice
- Post-sales interviews: 100% ranked {priority} in top 2 priorities
- 0% mentioned social proof as factor in decision
- NPS correlation: Higher NPS (72) when we led with {priority} messaging

**Analysis:**
Premium segment decisively prioritizes {priority} over social proof. This is
now a validated customer segmentation insight that should drive GTM strategy
for premium enterprise.

**Canvas Impact:**
- Update `strategy/canvas/15.gtm.md` → Premium segment GTM: Lead with {priority} messaging
- Update `strategy/canvas/10.assumptions.md` → Mark H12 as VALIDATED (90% confidence)

---

## Surprises

### Positive Surprises

**Surprise 1: Support burden lower than expected**
- **Expected:** 2 hours/week per client
- **Actual:** 1.5 hours/week per client (-25%)
- **Impact:** Better gross margin (91% vs 85% target)
- **Root cause:** Comprehensive documentation + client engineering teams are strong
- **Opportunity:** Can scale to 10+ clients without additional support headcount
- **New Thread:** None (just update support cost model)

**Surprise 2: Upsell opportunity - analytics package**
- **Unexpected:** {Customer} requested additional analytics dashboard
- **Impact:** Potential $100K-150K/year upsell per client
- **Opportunity:** Build enterprise analytics tier as separate SKU
- **New Hypothesis:** H15: "Enterprise premium tier clients will pay for analytics upsell"
- **New Thread:** business/analytics-upsell (pursue this opportunity)

**Surprise 3: {Customer-3} closed faster than expected**
- **Expected:** 60% probability, 6-month timeframe
- **Actual:** Closed in month 3 (accelerated by {Customer} reference)
- **Impact:** $500K ARR earlier than planned
- **Root cause:** Social proof within premium segment ({Customer} acted as reference)
- **Learning:** Premium segment customers DO value social proof, but from PEER brands, not co-branding

### Negative Surprises

**Surprise 1: Legal contract negotiation took longer**
- **Expected:** 1 week legal review
- **Actual:** 2 weeks average (7-10 days per contract)
- **Impact:** Extended sales cycle by 7-10 days, delayed revenue recognition
- **Root cause:** Custom terms required more legal scrutiny
- **Mitigation:** Create standardized contract template, reduce custom terms
- **New Risk:** Add "legal review delay" to risk register for future enterprise deals

**Surprise 2: Custom asset requests**
- **Expected:** Simple branding assets
- **Actual:** Each client requested minor customizations (custom fonts, loading animations)
- **Impact:** +1-2 days per client onboarding
- **Root cause:** Premium segment customers have strict brand guidelines
- **Mitigation:** Define "standard tier" vs "premium tier" customization, charge for custom
- **New Hypothesis:** H16: "Premium segment clients will pay for custom features beyond standard tier"

---

## Canvas Updates Required

### 04.segments.md
**Change:** Split "Enterprise" segment into two sub-segments:
**File:** `strategy/canvas/04.segments.md`
1. **{Premium Segment}** ($100M+ {key metric})
   - Characteristics: {Priority} priority, $400K-600K budgets, strong engineering teams
   - Premium tier positioning

2. **{Standard Segment}** ($50M-100M {key metric})
   - Characteristics: Trust signal priority, $300K-400K budgets, social proof important
   - Standard tier positioning

**Rationale:** 100% pattern consistency across 5 enterprise conversations. Premium segment prefers solution approach, standard segment prefers alternative.

**Confidence:** 95%

---

### 12.revenu.md
**Change:** Add validated revenue tier:
**File:** `strategy/canvas/12.revenu.md`

**Premium Enterprise:** $400K-600K/year per client
- Target: Premium segment customers ($100M+ {key metric})
- Includes: Premium solution, isolated deployment, 2 hours/week support
- Gross margin: 91%
- Validated: 3 clients, $1.1M ARR

**Rationale:** All 3 closed deals fell within $400K-500K range. Pricing validated.

**Confidence:** 95%

---

### 10.assumptions.md
**File:** `strategy/canvas/10.assumptions.md`

**Update A4:** "Solution approach preference correlates with segment"
- Status: CHALLENGED → ✅ VALIDATED
- Confidence: 30% → 95%
- Evidence: threads/operations/enterprise-solution-tier/6-learning.md
- Date: 2025-12-15

**Update A2:** "Enterprise willingness to pay $300K+ per year"
- Status: VALIDATED → ✅ VALIDATED (strengthened)
- Confidence: 85% → 95%
- Evidence: threads/operations/enterprise-solution-tier/6-learning.md
- Date: 2025-12-15

**Update A9:** "Enterprise sales cycle 30-60 days"
- Status: VALIDATED → ⚠️ PARTIALLY VALIDATED
- Confidence: 70% → 80%
- Adjustment: 45-60 days (account for legal review)
- Evidence: threads/operations/enterprise-solution-tier/6-learning.md
- Date: 2025-12-15

**Update H12:** "{Premium Segment} values {priority} > social proof"
- Status: NEW → ✅ VALIDATED
- Confidence: 65% → 90%
- Evidence: threads/operations/enterprise-solution-tier/6-learning.md
- Date: 2025-12-15

**Add H15:** "Enterprise premium tier clients will pay for analytics upsell"
- Status: NEW
- Confidence: 50%
- Test: Offer analytics package to {Customer}, {Customer-2}, {Customer-3}
- Expected validation: Q1 2026

**Add H16:** "Premium segment clients will pay for custom features beyond standard tier"
- Status: NEW
- Confidence: 60%
- Test: Create "premium tier" pricing, offer to next 2 clients
- Expected validation: Q2 2026

---

## Prediction Accuracy

**Decision Stage Predictions (from 4-decision.md):**

### 3-Month Predictions
| Prediction | Actual | Accuracy |
|------------|--------|----------|
| {Customer} pilot: $400K ARR | $400K ARR ✅ | 100% |
| {Customer-2}: $450K ARR (70% prob) | $450K ARR ✅ | 100% |
| Total ARR: $850K | $1.1M (incl. {Customer-3}) | 129% |

### 6-Month Predictions
| Prediction | Actual (month 3 data) | Accuracy |
|------------|--------|----------|
| 2 additional deals | 1 additional ({Customer-3}) early | N/A (early) |
| Total ARR: $1.35M | On track (3 closed, 2 warm) | TBD |

### 12-Month Predictions
| Prediction | Status (month 3) | Progress |
|------------|--------|----------|
| 4-5 enterprise clients | 3 closed, 2 warm leads | 60% to target |
| $1.8M-2.4M ARR | $1.1M ARR, on track | 46%-61% to target |

### Overall Prediction Accuracy
**Average accuracy (3-month):** 110% (exceeded predictions)
**Best prediction:** {Customer} ARR (100% accurate)
**Worst prediction:** Close rate timing ({Customer-3} closed earlier than expected)

**Lessons:**
- Revenue predictions were conservative (good problem to have)
- Underestimated social proof value within premium segment ({Customer} reference accelerated {Customer-3})
- Legal review timeline was optimistic (need to add 1 week buffer)

---

## What Worked Well

1. **Segment-specific positioning ({priority} for premium segment)**
   - Why: Resonated deeply with premium segment customers' core values
   - Replicate: Create positioning playbooks by segment for all products

2. **Early reference customer ({Customer})**
   - Why: Premium segment customers trust peer brands more than alternative approaches
   - Replicate: Prioritize reference customers in each segment

3. **Comprehensive documentation**
   - Why: Reduced support burden to 1.5 hours/week (25% better than target)
   - Replicate: Invest in docs upfront for all enterprise features

4. **Isolated namespace architecture**
   - Why: Prevented client-specific issues, enabled faster debugging
   - Replicate: Use isolation pattern for all multi-tenant enterprise features

---

## What Didn't Work

1. **Legal contract timeline estimation**
   - Why: Underestimated scrutiny for custom terms (2 weeks vs 1 week)
   - Fix: Create standardized contract template, add 1 week buffer to sales cycle
   - Impact: Extended sales cycle by 7-10 days, minor revenue recognition delay

2. **Standard tier definition**
   - Why: Didn't anticipate custom feature requests (fonts, animations)
   - Fix: Define "standard" vs "premium" tier features, charge for custom
   - Impact: +1-2 days onboarding per client, manageable but needs pricing tier

---

## Next Actions

### Canvas Updates (Automated)
- [x] Update assumption A4, A2, A9, H12 status and confidence
- [x] Update section 5 (customer segments) - split enterprise by segment
- [x] Update section 8 (revenue streams) - add premium tier
- [x] Update section 13 (assumptions) - all hypothesis validations
- [x] Add new hypotheses H15 (analytics upsell), H16 (custom features)
- [x] Flag strategic win in ops/today.md (exceeded all targets)

### New Threads Generated
- [ ] **business/analytics-upsell:** Enterprise analytics package opportunity
  - Trigger: {Customer} requested analytics dashboard
  - Expected impact: $100K-150K/year per client upsell
  - Priority: High (validate in Q1 2026)

- [ ] **business/premium-tier-customization:** Custom features tier
  - Trigger: All 3 clients requested customization beyond standard
  - Expected impact: $50K-100K/year premium tier pricing
  - Priority: Medium (validate in Q2 2026)

- [ ] **operations/legal-contract-template:** Streamline contracts
  - Trigger: Legal review took 2 weeks vs 1 week target
  - Expected impact: Reduce sales cycle by 7 days
  - Priority: Medium (implement by end of Q4 2025)

### Human Review
- [ ] Quarterly Canvas validation review: 2026-03-01
- [ ] Strategic pivot review: Not flagged (proceeding within strategic bounds)

---

## Related Threads

**Upstream:**
- Input: threads/operations/enterprise-solution-tier/1-input.md (3 premium segment customers requested solution)
- Hypothesis: threads/operations/enterprise-solution-tier/2-hypothesis.md (challenged A4, validated A2)
- Implication: threads/operations/enterprise-solution-tier/3-implication.md ($1.71M ROI)
- Decision: threads/operations/enterprise-solution-tier/4-decision.md (build premium tier)
- Actions: threads/operations/enterprise-solution-tier/5-actions/*.md (all completed)

**Downstream:**
- business/analytics-upsell (new opportunity from {Customer})
- business/premium-tier-customization (custom features tier)
- operations/legal-contract-template (process improvement)

---

## Thread Status

**Status:** completed
**Completed date:** 2025-12-15
**Archive date:** 2026-03-15 (90 days)

**Final Assessment:** Success
- Exceeded all primary metrics (ARR +29%, close rate +50%, NPS +20%)
- Validated 4 key hypotheses (A4, A2, H12) and partially validated A9
- Generated 3 new opportunity threads
- Strategic alignment maintained (enterprise expansion priority)

---

## Appendix: Evidence

**Data sources:**
- Analytics dashboard: [link to Grafana dashboard]
- Customer feedback: NPS surveys from {Customer}, {Customer-2}, {Customer-3}
- Financial reports: ARR tracking spreadsheet
- Meeting notes: Post-sales interviews with 3 clients

**Artifacts:**
- Premium solution: [GitHub repository]
- Deployment automation: [Terraform/Helm charts]
- Documentation: [Onboarding guide, API reference, troubleshooting]
- Contracts: [Signed contracts - confidential]
```

## Validation Result Types

### success
**Definition:** Met or exceeded primary metrics, validated key hypotheses
**Impact:** Strengthens Canvas confidence, generates opportunities

### partial
**Definition:** Met some metrics, mixed hypothesis validation
**Impact:** Update Canvas with caveats, investigate gaps

### failure
**Definition:** Missed most metrics, invalidated hypotheses
**Impact:** Major Canvas revisions, pivot or kill decision

## Hypothesis Validation Status

### ✅ VALIDATED
**Definition:** Evidence strongly supports hypothesis
**Action:** Increase confidence (typically to 85-95%), update Canvas

### ❌ INVALIDATED
**Definition:** Evidence contradicts hypothesis
**Action:** Set confidence to 0%, replace with new hypothesis, update Canvas

### ⚠️ INCONCLUSIVE
**Definition:** Mixed evidence, unclear result
**Action:** Maintain or slightly adjust confidence, gather more data

## Canvas Update Automation

After Stage 6 completes, AI agent automatically:

1. **Parse learning document** for hypothesis validations
2. **Update Canvas sections** with new evidence
3. **Mark assumptions** as validated/invalidated with confidence levels
4. **Add new hypotheses** discovered during execution
5. **Commit changes** with thread reference
6. **Flag in ops/today.md** if major strategic changes
7. **Generate new threads** from opportunities discovered

**Human review required only if:**
- Major strategic pivot (>0.8 impact)
- Contradicts multiple existing assumptions
- Quarterly Canvas validation review
- AI agent flags for review

## Surprise Analysis

### Why Track Surprises?

Surprises reveal:
- **Blind spots:** What we didn't know we didn't know
- **Opportunities:** New revenue streams, market insights
- **Risks:** Hidden challenges, underestimated costs
- **Model accuracy:** Where our predictions failed

### Types of Surprises

**Positive:**
- Better than expected outcomes
- Unexpected opportunities
- Faster than predicted progress
- Lower costs than estimated

**Negative:**
- Worse than expected outcomes
- Hidden challenges
- Delays
- Higher costs

### Learning from Surprises

For each surprise:
1. **Document what happened** (observation)
2. **Explain why** (root cause)
3. **Determine impact** (cost/benefit)
4. **Update model** (adjust future predictions)
5. **Generate action** (new thread or mitigation)

## Validation Rules

### Must Have
- Actual results vs expected outcomes
- Hypothesis validation (at least 1)
- Canvas sections to update
- New threads generated (if opportunities discovered)
- Prediction accuracy analysis

### Must NOT Have
- Results without comparison to predictions
- Hypotheses without validation status
- Learning without Canvas updates
- Surprises without root cause analysis

### Gate Criteria

**Learning is complete when:**
- All hypothesis statuses updated
- Canvas sections identified for update
- Prediction accuracy calculated
- Thread status set to "completed"

**Trigger Canvas updates:**
- AI agent automatically updates Canvas
- Human reviews quarterly or when flagged

## Best Practices

### 1. Compare to Predictions
Always show expected vs actual with variance percentage.

### 2. Validate Every Hypothesis
Don't leave hypotheses from Stage 2 unresolved.

### 3. Find Surprises
If nothing surprised you, you didn't learn anything new.

### 4. Generate New Threads
Opportunities discovered → new threads immediately.

### 5. Update Canvas Automatically
Don't let learning docs gather dust. Update Canvas now.

### 6. Calculate Prediction Accuracy
Track how well you predicted. Improve prediction model over time.

## SLA & Gates

**SLA:** Complete within 7 days of action completion and results observation

**Gate:** Must update ≥1 Canvas section

**Thread Closure:** Learning completion closes thread, archives after 90 days

---

Remember: Learning stage is about **closing the feedback loop**. Every thread must produce validated learning that updates the Canvas. Otherwise, it was activity without progress. The goal is continuous improvement of the business model based on evidence.
