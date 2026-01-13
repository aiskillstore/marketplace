---
name: foundations-market-intelligence
description: Market analysis and competitive intelligence for startups. Use when analyzing market opportunities, sizing TAM, profiling segments, or mapping competition.
---

# Market Intelligence Agent

## Overview

The Market Intelligence Agent provides comprehensive market analysis for startup decision-making. This agent merges four specialized capabilities: Context Mapping, Opportunity Evaluation, Segment Profiling, and Competitor Intelligence into a unified workflow that produces actionable market insights.

**Primary Use Cases**: Market discovery, TAM/SAM/SOM analysis, competitive assessment, customer segmentation, opportunity scoring, market timing evaluation.

**Lifecycle Phases**: Discovery (primary), quarterly reviews, major pivots, expansion planning.

## Core Functions

### 1. Market Sizing & Segmentation

Calculate addressable market using rigorous bottom-up and top-down methodologies.

**Workflow**:

1. **Define Market Boundaries**
   - Establish geographic scope (countries, regions, cities)
   - Identify industry vertical(s) and sub-segments
   - Clarify product/service category definition

2. **Calculate TAM (Total Addressable Market)**
   - **Top-Down Method**: Industry reports × applicable percentage
   - **Bottom-Up Method**: Target customer count × average revenue per customer × adoption rate
   - **Value Theory Method**: Problem cost × affected population × solution value capture
   - Cross-validate all three methods; use conservative estimates

3. **Calculate SAM (Serviceable Addressable Market)**
   - Apply geographic constraints
   - Apply channel access limitations
   - Apply regulatory or compliance filters
   - SAM = TAM × (serviceable percentage)

4. **Calculate SOM (Serviceable Obtainable Market)**
   - Assess realistic market share in 1-3 years
   - Factor in competitive intensity
   - Account for GTM capacity constraints
   - SOM = SAM × (obtainable market share %)

5. **Segment the Market**
   - **Demographic Segmentation**: Age, income, company size, industry
   - **Psychographic Segmentation**: Values, attitudes, lifestyle, culture
   - **Jobs-to-be-Done Segmentation**: Functional jobs, emotional jobs, social jobs
   - Identify 3-5 distinct segments with unique characteristics

6. **Validate Segment Viability**
   - **Willingness to Pay**: Evidence of budget allocation for similar solutions
   - **Urgency Score**: How critical is solving this problem (1-5 scale)
   - **Accessible Channels**: Can you reach this segment cost-effectively?
   - Rank segments by: size × urgency × accessibility

**Output Template**:
```
Market Size Analysis
├── TAM: $XXM - $XXXM (methodology: top-down + bottom-up)
├── SAM: $XXM - $XXM (X% of TAM, constraints: geography, channels)
├── SOM (Year 1-3): $XM - $XXM (X% market share assumption)
└── Confidence Level: High/Medium/Low (rationale)

Top 3 Segments (prioritized):
1. [Segment Name]
   - Size: X customers / $XXM market
   - Pain Severity: X/5
   - Urgency: X/5
   - Accessibility: [channels]
   - Willingness to Pay: $X-$X per [unit]

2. [Segment Name]...
3. [Segment Name]...

Penetration Strategy:
- Entry segment: [Segment 1]
- Expansion path: [Segment 1] → [Segment 2] → [Segment 3]
- Rationale: [why this sequence]
```

### 2. Competitive Analysis

Map the competitive landscape to identify differentiation opportunities and strategic positioning.

**Workflow**:

1. **Identify Competitors**
   - **Direct Competitors**: Same solution, same target customer
   - **Indirect Competitors**: Different solution, same job-to-be-done
   - **Future Threats**: Adjacent players who could enter, tech disruption
   - Limit to top 5 most relevant competitors for focus

2. **Analyze Competitive Positioning**
   - Value proposition and messaging
   - Target customer segments
   - Pricing strategy and business model
   - Brand perception and market position

3. **Map Feature Gaps**
   - Core features they offer
   - Notable omissions or weaknesses
   - User complaints and pain points (review mining)
   - Technical limitations or debt

4. **Assess Go-to-Market Strategies**
   - Primary acquisition channels
   - Sales model (self-serve, sales-led, hybrid)
   - Partnership ecosystem
   - Content and thought leadership

5. **Track Strategic Activity**
   - Recent funding rounds and amounts
   - Product releases and roadmap signals
   - Pricing changes and promotional tactics
   - Acquisitions, partnerships, leadership changes

6. **Identify Differentiation Opportunities**
   - Unserved or underserved segments
   - Feature gaps with high customer demand
   - Business model innovations (pricing, packaging)
   - Channel or GTM advantages

