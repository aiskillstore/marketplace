---
name: automated-soap-note-generator
description: 1. Confirm the user objective, required inputs, and non-negotiable constraints before doing detailed work. 2. Validate that the request matches the documented scope and stop early if the task would require unsupported as.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Automated SOAP Note Generator

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

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `dataclasses`: `unspecified`. Declared in `requirements.txt`.
- `enum`: `unspecified`. Declared in `requirements.txt`.

## Example Usage

See `## Usage` above for related details.

```bash
cd "20260318/scientific-skills/Academic Writing/automated-soap-note-generator"
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
python scripts/main.py --input "Audit validation sample with explicit symptoms, history, assessment, and next-step plan." --patient-id P12345 --provider "Dr. Smith" --format json
```

## Workflow

1. Confirm the user objective, required inputs, and non-negotiable constraints before doing detailed work.
2. Validate that the request matches the documented scope and stop early if the task would require unsupported assumptions.
3. Use the packaged script path or the documented reasoning path with only the inputs that are actually available.
4. Return a structured result that separates assumptions, deliverables, risks, and unresolved items.
5. If execution fails or inputs are incomplete, switch to the fallback path and state exactly what blocked full completion.

## Overview

AI-powered clinical documentation tool that converts unstructured clinical input into professionally formatted SOAP notes compliant with medical documentation standards.

**Key Capabilities:**
- **Intelligent Parsing**: Extracts structured information from free-text clinical narratives
- **SOAP Classification**: Automatically categorizes content into Subjective, Objective, Assessment, Plan sections
- **Medical Entity Recognition**: Identifies symptoms, diagnoses, medications, procedures, and anatomical locations
- **Temporal Analysis**: Extracts timeline information (onset, duration, progression)
- **Template Generation**: Produces standardized SOAP format suitable for EHR integration
- **Multi-modal Input**: Accepts text dictation, transcripts, or clinical notes

## Core Capabilities

### 1. Input Processing and Preprocessing

Handle various input formats and prepare for NLP analysis:

```python
from scripts.soap_generator import SOAPNoteGenerator

generator = SOAPNoteGenerator()

# Process text input
soap_note = generator.generate(
    input_text="Patient presents with 2-day history of chest pain, radiating to left arm...",
    patient_id="P12345",
    encounter_date="2026-01-15",
    provider="Dr. Smith"
)

# Process from audio transcript
soap_note = generator.generate_from_transcript(
    transcript_path="consultation_transcript.txt",
    patient_id="P12345"
)
```

**Input Preprocessing Steps:**
1. **Text Cleaning**: Remove filler words ("um", "uh"), timestamps, speaker labels
2. **Sentence Segmentation**: Split into clinically meaningful segments
3. **Normalization**: Standardize abbreviations and medical shorthand
4. **Encoding Detection**: Handle various file formats (UTF-8, ASCII, etc.)

**Parameters:**
| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| `input_text` | str | Yes* | Raw clinical text or dictation | None |
| `transcript_path` | str | Yes* | Path to transcript file | None |
| `patient_id` | str | No | Patient identifier (MUST be de-identified for testing) | None |
| `encounter_date` | str | No | Date in ISO 8601 format (YYYY-MM-DD) | Current date |
| `provider` | str | No | Healthcare provider name | None |
| `specialty` | str | No | Medical specialty context | "general" |
| `verbose` | bool | No | Include confidence scores | False |

*Either `input_text` or `transcript_path` required

**Best Practices:**
- Always verify input text quality (clear audio → better transcription → better SOAP)
- Remove patient identifiers before processing unless in secure environment
- Split long encounters (>30 minutes) into logical segments
- Flag ambiguous abbreviations for manual review

### 2. Medical Named Entity Recognition (NER)

Identify and extract medical concepts from unstructured text:

