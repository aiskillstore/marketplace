# CSR Real Estate Brand Style Guide

## Brand Overview

**Company:** CSR Real Estate LLC
**Tagline:** Built on Legacy
**Established:** 2025
**Location:** Miami, FL
**Industry:** Real Estate Development

---

## Color Palette

### Primary Colors

| Color Name | Hex | RGB | Usage |
|------------|-----|-----|-------|
| **CSR Cream** | `#EDEAE3` | `rgb(237, 234, 227)` | Primary backgrounds, cards, header |
| **CSR Dark Blue** | `#07254B` | `rgb(7, 37, 75)` | Text, headings, footer, primary CTAs |

### Accent Colors

| Color Name | Hex | RGB | Usage |
|------------|-----|-----|-------|
| **CSR Light Blue** | `#B4C1D1` | `rgb(180, 193, 209)` | Hover states, labels, secondary accents |

### Color Swatches

```
┌─────────────────────────────────────────────────────────────────┐
│  CSR Cream          │  CSR Dark Blue       │  CSR Light Blue    │
│  #EDEAE3            │  #07254B             │  #B4C1D1           │
│  ████████████████   │  ████████████████    │  ████████████████  │
│  Backgrounds        │  Text & Headings     │  Accents           │
└─────────────────────────────────────────────────────────────────┘
```

### Color Usage Guidelines

**DO:**
- Use Dark Blue for all body text and headings
- Use Cream for backgrounds and card surfaces
- Use Light Blue sparingly for hover effects and labels
- Maintain high contrast for accessibility

**DON'T:**
- Use Light Blue for body text (low contrast)
- Mix multiple background colors on the same page
- Use colors outside the palette without approval

---

## Typography

### Primary Font

**Manrope** (Google Fonts)
https://fonts.google.com/specimen/Manrope

### Font Weights

| Weight | Name | Usage |
|--------|------|-------|
| 300 | Light | Headings, display text |
| 400 | Regular | Body text (minimal use) |
| 700 | Bold | Labels, CTAs, emphasis |

### Type Scale

| Element | Mobile | Desktop | Style |
|---------|--------|---------|-------|
| H1 (Hero) | 3rem (48px) | 9rem (144px) | font-light tracking-tighter leading-[0.9] |
| H2 (Section) | 2.25rem (36px) | 3rem (48px) | font-light |
| H3 (Card Title) | 1.25rem (20px) | 1.25rem (20px) | font-light |
| Body | 1.125rem (18px) | 1.125rem (18px) | font-light leading-relaxed |
| Label | 0.75rem (12px) | 0.75rem (12px) | font-bold uppercase tracking-widest |
| Caption | 0.625rem (10px) | 0.625rem (10px) | font-bold uppercase tracking-widest opacity-40 |

### Typography Examples

**H1 - Hero Headlines**
```
Built on
Legacy.
```
*Style: text-5xl md:text-9xl font-light tracking-tighter*

**H2 - Section Titles**
```
Selected Works
```
*Style: text-4xl md:text-5xl font-light*

**Body Text**
```
CSR acquires and develops real estate assets that create
long-term value for communities in Miami and beyond.
```
*Style: text-lg font-light leading-relaxed text-csr-darkBlue/80*

**Labels**
```
REAL ESTATE DEVELOPMENT
```
*Style: text-xs font-bold uppercase tracking-widest*

---

## Logo

### Primary Logo

The CSR logo consists of:
- **Letterforms:** "CSR" in a custom serif typeface
- **Accent:** Light blue curved element above the "S"

### Logo Colors

