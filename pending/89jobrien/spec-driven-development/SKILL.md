---
name: spec-driven-development
description: Spec-Driven Development (SDD) methodology based on GitHub's SpecKit.
  Use for structured AI-assisted development with constitutional governance, phased
  workflows, and multi-agent coordination. Implements 7-phase process from constitution
  to implementation.
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: skill
type: skill
---

# Spec-Driven Development (SDD)

This skill implements GitHub's SpecKit methodology for structured, AI-assisted software development. SpecKit transforms
specifications into executable artifacts through a systematic, phase-based approach with built-in quality gates and
multi-agent coordination.

## Core Philosophy

**"Specifications become executable, directly generating working implementations rather than just guiding them."**

## When to Use This Skill

- Starting new projects that require structured development
- Coordinating multiple AI agents or developers on complex features
- Ensuring consistent quality through constitutional governance
- Breaking down complex features into manageable, parallel work
- Preventing premature implementation before clear specifications
- Enterprise projects with strict governance requirements
- Teams needing real-time visibility across multiple features

## The 7-Phase Workflow

### Phase 0: Project Initialization

**Purpose:** Create project structure and configure development environment

**Artifacts:**

- `.specify/` directory structure
- Git repository
- Automation scripts
- Templates

**Key Actions:**

- Set up directory structure
- Initialize version control
- Configure AI agent preferences
- Generate script variants (bash/powershell)

### Phase 1: Constitution

**Purpose:** Establish project governance and development principles

**Artifact:** `memory/constitution.md`

**Core Principles:**

1. **Library-First Principle:** Every feature starts as a standalone library
2. **CLI Interface Mandate:** All libraries must have text-based interfaces
3. **Test-First Imperative:** Tests must precede implementation
4. **Simplicity and Anti-Abstraction:** Minimize complexity
5. **Integration-First Testing:** Prioritize realistic testing environments

**Versioning:** Semantic versioning (MAJOR.MINOR.PATCH)

- MAJOR: Backward-incompatible governance changes
- MINOR: New principles or material expansions
- PATCH: Minor clarifications or refinements

**Orchestration:** Interactive principle definition with validation across all artifacts

### Phase 2: Specification

**Purpose:** Create detailed feature specifications focused on WHAT and WHY, not HOW

**Artifact:** `specs/[feature]/spec.md`

**Required Sections:**

- Feature branch name (2-4 words)
- User scenarios (P1, P2, P3 prioritized)
- Acceptance scenarios (Given/When/Then format)
- Edge cases
- Functional requirements (FR-XXX)
- Key entities
- Success criteria (measurable, technology-agnostic)

**Key Constraints:**

- Focus on business value, not implementation
- Write for stakeholders, not developers
- Maximum 3 clarification markers for critical unknowns
- Each user story must be independently testable

**Quality Gates:**

- Content quality validation
- Requirement completeness check
- Feature readiness assessment
- Success criteria measurability

### Phase 3: Clarification

**Purpose:** Systematically identify and resolve ambiguities in specifications

**Artifact:** Updates `specs/[feature]/spec.md`

**Clarification Dimensions:**

- Functional scope
- Data model
- User experience (UX)
- Non-functional attributes (performance, security, etc.)
- Integration points

**Key Constraints:**

- Maximum 5 questions per session
- Multiple-choice or short-answer format
- Focus on high-impact, implementation-critical uncertainties
- One question at a time for iterative refinement

**Orchestration:** Interactive questioning workflow with incremental spec updates after each answer

### Phase 4: Planning

**Purpose:** Create technical implementation strategy and resolve technical unknowns

**Sub-Phases:**

**Phase 0 - Research:**

- Identify and research technical unknowns
- Output: `research.md` with all uncertainties resolved
- **Gate:** ERROR on unresolved clarifications

**Phase 1 - Design:**

- Create data models and API contracts
- Outputs: `data-model.md`, contract schemas, agent-specific context

**Artifacts:**

- `specs/[feature]/plan.md`
- `specs/[feature]/research.md`
- `specs/[feature]/data-model.md`
- `specs/[feature]/contracts/`

**Plan Sections:**

- Feature summary
- Technical context (language, dependencies, platform)
- Project structure
- Repository layout
- Complexity tracking for non-standard approaches

