---
name: digital-twin-discharge-drafter
description: Use when drafting patient discharge summaries, creating personalized discharge instructions, simulating post-discharge outcomes, reducing hospital readmissions, or optimizing care transitions. Generates AI-enhanced discharge documentation with digital twin predictions for improved patient safety.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Digital Twin Discharge Drafter

Generate AI-enhanced discharge summaries and personalized care plans using digital twin patient models to predict outcomes and optimize post-discharge care transitions.

## When to Use

- Use this skill when the task needs Use when drafting patient discharge summaries, creating personalized discharge instructions, simulating post-discharge outcomes, reducing hospital readmissions, or optimizing care transitions. Generates AI-enhanced discharge documentation with digital twin predictions for improved patient safety.
- Use this skill for academic writing tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## Key Features

- Scope-focused workflow aligned to: Use when drafting patient discharge summaries, creating personalized discharge instructions, simulating post-discharge outcomes, reducing hospital readmissions, or optimizing care transitions. Generates AI-enhanced discharge documentation with digital twin predictions for improved patient safety.
- Packaged executable path(s): `scripts/main.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `dataclasses`: `unspecified`. Declared in `requirements.txt`.
- `dateutil`: `unspecified`. Declared in `requirements.txt`.

## Example Usage

```bash
cd "20260318/scientific-skills/Academic Writing/digital-twin-discharge-drafter"
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

## Quick Start

```python
from scripts.discharge_drafter import DischargeDrafter

drafter = DischargeDrafter()

# Generate comprehensive discharge summary
summary = drafter.generate(
    patient_id="PT12345",
    admission_data=admission_info,
    hospital_course=treatment_history,
    digital_twin_model=patient_model,
    output_format="structured"
)

# Export patient-friendly version
patient_version = drafter.generate_patient_friendly(summary)

print(summary.readmission_risk_score)  # 0.23
print(summary.key_interventions)       # ['home_health', 'med_reconciliation']
```

## Core Capabilities

### 1. Digital Twin-Powered Summary Generation

```python
summary = drafter.create_summary(
    patient_data=patient_record,
    digital_twin_model=twin_model,
    include_predictions=True,
    risk_stratification="high",
    readmission_risk_threshold=0.15
)
```

**Summary Components:**
- **Hospital Course**: AI-summarized treatment narrative
- **Digital Twin Predictions**: 7-day, 30-day outcome probabilities
- **Risk Stratification**: Readmission risk score with factors
- **Medication Reconciliation**: AI-validated med list
- **Follow-up Schedule**: Optimized based on patient model

### 2. Post-Discharge Outcome Simulation

```python
scenarios = drafter.simulate_outcomes(
    patient_model=digital_twin,
    scenarios=[
        "medication_adherent",
        "medication_non_adherent", 
        "follow_up_missed",
        "social_support_optimal"
    ],
    timeframe="30_days",
    metrics=["readmission_risk", "recovery_trajectory", "cost_projection"]
)
```

**Simulation Outputs:**

| Scenario | Readmission Risk | Recovery Time | Cost Impact |
|----------|-----------------|---------------|-------------|
| Optimal adherence | 5% | 14 days | Baseline |
| Med non-adherent | 25% | 28 days | +$8,500 |
| Missed follow-up | 18% | 21 days | +$4,200 |

### 3. Personalized Patient Instructions

```python
instructions = drafter.create_personalized_instructions(
    patient_profile=profile,
    health_literacy_level="assessed",  # or "8th_grade", "college"
    language_preference="English",
    cultural_considerations=True,
    access_barriers=["transportation", "cost"]
)

# Returns structured instructions
print(instructions.medication_list)      # Formatted medication table
print(instructions.followup_appointments)  # Scheduled visits
print(instructions.red_flags)            # When to call doctor
print(instructions.lifestyle_changes)    # Diet, activity restrictions
```

**Personalization Factors:**
- **Health Literacy**: Adjust complexity (Flesch-Kincaid 6th-12th grade)
- **Language**: Multi-language support with medical accuracy
- **Cultural**: Dietary restrictions, family dynamics, beliefs
- **Barriers**: Transportation, cost, caregiver availability

