# Sales Thread Architecture

## Overview

Sales threads manage individual deal pipelines using the 6-stage causal flow. Traditional sales stages (lead → qualification → demo → pilot → close) become **typed actions** within Stage 5.

## Thread Structure

```
threads/sales/{deal-name}/
├── meta.json
├── 1-input.md              # Lead inquiry
├── 2-hypothesis.md         # Canvas assumptions tested
├── 3-implication.md        # Deal ROI analysis
├── 4-decision.md           # PURSUE or PASS
├── 5-actions/
│   ├── lead-intake.md      # Type: sales:lead-intake
│   ├── qualify.md          # Type: sales:qualification
│   ├── demo.md             # Type: sales:demo
│   ├── pilot.md            # Type: sales:pilot
│   └── close.md            # Type: sales:close
└── 6-learning.md           # Canvas updates
```

## Segment Binding

Every sales thread is bound to exactly ONE customer segment at creation (via lead-intake action). This segment binding determines:

### Segment Detection (Automatic)

During `sales:lead-intake` action:
1. AI loads all ICP files for the product: `research/customer/icp/*.md`
2. Scores the lead against each segment's observable characteristics
3. Assigns the highest-scoring segment (minimum threshold: 0.6)
4. Updates thread metadata with segment binding

### Thread Metadata with Segment

```json
{
  "segment": "{best-matching-segment}",
  "icp_file": "research/customer/icp/{segment}-icp.md",
  "icp_match_score": 0.85,
  "narrative_path": "threads/sales/narratives/{segment}/",
  "materials_version": "2025-11-14"
}
```

### Materials Referencing

All sales actions reference materials by segment:

**Narrative content:**
- Path: `threads/sales/narratives/{segment}/`
- Files: `1-problem.md`, `2-solution.md`, `3-roi.md`, `4-objections.md`
- Used in: Call scripts, email templates, pitch decks

**Product materials:**
- Path: `artifacts/sales/current/`
- Files: `pitch-deck.md`, `one-pager.md`, `call-scripts.md`, `email-templates.md`
- Shared across all segments (product-level materials)

**Segment-specific customizations:**
- Narrative language ({premium segment} vs fast-{industry} messaging)
- Use cases (seasonal trends vs core collection)
- Pricing tiers (enterprise vs mid-market)
- Success stories (similar brands in same segment)

## Sales Action Types

### Action Type Catalog

| Type | Purpose | Human Required | Duration | Skill |
|------|---------|----------------|----------|-------|
| `sales:lead-intake` | Capture lead data, initial scoring | No | 1 day | `sales-prospect-research` |
| `sales:qualification` | Discovery call, ICP validation | Yes | 3-5 days | `sales-qualification-support` |
| `sales:demo` | Product demonstration | Yes | 5-7 days | `sales-materials-generation` |
| `sales:pilot` | Pilot program execution | Yes | 14-30 days | Human workflow |
| `sales:close` | Contract negotiation, signing | Yes | 7-14 days | Human workflow |

### Action Metadata Format

```json
{
  "action_id": "qualify-{Customer}",
  "type": "sales:qualification",
  "status": "completed",
  "skill": "sales-qualification-support",
  "human_required": true,
  "assigned_to": "human",
  "created": "2025-11-15",
  "due": "2025-11-17",
  "completed": "2025-11-16",
  "result": "qualified",
  "notes": "Strong ICP fit, budget confirmed"
}
```

## Thread Metadata

```json
{
  "thread_id": "{Customer}-{premium tier}",
  "type": "sales",
  "status": "active",
  "owner": "ai-agent",
  "created": "2025-11-05",
  "updated": "2025-11-15",
  "stage": 5,
  "current_action": "sales:demo",
  "impact_score": 0.85,
  "canvas_assumptions": ["A4", "A7"],
  "related_threads": ["enterprise-{premium tier}"],
  "deal_size": 1100000,
  "close_probability": 0.60
}
```

**Sales-specific fields:**
- `current_action`: Current pipeline stage (action type)
- `deal_size`: Expected ARR (dollars)
- `close_probability`: Win probability (0.0-1.0)

## AI Agent Sales Logic

### Stage 4: Decision

**If verdict = PURSUE:**
```python
create_action(type="sales:lead-intake", auto_execute=True)
create_action(type="sales:qualification", human_required=True)
# Future actions created as previous complete
```

