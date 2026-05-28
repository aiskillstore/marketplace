---
name: ectd-xml-compiler
description: Automatically convert uploaded drug application documents (Word/PDF) into XML skeleton structure compliant with eCTD 4.0/3.2.2 specifications.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# eCTD XML Compiler

ID: 197

Automatically convert uploaded drug application documents (Word/PDF) into XML skeleton structure compliant with eCTD 4.0/3.2.2 specifications.

## When to Use

- Use this skill when the task needs Automatically convert uploaded drug application documents (Word/PDF) into XML skeleton structure compliant with eCTD 4.0/3.2.2 specifications.
- Use this skill for academic writing tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## Key Features

- Scope-focused workflow aligned to: Automatically convert uploaded drug application documents (Word/PDF) into XML skeleton structure compliant with eCTD 4.0/3.2.2 specifications.
- Packaged executable path(s): `scripts/main.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

```
python-docx>=0.8.11    # Word document parsing
PyPDF2>=3.0.0          # PDF text extraction
lxml>=4.9.0            # XML processing
```

## Example Usage

See `## Usage` above for related details.

```bash
cd "20260318/scientific-skills/Academic Writing/ectd-xml-compiler"
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

## Overview

eCTD (electronic Common Technical Document) is the electronic Common Technical Document standard established by ICH for submitting drug registration applications to regulatory agencies such as FDA and EMA.

This tool parses uploaded drug application documents (Word/PDF) and converts them into XML skeleton structure compliant with eCTD 4.0/3.2.2 specifications.

## eCTD Structure

```
eCTD/
├── m1/  # Module 1: Administrative Information and Prescribing Information (region-specific)
│   ├── m1.xml
│   └── ...
├── m2/  # Module 2: CTD Summaries
│   ├── m2.xml
│   └── ...
├── m3/  # Module 3: Quality
│   ├── m3.xml
│   └── ...
├── m4/  # Module 4: Nonclinical Study Reports
│   ├── m4.xml
│   └── ...
├── m5/  # Module 5: Clinical Study Reports
│   ├── m5.xml
│   └── ...
├── index.xml      # Master index file
├── index-md5.txt  # MD5 checksum file
└── dtd/           # DTD files
```

## Usage

```text
python skills/ectd-xml-compiler/scripts/main.py [options] <input_files...>
```

### Arguments

| Argument | Description |
|----------|-------------|
| `input_files` | Input Word/PDF file paths (supports multiple) |

### Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--output` | `-o` | Output directory path | `./ectd-output` |
| `--module` | `-m` | Target module (m1-m5, auto) | `auto` |
| `--region` | `-r` | Target region (FDA, EMA, ICH) | `ICH` |
| `--version` | `-v` | eCTD version (3.2.2, 4.0) | `4.0` |
| `--dtd-path` | `-d` | Custom DTD path | Built-in DTD |
| `--validate` |  | Validate generated XML | `False` |

### Examples

```text

# Basic usage - auto-detect module
python skills/ectd-xml-compiler/scripts/main.py document1.docx document2.pdf

# Specify output directory and module
python skills/ectd-xml-compiler/scripts/main.py -o ./my-ectd -m m3 quality-doc.docx

# FDA submission format
python skills/ectd-xml-compiler/scripts/main.py -r FDA -v 3.2.2 *.pdf

# Validate generated XML
python skills/ectd-xml-compiler/scripts/main.py --validate submission.pdf
```

## Input Document Processing

### Supported Formats
- Microsoft Word (.docx, .doc)
- PDF (.pdf)

### Document Parsing Logic
1. **Title Recognition**: Extract heading hierarchy based on font size and style
2. **TOC Mapping**: Auto-recognize section numbers (e.g., 3.2.S.1.1)
3. **Metadata Extraction**: Extract author, date, version, and other information
4. **Content Classification**: Map to corresponding eCTD modules based on keyword matching

### Module Auto-Recognition Rules

| Keyword Pattern | Target Module |
|------------|----------|
| Administrative, Label, Package Insert | m1 |
| Summary, summary, Overview | m2 |
| Quality, quality, CMC, API, Drug Product | m3 |
| Nonclinical, Toxicology, Pharmacokinetics | m4 |
| Clinical, clinical, Study, Trial | m5 |

## Output Structure

Generated eCTD skeleton contains:

### index.xml
Master index file containing references and sequence information for all modules.

### Module XML (m1.xml - m5.xml)
XML skeleton for each module, containing:
- Document hierarchy structure (`<leaf>`, `<node>`)
- Cross-references (`<cross-reference>`)
- Attribute definitions (ID, version, operation type)

### MD5 Checksums
MD5 checksum values for each file to ensure integrity.

## Installation

```text

# Install dependencies
pip install python-docx PyPDF2 lxml
```

## Validation

Using `--validate` option can validate generated XML:
- DTD structure validation
- Required elements and attributes check
- Cross-reference integrity check

## References

- [ICH eCTD Specification v4.0](https://www.ich.org/page/ectd)
- [FDA eCTD Guidance](https://www.fda.gov/drugs/electronic-regulatory-submission-and-review/ectd-technical-conformance-guide)
- [EMA eCTD Requirements](https://www.ema.europa.eu/en/human-regulatory/marketing-authorisation/application-procedures/electronic-application-forms)

## License

MIT License

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

This skill accepts requests that match the documented purpose of `ectd-xml-compiler` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `ectd-xml-compiler` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

## References

- [references/audit-reference.md](references/audit-reference.md) - Supported scope, audit commands, and fallback boundaries

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
