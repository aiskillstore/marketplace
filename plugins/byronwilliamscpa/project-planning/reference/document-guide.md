# Project Planning Document Guide

Comprehensive guidance for creating and maintaining project planning documents.

## Table of Contents

1. [Why These Four Documents](#why-these-four-documents)
2. [Document Relationships](#document-relationships)
3. [Quality Standards](#quality-standards)
4. [Common Pitfalls](#common-pitfalls)
5. [Maintenance Schedule](#maintenance-schedule)

---

## Why These Four Documents

### The Problem They Solve

AI-assisted development fails when:
- Massive context dumps overwhelm the model
- Planning is skipped, leading to architectural drift
- Decisions aren't documented, causing hallucinations
- No clear success criteria exist

### How They Work Together

```
┌─────────────────────────────┐
│   Project Vision & Scope    │  ← WHAT & WHY
│   (Problem, Users, Scope)   │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│  Architecture Decision      │  ← KEY CHOICES
│  Records (ADRs)             │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│  Technical Implementation   │  ← HOW
│  Specification              │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│  Development Roadmap        │  ← WHEN
│  (Phases, Tasks, Criteria)  │
└─────────────────────────────┘
```

---

## Document Relationships

### Project Vision & Scope (PVS)

**Feeds into**:
- ADRs: Technical choices stem from requirements
- Tech Spec: Features define what to implement
- Roadmap: Scope determines work items

**Updated when**:
- Major scope changes
- New success metrics identified
- Quarterly review

### Architecture Decision Records (ADRs)

**Feeds into**:
- Tech Spec: Decisions define implementation approach
- Roadmap: Some decisions require phased migration

**Referenced by**:
- Code comments where decisions are implemented
- Tech Spec for rationale

**Updated when**:
- New architectural decision made
- Previous decision superseded
- Post-implementation review reveals issues

### Technical Implementation Spec

**Feeds into**:
- Roadmap: Components map to work items
- Code: Direct reference during implementation

**References**:
- PVS for requirements context
- ADRs for decision rationale

**Updated when**:
- Architecture changes
- Version upgrades
- Security requirements change

### Development Roadmap

**References**:
- PVS for scope
- Tech Spec for component breakdown
- ADRs for dependencies

**Updated when**:
- After each phase/sprint
- Timeline shifts
- New features added

---

## Quality Standards

### Conciseness

| Document | Target Length | Max Length |
|----------|---------------|------------|
| PVS | 500-800 words | 1000 words |
| ADR (each) | 300-600 words | 800 words |
| Tech Spec | 1000-1500 words | 2000 words |
| Roadmap | 800-1200 words | 1500 words |

### Specificity Checklist

Every document should pass these tests:

- [ ] **No generic boilerplate**: Could this apply to any project? If yes, revise.
- [ ] **Concrete technologies**: "PostgreSQL 16" not "a database"
- [ ] **Measurable criteria**: "< 200ms p95" not "fast"
- [ ] **Explicit scope**: Clear in/out boundaries
- [ ] **Actionable**: Developer can implement from this

### Cross-Reference Standards

Use explicit links between documents:

```markdown
<!-- Good -->
See [ADR-001: Database Choice](./adr/adr-001-database-choice.md) for rationale.
Per [Tech Spec Section 3](./tech-spec.md#3-data-model), use UUID for all IDs.

<!-- Bad -->
See the ADR for more info.
As mentioned elsewhere...
```

---

## Common Pitfalls

### Pitfall 1: Documents Too Generic

**Symptom**: Could apply to any project
**Solution**: Replace every placeholder with project-specific content

**Bad**:
```markdown
### Success Metrics
- Improve user satisfaction
- Reduce errors
```

**Good**:
```markdown
### Success Metrics
- Transaction import time: 30s → 5s (6x improvement)
- Categorization accuracy: Manual → 95% automated
```

### Pitfall 2: Over-Engineering

**Symptom**: Documents longer than code
**Solution**: Focus on decisions and constraints, not exhaustive detail

### Pitfall 3: Inconsistent References

**Symptom**: Documents contradict each other
**Solution**: Generate in order, review for consistency

### Pitfall 4: Missing ADRs

**Symptom**: AI generates inconsistent architectural approaches
**Solution**: Create ADR before implementing any significant component

### Pitfall 5: Outdated Documents

**Symptom**: Code doesn't match specs
**Solution**: Update documents as part of Definition of Done

---

## Maintenance Schedule

### Weekly Updates

- **Roadmap**: Progress on tasks, blockers discovered

### Per-Decision Updates

- **ADR**: Whenever a significant technical choice is made

### Per-Feature Updates

- **Tech Spec**: When new components added
- **PVS**: When scope changes

### Quarterly Review

- **All documents**: Check for currency and accuracy
- **ADRs**: Review for deprecation
- **PVS**: Validate assumptions

---

## Using Documents During Development

### Starting a New Session

```
Load context from:
- PVS sections 2-3 (core features)
- ADR-001, ADR-002 (key decisions)
- Tech Spec section 6 (data model)

Then implement [specific feature].
```

### Validating AI-Generated Code

```
Review this code against:
- Tech Spec section 5 (security requirements)
- ADR-003 (authentication decision)

Flag any violations.
```

### Adding New Features

1. Add user story to Roadmap
2. Update Tech Spec with new components
3. Create ADR if architectural choice required
4. Update PVS if scope changes

---

## Document Storage

### Recommended Structure

```
docs/
└── planning/
    ├── README.md           # Quick start guide
    ├── project-vision.md   # PVS
    ├── tech-spec.md        # Technical spec
    ├── roadmap.md          # Development roadmap
    └── adr/
        ├── README.md       # ADR index
        ├── adr-001-database-choice.md
        ├── adr-002-auth-strategy.md
        └── ...
```

### Version Control

- Commit documents with code changes
- Use conventional commits: `docs: update roadmap with phase 1 results`
- Review document changes in PRs