**If verdict = PASS:**
```python
skip_to_results(reason="disqualified")
```

### Stage 5: Actions

**Qualification result:**
```python
if action.type == "sales:qualification":
    if action.result == "qualified":
        create_action("sales:demo")
    elif action.result == "disqualified":
        skip_remaining_actions()
        proceed_to_results("deal_lost")
```

**Demo result:**
```python
if action.type == "sales:demo":
    if action.result == "interested":
        create_action("sales:pilot")
    elif action.result == "not_interested":
        skip_remaining_actions()
        proceed_to_results("deal_lost")
```

**Pilot result:**
```python
if action.type == "sales:pilot":
    if action.result == "success":
        create_action("sales:close")
    elif action.result == "failed":
        skip_remaining_actions()
        proceed_to_results("deal_lost")
```

**Close result:**
```python
if action.type == "sales:close":
    if action.result == "won":
        proceed_to_results("deal_won")
    elif action.result == "lost":
        proceed_to_results("deal_lost")
```

## Example: Sales Thread Execution

### Input Data
```
{Customer} ({segment}, ${GMV}) wants {product/feature}.
Contact: {Name} ({Title})
Budget: ${budget}/year
Context: {Context about lead source}
```

### Stage 1: Input
```markdown
# Input

**Date:** 2025-11-05

## Observation
{Customer} contacted us requesting {product/feature}.

## Details
- **Contact:** {Name}, {Title}
- **Company:** {Customer} ({segment})
- **Size:** ${GMV}
- **Budget:** ${budget}/year
- **Context:** {Context about lead source}

## Source
Inbound email via contact form

## Next Steps
Proceed to hypothesis validation (Stage 2)
```

### Stage 2: Hypothesis
```markdown
# Hypothesis

**Date:** 2025-11-07

## Canvas Assumptions Tested

### A4: {Assumption Title}
**Status:** ⚠️ CHALLENGED
**Current assumption:** {current belief}
**Evidence:** {data points}
**New hypothesis:** {refined hypothesis}
**Confidence:** 80%

### A2: {Assumption Title}
**Status:** ✅ VALIDATED
**Current assumption:** {current belief}
**Evidence:** {data confirming assumption}
**Confidence:** 95%

## Canvas Impact
- 04.segments.md (split by brand type)
- 10.assumptions.md (mark A4 challenged, A2 validated)
- 12.revenu.md (validate {premium tier} tier)

## Next Steps
Proceed to implication analysis (Stage 3)
```

### Stage 3: Implication
```markdown
# Implication

**Date:** 2025-11-10

## Deal Opportunity

### Revenue
- **Expected ARR:** $1.1M
  - Base: $500K (midpoint of budget)
  - Analytics upsell: $600K (likelihood 70%)
- **Contract term:** 2 years
- **LTV:** $2.2M

### Close Probability
- **ICP fit:** 95% ({premium segment}, technical buyer, budget confirmed)
- **Competition:** Low ({premium tier} niche)
- **Timeline:** 3 months (pilot required)
- **Overall:** 60%

### Sales Cycle
- Lead intake: 1 day
- Qualification: 3 days
- Demo: 5 days
- Pilot: 30 days
- Close: 7 days
- **Total:** 46 days

## Resource Cost

### Sales
- Qualification call: 2 hours
- Demo prep + call: 4 hours
- Pilot support: 10 hours
- Negotiation: 8 hours
- **Total:** 24 hours @ $200/hr = $4,800

### Engineering
- SDK customization: $15K
- Pilot integration: $5K
- **Total:** $20K

### Legal
- Contract review: $5K

### Total Cost
- **First deal:** $29.8K
- **Marginal cost (future deals):** $20K

## ROI Analysis

### First Deal
- Revenue: $1.1M
- Cost: $29.8K
- Margin: $1.07M (97%)
- ROI: 36x

### Risk Assessment
- **Technical risk:** Low (SDK exists)
- **Market risk:** Medium (new segment)
- **Execution risk:** Low (proven sales process)
- **Overall risk:** Medium

## Recommendation
**PURSUE** - High ROI, validates enterprise {premium tier} hypothesis

## Next Steps
Proceed to decision (Stage 4)
```

