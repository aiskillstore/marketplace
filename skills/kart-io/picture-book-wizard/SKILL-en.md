---
name: picture-book-wizard
description: A specialized skill for generating high-quality, consistent children's bilingual picture books using 'banana nano'. Supports 18 visual styles across 4 categories (7 core children's book styles, 5 atmospheric styles, 5 Chinese cultural styles, 1 specialized), 12 scenes (5 nature + 7 cultural), age-driven dynamic content system (ages 3-12), and expanded learning domains (science, math, history, psychology, etc.). Use when the user wants to create picture book stories, prompts, or learning materials.
argument-hint: "[style] [scene] [age] [pages-optional] [character-optional]"
---

# Picture Book Wizard

A professional picture book creation skill that generates bilingual (Chinese/English) educational content with optimized image prompts for the 'banana nano' generator.

## Quick Start

**Usage**: `/picture-book-wizard [style] [scene] [age] [pages-optional] [character-optional] [soul-optional]`

**Complete Story System**:
- **Skeleton**: Style, Scene, Age, Pages, Character (required)
- **Soul**: Emotion, Theme, Narrative, Pacing, Color (optional, auto-selected if not specified)

**Age-Driven System** (Recommended):
- **Age**: Target reader age (3-12 years)
- **Pages**: Auto-calculated based on age (can be overridden)
- **Character**: Auto-adapted or dynamically generated based on age

### Available Styles (18 total)

**I. Core Children's Book Styles** (Highly Recommended):
- `storybook`, `watercolor`, `gouache`, `crayon`, `colored-pencil`, `clay`, `paper-cut`

**II. Atmospheric Enhancement Styles** (Use for 10-20% of pages):
- `dreamy`, `fairytale`, `collage`, `fabric`, `felt`

**III. Chinese Cultural Styles**:
- `ink`, `ink-line`, `nianhua`, `porcelain`, `shadow-puppet`

**IV. Specialized**: `tech` (use sparingly)

> **Full details**: `references/config/core/styles.md`

### Available Scenes (12 Core + Extended)

**Core 12 Scenes** (HIGH validation - >90% accuracy):
- **Nature**: `meadow`, `pond`, `rice-paddy`, `stars`, `forest`
- **Cultural & Daily Life**: `kitchen`, `courtyard`, `market`, `temple`, `festival`, `grandma-room`, `kindergarten`

**Extended Scenes**: System supports unlimited scenes through intelligent matching to core scenes.

> **Full details**: `references/config/core/scenes.md`, `references/config/advanced/scene-matching.md`

### Available Characters

**Main Protagonists**:
- `yueyue` - 5yo girl, curious and gentle (Default)
- `xiaoming` - 6yo boy, adventurous and energetic
- `lele` - 3yo boy, cheerful and innocent
- `meimei` - 4yo girl, creative and imaginative

**Supporting Characters**: `grandma`, `dad`, `mom`, `grandpa`, `sibling`
**Animal Companions**: `cat`, `dog`, `rabbit`, `chick`, `duckling`, etc.

> **Full details**: `references/config/core/characters.md`, `references/config/advanced/supporting-characters.md`

### Multi-Character Usage
- **Family**: `with:grandma`, `with:dad`, `with:mom`
- **Animals**: `with:cat`, `with:dog`, `with:rabbit`
- **Multiple**: `with:grandma,cat`

### Soul Elements (Optional)
- **Emotion**: `joyful`, `calm`, `curious`, `brave`, `warm`, `wonder`, `reflective`
- **Theme**: `growth`, `friendship`, `nature`, `family`, `courage`, `creativity`, `discovery`
- **Narrative**: `journey`, `problem`, `cycle`, `transform`, `quest`
- **Pacing**: `gentle`, `lively`, `building`, `varied`
- **Color**: `warm-bright`, `fresh`, `dreamy`, `vibrant`, `serene`

> **Full details**: `references/config/advanced/story-soul.md`

### Examples
```bash
# Age-Based Generation (Recommended)
/picture-book-wizard watercolor meadow 4
/picture-book-wizard clay forest 8 5
/picture-book-wizard nianhua kitchen 10 7 xiaoming

# With Soul Elements
/picture-book-wizard watercolor forest 8 yueyue emotion:curious
/picture-book-wizard storybook meadow 5 theme:friendship

# With Multi-Character
/picture-book-wizard watercolor kitchen 6 yueyue with:grandma theme:family

# Helper Commands
/picture-book-wizard help:style warm cozy
/picture-book-wizard help:character age:4 theme:creative
```

---

