---
project_id: "incubator-{{PROJECT_NAME}}"
title: "{{PROJECT_TITLE}}"
project_type: "incubator-program"
status: "incubating"
date_created: "{{DATE_CREATED}}"
date_modified: "{{DATE_CREATED}}"
folder_path: "Active Projects/_Incubator/{{PROJECT_NAME}}"
tags: [{{TAGS}}]
strategic_alignment:
  oobg_relevance: "{{OOBG_RELEVANCE}}"
  unique_vehicle_fit: "{{UV_FIT}}"
  avatar_targets: [{{AVATARS}}]

# Dependency tracking (FORCING FUNCTION - always populate, even if empty)
dependencies:
  blocks: {{BLOCKS}}                    # Projects that BLOCK this one (must complete first)
  blocked_by: {{BLOCKED_BY}}            # Projects this one BLOCKS (waiting for this)
  related_parallel: {{RELATED}}         # Connected but not blocking

dependency_status:
  is_blocked: {{IS_BLOCKED}}            # Auto-calculated from blocks[]
  blocking_count: {{BLOCKING_COUNT}}    # Auto-calculated from blocked_by[]
  ready_to_start: {{READY}}             # Auto-calculated

last_sync: "{{DATE_CREATED}} (Project creation)"
---

## Current Status

**{{STATUS_DESCRIPTION}}**

{{CONTEXT}}

## PARENT SYSTEM INTEGRATION

**Auto-synced**: {{DATE_CREATED}}

**Dependencies**:
- Upstream: {{UPSTREAM_PROSE}}
- Downstream: {{DOWNSTREAM_PROSE}}

**Integration Notes**: {{INTEGRATION_NOTES}}

## Key Deliverables

{{DELIVERABLES_CHECKLIST}}

## Last Activity

**Created**: {{DATE_CREATED}} (Initial project setup)
**Last Modified**: {{DATE_CREATED}}

## Quick Access

**Full Project**: [Active Projects/_Incubator/{{PROJECT_NAME}}](../../Active Projects/_Incubator/{{PROJECT_NAME}}/)
- [README.md](../../Active Projects/_Incubator/{{PROJECT_NAME}}/README.md)
- [CLAUDE.md](../../Active Projects/_Incubator/{{PROJECT_NAME}}/CLAUDE.md)
