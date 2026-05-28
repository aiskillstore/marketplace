---
name: motif-logo-generator
description: Generate publication-quality sequence logos for DNA or protein motifs.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Motif Logo Generator

Generate sequence logos for DNA or protein motifs to visualize conserved positions.

## When to Use

- Use this skill when the task is to Generate publication-quality sequence logos for DNA or protein motifs.
- Use this skill for data analysis tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## Key Features

- Scope-focused workflow aligned to: Generate publication-quality sequence logos for DNA or protein motifs.
- Packaged executable path(s): `scripts/main.py`.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

See `## Prerequisites` above for related details.

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `numpy`: `unspecified`. Declared in `requirements.txt`.

## Example Usage

See `## Usage` above for related details.

```bash
cd "20260318/scientific-skills/Data Analytics/motif-logo-generator"
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

## Installation

```text
cd /Users/z04030865/.openclaw/workspace/skills/motif-logo-generator
pip install -r requirements.txt
```

Dependencies:
- `logomaker` - Generate publication-quality sequence logos
- `pandas` - Data manipulation for sequence alignment
- `numpy` - Numerical operations
- `matplotlib` - Visualization backend

## Quick Start

```text

# Generate logo from FASTA file
python scripts/main.py --input sequences.fasta --output logo.png --type dna

# Generate logo from raw sequences
python scripts/main.py --sequences "ACGT\nACCT\nAGGT" --output logo.png --type dna

# Protein sequences with custom styling
python scripts/main.py --input proteins.fasta --output logo.pdf --type protein --title "Conserved Domain"
```

## Usage

### Python API

```python
from motif_logo_generator import generate_logo

# From file
logo = generate_logo(
    input_file="sequences.fasta",
    seq_type="dna",
    output_path="logo.png",
    title="My Motif"
)

# From sequences list
sequences = [
    "ACGTAGCT",
    "ACGTAGCT",
    "ACCTAGCT",
    "ACGTAGTT"
]
logo = generate_logo(
    sequences=sequences,
    seq_type="dna",
    output_path="logo.png"
)
```

### Command Line

```text
python scripts/main.py [OPTIONS]

Required:
  --input PATH       Input FASTA file (or use --sequences)
  --sequences TEXT   Raw sequences separated by newline (or use --input)
  --output PATH      Output file path (.png, .pdf, .svg)

Optional:
  --type {dna,protein}   Sequence type (default: dna)
  --title TEXT           Logo title
  --width INT            Figure width in inches (default: 10)
  --height INT           Figure height in inches (default: 3)
  --colorscheme TEXT     Color scheme (default: classic)
                         DNA: classic, base_pairing
                         Protein: chemistry, hydrophobicity, classic
```

## Output

Generates a sequence logo showing:
- Letter height = information content (conservation)
- Letter stack = frequency at each position
- Y-axis: bits (information content) for DNA, or relative frequency for protein

## Example

Input (FASTA):
```
>seq1
ACGT
>seq2
ACGT
>seq3
ACCT
>seq4
AGGT
```

Output: Logo with position 2 showing C/G variability and other positions conserved.

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

```text

# Python dependencies
pip install -r requirements.txt
```

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

This skill accepts requests that match the documented purpose of `motif-logo-generator` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `motif-logo-generator` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

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
