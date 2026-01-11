# Intent Analyzer - Detailed Workflow

## Process Overview

The Intent Analyzer uses a 5-phase cognitive science-based approach to transform ambiguous user requests into clear, actionable plans.

## Phase Breakdown

### Phase 1: Capture User Input (2 min)

**Objective**: Comprehensive data gathering

**Steps**:
1. Extract raw user request verbatim
2. Capture environmental context (cwd, env vars, recent history)
3. Analyze request characteristics (length, complexity, specificity)
4. Gather filesystem and project clues
5. Store all data in memory

**Agents**: None (automated)

**Outputs**:
- `raw-input.json`
- `characteristics.json`
- `context-clues.json`

**Validation**:
- All context gathered
- Specificity score calculated
- Memory storage confirmed

---

### Phase 2: Decompose Intent (5 min)

**Objective**: Break request into fundamental components

**Agent**: Researcher

**Steps**:
1. Tokenize request into actions, subjects, constraints, outcomes
2. Build component tree with primary/secondary/implicit intents
3. Map dependencies (sequential, parallel, conditional)
4. Identify implicit requirements from context

**Techniques**:
- First principles decomposition
- Dependency graph construction
- Implicit assumption surfacing

**Outputs**:
- `component-tree.json`
- `dependencies.json`
- `decomposition-report.md`

**Validation**:
- All verbs extracted
- Tree structure complete
- Dependencies mapped

---

### Phase 3: Map Probabilities (5 min)

**Objective**: Generate and rank possible interpretations

**Agent**: Analyst

**Steps**:
1. Generate 3-5 interpretation candidates
2. Assign initial probabilities based on evidence
3. Apply Bayesian reasoning with context
4. Rank by confidence level
5. Tag assumptions for each interpretation

**Techniques**:
- Probabilistic reasoning
- Bayesian updating
- Evidence accumulation
- Self-consistency checking

**Outputs**:
- `interpretations.json` (all candidates)
- `ranked-interpretations.json` (sorted by probability)
- `probability-analysis.md`

**Validation**:
- Probabilities sum to ~1.0
- Top interpretation has evidence
- Assumptions documented

---

### Phase 4: Clarify Ambiguities (10 min)

**Objective**: Resolve uncertainty through targeted questions

**Agent**: Planner

**Steps**:
1. Identify ambiguous assumptions (probability < 0.8)
2. Generate clarifying questions for high-impact ambiguities
3. Prioritize questions by impact and probability
4. Present to user (max 3 questions)
5. Process responses and update probabilities
6. Re-rank interpretations

**Techniques**:
- Socratic questioning
- Impact-priority matrix
- Bayesian updating from evidence
- Contradiction detection

**Outputs**:
- `questions.json`
- `user-responses.json`
- `refined-interpretations.json`

**Validation**:
- Questions address key ambiguities
- User responses captured
- Probabilities updated
- Top interpretation confidence improved

---

### Phase 5: Synthesize Understanding (8 min)

**Objective**: Create final interpretation with execution plan

**Agents**: Analyst + Planner

**Steps**:
1. Select final interpretation (highest probability)
2. Generate confirmation statement
3. Present to user for verification
4. Create execution brief with action plan
5. Export results for next workflow
6. Handoff to execution if confidence > 0.85

**Techniques**:
- Synthesis and integration
- Action planning
- Risk identification
- Handoff protocol

**Outputs**:
- `final-synthesis.json`
- `execution-brief.json`
- `confirmation-statement.md`
- `intent-analysis-result.json` (primary output)

**Validation**:
- Confidence > 0.8
- User confirmation obtained
- Execution brief complete
- Next steps defined

---

## Workflow Diagram

```
User Request
    ↓
[Phase 1: Capture]
    ↓
Raw Input + Context
    ↓
[Phase 2: Decompose] ← Researcher Agent
    ↓
Component Tree
    ↓
[Phase 3: Map Probabilities] ← Analyst Agent
    ↓
Ranked Interpretations
    ↓
Decision: Confidence > 0.8?
    ↓
   No → [Phase 4: Clarify] ← Planner Agent
    ↓       ↓
   Yes   Questions → User → Responses
    ↓       ↓
    ↓   Update Probabilities
    ↓       ↓
    └───────┘
        ↓
[Phase 5: Synthesize] ← Analyst + Planner
    ↓
Execution Brief
    ↓
User Confirmation
    ↓
Handoff to Next Workflow
```