**Output Template**:
```
Competitive Matrix

| Competitor | Positioning | Strengths | Weaknesses | Pricing | Funding |
|------------|-------------|-----------|------------|---------|---------|
| [Name 1]   | [1 line]    | [3 max]   | [3 max]    | $X/mo   | $XM     |
| [Name 2]   | [1 line]    | [3 max]   | [3 max]    | $X/mo   | $XM     |
| ...        |             |           |            |         |         |

Differentiation Opportunities:
1. [Opportunity]: [Description + rationale]
2. [Opportunity]: [Description + rationale]
3. [Opportunity]: [Description + rationale]

Competitive Threats:
- Immediate: [threat + mitigation strategy]
- Medium-term: [threat + monitoring plan]
- Long-term: [threat + strategic positioning]

Recommended Positioning:
[1-2 sentences describing unique strategic position]
```

### 3. Customer Intelligence

Deep research into target customer problems, buying behavior, and decision criteria.

**Workflow**:

1. **Research Pain Points**
   - **Primary Research**: Customer interviews (minimum 10-15 for validity)
   - **Secondary Research**: Reviews, forums, support tickets, social media
   - **Jobs-to-be-Done Analysis**: Functional, emotional, and social jobs
   - Quantify: frequency, severity, current workarounds

2. **Define Ideal Customer Profile (ICP)**
   - **Firmographics** (B2B): Company size, industry, revenue, growth stage
   - **Demographics** (B2C): Age, income, location, education, occupation
   - **Behavioral**: Tech adoption curve, buying triggers, budget authority
   - **Psychographic**: Values, motivations, fears, aspirations

3. **Create Personas**
   - 2-3 primary personas (avoid over-proliferation)
   - Include: role, goals, challenges, information sources, objections
   - Map buying journey: awareness → consideration → decision → retention
   - Define anti-personas (who NOT to target)

4. **Quantify Problem & Solution Value**
   - **Problem Severity**: Cost of status quo (time, money, opportunity cost)
   - **Solution Value**: ROI or value delivery in measurable terms
   - **Switching Costs**: Effort required to adopt (time, training, migration)
   - Calculate value-to-cost ratio for prioritization

5. **Map Buying Process**
   - Decision-maker vs. influencers vs. users
   - Evaluation criteria and deal-breakers
   - Typical sales cycle length
   - Budget cycles and procurement processes

**Output Template**:
```
Ideal Customer Profile (ICP)
[B2B Example]
├── Company Size: X-X employees
├── Revenue: $XM-$XM ARR
├── Industry: [primary], [secondary]
├── Growth Stage: [seed/series A/B/growth]
├── Tech Stack: [key technologies]
└── Buying Authority: [role/title]

Primary Persona: [Name/Title]
├── Goals: [3 key objectives]
├── Challenges: [3 main pain points]
├── Daily Context: [typical day/workflow]
├── Information Sources: [where they learn]
├── Objections: [typical concerns]
└── Success Metrics: [how they measure results]

Anti-Persona: [Who NOT to target]
- [Profile]: [reason to avoid]

Customer Acquisition Strategy:
├── Entry Point: [specific pain point to lead with]
├── Value Proof: [how to demonstrate value quickly]
├── Buying Triggers: [events that create urgency]
└── First Purchase: [initial offering to convert]

Problem-Solution Economics:
├── Annual Cost of Problem: $X per customer
├── Solution Value Delivery: $X per customer per year
├── Value-to-Price Ratio: Xx (target: >10x for early stage)
└── Payback Period: X months
```

### 4. Market Dynamics

Assess market growth, trends, and timing to evaluate entry strategy and readiness.

**Workflow**:

1. **Assess Market Growth**
   - Historical growth rate (CAGR) over 3-5 years
   - Projected growth rate for next 3-5 years
   - Identify growth drivers and constraints
   - Evaluate if market is expanding, mature, or contracting

2. **Identify Consolidation Trends**
   - M&A activity in the space
   - Market concentration (few large players vs. fragmented)
   - Platform dynamics and winner-take-most effects
   - Network effects and defensibility patterns

3. **Detect Disruption Signals**
   - Technology enablers (new tech making new solutions possible)
   - Regulatory shifts (new laws, compliance requirements)
   - Cultural changes (shifting behaviors, values, preferences)
   - Economic factors (recession, inflation, disposable income)

4. **Evaluate Market Readiness**
   - **Too Early**: Education required, infrastructure missing, budget unavailable
   - **Right Time**: Awareness exists, budget allocated, infrastructure ready
   - **Too Late**: Incumbents entrenched, commoditization underway
   - Map adoption curve: innovators → early adopters → early majority → late majority

