---
name: art-style-creator
description: Create and define visual art styles for projects. Use when user wants to establish an art direction, create a style guide, define visual language, document aesthetic choices, or create consistent artwork guidelines for games, illustrations, animations, or other visual media.
---

# Art Style Creator

This skill guides the creation of comprehensive art style definitions for visual projects.

## Workflow

### Step 1: Vision & Context

Gather project context:
1. **Project type**: Game, illustration, animation, UI, branding
2. **Target audience**: Age group, cultural context
3. **Vision statement**: 2-3 sentences describing the visual direction
4. **Key words**: 5-7 words capturing the style essence
5. **Primary influences**: Reference styles, artists, or works

### Step 2: Color Palette

Define the color system. See [color-theory.md](references/color-theory.md) for detailed guidance.

Ask for:
- **Palette type**: Monochromatic, analogous, complementary, triadic, etc.
- **Dominant color** (60%): Background, large areas
- **Secondary color** (30%): Supporting elements
- **Accent color** (10%): Highlights, focal points
- **Mood alignment**: Match colors to intended emotion
- **Forbidden colors**: Colors to avoid and why

### Step 3: Line Work

Establish line characteristics. See [line-and-shape.md](references/line-and-shape.md) for details.

Define:
- **Outline approach**: Full / Partial / None / Color holds
- **Base weight**: Thin / Medium / Thick (with pixel/pt measurement)
- **Quality**: Clean / Sketchy / Geometric / Organic / Calligraphic
- **Weight variation**: Different weights for FG/MG/BG
- **Line color**: Black / Dark local color / Color holds

### Step 4: Shape Language

Define shape characteristics. See [line-and-shape.md](references/line-and-shape.md).

Specify:
- **Dominant shape**: Circle (friendly), Square (stable), Triangle (dynamic)
- **Complexity level**: Simple / Moderate / Complex
- **Edge treatment**: Sharp / Rounded / Mixed
- **Character shapes**: Heroes, villains, NPCs
- **Environment shapes**: Architecture, nature, props
- **Silhouette priority**: High / Medium / Low

### Step 5: Composition

Set layout rules. See [composition-lighting.md](references/composition-lighting.md).

Define:
- **Framing system**: Rule of thirds / Golden ratio / Center-focused / Dynamic
- **Symmetry preference**: Symmetric / Asymmetric / Varied
- **Depth approach**: FG/MG/BG presence and treatment
- **Perspective type**: 1-point / 2-point / 3-point / Isometric
- **Visual hierarchy**: Primary method (size/contrast/color/position)
- **Negative space**: Minimal / Moderate / Abundant

### Step 6: Lighting & Atmosphere

Define lighting style. See [composition-lighting.md](references/composition-lighting.md).

Specify:
- **Overall brightness**: Dark / Dim / Neutral / Bright
- **Contrast level**: Low / Medium / High / Extreme
- **Shadow rendering**: Gradient / Cel-shaded / Hatched / Minimal / None
- **Primary light direction**: Front / Side / Back / Top / Variable
- **Light hardness**: Soft / Medium / Hard
- **Shadow color**: Black / Colored / Complementary
- **Atmospheric effects**: Fog, particles, god rays

### Step 7: Texture & Detail

Set detail approach. See [texture-mood.md](references/texture-mood.md).

Define:
- **Detail level**: Minimal / Low / Medium / High / Photorealistic
- **Texture rendering**: Painted / Photo / Procedural / Flat / Stylized
- **Detail distribution**: High detail for focus, low for background
- **Surface treatments**: How to handle different materials
- **Aging/weathering**: None / Subtle / Visible / Heavy
- **Noise/grain**: None / Subtle / Visible

### Step 8: Mood & Tone

Establish emotional baseline. See [texture-mood.md](references/texture-mood.md).

Specify:
- **Core emotion**: Joy, sadness, fear, tension, peace, mystery, etc.
- **Intensity**: Subtle / Moderate / Strong
- **Tone position**: Light ↔ Dark spectrum
- **Energy level**: Calm / Moderate / Energetic
- **Genre alignment**: Fantasy, sci-fi, horror, noir, etc.
- **Elements to avoid**: What would break the mood

### Step 9: Technical Specs

Document technical requirements. See [technical-specs.md](references/technical-specs.md).

Define:
- **Working resolution**: Dimensions at DPI
- **Export resolution**: Final output specs
- **Color mode**: RGB / CMYK / Indexed
- **File formats**: Working and export formats
- **Asset sizes**: Characters, environments, UI elements, icons

### Step 10: Generate Style Document

Output the complete art style definition using the template below.

---

## Output Template