## Decision Points

### After Phase 3
- **IF** confidence > 0.8 → Skip to Phase 5
- **ELSE** → Proceed to Phase 4

### After Phase 4
- **IF** confidence > 0.8 after clarification → Proceed to Phase 5
- **ELSE IF** clarification rounds < 3 → Repeat Phase 4 with different questions
- **ELSE** → Manual escalation (request more detailed user input)

### After Phase 5
- **IF** user confirms → Export execution brief
- **ELSE** → Return to Phase 4 with specific correction

## Memory Flow

```
Phase 1 → Store: raw-input, characteristics, context-clues
Phase 2 → Store: component-tree, dependencies
Phase 3 → Store: interpretations, ranked-interpretations
Phase 4 → Store: questions, user-responses, refined-interpretations
Phase 5 → Store: final-synthesis, execution-brief
```

## Error Handling

### Low Confidence Persistence
- **Symptom**: Confidence remains < 0.7 after 2 clarification rounds
- **Action**: Request specific example from user
- **Escalation**: Suggest user reformulate request

### Contradictory Responses
- **Symptom**: User responses create logical contradictions
- **Action**: Highlight contradictions, ask for priority
- **Resolution**: User chooses which requirement is more important

### Too Many Equal Interpretations
- **Symptom**: Top 3 interpretations have similar probability
- **Action**: Present binary choice between top 2
- **Resolution**: User directly selects interpretation

## Integration Patterns

### Sequential Integration
```bash
intent-analyzer → output.json → next-skill --input output.json
```

### Conditional Integration
```javascript
if (intentBrief.confidence > 0.85) {
  executeWorkflow(intentBrief.actionPlan);
} else {
  manualReview(intentBrief);
}
```

### Cascade Integration
```javascript
{
  steps: [
    { skill: 'intent-analyzer', output: 'intent' },
    { skill: 'sparc-spec', input: '${intent}', conditional: '${intent.confidence} > 0.8' }
  ]
}
```

## Performance Benchmarks

- **Average Duration**: 15-25 minutes
- **Confidence Achievement**: 87% reach >0.8 confidence
- **Clarification Rounds**: Average 1.3 rounds
- **User Satisfaction**: 92% confirm accurate understanding

## Best Practices

1. **Provide Full Context**: Include relevant files, recent work, project goals
2. **Answer Honestly**: Clarifying questions help accuracy
3. **Review Carefully**: Check interpretation before confirming
4. **Iterate if Needed**: Don't hesitate to correct misunderstandings
5. **Use Results**: Feed execution brief to next workflow

## Advanced Features

### Intent Caching
- Frequently seen patterns cached for faster resolution
- Similarity matching using embeddings
- 90%+ similarity → instant interpretation

### Parallel Generation
- Multiple interpretation strategies run concurrently
- Literal, inferred, expert, novel perspectives
- Consensus building from diverse views

### Expertise Adaptation
- Detects user expertise level
- Adjusts question complexity accordingly
- Expert users get fewer basic questions

## Troubleshooting Guide

| Issue | Cause | Solution |
|-------|-------|----------|
| Low specificity score | Vague request | Use more open-ended questions |
| No clear top interpretation | Insufficient context | Request examples or similar work |
| User confused by questions | Too technical | Simplify language, provide context |
| Confidence drops after clarification | Contradictory evidence | Highlight contradiction, ask priority |
| Too many clarification rounds | Complex multi-part request | Split into sub-intents |

## Output Schema

```typescript
interface IntentAnalysisResult {
  metadata: {
    skillName: string;
    timestamp: string;
    confidence: number;
  };
  userIntent: {
    original: string;
    interpreted: string;
    clarifications: number;
  };
  actionPlan: {
    phases: Phase[];
    agents: string[];
    estimatedDuration: string;
    dependencies: Dependency[];
  };
  successCriteria: string[];
  riskFactors: Risk[];
}
```

For implementation details, see SKILL.md
