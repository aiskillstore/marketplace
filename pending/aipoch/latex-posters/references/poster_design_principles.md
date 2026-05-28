# Research Poster Design Principles

## Overview

Effective poster design balances visual appeal, readability, and scientific content. This guide covers typography, color theory, visual hierarchy, accessible design, and evidence-based research poster design principles.

## Core Design Principles

### 1. Visual Hierarchy

Guide viewers through content in logical order using size, color, position, and contrast.

**Hierarchy levels:**

1.  **Level 1 (Title)**: Largest, most prominent
    *   Font size: 72-120pt
    *   Position: Top center or spanning top
    *   Weight: Bold
    *   Purpose: Attract attention from 20 feet away

2.  **Level 2 (Column headers)**: Organize content
    *   Font size: 48-72pt
    *   Weight: Bold or Semi-bold
    *   Purpose: Section navigation, readable from 10 feet

3.  **Level 3 (Body)**: Main content
    *   Font size: Minimum 24-36pt
    *   Weight: Regular
    *   Purpose: Detailed information, readable from 4-6 feet

4.  **Level 4 (Captions, references)**: Supporting info
    *   Font size: 18-24pt
    *   Weight: Regular or Light
    *   Purpose: Background explanation and attribution

**Implementation:**
```latex
% Define hierarchy in LaTeX
\setbeamerfont{title}{size=\VeryHuge,series=\bfseries}        % 90pt+
\setbeamerfont{block title}{size=\Huge,series=\bfseries}      % 60pt
\setbeamerfont{block body}{size=\LARGE}                        % 30pt
\setbeamerfont{caption}{size=\large}                           % 24pt
```

### 2. White Space / Negative Space

White space is not wasted space—it enhances readability and directs attention.

**Functions of white space:**
*   **Breathing room**: Prevents audience feeling overwhelmed
*   **Grouping**: Shows which elements belong together
*   **Focus**: Draws attention to important elements
*   **Flow**: Creates visual paths through content

**Guidelines:**
*   Maintain at least 5-10% margins on all sides
*   Consistent spacing between blocks (1-2cm)
*   Space around figures should equal or exceed border width
*   Group related items tightly, separate unrelated items
*   Don't fill every inch—aim for 40-60% text coverage

**LaTeX implementation:**
```latex
% beamerposter spacing
\setbeamertemplate{block begin}{
  \vskip2ex  % Space before block
  ...
}

% tikzposter spacing
\documentclass[..., blockverticalspace=15mm, colspace=15mm]{tikzposter}

% Manual spacing
\vspace{2cm}  % Vertical spacing
hspace{1cm}  % Horizontal spacing
```

### 3. Alignment and Grid Systems

Proper alignment creates a professional, organized appearance.

**Alignment types:**
*   **Left-aligned text**: Most readable for body text (Western audiences)
*   **Center-aligned**: Section headers, titles, symmetric layouts
*   **Right-aligned**: Rarely used, only for special cases
*   **Justified**: Avoid (creates uneven spacing)

**Grid systems:**
*   **2-column**: Simple, traditional, good for narrative flow
*   **3-column**: Most common, balanced and versatile
*   **4-column**: Complex, information-dense, requires careful design
*   **Asymmetric**: Creative, modern, requires professional skill

**Best practices:**
*   Align block edges to invisible grid lines
*   Maintain consistent column widths (unless intentionally asymmetric)
*   Align similar elements (all figures, all text blocks)
*   Use consistent margins throughout

### 4. Visual Flow and Reading Patterns

Design based on natural eye movement and logical content progression.

**Common reading patterns:**

**Z-pattern (horizontal posters):**
```
Start → → → Top right
  ↓
Mid-left → → Middle
  ↓
Bottom-left → → → End
```

**F-pattern (vertical posters):**
```
Title → → → →
↓
Intro → →
↓
Methods
↓
Results → →
↓
Results (cont)
↓
Discussion
↓
Conclusions → →
```

**Gutenberg Diagram:**
```
Primary Area (top-left)     Strong Rest Area (top-right)
        ↓                      ↓
Weak Rest Area (bottom-left) Terminal Area (bottom-right)
```

**Implementation strategies:**
1. Place most important content in "hot zones" (top-left, center)
2. Use arrows, lines, or colors to create visual paths
3. Use numbering for sequential information (e.g., method steps)
4. Design left-to-right, top-to-bottom (for Western audiences)
5. Prominently place conclusions (bottom-right is natural endpoint)

