# Marketing Thread Architecture

## Overview

Marketing threads manage campaign execution using the 6-stage causal flow. Traditional campaign stages (research → create → publish → promote → measure) become **typed actions** within Stage 5, similar to sales threads.

## Thread Structure

```
threads/marketing/{campaign-name}/
├── meta.json
├── 1-input.md              # Campaign trigger or opportunity
├── 2-hypothesis.md         # Canvas assumptions tested
├── 3-implication.md        # Campaign ROI analysis
├── 4-decision.md           # LAUNCH, TEST, or HOLD
├── 5-actions/
│   ├── research.md         # Type: marketing:research
│   ├── create-content.md   # Type: marketing:create
│   ├── publish.md          # Type: marketing:publish
│   ├── promote.md          # Type: marketing:promote
│   └── measure.md          # Type: marketing:measure
├── 6-learning.md           # Canvas updates
```

## Marketing Action Types

### Action Type Catalog

| Type | Purpose | Human Required | Duration | Skill |
|------|---------|----------------|----------|-------|
| `marketing:research` | Audience research, competitive analysis | No | 2-3 days | `marketing-content-strategy` |
| `marketing:create` | Content creation (copy, design, video) | Yes (approval) | 5-7 days | `content-generation` |
| `marketing:publish` | Publish to channels (LinkedIn, website, email) | No | 1 day | Human workflow |
| `marketing:promote` | Paid promotion, outreach, distribution | Yes (budget) | 14-30 days | Human workflow |
| `marketing:measure` | Track metrics, analyze performance | No | 7 days | `goal-tracker` |

### Action Metadata Format

```json
{
  "action_id": "create-{premium tier}-announcement",
  "type": "marketing:create",
  "status": "completed",
  "skill": "content-generation",
  "human_required": true,
  "assigned_to": "human",
  "created": "2025-12-01",
  "due": "2025-12-08",
  "completed": "2025-12-07",
  "deliverables": ["LinkedIn post", "Blog article", "Email campaign"],
  "quality_score": 4.5
}
```

## Thread Metadata

```json
{
  "thread_id": "{premium tier}-launch-announcement",
  "type": "marketing",
  "status": "active",
  "owner": "ai-agent",
  "created": "2025-12-01",
  "updated": "2026-01-15",
  "stage": 5,
  "current_action": "marketing:promote",
  "impact_score": 0.65,
  "canvas_assumptions": ["A10", "A15"],
  "related_threads": ["business/enterprise-{premium tier}"],
  "budget": 5000,
  "target_reach": 50000,
  "target_conversions": 15
}
```

**Marketing-specific fields:**
- `current_action`: Current campaign stage (action type)
- `budget`: Campaign budget (dollars)
- `target_reach`: Expected audience reach
- `target_conversions`: Expected conversions (leads, demos, etc.)

## AI Agent Marketing Logic

### Stage 4: Decision

**If verdict = LAUNCH:**
```python
create_action(type="marketing:research", auto_execute=True)
create_action(type="marketing:create", human_required=True)
# Future actions created as previous complete
```

**If verdict = TEST:**
```python
create_action(type="marketing:research", auto_execute=True)
create_action(type="marketing:create", human_required=True)
# Smaller budget, shorter timeframe
```

**If verdict = HOLD:**
```python
skip_to_results(reason="timing_not_right")
set_reminder(days=30, reason="revisit_campaign")
```

### Stage 5: Actions

**Research complete:**
```python
if action.type == "marketing:research":
    insights = extract_insights(action.deliverables)
    create_action("marketing:create", context=insights)
```

**Content created:**
```python
if action.type == "marketing:create":
    if action.result == "approved":
        create_action("marketing:publish")
    elif action.result == "needs_revision":
        reopen_action("marketing:create")
```

**Content published:**
```python
if action.type == "marketing:publish":
    create_action("marketing:promote", budget=thread.budget)
```

**Promotion complete:**
```python
if action.type == "marketing:promote":
    create_action("marketing:measure")
```

**Measurement complete:**
```python
if action.type == "marketing:measure":
    proceed_to_results(metrics=action.data)
```

## Example: Marketing Thread Execution

### Input Data
```
{premium tier} tier launched. Need to announce to market.
Target: Enterprise {premium segment} brands
Goal: 15 demo requests in 30 days
```