### Phase 5: Analysis

**Purpose:** Validate cross-artifact consistency before implementation

**Artifacts Analyzed:**

- `specs/[feature]/spec.md`
- `specs/[feature]/plan.md`
- `specs/[feature]/tasks.md`

**Detection Passes:**

1. Duplications
2. Ambiguities
3. Underspecified items
4. Constitution conflicts

**Output:** Analysis report with severity-ranked findings (max 50 high-signal issues)

**Key Constraints:**

- Read-only operation (cannot modify files)
- Must run after task breakdown
- Prioritizes constitution principles

### Phase 6: Task Breakdown

**Purpose:** Generate actionable, dependency-ordered task list from plan

**Artifact:** `specs/[feature]/tasks.md`

**Task Structure:**

- Checkbox for completion tracking
- Sequential Task ID
- Optional parallelization marker (`||`)
- Story label (P1, P2, P3 when applicable)
- Precise file path
- Clear description

**Phase Structure:**

1. **Phase 1:** Project Setup
2. **Phase 2:** Foundational Prerequisites (BLOCKING - must complete before user stories)
3. **Phase 3+:** User Story Implementation (priority order: P1 → P2 → P3)
4. **Final Phase:** Polish & Cross-Cutting Concerns

**Key Principles:**

- Tasks grouped by user story for independent implementation
- Each story independently testable and deliverable
- Clear dependency tracking
- Explicit parallelization markers
- No user story work until foundational phase complete

### Phase 7: Implementation

**Purpose:** Execute implementation phase-by-phase with built-in validation

**8-Stage Process:**

1. **Prerequisite Checking:** Validate project readiness
2. **Checklist Validation:** Count completed/incomplete items, require confirmation if incomplete
3. **Context Analysis:** Read required artifacts (tasks.md, plan.md) and optional ones
4. **Project Setup:** Create/verify ignore files for detected technologies
5. **Task Processing:** Parse tasks, extract phases, dependencies, execution flow
6. **Phased Implementation:** Execute tasks phase-by-phase following TDD
7. **Error Handling:** Report progress, handle failures, provide debugging context
8. **Final Validation:** Confirm completion, validate implementation, check test coverage

**Orchestration:** Systematic multi-stage execution with built-in checks and balances

## Orchestration & Parallel Execution

### Core Orchestration Philosophy

**Sequential phase progression with parallel execution within phases where dependencies allow.**

### Coordination Mechanisms

#### 1. Phase-Based Gates

- Each phase must complete and validate before next phase begins
- Gates block on errors or unresolved issues
- Implementation: Template validation, checklist requirements, constitution alignment checks

#### 2. Dependency Tracking

- Tasks marked with dependencies that must be resolved before execution
- Foundational phase blocks all user story work
- Tasks reference prerequisites explicitly

#### 3. Parallelization Markers

- Tasks explicitly marked for parallel execution when no dependencies exist
- Optional `||` marker in task format
- Indicates tasks can run concurrently

#### 4. User Story Grouping

- Tasks grouped by user story for independent, parallel implementation
- Each user story is independently testable and deliverable
- Enables multiple agents/developers to work simultaneously

#### 5. Constitutional Consistency

- All phases reference constitution to maintain consistent practices
- Constitution loaded and validated across all commands
- Ensures alignment across parallel work streams

### Parallel Execution Patterns

#### Pattern 1: User Story Parallelization

After foundational phase completes, user stories (P1, P2, P3) can be implemented in parallel by different agents

**Benefits:**

- Independent testability
- Incremental delivery
- Reduced blocking
- Scalable team coordination

**Example:**

```
Foundation: ✓ Project setup, database schema, auth framework

Parallel Work:
├─ Agent 1: P1 Story - User registration flow
├─ Agent 2: P1 Story - User login flow
└─ Agent 3: P2 Story - Profile management
```

#### Pattern 2: Task-Level Parallelization

Within a phase, tasks without dependencies can execute concurrently

**Example:**

```
Phase 3: P1 User Registration
├─ [ ] T3.1 || Create user model (tests/models/test_user.py)
├─ [ ] T3.2 || Create registration endpoint (tests/api/test_register.py)
└─ [ ] T3.3 || Create validation service (tests/services/test_validation.py)
```

