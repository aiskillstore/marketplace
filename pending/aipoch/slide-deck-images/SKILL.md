---
name: slide-deck-images
description: Generate professional slide-deck SVG images (not PPTX/PDF) when users ask to “create slides / slide deck / PPT” and need image outputs.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

Use this skill when you need to produce **slide images as SVG files** (plus outline/prompts), especially when:

1. A user asks for a “slide deck”, “PPT”, or “presentation” but explicitly wants **images** (SVG) rather than PPTX/PDF.
2. You need a **readable, shareable deck** optimized for scrolling/swiping (each slide stands alone without a presenter).
3. You want a **style-driven deck** using presets (e.g., `corporate`, `minimal`, `blueprint`) or custom style dimensions.
4. You need a **structured workflow** with optional review gates (outline review, prompt review) before generating images.
5. You need to **regenerate specific slides** (e.g., only slide 3 or slides 2,5,8) without rebuilding everything.

## Key Features

- **SVG-only output**: Generates `.svg` slide images (no PPTX/PDF generation).
- **Deterministic file structure**:
  - Output directory: `slides-svg/`
  - Naming: `NN-slide-[slug].svg`
- **End-to-end workflow**: Analyze → confirm → outline → prompts → SVG render → summary.
- **Style system**:
  - Preset styles (e.g., `blueprint`, `corporate`, `sketch-notes`, `notion`, etc.)
  - Custom style dimensions: texture, mood, typography, density
  - Automatic preset recommendation based on content signals
- **Review controls**:
  - `--outline-only`, `--prompts-only`, `--images-only`
  - Optional outline/prompt review steps via confirmation questions
- **Selective regeneration**: `--regenerate <N>` or `--regenerate 2,5,8`
- **No image-model dependency**: SVG rendering is performed by a Python script using configuration parameters.

## Dependencies

- Python **3.10+**
- Project script: `scripts/generate_svg.py` (invoked locally)
- Reference/spec files (used by the workflow):
  - `references/analysis-framework.md`
  - `references/outline-template.md`
  - `references/base-prompt.md`
  - `references/layouts.md`
  - `references/design-guidelines.md`
  - `references/dimensions/*.md`
  - `references/styles/<style>.md`
  - `references/config/preferences-schema.md`

## Example Usage

### CLI (skill invocation)

```bash
/slide-deck "Explain OAuth 2.0 for product managers"
/slide-deck "Explain OAuth 2.0 for product managers" --style corporate
/slide-deck "Explain OAuth 2.0 for product managers" --audience executives
/slide-deck "Explain OAuth 2.0 for product managers" --lang en
/slide-deck "Explain OAuth 2.0 for product managers" --slides 10
/slide-deck "Explain OAuth 2.0 for product managers" --outline-only
/slide-deck "Explain OAuth 2.0 for product managers" --prompts-only
/slide-deck "Explain OAuth 2.0 for product managers" --images-only
/slide-deck "Explain OAuth 2.0 for product managers" --regenerate 3
/slide-deck "Explain OAuth 2.0 for product managers" --regenerate 2,5,8
/slide-deck  # then paste content
```

### Generate SVG files locally

The SVG renderer reads parameters from its configuration area and **does not use CLI arguments**:

```bash
python scripts/generate_svg.py
```

Expected outputs:

- `outline.md`
- `prompts/` (one prompt file per slide)
- `slides-svg/NN-slide-[slug].svg`

## Implementation Details

### Output constraints

- Format: `.svg`
- Output directory: `slides-svg/`
- Filename pattern: `NN-slide-[slug].svg`

### Style system

#### Presets

| Preset | Characteristics | Typical use |
|---|---|---|
| `blueprint` (default) | grid + cool + technical + balanced | architecture, system design |
| `chalkboard` | organic + warm + handwritten + balanced | education, tutorials |
| `corporate` | clean + professional + geometric + balanced | pitches, proposals |
| `minimal` | clean + neutral + geometric + minimal | executive briefings |
| `sketch-notes` | organic + warm + handwritten + balanced | education, tutorials |
| `watercolor` | organic + warm + humanist + minimal | lifestyle, wellness |
| `dark-atmospheric` | clean + dark + editorial + balanced | entertainment, gaming |
| `notion` | clean + neutral + geometric + dense | product demos, SaaS |
| `bold-editorial` | clean + vibrant + editorial + balanced | launches, keynotes |
| `editorial-infographic` | clean + cool + editorial + dense | explainers, research |
| `fantasy-animation` | organic + vibrant + handwritten + minimal | storytelling |
| `intuition-machine` | clean + cool + technical + dense | academia, technical docs |
| `pixel-art` | pixel + vibrant + technical + balanced | gaming, dev talks |
| `scientific` | clean + cool + technical + dense | medical, biology, chemistry |
| `vector-illustration` | clean + vibrant + humanist + balanced | creative, kids content |
| `vintage` | paper + warm + editorial + balanced | history, culture |

#### Style dimensions

