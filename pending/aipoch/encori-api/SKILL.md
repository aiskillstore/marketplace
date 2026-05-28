---
name: encori-api
description: "Access ENCORI (StarBase) database for miRNA-target, RNA-RNA, and other regulatory data. Invoke when user asks to search ENCORI or retrieve regulatory interactions."
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- Use this skill when the request matches its documented task boundary.
- Use it when the user can provide the required inputs and expects a structured deliverable.
- Prefer this skill for repeatable, checklist-driven execution rather than open-ended brainstorming.

## Key Features

- Scope-focused workflow aligned to: "Access ENCORI (StarBase) database for miRNA-target, RNA-RNA, and other regulatory data. Invoke when user asks to search ENCORI or retrieve regulatory interactions.".
- Packaged executable path(s): `scripts/encori_client.py` plus 1 additional script(s).
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- Python 3
- `requests` library

## Example Usage

See `## Usage` above for related details.

```bash
cd "20260316/scientific-skills/Evidence Insight/encori-api"
python -m py_compile scripts/encori_client.py
python scripts/encori_client.py --help
```

Example run plan:
1. Confirm the user input, output path, and any required config values.
2. Edit the in-file `CONFIG` block or documented parameters if the script uses fixed settings.
3. Run `python scripts/encori_client.py` with the validated inputs.
4. Review the generated output and return the final artifact with any assumptions called out.

## Implementation Details

- Execution model: validate the request, choose the packaged workflow, and produce a bounded deliverable.
- Input controls: confirm the source files, scope limits, output format, and acceptance criteria before running any script.
- Primary implementation surface: `scripts/encori_client.py` with additional helper scripts under `scripts/`.
- Parameters to clarify first: input path, output path, scope filters, thresholds, and any domain-specific constraints.
- Output discipline: keep results reproducible, identify assumptions explicitly, and avoid undocumented side effects.

## Validation Shortcut

Run this minimal command first to verify the supported execution path:

```bash
python scripts/validate_skill.py --help
```

# ENCORI API Skill

This skill allows you to query the ENCORI (The Encyclopedia of RNA Interactomes) database programmatically. It supports multiple endpoints for retrieving data on miRNA-target interactions, RNA-RNA networks, RBP-target interactions, and more.

## Capabilities

The skill provides access to the following data modules via the `encori_client.py` script:

1.  **miRNATarget**: miRNA-target interactions supported by Ago CLIP-seq.
2.  **degradomeRNA**: miRNA cleavage events supported by degradome-seq.
3.  **RNARNA**: ncRNA-RNA interaction networks.
4.  **ceRNA**: ceRNA networks.
5.  **RBPTarget**: RBP-RNA interactions supported by CLIP-seq.
6.  **RBPDisease**: RBP-gene interactions and somatic mutations in diseases.
7.  **RBPMotifScan**: Binding motifs of RBPs.
8.  **bindingSite**: Binding sites of CLIP-seq.

## Usage

Run the python script `.trae/skills/encori-api/scripts/encori_client.py` with the appropriate subcommand and arguments.

### Common Arguments
Most endpoints support:
- `--assembly`: Genome version (default: hg38)
- `--geneType`: Main gene type (default: mRNA)
- `--cellType`: Cell type (default: all)

### Examples

#### 1. miRNA-Target
Get all miRNA data for PDCD4 in HeLa cells:
```bash
python .trae/skills/encori-api/scripts/encori_client.py miRNATarget --target PDCD4 --cellType HeLa
```

#### 2. Degradome-RNA
Get all miRNA cleavage data for TP53:
```bash
python .trae/skills/encori-api/scripts/encori_client.py degradomeRNA --target TP53
```

#### 3. RNA-RNA
Get interaction networks of TP53-mRNA:
```bash
python .trae/skills/encori-api/scripts/encori_client.py RNARNA --RNA TP53
```

#### 4. CeRNA
Get ceRNAs for a specific miRNA family:
```bash
python .trae/skills/encori-api/scripts/encori_client.py ceRNA --family "miR-10-5p"
```

#### 5. RBP-Target
Get data of all RBPs that bind to TP53 in HeLa cells:
```bash
python .trae/skills/encori-api/scripts/encori_client.py RBPTarget --target TP53 --cellType HeLa
```

#### 6. RBP-Disease
Get RBP-MYC interactions in breast carcinoma:
```bash
python .trae/skills/encori-api/scripts/encori_client.py RBPDisease --tissue breast --disease carcinoma --target MYC
```

#### 7. RBP Motif Scan
Retrieve binding motifs containing 'UGCAUG':
```bash
python .trae/skills/encori-api/scripts/encori_client.py RBPMotifScan --motif UGCAUG
```

#### 8. Binding Sites
Retrieve binding sites for a specific dataset ID:
```bash
python .trae/skills/encori-api/scripts/encori_client.py bindingSite --datasetID SBDH2131
```

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
- If a file is produced, prefer a deterministic output name such as `encori_api_result.md` unless the skill documentation defines a better convention.
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

```bash
python scripts/encori_client.py --help
```

Expected output format:

```text
Result file: encori_api_result.md
Validation summary: PASS/FAIL with brief notes
Assumptions: explicit list if any
```

## Deterministic Output Rules

- Use the same section order for every supported request of this skill.
- Keep output field names stable and do not rename documented keys across examples.
- If a value is unavailable, emit an explicit placeholder instead of omitting the field.

## Completion Checklist

- Confirm all required inputs were present and valid.
- Confirm the supported execution path completed without unresolved errors.
- Confirm the final deliverable matches the documented format exactly.
- Confirm assumptions, limitations, and warnings are surfaced explicitly.