### Stage 1: Input
```markdown
# Input

**Date:** 2025-12-01

## Observation
{premium tier} enterprise tier launched successfully (see threads/operations/enterprise-{premium tier}/)

## Campaign Trigger
- **Event:** Product launch ({new feature/tier})
- **Target audience:** {target segment}
- **Goal:** Generate 15 qualified demo requests in 30 days
- **Budget:** $5K

## Market Context
- Enterprise pipeline: $4.5M (4 weeks post-launch)
- First customer: {Customer} ($1.1M ARR)
- Competitive landscape: First-mover advantage ({your positioning})

## Strategic Alignment
- 07.uvp.md: "Brand-first {industry} AI"
- 14.growth.md: Enterprise expansion priority
- 15.gtm.md: LinkedIn + direct outreach

## Next Steps
Proceed to hypothesis validation (Stage 2)
```

### Stage 2: Hypothesis
```markdown
# Hypothesis

**Date:** 2025-12-03

## Canvas Assumptions Tested

### A10: Marketing Channel Effectiveness
**Status:** ⚠️ CHALLENGED
**Current assumption:** Blog + email = primary enterprise channels
**Counter-evidence:** {Customer} came from LinkedIn (inbound)
**New hypothesis:** LinkedIn > Blog > Email for enterprise {premium segment} brands
**Confidence:** 75%
**Test method:** Track lead source attribution for next 15 demos

### A15: Messaging Hierarchy
**Status:** 🆕 NEW HYPOTHESIS
**Hypothesis:** {Target segment} cares about {primary value prop} > {secondary value prop}
**Rationale:** {Customer} chose {option A} despite {trade-off} vs {option B}
**Confidence:** 70%
**Test method:** A/B test messaging (brand control vs cost efficiency)

### A12: Demo Request Conversion Rate
**Status:** ✅ VALIDATED (historical)
**Current assumption:** 3% website visitors → demo requests
**Historical data:** 2.8% average (last 6 months)
**Confidence:** 90%

## Canvas Impact
- **13.metrics.md:** Update channel mix (LinkedIn focus)
- **15.gtm.md:** Prioritize LinkedIn over blog
- **07.uvp.md:** Lead with brand control messaging

## Next Steps
Proceed to implication analysis (Stage 3)
```

### Stage 3: Implication
```markdown
# Implication

**Date:** 2025-12-05

## Campaign Opportunity

### Target Metrics
- **Reach:** 50,000 enterprise decision makers (CTOs, CPOs)
- **Engagement:** 1,500 clicks (3% CTR)
- **Demo requests:** 15 (1% click-to-demo conversion)
- **Qualified opportunities:** 9 (60% qualification rate)
- **Deals closed:** 5 (60% close rate, 90-day cycle)

### Revenue Impact
- **Pipeline:** $5M (9 qualified × $550K average deal)
- **Expected revenue:** $3M (5 deals closed)
- **LTV:** $6M (2-year contracts)

### Timeline
- Week 1: Research + content creation
- Week 2: Publish + initial promotion
- Week 3-4: Paid promotion + outreach
- Week 5: Measure + optimize

## Cost Analysis

### Content Creation
- **LinkedIn posts:** 5 posts × $200 = $1K
- **Blog article:** 1 long-form × $800 = $800
- **Email campaign:** 3 emails × $150 = $450
- **Total:** $2.25K

### Distribution
- **LinkedIn ads:** $2K (30 days, $65/day)
- **Outreach tools:** $250 (Apollo.io, LinkedIn Sales Nav)
- **Total:** $2.25K

### Total Budget
- **Content + Distribution:** $4.5K
- **Buffer:** $500
- **Total:** $5K

## ROI Analysis

### Campaign ROI
- **Cost:** $5K
- **Expected revenue:** $3M (Year 1)
- **ROI:** 600x

### CAC Analysis
- **Cost per demo:** $333 ($5K / 15 demos)
- **Cost per qualified opp:** $555 ($5K / 9 qualified)
- **CAC:** $1K ($5K / 5 customers)
- **LTV:CAC ratio:** 6,000:1 (exceptional)

## Risk Assessment

### Creative Risk: MEDIUM
- Messaging hypothesis untested (brand control > cost)
- Mitigation: A/B test two message variants
- Fallback: Pivot messaging based on engagement

### Channel Risk: LOW
- LinkedIn proven ({Customer} inbound)
- Historical performance: 3% CTR
- Mitigation: Diversify to blog + email

### Budget Risk: LOW
- $5K well within marketing budget
- Can pause/adjust mid-campaign
- Low burn rate ($65/day)

### Execution Risk: LOW
- Content creation: 7 days (proven velocity)
- Promotion: Automated (LinkedIn ads)
- Measurement: Automated (analytics tracking)

### Overall Risk: LOW-MEDIUM

## Impact Score
**0.65** (medium-high impact)

**Factors:**
- Revenue impact: $3M expected (high)
- Strategic: Validates enterprise GTM (high)
- Risk: Low-medium
- Cost: $5K (low)
- Reversibility: High (can pause campaign)

## Alternatives Considered

### 1. Wait for organic growth
- **Pros:** $0 cost
- **Cons:** Slow (3-6 months to 15 demos)
- **Decision:** REJECTED (opportunity cost too high)

### 2. Partner with agency
- **Pros:** Professional execution
- **Cons:** $20K cost, 4-week delay
- **Decision:** REJECTED (cost 4x budget, slower)

### 3. Conference sponsorship
- **Pros:** Direct access to decision makers
- **Cons:** $15K+ cost, 3-month lead time
- **Decision:** REJECTED (budget + timing)

### 4. LinkedIn + blog (chosen approach)
- **Pros:** Proven channel, fast execution, low cost
- **Cons:** Requires content creation
- **Decision:** SELECTED

## Recommendation
**LAUNCH** campaign

**Rationale:**
1. High ROI (600x)
2. Low risk ($5K, reversible)
3. Fast execution (5 weeks)
4. Tests strategic hypothesis (A10, A15)
5. Proven channel (LinkedIn)

## Next Steps
Proceed to decision (Stage 4)
```

