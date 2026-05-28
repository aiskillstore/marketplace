---
name: image-ocr
description: Extract text from images with Tesseract OCR; use it when you need to recognize text from PNG/JPEG/TIFF/BMP images, select a language model, or run OCR via natural-language requests (e.g., "Interpret the image at C:\path\image.png").
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- You need to extract text from an image file (PNG/JPEG/TIFF/BMP) for downstream processing or review.
- You want to run OCR with a specific Tesseract language model (e.g., `eng`, `chi_sim`).
- You prefer providing a natural-language request that contains an image path (e.g., "Interpret the image at ...") instead of manually setting `image_path`.
- You need a quick local OCR verification workflow from the command line.
- You want a simple JSON-configured OCR runner that can be integrated into scripts or automation.

## Key Features

- OCR text extraction using Tesseract via `pytesseract`.
- Supports common image formats: PNG, JPEG, TIFF, BMP (via Pillow).
- Multi-language OCR through the `lang` configuration option.
- Natural-language request parsing to automatically locate the image path.
- Config-driven execution through `scripts/ocr_config.json`.

## Dependencies

- Python packages:
  - `pytesseract` (version not specified)
  - `Pillow` (version not specified)
- System dependency:
  - Tesseract OCR (installed separately; ensure `tesseract_cmd` points to the executable)

## Example Usage

1. Install dependencies (example):

```bash
pip install pytesseract Pillow
```

2. Install Tesseract OCR (system-level) and ensure it is accessible.  
   - If it is not on `PATH`, set `tesseract_cmd` to the full executable path in the config.

3. Create or edit `scripts/ocr_config.json`:

### Option A: Direct image path

```json
{
  "image_path": "C:\\Users\\xuw\\Desktop\\test_image.png",
  "request": "",
  "lang": "chi_sim",
  "tesseract_cmd": "tesseract"
}
```

### Option B: Natural-language request (image path embedded)

```json
{
  "request": "Interpret the image at C:\\Users\\xuw\\Desktop\\test_image.png",
  "lang": "chi_sim",
  "tesseract_cmd": "tesseract"
}
```

4. Run:

```bash
python scripts/image_ocr.py
```

## Implementation Details

- **Configuration inputs**
  - `image_path`: Explicit path to the image file to OCR.
  - `request`: Natural-language instruction that includes an image path; when provided, the script extracts the path from this text and uses it as the OCR target.
  - `lang`: Tesseract language model code (e.g., `eng`, `chi_sim`). This is passed to Tesseract to control recognition language.
  - `tesseract_cmd`: The Tesseract executable name or full path; used to configure `pytesseract` to locate Tesseract.

- **Execution flow (high level)**
  1. Load `scripts/ocr_config.json`.
  2. Determine the target image path:
     - Use `image_path` if present and non-empty; otherwise parse the path from `request`.
  3. Load the image via Pillow.
  4. Run OCR via `pytesseract` with the configured `lang`.
  5. Output the extracted text (script-defined output behavior).

- **Language model requirement**
  - The selected `lang` must be installed in your local Tesseract language data; otherwise OCR may fail or fall back depending on your Tesseract setup.

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

## Deterministic Output Rules

- Use the same section order for every supported request of this skill.
- Keep output field names stable and do not rename documented keys across examples.
- If a value is unavailable, emit an explicit placeholder instead of omitting the field.

## Output Contract

- Return a structured deliverable that is directly usable without reformatting.
- If a file is produced, prefer a deterministic output name such as `image_ocr_result.md` unless the skill documentation defines a better convention.
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

## Completion Checklist

- Confirm all required inputs were present and valid.
- Confirm the supported execution path completed without unresolved errors.
- Confirm the final deliverable matches the documented format exactly.
- Confirm assumptions, limitations, and warnings are surfaced explicitly.

## Quick Validation

Run this minimal verification path before full execution when possible:

```bash
python scripts/image_ocr.py --help
```

Expected output format:

```text
Result file: image_ocr_result.md
Validation summary: PASS/FAIL with brief notes
Assumptions: explicit list if any
```

## Scope Reminder

- Core purpose: Extract text from images with Tesseract OCR; use it when you need to recognize text from PNG/JPEG/TIFF/BMP images, select a language model, or run OCR via natural-language requests (e.g., "Interpret the image at C:\path\image.png").