#### Pattern 3: Multi-Agent Coordination

Different AI agents can work on different aspects using shared artifact format

**Example:**

```
Feature "User Authentication":
├─ Claude: Generated spec.md and plan.md (reasoning strength)
├─ Copilot: Implemented auth endpoints (code generation)
└─ Gemini: Wrote integration tests (test coverage)
```

### Synchronization Points

Critical points where parallel work must synchronize:

1. **After constitution:** All subsequent work must align with principles
2. **After specification:** Clarifications must be resolved before planning
3. **After planning research:** All unknowns must be resolved before design
4. **After tasks:** Analysis must validate before implementation
5. **After foundational tasks:** User story work can begin
6. **Within implementation:** Checklist validation blocks execution

## Agent Coordination Patterns

### Pattern 1: Template-Driven Handoffs

Structured markdown templates ensure consistent artifact format across different AI agents

**Benefits:** Agent interoperability, consistent documentation, reduced ambiguity

### Pattern 2: Constitutional Alignment

Constitution acts as shared context across all agents and phases

**Benefits:** Consistent quality standards, predictable behavior, alignment across team/agents

### Pattern 3: Phased Progression

Linear phase progression with clear handoff points between agents

**Benefits:** Clear responsibilities, reduced confusion, quality gates

### Pattern 4: Incremental Refinement

Iterative improvement within phases before moving forward

**Benefits:** Higher quality artifacts, reduced rework, early error detection

### Pattern 5: Artifact-Driven Context

Context passed through artifact references rather than conversation

**Benefits:** Stateless execution, context recovery, long-running projects

## Directory Structure

```
.specify/
├── memory/
│   └── constitution.md          # Project governance and principles
├── scripts/
│   ├── *.sh                     # Bash automation scripts
│   └── *.ps1                    # PowerShell automation scripts
├── specs/
│   └── [feature-name]/
│       ├── spec.md              # Feature specification
│       ├── plan.md              # Technical implementation plan
│       ├── tasks.md             # Actionable task breakdown
│       ├── research.md          # Research findings (optional)
│       ├── data-model.md        # Data structure design (optional)
│       ├── quickstart.md        # Getting started (optional)
│       └── contracts/           # API/interface definitions (optional)
└── templates/                   # Command and artifact templates
```

## Best Practices

1. **Establish constitution early** to guide all subsequent decisions
2. **Use clarify command** to resolve ambiguities before planning
3. **Run analyze command** before implementation to catch issues early
4. **Structure user stories** for independent testability
5. **Mark parallelizable tasks** explicitly with `||`
6. **Complete foundational phase** fully before user story work
7. **Maintain constitution alignment** throughout all phases
8. **Use specific, measurable success criteria** in specifications
9. **Avoid implementation details** in specification phase
10. **Leverage multiple AI agents** for different strengths

## Pitfalls to Avoid

1. Skipping clarification phase leads to ambiguous specifications
2. Premature implementation details in specs reduce flexibility
3. Ignoring constitution causes inconsistent practices
4. Parallel work without proper dependency tracking causes conflicts
5. Incomplete foundational phase blocks all user story work
6. Not running analyze before implementation wastes effort on flawed plans
7. Over-specification in early phases limits AI agent creativity
8. Insufficient success criteria make validation subjective
9. Not using user story grouping limits parallelization potential

## Implementation Scenarios

### Scenario 1: Starting a New Project

Use full 7-phase workflow with constitutional governance. Focus on establishing principles early.

### Scenario 2: Team with Multiple Developers/Agents

Emphasize user story parallelization and worktree isolation. Use dashboard for real-time visibility.

### Scenario 3: Enterprise with Governance Requirements

Comprehensive constitution with enterprise constraints. Mandate analysis phase before implementation.

### Scenario 4: Rapid Prototyping

Detailed specifications to align on vision, but lighter planning. Small user stories for quick validation.

## References

Based on GitHub SpecKit (spec-kit) methodology - an open-source toolkit for Spec-Driven Development supporting 15+ AI
coding agents including Claude Code, GitHub Copilot, Gemini, and Cursor.