### Stage 4: Decision
```markdown
# Decision

**Date:** 2025-11-13

## Verdict
**PURSUE**

## Rationale
1. **Strong ICP fit:** {premium segment}, technical buyer, budget confirmed
2. **High ROI:** 36x on first deal
3. **Strategic validation:** Tests enterprise {premium tier} hypothesis (A4)
4. **Low risk:** SDK exists, proven sales process

## Alternatives Considered

### Wait for more data
**Rejected** - 3 enterprise inquiries = pattern established

### Partner with agency
**Rejected** - Margins too low (50% vs 97%)

### Build co-branded only
**Rejected** - Contradicts 3/5 enterprise leads requesting {premium tier}

## Success Metrics
- Close rate: >60%
- Sales cycle: <50 days
- ARR: >$400K
- NPS: >60
- Margin: >90%

## Decision Authority
**Approved by:** AI Agent (autonomous)
**Impact score:** 0.65 (medium-high, within autonomous bounds)
**Human review:** Not required (< 0.7 threshold)

## Next Steps
Proceed to actions (Stage 5)
```

### Stage 5: Actions
```markdown
# Actions

## Action 1: Lead Intake
**Type:** sales:lead-intake
**Status:** completed
**Owner:** AI Agent
**Duration:** 1 day (2025-11-15)

### Activities
- Lead data captured in CRM
- Company research completed
- ICP score calculated: 95/100
- Priority: High

**Result:** READY_FOR_QUALIFICATION

---

## Action 2: Qualification
**Type:** sales:qualification
**Status:** completed
**Owner:** Human (Founder)
**Skill:** sales-qualification-support
**Duration:** 3 days (2025-11-16 - 2025-11-18)

### Pre-Call
- AI auto-scheduled discovery call
- AI generated pre-call research brief

### Discovery Call (45 min)
**Attendees:** Sarah Chen (CTO), Founder
**ICP Validation:**
- ✓ Company size: 250 employees (50-500 range)
- ✓ GMV: $200M ($50M-$500M range)
- ✓ Decision maker: Sarah has budget authority
- ✓ Budget: $500K/year confirmed
- ✓ Timeline: 30-day pilot, then contract

**Key Insights:**
- {industry} recommendation accuracy critical (>85%)
- {premium tier} requirement (brand consistency)
- Analytics dashboard wanted (upsell opportunity)

**Result:** QUALIFIED

---

## Action 3: Demo
**Type:** sales:demo
**Status:** completed
**Owner:** Human (Founder)
**Skill:** sales-materials-generation
**Duration:** 5 days (2025-11-20 - 2025-11-24)

### Preparation
- Custom demo environment created
- {premium tier} branding applied
- Use cases tailored to {premium segment} {industry}

### Demo Call (45 min)
**Attendees:** Sarah Chen, Founder
**Demo flow:**
1. {premium tier} SDK integration (15 min)
2. {industry} recommendation engine (15 min)
3. Analytics preview (10 min)
4. Q&A (5 min)

**Technical Q&A:**
- Latency: <200ms confirmed
- Accuracy: >90% on {premium segment} dataset
- Scalability: 10M requests/day

**Next steps agreed:** 30-day pilot with 3 use cases

**Result:** INTERESTED (pilot requested)

---

## Action 4: Pilot
**Type:** sales:pilot
**Status:** completed
**Owner:** Human (Founder)
**Duration:** 30 days (2025-11-25 - 2025-12-24)

### Pilot Terms
- Duration: 30 days
- Cost: $0 (free pilot)
- Use cases: 3 (dresses, accessories, seasonal)
- Success criteria: >85% accuracy, <200ms latency

### Engineering Support
- Integration: 10 hours
- Bug fixes: 5 hours
- Optimization: 3 hours

### Results
- ✓ Accuracy: 92% (exceeded target)
- ✓ Latency: 150ms (exceeded target)
- ✓ User feedback: 4.5/5 stars
- Analytics interest confirmed

**Result:** SUCCESS

---

## Action 5: Close
**Type:** sales:close
**Status:** completed
**Owner:** Human (Founder)
**Duration:** 7 days (2025-12-26 - 2026-01-01)

### Negotiation
- Base tier: $500K/year (no change)
- Analytics add-on: $600K/year (added)
- Contract term: 2 years
- Total: $1.1M ARR

### Legal Review
- Contract review: 5 days (vs 3 days estimated)
- Terms accepted: Standard SLA, 99.9% uptime

### Signing
- Contract signed: 2026-01-01
- Start date: 2026-01-15

**Result:** WON
```

