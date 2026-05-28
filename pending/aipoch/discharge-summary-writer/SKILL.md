---
name: discharge-summary-writer
description: Generate hospital discharge summaries from admission data, hospital course.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Discharge Summary Writer

Generate standardized, clinically accurate hospital discharge summaries by integrating all inpatient medical data.

## When to Use

- Use this skill when the task is to Generate hospital discharge summaries from admission data, hospital course.
- Use this skill for academic writing tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## Key Features

- Scope-focused workflow aligned to: Generate hospital discharge summaries from admission data, hospital course.
- Packaged executable path(s): `scripts/main.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

See `## Prerequisites` above for related details.

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

See `## Usage` above for related details.

```bash
cd "20260318/scientific-skills/Academic Writing/discharge-summary-writer"
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
python scripts/main.py -h
python scripts/main.py --help
```

## Workflow

1. Confirm the user objective, required inputs, and non-negotiable constraints before doing detailed work.
2. Validate that the request matches the documented scope and stop early if the task would require unsupported assumptions.
3. Use the packaged script path or the documented reasoning path with only the inputs that are actually available.
4. Return a structured result that separates assumptions, deliverables, risks, and unresolved items.
5. If execution fails or inputs are incomplete, switch to the fallback path and state exactly what blocked full completion.

## Input Requirements

### Required Patient Data
```json
{
  "patient_info": {
    "name": "string",
    "gender": "string",
    "age": "number",
    "medical_record_number": "string",
    "admission_date": "YYYY-MM-DD",
    "discharge_date": "YYYY-MM-DD",
    "department": "string",
    "attending_physician": "string"
  },
  "admission_data": {
    "chief_complaint": "string",
    "present_illness_history": "string",
    "past_medical_history": "string",
    "physical_examination": "string",
    "admission_diagnosis": ["string"]
  },
  "hospital_course": {
    "treatment_summary": "string",
    "procedures_performed": ["string"],
    "significant_findings": "string",
    "complications": ["string"],
    "consultations": ["string"]
  },
  "discharge_status": {
    "discharge_diagnosis": ["string"],
    "discharge_condition": "string",
    "hospital_stay_days": "number"
  },
  "medications": {
    "discharge_medications": [
      {
        "name": "string",
        "dosage": "string",
        "frequency": "string",
        "route": "string",
        "duration": "string"
      }
    ]
  },
  "follow_up": {
    "instructions": "string",
    "follow_up_appointments": ["string"],
    "warning_signs": ["string"],
    "activity_restrictions": "string",
    "diet_instructions": "string"
  }
}
```

## Usage

### Python Script
```text
python scripts/main.py --input patient_data.json --output discharge_summary.md --format standard
```

## Parameters

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `--input` | string | - | Yes | Path to JSON file containing patient data |
| `--output` | string | discharge_summary.md | No | Output file path |
| `--format` | string | standard | No | Output format (standard, structured, json) |
| `--template` | string | - | No | Custom template file path |
| `--language` | string | zh | No | Output language (zh or en) |

## Output Formats

### Standard Format
Human-readable markdown document following clinical discharge summary structure:
1. Patient Information
2. Admission Information
3. Hospital Course
4. Discharge Status
5. Discharge Medications
6. Follow-up Instructions
7. Physician Signature

### Structured Format
Sectioned markdown with clear headers for EMR integration.

### JSON Format
Machine-readable structured data for system integration.

## Technical Difficulty

**⚠️ HIGH - Manual Review Required**

This skill handles critical medical documentation. Output requires:
- Physician verification before use
- Compliance with local medical documentation standards
- Review for accuracy and completeness
- Institutional approval for template formats

## Safety Considerations

1. **Never use generated summaries without physician review**
2. **Verify all medication dosages and instructions**
3. **Confirm follow-up appointments with hospital scheduling system**
4. **Ensure discharge diagnoses match official medical records**
5. **Validate patient identifiers and dates**

## References

- `references/discharge_template.md` - Standard discharge summary template
- `references/medical_terms.json` - Standardized medical terminology
- `references/section_guidelines.md` - Guidelines for each section

## Limitations

- Does not access live EMR systems (requires manual data input)
- Medication interactions not validated
- Does not generate ICD-10 codes automatically
- Requires structured input data
- Output format must align with institutional requirements

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

No additional Python packages required.

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

This skill accepts requests that match the documented purpose of `discharge-summary-writer` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `discharge-summary-writer` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

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
