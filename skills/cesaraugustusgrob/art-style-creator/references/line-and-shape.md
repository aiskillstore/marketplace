# Line Work and Shape Language

## Table of Contents
1. [Line Characteristics](#line-characteristics)
2. [Outline Approaches](#outline-approaches)
3. [Line Style Definition Format](#line-style-definition-format)
4. [Shape Psychology](#shape-psychology)
5. [Shape Complexity](#shape-complexity)
6. [Geometric vs Organic](#geometric-vs-organic)
7. [Shape Language Definition Format](#shape-language-definition-format)

---

## Line Characteristics

### Line Weight

| Weight | Effect | Use Cases |
|--------|--------|-----------|
| **Thin/Fine** | Delicate, detailed, fragile | Details, distant objects, subtle elements |
| **Medium** | Balanced, standard | General outlines, most elements |
| **Thick/Bold** | Strong, dominant, close | Foreground, emphasis, silhouettes |
| **Variable** | Dynamic, organic, expressive | Character art, natural forms |

### Line Quality

| Quality | Description | Emotional Effect |
|---------|-------------|------------------|
| **Clean/Smooth** | Precise, vector-like | Professional, controlled, modern |
| **Sketchy/Rough** | Visible construction | Energetic, organic, unfinished |
| **Geometric** | Ruler-straight, perfect curves | Technical, artificial, designed |
| **Organic** | Natural flow, imperfect | Living, handmade, warm |
| **Broken/Implied** | Gaps, suggestions | Artistic, open, interpretive |
| **Calligraphic** | Thick-thin variation | Elegant, traditional, flowing |

### Line Confidence
- **Confident strokes**: Single, decisive lines (professional feel)
- **Hairy/Multiple strokes**: Many overlapping lines (sketchy feel)
- **Correction visible**: Erasure marks, redrawing (raw, process-visible feel)

---

## Outline Approaches

| Approach | Description | Examples |
|----------|-------------|----------|
| **Full outline** | Complete enclosing lines | Comics, cartoons, anime |
| **Partial outline** | Selective lines, lost edges | Illustration, concept art |
| **No outline** | Form defined by color/value only | Painting, realistic styles |
| **Color holds** | Outlines match fill color | Modern animation, subtle definition |

---

## Line Style Definition Format

```
LINE STYLE: [Name]

GENERAL APPROACH:
- Outline presence: [Full / Partial / None / Color holds]
- Base weight: [Thin / Medium / Thick] at [X px/pt at Y resolution]
- Quality: [Clean / Sketchy / Geometric / Organic / Calligraphic]

WEIGHT VARIATION:
- Foreground: [Weight]
- Midground: [Weight]
- Background: [Weight]
- Details: [Weight]

LINE COLOR:
- Default: [Black / Dark value of local color / Color holds]
- Shadows: [Darker / Same]
- Highlights: [Lighter / None]

SPECIAL RULES:
- [Any specific guidelines]
```

---

## Shape Psychology

### Fundamental Shapes

```
    ┌───────────┐        ╭─────────╮         △
    │           │        │         │        ╱ ╲
    │  SQUARE   │        │ CIRCLE  │       ╱   ╲
    │           │        │         │      ╱     ╲
    └───────────┘        ╰─────────╯     ╱───────╲
                                         TRIANGLE

    Stability           Softness         Direction
    Reliability         Friendliness     Danger
    Strength            Completion       Dynamism
    Rigidity            Infinity         Aggression
    Order               Safety           Movement
```

### Character Design Shapes

| Shape Base | Character Archetype | Physical Impression |
|------------|--------------------|--------------------|
| **Square/Rectangle** | Strong, reliable, stubborn | Muscular, solid, immovable |
| **Circle/Oval** | Friendly, approachable, soft | Round, cuddly, non-threatening |
| **Triangle (up)** | Heroic, aspirational, dynamic | Athletic, directional, powerful |
| **Triangle (down)** | Unstable, villainous, sinister | Top-heavy, intimidating |
| **Mixed shapes** | Complex, nuanced characters | Varied, realistic, interesting |

---

## Shape Complexity

```
SIMPLE ◄────────────────────────────────────────► COMPLEX

○ △ □        Stylized        Detailed        Realistic
             Shapes          Shapes          Forms

Iconic       Cartoon         Illustration    Photorealistic
Minimal      Recognizable    Nuanced         Accurate
Fast read    Character       Depth           Believable
```

### When to Use Each

| Complexity | Best For | Examples |
|------------|----------|----------|
| **Simple** | Icons, logos, mobile games | Angry Birds, Among Us |
| **Stylized** | Animation, casual games | Disney, Ghibli, Overwatch |
| **Detailed** | Illustration, concept art | Game splash art, book covers |
| **Realistic** | Film, AAA games | Photorealistic rendering |

---

## Geometric vs Organic

| Aspect | Geometric | Organic |
|--------|-----------|---------|
| Lines | Straight, precise | Curved, flowing |
| Angles | Sharp, defined | Soft, variable |
| Feeling | Artificial, designed | Natural, alive |
| Use cases | Architecture, UI, tech | Nature, characters, creatures |
| Examples | Art Deco, Bauhaus | Art Nouveau, naturalism |

---

## Shape Language Definition Format

```
SHAPE LANGUAGE: [Name]

PRIMARY SHAPES:
- Dominant shape: [Circle / Square / Triangle / Mixed]
- Shape complexity: [Simple / Moderate / Complex]
- Edge treatment: [Sharp / Rounded / Mixed]

CHARACTER SHAPES:
- Heroes: [Shape description]
- Villains: [Shape description]
- Neutral/NPC: [Shape description]

ENVIRONMENT SHAPES:
- Architecture: [Geometric / Organic / Mixed]
- Nature: [Stylized / Realistic]
- Props: [Shape consistency rules]

SILHOUETTE PRIORITY:
- [High / Medium / Low]
- Readability goal: [Instant / Studied / Subtle]

DEFORMATION RULES:
- Squash and stretch: [None / Subtle / Exaggerated]
- Proportion flexibility: [Rigid / Flexible / Extreme]
```
