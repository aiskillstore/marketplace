---
name: reasoning-dialectical
description: Synthesize competing positions through structured thesis-antithesis-synthesis process. Use when stakeholders disagree, trade-offs exist, or multiple valid perspectives need integration. Produces integrated positions with acknowledged trade-offs.
---

# Dialectical Reasoning

Synthesize opposing views into higher-order resolution. The logic of productive disagreement.

## Type Signature

```
Dialectical : Thesis → Antithesis → Synthesis

Where:
  Thesis     : Position × Evidence × Stakeholder → ArgumentA
  Antithesis : ArgumentA → CounterPosition × Evidence × Stakeholder → ArgumentB
  Synthesis  : (ArgumentA, ArgumentB) → IntegratedPosition × Tradeoffs
```

## When to Use

**Use dialectical when:**
- Stakeholders hold opposing valid positions
- Trade-offs need explicit analysis
- Strategic tension requires resolution
- Multiple perspectives each have merit
- "On one hand... on the other" situations

**Don't use when:**
- Cause-effect chain needed → Use Causal
- Explaining observation → Use Abductive
- Evaluating past decisions → Use Counterfactual

## Core Principles

### Charitable Interpretation

Each position must be represented at its strongest:
- Steel-man, don't straw-man
- Assume good faith and valid reasoning
- Identify the kernel of truth in each view

### Genuine Synthesis

Synthesis is NOT:
- Compromise (splitting the difference)
- Victory (one side wins)
- Avoidance (postpone decision)

Synthesis IS:
- Integration at higher level of abstraction
- Resolution that addresses underlying concerns
- New position that transcends original framing

## Three-Stage Process

### Stage 1: Thesis

**Purpose:** Articulate first position at maximum strength.

**Components:**
```yaml
thesis:
  position: 
    statement: "Core claim being made"
    underlying_concern: "What this position is really about"
    
  stakeholder:
    who: "Person/team holding this view"
    role: "Their organizational function"
    incentives: "What they optimize for"
    
  evidence:
    supporting:
      - claim: "Evidence point"
        source: "Where this comes from"
        strength: 0.0-1.0
    empirical: [DataPoint]
    logical: [Argument]
    
  implications:
    if_adopted: "What happens if we go this way"
    risks: [Risk]
    benefits: [Benefit]
```

**Example:**
```yaml
thesis:
  position:
    statement: "We should prioritize enterprise features over SMB growth"
    underlying_concern: "Revenue concentration and deal size efficiency"
    
  stakeholder:
    who: "Sales leadership"
    role: "Revenue generation"
    incentives: "ARR, deal size, quota attainment"
    
  evidence:
    supporting:
      - claim: "Enterprise deals average $400K vs SMB $5K"
        source: "Q3 sales data"
        strength: 0.95
      - claim: "Sales cost per $ revenue 5x lower for enterprise"
        source: "CAC analysis"
        strength: 0.85
    empirical:
      - "3 enterprise deals = entire SMB revenue"
      - "Enterprise churn 3% vs SMB 8%"
      
  implications:
    if_adopted: "Focus engineering on enterprise features, reduce SMB investment"
    risks: 
      - "Lose SMB market to competitors"
      - "Revenue concentration risk"
    benefits:
      - "Higher margins"
      - "Larger average deal"
```

### Stage 2: Antithesis

**Purpose:** Articulate counter-position at maximum strength.

**Process:**
1. Identify what thesis misses or undervalues
2. Find stakeholder with opposing view
3. Build strongest case for alternative
4. Identify where thesis assumptions break

**Components:**
```yaml
antithesis:
  position:
    statement: "Counter claim"
    underlying_concern: "What this position is really about"
    
  stakeholder:
    who: "Person/team holding this view"
    role: "Their organizational function"
    incentives: "What they optimize for"
    
  critique_of_thesis:
    - assumption_challenged: "Thesis assumes X"
      counter_evidence: "But actually Y"
    - risk_identified: "Thesis ignores Z"
      
  evidence:
    supporting: [EvidencePoint]
    empirical: [DataPoint]
    logical: [Argument]
    
  implications:
    if_adopted: "What happens if we go this way"
    risks: [Risk]
    benefits: [Benefit]
```

