# LaTeX Research Poster Generation Skill

Create professional, publication-ready research posters for conferences and academic presentations using LaTeX.

## Overview

This skill provides comprehensive guidance on creating research posters using three main LaTeX packages:
- **beamerposter**: Traditional academic poster with familiar Beamer syntax
- **tikzposter**: Modern, colorful design with TikZ integration
- **baposter**: Structured multi-column layout with automatic positioning

## Quick Start

### 1. Choose a Template

Browse templates in `assets/`:
- `beamerposter_template.tex` - Classic academic style
- `tikzposter_template.tex` - Modern, colorful design
- `baposter_template.tex` - Structured multi-column layout

### 2. Customize Content

Edit the template for your research:
- Title, authors, affiliations
- Introduction, Methods, Results, Conclusions
- Replace placeholder figures with your images
- Update references and acknowledgments

### 3. Full-Page Configuration

Posters should cover the entire page with minimal margins:

```latex
% beamerposter - Full page settings
\documentclass[final,t]{beamer}
\usepackage[size=a0,scale=1.4,orientation=portrait]{beamerposter}
\setbeamersize{text margin left=5mm, text margin right=5mm}
\usepackage[margin=10mm]{geometry}

% tikzposter - Full page settings
\documentclass[25pt,a0paper,portrait,margin=10mm,innermargin=15mm]{tikzposter}

% baposter - Full page settings
\documentclass[a0paper,portrait,fontscale=0.285]{baposter}
```

### 4. Compile

```bash
pdflatex poster.tex

# Or for better font support:
lualatex poster.tex
xelatex poster.tex
```

### 5. Check PDF Quality

**Must do before printing!**

```bash
# Run automated check
./scripts/review_poster.sh poster.pdf

# Manual verification (see checklist below)
```

## Core Features

### Full-Page Coverage

All templates are configured to maximize content area:
- Minimal external margins (5-15mm)
- Optimal spacing between columns (15-20mm)
- Appropriate block padding for readability
- No wasted white space

### PDF Quality Control

**Automated checks** (`review_poster.sh`):
- Page size validation
- Font embedding check
- Image resolution analysis
- File size optimization

**Manual verification** (`assets/poster_quality_checklist.md`):
- Visual check at 100% zoom
- Scaled-down print test (25%)
- Typography and spacing review
- Content completeness check

### Design Principles

All templates follow evidence-based poster design:
- **Typography**: Titles 72pt+, headers 48-72pt, body 24-36pt
- **Color**: High contrast (≥4.5:1), colorblind-friendly palettes
- **Layout**: Clear visual hierarchy, logical flow
- **Content**: Maximum 300-800 words, 40-50% visual content

## Common Poster Sizes

Templates support all standard sizes:

| Size | Dimensions | Configuration |
|------|------------|---------------|
| A0 | 841 × 1189 mm | `size=a0` or `a0paper` |
| A1 | 594 × 841 mm | `size=a1` or `a1paper` |
| 36×48" | 914 × 1219 mm | Custom page size |
| 42×56" | 1067 × 1422 mm | Custom page size |

## Documentation

### Reference Guides

**Comprehensive documentation** (in `references/`):

1. **`latex_poster_packages.md`** (746 lines)
   - Detailed comparison of beamerposter, tikzposter, baposter
   - Package-specific syntax and examples
   - Advantages, limitations, best use cases
   - Theme and color customization
   - Compilation tips and troubleshooting

2. **`poster_design_principles.md`** (807 lines)
   - Visual hierarchy and white space
   - Typography: font selection, sizing, readability
   - Color theory: schemes, contrast, accessibility
   - Colorblind-friendly palettes
   - Icons, graphics, and visual elements
   - Common design mistakes to avoid

3. **`poster_layout_design.md`** (650+ lines)
   - Grid systems (2, 3, 4 column layouts)
   - Visual flow and reading patterns
   - Spatial organization strategies
   - White space management
   - Block and box design
   - Layout patterns by research type

