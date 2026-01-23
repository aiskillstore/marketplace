# Tech Specs Creation Tasks

## Prerequisites

- PRD must exist at `specs/prd.md`

## Tasks

- T001: Verify PRD exists at `specs/prd.md`. If not, stop and inform user to create PRD first.
- T002: Read and analyze PRD at `specs/prd.md` to understand product requirements.
- T003: Read tech specs template at `.claude/skills/specs-creator/templates/tech.md` for structure compliance.
- T004: Generate tech specs based on PRD and save to `specs/tech-specs.md`
- T005: Validate the following sections are present in the tech specs:

  - [ ] **Overview**: Tech stack, dependencies, deployment, project structure
  - [ ] **Architecture Design**: Component diagram, core architecture, key decisions
  - [ ] **Data Models**: Schema, relationships, indexes, validation
  - [ ] **API/Interface Specifications**: Endpoints, internal APIs
  - [ ] **Authentication & Security**: Auth method, data protection, threat mitigation
  - [ ] **Testing Strategy**: Test types, critical test cases, coverage goals
  - [ ] **Deployment & Operations**: Build process, deployment, monitoring, rollback
  - [ ] **Implementation Details**: Core features, technical decisions, edge cases

- T006: Run validation scripts in `.claude/skills/specs-creator/scripts/` for extra compliance checks.
- T007: If validation failed, revise the tech specs and run validation again.
- T008: Report to the user once the tech specs are created successfully.
