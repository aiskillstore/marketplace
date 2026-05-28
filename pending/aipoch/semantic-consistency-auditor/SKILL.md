---
name: semantic-consistency-auditor
description: Use semantic consistency auditor for academic writing workflows that need structured execution, explicit assumptions, and clear output boundaries.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Skill: Semantic Consistency Auditor

**ID:** 212  
**Name:** semantic-consistency-auditor  
**Description:** Introduces BERTScore and COMET algorithms to evaluate the semantic consistency between AI-generated clinical notes and expert gold standards from the "semantic entailment" level.

## When to Use

- Use this skill when the task needs Use semantic consistency auditor for academic writing workflows that need structured execution, explicit assumptions, and clear output boundaries.
- Use this skill for academic writing tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## Key Features

- Scope-focused workflow aligned to: Use semantic consistency auditor for academic writing workflows that need structured execution, explicit assumptions, and clear output boundaries.
- Packaged executable path(s): `scripts/main.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

See `## Prerequisites` above for related details.

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `bert_score`: `unspecified`. Declared in `requirements.txt`.
- `comet`: `unspecified`. Declared in `requirements.txt`.
- `dataclasses`: `unspecified`. Declared in `requirements.txt`.
- `numpy`: `unspecified`. Declared in `requirements.txt`.
- `torch`: `unspecified`. Declared in `requirements.txt`.
- `yaml`: `unspecified`. Declared in `requirements.txt`.

## Example Usage

See `## Usage` above for related details.

```bash
cd "20260318/scientific-skills/Academic Writing/semantic-consistency-auditor"
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

Semantic Consistency Auditor is a medical AI evaluation tool used to assess the semantic consistency between AI-generated clinical notes and expert-written gold standards from a semantic level. This tool is not limited to traditional string matching or bag-of-words models, but uses deep learning models to understand semantic entailment relationships, capable of identifying expressions with different wording but similar meaning.

## Algorithms

### 1. BERTScore
BERTScore uses pre-trained BERT model contextual embeddings to calculate similarity between candidate text and reference text:
- **Precision**: How much semantics in the candidate text is covered by the reference text
- **Recall**: How much semantics in the reference text is covered by the candidate text
- **F1 Score**: Harmonic mean of Precision and Recall

### 2. COMET (Cross-lingual Optimized Metric for Evaluation of Translation)
COMET is a neural network-based evaluation metric originally used for machine translation evaluation, applicable to semantic entailment tasks:
- Uses XLM-RoBERTa encoder to capture deep semantics
- Outputs semantic consistency scores between 0-1
- Gives high scores to semantically equivalent but differently expressed text

## Installation

```text

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac

# Or venv\Scripts\activate  # Windows

# Install dependencies
pip install bertscore comet-ml transformers torch
```

## Configuration

Configure in `~/.openclaw/skills/semantic-consistency-auditor/config.yaml`:

```yaml

# BERTScore Configuration
bertscore:
  model: "microsoft/deberta-xlarge-mnli"  # Or "bert-base-chinese" for Chinese
  lang: "zh"  # Language code: zh, en, etc.
  rescale_with_baseline: true
  device: "auto"  # auto, cpu, cuda

# COMET Configuration
comet:
  model: "Unbabel/wmt22-comet-da"  # COMET model
  batch_size: 8
  device: "auto"

# Evaluation Thresholds
thresholds:
  bertscore_f1: 0.85
  comet_score: 0.75
  semantic_consistency: 0.80  # Comprehensive score threshold
```

## Usage

### Command Line

```text

# Evaluate single case pair
python scripts/main.py \
  --ai-generated "Patient presented with fever for 3 days, highest temperature 39°C, accompanied by cough." \
  --gold-standard "Patient chief complaint of fever for 3 days, highest temperature 39°C, accompanied by cough symptoms." \
  --output results.json

# Batch evaluation from JSON file
python scripts/main.py \
  --input-file batch_cases.json \
  --output results.json \
  --format detailed

# Use specific model
python scripts/main.py \
  --ai-generated "..." \
  --gold-standard "..." \
  --bert-model "bert-base-chinese" \
  --comet-model "Unbabel/wmt20-comet-da"
