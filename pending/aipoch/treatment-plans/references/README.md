# Treatment Plans Skill

## Overview

This skill is used to generate **concise and clinician-centric** medical treatment plans for all clinical specialties. It provides LaTeX/PDF templates with SMART goal frameworks, evidence-based interventions, regulatory compliance, and validation tools for patient-centered care planning.

Most cases **default to a 1-page format** — positioned as a "Quick Reference Card" rather than a "comprehensive textbook."

## What's Included

### 📋 Seven Treatment Plan Types

1. **One-Page Treatment Plan** (Preferred) — A concise, quick-reference format suitable for most clinical scenarios.
2. **General Medical Treatment Plans** — Primary care, chronic diseases (Diabetes, Hypertension, Heart Failure).
3. **Rehabilitation Treatment Plans** — Physical therapy, occupational therapy, cardiopulmonary rehabilitation.
4. **Mental Health Treatment Plans** — Psychiatric care, depression, anxiety, PTSD, substance abuse.
5. **Chronic Disease Management Plans** — Complex multimorbidity, long-term care coordination.
6. **Perioperative Care Plans** — Preoperative optimization, ERAS protocols, postoperative recovery.
7. **Pain Management Plans** — Acute and chronic pain, multimodal analgesia, opioid reduction strategies.

### 📚 Reference Files (5 Comprehensive Guides)

- `treatment_plan_standards.md` — Professional standards, documentation requirements, legal considerations.
- `goal_setting_frameworks.md` — SMART goals, patient-centered outcomes, shared decision-making.
- `intervention_guidelines.md` — Evidence-based treatments, pharmacological and non-pharmacological therapies.
- `regulatory_compliance.md` — HIPAA compliance, billing documentation, quality metrics.
- `specialty_specific_guidelines.md` — Detailed guidelines for each treatment plan type.

### 📄 LaTeX Templates (7 Professional Sets)

- `one_page_treatment_plan.tex` — **Preferred** — Information-dense, easy-to-scan 1-page format (similar to precision oncology reports).
- `general_medical_treatment_plan.tex` — Comprehensive medical care planning.
- `rehabilitation_treatment_plan.tex` — Functional recovery and therapy.
- `mental_health_treatment_plan.tex` — Psychiatric and behavioral health.
- `chronic_disease_management_plan.tex` — Long-term disease management.
- `perioperative_care_plan.tex` — Surgical and procedural care.
- `pain_management_plan.tex` — Multimodal pain treatment.

### 🔧 Validation Scripts (4 Automation Tools)

- `generate_template.py` — Interactive template selection and generation.
- `validate_treatment_plan.py` — Comprehensive quality and compliance checks.
- `check_completeness.py` — Verifies that all necessary sections are present.
- `timeline_generator.py` — Creates visual treatment timelines and schedules.

## Quick Start

### Generate Treatment Plan Template

```bash
cd .claude/skills/treatment-plans/scripts
python generate_template.py

# Or specify type directly
python generate_template.py --type general_medical --output diabetes_plan.tex
```

Available template types:
- `one_page` (Preferred - suitable for most cases)
- `general_medical`
- `rehabilitation`
- `mental_health`
- `chronic_disease`
- `perioperative`
- `pain_management`

### Compile to PDF

```bash
cd /path/to/your/treatment/plan
pdflatex my_treatment_plan.tex
```

### Validate Treatment Plan

```bash
# Check completeness
python check_completeness.py my_treatment_plan.tex

# Comprehensive validation
python validate_treatment_plan.py my_treatment_plan.tex
```

### Generate Treatment Timeline

```bash
python timeline_generator.py --plan my_treatment_plan.tex --output timeline.pdf
```

## Standard Treatment Plan Components

All templates include the following core sections:

### 1. Patient Information (De-identified)
- Demographics and relevant medical background
- Active conditions and comorbidities
- Current medications and allergies
- Functional status baseline
- HIPAA-compliant de-identification

### 2. Diagnosis & Assessment Summary
- Primary diagnosis (ICD-10 codes)
- Secondary diagnoses
- Severity classification
- Functional limitations
- Risk stratification

### 3. Treatment Goals (SMART Format)

**Short-term Goals** (1-3 months):
- Specific, measurable outcomes
- Realistic targets with clear timeframes
- Patient-centered priorities