### Stage 4: Decision
```markdown
# Decision

**Date:** 2025-12-08

## Verdict
**LAUNCH** {feature/product} announcement campaign

## Rationale

### Strategic Alignment
- **07.uvp.md:** "Brand-first {industry} AI" → lead with brand control
- **14.growth.md:** Enterprise expansion = priority
- **15.gtm.md:** LinkedIn + content = validated channels

### Financial Justification
- **ROI:** 600x ($5K → $3M expected)
- **CAC:** $1K per customer (LTV:CAC = 6,000:1)
- **Risk-adjusted NPV:** $2M+ over 2 years

### Hypothesis Validation
- **A10 (Channel effectiveness):** Test LinkedIn > Blog > Email
- **A15 (Messaging):** Test brand control > cost savings
- **Success criteria:** 15 demos, 3% CTR, 1% conversion

### Market Timing
- **First-mover advantage:** 6-month window before competitors
- **Hot pipeline:** $4.5M already (momentum building)
- **Proof point:** {Customer} case study (credibility)

## Alternatives Rejected

| Alternative | Why Rejected |
|-------------|--------------|
| Wait for organic | Too slow (3-6 months), opportunity cost high |
| Agency partner | 4x cost, slower execution |
| Conference | 3x cost, 3-month delay |

## Success Metrics

### Reach
- **Target:** 50,000 impressions
- **Baseline:** 0 (new campaign)

### Engagement
- **CTR:** >3% (LinkedIn ads)
- **Clicks:** >1,500
- **Baseline:** Historical 2.8%

### Conversion
- **Demo requests:** >15
- **Qualified:** >9 (60% rate)
- **Click-to-demo:** >1%

### Revenue
- **Pipeline:** >$5M
- **Closed deals:** >5 (90-day cycle)
- **Expected ARR:** >$3M

## Decision Authority
**Approved by:** AI Agent (autonomous)
**Impact score:** 0.65 (medium-high, within bounds)
**Rationale for autonomy:**
- ROI > 3x (600x actual) ✓
- Cost < $100K ($5K actual) ✓
- Timeline < 3 months (5 weeks) ✓
- Risk: Low-medium ✓
- Strategic alignment: High ✓

**Human review:** Not required (no flags triggered)
**Budget approval:** Required for promotion spend ($2.25K)

## Implementation Plan

### Week 1: Research + Create (Dec 8-15)
- Research: Target audience, competitive positioning
- Content: 5 LinkedIn posts, 1 blog, 3 emails
- Assets: Case study ({Customer}), demo video

### Week 2: Publish (Dec 16-22)
- LinkedIn posts: 5 posts (Mon/Wed/Fri)
- Blog article: Product launch announcement
- Email: Announcement to 5,000 subscribers

### Week 3-4: Promote (Dec 23 - Jan 5)
- LinkedIn ads: $65/day targeting (CTOs, CPOs, {premium segment} brands)
- Outreach: Direct messages to 200 warm leads
- Retargeting: Website visitors

### Week 5: Measure (Jan 6-12)
- Analytics: Reach, CTR, conversions
- Attribution: Lead source tracking
- Results: Document in Stage 6

## Next Steps
Proceed to actions (Stage 5)
```

### Stage 5-7: Complete Campaign Execution
(Actions, Results, Learning sections follow similar detailed format as business/sales threads)

## Output Templates

