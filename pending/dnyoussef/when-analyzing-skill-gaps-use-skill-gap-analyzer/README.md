# Skill Gap Analyzer

Comprehensive skill library analysis tool for identifying coverage gaps, redundant overlaps, and optimization opportunities.

## Overview

This skill helps you:
- Map domain coverage and identify missing capabilities
- Detect duplicate functionality and consolidation opportunities
- Find under-utilized and over-complex skills
- Test scenario execution readiness
- Generate prioritized recommendations

## Quick Start

```bash
# Activate skill
Use skill: when-analyzing-skill-gaps-use-skill-gap-analyzer

# Analyze library
"Analyze my skill library for gaps and optimization opportunities"
```

## Key Features

### 1. Coverage Gap Analysis
- Domain coverage mapping (Development, DevOps, Data, AI/ML, etc.)
- Missing capability identification
- Use case scenario testing
- Priority-based gap ranking

### 2. Redundancy Detection
- Duplicate functionality identification (70%+ overlap)
- Consolidation opportunity analysis
- Naming collision detection
- Token/storage savings estimation

### 3. Optimization Opportunities
- Under-utilized skill detection (<5% usage, 90+ days)
- Over-complex skill identification (high tokens, low success)
- Composability improvement suggestions
- Dependency optimization

### 4. Usage Pattern Analysis
- Frequency metrics
- Co-occurrence patterns
- Success rate tracking
- Token efficiency measurement

### 5. Recommendation Generation
- Prioritized action items (immediate/short/long-term)
- Consolidation strategies
- New skill proposals
- Deprecation candidates

## Example Results

**Input:** Library with 47 skills

**Findings:**
- Domain coverage: 67% (target: 90%)
- Critical gap: Data Engineering (23% coverage)
- Redundancy: 4 code review skills (78% overlap)
- Under-utilized: 3 skills (<5% usage)
- Over-complex: 1 skill (8.7K tokens, 64% success)

**Recommendations:**
1. Create data-engineering-workflow skill
2. Consolidate code review skills (save 15K tokens)
3. Break full-stack-architect into 3 focused skills
4. Archive or promote legacy-converter

**Expected Impact:**
- Coverage: 67% → 89%
- Redundancy: 18% → 7%
- Token efficiency: +32%

## When to Use

- Building new skill library
- Quarterly portfolio reviews
- Before major refactoring
- When considering new skill additions
- After project pivots

## Output Format

```markdown
## Skill Gap Analysis Report

### Executive Summary
- Coverage: [%]
- Gaps: [count]
- Redundancy: [count]
- Optimizations: [count]

### Coverage Gaps (by priority)
...

### Redundancy Analysis
...

### Optimization Opportunities
...

### Scenario Coverage
...

### Prioritized Recommendations
- Immediate
- Short-term
- Long-term
```

## Integration

Works seamlessly with:
- `when-optimizing-prompts-use-prompt-optimization-analyzer` (optimize individual skills)
- `when-managing-token-budget-use-token-budget-advisor` (budget impact)
- `skill-forge` (create new skills)

## Configuration

Analyzes skills in:
- `~/.claude/skills/`
- Project `.claude/skills/`

Tracks metrics in:
- Memory key: `gap-analysis/*`
- Hook integration: pre-task, post-task

## Success Criteria

- Domain coverage: >85%
- Redundancy rate: <10%
- Under-utilization: <5%
- Core scenario execution: 100%
- Recommendation adoption: >80%

## Support

- Version: 1.0.0
- Complexity: MEDIUM
- Agents: researcher, code-analyzer
- Review frequency: Quarterly
