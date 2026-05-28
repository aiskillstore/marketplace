---
name: phylogenetic-tree-styler
description: Analyze data with `phylogenetic-tree-styler` using a reproducible workflow, explicit validation, and structured outputs for review-ready interpretation.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Phylogenetic Tree Styler

## When to Use

- Use this skill when the task needs Beautify phylogenetic trees with taxonomy color blocks, bootstrap values.
- Use this skill for data analysis tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## Key Features

See `## Features` above for related details.

- Scope-focused workflow aligned to: Analyze data with `phylogenetic-tree-styler` using a reproducible workflow, explicit validation, and structured outputs for review-ready interpretation.
- Packaged executable path(s): `scripts/main.py`.
- Reference material available in `references/` for task-specific guidance.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

- Python 3.8+
- ete3
- matplotlib
- numpy
- pandas

Install dependencies:
```text
pip install ete3 matplotlib numpy pandas
```

## Example Usage

See `## Usage` above for related details.

```bash
cd "20260318/scientific-skills/Data Analytics/phylogenetic-tree-styler"
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

# Example invocation: python scripts/main.py --help

# Example invocation: python scripts/main.py --input "Audit validation sample with explicit symptoms, history, assessment, and next-step plan." --format json
```

## Workflow

1. Confirm the user objective, required inputs, and non-negotiable constraints before doing detailed work.
2. Validate that the request matches the documented scope and stop early if the task would require unsupported assumptions.
3. Use the packaged script path or the documented reasoning path with only the inputs that are actually available.
4. Return a structured result that separates assumptions, deliverables, risks, and unresolved items.
5. If execution fails or inputs are incomplete, switch to the fallback path and state exactly what blocked full completion.

## Features
Beautify phylogenetic trees, add taxonomy color blocks, Bootstrap values, and timelines.

## Usage

```text
python3 scripts/main.py --input <input_tree.nwk> --output <output.png> [options]
```

### Parameters

| Parameter | Description | Default |
|------|------|--------|
| `-i`, `--input` | Input Newick format phylogenetic tree file | Required |
| `-o`, `--output` | Output image file path | tree_styled.png |
| `-f`, `--format` | Output format: png, pdf, svg | png |
| `-w`, `--width` | Image width (pixels) | 1200 |
| `-h`, `--height` | Image height (pixels) | 800 |
| `--show-bootstrap` | Show Bootstrap values | False |
| `--bootstrap-threshold` | Only show Bootstrap values above this threshold | 50 |
| `--taxonomy-file` | Species taxonomy information file (CSV format: name,domain,phylum,class,order,family,genus) | None |
| `--show-timeline` | Show timeline | False |
| `--root-age` | Root node age (million years ago) | None |
| `--branch-color` | Branch color | black |
| `--leaf-color` | Leaf node label color | black |

## Examples

### Basic Beautification
```text
python3 scripts/main.py -i tree.nwk -o tree_basic.png
```

### Show Bootstrap Values
```text
python3 scripts/main.py -i tree.nwk -o tree_bootstrap.png --show-bootstrap --bootstrap-threshold 70
```

### Add Taxonomy Color Blocks
```text
python3 scripts/main.py -i tree.nwk -o tree_taxonomy.png --taxonomy-file taxonomy.csv
```

### Add Timeline
```text
python3 scripts/main.py -i tree.nwk -o tree_timeline.png --show-timeline --root-age 500
```

### Comprehensive Usage
```text
python3 scripts/main.py -i tree.nwk -o tree_full.png \
    --show-bootstrap --bootstrap-threshold 70 \
    --taxonomy-file taxonomy.csv \
    --show-timeline --root-age 500
```

## Taxonomy Information File Format

taxonomy.csv example:
```csv
name,domain,phylum,class
Species_A,Bacteria,Proteobacteria,Gammaproteobacteria
Species_B,Bacteria,Firmicutes,Bacilli
Species_C,Archaea,Euryarchaeota,Methanobacteria
```

## Input Format

Supports standard Newick format (.nwk or .newick):
```
((A:0.1,B:0.2)95:0.3,(C:0.4,D:0.5)88:0.6);
```

Bootstrap values can be placed at node label positions (like the 95, 88 above).

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

This skill accepts requests that match the documented purpose of `phylogenetic-tree-styler` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `phylogenetic-tree-styler` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

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
