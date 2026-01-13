---
name: devflow-constitution-quick-ref
description: Quick reference guide to CC-DevFlow Constitution v2.0.0 with links to full text. Covers all 10 Articles and Phase -1 Gates.
---

# DevFlow Constitution Quick Reference

## Purpose
Provide quick summaries of all 10 Constitutional Articles with links to full Constitution document. This skill does NOT duplicate the complete Constitution text.

**Full Constitution**: `.claude/rules/project-constitution.md` v2.0.0

## Constitution Overview

**Version**: v2.0.0
**Effective Date**: 2025-01-10
**Authority**: Supreme Priority, Inviolable, Persistent, Universal
**Scope**: All requirements, all stages, all agents

## Article I: Quality First (质量至上)

### Summary
Quality is the non-negotiable baseline.

### Key Rules
- **I.1**: NO PARTIAL IMPLEMENTATION (no TODO/FIXME placeholders)
- **I.2**: Test coverage ≥80%
- **I.3**: No "simplified for now" excuses
- **I.4**: Must pass type checking, linting, security scanning, build verification

### Enforcement
- **Real-time**: constitution-guardian guardrail (blocks TODOs/FIXMEs)
- **Batch**: validate-constitution.sh --type all
- **Pre-push**: pre-push-guard.sh

### Example Violations
```markdown
❌ "TODO later: Add email verification"
❌ "// Simplified for now, will complete in v2"
❌ "defer to v2"
```

**For Details**: See `.claude/rules/project-constitution.md#article-i-quality-first-质量至上`

---

## Article II: Architectural Consistency (架构一致性)

### Summary
Maintain codebase uniformity and predictability.

### Key Rules
- **II.1**: No code duplication (search existing codebase first)
- **II.2**: Consistent naming (follow existing patterns)
- **II.3**: Anti-over-engineering (no BaseController, AbstractService)
- **II.4**: Single responsibility (≤500 lines per file)

### Enforcement
- **Phase -1 Gates**: planner agent checks before EPIC generation
- **Code review**: code-reviewer agent

### Example Violations
```typescript
❌ class BaseController {}       // Over-abstraction
❌ function helperManager() {}   // Vague naming
❌ 800-line file                 // Exceeds limit
```

**For Details**: See `.claude/rules/project-constitution.md#article-ii-architectural-consistency-架构一致性`

---

## Article III: Security First (安全优先)

### Summary
Security is foundational, not an afterthought.

### Key Rules
- **III.1**: NO HARDCODED SECRETS (use env variables)
- **III.2**: All inputs must be validated BEFORE processing
- **III.3**: Principle of least privilege (deny by default)
- **III.4**: Secure by default (HTTPS, CORS whitelist, auth required)

### Enforcement
- **Real-time**: constitution-guardian guardrail (blocks hardcoded secrets)
- **Pre-push**: pre-push-guard.sh scans for secret patterns
- **QA**: security-reviewer agent

### Example Violations
```typescript
❌ const API_KEY = "sk-abc123..."    // Hardcoded
❌ const PASSWORD = "admin123"       // Hardcoded
```

**For Details**: See `.claude/rules/project-constitution.md#article-iii-security-first-安全优先`

---

## Article IV: Performance Accountability (性能责任)

### Summary
Performance is user experience; proactive optimization required.

### Key Rules
- **IV.1**: No resource leaks (always close connections)
- **IV.2**: Algorithm efficiency (avoid O(n²) when O(n) exists)
- **IV.3**: Lazy loading (pagination for large datasets)
- **IV.4**: Intelligent caching (with TTL and invalidation)

### Enforcement
- **QA**: qa-tester agent includes performance profiling
- **Code review**: code-reviewer agent checks resource management

### Example Violations
```typescript
❌ loadAllUsers()                    // Loads 1M users into memory
❌ nested loops over same dataset    // O(n²)
❌ no connection.close()             // Resource leak
```

**For Details**: See `.claude/rules/project-constitution.md#article-iv-performance-accountability-性能责任`

---

## Article V: Maintainability (可维护性)

### Summary
Code must be understandable, modifiable, and extensible.

### Key Rules
- **V.1**: No dead code (delete unused imports, commented code)
- **V.2**: Separation of concerns (models, services, controllers, views)
- **V.3**: Documentation mandate (complex algorithms, business logic)
- **V.4**: File size limits (≤500 lines per file, ≤50 lines per function)

