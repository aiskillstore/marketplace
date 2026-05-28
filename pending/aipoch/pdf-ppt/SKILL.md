---
name: pdf-ppt
description: Create literature-report PPTX decks from PDF papers. Use when you must extract a paper’s metadata, summarize the study, interpret Results/Figures/Tables, and generate slides with 1:1 figure-to-text alignment and layout rules (triggered by requests like “PDF to PPT”, “literature report slides”, or “turn this paper into a presentation”).
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- Converting a research paper **PDF** into a **literature-report PPTX** with a standard academic slide structure (title → overview → results → conclusion).
- When the user requires **figure-by-figure interpretation** (including subpanels) and strict **1:1 mapping** between each figure/table and slide content.
- When you must work **offline-first** (no external API calls) to extract text, figures, legends, and tables from a PDF.
- When the PPT must **match a provided layout script** (positions, aspect ratios, text boxes) and keep consistent styling across the deck.
- When the output narration must be **professional Chinese**, concise, and technically accurate.

## Key Features

- Offline-first PDF parsing to extract:
  - Title, journal, publication date, section text
  - Figure images and legends grouped by figure number
  - Tables and (optionally) graphical abstract
- Full-paper summary in professional Chinese (background + key findings).
- Results interpretation aligned **per figure/subfigure**, avoiding vague references.
- PPTX generation with:
  - Fixed slide structure (Title / Overview / Figure slides / Final summary)
  - Layout constraints matching a v5-style deck (coordinates, font sizes)
  - Consistent panel-label styling and per-deck label color
  - Per-figure slide “Summary:” one-liner
- Integration guidance for PPTX editing via `D:\\SKILL\\project\\PPTX\\SKILL.md`.

## Dependencies

- Local offline parsing workflow: `references/offline-parsing.md` (version: N/A, repository-local)
- Figure/table interpretation rules: `references/figure-interpretation.md` (version: N/A, repository-local)
- PPTX creation/editing skill: `D:\\SKILL\\project\\PPTX\\SKILL.md` (version: N/A, local path)
- Optional local mapping file: `figure_titles_zh.txt` (version: N/A, user/project-provided)

## Example Usage

### Input (user request)

> Please convert this paper PDF into a literature-report PPT.  
> Requirements: interpret each figure, keep figure-to-text alignment, and follow the v5 layout rules.

### Expected Workflow Output (offline-first → structured → PPTX)

1. **Offline parse the PDF** (no external APIs), following `references/offline-parsing.md`, and produce a local structured package:
   - Cleaned metadata text: title, journal/date, headings
   - Figure legends grouped by figure number
   - Extracted images named:
     - `Figure_1.jpg`, `Figure_2.jpg`, ...
   - Graphical abstract image (if present)
   - Draft `explication.json` aligned to figure order

2. **Write Chinese content**:
   - Full-paper summary (background + key findings)
   - Figure-by-figure Results interpretation (purpose → method → object → outcome)
   - Concise critical appraisal (core contributions + internal limitations)

3. **Generate PPTX** with the required slide structure and layout constraints:
   - Slide 1: Title + metadata (journal/date/presenter/report date)
   - Slide 2: Overview (two text boxes; graphical abstract if present)
   - Middle slides: one slide per figure/table in original order
   - Final slide: overall summary + critical appraisal

### Minimal runnable “deck plan” (content-to-slide mapping)

```json
{
  "deck_style": {
    "language": "zh-CN",
    "panel_label_color": "#065A82",
    "transition_preset": "fade",
    "entrance_preset": "appear"
  },
  "slides": [
    {
      "type": "title",
      "title": "<Paper Title>",
      "meta": {
        "journal": "<Journal>",
        "publication_date": "<YYYY-MM-DD>",
        "presenter": "XXX",
        "report_date": "<YYYY-MM-DD>"
      }
    },
    {
      "type": "overview",
      "background": "<Chinese background summary>",
      "findings": "<Chinese key findings summary>",
      "graphical_abstract": "Graphical_Abstract.jpg"
    },
    {
      "type": "figure",
      "figure_id": "Figure_1",
      "title": "Figure 1: <Chinese figure title if available>",
      "image": "Figure_1.jpg",
      "body_zh": [
        "**A** ...",
        "**B** ...",
        "**Summary:** ..."
      ]
    },
    {
      "type": "final_summary",
      "core_highlights": ["..."],
      "internal_limitations": ["..."]
    }
  ]
}
```

