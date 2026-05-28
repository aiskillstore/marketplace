---
name: image-processing
description: Batch-convert and compress local images with Pillow; use when you need an offline, scriptable pipeline for directory-based processing.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- You need to batch convert a folder of images into a single target format (e.g., WebP) for distribution.
- You want to reduce file sizes via compression while keeping processing fully offline (no network calls).
- You need a repeatable, scriptable pipeline for CI/local automation (e.g., preparing assets for a website/app).
- You want to preserve the source directory structure in the output directory during conversion.
- You need best-effort batch processing where individual file errors are reported but do not stop the entire run.

## Key Features

- Batch conversion of common image formats using Pillow.
- Configurable output format (default: `webp`) and quality (default: `80`).
- Optional recursive traversal of subdirectories while preserving folder structure in output.
- Overwrite policy control to prevent accidental replacement of existing outputs.
- Summary reporting (counts, errors) printed to standard output.
- Local-only operation: reads from a specified source directory and writes to a specified output directory.

## Dependencies

- Python `>= 3.9`
- Pillow (installed via requirements file):
  - `pip install -r scripts/requirements.txt`

## Example Usage

> For additional examples, see `references/examples.md`.

```bash
# 1) Install dependencies
pip install -r scripts/requirements.txt

# 2) Convert all images under <src> to WebP with quality 80, writing to <out>
python scripts/convert_images.py \
  --source-dir "<src>" \
  --output-dir "<out>" \
  --format webp \
  --quality 80

# 3) (Optional) Typical variants (flags may vary by implementation)
# - Enable recursion
# python scripts/convert_images.py --source-dir "<src>" --output-dir "<out>" --format webp --quality 80 --recursive
#
# - Allow overwriting existing outputs
# python scripts/convert_images.py --source-dir "<src>" --output-dir "<out>" --format webp --quality 80 --overwrite
```

## Implementation Details

- **Processing engine**: All conversions are performed via **Pillow** (no external binaries).
- **I/O boundaries**:
  - Reads only from `--source-dir`.
  - Writes only to `--output-dir`.
  - No network access; no external APIs; no credentials required.
- **Batch behavior**:
  - The script continues processing remaining files even if some files fail.
  - Errors are collected and summarized at the end.
- **Directory structure**:
  - The relative path under `--source-dir` is preserved under `--output-dir`.
- **Format-specific save rules**:
  - **JPG/JPEG**: converted/saved in **RGB**; uses the provided `quality`; enables **progressive** output.
  - **PNG**: uses a **compression level derived from the `quality`** parameter (higher quality typically implies lower compression and vice versa, depending on the mapping used by the script).
  - **WebP**: uses the provided `quality` and sets `method=6` for encoding.
- **Default parameters**:
  - Output format: `webp`
  - Quality: `80`

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
- If a file is produced, prefer a deterministic output name such as `image_processing_result.md` unless the skill documentation defines a better convention.
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
python scripts/convert_images.py --help
```

Expected output format:

```text
Result file: image_processing_result.md
Validation summary: PASS/FAIL with brief notes
Assumptions: explicit list if any
```
