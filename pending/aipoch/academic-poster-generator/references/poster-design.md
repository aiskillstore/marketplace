# Poster Design Reference

Comprehensive design principles and best practices for academic posters.

## Visual Hierarchy

### Establish Clear Information Flow

Guide viewers through content with intentional structure:

**Z-pattern flow:**
1. **Top-left**: Title and authors (primary attention)
2. **Top-right**: Abstract or key finding
3. **Middle-left**: Introduction and methods
4. **Middle-right**: Results
5. **Bottom**: Conclusions and references

**F-pattern flow (for text-heavy posters):**
1. **Top**: Title and abstract
2. **Left column**: Introduction, methods
3. **Middle**: Results
4. **Right column**: Discussion, conclusions

### Size and Scale Guidelines

**Text sizes for A0 poster:**
```
Title:           72-120pt   (72pt minimum, 90-100pt optimal)
Authors:         36-48pt    (Affiliation slightly smaller)
Section headers: 48-72pt    (48pt minimum, 60pt optimal)
Sub-headers:     36-48pt
Body text:       24-36pt    (24pt minimum, 28-32pt optimal)
Figure captions: 20-24pt
Footnotes:       16-20pt
```

**Scaling for different sizes:**
- A1: Multiply A0 sizes by 0.71
- A2: Multiply A0 sizes by 0.5
- 36×48": Similar to A0 (slightly smaller)

### Visual Weight Distribution

**Rule of thirds:**
- Top third: Title, authors, affiliations, logos
- Middle two-thirds: Main content columns
- Bottom third: Conclusions, references, contact info

**Content balance:**
- Text: 50-60% of total area
- Visuals (figures/tables): 30-40%
- White space: 10-20%

## Typography

### Font Selection

**Recommended sans-serif fonts:**
```
Helvetica/Arial:         Clean, professional (most common)
Calibri:                Modern, friendly (Microsoft)
Futura:                 Geometric, bold
Optima:                 Elegant, readable
Verdana:                Wide, highly legible
```

**Font pairing guidelines:**
- Use maximum 2-3 font families
- Title font: Bold, distinctive
- Body font: Clean, readable
- Math font: Sans-serif math (use `\usepackage{sfmath}`)

### Font Implementation

**Helvetica in LaTeX:**
```latex
\usepackage{helvet}
\renewcommand{\familydefault}{\sfdefault}
```

**Calibri (requires XeLaTeX/LuaLaTeX):**
```latex
\usepackage{fontspec}
\setsansfont{Calibri}
```

**Arial in LaTeX:**
```latex
\usepackage[T1]{fontenc}
\usepackage[arial]{helvet}
\renewcommand{\familydefault}{\sfdefault}
```

### Text Formatting

**Emphasis:**
```latex
% Bold for key terms
\textbf{important finding}

% Color highlights (use sparingly)
\textcolor{blue}{key point}

% Underlining (avoid - hard to read)
\underline{text}

% Boxes for critical information
\fbox{\textbf{Main Result}}
```

**Avoid:**
- ❌ All caps for body text
- ❌ Italic text (hard to read from distance)
- ❌ Multiple colors in single paragraph
- ❌ Font sizes below 24pt for body text

## Color Design

### Color Principles

**Contrast requirements:**
- Text-background: 4.5:1 minimum (WCAG AA)
- Important elements: 7:1 recommended (WCAG AAA)
- Large text: 3:1 acceptable

**Color schemes:**

**Monochromatic:**
```
Primary:   Blue #0066CC
Secondary: Blue #4DA6FF
Accent:    Blue #001A33
Background: White #FFFFFF
```

**Analogous:**
```
Primary:   Blue #0066CC
Secondary: Teal #00CC99
Accent:    Purple #9900CC
Background: White #FFFFFF
```

**Complementary:**
```
Primary:   Blue #0066CC
Secondary: Orange #FF9933
Accent:    Dark Orange #CC6600
Background: Light Gray #F5F5F5
```