## Implementation Details

### 1) Offline-first PDF collection (must not call external APIs)

Follow `references/offline-parsing.md` and produce a local structured output containing:

- Cleaned text fields:
  - `title`, `journal`, `publication_date`
  - section headings and key paragraphs (abstract/intro/results)
- Figures:
  - images exported and named `Figure_1.jpg`, `Figure_2.jpg`, ...
  - legends grouped by figure number
- Tables:
  - extracted table content and captions (as text or images, depending on the workflow)
- Graphical abstract:
  - capture image and approximate placement if present
- Draft `explication.json`:
  - ordered by figure appearance
  - each entry links legend → image filename → planned slide text blocks

Ignore supplementary items (e.g., `Figure S1`) unless explicitly requested.

### 2) Figure/table interpretation rules (Chinese, precise, aligned)

Use `references/figure-interpretation.md` and enforce:

- **1:1 mapping**: every figure/table must be covered by exactly one corresponding slide section (or one slide if required).
- Each result paragraph must be complete:
  - experimental purpose → method → object → concrete outcome (increase/decrease, up/down, etc.)
- Avoid vague phrases like “as shown in the figure”.
- Remove any leading `#` markers from figure body lines.
- Bold leading panel labels and ranges:
  - `A`, `A, B`, `A-C` → `**A**`, `**A, B**`, `**A-C**`
- Add a one-sentence line at the end of each figure slide:
  - `**Summary:** <one-sentence key result>`
  - Style “Summary” like panel labels (bold + label color)

### 3) Figure titles and localization

- Slide titles should use: `Figure X: <figure title>` when a title can be extracted (e.g., from “Figure 1. ...”).
- Convert figure titles to Chinese when possible.
- Prefer a local mapping file `figure_titles_zh.txt` if available:
  - Format: `Figure_1<TAB>Chinese Title`

### 4) Consistent per-deck styling parameters

- Panel label color: randomly choose **one** per deck from:
  - `#2C5F2D`, `#F96167`, `#065A82`, `#990011`
- Apply the same chosen color across all slides.
- Animations:
  - Randomly choose one slide transition preset and one entrance preset per deck
  - Keep them consistent across all slides
  - Reveal order: title → text → image

### 5) PPT layout constraints (Match v5 slides)

If a user-provided layout script is accessible, follow it. Otherwise, use the following fixed coordinates (inches) and typography:

- **Title slide**
  - Title box: `(2.0825, 1.796, 9.1683, 1.2)`, 32pt bold, centered
  - Metadata block (left = 4.8673, width = 6.0, height = 0.6):
    - Journal: top `4.5049`, 18pt
    - Presenter/date: top `5.2327` and `5.9049`, 16pt
- **Overview slide**
  - Background box: `(0.6, 0.6, 5.8, 6.2)`
  - Findings box: `(0.6, 3.4, 5.8, 3.4)`
  - Image: `(7.0, 0.8, 5.8, 5.6)`
- **Figure slides**
  - Title: `(0.6, 0.2, 12.0, 0.6)`, 22pt bold
  - Text box: `(0.7749, 1.5102, 4.7498, 2.861)`, 14pt
  - Image: `(7.0, 1.0, 5.8, 5.8)`
- **Summary slide**
  - Add borders
  - “Core Highlights” box: `(0.6, 0.6, 5.8, 3.0)`
  - “Internal Limitations” box: `(6.7, 3.9, 6.0, 3.0)`

### 6) PPTX editing integration

When creating or editing a `.pptx`, also follow the PPTX editing guidelines in:

- `D:\\SKILL\\project\\PPTX\\SKILL.md`