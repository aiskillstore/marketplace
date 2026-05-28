---
name: usmle-case-generator
description: Generate USMLE Step 1/2 style clinical cases with patient history, physical.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# USMLE Case Generator

Generate USMLE Step 1 and Step 2 CK style clinical cases for medical education and board exam preparation.

## When to Use

- Use this skill when the task is to Generate USMLE Step 1/2 style clinical cases with patient history, physical.
- Use this skill for academic writing tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## Key Features

See `## Features` above for related details.

- Scope-focused workflow aligned to: Generate USMLE Step 1/2 style clinical cases with patient history, physical.
- Packaged executable path(s): `scripts/main.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- Python 3.8+
- No external API dependencies (template-based generation)
- Optional: LLM integration for case variation

## Example Usage

See `## Usage` above for related details.

```bash
cd "20260318/scientific-skills/Academic Writing/usmle-case-generator"
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

- **Step 1 Cases**: Basic science concepts, pathophysiology, pharmacology
- **Step 2 Cases**: Clinical diagnosis, management, next best steps
- **Complete Vignettes**: History, physical exam, labs, imaging
- **Multiple Choice Questions**: Single best answer format
- **Answer Explanations**: Detailed rationale for learning

## Usage

```python

# Generate a Step 1 case (pathophysiology focus)
python scripts/main.py --step 1 --topic cardiology --difficulty medium

# Generate a Step 2 case (clinical management focus)
python scripts/main.py --step 2 --topic nephrology --include-diagnosis

# Generate case with specific conditions
python scripts/main.py --step 2 --condition "diabetic ketoacidosis" --format json
```

## Parameters

| Parameter | Options | Description |
|-----------|---------|-------------|
| `--step` | 1, 2 | USMLE Step level |
| `--topic` | See references/topics.json | Medical specialty |
| `--condition` | Any condition | Specific disease/condition |
| `--difficulty` | easy, medium, hard | Case complexity |
| `--format` | text, json, markdown | Output format |
| `--include-diagnosis` | flag | Include answer key |
| `--count` | 1-10 | Number of cases to generate |

## Topics Covered

- Cardiology
- Pulmonology
- Gastroenterology
- Nephrology
- Endocrinology
- Hematology/Oncology
- Infectious Disease
- Neurology
- Psychiatry
- Musculoskeletal
- Dermatology
- Obstetrics/Gynecology
- Pediatrics
- Surgery

## Case Structure

Each generated case includes:

1. **Patient Demographics**: Age, gender, relevant background
2. **Chief Complaint**: Presenting problem
3. **History of Present Illness**: Detailed symptom timeline
4. **Past Medical History**: Relevant comorbidities
5. **Medications**: Current drug regimen
6. **Allergies**: Drug/environmental allergies
7. **Family History**: Genetic conditions
8. **Social History**: Smoking, alcohol, occupation
9. **Physical Examination**: Vital signs, relevant findings
10. **Laboratory Studies**: CBC, CMP, specific markers
11. **Imaging/Diagnostics**: X-ray, CT, ECG, etc.
12. **Question**: USMLE-style multiple choice
13. **Answer Options**: 5 choices (A-E)
14. **Correct Answer**: With detailed explanation
15. **Educational Objectives**: Key learning points

## Output Formats

### Text Format (Default)
Plain text suitable for printing or reading.

### JSON Format
Structured data for integration with applications.

### Markdown Format
Formatted for documentation or web display.

## Technical Difficulty

**High** - Requires medical knowledge validation and clinical accuracy.

⚠️ **Manual Review Required**: Generated cases should be reviewed by medical professionals before use in high-stakes educational settings.

## References

- `references/topics.json` - Medical specialty taxonomy
- `references/case_templates.json` - Case structure templates
- `references/usmle_patterns.md` - USMLE question patterns
- `references/conditions/` - Condition-specific case data

## Example Output

```
Case: A 58-year-old male with chest pain

A 58-year-old man presents to the emergency department with 
crushing substernal chest pain radiating to his left arm, 
beginning 2 hours ago at rest...

[History, physical, labs, ECG findings...]

Question: What is the most appropriate next step in management?

A. Administer aspirin and nitroglycerin
B. Order CT pulmonary angiography
C. Perform immediate synchronized cardioversion
D. Start heparin drip and call cardiology
E. Discharge with outpatient stress test

Correct Answer: D
Explanation: [Detailed rationale...]
```

## Safety & Limitations

- Cases are AI-generated and may contain inaccuracies
- Not a substitute for professional medical education
- Always verify clinical details with authoritative sources
- Intended for educational purposes only

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

This skill accepts requests that match the documented purpose of `usmle-case-generator` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `usmle-case-generator` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

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
