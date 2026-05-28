---
name: dpi-upscaler-checker
description: Check if images meet 300 DPI printing standards, and intelligently restore blurry low-resolution images using AI super-resolution technology.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

# DPI Upscaler & Checker

Check if images meet 300 DPI printing standards, and intelligently restore blurry low-resolution images using AI super-resolution technology.

## Input Validation

This skill accepts: image files (JPG, PNG, TIFF, BMP, WebP) or folder paths for DPI checking and/or AI super-resolution upscaling.

If the user's request does not involve image DPI checking or upscaling — for example, asking to analyze text documents, process audio files, or perform general data analysis — do not proceed with the workflow. Instead respond:
> "dpi-upscaler-checker is designed to check image DPI standards and restore low-resolution images. Your request appears to be outside this scope. Please provide an image file path or folder, or use a more appropriate tool for your task."

Do not continue the workflow when the request is out of scope, missing a critical input (`--input` path), or would require unsupported assumptions. For missing inputs, state exactly which fields are missing.

## When to Use

- Check whether images meet 300 DPI printing standards
- Upscale or restore low-resolution images using AI super-resolution
- Batch-process folders of mixed-DPI images for print readiness

## Quick Check

```bash
python -m py_compile scripts/main.py
python scripts/main.py --help
python scripts/main.py --demo
python -c "import PIL; print('Pillow OK')"
python scripts/main.py check --input image.jpg --json
```

## Workflow

1. **Validate input first** — confirm the request is within scope and `--input` path is provided before any processing.
2. Confirm the user objective, required inputs, and non-negotiable constraints.
3. Use the packaged script path or the documented reasoning path with only the inputs that are actually available.
4. Return a structured result that separates assumptions, deliverables, risks, and unresolved items.
5. If execution fails or inputs are incomplete, switch to the fallback path and state exactly what blocked full completion.

## Usage

### Check Single Image DPI
```text
python scripts/main.py check --input image.jpg
python scripts/main.py check --input image.jpg --json        # JSON to stdout for agent consumption
```

### Batch Check Folder
```text
python scripts/main.py check --input ./images/ --output report.json
```

### Super-Resolution Restoration
```text
python scripts/main.py upscale --input image.jpg --output upscaled.jpg --scale 4
```

### Batch Fix Low DPI Images
```text
python scripts/main.py upscale --input ./images/ --output ./output/ --min-dpi 300 --scale 2
```

### Demo Mode (no real images required)
```text
python scripts/main.py --demo
```

## Parameters

### Check Command
| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `--input` | string | - | Yes | Input image path or folder |
| `--output` | string | stdout | No | Output report path |
| `--target-dpi` | int | 300 | No | Target DPI threshold |
| `--json` | flag | false | No | Output results as JSON to stdout |

### Upscale Command
| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `--input` | string | - | Yes | Input image path or folder |
| `--output` | string | - | Yes | Output path |
| `--scale` | int | 2 | No | Scale factor (2/3/4) |
| `--min-dpi` | int | - | No | Only process images below this DPI |
| `--denoise` | int | 0 | No | Denoise level (0-3) |
| `--face-enhance` | flag | false | No | Enable face enhancement |

## Output

### DPI Check Report (JSON)
```json
{
  "file": "image.jpg",
  "dpi": [72, 72],
  "width_px": 1920,
  "height_px": 1080,
  "print_width_cm": 67.7,
  "print_height_cm": 38.1,
  "meets_300dpi": false,
  "recommended_scale": 4.17
}
```

### Restored Image
- Saved as `<original_filename>_upscaled.<extension>`
- Preserves original EXIF information
- Sets DPI metadata to target value

## Algorithm

- DPI: `print_size_cm = (pixel_count / dpi) * 2.54`; `recommended_scale = target_dpi / avg_dpi`
- Super-resolution fallback chain: Real-ESRGAN → OpenCV DNN → PIL Lanczos
- RGBA alpha channel upscaled separately and reattached

## Known Limitations

- Super-resolution cannot create non-existent information; extremely blurry images have limited improvement
- GPU acceleration requires CUDA environment (optional)
- Batch upscale mode does not currently save a JSON summary report (only check mode saves JSON to `--output`)
- EXIF parsing uses `except (AttributeError, KeyError, TypeError, ZeroDivisionError)` — bare except replaced with specific exception types
- Output format parameters are conditioned on file extension (JPEG: `quality=95`; PNG: `compress_level=6`)
- Batch processing uses `Path.rglob`; resolve paths with `path.resolve()` before processing to avoid unexpected directory traversal via symlinks

## Fallback Behavior

If `scripts/main.py` fails or required inputs are incomplete:
1. Report the exact failure point and error message (sanitized — no internal paths).
2. State what can still be completed safely (e.g., DPI check without upscale).
3. Manual fallback: `from PIL import Image; img = Image.open('file.jpg'); print(img.info.get('dpi'))`.
4. Do not fabricate execution outcomes or file contents.

## Error Handling

- If required inputs are missing, state exactly which fields are missing and request only the minimum additional information.
- If the task goes outside the documented scope, stop instead of guessing or silently widening the assignment.
- If `scripts/main.py` fails, report the failure point, summarize what still can be completed safely, and provide a manual fallback.
- Do not fabricate files, citations, data, search results, or execution outcomes.
- Script exits with non-zero code on error in both check and upscale modes.

## Response Template

1. Objective
2. Inputs Received
3. Assumptions
4. Workflow
5. Deliverable
6. Risks and Limits
7. Next Checks

## Dependencies

- Python >= 3.8
- Pillow >= 9.0.0
- opencv-python >= 4.5.0
- numpy >= 1.21.0
- realesrgan (optional, for best results)

```text
pip install -r requirements.txt
```
