---
name: medical-device-mdr-auditor
description: Audit medical device technical files against EU MDR 2017/745 regulations.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Medical Device MDR Auditor

**ID**: 130  
**Version**: 1.0.0  
**Description**: Check whether medical device technical files contain required documents according to EU MDR (2017/745) regulations

---

## When to Use

- Use this skill when the task needs Audit medical device technical files against EU MDR 2017/745 regulations.
- Use this skill for academic writing tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## Key Features

- Scope-focused workflow aligned to: Audit medical device technical files against EU MDR 2017/745 regulations.
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
cd "20260318/scientific-skills/Academic Writing/medical-device-mdr-auditor"
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
```

## Workflow

1. Confirm the user objective, required inputs, and non-negotiable constraints before doing detailed work.
2. Validate that the request matches the documented scope and stop early if the task would require unsupported assumptions.
3. Use the packaged script path or the documented reasoning path with only the inputs that are actually available.
4. Return a structured result that separates assumptions, deliverables, risks, and unresolved items.
5. If execution fails or inputs are incomplete, switch to the fallback path and state exactly what blocked full completion.

## Overview

This Skill is used to audit the compliance of medical device technical files, checking whether documents contain necessary Clinical Evaluation Reports and Post-Market Surveillance plans according to EU MDR 2017/745 regulatory requirements.

## Usage

```text

# Check single technical file directory
python3 /Users/z04030865/.openclaw/workspace/skills/medical-device-mdr-auditor/scripts/main.py --input /path/to/technical/file --class IIa

# Batch check using JSON configuration file
python3 /Users/z04030865/.openclaw/workspace/skills/medical-device-mdr-auditor/scripts/main.py --config /path/to/config.json

# Output detailed report
python3 /Users/z04030865/.openclaw/workspace/skills/medical-device-mdr-auditor/scripts/main.py --input /path/to/technical/file --class III --verbose --output report.json
```

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--input` | string | Conditional | Technical file directory path |
| `--config` | string | Conditional | JSON configuration file path |
| `--class` | string | Yes | Device classification (I, IIa, IIb, III) |
| `--output` | string | No | Output report path |
| `--verbose` | flag | No | Output detailed information |

## MDR 2017/745 Check Points

### 1. Clinical Evaluation Report (CER)

According to MDR Annex XIV Part A, must include:
- [ ] Clinical Evaluation Plan
- [ ] Clinical Data Assessment (Literature review / Clinical investigation data)
- [ ] Clinical Evidence Analysis
- [ ] Benefit-risk Conclusion

### 2. Post-Market Surveillance Plan (PMS)

According to MDR Article 83 & Annex III, must include:
- [ ] PMS procedure description
- [ ] Data collection methods
- [ ] Risk assessment update mechanism
- [ ] Trend reporting mechanism

### 3. Post-Market Clinical Follow-up Plan (PMCF Plan)

According to MDR Annex XIV Part B, for Class IIa and above devices:
- [ ] PMCF plan document
- [ ] Clinical data continuous collection methods
- [ ] Safety and performance monitoring procedures

### 4. Other Key Documents

- [ ] Risk Management File (ISO 14971)
- [ ] Usability Engineering File
- [ ] Biological Evaluation Report
- [ ] Labeling & Instructions for Use

## Output Format

### Compliance Report Example

```json
{
  "audit_date": "2026-02-06T06:00:00Z",
  "device_class": "IIa",
  "compliance_status": "PARTIAL",
  "findings": [
    {
      "category": "CRITICAL",
      "regulation": "MDR Annex XIV Part A",
      "item": "Clinical Evaluation Report",
      "status": "MISSING",
      "description": "Clinical evaluation report file not found"
    },
    {
      "category": "MAJOR",
      "regulation": "MDR Article 83",
      "item": "PMS Plan",
      "status": "INCOMPLETE",
      "description": "PMS plan lacks trend reporting mechanism"
    }
  ],
  "summary": {
    "total_checks": 12,
    "passed": 8,
    "warnings": 2,
    "failed": 2
  }
}
```

## Compliance Levels

| Level | Description |
|-------|-------------|
| `COMPLIANT` | Fully compliant with MDR requirements |
| `PARTIAL` | Partially compliant, with correctable deficiencies |
| `NON_COMPLIANT` | Seriously non-compliant, critical documents missing |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Audit passed, fully compliant |
| 1 | Audit passed, with warnings |
| 2 | Audit failed, with deficiencies |
| 3 | Execution error |

## References

- Regulation (EU) 2017/745 (MDR)
- MDCG Guidance Documents
- EN ISO 14971:2019
- EN ISO 13485:2016

## Author

OpenClaw Skill Development Team

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

This skill accepts requests that match the documented purpose of `medical-device-mdr-auditor` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `medical-device-mdr-auditor` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

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
