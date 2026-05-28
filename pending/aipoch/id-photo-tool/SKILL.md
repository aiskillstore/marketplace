---
name: id-photo-tool
description: Replace an ID photo background color (blue/white/red) and/or add a configurable text watermark when you need compliant ID-photo variants from local JPG/PNG files.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use
- You need to convert an ID photo background to a required solid color (blue/white/red) for official submissions.
- You need to add a visible “for application only” style watermark to prevent misuse of shared ID photos.
- You need to batch-generate multiple variants while keeping the original image unchanged (explicit output path).
- You need an offline, local-only tool (no network access) for processing sensitive personal images.

## Key Features
- Background color replacement for ID photos:
  - Supported target colors: `blue`, `white`, `red`
  - Detects the dominant background color using edge pixels and replaces it using color-distance matching
- Text watermark overlay:
  - Supported positions: top-left, top-right, bottom-left, bottom-right, center
  - Configurable opacity, font size, and font color
- Input/output constraints:
  - Supports `JPG` and `PNG` only
  - Output keeps the same format as the input
  - Does not overwrite the original file (output path must be provided)
- Local processing only:
  - Reads only from user-provided input paths and writes only to user-provided output paths

## Dependencies
- Python 3.x
- pillow (PIL) — version not pinned
- numpy — version not pinned

Install:
```bash
python -m pip install pillow numpy
```

## Example Usage
Background color replacement (JPG):
```bash
python scripts/id_photo_tool.py change-bg \
  --input input.jpg \
  --output output.jpg \
  --color blue
```

Background color replacement (PNG):
```bash
python scripts/id_photo_tool.py change-bg \
  --input input.png \
  --output output.png \
  --color white
```

Add a text watermark:
```bash
python scripts/id_photo_tool.py add-watermark \
  --input input.jpg \
  --output watermarked.jpg \
  --text "For application use only"
```

## Implementation Details
### Background Color Replacement
- **Background sampling**: The tool estimates the original background color by sampling pixels along the image edges (where background is most likely present).
- **Color-distance based replacement**: Pixels close to the estimated background color (by color distance) are treated as background and replaced with the selected target color.
- **Supported target colors**:
  - `blue`
  - `white`
  - `red`

### Text Watermark
- **Placement**: One of five positions is supported: top-left, top-right, bottom-left, bottom-right, center.
- **Rendering parameters**:
  - Opacity controls watermark transparency.
  - Font size controls text scale.
  - Font color controls text color.
- **Output behavior**: The watermark is composited onto the image and saved to the specified output path without modifying the original input file.

### Security / Compliance Notes
- No network access is used; all processing is performed locally.
- The script only accesses file paths explicitly provided via CLI arguments.
- The tool requires an explicit output path and does not overwrite the original file by default.