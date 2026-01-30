# Forms and Structured Data Guide / 表单与结构化数据指南

This document provides structured input formats and templates for the Picture Book Wizard skill.

---

## Table of Contents

- [Story Generation Request Form](#story-generation-request-form)
- [Character Configuration Template](#character-configuration-template)
- [Scene Description Format](#scene-description-format)
- [Batch Generation Configuration](#batch-generation-configuration)
- [Custom Story Template](#custom-story-template)

---

## Story Generation Request Form

### Basic Story Request

```yaml
---
# Picture Book Story Request
style: clay                    # Required: clay, tech, ink, paper-cut, nianhua, porcelain, shadow-puppet
scene: pond                    # Required: See references/config/scenes.md for all options
character: yueyue              # Optional: yueyue (default), xiaoming, lele, meimei
pages: 1                       # Optional: 1 (default), 3, 5, 7
---

# Optional: Custom Story Requirements
theme: "reflection and self-discovery"
learning_focus: "water, nature, science"
tone: "gentle and contemplative"
```

### Multi-Page Story Request

```yaml
---
# Multi-Page Story Request
style: nianhua
scene: kitchen
character: xiaoming
pages: 3
---

# Story Arc
narrative_type: "learning journey"      # learning journey, discovery, growth, challenge
theme: "family cooperation"
learning_objectives:
  - type: character                     # Always included
  - type: objects                       # Optional: traditional tools/items
  - type: logic                         # Optional: cause-effect, sequences
  - type: emotional                     # Optional: feelings, empathy

# Educational Goals
target_age: "5-6 years"
primary_skill: "using chopsticks"
cultural_element: "Chinese food culture"
```

---

## Character Configuration Template

### Character Selection Criteria

```json
{
  "character_selection": {
    "story_type": "nature_exploration",
    "target_audience": {
      "age_range": "3-6 years",
      "gender_preference": "any",
      "personality_match": "curious"
    },
    "recommended_character": "yueyue",
    "alternatives": ["xiaoming", "meimei"],
    "reasoning": "Yueyue's gentle curiosity suits nature discovery stories"
  }
}
```

### Character Override

```yaml
# Override default character for specific scene
scene: forest
character: xiaoming              # Use adventurous Xiaoming for forest exploration
rationale: "Adventure-focused story requires energetic character"
```

---

## Scene Description Format

### Standard Scene

```yaml
scene:
  name: pond
  type: nature
  primary_elements:
    - clear water surface
    - lotus leaves
    - reflection effects
  optional_elements:
    - dragonflies
    - small fish
    - water ripples
  lighting: soft natural daylight
  atmosphere: peaceful and contemplative
```

### Custom Scene (Not in Predefined List)

```yaml
custom_scene:
  name: "snowy field"
  base_template: meadow           # Use existing scene as base
  modifications:
    - replace: grass → snow
    - add: snowflakes
    - adjust: lighting → winter diffused
  environmental_conditions:
    - season: winter
    - weather: snowing
    - temperature: cold
  required_props:
    - winter clothing for character
    - snow-covered ground
    - bare trees
```

---

## Batch Generation Configuration

### Series Generation

```json
{
  "batch_generation": {
    "series_name": "Nature Discovery Series",
    "character": "yueyue",
    "style": "clay",
    "stories": [
      {
        "scene": "meadow",
        "pages": 1,
        "theme": "seed discovery"
      },
      {
        "scene": "pond",
        "pages": 1,
        "theme": "water reflection"
      },
      {
        "scene": "forest",
        "pages": 1,
        "theme": "tree observation"
      }
    ],
    "consistency_requirements": {
      "character_appearance": "strict",
      "style_rendering": "strict",
      "educational_level": "HSK 1-2"
    }
  }
}
```

### Theme-Based Generation

```yaml
theme_series:
  theme: "seasonal changes"
  stories:
    - scene: meadow
      season_variant: spring
      learning_focus: "flowers blooming"
    - scene: meadow
      season_variant: summer
      learning_focus: "grass growing"
    - scene: meadow
      season_variant: autumn
      learning_focus: "leaves changing"
    - scene: meadow
      season_variant: winter
      learning_focus: "snow covering"
```

---

## Custom Story Template

### Story Outline Form

```markdown
# Story Title: ______________________

## Story Metadata
- **Character**: ___________
- **Scene**: ___________
- **Style**: ___________
- **Pages**: ___

## Story Content (Per Page)

### Page 1
**Chinese Text** (5-12 words):
悦悦_______________________。

**English Translation**:
Yueyue _____________________.

**Learning Point**:
- Character: ___ (pinyin: ___) - meaning: ___
- Optional Objective Type: ___
- Optional Objective Content: ___

**Key Visual Elements**:
- Character pose: ___________
- Main action: ___________
- Background elements: ___________
- Special effects: ___________

### Page 2 (if multi-page)
[Repeat structure]

---

## Story Summary (Multi-Page Only)

**Complete Story** (2-3 sentences):
Chinese: ___________________
English: ___________________

**Characters Learned**:
- Page 1: ___
- Page 2: ___
- Page 3: ___

**Theme**: ___________________
**Core Value**: ___________________

**Extension Activities**:
1. ___________________
2. ___________________
3. ___________________

**Age Suitability**: ___-___ years old
**Reasoning**: ___________________
```

---

## Validation Checklist

Before submitting a story request, verify:

```yaml
validation:
  content_requirements:
    - [ ] Style is valid (clay/tech/ink/paper-cut/nianhua/porcelain/shadow-puppet)
    - [ ] Scene is valid (see references/config/scenes.md)
    - [ ] Character is valid (yueyue/xiaoming/lele/meimei)
    - [ ] Pages is valid (1/3/5/7)
    - [ ] Age-appropriate language (3-6 years)
    - [ ] Learning character is HSK 1-2 level

  technical_requirements:
    - [ ] Character signature features specified
    - [ ] Style keywords included
    - [ ] Scene elements defined
    - [ ] Rendering parameters considered

  educational_requirements:
    - [ ] Learning objective is clear
    - [ ] Character appears in story
    - [ ] Visual reinforcement planned
    - [ ] Cultural authenticity maintained
```

---

## Advanced Configuration

### Learning Objectives Matrix

```json
{
  "learning_matrix": {
    "primary": "character_learning",
    "secondary": [
      {
        "type": "logic",
        "concept": "cause_and_effect",
        "example": "seed + water + sun → growth"
      },
      {
        "type": "objects",
        "item": "chopsticks",
        "usage": "traditional Chinese utensil for picking up food"
      },
      {
        "type": "emotional",
        "emotion": "joy",
        "context": "playing in snow brings pure happiness"
      }
    ],
    "integration": "natural_within_narrative"
  }
}
```

### Output Customization

```yaml
output_preferences:
  file_naming:
    include_timestamp: true
    timestamp_format: YYYYMMDD
    location: ./output/picture-books/YYYY-MM/

  content_format:
    include_pinyin: true
    include_learning_summary: true  # for multi-page
    include_extension_activities: true  # for multi-page

  notification:
    verbose: true
    show_file_path: true
    show_summary: true
```

---

## Examples

### Example 1: Simple Single-Page Request

```yaml
style: clay
scene: pond
character: yueyue
pages: 1
```

### Example 2: Advanced Multi-Page Request

```yaml
style: nianhua
scene: kitchen
character: xiaoming
pages: 3
theme: "learning traditional skills"
learning_objectives:
  - character
  - objects: "chopsticks, dumplings"
  - logic: "sequential learning process"
  - emotional: "family encouragement"
```

### Example 3: Custom Scene Request

```yaml
style: clay
scene: custom
custom_scene:
  base: meadow
  modification: "winter snow field"
  elements:
    - snow-covered ground
    - falling snowflakes
    - winter clothing
character: lele
pages: 3
theme: "first snow experience"
```

---

## Notes

- All forms support both English and Chinese input
- Custom scenes should reference existing scenes as base templates
- Batch generation requires consistent character and style choices
- Learning objectives are optional but enhance educational value
- Output files are automatically organized by month

---

**Related Documents**:
- See `references/REFERENCE.md` for complete parameter reference
- See `references/config/scenes.md` for all available scenes
- See `references/config/characters.md` for character specifications
- See `references/guides/usage-guide.md` for detailed usage instructions

**Last Updated**: 2026-01-10