5. **Assess Category Creation vs. Category Entry**
   - **Category Creation**: Educate market, higher risk, potential for category leadership
   - **Category Entry**: Leverage existing demand, lower risk, compete on differentiation
   - Determine positioning strategy accordingly

**Output Template**:
```
Market Dynamics Assessment

Growth Profile:
├── Historical CAGR: X% (20XX-20XX)
├── Projected CAGR: X% (20XX-20XX)
├── Growth Stage: [emerging/growth/mature/declining]
└── Growth Drivers: [3 key factors]

Market Structure:
├── Concentration: [fragmented/consolidating/oligopoly]
├── Recent M&A: [X acquisitions in past 2 years]
├── Market Leader Share: X%
└── Defensibility: [network effects/switching costs/brand/other]

Disruption Signals:
├── Technology: [enabling technology shifts]
├── Regulatory: [policy changes affecting market]
├── Cultural: [behavioral or preference shifts]
└── Economic: [macro factors]

Market Timing Assessment:
├── Timing Score: X/100
├── Adoption Phase: [innovators/early adopters/early majority/late majority]
├── Market Readiness: [too early/right time/too late]
└── Rationale: [2-3 sentences]

Entry Strategy:
├── Approach: [category creation/category entry]
├── Positioning: [how to frame the solution]
├── Education Required: [low/medium/high]
└── Timing Recommendation: [now/wait X months/conditions to meet]
```

### 5. Opportunity Scoring

Synthesize all intelligence into a comprehensive go/no-go recommendation.

**Workflow**:

1. **Evaluate Market Attractiveness**
   - Market size and growth rate (weight: 30%)
   - Willingness to pay and unit economics (weight: 25%)
   - Accessibility and competition level (weight: 20%)
   - Strategic importance and future optionality (weight: 15%)
   - Market timing and momentum (weight: 10%)

2. **Assess Competitive Intensity**
   - Number and strength of incumbents
   - Barriers to entry (capital, regulation, network effects)
   - Differentiation potential (can you be 10x better?)
   - Competitive response likelihood and speed

3. **Evaluate Execution Fit**
   - Team expertise and domain knowledge
   - Resource requirements vs. availability
   - Time to market and burn rate implications
   - Strategic alignment with company vision

4. **Risk Assessment**
   - **Market Risks**: Market smaller than estimated, adoption slower than expected
   - **Timing Risks**: Too early (education costs), too late (incumbents entrenched)
   - **Competitive Risks**: Well-funded competitor launches, price wars
   - **Execution Risks**: Technical complexity, regulatory hurdles, talent availability

5. **Prioritize Opportunities**
   - **By ROI Potential**: Expected return vs. investment required
   - **By Strategic Value**: Long-term positioning, optionality, learning value
   - **By Speed**: Time to first revenue, time to validation

6. **Generate Recommendation**
   - Go/No-Go decision with confidence level (%)
   - Key assumptions and validation experiments
   - Next 3 immediate actions to de-risk or capitalize

**Output Template**:
```
Opportunity Scoring Summary

Overall Score: XX/100 (Recommendation: GO / NO-GO / INVESTIGATE FURTHER)

Component Scores:
├── Market Attractiveness: XX/100 (weight: 30%)
│   ├── Size & Growth: X/25
│   ├── Economics: X/25
│   ├── Accessibility: X/25
│   └── Timing: X/25
├── Competitive Position: XX/100 (weight: 35%)
│   ├── Differentiation Potential: X/35
│   ├── Barriers to Entry: X/35
│   └── Competitive Intensity: X/30
└── Execution Fit: XX/100 (weight: 35%)
    ├── Team/Expertise: X/35
    ├── Resources Available: X/35
    └── Strategic Alignment: X/30

Risk Assessment:
├── CRITICAL RISKS (kill if not mitigated):
│   - [Risk]: [Mitigation approach]
├── HIGH RISKS (monitor closely):
│   - [Risk]: [Mitigation approach]
└── MEDIUM RISKS (acceptable):
    - [Risk]: [Mitigation approach]

Key Assumptions to Validate:
1. [Assumption]: [Validation method]
2. [Assumption]: [Validation method]
3. [Assumption]: [Validation method]

Recommended Next Actions:
1. [Action]: [Expected outcome + timeline]
2. [Action]: [Expected outcome + timeline]
3. [Action]: [Expected outcome + timeline]

Confidence Level: X% (rationale: [1-2 sentences])
```

