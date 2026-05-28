---
name: iso-certification
description: "A toolkit for preparing ISO 13485:2016 certification documentation for medical device QMS. Use when you need to perform a documentation gap analysis, draft or update a Quality Manual, create required procedures/work instructions, build Medical Device Files (MDF), interpret ISO 13485 clauses, or identify missing documents for certification (often triggered by ISO 13485, QMS certification, FDA QMSR, EU MDR, or quality system documentation requests)."
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

Use this skill in any of the following situations:

1. **Starting ISO 13485 implementation** and you need a structured documentation set (Quality Manual, procedures, records, templates).
2. **Assessing an existing QMS** and you want a **gap analysis** against ISO 13485:2016 requirements and mandatory documentation.
3. **Preparing for a certification audit** and you need readiness checks, evidence mapping, and prioritized remediation actions.
4. **Creating or updating specific SOPs** (e.g., CAPA, complaint handling, internal audit, document/record control) using consistent templates.
5. **Transitioning or harmonizing with regulations** (e.g., **FDA QMSR** alignment, **EU MDR** documentation expectations) and you need to reorganize device documentation (e.g., MDF).

## Key Features

- **Automated documentation gap analysis** via `scripts/gap_analyzer.py` to detect missing/covered QMS documents.
- **Clause-by-clause ISO 13485 reference guidance** using `references/iso-13485-requirements.md`.
- **Mandatory documentation mapping** (procedures and required documents) using `references/mandatory-documents.md`.
- **Comprehensive audit-style checklist** for detailed assessments using `references/gap-analysis-checklist.md`.
- **Template-based document generation** for Quality Manual and key procedures under `assets/templates/`.
- **Medical Device File (MDF) guidance** aligned to ISO 13485 Clause 4.2.3 and FDA QMSR harmonization concepts.

## Dependencies

- **Python**: 3.10+ (recommended)
- **pip**: 23+ (recommended)

> Note: This repository references a script (`scripts/gap_analyzer.py`). If it introduces additional third-party packages, install them per the repository’s `requirements.txt` (if present). If no `requirements.txt` exists, the script is expected to run on the Python standard library.

## Example Usage

### 1) Run an automated gap analysis (end-to-end)

```bash
# 1) (Optional) Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows PowerShell

# 2) Run the gap analyzer against your existing QMS document folder
python scripts/gap_analyzer.py \
  --docs-dir ./my-qms-docs \
  --output ./gap-report.json

# 3) Review the output
cat ./gap-report.json
```

### 2) Use the references and templates to draft core documents

A typical workflow after generating `gap-report.json`:

1. Read ISO clause guidance:
   - `references/iso-13485-requirements.md`
2. Confirm mandatory documents and applicability:
   - `references/mandatory-documents.md`
3. Draft/update the Quality Manual:
   - `assets/templates/quality-manual-template.md`
   - Guidance: `references/quality-manual-guide.md`
4. Draft priority procedures (examples):
   - `assets/templates/procedures/document-control-procedure-template.md`
   - `assets/templates/procedures/CAPA-procedure-template.md`
5. Perform a detailed checklist-based assessment:
   - `references/gap-analysis-checklist.md`

## Implementation Details

### 1) Gap analysis logic (practical model)

The gap analysis workflow is designed to answer:

- **Existence**: Do required documents/procedures appear to exist in the provided document set?
- **Coverage**: Which ISO 13485 clauses and mandatory procedures are addressed?
- **Prioritization**: What should be created/updated first to reduce audit risk?

**Typical inputs**
- A directory containing QMS documentation (e.g., `.md`, `.txt`, `.docx`, `.pdf`), including manuals, SOPs, work instructions, and forms.

**Typical outputs**
- A machine-readable report (e.g., `gap-report.json`) that can be summarized into:
  - Present vs. missing procedures/documents
  - Clause coverage estimates
  - A prioritized action list (Critical/High/Medium/Low)

### 2) ISO 13485 documentation structure (recommended hierarchy)

- **Level 1**: Quality Manual (policy-level mapping to Clauses 4–8)
- **Level 2**: Procedures / SOPs (who/what/when; stable process requirements)
- **Level 3**: Work Instructions (how-to steps; task-level detail)
- **Level 4**: Forms / Records (evidence of implementation)

This skill emphasizes writing procedures that define **what must be done** and **who is responsible**, while keeping detailed step-by-step instructions in work instructions.

### 3) Quality Manual requirements (key checkpoints)

When drafting with `assets/templates/quality-manual-template.md` and `references/quality-manual-guide.md`, ensure:

- The manual includes required content aligned to **ISO 13485 Clause 4.2.2**.
- The **scope** is explicit and any **exclusions** are justified (only where permitted and not impacting safety/effectiveness).
- The manual references the supporting procedures and describes **process interactions** (e.g., a process map).
- Approval/signature expectations are met (top management ownership of policy-level commitments).

### 4) Medical Device File (MDF) content model (Clause 4.2.3)

For each device type/family, the MDF should consolidate or reference:

1. Device description and intended use
2. Labeling and IFU specifications
3. Product and manufacturing specifications
4. Purchasing/manufacturing/servicing procedures (as applicable)
5. Monitoring and measurement procedures
6. Installation requirements (if applicable)
7. Risk management documentation
8. Verification and validation evidence
9. Design and development documentation (if applicable)

This structure supports ISO 13485 expectations and aligns with FDA QMSR’s direction toward consolidated device documentation.

### 5) Procedure customization parameters (what must be decided)

When generating SOPs from templates (e.g., CAPA, document control), the organization must define:

- **Roles and responsibilities** (role-based, not person-based)
- **Triggers and inputs** (complaints, audit findings, nonconformities, feedback)
- **Timeframes** (triage, investigation, closure, effectiveness checks)
- **Decision criteria** (severity, risk, escalation thresholds)
- **Records and retention** (what evidence is kept and for how long)
- **Interfaces** (how CAPA links to complaints, audits, risk management, change control)

### 6) Mandatory procedures list (reference-driven)

Use `references/mandatory-documents.md` as the source of truth for:
- Which procedures are required vs. conditional (“if applicable”)
- How to justify non-applicability
- What evidence/records each procedure should produce

For detailed clause interpretation, use `references/iso-13485-requirements.md`.
