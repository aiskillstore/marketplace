---
name: reasoning-inductive
description: Extract patterns and generalizations from multiple observations. Use when detecting recurring themes, building predictive rules, or identifying systemic behaviors from accumulated data. Produces validated patterns with confidence bounds and exception handling.
---

# Inductive Reasoning

Generalize from instances to rules. The logic of pattern extraction and empirical learning.

## Type Signature

```
Inductive : [Observation] → Pattern → Generalization → ConfidenceBounds

Where:
  Observations     : [Instance] → Dataset
  Pattern          : Dataset → (Regularity × Frequency)
  Generalization   : (Regularity × Frequency) → Rule
  ConfidenceBounds : Rule × SampleSize → (Confidence × Exceptions)
```

## When to Use

**Use inductive when:**
- Multiple similar observations accumulate
- Looking for recurring patterns across threads
- Building predictive rules from experience
- Identifying systemic behaviors
- Validating or discovering Canvas assumptions
- "This keeps happening" situations

**Don't use when:**
- Explaining single observation → Use Abductive
- Known causal chain exists → Use Causal
- Transferring one case to another → Use Analogical
- Resolving disagreement → Use Dialectical

## Distinction from Other Modes

| Mode | Input | Output | Question |
|------|-------|--------|----------|
| **Abductive** | Single anomaly | Explanation | "Why did this happen?" |
| **Inductive** | Multiple instances | Pattern/Rule | "What keeps happening?" |
| **Analogical** | One source case | Transferred solution | "How is this like that?" |

**Key difference from Abductive:**
- Abductive: 1 observation → 1 explanation
- Inductive: N observations → 1 generalization

## Four-Stage Process

### Stage 1: Observation Collection

**Purpose:** Gather and structure multiple instances for analysis.

**Minimum Sample Requirements:**

| Confidence Target | Minimum N | Notes |
|-------------------|-----------|-------|
| Exploratory | 3-5 | Hypothesis generation only |
| Tentative | 6-10 | Directional confidence |
| Moderate | 11-20 | Actionable patterns |
| High | 21+ | Strong generalizations |

**Components:**
```yaml
observations:
  dataset:
    - instance_id: "deal-001"
      timestamp: ISO8601
      context: "Enterprise sales"
      attributes:
        deal_size: 400000
        sales_cycle: 120
        stalled_at: "legal_review"
        outcome: "won"
        
    - instance_id: "deal-002"
      timestamp: ISO8601
      context: "Enterprise sales"
      attributes:
        deal_size: 350000
        sales_cycle: 150
        stalled_at: "legal_review"
        outcome: "lost"
        
    # ... more instances
    
  metadata:
    total_instances: 12
    time_range: "Q3-Q4 2024"
    source: "threads/sales/*/6-learning.md"
    collection_method: "automated scan"
    
  quality:
    completeness: 0.92  # % of fields populated
    consistency: 0.88   # % following same schema
    recency: 0.75       # Weight toward recent
```

### Stage 2: Pattern Detection

**Purpose:** Identify regularities in the dataset.

**Pattern Types:**

| Type | Description | Example |
|------|-------------|---------|
| **Frequency** | How often X occurs | "7/12 deals stall at legal" |
| **Correlation** | X and Y co-occur | "Large deals AND long cycles" |
| **Sequence** | X follows Y | "Stall → lose within 30 days" |
| **Cluster** | Groups emerge | "Two deal archetypes exist" |
| **Trend** | Direction over time | "Cycles getting longer" |
| **Threshold** | Breakpoint exists | "Deals >$300K behave differently" |

**Detection Process:**
```yaml
patterns:
  detected:
    - pattern_id: P1
      type: frequency
      description: "Legal review stalls"
      evidence: "7 of 12 deals (58%) stalled at legal review"
      strength: 0.78
      
    - pattern_id: P2
      type: correlation
      description: "Deal size correlates with cycle length"
      evidence: "r=0.72 between deal_size and sales_cycle"
      strength: 0.72
      
    - pattern_id: P3
      type: threshold
      description: "CFO involvement threshold"
      evidence: "Deals >$250K require CFO, adding 30+ days"
      strength: 0.85
      
    - pattern_id: P4
      type: sequence
      description: "Stall duration predicts outcome"
      evidence: "Stalls >21 days → 80% loss rate"
      strength: 0.80
      
  rejected:
    - pattern: "Industry affects outcome"
      reason: "No significant difference across industries (p>0.3)"
      
  insufficient_data:
    - pattern: "Seasonality effects"
      reason: "Only 2 quarters of data, need 4+ for seasonality"
```