### Enforcement
- **Linting**: ESLint, Pylint rules
- **Code review**: code-reviewer agent

### Example Violations
```typescript
❌ // Commented-out code block    // Dead code
❌ Unused import statements         // Dead code
❌ 800-line function               // Exceeds limit
```

**For Details**: See `.claude/rules/project-constitution.md#article-v-maintainability-可维护性`

---

## Article VI: Test-First Development (测试优先开发)

### Summary
Tests define behavior; implementation makes tests pass.

### Key Rules
- **VI.1**: TDD mandate (write tests FIRST, tests MUST fail initially)
- **VI.2**: Test independence (each test runs in isolation)
- **VI.3**: Meaningful tests (no `assert True`, test actual behavior)

### Enforcement
- **Real-time**: devflow-tdd-enforcer guardrail (blocks TDD violations)
- **TASKS.md**: TEST VERIFICATION CHECKPOINT between Phase 2 and Phase 3
- **planner agent**: Generates TASKS.md with TDD order

### TDD Sequence
```
Phase 2: Write Tests FIRST ⚠️
  → All tests MUST fail initially
  → TEST VERIFICATION CHECKPOINT

Phase 3: Write Implementation
  → Goal: Make tests pass
```

**For Details**: See `.claude/rules/project-constitution.md#article-vi-test-first-development-测试优先开发`

---

## Article VII: Simplicity Gate (简单性闸门)

### Summary
Default to simplicity; complexity requires justification.

### Key Rules (Phase -1 Gates)
- **VII.1**: Maximum project count ≤3 simultaneously
- **VII.2**: Minimal dependencies (use standard library when possible)
- **VII.3**: Vertical slice first (full feature before next feature)
- **VII.4**: Direct framework usage (avoid custom abstractions)

### Enforcement
- **Phase -1 Gates**: planner agent enforces BEFORE generating EPIC
- **EPIC.md**: Contains "Phase -1 Simplicity Gate" check section

### Example Violations
```yaml
❌ 5 projects in scope                    # Exceeds limit
❌ Adding new framework for simple task   # Over-dependency
❌ Custom ORM wrapper                     # Unnecessary abstraction
```

**For Details**: See `.claude/rules/project-constitution.md#article-vii-simplicity-gate-简单性闸门`

---

## Article VIII: Anti-Abstraction (反抽象化)

### Summary
Prefer concrete code over abstractions until three+ use cases proven.

### Key Rules (Phase -1 Gates)
- **VIII.1**: No premature abstraction (Rule of Three)
- **VIII.2**: No generic layers (no GenericService<T>)
- **VIII.3**: Direct framework usage (Express, FastAPI, Flask)
- **VIII.4**: Inline before extract (copy-paste OK until 3rd repetition)

### Enforcement
- **Phase -1 Gates**: planner agent enforces BEFORE generating EPIC
- **EPIC.md**: Contains "Phase -1 Anti-Abstraction Gate" check section

### Example Violations
```typescript
❌ class BaseController {}              // Premature abstraction
❌ GenericRepository<T>                 // Generic layer
❌ Custom framework wrapper             // Over-abstraction
```

**For Details**: See `.claude/rules/project-constitution.md#article-viii-anti-abstraction-反抽象化`

---

## Article IX: Integration-First Testing (集成优先测试)

### Summary
Test contracts/integrations before internal logic.

### Key Rules (Phase -1 Gates)
- **IX.1**: Contract tests first (API contracts, GraphQL schemas)
- **IX.2**: Integration tests before unit tests (test boundaries first)
- **IX.3**: Test external dependencies (database, APIs, queues)
- **IX.4**: E2E critical paths (happy path + error path)

### Enforcement
- **Phase -1 Gates**: planner agent enforces BEFORE generating EPIC
- **TASKS.md Phase 2**: Lists contract/integration tests FIRST
- **TEST VERIFICATION CHECKPOINT**: Ensures Phase 2 tests run before Phase 3

### Test Order
```
1. Contract tests (API contracts, GraphQL)
2. Integration tests (DB, external APIs)
3. E2E tests (critical user paths)
4. Unit tests (internal logic)
```

**For Details**: See `.claude/rules/project-constitution.md#article-ix-integration-first-testing-集成优先测试`

---

## Article X: Requirement Boundary (需求边界)

### Summary
Prevent scope creep; enforce strict requirement boundaries.

