# Validation Checklists

## SRS Completeness Checklist

### Section 1: Introduction
- [ ] 1.1 Purpose clearly stated
- [ ] 1.2 Scope defined with product name
- [ ] 1.2 Objectives listed
- [ ] 1.2 Benefits described
- [ ] 1.3 All terms defined in glossary
- [ ] 1.3 All acronyms expanded
- [ ] 1.4 All referenced documents listed
- [ ] 1.5 Document structure overview provided

### Section 2: Overall Description
- [ ] 2.1.1 System context described
- [ ] 2.1.2 System interfaces identified
- [ ] 2.1.3 User interface requirements stated
- [ ] 2.1.4 Hardware interfaces listed (if applicable)
- [ ] 2.1.5 Software interfaces listed
- [ ] 2.1.6 Communication interfaces specified
- [ ] 2.2 Product functions summarized
- [ ] 2.3 User classes/characteristics defined
- [ ] 2.4 Constraints documented
- [ ] 2.5 Assumptions listed
- [ ] 2.5 Dependencies identified

### Section 3: Specific Requirements
- [ ] 3.1 All external interfaces detailed
- [ ] 3.2 All functional requirements documented
- [ ] 3.2 Each FR has unique identifier
- [ ] 3.2 Each FR has priority assigned
- [ ] 3.2 Each FR has acceptance criteria
- [ ] 3.3 Performance requirements specified
- [ ] 3.3 Security requirements specified
- [ ] 3.3 Reliability requirements specified
- [ ] 3.3 Usability requirements specified
- [ ] 3.3 Maintainability requirements specified
- [ ] 3.4 Design constraints documented
- [ ] 3.5 Database requirements documented (if applicable)
- [ ] 3.5 Internationalization requirements documented (if applicable)

### Appendices
- [ ] Glossary complete
- [ ] Analysis models included (DFD, ERD, etc.)
- [ ] Traceability matrix complete
- [ ] Stakeholder sign-off section included

---

## Requirement Quality Checklist (SMART)

For each requirement, verify:

### S - Specific
- [ ] Requirement is clear and precise
- [ ] No ambiguous terms used
- [ ] "User" and other actors clearly defined
- [ ] Scope is bounded

### M - Measurable
- [ ] Success criteria can be verified
- [ ] Quantitative metrics where applicable
- [ ] Test method is clear

### A - Achievable
- [ ] Technically feasible
- [ ] Resources available
- [ ] Within project constraints

### R - Relevant
- [ ] Traces to business objective
- [ ] Provides value to stakeholders
- [ ] Aligned with project goals

### T - Time-bound
- [ ] Has timeline context
- [ ] Priority is assigned
- [ ] Phase/release is identified

---

## User Story Quality Checklist (INVEST)

For each user story, verify:

### I - Independent
- [ ] Can be developed separately from other stories
- [ ] No blocking dependencies
- [ ] Self-contained

### N - Negotiable
- [ ] Open to discussion with stakeholders
- [ ] Not over-specified
- [ ] Allows for solution flexibility

### V - Valuable
- [ ] Delivers value to user or business
- [ ] "So that" clause is meaningful
- [ ] Benefit is clear

### E - Estimable
- [ ] Enough detail to size
- [ ] Technical approach is understood
- [ ] Dependencies are known

### S - Small
- [ ] Can be completed in one sprint
- [ ] Not too large to estimate
- [ ] Scope is appropriate

### T - Testable
- [ ] Has clear acceptance criteria
- [ ] Pass/fail can be determined
- [ ] Test scenarios can be written

---

## Functional Requirement Checklist

For each functional requirement, verify:

### Identification
- [ ] Unique ID assigned (FR-XXX)
- [ ] Title is descriptive
- [ ] Category/feature area identified

### Description
- [ ] Uses "shall" for mandatory requirements
- [ ] Single requirement per statement
- [ ] Active voice used
- [ ] No implementation details included

