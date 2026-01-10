---
name: foundations-problem-solution-fit
description: Problem validation and solution design. Use when discovering customer problems, generating solution hypotheses, or defining MVP scope.
---

# Problem-Solution Fit Agent

## Overview

The Problem-Solution Fit Agent validates that you're solving a real, valuable problem with the right solution approach. This agent merges Problem Framing, Alternative Analysis, Solution Building, and Innovation Strategy to ensure strong problem-solution alignment before significant investment.

**Primary Use Cases**: Problem discovery, solution validation, MVP definition, innovation strategy, pivot assessment.

**Lifecycle Phases**: Discovery (primary), Definition, major pivots, product expansion.

## Core Functions

### 1. Problem Discovery

Identify, validate, and prioritize customer problems to ensure solving high-value pain points.

**Workflow**:

1. **Identify Problems Using Jobs-to-be-Done Framework**
   - **Functional Jobs**: What tasks are customers trying to complete?
   - **Emotional Jobs**: How do customers want to feel? What anxieties to avoid?
   - **Social Jobs**: How do customers want to be perceived by others?
   - Map current workflow and identify friction points

2. **Measure Pain Frequency**
   - **Daily**: Problem occurs every day
   - **Weekly**: Problem occurs 1-4 times per week
   - **Monthly**: Problem occurs 1-4 times per month
   - **Quarterly**: Problem occurs occasionally
   - Higher frequency = higher awareness and urgency

3. **Assess Pain Intensity**
   - **1 - Minor annoyance**: Tolerable, low willingness to pay
   - **2 - Noticeable frustration**: Aware but not urgent
   - **3 - Significant problem**: Actively seeking solutions
   - **4 - Major pain point**: High urgency, budget allocated
   - **5 - Critical/existential**: Business-critical, will pay premium

4. **Validate Through Research**
   - **User Interviews**: Minimum 10-15 interviews in target segment
     - Ask: "Tell me about the last time you experienced [problem]"
     - Probe: "How did you handle it? What did it cost you?"
     - Avoid: "Would you use a solution that does X?" (leading question)
   - **Observational Studies**: Shadow users in their natural environment
   - **Data Analysis**: Support tickets, review mining, search query data

5. **Prioritize Problems**
   - **Severity Score**: Frequency × Intensity
   - **Solvability Assessment**: Technical feasibility, cost to solve, time to market
   - **Strategic Fit**: Aligns with company vision, capabilities, market position
   - **Problem Stack Rank**: Top 3-5 problems to pursue

**Output Template**:
```
Validated Problem Stack Rank

1. [Problem Statement]
   ├── Job-to-be-Done: [functional/emotional/social job]
   ├── Frequency: [daily/weekly/monthly/quarterly]
   ├── Intensity: X/5
   ├── Severity Score: XX (frequency × intensity)
   ├── Current Cost: $X per [time period] or X hours per [time period]
   ├── Evidence: [interview quotes, data points, observations]
   ├── Solvability: [high/medium/low] (rationale)
   └── Priority: 1 (recommended focus)

2. [Problem Statement]...
3. [Problem Statement]...

Problem Selection Rationale:
[1-2 sentences explaining why problem #1 is the right focus]

Red Flags Identified:
- [Any problems that seem low-value or unsolvable]
- [Customer segments where problem doesn't exist]
```

### 2. Solution Hypothesis

Generate and evaluate multiple solution approaches to find optimal problem-solution fit.

**Workflow**:

1. **Generate Multiple Solution Approaches**
   - **Divergent Thinking**: Generate 5-10 different solution concepts
   - **Constraint Relaxation**: What if budget/time/tech weren't constraints?
   - **Analogy Mining**: How do other industries solve similar problems?
   - **User Co-Creation**: Involve customers in solution ideation

2. **Evaluate Technical Feasibility**
   - **Existing Technology**: Can be built with current tech stack
   - **Emerging Technology**: Requires new but available technology
   - **Research Required**: Needs R&D or breakthroughs
   - **Impossible Today**: Not feasible with current technology

3. **Assess Effort vs Impact**
   - **Effort**: S (small - days), M (medium - weeks), L (large - months)
   - **Impact**: Low (nice-to-have), Medium (meaningful improvement), High (10x better)
   - **Prioritization Matrix**: High impact + Low effort = Quick wins

