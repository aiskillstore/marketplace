---
name: fiftyone-pr-triage
description: Triage FiftyOne GitHub issues by validating status, categorizing resolution, and generating standardized responses. Use when reviewing issues to determine if fixed, won't fix, not reproducible, no longer relevant, or still valid.
---

# FiftyOne Issue Triage

## Triage Categories

| Category | When to Use |
|----------|-------------|
| **Already Fixed** | Issue resolved in recent commits/releases |
| **Won't Fix** | By design, out of scope, or not aligned with project goals |
| **Not Reproducible** | Cannot reproduce with provided info |
| **No Longer Relevant** | Outdated FiftyOne version, deprecated feature, or stale |
| **Still Valid** | Confirmed bug or valid feature request |

## Triage Workflow

### Step 1: Read Issue Details

Extract key information:
```
- Issue type: [BUG] / [FR] / [?]
- FiftyOne version reported
- Code to reproduce
- Error message/traceback
- Related module/feature
```

### Step 2: Search Codebase

```bash
# Search for related code
grep -r "keyword" fiftyone/
grep -r "ClassName" fiftyone/core/

# Find the module mentioned in issue
find fiftyone/ -name "*.py" | xargs grep -l "function_name"
```

### Step 3: Check Git History

```bash
# Recent commits related to issue
git log --oneline --since="2024-01-01" -- fiftyone/path/to/module.py

# Search commit messages
git log --oneline --grep="keyword"

# Check if specific function was modified
git log -p --all -S "function_name" -- "*.py"

# Blame specific lines
git blame fiftyone/path/to/file.py -L 100,120
```

### Step 4: Check Related PRs/Issues

```bash
# Search closed issues
gh issue list --repo voxel51/fiftyone --state closed --search "keyword"

# Search PRs
gh pr list --repo voxel51/fiftyone --state merged --search "keyword"
```

### Step 5: Categorize and Respond

Based on findings, select category and use appropriate response template.

## Category Decision Tree

```
Issue reported
    │
    ├─ Can reproduce?
    │   ├─ NO → "Not Reproducible"
    │   └─ YES ↓
    │
    ├─ Fixed in recent commit/release?
    │   ├─ YES → "Already Fixed"
    │   └─ NO ↓
    │
    ├─ Is this by design or out of scope?
    │   ├─ YES → "Won't Fix"
    │   └─ NO ↓
    │
    ├─ Is issue still relevant? (version, feature exists)
    │   ├─ NO → "No Longer Relevant"
    │   └─ YES → "Still Valid"
```

## Response Templates

### Already Fixed

```markdown
Hi @{author},

This issue has been addressed in {version/commit}.

**Fix details:**
- PR: #{pr_number} or Commit: `{commit_hash}`
- File: `{filepath}`
- Change: {brief description}

**To resolve:**
```bash
pip install --upgrade fiftyone
```

Please update and let us know if the issue persists.
```

### Won't Fix

```markdown
Hi @{author},

Thank you for the detailed report. After investigation, we've determined this is {reason}:

**Reason:** {explanation}

{alternative_if_applicable}

We're closing this issue, but feel free to reopen if you have additional context.
```

**Common reasons:**
- Working as designed
- Out of project scope
- Would break backward compatibility
- Performance/complexity tradeoff

### Not Reproducible

```markdown
Hi @{author},

We were unable to reproduce this issue with the provided information.

**Environment tested:**
- FiftyOne: v{version}
- Python: {python_version}
- OS: {os}

**Could you provide:**
1. Minimal reproducible example
2. Complete error traceback
3. Sample data (if applicable)

We'll reopen once we can reproduce.
```

### No Longer Relevant

```markdown
Hi @{author},

This issue appears to be no longer relevant:

**Reason:** {reason}

{details}

If you're still experiencing this on FiftyOne v{current_version}, please open a new issue with updated details.
```

**Common reasons:**
- Reported version is significantly outdated
- Related feature was deprecated/removed
- No activity for 6+ months
- Duplicate of resolved issue

### Still Valid

```markdown
Hi @{author},

Confirmed this issue. Here's our analysis:

**Summary:**
{brief description of the bug/feature}

**Root cause:**
{technical explanation with code reference}

**Suggested fix:**
{approach or PR if proposing one}

**Affected code:**
- File: `{filepath}:{line_number}`
- Function: `{function_name}`

{next_steps}
```

## Code Reference Format

When referencing code in responses:

```markdown
**Location:** `fiftyone/core/module.py:123`

**Current behavior:**
```python
# Line 123-130
def problematic_function():
    ...
```

**Suggested change:**
```python
def fixed_function():
    ...
```
```

## Investigation Checklist

Before categorizing, verify:

- [ ] Read full issue description and comments
- [ ] Checked FiftyOne version reported vs current
- [ ] Searched codebase for related code
- [ ] Checked git history for recent fixes
- [ ] Searched closed issues for duplicates
- [ ] Attempted reproduction (if bug)
- [ ] Identified root cause or reason

## Quick Reference

| Category | Key Indicator | Response Action |
|----------|---------------|-----------------|
| Already Fixed | Found fix in git log | Point to PR/commit, suggest upgrade |
| Won't Fix | By design or out of scope | Explain reasoning, suggest alternative |
| Not Reproducible | Can't reproduce | Request more info |
| No Longer Relevant | Old version, stale, deprecated | Explain why, suggest new issue |
| Still Valid | Confirmed, no fix exists | Document root cause, propose fix |