## Input Requirements

To perform comprehensive market intelligence analysis, provide:

**Required**:
- `product_idea`: Brief description (1-2 sentences) of what you're building
- `target_geography`: List of countries/regions to analyze
- `industry_vertical`: Primary industry or category

**Optional**:
- `initial_hypothesis`: Your assumptions about market, customer, competition
- `constraints`: Budget, timeline, team size limitations
- `strategic_context`: Company goals, pivoting from what, expansion plans

**Example Input**:
```
product_idea: "AI-powered beauty product recommendations based on skin analysis and personal preferences"
target_geography: ["United States", "Canada"]
industry_vertical: "Beauty & Personal Care - Digital/D2C"
initial_hypothesis: {
  "target_customer": "Women 25-40, digitally native, skincare enthusiasts",
  "willingness_to_pay": "$15-30/month subscription",
  "main_competitor": "Sephora's Color IQ, Function of Beauty"
}
```

## Output Structure

All market intelligence analysis follows this standardized format:

```json
{
  "market_size": {
    "TAM": 5000000000,
    "SAM": 1200000000,
    "SOM": 24000000,
    "confidence": "medium",
    "methodology": "bottom-up + top-down validated"
  },
  "top_segments": [
    {
      "name": "Skincare Enthusiasts (25-40)",
      "size": 12000000,
      "pain_severity": 4,
      "urgency": 3,
      "accessibility": "high",
      "willingness_to_pay": "$20-35/month"
    },
    {
      "name": "Beauty Novices Seeking Guidance",
      "size": 8500000,
      "pain_severity": 3,
      "urgency": 2,
      "accessibility": "medium",
      "willingness_to_pay": "$10-20/month"
    },
    {
      "name": "Professional MUAs & Estheticians",
      "size": 450000,
      "pain_severity": 5,
      "urgency": 4,
      "accessibility": "medium",
      "willingness_to_pay": "$50-100/month"
    }
  ],
  "competitors": [
    {
      "name": "Function of Beauty",
      "positioning": "Personalized haircare via quiz",
      "strengths": ["Strong brand", "Proven unit economics", "Wide distribution"],
      "gaps": ["Limited to hair", "No AI/skin analysis", "High price point"],
      "pricing": "$30-50/month",
      "funding": "$150M Series C"
    }
  ],
  "market_timing": {
    "score": 78,
    "rationale": "AI beauty tech awareness high post-2023, but market not saturated. Early majority adoption phase. Strong timing.",
    "recommendation": "Enter now"
  },
  "next_actions": [
    "Validate willingness-to-pay with 20 customer interviews in primary segment",
    "Build competitive feature matrix and identify 3 key differentiation points",
    "Run micro-landing page test to validate demand ($500 budget, 2 weeks)"
  ]
}
```

## Integration with Other Agents

### Provides Input To:

**problem-solution-fit**: Market insights inform which problems to prioritize
- Segment profiles → Problem validation focus areas
- Competitive gaps → Solution differentiation requirements

**value-proposition**: Market positioning informs value articulation
- Top segments → Target customer definition
- Competitive analysis → Differentiation messaging

**business-model**: Market economics drive business model design
- Willingness to pay → Pricing strategy
- Market size → Revenue projections

**go-to-market**: Market intelligence shapes channel strategy
- Customer profiles → Channel selection
- Competitive dynamics → Launch timing and positioning

### Receives Input From:

**validation**: Experiment results refine market assumptions
- Validated hypotheses → Update market sizing
- Customer feedback → Refine segment profiles

**execution**: Actual user data improves intelligence accuracy
- User demographics → Validate ICP accuracy
- Pricing tests → Refine willingness-to-pay estimates

## Best Practices

### For Accurate Market Sizing

1. **Always Use Multiple Methods**: Cross-validate TAM with top-down AND bottom-up
2. **Be Conservative**: When in doubt, use lower estimates (better to exceed than miss)
3. **Document Assumptions**: Every number should have a source and calculation method
4. **Update Regularly**: Market intelligence degrades; refresh quarterly at minimum

### For Competitive Analysis

1. **Focus on Top 5**: More competitors = diluted insights, focus on most relevant
2. **Mine User Reviews**: G2, Capterra, App Store reviews reveal true strengths/weaknesses
3. **Track Changes**: Set Google Alerts, monitor product releases, pricing changes
4. **Look Beyond Features**: Business model, GTM, and positioning matter more than features

### For Customer Intelligence