## Typography

### Font Selection

**Recommended fonts:**

**Sans-serif (recommended for posters):**
*   **Helvetica**: Clean, professional, widely available
*   **Arial**: Similar to Helvetica, good compatibility
*   **Calibri**: Modern, friendly, readable
*   **Open Sans**: Contemporary style, excellent for web and print
*   **Roboto**: Modern, Google design, highly readable
*   **Lato**: Warm, professional, works well at various sizes

**Serif (use sparingly):**
*   **Times New Roman**: Traditional, formal
*   **Garamond**: Elegant, suitable for humanities
*   **Georgia**: Designed for screens, excellent readability

**Avoid:**
*   ❌ Comic Sans (unprofessional)
*   ❌ Decorative or handwritten fonts (unreadable from distance)
*   ❌ Mixing more than 2-3 font families

**LaTeX implementation:**
```latex
% Helvetica (sans-serif)
\usepackage{helvet}
\renewcommand{\familydefault}{\sfdefault}

% Arial-like
\usepackage{avant}
\renewcommand{\familydefault}{\sfdefault}

% Modern fonts with fontspec (requires LuaLaTeX/XeLaTeX)
\usepackage{fontspec}
\setmainfont{Helvetica Neue}
\setsansfont{Open Sans}
```

### Font Sizing

**Absolute minimum sizes** (readable from 4-6 feet):
*   Titles: 72pt+ (recommended 85-120pt)
*   Column headers: 48-72pt
*   Body: 24-36pt (recommended 30pt+)
*   Captions/small text: 18-24pt
*   References: Minimum 16-20pt

**Test readability:**
*   Print at 25% scale
*   Read from 2-3 feet away
*   If clearly readable, full-size poster will be readable from 8-12 feet

**Size reference:**
| LaTeX command | Approximate size | Use case |
|---------------|------------------|----------|
| `\tiny` | 10pt | Avoid in posters |
| `\small` | 16pt | Use sparingly |
| `\normalsize` | 20pt | References (when enlarged) |
| `\large` | 24pt | Captions, small text |
| `\Large` | 28pt | Body text (minimum) |
| `\LARGE` | 32pt | Body text (recommended) |
| `\huge` | 36pt | Subheadings |
| `\Huge` | 48pt | Column headers |
| `\VeryHuge` | 72pt+ | Titles |

### Text Formatting Best Practices

**Do:**
*   ✅ **Bold** for emphasis and headers
*   ✅ Short paragraphs (maximum 3-5 lines)
*   ✅ Use bullet point lists
*   ✅ Appropriate line spacing (1.2-1.5)
*   ✅ High contrast (dark text on light background)

**Avoid:**
*   ❌ Italics for distance reading (hard to read)
*   ❌ Long paragraphs in all caps (slow reading)
*   ❌ Underlining (outdated, interferes with descenders)
*   ❌ Long paragraphs (>6 lines)
*   ❌ Light text on light background

**Line spacing:**
```latex
% Increase line spacing for readability
\usepackage{setspace}
\setstretch{1.3}  % 1.3x normal spacing

% Or in specific blocks
\begin{spacing}{1.5}
  Text here with extra spacing
\end{spacing}
```

## Poster Color Theory

### Color Psychology and Meaning

Colors convey meaning and influence audience perception:

| Color | Associations | Use Cases |
|-------|--------------|-----------|
| **Blue** | Trust, professionalism, science | Academic, medical, technical |
| **Green** | Nature, health, growth | Environmental, biology, health |
| **Red** | Energy, urgency, passion | Attention-grabbing, warnings, bold statements |
| **Orange** | Creativity, enthusiasm | Innovation research, friendly approaches |
| **Purple** | Wisdom, creativity, luxury | Humanities, arts, high-end research |
| **Gray** | Neutral, professional, modern | Technology, minimalist design |
| **Yellow** | Optimism, attention, caution | Highlighting, energy, warning areas |

### Color Scheme Types

**1. Monochromatic**: Variations of a single hue
*   **Advantages**: Harmonious, professional, easy to implement
*   **Disadvantages**: Can be dull, lacks visual interest
*   **Use case**: Conservative conferences, institutional branding

