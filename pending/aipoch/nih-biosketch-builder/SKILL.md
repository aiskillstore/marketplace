---
name: nih-biosketch-builder
description: Generate NIH Biosketch documents compliant with the 2022 OMB-approved.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# NIH Biosketch Builder

**ID**: 101  
**Version**: 1.0.0  
**NIH Format**: 2022 OMB-approved version

## When to Use

- Use this skill when the task is to Generate NIH Biosketch documents compliant with the 2022 OMB-approved.
- Use this skill for academic writing tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## Key Features

- Scope-focused workflow aligned to: Generate NIH Biosketch documents compliant with the 2022 OMB-approved.
- Packaged executable path(s): `scripts/main.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- Python 3.8+
- python-docx
- requests (for PubMed API)

Install dependencies:
```text
pip install python-docx requests
```

## Example Usage

See `## Usage` above for related details.

```bash
cd "20260318/scientific-skills/Academic Writing/nih-biosketch-builder"
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

## Functions

Automatically generate NIH Biosketch documents in the 2022 format for NIH grant applications.

## NIH Biosketch Format Requirements (2022 Version)

### Required Sections
1. **Personal Statement** - Personal statement (max 1 page)
2. **Positions and Honors** - Positions and honors
3. **Contributions to Science** - Scientific contributions (max 4 items)
4. **Research Support** - Research support (optional)

### Format Specifications
- Page count: No more than 5 pages
- Fonts: Arial, Helvetica, Palatino Linotype, or Georgia, ≥11pt
- Margins: ≥0.5 inches
- Line spacing: Single or double

## Usage

### Command Line
```text
python skills/nih-biosketch-builder/scripts/main.py --input data.json --output biosketch.docx
```

### Input Data Format (JSON)
```json
{
  "personal_info": {
    "name": "Zhang San",
    "position": "Associate Professor",
    "department": "Department of Biology",
    "organization": "University of Example",
    "email": "zhang.san@example.edu"
  },
  "personal_statement": "Your personal statement text here...",
  "positions_and_honors": [
    {"year": "2020-present", "position": "Associate Professor", "institution": "University of Example"}
  ],
  "contributions": [
    {
      "title": "Breakthrough in Cancer Research",
      "description": "Detailed description of contribution...",
      "publications": ["PMID:12345678", "DOI:10.1000/example"]
    }
  ],
  "research_support": [
    {"title": "R01 Grant", "agency": "NIH", "period": "2021-2026", "amount": "$1,500,000"}
  ]
}
```

### SCI Paper Auto-import
```text

# Automatically retrieve paper information via PMID
python skills/nih-biosketch-builder/scripts/main.py --import-pubmed "12345678,23456789" --output publications.json

# Auto-fill into biosketch
python skills/nih-biosketch-builder/scripts/main.py --input data.json --auto-import-pubmed --output biosketch.docx
```

## Output Format

Generate DOCX file in NIH official template format, ready to use for grant applications.

## References

- [NIH Biosketch Format Instructions](https://grants.nih.gov/grants/forms/biosketch.htm)
- [SciENcv](https://www.ncbi.nlm.nih.gov/sciencv/) - NIH official tool

## Risk Assessment

| Risk Indicator | Assessment | Level |
|----------------|------------|-------|
| Code Execution | Python scripts with tools | High |
| Network Access | External API calls | High |
| File System Access | Read/write data | Medium |
| Instruction Tampering | Standard prompt guidelines | Low |
| Data Exposure | Data handled securely | Medium |

## Security Checklist

- [ ] No hardcoded credentials or API keys
- [ ] No unauthorized file system access (../)
- [ ] Output does not expose sensitive information
- [ ] Prompt injection protections in place
- [ ] API requests use HTTPS only
- [ ] Input validated against allowed patterns
- [ ] API timeout and retry mechanisms implemented
- [ ] Output directory restricted to workspace
- [ ] Script execution in sandboxed environment
- [ ] Error messages sanitized (no internal paths exposed)
- [ ] Dependencies audited
- [ ] No exposure of internal service architecture

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

This skill accepts requests that match the documented purpose of `nih-biosketch-builder` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `nih-biosketch-builder` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

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
