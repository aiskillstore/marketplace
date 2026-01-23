# EPIC Workflow Validation Scripts

## Overview

This directory contains validation scripts for the EPIC workflow that ensure subagents complete their assigned tasks and create required documentation.

## Scripts

### validate-phase.py

Validates that a specific EPIC phase has been completed by checking for required report files in the session directory.

**Usage:**
```bash
python validate-phase.py <phase> <session-dir>
```

**Parameters:**
- `<phase>`: The EPIC phase to validate (explore, research, plan, validate, implement, review, iterate)
- `<session-dir>`: Path to the session directory (e.g., `.claude/sessions/01-user-auth-feature`)

**Example:**
```bash
python validate-phase.py explore .claude/sessions/01-user-auth-feature
```

**Exit Codes:**
- `0`: Validation passed
- `1`: Validation failed (missing required files)

## EPIC Phases and Required Files

| Phase | Required File | Created By |
|-------|---------------|------------|
| Explore | `codebase-status.md` | codebase-explorer agent |
| Research | `research-report.md` | research-specialist agent |
| Plan | `implementation-plan.md` | strategic-planner agent |
| Validate | `validation-feedback.md` | consulting-expert agent |
| Implement | `implementation-complete.md` | main agent |
| Review | `quality-report.md` | review agents |
| Iterate | `final-verification.md` | main agent |

## Iterative Compliance Flow

The EPIC workflow enforces an iterative compliance pattern:

1. **Run validation** after completing a phase
2. **If validation PASSES**: Proceed to next phase
3. **If validation FAILS**:
   - Identify missing file(s)
   - Reinvoke the responsible subagent with explicit instruction to create missing file(s)
   - Re-run validation
   - Repeat until validation passes
4. **Do NOT proceed** to next phase until validation passes

This ensures:
- All subagents complete their assigned tasks
- Required documentation is created
- No phases are skipped or incomplete
- Full audit trail of the development process

## Session Directory Structure

All reports must be saved to: `.claude/sessions/[NN]-[session-description]/`

**Example session directory:**
```
.claude/sessions/01-user-auth-feature/
├── codebase-status.md
├── research-report.md
├── implementation-plan.md
├── validation-feedback.md
├── implementation-complete.md
├── quality-report.md
└── final-verification.md
```

**Naming convention:**
- `[NN]`: Two-digit number (e.g., 01, 02, 03)
- `[session-description]`: Descriptive name using hyphens (e.g., user-auth-feature)