### Stage 3: Generalization

**Purpose:** Form rules from validated patterns.

**Rule Formation:**
```yaml
generalizations:
  rules:
    - rule_id: R1
      statement: "Enterprise deals >$250K require CFO approval, adding 30+ days to cycle"
      derived_from: [P2, P3]
      
      structure:
        condition: "deal_size > 250000"
        prediction: "sales_cycle += 30 days"
        mechanism: "CFO approval requirement"
        
      applicability:
        domain: "Enterprise sales"
        segments: ["all enterprise"]
        exceptions: ["existing customers with MSA"]
        
    - rule_id: R2
      statement: "Legal review stalls >21 days predict deal loss with 80% probability"
      derived_from: [P1, P4]
      
      structure:
        condition: "stall_duration > 21 AND stall_stage = 'legal'"
        prediction: "outcome = 'lost' (p=0.80)"
        mechanism: "Budget cycle expiration, champion fatigue"
        
      applicability:
        domain: "Enterprise sales"
        segments: ["new customers"]
        exceptions: ["government deals with known long cycles"]
        
    - rule_id: R3
      statement: "58% of enterprise deals will stall at legal review"
      derived_from: [P1]
      
      structure:
        condition: "enterprise deal"
        prediction: "P(legal_stall) = 0.58"
        mechanism: "Custom contract requirements"
        
      applicability:
        domain: "Enterprise sales"
        segments: ["all"]
        exceptions: ["standard contract accepted"]
```

### Stage 4: Confidence Bounds

**Purpose:** Quantify reliability and identify exceptions.

**Confidence Calculation:**
```
Confidence = f(sample_size, pattern_strength, consistency, recency)

Base confidence from sample size:
  N < 5:   max 0.40
  N 5-10:  max 0.60
  N 11-20: max 0.80
  N > 20:  max 0.95

Adjustments:
  × pattern_strength (0-1)
  × consistency (0-1)
  × recency_weight (0.5-1.0)
```

**Components:**
```yaml
confidence_analysis:
  rules:
    - rule_id: R1
      confidence: 0.72
      calculation:
        base: 0.80        # N=12, moderate sample
        strength: 0.85    # Strong pattern
        consistency: 0.88 # Good data quality
        recency: 0.95     # Recent data
        final: 0.72       # base × min(strength, consistency, recency)
        
      bounds:
        lower: 0.58       # Pessimistic estimate
        upper: 0.82       # Optimistic estimate
        
      exceptions:
        identified:
          - "Existing customer deal closed in 45 days despite $400K size"
            explanation: "Pre-existing MSA eliminated legal review"
          - "Government deal took 180 days but won"
            explanation: "Known government procurement cycle"
        exception_rate: 0.17  # 2/12 instances
        
      validity:
        expires: "2025-06-01"  # Re-validate after 6 months
        invalidated_by: 
          - "Process change eliminating legal review"
          - "New contract template adoption"
        strengthened_by:
          - "3+ more instances following pattern"
          - "Causal mechanism confirmed"
          
    - rule_id: R2
      confidence: 0.68
      # ... similar structure
```

**Output Summary:**
```yaml
inductive_output:
  summary:
    rules_generated: 3
    highest_confidence: R1 (0.72)
    total_observations: 12
    time_range: "Q3-Q4 2024"
    
  actionable_rules:
    - rule: R1
      action: "Add 30 days to forecast for deals >$250K"
      confidence: 0.72
      
    - rule: R2
      action: "Escalate intervention when legal stall exceeds 14 days"
      confidence: 0.68
      
  tentative_rules:
    - rule: R3
      action: "Plan for legal stall in 60% of deals (resource accordingly)"
      confidence: 0.55
      needs: "5+ more observations to reach actionable confidence"
      
  canvas_implications:
    validate:
      - assumption: "A4: Enterprise sales cycle is 90 days"
        finding: "Actually 120 days for deals >$250K"
        action: "Update assumption"
        
    new_hypothesis:
      - "H17: Standard contract template would reduce legal stalls by 50%"
        basis: "Legal stall is primary cycle driver"
        test: "Pilot standard contract with 5 deals"
```

## Quality Gates

| Gate | Requirement | Failure Action |
|------|-------------|----------------|
| Sample size | ≥5 instances | Collect more data |
| Data quality | ≥80% completeness | Clean dataset |
| Pattern strength | ≥0.6 for at least one | Lower threshold or collect more |
| Exception rate | <30% for actionable rules | Narrow rule scope |
| Mechanism identified | Plausible explanation | Add abductive analysis |

## Common Failure Modes