### 4. Risk-Based Care Planning

```python
care_plan = drafter.create_risk_based_plan(
    patient_risk_score=0.72,
    risk_factors=["CHF", "diabetes", "living_alone"],
    interventions=[
        "telehealth_monitoring",
        "home_health_visit",
        "pharmacy_consult"
    ]
)
```

**Risk Stratification:**

| Risk Level | Score | Interventions |
|------------|-------|---------------|
| Low | <0.10 | Standard discharge + phone follow-up |
| Moderate | 0.10-0.25 | + Telehealth monitoring |
| High | 0.25-0.50 | + Home health visit within 48h |
| Very High | >0.50 | + Care coordination + daily check-ins |

### 5. Quality Assurance

```python
qa_report = drafter.validate_summary(
    discharge_summary,
    checks=[
        "completeness_jcaho",
        "medication_accuracy",
        "readability_score",
        "prediction_confidence"
    ]
)
```

## CLI Usage

```text

# Generate complete discharge package
python scripts/discharge_drafter.py \
  --patient PT12345 \
  --digital-twin-model models/patient_v2.pkl \
  --include-predictions \
  --output-format both \
  --output-dir discharge_summaries/

# Batch process high-risk patients
python scripts/discharge_drafter.py \
  --batch high_risk_patients.csv \
  --priority ICU,CCU \
  --auto-escalate-risk 0.30

# Generate patient-friendly only
python scripts/discharge_drafter.py \
  --patient PT12345 \
  --mode patient-friendly \
  --reading-level 6th_grade \
  --language Spanish \
  --output patient_handout.pdf
```

## Common Patterns

### Pattern 1: CHF Patient Discharge

**Digital Twin Insights:**
- Baseline readmission risk: 22%
- With medication adherence: 8%
- Without follow-up: 35%

**Generated Interventions:**
- Daily weight telemonitoring
- Cardiology appointment within 7 days
- Medication reconciliation with pharmacist
- Home health evaluation

### Pattern 2: Post-Surgical Patient

**Digital Twin Insights:**
- Infection risk peaks day 3-5
- Mobility compliance critical for recovery

**Generated Plan:**
- Wound care video instructions
- Physical therapy schedule
- Red flag symptom checklist
- Pain management protocol

## Quality Checklist

**Pre-Discharge:**
- [ ] Digital twin model updated with hospital course
- [ ] Readmission risk calculated and documented
- [ ] Medication reconciliation completed
- [ ] Follow-up appointments scheduled
- [ ] Patient/caregiver education requirements assessed

**Discharge Summary:**
- [ ] Includes digital twin predictions with confidence intervals
- [ ] Risk factors clearly listed with mitigation strategies
- [ ] Patient-friendly instructions at appropriate literacy level
- [ ] Emergency contact numbers provided
- [ ] 24/7 nurse line access included

**Post-Discharge (24-48 hours):**
- [ ] Automated follow-up call triggered
- [ ] Pharmacy notified of new prescriptions
- [ ] Primary care provider receives summary
- [ ] Home health services activated (if indicated)

## Best Practices

**Digital Twin Model Maintenance:**
- Update models weekly with new patient data
- Validate predictions against actual outcomes
- Retrain models quarterly for accuracy improvement

**Patient Communication:**
- Always provide both clinical and patient-friendly versions
- Use teach-back method to confirm understanding
- Document health literacy level in patient record

## Common Pitfalls

❌ **Over-reliance on AI**: Digital twin predictions supplement, not replace, clinical judgment
✅ **Clinical Oversight**: Physician reviews and approves all AI-generated content

❌ **Generic Instructions**: One-size-fits-all discharge plans
✅ **Personalized Plans**: Tailored to individual patient models and barriers

❌ **Ignoring Low-Risk Patients**: Focusing only on high-risk cases
✅ **Universal Application**: All patients benefit from digital twin insights

---

**Skill ID**: 214 | **Version**: 1.0 | **License**: MIT

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

This skill accepts requests that match the documented purpose of `digital-twin-discharge-drafter` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `digital-twin-discharge-drafter` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

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
