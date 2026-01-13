# Visual Identity Specifications

Complete technical specifications for all brand visual elements.

## Logo Specifications

### Logo Variations

Every brand should define:
- **Primary logo** (full-color version)
- **Secondary logo** (single-color or monochrome)
- **Logo icon/symbol** (standalone mark)
- **Horizontal and vertical lockups**
- **Reversed/inverse versions** (for dark backgrounds)

### Logo Usage Rules

**Clear Space:**
Define minimum clear space around the logo to prevent visual clutter:
```
Minimum clear space = X (where X is typically the height of a logo element)
Example: If logo height = 50px, maintain 50px clear space on all sides
```

**Minimum Size:**
```
Print: Minimum width of 0.75 inches (1.9 cm)
Digital: Minimum width of 120 pixels
Icon only: Minimum 32x32 pixels for digital
```

**Color Variations:**
- Primary: Full-color version on white/light backgrounds
- Black: 100% black for single-color printing
- White: Reversed version for dark backgrounds
- Grayscale: For black-and-white reproduction

**Don'ts:**
- Do not stretch, skew, or distort the logo
- Do not rotate the logo
- Do not change logo colors
- Do not add effects (drop shadows, gradients, outlines)
- Do not place logo on busy backgrounds
- Do not recreate or alter the logo elements

## Color System

### Color Palette Structure

**Primary Colors:** The main brand colors used most frequently (typically 1-3 colors)
**Secondary Colors:** Supporting colors that complement the primary palette (2-5 colors)
**Accent Colors:** Used sparingly for emphasis, calls-to-action, or highlights (1-3 colors)
**Neutral Colors:** Grays, blacks, and whites for backgrounds and text

### Color Specification Format

For each color, provide:
```
Color Name: Brand Blue
Pantone: PMS 2945 C
CMYK: 100/45/0/0 (for print)
RGB: 0/114/206 (for screen)
HEX: #0072CE (for web)
HSL: 207°/100%/40% (alternative web format)

Usage: Primary brand color, use for headers, CTAs, key elements
Accessibility: AAA compliant at 18pt+ on white, AA compliant at all sizes
```

### Color Usage Guidelines

**Ratios and Proportions:**
```
Primary colors: 60% of design
Secondary colors: 30% of design
Accent colors: 10% of design
```

**Backgrounds:**
- Light backgrounds: Use dark text (minimum 4.5:1 contrast ratio)
- Dark backgrounds: Use light text (minimum 4.5:1 contrast ratio)
- Brand color backgrounds: Test contrast for all text

**Accessibility Requirements:**
- **WCAG AA compliance:** 4.5:1 contrast ratio for normal text (minimum)
- **WCAG AAA compliance:** 7:1 contrast ratio for normal text (preferred)
- **Large text (18pt+):** 3:1 minimum contrast ratio
- Test all color combinations for readability

## Typography

### Font Families

**Primary Typeface:**
```
Family: Helvetica Neue
Weights: Light (300), Regular (400), Medium (500), Bold (700)
Usage: Headings, subheadings, body text
License: Commercial license required
Fallback: Arial, sans-serif
```

**Secondary Typeface:**
```
Family: Georgia
Weights: Regular (400), Bold (700)
Usage: Pull quotes, callouts, editorial content
License: System font
Fallback: Times New Roman, serif
```

**Monospace Typeface:**
```
Family: Courier New
Usage: Code snippets, technical documentation
Fallback: Courier, monospace
```

### Typography Hierarchy

**Heading Scale:**
```
H1: 48px/3rem, Bold (700), 1.2 line-height, 0.02em letter-spacing
H2: 36px/2.25rem, Bold (700), 1.3 line-height
H3: 28px/1.75rem, Medium (500), 1.3 line-height
H4: 24px/1.5rem, Medium (500), 1.4 line-height
H5: 20px/1.25rem, Regular (400), 1.4 line-height
H6: 16px/1rem, Regular (400), 1.5 line-height
```

**Body Text:**
```
Paragraph: 16px/1rem, Regular (400), 1.6 line-height
Small text: 14px/0.875rem, Regular (400), 1.5 line-height
Caption: 12px/0.75rem, Regular (400), 1.4 line-height
```

**Specialty Text:**
```
Button text: 16px/1rem, Medium (500), Uppercase, 0.05em letter-spacing
Link text: 16px/1rem, Regular (400), Underline on hover
Pull quote: 24px/1.5rem, Bold (700), 1.4 line-height, Italic
```

### Typography Best Practices

**Line Length:**
- Optimal: 45-75 characters per line
- Maximum: 90 characters per line
- Minimum: 35 characters per line

**Spacing:**
```
Paragraph spacing: 1em (equal to font size)
Section spacing: 2-3em
Heading margin-top: 1.5-2em
Heading margin-bottom: 0.5-0.75em
```

**Alignment:**
- Body text: Left-aligned (preferred for readability)
- Headings: Left-aligned or center-aligned
- Avoid: Justified text (creates uneven spacing)
- Use sparingly: Right-aligned text (for special cases)

## Iconography and Imagery

### Icon Style

**Visual Characteristics:**
```
Style: Line icons (outlined)
Weight: 2px stroke
Corner radius: 2px rounded
Grid: 24x24 pixel base grid
Padding: 2px internal padding
Color: Brand primary or neutral dark
```

**Icon Usage:**
- Use consistently throughout all materials
- Maintain consistent stroke weight
- Align icons to grid for pixel-perfect rendering
- Use single color (no gradients in icons)
- Ensure icons scale well at different sizes

### Photography Guidelines

**Style Characteristics:**
```
Composition: Natural, authentic, diverse
Lighting: Bright, natural light preferred
Color treatment: Vibrant, true-to-life colors
Mood: Professional yet approachable
Subjects: Real people, real situations (avoid stock photo clichés)
```

**Technical Requirements:**
```
Resolution: Minimum 300 DPI for print
Format: JPEG for photos, PNG for transparency
Color space: sRGB for web, CMYK for print
Aspect ratios: 16:9, 4:3, 1:1 (depending on use)
```

**Image Overlays:**
When placing text over images:
```
Option 1: Apply 40-60% dark overlay (multiply blend mode)
Option 2: Add gradient overlay (dark to transparent)
Option 3: Use image area with low detail/contrast
Ensure: Minimum 4.5:1 text contrast ratio
```

## Spacing and Layout

### Spacing System

**Base Unit: 8px**

```
Scale:
4px (0.25rem) - Tight spacing
8px (0.5rem) - Base unit
16px (1rem) - Comfortable spacing
24px (1.5rem) - Section spacing
32px (2rem) - Large spacing
48px (3rem) - Extra-large spacing
64px (4rem) - Component spacing
96px (6rem) - Section divider
```

**Application:**
- Use multiples of 8px for all margins and padding
- Maintain consistent spacing patterns
- Increase spacing for visual hierarchy
- Reduce spacing to show relationship

### Grid System

**Desktop Layout:**
```
Columns: 12-column grid
Gutter: 24px
Margin: 48px (left and right)
Max width: 1200px
Breakpoint: 1024px and up
```

**Tablet Layout:**
```
Columns: 8-column grid
Gutter: 16px
Margin: 32px
Max width: 768px
Breakpoint: 768px - 1023px
```

**Mobile Layout:**
```
Columns: 4-column grid
Gutter: 16px
Margin: 16px
Max width: 100%
Breakpoint: 0px - 767px
```
