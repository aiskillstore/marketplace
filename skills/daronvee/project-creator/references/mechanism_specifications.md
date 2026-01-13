# CCGG Business Operations Mechanism Specifications

**Purpose**: Detailed specifications for each mechanism that must be implemented in CCGG Business Operations sub-projects.

**Source of Truth**: `System Documentation/CCGG_MECHANISMS_REGISTRY.md` (in CCGG Business Operations root)

**Last Synced**: 2025-10-29

---

## Mechanism 1: PARENT SYSTEM INTEGRATION Section

**Status**: REQUIRED (All projects)

### Required Location
CLAUDE.md (typically after SCOPE & BOUNDARIES section)

### Complete Template

```markdown
## PARENT SYSTEM INTEGRATION

**This is a sub-project of CCGG Business Operations**

### Project Memory Index Sync

**Your Project Index**: `../../../Project Memory/Active Projects Index/{{PROJECT_NAME}}-index.md`

**When to Update**:
- After completing major deliverable
- When project status changes
- After significant progress (weekly recommended)

**How to Update**:
1. Read your index file
2. Update: Current Status, Key Deliverables, Last Activity
3. Update date_modified and last_sync timestamps
4. Offer to log in operations_log.txt

### Operations Logging

**Location**: `../../../operations_log.txt`

**Format**: `[YYYY-MM-DD HH:MM:SS] - [ACTION] - {{PROJECT_NAME}} - [details]`

**Actions to Auto-Log** (without asking):
- CREATE: New deliverables, documents, implementations
- UPDATE: Revisions to key outputs
- COMPLETE: Phase completions, deliverable handoffs
- SYSTEM_UPGRADE: Infrastructure improvements
- SYNC: Project index updates

**Behavior**: Auto-log major actions WITHOUT prompting user

### Strategic Alignment Validation

**Reference**: `../../../AI Growth Engine/Knowledge Base/Strategy_for_CCGG_AI_Leaders_Business.md`

**Three Validation Checks**:

1. **OOBG Check**: Does this help coaches/consultants monetize with AI?
2. **Unique Vehicle Check**: Does this leverage YouTube + CCGG paid community?
3. **Avatar Targeting**: Which specific customer avatars benefit from this?

**When to Validate**: Project creation, phase transitions, strategic reviews

### Cross-Project Intelligence

**Path**: `../../../Project Memory/Active Projects Index/`

**Behavior**: When asked "what related projects exist?", search Active Projects Index folder for similar work

**Use Cases**: Find similar work, identify dependencies, discover synergies
```

---

## Mechanism 2: Active Projects Index Entry

**Status**: REQUIRED (All projects)

### File Location
`Project Memory/Active Projects Index/{{PROJECT_NAME}}-index.md`

### Complete Template

```yaml
---
project_id: "incubator-{{PROJECT_NAME}}" OR "active-{{PROJECT_NAME}}"
title: "{{PROJECT_TITLE}}"
project_type: "incubator-program" OR "active-program"
status: "incubating" OR "active" OR "paused" OR "completed"
date_created: "YYYY-MM-DD"
date_modified: "YYYY-MM-DD"
folder_path: "Active Projects/_Incubator/{{PROJECT_NAME}}" OR "Active Projects/{{PROJECT_TITLE}}"
tags: ["tag1", "tag2", "tag3"]
strategic_alignment:
  oobg_relevance: "How this helps coaches monetize with AI"
  unique_vehicle_fit: "How this leverages YouTube + CCGG community"
  avatar_targets: ["avatar1", "avatar2"]
last_sync: "YYYY-MM-DD HH:MM:SS (context: initial creation)"
---

## Current Status

[Current state description - initially "Incubating - exploring viability"]

## Key Deliverables

[ ] Deliverable 1
[ ] Deliverable 2
[ ] Deliverable 3

## Last Activity

[Most recent work with date - initially "Created project structure"]

## Quick Access

- Full project: [Active Projects/_Incubator/{{PROJECT_NAME}}](../../../Active Projects/_Incubator/{{PROJECT_NAME}})
- CLAUDE.md: [CLAUDE.md](../../../Active Projects/_Incubator/{{PROJECT_NAME}}/CLAUDE.md)
```

---

## Mechanism 3: Operations Logging (Centralized)

**Status**: REQUIRED (All projects log here)

### File Location
`operations_log.txt` (root of CCGG Business Operations)

### Format
```
[YYYY-MM-DD HH:MM:SS] - [ACTION] - [project-name] - [details]
```