### Stage 6: Results
```markdown
# Results

**Date:** 2026-01-12

## Deal Outcome
**Status:** WON
**ARR:** $1.1M
**Contract term:** 2 years
**LTV:** $2.2M

## Metrics vs. Targets

| Metric | Target | Actual | Variance |
|--------|--------|--------|----------|
| Close rate | >60% | 100% | +67% |
| Sales cycle | <50 days | 46 days | +8% faster |
| ARR | >$400K | $1.1M | +175% |
| NPS | >60 | 65 | +8% |
| Margin | >90% | 97% | +7% |

## Resource Actuals

| Resource | Estimated | Actual | Variance |
|----------|-----------|--------|----------|
| Sales time | 24 hours | 28 hours | +17% |
| Engineering | $20K | $18K | -10% |
| Legal | $5K | $10K | +100% |
| **Total** | **$29.8K** | **$33.6K** | **+13%** |

## ROI Actual
- Revenue: $1.1M
- Cost: $33.6K
- Margin: $1.066M
- ROI: 32x (vs 36x projected)

## Key Insights
1. **Pilot critical:** Added 30 days but ensured close
2. **Legal variance:** Contract review took 5 days (not 3)
3. **Analytics attach:** 100% rate on pilot (vs 70% assumed)
4. **Engineering efficiency:** SDK customization minimal

## Next Steps
Proceed to learning (Stage 7)
```

### Stage 7: Learning
```markdown
# Learning

**Date:** 2026-01-19

## Hypothesis Validation

### A4: Brand Preferences by Segment
**Status:** ✅ VALIDATED
**Result:** {premium segment} chose {premium tier}
**Evidence:** 100% of {premium segment} inquiries chose {premium tier} (N=3)
**Confidence:** 95%
**Action:** Update Canvas - split enterprise by brand type

### A2: Enterprise Willingness to Pay
**Status:** ✅ VALIDATED
**Result:** $1.1M ARR (vs $300K+ hypothesis)
**Evidence:** Deal closed at 3.7x minimum threshold
**Confidence:** 100%
**Action:** Update Canvas - increase enterprise pricing estimates

### A7: Enterprise Close Rate
**Status:** ✅ VALIDATED
**Result:** 100% close rate (vs 60% target)
**Evidence:** 1/1 qualified deals closed
**Confidence:** 85% (N=1, need more data)
**Action:** Update Canvas - maintain 60% estimate pending more data

### A9: Sales Cycle Duration
**Status:** ⚠️ CHALLENGED
**Result:** 46 days actual vs 30 days estimated (53% variance)
**Root cause:** Pilot adds 30 days (not factored in original estimate)
**Confidence:** 90%
**Action:** Update Canvas - adjust sales cycle to 45 days for pilot deals

### H12: Analytics Upsell Rate (New)
**Status:** 🆕 NEW HYPOTHESIS
**Hypothesis:** Enterprise clients request analytics after pilot
**Evidence:** 1/1 pilot clients added analytics ($600K)
**Confidence:** 70% (N=1)
**Action:** Track in next 5 enterprise deals

## Canvas Updates Applied

### 1. Segments (04.segments.md)
**File:** `strategy/canvas/04.segments.md`
**Change:** Split enterprise segment by brand type
```markdown
## Enterprise Segment

### {premium segment} Brands
- Size: $100M-$500M GMV
- Preference: {premium tier} SDK
- Willingness to pay: $400K-$600K/year
- Close rate: 60% (validated)

### Fast {industry} Brands
- Size: $50M-$200M GMV
- Preference: Co-branded solution
- Willingness to pay: $200K-$400K/year
- Close rate: TBD (not yet validated)
```

### 2. Assumptions (10.assumptions.md)
**File:** `strategy/canvas/10.assumptions.md`
**Change:** Update A4, A2, A7, A9 status

```markdown
### A4: Brand Preferences by Segment
**Status:** ✅ VALIDATED
**Hypothesis:** {premium segment} brands prefer {premium tier}
**Confidence:** 95%
**Evidence:** threads/sales/{Customer}-{premium tier}/7-learning.md (N=3)
**Last validated:** 2026-01-19

### A2: Enterprise Willingness to Pay
**Status:** ✅ VALIDATED
**Hypothesis:** Enterprise willing to pay $300K+
**Confidence:** 100%
**Evidence:** threads/sales/{Customer}-{premium tier}/7-learning.md ($1.1M ARR)
**Last validated:** 2026-01-19