**Example:**
```yaml
antithesis:
  position:
    statement: "SMB volume creates the foundation for sustainable growth"
    underlying_concern: "Market presence, product iteration, and risk distribution"
    
  stakeholder:
    who: "Product leadership"
    role: "Product-market fit and growth"
    incentives: "Usage, retention, feature validation"
    
  critique_of_thesis:
    - assumption_challenged: "Enterprise features drive growth"
      counter_evidence: "SMB usage generates product insights 10x faster"
    - assumption_challenged: "Revenue concentration is acceptable"
      counter_evidence: "Losing 1 enterprise deal = losing 80 SMB accounts"
    - risk_identified: "Enterprise sales cycle is 9 months"
      
  evidence:
    supporting:
      - claim: "SMB accounts generate 80% of feature requests"
        source: "Product feedback analysis"
        strength: 0.90
      - claim: "SMB provides faster iteration cycles"
        source: "Release metrics"
        strength: 0.85
    empirical:
      - "SMB churn prediction accuracy 95% vs enterprise 60%"
      - "Product improvements from SMB feedback shipped in 2 weeks"
      
  implications:
    if_adopted: "Maintain SMB investment, use as product lab"
    risks:
      - "Slower revenue growth short-term"
      - "Lower margin overall"
    benefits:
      - "Diversified revenue base"
      - "Faster product iteration"
      - "Lower concentration risk"
```

### Stage 3: Synthesis

**Purpose:** Integrate positions at higher level, resolving underlying tensions.

**Synthesis Approaches:**

| Approach | When to Use | Example |
|----------|-------------|---------|
| **Integration** | Both positions address valid concerns | "Enterprise revenue + SMB as product lab" |
| **Sequencing** | Temporal resolution possible | "SMB first for PMF, then enterprise scale" |
| **Segmentation** | Different contexts warrant different approaches | "SMB for product X, Enterprise for product Y" |
| **Reframing** | Original dichotomy was false | "The real question isn't SMB vs Enterprise, it's time-to-value" |
| **Transcendence** | Higher goal subsumes both | "Optimize for sustainable unit economics regardless of segment" |

**Synthesis Components:**
```yaml
synthesis:
  integrated_position:
    statement: "What we will actually do"
    framing: "How this resolves the tension"
    
  how_thesis_is_addressed:
    concern_validated: "What's true about thesis"
    how_incorporated: "How we address that concern"
    
  how_antithesis_is_addressed:
    concern_validated: "What's true about antithesis"
    how_incorporated: "How we address that concern"
    
  trade_offs_acknowledged:
    - trade_off: "What we're giving up"
      mitigation: "How we reduce impact"
      accepted_by: "Stakeholder who accepts this"
      
  resolution_type: integration | sequencing | segmentation | reframing | transcendence
  
  implementation:
    actions: [Action]
    metrics: [Metric]  # How we know it's working
    review_date: date  # When we reassess
```

**Example:**
```yaml
synthesis:
  integrated_position:
    statement: "SMB as rapid learning engine, enterprise as revenue engine, 
                with explicit feature graduation path"
    framing: "Not SMB vs Enterprise, but learning velocity vs revenue efficiency 
              with a bridge between them"
              
  how_thesis_is_addressed:
    concern_validated: "Enterprise deals are more efficient per dollar"
    how_incorporated: "Maintain enterprise sales motion, prioritize enterprise 
                       features that have been validated through SMB"
                       
  how_antithesis_is_addressed:
    concern_validated: "SMB generates faster product learning"
    how_incorporated: "Protect SMB investment as product lab, use SMB metrics 
                       to prioritize enterprise features"
                       
  trade_offs_acknowledged:
    - trade_off: "Some enterprise-only features will ship slower"
      mitigation: "Identify 'must have' enterprise features, fast-track those"
      accepted_by: "Sales leadership (with fast-track list)"
      
    - trade_off: "Some SMB features won't graduate to enterprise"
      mitigation: "Clear graduation criteria defined upfront"
      accepted_by: "Product leadership (with criteria agreement)"
      
  resolution_type: integration
  
  implementation:
    actions:
      - "Define feature graduation criteria (Product + Sales)"
      - "Create SMB → Enterprise feature pipeline"
      - "Allocate 60% engineering to graduated features, 40% to SMB lab"
    metrics:
      - "SMB feature graduation rate (target: 3/month)"
      - "Enterprise close rate on graduated features (target: +20%)"
      - "Combined revenue growth (target: 30% QoQ)"
    review_date: "End of Q2"
```

