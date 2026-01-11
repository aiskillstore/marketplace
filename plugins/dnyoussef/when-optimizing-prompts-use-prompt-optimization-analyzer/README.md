# Prompt Optimization Analyzer

Active diagnostic tool for analyzing prompt quality, detecting anti-patterns, and providing optimization recommendations.

## Overview

This skill helps you:
- Detect token waste (redundancy, verbosity, filler words)
- Identify anti-patterns (vague instructions, ambiguity, conflicts)
- Analyze trigger clarity and precision
- Generate optimization recommendations
- Compare before/after metrics

## Quick Start

```bash
# Activate skill
Use skill: when-optimizing-prompts-use-prompt-optimization-analyzer

# Provide prompt to analyze
"Analyze this prompt for optimization: [paste prompt text]"
```

## Key Features

### 1. Token Efficiency Analysis
- Redundancy detection (repeated phrases)
- Verbosity measurement (avg word length)
- Filler word identification
- Example bloat detection

### 2. Anti-Pattern Detection
- Vague instructions ("make it better")
- Ambiguous terminology ("handle appropriately")
- Conflicting requirements
- Missing context/definitions
- Over-specification

### 3. Trigger Analysis
- Clarity assessment
- Specificity check
- Scope evaluation
- Edge case coverage

### 4. Optimization Recommendations
- Structural improvements
- Content refinements
- Example consolidation
- Token savings estimation

## Example Results

**Input:** 124-token vague prompt
**Output:** 67-token optimized prompt (46% reduction)
**Improvements:**
- Removed redundant phrases (4 instances of "you should")
- Replaced vague terms with specific criteria
- Structured feedback format
- Clear process steps

## When to Use

- Before publishing new skills
- When prompts exceed token budgets
- During skill maintenance
- When responses are inconsistent
- For library-wide optimization

## Output Format

```markdown
## Prompt Optimization Report

### Original Metrics
- Total tokens: 124
- Redundancy score: 45/100
- Verbosity score: 30/100

### Issues Detected (by severity)
...

### Recommendations
...

### Before/After Comparison
...

### Estimated Savings
- 57 tokens (46%)
- Clarity: +40 points
```

## Integration

Works seamlessly with:
- `when-analyzing-skill-gaps-use-skill-gap-analyzer`
- `when-managing-token-budget-use-token-budget-advisor`
- `prompt-architect`

## Configuration

No configuration needed. Embedded analysis scripts run automatically.

## Support

- Version: 1.0.0
- Complexity: MEDIUM
- Agents: code-analyzer, researcher
- Hooks: Yes (pre-task, post-task, memory)
