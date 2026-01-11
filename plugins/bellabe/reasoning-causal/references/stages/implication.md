
# Stage 3: Implication (Analyze Impact)

You are an expert at business impact analysis and cost-benefit evaluation. Your role is to quantify what hypothesis changes mean for the business before any decisions are made.

## Purpose

Transform hypothesis changes into actionable business intelligence by:
- Quantifying revenue opportunities
- Calculating full costs (development, operations, opportunity cost)
- Analyzing risks and mitigation strategies
- Mapping to service architecture
- Providing clear recommendation with ROI

## Core Principle

**Quantify everything. No vague analysis. Numbers drive decisions.**

## When to Use

- After Stage 2 (Hypothesis) completes
- Re-evaluating impact with changed conditions
- Updating cost/benefit analysis with new data
- Comparing alternative approaches

## Implication Document Structure

Create: `threads/operations/{thread-name}/3-implication.md`

### Template

```markdown
---
thread: {thread-name}
stage: 3-implication
impact: low | medium | high | critical
date: {YYYY-MM-DD}
owner: ai-agent
---

# Implication: {Title}

## Business Impact Summary

**Revenue Opportunity:** ${amount} over {timeframe}
**Cost:** ${amount}
**ROI:** ${revenue - cost} ({percentage}% margin)
**Timeline:** {weeks/months}
**Risk Level:** low | medium | high

---

## Revenue Opportunity

### Immediate (0-3 months)
- ${amount}: {Source/deal}
- ${amount}: {Source/deal}
**Total:** ${amount}

### Short-term (3-12 months)
- ${amount}: {Projected source}
- Assumptions: {What must be true}
**Total:** ${amount}

### Long-term (12+ months)
- ${amount}: {Projected source}
- Assumptions: {What must be true}
**Total:** ${amount}

### Downside Risk
**If we don't act:** ${lost opportunity}
**If we act and fail:** ${sunk cost}

---

## Cost Structure

### Development Costs
- Engineering: ${amount} ({X weeks @ $Y/week loaded cost})
- Design: ${amount}
- Product: ${amount}
**Total development:** ${amount}

### One-Time Costs
- Legal: ${amount} ({reason})
- Marketing: ${amount} ({reason})
- Infrastructure: ${amount} ({reason})
**Total one-time:** ${amount}

### Ongoing Costs
- Support: ${amount/year per customer}
- Infrastructure: ${amount/month}
- Maintenance: ${amount/month}
**Total ongoing:** ${amount/year}

### Opportunity Cost
**What we won't build:** {Feature/project delayed}
**Revenue impact:** ${amount lost/delayed}

**Total Cost:** ${dev + one-time + ongoing (12mo) + opportunity}

---

## ROI Analysis

**Total Revenue (12mo):** ${amount}
**Total Cost (12mo):** ${amount}
**Net Profit (12mo):** ${revenue - cost}
**ROI:** {percentage}%
**Payback Period:** {months}

**Break-even:** {When do we recover costs?}

### Sensitivity Analysis
- **Best case** (80th percentile): ${amount} profit
- **Expected case** (50th percentile): ${amount} profit
- **Worst case** (20th percentile): ${amount} profit

---

## Product Impact

### Required Changes
1. **{Component/service}:** {What needs to be built/changed}
   - Effort: {weeks}
   - Complexity: low | medium | high
   - Dependencies: {What it depends on}

2. **{Component/service}:** {What needs to be built/changed}
   - Effort: {weeks}
   - Complexity: low | medium | high
   - Dependencies: {What it depends on}

**Total effort:** {weeks} engineering

### Technical Risks
- **{Risk 1}:** {Description}
  - Impact: low | medium | high
  - Mitigation: {Strategy}

- **{Risk 2}:** {Description}
  - Impact: low | medium | high
  - Mitigation: {Strategy}

### Service Mapping
**Affected services:**
- `{service-name}`: {Impact level} - {What changes}
- `{service-name}`: {Impact level} - {What changes}

---

## GTM Impact

### Marketing
- **Collateral needed:** {What materials}
- **Messaging changes:** {What positioning updates}
- **Cost:** ${amount}
- **Timeline:** {weeks}

### Sales
- **Playbook updates:** {What changes to sales process}
- **Training required:** {What team needs to learn}
- **Deal structure:** {Contract/pricing changes}
- **Timeline:** {weeks}

### Customer Success
- **Onboarding changes:** {What's different}
- **Support burden:** {Expected increase}
- **Documentation:** {What needs to be created}

---

## Risk Analysis

### If We Build

**Pros:**
- ✅ {Benefit 1}
- ✅ {Benefit 2}
- ✅ {Benefit 3}

**Cons:**
- ⚠️ {Risk 1}
- ⚠️ {Risk 2}
- ⚠️ {Risk 3}

**Mitigation:**
- {Risk 1} → {Mitigation strategy}
- {Risk 2} → {Mitigation strategy}

### If We Don't Build

**Pros:**
- ✅ {Benefit 1: e.g., Keep product simple}
- ✅ {Benefit 2: e.g., Focus resources elsewhere}

**Cons:**
- ❌ {Cost 1: e.g., Lose revenue}
- ❌ {Cost 2: e.g., Market perception}
- ❌ {Cost 3: e.g., Competitive disadvantage}

---

## Dependencies

**Blocking dependencies:**
- [ ] {Dependency 1: e.g., Legal approval}
- [ ] {Dependency 2: e.g., Engineering capacity}
- [ ] {Dependency 3: e.g., Partner agreement}

**Timeline impact:** {How dependencies affect schedule}

**Mitigation:** {How to unblock or work around}

---

## Strategic Alignment

**Company Strategy:** {How this aligns or conflicts}
**Current Priorities:** {How this ranks against other initiatives}
**Resource Impact:** {What gets delayed or paused}

**Alignment Score:** {0.0-1.0}
- 0.0-0.3: Misaligned, conflicts with strategy
- 0.4-0.6: Neutral, neither helps nor hurts
- 0.7-0.9: Aligned, supports strategy
- 1.0: Critical, essential to strategy

---

## Recommendation

**Decision:** BUILD | DON'T BUILD | WAIT | ALTERNATIVE

**Rationale:**
{2-3 sentence summary of why this is the recommendation}

**Conditions:**
- {Condition 1 that must be true}
- {Condition 2 that must be true}

**Next Steps:**
1. {Action 1}
2. {Action 2}
3. {Action 3}

---

## Next Stage Trigger
{Should we proceed to decision stage?}

Proceed to Stage 4: Decision
```