| Context | Primary | Accent |
|---------|---------|--------|
| Light backgrounds | Dark Blue (#07254B) | Light Blue (#B4C1D1) |
| Dark backgrounds | Cream (#EDEAE3) | Light Blue (#B4C1D1) |

### Clear Space

Maintain minimum clear space equal to the height of the "C" on all sides.

### Minimum Sizes

- **Digital:** 80px width minimum
- **Print:** 1 inch width minimum

### Logo Files

- `/assets/images/csr-logo.svg` - Primary SVG (scalable)

---

## Imagery

### Photography Style

**Aesthetic:** Professional, sophisticated architectural photography

**Subjects:**
- Modern buildings and developments
- Miami skyline and cityscapes
- Luxury interiors and finishes
- Construction and development progress
- Urban landscapes

### Image Treatments

**Default Treatment:**
1. Subtle grayscale filter (20%)
2. Dark blue overlay (10% opacity, mix-blend-multiply)

**CSS Implementation:**
```css
.image-treatment {
    filter: grayscale(20%);
}
.image-overlay {
    background-color: rgba(7, 37, 75, 0.1);
    mix-blend-mode: multiply;
}
```

### Aspect Ratios

| Context | Ratio | Example Size |
|---------|-------|--------------|
| Hero/Video | 16:9 | 1920 × 1080 |
| Portfolio Cards | 4:5 | 800 × 1000 |
| Team Photos | 1:1 | 600 × 600 |
| Property Hero | Full height | 2000 × 1125 |

### Stock Photo Search Terms

- "miami architecture modern"
- "luxury real estate development"
- "miami skyline dusk"
- "modern office building"
- "construction progress aerial"
- "luxury interior minimal"

---

## Voice & Tone

### Brand Personality

| Attribute | Description |
|-----------|-------------|
| **Professional** | Expertise and competence in every communication |
| **Sophisticated** | Refined language without being pretentious |
| **Trustworthy** | Honest, transparent, reliable |
| **Visionary** | Forward-thinking, innovative perspective |

### Tone Guidelines

**Overall Tone:** Confident but not arrogant, elegant but accessible

### Writing Examples

**DO:**
```
"CSR acquires and develops real estate assets that create
long-term value for communities in Miami and beyond."

"Built on Legacy."

"Elevating the standard of living through thoughtful design."
```

**DON'T:**
```
"We're the BEST real estate company in Miami!!"

"Click here to learn more about our awesome properties!"

"Don't miss out on these incredible deals!"
```

### Voice Principles

1. **Be concise** - Every word should earn its place
2. **Be specific** - Use concrete details, not vague claims
3. **Be confident** - State facts directly without hedging
4. **Be respectful** - Treat the reader as intelligent and informed

---

## Responsive Design

### Breakpoints

| Name | Width | Tailwind | Usage |
|------|-------|----------|-------|
| Mobile | < 768px | Default | Phones, small tablets |
| Tablet | 768px - 1023px | `md:` | Tablets, small laptops |
| Desktop | ≥ 1024px | `lg:` | Laptops, desktops |

### Component Behaviors

**Navigation:**
- Mobile: Hamburger menu with full-screen overlay
- Desktop: Minimal header with logo and hamburger

**Hero Section:**
- Mobile: Stacked (content above video)
- Desktop: Side-by-side split (40% content / 60% video)

**Portfolio Grid:**
- Mobile: Single column
- Tablet: 2 columns
- Desktop: 3 columns with offset middle card

**Footer:**
- Mobile: Single column, stacked sections
- Desktop: 4-column grid

### Content Max Width

- **Max width:** 1400px
- **Side padding:** 24px (mobile) / 64px (desktop)

```css
.container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 0 1.5rem; /* 24px */
}

@media (min-width: 768px) {
    .container {
        padding: 0 4rem; /* 64px */
    }
}
```

---

## UI Components

### Buttons

**Primary CTA (Text Link Style):**
```html
<a class="group flex items-center gap-4 text-xs font-bold uppercase tracking-widest">
    <span>Our Projects</span>
    <span class="block w-8 h-px bg-csr-darkBlue group-hover:w-16 transition-all duration-500"></span>
</a>
```

**Status Badges:**
```html
<!-- Active -->
<span class="bg-emerald-500 text-white text-[10px] font-bold px-3 py-1 uppercase tracking-widest">
    Active
</span>

<!-- Development -->
<span class="bg-amber-500 text-white text-[10px] font-bold px-3 py-1 uppercase tracking-widest">
    Development
</span>

<!-- Sold/Completed -->
<span class="bg-csr-darkBlue text-csr-cream text-[10px] font-bold px-3 py-1 uppercase tracking-widest">
    Sold
</span>
```

### Cards

**Portfolio Card:**
- Aspect ratio: 4:5
- Image with status badge overlay (top-left)
- Title below image
- Location as caption

### Forms

- Minimal styling
- Dark blue text on cream background
- Thin bottom border on inputs
- Uppercase labels

---

## Animation Guidelines

### Principles

1. **Subtle** - Animations enhance, never distract
2. **Purposeful** - Every animation serves a function
3. **Fast** - Quick transitions (300-500ms)

### Standard Timings

| Type | Duration | Easing |
|------|----------|--------|
| Hover | 300ms | ease |
| Page transition | 500ms | ease-out |
| Scroll reveal | 800ms | ease-out |

### Common Animations

**Fade Up (scroll reveal):**
```css
.hero-text {
    opacity: 0;
    transform: translateY(32px);
    transition: opacity 0.8s ease-out, transform 0.8s ease-out;
}
.hero-text.visible {
    opacity: 1;
    transform: translateY(0);
}
```

**Line Expand:**
```css
.line-reveal {
    transform: scaleX(0);
    transform-origin: left;
    transition: transform 0.8s ease-out;
}
.line-reveal.visible {
    transform: scaleX(1);
}
```

---

## File Reference

| Asset | Path |
|-------|------|
| Logo (SVG) | `/assets/images/csr-logo.svg` |
| Hero Video | `/assets/video/hero-video.mp4` |
| Animations JS | `/assets/js/csr-animations.js` |
| Main Stylesheet | `/style.css` |

---

*Last Updated: December 2025*
*Version: 1.0*
