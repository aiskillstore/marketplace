---
name: hipaa-compliance-auditor
description: A clinical-grade PII/PHI detection and de-identification tool for healthcare text data.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# HIPAA Compliance Auditor

A clinical-grade PII/PHI detection and de-identification tool for healthcare text data.

## When to Use

- Use this skill when the task needs A clinical-grade PII/PHI detection and de-identification tool for healthcare text data.
- Use this skill for academic writing tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## Key Features

See `## Features` above for related details.

- Scope-focused workflow aligned to: A clinical-grade PII/PHI detection and de-identification tool for healthcare text data.
- Packaged executable path(s): `scripts/main.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- Python 3.9+
- spaCy (en_core_web_trf or en_core_web_lg)
- regex (for advanced pattern matching)
- Presidio (optional, for enhanced PII detection)

See `references/requirements.txt` for full dependency list.

## Example Usage

See `## Usage` above for related details.

```bash
cd "20260318/scientific-skills/Academic Writing/hipaa-compliance-auditor"
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
python scripts/main.py --text "Audit validation sample with explicit methods, findings, and conclusion."
```

## Workflow

1. Confirm the user objective, required inputs, and non-negotiable constraints before doing detailed work.
2. Validate that the request matches the documented scope and stop early if the task would require unsupported assumptions.
3. Use the packaged script path or the documented reasoning path with only the inputs that are actually available.
4. Return a structured result that separates assumptions, deliverables, risks, and unresolved items.
5. If execution fails or inputs are incomplete, switch to the fallback path and state exactly what blocked full completion.

## Overview

This skill analyzes text for HIPAA-protected identifiers and automatically redacts or anonymizes them. It uses a combination of regex patterns, NLP entity recognition, and contextual analysis to identify 18 HIPAA identifier categories.

## Features

- **18 HIPAA Identifiers Detection**: Names, dates, SSN, MRN, phone/fax, email, geographic data, etc.
- **Automatic De-identification**: Replace PII with semantic tokens (e.g., `[PATIENT_NAME]`, `[DATE_1]`)
- **Context-Aware Detection**: Distinguishes between similar patterns (dates vs. lab values)
- **Audit Logging**: Track all redaction actions for compliance documentation
- **Confidence Scoring**: Flag uncertain detections for manual review

## Usage

### Command Line
```text
python scripts/main.py --input "patient_text.txt" --output "deidentified.txt"
python scripts/main.py --text "Patient John Doe, SSN 123-45-6789..." --audit-log audit.json
```

### Python API
```python
from scripts.main import HIPAAAuditor

auditor = HIPAAAuditor()
result = auditor.deidentify("Patient John Doe was admitted on 2024-01-15...")
print(result.cleaned_text)  # De-identified output
print(result.detected_pii)  # List of found PII entities
```

## Parameters

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `--input`, `-i` | string | - | No | Path to input text file |
| `--text` | string | - | No | Direct text input (alternative to file) |
| `--output`, `-o` | string | - | No | Path for de-identified output file |
| `--audit-log` | string | - | No | Path for JSON audit log |
| `--confidence` | float | 0.7 | No | Minimum confidence threshold (0.0-1.0) |
| `--preserve-structure` | bool | true | No | Maintain document structure |
| `--custom-patterns` | string | - | No | Path to custom regex patterns JSON |

## HIPAA Identifier Categories Detected

1. Names (patient, relatives, employers)
2. Geographic subdivisions smaller than state
3. Dates (except year) related to individual
4. Phone numbers
5. Fax numbers
6. Email addresses
7. SSN
8. Medical record numbers
9. Health plan beneficiary numbers
10. Account numbers
11. Certificate/license numbers
12. Vehicle identifiers
13. Device identifiers
14. URLs
15. IP addresses
16. Biometric identifiers
17. Full-face photos
18. Any other unique identifying numbers

## Output Format

### De-identified Text
Original identifiers replaced with semantic tags:
- `[PATIENT_NAME_1]`, `[PATIENT_NAME_2]` ...
- `[DATE_1]`, `[DATE_2]` ...
- `[SSN_1]`
- `[PHONE_1]`, `[PHONE_2]` ...
- `[EMAIL_1]`
- `[MRN_1]` (Medical Record Number)
- `[ADDRESS_1]`

### Audit Log JSON
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "input_hash": "sha256:abc123...",
  "detections": [
    {
      "type": "PATIENT_NAME",
      "position": [10, 18],
      "confidence": 0.95,
      "replacement": "[PATIENT_NAME_1]",
      "original_length": 8
    }
  ],
  "statistics": {
    "total_pii_found": 5,
    "categories_detected": ["NAME", "DATE", "PHONE", "SSN"]
  }
}
```

## Technical Architecture

1. **Preprocessing**: Normalize text encoding, handle line breaks
2. **Regex Engine**: Pattern matching for structured identifiers (SSN, phone, email, MRN)
3. **NLP Pipeline**: spaCy NER for names, organizations, locations
4. **Context Filter**: Remove false positives (e.g., "Dr. Smith" vs. "smith fracture")
5. **Replacement Engine**: Sequential replacement with semantic tokens
6. **Validation**: Ensure no original PII remains in output

## Limitations & Warnings

⚠️ **CRITICAL**: This tool is designed as a helper, not a replacement for human review.

- Context-dependent PII (e.g., rare disease names + location) may not be fully detected
- Unstructured narrative text may contain identifying information not caught by patterns
- Always perform manual QA on output before HIPAA-compliant release
- **AI Autonomous Acceptance Status**: Requires Manual Review (Requires Manual Review)

## References

- `references/hipaa_safe_harbor_guide.pdf` - HIPAA Safe Harbor de-identification standards
- `references/pii_patterns.json` - Complete regex pattern definitions
- `references/test_cases/` - Sample clinical texts with expected outputs
- `references/requirements.txt` - Python dependencies

## Technical Difficulty: High

Complex NLP pipelines, contextual disambiguation, regulatory compliance requirements.

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

This skill accepts requests that match the documented purpose of `hipaa-compliance-auditor` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `hipaa-compliance-auditor` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

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