### Example: Enterprise {Premium Tier}

```markdown
---
thread: enterprise-{premium-tier}
stage: 3-implication
impact: high
date: 2025-11-05
owner: ai-agent
---

# Implication: {Premium Tier} Required

## Business Impact Summary

**Revenue Opportunity:** $1.8M over 12 months
**Cost:** $90K total (dev + legal + ongoing)
**ROI:** $1.71M (95% margin)
**Timeline:** 3 weeks development
**Risk Level:** Medium (manageable complexity, proven demand)

---

## Revenue Opportunity

### Immediate (0-3 months)
- $400K: {Customer A} pilot (signed LOI, Q1 2026 start)
- $450K: {Customer B} (warm lead, 70% close probability)
**Total:** $850K (weighted: $715K)

### Short-term (3-12 months)
- $500K: {Customer C} (warm lead, 60% close probability)
- $600K: 2 additional {premium segment} leads from pipeline (40% close probability)
- Assumptions: 40% close rate on {premium segment}, 45-day sales cycle
**Total:** $1.1M (weighted: $540K)

### Long-term (12+ months)
- $2.4M: 4 additional {premium segment} customers @ $600K/year
- Assumptions: {Premium tier} becomes standard enterprise offering
**Total:** $2.4M (weighted: $1.2M)

### Downside Risk
**If we don't act:**
- Lose {Customer A} deal: $400K
- Lose {Customer B}, {Customer C}: $950K
- Signal "not enterprise-ready" to market
- **Total opportunity cost:** $1.35M

**If we act and fail:**
- Sunk development cost: $45K
- Sunk legal cost: $5K
- **Total sunk cost:** $50K

**Risk-adjusted decision:** $1.35M downside >> $50K downside → BUILD

---

## Cost Structure

### Development Costs
- Engineering: $40K (3 weeks @ $13.3K/week loaded, 2 engineers)
  - SDK generation service (no branding)
  - {premium tier} deployment pipeline
  - Analytics/reporting for {premium tier} clients
- Design: $0 (no UI changes)
- Product: $3K (0.5 weeks PM @ $6K/week loaded)
**Total development:** $43K

### One-Time Costs
- Legal: $5K (contract modifications, {premium tier} terms)
- Marketing: $8K (enterprise collateral, case study template)
- Infrastructure: $2K (deployment automation setup)
**Total one-time:** $15K

### Ongoing Costs
- Support: $5K/year per client (estimated 2 hours/week @ $50/hour)
- Infrastructure: $500/month per client (isolated namespace, monitoring)
- Maintenance: $2K/month (feature updates, security patches)
**Total ongoing:** $32K/year (assuming 4 clients)

### Opportunity Cost
**What we won't build:** Analytics v2 dashboard (delayed 3 weeks)
**Revenue impact:** $0 (no current deals dependent on analytics v2)

**Total Cost (12mo):** $43K + $15K + $32K = $90K

---

## ROI Analysis

**Total Revenue (12mo):** $1.8M (immediate + short-term)
**Total Cost (12mo):** $90K
**Net Profit (12mo):** $1.71M
**ROI:** 1900%
**Payback Period:** 1 deal ({Customer A} = 4.4x cost)

**Break-even:** First customer ({Customer A}) pays $400K vs $90K cost

### Sensitivity Analysis
- **Best case** (3 deals in 12mo): $1.35M revenue - $90K cost = $1.26M profit
- **Expected case** (2 deals in 12mo): $850K revenue - $90K cost = $760K profit
- **Worst case** (1 deal in 12mo): $400K revenue - $90K cost = $310K profit

**All scenarios profitable.** Risk is low.

---

## Product Impact

### Required Changes
1. **SDK Generation Service:** Add {premium tier} flag to build pipeline
   - Effort: 1.5 weeks
   - Complexity: Medium (extend existing system)
   - Dependencies: None

2. **Brand Configuration System:** Template system for client branding injection
   - Effort: 1 week
   - Complexity: Low (configuration layer)
   - Dependencies: SDK generation service

3. **Deployment Automation:** Client-specific namespace deployment
   - Effort: 0.5 weeks
   - Complexity: Low (infrastructure as code)
   - Dependencies: Brand configuration

**Total effort:** 3 weeks engineering

### Technical Risks
- **Client custom branding requests:** May require more customization than planned
  - Impact: Medium (could add 1-2 weeks per client)
  - Mitigation: Set clear branding guidelines upfront, charge for custom work

- **Support complexity:** Harder to debug client-specific deployments
  - Impact: Low (isolated namespaces simplify debugging)
  - Mitigation: Comprehensive logging, monitoring per client

### Service Mapping
**Affected services:**
- `{service-1}`: Medium impact - Add SDK generation endpoint
- `{service-2}`: Low impact - {Premium tier} reporting views
- `infrastructure`: Low impact - Client namespace deployment

---

## GTM Impact

### Marketing
- **Collateral needed:** Enterprise {premium tier} one-pager, case study template
- **Messaging changes:** Add "brand control" positioning for {premium segment}
- **Cost:** $8K (freelance writer + designer)
- **Timeline:** 1 week

### Sales
- **Playbook updates:** Split enterprise pitch by segment ({premium segment} vs {budget segment})
- **Training required:** How to position brand control vs social proof
- **Deal structure:** {Premium tier} pricing ($400K-600K/year)
- **Timeline:** 2 days (playbook update + team training)

### Customer Success
- **Onboarding changes:** Client branding asset collection process
- **Support burden:** +2 hours/week per client (estimated)
- **Documentation:** {Premium tier} deployment guide, troubleshooting docs
- **Timeline:** 1 week (parallel with development)

---

## Risk Analysis

### If We Build

**Pros:**
- ✅ Unlock $1M+ revenue segment ({premium segment} enterprise)
- ✅ Validate segment-specific product market fit
- ✅ Differentiate from competitors (most don't offer {premium tier})
- ✅ Create premium tier justifying $400K-600K pricing

**Cons:**
- ⚠️ Increase product complexity ({premium tier} + co-branded paths)
- ⚠️ Support burden grows with client-specific deployments
- ⚠️ Custom requests may creep beyond initial scope

**Mitigation:**
- Complexity → Set strict boundaries on customization
- Support → Charge $5K/year per client for support (already in pricing)
- Scope creep → Define {premium tier} precisely in contracts

### If We Don't Build

**Pros:**
- ✅ Keep product simple (single deployment model)
- ✅ Focus engineering resources on self-serve scale
- ✅ Avoid support overhead of custom deployments

**Cons:**
- ❌ Lose {Customer A} ($400K), {Customer B} ($450K), {Customer C} ($500K) = $1.35M
- ❌ Signal to market we're not enterprise-ready for {premium segment}
- ❌ Competitors may capture {premium segment} first
- ❌ Miss validation of $400K-600K pricing hypothesis

**Net:** Downside of not building significantly outweighs complexity concerns

---

## Dependencies

**Blocking dependencies:**
- [x] Legal approval for contract modifications (checked with legal, 1 week turnaround)
- [x] Engineering capacity available (2 engineers free for 3 weeks)
- [ ] {Customer A} contract signed (LOI signed, full contract by end of month)

**Timeline impact:** No blockers. Can start immediately.

**Mitigation:** Proceed with development in parallel with contract finalization.
Risk is low (LOI signed, $50K sunk cost acceptable).

---

## Strategic Alignment

**Company Strategy:** Expand enterprise segment, validate premium pricing
**Current Priorities:** Enterprise growth is top priority for 2025
**Resource Impact:** Delays analytics v2 by 3 weeks (no deal dependency)

**Alignment Score:** 0.9 (highly aligned)
- Directly supports enterprise expansion strategy
- Validates premium pricing hypothesis (A2)
- Enables {premium segment} segment capture (new market)

---

## Recommendation

**Decision:** BUILD

**Rationale:**
ROI is exceptional (1900%), risk is manageable, and strategic alignment is high.
All scenarios (best, expected, worst case) are profitable. Not building would cost
$1.35M in lost opportunity vs $90K investment. {Premium tier} capability unlocks
entire {premium segment}.

**Conditions:**
- Engineering capacity remains available (2 engineers × 3 weeks)
- {Customer Name} contract finalizes by end of month (de-risk with LOI)
- Legal approves contract modifications within 1 week

**Next Steps:**
1. Proceed to Stage 4: Decision (document official commitment)
2. Plan engineering sprint (3 weeks)
3. Finalize legal contracts
4. Create GTM collateral (parallel track)

---

## Next Stage Trigger
High ROI ($1.71M profit), clear strategic alignment (0.9), manageable risk.
Proceed to Stage 4: Decision for official commitment.
```

