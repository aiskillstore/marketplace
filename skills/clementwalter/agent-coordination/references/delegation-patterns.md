# Delegation Patterns

Detailed patterns for delegating work to coding agents using a two-tier model approach.

## Two-Tier Delegation Model

### Why Two Tiers?

Different tasks require different capabilities:

| Task Type      | Model Needed | Cost   | Example                             |
| -------------- | ------------ | ------ | ----------------------------------- |
| Investigation  | Opus/Sonnet  | Higher | "Find all usages of deprecated API" |
| Implementation | Haiku/Sonnet | Lower  | "Replace X with Y in these 5 files" |

**Key insight**: Expensive models do thinking; cheap models do execution with clear instructions.

### Tier 1: Investigation Tasks

**Purpose**: Explore, quantify, plan

**Characteristics**:

- Requires understanding complex codebases
- Needs judgment and decision-making
- Produces a detailed plan for execution
- Uses Opus or Sonnet model

**Task Template**:

```markdown
## Investigate: [Brief description]

### Question

[What needs to be understood/discovered]

### Context

[Background information]

### Investigation Areas

1. [Area to explore]
2. [Area to explore]

### Expected Deliverables

- [ ] Summary of findings with file paths
- [ ] Quantified scope (e.g., "12 files, ~200 lines to change")
- [ ] Poker planning estimate (S/M/L/XL)
- [ ] Detailed implementation plan for executor
- [ ] Follow-up task descriptions ready to create

### Output Format

Provide implementation plan as markdown that can be directly used as a task description for the implementation tier.
```

### Tier 2: Implementation Tasks

**Purpose**: Execute a clear, pre-defined plan

**Characteristics**:

- Clear instructions from investigation phase
- Minimal decision-making required
- Follows step-by-step plan
- Uses Haiku or Sonnet model

**Task Template**:

```markdown
## Implement: [Brief description]

### Plan

[Paste the detailed plan from investigation]

### Steps

1. [ ] Step 1 with specific file/function
2. [ ] Step 2 with specific changes
3. [ ] Step 3...

### Verification

- [ ] Tests pass
- [ ] No new warnings
- [ ] CI green

### Report

When done, summarize:

- What worked as planned
- What required adjustment
- Any follow-up needed
```

## Complete Two-Tier Example

### User Request

"Remove all references to the old 'lovable' branding"

### Tier 1: Investigation Task

````markdown
## Investigate: Scope of lovable branding removal

### Question

Quantify all "lovable" references that need removal or replacement.

### Context

We're rebranding. Need to find all mentions of "lovable" in code, docs, and config.

### Investigation Areas

1. Source code (strings, comments, variable names)
2. Documentation files
3. Configuration and environment files
4. Test fixtures and mocks
5. CI/CD configurations

### Expected Deliverables

- [ ] Complete list of files with "lovable" references
- [ ] Count of changes per file
- [ ] Classification (code vs docs vs config)
- [ ] Risk assessment (breaking changes?)
- [ ] Implementation plan for executor

### Tools to Use

```bash
grep -r "lovable" --include="*.{ts,js,tsx,jsx,md,json,yaml,yml}"
```

**Investigation Output** (what the agent produces):

```markdown
## Findings: Lovable Branding Removal

### Summary

- **Total files**: 23
- **Total occurrences**: 67
- **Estimate**: Medium (2-4 hours)

### Breakdown

| Category   | Files | Occurrences | Risk   |
| ---------- | ----- | ----------- | ------ |
| UI strings | 8     | 24          | Low    |
| Comments   | 6     | 18          | None   |
| Docs       | 5     | 15          | Low    |
| Config     | 4     | 10          | Medium |

### High-Risk Items

- `config/branding.ts` - exports BRAND_NAME constant used in 12 places
- `.env.example` - LOVABLE_API_KEY needs renaming

### Implementation Plan

**Phase 1: Config (do first)**

1. Update `config/branding.ts`: change BRAND_NAME export
2. Rename env var in `.env.example` and `.env.local`

**Phase 2: UI Strings**
Files: [list of 8 files with line numbers]

**Phase 3: Documentation**
Files: [list of 5 files]

**Phase 4: Comments** (optional, low priority)
Files: [list of 6 files]
```

### Tier 2: Implementation Task

```markdown
## Implement: Remove lovable branding - Phase 1 & 2

### Plan

From investigation task #123.

### Phase 1: Config

1. `config/branding.ts:5` - Change `BRAND_NAME = "lovable"` to `BRAND_NAME = "newbrand"`
2. `.env.example:12` - Rename `LOVABLE_API_KEY` to `NEWBRAND_API_KEY`
3. `.env.local` - Same rename

### Phase 2: UI Strings

1. `src/components/Header.tsx:23` - Update welcome message
2. `src/components/Footer.tsx:8` - Update copyright
   [... specific file:line for each change ...]

### Verification

- [ ] `npm run build` succeeds
- [ ] `npm test` passes
- [ ] `grep -r "lovable"` returns only Phase 3/4 items

### Out of Scope

- Documentation (Phase 3 - separate task)
- Comments (Phase 4 - optional)
```

## Parallel vs Sequential Delegation

### Safe to Parallelize

Tasks can run simultaneously when:

- Different directories
- No shared dependencies
- Independent features

```text
Task A: Update /src/auth/*
Task B: Update /src/billing/*
→ Safe to run in parallel
```

### Must Be Sequential

Tasks must wait when:

- Same files
- One depends on other's output
- Shared state/config

```text
Task A: Refactor config system
Task B: Update features using config
→ B waits for A to complete
```

## Handling Task Results

### On Success

1. Update task status to `done`
2. Check for follow-up tasks
3. Verify no regression

### On Partial Success

1. Keep task `inprogress`
2. Create follow-up task for remaining work
3. Document what completed

### On Failure

1. Keep task `inprogress`
2. Analyze failure reason
3. Either:
   - Adjust plan and retry
   - Escalate to user
   - Create investigation task to understand issue

## Cost Optimization Tips

1. **Batch similar changes**: One task for "update all imports" vs individual tasks
2. **Front-load investigation**: Thorough Tier 1 prevents Tier 2 rework
3. **Limit scope**: Smaller tasks = lower risk of expensive failures
4. **Use Haiku for**: Formatting, simple replacements, test running
5. **Use Opus for**: Architecture decisions, complex refactoring, debugging
````
