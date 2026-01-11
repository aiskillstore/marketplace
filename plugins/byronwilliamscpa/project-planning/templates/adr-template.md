# Architecture Decision Record Template

## Structure

```markdown
# ADR-[NNN]: [Decision Title]

> **Status**: Proposed | Accepted | Deprecated | Superseded
> **Date**: [YYYY-MM-DD]
> **Supersedes**: [ADR-XXX] (if applicable)

## TL;DR
[One sentence: What was decided and the primary reason]

## Context

### Problem
[What technical challenge requires a decision?]

### Constraints
- **Technical**: [Existing systems, limitations]
- **Business**: [Time, budget, resources]

### Significance
[Why is this architecturally significant? Cost of getting it wrong?]

## Decision

**We will use [CHOICE] because [PRIMARY REASON].**

### Rationale
[Why this option over alternatives - key criteria]

## Options Considered

### Option 1: [Chosen Solution] ✓
**Pros**:
- ✅ [Advantage]
- ✅ [Advantage]

**Cons**:
- ❌ [Limitation]

### Option 2: [Alternative]
**Pros**:
- ✅ [Advantage]

**Cons**:
- ❌ [Why not chosen]
- ❌ [Limitation]

### Option 3: [Alternative]
[Brief assessment]

## Consequences

### Positive
- ✅ [Benefit]: [Impact]
- ✅ [Benefit]: [Impact]

### Trade-offs
- ⚠️ [Trade-off]: [Mitigation]

### Technical Debt
- [Debt item]: [What to address later]

## Implementation

### Components Affected
1. **[Component]**: [What changes]
2. **[Component]**: [What changes]

### Testing Strategy
- Unit: [Coverage requirements]
- Integration: [Key scenarios]

## Validation

### Success Criteria
- [ ] [Measurable outcome]
- [ ] [Measurable outcome]

### Review Schedule
- Initial: [Date/milestone]
- Ongoing: [Frequency]

## Related
- [ADR-XXX](./adr-xxx.md): [Relationship]
- [Tech Spec Section](../tech-spec.md#section): [Reference]
```

## Generation Notes

- One ADR per decision (not mega-documents)
- Number sequentially: ADR-001, ADR-002
- Always include alternatives considered
- Be honest about trade-offs
- Keep under 600 words per ADR

## Common Initial ADRs

For new projects, typically create:
1. `adr-001-database-choice.md` - Storage strategy
2. `adr-002-auth-strategy.md` - Authentication approach (if applicable)
3. `adr-003-api-design.md` - API patterns (if applicable)
