---
name: reasoning-counterfactual
description: Evaluate alternative scenarios by simulating interventions on past decisions or hypothetical futures. Use when assessing decisions in hindsight, planning scenarios, or comparing paths not taken. Produces comparative analysis with probability-weighted outcomes.
---

# Counterfactual Reasoning

Simulate alternative realities. The logic of "what if" and decision evaluation.

## Type Signature

```
Counterfactual : Actual → Intervention → Alternative → Comparison

Where:
  Actual       : Decision × Outcome → ActualWorld
  Intervention : ActualWorld × Δ → ModifiedPremise
  Alternative  : ModifiedPremise → ProjectedOutcome
  Comparison   : (ActualWorld, ProjectedOutcome) → DifferenceAnalysis
```

## When to Use

**Use counterfactual when:**
- Evaluating past decisions ("Should we have...")
- Scenario planning ("What if X happens...")
- Comparing options not taken ("If we had chosen...")
- Strategic simulation ("If competitor does X...")
- Learning from outcomes ("Was our decision right?")

**Don't use when:**
- Executing known process → Use Causal
- Explaining observation → Use Abductive
- Resolving disagreement → Use Dialectical

## Core Principles

### Minimal Intervention

Change only what's necessary to test the hypothesis:
- Modify one variable at a time where possible
- Keep everything else constant (ceteris paribus)
- Trace downstream effects carefully

### Probability Weighting

Alternative outcomes aren't certain:
- Assign probability to each projected outcome
- Consider multiple possible alternatives per intervention
- Avoid overconfidence in projections

### Asymmetry Awareness

Counterfactual analysis has inherent biases:
- Hindsight makes alternatives seem clearer
- Survivors don't see paths that led to failure
- Confidence in projections often too high

## Four-Stage Process

### Stage 1: Actual World

**Purpose:** Document the decision made and observed outcome.

**Components:**
```yaml
actual:
  decision:
    what: "The choice that was made"
    when: ISO8601
    who: "Decision maker(s)"
    context: "Circumstances at decision time"
    alternatives_considered: [string]  # At the time
    
  outcome:
    result: "What actually happened"
    metrics:
      - metric: "Measurable outcome"
        value: number
        expected: number  # What was predicted
    timeline: "How long to outcome"
    
  assessment:
    success_level: high | medium | low | failed
    surprise_level: 0.0-1.0  # How unexpected
    
  causal_chain:
    - step: "Decision led to X"
    - step: "X led to Y"
    - step: "Y produced outcome"
```

**Example:**
```yaml
actual:
  decision:
    what: "Priced enterprise tier at $50K/year"
    when: "2024-06-01"
    who: "Founders"
    context: "First enterprise launch, no market data"
    alternatives_considered:
      - "$30K/year (lower barrier)"
      - "$75K/year (higher margin)"
      - "Usage-based pricing"
      
  outcome:
    result: "Closed 3 deals in 6 months, $150K ARR"
    metrics:
      - metric: "Deals closed"
        value: 3
        expected: 5
      - metric: "ARR"
        value: 150000
        expected: 250000
      - metric: "Sales cycle"
        value: 120  # days
        expected: 90
    timeline: "6 months"
    
  assessment:
    success_level: medium
    surprise_level: 0.4  # Somewhat below expectations
    
  causal_chain:
    - step: "$50K price point set"
    - step: "3/5 prospects required CFO approval at this level"
    - step: "CFO approval added 30 days to cycle"
    - step: "2 deals lost to budget cycle timing"
```

### Stage 2: Intervention

**Purpose:** Define the alternative decision to evaluate.

**Intervention Types:**

| Type | Description | Example |
|------|-------------|---------|
| **Price** | Different pricing decision | "$30K instead of $50K" |
| **Timing** | Earlier or later action | "Launched 3 months earlier" |
| **Strategy** | Different strategic choice | "SMB-first instead of enterprise" |
| **Resource** | Different allocation | "Hired sales earlier" |
| **Partner** | Different relationship | "Partnered with X instead of Y" |