| Dimension | Options | Meaning |
|---|---|---|
| Texture | clean, grid, organic, pixel, paper | background/texture treatment |
| Mood | professional, warm, cool, vibrant, dark, neutral | tone and color temperature |
| Typography | geometric, humanist, handwritten, editorial, technical | heading/body typographic feel |
| Density | minimal, balanced, dense | information density per slide |

Full dimension specs: `references/dimensions/*.md`

#### Automatic preset recommendation (signals → preset)

| Content signals | Preset |
|---|---|
| tutorial, learn, education, guide, beginner | `sketch-notes` |
| classroom, teaching, school, chalkboard | `chalkboard` |
| architecture, system, data, analysis, technical | `blueprint` |
| creative, children, kids, cute | `vector-illustration` |
| briefing, academic, research, bilingual | `intuition-machine` |
| executive, minimal, clean, simple | `minimal` |
| saas, product, dashboard, metrics | `notion` |
| investor, quarterly, business, corporate | `corporate` |
| launch, marketing, keynote, magazine | `bold-editorial` |
| entertainment, music, gaming, atmospheric | `dark-atmospheric` |
| explainer, journalism, science communication | `editorial-infographic` |
| story, fantasy, animation, magical | `fantasy-animation` |
| gaming, retro, pixel, developer | `pixel-art` |
| biology, chemistry, medical, scientific | `scientific` |
| history, heritage, vintage, expedition | `vintage` |
| lifestyle, wellness, travel, artistic | `watercolor` |
| Default | `blueprint` |

### Design philosophy (reader-first decks)

Decks are designed for **reading and sharing**, not live presenting:

- Each slide is understandable without narration.
- Logical flow when scrolling/swiping.
- Each slide includes necessary context.
- Optimized for social sharing.

See: `references/design-guidelines.md` (visual hierarchy, density, colors, fonts, recommendations).  
Layouts: `references/layouts.md`.

### Workflow and state files

#### Step 1: Setup & Analyze

1. **Load preferences** from `EXTEND.md` (if present) and summarize:
   - Style (preset/custom)
   - Audience (or auto-detect)
   - Language (or auto-detect)
   - Review enabled/disabled  
   Schema: `references/config/preferences-schema.md`

2. **Analyze content** (per `references/analysis-framework.md`):
   - Save input as `source.md` (backup existing as `source-backup-YYYYMMDD-HHMMSS.md`)
   - Detect language
   - Recommend style preset from content signals
   - Estimate slide count
   - Generate topic slug

3. **Check existing content (required)** before confirmation:
   - If output directory exists, ask how to proceed:
     - Regenerate outline (keep images)
     - Regenerate images (keep outline)
     - Backup and regenerate all (`{slug}-backup-{timestamp}`)
     - Exit
   - Save `analysis.md` with topic, audience, signals, recommended style, slide count, language.

#### Step 2: Confirmation (required)

- Two rounds:
  - Round 1: always
  - Round 2: only if “Custom dimensions” is selected
- Round 1 questions (AskUserQuestion):
  1. Style (recommended preset / alternative / custom dimensions)
  2. Audience (general/beginners/experts/executives)
  3. Slide count (recommended / fewer / more)
  4. Review outline? (yes/no)
  5. Review prompts? (yes/no)

- Round 2 (custom dimensions): AskUserQuestion for texture, mood, typography, density.

After confirmation:
- Write results back to `analysis.md`
- Record `skip_outline_review` and `skip_prompt_review`

#### Step 3: Generate outline

- If preset: read `references/styles/{preset}.md`
- If custom: combine from `references/dimensions/`
- Follow `references/outline-template.md`
- Save as `outline.md`
- Stop if `--outline-only`
- If `skip_outline_review` → skip to Step 5, else Step 4

#### Step 4: Review outline (conditional)

- Show slide summary table (title/type/layout)
- Ask whether to proceed, edit `outline.md`, or regenerate outline

#### Step 5: Generate prompts

- Base prompt: `references/base-prompt.md`
- For each slide:
  - Extract style instructions from outline
  - Merge layout guidance from `references/layouts.md` when specified
- Save to `prompts/`
  - Backup existing prompt files as `prompts/NN-slide-{slug}-backup-YYYYMMDD-HHMMSS.md`
- Stop if `--prompts-only`
- If `skip_prompt_review` → skip to Step 7, else Step 6

#### Step 6: Review prompts (conditional)

- Show prompt list table and `prompts/` path
- Ask whether to proceed, edit prompts, or regenerate prompts

#### Step 7: Generate SVG images

- If `--images-only`, start here
- If `--regenerate`, render only specified pages
- Render via `scripts/generate_svg.py`
- Create session id: `slides-{topic-slug}-{timestamp}`
- Backup existing images as `NN-slide-{slug}-backup-YYYYMMDD-HHMMSS.svg`
- Progress reporting: `Generated X/N` (in user language)
- Retry once on failure, then report error

#### Step 8: Output summary

Include:
- Topic
- Style (preset or custom dimensions)
- Total slides
- List of generated SVG filenames
- `outline.md` location