---
name: smiles-de-salter
description: Analyze data with `smiles-de-salter` using a reproducible workflow, explicit validation, and structured outputs for review-ready interpretation.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# SMILES De-salter

ID: 176

Batch process chemical structure strings, removing salt ion portions and retaining only the active core.

## When to Use

- Use this skill when the task needs Batch process chemical SMILES strings to remove salt ions and retain.
- Use this skill for data analysis tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## Key Features

- Scope-focused workflow aligned to: Analyze data with `smiles-de-salter` using a reproducible workflow, explicit validation, and structured outputs for review-ready interpretation.
- Packaged executable path(s): `scripts/main.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- Python >= 3.8
- rdkit >= 2022.03.1

## Example Usage

See `## Usage` above for related details.

```bash
cd "20260318/scientific-skills/Data Analytics/smiles-de-salter"
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
python scripts/main.py --input "Audit validation sample with explicit symptoms, history, assessment, and next-step plan."
```

## Workflow

1. Confirm the user objective, required inputs, and non-negotiable constraints before doing detailed work.
2. Validate that the request matches the documented scope and stop early if the task would require unsupported assumptions.
3. Use the packaged script path or the documented reasoning path with only the inputs that are actually available.
4. Return a structured result that separates assumptions, deliverables, risks, and unresolved items.
5. If execution fails or inputs are incomplete, switch to the fallback path and state exactly what blocked full completion.

## Function Description

This Skill is used to process chemical SMILES strings, automatically identifying and removing counterions, retaining only the active pharmaceutical ingredient (API).

### Salt Ion Identification Rules

- Identify multiple components through `.` separator
- Salt ions are usually smaller ions (such as Na⁺, Cl⁻, K⁺, Br⁻, etc.)
- Retain the component with the most atoms as the core
- Support common inorganic salts and organic acid salts

### Supported Salt Types

| Type | Examples |
|------|------|
| Inorganic salts | NaCl, KCl, HCl, H₂SO₄ |
| Organic acid salts | Citrate, Tartrate, Maleate |
| Quaternary ammonium salts | Various quaternary ammonium compounds |

## Usage

### Command Line

```text
python -m py_compile scripts/main.py

# Example invocation: python scripts/main.py -i input.csv -o output.csv -c smiles_column
```

### Parameter Description

| Parameter | Short | Description | Default |
|------|------|------|--------|
| `--input` | `-i` | Input file path (CSV/TSV/SMILES) | Required |
| `--output` | `-o` | Output file path | desalted_output.csv |
| `--column` | `-c` | SMILES column name | smiles |
| `--keep-largest` | `-k` | Keep largest component (by atom count) | True |

### Single Processing Example

```text
python scripts/main.py -s "CC(C)CN1C(=O)N(C)C(=O)C2=C1N=CN2C.[Na+]"

# Output: CC(C)CN1C(=O)N(C)C(=O)C2=C1N=CN2C
```

## Input Format

### CSV/TSV Files

```csv
id,smiles,name
1,CCO.[Na+],ethanol_sodium
2,c1ccccc1.[Cl-],benzene_hcl
```

### Pure SMILES Files

One SMILES string per line:
```
CCO.[Na+]
c1ccccc1.[Cl-]
```

## Output Format

Output file contains original data and new processing result columns:

```csv
id,smiles,name,desalted_smiles,status
1,CCO.[Na+],ethanol_sodium,CCO,success
2,c1ccccc1.[Cl-],benzene_hcl,c1ccccc1,success
```

## Install Dependencies

```text
pip install rdkit pandas
```

## Processing Logic

1. **Parse SMILES**: Use RDKit to parse input string
2. **Component Splitting**: Identify multiple molecular components separated by `.`
3. **Core Identification**:
   - Default selects component with the most atoms
   - Optional: based on molecular weight, ring count, etc.
4. **Output Result**: Return clean core SMILES

## Error Handling

- If required inputs are missing, state exactly which fields are missing and request only the minimum additional information.
- If the task goes outside the documented scope, stop instead of guessing or silently widening the assignment.
- If `scripts/main.py` fails, report the failure point, summarize what still can be completed safely, and provide a manual fallback.
- Do not fabricate files, citations, data, search results, or execution outcomes.

## Examples

### Example 1: Simple Inorganic Salt

Input: `CCO.[Na+]`
Output: `CCO`

### Example 2: HCl Salt

Input: `CN1C=NC2=C1C(=O)N(C)C(=O)N2C.Cl`
Output: `CN1C=NC2=C1C(=O)N(C)C(=O)N2C`

### Example 3: Complex Organic Salt

Input: `CC(C)CN1C(=O)N(C)C(=O)C2=C1N=CN2C.C(C(=O)O)C(CC(=O)O)(C(=O)O)O`
Output: `CC(C)CN1C(=O)N(C)C(=O)C2=C1N=CN2C` (retains larger caffeine molecule)

## Notes

1. This tool assumes the core is the component with the most atoms
2. For co-crystals or multi-component drugs, manual review may be needed
3. Some hydrochloride salts may exist as `[Cl-]` or `Cl`
4. It is recommended to sample and verify results

## Author

OpenClaw Skill Hub

## Version

v1.0.0

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

## Input Validation

This skill accepts requests that match the documented purpose of `smiles-de-salter` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `smiles-de-salter` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

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

## Inputs to Collect

- Required inputs: the user goal, the primary data or source file, and the requested output format.
- Optional inputs: output directory, formatting preferences, and validation constraints.
- If a required input is unavailable, return a short clarification request before continuing.

## Output Contract

- Return a short summary, the main deliverables, and any assumptions that materially affect interpretation.
- If execution is partial, label what succeeded, what failed, and the next safe recovery step.
- Keep the final answer within the documented scope of the skill.

## Validation and Safety Rules

- Validate identifiers, file paths, and user-provided parameters before execution.
- Do not fabricate results, metrics, citations, or downstream conclusions.
- Use safe fallback behavior when dependencies, credentials, or required inputs are missing.
- Surface any execution failure with a concise diagnosis and recovery path.
