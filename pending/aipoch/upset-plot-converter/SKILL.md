---
name: upset-plot-converter
description: Convert complex Venn diagrams with more than 4 sets to clearer Upset.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Upset Plot Converter

Convert complex Venn diagrams (more than 4 sets) to clearer Upset Plots.

## When to Use

- Use this skill when the task is to Convert complex Venn diagrams with more than 4 sets to clearer Upset.
- Use this skill for data analysis tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## Key Features

- Scope-focused workflow aligned to: Convert complex Venn diagrams with more than 4 sets to clearer Upset.
- Packaged executable path(s): `scripts/main.py`.
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

See `## Prerequisites` above for related details.

- `Python`: `3.10+`. Repository baseline for current packaged skills.
- `matplotlib`: `unspecified`. Declared in `requirements.txt`.
- `numpy`: `unspecified`. Declared in `requirements.txt`.

## Example Usage

See `## Usage` above for related details.

```bash
cd "20260318/scientific-skills/Data Analytics/upset-plot-converter"
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
python scripts/main.py
```

## Workflow

1. Confirm the user objective, required inputs, and non-negotiable constraints before doing detailed work.
2. Validate that the request matches the documented scope and stop early if the task would require unsupported assumptions.
3. Use the packaged script path or the documented reasoning path with only the inputs that are actually available.
4. Return a structured result that separates assumptions, deliverables, risks, and unresolved items.
5. If execution fails or inputs are incomplete, switch to the fallback path and state exactly what blocked full completion.

## Usage

```python
from skills.upset_plot_converter.scripts.main import convert_venn_to_upset

# From set data
sets = {
    'A': {1, 2, 3, 4, 5},
    'B': {4, 5, 6, 7, 8},
    'C': {3, 5, 7, 9, 10},
    'D': {2, 4, 6, 8, 10},
    'E': {1, 3, 5, 7, 9}
}
convert_venn_to_upset(sets, output_path="upset_plot.png")

# From list data
from skills.upset_plot_converter.scripts.main import upset_from_lists
set_names = ['Genes A', 'Genes B', 'Genes C', 'Genes D', 'Genes E']
lists = [
    ['gene1', 'gene2', 'gene3'],
    ['gene2', 'gene4', 'gene5'],
    ['gene3', 'gene5', 'gene6'],
    ['gene7', 'gene8', 'gene9'],
    ['gene1', 'gene10', 'gene11']
]
upset_from_lists(set_names, lists, output_path="gene_upset.png", title="Gene Intersections")
```

## Input

- **sets**: Dictionary of set names to sets/lists of elements, OR
- **set_names**: List of set names
- **lists**: List of lists (each containing elements)
- **output_path**: Path to save the output figure
- **title**: Optional title for the plot
- **min_subset_size**: Minimum subset size to display (default: 1)
- **max_intersections**: Maximum number of intersections to show (default: 30)

## Output

PNG file of the Upset Plot visualization.

## Notes

- When Venn diagrams exceed 4 sets, they become difficult to read
- Upset Plots provide a clearer alternative for visualizing set intersections
- The x-axis shows set intersections as dot patterns
- Bar heights represent the size of each intersection
- Automatically sorts intersections by size for better readability

## Requirements

- matplotlib
- numpy
- pandas

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

This skill accepts requests that match the documented purpose of `upset-plot-converter` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `upset-plot-converter` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

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
