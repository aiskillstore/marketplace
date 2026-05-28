---
name: method-writing
description: Write and revise the Methods section of research papers to ensure reproducibility; use when preparing an IMRAD manuscript or responding to journal/reporting-guideline requirements (e.g., CONSORT/STROBE/PRISMA).
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

Use this skill when you need to:

1. Draft or substantially revise the **Methods** section of a scientific manuscript to make the study reproducible.
2. Align a manuscript with **IMRAD** conventions and ensure the Methods content matches what is reported in Results.
3. Ensure compliance with **study-type reporting guidelines** (e.g., CONSORT for RCTs, STROBE for observational studies, PRISMA for systematic reviews/meta-analyses).
4. Prepare a submission for a **specific journal** with strict formatting, word limits, and required declarations (ethics, funding, data availability).
5. Address **reviewer comments** about missing methodological detail, unclear procedures, or insufficient statistical reporting.

## Key Features

- **Reproducible Methods prose**: Produces fluent paragraph-based Methods text suitable for final manuscripts (not bullet lists).
- **IMRAD-compatible structure**: Organizes Methods content into standard subsections (design, setting, participants/samples, procedures, outcomes, statistics, ethics).
- **Guideline-driven completeness**: Maps content to reporting checklists (CONSORT/STROBE/PRISMA and others) to reduce omissions.
- **Experimental and procedural specificity**: Captures materials, equipment, calibration, conditions, controls, replicates, and step-by-step procedures.
- **Statistical transparency**: Specifies assumptions, tests, effect sizes, confidence intervals, multiple-comparison control, missing-data and outlier handling.
- **Data management and integrity**: Documents collection formats, preprocessing, storage, access control, anonymization, and compliance constraints.
- **Field-specific terminology**: Applies discipline conventions (biomedical, molecular biology, chemistry/pharma, neuroscience) and consistent nomenclature.
- **Journal tailoring**: Adapts wording and required declarations to match author guidelines and editorial expectations.

Reference materials (optional, if present in the repository):
- `references/imrad_structure.md`
- `references/reporting_guidelines.md`
- `references/writing_principles.md`

## Dependencies

- None (documentation/writing skill; no runtime dependencies).

## Example Usage

### Input (what you provide)

**Study context**
- Design: randomized, double-blind, placebo-controlled trial  
- Setting: single academic hospital, 2023-2024  
- Participants: adults 18-65 with condition X; key inclusion/exclusion criteria  
- Intervention: Drug A 50 mg daily vs placebo for 8 weeks  
- Outcomes: primary outcome Y at week 8; secondary outcomes Z1-Z3  
- Randomization/blinding: block randomization (block size 4), allocation concealment via central web system  
- Sample size: power 0.8, alpha 0.05, expected effect size d=0.5  
- Statistics: intention-to-treat; mixed-effects model; Holm correction; report Cohen's d and 95% CI  
- Ethics: IRB approval ID; written informed consent  
- Data handling: de-identified dataset; stored on encrypted server; access limited to study team

**Target constraints**
- Journal: requires CONSORT adherence and structured Methods subsections  
- Style: full paragraphs only; define abbreviations at first use

### Output (a runnable Methods section draft)

#### Methods

**Study design and oversight.** We conducted a randomized, double-blind, placebo-controlled, parallel-group trial to evaluate the efficacy of Drug A compared with placebo over 8 weeks. The protocol was approved by the Institutional Review Board of [Institution] (approval ID: [ID]). All participants provided written informed consent before any study procedures were performed.

**Participants.** Adults aged 18-65 years with a diagnosis of condition X were recruited from [clinic/service] between [month year] and [month year]. Key inclusion criteria were [criterion 1], [criterion 2], and [criterion 3]. Key exclusion criteria were [criterion 1], [criterion 2], and current use of [medication/class] within [time window]. Eligibility was confirmed by [assessment method], and baseline characteristics were collected at enrollment.

**Randomization and blinding.** Participants were assigned in a 1:1 ratio to Drug A or placebo using computer-generated block randomization with a fixed block size of 4. Allocation concealment was implemented through a centralized web-based randomization system accessible only to the study pharmacist. Participants, investigators, outcome assessors, and statisticians remained blinded to group assignment until database lock.

**Intervention and procedures.** Participants in the intervention group received Drug A 50 mg orally once daily for 8 weeks; the control group received a matching placebo on the same schedule. Study medication was dispensed at baseline and week 4, and adherence was assessed by pill count and participant diary. Concomitant treatments were permitted only if stable for at least [duration] before enrollment and unchanged during follow-up. Safety was monitored at each visit by adverse-event assessment and [laboratory/clinical measures], with severity graded using [standard].

**Outcomes.** The primary outcome was outcome Y measured at week 8 using [instrument/scale], where higher scores indicate [direction]. Secondary outcomes included Z1-Z3 assessed at baseline, week 4, and week 8 using [methods]. All outcomes were collected by trained assessors following a standardized operating procedure.

**Sample size.** The planned sample size was calculated to provide 80% power to detect a standardized mean difference of 0.5 in the primary outcome between groups at a two-sided alpha level of 0.05. Allowing for an anticipated attrition rate of [x%], we aimed to enroll [N] participants.

