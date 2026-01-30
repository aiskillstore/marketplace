# Picture Book Wizard - Complete API Reference

This document provides comprehensive technical reference for all parameters, options, and advanced features of the Picture Book Wizard skill.

---

## Table of Contents

- [Command Syntax](#command-syntax)
- [Parameters Reference](#parameters-reference)
- [Visual Styles Reference](#visual-styles-reference)
- [Scenes Reference](#scenes-reference)
- [Characters Reference](#characters-reference)
- [Learning Objectives Reference](#learning-objectives-reference)
- [Output Format Reference](#output-format-reference)
- [Advanced Features](#advanced-features)
- [Error Handling](#error-handling)

---

## Command Syntax

### Basic Syntax

```
/picture-book-wizard [style] [scene] [pages] [character]
```

### Parameter Order

| Position | Parameter | Required | Default | Valid Values |
|----------|-----------|----------|---------|--------------|
| 1 | style | No* | interactive | See [Styles](#visual-styles-reference) |
| 2 | scene | No* | interactive | See [Scenes](#scenes-reference) |
| 3 | pages | No | 1 | 1, 3, 5, 7 |
| 4 | character | No | yueyue | yueyue, xiaoming, lele, meimei |

*If omitted, interactive selection will be triggered

### Examples

```bash
# Minimal - triggers interactive mode
/picture-book-wizard

# Single page with defaults
/picture-book-wizard clay pond

# Single page with specific character
/picture-book-wizard clay pond 1 xiaoming

# Multi-page story
/picture-book-wizard nianhua kitchen 3 xiaoming

# Full specification
/picture-book-wizard ink forest 5 meimei
```

---

## Parameters Reference

### Style Parameter

**Type**: String (enum)
**Required**: No (triggers interactive mode if omitted)
**Default**: None (interactive selection)

**Valid Values**:

| Code | Name | Description | Best For |
|------|------|-------------|----------|
| `clay` | Clay/Claymation | Hand-sculpted tactile textures | Nature scenes, cozy stories |
| `tech` | Tech/Futuristic | Glowing holographic elements | Space, stars, innovation |
| `ink` | Ink Wash | Traditional Chinese painting | Landscapes, cultural content |
| `paper-cut` | Paper-Cut | Chinese paper-cutting art | Festivals, celebrations |
| `nianhua` | New Year Painting | Chinese folk art style | Domestic scenes, family stories |
| `porcelain` | Blue-White Porcelain | Ceramic glaze aesthetic | Elegant, contemplative scenes |
| `shadow-puppet` | Shadow Puppet | Theatrical silhouettes | Storytelling, dramatic scenes |

**Reference**: `references/config/styles.md` for complete specifications

---

### Scene Parameter

**Type**: String (enum)
**Required**: No (triggers interactive mode if omitted)
**Default**: None (interactive selection)

**Categories**:

#### Nature Scenes

| Code | Name | Primary Elements | Learning Focus |
|------|------|------------------|----------------|
| `meadow` | Grassy Meadow | Grass, wildflowers, open field | Plants, nature discovery |
| `pond` | Pond | Water, lotus leaves, reflections | Water, aquatic life |
| `rice-paddy` | Rice Paddy | Agricultural field, seedlings | Growth, farming, food |
| `stars` | Starry Sky | Night sky, celestial elements | Dreams, cosmos, wonder |
| `forest` | Forest | Trees, woodland, foliage | Trees, ecosystems, exploration |

#### Cultural & Daily Life Scenes

| Code | Name | Primary Elements | Learning Focus |
|------|------|------------------|----------------|
| `kitchen` | Kitchen | Cooking area, family setting | Food, family bonds, cooking |
| `courtyard` | Courtyard | Traditional Chinese architecture | Culture, tradition, heritage |
| `market` | Market | Street stalls, bustling activity | Social interaction, numbers |
| `temple` | Temple | Pagoda, peaceful setting | Culture, respect, spirituality |
| `festival` | Festival | Celebration, decorations | Traditions, customs, joy |
| `grandma-room` | Grandma's Room | Traditional elder's room | Family, respect for elders |
| `kindergarten` | Kindergarten | Classroom, learning environment | Friendship, sharing, learning |

**Reference**: `references/config/scenes.md` for complete specifications

---

### Pages Parameter

**Type**: Integer
**Required**: No
**Default**: 1
**Valid Values**: 1, 3, 5, 7

**Story Structures**:

| Pages | Structure | Best For |
|-------|-----------|----------|
| 1 | Single moment | Simple concepts, quick learning |
| 3 | Beginning → Middle → End | Short stories, basic narrative arcs |
| 5 | Full story arc (Setup → Rising → Climax → Falling → Resolution) | Complete stories, character development |
| 7 | Extended journey | Complex narratives, multiple discoveries |

**Reference**: `references/config/story-flow.md` for detailed story patterns

---

### Character Parameter

**Type**: String (enum)
**Required**: No
**Default**: yueyue
**Valid Values**: yueyue, xiaoming, lele, meimei

**Character Specifications**:

| Code | Name | Age | Gender | Personality | Signature Features |
|------|------|-----|--------|-------------|-------------------|
| `yueyue` | 悦悦 | 5 | Girl | Curious, gentle, wonder-filled | Two pigtails with red ribbons, yellow sweater |
| `xiaoming` | 小明 | 6 | Boy | Adventurous, energetic, confident | Side-part hair, blue t-shirt |
| `lele` | 乐乐 | 3 | Boy | Cheerful, innocent, playful | Chubby toddler face, red striped shirt |
| `meimei` | 美美 | 4 | Girl | Creative, imaginative, artistic | Long ponytail with colorful clip, pink flower dress |

**Character Selection Matrix**:

| Story Type | Recommended Characters |
|------------|------------------------|
| Nature Exploration | Yueyue ⭐⭐⭐, Xiaoming ⭐⭐⭐ |
| Cultural Learning | Yueyue ⭐⭐⭐, Meimei ⭐⭐⭐ |
| Adventure/Action | Xiaoming ⭐⭐⭐ |
| Creative/Artistic | Meimei ⭐⭐⭐ |
| Family Bonding | Yueyue ⭐⭐⭐, Lele ⭐⭐⭐ |
| First Experiences | Lele ⭐⭐⭐, Meimei ⭐⭐ |

**Reference**: `references/config/characters.md` for complete specifications

---

## Visual Styles Reference

### Style Properties

Each style has defined:
- **Color Palette**: Dominant and accent colors
- **Texture**: Material and surface qualities
- **Lighting**: Light direction and quality
- **Technical Keywords**: Rendering parameters for Banana Nano

### Clay Style

```yaml
style: clay
properties:
  technique: "hand-sculpted claymation"
  textures: "physical clay, fingerprint marks, tactile surfaces"
  colors: "warm earth tones, natural palette"
  lighting: "soft studio lighting, warm diffused"
  rendering: "octane render, macro texture details, 8k resolution"
  atmosphere: "warm, inviting, cozy"
  best_for:
    - nature scenes (meadow, pond, forest)
    - intimate family stories (kitchen)
    - close-up interactions
```

### Tech Style

```yaml
style: tech
properties:
  technique: "futuristic technological"
  textures: "smooth surfaces, metallic, holographic"
  colors: "blue, purple, cyan, cool tones"
  lighting: "glowing elements, cool lighting, neon accents"
  rendering: "digital rendering, sharp details, bloom effects"
  atmosphere: "futuristic, innovative, wonder"
  best_for:
    - space scenes (stars)
    - modern concepts
    - innovation themes
```

### Ink Style

```yaml
style: ink
properties:
  technique: "Chinese ink wash painting (水墨画)"
  textures: "fluid brushstrokes, paper texture, wet-on-wet"
  colors: "black, grey, muted colors, minimal palette"
  lighting: "natural ambient, ethereal mist"
  rendering: "traditional art simulation, soft edges"
  atmosphere: "contemplative, artistic, serene"
  best_for:
    - landscapes (meadow, pond, forest)
    - cultural content (courtyard, temple)
    - artistic expression
```

**See `references/config/styles.md` for all 7 styles**

---

## Scenes Reference

### Scene Properties

Each scene defines:
- **Primary Elements**: Essential visual components
- **Optional Elements**: Additional details
- **Environmental Conditions**: Lighting, weather, atmosphere
- **Learning Vocabulary**: Related Chinese characters

### Pond Scene (Example)

```yaml
scene: pond
category: nature
primary_elements:
  - clear water surface
  - lotus leaves (green, floating)
  - water reflections
optional_elements:
  - lily pads
  - dragonflies
  - small fish
  - ripples
environmental_conditions:
  lighting: soft natural daylight
  time_of_day: morning or afternoon
  weather: clear, calm
  atmosphere: peaceful, contemplative
learning_vocabulary:
  primary: 水 (shuǐ) - water
  related: 莲 (lián) - lotus, 叶 (yè) - leaf, 鱼 (yú) - fish
visual_effects:
  - mirror-like reflection on water surface
  - subtle ripple distortions
  - light refraction through water
```

**See `references/config/scenes.md` for all 12 scenes**
**See `references/config/visual-effects.md` for special effects**

---

## Characters Reference

### Character Visual Specifications

Each character has strict visual consistency requirements:

#### Yueyue (悦悦) - Complete Specification

```yaml
character: yueyue
demographics:
  age: 5 years old
  gender: female
  ethnicity: Chinese

appearance:
  face:
    shape: round
    features: rosy cheeks, gentle smile
  hair:
    style: two pigtails
    accessories: red ribbons tied in bows (SIGNATURE - MANDATORY)
  clothing:
    top: yellow sweater (SIGNATURE)
    bottom: denim overalls
    footwear: small shoes

personality:
  primary: curious
  secondary: gentle, wonder-filled
  interaction_style: observant, thoughtful

character_anchor_prompt: |
  A 5-year-old Chinese girl named Yueyue, round face, rosy cheeks,
  two pigtails with red ribbons, wearing yellow sweater and denim overalls

best_suited_for:
  story_types:
    - nature exploration ⭐⭐⭐
    - cultural learning ⭐⭐⭐
    - family bonding ⭐⭐⭐
  age_appropriateness: 4-6 years
  educational_level: beginner to intermediate
```

**See `references/config/characters.md` for all 4 characters**

---

## Learning Objectives Reference

### Primary Objective: Character Learning

**Always Included**: Every page teaches one Chinese character

```yaml
learning_point:
  type: character
  character: 水
  pinyin: shuǐ
  tone: 3rd tone (falling-rising)
  english: water
  hsk_level: 1
  stroke_count: 4
  usage_context: "appears in story text and visible in image"
```

### Secondary Objectives (Optional)

#### 1. Logic (逻辑思维)

```yaml
logic_learning:
  type: logic
  category: cause_and_effect
  concept: "seed + water + sun → growth"
  chinese: "种子 + 水 + 阳光 → 生长"
  teaching_method: "sequential observation in story"
```

#### 2. Objects (物品认知)

```yaml
object_learning:
  type: objects
  item: chopsticks
  chinese: 筷子 (kuàizi)
  category: traditional_utensil
  description: "Chinese traditional eating utensil, used in pairs"
  cultural_context: "requires practice to master, part of Chinese culture"
  usage: "picking up food"
```

#### 3. Emotional (情感发展)

```yaml
emotional_learning:
  type: emotional
  emotion: joy
  chinese: 快乐 (kuàilè)
  context: "playing in snow brings pure happiness"
  development: "recognizing and expressing positive emotions"
```

**See `references/config/learning-objectives.md` for all 6 categories**

---

## Output Format Reference

### Single Page Output

```markdown
# [Title] / [Chinese Title]

**Generated**: YYYY-MM-DD HH:MM:SS
**Style**: [Style name]
**Scene**: [Scene name]
**Character**: [Character name]
**Pages**: 1

---

📖 **故事 / Story:**
[Chinese text]
[English translation]

---

🔤 **拼音 / Pinyin:**
[Pinyin with tone marks]

---

✨ **学习要点 / Learning Point:**
**汉字 (Character)**: [字] ([pinyin]) - [meaning]
[Optional: Secondary learning objectives]

---

🎨 **Banana Nano Prompt:**
[Complete image generation prompt, 150-250 words]

---

## Generation Info / 生成信息
...
```

### Multi-Page Output Structure

```markdown
# [Story Title] / [Chinese Title]

[Metadata block]

---

## Page 1 / 第一页
[Page 1 content: Story + Pinyin + Learning + Prompt]

---

## Page 2 / 第二页
[Page 2 content]

---

## Page 3 / 第三页
[Page 3 content]

---

## 📚 故事总结 / Story Summary

### 完整故事 / Complete Story
[2-3 sentences in Chinese and English]

### 学习成果 / Learning Outcomes
**汉字学习**: [All characters from all pages]
**主题**: [Theme]
**核心价值**: [Core value]

### 延伸活动建议 / Extension Activities
1. [Activity 1]
2. [Activity 2]
3. [Activity 3]

### 适合年龄 / Age Suitability
...
```

**See `assets/templates/output-format.md` for complete template**

---

## Advanced Features

### Custom Scenes

When a scene is not in the predefined list:

1. **Base Template Selection**: Choose similar existing scene
2. **Modification Specification**: Define differences
3. **Element Addition**: Add custom elements
4. **Environmental Adjustment**: Modify lighting, weather

Example:
```yaml
custom_scene:
  base: meadow
  name: "snowy field"
  modifications:
    - replace: grass → snow
    - add: falling snowflakes
    - adjust: lighting → winter diffused
```

### Style-Scene Compatibility

**Excellent Combinations (⭐⭐⭐)**:
- Clay + Nature scenes (meadow, pond, rice-paddy, forest)
- Ink + Nature + Cultural (meadow, pond, forest, courtyard, temple)
- Nianhua + Cultural/Family (kitchen, courtyard, market, festival)
- Paper-Cut + Celebrations (festival, market, courtyard)

**Good Combinations (⭐⭐)**:
- Tech + Cosmic (stars)
- All styles + Any scene (with appropriate adjustments)

**See `references/config/scenes.md` for complete compatibility matrix**

### Batch Generation

Generate multiple related stories:

```yaml
batch_request:
  series: "Four Seasons"
  base_config:
    style: clay
    scene: meadow
    character: yueyue
  variations:
    - pages: 1, theme: "spring flowers"
    - pages: 1, theme: "summer grass"
    - pages: 1, theme: "autumn leaves"
    - pages: 1, theme: "winter snow"
```

---

## Error Handling

### Common Errors

| Error | Cause | Resolution |
|-------|-------|------------|
| Invalid style | Style not in valid list | Use one of: clay, tech, ink, paper-cut, nianhua, porcelain, shadow-puppet |
| Invalid scene | Scene not in valid list | See `references/config/scenes.md` for all options |
| Invalid character | Character not in valid list | Use: yueyue, xiaoming, lele, meimei |
| Invalid pages | Pages not 1/3/5/7 | Use only: 1, 3, 5, or 7 |

### Validation

Before generation, the system validates:
- Parameter types and values
- Style-scene compatibility
- Character-story fit
- Educational appropriateness

---

## File Output

### Automatic File Creation

All generated content is automatically saved to markdown files.

**Location**: `./output/picture-books/[YYYY-MM]/`

**Naming Convention**:
```
[style]-[scene]-[character]-[timestamp].md                # Single page
[style]-[scene]-[character]-[pages]pages-[timestamp].md  # Multi-page
```

**Examples**:
```
clay-pond-yueyue-20260110.md
nianhua-kitchen-xiaoming-3pages-20260110.md
```

### File Organization

```
output/picture-books/
├── README.md
├── 2026-01/
│   ├── clay-pond-yueyue-20260110.md
│   ├── nianhua-kitchen-xiaoming-3pages-20260110.md
│   └── ...
├── 2026-02/
└── ...
```

---

## API Version

**Current Version**: 1.0
**Last Updated**: 2026-01-10
**Compatibility**: Claude Code (Skill System)

---

## Related Documentation

- **Usage Guide**: `references/guides/usage-guide.md`
- **Forms**: `references/FORMS.md`
- **Design Document**: `references/guides/design.md`
- **Extension Guide**: `references/guides/extending.md`

---

**End of Reference Document**
