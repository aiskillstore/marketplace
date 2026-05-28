---
name: authorship-credit-gen
description: Use when determining author order on research manuscripts, assigning CRediT contributor roles for transparency, documenting individual contributions to collaborative projects, or resolving authorship disputes in multi-institutional research. Generates fair and transparent authorship assignments following ICMJE guidelines and CRediT taxonomy. Helps research teams document contributions, resolve disputes, and ensure equitable credit distribution in academic publications.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Research Authorship and Contributor Credit Generator

## When to Use

- Use this skill when the task needs Use when determining author order on research manuscripts, assigning CRediT contributor roles for transparency, documenting individual contributions to collaborative projects, or resolving authorship disputes in multi-institutional research. Generates fair and transparent authorship assignments following ICMJE guidelines and CRediT taxonomy. Helps research teams document contributions, resolve disputes, and ensure equitable credit distribution in academic publications.
- Use this skill for academic writing tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## Key Features

- Scope-focused workflow aligned to: Use when determining author order on research manuscripts, assigning CRediT contributor roles for transparency, documenting individual contributions to collaborative projects, or resolving authorship disputes in multi-institutional research. Generates fair and transparent authorship assignments following ICMJE guidelines and CRediT taxonomy. Helps research teams document contributions, resolve disputes, and ensure equitable credit distribution in academic publications.
- Packaged executable path(s): `scripts/main.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `dataclasses`: `unspecified`. Declared in `requirements.txt`.

## Example Usage

```bash
cd "20260318/scientific-skills/Academic Writing/authorship-credit-gen"
python -m py_compile scripts/main.py
python scripts/main.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/main.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

See `## Workflow` above for related details.

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/main.py`.
- Reference guidance: `references/` contains supporting rules, prompts, or checklists.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## Quick Check

Use this command to verify that the packaged script entry point can be parsed before deeper execution.

```bash
python -m py_compile scripts/main.py
```

## Audit-Ready Commands

Use these concrete commands for validation. They are intentionally self-contained and avoid placeholder paths.

```bash
python -m py_compile scripts/main.py
python scripts/main.py --help
```

## Workflow

1. Confirm the user objective, required inputs, and non-negotiable constraints before doing detailed work.
2. Validate that the request matches the documented scope and stop early if the task would require unsupported assumptions.
3. Use the packaged script path or the documented reasoning path with only the inputs that are actually available.
4. Return a structured result that separates assumptions, deliverables, risks, and unresolved items.
5. If execution fails or inputs are incomplete, switch to the fallback path and state exactly what blocked full completion.

## When to Use This Skill

- determining author order on research manuscripts
- assigning CRediT contributor roles for transparency
- documenting individual contributions to collaborative projects
- resolving authorship disputes in multi-institutional research
- preparing contributor statements for journal submissions
- evaluating contribution equity in research teams

## Quick Start

```python
from scripts.main import AuthorshipCreditGen

# Initialize the tool
tool = AuthorshipCreditGen()

from scripts.authorship_credit import AuthorshipCreditGenerator

generator = AuthorshipCreditGenerator(guidelines="ICMJEv4")

# Document contributions
contributions = {
    "Dr. Sarah Chen": [
        "Conceptualization",
        "Methodology", 
        "Writing - Original Draft",
        "Supervision"
    ],
    "Dr. Michael Roberts": [
        "Data Curation",
        "Formal Analysis",
        "Writing - Review & Editing"
    ],
    "Dr. Lisa Zhang": [
        "Investigation",
        "Resources",
        "Validation"
    ]
}

# Generate fair authorship order
authorship = generator.determine_order(
    contributions=contributions,
    criteria=["intellectual_input", "execution", "writing", "supervision"],
    weights={"intellectual_input": 0.4, "execution": 0.3, "writing": 0.2, "supervision": 0.1}
)

print(f"First author: {authorship.first_author}")
print(f"Corresponding: {authorship.corresponding_author}")
print(f"Author order: {authorship.ordered_list}")

# Generate CRediT statement
credit_statement = generator.generate_credit_statement(
    contributions=contributions,
    format="journal_submission"
)

# Check for disputes
dispute_check = generator.check_equity_issues(authorship)
if dispute_check.has_issues:
    print(f"Recommendations: {dispute_check.recommendations}")
