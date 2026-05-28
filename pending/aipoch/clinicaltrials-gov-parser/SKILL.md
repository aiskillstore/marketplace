---
name: clinicaltrials-gov-parser
description: Monitor and summarize competitor clinical trial status changes from ClinicalTrials.gov.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# ClinicalTrials.gov Parser

Monitor and summarize competitor clinical trial status changes from ClinicalTrials.gov.

## When to Use

- Use this skill when the task needs Monitor and summarize competitor clinical trial status changes from ClinicalTrials.gov.
- Use this skill for evidence insight tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## Key Features

- Scope-focused workflow aligned to: Monitor and summarize competitor clinical trial status changes from ClinicalTrials.gov.
- Packaged executable path(s): `scripts/main.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

See `## Prerequisites` above for related details.

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `dataclasses`: `unspecified`. Declared in `requirements.txt`.
- `requests`: `unspecified`. Declared in `requirements.txt`.

## Example Usage

See `## Usage` above for related details.

```bash
cd "20260318/scientific-skills/Evidence Insight/clinicaltrials-gov-parser"
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

## Use Cases

- **Trial Monitoring**: Track status changes of specific clinical trials
- **Competitive Intelligence**: Monitor competitor trial activities and milestones
- **Recruitment Tracking**: Get updates on enrollment status
- **Completion Alerts**: Monitor trial completion and results posting

## Parameters

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `--sponsor` | string | - | No | Trial sponsor name |
| `--condition` | string | - | No | Medical condition/disease |
| `--status` | string | - | No | Trial status (Recruiting, Completed, etc.) |
| `--trials` | string | - | No | Comma-separated trial IDs (NCT numbers) |
| `--output` | string | json | No | Output format (json, csv) |
| `--days` | int | 30 | No | Number of days for monitoring |

## Usage

```python
from scripts.main import ClinicalTrialsMonitor

# Initialize monitor
monitor = ClinicalTrialsMonitor()

# Search for trials
trials = monitor.search_trials(
    sponsor="Pfizer",
    condition="Diabetes",
    status="Recruiting"
)

# Get trial details
trial = monitor.get_trial("NCT05108922")

# Check for status changes
changes = monitor.check_status_changes(trial_ids=["NCT05108922"])
```

## CLI Usage

```text

# Search trials
python scripts/main.py search --sponsor "Pfizer" --condition "Diabetes"

# Get trial details
python scripts/main.py get NCT05108922

# Monitor status changes
python scripts/main.py monitor --trials NCT05108922,NCT05108923 --output json

# Generate summary report
python scripts/main.py report --sponsor "Pfizer" --days 30
```

## API Methods

| Method | Description |
|--------|-------------|
| `search_trials()` | Search trials with filters |
| `get_trial(nct_id)` | Get detailed trial information |
| `check_status_changes()` | Check for status updates |
| `get_recruitment_status()` | Get enrollment updates |
| `generate_summary()` | Generate competitor summary |

## Technical Details

- **API**: ClinicalTrials.gov API v2
- **Rate Limit**: 10 requests/second
- **Data Format**: JSON
- **Difficulty**: Medium

## References

- See `references/api-docs.md` for API documentation
- See `references/status-codes.md` for trial status definitions
- See `references/examples.md` for usage examples

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

This skill accepts requests that match the documented purpose of `clinicaltrials-gov-parser` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `clinicaltrials-gov-parser` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

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