```markdown
# [PROJECT NAME] — Art Style Guide

## Overview
**Project**: [Name]
**Style Name**: [Unique identifier]
**Version**: 1.0

### Vision Statement
[2-3 sentences describing the visual vision]

### Key Words
[5-7 words capturing the essence]

---

## 1. Color Palette

### Primary Palette
| Role | Color | Hex | Usage |
|------|-------|-----|-------|
| Dominant | [Name] | #XXXXXX | [60% - backgrounds, large areas] |
| Secondary | [Name] | #XXXXXX | [30% - supporting elements] |
| Accent | [Name] | #XXXXXX | [10% - highlights, CTAs] |

### Extended Palette
- Highlight: #XXXXXX
- Shadow: #XXXXXX
- Neutrals: #XXXXXX, #XXXXXX

### Color Rules
- [Rule 1]
- [Rule 2]

### Forbidden Colors
- [Color]: [Reason]

---

## 2. Line Work

- **Outline**: [Full/Partial/None/Color holds]
- **Base weight**: [Thin/Medium/Thick] at [X px at Y resolution]
- **Quality**: [Clean/Sketchy/Geometric/Organic]
- **FG weight**: [Weight]
- **BG weight**: [Weight]
- **Line color**: [Black/Colored/Color holds]

---

## 3. Shape Language

- **Dominant shape**: [Circle/Square/Triangle/Mixed]
- **Complexity**: [Simple/Moderate/Complex]
- **Edges**: [Sharp/Rounded/Mixed]
- **Heroes**: [Shape description]
- **Villains**: [Shape description]
- **Environments**: [Geometric/Organic/Mixed]
- **Silhouette priority**: [High/Medium/Low]

---

## 4. Composition

- **Framing**: [Rule of thirds/Golden ratio/etc.]
- **Symmetry**: [Symmetric/Asymmetric/Varied]
- **Depth layers**: [FG/MG/BG treatment]
- **Perspective**: [Type]
- **Hierarchy method**: [Size/Contrast/Color/Position]
- **Negative space**: [Minimal/Moderate/Abundant]

---

## 5. Lighting

- **Brightness**: [Dark/Dim/Neutral/Bright]
- **Contrast**: [Low/Medium/High]
- **Shadow style**: [Gradient/Cel-shaded/Hatched/None]
- **Light direction**: [Default direction]
- **Hardness**: [Soft/Medium/Hard]
- **Shadow color**: [Black/Colored] at [opacity]%
- **Atmosphere**: [Effects if any]

---

## 6. Texture & Detail

- **Detail level**: [Minimal/Low/Medium/High]
- **Texture style**: [Painted/Flat/Stylized/etc.]
- **Focus areas**: [High detail]
- **Background**: [Low detail]
- **Weathering**: [None/Subtle/Visible]
- **Grain**: [None/Subtle/Visible]

---

## 7. Mood & Tone

- **Core emotion**: [Emotion] at [intensity]
- **Tone**: [Light ↔ Dark position]
- **Energy**: [Calm/Moderate/Energetic]
- **Genre**: [Genre]
- **Avoid**: [Elements that break mood]

---

## 8. Technical Specs

- **Working**: [Dimensions] at [DPI]
- **Export**: [Dimensions] at [DPI]
- **Color mode**: [RGB/CMYK]
- **Formats**: [Working] → [Export formats]
- **Character size**: [Dimensions]
- **Environment size**: [Dimensions]
- **Icon size**: [Dimensions]

---

## 9. References

### Primary Influences
1. [Influence]: [What to take]
2. [Influence]: [What to take]

### Avoid
- [Style/Work]: [Why]

---

## 10. Do's and Don'ts

### Do
- [Correct practice]
- [Correct practice]

### Don't
- [Incorrect practice]
- [Incorrect practice]
```

---

## Reference Files

Load these as needed for detailed guidance:

- [color-theory.md](references/color-theory.md) - Color wheel, palette types, psychology, construction rules
- [line-and-shape.md](references/line-and-shape.md) - Line characteristics, shape psychology, silhouettes
- [composition-lighting.md](references/composition-lighting.md) - Composition principles, perspective, lighting setups
- [texture-mood.md](references/texture-mood.md) - Detail levels, texture types, mood mapping, genre guides
- [technical-specs.md](references/technical-specs.md) - Resolution, color modes, file formats
- [style-references.md](references/style-references.md) - Art movements, contemporary styles, animation styles
- [glossary.md](references/glossary.md) - Art terminology definitions

## Quick Style Presets

For rapid style definition, use these genre presets as starting points:

| Genre | Colors | Lines | Shapes | Lighting | Detail |
|-------|--------|-------|--------|----------|--------|
| **Anime** | Saturated, clean | Clean, variable weight | Soft, appealing | Cel-shaded | Medium |
| **Cartoon** | Bright, primary | Bold outlines | Round, exaggerated | Flat/minimal | Low |
| **Realistic** | Natural, full range | No outline | Complex, accurate | Gradient | High |
| **Pixel Art** | Limited palette | Sharp, 1px | Blocky, simplified | Dithered | Low |
| **Noir** | Mono + accent | Heavy contrast | Stark, geometric | High contrast | Medium |
| **Fantasy** | Rich, varied | Flowing, ornate | Organic, majestic | Dramatic | High |
| **Sci-Fi** | Cool, neon accents | Clean, geometric | Streamlined | Artificial | Medium-High |
| **Horror** | Desaturated, sickly | Jagged, broken | Distorted | Low key | Varied |
| **Minimalist** | Limited, pastel | None or thin | Simple geometric | Flat | Minimal |