```latex
% Monochromatic blue scheme
\definecolor{darkblue}{RGB}{0,51,102}
\definecolor{medblue}{RGB}{51,102,153}
\definecolor{lightblue}{RGB}{204,229,255}
```

**2. Analogous**: Colors adjacent on the color wheel
*   **Advantages**: Harmonious, visually comfortable
*   **Disadvantages**: Low contrast, may lack excitement
*   **Use case**: Nature/biology themes, smooth gradients

```latex
% Analogous blue-teal scheme
\definecolor{blue}{RGB}{0,102,204}
\definecolor{teal}{RGB}{0,153,153}
\definecolor{green}{RGB}{51,153,102}
```

**3. Complementary**: Colors opposite on the color wheel
*   **Advantages**: High contrast, vibrant, energetic
*   **Disadvantages**: Can cause visual fatigue if too intense
*   **Use case**: Attention-grabbing, modern designs

```latex
% Complementary blue-orange scheme
\definecolor{primary}{RGB}{0,71,171}     % Blue
\definecolor{accent}{RGB}{255,127,0}     % Orange
```

**4. Triadic**: Three colors evenly spaced
*   **Advantages**: Balanced, vibrant, visually rich
*   **Disadvantages**: Can appear cluttered without balance
*   **Use case**: Multi-topic posters, creative fields

```latex
% Triadic scheme
\definecolor{blue}{RGB}{0,102,204}
\definecolor{red}{RGB}{204,0,51}
\definecolor{yellow}{RGB}{255,204,0}
```

**5. Split-complementary**: Base color plus two colors adjacent to its complement
*   **Advantages**: High contrast but softer than pure complementary
*   **Disadvantages**: Difficult to balance
*   **Use case**: Complex designs, experienced designers

### High Contrast Combinations

Ensure sufficient contrast for readability:

**Excellent contrast (recommended):**
*   Dark blue on white
*   Black on white
*   White on dark blue/green/purple
*   Dark gray on light yellow
*   Black on light cyan

**Poor contrast (avoid):**
*   ❌ Green text on red background (colorblind issues)
*   ❌ Yellow text on white
*   ❌ Light gray on white
*   ❌ Blue text on black (hard to read)
*   ❌ Any pure colors stacked on each other

**Contrast ratio standards:**
*   Minimum: 4.5:1 (WCAG AA)
*   Recommended: 7:1 (WCAG AAA)
*   Test tool: https://webaim.org/resources/contrastchecker/

**LaTeX color contrast:**
```latex
% High contrast headers
\setbeamercolor{block title}{bg=black, fg=white}

% Medium contrast body
\setbeamercolor{block body}{bg=gray!10, fg=black}

% Manually check contrast or use online tools
```

### Colorblind-Friendly Palettes

Approximately 8% of males and 0.5% of females have color vision deficiencies.

**Safe color combinations:**
*   Blue + Orange (most universally distinguishable)
*   Blue + Yellow
*   Blue + Red
*   Purple + Green (use with caution)

**Avoid:**
*   ❌ Red + Green (most common colorblind confusion)
*   ❌ Green + Brown
*   ❌ Blue + Purple (may be problematic)
*   ❌ Light green + Yellow

**Recommended palettes:**

**IBM Colorblind Safe** (excellent accessibility):
```latex
\definecolor{ibmblue}{RGB}{100,143,255}
\definecolor{ibmmagenta}{RGB}{254,97,0}
\definecolor{ibmpurple}{RGB}{220,38,127}
\definecolor{ibmcyan}{RGB}{33,191,115}
```

**Okabe-Ito Palette** (scientifically tested):
```latex
\definecolor{okorange}{RGB}{230,159,0}
\definecolor{okskyblue}{RGB}{86,180,233}
\definecolor{okgreen}{RGB}{0,158,115}
\definecolor{okyellow}{RGB}{240,228,66}
\definecolor{okblue}{RGB}{0,114,178}
\definecolor{okvermillion}{RGB}{213,94,0}
\definecolor{okpurple}{RGB}{204,121,167}
```

**Paul Tol's Bright Palette:**
```latex
\definecolor{tolblue}{RGB}{68,119,170}
\definecolor{tolred}{RGB}{204,102,119}
\definecolor{tolgreen}{RGB}{34,136,51}
\definecolor{tolyellow}{RGB}{238,221,136}
\definecolor{tolcyan}{RGB}{102,204,238}
```