## Impact Classification

### Low Impact
- Revenue: <$100K
- Cost: <$10K
- Timeline: <1 week
- Risk: Reversible

### Medium Impact
- Revenue: $100K-$500K
- Cost: $10K-$50K
- Timeline: 1-4 weeks
- Risk: Some sunk cost

### High Impact
- Revenue: $500K-$2M
- Cost: $50K-$200K
- Timeline: 1-3 months
- Risk: Significant commitment

### Critical Impact
- Revenue: >$2M
- Cost: >$200K
- Timeline: >3 months
- Risk: Strategic pivot

## ROI Thresholds

### Strong ROI
- ROI: >500%
- Payback: <3 months
- Confidence: High

**Action:** Proceed to decision

### Good ROI
- ROI: 200-500%
- Payback: 3-6 months
- Confidence: Medium-High

**Action:** Proceed with conditions

### Moderate ROI
- ROI: 100-200%
- Payback: 6-12 months
- Confidence: Medium

**Action:** Consider alternatives

### Weak ROI
- ROI: <100%
- Payback: >12 months
- Confidence: Low

**Action:** Don't build or wait for more data

## Validation Rules

### Must Have
- Revenue quantified ($ amounts)
- Costs quantified (dev + one-time + ongoing)
- ROI calculated
- Timeline estimated
- Risk analysis with mitigation
- Clear recommendation

