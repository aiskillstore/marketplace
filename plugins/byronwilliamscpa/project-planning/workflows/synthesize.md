---
argument-hint: [--start-phase]
description: Synthesize 4 planning documents into comprehensive PROJECT-PLAN.md with git branch strategy
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(git:*), TodoWrite
---

# Synthesize Planning Documents Workflow

Transform the four generated planning documents into a comprehensive, actionable project plan with semantic release-aligned phase branches.

## Prerequisites

Run this workflow AFTER generating all planning documents:

```bash
# Verify documents exist (not placeholders)
ls -la docs/planning/
# Should show: project-vision.md, tech-spec.md, roadmap.md, adr/
```

## Arguments

- `--start-phase`: After synthesis, automatically create the first phase branch

## Workflow Steps

### 1. Validate Source Documents

```bash
# Check each document is generated (not placeholder)
echo "Checking planning documents..."

for doc in project-vision.md tech-spec.md roadmap.md; do
    if grep -q "Awaiting Generation" "docs/planning/$doc" 2>/dev/null; then
        echo "❌ $doc not generated - run /plan first"
        exit 1
    fi
    echo "✅ $doc exists"
done

# Check ADRs exist
adr_count=$(ls docs/planning/adr/*.md 2>/dev/null | wc -l)
if [ "$adr_count" -eq 0 ]; then
    echo "❌ No ADR documents found"
    exit 1
fi
echo "✅ Found $adr_count ADR(s)"
```

### 2. Extract Information

Read and extract key information from each document:

**project-vision.md**:
- TL;DR / Executive summary
- Problem statement
- Target users
- Core capabilities (in-scope)
- Out-of-scope items
- Success metrics
- Constraints

**tech-spec.md**:
- Technology stack
- Architecture overview
- Data model
- API specifications
- Security requirements
- Dependencies

**roadmap.md**:
- Phase names and durations
- Deliverables per phase
- Success criteria
- Dependencies
- Risks

**adr/*.md**:
- Decision titles
- Status
- Key rationale
- Consequences

### 3. Map Phases to Git Branches

For each phase in the roadmap, determine the appropriate branch type:

| Phase Content | Branch Type | Version Impact |
|---------------|-------------|----------------|
| Foundation/Setup/Infrastructure | `feat/` | Minor (0.X.0) |
| Core Features | `feat/` | Minor (0.X.0) |
| Additional/Advanced Features | `feat/` | Minor (0.X.0) |
| Performance Optimization | `perf/` | Patch (0.0.X) |
| Documentation | `docs/` | No release |
| Bug Fixes | `fix/` | Patch (0.0.X) |
| Refactoring | `refactor/` | No release |

**Branch Naming**:
```
{type}/phase-{number}-{short-slug}

Examples:
feat/phase-0-foundation
feat/phase-1-core-features
feat/phase-2-advanced
perf/phase-3-optimization
docs/phase-4-documentation
```

### 4. Generate PROJECT-PLAN.md

Create `docs/planning/PROJECT-PLAN.md` with synthesized content:

```markdown
---
schema_type: planning
title: "{project_name} - Project Plan"
description: "Comprehensive project plan synthesized from planning documents"
status: active
generated: "{date}"
source_documents:
  - project-vision.md
  - tech-spec.md
  - roadmap.md
  - adr/*.md
---

# Project Plan: {Project Name}

> **Generated**: {date}
> **Status**: Ready for Development

## Executive Summary

{Synthesized from PVS TL;DR and problem statement}

## Project Scope

### In Scope
{From PVS core capabilities}

### Out of Scope
{From PVS out-of-scope}

## Git Branch Strategy

| Phase | Branch | Type | Version Impact |
|-------|--------|------|----------------|
| Phase 0 | `feat/phase-0-foundation` | feat | Minor |
| Phase 1 | `feat/phase-1-{name}` | feat | Minor |
| ... | ... | ... | ... |

**Start a phase**:
```bash
/git/milestone start {branch-name}
```

**Complete a phase**:
```bash
/git/milestone complete
/git/pr-prepare --include_wtd=true
```

## Phased Development

{For each phase from roadmap}

### Phase {N}: {Name}

**Branch**: `{type}/phase-{n}-{slug}`
**Duration**: {duration}
**Dependencies**: {dependencies}

**Deliverables**:
{list from roadmap}

**Success Criteria**:
{criteria from roadmap}

**Start Phase**:
```bash
/git/milestone start {branch-name}
```

---

{Repeat for all phases}

## System Architecture

{From tech-spec architecture section}

## Technology Stack

{From tech-spec with versions}

## Architecture Decisions

{For each ADR}

### ADR-{N}: {Title}

**Status**: {status}
**Summary**: {brief summary}
**Rationale**: {key points}

[Full ADR](./adr/adr-{n}-{slug}.md)

---

## Risk Management

{Consolidated from all documents}

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
{risks from roadmap and ADRs}

## Success Metrics

{From PVS success metrics}

## Dependencies & Requirements

{From tech-spec}

## Next Steps

1. Review this synthesized plan for accuracy
2. Start Phase 0:
   ```bash
   /git/milestone start feat/phase-0-foundation
   ```
3. Track progress with TodoWrite
4. Complete phases with PR workflow

## Document References

- [Project Vision & Scope](./project-vision.md)
- [Technical Specification](./tech-spec.md)
- [Development Roadmap](./roadmap.md)
- [Architecture Decisions](./adr/)
```

### 5. Create Initial TODO List

Generate TodoWrite items for Phase 0:

```markdown
## Phase 0: Foundation

### Setup
- [x] Generate planning documents (PVS, Tech Spec, Roadmap, ADR)
- [x] Synthesize into PROJECT-PLAN.md
- [ ] Review synthesized plan
- [ ] Create phase branch: feat/phase-0-foundation

### Phase 0 Deliverables
{From roadmap Phase 0 deliverables}

### Phase Completion
- [ ] All deliverables complete
- [ ] Tests passing
- [ ] Pre-commit checks pass
- [ ] Create PR via /git/pr-prepare
```

### 6. Optional: Start First Phase

If `--start-phase` argument provided:

```bash
# Create first phase branch
/git/milestone start feat/phase-0-foundation

# Or if on main already:
git checkout -b feat/phase-0-foundation
```

## Output Summary

After synthesis:

```
✅ Created docs/planning/PROJECT-PLAN.md

📊 Plan Summary:
   - {N} phases identified
   - Phase branches: feat/phase-0-foundation, feat/phase-1-...
   - {M} architecture decisions referenced
   - {K} risks identified

📋 TODO list created for Phase 0

🚀 Next: Review plan, then run:
   /git/milestone start feat/phase-0-foundation
```

## Error Handling

### Missing Documents
```
❌ Missing required documents:
   - project-vision.md (placeholder)
   - tech-spec.md (placeholder)

Run first: /plan <your project description>
```

### Conflicting Information
```
⚠️ Inconsistency detected:
   - Roadmap Phase 1 duration: 3 weeks
   - Tech Spec estimates: 5 weeks

Please clarify timeline before synthesis.
```

### No ADRs Found
```
⚠️ No Architecture Decision Records found.

Consider creating ADR for:
- Database choice
- Authentication strategy
- Key framework decisions

Use: /adr create <decision-title>
```

## Related Commands

- `/plan <description>` - Generate initial 4 documents
- `/git/milestone start` - Start phase branch
- `/git/milestone complete` - Complete phase
- `/git/pr-prepare` - Create PR
