# Academic Poster Quality Self-Checklist

Use this comprehensive checklist before printing or presenting your research poster.

## Pre-Compilation Checks

### Content Completeness
- [ ] Title is concise and descriptive (10-15 words)
- [ ] All author names are spelled correctly
- [ ] Institutional affiliations are complete and accurate
- [ ] Contact email address is included
- [ ] All sections present: Introduction, Methods, Results, Conclusions
- [ ] References cited (5-10 core citations)
- [ ] Acknowledgments included (funding agencies, collaborators)
- [ ] No remaining placeholder text (e.g., TODO, Lorem ipsum, etc.)

### Visual Content
- [ ] All images ready and high resolution (300+ DPI)
- [ ] Figure captions written and descriptive
- [ ] Logos available (university, funding agencies)
- [ ] QR codes generated and tested
- [ ] Icon/graphic assets acquired (if used)

### LaTeX Configuration
- [ ] Correct paper size specified (A0, A1, 36×48", etc.)
- [ ] Orientation correct (portrait/landscape)
- [ ] Minimal margins configured (5-15mm)
- [ ] Font sizes appropriate (titles 72pt+, body 24pt+)
- [ ] Color scheme defined
- [ ] All packages installed and working

## Compilation Checks

### Successful Compilation
- [ ] PDF compiles without errors
- [ ] No critical warnings in .log file
- [ ] All references resolved (no [?] markers)
- [ ] All cross-references working
- [ ] Reference list generates correctly (if using BibTeX)

### Warning Check
Run in terminal: `grep -i "warning\|overfull\|underfull" poster.log`

- [ ] No overfull hbox warnings (text too wide)
- [ ] No underfull hbox warnings (spacing too loose)
- [ ] No missing figure warnings
- [ ] No missing font warnings
- [ ] No undefined reference warnings

## PDF Quality Checks

### Automated Checks

Run: `./scripts/review_poster.sh poster.pdf` or verify manually:

#### Page Specifications
```bash
pdfinfo poster.pdf | grep "Page size"
```
- [ ] Page size exactly matches requirements
- [ ] Single page document (not multiple pages)
- [ ] Orientation correct

#### Font Embedding
```bash
pdffonts poster.pdf
```
- [ ] All fonts show "yes" in "emb" column
- [ ] No bitmap fonts (should be Type 1 or TrueType)

#### Image Quality
```bash
pdfimages -list poster.pdf
```
- [ ] All images at least 300 DPI
- [ ] No JPEG artifacts in images
- [ ] Vector graphics used where possible

#### File Size
```bash
ls -lh poster.pdf
```
- [ ] Size reasonable (typically 2-50 MB)
- [ ] Not too large for digital sharing (<50 MB)
- [ ] Not too small (<1 MB may indicate low quality)

## Visual Check (100% Zoom)

### Layout and Spacing
- [ ] Content fills entire page (no excessive white margins)
- [ ] Consistent column spacing (1-2cm)
- [ ] Consistent module spacing (1-2cm)
- [ ] All elements aligned to grid
- [ ] No overlapping text or images
- [ ] White space evenly distributed (30-40% of total area)
- [ ] Poster visually balanced overall (no overly crowded or empty areas)

### Typography
- [ ] Title clear, readable, and prominent (72-120pt)
- [ ] Section headers clear (48-72pt)
- [ ] Body text large enough (minimum 24-36pt, recommended 30pt+)
- [ ] Figure captions readable (18-24pt)
- [ ] Text does not overflow edges
- [ ] Consistent font usage throughout
- [ ] Appropriate line spacing (1.2-1.5×)
- [ ] No awkward hyphenation or word breaks
- [ ] All special characters render correctly (Greek letters, math symbols)

### Visual Elements
- [ ] All figures display correctly
- [ ] No pixelated or blurry images
- [ ] High image resolution (verify by zooming to 200%)
- [ ] Figure labels large and clear
- [ ] Figure axes labeled with units
- [ ] Consistent color scheme across figures
- [ ] Legends readable and well-positioned
- [ ] Logos clear and professional
- [ ] QR codes clear with high contrast (minimum 2×2cm)
- [ ] No visual artifacts or rendering errors

### Color
- [ ] Colors render as expected (no fading)
- [ ] High contrast between text and background (≥4.5:1)
- [ ] Color scheme harmonious
- [ ] Colors suitable for printing (not too bright or fluorescent)
- [ ] Correct use of institutional standard colors
- [ ] Colorblind-friendly palette used (avoid relying solely on red-green)

### Content
- [ ] Title complete and correctly positioned
- [ ] All author names and affiliations visible
- [ ] All sections present and labeled
- [ ] Results section includes figures/data
- [ ] Conclusions clearly stated
- [ ] References consistently formatted
- [ ] Contact information clearly visible
- [ ] No missing content

## Scaled Print Test (Critical)

### Test Print Preparation
Print poster at 25% scale:
- A0 poster → Print on A4 paper
- 36×48" poster → Print on Letter paper
- A1 poster → Print on A5 paper

### Distance Readability

**At 6 feet (2 meters):**
- [ ] Title clearly readable
- [ ] Author identity recognizable
- [ ] Main figures visible

**At 4 feet (1.2 meters):**
- [ ] Section headers readable
- [ ] Figure captions readable
- [ ] Key results visible

**At 2 feet (0.6 meters):**
- [ ] Body text readable
- [ ] References readable
- [ ] All details clear

### Print Quality
- [ ] Colors accurate (matches screen preview)
- [ ] No banding or color cast
- [ ] Edges sharp (not blurry)
- [ ] Consistent print density
- [ ] No printer-induced defects

## Content Proofreading

### Text Accuracy
- [ ] Spell-checked all text
- [ ] Grammar checked
- [ ] All author names spelled correctly
- [ ] All affiliations accurate
- [ ] Email addresses correct
- [ ] No typos in title or headings

### Scientific Accuracy
- [ ] All numbers and statistics verified
- [ ] Units included and correct
- [ ] Statistical significance correctly indicated
- [ ] Sample sizes reported (n=)
- [ ] Figure numbers consistent
- [ ] Citations accurate and complete
- [ ] Research methods accurately described
- [ ] Results match figures/data
- [ ] Conclusions supported by data

### Consistency
- [ ] Terminology consistent throughout
- [ ] Abbreviations defined on first use
- [ ] Consistent notation (e.g., italics for genes)
- [ ] Consistent units (don't mix metric/imperial)
- [ ] Consistent decimal places
- [ ] Consistent citation format

## Accessibility Checks

### Color Contrast
Test at: https://webaim.org/resources/contrastchecker/

- [ ] Title and background contrast ≥ 7:1
- [ ] Body text and background contrast ≥ 4.5:1
- [ ] All text meets WCAG AA minimum requirements

### Colorblind Friendliness
Test using simulator: https://www.color-blindness.com/coblis-color-blindness-simulator/

- [ ] Information not lost in deuteranopia (green-blind)
- [ ] Key differences still visible in protanopia (red-blind)
- [ ] Pattern/shape differentiation used beyond color
- [ ] No critical information conveyed by color alone

### Visual Clarity
- [ ] Clear visual hierarchy (shown through size, weight, position)
- [ ] Reading order logically clear
- [ ] Grouping of related elements obvious
- [ ] Important information appropriately emphasized

## Peer Review

### 30 Second Test
Show poster to colleague for 30 seconds, then ask:
- [ ] Can they identify the research topic?
- [ ] Can they state the main findings?
- [ ] Do they remember key figures?

### 5 Minute Review
Have colleague read poster (5 minutes), then ask:
- [ ] Do they understand the research question?
- [ ] Can they explain the research methods?
- [ ] Can they summarize the conclusions?
- [ ] Can they identify the research novelty/importance?

### Feedback
- [ ] Noted all confusing elements
- [ ] Identified any unclear figures
- [ ] Checked for technical terms needing definition
- [ ] Verified logical flow

## Final Pre-Print Checks

### Technical Specifications
- [ ] PDF dimensions exactly match conference requirements
- [ ] Orientation correct (landscape vs. portrait)
- [ ] All fonts embedded (verified via pdffonts)
- [ ] Color space correct (RGB for screen, CMYK for printer if required)
- [ ] Resolution sufficient (all images 300+ DPI)
- [ ] Bleed added if required (typically 3-5mm)
- [ ] Crop marks visible if required
- [ ] File naming convention followed

### Communication with Print Shop
- [ ] Confirmed paper type (matte vs. glossy)
- [ ] Confirmed poster dimensions
- [ ] Provided color profile if required
- [ ] Verified delivery deadline
- [ ] Confirmed shipping/pickup arrangements
- [ ] Discussed backup plan if issues arise

### Backup and Storage
- [ ] PDF saved with clear filename: `surname_conference_poster.pdf`
- [ ] Original .tex file backed up
- [ ] All image files backed up
- [ ] Copy saved in cloud storage
- [ ] Copy saved on USB drive for conference
- [ ] Electronic version ready to email if requested

## Digital Presentation Checks

If presenting digitally or sharing online:

### File Optimization
- [ ] PDF compressed if >10MB (for email)
- [ ] Tested opening in Adobe Reader
- [ ] Tested opening in Preview (Mac)
- [ ] Tested opening in browser PDF viewer
- [ ] Tested on mobile devices

### Interactive Elements
- [ ] All QR codes tested and working
- [ ] QR codes link to correct URLs
- [ ] Hyperlinks working (if included)
- [ ] Links open correctly in new tab/window

### Alternative Formats
- [ ] PNG version created for social media (if needed)
- [ ] Thumbnail created
- [ ] Poster description/abstract prepared
- [ ] Hashtags and social media copy ready

## Conference-Specific Requirements

### Requirement Verification
- [ ] Poster size exactly matches conference specifications
- [ ] Orientation matches requirements
- [ ] File format correct (usually PDF)
- [ ] Submission deadline met
- [ ] File naming convention followed
- [ ] Abstract/description submitted if required

### Physical Preparation
- [ ] Poster printed and checked
- [ ] Backup printout prepared
- [ ] Pushpins/hanging materials ready
- [ ] Poster tube or flat portfolio for transport
- [ ] Business cards/handouts prepared
- [ ] Digital backup on laptop/phone

### Presentation Preparation
- [ ] Prepared 30-second "elevator pitch"
- [ ] Prepared 2-minute summary
- [ ] Prepared 5-minute detailed explanation
- [ ] Anticipated likely questions
- [ ] Follow-up materials ready (e.g., QR code to paper)

## Final Sign-Off

Date: ________________

Poster Title: _______________________________________________

Conference Name: _______________________________________________

Reviewer: ________________________________________________

All key items checked: [ ]

Ready to print: [ ]

Ready to present: [ ]

Notes/Issues to address:
_________________________________________________________
_________________________________________________________
_________________________________________________________

---

## Quick Reference: Common Problems

| Problem | Quick Fix |
|---------|-----------|
| White margins too large | Reduce margins in documentclass: `margin=5mm` |
| Text too small | Increase scale in beamerposter: `scale=1.5` |
| Figures blurry | Use vector graphics (PDF) or higher resolution (600+ DPI) |
| Colors wrong | Check RGB vs CMYK, test print before final printing |
| Fonts not embedded | Compile with: `pdflatex -dEmbedAllFonts=true` |
| Content being cut off | Check total width: column width + spacing + margins = page width |
| QR code won't scan | Increase size (minimum 2×2cm), ensure high contrast |
| File too large | Compress: `gs -sDEVICE=pdfwrite -dPDFSETTINGS=/printer ...` |

## Checklist Version
Version 1.0 - Applicable to LaTeX poster packages (beamerposter, tikzposter, baposter)
