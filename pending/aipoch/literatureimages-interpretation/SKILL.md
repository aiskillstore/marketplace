---
name: literatureimages-interpretation
description: Interpret figures in academic papers and their captions when the input is a PDF-to-Markdown document with page markers and image links, producing a structured Markdown report for extracting variables, trends, and conclusions.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- You have a paper converted from PDF to Markdown (including `## Page XX` markers and image links) and need a figure-by-figure interpretation report.
- You need to extract key variables, trends, comparisons, and conclusions primarily from charts/plots rather than from the main text.
- You want to align images in a `*-images/` folder with figure numbers (e.g., Figure 1A, Figure 2) using captions and in-text citations.
- You need a standardized, UTF-8 Markdown output suitable for downstream summarization, data extraction, or knowledge base ingestion.
- You must filter out non-figure images (e.g., scanned body text blocks) and interpret only chart-like content.

## Key Features

- Parses Markdown image links and locates the corresponding `*-images/` directory (e.g., `RateSOX2.md` → `RateSOX2-images/`).
- Opens **every** image in the images folder without skipping and classifies each as chart / table / schematic / flowchart / body-text block.
- Builds an internal (non-exported) alignment list to map images to figure numbers using captions and body-text citations.
- Interprets **only chart-type** images (and other figure-like visuals when required), excluding body-text blocks.
- Produces a single structured “Image Interpretation” Markdown report per input file, saved to `outputs/`.
- Enforces evidence-based interpretation: rely only on captions, body text, and visible image content; do not speculate.

## Dependencies

- `pdf-extract` (version: not specified) — used only when the source is PDF and must be converted to Markdown first.
- Markdown template: `assets/figure_interpretation_template.md` (version: not specified)
- Quality/requirements reference: `references/guide.md` (version: not specified)

## Example Usage

### Input layout

```
skill/
  literatureimages-interpretation/
    inputs/
      RateSOX2.md
    RateSOX2-images/
      image_001.png
      image_002.png
      ...
    assets/
      figure_interpretation_template.md
    references/
      guide.md
    outputs/
```

### Run (conceptual workflow)

1. If starting from PDF, convert to Markdown first:
   ```bash
   pdf-extract RateSOX2.pdf > skill/literatureimages-interpretation/inputs/RateSOX2.md
   ```

2. Ensure the images folder exists and matches the literature name:
   - `inputs/RateSOX2.md`
   - `RateSOX2-images/`

3. Execute the interpretation process:
   - Read `inputs/RateSOX2.md` (captions + in-text citations + image links).
   - Open every image in `RateSOX2-images/` sequentially.
   - Classify images; keep only chart/figure-like items for interpretation.
   - Align images to figure numbers (e.g., Figure 1A) when possible; otherwise mark as **Unassigned**.
   - Fill `assets/figure_interpretation_template.md`.
   - Write exactly one UTF-8 Markdown output to:
     - `outputs/RateSOX2_figure_interpretation.md` (example name; keep it concise)

### Output (must be a single Markdown file)

- Location: `outputs/`
- Content: **only** the “Image Interpretation” section (do **not** include the internal image list table)
- Encoding: UTF-8

## Implementation Details

- **Input assumptions**
  - Default input is a PDF-to-Markdown file (`.md`) containing:
    - page markers like `## Page XX`
    - image links
    - captions and surrounding body text
  - If only a PDF is provided, convert it to Markdown using `pdf-extract` before interpretation.

- **Image discovery**
  - Images are typically stored in a folder named `*-images/` matching the literature filename.
  - Use Markdown image links and/or folder naming to locate the correct images.

- **Mandatory full pass over images**
  - Open **every** image in the `*-images/` folder without skipping.
  - Classify each image into one of:
    - chart/plot
    - table
    - schematic
    - flowchart
    - body text block (to be excluded from interpretation)

- **Figure attribution (alignment)**
  - Use captions and in-text citations to assign figure identifiers (e.g., Figure 2, Fig. 3B).
  - If attribution cannot be determined, label the item as **Unassigned**.
  - Maintain an internal alignment list for processing only; **do not** generate or export any image list file.

- **Interpretation scope and constraints**
  - Interpret **only** chart-type (and other figure-like) images that require analysis; exclude body-text blocks.
  - Interpretations must be grounded in:
    - visible content in the image (axes, legends, labels, values, trends)
    - caption text
    - relevant body text citations
  - Do not infer beyond the evidence; if information is missing, write **“Not specified”**.

- **Output rules**
  - Use `assets/figure_interpretation_template.md` as the structure.
  - Output exactly **one** Markdown file per input document.
  - Save to `outputs/` with a concise filename (avoid redundant phrases).
  - Do not include the internal image list table; output only the final “Image Interpretation” content.
  - Ensure UTF-8 encoding to prevent character corruption.

- **Quality checks**
  - Follow detailed requirements and checkpoints in `references/guide.md`.