**Long-term Goals** (6-12 months):
- Disease control targets
- Functional improvement goals
- Quality of life enhancement
- Complication prevention

### 4. Interventions

- **Pharmacological**: Medications including dosage, frequency, and monitoring requirements.
- **Non-pharmacological**: Lifestyle modifications, behavioral interventions, education.
- **Procedural**: Planned surgeries/procedures, specialty referrals, diagnostic testing.

### 5. Timeline & Schedule
- Treatment phases with timeframes
- Visit frequency
- Milestone assessments
- Expected duration of treatment

### 6. Monitoring Parameters
- Clinical outcomes to track
- Assessment tools and scales
- Frequency of monitoring
- Intervention thresholds

### 7. Expected Outcomes
- Primary outcome measures
- Success criteria
- Improvement timeline
- Long-term prognosis

### 8. Follow-up Plan
- Appointment schedule
- Communication protocol
- Emergency procedures
- Referral/transition planning

### 9. Patient Education
- Understanding of the condition
- Self-management skills
- Warning signs
- Resources and support

### 10. Risk Mitigation
- Adverse effect management
- Safety monitoring
- Emergency action plans
- Fall/infection prevention

## Common Use Cases

### 1. Type 2 Diabetes Management

```
Goal: Develop a comprehensive treatment plan for newly diagnosed diabetes

Template: general_medical_treatment_plan.tex

Key Components:
- SMART Goals: HbA1c <7% in 3 months, 10 lb weight loss in 6 months
- Medication: Metformin titration schedule
- Lifestyle: Diet, exercise, glucose monitoring
- Monitoring: HbA1c every 3 months, quarterly follow-ups
- Education: Diabetes self-management education
```

### 2. Post-Stroke Rehabilitation

```
Goal: Create a rehabilitation plan for a stroke patient with hemiplegia

Template: rehabilitation_treatment_plan.tex

Key Components:
- Functional Assessment: FIM scores, ROM, strength testing
- PT Goals: Independent ambulation 150 ft with walker in 12 weeks
- OT Goals: Independence in ADLs, upper extremity functional recovery
- Therapy Schedule: PT/OT/SLP 3x weekly each
- Home exercise program
```

### 3. Major Depressive Disorder

```
Goal: Develop a comprehensive treatment plan for depression

Template: mental_health_treatment_plan.tex

Key Components:
- Assessment: PHQ-9 score of 16 (Moderate-Severe)
- Goals: PHQ-9 <5, return to work within 12 weeks
- Psychotherapy: Weekly CBT sessions
- Medication: SSRI with titration plan
- Safety Plan: Crisis contacts, warning signs
```

### 4. Total Knee Arthroplasty (TKA)

```
Goal: Perioperative care plan for elective TKA

Template: perioperative_care_plan.tex

Key Components:
- Preop Optimization: Medical clearance, medication management
- ERAS Protocol implementation
- Postop Milestones: Ambulation on POD 1, discharge on POD 2-3
- Pain Management: Multimodal analgesia
- Rehab Plan: PT starting POD 0
```

### 5. Chronic Low Back Pain

```
Goal: Multimodal pain management plan

Template: pain_management_plan.tex

Key Components:
- Pain Assessment: Location, intensity, impact on function
- Goals: Reduce pain from 7/10 to 3/10, return to work
- Medication: Non-opioid analgesics, adjuvant medications
- PT: Core strengthening, McKenzie therapy
- Behavioral: Pain CBT, mindfulness
- Interventional: Consider ESI if poor response
```

## SMART Goals Framework

All treatment plans use SMART criteria for goal setting:

- **Specific**: Clear, well-defined outcomes (not vague)
- **Measurable**: Quantifiable metrics or observable behaviors
- **Achievable**: Realistic goals considering patient capacity and resources
- **Relevant**: Aligned with patient priorities and values
- **Time-bound**: Defined schedule for achievement

### Examples

**Good SMART Goals**:
- Reduce HbA1c from 8.5% to <7% within 3 months
- Ambulate 150 feet independently with assistive device within 8 weeks
- Reduce PHQ-9 depression score from 18 to <10 within 8 weeks
- Achieve knee flexion >90 degrees by postoperative day 14
- Reduce pain from 7/10 to ≤4/10 within 6 weeks