| Failure | Symptom | Fix |
|---------|---------|-----|
| **Small N** | High variance, unstable patterns | Wait for more data |
| **Survivorship bias** | Only successful cases analyzed | Include failures |
| **Confounding** | Correlation ≠ causation | Test mechanism with intervention |
| **Overfitting** | Rule too specific to sample | Simplify rule, test holdout |
| **Recency bias** | Old patterns weighted equally | Apply recency weighting |
| **Cherry-picking** | Only confirming instances | Systematic collection |

## Pattern Validation

Before promoting rule to actionable:

### Statistical Validation
```yaml
validation:
  method: "holdout"
  training_set: 8 instances
  test_set: 4 instances
  rule_accuracy_on_test: 0.75
  passed: true
```

### Causal Validation
```yaml
validation:
  method: "mechanism_test"
  proposed_mechanism: "CFO approval adds 30 days"
  test: "Interview 3 CFOs about approval process"
  result: "Confirmed - CFO review averages 25-35 days"
  passed: true
```

### Temporal Validation
```yaml
validation:
  method: "stability_check"
  pattern_in_Q3: 0.62
  pattern_in_Q4: 0.54
  drift: -0.08 (acceptable)
  passed: true
```

## Automated Pattern Detection

For continuous learning, run inductive scans:

```yaml
automated_scan:
  frequency: weekly
  sources:
    - "threads/sales/*/6-learning.md"
    - "threads/marketing/*/6-learning.md"
    - "threads/operations/*/6-learning.md"
    
  thresholds:
    min_instances: 5
    min_pattern_strength: 0.6
    
  output:
    location: "ops/patterns.md"
    alert_threshold: 0.75  # Flag high-confidence new patterns
    
  actions:
    new_pattern_detected: "Flag in ops/today.md for review"
    existing_pattern_strengthened: "Update confidence, log"
    pattern_invalidated: "Alert, review rule"
```

## Output Contract

```yaml
inductive_output:
  observations:
    count: int
    time_range: string
    sources: [string]
    quality_score: float
    
  patterns:
    detected: [{
      pattern_id: string
      type: frequency | correlation | sequence | cluster | trend | threshold
      description: string
      strength: float
      evidence: string
    }]
    rejected: [{pattern: string, reason: string}]
    
  rules:
    - rule_id: string
      statement: string
      confidence: float
      bounds: {lower: float, upper: float}
      exceptions: [{instance: string, explanation: string}]
      applicability: {domain: string, segments: [string], exceptions: [string]}
      validity: {expires: date, invalidated_by: [string]}
      
  canvas_implications:
    validate: [{assumption: string, finding: string, action: string}]
    invalidate: [{assumption: string, finding: string, action: string}]
    new_hypotheses: [{hypothesis: string, basis: string, test: string}]
    
  actions:
    immediate: [string]        # High-confidence rules to act on
    monitor: [string]          # Tentative patterns to watch
    collect: [string]          # Data gaps to fill
    
  next:
    suggested_mode: ReasoningMode
    threads_to_create: [string]
    
  trace:
    patterns_evaluated: int
    rules_generated: int
    duration_ms: int
```

## Example Execution

**Context:** "Review last 6 months of marketing content performance"

**Stage 1 - Observations:**
```
Collected: 24 content pieces
Sources: threads/marketing/*/6-learning.md
Attributes: topic, format, channel, sessions, conversions, time_to_demo
Quality: 0.88 completeness
```

**Stage 2 - Patterns:**
```
P1 (frequency): Case studies convert 2.3x average (8/24, all above average)
P2 (correlation): Technical depth correlates with enterprise demos (r=0.68)
P3 (threshold): Posts >2000 words perform better on SEO (breakpoint identified)
P4 (trend): LinkedIn declining, organic search rising over 6 months
```

**Stage 3 - Generalizations:**
```
R1: "Case studies should be prioritized for bottom-funnel conversion"
    Confidence: 0.75, based on 8 instances

R2: "Technical content attracts enterprise prospects"
    Confidence: 0.68, based on correlation analysis

R3: "SEO content should target >2000 words"
    Confidence: 0.70, based on threshold analysis
```

**Stage 4 - Confidence Bounds:**
```
R1: 0.75 [0.62, 0.85] - Actionable
R2: 0.68 [0.54, 0.78] - Actionable with caution
R3: 0.70 [0.58, 0.80] - Actionable

Canvas update: 
  - Validate H8 (case studies convert)
  - New H18: "Long-form SEO content drives organic growth"
  
Action: Shift content mix toward case studies and long-form technical guides
```