```

### Python API

```python
from semantic_consistency_auditor import SemanticConsistencyAuditor

# Initialize evaluator
auditor = SemanticConsistencyAuditor(
    bert_model="microsoft/deberta-xlarge-mnli",
    comet_model="Unbabel/wmt22-comet-da",
    lang="zh"
)

# Evaluate single case
result = auditor.evaluate(
    ai_text="Patient presented with fever for 3 days...",
    gold_text="Patient chief complaint of fever for 3 days..."
)

print(f"BERTScore F1: {result['bertscore']['f1']:.4f}")
print(f"COMET Score: {result['comet']['score']:.4f}")
print(f"Consistency: {result['consistency']:.4f}")
print(f"Passed: {result['passed']}")

# Batch evaluation
results = auditor.evaluate_batch([
    {"ai": "...", "gold": "..."},
    {"ai": "...", "gold": "..."}
])
```

## Input Format

### Single Case (Command Line)

Pass text directly through `--ai-generated` and `--gold-standard` parameters.

### Batch Evaluation File (JSON)

```json
[
  {
    "case_id": "CASE001",
    "ai_generated": "Patient presented with fever for 3 days, highest temperature 39°C, accompanied by cough.",
    "gold_standard": "Patient chief complaint of fever for 3 days, highest temperature 39°C, accompanied by cough symptoms.",
    "metadata": {
      "department": "Respiratory",
      "disease_type": "Upper respiratory infection"
    }
  },
  {
    "case_id": "CASE002",
    "ai_generated": "...",
    "gold_standard": "..."
  }
]
```

## Output Format

### Summary Mode

```json
{
  "overall": {
    "total_cases": 100,
    "passed_cases": 85,
    "pass_rate": 0.85,
    "avg_bertscore_f1": 0.8923,
    "avg_comet_score": 0.8234,
    "avg_consistency": 0.8579
  },
  "thresholds": {
    "bertscore_f1": 0.85,
    "comet_score": 0.75,
    "semantic_consistency": 0.80
  }
}
```

### Detailed Mode

```json
{
  "cases": [
    {
      "case_id": "CASE001",
      "ai_generated": "Patient presented with fever for 3 days...",
      "gold_standard": "Patient chief complaint of fever for 3 days...",
      "metrics": {
        "bertscore": {
          "precision": 0.9123,
          "recall": 0.8934,
          "f1": 0.9028
        },
        "comet": {
          "score": 0.8234,
          "system_score": 0.8156
        },
        "semantic_consistency": 0.8631
      },
      "passed": true,
      "details": {
        "semantic_gaps": [],
        "matched_concepts": ["fever for 3 days", "temperature 39°C", "cough"]
      }
    }
  ],
  "summary": { ... }
}
```

## Error Handling

- If required inputs are missing, state exactly which fields are missing and request only the minimum additional information.
- If the task goes outside the documented scope, stop instead of guessing or silently widening the assignment.
- If `scripts/main.py` fails, report the failure point, summarize what still can be completed safely, and provide a manual fallback.
- Do not fabricate files, citations, data, search results, or execution outcomes.

## Performance Notes

- **BERTScore**: First run will download model (approximately 400MB-1GB)
- **COMET**: First run will download model (approximately 500MB-1.5GB)
- **GPU Acceleration**: Significantly improves evaluation speed in CUDA environment
- **Batch Processing**: Recommended for batch evaluation to fully utilize GPU parallel capability

## References

1. Zhang et al. "BERTScore: Evaluating Text Generation with BERT" ICLR 2020
2. Rei et al. "COMET: A Neural Framework for MT Evaluation" EMNLP 2020
3. Medical Record Standardization Evaluation Guidelines (National Health Commission)

## Changelog

- **v1.0.0** (2026-02-06): Initial version, supports dual-algorithm evaluation with BERTScore and COMET

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

## Output Requirements

Every final response should make these items explicit when they are relevant:

- Objective or requested deliverable
- Inputs used and assumptions introduced
- Workflow or decision path
- Core result, recommendation, or artifact
- Constraints, risks, caveats, or validation needs
- Unresolved items and next-step checks

## Input Validation

This skill accepts requests that match the documented purpose of `semantic-consistency-auditor` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `semantic-consistency-auditor` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

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
