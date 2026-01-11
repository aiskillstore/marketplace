# Development Roadmap Template

## Structure

```markdown
# Development Roadmap: [Project Name]

> **Status**: Active | **Updated**: [Date]

## TL;DR
[One sentence: What we're building, in what order, target completion]

## Timeline Overview

```
Phase 0: Foundation    ████████░░░░░░░░ (1 week)  - Setup
Phase 1: MVP Core      ░░░░░░░░████████ (3 weeks) - Core features
Phase 2: Enhancement   ░░░░░░░░░░░░░░░░ (2 weeks) - Additional features
Phase 3: Polish        ░░░░░░░░░░░░░░░░ (1 week)  - Testing & docs
```

## Milestones

| Milestone | Target | Status | Dependencies |
|-----------|--------|--------|--------------|
| M0: Dev Environment | [Date] | ⏸️ Planned | None |
| M1: [Core Feature] | [Date] | ⏸️ Planned | M0 |
| M2: [Core Feature] | [Date] | ⏸️ Planned | M1 |
| M3: MVP Complete | [Date] | ⏸️ Planned | M2 |

---

## Phase 0: Foundation (Week 1)

### Objective
Establish development environment and core infrastructure.

### Deliverables
- [ ] Development environment documented and working
- [ ] CI/CD pipeline configured
- [ ] Project structure finalized
- [ ] Dependencies locked

### Success Criteria
- ✅ Clone → run locally in < 15 minutes
- ✅ CI pipeline passes on main branch
- ✅ Pre-commit hooks working

### Tasks
| Task | Est. Hours | Status |
|------|------------|--------|
| Configure UV and dependencies | 2 | ⏸️ |
| Set up pre-commit hooks | 1 | ⏸️ |
| Configure CI workflow | 2 | ⏸️ |
| Write local dev guide | 1 | ⏸️ |

---

## Phase 1: MVP Core (Weeks 2-4)

### Objective
Implement minimum viable product with core user workflows.

### Deliverables
- [ ] [Core Feature 1]: [Brief description]
- [ ] [Core Feature 2]: [Brief description]
- [ ] [Core Feature 3]: [Brief description]

### Success Criteria
- ✅ [Testable criterion for feature 1]
- ✅ [Testable criterion for feature 2]
- ✅ [Testable criterion for feature 3]

### User Stories

#### US-001: [Story Title]
**As a** [user type]
**I want** [capability]
**So that** [benefit]

**Acceptance Criteria**:
- [ ] [Specific condition]
- [ ] [Specific condition]

**Tasks**:
| Task | Est. Hours | Status |
|------|------------|--------|
| [Implementation task] | [X] | ⏸️ |
| [Test task] | [X] | ⏸️ |

#### US-002: [Story Title]
[Repeat format]

### Dependencies
- Requires: Phase 0 complete
- Blocks: Phase 2

---

## Phase 2: Enhancement (Weeks 5-6)

### Objective
Add additional features beyond MVP.

### Deliverables
- [ ] [Enhancement 1]
- [ ] [Enhancement 2]

### Success Criteria
- ✅ [Testable criterion]
- ✅ [Testable criterion]

### User Stories
[Same format as Phase 1]

---

## Phase 3: Polish (Week 7)

### Objective
Finalize testing, documentation, and release preparation.

### Deliverables
- [ ] Test coverage ≥ [X]%
- [ ] Documentation complete
- [ ] Performance validated
- [ ] Security review complete

### Success Criteria
- ✅ All tests passing
- ✅ No critical/high security issues
- ✅ README covers all usage
- ✅ CHANGELOG updated

### Tasks
| Task | Est. Hours | Status |
|------|------------|--------|
| Increase test coverage | 4 | ⏸️ |
| Write user documentation | 4 | ⏸️ |
| Performance testing | 2 | ⏸️ |
| Security review | 2 | ⏸️ |

---

## Risk Register

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| [Risk description] | M | H | [Strategy] |
| [Risk description] | L | M | [Strategy] |

## Definition of Done

A feature is complete when:
- [ ] Code reviewed and approved
- [ ] Tests written and passing
- [ ] Documentation updated
- [ ] No linting errors
- [ ] Merged to main

## Related Documents
- [Project Vision](./project-vision.md)
- [Technical Spec](./tech-spec.md)
- [Architecture Decisions](./adr/)
```

## Generation Notes

- Break into testable phases
- Each phase has clear exit criteria
- Tasks should be < 1 day each
- Include realistic time estimates
- Mark dependencies between phases
- Keep under 1200 words