```python

# Extract entities with context
entities = generator.extract_medical_entities(
    "Patient has history of hypertension and diabetes, 
     currently taking lisinopril 10mg daily and metformin 500mg BID"
)

# Returns structured entities:

# {

#   "diagnoses": ["hypertension", "diabetes mellitus"],

#   "medications": [

#     {"name": "lisinopril", "dose": "10mg", "frequency": "daily"},

#     {"name": "metformin", "dose": "500mg", "frequency": "BID"}

#   ]

# }
```

**Entity Types Recognized:**
| Category | Examples | Notes |
|----------|----------|-------|
| **Diagnoses** | diabetes, hypertension, pneumonia | ICD-10 compatible where possible |
| **Symptoms** | chest pain, headache, nausea | Includes severity modifiers |
| **Medications** | metformin, lisinopril, aspirin | Extracts dose, route, frequency |
| **Procedures** | ECG, CT scan, blood draw | Includes body site |
| **Anatomy** | left arm, chest, abdomen | Laterality and location |
| **Lab Values** | glucose 120, BP 140/90 | Units and reference ranges |
| **Temporal** | yesterday, 3 days ago, chronic | Normalized to relative dates |

**Common Issues and Solutions:**

**Issue: Missed medications**
- Symptom: Generic names not recognized (e.g., "water pill" for diuretic)
- Solution: Manual review required; tool flags colloquial terms for verification

**Issue: Ambiguous abbreviations**
- Symptom: "SOB" could be shortness of breath or something else
- Solution: Context-aware disambiguation; flag uncertain cases

**Issue: Misspelled drug names**
- Symptom: "metfomin" instead of "metformin"
- Solution: Fuzzy matching with confidence threshold; flag low-confidence matches

### 3. SOAP Section Classification

Automatically categorize sentences into appropriate SOAP sections:

```python

# Classify content into SOAP sections
classified = generator.classify_soap_sections(
    "Patient reports chest pain for 2 days. Physical exam shows BP 140/90. 
     Likely angina. Schedule stress test and start aspirin 81mg daily."
)

# Output structure:

# {

#   "Subjective": ["Patient reports chest pain for 2 days"],

#   "Objective": ["Physical exam shows BP 140/90"],

#   "Assessment": ["Likely angina"],

#   "Plan": ["Schedule stress test", "start aspirin 81mg daily"]

# }
```

**Classification Rules:**
| Section | Content Type | Examples |
|---------|--------------|----------|
| **S** - Subjective | Patient-reported information | "Patient states...", "Patient reports...", "Complains of..." |
| **O** - Objective | Observable/measurable findings | Vital signs, physical exam, lab results, imaging |
| **A** - Assessment | Clinical interpretation | Diagnosis, differential, clinical impression |
| **P** - Plan | Actions to be taken | Medications, procedures, follow-up, patient education |

**Multi-label Handling:**
Some sentences span multiple sections (e.g., "Patient reports chest pain [S], which was sharp and 8/10 [S], with ECG showing ST elevation [O]")
- Tool splits compound sentences at conjunctions
- Assigns primary and secondary labels with confidence scores

**Best Practices:**
- Review classification accuracy, especially for complex multi-part statements
- Manually verify Assessment section (most critical for patient care)
- Ensure temporal context preserved (recent vs. chronic symptoms)

### 4. Temporal Information Extraction

Parse and normalize timeline information:

```python

# Extract temporal relationships
timeline = generator.extract_temporal_info(
    "Patient had chest pain starting 3 days ago, worsening since yesterday. 
     Had similar episode 2 months ago that resolved with rest."
)

# Returns:

# {

#   "onset": "3 days ago",

#   "progression": "worsening",

#   "previous_episodes": [

#     {"time": "2 months ago", "resolution": "with rest"}

#   ]

# }
```

**Temporal Elements Extracted:**
- **Onset**: When symptoms started ("2 days ago", "this morning")
- **Duration**: How long symptoms lasted ("for 3 hours", "ongoing")
- **Frequency**: How often symptoms occur ("daily", "intermittently")
- **Progression**: Getting better/worse/stable
- **Prior Episodes**: Previous similar events
- **Context**: "before meals", "with exertion", "at night"