```

## Core Capabilities

### 1. Generate Fair Authorship Orders

Analyze contributions using weighted criteria to determine equitable author ranking.

```python

# Define weighted contribution criteria
weights = {
    "conceptualization": 0.25,
    "methodology_design": 0.20,
    "data_collection": 0.15,
    "analysis": 0.15,
    "manuscript_writing": 0.15,
    "supervision": 0.10
}

# Calculate contribution scores
scores = tool.calculate_contribution_scores(
    contributions=team_contributions,
    weights=weights
)

# Generate ordered author list
authorship_order = tool.generate_author_order(scores)
print(f"Recommended order: {authorship_order}")
```

### 2. Assign CRediT Roles

Map contributions to official CRediT (Contributor Roles Taxonomy) categories.

```python

# Map contributions to CRediT roles
credit_roles = tool.assign_credit_roles(
    contributions=contributions,
    version="CRediT_2021"
)

# Generate CRediT statement for journal
statement = tool.generate_credit_statement(
    roles=credit_roles,
    format="JATS_XML"
)

# Validate role assignments
validation = tool.validate_credit_roles(credit_roles)
if validation.is_valid:
    print("CRediT roles properly assigned")
```

### 3. Detect Contribution Inequities

Identify potential authorship disputes before submission.

```python

# Analyze contribution distribution
equity_analysis = tool.analyze_equity(
    contributions=contributions,
    thresholds={"min_substantial": 0.15}
)

# Flag potential issues
if equity_analysis.has_inequities:
    for issue in equity_analysis.issues:
        print(f"Warning: {issue.description}")
        print(f"Recommendation: {issue.recommendation}")

# Generate equity report
report = tool.generate_equity_report(equity_analysis)
```

### 4. Generate Journal-Ready Statements

Create formatted contributor statements for various journal requirements.

```python

# Generate for Nature-style statement
nature_statement = tool.generate_contributor_statement(
    style="Nature",
    include_competing_interests=True
)

# Generate for Science-style statement  
science_statement = tool.generate_contributor_statement(
    style="Science",
    include_author_contributions=True
)

# Export in multiple formats
tool.export_statement(
    statement=nature_statement,
    formats=["docx", "pdf", "txt"]
)
```

## Command Line Usage

```text
python scripts/main.py --contributions contributions.json --guidelines ICMJE --output authorship_order.json
```

## Best Practices

- Discuss authorship expectations at project inception
- Document contributions continuously throughout project
- Review and agree on author order before submission
- Include non-author contributors in acknowledgments

## Quality Checklist

Before using this skill, ensure you have:
- [ ] Clear understanding of your objectives
- [ ] Necessary input data prepared and validated
- [ ] Output requirements defined
- [ ] Reviewed relevant documentation

After using this skill, verify:
- [ ] Results meet your quality standards
- [ ] Outputs are properly formatted
- [ ] Any errors or warnings have been addressed
- [ ] Results are documented appropriately

## References

- `references/guide.md` - Comprehensive user guide
- `references/examples/` - Working code examples
- `references/api-docs/` - Complete API documentation

---

**Skill ID**: 766 | **Version**: 1.0 | **License**: MIT

## Output Requirements

Every final response should make these items explicit when they are relevant:

- Objective or requested deliverable
- Inputs used and assumptions introduced
- Workflow or decision path
- Core result, recommendation, or artifact
- Constraints, risks, caveats, or validation needs
- Unresolved items and next-step checks

## Error Handling

- If required inputs are missing, state exactly which fields are missing and request only the minimum additional information.
- If the task goes outside the documented scope, stop instead of guessing or silently widening the assignment.
- If `scripts/main.py` fails, report the failure point, summarize what still can be completed safely, and provide a manual fallback.
- Do not fabricate files, citations, data, search results, or execution outcomes.

## Input Validation

This skill accepts requests that match the documented purpose of `authorship-credit-gen` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `authorship-credit-gen` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

## References

- [references/audit-reference.md](references/audit-reference.md) - Supported scope, audit commands, and fallback boundaries

## Response Template

Use the following fixed structure for non-trivial requests:

1. Objective
2. Inputs Received
3. Assumptions
4. Workflow
5. Deliverable
6. Risks and Limits
7. Next Checks

If the request is simple, you may compress the structure, but still keep assumptions and limits explicit when they affect correctness.