### Standard Actions
- **CREATE**: New projects, deliverables, systems
- **UPDATE**: Major revisions
- **COMPLETE**: Phase/project completions
- **GRADUATE**: Incubator → Active promotion
- **ARCHIVE**: Project completion/deprecation
- **SYNC**: Index synchronization
- **SYSTEM_UPGRADE**: Business OS infrastructure improvements
- **DAILY_ROADMAP**: Daily execution roadmap generation
- **STRATEGIC_PLANNING**: Strategic planning sessions

### Behavior
Automatic logging (no prompt) for major actions

---

## Mechanism 9: Coordination Hub (Complex Projects Only)

**Status**: OPTIONAL (Only for complex projects with dependencies)

### When to Use
Projects with:
- 2+ upstream dependencies (what this project needs from others)
- 2+ downstream dependencies (what other projects need from this)
- Strategic planning projects requiring integration validation
- Coordination/integration projects

### Required Files

#### File 1: PROJECT_DEPENDENCIES.md

```markdown
# Project Dependencies - {{PROJECT_TITLE}}

## Upstream Dependencies (What We Need)

### From [Project Name]
- **Dependency**: [What we need]
- **Status**: PENDING | IN PROGRESS | COMPLETE
- **Impact if Delayed**: [Description]
- **Owner**: [Responsible party]

## Downstream Dependencies (What Others Need from Us)

### To [Project Name]
- **Deliverable**: [What they need]
- **Status**: PENDING | IN PROGRESS | COMPLETE
- **Due Date**: YYYY-MM-DD
- **Owner**: [Responsible party]

## Integration Checkpoints

- [ ] Checkpoint 1 (Date: YYYY-MM-DD)
- [ ] Checkpoint 2 (Date: YYYY-MM-DD)

## Current Blockers

**None** OR list blockers with mitigation plans
```

#### File 2: INTEGRATION_CHECKLIST.md

```markdown
# Integration Checklist - {{PROJECT_TITLE}}

## Phase 1: Pre-Requisites (Before We Start)

- [ ] Dependency from [Project] received
- [ ] Dependency from [Project] validated
- [ ] All upstream deliverables confirmed

## Phase 2: Execution (This Project's Work)

- [ ] Deliverable 1
- [ ] Deliverable 2
- [ ] Integration test with upstream dependencies

## Phase 3: Post-Implementation (Handoff to Downstream)

- [ ] Deliverable to [Project] completed
- [ ] Deliverable to [Project] validated
- [ ] All downstream consumers notified

## Validation Criteria

**Phase 1 → 2**: [Criteria]
**Phase 2 → 3**: [Criteria]

## Risks & Mitigation

**Risk 1**: [Description]
- Mitigation: [Plan]

**Risk 2**: [Description]
- Mitigation: [Plan]
```

#### File 3: OUTPUT_LIBRARY.md

```markdown
# Output Library - {{PROJECT_TITLE}}

## Deliverables Produced by This Project

### Output 1: [Name]
- **Status**: PENDING | IN PROGRESS | COMPLETE
- **File Link**: [path when complete]
- **Consumer Projects**: [Project 1], [Project 2]
- **Description**: [What this output is]

### Output 2: [Name]
- **Status**: PENDING | IN PROGRESS | COMPLETE
- **File Link**: [path when complete]
- **Consumer Projects**: [Project 1]
- **Description**: [What this output is]

## How to Use This Library

Other projects reference this file to track when deliverables are ready for integration.
```

---

## Variable Replacement Guide

When creating projects, replace these variables:

- `{{PROJECT_NAME}}`: Hyphen-case identifier (e.g., "ccgg-offers-pricing")
- `{{PROJECT_TITLE}}`: Human-readable title (e.g., "CCGG Offers & Pricing Model")
- `{{PROJECT_TYPE}}`: "incubator-program" or "active-program"
- `{{PROJECT_PURPOSE}}`: 1-2 sentence purpose
- `{{CREATED_DATE}}`: YYYY-MM-DD format
- `{{CORE_FOCUS_ITEMS}}`: Bullet list of focus areas
- `{{IN_SCOPE_ITEMS}}`: What's included in project
- `{{OUT_OF_SCOPE_ITEMS}}`: What's explicitly excluded
- `{{OOBG_ALIGNMENT}}`: How this serves OOBG (coaches monetizing AI)
- `{{UV_ALIGNMENT}}`: How this leverages Unique Vehicle (YouTube + CCGG)
- `{{AVATAR_TARGETING}}`: Which avatars benefit
- `{{RELATED_PROJECTS}}`: Links to related projects
- `{{FOLDER_STRUCTURE}}`: Project folder tree

---

**Maintained By**: CCGG Business Operations system
**Version**: v1.0 (synced with CCGG_MECHANISMS_REGISTRY.md)
