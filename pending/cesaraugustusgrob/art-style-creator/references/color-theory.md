# Color Theory and Palettes

## Table of Contents
1. [Color Properties](#color-properties)
2. [The Color Wheel](#the-color-wheel)
3. [Palette Types](#palette-types)
4. [Color Psychology](#color-psychology)
5. [Palette Construction Rules](#palette-construction-rules)
6. [Palette Definition Format](#palette-definition-format)

---

## Color Properties

| Property | Definition | Range |
|----------|------------|-------|
| **Hue** | The color itself | Red, blue, green, etc. |
| **Saturation** | Color intensity/purity | Vivid ↔ Gray |
| **Value/Brightness** | Light or dark | White ↔ Black |
| **Temperature** | Perceived warmth | Warm ↔ Cool |

---

## The Color Wheel

```
                    YELLOW
                      │
           Yellow-    │    Yellow-
           Orange     │    Green
                \     │     /
                 \    │    /
      ORANGE ─────────┼───────── GREEN
                 /    │    \
                /     │     \
           Red-       │      Blue-
           Orange     │      Green
                      │
        RED ──────────┼────────── BLUE
                      │
              Red-    │    Blue-
              Violet  │    Violet
                      │
                   VIOLET
```

**Primary colors**: Red, Yellow, Blue
**Secondary colors**: Orange, Green, Violet
**Tertiary colors**: Yellow-Orange, Red-Orange, Red-Violet, Blue-Violet, Blue-Green, Yellow-Green

---

## Palette Types

### Monochromatic
- **Definition**: Single hue with value and saturation variations
- **Effect**: Unity, elegance, simplicity, specific mood
- **Use cases**: Minimalist design, noir aesthetics, focused emotion
- **Example**: All blues from navy to sky blue

### Analogous
- **Definition**: 2-4 adjacent colors on the color wheel
- **Effect**: Harmony, natural feeling, smooth transitions
- **Use cases**: Nature scenes, peaceful atmospheres, organic themes
- **Example**: Yellow, yellow-green, green

### Complementary
- **Definition**: Two colors opposite on the color wheel
- **Effect**: High contrast, vibrant energy, visual tension
- **Use cases**: Action scenes, focal points, dynamic compositions
- **Example**: Blue and orange, red and green

### Split-Complementary
- **Definition**: One color plus two colors adjacent to its complement
- **Effect**: Contrast with less tension than complementary
- **Use cases**: Balanced but dynamic scenes
- **Example**: Blue, yellow-orange, red-orange

### Triadic
- **Definition**: Three colors equally spaced on the wheel
- **Effect**: Vibrant, balanced, playful
- **Use cases**: Cartoon styles, energetic themes, children's content
- **Example**: Red, yellow, blue (primary triad)

### Tetradic (Double Complementary)
- **Definition**: Four colors forming a rectangle on the wheel
- **Effect**: Rich, complex, requires careful balance
- **Use cases**: Complex scenes, varied environments
- **Example**: Red, green, blue, orange

---

## Color Psychology

| Color | Primary Associations | Secondary Associations | Cautions |
|-------|---------------------|----------------------|----------|
| **Red** | Passion, danger, energy | Love, anger, urgency | Can feel aggressive |
| **Orange** | Warmth, enthusiasm, creativity | Playfulness, autumn | Can feel cheap |
| **Yellow** | Happiness, optimism, attention | Caution, intellect | Can cause anxiety |
| **Green** | Nature, growth, calm | Money, envy, health | Can feel stagnant |
| **Blue** | Trust, calm, professionalism | Sadness, cold, depth | Can feel distant |
| **Purple** | Royalty, mystery, spirituality | Creativity, luxury | Can feel artificial |
| **Pink** | Romance, softness, youth | Femininity, sweetness | Can feel immature |
| **Brown** | Earth, stability, reliability | Warmth, rusticity | Can feel dull |
| **Black** | Elegance, power, mystery | Death, evil, void | Can feel oppressive |
| **White** | Purity, cleanliness, space | Emptiness, sterility | Can feel cold |
| **Gray** | Neutrality, sophistication | Sadness, ambiguity | Can feel lifeless |

---

## Palette Construction Rules

### The 60-30-10 Rule

```
┌────────────────────────────────────────────────────────┐
│ 60% DOMINANT COLOR                                      │
│ - Background, large areas                               │
│ - Sets overall mood                                     │
├────────────────────────────────────────────────────────┤
│ 30% SECONDARY COLOR                                     │
│ - Supporting elements                                   │
│ - Creates contrast with dominant                        │
├──────────────────────┐                                  │
│ 10% ACCENT COLOR     │                                  │
│ - Highlights, CTAs   │                                  │
│ - Draws attention    │                                  │
└──────────────────────┴─────────────────────────────────┘
```

### Value Distribution
- Maintain clear value contrast for readability
- Background: Usually lower contrast (darker or lighter extremes)
- Foreground/Subject: Higher contrast, more saturated
- Focal points: Strongest contrast and/or saturation

### Saturation Guidelines

| Style Type | Saturation Level | Value Range |
|------------|------------------|-------------|
| Realistic | Low to medium | Full range |
| Stylized | Medium to high | Controlled range |
| Cartoon | High | Limited range |
| Noir/Moody | Very low | Extreme contrast |
| Fantasy | Medium-high | Full range |
| Minimalist | Low to medium | Limited range |

---

## Palette Definition Format

Use this format when documenting a color palette:

```
PALETTE NAME: [Name]

PRIMARY COLORS:
- Dominant:    #HEXCODE | RGB(r,g,b) | [Name/Description]
- Secondary:   #HEXCODE | RGB(r,g,b) | [Name/Description]
- Accent:      #HEXCODE | RGB(r,g,b) | [Name/Description]

EXTENDED PALETTE:
- Highlight:   #HEXCODE | [Description]
- Shadow:      #HEXCODE | [Description]
- Neutral 1:   #HEXCODE | [Description]
- Neutral 2:   #HEXCODE | [Description]

SKIN TONES (if applicable):
- Light:       #HEXCODE
- Medium:      #HEXCODE
- Dark:        #HEXCODE

FORBIDDEN COLORS:
- [Colors to avoid and why]

USAGE RULES:
- [Specific application guidelines]
```
