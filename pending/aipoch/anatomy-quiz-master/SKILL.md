---
name: anatomy-quiz-master
description: Generate interactive anatomy quizzes for medical education with multiple.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Anatomy Quiz Master

## When to Use

- Use this skill when the task is to Generate interactive anatomy quizzes for medical education with multiple.
- Use this skill for academic writing tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## Key Features

- Scope-focused workflow aligned to: Generate interactive anatomy quizzes for medical education with multiple.
- Packaged executable path(s): `scripts/main.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `argparse`: `unspecified`. Declared in `requirements.txt`.
- `json`: `unspecified`. Declared in `requirements.txt`.
- `random`: `unspecified`. Declared in `requirements.txt`.

## Example Usage

See `## Usage` above for related details.

```bash
cd "20260318/scientific-skills/Academic Writing/anatomy-quiz-master"
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

Comprehensive anatomy education tool that generates interactive quizzes covering gross anatomy, neuroanatomy, and clinical anatomy with adaptive difficulty and detailed explanations.

**Key Capabilities:**
- **Regional Quizzes**: Head/neck, thorax, abdomen, pelvis, limbs
- **Multiple Question Types**: Identification, function, clinical correlation
- **Adaptive Difficulty**: Basic, intermediate, advanced levels
- **Image Integration**: Label identification with anatomical images
- **Progress Tracking**: Performance analytics and weak area identification
- **Exam Mode**: Timed simulations for USMLE-style preparation

## Core Capabilities

### 1. Regional Anatomy Quizzes

Generate focused quizzes by body region:

```python
from scripts.quiz_generator import QuizGenerator

generator = QuizGenerator()

# Generate thorax quiz
quiz = generator.generate_quiz(
    region="thorax",
    topics=["heart", "lungs", "mediastinum", "thoracic_wall"],
    difficulty="intermediate",
    n_questions=20
)

# Export for LMS
quiz.export(format="json", filename="thorax_quiz.json")
```

**Supported Regions:**
| Region | Subtopics | Question Types |
|--------|-----------|----------------|
| **Head & Neck** | Skull, cranial nerves, triangles, viscera | Identification, pathways, clinical |
| **Thorax** | Heart, lungs, mediastinum, pleura | Relations, auscultation, imaging |
| **Abdomen** | GI tract, retroperitoneum, vessels | Peritoneal reflections, vascular supply |
| **Pelvis** | Organs, perineum, walls | Gender differences, clinical correlations |
| **Upper Limb** | Shoulder, arm, forearm, hand | Muscle actions, innervation, clinical |
| **Lower Limb** | Hip, thigh, leg, foot | Gait, compartments, clinical exams |
| **Back** | Vertebral column, spinal cord, muscles | Levels, landmarks, clinical |

### 2. Neuroanatomy Pathway Tracing

Specialized quizzes for neural pathways:

```python

# Neuroanatomy quiz
neuro_quiz = generator.generate_neuro_quiz(
    pathway_type="motor",  # or "sensory", "cranial_nerves", "reflexes"
    include_lesions=True,
    clinical_correlations=True
)
```

**Pathway Types:**
- **Motor Pathways**: Corticospinal, corticobulbar, basal ganglia circuits
- **Sensory Pathways**: Dorsal column, spinothalamic, trigeminal
- **Cranial Nerves**: All 12 nerves with nuclei and clinical tests
- **Reflex Arcs**: Deep tendon, superficial, visceral
- **Vascular**: Arterial supply, venous drainage, stroke syndromes

### 3. Clinical Correlation Questions

Integrate anatomy with clinical scenarios:

```python
clinical_quiz = generator.generate_clinical_quiz(
    region="abdomen",
    scenario_types=["surgery", "radiology", "physical_exam"],
    difficulty="advanced"
)
```

**Question Formats:**
```
Clinical Scenario:
"A 45-year-old male presents with epigastric pain radiating to the back. 
CT shows a mass in the lesser sac."

Question: "Which artery runs immediately posterior to the body of the 
pancreas and would be at risk during resection?"

A) Splenic artery
B) Superior mesenteric artery
C) Common hepatic artery
D) Left gastric artery

Correct: B) Superior mesenteric artery

Explanation: The SMA emerges from the aorta at L1 and passes posterior 
to the neck of the pancreas and anterior to the uncinate process...
```

### 4. Adaptive Learning System

Adjust difficulty based on performance:

```python
from scripts.adaptive import AdaptiveEngine

engine = AdaptiveEngine()

# Track student performance
student_progress = engine.track_performance(
    student_id="student_001",
    quiz_results=results,
    time_per_question=True
)

