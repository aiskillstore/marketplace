---
name: specs-creator
description: Use PROACTIVELY this skill when you need to create comprehensive PRDs, tech specs, and ux specs based on feature description. If the user specify "Create PRD", "Create Tech Specs", or "Create UX Specs", this skill must be triggered.
---

**Goal**: Create comprehensive PRDs, tech specs, and ux specs based on feature requirements

## Dependency Chain

```
app-vision.md → prd.md → tech-specs.md → ux.md
```

## Workflow

- T001: Read and analyze the appropriate template in `.claude/skills/specs-creator/templates/` for structure compliance
- T002: Analyze feature requirements
- T003: Choose the the appropriate instructions in the `.claude/skills/specs-creator/instructions/`
- T003: Execute the instructions
- T004: Run Validation Scripts in `.claude/skills/specs-creator/scripts/`
- T005: Provide comprehensive report to user with specs details, location, and usage guidance

## Prohibited Tasks

- NEVER create a spec if its dependency doesn't exist yet (see Dependency Chain)
- NEVER write or modify actual code implementation
- NEVER overwrite existing specs without explicit user approval
- DO NOT make architectural decisions beyond documentation scope
- NEVER skip template compliance validation
- DO NOT create specs outside designated `specs/` directory
- NEVER assume requirements without user clarification

## Success Criteria

- All specs follow the template structure in `.claude/skills/specs-creator/templates/`
- Feature requirements are fully captured with no ambiguity
- Validation scripts pass without errors
- Specs are saved to correct location in `specs/`
- User receives clear report with file location and usage guidance

## Template Paths

- **PRD** `.claude/skills/specs-creator/templates/prd.md`
- **Tech Specs** `.claude/skills/specs-creator/templates/tech-specs.md`
- **UX Specs** `.claude/skills/specs-creator/templates/ux.md`
