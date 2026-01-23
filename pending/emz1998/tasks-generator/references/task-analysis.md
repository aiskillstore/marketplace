# Task Analysis Reference

Quick-reference patterns for extracting tasks from specifications. Focuses on commonly overlooked aspects.

## Priority to Sprint Mapping

| PRD Priority | Sprint Placement |
|--------------|------------------|
| P0 / Must Have | Phase 1 |
| P1 / Should Have | Phase 2 |
| P2 / Nice to Have | Phase 3+ |

## User Story Decomposition

From `As a [user], I want [action] so that [benefit]`:

| Element | Produces |
|---------|----------|
| `[action]` | Implementation task(s) |
| `[user]` | Auth/permission task (if role-specific) |
| `[benefit]` | Acceptance criteria |

**Standard breakdown:** Types → API route → UI component → State/hooks → Error handling → Tests

**Example:** "As a student, I want to save notes so I can review later"
→ Define Note type → Create save API → Build editor UI → Add auto-save hook → Handle save errors → Write tests

## Task Granularity Guidelines

| Indicator | Action |
|-----------|--------|
| Exceeds 1 day of work | Split into smaller tasks |
| Spans multiple domains | Split by domain |
| Contains "and" in title | Split into separate tasks |
| Under 2 hours | Combine with related work |
| Single function change | Combine with parent feature |

**Ideal task:** Single deliverable, testable in isolation, completable in 2-8 hours.

## Dependency Classification

**Hard Dependencies** (sequential execution required):
- Task B consumes Task A's output
- Task B imports from Task A's module
- Task B requires Task A's environment configuration
- Task B's tests depend on Task A's functionality

**Parallel-Safe** (concurrent execution possible):
- Separate domains (frontend/backend)
- No shared types or state
- Independent test suites
- No database schema conflicts

**Example:** "Build login UI" and "Create auth API" are parallel-safe. "Add protected routes" depends on both completing first.

## Commonly Overlooked Tasks

1. **Type/schema definitions** — Must exist before implementation
2. **Authentication setup** — Required before testing protected features
3. **Local storage layer** — Must work standalone before sync implementation
4. **Fallback mechanisms** — Synchronous before asynchronous, cache before network
5. **Error handling** — Required for every async operation
6. **Cross-cutting concerns** — Logging, error boundaries, loading states
7. **Data migrations** — Required for any schema changes

## Testing Considerations

Ensure separate tasks exist for:
- Test infrastructure (mocks, fixtures, test utilities)
- E2E tests for critical user flows
- Integration tests for external service interactions

## Risk-Based Task Additions

| Risk Category | Recommended Task |
|---------------|------------------|
| Unfamiliar technology | Spike/prototype (time-boxed) |
| External API dependency | Mock implementation |
| Performance requirements | Benchmark validation |
| Complex integration | Early integration test |
| Ambiguous requirements | Clarification before implementation |

## Sprint Capacity Guidelines

| Sprint Type | Task Range | Description |
|-------------|------------|-------------|
| Foundation | 6-10 tasks | Project setup, infrastructure, core types |
| Feature | 4-6 tasks | New user-facing functionality |
| Integration | 3-5 tasks | Connecting systems, E2E flows, polish |

Include 10-20% buffer for unexpected blockers.

## Exclusions

Do not create separate tasks for:
- Standard project configuration (package.json, tsconfig)
- Auto-generated code (UI component libraries)
- Familiar patterns within implementer's expertise
- Functionality already present in codebase
- Refactoring (include within feature tasks)