### Color Blind Friendly Palettes

**Viridis (scientific):**
```latex
\definecolor{viridis1}{RGB}{68,1,84}
\definecolor{viridis2}{RGB}{59,82,139}
\definecolor{viridis3}{RGB}{33,144,141}
\definecolor{viridis4}{RGB}{94,201,98}
\definecolor{viridis5}{RGB}{253,231,37}
```

**ColorBrewer qualitative:**
```latex
\definecolor{cb1}{RGB}{230,97,1}      % Orange
\definecolor{cb2}{RGB}{253,184,99}    % Light orange
\definecolor{cb3}{RGB}{178,171,210}   % Light purple
\definecolor{cb4}{RGB}{94,60,153}     % Purple
```

**IBM Color Blind Safe:**
```latex
\definecolor{ibm1}{RGB}{119,158,203}  % Blue
\definecolor{ibm2}{RGB}{255,179,71}   % Orange
\definecolor{ibm3}{RGB}{77,190,238}   % Light blue
\definecolor{ibm4}{RGB}{209,131,105}  % Light orange
\definecolor{ibm5}{RGB}{156,156,156}  % Gray
```

### Institutional Colors

**Common university colors:**

MIT:
```latex
\definecolor{mitred}{RGB}{163,31,52}
```

Stanford:
```latex
\definecolor{stanfordred}{RGB}{140,21,21}
\definecolor{stanfordcardinal}{RGB}{140,21,21}
```

Harvard:
```latex
\definecolor{harvardcrimson}{RGB}{165,28,28}
```

UC Berkeley:
```latex
\definecolor{berkeleyblue}{RGB}{0,50,98}
\definecolor{calgold}{RGB}{253,181,21}
```

### Color Implementation

**In beamerposter:**
```latex
\definecolor{primary}{RGB}{0,102,204}
\definecolor{secondary}{RGB}{204,0,0}

\setbeamercolor{block title}{bg=primary,fg=white}
\setbeamercolor{block body}{bg=primary!10,fg=black}
```

**In tikzposter:**
```latex
\definecolor{primary}{RGB}{0,102,204}
\definecolor{secondary}{RGB}{204,0,0}

\setcolorpalette{primary}{primary}
\setcolorpalette{secondary}{secondary}
```

**In baposter:**
```latex
\begin{poster}{
  headerColorOne=primary!80,
  headerColorTwo=primary!40,
  borderColor=primary!50,
  boxColorOne=primary!10
}{...}{...}
```

## Layout Design

### Column Structures

**Two-column layout:**
- Left: Introduction, Methods (40%)
- Right: Results, Discussion, Conclusions (60%)

**Three-column layout (most common):**
- Left: Introduction, Methods (33%)
- Middle: Results (33%)
- Right: Discussion, Conclusions, References (33%)

**Four-column layout:**
- Leftmost: Introduction (25%)
- Left-middle: Methods (25%)
- Right-middle: Results (25%)
- Rightmost: Discussion, Conclusions (25%)

### Spacing Guidelines

**Margins:**
- Outer margins: 10-15mm
- Column spacing: 15-20mm
- Block spacing: 15-20mm
- Internal padding: 10-15mm

**Implementation:**
```latex
% beamerposter
\setbeamersize{text margin left=10mm, text margin right=10mm}

% tikzposter
\documentclass[...,margin=10mm,colspacing=15mm]{tikzposter}

% baposter
\begin{poster}{colspacing=1.5em,...}{...}{...}
```

### White Space Management

**Active vs. passive white space:**
- Active white space: Intentional spacing to guide eye
- Passive white space: Natural margins and gutters

**White space ratios:**
- Total white space: 10-20% of poster
- Between sections: 15-20mm
- Between paragraphs: 5-10mm
- Between blocks: 15-20mm

## Visual Elements

### Figure Design

