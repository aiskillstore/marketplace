---
name: multi-panel-figure-assembler
description: Assemble 6 sub-figures (A–F) into a high-resolution composite figure with consistent labels, padding, and publication-ready DPI.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# Multi-Panel Figure Assembler

Assemble 6 sub-figures (A–F) into a high-resolution composite figure with consistent styling, labels, and publication-ready output.

## Input Validation

This skill accepts: exactly 6 image files (panels A–F) in supported formats, plus an output path, for assembly into a composite figure.

If the request does not involve assembling exactly 6 image panels into a composite figure — for example, asking to generate plots from data, edit image content, or assemble a different number of panels — do not proceed. Instead respond:

> "multi-panel-figure-assembler is designed to assemble exactly 6 sub-figures (A–F) into a composite image. Your request appears to be outside this scope. Please provide 6 image files and an output path, or use a more appropriate tool for your task. For plot generation from data, consider matplotlib, seaborn, or R ggplot2."

Do not attempt any data processing or partial analysis before emitting this refusal. Validate scope first — this is the absolute first action before any other processing.

## When to Use

- Combining individual plot panels into a single composite figure for publication
- Standardizing label fonts, padding, and DPI across a figure set
- Producing 2×3 or 3×2 grid layouts from existing image files
- Automating figure assembly to ensure reproducibility

**Note:** This skill is fixed to exactly 6 panels (A–F labeling convention). For 4-panel (2×2) or 9-panel (3×3) layouts, a future `--panels` parameter may be added.

## Workflow

1. **Validate input** — confirm scope and that exactly 6 panels are provided before any processing. Do not generate any output before this check.
2. Confirm the user objective, required inputs, and non-negotiable constraints.
3. Use the packaged script path or the documented reasoning path with only the inputs that are actually available.
4. Return a structured result that separates assumptions, deliverables, risks, and unresolved items.
5. If execution fails or inputs are incomplete, switch to the fallback path and state exactly what blocked full completion.

## Usage

```text
# Basic 2×3 layout
python scripts/main.py --input A.png B.png C.png D.png E.png F.png --output figure.png

# 3×2 layout at 600 DPI
python scripts/main.py --input A.png B.png C.png D.png E.png F.png --output figure.png --layout 3x2 --dpi 600

# Custom label styling
python scripts/main.py --input A.png B.png C.png D.png E.png F.png --output figure.png \
  --label-size 32 --label-position topright --padding 20 --border 4
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--input` / `-i` | 6 paths | Required | Input image paths for panels A–F |
| `--output` / `-o` | path | Required | Output composite file path |
| `--layout` / `-l` | enum | `2x3` | Grid layout: `2x3` or `3x2` |
| `--dpi` / `-d` | int | `300` | Output DPI |
| `--label-font` | str | `Arial` | Font family for panel labels |
| `--label-size` | int | `24` | Font size for panel labels |
| `--label-position` | str | `topleft` | Label position: `topleft`, `topright`, `bottomleft`, `bottomright` |
| `--padding` / `-p` | int | `10` | Padding between panels (pixels) |
| `--border` / `-b` | int | `2` | Border width around each panel (pixels) |
| `--bg-color` | str | `white` | Background color (white/black/hex) |
| `--label-color` | str | `black` | Label text color |

## Supported Formats

- Input: PNG, JPG, JPEG, BMP, TIFF, GIF
- Output: PNG (recommended), JPG, TIFF

## Quick Check

```bash
python -m py_compile scripts/main.py
python scripts/main.py --help
python -c "import PIL; print('Pillow OK')"
```

## Error Handling

- If fewer or more than 6 input images are provided, state the count mismatch and stop.
- If any input file path contains `../` or points outside the workspace, reject with a path traversal warning.
- If the task goes outside the documented scope, stop instead of guessing or silently widening the assignment.
- If `scripts/main.py` fails (e.g., returncode=2 from missing required args), report the exact error and provide the correct command syntax.
- If PIL/Pillow is not installed, print: `pip install Pillow numpy` and exit with a non-zero code.
- Do not fabricate files, citations, or execution outcomes.

## Fallback Template

When execution fails or inputs are incomplete, respond with this structure:

```
FALLBACK REPORT
───────────────────────────────────────
Objective      : [restate the goal]
Blocked by     : [exact missing input or error — e.g., only 4 of 6 panels provided]
Partial result : [what can be completed — e.g., layout plan, parameter defaults]
Assumptions    : [layout, DPI, label style assumed]
Constraints    : [format requirements, DPI minimum]
Risks          : [aspect ratio mismatch, font availability]
Unresolved     : [what still needs user input]
Next step      : [minimum action needed to unblock]
───────────────────────────────────────
```

## Response Template

Use the following fixed structure for non-trivial requests:

1. Objective
2. Inputs Received
3. Assumptions
4. Workflow
5. Deliverable
6. Risks and Limits
7. Next Checks

If the request is simple, compress the structure but keep assumptions and limits explicit when they affect correctness.

## Notes

- Input images are automatically resized to match the largest dimension while maintaining aspect ratio
- For best results, use input images with similar aspect ratios
- Label fonts require the font to be available on the system; Arial falls back to DejaVu Sans if unavailable
- PNG output preserves transparency if any input images have alpha channels

## Prerequisites

```text
pip install Pillow numpy
```
