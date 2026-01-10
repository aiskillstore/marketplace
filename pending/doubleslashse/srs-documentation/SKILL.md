---
name: srs-documentation
description: Software Requirements Specification documentation following IEEE 830 standard. Use when generating formal SRS documents or compiling gathered requirements into structured documentation.
allowed-tools: Read, Write, Glob
---

# SRS Documentation Skill

## Overview

This skill provides guidance for creating formal Software Requirements Specification (SRS) documents following the IEEE 830 standard structure.

## IEEE 830 Standard Structure

### 1. Introduction

#### 1.1 Purpose
- State the purpose of the SRS document
- Identify the intended audience
- Specify the scope of coverage

#### 1.2 Scope
- Identify the software product by name
- Explain what the software will do
- Describe application benefits, objectives, goals
- Be consistent with related higher-level specs

#### 1.3 Definitions, Acronyms, and Abbreviations
- Define all terms used in the document
- Include technical terms, acronyms, abbreviations
- Reference glossary or appendix if extensive

#### 1.4 References
- List all referenced documents
- Include document titles, numbers, dates, sources
- Identify version or revision information

#### 1.5 Overview
- Describe document organization
- Explain the structure of remaining sections

### 2. Overall Description

#### 2.1 Product Perspective
- **System Context**: How the product fits into the larger ecosystem
- **System Interfaces**: Connections to other systems
- **User Interfaces**: UI considerations and constraints
- **Hardware Interfaces**: Required hardware connections
- **Software Interfaces**: Required software connections
- **Communications Interfaces**: Network and protocol requirements
- **Memory Constraints**: Memory and storage limitations
- **Operations**: Normal and special operations modes
- **Site Adaptation Requirements**: Installation and deployment needs

#### 2.2 Product Functions
- Summary of major functions
- High-level feature overview
- Organized by user or business function

#### 2.3 User Characteristics
- General characteristics of intended users
- Educational level, experience, technical expertise
- Accessibility considerations

#### 2.4 Constraints
- Regulatory requirements
- Hardware limitations
- Interface requirements
- Standards compliance
- Security considerations

#### 2.5 Assumptions and Dependencies
- Factors assumed to be true
- Dependencies on other systems or components
- Conditions that if changed would affect requirements

### 3. Specific Requirements

#### 3.1 External Interface Requirements
- **User Interfaces**: Detailed UI specifications
- **Hardware Interfaces**: Hardware interaction details
- **Software Interfaces**: API and integration details
- **Communications Interfaces**: Protocol specifications

#### 3.2 Functional Requirements
Organized by:
- Feature or function
- User class
- Business object
- Mode of operation
- Stimulus/response sequence

Each requirement should include:
- Unique identifier (FR-XXX)
- Description of functionality
- Inputs and outputs
- Processing logic
- Error handling

#### 3.3 Performance Requirements
- Response time requirements
- Throughput requirements
- Capacity requirements
- Resource utilization limits

#### 3.4 Design Constraints
- Standards compliance
- Hardware limitations
- Software constraints
- Architectural requirements

#### 3.5 Software System Attributes
- **Reliability**: Mean time between failures, recovery
- **Availability**: Uptime requirements
- **Security**: Access control, data protection
- **Maintainability**: Modification ease, documentation
- **Portability**: Platform requirements

#### 3.6 Other Requirements
- Database requirements
- Operations requirements
- Internationalization requirements

### 4. Appendices

#### A. Glossary
Complete list of defined terms

#### B. Analysis Models
- Data flow diagrams
- Entity-relationship diagrams
- State diagrams
- Use case diagrams

#### C. Requirements Traceability Matrix
- Maps requirements to business objectives
- Maps requirements to test cases
- Shows requirement dependencies

## Writing Guidelines

### Requirement Characteristics
Each requirement should be:

| Characteristic | Description | Example |
|---------------|-------------|---------|
| Necessary | Needed for system success | Not nice-to-have |
| Unambiguous | Single interpretation | "User" defined specifically |
| Complete | All information included | Includes error scenarios |
| Consistent | No conflicts | Aligns with other requirements |
| Verifiable | Can be tested | Measurable criteria |
| Traceable | Has clear origin | Links to business need |
| Modifiable | Can be changed easily | Unique ID, no redundancy |
| Prioritized | Ranked by importance | MoSCoW classification |

### Requirement Writing Style

**DO:**
- Use "shall" for mandatory requirements
- Use "should" for desirable requirements
- Use "may" for optional requirements
- Be specific and quantitative
- Use consistent terminology
- Write in active voice
- One requirement per statement

**DON'T:**
- Use vague terms (fast, user-friendly, flexible)
- Use negative requirements when possible
- Combine multiple requirements
- Include design/implementation details
- Use inconsistent terminology

### Examples

**Good Requirement:**
```
FR-001: The system shall display search results within 3 seconds
of the user submitting a search query.
```

**Bad Requirement:**
```
The system should be fast and display results quickly.
```

## Requirement ID Conventions

### Functional Requirements
```
FR-XXX: Core functional requirements
FR-AUTH-XXX: Authentication related
FR-RPT-XXX: Reporting related
FR-INT-XXX: Integration related
```

### Non-Functional Requirements
```
NFR-PERF-XXX: Performance
NFR-SEC-XXX: Security
NFR-REL-XXX: Reliability
NFR-USA-XXX: Usability
NFR-MAINT-XXX: Maintainability
```

### Constraints
```
CON-XXX: General constraints
CON-REG-XXX: Regulatory constraints
CON-TECH-XXX: Technical constraints
```

## Priority Levels

### MoSCoW Method
| Priority | Code | Description |
|----------|------|-------------|
| Must Have | M | Critical for success |
| Should Have | S | Important but not critical |
| Could Have | C | Nice to have |
| Won't Have | W | Out of scope for this release |

### Risk-Based Priority
| Priority | Level | Description |
|----------|-------|-------------|
| Critical | P1 | System cannot function without |
| High | P2 | Major feature impacted |
| Medium | P3 | Minor feature impacted |
| Low | P4 | Enhancement or convenience |

## Document Formatting

### Section Numbering
```
1. Introduction
   1.1 Purpose
   1.2 Scope
2. Overall Description
   2.1 Product Perspective
```

### Requirement Tables
```markdown
| ID | Description | Priority | Status | Source |
|----|-------------|----------|--------|--------|
| FR-001 | User login | M | Approved | Stakeholder Meeting 2024-01-15 |
```

### Cross-References
- Use hyperlinks within document
- Reference by ID: "See FR-001"
- Include traceability: "Implements BR-003"

## Validation Checklist

Before finalizing SRS, verify:

- [ ] All sections of IEEE 830 template completed
- [ ] All requirements have unique identifiers
- [ ] All requirements are verifiable
- [ ] No conflicting requirements
- [ ] All terms defined in glossary
- [ ] Traceability matrix complete
- [ ] Stakeholder sign-off obtained
- [ ] Version control and change history included

See [template.md](template.md) for the complete SRS template.
See [checklists.md](checklists.md) for validation checklists.