**Normalization:**
Converts relative dates to standardized format:
- "yesterday" → Encounter date minus 1 day
- "3 days ago" → Specific date calculated
- "chronic" → Flagged for chronic condition tracking

### 5. Negation and Uncertainty Detection

Critical for accurate medical documentation:

```python

# Detect negations and uncertainties
analysis = generator.analyze_certainty(
    "Patient denies chest pain. No shortness of breath. 
     Possibly had fever yesterday but not sure."
)

# Identifies:

# - "denies chest pain" → Negative finding (important!)

# - "No shortness of breath" → Negative finding

# - "Possibly had fever" → Uncertain finding (flag for verification)
```

**Detection Categories:**
| Type | Cues | Action |
|------|------|--------|
| **Negation** | denies, no, without, absent | Mark as negative finding |
| **Uncertainty** | possibly, maybe, uncertain, ? | Flag for physician review |
| **Hypothetical** | if, would, could | Note as conditional |
| **Family History** | family history of, mother had | Separate from patient findings |

**⚠️ Critical:**
Negation errors are high-risk (e.g., missing "denies" → documenting symptom they don't have)
- Always verify negative findings in Subjective section
- Uncertain findings must be explicitly marked for review

### 6. Structured SOAP Generation

Produce final formatted output:

```python

# Generate complete SOAP note
soap_output = generator.generate_soap_document(
    structured_data=classified,
    format="markdown",  # Options: markdown, json, hl7, text
    include_metadata=True
)
```

**Output Format:**
```markdown

# SOAP Note

**Patient ID:** P12345  
**Date:** 2026-01-15  
**Provider:** Dr. Smith

## Subjective
Patient reports [extracted symptoms with duration]. History of [chronic conditions]. 
Currently taking [medications]. Patient denies [negative findings].

## Objective
**Vital Signs:** [BP, HR, RR, Temp, O2Sat]  
**Physical Examination:** [Exam findings by system]  
**Laboratory/Data:** [Relevant results]

## Assessment
[Primary diagnosis/differential]  
[Clinical reasoning summary]

## Plan
1. [Action item 1]
2. [Action item 2]
3. [Follow-up instructions]

---
*Generated by AI. REQUIRES PHYSICIAN REVIEW before entry into patient record.*
```

**Export Formats:**
| Format | Use Case | Notes |
|--------|----------|-------|
| **Markdown** | Human review, documentation | Default, readable |
| **JSON** | System integration, research | Structured data |
| **HL7 FHIR** | EHR integration | Healthcare standard |
| **Plain Text** | Simple documentation | Minimal formatting |
| **CSV** | Data analysis, research | Tabular data export |

## Limitations

- **Not a diagnostic tool**: Cannot make medical decisions or diagnoses
- **Specialty coverage**: Best performance in internal medicine, family practice; variable in highly specialized fields
- **Language**: Optimized for English; limited support for other languages
- **Context window**: May lose context in very long, complex encounters
- **Ambiguity**: Struggles with highly ambiguous or contradictory input
- **Rare conditions**: May not recognize very rare diseases or new medications
- **Non-verbal cues**: Cannot interpret tone, emphasis, or non-verbal information from audio

## Parameters

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `--input`, `-i` | string | - | No | Input clinical text directly |
| `--input-file`, `-f` | string | - | No | Path to input text file |
| `--output`, `-o` | string | - | No | Output file path |
| `--patient-id`, `-p` | string | - | No | Patient identifier |
| `--provider` | string | - | No | Healthcare provider name |
| `--format` | string | markdown | No | Output format (markdown, json) |

## Usage

### Basic Usage

```text

# Generate SOAP from text
python scripts/main.py --input "Patient reports chest pain..." --output note.md

# From file
python scripts/main.py --input-file consultation.txt --patient-id P12345 --provider "Dr. Smith"

# JSON output
python scripts/main.py --input-file notes.txt --format json --output note.json
```

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

This skill accepts requests that match the documented purpose of `automated-soap-note-generator` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `automated-soap-note-generator` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

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
