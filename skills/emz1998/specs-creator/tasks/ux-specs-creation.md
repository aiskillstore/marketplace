# UX Specs Creation Tasks

## Prerequisites

- PRD must exist at `specs/prd.md`
- Tech specs must exist at `specs/tech-specs.md`

## Tasks

- T001: Verify PRD exists at `specs/prd.md`. If not, stop and inform user to create PRD first.
- T002: Verify tech specs exists at `specs/tech-specs.md`. If not, stop and inform user to create tech specs first.
- T003: Read and analyze PRD at `specs/prd.md` to understand user stories and requirements.
- T004: Read and analyze tech specs at `specs/tech-specs.md` to understand architecture and components.
- T005: Read UX specs template at `.claude/skills/specs-creator/templates/ux.md` for structure compliance.
- T006: Generate UX specs based on PRD and tech specs, save to `specs/ux.md`
- T007: Validate the following sections are present in the UX specs:

  - [ ] **Design Principles**: Core philosophy, design system foundation
  - [ ] **Color System**: Primary colors, semantic colors, theme variations
  - [ ] **Core Architecture**: Main components, dialogs, visual design
  - [ ] **Core Components**: Component styling, states, behavior
  - [ ] **Application Screens**: Screen layouts, sections, interactions
  - [ ] **Responsive Design**: Breakpoints, responsive adaptations
  - [ ] **Accessibility**: Keyboard navigation, ARIA attributes, screen reader support
  - [ ] **Animation & Motion**: Transition timing, animation principles
  - [ ] **Dark Mode**: Theme switching, color adaptations
  - [ ] **Performance Targets**: Critical metrics, optimization strategies
  - [ ] **Design Checklist**: MVP requirements checklist

- T008: Run validation scripts in `.claude/skills/specs-creator/scripts/` for extra compliance checks.
- T009: If validation failed, revise the UX specs and run validation again.
- T010: Report to the user once the UX specs are created successfully.
