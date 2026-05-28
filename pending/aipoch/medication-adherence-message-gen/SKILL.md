---
name: medication-adherence-message-gen
description: Use medication adherence message gen for academic writing workflows that need structured execution, explicit assumptions, and clear output boundaries.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Skill: Medication Adherence Message Gen

**ID:** 136  
**Name:** medication-adherence-message-gen  
**Description:** Uses behavioral psychology principles to generate SMS/push notification copy for reminding patients to take medication.  
**Version:** 1.0.0  

---

## When to Use

- Use this skill when the task needs Use medication adherence message gen for academic writing workflows that need structured execution, explicit assumptions, and clear output boundaries.
- Use this skill for academic writing tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## Key Features

- Scope-focused workflow aligned to: Use medication adherence message gen for academic writing workflows that need structured execution, explicit assumptions, and clear output boundaries.
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
cd "20260318/scientific-skills/Academic Writing/medication-adherence-message-gen"
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

## Overview

This skill generates personalized medication reminder messages based on behavioral psychology and behavioral economics principles. By applying psychological mechanisms such as social norms, loss aversion, implementation intentions, commitment consistency, etc., it improves patient medication adherence.

## Psychological Principles Used

| Principle | English | Description |
|------|------|------|
| Social Norms | Social Norms | Emphasizes "most patients can adhere to medication" |
| Loss Aversion | Loss Aversion | Emphasizes what will be lost if medication is not taken on time |
| Implementation Intentions | Implementation Intentions | "If-then" plans |
| Immediate Rewards | Immediate Rewards | Immediate positive feedback after taking medication |
| Commitment Consistency | Commitment | Reinforces patient commitment and responsibility |
| Self-Efficacy | Self-Efficacy | Enhances patient confidence in self-management |
| Anchoring Effect | Anchoring | Provides specific quantifiable goals |
| Scarcity | Scarcity | Emphasizes timeliness of treatment |

## Usage

### Command Line

```text
python scripts/main.py [options]
```

### Options

| Parameter | Short | Type | Required | Description |
|------|------|------|------|------|
| `--name` | `-n` | str | No | Patient name |
| `--medication` | `-m` | str | Yes | Medication name |
| `--dosage` | `-d` | str | No | Dosage information |
| `--time` | `-t` | str | No | Medication time |
| `--principle` | `-p` | str | No | Psychology principle (social_norms/loss_aversion/implementation/intent/reward/commitment/self_efficacy/anchoring/scarcity/random) |
| `--tone` |  | str | No | Tone style (gentle/firm/encouraging/urgent) |
| `--language` | `-l` | str | No | Language (zh/en) |
| `--output` | `-o` | str | No | Output format (text/json) |

### Examples

```text

# Basic usage
python scripts/main.py -m "Atorvastatin" -n "Mr. Zhang"

# Specify psychology principle
python scripts/main.py -m "Metformin" -p "loss_aversion" -t "After breakfast"

# Generate JSON format
python scripts/main.py -m "Antihypertensive" -p "social_norms" -o json

# English output
python scripts/main.py -m "Metformin" -n "John" -l en -p "commitment"
```

### Python API

```python
from scripts.main import generate_message

message = generate_message(
    medication="Atorvastatin",
    patient_name="Mr. Zhang",
    dosage="20mg",
    time="After dinner",
    principle="social_norms",
    tone="encouraging"
)
print(message)
```

## Output Format

### Text Mode
```
【Medication Reminder】Mr. Zhang, it's time after dinner. 95% of patients taking Atorvastatin can adhere to daily medication, and you're one of them! Please take 20mg to keep your heart healthy.
```

### JSON Mode
```json
{
  "medication": "Atorvastatin",
  "patient_name": "Mr. Zhang",
  "principle": "social_norms",
  "tone": "encouraging",
  "message": "【Medication Reminder】Mr. Zhang, it's time after dinner...",
  "psychology_insight": "Uses social norms principle to enhance patient behavioral motivation by emphasizing high adherence rates"
}
```

## Message Templates

Each psychology principle has multiple copy templates, randomly selected to avoid repetition fatigue.

---

**Author:** OpenClaw  
**License:** MIT

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

This skill accepts requests that match the documented purpose of `medication-adherence-message-gen` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `medication-adherence-message-gen` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

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
