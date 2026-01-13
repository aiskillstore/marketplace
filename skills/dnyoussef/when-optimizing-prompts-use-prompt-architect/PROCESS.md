# Prompt Architect - Detailed Workflow

## Process Overview

Transform prompts using evidence-based prompt engineering through systematic analysis, optimization, and validation.

## Phase Breakdown

### Phase 1: Analyze Current Prompt (5 min)

**Objective**: Identify weaknesses and improvement opportunities

**Agent**: Researcher

**Analysis Components**:
1. **Structural Analysis**: Check for 7 key components
   - System context
   - Role definition
   - Task description
   - Constraints
   - Format specification
   - Examples
   - Quality criteria

2. **Anti-Pattern Detection**:
   - Vague instructions ("please", "try to", "maybe")
   - Missing context
   - No output format
   - Conflicting instructions
   - Implicit assumptions

3. **Metrics Calculation**:
   - Clarity score
   - Specificity score
   - Completeness score

**Outputs**:
- `analysis-report.json`
- `anti-patterns.json`
- `missing-components.json`

---

### Phase 2: Structure Optimization (10 min)

**Objective**: Reorganize prompt for logical flow

**Agent**: Coder (Prompt Specialist)

**Optimization Steps**:
1. Apply template structure (7 components)
2. Build hierarchical organization
3. Add progressive disclosure
4. Ensure logical flow

**Template Structure**:
```
System Context → Role Definition → Task Description →
Constraints → Format Specification → Examples → Quality Criteria
```

**Outputs**:
- `structured-prompt.md`
- `organization-map.json`

---

### Phase 3: Apply Evidence-Based Techniques (10 min)

**Objective**: Incorporate proven prompt engineering methods

**Agents**: Researcher + Coder

**Techniques Applied**:

1. **Chain-of-Thought**: Add explicit reasoning steps
2. **Self-Consistency**: Multiple reasoning paths
3. **ReAct Pattern**: Reasoning + Acting cycle
4. **Few-Shot Examples**: 2-3 demonstrations
5. **Constraint Framing**: Clear boundaries and priorities

**Enhancement Process**:
- Add thinking tags for reasoning
- Include multiple approaches
- Provide concrete examples
- Frame constraints explicitly

**Outputs**:
- `enhanced-prompt.md`
- `techniques-applied.json`

---

### Phase 4: Validate Effectiveness (10 min)

**Objective**: Test performance and measure improvement

**Agent**: Researcher

**Validation Process**:

1. **Define Test Cases**:
   - Typical use case
   - Edge case
   - Stress test (complex/ambiguous)

2. **Run A/B Tests**:
   - Test original prompt
   - Test optimized prompt
   - Compare outputs

3. **Calculate Metrics**:
   - Average score
   - Success rate
   - Consistency
   - Improvement percentages

**Metrics Tracked**:
```javascript
{
  "scoreImprovement": "+35%",
  "successRateImprovement": "+28%",
  "consistencyImprovement": "+42%"
}
```

**Outputs**:
- `test-results.json`
- `ab-comparison.md`
- `metrics-report.json`

---

### Phase 5: Refine Iteratively (5 min)

**Objective**: Continuous improvement based on results

**Agent**: Coder

**Refinement Process**:

1. **Analyze Failures**:
   - Identify test cases that failed
   - Determine root causes
   - Generate fix recommendations

2. **Apply Refinements**:
   - Add missing constraints
   - Clarify ambiguous instructions
   - Add edge case examples
   - Improve guidance

3. **Re-validate**:
   - Run tests on refined version
   - Compare to optimized version
   - Adopt if improvement > 5%

4. **Generate Documentation**:
   - Optimization report
   - Performance metrics
   - Usage recommendations

**Outputs**:
- `final-prompt.md`
- `optimization-report.md`
- `usage-guide.md`

---

## Workflow Diagram

```
Original Prompt
    ↓
[Phase 1: Analyze]
    ↓
Analysis Report + Anti-Patterns
    ↓
[Phase 2: Structure]
    ↓
Structured Prompt
    ↓
[Phase 3: Enhance]
    ↓
Enhanced Prompt (with techniques)
    ↓
[Phase 4: Validate]
    ↓
A/B Test Results
    ↓
Decision: Improvement > 20%?
    ↓
   Yes → [Phase 5: Refine]
    ↓       ↓
   No    Failure Analysis
    ↓       ↓
    ↓    Apply Fixes
    ↓       ↓
    ↓    Re-validate
    ↓       ↓
    └───────┘
        ↓
Final Optimized Prompt + Report
```

## Decision Points

### After Phase 4
- **IF** improvement > 20% AND success rate > 85% → Accept optimized version
- **ELSE** → Proceed to Phase 5 for refinement

### After Phase 5
- **IF** refined improvement > 5% over optimized → Adopt refined version
- **ELSE** → Keep optimized version

## Evidence-Based Techniques Detail

### Chain-of-Thought (CoT)
```markdown
Think through this step by step:
1. Understand the problem
2. Break into components
3. Reason through logic
4. Synthesize insights
5. Conclude
```

### Self-Consistency
```markdown
Generate 3 independent solutions:
- Approach 1: [Method]
- Approach 2: [Method]
- Approach 3: [Method]

Compare and select best.
```

### ReAct Pattern
```markdown
Thought: [What you're thinking]
Action: [What you're doing]
Observation: [What you learned]
(Repeat until complete)
```

### Few-Shot Learning
```markdown
Example 1: Input → Reasoning → Output
Example 2: Input → Reasoning → Output
Example 3: Input → Reasoning → Output

Now apply to: [Actual Input]
```

## Performance Benchmarks

- **Typical Improvement**: 20-40% score increase
- **Success Rate**: 85-95% after optimization
- **Consistency**: 0.8-0.9 score
- **Time to Optimize**: 20-40 minutes

## Best Practices

1. **Start with Structure**: Fix organization before adding techniques
2. **Use Concrete Examples**: Show don't tell
3. **Test Thoroughly**: Use diverse test cases
4. **Iterate**: Refine based on failures
5. **Document**: Record what worked and why

## Anti-Pattern Detection

| Anti-Pattern | Example | Fix |
|--------------|---------|-----|
| Vague Instructions | "Please try to..." | "You must..." |
| Missing Context | No background | Add domain info |
| No Format | Unstructured output | Specify exact format |
| Conflicting Rules | "Be brief but detailed" | Prioritize constraints |
| Implicit Assumptions | Assumes knowledge | Make explicit |

## Integration Patterns

### With Agent Systems
```javascript
const optimizedAgentPrompt = await promptArchitect.optimize({
  role: 'backend-developer',
  domain: 'API development',
  constraints: ['security-first', 'RESTful'],
  outputFormat: 'production code'
});
```

### With SPARC
```bash
# Optimize SPARC prompts
prompt-architect → sparc-spec-prompt → SPARC workflow
```

### Standalone
```bash
# Optimize any prompt
prompt-architect --input original.md --output optimized.md
```

## Output Schema

```typescript
interface PromptOptimizationResult {
  original: string;
  optimized: string;
  metrics: {
    scoreImprovement: string;
    successRate: number;
    consistency: number;
  };
  changesApplied: string[];
  testResults: TestResult[];
  recommendations: string[];
}
```

For implementation details, see SKILL.md
