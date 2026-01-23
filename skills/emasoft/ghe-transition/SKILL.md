---
name: ghe-transition
description: |
  CHANGE phases in the GitHub Elements workflow. Closes current thread and opens next phase thread. This is a PHASE CHANGE operation, not just saving progress.

  USE THIS SKILL WHEN:
  - User says "transition to TEST" or "move to REVIEW"
  - User says "I'm done with DEV, start TEST" or "DEV complete"
  - User says "advance to next phase" or "close this phase"
  - User says "demote to DEV" (from TEST or REVIEW)
  - User says "tests pass, ready for review"
  - User says "merge this" (after REVIEW PASS)
  - User explicitly wants to END current phase and BEGIN next

  DO NOT USE THIS SKILL WHEN:
  - User just wants to SEE status (use ghe-status)
  - User wants to START work on new issue (use ghe-claim)
  - User wants to SAVE progress but CONTINUE working (use ghe-checkpoint)
  - User wants reports (use ghe-report)
  - User is not ready to END current phase

  IMPORTANT: This CLOSES current thread and OPENS next thread. Use ghe-checkpoint if you just want to save progress without changing phases.

  EXAMPLES:
  <example>
  Context: DEV work complete, ready for testing
  user: "I'm done with DEV, transition to TEST"
  assistant: "I'll use ghe-transition to close DEV and open TEST thread"
  </example>
  <example>
  Context: All tests pass, ready for review
  user: "Tests pass, move to REVIEW"
  assistant: "I'll use ghe-transition to close TEST and open REVIEW thread"
  </example>
  <example>
  Context: Structural issues found in TEST
  user: "This needs structural changes, demote to DEV"
  assistant: "I'll use ghe-transition to demote from TEST back to DEV"
  </example>
  <example>
  Context: REVIEW passed, ready to merge
  user: "REVIEW passed, merge it"
  assistant: "I'll use ghe-transition to complete the workflow and merge"
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
- `enabled`: If false, skip transition
- `enforcement_level`: strict (all criteria) / standard (allow override) / lenient (advisory)
- `serena_sync`: If false, skip SERENA memory bank update

---

# GitHub Elements Transition

**Purpose**: Change phases by closing current thread and opening next. MODIFIES workflow state significantly.

## When to Use

- ENDING current phase
- STARTING next phase
- DEV complete → TEST
- TEST complete → REVIEW
- REVIEW PASS → merge
- Demotion (TEST→DEV or REVIEW→DEV)

## Valid Transitions

| From | To | Condition |
|------|-----|-----------|
| DEV | TEST | DEV complete, tests written |
| TEST | REVIEW | All tests pass |
| TEST | DEV | Structural issues (demotion) |
| REVIEW | DEV | FAIL verdict (demotion) |
| REVIEW | merge | PASS verdict |

## Invalid Transitions (Will Block)

- DEV → REVIEW (must go through TEST)
- REVIEW → TEST (must demote to DEV, never TEST)

## How to Execute

### Step 1: Validate with phase-gate

Spawn **phase-gate** agent to check:
- Prerequisites for transition are met
- No violations exist
- Target phase is valid
- Completion comments exist

If blocked:
- Report reason to user
- Do NOT proceed

### Step 2: Execute transition

Spawn appropriate thread manager for CURRENT phase:
- Closing DEV → **dev-thread-manager**
- Closing TEST → **test-thread-manager**
- Closing REVIEW → **review-thread-manager**

The thread manager will:
1. Post completion comment
2. Close current thread
3. Create/open next thread (with correct labels)
4. Link threads together

### Step 3: Sync memory

Spawn **memory-sync** agent to:
- Remove from activeContext.md
- Add to progress.md
- Set up for new thread

## Output

Confirmation including:
- Phase gate validation result
- Current thread closed
- New thread created/opened
- Links established
- Memory bank updated

## Key Differentiator

This skill CHANGES phases (closes one, opens another). To just SAVE progress without changing phases, use `ghe-checkpoint` instead.