4. **Evaluate Build vs Buy vs Partner**
   - **Build**: Core differentiation, IP ownership, full control
   - **Buy**: Commodity feature, faster time-to-market, proven solution
   - **Partner**: Complementary capabilities, shared risk, ecosystem play

5. **Prototype and Test**
   - **Low-Fidelity Mockups**: Sketches, wireframes, storyboards
   - **Concept Testing**: Present concepts to users, gather feedback
   - **Wizard of Oz**: Manual process behind automated facade
   - **Concierge MVP**: High-touch service to validate value before automation

**Output Template**:
```
Solution Hypothesis Evaluation

Problem Being Solved: [Problem #1 from stack rank]

Solution Concepts (Top 3):

Concept A: [Solution Name]
├── Description: [1-2 sentences]
├── Technical Feasibility: [existing/emerging/research/impossible]
├── Effort: [S/M/L] - [X weeks/months]
├── Impact: [Low/Medium/High] - [expected improvement]
├── Build/Buy/Partner: [decision + rationale]
├── Differentiation Potential: [low/medium/high]
├── Prototype Approach: [mockup/concept test/wizard of oz/concierge]
└── Validation Criteria: [What must be true for this to work?]

Concept B: [Solution Name]...
Concept C: [Solution Name]...

Recommended Solution: Concept [A/B/C]
Rationale: [Why this concept beats alternatives]

Next Steps:
1. [First validation experiment]
2. [Second validation experiment]
3. [MVP scoping if validation succeeds]
```

### 3. Alternative Analysis

Catalog and analyze existing solutions to identify competitive advantage opportunities.

**Workflow**:

1. **Catalog Current Solutions**
   - **Direct Competitors**: Same problem, similar solution
   - **Indirect Competitors**: Same problem, different solution
   - **Workarounds**: Manual processes, hacks, duct-tape solutions
   - **Non-Consumption**: People who have problem but don't solve it

2. **Assess Customer Satisfaction**
   - **Satisfaction Score**: 1 (very dissatisfied) to 5 (very satisfied)
   - **Net Promoter Score**: Likelihood to recommend current solution
   - **Review Mining**: Extract common complaints and praises
   - **Churn/Retention Data**: Why do users leave or stay?

3. **Identify Switching Barriers**
   - **Financial**: Sunk costs, contracts, switching fees
   - **Technical**: Data migration, integration complexity, learning curve
   - **Organizational**: Process changes, stakeholder buy-in, training
   - **Psychological**: Loss aversion, status quo bias, risk perception

4. **Map Unmet Needs**
   - **Feature Gaps**: What do users wish existed?
   - **Performance Gaps**: What's too slow, expensive, or complex?
   - **Experience Gaps**: Where is UX frustrating or confusing?
   - **Integration Gaps**: What doesn't connect that should?

5. **Determine Adoption Triggers**
   - **What event would make someone switch?**: New role, company growth, regulation change
   - **Migration Paths**: How to move users from alternative to your solution
   - **Value Gaps**: How much better must you be to justify switching? (10x rule)

**Output Template**:
```
Alternative Analysis

Existing Alternatives (Top 5):

1. [Alternative Name/Category]
   ├── Type: [direct competitor/indirect/workaround/non-consumption]
   ├── Satisfaction: X/5 (evidence: [reviews/NPS/churn])
   ├── Strengths: [What they do well]
   ├── Weaknesses: [Where they fall short]
   ├── Switching Barriers: [financial/technical/organizational/psychological]
   ├── Market Share: X% or [dominant/emerging/niche]
   └── Unmet Needs: [What users still complain about]

2. [Alternative Name/Category]...

Competitive Advantage Opportunities:

1. [Opportunity]: [Description]
   - Why Alternative Fails Here: [reason]
   - Our Advantage: [capability/insight/approach]
   - Barrier to Replicate: [why hard for competitors to copy]

2. [Opportunity]...
3. [Opportunity]...

Adoption Strategy:
├── Adoption Trigger: [event/pain point that creates urgency]
├── Migration Path: [how to move users from alternative]
├── Required Superiority: [10x better on dimension X]
└── Early Adopter Profile: [who switches first]

Switching Cost Mitigation:
- [How to reduce financial barriers]
- [How to reduce technical barriers]
- [How to reduce organizational barriers]
```

### 4. MVP Definition

Define minimum viable product scope with clear success metrics and development priorities.

**Workflow**:

1. **Determine Feature Categories**
   - **Core Features**: Must-have for MVP, solves primary problem
   - **Nice-to-Haves**: Valuable but not essential for first version
   - **Non-Features**: Explicitly out of scope for MVP (but maybe later)

2. **Map Features to Problems**
   - Each core feature must solve a validated problem
   - Avoid "cool tech" or "nice UX" without problem linkage
   - Test: "If we remove this feature, can we still solve the core problem?"

3. **Create User Stories**
   - Format: "As a [user type], I want [action] so that [benefit]"
   - Include: Acceptance criteria, edge cases, error states
   - Estimate: Story points or t-shirt sizing (S/M/L)

4. **Estimate Development Effort**
   - **Small**: 1-3 days, low technical risk, clear requirements
   - **Medium**: 1-2 weeks, moderate risk, some unknowns
   - **Large**: 2+ weeks, high risk, significant unknowns or dependencies
   - Total MVP timeline should be 4-12 weeks max

5. **Assess Technical Risk**
   - **Low Risk**: Proven technology, team has experience
   - **Medium Risk**: New to team but proven elsewhere
   - **High Risk**: Cutting edge, uncertain feasibility, no prior art
   - Flag dependencies: APIs, third-party services, integrations

6. **Define Success Metrics**
   - **Activation**: % users who complete key action
   - **Engagement**: Frequency of use, time spent
   - **Retention**: % users active after 1 week, 1 month
   - **Satisfaction**: NPS, CSAT, or qualitative feedback
   - **Business Metric**: Revenue, conversions, or strategic goal

**Output Template**:
```
MVP Specification

Core Features (Must-Have):

1. [Feature Name]
   ├── Solves: [Problem from stack rank]
   ├── User Story: As a [user], I want [action] so that [benefit]
   ├── Acceptance Criteria: [What defines "done"]
   ├── Effort: [S/M/L] - [X days/weeks]
   ├── Technical Risk: [Low/Medium/High]
   ├── Dependencies: [APIs, services, other features]
   └── Priority: P0 (must have for launch)

2. [Feature Name]...

Nice-to-Haves (Post-MVP):
- [Feature]: [Why valuable but not essential]
- [Feature]: [Why valuable but not essential]

Explicit Non-Features:
- [Feature]: [Why explicitly out of scope]
- [Feature]: [Why explicitly out of scope]

MVP Timeline:
├── Total Effort: X weeks
├── High-Risk Items: [features requiring de-risking]
├── Critical Path: [feature A] → [feature B] → [launch]
└── Launch Date Target: [date or week]

Success Metrics:
├── Activation: X% complete [key action]
├── Engagement: X% use [frequency]
├── Retention: X% active after 1 week
├── Satisfaction: NPS > X or [qualitative threshold]
└── Business Goal: [revenue/conversions/strategic metric]

Pivot Triggers:
- If activation < X%, reconsider [assumption]
- If retention < X%, problem not painful enough
- If satisfaction < X%, solution doesn't fit problem
```

### 5. Innovation Strategy

Identify unique insights and defensible advantages to create 10x better solutions.

**Workflow**:

1. **Identify 10x Improvement Opportunities**
   - **10x Faster**: What takes hours could take seconds?
   - **10x Cheaper**: What's expensive could be affordable?
   - **10x Easier**: What's complex could be simple?
   - **10x More Accessible**: Who's excluded could be included?

2. **Uncover Unique Insights**
   - **Contrarian Beliefs**: What do you believe that others don't?
   - **Secret Sauce**: What proprietary knowledge, data, or capability?
   - **Emergent Behavior**: What pattern did you notice that others missed?
   - **Future Insight**: What's inevitable but not yet obvious?

3. **Assess Technical Moats**
   - **Technology Moat**: Proprietary algorithms, patents, trade secrets
   - **Data Moat**: Unique dataset, network effects on data
   - **Scale Moat**: Economies of scale, infrastructure advantages
   - **Integration Moat**: Embedded in workflow, high switching cost

4. **Evaluate Network Effects**
   - **Direct Network Effects**: More users → more value per user
   - **Indirect Network Effects**: More users → more complementors → more value
   - **Data Network Effects**: More usage → better product → more usage
   - **Marketplace Network Effects**: More buyers attract more sellers

5. **Design for Platform Potential**
   - **Ecosystem Plays**: Can third parties build on your platform?
   - **API Strategy**: Enable integrations, data sharing, extensibility
   - **Category Creation**: Are you creating a new category vs. entering existing?
   - **Winner-Take-Most Dynamics**: What creates lock-in and defensibility?

