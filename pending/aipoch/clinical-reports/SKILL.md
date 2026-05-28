---
name: clinical-reports
description: Write comprehensive clinical reports (case reports, diagnostic reports, clinical trial reports, and patient documentation) when accuracy, regulatory compliance (HIPAA/FDA/ICH-GCP), and template-driven validation are required.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

Use this skill when you need to:

1. Draft a **journal-ready clinical case report** that follows **CARE** guidelines and includes consent/de-identification.
2. Produce **diagnostic reports** (radiology, pathology, laboratory) that are structured, actionable, and consistent with common standards (e.g., ACR/CAP conventions).
3. Prepare **clinical trial safety documentation**, especially **Serious Adverse Event (SAE)** narratives and submissions under regulatory timelines.
4. Write an **ICH E3–aligned Clinical Study Report (CSR)** for sponsor/regulatory submission, including appendices and traceable data presentation.
5. Create or QA **patient medical record documentation** (SOAP notes, H&P, discharge summaries) for continuity of care, billing support, and medico-legal defensibility.

## Key Features

- **Template-driven authoring** for:
  - Case reports (CARE)
  - Radiology / pathology / lab reports
  - SAE reports and CSR (ICH E3)
  - SOAP, H&P, discharge summaries
- **Compliance-first workflow**
  - HIPAA de-identification (Safe Harbor identifiers checklist)
  - FDA documentation awareness (e.g., 21 CFR Parts 11/50/56/312)
  - ICH-GCP principles (data integrity, auditability, consent, protocol adherence)
- **Validation and QA tooling**
  - Completeness checks per report type
  - De-identification scanning
  - Consistency checks across sections (dates, identifiers, outcomes)
- **Publication-quality data presentation guidance**
  - Tables/figures conventions, labeling, precision, and safety summaries
  - Trial flow diagrams and case timelines
- **Reference and asset library integration**
  - Uses supporting files under `references/` and `assets/` for standards and templates

## Dependencies

- Python **3.10+**
- (Optional, for automation scripts) Common Python tooling typically used in this repository:
  - `argparse` (stdlib)
  - `re` (stdlib)
  - `json` (stdlib)

> Note: The provided scripts and templates are referenced by path (e.g., `scripts/validate_case_report.py`). If your repository defines additional pinned packages (e.g., in `requirements.txt`), use those versions as the source of truth.

## Example Usage

Below is a complete, runnable example that generates a report skeleton, validates it, and checks de-identification. Adjust paths to match your repository layout.

### 1) Generate a template (interactive or parameterized)

```bash
python scripts/generate_report_template.py
```

If the generator supports arguments in your repo, you can typically do something like:

```bash
python scripts/generate_report_template.py --type case-report --out reports/case_report.md
```

### 2) Validate a CARE case report draft

```bash
python scripts/validate_case_report.py reports/case_report.md
```

### 3) Check HIPAA de-identification (Safe Harbor scan)

```bash
python scripts/check_deidentification.py reports/case_report.md
```

### 4) (Optional) Validate a clinical trial report structure (ICH E3)

```bash
python scripts/validate_trial_report.py reports/csr.md
```

### 5) Use a template asset directly (copy and fill)

```bash
cp assets/soap_note_template.md reports/soap_note.md
```

Recommended supporting references while writing:

- CARE and case report guidance: `references/case_report_guidelines.md`
- Diagnostic reporting standards: `references/diagnostic_reports_standards.md`
- Trial reporting (SAE/CSR, ICH E3): `references/clinical_trial_reporting.md`
- Regulatory compliance (HIPAA/FDA/ICH-GCP): `references/regulatory_compliance.md`

## Implementation Details

### 1) Report Types and Required Sections (High-Level)

**Case reports (CARE-aligned)** typically require:
- Title/keywords/abstract
- Patient information (de-identified) + consent statement
- Clinical findings + **timeline**
- Diagnostic assessment (tests + differential + rationale)
- Therapeutic interventions (dose/route/duration + rationale)
- Follow-up/outcomes (including PROs when available)
- Discussion (novelty, literature context, limitations, implications)

Reference: `references/case_report_guidelines.md`

**Radiology reports** commonly follow:
- Indication → technique → comparison → findings → impression (with recommendations)
- Prefer standardized lexicons and structured reporting where applicable (e.g., BI-RADS, LI-RADS)

Reference: `references/diagnostic_reports_standards.md`

**Pathology reports** commonly follow:
- Specimen/clinical history → gross → microscopic → diagnosis (synoptic elements for cancer) → comment
- CAP-style synoptic checklists improve completeness for oncology

Reference: `references/diagnostic_reports_standards.md`

**Laboratory reports** commonly include:
- Patient/specimen metadata → method → results (units + reference ranges) → interpretation (if applicable)
- Critical value handling requires documented notification workflow

Reference: `references/diagnostic_reports_standards.md`

**SAE reports** should capture:
- Seriousness criteria, severity, outcome
- Causality + expectedness with rationale
- Action taken, concomitant therapy, and a coherent narrative timeline
- Regulatory timelines (e.g., 7/15-day rules depending on jurisdiction and event type)

Reference: `references/clinical_trial_reporting.md`

**CSR (ICH E3)** should be:
- Traceable to protocol/SAP, transparent about deviations, and complete in safety/efficacy presentation
- Structured per ICH E3 sections with appendices (protocol, amendments, sample CRFs, listings)

Reference: `assets/clinical_trial_csr_template.md`, `references/clinical_trial_reporting.md`

### 2) HIPAA De-identification (Safe Harbor)

De-identification checks should ensure removal/modification of the **18 HIPAA identifiers**, including:
- Names, detailed geography, full dates (except year), contact info, MRNs, account numbers, device identifiers, URLs/IPs, biometrics, full-face photos, and other unique identifiers.

Operational guidance:
- Prefer relative time (“3 months prior”) or year-only when feasible.
- Avoid institution names unless essential and permitted.
- Ensure images are cropped/blurred and consented if potentially identifying.

Reference: `references/regulatory_compliance.md`

### 3) Quality Validation Logic (What the scripts should enforce)

Typical validation checks implemented by repository scripts (by intent) include:

- **Completeness**: required headings/fields exist for the chosen report type.
- **Internal consistency**: dates, subject IDs, outcomes, and interventions do not conflict across sections.
- **Terminology hygiene**: discourages unsafe abbreviations (e.g., Joint Commission “Do Not Use” list) and encourages standard nomenclatures (SNOMED CT, LOINC, ICD-10-CM, CPT) when coding is required.
- **Regulatory readiness**: presence of consent statements (when applicable), GCP/ethics statements for trials, and documentation of deviations/CAPA where relevant.

References:
- Terminology: `references/medical_terminology.md`
- Data presentation: `references/data_presentation.md`
- QA checklists: `assets/quality_checklist.md`, `assets/hipaa_compliance_checklist.md`

### 4) Recommended Assets and Scripts (Repository Paths)

**Templates (`assets/`)**
- `assets/case_report_template.md`
- `assets/radiology_report_template.md`
- `assets/pathology_report_template.md`
- `assets/lab_report_template.md`
- `assets/clinical_trial_sae_template.md`
- `assets/clinical_trial_csr_template.md`
- `assets/soap_note_template.md`
- `assets/history_physical_template.md`
- `assets/discharge_summary_template.md`

**Automation (`scripts/`)**
- `scripts/validate_case_report.py`
- `scripts/validate_trial_report.py`
- `scripts/check_deidentification.py`
- `scripts/compliance_checker.py`
- `scripts/terminology_validator.py`

Use these to standardize structure, reduce omissions, and improve compliance before submission or chart finalization.