### Institutional Branding

Match university or department colors:

```latex
% Example: Stanford colors
\definecolor{stanford-red}{RGB}{140,21,21}
\definecolor{stanford-gray}{RGB}{83,86,90}

% Example: MIT colors
\definecolor{mit-red}{RGB}{163,31,52}
\definecolor{mit-gray}{RGB}{138,139,140}

% Example: Cambridge colors
\definecolor{cambridge-blue}{RGB}{163,193,173}
\definecolor{cambridge-lblue}{RGB}{212,239,223}
```

## Accessible Design Considerations

### Universal Design Principles

Design posters usable by the widest possible audience:

**1. Visual accessibility:**
*   High contrast text (minimum 4.5:1 ratio)
*   Large fonts (body 24pt+)
*   Colorblind-safe palettes
*   Clear visual hierarchy
*   Avoid conveying information by color alone

**2. Cognitive accessibility:**
*   Clear, simple language
*   Logical, organized content
*   Consistent layout
*   Use visual cues for navigation (arrows, numbering)
*   Avoid clutter and information overload

**3. Physical accessibility:**
*   Place core content at wheelchair-accessible height (3-5 feet)
*   Provide QR codes pointing to electronic versions
*   Provide paper handouts for close-up viewing
*   Consider lighting and glare when selecting poster material

### Alt Text and Descriptions

Make posters accessible to screen readers (for electronic versions):

```latex
% Add alt text to images
includegraphics[width=\linewidth]{figure.pdf}
% Alternative: include detailed captions
\caption{Bar chart showing mean treatment outcomes ± standard deviation.
Control group (blue): 45±5\%; Treatment group (orange): 78±6\%.
Asterisks indicate significance: *p<0.05, **p<0.01.}
```

### Multimodal Information

Don't rely on a single sensory channel:

**Use redundant coding:**
*   Color + shape (don't just use color to categorize)
*   Color + pattern (hatching, dots)
*   Color + labels (add text labels to chart elements)
*   Text + icons (visual + verbal)

**Example:**
```latex
% Recommended: color + shape + labels
\begin{tikzpicture}
  \draw[fill=blue, circle] (0,0) circle (0.3) node[right] {Males: 45\%};
  \draw[fill=red, rectangle] (0,-1) rectangle (0.6,-0.4) node[right] {Females: 55\%};
\end{tikzpicture}


### Rule of Thirds

```

## Layout CompositionDivide poster into 3×3 grid; place key elements at intersection points:

```
+-----+-----+-----+
|  ×  |     |  ×  |  ← Top third (title, logos)
+-----+-----+-----+
|     |  ×  |     |  ← Middle third (core content)
+-----+-----+-----+
|  ×  |     |  ×  |  ← Bottom third (conclusions)
+-----+-----+-----+
  ↑           ↑
 Left        Right
```

**Power points** (intersections):
*   Top-left: Starting point for main columns
*   Top-right: Logo, QR code
*   Center: Key figure or main results
*   Bottom-right: Conclusions, contact info

### Balance and Symmetry

**Symmetrical layouts:**
*   Formal, traditional, stable
*   Easy to design
*   May seem stiff or boring
*   Suitable for conservative audiences

**Asymmetrical layouts:**
*   Dynamic, modern, interesting
*   Harder to execute perfectly
*   More visually engaging
*   Suitable for creative fields

**Visual weight balancing:**
*   Large elements = heavy visual weight
*   Dark colors = heavy visual weight
*   Dense text = heavy visual weight
*   Distribute weight evenly across poster

### Proximity and Grouping

**Gestalt principles:**

**Proximity**: Items close together are perceived as related
```
[Introduction]       [Methods]

[Results]            [Discussion]
```

**Similarity**: Similar items are perceived as a group
*   Use consistent colors for related columns
*   Use same border style for similar content types

**Continuity**: Eyes follow lines and paths
*   Use arrows to guide through methods section
*   Align elements to create invisible lines

**Closure**: Brain automatically completes incomplete shapes
*   Use partial borders for grouping without fully enclosing

## Visual Elements

### Icons and Graphics

Strategically use icons to enhance understanding:

**Benefits:**
*   Universal language (crosses language barriers)
*   Faster processing than text
*   Adds visual interest
*   Clarifies concepts

**Best practices:**
*   Use consistent style (all line, all filled, or all flat)
*   Appropriate size (typically 1-3cm)
*   Label ambiguous icons
*   Resources: Font Awesome, Noun Project, academic icon sets

**LaTeX implementation:**
```latex
% Font Awesome icons
\usepackage{fontawesome5}
\faFlask{} Methods \quad \faChartBar{} Results

% Custom icons with TikZ
\begin{tikzpicture}
  \node[circle, draw, thick, minimum size=1cm] {\Huge \faAtom};
\end{tikzpicture}
```

### Borders and Lines

**Use borders to:**
*   Define areas
*   Group related content
*   Add visual interest
*   Match institutional branding

**Border styles:**
*   Solid: Traditional, formal
*   Dashed: Informal, secondary info
*   Rounded: Friendly, modern
*   Shadowed: Depth, modern (use sparingly)

**Guidelines:**
*   Maintain consistent width (typically 2-5pt)
*   Use moderately (not every element needs borders)
*   Border color should match content or theme
*   Ensure adequate white space (padding) inside borders

```latex
% tikzposter borders
\usecolorstyle{Denmark}
\tikzposterlatexaffectionproofoff  % Remove bottom-right logo

% Custom border style
\defineblockstyle{CustomBlock}{
  titlewidthscale=1, bodywidthscale=1, titleleft,
  titleoffsetx=0pt, titleoffsety=0pt, bodyoffsetx=0pt, bodyoffsety=0pt,
  bodyverticalshift=0pt, roundedcorners=10, linewidth=2pt,
  titleinnersep=8mm, bodyinnersep=8mm
}{
  \draw[draw=blocktitlebgcolor, fill=blockbodybgcolor, 
        rounded corners=\blockroundedcorners, line width=\blocklinewidth]
       (blockbody.south west) rectangle (blocktitle.north east);
}
```

### Backgrounds and Textures

**Background options:**

**Solid colors (recommended):**
*   White or very light colors
*   Maximum readability
*   Professional
*   Print-friendly

**Gradients:**
*   Subtle gradients are acceptable
*   Top-to-bottom or radial
*   Avoid strong contrasts that interfere with text

**Textures:**
*   Only very subtle textures
*   Watermarks of logos or molecules (5-10% opacity)
*   Avoid patterns that create visual noise

**Avoid:**
*   ❌ Cluttered backgrounds
*   ❌ Images behind text
*   ❌ High contrast backgrounds
*   ❌ Repetitive patterns that cause visual artifacts

```latex
% Gradient background in tikzposter
\documentclass{tikzposter}
\definecolorstyle{GradientStyle}{
  % ...color definitions...
}{
  \colorlet{backgroundcolor}{white!90!blue}
  \colorlet{framecolor}{white!70!blue}
}

% Watermark
\usepackage{tikz}
AddToShipoutPictureBG{
  \AtPageCenter{
    \includegraphics[width=0.5\paperwidth,opacity=0.05]{university-seal.pdf}
  }
}
```

## Common Design Mistakes

### Critical Errors

**1. Too much text** (most common mistake)
*   ❌ Over 1000 words
*   ❌ Long paragraphs (>5 lines)
*   ❌ Reducing font size to fit more content
*   ✅ Solution: Ruthless cutting, use bullets, focus on core message

**2. Poor contrast**
*   ❌ Light text on light background
*   ❌ Colored text on colored background
*   ✅ Solution: Dark on light or light on dark, test contrast ratios

**3. Font too small**
*   ❌ Body text smaller than 24pt
*   ❌ Trying to fit full paper content
*   ✅ Solution: Body 30pt+, highlight key findings only

**4. Cramped layout**
*   ❌ No white space
*   ❌ Elements flush with edges
*   ❌ Random placement
*   ✅ Solution: Generous margins, grid alignment, intentional white space

**5. Inconsistent style**
*   ❌ Multiple font families
*   ❌ Varied header styles
*   ❌ Elements misaligned
*   ✅ Solution: Define style guide, use templates, align to grid

### Moderate Issues

**6. Poor figure quality**
*   ❌ Pixelated images (<300 DPI)
*   ❌ Tiny axis labels
*   ❌ Unreadable legends
*   ✅ Solution: Vector graphics (PDF/SVG), large labels, clear legends

**7. Color overload**
*   ❌ Too many colors (>5 different hues)
*   ❌ Neon or oversaturated colors
*   ✅ Solution: Limit to 2-3 main colors, use shade/tint variations

**8. Ignoring visual hierarchy**
*   ❌ All text same size
*   ❌ No clear entry point
*   ✅ Solution: Significant size differences, clear headers, visual guides

**9. Information overload**
*   ❌ Trying to show everything
*   ❌ Too many figures
*   ✅ Solution: Show 3-5 key results, link to full paper via QR code

**10. Poor typography**
*   ❌ Justified text (uneven spacing)
*   ❌ All caps body text
*   ❌ Random mixing of serif and sans-serif
*   ✅ Solution: Left-align body, use sentence case, consistent fonts

## Design Checklist

### Pre-Print Checks

*   [ ] Title clearly visible from 20 feet
*   [ ] Body text at least 24pt, ideally 30pt+
*   [ ] High contrast throughout (minimum 4.5:1)
*   [ ] Colorblind-friendly palette
*   [ ] Total word count under 800 words
*   [ ] White space around all elements
*   [ ] Consistent alignment and spacing
*   [ ] All figures high resolution (300+ DPI)
*   [ ] Figure labels readable (minimum 18pt+)
*   [ ] No orphaned text or awkward line breaks
*   [ ] Contact information included
*   [ ] QR codes tested and working
*   [ ] Consistent font usage (max 2-3 families)
*   [ ] All abbreviations defined
*   [ ] Correct institutional branding/logos
*   [ ] Test print at 25% scale to check readability

### Content Review

*   [ ] Clear narrative arc (problem → methods → findings → impact)
*   [ ] 1-3 main messages clearly communicated
*   [ ] Methods concise but reproducible
*   [ ] Results visually presented (not just text)
*   [ ] Conclusions clear and actionable
*   [ ] References properly cited
*   [ ] No spelling or grammar errors
*   [ ] Figures have descriptive captions
*   [ ] Data visualizations clear and honest
*   [ ] Statistical significance properly indicated

## Evidence-Based Design Suggestions

Research on poster effectiveness shows:

**Key findings:**
1.  **Viewers spend an average of 3-5 minutes per poster**
    *   Design for quick scanning, not deep reading
    *   Most important info must be immediately visible

2.  **Visual content is processed 60,000 times faster than text**
    *   Use figures not paragraphs for key findings
    *   Images grab attention first

3.  **High contrast improves recall by 40%**
    *   Light backgrounds with dark text outperform dark on light
    *   Color contrast aids memory retention

4.  **White space improves comprehension by 20%**
    *   Don't fear empty space
    *   Margins and padding are crucial

5.  **Three-column layout is most effective for vertical posters**
    *   Visual weight balance
    *   Natural reading flow

6.  **QR codes can increase engagement by 30%**
    *   Provide electronic access to full paper
    *   Link to videos, code repositories, data

## Resources and Tools

### Color Tools
*   **Coolors.co**: Generate color schemes
*   **Adobe Color**: Color wheel and accessibility checker
*   **ColorBrewer**: Scientific visualization colors
*   **WebAIM Contrast Checker**: Test contrast ratios

### Design Resources
*   **Canva**: Poster templates and inspiration
*   **Figma**: Design prototyping before LaTeX
*   **Noun Project**: Icons and graphics
*   **Font Awesome**: Icon font for LaTeX

### Testing Tools
*   **Coblis**: Colorblind simulator
*   **Vischeck**: Another colorblind checker
*   **Accessibility Checker**: WCAG compliance check

### LaTeX Packages
*   `xcolor`: Extended color support
*   `tcolorbox`: Colored boxes and frames
*   `fontawesome5`: Icon font
*   `qrcode`: QR code generation
*   `tikz`: Custom graphics

## Conclusion

Effective poster design balances aesthetics, readability, and scientific content. Follow these core principles:

1.  **Less is more**: Prioritize core message over comprehensive details
2.  **Size matters**: Make text large enough for distance reading
3.  **Contrast is key**: Ensure all text is highly legible
4.  **Accessibility first**: Design for diverse audiences
5.  **Visual hierarchy**: Guide viewers logically through content
6.  **Test early**: Print at reduced scale and gather feedback

Remember: Your poster is an advertisement for your research and the start of a conversation—not a substitute for reading the full paper.