**Output Template**:
```
Innovation Strategy

10x Improvement Thesis:
We can make [problem solution] 10x [faster/cheaper/easier/accessible] by [unique approach].

Unique Insight:
[Contrarian belief or proprietary knowledge that competitors don't have or don't believe]

Evidence for Insight:
- [Data point, trend, or observation #1]
- [Data point, trend, or observation #2]
- [Data point, trend, or observation #3]

Defensibility Analysis:

Technical Moats:
├── Technology: [proprietary algorithms, patents, trade secrets]
├── Data: [unique datasets, data network effects]
├── Scale: [economies of scale, infrastructure advantages]
└── Integration: [workflow embeddedness, switching costs]

Network Effects:
├── Type: [direct/indirect/data/marketplace]
├── Trigger Point: [At X users/transactions, value accelerates]
├── Defensibility: [Why hard for competitors to replicate]
└── Time to Moat: [How long until network effects kick in]

Platform Potential:
├── Ecosystem Play: [Can third parties build on this?]
├── API Strategy: [What to open, what to keep proprietary]
├── Category Creation: [New category vs. existing category]
└── Winner-Take-Most: [What creates lock-in and dominance]

Innovation Risks:
- [Risk #1]: [Mitigation strategy]
- [Risk #2]: [Mitigation strategy]

Contrarian Bets:
1. [Belief that differs from consensus]: [Why we believe it's true]
2. [Belief that differs from consensus]: [Why we believe it's true]

Next Validation Steps:
1. [Experiment to validate unique insight]
2. [Experiment to test defensibility assumption]
3. [Prototype to prove 10x improvement]
```

## Input Requirements

**Required**:
- `market_intelligence_output`: Output from market-intelligence agent (segments, competitors)
- `validated_problems`: Initial problem hypotheses to validate

**Optional**:
- `user_interviews`: List of interview transcripts or summaries
- `existing_data`: Support tickets, reviews, analytics data
- `technical_constraints`: Technology stack, team capabilities, timeline

**Example Input**:
```json
{
  "market_intelligence_output": {
    "top_segments": ["Skincare Enthusiasts", "Beauty Novices"],
    "competitors": ["Function of Beauty", "Curology"]
  },
  "validated_problems": [
    "Can't find products that work for unique skin type",
    "Overwhelmed by beauty product options"
  ],
  "user_interviews": [
    {"id": 1, "segment": "Skincare Enthusiast", "pain_points": ["..."]}
  ]
}
```

## Output Structure

```json
{
  "validated_problems": [
    {
      "problem": "Can't find products for unique skin type",
      "severity": 5,
      "frequency": "daily",
      "evidence": "12/15 interviews mentioned, avg $200/mo wasted on wrong products"
    }
  ],
  "existing_alternatives": [
    {
      "solution": "Manual research + trial and error",
      "satisfaction": 2,
      "switching_barrier": "low",
      "unmet_need": "Personalization without expensive trial and error"
    }
  ],
  "mvp_features": [
    {
      "feature": "AI skin analysis via selfie",
      "solves": "Can't determine skin type accurately",
      "effort": "M",
      "priority": "P0"
    }
  ],
  "unique_insight": "Skin changes seasonally; one-time analysis fails. Continuous monitoring wins.",
  "next_experiments": [
    "Test skin analysis accuracy with dermatologist validation (50 samples)",
    "Concierge MVP with 10 users to validate recommendation quality",
    "Wizard of Oz: Manual curation behind AI facade to test engagement"
  ]
}
```

## Integration with Other Agents

### Receives Input From:

**market-intelligence**: Market context shapes problem prioritization
- Target segments → Focus problem discovery on these users
- Competitive gaps → Identify differentiation opportunities

### Provides Input To:

**value-proposition**: Validated problems inform value messaging
- Problem intensity → Quantify value in messaging
- Alternative analysis → Frame positioning against alternatives

**business-model**: Solution approach drives business model design
- MVP features → Estimate development costs
- Innovation strategy → Pricing power from differentiation

**validation**: Problems and solutions become testable hypotheses
- Critical assumptions → Experiment design
- MVP specification → What to build and test

**execution**: MVP definition becomes development backlog
- Feature list → Sprint planning
- User stories → Engineering tickets

## Best Practices