**Figure size guidelines:**
- Main figures: 25-30% of poster width
- Small figures: 15-20% of poster width
- Height: Proportional, maintain aspect ratio

**Figure quality:**
- Resolution: 300 DPI minimum for print
- Vector graphics preferred (PDF, SVG, EPS)
- Raster: PNG, JPEG (300 DPI at final size)

**Figure labels:**
- Label size: 20-24pt
- Position: Below figure, centered
- Content: Descriptive, not just "Figure 1"

**Example:**
```latex
\begin{figure}
  \centering
  \includegraphics[width=0.8\linewidth]{results.pdf}
  \caption{Experimental results showing significant improvement (n=50, p<0.01)}
\end{figure}
```

### Table Design

**Table formatting:**
```latex
\usepackage{booktabs}

\begin{table}
  \centering
  \caption{Comparison of methods}
  \begin{tabular}{lcc}
    \toprule
    Method & Accuracy & F1-Score \\
    \midrule
    Baseline & 78.5% & 0.76 \\
    Proposed & 85.2% & 0.84 \\
    \midrule
    Improvement & +6.7% & +0.08 \\
    \bottomrule
  \end{tabular}
\end{table}
```

**Table guidelines:**
- Use `\toprule`, `\midrule`, `\bottomrule` for horizontal lines
- Avoid vertical lines
- Align numbers by decimal point
- Highlight key results in bold

### Icons and Graphics

**TikZ icons:**
```latex
\usepackage{fontawesome5}

% Common icons
\faBook        % Methods
\faFlask       % Experimental
\faChartBar    % Results
\faLightbulb   % Ideas
\faUniversity % Affiliation
```

**Custom icons:**
```latex
\begin{tikzpicture}
  \node[draw, circle, minimum size=2cm] {Icon};
\end{tikzpicture}
```

### QR Codes

**QR code implementation:**
```latex
\usepackage{qrcode}

% Basic QR code
\qrcode[height=3cm]{https://github.com/username/project}

% QR code with caption
\begin{center}
  \qrcode[height=3cm]{https://doi.org/10.1234/paper}\\
  \vspace{0.5em}
  \small{Scan for full paper}
\end{center}
```

**QR code best practices:**
- Minimum size: 2×2 cm
- High contrast (black on white)
- Place in visible location
- Test scanning before printing

## Content Guidelines

### Text Reduction Strategies

**Paragraph to bullets:**
```latex
% Original paragraph
"The experimental design involved 50 participants who were randomly assigned to either the treatment group or the control group. The treatment group received the new intervention, while the control group received standard care."

% Bullet points
\begin{itemize}
  \item 50 participants
  \item Random assignment
  \item Treatment vs. control groups
  \item New intervention vs. standard care
\end{itemize}
```

**Word count targets:**
- Title: 10-15 words
- Abstract: 50-100 words
- Introduction: 100-150 words
- Methods: 100-150 words
- Results: 150-200 words
- Discussion: 100-150 words
- Conclusions: 50-100 words
- Total: 300-800 words

### Section Organization

**Standard sections:**
1. Title and Authors (10-15% of space)
2. Introduction (10-15%)
3. Methods (15-20%)
4. Results (25-30%)
5. Discussion (15-20%)
6. Conclusions (10%)
7. References (5%)
8. Acknowledgments (2-3%)

### Visual-Text Balance

**Visual content ratio:**
- Text: 50-60%
- Figures: 25-35%
- Tables: 10-15%
- White space: 10-20%

**Figure placement:**
- Place figures near relevant text
- Group related figures together
- Use subfigures for comparisons
- Ensure figure captions are readable

## Accessibility

### Color Accessibility

**Contrast checker:**
- Use online tools: https://webaim.org/resources/contrastchecker/
- Ensure 4.5:1 ratio for normal text
- Ensure 3:1 ratio for large text

**Color blindness testing:**
- Use Coblis: https://www.color-blindness.com/coblis-color-blindness-simulator/
- Test with deuteranopia (most common)
- Avoid red-green combinations
- Use patterns or shapes in addition to color

