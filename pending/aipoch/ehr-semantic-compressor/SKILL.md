---
name: ehr-semantic-compressor
description: 1. Confirm the user objective, required inputs, and non-negotiable constraints before doing detailed work. 2. Validate that the request matches the documented scope and stop early if the task would require unsupported as.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# EHR Semantic Compressor

## When to Use

- Use this skill when the task needs 1. Confirm the user objective, required inputs, and non-negotiable constraints before doing detailed work. 2. Validate that the request matches the documented scope and stop early if the task would require unsupported as.
- Use this skill for academic writing tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## Key Features

- Scope-focused workflow aligned to: 1. Confirm the user objective, required inputs, and non-negotiable constraints before doing detailed work. 2. Validate that the request matches the documented scope and stop early if the task would require unsupported as.
- Packaged executable path(s): `scripts/main.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

See `references/requirements.txt` for complete list.

Key dependencies:
- transformers >= 4.30.0
- torch >= 2.0.0
- spacy >= 3.6.0
- scispacy >= 0.5.3

## Example Usage

See `## Usage` above for related details.

```bash
cd "20260318/scientific-skills/Academic Writing/ehr-semantic-compressor"
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
python scripts/main.py --input "Audit validation sample with explicit symptoms, history, assessment, and next-step plan."
```

## Workflow

1. Confirm the user objective, required inputs, and non-negotiable constraints before doing detailed work.
2. Validate that the request matches the documented scope and stop early if the task would require unsupported assumptions.
3. Use the packaged script path or the documented reasoning path with only the inputs that are actually available.
4. Return a structured result that separates assumptions, deliverables, risks, and unresolved items.
5. If execution fails or inputs are incomplete, switch to the fallback path and state exactly what blocked full completion.

## Overview

AI-powered EHR summarization using Transformer architecture to extract key clinical information from lengthy medical records. This skill processes lengthy Electronic Health Record (EHR) documents and generates structured, clinically accurate summaries.

**Technical Difficulty**: High

## Core Features

1. **Fast Processing**: Process lengthy EHR documents (1600+ words) in 10-20 seconds
2. **Structured Summaries**: Generate bullet-point summaries (200-300 words)
3. **Critical Information Extraction**:
   - Patient allergies and adverse reactions
   - Family medical history
   - Current and past medications
   - Diagnoses and conditions
   - Vital signs and lab results
   - Procedures and surgeries
4. **Clinical Accuracy**: Maintains completeness of medical information

## Usage

### Basic Usage

```text
python scripts/main.py --input ehr_document.txt --output summary.json
```

### Input Format

```json
{
  "ehr_text": "Full EHR document text...",
  "max_length": 300,
  "extract_sections": ["allergies", "medications", "diagnoses", "family_history"]
}
```

### Output Format

```json
{
  "status": "success",
  "data": {
    "summary": "Structured bullet-point summary...",
    "extracted_sections": {
      "allergies": [...],
      "medications": [...],
      "diagnoses": [...],
      "family_history": [...]
    },
    "metadata": {
      "original_length": 2500,
      "summary_length": 280,
      "compression_ratio": 0.89
    }
  }
}
```

## Parameters

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `--input`, `-i` | string | - | Yes | Input EHR document text file path |
| `--output`, `-o` | string | - | No | Output JSON file path |
| `--max-length` | int | 300 | No | Maximum summary length in words |
| `--extract-sections` | string | all | No | Comma-separated sections to extract |
| `--format` | string | json | No | Output format (json, markdown, text) |

## Technical Details

### Architecture

- **Base Model**: Transformer-based encoder-decoder architecture
- **Medical Domain Adaptation**: Fine-tuned on clinical text corpora
- **Section Extraction**: Rule-based + ML hybrid approach for structured data
- **Processing Pipeline**: Text segmentation -> Summarization -> Section extraction -> Output formatting

### Performance

- **Processing Time**: 10-20 seconds for 1600+ word documents
- **Memory**: Requires ~2GB RAM
- **Output Length**: 200-300 words (configurable)
- **Compression Ratio**: ~85-90%

## References

- `references/requirements.txt` - Python dependencies
- `references/guidelines.md` - Clinical summarization guidelines
- `references/sample_input.json` - Example input format
- `references/sample_output.json` - Example output format

## Safety & Compliance

- No external API calls or service dependencies
- All processing performed locally
- No patient data transmitted outside the system
- Error messages are semantic and do not expose technical details

## Testing

Run unit tests:
```text
cd scripts
python test_main.py
```

## Error Handling

- If required inputs are missing, state exactly which fields are missing and request only the minimum additional information.
- If the task goes outside the documented scope, stop instead of guessing or silently widening the assignment.
- If `scripts/main.py` fails, report the failure point, summarize what still can be completed safely, and provide a manual fallback.
- Do not fabricate files, citations, data, search results, or execution outcomes.

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

## Input Validation

This skill accepts requests that match the documented purpose of `ehr-semantic-compressor` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `ehr-semantic-compressor` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

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
