---
name: openclaw-medical-skills
description: "Codex adaptation of the OpenClaw Medical Skills library. Use for biomedical, clinical, healthcare AI, genomics, bioinformatics, drug discovery, pharmacovigilance, clinical trials, medical imaging, public health, medical device, regulatory, scientific data analysis, lab automation, and medical research workflows; also use when the user mentions OpenClaw Medical Skills, medical skill library, or any named capability preserved in the OpenClaw capability index."
---

# OpenClaw Medical Skills for Codex

## Purpose

Use this skill as a Codex-native router and execution guide for the OpenClaw Medical Skills capability library. Preserve the original capability set: do not rename, remove, merge, narrow, or reinterpret a listed OpenClaw capability. Adapt only the execution layer from OpenClaw/NanoClaw assumptions to Codex tools, local files, installed skills, web access, Python/R, MCP connectors, and user-provided data.

The canonical capability inventory is `references/capability-index.md`. The complete source text is preserved in `references/source-openclaw-medical-skills.md` for provenance. Treat OpenClaw/NanoClaw installation instructions in the source as historical context; this folder is the Codex skill.

## Safety Boundary

Use clinical and biomedical outputs for education, research, drafting, triage support, or decision support only. Do not present the output as a definitive diagnosis, prescription, treatment order, device approval, regulatory clearance, or substitute for a qualified clinician, pharmacist, genetic counsellor, institutional reviewer, or regulatory professional.

For emergencies, self-harm risk, severe acute symptoms, poisoning, overdose, stroke/MI signs, anaphylaxis, sepsis concern, suicidal intent, or threats to others, tell the user to contact local emergency services immediately; in the United States, mention 911 for emergencies and 988 for suicide or mental health crisis support when relevant. Keep crisis responses short, practical, and supportive.

For patient-specific medical advice, ask for missing critical context when needed, state uncertainty, identify red flags, recommend professional evaluation, and separate evidence from interpretation. Do not invent patient data, lab values, guideline recommendations, regulatory status, trial availability, or database results.

## Reference Navigation

Before executing a substantive task, locate the relevant OpenClaw capability:

1. If the user names a skill, search the exact slug in `references/capability-index.md`.
2. If the user describes a task, search category terms and candidate tools in `references/capability-index.md`.
3. Load only the relevant section or rows unless the task requires broad inventory review.
4. Use `references/source-openclaw-medical-skills.md` only when provenance, original wording, acknowledgements, or full README context matters.

Useful search patterns:

```bash
rg -n "clinical|trial|drug|variant|single-cell|regulatory|imaging|FHIR|PubMed|oncology" references/capability-index.md
rg -n "\\[tooluniverse-drug-drug-interaction\\]|drug-interaction" references/capability-index.md
rg -n "^##|^###|^####|\\| \\[" references/capability-index.md
```

## Codex Execution Workflow

1. Classify the request by risk and domain: direct patient care, clinical research, literature review, drug/variant interpretation, bioinformatics pipeline, data analysis, regulatory writing, document generation, or tool discovery.
2. Identify the matching OpenClaw capability from the reference index. If several apply, choose one primary capability and name secondary capabilities that will inform the work.
3. Translate the capability into Codex execution:
   - Use installed Codex skills and connectors when they directly fit.
   - Use local files, Python/R, shell tools, spreadsheets, document tools, and browser/web verification as appropriate.
   - Use official or primary sources for current medical, regulatory, label, guideline, trial, or database facts.
   - If an OpenClaw-specific MCP/API/database is unavailable in this Codex session, state the limitation, then use the best available primary source or ask for credentials/files only when needed.
4. Produce auditable outputs: include assumptions, input provenance, methods, version/date of sources when available, evidence tables for research tasks, and reproducible commands or scripts for analyses.
5. Validate work before completion: check generated files, rerun analyses where feasible, verify cited identifiers, and confirm that medical safety caveats match the task risk.

## Output Standards By Task

Clinical or patient-facing summaries:
- Use plain language first, with medical terms explained.
- Include urgent red flags and when to seek care.
- Avoid definitive diagnosis or treatment instructions unless explicitly framed as clinician-reviewed source information.
- Encourage professional review for medication changes, pregnancy, paediatrics, renal/hepatic disease, complex comorbidity, or abnormal critical values.

Literature review and evidence synthesis:
- Report search strategy, databases, date searched, inclusion/exclusion criteria, and evidence limitations.
- Prefer PubMed/PMC, DOI, guideline bodies, trial registries, FDA/EMA labels, and peer-reviewed sources.
- Distinguish guidelines, randomized trials, observational evidence, preprints, mechanistic studies, and expert opinion.

Drug research, DDI, pharmacovigilance, and pharmacogenomics:
- Capture drug name, formulation, dose, route, indication, patient factors, and co-medications when patient-specific.
- Provide mechanism, severity, evidence source, monitoring, alternatives, and escalation criteria.
- Verify labels, adverse-event databases, guideline sources, and pharmacogenomic annotations when current facts matter.

Genomics, variants, oncology, rare disease, and PRS:
- Record genome build, transcript, nomenclature, assay type, sample type, zygosity/VAF, population frequency, and database versions when available.
- Use ACMG/AMP, AMP/ASCO/CAP, ClinVar, gnomAD, COSMIC, OMIM, Orphanet, HPO, or relevant primary databases as source-appropriate.
- Treat classifications as decision support requiring qualified genetics or molecular pathology review.

Clinical trials and cohort matching:
- Include NCT IDs, recruiting status, phase, eligibility criteria, geography, intervention, biomarker requirements, and last-updated dates.
- Do not imply enrolment eligibility without site confirmation and clinician review.

Bioinformatics and omics workflows:
- Inspect input formats and metadata before analysis.
- Record tool choices, parameters, genome build/reference, software versions where available, QC metrics, and generated outputs.
- Prefer reproducible scripts/notebooks and avoid irreversible edits to source data.

Medical imaging, pathology, and multimodal AI:
- Treat image interpretation as research or drafting support unless a qualified professional provides the diagnosis.
- State modality, body site, protocol, image limitations, and whether source images were available.
- Do not fabricate findings that are not visible or provided.

Medical device, software, regulatory, and quality systems:
- Identify jurisdiction, product type, intended use, risk class, lifecycle phase, and applicable standards.
- Use FDA, EMA, EU MDR/IVDR, IEC 62304, ISO 14971, IEC 62366, ISO 13485, ICH, GxP, or related primary standards as appropriate.
- Frame outputs as drafts/checklists requiring regulatory and quality review.

Scientific data analysis, statistics, visualization, and simulation:
- Define the estimand or scientific question before analysis.
- Check data quality, missingness, units, batch effects, multiplicity, model assumptions, and uncertainty.
- Save user-facing outputs in the requested format and include enough code or method detail to reproduce the result.

## Privacy And Data Handling

Minimize protected health information. When possible, de-identify names, exact dates, addresses, identifiers, accession numbers tied to individuals, and free-text notes before using them in examples or deliverables. Keep analysis local unless the user explicitly asks for an external service and the privacy implications are acceptable.

For clinical documents, mark generated text as a draft, preserve source provenance, and avoid adding facts absent from the provided record.
