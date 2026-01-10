# Monorepo Team Lead

> Reference doc for nx-monorepo skill. Covers team leadership and ownership structures.

## Overview

This skill provides expert-level (L4) capabilities for team management, code ownership, human-AI collaboration, and cross-team coordination in monorepo environments.

**Skill Level**: Principal (E5/L4)
**Matrix Coverage**: T.* (Team), M.* (Manager Skills)

## Code Ownership

### CODEOWNERS Template

```
# .github/CODEOWNERS

# Domain ownership
/domains/auth/           @team-auth
/domains/content/        @team-content
/domains/ai/             @team-ai

# Platform ownership
/platform/               @team-platform
/infrastructure/         @team-sre

# Critical paths (require senior)
*.lock                   @team-platform
/platform/auth/          @team-auth @security-leads

# AI layer
/.claude/                @team-ai @team-devex
```

### Ownership Principles

```
1. Every file has exactly ONE owner
2. Owners MUST approve PRs to their areas
3. Cross-cutting changes require ALL owners
4. No orphan code (everything is owned)
```

## Human-AI Task Routing

### Decision Matrix

```
HUMAN ONLY:
- Architecture decisions
- Breaking change approval
- Security-critical changes
- Cross-team coordination
- Production deployments

AI-ASSISTED (Human reviews):
- Feature implementation
- Test writing
- Documentation
- Refactoring
- Dependency updates

AI AUTONOMOUS:
- Lint fixes
- Formatting
- Type error fixes
- Simple bug fixes
```

### Routing Decision Tree

```
Task arrives:
├── Strategic? → HUMAN MANAGER
├── Needs judgment? → HUMAN ENGINEER
├── Well-defined & repeatable? → AI AGENT
├── Cross-domain? → HUMAN COORDINATES
└── Default:
    ├── Simple → AI (with review)
    ├── Complex → HUMAN (AI assists)
    └── Production → HUMAN required
```

## Onboarding

### Week 1 Checklist

```markdown
## Day 1-2: Setup
- [ ] Clone and install: pnpm install
- [ ] Verify build: pnpm build
- [ ] Understand structure: ls -la

## Day 3-4: First PR
- [ ] Find "good first issue"
- [ ] Create branch, make change
- [ ] Submit PR, respond to review

## Day 5: Learn System
- [ ] Read CODEOWNERS
- [ ] Understand CI pipeline
- [ ] Know who to ask
```

### Knowledge Transfer

```
KT CHECKLIST:
[ ] Domain architecture explained
[ ] Key files/modules identified
[ ] Common tasks demonstrated
[ ] Gotchas/pitfalls documented
[ ] Contacts for help listed
```

## RFC Process

### RFC Template

```markdown
# RFC: [Title]

## Summary
One paragraph explaining the proposal.

## Motivation
Why? What problem does it solve?

## Design
Technical details.

## Affected Packages
- @myorg/pkg-a: [changes]
- @myorg/pkg-b: [changes]

## Migration
How will existing code migrate?

## Timeline
- Week 1: Implementation
- Week 2: Migration

## Approvals
- [ ] @team-owner
- [ ] @team-affected
```

## Cross-Team Coordination

### Protocol

```
1. CREATE RFC
   - Describe change
   - List affected domains
   - Propose migration

2. GET ALIGNMENT
   - Tag all owners
   - Get written approval

3. IMPLEMENT IN PHASES
   - Add new (no breaking)
   - Migrate consumers
   - Remove old

4. COMMUNICATE
   - Announce in channels
   - Update documentation
```

## Manager Competencies

### AI Work Evaluation

```
EVALUATE AI OUTPUT:
- Does it match requirements?
- Is code subtly wrong?
- Are edge cases handled?
- Is it over-engineered?
- Did it respect boundaries?
```

### Quality Gates

| Gate | AI | Human | Manager |
|------|-----|-------|---------|
| Tests pass | Must | Must | Review |
| Breaking change | Flag | Review | Approve |
| Cross-domain | Flag | Coordinate | Approve |
| Security | Pass | Verify | Approve |

## Quick Reference

```bash
# Ownership
cat .github/CODEOWNERS | grep <path>

# RFC
gh issue create --template=rfc.md

# Onboarding
cat ONBOARDING.md

# Task routing
# Strategic → Human Manager
# Judgment → Human Engineer
# Repeatable → AI Agent
```
