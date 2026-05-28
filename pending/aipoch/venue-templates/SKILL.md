---
name: venue-templates
description: Venue-specific LaTeX templates, formatting requirements, and submission guidelines for journals, conferences, posters, and grants—use when a target venue imposes strict layout, page limits, anonymization, or agency compliance rules.
license: MIT
author: AIPOCH
---
> **Source**: [https://github.com/aipoch/medical-research-skills](https://github.com/aipoch/medical-research-skills)

## When to Use

- You are submitting a manuscript to a specific journal (e.g., Nature, Science, PLOS, Cell Press, IEEE, ACM) and must follow its official LaTeX class/style and author instructions.
- You are preparing a conference paper (e.g., NeurIPS, ICML, ICLR, CVPR, CHI, ACL/EMNLP) with strict page limits, anonymization rules, and required formatting.
- You need to produce a conference poster in a standard size (A0/A1/36×48/etc.) using common LaTeX poster packages.
- You are drafting a grant proposal (e.g., NSF, NIH, DOE, DARPA) where compliance constraints (page limits, margins, font rules, required sections) are enforced.
- You want to validate that a compiled PDF complies with venue requirements (page count, margins, fonts, reference style, figure constraints).

## Key Features

- **Template library** for:
  - Journal articles (Nature portfolio, Science family, PLOS, Cell Press, IEEE, ACM, Springer/Elsevier/Wiley/BMC/Frontiers, etc.)
  - Conference papers (NeurIPS/ICML/ICLR/CVPR/AAAI/CHI/SIGKDD/EMNLP/SIGIR/USENIX, etc.)
  - Research posters (A0/A1/US sizes; `beamerposter`, `tikzposter`, `baposter`)
  - Grant proposals (NSF/NIH/DOE/DARPA + selected foundations)
- **Venue requirements references** (page limits, fonts, margins, spacing, anonymization, file formats, supplementary limits).
- **Helper scripts** to:
  - query templates/requirements by venue (`scripts/query_template.py`)
  - customize templates with metadata (`scripts/customize_template.py`)
  - validate compiled outputs (`scripts/validate_format.py`)
- **Writing style guides and examples** (how the “voice” differs across venues), stored under `references/` and `assets/examples/`.

## Dependencies

- Python `>=3.10`
- TeX Live `>=2023` (or MiKTeX `>=23.x`)
- `latexmk >=4.80` (recommended for reproducible builds)

## Example Usage

A minimal end-to-end workflow (query → customize → compile → validate):

```bash
# 1) Discover templates and requirements for a venue
python scripts/query_template.py --venue "NeurIPS" --type "article"
python scripts/query_template.py --venue "NeurIPS" --requirements

# 2) Customize a template (example: Nature article)
python scripts/customize_template.py \
  --template assets/journals/nature_article.tex \
  --title "Your Paper Title" \
  --authors "First Author, Second Author" \
  --affiliations "University Name" \
  --output my_nature_paper.tex

# 3) Compile (choose one)
latexmk -pdf my_nature_paper.tex
# or:
pdflatex my_nature_paper.tex
bibtex my_nature_paper
pdflatex my_nature_paper.tex
pdflatex my_nature_paper.tex

# 4) Validate the compiled PDF against venue rules
python scripts/validate_format.py \
  --file my_nature_paper.pdf \
  --venue "Nature" \
  --check-all
```

Common reference and asset locations used by this skill:

- Requirements:
  - `references/journals_formatting.md`
  - `references/conferences_formatting.md`
  - `references/posters_guidelines.md`
  - `references/grants_requirements.md`
- Templates:
  - `assets/journals/`
  - `assets/posters/`
  - `assets/grants/`
- Writing style guides:
  - `references/venue_writing_styles.md`
  - `references/nature_science_style.md`
  - `references/ml_conference_style.md`
  - `references/reviewer_expectations.md`
- Writing examples:
  - `assets/examples/`

## Implementation Details

- **Template selection logic**
  - Use `scripts/query_template.py` to map `(venue, document type)` to a canonical template path under `assets/` and to the corresponding requirements entry under `references/`.
  - Prefer official venue class/style files when available (e.g., conference `.sty` files), and treat local templates as wrappers/examples.

- **Customization model**
  - `scripts/customize_template.py` replaces placeholders (title/authors/affiliations/email and other metadata) while preserving venue-controlled formatting directives.
  - Recommended practice: do not override class options, margins, font settings, or bibliography style unless the venue explicitly allows it.

- **Validation checks (typical)**
  - Page count vs. venue limit (e.g., NeurIPS/ICML main text limits; NSF/NIH section limits).
  - Margin and font constraints (common in grants; sometimes enforced in conferences).
  - Reference/citation style consistency (numeric vs author-year; bracket vs superscript).
  - Figure constraints (resolution guidance, allowed formats, color requirements).
  - Anonymization requirements for double-blind venues (presence of author-identifying metadata).

- **Poster sizing and layout**
  - Poster templates target standard sizes (A0/A1 and common US dimensions) and provide grid/column structures and recommended font scales for distance readability.
  - Typical packages supported: `beamerposter`, `tikzposter`, `baposter`.

- **Style guides (beyond formatting)**
  - Venue writing conventions are documented under `references/` (e.g., narrative breadth for Nature/Science vs. contribution-focused structure for ML conferences).
  - Examples under `assets/examples/` illustrate venue-typical abstracts/introductions/structured sections.