### Visual Accessibility

**Font readability:**
- Minimum 24pt body text
- Sans-serif fonts preferred
- High contrast (black on white or dark blue on white)
- Avoid complex backgrounds

**Alt text:**
- Add descriptive alt text to figures
- Include key data points in alt text
- Describe trends and patterns
- Keep alt text concise

## Common Design Mistakes

### Typography Mistakes
- ❌ Font sizes too small (under 24pt body text)
- ❌ Too many different fonts (stick to 2-3 max)
- ❌ Italic text (hard to read from distance)
- ❌ All caps for body text
- ❌ Poor contrast between text and background

### Layout Mistakes
- ❌ No clear visual hierarchy
- ❌ Inconsistent spacing
- ❌ Too much text (over 1000 words)
- ❌ Cluttered design, no white space
- ❌ Content not flowing logically

### Color Mistakes
- ❌ Low contrast combinations
- ❌ Too many colors (stick to 2-4 main colors)
- ❌ Color schemes not accessible
- ❌ Red-green combinations (color blindness)
- ❌ Distracting or neon colors

### Content Mistakes
- ❌ No clear message or story
- ❌ Too much jargon
- ❌ Results without context
- ❌ Missing key findings
- ❌ References not cited properly

## Design Templates

### Scientific Research Poster Template

**Structure:**
```
┌─────────────────────────────────────────────┐
│  Title (72pt)                                │
│  Authors (36pt) | Affiliations (28pt)       │
│  Logos                                      │
├─────────┬─────────┬─────────┬───────────────┤
│         │         │         │               │
│ Intro   │ Methods │ Results │ Discussion    │
│ (15%)   │ (18%)   │ (30%)   │ (15%)         │
│         │         │         │               │
├─────────┴─────────┴─────────┴───────────────┤
│ Conclusions (12%) | References (10%)        │
│ Acknowledgments | Contact info              │
└─────────────────────────────────────────────┘
```

### Clinical Trial Poster Template

**Structure:**
```
┌─────────────────────────────────────────────┐
│  Trial Title                                │
│  Investigators | Institution                │
├─────────┬─────────┬─────────────────────────┤
│         │         │                         │
│ Study   │ Methods │ Results (large)         │
│ Design  │         │                         │
│         │         │                         │
├─────────┴─────────┴─────────────────────────┤
│ Conclusions | Clinical Implications         │
│ Safety Data | References                    │
└─────────────────────────────────────────────┘
```

### Literature Review Poster Template

**Structure:**
```
┌─────────────────────────────────────────────┐
│  Review Title                                │
│  Author | Institution                        │
├─────────────┬─────────────┬─────────────────┤
│             │             │                 │
│ Introduction │ Key Themes  │ Main Findings   │
│             │             │                 │
├─────────────┴─────────────┴─────────────────┤
│ Gaps | Future Research | References         │
└─────────────────────────────────────────────┘
```

## Pre-Print Checklist

### Design Review
- [ ] Title clearly visible from 6 feet
- [ ] Section headers readable from 4 feet
- [ ] Body text readable from 2 feet
- [ ] Colors have adequate contrast (4.5:1 minimum)
- [ ] Layout flows logically
- [ ] Spacing consistent throughout

### Content Review
- [ ] Total word count under 1000
- [ ] Key message clear in 30 seconds
- [ ] All sections present and complete
- [ ] Figures clear and relevant
- [ ] Tables properly formatted
- [ ] References accurate

### Technical Review
- [ ] PDF size matches requirements (check with pdfinfo)
- [ ] All fonts embedded
- [ ] Images ≥300 DPI
- [ ] No compilation warnings
- [ ] Page boundaries correct

### Accessibility Review
- [ ] Color contrast passes WCAG AA
- [ ] Tested with color blindness simulator
- [ ] Alt text provided for figures
- [ ] Fonts readable for visually impaired
