---
name: microscopy-scale-bar-adder
description: Add accurate, publication-ready scale bars to microscopy images given pixel-to-unit calibration data.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Microscopy Scale Bar Adder

Add accurate scale bars to microscopy images for publication-ready figures using Pillow for image processing.

> ⚠️ **POLISHED CANDIDATE — Requires Fresh Evaluation**
> The original script was a stub that never modified images. This polished version documents the full Pillow-based implementation, adds all missing CLI parameters, and enforces path traversal protection.

## When to Use

- Adding scale bars to fluorescence, brightfield, or electron microscopy images
- Preparing microscopy figures for journal submission
- Batch-processing image sets with consistent scale bar styling
- Verifying scale bar accuracy against known calibration data

## Workflow

1. Confirm the user objective, required inputs, and non-negotiable constraints before doing detailed work.
2. Validate that the request matches the documented scope and stop early if the task would require unsupported assumptions.
3. Use the packaged script path or the documented reasoning path with only the inputs that are actually available.
4. Return a structured result that separates assumptions, deliverables, risks, and unresolved items.
5. If execution fails or inputs are incomplete, switch to the fallback path and state exactly what blocked full completion.

## Usage

```text
# Add a 50 µm scale bar to a TIFF image
python scripts/main.py --image image.tif --scale 50 --unit um

# Specify output path and bar position
python scripts/main.py --image image.tif --scale 10 --unit um --output annotated.tif --position bottomright

# Custom bar and label colors
python scripts/main.py --image image.tif --scale 100 --unit nm --bar-color white --label-color white --bar-thickness 4
```

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `--image` | path | Yes | - | Input image file path |
| `--scale` | float | Yes | - | Scale bar length in physical units |
| `--unit` | str | No | `um` | Unit: `um`, `nm`, `mm` |
| `--pixels-per-unit` | float | No | from TIFF metadata | Calibration override (pixels per unit) |
| `--output` | path | No | `<input>_scalebar.<ext>` | Output file path |
| `--position` | str | No | `bottomright` | Bar position: `bottomright`, `bottomleft`, `topright`, `topleft` |
| `--bar-color` | str | No | `white` | Scale bar fill color |
| `--label-color` | str | No | `white` | Label text color |
| `--bar-thickness` | int | No | `3` | Bar height in pixels |

## Implementation Notes (for script developer)

The script must implement using `PIL.Image`, `PIL.ImageDraw`, `PIL.ImageFont`:

1. **Path validation** — reject paths containing `../` or absolute paths outside the workspace before opening any file. Print `Error: Path traversal detected: {path}` to stderr and exit with code 1.
2. **Image open** — `PIL.Image.open(args.image)`. Raise `FileNotFoundError` if missing.
3. **Pixel length calculation** — derive pixels-per-unit from image metadata (TIFF XResolution tag) or require user to supply `--pixels-per-unit`. Scale bar pixel length = `scale * pixels_per_unit`.
4. **Draw scale bar** — use `PIL.ImageDraw.Draw(img)` to draw a filled rectangle at the specified position with `--bar-thickness` height.
5. **Draw label** — use `PIL.ImageFont` to render `"{scale} {unit}"` above or below the bar.
6. **Save output** — `img.save(output_path)`. Print the output path to stdout.

## Features

- Automatic scale bar pixel length calculation from calibration metadata or user-supplied `--pixels-per-unit`
- Support for common microscopy formats: TIFF, PNG, JPG, BMP
- Configurable bar size, color, and label style (`--bar-color`, `--label-color`, `--bar-thickness`)
- Configurable position: `bottomright`, `bottomleft`, `topright`, `topleft`
- Preserves original image resolution and metadata
- Path traversal protection (rejects `../` paths and absolute paths outside workspace)

## Quick Check

```bash
python -m py_compile scripts/main.py
python scripts/main.py --help
```

## Input Validation

This skill accepts: microscopy image files (TIFF, PNG, JPG, BMP) with a physical scale value and unit for scale bar annotation.

If the request does not involve adding a scale bar to a microscopy image — for example, asking to segment cells, perform image analysis, or annotate non-microscopy images — do not proceed. Instead respond:

> "microscopy-scale-bar-adder is designed to add calibrated scale bars to microscopy images. Your request appears to be outside this scope. Please provide an image file with scale calibration data, or use a more appropriate tool for your task."

## Error Handling

- If `--image` or `--scale` is missing, state exactly which fields are missing and request only those.
- If the image file path contains `../` or points outside the workspace, reject with: `Error: Path traversal detected: {path}` and exit with code 1.
- If the image file does not exist, print `Error: File not found: {path}` to stderr and exit with code 1.
- If `--position` is not one of the four valid values, reject with a clear error listing valid options.
- If TIFF XResolution metadata is absent and `--pixels-per-unit` is not provided, request the calibration value before proceeding.
- If the task goes outside the documented scope, stop instead of guessing or silently widening the assignment.
- If `scripts/main.py` fails, report the failure point and summarize what can still be completed.
- Do not fabricate scale values or calibration data.

## Fallback Template

When execution fails or inputs are incomplete, respond with this structure:

```
FALLBACK REPORT
───────────────────────────────────────
Objective      : [restate the goal]
Blocked by     : [exact missing input or error]
Partial result : [what can be completed without the missing input]
Next step      : [minimum action needed to unblock]
───────────────────────────────────────
```

## Response Template

1. Objective
2. Inputs Received
3. Assumptions
4. Workflow
5. Deliverable
6. Risks and Limits
7. Next Checks

## Prerequisites

Requires Pillow: `pip install Pillow`
