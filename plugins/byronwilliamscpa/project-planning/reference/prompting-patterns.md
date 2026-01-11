# Prompting Patterns for Planning Documents

How to effectively use planning documents during AI-assisted development.

## Table of Contents

1. [Context Loading Patterns](#context-loading-patterns)
2. [Incremental Development](#incremental-development)
3. [Validation Patterns](#validation-patterns)
4. [Update Patterns](#update-patterns)

---

## Context Loading Patterns

### Starting a New Session

Load only relevant sections, not entire documents:

```
Load context from:
- project-vision.md sections 2-3 (solution overview, scope)
- adr/adr-001-database-choice.md (we're working on data layer)
- tech-spec.md section 3 (data model)

Then implement the User entity as defined.
```

### Feature-Specific Loading

```
For implementing authentication:
- Load adr/adr-002-auth-strategy.md
- Load tech-spec.md sections 4, 6 (API spec, security)
- Reference roadmap.md Phase 1 user stories

Implement login endpoint.
```

### Resuming After Break

```
Resuming development after [X] days.

Current state from roadmap.md:
- Phase 1 in progress
- M1 (authentication) complete
- M2 (CRUD operations) next

Continue with US-003 from roadmap.
```

---

## Incremental Development

### Feature Implementation

**Bad** (too broad):
```
Build the entire authentication system.
```

**Good** (incremental):
```
Implement user registration endpoint per tech-spec.md section 4.1.
Focus on input validation first, per ADR-002 validation strategy.
```

### Test-Driven Approach

```
Write failing tests for login feature as defined in:
- roadmap.md Phase 1, US-002 acceptance criteria
- tech-spec.md section 4 (API specification)

Then implement to make tests pass.
```

### Component by Component

```
From tech-spec.md section 2 (Architecture):

Implement [Component A] first:
- Purpose: [from tech spec]
- Interfaces: [from tech spec]
- Tests: [from roadmap acceptance criteria]

Do not implement [Component B] yet (dependency).
```

---

## Validation Patterns

### Code Review Against Specs

```
Review this authentication code against:
- ADR-002 (JWT implementation decision)
- tech-spec.md section 6 (security requirements)
- tech-spec.md section 7 (error handling)

Flag any violations or improvements.
```

### Architecture Compliance

```
This PR adds a caching layer.

Check against:
- ADR index: Is there an existing caching ADR?
- tech-spec.md: Does this align with architecture diagram?
- project-vision.md: Is caching in scope for MVP?

Should we create ADR-00X for this decision?
```

### Security Validation

```
Validate this code against tech-spec.md section 6 (Security):

Check:
- [ ] Authentication method matches ADR-002
- [ ] Authorization per tech-spec RBAC section
- [ ] Data protection requirements met
- [ ] No sensitive data in logs

Report any violations.
```

---

## Update Patterns

### After Completing a Task

```
Completed US-001 from roadmap.md Phase 1.

Update roadmap.md:
- Mark US-001 tasks as ✅ Done
- Update milestone M1 progress
- Note any discovered blockers

Then proceed to US-002.
```

### After Making a Decision

```
Decided to use Redis for caching instead of in-memory.

Create docs/planning/adr/adr-004-caching-strategy.md:
- Context: Performance requirements from tech-spec
- Decision: Redis
- Alternatives: In-memory, Memcached
- Consequences: New dependency, deployment change

Update tech-spec.md section 1 (Technology Stack) to include Redis.
```

### After Scope Change

```
Stakeholder requested: Add export to CSV feature.

Update documents:
1. project-vision.md: Add to scope (In Scope or Phase 2?)
2. tech-spec.md: Add export component if in scope
3. roadmap.md: Add user story to appropriate phase

Flag if this affects timeline.
```

---

## Anti-Patterns to Avoid

### Context Dumping

**Bad**:
```
Here's my entire project-vision.md, tech-spec.md, and all ADRs.
Now implement feature X.
```

**Good**:
```
From tech-spec.md section 4.2 and ADR-001,
implement the database migration for User entity.
```

### Vague References

**Bad**:
```
Follow the spec.
Per the architecture decision.
```

**Good**:
```
Per tech-spec.md section 3.2 (User entity schema).
Per ADR-001 decision to use PostgreSQL with UUID primary keys.
```

### Skipping Validation

**Bad**:
```
Looks good, merge it.
```

**Good**:
```
Before merging, validate against:
- tech-spec.md section 6 (security)
- roadmap.md Definition of Done checklist
```

### Ignoring Document Updates

**Bad**:
```
We changed the approach but the docs still say the old way.
```

**Good**:
```
Implementation differs from tech-spec.md section 3.

Either:
1. Update tech-spec.md to match implementation, or
2. Refactor implementation to match spec

Create ADR if this is a significant architectural change.
```

---

## Quick Reference

### Prompt Templates

**Implement Feature**:
```
Per [doc] section [X], implement [feature].
Reference [ADR-XXX] for [specific decision].
Success criteria from roadmap.md: [criteria].
```

**Validate Code**:
```
Review against:
- [doc] section [X] ([topic])
- [ADR-XXX] ([decision])
Flag violations.
```

**Update Documents**:
```
Completed [task/decision].
Update:
- [doc]: [what to change]
- [doc]: [what to change]
```

**Start Session**:
```
Load from:
- [doc] sections [X-Y]
- [ADR-XXX]
Continue with [task].
```
