---
name: ghe-status
description: |
  READ-ONLY quick overview of GitHub Elements workflow state. Shows active threads, phase distribution, and workflow health at a glance.

  USE THIS SKILL WHEN:
  - User asks "what's the status" or "show me the status"
  - User asks "what threads are active" or "what am I working on"
  - User asks "show me the workflow state" or "what's happening"
  - User wants a quick overview before starting work
  - Starting a session and need context

  DO NOT USE THIS SKILL WHEN:
  - User wants to CLAIM an issue (use ghe-claim)
  - User wants to POST a checkpoint (use ghe-checkpoint)
  - User wants to TRANSITION phases (use ghe-transition)
  - User wants DETAILED metrics/health reports (use ghe-report)

  EXAMPLES:
  <example>
  Context: User starting a session wants to see current state
  user: "What's the github elements status?"
  assistant: "I'll use ghe-status to show you the current workflow state"
  </example>
  <example>
  Context: User wants to know what work is available
  user: "Show me what threads are active"
  assistant: "I'll use ghe-status to display active and available threads"
  </example>
  <example>
  Context: Quick check before doing work
  user: "What am I currently working on?"
  assistant: "I'll use ghe-status to find your in-progress threads"
  </example>
---

## IRON LAW: User Specifications Are Sacred

**THIS LAW IS ABSOLUTE AND ADMITS NO EXCEPTIONS.**

1. **Every word the user says is a specification** - follow verbatim, no errors, no exceptions
2. **Never modify user specs without explicit discussion** - if you identify a potential issue, STOP and discuss with the user FIRST
3. **Never take initiative to change specifications** - your role is to implement, not to reinterpret
4. **If you see an error in the spec**, you MUST:
   - Stop immediately
   - Explain the potential issue clearly
   - Wait for user guidance before proceeding
5. **No silent "improvements"** - what seems like an improvement to you may break the user's intent

**Violation of this law invalidates all work produced.**

## Background Agent Boundaries

When running as a background agent, you may ONLY write to:
- The project directory and its subdirectories
- The parent directory (for sub-git projects)
- ~/.claude (for plugin/settings fixes)
- /tmp

Do NOT write outside these locations.

---

## GHE_REPORTS Rule (MANDATORY)

**ALL reports MUST be posted to BOTH locations:**
1. **GitHub Issue Thread** - Full report text (NOT just a link!)
2. **GHE_REPORTS/** - Same full report text (FLAT structure, no subfolders!)

**Report naming:** `<TIMESTAMP>_<title or description>_(<AGENT>).md`
**Timestamp format:** `YYYYMMDDHHMMSSTimezone`

**ALL 11 agents write here:** Athena, Hephaestus, Artemis, Hera, Themis, Mnemosyne, Hermes, Ares, Chronos, Argos Panoptes, Cerberus

**REQUIREMENTS/** is SEPARATE - permanent design documents, never deleted.

**Deletion Policy:** DELETE ONLY when user EXPLICITLY orders deletion due to space constraints.

---

## Settings Awareness

Respects `.claude/ghe.local.md`:
- `enabled`: If false, return minimal status
- `notification_level`: Affects output verbosity

---

# GitHub Elements Status (Quick Overview)

**Purpose**: Read-only quick overview of workflow state. Does NOT modify anything.

## When to Use

- Quick status check
- See active threads
- Check what's available
- Session start context

## How to Execute

Spawn the **reporter** agent with report type "status".

The reporter will:
1. Query all threads with GitHub Elements labels
2. Show active threads (DEV, TEST, REVIEW)
3. Display phase distribution
4. List recent completions
5. Show workflow health indicators
6. Flag any violations or warnings

## Output Format

```markdown
## GitHub Elements Status Report

### Active Threads
| Issue | Type | Phase | Epic | Assignee | Last Activity |
|-------|------|-------|------|----------|---------------|

### Phase Distribution
DEV: N active | TEST: N active | REVIEW: N active

### Available Work
[Ready issues not yet claimed]

### Workflow Health
- Violations: N
- Checkpoint frequency: N%
```

## Key Differentiator

This is a **READ-ONLY** quick overview. For detailed metrics, health checks, or epic-specific reports, use `ghe-report` instead.