**Components:**
```yaml
intervention:
  what: "The alternative choice"
  
  change:
    variable: "What's being changed"
    from: "Actual value"
    to: "Alternative value"
    
  rationale:
    why_consider: "Why this alternative is worth evaluating"
    was_available: bool  # Was this actually an option at the time?
    
  assumptions:
    held_constant:
      - "What we assume stays the same"
    ripple_effects:
      - "Expected downstream changes"
```

**Example:**
```yaml
intervention:
  what: "Price at $30K/year instead of $50K"
  
  change:
    variable: "Enterprise tier annual price"
    from: "$50,000"
    to: "$30,000"
    
  rationale:
    why_consider: "Test if lower price would have increased velocity"
    was_available: true  # This was considered at the time
    
  assumptions:
    held_constant:
      - "Same product features"
      - "Same sales team"
      - "Same market conditions"
      - "Same target customer profile"
    ripple_effects:
      - "Different approval threshold (manager vs CFO)"
      - "Potentially different customer expectations"
      - "Lower margin per deal"
```

### Stage 3: Alternative Projection

**Purpose:** Project what would have happened under the intervention.

**Projection Method:**

1. **Identify decision point** - Where paths diverge
2. **Trace causal chain** - What changes downstream?
3. **Estimate outcomes** - With probability weights
4. **Consider multiple scenarios** - Best/worst/expected

**Components:**
```yaml
alternative:
  scenarios:
    - name: "Expected case"
      probability: 0.6
      outcome:
        deals: 6  # vs actual 3
        arr: 180000  # vs actual 150000
        cycle: 75  # days, vs actual 120
      reasoning: "Lower price = faster approval, more deals, but lower $ each"
      
    - name: "Optimistic case"
      probability: 0.25
      outcome:
        deals: 8
        arr: 240000
        cycle: 60
      reasoning: "Volume effect stronger than expected"
      
    - name: "Pessimistic case"
      probability: 0.15
      outcome:
        deals: 4
        arr: 120000
        cycle: 90
      reasoning: "Lower price signals lower value, some prospects hesitate"
      
  weighted_outcome:
    deals: 6.0  # (6×0.6 + 8×0.25 + 4×0.15)
    arr: 178000
    cycle: 74
    
  causal_reasoning:
    - "At $30K, most prospects can approve at director level"
    - "Director approval takes ~45 days vs CFO 90+ days"
    - "Faster cycle = more deals in same period"
    - "But: lower price per deal = lower total ARR per deal"
    
  confidence: 0.65  # How confident in this projection
  
  key_uncertainties:
    - "Would lower price attract different (worse?) customers?"
    - "Would sales team close at same rate at lower price?"
    - "Would competitors have responded differently?"
```

### Stage 4: Comparison

**Purpose:** Compare actual vs alternative, extract insights.

**Components:**
```yaml
comparison:
  quantitative:
    - metric: "Deals"
      actual: 3
      alternative: 6.0
      difference: "+3 (100%)"
      direction: better
      
    - metric: "ARR"
      actual: 150000
      alternative: 178000
      difference: "+$28K (19%)"
      direction: better
      
    - metric: "Sales cycle"
      actual: 120
      alternative: 74
      difference: "-46 days (38%)"
      direction: better
      
    - metric: "ARR per deal"
      actual: 50000
      alternative: 29667
      difference: "-$20K (41%)"
      direction: worse
      
  qualitative:
    better_in_alternative:
      - "Faster sales velocity"
      - "Lower customer acquisition cost"
      - "More reference customers faster"
      
    worse_in_alternative:
      - "Lower margin per customer"
      - "Potentially lower perceived value"
      - "Less room for discounting"
      
  verdict:
    assessment: "Alternative likely better overall"
    confidence: 0.65
    caveat: "Lower price creates different customer dynamics long-term"
    
  insight:
    learning: "At this stage, velocity matters more than margin"
    applies_to: "Early enterprise sales with unproven product"
    recommendation: "Consider price reduction or tier restructuring"
    
  action_implication:
    retrospective: "Pricing decision was suboptimal but not catastrophic"
    prospective: "For next segment, start lower and raise after validation"
```

## Quality Gates

