---
name: file-boundaries
description: Pattern for respecting file ownership boundaries during implementation. Prevents conflicts in parallel work.
allowed-tools: Read, Write, Edit
---

# File Boundaries Skill

Pattern for respecting file ownership in parallel work.

## When to Load This Skill

- You are implementing code with defined boundaries
- You're working in parallel with other agents
- You need to avoid file conflicts

## Boundary Rules

### Files You OWN
```yaml
boundaries:
  owns: [src/auth/login.ts, src/auth/logout.ts]
```

You CAN:
- Read these files
- Modify these files
- Create new files in these paths
- Delete these files

### Files You READ
```yaml
boundaries:
  reads: [src/types/user.ts, src/utils/crypto.ts]
```

You CAN:
- Read these files for reference
- Import from these files

You CANNOT:
- Modify these files
- If you need changes → report BLOCKED

## Checking Boundaries

Before modifying any file:
1. Is this file in my `owns` list?
2. If NO → STOP, don't modify
3. If need to modify → report BLOCKED with details

## Reporting Boundary Violations

If you need to modify a file outside boundaries:
```yaml
status: blocked
blocked_reason: boundary_violation
blocked_details:
  description: "Need to modify src/types/user.ts to add new type"
  needs: "Permission to modify or contract update"
  suggested_resolution: "Add UserSession type to user.ts"
```

## Parallel Work Safety

Boundaries exist to enable parallel work:
- Agent A owns `src/auth/`
- Agent B owns `src/api/`
- Both can work simultaneously without conflict

If boundaries are unclear or need changes:
- STOP and report BLOCKED
- Don't assume or proceed

## Principles

- **Strict ownership** - Only touch what you own
- **Explicit boundaries** - No implicit permissions
- **Block, don't break** - Report issues, don't work around
