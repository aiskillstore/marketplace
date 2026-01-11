---
name: requirements-elicitation
description: Requirements gathering and elicitation techniques for business analysis. Use when conducting stakeholder interviews, gathering functional/non-functional requirements, or identifying gaps in requirements.
allowed-tools: Read, Grep, Glob, AskUserQuestion, Write
---

# Requirements Elicitation Skill

## Overview

This skill provides structured techniques for gathering, analyzing, and documenting software requirements from stakeholders and existing systems.

## Elicitation Techniques

### 1. Structured Interviews
Use predefined question sets organized by category:
- Start with open-ended questions to understand context
- Follow with specific questions to gather details
- End with validation questions to confirm understanding

### 2. Adaptive Questioning
Dynamically adjust questions based on:
- Previous answers provided
- Domain context discovered
- Gaps identified in requirements
- Stakeholder role and expertise level

### 3. Document Analysis
Extract requirements from existing:
- Business process documents
- User manuals
- Training materials
- Support tickets and feedback

### 4. Observation
Understand requirements by observing:
- Current system usage
- User workflows
- Pain points and workarounds

## Requirement Categories

### Functional Requirements (FR)
What the system must DO:
- Features and capabilities
- Business rules and logic
- Data processing requirements
- User interactions

### Non-Functional Requirements (NFR)
How the system must BEHAVE:

#### FURPS+ Model
- **Functionality**: Security, compliance
- **Usability**: Accessibility, learnability
- **Reliability**: Availability, fault tolerance
- **Performance**: Response time, throughput
- **Supportability**: Maintainability, testability
- **+Constraints**: Design, implementation, interface

### Constraints
Limitations on the solution:
- Budget constraints
- Timeline constraints
- Technology constraints
- Regulatory constraints
- Resource constraints

### Assumptions
Conditions assumed to be true:
- User capabilities
- Infrastructure availability
- Third-party dependencies
- Business conditions

## Prioritization Methods

### MoSCoW Method
- **Must Have**: Critical for success, non-negotiable
- **Should Have**: Important but not critical
- **Could Have**: Nice to have, low impact if absent
- **Won't Have**: Out of scope for current release

### Value vs Effort Matrix
```
High Value + Low Effort  = Do First (Quick Wins)
High Value + High Effort = Do Second (Major Projects)
Low Value + Low Effort   = Do Later (Fill-ins)
Low Value + High Effort  = Don't Do (Time Wasters)
```

## Gap Analysis Process

1. **Document As-Is State**: Current capabilities
2. **Define To-Be State**: Desired capabilities
3. **Identify Gaps**: Missing capabilities
4. **Prioritize Gaps**: By business value
5. **Create Requirements**: To close gaps

## Validation Techniques

### Requirement Quality Checks
Each requirement should be:
- **Complete**: All necessary information included
- **Consistent**: No conflicts with other requirements
- **Unambiguous**: Single clear interpretation
- **Verifiable**: Can be tested/measured
- **Traceable**: Linked to business objective

### SMART Criteria
- **S**pecific: Clear and precise
- **M**easurable: Quantifiable success criteria
- **A**chievable: Technically feasible
- **R**elevant: Aligned with business goals
- **T**ime-bound: Has timeline context

### INVEST Criteria (for User Stories)
- **I**ndependent: Can be developed separately
- **N**egotiable: Open to discussion
- **V**aluable: Delivers user/business value
- **E**stimable: Can be sized
- **S**mall: Fits in a sprint
- **T**estable: Has clear acceptance criteria

## Stakeholder Analysis

### Stakeholder Categories
1. **End Users**: Direct system users
2. **Business Owners**: Decision makers
3. **Technical Team**: Developers, architects
4. **Operations**: Support, maintenance
5. **External**: Regulators, partners, customers

### Stakeholder Mapping
For each stakeholder identify:
- Role and responsibilities
- Interest level (High/Medium/Low)
- Influence level (High/Medium/Low)
- Key concerns and priorities
- Communication preferences

## Output Artifacts

### Requirements List
```markdown
| ID | Category | Description | Priority | Status |
|----|----------|-------------|----------|--------|
| FR-001 | Functional | User can login with email | Must | Confirmed |
| NFR-001 | Performance | Page load < 3 seconds | Should | Pending |
```

### User Story Format
```
As a [role]
I want [capability]
So that [business value]

Acceptance Criteria:
- Given [context]
- When [action]
- Then [outcome]
```

### Requirement Traceability
```
Business Objective -> Requirement -> User Story -> Test Case
```

See [question-templates.md](question-templates.md) for structured interview questions.