## Process Workflow

### Step 0: Content Safety Validation (MANDATORY)

**CRITICAL**: This check runs BEFORE any content generation.

1. **Input Validation**: Verify style, character, age are in allowed lists
2. **Forbidden Content**: Reject violence, horror, adult, political, commercial content
3. **Age-Theme Check**: Ensure theme appropriate for age group

> **Full rules**: `references/config/core/content-safety-validation.md`

### Step 0.5: Pre-Generation Helpers (Optional)

**Style Assistant** (`help:style [mood]`): Get style recommendations based on desired feeling
**Character Advisor** (`help:character [context]`): Get character recommendations based on story context
**Character Type Detection**: Auto-detects animal vs human character requests

> **Full details**: `references/config/core/style-assistant.md`, `references/config/core/character-advisor.md`

### Step 1: Parameter Validation

Validate style, scene, and age/pages parameters. If missing, ask user to specify.

**Age-Driven Auto-Calculation**:
- Ages 3-4: 1-3 pages, basic cognition
- Ages 5-6: 3-5 pages, basic science + social skills
- Ages 7-8: 5-7 pages, science + math + history
- Ages 9-10: 7-10 pages, advanced science + psychology
- Ages 11-12: 10-15 pages, interdisciplinary learning

> **Full specifications**: `references/config/core/age-system.md`

### Step 2: Character Consistency (CCLP 4.0)

Apply **Character Consistency Lock Protocol v4.0** for multi-page stories.

**Three Flexibility Levels**:
1. **STRICT** (Default): 100% identical appearance across all pages
2. **MODERATE**: Fixed face/hair/body, scene-adaptive clothing with narrative justification
3. **FLEXIBLE**: Signature features only, time/theme-adaptive changes

**Core Requirements**:
- **MANDATORY SIGNATURE markers** on key features
- **LOCK ESTABLISHED** statement on Page 1
- **CONSISTENCY REFERENCE** statement on subsequent pages
- **Watermark Prevention Level 2 (35 words)** at prompt end
- **Prompt compression**: 280-300 words total

> **Full protocol**: `references/config/cclp/character-consistency-lock.md`, `references/config/cclp/CCLP-FLEXIBILITY.md`

### Step 3: Content Generation

#### For Single Page
Generate four components:
1. **Story Text**: Bilingual (Chinese first, English), age-appropriate
2. **Learning Focus**: Chinese character + learning domain for age
3. **Image Prompt**: Character anchor + scene + style + rendering + watermark prevention
4. **Formatted Output**: Standard template

#### For Multi-Page Stories
1. **Cover Page**: Character showcase, title space, inviting atmosphere
2. **Story Arc**: 3-page (B-M-E), 5-page (full arc), 7-page (extended journey)
3. **Narrative Continuity**: Character consistency, story flow, learning progression
4. **Story Summary**: Characters learned, theme, extension activities

> **Story patterns**: `references/config/core/story-flow.md`
> **Output format**: `assets/templates/output-format.md`

### Step 4: Pre-Output Validation

**Reality Validation** (for discovery/science themes):
- Cross-check scene Observable Elements
- Verify biological/physical accuracy
- Scan for common error patterns

> **Validation rules**: `references/config/advanced/reality-validation.md`

### Step 5: File Output

Save to: `./output/picture-books/[YYYY-MM]/[style]-[scene]-[character]-[pages]-[timestamp].md`

---

## Image Prompt Assembly

### Solo Character Format
```
[Style] children's picture book illustration,
[Character Anchor with expression],
[Action/Pose],
[Scene Elements],
[Style Keywords],
[Rendering Parameters],
[Watermark Prevention Level 2]
```

### Multi-Character Format
```
[Primary Character Anchor - 150 words],
[Primary Action + Interaction],
[Secondary Character - 40-50 words],
[Relationship Description],
[Scene + Style + Rendering],
[Watermark Prevention Level 2]
```

**CRITICAL Multi-Character Rule**: NEVER use generic descriptions ("family members", "Dad's silhouette"). Each visible character MUST have detailed visual anchor.

> **Supporting character anchors**: `references/config/advanced/supporting-characters.md`
> **Multi-character fix guide**: `references/guides/MULTI-CHARACTER-PROMPT-FIX.md`

### Watermark Prevention (MANDATORY)

**Level 2 (35 words - Default for multi-page)**:
```
clean professional children's book illustration, publication-ready quality, pristine unmarked image, full bleed composition, no watermark, no text overlays, no signatures, no artist marks, no logos, no branding, no copyright symbols, no website URLs, clean professional image
```

