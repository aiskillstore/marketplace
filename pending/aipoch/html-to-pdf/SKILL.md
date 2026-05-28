---
name: html-to-pdf
description: Convert HTML files or URLs to high-fidelity PDFs using Puppeteer; auto-detects or forces RTL for Hebrew/Arabic when RTL content is present.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## Validation Shortcut

Run this minimal command first to verify the supported execution path:

```bash
python scripts/validate_skill.py --help
```

## When to Use

- Export a web page (URL) to a PDF with Chrome-accurate rendering (CSS Grid/Flexbox, backgrounds, web fonts).
- Convert a local HTML report/invoice into a print-ready PDF (A4/Letter) with predictable margins and scaling.
- Generate single-page PDFs that must fit *exactly* on one page (posters, certificates, one-page invoices).
- Produce RTL documents (Hebrew/Arabic) where direction must be correct and fonts must render reliably.
- Render dynamic HTML that requires JavaScript execution before printing (charts, client-side templates).

## Key Features

- **Chrome-quality rendering** via Puppeteer (headless Chromium/Chrome/Edge).
- **Input flexibility**: local HTML file, URL, or stdin (`-`) piping.
- **RTL support**: automatic RTL detection with an option to **force RTL** (`--rtl`).
- **Print controls**: format, landscape, margins (uniform or per-side), scale, background printing.
- **Header/Footer templates**: inject HTML header/footer.
- **Stability for fonts/resources**: waits for network idle and `document.fonts.ready`, plus configurable extra wait.

## Dependencies

- **Node.js**: >= 16 (recommended)
- **npm**: >= 8
- **puppeteer**: installed via `npm install` (Chromium bundled by default)
- Optional browser executable (if not using bundled Chromium):
  - **Google Chrome** or **Microsoft Edge** (path provided via `--executable-path` or `PUPPETEER_EXECUTABLE_PATH`)

## Example Usage

### 1) Install

```bash
cd d:/skills/html-to-pdf
npm install
```

### 2) Run (local HTML → PDF)

```bash
node assets/html-to-pdf.js input.html output.pdf
```

### 3) Run (URL → PDF)

```bash
node assets/html-to-pdf.js https://example.com page.pdf
```

### 4) Force RTL (Hebrew/Arabic)

```bash
node assets/html-to-pdf.js hebrew.html hebrew.pdf --rtl
```

### 5) Pipe HTML via stdin

```bash
echo "<h1>Example Title</h1>" | node assets/html-to-pdf.js - output.pdf --rtl
```

### 6) Use a specific browser executable (optional)

```bash
node assets/html-to-pdf.js https://example.com page.pdf --executable-path="C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
```

Or via environment variable:

```bash
set PUPPETEER_EXECUTABLE_PATH=C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe
node assets/html-to-pdf.js https://example.com page.pdf
```

### 7) A complete, runnable single-page A4 example (recommended pattern)

Create `single-page.html`:

```html
<!doctype html>
<html lang="he" dir="rtl">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <link href="https://fonts.googleapis.com/css2?family=Heebo:wght@400;700&display=swap" rel="stylesheet">
  <style>
    @page { size: A4; margin: 0; }

    /* Keep the page box exact; avoid backgrounds here to prevent extra pages */
    html, body {
      width: 210mm;
      height: 297mm;
      margin: 0;
      padding: 0;
      overflow: hidden;
    }

    /* Put backgrounds on a full-size container instead */
    .container {
      width: 100%;
      height: 100%;
      box-sizing: border-box;
      padding: 20mm;

      font-family: "Heebo", sans-serif;
      direction: rtl;
      text-align: right;

      background: #f5f5f5;
      overflow-wrap: break-word;
      word-wrap: break-word;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>כותרת לדוגמה</h1>
    <p>תוכן לדוגמה שמודפס כעמוד יחיד.</p>
  </div>
</body>
</html>
```

Generate the PDF:

```bash
node assets/html-to-pdf.js single-page.html single-page.pdf --format=A4 --margin=0 --wait=1000
```

## Implementation Details

### Rendering approach

- Uses **Puppeteer** to load either:
  - a local HTML file, or
  - a remote URL, or
  - HTML from **stdin** (`-`)
- Wait strategy (to reduce missing fonts/assets):
  - waits for `networkidle0` (resources finished loading),
  - waits for `document.fonts.ready`,
  - then waits an additional `--wait=<ms>` (default `1000`) for late JS/font rendering.

### RTL handling

- Default behavior: **auto-detect** RTL content (e.g., Hebrew/Arabic) and apply RTL direction.
- Override: `--rtl` forces RTL regardless of detection.

### Page-fit rule (single-page PDFs)

To avoid unexpected blank pages, ensure the content fits exactly within the page box:

- Do **not** set backgrounds on `html` or `body` (common cause of extra pages).
- Put backgrounds on a full-height container (`.container`) instead.
- Use `overflow: hidden` on `html, body` for strict single-page output.
- If overflow persists, adjust:
  - `--scale` (e.g., `0.9`, `0.8`)
  - `--margin` (e.g., `10mm`, `0`)

### CLI parameters

| Parameter | Description | Default |
|---|---|---|
| `--format=<format>` | Page size: A4, Letter, Legal, A3, A5 | A4 |
| `--landscape` | Landscape orientation | false |
| `--margin=<value>` | Uniform margin (e.g., `20mm`, `1in`) | 20mm |
| `--margin-top=<value>` | Top margin | 20mm |
| `--margin-right=<value>` | Right margin | 20mm |
| `--margin-bottom=<value>` | Bottom margin | 20mm |
| `--margin-left=<value>` | Left margin | 20mm |
| `--scale=<number>` | Scale factor (0.1-2.0) | 1 |
| `--background` | Print background graphics | true |
| `--no-background` | Disable background printing | - |
| `--header=<html>` | Header HTML template | - |
| `--footer=<html>` | Footer HTML template | - |
| `--wait=<ms>` | Extra wait time for fonts/JS | 1000 |
| `--rtl` | Force RTL direction | Auto-detect |

### Quality settings

- Uses Chrome print styles (`@page`) and supports print CSS.
- Sets `deviceScaleFactor` to **2** to improve output clarity.

### Verification workflow (recommended)

After each generation, visually verify the PDF:

- No extra blank pages (vertical overflow).
- No clipped text (horizontal overflow).
- If issues occur, iterate up to 5 attempts:
  1. default
  2. reduce `--scale`
  3. reduce `--margin`
  4. reduce both further
  5. fix HTML/CSS (wrap long words, ensure container sizing)

If it still fails after 5 attempts, the HTML layout must be corrected (e.g., reduce fixed heights, fix oversized elements, ensure wrapping).

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
- If a file is produced, prefer a deterministic output name such as `html_to_pdf_result.md` unless the skill documentation defines a better convention.
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

```text
No local script validation step is required for this skill.
```

Expected output format:

```text
Result file: html_to_pdf_result.md
Validation summary: PASS/FAIL with brief notes
Assumptions: explicit list if any
```

## Deterministic Output Rules

- Use the same section order for every supported request of this skill.
- Keep output field names stable and do not rename documented keys across examples.
- If a value is unavailable, emit an explicit placeholder instead of omitting the field.

## Completion Checklist

- Confirm all required inputs were present and valid.
- Confirm the supported execution path completed without unresolved errors.
- Confirm the final deliverable matches the documented format exactly.
- Confirm assumptions, limitations, and warnings are surfaced explicitly.