4_guide.md`** (900+ lines)
   - Content strategy. **`poster_content (3-5 minute rule)
   - Word budget by section
   - Visual-to-text ratio (40-50% visual)
   - Writing guidance for specific sections
   - Figure integration and captions
   - Adapting papers to posters

### Tools and Resources

**Scripts** (in `scripts/`):
- `review_poster.sh`: Automated PDF quality checking
  - Page size validation
  - Font embedding verification
  - Image resolution analysis
  - File size assessment

**Checklists** (in `assets/`):
- `poster_quality_checklist.md`: Comprehensive pre-print checklist
  - Pre-compilation checks
  - PDF quality verification
  - Visual inspection items
  - Accessibility checks
  - Peer review guidelines
  - Final print checklist

**Templates** (in `assets/`):
- `beamerposter_template.tex`: Fully working template
- `tikzposter_template.tex`: Fully working template
- `baposter_template.tex`: Fully working template

## Workflow

### Recommended Poster Creation Process

**1. Planning** (before LaTeX)
- Determine conference requirements (size, orientation)
- Identify 3-5 key results to highlight
- Create images (300+ DPI)
- Draft content outline (300-800 words)

**2. Template Selection**
- Choose package based on needs:
  - **beamerposter**: Traditional conferences, institutional branding
  - **tikzposter**: Modern conferences, creative fields
  - **baposter**: Multi-section posters, structured layouts

**3. Content Integration**
- Copy template and customize
- Replace placeholder text
- Add images ensuring high resolution
- Configure colors to match brand identity

**4. Compilation and Checking**
- Compile to PDF
- Run `review_poster.sh` for automated checks
- Visual inspection at 100% zoom
- Verify against `poster_quality_checklist.md`

**5. Test Printing**
- **Critical step!** Print at 25% scale
- A0 → A4 paper, 36×48" → Letter paper
- View from 2-3 feet away (simulates full-size 8-12 feet viewing)
- Verify readability and colors

**6. Revision**
- Fix any issues found
- Proofread carefully (errors are magnified!)
- Get colleague feedback
- Final compilation

**7. Printing**
- Verify page size: `pdfinfo poster.pdf`
- Check font embedding: `pdffonts poster.pdf`
- Send to professional print shop 2-3 days before deadline
- Keep backup copies

## Troubleshooting

### Large White Borders

**Problem**: Excessive white space around poster edges

**Solution**:
```latex
% beamerposter
\setbeamersize{text margin left=5mm, text margin right=5mm}
\usepackage[margin=10mm]{geometry}

% tikzposter
\documentclass[..., margin=5mm, innermargin=10mm]{tikzposter}

% baposter
\documentclass[a0paper, margin=5mm]{baposter}
```

### Content Being Cut Off

**Problem**: Text or images exceeding page boundaries

**Solution**:
- Check total width: column width + spacing + margins = page width
- Reduce column width or spacing
- Debug using visible page boundaries:
```latex
\usepackage{eso-pic}
AddToShipoutPictureBG{
  \AtPageLowerLeft{
    \put(0,0){\framebox(\LenToUnit{\paperwidth},\LenToUnit{\paperheight}){}}
  }
}
```

### Blurry Images

**Problem**: Images pixelated or low quality