| Gate | Requirement | Failure Action |
|------|-------------|----------------|
| Actual documented | Outcome with metrics | Gather actual data |
| Intervention minimal | Single variable change | Simplify intervention |
| Scenarios weighted | Probabilities sum to 1.0 | Adjust probabilities |
| Confidence bounded | State uncertainty explicitly | Add confidence intervals |
| Insight actionable | Clear learning for future | Extract practical lesson |

## Intervention Validity

Not all counterfactuals are useful:

**Valid interventions:**
- Was actually an option at the time
- Changes something controllable
- Has traceable downstream effects
- Provides actionable insight

**Invalid interventions:**
- "What if we had known X" (not available info)
- "What if competitor hadn't existed" (not controllable)
- "What if market was bigger" (not a decision)

## Common Failure Modes

| Failure | Symptom | Fix |
|---------|---------|-----|
| **Hindsight bias** | Alternative seems obviously better | Account for what was knowable at decision time |
| **Single scenario** | Only one alternative considered | Generate multiple scenarios with probabilities |
| **Overconfidence** | High certainty in projections | Widen confidence intervals |
| **Untraceable** | Can't explain why alternative differs | Build explicit causal chain |
| **Fantasy** | Intervention wasn't actually available | Verify intervention was feasible |

## Multiple Interventions

For complex decisions, evaluate multiple alternatives:

```yaml
interventions:
  - name: "Lower price ($30K)"
    outcome: {arr: 178000, deals: 6}
    
  - name: "Higher price ($75K)"
    outcome: {arr: 150000, deals: 2}
    
  - name: "Usage-based pricing"
    outcome: {arr: 200000, deals: 4}
    confidence: 0.5  # Higher uncertainty
    
comparison_matrix:
  best_arr: "Usage-based"
  best_velocity: "Lower price"
  best_margin: "Higher price"
  best_overall: "Lower price (velocity matters most at this stage)"
```

## Output Contract

```yaml
counterfactual_output:
  actual:
    decision: string
    outcome: {result: string, metrics: [Metric]}
    success_level: string
    
  intervention:
    what: string
    change: {variable: string, from: any, to: any}
    was_available: bool
    
  alternative:
    scenarios: [Scenario]
    weighted_outcome: {metric: value}
    confidence: float
    
  comparison:
    quantitative: [{metric: string, actual: any, alternative: any, direction: string}]
    verdict: string
    confidence: float
    
  insight:
    learning: string
    applies_to: string
    recommendation: string
    
  action:
    retrospective: string  # What does this mean for past decision
    prospective: string    # What does this mean for future decisions
    
  next:
    suggested_mode: ReasoningMode  # Usually causal
    canvas_updates: [string]
    experiments_to_run: [string]
    
  trace:
    interventions_evaluated: int
    confidence_average: float
    duration_ms: int
```

## Example Execution

**Context:** "Should we have taken the Series A when offered 18 months ago?"

**Stage 1 - Actual:**
```
Decision: Declined $5M Series A at $20M valuation
Outcome: Bootstrapped to $600K ARR, now raising at $30M valuation
Success level: Medium-high (slower growth, higher ownership)
```

**Stage 2 - Intervention:**
```
What: Accepted $5M Series A
Change: Funding status from bootstrapped to funded
Was available: Yes, term sheet was on the table
```

**Stage 3 - Alternative:**
```
Scenarios:
  - Expected (60%): $1.5M ARR now, but 25% dilution
  - Optimistic (25%): $2M ARR, enterprise sales team
  - Pessimistic (15%): $800K ARR, burned capital on wrong bets

Weighted: $1.4M ARR, 75% ownership vs current $600K ARR, 100% ownership
```

**Stage 4 - Comparison:**
```
ARR: Alternative 133% higher
Ownership value: Alternative $31.5M (75% × $42M) vs Actual $30M (100% × $30M)
Net: Roughly equivalent in value, different risk profiles

Verdict: Decision was reasonable given risk tolerance
Insight: Bootstrapping is viable if willing to accept slower growth
Recommendation: Current path validated, continue unless growth accelerates
```
