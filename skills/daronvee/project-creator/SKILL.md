---
name: project-creator
description: |
  Creates new projects in CCGG Business Operations with all required mechanisms automatically implemented.
  Ensures PARENT SYSTEM INTEGRATION, operations logging, strategic alignment, and cross-project intelligence are properly configured.
  Handles both simple projects (standard structure) and complex projects (with coordination hubs and dependency tracking).

  Use for: creating new incubator project, adding sub-project to CCGG, initializing project structure, setting up project coordination, ensuring PARENT SYSTEM INTEGRATION implemented, generating CLAUDE.md with all mechanisms, creating Active Projects Index entry.

  Trigger terms: create project, new project, initialize project, set up project, add sub-project, project structure, CCGG project creation.
version: 1.0.0
created: 2025-10-29
author: Daron Vener
repository: https://github.com/DaronVee/ccgg-project-creator-skill
---

# Project Creator for CCGG Business Operations

## Quick Start

**What this skill does**: Automatically creates new CCGG Business Operations projects with all required mechanisms pre-implemented (PARENT SYSTEM INTEGRATION, Active Projects Index, operations logging, etc.).

**Use when**: Creating new incubator project, adding sub-project to CCGG, setting up project structure

**Prevents**: Forgetting critical mechanisms like PARENT SYSTEM INTEGRATION (the problem that triggered this skill's creation)

---

## When to Use This Skill

**Trigger Phrases**:
- "Create new project in CCGG Business Operations"
- "Initialize new incubator project"
- "Set up project structure for [project-name]"
- "Add new sub-project to CCGG"

**Project Types Supported**:
1. **Simple Projects** (majority): Research, single-purpose tools, straightforward deliverables
2. **Complex Projects** (strategic): Multi-project coordination, dependencies, integration requirements

---

## Project Creation Workflow

### Step 1: Gather Project Information

**Ask Daron These Questions** (in conversational order):

1. **"What's the project name?"**
   - Format: hyphen-case (e.g., `member-retention-sequences`)
   - Max 40 characters
   - Will be used for folder name and project ID

2. **"What's the project purpose?"** (1-2 sentences)
   - Clear problem statement
   - Expected outcome
   - Example: "Design email sequences to re-engage churned members and improve retention rate"

3. **Analyze project description for multi-phase indicators** (SUGGESTION, not question):

   **Claude analyzes** project purpose and deliverables for signals:
   - Keywords: "validate", "test", "feedback", "iterate", "production rollout", "pilot"
   - Complex deliverables (3+ major components requiring testing)
   - Integration with existing systems (needs testing phase)
   - User mentions "experiment", "trial", or "phase"
   - Project type: infrastructure, framework, new system (vs simple content creation)

   **If multi-phase indicators detected**, SUGGEST phased approach:
   ```
   "Based on your project description, I recommend a multi-phase approach:

   Phase 1: [Research & Planning / Setup & Test / MVP]
   Phase 2: [Build & Test / Validation & Refinement / Production Rollout]
   Phase 3: [Deploy & Scale / Institutionalize / Maintenance]

   This allows testing and feedback before full rollout. Would you like to use this phased approach?"
   ```

   **User can respond**:
   - "Yes, use phases" → Generate PHASE_TRACKER.md with suggested phases
   - "No, single phase" → Skip Phase Tracker
   - "Let me customize phases" → Ask for phase names/durations

   **If NO multi-phase indicators**, skip suggestion and Phase Tracker

4. **"Will this project coordinate with or depend on other projects?"**
   - If YES → Complex project (needs Coordination Hub)
   - If NO → Simple project (standard structure only)

5. **ALWAYS: Detect and Capture Dependencies** (NEW - Forcing Function)

   **Claude PROACTIVELY suggests dependencies** based on project description:

   ```
   "Let me help identify dependencies for this project:

   BLOCKING DEPENDENCIES (must complete before starting this):
   - What existing work must finish before you can start?
   - What deliverables from other projects do you need?

   DOWNSTREAM DEPENDENCIES (projects waiting for this):
   - What other projects are waiting for this one?
   - What will this project enable or unblock?

   RELATED PARALLEL (connected but not blocking):
   - What other projects share themes/tools with this?

   [Based on your project description, I see potential dependencies:]
   - [Suggest upstream based on keywords/deliverables mentioned]
   - [Suggest downstream based on Active Projects needing this work]

   Should I add these to the dependency metadata?"
   ```

   **Capture in YAML format**:
   ```yaml
   dependencies:
     blocks: ["project-id-1", "project-id-2"]  # Must complete first
     blocked_by: ["project-id-3"]              # Waiting for this
     related_parallel: ["project-id-4"]        # Connected, not blocking
   ```

   **Even if "none"**, still create empty fields (forces conscious decision):
   ```yaml
   dependencies:
     blocks: []        # No upstream dependencies
     blocked_by: []    # No downstream dependencies
     related_parallel: []  # No related work
   ```

6. **If Complex: "Which projects does this coordinate with?"**
   - Upstream dependencies (what this project needs)
   - Downstream dependencies (what other projects need from this)
   - Example: "Depends on hormozi-money-models (frameworks), feeds into retention-reengagement (implementation)"
   - **NOTE**: This is for Coordination Hub documentation (prose), Step 5 captures YAML metadata

7. **"What are the key deliverables?"** (3-5 items)
   - Specific outputs this project will produce
   - Example: "Email sequence templates, DM scripts, retention playbook"

8. **"Which avatars does this serve?"** (optional, for strategic alignment)
   - From Target_Avatars_Complete_Profiles.md
   - If "all avatars" → note that
   - If specific → list them

---

### Step 2: Determine Project Complexity

**Based on Question 3 answer**:

**SIMPLE PROJECT** (if NO coordination):
- Standard folder structure
- CLAUDE.md with PARENT SYSTEM INTEGRATION
- README.md
- Active Projects Index
- operations_log entry

**COMPLEX PROJECT** (if YES coordination):
- All simple project components PLUS:
- Coordination Hub/ folder
  - PROJECT_DEPENDENCIES.md
  - INTEGRATION_CHECKLIST.md
  - OUTPUT_LIBRARY.md
- Enhanced CLAUDE.md (cross-project knowledge access patterns)
- Integration sections in related projects' CLAUDE.md files

---

### Step 3: Create Project Structure

**Location**: `Active Projects/_Incubator/[project-name]/`

**Manual Creation** (automated script planned for future):
1. Create folder: `mkdir "Active Projects/_Incubator/[project-name]"`
2. Use Write tool to create CLAUDE.md from `templates/CLAUDE_SIMPLE.md` OR `templates/CLAUDE_COMPLEX.md`
3. **If multi-phase project**: Use Write tool to create PHASE_TRACKER.md from `templates/PHASE_TRACKER_TEMPLATE.md`
4. Fill all placeholders (marked with `{{VARIABLE}}`)

This creates:
```
[project-name]/
├── CLAUDE.md                    # Project guidance (PARENT SYSTEM INTEGRATION included)
├── README.md                    # Quick start + overview
├── [folders based on project type]
└── Coordination Hub/            # If complex project
    ├── PROJECT_DEPENDENCIES.md
    ├── INTEGRATION_CHECKLIST.md
    └── OUTPUT_LIBRARY.md
```

**Note**: Full automation script (`create_project.sh`) is planned but not yet implemented. Current workflow uses templates + manual variable replacement.

---

### Step 4: Generate CLAUDE.md Content

**Use Template**:
- Simple: `templates/CLAUDE_SIMPLE.md`
- Complex: `templates/CLAUDE_COMPLEX.md`

**Required Sections** (ALL projects):
1. **PROJECT IDENTITY** (name, type, status, created date, owner)
2. **PROJECT MISSION** (purpose, core focus, expected outcomes)
3. **SCOPE & BOUNDARIES** (in scope, out of scope)
4. **PARENT SYSTEM INTEGRATION** ⚠️ CRITICAL
   - Project Memory Index Sync (path, when/how to update)
   - Operations Logging (format, actions to auto-log, examples)
   - Strategic Alignment Validation (OOBG check, UV check, Avatar targeting)
   - Cross-Project Intelligence (search related projects)
5. **PROJECT STRUCTURE** (folder organization, key files)
6. **EXPECTED DELIVERABLES** (phased if applicable)
7. **SUCCESS CRITERIA** (how to measure completion)

**Additional Sections** (Complex projects):
8. **AUTONOMOUS KNOWLEDGE ACCESS** (cross-project references, access commands)
9. **COORDINATION WITH OTHER PROJECTS** (dependency chain, integration points)

**Populate Variables**:
- Replace `{{PROJECT_NAME}}` with actual name
- Replace `{{PROJECT_PURPOSE}}` with purpose from Step 1
- Replace `{{DELIVERABLES}}` with list from Step 1
- Replace `{{UPSTREAM_DEPS}}` and `{{DOWNSTREAM_DEPS}}` with projects from Step 1 (if complex)
- Replace `{{AVATARS}}` with avatars from Step 1
- Add current date in `{{CREATED_DATE}}`
- Replace `{{PHASE_TRACKER_SECTION}}` with:
  - If multi-phase: "**This is a multi-phase project**. See `PHASE_TRACKER.md` for phase timeline, completion criteria, and proactive reminders.\n\n**Current Phase**: [Phase 1 name]\n**Next Milestone**: [Phase 1 completion]\n\n**Manual Check**: Say 'Check phase tracker' anytime for status update."
  - If single-phase: "**This is a single-phase project**. No phase tracker needed."

---

### Step 5: Generate README.md Content

**Use Template**: `templates/README.md`

**Required Sections**:
1. **Project Title + Overview** (1 paragraph)
2. **Quick Start** (how to begin working on this project)
3. **Context** (why this project exists, what problem it solves)
4. **Key Deliverables** (checklist format)
5. **Related Projects** (if complex project)
6. **Timeline** (if applicable)
7. **Success Criteria**

**Keep it Concise**: Max 200 lines. README is for quick orientation, CLAUDE.md has details.

---

### Step 6: Generate PHASE_TRACKER.md (If Multi-Phase Project)

**Skip This Step If**: Single-phase project (no phases suggested/accepted in Step 1)

**If Multi-Phase Project**:

**Location**: `Active Projects/_Incubator/[project-name]/PHASE_TRACKER.md`

**Use Template**: `templates/PHASE_TRACKER_TEMPLATE.md`

**Populate Variables**:
- `{{PROJECT_NAME}}`, `{{PROJECT_TITLE}}`, `{{CREATED_DATE}}` - From Step 1
- For each phase (1-3):
  - `{{PHASE_N_NAME}}` - Phase name (e.g., "Setup & Test", "Validation & Refinement")
  - `{{PHASE_N_GOAL}}` - What this phase accomplishes
  - `{{PHASE_N_DURATION}}` - Time estimate (e.g., "4 weeks", "1 week")
  - `{{PHASE_N_TARGET_DATES}}` - Date range (calculate from project start + duration)
  - `{{PHASE_N_CRITERIA}}` - Completion criteria (suggest based on deliverables)
  - `{{PHASE_N_DELIVERABLES}}` - Phase-specific deliverables checklist
  - `{{PHASE_N_REMINDER_LOGIC}}` - How Claude checks weekly
  - `{{PHASE_N_TRANSITION_TRIGGER}}` - When to prompt next phase
  - `{{PHASE_N_NEXT_TRIGGER}}` - Date or criteria
  - `{{PHASE_N_CHECK_LOGIC}}` - How to validate completion
  - `{{PHASE_N_SUCCESS_INDICATORS}}` - What signals success
  - `{{PHASE_N_SUCCESS_DEFINITION}}` - Overall phase success
- `{{PROJECT_COMPLETION_DEFINITION}}` - What "project complete" means
- `{{OVERALL_SUCCESS_DEFINITION}}` - Final success definition
- `{{NEXT_CHECK_DATE}}` - Calculate (project start + 1 week)

**Default Phase Structure** (if user accepts suggestion):

**Phase 1**: Setup & Test / MVP / Research & Planning (2-4 weeks)
- Goal: Create system, test basic functionality, validate approach
- Criteria: Core deliverables complete, basic testing done

**Phase 2**: Validation & Refinement / Production Rollout / Build & Test (1-2 weeks)
- Goal: Review Phase 1 results, refine approach, confirm effectiveness
- Criteria: Patterns identified, template/system refined, frequency/scope confirmed

**Phase 3**: Institutionalize / Scale / Deploy (1 week)
- Goal: Promote to production, document final workflow, mark production-ready
- Criteria: Integrated into root CLAUDE.md, added to registries, sustainable

**Proactive Reminder Example**:
```
Phase 1 Reminder Logic:
- Weekly: Check if [X weeks] passed OR [N deliverables] complete
- Transition: After [criteria met] OR [deadline] → "Ready for Phase 2?"

Phase 2 Reminder Logic:
- After Phase 1 complete → Prompt immediately
- After Phase 2 tasks done → "Ready for Phase 3?"

Phase 3 Reminder Logic:
- After Phase 2 complete → Prompt immediately
- After Phase 3 tasks done → "Project complete!"
```

---

### Step 7: Create Active Projects Index Entry

**Location**: `Project Memory/Active Projects Index/[project-name]-index.md`

**Use Template**: `templates/PROJECT_INDEX.md`

**Required Content** (YAML frontmatter + sections):
```yaml
---
project_id: "incubator-[project-name]"
title: "[Project Title]"
project_type: "incubator-program"
status: "incubating"
date_created: "YYYY-MM-DD"
date_modified: "YYYY-MM-DD"
folder_path: "Active Projects/_Incubator/[project-name]"
tags: ["tag1", "tag2", "tag3"]
strategic_alignment:
  oobg_relevance: "[How this serves OOBG]"
  unique_vehicle_fit: "[How this leverages YouTube + CCGG community]"
  avatar_targets: ["Avatar1", "Avatar2"]

# NEW: Dependency tracking (from Step 5)
dependencies:
  blocks: []                    # Projects that BLOCK this one (must complete first)
  blocked_by: []                # Projects this one BLOCKS (waiting for this)
  related_parallel: []          # Connected but not blocking

dependency_status:
  is_blocked: false             # Auto-calculated from blocks[]
  blocking_count: 0             # Auto-calculated from blocked_by[]
  ready_to_start: true          # Auto-calculated

last_sync: "YYYY-MM-DD (Project creation)"
---

## Current Status
[Project status description]

## Key Deliverables
[Checklist of deliverables]

## Last Activity
[Most recent work]

## Quick Access
[Links to project folder and key files]
```

**Populate with Data from Step 1**

---

### Step 7: Create Coordination Hub (Complex Projects Only)

**If Simple Project**: Skip this step.

**If Complex Project**: Create 3 coordination files:

#### PROJECT_DEPENDENCIES.md
**Purpose**: Track what this project needs from/provides to other projects

**Use Template**: `templates/coordination/PROJECT_DEPENDENCIES.md`

**Populate**:
- Upstream dependencies (projects this depends on)
- Downstream dependencies (projects that depend on this)
- Integration checkpoints
- Blocker tracking section

#### INTEGRATION_CHECKLIST.md
**Purpose**: Ensure all dependencies met before execution/handoff

**Use Template**: `templates/coordination/INTEGRATION_CHECKLIST.md`

**Populate**:
- Pre-requisites from upstream projects
- Execution checklist (this project's phases)
- Post-implementation checklist (handoffs to downstream)
- Validation criteria

#### OUTPUT_LIBRARY.md
**Purpose**: Catalog deliverables for other projects to reference

**Use Template**: `templates/coordination/OUTPUT_LIBRARY.md`

**Populate**:
- List expected outputs with status (PENDING/IN PROGRESS/COMPLETE)
- Link to files when created
- Note which projects consume each output

---

### Step 8: Log Project Creation

**Auto-log to operations_log.txt**:

```
[YYYY-MM-DD HH:MM:SS] - CREATE - [project-name] - New incubator project created. [Simple/Complex] structure. [Key context]. Deliverables: [list]. Dependencies: [if complex].
```

**Example**:
```
[2025-10-29 14:30:00] - CREATE - member-retention-sequences - New incubator project created. Simple structure. Email sequences to re-engage churned members. Deliverables: 5 email templates, 3 DM scripts, retention playbook.
```

---

### Step 9: Validate All Mechanisms Implemented

**Run Checklist** (automated validation):

```bash
bash scripts/validate_project.sh [project-name]
```

**Manual Checklist** (if script unavailable):
- [ ] CLAUDE.md exists with PARENT SYSTEM INTEGRATION section
- [ ] PARENT SYSTEM INTEGRATION has all 4 sub-sections:
  - [ ] Project Memory Index Sync
  - [ ] Operations Logging
  - [ ] Strategic Alignment Validation
  - [ ] Cross-Project Intelligence
- [ ] CLAUDE.md has MULTI-PHASE PROJECT TRACKER section with appropriate text
- [ ] README.md exists with Quick Start section
- [ ] Active Projects Index entry created
- [ ] operations_log.txt entry added
- [ ] Folder structure matches project complexity (simple vs complex)
- [ ] If complex: Coordination Hub created with 3 files
- [ ] If multi-phase: PHASE_TRACKER.md created and populated
- [ ] All template variables replaced (no `{{PLACEHOLDER}}` remaining)

**If any checks fail**: Fix before proceeding.

---

### Step 10: Report Completion

**Generate Summary Report**:

```
✅ Project Created: [project-name]

**Location**: Active Projects/_Incubator/[project-name]/
**Complexity**: [Simple/Complex]
**Multi-Phase**: [Yes (3 phases) / No (single-phase)]
**Purpose**: [One-sentence purpose]

**Files Created**:
- CLAUDE.md (with PARENT SYSTEM INTEGRATION ✓)
- README.md
- [If multi-phase] PHASE_TRACKER.md (Phase 1: [name], Phase 2: [name], Phase 3: [name])
- [List other files/folders]

**Index Entry**: Project Memory/Active Projects Index/[project-name]-index.md ✓
**Operations Log**: Logged at [timestamp] ✓

**Phase Tracker** (if multi-phase):
- Current Phase: Phase 1 ([name])
- Next Check: [date] (weekly during strategic planning)
- Manual Check: Say "Check phase tracker [project-name]" anytime

**Next Steps**:
1. Review CLAUDE.md for project-specific guidance
2. [If multi-phase] Review PHASE_TRACKER.md for phase timeline
3. Begin work on first deliverable: [first item from Step 1]
4. Update index after major progress

**Quick Access**: [Link to project folder]
```

**Present to Daron** for confirmation before moving on.

---

## Templates Reference

All templates are in `templates/` folder:

**Core Templates**:
- `CLAUDE_SIMPLE.md` - Standard project CLAUDE.md (with PARENT SYSTEM INTEGRATION)
- `CLAUDE_COMPLEX.md` - Complex project CLAUDE.md (adds cross-project coordination)
- `README.md` - Standard README structure
- `PROJECT_INDEX.md` - Active Projects Index entry template

**Coordination Templates** (complex projects only):
- `coordination/PROJECT_DEPENDENCIES.md`
- `coordination/INTEGRATION_CHECKLIST.md`
- `coordination/OUTPUT_LIBRARY.md`

**See**: [templates/README.md](templates/README.md) for template usage guide

---

## Scripts Reference

**create_project.sh** - Automates project structure creation
```bash
bash scripts/create_project.sh [project-name] [simple|complex]
```

**validate_project.sh** - Validates all mechanisms implemented
```bash
bash scripts/validate_project.sh [project-name]
```

**See**: [scripts/README.md](scripts/README.md) for script documentation

---

## Common Scenarios

### Scenario 1: Simple Research Project
**Example**: "Create project to research Dream 100 strategies"

**Workflow**:
1. Name: `dream-100-research`
2. Purpose: "Research and document Dream 100 implementation strategies for CCGG traffic growth"
3. Coordination: NO (simple project)
4. Deliverables: Research document, implementation plan, resource list
5. Avatars: All (traffic benefits everyone)
6. Create → Simple structure
7. Validate → Done

**Time**: 10-15 minutes

---

### Scenario 2: Complex Strategic Project
**Example**: "Create project for CCGG offers and pricing strategy"

**Workflow**:
1. Name: `ccgg-offers-pricing`
2. Purpose: "Design CCGG pricing structure and offer ladder to maximize revenue per customer"
3. Coordination: YES
   - Depends on: hormozi-money-models (frameworks), claude-code-business-os (offer ladder)
   - Feeds into: member-onboarding-ascension (upgrade sequences), retention-reengagement (win-back pricing)
4. Deliverables: Tier definitions, pricing structure, implementation plan, annual member presentation
5. Avatars: All avatars
6. Create → Complex structure (with Coordination Hub)
7. Populate dependency maps
8. Validate → Done

**Time**: 20-30 minutes

---

## Validation Failures & Fixes

**Problem**: "PARENT SYSTEM INTEGRATION section missing"
**Fix**: Add section from `templates/CLAUDE_SIMPLE.md` lines 40-120

**Problem**: "Template variables not replaced ({{PROJECT_NAME}} still present)"
**Fix**: Search for `{{` and replace all placeholders with actual values

**Problem**: "Operations log entry missing"
**Fix**: Add entry manually:
```
echo "[$(date +%Y-%m-%d\ %H:%M:%S)] - CREATE - [project-name] - [description]" >> "operations_log.txt"
```

**Problem**: "Active Projects Index missing strategic_alignment section"
**Fix**: Add to YAML frontmatter:
```yaml
strategic_alignment:
  oobg_relevance: "[description]"
  unique_vehicle_fit: "[description]"
  avatar_targets: ["avatar1"]
```

---

## Important Notes

### On PARENT SYSTEM INTEGRATION
⚠️ **CRITICAL**: This section is **REQUIRED** in every project CLAUDE.md. It is the integration point with CCGG Business Operations.

**Why it matters**:
- Enables automatic operations logging
- Keeps Project Memory Index in sync
- Validates strategic alignment
- Enables cross-project intelligence

**If forgotten**: Project will be orphaned from CCGG Business Operations system.

### On Complexity Assessment
**Default to Simple** unless clear multi-project coordination is needed.

**Indicators of Complex Project**:
- Depends on outputs from 2+ other projects
- 2+ other projects depend on this project's outputs
- Strategic planning (affects multiple business areas)
- Integration/coordination is core to the project

**Indicators of Simple Project**:
- Self-contained work
- Standalone deliverables
- No handoffs to other projects required
- Research or single-purpose tool

**When in doubt**: Ask Daron, "Will this project need to coordinate with other active projects?"

---

## Success Criteria

**Project creation is successful when**:
1. All validation checks pass (Step 9)
2. Daron can open the project and immediately understand:
   - What it does
   - What mechanisms are available
   - How to get started
3. PARENT SYSTEM INTEGRATION is fully implemented
4. Future Claude sessions can find this project via Active Projects Index search

**Project creation has FAILED if**:
- Any mechanism is missing (especially PARENT SYSTEM INTEGRATION)
- Template variables not replaced
- Daron has to manually add standard components
- Operations log entry missing

---

## Additional Resources

**For detailed mechanism specifications**, see:
- [references/mechanism_specifications.md](references/mechanism_specifications.md) - Complete templates, variable replacement guide, and mechanism requirements

**For template usage**, see:
- [templates/README.md](templates/README.md) - Template selection guide and variable documentation
- [templates/CLAUDE_SIMPLE.md](templates/CLAUDE_SIMPLE.md) - Standard project template
- templates/CLAUDE_COMPLEX.md - Complex project template (planned for future - use SIMPLE template + Coordination Hub for now)

**For validation scripts**, see:
- [scripts/README.md](scripts/README.md) - Script documentation and usage examples
- [scripts/validate_project.py](scripts/validate_project.py) - Python validation script (recommended)
- [scripts/validate_project.sh](scripts/validate_project.sh) - Bash validation script (legacy)

---

## Version History

**v1.0.0** (2025-10-29)
- Initial release
- Simple and complex project support
- Full PARENT SYSTEM INTEGRATION enforcement
- Automated validation with Python script
- Coordination Hub for complex projects
- Progressive disclosure via references/

---

**Created with Skills Factory** - Ensures every CCGG Business Operations project is created correctly