**Poor Goals** (Non-SMART):
- "Feel better" (Not specific, not measurable)
- "Improve diabetes" (Not specific, no timeframe)
- "Get stronger" (Not measurable)
- "Return to normal" (Vague, not specific)

## Workflow Examples

### Standard Treatment Plan Workflow

1. **Assess Patient** — Complete history, physical exam, diagnostic testing.
2. **Select Template** — Choose appropriate template based on clinical context.
3. **Generate Template** — `python generate_template.py --type [type]`.
4. **Customize Plan** — Fill in patient-specific info (de-identified).
5. **Set SMART Goals** — Define measurable short and long-term goals.
6. **Specify Interventions** — Evidence-based pharmacological and non-pharmacological treatments.
7. **Create Timeline** — Schedule follow-ups, milestones, re-evaluations.
8. **Define Monitoring** — Outcome measures, frequency of assessment.
9. **Verify Completeness** — `python check_completeness.py plan.tex`.
10. **Quality Check** — `python validate_treatment_plan.py plan.tex`.
11. **Review Quality Checklist** — Compare against `quality_checklist.md`.
12. **Generate PDF** — `pdflatex plan.tex`.
13. **Communicate with Patient** — Shared decision-making, confirm understanding.
14. **Implement & Document** — Execute plan, track progress in clinical notes.
15. **Re-evaluate & Revise** — Adjust plan based on outcomes.

### Multidisciplinary Care Plan Workflow

1. **Identify Team Members** — PCP, specialists, therapists, case managers.
2. **Create Base Plan** — Generate template for primary condition.
3. **Add Specialty Sections** — Integrate consultant recommendations.
4. **Coordinate Goals** — Ensure alignment of goals across disciplines.
5. **Define Communication** — Team meeting schedule, documentation sharing.
6. **Assign Responsibilities** — Clarify who manages each intervention.
7. **Create Care Timeline** — Coordinate appointments across providers.
8. **Share Plan** — Distribute to all team members and the patient.
9. **Track Collectively** — Shared monitoring and outcome tracking.
10. **Periodic Team Review** — Collaborative adjustment of the plan.

## Best Practices

### Patient-Centered Care
✓ Involve patients in goal setting and decision-making  
✓ Respect cultural beliefs and language preferences  
✓ Use appropriate language for health literacy levels  
✓ Align plans with patient values and life circumstances  
✓ Support patient agency and self-management  

### Evidence-Based Practice
✓ Follow current clinical practice guidelines  
✓ Use interventions with proven efficacy  
✓ Incorporate quality metrics (HEDIS, CMS)  
✓ Avoid low-value or ineffective interventions  
✓ Update plans based on emerging evidence  

### Regulatory Compliance
✓ De-identify according to HIPAA Safe Harbor method (18 identifiers)  
✓ Document medical necessity to support billing  
✓ Include records of informed consent  
✓ Sign and date all treatment plans  
✓ Maintain professional documentation standards  

### High-Quality Documentation
✓ Complete all necessary sections  
✓ Use clear, professional medical terminology  
✓ Include specific, measurable goals  
✓ Specify exact medications (dose, route, frequency)  
✓ Define monitoring parameters and frequency  
✓ Address safety and risk mitigation  

### Care Coordination
✓ Communicate plan to the entire care team  
✓ Define roles and responsibilities  
✓ Coordinate across care settings  
✓ Integrate specialty recommendations  
✓ Plan for transitions of care  

## Integration with Other Skills

### Clinical Reports
- **SOAP Notes**: Document implementation and progress of the treatment plan.
- **H&P Documentation**: Initial assessment informs treatment planning.
- **Discharge Summaries**: Summarize the execution of the treatment plan.
- **Progress Notes**: Track goal achievement and plan modifications.

### Scientific Writing
- **Citation Management**: Cite clinical practice guidelines.
- **Literature Review**: Understand the evidence base for interventions.
- **Research Retrieval**: Find current treatment recommendations.

### Research
- **Grant Writing**: Treatment protocols for clinical trials.
- **Clinical Trial Reporting**: Documenting trial interventions.

## Clinical Practice Guidelines

Treatment plans should align with evidence-based guidelines:

### General Medicine
- ADA Standards of Care in Diabetes
- ACC/AHA Cardiovascular Guidelines
- GOLD Guidelines for COPD
- JNC-8 Hypertension Guidelines
- KDIGO Guidelines for Chronic Kidney Disease

