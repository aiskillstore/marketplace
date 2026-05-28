# Paper2Web: Academic Homepage Generation System

## Overview

Paper2Web transforms academic papers into interactive, explorable academic homepages. Unlike traditional methods (direct generation, template-based, or HTML conversion), Paper2Web creates layout-aware interactive websites through an iterative optimization process.

## Core Capabilities

### 1. Layout-Aware Generation
- Analyzes paper structure and content organization.
- Creates responsive multi-column layouts.
- Adjusts design based on paper type (research paper, review, preprint, etc.).

### 2. Interactive Elements
- Expandable detail sections.
- Interactive figures.
- Embedded citations and references.
- Easy-to-browse navigation menus.
- Mobile-responsive design.

### 3. Content Refinement
The system uses an iterative pipeline:
1. Initial content extraction and structuring.
2. Layout generation with visual hierarchy.
3. Interactive element integration.
4. Aesthetic optimization.
5. Quality assessment and validation.

## Usage

### Basic Website Generation

```bash
python pipeline_all.py \
  --input-dir "path/to/papers" \
  --output-dir "path/to/output" \
  --model-choice 1
```

### Parameters

- `--input-dir`: Directory containing paper files (PDF or LaTeX).
- `--output-dir`: Output directory for generated website files.
- `--model-choice`: LLM model selection (1=GPT-4, 2=GPT-4.1).
- `--enable-logo-search`: Use Google Search API to find institution logos (optional).

### Input Format Requirements

**Supported Input Formats:**
1. **LaTeX Source** (Recommended, Best Results)
   - Main file: `main.tex`
   - Include all referenced images, tables, and reference files.
   - Each paper organized in a single directory.

2. **PDF Files**
   - High-quality PDF with selectable text.
   - Embedded images should be high resolution.
   - Proper section titles and structure.

**Directory Structure:**
```
input/
└── paper_name/
    ├── main.tex           # LaTeX source
    ├── bibliography.bib   # References
    ├── figures/           # Image files
    │   ├── fig1.png
    │   └── fig2.pdf
    └── tables/            # Table files
```

## Output Structure

Generated website includes:

```
output/paper_name/website/
├── index.html          # Main webpage
├── styles.css          # Stylesheet
├── script.js           # Interactive functionality scripts
├── assets/             # Images and media resources
│   ├── figures/
│   └── logos/
└── data/               # Structured data (optional)
```

## Customization Options

### Visual Design
Generated websites automatically include:
- Professional color scheme based on paper content.
- Typography optimized for readability.
- Consistent spacing and visual hierarchy.
- Dark mode support (optional).

### Content Sections
Standard sections include:
- Abstract
- Key findings/contributions
- Methodology overview
- Results and visualizations
- Discussion and implications
- References and citations
- Author information and affiliations

Automatically added sections based on paper content:
- Code repositories
- Dataset links
- Supplementary materials
- Related publications

## Quality Assessment

Paper2Web includes built-in evaluation mechanisms:

### Aesthetic Metrics
- Layout balance and spacing.
- Color harmony.
- Font consistency.
- Visual hierarchy effectiveness.

### Informational Metrics
- Content completeness.
- Clarity of key findings.
- Adequacy of methodology explanation.
- Quality of results presentation.

### Technical Metrics
- Page load time.
- Mobile responsiveness.
- Browser compatibility.
- Accessibility compliance.

## Advanced Features

### Automatic Logo Discovery
When Google Search API is enabled:
- Automatically finds institution logos.
- Matches author affiliations.
- Downloads and optimizes logo images.
- Integrates into website header.

### Citation Integration
- Interactive reference list.
- Hover preview of citations.
- Links to DOIs and external resources.
- Citation count tracking (if available).

### Image Enhancement
- High-resolution image rendering.
- Zoom and pan functionality.
- Figure captions and descriptions.
- Multi-figure navigation.

## Best Practices

### Input Preparation
1. **Use LaTeX when possible**: Provides best structure extraction.
2. **Include all resources**: Ensure images, tables, and references are included.
3. **Keep format clean**: Remove compiled artifacts and temporary files.
4. **High-quality images**: Use vector formats (PDF, SVG) when possible.

### Model Selection
- **GPT-4**: Best balance of quality and cost.
- **GPT-4.1**: Latest features, higher cost.
- **GPT-3.5-turbo**: Fast processing, suitable for simple papers.

### Output Optimization
1. Check accuracy of generated content.
2. Confirm all images render correctly.
3. Test interactive element functionality.
4. Verify mobile responsiveness.
5. Validate external links.

## Limitations

- Complex mathematical formulas may require manual verification.
- Multi-column layouts in PDF may affect extraction quality.
- Long papers (>50 pages) may require longer processing time.
- Certain chart types may require manual adjustment.

## Integration with Other Components

Paper2Web can be combined with:
- **Paper2Video**: Generate companion videos for websites.
- **Paper2Poster**: Create companion poster designs.
- **AutoPR**: Generate promotional content linked to websites.