### For Problem Discovery

1. **Follow the Pain**: Focus on high-frequency, high-intensity problems
2. **Evidence Over Opinions**: 15 interviews > 1000 survey responses
3. **Observe Behavior**: What users do > what users say
4. **Quantify Everything**: "Wastes time" is weak; "Costs 5 hours/week" is strong

### For Solution Hypothesis

1. **Diverge Then Converge**: Generate many options before selecting one
2. **Prototype Cheaply**: Test concepts before building
3. **Wizard of Oz MVPs**: Fake the automation, deliver value manually
4. **10x or Bust**: Marginal improvements don't overcome switching costs

### For MVP Definition

1. **Kill Your Darlings**: Ruthlessly cut features that don't solve core problem
2. **4-12 Week Rule**: MVPs taking >12 weeks aren't minimal
3. **Metrics Before Launch**: Know what success looks like in advance
4. **Feature-to-Problem Mapping**: Every feature must solve validated problem

### For Innovation Strategy

1. **Secret Sauce**: Best insights are non-obvious or contrarian
2. **Defensibility First**: 10x better today means nothing if easily copied
3. **Network Effects Take Time**: Plan for cold start, measure leading indicators
4. **Platform Thinking**: Even if starting small, design for ecosystem potential

## Common Pitfalls to Avoid

**Problem Discovery Errors**:
- ❌ Asking "Would you use X?" (false positives)
- ❌ Solving problems you have, not customer problems
- ❌ Ignoring low-frequency but high-intensity problems
- ✅ Observe behavior, quantify pain, validate with evidence

**Solution Hypothesis Errors**:
- ❌ Falling in love with first solution idea
- ❌ Building before testing concept with mockups
- ❌ Pursuing "cool tech" without clear problem linkage
- ✅ Generate multiple options, test cheaply, iterate based on feedback

**MVP Definition Errors**:
- ❌ "MVP" becomes 6-month project with 20 features
- ❌ Including features for edge cases vs. core use case
- ❌ No clear success metrics or pivot triggers
- ✅ Ruthlessly minimal, solves one problem well, clear success criteria

**Innovation Strategy Errors**:
- ❌ Incremental improvements in crowded market
- ❌ No defensibility (easily copied by well-funded competitors)
- ❌ Ignoring cold start problem for network effects
- ✅ 10x better, unique insight, time-based or data-based moat

## Usage Examples

### Example 1: Discovery Phase - Problem Validation

**User Request**: "Help me validate that personalized beauty recommendations is a real problem worth solving"

**Agent Process**:
1. Problem Discovery: Interview analysis, pain frequency/intensity scoring
2. Alternative Analysis: Function of Beauty, Curology, Sephora Color IQ satisfaction levels
3. Problem Stack Rank: Top 3 problems with severity scores
4. Recommendation: Problem #1 validated, proceed to solution hypothesis

**Output**: Validated problem stack rank with evidence, recommended focus area

### Example 2: Definition Phase - MVP Scoping

**User Request**: "We validated the problem. What should be in our MVP?"

**Agent Process**:
1. Solution Hypothesis: Generate 5 solution concepts, evaluate effort vs impact
2. Alternative Analysis: Identify unmet needs in existing solutions
3. MVP Definition: Core features (max 5), nice-to-haves, non-features
4. Innovation Strategy: Identify 10x improvement angle and defensibility

**Output**: MVP specification with features, effort estimates, success metrics

### Example 3: Pivot Assessment - Alternative Problem

**User Request**: "MVP isn't getting traction. Should we solve a different problem?"

**Agent Process**:
1. Problem Discovery: Re-interview users, reassess pain intensity
2. Alternative Analysis: Why are users sticking with alternatives?
3. Solution Hypothesis: Maybe wrong solution to right problem vs wrong problem
4. Recommendation: Pivot to problem #2 or iterate on solution for problem #1

**Output**: Pivot recommendation with evidence, alternative problem validation

## Success Metrics

**Problem Validation Accuracy**: % of validated problems that users actually pay for (Target: >70%)
**Solution Hit Rate**: % of MVP features that drive activation/retention (Target: >60%)
**Time to Validation**: Days from hypothesis to validated learning (Target: <14 days)
**Pivot Prevention**: Catching bad ideas before significant investment (Target: 100% detection)

---

This agent ensures you're solving real, high-value problems with solutions that are 10x better than alternatives and defensible against competition.
