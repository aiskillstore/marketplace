---
name: labarchive-integration
description: Converts LabArchives notebook data, entry metadata, and authorized ELN exports into manuscript-ready academic writing outputs such as Methods sections, data-availability statements, reproducibility appendices, experiment timelines, and submission support notes. Optional bundled scripts can be used to collect or validate source notebook data before writing.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# LabArchives Integration

This skill is an **Academic Writing** workflow built around LabArchives evidence. Its goal is not just API access, but turning authorized ELN material into manuscript-ready writing deliverables.

## When to Use

- The user has LabArchives notebook content and needs a **Methods** draft grounded in recorded procedures.
- The user needs a **data availability statement**, **reproducibility appendix**, **experiment timeline**, or **submission support summary** based on ELN records.
- The user wants to gather authorized notebook data first, then convert it into academic writing outputs.
- The user needs a deterministic evidence-to-writing workflow instead of freeform summarization.

## When Not to Use

- The user asks for unauthorized access to notebooks or other users' data.
- The user wants clinical recommendations, diagnosis, or treatment language.
- The user asks you to fabricate notebook records, timestamps, protocol details, or compliance statements that are not present in the source.
- The user has no authorized export, no notebook metadata, and no textual record to ground the writing output.

## Primary Writing Outputs

This skill supports these deliverables:

- **Methods Draft**
  Based on notebook entries, protocols, instrument logs, and sample-processing notes
- **Data Availability Statement**
  Based on notebook identifiers, repository links, export status, and sharing constraints
- **Reproducibility Appendix**
  Based on protocol versions, software environments, parameter logs, and file provenance
- **Experiment Timeline Summary**
  Based on dated entries, milestones, and decision points
- **Submission Support Note**
  Based on notebook scope, audit trail, and documentation completeness

## Authorized Input Sources

Use one or more of:

- exported notebook text or JSON
- manually pasted LabArchives entry content
- protocol summaries
- experiment metadata tables
- authorized backup output from bundled scripts

Optional collection step:

- `scripts/setup_config.py`
- `scripts/notebook_operations.py`
- `scripts/entry_operations.py`

## Writing Output Contract

### Output A: Methods Draft

Must include:

- study material or sample context
- experimental workflow in chronological order
- instrument / assay / software mentions if present in source
- quality-control or versioning note if present in source
- no invented parameter values

### Output B: Data Availability Statement

Must include:

- what data are available
- where they are stored or how they can be requested
- any access restrictions
- relationship to LabArchives or downstream repository

### Output C: Reproducibility Appendix

Must include:

- protocol version references
- software or pipeline identifiers if present
- provenance or notebook traceability note
- missing-record warning if the audit trail is incomplete

### Output D: Experiment Timeline Summary

Must include:

- dated milestone order
- major protocol transitions
- validation / repeat / deviation points if documented

## Workflow

### 1. Validate authorization and source sufficiency

Confirm:

- the requester has authorized access to the notebook data
- the source contains enough grounded information for the requested writing output

If not, stop and use the refusal template in `## Refusal and Recovery Contract`.

### 2. Choose the acquisition path

Use direct source text if already available. Prefer this path for speed.

If data must be collected first, use one of the bundled scripts:

```bash
python scripts/setup_config.py
python scripts/notebook_operations.py --help
python scripts/entry_operations.py --help
```

Use `--dry-run` where available before live execution.

### 3. Normalize notebook evidence

Extract only writing-relevant elements:

- dates
- protocol names and versions
- sample or cohort descriptors
- software / pipeline names
- QC notes
- repository / export details
- compliance or sharing constraints

### 4. Draft the requested academic writing output

Keep the prose:

- factual
- audit-trail grounded
- publication appropriate
- free of operational noise that does not belong in the manuscript deliverable

### 5. Run the final writing safety pass

Check that:

- every claim maps back to source evidence
- missing evidence is labeled as missing
- no compliance statement is invented
- no unauthorized identifiers are surfaced

## Refusal and Recovery Contract

If the workflow cannot proceed safely, respond with:

```text
Cannot generate the requested LabArchives-based writing output yet.
Reason: <missing authorization / insufficient export / incomplete metadata / unsupported request>
Minimum next step:
- <step 1>
- <step 2>
```

Use this contract for:

- missing notebook authorization
- no usable export or pasted content
- requests to infer missing protocol details
- requests to expose restricted data

## Script Usage Notes

The bundled scripts are **supporting collection utilities**, not the final output themselves.

- `setup_config.py`: create or validate configuration
- `notebook_operations.py`: list notebooks, plan backups, or perform authorized exports
- `entry_operations.py`: inspect entry-level content or upload artifacts when explicitly needed

If a script path fails:

- report the exact command
- report the exact failure
- continue with direct writing only if enough grounded notebook text is already available

## Academic Writing Style Rules

- write in neutral, methods-oriented academic prose
- prefer verifiable chronology over interpretive narrative
- do not overclaim documentation quality if the notebook trail is partial
- clearly distinguish `documented`, `not documented`, and `not provided`

## Recommended Templates

Use `assets/writing_outputs_template.md` as the default skeleton for the four main writing deliverables.

## Deterministic Rules

- keep output headings stable
- do not expose raw credentials, tokens, or private notebook identifiers unless the user explicitly needs authorized internal formatting
- if a timestamp or version is missing, say it is not documented
- treat data availability and reproducibility statements as formal manuscript components, not casual notes

## Completion Checklist

- Authorization boundary checked
- Source sufficiency checked
- Requested writing deliverable selected explicitly
- All statements grounded in notebook evidence
- Missing evidence labeled rather than invented