### A7: Enterprise Close Rate
**Status:** ✅ VALIDATED
**Hypothesis:** 60% close rate for qualified deals
**Confidence:** 85%
**Evidence:** threads/sales/{Customer}-{premium tier}/7-learning.md (1/1)
**Last validated:** 2026-01-19
**Note:** Low N, continue tracking

### A9: Sales Cycle Duration
**Status:** ⚠️ CHALLENGED
**Original:** 30 days
**Actual:** 45 days (pilot deals)
**Confidence:** 90%
**Evidence:** threads/sales/{Customer}-{premium tier}/7-learning.md
**Last updated:** 2026-01-19
```

### 3. Revenue (12.revenu.md)
**File:** `strategy/canvas/12.revenu.md`
**Change:** Add validated {premium tier} tier

```markdown
## {premium tier} Enterprise Tier (Validated)
- **Base SDK:** $400K-$600K/year
- **Analytics add-on:** $600K/year (100% attach rate)
- **Total ARR:** $1M-$1.2M
- **Evidence:** threads/sales/{Customer}-{premium tier}/7-learning.md
- **Confidence:** 95%
```

### 4. Metrics (13.metrics.md)
**File:** `strategy/canvas/13.metrics.md`
**Change:** Update enterprise sales metrics

```markdown
## Enterprise Sales Metrics
- **Close rate:** 60% (qualified deals)
- **Sales cycle:** 45 days (with pilot), 20 days (without pilot)
- **Average deal size:** $1.1M ARR
- **Validation:** threads/sales/{Customer}-{premium tier}/7-learning.md
```

## New Threads Generated

### business/analytics-upsell
**Trigger:** {Customer} requested analytics during pilot
**Priority:** High
**Hypothesis:** Analytics is 100% attach rate for enterprise
**Input:** Create thread to validate analytics upsell hypothesis

## Strategic Flags
**None** - Deal outcome within strategic bounds, no pivots required

## Meta-Learning Opportunities
1. **Legal estimation bias:** 5 days vs 3 days (100% variance)
   - Track next 5 deals to validate 5-day estimate
2. **Pilot impact on cycle:** +30 days consistent
   - Update Stage 3 implication templates
```

## Output Templates

### Thread Status Report
```markdown
## Thread: sales/{deal-name}

**Status:** Stage {n} of 7
**Deal size:** ${ARR}
**Close probability:** {percent}%
**Sales cycle:** {days} days (est)
**Current stage:** {action-type}

### Progress
- [✓] Stage 1: Input
- [✓] Stage 2: Hypothesis (challenged A4, validated A2)
- [✓] Stage 3: Implication (ROI: 32x)
- [✓] Stage 4: Decision (PURSUE)
- [→] Stage 5: Actions (demo in progress)
- [ ] Stage 6: Results
- [ ] Stage 7: Learning

### Next Steps
1. Complete demo call
2. Send pilot proposal
3. Schedule pilot kickoff
```

### Canvas Update Report
```markdown
## Canvas Updates: sales/{deal-name}

**Date:** {date}
**Deal outcome:** WON | LOST
**ARR:** ${amount}

### Assumptions Updated
- **A4:** Brand Preferences → ✅ VALIDATED (95% confidence)
- **A7:** Close Rate → ✅ VALIDATED (85% confidence)
- **A9:** Sales Cycle → ⚠️ CHALLENGED (90% confidence)

### Sections Modified
- strategy/canvas/04.segments.md
- strategy/canvas/10.assumptions.md
- strategy/canvas/12.revenu.md
- strategy/canvas/13.metrics.md

### New Hypotheses
- H12: Analytics upsell rate 100% for enterprise

### New Threads
- business/analytics-upsell
```

## Outbound Campaign Threads

Campaign threads orchestrate multi-prospect outbound sequences. They create individual deal threads from responses.

### Campaign Thread Structure

```
threads/sales/campaign-{name}/
├── meta.json                  # Type: "sales-campaign"
├── 1-input.md                 # Campaign hypothesis
├── 2-hypothesis.md            # ICP assumptions tested
├── 3-implication.md           # Campaign ROI analysis
├── 4-decision.md              # LAUNCH or CANCEL
├── 5-actions/
│   ├── prospect-list.md       # Type: campaign:prospect-list
│   ├── email-sequence.md      # Type: campaign:email-sequence
│   └── response-handling.md   # Type: campaign:response-handling
├── 6-results.md               # Campaign metrics
└── 7-learning.md              # ICP refinements
```