### Must NOT Have
- Vague estimates ("several thousand", "a few weeks")
- Missing cost categories
- Unbounded scope ("and more...")
- Decision or commitment (save for Stage 4)

### Gate Criteria

**Proceed to Stage 4 if:**
- All costs and revenue quantified
- ROI calculated
- Risk level acceptable
- Recommendation clear

**Return to Stage 2 if:**
- Hypothesis unclear
- Missing critical information
- Need more evidence

## Best Practices

### 1. Show Your Math
Don't just state "$1.8M revenue"
Show: "$400K + $450K + $500K + (2 × $300K) = $1.8M"

### 2. Include Worst Case
Optimism bias is real. Force yourself to model pessimistic scenario.

### 3. Account for Opportunity Cost
What are you NOT building? What revenue is delayed?

### 4. Map to Services
Link business impact to technical architecture.

### 5. Set Conditions
"Build IF X, Y, Z are true"

## SLA & Gates

**SLA:** Complete within 3 days of Stage 2 (Hypothesis)

**Gate:** Must be reviewed before Stage 4 (Decision) can proceed

**Next Stage Trigger:** Implication acceptance triggers Stage 4 (Decision)

---

Remember: Implication stage is about **quantifying impact**. Every statement must have a number. Revenue, cost, timeline, probability - quantify everything. Vague analysis leads to bad decisions.
