---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: reference
parent: technical-research
---

# Technical Spike: {{SPIKE_TITLE}}

**Ticket:** {{TICKET_ID}}
**Date:** {{YYYY-MM-DD}}
**Engineer:** {{NAME}}
**Timebox:** {{HOURS}} hours

---

## Objective

{{WHAT_ARE_WE_TRYING_TO_LEARN}}

### Questions to Answer

1. {{QUESTION_1}}
2. {{QUESTION_2}}
3. {{QUESTION_3}}

### Success Criteria

- [ ] {{CRITERION_1}}
- [ ] {{CRITERION_2}}
- [ ] {{CRITERION_3}}

---

## Background

### Context

{{WHY_IS_THIS_SPIKE_NEEDED}}

### Constraints

- {{CONSTRAINT_1}}
- {{CONSTRAINT_2}}

### Assumptions

- {{ASSUMPTION_1}}
- {{ASSUMPTION_2}}

---

## Options Explored

### Option 1: {{OPTION_NAME}}

**Description:** {{BRIEF_DESCRIPTION}}

**Proof of Concept:**

```{{LANGUAGE}}
{{CODE_SAMPLE}}
```

**Findings:**

- {{FINDING_1}}
- {{FINDING_2}}

**Pros:**

- {{PRO_1}}
- {{PRO_2}}

**Cons:**

- {{CON_1}}
- {{CON_2}}

**Effort Estimate:** {{LOW/MEDIUM/HIGH}}

---

### Option 2: {{OPTION_NAME}}

**Description:** {{BRIEF_DESCRIPTION}}

**Proof of Concept:**

```{{LANGUAGE}}
{{CODE_SAMPLE}}
```

**Findings:**

- {{FINDING_1}}

**Pros:**

- {{PRO_1}}

**Cons:**

- {{CON_1}}

**Effort Estimate:** {{LOW/MEDIUM/HIGH}}

---

### Option 3: {{OPTION_NAME}}

**Description:** {{BRIEF_DESCRIPTION}}

**Findings:**

- {{FINDING_1}}

**Verdict:** {{VIABLE/NOT_VIABLE}}

---

## Comparison Matrix

| Criteria | Weight | Option 1 | Option 2 | Option 3 |
|----------|--------|----------|----------|----------|
| {{CRITERIA_1}} | {{1-5}} | {{SCORE}} | {{SCORE}} | {{SCORE}} |
| {{CRITERIA_2}} | {{1-5}} | {{SCORE}} | {{SCORE}} | {{SCORE}} |
| {{CRITERIA_3}} | {{1-5}} | {{SCORE}} | {{SCORE}} | {{SCORE}} |
| **Weighted Total** | - | {{TOTAL}} | {{TOTAL}} | {{TOTAL}} |

---

## Recommendation

**Recommended Option:** {{OPTION_NAME}}

### Rationale

{{WHY_THIS_OPTION}}

### Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| {{RISK_1}} | {{H/M/L}} | {{H/M/L}} | {{STRATEGY}} |
| {{RISK_2}} | {{H/M/L}} | {{H/M/L}} | {{STRATEGY}} |

### Dependencies

- {{DEPENDENCY_1}}
- {{DEPENDENCY_2}}

---

## Implementation Path

### Phase 1: {{PHASE_NAME}}

- {{TASK_1}}
- {{TASK_2}}

### Phase 2: {{PHASE_NAME}}

- {{TASK_1}}
- {{TASK_2}}

### Estimated Effort

| Component | Estimate |
|-----------|----------|
| {{COMPONENT_1}} | {{POINTS/DAYS}} |
| {{COMPONENT_2}} | {{POINTS/DAYS}} |
| **Total** | {{TOTAL}} |

---

## Open Questions

1. {{UNANSWERED_QUESTION_1}}
2. {{UNANSWERED_QUESTION_2}}

---

## References

- [{{DOC_1}}]({{URL}})
- [{{DOC_2}}]({{URL}})

### Code Artifacts

- Branch: `spike/{{BRANCH_NAME}}`
- POC Location: `{{PATH}}`

---

## Answers to Original Questions

| Question | Answer |
|----------|--------|
| {{QUESTION_1}} | {{ANSWER}} |
| {{QUESTION_2}} | {{ANSWER}} |
| {{QUESTION_3}} | {{ANSWER}} |

---

## Quality Checklist

- [ ] All original questions answered
- [ ] Multiple options explored
- [ ] POC code tested
- [ ] Recommendation justified
- [ ] Risks identified
- [ ] Implementation path clear
- [ ] Timeboxed appropriately
