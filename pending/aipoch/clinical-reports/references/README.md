# Clinical Reports Skill

## Overview

A comprehensive skill set for writing clinical reports, including case reports, diagnostic reports, clinical trial reports, and patient documentation. Provides full support for templates, compliance, and validation tools.

## Included Content

### 📋 Four Major Report Types

1. **Clinical Case Reports** - CARE-compliant case reports for publication in medical journals.
2. **Diagnostic Reports** - Radiology (ACR), Pathology (CAP), and Laboratory reports.
3. **Clinical Trial Reports** - SAE reports, Clinical Study Reports (ICH-E3), and DSMB reports.
4. **Patient Documentation** - SOAP notes, History and Physical (H&P), Discharge Summaries, and Consultation notes.

### 📚 Reference Files (8 Comprehensive Guides)

- `case_report_guidelines.md` - CARE guidelines, de-identification, and journal requirements.
- `diagnostic_reports_standards.md` - ACR, CAP, and CLSI standards; structured reporting systems.
- `clinical_trial_reporting.md` - ICH-E3, CONSORT, SAE reporting, and MedDRA coding.
- `patient_documentation.md` - Standards for SOAP notes, H&P, and discharge summaries.
- `regulatory_compliance.md` - HIPAA, 21 CFR Part 11, ICH-GCP, and FDA regulations.
- `medical_terminology.md` - SNOMED-CT, LOINC, ICD-10, and CPT codes.
- `data_presentation.md` - Clinical tables, figures, and Kaplan-Meier curves.
- `peer_review_standards.md` - Peer review standards for clinical papers.

### 📄 Templates (12 Professional Templates)

- `case_report_template.md` - Structured case report following CARE guidelines.
- `soap_note_template.md` - SOAP progress note format.
- `history_physical_template.md` - Complete H&P examination template.
- `discharge_summary_template.md` - Hospital discharge documentation.
- `consult_note_template.md` - Specialist consultation format.
- `radiology_report_template.md` - Structured imaging report.
- `pathology_report_template.md` - Surgical pathology report with CAP synoptic elements.
- `lab_report_template.md` - Clinical laboratory test results.
- `clinical_trial_sae_template.md` - Serious Adverse Event reporting form.
- `clinical_trial_csr_template.md` - Clinical Study Report outline (ICH-E3).
- `quality_checklist.md` - Quality assurance checklist for all report types.
- `hipaa_compliance_checklist.md` - Privacy and de-identification verification.

### 🔧 Validation Scripts (8 Automation Tools)

- `validate_case_report.py` - Checks for CARE guideline compliance and completeness.
- `check_deidentification.py` - Scans reports for the 18 HIPAA identifiers.
- `validate_trial_report.py` - Validates ICH-E3 structure and required elements.
- `format_adverse_events.py` - Generates AE summary tables from CSV data.
- `generate_report_template.py` - Interactive template selection and generation.
- `extract_clinical_data.py` - Parses and extracts structured clinical data.
- `compliance_checker.py` - Verifies regulatory compliance requirements.
- `terminology_validator.py` - Validates medical terminology and prohibited abbreviations.

## Quick Start

### Generate Template

```bash
cd .claude/skills/clinical-reports/scripts
python generate_report_template.py

# Or specify type directly
python generate_report_template.py --type case_report --output my_case_report.md
```

### Validate Case Report

```bash
python validate_case_report.py my_case_report.md
```

### Check De-identification

```bash
python check_deidentification.py my_case_report.md
```

### Validate Clinical Trial Report

```bash
python validate_trial_report.py my_csr.md
```

## Core Features

### CARE Guideline Compliance
- Full coverage of the CARE checklist.
- De-identification validation.
- Informed consent documentation.
- Assisted timeline creation.
- Literature review integration.

### Regulatory Compliance
- **HIPAA** - Privacy protection, removal of 18 identifiers, Safe Harbor method.
- **FDA** - Compliance with 21 CFR Parts 11, 50, 56, 312.
- **ICH-GCP** - Good Clinical Practice for drug trials.
- **ALCOA-CCEA** - Data integrity principles.

### Professional Standards
- **ACR** - American College of Radiology reporting standards.
- **CAP** - College of American Pathologists synoptic reporting.
- **CLSI** - Clinical and Laboratory Standards Institute.
- **CONSORT** - Standards for reporting clinical trials.
- **ICH-E3** - Structure of clinical study reports.