### Rehabilitation Medicine
- APTA Clinical Practice Guidelines for Physical Therapy
- AOTA Occupational Therapy Practice Framework
- AHA/AACVPR Cardiac Rehabilitation Guidelines
- Best Practices in Stroke Rehabilitation

### Mental Health
- APA (American Psychiatric Association) Practice Guidelines
- VA/DoD Clinical Practice Guidelines for Mental Health
- NICE (National Institute for Health and Care Excellence) Guidelines
- Evidence-based psychotherapy protocols (CBT, DBT, ACT)

### Pain Management
- CDC Guideline for Prescribing Opioids
- AAPM (American Academy of Pain Medicine) Guidelines
- WHO Analgesic Ladder
- Best Practices in Multimodal Analgesia

### Perioperative Care
- ERAS (Enhanced Recovery After Surgery) Society Guidelines
- ASA Perioperative Guidelines
- SCIP (Surgical Care Improvement Project) Measures

## Professional Standards

### Documentation Requirements
- Complete and accurate patient information
- Clear diagnoses with appropriate ICD-10 codes
- Evidence-based interventions
- Measurable goals and outcomes
- Clear monitoring and follow-up
- Provider signature, credentials, and date

### Medical Necessity
Treatment plans must demonstrate:
- Medical appropriateness of interventions
- Consistency with diagnosis and severity
- Evidence supporting treatment choices
- Expected outcomes and benefits
- Reasonableness of frequency and duration

### Legal Considerations
- Documentation of informed consent
- Patient understanding and agreement
- Risk disclosure and mitigation
- Professional liability protection
- Compliance with state/federal regulations

## Support and Resources

### Getting Help

1. **Check Reference Files** — Comprehensive guides in the `references/` directory.
2. **Review Templates** — See example structures in the `assets/` directory.
3. **Run Validation Scripts** — Use automation tools to identify issues.
4. **Consult SKILL.md** — Detailed documentation and best practices.
5. **Review Quality Checklist** — Ensure all quality standards are met.

### External Resources

- Clinical Practice Guidelines from specialty societies
- UpToDate and DynaMed treatment recommendations
- AHRQ Effective Health Care Program
- Cochrane Library for evidence on interventions
- CMS Quality Measures and HEDIS specifications
- HEDIS (Healthcare Effectiveness Data and Information Set)

### Professional Organizations

- American Medical Association (AMA)
- American Academy of Family Physicians (AAFP)
- Specialty societies (ADA, ACC, AHA, APA, etc.)
- Joint Commission standards
- Centers for Medicare & Medicaid Services (CMS)

## Frequently Asked Questions

### How do I choose the right template?

Select the template based on your primary clinical focus:
- **Chronic medical conditions** → general_medical or chronic_disease
- **Post-surgery or injury** → rehabilitation or perioperative
- **Psychiatric conditions** → mental_health
- **Pain as the primary issue** → pain_management

### What if my patient has multiple conditions?

For complex multimorbidity, use the `chronic_disease_management_plan.tex` template, or select the template for the primary condition and add sections for comorbidities.

### How often should treatment plans be updated?

- **Initial Creation**: At the time of diagnosis or start of treatment.
- **Periodic Updates**: Every 3-6 months for chronic conditions.
- **Significant Changes**: When goals are met or treatment is modified.
- **Annual Review**: Minimum requirement for all chronic disease plans.

### Can I modify the LaTeX templates?

Yes! Templates are designed to support customization. You can modify sections, add specialty-specific content, or adjust formatting as needed.

### How do I ensure HIPAA compliance?

- Remove all 18 HIPAA identifiers (see Safe Harbor method).
- Use age ranges instead of exact ages (e.g., "60-65" instead of "63").
- Remove specific dates; use relative timelines.
- Omit geographic identifiers smaller than a state.
- Use the `check_deidentification.py` script from the clinical-reports skill.

### What if the validation script finds issues?

Review the specific issues identified, consult the reference files for guidance, and modify the plan accordingly. Common issues include:
- Missing required sections
- Goals that are not SMART
- Insufficient monitoring parameters
- Incomplete medication information

## License

Part of the Claude Scientific Writing Project. See main LICENSE file.

---

For detailed documentation, see `SKILL.md`. For questions, consult the comprehensive reference files in the `references/` directory.