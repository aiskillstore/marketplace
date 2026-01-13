# Project Creator Templates

This folder contains templates used by the project-creator skill to generate CCGG Business Operations projects.

## Templates

### CLAUDE_SIMPLE.md
Standard project CLAUDE.md template with PARENT SYSTEM INTEGRATION.

**When to use**: Projects that don't coordinate with other projects (most projects).

**Variables to replace**:
- `{{PROJECT_NAME}}` - Hyphen-case project name
- `{{PROJECT_TITLE}}` - Human-readable title
- `{{PROJECT_TYPE}}` - Type (incubator-program, active-program, etc.)
- `{{CREATED_DATE}}` - YYYY-MM-DD format
- `{{PROJECT_PURPOSE}}` - 1-2 sentence purpose
- `{{CORE_FOCUS_ITEMS}}` - Bullet list of focus areas
- `{{IN_SCOPE_ITEMS}}` - What's included
- `{{OUT_OF_SCOPE_ITEMS}}` - What's not included
- `{{OOBG_ALIGNMENT}}` - How this serves OOBG
- `{{UV_ALIGNMENT}}` - How this leverages Unique Vehicle
- `{{AVATAR_TARGETING}}` - Which avatars benefit
- `{{RELATED_PROJECTS}}` - Links to related projects
- `{{FOLDER_STRUCTURE}}` - Project folder tree
- `{{DELIVERABLES_LIST}}` - Phased deliverables list
- `{{PROJECT_SUCCESS_CRITERIA}}` - How to measure success
- `{{BUSINESS_IMPACT_CRITERIA}}` - Post-implementation impact
- `{{MISSION_STATEMENT}}` - One-sentence mission

### CLAUDE_COMPLEX.md
Complex project template with Coordination Hub support.

**When to use**: Projects that coordinate with 2+ other projects.

**Additional variables**:
- `{{UPSTREAM_DEPENDENCIES}}` - Projects this depends on (with status, blockers)
- `{{DOWNSTREAM_DEPENDENCIES}}` - Projects that depend on this
- `{{DEPENDENCY_CHAIN_DESCRIPTION}}` - How dependencies flow
- `{{INTEGRATION_POINTS}}` - Where projects connect
- `{{INTEGRATION_SUCCESS_CRITERIA}}` - How to measure coordination success

### PHASE_TRACKER_TEMPLATE.md
Multi-phase project tracker template.

**When to use**: Projects with 2+ phases (test → validate, MVP → production, etc.)

**Variables to replace**:
- `{{PROJECT_NAME}}` - Hyphen-case project name
- `{{PROJECT_TITLE}}` - Human-readable title
- `{{CREATED_DATE}}` - YYYY-MM-DD format
- `{{PHASE_1_NAME}}` - Phase 1 name (e.g., "Setup & Test")
- `{{PHASE_1_GOAL}}` - What Phase 1 accomplishes
- `{{PHASE_1_DURATION}}` - Time estimate (e.g., "4 weeks")
- `{{PHASE_1_TARGET_DATES}}` - Date range (e.g., "Nov 7 - Dec 7, 2025")
- `{{PHASE_1_CRITERIA}}` - Completion criteria checklist
- `{{PHASE_1_DELIVERABLES}}` - Deliverables checklist
- `{{PHASE_1_REMINDER_LOGIC}}` - How Claude reminds weekly
- `{{PHASE_1_TRANSITION_TRIGGER}}` - When to prompt Phase 2
- `{{PHASE_1_NEXT_TRIGGER}}` - Date or criteria for Phase 2
- (Repeat for Phase 2 and Phase 3)
- `{{PHASE_1_CHECK_LOGIC}}` - How to check if Phase 1 complete
- `{{PHASE_1_SUCCESS_INDICATORS}}` - What signals success
- `{{PHASE_1_SUCCESS_DEFINITION}}` - Overall Phase 1 success criteria
- `{{PROJECT_COMPLETION_DEFINITION}}` - What "project complete" means
- `{{OVERALL_SUCCESS_DEFINITION}}` - Final success definition
- `{{NEXT_CHECK_DATE}}` - Next scheduled check

---

**Note**: Phase Tracker is OPTIONAL. Only use for multi-phase projects requiring validation/testing before full rollout.