### Completeness
- [ ] Inputs specified
- [ ] Processing logic described
- [ ] Outputs defined
- [ ] Error handling addressed
- [ ] Edge cases considered

### Traceability
- [ ] Source/origin documented
- [ ] Business objective linked
- [ ] Related requirements referenced
- [ ] Test cases mapped (or will be)

### Status
- [ ] Priority assigned (M/S/C/W)
- [ ] Status tracked (Proposed/Approved/etc.)
- [ ] Stakeholder ownership identified

---

## Non-Functional Requirement Checklist

For each NFR, verify:

### Performance Requirements
- [ ] Response time specified with metrics
- [ ] Throughput requirements quantified
- [ ] Concurrent user capacity defined
- [ ] Resource utilization limits set

### Security Requirements
- [ ] Authentication method specified
- [ ] Authorization levels defined
- [ ] Data encryption requirements stated
- [ ] Audit logging requirements documented
- [ ] Compliance standards referenced

### Reliability Requirements
- [ ] Availability target specified (e.g., 99.9%)
- [ ] Recovery time objective (RTO) defined
- [ ] Recovery point objective (RPO) defined
- [ ] Failure handling described

### Usability Requirements
- [ ] User skill level considered
- [ ] Accessibility standards referenced (WCAG)
- [ ] Error message guidelines provided
- [ ] Help/documentation requirements stated

### Maintainability Requirements
- [ ] Code standards referenced
- [ ] Documentation requirements stated
- [ ] Logging/monitoring requirements defined
- [ ] Update/deployment requirements specified

---

## Traceability Matrix Checklist

### Business Objective Tracing
- [ ] All business objectives have at least one requirement
- [ ] No orphan requirements (without business justification)
- [ ] Priorities align with business value

### Requirement Dependencies
- [ ] All dependencies identified
- [ ] No circular dependencies
- [ ] Critical path requirements flagged

### Test Coverage Tracing
- [ ] All requirements have test cases planned
- [ ] High-priority requirements have multiple test scenarios
- [ ] Negative test cases identified

---

## Document Quality Checklist

### Consistency
- [ ] Terminology consistent throughout
- [ ] Formatting consistent
- [ ] ID numbering consistent
- [ ] Priority scheme consistent

### Completeness
- [ ] All template sections completed
- [ ] No TBD items remaining
- [ ] All cross-references valid

### Correctness
- [ ] No contradicting requirements
- [ ] No duplicate requirements
- [ ] References accurate

### Clarity
- [ ] Language is clear and professional
- [ ] Technical terms defined
- [ ] Diagrams support text

---

## Validation Report Scoring

### Completeness Score Calculation

```
Section Weights:
- Introduction: 10%
- Overall Description: 20%
- Functional Requirements: 35%
- Non-Functional Requirements: 25%
- Appendices: 10%

Score = Sum of (Section % Complete * Section Weight)
```

### Quality Score Calculation

```
Quality Factors:
- SMART Compliance: 30%
- Traceability: 25%
- Consistency: 20%
- Clarity: 15%
- Stakeholder Confirmation: 10%

Score = Sum of (Factor % Achieved * Factor Weight)
```

### Status Thresholds

| Score | Status | Action |
|-------|--------|--------|
| 90-100% | Excellent | Ready for approval |
| 75-89% | Good | Minor revisions needed |
| 60-74% | Fair | Significant revisions needed |
| Below 60% | Poor | Major rework required |

---

## Quick Validation Questions

Before finalizing any requirements artifact, ask:

1. **Who** is this requirement for? (Stakeholder identified)
2. **What** must the system do? (Functionality clear)
3. **Why** is this needed? (Business value traced)
4. **When** is this needed? (Priority assigned)
5. **How** will we know it's done? (Acceptance criteria defined)
6. **Is this testable?** (Verification method clear)
7. **Any conflicts?** (Consistency checked)
8. **Confirmed by stakeholder?** (Sign-off obtained)