### Key Rules
- **X.1**: One REQ-ID, one bounded context (no "also add X")
- **X.2**: No feature expansion during implementation
- **X.3**: Separate REQ-IDs for separate concerns
- **X.4**: Explicit scope documentation in PRD.md

### Enforcement
- **PRD generation**: prd-writer agent enforces Anti-Expansion mandate
- **Scope validation**: validate-scope-boundary.sh
- **Code review**: code-reviewer agent checks for scope violations

### Example Violations
```markdown
❌ PRD.md: "User Registration (also add social login)"    # Scope creep
❌ Adding unplanned features during /flow-dev             # Feature expansion
```

**For Details**: See `.claude/rules/project-constitution.md#article-x-requirement-boundary-需求边界`

---

## Phase -1 Gates

**Executed by**: planner agent BEFORE generating EPIC and TASKS

### Gate 1: Simplicity Check (Article VII)
- [ ] Project count ≤3
- [ ] Minimal dependencies
- [ ] Vertical slice approach
- [ ] Direct framework usage

### Gate 2: Anti-Abstraction Check (Article VIII)
- [ ] No premature abstractions
- [ ] No generic layers
- [ ] Inline before extract
- [ ] Direct framework calls

### Gate 3: Integration-First Check (Article IX)
- [ ] Contract tests listed first
- [ ] Integration tests before unit tests
- [ ] External dependency tests included
- [ ] E2E critical paths covered

**Documented in**: EPIC.md contains "Phase -1 Gates" check section

**For Details**: See [planner agent](.claude/agents/planner.md) Phase -1 Gates Enforcement Sequence

---

## Enforcement Summary

| Article | Real-time Guardrail | Phase Gate | Batch Validation | Pre-push |
|---------|---------------------|------------|------------------|----------|
| I       | constitution-guardian | prd/tech/epic Exit | validate-constitution.sh | ✓ |
| II      | —                   | Phase -1 (planner) | validate-constitution.sh | — |
| III     | constitution-guardian | — | validate-constitution.sh | ✓ |
| IV      | —                   | — | validate-constitution.sh (QA) | — |
| V       | —                   | — | Linting + code review | — |
| VI      | devflow-tdd-enforcer | TEST VERIFICATION | validate-constitution.sh | — |
| VII     | —                   | Phase -1 (planner) | validate-constitution.sh | — |
| VIII    | —                   | Phase -1 (planner) | validate-constitution.sh | — |
| IX      | —                   | Phase -1 (planner) | validate-constitution.sh | — |
| X       | —                   | PRD generation | validate-scope-boundary.sh | — |

---

## Quick Lookup by Scenario

### Scenario: "Can I add TODO for later?"
**Answer**: ❌ NO (Article I.1 - No Partial Implementation)
**Guardrail**: constitution-guardian blocks save
**Alternative**: Complete implementation now, or remove from scope

### Scenario: "Should I create BaseController?"
**Answer**: ❌ NO (Article II.3, VIII.2 - Anti-Abstraction)
**Phase Gate**: Phase -1 Gates block EPIC generation
**Alternative**: Use framework directly (Express, FastAPI)

### Scenario: "Can I hardcode API_KEY for testing?"
**Answer**: ❌ NO (Article III.1 - No Hardcoded Secrets)
**Guardrail**: constitution-guardian blocks save
**Alternative**: Use .env file with dotenv library

### Scenario: "Should I write implementation first?"
**Answer**: ❌ NO (Article VI.1 - TDD Mandate)
**Guardrail**: devflow-tdd-enforcer blocks TASKS.md edit
**Sequence**: Write failing test FIRST, then implementation

### Scenario: "Can I add social login to user registration?"
**Answer**: ❌ NO (Article X.1 - Requirement Boundary)
**Enforcement**: prd-writer agent Anti-Expansion mandate
**Alternative**: Create separate REQ-ID for social login

---

## Design Principle

**This skill does NOT contain**:
- ❌ Complete Constitution text (that's in project-constitution.md)
- ❌ Detailed Article explanations (that's in full Constitution)
- ❌ Implementation guidelines (those are in agent files)

**This skill ONLY contains**:
- ✅ Article summaries (quick reference)
- ✅ Key rules and examples
- ✅ Enforcement mechanisms
- ✅ Links to full Constitution document
- ✅ Quick lookup by scenario

**Rationale**: Avoid duplication ("不重不漏" principle). Constitution document owns full text, this skill owns quick reference and routing.