**Placement**: MUST be LAST in prompt.

> **Troubleshooting**: `references/guides/WATERMARK-TROUBLESHOOTING.md`

---

## Character Anchors (Quick Reference)

**Yueyue** (5yo):
- Signature: **bright red satin ribbon pigtails**, **sunshine yellow knit sweater**, **denim overalls**
- Build: chubby preschooler, 105-110cm

**Xiaoming** (6yo):
- Signature: **short black hair with left side part**, **royal blue cotton t-shirt**, **tan khaki shorts**
- Build: average 6yo boy, 115-118cm

**Meimei** (4yo):
- Signature: **rainbow pattern hairclip ponytail**, **pastel pink daisy dress**, **white strappy sandals**
- Build: slender 4yo, 100-102cm

**Lele** (3yo):
- Signature: **short fluffy black hair**, **red-white striped t-shirt**, **royal blue elastic pants**
- Build: very chubby toddler, 90-95cm

> **Full anchors**: `references/config/core/characters.md`

---

## Quality Checklist

**Content Quality**:
- [ ] Age-appropriate language
- [ ] Accurate pinyin with tone marks
- [ ] Learning objectives match age
- [ ] Natural bilingual translations

**Technical Quality**:
- [ ] Character anchor included
- [ ] Style keywords present
- [ ] Rendering parameters complete
- [ ] **Watermark directive included** (CRITICAL)

**CCLP Quality (Multi-Page)**:
- [ ] MANDATORY SIGNATURE markers on key features
- [ ] LOCK ESTABLISHED / CONSISTENCY REFERENCE statements
- [ ] CRITICAL CONSISTENCY ENFORCEMENT command
- [ ] Character appearance IDENTICAL across pages
- [ ] Only expression and pose change (STRICT mode)
- [ ] Watermark Level 2 (35w) at end
- [ ] Total prompt 280-300 words

---

## Configuration Reference

### Core Configuration
| File | Description |
|------|-------------|
| `references/config/core/characters.md` | 4 main protagonists + selection guidelines |
| `references/config/core/styles.md` | 18 visual styles across 4 categories |
| `references/config/core/scenes.md` | 12 scenes with Observable Elements |
| `references/config/core/age-system.md` | Age-driven content specifications |
| `references/config/core/rendering.md` | Technical rendering + watermark system |

### Character Consistency
| File | Description |
|------|-------------|
| `references/config/cclp/character-consistency-lock.md` | CCLP 4.0 protocol |
| `references/config/cclp/CCLP-FLEXIBILITY.md` | Three-tier flexibility system |
| `references/config/advanced/supporting-characters.md` | Family/animal character anchors |
| `references/config/advanced/relationship-dynamics.md` | Multi-character patterns |

### Story Creation
| File | Description |
|------|-------------|
| `references/config/advanced/story-soul.md` | Emotion, Theme, Narrative, Pacing, Color |
| `references/config/core/story-flow.md` | Multi-page story patterns + cover design |
| `references/config/advanced/scene-matching.md` | Extended scene intelligent matching |
| `references/config/advanced/reality-validation.md` | Scientific accuracy validation |

### Safety & Helpers
| File | Description |
|------|-------------|
| `references/config/core/content-safety-validation.md` | Forbidden content rules |
| `references/config/core/style-assistant.md` | Style recommendation system |
| `references/config/core/character-advisor.md` | Character recommendation system |

### Animals
| File | Description |
|------|-------------|
| `references/config/animals/animal-characters.md` | Animal character system |
| `references/config/animals/animal-cclp.md` | Animal CCLP rules |

### Templates & Examples
| File | Description |
|------|-------------|
| `assets/templates/output-format.md` | Output structure + file specifications |
| `references/examples/` | Working demonstrations by style/scene |

### Guides
| File | Description |
|------|-------------|
| `references/guides/design.md` | Architecture documentation |
| `references/guides/extending.md` | Extension guide |
| `references/guides/WATERMARK-TROUBLESHOOTING.md` | Watermark fix strategies |
| `references/guides/MULTI-CHARACTER-PROMPT-FIX.md` | Multi-character fix guide |

---

## Key Principles

1. **Educational Focus**: Every page serves a clear learning objective
2. **Character Consistency**: Signature features are non-negotiable
3. **Prompt Optimization**: 150-250 words, all VCP anchors included
4. **Cultural Authenticity**: Accurate Chinese characters and context
5. **No Watermarks**: ALWAYS include watermark prevention directive

---

*For detailed specifications, consult the referenced configuration files.*
