---
name: workflow-orchestration
description: Coordinates multi-step CI/CD pipelines by chaining autonomous-ci, code-review, smart-commit, and jules-integration plugins. Use when executing validation-to-PR workflows or recovering from CI failures.
---

# Skill: workflow-orchestration

## Overview

This skill orchestrates complex workflows by chaining existing plugins into pipelines.
It maintains state awareness through CHANGELOG.md and coordinates cross-plugin operations.

## When to Use

- **Pre-commit validation**: Before any commit, ensure all quality gates pass
- **PR creation**: When changes are ready for review and PR creation
- **CI recovery**: When CI fails and automated diagnosis/fix is needed
- **Multi-step automation**: Any task requiring coordinated plugin execution

## Prerequisites

**Required Plugins:**

- `autonomous-ci` - Validation and CI monitoring
- `code-review` - Quality analysis
- `smart-commit` - Commit message generation

**Optional Plugins:**

- `jules-integration` - Async PR delegation

**Required Skills (from Superpowers):**

- `systematic-debugging` - For failure analysis
- `verification-before-completion` - For evidence-based completion

## Process

### Phase 1: Context Gathering

Before executing any pipeline:

```bash
# 1. Read CHANGELOG for recent context
Read the file: CHANGELOG.md
# Focus on [Unreleased] section to understand pending work

# 2. Check git state
git status --porcelain
git log --oneline -5

# 3. Verify required plugins are available
claude plugin list
```

### Phase 2: Pipeline Selection

Choose the appropriate pipeline based on the task:

| Task | Pipeline | Plugins Used |
|------|----------|--------------|
| Validate before commit | `pre-commit` | autonomous-ci, code-review, smart-commit |
| Create PR | `pr-create` | All + jules-integration |
| Fix CI failure | `ci-recover` | autonomous-ci + systematic-debugging |

### Phase 3: Pipeline Execution

#### Pre-Commit Pipeline

```text
Step 1: Validate
├── Run: ./tooling/scripts/local-validate.sh
├── On success: Continue
└── On failure: STOP, report issues

Step 2: Review
├── Invoke: code-review skill
├── Analyze: Security, style, performance
├── On success: Continue
└── On failure: Report issues, suggest fixes

Step 3: Commit Message
├── Invoke: smart-commit skill
├── Generate: Conventional commit message
├── On success: Present message for human approval
└── On failure: Provide manual template
```

#### PR-Create Pipeline

```text
Step 1: Pre-Commit Pipeline
├── Execute full pre-commit pipeline
└── On failure: STOP

Step 2: Stage Changes
├── Present diff for human review
├── REQUIRE: Human approval for git commit
└── On approval: Continue

Step 3: Delegate to Jules
├── Invoke: jules-integration skill
├── Create: Jules session with PR task
├── Set: requirePlanApproval = true
└── Monitor: Session status
```

#### CI-Recover Pipeline

```text
Step 1: Diagnose
├── Invoke: systematic-debugging skill
├── Analyze: CI failure logs
├── Identify: Root cause
└── On failure: Escalate to human

Step 2: Fix
├── Implement fix based on diagnosis
├── Follow TDD if adding code
└── On failure: Escalate with context

Step 3: Re-validate
├── Run: ./tooling/scripts/local-validate.sh
├── On success: Report recovery
├── On failure: Retry (max 3 times)
└── On max retries: Escalate
```

### Phase 4: Completion

**ALWAYS verify before claiming complete:**

```bash
# Run validation
./tooling/scripts/local-validate.sh

# Check all tests pass
# (if applicable)

# Update CHANGELOG.md under [Unreleased]
```

**Report with evidence:**

```markdown
## Pipeline Execution Summary

| Step | Status | Evidence |
|------|--------|----------|
| Validation | ✅ | local-validate.sh passed |
| Review | ✅ | No critical issues |
| Commit | ⏳ | Awaiting human approval |

### Artifacts

- Commit message: `feat: add workflow orchestration`
- Files changed: 5
- Lines: +230 / -12
```

## State Management

The orchestrator reads state from multiple sources:

### CHANGELOG.md

```bash
# Extract pending work
grep -A 50 "\[Unreleased\]" CHANGELOG.md
```

Provides:

- What's been added/changed/fixed
- What's pending
- Recent decisions and context

### Git State

```bash
git status --porcelain    # Working directory state
git log --oneline -5      # Recent commits
git diff --stat           # Changes summary
```

### CI State

```bash
# Via autonomous-ci skill
./plugins/autonomous-ci/scripts/wait-for-ci.sh
```

## Error Handling

### Validation Failures

1. Parse error output
2. Identify failing check (shellcheck, markdownlint, plugin validation)
3. Attempt automatic fix if deterministic
4. Re-run validation
5. If still failing after 3 attempts, report with full context

### Review Failures

1. Collect all review issues
2. Categorize by severity (critical, warning, info)
3. For critical issues: STOP and report
4. For warnings: Report and continue with human acknowledgment

### Jules API Failures

1. Check API key validity
2. Retry with exponential backoff (5s, 15s, 30s)
3. If persistent, report and suggest manual PR creation

## Integration with Other Skills

### From Superpowers

| Skill | When Used |
|-------|-----------|
| `systematic-debugging` | CI failure diagnosis |
| `test-driven-development` | Writing fixes |
| `verification-before-completion` | Before claiming done |
| `brainstorming` | Complex architectural decisions |

### From This Repo

| Skill | When Used |
|-------|-----------|
| `autonomous-ci` | Validation and monitoring |
| `code-review` | Quality analysis |
| `smart-commit` | Commit generation |
| `jules-integration` | PR delegation |
| `working-on-ancplua-plugins` | Repo conventions |

## Examples

### Example 1: Pre-Commit Flow

**Trigger:** Developer requests validation before commit

```text
1. Read CHANGELOG.md → Understand context
2. Run local-validate.sh → All checks pass
3. Invoke code-review → No critical issues
4. Invoke smart-commit → Generate: "feat(agent): add workflow orchestrator"
5. Present summary → Human approves
6. Report complete with evidence
```

### Example 2: CI Recovery

**Trigger:** CI fails on shellcheck

```text
1. Detect failure via autonomous-ci monitoring
2. Invoke systematic-debugging:
   - Phase 1: Gather evidence (CI logs)
   - Phase 2: Identify cause (SC2086 unquoted variable)
   - Phase 3: Hypothesize fix (add quotes)
   - Phase 4: Verify fix locally
3. Apply fix to script
4. Run local-validate.sh → Passes
5. Report recovery with evidence
```

### Example 3: Full PR Pipeline

**Trigger:** Feature complete, ready for review

```text
1. Execute pre-commit pipeline → All green
2. Present diff for human review
3. Human approves commit
4. Invoke jules-integration:
   - Create session: "Create PR for workflow-orchestrator agent"
   - Set requirePlanApproval: true
   - Monitor session
5. Report PR URL when created
```

## Maintenance Rules for Claude

1. **Never skip validation** - Always run local-validate.sh before completion
2. **Always read CHANGELOG first** - Context prevents duplicate work
3. **Chain skills, don't reinvent** - Use existing plugins instead of custom logic
4. **Require human approval for commits** - Orchestration ≠ autonomous commits
5. **Report with evidence** - Tables with status and artifacts
6. **Update CHANGELOG** - Every pipeline execution that changes files