# Generate personalized quiz targeting weak areas
personalized = engine.generate_adaptive_quiz(
    student_progress=student_progress,
    focus_areas=["thorax_vessels", "cranial_nerves"],
    mastery_threshold=0.80
)
```

## Quality Checklist

**Question Quality:**
- [ ] Anatomical accuracy verified against standard atlases (Netter, Gray's)
- [ ] Clinical correlations reviewed by licensed physicians
- [ ] Multiple difficulty levels appropriately calibrated
- [ ] Distractors (wrong answers) are plausible and educational
- [ ] Explications explain *why* correct answer is right
- [ ] Image quality sufficient for identification (resolution, labeling)

**Educational Value:**
- [ ] Questions test high-yield anatomy (clinically relevant)
- [ ] Progressive difficulty builds knowledge systematically
- [ ] Clinical scenarios reflect real patient presentations
- [ ] Explanations include anatomical reasoning

**Technical Quality:**
- [ ] Randomization prevents pattern recognition
- [ ] No duplicate questions in quiz banks
- [ ] Image files properly licensed or original
- [ ] Accessibility compliance (alt text for images)

**Before Use:**
- [ ] **CRITICAL**: Faculty review for anatomical accuracy
- [ ] Pilot test with target student population
- [ ] Time limits appropriate for difficulty
- [ ] Answer key double-checked for errors

## Common Pitfalls

**Content Issues:**
- ❌ **Outdated anatomical knowledge** → Teaching old terminology
  - ✅ Use current Terminologia Anatomica standards

- ❌ **Nit-picky details** → Testing obscure structures rarely clinically relevant
  - ✅ Focus on high-yield anatomy that appears in clinical practice

- ❌ **Unclear images** → Poor resolution or confusing labels
  - ✅ Use high-quality images; test label legibility at screen resolution

**Educational Issues:**
- ❌ **Questions too easy** → No learning benefit
  - ✅ Calibrate to student level; aim for 60-80% success rate

- ❌ **No clinical context** → Pure memorization without application
  - ✅ Include clinical correlation questions

- ❌ **Punitive difficulty** → Discouraging rather than challenging
  - ✅ Provide encouraging feedback; focus on improvement

**Technical Issues:**
- ❌ **Predictable patterns** → Students game the system
  - ✅ Randomize question order and distractor placement

- ❌ **No progress tracking** → Can't identify weak areas
  - ✅ Implement analytics to guide focused study

## References

Available in `references/` directory:

- `netter_atlas_correlation.md` - Question-to-atlas page mapping
- `terminologia_anatomica.md` - Standard anatomical terminology
- `usmle_content_outline.md` - NBME anatomy topic frequencies
- `clinical_correlations.md` - High-yield clinical anatomy scenarios
- `image_sources.md` - Licensed anatomical image repositories
- `difficulty_calibration.md` - Bloom's taxonomy level alignment

## Scripts

Located in `scripts/` directory:

- `main.py` - CLI for quiz generation
- `quiz_generator.py` - Core question generation engine
- `neuro_quiz.py` - Specialized neuroanatomy questions
- `clinical_correlator.py` - Clinical scenario integration
- `adaptive_engine.py` - Personalized difficulty adjustment
- `image_quiz.py` - Label identification with images
- `progress_tracker.py` - Performance analytics
- `report_generator.py` - Progress reports and statistics

## Limitations

- **Cadaver Images**: Cannot replace hands-on dissection experience
- **3D Spatial Relations**: 2D images may not convey depth relationships
- **Variability**: Normal anatomical variation not fully captured
- **Updates**: Anatomical knowledge evolves; requires periodic review
- **Cultural Sensitivity**: Some anatomical terms may vary by region
- **Disability Accommodation**: Image-based questions need alternatives for visually impaired students

## Parameters

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `--region`, `-r` | string | upper_limb | No | Anatomical region (upper_limb, lower_limb, thorax, abdomen, pelvis, head_neck, neuroanatomy) |
| `--difficulty`, `-d` | string | intermediate | No | Difficulty level (basic, intermediate, advanced) |
| `--count`, `-c` | int | 1 | No | Number of questions to generate |
| `--output`, `-o` | string | - | No | Output file path (JSON format) |
| `--format` | string | json | No | Output format (json or text) |
| `--list-regions` | flag | - | No | List all available regions and exit |

## Usage

### Basic Usage

```text

# Generate single question
python scripts/main.py --region upper_limb

# Generate 10-question quiz
python scripts/main.py --region neuroanatomy --difficulty advanced --count 10 --output quiz.json

# List available regions
python scripts/main.py --list-regions

# Text format output
python scripts/main.py --region thorax --format text
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

This skill accepts requests that match the documented purpose of `anatomy-quiz-master` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `anatomy-quiz-master` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

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
