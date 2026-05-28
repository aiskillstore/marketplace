---
name: unstructured-medical-text-miner
description: Mine unstructured clinical text from MIMIC-IV to extract diagnostic logic.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Unstructured Medical Text Miner (ID: 213)

## When to Use

- Use this skill when the task needs Mine unstructured clinical text from MIMIC-IV to extract diagnostic logic.
- Use this skill for evidence insight tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## Key Features

See `## Features` above for related details.

- Scope-focused workflow aligned to: Mine unstructured clinical text from MIMIC-IV to extract diagnostic logic.
- Packaged executable path(s): `scripts/__init__.py` plus 1 additional script(s).
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

```
pandas>=1.3.0
spacy>=3.4.0
scispacy>=0.5.1
radlex (for radiology terminology)
negspacy (for negation detection)
```

## Example Usage

See `## Usage` above for related details.

```bash
cd "20260318/scientific-skills/Evidence Insight/unstructured-medical-text-miner"
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
- Primary implementation surface: `scripts/__init__.py` with additional helper scripts under `scripts/`.
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

Mine "text data" that has been long overlooked in MIMIC-IV, extracting unstructured diagnostic logic, order details, and progress notes.

## Purpose

The MIMIC-IV database contains large amounts of structured data (vital signs, laboratory results, etc.), but its true clinical value is often hidden in unstructured text:
- Diagnostic reasoning chains in discharge summaries
- Subtle finding descriptions in imaging reports
- Treatment decision logic in progress notes
- Personalized medication considerations in orders

This Skill provides a complete text mining toolchain to transform raw medical text into analyzable structured insights.

## Features

### 1. Text Extraction
- **NOTEEVENTS**: Extract clinical notes from MIMIC-IV NOTE module
- **Radiology Reports**: Extract imaging diagnostic text
- **ECG Reports**: Parse ECG interpretation text
- **Discharge Summaries**: Extract complete diagnostic and treatment course

### 2. Information Extraction
- **Entity Recognition**: Diseases, symptoms, medications, procedures, anatomical sites
- **Relation Extraction**: Medication-disease treatment relationships, symptom-disease diagnostic relationships
- **Timeline Extraction**: Event occurrence times, disease progression sequence
- **Negation Detection**: Identify negated clinical findings (e.g., "no fever")

### 3. Clinical Logic Parsing
- **Diagnostic Reasoning Chain**: Reasoning path from symptoms → examination → diagnosis
- **Treatment Decision Tree**: Clinical basis for medication selection and dosage adjustment
- **Disease Progression**: Disease progression and outcome descriptions

### 4. Structured Output
- FHIR-compatible clinical document format
- Knowledge graph-friendly triple format
- Temporal event sequences

## Usage

```python
from skills.unstructured_medical_text_miner.scripts.main import MedicalTextMiner

# Initialize miner
miner = MedicalTextMiner()

# Load MIMIC-IV note data
miner.load_notes(notes_path="path/to/noteevents.csv")

# Extract all text records for a specific patient
patient_texts = miner.get_patient_texts(subject_id=10000032)

# Execute complete information extraction
insights = miner.extract_insights(
    text=patient_texts,
    extract_entities=True,
    extract_relations=True,
    extract_timeline=True
)
```

## Input

### Data Sources
- MIMIC-IV NOTEEVENTS table (csv/parquet format)
- Discharge summary files
- Imaging report files
- Custom medical text

### Field Requirements
| Field Name | Description | Required |
|--------|------|------|
| subject_id | Patient unique identifier | Yes |
| hadm_id | Hospital admission record identifier | No |
| note_type | Note type (DS/RR/ECG, etc.) | Yes |
| note_text | Note text content | Yes |
| charttime | Record time | No |

## Output

### Entity Extraction Results
```json
{
  "entities": [
    {
      "text": "acute myocardial infarction",
      "type": "DISEASE",
      "start": 156,
      "end": 183,
      "confidence": 0.94
    },
    {
      "text": "aspirin 81mg",
      "type": "MEDICATION",
      "start": 245,
      "end": 257,
      "attributes": {
        "dose": "81mg",
        "frequency": "daily"
      }
    }
  ]
}
```

### Clinical Logic Graph
```json
{
  "clinical_logic": {
    "presenting_complaint": "chest pain",
    "differential_diagnoses": ["ACS", "PE", "aortic dissection"],
    "workup": ["ECG", "troponin", "CTA chest"],
    "final_diagnosis": "STEMI",
    "treatment_plan": ["PCI", "dual antiplatelet"]
  }
}
```

### Temporal Events
```json
{
  "timeline": [
    {
      "time": "2020-03-15 08:30",
      "event": "admission",
      "description": "presented with chest pain"
    },
    {
      "time": "2020-03-15 09:15",
      "event": "ECG",
      "description": "ST elevation in V1-V4"
    }
  ]
}
```

## Configuration

```yaml

# config.yaml
extraction:
  entity_types: ["DISEASE", "SYMPTOM", "MEDICATION", "PROCEDURE", "ANATOMY"]
  relation_types: ["TREATS", "CAUSES", "CONTRAINDICATED_WITH"]
  enable_negation_detection: true
  
models:
  ner_model: "en_core_sci_lg"  # or "en_core_sci_scibert"
  relation_model: "custom_relation_extractor"
  
output:
  format: "json"  # json/fhir/kg
  include_raw_text: false
```

## CLI Usage

```text

# Process single file
python -m skills.unstructured_medical_text_miner.scripts.main \
  --input notes.csv \
  --output extracted.json \
  --extract all

# Process specific patient
python -m skills.unstructured_medical_text_miner.scripts.main \
  --subject-id 10000032 \
  --db-path mimic_iv.db \
  --output patient_insights.json
```

## References

1. MIMIC-IV Clinical Database: https://physionet.org/content/mimiciv/
2. scispacy: https://allenai.github.io/scispacy/
3. NegEx/negspacy for negation detection
4. FHIR Clinical Document specifications

## Author

Skill ID: 213
Category: Medical Data Mining
Complexity: Advanced

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

This skill accepts requests that match the documented purpose of `unstructured-medical-text-miner` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `unstructured-medical-text-miner` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

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