### Medical Coding Systems
- **ICD-10-CM** - Diagnosis coding.
- **CPT** - Procedure coding.
- **SNOMED-CT** - Clinical medical terminology set.
- **LOINC** - Logical Observation Identifiers Names and Codes for labs.
- **MedDRA** - Medical Dictionary for Regulatory Activities.

## Common Use Cases

### 1. Publishing Clinical Case Reports

```
> Create a clinical case report for a 65-year-old patient presenting with atypical acute appendicitis.

> Check this case report for HIPAA compliance.
> Validate against CARE guidelines.
```

### 2. Writing Diagnostic Reports

```
> Generate a radiology report template for a chest CT.
> Create a pathology report for a colectomy specimen (adenocarcinoma).
> Write a laboratory report for a complete blood count (CBC).
```

### 3. Clinical Trial Documentation

```
> Write a Serious Adverse Event (SAE) report for a hospitalization due to pneumonia.
> Create a Clinical Study Report outline for a Phase 3 diabetes trial.
> Generate an adverse event summary table based on trial data.
```

### 4. Patient Clinical Records

```
> Create a SOAP note for a follow-up visit.
> Generate an H&P for a patient admitted with chest pain.
> Write a discharge summary for a heart failure hospitalization.
> Create a cardiology consultation note.
```

## Workflow Examples

### Case Report Workflow

1. **Obtain Informed Consent**: From the patient.
2. **Generate Template**: `python generate_report_template.py --type case_report`
3. **Write Report**: Follow the CARE structure.
4. **Validate Compliance**: `python validate_case_report.py case_report.md`
5. **Check De-identification**: `python check_deidentification.py case_report.md`
6. **Submit to Journal**: Include the CARE checklist.

### Clinical Trial SAE Workflow

1. **Generate SAE Template**: `python generate_report_template.py --type sae`
2. **Fill SAE Form**: Complete within 24 hours of event awareness.
3. **Assess Causality**: Use WHO-UMC or Naranjo algorithms.
4. **Validate Completeness**: `python validate_trial_report.py sae_report.md`
5. **Submit to Sponsor**: Within regulatory timelines (7 or 15 days).
6. **Notify IRB**: According to institutional policy.

## Best Practices

### Privacy & Ethics
✓ Always obtain informed consent for case reports.  
✓ Remove all 18 HIPAA identifiers before publication.  
✓ Use de-identification validation scripts.  
✓ State in the manuscript that informed consent was signed.  
✓ Assess re-identification risk for rare cases.  

### Clinical Quality
✓ Use professional medical terminology.  
✓ Follow structured reporting templates.  
✓ Include all necessary elements.  
✓ Document chronological order clearly.  
✓ Provide evidence support for diagnoses.  

### Regulatory Compliance
✓ Meet SAE reporting timelines (7 days, 15 days).  
✓ Ensure CSR follows ICH-E3 structure.  
✓ Maintain ALCOA-CCEA data integrity.  
✓ Document protocol adherence.  
✓ Use MedDRA coding for adverse events.  

### Documentation Standards
✓ Sign and date all clinical records.  
✓ Document medical necessity.  
✓ Use only standard abbreviations.  
✓ Avoid prohibited abbreviations (JCAHO "Do Not Use" list).  
✓ Maintain legibility and completeness.  

## Integration

The clinical-reports skill integrates seamlessly with:

- **scientific-writing** - For clear, professional medical writing.
- **peer-review** - For quality assessment of case reports.
- **citation-management** - For literature citations in case reports.
- **research-grants** - For clinical trial protocol development.

## Resources

### External Standards
- CARE Guidelines: https://www.care-statement.org/
- ICH-E3 Guidelines: https://database.ich.org/sites/default/files/E3_Guideline.pdf
- CONSORT Statement: http://www.consort-statement.org/
- HIPAA: https://www.hhs.gov/hipaa/
- ACR Practice Parameters: https://www.acr.org/Clinical-Resources/Practice-Parameters-and-Technical-Standards
- CAP Cancer Protocols: https://www.cap.org/protocols-and-guidelines

### Professional Organizations
- American Medical Association (AMA)
- American College of Radiology (ACR)
- College of American Pathologists (CAP)
- Clinical and Laboratory Standards Institute (CLSI)
- International Council for Harmonisation (ICH)

## Support

For questions or issues regarding the clinical-reports skill:
1. Check the comprehensive reference files.
2. Refer to template examples.
3. Run validation scripts to identify issues.
4. Consult SKILL.md for detailed guidance.

## License

Part of the Claude Scientific Writer project. Please see the main LICENSE file.