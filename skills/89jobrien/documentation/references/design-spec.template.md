---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: reference
parent: documentation
---

# Design Specification: {{FEATURE_NAME}}

**Author:** {{NAME}}
**Date:** {{YYYY-MM-DD}}
**Status:** {{DRAFT|REVIEW|APPROVED|IMPLEMENTED}}
**Reviewers:** {{NAMES}}

---

## Overview

### Problem Statement

{{WHAT_PROBLEM_ARE_WE_SOLVING}}

### Goals

- {{GOAL_1}}
- {{GOAL_2}}
- {{GOAL_3}}

### Non-Goals

- {{NON_GOAL_1}}
- {{NON_GOAL_2}}

---

## Background

### Context

{{RELEVANT_BACKGROUND_INFO}}

### Current State

{{HOW_THINGS_WORK_TODAY}}

### User Research / Requirements

| Requirement | Source | Priority |
|-------------|--------|----------|
| {{REQ_1}} | {{SOURCE}} | {{P0-P3}} |
| {{REQ_2}} | {{SOURCE}} | {{P0-P3}} |

---

## Proposed Solution

### High-Level Design

{{SOLUTION_OVERVIEW}}

```
{{ARCHITECTURE_DIAGRAM}}
```

### User Flow

1. User {{ACTION_1}}
2. System {{RESPONSE_1}}
3. User {{ACTION_2}}
4. System {{RESPONSE_2}}

### Data Model

```{{LANGUAGE}}
{{DATA_STRUCTURES}}
```

### API Design

#### {{ENDPOINT_NAME}}

```
{{METHOD}} {{PATH}}
```

**Request:**

```json
{{REQUEST_BODY}}
```

**Response:**

```json
{{RESPONSE_BODY}}
```

---

## Detailed Design

### Component 1: {{COMPONENT_NAME}}

**Purpose:** {{PURPOSE}}

**Implementation:**

```{{LANGUAGE}}
{{CODE_SAMPLE}}
```

**Interactions:**

- Receives: {{INPUT}}
- Produces: {{OUTPUT}}
- Depends on: {{DEPENDENCIES}}

---

### Component 2: {{COMPONENT_NAME}}

**Purpose:** {{PURPOSE}}

**Implementation:**

{{DESCRIPTION}}

---

### State Management

| State | Type | Initial | Transitions |
|-------|------|---------|-------------|
| {{STATE}} | {{TYPE}} | {{VALUE}} | {{TRANSITIONS}} |

### Error Handling

| Error Case | Handling | User Message |
|------------|----------|--------------|
| {{ERROR}} | {{HANDLING}} | {{MESSAGE}} |

---

## Alternatives Considered

### Alternative 1: {{NAME}}

{{DESCRIPTION}}

**Pros:**

- {{PRO}}

**Cons:**

- {{CON}}

**Why Not:** {{REASON}}

---

### Alternative 2: {{NAME}}

{{DESCRIPTION}}

**Why Not:** {{REASON}}

---

## Security Considerations

### Threats

| Threat | Risk | Mitigation |
|--------|------|------------|
| {{THREAT}} | {{H/M/L}} | {{MITIGATION}} |

### Data Privacy

- {{PRIVACY_CONSIDERATION_1}}
- {{PRIVACY_CONSIDERATION_2}}

---

## Performance Considerations

### Expected Load

| Metric | Expected | Peak |
|--------|----------|------|
| Requests/sec | {{N}} | {{N}} |
| Response Time | {{MS}}ms | {{MS}}ms |

### Scalability

{{HOW_SOLUTION_SCALES}}

### Caching Strategy

{{CACHING_APPROACH}}

---

## Testing Strategy

### Unit Tests

- {{TEST_CASE_1}}
- {{TEST_CASE_2}}

### Integration Tests

- {{TEST_CASE_1}}
- {{TEST_CASE_2}}

### Edge Cases

- {{EDGE_CASE_1}}
- {{EDGE_CASE_2}}

---

## Rollout Plan

### Phase 1: {{PHASE_NAME}}

- {{DELIVERABLE}}
- Audience: {{WHO}}

### Phase 2: {{PHASE_NAME}}

- {{DELIVERABLE}}
- Audience: {{WHO}}

### Feature Flags

| Flag | Purpose | Default |
|------|---------|---------|
| `{{FLAG}}` | {{PURPOSE}} | {{VALUE}} |

### Rollback Criteria

- {{ROLLBACK_TRIGGER_1}}
- {{ROLLBACK_TRIGGER_2}}

---

## Monitoring & Observability

### Metrics

| Metric | Purpose | Alert Threshold |
|--------|---------|-----------------|
| {{METRIC}} | {{PURPOSE}} | {{THRESHOLD}} |

### Logging

| Event | Level | Data |
|-------|-------|------|
| {{EVENT}} | {{INFO/WARN/ERROR}} | {{DATA}} |

### Dashboards

- {{DASHBOARD_1}}
- {{DASHBOARD_2}}

---

## Dependencies

### External Dependencies

| Dependency | Purpose | Owner |
|------------|---------|-------|
| {{DEP}} | {{PURPOSE}} | {{OWNER}} |

### Internal Dependencies

- {{INTERNAL_DEP_1}}
- {{INTERNAL_DEP_2}}

---

## Open Questions

1. {{QUESTION_1}}
2. {{QUESTION_2}}

---

## Timeline

| Milestone | Date |
|-----------|------|
| Design Review | {{DATE}} |
| Implementation Start | {{DATE}} |
| Testing Complete | {{DATE}} |
| Rollout | {{DATE}} |

---

## References

- [{{DOC_1}}]({{URL}})
- [{{DOC_2}}]({{URL}})

---

## Quality Checklist

- [ ] Problem clearly stated
- [ ] Goals and non-goals defined
- [ ] Alternatives considered
- [ ] Security reviewed
- [ ] Performance considered
- [ ] Testing strategy defined
- [ ] Rollout plan documented
- [ ] Monitoring planned
