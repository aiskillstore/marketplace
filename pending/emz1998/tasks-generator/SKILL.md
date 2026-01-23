---
name: tasks-generator
description: Generate structured task roadmaps from project specifications. Use when the user asks to create tasks, sprint plans, roadmaps, or work breakdowns based on PRD (Product Requirements Document), Tech Specs, or UI/UX specs. Triggers include requests like "generate tasks from PRD", "create sprint plan", "break down this spec into tasks", "create a roadmap", or "plan the implementation".
---

# Tasks Generator

Generate structured, actionable task roadmaps from project specifications (PRD, Tech Specs, UI/UX Specs).

## Workflow

1. **Gather inputs** - Locate and read PRD, Tech Specs, and UI/UX specs
2. **Analyze specifications** - Extract features, requirements, and dependencies
3. **Generate task breakdown** - Create hierarchical tasks organized by phase/sprint
4. **Apply template** - Format output using `assets/tasks-template.md`
5. **Review dependencies** - Validate task sequencing and parallel opportunities

## Input Requirements

Locate specification documents in these common paths:

- PRD: `.claude/docs/specs/prd.md` or `docs/prd.md`
- Tech Specs: `.claude/docs/specs/tech-specs.md` or `docs/tech-specs.md`
- UI/UX: `.claude/docs/specs/ui-ux.md` or `docs/ui-ux.md`

If documents are missing, prompt user for their locations.

## Task Generation Process

### Step 1: Extract from PRD

Parse the PRD for:

- Core features and user stories → become sprint goals
- MVP requirements → Phase 1/2 priority tasks
- Non-functional requirements → infrastructure/foundation tasks
- Success metrics → verification criteria

### Step 2: Extract from Tech Specs

Parse Tech Specs for:

- Architecture decisions → foundation phase setup tasks
- Data models/schemas → type definition tasks (SPRINT-002)
- API contracts → integration tasks
- Technology stack → environment setup tasks (SPRINT-001)
- Performance requirements → optimization tasks

### Step 3: Extract from UI/UX Specs

Parse UI/UX for:

- Component specifications → UI development tasks
- User flows → feature integration tasks
- Design system requirements → styling/theming tasks
- Accessibility requirements → QA tasks

### Step 4: Organize into Phases

**Phase 1: Foundation** (Always required)

- SPRINT-001: Environment Setup - tooling, dependencies, project structure
- SPRINT-002: Define Contracts/Types - interfaces, schemas, validation

**Phase 2: Build** (Feature development)

- Group related features into sprints
- Order by dependency chain
- Mark parallel tasks with `[P]`

**Phase 3: Deployment**

- CI/CD pipeline setup
- Environment configuration
- Monitoring and observability

## Task ID Convention

Use sequential numbering: `T001`, `T002`, `T003`...

Alternative: Decade-based per sprint: `SPRINT-001: T001-T009`, `SPRINT-002: T010-T019`

Choose one approach consistently.

## Parallel Task Rules

Mark tasks with `[P]` when:

- Task has NO dependencies on other tasks in same sprint
- Task can start immediately when sprint begins
- Multiple `[P]` tasks can run simultaneously

Example:

```
- T001 [P]: Initialize project structure
- T002 [P]: Configure linting
- T003: Install dependencies (depends on T001)
```

## Acceptance Criteria Guidelines

Each sprint must include:

1. **Acceptance Criteria** - Checklist of completion requirements
2. **Verification** - Concrete steps to validate completion

Pattern:

```markdown
**Acceptance Criteria:**
- [ ] [Specific measurable outcome]
- [ ] [Tests pass / coverage requirement]
- [ ] [Integration verified]

**Verification:**
- Run [specific command] and confirm [expected result]
- Demo [specific feature] to verify [behavior]
```

## Output Format

Use the template at `assets/tasks-template.md` for consistent formatting.

Key sections:

- Overview with project metadata
- Roadmap organized by Phase → Sprint → Tasks
- Dependencies and Execution Order
- Parallel Opportunities
- Risks & Blockers

## Task Estimation Heuristics

When specs don't provide estimates:

- Type definitions: 1-2 tasks per domain
- API endpoints: 1 task per endpoint + integration
- UI components: 1 task per major component
- Environment setup: 3-5 tasks standard
- Testing: ~30% of implementation tasks

## References

- For detailed task analysis patterns: see `references/task-analysis.md`
- For output template: see `assets/tasks-template.md`
