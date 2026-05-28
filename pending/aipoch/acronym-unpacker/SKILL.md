---
name: acronym-unpacker
description: Intelligent medical abbreviation disambiguation tool that resolves ambiguous acronyms using clinical context, specialty-specific knowledge, and document-level semantic analysis.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Acronym Unpacker

Intelligent medical abbreviation disambiguation tool that resolves ambiguous acronyms using clinical context, specialty-specific knowledge, and document-level semantic analysis.

## When to Use

- Use this skill when the task needs Intelligent medical abbreviation disambiguation tool that resolves ambiguous acronyms using clinical context, specialty-specific knowledge, and document-level semantic analysis.
- Use this skill for evidence insight tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## Key Features

See `## Features` above for related details.

- Scope-focused workflow aligned to: Intelligent medical abbreviation disambiguation tool that resolves ambiguous acronyms using clinical context, specialty-specific knowledge, and document-level semantic analysis.
- Packaged executable path(s): `scripts/main.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

```text
pip install -r requirements.txt
```

No external dependencies required.

## Example Usage

See `## Usage` above for related details.

```bash
cd "20260318/scientific-skills/Evidence Insight/acronym-unpacker"
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

- **Context-Aware Disambiguation**: Uses clinical specialty to rank expansions
- **Semantic Analysis**: Analyzes surrounding text for contextual clues
- **Frequency-Based Ranking**: Prioritizes common usage patterns
- **Multi-Specialty Support**: Covers medicine, nursing, pharmacy, and research
- **Batch Processing**: Expand acronyms in entire documents
- **Learning System**: Improves accuracy with usage feedback

## Usage

### Basic Usage

```text

# Expand single acronym
python scripts/main.py PID

# Expand with context
python scripts/main.py MI --context cardiology

# List known acronyms
python scripts/main.py --list
```

### Parameters

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `acronym` | str | None | Yes | Acronym to expand |
| `--context`, `-c` | str | general | No | Clinical context (e.g., cardiology, gynecology) |
| `--list`, `-l` | flag | False | No | List known acronyms |

### Advanced Usage

```text

# Disambiguate with specific context
python scripts/main.py PID --context gynecology

# Check all available acronyms
python scripts/main.py --list
```

## Supported Acronyms

| Acronym | General | Cardiology | Gynecology | Immunology |
|---------|---------|------------|------------|------------|
| **PID** | Pelvic Inflammatory Disease | - | Pelvic Inflammatory Disease (90%) | Primary Immunodeficiency (95%) |
| **MI** | Myocardial Infarction (70%) | Myocardial Infarction (95%) | - | - |
| **COPD** | Chronic Obstructive Pulmonary Disease | - | - | - |
| **HTN** | Hypertension | Hypertension | - | - |
| **DM** | Diabetes Mellitus (90%) | - | - | - |

## Output Example

```
============================================================
ACRONYM: PID
Context: gynecology
============================================================
1. Pelvic Inflammatory Disease
   Confidence: 90.0% ████████████████████
2. Prolapsed Intervertebral Disc
   Confidence: 10.0% ██
============================================================
```

## Technical Difficulty: **LOW**

⚠️ **AI independent acceptance status**: manual inspection required
This skill requires:
- Python 3.7+ environment
- No external dependencies

## Risk Assessment

| Risk Indicator | Assessment | Level |
|----------------|------------|-------|
| Code Execution | Python scripts executed locally | Low |
| Network Access | No network access | Low |
| File System Access | Read-only | Low |
| Instruction Tampering | Standard prompt guidelines | Low |
| Data Exposure | No sensitive data exposure | Low |

## Security Checklist

- [x] No hardcoded credentials or API keys
- [x] No unauthorized file system access
- [x] Output does not expose sensitive information
- [x] Prompt injection protections in place
- [x] Error messages sanitized
- [x] Dependencies audited

## Prerequisites

```text
python scripts/main.py --help
```

## Evaluation Criteria

### Success Metrics
- [ ] Successfully expands known acronyms
- [ ] Context-aware ranking works correctly
- [ ] Confidence scores are meaningful
- [ ] Handles unknown acronyms gracefully

### Test Cases
1. **Basic Expansion**: Known acronym → Multiple expansions with confidence
2. **Context Filtering**: Context flag → Contextually appropriate results
3. **Unknown Acronym**: Unknown input → Graceful handling
4. **List Mode**: --list flag → Shows all known acronyms

## Lifecycle Status

- **Current Stage**: Draft
- **Next Review Date**: 2026-03-15
- **Known Issues**: Limited acronym database
- **Planned Improvements**: 
  - Expand acronym database
  - Add machine learning for context detection
  - Support for multi-language acronyms

## References

Available in `references/`:
- Medical abbreviation standards
- Clinical terminology sources
- Context disambiguation methods

## Limitations

- **Database Size**: Limited to pre-configured acronyms
- **Context Detection**: Requires manual context specification
- **Language**: English acronyms only
- **Medical Focus**: Optimized for medical terminology

---

**💡 Tip: When in doubt about the context, try multiple contexts to see which expansion makes the most sense in your specific use case.**

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

This skill accepts requests that match the documented purpose of `acronym-unpacker` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `acronym-unpacker` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

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
