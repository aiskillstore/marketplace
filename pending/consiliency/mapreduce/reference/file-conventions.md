# File Conventions Reference

> Standard file locations and naming for MapReduce workflows

## Overview

MapReduce operations use file-based coordination between workers and reducers.
This document defines the standard locations and naming conventions.

## Directory Structure

```
project-root/
├── specs/
│   ├── plans/                    # Planning outputs
│   │   ├── planner-claude.md
│   │   ├── planner-codex.md
│   │   ├── planner-gemini.md
│   │   └── planner-cursor.md
│   ├── ROADMAP.md               # Consolidated plan
│   └── attribution.md           # What came from where
│
├── implementations/              # Code generation outputs
│   ├── impl-claude.ts
│   ├── impl-codex.ts
│   ├── impl-gemini.ts
│   ├── COMPARISON.md            # Evaluation report
│   └── selected/                # Winner or merged code
│       └── implementation.ts
│
├── diagnoses/                   # Debug outputs
│   ├── debug-claude.md
│   ├── debug-codex.md
│   ├── debug-gemini.md
│   └── RESOLUTION.md            # Selected fix documentation
│
└── reviews/                     # Code review outputs
    ├── review-claude.md
    ├── review-codex.md
    └── CONSOLIDATED-REVIEW.md
```

## Naming Conventions

### Worker Outputs

Pattern: `{type}-{provider}.{ext}`

| Type | Provider | Example |
|------|----------|---------|
| planner | claude, codex, gemini, cursor | `planner-claude.md` |
| impl | claude, codex, gemini, cursor | `impl-codex.ts` |
| debug | claude, codex, gemini, cursor | `debug-gemini.md` |
| review | claude, codex, gemini, cursor | `review-cursor.md` |

### Variant Workers

For multiple workers of the same type:

Pattern: `{type}-{variant}.{ext}`

| Variant | Description | Example |
|---------|-------------|---------|
| conservative | Low-risk approach | `planner-conservative.md` |
| aggressive | Fast-track approach | `planner-aggressive.md` |
| security | Security-focused | `planner-security.md` |
| scalability | Scale-focused | `planner-scalability.md` |

### Consolidated Outputs

| Type | Location | Naming |
|------|----------|--------|
| Roadmaps | `specs/ROADMAP.md` | UPPERCASE |
| Phase plans | `specs/P{n}.md` | P1.md, P2.md |
| Code | Target location | Original name |
| Reviews | Same dir as inputs | `CONSOLIDATED-REVIEW.md` |
| Comparison | Same dir as inputs | `COMPARISON.md` |

## File Formats

### Planning Outputs

```markdown
# {Feature} Implementation Plan

## Executive Summary
[2-3 paragraphs]

## Strategic Bias
[conservative | aggressive | security | scalability]

## Phases

### Phase 1: {Name}
#### Objective
#### Tasks
#### Dependencies
#### Risks
#### Exit Criteria

...

## Timeline Estimate
## Risk Assessment
```

### Code Implementation Outputs

```typescript
/**
 * Implementation: {feature}
 * Provider: {claude | codex | gemini}
 * Strategy: {description}
 *
 * @generated
 */

// Implementation code
```

### Debug Diagnosis Outputs

```markdown
# Bug Diagnosis: {Issue ID/Title}

## Symptom
[What was observed]

## Root Cause Hypothesis
[Technical explanation]

## Evidence
[Code references, stack traces, logs]

## Proposed Fix

### Location
file:line

### Change
```diff
- old code
+ new code
```

### Confidence
[HIGH | MEDIUM | LOW]

### Rationale
[Why this fix works]
```

## Attribution Format

Every consolidated output should reference sources:

```markdown
## Attribution

| Section | Primary Source | Contributing | Confidence |
|---------|---------------|--------------|------------|
| Phase 1 | planner-claude | planner-codex | HIGH |
| Auth Design | planner-security | - | LOW |
| Timeline | planner-conservative | All | HIGH |

## Source Files

- planner-claude.md: specs/plans/planner-claude.md
- planner-codex.md: specs/plans/planner-codex.md
- planner-security.md: specs/plans/planner-security.md
- planner-conservative.md: specs/plans/planner-conservative.md
```

## Cleanup

### Preserving Artifacts

By default, keep intermediate files for:
- Auditing decisions
- Debugging consolidation issues
- Learning from different approaches

### Optional Cleanup

After successful consolidation:

```bash
# Archive intermediate files
mkdir -p .archive/mapreduce/$(date +%Y%m%d)
mv specs/plans/planner-*.md .archive/mapreduce/$(date +%Y%m%d)/
mv implementations/impl-*.ts .archive/mapreduce/$(date +%Y%m%d)/

# Or delete if not needed
rm -rf specs/plans/planner-*.md
```

## Git Integration

### Commit Patterns

```bash
# After map phase
git add specs/plans/
git commit -m "feat(planning): parallel planning outputs for ${feature}"

# After reduce phase
git add specs/ROADMAP.md specs/attribution.md
git commit -m "feat(planning): consolidated roadmap for ${feature}"

# Cleanup
git add .archive/
git commit -m "chore: archive mapreduce artifacts"
```

### Branch Strategy

For large MapReduce operations:

```bash
# Create feature branch
git checkout -b feature/${feature}-mapreduce

# Map phase commits
# Reduce phase commits
# Cleanup commits

# Merge to main
git checkout main
git merge feature/${feature}-mapreduce
```

## Error States

### Missing Files

If expected worker output is missing:

```markdown
## Missing Outputs

| Worker | Expected | Status |
|--------|----------|--------|
| planner-claude | specs/plans/planner-claude.md | ✓ Present |
| planner-codex | specs/plans/planner-codex.md | ✗ Missing |

Proceeding with available outputs. Confidence reduced.
```

### Malformed Files

If worker output is invalid:

```markdown
## Invalid Outputs

| Worker | Issue | Action |
|--------|-------|--------|
| impl-codex | Type errors | Attempted fix |
| impl-gemini | Empty file | Excluded |
```

## Best Practices

1. **Consistent naming**: Always use the same provider names
2. **Clear directories**: Keep types of outputs separate
3. **Preserve attribution**: Never lose track of what came from where
4. **Version control**: Commit intermediate outputs for history
5. **Clean up intentionally**: Archive or delete, don't leave orphans