**Solution**:
- Use vector graphics when possible (PDF, SVG)
- Raster images: minimum 300 DPI at final print size
- For A0 width (33.1"): 300 DPI = at least 9930 pixels
- Check with: `pdfimages -list poster.pdf`

### Fonts Not Embedded

**Problem**: Printer rejects PDF due to missing fonts

**Solution**:
```bash
# Recompile with embedded fonts
pdflatex -dEmbedAllFonts=true poster.tex

# Verify embedding
pdffonts poster.pdf
# All fonts should show "yes" under "emb" column
```

### File Too Large

**Problem**: PDF exceeds email size limit (>50MB)

**Solution**:
```bash
# Compress for digital sharing
gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 \
   -dPDFSETTINGS=/printer -dNOPAUSE -dQUIET -dBATCH \
   -sOutputFile=poster_compressed.pdf poster.pdf

# Keep original uncompressed version for printing
```

## Common Mistakes to Avoid

### Content
- ❌ Too much text (>1000 words)
- ❌ Font too small (body <24pt)
- ❌ No clear core message
- ✅ 300-800 words, 30pt+ body, 1-3 key findings

### Design
- ❌ Poor color contrast (<4.5:1)
- ❌ Red-green color scheme (colorblind issues)
- ❌ Cramped layout with no white space
- ✅ High contrast, accessible colors, generous spacing

### Technical
- ❌ Wrong poster size
- ❌ Low resolution images (<300 DPI)
- ❌ Fonts not embedded
- ✅ Verify specs, high-res images, embedded fonts

## Package Comparison

Quick reference for choosing the right package:

| Feature | beamerposter | tikzposter | baposter |
|---------|--------------|------------|----------|
| **Learning curve** | Simple (Beamer users) | Medium | Medium |
| **Aesthetics** | Traditional | Modern | Professional |
| **Customization** | Medium | High (TikZ) | Structured |
| **Compilation speed** | Fast | Slower | Fast-Medium |
| **Best for** | Academic conferences | Creative design | Multi-column layouts |

**Recommendations:**
- First-time poster makers: **beamerposter** (familiar, simple)
- Modern conferences: **tikzposter** (beautiful, flexible)
- Complex layouts: **baposter** (auto-positioning)

## Usage Examples

### In Scientific Writer CLI

```
> Create a research poster about Transformer Attention for NeurIPS

The assistant will:
1. Ask about poster size and orientation
2. Generate complete LaTeX poster with your content
3. Configure full-page coverage
4. Provide compilation instructions
5. Run quality checks on generated PDF
```

### Manual Creation

```bash
# 1. Copy template
cp assets/tikzposter_template.tex my_poster.tex

# 2. Edit content
vim my_poster.tex

# 3. Compile
pdflatex my_poster.tex

# 4. Check
./scripts/review_poster.sh my_poster.pdf

# 5. Test print at 25% scale
# (A4 paper for A0 content)

# 6. Final printing
```

## Secrets to Success

### Content Strategy
1. **One core message**: What should the audience remember most?
2. **3-5 key figures**: Visual content dominates
3. **300-800 words**: Less is more
4. **Bullet points**: More readable than paragraphs

### Design Strategy
1. **High contrast**: Dark on light or light on dark
2. **Large fonts**: 30pt+ body for distance reading
3. **White space**: 30-40% of poster should be blank
4. **Visual hierarchy**: Significant size differences (titles 3x body)

### Technical Strategy
1. **Test early**: Print at 25% before final printing
2. **Vector graphics**: Use PDF/SVG whenever possible
3. **Verify specs**: Check page size, fonts, resolution
4. **Get feedback**: Have colleagues review before printing

## Additional Resources

### Online Tools
- **Color contrast checker**: https://webaim.org/resources/contrastchecker/
- **Colorblind simulator**: https://www.color-blindness.com/coblis-color-blindness-simulator/
- **Palette generator**: https://coolors.co/

### LaTeX Packages
- `beamerposter`: Extends Beamer for poster-sized documents
- `tikzposter`: Creates modern posters using TikZ
- `baposter`: Box-based automatic poster layout
- `qrcode`: Generates QR codes in LaTeX
- `graphicx`: Includes images
- `tcolorbox`: Colored boxes and frames

### Further Reading
- All reference documents in `references/` directory
- Quality checklist in `assets/poster_quality_checklist.md`
- Package comparison in `references/latex_poster_packages.md`

## Support

For questions or concerns:
- Check reference documents in `references/`
- Review troubleshooting section above
- Run automated check: `./scripts/review_poster.sh`
- Use quality checklist: `assets/poster_quality_checklist.md`

## Version

LaTeX Poster Skill v1.0
Compatible with: beamerposter, tikzposter, baposter
Last updated: January 2025
