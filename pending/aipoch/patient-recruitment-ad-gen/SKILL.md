---
name: patient-recruitment-ad-gen
description: Generate ethical, compliant, and patient-friendly recruitment advertisements for clinical trials.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Patient Recruitment Ad Generator

Generate ethical, compliant, and patient-friendly recruitment advertisements for clinical trials.

## When to Use

- Use this skill when the task is to Generate ethical, compliant, and patient-friendly recruitment advertisements for clinical trials.
- Use this skill for academic writing tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## Key Features

- Scope-focused workflow aligned to: Generate ethical, compliant, and patient-friendly recruitment advertisements for clinical trials.
- Packaged executable path(s): `scripts/main.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

See `## Prerequisites` above for related details.

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `Third-party packages`: `not explicitly version-pinned in this skill package`. Add pinned versions if this skill needs stricter environment control.

## Example Usage

See `## Usage` above for related details.

```bash
cd "20260318/scientific-skills/Academic Writing/patient-recruitment-ad-gen"
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

## Purpose

This skill helps researchers, CROs, and medical institutions create patient recruitment advertisements that meet Institutional Review Board (IRB) / Ethics Committee (EC) requirements while being accessible and encouraging to potential participants.

## Key Compliance Requirements

### Essential Elements (IRB/EC Standards)

1. **Trial Identity**
   - Study title or identifier
   - Sponsor information (if required)

2. **Purpose Statement**
   - Clear description of the research
   - Why the study is being conducted

3. **Eligibility Criteria**
   - Inclusion criteria (who can participate)
   - Exclusion criteria (who cannot participate)

4. **Study Procedures**
   - What participants will do
   - Time commitment required
   - Number of visits

5. **Risks and Benefits**
   - Potential risks/discomforts
   - Potential benefits (direct and societal)
   - Statement that benefits are not guaranteed

6. **Confidentiality**
   - How personal information is protected
   - Regulatory oversight mention

7. **Voluntary Participation**
   - Right to withdraw at any time
   - No penalty for withdrawal
   - No impact on regular medical care

8. **Contact Information**
   - Principal Investigator
   - Study coordinator
   - IRB/EC contact for questions about rights

### Prohibited Content

- **Promises of cure** or guaranteed benefits
- **Undue influence** (excessive payment, coercion)
- **Misleading language** ("free treatment" when experimental)
- **Stigmatizing terms** ("sufferers," "victims")
- **Pressure tactics** (limited spots, urgency)

## Usage

### Input Parameters

```python
{
    "disease_condition": str,        # Target disease/condition
    "study_phase": str,              # Phase I/II/III/IV
    "intervention_type": str,        # Drug, device, procedure, etc.
    "target_population": str,        # Demographics, age range
    "study_duration": str,           # Expected time commitment
    "site_location": str,            # Study site location
    "compensation": Optional[str],   # Participant payment (if any)
    "pi_name": str,                  # Principal Investigator
    "contact_info": str,             # Phone/email for inquiries
    "irb_reference": str             # IRB/EC approval number
}
```

### Example

```python
python /Users/z04030865/.openclaw/workspace/skills/patient-recruitment-ad-gen/scripts/main.py \
    --disease "Type 2 Diabetes" \
    --phase "Phase II" \
    --intervention "Investigational oral medication" \
    --population "Adults 18-65 with T2DM" \
    --duration "12 weeks, 6 clinic visits" \
    --location "City Medical Center, Building C" \
    --pi "Dr. Sarah Chen" \
    --contact "(555) 123-4567 or diabetes-study@cmc.edu" \
    --irb "IRB-2024-001"
```

### Output

Generates a structured recruitment ad with:
- Headline (attention-grabbing, compliant)
- Study summary (plain language)
- Who can participate (eligibility)
- What's involved (procedures)
- Rights and protections (ethics)
- Contact information

## Technical Notes

- **Difficulty**: Medium
- **Language**: Patient-friendly (6th-8th grade reading level)
- **Tone**: Respectful, informative, empowering
- **Format**: Print, digital, or social media ready
- **Compliance**: Based on FDA, EMA, CIOMS, and ICH-GCP guidelines

## References

See `references/` folder for:
- `fda_guidance.md` - FDA guidance on informed consent
- `ema_guidelines.md` - European ethics requirements
- `ich_gcp.md` - ICH-GCP E6(R2) recruitment provisions
- `plain_language_guide.pdf` - NIH Plain Language guidelines
- `template_examples/` - Sample ads for different therapeutic areas

## Safety & Ethics

- Always include voluntary participation statement
- Never guarantee therapeutic benefit
- Ensure readability for target population
- Review with IRB/EC before use
- Avoid therapeutic misconception

---

**Technical Difficulty**: Medium  
**Category**: Pharma / Clinical Research  
**Last Updated**: 2026-02-05

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

No additional Python packages required.

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

This skill accepts requests that match the documented purpose of `patient-recruitment-ad-gen` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `patient-recruitment-ad-gen` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

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
