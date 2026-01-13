# Prompt Optimization Analyzer - Process Flow

## Overview

This document outlines the step-by-step process for analyzing and optimizing prompts.

## Process Phases

### Phase 1: Token Waste Detection (5-10 min)

**Input:** Original prompt text

**Actions:**
1. Count total words and tokens
2. Detect phrase repetition (3+ occurrences)
3. Measure average word length
4. Identify filler words
5. Calculate redundancy/verbosity scores

**Output:**
```json
{
  "totalTokens": 124,
  "redundancyScore": 45,
  "verbosityScore": 30,
  "issues": [...]
}
```

**Hook Integration:**
```bash
npx claude-flow@alpha hooks pre-task --description "Analyzing token waste"
npx claude-flow@alpha memory store --key "optimization/original-tokens" --value "{...}"
```

---

### Phase 2: Anti-Pattern Detection (10-15 min)

**Input:** Prompt text + token analysis results

**Actions:**
1. Scan for vague instruction markers
2. Check for undefined technical terms
3. Identify conflicting requirements
4. Detect missing context
5. Flag over-specification

**Output:**
```json
{
  "patterns": [
    {
      "type": "vague-instruction",
      "severity": "high",
      "examples": ["good", "appropriate", "proper"],
      "suggestion": "Replace with specific criteria"
    }
  ]
}
```

**Detection Rules:**
- Vague terms: better, good, appropriate, proper, suitable
- Missing definitions: >5 technical terms, <30% defined
- Conflicting requirements: >10 MUST + >10 SHOULD statements

---

### Phase 3: Trigger Analysis (5 min)

**Input:** Trigger/activation text

**Actions:**
1. Check for explicit conditions (when/if)
2. Verify specificity (no "something", "anything")
3. Assess scope (too narrow/broad)
4. Evaluate edge case coverage

**Output:**
```json
{
  "triggerIssues": [
    {
      "type": "unclear-condition",
      "severity": "high",
      "suggestion": "Add explicit 'when' clause"
    }
  ]
}
```

---

### Phase 4: Optimization Recommendations (15-20 min)

**Input:** All analysis results

**Agent Task:** Code Analyzer
**Instructions:**
1. Review all detected issues
2. Prioritize by severity and impact
3. Generate specific recommendations
4. Create before/after examples
5. Calculate estimated token savings

**Output:**
```markdown
## Recommendations

### Structural
- [ ] Reorganize into logical sections
- [ ] Extract repetitive content

### Content
- [ ] Replace vague terms: [list]
- [ ] Add definitions: [list]
- [ ] Remove filler words: [count]

### Examples
- [ ] Consolidate similar examples
- [ ] Add edge case examples

### Estimated Savings
- 57 tokens (46%)
- Clarity: +40 points
```

**Hook Integration:**
```bash
npx claude-flow@alpha memory store --key "optimization/recommendations" --value "{...}"
```

---

### Phase 5: Before/After Comparison (10 min)

**Input:** Original + optimized versions

**Actions:**
1. Extract key differences
2. Highlight specific improvements
3. Calculate actual savings
4. Generate comparison report

**Output:**
```markdown
## Before/After Comparison

### Before (124 tokens)
```
[original problematic version]
```

### After (67 tokens)
```
[optimized version]
```

### Key Improvements
1. Removed 4 instances of "you should"
2. Replaced vague terms with criteria
3. Structured feedback format
4. Added specific examples

### Metrics
- Token reduction: 57 (46%)
- Clarity improvement: +40 points
- Specificity: +50 points
```

**Hook Integration:**
```bash
npx claude-flow@alpha hooks post-task --task-id "prompt-optimization"
npx claude-flow@alpha memory store --key "optimization/final-metrics" --value "{...}"
```

---

## Decision Tree

```
Start: Prompt to analyze
  |
  v
Has token budget issue?
  Yes → Prioritize token reduction
  No  → Prioritize clarity
  |
  v
Complexity level?
  Simple  → Focus on structure
  Medium  → Full analysis
  Complex → Add chunking strategy
  |
  v
Target audience?
  AI Agent  → Optimize for precision
  Human Dev → Balance clarity/brevity
  Mixed     → Layered detail approach
  |
  v
Generate recommendations
  |
  v
Apply optimizations
  |
  v
Verify improvements
  |
  v
Store metrics & patterns
  |
  v
End
```

## Integration Points

### Pre-Task Hook
```bash
npx claude-flow@alpha hooks pre-task \
  --description "Optimizing prompt: [name]" \
  --complexity "medium" \
  --estimated-tokens "150"
```

### Memory Storage
```bash
# Store original
npx claude-flow@alpha memory store \
  --key "optimization/[prompt-id]/original" \
  --value "{text, tokens, metrics}"

# Store recommendations
npx claude-flow@alpha memory store \
  --key "optimization/[prompt-id]/recommendations" \
  --value "{issues, suggestions, savings}"

# Store final
npx claude-flow@alpha memory store \
  --key "optimization/[prompt-id]/optimized" \
  --value "{text, tokens, improvements}"
```

### Post-Task Hook
```bash
npx claude-flow@alpha hooks post-task \
  --task-id "optimize-[prompt-id]" \
  --tokens-saved "57" \
  --quality-improvement "40"
```

## Success Criteria

- Token reduction: 20-50%
- All high-severity anti-patterns eliminated
- Trigger precision: >90%
- Clarity score improvement: +30 points minimum
- Maintainability: Easier to understand and modify

## Common Patterns

### Pattern 1: Redundant Instructions
**Before:** "You should X. Make sure to X. Always remember to X."
**After:** "X [with specific criteria]"
**Savings:** ~50%

### Pattern 2: Vague Requirements
**Before:** "Handle errors appropriately"
**After:** "Catch exceptions, log to memory key 'errors/[id]', return {error, message}"
**Improvement:** Actionable specification

### Pattern 3: Example Bloat
**Before:** 8 similar examples
**After:** 3 diverse examples + "See also: [link]"
**Savings:** ~40%

### Pattern 4: Over-Specification
**Before:** 15 detailed formatting rules
**After:** "Follow .editorconfig settings"
**Savings:** ~70%

## Iteration

1. First pass: Identify all issues
2. Second pass: Apply high-severity fixes
3. Third pass: Apply medium-severity fixes
4. Fourth pass: Polish and verify
5. Final pass: Compare metrics and validate

## Related Processes

- Skill Gap Analysis (library-wide review)
- Token Budget Management (chunking strategy)
- Prompt Architecture (advanced patterns)