1. **Talk to Customers**: No amount of desk research replaces 15 real conversations
2. **Seek Disconfirming Evidence**: Actively look for data that contradicts your hypothesis
3. **Quantify Everything**: "Customers want X" is weak; "73% rated X as critical" is strong
4. **Identify Anti-Personas**: Knowing who NOT to target is as valuable as ICP

### For Market Timing

1. **Look for Inflection Points**: Technology shifts, regulatory changes, cultural moments
2. **Assess Education Required**: High education cost = wait or plan for slow adoption
3. **Monitor Adjacent Markets**: What's happening in related industries signals future trends
4. **Balance First-Mover vs. Fast-Follower**: Being first isn't always winning

## Common Pitfalls to Avoid

**Market Sizing Errors**:
- ❌ Using TAM as if it's achievable (confusing TAM with SOM)
- ❌ Top-down only (leads to inflated estimates)
- ❌ Not accounting for accessibility constraints
- ✅ Conservative, multi-method validation with clear assumptions

**Competitive Analysis Errors**:
- ❌ Analyzing too many competitors (lose focus)
- ❌ Focusing only on direct competitors (miss disruption from adjacent spaces)
- ❌ Assuming competitors are static (they will respond)
- ✅ Focus on top 5, include indirect and future threats, plan for responses

**Customer Intelligence Errors**:
- ❌ Talking only to early adopters (they're not representative)
- ❌ Asking "would you buy this?" (leads to false positives)
- ❌ Creating too many personas (analysis paralysis)
- ✅ Talk to mainstream buyers, observe behavior, focus on 2-3 personas

**Market Timing Errors**:
- ❌ Assuming "inevitable" means "imminent" (timing is everything)
- ❌ Ignoring category creation costs (education is expensive)
- ❌ Missing regulatory or infrastructure dependencies
- ✅ Assess readiness realistically, plan for education costs, validate timing assumptions

## Usage Examples

### Example 1: Discovery Phase - New Market Entry

**User Request**: "Analyze the market for AI-powered personal finance coaching for Gen Z"

**Agent Process**:
1. Market Sizing: TAM/SAM/SOM for Gen Z (18-27) in US personal finance coaching
2. Segmentation: Students, early career, gig workers, crypto-natives
3. Competitive Analysis: Mint, YNAB, Betterment, Copilot, traditional advisors
4. Customer Intelligence: Gen Z money anxieties, digital-first preferences, trust factors
5. Market Dynamics: Shift from budgeting tools to coaching, AI personalization trend
6. Opportunity Score: 72/100 - GO with caveats on willingness-to-pay validation

**Output**: Complete market intelligence report with recommended entry segment and next 3 actions

### Example 2: Quarterly Review - Market Evolution

**User Request**: "Update our market intelligence - we launched 6 months ago, seeing traction in enterprise segment"

**Agent Process**:
1. Refresh competitive analysis: New entrants, competitive responses
2. Validate segment hypotheses: Did enterprise match projections?
3. Update market sizing: Based on actual conversion data
4. Identify new opportunities: Adjacent segments, expansion markets
5. Assess competitive threats: Who's moving into your space?

**Output**: Updated market intelligence focusing on changes and new opportunities

### Example 3: Pivot Decision - Alternative Market

**User Request**: "We're struggling in B2C, should we pivot to B2B SaaS?"

**Agent Process**:
1. Analyze B2B market: Size, growth, competition
2. Compare markets: B2C vs B2B opportunity scoring
3. Assess execution fit: Does team have B2B GTM expertise?
4. Risk analysis: Pivot risks vs. stay-the-course risks
5. Generate recommendation: GO/NO-GO with confidence level

**Output**: Comparative market analysis with pivot recommendation and de-risking actions

## Success Metrics

Track these metrics to ensure market intelligence effectiveness:

**Accuracy**: How often do market size estimates match reality? (Target: ±30%)
**Usefulness**: Do other agents use this intelligence in their work? (Target: >80% utilization)
**Freshness**: How often is intelligence updated? (Target: Quarterly minimum)
**Action Orientation**: Do intelligence reports lead to clear next actions? (Target: 100%)

## Quarterly Review Checklist

Run this checklist every quarter to keep intelligence current:

- [ ] Update TAM/SAM/SOM based on latest industry data
- [ ] Refresh competitive matrix: new entrants, exits, pivots
- [ ] Validate ICP accuracy against actual customer data
- [ ] Reassess market timing and growth trajectory
- [ ] Update opportunity score based on new information
- [ ] Identify 3 new opportunities or threats
- [ ] Generate updated next actions for upcoming quarter

---

This agent transforms raw market data into strategic intelligence, enabling informed decisions about market entry, positioning, and resource allocation.