### Thread Status Report
```markdown
## Thread: marketing/{campaign-name}

**Status:** Stage {n} of 7
**Budget:** ${amount}
**Target reach:** {impressions}
**Target conversions:** {demos}
**Current stage:** {action-type}

### Progress
- [✓] Stage 1: Input
- [✓] Stage 2: Hypothesis (testing A10, A15)
- [✓] Stage 3: Implication (ROI: 600x)
- [✓] Stage 4: Decision (LAUNCH)
- [→] Stage 5: Actions (content creation in progress)
- [ ] Stage 6: Results
- [ ] Stage 7: Learning

### Campaign Performance (Live)
- Reach: {current} / {target}
- CTR: {percent}%
- Conversions: {count} / {target}

### Next Steps
1. Complete content creation
2. Publish to LinkedIn
3. Launch paid promotion
```

### Canvas Update Report
```markdown
## Canvas Updates: marketing/{campaign-name}

**Date:** {date}
**Campaign outcome:** SUCCESS | PARTIAL | FAILURE
**ROI:** {multiplier}x

### Assumptions Updated
- **A10:** Channel Effectiveness → ✅ VALIDATED (LinkedIn > Blog)
- **A15:** Messaging Hierarchy → ✅ VALIDATED (Brand control > Cost)

### Sections Modified
- strategy/canvas/13.metrics.md
- strategy/canvas/15.gtm.md

### New Hypotheses
- H16: Video content performs 2x better than text

### Strategic Flags
None - campaign within performance bounds
```

## Human Touch Points

### Content Approval (Create)
- **Duration:** 30 min review
- **Attendees:** Founder (or designated approver)
- **AI prep:** Draft content, design mockups
- **Human tasks:** Review copy, approve messaging, check brand
- **AI follow-up:** Finalize content, schedule publishing

### Budget Approval (Promote)
- **Duration:** 15 min review
- **Attendees:** Founder (or designated approver)
- **AI prep:** Budget breakdown, ROI projection
- **Human tasks:** Approve spend, set limits
- **AI follow-up:** Launch ads, track spend

### Performance Review (Measure)
- **Duration:** 30 min review
- **Attendees:** Founder (or designated approver)
- **AI prep:** Analytics dashboard, insights report
- **Human tasks:** Interpret results, decide next steps
- **AI follow-up:** Update Canvas, create learning doc

## AI Automation Points

### Research
- ✅ Competitive analysis (scrape competitor content)
- ✅ Audience research (LinkedIn demographics)
- ✅ Trend analysis (Google Trends, social listening)
- ✅ Keyword research (SEO tools)

### Create
- ✅ Draft copy (GPT-4 + brand guidelines)
- ✅ Generate visuals (Midjourney, Canva templates)
- ✅ Create video (AI video tools)
- ⚠️ Human approval required (brand quality)

### Publish
- ✅ Schedule posts (Buffer, Hootsuite)
- ✅ Email automation (Mailchimp)
- ✅ Website updates (CMS integration)

### Promote
- ✅ LinkedIn ads setup (automated bidding)
- ✅ Retargeting pixels (automated tracking)
- ✅ Budget monitoring (auto-pause if overspend)
- ⚠️ Human approval required (budget release)

### Measure
- ✅ Analytics tracking (Google Analytics, LinkedIn)
- ✅ Attribution tracking (UTM codes)
- ✅ Performance dashboards (auto-generated)
- ✅ Insights extraction (anomaly detection)

## Campaign Types

### 1. Product Launch
- Goal: Awareness + demos
- Duration: 4-6 weeks
- Budget: $5K-$15K
- Actions: Research, Create (5-10 assets), Publish (multi-channel), Promote (ads), Measure

### 2. Thought Leadership
- Goal: Brand credibility
- Duration: 8-12 weeks
- Budget: $2K-$5K
- Actions: Research (trends), Create (3-5 articles), Publish (LinkedIn + blog), Promote (organic), Measure

### 3. Customer Story
- Goal: Social proof
- Duration: 3-4 weeks
- Budget: $3K-$8K
- Actions: Research (customer interview), Create (case study), Publish (website + LinkedIn), Promote (ads + PR), Measure

### 4. Event Promotion
- Goal: Registrations
- Duration: 6-8 weeks
- Budget: $5K-$20K
- Actions: Research (audience), Create (landing page + emails), Publish (multi-channel), Promote (ads + partnerships), Measure

## Key Metrics by Action Type

### Research
- Time: 2-3 days
- Quality: Actionable insights (3-5 key findings)
- Cost: $0 (AI-automated)

### Create
- Time: 5-7 days (human approval bottleneck)
- Quality: 4+ stars (internal review)
- Cost: $1K-$3K (design + copy)

### Publish
- Time: 1 day
- Reach: Baseline audience (email list, followers)
- Cost: $0 (automated)

### Promote
- Time: 14-30 days
- Reach: 10x baseline (paid amplification)
- Cost: $2K-$10K (ads)

### Measure
- Time: 7 days (performance stabilization)
- Insights: 3-5 actionable findings
- Cost: $0 (automated analytics)