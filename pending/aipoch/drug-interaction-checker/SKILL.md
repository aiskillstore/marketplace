---
name: drug-interaction-checker
description: Check for interactions between multiple medications, including severity classification and mechanism explanations.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Drug Interaction Checker

Check for interactions between multiple medications, including severity classification and mechanism explanations.

## When to Use

- Use this skill when the task needs Check for interactions between multiple medications, including severity classification and mechanism explanations.
- Use this skill for evidence insight tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## Key Features

See `## Features` above for related details.

- Scope-focused workflow aligned to: Check for interactions between multiple medications, including severity classification and mechanism explanations.
- Packaged executable path(s): `scripts/main.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

See `## Prerequisites` above for related details.

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `dataclasses`: `unspecified`. Declared in `requirements.txt`.
- `enum`: `unspecified`. Declared in `requirements.txt`.

## Example Usage

See `## Usage` above for related details.

```bash
cd "20260318/scientific-skills/Evidence Insight/drug-interaction-checker"
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

## Features

- **Multi-drug analysis**: Check interactions between 2+ medications simultaneously
- **Severity classification**: Critical / Major / Moderate / Minor / Unknown
- **Mechanism explanation**: Pharmacological basis for each interaction
- **Clinical guidance**: Recommendations for management

## Severity Levels

| Level | Description | Action Required |
|-------|-------------|-----------------|
| **Critical** | Life-threatening interaction | Absolute contraindication |
| **Major** | Significant risk, may need medical intervention | Avoid combination or monitor closely |
| **Moderate** | Moderate risk, may require dose adjustment | Monitor for adverse effects |
| **Minor** | Mild interaction, unlikely to cause issues | Be aware, usually acceptable |
| **Unknown** | Insufficient data | Proceed with caution |

## Usage

### Python Script

```text
python scripts/main.py --drugs "Warfarin" "Aspirin" "Ibuprofen"
```

### As a Module

```python
from scripts.main import check_interactions

result = check_interactions(["Metformin", "Simvastatin", "Amlodipine"])
```

## Parameters

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `--drugs` | list | - | Yes | List of drug names (generic or brand names accepted) |
| `--format` | string | text | No | Output format (text, json, markdown) |
| `--include-mechanism` | flag | true | No | Include pharmacological mechanism |
| `--include-management` | flag | true | No | Include clinical recommendations |
| `--output`, `-o` | string | - | No | Output file path |

## Output Format

```json
{
  "drugs_checked": ["Drug A", "Drug B"],
  "interactions": [
    {
      "drug_pair": ["Drug A", "Drug B"],
      "severity": "Major",
      "mechanism": "Pharmacodynamic synergism...",
      "effect": "Increased bleeding risk",
      "recommendation": "Avoid combination or monitor INR closely"
    }
  ],
  "summary": {
    "critical": 0,
    "major": 1,
    "moderate": 0,
    "minor": 0
  }
}
```

## Data Sources

This skill uses a curated drug interaction database stored in `references/interactions_db.json`. The database includes:

- FDA-approved drug interaction data
- Known metabolic pathways (CYP450 enzymes)
- Pharmacodynamic interactions
- Common supplement interactions

## Limitations

- Database may not include all possible drug combinations
- Always consult healthcare professionals for medical decisions
- Does not account for patient-specific factors (age, renal function, etc.)
- Not a substitute for professional medical advice

## Technical Difficulty

**High** - Requires extensive pharmacological knowledge database, accurate severity classification, and clear mechanism explanations.

## References

See `references/` directory for:
- `interactions_db.json` - Drug interaction database
- `severity_criteria.md` - Classification criteria
- `cyp450_substrates.json` - Metabolic pathway data

## Risk Assessment

| Risk Indicator | Assessment | Level |
|----------------|------------|-------|
| Code Execution | Python/R scripts executed locally | Medium |
| Network Access | No external API calls | Low |
| File System Access | Read input files, write output files | Medium |
| Instruction Tampering | Standard prompt guidelines | Low |
| Data Exposure | Output files saved to workspace | Low |

## Security Checklist

- [ ] No hardcoded credentials or API keys
- [ ] No unauthorized file system access (../)
- [ ] Output does not expose sensitive information
- [ ] Prompt injection protections in place
- [ ] Input file paths validated (no ../ traversal)
- [ ] Output directory restricted to workspace
- [ ] Script execution in sandboxed environment
- [ ] Error messages sanitized (no stack traces exposed)
- [ ] Dependencies audited

## Prerequisites

```text

# Python dependencies
pip install -r requirements.txt
```

## Evaluation Criteria

### Success Metrics
- [ ] Successfully executes main functionality
- [ ] Output meets quality standards
- [ ] Handles edge cases gracefully
- [ ] Performance is acceptable

### Test Cases
1. **Basic Functionality**: Standard input → Expected output
2. **Edge Case**: Invalid input → Graceful error handling
3. **Performance**: Large dataset → Acceptable processing time

## Lifecycle Status

- **Current Stage**: Draft
- **Next Review Date**: 2026-03-06
- **Known Issues**: None
- **Planned Improvements**: 
  - Performance optimization
  - Additional feature support

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

This skill accepts requests that match the documented purpose of `drug-interaction-checker` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `drug-interaction-checker` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

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
