---
name: western-blot-quantifier
description: Automatically identify Western Blot gel bands, perform densitometric analysis, and calculate normalized values relative to loading controls.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Western Blot Quantifier

Automatically identify Western Blot gel bands, perform densitometric analysis, and calculate normalized values relative to loading controls.

## When to Use

- Use this skill when the task needs Automatically identify Western Blot gel bands, perform densitometric analysis, and calculate normalized values relative to loading controls.
- Use this skill for data analysis tasks that require explicit assumptions, bounded scope, and a reproducible output format.
- Use this skill when you need a documented fallback path for missing inputs, execution errors, or partial evidence.

## Key Features

See `## Features` above for related details.

- Scope-focused workflow aligned to: Automatically identify Western Blot gel bands, perform densitometric analysis, and calculate normalized values relative to loading controls.
- Packaged executable path(s): `scripts/__init__.py` plus 1 additional script(s).
- Structured execution path designed to keep outputs consistent and reviewable.

## Dependencies

```
numpy>=1.21.0
opencv-python>=4.5.0
pandas>=1.3.0
matplotlib>=3.4.0
scipy>=1.7.0
scikit-image>=0.18.0
```

## Example Usage

See `## Usage` above for related details.

```bash
cd "20260318/scientific-skills/Data Analytics/western-blot-quantifier"
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
- Primary implementation surface: `scripts/__init__.py` with additional helper scripts under `scripts/`.
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

## Features

- **Automatic Band Detection**: Detect protein band positions in gel images
- **Densitometric Analysis**: Calculate grayscale/optical density values for each band
- **Normalization**: Normalize relative to loading control proteins (e.g., GAPDH, β-actin, Tubulin)
- **Data Export**: Output quantitative results in CSV format

## Usage

### Basic Usage

```python

# Call in Python
from skills.western_blot_quantifier.scripts.main import WesternBlotQuantifier

# Create analyzer
analyzer = WesternBlotQuantifier()

# Analyze single image
result = analyzer.analyze(
    image_path="path/to/wb_image.png",
    reference_bands=["GAPDH"],  # Loading control band names
    target_bands=["p53", "Bcl-2"],  # Target protein band names
    lane_positions=[0.2, 0.4, 0.6, 0.8]  # Lane positions (relative to image width)
)

print(result.summary())
result.save("output/quantification_results.csv")
```

### Command Line Usage

```text
python -m skills.western_blot_quantifier.scripts.main \
    --input path/to/wb_image.png \
    --reference GAPDH \
    --targets p53,Bcl-2 \
    --lanes 4 \
    --output results.csv
```

## Parameter Description

| Parameter | Description | Default |
|------|------|--------|
| `image_path` | Gel image path | Required |
| `reference_bands` | Loading control protein name list | ["GAPDH"] |
| `target_bands` | Target protein name list | [] |
| `lane_positions` | Lane position list | Auto-detect |
| `threshold` | Band detection threshold | 0.1 |
| `background_correction` | Background correction method | "rolling_ball" |

## Output Format

### CSV Output Example

```csv
Lane,Protein,Raw_Intensity,Background,Corrected_Intensity,Normalized_to_Reference
1,GAPDH,125000.5,5000.2,120000.3,1.00
1,p53,85000.2,3000.1,82000.1,0.68
1,Bcl-2,62000.8,2500.5,59500.3,0.50
2,GAPDH,118000.3,4800.2,113200.1,1.00
...
```

### Return Object

```python
{
    "raw_data": DataFrame,           # Raw optical density data
    "normalized_data": DataFrame,    # Normalized data
    "band_regions": List[Dict],      # Detected band region coordinates
    "statistics": Dict,              # Statistical analysis results
    "figures": Dict                  # Visualization chart paths
}
```

## Installation

```text
pip install -r requirements.txt
```

## Notes

1. **Image Quality**: High resolution, good contrast grayscale or black and white gel images are recommended
2. **Loading Control Selection**: Common loading controls include GAPDH, β-actin, Tubulin; selection depends on experimental conditions
3. **Background Correction**: Supports rolling_ball, median, none three background correction methods
4. **Lane Marking**: If auto-detection is inaccurate, lane positions can be manually specified

## Examples

### Example 1: Basic Analysis

```python
from skills.western_blot_quantifier.scripts.main import WesternBlotQuantifier

analyzer = WesternBlotQuantifier()

# Analyze 4-lane Western Blot results
result = analyzer.analyze(
    image_path="experiment_data/wb_gel.png",
    reference_bands=["GAPDH"],
    target_bands=["p53", "p21"],
    lane_count=4
)

# View normalized results
print(result.normalized_data)

# Save charts
result.save_figures("output/")
```

### Example 2: Batch Processing

```python
import glob

analyzer = WesternBlotQuantifier()

for image_path in glob.glob("experiments/*.png"):
    result = analyzer.analyze(
        image_path=image_path,
        reference_bands=["β-actin"],
        target_bands=["Target_Protein"],
        lane_count=6
    )
    result.save(f"output/{Path(image_path).stem}_results.csv")
```

## Algorithm Description

1. **Image Preprocessing**: Grayscale conversion → Background correction → Denoising
2. **Lane Detection**: Automatic lane boundary identification based on vertical projection analysis
3. **Band Detection**: Band localization using 1D Gaussian fitting or peak detection algorithms
4. **Optical Density Calculation**: Integrate grayscale values in band region, subtract background
5. **Normalization**: Target protein value / Loading control protein value

## Author

OpenClaw Skills

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

This skill accepts requests that match the documented purpose of `western-blot-quantifier` and include enough context to complete the workflow safely.

Do not continue the workflow when the request is out of scope, missing a critical input, or would require unsupported assumptions. Instead respond:

> `western-blot-quantifier` only handles its documented workflow. Please provide the missing required inputs or switch to a more suitable skill.

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