### Campaign Action Types

| Type | Purpose | Duration | Subskill |
|------|---------|----------|----------|
| `campaign:prospect-list` | Generate target list | 1-2 days | prospect-research |
| `campaign:email-sequence` | Generate outreach emails | 1 day | outreach-sequencing |
| `campaign:response-handling` | Triage responses | Ongoing | contact-finding |
| `campaign:deal-create` | Create deal thread from response | 1 day | sales-execution |

### Response Handling → Deal Thread Creation

When a prospect responds positively:

**Campaign action:**
```python
if response_type == "interested":
    create_deal_thread(
        type="sales",
        product=campaign.product,
        segment=campaign.segment,  # Inherited from campaign
        lead_source=f"campaign:{campaign.id}",
        initial_action="sales:qualification"
    )
```

**New deal thread metadata:**
```json
{
  "thread_id": "{company-name}",
  "type": "sales",
  "segment": "{campaign.segment}",  # Inherited
  "lead_source": "campaign:{premium segment}-brands-q1",
  "created": "2025-11-15",
  "stage": 1,
  "icp_file": "research/customer/icp/{segment}-icp.md"
}
```

### Example: Campaign Flow

**Campaign:** {premium segment}-brands-q1
**Segment:** {premium segment}-department-stores
**Target list:** 50 {premium segment} brands (ICP score >0.8)

**Actions:**
1. `campaign:prospect-list` → Generate 50 prospects
2. `campaign:email-sequence` → 3-email sequence (intro, value, demo offer)
3. `campaign:response-handling` → 12 responses received
   - 8 interested → Create 8 deal threads
   - 3 not now → Add to nurture list
   - 1 unsubscribe → Remove from list

**Deal threads created:**
- `sales/nordstrom-{premium tier}` (segment: {premium segment}-department-stores)
- `sales/saks-personalization` (segment: {premium segment}-department-stores)
- ... (6 more)

## Human Touch Points

### Discovery Call (Qualification)
- **Duration:** 30-45 min
- **Attendees:** Prospect CTO/VP, Founder
- **AI prep:** Research brief, ICP checklist, calendar scheduling
- **Human tasks:** Build rapport, validate ICP, understand pain points
- **AI follow-up:** Send summary, next steps email

### Demo Call
- **Duration:** 45 min
- **Attendees:** Prospect technical team, Founder
- **AI prep:** Custom demo environment, use case scenarios
- **Human tasks:** Present solution, answer technical questions, build confidence
- **AI follow-up:** Demo recording, technical docs, pilot proposal

### Pilot Negotiation
- **Duration:** 30 min
- **Attendees:** Prospect stakeholders, Founder
- **AI prep:** Pilot terms template, success criteria, ROI calculator
- **Human tasks:** Negotiate terms, set expectations, define success
- **AI follow-up:** Pilot agreement, kickoff email

### Contract Closing
- **Duration:** Multiple calls (2-3 hours total)
- **Attendees:** Prospect decision makers, legal, Founder
- **AI prep:** Contract draft, pricing calculator, legal docs
- **Human tasks:** Final negotiation, address concerns, sign contract
- **AI follow-up:** Onboarding sequence, customer success handoff

## AI Automation Points

### Lead Intake
- ✅ Capture lead data from form/email
- ✅ Company research (funding, size, tech stack)
- ✅ ICP scoring (0-100)
- ✅ Priority assignment (high/medium/low)
- ✅ Create CRM record

### Qualification
- ✅ Auto-schedule discovery call
- ✅ Generate pre-call research brief
- ✅ Send follow-up email with next steps
- ✅ Update CRM status

### Demo
- ✅ Create custom demo environment
- ✅ Generate use case scenarios
- ✅ Send calendar invite with agenda
- ✅ Record demo (with permission)
- ✅ Send demo recording + docs

### Pilot
- ✅ Generate pilot agreement
- ✅ Schedule kickoff call
- ✅ Track pilot progress (automated reports)
- ✅ Send weekly updates to prospect
- ✅ Compile pilot results

### Close
- ✅ Generate contract draft
- ✅ Track negotiation rounds
- ✅ Send for legal review
- ✅ Schedule signing call
- ✅ Trigger onboarding sequence