**Statistical analysis.** Analyses followed the intention-to-treat principle and included all randomized participants with available outcome data. The primary analysis used a linear mixed-effects model with fixed effects for treatment group, time, and their interaction, and a random intercept for participant to account for repeated measures. Model assumptions were assessed by inspection of residual plots and formal normality testing (Shapiro-Wilk). For secondary outcomes, p values were adjusted for multiple comparisons using the Holm method. Effect sizes are reported as Cohen's d with 95% confidence intervals (CIs) for continuous outcomes and as odds ratios (ORs) with 95% CIs for binary outcomes, as applicable. Missing data were handled using [complete-case analysis / multiple imputation], with sensitivity analyses performed under [assumption]. All tests were two-sided with a significance threshold of 0.05 after adjustment where applicable. Analyses were performed using [software, version].

**Data management and availability.** Data were recorded in [system], exported to [format], and stored on an encrypted institutional server with access restricted to authorized study personnel. Identifiers were removed and replaced with study codes prior to analysis. A data dictionary and analysis code are available at [repository/link] subject to [conditions], in accordance with [GDPR/HIPAA/other] requirements.

## Implementation Details

### Methods-section algorithm (IMRAD-aligned)

1. **Identify study type and structure**: Choose the appropriate Methods template (e.g., RCT, cohort, case-control, systematic review). For IMRAD guidance, consult `references/imrad_structure.md` if available.
2. **Map to reporting checklist**: Select the relevant guideline (CONSORT/STROBE/PRISMA, etc.) and ensure each required methodological element is explicitly reported. See `references/reporting_guidelines.md` if available.
3. **Write in manuscript-ready prose**: Produce full paragraphs with logical transitions; avoid bullet lists in the final Methods text.
4. **Specify reproducibility-critical details**:
   - **Participants/samples**: source, eligibility, handling, and attrition rules.
   - **Materials and equipment**: manufacturer/model, key settings, calibration frequency/standards.
   - **Procedures**: step order, timing, temperature, pH, incubation, centrifugation, sterile conditions, and acceptance criteria.
   - **Controls and replication**: positive/negative controls; technical vs biological replicates; batch handling.
5. **Statistical reporting parameters**:
   - Assumption checks (e.g., Shapiro-Wilk; Levene/Bartlett where relevant).
   - Primary/secondary models and covariates; effect sizes (Cohen's d, η², OR, RR) and **95%/99% CIs**.
   - Multiple-comparison control (Bonferroni, Holm, FDR).
   - Missing-data strategy (complete case vs imputation) and outlier policy (IQR/Grubbs) defined *a priori*.
   - Sample-size justification (power, alpha, expected effect size) and any interim analysis rules.
6. **Bias control**: Describe randomization, allocation concealment, and blinding (single/double/triple) with operational details.
7. **Ethics and safety**: Include approvals, consent, biosafety level/PPE, chemical safety references (MSDS), and waste disposal where applicable.
8. **Data integrity and security**: Document naming conventions, preprocessing (normalization/filtering), backups, access permissions, anonymization/encryption, and regulatory compliance.
9. **Field-specific terminology rules**:
   - Genetics: italicize gene symbols (e.g., *TP53*) and use protein symbols in roman type (p53); follow species conventions.
   - Chemistry/pharma: use IUPAC where needed; report concentrations with correct units (mM, μM, % w/v).
   - Biomedical: prefer standardized disease nomenclature and SI units when required by the journal.
10. **Journal adaptation**: Apply author instructions for section headings, word limits, declarations, and citation/formatting. For style guidance, consult `references/writing_principles.md` if available.

## When Not to Use

- Do not use this skill when the required source data, identifiers, files, or credentials are missing.
- Do not use this skill when the user asks for fabricated results, unsupported claims, or out-of-scope conclusions.
- Do not use this skill when a simpler direct answer is more appropriate than the documented workflow.

## Required Inputs

- A clearly specified task goal aligned with the documented scope.
- All required files, identifiers, parameters, or environment variables before execution.
- Any domain constraints, formatting requirements, and expected output destination if applicable.

## Recommended Workflow

1. Validate the request against the skill boundary and confirm all required inputs are present.
2. Select the documented execution path and prefer the simplest supported command or procedure.
3. Produce the expected output using the documented file format, schema, or narrative structure.
4. Run a final validation pass for completeness, consistency, and safety before returning the result.

## Output Contract

- Return a structured deliverable that is directly usable without reformatting.
- If a file is produced, prefer a deterministic output name such as `method_writing_result.md` unless the skill documentation defines a better convention.
- Include a short validation summary describing what was checked, what assumptions were made, and any remaining limitations.

## Validation and Safety Rules

- Validate required inputs before execution and stop early when mandatory fields or files are missing.
- Do not fabricate measurements, references, findings, or conclusions that are not supported by the provided source material.
- Emit a clear warning when credentials, privacy constraints, safety boundaries, or unsupported requests affect the result.
- Keep the output safe, reproducible, and within the documented scope at all times.

## Failure Handling

- If validation fails, explain the exact missing field, file, or parameter and show the minimum fix required.
- If an external dependency or script fails, surface the command path, likely cause, and the next recovery step.
- If partial output is returned, label it clearly and identify which checks could not be completed.

## Quick Validation

Run this minimal verification path before full execution when possible:

```text
No local script validation step is required for this skill.
```

Expected output format:

```text
Result file: method_writing_result.md
Validation summary: PASS/FAIL with brief notes
Assumptions: explicit list if any
```
