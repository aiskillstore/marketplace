---
name: cross-disciplinary-bridge-finder
description: Use when identifying collaboration opportunities across fields, finding experts in complementary disciplines, translating methodologies between scientific domains, or building interdisciplinary research teams. Identifies synergies between scientific disciplines, matches researchers with complementary expertise, and facilitates cross-domain collaborations. Supports interdisciplinary grant applications and innovative research team formation.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Cross-Disciplinary Research Collaboration Finder

## When to Use

- Use this skill when the task needs Use when identifying collaboration opportunities across fields, finding experts in complementary disciplines, translating methodologies between scientific domains, or building interdisciplinary research teams. Identifies synergies between scientific disciplines, matches researchers with complementary expertise, and facilitates cross-domain collaborations. Supports interdisciplinary grant applications and innovative research team formation.
- Use this skill for evidence insight tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## Key Features

- Scope-focused workflow aligned to: Use when identifying collaboration opportunities across fields, finding experts in complementary disciplines, translating methodologies between scientific domains, or building interdisciplinary research teams. Identifies synergies between scientific disciplines, matches researchers with complementary expertise, and facilitates cross-domain collaborations. Supports interdisciplinary grant applications and innovative research team formation.
- Packaged executable path(s): `scripts/main.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `dataclasses`: `unspecified`. Declared in `requirements.txt`.
- `networkx`: `unspecified`. Declared in `requirements.txt`.
- `numpy`: `unspecified`. Declared in `requirements.txt`.
- `sklearn`: `unspecified`. Declared in `requirements.txt`.
- `networkx`: `>=2.8`. Declared in `scripts/requirements.txt`.
- `numpy`: `>=1.21`. Declared in `scripts/requirements.txt`.
- `pandas`: `>=1.3`. Declared in `scripts/requirements.txt`.
- `scikit-learn`: `>=1.0`. Declared in `scripts/requirements.txt`.
- `matplotlib`: `>=3.5`. Declared in `scripts/requirements.txt`.
- `seaborn`: `>=0.11`. Declared in `scripts/requirements.txt`.
- `openai`: `>=1.0`. Declared in `scripts/requirements.txt`.

## Example Usage

```bash
cd "20260318/scientific-skills/Evidence Insight/cross-disciplinary-bridge-finder"
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

- identifying collaboration opportunities across fields
- finding experts in complementary disciplines
- translating methodologies between scientific domains
- building interdisciplinary research teams
- discovering funding for interdisciplinary projects
- mapping knowledge transfer pathways

## Quick Start

```python
from scripts.interdisciplinary import CollaborationFinder

finder = CollaborationFinder()

# Find collaborators in different field
collaborators = finder.find_experts(
    my_expertise="machine_learning",
    target_field="immunology",
    collaboration_type="co_authorship",
    min_publications=10,
    h_index_threshold=15
)

if not collaborators:
    print("No collaborators found — try lowering min_publications or h_index_threshold.")
else:
    # Validate quality before proceeding: only consider complementarity_score > 0.7
    qualified = [e for e in collaborators if e.complementarity_score > 0.7]
    print(f"Found {len(collaborators)} candidates; {len(qualified)} meet quality threshold (score > 0.7):")
    for expert in qualified[:5]:
        print(f"  - {expert.name} ({expert.institution})")
        print(f"    Research: {expert.research_focus}")
        print(f"    Complementarity score: {expert.complementarity_score}")

# Identify transferable methods
methods = finder.identify_transferable_methods(
    from_field="physics",
    to_field="biology",
    application_area="systems_modeling"
)

if not methods:
    print("No transferable methods found — consider broadening the application_area.")
else:
    # Validate applicability before proceeding: review transfer_potential
    for method in methods:
        print(f"Method: {method.name}")
        print(f"  Success in source field: {method.success_rate}")
        print(f"  Application potential: {method.transfer_potential}")
        if method.transfer_potential < 0.6:
            print(f"  ⚠ Low transfer potential — consider a different application_area.")

# Find interdisciplinary funding
grants = finder.find_interdisciplinary_funding(
    fields=["AI", "medicine", "ethics"],
    funder_types=["NIH", "NSF", "private_foundation"],
    deadline_within_months=6
)

if not grants:
    print("No grants found — try extending deadline_within_months or broadening funder_types.")

# Generate collaboration proposal outline
proposal_outline = finder.generate_collaboration_proposal(
    partner_expertise="clinical_trial_design",
    my_expertise="data_science",
    research_question="precision_medicine"
)
```

## Command Line Usage

```text
python scripts/main.py --my-field machine_learning --target-field immunology --find-collaborators --output matches.json
```

## Handling Poor Results

- **Empty collaborator list**: Lower `min_publications` or `h_index_threshold`; broaden `collaboration_type`.
- **No transferable methods**: Widen `application_area` to a higher-level domain (e.g., `"modeling"` instead of `"systems_modeling"`).
- **No funding results**: Extend `deadline_within_months` or add more entries to `funder_types`.
- **Weak proposal outline**: Ensure `research_question` is a descriptive string rather than a short keyword.

## References

- `references/guide.md` - Comprehensive user guide
- `references/examples/` - Working code examples
- `references/api-docs/` - Complete API documentation

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

This skill accepts requests that match the documented purpose of `cross-disciplinary-bridge-finder` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `cross-disciplinary-bridge-finder` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

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
