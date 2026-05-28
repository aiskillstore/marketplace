---
name: linkedin-optimizer
description: Use when optimizing LinkedIn profiles for doctors, physicians, nurses, healthcare professionals, or medical researchers. Crafts compelling headlines, writes professional summaries, integrates healthcare keywords, and builds personal branding for medical careers.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# LinkedIn Optimizer for Healthcare Professionals

Optimize LinkedIn profiles for doctors, physicians, nurses, and healthcare professionals to enhance professional visibility and career opportunities.

## When to Use

- Use this skill when the task needs Use when optimizing LinkedIn profiles for doctors, physicians, nurses, healthcare professionals, or medical researchers. Crafts compelling headlines, writes professional summaries, integrates healthcare keywords, and builds personal branding for medical careers.
- Use this skill for other tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when the response must stay inside the documented task boundary instead of expanding into adjacent work.

## Key Features

- Scope-focused workflow aligned to: Use when optimizing LinkedIn profiles for doctors, physicians, nurses, healthcare professionals, or medical researchers. Crafts compelling headlines, writes professional summaries, integrates healthcare keywords, and builds personal branding for medical careers.
- Packaged executable path(s): `scripts/main.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

```bash
cd "20260318/scientific-skills/Academic Writing/linkedin-optimizer"
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
python scripts/main.py
```

## Workflow

1. Confirm the user objective, required inputs, and non-negotiable constraints before doing detailed work.
2. Validate that the request matches the documented scope and stop early if the task would require unsupported assumptions.
3. Use the packaged script path or the documented reasoning path with only the inputs that are actually available.
4. Return a structured result that separates assumptions, deliverables, risks, and unresolved items.
5. If execution fails or inputs are incomplete, switch to the fallback path and state exactly what blocked full completion.

## Quick Start

```python
from scripts.linkedin_optimizer import LinkedInOptimizer

optimizer = LinkedInOptimizer()

# Generate optimized profile content
profile = optimizer.optimize(
    role="Cardiologist",
    specialty="Interventional Cardiology",
    achievements=["Published 15+ peer-reviewed papers", "Led clinical trial for novel stent"],
    years_experience=12
)

print(profile.headline)
print(profile.about_section)
```

## Core Capabilities

### 1. Headline Optimization

```python
optimizer = LinkedInOptimizer()
headline = optimizer.generate_headline(
    title="Board-Certified Cardiologist",
    specialty="Heart Failure & Transplant",
    differentiator="Clinical Researcher"
)

# Output: "Board-Certified Cardiologist | Heart Failure & Transplant Specialist | Clinical Researcher"
```

**Headline Formulas:**
- `Title | Specialty | Differentiator`
- `Role | Key Skill | Mission`
- `Credentials | Focus Area | Value Proposition`

### 2. About Section Writing

```python
about = optimizer.write_about_section(
    role="Oncologist",
    approach="Patient-centered care with precision medicine",
    expertise=["Immunotherapy", "Clinical trials", "Palliative care"],
    achievements=["Treated 1000+ patients", "Principal investigator on 5 trials"]
)
```

**About Section Structure:**
1. **Opening Hook** (2-3 sentences) - Who you help and how
2. **Expertise Areas** (bullet points) - Key skills and specialties
3. **Key Achievements** (bullet points) - Quantified accomplishments
4. **Call to Action** - How to connect

**Example:**
> I'm a board-certified oncologist dedicated to advancing cancer treatment through precision medicine and immunotherapy. With over 10 years of experience, I specialize in developing personalized treatment plans that improve patient outcomes while maintaining quality of life.
>
> **Areas of Expertise:**
> - Immunotherapy and targeted therapy
> - Clinical trial design and implementation
> - Palliative care integration
> - Multi-disciplinary team leadership
>
> **Key Achievements:**
> - Treated 1000+ cancer patients with 85% positive outcomes
> - Principal investigator on 5 Phase II/III clinical trials
> - Published 20+ peer-reviewed papers on novel treatment protocols
>
> **Let's Connect:** Open to collaborations on clinical research and discussing innovative treatment approaches.

### 3. Keyword Integration

```python
keywords = optimizer.suggest_keywords(
    specialty="Emergency Medicine",
    role="ER Physician",
    target_audience=["Recruiters", "Hospital administrators", "Medical device companies"]
)
```

**High-Value Keywords by Specialty:**

| Specialty | Primary Keywords | Secondary Keywords |
|-----------|-----------------|-------------------|
| Cardiology | Cardiologist, Interventional Cardiology, Heart Failure | Clinical Cardiology, Cardiac Catheterization |
| Oncology | Oncologist, Medical Oncology, Cancer Treatment | Immunotherapy, Precision Medicine |
| Surgery | Surgeon, General Surgery, Minimally Invasive | Robotic Surgery, Laparoscopic |
| Pediatrics | Pediatrician, Child Health, Developmental Medicine | Neonatology, Pediatric Emergency |
| Research | Clinical Research, Principal Investigator, FDA Trials | Drug Development, Protocol Design |

### 4. Experience Section Optimization

```python
experiences = optimizer.optimize_experiences([
    {
        "title": "Attending Physician",
        "organization": "Mayo Clinic",
        "duration": "2019-Present",
        "achievements": ["Reduced readmission rates by 25%", "Implemented new protocol"]
    }
])
```

**Experience Formula:**
- **Action verb** + **What you did** + **Result/Impact**
- Example: "Implemented early discharge protocol reducing average length of stay by 2.3 days and saving $500K annually"

## CLI Usage

```text

# Optimize complete profile
python scripts/linkedin_optimizer.py \
  --role "Neurologist" \
  --specialty "Movement Disorders" \
  --achievements "Published 10 papers, Led Parkinson's clinic" \
  --output profile.json

# Generate only headline
python scripts/linkedin_optimizer.py \
  --mode headline \
  --title "Emergency Medicine Physician" \
  --specialty "Trauma & Critical Care"
```

## Common Patterns

See `references/linkedin-examples.md` for detailed examples:
- Academic Physician Profile
- Private Practice Doctor
- Medical Researcher
- Healthcare Executive
- Resident/Fellow Profile

## Quality Checklist

**Before Optimization:**
- [ ] Define target audience (recruiters, patients, collaborators)
- [ ] List 3-5 key achievements with metrics
- [ ] Identify unique value proposition

**After Optimization:**
- [ ] Headline under 220 characters
- [ ] About section includes keywords naturally
- [ ] All claims are verifiable
- [ ] Call to action is clear

## References

- `references/linkedin-examples.md` - Profile examples by specialty
- `references/keywords-by-specialty.json` - Keyword database
- `references/headline-templates.md` - Headline formulas

---

**Skill ID**: 201 | **Version**: 1.0 | **License**: MIT

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

This skill accepts requests that match the documented purpose of `linkedin-optimizer` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `linkedin-optimizer` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

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