## Quality Gates

| Gate | Requirement | Failure Action |
|------|-------------|----------------|
| Thesis strength | Steel-manned, evidence-backed | Strengthen before proceeding |
| Antithesis genuine | Not straw-man, different stakeholder | Find genuine opposition |
| Synthesis integrative | Not compromise or victory | Reframe until true synthesis |
| Trade-offs explicit | All parties acknowledge costs | Surface hidden disagreements |
| Actionable | Concrete next steps | Add implementation detail |

## Stakeholder Agreement Protocol

Synthesis isn't complete until affected stakeholders acknowledge:

1. **Their concern was understood** (thesis/antithesis accurately represented)
2. **The synthesis addresses their core interest** (not just their stated position)
3. **They accept the trade-offs** (explicitly, not assumed)

```yaml
stakeholder_acknowledgment:
  thesis_stakeholder:
    name: "Sales leadership"
    concern_understood: true
    synthesis_addresses_concern: true
    accepts_trade_offs: true
    conditions: "Fast-track list for critical enterprise features"
    
  antithesis_stakeholder:
    name: "Product leadership"
    concern_understood: true
    synthesis_addresses_concern: true
    accepts_trade_offs: true
    conditions: "Clear graduation criteria before implementation"
```

## Common Failure Modes

| Failure | Symptom | Fix |
|---------|---------|-----|
| **False dichotomy** | Positions aren't truly opposed | Reframe the actual tension |
| **Straw-man** | Weak representation of one side | Involve actual stakeholder |
| **Mushy middle** | Synthesis is just "do both" | Force resource allocation |
| **Unacknowledged loss** | Trade-offs hidden | Surface what's being given up |
| **No implementation** | Synthesis is abstract | Add concrete actions |

## Output Contract

```yaml
dialectical_output:
  thesis:
    position: string
    stakeholder: string
    evidence: [EvidencePoint]
    strength: float  # 0.0-1.0
    
  antithesis:
    position: string
    stakeholder: string
    evidence: [EvidencePoint]
    strength: float
    
  synthesis:
    position: string
    resolution_type: string
    confidence: float
    
  integration:
    thesis_addressed: string
    antithesis_addressed: string
    
  trade_offs:
    - trade_off: string
      mitigation: string
      accepted_by: string
      
  stakeholder_agreement:
    - stakeholder: string
      agrees: bool
      conditions: optional<string>
      
  implementation:
    actions: [string]
    metrics: [string]
    review_date: date
    
  next:
    suggested_mode: ReasoningMode  # Usually causal
    canvas_updates: [string]
    
  trace:
    duration_ms: int
    rounds_of_refinement: int
```

## Example Execution

**Context:** "Engineering wants to rebuild core platform (6 months). Sales wants new features for Q2 deals."

**Stage 1 - Thesis (Engineering):**
```
Position: "Technical debt is blocking velocity. Rebuild now or pay 10x later."
Evidence: 
  - Deploy time increased 300% YoY
  - 40% of sprint spent on workarounds
  - 3 critical bugs from architecture issues
Underlying concern: Sustainable development velocity
```

**Stage 2 - Antithesis (Sales):**
```
Position: "We have $2M in pipeline dependent on Q2 features. Delay = lose deals."
Evidence:
  - 5 enterprise deals waiting on specific features
  - Competitor launching similar features in March
  - Q2 quota at risk without new capabilities
Underlying concern: Revenue target attainment
```

**Stage 3 - Synthesis:**
```
Integrated position: "Strangler fig pattern - rebuild incrementally while 
                      delivering high-priority features"

How thesis addressed: Platform rebuild happens, but in modules alongside features
How antithesis addressed: Q2 features delivered, no delay

Trade-offs:
  - Rebuild takes 9 months instead of 6 (Engineering accepts)
  - Only top 3 features in Q2, not all 5 (Sales accepts with prioritization input)
  
Resolution type: Integration via sequencing

Implementation:
  - Week 1: Joint prioritization session (top 3 features + first rebuild module)
  - Q2: Deliver features on new modules where possible
  - Q3-Q4: Complete rebuild with feature delivery continuing
```
