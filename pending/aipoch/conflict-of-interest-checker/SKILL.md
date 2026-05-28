---
name: conflict-of-interest-checker
description: Check for co-authorship and institutional conflicts between authors and suggested reviewers to support peer review integrity. Coauthorship and institutional conflict detection supported.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Conflict of Interest Checker

Reviewer conflict detection tool for journal submissions and editorial decisions.

## Quick Check

```bash
python -m py_compile scripts/main.py
```

## Audit-Ready Commands

```bash
python -m py_compile scripts/main.py
python scripts/main.py --help
python scripts/main.py --authors "Smith,Jones,Lee" --reviewers "Brown,Davis,Wilson"
```

## When to Use

- Journal submission preparation
- Editorial conflict screening
- Peer review integrity verification
- Compliance verification for grant review panels

## Workflow

1. Confirm the user objective, required inputs, and non-negotiable constraints before doing detailed work.
2. Validate that the request matches the documented scope and stop early if the task would require unsupported assumptions.
3. Use the packaged script path or the documented reasoning path with only the inputs that are actually available.
4. Return a structured result that separates assumptions, deliverables, risks, and unresolved items.
5. If execution fails or inputs are incomplete, switch to the fallback path and state exactly what blocked full completion.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--authors`, `-a` | string | Yes | Comma-separated author names |
| `--reviewers`, `-r` | string | Yes | Comma-separated reviewer names |
| `--publications`, `-p` | string | No | CSV file with publication records |

### CSV Format

```csv
author,reviewer,paper_id
Smith,Brown,paper1
Smith,Jones,paper2
```

> **Known limitations:** (1) `check_collaboration_conflict()` is a stub that always returns an empty list — only coauthorship conflicts (via shared paper IDs) are actively detected. (2) `check_institutional_conflict()` has a NameError bug at line 59 — use the Claude Direct Path below instead of calling this method directly.

## Usage

```bash
# Check with demo data
python scripts/main.py --authors "Smith,Jones,Lee" --reviewers "Brown,Davis,Wilson"

# Check with publication records
python scripts/main.py --authors "Smith,Jones" --reviewers "Brown,Davis" --publications pubs.csv
```

## Output

- Conflict flagging (coauthorship)
- Shared publication list
- Recommendation: Accept/Recuse

### Example Output

```
⚠ Found 2 potential conflict(s):

1. COAUTHORSHIP CONFLICT
   Reviewer: Brown
   Author: Smith
   Shared papers: paper1

2. COAUTHORSHIP CONFLICT
   Reviewer: Wilson
   Author: Smith
   Shared papers: paper2
```

## Institutional Conflict — Claude Direct Path

The script's `check_institutional_conflict()` method has a known NameError bug (the `reviewer` variable is not defined in the method scope at line 59). When institutional conflict checking is needed, use this Claude Direct path instead:

1. Ask the user for: reviewer name, reviewer institution, and a list of author names with their institutions.
2. Compare reviewer institution against each author institution (case-insensitive).
3. Flag any reviewer-author pair sharing the same institution as an INSTITUTIONAL CONFLICT.
4. Report in the same format as coauthorship conflicts, with `conflict_type: "institutional"`.
5. Note: "Institutional conflict detected via Claude Direct path — script method has a known bug and was bypassed."

## Stress-Case Rules

For complex multi-constraint requests, always include these blocks:

1. Assumptions
2. Hard Constraints
3. Conflict Detection Path
4. Residual Risks
5. Unresolved Items

## Input Validation

This skill accepts requests involving co-authorship conflict detection between manuscript authors and proposed reviewers.

If the user's request does not involve conflict-of-interest checking for peer review — for example, asking to write a review, evaluate manuscript quality, or perform general author searches — do not proceed with the workflow. Instead respond:
> "conflict-of-interest-checker is designed to detect co-authorship and institutional conflicts between authors and reviewers. Your request appears to be outside this scope. Please provide author and reviewer name lists, or use a more appropriate tool for your task."

## Output Requirements

Every final response must include:

- Objective or requested deliverable
- Inputs used and assumptions introduced
- Workflow or decision path
- Core result, recommendation, or artifact
- Constraints, risks, caveats, or validation needs
- Unresolved items and next-step checks

## Error Handling

- If `--authors` or `--reviewers` are missing, request them before proceeding.
- If `--publications` CSV is malformed or missing expected columns (`author`, `paper_id`), report the error and fall back to demo data with a warning.
- If institutional conflict checking is requested, use the Claude Direct Path above — do not call `check_institutional_conflict()` directly.
- If the task goes outside the documented scope, stop instead of guessing or silently widening the assignment.
- If `scripts/main.py` fails, report the failure point, summarize what still can be completed safely, and provide a manual fallback.
- Do not fabricate files, citations, data, search results, or execution outcomes.

## Response Template

1. Objective
2. Inputs Received
3. Assumptions
4. Workflow
5. Deliverable
6. Risks and Limits
7. Next Checks
