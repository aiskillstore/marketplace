# PRD Creation Tasks

## Prerequisites

- App vision must exist at `specs/app-vision.md`

## Tasks

- T001: Verify app-vision.md exists at `specs/app-vision.md`. If not, stop and inform user to create app vision first.
- T002: Read and analyze app-vision.md to understand product vision and goals.
- T003: Read PRD template at `.claude/skills/specs-creator/templates/PRD.md` for structure compliance.
- T004: Generate PRD based on app-vision.md and save to `specs/prd.md`
- T005: Validate the following sections are present in the PRD:

  - [ ] **Overview**: Problem statement and solution summary
  - [ ] **Goals**: Primary and secondary objectives
  - [ ] **User Stories**: As a [user], I want [feature], so that [benefit]
  - [ ] **Requirements**: Functional and non-functional requirements
  - [ ] **Scope**: In-scope and out-of-scope items
  - [ ] **Success Metrics**: Measurable outcomes

- T006: Run validation scripts in `.claude/skills/specs-creator/scripts/` for extra compliance checks.
- T007: If validation failed, revise the PRD and run validation again.
- T008: Report to the user once the PRD is created successfully.
