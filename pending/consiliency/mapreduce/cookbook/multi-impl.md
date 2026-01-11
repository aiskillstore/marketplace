# Multi-Implementation Cookbook

> Generate the same feature with multiple models, select or merge the best implementation

## Overview

This cookbook shows how to generate multiple implementations of the same
feature using different AI models, then evaluate and select the best one
or merge the best traits from each.

## When to Use

- Critical code paths where quality matters
- When you want to compare different approaches
- Complex algorithms with multiple valid solutions
- When test coverage makes comparison objective

## Basic Pattern

### Step 1: Define Implementation Spec

Create a clear specification all implementers will follow:

```markdown
## Implementation Specification

Feature: UserService - User management CRUD operations

Interface:
```typescript
interface UserService {
  createUser(data: CreateUserDTO): Promise<User>;
  getUser(id: string): Promise<User | null>;
  updateUser(id: string, data: UpdateUserDTO): Promise<User>;
  deleteUser(id: string): Promise<void>;
  listUsers(filter: UserFilter): Promise<PaginatedResult<User>>;
}
```

Requirements:
- Input validation with proper error types
- Database transaction support
- Audit logging for mutations
- Rate limiting consideration
- Test coverage > 85%
```

### Step 2: Spawn Implementers (MAP)

In a SINGLE message, launch all implementers:

```markdown
Task(subagent_type="general-purpose", prompt="""
  Implement UserService according to spec.

  Read spec: specs/user-service-spec.md

  Write implementation to: implementations/impl-claude.ts
  Write tests to: implementations/impl-claude.test.ts

  Style preferences:
  - Functional programming style
  - Explicit error handling with Result types
  - Comprehensive JSDoc comments
""", run_in_background=true)

# External providers
Bash("codex -m gpt-5.1-codex -a full-auto '$(cat specs/user-service-spec.md)
Implement this in TypeScript. Write to implementations/impl-codex.ts'")

Bash("gemini -m gemini-3-pro '$(cat specs/user-service-spec.md)
Implement this in TypeScript. Write to implementations/impl-gemini.ts'")
```

### Step 3: Collect Results (COLLECT)

```markdown
# Wait for Claude subagent
TaskOutput(task_id=impl-id, block=true, timeout=180000)

# Verify all implementations exist
Glob("implementations/impl-*.ts")

# Quick validation - check files are non-empty and valid TS
Bash("npx tsc --noEmit implementations/impl-*.ts 2>&1 | head -20")
```

### Step 4: Evaluate and Select (REDUCE)

Launch the code reducer:

```markdown
Task(subagent_type="ai-dev-kit:orchestration:code-reducer", prompt="""
  Compare implementations in: implementations/impl-*.ts

  Evaluation steps:
  1. Run static analysis (tsc, eslint)
  2. Run tests against each implementation
  3. Score on rubric criteria
  4. Select winner or merge best traits

  Test command: npm test -- --grep "UserService"

  Output:
  - Selected implementation to: src/services/UserService.ts
  - Quality report to: implementations/COMPARISON.md

  Preferences:
  - Prioritize correctness over elegance
  - Prefer simpler solutions when quality is similar
  - Error handling is critical for this service
""")
```

## Advanced Patterns

### Pattern A: Trait Extraction

When different implementations excel in different areas:

```markdown
## Trait Analysis

| Trait | Best In | Lines | Why |
|-------|---------|-------|-----|
| Error handling | impl-claude | 45-78 | Comprehensive error types |
| Validation | impl-codex | 12-34 | Clean validation chain |
| Performance | impl-gemini | 89-102 | Efficient query building |
| Types | impl-claude | 1-20 | Strong type inference |

## Merge Strategy

1. Base: impl-claude (best overall structure)
2. Replace validation logic with impl-codex approach
3. Adopt query builder from impl-gemini
4. Keep error handling from impl-claude
```

### Pattern B: Test-Driven Selection

When you have a comprehensive test suite:

```markdown
## Test Matrix

| Implementation | Pass | Fail | Coverage | Time |
|----------------|------|------|----------|------|
| impl-claude | 48/50 | 2 | 92% | 1.2s |
| impl-codex | 50/50 | 0 | 88% | 1.8s |
| impl-gemini | 47/50 | 3 | 85% | 0.9s |

## Selection

Winner: impl-codex
Rationale: Only implementation passing all tests
Note: Lower coverage acceptable given 100% test pass rate
```

### Pattern C: A/B Implementation

For features where you want runtime comparison:

```markdown
## Feature Flag Approach

1. Keep both implementations
2. Use feature flag to route traffic
3. Monitor metrics in production
4. Gradually shift to winner

Generated files:
- src/services/UserServiceV1.ts (impl-claude)
- src/services/UserServiceV2.ts (impl-codex)
- src/services/UserService.ts (router with feature flag)
```

## Output Example

```markdown
# Implementation Comparison Report

## Summary

| Implementation | Score | Recommendation |
|----------------|-------|----------------|
| impl-claude | 4.2/5 | SELECTED (with modifications) |
| impl-codex | 3.8/5 | Trait donor (validation) |
| impl-gemini | 3.5/5 | Not selected |

## Static Analysis

### impl-claude
```
Type errors: 0
Lint warnings: 2 (minor - unused imports)
Complexity: 14 (acceptable)
```

### impl-codex
```
Type errors: 0
Lint warnings: 5 (moderate - naming conventions)
Complexity: 18 (moderate)
```

### impl-gemini
```
Type errors: 2 (fixed in evaluation)
Lint warnings: 3 (minor)
Complexity: 11 (good)
```

## Test Results

| Impl | Passed | Failed | Coverage | Performance |
|------|--------|--------|----------|-------------|
| claude | 48/50 | 2 | 92% | 1.2s |
| codex | 50/50 | 0 | 88% | 1.8s |
| gemini | 47/50 | 3 | 85% | 0.9s |

### Failed Tests Detail

impl-claude:
- `should handle concurrent updates` - race condition in update
- `should validate email format` - missing email regex

impl-gemini:
- `should handle concurrent updates` - same issue
- `should paginate correctly` - off-by-one error
- `should apply rate limits` - not implemented

## Scoring Breakdown

| Criterion | claude | codex | gemini |
|-----------|--------|-------|--------|
| Correctness | 4 | 5 | 3 |
| Readability | 5 | 4 | 4 |
| Maintainability | 4 | 4 | 3 |
| Performance | 4 | 3 | 5 |
| Security | 4 | 4 | 3 |
| **Average** | 4.2 | 4.0 | 3.6 |

## Final Implementation

Selected: impl-claude with fixes

Changes made:
1. Fixed race condition (adopted locking from impl-codex)
2. Added email validation (adopted from impl-codex)
3. Kept overall structure and error handling

Output: src/services/UserService.ts
```

## Error Handling

### Compilation Failures

```markdown
If implementation fails to compile:
  - Log the errors
  - Attempt simple fixes (imports, types)
  - If unfixable, exclude from comparison
  - Note exclusion in report
```

### Test Failures

```markdown
If tests fail:
  - Document which tests failed
  - Analyze if fix is simple
  - Compare severity of failures
  - May still select if failures are minor
```

## Tips

1. **Clear specs**: Ambiguous specs produce incompatible implementations
2. **Same interface**: All implementations should match the same interface
3. **Test first**: Have tests ready before generating implementations
4. **Quick iteration**: Start with 2 implementations, add more if needed
5. **Keep all artifacts**: Implementations are valuable for future reference
